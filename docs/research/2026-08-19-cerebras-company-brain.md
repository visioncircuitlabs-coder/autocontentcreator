# Cerebras Company Brain — what they actually meant

*Written 2026-08-19 after the previous research pass looked at the **wrong Cerebras** (their inference chips). This note is about **Cerebras Knowledge**, the internal system commentators call their company brain.*

**Verdict for our machine:** this does **not** change the four-layer pipeline you already like. It **does** change how we build Layer 2, the Brand Brain. We keep the conveyor belt. We upgrade the memory.

## Two different Cerebras

| | What the last pass used | What you meant |
|---|---|---|
| Name | Cerebras Inference API | Cerebras Knowledge (“company brain”) |
| Job | Cheap, fast tokens for scoring | One retrieval layer over Slack, docs, wikis, code, internal DBs |
| Role in *our* product | Optional engine for the Relevance Scorer | Blueprint for the Brand Brain |
| Keep it? | Yes, behind a gateway, never hard-wired | Yes — this is the memory design we were missing the mechanics for |

Both exist. They are not the same product. The last map only cited the chip/API. That citation stays valid for the scorer. It was the wrong answer to “which Cerebras?”

## What Cerebras Knowledge is

Cerebras (the wafer-scale chip company) published an engineering write-up of an internal tool, **Cerebras Knowledge**, around July 2026. Independent write-ups (MonoClick 20 Jul 2026, Stellar Work 21 Jul 2026, mer.vin 17 Jul 2026) agree on the same shape. Cerebras’ own blog is at `https://www.cerebras.ai/blog/how-we-built-our-knowledge-base` — that page did not load in this session, so numbers below are **vendor-published, secondary-confirmed**, not re-read from the primary HTML.

Reported (treat as vendor-claimed):

- ~15,000 questions/day within ~3 months of launch
- Used by employees, automations, **and other AI agents**
- One of their most-adopted internal tools

What matters is the design, not the vanity number.

## The founding decision

They refused to build a new wiki that everyone has to keep updated.

They **meet data where it already lives**: Slack threads, Google Docs, Confluence, GitHub, Jira, specialist databases. Each source keeps its own authoring UX. A connector copies a normalized row into one shared index.

That is the opposite of “Karpathy / GBrain company brain = dump everything into a stored wiki the model reads.” Cerebras rejected that. The brain is a **retrieval layer**, not a second copy of the company.

## Architecture we actually copy

```text
connectors (Slack, docs, claims files, approvals)
        │
        ▼
  distill first  ──►  one shared index (Postgres + embeddings + full-text)
        │
        ▼
  query pipeline ──►  plan → retrieve several ways → fuse ranks → rerank → cite
        │
        ├── humans ask in a search box
        └── agents call the same layer (MCP-style tools)
```

Seven mechanics that transfer to a regulated brand:

1. **Meet data where it lives.** Brand guidelines, medical-affairs PDFs, claims matrices, past legal redlines, approval comments — ingest them. Do not make Legal retype them into our UI.
2. **One index, many sources.** Adding “ASCI circulars” or “US FTC letters” later is a connector, not a rebuild.
3. **Distill before you embed.** Raw Slack or a 40-page brand book is noise. Store: the question, the resolution, the systems/products involved, then embed *that*. Keep the raw text for exact keyword search only.
4. **Hybrid retrieval, not “just vectors.”** Exact claim strings (“dermatologist tested”) must match as literals. Paraphrases (“skin-doctor approved”) must match as meaning. Recency must beat a 2019 claim that legal retired. Filler (“looks good”) must lose.
5. **Citations or it didn’t happen.** Every answer — and every judge verdict — points at the source row. A support answer with no source is a guess. A brand claim with no source is a lawsuit.
6. **Scope before it drowns.** Search is scoped by brand / SKU / market / jurisdiction. A Neutrogena India query must not retrieve a Listerine US retired claim.
7. **Built for agents, not a chat box.** The Brand Brain is a retrieval API the Strategist, Copywriter, and Judge all call. It is not a paragraph we paste into every prompt.

Auth, permissions, and an audit log sit in front of every query. For a Kenvue-class buyer this is not optional.

## What we do *not* copy

- Their 40 GB code-repo chunker as a v1 source. We are not indexing chip netlists.
- Treating the company brain as the *whole product*. Their brain answers “where is X / who knows Y.” Ours must still *make* content and *block* illegal claims.
- Fast Cerebras inference as a brand-copy engine. Wrong model class for voice.

## What this changes in *our* map

**Does not change:** Trend Radar → Brand Brain → Content Factory → Command Center. Humans still approve. Agents still live only inside steps.

**Does change:** Layer 2 stops being “four folders we typed in.” It becomes a living, permission-aware memory:

| Shelf (already on the map) | Company-brain mechanic |
|---|---|
| Brand Book | Ingest from the files brand already maintains. Distill into voice rules + examples. Humans remain the only editors of the *canonical* rules. |
| Product Facts | Claims library is a first-class source with exact-match retrieval. Retired claims age-decay to zero. |
| Trend Reports | Same index, different source type, with freshness decay (already locked). |
| Track Record | Every approve/reject **with reason** is distilled (question → decision → why) *before* it is embedded. That is how tomorrow’s brief gets “write like these, avoid those.” |

## Confidence and caveats

- Architecture shape: **high** (multiple independent write-ups, same diagram).
- 15k/day and “3 months”: **medium** (vendor-published, not independently counted).
- Primary blog HTML: **not re-fetched this session** — if we cite this in a client deck, re-open the Cerebras post first.
- “Company brain” is commentators’ name, not Cerebras’ product name. They call it Cerebras Knowledge.

## Sources

- Cerebras (primary, unloadable this session): https://www.cerebras.ai/blog/how-we-built-our-knowledge-base
- MonoClick, 20 Jul 2026: https://www.monoclick.ai/blog/cerebras-knowledge-base-lessons-for-ecommerce
- mer.vin, 17 Jul 2026: https://mer.vin/2026/07/how-cerebras-built-a-15k-query-day-internal-knowledge-base/
- Stellar Work, 21 Jul 2026: https://www.stellarwork.com/captains-log/how-cerebras-built-their-company-brain
- Cerebras inference (the *other* Cerebras, still valid for scoring): https://www.cerebras.ai/pricing
