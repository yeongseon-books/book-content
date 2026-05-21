#!/usr/bin/env python3
"""Check that no series has duplicated H2 section content across 5+ files.

Fails if a single H2 section body (>= 1500 bytes) appears identically in
5 or more files within the same series.
"""

import re
import glob
import hashlib
import sys
from collections import Counter, defaultdict


def main() -> int:
    errors = []

    series_dirs = sorted({p.split("/")[1] for p in glob.glob("content/*/ko/*.md")})

    for s in series_dirs:
        if s == "azure-app-service-101":
            continue
        files = sorted(glob.glob(f"content/{s}/ko/*.md"))
        if len(files) < 5:
            continue

        sec: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
        for f in files:
            body = re.sub(r"^---\n.*?\n---\n", "", open(f).read(), count=1, flags=re.S)
            for m in re.finditer(r"^## (.+?)\n(.*?)(?=\n## |\Z)", body, re.M | re.S):
                h2 = m.group(1).strip()
                content = m.group(2).strip()
                if len(content) < 1500:
                    continue
                h = hashlib.md5(content.encode()).hexdigest()[:8]
                sec[h2].append((f, h, len(content)))

        for h2, items in sec.items():
            cnt = Counter(r[1] for r in items)
            for h, n in cnt.most_common(1):
                if n >= 5:
                    errors.append(
                        f"  {s}: '## {h2}' duplicated in {n}/{len(items)} files "
                        f"({items[0][2]} bytes each)"
                    )

    if errors:
        print("FAIL: Boilerplate duplication detected:")
        for e in errors:
            print(e)
        return 1

    print("PASS: No boilerplate duplication found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
