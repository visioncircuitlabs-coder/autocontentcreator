# Why we built this

## The goal

Build an always-on content machine that a large, regulated consumer brand
(health, beauty, personal care, packaged food) could actually trust in
production. The target buyer is a big company with a legal team, a claims
matrix and medical or regulatory review, starting in India and then going
global.

Today those brands make social content slowly, by hand, through agencies,
and every post that mentions a product benefit has to clear legal. Trends move
faster than that process. We wanted to show a system that keeps up with
culture **without** ever putting an unapproved claim in front of the public.

## What the machine was meant to do

1. **Watch the world.** Pull news, search trends and community chatter, and
   score which moments actually fit the brand.
2. **Remember the brand.** Hold the brand book, the approved claims per
   country, the required disclaimers, the topics to stay away from, and every
   past human yes/no with its reason.
3. **Draft on brand.** Turn a moment into a brief, several caption angles, and
   an on-brand image or short product video.
4. **Block bad claims.** Hard coded rules plus a locked AI judge stop
   unapproved or risky claims before a human ever sees them.
5. **Keep a human in charge.** A person approves or rejects every post with a
   reason. The machine never publishes on its own; export is a reviewed pack.
6. **Get better over time.** Every decision feeds back into the brand memory so
   the next draft starts closer to a yes.

## Why it mattered

- Speed: trend to approved post in hours, not weeks.
- Safety: every claim traces back to an approved row, so a legal team can
  audit why something was allowed.
- Cost: less agency back and forth for routine always-on content.

## Status and scope

This is a working demo, not a shipped product. The brand packs in
`apps/api/fixtures/` are **unofficial demo fixtures** made for show. They are
not partner builds, not approved by the brand owners, and not real legal copy.
Real pack artwork is kept out of the repo; placeholders stand in for it.

The walkable demo lives on the `feat/foolproof-design` branch (with client
demo variants on the `cursor/*` branches). `main` holds the architecture map
(`docs/show-me-architecture.html`) and the research.

A sister project, Circuit Studio, took the same "enterprise content
automation" idea in a different direction: adapting an agency's master
creative into every channel format and language, for static and video.
