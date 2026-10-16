/* Build guide/kb/bundle.json from content/site.json.
   The router is guide/engine.mjs, adapted from Webex Lab at
   7631b317cbf2cad236403df960b5d5fac353a6de. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const site = JSON.parse(fs.readFileSync(path.join(root, "content/site.json"), "utf8"));
const games = Array.isArray(site.games) ? site.games : [];
const kb = {
  intents: [
    { id: "quiz", phrases: ["quiz me", "test me"] },
    { id: "lesson", phrases: ["teach me", "teach me this room"] },
    { id: "game", phrases: ["play a game"] },
    { id: "cards", phrases: ["flashcards", "show the cards"] },
    { id: "start", phrases: ["how do i use this", "start here"] },
    { id: "help", phrases: ["help", "what can you do"] },
    { id: "progress", phrases: ["my progress"] },
    { id: "identity", phrases: ["who are you"] },
    { id: "tour", phrases: ["tour this room", "show me around"] }
  ],
  synonyms: {
    pratyahara: "pratyāhāra",
    ashtadhyayi: "aṣṭādhyāyī"
  },
  rooms: site.rooms,
  facts: site.facts,
  quizzes: site.quizzes,
  cards: site.cards,
  lessons: site.lessons,
  tours: site.tours,
  pages: site.pages,
  curriculum: site.curriculum,
  games: { ports: games, rooms: games },
  counts: { sutras: 3983, lines: 14, kashmir: 75 }
};
const dir = path.join(root, "guide/kb");
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, "bundle.json"), JSON.stringify(kb));
console.log("kb", kb.facts.length, "facts", kb.quizzes.length, "quizzes", kb.cards.length, "cards", kb.rooms.length, "rooms");
