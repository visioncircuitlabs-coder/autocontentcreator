# Agent handbook

This folder is the **operating manual for coding agents**. Humans should start at the repo `README.md` and `docs/runbooks/make-a-post.md`.

**Truth order when sources disagree**

1. `docs/agents/invariants.md` (locked product rules)
2. Live code under `apps/`
3. Tests under `apps/api/tests/` and `apps/web/desk/*.test.ts`
4. This handbook
5. `docs/decisions/` (why we built it this way)
6. `docs/superpowers/specs/` (box *intent* — may lag the file map)
7. `docs/superpowers/plans/` (historical. Demo plan is **done**. Do not re-implement it.)

## Read order

| If you need to… | Read |
|---|---|
| Not break the product | [invariants.md](invariants.md) |
| Know what exists | [system.md](system.md) |
| Map a box to files | [boxes.md](boxes.md) |
| Understand brand memory (md files that learn) | [memory.md](memory.md) |
| Change Look / Pick / Make / Preview | [ui.md](ui.md) |
| Run, env, Docker, worktrees | [runtime.md](runtime.md) |
| Avoid a known trap | [gotchas.md](gotchas.md) |
| Change a common thing | [change-playbook.md](change-playbook.md) |

Also load the repo skill: `.grok/skills/repo-context/SKILL.md`.

## What this product is

Unofficial Neutrogena **pilot** for Vision Circuit Labs (Kerala). A content person looks at today’s news, makes a caption, makes one picture, says yes or no with a reason, and downloads a **paused** ZIP. Nothing goes live.

Four layers, seventeen boxes:

```text
Trend Radar  →  Brand Brain  →  Content Factory  →  Command Center
  fetch           fixtures         belt + agents        five-step walk
  score           claims           hard rules           named yes/no
  1 deep dive     track record     Imagine + overlay    paused ZIP
```

Code moves work. Models sit **inside** steps. No CrewAI.

## Current walk (2026-08-22)

```text
1 Look     POST /radar/run          headlines + one closer look
2 Pick     (UI only)                person picks the idea
3 Make     POST /factory/run        2–3 captions, claims loop, NO photo
           then pick a version
           POST /factory/image      Grok Imagine 4:5 + wordmark/disclaimer
4 Your call POST /review/{id}       name + why required
5 Preview  GET  /export/{id}        paused ZIP
```

Live UI: http://localhost:3050 (`WalkApp`). Optional **How it is made** graph.

## Doc map (whole repo)

Human index: [../DOC-MAP.md](../DOC-MAP.md). API reference: [../reference-api.md](../reference-api.md).
