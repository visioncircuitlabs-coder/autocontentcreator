"""SessionStart reminder. Stdout is ignored; stderr shows in the hook log."""
import sys
from pathlib import Path

msg = (
    "Content Machine product is D:\\PROJECTS\\autocontentcreator\\.worktrees\\feat-foolproof-design. "
    "Read docs/agents/WHERE-WE-ARE.md before product work. Do not scaffold on main."
)
print(msg, file=sys.stderr)
cwd = Path.cwd()
if cwd.name.lower() == "autocontentcreator" and ".worktrees" not in str(cwd).lower():
    print("This cwd is main (design map only). Open the feat worktree.", file=sys.stderr)
sys.exit(0)
