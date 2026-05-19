#!/usr/bin/env python3
# pyright: reportMissingTypeStubs=false, reportExplicitAny=false, reportAny=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnannotatedClassAttribute=false, reportUnusedCallResult=false
"""Audit cross-series quality problems and write ranked reports.

Signals:
- BadImg: PNG height <= 100px under assets/<series>/
- Synt: Python fenced code blocks that fail ast.parse()
- BrkLink: github.com/yeongseon-books/<repo> links where the repo does not exist
- Shrt: markdown body shorter than 150 lines (after front matter)
- NoEn: ko article with no en counterpart at the same basename

Python syntax skip rule:
- If the first non-empty line inside a Python fence starts with
  ``# pseudocode``, ``# pseudo-code``, or ``# example``, the block is treated
  as explicitly illustrative and is skipped.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
ASSETS_DIR = REPO_ROOT / "assets"
OUTPUT_DIR = REPO_ROOT / ".sisyphus" / "quality-audit"
JSON_OUTPUT = OUTPUT_DIR / "audit.json"
MD_OUTPUT = OUTPUT_DIR / "audit.md"

LANG_DIRS = ("ko", "en")
SHORT_ARTICLE_LINES = 150
BAD_IMAGE_HEIGHT = 100
KNOWN_EXISTING_REPOS = {"book-content", "book-public-assets"}
KNOWN_LOW_HEIGHT_IMAGE_EXEMPTIONS = {
    "assets/azure-app-service-101/04/01-deployment-pipeline.en.png",
    "assets/azure-app-service-101/04/01-deployment-pipeline.ko.png",
    "assets/azure-app-service-101/05/key-vault-reference-flow.en.png",
    "assets/azure-app-service-101/05/key-vault-reference-flow.ko.png",
    "assets/azure-app-service-101/06/03-correlation-id-flow.en.png",
    "assets/azure-app-service-101/06/03-correlation-id-flow.ko.png",
}
PYTHON_INFO_STRINGS = {"python", "py", "python3", "py3"}
SKIP_PREFIXES = ("# pseudocode", "# pseudo-code", "# example")
GITHUB_REPO_RE = re.compile(
    r"https?://(?:www\.)?github\.com/yeongseon-books/([A-Za-z0-9_.-]+)"
)
FENCE_OPEN_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")


@dataclass(slots=True)
class AuditItem:
    kind: str
    path: str
    line: int
    message: str
    article: str | None = None
    lang: str | None = None
    code: str | None = None
    image: str | None = None
    width: int | None = None
    height: int | None = None
    repo: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit content-series quality.")
    parser.add_argument("--series", default=None, help="Only audit one series id")
    parser.add_argument(
        "--gate",
        type=int,
        default=None,
        help="Fail if any series has more than N total issues",
    )
    parser.add_argument("--json-output", type=Path, default=JSON_OUTPUT)
    parser.add_argument("--md-output", type=Path, default=MD_OUTPUT)
    parser.add_argument(
        "--dated-md-output",
        type=Path,
        default=OUTPUT_DIR / f"audit-{dt.date.today():%Y-%m}.md",
        help="Optional dated markdown snapshot path",
    )
    return parser.parse_args()


def iter_series_dirs(series: str | None) -> list[Path]:
    if series:
        target = CONTENT_DIR / series
        return [target] if (target / "series.yaml").is_file() else []
    return sorted(
        path
        for path in CONTENT_DIR.iterdir()
        if path.is_dir() and (path / "series.yaml").is_file()
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, int]:
    if not text.startswith("---\n"):
        return text, 1
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text, 1
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body = "\n".join(lines[index + 1 :])
            return body, index + 2
    return text, 1


def normalize_lang_token(info: str) -> str:
    token = info.split()[0].strip() if info.strip() else ""
    if token.startswith("{.") and token.endswith("}"):
        token = token[2:-1]
    return token.strip("{}").lower()


def is_fence_close(line: str, fence_char: str, fence_len: int) -> bool:
    stripped = line.strip()
    if not stripped.startswith(fence_char * fence_len):
        return False
    run_len = 0
    for char in stripped:
        if char == fence_char:
            run_len += 1
        else:
            break
    return run_len >= fence_len and stripped[run_len:].strip() == ""


def strip_fences(text: str) -> str:
    result: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in text.splitlines():
        stripped_left = line.lstrip()
        if not in_fence:
            match = FENCE_OPEN_RE.match(stripped_left)
            if match:
                in_fence = True
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                continue
            result.append(line)
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0
    return "\n".join(result)


def extract_python_fences(body: str, body_start_line: int) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    lines = body.splitlines()
    in_fence = False
    fence_char = ""
    fence_len = 0
    current_start = 0
    current_lines: list[str] = []

    for index, line in enumerate(lines, start=body_start_line):
        stripped_left = line.lstrip()
        if not in_fence:
            match = FENCE_OPEN_RE.match(stripped_left)
            if not match:
                continue
            lang = normalize_lang_token(match.group(2).strip())
            if lang not in PYTHON_INFO_STRINGS:
                continue
            in_fence = True
            fence_char = match.group(1)[0]
            fence_len = len(match.group(1))
            current_start = index
            current_lines = []
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            blocks.append((current_start, "\n".join(current_lines)))
            in_fence = False
            fence_char = ""
            fence_len = 0
            current_start = 0
            current_lines = []
            continue

        current_lines.append(line)

    return blocks


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def should_skip_python_block(code: str) -> bool:
    first_line = first_nonempty_line(code).lower()
    return any(first_line.startswith(prefix) for prefix in SKIP_PREFIXES)


def normalize_python_block(code: str) -> str:
    return textwrap.dedent(code).strip("\n")


def try_parse_python(code: str) -> tuple[bool, str | None, int | None]:
    try:
        ast.parse(code)
        return True, None, None
    except SyntaxError as exc:
        original_message = exc.msg
        original_line = exc.lineno

    wrapped = "def _audit_wrapper():\n" + "\n".join(
        f"    {line}" if line else "" for line in code.splitlines()
    )
    try:
        ast.parse(wrapped)
        return True, None, None
    except SyntaxError:
        return False, original_message, original_line


def get_png_size(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image  # type: ignore[import-not-found]

        with Image.open(path) as image:
            width, height = image.size
            return int(width), int(height)
    except Exception:
        with path.open("rb") as handle:
            signature = handle.read(8)
            if signature != b"\x89PNG\r\n\x1a\n":
                raise ValueError(f"not a PNG file: {path}")
            length = int.from_bytes(handle.read(4), "big")
            chunk_type = handle.read(4)
            if length != 13 or chunk_type != b"IHDR":
                raise ValueError(f"invalid IHDR chunk: {path}")
            width = int.from_bytes(handle.read(4), "big")
            height = int.from_bytes(handle.read(4), "big")
            return width, height


class RepoExistenceCache:
    def __init__(self) -> None:
        self._cache: dict[str, bool] = {repo: True for repo in KNOWN_EXISTING_REPOS}
        self.method = "gh"

    def exists(self, repo: str) -> bool:
        cached = self._cache.get(repo)
        if cached is not None:
            return cached

        env = os.environ.copy()
        env.setdefault("CI", "true")
        env.setdefault("GIT_TERMINAL_PROMPT", "0")
        env.setdefault("GH_PAGER", "cat")
        result = subprocess.run(
            ["gh", "repo", "view", f"yeongseon-books/{repo}"],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            self._cache[repo] = True
            return True
        missing_markers = ("not found", "Could not resolve", "HTTP 404")
        stderr = f"{result.stdout}\n{result.stderr}"
        if any(marker.lower() in stderr.lower() for marker in missing_markers):
            self._cache[repo] = False
            return False

        self.method = "gh-with-errors"
        self._cache[repo] = repo in KNOWN_EXISTING_REPOS
        return self._cache[repo]


def audit_images(series_id: str) -> list[AuditItem]:
    problems: list[AuditItem] = []
    series_assets_dir = ASSETS_DIR / series_id
    if not series_assets_dir.is_dir():
        return problems

    for png in sorted(series_assets_dir.rglob("*.png")):
        width, height = get_png_size(png)
        if height > BAD_IMAGE_HEIGHT:
            continue
        rel = display_path(png)
        if rel in KNOWN_LOW_HEIGHT_IMAGE_EXEMPTIONS:
            continue
        problems.append(
            AuditItem(
                kind="BadImg",
                path=rel,
                line=1,
                message=f"PNG height {height}px <= {BAD_IMAGE_HEIGHT}px",
                image=png.name,
                width=width,
                height=height,
            )
        )
    return problems


def audit_articles(
    series_dir: Path, repo_cache: RepoExistenceCache
) -> dict[str, list[AuditItem]]:
    results = {"Synt": [], "BrkLink": [], "Shrt": [], "NoEn": []}
    en_files: set[str] = set()

    for lang in LANG_DIRS:
        lang_dir = series_dir / lang
        if not lang_dir.is_dir():
            continue

        for md in sorted(lang_dir.glob("*.md")):
            rel = display_path(md)
            text = md.read_text(encoding="utf-8")
            body, body_start_line = split_frontmatter(text)
            lines = body.splitlines()

            if lang == "en":
                en_files.add(md.name)

            if len(lines) < SHORT_ARTICLE_LINES:
                results["Shrt"].append(
                    AuditItem(
                        kind="Shrt",
                        path=rel,
                        line=body_start_line,
                        message=f"markdown body has {len(lines)} lines (< {SHORT_ARTICLE_LINES})",
                        article=md.name,
                        lang=lang,
                    )
                )

            stripped_for_links = strip_fences(body)
            for line_no, line in enumerate(
                stripped_for_links.splitlines(), start=body_start_line
            ):
                for match in GITHUB_REPO_RE.finditer(line):
                    repo = match.group(1)
                    if repo_cache.exists(repo):
                        continue
                    results["BrkLink"].append(
                        AuditItem(
                            kind="BrkLink",
                            path=rel,
                            line=line_no,
                            message=f"referenced repo does not exist: yeongseon-books/{repo}",
                            article=md.name,
                            lang=lang,
                            repo=repo,
                        )
                    )

            for fence_start, code in extract_python_fences(body, body_start_line):
                normalized_code = normalize_python_block(code)
                if should_skip_python_block(normalized_code):
                    continue
                ok, message, error_line = try_parse_python(normalized_code)
                if ok:
                    continue
                absolute_line = fence_start + (error_line or 1)
                results["Synt"].append(
                    AuditItem(
                        kind="Synt",
                        path=rel,
                        line=absolute_line,
                        message=message or "syntax error",
                        article=md.name,
                        lang=lang,
                        code=first_nonempty_line(normalized_code)[:160],
                    )
                )

    ko_dir = series_dir / "ko"
    if ko_dir.is_dir():
        for ko_md in sorted(ko_dir.glob("*.md")):
            if ko_md.name in en_files:
                continue
            results["NoEn"].append(
                AuditItem(
                    kind="NoEn",
                    path=display_path(ko_md),
                    line=1,
                    message=f"missing English counterpart: content/{series_dir.name}/en/{ko_md.name}",
                    article=ko_md.name,
                    lang="ko",
                )
            )

    return results


def summarize_series(
    series_dir: Path, repo_cache: RepoExistenceCache
) -> dict[str, Any]:
    series_id = series_dir.name
    details = audit_articles(series_dir, repo_cache)
    details["BadImg"] = audit_images(series_id)

    counts = {kind: len(items) for kind, items in details.items()}
    total = sum(counts.values())
    max_issue_kind = (
        max(counts.items(), key=lambda item: (item[1], item[0]))[0] if counts else None
    )

    return {
        "series": series_id,
        "counts": counts,
        "total": total,
        "max_issue_kind": max_issue_kind,
        "examples": {
            kind: [asdict(item) for item in items[:10]]
            for kind, items in details.items()
            if items
        },
        "items": {
            kind: [asdict(item) for item in items]
            for kind, items in details.items()
            if items
        },
    }


def markdown_table(results: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Rank | Series | Total | BadImg | Synt | BrkLink | Shrt | NoEn |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, result in enumerate(results, start=1):
        counts = result["counts"]
        lines.append(
            f"| {index} | `{result['series']}` | {result['total']} | {counts.get('BadImg', 0)} | {counts.get('Synt', 0)} | {counts.get('BrkLink', 0)} | {counts.get('Shrt', 0)} | {counts.get('NoEn', 0)} |"
        )
    return lines


def render_example(item: dict[str, Any]) -> str:
    suffix_parts: list[str] = []
    if item.get("repo"):
        suffix_parts.append(f"repo={item['repo']}")
    if item.get("width") is not None and item.get("height") is not None:
        suffix_parts.append(f"size={item['width']}x{item['height']}")
    if item.get("code"):
        suffix_parts.append(f"code=`{item['code']}`")
    suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""
    return f"- `{item['path']}:{item['line']}` — {item['message']}{suffix}"


def make_markdown(payload: dict[str, Any]) -> str:
    results = payload["results"]
    problem_series = [result for result in results if result["total"] > 0]
    lines = [
        "# Cross-Series Quality Audit",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "Signals:",
        f"- `BadImg`: PNG height <= {BAD_IMAGE_HEIGHT}px under `assets/<series>/`",
        "- `Synt`: Python fenced code blocks that fail `ast.parse()`",
        "- `BrkLink`: `github.com/yeongseon-books/<repo>` references to missing repos",
        f"- `Shrt`: markdown body shorter than {SHORT_ARTICLE_LINES} lines after front matter",
        "- `NoEn`: `ko/*.md` file with no matching `en/*.md` basename",
        "",
        "Python syntax skip rule:",
        "- Skip a Python fence only when its first non-empty line starts with `# pseudocode`, `# pseudo-code`, or `# example`.",
        "",
        "## Summary",
        "",
        f"- Series audited: **{payload['series_count']}**",
        f"- Series with any issue: **{payload['problem_series_count']}**",
        f"- Series at or above 5 issues: **{payload['series_with_5_plus']}**",
        f"- Total issues: **{payload['totals']['all']}**",
        f"  - BadImg: **{payload['totals']['BadImg']}**",
        f"  - Synt: **{payload['totals']['Synt']}**",
        f"  - BrkLink: **{payload['totals']['BrkLink']}**",
        f"  - Shrt: **{payload['totals']['Shrt']}**",
        f"  - NoEn: **{payload['totals']['NoEn']}**",
        f"- Repo existence check method: **{payload['repo_check_method']}**",
        "",
        "## Ranked series",
        "",
        *markdown_table(problem_series),
    ]

    for result in problem_series:
        counts = result["counts"]
        lines.extend(
            [
                "",
                f"## {result['series']} — Total {result['total']}",
                "",
                f"- BadImg={counts.get('BadImg', 0)} Synt={counts.get('Synt', 0)} BrkLink={counts.get('BrkLink', 0)} Shrt={counts.get('Shrt', 0)} NoEn={counts.get('NoEn', 0)}",
            ]
        )
        for kind in ("BadImg", "Synt", "BrkLink", "Shrt", "NoEn"):
            examples = result["examples"].get(kind, [])
            if not examples:
                continue
            lines.extend(["", f"### {kind}"])
            for item in examples[:5]:
                lines.append(render_example(item))
            remaining = counts.get(kind, 0) - min(len(examples), 5)
            if remaining > 0:
                lines.append(f"- ... {remaining} more")

    return "\n".join(lines) + "\n"


def build_payload(
    results: list[dict[str, Any]], repo_check_method: str, gate: int | None
) -> dict[str, Any]:
    totals = {"BadImg": 0, "Synt": 0, "BrkLink": 0, "Shrt": 0, "NoEn": 0, "all": 0}
    for result in results:
        for kind in ("BadImg", "Synt", "BrkLink", "Shrt", "NoEn"):
            totals[kind] += result["counts"].get(kind, 0)
        totals["all"] += result["total"]

    problem_series_count = sum(1 for result in results if result["total"] > 0)
    series_with_5_plus = sum(1 for result in results if result["total"] >= 5)
    failing_series = [
        result["series"]
        for result in results
        if gate is not None and result["total"] > gate
    ]

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "series_count": len(results),
        "problem_series_count": problem_series_count,
        "series_with_5_plus": series_with_5_plus,
        "gate": gate,
        "gate_failed_series": failing_series,
        "repo_check_method": repo_check_method,
        "totals": totals,
        "results": results,
    }


def main() -> int:
    args = parse_args()
    series_dirs = iter_series_dirs(args.series)
    if not series_dirs:
        print("No series found to audit", file=sys.stderr)
        return 1

    repo_cache = RepoExistenceCache()
    results = [summarize_series(series_dir, repo_cache) for series_dir in series_dirs]
    results.sort(
        key=lambda item: (
            -item["total"],
            -item["counts"].get("BadImg", 0),
            -item["counts"].get("Synt", 0),
            item["series"],
        )
    )

    payload = build_payload(results, repo_cache.method, args.gate)
    markdown = make_markdown(payload)

    write_json(args.json_output, payload)
    write_markdown(args.md_output, markdown)
    if args.dated_md_output:
        write_markdown(args.dated_md_output, markdown)

    print(f"series_audited={payload['series_count']}")
    print(f"problem_series={payload['problem_series_count']}")
    print(f"total_issues={payload['totals']['all']}")
    print(f"json_output={display_path(args.json_output)}")
    print(f"md_output={display_path(args.md_output)}")
    if args.dated_md_output:
        print(f"dated_md_output={display_path(args.dated_md_output)}")

    if args.gate is None:
        return 0
    return 1 if payload["gate_failed_series"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
