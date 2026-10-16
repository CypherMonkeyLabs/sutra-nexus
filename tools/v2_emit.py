#!/usr/bin/env python3
"""Content, diagrams, downloads, and pages for Sūtra Nexus v2."""
import base64
import json
import math
import os
import re
import struct
import zipfile

import cairosvg
from docx import Document
from docx.shared import Pt
from pptx import Presentation
from pptx.util import Emu, Inches, Pt as PptPt
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas

import build_v2 as b

ROOT = b.ROOT
DISCLAIMER = b.DISCLAIMER
CONTACT = b.CONTACT
CHECKED = b.CHECKED

def stats():
    ashta = b.load("ashtadhyayi")
    maha = b.load("maheshvara")
    shiva = b.load("shiva_sutras_kashmir")
    assert b.selftest(maha)
    known = {
        "ac": b.pratyahara(maha, "a", 1, 4),
        "ik": b.pratyahara(maha, "i", 1, 2),
        "yaṇ": b.pratyahara(maha, "y", 5, 6),
        "śar": b.pratyahara(maha, "ś", 13, 13),
        "ak": b.pratyahara(maha, "a", 1, 2),
        "ec": b.pratyahara(maha, "e", 3, 4),
        "hal": b.pratyahara(maha, "h", 5, 14),
        "al": b.pratyahara(maha, "a", 1, 14),
    }
    by_num = {row["num"]: row for row in ashta["sutras"]}
    return {
        "ashta": ashta,
        "maha": maha,
        "shiva": shiva,
        "types": dict(sorted(__import__("collections").Counter(row["type"] for row in ashta["sutras"]).items())),
        "adhyaya": [sum(1 for row in ashta["sutras"] if row["adhyaya"] == n) for n in range(1, 9)],
        "anuvritti": sum(1 for row in ashta["sutras"] if row.get("anuvritti")),
        "padaccheda": sum(1 for row in ashta["sutras"] if row.get("padaccheda")),
        "pada1": [sum(1 for row in ashta["sutras"] if row["adhyaya"] == 1 and row["pada"] == n) for n in range(1, 5)],
        "unmesha": [sum(1 for row in shiva["sutras"] if row["unmesha"] == n) for n in (1, 2, 3)],
        "known": known,
        "s111": by_num["1.1.1"],
        "s113": by_num["1.1.3"],
    }

def diagrams(st):
    items = []
    def add(kind, title, body, source, animated=False, room="diagrams"):
        slug = f"{len(items)+1:02d}-" + "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
        slug = "-".join(part for part in slug.split("-") if part)[:72]
        svg = b.svg_doc(title, body, source, animated=animated)
        items.append({"id": slug, "title": title, "source": source, "animated": animated, "room": room, "svg": svg, "kind": kind})

    sets = [
        ("ac", "a on line 1 through the marker on line 4"),
        ("ik", "i on line 1 through the marker on line 2"),
        ("yaṇ", "y on line 5 through the marker on line 6"),
        ("śar", "ś on line 13 through the marker on line 13"),
        ("ak", "a on line 1 through the marker on line 2"),
        ("ec", "e on line 3 through the marker on line 4"),
        ("hal", "h on line 5 through the marker on line 14"),
        ("al", "a on line 1 through the marker on line 14"),
    ]
    for name, how in sets:
        sounds = " ".join(st["known"][name])
        add("flow", f"Pratyāhāra {name}", b.flow_body(["Start", how, "Drop the it marker", sounds[:40] or "set"]),
            f"Computed from data/maheshvara.json. {name} has {len(st['known'][name])} sounds. Not a translation.", True, "maheshvara")
    flows = [
        ("It marker is not part of the set", ["Read a line", "The last letter is a marker", "The builder drops it", "The sounds stay"], "maheshvara"),
        ("Read a sūtra number", ["Adhyāya", "Pāda", "Sūtra", "Example 1.1.1"], "ashtadhyayi"),
        ("Anuvṛtti on 1.1.3", ["Open 1.1.3", "Read the anuvritti field", "Do not translate it here", "Confirm before relying"], "anuvrtti"),
        ("No invented meaning", ["Source text", "Script IAST", "Meaning unsourced", "Learner's note is labeled"], "about"),
        ("Six-step start path", ["Foundations", "Māheśvara", "Anuvṛtti", "Aṣṭādhyāyī", "Sandhi", "Practice"], "index"),
        ("Licence gate", ["Open the source page", "Read its licence", "Record the check", "Only then quote"], "credits"),
        ("Offline search", ["Type in the menu", "Index loads locally", "Sūtra number matches", "No network required"], "index"),
        ("Room quiz", ["Read the note", "Pick an answer", "Read why", "Score stays on this device"], "play"),
        ("Flashcard ladder", ["See the front", "Show the back", "Again is one minute", "Know waits a day, then longer"], "play"),
        ("Eight chapters", ["Book 1", "Books 2 to 7", "Book 8", "Counts are from the file"], "ashtadhyayi"),
        ("Four pādas", ["A chapter", "Four sections", "Wikipedia checked 2026-10-16", "Confirm the edition you cite"], "ashtadhyayi"),
        ("Type letters in the file", ["S 200", "P 23", "V 3629", "AT and AD stay unexpanded"], "ashtadhyayi"),
        ("Dhātu gap", ["The term is a verb root", "This file has no dhātu list", "Do not invent forms", "Mark the gap"], "dhatu"),
        ("Three unmeshas", ["Section 1", "Section 2", "Section 3", "75 lines in this file"], "shiva"),
        ("75 and the other count", ["This file says 75", "The meta note trails off", "Differences are unknown", "Confirm before relying"], "shiva"),
        ("Guide choices", ["One-minute read", "Ten-minute read", "One-hour course", "Mute and read"], "listen"),
        ("Voice stays off", ["Default is silent", "A browser voice is optional", "Sanskrit may be wrong", "It is a reading aid"], "listen"),
        ("Every download", ["Disclaimer inside", "Credits where needed", "Individual file", "One optional zip"], "downloads"),
        ("Phone menu", ["Bottom bar", "Menu on the left", "Hint dismisses once", "Drawer uses a transform"], "index"),
        ("History stays disputed", ["Open the page", "Quote the dispute", "Do not pick a year", "Confirm before relying"], "history"),
        ("Cache skips contact", ["Same-origin files", "Contact is outside", "The worker returns", "It does not store that URL"], "about"),
        ("Report a correction", ["Use the contact form", "No email address", "Say which line", "A person can check IAST"], "about"),
        ("Sandhi without a fake join", ["Two sounds meet", "A rule would name a set", "No open rule text yet", "Use the builder for the set"], "sandhi"),
        ("Ecosystem is a map", ["Room", "Sister topic", "Bridge is labeled", "Not a historical claim"], "ecosystem"),
    ]
    for title, steps, room in flows:
        add("flow", title, b.flow_body(steps), "Learner path drawn for this app. Counts and file notes are from the data. Confirm before relying on any wider claim.", True, room)
    add("chart", "Sūtras in each adhyāya", b.bars_body([(str(i+1), n) for i, n in enumerate(st["adhyaya"])]),
        "Counted from data/ashtadhyayi.json on " + CHECKED + ". Total 3,983.", False, "charts")
    add("chart", "Type letters in the data file", b.bars_body(list(st["types"].items())),
        "S, P, V, AT, AD are the file's own letters. The meta glosses only S, P, and V. AT and AD are not expanded here.", False, "charts")
    add("chart", "Lines with an anuvṛtti field", b.bars_body([("with", st["anuvritti"]), ("without", 3983 - st["anuvritti"])]),
        f"{st['anuvritti']} of 3,983 rows have a non-empty anuvritti array in the file.", False, "anuvrtti")
    add("mind", "Start here map", b.mind_body("Start", ["Sounds", "14 lines", "Read a sūtra", "Sandhi", "Practice", "Sources"]),
        "A map of this app's path, not a traditional curriculum.", False, "index")
    add("mind", "Foundations map", b.mind_body("Script", ["Devanāgarī", "IAST", "14 lines", "Śikṣā term", "Unsourced chart"]),
        "Śikṣā is cited from Wikipedia's short description, checked " + CHECKED + ".", False, "foundations")
    add("mind", "Grammar map", b.mind_body("Grammar", ["Chapters", "Type letters", "Anuvṛtti", "Dhātu gap", "No meaning"]),
        "Structure from the data file and the Wikipedia Aṣṭādhyāyī page checked " + CHECKED + ".", False, "ashtadhyayi")
    add("mind", "Ecosystem map", b.mind_body("Nexus", ["Phonetics", "Linguistics", "A learner bridge", "NLP is not claimed", "Confirm"]),
        "Bridges are labeled learner's notes. They are not quotations from Pāṇini.", False, "ecosystem")
    add("mind", "Room links", b.mind_body("Rooms", ["Start", "Sound", "Rules", "Practice", "Sources", "Downloads"]),
        "Navigation map of this site.", False, "ecosystem")
    lines = st["maha"]["sutras"]
    grid = []
    for row in lines:
        y = 100 + row["n"] * 28
        grid.append(f'<text class="deva" x="40" y="{y}" font-size="18" fill="#1b1340">{row["n"]}. {b.E(row["devanagari"])}  ·  {b.E(" ".join(row["sounds"]))}  · marker {b.E(row["marker"])}</text>')
    add("grid", "The fourteen Māheśvara lines", "".join(grid),
        "Devanāgarī and parsed sounds from data/maheshvara.json. The IAST field is script-converted and is not printed in this grid.", False, "maheshvara")
    add("grid", "Sounds on lines 1 to 4", b.flow_body([" ".join(lines[0]["sounds"]), " ".join(lines[1]["sounds"]), " ".join(lines[2]["sounds"]), " ".join(lines[3]["sounds"])]),
        "These are the sounds arrays on lines 1–4. This drawing does not call them a vowel chart.", False, "foundations")
    add("grid", "Sounds on lines 5 to 14", b.flow_body(["line " + str(row["n"]) + " " + row["sounds"][0] for row in lines[4:]]),
        "First sound of each later line, from the file. Not a place-of-articulation chart.", False, "foundations")
    add("compare", "This file has 75 Kashmir lines", b.bars_body([("in file", 75), ("difference", 0)]),
        "The second bar is zero because this app does not know which lines differ from the other recension. The meta note trails off. Confirm before relying.", False, "shiva")
    add("timeline", "Dating notes that were actually opened", b.flow_body(["Cardona 1997 via Wikipedia", "Not earlier than 400 BCE", "Hinüber and Falk", "Mid 4th century BCE", "This app picks neither"]),
        "Paraphrase of the English Wikipedia Pāṇini article, checked " + CHECKED + ". Dates are disputed there.", False, "history")
    add("stack", "What a row in the file holds", b.flow_body(["Number", "Devanāgarī", "IAST unchecked", "Type letter", "No English meaning"]),
        "Fields present on each Aṣṭādhyāyī row in this repository.", False, "ashtadhyayi")
    add("badges", "Three counts you can check", b.bars_body([("sūtras", 3983), ("lines", 14), ("Kashmir", 75)]),
        "3,983, 14, and 75 are the lengths of the three JSON files.", False, "index")
    add("chart", "Chapter 1 by pāda", b.bars_body([(str(i + 1), n) for i, n in enumerate(st["pada1"])]),
        "Counted from data/ashtadhyayi.json. Chapter 1 only, four sections. The other chapters are counted on the adhyāya chart.", False, "ashtadhyayi")
    add("chart", "Kashmir unmeṣa lengths", b.bars_body([("1", st["unmesha"][0]), ("2", st["unmesha"][1]), ("3", st["unmesha"][2])]),
        "Counted from the unmesha field in data/shiva_sutras_kashmir.json. The file meta writes 20+10+45. The other recension is not in this file.", False, "shiva")
    add("chart", "Rows that carry a word split", b.bars_body([("split", st["padaccheda"]), ("empty", 3983 - st["padaccheda"])]),
        "A non-empty padaccheda field in data/ashtadhyayi.json. The file calls this a word split. It is not an English meaning.", False, "ashtadhyayi")
    add("flow", "Compute a set in the builder", b.flow_body(["Pick a start sound", "Pick a marker line", "Drop the markers", "Read the count"]),
        "The builder on the Māheśvara page calls the same function as the self-test.", True, "maheshvara")
    add("flow", "What a grammar row stores", b.flow_body(["Devanāgarī", "Unchecked IAST", "Type letter", "No English gloss"]),
        "Fields on an Aṣṭādhyāyī row. The gloss field is empty in this file.", True, "ashtadhyayi")
    add("flow", "Five parts of a room", b.flow_body(["Five-minute note", "A visual", "A worked example", "A quiz", "A source list"]),
        "Every study room in this app uses this shape.", True, "index")
    add("flow", "Leave the voice off", b.flow_body(["Open the guide", "Read the card", "Voice stays off", "Turn it on only if you want"]),
        "Browser speech is a reading aid. It is not a Sanskrit recording.", True, "listen")
    add("mind", "Anuvṛtti map", b.mind_body("Carry", ["Earlier words", "File field", "Not a meaning", "1.1.3 sample", "Confirm"]),
        "The anuvritti array is copied from the data file. This map does not translate those words.", False, "anuvrtti")
    add("mind", "Download kinds", b.mind_body("Files", ["SVG", "PNG", "HTML", "PDF", "GLB", "One zip"]),
        "Individual files, plus one optional zip named sutra-nexus-all.zip.", False, "downloads")
    markers = []
    for row in lines:
        y = 108 + (row["n"] - 1) * 30
        markers.append(f'<text x="48" y="{y}" font-size="18" fill="#1b1340">{row["n"]}. marker {b.E(row["marker"])} · first sound {b.E(row["sounds"][0])}</text>')
    add("grid", "Markers on the fourteen lines", "".join(markers),
        "Marker and first sound from data/maheshvara.json. The marker is not part of a pratyāhāra set.", False, "maheshvara")
    add("chart", "Nothing is uploaded", b.bars_body([("on device", 3), ("uploaded", 0)]),
        "Theme, start-path marks, and card timing stay in this browser. The zero bar is the count of uploads. There is no account.", False, "about")
    return items

def quiz(qid, question, choices, answer, why):
    buttons = "".join(f"<button type=\"button\">{b.E(choice)}</button>" for choice in choices)
    return f'<div class="quiz-q" id="{qid}" data-answer="{answer}" data-why="{b.E(why)}"><p>{b.E(question)}</p>{buttons}<p class="why"></p></div>'

def learn_block(paragraphs):
    return '<section class="learn" id="learn"><h2>Learn it in 5 minutes</h2>' + "".join(f"<p>{b.E(p)}</p>" for p in paragraphs) + "</section>"

def example_block(title, steps):
    lis = "".join(f"<li>{b.E(step)}</li>" for step in steps)
    return f'<section class="example" id="example"><h2>Worked example</h2><h3>{b.E(title)}</h3><ol>{lis}</ol></section>'

def visual_block(item):
    return f'''<section class="diagram-card" id="visual"><h2>A visual</h2>
<figure>{item["svg"].replace('<?xml version="1.0" encoding="UTF-8"?>', '')}
<figcaption>{b.E(item["title"])}. {b.E(item["source"])}</figcaption></figure>
<p><a href="downloads/diagrams/{item["id"]}.svg">SVG</a> · <a href="downloads/diagrams/{item["id"]}.png">PNG</a> · <a href="downloads/diagrams/{item["id"]}.html">Standalone HTML</a></p>
</section>'''

def sources_block(rows):
    lis = []
    for row in rows:
        name = b.E(row["name"])
        head = f'<a href="{b.E(row["url"])}">{name}</a>' if row.get("url") else name
        lis.append(f'<li>{head}. {b.E(row["detail"])} Checked {CHECKED}. Licence: {b.E(row["licence"])}.</li>')
    return '<section class="sources" id="sources"><h2>Cited sources</h2><ul>' + "".join(lis) + "</ul></section>"

def eco_block(glossary, sisters, bridges, hooks):
    terms = "".join(f"<li><b>{b.E(term)}</b> — {b.E(defn)}</li>" for term, defn in glossary)
    return f'''<section class="eco" id="ecosystem"><h2>Ecosystem</h2>
<h3>Glossary</h3><ul>{terms}</ul>
<h3>Sister topics</h3><p>{b.E(sisters)}</p>
<h3>Bridges</h3><p>{b.E(bridges)}</p>
<h3>Later hooks</h3><p>{b.E(hooks)}</p>
</section>'''

DATA_CREDIT = {
    "name": "ashtadhyayi-com/data README",
    "url": "https://github.com/ashtadhyayi-com/data",
    "detail": "The raw README says you are free to use the data in your own projects if you give appropriate credit. No SPDX identifier is stated.",
    "licence": "credit required, no formal SPDX, confirmed from the raw README",
}
WIKI_ASHTA = {
    "name": "English Wikipedia, Aṣṭādhyāyī",
    "url": "https://en.wikipedia.org/wiki/Aṣṭādhyāyī",
    "detail": "The page says the work has 3,983 sūtras in eight chapters, each subdivided into four pādas, and lists vidhi, paribhāṣā, adhikāra, atideśa, niyama, and negation rules. CC BY-SA.",
    "licence": "CC BY-SA 4.0",
}
WIKI_PANINI = {
    "name": "English Wikipedia, Pāṇini",
    "url": "https://en.wikipedia.org/wiki/Pāṇini",
    "detail": "The page reports Cardona (1997) that evidence supports a date no earlier than 400 BCE, and that Hinüber (1989) and Falk (1993) place him in the mid-4th century BCE. The dates are disputed on that page.",
    "licence": "CC BY-SA 4.0",
}
WIKI_SHIKSHA = {
    "name": "English Wikipedia, Shiksha",
    "url": "https://en.wikipedia.org/wiki/Shiksha",
    "detail": "Short description on the page: a Vedic-era study of phonetics and phonology, one of six Vedangas.",
    "licence": "CC BY-SA 4.0",
}
WIKI_SANDHI = {
    "name": "English Wikipedia, Sandhi",
    "url": "https://en.wikipedia.org/wiki/Sandhi",
    "detail": "Short description on the page: a type of sound change at morpheme or syllable boundaries.",
    "licence": "CC BY-SA 4.0",
}
WIKI_IAST = {
    "name": "English Wikipedia, IAST",
    "url": "https://en.wikipedia.org/wiki/International_Alphabet_of_Sanskrit_Transliteration",
    "detail": "Short description: a transliteration scheme for Indic scripts. The page names the 19th century onward.",
    "licence": "CC BY-SA 4.0",
}
WIKI_DEVA = {
    "name": "English Wikipedia, Devanagari",
    "url": "https://en.wikipedia.org/wiki/Devanagari",
    "detail": "Short description: an Indic script used in the Indian subcontinent.",
    "licence": "CC BY-SA 4.0",
}
WIKI_MAHA = {
    "name": "English Wikipedia, Shiva Sutras (phoneme list)",
    "url": "https://en.wikipedia.org/wiki/Shiva_Sutras",
    "detail": "Short description: 14 verses organizing the phonemes of Sanskrit. The page points the Kashmir text to a different article and says it needs more citations.",
    "licence": "CC BY-SA 4.0",
}
WIKI_KASH = {
    "name": "English Wikipedia, Shiva Sutras of Vasugupta",
    "url": "https://en.wikipedia.org/wiki/Shiva_Sutras_of_Vasugupta",
    "detail": "Short description: a collection of aphorisms from Kashmir Shaivism. This app did not find a clear 75-versus-77 sentence to quote.",
    "licence": "CC BY-SA 4.0",
}
GRETIL = {
    "name": "GRETIL Śivasūtra with vārttika",
    "url": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_zivasUtra-with-vArttika.htm",
    "detail": "The page distributes the e-text under CC BY-NC-SA 4.0. Non-commercial and share-alike terms apply to that e-text. No English translation is copied here.",
    "licence": "CC BY-NC-SA 4.0, confirmed on the page",
}

def rooms(st, diagrams_by_room):
    ac = " ".join(st["known"]["ac"])
    hal_n = len(st["known"]["hal"])
    al_n = len(st["known"]["al"])
    s113 = st["s113"]
    out = []

    def take(room, fallback):
        found = [item for item in diagrams_by_room if item["room"] == room]
        return found[0] if found else fallback

    common_tail = "Meaning field for every canon line in this app: meaning: not yet sourced from an open text. IAST from the Aṣṭādhyāyī file is script-converted, not yet human-checked."

    specs = []
    specs.append(dict(
        file="index.html", title="Sūtra Nexus",
        desc="A free offline study of Sanskrit sound and grammar, with the gaps labeled.",
        room="index",
        paras=[
            "Sūtra Nexus is a free study desk for three open data files: 3,983 Aṣṭādhyāyī lines, 14 Māheśvara lines, and 75 Kashmir Śiva Sūtras. It is a learning project by a lifelong student and AI enthusiast moving toward AI omni-channel agents.",
            "The start path has six steps. Progress marks stay in this browser. Nothing is uploaded.",
            common_tail,
            "A short plain-English line in this app is a learner's note (not a translation). It teaches how the app is organized. It is not a scholar's rendering of a sūtra.",
        ],
        example=("Read the number 1.1.1", [
            "The file stores the number 1.1.1 on the first row.",
            "The digits mean chapter 1, section 1, line 1. English Wikipedia's Aṣṭādhyāyī page, checked 2026-10-16, says eight chapters each subdivided into four sections.",
            "The Devanāgarī on that row is वृद्धिरादैच्. The file's IAST is vṛddhirādaic and is script-converted, not yet human-checked.",
            "The meaning is not yet sourced from an open text. This example stops there on purpose.",
        ]),
        quizzes=[
            ("How many Aṣṭādhyāyī rows are in the data file?", ["3,959", "3,983", "4,000", "75"], 1, "The file meta and the row list both say 3,983."),
            ("How many Māheśvara lines are in the data file?", ["10", "14", "75", "77"], 1, "data/maheshvara.json has 14 lines."),
            ("What does this app put in a meaning field today?", ["A fresh translation", "meaning: not yet sourced from an open text", "A verse from another scripture", "A guess labeled as Vasu"], 1, "No open translation passed the licence check, so no English meaning is shown."),
            ("Where do progress marks live?", ["A remote account", "This browser only", "An email", "A vendor cloud"], 1, "Quizzes, cards, and the path use local storage. There is no account."),
            ("What is a learner's note?", ["A scholarly translation", "A labeled teaching line, not a translation", "A sūtra from the file", "A quoted verse"], 1, "The label is learner's note (not a translation)."),
        ],
        sources=[DATA_CREDIT, WIKI_ASHTA],
        extra_html='''<section class="path" id="path" data-path><h2>Start here</h2><ol class="steps">
<li>Foundations: script and what a sound chart still lacks. <a href="foundations.html">Open</a></li>
<li>Māheśvara lines and a pratyāhāra you compute. <a href="maheshvara.html">Open</a></li>
<li>How to read a number, then anuvṛtti. <a href="anuvrtti.html">Open</a></li>
<li>The shape of the Aṣṭādhyāyī file. <a href="ashtadhyayi.html">Open</a></li>
<li>Sandhi as an idea, without a fake join. <a href="sandhi.html">Open</a></li>
<li>Practice, then listen to a scripted read. <a href="play.html">Open</a></li>
</ol>
<p data-path-meter>0 of 6 steps marked on this device.</p>
<button type="button" data-step="1" data-label="Foundations">Mark done: Foundations</button>
<button type="button" data-step="2" data-label="Māheśvara">Mark done: Māheśvara</button>
<button type="button" data-step="3" data-label="Anuvṛtti">Mark done: Anuvṛtti</button>
<button type="button" data-step="4" data-label="Aṣṭādhyāyī">Mark done: Aṣṭādhyāyī</button>
<button type="button" data-step="5" data-label="Sandhi">Mark done: Sandhi</button>
<button type="button" data-step="6" data-label="Practice">Mark done: Practice</button>
</section>''',
        glossary=[("sūtra", "A short rule line. This app shows the source text and does not translate it."), ("IAST", "A Latin transliteration scheme. Here it is script-converted unless a row says otherwise.")],
        deps="None. This is the front door.",
        history="Dates are on the history page, and only as the opened article states them.",
        roadmap="Next: an open-licensed meaning, then a human check of the IAST.",
        world="People compare rule lists with programming and with linguistics. Those comparisons in this app are learner's bridges, not claims about Pāṇini's intent. Confirm before relying.",
        sisters="Foundations, Māheśvara, and the downloads page.",
        bridges="Learner's note (not a translation): a pratyāhāra names a set of sounds, which is why programmers sometimes think of a character class. That is an analogy made here, not a quotation.",
        hooks="A checked translation, and a reviewer for the IAST.",
    ))

    specs.append(dict(
        file="foundations.html", title="Foundations",
        desc="Devanāgarī, IAST, and the phonetic chart this app will not invent.",
        room="foundations",
        paras=[
            "The rows in this app are written in Devanāgarī. English Wikipedia's Devanagari page, checked 2026-10-16, describes it in the short description as an Indic script used in the Indian subcontinent.",
            "IAST is the Latin scheme used beside those rows. English Wikipedia's IAST page, checked the same day, calls it a transliteration scheme for Indic scripts. In the Aṣṭādhyāyī file the IAST was produced by a script and has not been checked by a person. The label is: script-converted, not yet human-checked.",
            "English Wikipedia's Shiksha page, checked 2026-10-16, calls Śikṣā a Vedic-era study of phonetics and phonology, one of six Vedangas. Sthāna (place) and prayatna (effort) are the classroom names for phonetic charts. This app does not draw those charts, because no open phonetic edition was opened and recorded. Confirm before relying on any place-of-articulation table you bring from elsewhere.",
            "What you can trust here is the 14-line sound list in the data file, printed as the file records it.",
        ],
        example=("Tell a script sign from a meaning", [
            "Look at line 1 of the Māheśvara file: अइउण्.",
            "The sounds array on that line is a, i, u. The marker is ण्, stored as ṇ.",
            "That is a parse of the file, not a translation and not a statement about where in the mouth the sounds are made.",
            "If a chart of tongue positions is added later, it needs its own opened source.",
        ]),
        quizzes=[
            ("What does this app claim about tongue position?", ["A full sthāna chart", "It does not chart it yet", "Every sound is velar", "The 14 lines are the five places"], 1, "No open phonetic edition was confirmed, so there is no place chart."),
            ("How is Aṣṭādhyāyī IAST labeled?", ["Human-checked", "script-converted, not yet human-checked", "A published IAST edition", "Audio"], 1, "The file meta says the IAST was machine-converted."),
            ("What is Śikṣā, per the Wikipedia short description checked 2026-10-16?", ["A verse commentary", "A Vedic-era study of phonetics and phonology, one of six Vedangas", "The Kashmir sūtras", "A programming language"], 1, "That wording is the page's short description, not a full article paraphrase."),
            ("Which script are the source lines in?", ["Roman only", "Devanāgarī", "Brahmi images", "A private cipher"], 1, "The devanagari field holds Devanāgarī."),
            ("What should you do with an unsourced phonetic claim?", ["Treat it as Pāṇini", "Confirm before relying", "Email the author", "Add it to the file silently"], 1, "The contact path is the form, and the gap stays labeled."),
        ],
        sources=[WIKI_DEVA, WIKI_IAST, WIKI_SHIKSHA, DATA_CREDIT],
        glossary=[("Devanāgarī", "The script of the source lines in these files."), ("sthāna", "A traditional name for place of articulation. Not charted here. Confirm before relying."), ("prayatna", "A traditional name for articulatory effort. Not charted here. Confirm before relying.")],
        deps="Start here.",
        history="The Śikṣā page calls the study Vedic-era. This app does not assign a year.",
        roadmap="An opened phonetic source, then a chart with that citation.",
        world="Speech technology uses place and manner features. Mapping those features onto this tradition needs a cited source. Confirm before relying.",
        sisters="Māheśvara and sandhi.",
        bridges="Learner's note (not a translation): a sound list is the inventory a later rule can name. The inventory in this app is the 14-line file.",
        hooks="A subset font is already shipped so the script does not depend on a network.",
    ))

    specs.append(dict(
        file="maheshvara.html", title="Māheśvara lines and pratyāhāra",
        desc="Fourteen lines, markers, and sets you can recompute.",
        room="maheshvara",
        paras=[
            "The file data/maheshvara.json holds 14 lines. English Wikipedia's Shiva Sutras article, checked 2026-10-16, uses the short description \"14 verses organizing the phonemes of Sanskrit\" and tells readers that the Kashmir text is a different article. That Wikipedia page also says it needs more citations, so this app treats the file, not the article, as the list.",
            "Each line has sounds and a final marker. A pratyāhāra in this app is a computed set: start at a sound, walk forward, and stop at a chosen marker line. The marker itself is not kept. This is an operation on the file, not a translation.",
            f"The self-test checks ac, ik, yaṇ, śar, ak, ec, hal ({hal_n} sounds), and al ({al_n} sounds).",
            "The IAST strings in that file are script-converted, not yet human-checked. The Devanāgarī and the sounds arrays are what the builder uses.",
        ],
        example=(f"Build ac", [
            "Start at a on line 1.",
            "Walk forward through lines 1, 2, 3, and 4.",
            "Stop at the marker on line 4. Drop every marker.",
            f"The sounds are: {ac}.",
            "The same function returns 33 sounds for hal and 42 for al. You can recompute both in the builder below.",
        ]),
        quizzes=[
            ("How many sounds does the self-test expect for hal?", ["14", "33", "42", "75"], 1, "hal is h on line 5 through the marker on line 14, and the length is 33."),
            ("How many sounds does al contain in the self-test?", ["14", "33", "42", "8"], 2, "al starts at a on line 1 and runs through line 14. Length 42."),
            ("Is the marker kept inside the set?", ["Yes", "No", "Only on line 14", "Only for vowels"], 1, "The builder drops the it marker."),
            ("What does ac start with?", ["h", "a on line 1", "ś", "k"], 1, "ac starts at a on line 1 and ends at the marker on line 4."),
            ("Which text is this page not?", ["The 14-line file", "The Kashmir Śiva Sūtras", "A computed set", "A self-test"], 1, "The Kashmir file is a different work and a different page."),
        ],
        sources=[DATA_CREDIT, WIKI_MAHA],
        glossary=[("pratyāhāra", "In this app, a set computed from a start sound and a marker line."), ("it marker", "The final marker on a line. The builder does not keep it in the set."), ("ac", f"The computed set: {ac}.")],
        deps="Foundations, so the script and the IAST label are clear.",
        history="The Wikipedia phoneme article's own page asks for more citations. Confirm before relying on stories about the list's origin.",
        roadmap="Show every pratyāhāra the function can build, still as computation.",
        world="Learner's note (not a translation): naming a set with a short code is why this list gets compared to character classes in programming. The comparison is made in this app.",
        sisters="Sandhi, foundations, play.",
        bridges="A programmer can read ac as a named set. That reading is a bridge, not a claim that the tradition described software.",
        hooks="A human check of the line IAST.",
        extra_html=builder_html(st),
    ))

    specs.append(dict(
        file="sandhi.html", title="Sandhi basics",
        desc="Sound-joining as an idea, without an invented example join.",
        room="sandhi",
        paras=[
            "English Wikipedia's Sandhi page, checked 2026-10-16, uses the short description \"type of sound change at morpheme or syllable boundaries.\" This app uses that as the plain name of the topic.",
            "A sandhi rule in the Aṣṭādhyāyī tradition is often taught as naming a set of sounds with a pratyāhāra, then stating what happens when those sounds meet. This app can show the set, because the set is computed from the 14 lines. It cannot show the operation of a particular rule, because the English of that rule is not yet sourced from an open text.",
            "There is no sample join such as a textbook word pair on this page. Adding one would be writing a result this project has not cited.",
            "Learner's note (not a translation): when you are ready to study a real rule, open a sourced edition, find the pratyāhāra it names, and check that set in the builder. Confirm before relying.",
        ],
        example=("Use the set, stop before the join", [
            "Suppose a classroom says a rule applies inside ac.",
            f"Compute ac. The sounds are {ac}.",
            "Stop. The app does not apply a change to an example word.",
            "The meaning of the rule that would name ac is not yet sourced from an open text.",
        ]),
        quizzes=[
            ("What does the Sandhi Wikipedia short description say?", ["A chapter count", "A type of sound change at morpheme or syllable boundaries", "75 aphorisms", "A font"], 1, "That is the short description checked 2026-10-16."),
            ("Why is there no example word join?", ["The builder is broken", "A join would be an uncitable result", "Sandhi is not a sound change", "The file forbids vowels"], 1, "No open rule text was confirmed, so no join is demonstrated."),
            ("What can you compute today?", ["A finished sandhi word", "The sounds inside a pratyāhāra", "An English meaning", "A recited audio file"], 1, "The builder computes sets from the 14 lines."),
            ("What label covers a plain-English hint on this page?", ["Translation by Vasu", "Learner's note (not a translation)", "A sūtra", "A GRETIL sentence"], 1, "Hints stay labeled."),
            ("Where do you go to recompute ac?", ["The history page", "The Māheśvara builder", "The zip file only", "A video"], 1, "The builder lives on the Māheśvara page and the play page."),
        ],
        sources=[WIKI_SANDHI, DATA_CREDIT],
        glossary=[("sandhi", "Sound change where pieces meet, per the Wikipedia short description cited here."), ("set", "The sounds a pratyāhāra names in this app's computation.")],
        deps="Māheśvara lines, because the sets come from them.",
        history="This page does not date the rules.",
        roadmap="Quote one open-licensed sandhi rule, then show only what that quotation says.",
        world="Tokenizer and phonology textbooks also talk about boundary changes. A mapping needs its own citation. Confirm before relying.",
        sisters="Māheśvara and anuvṛtti.",
        bridges="Learner's note (not a translation): a boundary rule is easier to see once the set has a name. The name here is the pratyāhāra.",
        hooks="One cited rule, with the edition's page.",
    ))

    specs.append(dict(
        file="ashtadhyayi.html", title="Aṣṭādhyāyī structure",
        desc="Eight chapters, the type letters in the file, and a lazy line search.",
        room="ashtadhyayi",
        paras=[
            "The file holds 3,983 rows. English Wikipedia's Aṣṭādhyāyī page, checked 2026-10-16, also says 3,983 sūtras in eight chapters, each subdivided into four pādas.",
            f"Chapter counts in this file are {', '.join(str(n) for n in st['adhyaya'])}. They sum to 3,983.",
            f"The file's type letters are {', '.join(k+' '+str(v) for k,v in st['types'].items())}. The file meta glosses S as saṃjñā, P as paribhāṣā, and V as vidhi. It does not gloss AT or AD. This app does not expand those two letters. Confirm before relying.",
            "Wikipedia's list of ancillary types, on the page checked the same day, names paribhāṣā as metarules, adhikāra as headings, atideśa as extension rules, niyama as restrictive rules, and pratiṣedha and niṣedha as negation rules, beside vidhi as the operational rules. This app does not assert that the file's AT or AD letters are those words.",
            "Every row's meaning is not yet sourced from an open text.",
        ],
        example=("Look up 1.1.1 without translating it", [
            "Type 1.1.1 in the browser below. The index loads when you type.",
            "You should see the Devanāgarī वृद्धिरादैच् and the IAST vṛddhirādaic.",
            "Read the label under it: the meaning is not sourced, and the IAST is not human-checked.",
            "The type letter on that row in the file is S. The file meta calls S saṃjñā.",
        ]),
        quizzes=[
            ("How many chapters does the Wikipedia page name?", ["4", "8", "14", "75"], 1, "Eight chapters, each with four pādas, on the page checked 2026-10-16."),
            ("What does the file meta call type letter V?", ["vidhi", "a vowel", "a verse", "unknown and unstated"], 0, "The meta says V=vidhi. It does not define AT or AD."),
            ("Does this app equate AT with atideśa?", ["Yes", "No", "Only in the chart", "Only in downloads"], 1, "The chart prints the letter and refuses the expansion."),
            ("How many rows have type V?", ["23", "200", "3629", "3983"], 2, "Counted from the file: V is 3629."),
            ("What appears under a looked-up line?", ["A new translation", "meaning: not yet sourced from an open text", "A Gītā verse", "An audio recitation"], 1, "No open translation was confirmed."),
        ],
        sources=[DATA_CREDIT, WIKI_ASHTA],
        glossary=[("adhyāya", "A chapter. The file numbers them 1 through 8."), ("pāda", "A section of a chapter. Wikipedia's page says four per chapter."), ("saṃjñā", "The file meta's gloss for type letter S. Not a translation of a sūtra."), ("vidhi", "The file meta's gloss for type letter V, and Wikipedia's name for an operational rule.")],
        deps="The start page, and anuvṛtti if you want to read a carried word.",
        history="See the history page for the dating dispute.",
        roadmap="Meanings only after an open text is checked into licences.json as confirmed.",
        world="Computational linguistics papers discuss this rule list. This app does not summarize a paper it has not opened. Confirm before relying.",
        sisters="Anuvṛtti, dhātu, charts.",
        bridges="Learner's note (not a translation): a type letter is metadata about a row, similar to a tag on a record. The tags here are the file's letters.",
        hooks="A per-chapter browser that still lazy-loads.",
        extra_html='''<section class="card" id="browser" data-sutra-browser><h2>Look up a line</h2>
<label for="sutra-q">Number, Devanāgarī, or IAST</label>
<input id="sutra-q" class="q-input" type="search" placeholder="1.1.1">
<div data-sutra-out><p>The index loads after you type, so the first paint stays light.</p></div></section>''',
    ))

    specs.append(dict(
        file="anuvrtti.html", title="Anuvṛtti",
        desc="Carried words as the file records them on 1.1.3.",
        room="anuvrtti",
        paras=[
            f"{st['anuvritti']} of the 3,983 rows have a non-empty anuvritti array. The other rows have an empty array. That is a count, not a theory.",
            "Learner's note (not a translation): classrooms use anuvṛtti for words that carry forward from an earlier line so the later line can stay short. This app shows the strings the file stored. It does not decide whether a string was carried correctly.",
            f"On 1.1.3 the Devanāgarī is {s113['devanagari']}. The file's IAST is {s113['iast']} and is script-converted, not yet human-checked. The anuvritti field lists: {', '.join(s113['anuvritti'])}.",
            "The padaccheda field on that row is also stored in the file. It is shown as file data, not as this project's analysis. Meaning: not yet sourced from an open text.",
        ],
        example=("Read 1.1.3 as a file row", [
            f"Number: {s113['num']}. Type letter: {s113['type']}. The meta calls P paribhāṣā.",
            f"Devanāgarī: {s113['devanagari']}.",
            f"anuvritti array: {', '.join(s113['anuvritti'])}.",
            f"padaccheda from the file: {s113['padaccheda']}.",
            "Stop before an English rendering. There isn't a confirmed open one in this project.",
        ]),
        quizzes=[
            ("How many rows have a non-empty anuvritti array?", ["0", "14", str(st["anuvritti"]), "3,983"], 2, "Counted from the file while building this site."),
            ("What does 1.1.3's anuvritti field contain?", ["Nothing", "वृद्धिः and गुणः", "A translation", "The Kashmir text"], 1, "Those two strings are the array in the file."),
            ("Is the padaccheda this project's parsing?", ["Yes", "No, it is a field in the source file", "It is audio", "It is a meaning"], 1, "The field ships with the data file."),
            ("What is the learner's note allowed to do?", ["Replace the sūtra", "Explain the classroom word anuvṛtti and stay labeled", "Invent a join", "Quote an unsourced verse"], 1, "The note is labeled and does not translate 1.1.3."),
            ("What is the type letter on 1.1.3?", ["V", "P", "S", "AT"], 1, "The row's type is P."),
        ],
        sources=[DATA_CREDIT, WIKI_ASHTA],
        glossary=[("anuvṛtti", "The classroom name for words understood from earlier lines. The file field is anuvritti."), ("padaccheda", "The file's word-split field. Not re-analyzed here.")],
        deps="Aṣṭādhyāyī structure, so the number 1.1.3 is meaningful.",
        history="No date is added on this page.",
        roadmap="Show a chain of carried strings across several rows, still without translating them.",
        world="Compression in a rule list is interesting to programming-language people. Calling anuvṛtti a macro is a learner's bridge. Confirm before relying if you say it in an interview as history.",
        sisters="Aṣṭādhyāyī and dhātu.",
        bridges="Learner's note (not a translation): a later line can be short because an earlier line still applies. The evidence in this app is the array on the row.",
        hooks="A view that highlights the carried strings in Devanāgarī only.",
    ))

    specs.append(dict(
        file="dhatu.html", title="Dhātu and pada basics",
        desc="Names for verb roots and word classes, and the list this app does not have.",
        room="dhatu",
        paras=[
            "Learner's note (not a translation): dhātu is the classroom name for a verb root, and a pada is a finished word. People also meet tiṅ (verb endings) and sup (nominal endings) as names of ending sets. This page does not quote a sūtra that defines them, because that would be a translation.",
            "The Aṣṭādhyāyī data file has no dhātu inventory. The repository README of ashtadhyayi-com/data, opened 2026-10-16, mentions dhātu forms as data the website edits, but those forms are not in the three JSON files shipped here.",
            "So this room teaches the gap. You can learn the words as labels. You cannot look up a root's forms in this app yet.",
            "Confirm before relying on any root list you remember from a class until it is tied to an opened edition.",
        ],
        example=("Notice the missing list", [
            "Search this site's downloads for a dhātu table. There isn't one.",
            "The three JSON files are the sūtra rows, the 14 lines, and the 75 Kashmir lines.",
            "A worksheet in the downloads asks you to record a root only when you have a source in hand.",
            "Leave the meaning column as not yet sourced.",
        ]),
        quizzes=[
            ("Does this app ship a dhātu inventory?", ["Yes, 2,000 roots", "No", "Only in the zip as a translation", "As audio"], 1, "The three JSON files do not include a root list."),
            ("What is a learner's note allowed to say a dhātu is?", ["A quoted sūtra", "The classroom name for a verb root, labeled as not a translation", "A Kashmir aphorism", "A chapter"], 1, "The sentence is labeled."),
            ("Where would a future root list have to come from?", ["Memory", "An opened, licensed source recorded in licences.json", "A guess", "A video narration"], 1, "No words are added without a confirmed licence."),
            ("What endings are named, without a quotation?", ["tiṅ and sup, as classroom names", "Only hal", "Only ac", "SMTP"], 0, "They are named as classroom labels, not as translated sūtras."),
            ("Which file would you open for the 14 lines?", ["shiva_sutras_kashmir.json", "maheshvara.json", "A PDF of a commentary", "The font"], 1, "The 14 lines are maheshvara.json."),
        ],
        sources=[DATA_CREDIT],
        glossary=[("dhātu", "Classroom name for a verb root. No inventory in this app. Confirm before relying."), ("pada", "Classroom name for a finished word."), ("tiṅ", "Classroom name for a set of verb endings. Not quoted from a sūtra here."), ("sup", "Classroom name for a set of nominal endings. Not quoted from a sūtra here.")],
        deps="Aṣṭādhyāyī structure.",
        history="No century is assigned to the root lists.",
        roadmap="If an open dhātu file is confirmed, add it as its own dataset with the licence recorded.",
        world="Morphological analyzers store roots and endings. Pointing at a specific analyzer needs a citation this page does not have. Confirm before relying.",
        sisters="Anuvṛtti and play.",
        bridges="Learner's note (not a translation): a root plus an ending is a familiar shape in computing. The shape is an analogy until a text is cited.",
        hooks="A worksheet that refuses a blank source line.",
    ))

    specs.append(dict(
        file="shiva.html", title="Śiva Sūtras, Kashmir text",
        desc="Seventy-five lines from the GRETIL e-text, with no English added.",
        room="shiva",
        paras=[
            "This page is not the 14 Māheśvara lines. English Wikipedia's Shiva Sutras of Vasugupta page, checked 2026-10-16, calls that work a collection of aphorisms from Kashmir Shaivism in its short description.",
            "The file has 75 rows. Its meta note says this recension counts 20+10+45=75, and that the common Kṣemarāja recension counts 22+10+45, then the note trails off. Which lines differ is unknown beyond that note. Confirm before relying.",
            "The file says its IAST comes from the GRETIL source and that the Devanāgarī was machine-converted and is unverified. The GRETIL page, opened 2026-10-16, distributes the e-text under CC BY-NC-SA 4.0. Those non-commercial and share-alike terms stay with the e-text. Nothing here is sold.",
            "No English meaning is included. A translation was not confirmed as open.",
        ],
        example=("Read row 1.1 without translating it", [
            "The file's first IAST is caitanyam ātmā.",
            "The file's Devanāgarī is चैतन्यम् आत्मा, marked machine-converted from the IAST.",
            "Do not add an English sentence and call it the sūtra.",
            "If you cite the e-text, keep the CC BY-NC-SA credit and the GRETIL URL.",
        ]),
        quizzes=[
            ("How many rows are in the Kashmir file?", ["14", "75", "77", "3,983"], 1, "The file count is 75."),
            ("Does this app list the lines that differ from the other recension?", ["Yes, all of them", "No. The meta note does not list them", "Only in the zip", "Only in audio"], 1, "The difference remains unknown beyond the note."),
            ("What licence does the opened GRETIL page state?", ["MIT only", "CC BY-NC-SA 4.0", "Public domain with no statement", "All rights reserved and no use"], 1, "The page says CC BY-NC-SA 4.0."),
            ("Is an English meaning shown?", ["Yes, from memory", "No", "Only the first ten", "A paraphrase of a verse from another book"], 1, "No open translation was confirmed."),
            ("Which Wikipedia short description fits this page?", ["14 verses organizing phonemes", "A collection of aphorisms from Kashmir Shaivism", "A font licence", "A sandhi definition"], 1, "That is the Vasugupta article's short description. The 14 verses are the other article."),
        ],
        sources=[GRETIL, WIKI_KASH, DATA_CREDIT],
        glossary=[("unmeṣa", "The file groups lines into sections numbered on each row. This app does not translate the word."), ("recension", "A version of a text. This file describes its own count and trails off on the other.")],
        deps="Know that the 14-line list is a different page.",
        history="This app does not assign the Kashmir text a century from a category label.",
        roadmap="If an open translation is confirmed, add it with the translator, year, and URL.",
        world="Do not mix this text into a grammar exercise. They are different works.",
        sisters="Māheśvara, for the contrast, and resources.",
        bridges="The only bridge is bibliographic: two works share a Sanskrit name in English articles and are easy to confuse. This app keeps them on separate pages.",
        hooks="A side-by-side that still refuses to invent the missing lines.",
    ))

    specs.append(dict(
        file="history.html", title="History and timeline",
        desc="Only the dating sentences that were on the page opened 2026-10-16.",
        room="history",
        paras=[
            "English Wikipedia's Pāṇini article, checked 2026-10-16, treats the dates as disputed. It reports that George Cardona (1997) says the available evidence strongly supports a date no earlier than 400 BCE, and that earlier dates rely on interpretations that are not probative.",
            "The same article reports that Oskar von Hinüber (1989) and Harry Falk (1993) place Pāṇini in the mid-4th century BCE. This app does not choose between those reports.",
            "The article mentions Kātyāyana and Patañjali inside that dating discussion. This page does not assign either of them a century, because that sentence was not the one copied into the notes.",
            "All of these years are approximate scholarly estimates as reported by that encyclopedia page. Confirm before relying. Nothing here is a primary source.",
        ],
        example=("Say a date without overclaiming", [
            "Open the history diagram. It names Cardona, then Hinüber and Falk.",
            "Say: Wikipedia's Pāṇini article, checked 2026-10-16, reports both.",
            "Do not say the true year is 350, or 500, or any single year.",
            "If you need a date for a citation, go back to the article and to the books it names.",
        ]),
        quizzes=[
            ("What does the page report from Cardona 1997?", ["A birth certificate", "Evidence supports a date no earlier than 400 BCE", "The year 1200 CE", "That the text is modern"], 1, "That is the sentence visible on the article."),
            ("Who does the article say place Pāṇini in the mid-4th century BCE?", ["This app's author", "Hinüber (1989) and Falk (1993)", "A font vendor", "GRETIL"], 1, "Those names are on the article."),
            ("Does this app pick one year?", ["Yes, 400 BCE exactly", "No", "Yes, 350 BCE as fact", "Yes, the 9th century"], 1, "The dispute is left standing."),
            ("Are Kātyāyana and Patañjali given centuries here?", ["Yes", "No", "Only Patañjali", "Only in the zip"], 1, "Their centuries were not copied into these notes."),
            ("What should a reader do before quoting a year?", ["Trust the diagram alone", "Confirm before relying, and open the article", "Email a guess", "Use a verse from another book"], 1, "The diagram is a reminder of the article, not a primary source."),
        ],
        sources=[WIKI_PANINI],
        glossary=[("approximate", "The article's dates are scholarly estimates. This app marks them that way.")],
        deps="None, but the Aṣṭādhyāyī page explains the work being dated.",
        history="This page is the history room.",
        roadmap="Add a later grammarian only when a page that states the date has been opened and quoted narrowly.",
        world="Histories of linguistics mention this tradition. A specific modern book needs its own citation. Confirm before relying.",
        sisters="Aṣṭādhyāyī and credits.",
        bridges="The bridge to computing history is not claimed here. The metalanguage idea is discussed on the Wikipedia page; this room does not expand it beyond the dating sentences.",
        hooks="A timeline that stays empty where a date was not opened.",
    ))

    # Attach visuals and standard sections while emitting.
    pages = []
    for spec in specs:
        visual = take(spec["room"], diagrams_by_room[0])
        quiz_html = "".join(quiz(f'{spec["file"]}-q{i}', q, c, a, w) for i, (q, c, a, w) in enumerate(spec["quizzes"], 1))
        body = []
        body.append(f'<h1 class="hero-title">{b.E(spec["title"])}</h1><p class="lede">{b.E(spec["desc"])}</p>')
        body.append(learn_block(spec["paras"]))
        body.append(f'<section class="card"><h2>Foundations, dependencies, history, roadmap</h2><p><b>Dependencies.</b> {b.E(spec["deps"])}</p><p><b>History.</b> {b.E(spec["history"])}</p><p><b>Roadmap.</b> {b.E(spec["roadmap"])}</p><p><b>Where the idea shows up.</b> {b.E(spec["world"])}</p></section>')
        body.append(visual_block(visual))
        body.append(example_block(spec["example"][0], spec["example"][1]))
        if spec.get("extra_html"):
            body.append(spec["extra_html"])
        body.append(f'<section class="quiz" id="quiz"><h2>Quiz</h2>{quiz_html}</section>')
        body.append(sources_block(spec["sources"]))
        body.append(eco_block(spec["glossary"], spec["sisters"], spec["bridges"], spec["hooks"]))
        pages.append({**spec, "html": "\n".join(body), "visual": visual})
    return pages

def builder_html(st):
    options = []
    for line in st["maha"]["sutras"]:
        for sound in line["sounds"]:
            options.append(f'<option value="{b.E(sound)}|{line["n"]}">{b.E(sound)} on line {line["n"]}</option>')
    markers = "".join(f'<option value="{n}">{n}</option>' for n in range(1, 15))
    lines_json = json.dumps([{"n": row["n"], "sounds": row["sounds"], "marker": row["marker"]} for row in st["maha"]["sutras"]], ensure_ascii=False)
    return f'''<section class="card" data-pratyahara><h2>Builder</h2>
<label>Start <select data-start>{''.join(options)}</select></label>
<label>Marker line <select data-marker>{markers}</select></label>
<p data-pr-out></p>
<p class="note">The set is computed in the browser from the 14 lines. It is not a translation.</p>
</section>
<script>window.SUTRA_LINES={lines_json};</script>'''

def shell_page(spec):
    return b.page_shell(spec["file"], spec["title"] + " · Sūtra Nexus", spec["desc"], spec["html"])

def css_standalone(embed_font=False):
    css = open("assets/css/sutra.css", encoding="utf-8").read()
    font_url = 'url("../fonts/NotoSansDevanagari-Regular.woff2")'
    if embed_font:
        raw = open("assets/fonts/NotoSansDevanagari-Regular.woff2", "rb").read()
        data = "url(\"data:font/woff2;base64," + base64.b64encode(raw).decode("ascii") + "\")"
        css = css.replace(font_url, data)
    else:
        css = css.replace(font_url + ' format("woff2")', 'local("Noto Sans Devanagari")')
    return css

def standalone_html(title, inner):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="bloom">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{b.E(title)}</title>
<style>
{css_standalone(False)}
</style>
</head>
<body>
<main class="main-wrap">
{inner}
</main>
{b.footer_html_fixed()}
</body>
</html>
'''

def write_diagrams(items):
    os.makedirs("downloads/diagrams", exist_ok=True)
    for item in items:
        svg_path = f'downloads/diagrams/{item["id"]}.svg'
        b.write(svg_path, item["svg"])
        png_path = f'downloads/diagrams/{item["id"]}.png'
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=960, output_height=820)
        svg = item["svg"].replace('<?xml version="1.0" encoding="UTF-8"?>', "")
        inner = f'<h1>{b.E(item["title"])}</h1>{svg}<p>{b.E(item["source"])}</p>'
        b.write(f'downloads/diagrams/{item["id"]}.html', standalone_html(item["title"], inner))

pdfmetrics.registerFont(TTFont("Deja", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Deva", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"))

def _is_deva(ch):
    code = ord(ch)
    return 0x0900 <= code <= 0x097F or code in (0x200C, 0x200D)

def _runs(text):
    runs, buf, kind = [], "", None
    for ch in text:
        if ch == "🐒":
            if buf:
                runs.append((kind, buf))
                buf = ""
            runs.append(("monkey", "🐒"))
            kind = None
            continue
        next_kind = "Deva" if _is_deva(ch) else "Deja"
        if kind and next_kind != kind and buf:
            runs.append((kind, buf))
            buf = ""
        kind = next_kind
        buf += ch
    if buf:
        runs.append((kind, buf))
    return runs

def _draw_mixed(c, text, x, y, size, bold=False):
    cursor = x
    for kind, chunk in _runs(text):
        if kind == "monkey":
            c.setFillColorRGB(0.45, 0.25, 0.1)
            c.circle(cursor + 6, y + 3, 5, stroke=0, fill=1)
            c.setFillColorRGB(0.4, 0.9, 0.95)
            c.circle(cursor + 4, y + 4, 1.4, stroke=0, fill=1)
            c.circle(cursor + 8, y + 4, 1.4, stroke=0, fill=1)
            c.setFillColorRGB(0, 0, 0)
            cursor += 16
            continue
        font = "Deva" if kind == "Deva" else ("DejaBold" if bold else "Deja")
        c.setFont(font, size)
        c.drawString(cursor, y, chunk)
        cursor += pdfmetrics.stringWidth(chunk, font, size)
    return cursor

def pdf_text(path, title, paragraphs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = pdfcanvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 48

    def draw_para(text, size=11, bold=False):
        nonlocal y
        words = text.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            width_so_far = 0
            for kind, chunk in _runs(trial):
                if kind == "monkey":
                    width_so_far += 16
                else:
                    font = "Deva" if kind == "Deva" else ("DejaBold" if bold else "Deja")
                    width_so_far += pdfmetrics.stringWidth(chunk, font, size)
            if width_so_far > width - 80 and line:
                if y < 64:
                    c.showPage()
                    y = height - 48
                _draw_mixed(c, line, 40, y, size, bold=bold)
                y -= size + 4
                line = word
            else:
                line = trial
        if line:
            if y < 64:
                c.showPage()
                y = height - 48
            _draw_mixed(c, line, 40, y, size, bold=bold)
            y -= size + 4
        y -= 8

    draw_para(title, 16, bold=True)
    for para in paragraphs:
        draw_para(para)
    draw_para("CypherMonkey Labs")
    draw_para("© 2026 CypherMonkeyLabs 🐒")
    draw_para(DISCLAIMER)
    draw_para("Contact form: " + CONTACT)
    c.save()

def docx_text(path, title, paragraphs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = Document()
    doc.add_heading(title, 1)
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.add_paragraph("CypherMonkey Labs")
    doc.add_paragraph("© 2026 CypherMonkeyLabs 🐒")
    p = doc.add_paragraph(DISCLAIMER)
    p.runs[0].font.size = Pt(11)
    doc.add_paragraph("Contact form: " + CONTACT)
    section = doc.sections[0]
    section.footer.paragraphs[0].text = DISCLAIMER + " Contact form: " + CONTACT
    doc.save(path)

def write_pptx(path, slides):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for title, body in slides:
        slide = prs.slides.add_slide(blank)
        box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(1))
        box.text_frame.text = title
        box.text_frame.paragraphs[0].font.size = PptPt(28)
        body_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(12.3), Inches(4.2))
        frame = body_box.text_frame
        frame.word_wrap = True
        frame.text = body
        foot = slide.shapes.add_textbox(Inches(0.4), Inches(6.2), Inches(12.5), Inches(1.1))
        foot.text_frame.word_wrap = True
        foot.text_frame.text = "© 2026 CypherMonkeyLabs 🐒  " + DISCLAIMER + " Contact form: " + CONTACT
        foot.text_frame.paragraphs[0].font.size = PptPt(10)
    prs.save(path)

def glb_bytes(positions, colors, indices):
    pos = b"".join(struct.pack("<fff", *p) for p in positions)
    col = b"".join(struct.pack("<fff", *c) for c in colors)
    idx = b"".join(struct.pack("<H", i) for i in indices)
    blob = pos + col + idx
    while len(blob) % 4:
        blob += b"\x00"
    def accessor(offset, count, typ, ctype, mins=None, maxs=None):
        item = {"bufferView": 0, "byteOffset": offset, "componentType": ctype, "count": count, "type": typ}
        if mins is not None:
            item["min"] = mins
            item["max"] = maxs
        return item
    mins = [min(p[i] for p in positions) for i in range(3)]
    maxs = [max(p[i] for p in positions) for i in range(3)]
    gltf = {
        "asset": {"version": "2.0", "generator": "Sutra Nexus v2", "copyright": DISCLAIMER},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "original"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "COLOR_0": 1}, "indices": 2}]}],
        "accessors": [
            accessor(0, len(positions), "VEC3", 5126, mins, maxs),
            accessor(len(pos), len(colors), "VEC3", 5126),
            accessor(len(pos) + len(col), len(indices), "SCALAR", 5123),
        ],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pos) + len(col) + len(idx)}],
        "buffers": [{"byteLength": len(blob)}],
        "extras": {"disclaimer": DISCLAIMER, "contact": CONTACT},
    }
    js = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    while len(js) % 4:
        js += b" "
    out = b"glTF" + struct.pack("<II", 2, 12 + 8 + len(js) + 8 + len(blob))
    out += struct.pack("<I", len(js)) + b"JSON" + js
    out += struct.pack("<I", len(blob)) + b"BIN\x00" + blob
    return out

def box(cx, cy, cz, sx, sy, sz, color):
    x, y, z = sx / 2, sy / 2, sz / 2
    corners = [(cx+dx*x, cy+dy*y, cz+dz*z) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    positions, colors, indices = [], [], []
    for a, b1, c, d in faces:
        start = len(positions)
        for i in (a, b1, c, d):
            positions.append(corners[i])
            colors.append(color)
        indices += [start, start+1, start+2, start, start+2, start+3]
    return positions, colors, indices

def write_models():
    os.makedirs("downloads/models", exist_ok=True)
    parts = [
        box(0, 0, 0, 1.4, 0.28, 1.4, (0.95, 0.75, 0.2)),
        box(0, 0.45, 0, 0.9, 0.18, 0.9, (0.45, 0.35, 0.9)),
        box(0, 0.9, 0, 0.45, 0.18, 0.45, (0.9, 0.4, 0.55)),
    ]
    # spokes as thin boxes
    for i in range(8):
        ang = i * math.pi / 4
        parts.append(box(math.cos(ang) * 0.7, 0.2, math.sin(ang) * 0.7, 0.12, 0.35, 0.12, (0.2, 0.8, 0.85)))
    pos, col, idx = [], [], []
    for p, c, i in parts:
        shift = len(pos)
        pos += p
        col += c
        idx += [n + shift for n in i]
    blob = glb_bytes(pos, col, idx)
    open("downloads/models/study-wheel.glb", "wb").write(blob)
    monkey_parts = [
        box(0, 0.2, 0, 0.7, 0.8, 0.45, (0.91, 0.56, 0.23)),
        box(0, 1.05, 0, 0.72, 0.62, 0.55, (0.91, 0.56, 0.23)),
        box(-0.48, 1.25, 0, 0.22, 0.22, 0.12, (0.7, 0.35, 0.1)),
        box(0.48, 1.25, 0, 0.22, 0.22, 0.12, (0.7, 0.35, 0.1)),
        box(-0.16, 1.05, 0.28, 0.18, 0.12, 0.06, (0.4, 0.9, 0.95)),
        box(0.16, 1.05, 0.28, 0.18, 0.12, 0.06, (0.4, 0.9, 0.95)),
    ]
    pos, col, idx = [], [], []
    for p, c, i in monkey_parts:
        shift = len(pos)
        pos += p
        col += c
        idx += [n + shift for n in i]
    open("downloads/models/guide-monkey.glb", "wb").write(glb_bytes(pos, col, idx))
    note = "Author: original geometry written for Sūtra Nexus v2.\nLicence: CC0-1.0 for these two model files.\nSource: this repository, not a scanned object.\n" + DISCLAIMER + "\nContact form: " + CONTACT + "\n"
    b.write("downloads/models/study-wheel-credits.txt", note + "Model: study-wheel.glb\nPoster: study-wheel.png is a 2D drawing of the same original wheel, not a photograph.\n")
    b.write("downloads/models/guide-monkey-credits.txt", note + "Model: guide-monkey.glb\nPoster: guide-monkey.png is a 2D drawing of the same original monkey with glasses, not a photograph and not a copied mascot.\n")
    wheel_svg = b.svg_doc("Study wheel poster", b.mind_body("Wheel", ["8", "Glow", "Study", "Original"]), "Original 2D poster for study-wheel.glb. CC0-1.0.", False)
    monkey_svg = b.svg_doc("Guide monkey poster", b.flow_body(["Ears", "Glasses", "Original", "No borrowed mascot"]), "Original 2D poster for guide-monkey.glb. CC0-1.0.", False)
    b.write("downloads/models/study-wheel.svg", wheel_svg)
    b.write("downloads/models/guide-monkey.svg", monkey_svg)
    cairosvg.svg2png(url="downloads/models/study-wheel.svg", write_to="downloads/models/study-wheel.png", output_width=960, output_height=820)
    cairosvg.svg2png(url="downloads/models/guide-monkey.svg", write_to="downloads/models/guide-monkey.png", output_width=960, output_height=820)

def write_sheets(st):
    os.makedirs("downloads/sheets", exist_ok=True)
    ac = " ".join(st["known"]["ac"])
    sheets = [
        ("pratyahara", "Pratyāhāra cheat sheet", [
            "A pratyāhāra in this app is computed from data/maheshvara.json.",
            f"ac = {ac}",
            f"hal has {len(st['known']['hal'])} sounds. al has {len(st['known']['al'])} sounds.",
            "Markers are dropped. IAST in the file is script-converted, not yet human-checked.",
            "This is not a translation.",
        ]),
        ("counts", "Counts and type letters", [
            "Aṣṭādhyāyī rows: 3,983. Māheśvara lines: 14. Kashmir Śiva Sūtras: 75.",
            "Type letters: " + ", ".join(f"{k} {v}" for k, v in st["types"].items()),
            "The file meta glosses S as saṃjñā, P as paribhāṣā, V as vidhi.",
            "AT and AD are not expanded. Confirm before relying.",
            "Chapter counts: " + ", ".join(str(n) for n in st["adhyaya"]),
        ]),
        ("read-a-number", "How to read a sūtra number", [
            "1.1.1 means chapter 1, section 1, line 1 in this file.",
            "English Wikipedia's Aṣṭādhyāyī page, checked 2026-10-16, says eight chapters, four sections each, 3,983 sūtras.",
            "The first row's Devanāgarī is in the data file. Its meaning is not yet sourced from an open text.",
            "IAST is script-converted, not yet human-checked.",
        ]),
        ("kashmir-notes", "Kashmir file notes", [
            "75 rows. Meta: 20+10+45=75. The other recension's note trails off at 22+10+45.",
            "Which lines differ is unknown. Confirm before relying.",
            "GRETIL page checked 2026-10-16 states CC BY-NC-SA 4.0 for the e-text.",
            "No English meaning is included.",
        ]),
    ]
    for slug, title, paras in sheets:
        inner = f'<h1>{b.E(title)}</h1>' + "".join(f"<p>{b.E(p)}</p>" for p in paras)
        b.write(f"downloads/sheets/{slug}.html", standalone_html(title, inner))
        pdf_text(f"downloads/sheets/{slug}.pdf", title, paras)
        svg = b.svg_doc(title, b.flow_body(paras[0][:40] for paras in [paras] for _ in [0]) if False else b.flow_body([p[:40] for p in paras[:4]]), "Cheat sheet poster. Full text is in the HTML and PDF.", False)
        # fix the botched expression by writing a clean svg
        svg = b.svg_doc(title, b.flow_body([p[:42] for p in paras[:4]]), "Poster for the cheat sheet. The HTML and PDF carry the full wording and the disclaimer.", False)
        b.write(f"downloads/sheets/{slug}.svg", svg)
        cairosvg.svg2png(url=f"downloads/sheets/{slug}.svg", write_to=f"downloads/sheets/{slug}.png", output_width=960, output_height=820)

def write_templates():
    os.makedirs("downloads/templates", exist_ok=True)
    templates = [
        ("study-plan", "Study plan", [
            "Six steps: foundations, Māheśvara, anuvṛtti, Aṣṭādhyāyī shape, sandhi as an idea, practice.",
            "Mark a step done only after you can say what the page refuses to claim.",
            "Keep IAST labeled script-converted until a person checks it.",
            "Use the contact form to report a line. Do not invent an address.",
        ]),
        ("sutra-worksheet", "Sūtra analysis worksheet", [
            "Number:",
            "Devanāgarī from the file:",
            "IAST from the file (script-converted, not yet human-checked):",
            "Type letter from the file:",
            "Meaning: not yet sourced from an open text, unless you attach an opened licence.",
            "Source you opened:",
        ]),
        ("pratyahara-worksheet", "Pratyāhāra worksheet", [
            "Start sound and line:",
            "Marker line:",
            "Sounds you computed:",
            "Check ac, ik, yaṇ, śar, ak, ec, hal=33, al=42 against the self-test.",
            "This worksheet does not ask you to translate.",
        ]),
        ("glossary-builder", "Glossary builder", [
            "Term:",
            "Learner's note (not a translation):",
            "Source URL opened, and the date:",
            "If you cannot open a source, write: confirm before relying.",
        ]),
    ]
    for slug, title, paras in templates:
        inner = f'<h1>{b.E(title)}</h1>' + "".join(f"<p>{b.E(p)}</p>" for p in paras)
        b.write(f"downloads/templates/{slug}.html", standalone_html(title, inner))
        docx_text(f"downloads/templates/{slug}.docx", title, paras)
        pdf_text(f"downloads/templates/{slug}.pdf", title, paras)

def write_cards(st):
    cards = []
    facts = [
        ("How many Aṣṭādhyāyī rows?", "3,983, from data/ashtadhyayi.json.", "ashtadhyayi.html", "Aṣṭādhyāyī"),
        ("How many Māheśvara lines?", "14, from data/maheshvara.json.", "maheshvara.html", "Māheśvara"),
        ("How many Kashmir rows?", "75. The other recension's differences are not listed.", "shiva.html", "Śiva Sūtras"),
        ("What is hal's length?", f"{len(st['known']['hal'])} sounds.", "maheshvara.html", "Māheśvara"),
        ("What is al's length?", f"{len(st['known']['al'])} sounds.", "maheshvara.html", "Māheśvara"),
        ("What does the meaning field say?", "meaning: not yet sourced from an open text.", "about.html", "About"),
        ("How is Aṣṭādhyāyī IAST labeled?", "script-converted, not yet human-checked.", "foundations.html", "Foundations"),
        ("What does the file meta call S?", "saṃjñā.", "ashtadhyayi.html", "Aṣṭādhyāyī"),
        ("What does the file meta call P?", "paribhāṣā.", "ashtadhyayi.html", "Aṣṭādhyāyī"),
        ("What does the file meta call V?", "vidhi.", "ashtadhyayi.html", "Aṣṭādhyāyī"),
        ("Are AT and AD expanded?", "No. Confirm before relying.", "ashtadhyayi.html", "Aṣṭādhyāyī"),
        ("What licence did the GRETIL page state?", "CC BY-NC-SA 4.0, checked 2026-10-16.", "shiva.html", "Śiva Sūtras"),
        ("What is a learner's note?", "A labeled teaching line, not a translation.", "index.html", "Start"),
        ("Where is the contact path?", "https://cyphermonkeylabs.com/#contact", "about.html", "About"),
        ("Does the app include a Gītā verse?", "No.", "about.html", "About"),
    ]
    for i, (front, back, href, room) in enumerate(facts, 1):
        cards.append({"id": f"c{i}", "front": front, "back": back, "source": room + ", this app's notes", "href": href, "room": href.replace(".html", ""), "roomTitle": room})
    payload = {"cards": cards, "disclaimer": DISCLAIMER, "contact": CONTACT}
    b.write("downloads/flashcards.json", json.dumps(payload, ensure_ascii=False, indent=1))
    inner = "<h1>Flashcards</h1>" + "".join(f'<p><b>{b.E(c["front"])}</b><br>{b.E(c["back"])}</p>' for c in cards)
    b.write("downloads/flashcards.html", standalone_html("Flashcards", inner))
    pdf_text("downloads/flashcards.pdf", "Flashcards", [c["front"] + " — " + c["back"] for c in cards])
    return cards

def write_deck(st):
    slides = [
        ("Sūtra Nexus", "Ancient rules. Living systems. A free study desk. Counts: 3,983 / 14 / 75."),
        ("What is not here", "No English meaning has been sourced from an open text. IAST in the Aṣṭādhyāyī file is script-converted, not yet human-checked."),
        ("Fourteen lines", "Pratyāhāras are computed. hal has 33 sounds. al has 42. Markers are dropped."),
        ("Eight chapters", "Chapter counts: " + ", ".join(str(n) for n in st["adhyaya"]) + "."),
        ("Type letters", ", ".join(f"{k} {v}" for k, v in st["types"].items()) + ". AT and AD are not expanded."),
        ("Anuvṛtti", f"{st['anuvritti']} rows carry an anuvritti array. 1.1.3 lists वृद्धिः and गुणः. They are not translated here."),
        ("Two different Śiva texts", "14 phoneme lines are not the 75 Kashmir lines. The GRETIL e-text is CC BY-NC-SA 4.0."),
        ("Dates", "Wikipedia's Pāṇini article, checked 2026-10-16, reports a dispute. This deck does not pick a year."),
        ("Practice", "Builder, quizzes, cards on this device, scripted reads. No audio file is claimed."),
        ("Downloads", "Each diagram is SVG, PNG, and HTML. One optional zip. No other archive."),
        ("Disclaimer", DISCLAIMER),
        ("CypherMonkey Labs", "© 2026 CypherMonkeyLabs. Contact form: " + CONTACT),
    ]
    write_pptx("downloads/sutra-nexus-deck.pptx", slides)

def write_catalog(rows):
    payload = {
        "disclaimer": DISCLAIMER,
        "contact": CONTACT,
        "copyright": "© 2026 CypherMonkeyLabs",
        "files": [row for row in rows if row["path"] != "downloads/catalog.json"],
    }
    b.write("downloads/catalog.json", json.dumps(payload, ensure_ascii=False, indent=2))

def catalogue(items):
    rows = []
    def add(path, kind, room, title, thumb):
        if not os.path.exists(path):
            return
        rows.append({"path": path, "kind": kind, "room": room, "title": title, "bytes": os.path.getsize(path), "thumb": thumb})
    for item in items:
        add(f'downloads/diagrams/{item["id"]}.svg', "diagram", item["room"], item["title"] + " SVG", f'downloads/diagrams/{item["id"]}.png')
        add(f'downloads/diagrams/{item["id"]}.png', "diagram", item["room"], item["title"] + " PNG", f'downloads/diagrams/{item["id"]}.png')
        add(f'downloads/diagrams/{item["id"]}.html', "diagram", item["room"], item["title"] + " HTML", f'downloads/diagrams/{item["id"]}.png')
    for slug in ["pratyahara", "counts", "read-a-number", "kashmir-notes"]:
        for ext, kind in [("html", "sheet"), ("pdf", "sheet"), ("png", "sheet")]:
            add(f"downloads/sheets/{slug}.{ext}", kind, "downloads", slug + " " + ext, f"downloads/sheets/{slug}.png")
    for slug in ["study-plan", "sutra-worksheet", "pratyahara-worksheet", "glossary-builder"]:
        for ext in ["html", "docx", "pdf"]:
            add(f"downloads/templates/{slug}.{ext}", "template", "downloads", slug + " " + ext, "downloads/sheets/counts.png")
    add("downloads/flashcards.json", "cards", "play", "Flashcards JSON", "downloads/sheets/counts.png")
    add("downloads/flashcards.html", "cards", "play", "Flashcards HTML", "downloads/sheets/counts.png")
    add("downloads/flashcards.pdf", "cards", "play", "Flashcards PDF", "downloads/sheets/counts.png")
    add("downloads/sutra-nexus-deck.pptx", "deck", "downloads", "Slide deck", "downloads/sheets/counts.png")
    for name in ["study-wheel", "guide-monkey"]:
        add(f"downloads/models/{name}.glb", "model", "about", name + " GLB", f"downloads/models/{name}.png")
        add(f"downloads/models/{name}.png", "model", "about", name + " poster", f"downloads/models/{name}.png")
        add(f"downloads/models/{name}-credits.txt", "model", "about", name + " credits", f"downloads/models/{name}.png")
    add("downloads/sutra-nexus-single-file.html", "app", "downloads", "Single-file app", "downloads/sheets/counts.png")
    add("downloads/catalog.json", "bundle", "downloads", "Download catalogue", "downloads/sheets/counts.png")
    add("downloads/sutra-nexus-all.zip", "bundle", "downloads", "Optional: everything in one ZIP", "downloads/sheets/counts.png")
    return rows

def downloads_page(rows, visual=None):
    titles = {href.replace(".html", ""): label for href, label, _desc in b.NAV}
    titles["index"] = "Start here"
    order = [href.replace(".html", "") for href, _label, _desc in b.NAV]
    groups = {}
    for row in rows:
        groups.setdefault(row["room"], []).append(row)
    rooms = [room for room in order if room in groups] + [room for room in groups if room not in order]
    sections = []
    for index, room in enumerate(rooms):
        cards = []
        for row in groups[room]:
            size = f'{row["bytes"]/1024:.0f} KB' if row["bytes"] < 1048576 else f'{row["bytes"]/1048576:.1f} MB'
            cards.append(f'''<article class="dl-card" data-dl data-kind="{b.E(row["kind"])}" data-room="{b.E(row["room"])}">
<img class="thumb" src="{b.E(row["thumb"])}" alt="" width="160" height="100" loading="lazy" decoding="async">
<h3>{b.E(row["title"])}</h3>
<p>{b.E(row["kind"])} · {size}</p>
<p><a href="{b.E(row["path"])}">Download</a></p>
</article>''')
        opened = " open" if index == 0 else ""
        label = titles.get(room, room)
        sections.append(f'<details class="dl-room"{opened}><summary>{b.E(label)} · {len(groups[room])} files</summary><div class="dl-grid">{"".join(cards)}</div></details>')
    filters = "".join(f'<button type="button" data-filter="{key}">{label}</button>' for key, label in [
        ("all", "All"), ("diagram", "Diagrams"), ("sheet", "Sheets"), ("cards", "Cards"), ("template", "Templates"), ("deck", "Deck"), ("model", "Models"), ("app", "Single file"), ("bundle", "Optional zip")])
    tail = ""
    if visual:
        tail = five_blocks("downloads.html", "Downloads", "Individual study files and one optional zip.", [
            "Every drawing is an SVG, a PNG, and an HTML page. Every 3D model is a GLB, a PNG poster, and a credits file.",
            "Cheat sheets are PDF, HTML, and PNG. Templates are DOCX, PDF, and HTML. Flashcards are PDF, JSON, and HTML.",
            "There is one optional zip, sutra-nexus-all.zip. It is the only archive. The same files are also listed one by one.",
        ], ("Take a single file", ["Filter to Sheets or Models.", "Download one file.", "Open it and find the disclaimer. You do not need the zip."]), [
            ("How many zip files does this page offer?", ["None", "One optional zip", "One zip per room", "Four"], 1, "The only archive is sutra-nexus-all.zip."),
            ("What comes with a 3D model?", ["Only the GLB", "A GLB, a PNG poster, and a credits file", "A video", "An email"], 1, "The poster is a 2D drawing, not a photograph."),
            ("Do you have to download the zip?", ["Yes", "No. Each file is also listed alone", "Only on a phone", "Only for the font"], 1, "The zip is optional."),
            ("What is inside the zip's readme?", ["A translation of 1.1.1", "The disclaimer, the contents, and the licence notes", "A Gītā verse", "A password"], 1, "The readme repeats the disclaimer."),
            ("Are the cheat-sheet PNGs the full wording?", ["They replace the PDF", "They are posters. The HTML and PDF carry the full wording", "They are audio", "They omit the disclaimer"], 1, "The SVG caption says the HTML and PDF carry the full wording, and the disclaimer is painted on the poster."),
        ], visual, [("optional zip", "One archive that repeats the individual files. You can skip it.")])
    body = f'''<h1 class="hero-title">Downloads</h1>
<p class="lede">Every file is listed on its own. The zip is optional and is the only archive.</p>
{tail}
<div class="filter-bar" data-filters>{filters}</div>
{''.join(sections)}
<section class="note"><h2>Optional: everything in one ZIP</h2><p>The card labeled bundle is the only zip. It repeats the same files and includes a readme with this disclaimer and the credits.</p></section>'''
    return b.page_shell("downloads.html", "Downloads · Sūtra Nexus", "Individual study files and one optional zip.", body)

def write_zip(rows):
    path = "downloads/sutra-nexus-all.zip"
    if os.path.exists(path):
        os.remove(path)
    readme = "Sūtra Nexus optional bundle\n\n" + DISCLAIMER + "\nContact form: " + CONTACT + "\n\nContents:\n"
    names = []
    for row in rows:
        if row["path"].endswith(".zip"):
            continue
        names.append(row["path"] + f' ({row["bytes"]} bytes, {row["kind"]})')
    readme += "\n".join(names)
    readme += "\n\nLicences: see assets/data/licences.json in the site. Simple Icons 13.21.0 are CC0. Noto Sans Devanagari is OFL 1.1. The GRETIL e-text is CC BY-NC-SA 4.0. The ashtadhyayi-com data README asks for credit and states no SPDX.\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", readme)
        for row in rows:
            if row["path"].endswith(".zip") or row["path"] == "downloads/catalog.json":
                continue
            zf.write(row["path"], row["path"])
        if os.path.exists("downloads/catalog.json"):
            zf.write("downloads/catalog.json", "downloads/catalog.json")
    return path

def search_index(st, items, glossary):
    rows = []
    for href, label, desc in b.NAV:
        rows.append({"title": label, "href": href, "kind": "room", "note": desc, "hay": f"{label} {desc} {href}"})
    for term, defn, href in glossary:
        rows.append({"title": term, "href": href, "kind": "glossary", "note": defn, "hay": f"{term} {defn}"})
    for item in items:
        rows.append({"title": item["title"], "href": f'downloads/diagrams/{item["id"]}.html', "kind": "diagram", "note": item["source"][:80], "hay": item["title"] + " " + item["source"]})
    for row in st["ashta"]["sutras"]:
        rows.append({"title": row["num"], "href": "ashtadhyayi.html#browser", "kind": "sūtra", "note": "meaning not yet sourced", "hay": f'{row["num"]} {row["devanagari"]} {row["iast"]}'})
    for row in st["shiva"]["sutras"]:
        rows.append({"title": "Kashmir " + row["num"], "href": "shiva.html", "kind": "sūtra", "note": "no English", "hay": f'{row["num"]} {row["devanagari"]} {row["iast"]} kashmir'})
    b.write("assets/data/search-index.json", json.dumps({"items": rows}, ensure_ascii=False))
    compact = [[row["num"], row["devanagari"], row["iast"]] for row in st["ashta"]["sutras"]]
    b.write("assets/data/sutra-index.json", json.dumps({"rows": compact}, ensure_ascii=False))

def site_json(pages, cards, items):
    facts, quizzes, lessons, curriculum, gloss = [], [], [], [], []
    for spec in list(pages) + EXTRA:
        lessons.append({"id": spec["file"].replace(".html", ""), "title": spec["title"], "room": spec["file"].replace(".html", ""), "href": spec["file"], "steps": [{"title": spec["title"], "text": spec["paras"][0], "href": spec["file"]}]})
        curriculum.append({"room": spec["file"].replace(".html", ""), "title": spec["title"], "href": spec["file"], "track": "study", "trackName": "Sūtra study"})
        for para in spec["paras"]:
            facts.append({"id": spec["file"] + "-" + str(len(facts)), "text": para, "href": spec["file"], "cite": spec["title"], "room": spec["file"].replace(".html", ""), "roomTitle": spec["title"], "keywords": [], "weight": 1, "difficulty": "medium", "kind": "takeaway"})
        for term, defn in spec["glossary"]:
            gloss.append((term, defn, spec["file"]))
            facts.append({"id": "g-" + spec["file"] + "-" + term, "text": term + ": " + defn, "href": spec["file"] + "#ecosystem", "cite": spec["title"], "room": spec["file"].replace(".html", ""), "roomTitle": spec["title"], "keywords": [term], "kind": "card"})
        for i, (q, choices, answer, why) in enumerate(spec["quizzes"]):
            quizzes.append({"id": spec["file"] + str(i), "room": spec["file"].replace(".html", ""), "roomTitle": spec["title"], "href": spec["file"] + "#quiz", "question": q, "choices": choices, "answer": answer, "why": why, "difficulty": "medium"})
    games = []
    for item in quizzes[:12]:
        games.append({"id": "game-" + item["id"], "prompt": item["question"], "choices": item["choices"], "answer": item["answer"], "why": item["why"], "href": item["href"], "cite": item["roomTitle"]})
    payload = {
        "rooms": [{"id": spec["file"].replace(".html", ""), "title": spec["title"], "href": spec["file"], "howTo": spec["desc"]} for spec in list(pages) + EXTRA],
        "facts": facts,
        "quizzes": quizzes,
        "cards": cards,
        "lessons": lessons,
        "tours": [{"id": "home", "match": ["index.html"], "title": "Start", "steps": [{"text": "Six steps. The gaps stay labeled.", "href": "index.html"}]}],
        "curriculum": curriculum,
        "pages": [{"file": spec["file"], "title": spec["title"], "lede": spec["paras"][0], "howTo": spec["desc"], "keywords": [spec["title"]]} for spec in list(pages) + EXTRA],
        "games": games,
        "glossary": [{"term": t, "defn": d, "href": h} for t, d, h in gloss],
        "diagrams": [{"id": item["id"], "title": item["title"], "animated": item["animated"]} for item in items],
    }
    b.write("content/site.json", json.dumps(payload, ensure_ascii=False))
    return gloss

EXTRA = []

def five_blocks(file, title, desc, paras, example, quizzes, visual, glossary, sources=None):
    EXTRA[:] = [spec for spec in EXTRA if spec["file"] != file]
    EXTRA.append({"file": file, "title": title, "desc": desc, "paras": paras, "glossary": glossary, "quizzes": quizzes})
    qhtml = "".join(quiz(f"{file}-q{i}", q, ch, a, w) for i, (q, ch, a, w) in enumerate(quizzes, 1))
    return (
        learn_block(paras)
        + visual_block(visual)
        + example_block(example[0], example[1])
        + f'<section class="quiz" id="quiz"><h2>Quiz</h2>{qhtml}</section>'
        + sources_block(sources if sources is not None else [DATA_CREDIT, WIKI_ASHTA])
        + eco_block(glossary, "Sister rooms are the chips in the section banner.", "Learner's note (not a translation): this page explains the app. It does not add a rule of the grammar.", "An open meaning, and a human check of the IAST. Confirm before relying.")
    )

def other_pages(st, items, pages):
    # diagrams gallery
    cards = []
    for item in items:
        cards.append(f'''<article class="diagram-card"><h3>{b.E(item["title"])}</h3>
<img src="downloads/diagrams/{item["id"]}.png" alt="{b.E(item["title"])}" width="320" height="180" loading="lazy" decoding="async">
<p>{b.E(item["source"])}</p>
<p><a href="downloads/diagrams/{item["id"]}.svg">SVG</a> · <a href="downloads/diagrams/{item["id"]}.png">PNG</a> · <a href="downloads/diagrams/{item["id"]}.html">HTML</a></p></article>''')
    b.write("diagrams.html", b.page_shell("diagrams.html", "Diagrams · Sūtra Nexus", "Drawings with SVG, PNG, and HTML.",
        f'<h1 class="hero-title">Diagrams</h1><p class="lede">{len(items)} drawings. {sum(1 for i in items if i["animated"])} include a moving dot. Reduced motion hides the dot.</p>'
        + five_blocks("diagrams.html", "Diagrams", "Drawings with SVG, PNG, and HTML.", [
            "Each drawing has three files: an SVG, a PNG of that SVG, and a standalone HTML page. The disclaimer is inside all three.",
            "A moving dot means reading order. If you asked the browser to reduce motion, the dot is hidden and the boxes stay.",
            "Counts on a chart are from the JSON files. A mind map is a map of this app, not a claim about history.",
        ], ("Open one drawing three ways", ["Pick a card below.", "Open the SVG, then the PNG, then the HTML.", "The words match. The HTML page also has the site footer."]), [
            ("What does a moving dot mean?", ["A recitation", "Reading order", "A sandhi join", "A translation"], 1, "The caption says the dot shows reading order."),
            ("What happens to the dot when motion is reduced?", ["It speeds up", "It is hidden", "It becomes a video", "It is emailed"], 1, "The SVG hides the mover when motion is reduced."),
            ("How many file types does each drawing have?", ["One PDF", "SVG, PNG, and HTML", "Only a GIF", "A ZIP per drawing"], 1, "Those three files are written for every drawing."),
            ("Is a mind map here a historical claim?", ["Yes", "No, it is a map of this app", "It quotes a verse", "It is a dhātu list"], 1, "The source line on each mind map says what it is."),
            ("Where is the disclaimer on a drawing?", ["Only on the home page", "Inside the SVG, the PNG, and the HTML page", "In an email", "It is omitted from PNG"], 1, "The PNG is a picture of the SVG, and the SVG paints the disclaimer."),
        ], items[0], [("diagram", "A drawing with a title, a caption, and a source line.")])
        + f'<div class="grid-2">{"".join(cards)}</div>'))
    charts = [i for i in items if i["kind"] == "chart"]
    chart_html = "".join(f'<article class="diagram-card"><h3>{b.E(i["title"])}</h3><img src="downloads/diagrams/{i["id"]}.png" alt="{b.E(i["title"])}" width="320" height="180" loading="lazy" decoding="async"><p>{b.E(i["source"])}</p></article>' for i in charts)
    chart_visual = charts[0] if charts else items[0]
    b.write("charts.html", b.page_shell("charts.html", "Charts · Sūtra Nexus", "Counts from the data files.",
        '<h1 class="hero-title">Charts</h1><p class="lede">These numbers are counts from the JSON files, not traffic or adoption.</p>'
        + five_blocks("charts.html", "Charts", "Counts from the data files.", [
            "A bar is a count of rows in a file in this repository. It is not a survey and not a popularity rank.",
            "Chapter bars add up to 3,983. The type-letter bars use the letters stored on each row.",
            "AT and AD stay unexpanded. The file meta glosses S, P, and V only.",
        ], ("Check one bar", ["Open the adhyāya chart.", "Add the eight numbers.", "The sum is 3,983, the length of data/ashtadhyayi.json."]), [
            ("What does a bar count?", ["Page views", "Rows in a file in this repository", "Students", "Years"], 1, "The caption names the file."),
            ("What do the eight chapter bars add up to?", ["75", "14", "3,983", "200"], 2, "That is the length of the Aṣṭādhyāyī file."),
            ("Which type letters does the file meta gloss?", ["AT and AD", "S, P, and V", "Only V", "None"], 1, "The meta glosses S as saṃjñā, P as paribhāṣā, and V as vidhi."),
            ("Should AT be read as a named rule class here?", ["Yes, as atideśa", "No. Confirm before relying", "Yes, as a dhātu", "Yes, as sandhi"], 1, "The app does not expand AT or AD."),
            ("Are these charts traffic?", ["Yes", "No", "Only the home page", "Only downloads"], 1, "They are file counts."),
        ], chart_visual, [("bar", "A count from a JSON file, named in the caption.")])
        + f'<div class="grid-2">{chart_html}</div>'))
    # glossary gathered later
    resources = [
        DATA_CREDIT, WIKI_ASHTA, WIKI_PANINI, WIKI_SHIKSHA, WIKI_SANDHI, WIKI_IAST, WIKI_DEVA, WIKI_MAHA, WIKI_KASH, GRETIL,
        {"name": "ashtadhyayi.com", "url": "https://ashtadhyayi.com/", "detail": "The site that reads ashtadhyayi-com/data. Opened 2026-10-16. Commentaries on that site are not copied here.", "licence": "site content stays with its owners"},
        {"name": "Simple Icons 13.21.0", "url": "", "detail": "Icons for GitHub, X, LinkedIn, Hugging Face, and Linktree. Named here without a link. The licence file was fetched the same day.", "licence": "CC0-1.0"},
        {"name": "Noto Sans Devanagari", "url": "", "detail": "Subset woff2 shipped for the Devanāgarī block. Named here without a link. The font's name table says SIL OFL 1.1.", "licence": "OFL-1.1"},
    ]
    b.write("resources.html", b.page_shell("resources.html", "Resources · Sūtra Nexus", "Pages opened on 2026-10-16.",
        f'<h1 class="hero-title">Resources</h1><p class="lede">Each citation below was opened on {CHECKED}. If a later page changes, confirm before relying.</p>'
        + five_blocks("resources.html", "Resources", "Pages opened on 2026-10-16.", [
            "A link on this page was opened in October 2026 and the licence line is what that page said then.",
            "Wikipedia text is CC BY-SA. The GRETIL e-text page states CC BY-NC-SA 4.0. The data README asks for credit and states no SPDX.",
            "Vasu's English was not confirmed, so no words from it appear. Confirm before relying on any meaning you add later.",
        ], ("Check a licence line", ["Pick the GRETIL row.", "Read CC BY-NC-SA 4.0.", "That is why the Kashmir file is source text only."]), [
            ("When were these pages opened for this app?", ["2019", "2026-10-16", "The year of Pāṇini", "Unknown and unstated"], 1, "The date is written on the page."),
            ("What licence did the GRETIL page state?", ["MIT", "CC BY-NC-SA 4.0", "Public domain with no conditions", "All rights reserved, no grant"], 1, "Non-commercial and share-alike apply to that e-text."),
            ("Why is there no Vasu English?", ["It was rejected as too long", "The licence was not confirmed", "The file already had it", "It is the same as GRETIL"], 1, "Unconfirmed text is not copied."),
            ("What does the data README require?", ["A fee", "Appropriate credit", "A login", "An email"], 1, "The raw README says you are free to use the data if you give credit."),
            ("If a source page changes later, what should you do?", ["Keep the old quote as current", "Confirm before relying", "Delete the Devanāgarī", "Invent the new sentence"], 1, "The page says so."),
        ], items[0], [("source", "A page that was opened, with the licence written down.")], resources)))
    play = '''<h1 class="hero-title">Play</h1>
<p class="lede">Touch and keyboard both work. Scores stay in this browser.</p>
<section class="card" data-pratyahara><h2>Build a pratyāhāra</h2>
<p>The same builder as the Māheśvara page. Marker lines are 1 through 14.</p>
<p class="note">Open the Māheśvara page for the full control. Here is a quick check.</p>
<form data-game data-expect="33" data-why="hal is 33 sounds in the self-test.">
<label>How many sounds are in hal? <input name="answer" inputmode="numeric" aria-label="hal length"></label>
<button type="submit">Check</button><p class="why"></p></form></section>
<section class="card"><h2>Sort the glossed type letters</h2>
<form data-game data-expect="vidhi" data-why="The file meta says V means vidhi. AT and AD are not in this answer.">
<label>The file meta calls V <input name="answer" aria-label="gloss of V"></label>
<button type="submit">Check</button><p class="why"></p></form></section>
<section class="card"><h2>Match a marker</h2>
<form data-game data-expect="4" data-why="ac stops at the marker on line 4.">
<label>ac stops at marker line <input name="answer" inputmode="numeric" aria-label="marker line for ac"></label>
<button type="submit">Check</button><p class="why"></p></form></section>
<section class="card" data-cards><h2>Flashcards</h2>
<p data-card-front></p><p data-card-back hidden></p>
<button type="button" data-card-show>Show</button>
<button type="button" data-card-again>Again</button>
<button type="button" data-card-know>Know</button>
<p class="note">Again waits about a minute. Know waits a day, then three, then seven. This is a simple ladder, not a medical schedule.</p></section>
<section class="card" id="interview"><h2>Interview bank</h2>
<p>Generic questions. Sample answers cite this app's sources. They are not a personal résumé and not a claim about a job.</p>
<h3>How is a pratyāhāra like a character class?</h3>
<p>Learner's note (not a translation): both name a set. In this app, ac is the computed list ''' + " ".join(st["known"]["ac"]) + '''. The analogy is made here. Confirm before relying if you present it as Pāṇini's own comparison.</p>
<h3>What would you refuse to invent in an interview?</h3>
<p>An English meaning, a sandhi join, a century for Kātyāyana, and which Kashmir lines differ. The pages say confirm before relying.</p>
<h3>How does anuvṛtti resemble a carried variable?</h3>
<p>Learner's note (not a translation): 1.1.3's file field lists two earlier strings. Calling that a variable is a bridge for programmers, not a translation of the line.</p>
</section>'''
    b.write("play.html", b.page_shell("play.html", "Play · Sūtra Nexus", "Builders, cards, and an interview bank.",
        play + five_blocks("play.html", "Play", "Builders, cards, and an interview bank.", [
            "Games check a number or a gloss that this app already states. They do not score you on a translation.",
            "Flashcards use a simple ladder on this device: again is about a minute, then a day, three days, and seven.",
            "Interview answers are generic and cited. They are not a résumé and not someone's job story.",
        ], ("Recompute hal", ["Open the builder.", "Start at h on line 5.", "Stop at marker line 14.", "Count 33 sounds."]), [
            ("How many sounds does the self-test give hal?", ["14", "33", "42", "75"], 1, "hal is 33 in the self-test."),
            ("Where do card timings live?", ["A server", "This browser", "An email", "The zip"], 1, "The ladder uses local storage."),
            ("What is an interview answer here?", ["A personal résumé", "A generic note that cites this app", "A sūtra translation", "A recorded voice"], 1, "The page says they are not a résumé."),
            ("What does Again wait?", ["A week", "About a minute", "A year", "Until you log in"], 1, "The note under the cards says about a minute."),
            ("Does the builder translate the set?", ["Yes", "No", "Only ac", "Only into Hindi"], 1, "The note says the set is not a translation."),
        ], items[0], [("pratyāhāra", "A set computed from a start sound and a marker line.")])
        + builder_html(st).replace("<h2>Builder</h2>", "<h2>Full builder</h2>")))
    listen = '''<h1 class="hero-title">Listen</h1>
<p class="lede">These are scripted reads run on the page and in the guide. There is no audio file and no recited Sanskrit recording.</p>
<section class="card" id="minute"><h2>1-minute clip</h2>
<ol>
<li>Three files: 3,983, 14, and 75.</li>
<li>Meanings are not sourced yet.</li>
<li>IAST in the grammar file is script-converted.</li>
<li>The builder can recompute ac.</li>
</ol>
<p class="note">About one minute if you read slowly. Not a video.</p></section>
<section class="card" id="trailer"><h2>10-minute trailer</h2>
<ol>
<li>Read Start, then Foundations.</li>
<li>Compute ac, hal, and al.</li>
<li>Open 1.1.3 and look at the anuvritti field without translating it.</li>
<li>Read the type-letter chart and leave AT and AD unexpanded.</li>
<li>Read the dating dispute and do not pick a year.</li>
<li>Remember the Kashmir file is a different text, under CC BY-NC-SA 4.0.</li>
<li>Take one quiz.</li>
<li>Open the guide and leave the voice off.</li>
</ol></section>
<section class="card" id="hour"><h2>1-hour guided walk</h2>
<p>The guide's one-hour course walks the rooms in order and asks a checkpoint from each room's quiz. It only repeats sentences written in the app. Stay with it and the reading is about an hour. It is not a recording.</p>
<p><button type="button" data-open-guide>Open the guide</button></p></section>'''
    b.write("listen.html", b.page_shell("listen.html", "Listen · Sūtra Nexus", "Scripted reads. No audio file.",
        listen + five_blocks("listen.html", "Listen", "Scripted reads. No audio file.", [
            "The 1-minute clip, the 10-minute trailer, and the 1-hour walk are scripts you read. There is no video file and no Sanskrit recording.",
            "Voice in the guide is off until you turn it on. A browser voice may mispronounce Sanskrit. It is a reading aid.",
            "The one-hour course repeats sentences already written in the rooms and then asks a checkpoint.",
        ], ("Read the one-minute script", ["Open the 1-minute card above.", "Read the four lines slowly.", "You have not played a video."]), [
            ("Is the 1-minute clip a video?", ["Yes", "No, it is a scripted read", "It is an mp3", "It is a lecture recording"], 1, "The page says it is not a video."),
            ("What is the default for voice?", ["On, in Sanskrit", "Off", "A downloaded recitation", "Email audio"], 1, "Voice stays off until you turn it on."),
            ("What may a browser voice get wrong?", ["Nothing", "Sanskrit pronunciation", "The number 3,983", "The disclaimer"], 1, "The guide says Sanskrit may be wrong."),
            ("What does the one-hour course repeat?", ["A new translation", "Sentences already written in the app", "A Gītā verse", "A personal story"], 1, "It does not invent lines."),
            ("Where is the 10-minute trailer?", ["A streaming site", "On this Listen page", "Inside the zip only", "In an email"], 1, "It is the reading list with id trailer."),
        ], items[0], [("scripted read", "Text you read on the page. Not an audio file.")])
    ))
    about = '''<h1 class="hero-title">About</h1>
<p>Sūtra Nexus is a free learning project by a lifelong student and AI enthusiast moving toward AI omni-channel agents. The note is short on purpose.</p>
<p>Corrections go through the <a href="https://cyphermonkeylabs.com/#contact">contact form</a>. There is no email address on this site.</p>
<p>The study wheel below is optional and loads only if you ask, on a wide screen, with motion allowed.</p>
<div data-three style="width:72px;height:72px"></div>
<button type="button" data-load-three>Load the 3D wheel</button>
<p class="note">Phones and reduced motion keep the still poster in Downloads.</p>'''
    b.write("about.html", b.page_shell("about.html", "About · Sūtra Nexus", "A short note about the project.",
        about + five_blocks("about.html", "About", "A short note about the project.", [
            "This is a free learning project by a lifelong student and AI enthusiast moving toward AI omni-channel agents.",
            "Nothing here is sold. Corrections go through the contact form. There is no email address on this site.",
            "The 3D wheel loads only if you ask, on a wide screen, with motion allowed. Phones keep the still poster.",
        ], ("Send a correction without email", ["Find the contact form link in the disclaimer.", "It opens the Labs contact section.", "Say which line to check."]), [
            ("How do you report a correction?", ["An email address on this site", "The contact form", "A comment under a video", "By editing the data silently"], 1, "The about page and the disclaimer name the form."),
            ("Is anything sold here?", ["The zip", "No", "The 3D model", "A certificate"], 1, "The disclaimer says nothing here is sold."),
            ("When does the 3D wheel load?", ["On every phone", "When you ask, on a wide screen, with motion allowed", "In the service worker", "Never, there is no model"], 1, "Phones and reduced motion keep the poster."),
            ("Who is the project for?", ["A vendor exam", "A learner, as a free study desk", "A résumé", "A paid class"], 1, "It is a learning-only student project."),
            ("Does this site show an email address?", ["Yes", "No", "Only in the zip", "Only in the guide"], 1, "Contact is the form."),
        ], items[0], [("contact form", "The link in the disclaimer. Not an email address.")])
    ))
    credits = '''<h1 class="hero-title">Credits</h1>
<table>
<thead><tr><th>Name</th><th>Version</th><th>Licence</th><th>URL</th></tr></thead>
<tbody>
<tr><td>Webex Lab kit, adapted</td><td>commit 7631b317cbf2cad236403df960b5d5fac353a6de</td><td>MIT</td><td><a href="https://github.com/CypherMonkeyLabs/webex-lab-free-university-mesmerizing">repository</a></td></tr>
<tr><td>anime.js</td><td>4.5.0, vendored, loaded only if the 3D extra starts</td><td>MIT</td><td><a href="https://animejs.com/">animejs.com</a></td></tr>
<tr><td>rough.js</td><td>4.6.6, vendored, same optional load</td><td>MIT</td><td><a href="https://roughjs.com/">roughjs.com</a></td></tr>
<tr><td>three.js</td><td>r170, vendored, same optional load</td><td>MIT</td><td><a href="https://threejs.org/">threejs.org</a></td></tr>
<tr><td>d3</td><td>7.9.0, vendored, not loaded by the pages</td><td>ISC</td><td><a href="https://d3js.org/">d3js.org</a></td></tr>
<tr><td>canvas-confetti</td><td>1.9.3, vendored, not loaded by the pages</td><td>ISC</td><td><a href="https://github.com/catdad/canvas-confetti">repository</a></td></tr>
<tr><td>markmap-view</td><td>0.18.12, vendored, not loaded; mind maps are static SVG</td><td>MIT</td><td><a href="https://markmap.js.org/">markmap.js.org</a></td></tr>
<tr><td>Simple Icons</td><td>13.21.0</td><td>CC0-1.0</td><td>simpleicons.org, named without a link</td></tr>
<tr><td>Noto Sans Devanagari</td><td>subset of the regular face</td><td>OFL-1.1</td><td>notofonts/devanagari, named without a link</td></tr>
<tr><td>ashtadhyayi-com/data</td><td>the three JSON files' source</td><td>credit required, no SPDX</td><td><a href="https://github.com/ashtadhyayi-com/data">repository</a></td></tr>
<tr><td>GRETIL e-text</td><td>Śivasūtra with vārttika</td><td>CC BY-NC-SA 4.0</td><td><a href="https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_zivasUtra-with-vArttika.htm">GRETIL page</a></td></tr>
<tr><td>Study wheel and guide monkey models</td><td>original</td><td>CC0-1.0</td><td>downloads/models/</td></tr>
</tbody></table>
<p class="note">Code libraries are MIT, Apache-2.0, BSD, or ISC. CC0 and CC BY and OFL and CC BY-NC-SA are limited to icons, the font, art, or the cited data, with attribution kept. Vendored files live in vendor/.</p>'''
    b.write("credits.html", b.page_shell("credits.html", "Credits · Sūtra Nexus", "Libraries, icons, the font, and the data.",
        credits + five_blocks("credits.html", "Credits", "Libraries, icons, the font, and the data.", [
            "Code libraries in vendor/ are MIT or ISC. They are not loaded on the first screen except where a page says so.",
            "Simple Icons 13.21.0 are CC0. Noto Sans Devanagari is OFL 1.1. The two 3D models are original and marked CC0.",
            "The Webex Lab kit was adapted from commit 7631b317cbf2cad236403df960b5d5fac353a6de. Webex and Cisco product copy is not used.",
        ], ("Find the Webex commit", ["Open the first row of the table.", "Read the commit.", "That is the kit this chrome was adapted from."]), [
            ("Which Webex Lab commit was adapted?", ["A local copy with no hash", "7631b317cbf2cad236403df960b5d5fac353a6de", "The main branch with no pin", "A Cisco sample"], 1, "The credits table names that commit."),
            ("What licence are the Simple Icons?", ["CC BY-NC", "CC0-1.0", "Proprietary", "OFL"], 1, "Version 13.21.0, checked 2026-10-16."),
            ("What licence is the Devanāgarī font subset?", ["MIT", "OFL-1.1", "CC BY-NC-SA", "None"], 1, "The name table and the OFL file say SIL OFL 1.1."),
            ("Are d3 and markmap loaded on the home page?", ["Yes", "No, they are vendored and not loaded", "Only markmap", "Only on phones"], 1, "Mind maps are static SVG."),
            ("Who owns the study-wheel model?", ["A scanned museum object", "It is original geometry in this repository, marked CC0", "three.js", "Wikipedia"], 1, "The credits file next to the GLB says so."),
        ], items[0], [("vendor", "A library file kept in this repository, with its licence named.")])
    ))
    # ecosystem page uses mind diagrams
    minds = [i for i in items if i["kind"] == "mind"]
    mind_html = "".join(f'<article class="diagram-card"><h3>{b.E(i["title"])}</h3><img src="downloads/diagrams/{i["id"]}.png" alt="{b.E(i["title"])}" width="320" height="180" loading="lazy" decoding="async"><p>{b.E(i["source"])}</p></article>' for i in minds)
    eco = f'''<h1 class="hero-title">Ecosystem</h1>
<p class="lede">A map of this app. Sister topics point at rooms. Bridges are labeled learner's notes.</p>
<div class="grid-2">{mind_html}</div>
<section class="eco"><h2>Integration</h2>
<p>Phonetics, linguistics, and programming-language teaching all have reasons to look at a named sound set. This page does not cite a specific NLP paper. Confirm before relying on any paper you add.</p>
<h2>Future hooks</h2>
<p>An open meaning, a human IAST check, and a dhātu list only after its licence is confirmed.</p></section>'''
    eco_visual = minds[0] if minds else items[0]
    b.write("ecosystem.html", b.page_shell("ecosystem.html", "Ecosystem · Sūtra Nexus", "How the rooms connect.",
        eco + five_blocks("ecosystem.html", "Ecosystem", "How the rooms connect.", [
            "Each study room ends with a glossary, sister topics, a bridge, and a later hook. This page gathers the maps.",
            "A bridge is a learner's note. It is not a quotation from Pāṇini and not a claim that the tradition described software.",
            "No NLP paper is cited here. Confirm before relying if you attach one.",
        ], ("Read a bridge as a bridge", ["Open a mind map.", "Read the caption.", "If it says learner's note, do not quote it as a sūtra."]), [
            ("What is a bridge on this site?", ["A translated sūtra", "A labeled learner's note", "A dhātu list", "A video"], 1, "The pages say the analogy is made here."),
            ("Does this page cite an NLP paper?", ["Yes, three", "No", "Only Vasu", "Only the Gītā"], 1, "It says no specific paper is cited."),
            ("Where does each study room put its glossary?", ["Only here", "In the ecosystem section at the end of the room, and terms also appear in the glossary", "In an email", "Nowhere"], 1, "The room section is titled Ecosystem."),
            ("Is a sister topic a historical claim?", ["Always", "No. It points at another room", "It dates Kātyāyana", "It expands AT"], 1, "Sister topics are navigation."),
            ("What future hook is named?", ["A paid tier", "An open meaning and a human IAST check", "A Gītā chapter", "A sandhi join that was invented"], 1, "Those are the gaps."),
        ], eco_visual, [("bridge", "A learner's analogy, labeled, and not a translation.")])
    ))

def glossary_page(gloss, visual):
    rows = "".join(f'<tr><td>{b.E(t)}</td><td>{b.E(d)}</td><td><a href="{b.E(h)}">Room</a></td></tr>' for t, d, h in gloss)
    tail = five_blocks("glossary.html", "Glossary", "Terms used in these rooms.", [
        "A glossary line is the wording used in this app. If it is not a quotation, it is a learner's note.",
        "Sthāna and prayatna are named and then marked as not charted. Confirm before relying on a chart from somewhere else.",
        "The same term can appear on the room that introduced it. This table points back there.",
    ], ("Look up pratyāhāra", ["Find the row.", "Read the note.", "Open the room and compute a set."]), [
        ("Is a glossary line always a translation?", ["Yes", "No. It is the wording used in this app", "Only the first row", "Only Kashmir"], 1, "Translations are not included."),
        ("Does this app chart sthāna?", ["Yes, fully", "No. The term is named and the chart is not drawn", "Only vowels", "Only in the zip"], 1, "No open phonetic edition was confirmed."),
        ("What does the table link to?", ["An email", "The room that introduced the term", "A video", "A store"], 1, "The third column is the room."),
        ("What should you do with an unsourced definition?", ["Treat it as Pāṇini", "Confirm before relying", "Add it to the data file", "Recite it"], 1, "Gaps stay labeled."),
        ("How many Māheśvara lines does the glossary's app use?", ["10", "14", "75", "77"], 1, "The file has 14 lines."),
    ], visual, [("glossary", "A short note for a term used in these rooms.")])
    b.write("glossary.html", b.page_shell("glossary.html", "Glossary · Sūtra Nexus", "Terms used in these rooms.", f'<h1 class="hero-title">Glossary</h1><table><thead><tr><th>Term</th><th>Note</th><th>Where</th></tr></thead><tbody>{rows}</tbody></table>{tail}'))

def js_embed(value):
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

def scope_ids(html, room):
    html = re.sub(r'\bid="([^"]+)"', lambda match: f'id="{room}-{match.group(1)}"', html)
    html = re.sub(r'href="#([^"]+)"', lambda match: f'href="#{room}-{match.group(1)}"', html)
    return html

def write_single_file():
    panels = []
    for href, _label, _desc in b.NAV:
        text = open(href, encoding="utf-8").read()
        match = re.search(r'<main id="main"[^>]*>(.*)</main>', text, re.S)
        if not match:
            raise SystemExit("single file could not read " + href)
        room = href.replace(".html", "")
        hidden = "" if room == "index" else " hidden"
        panels.append(f'<section data-room-panel="{room}"{hidden}>{scope_ids(match.group(1), room)}</section>')
    switch = '''<script>
document.addEventListener("click", function (event) {
  var link = event.target.closest ? event.target.closest("a[href]") : null;
  if (!link) return;
  var href = link.getAttribute("href") || "";
  var match = href.match(/^([A-Za-z0-9_-]+)\\.html([#?][\\s\\S]*)?$/);
  if (!match) return;
  event.preventDefault();
  var id = match[1];
  document.querySelectorAll("[data-room-panel]").forEach(function (panel) {
    panel.hidden = panel.getAttribute("data-room-panel") !== id;
  });
  document.body.dataset.room = id;
  document.querySelectorAll(".section-chip, .drawer a[href], .dock-item[href]").forEach(function (node) {
    var target = (node.getAttribute("href") || "").split("#")[0];
    if (target === id + ".html") node.setAttribute("aria-current", "page");
    else node.removeAttribute("aria-current");
  });
  var hash = "";
  if (match[2] && match[2].charAt(0) === "#") hash = match[2].slice(1);
  var target = hash ? (document.getElementById(id + "-" + hash) || document.getElementById(hash)) : null;
  if (target) target.scrollIntoView();
  else window.scrollTo(0, 0);
}, true);
</script>'''
    body = (
        '<p class="lede">This file is the study app in one page. Colours, the guide, search, and the sūtra index are inside the file. The optional 3D wheel stays in the multi-file site.</p>'
        + "".join(panels)
        + switch
    )
    html = b.page_shell("index.html", "Sūtra Nexus — single file", "The study app in one HTML file.", body)
    html = html.replace('<link rel="stylesheet" href="assets/css/sutra.css">', "<style>\n" + css_standalone(True) + "\n</style>")
    html = re.sub(r'<link rel="icon"[^>]*>\n?', "", html)
    html = re.sub(r'<script>if\(location\.protocol[\s\S]*?</script>\n?', "", html)
    embed = {
        "search": json.load(open("assets/data/search-index.json", encoding="utf-8")),
        "cards": json.load(open("downloads/flashcards.json", encoding="utf-8")),
        "sutras": json.load(open("assets/data/sutra-index.json", encoding="utf-8")),
        "kb": json.load(open("guide/kb/bundle.json", encoding="utf-8")),
    }
    def inline_script(path):
        return "<script>\n" + open(path, encoding="utf-8").read() + "\n</script>"
    engine = open("guide/engine.mjs", encoding="utf-8").read().replace("export function", "function")
    guide = open("assets/js/guide.js", encoding="utf-8").read().replace(
        'import { createGuide, blankSession } from "../../guide/engine.mjs";\n', ""
    )
    html = html.replace(
        '<script src="assets/js/brand.js"></script>',
        "<script>window.SUTRA_EMBED=" + js_embed(embed) + ";</script>\n" + inline_script("assets/js/brand.js"),
    )
    html = html.replace('<script src="assets/js/frame.js"></script>', inline_script("assets/js/frame.js"))
    html = html.replace('<script src="assets/js/phone-nav.js"></script>', inline_script("assets/js/phone-nav.js"))
    html = html.replace('<script src="assets/js/app.js"></script>', inline_script("assets/js/app.js"))
    html = html.replace(
        '<script type="module" src="assets/js/guide.js"></script>',
        "<script type=\"module\">\n" + engine + "\n" + guide + "\n</script>",
    )
    if "sutra.css" in html or 'src="assets/' in html:
        raise SystemExit("single file still points at an external asset")
    b.write("downloads/sutra-nexus-single-file.html", html)

def favicon():
    b.write("favicon.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#4c1d95"/><circle cx="16" cy="16" r="8" fill="none" stroke="#fde047" stroke-width="2"/><circle cx="16" cy="16" r="2" fill="#67e8f9"/></svg>''')

def offline():
    b.write("offline.html", b.page_shell("offline.html", "Offline · Sūtra Nexus", "You are offline.", "<h1>You are offline</h1><p>Cached pages can still open. The contact form is not cached.</p>"))

def licences():
    data = {
        "checked": CHECKED,
        "texts": [
            {"text": "Aṣṭādhyāyī rows and Māheśvara lines", "author": "ashtadhyayi-com/data", "year": "repository README opened 2026", "url": "https://github.com/ashtadhyayi-com/data", "licence": "Free to use with appropriate credit. No SPDX identifier in the README.", "status": "confirmed", "date": CHECKED, "words": "Devanāgarī source text only. English meanings not included."},
            {"text": "Kashmir Śiva Sūtras e-text", "author": "GRETIL, input as stated on the page", "year": "page opened 2026", "url": GRETIL["url"], "licence": "CC BY-NC-SA 4.0", "status": "confirmed", "date": CHECKED, "words": "Source text only. No English translation copied."},
            {"text": "Vasu Aṣṭādhyāyī English", "author": "not confirmed", "year": "", "url": "", "licence": "not confirmed", "status": "unconfirmed", "date": CHECKED, "words": "not included"},
            {"text": "Any Bhagavad Gītā verse", "author": "", "year": "", "url": "", "licence": "none in hand", "status": "not used", "date": CHECKED, "words": "none"},
        ],
    }
    b.write("assets/data/licences.json", json.dumps(data, ensure_ascii=False, indent=2))

def socials_file():
    if os.path.exists("assets/data/socials.json"):
        return
    payload = {
        "disclaimer": DISCLAIMER,
        "contact": CONTACT,
        "copyright": "© 2026 CypherMonkeyLabs 🐒",
        "labs": "CypherMonkey Labs",
        "icons": [
            {"id": "web", "icon": "monkey", "class": "brand-web", "label": "CypherMonkey Labs", "href": "https://cyphermonkeylabs.com"},
            {"id": "github", "icon": "github", "class": "brand-gh", "label": "GitHub organization", "href": "https://github.com/CypherMonkeyLabs"},
            {"id": "linktree", "icon": "linktree", "class": "brand-lt", "label": "Linktree", "href": "https://linktr.ee/cyphermonkey"},
            {"id": "x", "icon": "x", "class": "brand-x", "label": "X", "href": "https://x.com/Cypher0x9"},
            {"id": "linkedin", "icon": "linkedin", "class": "brand-li", "label": "LinkedIn", "href": "https://www.linkedin.com/in/luckylakshmanucwebex"},
            {"id": "huggingface", "icon": "huggingface", "class": "brand-hf", "label": "Hugging Face", "href": "https://huggingface.co/Cypher0x9"},
        ],
    }
    b.write("assets/data/socials.json", json.dumps(payload, ensure_ascii=False, indent=2))

def main():
    socials_file()
    licences()
    favicon()
    st = stats()
    items = diagrams(st)
    print("diagrams", len(items), "animated", sum(1 for i in items if i["animated"]))
    write_diagrams(items)
    pages = rooms(st, items)
    for spec in pages:
        if spec["file"] in {"diagrams.html", "charts.html", "downloads.html", "glossary.html", "credits.html", "about.html", "resources.html", "play.html", "listen.html", "ecosystem.html"}:
            continue
        b.write(spec["file"], shell_page(spec))
    cards = write_cards(st)
    write_sheets(st)
    write_templates()
    write_deck(st)
    write_models()
    other_pages(st, items, pages)
    offline()
    rows = catalogue(items)
    visual = items[0]
    write_catalog(rows)
    b.write("downloads.html", downloads_page([r for r in rows if r["kind"] != "bundle"], visual))
    rows = catalogue(items)
    write_catalog(rows)
    write_zip([r for r in rows if not r["path"].endswith(".zip")])
    rows = catalogue(items)
    write_catalog(rows)
    b.write("downloads.html", downloads_page(rows, visual))
    gloss = []
    for spec in list(pages) + EXTRA:
        if spec["file"] == "glossary.html":
            continue
        for term, defn in spec["glossary"]:
            gloss.append((term, defn, spec["file"]))
    glossary_page(gloss, visual)
    site_json(pages, cards, items)
    search_index(st, items, gloss)
    write_single_file()
    rows = catalogue(items)
    write_catalog(rows)
    write_zip([row for row in rows if not row["path"].endswith(".zip")])
    rows = catalogue(items)
    write_catalog(rows)
    b.write("downloads.html", downloads_page(rows, visual))
    print("pages written", len(pages), "library", len(EXTRA), "downloads", len(rows))

if __name__ == "__main__":
    main()
