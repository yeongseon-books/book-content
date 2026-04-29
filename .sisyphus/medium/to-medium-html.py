#!/usr/bin/env python3
"""Render medium/<NN>.md to medium/<NN>.html for browser-copy publishing.

Workflow:
1. Open medium/<NN>.html in Chrome/Chromium.
2. Ctrl+A, Ctrl+C.
3. Open a fresh empty Medium draft.
4. Click into the body, Ctrl+V.
5. Manually copy the trailing 'Tags: ...' line into Medium's tag input field
   (then delete the line from the body).

Why HTML and not raw markdown?
- Medium's web editor preserves rich text on paste from a rendered page:
  H1 -> title slot, headings, lists, blockquotes, code blocks, links.
- Pasting raw markdown shows literal '#' / '*' / '|' characters.

Image handling:
- Local images (`../../../assets/...`) are inlined as base64 `data:` URIs so
  the browser can render them. On paste, Medium MAY embed them; if not, the
  rendered <img> still tells the author which PNG to manually drag-drop.
- External images are kept as-is.

Table handling:
- 4+ col tables marked with the TODO PNG comment in the source markdown are
  rendered as native HTML <table>. Whether Medium preserves the table on
  paste is empirical (Oracle bg_2b10ce72 flagged this as the highest-risk
  element); the TODO marker stays as an HTML comment for the author.

This script is read-only on its inputs (medium/*.md). It writes only
medium/*.html alongside, and is idempotent.
"""

from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _catalog import is_present, load_catalog  # noqa: E402

MD_EXTENSIONS = [
    "fenced_code",
    "tables",
    "sane_lists",
    "nl2br",
]

NUMERIC_PREFIX_RE = re.compile(r"^(\d+)")
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)


def numeric_prefix(name: str) -> str | None:
    m = NUMERIC_PREFIX_RE.match(name)
    return m.group(1) if m else None


def inline_local_image(src: str, base_dir: Path) -> str:
    """Convert a local relative img src to a base64 data: URI; return original on failure."""
    if src.startswith(("http://", "https://", "data:")):
        return src
    candidate = (base_dir / src).resolve()
    if not candidate.is_file():
        return src
    mime, _ = mimetypes.guess_type(candidate.name)
    if not mime:
        mime = "application/octet-stream"
    payload = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def rewrite_image_srcs(html: str, base_dir: Path) -> str:
    def sub(m: re.Match) -> str:
        original = m.group(0)
        src = m.group(1)
        new_src = inline_local_image(src, base_dir)
        if new_src == src:
            return original
        return original.replace(f'src="{src}"', f'src="{new_src}"')

    return IMG_SRC_RE.sub(sub, html)


HTML_DOC_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  /* Preview-only styles. Medium strips CSS on paste; this is for
     the author's local preview in Chrome before copying. */
  body {{
    max-width: 720px;
    margin: 2rem auto;
    padding: 0 1rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 18px;
    line-height: 1.6;
    color: #292929;
  }}
  h1 {{ font-size: 2.4rem; line-height: 1.2; margin-top: 0; }}
  h2 {{ font-size: 1.6rem; margin-top: 2rem; }}
  h3 {{ font-size: 1.25rem; }}
  pre {{
    background: #f6f8fa;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 14px;
  }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.9em; }}
  pre code {{ font-size: 14px; }}
  table {{
    border-collapse: collapse;
    margin: 1rem 0;
    width: 100%;
    font-size: 0.95em;
  }}
  th, td {{ border: 1px solid #d0d7de; padding: 6px 12px; text-align: left; vertical-align: top; }}
  th {{ background: #f6f8fa; }}
  blockquote {{
    border-left: 3px solid #d0d7de;
    margin: 1rem 0;
    padding: 0 1rem;
    color: #57606a;
  }}
  img {{ max-width: 100%; height: auto; }}
  hr {{ border: none; border-top: 1px solid #d0d7de; margin: 2rem 0; }}
  .tags-line {{
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px dashed #d0d7de;
    color: #57606a;
    font-size: 0.95em;
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
TAGS_LINE_RE = re.compile(r"^Tags:\s*(.+?)\s*$", re.MULTILINE)


def extract_title(md_text: str) -> str:
    m = H1_RE.search(md_text)
    return m.group(1).strip() if m else "Untitled"


def render_md_to_html(md_path: Path) -> str:
    md_text = md_path.read_text(encoding="utf-8")
    title = extract_title(md_text)
    body_html = markdown.markdown(md_text, extensions=MD_EXTENSIONS, output_format="html5")
    body_html = rewrite_image_srcs(body_html, md_path.parent)
    # Highlight the tag line so the author notices it during copy-paste prep.
    body_html = re.sub(
        r"<p>Tags:\s*([^<]+)</p>",
        r'<p class="tags-line">Tags: \1</p>',
        body_html,
        count=1,
    )
    return HTML_DOC_TEMPLATE.format(title=title, body=body_html)


def process_series_medium_dir(medium_dir: Path) -> tuple[int, int]:
    written = 0
    skipped = 0
    for md in sorted(medium_dir.glob("*.md")):
        if not numeric_prefix(md.name):
            skipped += 1
            continue
        html = render_md_to_html(md)
        out_path = md.with_suffix(".html")
        out_path.write_text(html, encoding="utf-8")
        written += 1
    return written, skipped


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        medium_dirs = [Path(p).resolve() for p in argv[1:]]
    else:
        medium_dirs = [
            entry.path / "medium"
            for entry in load_catalog()
            if is_present(entry) and (entry.path / "medium").is_dir()
        ]
    total_w, total_s = 0, 0
    for medium_dir in medium_dirs:
        if not medium_dir.is_dir():
            print(f"SKIP missing dir: {medium_dir}")
            continue
        print(f"== {medium_dir.relative_to(ROOT)}")
        w, s = process_series_medium_dir(medium_dir)
        total_w += w
        total_s += s
        print(f"   wrote {w}, skipped {s}")
    print(f"\nTotal: wrote {total_w}, skipped {total_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
