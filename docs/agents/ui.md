# UI walk

Default product is **App Mode**: one page, five beats. Graph is optional.

Entry: `apps/web/app/page.tsx` → `walk/WalkApp.tsx`. Shell: `walk/WalkShell.tsx`. Graph: `walk/MachineGraph.tsx`.

## Beats

| n | id | Button / act | API |
|---|---|---|---|
| 1 | look | **Look for ideas** | `POST /radar/run` then maybe `POST /radar/fixture` |
| 2 | pick | Read the idea; optional sample | none |
| 3 | make | **Make a post** → pick Version 1/2/3 → **Make the picture** | `POST /factory/run` then `POST /factory/image` |
| 4 | call | name + why, **Yes, keep this** / **No, do not use this** | `POST /review/{draft_id}` |
| 5 | preview | phone frame, **Download pack** | `GET /export/{draft_id}` |

Words: `apps/web/desk/words.ts`. Map: `docs/conventions/words-we-use.md`.

## Rules the walk already encodes

- **Look does not wipe today’s headlines** if you later open a practice idea. `signals` / `scores` from this run stay. Practice is labeled.
- **Sample idea** only after this search stored zero closer looks (`shouldOfferFixture`).
- **Also in this look / Today’s headlines** even on practice, from this-run signals. Cap 8. Sorted closer-look first.
- **Sources** is a `<details>` fold. Junk URLs never listed (`isJunkSourceUrl` in `desk/review.ts`).
- **Make a post** = text factory only. Do not call Imagine here.
- **Make the picture** after a version is selected. One photo for that `draft_id`. Then beat 4.
- Yes/No stay disabled until name and why are non-empty (`canSubmitReview`). API also rejects blanks.
- Every yes/no lands in brand memory (`data/memory/`); Preview says so in one quiet line. See [memory.md](memory.md).
- Quiet sources: `News wire sent nothing back` (etc.), keep going.
- 504 copy is **That took too long. Try again.** — not “that look took too long.” Factory and Imagine also sit behind the same proxy.
- Client events (`logClient`) never block the walk.

## Why delaying the photo does not weaken Pick

Pick and caption judges are **text**. Imagine is a later render. Do not “help” ranking by generating three photos up front (that is what blew the 5-minute page budget).

## Leftover desk routes

`/radar` `/factory` `/queue` `/preview/[id]` still mount. Home is the walk. Do not revive the 17-box rail as default chrome (`docs/decisions/022-walk-ui.md`).

## Changing copy

1. Edit `apps/web/desk/words.ts` (or the runbook, not both with different words).
2. Run `npm test` in `apps/web`.
3. Read `.grok/skills/plain-english/SKILL.md`. No Hassid patterns (`docs/conventions/words-we-use.md`).
