"""Preview & Export — paused ZIP. Media ops owns go-live. No autonomous publish."""

from __future__ import annotations

import json
import os
import zipfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from boxes.art_director import compose
from boxes.audit import build_audit, render_audit_html
from boxes.video import compose_video
from boxes.visual import video_prompt, visual_prompt
from db import get_draft, upsert_draft
from models import Draft


def _export_dir() -> Path:
    override = os.environ.get("EXPORT_DIR")
    if override:
        return Path(override)
    sqlite = Path(os.environ.get("SQLITE_PATH") or "data/demo.db")
    return sqlite.resolve().parent / "exports"


def _ensure_image(draft: Draft) -> Draft:
    if draft.image_path and Path(draft.image_path).is_file():
        return draft
    updated = compose(draft, visual_prompt(draft))
    upsert_draft(updated)
    return updated


def _ensure_video(draft: Draft) -> Draft:
    if draft.video_path and Path(draft.video_path).is_file():
        return draft
    updated = compose_video(draft, video_prompt(draft))
    upsert_draft(updated)
    return updated


def _preview_html(draft: Draft, image_name: str, video_name: str | None) -> str:
    caption = escape(draft.caption or "")
    media = f'<img src="{escape(image_name)}" alt="paused preview"/>'
    if video_name:
        media = (
            f'<video src="{escape(video_name)}" controls muted playsinline '
            f'poster="{escape(image_name)}"></video>'
            f'<img src="{escape(image_name)}" alt="paused still"/>'
        )
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
    .phone img, .phone video {{ width:100%; display:block; }}
    .caption {{ padding:12px 16px; white-space:pre-wrap; font-size:14px; }}
    .stamp {{ text-align:center; color:#c9a227; font-size:12px;
              letter-spacing:.12em; padding:8px; }}
  </style>
</head>
<body>
  <div class="phone">
    <div class="stamp">PAUSED — NOT PUBLISHED</div>
    {media}
    <div class="caption">{caption}</div>
  </div>
</body>
</html>
"""


def export_pack(draft_id: str) -> Path:
    """Write a paused preview ZIP (HTML + PNG + MP4 + caption). Does not publish."""
    draft = get_draft(draft_id)
    if draft is None:
        raise ValueError("That draft is not in the queue.")
    draft = _ensure_image(draft)
    draft = _ensure_video(draft)
    out_dir = _export_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{draft.draft_id}_paused.zip"
    image_name = "card.png"
    video_name = "clip.mp4"
    meta = {
        "draft_id": draft.draft_id,
        "status": "paused",
        "published": False,
        "flag_human": bool(draft.flag_human),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "note": "Paused preview pack. No autonomous publish.",
        "has_video": bool(draft.video_path and Path(draft.video_path).is_file()),
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        audit = build_audit(draft.draft_id)
        # evidence chain: flatten audit sections into chained records, then
        # re-emit audit.json with digests + a manifest over every file
        chain_records = [
            {"section": key, "content": value}
            for key, value in sorted(audit.items())
        ]
        caption_bytes = ((draft.caption or "") + "\n").encode("utf-8")
        meta_bytes = json.dumps(meta, indent=2).encode("utf-8")
        has_video = bool(draft.video_path and Path(draft.video_path).is_file())
        preview_bytes = _preview_html(
            draft, image_name, video_name if has_video else None
        ).encode("utf-8")
        image_bytes = (
            Path(draft.image_path).read_bytes()
            if draft.image_path and Path(draft.image_path).is_file()
            else None
        )
        video_bytes = (
            Path(draft.video_path).read_bytes()
            if has_video
            else None
        )
        files: dict[str, bytes] = {
            "caption.txt": caption_bytes,
            "meta.json": meta_bytes,
            "preview.html": preview_bytes,
        }
        if image_bytes:
            files[image_name] = image_bytes
        if video_bytes:
            files[video_name] = video_bytes
        from boxes.evidence import build_manifest, hash_chain_records, sign_manifest

        chained = hash_chain_records(chain_records)
        audit_chained = {**audit, "records": chained}
        audit_bytes = json.dumps(audit_chained, indent=2, default=str).encode("utf-8")
        files["audit.json"] = audit_bytes
        manifest = sign_manifest(build_manifest(files, draft_id=draft.draft_id))
        zf.writestr("caption.txt", caption_bytes)
        zf.writestr("meta.json", meta_bytes)
        zf.writestr("preview.html", preview_bytes)
        zf.writestr("audit.json", audit_bytes)
        zf.writestr(
            "audit.html",
            render_audit_html(audit)
            + "<p class='meta'>Evidence chain head: "
            + (chained[-1]["digest"] if chained else "n/a")
            + "</p>",
        )
        if image_bytes:
            zf.write(str(draft.image_path), arcname=image_name)
        if video_bytes:
            zf.write(str(draft.video_path), arcname=video_name)
        zf.writestr(
            "MANIFEST.json",
            json.dumps(manifest, indent=2, default=str),
        )
    return dest
