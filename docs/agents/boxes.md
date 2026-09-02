# Boxes — live file map

Specs in `docs/superpowers/specs/` lock **intent**. This table is **what ships**. If they disagree, code wins; add a drift note, do not silently “fix” the spec by rewriting the box.

| # | Box | Live module | Owns | Must not own |
|---|---|---|---|---|
| 1 | Source Fetcher | `boxes/fetcher.py` + `adapters/{gdelt,news_rss,reddit_json,grok_web}.py` | Collect title/url/snippet. One dead source continues. | Scoring, captions |
| 2 | Relevance Scorer | `boxes/scorer.py` | Exclusion kill, brand_fit 1–10, gate | Writing posts |
| 3 | Deep-Dive Researcher | `boxes/researcher.py` | Diamond research, junk URL denylist, budget | Ads, Imagine |
| 4 | Brand Book | `boxes/brand_book.py` + `fixtures/neutrogena/brand.json` | Voice cards, examples | Claims gazette |
| 5 | Product Facts | `boxes/product_facts.py` + `claims.json` | Approved / forbidden phrases | Fetch |
| 6 | Trend Reports | SQLite `reports` via `db.py` | Shelf for a closer look | Factory text |
| 7 | Track Record | `boxes/feedback.py` + table `track_record` | Distilled yes/no with caption | Publishing |
| 8 | Brief Builder | `boxes/brief.py` | Deterministic pack: report + brand slice + claims + wins/losses | LLM |
| 9 | Strategist | `boxes/strategist.py` | Angles / persona / claim-safe pain. Templates if chat down | Captions |
| 10 | Copywriter | `boxes/copywriter.py` | Ask 8 captions, filter to 2–3 postable. Rewrite from numbered reasons | Image, go-live |
| 11 | Art Director | `boxes/art_director.py` + `boxes/visual.py` | Unlocked photo + coded overlay | Claims policy |
| 12 | Compliance Judge | `boxes/judge.py` | Sentence vs Product Facts, optional implied-claim chat | Hard-token gazette |
| 13 | Hard Rules | `boxes/hard_rules.py` | Banned tokens, #ad, disclaimer presence. **No LLM** | Taste |
| 14 | Improvement Loop | `boxes/loop.py` + `boxes/craft.py` | Rules + judge + craft. Max 3. Then `flag_human` | Human yes/no |
| 15 | Review & Approve | `boxes/review.py` | Named person, reason, verdict. Not publish | Instagram |
| 16 | Preview & Export | `boxes/export.py` | Paused ZIP (html + png + json). May paint if image missing | Go-live |
| 17 | Feedback Writer | `boxes/feedback.py` | Ledger row after decide | Radar |
| — | Spine | `boxes/belt.py`, `ports.py`, `main.py` | Order of steps | Extra orchestrator |

Fixture deep-dive (practice idea): `boxes/fixture_dive.py` + `POST /radar/fixture`. Labeled. Not “this search.”

## Scoring gates

`decide_gate` in `scorer.py`:

```text
safety == kill  OR  brand_fit < 5  →  discard     (Don't use)
brand_fit >= 8                     →  deep_dive   (Closer look)
else                               →  background  (Skip for now)
```

Exclusion file: `fixtures/neutrogena/exclusion.txt` (`category|pattern`). Match → `safety=kill`. Velocity never overrides a kill.

Chat scores at most **5** headlines (`MAX_CHAT_SCORES`) after keyword prefilter (`MIN_KEYWORD_FIT_FOR_CHAT = 4`). The rest stay on keyword fallback so Look can finish inside the proxy window.

## Research (demo fence)

Radar path: `run_research(..., chat=None, max_gets=3, max_seconds=35)`.

Junk URLs (`is_junk_url`): analytics, tag managers, ads, gstatic, `google-analytics.com` (this host does **not** contain `google.com` — both checks are required), `/gtag/`, `/pagead/`, `/ads/`, `.js` / `.png` paths, `/collect`. Same list mirrored in `apps/web/desk/review.ts`. Junk never appears in the main Pick body; optional **Sources** fold shows remaining citations.

Google News tracker hosts are skipped (`news.google.com`). Pages are wrapped as data. Binary/PNG bodies are not quotes.

## Copy (demo fence)

Industry method: examples from the brand card, generate many, filter.

- `CHAT_ASK = 8`, keep `MIN_DRAFTS..MAX_DRAFTS` (2–3)
- `_is_postable` rejects stage notes (`soft close`, `no miracle talk`, …)
- Templates exist so empty chat still walks
- Disease names blocked in strategist/copywriter

Craft review (`craft.py`) is a second Grok pass, writer ≠ this pass. Chat failure → craft PASS (do not freeze the belt). Human is still the last yes/no.

## Image

```text
visual_prompt(draft)     4:5 Instagram beauty ad, white lid, aqua gel, marble
                         lighting_from_caption keywords only (no caption leak)
ImagineImageGen          aspect_ratio 4:5, 90s
apply_locks              Neutrogena: Pillow wordmark + disclaimer bar
                         Lays: tiny unofficial legal only (no second wordmark)
                         canvas 1080×1350
```

Do not send SVG text to Imagine (it vanished; we painted a blue blob). Do not `object-fit: cover` a square into the phone frame (it cropped the bar). CSS: `.ig-photo` `aspect-ratio: 4/5; object-fit: contain`.

## Spec drift (known)

| Spec / plan says | Live truth |
|---|---|
| ALL-BOXES: “locked design, not built” | Demo is built on this branch |
| Spine: “still no app code” | `apps/api` + `apps/web` exist |
| Plan path `apps/api/belt/` | File is `apps/api/boxes/belt.py` |
| Plan UI: Fetch → Grid → … | Walk is Look → Pick → Make → Your call → Preview |
| Image stub until HTTP pasted | Mode `imagine` is first-class; `.env.example` defaults to it |
| Chat = Gemini/Groq | Default `CHAT_MODEL=xai/grok-4.6` |
| Researcher 90s / 6 GETs | Radar research 35s / 3 GETs |
| Factory paints with copy | Paint is a later button |

When you change a box, update this table if you create new drift. Do not rewrite history in the 2026-08-19 spec files beyond a one-line status banner.
