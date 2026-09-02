"""Instagram feed picture prompt.

Neutrogena stills: unlocked zone; navy wordmark + disclaimer stay in Pillow.
Chile Limón: the provided pack photo is the bag (logo already on it). Type lives
in the art. Do not Pillow-stamp a second LAY'S wordmark or unofficial bar.
"""

from __future__ import annotations

from models import Draft

# Real Hydro Boost / drugstore water-gel ads: 4:5 feed, bright, dewy, white lid,
# aqua gel, centered jar, empty margins. Not a night-rain still life.

CHILE_LIMON_TYPE = (
    "TANGY LIME. SPICY HIT.",
    "CRUNCH THE HEAT.",
    "DARE A BITE?",
)


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
    """World-class campaign still: product hero, burst composition, designed type."""
    light = lighting_from_caption(draft.caption or "")
    if is_chile_limon_pack(draft):
        type_line = " / ".join(CHILE_LIMON_TYPE)
        return (
            "World-class finished 4:5 vertical print and Instagram campaign poster, Super Bowl craft. "
            "Image-edit FROM this exact product photograph of the green Lay's Chile Limón India pack. "
            "Keep this bag identity: do not redraw, restyle, or replace the pack. "
            "Keep the printed Lay's ribbon logo, 25% MORE, Chile Limón Flavour, veg mark, "
            "lime, red chilli, garlic, and rippled chips that are already on the photo. "
            "The pack is the hero. Open-bag energy: flavour exploding out of the OPEN bag — "
            "lime zest, red chilli (not jalapeño), garlic, golden rippled chips — bursting "
            "around the real pack on a lime-green field. "
            f"{light}. "
            "Designed campaign type in the empty margins as graphic headlines, "
            f"bold condensed sans-serif, locked in the art (not a legal bar): {type_line} "
            "The logo on this pack may stay because it is printed on the real pack. "
            "Do not add a second LAY'S wordmark. No unofficial disclaimer, no legal bar, "
            "no Grok watermark, no people, no hands, no Magic Masala, no jalapeño."
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
    if is_chile_limon_pack(draft):
        type_line = " / ".join(CHILE_LIMON_TYPE)
        freeze = (
            "Five-second image-to-video of the finished campaign poster as the first frame, "
            "vertical 3:4, 720p. Keep layout and type frozen: the real Chile Limón pack, "
            f"headlines ({type_line}), and margins must not wander, warp, or be redrawn. "
            "Motion is only the open-pack burst plus slight camera and particles. "
            "Do not add a second LAY'S wordmark, no new headlines, no unofficial disclaimer, "
            "no legal bar, no Grok watermark. "
        )
        motion = (
            "Animate the pack opening: the bag flexes, the top opens or tears, chips and "
            "lime-chilli garnish burst toward the camera in slow appetizing motion. "
            "Not a static bag-on-table loop. Not jalapeño. "
            "No cuts, no people, no hands, no voiceover, no subtitles. "
        )
        return freeze + motion + f"{light}."
    freeze = (
        "Five-second image-to-video of the finished campaign poster as the first frame, "
        "vertical 3:4, 720p. Keep layout and type frozen: headlines, the pack, margins, "
        "and any marks already in the still must not wander, warp, or be redrawn. "
        "Motion is only the burst plus slight camera and particles. "
        "Do not add new headlines, no logo, no watermarks including a Grok watermark, "
        "and no legal bar. "
    )
    motion = (
        "Animate the pack opening: this pack is the jar — the white lid unscrews, "
        "aqua hyaluronic water gel and dew burst toward the camera, light particles, "
        "slight camera push. Not a static product-on-table loop. No extra wordmark. "
        "No cuts, no people, no hands, no voiceover, no subtitles. "
    )
    return freeze + motion + f"{light}."
