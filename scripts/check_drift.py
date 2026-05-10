#!/usr/bin/env python3
"""Check for uncommitted generated outputs.

Generated outputs (docs/, exports/, content/*/medium/) should be committed
for publishing review. This script detects drift between working tree and
last commit. Also checks for untracked new files in generated directories.
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

    # Also check for untracked files in generated paths
    cmd_untracked = ["git", "ls-files", "--others", "--exclude-standard", "--"] + GENERATED_PATHS
    result_untracked = subprocess.run(cmd_untracked, capture_output=True, text=True)

    if result_untracked.returncode != 0:
        print(f"Error running git ls-files: {result_untracked.stderr}")
        return 1

    untracked = (
        result_untracked.stdout.strip().split("\n")
        if result_untracked.stdout.strip()
        else []
    )

    if changed or untracked:
        if changed:
            print("❌ Uncommitted generated outputs detected:")
            for path in changed:
                if path:
                    print(f"  - {path}")
        if untracked:
            print("❌ Untracked generated files detected:")
            for path in untracked:
                if path:
                    print(f"  - {path}")
        print()
        print("Generated outputs should be committed for publishing review.")
        print(
            "Run: git add docs/ exports/ content/*/medium/ && git commit -m 'update: generated outputs'"
        )
        return 1

    print("✅ All generated outputs are committed and no untracked files.")
    return 0
