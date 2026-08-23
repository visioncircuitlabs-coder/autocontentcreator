import assert from "node:assert/strict";
import test from "node:test";
import {
  agoNote,
  breakerTone,
  formatMoney,
  formatPercent,
  OPS_BREAKER_LABELS,
  spendFraction,
} from "./words.ts";

test("percent formatting keeps a blank for no decisions yet", () => {
  assert.equal(formatPercent(null), "—");
  assert.equal(formatPercent(undefined), "—");
});

test("percent formatting rounds to whole numbers", () => {
  assert.equal(formatPercent(0.5), "50%");
  assert.equal(formatPercent(2 / 3), "67%");
  assert.equal(formatPercent(1), "100%");
  assert.equal(formatPercent(0), "0%");
});

test("spend fraction clamps into the bar, never past it", () => {
  assert.equal(spendFraction(0.5, 2), 0.25);
  assert.equal(spendFraction(4, 2), 1);
  assert.equal(spendFraction(0.3, 0), 0);
  assert.equal(spendFraction(-1, 2), 0);
});

test("money reads like a price tag", () => {
  assert.equal(formatMoney(0), "$0.00");
  assert.equal(formatMoney(0.06), "$0.06");
  assert.equal(formatMoney(2), "$2.00");
});

test("breaker dot: green closed, amber half_open, red open", () => {
  assert.equal(breakerTone("closed"), "ok");
  assert.equal(breakerTone(null), "ok");
  assert.equal(breakerTone("half_open"), "warn");
  assert.equal(breakerTone("open"), "down");
  assert.equal(OPS_BREAKER_LABELS[breakerTone("open")], "Model calls paused");
});

test("last runs read as plain time-ago words", () => {
  const now = Date.parse("2026-08-24T12:00:00Z");
  assert.equal(agoNote(null, now), "not yet");
  assert.equal(agoNote("2026-08-24T11:59:30+00:00", now), "30s ago");
  assert.equal(agoNote("2026-08-24T11:00:00+00:00", now), "1h ago");
  assert.equal(agoNote("2026-08-24T11:45:00+00:00", now), "15m ago");
  assert.equal(agoNote("2026-08-22T12:00:00+00:00", now), "2d ago");
  assert.equal(agoNote("not-a-stamp", now), "—");
});
