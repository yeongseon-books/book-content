"""Validate every relative link/image target in content/<series>/{ko,en}/*.md.

Scope:
- Local markdown link: `[text](./foo.md)` and `[text](../bar/baz.md)`
- Image: `![alt](../../../assets/...)`
- Anchors and query strings are stripped before resolution
- External links (http://, https://, mailto:, #fragment-only) are skipped
- Code fences are skipped to avoid false positives in command examples

Returns nonzero exit if any unresolved relative target is found.

Note: medium/ files use absolute raw URLs (commit-pinned) and are not
checked here. to-medium.py owns medium URL generation; treat its output
as opaque.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

LINK_RE = re.compile(r"(!?)\[([^\]]+)\]\(([^)]+)\)")
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)


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
    failures = 0
    checked = 0
    for md in sorted(CONTENT_DIR.glob("*/*/*.md")):
        if md.parent.name not in {"ko", "en"}:
            continue
        checked += 1
        errs = check_file(md)
        if errs:
            failures += 1
            print(f"FAIL {md.relative_to(REPO_ROOT)}")
            for e in errs:
                print(f"  - {e}")
    print(f"\nchecked: {checked}, failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
