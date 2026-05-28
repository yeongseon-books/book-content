---
series: technical-writing-101
episode: 10
title: "Technical Writing 101 (10/10): Pre-publish Checklist"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - TechnicalWriting
  - Checklist
  - Publishing
  - Quality
  - Beginner
seo_description: Use a repeatable pre-publish checklist for titles, links, code, visuals, and final verification before readers see the post.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (10/10): Pre-publish Checklist

The riskiest moment in writing is often the moment when the draft feels almost done. That is when broken links, stale commands, missing captions, and title typos get waved through as small details. Readers usually notice those details first.

A pre-publish pass is not perfectionism. It is a cost-control routine. One round of automated checks plus one round of human review can remove a surprising number of expensive fixes before the post reaches real readers.

This is the final post in the Technical Writing 101 series. It turns that last-pass review into a repeatable workflow for titles, links, code, visuals, and post-publish follow-up.


![technical writing 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/10/10-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 10 flow overview*
> A pre-publish pass is the difference between a fix that costs 24 hours (before readers see it) and a fix that costs a week (after they do).

## Questions to Keep in Mind

- Title* review?
- Link* validation?
- Code* execution?

## Why It Matters

A *fix after publish* is far more expensive than a *check before publish*.

> Mental model: the final pass is an operating routine for titles, links, code, visuals, and follow-up.

A pre-publish checklist is not perfectionism; it is cost control. One round of automated checks plus one round of human review can catch broken links, stale commands, missing captions, and edge cases before real readers encounter them.
## Key Terms

- **link rot**: A *broken link* over time.
- **smoke test**: A *basic functional check*.
- **canary read**: A *peer pre-review*.
- **post-mortem**: A *post-publish retrospective*.
- **errata**: *Typo corrections*.

## Before/After

**Before**: A *broken link* found right after publish.

**After**: The *checklist* passes before publish.

## Turn the checklist into a repeatable release routine

For a repository like this one, the final pass is stronger when it becomes a command sequence instead of a memory exercise.

```bash
python3 .sisyphus/medium/finalize-posts.py
bash .sisyphus/style/check-ko.sh content/technical-writing-101/ko
python3 scripts/check_frontmatter.py
python3 scripts/check_links.py
python3 scripts/check_article_structure.py
make check
```

**Expected output:**

```text
hard failures: 0
warnings: 0
```

Automation does not replace human review. After the commands pass, it is still worth rereading the title and first three paragraphs as if you were a first-time visitor. Readers often decide whether to trust the whole post from that narrow slice alone.

## Hands-on: A Five Step Review

### Step 1 — Title review

```python
title_ok = ["has a verb", "fits 55 chars", "uses reader words"]
```

### Step 2 — Link validation

```bash
python3 scripts/check_links.py
```

### Step 3 — Code execution

```bash
python3 -c "from m import add; assert add(2,3) == 5"
```

### Step 4 — Image check

```python
images = {"caption": True, "alt_text": True, "resolution": "2x"}
```

### Step 5 — Post-publish review

```python
post = ["fix typos within 24h", "reply to reader comments"]
```

## What to Notice in This Code

- The *title* fits *55 characters*.
- *Links* are *validated automatically*.
- The *code* really *runs*.

## Five Common Mistakes

1. **Letting *link rot* sit.**
2. ***Code* that does not run.**
3. **An *image* with no *alt text*.**
4. **A *typo* left in place.**
5. **No *post-mortem*.**

## How This Shows Up in Production

Engineering blog teams run *peer review*, *automated checks*, and *post-mortems* together.

## How a Senior Engineer Thinks

- The *checklist* is a *routine*.
- *Links* are validated *automatically*.
- *Code* runs *on copy paste*.
- Typos are fixed *within 24 hours*.
- The *post-mortem* feeds the *next post*.

## Checklist

- [ ] *Title* OK.
- [ ] *Link* validation passes.
- [ ] *Code* execution passes.
- [ ] *Image* check passes.

## Practice Problems

1. Write the meaning of *link rot* in one line.
2. Write the definition of *canary read* in one line.
3. Write an example of *errata* in one line.

## Wrap-up and Next Steps

This is the *final* post in *Technical Writing 101*. The next series covers *Open Source Contribution*.

## Answering the Opening Questions

- **What should you check last before hitting publish?**
  Title accuracy, all links working, code blocks executing correctly, images loading, metadata complete—these are the minimum. A single broken link or non-running code example undermines the entire piece's credibility.
- **Why should title, links, code, images, and post-publish response be treated as one routine?**
  They form a single quality chain: a misleading title attracts wrong readers, broken links strand them, non-working code frustrates them, missing images confuse them, and no post-publish monitoring means you never learn about these failures.
- **Why is post-publish fix cost far higher than pre-publish check cost?**
  Once published, wrong information propagates through shares, bookmarks, and search indexes. Corrections require announcements, redirects, and reputation recovery. Five minutes of pre-publish checking prevents days of post-publish damage control.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): Defining the Reader](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): Title and Structure](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): Explaining Concepts](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): Explaining Example Code](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): Using Figures and Tables](./06-using-figures-and-tables.md)
- [Technical Writing 101 (7/10): Writing the README](./07-writing-the-readme.md)
- [Technical Writing 101 (8/10): Writing Tutorials](./08-writing-tutorials.md)
- [Technical Writing 101 (9/10): Blog vs Documentation](./09-blog-vs-docs.md)
- **Pre-publish Checklist (current)**

<!-- toc:end -->

## References

- [Editorial Calendars - Trello Guide](https://blog.trello.com/editorial-calendar)
- [Hemingway Editor](https://hemingwayapp.com/)
- [Vale - Prose Linter](https://vale.sh/)
- [Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/)

Tags: TechnicalWriting, Checklist, Publishing, Quality, Beginner
