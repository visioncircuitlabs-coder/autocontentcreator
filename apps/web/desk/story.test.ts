import assert from "node:assert/strict";
import test from "node:test";
import { BOX_STORY, lineForEvent, liveLines } from "./story.ts";

test("picture waits until a version is picked", () => {
  assert.match(BOX_STORY.art.takes, /version you picked/i);
  assert.match(BOX_STORY.loop.then, /pick a version/i);
  assert.match(BOX_STORY.art.does, /4:5/i);
});

test("radar boxes tell a person what happens next", () => {
  assert.match(BOX_STORY.fetcher.then, /scorer/i);
  assert.match(BOX_STORY.scorer.gives, /closer look/i);
  assert.equal(BOX_STORY.scorer.gives.includes("deep_dive"), false);
  assert.match(BOX_STORY.researcher.gives, /Pick/i);
});

test("google news fetch becomes a plain line", () => {
  const line = lineForEvent({
    id: "a",
    kind: "fetch_source",
    payload: { source: "news_rss", n: 20, ok: true },
  });
  assert.equal(line?.box, "fetcher");
  assert.equal(line?.line, "Google News sent 20 headlines.");
});

test("a dead news wire stays on the walk", () => {
  const line = lineForEvent({
    id: "b",
    kind: "fetch_source",
    payload: { source: "gdelt", n: 0, ok: false, error: "429" },
  });
  assert.equal(line?.line, "News wire sent nothing back. We kept going.");
});

test("scorer names the closer look, not the gate", () => {
  const line = lineForEvent({
    id: "c",
    kind: "radar_scored",
    payload: {
      gates: { deep_dive: 1, background: 14 },
      top: [{ title: "How double cleansing can make your nighttime skincare routine more effective - Vogue India", gate: "deep_dive" }],
    },
  });
  assert.equal(line?.box, "scorer");
  assert.match(line?.line ?? "", /Closer look: How double cleansing/);
  assert.equal(line?.line.includes("deep_dive"), false);
});

test("live lines run fetch then score then research", () => {
  const lines = liveLines([
    { id: "3", kind: "radar_end", payload: { n_reports: 1 } },
    { id: "2", kind: "radar_scored", payload: { gates: { deep_dive: 1 } } },
    { id: "1", kind: "fetch_source", payload: { source: "news_rss", n: 20, ok: true } },
  ]);
  assert.deepEqual(
    lines.map((row) => row.box),
    ["fetcher", "scorer", "researcher"],
  );
});
