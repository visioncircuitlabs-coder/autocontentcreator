import assert from "node:assert/strict";
import test from "node:test";
import {
  canSubmitReview,
  isJunkSourceUrl,
  missingSources,
  readableQuote,
  alsoTodayHeadlines,
  shouldOfferFixture,
  sortSignals,
  sourceFields,
  sourceLinkLabel,
  ticketTone,
} from "./review.ts";
import {
  ALSO_TODAY,
  PICTURE_BUTTON,
  SAMPLE_BUTTON,
  SOURCES_BUTTON,
  TODAY_HEADLINES,
  VIDEO_BUTTON,
  VIDEO_HINT,
  checkLines,
  emptySourceNote,
  gateLabel,
} from "./words.ts";

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

test("practice idea still lists today's headlines", () => {
  const signals = [
    { signal_id: "news-a", title: "Vogue double cleanse" },
    { signal_id: "fixture", title: "Hydro Boost practice" },
    { signal_id: "news-b", title: "Monsoon moisturizer talk" },
  ];
  const scores = [
    { signal_id: "news-a", gate: "background", brand_fit: 6 },
    { signal_id: "fixture", gate: "deep_dive", brand_fit: 9 },
    { signal_id: "news-b", gate: "background", brand_fit: 5 },
  ];
  const rows = alsoTodayHeadlines(signals, scores, "fixture");
  assert.deepEqual(
    rows.map((item) => item.signal_id),
    ["news-a", "news-b"],
  );
  assert.equal(TODAY_HEADLINES, "Today's headlines");
  assert.equal(ALSO_TODAY, "Also in this look");
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

test("check lines mention a second Grok pass", () => {
  const lines = checkLines({
    round: 2,
    judge: { verdict: "PASS", craft: "PASS" },
    flag_human: false,
    rules: [],
  });
  assert.ok(lines.some((line) => line.includes("round 2")));
  assert.ok(lines.some((line) => line.includes("reads like a post")));
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

test("script dumps are not something we read", () => {
  assert.equal(
    readableQuote("window.WIZ_global_data = {'AfY8Hf':true};"),
    "",
  );
  assert.equal(readableQuote("PNG IHDR IDAT garbage"), "");
  assert.equal(
    readableQuote("Double cleansing at night is getting a closer look."),
    "Double cleansing at night is getting a closer look.",
  );
});

test("google image urls are not sources", () => {
  assert.equal(
    isJunkSourceUrl("https://lh3.googleusercontent.com/a/photo=s400"),
    true,
  );
  assert.equal(
    sourceFields({
      url: "https://lh3.googleusercontent.com/a/photo=s400",
      quote: "PNG IHDR IDAT",
    }).url,
    "",
  );
});

test("tracker urls are not sources", () => {
  assert.equal(
    isJunkSourceUrl("https://www.google-analytics.com/g/collect"),
    true,
  );
  assert.equal(
    sourceFields({
      url: "https://www.google-analytics.com/g/collect",
      quote: "ok",
    }).url,
    "",
  );
  assert.equal(isJunkSourceUrl("https://www.vogue.in/beauty/story"), false);
});

test("sources control is one short word", () => {
  assert.equal(SOURCES_BUTTON, "Sources");
});

test("picture button waits until a version is picked", () => {
  assert.equal(PICTURE_BUTTON, "Make the picture");
});

test("short video button is plain language", () => {
  assert.equal(VIDEO_BUTTON, "Make a short video");
  assert.match(VIDEO_HINT, /five seconds/i);
  assert.match(VIDEO_HINT, /does not go live/i);
});

test("google news urls get a short name", () => {
  assert.equal(
    sourceLinkLabel(
      "https://news.google.com/rss/articles/CBMiqAFBVV95cUxPTHNIWmlFQm1?oc=5",
    ),
    "Google News",
  );
  assert.equal(sourceLinkLabel("https://www.vogue.in/beauty/story"), "vogue.in");
});
