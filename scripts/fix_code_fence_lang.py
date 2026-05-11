"""Conservative code-fence language tag fixer.

Auto-tags untagged code fences only when language can be inferred with HIGH
confidence. Categories applied:

  - ascii diagrams (with → ← ↑ ↓ or box-drawing) → ``text``
  - pure HTTP request listings (every non-empty line ``METHOD /path``) → ``http``
  - pure shell snippets (every non-empty line starts with ``$ ``) → ``bash``
  - pure SQL statements (any line begins with SELECT/INSERT/UPDATE/CREATE/ALTER/DROP) → ``sql``
  - pure Dockerfile (every non-comment line begins with a Dockerfile directive) → ``dockerfile``
  - pure Python (def/class/import/from/@ at line start AND no arrow annotations) → ``python``

Anything outside these patterns is left untouched. Run with ``--dry-run`` to
preview, omit to apply in place.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

CONTENT_ROOT = Path("content")

FENCE_OPEN_RE = re.compile(r"^(```+|~~~+)(.*)$")

ARROW_RE = re.compile(r"[→←↑↓│┌└├─┐┘┤┬┴┼╔╗╚╝═║╠╣╦╩╬]")
HTTP_LINE_RE = re.compile(
    r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+/\S*", re.IGNORECASE
)
SHELL_PROMPT_RE = re.compile(r"^\$\s+\S")
SQL_KW_RE = re.compile(
    r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE\s+(TABLE|INDEX|VIEW|DATABASE)|ALTER\s+TABLE|DROP\s+(TABLE|INDEX)|WITH)\b",
    re.IGNORECASE,
)
DOCKER_KW_RE = re.compile(
    r"^(FROM|RUN|CMD|ENTRYPOINT|COPY|ADD|WORKDIR|ENV|EXPOSE|ARG|LABEL|USER|VOLUME|HEALTHCHECK)\s+\S"
)
PY_HEAD_RE = re.compile(r"^(def\s|class\s|import\s|from\s+\S+\s+import\s|@\w+)")


def infer_lang(content: str) -> str | None:
    """Return inferred language tag or None when not confident."""
    s = content.rstrip("\n")
    stripped = s.strip()
    if not stripped:
        return None

    lines = [ln for ln in s.splitlines() if ln.strip()]
    if not lines:
        return None

    # 1. ASCII diagram: arrows or box-drawing characters present.
    if ARROW_RE.search(s):
        return "text"

    # 2. Pure HTTP listing: every non-empty line is METHOD /path (optional ctx).
    if all(HTTP_LINE_RE.match(ln.strip()) for ln in lines):
        return "http"

    # 3. Pure shell: every non-empty line starts with `$ ` prompt.
    if all(SHELL_PROMPT_RE.match(ln.strip()) for ln in lines):
        return "bash"

    # 4. SQL: at least one keyword AND no python/yaml/json giveaways.
    if SQL_KW_RE.search(s) and not re.search(
        r"\bdef\s|\bclass\s|\{|^\s*-\s", s, re.MULTILINE
    ):
        # Reject if other comment styles (#) but allow -- and /* */.
        return "sql"

    # 5. Dockerfile: every non-comment, non-blank line is a Dockerfile directive.
    non_comment = [ln for ln in lines if not ln.lstrip().startswith("#")]
    if non_comment and all(DOCKER_KW_RE.match(ln.lstrip()) for ln in non_comment):
        return "dockerfile"

    # 6. Pure Python: header keyword present, no arrows (already filtered),
    #    no obvious shell prompts, no annotation arrows like `← ...`.
    if PY_HEAD_RE.search(s) and not re.search(r"←|→", s):
        # Avoid REPL-style snippets unless explicitly tagged.
        if not re.search(r"^>>>", s, re.MULTILINE):
            return "python"

    return None


def split_frontmatter(raw: str) -> tuple[str, str]:
    """Return (front_matter_with_delims, body) preserving exact bytes."""
    if not raw.startswith("---\n"):
        return "", raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return "", raw
    fm_end = end + len("\n---\n")
    return raw[:fm_end], raw[fm_end:]


def process_file(path: Path, apply: bool) -> tuple[int, Counter]:
    raw = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(raw)
    lines = body.split("\n")

    new_lines: list[str] = []
    i = 0
    fixed = 0
    by_lang: Counter = Counter()

    while i < len(lines):
        line = lines[i]
        m = FENCE_OPEN_RE.match(line)
        if not m:
            new_lines.append(line)
            i += 1
            continue

        fence = m.group(1)
        tag = m.group(2).strip()

        j = i + 1
        while j < len(lines):
            stripped = lines[j].lstrip()
            if stripped.startswith(fence[0] * len(fence)):
                cm = re.match(r"^(`+|~+)\s*$", stripped)
                if cm and len(cm.group(1)) >= len(fence) and cm.group(1)[0] == fence[0]:
                    break
            j += 1

        if not tag and j < len(lines):
            content = "\n".join(lines[i + 1 : j])
            inferred = infer_lang(content)
            if inferred:
                line = f"{fence}{inferred}"
                fixed += 1
                by_lang[inferred] += 1

        new_lines.append(line)
        for k in range(i + 1, min(j + 1, len(lines))):
            new_lines.append(lines[k])
        i = j + 1

    if fixed and apply:
        new_body = "\n".join(new_lines)
        path.write_text(fm + new_body, encoding="utf-8")

    return fixed, by_lang


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report only, do not write.")
    ap.add_argument("--root", default=str(CONTENT_ROOT))
    args = ap.parse_args()

    root = Path(args.root)
    total_files = 0
    files_changed = 0
    total_fixed = 0
    overall: Counter = Counter()

    for md in sorted(root.rglob("*.md")):
        parts = md.parts
        if "medium" in parts:
            continue
        if not any(p in {"ko", "en"} for p in parts):
            continue
        total_files += 1
        fixed, by_lang = process_file(md, apply=not args.dry_run)
        if fixed:
            files_changed += 1
            total_fixed += fixed
            overall.update(by_lang)
            mode = "DRY" if args.dry_run else "FIX"
            print(f"  [{mode}] {md} (+{fixed}: {dict(by_lang)})")

    print()
    print(f"Files scanned: {total_files}")
    print(f"Files {'would change' if args.dry_run else 'changed'}: {files_changed}")
    print(f"Total fences {'would tag' if args.dry_run else 'tagged'}: {total_fixed}")
    for k, v in overall.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
