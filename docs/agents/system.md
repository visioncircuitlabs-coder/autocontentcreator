# System

Four layers. One belt. One walk. Ports at the edges.

```text
┌─────────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Trend Radar │ → │ Brand Brain │ → │ Content      │ → │ Command      │
│ fetch/score │   │ fixtures +  │   │ Factory      │   │ Center       │
│ 1 deep dive │   │ track record│   │ text then    │   │ five beats   │
│             │   │             │   │ one picture  │   │ paused ZIP   │
│             │   │             │   │ then ~5s clip│   │              │
└─────────────┘   └─────────────┘   └──────────────┘   └──────────────┘
```

## Repo layout

```text
apps/api/                 FastAPI engine
  main.py                 HTTP surface
  models.py               Signal, Score, TrendReport, Brief, Concept, Draft, Decision
  ports.py                TrendSource, ChatModel, ImageGen, VideoGen
  db.py                   SQLite (signals, scores, reports, claims, briefs,
                          concepts, drafts, decisions, events, track_record,
                          api_keys, runs, claims_registry, idempotency_keys)
  obs.py                  JSONL events
  adapters/               gdelt, news_rss, reddit_json, grok_web, chat_litellm,
                          image_imagine, image_http, image_stub,
                          video_imagine, video_stub, resilience
  boxes/                  one module per box + belt.py
    auth.py               API keys + roles (viewer/approver/admin)
    brand_pack.py         BRAND_SLUG → fixture pack loader
    claims_registry.py    evidence-bound benefit claims
    audit.py              provenance chain for a draft
    evidence.py           hash-chain + manifest (tamper-evident exports)
    image_budget.py       Grok $ cap gate (stills)
    video.py              unlocked clip + coded overlay
    video_budget.py       Grok $ cap gate (5s clips)
    metrics.py            /metrics aggregation
    learning.py           approval-memory → writer prompt
    rubric.py             deterministic craft scorer v2
    strategist/copywriter/judge/craft/loop/hard_rules/review/export/...
  harness/                agent-harness primitives (no frameworks)
    breaker.py            circuit breakers (chat + image + video)
    steps.py              StepResult envelope, run-id contextvar
    admission.py          bounded concurrency + 503 shedding
    chat_wallet.py        token/$ accounting
    resumer.py            failed-run resume
    eval.py               golden-set evaluation
  fixtures/neutrogena/    unofficial brand pack
apps/web/                 Next.js App Router
  app/page.tsx            WalkApp (the product)
  app/engine/[...path]    900s proxy → API
  walk/                   five-beat UI
  desk/                   API client, words, ops strip, review helpers
infra/docker-compose.yml  api :8000, web :3050→3000
data/                     demo.db, images/, exports/, logs/, spend.jsonl (local)
docs/                     human + agent docs; docs/bar/ = research bars
```

Feature folders, not type folders, once new product code starts. Boxes already follow that: `boxes/copywriter.py`, not `services/`.

## Belt (plain Python)

`apps/api/boxes/belt.py` — not `apps/api/belt/` (the demo plan path is stale).

```text
run_radar
  run_fetch          GDELT + Google News RSS + Reddit JSON + optional Grok web
  run_score          exclusion → keyword fit → up to 5 Grok scores
  run_research ×1    chat=None, 3 GETs, 35s cap on the radar path

run_factory          picture does NOT run here
  build_brief        code pack, no model
  run_strategist     angles (templates if chat down)
  run_copywriter     ask 8, keep 2–3 postable captions
  run_loop           hard rules + judge + craft; rewrite ≤3; else flag_human

paint_chosen         after a person picks a version
  visual_prompt      4:5 bright water-gel ad; lighting from caption keywords only
  compose            ImageGen then Pillow wordmark + disclaimer bar

film_chosen          after the still — refuses if there is no campaign still
  video_prompt       motion from that still; no new text/logo/disclaimer in the prompt
  compose_video      image-to-video from the still, then ffmpeg overlay of the coded legal sheet
```

Caps: `MAX_DEEP_DIVES = 1`, `MAX_FACTORY_CONCEPTS = 1`, `MAX_CHAT_SCORES = 5`, chat timeout 20s, Imagine still timeout 180s, Imagine video poll 900s every 5s, Next proxy 900s, radar fetch rate 6/min/host.

## Ports

```text
TrendSource.fetch(query_id) -> list[Signal]
ChatModel.complete_json(system, user, schema) -> BaseModel
ImageGen.generate(prompt, out_path) -> Path
VideoGen.generate(prompt, out_path, *, source_image=None) -> Path
```

`build_chat()` returns `None` if `XAI_API_KEY`, `GEMINI_API_KEY`, and `GROQ_API_KEY` are all empty. Callers must still walk on templates.

`build_image_gen()`:

| `IMAGE_GEN_MODE` | Adapter |
|---|---|
| `imagine` / `grok-imagine` / `grok_imagine` | `ImagineImageGen` → `POST https://api.x.ai/v1/images/generations` model `grok-imagine-image`, `aspect_ratio: 4:5` |
| `http` | `HttpImageGen` → `IMAGE_GEN_URL` |
| `stub` or unknown | `StubImageGen` Pillow card |

Imagine failure falls back to stub (unless already stub). Overlay always runs.

`build_video_gen()`:

| `VIDEO_GEN_MODE` (falls back to `IMAGE_GEN_MODE`) | Adapter |
|---|---|
| `imagine` / `grok-imagine` / `grok-imagine-video` | `ImagineVideoGen` → `POST https://api.x.ai/v1/videos/generations` model `grok-imagine-video-1.5`, `duration: 5`, `image.url` = campaign still, `generate_audio: false`, poll `GET /v1/videos/{request_id}` every 5s up to 900s |
| `stub` or unknown | `StubVideoGen` loops the campaign still → mp4 |

Video failure falls back to stub (unless already stub), still looping the campaign still. Overlay always runs. ffmpeg is required to write the mp4. Text-to-video is not the happy path.

## Data (SQLite)

Default `SQLITE_PATH=data/demo.db` (Compose: `/data/demo.db`).

Tables: `signals`, `scores`, `reports`, `claims`, `briefs`, `concepts`, `drafts`, `decisions`, `events`, `track_record`.

Brand memory (dual store): SQLite is the machine truth; `MEMORY_DIR=data/memory`
mirrors it into human-editable Markdown — see [memory.md](memory.md). Only
`lessons.md` survives rebuilds; the rest regenerates from SQLite.

IDs: `signal_id` = sha256(url). Drafts: `dft_…`. Images: `data/images/{draft_id}.png`. Videos: `data/videos/{draft_id}.mp4`. ZIPs: `data/exports/{draft_id}_paused.zip`.

Datetimes ISO-8601, timezone-aware.

## Web

Homepage is App Mode: `walk/WalkApp.tsx`. Desk routes `/radar` `/factory` `/queue` `/preview/[id]` still exist; do not make them the default story.

Browser calls `NEXT_PUBLIC_API_URL` (Compose and local Next: `/engine`). `app/engine/[...path]/route.ts` proxies to `ENGINE_URL` (default `http://127.0.0.1:8000`) with **300 second** timeout. Direct `http://localhost:8000` from the browser is the exception, not the walk.

On-screen copy lives in `apps/web/desk/words.ts`. Internal names stay in code.

## Observability

- `data/logs/machine.jsonl` via `obs.emit`
- `events` table; `GET /events`, `POST /events` (UI `ui.*` kinds)
- `X-Request-Id` on HTTP
- User never sees a stack trace

Kinds: `api_start`, `http`, `fetch_source`, `radar_start`, `radar_scored`, `radar_end`, `radar_fail`, `paint_start`, `paint_end`, `film_start`, `film_end`, `ui.look_click`, `ui.look_fail`, `ui.fetch_fail`.

## Tests

| Area | Command |
|---|---|
| API | `cd apps/api` then `pytest` |
| Web | `cd apps/web` then `npm test` (typecheck + `desk/*.test.ts`) |
| CI | `.github/workflows/ci.yml` — Python 3.12 compileall+pytest, Node 22 `npm run build`. No Docker in CI. |
| Smoke | `python scripts/demo_walk.py` against a live `:8000` |

## Related

- HTTP: [../reference-api.md](../reference-api.md)
- Box files: [boxes.md](boxes.md)
- Walk: [ui.md](ui.md)
