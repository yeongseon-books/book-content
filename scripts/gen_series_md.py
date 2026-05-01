"""Generate SERIES.md from series.yaml and front matter status.

Reads series.yaml (which has per.{ko,en}.articles populated by sync_series_per.py)
and regenerates SERIES.md with accurate per-article status from front matter.

Run after sync_series_per.py to get a consistent SERIES.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"
SERIES_MD = REPO_ROOT / "SERIES.md"

STATUS_DISPLAY = {
    "draft": "Draft",
    "content-ready": "Content Ready",
    "code-checked": "Code Checked",
    "publish-ready": "Publish Ready",
    "ready": "Ready",
    "published": "Published",
    "needs-update": "Needs Update",
    "needs-polish": "Needs Polish",
}

CATEGORY_HEADERS = {
    "azure": "## Azure",
    "llm": "## LLM / AI",
    "other": "## Other",
}


def _series_row(s: dict, idx: int, art_ko: dict | None, art_en: dict | None) -> str:
    sid = s["id"]
    path = s["path"]
    title = (art_ko or art_en or {}).get("title", f"Episode {idx}")
    status_raw = (art_ko or art_en or {}).get("status", "draft")
    status = STATUS_DISPLAY.get(status_raw, status_raw)

    langs = s.get("languages", [])
    targets = s.get("targets", {})

    slug_ko = art_ko["slug"] if art_ko else None
    slug_en = art_en["slug"] if art_en else None

    ko_cell = f"[ko](./{path}/ko/{slug_ko}.md)" if slug_ko else "—"
    en_cell = f"[en](./{path}/en/{slug_en}.md)" if slug_en else "—"
    medium_cell = f"[medium](./{path}/medium/{idx:02d}.html)" if targets.get("medium") and slug_en else "—"

    return f"| {idx} | {title} | {ko_cell} | {en_cell} | {medium_cell} | {status} |"


def _series_section(s: dict) -> str:
    sid = s["id"]
    title_ko = s.get("title", {}).get("ko", sid)
    title_en = s.get("title", {}).get("en", sid)
    desc_ko = s.get("description", {}).get("ko", "")
    path = s["path"]
    langs = s.get("languages", [])
    targets = s.get("targets", {})
    level = s.get("level", "")
    status = s.get("status", "planned")

    target_list = ", ".join(k for k, v in targets.items() if v)
    lang_list = ", ".join(langs)

    per = s.get("per", {})
    arts_ko = {a["idx"]: a for a in per.get("ko", {}).get("articles", [])}
    arts_en = {a["idx"]: a for a in per.get("en", {}).get("articles", [])}

    all_idx = sorted(set(list(arts_ko.keys()) + list(arts_en.keys())))

    lines = [
        f"### {title_ko} (`{sid}`)",
        "",
        desc_ko,
        "",
        f"- 언어: {lang_list}" if lang_list else "",
        f"- 발행 대상: {target_list}" if target_list else "",
        f"- 경로: [`{path}/`](./{path}/)",
        "",
        "| # | Title | KO | EN | Medium | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines = [l for l in lines if l is not None]

    if all_idx:
        for i in all_idx:
            lines.append(_series_row(s, i, arts_ko.get(i), arts_en.get(i)))
    else:
        lines.append(f"| — | *(no articles on disk)* | — | — | — | {STATUS_DISPLAY.get(status, status)} |")

    return "\n".join(lines)


def main() -> int:
    data = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    series_list = data.get("series", [])

    by_category: dict[str, list] = {}
    for s in series_list:
        cat = s.get("category", "other")
        by_category.setdefault(cat, []).append(s)

    out_lines = [
        "# Series Index",
        "",
        "전체 콘텐츠 시리즈의 목록과 발행 상태. 단일 출처는 [`series.yaml`](./series.yaml).",
        "",
        "> 이 파일은 `scripts/gen_series_md.py`로 자동 생성됩니다.",
        "> 직접 편집하지 마세요 — front matter `status` 변경 후 `python3 scripts/sync_series_per.py && python3 scripts/gen_series_md.py`를 실행하세요.",
        "",
        "## Status Legend",
        "",
        "| Status | Meaning |",
        "| --- | --- |",
        "| Draft | 초안 작성 중 |",
        "| Content Ready | 본문 완성, 코드 미검증 |",
        "| Code Checked | 코드 실행 검증 완료 |",
        "| Publish Ready | 발행 준비 완료 (채널별 제목 포함) |",
        "| Ready | 발행 준비 완료 (레거시 alias) |",
        "| Published | 발행 완료 |",
        "| Needs Update | 업데이트 필요 (API 변경 등) |",
        "",
        "---",
        "",
    ]

    category_order = ["azure", "llm", "other"]
    for cat in category_order:
        if cat not in by_category:
            continue
        header = CATEGORY_HEADERS.get(cat, f"## {cat.title()}")
        out_lines.append(header)
        out_lines.append("")
        for s in by_category[cat]:
            out_lines.append(_series_section(s))
            out_lines.append("")
        out_lines.append("---")
        out_lines.append("")

    SERIES_MD.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Generated SERIES.md ({len(series_list)} series)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
