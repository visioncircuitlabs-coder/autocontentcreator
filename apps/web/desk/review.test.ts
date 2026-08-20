import assert from "node:assert/strict";
import test from "node:test";
import {
  canSubmitReview,
  missingSources,
  shouldOfferFixture,
  sortSignals,
  sourceFields,
  ticketTone,
} from "./review.ts";
import { SAMPLE_BUTTON, checkLines, emptySourceNote, gateLabel } from "./words.ts";

test("blank reason cannot submit", () => {
  assert.equal(canSubmitReview("Anand", ""), false);
  assert.equal(canSubmitReview("Anand", "   "), false);
});

test("blank clerk cannot submit", () => {
  assert.equal(canSubmitReview("", "on-claim for India"), false);
  assert.equal(canSubmitReview("  ", "on-claim for India"), false);
});

test("named clerk plus reason can submit", () => {
  assert.equal(
    canSubmitReview("Anand", "Approved dermatologist-tested only."),
    true,
  );
});

test("missing sources are named plainly", () => {
  assert.deepEqual(missingSources([]), ["gdelt", "news_rss", "reddit"]);
  assert.deepEqual(missingSources([{ source: "news_rss" }]), ["gdelt", "reddit"]);
  assert.equal(
    emptySourceNote("gdelt"),
    "News wire sent nothing back. We kept going.",
  );
});

test("deep_dive tickets sort first", () => {
  const signals = [
    { signal_id: "a" },
    { signal_id: "b" },
    { signal_id: "c" },
  ];
  const scores = [
    { signal_id: "a", gate: "discard", brand_fit: 9 },
    { signal_id: "b", gate: "deep_dive", brand_fit: 4 },
    { signal_id: "c", gate: "background", brand_fit: 8 },
  ];
  assert.deepEqual(
    sortSignals(signals, scores).map((item) => item.signal_id),
    ["b", "c", "a"],
  );
});

test("kill and deep_dive get inspection tones", () => {
  assert.equal(ticketTone("discard", "kill"), "kill");
  assert.equal(ticketTone("deep_dive", "ok"), "gate");
});

test("sample idea only after a search with nothing to look at", () => {
  assert.equal(shouldOfferFixture(false, 0), false);
  assert.equal(shouldOfferFixture(true, 1), false);
  assert.equal(shouldOfferFixture(true, 0), true);
  assert.match(SAMPLE_BUTTON, /sample idea/i);
});

test("gates speak English on the card", () => {
  assert.equal(gateLabel("deep_dive"), "Closer look");
  assert.equal(gateLabel("background"), "Skip for now");
  assert.equal(gateLabel("discard"), "Don't use");
});

test("check lines hide judge jargon", () => {
  const lines = checkLines({
    rules: ["banned token: cures"],
    flag_human: true,
    judge: { verdict: "FAIL", reasons: ["1. forbidden claim"] },
  });
  assert.ok(lines.some((line) => line.includes("We blocked this")));
  assert.ok(lines.some((line) => line.includes("person still has to decide")));
});

test("source fields expose url, quote, and hash", () => {
  const row = sourceFields({
    url: "https://news.example/skincare-spike",
    quote: "barrier-cream talk",
    hash: "abc",
  });
  assert.equal(row.url, "https://news.example/skincare-spike");
  assert.equal(row.quote, "barrier-cream talk");
  assert.equal(row.hash, "abc");
  assert.equal(sourceFields({}).url, "");
});
