# Task 4 — Relevance Scorer

## 1. Identity

| | |
|---|---|
| **Task** | 4 |
| **Plan heading** | Task 4: Scorer (`docs/superpowers/plans/2026-08-19-demo.md`) |
| **Box** | Box 2 — Relevance Scorer (`docs/superpowers/specs/2026-08-19-relevance-scorer.md`) |
| **Range** | `7da5c99..f2f8059` |
| **Commits** | `bb09b427aaac76badc35e9be969a7d233ef94c8b` `feat: relevance scorer` (2026-08-19 23:23 IST); `f2f8059d2d1f56c238ea6e63e68cb2579724f78f` `fix: reddit comment volume in scorer velocity` (2026-08-19 23:27 IST) |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` on `feat/foolproof-design` |
| **Implementer agent id** | UNKNOWN (not in `.superpowers/sdd/2026-08-19-demo/progress.md` for this task) |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | Task complete after fix round 1/5; review clean; minors deferred |

## 2. What the user would see

After Fetch, every headline gets two numbers (how on-brand, how loud) and a bucket: throw it away, keep it on a quiet shelf, or send it to research. A recall, lawsuit, or job-ad story is thrown away even if it looks on-brand. No extra screen landed in this task — scoring is a function the later Command Center / belt will call.

## 3. The problem this task was solving

Task 3 only collects signals. Without a bouncer, every GDELT/RSS/Reddit row would wake the Deep-Dive Researcher (Task 5), blow the 6-GET / 90s cap, and put crisis copy next to skincare talk.

This box answers two cheap questions and stamps a gate. Task 5 consumes only `gate=deep_dive`. Task 10's belt (`run_radar`) walks fetch → score → research. Velocity is logged; it is **not** a claims go-ahead.

## 4. Constraints that were already locked

Quoted, not softened:

> Exclusion brief (code): drop job ads, “neutrogena” as username spam, crisis words → `kill`.
> Brand-fit: cheap `complete_json` into `{brand_fit, reason}` or keyword fallback if no API key.
> Velocity: recency + source rank (reddit comments / GDELT seendate), scaled 1–10.
> Gates: `<5` or kill → discard; `5–7` → background; `≥8` and not kill → deep_dive.
> — plan Task 4, `docs/superpowers/plans/2026-08-19-demo.md`

> | **discard** | brand_fit &lt; 5, **or** safety = kill |
> | **background** | 5–7, stored on the trend shelf, no researcher |
> | **deep_dive** | brand_fit ≥ 8 **and** safety ≠ kill. |
> Velocity is **not** a green light to make a health claim.
> — spec `docs/superpowers/specs/2026-08-19-relevance-scorer.md`

> If the model returns garbage, the row is `watch` and a human sees it on the shelf — we do not invent an 8.
> — same spec

> Letting velocity or “it’s trending” override a safety kill.
> — spec Forbidden

> If no LLM key, Scorer/Judge/Hard Rules still run on code
> — plan “Same structure, cheaper guts”

> **Do not** One embedding “is this relevant?”
> — spec Buy/wrap/build

> raw_ref (vendor mention id — not a scrape blob)
> — fetcher spec; `Signal` fields locked in the plan Interfaces block (`apps/api/models.py`)

> No Brandwatch, Meltwater, Veeva, Writer, Firecrawl paid, Recraft until production plan.
> — plan Global Constraints

> Work on `feat/foolproof-design` worktree. D: for caches. Tests with each box.
> — plan Global Constraints

## 5. Options considered

### A. Do nothing / score later (Task 10 belt)

- **Would give:** skip a box; researcher could take raw fetch output.
- **Cost:** Task 5's 6-GET budget spent on cricket scores and recalls; no replayable `prompt_version`; belt has nothing to gate on.
- **Lost because:** Layer 1 Radar is specced as Fetcher → Scorer → Researcher. Plan Task 4 is explicit.

### B. Always call LiteLLM / Gemini for brand-fit (no keyword path)

- **Would give:** closer to production “cheap model via LiteLLM → Cerebras.”
- **Cost:** demo dies without `GEMINI_API_KEY`; CI needs a paid/free-tier key; contradicts “if no LLM key, Scorer still runs on code.”
- **Lost because:** fallback is the locked demo path. `ChatModel` is optional on `run_score`.

### C. One embedding “is this relevant?”

- **Would give:** one number, maybe better homonyms than three keyword hits.
- **Cost:** vector store, a model, no exportable exclusion brief, no 1–10 rubric, no lawyer-readable reason line.
- **Lost because:** spec **Do not**.

### D. Add `num_comments: int` (or `velocity_meta`) on `Signal`

- **Would give:** typed comment volume; no JSON parse in the scorer.
- **Cost:** changes the Task 2 locked `Signal` shape (plan Interfaces + `models.py:7-18`); SQLite `signals` schema; every adapter.
- **Lost because:** the Important review item was “use reddit comment volume,” not “widen the domain type.” Volume went into existing `raw_ref` instead.

### E. Word-boundary / tokenized exclusion instead of substring

- **Would give:** fewer over-kills (`boycott` inside unrelated titles).
- **Cost:** miss `boycott!`, glued tokens, URL path fragments; crisis false-negatives.
- **Lost for demo:** exclusion file says substring on purpose; over-kill parked as a minor (see §10–11).

## 6. Decision

Public surface: `run_score(signals, *, chat=None, exclusion_path=None, persist=True, now=None) -> list[Score]`. No `POST /radar/score`.

| File | Role |
|---|---|
| `apps/api/boxes/scorer.py` | `load_exclusion_rules`, `match_exclusion`, `keyword_brand_fit`, `score_velocity`, `_reddit_comment_bump`, `_brand_fit_via_chat`, `decide_gate`, `score_one`, `run_score` |
| `apps/api/fixtures/neutrogena/exclusion.txt` | Owned kill/job/spam patterns (`category\|pattern`) |
| `apps/api/ports.py` | `ChatModel.complete_json(system, user, schema) -> BaseModel` |
| `apps/api/adapters/chat_litellm.py` | Stub `LiteLLMChat` (not used by tests) |
| `apps/api/db.py` | `upsert_scores()` into table `scores` |
| `apps/api/adapters/reddit_json.py` | `raw_ref` compact JSON (`id`, `num_comments`, `score`) — fix commit |
| `apps/api/tests/test_scorer.py` | Kill, fallback, gates, chat, persist, comment bump |
| `apps/api/models.py` | Unchanged `Score` / `Signal` (Task 2) |

Gate function (velocity is not an argument):

```66:71:apps/api/boxes/scorer.py
def decide_gate(*, brand_fit: int, safety: Safety) -> Gate:
    if safety == "kill" or brand_fit < 5:
        return "discard"
    if brand_fit >= 8:
        return "deep_dive"
    return "background"
```

## 7. Why this exact shape

### Exclusion-first kill

`score_one` matches the exclusion file **before** chat or keywords (`scorer.py:205-220`). A hit returns immediately: `safety="kill"`, `gate="discard"`, `brand_fit=1`, `model="exclusion"`, `reason="exclusion:{category}:{pattern}"`. Chat is never asked. That is the spec order (exclusion brief, then brand-fit) plus the Forbidden line that velocity/trending cannot override a kill.

`test_kill_overrides_high_brand_fit_from_chat` (`test_scorer.py:231-244`) proves a FakeChat `brand_fit=10` still discards on “Class action lawsuit after product recall.”

Job ads and username spam also become `kill`, not a fourth safety enum. `Score.safety` is locked as `ok | watch | kill`. Category survives only in `reason`. That is why the ledger’s minor “all exclusions labeled kill” is a naming clash, not a missed gate: the plan already said those three classes → `kill`.

### Keyword fallback without LLM

`run_score(..., chat=None)` is the default demo path (`scorer.py:223-225`, `model="keyword-fallback"`). `POSITIVE_KEYWORDS` (`scorer.py:31-48`) is a owned list, not an embedding.

| Hits | Fit | Typical gate |
|---|---|---|
| ≥3, or `neutrogena` plus ≥2 | `min(10, 7+hits)` → ≥8 | `deep_dive` if not killed |
| 2 (no brand-name shortcut) | 6 | `background` |
| 1 | 5 | `background` |
| 0 | 2 | `discard` |

`test_fallback_scoring_without_llm` (`test_scorer.py:76-98`): Hydro Boost + hyaluronic + serum + moisturizer + ceramides + dry skin → ≥8 `deep_dive`; cricket → `<5` `discard`. No `GEMINI_API_KEY`. Coarse on homonyms beyond `exclusion.txt` — implementer concern, not a spec miss.

### Gate thresholds `<5` / `5–7` / `≥8`

Parametrized `test_gate_thresholds` (`test_scorer.py:101-119`): `(4,ok)→discard`, `(5,ok)→background`, `(7,ok)→background`, `(8,ok)→deep_dive`, `(10,ok)→deep_dive`, `(9,kill)→discard`, `(6,kill)→discard`, `(8,watch)→deep_dive`.

`watch` does **not** kill. Garbage chat is forced `watch` **and** `brand_fit` capped at 7 (`scorer.py:187-195`) so we cannot invent an 8. `test_chat_garbage_falls_back_to_watch_not_fake_eight` asserts `brand_fit < 8` and gate in `{discard, background}`.

Velocity is computed always and stored, but `decide_gate` ignores it. A fast GLP-1 spike can be loud and still `kill` from the exclusion file.

### Why reddit `num_comments` went into `raw_ref` JSON instead of a new `Signal` field

Plan Task 4 says velocity uses “reddit comments / GDELT seendate.” First implementer (`bb09b42`) only used recency + `SOURCE_RANK` (`reddit=3`, `gdelt=2`, `news_rss/rss=1`). Reviewer Important: that is rank, not comment volume.

Fix (`f2f8059`) did **not** add `Signal.num_comments`. Reasons in evidence:

1. `Signal` is a locked plan interface (`demo.md` Interfaces; `models.py:7-18`). A new field is a Task 2 schema change (`signals.raw_ref` already exists as `TEXT`).
2. Fetcher spec: `raw_ref` is a vendor mention id, **not a scrape blob**. Compact JSON `{"id":"t3_…","num_comments":N,"score":N}` is still metadata, not HTML (`reddit_json.py:72-83`).
3. Scorer parses only when `source=="reddit"` and `raw_ref` starts with `{` (`scorer.py:122-125`, `171-172`). Invalid JSON → bump 0. GDELT still uses `happened_at` (seendate) + rank, unchanged.
4. Bump: 5 comments → +1, 25 → +2, 100 → +3, then clamp 1–10 (`scorer.py:136-142`). `test_reddit_comment_volume_bumps_velocity`: identical timestamps, 150 comments > 0 comments.

Pre-fix `raw_ref` was `t3_{id}`. Tests now assert `'"id":"t3_abc123"'` and `'"num_comments":42'` (`test_fetcher.py:167-168`).

### Why `chat_litellm` is still a stub

`ports.ChatModel` landed so later boxes can inject a real client. `LiteLLMChat.complete_json` (`chat_litellm.py:16-23`):

- no `GEMINI_API_KEY` / `LITELLM_API_KEY` → `RuntimeError` telling the caller to use `chat=None`
- key present → `NotImplementedError` (“LiteLLM wiring is deferred”)

Scorer tests use `chat=None`, `FakeChat`, or `BadChat`. They never import the adapter. Production swap is “LiteLLM → Cerebras for brand-fit” (`docs/superpowers/plans/2026-08-19-production.md` adapter table). Demo plan still requires Scorer to run without a key. Wiring the SDK here would have spent the optional ~$5 and failed CI in rooms with empty `.env`.

`PROMPT_VERSION = "v1"` (`scorer.py:16`) is stored on every `Score` so a later rubric bump stays replayable (spec Forbidden: don’t change the rubric without a version bump).

### Substring over-kill tradeoff

`match_exclusion` lowercases `title + snippet + url` and tests `pattern in haystack` (`scorer.py:94-101`). `exclusion.txt:2` documents that. `boycott` as a lone kill token will discard any title that contains those letters as a substring — including legitimate news (“plastic-packaging boycott”) and, more awkwardly, accidental hits.

Chosen because: (1) crisis false-negative is worse than an extra discard in a demo; (2) the file is owned text we can export (Sprinklr-shaped inclusion/exclusion brief); (3) word-boundary matching was option E and lost. Parked as a known hole, not a silent bug.

## 8. What we refused

- NewsWhip Spike (spec “buy later”; velocity is recency + rank + reddit comments).
- Direct Cerebras SDK (spec: wrap through LiteLLM; demo does not call Cerebras at all — Company Brain ≠ inference).
- One embedding relevance score.
- Exploding Topics % as a claims green light.
- Scorer writing angles or copy (researcher/factory).
- `POST /radar/score` and Command Center pages (later tasks).
- Brandwatch / Meltwater / Firecrawl.
- Widening `Signal` for comment counts.
- Spending the ~$5 optional budget (progress.md budget ruling; not spent as of Task 8).

## 9. Verification that actually ran

**Seen in the implementer report** (quoted; this documentation pass did not re-run pytest):

Implement (`bb09b42`), from `apps/api`:

```text
.\.venv\Scripts\python.exe -m pytest tests/test_scorer.py -q
.................                                                        [100%]
17 passed in 0.48s

.\.venv\Scripts\python.exe -m pytest tests/ -q
.....................................                                    [100%]
37 passed in 0.62s
```

Fix (`f2f8059`):

```text
.\.venv\Scripts\python.exe -m pytest tests/test_scorer.py tests/test_fetcher.py -q
31 passed in 0.64s

.\.venv\Scripts\python.exe -m pytest tests/ -q
38 passed in 0.73s
```

| Test | What it actually asserts |
|---|---|
| `test_kill_word_forces_discard` | recall/adverse → `kill` + `discard` |
| `test_job_ad_exclusion_is_kill` | hiring copy → `kill` |
| `test_username_spam_exclusion_is_kill` | `u/neutrogena` / `@neutrogena` → `kill` |
| `test_fallback_scoring_without_llm` | strong skincare ≥8 `deep_dive`; cricket `<5` `discard`; `model=keyword-fallback` |
| `test_gate_thresholds[...]` | 4 / 5–7 / 8+ / kill / watch matrix |
| `test_chat_model_brand_fit_when_provided` | FakeChat 9 → `deep_dive` |
| `test_chat_garbage_falls_back_to_watch_not_fake_eight` | exception → `watch`, fit `<8` |
| `test_velocity_recency_and_source_rank` | fresh reddit > old rss |
| `test_reddit_comment_volume_bumps_velocity` | 150 comments > 0 comments (added in fix) |
| `test_run_score_persists_to_scores` | SQLite `scores` row matches |
| `test_kill_overrides_high_brand_fit_from_chat` | chat 10 + lawsuit → `discard` |

**Claimed, not seen here:** live `docker compose` scoring a real fetch. Task 4 report does not claim a compose walk. No live LiteLLM call (adapter is a stub).

## 10. Review findings and rulings

Review package: `review-7da5c99..bb09b42.diff` then fix package `review-bb09b42..f2f8059.diff`.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| **Important** | Velocity used fixed source rank only; plan asked for reddit comment volume / GDELT seendate | Use `num_comments` without a new `Signal` field | **Fixed** in `f2f8059`: JSON in `raw_ref` + `_reddit_comment_bump`; GDELT path unchanged |
| Critical | none in ledger | — | — |
| Minor | all exclusions labeled `kill` | deferred | job/spam still `safety=kill`; category in `reason` only |
| Minor | `chat_litellm.py` stub | deferred | still `NotImplementedError` with a key |
| Minor | substring over-kill | deferred | see §11 |

Progress.md: “Task 4: complete (commits 7da5c99..f2f8059, review clean).” Exact reviewer prose beyond the implementer’s paraphrase of the Important item is UNKNOWN (no reviewer report file in the SDD folder).

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Keyword brand-fit is coarse (three positive hits → `deep_dive`; weak homonyms) | production scorer (LiteLLM rubric); not Task 5 |
| `LiteLLMChat` is a stub | production adapter swap; optional when a key exists for copy (Task 8 uses `ChatModel` but not this file’s body) |
| No `POST /radar/score` | Task 11 Command Center / Task 10 belt |
| Substring exclusion over-discards (`boycott` anywhere) | production plan (tighter matchers) or a later exclusion-file edit |
| Job/spam collapsed to `kill` rather than a distinct safety | keep unless `Score.safety` is deliberately widened (would be a types change) |
| `Signal.raw_ref` now JSON for reddit, still a plain string for other sources | acceptable; scorer only JSON-parses reddit |

## 12. Third-party check list

Open these in under 15 minutes:

1. `apps/api/boxes/scorer.py:66-71` — `decide_gate` has no `velocity` argument; kill or `<5` discards.
2. `apps/api/boxes/scorer.py:205-220` — exclusion return happens before `chat`.
3. `apps/api/fixtures/neutrogena/exclusion.txt` — `kill|`, `job|`, `spam|`; header says substring.
4. `apps/api/tests/test_scorer.py` — run `pytest tests/test_scorer.py` from `apps/api` with `chat=None` paths; expect the kill / fallback / gate tests above.
5. `apps/api/adapters/reddit_json.py:72-83` — `raw_ref` is `json.dumps` of `id`/`num_comments`/`score`, not a new model field.
6. `apps/api/models.py:7-18` — `Signal` still has no `num_comments`.
7. `apps/api/adapters/chat_litellm.py:16-23` — still raises; tests do not import it.
8. `apps/api/main.py` — no `/radar/score` route (grep empty).
9. Git: `git show bb09b42 --stat` and `git show f2f8059 --stat` match the files in §6.
10. Confirm `Score.prompt_version` is written (`test_run_score_persists_to_scores` selects it).
