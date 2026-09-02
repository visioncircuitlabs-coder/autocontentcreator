"""Campaign still from a real pack photo. Used when Imagine is off or fails.

This is not a catalog JPEG: the pack sits in a 4:5 lime/chilli scene.
The pack already carries the Lay's mark — do not paint a second wordmark here.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from adapters.image_stub import _font
from boxes.brand_pack import load_brand_pack
from boxes.products import pack_photo, product_label

logger = logging.getLogger(__name__)

FEED_SIZE = (1080, 1350)
EMERALD = (6, 42, 28)
LIME = (176, 214, 74)
CHILLI = (196, 48, 42)
GOLD = (232, 176, 64)


def _cut_studio_bg(src: Image.Image) -> Image.Image:
    """Soft-key near-white studio backdrop so the bag can sit on a campaign scene."""
    rgba = src.convert("RGBA")
    pixels = list(rgba.getdata())
    cut: list[tuple[int, int, int, int]] = []
    for r, g, b, a in pixels:
        luma = (r + g + b) / 3
        if luma >= 236 and abs(r - g) < 18 and abs(g - b) < 18:
            cut.append((r, g, b, 0))
        elif luma >= 210 and abs(r - g) < 28 and abs(g - b) < 28:
            fade = int(255 * (1 - (luma - 210) / 46))
            cut.append((r, g, b, max(0, min(a, fade))))
        else:
            cut.append((r, g, b, a))
    rgba.putdata(cut)
    return rgba


def _scene(size: tuple[int, int] = FEED_SIZE) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, EMERALD)
    draw = ImageDraw.Draw(img)
    draw.ellipse([-220, -180, 980, 980], fill=(18, 92, 52))
    draw.ellipse([420, 780, 1380, 1580], fill=(10, 58, 34))
    draw.ellipse([620, -120, 1320, 460], fill=(28, 78, 40))
    return img


def paint_campaign_still(
    dest: Path,
    *,
    sku: str | None = None,
    slug: str | None = None,
) -> Path:
    """Write a 4:5 campaign PNG using the pack photo when we have one."""
    pack = load_brand_pack(slug)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h = FEED_SIZE
    canvas = _scene().convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Lime wash + chilli rim so it reads as an ad, not a white-background pack shot.
    glow = Image.new("RGBA", FEED_SIZE, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    gdraw.ellipse([-180, 720, 620, 1500], fill=(*LIME, 48))
    gdraw.ellipse([540, -80, 1280, 520], fill=(*CHILLI, 36))
    gdraw.ellipse([200, 180, 900, 980], fill=(255, 255, 255, 18))
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(42)))
    draw = ImageDraw.Draw(canvas, "RGBA")

    for i, radius in enumerate((210, 340, 490, 660)):
        box = [w // 2 - radius, 340 - radius, w // 2 + radius, 340 + radius]
        draw.ellipse(box, outline=(*LIME, 28 + i * 6), width=3)

    photo = pack_photo(sku, slug)
    if photo is not None:
        bag = _cut_studio_bg(Image.open(photo))
        target_h = int(h * 0.72)
        ratio = target_h / max(bag.height, 1)
        bag = bag.resize(
            (max(80, int(bag.width * ratio)), target_h),
            Image.Resampling.LANCZOS,
        )
        shadow = Image.new("RGBA", (bag.width + 80, bag.height + 80), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow, "RGBA")
        sdraw.ellipse([20, bag.height - 40, bag.width + 60, bag.height + 70], fill=(0, 0, 0, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        sx = (w - shadow.width) // 2
        sy = h - shadow.height - 90
        canvas.alpha_composite(shadow, (sx, sy))
        bx = (w - bag.width) // 2
        by = int(h * 0.14)
        canvas.alpha_composite(bag, (bx, by))
    else:
        label = product_label(sku, slug) or pack["name"]
        font = _font(54)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, h // 2 - 40), label, font=font, fill=(255, 255, 255, 240))

    dest_rgb = canvas.convert("RGB")
    dest_rgb.save(dest, "PNG")
    logger.info("campaign still wrote %s sku=%s", dest, sku)
    return dest
