"""Free ImageGen adapter: dark card + headline. Logo/disclaimer overlay happens in compose."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

STUB_SIZE = (1080, 1080)
BG = (15, 17, 23)
FG = (232, 234, 240)
MUTED = (154, 161, 178)


def _font(size: int) -> ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    )
    for path in candidates:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _headline(prompt: str) -> str:
    line = (prompt or "").strip().splitlines()[0] if prompt else ""
    return (line[:96] if line else "Draft").strip()


class StubImageGen:
    """Unlocked zone only: dark Instagram card with the prompt as headline."""

    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        source_image: Path | None = None,
    ) -> Path:
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source_image is not None:
            from boxes.pack_photo import composite_from_pack

            return composite_from_pack(source_image, dest)

        width, height = STUB_SIZE
        img = Image.new("RGB", STUB_SIZE, BG)
        draw = ImageDraw.Draw(img)
        font = _font(52)
        small = _font(22)
        lines = _wrap(draw, _headline(prompt), font, width - 160)[:4]
        y = 360
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(((width - tw) // 2, y), line, fill=FG, font=font)
            y += th + 14
        hint = "unlocked zone · brand marks added in code"
        hb = draw.textbbox((0, 0), hint, font=small)
        draw.text(((width - (hb[2] - hb[0])) // 2, y + 24), hint, fill=MUTED, font=small)

        img.save(dest, "PNG")
        return dest
