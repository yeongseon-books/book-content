#!/usr/bin/env python3
"""Crawl Tistory category pages and update ko front matter with published_to info."""

import html as html_module
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fetch_page(page_num: int) -> str:
    url = f"https://yeongseonchoe.tistory.com/category?page={page_num}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_posts(page_html: str) -> list[dict]:
    posts = []
    link_pattern = re.compile(
        r'<a\s+href="/(\d+)"\s+class="link_post"[^>]*'
        r'data-tiara-name="([^"]*)"',
        re.DOTALL,
    )
    date_pattern = re.compile(
        r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{1,2}):(\d{2})",
    )
    blocks = page_html.split('<div class="list_content">')
    for block in blocks[1:]:
        link_match = link_pattern.search(block)
        date_match = date_pattern.search(block)
        if link_match and date_match:
            post_id = link_match.group(1)
            title = html_module.unescape(link_match.group(2))
            year = date_match.group(1)
            month = date_match.group(2).zfill(2)
            day = date_match.group(3).zfill(2)
            posts.append(
                {
                    "id": post_id,
                    "title": title,
                    "url": f"https://yeongseonchoe.tistory.com/{post_id}",
                    "published_at": f"{year}-{month}-{day}",
                }
            )
    return posts


def norm_full(title: str) -> str:
    """Full normalization for exact match."""
    t = title.strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s*&\s*", " ", t)
    t = re.sub(r"\s*:\s*", ":", t)
    t = t.replace("\u2014", "-").replace("\u2013", "-")
    t = t.lower()
    return t


def norm_sub(title: str) -> str:
    """Normalize for subtitle-level matching (strip series prefix + episode)."""
    t = title.strip()
    t = re.sub(r"\s*&\s*", " ", t)
    t = t.replace("\u2014", "-").replace("\u2013", "-")
    # Remove (N/M) pattern
    t = re.sub(r"\s*\(\d+/\d+\)\s*", " ", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s*:\s*", ":", t)
    t = t.lower().strip()
    return t


def get_subtitle(title: str) -> str:
    """Get just the subtitle part (after first colon), normalized."""
    t = title.strip()
    t = t.replace("\u2014", "-").replace("\u2013", "-")
    # Remove (N/M) pattern
    t = re.sub(r"\s*\(\d+/\d+\)\s*", " ", t)
    t = re.sub(r"\s+", " ", t)
    parts = t.split(":", 1)
    if len(parts) == 2:
        return parts[1].strip().lower()
    return ""


def get_all_posts(max_pages: int = 27) -> list[dict]:
    all_posts = []
    for page in range(1, max_pages + 1):
        print(f"  Fetching page {page}/{max_pages}...")
        page_html = fetch_page(page)
        posts = parse_posts(page_html)
        if not posts:
            break
        all_posts.extend(posts)
        time.sleep(0.5)
    return all_posts


def get_ko_files() -> tuple[dict, dict, dict]:
    """Returns (exact_map, sub_map, subtitle_only_map).

    exact_map: norm_full(title) -> Path
    sub_map: norm_sub(title) -> Path  (with episode stripped)
    subtitle_only_map: subtitle_text -> Path  (just the part after colon)
    """
    exact_map = {}
    sub_map = {}
    subtitle_only_map = {}

    for md_file in sorted(ROOT.glob("content/*/ko/*.md")):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read(2000)
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        title_match = re.search(r'^title:\s*"(.*?)"\s*$', fm, re.MULTILINE)
        if not title_match:
            title_match = re.search(r"^title:\s*'(.*?)'\s*$", fm, re.MULTILINE)
        if not title_match:
            title_match = re.search(r"^title:\s*(.+?)\s*$", fm, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            exact_map[norm_full(title)] = md_file
            sub_map[norm_sub(title)] = md_file
            subtitle = get_subtitle(title)
            if subtitle:
                subtitle_only_map[subtitle] = md_file
    return exact_map, sub_map, subtitle_only_map


def update_frontmatter(file_path: Path, url: str, published_at: str) -> bool:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    fm_match = re.match(r"^(---\n)(.*?)(\n---)", content, re.DOTALL)
    if not fm_match:
        return False

    fm = fm_match.group(2)
    body = content[fm_match.end() :]

    if "published_to:" in fm and "tistory:" in fm:
        return False

    # Update status
    fm = re.sub(
        r"^status:\s*publish-ready\s*$", "status: published", fm, flags=re.MULTILINE
    )
    fm = re.sub(r"^status:\s*ready\s*$", "status: published", fm, flags=re.MULTILINE)

    # Add published_to after status line
    published_to_block = f"published_to:\n  tistory:\n    url: \"{url}\"\n    published_at: '{published_at}'"

    if "published_to:" not in fm:
        fm = re.sub(
            r"^(status:\s*published)\s*$",
            r"\1\n" + published_to_block,
            fm,
            flags=re.MULTILINE,
        )

    new_content = fm_match.group(1) + fm + fm_match.group(3) + body
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    print("=== Tistory Published Tracking ===\n")
    print("Step 1: Crawling Tistory category pages...")
    all_posts = get_all_posts()
    print(f"  Found {len(all_posts)} posts total.\n")

    print("Step 2: Building ko file title mapping...")
    exact_map, sub_map, subtitle_only_map = get_ko_files()
    print(
        f"  Exact: {len(exact_map)}, Sub: {len(sub_map)}, Subtitle-only: {len(subtitle_only_map)}\n"
    )

    print("Step 3: Matching and updating...")
    matched = 0
    unmatched = []
    match_methods = {"exact": 0, "sub": 0, "subtitle": 0}

    for post in all_posts:
        title = post["title"]
        file_path = None
        method = None

        # Pass 1: exact normalized match
        key = norm_full(title)
        if key in exact_map:
            file_path = exact_map[key]
            method = "exact"

        # Pass 2: subtitle-stripped match (handles & removal, space around colon)
        if not file_path:
            key = norm_sub(title)
            if key in sub_map:
                file_path = sub_map[key]
                method = "sub"

        # Pass 3: Tistory title IS the subtitle of a repo title
        # Normalize the full Tistory title as if it were a subtitle
        if not file_path:
            t = title.strip()
            t = t.replace("\u2014", "\u2014").replace("\u2013", "\u2013")
            t_norm = t.replace("\u2014", "-").replace("\u2013", "-")
            t_norm = re.sub(r"\s+", " ", t_norm).strip().lower()
            if t_norm in subtitle_only_map:
                file_path = subtitle_only_map[t_norm]
                method = "subtitle"

        if file_path:
            updated = update_frontmatter(file_path, post["url"], post["published_at"])
            if updated:
                matched += 1
            match_methods[method] = match_methods.get(method, 0) + 1
        else:
            unmatched.append(title)

    print(f"  Updated: {matched} files")
    print(f"  Match methods: {match_methods}")
    print(f"  Unmatched: {len(unmatched)} posts")
    if unmatched:
        print("\n  Unmatched titles:")
        for t in unmatched:
            print(f"    - {t}")


if __name__ == "__main__":
    main()
