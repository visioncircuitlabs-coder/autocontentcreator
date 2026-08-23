# 023 — Agent handbook + doc refresh

**Status:** filled  
**When:** 2026-08-22  
**Where:** this worktree, `feat/foolproof-design`

## What the user would see

A coding agent that opens this repo can find one start file and the hard locks, instead of a design-stage README fighting a walkable demo. A person still starts at the runbook and the architecture HTML.

## The problem

Docs disagreed with the product:

- Specs said “not built.” The walk was live.
- README still described stub images and Fetch-first chrome.
- Agents re-read the demo plan as a to-do and could scaffold a second app.
- Session traps (junk URLs, paint-on-Make, Imagine vs stub env, 300s proxy) lived in chat, not in a file.

## Decision

Separate **agent** docs under `docs/agents/` plus `AGENTS.md`. Update human entry points (README, CLAUDE.md, runbooks, API reference, how-to run). Do not regenerate the 17 box specs. Add one-line status banners where those files still claim “no app.”

## Why this shape

- Agents need invariants, a file map, and gotchas. Employees need five steps and short words.
- Specs stay the lock on *intent*. A live map in `docs/agents/boxes.md` records drift instead of rewriting August 19 history.
- Diataxis: tutorial = make-a-post; how-to = run the demo; reference = API + boxes; explanation = invariants + decisions.

## What we refused

- A wiki of one file per function
- Replacing `show-me-architecture.html`
- Auto-committing secrets or pasting live keys into examples

## Verification

Files exist under `docs/agents/`, `docs/DOC-MAP.md`, `docs/reference-api.md`, `docs/howto-run-the-demo.md`. Cross-links from README and CLAUDE.md. Claims in the handbook were read from `main.py`, `belt.py`, `WalkApp.tsx`, `.env.example`.

## Deferred

Ox Alpha review report if/when `docs/reviews/2026-08-22-ox-alpha-review.md` lands. Production plan docs stay parked.
