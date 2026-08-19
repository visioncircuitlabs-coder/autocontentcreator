# Box 4 — Brand Book (hardened)

Status: **locked** (you said yes to all). Next boxes 5–17 written in the same pass. No app code.

The soul of the brand, as a retrieval layer — not a PDF nobody opens, not a second wiki people forget to update.

## What it is

How we sound, look, and refuse. **Not** what we may legally claim (that is Product Facts). A copywriter queries this. They do not receive the whole book pasted into a prompt.

## What goes in

| Input | Who | Notes |
|---|---|---|
| Existing brand files | Brand / agency | Google Docs, PDFs, DAM, Frontify if they have it. We meet them there. |
| Voice examples | Human | 10 on-voice lines, 10 off-voice lines. Examples beat adjectives. |
| Visual kit | Human | Colors, type, photo style, logo lockups, clear space. |
| Do / don’t | Human | Topics, humor, competitor mentions, “never joke about skin disease.” |
| Channel overlays | Human | Instagram ≠ LinkedIn ≠ IN Hindi register. Typeface kit-per-channel idea. |

Humans are the only editors of **canonical** rules. The machine may draft a distilled card; a human must verify it before it is citeable.

## What comes out (when something queries it)

```text
slice            (only the part that matches brand + market + channel)
source_ref       (file, page, or card id)
verify_state     verified | unverified | expired     (Guru idea)
expires_at
cite             required — no slice without a pointer
```

Scope: Neutrogena India cannot pull Listerine US voice notes.

## How it runs (Cerebras Knowledge shape)

```text
connectors     read where brand already writes
    │
    ▼
distill        one card: rule + examples + channel
               raw file stays for keyword search; we embed the card
    │
    ▼
one index      hybrid: exact phrase + meaning + recency
    │
    ▼
query          Strategist / Copywriter / Art Director / Brief
               always with citations
```

Karpathy “LLM wiki” is allowed only as a **compiled layer on top of immutable sources**. Model-written pages that cite themselves are forbidden (operators saw this break ~1k files).

Verify badge + expiry: a voice card that nobody has confirmed in 90 days is `unverified`. Generators may not treat it as law.

## Buy / wrap / build

| | |
|---|---|
| **Build** | Index, distill-before-embed, hybrid retrieve, cite, scope by brand/market/channel, verify states. |
| **Steal** | Frontify “brand as API, start read-only.” Typeface kit-per-channel. Guru verify/expiry. Cerebras: meet data where it lives. |
| **Wrap later** | Frontify MCP if the brand already lives there. |
| **Do not buy** | Glean (275 connectors) for a pilot. The Curator as production memory. Jasper as the system of record. |

## Forbidden

- Making Legal retype the brand book into our UI.
- Letting the model edit canonical rules.
- Filing an agent’s answer back as if it were a source.
- One global search across all brands.
- Pasting the whole book into every prompt.

## If a lawyer opens this box

They get: which file the voice rule came from, who verified it, when it expires, and which brand/market was in scope. An unverified card cannot be the reason a claim shipped (claims are Product Facts anyway).

## Hands off to

Brief Builder and every creative box **query** this. Product Facts stays a separate shelf (claims objects).

## Done when you say

This box is locked. Next is **Product Facts**.
