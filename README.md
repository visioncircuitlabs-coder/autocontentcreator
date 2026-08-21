# Content Machine

An always-on content system for regulated consumer brands (Kenvue-class: Neutrogena, Listerine, and siblings). It watches culture, drafts on-brand posts, blocks illegal claims, and learns from every human yes/no.

**Status:** free-tool **demo** is walkable end-to-end (Trend Radar → Brand Brain fixtures → Content Factory belt → Command Center approve/export). Production swap-map is parked.

- Demo plan: `docs/superpowers/plans/2026-08-19-demo.md`
- Production (later): `docs/superpowers/plans/2026-08-19-production.md`
- **Why we built it this way** (third-party review pack): `docs/decisions/`

The demo brand pack is an **unofficial Neutrogena** fixture for show — not a partner build, not medical advice, not a claim that we speak for Kenvue.

## What it does

- **Trend Radar** — Fetch pulls GDELT / Google News RSS / Reddit JSON, scores what matters, deep-dives with sources.
- **Brand Brain** — unofficial Neutrogena brand book, approved claims, disclaimer, exclusion list, past decisions.
- **Content Factory** — a conveyor belt. Code moves work left to right. Agents write. Hard rules + a locked judge catch claims. Image is a port (Pillow stub by default; paste `IMAGE_GEN_*` when ready).
- **Command Center** — you approve with a reason. The machine never publishes regulated content on its own. Export is a ZIP.

## Look at the architecture

Open this file in a browser (double-click it):

`docs/show-me-architecture.html`

Every box is clickable. Each panel ends with who already ships a version of that idea.

## How to run the demo

From the repo root:

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
- API health: http://localhost:8000/health → `{"ok": true}`

Port 3000 is often taken by another project on this PC. This app uses **3050** on purpose.
- API health: http://localhost:8000/health → `{"ok": true}`

SQLite lives at `./data/demo.db`. Compose mounts `./data` into the API as `/data`.

### Keys (all optional for the walk)

| Variable | What it does |
|---|---|
| `XAI_API_KEY` | Optional Grok key. Empty = word-count ranking and template copy. |
| `GEMINI_API_KEY` | Optional. Same idea as Grok. |
| `GROQ_API_KEY` | Optional. Same idea as Grok. |
| `IMAGE_GEN_URL` / `IMAGE_GEN_KEY` | Optional. Leave empty and keep `IMAGE_GEN_MODE=stub` for the Pillow card (logo + disclaimer stamped in code). When you have an HTTP image API, set the URL/key and `IMAGE_GEN_MODE=http`. |
| `NEXT_PUBLIC_API_URL` | Browser → API (default `http://localhost:8000`). |

Paid trend/research/image vendors are **not** required. Do not put Firecrawl, Brandwatch, Recraft, or similar keys in `.env` for this demo.

### Stranger walk (definition of done)

1. `docker compose up --build`
2. Open http://localhost:3050 → **Look for ideas**
3. Pick a closer-look card (or **Use a sample idea (practice)** if this search is empty)
4. **Make a post** → pick a version → **Your call** (name + why)
5. Phone preview → **Download pack** (does not go live)

Train someone with `docs/runbooks/make-a-post.md`. Words we use: `docs/conventions/words-we-use.md`.

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
uvicorn main:app --reload --port 8000
```

```text
cd apps\web
npm install
npm test
npm run build
npm run dev
```

## CI

GitHub Actions (`.github/workflows/ci.yml`): `compileall` + `pytest` on Python 3.12 for `apps/api`, and `npm run build` on Node 22 for `apps/web`. No Docker in CI — that gate stays local/`docker compose up --build`.

## Research

| File | What it is |
|---|---|
| `docs/decisions/` | Third-party why-journal (constraints, rejected options, review rulings) |
| `docs/research/2026-08-18-industry-research.md` | Locked industry findings + design decisions |
| `docs/research/raw-dossiers-2026-08-18.json` | Full dossiers with source links |
| `docs/research/2026-08-19-cerebras-company-brain.md` | What Cerebras *Knowledge* actually is (the company brain) |
| `private deck notes (not in this repo)` | What we take / reject from the reference pitch deck |
| `docs/research/sota/2026-08-19-sota-scorecard.md` | Chosen process + tools per box (X + GitHub swarm) |

## How we will deploy it (later)

CI on GitHub Actions (already wired for lint-ish + test + web build). App in Docker. Secrets only in `.env` (never in git). Currency INR, timezone Asia/Kolkata, Razorpay if we take payments.

## Ground rules already locked

1. Loops win. Agents only live *inside* steps.
2. Compliance is the product, not a feature.
3. A human approves every published regulated item. An approval dial can loosen review later — it is logged, never implicit.
4. The moat is memory: every decision with a reason.

## Repo

Private at [visioncircuitlabs-coder/autocontentcreator](https://github.com/visioncircuitlabs-coder/autocontentcreator). All work stays on the D: drive. Feature work happens in `.worktrees/`.
