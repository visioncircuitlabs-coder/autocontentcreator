# Task 10 — Review, Feedback, Export, Belt

**Status:** filled (review closed). Feat `24e103a` is on the branch. No fix commit. Ledger: review clean with deferred minors; first-concept-only accepted; `$5` still unspent.

## Locked before anyone writes code

Evidence preserved from the pre-implementation stub (same contract the implementer built against):

- `decide(draft_id, user, verdict, reason) -> Decision` — **reason required**.
- `run_radar() -> list[TrendReport]`
- `run_factory(report_id) -> list[Draft]` through the loop
- `export_pack(draft_id) -> zip path`
- Belt order: fetch → score → research deep_dives → store reports. Factory: brief → strategist → copywriter → hard_rules → judge → loop → art_director → queue.
- Persist `flag_human` (parked from Task 7).
- No autonomous publish. Export is preview + PNG/ZIP. Paused only.

## Implementer note (accepted shape)

- `decide` refuses blank/whitespace reason. Approve and reject both write Track Record the same day (`boxes/feedback.py` distill = collapsed whitespace, no Brand Brain).
- `flag_human` is a `drafts.flag_human` column **and** `judge.flag_human` JSON so a reload still shows the flag.
- Belt: `run_radar` = fetch → score → research deep_dives → store reports. `run_factory` = brief → strategist → copywriter → loop (rules+judge inside) → art_director → queue. **First concept only**, 2–3 variants (accepted).
- Export is `*_paused.zip` (preview.html + PNG + caption + meta `published: false`). No publish/boost/send route.
- HTTP for Task 11: `POST /radar/run`, `POST /factory/run`, `POST /review/{draft_id}`, `GET /export/{draft_id}`, list `GET /signals|/scores|/reports|/drafts|/queue`.

## 1. Identity

| | |
|---|---|
| **Task** | 10 |
| **Plan heading** | Review, Feedback, Export, Belt (`docs/superpowers/plans/2026-08-19-demo.md`, “Task 10”) |
| **Boxes** | 7 Track Record (ledger write), 15 Review & Approve, 16 Preview & Export, 17 Feedback Writer, plus the plain-code belt that wires Radar + Factory |
| **Branch / worktree** | `feat/foolproof-design` at `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Base** | `865446a` `feat: art director with image port` |
| **Feat** | `24e103a` `feat: review export belt` (2026-08-20; date from `task-10-report.md`) |
| **Fix** | none — no fix round |
| **Head (task closed)** | `24e103a` |
| **Author on git** | UNKNOWN (this documentation agent has no shell; review package lists the SHA/message only) |
| **Implementer agent id** | UNKNOWN (not named in `progress.md` for this task) |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/task-10-brief.md`, `task-10-report.md`, `progress.md` |
| **Review package** | `review-865446a..24e103a.diff` (10 files) |
| **Re-review** | Not needed — ledger says review clean; no Important/Critical; no fix commit |

## 2. What the user would see

Still no Command Center screens (Task 11). Behind the API, the machine can now run the full Radar and Factory belts end to end: pull free signals, keep only deep-dives as reports, build a Neutrogena-style draft with a stub card, park it on a review queue, force a named human to type a reason on approve *or* reject, write that reason into a same-day learning ledger, and download a ZIP stamped **PAUSED — NOT PUBLISHED**. Nothing posts to Instagram or any ESP.

## 3. The problem this task was solving

Tasks 3–9 built every box on the belt, but nothing called them in order, nothing persisted the human-flag from a failed loop, nothing required a reason to leave the queue, and nothing produced a preview pack. Task 8’s Track Record helper returned empty wins/losses on purpose. Task 7 parked `flag_human` as in-memory only. Without this task, Task 11 has no `/radar/run`, `/factory/run`, `/review/…`, `/export/…`, or `/queue` to click.

Depends on it:

- **Task 11** — Command Center story pages wire these HTTP routes and the queue/preview UX.
- **Task 12** — demo walk / CI must be able to exercise belt → approve → ZIP.
- **Brief / Track Record loop** — `load_track_record_examples` now reads real ledger rows so later briefs can pack 3 wins / 3 losses.
- Closes Task 7 park: persist `flag_human`.

## 4. Constraints that were already locked

Demo plan Task 10 (`docs/superpowers/plans/2026-08-19-demo.md:360-376`):

> Interfaces:
> - `decide(draft_id, user, verdict, reason) -> Decision`  # reason required
> - `run_radar() -> list[TrendReport]`
> - `run_factory(report_id) -> list[Draft]`  # through loop
> - `export_pack(draft_id) -> zip path`
>
> Belt order: fetch → score → research deep_dives → store reports. Factory: brief → strategist → copywriter → hard_rules → judge → loop → art_director → queue.
>
> Step 1: Test reject without reason fails; approve writes Track Record; belt on fixtures produces a queued draft.
> Step 3: Commit `feat: review export belt`.

Review spec (`docs/superpowers/specs/2026-08-19-review-approve.md:3-9`):

> Builder cannot approve. Comments ≠ last yes. Last yes sits on **irreversible verbs**: publish, boost, send, claim. Day one: 100% human on benefit claims.
>
> **Forbidden:** Machina Sports as the model; day-one 80% auto-approve; an agent as the signature.

Export spec (`docs/superpowers/specs/2026-08-19-preview-export.md:3-7`):

> Export **paused/draft** (Adobe TikTok path). Media ops owns go-live.
>
> **Forbidden:** “create, preview, publish in one go” inside the ESP; API/transactional bypass as the happy path.

Feedback + Track Record (`feedback-writer.md:3-7`; `track-record.md:3-9`):

> Require a reason. Distill. Write back into Track Record / Brand Brain the same day.
>
> Every draft + judge verdict + **named human** + **reason**.
>
> **Forbidden:** one-click reject; CTR overriding a legal no; silent “learning approval patterns.”

Global / spine (`docs/decisions/001-global-rulings.md` §3.3, §5.1–5.2; `progress.md:4`):

> No autonomous publish. A named human must approve, with a reason.
> No CrewAI. Plain-code belt; models sit inside steps.
> free adapters are the default. ~$5 optional only if a tool clearly improves the show… Do not spend the $5 unless image quality is the leftover demo gap after Task 9.

Task 7 park (`progress.md:30`; `016-task-7-rules-judge-loop.md`):

> parked for Task 10 — persist flag_human

## 5. Options considered

### A. One-click reject / optional reason “for the demo”

- **Would give:** Faster queue clicks in a live walk.
- **Would cost:** Breaks Feedback + Track Record locks (“Require a reason”; “one-click reject” forbidden). Same miss survives twice.
- **Lost because:** locked. `decide` strips and refuses blank/whitespace; HTTP 400/422 without a reason.

### B. Approve writes Track Record; reject does not

- **Would give:** Smaller ledger; only “wins” feed the brief.
- **Would cost:** Spec wants every named human + reason. Losses are how the factory stops repeating cure-claim copy.
- **Lost because:** both verdicts call `write_feedback` the same day (`review.py` → `feedback.py`).

### C. Autopublish / “create → preview → publish” export

- **Would give:** Sexier demo climax.
- **Would cost:** Export forbidden path; regulated beauty/health day-one rule; PPTX “no approval chains” was explicitly rejected as doctrine.
- **Lost because:** ZIP is `*_paused.zip` with `published: false`; `test_no_publish_route` asserts no publish/boost path.

### D. CrewAI / LangGraph-as-the-whole-factory for the belt

- **Would give:** Fancy orchestrator marketing.
- **Would cost:** Global “No CrewAI”; node-replay double-bills image gen; second architecture to tear out before legal review.
- **Lost because:** `boxes/belt.py` is plain functions calling existing boxes. No crewai dependency.

### E. Persist every strategist concept through the factory

- **Would give:** Full grid on the queue for the UI to browse.
- **Would cost:** Longer demo run, more stub images, more review noise for a walk that needs one showable post.
- **Lost / accepted:** `MAX_FACTORY_CONCEPTS = 1` — first concept only, then 2–3 caption variants. Recorded as implementer concern #1; **accepted** for the demo. Strategist grid is not persisted for UI.

### F. Spend the ~$5 on a paid image API now that the belt exists

- **Would give:** Nicer cards in the paused ZIP.
- **Would cost:** Burns the only demo spend slot after Task 9 already judged the stub showable.
- **Lost because:** `$5` still unspent; belt/export tests use stub / tiny PNG gen.

### G. Do nothing / leave belt + review to Task 11

- **Would give:** Smaller Task 10 diff.
- **Would cost:** Plan files list; Command Center would invent orchestration and reason rules in React; `flag_human` park stays open.
- **Lost because:** the plan.

### H. Brand Brain / Cerebras Knowledge write-back on distill

- **Would give:** Spec-faithful “Distill before search (Cerebras)” production path.
- **Would cost:** Demo has no Cerebras Knowledge; Company Brain ≠ Inference API.
- **Lost / simplified:** `distill` = whitespace collapse to 280 chars. No Brand Brain. Production owns Cerebras write-back.

## 6. Decision

Command-layer boxes + plain-code belt + HTTP for Task 11. No Command Center pages. No autonomous publish. `$5` unspent.

```text
run_radar()
  fetch → score → research (deep_dive only) → store reports

run_factory(report_id)
  brief → strategist → copywriter
       → loop (hard_rules + judge inside)
       → art_director.compose
       → upsert_draft (queue)
  # concepts[:MAX_FACTORY_CONCEPTS] with MAX=1 (accepted)

decide(draft_id, user, verdict, reason)
  strip user + reason → refuse blank
  insert_decision → write_feedback (Track Record same day)
  # approve and reject both ledger

export_pack(draft_id)
  ensure image → {id}_paused.zip
  preview.html + card.png + caption.txt + meta.json (published: false)
```

| Piece | Role |
|---|---|
| `apps/api/boxes/review.py` | `decide` — named human, reason required, not a publish button |
| `apps/api/boxes/feedback.py` | Distill + Track Record write; `load_track_examples` for brief wins/losses |
| `apps/api/boxes/export.py` | Paused ZIP packer |
| `apps/api/boxes/belt.py` | `run_radar` / `run_factory` |
| `apps/api/boxes/brief.py` | `load_track_record_examples` now delegates to feedback (closes empty stub) |
| `apps/api/db.py` | `drafts.flag_human` column (+ migrate), decisions, track_record, `list_queue` |
| `apps/api/main.py` | HTTP surfaces for Task 11 |
| Tests | `apps/api/tests/test_review.py`, `test_belt.py` |

HTTP:

- `POST /radar/run`
- `POST /factory/run` `{report_id}`
- `POST /review/{draft_id}` `{user, verdict, reason}`
- `GET /export/{draft_id}` → zip bytes
- `GET /signals` `/scores` `/reports` `/drafts` `/queue` (+ by-id for report/draft)

## 7. Why this exact shape

### Reason required on both verdicts

`decide` (`review.py:14-36`) strips `user` and `reason`. Empty name → “A named person must approve or reject.” Empty/whitespace reason → “A reason is required. Same miss should not survive twice.” Verdict must be `approve` or `reject`. Type-level lock remains `Decision.reason` `Field(min_length=1)` (`models.py:98`). Review HTTP body allows empty strings into the handler so the *box* owns the friendly error (`ReviewIn` in `main.py:71-74`), matching “friendly user errors, technical detail in logs.”

### Track Record same day — approve and reject

After `insert_decision`, every successful `decide` calls `write_feedback(decision, draft)` (`review.py:35-36`). Feedback packs draft + judge + named human + reason + distilled + sku/market + `flag_human` into `track_record` (`feedback.py:14-31`). Brief’s old empty helper now imports `load_track_examples` (`brief.py:21-29`) so later packs can show 3 wins / 3 losses without a second write path.

### Distill is collapse, not a model

`distill` (`feedback.py:9-11`) joins whitespace and caps at 280. Name looks like “AI summarize”; demo meaning is “searchable one-liner for the ledger.” Cerebras Knowledge write-back stays production (Company Brain, not Inference API).

### `flag_human` column **and** judge JSON

Task 7 left the flag on `Draft` + `judge` dict only. Task 10 adds `drafts.flag_human INTEGER` on create and `_ensure_column` for older DBs (`db.py` drafts DDL + migrate). `upsert_draft` ORs column/dict and writes both (`db.py` upsert_draft docstring: “flag_human is a column and copied into judge JSON”). `_draft_from_row` rehydrates both so `get_draft` after reload still shows the flag. Loop comment updated: flag is “also a drafts.flag_human column on persist” (`loop.py:55`).

### Queue = drafts without a decision

`list_queue` (`db.py`) is drafts with no row in `decisions`. Approve removes the draft from the queue without deleting it — history stays in `drafts` + `decisions` + `track_record`.

### First concept only (accepted)

`MAX_FACTORY_CONCEPTS = 1` (`belt.py:23`, used at `belt.py:80`). Strategist still builds a grid; factory only loops the first concept’s 2–3 variants, then breaks once anything queues. Plan Step 1 asked for “a queued draft,” not the full grid on disk. **Accepted** concern for demo speed; UI persistence of the grid is Task 11 / later if needed.

### Export is paused ZIP, not publish

`export_pack` (`export.py:68-92`) writes `{draft_id}_paused.zip` under `EXPORT_DIR` or `data/exports`. Contents: `caption.txt`, `meta.json` (`status: paused`, `published: false`), `preview.html` with a fake phone frame and “PAUSED — NOT PUBLISHED” stamp, and `card.png` when an image exists (composes via Art Director if missing). Filename and meta make the pause impossible to miss. No `POST /publish`, no boost, no send.

### Plain-code belt; models inside steps

`run_radar` / `run_factory` (`belt.py`) call existing boxes. Hard rules + judge stay inside `run_loop` (plan listed them as separate belt stages; code comment notes the loop already runs both each round — same order, one call). Art Director sits after the loop so queued drafts have `image_path`. Visual prompt forbids text/logo/claims in the *image* prompt (`belt.py:65-67`); locks still overlay in code.

### HTTP for Task 11, not UI

Routes live in `main.py` so Task 11 is wiring, not invention. `/radar/run` shares the 6/min fetch rate bucket with `/radar/fetch` (implementer concern #5; fine for a couple demo hits). Errors return `{"error": ...}` without stack traces (`_friendly`).

### `$5` unused

Belt and export tests use `IMAGE_GEN_MODE=stub` / `TinyGen` PNGs. No Recraft/Firecrawl purchase. Ledger and report: budget still unspent.

## 8. What we refused

- **One-click reject / blank reason.**
- **Autonomous publish** or ESP “create, preview, publish in one go.”
- **CrewAI / roaming agent belt.**
- **Spending the ~$5** — stub / tiny gen remains the show path.
- **Command Center pages** — Task 11 files list.
- **Brand Brain / Cerebras Knowledge write-back** on distill (production).
- **Expire / withdraw button** from the Preview spec — binding for this task was `export_pack` only.
- **Role model for “builder cannot approve”** — any named string with a reason can decide today (see deferred).
- **Persisting the full strategist grid** — first concept only, accepted.
- **Day-one 80% auto-approve** / agent-as-signature (Review spec forbidden).

## 9. Verification that actually ran

**Claimed** in `task-10-report.md` from `apps/api` local `.venv`. This documentation agent did **not** re-run pytest. No compose, no live GDELT, no live image API.

TDD red first (claimed): 14 failed (`No module named 'boxes.review'` / `'boxes.export'` / `'boxes.belt'`; missing `upsert_draft` / `get_draft` / `run_radar`).

After `24e103a` (claimed):

```text
pytest tests/test_review.py tests/test_belt.py -q
14 passed in 1.51s

pytest tests/ -q
102 passed in 2.88s
```

| Test | What it would fail on |
|---|---|
| `test_reject_without_reason_fails` | empty/whitespace reason accepted; decision or ledger written |
| `test_approve_without_reason_fails` | approve without reason succeeds |
| `test_approve_writes_track_record` | no decision / no Track Record / brief wins empty / draft still on queue |
| `test_reject_with_reason_writes_loss` | reject does not appear in losses pack |
| `test_flag_human_survives_reload` | column or `judge.flag_human` lost after `get_draft` |
| `test_export_pack_is_paused_zip_not_publish` | missing preview/PNG/caption; meta not paused / published true |
| `test_post_review_http_requires_reason` | 200 on blank reason; stack/trace leaked |
| `test_post_review_http_approve` | approve HTTP ≠ 200 or drops reason |
| `test_get_export_http_returns_zip` | non-zip body |
| `test_no_publish_route` | publish/boost path exists |
| `test_run_radar_fetch_score_research_store` | kill not discarded; deep-dive not stored |
| `test_belt_on_fixtures_produces_queued_draft` | no queued draft / no PNG / cures or PCOS in caption |
| `test_run_factory_unknown_report_fails` | missing report does not raise |
| `test_http_lists_and_radar_factory` | list GETs or POST radar/factory fail |

**Seen by implementer (claimed):** fixture radar → one deep-dive; factory → queued draft with PNG on disk; ZIP contents; HTTP 400/422/200 paths.

**Not seen:** live compose; live GDELT/News/Reddit through `run_radar`; paid `IMAGE_GEN_URL`; Command Center click-walk.

pycache under `apps/api/tests/` includes `test_review.cpython-313-pytest-8.4.2.pyc` and `test_belt.cpython-313-pytest-8.4.2.pyc` — evidence the suite ran on this machine at some point; not a substitute for re-running here.

## 10. Review findings and rulings

Reviewer package: `review-865446a..24e103a.diff`. Ledger (`progress.md:37-39`):

> Task 10: complete (commits 865446a..24e103a, review clean)
> Task 10: minor (deferred): tautological flag_human assert; second decide allowed; empty SKU wildcard; export PNG optional
> Task 10: implementer DONE_WITH_CONCERNS — persist flag_human, review+reason, track record, export paused zip, belt + HTTP. No Command Center UI.

Controller / session ruling for this journal: **Approved with only minors.** No Important/Critical. No fix commit. Exact reviewer prose file is **UNKNOWN** (not kept beyond the ledger lines). Minors below mix ledger deferred notes and implementer concerns; **first concept only** is explicitly **accepted**.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| Critical | none | — | — |
| Important | none | — | — |
| Minor (deferred) | `test_belt_on_fixtures…` assert `flag_human is False or True` is tautological | Tighten later if needed | **Parked** |
| Minor (deferred) | Second `decide` on same draft_id allowed (PK is `draft_id, decided_at`) | Demo queue drops after first decision; history appends | **Parked** |
| Minor (deferred) | Empty SKU/market wildcards in `load_track_examples` | Empty pack still allowed by brief design | **Parked** |
| Minor (deferred) | Export PNG arcname only written if file exists after ensure | `_ensure_image` usually composes; edge case remains | **Parked** |
| Concern (accepted) | Factory uses **first concept only** | Demo needs one queued post, not the full grid | **Accepted** (`MAX_FACTORY_CONCEPTS = 1`) |
| Concern | Distill = whitespace collapse; no Brand Brain | Production Cerebras Knowledge | **Honored** |
| Concern | Expire / withdraw not built | Binding was `export_pack` | **Parked → production / later** |
| Concern | “Builder cannot approve” has no role model | Any named user + reason can decide | **Parked → production / Task 11 UX** |
| Concern | `/radar/fetch` and `/radar/run` share 6/min cap | Fine for demo walk | **Accepted** |
| Concern | No live compose / live GDELT in this task | Fixtures + mocks by design | **Honored** |
| Budget | `$5` unspent | Do not buy unless stub later fails the show | **Honored** |

Out of scope honored: no Command Center pages in the diff (API + boxes + tests + db only).

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Command Center story pages (radar / factory / queue / preview) | **Task 11** |
| CI + demo README walk | **Task 12** |
| Role model / “builder cannot approve” enforcement | production plan / Task 11 UX policy |
| Expire / withdraw with state | production Preview & Export |
| Brand Brain / Cerebras Knowledge distill write-back | production Track Record |
| Persist full strategist grid for UI (beyond first concept) | leftover / Task 11 if product wants it |
| Tighten tautological `flag_human` assert | leftover test |
| Idempotent / single-decision guard on `decide` | leftover / production |
| Empty SKU wildcard matching | leftover; may be intentional for sparse ledger |
| LiteLLM `complete_json` still stub | leftover; templates walk the demo |
| Live image API / optional ~$5 if stub later judged weak | controller open-budget only |
| Shared rate limit between `/radar/fetch` and `/radar/run` | leftover; OK for demo |

## 12. Third-party check list

Under 15 minutes:

1. `git log --oneline 865446a..24e103a` — expect exactly `24e103a feat: review export belt`. No later Task 10 fix.
2. Open `.superpowers/sdd/2026-08-19-demo/progress.md` — Task 10 complete, review clean, minors deferred, **`$5` still unspent**.
3. Open `apps/api/boxes/review.py` — `decide` refuses blank/whitespace reason; calls `write_feedback` for every verdict.
4. Open `apps/api/boxes/feedback.py` — `write_feedback` → `insert_track_record`; `distill` is whitespace collapse only.
5. Open `apps/api/boxes/brief.py` — `load_track_record_examples` delegates to `boxes.feedback.load_track_examples` (no longer hard-coded `[], []`).
6. Open `apps/api/boxes/export.py` — dest name ends with `_paused.zip`; meta has `published: False`; preview stamp “PAUSED — NOT PUBLISHED.”
7. Open `apps/api/boxes/belt.py` — `MAX_FACTORY_CONCEPTS = 1`; `run_radar` / `run_factory` order matches the plan; `compose` after `run_loop`.
8. Open `apps/api/db.py` — `drafts.flag_human` column; `_ensure_column` migrate; `track_record` table; `list_queue` excludes decided drafts.
9. Open `apps/api/main.py` — routes for `/radar/run`, `/factory/run`, `/review/{draft_id}`, `/export/{draft_id}`, list GETs; **no** publish/boost path.
10. From `apps/api`: `pytest tests/test_review.py tests/test_belt.py -q` — expect 14 passed if the claimed count still holds.
11. Read `test_reject_without_reason_fails` + `test_approve_writes_track_record` + `test_reject_with_reason_writes_loss` — reason required; both verdicts ledger.
12. Read `test_flag_human_survives_reload` — column **and** `judge.flag_human` after reload.
13. Read `test_export_pack_is_paused_zip_not_publish` + `test_no_publish_route`.
14. Confirm no `apps/web/app/radar` / `factory` / `queue` / `preview` pages in this commit (Task 11).
15. Confirm `.env.example` still defaults `IMAGE_GEN_MODE=stub` and no Recraft/Firecrawl spend was introduced.
