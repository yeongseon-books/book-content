"""Verify that publishing artifacts reference existing public assets.

Scans:
- content/<series>/medium/*.html
- exports/tistory/**/*.md
- exports/hashnode/**/*.md

For URLs under series.yaml meta.asset_base_url, verifies that the referenced
file exists either:

- under the local book-content repository when --target is omitted, or
- under the provided book-public-assets checkout when --target is passed.

Also detects:
- missing referenced public assets
- residual ../../../assets/ paths in external publishing outputs
- wrong YeongseonBooks asset host URLs
- unsupported public asset extensions

Exit code 0 = all referenced assets found. Exit code 1 = errors detected.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"

# Match <img src="https://..."> in HTML
HTML_IMG_RE = re.compile(r'<img\s[^>]*src="([^"]+)"', re.IGNORECASE)

# Match ![alt](url) in Markdown
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

# Detect residual local relative image paths
LOCAL_ASSET_RE = re.compile(r"\.\./\.\./\.\./assets/")


def _load_asset_base_url() -> str:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    meta = catalog.get("meta") or {}
    url = meta.get("asset_base_url", "")
    if not url:
        raise SystemExit("series.yaml meta.asset_base_url is required.")
    return url.rstrip("/")


def _extract_urls(text: str, *, html: bool) -> list[str]:
    """Return all image URLs found in text."""
    pattern = HTML_IMG_RE if html else MD_IMG_RE
    return [m.group(1) for m in pattern.finditer(text)]


def _check_file(
    filepath: Path,
    base_url: str,
    errors: list[str],
    *,
    html: bool,
    asset_root: Path,
) -> int:
    """Check a single file.  Returns number of refs checked."""
    text = filepath.read_text(encoding="utf-8")
    rel_display = filepath.relative_to(REPO_ROOT)
    checked = 0
    prefix = f"{base_url}/"

    for src in _extract_urls(text, html=html):
        if src.startswith(prefix):
            # Public URL — verify local file exists and extension is allowed
            rel = src[len(prefix):]
            local = asset_root / rel
            ext = Path(rel).suffix.lower()
            allowed = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
            if ext not in allowed:
                errors.append(f"{rel_display}: unsupported public asset extension {rel}")
            if not local.is_file():
                errors.append(f"{rel_display}: references missing {rel}")
            checked += 1
        elif LOCAL_ASSET_RE.search(src):
            # Residual local relative path — should have been rewritten
            errors.append(f"{rel_display}: residual local path {src}")
            checked += 1
        elif src.startswith(("http://", "https://")):
            # Only flag URLs from our own org that point to wrong asset host
            if "yeongseon-books.github.io" in src and "book-public-assets" not in src:
                errors.append(f"{rel_display}: wrong YeongseonBooks asset URL {src}")
                checked += 1
    return checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Directory to verify asset files in (default: REPO_ROOT)",
    )
    args = parser.parse_args(argv)

    asset_root = args.target.resolve() if args.target else REPO_ROOT

    # If --target is given, verify it looks like a valid asset tree
    if args.target:
        if asset_root.name != "book-public-assets":
            print(
                f"ERROR: --target directory must be named 'book-public-assets', got: {asset_root.name}",
                file=sys.stderr,
            )
            return 1
        marker = asset_root / ".no-content-here"
        if not marker.is_file():
            print(
                f"ERROR: {asset_root} has no .no-content-here marker",
                file=sys.stderr,
            )
            return 1

    base_url = _load_asset_base_url()
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    errors: list[str] = []
    checked = 0
    warnings: list[str] = []

    # 1. Scan medium HTML artifacts
    for s in catalog["series"]:
        if not s.get("targets", {}).get("medium"):
            continue
        if "en" not in s.get("languages", []):
            continue
        medium_dir = REPO_ROOT / s["path"] / "medium"
        if not medium_dir.is_dir():
            continue
        for html_file in sorted(medium_dir.glob("*.html")):
            checked += _check_file(html_file, base_url, errors, html=True, asset_root=asset_root)

    # 2. Scan Tistory/Hashnode Markdown exports (warn if dirs absent)
    for export_name in ("tistory", "hashnode"):
        export_root = REPO_ROOT / "exports" / export_name
        if not export_root.is_dir():
            warnings.append(f"exports/{export_name}/ not found — skipped")
            continue
        for md_file in sorted(export_root.rglob("*.md")):
            checked += _check_file(md_file, base_url, errors, html=False, asset_root=asset_root)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: {checked} public asset references verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
