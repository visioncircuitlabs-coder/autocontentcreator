# API reference

FastAPI app: `apps/api/main.py`. Title `Content Machine`. CORS allows localhost/127.0.0.1 on ports **3000** and **3050**.

Base URL for the walk: `http://localhost:3050/engine` (Next proxy, 300s). Direct: `http://127.0.0.1:8000`.

Errors: JSON `{"error": "<friendly sentence>"}`. Typical status 400, 404, 429, 500, 502, 504. No stack traces.

Every response (except `/health` and `/events`) is logged with `X-Request-Id`.

## Health and events

### `GET /health`

```json
{"ok": true, "chat": true}
```

`chat` is whether `build_chat()` found a key.

### `POST /events`

Body: `{ "kind": "look_click", "payload": {} }`. Stored as `ui.<kind>`. Always `{"ok": true}` from the client’s point of view even if logging fails.

### `GET /events?limit=80`

Recent machine events, newest first.

## Radar

Rate limit: **6** `POST /radar/fetch` or `POST /radar/run` per client host per 60 seconds → **429** `"Too many fetches. Please wait a minute and try again."`

### `POST /radar/fetch`

Returns `Signal[]` only (no scores). Used by tests and the old desk.

### `POST /radar/run`

Fetch + score + at most one deep-dive.

```json
{
  "reports": [ { "report_id": "…", "what": "…", "why_now": "…", "sources": [], "skeptic": "…" } ],
  "scores": [ { "signal_id": "…", "brand_fit": 8, "velocity": 5, "safety": "ok", "gate": "deep_dive", "reason": "…", "model": "…", "prompt_version": "v1" } ],
  "signals_seen": [ { "signal_id": "…", "source": "news_rss", "url": "https://…", "title": "…", "snippet": "…" } ],
  "deep_dives": [ "«same as reports»" ]
}
```

`gate` is `discard` | `background` | `deep_dive`. `source` is `gdelt` | `news_rss` | `reddit` | `rss` | `grok_web`.

### `POST /radar/fixture`

Unofficial canned closer look. Not this Fetch.

```json
{ "fixture": true, "signal": {}, "score": {}, "report": {} }
```

## Factory

### `POST /factory/run`

```json
{ "report_id": "rpt_…" }
```

Returns `Draft[]` (usually 2–3 caption variants). **`image_path` is null.** Loop fields: `caption`, `variant`, `rules`, `round`, `flag_human`, `judge`.

500: `"Could not build a post from that report. Please try again."`

### `POST /factory/image`

```json
{ "draft_id": "dft_…" }
```

Returns one `Draft` with `image_path` set. Always regenerates via `visual_prompt` then overlay.

500: `"Could not make that picture. Please try again."`

### `POST /factory/video`

```json
{ "draft_id": "dft_…" }
```

Returns one `Draft` with `video_path` set. Always regenerates via `video_prompt` then coded overlay. Does **not** publish.

500: `"Could not make that short video. Please try again."`

## Review and export

### `POST /review/{draft_id}`

```json
{ "user": "Asha", "verdict": "approve", "reason": "Claim-safe and on the monsoon idea." }
```

`verdict`: `approve` | `reject`. Empty user or reason → 400. Does **not** publish.

### `GET /export/{draft_id}`

`application/zip` named `{draft_id}_paused.zip`. If the PNG or mp4 is missing, export may compose them. Contents: preview HTML, PNG, MP4, JSON sidecar, signed manifest. Stamp: paused / does not go live.

## Reads

| Method | Path | Notes |
|---|---|---|
| GET | `/signals` | All stored headlines |
| GET | `/scores` | All scores |
| GET | `/reports` | All trend reports |
| GET | `/reports/{report_id}` | 404 `"That report is not on the shelf."` |
| GET | `/briefs/{brief_id}` | Brief plus `concepts` |
| GET | `/drafts` | All drafts |
| GET | `/drafts/{draft_id}` | 404 `"That draft is not in the queue."` |
| GET | `/drafts/{draft_id}/image` | `image/png` |
| GET | `/drafts/{draft_id}/video` | `video/mp4` |
| GET | `/queue` | Drafts waiting a human |

## Domain shapes (Python)

See `apps/api/models.py`. TypeScript twins: `apps/web/desk/types.ts`.

Related: [agents/system.md](agents/system.md), [agents/ui.md](agents/ui.md).
