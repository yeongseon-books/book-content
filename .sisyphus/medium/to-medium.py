#!/usr/bin/env python3
"""Convert en/*.md to Medium import-ready medium/<NN>.md.

Rules (confirmed by user):
- Image refs `![alt](../../assets/...)` -> kept as-is (relative local path).
  Medium import does not fetch private-repo raw URLs, so PNGs are uploaded
  manually via Medium's UI (drag-and-drop). The local path doubles as a
  reference so the author knows which PNG to attach where.
- Other relative links `[text](../something)` or `[text](./something)` -> github.com/<owner>/<repo>/blob/<TAG>/<resolved>
- H3+ (### and deeper) -> bold paragraph (`**text**`)
- Tables -> bullet list, each row: "- **col1**: v1 / **col2**: v2 ..."
- Code fences left as-is
- Front matter (YAML between ---) stripped
- TOC marker comments (<!-- toc:begin --> / <!-- toc:end -->) removed
- Trailing `Tags: ...` line removed; surfaced as leading <!-- Tags: ... --> comment
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

_meta = yaml.safe_load((ROOT / "series.yaml").read_text(encoding="utf-8")).get("meta") or {}
if "repo" not in _meta or "published_ref" not in _meta:
    raise SystemExit(
        "series.yaml is missing meta.repo or meta.published_ref. Both are "
        "required to build the immutable raw URLs that get baked into "
        "Medium articles. Add a top-level meta: {repo, published_ref} block."
    )
REPO = _meta["repo"]
TAG = _meta["published_ref"]

from _catalog import is_present, load_catalog

BLOB_BASE = f"https://github.com/{REPO}/blob/{TAG}"

FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{3,6})\s+(.*)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)
TOC_BEGIN_RE = re.compile(r"^<!--\s*toc:begin\s*-->\s*$", re.MULTILINE)
TOC_END_RE = re.compile(r"^<!--\s*toc:end\s*-->\s*$", re.MULTILINE)
TAGS_LINE_RE = re.compile(r"^Tags:\s*(.+?)\s*$", re.MULTILINE)


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1)


def resolve_relative(src_md: Path, target: str) -> str | None:
    """Resolve a relative path from src_md's directory; return repo-relative POSIX path or None if absolute/external."""
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    base = src_md.parent
    resolved = (base / clean).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError:
        return None
    return rel.as_posix()


def replace_images(text: str, src_md: Path) -> str:
    # Images are kept as relative local paths. Medium import doesn't fetch
    # private-repo raw URLs anyway; the author uploads PNGs manually via
    # Medium's UI, using the local path as a guide for which file to attach.
    _ = src_md
    return text


def replace_links(text: str, src_md: Path) -> str:
    def sub(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        rel = resolve_relative(src_md, url)
        if rel is None:
            return m.group(0)
        frag = ""
        if "#" in url:
            frag = "#" + url.split("#", 1)[1]
        return f"[{label}]({BLOB_BASE}/{rel}{frag})"

    return LINK_RE.sub(sub, text)


def split_code_segments(text: str) -> list[tuple[bool, str]]:
    """Return list of (is_code, segment) preserving order. Code = inside ``` fences."""
    segments: list[tuple[bool, str]] = []
    in_code = False
    buf: list[str] = []
    for line in text.split("\n"):
        if line.startswith("```"):
            buf.append(line)
            if in_code:
                segments.append((True, "\n".join(buf)))
                buf = []
                in_code = False
            else:
                opening = buf.pop()
                if buf:
                    segments.append((False, "\n".join(buf)))
                    buf = []
                buf.append(opening)
                in_code = True
        else:
            buf.append(line)
    if buf:
        segments.append((in_code, "\n".join(buf)))
    return segments


def demote_headings(prose: str) -> str:
    def sub(m: re.Match) -> str:
        return f"**{m.group(2).strip()}**"

    return HEADING_RE.sub(sub, prose)


TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def parse_table_block(lines: list[str], i: int) -> tuple[list[str] | None, list[list[str]] | None, int]:
    """If lines[i] starts a markdown table, parse and return (headers, rows, next_i). Else (None, None, i)."""
    if i >= len(lines):
        return None, None, i
    if not TABLE_ROW_RE.match(lines[i]):
        return None, None, i
    if i + 1 >= len(lines) or not TABLE_SEP_RE.match(lines[i + 1]):
        return None, None, i

    def split_row(line: str) -> list[str]:
        s = line.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c.strip() for c in s.split("|")]

    headers = split_row(lines[i])
    rows: list[list[str]] = []
    j = i + 2
    while j < len(lines) and TABLE_ROW_RE.match(lines[j]) and not TABLE_SEP_RE.match(lines[j]):
        rows.append(split_row(lines[j]))
        j += 1
    return headers, rows, j


def render_table_as_nested_bullets(headers: list[str], rows: list[list[str]]) -> list[str]:
    def strip_bold(s: str) -> str:
        s = s.strip()
        while s.startswith("**") and s.endswith("**") and len(s) >= 4:
            s = s[2:-2].strip()
        return s

    out: list[str] = []
    for row in rows:
        first_header = strip_bold(headers[0]) if headers else ""
        first_value = strip_bold(row[0]) if row else ""
        label = first_value or first_header
        out.append(f"**{label}**")
        for h, v in list(zip(headers, row))[1:]:
            h_clean = h.strip()
            v_clean = v.strip()
            if not h_clean and not v_clean:
                continue
            if h_clean and v_clean:
                out.append(f"- {h_clean}: {v_clean}")
            elif v_clean:
                out.append(f"- {v_clean}")
            else:
                out.append(f"- {h_clean}")
        out.append("")
    return out


def render_table_as_markdown(headers: list[str], rows: list[list[str]]) -> list[str]:
    def fmt_row(cells: list[str]) -> str:
        return "| " + " | ".join(c.strip() for c in cells) + " |"

    out = [
        "<!-- TODO: render this table as PNG and replace with ![alt](../../../assets/.../table.png) -->",
        fmt_row(headers),
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    out.extend(fmt_row(r) for r in rows)
    out.append("")
    return out


def tables_to_bullets(prose: str) -> str:
    lines = prose.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        headers, rows, next_i = parse_table_block(lines, i)
        if headers is not None and rows is not None:
            if len(headers) <= 3:
                out.extend(render_table_as_nested_bullets(headers, rows))
            else:
                out.extend(render_table_as_markdown(headers, rows))
            i = next_i
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def transform_prose(prose: str) -> str:
    prose = tables_to_bullets(prose)
    prose = demote_headings(prose)
    return prose


def convert(src_md: Path) -> str:
    text = src_md.read_text(encoding="utf-8")
    text = strip_front_matter(text)
    text = replace_images(text, src_md)
    text = replace_links(text, src_md)

    segments = split_code_segments(text)
    converted = []
    for is_code, seg in segments:
        if is_code:
            converted.append(seg)
        else:
            converted.append(transform_prose(seg))
    return "\n".join(converted)


def extract_tags(text: str) -> str | None:
    matches = TAGS_LINE_RE.findall(text)
    return matches[-1].strip() if matches else None


def clean_for_medium_import(text: str) -> str:
    text = TOC_BEGIN_RE.sub("", text)
    text = TOC_END_RE.sub("", text)
    text = TAGS_LINE_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?m)^---\s*\n\s*\n---\s*$", "---", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def finalize_md_for_medium(body: str, tags: str | None) -> str:
    cleaned = clean_for_medium_import(body)
    header_lines = [
        "<!-- Medium import-ready. Tags go in Medium's tag field, not the body. -->",
    ]
    if tags:
        header_lines.append(f"<!-- Tags: {tags} -->")
    return "\n".join(header_lines) + "\n\n" + cleaned


def numeric_prefix(name: str) -> str | None:
    m = re.match(r"^(\d+)", name)
    return m.group(1) if m else None


def process_series(en_dir: Path) -> tuple[int, int]:
    medium_dir = en_dir.parent / "medium"
    medium_dir.mkdir(exist_ok=True)
    written = 0
    skipped = 0
    for md in sorted(en_dir.glob("*.md")):
        prefix = numeric_prefix(md.name)
        if not prefix:
            print(f"  SKIP no numeric prefix: {md.name}")
            skipped += 1
            continue
        body = convert(md)
        tags = extract_tags(body)
        md_out = finalize_md_for_medium(body, tags)
        (medium_dir / f"{prefix}.md").write_text(md_out, encoding="utf-8")
        written += 1
    return written, skipped


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        en_dirs = [Path(p).resolve() for p in argv[1:]]
    else:
        en_dirs = [
            entry.path / "en"
            for entry in load_catalog()
            if is_present(entry) and "en" in entry.languages and (entry.path / "en").is_dir()
        ]
    total_w, total_s = 0, 0
    for en_dir in en_dirs:
        if not en_dir.is_dir():
            print(f"SKIP missing dir: {en_dir}")
            continue
        print(f"== {en_dir.relative_to(ROOT)}")
        w, s = process_series(en_dir)
        total_w += w
        total_s += s
        print(f"   wrote {w}, skipped {s}")
    print(f"\nTotal: wrote {total_w}, skipped {total_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
