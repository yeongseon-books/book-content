#!/usr/bin/env python3
"""Guard: ko posts should not have untranslated English prose comments in source code blocks.

Checks for English explanatory comments (3+ words, contains function words) 
in Python/JS/TS/Go/Java/C/Rust code blocks.

Excludes (by design):
- File paths (server.py, src/foo.py)
- Install commands (pip install, npm install)
- Data/output values (dicts, lists, numbers)
- Math/graph notation (A -> B, P(A ∩ B))
- Code fragments (variable assignments, function calls)
- Short comments (< 3 words)
"""
import re
import glob
import sys

HAN = re.compile(r"[\uac00-\ud7a3]")
SRC = {
    "python", "py", "javascript", "js", "typescript", "ts",
    "rust", "rs", "go", "java", "c", "cpp", "csharp", "cs",
    "ruby", "rb", "php", "kotlin", "swift", "scala",
    "clojure", "elixir", "haskell",
}


def is_translatable_prose(text: str) -> bool:
    """Return True only for genuine English prose that should be translated."""
    t = text.strip()
    # Skip install commands
    if t.startswith(("pip install", "npm install", "cargo install")):
        return False
    # Skip data-like patterns
    if re.match(r'^[\d{(\[\'"%|~¬]', t):
        return False
    if re.match(r"^(\.\.\.|──|->)", t):
        return False
    # Skip code-like patterns
    if re.match(r"^[a-z_]\w*\s*[=.([\]]", t):
        return False
    if re.match(r"^[A-Z]\w*\s*[=.([\]]", t):
        return False
    # Skip lines with heavy symbols (math, data)
    if t.count("=") > 1 or t.count("{") > 0 or t.count("[") > 0:
        return False
    if t.count("'") > 1 or t.count('"') > 1:
        return False
    # Skip graph notation
    if re.match(r"^[A-Z]\s*->", t) or re.match(r"^[A-Z]:\s", t):
        return False
    # Must be mostly alphabetic
    alpha_ratio = sum(1 for c in t if c.isalpha()) / max(len(t), 1)
    if alpha_ratio < 0.5:
        return False
    # Must contain English prose indicators
    if not re.search(
        r"\b(the|is|are|do|does|for|to|of|with|from|if|when|this|that|"
        r"not|and|or|but|can|will|should|must|has|have|it|we|you|use|only)\b",
        t,
        re.I,
    ):
        return False
    # Must start with capital or prose word
    if not re.match(r"^[A-Z]", t) and not re.match(
        r"^(the|a|an|this|that|if|when|for|in|on|at|by|no|not)\b", t, re.I
    ):
        return False
    return True


def check():
    errors = []
    for f in sorted(glob.glob("content/*/ko/*.md")):
        if "azure-app-service-101" in f:
            continue
        # Deep-dive series intentionally cite external source code verbatim
        if "azure-functions-deep-dive" in f:
            continue
        body = re.sub(
            r"^---\n.*?\n---\n", "", open(f).read(), count=1, flags=re.S
        )
        for lang, code in re.findall(
            r"```([a-zA-Z0-9_+-]*)\n(.*?)```", body, re.S
        ):
            if lang.lower() not in SRC:
                continue
            for line in code.split("\n"):
                m = re.match(r"^\s*#\s+([^\s#].*)$", line)
                if not m:
                    m = re.match(r"^\s*//\s+(.+)$", line)
                if not m:
                    continue
                c = m.group(1).strip()
                if HAN.search(c):
                    continue
                if re.fullmatch(r"[\w./\\-]+\.\w+", c):
                    continue
                if c.startswith("→"):
                    continue
                # Skip code statements that happen to be comments
                if re.match(r"^(for |if |while |def |class |import |from )", c):
                    continue
                if len(c.split()) < 3:
                    continue
                if is_translatable_prose(c):
                    errors.append(f"  {f}: # {c}")

    if errors:
        print(
            f"FAIL: {len(errors)} untranslated English prose comments in ko code blocks:"
        )
        for e in errors:
            print(e)
        return 1
    print("PASS: No untranslated English prose comments in ko code blocks.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
