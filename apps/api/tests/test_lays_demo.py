"""Unofficial Lay's Chile Limón client demo."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from models import Concept, Draft

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
LOGO_NAVY = (11, 61, 145)
ROOT = Path(__file__).resolve().parent.parent / "fixtures" / "lays"


def _draft(caption: str = "4pm. Chile Limón. Lime and chilli flavour.") -> Draft:
    return Draft(
        draft_id="dft_lays",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def test_lays_pack_is_unofficial_and_complete(lays_brand) -> None:
    from boxes.brand_pack import load_brand_pack

    pack = load_brand_pack()
    assert pack["slug"] == "lays"
    assert pack["name"] == "Lay's"
    assert pack["hero_sku"] == "DEMO-CHILE-LIMON"
    assert pack["logo_in_imagine"] is True
    assert pack["overlay_wordmark"] is False
    blob = " ".join(
        [
            pack["disclaimer"],
            pack["unofficial_line"],
            (ROOT / "brand.json").read_text(encoding="utf-8"),
            (ROOT / "claims.json").read_text(encoding="utf-8"),
        ]
    ).lower()
    assert "unofficial" in blob
    assert "pepsico" in blob
    assert "not pepsi" in blob or "not pepsico" in blob
    for name in (
        "brand.json",
        "claims.json",
        "disclaimer.txt",
        "exclusion.txt",
        "logo.svg",
        "products.json",
    ):
        assert (ROOT / name).is_file(), name
    assert (ROOT / "products" / "chile-limon.jpg").is_file()


def test_lays_catalog_has_five_flavours_and_chile_limon_photo(lays_brand) -> None:
    from boxes.products import hero_sku, list_products, pack_photo

    rows = list_products()
    assert len(rows) == 5
    names = {str(row["name"]) for row in rows}
    assert "Chile Limón" in names
    assert "India's Magic Masala" in names
    assert hero_sku() == "DEMO-CHILE-LIMON"
    photo = pack_photo("DEMO-CHILE-LIMON")
    assert photo is not None and photo.is_file()
    assert photo.stat().st_size > 10_000


def test_get_brand_and_products_are_lays_not_neutrogena(lays_brand) -> None:
    from main import app

    client = TestClient(app)
    brand = client.get("/brand").json()
    assert brand["slug"] == "lays"
    assert brand["name"] == "Lay's"
    assert "neutrogena" not in str(brand).lower()
    assert "skincare" not in str(brand).lower()
    assert brand["handle"] == "snacks"
    assert "pepsico" in brand["unofficial_line"].lower() or "pepsico" in brand["disclaimer"].lower()

    catalog = client.get("/brand/products").json()
    skus = [row["sku"] for row in catalog["products"]]
    assert catalog["hero_sku"] == "DEMO-CHILE-LIMON"
    assert "DEMO-CHILE-LIMON" in skus
    chile = next(row for row in catalog["products"] if row["sku"] == "DEMO-CHILE-LIMON")
    assert chile["has_image"] is True
    assert chile["image_url"] == "/brand/products/DEMO-CHILE-LIMON/image"

    image = client.get("/brand/products/DEMO-CHILE-LIMON/image")
    assert image.status_code == 200
    assert image.headers["content-type"].startswith("image/")
    assert len(image.content) > 10_000


def test_lays_factory_uses_chile_limon_sku(lays_brand) -> None:
    from boxes.fixture_dive import persist_unofficial_fixture, unofficial_fixture_pack
    from main import app

    pack = unofficial_fixture_pack()
    assert "chile limón" in pack["report"].what.lower() or "chile limon" in pack["report"].what.lower()
    assert "neutrogena" not in pack["report"].what.lower()
    persist_unofficial_fixture()

    client = TestClient(app)
    res = client.post(
        "/factory/run",
        json={"report_id": pack["report"].report_id, "sku": "DEMO-CHILE-LIMON"},
    )
    assert res.status_code == 200, res.text
    drafts = res.json()
    assert drafts
    blob = " ".join(row["caption"] for row in drafts).lower()
    assert "chile limón" in blob or "chile limon" in blob
    assert "neutrogena" not in blob
    assert "hydro boost" not in blob
    assert "unofficial" in blob or "pepsico" in blob

    brief = client.get(f"/briefs/{drafts[0]['brief_id']}").json()
    assert brief["sku"] == "DEMO-CHILE-LIMON"


def test_lays_copy_is_grok_written_not_fixture(lays_brand) -> None:
    from boxes.copywriter import CopyOut, run_copywriter
    from boxes.hard_rules import load_disclaimer, without_disclaimer

    disc = load_disclaimer()
    calls = {"n": 0}

    class Grok:
        def complete_json(self, system: str, user: str, schema: type) -> CopyOut:
            calls["n"] += 1
            blob = f"{system}\n{user}".lower()
            assert schema is CopyOut
            assert "<packet>" in user
            assert "chile" in blob or "limón" in blob or "limon" in blob
            return CopyOut(
                captions=[
                    "4pm AC. Chile Limón — lime hit, then the chilli. Ridged potato chips.",
                    "Train home. Tear Chile Limón. Lime and chilli flavour, then crunch.",
                    "Monsoon desk. One green pack. Chile Limón, lime heat after the chilli.",
                ]
            )

    concept = Concept(
        concept_id="con_lays_copy",
        brief_id="b1",
        angle="4pm desk crunch",
        persona="office 4pm snacker",
        claim_safe_pain="4pm desk slump",
        channel="instagram",
        indic_register="hinglish",
        idea="Chile Limón lime then chilli for India evenings.",
    )
    drafts = run_copywriter(concept, round=1, chat=Grok())
    assert calls["n"] == 1
    assert len(drafts) >= 2
    bodies = [without_disclaimer(row.caption, disc).strip().lower() for row in drafts]
    assert len(set(bodies)) >= 2
    blob = " ".join(row.caption for row in drafts).lower()
    assert "chile" in blob
    assert "ridged crunch, lime first, chilli after" not in blob
    assert "unofficial" in blob or "pepsico" in blob
    assert "neutrogena" not in blob
    assert "dermatologist" not in blob


def test_lays_visual_is_explosion_ad_not_pack_shot(lays_brand) -> None:
    from boxes.visual import visual_prompt

    prompt = visual_prompt(_draft())
    lower = prompt.lower()
    assert "4:5" in lower
    assert "chile limón" in lower or "chile limon" in lower
    assert "catalog jpeg" in lower or "not a catalog" in lower
    assert "logo" in lower and "allowed" in lower
    assert "no logo" not in lower
    assert "hydro boost" not in lower
    assert "white" not in lower or "lid" not in lower
    assert "explosion" in lower
    assert "open bag" in lower
    assert "tangy lime" in lower
    assert "spicy hit" in lower
    assert "brush" in lower
    assert "jalapeño" in lower or "jalapeno" in lower
    assert "not jalap" in lower.replace("é", "e")
    assert "shop now" not in lower
    assert "sponsored" not in lower
    assert "second" in lower and "wordmark" in lower
    assert "disclaimer" in lower and "code" in lower


def test_chile_limon_type_is_lime_and_chilli_not_generic(lays_brand) -> None:
    from boxes.campaign_still import CHILE_CTA, CHILE_HEADLINE, CHILE_SLOGAN, flavour_art

    art = flavour_art("DEMO-CHILE-LIMON")
    blob = " ".join((*art["headline"], str(art["slogan"]), str(art["cta"]))).lower()
    assert art["headline"] == CHILE_HEADLINE
    assert art["slogan"] == CHILE_SLOGAN
    assert art["cta"] == CHILE_CTA
    assert "lime" in blob and "spicy" in blob
    assert "delicious" not in blob
    assert "shop now" not in blob
    assert "sponsored" not in blob
    assert "lay's" not in blob
    assert "jalap" not in blob


def test_lays_compose_is_campaign_frame_not_meta_chrome(
    lays_brand, tmp_path: Path
) -> None:
    from boxes.art_director import compose

    result = compose(_draft(), "campaign chile limon still", out_path=tmp_path / "lays.png")
    path = Path(result.image_path)
    assert path.read_bytes()[:8] == PNG_MAGIC
    img = Image.open(path).convert("RGB")
    assert img.size == (1080, 1350)
    w, h = img.size
    # Neutrogena navy wordmark must not appear on a Lays still.
    navy = False
    for y in range(0, int(h * 0.22), 3):
        for x in range(0, w, 4):
            px = img.getpixel((x, y))
            if all(abs(px[i] - LOGO_NAVY[i]) <= 18 for i in range(3)):
                navy = True
                break
        if navy:
            break
    assert navy is False
    # Designed headline lives top-left (bright type, not a dark Sponsored chip).
    white_type = 0
    for y in range(40, 280, 2):
        for x in range(20, 560, 2):
            px = img.getpixel((x, y))
            if px[0] > 200 and px[1] > 200 and px[2] > 200:
                white_type += 1
    assert white_type > 400
    # Burst carries lime + chilli + chip gold, not a flat pack shot.
    gold = chilli = lime = 0
    for y in range(int(h * 0.12), int(h * 0.48), 3):
        for x in range(int(w * 0.12), int(w * 0.88), 3):
            r, g, b = img.getpixel((x, y))
            if r > 180 and 90 < g < 220 and b < 100:
                gold += 1
            if r > 150 and g < 90 and b < 90:
                chilli += 1
            if g > r + 15 and g > 110 and b < 130:
                lime += 1
    assert gold > 20
    assert chilli > 15
    assert lime > 15
    # Tiny unofficial legal remains (pale pixels), but the bottom is not a fat grey-black bar.
    pale = False
    slab = total = 0
    for y in range(int(h * 0.96), h, 1):
        for x in range(0, w, 4):
            px = img.getpixel((x, y))
            total += 1
            if max(px) < 34 and (max(px) - min(px)) < 12:
                slab += 1
            if px[0] > 180 and px[1] > 180 and px[2] > 180:
                pale = True
    assert pale is True
    assert total and (slab / total) < 0.35


def test_neutrogena_preview_payload_stays_neutrogena() -> None:
    from main import app

    client = TestClient(app)
    brand = client.get("/brand").json()
    assert brand["slug"] == "neutrogena"
    assert brand["name"] == "Neutrogena"
