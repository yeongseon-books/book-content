#!/usr/bin/env python3
"""
Insert series intro line right after H1 + first paragraph when missing.

STYLE_GUIDE §1.1:
  ko: '이 글은 {시리즈 표시명} 시리즈의 {첫 번째 / N번째 / 마지막} 글입니다.'
  en: 'This is the {first|Nth|final} post in the {Series Name} series.'

Uses series.yaml for display titles. Counts files in the language directory
as filesystem fallback when series.yaml has no `per` entry.

Idempotent: skips files whose first 25 lines after H1 already satisfy the
regex used by scripts/check_article_structure.py.

CRITICAL: preserves front matter byte-exactly (no key reordering, no quoting
changes). Only edits the body between '---\\n' boundary and EOF.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

H1_RE = re.compile(r"^# .+$", re.MULTILINE)
KO_SERIES_INTRO = re.compile(r"이\s*글은[^.\n]{2,200}시리즈", re.MULTILINE)
EN_SERIES_INTRO = re.compile(r"\b[Tt]his is\b[^.\n]{2,200}\bseries\b", re.MULTILINE)
WINDOW = 25


def ordinal_en(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def ko_phrase(idx: int, total: int) -> str:
    if idx == 1:
        return "첫 번째"
    if idx == total:
        return "마지막"
    return f"{idx}번째"


def en_phrase(idx: int, total: int) -> str:
    if idx == 1:
        return "first"
    if idx == total:
        return "final"
    return ordinal_en(idx)


def build_intro(lang: str, series_title: str, idx: int, total: int) -> str:
    if lang == "ko":
        return f"이 글은 {series_title} 시리즈의 {ko_phrase(idx, total)} 글입니다."
    phrase = en_phrase(idx, total)
    return f"This is the {phrase} post in the {series_title} series."


def split_frontmatter(text: str):
    """Return (fm_block_including_delims, body, parsed_meta) or None."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm_block = text[: end + 5]
    body = text[end + 5 :]
    try:
        meta = yaml.safe_load(text[4:end])
    except Exception:
        return None
    if not isinstance(meta, dict):
        return None
    return fm_block, body, meta


def process_file(path: Path, series_meta: dict, dry_run: bool = False):
    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if not parts:
        return False, "no frontmatter"
    fm_block, body, meta = parts

    lang = meta.get("language", path.parent.name)
    series_id = meta.get("series")
    episode = meta.get("episode")
    if not series_id or not isinstance(episode, int):
        return False, "missing series or episode in frontmatter"
    if series_id not in series_meta:
        return False, f"series {series_id} not in series.yaml"

    sm = series_meta[series_id]
    title_map = sm.get("title", {})
    title = title_map.get(lang) if isinstance(title_map, dict) else None
    per = sm.get("per", {})
    per_lang = per.get(lang, {}) if isinstance(per, dict) else {}
    articles = per_lang.get("articles", []) if isinstance(per_lang, dict) else []
    total = len(articles)
    if total == 0:
        total = len(sorted(path.parent.glob("*.md")))
    if not title or total == 0:
        return False, f"no title/articles for {series_id} {lang}"

    h1 = H1_RE.search(body)
    if not h1:
        return False, "no H1"

    after_h1 = body[h1.end() :]
    window_lines = after_h1.splitlines()[:WINDOW]
    window_text = "\n".join(window_lines)
    intro_re = KO_SERIES_INTRO if lang == "ko" else EN_SERIES_INTRO
    if intro_re.search(window_text):
        return False, "already present"

    intro_line = build_intro(lang, title, episode, total)

    lines = after_h1.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        new_after = "\n\n" + intro_line + "\n"
        new_body = body[: h1.end()] + new_after
    else:
        j = i
        while j < len(lines) and lines[j].strip() != "":
            j += 1
        new_lines = lines[:j] + ["", intro_line] + lines[j:]
        new_body = body[: h1.end()] + "\n".join(new_lines)

    new_text = fm_block + new_body
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True, intro_line


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--series", help="Limit to one series id")
    parser.add_argument("--lang", choices=["ko", "en"], help="Limit to language")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(REPO_ROOT / "series.yaml") as f:
        catalog = yaml.safe_load(f)
    series_meta = {s["id"]: s for s in catalog["series"]}

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = []
        for series_dir in sorted((REPO_ROOT / "content").iterdir()):
            if not series_dir.is_dir():
                continue
            if args.series and series_dir.name != args.series:
                continue
            for sub in ("ko", "en"):
                if args.lang and sub != args.lang:
                    continue
                d = series_dir / sub
                if d.is_dir():
                    targets.extend(sorted(d.glob("*.md")))

    changed = 0
    skipped = 0
    errors = 0
    for path in targets:
        try:
            ok, reason = process_file(path, series_meta, dry_run=args.dry_run)
        except Exception as e:
            errors += 1
            print(f"ERROR {path}: {e}", file=sys.stderr)
            continue
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
        if ok:
            changed += 1
            print(f"FIX {rel}: {reason}")
        elif reason not in (
            "already present",
            "missing series or episode in frontmatter",
        ):
            skipped += 1
            print(f"SKIP {rel}: {reason}")

    suffix = " [DRY RUN]" if args.dry_run else ""
    print(f"\nChanged: {changed}, skipped: {skipped}, errors: {errors}{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
