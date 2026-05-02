#!/usr/bin/env python3
"""Check for uncommitted generated outputs.

Generated outputs (docs/, exports/, content/*/medium/) should be committed
for publishing review. This script detects drift between working tree and
last commit.
"""

import subprocess
import sys

GENERATED_PATHS = [
    "docs/",
    "exports/",
    "content/*/medium/",
]


def main():
    # Check for uncommitted changes in generated paths
    cmd = ["git", "diff", "--name-only", "--"] + GENERATED_PATHS
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running git diff: {result.stderr}")
        return 1

    changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if changed:
        print("❌ Uncommitted generated outputs detected:")
        for path in changed:
            print(f"  - {path}")
        print("\nGenerated outputs should be committed for publishing review.")
        print(
            "Run: git add docs/ exports/ content/*/medium/ && git commit -m 'update: generated outputs'"
        )
        return 1

    print("✅ All generated outputs are committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
