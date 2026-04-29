#!/usr/bin/env python3
"""Mechanical caption normalization pass.

Applies safe, idempotent fixes to image alt text:
- Strip leading section numbers ("4. ", "5)")
- Strip trailing terminal punctuation (.?!)
- Remove backticks (identifier names stay as plain text)
- Collapse repeated whitespace

Does NOT rewrite semantics (sentence-form -> noun-phrase, Title Case -> sentence case,
question -> declarative). Those require AI/manual rewrite per AGENTS.md policy.

Default: dry-run. Pass --apply to write changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

IMG_RE = re.compile(r"(!\[)([^\]]+)(\])")
LEADING_NUM_RE = re.compile(r"^\s*\d+[\.)]\s+")
TRAILING_PUNCT_RE = re.compile(r"[\.!?。！？]+$")
BACKTICK_RE = re.compile(r"`+")
MULTISPACE_RE = re.compile(r"\s+")


def normalize_alt(alt: str) -> str:
    new = alt
    new = LEADING_NUM_RE.sub("", new)
    new = BACKTICK_RE.sub("", new)
    new = TRAILING_PUNCT_RE.sub("", new)
    new = MULTISPACE_RE.sub(" ", new).strip()
    return new


def iter_markdown_files() -> list[Path]:
    series_yaml = yaml.safe_load((ROOT / "series.yaml").read_text())
    files: list[Path] = []
    for s in series_yaml["series"]:
        spath = ROOT / s["path"]
        if not spath.exists():
            continue
        for sub in ("ko", "en"):
            d = spath / sub
            if d.is_dir():
                files.extend(sorted(d.glob("*.md")))
        files.extend(sorted(spath.glob("[0-9][0-9]-*.md")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    files = iter_markdown_files()
    total_changes = 0
    files_changed = 0

    for f in files:
        text = f.read_text()
        diffs: list[tuple[str, str]] = []
        for m in IMG_RE.finditer(text):
            old = m.group(2)
            new = normalize_alt(old)
            if old != new:
                diffs.append((old, new))
        if diffs:
            files_changed += 1
            total_changes += len(diffs)
            rel = f.relative_to(ROOT)
            for old, new in diffs:
                print(f"  {rel}\n    - {old!r}\n    + {new!r}")
            if args.apply:
                f.write_text(
                    IMG_RE.sub(
                        lambda m: f"{m.group(1)}{normalize_alt(m.group(2))}{m.group(3)}",
                        text,
                    )
                )

    mode = "applied" if args.apply else "dry-run"
    print(f"\n[{mode}] {total_changes} caption normalizations across {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
