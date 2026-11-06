# Content Machine

An always-on content system for regulated consumer brands (Kenvue-class: Neutrogena, Listerine, and siblings). It watches culture, drafts on-brand posts, blocks illegal claims, and learns from every human yes/no.

**Status:** free-tool **demo is walkable** on this branch (`feat/foolproof-design`). Last landed wave (24 Aug): reliability harness, per-country claims, brand memory in SQLite **and** Markdown. Stage for agents: `docs/agents/WHERE-WE-ARE.md`. Production swap-map is parked.

The demo brand pack is an **unofficial Neutrogena** fixture for show — not a partner build, not medical advice, not a claim that we speak for Kenvue.

**Why we built this:** [docs/GOAL.md](docs/GOAL.md)

## What it does

- **Trend Radar** — Look for ideas pulls GDELT / Google News RSS / Reddit JSON (and optional Grok search), scores what fits, deep-dives one closer look.
- **Brand Brain** — unofficial Neutrogena brand book, approved claims, disclaimer, exclusion list, past decisions.
- **Content Factory** — a conveyor belt. Code moves work. Agents write captions. Hard rules + a locked judge catch claims. After you pick a version, **Grok Imagine** makes a 4:5 photo (Chile Limón image-edits the real pack). Neutrogena stamps wordmark + disclaimer in code; Lays does not.
- **Command Center** — you approve with a reason. The machine never publishes. Export is a paused ZIP.

## Look at the architecture

Open this file in a browser (double-click it):

`docs/show-me-architecture.html`

Every box is clickable. Each panel ends with who already ships a version of that idea.

**Docs map:** [docs/DOC-MAP.md](docs/DOC-MAP.md)  
**Coding agents:** [AGENTS.md](AGENTS.md) → [docs/agents/README.md](docs/agents/README.md)

## How to run the demo

Short version below. Full how-to: [docs/howto-run-the-demo.md](docs/howto-run-the-demo.md).

From **this worktree** (`D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design`):

1. Copy env template (keys can stay empty):

```text
copy .env.example .env
```

On macOS/Linux: `cp .env.example .env`

2. Start everything:

```text
docker compose up --build
```

- Make today’s post: http://localhost:3050
- API health: http://localhost:8000/health → `{"ok": true, "chat": …}`

Port 3000 is often taken on this PC. This app uses **3050** on purpose.

SQLite lives at `./data/demo.db`. Compose mounts `./data` into the API as `/data`.

### Keys (all optional for the walk)

| Variable | What it does |
|---|---|
| `XAI_API_KEY` | Grok chat, optional Grok web headlines, and Grok Imagine. Empty = word-count ranking, template copy, Pillow card. |
| `CHAT_MODEL` | Default `xai/grok-4.6`. |
| `GEMINI_API_KEY` / `GROQ_API_KEY` | Alternate chat. |
| `IMAGE_GEN_MODE` | `imagine` (Grok Imagine), `stub` (Pillow card), or `http` (paste `IMAGE_GEN_URL`). Example file defaults to `imagine`. |
| `IMAGE_GEN_MODEL` | `grok-imagine-image` when mode is imagine. |
| `NEXT_PUBLIC_API_URL` | Browser → API. Walk uses `/engine` (Next proxy, 5 minutes). |

Paid trend/research/image vendors are **not** required. Do not put Firecrawl, Brandwatch, Recraft, or similar keys in `.env` for this demo.

If `.env` still says `IMAGE_GEN_MODE=stub`, a restart will draw the dark card even if you used Imagine earlier. Set the file, or export `imagine` on the API process. See [docs/agents/runtime.md](docs/agents/runtime.md).

### Stranger walk (definition of done)

1. `docker compose up --build`
2. Open http://localhost:3050 → **Look for ideas**
3. Pick a closer-look card (or **Use a sample idea (practice)** if this search is empty)
4. **Make a post** → pick Version 1, 2, or 3 → **Make the picture** → **Make a short video**
5. **Your call** (name + why) → phone preview → **Download pack** (does not go live)

Train someone with [docs/runbooks/make-a-post.md](docs/runbooks/make-a-post.md). Words we use: [docs/conventions/words-we-use.md](docs/conventions/words-we-use.md). Picture-first explainer: `docs/eli5-make-a-post/eli5-make-a-post.html`.

Optional API smoke (API already running):

```text
python scripts/demo_walk.py
```

Skips cleanly if nothing is listening on `:8000`.

### Without Docker (PowerShell, from this worktree)

```text
cd apps\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn main:app --host 127.0.0.1 --port 8000
```

```text
cd apps\web
npm install
npm test
$env:NEXT_PUBLIC_API_URL = "/engine"
$env:ENGINE_URL = "http://127.0.0.1:8000"
npx next dev --hostname 127.0.0.1 --port 3050
```

## CI

GitHub Actions (`.github/workflows/ci.yml`): `compileall` + `pytest` on Python 3.12 for `apps/api`, and `npm run build` on Node 22 for `apps/web`. No Docker in CI — that gate stays local/`docker compose up --build`.

API docs: [docs/reference-api.md](docs/reference-api.md).

## Research and why

| File | What it is |
|---|---|
| `docs/decisions/` | Third-party why-journal (constraints, rejected options, review rulings) |
| `docs/research/2026-08-18-industry-research.md` | Locked industry findings + design decisions |
| `docs/research/raw-dossiers-2026-08-18.json` | Full dossiers with source links |
| `docs/research/2026-08-19-cerebras-company-brain.md` | What Cerebras *Knowledge* actually is (the company brain) |
| `private deck notes (not in this repo)` | What we take / reject from the reference pitch deck |
| `docs/research/sota/2026-08-19-sota-scorecard.md` | Chosen process + tools per box (X + GitHub swarm) |
| `docs/designs/research-and-copy.md` | Demo-fence method for research and captions |

Demo plan (historical, **already built**): `docs/superpowers/plans/2026-08-19-demo.md`  
Production (later): `docs/superpowers/plans/2026-08-19-production.md`

## How we will deploy it (later)

CI on GitHub Actions (already wired for lint-ish + test + web build). App in Docker. Secrets only in `.env` (never in git). Currency INR, timezone Asia/Kolkata, Razorpay if we take payments.

## Ground rules already locked

1. Loops win. Agents only live *inside* steps.
2. Compliance is the product, not a feature.
3. A human approves every published regulated item. An approval dial can loosen review later — it is logged, never implicit.
4. The moat is memory: every decision with a reason.

## Repo

Private at [visioncircuitlabs-coder/autocontentcreator](https://github.com/visioncircuitlabs-coder/autocontentcreator). All work stays on the D: drive. Feature work happens in `.worktrees/`.
