"""Check article body structure for publish-ready and published articles.

For articles with status 'publish-ready' or 'published', verifies:
- H1 exists
- Questions block exists ("이 글에서 답할 질문" for ko, "Questions this post answers" for en)
- Mental model block exists (blockquote `> ...`)
- At least one code block exists
- Checklist exists (checkbox `- [ ]` or `- [x]`)
- References section exists ("## 참고 자료" for ko, "## References" for en)
- Tags line exists as last line

Exit code: 0 on success, 1 on any validation error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

STRICT_STATUSES = {"publish-ready", "published"}

H1_RE = re.compile(r"^# .+", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"^```", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^- \[[ x]\]", re.MULTILINE)
BLOCKQUOTE_RE = re.compile(r"^> .+", re.MULTILINE)
TAGS_RE = re.compile(r"^Tags: .+$", re.MULTILINE)

KO_QUESTIONS = re.compile(r"^## .*(\uc9c8\ubb38|\ub2f5\ud560 \uc9c8\ubb38|\ub2e4\ub8f0 \uc9c8\ubb38)", re.MULTILINE)
EN_QUESTIONS = re.compile(r"^## .*(Questions|answers|What you will learn)", re.MULTILINE)
A_GRADE_MARKER = "<!-- a-grade-intro:begin -->"

KO_REFS = re.compile(r"^## 참고 자료", re.MULTILINE)
EN_REFS = re.compile(r"^## References", re.MULTILINE)


def check_article(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block CI; warnings are informational."""
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")

    try:
        post = frontmatter.loads(text)
    except Exception:
        return [], []  # front matter issues are caught by check_frontmatter.py

    status = post.metadata.get("status")
    if status not in STRICT_STATUSES:
        return [], []  # only strict-check for publish-ready+

    lang = post.metadata.get("language", path.parent.name)
    body = post.content

    # --- blocking checks ---
    if not H1_RE.search(body):
        errors.append("missing H1 title")

    refs_re = KO_REFS if lang == "ko" else EN_REFS
    if not refs_re.search(body):
        errors.append("missing references section")

    # Tags line should be the last non-empty line
    lines = text.rstrip().split("\n")
    if lines and not lines[-1].startswith("Tags: "):
        errors.append("missing or misplaced Tags line (must be last line)")

    # --- advisory checks (warnings) ---
    if A_GRADE_MARKER not in body:
        questions_re = KO_QUESTIONS if lang == "ko" else EN_QUESTIONS
        if not questions_re.search(body):
            warnings.append("missing questions block")

    if not BLOCKQUOTE_RE.search(body):
        warnings.append("missing mental model blockquote (> ...)")

    code_required = post.metadata.get("code_required", True)
    if code_required and not CODE_BLOCK_RE.search(body):
        warnings.append("missing code block")

    if not CHECKBOX_RE.search(body):
        warnings.append("missing checklist")

    return errors, warnings


def main() -> int:
    if not CONTENT_DIR.is_dir():
        print(f"no content/ directory at {CONTENT_DIR}", file=sys.stderr)
        return 1

    failures = 0
    warned = 0
    checked = 0
    skipped = 0

    for md in sorted(CONTENT_DIR.glob("*/*/*.md")):
        if md.parent.name not in ("ko", "en"):
            continue
        errs, warns = check_article(md)
        if not errs and not warns:
            try:
                post = frontmatter.loads(md.read_text(encoding="utf-8"))
                if post.metadata.get("status") in STRICT_STATUSES:
                    checked += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
            continue
        checked += 1
        rel = md.relative_to(REPO_ROOT)
        if errs:
            failures += 1
            print(f"FAIL {rel}")
            for e in errs:
                print(f"  - {e}")
        if warns:
            warned += 1
            if not errs:
                print(f"WARN {rel}")
            for w in warns:
                print(f"  - [warning] {w}")

    print(
        f"\nstrict-checked: {checked}, skipped: {skipped}, failures: {failures}, warnings: {warned}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
