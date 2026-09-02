# Product video as a factory step (not inside Make a post)

**Status:** locked for the walkable demo. Branch `cursor/product-video-generation-afe0`.

## What a person sees

After they pick a caption version and tap **Make the picture**, they can tap **Make a short video**. That animates the picture they just made for about five seconds. Neutrogena stills/clips still get the coded wordmark + legal line. Chile Limón does not — type is in the art, and the bag is the provided pack photo. Yes/No still needs a name and a reason. The ZIP stays paused. Nothing goes to Instagram.

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
- **Let Pillow stamp a second LAY'S wordmark or unofficial bar on Chile Limón.** Founder override 2026-09-02. Type belongs in the art. Lost.
- **Redraw the Chile Limón bag in Imagine.** The pack in the ad must be `fixtures/lays/products/chile-limon.jpg` (composite or image-edit). Lost.
- **Copy the 90s Imagine still timeout.** Docs say generation typically takes up to several minutes. Poll budget is 900s. Lost.
- **Publish the clip.** No autonomous publish. Lost.
- **A second content app / CrewAI belt.** The product already exists on this branch. Lost.
- **Skip the stub.** Live API will be missing in CI and on a cold laptop. Lost.

## Locks this adds

- Video is a dedicated step. `run_factory` does not film.
- `POST /factory/video` requires a campaign still (`draft.image_path` on disk, not under `fixtures/`).
- Happy path is image-to-video from that composed still as the first frame.
- The still is a designed campaign ad (product hero, burst composition, graphic type).
- Neutrogena: wordmark and legal bar stay in the code overlay. Video freezes that layout and only adds product motion.
- Chile Limón: still composites or image-edits FROM `chile-limon.jpg` so the bag is that pack (logo, 25% MORE, Chile Limón Flavour, veg mark, lime/chilli/garlic). Burst + type around it (`TANGY LIME. SPICY HIT.` / `CRUNCH THE HEAT.` / `DARE A BITE?`). `overlay_disclaimer=false`, `always_disclaimer=false`. Logo MAY go into Grok Imagine because it is on the real pack. Do not stamp a second LAY'S wordmark. Lime + red chilli, not jalapeño, not Magic Masala. Duration stays 5s. Do not take Night Shift's Lays PR.
- Video prompt: freeze the still's layout and type. No new headlines, no extra wordmark, no unofficial bar, no Grok watermark.
- Neutrogena overlay after generate so the legal line cannot warp. Lays: skip that overlay.
- Image spend and video spend are separate caps on the same `spend.jsonl`.
- Stub + ffmpeg loops the campaign still into a walkable H.264 mp4 when Imagine is off.

## Files

| Piece | Role |
|---|---|
| `POST /factory/video` | Dedicated step (`boxes/belt.py` `film_chosen`) |
| `adapters/video_imagine.py` | xAI video generations + 900s poll + I2V data URL |
| `adapters/video_stub.py` | Loop campaign still → mp4 |
| `boxes/video.py` | `compose_video`; Neutrogena overlay, Lays skip |
| `boxes/pack_photo.py` | Chile Limón JPEG + Pillow composite around the real bag |
| `boxes/visual.py` `video_prompt` | Product-true motion from the still, no caption leak |
| `boxes/video_budget.py` | `$2` default cap, `$0.40` per 5s clip |
