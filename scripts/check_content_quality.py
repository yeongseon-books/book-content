from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path
from typing import Protocol, cast


class FrontmatterModule(Protocol):
    def loads(self, text: str) -> object: ...


frontmatter = cast(
    FrontmatterModule,
    cast(object, importlib.import_module("frontmatter")),
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

LANG_DIRS = {"ko", "en"}
REFS_HEADERS = {"## 참고 자료", "## References"}
TAGS_PREFIX = "Tags: "

FENCE_OPEN_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
GITHUB_REPO_RE = re.compile(r"https?://github\.com/([^/\s]+)/([^/\s)]+)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check advisory content quality items."
    )
    _ = parser.add_argument(
        "--series", help="check only one series id (content/<series>/)"
    )
    return parser.parse_args()


def iter_articles(series: str | None) -> list[Path]:
    if series:
        series_dir = CONTENT_DIR / series
        if not series_dir.is_dir():
            return []
        roots = [series_dir]
    else:
        roots = [path for path in sorted(CONTENT_DIR.iterdir()) if path.is_dir()]

    items: list[Path] = []
    for root in roots:
        for lang in LANG_DIRS:
            lang_dir = root / lang
            if not lang_dir.is_dir():
                continue
            items.extend(sorted(lang_dir.glob("*.md")))
    return items


def normalize_lang_token(info: str) -> str:
    if not info:
        return ""
    token = info.split()[0].strip()
    if token.startswith("{.") and token.endswith("}"):
        token = token[2:-1]
    token = token.strip("{}")
    return token.lower()


def is_fence_close(line: str, fence_char: str, fence_len: int) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if not stripped.startswith(fence_char * fence_len):
        return False

    run_len = 0
    for ch in stripped:
        if ch == fence_char:
            run_len += 1
        else:
            break
    if run_len < fence_len:
        return False
    return stripped[run_len:].strip() == ""


def inspect_fences(lines: list[str]) -> tuple[list[str], bool]:
    warnings: list[str] = []
    has_code_examples = False

    in_fence = False
    fence_char = ""
    fence_len = 0

    for line_no, line in enumerate(lines, start=1):
        stripped_left = line.lstrip()
        if not in_fence:
            match = FENCE_OPEN_RE.match(stripped_left)
            if not match:
                continue

            fence = match.group(1)
            info = match.group(2).strip()
            lang = normalize_lang_token(info)

            if not lang:
                warnings.append(f"Code block at line {line_no} missing language tag")

            if lang != "mermaid":
                has_code_examples = True

            in_fence = True
            fence_char = fence[0]
            fence_len = len(fence)
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0

    return warnings, has_code_examples


def find_missing_image_alt(lines: list[str]) -> list[str]:
    warnings: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line_no, line in enumerate(lines, start=1):
        stripped_left = line.lstrip()
        if not in_fence:
            match = FENCE_OPEN_RE.match(stripped_left)
            if match:
                in_fence = True
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                continue

            for image_match in IMAGE_RE.finditer(line):
                if not image_match.group(1).strip():
                    warnings.append(f"Image at line {line_no} missing alt text")
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0

    return warnings


def extract_references_section(lines: list[str]) -> str:
    start = -1
    for idx, line in enumerate(lines):
        if line.strip() in REFS_HEADERS:
            start = idx + 1
            break
    if start < 0:
        return ""

    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith(TAGS_PREFIX):
            end = idx
            break
    return "\n".join(lines[start:end])


def has_companion_repo_link(ref_text: str, series_id: str) -> bool:
    for match in GITHUB_REPO_RE.finditer(ref_text):
        repo = match.group(2).removesuffix(".git").lower()
        if repo == series_id.lower():
            return True
    return False


def check_article(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as exc:
        return [f"Unable to parse front matter: {exc}"]

    post_obj = post
    metadata = cast(dict[str, object], getattr(post_obj, "metadata"))
    content = cast(str, getattr(post_obj, "content"))

    series_id = metadata.get("series")
    if not isinstance(series_id, str) or not series_id:
        series_id = path.parts[path.parts.index("content") + 1]

    lines = content.splitlines()
    warnings, has_code_examples = inspect_fences(lines)
    warnings.extend(find_missing_image_alt(lines))

    if has_code_examples:
        refs = extract_references_section(lines)
        if not refs:
            warnings.append(
                "Has code examples but no references section to place companion repo link"
            )
        elif not has_companion_repo_link(refs, series_id):
            warnings.append(
                f"Has code examples but references lack companion GitHub repo ({series_id})"
            )

    return warnings


def main() -> int:
    args = parse_args()
    series = cast(str | None, args.series)

    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1

    articles = iter_articles(series)
    if series and not articles:
        print(f"No articles found for series: {series}", file=sys.stderr)
        return 1

    print("Checking content quality...")
    checked = 0
    warning_count = 0

    for md in articles:
        if md.parent.name not in LANG_DIRS:
            continue

        checked += 1
        warnings = check_article(md)
        if not warnings:
            continue

        rel = md.relative_to(REPO_ROOT)
        print(f"== {rel}")
        for warning in warnings:
            warning_count += 1
            print(f"  WARNING: {warning}")

    print(f"\nSummary: {checked} articles checked, {warning_count} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
