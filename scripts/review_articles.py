#!/usr/bin/env python3
# pyright: reportMissingTypeStubs=false, reportExplicitAny=false, reportUnusedCallResult=false, reportUnknownVariableType=false, reportAny=false, reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_article_structure import (
    STRICT_STATUSES,
    check_article as check_structural,
)
from scripts.check_content_quality import (
    FENCE_OPEN_RE,
    IMAGE_RE,
    check_article as check_quality,
    is_fence_close,
)
from scripts.check_frontmatter import load_catalog, validate_article
from scripts.check_links import (
    LINK_RE,
    check_file as check_links_file,
    is_external,
    strip_code_fences,
)
from scripts.lint_captions import IMG_RE, lint_caption

CONTENT_DIR = REPO_ROOT / "content"
VALID_LANGS = {"ko", "en"}
CSV_COLUMNS = [
    "series",
    "language",
    "status",
    "slug",
    "path",
    "paired",
    "body_words",
    "code_blocks",
    "images",
    "structural_errors",
    "structural_warnings",
    "frontmatter_errors",
    "quality_warnings",
    "infra_warnings",
    "caption_warnings",
    "link_warnings",
    "severity",
    "action",
]
# Series-level signals that pollute per-article severity. They reflect
# infrastructure backlog (e.g., missing companion GitHub repo for a series),
# not authoring defects in an individual article. We preserve them in their
# own column but exclude them from the severity escalator.
INFRA_QUALITY_PATTERNS = (
    "lack companion GitHub repo",
    "no references section to place companion repo link",
)


def split_infra_warnings(warnings: list[str]) -> tuple[list[str], list[str]]:
    """Partition quality warnings into (article-level, series-infra-level)."""
    article: list[str] = []
    infra: list[str] = []
    for warning in warnings:
        if any(pattern in warning for pattern in INFRA_QUALITY_PATTERNS):
            infra.append(warning)
        else:
            article.append(warning)
    return article, infra


SEVERITY_ORDER = {
    "parse-error": 0,
    "blocker": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "pass": 5,
}


@dataclass
class ArticleRecord:
    row: dict[str, Any]
    issue_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build per-article review reports.")
    _ = parser.add_argument("--series", help="limit to one series id")
    _ = parser.add_argument(
        "--output-dir",
        default="reports/article-review",
        help="output directory for report bundle",
    )
    return parser.parse_args()


def resolve_output_dir(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def iter_articles(series: str | None) -> list[Path]:
    roots: list[Path]
    if series:
        root = CONTENT_DIR / series
        if not root.is_dir():
            raise SystemExit(f"Series not found: {series}")
        roots = [root]
    else:
        roots = sorted(path for path in CONTENT_DIR.iterdir() if path.is_dir())

    files: list[Path] = []
    for root in roots:
        for lang in ("ko", "en"):
            lang_dir = root / lang
            if lang_dir.is_dir():
                files.extend(sorted(lang_dir.glob("*.md")))
    return files


def csv_join(items: list[str]) -> str:
    return " | ".join(items)


def count_internal_links(md: Path) -> int:
    text = strip_code_fences(md.read_text(encoding="utf-8"))
    count = 0
    for match in LINK_RE.finditer(text):
        target = match.group(3).strip()
        if not is_external(target):
            count += 1
    return count


def opposite_lang_path(path: Path) -> Path:
    other_lang = "en" if path.parent.name == "ko" else "ko"
    return path.parent.parent / other_lang


def has_bilingual_pair(path: Path) -> bool:
    prefix = path.stem.split("-", 1)[0]
    other_dir = opposite_lang_path(path)
    if not other_dir.is_dir():
        return False
    return any(other_dir.glob(f"{prefix}-*.md"))


def count_code_blocks_and_strip(lines: list[str]) -> tuple[int, list[str]]:
    code_blocks = 0
    visible_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        stripped_left = line.lstrip()
        if not in_fence:
            match = FENCE_OPEN_RE.match(stripped_left)
            if match:
                in_fence = True
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                code_blocks += 1
                continue
            visible_lines.append(line)
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0

    return code_blocks, visible_lines


def compute_size_signals(path: Path) -> tuple[int, int, int]:
    text = path.read_text(encoding="utf-8")
    post = frontmatter.loads(text)
    lines = post.content.splitlines()
    code_blocks, visible_lines = count_code_blocks_and_strip(lines)
    visible_text = "\n".join(visible_lines)
    body_words = len(re.findall(r"\S+", visible_text))
    images = len(IMAGE_RE.findall(post.content))
    return body_words, code_blocks, images


def caption_warnings(path: Path) -> list[str]:
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in IMG_RE.finditer(line):
            alt = match.group(1)
            issues = lint_caption(alt)
            if issues:
                warnings.append(f"line {line_no}: {alt!r} [{', '.join(issues)}]")
    return warnings


def severity_and_action(
    *,
    status: str,
    parse_error: bool,
    structural_errors: list[str],
    frontmatter_errors: list[str],
    structural_warnings: list[str],
    frontmatter_warnings: list[str],
    quality_warnings: list[str],
    caption_warns: list[str],
    link_warns: list[str],
) -> tuple[str, str]:
    if parse_error:
        return "parse-error", "fix-now"

    if structural_errors or frontmatter_errors:
        return "blocker", "fix-now"

    warning_count = sum(
        len(items)
        for items in (
            structural_warnings,
            frontmatter_warnings,
            quality_warnings,
            caption_warns,
            link_warns,
        )
    )

    if status in STRICT_STATUSES and warning_count >= 2:
        return "high", "needs-deep-review"
    if (status in STRICT_STATUSES and warning_count == 1) or warning_count > 0:
        if status in STRICT_STATUSES:
            return "medium", "needs-light-edit"
        return "low", "triage-when-publishing"
    return "pass", "pass"


def record_issue_count(
    structural_errors: list[str],
    structural_warnings: list[str],
    frontmatter_errors: list[str],
    frontmatter_warnings: list[str],
    quality_warnings: list[str],
    caption_warns: list[str],
    link_warns: list[str],
) -> int:
    return sum(
        len(items)
        for items in (
            structural_errors,
            structural_warnings,
            frontmatter_errors,
            frontmatter_warnings,
            quality_warnings,
            caption_warns,
            link_warns,
        )
    )


def analyze_article(path: Path, catalog: dict[str, dict[str, Any]]) -> ArticleRecord:
    rel_path = path.relative_to(REPO_ROOT).as_posix()
    series = path.parts[path.parts.index("content") + 1]
    language = path.parent.name
    slug = path.stem
    paired = has_bilingual_pair(path)
    status = "unknown"
    body_words = 0
    code_blocks = 0
    images = 0

    frontmatter_errors, frontmatter_warnings = validate_article(path, catalog)
    parse_error = any("parse error" in error for error in frontmatter_errors)

    structural_errors: list[str] = []
    structural_warnings: list[str] = []
    quality_warnings: list[str] = []
    infra_warnings: list[str] = []
    caption_warns: list[str] = []
    link_warns: list[str] = []
    internal_links = 0

    if not parse_error:
        text = path.read_text(encoding="utf-8")
        post = frontmatter.loads(text)
        metadata = post.metadata
        status_value = metadata.get("status")
        if isinstance(status_value, str):
            status = status_value
        structural_errors, structural_warnings = check_structural(path, warn_all=True)
        quality_warnings, infra_warnings = split_infra_warnings(check_quality(path))
        caption_warns = caption_warnings(path)
        link_warns = check_links_file(path)
        internal_links = count_internal_links(path)
        body_words, code_blocks, images = compute_size_signals(path)

    severity, action = severity_and_action(
        status=status,
        parse_error=parse_error,
        structural_errors=structural_errors,
        frontmatter_errors=frontmatter_errors,
        structural_warnings=structural_warnings,
        frontmatter_warnings=frontmatter_warnings,
        quality_warnings=quality_warnings,
        caption_warns=caption_warns,
        link_warns=link_warns,
    )

    issue_count = record_issue_count(
        structural_errors,
        structural_warnings,
        frontmatter_errors,
        frontmatter_warnings,
        quality_warnings,
        caption_warns,
        link_warns,
    )

    row = {
        "series": series,
        "language": language,
        "status": status,
        "slug": slug,
        "path": rel_path,
        "paired": str(paired).lower(),
        "body_words": body_words,
        "code_blocks": code_blocks,
        "images": images,
        "structural_errors": csv_join(structural_errors),
        "structural_warnings": csv_join(structural_warnings),
        "frontmatter_errors": csv_join(frontmatter_errors + frontmatter_warnings),
        "quality_warnings": csv_join(quality_warnings),
        "infra_warnings": csv_join(infra_warnings),
        "caption_warnings": csv_join(caption_warns),
        "link_warnings": csv_join(link_warns),
        "severity": severity,
        "action": action,
        "_issue_count": issue_count,
        "_internal_links": internal_links,
    }
    return ArticleRecord(row=row, issue_count=issue_count)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in CSV_COLUMNS})


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = [{key: row[key] for key in CSV_COLUMNS} for row in rows]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def build_summary_table(rows: list[dict[str, Any]]) -> str:
    total = len(rows)
    by_lang = Counter(row["language"] for row in rows)
    by_status = Counter(row["status"] for row in rows)
    by_severity = Counter(row["severity"] for row in rows)
    summary_rows = [
        ["total_articles", total],
        ["language:ko", by_lang.get("ko", 0)],
        ["language:en", by_lang.get("en", 0)],
    ]
    for status, count in sorted(by_status.items()):
        summary_rows.append([f"status:{status}", count])
    for severity in ["parse-error", "blocker", "high", "medium", "low", "pass"]:
        summary_rows.append([f"severity:{severity}", by_severity.get(severity, 0)])
    return markdown_table(["metric", "count"], summary_rows)


def build_top_issues(rows: list[dict[str, Any]]) -> str:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            -int(row["_issue_count"]),
            SEVERITY_ORDER.get(str(row["severity"]), 99),
            row["path"],
        ),
    )[:20]
    issue_rows = [
        [
            row["path"],
            row["severity"],
            row["action"],
            row["_issue_count"],
        ]
        for row in sorted_rows
    ]
    return markdown_table(["path", "severity", "action", "issues"], issue_rows)


def build_series_rollup(rows: list[dict[str, Any]]) -> str:
    buckets: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        series = str(row["series"])
        buckets[series]["total"] += 1
        buckets[series][str(row["severity"])] += 1

    rollup_rows: list[list[Any]] = []
    for series in sorted(buckets):
        counts = buckets[series]
        rollup_rows.append(
            [
                series,
                counts.get("total", 0),
                counts.get("blocker", 0) + counts.get("parse-error", 0),
                counts.get("high", 0),
                counts.get("medium", 0),
                counts.get("low", 0),
                counts.get("pass", 0),
            ]
        )
    return markdown_table(
        ["series_id", "total", "blockers", "high", "medium", "low", "pass"], rollup_rows
    )


def build_top_severity_sections(rows: list[dict[str, Any]]) -> str:
    severity_groups = defaultdict(list)
    for row in rows:
        for column in (
            "structural_errors",
            "structural_warnings",
            "frontmatter_errors",
            "quality_warnings",
            "infra_warnings",
            "caption_warnings",
            "link_warnings",
        ):
            value = str(row[column]).strip()
            if not value:
                continue
            for item in value.split(" | "):
                severity_groups[column].append(item)

    headers = ["dimension", "top issues"]
    body: list[list[Any]] = []
    for column, label in (
        ("structural_errors", "structural_errors"),
        ("frontmatter_errors", "frontmatter_errors"),
        ("structural_warnings", "structural_warnings"),
        ("quality_warnings", "quality_warnings"),
        ("infra_warnings", "infra_warnings (series-level, excluded from severity)"),
        ("caption_warnings", "caption_warnings"),
        ("link_warnings", "link_warnings"),
    ):
        top = Counter(severity_groups[column]).most_common(5)
        rendered = (
            "<br>".join(f"{count}× {issue}" for issue, count in top) if top else "-"
        )
        body.append([label, rendered])
    return markdown_table(headers, body)


def write_index(path: Path, rows: list[dict[str, Any]]) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = [
        f"# Article Review Report — generated {generated_at}",
        "",
        "> Severity rubric: series-level `infra_warnings` (e.g., missing companion GitHub repo) are tracked separately and **do not escalate per-article severity**. They appear in their own column and in the Top issues table for backlog tracking.",
        "",
        "## Summary",
        build_summary_table(rows),
        "",
        "## Top issues by dimension",
        build_top_severity_sections(rows),
        "",
        "## Top 20 worst articles",
        build_top_issues(rows),
        "",
        "## Per-series rollup",
        build_series_rollup(rows),
        "",
        "---",
        "Regenerate with: `python3 scripts/review_articles.py`",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog()
    articles = iter_articles(args.series)
    records = [analyze_article(path, catalog) for path in articles]
    rows = [record.row for record in records]

    write_csv(output_dir / "articles.csv", rows)
    write_json(output_dir / "articles.json", rows)
    write_index(output_dir / "index.md", rows)

    expected = len(articles)
    actual = len(rows)
    discrepancy = "" if expected == actual else f" (discrepancy: expected {expected})"
    print(f"Reviewed {actual} articles{discrepancy}")
    print(f"Reports written to {output_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
