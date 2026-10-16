#!/usr/bin/env python3
"""Sūtra Nexus v2 checks. Run from the repository root: python3 verify.py

Keeps the v1 count and pratyāhāra checks. v2 allows exactly one
https://linktr.ee/cyphermonkey URL and exactly one optional zip.
mailto, dev.to, and email-shaped text stay banned. The personal GitHub account used in v1 stays banned.
"""
import os
import re
import json
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, "tools")
from nexus_lib import load, selftest

ok = True

def check(name, cond, detail=""):
    global ok
    status = "PASS" if cond else "FAIL"
    print(f"{status} {name}" + (f" — {detail}" if detail else ""))
    ok = ok and bool(cond)

ashta = json.load(open("data/ashtadhyayi.json", encoding="utf-8"))
maha = json.load(open("data/maheshvara.json", encoding="utf-8"))
shiva = json.load(open("data/shiva_sutras_kashmir.json", encoding="utf-8"))
check("Aṣṭādhyāyī count 3983", len(ashta["sutras"]) == 3983 and ashta["meta"]["count"] == 3983, str(len(ashta["sutras"])))
check("unique numbers 3983", len({row["num"] for row in ashta["sutras"]}) == 3983)
check("Māheśvara count 14", len(maha["sutras"]) == 14)
check("Kashmir count 75", len(shiva["sutras"]) == 75)
try:
    check("pratyāhāra self-test", selftest(maha))
except AssertionError as exc:
    check("pratyāhāra self-test", False, str(exc))

DISCLAIMER = "Sūtra Nexus is an independent, free, learning-only student project."
BLOCKS = ['id="learn"', 'id="visual"', 'id="example"', 'id="quiz"', 'id="sources"', 'id="ecosystem"', "data-canon-footer", DISCLAIMER]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED = {
    "cyphermonkeylabs.com", "github.com", "linktr.ee", "x.com", "www.linkedin.com",
    "linkedin.com", "huggingface.co", "ashtadhyayi.com", "gretil.sub.uni-goettingen.de",
    "en.wikipedia.org", "simpleicons.org", "animejs.com", "roughjs.com", "threejs.org",
    "d3js.org", "markmap.js.org",
}
GITHUB_OK = ("/CypherMonkeyLabs", "/ashtadhyayi-com/", "/notofonts/", "/catdad/")

mailto, devto, cipher, emails, bad_hosts = [], [], [], [], []
linktree = set()
zips = []
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [name for name in dirnames if name not in {".git", "node_modules"}]
    for name in filenames:
        path = os.path.join(dirpath, name)
        rel = path[2:] if path.startswith("./") else path
        if rel.endswith(".zip"):
            zips.append(rel)
        ext = os.path.splitext(name)[1]
        if ext not in {".html", ".js", ".mjs", ".css", ".json", ".md", ".svg", ".txt", ".py"}:
            continue
        if rel.startswith("data/") or (rel.startswith("vendor/") and ext == ".js"):
            continue
        if rel in {"verify.py", "scripts/verify.mjs"}:
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if re.search(r"mailto:", text, re.I):
            mailto.append(rel)
        if re.search(r"(^|[^\w])dev\.to([^\w]|$)", text, re.I):
            devto.append(rel)
        if "cipher0x9" in text:
            cipher.append(rel)
        found = EMAIL.findall(text)
        if found:
            emails.append(rel)
        for url in re.findall(r"https?://linktr\.ee/[A-Za-z0-9_.-]+", text):
            linktree.add(url)
        if ext == ".html" and not rel.startswith("downloads/"):
            if rel == "offline.html":
                check("offline footer", "data-canon-footer" in text and DISCLAIMER in text)
            else:
                missing = [bit for bit in BLOCKS if bit not in text]
                quizzes = text.count('class="quiz-q"')
                check(rel, not missing and quizzes >= 5, f"missing={missing} quizzes={quizzes}")
        for url in re.findall(r'(?:href|src)\s*=\s*["\'](https?://[^"\']+)', text):
            host = re.sub(r"^https?://", "", url).split("/")[0]
            if host == "github.com" and not any(bit in url for bit in GITHUB_OK):
                bad_hosts.append(rel + " " + url)
            elif host != "github.com" and host not in ALLOWED:
                bad_hosts.append(rel + " " + url)

check("no mailto", not mailto, ", ".join(mailto[:5]))
check("no dev.to", not devto, ", ".join(devto))
check("no cipher0x9", not cipher, ", ".join(cipher[:8]))
check("no email-shaped text", not emails, ", ".join(emails[:4]))
check("one optional zip", zips == ["downloads/sutra-nexus-all.zip"], ", ".join(zips))
check("only linktr.ee/cyphermonkey", linktree == {"https://linktr.ee/cyphermonkey"}, ", ".join(sorted(linktree)))
check("allowed hosts", not bad_hosts, " | ".join(bad_hosts[:8]))

css = open("assets/css/sutra.css", encoding="utf-8").read()
check("banner nowrap", "flex-wrap: nowrap" in css and ".section-rail" in css)
check("drawer transform", "transform: translateX" in css)
credits = open("credits.html", encoding="utf-8").read()
for needle in ["anime", "rough", "three", "d3", "confetti", "markmap", "Simple Icons", "Noto Sans Devanagari", "7631b317cbf2cad236403df960b5d5fac353a6de"]:
    check("credits " + needle, needle in credits)
for name in os.listdir("vendor"):
    if name == "README.md":
        continue
    low = credits.lower()
    key = name.split(".")[0].replace("esm", "").replace("module", "").replace("min", "").replace("browser", "")
    check("vendor " + name, name.split(".")[0].split("-")[0].lower() in low or "confetti" in name and "confetti" in low)

animated = 0
diagrams = 0
if os.path.isdir("downloads/diagrams"):
    for name in os.listdir("downloads/diagrams"):
        if name.endswith(".svg"):
            diagrams += 1
            if "animateMotion" in open(os.path.join("downloads/diagrams", name), encoding="utf-8").read():
                animated += 1
check("at least 54 diagrams", diagrams >= 54, str(diagrams))
check("at least 30 animated flows", animated >= 30, str(animated))

sys.exit(0 if ok else 1)
