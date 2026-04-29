"""Run `mkdocs-ebook lint` against every ebook source bundle.

This is the cheapest end-to-end smoke test for the eBook pipeline:
no system deps (pandoc/xelatex/fonts) required, just the Python install
of mkdocs-ebook (see EBOOK.md §1.1 for install instructions, including
the gh-token HTTPS path for environments without SSH access).

It iterates every series in `series.yaml` that has `targets.ebook: true`,
finds each `<lang>` it declares, and runs `mkdocs-ebook lint` on the
corresponding bundle under `exports/ebook-source/<series>-<lang>/`.

Exits non-zero on the first lint failure or missing bundle, so it can
sit in front of any future ebook build / release flow.

Usage:
    python3 scripts/lint_ebook_bundles.py
    python3 scripts/lint_ebook_bundles.py --series azure-functions-101
    python3 scripts/lint_ebook_bundles.py --bin /tmp/ebookvenv/bin/mkdocs-ebook
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"
EXPORT_BASE = REPO_ROOT / "exports" / "ebook-source"


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
    ap.add_argument("--series", help="lint only this series id")
    ap.add_argument(
        "--bin",
        default=shutil.which("mkdocs-ebook") or "mkdocs-ebook",
        help="path to mkdocs-ebook executable (default: PATH)",
    )
    args = ap.parse_args()

    if not Path(args.bin).is_file() and shutil.which(args.bin) is None:
        print(
            f"ERROR: mkdocs-ebook not found at {args.bin!r}. Install it per "
            "EBOOK.md §1.1, then pass --bin if it lives outside PATH.",
            file=sys.stderr,
        )
        return 2

    targets = load_targets(args.series)
    if not targets:
        print("no ebook-target series found (filter excluded everything?)")
        return 1

    failed: list[tuple[str, str, int]] = []
    for series_id, lang in targets:
        bundle = EXPORT_BASE / f"{series_id}-{lang}"
        if not bundle.is_dir():
            print(f"FAIL {series_id}-{lang}: bundle missing ({bundle.relative_to(REPO_ROOT)})")
            failed.append((series_id, lang, -1))
            continue
        proc = subprocess.run(
            [args.bin, "lint", "-p", str(bundle)],
            capture_output=True,
            text=True,
        )
        last_line = (proc.stdout.strip().splitlines() or [""])[-1]
        status = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"{status} {series_id}-{lang}: {last_line}")
        if proc.returncode != 0:
            failed.append((series_id, lang, proc.returncode))
            if proc.stderr.strip():
                print(f"  stderr: {proc.stderr.strip()}")

    print()
    print(f"{len(targets) - len(failed)}/{len(targets)} bundles passed lint")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
