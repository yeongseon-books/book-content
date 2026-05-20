"""Check content quality: boilerplate, length, empty headings, josa, AI slop.

This script is warning-only by default (exit 0). Pass --strict to exit 1 on errors.

Checks:
1. Ko boilerplate patterns (3 known phrases from Q-Loop regression)
2. En boilerplate pattern ("The core of ... is not the feature name")
3. Article body length (ko: warn <7000 chars, error <5000; en: warn <800 words)
4. Empty H2 headings (## heading followed immediately by another ## or end)
5. Ko josa errors (받침-sensitive 를/을 misuse on English words)
6. En AI slop words (leverage, robust, seamlessly, "In summary")
7. Code blocks missing language tag
8. Images missing alt text

Exit code: 0 (warning-only mode, default), 1 (--strict and errors found).
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path
from typing import Protocol, cast

# ---------------------------------------------------------------------------
# Frontmatter import (lazy, avoids type issues)
# ---------------------------------------------------------------------------


class FrontmatterModule(Protocol):
    def loads(self, text: str) -> object: ...


frontmatter = cast(
    FrontmatterModule,
    cast(object, importlib.import_module("frontmatter")),
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = {"ko", "en"}

FENCE_OPEN_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

# Ko boilerplate patterns (from meta #1016)
KO_BOILERPLATE_PATTERNS = [
    re.compile(r"운영 흐름 안에서 어디에 배치해야 하는지"),
    re.compile(r"핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호"),
    re.compile(r"의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고"),
]

# En boilerplate pattern (from meta #1110)
EN_BOILERPLATE_PATTERNS = [
    re.compile(
        r"The core of .+ is not the feature name;?\s*it is deciding what to verify"
    ),
]

# AI slop words for English (from meta #1110)
AI_SLOP_PATTERNS = [
    (re.compile(r"\bleverag(?:e[ds]?|ing)\b", re.IGNORECASE), "leverage"),
    (re.compile(r"\brobust\b", re.IGNORECASE), "robust"),
    (re.compile(r"\bseamlessly\b", re.IGNORECASE), "seamlessly"),
    (re.compile(r"\bIn summary\b"), "In summary"),
]

# Ko josa: English word ending with consonant-like letter + 를 (should be 을)
# or ending with vowel-like letter + 을 (should be 를)
# Simplified heuristic: detect common patterns from the issue
JOSA_BATCHIM_RE = re.compile(
    r"([A-Za-z][a-z]*(?:er|on|or|es|al|le|ng|nt|ct|st|pt|rd|nd|rn|rm|rt|ck|lk|nk|mp|ft|lt))\s*를"
)
JOSA_NO_BATCHIM_RE = re.compile(r"([A-Za-z][a-z]*(?:a|e|i|o|u|y|ee|oo|ay|ey|ow))\s*을")

# Length thresholds
KO_LENGTH_ERROR = 5000  # chars (body, excluding code blocks and front matter)
KO_LENGTH_WARN = 7000
EN_WORD_WARN = 800  # words

# ---------------------------------------------------------------------------
# Utility functions (fence handling)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

Diagnostic = tuple[str, str]  # (level, message) where level is "error" or "warning"


def check_boilerplate(lines: list[str], lang: str) -> list[Diagnostic]:
    results: list[Diagnostic] = []
    patterns = KO_BOILERPLATE_PATTERNS if lang == "ko" else EN_BOILERPLATE_PATTERNS
    for line_no, line in enumerate(lines, start=1):
        for pat in patterns:
            if pat.search(line):
                snippet = line.strip()[:60]
                results.append(
                    ("error", f'boilerplate: "{snippet}..." (line {line_no})')
                )
    return results


def check_ai_slop(lines: list[str]) -> list[Diagnostic]:
    """Check English files for AI slop words."""
    results: list[Diagnostic] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line_no, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if not in_fence:
            m = FENCE_OPEN_RE.match(stripped)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
        else:
            if is_fence_close(stripped, fence_char, fence_len):
                in_fence = False
                fence_char = ""
                fence_len = 0
            continue

        for pat, name in AI_SLOP_PATTERNS:
            if pat.search(line):
                results.append(("warning", f'ai-slop: "{name}" (line {line_no})'))
    return results


def body_text_no_code(lines: list[str]) -> str:
    """Extract body text excluding code blocks."""
    parts: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in lines:
        stripped = line.lstrip()
        if not in_fence:
            m = FENCE_OPEN_RE.match(stripped)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
            parts.append(line)
        else:
            if is_fence_close(stripped, fence_char, fence_len):
                in_fence = False
                fence_char = ""
                fence_len = 0
    return "\n".join(parts)


def check_length(lines: list[str], lang: str) -> list[Diagnostic]:
    results: list[Diagnostic] = []
    body = body_text_no_code(lines)
    if lang == "ko":
        char_count = len(body.replace(" ", "").replace("\n", ""))
        if char_count < KO_LENGTH_ERROR:
            results.append(
                (
                    "warning",
                    f"length: {char_count} chars (< {KO_LENGTH_ERROR} error threshold)",
                )
            )
        elif char_count < KO_LENGTH_WARN:
            results.append(
                (
                    "warning",
                    f"length: {char_count} chars (< {KO_LENGTH_WARN} warn threshold)",
                )
            )
    else:
        word_count = len(body.split())
        if word_count < EN_WORD_WARN:
            results.append(
                ("warning", f"length: {word_count} words (< {EN_WORD_WARN})")
            )
    return results


def check_empty_h2(lines: list[str]) -> list[Diagnostic]:
    """Detect ## headings followed immediately by another ## (no body between)."""
    results: list[Diagnostic] = []
    h2_re = re.compile(r"^##\s+(.+)")
    prev_h2_line: int | None = None
    prev_h2_title: str = ""

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if h2_re.match(stripped):
            if prev_h2_line is not None:
                # Check if there's non-empty content between prev_h2 and this line
                between = lines[prev_h2_line : line_no - 1]  # 0-indexed slice
                has_content = any(l.strip() for l in between)
                if not has_content:
                    results.append(
                        (
                            "error",
                            f'empty H2: "## {prev_h2_title}" (line {prev_h2_line})',
                        )
                    )
            m = h2_re.match(stripped)
            prev_h2_line = line_no
            prev_h2_title = m.group(1) if m else ""
        elif stripped and not stripped.startswith("#"):
            # Non-empty non-heading line resets the "empty" check
            prev_h2_line = None
            prev_h2_title = ""

    return results


def check_josa(lines: list[str]) -> list[Diagnostic]:
    """Check Korean josa errors on English words."""
    results: list[Diagnostic] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line_no, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if not in_fence:
            m = FENCE_OPEN_RE.match(stripped)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
        else:
            if is_fence_close(stripped, fence_char, fence_len):
                in_fence = False
                fence_char = ""
                fence_len = 0
            continue

        for pat_match in JOSA_BATCHIM_RE.finditer(line):
            word = pat_match.group(1)
            results.append(
                ("warning", f'josa: "{word}를" → "{word}을" (line {line_no})')
            )
        for pat_match in JOSA_NO_BATCHIM_RE.finditer(line):
            word = pat_match.group(1)
            results.append(
                ("warning", f'josa: "{word}을" → "{word}를" (line {line_no})')
            )
    return results


def inspect_fences(lines: list[str]) -> list[Diagnostic]:
    results: list[Diagnostic] = []
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
                results.append(
                    ("warning", f"Code block at line {line_no} missing language tag")
                )
            in_fence = True
            fence_char = fence[0]
            fence_len = len(fence)
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0

    return results


def find_missing_image_alt(lines: list[str]) -> list[Diagnostic]:
    results: list[Diagnostic] = []
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
                    results.append(
                        ("warning", f"Image at line {line_no} missing alt text")
                    )
            continue

        if is_fence_close(stripped_left, fence_char, fence_len):
            in_fence = False
            fence_char = ""
            fence_len = 0

    return results


# ---------------------------------------------------------------------------
# Main check orchestrator
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check content quality (boilerplate, length, josa, AI slop)."
    )
    _ = parser.add_argument(
        "--series", help="check only one series id (content/<series>/)"
    )
    _ = parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any errors found (not just warnings)",
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


def check_article(path: Path) -> list[Diagnostic]:
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as exc:
        return [("error", f"Unable to parse front matter: {exc}")]

    content = cast(str, getattr(post, "content"))
    lines = content.splitlines()

    lang = path.parent.name  # "ko" or "en"

    diagnostics: list[Diagnostic] = []

    # Boilerplate
    diagnostics.extend(check_boilerplate(lines, lang))

    # Length
    diagnostics.extend(check_length(lines, lang))

    # Empty H2
    diagnostics.extend(check_empty_h2(lines))

    # Language-specific checks
    if lang == "ko":
        diagnostics.extend(check_josa(lines))
    elif lang == "en":
        diagnostics.extend(check_ai_slop(lines))

    # Generic checks
    diagnostics.extend(inspect_fences(lines))
    diagnostics.extend(find_missing_image_alt(lines))

    return diagnostics


def main() -> int:
    args = parse_args()
    series = cast(str | None, args.series)
    strict: bool = args.strict

    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1

    articles = iter_articles(series)
    if series and not articles:
        print(f"No articles found for series: {series}", file=sys.stderr)
        return 1

    print("Checking content quality...")
    checked = 0
    error_count = 0
    warning_count = 0

    for md in articles:
        if md.parent.name not in LANG_DIRS:
            continue

        checked += 1
        diagnostics = check_article(md)
        if not diagnostics:
            continue

        rel = md.relative_to(REPO_ROOT)
        print(f"== {rel}")
        for level, msg in diagnostics:
            if level == "error":
                error_count += 1
                print(f"  ❌ {msg}")
            else:
                warning_count += 1
                print(f"  ⚠️  {msg}")

    print(
        f"\nSummary: {checked} articles checked, {error_count} errors, {warning_count} warnings"
    )

    if strict and error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
