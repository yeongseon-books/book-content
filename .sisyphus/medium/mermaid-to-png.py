#!/usr/bin/env python3
"""
mermaid-to-png.py — replace ```mermaid``` blocks in markdown with PNG image refs.

For each markdown file:
  1. Find every ```mermaid ... ``` block.
  2. Extract a slug from a heading immediately before the block (if any) or block index.
  3. Render to assets/<series>/<NN>/<NN>-<slug>.{ko|en}.png via mmdc.
  4. Replace the block in-place with `![alt](../../assets/...)`.
  5. Write the modified markdown back.

Usage:
  ./mermaid-to-png.py <markdown-file> [<markdown-file> ...]

Naming pattern matches existing assets/azure-app-service-101/ structure:
  - <series> = parent-of-parent of the markdown file (e.g. azure-aks-101)
  - <NN>     = leading 2-digit prefix of the markdown filename (01-foo.md -> "01")
  - <slug>   = nearest preceding heading text slugified, fallback to <NN>+block_idx
  - lang     = "ko" or "en" inferred from path .../ko/... or .../en/...
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PUPPETEER_CFG = REPO_ROOT / ".sisyphus/medium/puppeteer.json"
MERMAID_CFG = REPO_ROOT / ".sisyphus/medium/mermaid-config.json"
MMDC = shutil.which("mmdc") or "mmdc"

MERMAID_BLOCK_RE = re.compile(r"^```mermaid\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def slugify(text: str, max_len: int = 40) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if not text:
        return "diagram"
    return text[:max_len].rstrip("-")


def detect_lang(md_path: Path) -> str:
    parts = md_path.parts
    for p in reversed(parts):
        if p in ("ko", "en"):
            return p
    raise ValueError(f"cannot detect ko/en in path: {md_path}")


def detect_series(md_path: Path) -> str:
    return md_path.parents[1].name


def episode_prefix(md_path: Path) -> str:
    m = re.match(r"^(\d{2})", md_path.name)
    return m.group(1) if m else "00"


def find_preceding_heading(text_before: str) -> str | None:
    matches = list(HEADING_RE.finditer(text_before))
    if not matches:
        return None
    return matches[-1].group(2).strip()


def en_counterpart(md_path: Path) -> Path | None:
    parts = list(md_path.parts)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == "ko":
            parts[i] = "en"
            cand = Path(*parts)
            return cand if cand.exists() else None
    return None


def en_block_headings(en_path: Path) -> list[str | None]:
    src = en_path.read_text(encoding="utf-8")
    headings: list[str | None] = []
    for m in MERMAID_BLOCK_RE.finditer(src):
        h = find_preceding_heading(src[: m.start()])
        headings.append(h)
    return headings


def extract_alt_text(mermaid_src: str, fallback: str) -> str:
    for line in mermaid_src.splitlines():
        line = line.strip()
        if line.startswith("title"):
            return line.split(":", 1)[-1].strip().strip('"')
    return fallback


def render_png(mermaid_src: str, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_src)
        tmp = f.name
    try:
        cmd = [
            MMDC,
            "-i", tmp,
            "-o", str(out_png),
            "-b", "white",
            "-w", "1400",
            "-p", str(PUPPETEER_CFG),
            "-c", str(MERMAID_CFG),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 or not out_png.exists():
            raise RuntimeError(
                f"mmdc failed for {out_png.name}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            )
    finally:
        os.unlink(tmp)


def process_file(md_path: Path) -> tuple[int, list[tuple[int, str]]]:
    src = md_path.read_text(encoding="utf-8")
    matches = list(MERMAID_BLOCK_RE.finditer(src))
    if not matches:
        return 0, []

    lang = detect_lang(md_path)
    series = detect_series(md_path)
    ep = episode_prefix(md_path)

    slug_source_headings: list[str | None]
    if lang == "ko":
        en_path = en_counterpart(md_path)
        if en_path is not None:
            en_heads = en_block_headings(en_path)
            if len(en_heads) == len(matches):
                slug_source_headings = en_heads
            else:
                print(
                    f"    WARN: en counterpart has {len(en_heads)} mermaid blocks vs ko {len(matches)}; falling back to ko headings",
                    file=sys.stderr,
                )
                slug_source_headings = [find_preceding_heading(src[: m.start()]) for m in matches]
        else:
            slug_source_headings = [find_preceding_heading(src[: m.start()]) for m in matches]
    else:
        slug_source_headings = [find_preceding_heading(src[: m.start()]) for m in matches]

    new_parts: list[str] = []
    cursor = 0
    used_slugs: dict[str, int] = {}
    failures: list[tuple[int, str]] = []
    replaced = 0

    for idx, m in enumerate(matches, start=1):
        block_start = m.start()
        block_end = m.end()
        mermaid_src = m.group(1)

        slug_heading = slug_source_headings[idx - 1]
        ko_heading = find_preceding_heading(src[:block_start]) if lang == "ko" else slug_heading
        base_slug = slugify(slug_heading) if slug_heading else f"diagram-{idx}"

        count = used_slugs.get(base_slug, 0) + 1
        used_slugs[base_slug] = count
        slug = base_slug if count == 1 else f"{base_slug}-{count}"

        png_name = f"{ep}-{idx:02d}-{slug}.{lang}.png"
        if "content" in md_path.parts:
            rel_png = Path(f"../../../assets/{series}/{ep}/{png_name}")
        else:
            rel_png = Path(f"../../assets/{series}/{ep}/{png_name}")
        abs_png = REPO_ROOT / "assets" / series / ep / png_name

        alt = extract_alt_text(mermaid_src, ko_heading or slug_heading or f"{series} diagram {idx}")

        print(f"  [{idx}/{len(matches)}] {png_name}")
        try:
            render_png(mermaid_src, abs_png)
        except Exception as e:
            short = str(e).splitlines()[0] if str(e) else "unknown"
            print(f"    FAIL: {short}", file=sys.stderr)
            failures.append((idx, png_name))
            new_parts.append(src[cursor:block_end])
            cursor = block_end
            continue

        new_parts.append(src[cursor:block_start])
        new_parts.append(f"![{alt}]({rel_png.as_posix()})")
        cursor = block_end
        replaced += 1

    new_parts.append(src[cursor:])
    if replaced > 0:
        md_path.write_text("".join(new_parts), encoding="utf-8")
    return replaced, failures


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: mermaid-to-png.py <md-file> [<md-file> ...]", file=sys.stderr)
        return 2
    total_blocks = 0
    total_files = 0
    all_failures: list[tuple[Path, int, str]] = []
    for arg in argv[1:]:
        path = Path(arg).resolve()
        if not path.exists():
            print(f"skip (not found): {path}", file=sys.stderr)
            continue
        print(f"\n>>> {path.relative_to(REPO_ROOT)}")
        n, fails = process_file(path)
        if n:
            total_files += 1
            total_blocks += n
            print(f"    replaced {n} mermaid block(s)")
        elif not fails:
            print("    no mermaid blocks")
        for idx, name in fails:
            all_failures.append((path, idx, name))
    print(f"\nDONE: {total_blocks} blocks across {total_files} file(s)")
    if all_failures:
        print(f"\nFAILURES ({len(all_failures)}):")
        for path, idx, name in all_failures:
            print(f"  {path.relative_to(REPO_ROOT)}  block #{idx}  -> {name}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
