# 024 — Unofficial Lay's Chile Limón client demo

**Status:** filled  
**When:** 2026-09-02  
**Where:** this worktree, `feat/foolproof-design` family (`cursor/lays-chile-limon-demo-3ae9`)

## What the user would see

A founder walk on http://localhost:3050 with `BRAND_SLUG=lays`: look for snack ideas, pick the moment, pick the Chile Limón packet, get flavour captions, see a campaign-grade 4:5 still in the phone preview, say yes/no with a name, download a paused ZIP. The preview says Lay's, not Neutrogena. Unofficial, not PepsiCo.

## The problem

The walkable demo was Neutrogena-only. A same-day client demo needed unofficial Lay's Chile Limón, a packet picker, and an ad that looks like a real Instagram still — not a catalog JPEG of the bag, and not a second LAY'S wordmark stamped on top of a bag that already has the mark.

Older invariants said brand marks must not go into Imagine. The founder overrode that for this demo.

## Decision

- Keep Neutrogena as the default fixture when `BRAND_SLUG` is unset. Client demo sets `BRAND_SLUG=lays`.
- Ship a full unofficial Lay's pack next to `fixtures/lays/products/chile-limon.jpg`.
- `GET /brand` and `GET /brand/products` drive the walk so Neutrogena cannot leak into a Lays preview.
- Factory takes the chosen SKU. Five India flavours in the picker; Chile Limón is the hero. No sixth SKU.
- Imagine may include the Lay's logo because it is on the real pack. Overlay stamps the unofficial disclaimer only — never a second wordmark.
- Stub/Imagine-fail paints a 4:5 campaign still from the real pack photo (lime/chilli scene), not the raw JPEG.

## What we refused

- A new app, work on `main`, or rebuilding the 19 Aug demo
- Live Instagram publish
- Calling this a PepsiCo or official Lay's engagement
- Stamping `LAY'S` in Pillow on top of the pack photo

## Verification

`pytest` `test_lays_demo.py` plus existing Neutrogena tests. Walk: `copy .env.example .env`, `BRAND_SLUG=lays`, `docker compose up --build`, http://localhost:3050.
