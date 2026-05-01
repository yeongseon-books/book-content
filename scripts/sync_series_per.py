"""Sync per-article metadata from front matter into series.yaml.

Walks content/<series>/{ko,en}/*.md, reads front matter, and writes
a `per` block under each series entry in series.yaml:

    per:
      ko:
        articles:
          - idx: 1
            slug: 01-what-is-azure-functions
            title: "Azure Functions란? — ..."
            status: ready
      en:
        articles:
          - idx: 1
            slug: 01-what-is-azure-functions
            title: "What Is Azure Functions?"
            status: ready

Only series with content on disk are updated. Planned series with no
content directory are left without a `per` field.

Run this after adding or renaming articles, or after bulk status changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import frontmatter as fm
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"


class _LiteralStr(str):
    pass


def _literal_representer(dumper: yaml.Dumper, data: _LiteralStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


def _build_per(series_path: Path, languages: list[str]) -> dict:
    per: dict = {}
    for lang in languages:
        lang_dir = series_path / lang
        if not lang_dir.is_dir():
            continue
        articles = []
        for md in sorted(lang_dir.glob("[0-9][0-9]-*.md")):
            try:
                post = fm.load(str(md))
            except Exception as e:
                print(f"  WARN: could not parse {md.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
                continue
            idx = int(md.stem[:2])
            slug = md.stem
            title = post.metadata.get("title", md.stem)
            status = post.metadata.get("status", "draft")
            articles.append({"idx": idx, "slug": slug, "title": title, "status": status})
        if articles:
            per[lang] = {"articles": articles}
    return per


def main() -> int:
    raw = SERIES_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    updated = 0
    for s in data["series"]:
        sid = s["id"]
        path_str = s.get("path", "")
        series_path = REPO_ROOT / path_str
        if not series_path.is_dir():
            continue
        languages = s.get("languages", [])
        per = _build_per(series_path, languages)
        if per:
            s["per"] = per
            updated += 1
            total = sum(len(per[l]["articles"]) for l in per)
            print(f"  {sid}: {list(per.keys())} ({total} articles)")

    yaml.add_representer(_LiteralStr, _literal_representer)

    out = yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120,
    )
    SERIES_YAML.write_text(out, encoding="utf-8")
    print(f"\nUpdated {updated} series in series.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
