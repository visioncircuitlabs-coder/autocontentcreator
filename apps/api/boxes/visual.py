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
    if any(token in text for token in ("chile", "limón", "limon", "chilli", "chili")):
        return "hard center light on a lime-green field, snack-ad daylight"
    return "bright commercial beauty-studio daylight"


def _pack_blob(draft: Draft) -> str:
    bits = [draft.caption or ""]
    try:
        from db import get_brief

        brief = get_brief(draft.brief_id) if draft.brief_id else None
        if brief is not None:
            bits.append(brief.sku or "")
    except Exception:
        pass
    return " ".join(bits).lower().replace("ó", "o")


def is_chile_limon_pack(draft: Draft) -> bool:
    """Chile Limón snack energy. Not Jalapeño Lime. Not a reason to take the Lays PR."""
    blob = _pack_blob(draft)
    return any(token in blob for token in ("lays", "chile", "limon", "chip", "crisp"))


def visual_prompt(draft: Draft) -> str:
    """World-class campaign still: product hero, burst composition, designed type.

    Brand wordmark and the legal bar stay out of the model — overlay paints those.
    """
    light = lighting_from_caption(draft.caption or "")
    if is_chile_limon_pack(draft):
        return (
            "World-class finished 4:5 vertical print and Instagram campaign poster, Super Bowl craft. "
            "Hero: one unofficial chile-limon potato-chip bag, lime plus dried chilli, "
            "centered pack hero, burst composition, center-lit explosion of lime zest, "
            "chilli flakes, and chips on a lime-green field. "
            f"{light}. "
            "Designed campaign type locked in the empty margins as graphic headlines, "
            "bold condensed sans-serif: short punchy lines about tangy lime and chilli heat. "
            "Do not write a brand name, no extra wordmark, no logo, no Grok watermark, "
            "no legal disclaimer bar, no people, no hands, no packaging claims."
        )
    return (
        "World-class finished 4:5 vertical print and Instagram campaign poster, Super Bowl craft. "
        "Hero: one closed clear jar of aqua-blue hyaluronic water gel moisturizer "
        "with a white screw lid, gel visible through the glass, fine dew on the jar. "
        "Jar sits centered on pale wet marble. Burst composition: frozen water-gel splash "
        "and droplets around the jar, large empty margins for locked type. "
        f"{light}. Sharp, clean, dewy, premium drugstore skincare. "
        "Fresh and bright like a water-gel moisturizer ad. "
        "Designed campaign type locked in the empty margins as graphic headlines, "
        "bold condensed sans-serif: two or three short punchy lines about cool water "
        "and after-commute skin. "
        "Do not write a brand name, no logo, no Grok watermark, no legal disclaimer bar, "
        "no medical claims, no cures, no heals, no people, no hands, no packaging text."
    )


def video_prompt(draft: Draft) -> str:
    """I2V from the finished still. Layout and type frozen. Product burst only."""
    light = lighting_from_caption(draft.caption or "")
    freeze = (
        "Five-second image-to-video of the finished campaign poster as the first frame, "
        "vertical 3:4, 720p. Keep layout and type frozen: headlines, the pack, margins, "
        "and any marks already in the still must not wander, warp, or be redrawn. "
        "Motion is only the burst plus slight camera and particles. "
        "Do not add new headlines, no logo, no watermarks including a Grok watermark, "
        "and no legal bar. "
    )
    if is_chile_limon_pack(draft):
        motion = (
            "Animate the pack opening: the bag flexes, the top opens or tears, chips and "
            "lime-chilli garnish burst toward the camera in slow appetizing motion. "
            "Not a static bag-on-table loop. No extra wordmark. "
            "No cuts, no people, no hands, no voiceover, no subtitles. "
        )
    else:
        motion = (
            "Animate the pack opening: this pack is the jar — the white lid unscrews, "
            "aqua hyaluronic water gel and dew burst toward the camera, light particles, "
            "slight camera push. Not a static product-on-table loop. No extra wordmark. "
            "No cuts, no people, no hands, no voiceover, no subtitles. "
        )
    return freeze + motion + f"{light}."
