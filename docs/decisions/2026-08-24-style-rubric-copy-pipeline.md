# Decision — Style Rubric Wired Into the Copy Pipeline

**Date:** 2026-08-24
**Status:** Accepted
**Scope:** `boxes/rubric.py` (new), `boxes/strategist.py`, `boxes/copywriter.py`, `boxes/craft.py`, `boxes/judge.py`, `boxes/loop.py`

## Context

`docs/style/rubric.md` codifies an agency-grade voice standard (Nike / Apple / Aesop /
Glossier patterns + scored dimensions D1–D7 with 1–5 anchors), but none of it was
wired into the generator pipeline. Captions came out as three near-identical
compliance-safe posts, and craft review was a binary PASS/FAIL with no rubric signal.

## Decision

1. **Single source in code — `boxes/rubric.py`.** The rubric's prompt-ready blocks
   (`RUBRIC_VOICE`, `MODE_PROMPT_BLOCK`) plus deterministic helpers live in one module.
   No LLM calls inside it; hard rules stay untouched and LLM-free.

2. **Strategist.** Angle templates now carry rubric voice rules and three concrete
   exemplar patterns (Nike imperative compression, Apple poetry-line + proof-line,
   Glossier peer voice). The chat payload wraps them in `<rubric>` as DATA.

3. **Copywriter — mode-diverse variants.** The system prompt requires each of the
   2–3 caption variants to be written in a DIFFERENT rubric mode:
   `imperative-compression` / `peer-voice-intimate` / `describe-dont-promise`.
   The template fallback was rewritten so each template embodies one mode instead of
   three near-clones. Cliché phrasing is banned in-prompt; enforcement is downstream.

4. **Craft pass — deterministic first.** `review_craft` scores every caption on five
   dimensions (hook strength, rhythm/economy, specificity, emotional truth, brand fit)
   via `rubric.score_dimensions` before any model call, and **fails outright on the
   cliché blacklist** ("glow like never before", "unleash your", "game-changer",
   "elevate your skincare", "revolutionary", etc.). The optional chat pass only adds
   human-fixable reasons on top.

5. **Judge — dimension-scored style verdict.** `run_judge` now returns a `StyleScore`
   (`dimensions: {D1..D5}: 1–5`, `average`, `verdict: PASS|REWRITE`, `one_line_fix` =
   single highest-leverage rewrite instruction). Compliance verdict semantics are
   unchanged: style never blocks go-live by itself; when compliance passes but style
   says REWRITE, the fix surfaces as an advisory note that the loop threads to the
   rewriter. Craft dimensions are recorded in the draft judge payload
   (`craft_dimensions`) for observability.

## Invariants preserved

- Writer ≠ judge: style scoring is deterministic code shared by craft/judge; no new
  LLM schema calls were added to the judge/craft path.
- Max 3 rewrite rounds → `flag_human` unchanged.
- Hard rules untouched; benefit claims still 100% human-approved (registry flow intact).
- Pass bar mirrors rubric §3 intent: avg ≥ 3.8 and no dimension below 3.

## Consequences

- Variant diversity is structural (one mode per variant), not left to sampling luck.
- Clichés are caught deterministically even with `chat=None` / offline runs.
- Dimension scores give the rewrite loop a targeted instruction instead of "make it
  better", and make quality trends visible in stored drafts.
