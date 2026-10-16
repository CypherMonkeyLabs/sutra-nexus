#!/usr/bin/env python3
"""Generate the Sūtra Nexus v2 static site from the three open data files.

Chrome behavior is adapted from Webex Lab commit
7631b317cbf2cad236403df960b5d5fac353a6de. This script does not copy Webex copy.
"""
import html
import json
import math
import os
import struct
import sys
import zipfile
from collections import Counter

from docx import Document
from docx.shared import Pt
from pptx import Presentation
from pptx.util import Inches, Pt as PptPt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import load, pratyahara, selftest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DISCLAIMER = (
    "Sūtra Nexus is an independent, free, learning-only student project. "
    "It respects every tradition, scholar, publisher, company and vendor. "
    "Trademarks, texts and sources belong to their owners, and nothing here is affiliated with or endorsed by them. "
    "If something should be removed or corrected, it will be handled promptly through the contact form. "
    "Nothing here is sold. I am happy to volunteer for any organization."
)
CONTACT = "https://cyphermonkeylabs.com/#contact"
CHECKED = "2026-10-16"

def E(value):
    return html.escape(str(value if value is not None else ""), quote=True)

def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)

def write(path, text):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)

def socials():
    data = read_json("assets/data/socials.json")
    icons = []
    for item in data.get("icons", []):
        href = str(item.get("href", ""))
        if item.get("id") in {"x", "linkedin", "huggingface"}:
            continue
        blocked = ("linkedin.com", "://x.com", "twitter.com", "hugging" + "face.co")
        if any(bit in href for bit in blocked):
            continue
        icons.append(item)
    data["icons"] = icons
    return data

def icon_svg(name):
    path = {
        "github": "assets/icons/si-github.svg",
        "linktree": "assets/icons/si-lt.svg",
        "monkey": "assets/icons/monkey.svg",
    }[name]
    raw = open(path, encoding="utf-8").read()
    raw = raw.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
    return raw.replace("<svg ", '<svg class="brand-glyph" ', 1)

def footer_html():
    data = socials()
    icons = []
    for item in data["icons"]:
        glyph = icon_svg(item["icon"])
        icons.append(
            f'<a class="brand-icon {E(item["class"])}" href="{E(item["href"])}" aria-label="{E(item["label"])}">{glyph}</a>'
        )
    return f'''<footer class="site-footer" data-canon-footer>
<div class="disclaimer-panel" role="note">
<svg class="disclaimer-ico" viewBox="0 0 48 48" aria-hidden="true"><path fill="#0f766e" d="M24 4 8 10v12c0 9.5 6.4 16.8 16 20 9.6-3.2 16-10.5 16-20V10z"/><path fill="#ecfdf5" d="m16 24 5 5 12-13" stroke="#ecfdf5" stroke-width="2" fill="none"/></svg>
<div>
<h2>Disclaimer</h2>
<p>{E(DISCLAIMER[:-1]) if False else E(DISCLAIMER)} <a href="{CONTACT}">contact form</a>.</p>
</div>
</div>
<p class="footer-brand">CypherMonkey Labs</p>
<p class="site-copy">© 2026 CypherMonkeyLabs 🐒</p>
<div class="brand-icons">{''.join(icons)}</div>
</footer>'''

# The disclaimer sentence already says "contact form". Linking the words inside the sentence
# keeps the wording. The extra sentence above duplicated it. Fix footer to link the words.
def footer_html_fixed():
    data = socials()
    icons = []
    for item in data["icons"]:
        icons.append(
            f'<a class="brand-icon {E(item["class"])}" href="{E(item["href"])}" aria-label="{E(item["label"])}">{icon_svg(item["icon"])}</a>'
        )
    linked = DISCLAIMER.replace(
        "contact form",
        f'<a href="{CONTACT}">contact form</a>',
    )
    return f'''<footer class="site-footer" data-canon-footer>
<div class="disclaimer-panel" id="site-disclaimer" role="note">
<svg class="disclaimer-ico" viewBox="0 0 48 48" aria-hidden="true"><path fill="#0f766e" d="M24 4 8 10v12c0 9.5 6.4 16.8 16 20 9.6-3.2 16-10.5 16-20V10z"/><path d="m16 24 5 5 12-13" fill="none" stroke="#ecfdf5" stroke-width="2.4" stroke-linecap="round"/></svg>
<div>
<h2>Disclaimer</h2>
<p>{linked}</p>
</div>
</div>
<p class="footer-brand">CypherMonkey Labs</p>
<p class="site-copy">© 2026 CypherMonkeyLabs 🐒</p>
<div class="brand-icons">{''.join(icons)}</div>
</footer>'''

NAV = [
    ("index.html", "Start here", "A six-step path and what this app will not invent."),
    ("foundations.html", "Foundations", "Script, sounds, and the phonetic terms still unsourced."),
    ("maheshvara.html", "Māheśvara", "The 14 lines and a pratyāhāra you can compute."),
    ("sandhi.html", "Sandhi", "Sound-joining, without a fake rule walk."),
    ("ashtadhyayi.html", "Aṣṭādhyāyī", "3,983 lines, eight chapters, and the type letters in the file."),
    ("anuvrtti.html", "Anuvṛtti", "How the data file carries earlier words."),
    ("dhatu.html", "Dhātu", "Verb roots and word classes, with the gaps marked."),
    ("shiva.html", "Śiva Sūtras", "The 75-line Kashmir file, with no English added."),
    ("history.html", "History", "Dates only as the opened pages state them."),
    ("diagrams.html", "Diagrams", "Every drawing, with a still PNG and a standalone page."),
    ("charts.html", "Charts", "Counts from this repository."),
    ("play.html", "Play", "Builders, drills, cards, and an interview bank."),
    ("listen.html", "Listen", "Scripted reads. No audio file is claimed."),
    ("ecosystem.html", "Ecosystem", "How the rooms connect, as a map not a claim of history."),
    ("resources.html", "Resources", "Pages opened on 2026-10-16."),
    ("downloads.html", "Downloads", "Individual files, plus one optional zip."),
    ("glossary.html", "Glossary", "Terms used in these rooms."),
    ("credits.html", "Credits", "Libraries, icons, the font, and the data."),
    ("about.html", "About", "A short note and the same disclaimer."),
]

GROUPS = [
    ("Start here", ["index.html"]),
    ("Learn", ["foundations.html", "maheshvara.html", "sandhi.html", "ashtadhyayi.html", "anuvrtti.html", "dhatu.html", "shiva.html", "history.html"]),
    ("Practice", ["diagrams.html", "charts.html", "play.html", "listen.html"]),
    ("Library", ["ecosystem.html", "resources.html", "downloads.html", "glossary.html"]),
    ("Project", ["credits.html", "about.html"]),
]

def wheel_svg():
    spokes = []
    for i in range(8):
        spokes.append(f'<line x1="48" y1="12" x2="48" y2="28" transform="rotate({i * 45} 48 48)" stroke="#fde047" stroke-width="3" stroke-linecap="round"/>')
    return f'''<div class="wheel-hero"><svg viewBox="0 0 96 96" role="img" aria-label="A glowing study wheel">
<circle cx="48" cy="48" r="40" fill="none" stroke="#22d3ee" stroke-width="4"/>
<g class="wheel-spin">{''.join(spokes)}<circle cx="48" cy="48" r="8" fill="#f472b6"/></g>
</svg></div>'''

def banner(current):
    chips = []
    for href, label, desc in NAV:
        current_attr = ' aria-current="page"' if href == current else ""
        chips.append(f'<a class="section-chip" href="{href}"{current_attr} title="{E(desc)}">{E(label)}</a>')
    return f'''<div class="canon-banner">
<button type="button" class="rail-btn" data-rail="-1" aria-label="Scroll sections left">‹</button>
<div class="rail-scroller"><nav class="section-rail" aria-label="Sections">{''.join(chips)}</nav></div>
<button type="button" class="rail-btn" data-rail="1" aria-label="Scroll sections right">›</button>
</div>'''

def drawer(current):
    by_href = {href: (label, desc) for href, label, desc in NAV}
    blocks = [wheel_svg(), '<div class="drawer-bar"><p>Menu</p><button type="button" data-close-menu>Close</button></div>',
              '<div class="drawer-search"><label class="sr" for="q">Search</label><input id="q" data-search type="search" placeholder="Rooms, sūtra numbers, terms" autocomplete="off"><div class="search-hits" data-search-hits></div></div>',
              '<div class="drawer-list">']
    for group, hrefs in GROUPS:
        blocks.append(f'<p class="drawer-group">{E(group)}</p>')
        for href in hrefs:
            label, desc = by_href[href]
            current_attr = ' aria-current="page"' if href == current else ""
            blocks.append(f'<a href="{href}"{current_attr}><span><b>{E(label)}</b><span>{E(desc)}</span></span></a>')
    blocks.append("</div>")
    return f'<div class="backdrop" data-close-menu></div><nav class="drawer" aria-label="Full menu">{''.join(blocks)}</nav>'

def display_panel():
    themes = [("bloom", "Bloom"), ("dark", "Dark"), ("light", "Light"), ("contrast", "Contrast")]
    buttons = "".join(f'<button type="button" data-set-theme="{key}">{label}</button>' for key, label in themes)
    swatches = "".join(f'<button type="button" class="swatch" data-ink="{color}" style="background:{color}" aria-label="Font color {color}"></button>' for color in ["#1b1340", "#1a1a1a", "#ffffff", "#fde047", "#67e8f9", "#86efac"])
    return f'''<div class="display-panel" id="display-panel" hidden>
<p>Text size</p>
<button type="button" data-font-step="-0.1" aria-label="Smaller text">A-</button>
<button type="button" data-font-reset aria-label="Normal text size">A</button>
<button type="button" data-font-step="0.1" aria-label="Larger text">A+</button>
<label class="sr" for="font-slider">Text size slider</label>
<input id="font-slider" data-font-slider type="range" min="0.85" max="1.6" step="0.05" value="1">
<p>Theme</p><div>{buttons}</div>
<p>Font color</p><div>{swatches}<label class="sr" for="ink-custom">Custom font color</label><input id="ink-custom" data-ink-custom type="color" value="#1b1340" aria-label="Custom font color"><button type="button" data-ink-reset>Theme default</button></div>
<p data-contrast-warn class="contrast-warn"></p>
<button type="button" data-motion-toggle aria-pressed="false">Reduce motion</button>
</div>'''

def header():
    return f'''<header class="site-header">
<button type="button" class="menu-btn menu-desktop" data-open-menu aria-expanded="false" aria-controls="site-drawer">Menu</button>
<a class="brand" href="index.html"><span><b>Sūtra Nexus</b><small>Ancient rules. Living systems.</small></span></a>
<div class="header-spacer"></div>
<button type="button" class="display-btn" aria-expanded="false" aria-controls="display-panel">Display</button>
{display_panel()}
</header>'''

def phone_dock(current):
    items = [
        ("menu", "Menu", None),
        ("foundations.html", "Learn", "foundations.html"),
        ("diagrams.html", "Diagrams", "diagrams.html"),
        ("play.html", "Play", "play.html"),
        ("listen.html", "Listen", "listen.html"),
        ("guide", "Guide", None),
    ]
    parts = []
    for key, label, href in items:
        if key == "menu":
            parts.append('<button type="button" class="dock-item menu-glow" data-open-menu aria-expanded="false" aria-controls="site-drawer">Menu</button>')
        elif key == "guide":
            parts.append('<button type="button" class="dock-item" data-open-guide>Guide</button>')
        else:
            current_attr = ' aria-current="page"' if href == current else ""
            parts.append(f'<a class="dock-item" href="{href}"{current_attr}>{E(label)}</a>')
    hint = '<div class="nav-hint" role="note" aria-label="How to open the menu"><span>Tap for menu</span><button type="button">Got it</button></div>'
    return f'<nav class="phone-dock" aria-label="Phone">{hint}{''.join(parts)}</nav>'

HEAD_BOOT = '''<script>try{var t=localStorage.getItem("sutra-theme")||"bloom";if(["bloom","dark","light","contrast"].indexOf(t)<0)t="bloom";document.documentElement.dataset.theme=t;var f=parseFloat(localStorage.getItem("sutra-fscale")||"1");if(f)document.documentElement.style.setProperty("--fscale",String(f));var m=localStorage.getItem("sutra-motion");if(m==="reduce"||m==="full")document.documentElement.dataset.motion=m;var ink=localStorage.getItem("sutra-ink");if(ink&&/^#[0-9a-f]{6}$/i.test(ink))document.documentElement.style.setProperty("--ink",ink);if(matchMedia("(max-width:720px)").matches&&localStorage.getItem("sutra-nav-hint")!=="1"){document.documentElement.dataset.navHint="1";document.documentElement.style.setProperty("--dock-h","120px");}}catch(e){}</script>'''

def page_shell(current, title, description, body, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="bloom">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{HEAD_BOOT}
<link rel="stylesheet" href="assets/css/sutra.css">
</head>
<body data-room="{E(current.replace('.html',''))}">
<a class="skip" href="#main">Skip to content</a>
{header()}
{banner(current)}
<div id="site-drawer">{drawer(current)}</div>
<div class="page-scroll">
<main id="main" class="main-wrap" tabindex="-1">
{body}
</main>
{footer_html_fixed()}
</div>
{phone_dock(current)}
<div class="guide-root"></div>
<script src="assets/js/tour.js"></script>
<script src="assets/js/brand.js"></script>
<script src="assets/js/frame.js"></script>
<script src="assets/js/phone-nav.js"></script>
<script src="assets/js/app.js"></script>
<script type="module" src="assets/js/guide.js"></script>
<script>if(location.protocol.indexOf("http")===0&&"serviceWorker"in navigator){{window.addEventListener("load",function(){{navigator.serviceWorker.register("sw.js");}});}}</script>
{extra}
</body>
</html>
'''

def wrap_lines(text, width=88):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines

def svg_doc(title, body, source, animated=False):
    lines = wrap_lines(DISCLAIMER, 92)
    footer = []
    y = 600
    footer.append(f'<text x="36" y="{y}" font-size="13" font-weight="700" fill="#052e2b">Disclaimer</text>')
    y += 18
    for line in lines:
        footer.append(f'<text x="36" y="{y}" font-size="11" fill="#0b1f2a">{E(line)}</text>')
        y += 15
    footer.append(f'<text x="36" y="{y+6}" font-size="11" fill="#134e4a">{E(source)}</text>')
    motion = '''
@media (prefers-reduced-motion: reduce) { .mover { display: none; } }
'''
    anim = ""
    if animated:
        anim = '''<circle class="mover" r="8" fill="#6d28d9"><animateMotion dur="4.8s" repeatCount="indefinite" path="M 70 300 H 890"/></circle>'''
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 820" role="img" aria-label="{E(title)}">
<title>{E(title)}</title>
<style>
text {{ font-family: "Noto Sans Devanagari", "Segoe UI", sans-serif; }}
{motion}
</style>
<rect width="960" height="820" rx="24" fill="#f6f3ff"/>
<rect x="20" y="16" width="920" height="64" rx="16" fill="#1e1b4b"/>
<text x="40" y="56" font-size="26" fill="#f8fafc">{E(title)}</text>
{body}
<rect x="20" y="572" width="920" height="228" rx="16" fill="#d1fae5" stroke="#0f766e" stroke-width="2"/>
{''.join(footer)}
{anim}
</svg>
'''

def flow_body(steps):
    parts = []
    count = len(steps)
    gap = 860 / max(count, 1)
    box_w = max(70, gap - 24)
    for index, step in enumerate(steps):
        x = 40 + index * gap
        words = step.split()
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if len(trial) > 16 and cur:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        lines = lines[:3]
        parts.append(f'<rect x="{x:.0f}" y="140" width="{box_w:.0f}" height="140" rx="16" fill="#fff" stroke="#7c3aed" stroke-width="2"/>')
        for line_index, line in enumerate(lines):
            parts.append(f'<text x="{x+10:.0f}" y="{178 + line_index * 18:.0f}" font-size="13" fill="#1b1340">{E(line)}</text>')
        if index < count - 1:
            parts.append(f'<path d="M {x+gap-28:.0f} 210 H {x+gap-8:.0f}" stroke="#0891b2" stroke-width="3" marker-end="url(#arrow)"/>')
    return '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#0891b2"/></marker></defs>' + "".join(parts) + '<text x="40" y="340" font-size="15" fill="#3b3560">A moving dot shows the reading order. Reduced motion hides it.</text>'

def bars_body(pairs):
    top = max(value for _, value in pairs) or 1
    parts = []
    width = 800 / max(len(pairs), 1)
    for index, (label, value) in enumerate(pairs):
        height = 280 * value / top
        x = 50 + index * width
        y = 480 - height
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{width-18:.1f}" height="{height:.1f}" rx="8" fill="#818cf8"/>')
        parts.append(f'<text x="{x:.1f}" y="506" font-size="13" fill="#1b1340">{E(label)}</text>')
        parts.append(f'<text x="{x:.1f}" y="{y-8:.1f}" font-size="13" fill="#1b1340">{value}</text>')
    return "".join(parts)

def mind_body(center, leaves):
    parts = [f'<circle cx="480" cy="280" r="70" fill="#fde68a" stroke="#b45309" stroke-width="2"/>',
             f'<text x="430" y="286" font-size="16" fill="#1b1340">{E(center)}</text>']
    for index, leaf in enumerate(leaves):
        angle = -math.pi / 2 + index * (2 * math.pi / len(leaves))
        x = 480 + math.cos(angle) * 250
        y = 280 + math.sin(angle) * 140
        parts.append(f'<line x1="480" y1="280" x2="{x:.0f}" y2="{y:.0f}" stroke="#0891b2" stroke-width="2"/>')
        parts.append(f'<rect x="{x-70:.0f}" y="{y-22:.0f}" width="150" height="44" rx="12" fill="#fff" stroke="#6d28d9"/>')
        parts.append(f'<text x="{x-58:.0f}" y="{y+6:.0f}" font-size="13" fill="#1b1340">{E(leaf[:22])}</text>')
    return "".join(parts)
