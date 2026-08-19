# Task 11 — Command Center UI (phone-usable)

**Status:** filled (review closed). Feat `2edc4b4` + fix `1bb268a` are on the branch. Ledger: review clean after fixture deep-dive + sources fix; `$5` still unspent. Docker images on `:8000`/`:3000` may still be the old scaffold until Task 12 rebuild.

## Locked before anyone writes code

Evidence preserved from the pre-implementation stub (same contract the implementer built against):

Walk this story on a phone-width (390px) screen:

1. Fetch trends → signals + scores + gates
2. Open a `deep_dive` → report
3. Create post → brief + grid + captions + rule/judge trail
4. Queue → approve/reject + **reason required**
5. Preview → fake IG frame + image + ZIP download

Tap targets must work on a phone. Do not add a second product (analytics dashboard, settings maze). This is the show.

Implementer note (accepted shape):

- Night inspection desk: ink `#14110E`, ticket `#F4EFE4`, stamp red only on kill/reject, pass green spare, gate gold, mute `#8A8478`. Fraunces + IBM Plex Sans + IBM Plex Mono via `next/font`.
- Vertical 17-box story rail is chrome on every page. Home is the rail plus the five-step walk.
- Reason cannot be skipped: submit disabled until clerk name + non-whitespace reason (`desk/review.ts` `canSubmitReview`).
- Unofficial Neutrogena fixture tape in the mast so nobody thinks this is a Kenvue product.
- HTTP extras for the story (belt still returns the locked types): `POST /radar/run` envelope `{reports, scores, signals_seen, deep_dives}`; `GET /briefs/{id}` includes stored concepts; `GET /drafts/{id}/image` PNG. CORS already allowed `localhost:3000`.
- No login, analytics, or extra pages.

## 1. Identity

| | |
|---|---|
| **Task** | 11 |
| **Plan heading** | Command Center UI (phone-usable) (`docs/superpowers/plans/2026-08-19-demo.md`, “Task 11”) |
| **Boxes** | Layer 4 Command Center story — Review & Approve (15), Preview & Export (16), Feedback Writer (17) as UI; the 17-box rail is chrome that points at every box |
| **Branch / worktree** | `feat/foolproof-design` at `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Base** | `24e103a` `feat: review export belt` |
| **Feat** | `2edc4b4` `feat: command center demo ui` (2026-08-20; date from `task-11-report.md`) |
| **Fix** | `1bb268a` `fix: fixture deep-dive fallback and show sources` |
| **Head (task closed)** | `1bb268a` |
| **Author on git** | UNKNOWN (this documentation agent has no shell; review packages list the SHA/message only) |
| **Implementer agent id** | UNKNOWN (not named in `progress.md` for this task) |
| **Reviewer agent id** | UNKNOWN |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/task-11-brief.md`, `task-11-report.md`, `progress.md` |
| **Review packages** | `review-24e103a..2edc4b4.diff` (23 files, +2376); `review-2edc4b4..1bb268a.diff` (10 files, +425) |
| **Re-review** | Fix round 1/5 closed the Important demo-walk hole (0 live `deep_dive`); ledger says review clean at `1bb268a` |

## 2. What the user would see

A night inspection desk on a phone-width screen — dark ink, ticket-paper cards, gold gate stamps, red only when something is killed or rejected. A vertical 17-box rail stays on every page. Yellow unofficial Neutrogena tape sits in the mast so nobody mistakes this for a Kenvue product. Home lists the five-step walk. Fetch trends shows real headlines with brand-fit, velocity, and gates. When this Fetch lands zero deep-dives, a labeled **Open unofficial fixture deep-dive** ticket appears (stamp: **not this Fetch**) so Create post can still run. Factory shows brief, concept grid, captions, hard-rules hits, and the judge trail. Queue forces a named clerk and a typed reason before Approve or Reject light up. Preview is a paused Instagram-shaped frame with the composed PNG and a ZIP download. Nothing publishes.

## 3. The problem this task was solving

Tasks 1–10 built an empty Next shell, every box, the belt, and HTTP — but the Command Center was still one heading. A stranger could not click Fetch → deep-dive → Create post → Approve with reason → paused ZIP. The demo walk in the plan (`docs/superpowers/plans/2026-08-19-demo.md:414-425`) is the definition of done; without these pages the belt stays an API-only story.

Depends on it:

- **Task 12** — CI + README / `docker compose up` demo script must point at a walkable UI; compose images need rebuild so `:8000`/`:3000` match this code.
- Closes the “web is a heading” park from Task 1 and the “HTTP for Task 11, not UI” park from Task 10.
- Surfaces `sources[]` on opened reports so the skeptic cage is visible, not only stored.

## 4. Constraints that were already locked

Demo plan Task 11 (`docs/superpowers/plans/2026-08-19-demo.md:380-397`):

> **Files:**
> - Create: `apps/web/app/page.tsx` (story rail)
> - Create: `apps/web/app/radar/page.tsx`
> - Create: `apps/web/app/factory/page.tsx`
> - Create: `apps/web/app/queue/page.tsx`
> - Create: `apps/web/app/preview/[id]/page.tsx`
>
> **Story you click in a demo:**
> 1. **Fetch trends** → list signals + scores + gates
> 2. Open a `deep_dive` → report
> 3. **Create post** → brief + grid + captions + rule/judge trail
> 4. **Queue** → approve/reject + reason
> 5. **Preview** → fake IG frame + image + ZIP download
>
> Step 1: Wire API. Mobile width 390px usable (tap targets).
> Step 2: Walk the story yourself. Commit `feat: command center demo ui`.

Demo walk / definition of done (`docs/superpowers/plans/2026-08-19-demo.md:414-425`):

> A stranger can: `docker compose up`; Click Fetch and see real headlines; Open a deep-dive with sources; Generate a Neutrogena-style post that used the belt; See an image with logo+disclaimer **not** generated by the model; Approve with a reason and export a ZIP. If any of those fail, the demo is not done.

Review / Feedback locks (still binding in UI — Task 10 API already enforces):

> Require a reason. … **Forbidden:** one-click reject.
> Builder cannot approve. … Last yes sits on irreversible verbs: publish, boost, send, claim. Day one: 100% human on benefit claims.

Global / spine (`docs/decisions/001-global-rulings.md`; stub `020` pre-lock; `progress.md:4`):

> No autonomous publish. A named human must approve, with a reason.
> Do not add a second product (analytics dashboard, settings maze).
> free adapters are the default. ~$5 optional only if a tool clearly improves the show… Do not spend the $5 unless image quality is the leftover demo gap after Task 9.

Task 10 HTTP surface (`019-task-10-review-export-belt.md`):

> HTTP for Task 11: `POST /radar/run`, `POST /factory/run`, `POST /review/{draft_id}`, `GET /export/{draft_id}`, list `GET /signals|/scores|/reports|/drafts|/queue`.

Unofficial fixture / brand (`CLAUDE.md` gotchas; Brand Book fixture):

> The reference pitch deck is a **reference**, not the spec.
> Unofficial Neutrogena — not a Kenvue product.

## 5. Options considered

### A. Analytics dashboard / settings maze / login wall

- **Would give:** Feels like a “product.” Multi-user roles day one.
- **Would cost:** Breaks the “one story, phone-usable” lock. Adds auth, charts, and a second product before the belt walk works.
- **Lost because:** stub + plan forbid a second product. No login. Clerk name is a session-stored text field, not an account.

### B. Do nothing / leave Command Center as the Task 1 heading

- **Would give:** Zero UI risk; API-only demo.
- **Would cost:** Demo walk fails. Task 12 has nothing to document. Third-party reviewer cannot click the machine.
- **Lost because:** Task 11 is the show. Plan files list the five pages.

### C. Fake the walk with hard-coded mock JSON in React

- **Would give:** Pretty screens without Docker/API friction.
- **Would cost:** Lies about the belt. Score/judge/flag_human would be theater. Demo walk requires real Fetch + belt.
- **Lost because:** pages call FastAPI (`desk/api.ts`). Live `POST /radar/run` was walked (103 signals / 20 scores on this LAN).

### D. Silent auto-pick of a canned report when Fetch returns 0 deep_dives

- **Would give:** Factory always has something; fewer clicks.
- **Would cost:** Operator thinks the live Fetch produced the deep-dive. Contaminates trust in the radar.
- **Lost because:** fix `1bb268a` keeps live tickets and offers a **labeled** fixture (`not this Fetch` / `UNOFFICIAL FIXTURE`). Operator opts in.

### E. Spend the ~$5 on Recraft / Firecrawl / paid UI kit for “demo polish”

- **Would give:** Fancier cards or scraped pages.
- **Would cost:** Budget gate; stub PNG already showable (Task 9 ruling).
- **Lost because:** `$5` still unspent. Desk is CSS tokens + `next/font`, not a paid design system.

### F. Role model enforcing “builder cannot approve”

- **Would give:** Spec-literal Review lock in the UI.
- **Would cost:** Auth/roles the demo does not have.
- **Lost because:** Task 10 parked this to production / Task 11 UX policy; this task kept **named clerk + reason** without roles. Still parked for production.

## 6. Decision

Night inspection desk Command Center wired to Task 10 HTTP, plus the smallest desk extras the story needed.

```text
apps/web/app/
  layout.tsx              Fraunces + IBM Plex; themeColor #14110E
  globals.css             design tokens, 44px taps, IG frame, tape
  page.tsx                five-step walk + 17-box index
  radar/page.tsx          Fetch → tickets → open deep_dive / fixture
  factory/page.tsx        Create post → brief + grid + captions + trail
  queue/page.tsx          clerk + reason gate → approve/reject
  preview/[id]/page.tsx   paused IG frame + PNG + ZIP

apps/web/desk/
  DeskShell.tsx           mast tape + rail chrome
  StoryRail.tsx           vertical 17-box belt
  boxes.ts                BOXES[1..17] + layers
  api.ts                  API_URL + runRadar/openFixtureDive/…
  review.ts               canSubmitReview, fixture copy, sources helpers
  review.test.ts          8 logic tests
  ui.tsx                  Ticket/Stamp/ReportCopy/ReportSources
  types.ts / format.ts

apps/api/ (desk extras only)
  main.py                 /radar/run envelope; /radar/fixture;
                          GET /briefs/{id} + concepts; GET /drafts/{id}/image
  db.py                   concepts table; upsert_concepts / list_concepts
  boxes/belt.py           upsert_concepts after strategist
  boxes/fixture_dive.py   labeled unofficial pack (fix)
  tests/test_desk.py      envelope, brief grid, PNG, fixture runnable
```

Commit messages exactly: `feat: command center demo ui` then `fix: fixture deep-dive fallback and show sources`.

## 7. Why this exact shape

### Night inspection desk tokens

`:root` in `apps/web/app/globals.css`:

| Token | Value | Use |
|---|---|---|
| `--ink` | `#14110e` | page ground |
| `--ticket` | `#f4efe4` | card paper |
| `--stamp` | `#c43b3b` | kill / reject only |
| `--pass` | `#2f6b4f` | spare pass green |
| `--gate` | `#c9a227` | deep_dive / lit rail / kickers |
| `--mute` | `#8a8478` | secondary copy |
| `--tap` | `44px` | minimum tap target |
| `--rail` | `58px` | story-rail column |

Fonts via `next/font/google` in `layout.tsx`: Fraunces (display), IBM Plex Sans, IBM Plex Mono. Viewport `themeColor: #14110E`. Max desk width ~520px centered so 390px phones stay usable.

### 17-box story rail

`desk/boxes.ts` lists all 17 boxes in Radar / Memory / Factory / Command layers. `StoryRail` is sticky chrome on every page through `DeskShell`. Home lights box 01 (fetcher); other pages light the boxes whose `step` matches. Rail items are 44×44 tap targets (`min-height: var(--tap)`). This is orientation chrome, not a second product — each number jumps to the story page that exercises that layer.

### Unofficial tape

`DeskShell` mast:

> Unofficial Neutrogena fixture · not a Kenvue product

Gold hatch `.tape` strip. Preview IG handle repeats “not a Kenvue product.” Fixture report `what` starts with `UNOFFICIAL FIXTURE (not this Fetch)`.

### Reason required

Client: `canSubmitReview(user, reason)` requires non-whitespace clerk **and** reason (`desk/review.ts`). Queue Approve/Reject stay `disabled` until both pass (`queue/page.tsx`). Placeholder: “A reason is required. Same miss should not survive twice.”

Server still refuses blanks (`POST /review/{id}` → Task 10 `decide`). Client disable is UX; API is the lock.

Clerk name persists in `sessionStorage` under `cm-clerk` so a phone walk does not retype between tickets — still not login.

### Radar envelope + 0-deep_dive fixture fallback

`POST /radar/run` returns `{reports, scores, signals_seen, deep_dives}` so one click fills the desk (`main.py`). Live walk on this LAN: 103 signals, 20 scores, **0 deep_dives** (15 background / 5 discard) — same GDELT/Reddit friction as Task 3.

Fix `1bb268a`:

- `shouldOfferFixture(didRun, deepDivesThisPass)` only after a Fetch with 0 deep-dives.
- Button copy: **Open unofficial fixture deep-dive**; stamp **not this Fetch**.
- `POST /radar/fixture` persists `sig_fixture_dive` / `rep_fixture_dive` with `sources[]` (url, quote, hash) — same seed shape as Task 10 belt tests (`boxes/fixture_dive.py`).
- Live tickets stay on the desk; fixture does not replace them.
- Factory empty shelf offers the same labeled button.

### `sources[]` shown

`ReportSources` / `ReportCopy` in `desk/ui.tsx` render url (link), quote, and hash. Used on opened deep-dives, fixture reports, and the brief’s packed report. Plan demo walk step 3: “Open a deep-dive with sources.”

### Concept grid persistence

Task 10 accepted first-concept-only on the belt. Factory UI still needs the strategist grid on screen. `upsert_concepts` after `run_strategist`; `GET /briefs/{id}` returns brief + `concepts[]`. Grid ticket labels row 0 “on the belt.”

### Preview = paused, not publish

IG frame badge: **Paused — not published**. ZIP via `GET /export/{id}` downloads `{draft_id}_paused.zip`. No publish/boost route. Image via `GET /drafts/{id}/image` (PNG).

### iOS zoom / taps

Reason textarea and inputs use `font-size: 16px` so iOS Safari does not zoom on focus (fix note). Buttons/links honor `--tap` 44px.

### Friendly errors

`desk/api.ts` maps network miss → “Could not reach the machine…”, 429 → wait-a-minute copy, JSON `{error}` without stacks. Matches API `_friendly` pattern.

## 8. What we refused

- **Login / roles / “builder cannot approve” enforcement** — named clerk text only; production owns roles.
- **Analytics dashboard, settings maze, extra pages** — five story routes + home only.
- **Paid UI kits / Recraft / Firecrawl for polish** — `$5` unspent.
- **Silent fixture swap when Fetch is empty** — labeled opt-in only.
- **Autopublish or one-click reject** — reason gate on both verdicts.
- **CrewAI / agent-driven UI orchestration** — plain `fetch` to FastAPI; belt stays server-side.
- **Pretending Docker `:8000` was current** — report records story walked on `uvicorn :8001` + `next dev :3001`; compose images may be stale until Task 12 rebuild.

## 9. Verification that actually ran

**Claimed** in `task-11-report.md` from local `.venv` / `apps/web`. This documentation agent did **not** re-run pytest, npm test, or compose. Evidence on disk: `apps/api/tests/__pycache__/test_desk.cpython-313-pytest-8.4.2.pyc` and web test file present.

After feat `2edc4b4` (claimed):

```text
apps/api  pytest tests/ -q
105 passed in 3.37s

apps/web  npm test
next typegen && tsc --noEmit && node --experimental-strip-types --test desk/review.test.ts
6 passed (blank reason cannot submit, clerk required, missing sources named, deep_dive sorts first)
```

After fix `1bb268a` (claimed):

```text
apps/api  pytest tests/test_desk.py tests/test_belt.py -q   8 passed
apps/web  npm test   typecheck + 8 logic tests (fixture offer + source fields)
```

| Test | What it would fail on |
|---|---|
| `test_radar_run_envelope_keys` | missing `reports`/`scores`/`signals_seen`/`deep_dives`; stack leaked |
| `test_get_brief_includes_grid` | concepts not on brief GET; 404 body lacks `error` |
| `test_get_draft_image_png` | non-PNG body; missing image not 404 |
| `test_unofficial_fixture_dive_is_labeled_and_runnable` | fixture not labeled UNOFFICIAL / not this Fetch; sources lack url+quote+hash; factory captions empty / PCOS |
| web `blank reason cannot submit` | whitespace reason enables stamp |
| web `blank clerk cannot submit` | empty name enables stamp |
| web `fixture offer only after a Fetch with 0 deep_dives` | fixture shown before Fetch or when deep_dives > 0 |
| web `source fields expose url, quote, and hash` | sources helpers drop fields |

**Seen by implementer (claimed):**

- Pages 200 with unofficial tape: `/` `/radar` `/factory` `/queue` `/preview/[id]`
- CORS `Access-Control-Allow-Origin: http://localhost:3000`
- Live `POST /radar/run` → 103 signals, 20 scores, **0 deep_dives**
- Fixture path → report 200, PNG 200 (~62KB), brief 6 concepts, blank reason **400**, approve Anand **200**, paused ZIP **200** (~55KB), queue dropped that draft

**Not seen (honest holes):**

- Fresh `docker compose up` with **rebuilt** images exercising this UI on `:8000`/`:3000` — Docker still served old health-only API at verify time; story walked on `:8001`/`:3001`.
- Live Fetch producing a real `deep_dive` on this LAN (fixture continued the walk).
- Paid `IMAGE_GEN_URL`.

## 10. Review findings and rulings

Reviewer packages: `review-24e103a..2edc4b4.diff`, then `review-2edc4b4..1bb268a.diff`. Ledger (`progress.md:39-43`):

> Task 11: complete (commits 24e103a..1bb268a, review clean)
> Task 11: fix round 1/5 (fixture deep-dive + sources; 1bb268a)
> Task 11: minor (deferred): /radar/run returns whole shelf; factory prefers leftover reports if any exist
> Task 11: implementer DONE_WITH_CONCERNS commit 2edc4b4 feat: command center demo ui. Live radar 0 deep_dives this LAN; factory walk used fixture report. Docker :8000 still old health-only; story walked on :8001/:3001.

Controller / session ruling for this journal: **Approved after fix round 1.** No remaining Important/Critical in the ledger. Exact reviewer prose file is **UNKNOWN** (not kept beyond the ledger lines). The 0-deep_dive demo-walk hole was the fix trigger.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| Critical | none recorded | — | — |
| Important (fix) | Live Fetch often yields 0 `deep_dive`; demo walk stuck before Create post | Labeled unofficial fixture opt-in; show `sources[]` | **Fixed** in `1bb268a` |
| Minor (deferred) | `/radar/run` returns whole shelf (`list_signals` / `list_scores` / `list_reports`), not only this pass | UI hides unscored when scores exist; ok for demo | **Parked** |
| Minor (deferred) | Factory empty-shelf / pick list can prefer leftover reports already in DB | Operator can still pick; fixture if shelf empty | **Parked** |
| Concern | Docker `:8000`/`:3000` images stale (health-only) | Rebuild is Task 12 / local `docker compose build` | **Parked → Task 12** |
| Concern | Reason disable is client-side | API still 400/422 on blank | **Accepted** (defense in depth) |
| Concern | “Builder cannot approve” still no role model | Named user + reason only | **Parked → production** |
| Concern | `data/demo.db` held unscored fetch leftovers | Radar hides unscored when scores exist | **Accepted** |
| Budget | `$5` unspent | Do not buy for UI polish | **Honored** |

Out of scope honored: no analytics, no login, no publish route, no CrewAI, no second product.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| Rebuild / prove `docker compose up` serves this Command Center on `:8000`/`:3000` | **Task 12** |
| CI workflow (lint + pytest + web build) + README demo walk | **Task 12** |
| `/radar/run` returns whole shelf vs this-pass-only envelope | leftover; UI filters unscored |
| Factory preferring leftover DB reports over “this Fetch” | leftover; fixture path labeled when empty |
| Role model / “builder cannot approve” | production plan |
| Live deep_dive reliability (GDELT 429 / Reddit 403 on some LANs) | leftover / ops; fixture bridge for demo |
| CORS allowlist is `:3000` only — walk used `:3001` with local uvicorn | leftover; set `NEXT_PUBLIC_API_URL` or rebuild compose |
| Persist / show full strategist grid beyond first belt concept | partially done (concepts table); belt still `MAX_FACTORY_CONCEPTS = 1` |
| Idempotent / single-decision guard on `decide` | leftover from Task 10 |
| LiteLLM / paid image still stub defaults | intentional; `$5` unspent |
| Expire / withdraw export state | production Preview & Export |

## 12. Third-party check list

Under 15 minutes:

1. `git log --oneline 24e103a..1bb268a` — expect `2edc4b4 feat: command center demo ui` then `1bb268a fix: fixture deep-dive fallback and show sources`.
2. Open `.superpowers/sdd/2026-08-19-demo/progress.md` — Task 11 complete, review clean after fix, minors deferred, Docker stale note, **`$5` still unspent**.
3. Open `apps/web/app/globals.css` — tokens `--ink #14110e`, `--ticket #f4efe4`, `--stamp #c43b3b`, `--pass #2f6b4f`, `--gate #c9a227`, `--mute #8a8478`, `--tap 44px`.
4. Open `apps/web/desk/DeskShell.tsx` — unofficial Neutrogena tape; “Night inspection desk” mast sub.
5. Open `apps/web/desk/boxes.ts` + `StoryRail.tsx` — 17 boxes, four layers, rail chrome.
6. Open `apps/web/desk/review.ts` — `canSubmitReview`; `FIXTURE_NOTE` / `shouldOfferFixture`; `SOURCE_LABELS`.
7. Open `apps/web/app/queue/page.tsx` — Approve/Reject `disabled` until clerk + reason; no publish control.
8. Open `apps/web/app/radar/page.tsx` — fixture ticket with stamp **not this Fetch** only when `offerFixture`.
9. Open `apps/web/desk/ui.tsx` — `ReportSources` shows url, quote, hash.
10. Open `apps/api/boxes/fixture_dive.py` — `UNOFFICIAL FIXTURE (not this Fetch)` in `what`; `sources[]` with url/quote/hash.
11. Open `apps/api/main.py` — `/radar/run` envelope; `/radar/fixture`; `/briefs/{id}` includes `concepts`; `/drafts/{id}/image`; **no** publish route; CORS `localhost:3000`.
12. From `apps/api`: `pytest tests/test_desk.py -q` — expect envelope / brief grid / PNG / fixture tests green if claimed count still holds.
13. From `apps/web`: `npm test` — expect typecheck + 8 logic tests including fixture offer + blank reason.
14. Confirm preview copy says **Paused — not published** (`preview/[id]/page.tsx`).
15. Treat Docker `:8000`/`:3000` as **unverified until rebuild** (Task 12). If compose still serves health-only API, that is a known hole, not a Task 11 regression in git.
