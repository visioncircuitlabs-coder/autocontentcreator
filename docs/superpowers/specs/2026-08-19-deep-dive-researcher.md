# Box 3 — Deep-Dive Researcher (hardened)

Status: **locked** (you said yes). Layer 1 Radar is complete. Next is Brand Book. No app code.

The only radar box that may wander. It fires only when the Scorer says `deep_dive`. It files a cited Trend Report. It does not write ads.

## What goes in

| Input | From |
|---|---|
| One signal | Scorer gate `deep_dive` (brand-fit ≥ 8, not killed) |
| Brand slice | Brand Brain query (category, do-not-join topics) — cited, not the whole book |
| Trusted-site list | Human. Default: brand.com, ASCI/FTC/gazette pages, licensed CI, the signal’s own url |
| Caps | Code: max searches, max spend, max minutes, max worker count |

## What comes out

One Trend Report, same shape every time:

```text
report_id
signal_id
what            (what is happening)
why_now
who             (who is driving it)
angles[]        (content ideas — not copy)
risks[]         (controversy, fade, claim-adjacent)
sources[]       (url, fetched_at, hash, quote-or-not)
skeptic         (what was killed and why)
spent           (searches, tokens, rupees)
capped_at       (why it stopped)
```

No report without sources. A source the skeptic kills does not appear as fact.

## How it runs (diamond)

```text
planner          splits 3–5 angles  (not 20)
    │
    ├─ worker A   reads only trusted sites + the seed url
    ├─ worker B   same cage, different angle
    └─ worker C   same cage
         │
         ▼
    skeptic        separate job — tries to kill each finding
                   (wrong, stale, no real source)
         │
         ▼
    merge survivors → Trend Report → Brand Brain shelf
```

This is EXM7777’s diamond + Anthropic’s “agent only when the path is unknown” + gpt-researcher’s planner/parallel/cite. The **reader cannot call tools**. Pages are data. Dual-LLM: the model that reads HTML cannot publish, search extra, or write the final report’s claims.

Hard stop: time, money, or search count. Then it **must** file, even if thin. Thin + honest beats a looping “almost done.”

## Buy / wrap / build

| | |
|---|---|
| **Build** | The cage, trusted-site lock, skeptic job, report schema, caps. |
| **Wrap** | `assafelovic/gpt-researcher` **shape**, or OpenAI/Gemini Deep Research **with trusted sites on**. DeerFlow: steal `max_total_per_run` + sandbox only. |
| **Do not** | Open-web Deep Research attached to Gmail/Drive. Uncapped fact-check loops. DeerFlow as the factory. Treating the researcher as a copywriter. |

## Forbidden

- Following instructions found on a web page.
- Using a consumer Deep Research path that can see mailbox or Drive.
- Writing captions, claims, or “#1” lines inside the report.
- Re-running forever until it “feels complete.”
- Letting the same worker grade its own findings.

## If a lawyer opens this box

They get: the seed signal, the trusted-site list, every url + hash, what the skeptic dropped, spend, and the cap that stopped it. A missing source means the line is not in the report.

## Hands off to

Trend Reports shelf (decays). A human may press Create later. This box never starts the factory.

## Done when you say

This box is locked. Layer 1 (Radar) is then complete. Next is **Brand Book**.
