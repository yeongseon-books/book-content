#!/usr/bin/env python3
"""Shared series catalog loader for finalize-posts.py and to-medium.py.

Single source of truth: top-level series.yaml. Each series entry has a `path:`
field; tools resolve series locations through this field, NOT by guessing
`ROOT/<series-id>`. This decouples series identity (id) from filesystem
location (path), enabling Phase 6 moves to `content/<series>/` without
breaking tooling.

Resolution rules:
- `path:` is interpreted relative to repo root.
- A series is "present on disk" iff `ROOT/<path>` exists as a directory AND
  contains at least one of: ko/, en/, medium/, or *.md (flat single-variant).
- Tools should iterate over present series only; planned/missing series are
  silently skipped.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "series.yaml"


@dataclass(frozen=True)
class SeriesEntry:
    id: str
    path: Path  # absolute, repo-root-anchored
    languages: tuple[str, ...]


def load_catalog() -> list[SeriesEntry]:
    """Return all series entries with `path:` resolved against repo root.

    Does NOT filter by presence; callers decide whether to skip missing dirs.
    """
    raw = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    out: list[SeriesEntry] = []
    for s in raw.get("series", []):
        sid = s["id"]
        rel = s.get("path", sid)
        languages = tuple(s.get("languages", ["ko"]))
        out.append(SeriesEntry(id=sid, path=(ROOT / rel).resolve(), languages=languages))
    return out


def is_present(entry: SeriesEntry) -> bool:
    """A series is present if its directory exists and has any markdown content."""
    if not entry.path.is_dir():
        return False
    for sub in ("ko", "en", "medium"):
        if (entry.path / sub).is_dir():
            return True
    # Flat single-variant layout (e.g. ai-web-dev-101 pre-Phase-6).
    return any(entry.path.glob("*.md"))
