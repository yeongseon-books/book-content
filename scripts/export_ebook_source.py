"""Export an ebook source bundle for the private mkdocs-ebook builder.

Per EBOOK.md (sections 4 and 5), this writes a self-contained directory
the private builder can consume:

    exports/ebook-source/<series>-<lang>/
        mkdocs.yml
        docs/
            index.md
            preface.md
            01-<slug>.md
            02-<slug>.md
            ...
        assets/<series>/...

Transforms applied (per EBOOK.md section 5):
- strip front matter (private builder uses its own metadata)
- strip blog-only blocks
- keep ebook-only blocks (markers stripped, body kept)
- strip TOC marker block (book TOC replaces series TOC)
- strip bottom Tags line
- rewrite image paths from `../../../assets/...` to `../assets/...` so the
  flat docs/ tree resolves to the bundle's assets/

Cross-series links are left as-is and reported as warnings; the book is
self-contained, so cross-series references should be footnoted manually
or removed before publishing. (We don't auto-strip them — that's an
editorial decision.)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_BASE = REPO_ROOT / "exports" / "ebook-source"
SERIES_YAML = REPO_ROOT / "series.yaml"
ASSETS_DIR = REPO_ROOT / "assets"
TEMPLATES = REPO_ROOT / "templates"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _transform import transform_for_ebook

IMG_PATH_RE = re.compile(r"(!\[[^\]]*\]\()\.\./\.\./\.\./assets/")
LINK_PATH_RE = re.compile(r"(?<!!)(\[[^\]]+\]\()\.\./\.\./\.\./assets/")
CROSS_SERIES_LINK_RE = re.compile(
    r"(?<!!)\[[^\]]+\]\(\.\./\.\./[a-z][a-z0-9-]+/(ko|en)/[^)]+\)"
)


def rewrite_assets(text: str) -> str:
    text = IMG_PATH_RE.sub(r"\1../assets/", text)
    text = LINK_PATH_RE.sub(r"\1../assets/", text)
    return text


def load_root_series(series_id: str) -> dict:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))["series"]
    for s in catalog:
        if s["id"] == series_id:
            return s
    raise SystemExit(f"unknown series: {series_id}")


def load_per_series(series_path: Path) -> dict:
    f = series_path / "series.yaml"
    if not f.is_file():
        raise SystemExit(f"missing per-series catalog: {f}")
    return yaml.safe_load(f.read_text(encoding="utf-8"))


def article_title(md: Path, fallback: str) -> str:
    try:
        post = frontmatter.loads(md.read_text(encoding="utf-8"))
        t = post.metadata.get("title")
        if isinstance(t, str) and t.strip():
            return t.strip()
    except Exception:
        pass
    return fallback


def render_template(path: Path, vars_: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for k, v in vars_.items():
        text = text.replace("{{ " + k + " }}", v)
    return text


def build_bundle(series_id: str, lang: str, out_dir: Path) -> int:
    s = load_root_series(series_id)
    if lang not in s.get("languages", []):
        raise SystemExit(f"series {series_id} has no {lang}/ language")
    if not s.get("targets", {}).get("ebook"):
        raise SystemExit(f"series {series_id} does not target ebook")
    series_path = REPO_ROOT / s["path"]
    per = load_per_series(series_path)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    docs = out_dir / "docs"
    docs.mkdir(parents=True)

    chapters: list[dict] = []
    cross_warnings: list[tuple[str, str]] = []

    for art in per.get("articles", []):
        slug = art["slug"]
        idx = art["idx"]
        src = series_path / lang / f"{slug}.md"
        if not src.is_file():
            print(f"  skip ch{idx}: missing {src.relative_to(REPO_ROOT)}")
            continue
        raw = src.read_text(encoding="utf-8")
        title = article_title(src, slug)
        text = transform_for_ebook(raw)
        text = rewrite_assets(text)
        for m in CROSS_SERIES_LINK_RE.finditer(text):
            cross_warnings.append((src.name, m.group(0)))
        dst = docs / f"{idx:02d}-{slug.split('-', 1)[1] if '-' in slug else slug}.md"
        dst.write_text(text, encoding="utf-8")
        chapters.append({"idx": idx, "title": title, "filename": dst.name})

    asset_src = ASSETS_DIR / series_id
    asset_dst = out_dir / "assets" / series_id
    if asset_src.is_dir():
        shutil.copytree(asset_src, asset_dst)

    title_field = s.get("title", {}).get(lang, series_id)
    desc_field = s.get("description", {}).get(lang, "")
    canonical_links = "\n  ".join(
        f"- [{c['title']}](../../{s['path']}/{lang}/{per['articles'][i]['slug']}.md)"
        for i, c in enumerate(chapters) if i < len(per.get("articles", []))
    )
    series_overview = "\n".join(f"- 제 {c['idx']} 장: {c['title']}" for c in chapters)

    index_md = render_template(TEMPLATES / "ebook-index.md", {
        "ebook_title": title_field,
        "ebook_subtitle": desc_field,
        "author": "Yeongseon Choe",
        "first_edition_date": "TBD",
        "this_edition_date": "TBD",
    })
    index_md = re.sub(
        r"\{% for chapter in chapters %\}.*?\{% endfor %\}",
        series_overview,
        index_md, flags=re.DOTALL,
    )
    (docs / "index.md").write_text(index_md, encoding="utf-8")

    preface_md = render_template(TEMPLATES / "ebook-preface.md", {
        "series_title": title_field,
        "series_overview": series_overview,
        "chapter_connections": "(편집 시 보강)",
        "canonical_links": canonical_links,
        "last_updated": "TBD",
    })
    (docs / "preface.md").write_text(preface_md, encoding="utf-8")

    nav_lines = ["nav:", "  - Preface: preface.md"]
    for c in chapters:
        nav_lines.append(f"  - 제 {c['idx']} 장: {c['filename']}")
    mkdocs_yml = (
        f"site_name: {title_field}\n"
        f"site_description: {desc_field}\n"
        f"docs_dir: docs\n"
        f"theme:\n  name: material\n  language: {lang}\n"
        + "\n".join(nav_lines) + "\n"
    )
    (out_dir / "mkdocs.yml").write_text(mkdocs_yml, encoding="utf-8")

    print(f"wrote {len(chapters)} chapters to {out_dir.relative_to(REPO_ROOT)}/")
    if cross_warnings:
        print(f"\nWARN: {len(cross_warnings)} cross-series link(s) preserved verbatim")
        print("  (book is self-contained; review these manually before publishing):")
        for fname, link in cross_warnings[:10]:
            print(f"    {fname}: {link}")
        if len(cross_warnings) > 10:
            print(f"    ... and {len(cross_warnings) - 10} more")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series", help="series id, e.g. azure-functions-101")
    ap.add_argument("--lang", required=True, choices=["ko", "en"])
    ap.add_argument("--out", default=None,
                    help=f"override output dir (default: {EXPORT_BASE}/<series>-<lang>)")
    args = ap.parse_args()
    out = Path(args.out) if args.out else EXPORT_BASE / f"{args.series}-{args.lang}"
    return build_bundle(args.series, args.lang, out)


if __name__ == "__main__":
    sys.exit(main())
