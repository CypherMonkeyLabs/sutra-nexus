#!/usr/bin/env python3
"""Check every download for the disclaimer, then open HTML and SVG in headless Chrome."""
import glob
import json
import os
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor

from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NEEDLE = "Sūtra Nexus is an independent, free, learning-only student project."
report = {"checked": [], "failed": []}

def fail(path, reason):
    report["failed"].append({"path": path, "reason": reason})

def ok(path, kind):
    report["checked"].append({"path": path, "kind": kind})

def text_has(path, text):
    if NEEDLE not in text:
        fail(path, "disclaimer missing")
    else:
        ok(path, "text")

for path in glob.glob("downloads/**/*", recursive=True):
    if not os.path.isfile(path) or path.endswith(".zip"):
        continue
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in {".html", ".svg", ".txt", ".json"}:
            text_has(path, open(path, encoding="utf-8").read())
        elif ext == ".pdf":
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            text_has(path, text)
        elif ext == ".docx":
            with zipfile.ZipFile(path) as zf:
                xml = zf.read("word/document.xml") + zf.read("word/footer1.xml") if "word/footer1.xml" in zf.namelist() else zf.read("word/document.xml")
            text_has(path, xml.decode("utf-8", "replace"))
        elif ext == ".pptx":
            with zipfile.ZipFile(path) as zf:
                blobs = [zf.read(name) for name in zf.namelist() if name.startswith("ppt/slides/slide")]
            text_has(path, b"".join(blobs).decode("utf-8", "replace"))
        elif ext == ".glb":
            data = open(path, "rb").read()
            if not data.startswith(b"glTF"):
                fail(path, "missing glTF magic")
            else:
                text_has(path, data.decode("utf-8", "replace"))
        elif ext == ".png":
            ok(path, "png-bytes")
        else:
            ok(path, "other")
    except Exception as exc:
        fail(path, str(exc))

zip_path = "downloads/sutra-nexus-all.zip"
with zipfile.ZipFile(zip_path) as zf:
    names = zf.namelist()
    if "README.txt" not in names:
        fail(zip_path, "readme missing")
    else:
        text_has(zip_path + "#README.txt", zf.read("README.txt").decode("utf-8"))
    if any(name.endswith(".zip") for name in names):
        fail(zip_path, "nested zip")
    for name in names:
        if name == "README.txt":
            continue
        if not os.path.isfile(name):
            fail(zip_path, "listed file missing on disk " + name)

chrome = os.environ.get("CHROME", "google-chrome")
htmls = sorted(glob.glob("downloads/**/*.html", recursive=True) + glob.glob("downloads/**/*.svg", recursive=True))
os.makedirs("/tmp/sutra-dom", exist_ok=True)

def dump_one(item):
    index, path = item
    url = "file://" + os.path.abspath(path)
    proc = subprocess.run(
        ["timeout", "4", chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--user-data-dir=/tmp/sutra-chrome-{index}", f"--remote-debugging-port={9400 + index}",
         "--virtual-time-budget=1200",
         "--dump-dom", url],
        capture_output=True,
    )
    dumped = proc.stdout.decode("utf-8", "replace")
    if path.endswith(".html") and NEEDLE not in dumped:
        return path, "headless html missing disclaimer"
    if not dumped.strip():
        return path, "headless dump empty"
    return path, ""

with ThreadPoolExecutor(max_workers=4) as pool:
    for path, reason in pool.map(dump_one, list(enumerate(htmls))):
        if reason:
            fail(path, reason)
        else:
            ok(path, "headless")

os.makedirs("docs", exist_ok=True)
json.dump(report, open("docs/download-test.json", "w", encoding="utf-8"), indent=2)
print("checked", len(report["checked"]), "failed", len(report["failed"]))
if report["failed"]:
    print(json.dumps(report["failed"][:12], indent=2))
    sys.exit(1)
