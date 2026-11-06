"""Art Director — Imagine still, then optional Pillow logo/disclaimer overlay.

Neutrogena: unlocked ImageGen, then coded navy wordmark + disclaimer bar.
Chile Limón: edit/composite FROM the provided pack photo. Overlay skips
(overlay_disclaimer=false, always_disclaimer=false). Do not stamp a second LAY'S.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

from adapters.image_http import HttpImageGen
from adapters.image_imagine import ImagineImageGen
from adapters.image_stub import StubImageGen, _font, _wrap
from boxes.brand_pack import load_brand_pack
from boxes.hard_rules import load_disclaimer
from boxes.pack_photo import composite_from_pack, pack_photo_for
from models import Draft
from ports import ImageGen

logger = logging.getLogger(__name__)

_PACK = load_brand_pack()
DEFAULT_LOGO_PATH = _PACK["logo_path"]
DEFAULT_SIZE_TOKEN = "1080x1350"
FEED_SIZE = (1080, 1350)  # Instagram 4:5
LOGO_NAVY = (11, 61, 145, 255)
LOGO_WHITE = (255, 255, 255, 255)
WORDMARK = _PACK["wordmark"]


def rasterize_logo(svg_path: Path | None = None) -> Image.Image:
    """Paint the unofficial wordmark in code. SVG path is kept for fixture identity."""
    _ = svg_path or DEFAULT_LOGO_PATH
    width, height = 360, 56
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=8, fill=LOGO_NAVY)
    font = _font(22)
    bbox = draw.textbbox((0, 0), WORDMARK, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) // 2 - bbox[0]
    y = (height - th) // 2 - bbox[1]
    draw.text((x, y), WORDMARK, font=font, fill=LOGO_WHITE)
    return img


def _to_feed(img: Image.Image) -> Image.Image:
    """Crop-cover to Instagram 4:5 so overlays are never sliced off in the phone frame."""
    tw, th = FEED_SIZE
    src = img.convert("RGBA")
    sw, sh = src.size
    if sw < 8 or sh < 8:
        canvas = Image.new("RGBA", FEED_SIZE, (20, 22, 28, 255))
        return canvas
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    scaled = src.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return scaled.crop((left, top, left + tw, top + th))


def locks_overlay_image(
    *,
    logo_path: Path | None = None,
    size: tuple[int, int] = FEED_SIZE,
) -> Image.Image:
    """Transparent 4:5 sheet: wordmark + disclaimer bar. Never sent to a model."""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pad = max(20, w // 28)
    logo = rasterize_logo(logo_path)
    target_w = max(120, int(w * 0.28))
    ratio = target_w / max(logo.width, 1)
    logo = logo.resize(
        (target_w, max(28, int(logo.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    img.alpha_composite(logo, (pad, pad))

    disc = (load_disclaimer() or "").strip()
    draw = ImageDraw.Draw(img)
    font = _font(max(16, h // 54))
    lines = _wrap(draw, disc, font, w - pad * 2) or [disc]
    line_h = 0
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        line_h = max(line_h, box[3] - box[1])
    bar_h = pad + len(lines) * (line_h + 6) + pad
    bar_h = min(max(bar_h, 56), h // 4)
    bar = Image.new("RGBA", (w, bar_h), (12, 14, 22, 220))
    img.alpha_composite(bar, (0, h - bar_h))
    y = h - bar_h + pad
    fill = (232, 234, 240, 255)
    for line in lines:
        draw.text((pad, y), line, font=font, fill=fill)
        y += line_h + 6
    return img


def write_locks_overlay(path: Path, *, logo_path: Path | None = None) -> Path:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    locks_overlay_image(logo_path=logo_path).save(dest, "PNG")
    return dest


def stamp_locks(draft: Draft | None = None) -> bool:
    """Pillow wordmark + disclaimer. Off for Chile Limón (founder override)."""
    if draft is not None:
        from boxes.visual import is_chile_limon_pack

        if is_chile_limon_pack(draft):
            return False
    pack = load_brand_pack()
    if pack.get("overlay_disclaimer") is False and pack.get("overlay_wordmark") is False:
        return False
    if pack.get("always_disclaimer") is False and pack.get("overlay_disclaimer") is False:
        return bool(pack.get("overlay_wordmark"))
    return True


def _write_feed(image_path: Path) -> None:
    dest = Path(image_path)
    try:
        raw = Image.open(dest)
    except Exception as exc:
        logger.warning("compose could not open generated image: %s", exc)
        raise RuntimeError("The generated picture could not be opened. Try stub mode.") from exc
    img = _to_feed(raw)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, "PNG")


def _call_generate(gen: ImageGen, prompt: str, dest: Path, source_image: Path | None) -> Path:
    try:
        if source_image is not None:
            return gen.generate(prompt, dest, source_image=source_image)
        return gen.generate(prompt, dest)
    except TypeError:
        return gen.generate(prompt, dest)


def apply_locks(image_path: Path, *, logo_path: Path | None = None) -> None:
    """Paste wordmark and the full disclaimer as a thin legal line. Not in the model."""
    dest = Path(image_path)
    try:
        raw = Image.open(dest)
    except Exception as exc:
        logger.warning("compose could not open generated image: %s", exc)
        raise RuntimeError("The generated picture could not be opened. Try stub mode.") from exc

    img = _to_feed(raw)
    img.alpha_composite(locks_overlay_image(logo_path=logo_path, size=img.size))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, "PNG")


def _default_out_path(draft: Draft) -> Path:
    override = os.environ.get("IMAGE_OUT_DIR")
    if override:
        root = Path(override)
    else:
        sqlite = Path(os.environ.get("SQLITE_PATH") or "data/demo.db")
        root = sqlite.resolve().parent / "images"
    return root / f"{draft.draft_id}.png"


def build_image_gen(
    *,
    mode: str | None = None,
    client: httpx.Client | None = None,
) -> ImageGen:
    selected = (mode if mode is not None else os.environ.get("IMAGE_GEN_MODE") or "stub").strip().lower()
    if selected in {"imagine", "grok-imagine", "grok_imagine"}:
        return ImagineImageGen(client=client)
    if selected == "http":
        return HttpImageGen(client=client, size=DEFAULT_SIZE_TOKEN)
    if selected not in {"", "stub"}:
        logger.warning("unknown IMAGE_GEN_MODE=%s; using stub", selected)
    return StubImageGen()


def compose(
    draft: Draft,
    prompt: str,
    *,
    image_gen: ImageGen | None = None,
    out_path: Path | str | None = None,
    client: httpx.Client | None = None,
) -> Draft:
    """Make the campaign still. Chile Limón keeps the provided pack; Neutrogena overlays."""
    gen = image_gen or build_image_gen(client=client)
    dest = Path(out_path) if out_path is not None else _default_out_path(draft)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pack = pack_photo_for(draft)
    if pack is not None and not pack.is_file():
        raise RuntimeError("The Chile Limón pack photo is missing.")
    try:
        _call_generate(gen, prompt, dest, pack)
    except Exception as exc:
        if type(gen).__name__ == "StubImageGen":
            raise
        logger.warning("image gen failed (%s); drawing a stub card", exc)
        if pack is not None:
            composite_from_pack(pack, dest)
        else:
            StubImageGen().generate(prompt, dest)
    if stamp_locks(draft):
        apply_locks(dest)
    else:
        _write_feed(dest)
    logger.info("art director wrote %s", dest)
    return draft.model_copy(update={"image_path": str(dest.resolve())})
