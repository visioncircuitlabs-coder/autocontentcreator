# Content Machine

An always-on content system for regulated consumer brands (Kenvue-class: Neutrogena, Listerine, and siblings). It watches culture, drafts on-brand posts, blocks illegal claims, and learns from every human yes/no.

**Status:** design locked. Two build plans: a free-tool **demo** (same 17 boxes) and a parked **production** swap-map.

- Demo: `docs/superpowers/plans/2026-08-19-demo.md`
- Production (later): `docs/superpowers/plans/2026-08-19-production.md`

## What it does

- **Trend Radar** — a scheduled loop that pulls the outside world and scores what matters to the brand.
- **Brand Brain** — the memory: brand book, approved claims, trend reports, and every past approval/rejection.
- **Content Factory** — a conveyor belt. Code moves work left to right. Agents write. A locked judge and hard rules catch claims.
- **Command Center** — you approve. The machine never publishes regulated content on its own.

## Look at the architecture

Open this file in a browser (double-click it):

`docs/show-me-architecture.html`

Every box is clickable. Each panel ends with who already ships a version of that idea.

## Research

| File | What it is |
|---|---|
| `docs/research/2026-08-18-industry-research.md` | Locked industry findings + design decisions |
| `docs/research/raw-dossiers-2026-08-18.json` | Full dossiers with source links |
| `docs/research/2026-08-19-cerebras-company-brain.md` | What Cerebras *Knowledge* actually is (the company brain) |
| `private deck notes (not in this repo)` | What we take / reject from the reference pitch deck |
| `docs/research/sota/2026-08-19-sota-scorecard.md` | Chosen process + tools per box (X + GitHub swarm, Aug 19) |

## How we will run it (later)

```text
docker compose up
```

Nothing to start yet — there is no app until the spec is approved.

## How we will deploy it (later)

CI on GitHub Actions. App in Docker. Secrets only in `.env` (never in git). Currency INR, timezone Asia/Kolkata, Razorpay if we take payments.

## Ground rules already locked

1. Loops win. Agents only live *inside* steps.
2. Compliance is the product, not a feature.
3. A human approves every published regulated item. An approval dial can loosen review later — it is logged, never implicit.
4. The moat is memory: every decision with a reason.

## Repo

Private at [visioncircuitlabs-coder/autocontentcreator](https://github.com/visioncircuitlabs-coder/autocontentcreator). All work stays on the D: drive. Feature work happens in `.worktrees/`.
