# Content Machine — Production plan (parked)

**Status:** Saved for later. Do not implement until there is budget to buy vendors and run a real pilot.

**Goal:** The same 17-box machine as the demo, with licensed sources, a real Brand Brain, frontier voice, and audit that survives a Kenvue legal review.

This file is the swap map. The demo already uses the box names and ports. Production replaces adapters and raises the bar. It does not invent a new architecture.

## When to open this file

- Demo walked in a room and someone asked “what do we buy?”
- There is money for Brandwatch *or* Meltwater, a claims calibration set, and LiteLLM + a frontier model
- You are ready to host Postgres + Langfuse, not SQLite

Until then, keep building on the demo ports.

## Same structure

Radar → Brand Brain → Factory → Command Center. Humans approve benefit claims. No autonomous publish. Plain-code belt. Dual-LLM on web reads.

## Adapter swap (demo → production)

| Box | Demo (now) | Production (later) |
|---|---|---|
| 1 Fetcher | GDELT, Google News RSS, Reddit .json | **Buy one:** Brandwatch or Meltwater. India: Wizikey or Konnect. TikTok official Discovery only. Firecrawl `/extract` on named pages. |
| 2 Scorer | Exclusion file + cheap LLM / keywords | LiteLLM → Cerebras for brand-fit. Optional NewsWhip Spike for velocity. Versioned rubric. |
| 3 Researcher | httpx + 3 pages + skeptic | Trusted-site lock, gpt-researcher shape, DeerFlow-style caps, sandbox. No Gmail/Drive. |
| 4 Brand Book | `brand.json` | Cerebras Knowledge pattern: ingest Docs/DAM, distill, hybrid retrieve, cite, scope brand/market. Guru-style verify badges. Optional Frontify if they already have it. |
| 5 Product Facts | `claims.json` | Full claim objects + evidence files + expiry + harvest-on-approve. Optional Artixio/Cosmedesk/EnterCo for dossiers. Calibrate with Tap-a-Gain. |
| 6 Trend Reports | SQLite + decay | Same shelf on Postgres. |
| 7 Track Record | SQLite | Postgres ledger. Never drop comments at publish. |
| 8 Brief | Code pack | Same, queries live Brand Brain + claims. |
| 9–10 Words | Gemini/Groq or templates | Frontier via LiteLLM. Filter-then-rank. Indic register. |
| 11 Pictures | Pillow stub / your HTTP API | Recraft or Flux via gateway. Four lock modes. Logo never in the model. |
| 12 Judge | Library compare + cheap LLM | Same compare. Second judge on health. Implied-claim pack (FTC). India pack (ASCI/CCPA/DMROA/FSSAI). Green pack. |
| 13 Hard Rules | Token lists | Gazette refresh job. ASCI AI-label tree as config. Geometry checks for video later. |
| 14 Loop | max 3 | Same. |
| 15 Review | Single user | Roles. Logged dial later (not day one). |
| 16 Export | ZIP + preview | Paused push to Ads/ESP. Expire/withdraw + time-to-dark. |
| 17 Feedback | Same day distill | Same, on Postgres. |
| Spine | SQLite, optional LiteLLM | Postgres+pgvector, LiteLLM Proxy pin ≥1.83.7, Langfuse, Instructor, OWASP dual-LLM. |

## Do not buy (even in production)

Adobe / Typeface / Veeva / Writer **as the product**. CrewAI. Portkey as gateway. Meta Content Library. TikTok scrape. Day-one 80% auto-approve. Autonomous publish.

## Money order (when funds exist)

1. Hosting: Postgres, LiteLLM, backups (Oracle/Cloudflare-cheap first).  
2. One licensed listener (Brandwatch **or** Meltwater — not both).  
3. Frontier model budget for copy + judge (via LiteLLM).  
4. Image model (or keep the API you plug into the demo).  
5. India vernacular listener if the room is IN-first.  
6. Tap-a-Gain sample set to calibrate the judge.  
7. Langfuse if they ask for traces in procurement.

## Slices (after funds)

Reuse the same order as the parked “trust desk / factory / pictures / radar” idea, but **radar already exists in the demo**. Production work is mostly swapping Fetcher/Scorer/Researcher/Brand Brain to paid adapters and moving SQLite → Postgres.

## How to start production later

1. Copy demo repo / same branch lineage.  
2. Implement `TrendSource` for Brandwatch behind a feature flag.  
3. Dual-run: demo sources still on, paid source adding signals.  
4. Cut over when the paid pipe is more trusted than GDELT.  
5. Do not rewrite the belt.

## Pointers

- Locked boxes: `docs/superpowers/specs/2026-08-19-ALL-BOXES.md`
- Scorecard: `docs/research/sota/2026-08-19-sota-scorecard.md`
- Demo build: `docs/superpowers/plans/2026-08-19-demo.md`
