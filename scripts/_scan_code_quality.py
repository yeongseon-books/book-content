"""Scan all Python code blocks in canonical content for issues.

Reports:
- syntax errors (with subtype classification)
- placeholder-only blocks
- deprecated typing imports

Usage:
    python3 scripts/_scan_code_quality.py [--series SERIES] [--detail]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
LANGS = {"ko", "en"}


def extract_python_blocks(text: str) -> list[tuple[int, str]]:
    """Extract ```python ... ``` blocks using line-based parsing.

    Returns list of (start_line_1based, body). Closing fence must be at
    line start (matching the opening indentation) - this avoids false
    truncation at inline backticks within string literals.
    """
    blocks: list[tuple[int, str]] = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        ln = lines[i]
        stripped = ln.lstrip()
        indent = len(ln) - len(stripped)
        if stripped.rstrip("\n").rstrip("\r") == "```python" or stripped.startswith(
            "```python"
        ):
            opener = stripped.rstrip("\n").rstrip("\r")
            if opener == "```python":
                start = i + 1
                body_lines: list[str] = []
                j = i + 1
                while j < len(lines):
                    candidate = lines[j]
                    cand_strip = candidate.lstrip()
                    cand_indent = len(candidate) - len(cand_strip)
                    if (
                        cand_strip.rstrip("\n").rstrip("\r") == "```"
                        and cand_indent == indent
                    ):
                        break
                    body_lines.append(candidate)
                    j += 1
                blocks.append((start + 1, "".join(body_lines)))
                i = j + 1
                continue
        i += 1
    return blocks


def classify_syntax(code: str, err: SyntaxError) -> str:
    """Best-effort classification of a SyntaxError."""
    msg = (err.msg or "").lower()
    if "unterminated" in msg or "eof in" in msg or "was never closed" in msg:
        return "unterminated_string"
    if (
        "indent" in msg
        or "unexpected indent" in msg
        or "expected an indented block" in msg
    ):
        return "indentation"
    # output mixed: lines that look like REPL/output rather than code
    head = code.lstrip().splitlines()[:8]
    for ln in head:
        s = ln.strip()
        if s.startswith(">>>") or s.startswith("...") or s.startswith("$ "):
            return "output_mixed"
    # presence of REPL anywhere
    if ">>>" in code or "\n... " in code:
        return "output_mixed"
    return "syntax"


def is_placeholder(code: str) -> bool:
    """Block has only `...` / `pass` / blank / comments."""
    lines = [ln.strip() for ln in code.strip().splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("#")]
    if not lines:
        return False  # empty - separate category
    return all(ln in ("...", "pass") for ln in lines)


def has_deprecated_callable(code: str) -> bool:
    return bool(
        re.search(r"^from\s+typing\s+import\s+[^\n]*\bCallable\b", code, re.MULTILINE)
    )


def scan_block(code: str) -> dict | None:
    s = code.strip()
    if not s:
        return None
    if s in ("...", "pass"):
        return {"kind": "placeholder"}
    if is_placeholder(code):
        return {"kind": "placeholder"}

    issues: list[str] = []
    if has_deprecated_callable(code):
        issues.append("deprecated_callable")

    try:
        ast.parse(code)
    except SyntaxError as e1:
        # try as function body (allow free-floating return etc.)
        wrapped = "def _():\n" + "".join("  " + ln + "\n" for ln in code.splitlines())
        try:
            ast.parse(wrapped)
        except SyntaxError as e2:
            kind = classify_syntax(code, e1)
            return {
                "kind": "syntax_error",
                "subtype": kind,
                "msg": e1.msg,
                "line": e1.lineno,
                "issues": issues,
            }
    if issues:
        return {"kind": "deprecated_only", "issues": issues}
    return None


def iter_articles(series_filter: str | None):
    for series_dir in sorted(CONTENT.iterdir()):
        if not series_dir.is_dir():
            continue
        if series_filter and series_dir.name != series_filter:
            continue
        for lang in LANGS:
            d = series_dir / lang
            if not d.is_dir():
                continue
            for md in sorted(d.glob("*.md")):
                yield series_dir.name, md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument(
        "--kind", choices=["syntax_error", "placeholder", "deprecated_only"]
    )
    ap.add_argument("--subtype")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    series_stats: dict[str, dict[str, int]] = {}
    subtype_stats: dict[str, int] = {}
    detail: list[dict] = []
    total_blocks = 0

    for series, md in iter_articles(args.series):
        text = md.read_text(encoding="utf-8", errors="replace")
        for line_no, code in extract_python_blocks(text):
            total_blocks += 1
            result = scan_block(code)
            if not result:
                continue
            if args.kind and result["kind"] != args.kind:
                continue
            if args.subtype and result.get("subtype") != args.subtype:
                continue
            stats = series_stats.setdefault(series, {})
            key = (
                result["kind"]
                if "subtype" not in result
                else f"{result['kind']}:{result['subtype']}"
            )
            stats[key] = stats.get(key, 0) + 1
            subtype_stats[key] = subtype_stats.get(key, 0) + 1
            if args.detail:
                detail.append(
                    {
                        "series": series,
                        "file": str(md.relative_to(REPO)),
                        "block_line": line_no,
                        **result,
                        "preview": code.strip().splitlines()[:3],
                    }
                )

    if args.json:
        json.dump(
            {
                "total_blocks": total_blocks,
                "series": series_stats,
                "subtype": subtype_stats,
                "detail": detail,
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        return 0

    print(f"Total python blocks scanned: {total_blocks}")
    print(f"\nBy kind/subtype:")
    for k, v in sorted(subtype_stats.items(), key=lambda x: -x[1]):
        print(f"  {k:40s} {v}")
    print(f"\nBy series:")
    for s in sorted(series_stats, key=lambda s: -sum(series_stats[s].values())):
        total = sum(series_stats[s].values())
        breakdown = ", ".join(f"{k}={v}" for k, v in series_stats[s].items())
        print(f"  {s:40s} {total:4d}  ({breakdown})")

    if args.detail:
        print(f"\nDetails: {len(detail)} entries")
        for d in detail[:50]:
            print(
                f"\n  {d['file']}:{d['block_line']}  [{d['kind']}{':' + d['subtype'] if 'subtype' in d else ''}]"
            )
            for ln in d["preview"]:
                print(f"    | {ln}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
