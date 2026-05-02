#!/usr/bin/env python3
"""Sync image assets from book-content to book-public-assets.

Usage:
    python3 scripts/sync_assets.py --target TARGET_DIR [--apply] [--prune] [--series SERIES]

TARGET_DIR is the root of a local book-public-assets checkout.
By default runs in dry-run mode — pass --apply to actually copy files.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"

ALLOWED_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".svg"})
SAFETY_MARKER = ".no-content-here"


def _has_safety_marker(path: Path) -> bool:
    """Check if *path* contains the safety marker file."""
    return (path / SAFETY_MARKER).exists()


def collect_assets(series_filter: str | None = None) -> list[Path]:
    """Return list of asset files relative to ASSETS_DIR."""
    files: list[Path] = []
    if not ASSETS_DIR.is_dir():
        return files
    for root_str, _dirs, filenames in os.walk(ASSETS_DIR):
        root = Path(root_str)
        rel = root.relative_to(ASSETS_DIR)
        parts = rel.parts
        if series_filter and parts and parts[0] != series_filter:
            continue
        for fname in filenames:
            if fname.startswith("."):
                continue
            if Path(fname).suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            files.append(rel / fname)
    return sorted(files)


def sync(
    target_dir: Path,
    *,
    apply: bool = False,
    prune: bool = False,
    series_filter: str | None = None,
) -> tuple[int, int, int]:
    """Sync assets to *target_dir*/assets/.

    Returns (copied, skipped, pruned) counts.
    """
    target_assets = target_dir / "assets"
    source_files = collect_assets(series_filter)
    source_rel_set = {str(f) for f in source_files}

    copied = 0
    skipped = 0
    pruned = 0

    # Copy new / updated files
    for rel in source_files:
        src = ASSETS_DIR / rel
        dst = target_assets / rel
        if dst.exists() and filecmp.cmp(src, dst, shallow=False):
            skipped += 1
            continue
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"{'COPY' if apply else 'WOULD COPY'}: assets/{rel}")
        copied += 1

    # Prune files not in source
    if prune and target_assets.is_dir():
        for root_str, _dirs, filenames in os.walk(target_assets):
            root = Path(root_str)
            for fname in filenames:
                if fname.startswith("."):
                    continue
                dst = root / fname
                rel = dst.relative_to(target_assets)
                if series_filter:
                    parts = rel.parts
                    if parts and parts[0] != series_filter:
                        continue
                if str(rel) not in source_rel_set:
                    if apply:
                        dst.unlink()
                    print(f"{'DELETE' if apply else 'WOULD DELETE'}: assets/{rel}")
                    pruned += 1

    return copied, skipped, pruned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync image assets to book-public-assets checkout."
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Root of the book-public-assets checkout.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually copy files (default is dry-run).",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove files in target that no longer exist in source.",
    )
    parser.add_argument(
        "--series",
        default=None,
        help="Sync only a specific series (e.g. azure-functions-101).",
    )
    args = parser.parse_args(argv)

    target = args.target.resolve()
    if not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        return 1

    if not _has_safety_marker(target):
        print(
            f"ERROR: {target} does not contain '{SAFETY_MARKER}'. "
            "This file must exist in the book-public-assets root as a safety check.",
            file=sys.stderr,
        )
        return 1

    if target.name != "book-public-assets":
        print(
            f"ERROR: target directory must be named 'book-public-assets', got: {target.name}",
            file=sys.stderr,
        )
        return 1

    if not ASSETS_DIR.is_dir():
        print(f"ERROR: assets directory not found: {ASSETS_DIR}", file=sys.stderr)
        return 1

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Syncing assets/ -> {target}/assets/")
    if args.series:
        print(f"  Series filter: {args.series}")
    print()

    copied, skipped, pruned = sync(
        target,
        apply=args.apply,
        prune=args.prune,
        series_filter=args.series,
    )

    print()
    print(f"Done: {copied} copied, {skipped} unchanged, {pruned} pruned.")
    if not args.apply and copied + pruned > 0:
        print("(Dry-run mode. Pass --apply to execute.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
