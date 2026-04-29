"""Materialize content/<series>/{ko,en}/*.md into docs/{ko,en}/<series>/<slug>.md.

This script is for MkDocs only. It does NOT touch mkdocs.yml `nav`; nav
generation is owned by scripts/build_series_index.py. Run order for a full
docs rebuild: build_series_index.py first (nav), then this script (files).

Per-target transforms applied:
- strip blog-only blocks
- strip ebook-only blocks (default; --include-ebook keeps them with markers stripped)
- strip TOC marker comments
- strip bottom plain-text Tags line
- rewrite image paths from `../../../assets/<series>/...` to `../../assets/<series>/...`
  to match the docs/ tree depth (docs/<lang>/<series>/<slug>.md needs `../../assets/`)

YAML front matter is preserved (MkDocs material reads title/description/tags).

Index pages docs/index.md, docs/ko/index.md, docs/en/index.md are written
on every run from a small built-in template that lists series links.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
DOCS_DIR = REPO_ROOT / "docs"
ASSETS_DIR = REPO_ROOT / "assets"
SERIES_YAML = REPO_ROOT / "series.yaml"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _transform import rewrite_outside_fences, transform_for_mkdocs

IMG_PATH_RE = re.compile(r"(!\[[^\]]*\]\()\.\./\.\./\.\./assets/")
LINK_PATH_RE = re.compile(r"(?<!!)(\[[^\]]+\]\()\.\./\.\./\.\./assets/")
CROSS_SERIES_LINK_RE = re.compile(
    r"(?<!!)(\[[^\]]+\]\()\.\./\.\./([a-z][a-z0-9-]+)/(ko|en)/"
)


def rewrite_asset_paths(text: str) -> str:
    def rewrite(line: str) -> str:
        line = IMG_PATH_RE.sub(r"\1../../assets/", line)
        line = LINK_PATH_RE.sub(r"\1../../assets/", line)
        return line
    return rewrite_outside_fences(text, rewrite)


def rewrite_cross_series_links(text: str, current_lang: str) -> str:
    def repl(m: re.Match) -> str:
        prefix, other_series, lang = m.group(1), m.group(2), m.group(3)
        if lang != current_lang:
            return m.group(0)
        return f"{prefix}../{other_series}/"
    return rewrite_outside_fences(text, lambda line: CROSS_SERIES_LINK_RE.sub(repl, line))


def load_catalog() -> list[dict]:
    return yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8")).get("series", [])


def ensure_clean(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_index_pages(catalog: list[dict]) -> None:
    home = ["# Tech Writing", "", "기술 콘텐츠 멀티채널 퍼블리싱 저장소.", "",
            "- [한국어 글 보기](ko/index.md)", "- [English posts](en/index.md)", ""]
    (DOCS_DIR / "index.md").write_text("\n".join(home), encoding="utf-8")

    for lang in ("ko", "en"):
        lines = ["# Korean Series" if lang == "ko" else "# English Series", ""]
        for s in catalog:
            if lang not in s.get("languages", []):
                continue
            if not s.get("targets", {}).get("mkdocs"):
                continue
            sid = s["id"]
            title = s.get("title", {}).get(lang, sid)
            desc = s.get("description", {}).get(lang, "")
            lines.append(f"## [{title}]({sid}/)")
            lines.append("")
            if desc:
                lines.append(desc)
                lines.append("")
        (DOCS_DIR / lang).mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / lang / "index.md").write_text("\n".join(lines), encoding="utf-8")


def materialize(include_ebook: bool) -> tuple[int, int]:
    ensure_clean(DOCS_DIR)
    catalog = load_catalog()
    write_index_pages(catalog)

    docs_assets = DOCS_DIR / "assets"
    if ASSETS_DIR.is_dir():
        shutil.copytree(ASSETS_DIR, docs_assets)

    written = 0
    skipped = 0
    for s in catalog:
        if not s.get("targets", {}).get("mkdocs"):
            continue
        series_dir = REPO_ROOT / s["path"]
        if not series_dir.is_dir():
            skipped += 1
            continue
        for lang in ("ko", "en"):
            if lang not in s.get("languages", []):
                continue
            src_lang = series_dir / lang
            if not src_lang.is_dir():
                continue
            dst_lang = DOCS_DIR / lang / s["id"]
            dst_lang.mkdir(parents=True, exist_ok=True)
            for md in sorted(src_lang.glob("*.md")):
                text = md.read_text(encoding="utf-8")
                text = transform_for_mkdocs(text, include_ebook_blocks=include_ebook)
                text = rewrite_asset_paths(text)
                text = rewrite_cross_series_links(text, current_lang=lang)
                (dst_lang / md.name).write_text(text, encoding="utf-8")
                written += 1
    return written, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-ebook", action="store_true",
                    help="keep ebook-only blocks in MkDocs output (default: strip)")
    args = ap.parse_args()
    written, skipped_series = materialize(include_ebook=args.include_ebook)
    print(f"docs/: wrote {written} markdown files, skipped {skipped_series} series")
    return 0


if __name__ == "__main__":
    sys.exit(main())
