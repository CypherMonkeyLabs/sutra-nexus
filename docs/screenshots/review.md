# Screenshot review

Served from `node scripts/gzip-static.mjs` on `http://127.0.0.1:8742/`. Sizes are 1440×900 and 390×844.

## What was wrong in the first shots (`before/`)

- The phone guide button floated over the lesson text and over the “Tap for menu” hint. The dock already has Guide, so the extra button was removed on narrow screens.
- The guide sheet was tall enough to cover the page heading, and the hint sat on top of the sheet.
- Diagram step labels were clipped inside the boxes.
- On a phone, the first-visit hint covered the disclaimer and the brand icons when the footer was on screen.

## What the later shots show (`after/`)

- Home, a room, and Downloads keep one banner row. Chips scroll; they do not wrap.
- The phone dock is Menu, Learn, Diagrams, Play, Listen, Guide. The hint sits above Menu and hides when the footer is on screen.
- The guide sheet on a phone leaves the heading readable. Desktop keeps the round guide button in the side margin.
- The disclaimer, the copyright line, and the six brand icons sit above the phone dock.
- Menu open shows the wheel, the search field, and the section list, with a transform drawer.

Lighthouse mobile, gzip static server, 2026-10-16: home, Māheśvara, and Downloads each scored performance 100, accessibility 100, best practices 100, SEO 100. Cumulative layout shift was 0. Desktop home matched those scores.

## Review of 52b3801, fixed on this branch

- The X footer icon was a black path on a black tile. `.brand-icon svg` now uses `fill: currentColor`. The six footer glyphs measure as visible shapes: monkey, GitHub, Linktree, white X, LinkedIn, Hugging Face.
- HTML downloads inline the stylesheet and the drawing. `downloads/sutra-nexus-single-file.html` is the study app in one file and is inside the optional zip.
- The first-run hint is a one-line pill inside the phone bar. The lead stays readable. On a phone the page scrolls above that bar.
- Downloads are 16 collapsed room sections. One section starts open. Closed sections do not lay out their thumbnails.
- simpleicons.org and notofonts are named in Credits without links. Cited sources stay in the Sources block.
- Desktop menu open keeps the heading whole, to the right of the drawer. Desktop guide open shows the welcome and does not cover the heading. Shots: `docs/screenshots/after/menu-open-1440.png`, `guide-open-1440.png`, `hint-390.png`, `footer-icons-1440.png`, `downloads-groups-390.png`.
