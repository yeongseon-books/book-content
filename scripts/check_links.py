"""Validate every relative link/image target in content/<series>/{ko,en}/*.md.

Scope:
- Local markdown link: `[text](./foo.md)` and `[text](../bar/baz.md)`
- Image: `![alt](../../../assets/...)`
- Anchors and query strings are stripped before resolution
- External links (http://, https://, mailto:, #fragment-only) are skipped
- Code fences are skipped to avoid false positives in command examples

Policy:
- Unresolved links in series with status `draft` emit warnings only (exit 0).
- Unresolved links in non-draft series are hard failures (exit 1).

Note: medium/ files use absolute raw URLs (commit-pinned) and are not
checked here. to-medium.py owns medium URL generation; treat its output
as opaque.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
SERIES_YAML = REPO_ROOT / "series.yaml"

LINK_RE = re.compile(r"(!?)\[([^\]]+)\]\(([^)]+)\)")


def load_draft_series() -> set[str]:
    raw = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    return {s["id"] for s in raw.get("series", []) if s.get("status") == "draft"}


def strip_code_fences(text: str) -> str:
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#", "/"))


def resolve(src_md: Path, target: str) -> Path | None:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    return (src_md.parent / clean).resolve()


def check_file(md: Path) -> list[str]:
    errors: list[str] = []
    text = strip_code_fences(md.read_text(encoding="utf-8"))
    for m in LINK_RE.finditer(text):
        target = m.group(3).strip()
        if is_external(target):
            continue
        resolved = resolve(md, target)
        if resolved is None:
            continue
        if not resolved.exists():
            try:
                rel = resolved.relative_to(REPO_ROOT)
            except ValueError:
                rel = resolved
            errors.append(f"unresolved: [{m.group(2)}]({target}) -> {rel}")
    return errors


def main() -> int:
    if not CONTENT_DIR.is_dir():
        print(f"missing {CONTENT_DIR}", file=sys.stderr)
        return 1
    draft_series = load_draft_series()
    hard_failures = 0
    warn_failures = 0
    checked = 0
    for md in sorted(CONTENT_DIR.glob("*/*/*.md")):
        if md.parent.name not in {"ko", "en"}:
            continue
        checked += 1
        errs = check_file(md)
        if not errs:
            continue
        # series id is the content/<series-id>/ directory name
        series_id = md.parts[md.parts.index("content") + 1]
        is_draft = series_id in draft_series
        label = "WARN" if is_draft else "FAIL"
        print(f"{label} {md.relative_to(REPO_ROOT)}")
        for e in errs:
            print(f"  - {e}")
        if is_draft:
            warn_failures += 1
        else:
            hard_failures += 1
    print(f"\nchecked: {checked}, hard failures: {hard_failures}, warnings: {warn_failures}")
    return 1 if hard_failures else 0


if __name__ == "__main__":
    sys.exit(main())
