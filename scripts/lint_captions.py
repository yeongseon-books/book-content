#!/usr/bin/env python3
"""Lint image alt-text (captions) against the AGENTS.md image caption policy.

Scans every Markdown file under content/<series>/{ko,en}/ and content/ai-web-dev-101/*.md
for `![alt](src)` patterns. Reports violations of the caption policy.

Exits 1 on any violation. Intended for pre-commit / CI.

Policy summary (see AGENTS.md "Image caption (alt text) policy"):
- ko: noun-phrase fragment, no `~입니다`/`~습니다` endings, no question form
- en: sentence-case descriptive fragment, no Title Case, no question form
- universal: no leading section number, no backticks, no trailing .?!,
  no em-dash decoration, no vague headline-clone captions
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

IMG_RE = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")

# Vague / heading-clone captions that should be replaced with a descriptive fragment
VAGUE_LABELS = {
    "ko": {
        "큰 그림", "한 화면으로", "한 그림으로", "전체 흐름", "전체 구조",
        "오늘 할 일", "오늘 할 일의 순서", "배포",
    },
    "en": {
        "big picture", "one diagram first", "all on one screen",
        "decision tree", "today's flow", "request path", "execution path",
    },
}

# Editorial / slogan phrases
SLOGAN_PATTERNS = [
    re.compile(r"\bNo Peeking at the Future\b", re.I),
    re.compile(r"\b3 ?am\b", re.I),
]

# Korean sentence endings forbidden in captions
KO_SENTENCE_ENDINGS = re.compile(r"(입니다|습니다|합니다|됩니다|있습니다)")

# Korean / English question markers
QUESTION_RE = re.compile(r"[?？]$|는가$|은가$|할까$|인가$|왜\s|어떻게\s|어디\s")

# Leading section/list number ("4. ", "5)", "1) ")
LEADING_NUM_RE = re.compile(r"^\s*\d+[\.)]\s+")

# Trailing terminal punctuation
TRAILING_PUNCT_RE = re.compile(r"[\.!?。！？]$")

# Backticks
BACKTICK_RE = re.compile(r"`")

# Em dash anywhere (caution-only; we still allow one if it's a label split, but flag for review)
EM_DASH_RE = re.compile(r"\s—\s")

# English Title Case heuristic: 3+ capitalized non-stop words in a row
TITLE_CASE_WORD_RE = re.compile(r"\b[A-Z][a-z]+\b")
TITLE_CASE_STOPWORDS = {
    "A", "An", "The", "And", "Or", "But", "Of", "In", "On", "At", "To",
    "For", "With", "By", "Vs", "Vs.", "From", "Per", "Into", "As",
}


def is_korean(text: str) -> bool:
    return any("\uac00" <= ch <= "\ud7a3" for ch in text)


def looks_title_case(text: str) -> bool:
    """Heuristic: en caption with 3+ Title-Cased non-stopword tokens in a row."""
    if is_korean(text):
        return False
    tokens = text.split()
    streak = 0
    for tok in tokens:
        clean = tok.strip(",.:;-—()[]\"'")
        if not clean:
            continue
        if clean in TITLE_CASE_STOPWORDS:
            streak = max(streak, 0)
            continue
        if clean[0].isupper() and any(c.islower() for c in clean[1:]):
            streak += 1
            if streak >= 3:
                return True
        else:
            streak = 0
    return False


def lint_caption(alt: str) -> list[str]:
    issues: list[str] = []
    ko = is_korean(alt)
    text = alt.strip()

    if LEADING_NUM_RE.match(text):
        issues.append("leading-section-number")
    if BACKTICK_RE.search(text):
        issues.append("backticks-in-alt")
    if TRAILING_PUNCT_RE.search(text):
        issues.append("trailing-punct")
    for slogan in SLOGAN_PATTERNS:
        if slogan.search(text):
            issues.append(f"slogan:{slogan.pattern}")
    if EM_DASH_RE.search(text):
        issues.append("em-dash")
    if QUESTION_RE.search(text):
        issues.append("question-form")

    lower = text.lower()
    if ko:
        if KO_SENTENCE_ENDINGS.search(text):
            issues.append("ko-sentence-ending")
        if text in VAGUE_LABELS["ko"]:
            issues.append("vague-label")
    else:
        if lower in VAGUE_LABELS["en"]:
            issues.append("vague-label")
        if looks_title_case(text):
            issues.append("title-case")

    return issues


def iter_markdown_files() -> list[Path]:
    series_yaml = yaml.safe_load((ROOT / "series.yaml").read_text())
    files: list[Path] = []
    for s in series_yaml["series"]:
        spath = ROOT / s["path"]
        if not spath.exists():
            continue
        for sub in ("ko", "en"):
            d = spath / sub
            if d.is_dir():
                files.extend(sorted(d.glob("*.md")))
        # flat layout (ai-web-dev-101)
        flat = sorted(spath.glob("[0-9][0-9]-*.md"))
        files.extend(flat)
    return files


def main() -> int:
    violations: list[tuple[Path, int, str, list[str]]] = []
    files = iter_markdown_files()

    for f in files:
        text = f.read_text()
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in IMG_RE.finditer(line):
                alt = m.group(1)
                issues = lint_caption(alt)
                if issues:
                    violations.append((f.relative_to(ROOT), line_no, alt, issues))

    if not violations:
        print(f"OK: 0 caption violations across {len(files)} files")
        return 0

    by_issue: dict[str, int] = {}
    for _, _, _, issues in violations:
        for i in issues:
            by_issue[i] = by_issue.get(i, 0) + 1

    print(f"FAIL: {len(violations)} caption violations across {len(files)} files\n")
    print("By rule:")
    for rule, count in sorted(by_issue.items(), key=lambda x: -x[1]):
        print(f"  {count:4d}  {rule}")
    print()
    print("Details:")
    for path, ln, alt, issues in violations:
        tags = ",".join(issues)
        print(f"  {path}:{ln}  [{tags}]  {alt!r}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
