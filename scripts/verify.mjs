/* Public-tree checks for Sūtra Nexus v2.
   Link rules follow the v2 brief: one Linktree URL, one optional zip,
   no mailto, no dev.to, and no personal GitHub account from v1. */
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];
function check(name, ok, detail) {
  if (!ok) failures.push(name + (detail ? ": " + detail : ""));
  else console.log("ok " + name);
}

const ashta = JSON.parse(fs.readFileSync(path.join(root, "data/ashtadhyayi.json"), "utf8"));
const maha = JSON.parse(fs.readFileSync(path.join(root, "data/maheshvara.json"), "utf8"));
const shiva = JSON.parse(fs.readFileSync(path.join(root, "data/shiva_sutras_kashmir.json"), "utf8"));
check("3983 rows", ashta.sutras.length === 3983 && ashta.meta.count === 3983, String(ashta.sutras.length));
check("14 lines", maha.sutras.length === 14);
check("75 kashmir rows", shiva.sutras.length === 75);

const self = spawnSync("python3", ["-c", "import sys; sys.path.insert(0,'tools'); from nexus_lib import selftest, load; assert selftest(load('maheshvara'))"], { cwd: root, encoding: "utf8" });
check("pratyahara self-test", self.status === 0, self.stderr);

const skipDir = new Set([".git", "node_modules"]);
const textExt = new Set([".html", ".js", ".mjs", ".css", ".json", ".md", ".svg", ".txt"]);
const files = [];
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (skipDir.has(name)) continue;
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) walk(full);
    else files.push(full);
  }
}
walk(root);

const email = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/;
const hrefRe = /(?:href|src)\s*=\s*["']([^"']+)["']/gi;
const allowedHost = [
  "cyphermonkeylabs.com",
  "github.com",
  "linktr.ee",
  "x.com",
  "www.linkedin.com",
  "linkedin.com",
  "huggingface.co",
  "ashtadhyayi.com",
  "www.ashtadhyayi.com",
  "gretil.sub.uni-goettingen.de",
  "en.wikipedia.org",
  "animejs.com",
  "roughjs.com",
  "threejs.org",
  "d3js.org",
  "markmap.js.org",
  "github.com"
];
let linktree = new Set();
let zips = [];
let mailto = [];
let emails = [];
let devto = [];
let cipher = [];
let badHosts = [];
const disclaimer = "Sūtra Nexus is an independent, free, learning-only student project.";
const pages = [];

for (const full of files) {
  const rel = path.relative(root, full);
  if (rel.startsWith("data" + path.sep)) continue;
  if (rel === "downloads/sutra-nexus-all.zip") zips.push(rel);
  else if (rel.endsWith(".zip")) zips.push(rel);
  const ext = path.extname(full);
  if (!textExt.has(ext)) continue;
  if (rel.startsWith("vendor" + path.sep) && ext === ".js") continue;
  if (rel === "verify.py" || rel === "scripts/verify.mjs") continue;
  const text = fs.readFileSync(full, "utf8");
  if (/mailto:/i.test(text)) mailto.push(rel);
  if (/(^|[^\w])dev\.to([^\w]|$)/i.test(text)) devto.push(rel);
  if (/cipher0x9/i.test(text)) cipher.push(rel);
  const found = text.match(email);
  if (found) emails.push(rel + " " + found.slice(0, 2).join(","));
  const trees = text.match(/https?:\/\/linktr\.ee\/[A-Za-z0-9_.-]+/g) || [];
  trees.forEach((url) => linktree.add(url));
  if (ext === ".html" && rel.startsWith("downloads" + path.sep) && rel !== "downloads/sutra-nexus-single-file.html") {
    check(rel + " standalone", text.includes("<style") && !text.includes("sutra.css") && !text.includes("assets/"));
  }
  if (rel === "downloads/sutra-nexus-single-file.html") {
    check("single-file app", text.includes("<style") && !text.includes("sutra.css") && !text.includes('src="assets/') && text.includes("SUTRA_EMBED"));
  }
  if (ext === ".html" && !rel.startsWith("downloads" + path.sep)) pages.push(rel);
  let match;
  hrefRe.lastIndex = 0;
  while ((match = hrefRe.exec(text))) {
    const url = match[1];
    if (!/^https?:/i.test(url)) continue;
    let host = "";
    try { host = new URL(url).host; } catch (err) { badHosts.push(rel + " " + url); continue; }
    if (url.includes("simpleicons.org") || url.includes("notofonts")) badHosts.push(rel + " " + url);
    if (host === "github.com" && !url.includes("github.com/CypherMonkeyLabs") && !url.includes("github.com/ashtadhyayi-com/") && !url.includes("github.com/catdad/")) {
      badHosts.push(rel + " " + url);
    }
    if (host !== "github.com" && allowedHost.indexOf(host) === -1) badHosts.push(rel + " " + url);
  }
}

check("no mailto", mailto.length === 0, mailto.slice(0, 5).join(", "));
check("no dev.to", devto.length === 0, devto.join(", "));
check("no cipher0x9", cipher.length === 0, cipher.slice(0, 8).join(", "));
check("no email-shaped text", emails.length === 0, emails.slice(0, 4).join(" | "));
check("one zip", zips.length === 1 && zips[0] === "downloads/sutra-nexus-all.zip", zips.join(", "));
check("only linktr.ee/cyphermonkey", linktree.size === 1 && linktree.has("https://linktr.ee/cyphermonkey"), [...linktree].join(", "));
check("allowed hosts", badHosts.length === 0, badHosts.slice(0, 8).join(" | "));

const blocks = ["id=\"learn\"", "id=\"visual\"", "id=\"example\"", "id=\"quiz\"", "id=\"sources\"", "id=\"ecosystem\"", "data-canon-footer", disclaimer];
for (const rel of pages) {
  if (rel === "offline.html") {
    const text = fs.readFileSync(path.join(root, rel), "utf8");
    check("offline footer", text.includes("data-canon-footer") && text.includes(disclaimer));
    continue;
  }
  const text = fs.readFileSync(path.join(root, rel), "utf8");
  const missing = blocks.filter((bit) => !text.includes(bit));
  const quizzes = (text.match(/class="quiz-q"/g) || []).length;
  check(rel + " room shape", missing.length === 0 && quizzes >= 5, missing.join(",") + " quizzes=" + quizzes);
}

const css = fs.readFileSync(path.join(root, "assets/css/sutra.css"), "utf8");
check("banner does not wrap", css.includes("flex-wrap: nowrap") && css.includes(".section-rail"));
check("drawer uses transform", css.includes("transform: translateX"));
const credits = fs.readFileSync(path.join(root, "credits.html"), "utf8");
for (const needle of ["anime", "rough", "three", "d3", "confetti", "markmap", "Simple Icons", "Noto Sans Devanagari", "7631b317cbf2cad236403df960b5d5fac353a6de"]) {
  check("credits mention " + needle, credits.includes(needle));
}
for (const file of fs.readdirSync(path.join(root, "vendor"))) {
  if (file === "README.md") continue;
  const named = file.replace(".esm.min.js", "").replace(".module.min.js", "").replace(".browser.js", "").replace(".min.js", "").replace(".esm.js", "");
  const ok = credits.toLowerCase().includes(named.split(".")[0].toLowerCase()) || (file.startsWith("confetti") && credits.includes("confetti")) || (file.startsWith("markmap") && credits.includes("markmap")) || (file.startsWith("anime") && credits.includes("anime")) || (file.startsWith("rough") && credits.includes("rough")) || (file.startsWith("three") && credits.includes("three")) || (file.startsWith("d3") && credits.includes("d3"));
  check("vendor credited " + file, ok);
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log("verify.mjs passed");
