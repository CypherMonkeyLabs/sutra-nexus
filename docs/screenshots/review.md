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
