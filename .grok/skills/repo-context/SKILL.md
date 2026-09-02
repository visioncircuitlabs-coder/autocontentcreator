---
name: repo-context
description: Load this project's architecture, conventions, runbooks, and decisions before changing code. Stops inventing a third way. Triggers: new screen, new endpoint, UI change, "how we do this", agent context, /repo-context.
---

# Repo context

Do not build a wiki. Read the files that already exist.

| Kind | File | Use it for |
|---|---|---|
| Agent start | `AGENTS.md` then `docs/agents/WHERE-WE-ARE.md` | Current stage. Do not re-scaffold. |
| Hard locks | `docs/agents/invariants.md` | Fail the PR from this file |
| Live system | `docs/agents/system.md` | Belt, data, ports |
| Box → file | `docs/agents/boxes.md` | Spec vs code. Code wins. |
| Memory | `docs/agents/memory.md` | SQLite + markdown dual store |
| Walk | `docs/agents/ui.md` | Five beats. Picture after caption pick. |
| Traps | `docs/agents/gotchas.md` | Junk URLs, timeouts, Imagine vs stub, Hermes cwd |
| Bar gaps | `docs/bar/STATUS.md` | What shipped vs still missing |
| Change X | `docs/agents/change-playbook.md` | Smallest patch |
| Whole product (intent) | `docs/superpowers/specs/2026-08-19-ALL-BOXES.md` | What each box owns |
| This screen | `docs/architecture/command-center.md` | Who owns policy |
| Why | `docs/decisions/` | Do not "improve" a locked choice |
| Words | `docs/conventions/words-we-use.md` | On-screen language |
| How a person uses it | `docs/runbooks/make-a-post.md` | Employee steps |
| Demo plan | `docs/superpowers/plans/2026-08-19-demo.md` | Historical. **Already built.** |

If the thing you want to add does not exist in the repo yet, write a one-page note first (owns / must not own / main flow / failure). Then code against that note.

A reviewer should be able to fail a PR from the convention file. If they cannot, you wrote a blog post.
