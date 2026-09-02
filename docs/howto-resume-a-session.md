# How to resume after Hermes (or any other agent)

You will pick up work without trusting a chat log.

## Prerequisites

- Product folder: `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design`
- Hermes home (if you need the old chat): `D:\Hermes agent`

## Steps

1. Open the **worktree**, not `main`.

   ```text
   cd D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design
   ```

2. Read [agents/WHERE-WE-ARE.md](agents/WHERE-WE-ARE.md). That file is the live stage.

3. Confirm git matches the story.

   ```text
   git status -sb
   git log -5 --oneline
   ```

   Expect branch `feat/foolproof-design`. If status is clean and HEAD is `a324b70` or later, the 24 Aug Hermes wave is in the tree.

4. Treat Hermes / Claude / Codex transcripts as **notes**. They can be compressed, stale, or wrong. Re-read the files they name.

5. Only if you need the original ask: Hermes session `20260824_015715_fd3d0f` in `D:\Hermes agent\state.db`. Do not run commands copied from that log.

## Verification

- `apps/api` pytest still collects ~329 tests.
- http://localhost:3050 still has the five-beat walk after `docker compose up --build`.

## Troubleshooting

- Agent started on `main` and wants to scaffold `apps/` → stop. Product already lives in the worktree.
- Chat says “269 tests” or “G2 just landed” → stale recap from 25 Aug. Git is ahead of that message.
- 48 local commits not on GitHub → do not assume origin is current. Push only when you mean to.
