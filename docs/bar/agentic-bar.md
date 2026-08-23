# Agentic Harness Bar

**What this is:** the reliability bar for Content Machine's pipeline harness, distilled from
Anthropic/OpenAI agent-engineering guidance, framework lessons-learned (LangGraph, Google ADK,
AutoGen), and classic SRE practice (Google SRE ch. 22, Netflix Hystrix, AWS Well-Architected).
Every checklist item is phrased so it can be **tested** (unit test, CI gate, or inspection), and
graded against the current `apps/api` harness as of this worktree.

**Grades:** `[HAVE]` = implemented and evidenced · `[PARTIAL]` = exists but incomplete/unproven ·
`[MISSING]` = gap against the bar.

---

## Sources distilled

| Source | What we took from it |
|---|---|
| Anthropic, *Building effective agents* | workflows vs agents; simplest-thing-first; programmatic gates between chained calls; evaluator-optimizer with iteration caps; stop conditions; ACI/tool poka-yoke; avoid framework abstraction that hides prompts |
| Anthropic, *Claude Code best practices* | give the agent a verification signal it can self-correct against; evidence over assertion; clean revertible steps |
| OpenAI, *A practical guide to building agents* | guardrails layered input→tool→output; human intervention triggers (failure thresholds, high-risk actions); eval-baseline-then-downsize model choice |
| LangGraph persistence/HITL docs | durable checkpoints keyed by run/thread id; interrupt/resume as a control-flow primitive; resume re-executes the node → side effects must be idempotent |
| Google ADK workflow agents | Sequential/Parallel/Loop primitives; shared typed state with unique output keys; LoopAgent `max_iterations` + early-exit quality gate |
| AutoGen v0.4 redesign + migration notes | async/event-driven boundaries; typed handoffs not free text; "treat each agent as an unreliable service"; timeouts everywhere; shadow/golden eval loops |
| Google SRE ch. 22 (*Addressing Cascading Failures*) | randomized exponential backoff + jitter; limit retries per request AND server-wide retry budget; don't stack retries across layers; distinguish retriable vs permanent errors; load shedding; graceful degradation — and regularly exercise the degraded path |
| Netflix Hystrix | CLOSED/OPEN/HALF_OPEN breaker with sleep-window probe; bulkheads per dependency; fail fast instead of queueing; fallbacks must not themselves do network calls or fail |
| AWS Well-Architected Reliability (REL12-BP04 et al.) | chaos engineering = hypothesize → inject fault → compare to steady state; graceful degradation + emergency levers as named best practices |
| LLM-as-judge literature (agreement/bias studies) | calibrate judges against human-labeled gold sets (Cohen's κ / Krippendorff's α); known biases: position, verbosity, self-preference; recalibrate after rubric/model changes |

---

## 1. Consensus patterns worth copying

These recur across ≥2 independent sources and are considered settled best practice:

1. **Typed step envelope at every node.** Every pipeline unit returns a uniform record —
   status, duration, attempts, error, correlation id — so observability and recovery are
   uniform instead of ad hoc. (LangGraph state; ADK `output_key`; our `StepResult`.)
2. **Plain code over frameworks until proven necessary.** Anthropic's #1 finding: successful
   teams use composable patterns in ordinary code; framework abstraction hides prompts and
   makes debugging harder. Frameworks are opt-in complexity.
3. **Programmatic gates between LLM calls (prompt chaining with checks).** Insert cheap,
   deterministic validation between steps; abort/repair early instead of feeding garbage
   downstream. Gates also *save money* by skipping later expensive calls.
4. **Budgeted, capped loops.** Every loop — tool-use, rewrite, retry — carries a hard
   iteration/step/token ceiling plus an explicit exit signal. Agents without stopping
   conditions are the canonical runaway-cost bug.
5. **Evaluator–optimizer loop with distinct identities and a cap.** Generator ≠ judge;
   loop until quality gate passes **or** the cap hits; then escalate rather than ship blind.
   Only justified where measurable improvement exists.
6. **Human-in-the-loop gates with defined triggers.** Two standard triggers: (a) failure
   threshold exceeded, (b) high-stakes/irreversible action. Escalation must be a *designed
   state*, not an exception.
7. **Fault containment per dependency: timeout → retry → breaker → fallback.**
   Classified retries (transient-only, jittered exponential backoff, bounded count);
   circuit breaker with half-open probe; fallback that cannot itself fail; fail fast
   instead of queueing.
8. **Graceful degradation ladders.** Pre-decided reduced-quality paths (cheaper model →
   cached/template result → skip-and-flag). SRE warns: the degraded path you never exercise
   is the one that won't work — drill it.
9. **Durable execution.** Persist state at step boundaries keyed by a stable run id so a
   crashed run resumes from the last completed step, and any run can be replayed/audited
   from its event log.
10. **Eval-driven development.** Golden sets run in CI with a numeric bar; baseline capture +
    regression gates; model downgrades validated against the same set; judges calibrated
    against human labels before being trusted as ground truth.
11. **Learning loop.** Production failures and human flags flow back into the golden set /
    rubric, so the system's checks improve from incidents (Claude Code "evidence", SRE
    postmortem culture).

## 2. Anti-patterns to avoid

1. **Multi-agent sprawl.** Spawning agent crews for tasks a chain handles. Multi-agent
   systems cost ~10–15× the tokens, multiply failure modes, and are far harder to audit.
   Default to sequential code; add autonomy only when measured to pay.
2. **Unbounded / stacked retries.** Retrying forever, or 3 retries at each of 3 layers =
   up to 64 attempts against a dying backend — the textbook cascade amplifier. Also:
   retrying non-retriable errors (4xx, malformed payloads) which can never succeed.
3. **Implicit / ambient state.** Globals, hidden mutable context, free-text handoffs
   between stages. Untestable, unreplayable, race-prone. State crosses boundaries only
   inside typed payloads with explicit keys.
4. **Queueing instead of shedding.** Unbounded in-flight work converts overload into
   latency collapse and memory exhaustion (SRE: reject early, fail cheap).
5. **Fallbacks that can fail.** A fallback containing network calls re-creates the outage
   it was meant to paper over (Hystrix: fallback = static/cache logic only).
6. **Judge-as-ground-truth without calibration.** LLM judges drift with position,
   verbosity, and self-preference bias; uncalibrated scores silently rot the bar they
   enforce.
7. **The untested degraded path.** Code paths only reachable during outages get written
   once and never run until the outage — when they don't work.
8. **Observability by println.** Unstructured logs can't answer "what did run X do, what
   did it cost, where did it stall." Every step emits structured, scrubbable events.

---

## 3. HARNESS BAR checklist — graded against current implementation

Evidence key: files cited under `apps/api/`. Graded by direct code inspection this worktree.

### A. Architecture & boundaries

| # | Requirement (testable form) | Grade | Justification |
|---|---|---|---|
| A1 | Orchestration is plain code — no agent framework import anywhere in `apps/api` | **[HAVE]** | `harness/`, `boxes/`, `adapters/` are ordinary modules; ports are `Protocol`s (`ports.py`) — zero CrewAI/LangGraph deps |
| A2 | Every cross-boundary payload is a typed pydantic model; LLM outputs parsed via `schema.model_validate_json`, never raw strings passed between steps | **[HAVE]** | `ports.ChatModel.complete_json(system, user, schema)`; boxes exchange `Draft`/`Claim`/verdict models |
| A3 | Cheap deterministic gates run *before* LLM calls in each round | **[HAVE]** | `boxes/loop.py`: `run_hard_rules()` short-circuits judge+craft on rule failure (saves 2 chat calls/round) |

### B. Fault containment (timeout → retry → breaker → fallback)

| # | Requirement | Grade | Justification |
|---|---|---|---|
| B1 | Retries are bounded (≤N), transient-only classified (never 4xx/permanent), exponential backoff **with jitter** | **[HAVE]** | `adapters/resilience.py`: `MAX_RETRIES=2`, `is_transient()` whitelists timeouts/connection/5xx only, backoff doubles + `random.uniform` jitter |
| B2 | Circuit breaker on the LLM dependency: OPEN on N consecutive failures, HALF_OPEN single-probe after cooldown, escalating cooldown with cap; fail-fast error carrying `retry_after` | **[HAVE]** | `harness/breaker.py`: threshold=3, 60 s cooldown doubling to 600 s cap, `BreakerOpen(retry_after_s)`; guards all chat via `CHAT_BREAKER` (`chat_litellm.py:57`) |
| B3 | Every outbound call has an explicit timeout shorter than the caller's patience | **[HAVE]** | `litellm.completion(timeout=20)` in `chat_litellm.py`; breaker prevents queued pile-up behind dead upstream |
| B4 | No retry amplification: exactly one retrying layer per dependency path; a process-wide retry budget counters attempts | **[PARTIAL]** | Adapter is the only retry layer today (loop rounds are separate concerns), but no aggregate retry-budget counter/metric exists if a second retrying layer appears |
| B5 | Each external dependency isolated (bulkhead): failure in one cannot consume the others; fan-out tolerates dead members | **[PARTIAL]** | Fetcher isolates dead trend sources (chaos-tested, `test_golden_eval.py::test_chaos_one_dead_source…`); but only chat has a breaker — `ImageGen` and future deps have none |
| B6 | Fallback logic makes no network calls and cannot itself throw into the caller | **[HAVE]** | `build_chat()` returns `None` when no API keys → callers use templates (`chat_litellm.py` docstring); template path is local-only |

### C. State, resumability, replay

| # | Requirement | Grade | Justification |
|---|---|---|---|
| C1 | Duplicate submissions deduplicated by client-supplied idempotency key with TTL; cached response replayed | **[HAVE]** | `idempotency.py`: `(key, endpoint)` PK, 10-min freshness window, replays stored success responses |
| C2 | One correlation id threads through every event of a run (queryable in log + DB) | **[PARTIAL]** | `run_id` emitted on `harness_step` events, but held in a module-level global (`steps.py:set_run_id`) — best-effort, not a contextvar; unsafe under concurrent runs |
| C3 | Crash-resume: completed steps persisted so a killed run restarts from the last checkpoint, not step 0 | **[MISSING]** | No checkpoint store; a crash mid-run loses all prior step work (idempotency only dedupes whole-request resubmission within TTL) |
| C4 | Deterministic replay: any historical run reconstructible step-by-step from its event log (inputs, outputs, versions recorded) | **[MISSING]** | Events carry status/timing/errors but not full step inputs/outputs or prompt/model versions — enough to audit *that* it ran, not to reproduce *what* it produced |

### D. Backpressure & load control

| # | Requirement | Grade | Justification |
|---|---|---|---|
| D1 | Concurrency is capped (semaphore/queue bound); excess requests shed fast with an explicit overload signal, never silently queued to infinity | **[MISSING]** | No admission control, in-flight cap, or 503-with-retry-after path; only the breaker bounds *upstream* pressure, not *our own* load |
| D2 | Shedding/degradation policy is priority-aware (e.g., interactive > batch) and observable when active | **[MISSING]** | No notion of request priority or shed-event telemetry |

### E. Graceful degradation ladders

| # | Requirement | Grade | Justification |
|---|---|---|---|
| E1 | Each dependency has a written, ordered ladder: full → cheaper-model → cache/template → skip-and-flag, chosen automatically on trip signals | **[PARTIAL]** | Chat has rung 1↔3 implicitly (key present? → model; else templates), but the ladder isn't per-step explicit, and there's no automatic downgrade on breaker trips — open breaker surfaces as error |
| E2 | Degraded modes are exercised regularly (tests/drill), monitored, and have kill switches — SRE: "the code path you never use doesn't work" | **[PARTIAL]** | Template/no-key path covered by offline tests; no scheduled degraded-mode drill, no alert when a run completes degraded, no runtime toggle |

### F. Loops & human-in-the-loop

| # | Requirement | Grade | Justification |
|---|---|---|---|
| F1 | Improvement loop has a hard round cap enforced in code, not convention | **[HAVE]** | `boxes/loop.py::run_loop(max_rounds=3)` — round counter incremented every rewrite; return guaranteed at cap |
| F2 | Judge ≠ writer (separate evaluation identity/prompts; multiple evaluators AND-ed) | **[HAVE]** | `run_judge` (claims) + `review_craft` (style) both must PASS; rewrite goes to copywriter with numbered reasons |
| F3 | On cap exhaustion the artifact is *flagged for human review*, never silently shipped | **[HAVE]** | `flag_human=True` set on cap exit (both rule-fail and judge-fail branches); surfaced in draft payload |
| F4 | Mid-run pause/resume primitive (human approval blocks durably; run resumes with state intact, side effects idempotent on re-entry) | **[MISSING]** | `flag_human` is terminal routing, not a durable interrupt; no mechanism to pause a live run awaiting approval and resume it (LangGraph-style `interrupt` equivalent) |

### G. Observability

| # | Requirement | Grade | Justification |
|---|---|---|---|
| G1 | Structured events dual-written (append-only JSONL + queryable table), secrets scrubbed | **[HAVE]** | `obs.py emit()`: JSONL line + `insert_event` row, `scrub()` redacts secret-named keys and API-key patterns |
| G2 | Uniform per-step envelope: name, ok, ms, attempts, error, started_at — emitted automatically | **[HAVE]** | `StepResult` + `step()` wrapper; never raises, records everything, tags `run_id` |
| G3 | Latency/error rollups per step: p50/p95 computed from events, alerting on drift (e.g., p95 > 2× baseline) | **[MISSING]** | Raw `ms` is logged per step but nothing aggregates percentiles or alarms; no dashboard/query for step-latency SLOs |
| G4 | Run-level cost visibility (tokens/$ per run, per step) alongside latency | **[MISSING]** | No token accounting on chat calls; only image spend is tracked (see J1) |

### H. Chaos-testability

| # | Requirement | Grade | Justification |
|---|---|---|---|
| H1 | Fault-injection tests prove a dead component degrades neighbors' service, not kills it | **[HAVE]** | `test_golden_eval.py::test_chaos_one_dead_source_does_not_kill_fetch` — dead `TrendSource` logged, alive honored |
| H2 | Breaker dynamics deterministically testable (injectable clock/sleep; fail-fast verified to stop invoking fn) | **[HAVE]** | `CircuitBreaker(clock=, sleep=)`; `test_chaos_breaker_stops_repeated_dead_upstream_calls` asserts fn not called while open; dedicated `test_breaker.py`, `test_resilience.py` |
| H3 | Whole-pipeline fault drills: critical path proven independent of noncritical deps (incl. blackhole/slow, not just raise-fast) | **[PARTIAL]** | Component-level chaos exists; no end-to-end drill injecting slow/blackholing (vs raising) faults through the full radar→factory→paint belt |
| H4 | Hypothesis-form chaos experiments: steady-state defined, fault injected in staging, hypothesis compared to observed (AWS REL12-BP04) | **[MISSING]** | Tests assert containment post-hoc; no steady-state hypothesis/experiment protocol (acceptable at this scale — document as deliberate deferral) |

### I. Eval harnesses

| # | Requirement | Grade | Justification |
|---|---|---|---|
| I1 | Golden set runs in CI with a numeric pass bar; includes negative cases (weak inputs *must* fail) | **[HAVE]** | `harness/eval.py` + `test_golden_eval.py`: strong cases must clear bars, weak cases must get REWRITE, overall `rate >= 0.9`; fully offline/deterministic |
| I2 | Baseline capture + regression gate (score may never drop vs saved baseline) | **[HAVE]** | `save_baseline` / `vs_baseline`; test asserts `delta >= 0` — "deterministic scorer must never regress" |
| I3 | LLM judges calibrated against human-labeled gold items with an agreement metric (κ ≥ agreed floor), recalibrated on rubric/model change | **[MISSING]** | Judge/craft verdicts are consumed raw; no human-labeled holdout, no agreement measurement, no recalibration trigger |
| I4 | Judge bias controls: order randomization for pairwise judging, position/verbosity probes, refusal-handling pinned in rubric | **[MISSING]** | Single-output rubric judging only; no pairwise mode yet — when added, these controls come with it (cheap to spec now) |

### J. Cost budgets

| # | Requirement | Grade | Justification |
|---|---|---|---|
| J1 | Hard $ cap on image generation, persisted across processes, blocking over-cap calls | **[HAVE]** | `boxes/image_budget.py`: default `$2.00`, `record_spend` persists (SQLite), gate refuses over cap; tested incl. bad-env fallback |
| J2 | Per-run token/$ budget on chat with pre-call enforcement (estimate before call, refuse/halt over budget, emit budget events) | **[MISSING]** | No token counting or run wallet for chat; a pathological loop could spend unbounded until its round cap (rounds bound *iterations*, not $) |
| J3 | Cost-aware ordering: cheapest sufficient check first; expensive ensemble calls skipped when a deterministic check already fails | **[HAVE]** | `loop.py` hard-rules short-circuit skips judge+craft (2 chat calls/round saved) — the exact "gate before generate" economics both vendor guides prescribe |

### Scorecard

| Area | HAVE | PARTIAL | MISSING |
|---|---|---|---|
| A Architecture (3) | 3 | 0 | 0 |
| B Fault containment (6) | 5 | 1 | 0 |
| C State/resume/replay (4) | 1 | 1 | 2 |
| D Backpressure (2) | 0 | 0 | 2 |
| E Degradation ladders (2) | 0 | 2 | 0 |
| F Loops/HITL (4) | 3 | 0 | 1 |
| G Observability (4) | 2 | 0 | 2 |
| H Chaos (4) | 2 | 1 | 1 |
| I Evals (4) | 2 | 0 | 2 |
| J Cost (3) | 2 | 0 | 1 |
| **Total (36)** | **20** | **5** | **11** |

### Highest-leverage gaps (ordered)

1. **G3 — per-step p50/p95 rollups + drift alarm.** The data already lands in the events
   table; this is a query + threshold, not new instrumentation. Cheapest path to "the
   harness tells you it's sick before users do."
2. **J2 — chat $ budget mirroring the image wallet.** Pattern already exists in
   `image_budget.py`; replicate with a token estimator and a per-run ledger.
3. **C2+C4 — make `run_id` a contextvar and record step I/O hashes + model/prompt versions
   in events.** Turns the existing log into a replay/audit trail and fixes the concurrency
   hazard in one move.
4. **B4/B5 — generalize the breaker into a per-dependency registry** (image gen next) and add
   a process-wide retry-attempt counter; both are small diffs to existing primitives.
5. **C3/F4 — decide deliberately whether durable resume is in scope.** If runs stay
   < minutes and idempotent to resubmit, document the deferral; if not, adopt a
   checkpoint-per-step keyed by `run_id` (the event table is already halfway there).
6. **I3 — start collecting human-labeled judge holdout now** (every `flag_human` resolution
   is a free label); calibration needs ~30–50 items before it means anything.

*Deferral rationale for D1/D2/H4:* single-process, low-QPS internal tool — formal admission
control and hypothesis-form chaos experiments are disproportionate today; revisit if the API
becomes multi-tenant or concurrent.
