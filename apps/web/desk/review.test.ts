import assert from "node:assert/strict";
import test from "node:test";
import {
  FIXTURE_BUTTON,
  canSubmitReview,
  emptySourceNote,
  missingSources,
  shouldOfferFixture,
  sortSignals,
  sourceFields,
  ticketTone,
} from "./review.ts";

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
    "GDELT returned nothing. The pipe logged it and the rest of the desk kept moving.",
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

test("fixture offer only after a Fetch with 0 deep_dives", () => {
  assert.equal(shouldOfferFixture(false, 0), false);
  assert.equal(shouldOfferFixture(true, 1), false);
  assert.equal(shouldOfferFixture(true, 0), true);
  assert.match(FIXTURE_BUTTON, /unofficial fixture/i);
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
