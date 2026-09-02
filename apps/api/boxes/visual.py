"""Instagram feed picture prompt. Unlocked zone only. Brand marks stay in code."""

from __future__ import annotations

from models import Draft

# Real Hydro Boost / drugstore water-gel ads: 4:5 feed, bright, dewy, white lid,
# aqua gel, centered jar, empty margins. Not a night-rain still life.


def lighting_from_caption(caption: str) -> str:
    text = (caption or "").lower()
    if any(token in text for token in ("ac", "commute", "office")):
        return "cool bathroom daylight, indoor India, air-con clean"
    if any(token in text for token in ("night", "evening", "double cleanse")):
        return "warm evening bathroom light, still bright like a beauty ad"
    if any(token in text for token in ("monsoon", "humid", "rain")):
        return "bright monsoon daylight on dewy glass, no dark rooms"
    return "bright commercial beauty-studio daylight"


def visual_prompt(draft: Draft) -> str:
    light = lighting_from_caption(draft.caption or "")
    return (
        "Instagram beauty advertisement, 4:5 vertical feed, commercial product photo. "
        "Hero object: one closed clear jar of aqua-blue hyaluronic water gel moisturizer "
        "with a white screw lid, gel visible through the glass, fine dew on the jar. "
        "Jar sits centered on pale wet marble. Large empty margins above and below. "
        f"{light}. Sharp, clean, dewy, premium drugstore skincare. "
        "Fresh and bright like a water-gel moisturizer ad, not a night film still. "
        "No people, no hands, no text, no letters, no numbers, no logo, no watermark, "
        "no claims on packaging, no brand name on the lid."
    )


def video_prompt(draft: Draft) -> str:
    """I2V from the finished still. Layout frozen. Product motion only. No legal bar from the model."""
    light = lighting_from_caption(draft.caption or "")
    return (
        "Five-second image-to-video from the finished campaign still as the first frame, "
        "vertical 3:4. Keep the layout frozen: the jar, empty margins, lighting, and any "
        "type or marks already in the still must not wander, warp, or be redrawn. "
        "Do not add new headlines, no logo, no watermarks including a Grok watermark, and no legal bar. "
        "Motion only: the white lid unscrews, aqua hyaluronic water gel bursts and ribbons "
        "toward the camera in slow appetizing motion, dew and light particles, slight camera push. "
        "No cuts, no people, no hands, no voiceover, no subtitles. "
        f"{light}."
    )
