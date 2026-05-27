#!/usr/bin/env python3
"""
Dedup consecutive duplicate H2 sections with identical body.

A "duplicate H2 section" is defined as:
- Same H2 heading text
- Body (lines between this H2 and next H2/EOF) is byte-identical to a previous occurrence in the same file
- Within 100 lines of the previous occurrence

Action: keep first occurrence, delete all subsequent identical ones.

Usage:
    python3 scripts/dedup_h2.py <file.md> [--dry-run]
    python3 scripts/dedup_h2.py --series <series> [--dry-run]
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path


def find_h2_sections(lines: list[str]) -> list[tuple[int, int, str, str]]:
    """Return [(start_line_0idx, end_line_0idx_exclusive, heading, body_normalized)]"""
    in_code = False
    h2_positions: list[int] = []
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("## "):
            h2_positions.append(i)

    sections = []
    for idx, start in enumerate(h2_positions):
        end = h2_positions[idx + 1] if idx + 1 < len(h2_positions) else len(lines)
        heading = lines[start]
        body_lines = lines[start + 1 : end]
        # Normalize: strip leading/trailing blank lines
        while body_lines and body_lines[0].strip() == "":
            body_lines.pop(0)
        while body_lines and body_lines[-1].strip() == "":
            body_lines.pop()
        body = "\n".join(body_lines)
        sections.append((start, end, heading, body))
    return sections


def dedup_file(path: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    """Returns (num_removed, removal_log)"""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    sections = find_h2_sections(lines)

    seen: dict[tuple[str, str], int] = {}  # (heading, body) -> first start_line
    to_remove: list[tuple[int, int]] = []  # (start, end) ranges to delete
    log: list[str] = []

    for start, end, heading, body in sections:
        key = (heading, body)
        if key in seen:
            prev_start = seen[key]
            # Only dedup if within 100 lines (consecutive template explosion pattern)
            if start - prev_start < 100:
                to_remove.append((start, end))
                log.append(
                    f"  {path}:{start + 1}-{end} duplicate of line {prev_start + 1}: {heading}"
                )
                continue
        seen[key] = start

    if not to_remove:
        return 0, log

    # Apply deletions in reverse so indices stay valid
    new_lines = list(lines)
    for start, end in sorted(to_remove, reverse=True):
        # Also consume trailing blank line if present (avoid accumulating blanks)
        actual_end = end
        # Don't delete past file end
        del new_lines[start:actual_end]

    if not dry_run:
        path.write_text("\n".join(new_lines), encoding="utf-8")

    return len(to_remove), log


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Files or directories")
    parser.add_argument(
        "--series", help="Series name (process content/<series>/{ko,en})"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets: list[Path] = []
    if args.series:
        base = Path("content") / args.series
        for sub in ("ko", "en"):
            d = base / sub
            if d.is_dir():
                targets.extend(sorted(d.glob("*.md")))
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            targets.extend(sorted(path.glob("*.md")))
        elif path.is_file():
            targets.append(path)

    if not targets:
        print("no targets", file=sys.stderr)
        return 1

    total_removed = 0
    affected_files = 0
    for path in targets:
        n, log = dedup_file(path, dry_run=args.dry_run)
        if n > 0:
            affected_files += 1
            total_removed += n
            for line in log:
                print(line)

    suffix = " [DRY RUN]" if args.dry_run else ""
    print(
        f"\nTotal: {total_removed} duplicate sections removed from {affected_files} files{suffix}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
