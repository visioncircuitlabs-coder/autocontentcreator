# Change playbook

Do the smallest change. Tests with the change. User-facing strings through `words.ts` + plain-english skill.

## Restart so Imagine + overlay actually run

1. Confirm `.env` or the process has `IMAGE_GEN_MODE=imagine`, `IMAGE_GEN_MODEL=grok-imagine-image-2.0`, `XAI_API_KEY` set.
2. Kill the process on port 8000. Stale uvicorn serves old `visual.py`.
3. Start API from `apps/api` with those env vars.
4. Keep Next on 3050 with `NEXT_PUBLIC_API_URL=/engine`.
5. Walk: Look → Make a post → pick a version → **Make the picture**. Do not judge an old PNG in `data/images/`.

## Change the photo look

- Prompt: `apps/api/boxes/visual.py` only. **Neutrogena:** keep “no text, no logo.” **Lays:** designed type belongs in the prompt (explosion ad); legal still overlays in code. Lighting from a **keyword list**, not the full caption.
- Overlay: `boxes/art_director.py` (`rasterize_logo`, `apply_locks`, `_to_feed`).
- Adapter: `adapters/image_imagine.py` (`aspect_ratio` 3:4, `resolution` 2k, timeout, URL).
- Tests: `apps/api/tests/test_visual.py`, `test_art_director.py`.
- UI frame: `apps/web/app/globals.css` `.ig-photo`.

## Stop / start painting at a different beat

| Want | Do |
|---|---|
| No photo on Make a post | Keep `run_factory` free of `compose`. UI `makePost` → `runFactory` only |
| Photo after version pick | `makePicture` → `paintDraft` → `POST /factory/image` |
| Photo on download if missing | `export._ensure_image` already composes. Do not also paint earlier “to be safe” |

## Add a banned word

`BANNED_TOKENS` in `boxes/hard_rules.py`. Add a test in `test_hard_rules.py`. Do not put taste bans here (that is craft/judge).

## Add an exclusion (crisis / hiring spam)

`fixtures/neutrogena/exclusion.txt` as `category|pattern`. Scorer sets `safety=kill`. Test in `test_scorer.py`.

## Add a fetch source

1. New adapter implementing `TrendSource` in `adapters/`.
2. Register in `fetcher.default_sources`.
3. Add a `SOURCE_LABELS` entry in `words.ts`.
4. One dead source must not fail the whole Look.
5. Locked query. No free-web crawl.
6. Test the adapter; do not hit paid APIs in CI.

## Change Look ranking

`boxes/scorer.py`: exclusion first, then keyword, then optional chat, then `decide_gate`. Closer look is `brand_fit >= 8`. Keep `MAX_CHAT_SCORES` unless you re-time the 300s proxy.

## Change captions

`boxes/copywriter.py` (generate-many-then-filter) and brand examples in `fixtures/neutrogena/brand.json`. Stage leaks belong in `_STAGE_LEAKS` / `_is_postable`. Loop rewrite goes through numbered reasons, not a new mega-prompt.

## Change on-screen words

`apps/web/desk/words.ts` + `docs/conventions/words-we-use.md` + runbook if the employee steps change. Never put `deep_dive` on a button.

## Lengthen timeouts

You are trading Grok cost and a 5-minute spinner. Touch all of: LiteLLM `CHAT_TIMEOUT_S` (default 90), Imagine 90s, researcher budget, Next `maxDuration` + `PROXY_MS`. Then walk Look and Make on `/engine`, not only pytest.

## New box

Do not. Same 17. If you truly need a new one: written note (owns / must not own / flow / failure), architecture map panel with “who already does this,” then code. Update `docs/agents/boxes.md`.

## After any change

- Stay on D:
- Tests that would fail if it broke (not only “build passes”)
- Computed values shown, logged, or tested
- No secrets in git
- User errors stay friendly
