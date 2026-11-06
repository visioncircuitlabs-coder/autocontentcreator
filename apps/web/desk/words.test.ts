import assert from "node:assert/strict";
import test from "node:test";
import { decisionLine, makePostFor, memoryLine } from "./words.ts";

test("memory line tells the person the machine learned", () => {
  assert.match(memoryLine(true), /brand memory/i);
  assert.match(memoryLine(false), /brand memory/i);
});

test("memory line differs for approve vs reject", () => {
  assert.notEqual(memoryLine(true), memoryLine(false));
  assert.match(memoryLine(true), /winner/i);
  assert.match(memoryLine(false), /anti-pattern/i);
});

test("make a post names the packet", () => {
  assert.equal(makePostFor("Chile Limón"), "Make a post for Chile Limón");
  assert.match(makePostFor(""), /Make a post/);
});

test("decision line still names the human and verdict", () => {
  const line = decisionLine("Rithwik", true);
  assert.match(line, /Rithwik/);
  assert.match(line, /yes/);
});
