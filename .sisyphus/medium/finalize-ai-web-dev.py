#!/usr/bin/env python3
"""Idempotent finalizer for the ai-web-dev-101 series (single-variant Korean).

Adapted from finalize-posts.py. Differences vs Azure series:
- Single flat directory (no ko/en/medium subfolders)
- Korean-only (always uses '## 참고 자료' and '## 시리즈 목차')
- Replaces legacy '**Tags:** `A` `B`' bold-backtick line with visible 'Tags: A, B, ...'
- Removes any pre-existing 'Series TOC' section (## or ### '시리즈 목차') sitting
  immediately above the references section, then inserts the canonical
  marker-wrapped TOC.

Three operations, each idempotent:
1. Normalize references heading to '## 참고 자료' (any '### 참고 자료' or numeric
   prefix variant immediately preceding the references section is rewritten).
2. Strip pre-existing TOC (marker-wrapped or ad-hoc 시리즈 목차 heading + list
   that sits between the last body content and the references heading).
3. Insert marker-wrapped TOC above references; ensure 'Tags: ...' is the very
   last non-empty line.
"""

from __future__ import annotations

import re
from pathlib import Path

from _catalog import ROOT, is_present, load_catalog

SERIES_ID = "ai-web-dev-101"


def resolve_series_dir() -> Path | None:
    for entry in load_catalog():
        if entry.id == SERIES_ID:
            return entry.path if is_present(entry) else None
    return None


SERIES_TAGS = ["AI", "LLM", "웹 개발", "Python", "Tutorial"]

KO_REF_HEADING = "## 참고 자료"
TOC_HEADING = "## 시리즈 목차"
TOC_BEGIN = "<!-- toc:begin -->"
TOC_END = "<!-- toc:end -->"
TAG_LINE_PREFIX = "Tags: "
LEGACY_TAG_RE = re.compile(r"^\s*\*\*Tags:\*\*\s")

# Any heading line that should be treated as the references section start.
REF_HEADING_RE = re.compile(r"^#{2,3}\s*(?:\d+\.\s*)?참고\s*자료\s*$")
# Any heading line that should be treated as a series-TOC start.
TOC_HEADING_RE = re.compile(r"^#{2,3}\s*(?:\d+\.\s*)?시리즈\s*목차\s*$")

H1_RE = re.compile(r"^#\s+(.+?)\s*$")


def numeric_prefix(name: str) -> str | None:
    m = re.match(r"^(\d+)", name)
    return m.group(1) if m else None


def read_h1(text: str) -> str | None:
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        m = H1_RE.match(s)
        if m:
            return m.group(1).strip()
        return None
    return None


def collect_series(series_dir: Path) -> tuple[Path, dict[int, dict[str, str]]]:
    """Return (posts_dir, {idx: {'title','filename'}}). Posts live in series_dir/ko/
    if that subdir exists (post-Phase-6 layout), otherwise series_dir itself
    (pre-Phase-6 flat layout)."""
    posts_dir = series_dir / "ko" if (series_dir / "ko").is_dir() else series_dir
    result: dict[int, dict[str, str]] = {}
    for md in sorted(posts_dir.glob("*.md")):
        prefix = numeric_prefix(md.name)
        if not prefix:
            continue
        idx = int(prefix)
        title = read_h1(md.read_text(encoding="utf-8")) or md.stem
        result[idx] = {"title": title, "filename": md.name}
    return posts_dir, result


def build_toc(entries: dict[int, dict[str, str]], current_idx: int) -> list[str]:
    lines = [TOC_BEGIN, TOC_HEADING, ""]
    for idx in sorted(entries):
        e = entries[idx]
        if idx < current_idx:
            lines.append(f"- [{e['title']}](./{e['filename']})")
        elif idx == current_idx:
            lines.append(f"- **{e['title']} (현재 글)**")
        else:
            lines.append(f"- {e['title']} (예정)")
    lines.append("")
    lines.append(TOC_END)
    return lines


def find_references_index(lines: list[str]) -> int | None:
    for i, line in enumerate(lines):
        if REF_HEADING_RE.match(line.strip()):
            return i
    return None


def normalize_ref_heading(lines: list[str], ref_idx: int) -> list[str]:
    out = list(lines)
    out[ref_idx] = KO_REF_HEADING
    return out


def strip_marker_toc(lines: list[str]) -> list[str]:
    if TOC_BEGIN not in "\n".join(lines):
        return lines
    out = []
    skip = False
    for line in lines:
        if line.strip() == TOC_BEGIN:
            skip = True
            continue
        if line.strip() == TOC_END:
            skip = False
            continue
        if not skip:
            out.append(line)
    return out


def strip_adhoc_toc_before_refs(lines: list[str]) -> list[str]:
    """Remove any '## 시리즈 목차' / '### 시리즈 목차' heading and its list that
    sits between the last body content and the references heading."""
    ref_idx = find_references_index(lines)
    if ref_idx is None:
        return lines
    # Walk back from ref_idx to find a TOC heading.
    i = ref_idx - 1
    # Skip blank lines and '---' dividers.
    while i >= 0 and (lines[i].strip() == "" or lines[i].strip() == "---"):
        i -= 1
    # Now collect contiguous list/blank lines, then expect the heading.
    list_block_start = i + 1
    while i >= 0 and (
        lines[i].strip() == ""
        or lines[i].lstrip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."))
    ):
        i -= 1
    if i < 0:
        return lines
    if not TOC_HEADING_RE.match(lines[i].strip()):
        return lines
    heading_idx = i
    # Remove from heading_idx through list_block_start - 1 (inclusive of heading
    # and any trailing blanks before refs handling). Keep everything before.
    return lines[:heading_idx] + lines[list_block_start:]


def find_toc_insert_point(lines: list[str], ref_idx: int) -> int:
    i = ref_idx - 1
    while i >= 0 and lines[i].strip() == "":
        i -= 1
    if i >= 0 and lines[i].strip() == "---":
        i -= 1
        while i >= 0 and lines[i].strip() == "":
            i -= 1
    return i + 1


def apply_tag_line(lines: list[str]) -> list[str]:
    desired = f"{TAG_LINE_PREFIX}{', '.join(SERIES_TAGS)}"
    out = [ln for ln in lines if not LEGACY_TAG_RE.match(ln)]
    out = [ln for ln in out if not ln.startswith(TAG_LINE_PREFIX)]
    while out and out[-1].strip() == "":
        out.pop()
    out.append("")
    out.append(desired)
    return out


def collapse_redundant(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s == "":
            if out and out[-1].strip() == "":
                continue
        elif s == "---":
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                j -= 1
            if j >= 0 and out[j].strip() == "---":
                continue
        out.append(line)
    while out and out[-1].strip() == "":
        out.pop()
    out.append("")
    return out


def process_post(path: Path, idx: int, entries: dict[int, dict[str, str]]) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 1. Strip marker-wrapped TOC if present.
    lines = strip_marker_toc(lines)

    # 2. Strip ad-hoc 시리즈 목차 (heading + list) sitting above refs.
    lines = strip_adhoc_toc_before_refs(lines)

    # 3. Drop any existing tag lines (legacy bold-backtick or canonical).
    lines = [ln for ln in lines if not LEGACY_TAG_RE.match(ln)]
    lines = [ln for ln in lines if not ln.startswith(TAG_LINE_PREFIX)]

    # 4. Locate references section and normalize its heading.
    ref_idx = find_references_index(lines)
    if ref_idx is None:
        return "no-references-section"
    lines = normalize_ref_heading(lines, ref_idx)

    # 5. Insert canonical TOC above references.
    insert_at = find_toc_insert_point(lines, ref_idx)
    toc_block = build_toc(entries, idx)
    new_lines = lines[:insert_at] + ["", "---", ""] + toc_block + [""] + lines[insert_at:]

    # 6. Cleanup + append tag line as the very last line.
    new_lines = collapse_redundant(new_lines)
    new_lines = apply_tag_line(new_lines)

    new_text = "\n".join(new_lines) + "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return "updated"
    return "unchanged"


def main() -> int:
    series_dir = resolve_series_dir()
    if series_dir is None:
        print(f"SKIP missing: {SERIES_ID}")
        return 1
    posts_dir, entries = collect_series(series_dir)
    print(f"== {SERIES_ID} ({posts_dir.relative_to(ROOT)}, {len(entries)} posts)")
    totals = {"updated": 0, "unchanged": 0, "no-references-section": 0}
    for idx, info in sorted(entries.items()):
        path = posts_dir / info["filename"]
        r = process_post(path, idx, entries)
        totals[r] = totals.get(r, 0) + 1
        print(f"  {r:8s} {path.relative_to(ROOT)}")
    print("\nTotals:")
    for k, v in sorted(totals.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
