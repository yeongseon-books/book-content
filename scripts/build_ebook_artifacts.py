"""Build PDF/EPUB artifacts for every ebook source bundle.

Driven by series.yaml (skips status: planned). Honors --series filter,
--to (formats), --profile, --series-profile-map for per-series profile
overrides. Default: build all formats for every published series, picking
the profile from language (ko -> korean-tech-book, en -> generic).

Requires the full system toolchain (pandoc, xelatex, Nanum + NotoEmoji
fonts, etc.) — run `mkdocs-ebook doctor` to verify before invoking.
See EBOOK.md §1.1 for the install path.

Outputs land in exports/ebook-source/<series>-<lang>/dist/, which is
gitignored. This script is the executable spec for "what does a release
build of every book look like".

Usage:
    python3 scripts/build_ebook_artifacts.py
    python3 scripts/build_ebook_artifacts.py --series azure-functions-101 --to pdf
    python3 scripts/build_ebook_artifacts.py --bin /tmp/ebookvenv/bin/mkdocs-ebook
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"
EXPORT_BASE = REPO_ROOT / "exports" / "ebook-source"

PROFILE_BY_LANG = {"ko": "korean-tech-book", "en": "generic"}


def load_targets(series_filter: str | None) -> list[tuple[str, str]]:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))["series"]
    out: list[tuple[str, str]] = []
    for s in catalog:
        if not s.get("targets", {}).get("ebook"):
            continue
        if s.get("status") == "planned":
            continue
        if series_filter and s["id"] != series_filter:
            continue
        for lang in s.get("languages", []):
            out.append((s["id"], lang))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", help="build only this series id")
    ap.add_argument("--to", default="all", help="format(s): epub, pdf, all, or comma-list")
    ap.add_argument(
        "--profile",
        default=None,
        help="override profile (default: ko->korean-tech-book, en->generic)",
    )
    ap.add_argument(
        "--bin",
        default=shutil.which("mkdocs-ebook") or "mkdocs-ebook",
        help="path to mkdocs-ebook (default: PATH)",
    )
    args = ap.parse_args()

    if not Path(args.bin).is_file() and shutil.which(args.bin) is None:
        print(f"ERROR: mkdocs-ebook not found at {args.bin!r}", file=sys.stderr)
        return 2

    targets = load_targets(args.series)
    if not targets:
        print("no ebook-target series found")
        return 1

    failed: list[tuple[str, str, int]] = []
    started = time.time()
    for series_id, lang in targets:
        bundle = EXPORT_BASE / f"{series_id}-{lang}"
        if not bundle.is_dir():
            print(f"FAIL {series_id}-{lang}: bundle missing")
            failed.append((series_id, lang, -1))
            continue
        profile = args.profile or PROFILE_BY_LANG.get(lang, "generic")
        t0 = time.time()
        proc = subprocess.run(
            [args.bin, "build", "-p", str(bundle), "--to", args.to, "--profile", profile],
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - t0
        status = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"{status} {series_id}-{lang} ({profile}, {elapsed:.1f}s)")
        if proc.returncode != 0:
            failed.append((series_id, lang, proc.returncode))
            for line in (proc.stdout + proc.stderr).strip().splitlines()[-8:]:
                print(f"  {line}")

    total = time.time() - started
    print()
    print(f"{len(targets) - len(failed)}/{len(targets)} bundles built in {total:.0f}s")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
