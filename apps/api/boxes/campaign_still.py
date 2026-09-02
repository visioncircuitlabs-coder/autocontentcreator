"""Campaign still: flavour explosion + designed type.

Used when Imagine is off or fails. This must read as a snack ad, not a
catalog JPEG with rounded UI chips glued on. The pack already carries the
Lay's mark — do not paint a second wordmark.
"""

from __future__ import annotations

import logging
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from boxes.brand_pack import load_brand_pack
from boxes.products import pack_photo, product_label

logger = logging.getLogger(__name__)

FEED_SIZE = (1080, 1350)
EMERALD = (4, 28, 18)
LIME = (176, 214, 74)
CHILLI = (196, 40, 36)
GOLD = (228, 168, 52)
WHITE = (255, 255, 255)

# Chile Limón lockup — heat + lime, not generic "delicious chips".
CHILE_HEADLINE = ("TANGY LIME.", "SPICY HIT.")
CHILE_SLOGAN = "CRUNCH THE HEAT."
CHILE_CTA = "DARE A BITE?"


def flavour_art(sku: str | None) -> dict[str, object]:
    """Designed-type copy for the still. Tests lock Chile Limón to lime + chilli."""
    token = (sku or "").upper()
    if "CHILE" in token or "LIMON" in token:
        return {
            "headline": CHILE_HEADLINE,
            "slogan": CHILE_SLOGAN,
            "cta": CHILE_CTA,
            "burst": "lime_chilli",
        }
    name = product_label(sku) or "Lay's"
    return {
        "headline": (name.upper() + ".", "CRUNCH IT."),
        "slogan": "OPEN THE PACK.",
        "cta": "DARE A BITE?",
        "burst": "chips",
    }


def _typeface(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf")
        if bold
        else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf")
    )
    roots = (
        Path("C:/Windows/Fonts"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation"),
    )
    for root in roots:
        for name in names:
            path = root / name
            if path.is_file():
                try:
                    return ImageFont.truetype(str(path), size=size)
                except OSError:
                    continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


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


def _radial_studio(size: tuple[int, int] = FEED_SIZE) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, EMERALD)
    draw = ImageDraw.Draw(img)
    draw.ellipse([-280, 520, 1360, 1680], fill=(3, 22, 14))
    draw.ellipse([520, -200, 1400, 420], fill=(10, 48, 28))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    # Hot radial behind the burst, slightly above bag mouth.
    gdraw.ellipse([180, 80, 900, 820], fill=(255, 255, 210, 70))
    gdraw.ellipse([300, 200, 780, 680], fill=(210, 230, 90, 90))
    gdraw.ellipse([360, 260, 720, 620], fill=(255, 250, 200, 110))
    gdraw.ellipse([-120, 900, 420, 1480], fill=(*LIME, 40))
    gdraw.ellipse([700, 40, 1200, 500], fill=(*CHILLI, 32))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(48)))
    return img


def _paste(canvas: Image.Image, sprite: Image.Image, cx: int, cy: int) -> None:
    x = int(cx - sprite.width / 2)
    y = int(cy - sprite.height / 2)
    canvas.alpha_composite(sprite, (x, y))


def _chip(size: int, angle: float) -> Image.Image:
    w, h = max(28, size), max(18, int(size * 0.62))
    img = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([8, h - 4, w + 10, h + 14], fill=(20, 10, 0, 90))
    body = [4, 4, 4 + w, 4 + h]
    d.rounded_rectangle(body, radius=max(8, h // 3), fill=(214, 150, 40, 255))
    d.rounded_rectangle(
        [8, 7, 4 + w - 6, 4 + h - 5],
        radius=max(6, h // 4),
        fill=(236, 188, 72, 255),
    )
    ridge = max(5, w // 9)
    for x in range(12, w - 4, ridge):
        d.line([(x, 10), (x, 4 + h - 8)], fill=(186, 112, 28, 200), width=2)
    d.arc([6, 6, w // 2 + 8, h], start=200, end=350, fill=(255, 236, 170, 220), width=3)
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def _lime_wedge(size: int, angle: float) -> Image.Image:
    s = max(28, size)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.pieslice([2, 2, s - 2, s - 2], start=200, end=325, fill=(198, 214, 64, 255))
    d.pieslice([8, 8, s - 8, s - 8], start=200, end=325, fill=(220, 230, 96, 255))
    cx, cy = s // 2, s // 2
    for deg in range(208, 320, 16):
        rad = math.radians(deg)
        d.line(
            [cx, cy, cx + int(math.cos(rad) * s * 0.38), cy + int(math.sin(rad) * s * 0.38)],
            fill=(150, 168, 36, 210),
            width=1,
        )
    d.arc([2, 2, s - 2, s - 2], start=200, end=325, fill=(92, 128, 28, 255), width=4)
    d.pieslice([2, 2, s - 2, s - 2], start=198, end=328, outline=(70, 100, 24, 255), width=2)
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def _chilli(size: int, angle: float) -> Image.Image:
    w = max(18, int(size * 0.42))
    h = max(40, int(size * 1.7))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([int(w * 0.12), int(h * 0.08), int(w * 0.88), int(h * 0.72)], fill=(*CHILLI, 255))
    d.ellipse([int(w * 0.18), int(h * 0.42), int(w * 0.82), int(h * 0.96)], fill=(168, 24, 28, 255))
    d.ellipse(
        [int(w * 0.28), int(h * 0.14), int(w * 0.52), int(h * 0.42)],
        fill=(230, 92, 70, 170),
    )
    d.ellipse([int(w * 0.36), 0, int(w * 0.64), int(h * 0.12)], fill=(46, 96, 36, 255))
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def _garlic(size: int, angle: float) -> Image.Image:
    s = max(16, size)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([2, 6, s - 2, s - 2], fill=(236, 228, 210, 255))
    d.ellipse([s // 3, 2, 2 * s // 3, s // 3], fill=(220, 210, 190, 255))
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def _spray(size: tuple[int, int], ox: int, oy: int, rng: random.Random) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for _ in range(90):
        dist = rng.randint(20, 380)
        ang = math.radians(rng.uniform(-150, -30))
        x = ox + int(math.cos(ang) * dist)
        y = oy + int(math.sin(ang) * dist)
        r = rng.randint(2, 8)
        tone = rng.choice(((*LIME, rng.randint(70, 180)), (255, 255, 230, rng.randint(50, 140)), (*CHILLI, rng.randint(60, 140))))
        d.ellipse([x - r, y - r, x + r, y + r], fill=tone)
    for _ in range(40):
        dist = rng.randint(40, 300)
        ang = math.radians(rng.uniform(-140, -40))
        x = ox + int(math.cos(ang) * dist)
        y = oy + int(math.sin(ang) * dist)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(180, 40, 30, 160))
    return layer.filter(ImageFilter.GaussianBlur(1.2))


def _streaks(size: tuple[int, int], ox: int, oy: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for deg in (-130, -110, -90, -70, -50, -35):
        rad = math.radians(deg)
        x2 = ox + int(math.cos(rad) * 420)
        y2 = oy + int(math.sin(rad) * 420)
        d.line([(ox, oy), (x2, y2)], fill=(255, 255, 210, 28), width=3)
    return layer.filter(ImageFilter.GaussianBlur(2))


def _burst(canvas: Image.Image, ox: int, oy: int, *, lime_chilli: bool) -> None:
    rng = random.Random(11)
    canvas.alpha_composite(_streaks(canvas.size, ox, oy))
    canvas.alpha_composite(_spray(canvas.size, ox, oy, rng))
    items: list[tuple[str, int, float, int, float]] = [
        ("chip", 95, -100, 88, 22),
        ("chip", 150, -78, 108, -16),
        ("chip", 200, -58, 92, 34),
        ("chip", 165, -28, 118, -28),
        ("chip", 230, -12, 76, 14),
        ("chip", 255, -118, 70, -38),
        ("chip", 120, -88, 100, 8),
        ("chip", 280, -42, 64, 26),
        ("chip", 190, -140, 72, -12),
    ]
    if lime_chilli:
        items.extend(
            [
                ("lime", 210, -96, 90, 18),
                ("lime", 250, -40, 78, -22),
                ("lime", 175, -18, 84, 36),
                ("lime", 300, -70, 62, -8),
                ("chilli", 220, -8, 78, 58),
                ("chilli", 185, -125, 70, -48),
                ("chilli", 268, 8, 58, 24),
                ("garlic", 140, -50, 34, 12),
            ]
        )
    makers = {"chip": _chip, "lime": _lime_wedge, "chilli": _chilli, "garlic": _garlic}
    for kind, dist, deg, size, spin in items:
        rad = math.radians(deg)
        x = ox + int(math.cos(rad) * dist)
        y = oy + int(math.sin(rad) * dist)
        sprite = makers[kind](size, spin)
        _paste(canvas, sprite, x, y)


def _distress(layer: Image.Image, seed: int = 5) -> Image.Image:
    """Nick the letter edges so type reads as print, not a UI label."""
    rng = random.Random(seed)
    pix = layer.load()
    w, h = layer.size
    punches = max(80, (w * h) // 55)
    for _ in range(punches):
        x = rng.randrange(w)
        y = rng.randrange(h)
        r, g, b, a = pix[x, y]
        if a < 40:
            continue
        pix[x, y] = (r, g, b, 0 if rng.random() < 0.55 else max(0, a - 140))
        if rng.random() < 0.4 and 0 < x < w - 1 and 0 < y < h - 1:
            pix[x + 1, y] = (r, g, b, max(0, a // 3))
    return layer


def _text_layer(
    lines: tuple[str, ...] | str,
    size: int,
    *,
    angle: float,
    fills: tuple[tuple[int, int, int, int], ...] | None = None,
) -> Image.Image:
    rows = lines if isinstance(lines, tuple) else (lines,)
    font = _typeface(size, bold=True)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    widths: list[int] = []
    heights: list[int] = []
    for line in rows:
        box = probe.textbbox((0, 0), line, font=font)
        widths.append(box[2] - box[0])
        heights.append(box[3] - box[1])
    gap = max(8, size // 8)
    img = Image.new(
        "RGBA",
        (max(widths) + 28, sum(heights) + gap * (len(rows) - 1) + 28),
        (0, 0, 0, 0),
    )
    d = ImageDraw.Draw(img, "RGBA")
    y = 8
    for index, (line, tw, th) in enumerate(zip(rows, widths, heights, strict=True)):
        fill = (255, 255, 255, 255)
        if fills and index < len(fills):
            fill = fills[index]
        d.text((10, y + 5), line, font=font, fill=(0, 0, 0, 150))
        d.text((6, y), line, font=font, fill=fill)
        y += th + gap
    return _distress(img).rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def _brush_banner(text: str) -> Image.Image:
    """Irregular painted banner — not a rounded-rect Shop-now pill."""
    font = _typeface(34, bold=True)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    box = probe.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    w, h = tw + 100, th + 78
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(9)

    def _smear(fill: tuple[int, int, int, int], jitter: int, y_shift: int) -> None:
        top = [
            (8 + i * (w - 16) / 7, 16 + y_shift + rng.randint(-jitter, jitter))
            for i in range(8)
        ]
        bot = [
            (w - 8 - i * (w - 16) / 7, h - 14 + y_shift + rng.randint(-jitter, jitter))
            for i in range(8)
        ]
        d.polygon([*top, *bot], fill=fill)

    _smear((132, 186, 36, 250), 14, 0)
    rng.seed(4)
    _smear((*LIME, 235), 18, 4)
    rng.seed(2)
    _smear((196, 40, 36, 40), 10, 8)
    tx = (w - tw) // 2 - box[0] + 8
    ty = (h - th) // 2 - box[1] - 2
    d.text((tx + 2, ty + 2), text, font=font, fill=(8, 22, 8, 140))
    d.text((tx, ty), text, font=font, fill=(18, 36, 14, 255))
    chilli = _chilli(28, 18)
    img.alpha_composite(chilli, (8, h // 2 - chilli.height // 2))
    return img.rotate(-11, resample=Image.Resampling.BICUBIC, expand=True)


def _designed_type(canvas: Image.Image, art: dict[str, object]) -> None:
    headline = art["headline"]
    assert isinstance(headline, tuple)
    lockup = _text_layer(
        headline,
        76,
        angle=12,
        fills=((255, 255, 255, 255), (*LIME, 255)),
    )
    canvas.alpha_composite(lockup, (8, 36))
    slogan = _text_layer(str(art["slogan"]), 30, angle=-8)
    canvas.alpha_composite(slogan, (canvas.width - slogan.width - 18, 760))
    banner = _brush_banner(str(art["cta"]))
    canvas.alpha_composite(banner, (canvas.width - banner.width - 8, 1070))


def paint_campaign_still(
    dest: Path,
    *,
    sku: str | None = None,
    slug: str | None = None,
) -> Path:
    """Write a 4:5 campaign PNG: pack + explosion + designed type."""
    pack = load_brand_pack(slug)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h = FEED_SIZE
    canvas = _radial_studio().convert("RGBA")
    art = flavour_art(sku)
    lime_chilli = art.get("burst") == "lime_chilli"

    photo = pack_photo(sku, slug)
    bag_top = int(h * 0.46)
    ox, oy = w // 2, bag_top + 36
    # Far burst sits behind the bag so the mouth feels open.
    _burst(canvas, ox, oy - 30, lime_chilli=lime_chilli)

    if photo is not None:
        bag = _cut_studio_bg(Image.open(photo))
        target_h = int(h * 0.48)
        ratio = target_h / max(bag.height, 1)
        bag = bag.resize(
            (max(80, int(bag.width * ratio)), target_h),
            Image.Resampling.LANCZOS,
        )
        shadow = Image.new("RGBA", (bag.width + 90, 120), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow, "RGBA")
        sdraw.ellipse([10, 20, bag.width + 80, 110], fill=(0, 0, 0, 130))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        bx = (w - bag.width) // 2
        by = bag_top
        canvas.alpha_composite(shadow, ((w - shadow.width) // 2, by + bag.height - 70))
        canvas.alpha_composite(bag, (bx, by))
    else:
        label = product_label(sku, slug) or pack["name"]
        font = _typeface(48, bold=True)
        draw = ImageDraw.Draw(canvas, "RGBA")
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text(((w - (bbox[2] - bbox[0])) // 2, h // 2), label, font=font, fill=(255, 255, 255, 240))

    # Near burst overlaps the bag mouth only (upward), not the Lay's mark.
    rng = random.Random(17)
    near = (
        ("chip", 70, -70, 96, 16),
        ("chip", 110, -48, 80, -22),
        ("lime", 90, -100, 70, 12) if lime_chilli else ("chip", 90, -100, 70, 12),
        ("chilli", 100, -28, 64, 40) if lime_chilli else ("chip", 100, -28, 64, 40),
    )
    makers = {"chip": _chip, "lime": _lime_wedge, "chilli": _chilli}
    for kind, dist, deg, size, spin in near:
        rad = math.radians(deg)
        x = ox + int(math.cos(rad) * dist) + rng.randint(-8, 8)
        y = oy + int(math.sin(rad) * dist) - 24
        _paste(canvas, makers[kind](size, spin), x, y)

    _designed_type(canvas, art)

    popped = ImageEnhance.Contrast(canvas.convert("RGB")).enhance(1.08)
    popped = ImageEnhance.Color(popped).enhance(1.12)
    popped.save(dest, "PNG")
    logger.info("campaign still wrote %s sku=%s", dest, sku)
    return dest
