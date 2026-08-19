# Task 1 — Scaffold so `docker compose up` shows a shell

## 1. Identity

| | |
|---|---|
| **Task** | 1 of 12 |
| **Plan heading** | `### Task 1: Scaffold so docker compose up shows a shell` in `docs/superpowers/plans/2026-08-19-demo.md:173` |
| **Range** | `a72b33c41554ee99b99349297b7bd06f6b223a80` .. `ff411ea8bcc70f45b5e306784e53929c48338cfa` |
| **Head commit** | `ff411ea` — `chore: scaffold demo apps` |
| **Dates** | Plan locked 2026-08-19 (`a72b33c`, worktree log `1787156241 +0530`). Scaffold committed 2026-08-19 22:34 IST (`ff411ea`, worktree log `1787159046 +0530`). Live compose proof same evening; **no second commit**. |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` on `feat/foolproof-design` |
| **Implementer (first)** | agent `01a01adc` — **cancelled**. Docker Desktop engine pipe missing; hung on compose; left uncommitted files. |
| **Implementer (fresh)** | agent `01a01af9` — `DONE_WITH_CONCERNS`, then fix-round verify-only. |
| **Reviewer** | agent `01a01afb` — Approved, with one **Important**: live compose not proven. |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/progress.md` (gitignored scratch). Reports: `task-1-brief.md`, `task-1-report.md`. Review pack: `review-a72b33c..ff411ea.diff`. |
| **Later code warning** | `apps/api/main.py`, `apps/api/Dockerfile`, and `apps/api/.dockerignore` were rewritten by Tasks 3+. Quotes below distinguish **as of `ff411ea`** from **today**. |

`git show --stat ff411ea` (from the review package):

```text
 .env.example                  |   21 +-
 .gitignore                    |    8 +
 CLAUDE.md                     |   27 +-
 README.md                     |   31 +-
 apps/api/.dockerignore        |    5 +
 apps/api/Dockerfile           |   17 +
 apps/api/main.py              |    8 +
 apps/api/pytest.ini           |    3 +
 apps/api/requirements.txt     |    5 +
 apps/api/tests/test_health.py |   11 +
 apps/web/.dockerignore        |    3 +
 apps/web/Dockerfile           |   35 ++
 apps/web/app/layout.tsx       |   15 +
 apps/web/app/page.tsx         |    7 +
 apps/web/next-env.d.ts        |    7 +
 apps/web/next.config.ts       |    7 +
 apps/web/package-lock.json    | 1016 +
 apps/web/package.json         |   22 +
 apps/web/public/.gitkeep      |    0
 apps/web/tsconfig.json        |   36 ++
 docker-compose.yml            |    4 +
 infra/docker-compose.yml      |   35 ++
 22 files changed, 1308 insertions(+), 15 deletions(-)
```

## 2. What the user would see

Copy `.env.example` to `.env` (keys can stay empty). From the repo root, run `docker compose up`. A browser at `http://localhost:3000` shows a one-line page that says **Content Machine demo**. `http://localhost:8000/health` returns `{"ok": true}`. There is no Fetch button, no Radar, no Factory, no Queue. It is an empty machine that proves the two processes start.

## 3. The problem this task was solving

Nothing in the repo could be started. The design was locked (`a72b33c` demo + parked production plans) and the 17 boxes had specs, but a later implementer had nowhere to plug a FastAPI route or a Next page. Task 2 needs a Python package and a pytest harness. Task 3 needs an HTTP app and a compose network. Task 11 needs a Next app router. Task 12 needs a `docker compose up` story in the README.

If this task had been skipped, every later box would have reinvented “how do I run this,” and the CEO rule that the app starts with one command would have been fiction.

Depends on this: **every later demo task**. Direct consumers: Task 2 (types land in `apps/api`), Task 3 (`POST /radar/fetch` on the same app + the same compose API container), Task 11 (Command Center pages under `apps/web/app/`), Task 12 (CI + demo README).

## 4. Constraints that were already locked

Quoted, not softened.

From the plan header (`docs/superpowers/plans/2026-08-19-demo.md:9`):

> **Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLite (demo), Next.js Command Center, httpx, feedparser, LiteLLM talking to one free/cheap chat model (Gemini Flash or Groq). Image: `IMAGE_GEN_URL` + `IMAGE_GEN_KEY` stub until you paste the API. Docker Compose. Pytest.

From Global Constraints (`2026-08-19-demo.md:11-22`):

> Same box names, same handoffs, same forbidden lists as `docs/superpowers/specs/`.
> Demo is a prototype of the bigger machine, not “analyze + one image.”
> Secrets in `.env` only. Work on `feat/foolproof-design` worktree. D: for caches.
> Tests with each box. `docker compose up` runs the demo.

From Task 1 itself (`2026-08-19-demo.md:186-191`):

> **Step 2:** FastAPI app + compose (api, web). No Postgres in demo — SQLite file on D: `D:/PROJECTS/autocontentcreator/.worktrees/feat-foolproof-design/data/demo.db`.
> **Step 3:** `.env.example` with `CHAT_MODEL=gemini/gemini-2.0-flash`, `GEMINI_API_KEY=`, `IMAGE_GEN_URL=`, `IMAGE_GEN_KEY=`, `IMAGE_GEN_MODE=stub`.
> **Step 4:** `docker compose up` works. Commit `chore: scaffold demo apps`.

From the SDD ledger (written *before* implementers ran):

> Root `docker-compose.yml` will include `infra/docker-compose.yml` so `docker compose up` works from repo root.

From `CLAUDE.md` / project rules (already true before the scaffold):

> Keep everything on `D:\PROJECTS\autocontentcreator` (C: is full). Isolated work goes in `.worktrees/`.
> Do **not** add the 17 boxes or Command Center pages until the next plan tasks say so.

From the parked production plan (`docs/superpowers/plans/2026-08-19-production.md:13`):

> You are ready to host Postgres + Langfuse, **not SQLite**.

From the CEO global rules that apply to every project: the app must start with `docker compose up`; secrets in `.env` (gitignored); `.env.example` committed; tests alongside features.

## 5. Options considered

### A. Do nothing / leave the repo as design-only

**Would have given us.** Zero chance of scaffolding the 17 boxes “too early.” Matches the *previous* `CLAUDE.md` lock (“no app code until the design spec is signed off”).

**Would have cost.** Task 2–12 have no home. `docker compose up` stays a lie. The demo walk in the plan (`2026-08-19-demo.md:414`) cannot start.

**Why it lost.** The design *was* signed off. `a72b33c` is the demo plan. The task heading is the unlock.

### B. Scaffold later, inside Task 11 / Task 12

**Would have given us.** Implementers of boxes 1–10 would write against a fictional file map. One “big bang” compose at the end.

**Would have cost.** Every box test would invent its own runner. Health, env, and SQLite path would be renegotiated six times. The CEO could not see *anything* until the last week.

**Why it lost.** The plan put scaffold first so the empty machine is showable and later tasks stay small.

### C. Postgres in compose from day one (the production spine)

**Would have given us.** One less swap later. Real concurrent writers. pgvector ready for Brand Brain.

**Would have cost.** Another container, another volume, another thing to install on a machine whose C: is already full. The production plan is explicit that Postgres waits for funds (`2026-08-19-production.md:13, 41, 49`). The Task 1 step forbids it: “No Postgres in demo.”

**Why it lost.** Demo guts are cheaper. Same box names, not the same database.

### D. Hardcode the D: SQLite path the plan wrote

**Would have given us.** Literal obedience to `D:/PROJECTS/autocontentcreator/.worktrees/feat-foolproof-design/data/demo.db`.

**Would have cost.** The API image is `python:3.12-slim` (Linux). That path does not exist inside the container. CI on GitHub would also not be a Windows D: checkout. Tests would fight a shared file.

**Why it lost.** The *intent* of the lock is “SQLite file on this worktree’s disk, not a hosted database.” `SQLITE_PATH` keeps that intent and works in three places: host pytest, host uvicorn, Docker `/data/demo.db`.

### E. Put the full compose file at the repo root (no `include:`)

**Would have given us.** One file. Slightly easier to read.

**Would have cost.** The plan file map already says `infra/docker-compose.yml`. The ledger already said the root file will `include:` infra so the CEO command stays `docker compose up` from the repo root.

**Why it lost.** We wanted both: the documented infra home, and the one-line root command.

### F. Prove health only by starting Docker in every test / in CI

**Would have given us.** A test that the *container* listens on `:8000`, not just that the FastAPI object returns JSON.

**Would have cost.** The first implementer already hung because the Docker engine pipe was missing. This host also had `buzz-prod-relay-1` and a leftover Next process publishing `:3000`. CI (Task 12) is specified as “lint + pytest + web build,” not “start compose.” A red health test that needs Docker Desktop is an environmental flake, not a product test.

**Why it lost.** `TestClient` proves the contract `GET /health → {"ok": true}`. Live compose is a one-time acceptance hit, not the regression gate.

## 6. Decision

Empty demo shell. Two processes, one command, no boxes.

```text
repo root
  docker-compose.yml          include: infra/docker-compose.yml
  infra/docker-compose.yml    services: api :8000, web :3000
  .env.example                SQLITE_PATH + empty chat/image keys
  apps/api/
    main.py                   GET /health → {"ok": true}          # as of ff411ea: 8 lines
    Dockerfile                python:3.12-slim, COPY main.py only # later Task 3: COPY .
    requirements.txt          fastapi, uvicorn, pydantic, pytest, httpx
    tests/test_health.py      TestClient, not live Docker
  apps/web/
    app/page.tsx              <h1>Content Machine demo</h1>
    Dockerfile                Next standalone → node server.js
```

Named interfaces as of `ff411ea`:

- `GET /health` → `{"ok": true}` (`apps/api/main.py` at commit; still `apps/api/main.py:42-44` today).
- Web on `:3000`, API on `:8000` (`infra/docker-compose.yml:6-7, 30-31`).
- `SQLITE_PATH` env, default `data/demo.db` on the host, `/data/demo.db` in compose (`/.env.example:7-9`, `infra/docker-compose.yml:11, 21-22`).
- Image slot already stubbed in env: `IMAGE_GEN_MODE=stub` (no image code yet).

## 7. Why this exact shape

### Why FastAPI + Next + SQLite (not Flask, not Vite-only, not Postgres)

The plan named the stack. That is the lock. The reasons underneath it, so a reviewer does not think we shrugged:

- **FastAPI** is the smallest Python server that speaks the already-locked Pydantic v2 models as JSON and ships `TestClient` (Starlette + httpx) so Task 1’s health test and Task 3’s `POST /radar/fetch` do not need a running socket. Flask would have meant a second serialization story next to Pydantic. Django would have been an admin we do not want and a Postgres assumption we just forbade.
- **Next.js** is the Command Center the plan named. Task 11 will add `/radar`, `/factory`, `/queue`, `/preview/[id]` under the App Router. A static `index.html` would have been rewritten in Task 11. Vite+React would have worked; it was not the locked name.
- **SQLite, not Postgres** is a *demo* ruling, not a production ruling. Production plan: “ready to host Postgres + Langfuse, not SQLite.” Trend Reports and Track Record in production move to Postgres (`2026-08-19-production.md:30-31, 41`). Demo needs a file on D: that `docker compose up` can mount. No extra container, no hosted bill, no C: cache for a Postgres image.

### Why the root compose includes the infra compose

```text
# docker-compose.yml:1-4
name: content-machine
include:
  - path: infra/docker-compose.yml
```

The plan file map puts compose under `infra/`. The CEO command is `docker compose up` from the repo root (`CLAUDE.md:15-17`, README “How to run the demo shell”). The SDD ledger pre-decided the `include:`. That is how both remain true: infra stays the home of service definitions; the root file is a one-liner so nobody has to `cd infra`.

### Why `SQLITE_PATH` is env-driven (Docker vs D: host)

The plan’s absolute D: path is the *host* location of the worktree, not a path that exists in `python:3.12-slim`.

| Where | `SQLITE_PATH` | File |
|---|---|---|
| Host (this worktree) | `data/demo.db` (`.env.example:9`) | `D:\PROJECTS\...\feat-foolproof-design\data\demo.db` |
| API container | `/data/demo.db` (`infra/docker-compose.yml:11`, Dockerfile `ENV`) | bind `../data:/data` |
| Pytest | tmp path (Task 3 `conftest.py`; Task 1 had no db yet) | never the demo file |

A hardcoded `D:/PROJECTS/.../data/demo.db` would have failed in Linux containers and in CI. An env var is the same intent: one SQLite file on this machine’s disk, gitignored (`*.db` and `data/` in `.gitignore:33-34`).

### Why health is `TestClient`, not live Docker, in the test we will keep

`apps/api/tests/test_health.py:1-11` imports the FastAPI app and hits `/health` in-process:

```python
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
```

This is the regression gate. It does not start Docker. That is deliberate:

1. First implementer `01a01adc` was cancelled because the Docker engine pipe was missing. A test that requires the engine would have cancelled Task 1 again.
2. Live `:3000` on this LAN was already owned by `buzz-prod-relay-1` and a leftover Next from another repo. Compose proof needed a human to free the port. CI cannot do that.
3. Task 12’s CI is lint + pytest + web build, not `docker compose up`.
4. The *product* contract is the JSON body. The *ops* contract (image builds, ports publish) was proven once in the fix round and belongs in a smoke, not in every pytest.

Live compose **was** proven in fix round 1 (see Verification). It is not the test we committed.

### Why the web page is one heading

`apps/web/app/page.tsx` is:

```tsx
export default function HomePage() {
  return (
    <main>
      <h1>Content Machine demo</h1>
    </main>
  );
}
```

`CLAUDE.md:7` after this commit: “Do **not** add the 17 boxes or Command Center pages until the next plan tasks say so.” The live acceptance string is `"Content Machine"` inside 200 HTML. Anything more is Task 11.

### Why `.env.example` already lists chat and image keys

Task 1 does not call a model. The plan still required those names in `.env.example` so later boxes do not invent `OPENAI_API_KEY` or a Recraft key. Empty values are the demo default. `IMAGE_GEN_MODE=stub` is the parked image ruling from the budget line in the ledger.

### Why the API Dockerfile originally copied only `main.py`

As of `ff411ea` the API image was:

```text
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
```

At that moment `main.py` *was* the app. The hole: the moment Task 3 adds `boxes/` and `adapters/`, the running container would still be the 8-line health app. Task 3 closed this by changing to `COPY . .` (`2c817fa`). That is a known Task 1 hole with a named owner, not an accident we forgot.

### Why `httpx>=0.27,<1` and not `httpx2`

The first on-disk scaffold (cancelled implementer) had `httpx2>=2,<3`. That is not a real package. Starlette/FastAPI `TestClient` imports `httpx`. The fresh implementer fixed this before `ff411ea`. Without that pin, `test_health_returns_ok` cannot even import.

## 8. What we refused

- **Postgres / `DATABASE_URL`.** The previous `.env.example` had a commented `DATABASE_URL`. Task 1 replaced it with `SQLITE_PATH`. Production buys Postgres later.
- **Paid keys as required.** `FIRECRAWL_API_KEY` and `OPENROUTER_API_KEY` comments were removed from `.env.example`. Free adapters are the default. ~$5 optional only after a stub image exists (ledger budget ruling; not this task).
- **The 17 boxes and Command Center pages.** No `boxes/`, no `/radar`, no `/factory`. `CLAUDE.md` was rewritten to say so.
- **CrewAI, LangGraph-as-the-app, a “hello agent.”** The belt is later (`apps/api/belt/` in the file map). Agents sit inside steps, and there are no steps yet.
- **Hardcoded D: path inside Python.** See options.
- **Auth, users, HTTPS, a custom domain.** Demo on localhost.
- **Starting compose as a pytest.** See options.
- **Committing `.env`, `.venv`, `node_modules`, `.next`, `data/`, `*.db`, `.superpowers`.** All gitignored. `*.tsbuildinfo` added in this commit.

## 9. Verification that actually ran

Separate **seen** from **claimed**.

### Seen — API pytest (implementer, from `apps/api` after the httpx fix)

```text
.                                                                        [100%]
1 passed in 0.29s
```

Test name: `test_health_returns_ok`. Asserts status 200 and body `{"ok": true}`.

### Seen — web typecheck (implementer, `apps/web`, `node_modules` already present)

```text
npm test  →  next typegen && tsc --noEmit  →  exit 0
```

This is *not* a browser test. It is the script the package.json named `test`.

### Seen — compose config, not compose up (original report)

`docker compose config` resolved the root `include:` to infra services `api` / `web`, ports 8000/3000, `SQLITE_PATH=/data/demo.db`, `./data` → `/data`, `IMAGE_GEN_MODE=stub`.

`docker compose up` was **not** run in the commit session. Host `:3000` was already taken (`buzz-prod-relay-1`). Engine had been down for the cancelled implementer.

### Seen — live compose (fix round 1, no new commit)

Host prep: stopped leftover Next PID `35492` (`D:\PROJECTS\contentfactory\...`) and temporarily stopped `buzz-prod-relay-1`. Did not stop Docker Desktop.

```text
docker compose up --build -d
content-machine-api-1   Up   0.0.0.0:8000->8000/tcp
content-machine-web-1   Up   0.0.0.0:3000->3000/tcp

GET http://127.0.0.1:8000/health  →  {"ok":true}
GET http://127.0.0.1:3000         →  200 HTML containing "Content Machine"
```

Controller later confirmed the same two hits. Stack left running for later tasks. `buzz-prod-relay-1` left stopped so this demo could keep `:3000`.

### Claimed but not a committed test

“`docker compose up` works” is in the plan Step 4. It is **seen** in the fix round. It is **not** a pytest. Task 12 may add CI; it had not.

### Not committed (verified against `.gitignore`)

`.venv`, `node_modules`, `.next`, `.superpowers`, `.env`, `data/`, `__pycache__`, `*.tsbuildinfo`.

## 10. Review findings and rulings

Reviewer `01a01afb` on `a72b33c..ff411ea`: **Approved**.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| **Important** | Live `docker compose up` was not proven on this machine this session. Files and `docker compose config` looked runnable; host `:3000` was taken. | Prove the two live hits before calling Task 1 complete. Do not invent a second commit if the files are already correct. | **Fixed, no commit.** Fix round 1 brought the stack up. Controller confirmed `/health` and the web heading. Ledger: “1 addressed, 0 open.” |
| (none Critical) | — | — | — |
| Process | First implementer `01a01adc` cancelled (engine pipe missing). | Fresh implementer; compose verification for *that* pass = files + pytest health; engine down is environmental. | Followed. The Important then forced the live proof once the engine was up. |

No other Important/Critical items are recorded in the ledger or the task report. If a reviewer wrote more prose than those two sentences, it is **UNKNOWN** — it was not kept in the gitignored ledger beyond the one-line ruling.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| API Docker image copies only `main.py`. Next box that adds modules will be invisible inside the container until the Dockerfile copies the tree. | **Task 3** (`2c817fa` changed to `COPY . .`). |
| `.dockerignore` does not yet exclude `.env` / `data/` / `*.db`. Harmless while the image only copies `main.py`; becomes real the moment it copies the tree. | **Task 3 fix** `7da5c99`. |
| `init_db()` does not exist. Health does not touch SQLite. Compose still mounts `./data` so the path is ready. | **Task 2** creates tables; **Task 3** wires `init_db` on startup. |
| No CI workflow. Health is TestClient-only. | **Task 12**. |
| Web is a heading, not the Command Center story. | **Task 11**. |
| Chat/image env vars are declared and unused. | Tasks 4/8/9. Empty keys must still walk the demo (plan: fixture templates / stub image). |
| Host `:3000` collides with `buzz-prod-relay-1`. Demo compose wins only if that container stays stopped. | Operator / production plan. Not a code change. |
| `docker compose up` is proven by hand, not by CI. | Task 12 (optional smoke) or production plan. |

## 12. Third-party check list

A stranger with this worktree can confirm the *scaffold contract* in under 15 minutes. Do these in order.

1. `git log --oneline a72b33c..ff411ea` — one commit, message exactly `chore: scaffold demo apps`.
2. Open `docker-compose.yml`. It must `include:` `infra/docker-compose.yml` and define no services of its own.
3. Open `infra/docker-compose.yml`. Services `api` and `web`, ports `8000` and `3000`, `SQLITE_PATH: /data/demo.db`, volume `../data:/data`, `IMAGE_GEN_MODE` default `stub`. No `postgres` service.
4. Open `.env.example`. Required names present: `CHAT_MODEL=gemini/gemini-2.0-flash`, `GEMINI_API_KEY=`, `IMAGE_GEN_URL=`, `IMAGE_GEN_KEY=`, `IMAGE_GEN_MODE=stub`, `SQLITE_PATH=data/demo.db`. No `FIRECRAWL_API_KEY`, no `DATABASE_URL`.
5. Open `apps/api/tests/test_health.py`. It uses `TestClient`, not `docker`, not a live URL.
6. From `apps/api`: `pytest tests/test_health.py` — 1 passed, body `{"ok": true}`.
7. From `apps/web`: `npm test` — typecheck exit 0.
8. `git show ff411ea:apps/api/main.py` — eight lines, only `/health`. (Today’s `main.py` also has `/radar/fetch`; that is Task 3.)
9. `git show ff411ea:apps/api/Dockerfile` — `COPY main.py .` only.
10. `apps/web/app/page.tsx` still has a single `<h1>Content Machine demo</h1>` unless Task 11 has landed.
11. Optional live: free host `:3000`, then `docker compose up --build -d`. `GET :8000/health` → `{"ok":true}`. `GET :3000` HTML contains `Content Machine`.
12. Confirm `data/` and `*.db` are gitignored. Confirm no `.env` in `git ls-files`.
