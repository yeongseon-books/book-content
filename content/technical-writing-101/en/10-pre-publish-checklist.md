---
series: technical-writing-101
episode: 10
title: Pre-publish Checklist
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

# Pre-publish Checklist

The riskiest moment in writing is often the moment when the draft feels almost done. That is when broken links, stale commands, missing captions, and title typos get waved through as small details. Readers usually notice those details first.

A pre-publish pass is not perfectionism. It is a cost-control routine. One round of automated checks plus one round of human review can remove a surprising number of expensive fixes before the post reaches real readers.

This is the final post in the Technical Writing 101 series. It turns that last-pass review into a repeatable workflow for titles, links, code, visuals, and post-publish follow-up.

## Questions this post answers

- *Title* review
- *Link* validation
- *Code* execution
- *Image* checks
- *Post-publish* review

## Why It Matters

A *fix after publish* is far more expensive than a *check before publish*.

> Mental model: the final pass is an operating routine for titles, links, code, visuals, and follow-up.

## Concept at a Glance

![Concept at a Glance](../../../assets/technical-writing-101/10/10-01-concept-at-a-glance.en.png)

*Concept at a Glance*
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

<!-- toc:begin -->
- [What Is Technical Writing](./01-what-is-technical-writing.md)
- [Defining the Reader](./02-defining-the-reader.md)
- [Title and Structure](./03-title-and-structure.md)
- [Explaining Concepts](./04-explaining-concepts.md)
- [Explaining Example Code](./05-explaining-example-code.md)
- [Using Figures and Tables](./06-using-figures-and-tables.md)
- [Writing the README](./07-writing-the-readme.md)
- [Writing Tutorials](./08-writing-tutorials.md)
- [Blog vs Documentation](./09-blog-vs-docs.md)
- **Pre-publish Checklist (current)**
<!-- toc:end -->

## References

- [Editorial Calendars - Trello Guide](https://blog.trello.com/editorial-calendar)
- [Hemingway Editor](https://hemingwayapp.com/)
- [Vale - Prose Linter](https://vale.sh/)
- [Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/)

Tags: TechnicalWriting, Checklist, Publishing, Quality, Beginner
