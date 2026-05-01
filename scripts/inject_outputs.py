"""Execute Python code blocks in markdown files and inject their stdout output.

For each ```python ... ``` block not already followed by an injected-output
marker, this script:

1. Runs the code in a subprocess with GROQ_API_KEY in env.
2. Captures stdout (up to 60 lines / 4 KB).
3. Inserts a marker-delimited indented output block immediately after.

Output shape (safe against any stdout content):

    <!-- injected-output:start -->
    **Output**

        line 1 of stdout
        line 2 of stdout

    <!-- injected-output:end -->

For ko files the label is **출력 결과**.

Indented code blocks cannot be broken by arbitrary stdout — backtick/tilde
fences, markdown headings, HTML, or any other markdown in the output are
rendered as plain text inside the four-space block.

Blocks are skipped if:
- Already has an injected-output marker immediately after.
- Code contains input( (interactive).
- Code matches LLM/network/chain call patterns (nondeterministic).
- Code raises ImportError for a package not installed.
- Execution times out (45 s per block).

Usage:
    python3 scripts/inject_outputs.py content/llm-app-foundations-101/ko/02.md
    python3 scripts/inject_outputs.py content/llm-app-foundations-101/ko/
    python3 scripts/inject_outputs.py --series llm-app-foundations-101
    python3 scripts/inject_outputs.py --all-ai

Each file is rewritten in place. Run finalize-posts.py afterwards.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PYTHON_BLOCK_RE = re.compile(
    r"(```python\n)(.*?)(```)",
    re.DOTALL,
)

MARKER_START = "<!-- injected-output:start -->"
MARKER_END = "<!-- injected-output:end -->"

MARKER_BLOCK_RE = re.compile(
    r"\n\n" + re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\n",
    re.DOTALL,
)

MAX_OUTPUT_LINES = 60
MAX_OUTPUT_BYTES = 4096
TIMEOUT_SECS = 60

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

_SKIP_PATTERNS = re.compile(
    r"stream=True"
    r"|EventSource"
    r"|StreamingResponse"
    r"|AsyncGroq"
    r"|asyncio\.run\(",
)


def _indent_output(text: str) -> str:
    lines = text.splitlines()
    indented = []
    for line in lines:
        indented.append("    " + line if line.strip() else "")
    return "\n".join(indented)


def _make_output_block(out: str, lang: str) -> str:
    label = "**출력 결과**" if lang == "ko" else "**Output**"
    indented = _indent_output(out)
    return (
        f"\n\n{MARKER_START}\n"
        f"{label}\n\n"
        f"{indented}\n\n"
        f"{MARKER_END}"
    )


def run_block(code: str, context: str = "") -> str | None:
    """Run a single code block, optionally prepending accumulated context.

    The context portion has its stdout suppressed (redirected to /dev/null)
    so only the current block's output is captured.
    """
    if "input(" in code:
        return None
    if _SKIP_PATTERNS.search(code):
        return None

    # Build the full script: suppress context output, then run current block
    if context.strip():
        full_code = (
            "import sys as _sys, os as _os\n"
            "_devnull = open(_os.devnull, 'w')\n"
            "_real_stdout = _sys.stdout\n"
            "_sys.stdout = _devnull\n"
            "try:\n"
            + "\n".join("    " + line for line in context.splitlines())
            + "\nexcept Exception:\n    pass\nfinally:\n    _sys.stdout = _real_stdout\n    _devnull.close()\n"
            + code
        )
    else:
        full_code = code

    env = {**os.environ, "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", "")}

    try:
        result = subprocess.run(
            [sys.executable, "-c", full_code],
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
        if "ModuleNotFoundError" in err or "ImportError" in err:
            pkg = re.search(r"No module named '([^']+)'", err)
            print(f"    [missing package: {pkg.group(1) if pkg else '?'} — skipped]")
            return None
        print(f"    [exit {result.returncode}] {err[:120]}")
        return None

    out = result.stdout
    if not out.strip():
        return None

    lines = out.splitlines()
    if len(lines) > MAX_OUTPUT_LINES:
        lines = lines[:MAX_OUTPUT_LINES] + ["... (truncated)"]
        out = "\n".join(lines)
    if len(out.encode()) > MAX_OUTPUT_BYTES:
        out = out.encode()[:MAX_OUTPUT_BYTES].decode(errors="replace") + "\n... (truncated)"

    return out.rstrip()


def already_has_output(text: str, end_pos: int) -> bool:
    after = text[end_pos:].lstrip("\n")
    return after.startswith(MARKER_START)


def inject_file(path: Path) -> int:
    lang = "ko" if "/ko/" in str(path) else "en"
    text = path.read_text(encoding="utf-8")

    injected = 0
    offset = 0
    new_parts: list[str] = []
    accumulated_context: list[str] = []

    for m in PYTHON_BLOCK_RE.finditer(text):
        new_parts.append(text[offset: m.start()])
        offset = m.end()

        fence_open = m.group(1)
        code = m.group(2)
        fence_close = m.group(3)

        if already_has_output(text, m.end()):
            accumulated_context.append(code)
            new_parts.append(fence_open + code + fence_close)
            continue

        print(f"  executing block ({len(code.splitlines())} lines)…", end=" ", flush=True)
        context = "\n".join(accumulated_context)
        out = run_block(code, context=context)

        accumulated_context.append(code)

        if out is None:
            print("skipped")
            new_parts.append(fence_open + code + fence_close)
            continue

        print(f"ok ({len(out.splitlines())} lines)")
        new_parts.append(fence_open + code + fence_close + _make_output_block(out, lang))
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
    ap.add_argument("--lang", choices=["ko", "en", "both"], default="both")
    args = ap.parse_args()

    if not args.paths and not args.series and not args.all_ai:
        ap.print_help()
        return 1

    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set", file=sys.stderr)
        return 1

    files = collect_files(args)

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
