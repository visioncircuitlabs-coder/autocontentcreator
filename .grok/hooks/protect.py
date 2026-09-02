"""PreToolUse gate for Content Machine. Deny secret edits, C: caches, and scaffolding on main."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(r"D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design")
MAIN = Path(r"D:\PROJECTS\autocontentcreator")
C_DRIVE_PREFIXES = (
    r"c:\users\lenovo\appdata",
    r"c:\users\lenovo\.npm",
    r"c:\users\lenovo\.cache",
    r"c:\users\lenovo\pip",
)


def out(decision: str, reason: str = "") -> None:
    payload = {"decision": decision}
    if reason:
        payload["reason"] = reason
    sys.stdout.write(json.dumps(payload))
    sys.exit(0)


def flatten(value, acc: list[str]) -> None:
    if isinstance(value, str):
        acc.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            flatten(v, acc)
    elif isinstance(value, list):
        for v in value:
            flatten(v, acc)


def norm(p: str) -> str:
    return p.replace("/", "\\").lower()


def is_main_checkout(cwd: str, root: str) -> bool:
    for raw in (cwd, root):
        if not raw:
            continue
        try:
            p = Path(raw).resolve()
        except OSError:
            continue
        if ".worktrees" in str(p).lower():
            return False
        if p == MAIN.resolve():
            return True
    return False


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        out("allow")
        return

    tool = str(event.get("toolName") or "")
    inp = event.get("toolInput") or {}
    cwd = str(event.get("cwd") or "")
    root = str(event.get("workspaceRoot") or "")
    blobs: list[str] = []
    flatten(inp, blobs)
    text = "\n".join(blobs)
    low = norm(text)

    if ".env" in low and ".env.example" not in low:
        if any(x in low for x in ("write", "edit", "search_replace", "git add", "git commit")) or tool.lower() in {
            "write",
            "edit",
            "search_replace",
            "strreplace",
        }:
            out("deny", "Do not edit or commit .env. Change .env.example only.")

    if low.endswith(".pptx") or "\\*.pptx" in low:
        if tool.lower() in {"write", "edit", "search_replace"} or "git add" in low:
            out("deny", "Do not commit or write .pptx files. They are local references.")

    for prefix in C_DRIVE_PREFIXES:
        if prefix in low:
            out("deny", "Keep caches on D:. Do not write npm/pip/agent caches on C: (disk is full).")

    if is_main_checkout(cwd, root):
        scaffolding = (
            "apps\\api" in low
            or "apps/api" in text.lower()
            or "create-next-app" in low
            or "docker-compose.yml" in low
        )
        in_worktree = ".worktrees\\feat-foolproof-design" in low or ".worktrees/feat-foolproof-design" in text.lower()
        if scaffolding and not in_worktree:
            out(
                "deny",
                "Product already lives in D:\\PROJECTS\\autocontentcreator\\.worktrees\\feat-foolproof-design. "
                "Do not scaffold a second app on main. Read docs/agents/WHERE-WE-ARE.md in the worktree.",
            )

    out("allow")


if __name__ == "__main__":
    main()
