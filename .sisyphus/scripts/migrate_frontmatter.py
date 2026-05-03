#!/usr/bin/env python3
"""One-shot frontmatter migration to fix all 78 `make check` failures.

Categories handled:
  A) git-github-101 Eps 2-10 (18 files): old schema → canonical schema
     - add: episode (from order), language (from path)
     - convert targets: {ko: tistory, en: hashnode} → {tistory: true, medium: true, hashnode: true, mkdocs: true, ebook: true}
     - drop: date, description, order
  B) python-dbapi-101 Eps 7-10 (8 files): same migration as A, but targets is currently a list
  C) vector-search-101 (12 files): add title from H1
  D) ai-data-preparation-101 (8 files): sync title to richer H1
"""

from __future__ import annotations
import re, sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

CANONICAL_TARGETS = {
    "tistory": True,
    "medium": True,
    "hashnode": True,
    "mkdocs": True,
    "ebook": True,
}


def get_h1(body: str) -> str | None:
    m = H1_RE.search(body)
    return m.group(1).strip() if m else None


def migrate_canonical(path: Path) -> list[str]:
    """A+B: migrate old schema to canonical."""
    changes = []
    post = frontmatter.load(path)
    fm = post.metadata
    lang = path.parent.name  # ko or en
    if "language" not in fm:
        fm["language"] = lang
        changes.append(f"+language={lang}")
    if "episode" not in fm:
        if "order" in fm:
            fm["episode"] = fm.pop("order")
            changes.append(f"+episode={fm['episode']} (from order)")
        else:
            prefix = re.match(r"^(\d+)", path.stem)
            if prefix:
                fm["episode"] = int(prefix.group(1))
                changes.append(f"+episode={fm['episode']} (from filename)")
    # normalize targets
    targets = fm.get("targets")
    if not isinstance(targets, dict) or not all(
        isinstance(v, bool) for v in targets.values()
    ):
        fm["targets"] = dict(CANONICAL_TARGETS)
        changes.append("targets→canonical bool mapping")
    # drop unknowns
    for k in ("date", "description", "order"):
        if k in fm:
            del fm[k]
            changes.append(f"-{k}")
    # last_reviewed: if missing but date existed, we already dropped date — backfill from today's last_reviewed convention
    if "last_reviewed" not in fm:
        # use a stable date if not present (shouldn't be; A files all have it). fallback: file mtime as YYYY-MM-DD
        from datetime import date

        fm["last_reviewed"] = date.today().isoformat()
        changes.append(f"+last_reviewed={fm['last_reviewed']}")
    if changes:
        path.write_bytes(frontmatter.dumps(post).encode("utf-8") + b"\n")
    return changes


def add_title_from_h1(path: Path) -> list[str]:
    """C: add title from body H1."""
    post = frontmatter.load(path)
    if "title" in post.metadata:
        return []
    h1 = get_h1(post.content)
    if not h1:
        return [f"!! no H1 found in {path}"]
    post.metadata["title"] = h1
    path.write_bytes(frontmatter.dumps(post).encode("utf-8") + b"\n")
    return [f"+title={h1!r}"]


def sync_title_to_h1(path: Path) -> list[str]:
    """D: replace title field with the body H1 (richer version)."""
    post = frontmatter.load(path)
    h1 = get_h1(post.content)
    if not h1:
        return [f"!! no H1 in {path}"]
    old = post.metadata.get("title")
    if old == h1:
        return []
    post.metadata["title"] = h1
    path.write_bytes(frontmatter.dumps(post).encode("utf-8") + b"\n")
    return [f"title: {old!r} → {h1!r}"]


def run():
    total = 0
    # Category A: git-github-101 Eps 2-10
    for lang in ("ko", "en"):
        for ep in range(2, 11):
            files = list((CONTENT / "git-github-101" / lang).glob(f"{ep:02d}-*.md"))
            for f in files:
                ch = migrate_canonical(f)
                if ch:
                    total += 1
                    print(f"[A] {f.relative_to(ROOT)}: {', '.join(ch)}")
    # Category B: python-dbapi-101 Eps 7-10
    for lang in ("ko", "en"):
        for ep in range(7, 11):
            files = list((CONTENT / "python-dbapi-101" / lang).glob(f"{ep:02d}-*.md"))
            for f in files:
                ch = migrate_canonical(f)
                if ch:
                    total += 1
                    print(f"[B] {f.relative_to(ROOT)}: {', '.join(ch)}")
    # Category C: vector-search-101 missing title
    for lang in ("ko", "en"):
        for f in sorted((CONTENT / "vector-search-101" / lang).glob("*.md")):
            ch = add_title_from_h1(f)
            if ch:
                total += 1
                print(f"[C] {f.relative_to(ROOT)}: {', '.join(ch)}")
    # Category D: ai-data-preparation-101 H1 sync
    targets_d = [
        ("en", "06-quality-filtering.md"),
        ("en", "07-synthetic-data-generation.md"),
        ("en", "08-data-augmentation.md"),
        ("ko", "05-tokenization-chunking.md"),
        ("ko", "06-quality-filtering.md"),
        ("ko", "07-synthetic-data-generation.md"),
        ("ko", "08-data-augmentation.md"),
        ("ko", "09-train-eval-test-splitting.md"),
    ]
    for lang, name in targets_d:
        f = CONTENT / "ai-data-preparation-101" / lang / name
        ch = sync_title_to_h1(f)
        if ch:
            total += 1
            print(f"[D] {f.relative_to(ROOT)}: {', '.join(ch)}")
    print(f"\nTotal files migrated: {total}")


if __name__ == "__main__":
    run()
