"""Shared transformation helpers for content -> publishing channels.

Each publishing target (tistory, medium, mkdocs, ebook) has a different
combination of:
- blog-only / ebook-only block visibility
- bottom `Tags:` line visibility (Tistory keeps it visible; Medium surfaces
  via leading HTML comment; MkDocs and ebook drop it because tags are in
  the front matter)
- TOC marker visibility (`<!-- toc:begin -->` / `<!-- toc:end -->` are
  internal scaffolding for finalize-posts.py and never need to render)
- image path rewrites

Source posts (`content/<series>/{ko,en}/*.md`) are the canonical input;
this module never mutates them.

Conventions per PUBLISHING.md (the spec):
| Block / line   | Tistory | Medium | MkDocs   | eBook |
| -------------- | ------- | ------ | -------- | ----- |
| `blog-only`    | keep    | keep   | strip    | strip |
| `ebook-only`   | strip   | strip  | optional | keep  |
"""

from __future__ import annotations

import re
from collections.abc import Callable

BLOG_ONLY_RE = re.compile(
    r"<!--\s*blog-only:start\s*-->.*?<!--\s*blog-only:end\s*-->\s*\n?",
    re.DOTALL,
)
EBOOK_ONLY_RE = re.compile(
    r"<!--\s*ebook-only:start\s*-->.*?<!--\s*ebook-only:end\s*-->\s*\n?",
    re.DOTALL,
)
EBOOK_MARKERS_RE = re.compile(
    r"<!--\s*ebook-only:(?:start|end)\s*-->\s*\n?",
)
BLOG_MARKERS_RE = re.compile(
    r"<!--\s*blog-only:(?:start|end)\s*-->\s*\n?",
)
TOC_BEGIN_RE = re.compile(r"^<!--\s*toc:begin\s*-->\s*\n?", re.MULTILINE)
TOC_END_RE = re.compile(r"^<!--\s*toc:end\s*-->\s*\n?", re.MULTILINE)
TOC_BLOCK_RE = re.compile(
    r"\n*^---\s*\n+<!--\s*toc:begin\s*-->.*?<!--\s*toc:end\s*-->\s*\n?",
    re.DOTALL | re.MULTILINE,
)
TAGS_LINE_RE = re.compile(r"\n*^Tags:[^\n]*\n?\s*\Z", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1)


def strip_blog_only(text: str) -> str:
    return BLOG_ONLY_RE.sub("", text)


def strip_ebook_only(text: str) -> str:
    return EBOOK_ONLY_RE.sub("", text)


def strip_blog_only_markers_keep_body(text: str) -> str:
    return BLOG_MARKERS_RE.sub("", text)


def strip_ebook_only_markers_keep_body(text: str) -> str:
    return EBOOK_MARKERS_RE.sub("", text)


def strip_toc_markers(text: str) -> str:
    text = TOC_BEGIN_RE.sub("", text)
    text = TOC_END_RE.sub("", text)
    return text


def strip_toc_block(text: str) -> str:
    return TOC_BLOCK_RE.sub("\n", text)


def strip_bottom_tags_line(text: str) -> str:
    return TAGS_LINE_RE.sub("\n", text).rstrip() + "\n"


def rewrite_outside_fences(text: str, rewrite_line: Callable[[str], str]) -> str:
    """Apply `rewrite_line` only to lines outside fenced code blocks.

    Tracks the opening fence marker (backtick vs tilde) and its minimum
    length so that, e.g., a `~~~` line inside a ```` ``` ```` block does
    not accidentally close the fence.  The fence delimiter lines themselves
    are passed through unchanged.
    """
    out: list[str] = []
    fence_char: str | None = None
    fence_len: int = 0
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence_char is None:
            # Not inside a fence — check for opening.
            for ch in ('`', '~'):
                run = len(stripped) - len(stripped.lstrip(ch))
                if run >= 3:
                    fence_char = ch
                    fence_len = run
                    break
            if fence_char is not None:
                out.append(line)
                continue
            out.append(rewrite_line(line))
        else:
            # Inside a fence — check for matching close.
            run = len(stripped) - len(stripped.lstrip(fence_char))
            if run >= fence_len and stripped.rstrip() == fence_char * run:
                fence_char = None
                fence_len = 0
            out.append(line)
    return "".join(out)


def transform_for_mkdocs(text: str, include_ebook_blocks: bool = False) -> str:
    text = strip_blog_only(text)
    if include_ebook_blocks:
        text = strip_ebook_only_markers_keep_body(text)
    else:
        text = strip_ebook_only(text)
    text = strip_toc_block(text)
    text = strip_bottom_tags_line(text)
    return text


def transform_for_ebook(text: str) -> str:
    text = strip_front_matter(text)
    text = strip_blog_only(text)
    text = strip_ebook_only_markers_keep_body(text)
    text = strip_toc_block(text)
    text = strip_bottom_tags_line(text)
    return text


def transform_for_tistory(text: str) -> str:
    text = strip_front_matter(text)
    text = strip_ebook_only(text)
    text = strip_blog_only_markers_keep_body(text)
    text = strip_toc_markers(text)
    return text


def transform_for_hashnode(text: str) -> str:
    """Transform en/ source for Hashnode publishing.

    Identical to Tistory transform: strip front matter, strip ebook-only,
    keep blog-only body (markers removed), strip TOC markers (keep TOC body), keep Tags line.
    """
    text = strip_front_matter(text)
    text = strip_ebook_only(text)
    text = strip_blog_only_markers_keep_body(text)
    text = strip_toc_markers(text)
    return text

# --------------- Public Asset URL rewriting ---------------

ASSET_MD_IMAGE_RE = re.compile(
    r"(!\[[^\]]*\]\()(\.\.[\/]\.\.[\/]\.\.[\/]assets[\/])([^)]+)(\))"
)


def _rewrite_asset_line(line: str, asset_base_url: str) -> str:
    """Rewrite ``../../../assets/X`` image refs to public URLs in a single line."""
    base = asset_base_url.rstrip("/")

    def _repl(m: re.Match) -> str:
        prefix = m.group(1)   # ![alt](
        asset_rel = m.group(3)  # <series>/<NN>/<file>
        suffix = m.group(4)   # )
        return f"{prefix}{base}/assets/{asset_rel}{suffix}"

    return ASSET_MD_IMAGE_RE.sub(_repl, line)


def rewrite_public_asset_urls(text: str, asset_base_url: str) -> str:
    """Rewrite local asset image paths to public URLs, skipping code fences."""
    return rewrite_outside_fences(
        text,
        lambda line: _rewrite_asset_line(line, asset_base_url),
    )



# --------------- Copyright notice ---------------

def make_copyright_notice(
    holder: str,
    year: str,
    license_type: str,
    *,
    visible: bool = False,
    lang: str = "en",
) -> str:
    """Return a copyright notice as HTML comment or visible text.

    Args:
        holder: Copyright holder name (e.g. 'YeongseonBooks').
        year: Copyright year (e.g. '2026').
        license_type: License identifier (e.g. 'all-rights-reserved').
        visible: If True, return a visible Markdown line instead of HTML comment.
        lang: 'ko' for Korean notice, 'en' for English.
    """
    if visible:
        if lang == "ko":
            text = f"\u00a9 {year} \uc601\uc120\ubd81\uc2a4. \uc774 \uae00\uc758 \uc800\uc791\uad8c\uc740 \uc800\uc790\uc5d0\uac8c \uc788\uc2b5\ub2c8\ub2e4."
        else:
            text = f"\u00a9 {year} {holder}. All rights reserved."
        return f"---\n\n{text}"
    text = f"\u00a9 {year} {holder}. {license_type.replace('-', ' ').title()}."
    return f"<!-- {text} -->"


def make_copyright_comment(holder: str, year: str, license_type: str, *, html: bool = False) -> str:
    """Return a copyright notice as an HTML comment.

    .. deprecated:: Use :func:`make_copyright_notice` instead.
    """
    return make_copyright_notice(holder, year, license_type, visible=False, lang="en")


def append_copyright(
    body: str,
    holder: str,
    year: str,
    license_type: str,
    *,
    html: bool = False,
    visible: bool = False,
    lang: str = "en",
) -> str:
    """Append a copyright notice to the end of *body* if not already present."""
    notice = make_copyright_notice(
        holder, year, license_type, visible=visible, lang=lang,
    )
    if notice in body:
        return body
    return body.rstrip() + "\n\n" + notice + "\n"