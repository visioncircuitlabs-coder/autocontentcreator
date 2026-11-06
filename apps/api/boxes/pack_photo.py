"""Real pack photo for Chile Limón — the bag in the ad, not an Imagine remix.

The campaign still composites or image-edits FROM this JPEG so logo, 25% MORE,
Chile Limón Flavour, veg mark, and lime/chilli/garlic art stay the provided pack.
I2V still refuses this path as draft.image_path (it lives under fixtures/).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from boxes.brand_pack import FIXTURES_DIR
from boxes.visual import CHILE_LIMON_TYPE, is_chile_limon_pack
from models import Draft

FEED_SIZE = (1080, 1350)
PACK_RELATIVE = Path("lays") / "products" / "chile-limon.jpg"
# Workspace copy the founder dropped next to the repo (optional).
WORKSPACE_PACK = Path("/workspace/lays/chile-limon.jpg")
LIME_FIELD = (118, 176, 42, 255)
CHILLI_RED = (196, 40, 36, 255)
LIME_ZEST = (214, 232, 92, 255)
TYPE_FILL = (18, 28, 12, 255)
PACK_WIDTH_RATIO = 0.62


def chile_limon_pack_photo() -> Path | None:
    """Tracked India Chile Limón pack. Not Magic Masala. Not jalapeño."""
    tracked = FIXTURES_DIR / PACK_RELATIVE
    if tracked.is_file():
        return tracked.resolve()
    if WORKSPACE_PACK.is_file():
        return WORKSPACE_PACK.resolve()
    return None


def pack_photo_for(draft: Draft) -> Path | None:
    if not is_chile_limon_pack(draft):
        return None
    return chile_limon_pack_photo()


def pack_paste_box(
    pack_size: tuple[int, int],
    canvas: tuple[int, int] = FEED_SIZE,
) -> tuple[int, int, int, int]:
    """Where the real bag sits on the 4:5 canvas. Burst and type go around it."""
    cw, ch = canvas
    pw, ph = pack_size
    target_w = max(1, int(cw * PACK_WIDTH_RATIO))
    scale = target_w / max(pw, 1)
    nw, nh = max(1, int(pw * scale)), max(1, int(ph * scale))
    left = (cw - nw) // 2
    # Sit the bag slightly low so headline type has a clear top margin.
    top = int(ch * 0.22) + max(0, (int(ch * 0.58) - nh) // 2)
    return left, top, left + nw, top + nh


def composite_from_pack(pack_path: Path | str, dest: Path | str) -> Path:
    """Paste the provided pack onto a lime field. Type and burst around it.

    Does not stamp a second LAY'S wordmark. Does not stamp unofficial/disclaimer.
    """
    src = Path(pack_path)
    if not src.is_file():
        raise RuntimeError("The Chile Limón pack photo is missing.")
    out = Path(dest)
    out.parent.mkdir(parents=True, exist_ok=True)

    canvas = Image.new("RGBA", FEED_SIZE, LIME_FIELD)
    draw = ImageDraw.Draw(canvas)
    _paint_burst(draw, canvas.size)
    pack = Image.open(src).convert("RGB")
    box = pack_paste_box(pack.size, FEED_SIZE)
    nw, nh = box[2] - box[0], box[3] - box[1]
    placed = pack.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(placed, (box[0], box[1]))
    _paint_type(draw, canvas.size)
    canvas.convert("RGB").save(out, "PNG")
    return out


def _paint_burst(draw: ImageDraw.ImageDraw, size: tuple[int, int]) -> None:
    """Flavour exploding out of the open bag — lime + red chilli, not jalapeño."""
    width, height = size
    cx, cy = width // 2, int(height * 0.28)
    blobs = (
        (cx - 280, cy - 40, 90, 54, LIME_ZEST),
        (cx + 210, cy - 10, 84, 50, CHILLI_RED),
        (cx - 330, cy + 90, 70, 38, CHILLI_RED),
        (cx + 300, cy + 70, 76, 42, LIME_ZEST),
        (cx - 200, cy + 220, 60, 34, CHILLI_RED),
        (cx + 190, cy + 240, 64, 36, LIME_ZEST),
        (cx - 40, cy - 90, 48, 28, CHILLI_RED),
        (cx + 40, cy - 80, 52, 30, LIME_ZEST),
    )
    for x, y, rw, rh, fill in blobs:
        draw.ellipse([x - rw, y - rh, x + rw, y + rh], fill=fill)


def _paint_type(draw: ImageDraw.ImageDraw, size: tuple[int, int]) -> None:
    from adapters.image_stub import _font

    w, h = size
    headline = _font(54)
    sub = _font(42)
    dare = _font(48)
    lines = CHILE_LIMON_TYPE
    fonts = (headline, sub, dare)
    ys = (int(h * 0.045), int(h * 0.84), int(h * 0.91))
    for text, font, y in zip(lines, fonts, ys, strict=True):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2 - bbox[0]
        # Soft plate behind type so it reads on the lime field — not a legal bar.
        pad = 14
        draw.rounded_rectangle(
            [x - pad, y - 8, x + tw + pad, y + (bbox[3] - bbox[1]) + 12],
            radius=10,
            fill=(244, 248, 220, 235),
        )
        draw.text((x, y), text, font=font, fill=TYPE_FILL)
