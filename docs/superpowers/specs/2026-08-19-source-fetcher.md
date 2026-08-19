# Box 1 — Source Fetcher (hardened)

Status: **locked** (you said yes). Next box is Relevance Scorer. No app code.

The alarm clock. Every few hours it collects the outside world into one standard **signal**. It does not decide if a signal is on-brand. That is the Scorer.

## What goes in

| Input | Who sets it | Notes |
|---|---|---|
| Source list | Human | Allowlist only. No “search the whole web.” |
| Query pack per source | Human | Brandwatch-style Boolean + exclusion snippets (job ads, marketplaces, the brand name used as a common word). |
| Market | Human | IN / US / both. Changes which listener we call. |
| Schedule | Code | Every 6 hours. One dead source never stops the others. |

## What comes out

One row per unique event. Same shape every time:

```text
signal_id
seen_at          (when we fetched)
happened_at      (when the source says it happened)
source           (brandwatch | meltwater | wizikey | konnect | gdelt | tiktok_cc | firecrawl)
url              (canonical link, or empty if ToS forbids storing the body)
title
snippet          (short text we are licensed to keep)
lang
market
query_id         (which allowlisted query caught it)
raw_ref          (vendor mention id — not a scrape blob)
```

Pages from Firecrawl are stored as **data**, never pasted into a system prompt. Hash of the URL is kept so we can prove what we saw.

## How it runs

```text
scheduler
    │
    ├─ licensed social  ── Brandwatch OR Meltwater (US/global)
    ├─ India vernacular ── Wizikey or Konnect Insights
    ├─ news / recalls   ── GDELT (cheap, 15-min news graph)
    ├─ TikTok culture   ── official Creative Center / Discovery API only
    └─ named pages      ── Firecrawl /extract + schema (competitor site, ASCI, brand.com)
           │
           ▼
    normalize → dedupe by URL/title → hand to Relevance Scorer
```

If one pipe fails: log it, continue. The machine is late if a **provider** is late. We do not invent a fill-in.

## Buy / wrap / build

| | |
|---|---|
| **Buy one** | Brandwatch *or* Meltwater for licensed social. Not both on day one. |
| **Buy/wrap India** | Wizikey or Konnect if we need Hindi/Tamil. English-only Brandwatch is not enough for India. |
| **Wrap** | Firecrawl extract. GDELT. TikTok official Discovery only. |
| **Build** | The scheduler, the signal shape, dedupe, “one source dead → others run.” |
| **Do not run** | `ericciarla/trendFinder` as-is (stale Feb 2025, prompt-injection, one X account). Steal the **shape** only. |

## Forbidden

- Scraping TikTok Top Ads or competitor creatives in bulk.
- Using Meta Content Library (research-only, not commercial).
- Using Douyin 即创 as a TikTok proxy.
- Asking Meltwater for X tweet **bodies** (API is IDs only; ToS).
- Storing a selfie/UGC image as training data because a logo appeared in it.
- Treating a scraped page as instructions for any later agent.

## If a lawyer opens this box

They should get: which query, which vendor contract, which mention id, when we fetched, whether we stored text or only a link, and that a failed source did not silently invent rows.

## Hands off to

Relevance Scorer. Fetcher never scores, never writes a brief, never creates content.

## Done when you say

This box is locked. Next box is **Relevance Scorer**.
