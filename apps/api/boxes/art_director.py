"""Art Director — unlocked ImageGen + coded logo/disclaimer overlay."""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

from adapters.image_http import HttpImageGen
from adapters.image_stub import StubImageGen, _font, _wrap
from boxes.hard_rules import load_disclaimer
from models import Draft
from ports import ImageGen

logger = logging.getLogger(__name__)

DEFAULT_LOGO_PATH = (
    Path(__file__).resolve().parent.parent / "fixtures" / "neutrogena" / "logo.svg"
)
DEFAULT_SIZE_TOKEN = "1080x1080"


def _px(value: str | None, default: int) -> int:
    if not value:
        return default
    return int(float(str(value).strip().removesuffix("px")))


def _rgba(color: str | None) -> tuple[int, int, int, int]:
    raw = (color or "#000000").strip()
    if raw.startswith("#") and len(raw) == 7:
        return (int(raw[1:3], 16), int(raw[3:5], 16), int(raw[5:7], 16), 255)
    if raw.startswith("#") and len(raw) == 4:
        return (int(raw[1] * 2, 16), int(raw[2] * 2, 16), int(raw[3] * 2, 16), 255)
    return (0, 0, 0, 255)


def rasterize_logo(svg_path: Path | None = None) -> Image.Image:
    """Paint the fixture SVG with Pillow. No model, no cairo."""
    path = svg_path or DEFAULT_LOGO_PATH
    root = ET.parse(path).getroot()
    width = _px(root.get("width"), 240)
    height = _px(root.get("height"), 48)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag == "rect":
            x = _px(elem.get("x"), 0)
            y = _px(elem.get("y"), 0)
            w = _px(elem.get("width"), width)
            h = _px(elem.get("height"), height)
            rx = _px(elem.get("rx"), 0)
            fill = _rgba(elem.get("fill"))
            box = [x, y, x + max(w - 1, 0), y + max(h - 1, 0)]
            if rx:
                draw.rounded_rectangle(box, radius=rx, fill=fill)
            else:
                draw.rectangle(box, fill=fill)
        elif tag == "text":
            text = "".join(elem.itertext()).strip()
            if not text:
                continue
            x = float(elem.get("x") or 0)
            y = float(elem.get("y") or 0)
            size = max(8, _px(elem.get("font-size"), 14))
            fill = _rgba(elem.get("fill") or "#FFFFFF")
            font = _font(size)
            anchor = "ms" if (elem.get("text-anchor") or "") == "middle" else "ls"
            draw.text((x, y), text, font=font, fill=fill, anchor=anchor)
    return img


def apply_locks(image_path: Path, *, logo_path: Path | None = None) -> None:
    """Paste logo.svg and disclaimer.txt in code. Called after ImageGen.generate."""
    dest = Path(image_path)
    try:
        img = Image.open(dest).convert("RGBA")
    except Exception as exc:
        logger.warning("compose could not open generated image: %s", exc)
        raise RuntimeError("The generated picture could not be opened. Try stub mode.") from exc

    w, h = img.size
    pad = max(16, w // 24)
    logo = rasterize_logo(logo_path)
    target_w = max(80, int(w * 0.22))
    ratio = target_w / max(logo.width, 1)
    logo = logo.resize(
        (target_w, max(1, int(logo.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    img.alpha_composite(logo, (pad, pad))

    disc = load_disclaimer()
    bar_h = max(72, h // 7)
    bar = Image.new("RGBA", (w, bar_h), (12, 14, 22, 235))
    img.alpha_composite(bar, (0, h - bar_h))

    draw = ImageDraw.Draw(img)
    font = _font(max(14, h // 48))
    lines = _wrap(draw, disc, font, w - pad * 2)
    y = h - bar_h + max(12, bar_h // 8)
    fill = (232, 234, 240, 255)
    for line in lines[:5]:
        draw.text((pad, y), line, font=font, fill=fill)
        bbox = draw.textbbox((pad, y), line, font=font)
        y += (bbox[3] - bbox[1]) + 6

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
    """Generate the unlocked picture, then overlay logo + disclaimer in code."""
    gen = image_gen or build_image_gen(client=client)
    dest = Path(out_path) if out_path is not None else _default_out_path(draft)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Overlay logo/disclaimer in code. Never send them to ImageGen.
    gen.generate(prompt, dest)
    apply_locks(dest)
    logger.info("art director wrote %s", dest)
    return draft.model_copy(update={"image_path": str(dest.resolve())})
