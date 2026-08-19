# Task 2 — Types + SQLite

## 1. Identity

| | |
|---|---|
| **Task** | 2 of 12 |
| **Plan heading** | `### Task 2: Types + SQLite` in `docs/superpowers/plans/2026-08-19-demo.md:195` |
| **Range** | `ff411ea8bcc70f45b5e306784e53929c48338cfa` .. `074be52956c72227371cc8474ad0c21b3a856a1f` |
| **Head commit** | `074be52` — `feat: domain types and sqlite` |
| **Dates** | 2026-08-19 22:44 IST (worktree log `1787159680 +0530`), ~10 minutes after the scaffold. |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Implementer agent id** | UNKNOWN (ledger only says “Task 2: complete”). Git author on the commit is `vision <visioncircuitlabs@gmail.com>`. |
| **Reviewer agent id** | UNKNOWN. Ledger: “review clean.” |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/progress.md`. Reports: `task-2-brief.md`, `task-2-report.md`. Review pack: `review-ff411ea..074be52.diff`. |
| **Later code warning** | `apps/api/models.py` later gained `Concept`, `Brief`, and `Draft.flag_human`. `apps/api/db.py` later gained `briefs` and upsert helpers. Quotes of the *lock* refer to `074be52`. Current files are a superset. |

`git show --stat 074be52`:

```text
 apps/api/db.py                | 98 +++++++++++++++++++++++++++++++++++++++++++
 apps/api/models.py            | 72 +++++++++++++++++++++++++++++++
 apps/api/tests/test_models.py | 97 ++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 267 insertions(+)
```

## 2. What the user would see

Nothing new in the browser. `GET /health` is still `{"ok": true}`. The Command Center is still one heading. Under the floor, the demo now has a typed vocabulary (a Signal, a Score, a Decision…) and an empty SQLite file that can hold those rows. The user only notices this later, when Fetch writes headlines and when Approve refuses to save without a reason.

## 3. The problem this task was solving

Task 1 left an empty FastAPI app. Task 3 must return `list[Signal]`. Task 4 must attach a `Score` with a `gate`. Task 10 must write a `Decision` whose `reason` is required. Production adapters must plug into the *same* field names (`2026-08-19-demo.md:7`: “Production adapters … plug into the same ports later”).

If each box invented its own JSON (`headline` vs `title`, `ok` vs `approve`, `fit` vs `brand_fit`), the belt would become a translation layer and the parked production swap would be a rewrite.

Depends on this: **Task 3** (`Signal`, `signals` table, `SQLITE_PATH`), **Task 4** (`Score`), **Task 5** (`TrendReport`), **Task 6** (`Claim` status enum), **Task 7–10** (`Draft`, `Decision`, the other tables). Task 8 later added `Brief` / `Concept` on top of this file; those names were in the plan file map but not in the locked type block.

## 4. Constraints that were already locked

The plan header is labelled **“Interfaces (shared types — lock these names)”** (`2026-08-19-demo.md:98-169`). That heading is the force. The field names below were copied, not redesigned.

```python
# apps/api/models.py  — locked in the plan
class Signal(BaseModel):
    signal_id: str
    seen_at: datetime
    happened_at: datetime | None
    source: Literal["gdelt", "news_rss", "reddit", "rss"]
    url: str
    title: str
    snippet: str
    lang: str = "en"
    market: str = "IN"
    query_id: str
    raw_ref: str = ""

class Score(BaseModel):
    signal_id: str
    brand_fit: int          # 1-10
    velocity: int           # 1-10
    safety: Literal["ok", "watch", "kill"]
    reason: str
    gate: Literal["discard", "background", "deep_dive"]
    model: str
    prompt_version: str
# … TrendReport, Claim, Draft …
```

Task 2 steps (`2026-08-19-demo.md:201-206`):

> Produces: `init_db()`, tables `signals`, `scores`, `reports`, `claims`, `drafts`, `decisions`
> **Step 1:** Tests: Claim status enum; Signal requires url; Decision requires reason.
> **Step 3:** Commit `feat: domain types and sqlite`.

Task 10 already locked the Decision verb (`2026-08-19-demo.md:367`):

> `decide(draft_id, user, verdict, reason) -> Decision`  # reason required

Track Record spec (`docs/superpowers/specs/2026-08-19-track-record.md:3, 9`):

> Every draft + judge verdict + **named human** + **reason**.
> **Forbidden:** … one-click reject with no reason.

README ground rule 4 (already on main before this task):

> The moat is memory: every decision with a reason.

Source Fetcher spec output shape (`docs/superpowers/specs/2026-08-19-source-fetcher.md:20-32`) uses the same signal fields the plan locked (`signal_id`, `seen_at`, `happened_at`, `source`, `url`, `title`, `snippet`, `lang`, `market`, `query_id`, `raw_ref`). Demo `source` literals drop the paid names (`brandwatch`, `meltwater`, `wizikey`, `konnect`, `tiktok_cc`, `firecrawl`) and keep `gdelt | news_rss | reddit | rss`.

Global: **No Postgres in demo.** SQLite file via `SQLITE_PATH` (Task 1 already chose env-driven over the plan’s absolute D: path). stdlib `sqlite3` only — the brief/report restates this.

Inherited from Task 1 and still in force: FastAPI + Next + SQLite; root compose `include:`s infra; health stays TestClient; work on D:; do not add the 17 box modules yet.

## 5. Options considered

### A. Do nothing / invent types inside each later box

**Would have given us.** Task 2 stays a no-op. Task 3 could have declared `class Signal` next to the fetcher.

**Would have cost.** Six copies of “what is a signal.” Production adapters would have nothing stable to target. Decision.reason would be a UI nicety, not a type.

**Why it lost.** The plan put types in their own task *because* they are the shared language.

### B. SQLAlchemy + Alembic, or Postgres now

**Would have given us.** Migrations, ORM, easier production cutover.

**Would have cost.** A second runtime, a second mental model, and a database the plan forbade. Demo is one operator, one file, `CREATE TABLE IF NOT EXISTS`.

**Why it lost.** “stdlib `sqlite3` only — no SQLAlchemy/Postgres” (task-2-report). Production plan swaps the *store* later, not this week.

### C. Rename fields to “better” names (`fit_score`, `approved`, `link`, `summary`)

**Would have given us.** Taste. Slightly nicer English.

**Would have cost.** The lock is the names. Scorer gates (`<5` discard, `5–7` background, `≥8` deep_dive) are written against `brand_fit` and `gate`. Fetcher spec lawyers ask for `raw_ref` (vendor mention id, not a scrape blob). A rename here is a silent spec break.

**Why it lost.** Verbatim copy is the point of a lock.

### D. Make `Decision.reason` optional “for now,” enforce it in Task 10 UI

**Would have given us.** Faster types. A later form could require the textarea.

**Would have cost.** Any code path that constructs a Decision could store `reason=""` and the Track Record spec’s forbidden “one-click reject with no reason” would already be representable. The moat is the ledger, not the button.

**Why it lost.** Task 2 Step 1 tests it *now*. `Field(min_length=1)` is the type-level lock. Task 10 still has to persist it; it must not be allowed to invent a default.

### E. Tighten `brand_fit`/`velocity` to `ge=1, le=10`, `url` min_length 1, `reason` stripped

**Would have given us.** The comments `# 1-10` would be real. `url=""` and `reason="   "` would fail.

**Would have cost.** Extra fields the locked block did not write. A reviewer later marked these **minor / deferred**, not blocking.

**Why it lost *for this task*.** The implementer copied the lock, including its looseness. The minors are still open (see Deferred). That is a choice to stay literal, not a claim that empty URLs are good.

### F. Wire `init_db()` into FastAPI startup in this commit

**Would have given us.** A database file the moment the API starts.

**Would have cost.** Task 2’s brief is “types + SQLite,” not “the belt writes rows.” Creating `data/demo.db` on every `uvicorn` would have mixed concerns and invited a committed `*.db`.

**Why it lost.** Report: “`init_db()` is exported and tested but not yet wired into FastAPI startup — intentional.” Task 3 calls it from the lifespan when signals actually land.

## 6. Decision

Two new files, one test module. No HTTP change.

```text
apps/api/models.py     Pydantic v2: Signal, Score, TrendReport, Claim, Draft, Decision
apps/api/db.py         get_sqlite_path / connect / init_db   (stdlib sqlite3)
apps/api/tests/test_models.py
```

As of `074be52` (`apps/api/models.py` then, still the core of `apps/api/models.py:7-99` today):

| Type | Role | Lock that forced it |
|---|---|---|
| `Signal` | One unique outside-world row | Fetcher spec + plan type block |
| `Score` | Brand-fit / velocity / safety / gate | Scorer (Task 4) |
| `TrendReport` | Capped deep-dive | Researcher (Task 5) |
| `Claim` | Approved / conditional / forbidden library row | Product Facts (Task 6) |
| `Draft` | A caption going through rules/judge/loop | Factory (Tasks 7–9) |
| `Decision` | Named human + verdict + **reason** | Review (Task 10) + Track Record spec |

`init_db()` creates six tables of the same names: `signals`, `scores`, `reports`, `claims`, `drafts`, `decisions`. List/dict fields (`angles`, `risks`, `sources`, `spent`, `judge`, `rules`) are TEXT, JSON when a later task writes them.

`Decision` (not in the locked *code block*, but in the file map and in Step 1):

```python
class Decision(BaseModel):
    draft_id: str
    user: str
    verdict: Literal["approve", "reject"]
    reason: str = Field(min_length=1)
    decided_at: datetime
```

SQLite path remains env-driven (`apps/api/db.py:10-14`):

```python
DEFAULT_SQLITE_PATH = "data/demo.db"

def get_sqlite_path() -> str:
    return os.environ.get("SQLITE_PATH", DEFAULT_SQLITE_PATH)
```

## 7. Why this exact shape

### Why the locked Pydantic field names were copied verbatim

The heading in the plan is “lock these names.” Production is a **swap map**, not a second product (`2026-08-19-production.md:7`: “The demo already uses the box names and ports. Production replaces adapters and raises the bar. It does not invent a new architecture.”).

If Task 2 had “improved” `brand_fit` to `fit`, Task 4’s gates (`<5` / `5–7` / `≥8`) would have been written against a private name, and a Brandwatch adapter in production would have had to translate twice. Verbatim is how a later stranger greps one word across spec, plan, model, table, and JSON.

Demo `Signal.source` is `Literal["gdelt", "news_rss", "reddit", "rss"]` — the *free* subset of the spec’s source list. Paid names are refused here so a demo row cannot pretend it came from Brandwatch.

`market: str = "IN"` is the pilot default (Neutrogena unofficial, India-first, timezone Asia/Kolkata). It is a default, not a second type.

`raw_ref: str = ""` is the spec’s “vendor mention id — not a scrape blob.” Task 3 fills it with a domain / guid / `t3_id`, never `content:encoded`.

### Why `Decision.reason` is required

This is not a UX preference. Three locks say the same thing:

1. Track Record spec forbids “one-click reject with no reason.”
2. README: “The moat is memory: every decision with a reason.”
3. Task 10 interface: `decide(..., reason) -> Decision  # reason required`.
4. Global demo rule: no autonomous publish; a named human must approve, with a reason. Benefit claims are 100% human-yes.

`reason: str = Field(min_length=1)` makes `Decision(reason="")` a `ValidationError` *before* any UI exists. `test_decision_requires_reason` is that gate. `test_decision_accepts_nonempty_reason` also locks `verdict="reject"` as a first-class value — a reject with a reason is a memory, not a void.

What this does *not* yet do: strip whitespace. `reason=" "` is length 1 and passes. That is a recorded minor, not an intended product rule.

### Why Signal requires `url` as a field, not yet as a non-empty string

Step 1: “Signal requires url.” The test omits the argument and expects `ValidationError`. That is a *presence* lock, matching the Pydantic field in the plan. The plan type is `url: str`, not `HttpUrl` and not `min_length=1`. Empty string is still representable. Task 3’s `build_signal` refuses empty URLs at the adapter boundary (`adapters/common.py:106-109`). The type stays literal; the fetcher stays strict.

### Why Claim status is a closed enum

Product Facts (Task 6) compare copy to a library of `approved | conditional | forbidden`. An open `str` would let a fixture invent `maybe` and the judge would have to guess. `test_claim_status_rejects_unknown` uses `status="maybe"`. `test_claim_status_accepts_allowed` uses `approved`.

### Why six tables, JSON-as-TEXT, no ORM

The belt is not concurrent. Demo is one operator. `CREATE TABLE IF NOT EXISTS` is the whole migration story. List/dict columns stay TEXT because sqlite3 has no JSON column type we need, and Pydantic already owns the shape. Production moves the same *names* onto Postgres (`2026-08-19-production.md:30-31`).

`decisions` primary key is `(draft_id, decided_at)`, not `draft_id` alone — a draft can be rejected then approved; both reasons stay. That matches “never drop comments at publish” (Track Record / production).

### Why FastAPI + Next + SQLite still (this task did not reopen it)

Task 1 chose the runtime. Task 2 only adds the store the plan already named. Next.js is untouched. FastAPI is untouched (`GET /health` still the only route). Replacing SQLite here would have been a plan break, not an improvement.

### Why `SQLITE_PATH` stays env-driven

Same three worlds as Task 1: host `data/demo.db`, Docker `/data/demo.db`, tests a temp file. `test_init_db_creates_tables` sets `SQLITE_PATH` to `tmp_path / "demo.db"` so the commit never creates `data/demo.db`. `*.db` and `data/` are gitignored.

## 8. What we refused

- **Postgres, SQLAlchemy, Alembic, `DATABASE_URL`.** Demo store is a file.
- **Renaming locked fields.** No `headline`, no `fit`, no `link`.
- **Paid `source` literals** (`brandwatch`, `firecrawl`, `tiktok_cc`) on the demo `Signal`. Those are production adapters.
- **Box modules.** No `boxes/fetcher.py`. Types only.
- **Wiring startup / writing rows.** No `upsert_signals` yet (Task 3).
- **CrewAI “memory objects.”** These are Pydantic models and SQL tables, not an agent memory.
- **Committing a `.db`.** Tests use `tmp_path`. `data/` is gitignored.

## 9. Verification that actually ran

### Seen — pytest from `apps/api` with local `.venv`

```text
.\.venv\Scripts\python.exe -m pytest tests/ -q
.......                                                                  [100%]
7 passed in 0.65s
```

| Test | What it actually asserts |
|---|---|
| `test_claim_status_rejects_unknown` | `status="maybe"` → `ValidationError` |
| `test_claim_status_accepts_allowed` | `approved` stored |
| `test_signal_requires_url` | missing `url` kwarg → `ValidationError` |
| `test_decision_requires_reason` | `reason=""` → `ValidationError` |
| `test_decision_accepts_nonempty_reason` | reject + `"off-brand tone"` |
| `test_init_db_creates_tables` | six table names under temp `SQLITE_PATH` |
| `test_health_returns_ok` | Task 1 still green |

### Claimed

TDD: failing import/validation tests first, then implement (task-2-report checklist). There is no kept red-run log in the ledger. Treat the *order* as claimed by the implementer; treat the 7-pass run as seen.

### Not run / not needed

No live Docker. No network. `init_db` is not called from `main.py` in this commit (`git show 074be52:apps/api/main.py` is still the 8-line health app).

### Not committed

`.env`, `data/*.db`. Only the three intended files.

## 10. Review findings and rulings

Ledger: **Task 2 complete, review clean** (`ff411ea..074be52`).

No Important or Critical items are recorded.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| **Minor (deferred)** | `brand_fit` / `velocity` are plain `int` with a comment `# 1-10`, not `Field(ge=1, le=10)` | Do not block Task 2. Copy the lock. Tighten later if a box writes 0 or 99. | **Still open** in current `apps/api/models.py:23-24`. Owner: production plan, or the first box that is hurt by an out-of-range write (Scorer writes 1–10 by construction). |
| **Minor (deferred)** | `Decision.reason` `min_length=1` accepts whitespace-only | Do not block. Task 10 UI should still require a real sentence; type can grow `strip` later. | **Still open** (`apps/api/models.py:98`). |
| **Minor (deferred)** | `Signal.url` allows `""` | Presence is tested; emptiness is not. Fetcher (Task 3) drops empty URLs in `build_signal`. | **Still open** on the model; **mitigated** at the adapter boundary. |

If the reviewer wrote a longer note, it is **UNKNOWN** — not preserved beyond those three minors in the ledger.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| `init_db()` not called on API startup | **Task 3** (`lifespan` in `apps/api/main.py:33-36`) |
| No `upsert_signals` / no writer | **Task 3** |
| `Brief` / `Concept` types not in this commit (they are in the plan file map, not in the locked type block) | **Task 8** |
| `Draft.flag_human` | **Task 7** (and persist parked for Task 10) |
| `briefs` table | **Task 8** |
| `brand_fit`/`velocity` bounds, whitespace reason, empty `url` | production plan / later hardening (see minors) |
| Health still TestClient-only; compose not re-proven in this task | Task 1 already proved compose; Task 12 for CI |
| Next.js unused | Task 11 |

## 12. Third-party check list

1. `git log --oneline ff411ea..074be52` — one commit, message exactly `feat: domain types and sqlite`.
2. `git show 074be52 --stat` — exactly three files: `models.py`, `db.py`, `test_models.py`.
3. Diff `git show 074be52:apps/api/models.py` against the plan block at `docs/superpowers/plans/2026-08-19-demo.md:102-155`. Field names for `Signal`, `Score`, `TrendReport`, `Claim`, `Draft` must match. Do not accept a “cleanup” rename.
4. Confirm `Decision.reason` is `Field(min_length=1)` and `verdict` is `Literal["approve", "reject"]`.
5. Confirm `Claim.status` is `Literal["approved", "conditional", "forbidden"]`.
6. Confirm `Signal.source` is the *demo* literal (`gdelt`, `news_rss`, `reddit`, `rss`) — no `brandwatch` / `tiktok`.
7. `apps/api/db.py`: `get_sqlite_path()` reads `SQLITE_PATH`; default `data/demo.db`; `init_db()` creates the six table names. No SQLAlchemy import. No Postgres.
8. From `apps/api`: `pytest tests/test_models.py tests/test_health.py` — the six model/db tests plus health.
9. `test_decision_requires_reason` must fail the empty string, not merely omit the argument.
10. `test_signal_requires_url` must omit `url`, not pass `url=""`.
11. `git show 074be52:apps/api/main.py` still has no `init_db` — wiring later is intentional.
12. Confirm no `*.db` in the commit (`git show --name-only 074be52`).
