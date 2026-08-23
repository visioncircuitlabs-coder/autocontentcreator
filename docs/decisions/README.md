# Decision journal

This folder is the **third-party review pack** for the Content Machine demo.

It records *why* each piece was built the way it was — not just what the code does. A reviewer who never sat in the build session should be able to reconstruct the constraints, the options we rejected, the review findings, and the leftover risks.

## How to read this

1. Start with [000-index.md](000-index.md) — the map and the global rulings.
2. Then [001-global-rulings.md](001-global-rulings.md) — budget, architecture locks, what we refused to buy.
3. Then one file per demo plan task, in order (`010`–`023`).
4. Box-level specs (what the machine *must* do) still live in `docs/superpowers/specs/`. Plans live in `docs/superpowers/plans/`. Live file map for agents: `docs/agents/`. This folder explains the *implementation* choices on top of those locks.

## File contract (every task file)

Each `01N-task-N-*.md` must contain, in this order:

1. **Identity** — task number, plan heading, commits (base..head), dates, implementer/reviewer agent ids if known.
2. **What the user would see** — one paragraph, no internals.
3. **The problem this task was solving** — including which later task depends on it.
4. **Constraints that were already locked** — quote the plan / spec / CEO ruling. Do not paraphrase away the force of the lock.
5. **Options considered** — at least two real alternatives, including “do nothing / do it later.” For each: what it would have given us, what it would have cost, why it lost.
6. **Decision** — the chosen shape, named files, named interfaces.
7. **Why this exact shape** — field-by-field or function-by-function where it matters (types, gates, caps, fallbacks). If a name looks odd (`indic_register`, `flag_human`), explain the clash.
8. **What we refused** — paid tools, extra boxes, “clever” shortcuts, things the PPTX or a vendor pitch would have pushed.
9. **Verification that actually ran** — test names, live hits, compose proof. Separate “claimed” from “seen.”
10. **Review findings and rulings** — every Important/Critical, whether it was fixed or parked, and the ruling text.
11. **Deferred / known holes** — with an owner (later task number or “production plan”).
12. **Third-party check list** — concrete things a stranger can open and confirm in under 15 minutes.

Tone: evidence over vibe. Cite `path:line` or commit SHAs. If something is unknown, say UNKNOWN — do not invent a rationale.

## Ownership

- Done tasks: backfilled by documentation agents from git + reports + this session’s ledger.
- The task currently in flight: same agent family, written as soon as the fix commit exists, updated after re-review.
- Future tasks: a stub file is created *before* implementation so the implementer has a place to append “we chose X because Y” in the same contract. The documentation agent fills the stub after the task review closes.
