#!/usr/bin/env python3
"""Guard: detect known generic boilerplate answer phrases in article bodies.

These three sentences were inserted by a flawed expand-template script into
~450 articles' `## 처음 질문으로 돌아가기` answer bullets. They are 100%
disconnected from each article's content (article topic merely substituted
into a fixed template) and violate AGENTS.md Prime Directive §7.

Detects across full article bodies (excluding front matter and code fences)
so regression of this specific AI-slop pattern is blocked at CI time.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

BANNED = (
    # #1260: generic answer bullets
    "한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호",
    "예제와 그림에서는 어떤 값이 들어오고",
    "운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨",
    # #1261: generic opening questions (paired with #1260 answers)
    "운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요",
    "예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요",
    "실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요",
)


def body_without_fences(text: str) -> str:
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    errors: list[str] = []
    for md in sorted(CONTENT.glob("*/ko/*.md")) + sorted(CONTENT.glob("*/en/*.md")):
        body = body_without_fences(md.read_text(encoding="utf-8"))
        for phrase in BANNED:
            if phrase in body:
                errors.append(f"{md}: banned boilerplate phrase: {phrase!r}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} boilerplate residues found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
