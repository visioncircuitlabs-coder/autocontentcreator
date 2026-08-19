# Box 2 — Relevance Scorer (hardened)

Status: ready for your yes / change. No app code. Source Fetcher is locked.

The bouncer. It reads a batch of signals and answers two cheap questions. It does not research, brief, or write.

## What goes in

| Input | From |
|---|---|
| Signal rows | Source Fetcher (same shape every time) |
| Brand-fit rubric | Human, versioned. Category, audience, “is this even our world?” |
| Inclusion / exclusion brief | Human, we **own** the text (Sprinklr AI Topics idea). Homonyms: Neutrogena vs a lookalike word, “bank” = bench, etc. |
| Brand-safety flags | Adverse-event words, crisis topics, competitor smear. A list, not a vibe. |

## What comes out

Every signal gets two numbers and a gate:

```text
signal_id
brand_fit        1–10   (fixed rubric, cheap model)
velocity         1–10   (will this still be loud tomorrow? — NewsWhip idea)
safety           ok | watch | kill
reason           one line, logged
gate             discard | background | deep_dive
model            via LiteLLM (usually Cerebras)
prompt_version
```

| Gate | Rule |
|---|---|
| **discard** | brand_fit &lt; 5, **or** safety = kill |
| **background** | 5–7, stored on the trend shelf, no researcher |
| **deep_dive** | brand_fit ≥ 8 **and** safety ≠ kill. Wakes the Deep-Dive Researcher. |

Velocity is **not** a green light to make a health claim. A fast-rising “GLP-1 cream” spike can score high on velocity and still be `watch` or `kill`.

## How it runs

```text
signals (batch ~50)
    │
    ├─ 1. homonym / exclusion brief     code + owned text
    ├─ 2. brand-fit 1–10                cheap model via LiteLLM → Cerebras
    ├─ 3. velocity 1–10                 from source metadata now;
    │                                   NewsWhip Spike later if we buy it
    └─ 4. safety list                   code first (kill words), then model watch
              │
              ▼
         discard | background | deep_dive
```

One call, fixed job, zero freedom. Schema-enforced JSON (Instructor). If the model returns garbage, the row is `watch` and a human sees it on the shelf — we do not invent an 8.

## Buy / wrap / build

| | |
|---|---|
| **Wrap** | Cerebras through LiteLLM for brand-fit. Never a direct Cerebras SDK. |
| **Build** | Rubric, inclusion/exclusion brief we can export, gates, logs. |
| **Buy later** | NewsWhip Spike if we need predicted 24h engagement. Not day one. |
| **Do not** | One embedding “is this relevant?” Exploding Topics % as a claims go-ahead. An agent that “decides what matters.” |

## Forbidden

- Letting velocity or “it’s trending” override a safety kill.
- Using the scorer to write angles or copy.
- Changing the rubric without a version bump (old scores must stay replayable).
- Hard-wiring Cerebras so we cannot swap the model.

## If a lawyer opens this box

They get: the rubric version, the exclusion brief, the two scores, the one-line reason, the model id, and why a row did or did not wake the researcher. A discarded adverse-event spike is a feature, not a miss.

## Hands off to

- **discard** → stop.
- **background** → Trend Reports shelf, decaying.
- **deep_dive** → Deep-Dive Researcher, one signal, capped.

## Done when you say

This box is locked. Next is **Deep-Dive Researcher**.
