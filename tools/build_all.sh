#!/bin/bash
# Rebuilds everything from the open data files. Run from build/tools. Reads ../../data (never modifies it).
set -e
cd "$(dirname "$0")"
python3 gen_content.py
python3 ../guidebot/gen_kb.py
python3 make_pdfs.py
python3 make_pptx.py
python3 make_assets.py
python3 make_manifest.py; python3 make_single.py; python3 make_manifest.py; python3 make_single.py; python3 make_manifest.py
python3 make_readme.py
echo build complete
