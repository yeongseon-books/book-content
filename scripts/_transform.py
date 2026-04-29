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

    Lines inside ``` or ~~~ fences are passed through unchanged. The fence
    delimiter lines themselves (the opening and closing ``` ) are also passed
    through. This protects example code in tutorials from accidental link
    rewriting (e.g. cross-series link rewrites or asset path rewrites should
    not silently mutate URL strings shown to readers as code).
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
        else:
            out.append(rewrite_line(line))
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
    return text
