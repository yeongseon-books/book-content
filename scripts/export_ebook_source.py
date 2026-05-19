"""Export an ebook source bundle for the private mkdocs-ebook builder.

Per EBOOK.md sections 4 and 4.1, this writes a self-contained directory
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
- strip front matter block (private builder uses its own metadata)
- strip blog-only blocks
- keep ebook-only blocks (markers stripped, body kept)
- strip TOC block entirely (book has its own native nav)
- strip bottom Tags line
- rewrite image paths from `../../../assets/...` and absolute
  `<asset_base_url>/assets/...` URLs to `assets/...` (matches the
  relocated `docs/assets/<series>/...` copy; ebook bundles are
  self-contained per ASSET_POLICY.md)
- rewrite cross-series links from `../../<other-series>/<lang>/...` to
  absolute `https://github.com/<repo>/tree/<TAG>/content/<other-series>/<lang>/...`
  GitHub URLs (book is self-contained; cross-series refs become
  commit-pinned external pointers)

Cross-series link rewrites are also surfaced as a WARN list so an editor
can decide whether to footnote them, drop them, or replace them with a
book-internal cross-reference before publishing.
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

_meta = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8")).get("meta") or {}
if "repo" not in _meta or "published_ref" not in _meta:
    raise SystemExit(
        "series.yaml is missing meta.repo or meta.published_ref — both are "
        "required to build commit-pinned absolute URLs in ebook bundles. "
        "Add a top-level meta: {repo: <owner>/<repo>, published_ref: <sha>} "
        "block. (published_ref is the immutable publishing snapshot baked "
        "into ebook canonical/cross-series URLs.)"
    )
REPO = _meta["repo"]
PUBLISHED_REF = _meta["published_ref"]
ASSET_BASE_URL = (_meta.get("asset_base_url") or "").rstrip("/")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _transform import rewrite_outside_fences, transform_for_ebook

IMG_PATH_RE = re.compile(r"(!\[[^\]]*\]\()\.\./\.\./\.\./assets/")
LINK_PATH_RE = re.compile(r"(?<!!)(\[[^\]]+\]\()\.\./\.\./\.\./assets/")
# Canonical sources now embed absolute public asset URLs (see ASSET_POLICY.md).
# eBook bundles must be self-contained, so rewrite those URLs back to the
# local `assets/<rest>` path that the private builder consumes.
_PUBLIC_BASE_ESC = re.escape(ASSET_BASE_URL) if ASSET_BASE_URL else ""
PUBLIC_IMG_URL_RE = (
    re.compile(rf"(!\[[^\]]*\]\(){_PUBLIC_BASE_ESC}/assets/")
    if ASSET_BASE_URL
    else None
)
PUBLIC_LINK_URL_RE = (
    re.compile(rf"(?<!!)(\[[^\]]+\]\()(?:{_PUBLIC_BASE_ESC})/assets/")
    if ASSET_BASE_URL
    else None
)
CROSS_SERIES_LINK_RE = re.compile(
    r"(?<!!)\[[^\]]+\]\(\.\./\.\./[a-z][a-z0-9-]+/(ko|en)/[^)]+\)"
)
CROSS_SERIES_REWRITE_RE = re.compile(
    r"(?<!!)(\[[^\]]+\]\()\.\./\.\./([a-z][a-z0-9-]+/(?:ko|en)/?[^)]*)\)"
)


def rewrite_assets(text: str) -> str:
    def rewrite(line: str) -> str:
        line = IMG_PATH_RE.sub(r"\1assets/", line)
        line = LINK_PATH_RE.sub(r"\1assets/", line)
        if PUBLIC_IMG_URL_RE is not None:
            line = PUBLIC_IMG_URL_RE.sub(r"\1assets/", line)
        if PUBLIC_LINK_URL_RE is not None:
            line = PUBLIC_LINK_URL_RE.sub(r"\1assets/", line)
        return line

    return rewrite_outside_fences(text, rewrite)


def rewrite_cross_series_links(text: str) -> str:
    replacement = rf"\1https://github.com/{REPO}/tree/{PUBLISHED_REF}/content/\2)"
    return rewrite_outside_fences(
        text,
        lambda line: CROSS_SERIES_REWRITE_RE.sub(replacement, line),
    )


def chapter_label(idx: int, lang: str) -> str:
    return f"제 {idx} 장" if lang == "ko" else f"Chapter {idx}"


def validate_catalog(series_id: str, lang: str, series_path: Path, per: dict) -> None:
    """Ensure per-series catalog matches files on disk before building.

    The bundle is assembled from per['articles']; if catalog drifts from
    disk, we either skip real chapters or write empty stubs. Fail loudly
    instead of silently producing a malformed book.
    """
    declared = {(a["idx"], a["slug"]) for a in per.get("articles", [])}
    if not declared:
        raise SystemExit(
            f"per-series catalog has no articles: {series_path}/series.yaml"
        )
    lang_dir = series_path / lang
    if not lang_dir.is_dir():
        raise SystemExit(f"missing language directory: {lang_dir}")
    on_disk_files = sorted(p.name for p in lang_dir.glob("*.md"))
    declared_files = sorted(f"{slug}.md" for _, slug in declared)
    missing_on_disk = sorted(set(declared_files) - set(on_disk_files))
    extra_on_disk = sorted(set(on_disk_files) - set(declared_files))
    problems: list[str] = []
    if missing_on_disk:
        problems.append(
            f"declared in catalog but missing from {lang}/: {missing_on_disk}"
        )
    if extra_on_disk:
        problems.append(f"present in {lang}/ but missing from catalog: {extra_on_disk}")
    for art in per.get("articles", []):
        slug = art["slug"]
        idx = art["idx"]
        m = re.match(r"^(\d+)-", slug)
        if m and int(m.group(1)) != int(idx):
            problems.append(f"slug prefix disagrees with idx: idx={idx} slug={slug!r}")
    if problems:
        raise SystemExit(
            f"catalog/disk mismatch for series {series_id} ({lang}):\n  - "
            + "\n  - ".join(problems)
        )


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


def article_title(md: Path) -> str:
    try:
        post = frontmatter.loads(md.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"front matter parse error in {md}: {exc}") from exc
    t = post.metadata.get("title")
    if not isinstance(t, str) or not t.strip():
        raise SystemExit(
            f"missing or empty front matter title in {md} "
            f"(ebook bundles require every chapter to have a title; "
            f"run scripts/check_frontmatter.py to find all violations)"
        )
    return t.strip()


def render_template(path: Path, vars_: dict[str, str]) -> str:
    """Render a template, stripping its leading self-doc comment block.

    Templates start with a `# Template: ...` doc header (a few `#`-prefixed
    lines, terminated by a blank line) so they're self-explanatory when read
    directly. That header is meta and must not leak into the rendered page.

    The strip rule: if the file starts with `# Template:`, drop every line up
    to and including the first blank line. Otherwise, leave the file alone.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith("# Template:"):
        i = 1
        while i < len(lines) and lines[i].strip() != "":
            i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        text = "\n".join(lines[i:])
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
    validate_catalog(series_id, lang, series_path, per)

    out_resolved = out_dir.resolve()
    base_resolved = EXPORT_BASE.resolve()
    if base_resolved not in out_resolved.parents and out_resolved != base_resolved:
        raise SystemExit(
            f"refusing to wipe {out_dir}: not under {EXPORT_BASE} (rmtree guard)"
        )
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
            raise SystemExit(f"missing chapter source: {src.relative_to(REPO_ROOT)}")
        raw = src.read_text(encoding="utf-8")
        title = article_title(src)
        text = transform_for_ebook(raw)
        text = rewrite_assets(text)
        for m in CROSS_SERIES_LINK_RE.finditer(text):
            cross_warnings.append((src.name, m.group(0)))
        text = rewrite_cross_series_links(text)
        dst = docs / f"{slug}.md"
        dst.write_text(text, encoding="utf-8")
        chapters.append(
            {"idx": idx, "title": title, "filename": dst.name, "slug": slug}
        )

    asset_src = ASSETS_DIR / series_id
    asset_dst = docs / "assets" / series_id
    if asset_src.is_dir():
        shutil.copytree(asset_src, asset_dst)

    title_field = s.get("title", {}).get(lang, series_id)
    desc_field = s.get("description", {}).get(lang, "")
    canonical_links = "\n  ".join(
        f"- [{c['title']}](https://github.com/{REPO}/blob/{PUBLISHED_REF}/{s['path']}/{lang}/{c['slug']}.md)"
        for c in chapters
    )
    series_overview = "\n".join(
        f"- {chapter_label(c['idx'], lang)}: {c['title']}" for c in chapters
    )

    index_md = render_template(
        TEMPLATES / "ebook-index.md",
        {
            "ebook_title": title_field,
            "ebook_subtitle": desc_field,
            "author": "Yeongseon Choe",
            "first_edition_date": "TBD",
            "this_edition_date": "TBD",
        },
    )
    index_md = re.sub(
        r"\{% for chapter in chapters %\}.*?\{% endfor %\}",
        series_overview,
        index_md,
        flags=re.DOTALL,
    )
    (docs / "index.md").write_text(index_md, encoding="utf-8")

    preface_md = render_template(
        TEMPLATES / "ebook-preface.md",
        {
            "series_title": title_field,
            "series_overview": series_overview,
            "chapter_connections": "(편집 시 보강)",
            "canonical_links": canonical_links,
            "last_updated": "TBD",
        },
    )
    (docs / "preface.md").write_text(preface_md, encoding="utf-8")

    nav_lines = ["nav:", "  - Cover: index.md", "  - Preface: preface.md"]
    for c in chapters:
        nav_lines.append(f"  - {chapter_label(c['idx'], lang)}: {c['filename']}")
    mkdocs_yml = (
        f"site_name: {title_field}\n"
        f"site_description: {desc_field}\n"
        f"docs_dir: docs\n"
        f"theme:\n  name: material\n  language: {lang}\n" + "\n".join(nav_lines) + "\n"
    )
    (out_dir / "mkdocs.yml").write_text(mkdocs_yml, encoding="utf-8")

    print(f"wrote {len(chapters)} chapters to {out_dir.relative_to(REPO_ROOT)}/")
    if cross_warnings:
        print(
            f"\nWARN: {len(cross_warnings)} cross-series link(s) rewritten to absolute GitHub URLs"
        )
        print(
            "  (book is self-contained; review whether to footnote, drop, or replace each):"
        )
        for fname, link in cross_warnings[:10]:
            print(f"    {fname}: {link}")
        if len(cross_warnings) > 10:
            print(f"    ... and {len(cross_warnings) - 10} more")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series", help="series id, e.g. azure-functions-101")
    ap.add_argument("--lang", required=True, choices=["ko", "en"])
    ap.add_argument(
        "--out",
        default=None,
        help=f"override output dir (default: {EXPORT_BASE}/<series>-<lang>)",
    )
    args = ap.parse_args()
    out = Path(args.out) if args.out else EXPORT_BASE / f"{args.series}-{args.lang}"
    return build_bundle(args.series, args.lang, out)


if __name__ == "__main__":
    sys.exit(main())
