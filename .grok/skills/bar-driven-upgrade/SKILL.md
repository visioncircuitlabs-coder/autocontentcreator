---
name: bar-driven-upgrade
description: Use when the user says make it better, raise the bar, enterprise, iterate, world-class, SOTA, or close a gap from docs/bar.
---

# Bar-driven upgrade

Do not invent a new research pile. The bars exist.

1. Read `docs/agents/WHERE-WE-ARE.md` and `docs/bar/STATUS.md`.
2. Pick **one** `[MISSING]` (or a named user request).
3. Write the failing test in `apps/api/tests/` (or the matching web test).
4. Smallest code change. User-facing words through `desk/words.ts`.
5. Tick the row in `STATUS.md`. One-line note in `WHERE-WE-ARE.md` if the stage moved.

## Order unless the founder overrides

1. Propose-rule UI for `get_lesson_suggestions()`
2. Judge calibration from named yes/no
3. Engagement read-back (still no live publish)
4. Postgres / SSO only with a decision note

## Do not

- Re-research ASCI/FTC/copy craft. Edit `docs/bar/*` only when a source changed or a row shipped.
- Close a gap by adding CrewAI, auto-publish, or logo-in-Imagine.
- Land a bar item that is not shown, logged, or tested.
