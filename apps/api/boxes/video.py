"""Art Director video — image-to-video from the campaign still.

Neutrogena: coded overlay after generate so the legal line cannot warp.
Chile Limón: no Pillow wordmark/disclaimer (overlay_disclaimer=false).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx

from adapters.video_imagine import ImagineVideoGen
from adapters.video_stub import StubVideoGen
from boxes.art_director import stamp_locks, write_locks_overlay
from boxes.video_encode import overlay_locks_on_video, scale_video_to_feed
from models import Draft
from ports import VideoGen

logger = logging.getLogger(__name__)

DURATION_S = 5.0
PICTURE_FIRST = "Make the picture first. Then we can make a short video."


def _default_out_path(draft: Draft) -> Path:
    override = os.environ.get("VIDEO_OUT_DIR")
    if override:
        root = Path(override)
    else:
        sqlite = Path(os.environ.get("SQLITE_PATH") or "data/demo.db")
        root = sqlite.resolve().parent / "videos"
    return root / f"{draft.draft_id}.mp4"


def campaign_still(draft: Draft, *, source_image: Path | str | None = None) -> Path | None:
    """The composed campaign still only. Never a fixture pack photo."""
    raw = (
        str(source_image).strip()
        if source_image is not None
        else (draft.image_path or "").strip()
    )
    if not raw:
        return None
    path = Path(raw)
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if not resolved.is_file():
        return None
    if "fixtures" in {part.lower() for part in resolved.parts}:
        return None
    return resolved


def build_video_gen(
    *,
    mode: str | None = None,
    client: httpx.Client | None = None,
) -> VideoGen:
    selected = (
        mode
        if mode is not None
        else os.environ.get("VIDEO_GEN_MODE")
        or os.environ.get("IMAGE_GEN_MODE")
        or "stub"
    ).strip().lower()
    if selected in {
        "imagine",
        "grok-imagine",
        "grok_imagine",
        "grok-imagine-video",
        "grok_imagine_video",
    }:
        return ImagineVideoGen(client=client)
    if selected not in {"", "stub"}:
        logger.warning("unknown VIDEO_GEN_MODE=%s; using stub", selected)
    return StubVideoGen()


def compose_video(
    draft: Draft,
    prompt: str,
    *,
    video_gen: VideoGen | None = None,
    out_path: Path | str | None = None,
    client: httpx.Client | None = None,
    source_image: Path | str | None = None,
) -> Draft:
    """Animate the campaign still. Overlay only when stamp_locks says so."""
    still = campaign_still(draft, source_image=source_image)
    if still is None or not still.is_file():
        raise ValueError(PICTURE_FIRST)
    gen = video_gen or build_video_gen(client=client)
    dest = Path(out_path) if out_path is not None else _default_out_path(draft)
    dest.parent.mkdir(parents=True, exist_ok=True)
    unlocked = dest.with_name(f"{dest.stem}.unlocked.mp4")
    overlay = dest.with_name(f"{dest.stem}.locks.png")
    try:
        try:
            gen.generate(prompt, unlocked, source_image=still)
        except ValueError:
            raise
        except Exception as exc:
            if type(gen).__name__ == "StubVideoGen":
                raise
            logger.warning("video gen failed (%s); drawing a stub clip", exc)
            StubVideoGen().generate(prompt, unlocked, source_image=still)
        if stamp_locks(draft):
            write_locks_overlay(overlay)
            overlay_locks_on_video(unlocked, overlay, dest, seconds=DURATION_S)
        else:
            scale_video_to_feed(unlocked, dest, seconds=DURATION_S)
    finally:
        unlocked.unlink(missing_ok=True)
        overlay.unlink(missing_ok=True)
    logger.info("art director wrote video %s", dest)
    return draft.model_copy(update={"video_path": str(dest.resolve())})
