"""Tests for P2 functions: transform_for_hashnode, copyright helpers, check_public_assets."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _transform import (
    append_copyright,
    make_copyright_comment,
    transform_for_hashnode,
    transform_for_tistory,
)


# --- transform_for_hashnode ---


def test_hashnode_strips_front_matter():
    text = "---\ntitle: Test\n---\n# Hello\nBody\n"
    result = transform_for_hashnode(text)
    assert "---" not in result
    assert "# Hello" in result


def test_hashnode_strips_ebook_only():
    text = "Before\n<!-- ebook-only:start -->\nebook stuff\n<!-- ebook-only:end -->\nAfter\n"
    result = transform_for_hashnode(text)
    assert "ebook stuff" not in result
    assert "Before" in result
    assert "After" in result


def test_hashnode_keeps_blog_only_body():
    text = "Before\n<!-- blog-only:start -->\nblog content\n<!-- blog-only:end -->\nAfter\n"
    result = transform_for_hashnode(text)
    assert "blog content" in result
    assert "blog-only:start" not in result


def test_hashnode_strips_toc_markers():
    text = "Before\n<!-- toc:begin -->\n- Item 1\n- Item 2\n<!-- toc:end -->\nAfter\n"
    result = transform_for_hashnode(text)
    assert "- Item 1" in result
    assert "toc:begin" not in result
    assert "toc:end" not in result


def test_hashnode_keeps_tags_line():
    text = "Body\n\nTags: Azure, Functions, Serverless\n"
    result = transform_for_hashnode(text)
    assert "Tags: Azure, Functions, Serverless" in result


def test_hashnode_matches_tistory_transform():
    """Hashnode and Tistory should produce identical output for the same input."""
    text = "---\ntitle: Test\n---\n# Hello\n<!-- ebook-only:start -->\nhidden\n<!-- ebook-only:end -->\n<!-- blog-only:start -->\nvisible\n<!-- blog-only:end -->\n<!-- toc:begin -->\n- TOC\n<!-- toc:end -->\nBody\n\nTags: A, B\n"
    assert transform_for_hashnode(text) == transform_for_tistory(text)


# --- Copyright helpers ---


def test_make_copyright_comment():
    result = make_copyright_comment("YeongseonBooks", "2026", "all-rights-reserved")
    assert result == "<!-- \u00a9 2026 YeongseonBooks. All Rights Reserved. -->"


def test_make_copyright_comment_html_flag():
    # html flag should not change the format (always HTML comment)
    result = make_copyright_comment(
        "YeongseonBooks", "2026", "all-rights-reserved", html=True
    )
    assert "<!--" in result


def test_append_copyright_adds_notice():
    body = "Some content\n"
    result = append_copyright(body, "YeongseonBooks", "2026", "all-rights-reserved")
    assert "\u00a9 2026 YeongseonBooks" in result
    assert result.endswith("-->\n")


def test_append_copyright_idempotent():
    body = "Content\n\n<!-- \u00a9 2026 YeongseonBooks. All Rights Reserved. -->\n"
    result = append_copyright(body, "YeongseonBooks", "2026", "all-rights-reserved")
    assert result.count("\u00a9 2026") == 1


# --- rewrite_public_asset_urls ---

from _transform import rewrite_public_asset_urls


def test_rewrite_public_asset_urls():
    text = "![diagram](../../../assets/azure-functions-101/01/01-1-arch.ko.png)\n"
    result = rewrite_public_asset_urls(text, "https://example.github.io/pub")
    assert (
        "https://example.github.io/pub/assets/azure-functions-101/01/01-1-arch.ko.png"
        in result
    )


def test_rewrite_skips_code_fence():
    text = "```\n![diagram](../../../assets/series/01/img.png)\n```\n"
    result = rewrite_public_asset_urls(text, "https://example.github.io/pub")
    assert "../../../assets/" in result  # should NOT be rewritten


# --- check_public_assets regression ---

import importlib


def _load_check_public_assets():
    """Import check_public_assets as a module."""
    spec = importlib.util.spec_from_file_location(
        "check_public_assets",
        Path(__file__).resolve().parent.parent / "scripts" / "check_public_assets.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_check_public_assets_wrong_host(tmp_path):
    """wrong-host asset URLs should be flagged."""
    mod = _load_check_public_assets()
    html = '<img src="https://evil.example.com/assets/series/01/img.png">'
    f = tmp_path / "test.html"
    f.write_text(html)
    errors: list[str] = []
    # Monkey-patch REPO_ROOT so relative display works
    orig = mod.REPO_ROOT
    mod.REPO_ROOT = tmp_path
    try:
        mod._check_file(f, "https://good.github.io/pub", errors, html=True)
    finally:
        mod.REPO_ROOT = orig
    assert any("wrong-host" in e for e in errors)


def test_check_public_assets_residual_local_path(tmp_path):
    """Residual ../../../assets/ paths in export Markdown should be flagged."""
    mod = _load_check_public_assets()
    md = "![img](../../../assets/series/01/img.png)\n"
    f = tmp_path / "test.md"
    f.write_text(md)
    errors: list[str] = []
    orig = mod.REPO_ROOT
    mod.REPO_ROOT = tmp_path
    try:
        mod._check_file(f, "https://good.github.io/pub", errors, html=False)
    finally:
        mod.REPO_ROOT = orig
    assert any("residual local path" in e for e in errors)


def test_check_public_assets_valid_ref(tmp_path):
    """Valid public URL with existing local file should produce no errors."""
    mod = _load_check_public_assets()
    base = "https://good.github.io/pub"
    # Create the expected local file
    asset = tmp_path / "assets" / "series" / "01" / "img.png"
    asset.parent.mkdir(parents=True)
    asset.write_bytes(b"PNG")
    html = f'<img src="{base}/assets/series/01/img.png">'
    f = tmp_path / "test.html"
    f.write_text(html)
    errors: list[str] = []
    orig = mod.REPO_ROOT
    mod.REPO_ROOT = tmp_path
    try:
        checked = mod._check_file(f, base, errors, html=True)
    finally:
        mod.REPO_ROOT = orig
    assert errors == []
    assert checked == 1


def test_check_public_assets_missing_file(tmp_path):
    """Public URL referencing non-existent local file should be flagged."""
    mod = _load_check_public_assets()
    base = "https://good.github.io/pub"
    html = f'<img src="{base}/assets/series/01/missing.png">'
    f = tmp_path / "test.html"
    f.write_text(html)
    errors: list[str] = []
    orig = mod.REPO_ROOT
    mod.REPO_ROOT = tmp_path
    try:
        mod._check_file(f, base, errors, html=True)
    finally:
        mod.REPO_ROOT = orig
    assert any("missing" in e for e in errors)
