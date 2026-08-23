# AGENTS.md — Content Machine

You are on the **walkable demo**, not a greenfield design. Do not scaffold a second app.

**Before any product change, read in this order:**

1. `docs/agents/README.md` — map and read order
2. `docs/agents/invariants.md` — hard locks (fail the PR if you break one)
3. `docs/agents/system.md` — belt, data, API
4. `docs/agents/gotchas.md` — traps that already cost real time

Then open only the file that matches the task: `ui.md`, `boxes.md`, `runtime.md`, or `change-playbook.md`.

On-screen words: `docs/conventions/words-we-use.md`. If a reviewer cannot fail a PR from that file, you wrote a blog post.

## Who you talk to

CEO / product owner is not a developer. Explain what changed and why. Do not dump plumbing unless asked.

## Where the code is

This worktree: `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design`  
Branch: `feat/foolproof-design`

The git `main` checkout can still look like “design only.” That is stale. **This worktree is the product.**

## Do not

- Re-run `docs/superpowers/plans/2026-08-19-demo.md` as if the boxes are unbuilt
- Treat box specs as a file map (they lag). **Code + `invariants.md` win.** Then note the drift.
- Put brand marks or disclaimer text into Grok Imagine. Overlay is code.
- Paint images inside `POST /factory/run`. Picture is `POST /factory/image` after a person picks a caption.
- Publish to Instagram or any live channel
- Write secrets, `.env`, `.pptx`, or C: caches
- Use CrewAI. The belt is plain Python in `apps/api/boxes/belt.py`

## Commands

```text
cd apps\api
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

```text
cd apps\web
npm test
npx next dev --hostname 127.0.0.1 --port 3050
```

Walk: http://localhost:3050  
API: http://localhost:8000/health  

Stay on D:. Isolated work in `.worktrees/`.
