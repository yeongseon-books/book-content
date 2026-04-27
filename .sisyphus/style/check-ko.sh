#!/usr/bin/env bash
# Korean translation-smell checker.
# Usage: ./.sisyphus/style/check-ko.sh [path1 path2 ...]
#   No args -> scans azure-*/ko, ai-web-dev-101, README.md.
# Reads patterns from .sisyphus/style/translation-smells.txt (one ERE per line).
# Exit 0 = clean, 1 = smells found, 2 = config error.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SMELLS="$ROOT/.sisyphus/style/translation-smells.txt"

if [ ! -f "$SMELLS" ]; then
  echo "FATAL: smells dictionary not found at $SMELLS" >&2
  exit 2
fi

if [ "$#" -gt 0 ]; then
  TARGETS=("$@")
else
  TARGETS=()
  for d in "$ROOT"/azure-*/ko "$ROOT"/ai-web-dev-101; do
    [ -d "$d" ] && TARGETS+=("$d")
  done
  [ -f "$ROOT/README.md" ] && TARGETS+=("$ROOT/README.md")
fi

mapfile -t PATTERNS < <(grep -vE '^\s*(#|$)' "$SMELLS")

if [ "${#PATTERNS[@]}" -eq 0 ]; then
  echo "FATAL: no patterns loaded from $SMELLS" >&2
  exit 2
fi

COMBINED=$(IFS='|'; echo "${PATTERNS[*]}")

TOTAL=0
FILES_HIT=0

for t in "${TARGETS[@]}"; do
  while IFS= read -r -d '' f; do
    STRIPPED=$(awk '/^```/{c=!c; next} !c' "$f")
    HITS=$(printf '%s\n' "$STRIPPED" | grep -nE "$COMBINED" 2>/dev/null || true)
    if [ -n "$HITS" ]; then
      REL="${f#$ROOT/}"
      COUNT=$(printf '%s\n' "$HITS" | wc -l)
      printf '\n=== %s (%d) ===\n%s\n' "$REL" "$COUNT" "$HITS"
      TOTAL=$((TOTAL + COUNT))
      FILES_HIT=$((FILES_HIT + 1))
    fi
  done < <(find "$t" -type f -name '*.md' -print0 2>/dev/null)
done

echo ""
echo "=========================================="
echo "Files with smells: $FILES_HIT"
echo "Total smell hits:  $TOTAL"
echo "=========================================="

[ "$TOTAL" -eq 0 ] || exit 1
