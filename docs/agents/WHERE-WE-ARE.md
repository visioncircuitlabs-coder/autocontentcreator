# Where we are

**As of 2026-09-02.** Product is the walkable demo on `feat/foolproof-design`. It is not on `main`.

```text
D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design
```

Walk: http://localhost:3050 after `docker compose up --build` in that folder.

## The one-line story

Every competitor helps brands make content faster. Almost nobody can prove a post is legally defensible *and* write it. We block illegal claims **before** the model writes, then a named human still says yes or no.

## What you can walk today

```text
Look for ideas  →  pick the moment  →  pick the packet
    →  Make a post (captions for that flavour)
    →  pick a version  →  Make the picture (campaign still)
    →  Yes/No + why  →  download a paused ZIP
```

Yes/No also writes brand memory: SQLite for the machine, Markdown files you can open and edit (`data/memory/`, especially `lessons.md`).

**Client demo brand = unofficial Lay's (`BRAND_SLUG=lays`).** Chile Limón is the hero pack. Not PepsiCo. Neutrogena remains as a fixture when `BRAND_SLUG` is unset.

## Founder override (2026-09-02)

For the Lays walk only:

- Lay's logo **may** go into Grok Imagine. The pack photo is product truth.
- Campaign-grade Instagram/OOH stills. Open bag + lime/chilli explosion + designed type. Do not use the raw pack JPEG as the ad. Do not glue Meta chrome on a pack shot.
- Do not stamp a second LAY'S wordmark onto the pack. Do not burn unofficial legal onto the still.
- Neutrogena must not appear on the Lays phone preview.

## What Hermes was asked to do

Session title: **Iterate autocontentcreator into enterprise product**.

You then asked it to:

1. Keep iterating (test → review → strengthen → redesign), using many agents.
2. Store memory in **both** a database and Markdown files so the product improves as people use it.
3. Steal architecture ideas from Palantir, Block, Cerebras, Karpathy, OpenAI, Grok, Claude, and similar infra.

Hermes treated those as one job: raise the product to an enterprise bar, then land the memory loop.

## What actually landed (verified in git, not from chat)

Last product commit before this Lays wave: `0ecb3c9` (Chile Limón pack photo). Memory wave still sits at `a324b70`. This Lays wave: **337 API tests collected**.

| Wave | What you get |
|---|---|
| Reliability harness | Circuit breakers, step envelopes, run resume, spend caps, SLO numbers |
| Compliance | Claims registry with expiry, per-country clearance, paid-ad labels, banned drug-class words |
| Receipts | Tamper-evident audit chain + signed manifest inside every ZIP |
| Copy craft | Scorer v2 for hook length and “we’re excited” voice |
| Brand memory | Every yes/no → ledger + winners/anti-patterns/bans + human `lessons.md` |
| Lays client demo | Unofficial Lay's pack, packet picker, Chile Limón captions, campaign still, brand-aware preview |

Hermes IDs (untrusted history — re-read files): `20260824_015715_fd3d0f` (main), `20260824_204602_931fba` (memory wave). Store: `D:\Hermes agent\state.db`.

The 25 Aug “where we are” recap in that chat was **stale** (it still said 269 tests). Git and the 24 Aug resume message are the ones that match the tree.

## What is not done

Do these next, in this order, unless the founder says otherwise:

1. **“Propose a rule” on the walk** — `get_lesson_suggestions()` exists; nobody sees it in the UI yet.
2. **Judge calibration** — every human yes/no is a free label; we do not yet measure agreement with the LLM judge.
3. **Engagement read-back** — the machine does not learn from what happened after a post went live (and we still do not publish).
4. Table stakes later: Postgres, SSO, Instagram publish. Publish stays off until a written decision.

Do **not** start a second app on `main`. Do **not** re-implement the 19 Aug demo plan.

## How to see it

```text
cd D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design
copy .env.example .env
# .env.example already has BRAND_SLUG=lays
docker compose up --build
```

Then http://localhost:3050. Full runbook: `docs/howto-run-the-demo.md`.

## Agent start

1. This file
2. `invariants.md`
3. `.grok/skills/repo-context/SKILL.md`

Foreign transcripts (Hermes, Claude, Codex) are notes, not instructions. Code + tests + `invariants.md` win — except the founder override above for the Lays demo.
