"""Preview & Export — paused ZIP. Media ops owns go-live. No autonomous publish."""

from __future__ import annotations

import json
import os
import zipfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from boxes.art_director import compose
from db import get_draft, upsert_draft
from models import Draft


def _export_dir() -> Path:
    override = os.environ.get("EXPORT_DIR")
    if override:
        return Path(override)
    sqlite = Path(os.environ.get("SQLITE_PATH") or "data/demo.db")
    return sqlite.resolve().parent / "exports"


def visual_prompt(draft: Draft) -> str:
    line = (draft.caption or "").split("\n")[0].strip()[:120]
    return f"Skincare still life, no text, no logo, no claims. Mood: {line}"


def _ensure_image(draft: Draft) -> Draft:
    if draft.image_path and Path(draft.image_path).is_file():
        return draft
    updated = compose(draft, visual_prompt(draft))
    upsert_draft(updated)
    return updated


def _preview_html(draft: Draft, image_name: str) -> str:
    caption = escape(draft.caption or "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Paused preview {escape(draft.draft_id)}</title>
  <style>
    body {{ background:#111; color:#eee; font-family:sans-serif;
            display:flex; justify-content:center; padding:24px; margin:0; }}
    .phone {{ width:390px; background:#000; border-radius:24px; overflow:hidden;
              border:1px solid #333; }}
    .phone img {{ width:100%; display:block; }}
    .caption {{ padding:12px 16px; white-space:pre-wrap; font-size:14px; }}
    .stamp {{ text-align:center; color:#c9a227; font-size:12px;
              letter-spacing:.12em; padding:8px; }}
  </style>
</head>
<body>
  <div class="phone">
    <div class="stamp">PAUSED — NOT PUBLISHED</div>
    <img src="{escape(image_name)}" alt="paused preview"/>
    <div class="caption">{caption}</div>
  </div>
</body>
</html>
"""


def export_pack(draft_id: str) -> Path:
    """Write a paused preview ZIP (HTML + PNG + caption). Does not publish."""
    draft = get_draft(draft_id)
    if draft is None:
        raise ValueError("That draft is not in the queue.")
    draft = _ensure_image(draft)
    out_dir = _export_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{draft.draft_id}_paused.zip"
    image_name = "card.png"
    meta = {
        "draft_id": draft.draft_id,
        "status": "paused",
        "published": False,
        "flag_human": bool(draft.flag_human),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "note": "Paused preview pack. No autonomous publish.",
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("caption.txt", (draft.caption or "") + "\n")
        zf.writestr("meta.json", json.dumps(meta, indent=2))
        zf.writestr("preview.html", _preview_html(draft, image_name))
        if draft.image_path and Path(draft.image_path).is_file():
            zf.write(str(draft.image_path), arcname=image_name)
    return dest
