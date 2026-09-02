# Product video as a factory step (not inside Make a post)

**Status:** locked for the walkable demo. Branch `cursor/product-video-generation-afe0`.

## What a person sees

After they pick a caption version and tap **Make the picture**, they can tap **Make a short video**. That makes one ~5 second clip of the same water-gel jar. Logo and the legal line are stamped in code, same as the still. Yes/No still needs a name and a reason. The ZIP stays paused. Nothing goes to Instagram.

## Why this shape

Picture already waits for a pick (`POST /factory/image`, not inside `POST /factory/run`). Video follows that lock: `POST /factory/video`. Burying a live video call inside Make a post would wait on the 5-minute page again and spend money before anyone chose a caption.

xAI has a real video API: `POST https://api.x.ai/v1/videos/generations` (model `grok-imagine-video-1.5`, poll `GET /v1/videos/{request_id}`). We use it when `VIDEO_GEN_MODE=imagine` and `XAI_API_KEY` is set. If the key, budget, or API fails, a stub still writes a real ~5s mp4 so the walk works.

## Options we refused

- **Paint video during Make a post.** Same trap as the old three-photo factory. Lost.
- **Send the overlaid still into image-to-video.** That feeds the disclaimer and wordmark to the model. Overlay is code. Lost.
- **Let the model draw the legal bar.** Same lock as stills. Lost.
- **Publish the clip.** No autonomous publish. Lost.
- **A second content app / CrewAI belt.** The product already exists on this branch. Lost.
- **Skip the stub.** Live API will be missing in CI and on a cold laptop. Lost.

## Locks this adds

- Video is a dedicated step. `run_factory` does not film.
- Brand marks, claims, and the disclaimer stay out of the video prompt.
- Overlay after generate, always.
- Image spend and video spend are separate caps on the same `spend.jsonl`.
- Stub + ffmpeg produces a walkable H.264 mp4 when Imagine is off.

## Files

| Piece | Role |
|---|---|
| `POST /factory/video` | Dedicated step (`boxes/belt.py` `film_chosen`) |
| `adapters/video_imagine.py` | xAI video generations + poll |
| `adapters/video_stub.py` | Looping unlocked card → mp4 |
| `boxes/video.py` | `compose_video` then coded overlay |
| `boxes/visual.py` `video_prompt` | Product-true motion, no caption leak |
| `boxes/video_budget.py` | `$2` default cap, `$0.40` per 5s clip |
