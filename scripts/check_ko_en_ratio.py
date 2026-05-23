#!/usr/bin/env python3
"""Guard: detect ko/en byte-ratio asymmetry (issue #1226).

Background
==========

The golden reference ``content/azure-app-service-101`` keeps ko/en byte
ratio in the 2.1-2.5x range. Anything well above that signals that the ko
side was inflated past the en outline, typically because a previous expand
pass copied boilerplate to chase a byte target (Prime Directive §1/§7
violation). The mirror failure mode -- en much larger than ko -- is also
flagged because it means the en side was inflated independently.

Heuristic
=========

For each ko/en pair (skipping files smaller than 1 KB):

- WARN when ratio >= 3.0x (drift accumulating, request author attention).
- HARD FAIL when ratio >= 4.5x (clear boilerplate / outline mismatch).

The golden series is excluded from the audit (it defines the baseline).

The script never modifies files. It is purely diagnostic. The recommended
remediation for flagged files is to compress the larger side back to the
opposite-language outline, not to inflate the shorter side.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

GOLDEN_SERIES = "azure-app-service-101"
MIN_SIZE_BYTES = 1024  # ignore stubs
WARN_RATIO = 3.0
FAIL_RATIO = 4.5


def collect_pairs(root: str = "content") -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for ko in sorted(glob.glob(os.path.join(root, "*", "ko", "*.md"))):
        if f"/{GOLDEN_SERIES}/" in ko:
            continue
        en = ko.replace("/ko/", "/en/")
        if not os.path.exists(en):
            continue
        pairs.append((ko, en))
    return pairs


def analyze(pairs: list[tuple[str, str]]) -> tuple[list[tuple[float, int, int, str]], list[tuple[float, int, int, str]]]:
    warns: list[tuple[float, int, int, str]] = []
    fails: list[tuple[float, int, int, str]] = []
    for ko, en in pairs:
        ks = os.path.getsize(ko)
        es = os.path.getsize(en)
        if ks < MIN_SIZE_BYTES or es < MIN_SIZE_BYTES:
            continue
        ratio = max(ks, es) / min(ks, es)
        rec = (ratio, ks, es, ko)
        if ratio >= FAIL_RATIO:
            fails.append(rec)
        elif ratio >= WARN_RATIO:
            warns.append(rec)
    warns.sort(reverse=True)
    fails.sort(reverse=True)
    return warns, fails


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="content")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Never exit non-zero (report only).",
    )
    args = parser.parse_args(argv)

    pairs = collect_pairs(args.root)
    warns, fails = analyze(pairs)

    if not warns and not fails:
        print(f"PASS: {len(pairs)} ko/en pairs within ratio < {WARN_RATIO}.")
        return 0

    if warns:
        print(f"WARN: {len(warns)} pairs with ratio >= {WARN_RATIO} (drift).")
        for ratio, ks, es, ko in warns[:20]:
            print(f"  {ratio:.2f}x  ko={ks}  en={es}  {ko}")
        if len(warns) > 20:
            print(f"  ... and {len(warns) - 20} more")

    if fails:
        print(f"FAIL: {len(fails)} pairs with ratio >= {FAIL_RATIO} (boilerplate).")
        for ratio, ks, es, ko in fails:
            print(f"  {ratio:.2f}x  ko={ks}  en={es}  {ko}")

    # Audit #1226 baseline: 87 warn-bucket entries, 0 fail-bucket.
    # We hard-fail only on the strict bucket so the guard is actionable
    # without blocking publication on the long-tail compression work.
    if fails and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
