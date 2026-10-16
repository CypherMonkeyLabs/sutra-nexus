# Sūtra Nexus

A free study desk for three open files: **3,983** Aṣṭādhyāyī rows, **14** Māheśvara lines, and **75** Kashmir Śiva Sūtras. Ancient rules. Living systems.

[Open app](https://cyphermonkeylabs.com/sutra-nexus/) · [View repo](https://github.com/CypherMonkeyLabs/sutra-nexus)

The canonical site is GitHub Pages at `cyphermonkeylabs.com/sutra-nexus/`. Links inside the app are relative, so the same files work under that folder. This README is the short door. The app itself holds the lessons.

## What you can do

Read a room, compute a pratyāhāra, take a quiz, and download one file. The guide repeats only what the pages say. Voice is off until you turn it on.

## Counts you can check

| File | Rows |
| --- | --- |
| `data/ashtadhyayi.json` | 3,983 |
| `data/maheshvara.json` | 14 |
| `data/shiva_sutras_kashmir.json` | 75 |

Drawings: 58, of which 36 have a moving dot. Downloads are listed one by one, plus one optional zip. `downloads/sutra-nexus-single-file.html` is the study app in one file, and that file is inside the zip.

Measured on 2026-10-16 with `node scripts/gzip-static.mjs` (gzip for text responses) at `http://127.0.0.1:8742/`. Mobile Lighthouse on Home, Māheśvara, and Downloads: performance 100, accessibility 100, best practices 100, SEO 100, cumulative layout shift 0. Desktop Home matched those scores.

## Chrome

The banner, drawer, phone dock, and footer behavior are adapted from Webex Lab commit `7631b317cbf2cad236403df960b5d5fac353a6de`. Webex and Cisco product copy is not used.

## Gaps

- English meanings are not included. The licence for an English rendering was not confirmed. Each line says: meaning: not yet sourced from an open text.
- IAST in the Aṣṭādhyāyī file is script-converted, not yet human-checked. The Kashmir file's own note treats its IAST as the GRETIL e-text and its Devanāgarī as machine-converted.
- Type letters AT and AD are not expanded. Confirm before relying.
- There is no sthāna or prayatna chart, and no invented sandhi join.
- The Kashmir meta note trails off at 22+10+45. Which lines differ is unknown.
- The 1-minute, 10-minute, and 1-hour pieces are scripts, not videos or recordings.
- d3, markmap, and confetti are vendored and not loaded. The 3D models are simple original boxes.

<div class="disclaimer-panel">

**Disclaimer.** Sūtra Nexus is an independent, free, learning-only student project. It respects every tradition, scholar, publisher, company and vendor. Trademarks, texts and sources belong to their owners, and nothing here is affiliated with or endorsed by them. If something should be removed or corrected, it will be handled promptly through the [contact form](https://cyphermonkeylabs.com/#contact). Nothing here is sold. I am happy to volunteer for any organization.

</div>

CypherMonkey Labs

© 2026 CypherMonkeyLabs 🐒

[![CypherMonkey Labs](assets/icons/monkey.svg)](https://cyphermonkeylabs.com)
[![GitHub](assets/icons/si-github.svg)](https://github.com/CypherMonkeyLabs)
[![Linktree](assets/icons/si-lt.svg)](https://linktr.ee/cyphermonkey)
[![X](assets/icons/si-x.svg)](https://x.com/Cypher0x9)
[![LinkedIn](assets/icons/si-li.svg)](https://www.linkedin.com/in/luckylakshmanucwebex)
[![Hugging Face](assets/icons/si-hf.svg)](https://huggingface.co/Cypher0x9)
