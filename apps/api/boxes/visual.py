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
    """Unlocked ~5s product clip. Same hero as the still. No brand marks in the model."""
    light = lighting_from_caption(draft.caption or "")
    return (
        "Five-second Instagram beauty product video, vertical 3:4 then cropped to 4:5, "
        "commercial water-gel moisturizer ad. "
        "Hero object: one closed clear jar of aqua-blue hyaluronic water gel moisturizer "
        "with a white screw lid, gel visible through the glass, fine dew on the jar. "
        "Jar stays centered on pale wet marble for the whole clip. "
        "Slow camera push-in, a catch-light slides across the gel, no cuts, no people. "
        f"{light}. Sharp, clean, dewy, premium drugstore skincare. "
        "No people, no hands, no text, no letters, no numbers, no logo, no watermark, "
        "no claims on packaging, no brand name on the lid, no legal disclaimer, "
        "no on-screen caption, no subtitle, no voiceover."
    )
