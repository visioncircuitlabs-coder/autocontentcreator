# Task 6 — Brand Book + Product Facts fixtures

## 1. Identity

| | |
|---|---|
| **Task** | 6 |
| **Plan heading** | Task 6: Brand Book + Product Facts fixtures (`docs/superpowers/plans/2026-08-19-demo.md`) |
| **Boxes** | Box 4 — Brand Book (`docs/superpowers/specs/2026-08-19-brand-book.md`); Box 5 — Product Facts (`docs/superpowers/specs/2026-08-19-product-facts.md`) |
| **Range** | `a78d457..3229c81` |
| **Commit** | `3229c813dfd3808bb9ba4855f7a74a9af8b50dfa` `feat: brand book and claims fixtures` (2026-08-19 23:45 IST) |
| **Fix commit** | none (no Important/Critical; review clean on the feat commit) |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` on `feat/foolproof-design` |
| **Implementer agent id** | UNKNOWN |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | Task complete; review clean; minors deferred (unused loggers; tautological approved-filter assert) |

## 2. What the user would see

The demo now has a Neutrogena-**like** voice book and a claims library, both stamped unofficial / not Kenvue-approved. Later copy can pull only the India × Instagram (or LinkedIn) slice, with a citation, and can be checked against allowed “dermatologist tested” versus banned “cures acne”, “heals”, and “#1 sunscreen.” No new page. A US query does not get India cards.

## 3. The problem this task was solving

Layer 1 radar (Tasks 3–5) can fetch, score, and file a trend. Layer 3 factory cannot write claim-safe copy without (a) a voice slice that is **not** the whole book and (b) a claims matrix the judge compares to — not an LLM asked “is this legal?”

Task 7 Hard Rules + Judge call `compare_claims`. Task 8 Brief calls `query_brand` and packs claims. Task 9 compositor uses `logo.svg` + `disclaimer.txt` (created here, unused until then). Product Facts stays a separate shelf from Brand Book (voice ≠ legal claims).

## 4. Constraints that were already locked

Quoted:

> Fixture claims (unofficial demo, labeled as such): approved “dermatologist tested”; forbidden “cures acne”, “heals”, “#1 sunscreen”.
> `query_brand(market, channel) -> slice + citations`
> `compare_claims(text: str) -> list[{span, claim_id, status}]`
> Implement loaders + compare (exact + simple lookalike).
> — plan Task 6

> Pilot brand fixture: Neutrogena (unofficial).
> — plan Global Constraints

> A copywriter queries this. They do not receive the whole book pasted into a prompt.
> Scope: Neutrogena India cannot pull Listerine US voice notes.
> Humans are the only editors of **canonical** rules.
> Forbidden: … One global search across all brands. Pasting the whole book into every prompt. Filing an agent’s answer back as if it were a source.
> — Brand Book spec

> **Compare, don’t ask “is this legal?”** (Writer). … **Do not** buy Veeva for a beauty pilot or treat AdCompliance.in as clearance.
> **Forbidden:** model-invented claims; 2019 lines sneaking back.
> — Product Facts spec

> Benefit claims: 100% human yes in the demo.
> — plan Global Constraints

> The reference pitch deck is a **reference**, not the spec.
> — `CLAUDE.md` gotchas

> Cerebras in this project means two different things. **Company Brain** = Cerebras Knowledge (how we build Brand Brain). … Demo does not call it.
> — `CLAUDE.md` + index one-line rulings

## 5. Options considered

### A. Do nothing / invent claims inside the copywriter later

- **Would give:** skip fixtures; Task 8 templates could hard-code a caption.
- **Cost:** Task 7 has nothing to compare; no unofficial label; lawyer cannot open a library. Spec Forbidden: model-invented claims.
- **Lost because:** Memory layer is two boxes, locked, and Task 7/8 depend on the functions.

### B. Embeddings / vector “lookalike” for claims

- **Would give:** catch paraphrase (“gets rid of pimples for good”) without listing variants.
- **Cost:** a model + index on a demo that must run with empty keys; false friends; looks like “AI, is this legal?”
- **Lost because:** plan said “exact + simple lookalike”; Product Facts spec is **compare** to verbatim objects; implied-claim paraphrase is Task 7’s optional LLM pass (`IMPLIED_SYSTEM` in `judge.py`). SOTA reject: “AI, is this legal?”

### C. HTTP endpoints now (`GET /brand`, `POST /claims/compare`)

- **Would give:** a stranger can curl the slice without importing Python.
- **Cost:** API surface before Command Center; another place to forget the unofficial header.
- **Lost because:** Tasks 4–5 set the pattern — public functions, belt/UI later (Task 11). Same ruling here.

### D. Real Kenvue / Neutrogena brand book and legal claims

- **Would give:** a more impressive demo in a Kenvue room.
- **Cost:** we do not have that license; shipping their marks as if approved is the failure mode the unofficial stamp exists to prevent.
- **Lost because:** plan and `CLAUDE.md` say unofficial Neutrogena fixture. PPTX is not the spec.

### E. Paste the whole `brand.json` into every later prompt

- **Would give:** simpler `query_brand`.
- **Cost:** India cards leak to US; LinkedIn slang on Instagram; spec Forbidden.
- **Lost because:** `query_brand` filters `market` + `channel` (`*` = all channels in that market) and always returns `citations`.

## 6. Decision

Two loaders, no HTTP, no embeddings, no Cerebras Knowledge call.

| File | Role |
|---|---|
| `apps/api/fixtures/neutrogena/brand.json` | IN Instagram / LinkedIn / visual-`*` cards + `disclaimer` |
| `apps/api/fixtures/neutrogena/claims.json` | four claim objects + `lookalikes` |
| `apps/api/fixtures/neutrogena/disclaimer.txt` | locked market string for later hard-rules / art |
| `apps/api/fixtures/neutrogena/logo.svg` | stub mark (`NEUTROGENA*` + unofficial line) for Task 9 overlay |
| `apps/api/boxes/brand_book.py` | `load_brand`, `query_brand(market, channel) -> {slice, citations, disclaimer, market, channel}` |
| `apps/api/boxes/product_facts.py` | `load_claims`, `load_claim_models`, `compare_claims(text) -> [{span, claim_id, status}]` |
| `apps/api/tests/test_facts.py` | forbidden / approved / lookalike / scope / unofficial labels |
| `apps/api/models.py` | Unchanged `Claim` (Task 2) |

`compare_claims` reads **raw JSON** (so `lookalikes` stay available). `load_claim_models` maps rows onto `Claim` for later judge/persist; unused by compare itself. Task 7 later imports `load_claim_models` — that is after this task’s close.

## 7. Why this exact shape

### Unofficial Neutrogena labeling

Every user-facing fixture string says unofficial / not Kenvue-approved:

- `brand.json:2-3` — `"disclaimer": "UNOFFICIAL DEMO fixture — not Kenvue-approved…"`; `"brand": "Neutrogena (unofficial demo)"`
- `claims.json:2-3` — same idea for claims; “Do not ship as real legal copy.”
- `disclaimer.txt:1` — `UNOFFICIAL DEMO — not Kenvue-approved.`
- `logo.svg` `aria-label` + on-image text `*unofficial demo — not Kenvue-approved`
- `query_brand` copies the book disclaimer onto every returned slice (`brand_book.py:41`, `64`, `80`)
- `test_fixtures_labeled_unofficial` reads brand/claims/disclaimer and asserts the words

This is not decoration. The pilot brand is Neutrogena **like**. A reviewer who opens `logo.svg` must not think it is brand-legal artwork (Task 6 report concern #5).

### Approved “dermatologist tested”

`claims.json` `claim_id=approved-derm-tested`, `status=approved`, `sku=DEMO-HYDRO-BOOST`, `market=IN`, lookalikes `dermatologist-tested` / `dermatologist–tested` / `derm tested`. `test_compare_dermatologist_tested_is_approved` hits the exact phrase.

### Forbidden “cures acne” / “heals” / “#1 sunscreen”

Three forbidden objects, `sku=*`, with listed lookalikes (`cure acne`, `acne cure`, `heal`/`healed`/`healing`, `number 1 sunscreen`, `no.1 sunscreen`, …). Tests:

- `test_compare_cures_acne_is_forbidden` — span contains “cures acne”
- `test_compare_lookalike_heals_is_forbidden` — `"This cream Heals! dry patches fast."`
- `test_compare_number_one_sunscreen_forbidden` — `"#1 sunscreen"`

These are the same tokens Hard Rules will also list (Task 7). Product Facts is the **library compare**; Hard Rules is the unbribable token list. Both exist on purpose.

### `query_brand` slice + citations

`query_brand` (`brand_book.py:28-83`):

- uppercases market, lowercases channel
- keeps a card only if `card.market == market` **and** `card.channel` is the requested channel or `*`
- never returns the whole `cards` array
- every kept card appends a citation `{card_id, source_ref, market, channel, verify_state}`
- empty slice for `market="US"` (`test_query_brand_scopes_market`) — India cannot silently serve as US
- `test_query_brand_returns_slice_and_citations` requires non-empty IN/instagram slice **and** citations **and** unofficial text in the blob

Cards carry `verify_state` and `expires_at` (Guru-shaped) but **query does not filter expired** (concern #3). Enough for a 2026-08 demo; production Brand Brain must treat unverified/expired as non-law.

No Cerebras Knowledge ingest. Demo is JSON on disk. Production adapter swap is “Cerebras Knowledge pattern: ingest Docs/DAM, distill, hybrid retrieve” — not this commit.

### `compare_claims` exact + lookalike

`_normalize` lowercases, collapses whitespace, unifies en/em dashes (`product_facts.py:25-30`). `_pattern_for` splits on space/hyphen, joins with `[\s\-]+`, wraps `(?<!\w)…(?!\w)` so `heals` does not match `wheels` (`product_facts.py:33-43`). Each claim’s `text` plus `lookalikes[]` are searched in the **original** text (span is the actual substring). Overlaps: longer span wins, then earlier start; one hit per `claim_id` (`product_facts.py:107-135`).

That is “simple lookalike”: case, punctuation (`Heals!`), dashes, listed variants. Not embeddings. Not implied claims (“this gel makes acne history”).

### Why no embeddings

1. Plan Task 6: “exact + simple lookalike.”
2. Product Facts spec: compare to objects; do not ask the model if it is legal.
3. SOTA: reject “AI, is this legal?”; Writer-shaped comparison is string-to-library.
4. Implied paraphrase is explicitly Task 7 (`judge.py` `IMPLIED_SYSTEM`, FTC 2022) and is optional when `chat` is missing.
5. Demo has no pgvector / embedding model; spine production lists Postgres+pgvector later.
6. An embedding “close to ‘cures acne’” would invent a match without a `claim_id` in the library — the opposite of harvest-on-approve.

### Why no HTTP

Same belt-first ruling as scorer/researcher: public functions for later boxes. `main.py` has no brand/claims routes (grep empty at Task 6). Task 11 wires the story. Adding HTTP here would have been extra surface before anyone can click it, and it is not in the Task 6 file list.

## 8. What we refused

- Veeva, Writer, Saifr, AdCompliance.in as clearance, Glean, Frontify MCP, Cerebras Knowledge live ingest.
- Model-edited canonical rules; filing a model answer as a source.
- One global search across brands/markets.
- Pasting `brand.json` into every prompt.
- Embedding lookalikes; an LLM “is this legal?” endpoint.
- Real Neutrogena legal claims or brand-legal logo.
- Factory boxes, Hard Rules, Judge, Command Center pages (left to Tasks 7–11).
- Enforcing `expires_at` / `verify_state` in `query_brand` (cards still carry the fields).

## 9. Verification that actually ran

**Seen in the implementer report** (this documentation pass did not re-run pytest):

```text
.\.venv\Scripts\python.exe -m pytest tests/test_facts.py -q
7 passed in 0.36s

.\.venv\Scripts\python.exe -m pytest tests/ -q
55 passed in 0.85s
```

| Test | Asserts |
|---|---|
| `test_compare_cures_acne_is_forbidden` | span contains “cures acne”; status forbidden |
| `test_compare_dermatologist_tested_is_approved` | approved hit; see tautology in §10 |
| `test_compare_lookalike_heals_is_forbidden` | “Heals!” matches forbidden heals |
| `test_compare_number_one_sunscreen_forbidden` | “#1 sunscreen” forbidden |
| `test_query_brand_returns_slice_and_citations` | non-empty slice + citations + unofficial |
| `test_query_brand_scopes_market` | US query does not cite IN cards |
| `test_fixtures_labeled_unofficial` | brand/claims/disclaimer wording + `logo.svg` exists |

**Claimed, not seen here:** compose walk; any HTTP hit; expiry filtering; `load_claim_models` behavior (no test in `test_facts.py`). Downstream use in Task 7/8 is **after** this task.

## 10. Review findings and rulings

Review package: `review-a78d457..3229c81.diff`. No fix commit.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| Important | none in ledger | — | — |
| Critical | none in ledger | — | — |
| Minor | unused `logger` in `brand_book.py` and `product_facts.py` | deferred | both files still `logger = logging.getLogger(__name__)` with no `logger.*` call |
| Minor | tautological approved filter assert | deferred | `test_facts.py:21-23`: `approved = [h for h in hits if h["status"]=="approved"]` then `assert all(h["status"]=="approved" for h in approved)` — the useful assert is the span check on line 22 |

Progress.md: “Task 6: complete (commits a78d457..3229c81, review clean).” Exact reviewer prose UNKNOWN.

Implementer concerns (not raised as Important): lookalike is regex-only; no HTTP; expiry not enforced; `load_claim_models` unused by compare; logo is a stub SVG.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Regex lookalike only (no implied-claim) | Task 7 judge optional LLM pass |
| No HTTP | Task 11 Command Center |
| `expires_at` / `verify_state` not filtered in `query_brand` | production Brand Brain; or a later Task 8 brief guard |
| Unused loggers | cleanup whenever those files are next touched |
| Tautological assert in `test_compare_dermatologist_tested_is_approved` | same; replace with “no forbidden hits in that sentence” if retouched |
| `load_claim_models` unused **at Task 6 close** | Task 7 `judge.py` / `loop.py` (now uses it) |
| Logo is not brand-legal; compositor must keep unofficial label visible | Task 9 Art Director |
| No `conditional` fixture row | Task 7 added judge behavior for conditional; library still approved+forbidden only |
| Disclaimer/logo files unused until later boxes | Task 7 hard-rules / Task 9 art |

## 12. Third-party check list

1. Open `apps/api/fixtures/neutrogena/brand.json`, `claims.json`, `disclaimer.txt`, `logo.svg` — unofficial / not Kenvue in each.
2. `claims.json` — exactly those four statuses: approved dermatologist tested; forbidden cures acne / heals / #1 sunscreen.
3. `apps/api/boxes/brand_book.py:50-54` — market must match; channel must be requested or `*`.
4. `apps/api/boxes/product_facts.py:33-43` — word-ish boundaries; no embedding import (`grep` the file for `embed` / `openai` / `numpy`: empty).
5. `apps/api/boxes/product_facts.py:89-105` — iterates `text` + `lookalikes`, not a model.
6. `apps/api/tests/test_facts.py` — `pytest tests/test_facts.py` from `apps/api`.
7. `apps/api/main.py` — no brand/claims route.
8. `query_brand("US","instagram")["slice"]` is `[]` (test or a one-liner).
9. Git: `git show 3229c81 --stat` — the seven files in §6; no `apps/web` change.
10. Confirm Task 7 `boxes/judge.py` imports `compare_claims` (dependency this task unlocked) without this task having implemented the judge.
