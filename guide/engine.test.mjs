import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { createGuide, blankSession } from "./engine.mjs";

const kb = JSON.parse(fs.readFileSync(new URL("./kb/bundle.json", import.meta.url), "utf8"));
const guide = createGuide(kb, { rng: () => 0 });

function sortedQuizzes() {
  return kb.quizzes.slice().sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

test("a right answer and a wrong answer are graded from the notes", () => {
  const first = sortedQuizzes()[0];
  const second = sortedQuizzes()[1];
  let session = blankSession();
  let out = guide.route("Quiz me", session, { page: "index.html", room: "index" });
  session = out.session;
  assert.equal(out.reply.kind, "quiz");
  assert.equal(out.reply.question.prompt, first.question);
  out = guide.route(first.choices[first.answer], session, { page: "index.html", room: "index" });
  session = out.session;
  assert.match(out.reply.text, /That's the one in the notes/);
  assert.doesNotMatch(out.reply.text, /Not this one/);
  out = guide.route(second.choices[(second.answer + 1) % second.choices.length], session, {});
  assert.match(out.reply.text, /Not this one/);
  assert.doesNotMatch(out.reply.text, /That's the one in the notes/);
});

test("an unknown question is not guessed", () => {
  const out = guide.route("population of a city that is not in these notes", blankSession(), { page: "index.html", room: "index" });
  assert.equal(out.reply.kind, "fallback");
  assert.match(out.reply.text, /confirm before relying/);
  assert.match(out.reply.text, /will not guess/);
});

test("how do I use this cites the start page", () => {
  const out = guide.route("How do I use this?", blankSession(), { page: "about.html", room: "about" });
  assert.equal(out.reply.href, "index.html");
  assert.match(out.reply.text, /From /);
});
