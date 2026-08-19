# SOTA scorecard — process and tools per box

*Chosen 2026-08-19 after a swarm hunt (X + GitHub + live vendor docs + independent skeptics). This is the stack we present. Not a shopping list of everything we found.*

**Bar:** ships in production or readable code · auditable · fits a known belt · survives ASCI + FTC · cheap models for volume · buy the boring, build the moat.

**GitHub and X were first-class.** X threads stay `operator` unless a skeptic confirmed a product or repo.

---

## The stack in one page

```text
Listen     Brandwatch or Meltwater (licensed) + GDELT news + official TikTok CC
           + Firecrawl extract with a schema (rebuild trendFinder, do not run it)
Score      LiteLLM → Cerebras (cheap)  ·  velocity score separate from brand-fit
Research   planner + parallel crawl + skeptic  ·  trusted-site lock  ·  pages = data
Memory     our Brand Brain: Cerebras Knowledge shape  ·  Guru-style verify badges
           ·  Veeva-style claims objects  ·  Frontify-style kit as API
Factory    plain-code belt  ·  Instructor JSON on every step  ·  loop N=3
Words      generation-time rules + example bank  ·  angle×persona×register grid
Pictures   generate unlocked zone only  ·  code locks logo/type/disclaimer
Law        library compare + flag-and-fix  ·  unbribable lists first
Humans     last yes on irreversible verbs  ·  reviewer ≠ builder  ·  harvest on approve
Spine      LiteLLM + Langfuse + OWASP dual-LLM
Do not buy Adobe / Typeface / Veeva / Writer as the product. Steal their mechanics.
```

---

## Per box

### 1 · Source Fetcher

| | |
|---|---|
| **Process** | Allowlisted queries compiled first (Brandwatch Boolean + exclusion snippets). Licensed social API, not a scrape. Official TikTok Creative Center / Discovery API only. GDELT for news, recalls, regulator quotes. Schema extract (Firecrawl `/extract` + Zod/Pydantic) into one signal shape. |
| **Tools** | **Buy** Brandwatch *or* Meltwater for US/global. **Buy/wrap** Konnect Insights or Wizikey for India vernacular. **Wrap** Firecrawl extract. **Rebuild** the trendFinder shape (allowlist, 24h window, schema). |
| **Reject** | Running `ericciarla/trendFinder` as-is (stale Feb 2025, prompt-injection, one X account). Scraping TikTok Top Ads. Meta Content Library (research-only, not commercial). Douyin 即创 as a TikTok proxy. Meltwater X bodies (IDs only; ToS). |
| **Evidence** | Brandwatch query docs; Meltwater listening guide; trendFinder README last commit 2025-02-17; Meta Content Library eligibility Apr 2026. |

### 2 · Relevance Scorer

| | |
|---|---|
| **Process** | Two cheap scores, then a human-style fad kill. (1) Brand-fit 1–10 via a **fixed rubric** on a fast model. (2) Velocity / “will this still be loud tomorrow?” (NewsWhip idea). Homonym filter (Sprinklr AI Topics: inclusion/exclusion brief). Below 5 discard. 8+ wakes the researcher. |
| **Tools** | **Wrap** Cerebras via LiteLLM for the rubric. **Buy** NewsWhip Spike later if we need predicted engagement. Inclusion/exclusion text we **own** and can export. |
| **Reject** | One embedding “is this relevant?”. Treating Exploding Topics % growth as a health-claim green light. |
| **Evidence** | NewsWhip/Sprout product page; Sprinklr AI Topics; Cerebras via LiteLLM adapter (live). |

### 3 · Deep-Dive Researcher

| | |
|---|---|
| **Process** | EXM7777 diamond, confirmed by Anthropic + gpt-researcher: split angles → parallel workers → **separate skeptic** → cited report. Trusted-site lock (regs, brand.com, licensed CI). Reader model cannot call tools. Hard caps on searches, spend, time (DeerFlow `max_total_per_run`). |
| **Tools** | **Wrap** `assafelovic/gpt-researcher` shape (alive Jul 2026) or OpenAI/Gemini Deep Research **with** trusted sites on. **Steal** DeerFlow caps + sandbox. **Build** our cage in the belt. |
| **Reject** | Open-web Deep Research with Gmail/Drive attached. Uncapped fact-checker loops. Treating DeerFlow as the factory. |
| **Evidence** | EXM7777 article 2079934660982047021 (4.2k bookmarks); Anthropic Building Effective Agents; gpt-researcher README; deer-flow 80k★ MIT. |

### 4 · Brand Book

| | |
|---|---|
| **Process** | Meet files where brand already writes. Distill before embed. Hybrid retrieve. Cite. Scope by brand/market. Humans edit canonical rules. Compiled wiki (Karpathy) only **on top of** immutable sources. Verify badge + expiry (Guru). |
| **Tools** | **Build** the retrieval layer (Cerebras Knowledge pattern). **Steal** Frontify “brand as API/MCP, start read-only.” **Steal** Typeface kit-per-channel. Optional later wrap: Frontify if they already have a DAM. |
| **Reject** | New wiki nobody updates. Glean 275 connectors on day one. The Curator as production memory (48★ personal brain). Filing model answers back as sources. |
| **Evidence** | Cerebras Knowledge write-up Jul 2026; Frontify MCP; Guru verification docs; Karpathy gist + operator break at ~1k self-citing files. |

### 5 · Product Facts

| | |
|---|---|
| **Process** | Every claim is an object: verbatim text, SKU, market, evidence file, status (approved / conditional / forbidden), expiry. Checker **compares** copy to the library. Retired claims age to zero. Formula/ingredient lists are a separate hard table. |
| **Tools** | **Build** the matrix. **Steal** Veeva claims object + harvest-on-approve. **Steal** Writer comparison. Later **wrap** Artixio QuriousRI / Cosmedesk / EnterCo for ingredient dossiers if we sell those markets. |
| **Reject** | “AI, is this legal?” AdCompliance.in as clearance (real Bengaluru SPA, no named customers). Buying Veeva for a beauty pilot. |
| **Evidence** | Veeva PromoMats claims pages; Writer claims checker (live); AdCompliance.in exists (Getconvi CIN) but unproven. |

### 6 · Trend Reports

| | |
|---|---|
| **Process** | Scored, sourced, decaying shelf. A social spike is not a brief until it is on-brand **and** not an adverse-event story. Ipsos idea: do not copy consumer slang into a claim without a second check. |
| **Tools** | Our store. Inputs from Fetcher. Chanmama-style “what converts now” as a **feature**, not the product. |
| **Reject** | Evergreen trend wiki. Cloning Xiaohongshu winners as copy. |

### 7 · Track Record

| | |
|---|---|
| **Process** | Every draft + verdict + named human + reason. Distill before search (Cerebras). Harvest: a linked claim enters the library **only when the material is approved** (Veeva). Verify / Unverified / Expired states (Guru). Performance may inform creative; it may **never** override a legal no. |
| **Tools** | **Build** the ledger on day one. Adobe Brand Intelligence is the industry thesis (partly forward-looking). |
| **Reject** | Adobe GenStudio dropping comments at publish (their own docs). Typeface Arc Loop as a shipped legal-learning loop (vision). Silent model “learning approval patterns.” |

### 8 · Brief Builder

| | |
|---|---|
| **Process** | Code assembles: trend + brand slice + claims for featured SKUs + 3 winners + 3 rejections + format. Agents do not hunt context. Alimama 万相: brief = product facts + live intent. |
| **Tools** | **Build** in the belt. Typeface Ideation-from-graph is the pattern. |
| **Reject** | Blank-prompt “write a campaign.” |

### 9 · Strategist

| | |
|---|---|
| **Process** | Grid, not one idea. Axes that survived: **angle / pain (claim-safe) / persona / channel / Indic register** (pure Hindi vs Hinglish vs Roman). storyarb cascade: one atom → many derivatives. One specialist per channel (Typeface). One variable per test (operator posts). |
| **Tools** | **Build**. Frontier model via LiteLLM. Lapis only if Devanagari layout is the bottleneck. |
| **Reject** | Disease-pain grids (thyroid, PCOS, diabetes). Competitor-ad clones. Persado “no re-approval.” Ocean Engine auto-scripts without a judge. |

### 10 · Copywriter

| | |
|---|---|
| **Process** | Voice from examples, not adjectives. Rules apply **while writing**. Many candidates → **filter then rank** (Jacquard). 2–3 variants to the judge. Rewrite from numbered judge reasons. |
| **Tools** | **Build**. Frontier model. Writer-shaped guardrails in our prompt + data. |
| **Reject** | Buying Persado/Jacquard/Copy.ai as Brand Brain. Vendor “96% / statistically certain / $16M saved.” |

### 11 · Art Director

| | |
|---|---|
| **Process** | AI paints **unlocked** zones only. Code composites registered logo, licensed type, locked disclaimer. Adobe’s real lock table has **four** modes (not “two-zone”). Recraft/Flux for the picture. Cap edit turns (~6 Flux degrades). |
| **Tools** | **Build** compositor. **Wrap** Recraft or Flux via gateway. Pencil/Frontify library schema for the asset pack. |
| **Reject** | Prompting the logo. Higgsfield “locks your logo” homepage. Uploading SVG to CapCut/剪映 cloud. Recraft “generate logos.” |

### 12 · Compliance Judge

| | |
|---|---|
| **Process** | Compare every sentence to the claims library. Flag **and** propose a compliant rewrite (Saifr). Second independent judge on high-risk health lines. Implied-claim test (FTC 2022). India pack: ASCI + CCPA + DMROA + FSSAI. Green claims as a separate pack (Provenance). Video later: VO + supers (Cape). |
| **Tools** | **Build**. Calibrate with Tap-a-Gain (ex-ASCI SG) on a sample set. **Watch** AdCompliance.in. Do not buy Writer/Veeva/Saifr. |
| **Reject** | One LLM “is this legal?” Seed-stage Luthor as the brain. 3-second AdCompliance verdict as clearance. |

### 13 · Hard Rules

| | |
|---|---|
| **Process** | Pure code, before the judge. Banned tokens (`cures`, DMROA disease list, Writer superlatives). Required tokens (`#ad` / market disclaimer). Geometry later (disclaimer size/contrast/hold). ASCI 2026 AI-label **tree**: high = block (label does not cure); medium = inject label; low = log (AI *copy* is low in the draft). |
| **Tools** | **Build** from gazettes. Refresh when schedules change. IntelligenceBank risk list as a checklist. |
| **Reject** | Letting the model decide if “best” is puffery. Blanket “AI-generated” stamp on every caption (wrong reading of the ASCI draft). |

### 14 · Improvement Loop

| | |
|---|---|
| **Process** | Writer ≠ judge. Max **3** rounds, then flag to a human. Only the failed claim is revised (Skadoosh). EXM7777 stop rule: graphs buy breadth, not judgment. |
| **Tools** | **Build** in the belt. Anthropic evaluator-optimizer is the name of the pattern. |
| **Reject** | CrewAI Flows official sample (uncapped revise). LangGraph `interrupt` as the whole belt (node replay double-bills image gen). |

### 15 · Review & Approve

| | |
|---|---|
| **Process** | Builder cannot approve. Reviewer comments ≠ last yes (Adobe Workfront). Last yes sits on **irreversible verbs**: publish, boost, send, claim. Day one: 100% human on benefit claims. A logged dial (item-by-item → sampled) is a **later setting**, change itself is an approval. Decompose the post into claims for review. |
| **Tools** | **Build** a thin queue. Filestage/Ziflow = proofing pattern, not the product. Veeva MLR roles if the buyer is life-sciences. |
| **Reject** | Machina Sports as the model (no named paying-brand case). EXM7777 as a vendor. Day-one 80% auto-approve. Agent assigned as the signature. |

### 16 · Preview & Export

| | |
|---|---|
| **Process** | Pixel-perfect preview. Export **paused/draft** into ad/ESP accounts (Adobe TikTok path). Media ops owns go-live. Expire / withdraw is a button with state (Veeva / AEM). Prove time-to-dark. |
| **Tools** | **Build** preview + pack + expire. **Wrap** Braze/SFMC later. Their approval is launch governance, not our legal yes. |
| **Reject** | Typeface “create, preview, publish in one go” inside SFMC. Braze API/transactional bypass as the happy path. |

### 17 · Feedback Writer

| | |
|---|---|
| **Process** | Require a reason. Distill. Write back into Brand Brain the same day. Same mistake does not survive twice (EXM7777 soul/memory). |
| **Tools** | **Build**. |
| **Reject** | One-click reject. CTR overriding a legal no. |

---

## Spine (not a box, required)

| Piece | Pick | Why | Reject |
|---|---|---|---|
| Orchestrator | **Plain-code state machine** | Path is known. Anthropic: workflow, not agent. | CrewAI, DeerFlow-as-belt, Temporal for v1 |
| Gateway | **LiteLLM Proxy** | Cerebras first-class, json_schema, spend logs, Langfuse callback. Pin ≥1.83.7 (SQLi CVE-2026-42208). | Portkey (PANW acquired, OSS quiet), OpenRouter as the control plane |
| Schema | **Instructor + native json_schema** | Every step typed. trendFinder’s missing schema is the bug we do not copy. | Free-text JSON hope |
| Evals | **Langfuse self-host** | Traces + annotation queues. Audit logs are EE — our DB holds publish/approve until then. | Braintrust as SoR; Phoenix as hosted UI (ELv2) |
| Injection | **OWASP LLM01 + dual-LLM / CaMeL** | Reader cannot act. Pages in a data tag. | Regex “ignore previous instructions” |
| Cheap tokens | **Cerebras via LiteLLM** | Scoring only. Catalog churns. | Direct SDK; brand copy |

---

## What EXM7777 actually gave us (sorted, not worshipped)

Read end-to-end (bookmarks first):

1. **Graphs course** (article 2079934660982047021, ~4.2k bookmarks) — diamond, stop rule, human gate, loop cap, one writer per file, written routing. **Steal.**
2. **Team + self-improving loop** (2078476892127318295, ~4.2k bookmarks) — named agents, reviewer ≠ author, reasons write back. Raft is a sponsor. **Steal the loop, do not buy Raft as the factory.**
3. **GTM vault** (208973161 / 208971460, ~900 bookmarks) — folders, rulings as dated lines, hubs first. Same idea as Cerebras + Karpathy. **Steal rulings. Do not make Obsidian the production Brand Brain.**
4. Audience-growth / Hormozi / 17-year-old UGC articles — **discard** for this product.

Machina Sports remains one governance reference. It is not the architecture.

---

## Names that were not on last week’s dossier (required underdogs)

| Name | Region | Why it survived |
|---|---|---|
| Tap-a-Gain / AdCheck | IN | Ex-ASCI Secretary-General. Calibration set. |
| AdCompliance.in | IN | Real company. Watch, do not buy. |
| Wizikey, Konnect Insights | IN | Vernacular listening. |
| Artixio QuriousRI | IN | Cosmetic ingredient/label check. |
| Lapis | IN | Native Indic register, not translate. |
| Rocketium | IN | Locked design system + humans (vendor metrics). |
| Honasa / Mamaearth | IN | Cautionary: scale without a claims machine. |
| Tencent WeKnora | CN | OSS wiki + chunk rollback + HITL MCP. |
| DeerFlow | CN | Caps + sandbox. Not the belt. |
| Chanmama, 即创, 万相营造, 妙思 | CN | Volume creative / convert-now listening. Patterns only. |
| EnterCo CosReg | CN | Penalty-case library. |
| Filestage, Ziflow | EU | AI pre-flag + human yes. |
| Schlafender Hase TVT | EU | Diff vs approved fragment. EMA/MHRA-shaped. |
| Bannerflow, Frontify, Cosmedesk, Cape, Provenance | EU | Locks, PIF, video supers, green claims. |
| Guru, Jacquard (ex-Phrasee), LiteLLM, Langfuse, Instructor, gpt-researcher | US/global | Memory badges, filter-then-rank, spine, researcher shape. |
| SkadooshGG | US operator | Claim-decompose. Not a vendor. |

---

## Buy vs build (money)

**Build (the moat):** claims objects, Brand Brain retrieval, belt, hard-rule lists, review ledger, compositor, harvest loop.

**Buy/wrap (boring pipes):** one licensed listener, Firecrawl extract, LiteLLM, Langfuse, image API, later Braze/SFMC.

**Do not buy to become the product:** Adobe GenStudio, Typeface, Veeva, Writer, Persado, Glean, Raft, AdCompliance.

---

## Caveats the swarm could not kill

- Cerebras Knowledge 15k/day is vendor-published. Pattern is independently written up. Primary blog was thin in an earlier session; this pass’s memory hunter opened it.
- Adobe Brand Intelligence / Typeface Arc Loop are partly forward-looking.
- AdCompliance.in is real and unproven.
- ASCI AI-label text is a **draft** (consult ended Jun 2026). Build the tree as a toggle.
- China homepages (妙思, 即创) often return empty outside China. Treat CN volume stats as vendor.
- LiteLLM default branch naming is messy; pin a release, do not track `main` blindly.
