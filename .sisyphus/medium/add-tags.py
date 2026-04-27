#!/usr/bin/env python3
"""Insert series tag HTML comment at top of every post (ko/en/medium).

Tag source: README publishing checklist.
Format: <!-- tags: A, B, C, D -->
Insert: very first line. Idempotent: skip if line 1 already starts with `<!-- tags:`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SERIES_TAGS: dict[str, list[str]] = {
    "azure-app-service-101": ["Azure", "App Service", "Cloud", "Web Apps"],
    "azure-app-service-deep-dive": ["Azure", "App Service", "Distributed Systems", "Platform Engineering"],
    "azure-functions-101": ["Azure", "Azure Functions", "Serverless", "Cloud"],
    "azure-functions-deep-dive": ["Azure Functions", "Serverless", "Distributed Systems", "gRPC"],
    "azure-aks-101": ["Azure", "AKS", "Kubernetes", "Cloud"],
    "azure-aks-deep-dive": ["AKS", "Kubernetes", "Distributed Systems", "Containers"],
    "azure-aca-101": ["Azure", "Container Apps", "Serverless", "Containers"],
    "azure-aca-deep-dive": ["Container Apps", "KEDA", "Dapr", "Envoy"],
}


def tag_line(series: str) -> str:
    return f"<!-- tags: {', '.join(SERIES_TAGS[series])} -->"


def insert_tag(path: Path, series: str) -> str:
    text = path.read_text(encoding="utf-8")
    first_line = text.split("\n", 1)[0] if text else ""
    if first_line.startswith("<!-- tags:"):
        return "skip-existing"
    new_text = tag_line(series) + "\n" + text
    path.write_text(new_text, encoding="utf-8")
    return "inserted"


def main() -> int:
    counts = {"inserted": 0, "skip-existing": 0}
    for series in sorted(SERIES_TAGS):
        series_dir = ROOT / series
        if not series_dir.is_dir():
            print(f"SKIP missing: {series}")
            continue
        targets: list[Path] = []
        for sub in ("ko", "en", "medium"):
            sub_dir = series_dir / sub
            if sub_dir.is_dir():
                targets.extend(sorted(sub_dir.glob("*.md")))
        for md in targets:
            r = insert_tag(md, series)
            counts[r] += 1
            print(f"  {r}: {md.relative_to(ROOT)}")
    print(f"\nTotal inserted={counts['inserted']} skip-existing={counts['skip-existing']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
