"""Build the revision guide PDF from the Markdown sources in src/.

Usage: python build.py   (requires: pip install markdown pygments; node + playwright)
"""
import re
import subprocess
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).parent
SRC = ROOT / "src"
THEORY = ROOT / "theory"
HTML_OUT = ROOT / "build" / "guide.html"
PDF_OUT = ROOT / "Full-Stack-Revision-Guide.pdf"

CSS = """
@page { size: A4; margin: 18mm 15mm 18mm 15mm; }
body { font-family: 'DejaVu Sans', 'Helvetica', Arial, sans-serif; font-size: 10.2pt;
       line-height: 1.5; color: #1f2328; }
h1 { font-size: 24pt; color: #0b3d91; border-bottom: 3px solid #0b3d91; padding-bottom: 6px;
     page-break-before: always; margin-top: 0; }
h2 { font-size: 15pt; color: #0b3d91; margin-top: 22px; border-bottom: 1px solid #d0d7de;
     padding-bottom: 3px; page-break-after: avoid; }
h3 { font-size: 12pt; color: #24292f; margin-top: 16px; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
code { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 8.6pt;
       background: #f0f3f6; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-left: 4px solid #0b3d91;
      border-radius: 4px; padding: 8px 10px; white-space: pre-wrap; word-wrap: break-word;
      font-size: 8.3pt; line-height: 1.38; }
pre code { background: none; padding: 0; font-size: inherit; }
.codehilite { background: none; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #d0d7de; padding: 4px 7px; text-align: left; vertical-align: top; }
th { background: #e8eef9; }
tr:nth-child(even) td { background: #fafbfc; }
blockquote { border-left: 4px solid #d0d7de; margin: 8px 0; padding: 2px 12px; color: #57606a; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center;
         text-align: center; }
.cover h1 { page-break-before: avoid; border: none; font-size: 32pt; }
.cover .sub { font-size: 14pt; color: #57606a; margin-top: 8px; }
.cover .topics { margin-top: 40px; font-size: 12pt; line-height: 2; }
.toc h1 { page-break-before: always; }
.toc ul { list-style: none; padding-left: 0; }
.toc li.l1 { font-weight: bold; margin-top: 8px; }
.toc li.l2 { padding-left: 18px; font-size: 9.5pt; }
.toc a { color: #1f2328; text-decoration: none; }
.theory { background: #eef4ff; border: 1px solid #c6d7f5; border-left: 5px solid #2f6fdb;
          border-radius: 6px; padding: 4px 14px 6px 14px; margin: 10px 0 16px 0; }
.theory .label { font-weight: bold; color: #2f6fdb; font-size: 9pt; text-transform: uppercase;
                 letter-spacing: 0.5px; margin: 8px 0 2px 0; }
.theory pre { background: #fbfcff; }
.theory table { background: #fff; }
"""

COVER = """
<div class="cover">
  <h1>Full-Stack Developer<br>Revision Guide</h1>
  <div class="sub">Basics to Advanced — beginner-friendly explanations with coding examples</div>
  <div class="topics">
    JavaScript (ES2024+) &nbsp;•&nbsp; TypeScript<br>
    React (18 / 19) &nbsp;•&nbsp; Node.js &amp; Express<br>
    Python &nbsp;•&nbsp; Django &amp; Django REST Framework<br>
    SQL (PostgreSQL / MySQL)
  </div>
</div>
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_theory() -> dict[str, str]:
    """Parse theory/*.md files: sections start with '== <key>' (e.g. '== 1.4' or '== intro')."""
    theory = {}
    for path in sorted(THEORY.glob("*.md")):
        part = path.name.split("-")[0].lstrip("0") or "0"
        for chunk in re.split(r"^== ", path.read_text(), flags=re.M)[1:]:
            key, _, body = chunk.partition("\n")
            key = key.strip()
            theory[f"{part}:intro" if key == "intro" else key] = body.strip()
    return theory


def inject_theory(md_text: str, theory: dict[str, str], blocks: list[str]) -> str:
    """Place a placeholder paragraph for each theory block right after its heading."""
    out = []
    for line in md_text.splitlines():
        out.append(line)
        key = None
        if m := re.match(r"^# Part (\d+)\b", line):
            key = f"{m.group(1)}:intro"
        elif m := re.match(r"^## (\d+\.\d+) ", line):
            key = m.group(1)
        if key and key in theory:
            blocks.append(theory.pop(key))
            out += ["", f"THEORYBLOCK{len(blocks) - 1}", ""]
    if theory:
        raise SystemExit(f"Unused theory sections: {sorted(theory)}")
    return "\n".join(out)


def render_theory(blocks: list[str], body: str) -> str:
    for i, block in enumerate(blocks):
        html = markdown.markdown(
            block,
            extensions=["fenced_code", "tables", "codehilite", "sane_lists"],
            extension_configs={"codehilite": {"guess_lang": False, "css_class": "codehilite"}},
        )
        box = f'<div class="theory"><div class="label">Understand the concept</div>{html}</div>'
        body = body.replace(f"<p>THEORYBLOCK{i}</p>", box)
    return body


def build_html() -> str:
    md_text = "\n\n".join(p.read_text() for p in sorted(SRC.glob("*.md")))
    blocks: list[str] = []
    md_text = inject_theory(md_text, load_theory(), blocks)
    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "codehilite", "toc", "sane_lists"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"slugify": lambda value, sep: slugify(value), "toc_depth": "1-2"},
        },
    )
    body = render_theory(blocks, md.convert(md_text))

    toc_items = []
    for token in md.toc_tokens:
        toc_items.append(f'<li class="l1"><a href="#{token["id"]}">{token["name"]}</a></li>')
        for child in token["children"]:
            toc_items.append(f'<li class="l2"><a href="#{child["id"]}">{child["name"]}</a></li>')
    toc = f'<div class="toc"><h1>Table of Contents</h1><ul>{"".join(toc_items)}</ul></div>'

    pygments_css = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Full-Stack Revision Guide</title>"
        f"<style>{CSS}\n{pygments_css}</style></head><body>"
        f"{COVER}{toc}{body}</body></html>"
    )


def main():
    HTML_OUT.parent.mkdir(exist_ok=True)
    HTML_OUT.write_text(build_html())
    subprocess.run(["node", str(ROOT / "render.js"), str(HTML_OUT), str(PDF_OUT)], check=True)
    print(f"Wrote {PDF_OUT}")


if __name__ == "__main__":
    main()
