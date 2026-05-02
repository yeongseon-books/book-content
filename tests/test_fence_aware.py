"""Regression tests for fence-aware line transforms.

Tests cover:
- Backtick fences (```)
- Tilde fences (~~~)
- Mixed delimiters (~~~ inside ```, and vice versa)
- Code samples containing asset-like paths
- replace_images, replace_links, split_code_segments, rewrite_outside_fences
"""

from __future__ import annotations

import sys
from pathlib import Path

# -- path setup ---------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / ".sisyphus" / "medium"))


# --------------- _transform.rewrite_outside_fences ---------------------------

from _transform import rewrite_outside_fences


def _upper(line: str) -> str:
    return line.upper()


def test_basic_backtick_fence():
    text = "outside\n```\ninside\n```\noutside\n"
    result = rewrite_outside_fences(text, _upper)
    lines = result.splitlines()
    assert lines[0] == "OUTSIDE"
    assert lines[2] == "inside"
    assert lines[4] == "OUTSIDE"


def test_basic_tilde_fence():
    text = "outside\n~~~\ninside\n~~~\noutside\n"
    result = rewrite_outside_fences(text, _upper)
    lines = result.splitlines()
    assert lines[0] == "OUTSIDE"
    assert lines[2] == "inside"
    assert lines[4] == "OUTSIDE"


def test_tilde_inside_backtick_not_close():
    """A ~~~ line inside a ``` block must NOT close the fence."""
    text = "outside\n```\n~~~\ninside\n~~~\nstill inside\n```\noutside\n"
    result = rewrite_outside_fences(text, _upper)
    lines = result.splitlines()
    assert lines[0] == "OUTSIDE"
    # lines 1-6 are inside the backtick fence
    assert lines[2] == "~~~"
    assert lines[3] == "inside"
    assert lines[4] == "~~~"
    assert lines[5] == "still inside"
    assert lines[7] == "OUTSIDE"


def test_backtick_inside_tilde_not_close():
    """A ``` line inside a ~~~ block must NOT close the fence."""
    text = "outside\n~~~\n```\ninside\n```\nstill inside\n~~~\noutside\n"
    result = rewrite_outside_fences(text, _upper)
    lines = result.splitlines()
    assert lines[0] == "OUTSIDE"
    assert lines[3] == "inside"
    assert lines[5] == "still inside"
    assert lines[7] == "OUTSIDE"


def test_longer_fence_close():
    """A ```` (4-backtick) fence can only be closed by >= 4 backticks."""
    text = "outside\n````\n```\ninside\n```\nstill inside\n````\noutside\n"
    result = rewrite_outside_fences(text, _upper)
    lines = result.splitlines()
    assert lines[0] == "OUTSIDE"
    assert lines[3] == "inside"
    assert lines[5] == "still inside"
    assert lines[7] == "OUTSIDE"


def test_asset_path_inside_code_block():
    """Asset-like paths inside fences must not be rewritten."""
    text = (
        "![img](../../../assets/s/01/pic.png)\n"
        "```\n"
        "![img](../../../assets/s/01/pic.png)\n"
        "```\n"
        "![img](../../../assets/s/01/pic.png)\n"
    )

    def mark(line: str) -> str:
        return line.replace("../../../assets/", "PUBLIC/")

    result = rewrite_outside_fences(text, mark)
    lines = result.splitlines()
    assert "PUBLIC/" in lines[0]
    assert "PUBLIC/" not in lines[2]  # inside fence
    assert "PUBLIC/" in lines[4]


# --------------- to-medium split_code_segments -------------------------------

# Import after path setup
from importlib import import_module

_to_medium = import_module("to-medium")
split_code_segments = _to_medium.split_code_segments


def test_split_backtick():
    text = "prose\n```python\ncode\n```\nprose"
    segs = split_code_segments(text)
    assert segs[0] == (False, "prose")
    assert segs[1][0] is True
    assert "code" in segs[1][1]
    assert segs[2] == (False, "prose")


def test_split_tilde():
    text = "prose\n~~~\ncode\n~~~\nprose"
    segs = split_code_segments(text)
    assert segs[0] == (False, "prose")
    assert segs[1][0] is True
    assert "code" in segs[1][1]
    assert segs[2] == (False, "prose")


def test_split_mixed_no_false_close():
    """~~~ inside ``` fence does not split."""
    text = "prose\n```\n~~~\ncode\n~~~\n```\nprose"
    segs = split_code_segments(text)
    assert segs[0] == (False, "prose")
    assert segs[1][0] is True
    assert "~~~" in segs[1][1]
    assert "code" in segs[1][1]
    assert segs[2] == (False, "prose")


# --------------- to-medium replace_images (integration) ----------------------

replace_images = _to_medium.replace_images
replace_links = _to_medium.replace_links


def test_replace_images_skips_code_block(tmp_path):
    """replace_images() must not rewrite asset paths inside fenced code."""
    # Set module globals for public mode
    _to_medium._asset_mode = "public"
    orig_base = _to_medium.ASSET_BASE_URL
    _to_medium.ASSET_BASE_URL = "https://example.io"
    try:
        src = tmp_path / "en" / "01-test.md"
        src.parent.mkdir(parents=True)
        src.touch()
        text = (
            "![a](../../../assets/s/01/a.png)\n"
            "```\n"
            "![b](../../../assets/s/01/b.png)\n"
            "```\n"
            "![c](../../../assets/s/01/c.png)\n"
        )
        result = replace_images(text, src)
        lines = result.splitlines()
        assert "example.io" in lines[0], "outside fence: should rewrite"
        assert "example.io" not in lines[2], "inside fence: must NOT rewrite"
        assert "example.io" in lines[4], "outside fence: should rewrite"
    finally:
        _to_medium._asset_mode = "public"
        _to_medium.ASSET_BASE_URL = orig_base


def test_replace_links_skips_code_block():
    """replace_links() must not rewrite relative links inside fenced code."""
    # Use a real file inside the repo so resolve_relative works
    src = REPO_ROOT / "content" / "azure-functions-101" / "en" / "01-why-serverless.md"
    text = (
        "[link](../ko/01-why-serverless.md)\n"
        "```\n"
        "[link](../ko/01-why-serverless.md)\n"
        "```\n"
        "[link](../ko/01-why-serverless.md)\n"
    )
    result = replace_links(text, src)
    lines = result.splitlines()
    # Outside fence: links should be rewritten (contain github.com)
    # Inside fence: links must stay as-is
    assert "github.com" in lines[0], "outside fence: should rewrite"
    assert "../ko/01-why-serverless.md" in lines[2], "inside fence: must NOT rewrite"
    assert "github.com" in lines[4], "outside fence: should rewrite"
