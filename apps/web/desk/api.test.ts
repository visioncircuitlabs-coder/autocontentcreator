import assert from "node:assert/strict";
import test from "node:test";
import { messageForHttpError } from "./api.ts";

test("uses the engine's own error text", () => {
  assert.equal(
    messageForHttpError(500, '{"error":"Trend fetch hit a snag. Please try again."}'),
    "Trend fetch hit a snag. Please try again.",
  );
});

test("too many searches is plain", () => {
  assert.equal(
    messageForHttpError(429, ""),
    "Too many searches. Wait a minute and try again.",
  );
});

test("gateway timeout is a long look, not a blank snag", () => {
  assert.equal(
    messageForHttpError(504, "<html>Gateway Timeout</html>"),
    "That took too long. Try again.",
  );
});

test("bad gateway means the engine is down", () => {
  assert.equal(
    messageForHttpError(502, ""),
    "The news engine is not running. Start it, then try Look for ideas again.",
  );
});
