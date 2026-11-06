"""Product catalog for the loaded brand pack. SKU picker + pack photos."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from boxes.brand_pack import load_brand_pack


def list_products(slug: str | None = None) -> list[dict[str, Any]]:
    pack = load_brand_pack(slug)
    return list(pack.get("products") or [])


def get_product(sku: str | None, slug: str | None = None) -> dict[str, Any] | None:
    needle = (sku or "").strip()
    if not needle:
        return None
    for row in list_products(slug):
        if str(row.get("sku") or "") == needle:
            return row
    return None


def hero_sku(slug: str | None = None) -> str:
    pack = load_brand_pack(slug)
    hero = str(pack.get("hero_sku") or "").strip()
    if hero:
        return hero
    rows = list_products(slug)
    for row in rows:
        if row.get("hero"):
            return str(row["sku"])
    if rows:
        return str(rows[0]["sku"])
    return ""


def product_label(sku: str | None, slug: str | None = None) -> str:
    row = get_product(sku, slug)
    if row:
        return str(row.get("name") or sku or "")
    token = (sku or "").upper()
    if "CHILE" in token or "LIMON" in token:
        return "Chile Limón"
    if "HYDRO" in token:
        return "Hydro Boost"
    return (sku or "this pack").strip() or "this pack"


def pack_photo(sku: str | None, slug: str | None = None) -> Path | None:
    row = get_product(sku, slug)
    if not row:
        return None
    path = row.get("image_path")
    if isinstance(path, Path) and path.is_file():
        return path
    return None


def public_product(row: dict[str, Any]) -> dict[str, Any]:
    sku = str(row.get("sku") or "")
    has_image = isinstance(row.get("image_path"), Path) and row["image_path"].is_file()
    return {
        "sku": sku,
        "name": str(row.get("name") or sku),
        "flavour": str(row.get("flavour") or row.get("name") or sku),
        "chip_cut": str(row.get("chip_cut") or ""),
        "pack_color": str(row.get("pack_color") or ""),
        "hero": bool(row.get("hero")),
        "notes": str(row.get("notes") or ""),
        "has_image": has_image,
        "image_url": f"/brand/products/{sku}/image" if has_image else None,
    }
