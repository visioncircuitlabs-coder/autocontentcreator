# Industry Research — Who Has Built Working AI Content Machines for Brands
*Researched 2026-08-18 by a 20-agent fleet (10 researchers + 10 independent fact-checkers). Full structured dossiers with every source link: `raw-dossiers-2026-08-18.json`.*

## The four consensus findings (all 10 dossiers agree)

1. **Loops win, agents serve.** Every shipped production system is a deterministic pipeline with bounded AI steps inside — even the ones branded "agentic." CrewAI (the autonomous-agents flagship, 57k stars) added deterministic Flows and recommends wrapping crews inside them for production. LangGraph won production (Uber, LinkedIn, Replit) by treating agents as state machines. Anthropic's own guidance says the same.
2. **Compliance is the product, not a feature.** Adobe's entire enterprise pitch is guardrails (locked templates, verbatim disclaimers, brand scores, legal routing). Writer sells a standalone claims checker. Generation itself is commoditized — Adobe happily resells competitors' models.
3. **Humans approve, always.** Zero production systems let AI autonomously publish regulated brand content. Best-in-class scaling pattern: Machina's "approval dial" (item-by-item review until trust earned → sampled checks, mode logged per published item).
4. **The moat is memory.** Adobe Brand Intelligence (Apr 2026) and Typeface Arc Loop (Mar 2026) both bet on the same thing: converting human approvals/rejections into brand knowledge. Log review decisions with reasons from day one.

## Player-by-player (verified state, Aug 2026)

### Adobe GenStudio — the incumbent (confidence: high)
Enterprise "content supply chain." Coca-Cola, Estée Lauder, Pfizer-class logos. Key patterns to steal:
- **Two-zone templates**: AI generates only inside unlocked zones of pre-approved templates → on-brand by construction.
- **Approved fragments**: regulated text (claims/disclaimers) stored verbatim and injected after generation — AI never writes it.
- **Brand score before human review** → humans review pre-filtered content.
- **Pre-approve the container, not fast-track the approval** → trend response in hours.
- Caveats from fact-check: Brand Intelligence partly forward-looking at launch; customer metrics (Lumen "35×") vendor-published.

### Writer — the compliance wedge (confidence: high)
$1.9B valuation. Curology (skincare), E.L.F. Beauty, Mars are customers. **Product Claims Checker is live**: copy + approved-claims library → AI marks approved vs not. Compliance as *comparison against a claims library*, not "is this legal?". Superlative ban-list ("best", "only", "guaranteed"). Guardrails applied at generation time AND check time. Caveat: several logo customers are also investors; retail metrics vendor-reported.

### Typeface — orchestration engine (confidence: high)
~$1B valuation, $165M raised, ~$34M est. ARR. Arc Graph (brand data layer) + channel-specific Arc Agents + Arc Spaces (approvals) + Arc Forge ("turn workflows into custom agents" — starts from workflow, adds autonomy inside steps). P&G, AB InBev, Sally Beauty on logo bar. Master-asset → variations is the flagship money pattern.

### Jasper — survived by pivoting to governance (confidence: high)
Prosumer AI writing died (~$120M → ~$55M revenue est., four layoff rounds); enterprise pivot on **Jasper IQ** (persistent brand brain: Brand IQ + Knowledge Base + Governance) + fixed Plan→Create→Adapt→Activate→Optimize pipeline. Ulta Beauty, Sanofi customers. 2026 wedge: **GEO** (visibility in AI answers). Lesson: generic AI writing is dead; brand memory + governance + workflow is what survives.

### storyarb / Alex Lieberman — the human benchmark (confidence: high)
Human-led B2B content agency (mid-7-figure, 18 people, Mar 2025). SME interviews → anchor asset → derivative cascade (newsletter, social). AI assists inside steps; one beta agent (enrich→draft→human approves). Lieberman's 4-phase AI ladder: don't attempt autonomous agents (Phase 4) before AI works in bounded steps (Phases 1–3). "Don't market the AI — sell the outcome." Anti-slop: "content only you could publish."

### Machina Sports — closest architecture to ours (confidence: high)
AI agent platform for sports content. Early-stage, demo-led, **no named paying customers** (logo wall = partners/accelerators/investors). But their published platform design is the best governance blueprint found:
- Six-stage lifecycle: Connect → Ground → Configure → Approve → Ship → Measure.
- **Approval dial** (item-by-item → sampled once trust earned, mode logged per item).
- Typed canonical entities; freshness inherited from source ("if a provider is late, the agent is late"); rollback as first-class; audit trail as product.

### Cerebras — two products, do not collapse them
**Cerebras Knowledge (the company brain) — Brand Brain blueprint (confidence: high on shape, medium on vanity metrics).** Internal retrieval system launched ~Q2 2026. Independent write-ups (Jul 2026) describe: meet data where it lives (Slack/docs/code/DBs), one shared Postgres embeddings table, distill-before-embed, hybrid retrieval (full-text + vectors + rarity + age decay), rank fusion + rerank + citations, project-scoped search, MCP so *agents* query the same layer as humans. They rejected “migrate everything into a new wiki.” This is how Layer 2 should work. Full note: `2026-08-19-cerebras-company-brain.md`. 15k queries/day is vendor-published.

**Cerebras Inference — infra only (confidence: high).** Wafer-scale chips; API serves a small catalog of open models at ~3,000 tok/s, $0.35/$0.75 per M tokens. OpenAI partnership confirmed (Ultrafast tier). Use for high-volume cheap steps (trend scoring) only; route via gateway — their catalog churns. Speed only matters where a human is waiting. Wrong engine for final brand copy.

### trendFinder (open-source) — our Trend Radar blueprint (confidence: high)
4.1k stars, MIT, ~6 files, unmaintained since Feb 2025. Pipeline verified line-by-line: getCronSources → scrapeSources (Firecrawl /extract with schema) → generateDraft (one LLM call) → Slack webhook. Runs free on GitHub Actions cron. Fact-check corrections: current HEAD uses OpenAI o3-mini with NO schema enforcement on the final call (a fragility, not a pattern); X free tier = 1 account. We build our own version with schema enforcement everywhere.

### Agent frameworks 2026 (confidence: high)
LangGraph = production standard (checkpointing, pause-for-approval). CrewAI = fast prototype, teams migrate off it when reliability bites. Claude Agent SDK = production-grade, Claude-only, model-driven loop — good for generation steps. Plain-code state machine = legitimate choice for a known pipeline shape. **Our pipeline shape is known → explicit workflow (plain code or LangGraph-style), agents only inside steps. Avoid the CrewAI→rebuild migration tax.**
- Correction from fact-check: "Anthropic ships on LangGraph" is false; drop it.

### Compliance AI landscape (confidence: medium)
Mature claims-review AI exists mostly for **finance** (Saifr/Fidelity, Red Oak, IntelligenceBank+Red Marker, Luthor=seed-stage YC F24). **Consumer health & beauty has essentially Writer + human consultants — a real market gap.** Regulatory reality: FTC sent ~670 penalty-offense notices to health-product marketers (Apr 2023); ASCI (India) found 98% of 1,015 influencer ads needed modification (2024–25). Universal architecture: AI flags → suggests compliant rewording (Saifr pattern) → human approves → audit trail → periodic re-scan of live content. Watch: draft ASCI guidelines may require disclosure of AI use in ads — keep an "AI-generated" label toggle.

## Design decisions this research locks in for our machine
- Claims matrix / claims library as first-class, human-edited data (Writer + Adobe + SG Systems pattern).
- Regulated text injected verbatim, never generated (Adobe).
- Brand rules applied at generation time AND at a separate check gate (Writer).
- Automated brand/compliance score before human review (Adobe).
- Approval dial with logged modes + audit trail (Machina).
- Flag-and-fix: compliance failures return suggested compliant rewording (Saifr).
- Every approval/rejection logged with reason → future brand memory (Adobe Brand Intelligence thesis).
- Two-stage cheap filtering in the radar; schema-enforced JSON on every LLM step (trendFinder + its fact-check).
- Model routing per step through a gateway; cheap fast models for volume steps, frontier for voice (Cerebras dossier).
- Plain-code state machine orchestrator; Claude Agent SDK inside generation steps; no CrewAI.
- Rollback and freshness-decay as day-one features (Machina).
- Positioning: mid-market/India gap that Adobe's complexity and pricing leaves open; sell outcome, not "AI" (Lieberman).
- Brand Brain is a Cerebras-Knowledge-style retrieval layer, not a folder of pasted prompts: ingest from where brand/legal already write, distill decisions before embedding, hybrid retrieval so claim strings match exactly, cite every use, scope by brand/SKU/market (Cerebras Knowledge, 2026).
- Day-one publish path is 100% human on benefit claims. An 80/20 auto-approve split is a later *logged* setting on the approval dial, never the default (reference pitch deck is a reference, not the spec — see `private deck notes (not in this repo)`).
- Simulate, paid micro-test, amplify, and GEO/AI-recall are phase-2 / sibling capabilities. They do not redraw the four-layer factory.
