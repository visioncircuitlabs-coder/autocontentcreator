# Invariants

A reviewer must be able to fail a PR from this file. Do not “improve” a lock without a written decision in `docs/decisions/`.

## Product

| Lock | Meaning |
|---|---|
| Unofficial Neutrogena fixture | Not a Kenvue partner build. Not medical advice. Still the default when `BRAND_SLUG` is unset. |
| Unofficial Lay's demo | `BRAND_SLUG=lays`. Not PepsiCo. Not a real Lay's ad. Chile Limón is the hero SKU. |
| India Instagram first | Market `IN`, timezone `Asia/Kolkata`, currency INR if money appears. |
| India Instagram first | Market `IN`, timezone `Asia/Kolkata`, currency INR if money appears. |
| Same 17 boxes as production | Demo uses cheaper guts. Do not collapse to “analyze + one image.” |
| Loops win | Plain-code belt. Agents only inside steps. **No CrewAI.** |
| Compliance is the product | Hard rules have no LLM. Benefit claims are 100% human-yes in the demo. |
| No autonomous publish | Approve files a reason. ZIP is paused. Media ops posts in real life. |
| Memory is the moat | Every yes/no needs a name and a reason. Same miss should not survive twice. |

## Safety

| Lock | Where it lives |
|---|---|
| Web pages are **data**, never instructions | Researcher wraps sources in `<source url=…>`. Copy/judge/craft say the same. |
| Gazette bans (no model) | `cures`, `heals`, `best`, `only`, `guaranteed` — `boxes/hard_rules.py` |
| Disclaimer required on benefit lines | Fixture text in `fixtures/neutrogena/disclaimer.txt` |
| Writer ≠ judge | `boxes/loop.py`: hard rules + claims judge + craft review. Max 3 rounds, then `flag_human`. |
| Named human, non-empty reason | API `boxes/review.py` and UI both reject blanks. |
| Brand marks not in the image model | **Neutrogena:** Imagine prompt has no text, no logo. `art_director.apply_locks` paints `NEUTROGENA` + disclaimer. **Lays (founder override, 2026-09-02):** Lay's logo may go into Imagine because it is on the real pack. Do not stamp a second wordmark. Disclaimer overlay stays in code. See `docs/decisions/024-lays-client-demo.md`. |

## Radar and factory shape

| Lock | Value |
|---|---|
| Fetcher does not score | `boxes/fetcher.py` stores title/snippet/url only |
| Scorer does not write ads | Gate only: `discard` / `background` / `deep_dive` |
| Researcher does not write captions | Diamond: plan angles → read pages → skeptic. Radar research runs **without** extra chat (`chat=None`) |
| One closer look per Look | `MAX_DEEP_DIVES = 1` |
| One concept into copy | `MAX_FACTORY_CONCEPTS = 1` then 2–3 caption variants |
| Picture waits for a pick | `run_factory` does not compose. `paint_chosen` is `POST /factory/image` |
| Locked queries | Fetcher uses `skincare_in`. Grok web uses `LOCKED_QUERY`. Do not “search the whole web.” |

## Build / ops

| Lock | Meaning |
|---|---|
| All work on D: | `D:\PROJECTS\autocontentcreator`. C: is full. Caches in `.cache/` on D:. |
| Feature work in `.worktrees/` | Do not pile uncommitted product work on `main`. |
| Secrets in `.env` | Gitignore. Commit `.env.example` only. Never commit keys, `.pptx`, `.claude/`, `.firecrawl/`. |
| Friendly errors, technical logs | User sees `{"error": "…"}`. JSONL at `data/logs/machine.jsonl`. |
| Tests with the change | API pytest next to boxes. Web tests in `apps/web/desk/*.test.ts`. |
| Computed values must be used | If you add a score/ETA/flag, show it, log it, or test it. |
| Free adapters default | Do not add Brandwatch, Firecrawl paid, Recraft, Cerebras Knowledge, Veeva. |
| gstack is the *build* loop | Plan/review/ship. It is not the product architecture. |
| Kenvue Content Factory PPTX | Reference only. Do not adopt “no approval chains” or day-one 80% auto-approve. |

## Two Cerebras

Do not collapse these:

1. **Company Brain** — Cerebras Knowledge. How we would build Brand Brain in production. Demo does not call it.
2. **Inference API** — cheap scoring, if ever, via a gateway. Not “we run on Cerebras chips.”

## What you may not add without a decision note

- A second approval path
- Publishing adapters (Meta, Buffer, later)
- CrewAI / multi-agent orchestrators as the belt
- Putting logo/disclaimer/claims into Imagine or any image prompt (**except unofficial Lay's**, where the pack logo may be in the Imagine prompt; disclaimer still overlays in code)
- Generating photos during Look or during `Make a post`
- Auto-approve, including “80% auto-approve”
- New paid vendors
- Changing on-screen jargon back to `radar`, `deep_dive`, `gate` on the default walk
