#!/usr/bin/env python3
"""Render a SOMA-Codex book: inline local images as base64, convert HTML -> ODT,
verify the ODT embeds pictures and carries a heading outline.

Usage: python3 build.py <book.html>
Output: artifacts/odt/<book>.odt
"""
import base64, os, re, subprocess, sys, tempfile, zipfile

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, "artifacts", "odt")


def inline_images(html, base):
    def repl(m):
        path = m.group(1)
        if path.startswith("data:") or path.startswith("http"):
            return m.group(0)
        full = os.path.join(base, path)
        with open(full, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return 'src="data:image/png;base64,%s"' % b64
    return re.sub(r'src="([^"]+\.png)"', repl, html)


def main():
    os.makedirs(OUT, exist_ok=True)
    book = sys.argv[1]
    book_path = os.path.join(SRC, book)
    html = open(book_path, encoding="utf-8").read()
    # inline <!--INCLUDE:fragment.html--> fragments
    def _inc(m):
        frag = os.path.join(SRC, m.group(1).strip())
        return open(frag, encoding="utf-8").read()
    html = re.sub(r'<!--INCLUDE:([^>]+?)-->', _inc, html)
    # LibreOffice's HTML import fragments <div> backgrounds per wrapped line, so
    # render callout/invariant/openq boxes as single-cell tables (cell shading imports cleanly).
    # inline styles only — LibreOffice ignores class/compound selectors for cell shading
    BOX = {"callout":   ("#fff7ec", "#c8851a"),
           "invariant": ("#eef6f0", "#1f7a44"),
           "openq":     ("#f3eefb", "#6b4fa0")}
    def _box(m):
        bg, bd = BOX[m.group(1)]
        return ('<table style="border-collapse:collapse;width:100%%;margin:11pt 0">'
                '<tr><td style="background-color:%s;border:1.5px solid %s;padding:9px 13px">'
                '%s</td></tr></table>' % (bg, bd, m.group(2)))
    html = re.sub(r'<div class="(callout|invariant|openq)">(.*?)</div>', _box, html,
                  flags=re.DOTALL)
    # LibreOffice honors the HTML border attribute + bgcolor, but not CSS table borders.
    # Box tables are emitted as <table style=...> above, so the plain-<table> swap skips them.
    html = html.replace('<table>',
        '<table border="1" cellpadding="6" cellspacing="0" '
        'style="border-collapse:collapse;width:100%">')
    html = html.replace('<th>', '<th bgcolor="#eaf2ff">')
    css_path = os.path.join(SRC, "style.css")
    if "<!--SOMA_STYLE-->" in html and os.path.exists(css_path):
        css = open(css_path, encoding="utf-8").read()
        html = html.replace("<!--SOMA_STYLE-->", "<style>\n" + css + "\n</style>")
    html = inline_images(html, SRC)
    with tempfile.TemporaryDirectory() as td:
        tmp_html = os.path.join(td, book)
        open(tmp_html, "w", encoding="utf-8").write(html)
        lo_profile = os.path.join(td, "lo-profile")
        env = os.environ.copy()
        env["HOME"] = td
        env["XDG_CONFIG_HOME"] = os.path.join(td, "config")
        env["XDG_CACHE_HOME"] = os.path.join(td, "cache")
        env["XDG_RUNTIME_DIR"] = td
        subprocess.run([
            "soffice",
            "--headless",
            f"-env:UserInstallation=file://{lo_profile}",
            "--convert-to",
            "odt",
            "--outdir",
            td,
            tmp_html,
        ], check=True, env=env)
        odt_name = os.path.splitext(book)[0] + ".odt"
        tmp_odt = os.path.join(td, odt_name)
        final = os.path.join(OUT, odt_name)
        os.replace(tmp_odt, final)
    # verify
    with zipfile.ZipFile(final) as z:
        names = z.namelist()
        content = z.read("content.xml").decode("utf-8", "ignore")
    pics = [n for n in names if n.startswith("Pictures/")]
    imgs_in_html = html.count("data:image/png")
    outline = len(re.findall(r'text:outline-level="[0-9]"', content))
    tables = content.count("<table:table ")
    size_kb = os.path.getsize(final) // 1024
    print("OK  %-34s  %4dKB  pics=%d/%d  outline=%d  tables=%d"
          % (odt_name, size_kb, len(pics), imgs_in_html, outline, tables))
    if imgs_in_html and not pics:
        print("WARNING: images present in HTML but none embedded in ODT")


if __name__ == "__main__":
    main()
