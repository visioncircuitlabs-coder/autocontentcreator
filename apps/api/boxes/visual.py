"""Instagram feed picture prompt. Brand pack decides logo-in-Imagine vs overlay."""

from __future__ import annotations

from boxes.brand_pack import load_brand_pack
from boxes.products import get_product, hero_sku, product_label
from models import Draft


def lighting_from_caption(caption: str) -> str:
    text = (caption or "").lower()
    if any(token in text for token in ("ac", "commute", "office", "4pm", "desk")):
        return "cool indoor India daylight, air-con clean, snack-desk energy"
    if any(token in text for token in ("night", "evening", "double cleanse")):
        return "warm evening light, still bright like a campaign ad"
    if any(token in text for token in ("monsoon", "humid", "rain")):
        return "bright monsoon daylight, wet stone, no dark rooms"
    return "bright commercial studio daylight"


def _sku_for(draft: Draft) -> str:
    try:
        from boxes.brief import load_brief

        brief = load_brief(draft.brief_id)
        if brief.sku:
            return brief.sku
    except Exception:
        pass
    return hero_sku()


def _neutrogena_prompt(draft: Draft) -> str:
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


def _lays_prompt(draft: Draft, sku: str) -> str:
    product = get_product(sku) or {}
    name = product_label(sku)
    flavour = str(product.get("flavour") or name)
    ridged = "ridged" in str(product.get("chip_cut") or "").lower() or "chile" in name.lower()
    light = lighting_from_caption(draft.caption or "")
    chip_line = (
        "golden ridged / crinkle-cut potato chips catching hard highlights"
        if ridged
        else "golden potato chips catching hard highlights"
    )
    pack_truth = (
        f"Hero pack: unofficial India-market Lay's {flavour} bag as product truth. "
        "Deep emerald green film, darker green concentric circles, classic Lay's "
        "red ribbon wordmark on a yellow sun, white flavour name Chile Limón, "
        "floating ridged chips, lime wedge, long red chilli, garlic clove, "
        "Indian green veg mark. Photograph the real bag, not a redesigned pack."
        if "chile" in name.lower() or "limón" in name.lower() or "limon" in name.lower()
        else (
            f"Hero pack: unofficial India-market Lay's {flavour} bag as product truth. "
            "Photograph a real Lay's India pack for that flavour, not a redesigned bag."
        )
    )
    return (
        "Campaign-grade Instagram 4:5 vertical still, premium India FMCG snack advertisement, "
        "OOH/print energy, photoreal, not a catalog JPEG, not a screenshot, not a 3D render, "
        "not generic AI slop, not a pack on a white sweep. "
        f"{pack_truth} "
        f"The Lay's logo on the pack is allowed and should match the real bag. "
        "Do not invent a second giant floating LAY'S wordmark beside the pack. "
        "Do not add legal lines, nutrition tables, hashtags, or extra English slogans. "
        f"Scene: {name} stands in a shallow pool of lime juice and chilli oil on dark wet stone. "
        f"{chip_line}, lime mist, chilli flakes in the air, one lime wedge, one long red chilli. "
        f"{light}. Juicy highlights, cinematic rim light, emerald and lime palette. "
        "No people, no hands, no extra brands."
    )


def visual_prompt(draft: Draft) -> str:
    pack = load_brand_pack()
    sku = _sku_for(draft)
    if pack.get("slug") == "lays":
        return _lays_prompt(draft, sku)
    return _neutrogena_prompt(draft)
