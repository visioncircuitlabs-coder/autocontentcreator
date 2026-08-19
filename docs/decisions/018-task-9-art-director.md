# Task 9 — Art Director + image port

**Status:** filled (review closed). Feat `865446a` is on the branch. No fix commit. Ledger: review clean; `$5` still unspent because the stub PNG is showable.

## Locked before anyone writes code

Evidence preserved from the pre-implementation stub (same contract the implementer built against):

- `ImageGen` port: `generate(prompt, out_path) -> Path`.
- Default `IMAGE_GEN_MODE=stub`. Pillow card + headline + `logo.svg` + `disclaimer.txt` composited **in code**.
- HTTP adapter: `POST IMAGE_GEN_URL` with `{prompt, size}` and `Authorization: Bearer IMAGE_GEN_KEY`. Switch with `IMAGE_GEN_MODE=http` when the user pastes an API.
- **Never send the logo to the model.** Overlay in code.
- Free default. The optional ~$5 budget is *only* for this box, and only if the stub image is not showable enough. Do not buy Recraft/Firecrawl here unless the controller explicitly opens the budget after seeing the stub.

## 1. Identity

| | |
|---|---|
| **Task** | 9 |
| **Plan heading** | Art Director + image port (`docs/superpowers/plans/2026-08-19-demo.md`, “Task 9”) |
| **Boxes** | 11 Art Director (unlocked ImageGen + coded compositor) |
| **Branch / worktree** | `feat/foolproof-design` at `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Base** | `750a86be638cb3f23243ccb8e8f93a601591f1bb` `fix: copywriter uses judge reasons without chat` |
| **Feat** | `865446a` `feat: art director with image port` (2026-08-20; date from `task-9-report.md`) |
| **Fix** | none — no fix round |
| **Head (task closed)** | `865446a` |
| **Author on git** | UNKNOWN (this documentation agent has no shell; review package lists the SHA/message only) |
| **Implementer agent id** | UNKNOWN (not named in `progress.md` for this task) |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/task-9-brief.md`, `task-9-report.md`, `progress.md` |
| **Review package** | `review-750a86b..865446a.diff` (6 files, +537 lines) |
| **Re-review** | Not needed — no Important/Critical; Approved with minors only |

## 2. What the user would see

Still nothing new in the Command Center. If a later belt hands Art Director a draft and a picture prompt, the machine paints a dark Instagram-sized card with that prompt as the headline, then stamps the unofficial Neutrogena* mark and the fixture disclaimer on top in code. No paid image API runs. The returned draft points at a real PNG on disk. Switch to a pasted HTTP image API is possible later; it is off by default.

## 3. The problem this task was solving

Tasks 6–8 produced captions that still carried the full fixture disclaimer in the text, and drafts had `image_path=None`. Spec and plan require AI to paint **unlocked** zones only, with logo and disclaimer locked in code — not “prompt the logo into Flux/Recraft.” Without this box, Task 10’s factory belt (`… → loop → art_director → queue`) and Task 11’s Factory story have no showable card.

Depends on it:

- **Task 10** — `run_factory` wires `compose` after the loop; queued drafts need `image_path`.
- **Task 11** — Command Center Factory / Preview story needs a PNG, not a caption-only row.
- **Budget gate** — the optional ~$5 show spend is *this* slot, and only after a stub card exists and is judged not showable enough.

## 4. Constraints that were already locked

Demo plan Task 9 (`docs/superpowers/plans/2026-08-19-demo.md:338-356`):

> Interfaces:
> - `compose(draft, prompt) -> Draft` with `image_path`
> - `ImageGen.generate(prompt, path) -> Path`
>
> Stub: dark card + headline text + paste `logo.svg` + `disclaimer.txt` via Pillow.
> HTTP adapter: `POST IMAGE_GEN_URL` with `{prompt, size}` and `Authorization: Bearer IMAGE_GEN_KEY`, save bytes. Switch with `IMAGE_GEN_MODE=http` when you send the API.
>
> Never send the logo to the model. Overlay in code.

Box spec (`docs/superpowers/specs/2026-08-19-art-director.md:1-7`):

> AI paints **unlocked** zones only. Code composites logo, licensed type, locked disclaimer.
>
> **Forbidden:** prompting the registered logo; Higgsfield “locks your logo”; uploading SVG to CapCut/剪映; Recraft “generate logos.”

Global / ledger (`progress.md:4`; `docs/decisions/001-global-rulings.md` §4.1):

> free adapters are the default. ~$5 optional only if a tool clearly improves the show. Do not buy Firecrawl/Brandwatch/Recraft for the demo. IMAGE_GEN stays a port (stub default). Do not spend the $5 unless image quality is the leftover demo gap after Task 9.

Pre-code stub for this file (preserved above): same port, stub default, HTTP switch, never logo-to-model, free unless controller opens the budget after seeing the stub.

Task 6 leftover this task closes: `logo.svg` + `disclaimer.txt` were fixtures waiting for a compositor (`015-task-6-brand-facts.md` deferred holes).

## 5. Options considered

### A. Prompt the logo into the image model (Recraft / Flux / CapCut)

- **Would give:** One “pretty” PNG with brand marks baked in by the model.
- **Would cost:** Spec-forbidden (“prompting the registered logo”; “Recraft generate logos”). Unbribable lock becomes model luck. Paid call.
- **Lost because:** locked. Overlay is `apply_locks` after `generate`, never in the prompt/POST body.

### B. Spend the ~$5 on Recraft/Firecrawl day one

- **Would give:** Nicer show pictures without waiting.
- **Would cost:** Violates free-default ruling; buys a tool the production plan parks; burns the only demo spend slot before proving the stub.
- **Lost because:** stub PNG was showable (~42KB 1080×1080 with logo + headline + disclaimer). Ledger after close: “$5 image budget still unspent; stub PNG is the show default.”

### C. HTTP-only ImageGen (no Pillow stub)

- **Would give:** Real API pictures whenever a key exists.
- **Would cost:** Empty `IMAGE_GEN_*` would break the demo walk. Plan requires stub file exists and is PNG; env default is `IMAGE_GEN_MODE=stub`.
- **Lost because:** free walk is mandatory. HTTP is the optional adapter.

### D. cairo / librsvg / full SVG engine for `logo.svg`

- **Would give:** Faithful SVG (paths, gradients).
- **Would cost:** Extra native deps in Docker slim; overkill for a fixture that is only `rect` + `text`.
- **Lost / simplified:** `rasterize_logo` paints rect/text with Pillow. Fixture-shaped by design (implementer concern #1; accepted as minor).

### E. Do nothing / leave `image_path=None` until Task 10 or 11

- **Would give:** Less coupling this sprint.
- **Would cost:** Plan order; belt cannot call `art_director`; Command Center has no card; `$5` gate never opens honestly.
- **Lost because:** the plan.

### F. Adobe four-mode lock table in the demo

- **Would give:** Spec-faithful production Art Director modes.
- **Would cost:** Far beyond demo Task 9 (“dark card + overlay”).
- **Parked:** demo is two-layer — unlocked picture + coded logo/disclaimer (concern #5).

## 6. Decision

Art Director path only. No Review, Export, Belt, or Command Center pages.

```text
compose(draft, prompt)
  │
  ├─ IMAGE_GEN_MODE=stub (default) → StubImageGen.generate
  │                                    dark 1080×1080 card + headline PNG
  ├─ IMAGE_GEN_MODE=http           → HttpImageGen.generate
  │                                    POST {prompt, size} + Bearer → save bytes
  └─ apply_locks                   paste logo.svg + disclaimer.txt in Pillow
                                   │
                                   ▼
                              Draft.image_path → real PNG
```

| Piece | Role |
|---|---|
| `apps/api/ports.py` | `ImageGen` Protocol: `generate(prompt, out_path) -> Path` |
| `apps/api/adapters/image_stub.py` | Free dark card + headline; no logo |
| `apps/api/adapters/image_http.py` | Optional `POST IMAGE_GEN_URL`; payload `{prompt, size}` only |
| `apps/api/boxes/art_director.py` | `build_image_gen`, `compose`, `rasterize_logo`, `apply_locks` |
| `apps/api/requirements.txt` | `pillow>=10.1,<12` |
| `apps/api/tests/test_art_director.py` | PNG magic, stub skips HTTP, overlay colors, HTTP contract |
| Fixtures (Task 6) | `fixtures/neutrogena/logo.svg`, `disclaimer.txt` via `load_disclaimer` |

## 7. Why this exact shape

### Port first, adapters behind a mode switch

`ImageGen` in `ports.py:19-20` matches ChatModel/TrendSource style: a Protocol, not a vendor SDK. `build_image_gen` (`art_director.py:127-137`) reads `IMAGE_GEN_MODE` (default `stub`). Unknown modes warn and fall back to stub. HTTP is constructed only when mode is exactly `http`. Tests force stub via autouse fixture and assert `HttpImageGen.generate` / `httpx.Client.post` never run when mode is stub — even if a paid-looking URL/key is set (`test_stub_file_exists_and_is_png_http_not_called`).

Plan sketch said `generate(prompt, path)`; shipped name is `out_path` (same as the pre-code stub). Call sites and tests use `out_path`.

### Stub paints unlocked zone only

`StubImageGen.generate` (`image_stub.py:56-81`) draws a dark 1080×1080 RGB card and wraps the first line of the prompt as headline. Hint text: “unlocked zone · brand marks added in code.” It does **not** open `logo.svg` or `disclaimer.txt`. That separation is the lock: the generator never sees brand marks.

### Overlay after generate, always

`compose` (`art_director.py:140-156`):

1. Resolve out path (`IMAGE_OUT_DIR` or `<sqlite parent>/images/{draft_id}.png`).
2. `gen.generate(prompt, dest)` — prompt only.
3. `apply_locks(dest)` — logo top-left, disclaimer bar at bottom.
4. Return `draft.model_copy(update={"image_path": str(dest.resolve())})`.

Comment in source: “Overlay logo/disclaimer in code. Never send them to ImageGen.” HTTP path is identical: save response bytes, then `apply_locks`. Tests check navy `#0B3D91` logo pixels and light disclaimer-bar pixels on both stub and mocked HTTP red canvases; POST JSON is exactly `{prompt, size}` with no SVG.

### Fixture SVG without cairo

`rasterize_logo` (`art_director.py:42-75`) parses the Task 6 SVG with ElementTree and paints `rect` / `text`. Enough for `NEUTROGENA*` + “unofficial demo” line. No Recraft, no cairo. Disclaimer text comes from `load_disclaimer()` (Hard Rules helper) so caption and image share one fixture string.

### Friendly errors, technical logs

Empty `IMAGE_GEN_URL` in HTTP mode raises a user-facing `RuntimeError` that says stay on stub or paste an API (`image_http.py:37-39`). Bad HTTP status / empty body similarly. Open failures in `apply_locks` log a warning and raise a friendly “Try stub mode” message.

### Free default; $5 closed

`.env.example` still has `IMAGE_GEN_MODE=stub` and empty URL/key. No Recraft package. Manual stub compose produced a showable PNG; file was deleted, not committed. Therefore the optional ~$5 was **not** spent.

## 8. What we refused

- **Prompting / generating the registered logo** (Recraft “generate logos,” Higgsfield locks, CapCut SVG upload).
- **Spending the ~$5** — stub card is the show default.
- **Firecrawl / Brandwatch / Meltwater** as part of this box (never were).
- **Review, Feedback, Export, Belt, Command Center** — Task 10 / 11 files list.
- **cairo / full SVG stack** — Pillow rect+text only.
- **Adobe four-mode lock table** — demo stays two-layer.
- **Live paid image call in CI/tests** — MockTransport / spies only; autouse keeps mode=stub.
- **Committing preview PNGs** — generated under tmp / local images dir, not the repo.

## 9. Verification that actually ran

**Claimed** in `task-9-report.md` from `apps/api` local `.venv`. This documentation agent did **not** re-run pytest. No compose, no live image API.

TDD red first (claimed): 7 failed (`No module named 'boxes.art_director'` / `'adapters.image_http'` / `'PIL'`).

After `865446a` (claimed):

```text
pytest tests/test_art_director.py -q
7 passed in 0.68s

pytest tests/ -q
88 passed in 1.68s
```

| Test | What it would fail on |
|---|---|
| `test_stub_file_exists_and_is_png_http_not_called` | missing file, not PNG magic, or HTTP generate/post called while mode=stub with a fake paid URL |
| `test_default_mode_is_stub_without_env` | unset mode builds something other than `StubImageGen` |
| `test_http_adapter_posts_prompt_size_and_bearer` | wrong method/headers/body keys; logo/SVG in prompt; bytes not saved |
| `test_http_compose_overlays_logo_and_never_sends_it` | SVG in POST JSON; missing navy logo / red mid / light disclaimer pixels |
| `test_stub_overlay_pastes_logo_and_disclaimer` | missing navy/disclaimer pixels; caption mutated |
| `test_compose_passes_prompt_verbatim_to_generator` | generator sees anything but the prompt string |
| `test_http_adapter_refuses_empty_url` | empty URL does not raise `RuntimeError` mentioning `IMAGE_GEN_URL` |

**Seen by implementer (claimed):** one local stub PNG open (~42KB, 1080×1080) with logo, headline, disclaimer; then deleted.

**Not seen:** live `IMAGE_GEN_URL` hit; Docker font rendering of the card; belt calling `compose`; Command Center preview.

pycache under `apps/api/tests/` includes `test_art_director.cpython-313-pytest-8.4.2.pyc` — evidence the suite ran on this machine at some point; not a substitute for re-running here.

## 10. Review findings and rulings

Reviewer package: `review-750a86b..865446a.diff`. Ledger (`progress.md`):

> Task 9: complete (commits 750a86b..865446a, review clean). $5 image budget still unspent; stub PNG is the show default.

Controller / session ruling for this journal: **Approved with only minors.** No Important/Critical. No fix commit. Exact reviewer prose file is **UNKNOWN** (not kept beyond the ledger line); minors below are the implementer’s recorded concerns, treated as accepted deferred notes.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| Critical | none | — | — |
| Important | none | — | — |
| Minor | SVG rasterizer is fixture-shaped (rect + text only) | Enough for demo lock | **Parked** — production SVG engine if logo gains paths |
| Minor | Docker slim may lack TTF; `load_default` still works | Add font package later if cards look thin | **Parked** |
| Minor | `compose` not on the belt yet | Task 10 wires after loop | **Owned by Task 10** |
| Minor | HTTP adapter mock-only; no live URL | By design — free default | **Honored** |
| Minor | Adobe four-mode lock table absent | Demo is two-layer | **Parked / production** |
| Minor / budget | `$5` unspent | Do not buy Recraft unless controller opens budget after stub | **Honored** — stub is showable |

Out of scope honored: no Review / Export / Belt / UI files in the diff (only the six Art Director files).

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Wire `compose` into `run_factory` after loop | **Task 10** |
| Persist / serve images for Preview UI | **Task 11** |
| Live `IMAGE_GEN_URL` when controller pastes an API | operator; mode=`http` |
| Optional ~$5 if stub later judged not showable | controller open-budget only |
| Full SVG (paths/gradients) / licensed type | production Art Director |
| Adobe four-mode lock table | production |
| Docker font package if slim cards look thin | leftover / Task 12 image polish |
| Caption may still carry full disclaimer text until copy path is trimmed | leftover; overlay now duplicates the lock on the image |
| No HTTP route for Art Director | **Task 10 / 11** |

## 12. Third-party check list

Under 15 minutes:

1. `git log --oneline 750a86b..865446a` — expect exactly `865446a feat: art director with image port`. No later Task 9 fix.
2. Open `.superpowers/sdd/2026-08-19-demo/progress.md` — Task 9 complete, review clean, **$5 still unspent**, stub is the show default.
3. Open `apps/api/ports.py` — `ImageGen.generate(prompt, out_path) -> Path`.
4. Open `apps/api/boxes/art_director.py` — `compose` calls `generate` then `apply_locks`; comment says never send logo to ImageGen.
5. Open `apps/api/adapters/image_stub.py` — dark card + headline only; no `logo.svg` import.
6. Open `apps/api/adapters/image_http.py` — payload keys are only `prompt` and `size`; `Authorization: Bearer …`.
7. Open `.env.example` — `IMAGE_GEN_MODE=stub`, empty `IMAGE_GEN_URL` / `IMAGE_GEN_KEY`.
8. Open `apps/api/requirements.txt` — `pillow>=10.1,<12`; no Recraft/Firecrawl.
9. From `apps/api`: `pytest tests/test_art_director.py -q` — expect 7 passed if the claimed count still holds.
10. Read `test_stub_file_exists_and_is_png_http_not_called` — mode stub with a fake paid URL must not call HTTP.
11. Read `test_http_compose_overlays_logo_and_never_sends_it` — POST body has no SVG; navy logo pixels after overlay.
12. Confirm no `boxes/review.py`, `feedback.py`, `export.py`, `belt.py`, and no Factory UI routes landed in this commit.
13. Confirm fixtures `apps/api/fixtures/neutrogena/logo.svg` and `disclaimer.txt` still say unofficial / not Kenvue.
