"""Regenerate SERIES.md and mkdocs.yml `nav` from series.yaml + per-series YAML.

This script is the single owner of:
- SERIES.md (whole file is regenerated)
- mkdocs.yml `nav` block between `# AUTOGEN-NAV-START` and `# AUTOGEN-NAV-END`

Source of truth:
- series.yaml: ordered series catalog with category, languages, targets, status, path
- content/<series>/series.yaml: articles[{idx, slug, status}]
- content/<series>/{ko,en}/<slug>.md: front matter `title:` field (per-article display title)

Categories are inferred from each series' `category:` field and grouped in
declaration order from series.yaml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"
SERIES_MD = REPO_ROOT / "SERIES.md"
MKDOCS_YAML = REPO_ROOT / "mkdocs.yml"

NAV_START = "# AUTOGEN-NAV-START"
NAV_END = "# AUTOGEN-NAV-END"

CATEGORY_LABELS = {
    "ai": "AI",
    "cs-core": "CS 핵심 과목",
    "software-engineering": "소프트웨어 엔지니어링",
    "data": "데이터",
    "programming": "프로그래밍",
    "azure": "Azure",
}

STATUS_LABELS = {
    "planned": "Planned",
    "draft": "Draft",
    "content-ready": "Content Ready",
    "code-checked": "Code Checked",
    "publish-ready": "Publish Ready",
    "ready": "Ready (legacy)",
    "published": "Published",
    "needs-update": "Needs Update",
}


def load_root_catalog() -> list[dict]:
    raw = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    return raw.get("series", [])


def load_per_series(series: dict) -> dict | None:
    p = REPO_ROOT / series["path"] / "series.yaml"
    if not p.is_file():
        return None
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def article_title(series_path: Path, slug: str, lang: str, fallback: str) -> str:
    md = series_path / lang / f"{slug}.md"
    if not md.is_file():
        return fallback
    try:
        post = frontmatter.loads(md.read_text(encoding="utf-8"))
        title = post.metadata.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    except Exception:
        pass
    return fallback


def render_series_md(catalog: list[dict]) -> str:
    out: list[str] = []
    out.append("# Series Index")
    out.append("")
    out.append(
        "이 문서는 전체 콘텐츠 시리즈의 목록과 발행 상태를 관리한다. "
        "단일 출처는 [`series.yaml`](./series.yaml) 이며, 본 문서는 "
        "`scripts/build_series_index.py` 가 자동 생성한다. 직접 편집 금지."
    )
    out.append("")
    out.append("## Status Legend")
    out.append("")
    out.append("| Status | Meaning |")
    out.append("| --- | --- |")
    for k, v in STATUS_LABELS.items():
        meanings = {
            "planned": "기획 중",
            "draft": "초안 작성 중",
            "content-ready": "본문 작성 완료, 코드 검증 전",
            "code-checked": "예제 코드 검증 완료",
            "publish-ready": "발행 준비 완료",
            "ready": "발행 준비 완료 (legacy)",
            "published": "발행 완료",
            "needs-update": "업데이트 필요",
        }
        out.append(f"| {v} | {meanings[k]} |")
    out.append("")
    out.append("---")
    out.append("")

    by_category: dict[str, list[dict]] = {}
    category_order: list[str] = []
    for s in catalog:
        cat = s.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
            category_order.append(cat)
        by_category[cat].append(s)

    for cat in category_order:
        out.append(f"## {CATEGORY_LABELS.get(cat, cat.title())}")
        out.append("")
        for s in by_category[cat]:
            sid = s["id"]
            title_ko = s.get("title", {}).get("ko", sid)
            title_en = s.get("title", {}).get("en", sid)
            desc_ko = s.get("description", {}).get("ko", "")
            languages = s.get("languages", [])
            targets = s.get("targets", {})
            series_status = s.get("status", "planned")
            per = load_per_series(s)

            heading = f"### {title_ko}"
            if title_en and title_en != title_ko:
                heading += f" / {title_en}"
            heading += f" (`{sid}`)"
            out.append(heading)
            out.append("")
            if desc_ko:
                out.append(desc_ko)
                out.append("")
            out.append(
                f"- 상태: **{STATUS_LABELS.get(series_status, series_status)}**"
            )
            out.append(f"- 언어: {', '.join(languages) if languages else '—'}")
            tgt_on = [k for k, v in targets.items() if v]
            out.append(
                f"- 발행 대상: {', '.join(tgt_on) if tgt_on else '—'}"
            )
            out.append(f"- 경로: [`{s['path']}/`](./{s['path']}/)")
            out.append("")

            if per is None or not per.get("articles"):
                out.append("_articles not yet enumerated._")
                out.append("")
                continue

            has_ko = "ko" in languages
            has_en = "en" in languages
            has_medium = bool(targets.get("medium")) and has_en

            header = ["#", "Title"]
            if has_ko:
                header.append("KO")
            if has_en:
                header.append("EN")
            if has_medium:
                header.append("Medium")
            header.append("Status")
            out.append("| " + " | ".join(header) + " |")
            out.append("| " + " | ".join(["---"] * len(header)) + " |")

            series_path = REPO_ROOT / s["path"]
            for art in per["articles"]:
                idx = art.get("idx") or art.get("episode", "?")
                slug = art["slug"]
                a_status = art.get("status", "draft")
                lang_for_title = "ko" if has_ko else "en"
                title = article_title(series_path, slug, lang_for_title, slug)
                row = [str(idx), title]
                if has_ko:
                    ko_md = series_path / "ko" / f"{slug}.md"
                    row.append(f"[ko](./{s['path']}/ko/{slug}.md)" if ko_md.is_file() else "—")
                if has_en:
                    en_md = series_path / "en" / f"{slug}.md"
                    row.append(f"[en](./{s['path']}/en/{slug}.md)" if en_md.is_file() else "—")
                if has_medium:
                    med_md = series_path / "medium" / f"{idx:02d}.md"
                    row.append(f"[medium](./{s['path']}/medium/{idx:02d}.md)" if med_md.is_file() else "—")
                row.append(STATUS_LABELS.get(a_status, a_status))
                out.append("| " + " | ".join(row) + " |")
            out.append("")
        out.append("---")
        out.append("")

    while out and out[-1] in ("", "---"):
        out.pop()
    out.append("")
    return "\n".join(out)


def render_nav(catalog: list[dict]) -> list[str]:
    lines = [NAV_START, "nav:", "  - Home: index.md"]

    by_category: dict[str, list[dict]] = {}
    category_order: list[str] = []
    for s in catalog:
        if not s.get("targets", {}).get("mkdocs"):
            continue
        per = load_per_series(s)
        if per is None or not per.get("articles"):
            continue
        cat = s.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
            category_order.append(cat)
        by_category[cat].append((s, per))

    for lang in ("ko", "en"):
        lang_label = "Korean" if lang == "ko" else "English"
        lines.append(f"  - {lang_label}:")
        lines.append(f"      - {lang}/index.md")
        for cat in category_order:
            cat_label = CATEGORY_LABELS.get(cat, cat.title())
            entries = [(s, per) for s, per in by_category[cat] if lang in s.get("languages", [])]
            if not entries:
                continue
            lines.append(f"      - {cat_label}:")
            for s, per in entries:
                title = s.get("title", {}).get(lang) or s["id"]
                lines.append(f"          - {title}:")
                series_path = REPO_ROOT / s["path"]
                for art in per["articles"]:
                    slug = art["slug"]
                    md = series_path / lang / f"{slug}.md"
                    if not md.is_file():
                        continue
                    a_title = article_title(series_path, slug, lang, slug)
                    safe_title = a_title.replace('"', '\\"')
                    lines.append(f'              - "{safe_title}": {lang}/{s["id"]}/{slug}.md')

    lines.append(NAV_END)
    return lines


def patch_mkdocs_nav(nav_block: list[str]) -> bool:
    text = MKDOCS_YAML.read_text(encoding="utf-8")
    new_nav = "\n".join(nav_block) + "\n"
    if NAV_START in text and NAV_END in text:
        pattern = re.compile(
            re.escape(NAV_START) + r".*?" + re.escape(NAV_END) + r"\n?",
            re.DOTALL,
        )
        new_text = pattern.sub(new_nav, text, count=1)
    else:
        nav_re = re.compile(r"^nav:.*?(?=\Z|\n[a-zA-Z_]+:)", re.DOTALL | re.MULTILINE)
        if nav_re.search(text):
            new_text = nav_re.sub(new_nav.rstrip() + "\n", text, count=1)
        else:
            new_text = text.rstrip() + "\n\n" + new_nav
    if new_text == text:
        return False
    MKDOCS_YAML.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    catalog = load_root_catalog()
    md = render_series_md(catalog)
    md_changed = SERIES_MD.read_text(encoding="utf-8") != md if SERIES_MD.exists() else True
    if md_changed:
        SERIES_MD.write_text(md, encoding="utf-8")
    nav_lines = render_nav(catalog)
    nav_changed = patch_mkdocs_nav(nav_lines)
    print(f"SERIES.md: {'updated' if md_changed else 'unchanged'}")
    print(f"mkdocs.yml nav: {'updated' if nav_changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
