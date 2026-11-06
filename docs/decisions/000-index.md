# Decision journal — index

**Product:** Content Machine (Vision Circuit Labs). Unofficial Neutrogena pilot.
**Branch / worktree:** `feat/foolproof-design` at `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design`
**Plan:** `docs/superpowers/plans/2026-08-19-demo.md`
**Production (parked):** `docs/superpowers/plans/2026-08-19-production.md`
**Locked box specs:** `docs/superpowers/specs/`
**Build process:** Superpowers subagent-driven development (fresh implementer per task + reviewer + fix loop). Ledger: `.superpowers/sdd/2026-08-19-demo/progress.md` (gitignored scratch; the committed record is this folder + git log).

## Status

| File | Scope | Status |
|---|---|---|
| [001-global-rulings.md](001-global-rulings.md) | Budget, architecture locks, what we will not buy | done |
| [010-task-1-scaffold.md](010-task-1-scaffold.md) | Compose + FastAPI + Next shell | filled |
| [011-task-2-types-sqlite.md](011-task-2-types-sqlite.md) | Domain types + SQLite | filled |
| [012-task-3-fetcher.md](012-task-3-fetcher.md) | Free-source fetcher | filled |
| [013-task-4-scorer.md](013-task-4-scorer.md) | Relevance scorer | filled |
| [014-task-5-researcher.md](014-task-5-researcher.md) | Capped deep-dive | filled |
| [015-task-6-brand-facts.md](015-task-6-brand-facts.md) | Brand book + claims fixtures | filled |
| [016-task-7-rules-judge-loop.md](016-task-7-rules-judge-loop.md) | Hard rules, judge, loop | filled |
| [017-task-8-factory-text.md](017-task-8-factory-text.md) | Brief, strategist, copywriter | filled (re-review clean at 750a86b) |
| [018-task-9-art-director.md](018-task-9-art-director.md) | Image port + compositor | filled (review clean at 865446a; $5 unspent) |
| [019-task-10-review-export-belt.md](019-task-10-review-export-belt.md) | Review, feedback, export, belt | filled (review clean at 24e103a; first concept only accepted; $5 unspent) |
| [020-task-11-command-center.md](020-task-11-command-center.md) | Phone-usable UI story | filled (review clean at 1bb268a after fixture fix; compose rebuild claimed in Task 12) |
| [021-task-12-ci-docs.md](021-task-12-ci-docs.md) | CI + demo README | filled (chore 32b37fa + docs pack 9a2d705; $5 unspent; remote Actions not seen here) |
| [022-walk-ui.md](022-walk-ui.md) | Five-step App Mode walk | filled |
| [023-agent-and-human-docs.md](023-agent-and-human-docs.md) | Agent handbook + doc refresh | filled |
| [024-product-video.md](024-product-video.md) | ~5s product clip as a factory step | locked |

## One-line rulings a reviewer must not miss

- The demo is the **same 17 boxes** as production, with cheaper guts. It is not “analyze + one image.”
- **Free adapters are the default.** About $5 of paid tooling is allowed only if it clearly improves the *show*, after the stub image exists. Recraft/Firecrawl still not bought. Live walk can use **Grok Imagine** via the existing `XAI_API_KEY` (`IMAGE_GEN_MODE=imagine`). That is not the Recraft envelope.
- **Agents:** start at `AGENTS.md` / `docs/agents/`. Specs lock intent; live file map is `docs/agents/boxes.md`.
- **No CrewAI.** Code moves work; models sit inside steps.
- **Web pages are data, never instructions.**
- **No autonomous publish.** A named human must approve, with a reason.
- **Benefit claims are 100% human-yes** in the demo.
- Cerebras in this project means **Company Brain (Knowledge)** for production memory, not “we infer on Cerebras chips.” Demo does not call it.
- Machina Sports is not the model. `@EXM7777` articles are a library, not doctrine.

## Commit spine (implementation only)

See `git log --oneline a72b33c..HEAD` on this branch. Expected prefixes: `chore: scaffold`, `feat:` per box, `fix:` per review round.
