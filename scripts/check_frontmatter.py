"""Validate YAML front matter on every article in content/.

Walks content/<series>/{ko,en}/*.md, parses front matter via python-frontmatter,
and fails on:
- missing required fields
- invalid status / language enum
- series id not in series.yaml
- language not declared in the series' languages: list
- episode/idx not matching the file's numeric prefix

Exit code: 0 on success, 1 on any validation error.

status enum: `planned` is a series-level state (in series.yaml) only.
Article-level front matter must be one of:
  draft, content-ready, code-checked, publish-ready, ready, published, needs-update.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
SERIES_YAML = REPO_ROOT / "series.yaml"

REQUIRED_FIELDS = {"title", "series", "episode", "language", "status", "targets", "tags", "last_reviewed"}
OPTIONAL_FIELDS = {"seo_title", "hashnode_title", "medium_title", "ebook_title", "published"}
VALID_STATUS = {"draft", "content-ready", "code-checked", "publish-ready", "ready", "published", "needs-update"}
VALID_LANGUAGE = {"ko", "en"}
TARGET_KEYS = {"tistory", "medium", "mkdocs", "ebook"}
OPTIONAL_TARGET_KEYS = {"hashnode"}
PUBLISHED_KEYS = {"tistory_url", "hashnode_url", "medium_url", "mkdocs_url"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PREFIX_RE = re.compile(r"^(\d+)")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def load_catalog() -> dict[str, dict]:
    raw = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    return {s["id"]: s for s in raw.get("series", [])}


def validate_article(path: Path, catalog: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as e:
        return [f"front matter parse error: {e}"]

    fm = post.metadata
    if not fm:
        return ["missing front matter (no `---` block at top)"]

    missing = REQUIRED_FIELDS - set(fm.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    status = fm.get("status")
    if status is not None and status not in VALID_STATUS:
        errors.append(f"invalid status: {status!r} (allowed: {sorted(VALID_STATUS)})")

    language = fm.get("language")
    if language is not None and language not in VALID_LANGUAGE:
        errors.append(f"invalid language: {language!r} (allowed: {sorted(VALID_LANGUAGE)})")

    series_id = fm.get("series")
    if series_id not in catalog:
        errors.append(f"series id not in series.yaml: {series_id!r}")
    elif language and language not in catalog[series_id].get("languages", []):
        errors.append(f"language {language!r} not declared in series {series_id!r}")

    expected_lang = path.parent.name
    if language and expected_lang in VALID_LANGUAGE and language != expected_lang:
        errors.append(f"language {language!r} disagrees with directory {expected_lang!r}")

    m = PREFIX_RE.match(path.stem)
    if m and "episode" in fm:
        try:
            file_idx = int(m.group(1))
            if int(fm["episode"]) != file_idx:
                errors.append(f"episode {fm['episode']} != file numeric prefix {file_idx}")
        except (TypeError, ValueError):
            errors.append(f"episode is not an integer: {fm['episode']!r}")

    targets = fm.get("targets")
    if targets is not None:
        if not isinstance(targets, dict):
            errors.append(f"targets must be a mapping, got {type(targets).__name__}")
        else:
            missing_targets = TARGET_KEYS - set(targets.keys())
            unknown_targets = set(targets.keys()) - TARGET_KEYS - OPTIONAL_TARGET_KEYS
            if missing_targets:
                errors.append(f"targets missing required channels: {sorted(missing_targets)}")
            if unknown_targets:
                errors.append(f"targets has unknown channels: {sorted(unknown_targets)} (allowed: {sorted(TARGET_KEYS | OPTIONAL_TARGET_KEYS)})")
            for k, v in targets.items():
                if not isinstance(v, bool):
                    errors.append(f"targets.{k} must be boolean, got {type(v).__name__}")

    published = fm.get("published")
    if published is not None:
        if not isinstance(published, dict):
            errors.append(f"published must be a mapping, got {type(published).__name__}")
        else:
            unknown_pub = set(published.keys()) - PUBLISHED_KEYS
            if unknown_pub:
                errors.append(f"published has unknown fields: {sorted(unknown_pub)} (allowed: {sorted(PUBLISHED_KEYS)})")
            for k, v in published.items():
                if not isinstance(v, str):
                    errors.append(f"published.{k} must be string URL, got {type(v).__name__}")

    tags = fm.get("tags")
    if tags is not None and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
        errors.append("tags must be a list of strings")

    last = fm.get("last_reviewed")
    if last is not None and not (isinstance(last, str) and DATE_RE.match(last)):
        errors.append(f"last_reviewed must be YYYY-MM-DD string, got {last!r}")

    fm_title = fm.get("title")
    if fm_title is not None:
        body = post.content
        m_h1 = H1_RE.search(body)
        if m_h1 is None:
            errors.append("body has no H1 (`# Title`) — front matter title cannot be cross-checked")
        elif m_h1.group(1).strip() != str(fm_title).strip():
            errors.append(
                f"H1 disagrees with front matter title:\n"
                f"      H1:    {m_h1.group(1).strip()!r}\n"
                f"      title: {str(fm_title).strip()!r}"
            )

    unknown = set(fm.keys()) - REQUIRED_FIELDS - OPTIONAL_FIELDS
    if unknown:
        errors.append(f"unknown fields: {sorted(unknown)}")

    return errors


def main() -> int:
    if not CONTENT_DIR.is_dir():
        print(f"no content/ directory at {CONTENT_DIR}", file=sys.stderr)
        return 1
    catalog = load_catalog()
    failures = 0
    checked = 0
    for md in sorted(CONTENT_DIR.glob("*/*/*.md")):
        if md.parent.name not in VALID_LANGUAGE:
            continue
        checked += 1
        errs = validate_article(md, catalog)
        if errs:
            failures += 1
            print(f"FAIL {md.relative_to(REPO_ROOT)}")
            for e in errs:
                print(f"  - {e}")
    print(f"\nchecked: {checked}, failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
