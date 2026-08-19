# Task 8 — Brief, Strategist, Copywriter

**Status:** filled (pending re-review). Feat `991d9cb` and fix `750a86b` are on the branch. The fix package `review-991d9cb..750a86b.diff` exists. `.superpowers/sdd/2026-08-19-demo/progress.md` has **no Task 8 line** after Task 7 closed — no “review clean,” no agent ids. Treat the two Important items as addressed by the implementer, not as re-accepted by a reviewer.

## 1. Identity

| | |
|---|---|
| **Task** | 8 |
| **Plan heading** | Brief, Strategist, Copywriter (`docs/superpowers/plans/2026-08-19-demo.md`, “Task 8”) |
| **Boxes** | 8 Brief Builder, 9 Strategist, 10 Copywriter (plus the Task 7 loop socket this task fills) |
| **Branch / worktree** | `feat/foolproof-design` at `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Base** | `11e40f05777c9affbb3e34e9243d4c8522ca52fd` `fix: judge conditional claims and implied skip flag` |
| **Feat** | `991d9cb4e5972c3c1048e80a9e5ab85ea49626f4` `feat: brief strategist copywriter` (2026-08-20 00:14 IST) |
| **Fix** | `750a86be638cb3f23243ccb8e8f93a601591f1bb` `fix: copywriter uses judge reasons without chat` (2026-08-20 00:22 IST) |
| **Head** | `750a86b` (also `HEAD` of this worktree at time of writing) |
| **Author on git** | `vision <visioncircuitlabs@gmail.com>` |
| **Implementer agent id** | UNKNOWN |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/task-8-report.md` (feat + “Fix round 1/5”). `progress.md` does **not** record this task. |
| **Review packages** | `review-11e40f0..991d9cb.diff`, `review-991d9cb..750a86b.diff` |
| **Re-review** | **Not done** (or not recorded). Open items below. |

## 2. What the user would see

Still nothing in the Command Center. If a later belt hands this task a stored trend report, the machine packs a brief without calling a model, invents a small grid of concepts (angle, who it’s for, everyday skin-feel, channel, Hindi/Hinglish/Roman), and writes two or three captions that stay on the approved phrase and the fixture disclaimer. Disease names such as PCOS are not allowed as a “pain.” If the judge sent numbered reasons, the next captions are edits of the seed, not a brand-new post. With no API key, template captions still appear so the demo can walk.

## 3. The problem this task was solving

Radar (Tasks 3–5) and memory fixtures (Task 6) can produce a report and a claims library. Task 7 can gate a draft. Nobody could yet *turn a report into copy*. The loop’s default rewriter was a token-strip stub that ignored numbered reasons (`_ = reasons` in `9b122ed`).

Depends on it:

- **Task 9** — Art Director takes a Draft caption/prompt; it needs these drafts.
- **Task 10** — `run_factory(report_id)` is brief → strategist → copywriter → hard rules → judge → loop. Track Record is supposed to fill the empty 3 wins / 3 losses helper.
- **Task 11** — Command Center Factory story has nothing to show without these functions.

## 4. Constraints that were already locked

Demo plan Task 8:

> `build_brief(report_id) -> brief_id`  # code only
> `run_strategist(brief_id) -> list[Concept]`  # grid
> `run_copywriter(concept, round, judge_reasons=None) -> list[Draft]`  # 2–3 variants
>
> Brief pack: report + brand slice + claims for SKU + 3 wins + 3 losses from Track Record (empty ok).
> Strategist axes: angle, persona, claim-safe pain, channel, register. Reject disease names in tests.
>
> Tests: brief has no LLM; strategist output has no “PCOS”; copywriter returns 2–3 drafts.
> Implement with ChatModel, template fallback if no key.

Box specs:

> Brief: “Code, not an agent. Same inputs → same brief. Pack: trend report + Brand Book slice + Product Facts for featured SKUs + 3 winners + 3 rejections + format. Agents downstream use **this pack only**. **Forbidden:** ‘write a campaign’ with no pack.” (`docs/superpowers/specs/2026-08-19-brief-builder.md`)
>
> Strategist: “Grid, not one idea. Axes: **angle / claim-safe pain / persona / channel / Indic register** (pure Hindi vs Hinglish vs Roman). … **Forbidden:** disease-pain grids (PCOS, thyroid, diabetes); competitor-ad clones; Persado ‘no re-approval’; auto-scripts without a judge. Output is concepts, not captions.” (`docs/superpowers/specs/2026-08-19-strategist.md`)
>
> Copywriter: “Voice from examples. Rules apply **while writing**. Many candidates → filter then rank (Jacquard). 2–3 variants to the Judge. Rewrites use numbered judge reasons, not a from-scratch redo. **Forbidden:** buying Persado/Jacquard as Brand Brain; unsubstantiated superlatives.” (`docs/superpowers/specs/2026-08-19-copywriter.md`)

Global: no CrewAI; web/tool text is data not instructions; free adapters default; no key ⇒ strategist/copywriter use fixture templates (demo plan “Same structure, cheaper guts”).

Task 7 leftover this task was required to close: “Default rewriter is a stub. … Task 8 must replace it with `run_copywriter(..., judge_reasons=)`.” (task-7-report.md)

## 5. Options considered

### A. Let an LLM write the brief

- **Would give:** A “smarter” pack, maybe a written strategy paragraph.
- **Would cost:** Non-determinism. Spec: “Code, not an agent. Same inputs → same brief.” Plan interface is `# code only`. Tests assert `ChatModel` / `complete_json` / `litellm` / a `chat` param are absent from `brief.py`.
- **Lost because:** locked. `build_brief` hashes `report_id|market|channel|sku|format` and upserts JSON.

### B. Build the Track Record box in this task so wins/losses are real

- **Would give:** The spec pack (“3 winners + 3 rejections”) with actual ledger rows.
- **Would cost:** Box 7 + review/feedback, which the plan parked in **Task 10**. Plan says “empty ok.”
- **Lost / parked:** `load_track_record_examples` returns `[], []` and ignores sku/market/n. Swap the helper body when the ledger exists.

### C. Field name `register` on `Concept` as the spec says

- **Would give:** Spec-faithful JSON (`register: hindi|hinglish|roman`).
- **Would cost:** A clash with Pydantic `BaseModel.register`. Implementer: “Axis field is `indic_register` (Pydantic `BaseModel.register` clash).”
- **Lost as a Python name.** JSON from chat still accepts `"register"` via `AliasChoices("indic_register", "register")` on `ConceptOut` (`strategist.py:65`). Domain model field is `indic_register`.

### D. Put the DMROA disease list on Hard Rules (Task 7 leftover) instead of a writer-side token filter

- **Would give:** Unbribable disease blocking at the gate, matching the Hard Rules spec.
- **Would cost:** Expanding Task 7’s gazette in a task that was not allowed to reopen Hard Rules’ contract beyond what copywriter needed (`strip_banned_tokens` moved for reuse).
- **What shipped:** `DISEASE_TOKENS` on the strategist (`pcos`, `pcod`, `polycystic`, `thyroid`, `hypothyroid`, `hyperthyroid`, `diabetes`, `diabetic`, `cancer`, `endometriosis`, `hiv`). Copywriter drops any caption `contains_disease`. **Hard rules still do not scan disease names.** A PCOS caption that never goes through the writers can pass Task 7. See Deferred.

### E. Chat-only rewrite (what `991d9cb` effectively tested)

- **Would give:** The model “fixes” the seed when a key exists; templates cover the no-key path.
- **Would cost:** Numbered reasons would not actually edit a seed without chat. The first test used seed `"This gel cures acne overnight."` and reason `"cures acne"` — `strip_banned_tokens` would drop “cures” even if reasons were ignored. That does not prove Skadoosh.
- **Lost because:** review Important. `750a86b` adds `apply_judge_reasons` (quoted replace pairs, then quoted spans dropped) and retests with `"Miracle glow water"` + `chat=None`, asserting “Monday light” survives.

### F. Do not thread `run_loop(..., chat=)` into the copywriter

- **Would give:** Chat used only for the judge’s implied pass (Task 7 behavior). Copywriter templates always.
- **Would cost:** One factory `ChatModel` could not rewrite; the copywriter would never see `<reasons>` inside the loop.
- **Lost because:** review Important. `750a86b` wraps `default_rewrite(..., chat=chat)` when `rewriter is None`. Custom `rewriter=` is unchanged.

### G. Do nothing / leave the stub rewriter until the belt (Task 10)

- **Would give:** Less coupling; Task 10 could wire copywriter once.
- **Would cost:** Plan order and the Task 7 concern that Task 8 *must* replace the stub. Loop tests after this task assert `default_rewrite` calls `rewrite_draft`.
- **Lost because:** the plan.

### H. Buy Persado / Jacquard / Writer as the copy brain

- **Would give:** Vendor voice + “filter then rank” as a product.
- **Would cost:** Locked “do not buy as Brand Brain.” Demo budget is free adapters.
- **Lost because:** locked. Rank in this task is a tiny “has approved phrase, length near 320” sort (`copywriter.py:265-272`).

## 6. Decision

Factory text path only. No Art Director, no belt, no Command Center, no Track Record box.

```text
report_id
  ├─ build_brief (code)     report + brand slice + SKU claims + 3 wins + 3 losses
  │                            wins/losses empty until Track Record
  ├─ run_strategist         grid: angle × persona × claim-safe pain × channel × indic_register
  │                            ChatModel optional; disease names stripped; templates fill
  └─ run_copywriter         2–3 Draft variants; rewrite from numbered judge reasons
                                │
                                ▼
                           loop.default_rewrite → rewrite_draft(..., chat=chat)
```

| Piece | Role |
|---|---|
| `apps/api/boxes/brief.py` | `build_brief` → `brief_id`. `load_track_record_examples` → `[], []`. |
| `apps/api/boxes/strategist.py` | `run_strategist` → `list[Concept]` (3–6). |
| `apps/api/boxes/copywriter.py` | `run_copywriter` → 2–3 `Draft`; `rewrite_draft` for the loop; `apply_judge_reasons` (no model). |
| `apps/api/models.py` | `Concept`, `Brief` (not in the plan’s locked type block). |
| `apps/api/db.py` | `briefs` table; `get_report`, `upsert_brief`, `get_brief`. |
| `apps/api/boxes/hard_rules.py` | `strip_banned_tokens` moved here from the Task 7 loop stub (reuse). |
| `apps/api/boxes/loop.py` | Default rewriter is the copywriter; `chat` threads through. |
| `apps/api/tests/test_factory_text.py` | no-LLM brief / no PCOS / 2–3 drafts / reasons without chat / loop chat. |

## 7. Why this exact shape

### Brief is code-only

`build_brief` (`brief.py:67-103`) loads the stored `TrendReport`, `query_brand(market, channel)`, `_claims_for_sku`, and `load_track_record_examples`. No `chat` argument; module source must not mention `ChatModel` / `complete_json` / `litellm` (test). Same inputs → same `brief_id`: `brf_` + sha256 of `report_id|market|channel|sku|format` (`brief.py:62-64`). Pack is a `Brief` Pydantic object persisted as JSON in SQLite.

`load_track_record_examples` (`brief.py:21-28`) is a named helper with the right signature so Task 10 can replace the body. It currently returns empty lists on purpose. `_ = (sku, market, n)`.

Defaults: market `IN`, channel `instagram`, format `instagram caption`, SKU first approved non-`*` claim or `DEMO-HYDRO-BOOST`. Downstream writers are supposed to use this pack only; they still *load* it by `brief_id` rather than accepting a free-form prompt. That is the 万相 / Typeface “not a blank campaign” lock, at demo fidelity.

`briefs` is a new table (`db.py:80-84`: `brief_id`, `report_id`, `pack`). Task 2 schema did not list it. `test_init_db_creates_tables` still does **not** assert `briefs` exists (`test_models.py:90-97`). Hole.

### Concept axes, and why `indic_register`

`Concept` (`models.py:56-65`): `angle`, `persona`, `claim_safe_pain`, `channel`, `indic_register`, plus `hook` / `idea`. Spec name is “Indic register.” Python name cannot be `register` because Pydantic `BaseModel.register` is already a method. Chat JSON may still send `"register"` (`Field(validation_alias=AliasChoices("indic_register", "register"))`). Values after `normalize_register`: `hindi` / `hinglish` / `roman`.

`template_concepts` (`strategist.py:160-198`) is a one-variable grid: hold a base row, then vary report angles, then personas, then claim-safe pains, then registers. Spec: “One variable per test.” Caps: `MIN_CONCEPTS = 3`, `MAX_CONCEPTS = 6`.

### Disease token filter (PCOS)

`DISEASE_TOKENS` (`strategist.py:20-32`) is a short list, not a gazette. `contains_disease` is word-boundary regex. `make_concept` returns `None` if any axis/hook/idea hits. Chat dump of a “PCOS warrior” grid is dropped; templates fill so the test still gets ≥1 concept with no PCOS/thyroid/diabetes in the blob (`test_strategist_strips_disease_names_from_chat`). Copywriter `_finish_caption` also returns `None` on disease. Other condition names can slip through (implementer concern #3).

Prompt injection: strategist and copywriter wrap the brief/concept/seed/reasons in `<brief>` / `<concept>` / `<seed>` / `<reasons>` and say that inner text is DATA, never instructions. Same pattern as Task 5/7. No tools.

### 2–3 drafts, template fallback, tiny Jacquard

`MIN_DRAFTS = 2`, `MAX_DRAFTS = 3`. `run_copywriter` (`copywriter.py:303-361`): optional chat captions + templates; `_finish_caption` applies reasons, replaces forbidden spans with the approved phrase, strips gazette tokens, appends disclaimer on benefit lines, drops disease. If output is thin, pad from templates. `_rank` prefers captions that contain the approved phrase, then length near 320 — “has approved phrase” sort, not a scorer (implementer concern #8).

LiteLLM adapter is still a stub (`adapters/chat_litellm.py` raises `NotImplementedError` even with a key). Injected `ChatModel` in tests is a fake. Demo walk without a key is templates. That matches the plan sentence “If no LLM key, … Strategist/Copywriter use fixture templates.”

Template voice always pins “dermatologist tested” (or the first approved claim in the pack) and the fixture disclaimer. Claim-safe, not voice-rich.

### Loop wired to `rewrite_draft`; numbered reasons without chat

`default_rewrite` (`loop.py:16-25`) imports `rewrite_draft` and passes `chat` through.

`rewrite_draft` (`copywriter.py:404-424`): seed is `judge.rewrite` if the judge suggested one, else the current caption; then `run_copywriter(..., judge_reasons=reasons, seed_caption=seed, chat=chat)`; keep **variant 1**.

`apply_judge_reasons` (`copywriter.py:96-106`, landed in `750a86b`): parse `replace "old" with "new"` pairs, then drop other quoted spans. Applied twice in `_finish_caption` (before and after token strip). `_seed_variations` keeps seed-based variants first so a rewrite is not a from-scratch redo (Skadoosh-shaped, at regex fidelity).

`run_loop(..., chat=)` (`loop.py:38-41`): when `rewriter is None`, the inner function calls `default_rewrite(..., chat=chat)` so the same model object sees judge `ImpliedClaimOut` **and** copywriter `CopyOut`. Custom `rewriter=` does not get chat (unchanged callback type `Callable[[Draft, list[str]], Draft]`).

## 8. What we refused

- **LLM brief / blank “write a campaign.”**
- **Track Record box, Art Director, belt, Command Center pages** — out of this task’s files list.
- **Persado, Jacquard, Copy.ai, Writer as Brand Brain.** Steal filter-then-rank; do not buy it.
- **Disease-pain grids** (PCOS / thyroid / diabetes) as marketing angles.
- **Persado “no re-approval.”** Benefit claims stay 100% human-yes.
- **Spending the ~$5 show budget.**
- **HTTP endpoints.** Public surface is `build_brief` / `run_strategist` / `run_copywriter` for the later belt.
- **Renaming Pydantic away** to keep the spec field `register` as a Python attribute. Alias instead.
- **Full DMROA gazette** on this pass. Token filter on the writers only.

## 9. Verification that actually ran

**Claimed** in task-8-report.md from `apps/api` local `.venv`. This documentation agent did **not** re-run pytest. No compose, no live model.

After `991d9cb` (claimed):

```text
pytest tests/test_factory_text.py tests/test_loop.py -q
11 passed
pytest tests/ -q
80 passed
```

After `750a86b` (claimed):

```text
pytest tests/test_factory_text.py tests/test_loop.py -q
12 passed
pytest tests/ -q
81 passed
```

| Test | What it would fail on |
|---|---|
| `test_brief_module_has_no_llm` | `ChatModel` / `complete_json` / `litellm` / `chat` param in brief |
| `test_build_brief_packs_report_brand_claims_and_empty_track` | missing report/brand/claims, or wins/losses not `[]` |
| `test_build_brief_is_deterministic` | same report_id yields different `brief_id` |
| `test_strategist_grid_has_no_pcos` | <3 concepts, missing axes, or PCOS/thyroid/diabetes in the grid |
| `test_strategist_strips_disease_names_from_chat` | fake PCOS grid leaks into output |
| `test_copywriter_returns_two_to_three_drafts` | not 2–3 Drafts, or “cures”/PCOS in captions |
| `test_copywriter_rewrite_uses_numbered_reasons` | `chat=None` still contains “Miracle glow water”, or seed “Monday light” discarded |
| `test_loop_threads_chat_to_copywriter` | FakeChat never sees `CopyOut` (only judge `ImpliedClaimOut`) |
| `test_loop_default_rewrite_uses_copywriter` | `default_rewrite` source lacks `rewrite_draft` / `run_copywriter`; “cures” remains |

**Not seen:** a real LiteLLM/Gemini call; replace-pair branch of `_REPLACE_RE` (test only drops a quoted span); `briefs` table in `test_init_db_creates_tables`; compose.

pycache under `apps/api/tests/` shows these tests were executed on this machine at some point; that is not the same as a recorded re-review.

## 10. Review findings and rulings

Original reviewer prose is **not** in the committed pack. Reconstruction from `750a86b`, the fix-round table in task-8-report.md, and the test diff. **Re-review of `750a86b` is not recorded.**

After `991d9cb`: **DONE_WITH_CONCERNS**. Reviewer package: `review-11e40f0..991d9cb.diff`.

| Severity | Finding (as recorded by the fix) | Ruling (as implemented) | Outcome |
|---|---|---|---|
| Important | Numbered judge reasons did not edit a seed unless chat (or a banned token) did the work. The `"cures acne"` test could go green via `strip_banned_tokens` alone. Spec: “Rewrites use numbered judge reasons, not a from-scratch redo.” | `apply_judge_reasons` must work with `chat=None`. Seed-based variants stay first. Test with a span that is **not** a banned token (`"Miracle glow water"`) and assert the rest of the seed (`Monday light`) remains. | **Claimed fixed** in `750a86b`. **Not re-reviewed.** |
| Important | `run_loop(..., chat=)` reached the judge implied pass only. Default copywriter rewrite never saw the model. | Pass that `chat` into `default_rewrite` → `rewrite_draft`. Custom `rewriter=` unchanged. Test: FakeChat must observe `CopyOut` as well as `ImpliedClaimOut`. | **Claimed fixed** in `750a86b`. **Not re-reviewed.** |
| Critical | none recorded | | |
| Parked / out of scope | Art Director; Track Record box | Stay out | Honored in both commits (files list). |

Implementer self-concerns (not reviewer Important, still true after the fix):

1. Track Record helper always empty.
2. LiteLLM adapter still a stub.
3. Disease filter is a token list, not DMROA.
4. `indic_register` vs spec `register` (alias on the way in).
5. No HTTP.
6. Template copy is claim-safe, not voice-rich.
7. `briefs` table was not in the Task 2 schema.
8. Rewrite keeps variant 1; rank is tiny.

Open for whoever runs the `991d9cb..750a86b` re-review: confirm the two Important items with the new tests; decide whether writer-only disease filtering vs Hard Rules gazette is acceptable for the demo; decide whether untested `_REPLACE_RE` and missing `briefs` in `test_init_db_creates_tables` are minors or must-fix.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Re-review of `750a86b` not closed in the SDD ledger | controller / reviewer (this file stays “pending re-review” until that happens) |
| `load_track_record_examples` always `[], []` | **Task 10** (Track Record + feedback harvest) |
| Disease names not on `run_hard_rules`; only strategist/copywriter | leftover vs Hard Rules spec; production gazette |
| Other condition names outside `DISEASE_TOKENS` | production |
| LiteLLM `complete_json` still `NotImplementedError` | leftover; templates walk the demo |
| `_REPLACE_RE` replace-pair path untested (drop-span is tested) | leftover test |
| `test_init_db_creates_tables` does not include `briefs` | leftover test |
| Rank / “keep variant 1” is not Jacquard | leftover / production copy |
| No HTTP, no Factory UI | **Task 10 / 11** |
| Caption carries the full fixture disclaimer until overlay | **Task 9** |
| `flag_human` still not in SQLite (Task 7 park) | **Task 10** |
| Conditional claims still absent from `claims.json` | leftover fixture content |
| `implied_check=ran` still untested (Task 7 minor) | leftover |

## 12. Third-party check list

Under 15 minutes:

1. `git log --oneline 11e40f0..HEAD` — expect `991d9cb feat: brief strategist copywriter` then `750a86b fix: copywriter uses judge reasons without chat`. No later Task 8 commit.
2. Open `.superpowers/sdd/2026-08-19-demo/progress.md` — confirm Task 8 is **missing**. That is why this journal is pending re-review.
3. `apps/api/boxes/brief.py` — no `chat` argument; `load_track_record_examples` returns `[], []`.
4. `apps/api/boxes/strategist.py` — `indic_register` + `AliasChoices(..., "register")`; `DISEASE_TOKENS` includes `pcos`.
5. `apps/api/boxes/copywriter.py` — `apply_judge_reasons`; `MIN_DRAFTS/MAX_DRAFTS`; `_finish_caption` called with `reasons`.
6. `apps/api/boxes/loop.py` — `default_rewrite` calls `rewrite_draft(..., chat=chat)`; `run_loop` inner function passes `chat` only when `rewriter is None`.
7. `apps/api/models.py` — `Concept.indic_register`, `Brief`, `Draft.flag_human` still present.
8. `apps/api/db.py` — `CREATE TABLE IF NOT EXISTS briefs`; `drafts` still has no `flag_human`.
9. From `apps/api`: `pytest tests/test_factory_text.py tests/test_loop.py -q` — expect 12 passed if the claimed count still holds.
10. Read `test_copywriter_rewrite_uses_numbered_reasons` — `chat=None`, span `"Miracle glow water"`, seed keeps `"Monday light"`. If this test were still the old `"cures acne"` seed, the Important item is not closed.
11. Read `test_loop_threads_chat_to_copywriter` — `CopyOut` must appear in `seen`.
12. Confirm `apps/api/boxes/hard_rules.py` still has **no** `pcos` token. Disease blocking is not the unbribable gazette.
13. Confirm no Art Director files, no Factory routes, no Track Record module.
