"""Check that no article uses '## 큰 그림' or '## Big Picture' as a section heading."""

import pathlib
import sys


def main() -> int:
    root = pathlib.Path("content")
    patterns = {"## 큰 그림", "## Big Picture"}
    failures: list[str] = []

    all_files = list(root.glob("*/ko/*.md")) + list(root.glob("*/en/*.md"))
    for md in sorted(all_files):
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.strip() in patterns:
                failures.append(str(md))
                break

    if failures:
        print(f"FAIL: {len(failures)} file(s) still use '## 큰 그림' / '## Big Picture':")
        for f in failures[:20]:
            print(f"  {f}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        return 1

    print("OK: no '## 큰 그림' / '## Big Picture' sections found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
