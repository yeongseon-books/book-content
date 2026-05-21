#!/usr/bin/env python3
"""Guard: ko posts must not have English-only H2/H3 headings.

Whitelist exceptions:
- Technical comparisons (vs/versus patterns): SRE vs DevOps, MTTR vs MTBF, etc.
- RFC/standard references: RFC 7807, ISO 8601
- Brand/product names used as headings
- Single-word headings (likely technical terms)
"""
import re
import glob
import sys

HAN = re.compile(r"[\uac00-\ud7a3]")
# Whitelist patterns (English headings that are acceptable in ko posts)
WHITELIST_RE = re.compile(
    r"^("
    r"[A-Z0-9\-]+ vs\.? [A-Z0-9\-]+"  # X vs Y comparisons
    r"|.*\bvs\b.*"  # anything with "vs"
    r"|RFC \d+"  # RFC references
    r"|ISO \d+"  # ISO references
    r"|[A-Z][a-z]+ [A-Z][a-z]+"  # Proper nouns (e.g. "Monte Carlo")
    r")$",
    re.I,
)

def check():
    errors = []
    for f in sorted(glob.glob("content/*/ko/*.md")):
        if "azure-app-service-101" in f:
            continue
        body = re.sub(r"^---\n.*?\n---\n", "", open(f).read(), count=1, flags=re.S)
        for m in re.finditer(r"^(#{2,3}) (.+)$", body, re.M):
            level, heading = m.group(1), m.group(2).strip()
            # Skip if contains Korean
            if HAN.search(heading):
                continue
            # Skip single-word headings
            if len(heading.split()) < 2:
                continue
            # Skip whitelisted patterns
            if WHITELIST_RE.match(heading):
                continue
            # Skip TOC markers
            if "toc:" in heading.lower():
                continue
            # Check for English function words (strong signal of untranslated heading)
            if re.search(
                r"\b(the|a|an|is|are|do|does|how|what|why|when|with|to|of|for|and|or)\b",
                heading,
                re.I,
            ):
                errors.append(f"  {f}: {level} {heading}")

    if errors:
        print(f"FAIL: {len(errors)} English-only H2/H3 headings in ko posts:")
        for e in errors:
            print(e)
        return 1
    print("PASS: No English-only H2/H3 headings in ko posts.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
