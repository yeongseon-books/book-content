#!/usr/bin/env python3
"""Guard: detect H2 sections with too-thin body content (issue #1237).

Background
==========

Golden reference (``azure-app-service-101``) keeps non-wrapper H2 sections
above ~800 characters of body. The audit found 5,980 short sections across
the repo, concentrated in ``capstone-project-101`` and ``kubernetes-101``.

Wrapper sections are intentionally short and excluded:

- ``먼저 던지는 질문`` / ``Questions to Keep in Mind`` (Question Loop opener)
- ``처음 질문으로 돌아가기`` / ``Answering the Opening Questions`` (closer)
- ``핵심 용어`` / ``Key Terms``
- ``체크리스트`` / ``Checklist``
- ``연습 문제`` / ``Exercises``
- ``정리와 다음 글`` / ``Wrap-Up``
- ``이 글에서 배우는 내용`` / ``What You'll Learn``
- ``참고 자료`` / ``References``

Heuristic
=========

For each non-wrapper H2 section in canonical posts, count the characters
of body text between the heading and the next ``## ``. Strip fenced code
blocks, raw HTML tags, and TOC markers before counting.

- WARN per file when at least one non-wrapper section has body < 200 chars.
- HARD FAIL never (this is a quality drift signal, not a correctness bug).

The script is diagnostic only. Remediation is per-file expansion of the
flagged sections, tracked against issue #1237.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

WRAPPER_HEADINGS = {
    "먼저 던지는 질문",
    "Questions to Keep in Mind",
    "처음 질문으로 돌아가기",
    "Answering the Opening Questions",
    "핵심 용어",
    "Key Terms",
    "체크리스트",
    "Checklist",
    "연습 문제",
    "Exercises",
    "정리와 다음 글",
    "Wrap-Up",
    "이 글에서 배우는 내용",
    "What You'll Learn",
    "참고 자료",
    "References",
    "이 시리즈에서 다루는 글",
    "Series Index",
}

MIN_BODY_CHARS = 200
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
HTML_RE = re.compile(r"<[^>]+>")
TOC_RE = re.compile(r"<!--\s*toc:(begin|end)\s*-->")
H2_SPLIT_RE = re.compile(r"^## (?!#)", re.MULTILINE)


def section_body_chars(body: str) -> int:
    cleaned = FENCE_RE.sub("", body)
    cleaned = TOC_RE.sub("", cleaned)
    cleaned = HTML_RE.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return len(cleaned)


def scan_file(path: str) -> list[tuple[str, int]]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    parts = H2_SPLIT_RE.split(text)
    if len(parts) < 2:
        return []
    findings: list[tuple[str, int]] = []
    for chunk in parts[1:]:
        head, _, rest = chunk.partition("\n")
        heading = head.strip()
        if heading in WRAPPER_HEADINGS:
            continue
        chars = section_body_chars(rest)
        if chars < MIN_BODY_CHARS:
            findings.append((heading, chars))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="content")
    parser.add_argument("--show-headings", action="store_true")
    args = parser.parse_args(argv)

    pattern = os.path.join(args.root, "*", "?[koen][on]?", "*.md")
    files = sorted(
        p for p in glob.glob(os.path.join(args.root, "*", "ko", "*.md"))
    ) + sorted(
        p for p in glob.glob(os.path.join(args.root, "*", "en", "*.md"))
    )

    flagged_files = 0
    total_sections = 0
    per_series: dict[str, int] = {}
    for path in files:
        findings = scan_file(path)
        if not findings:
            continue
        flagged_files += 1
        total_sections += len(findings)
        series = path.split(os.sep)[1]
        per_series[series] = per_series.get(series, 0) + len(findings)
        if args.show_headings:
            for heading, chars in findings:
                print(f"  {chars:4d}  {path}  ## {heading}")

    if not flagged_files:
        print(f"PASS: no non-wrapper H2 sections below {MIN_BODY_CHARS} chars.")
        return 0

    print(
        f"WARN: {total_sections} short H2 sections across {flagged_files} files "
        f"(threshold < {MIN_BODY_CHARS} chars)."
    )
    print("Top series:")
    for series, count in sorted(per_series.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:4d}  {series}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
