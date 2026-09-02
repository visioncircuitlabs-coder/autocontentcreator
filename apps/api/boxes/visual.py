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
    chile = "chile" in name.lower() or "limón" in name.lower() or "limon" in name.lower()
    ridged = "ridged" in str(product.get("chip_cut") or "").lower() or chile
    light = lighting_from_caption(draft.caption or "")
    chips = (
        "golden ridged / crinkle-cut potato chips catching hard highlights"
        if ridged
        else "golden potato chips catching hard highlights"
    )
    pack_truth = (
        "Hero pack: unofficial India-market Lay's Chile Limón bag as product truth — "
        "deep emerald green film, darker green concentric circles, classic Lay's "
        "red ribbon wordmark on a yellow sun already on the bag, white flavour name "
        "Chile Limón, Indian green veg mark. Photograph the real India bag, not a "
        "redesigned pack, not Jalapeño Lime (US), not green jalapeño slices."
        if chile
        else (
            f"Hero pack: unofficial India-market Lay's {flavour} bag as product truth. "
            "Photograph a real Lay's India pack for that flavour, not a redesigned bag."
        )
    )
    burst = (
        "Open bag in the lower third, mouth facing up. A flavour explosion bursts "
        "OUT of the bag toward the top of the frame: "
        f"{chips}, lime wedges and lime juice spray (citrus, NOT jalapeño), "
        "long red chillies, chilli flakes, one garlic clove, crumbs and particles "
        "frozen in mid-air, motion streaks. Hard studio lighting, 3D bag crinkle "
        "with specular highlights, real contact shadow, bright radial glow behind "
        "the burst on a deep forest-green field."
        if chile
        else (
            f"Open bag in the lower third. Flavour explosion of {chips} and {flavour} "
            "cues bursting upward, juice spray, particles, radial studio glow, "
            "3D bag crinkle, real shadows."
        )
    )
    type_block = (
        "TYPE IS DESIGN, painted into the composition like a print snack ad, "
        "not UI, not a caption, not Instagram chrome: top-left large slanted "
        "distressed white headline stacked on two lines TANGY LIME. / SPICY HIT. "
        "grunge brush texture, slight tilt. Lower-right smaller slogan CRUNCH THE HEAT. "
        "Lower-right irregular lime-green brush-stroke banner (painted organic shape, "
        "not a rounded pill, not a button) reading DARE A BITE?. "
        "Do not draw Instagram feed labels, rounded-rect tags, stickers, "
        "hashtags, nutrition tables, checkout pills, or Meta chrome."
        if chile
        else (
            f"TYPE IS DESIGN: slanted distressed headline for {flavour}, stacked slogan, "
            "irregular brush-stroke CTA banner. Not rounded pills, not Instagram "
            "feed labels, not a checkout button."
        )
    )
    return (
        "Campaign-grade 4:5 vertical still, premium India FMCG snack advertisement, "
        "OOH/print energy, photoreal, not a catalog JPEG, not a screenshot, "
        "not a pack on a white sweep, not generic AI slop. "
        f"{pack_truth} "
        "The Lay's logo on the pack is allowed because it is on the real bag. "
        "Do not invent a second giant floating LAY'S wordmark beside the pack. "
        "Do not paint legal lines or disclaimers — those are added in code after. "
        f"{burst} {type_block} {light} "
        "No people, no hands, no extra brands."
    )


def visual_prompt(draft: Draft) -> str:
    pack = load_brand_pack()
    sku = _sku_for(draft)
    if pack.get("slug") == "lays":
        return _lays_prompt(draft, sku)
    return _neutrogena_prompt(draft)
