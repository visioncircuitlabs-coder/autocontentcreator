# Task 5 — Deep-Dive Researcher (capped diamond)

## 1. Identity

| | |
|---|---|
| **Task** | 5 |
| **Plan heading** | Task 5: Researcher (capped diamond) (`docs/superpowers/plans/2026-08-19-demo.md`) |
| **Box** | Box 3 — Deep-Dive Researcher (`docs/superpowers/specs/2026-08-19-deep-dive-researcher.md`) |
| **Range** | `f2f8059..a78d457` |
| **Commits** | `22268747300ed9dbd66e7b1b82a9a3794f3be329` `feat: deep-dive researcher` (2026-08-19 23:35 IST); `a78d4579f590763f0e2c19dae632b8f6ecec9064` `fix: researcher redirect host and drop-only skeptic` (2026-08-19 23:40 IST) |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` on `feat/foolproof-design` |
| **Implementer agent id** | UNKNOWN |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | Task complete after fix round 1/5; review clean; one minor deferred (still follows off-host 302, then discards body) |

## 2. What the user would see

When a headline is marked “research this,” the machine files a short cited note: what is happening, why now, who is talking, three content ideas (not captions), risks, and every URL it actually opened. It stops after six page fetches or ninety seconds and still files, even if the note is thin. It does not write the ad. No research screen landed in this task.

## 3. The problem this task was solving

Task 4’s `deep_dive` gate has nowhere to go without this box. The factory (Task 8 brief) needs a `TrendReport`, not a raw headline. The box is the only radar step allowed to wander — and only inside a cage: seed host, six GETs, ninety seconds, a skeptic that may only drop lines.

Task 6 (Brand Book slice) is the next Layer 2 input the spec wanted; the demo researcher cages to the seed host instead and leaves Brand Brain to Task 6. Task 10’s belt calls this after scoring. Task 8’s brief packs the report.

## 4. Constraints that were already locked

Quoted:

> Planner splits 3 angles (LLM or templates). Each worker `httpx.get` the seed url + 1 linked same-host page max. Wrap body in `<source url=...>`. Skeptic function (second LLM call or heuristic) drops unsourced lines. Cap: 90 seconds, 6 GETs, then **must** file.
> — plan Task 5

> Web pages are data, never instructions (wrap HTML in a data tag; reader cannot call tools).
> — plan Global Constraints

> Hard stop: time, money, or search count. Then it **must** file, even if thin. Thin + honest beats a looping “almost done.”
> — spec `docs/superpowers/specs/2026-08-19-deep-dive-researcher.md`

> The **reader cannot call tools**. Pages are data. Dual-LLM: the model that reads HTML cannot publish, search extra, or write the final report’s claims.
> — same spec

> Forbidden: Following instructions found on a web page. … Re-running forever until it “feels complete.” Letting the same worker grade its own findings.
> — same spec

> No Brandwatch, Meltwater, Veeva, Writer, Firecrawl paid, Recraft until production plan.
> — plan Global Constraints

> Do not buy Firecrawl/Brandwatch/Recraft for the demo.
> — SDD `progress.md` budget ruling

> This box never starts the factory.
> — spec Hands off

> Angles are content ideas — not copy. Writing captions, claims, or “#1” lines inside the report is Forbidden.
> — spec

## 5. Options considered

### A. Do nothing / research later inside the belt

- **Would give:** skip a hard box; Task 8 could brief off a scored signal.
- **Cost:** no cited `TrendReport`, no skeptic trail, no spend/cap fields a lawyer can open. Spec: no report without sources.
- **Lost because:** Layer 1 is incomplete without the diamond; Task 8 packs a report, not a score.

### B. Firecrawl `/extract` (or paid crawl) for the three pages

- **Would give:** cleaner main-content extract, less raw HTML noise.
- **Cost:** paid account, extra vendor, pages still need the data-tag wrap; demo budget ruling forbids it.
- **Lost because:** global constraint + progress.md “Do not buy Firecrawl for the demo.” Production fetcher may wrap Firecrawl on **named** pages; this demo box uses `httpx`.

### C. Wrap `assafelovic/gpt-researcher` as the runtime

- **Would give:** closer to the SOTA “shape” the spec said to steal.
- **Cost:** extra dependency, default open-web search, harder to prove 6 GET / 90s / same-host / wrap tag in our tests.
- **Lost because:** spec says wrap the **shape**, build the cage in our belt. “Do not treat DeerFlow as the factory.”

### D. Parallel workers (asyncio / threads) for the three angles

- **Would give:** lower wall time on a live demo.
- **Cost:** three workers racing `ResearchBudget.gets` would need a lock; overshooting 6 is easy; tests assert `len(captured)==6` exactly.
- **Lost for demo:** sequential GETs keep the cap exact. Implementer concern #1: “Workers run sequentially… Parallel later if latency matters.”

### E. Refuse redirects entirely (`follow_redirects=False`)

- **Would give:** no off-host 302 follow at all (closes the remaining minor).
- **Cost:** miss same-host canonical URLs (`http`→`https`, trailing slash, `www`).
- **Lost for the fix round:** follow, then check `response.url` host. The 302 is still followed (request hits the evil host) but the body is not wrapped or quoted. Parked as minor.

## 6. Decision

Public surface: `run_research(signal, score, *, chat=None, client=None, persist=True, ...) -> TrendReport`. Rejects non-`deep_dive`. No `/radar/research` route.

```text
Signal + Score(gate=deep_dive)
    │
    ├─ plan_angles → 3 (ChatModel JSON or template_angles)
    ├─ for each angle (sequential):
    │     GET seed (counts) → wrap <source url=...> → read_findings
    │     GET 1 same-host link (counts) → wrap → read
    │     after each GET: final host must equal seed host
    ├─ run_skeptic: heuristic drop, then optional LLM intersect-only
    └─ MUST file TrendReport (spent.gets, capped_at=gets|time|complete)
```

| File | Role |
|---|---|
| `apps/api/boxes/researcher.py` | `ResearchBudget`, `wrap_source`, `plan_angles`, `read_findings`, `skeptic_filter`, `run_skeptic`, `_get`, `run_research` |
| `apps/api/db.py` | `upsert_reports()` |
| `apps/api/tests/test_researcher.py` | skeptic, 6-GET cap, 90s cap, wrap, persist, redirect leak, invent-and-drop |
| `apps/api/models.py` | Unchanged `TrendReport` (Task 2) |
| `apps/api/adapters/chat_litellm.py` | Still a stub; planner/reader/skeptic fall back without a key |

Caps in code: `MAX_GETS = 6`, `MAX_SECONDS = 90.0`, `MAX_ANGLES = 3`, `MAX_LINKED_PER_WORKER = 1` (`researcher.py:20-23`).

## 7. Why this exact shape

### Diamond + stop rule

Planner → three workers → separate skeptic → merge (`run_research` docstring at `researcher.py:385`). That is EXM7777’s diamond + gpt-researcher planner/cite, with DeerFlow-style `max_total_per_run`.

Stop is `ResearchBudget` (`researcher.py:72-108`): `allow_get` is false when `gets >= 6` or elapsed ≥ 90s. `record_get` increments **before** the HTTP call (`researcher.py:303-305`), so failed/404/off-host responses still consume budget. `finish_reason` writes `capped_at` as `"gets"`, `"time"`, or `"complete"`.

`test_cap_stops_after_6_gets` asserts exactly 6 captured URLs, `capped_at=="gets"`, `spent["gets"]==6`, off-host link never requested from HTML. `test_time_cap_still_files_report` advances the injected clock to 100s after the first GET → `capped_at=="time"`, one GET, still a `TrendReport` with a `what`. `test_must_file_when_pages_fail` (all 404) still returns a report. Thin + honest.

Seed is fetched **once per worker** (up to 3 identical GETs). Wasteful; implementer concern #3. It matches “each worker GET the seed url + 1 linked same-host page” and fills the 6-GET cap as 3×(seed+1).

### 90s / 6 GET cap

Plan numbers, not guesses. `spent` always includes `gets`, `searches` (same count), `tokens=0`, `rupees=0` (`researcher.py:462-467`). Lawyer view in the spec: seed, urls + hashes, what the skeptic dropped, spend, cap that stopped it.

### Wrap `<source url=>`

`wrap_source` (`researcher.py:123-125`) puts the body in a data tag. `read_findings` (`researcher.py:192-215`) is text-in / findings-out: it cannot fetch. Reader system prompt (`READER_SYSTEM`, `researcher.py:33-38`) says the tag is untrusted DATA, ignore jailbreaks, no tools, no ads.

`test_wraps_body_as_source_data_not_instructions`: jailbreak HTML is **in the user payload inside the tag**, **not** in `system`. Raw `<html>` does not enter the system prompt. That is the dual-LLM injection lock (OWASP LLM01 / spine spec) without buying a sandbox.

### Skeptic drop-only intersect

Heuristic `skeptic_filter` (`researcher.py:222-248`) drops missing `http(s)` URLs and URLs we never successfully fetched. `test_skeptic_drops_claim_with_no_url` covers the brief’s required case.

Optional LLM skeptic (`run_skeptic`, `researcher.py:251-289`) is a **second** job, not the worker grading itself. First implementer trusted `SkepticOut.survivors` as-is. Reviewer Important: the model could invent a new sentence (even with a fetched URL) and it would become `what`.

Fix: survivors = **intersect** of model output with original findings keyed on `(text, url)` (`researcher.py:269-278`). New sentences are listed as `dropped (not in original)` and never kept. Then heuristic filter runs again. `test_llm_skeptic_cannot_invent_new_claims` feeds unsourced invention **and** a `#1 guaranteed` line stamped with the seed URL; both discarded; every kept pair is in the original list.

If chat throws, heuristic result stands (`researcher.py:287-289`). LLM may only drop, never add.

### Redirect host check after follow

`build_client` still uses `follow_redirects=True` (`researcher.py:111-116`) so same-host canonical redirects work. First implementer only filtered `href` hosts via `same_host_links` (`researcher.py:135-153`). A same-host `href` that 302s to `evil.example` would still be read.

Fix `_get` (`researcher.py:296-320`): after the GET, `url_host(response.url)` must equal the seed host. Mismatch → log, return `None`, do **not** wrap, do **not** feed the reader. The GET still counted. `test_same_host_redirect_off_host_is_not_fed`: trap on `news.example` 302s to `evil.example`; secret payload is absent from `model_dump_json()`, from `sources[].url`, and from quotes.

Remaining hole (minor): httpx still **follows** the 302, so the request hits the off-host. Body is discarded after the fact. Option E (no follow) was not taken.

### Why workers are sequential

`for angle in angles:` (`researcher.py:423-453`) is a Python for-loop sharing one `ResearchBudget`. No `asyncio.gather`. Reasons in evidence:

1. Exact 6-GET test (`len(client.captured)==6`). Parallel GETs in flight can overshoot before `allow_get` sees the increment.
2. `claimed_links` set assigns each follow-up URL to one worker without a lock.
3. Demo latency is dominated by the cap, not by waiting on three sequential httpx calls in tests.

Parallel is explicitly “later if latency matters” (Task 5 report concerns). Spec’s diagram draws workers as a fan-out; demo implements the **cage** first.

### Why Firecrawl was refused

Plan Global Constraints name “Firecrawl paid.” Progress.md budget: free adapters default; do not buy Firecrawl for the demo. SOTA scorecard puts Firecrawl `/extract` on the **fetcher** named-pages pipe, not as the researcher runtime. This box’s job is the cage + skeptic + must-file, which we can prove with mocked `httpx`. Paying Firecrawl would not have improved the **show** (no Command Center page yet) and would have skipped the wrap-tag test.

## 8. What we refused

- Firecrawl, gpt-researcher as a library, OpenAI/Gemini Deep Research with Gmail/Drive, DeerFlow as the factory.
- Uncapped fact-check loops; “keep going until it feels complete.”
- Reader that can call tools or fetch extra URLs.
- Writing captions / `#1` / medical claims in the report (`PLANNER_SYSTEM` forbids them; template angles are “What is happening / Why now / Risks”).
- Brand Book slice inside this task (Task 6 owns it; cage is seed host only).
- `POST /radar/research`.
- Starting the factory from this box.
- Spending the ~$5 budget.

## 9. Verification that actually ran

**Seen in the implementer report** (this documentation pass did not re-run pytest):

Implement (`2226874`):

```text
.\.venv\Scripts\python.exe -m pytest tests/test_researcher.py -q
8 passed in 0.43s

.\.venv\Scripts\python.exe -m pytest tests/ -q
46 passed in 0.72s
```

Fix (`a78d457`):

```text
.\.venv\Scripts\python.exe -m pytest tests/test_researcher.py -q
10 passed in 0.39s

.\.venv\Scripts\python.exe -m pytest tests/ -q
48 passed in 0.73s
```

| Test | Asserts |
|---|---|
| `test_skeptic_drops_claim_with_no_url` | unsourced lines gone; note contains `"no url"` |
| `test_cap_stops_after_6_gets` | exactly 6 GETs; `capped_at=gets`; off-host skipped |
| `test_time_cap_still_files_report` | clock past 90s → 1 GET, still a report |
| `test_rejects_non_deep_dive` | `background` → `ValueError` |
| `test_must_file_when_pages_fail` | 404s still produce `TrendReport` |
| `test_planner_splits_three_angles_without_llm` | 3 non-copy angles |
| `test_wraps_body_as_source_data_not_instructions` | wrapper in user; jailbreak not in system |
| `test_run_research_persists_to_reports` | SQLite `reports` row matches |
| `test_same_host_redirect_off_host_is_not_fed` | leak payload absent (fix) |
| `test_llm_skeptic_cannot_invent_new_claims` | invented survivors discarded (fix) |

**Claimed, not seen here:** live network deep-dive; compose walk; real LiteLLM planner/reader/skeptic (adapter still stub).

## 10. Review findings and rulings

Review packages: `review-f2f8059..2226874.diff`, `review-2226874..a78d457.diff`.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| **Important** | Same-host cage leaked via 302 to another host | After every GET, `response.url` host must match seed host; discard body; GET still counts | **Fixed** `a78d457` + `test_same_host_redirect_off_host_is_not_fed` |
| **Important** | Optional LLM skeptic could invent new claims (even with a fetched URL) | Survivors = intersect with original `(text, url)` | **Fixed** `a78d457` + `test_llm_skeptic_cannot_invent_new_claims` |
| Critical | none in ledger | — | — |
| Minor | still follows off-host 302 then discards body | deferred | httpx `follow_redirects=True`; request may hit evil host; body not quoted |

Progress.md: “Task 5: complete (commits f2f8059..a78d457, review clean).” Exact reviewer prose is UNKNOWN beyond the implementer’s two-Important paraphrase.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Sequential workers (diamond drawn parallel) | later perf pass if live demo latency hurts; not Task 6 |
| Seed fetched once per worker (3 identical GETs) | same; or a shared seed cache inside `run_research` |
| No Brand Brain slice / trusted-site list beyond seed host | Task 6 fixtures exist; production researcher trusted-site lock |
| `chat_litellm.py` still a stub; planner/reader/skeptic use templates/heuristics | production LiteLLM |
| No `POST /radar/research` | Task 11 / Task 10 belt |
| Off-host 302 is followed, then body dropped | production: block redirects or pin `follow_redirects=False` for off-host |
| `remember(url, None)` still lists failed/off-host **request** URLs in `sources` with empty hash (not the leak URL) | acceptable for “we tried this”; confirm on lawyer walk |
| Heuristic reader is `clip_text(body, 400)` — can put raw HTML-ish text into `what` | cheap LLM reader when a key exists; skeptic still requires a fetched URL |

## 12. Third-party check list

1. `apps/api/boxes/researcher.py:20-23` — `MAX_GETS=6`, `MAX_SECONDS=90`, `MAX_ANGLES=3`, `MAX_LINKED_PER_WORKER=1`.
2. `researcher.py:123-125` — `wrap_source` format `<source url=…>`.
3. `researcher.py:269-278` — intersect on `(text, url)`; invented keys go to `dropped (not in original)`.
4. `researcher.py:311-316` — final host check after GET.
5. `researcher.py:385-387` — non-`deep_dive` raises.
6. `researcher.py:423` — `for angle in angles:` (no gather/thread pool).
7. `apps/api/tests/test_researcher.py` — the ten tests in §9; `pytest tests/test_researcher.py` from `apps/api`.
8. Grep `apps/api` for `firecrawl` / `Firecrawl`: should not appear in box code.
9. `apps/api/main.py` — no research route.
10. Git: `git show 2226874 --stat`, `git show a78d457 --stat`.
