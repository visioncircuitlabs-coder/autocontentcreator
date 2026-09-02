# Product video as a factory step (not inside Make a post)

**Status:** locked for the walkable demo. Branch `cursor/product-video-generation-afe0`.

## What a person sees

After they pick a caption version and tap **Make the picture**, they can tap **Make a short video**. That animates the picture they just made for about five seconds. Logo and the legal line stay stamped in code. Yes/No still needs a name and a reason. The ZIP stays paused. Nothing goes to Instagram.

## Why this shape

Picture already waits for a pick (`POST /factory/image`, not inside `POST /factory/run`). Video follows that lock: `POST /factory/video`. Burying a live video call inside Make a post would wait on the page again and spend money before anyone chose a caption.

xAI video is asynchronous. Do not copy the 90s Imagine still timeout.

Sources (fetched 2026-09-02):

- https://docs.x.ai/developers/model-capabilities/video/generation
- https://docs.x.ai/developers/rest-api-reference/inference/videos
- https://docs.x.ai/developers/models/grok-imagine-video-1.5

`POST https://api.x.ai/v1/videos/generations` returns `{ "request_id": "..." }` immediately. Poll `GET /v1/videos/{request_id}` every 5 seconds for up to 15 minutes (`POLL_BUDGET_S = 900`). Submit/poll/download HTTP timeouts are 60s. Status `pending | done | expired | failed`. On `done`, download `video.url` promptly (temporary). If `respect_moderation` is false, treat as blocked.

Model `grok-imagine-video-1.5`, `duration: 5` (API default is 8 if omitted), `aspect_ratio: 3:4`, `resolution: 720p`, `generate_audio: false`. Image-to-video sends the campaign still as `image.url` (data URL). Do not send `image` and `reference_images` together. We use this when `VIDEO_GEN_MODE=imagine` and `XAI_API_KEY` is set. If the key, budget, or API fails, a stub still writes a real ~5s mp4 from that still so the walk works. Next `/engine` waits 900s so the walk does not die at 90s.

## Options we refused

- **Paint video during Make a post.** Same trap as the old three-photo factory. Lost.
- **Text-to-video as the happy path.** Founder rejected a sample that animated a pack photo / generic clip. Lost.
- **Image-to-video from a fixture pack PNG.** That is a catalog shot, not the ad. Lost.
- **Let the model draw a new legal bar.** Same lock as stills. The prompt must not ask for one. Lost.
- **Copy the 90s Imagine still timeout.** Docs say generation typically takes up to several minutes. Poll budget is 900s. Lost.
- **Publish the clip.** No autonomous publish. Lost.
- **A second content app / CrewAI belt.** The product already exists on this branch. Lost.
- **Skip the stub.** Live API will be missing in CI and on a cold laptop. Lost.

## Locks this adds

- Video is a dedicated step. `run_factory` does not film.
- `POST /factory/video` requires a campaign still (`draft.image_path` on disk, not under `fixtures/`).
- Happy path is image-to-video from that composed still as the first frame.
- The still is a designed campaign ad (product hero, burst composition, graphic type). Wordmark and legal bar stay in the code overlay. Video freezes that layout and only adds product motion.
- Neutrogena motion is the water-gel jar. Chile Limón (if that SKU appears) is lime + chilli chips, never jalapeño, never extra LAY'S wordmarks. Do not take the Lays PR.
- Brand names, claims, and the disclaimer stay out of the **video prompt**.
- Overlay after generate, always, so the legal line cannot warp away during motion.
- Image spend and video spend are separate caps on the same `spend.jsonl`.
- Stub + ffmpeg loops the campaign still into a walkable H.264 mp4 when Imagine is off.

## Files

| Piece | Role |
|---|---|
| `POST /factory/video` | Dedicated step (`boxes/belt.py` `film_chosen`) |
| `adapters/video_imagine.py` | xAI video generations + 900s poll + I2V data URL |
| `adapters/video_stub.py` | Loop campaign still → mp4 |
| `boxes/video.py` | `compose_video` then coded overlay |
| `boxes/visual.py` `video_prompt` | Product-true motion from the still, no caption leak |
| `boxes/video_budget.py` | `$2` default cap, `$0.40` per 5s clip |
