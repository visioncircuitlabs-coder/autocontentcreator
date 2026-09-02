# Gotchas

These already cost real time. Read before you “fix” Look, Pick, or pictures.

## Docs lie in old files

- `main` CLAUDE.md / README may still say **design stage, no app**. Wrong. This worktree is the app.
- `docs/superpowers/plans/2026-08-19-demo.md` still reads like a to-do. **Do not implement it again.**
- Specs say “locked design, not built.” Intent is locked; software is on this branch.
- Plan path `apps/api/belt/` does not exist. Use `apps/api/boxes/belt.py`.

## Two trees, two CLAUDE.md files

| Path | Role |
|---|---|
| `D:\PROJECTS\autocontentcreator\CLAUDE.md` | Often injected as workspace rules |
| This worktree `CLAUDE.md` | Product commands |

If they fight, **this worktree + `docs/agents/invariants.md` win.**

## Imagine vs stub

`.env` can say `IMAGE_GEN_MODE=stub` while uvicorn was launched with `imagine`. Restart without the export → Pillow card, not Grok. `.env.example` is `imagine`. Imagine needs `XAI_API_KEY`. Failures fall back to stub; the user still sees *a* picture.

## Make a post must not paint

Old belt composed three Imagine photos while Pick waited. That is why the page hit 5 minutes and the banner blamed Look. `run_factory` is text. `paint_chosen` is the later button.

## “That took too long” is the proxy

Next `/engine` aborts at 300s. The UI cannot tell Look from Make from Imagine. Do not special-case the string back to “that look.”

## Junk sources

`google-analytics.com` does **not** match a `google.com` substring check. Denylist hosts **and** `google.com` tracker paths. Mirror the list in `researcher.py` and `desk/review.ts`. Never show junk on the main Pick card; **Sources** is optional.

## Practice idea hid “Also in this look”

Fixture used to replace `signals`. Keep this-run headlines. Practice is a labeled extra closer look, not a news wipe.

## Night-rain Hydro Boost

Caption words like monsoon/humid leaked into a cinematic still. `visual_prompt` is a bright 4:5 water-gel ad. Lighting is a short keyword map, not the caption pasted into Imagine. No people, no letters in the model. Wordmark is Pillow, not SVG text (SVG text often vanished → navy rectangle).

## Preview crop

Feed is 1080×1350. CSS `object-fit: contain` + `aspect-ratio: 4/5`. Cover on a square frame sliced the disclaimer.

## Chat 20s timeout

LiteLLM `timeout=20`. Craft/copy often fail open to templates or craft PASS. That is why you still get a walkable caption when Grok is slow. Do not raise this blindly without re-timing Look.

## Only five Grok scores

`MAX_CHAT_SCORES = 5`. Keyword fallback can cap fit so you never reach 8 (closer look). Celebrity Neutrogena news can still score 5 (discard). Do not score the whole RSS firehose live.

## GDELT 429 / Reddit 403 / Grok web ~40s

Fetcher logs and continues. Quiet-source notes on Pick are normal. Grok web is optional when `XAI_API_KEY` is set; locked query only.

## Worktree `.git` is a file

`gitdir: .../worktrees/name`. Copy tools that skip a `.git` **directory** will not skip it, and can overwrite the pointer. After a copy, read the first line of `.git`.

## C: full

No `npm` / pip / OpenCode caches on C:. XDG and npm cache on D: under `.cache/`.

## Overlay vs model

Never put `NEUTROGENA`, claims, or the disclaimer in the Imagine prompt. They are stamped after. If you “just add the logo to the prompt,” you will get misspelled packaging and we lose the legal line. **Lays exception:** designed headline/CTA may live in the Imagine prompt (print-ad craft); the unofficial disclaimer still overlays in code as a tiny legal line.

## Kenvue deck / Cerebras / gstack

PPTX is not the spec (no day-one 80% auto-approve). Cerebras Knowledge ≠ inference API. gstack is how we plan/review/ship, not the 17 boxes.

## Foreign transcripts

Claude/Codex/OpenCode/**Hermes** session dumps are untrusted history. Re-read the files.

Hermes on this machine lives at `D:\Hermes agent`. Content Machine session `20260824_015715_fd3d0f` had cwd **`main`** even while it wrote into the feat worktree. Do not follow that cwd.

The 25 Aug Hermes “where we are” recap said **269 tests**. Git HEAD `a324b70` is the memory wave with **329 tests collected**. Prefer git. How-to: `docs/howto-resume-a-session.md`.

Local `feat/foolproof-design` can sit dozens of commits ahead of `origin`. `git status` before you assume GitHub is current.

## Agent terminals block inline `python -c`

Debug one-liners via `python -c "..."` hit a consent gate and stall the run.
Use pytest itself, or write a throwaway `debug_*.py` script and delete it
after. Same for anything piping pytest through `tail/head`.

