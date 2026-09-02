"""Art Director — unlocked ImageGen + coded logo/disclaimer overlay."""

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
from models import Draft
from ports import ImageGen

logger = logging.getLogger(__name__)

DEFAULT_SIZE_TOKEN = "1080x1350"
FEED_SIZE = (1080, 1350)  # Instagram 4:5
LOGO_NAVY = (11, 61, 145, 255)
LOGO_WHITE = (255, 255, 255, 255)


def rasterize_logo(svg_path: Path | None = None) -> Image.Image:
    """Paint the unofficial wordmark in code. SVG path is kept for fixture identity."""
    pack = load_brand_pack()
    _ = svg_path or pack["logo_path"]
    wordmark = str(pack.get("wordmark") or pack.get("name") or "BRAND")
    width, height = 360, 56
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=8, fill=LOGO_NAVY)
    font = _font(22)
    bbox = draw.textbbox((0, 0), wordmark, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) // 2 - bbox[0]
    y = (height - th) // 2 - bbox[1]
    draw.text((x, y), wordmark, font=font, fill=LOGO_WHITE)
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


def apply_locks(image_path: Path, *, logo_path: Path | None = None) -> None:
    """Overlay brand locks in code. Lays: disclaimer only — pack already has the mark."""
    pack = load_brand_pack()
    dest = Path(image_path)
    try:
        raw = Image.open(dest)
    except Exception as exc:
        logger.warning("compose could not open generated image: %s", exc)
        raise RuntimeError("The generated picture could not be opened. Try stub mode.") from exc

    img = _to_feed(raw)
    w, h = img.size
    pad = max(20, w // 28)
    if pack.get("overlay_wordmark", True):
        logo = rasterize_logo(logo_path)
        target_w = max(120, int(w * 0.28))
        ratio = target_w / max(logo.width, 1)
        logo = logo.resize(
            (target_w, max(28, int(logo.height * ratio))),
            Image.Resampling.LANCZOS,
        )
        img.alpha_composite(logo, (pad, pad))

    if pack.get("overlay_disclaimer", True):
        disc = (load_disclaimer() or "").strip()
        if disc:
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


def _sku_for(draft: Draft) -> str:
    try:
        from boxes.brief import load_brief

        brief = load_brief(draft.brief_id)
        return str(brief.sku or "")
    except Exception:
        from boxes.products import hero_sku

        return hero_sku()


def compose(
    draft: Draft,
    prompt: str,
    *,
    image_gen: ImageGen | None = None,
    out_path: Path | str | None = None,
    client: httpx.Client | None = None,
) -> Draft:
    """Generate the picture, then overlay locks in code.

    Lays stub/fallback paints a campaign still from the real pack photo so the
    phone preview is never a raw catalog JPEG or a dark placeholder card.
    """
    pack = load_brand_pack()
    gen = image_gen or build_image_gen(client=client)
    dest = Path(out_path) if out_path is not None else _default_out_path(draft)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sku = _sku_for(draft)
    campaign = pack.get("slug") == "lays"

    def _campaign() -> None:
        from boxes.campaign_still import paint_campaign_still

        paint_campaign_still(dest, sku=sku)

    try:
        if image_gen is None and campaign and type(gen).__name__ == "StubImageGen":
            _campaign()
        else:
            gen.generate(prompt, dest)
    except Exception as exc:
        if type(gen).__name__ == "StubImageGen" and not campaign:
            raise
        logger.warning("image gen failed (%s); drawing a fallback still", exc)
        if campaign:
            _campaign()
        else:
            StubImageGen().generate(prompt, dest)
    apply_locks(dest)
    logger.info("art director wrote %s", dest)
    return draft.model_copy(update={"image_path": str(dest.resolve())})
