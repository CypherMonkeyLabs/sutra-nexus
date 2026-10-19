"""Give the standalone diagram pages (downloads/diagrams/*.html) the same
chrome as the rooms: large Menu, drawer, phone dock and the talking guide bot.
`add_chrome` is idempotent and prefixes every relative link with ../../ .
Run this file directly to upgrade the pages that are already on disk."""
import glob
import io
import re
import sys

PREFIX = "../../"
SCRIPTS = ("brand", "frame", "phone-nav", "app")


def _prefix_links(chunk):
    def fix(match):
        attr, url = match.group(1), match.group(2)
        if re.match(r"^(https?:|mailto:|tel:|#|/|data:|javascript:|\.\./)", url) or not url:
            return match.group(0)
        return '%s="%s%s"' % (attr, PREFIX, url)
    return re.sub(r'\b(href|src)="([^"]*)"', fix, chunk)


def chrome_from_page(page_html):
    """Cut the top and bottom chrome out of a built room page such as diagrams.html."""
    top = page_html[page_html.index('<a class="skip"'):page_html.index('<div class="page-scroll">')]
    bottom = page_html[page_html.index('<nav class="phone-dock"'):page_html.index('<div class="guide-root"></div>') + len('<div class="guide-root"></div>')]
    match = re.search(r'<script src="((?:\.\./)*)assets/js/boot\.js"></script>', page_html)
    if not match:
        raise SystemExit("room page is missing assets/js/boot.js")
    boot = '<script src="../../assets/js/boot.js"></script>'
    return top, bottom, boot


def add_chrome(html, top, bottom, boot):
    class_marker = 'class="guide-root"'
    if class_marker in html:
        return html
    head_add = '<link rel="icon" href="../../favicon.svg" type="image/svg+xml">'
    head, rest = html.split("</head>", 1)
    head = re.sub(r"<style>.*?</style>", boot + '\n<link rel="stylesheet" href="../../assets/css/sutra.css">', head, count=1, flags=re.S)
    html = head.replace("</title>", "</title>" + head_add, 1) + "</head>" + rest
    html = html.replace("<body>", '<body data-room="diagrams">\n' + _prefix_links(top) + '\n<div class="page-scroll">', 1)
    html = html.replace('<main class="main-wrap">', '<main id="main" class="main-wrap" tabindex="-1">', 1)
    scripts = "".join('<script src="%sassets/js/%s.js"></script>\n' % (PREFIX, name) for name in SCRIPTS)
    scripts += '<script type="module" src="%sassets/js/guide.js"></script>\n' % PREFIX
    html = html.replace("</body>", "</div>\n" + _prefix_links(bottom) + "\n" + scripts + "</body>", 1)
    return html


def upgrade_all(root="."):
    top, bottom, boot = chrome_from_page(io.open(root + "/diagrams.html", encoding="utf-8").read())
    count = 0
    for path in sorted(glob.glob(root + "/downloads/diagrams/*.html")):
        old = io.open(path, encoding="utf-8").read()
        new = add_chrome(old, top, bottom, boot)
        if new != old:
            io.open(path, "w", encoding="utf-8").write(new)
            count += 1
    return count


if __name__ == "__main__":
    print(upgrade_all(sys.argv[1] if len(sys.argv) > 1 else "."))
