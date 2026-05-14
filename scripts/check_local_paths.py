"""Lint local filesystem path leaks in article bodies.

Rule (FAIL): article body must not contain author-machine paths like
`/root/`, `/home/<user>/`, `/Users/<user>/`, or `C:\\Users\\<user>\\`.

Allowed placeholders (whitelisted, not flagged):
- `/Users/username/`, `/Users/<user>/`, `/Users/your-name/`
- `/home/username/`, `/home/user/`, `/home/<user>/`
- `/root` exactly (a literal path reference, not nested)

Detection: matches occur anywhere in the body (including code fences) since
local paths are leaks even in code samples.

Exit code: 0 if no failures, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = {"ko", "en"}

PLATFORM_HOME = {"site", "LogFiles", "runner", "app", "vsts", "vsts-agent"}
PLATFORM_ROOT = {
    ".cache",
    ".config",
    ".local",
    ".npm",
    ".docker",
    ".ssh",
    ".aws",
    ".azure",
}
PLACEHOLDERS = {"username", "user", "<user>", "your-name", "name", "you"}

PATH_PATTERNS = [
    (re.compile(r"/root/([A-Za-z0-9_.\-]+)"), "root", PLATFORM_ROOT | PLACEHOLDERS),
    (re.compile(r"/home/([A-Za-z0-9_.\-]+)/"), "home", PLATFORM_HOME | PLACEHOLDERS),
    (re.compile(r"/Users/([A-Za-z0-9_.\-]+)/"), "users", PLACEHOLDERS),
    (
        re.compile(r"C:\\Users\\([A-Za-z0-9_.\-]+)\\", re.IGNORECASE),
        "win-users",
        PLACEHOLDERS,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint local path leaks in articles")
    _ = parser.add_argument("--series", help="check only one series id")
    return parser.parse_args()


def iter_articles(series: str | None) -> list[Path]:
    if series:
        roots = [CONTENT_DIR / series]
    else:
        roots = [p for p in sorted(CONTENT_DIR.iterdir()) if p.is_dir()]
    items: list[Path] = []
    for root in roots:
        for lang in LANG_DIRS:
            d = root / lang
            if d.is_dir():
                items.extend(sorted(d.glob("*.md")))
    return items


def check_article(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as e:
        return [f"front matter parse error: {e}"]

    for line_no, line in enumerate(post.content.splitlines(), start=1):
        for pat, _kind, allowed in PATH_PATTERNS:
            for m in pat.finditer(line):
                segment = m.group(1)
                if segment in allowed:
                    continue
                errors.append(f"line {line_no}: local path leak '{m.group(0)}'")
    return errors


def main() -> int:
    args = parse_args()
    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1
    articles = iter_articles(args.series)
    failures = 0
    checked = 0
    for md in articles:
        if md.parent.name not in LANG_DIRS:
            continue
        checked += 1
        errs = check_article(md)
        if errs:
            failures += 1
            rel = md.relative_to(REPO_ROOT)
            print(f"FAIL {rel}")
            for e in errs:
                print(f"  - {e}")
    print(f"\nchecked: {checked}, failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
