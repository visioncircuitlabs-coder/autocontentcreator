"""Regulator-ready audit trail: signals → scores → brief → concepts → drafts
→ judge rounds → decision. JSON plus a clean printable HTML rendering.
"""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_audit(draft_id: str) -> dict:
    """Full provenance for one draft, as a plain dict (JSON-ready).

    Raises ValueError("That draft is not in the queue.") when unknown.
    """
    from db import (
        get_brief,
        get_draft,
        get_report,
        list_concepts,
        list_decisions,
        list_drafts,
        list_events,
        list_scores,
        list_signals,
    )
    from boxes.visual import visual_prompt

    draft = get_draft(draft_id)
    if draft is None:
        raise ValueError("That draft is not in the queue.")

    brief = get_brief(draft.brief_id)
    report = get_report(brief.report_id) if brief else None
    score = None
    signal = None
    if report is not None:
        for item in list_scores():
            if item.signal_id == report.signal_id:
                score = item
                break
        for item in list_signals():
            if item.signal_id == report.signal_id:
                signal = item
                break

    # Every caption variant for this brief, including rejected ones,
    # each carrying its judge verdict/reasons per loop round.
    siblings = [d for d in list_drafts() if d.brief_id == draft.brief_id]
    variants = [
        {
            "draft_id": d.draft_id,
            "variant": d.variant,
            "round": d.round,
            "caption": d.caption,
            "rules": list(d.rules or []),
            "judge": d.judge,
            "flag_human": bool(d.flag_human),
            "image_path": d.image_path,
            "chosen": d.draft_id == draft.draft_id,
        }
        for d in sorted(siblings, key=lambda x: (x.variant, x.round, x.draft_id))
    ]

    concepts = [
        c.model_dump(mode="json") for c in list_concepts(draft.brief_id)
    ]

    decisions = [
        {
            "user": dec.user,
            "verdict": dec.verdict,
            "reason": dec.reason,
            "decided_at": dec.decided_at.isoformat(),
        }
        for dec in list_decisions()
        if dec.draft_id == draft.draft_id
    ]

    # Event log entries tied to this draft (or its brief/report chain).
    trace_ids = {draft.draft_id}
    if brief is not None:
        trace_ids.add(brief.brief_id)
    if report is not None:
        trace_ids.add(report.report_id)
    if signal is not None:
        trace_ids.add(signal.signal_id)

    def _touches(payload: object) -> bool:
        text = json.dumps(payload, default=str)
        return any(tid in text for tid in trace_ids)

    events = [
        {"id": e["id"], "ts": e["ts"], "kind": e["kind"], "payload": e["payload"]}
        for e in reversed(list_events(500))
        if _touches(e["payload"])
    ]

    image_mode = (os.environ.get("IMAGE_GEN_MODE") or "stub").strip().lower() or "stub"
    image_provenance = {
        "prompt_used": visual_prompt(draft),
        "adapter": image_mode,
        "image_path": draft.image_path,
        "brand_locks_applied_in_code": True,
        "note": "No brand marks or claims are sent to the image model.",
    }

    return {
        "generated_at": _iso_now(),
        "draft": {
            "draft_id": draft.draft_id,
            "brief_id": draft.brief_id,
            "caption": draft.caption,
            "variant": draft.variant,
            "round": draft.round,
            "rules": list(draft.rules or []),
            "judge": draft.judge,
            "flag_human": bool(draft.flag_human),
            "image_path": draft.image_path,
        },
        "signal": signal.model_dump(mode="json") if signal else None,
        "score": score.model_dump(mode="json") if score else None,
        "report": report.model_dump(mode="json") if report else None,
        "brief": brief.model_dump(mode="json") if brief else None,
        "concepts": concepts,
        "variants": variants,
        "decisions": decisions,
        "events": events,
        "image_provenance": image_provenance,
    }


_CSS = """
body { font-family: Georgia, 'Times New Roman', serif; color:#1a1a1a;
       max-width: 820px; margin: 0 auto; padding: 32px 24px; line-height: 1.5; }
h1 { font-size: 22px; border-bottom: 2px solid #1a1a1a; padding-bottom: 6px; }
h2 { font-size: 16px; margin-top: 28px; background:#f0f0f0; padding: 6px 10px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 13px; }
th, td { border: 1px solid #bbb; padding: 5px 8px; text-align: left;
         vertical-align: top; }
th { background: #fafafa; }
pre { background:#f7f7f7; border:1px solid #ddd; padding:8px;
      white-space: pre-wrap; word-break: break-word; font-size:12px; }
.stamp { color:#8a1f11; font-weight:bold; letter-spacing:.08em; }
.pass { color:#14591d; font-weight:bold; }
.fail { color:#8a1f11; font-weight:bold; }
.meta { color:#555; font-size:12px; }
ul { margin: 4px 0; }
@media print { h2 { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
"""


def _esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def _kv_table(rows: list[tuple[str, object]]) -> str:
    out = ["<table><tbody>"]
    for key, value in rows:
        shown = value if value not in (None, "") else "—"
        if isinstance(shown, (dict, list)):
            body = "<pre>%s</pre>" % _esc(json.dumps(shown, indent=2, default=str))
        else:
            body = _esc(shown)
        out.append("<tr><th style='width:180px'>%s</th><td>%s</td></tr>" % (_esc(key), body))
    out.append("</tbody></table>")
    return "".join(out)


def render_audit_html(audit: dict) -> str:
    """Clean printable HTML. No JavaScript, inline CSS only."""
    draft = audit.get("draft", {})
    parts: list[str] = []
    parts.append(
        "<h1>Audit trail — draft %s <span class='stamp'>[PAUSED]</span></h1>" % _esc(draft.get("draft_id"))
    )
    parts.append(
        "<p class='meta'>Generated %s · Unofficial demo build — not medical advice.</p>"
        % _esc(audit.get("generated_at"))
    )

    parts.append("<h2>1. Signal (what we saw)</h2>")
    sig = audit.get("signal")
    if sig:
        parts.append(_kv_table([
            ("Title", sig.get("title")),
            ("Source", sig.get("source")),
            ("URL", sig.get("url")),
            ("Seen at", sig.get("seen_at")),
            ("Market / lang", "%s / %s" % (sig.get("market"), sig.get("lang"))),
            ("Query", sig.get("query_id")),
            ("Snippet", sig.get("snippet")),
        ]))
    else:
        parts.append("<p>No signal row found.</p>")

    parts.append("<h2>2. Score &amp; gate (no ads written here)</h2>")
    sc = audit.get("score")
    if sc:
        gate = _esc(sc.get("gate"))
        cls = "pass" if sc.get("gate") == "deep_dive" else ""
        parts.append(_kv_table([
            ("Brand fit", sc.get("brand_fit")),
            ("Velocity", sc.get("velocity")),
            ("Safety", sc.get("safety")),
            ("Gate", "<span class='%s'>%s</span>" % (cls, gate)),
            ("Reason", sc.get("reason")),
            ("Model / prompt v", "%s / %s" % (sc.get("model"), sc.get("prompt_version"))),
        ]))
    else:
        parts.append("<p>No score row found.</p>")

    parts.append("<h2>3. Deep-dive report &amp; strategist angles</h2>")
    rep = audit.get("report")
    if rep:
        angles = "<ul>%s</ul>" % "".join("<li>%s</li>" % _esc(a) for a in rep.get("angles", []))
        skeptic = rep.get("skeptic")
        parts.append(_kv_table([
            ("What", rep.get("what")),
            ("Why now", rep.get("why_now")),
            ("Who", rep.get("who")),
            ("Angles", angles),
            ("Risks", "<ul>%s</ul>" % "".join("<li>%s</li>" % _esc(r) for r in rep.get("risks", []))),
            ("Skeptic", skeptic),
            ("Sources", "<pre>%s</pre>" % _esc(json.dumps(rep.get("sources", []), indent=2, default=str))),
            ("Capped at", rep.get("capped_at")),
        ]))
    else:
        parts.append("<p>No report row found.</p>")

    parts.append("<h2>4. Brief</h2>")
    br = audit.get("brief")
    if br:
        parts.append(_kv_table([
            ("Brief id", br.get("brief_id")),
            ("SKU / market", "%s / %s" % (br.get("sku"), br.get("market"))),
            ("Channel / format", "%s / %s" % (br.get("channel"), br.get("format"))),
            ("Claims used", "<pre>%s</pre>" % _esc(json.dumps(br.get("claims", []), indent=2, default=str))),
        ]))
    else:
        parts.append("<p>No brief row found.</p>")

    parts.append("<h2>5. Concepts (strategist grid)</h2>")
    concepts = audit.get("concepts") or []
    if concepts:
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (_esc(c.get("concept_id")), _esc(c.get("angle")), _esc(c.get("persona")),
               _esc(c.get("claim_safe_pain")), _esc(c.get("hook")))
            for c in concepts
        )
        parts.append(
            "<table><thead><tr><th>Concept</th><th>Angle</th><th>Persona</th>"
            "<th>Claim-safe pain</th><th>Hook</th></tr></thead><tbody>%s</tbody></table>"
            % rows
        )
    else:
        parts.append("<p>No concept rows found.</p>")

    parts.append("<h2>6. Caption variants &amp; judge rounds (incl. rejected)</h2>")
    variants = audit.get("variants") or []
    for v in variants:
        judge = v.get("judge") or {}
        verdict = judge.get("verdict", "?")
        cls = "pass" if verdict == "PASS" else "fail"
        chosen = " <strong>[CHOSEN]</strong>" if v.get("chosen") else ""
        head = (
            "<div><p><strong>Variant %s · round %s%s</strong> — "
            "<span class='%s'>Judge: %s</span>, craft: %s%s</p>"
            % (
                _esc(v.get("variant")), _esc(v.get("round")), chosen,
                cls, _esc(verdict), _esc(judge.get("craft", "—")),
                " <span class='stamp'>FLAG HUMAN</span>" if v.get("flag_human") else "",
            )
        )
        reasons = list(judge.get("reasons") or []) + list(judge.get("craft_reasons") or [])
        rules = list(v.get("rules") or [])
        body = "<blockquote>%s</blockquote>" % _esc(v.get("caption"))
        extra = ""
        if rules:
            extra += "<p class='meta'>Hard-rule fails: %s</p>" % _esc("; ".join(rules))
        if reasons:
            extra += "<p class='meta'>Judge/craft reasons: %s</p>" % _esc("; ".join(reasons))
        parts.append(head + body + extra + "</div>")
    if not variants:
        parts.append("<p>No variant rows found.</p>")

    parts.append("<h2>7. Image provenance</h2>")
    ip = audit.get("image_provenance") or {}
    parts.append(_kv_table([
        ("Prompt used", ip.get("prompt_used")),
        ("Adapter", ip.get("adapter")),
        ("Image path", ip.get("image_path")),
        ("Brand locks applied in code", ip.get("brand_locks_applied_in_code")),
        ("Note", ip.get("note")),
    ]))

    parts.append("<h2>8. Decision (who / when / why)</h2>")
    decisions = audit.get("decisions") or []
    if decisions:
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (_esc(d.get("verdict")), _esc(d.get("user")), _esc(d.get("decided_at")), _esc(d.get("reason")))
            for d in decisions
        )
        parts.append(
            "<table><thead><tr><th>Verdict</th><th>User</th><th>At</th><th>Reason</th>"
            "</tr></thead><tbody>%s</tbody></table>" % rows
        )
    else:
        parts.append("<p class='stamp'>Not decided yet — pack is paused.</p>")

    parts.append("<h2>9. Event log for this draft</h2>")
    events = audit.get("events") or []
    if events:
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td><code>%s</code></td></tr>"
            % (_esc(e["ts"]), _esc(e["id"]), _esc(e["kind"]),
               _esc(json.dumps(e["payload"], default=str)))
            for e in events
        )
        parts.append(
            "<table><thead><tr><th>When</th><th>Event</th><th>Kind</th><th>Payload</th>"
            "</tr></thead><tbody>%s</tbody></table>" % rows
        )
    else:
        parts.append("<p>No matching event entries.</p>")

    body = "\n".join(parts)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\"/>\n"
        "<title>Audit trail %s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n"
        "</body>\n</html>\n" % (_esc(draft.get("draft_id")), _CSS, body)
    )
