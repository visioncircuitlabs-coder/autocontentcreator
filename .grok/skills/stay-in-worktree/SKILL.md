---
name: stay-in-worktree
description: Use when starting product work, scaffolding an app, editing belt/UI/API, cwd is main, or the user says scaffold, new app, greenfield, or "build the demo".
---

# Stay in the worktree

The walkable product is **already built**. It is not on `main`.

```text
D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design
```

Branch: `feat/foolproof-design`.

## Do

- Open that folder before any product change.
- Read `docs/agents/WHERE-WE-ARE.md` then `docs/agents/invariants.md`.
- Change the existing FastAPI belt + Next walk.

## Do not

- Scaffold a second app on `main`.
- Re-run `docs/superpowers/plans/2026-08-19-demo.md` as a to-do.
- Treat `main` README “design artifacts” as “nothing is built.”

## Red flags

| Thought | Reality |
|---|---|
| "No apps/ here, I'll create one" | You are on `main`. Switch worktree. |
| "The plan file still has checkboxes" | Historical. Software is on the feat branch. |
| "Hermes cwd was main, so work here" | Hermes wrote into the worktree anyway. Follow the worktree. |

`main` is allowed for the architecture HTML and industry research only.
