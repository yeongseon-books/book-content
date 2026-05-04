"""Seed seo_title and seo_description into article frontmatter.

Deterministic extraction from each article's own body — no LLM paraphrase,
no AI slop. Author can refine seeded values afterwards.

For each content/<series>/{ko,en}/<NN>-*.md:

seo_title:
  - If `len(NFC(title)) <= hard_limit[lang]`, omit seo_title entirely
    (resolver inherits from canonical title).
  - Else: try (a) drop trailing parenthetical, (b) drop leading "EpisodeN: "
    style prefix. If still over: emit a TODO marker and skip writing seo_title.

seo_description:
  - First non-blockquote-leading non-empty paragraph after H1, with the
    following exclusions:
      * lines that are only `> (N/M)` series-position markers
      * markdown list bullets / heading lines / code fences
      * existing seo_description front matter line (idempotent)
  - Strip markdown formatting (`**bold**`, `[text](url)` -> `text`,
    backticks). Collapse whitespace. Trim to recommended limit on a sentence
    boundary; if no boundary, soft-cut on word boundary.
  - Recommended limits: ko 75, en 145. Hard limits: ko 80, en 150.
  - Skip files where seo_description already present.

Idempotent. Writes only when seeds differ from existing values.

Usage:
  python3 scripts/seed_seo_metadata.py <series-id> [<series-id>...]
  python3 scripts/seed_seo_metadata.py --all
  python3 scripts/seed_seo_metadata.py --dry-run <series-id>
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
SERIES_YAML = REPO_ROOT / "series.yaml"

# NFC code-points (matches scripts/check_frontmatter.py SEO_LIMITS).
SEO_LIMITS = {
    "ko": {
        "seo_title_hard": 36,
        "seo_title_rec": 32,
        "seo_desc_hard": 80,
        "seo_desc_rec": 75,
    },
    "en": {
        "seo_title_hard": 60,
        "seo_title_rec": 55,
        "seo_desc_hard": 150,
        "seo_desc_rec": 145,
    },
}

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
PAREN_TAIL_RE = re.compile(r"\s*\([^()]*\)\s*$")
EPISODE_PREFIX_RE = re.compile(r"^(?:Episode|에피소드)\s*\d+\s*[:\-]\s*", re.IGNORECASE)
SERIES_POS_RE = re.compile(r"^\((\d+)\s*/\s*(\d+)\)\s*$")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
CODE_RE = re.compile(r"`([^`]+)`")
WS_RE = re.compile(r"\s+")
TOC_BEGIN = "<!-- toc:begin -->"

# Section header patterns (case-insensitive substring after H2 ## ).
MENTAL_MODEL_HEADERS = ("mental model", "\ud575\uc2ec \ube44\uc720", "\ud575\uc2ec \ubaa8\ub378")
WHY_HEADERS_KO = ("\uc65c \uc911\uc694\ud55c\uac00", "\uc65c \uc911\uc694\ud569\ub2c8\uae4c")
WHY_HEADERS_EN = ("why it matters", "why this matters", "why it's important")

# Meta-intro phrase prefixes to skip (paragraph starts with these).
META_INTRO_KO = (
    "\uc774 \uae00\uc744 \ub9c8\uce58\uba74",
    "\uc774 \uae00\uc744 \uc77d\uace0 \ub098\uba74",
    "\uc774 \uae00\uc5d0\uc11c\ub294",
    "\uc774 \uae00\uc758 \ubaa9\ud45c\ub294",
    "\uc774 \uc7a5\uc744 \ub9c8\uce58\uba74",
    "\uc774\ubc88 \uae00\uc5d0\uc11c\ub294",
    "\uc774 \uc5d0\ud53c\uc18c\ub4dc\uc5d0\uc11c\ub294",
    "\uc774 \uae00\uc740 Python",
    "\uc774 \uae00\uc740 \ub2e4\uc74c",
    "\uc774 \uc7a5\uc740 \ub2e4\uc74c",
)
META_INTRO_EN = (
    "by the end of",
    "after reading",
    "in this chapter",
    "this chapter",
    "in this article",
    "this article",
    "in this episode",
    "this episode",
    "this post",
    "in this post",
    "this guide",
    "in this guide",
    "this targets",
    "this chapter targets",
)

def nfc_len(s: str) -> int:
    return len(unicodedata.normalize("NFC", s))


def strip_markdown(text: str) -> str:
    text = LINK_RE.sub(r"\1", text)
    text = BOLD_RE.sub(r"\1", text)
    text = ITAL_RE.sub(r"\1", text)
    text = CODE_RE.sub(r"\1", text)
    return WS_RE.sub(" ", text).strip()


def cut_to_limit(text: str, hard: int, rec: int, lang: str) -> str:
    """Trim text to <= hard, preferring sentence boundary in [rec/2, hard]."""
    text = unicodedata.normalize("NFC", text).strip()
    if len(text) <= rec:
        return text
    sent_end = "\u3002.!?" if lang == "ko" else ".!?"
    min_acceptable = max(rec // 2, 30)
    best = -1
    for i, ch in enumerate(text[:hard]):
        if ch in sent_end:
            if lang == "ko":
                if ch == "." and i >= 1 and text[i - 1] == "\ub2e4":
                    best = i + 1
                elif ch in "!?":
                    best = i + 1
                elif ch == "\u3002":
                    best = i + 1
            else:
                if i + 1 == len(text) or text[i + 1] in " \n":
                    best = i + 1
    if best >= min_acceptable and best <= hard:
        return text[:best].strip()
    if len(text) <= hard:
        return text
    cut = text[: hard - 1]
    sp = cut.rfind(" ")
    if sp > hard // 2:
        cut = cut[:sp]
    return cut.rstrip(" ,.;:-") + "\u2026"


def extract_seo_title(title: str, lang: str) -> tuple[str | None, str | None]:
    """Return (seo_title or None, todo_reason or None).

    None seo_title means inherit canonical title (it already fits).
    """
    L = SEO_LIMITS[lang]
    hard = L["seo_title_hard"]
    if nfc_len(title) <= hard:
        return None, None
    # Try (a) drop trailing parenthetical, e.g. "Foo (Bar)" -> "Foo"
    cand = PAREN_TAIL_RE.sub("", title).strip()
    if cand and nfc_len(cand) <= hard:
        return cand, None
    # Try (b) drop "EpisodeN: " / "에피소드N: "
    cand2 = EPISODE_PREFIX_RE.sub("", title).strip()
    if cand2 and nfc_len(cand2) <= hard:
        return cand2, None
    return (
        None,
        f"title too long ({nfc_len(title)} > {hard}); manual seo_title required",
    )


def _is_hr(line: str) -> bool:
    s = line.strip()
    return bool(s and re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", s))


def _is_meta_intro(text: str, lang: str) -> bool:
    t = text.lstrip().lower()
    prefixes = META_INTRO_KO if lang == "ko" else META_INTRO_EN
    return any(t.startswith(p) for p in prefixes)


def _para_acceptable(p: str) -> str | None:
    """Return cleaned paragraph text if usable as description source, else None."""
    s = p.lstrip()
    if s.startswith("#") or s.startswith("```") or s.startswith("|"):
        return None
    non_hr_lines = [ln for ln in p.splitlines() if not _is_hr(ln) and ln.strip()]
    if not non_hr_lines:
        return None
    if all(ln.lstrip().startswith("#") for ln in non_hr_lines):
        return None
    if all(
        re.match(r"^\s*[-*+]\s", ln) or re.match(r"^\s*\d+\.\s", ln)
        for ln in non_hr_lines
    ):
        return None
    if s.startswith(">"):
        inner_lines = [re.sub(r"^\s*>\s?", "", ln) for ln in p.splitlines()]
        inner = " ".join(inner_lines).strip()
        if not inner or SERIES_POS_RE.match(inner):
            return None
        return inner
    # strip leading/trailing HR lines from the paragraph
    cleaned = "\n".join(non_hr_lines)
    return cleaned


def _split_paragraphs(text: str) -> list[str]:
    paras: list[str] = []
    cur: list[str] = []
    for raw in text.splitlines():
        ln = raw.rstrip()
        if _is_hr(ln):
            if cur:
                paras.append("\n".join(cur).strip())
                cur = []
            continue
        if not ln.strip():
            if cur:
                paras.append("\n".join(cur).strip())
                cur = []
            continue
        cur.append(ln)
    if cur:
        paras.append("\n".join(cur).strip())
    return paras


def _section_after(body: str, header_substrs: tuple[str, ...]) -> str | None:
    """Return body text starting AFTER the matching `## Header` line, until next H2."""
    lines = body.splitlines()
    start = -1
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m and any(h in m.group(1).lower() for h in header_substrs):
            start = i + 1
            break
    if start < 0:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^##\s+", lines[j]):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def _first_good_paragraph(section: str, lang: str, min_len: int) -> str | None:
    for p in _split_paragraphs(section):
        clean = _para_acceptable(p)
        if clean is None:
            continue
        if _is_meta_intro(clean, lang):
            continue
        if len(clean) < min_len:
            continue
        return clean
    return None


def first_paragraph(body: str, lang: str) -> str | None:
    """Priority extractor: Mental Model > Why It Matters > any non-meta paragraph."""
    if TOC_BEGIN in body:
        body = body.split(TOC_BEGIN, 1)[0]
    body = H1_RE.sub("", body, count=1).lstrip()

    # Priority 1: Mental Model section (often a punchy blockquote).
    sec = _section_after(body, MENTAL_MODEL_HEADERS)
    if sec:
        cand = _first_good_paragraph(sec, lang, min_len=20)
        if cand:
            return cand

    # Priority 2: Why It Matters section.
    why_headers = WHY_HEADERS_KO if lang == "ko" else WHY_HEADERS_EN
    sec = _section_after(body, why_headers)
    if sec:
        cand = _first_good_paragraph(sec, lang, min_len=30)
        if cand:
            return cand

    # Priority 3: Any acceptable non-meta paragraph in the whole body.
    cand = _first_good_paragraph(body, lang, min_len=40)
    if cand:
        return cand

    # Last resort: any acceptable paragraph (even meta-intro), to avoid empty.
    for p in _split_paragraphs(body):
        clean = _para_acceptable(p)
        if clean and len(clean) >= 20:
            return clean
    return None


def derive_seo_description(body: str, lang: str) -> tuple[str | None, str | None]:
    para = first_paragraph(body, lang)
    if not para:
        return None, "no extractable lead paragraph"
    plain = strip_markdown(para)
    if not plain:
        return None, "lead paragraph empty after markdown strip"
    L = SEO_LIMITS[lang]
    out = cut_to_limit(plain, L["seo_desc_hard"], L["seo_desc_rec"], lang)
    if not out:
        return None, "trimmed description empty"
    return out, None


def process_file(path: Path, dry_run: bool) -> tuple[bool, list[str]]:
    notes: list[str] = []
    text = path.read_text(encoding="utf-8")
    post = frontmatter.loads(text)
    fm = post.metadata
    lang = fm.get("language")
    if lang not in SEO_LIMITS:
        return False, [f"skip: unknown language {lang!r}"]
    title = fm.get("title")
    if not isinstance(title, str):
        return False, ["skip: no title in front matter"]

    changed = False

    if "seo_title" not in fm:
        seo_t, todo = extract_seo_title(title, lang)
        if seo_t is not None:
            fm["seo_title"] = seo_t
            changed = True
            notes.append(f"+seo_title ({nfc_len(seo_t)}c): {seo_t!r}")
        elif todo is not None:
            notes.append(f"TODO seo_title: {todo}")

    if "seo_description" not in fm:
        seo_d, todo = derive_seo_description(post.content, lang)
        if seo_d is not None:
            fm["seo_description"] = seo_d
            changed = True
            notes.append(f"+seo_description ({nfc_len(seo_d)}c): {seo_d!r}")
        elif todo is not None:
            notes.append(f"TODO seo_description: {todo}")

    if changed and not dry_run:
        new = frontmatter.dumps(post, sort_keys=False)
        if not new.endswith("\n"):
            new += "\n"
        path.write_text(new, encoding="utf-8")

    return changed, notes


def iter_series_files(series_id: str) -> list[Path]:
    base = CONTENT_DIR / series_id
    if not base.is_dir():
        return []
    out: list[Path] = []
    for sub in ("ko", "en"):
        d = base / sub
        if d.is_dir():
            out.extend(sorted(d.glob("*.md")))
    return out


def all_series_ids() -> list[str]:
    cat = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    return [s["id"] for s in cat.get("series", []) if (CONTENT_DIR / s["id"]).is_dir()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series", nargs="*", help="series ids; omit with --all")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.all:
        series_ids = all_series_ids()
    elif args.series:
        series_ids = args.series
    else:
        ap.error("specify series ids or --all")

    total_changed = 0
    total_files = 0
    todos = 0
    for sid in series_ids:
        files = iter_series_files(sid)
        if not files:
            print(f"[skip] {sid}: no content dir")
            continue
        print(f"\n=== {sid} ({len(files)} files) ===")
        for f in files:
            total_files += 1
            ch, notes = process_file(f, args.dry_run)
            rel = f.relative_to(REPO_ROOT)
            if ch:
                total_changed += 1
            if notes:
                for n in notes:
                    if n.startswith("TODO"):
                        todos += 1
                    print(f"  {rel}: {n}")
    suffix = " (dry-run)" if args.dry_run else ""
    print(
        f"\nTotal: {total_changed}/{total_files} files changed, {todos} TODOs{suffix}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
