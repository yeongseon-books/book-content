"""Execute Python code blocks in markdown files and inject their stdout output.

For each ```python ... ``` block that is NOT already followed by a
```\n출력 결과\n``` or ```\nOutput\n``` block, this script:

1. Runs the code in a subprocess with GROQ_API_KEY in env.
2. Captures stdout (up to 60 lines / 4 KB).
3. Inserts a fenced output block immediately after the closing ```.

Blocks are skipped if:
- Already has an output block immediately after.
- Code contains `input(` (interactive).
- Code raises an ImportError for a package not installed.
- Execution times out (30 s per block).

Usage:
    python3 scripts/inject_outputs.py content/llm-app-foundations-101/ko/02-understanding-tokens.md
    python3 scripts/inject_outputs.py content/llm-app-foundations-101/ko/
    python3 scripts/inject_outputs.py --series llm-app-foundations-101
    python3 scripts/inject_outputs.py --all-ai

Each file is rewritten in place. Run finalize-posts.py afterwards to sync
TOC/tags.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── regex ────────────────────────────────────────────────────────────────────

PYTHON_BLOCK_RE = re.compile(
    r"(```python\n)(.*?)(```)",
    re.DOTALL,
)

# Already-inserted output block patterns (ko or en)
OUTPUT_BLOCK_RE = re.compile(
    r"^(```|~~~)\n(출력 결과|Output|출력)\n",
    re.MULTILINE,
)

FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

MAX_OUTPUT_LINES = 60
MAX_OUTPUT_BYTES = 4096
TIMEOUT_SECS = 45

AI_SERIES = [
    "llm-app-foundations-101",
    "llm-api-production-101",
    "vector-search-101",
    "langchain-101",
    "ai-app-patterns-101",
    "korean-ai-stack-101",
    "document-ingestion-101",
    "llm-apps-ops-101",
    "rag-benchmark-101",
    "langgraph-101",
    "llm-finetuning-101",
    "rag-deep-dive",
]


# ── helpers ──────────────────────────────────────────────────────────────────


_LLM_CALL_PATTERNS = re.compile(
    r"chat\.completions\.create|AsyncGroq|stream=True|\.stream\(|EventSource|StreamingResponse",
)

def run_block(code: str, lang: str) -> str | None:
    """Execute code, return trimmed stdout or None on skip/error."""
    if "input(" in code:
        return None
    if _LLM_CALL_PATTERNS.search(code):
        return None

    env = {**os.environ, "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", "")}

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECS,
            env=env,
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired:
        print(f"    [timeout after {TIMEOUT_SECS}s — skipped]")
        return None

    if result.returncode != 0:
        err = result.stderr.strip()
        # Skip if missing package
        if "ModuleNotFoundError" in err or "ImportError" in err:
            pkg = re.search(r"No module named '([^']+)'", err)
            print(f"    [missing package: {pkg.group(1) if pkg else '?'} — skipped]")
            return None
        # Other errors: print warning, still skip
        print(f"    [exit {result.returncode}] {err[:120]}")
        return None

    out = result.stdout
    if not out.strip():
        return None  # nothing to show

    # Trim
    lines = out.splitlines()
    if len(lines) > MAX_OUTPUT_LINES:
        lines = lines[:MAX_OUTPUT_LINES] + ["... (truncated)"]
        out = "\n".join(lines)
    if len(out.encode()) > MAX_OUTPUT_BYTES:
        out = out.encode()[:MAX_OUTPUT_BYTES].decode(errors="replace") + "\n... (truncated)"

    out = _sanitize_output(out)
    return out.rstrip()


def _sanitize_output(text: str) -> str:
    """Convert ALL fence markers (``` or ~~~) to 4-space-indented lines.

    This is intentionally unconditional — we don't track open/close state
    because LLM responses may contain an odd number of fences, which would
    corrupt stateful toggling.  The output block is wrapped in ~~~ by the
    caller, so any inner ``` or ~~~ must be indented to avoid breaking the
    outer fence.
    """
    lines = text.splitlines()
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            result.append("    " + line)
        else:
            result.append(line)
    return "\n".join(result)


def label_for(lang: str) -> str:
    return "출력 결과" if lang == "ko" else "Output"


def already_has_output(text: str, end_pos: int) -> bool:
    """Check if the text immediately after end_pos starts with an output block."""
    after = text[end_pos:].lstrip("\n")
    return bool(OUTPUT_BLOCK_RE.match(after))


def inject_file(path: Path) -> int:
    """Process one markdown file. Returns number of blocks injected."""
    lang = "ko" if "/ko/" in str(path) else "en"
    text = path.read_text(encoding="utf-8")
    label = label_for(lang)

    injected = 0
    offset = 0
    new_parts: list[str] = []

    for m in PYTHON_BLOCK_RE.finditer(text):
        # Text before this match
        new_parts.append(text[offset : m.start()])
        offset = m.end()

        fence_open = m.group(1)   # ```python\n
        code = m.group(2)         # code body
        fence_close = m.group(3)  # ```

        # Check if output already follows
        if already_has_output(text, m.end()):
            new_parts.append(fence_open + code + fence_close)
            continue

        print(f"  executing block ({len(code.splitlines())} lines)…", end=" ", flush=True)
        out = run_block(code, lang)

        if out is None:
            print("skipped")
            new_parts.append(fence_open + code + fence_close)
            continue

        print(f"ok ({len(out.splitlines())} lines)")
        output_block = f"\n\n~~~\n{label}\n{out}\n~~~"
        new_parts.append(fence_open + code + fence_close + output_block)
        injected += 1

    new_parts.append(text[offset:])
    new_text = "".join(new_parts)

    if injected:
        path.write_text(new_text, encoding="utf-8")

    return injected


def collect_files(args: argparse.Namespace) -> list[Path]:
    files: list[Path] = []

    if args.all_ai:
        for s in AI_SERIES:
            for lang in ["ko", "en"]:
                d = REPO_ROOT / "content" / s / lang
                if d.exists():
                    files.extend(sorted(d.glob("*.md")))
        return files

    if args.series:
        for s in args.series:
            for lang in ["ko", "en"]:
                d = REPO_ROOT / "content" / s / lang
                if d.exists():
                    files.extend(sorted(d.glob("*.md")))
        return files

    for p in args.paths:
        path = Path(p).resolve()
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.is_file():
            files.append(path)

    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--series", nargs="+", metavar="SERIES_ID")
    ap.add_argument("--all-ai", action="store_true")
    ap.add_argument(
        "--lang", choices=["ko", "en", "both"], default="both",
        help="which language variant to process (default: both)"
    )
    args = ap.parse_args()

    if not args.paths and not args.series and not args.all_ai:
        ap.print_help()
        return 1

    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set", file=sys.stderr)
        return 1

    files = collect_files(args)

    # Filter by lang
    if args.lang != "both":
        files = [f for f in files if f"/{args.lang}/" in str(f)]

    total_injected = 0
    for f in files:
        print(f"\n>>> {f.relative_to(REPO_ROOT)}")
        n = inject_file(f)
        print(f"  => {n} block(s) injected")
        total_injected += n

    print(f"\nDONE: {total_injected} output block(s) across {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
