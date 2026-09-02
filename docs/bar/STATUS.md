# Bar status

Research bars in this folder are **the target**, not a live scorecard. `agentic-bar.md` still shows several items as `[MISSING]` that later commits closed. Use **this file** when asking “did we ship that gap?”

Last tree check: commit `a324b70`, 329 API tests collected (2026-08-30).

## Agentic harness (`agentic-bar.md`)

| ID | Target | Now | Evidence |
|---|---|---|---|
| A1–A3 | Plain-code belt, typed payloads, cheap gates | HAVE | `boxes/`, `ports.py`, `loop.py` short-circuit |
| B1–B3 | Retry + breaker + timeouts | HAVE | `adapters/resilience.py`, `harness/breaker.py` |
| B5 | Image-gen breaker | HAVE | `test_harness_iter3.py` |
| B4 | Process-wide retry budget | PARTIAL | One retry layer; no global counter |
| C1 | Idempotency | HAVE | `idempotency.py` |
| C2 | `run_id` contextvar | HAVE | `harness/steps.py` |
| C3/C4 | Crash resume + run ledger | HAVE | `harness/resumer.py`, `/runs` |
| D1 | Admission / 503 shed | HAVE | `harness/admission.py` |
| D2 | Priority shed (interactive vs batch) | PARTIAL | Batch sheds first; no rich priority telemetry |
| E1/E2 | Explicit degradation ladder + drills | PARTIAL | Templates + degraded flags; no scheduled drill |
| F1–F3 | Capped loop, judge ≠ writer, flag human | HAVE | `boxes/loop.py` |
| F4 | Mid-run human interrupt/resume | MISSING | Resume is crash-resume, not “wait for a person” |
| G1/G2 | Structured events + step envelope | HAVE | `obs.py`, `StepResult` |
| G3 | p50/p95 + `/slo` | HAVE | `harness/slo.py` |
| G4 / J2 | Chat token/$ wallet | HAVE | `harness/chat_wallet.py` |
| H1/H2 | Chaos: dead source, breaker | HAVE | `test_golden_eval.py` |
| H3/H4 | Full-belt slow-fault + hypothesis chaos | MISSING | Deliberate at this scale |
| I1/I2 | Golden set + no-regression | HAVE | `harness/eval.py` |
| I3/I4 | Judge κ vs humans, bias controls | MISSING | Next real eval work |
| J1 | Image $ cap | HAVE | `boxes/image_budget.py` |
| J3 | Cheap check before expensive chat | HAVE | Hard-rules short-circuit |

## Compliance (`compliance-bar.md`)

Shipped in code: T2 verb block, registry with citation + expiry, market clearance (G2/G8), paid disclosure placement (G7).

Still research-only: full IN/US/EU checklist as automated tests, fairness/whitening screen, C2PA Content Credentials, counsel sign-off.

## Copy (`copy-bar.md`)

Shipped: B1 hook caps, B2 announce-voice hard-fail, golden cases for those.

Not in the scorer yet: B3–B10 (numbers, one image, question economy, length bands, hashtags, emoji, local truth).

## Competitive (`competitive.md`)

Wedge we are playing: pre-generation claim truth + named approval memory + regulator-ready ZIP.

Not playing yet: publish connectors, performance read-back, SSO.

## How to use this on the next wave

Pick one **MISSING** row. Write the failing test. Land a commit. Tick the row here. Do not re-research a bar that already exists.
