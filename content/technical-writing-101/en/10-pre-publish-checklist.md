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

- What should you check last before hitting publish, and in what order?
- Why should title, links, code, images, and post-publish response be treated as one routine rather than separate concerns?
- Why is post-publish fix cost far higher than pre-publish check cost?

## Why It Matters

A fix after publish is far more expensive than a check before publish. Readers have already clicked broken links, copied stale commands, and formed first impressions that are expensive to reverse.

> Mental model: the final pass is an operating routine for titles, links, code, visuals, and follow-up.

A pre-publish checklist is not perfectionism; it is cost control. One round of automated checks plus one round of human review can catch broken links, stale commands, missing captions, and edge cases before real readers encounter them.

## Key Terms

- **link rot**: Links that break over time as external pages move or disappear.
- **smoke test**: A quick test of basic functionality before full verification.
- **canary read**: A peer reading the post before publish to catch blind spots.
- **post-mortem**: A retrospective after publish to capture what to improve next time.
- **errata**: A published correction notice for errors found after publish.

## Before/After

**Before**: A broken link found right after publish—readers already clicked it.

**After**: The checklist passes before publish—readers never see the broken state.

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

### The full checklist table

| Item | How to Check | Automatable? |
| --- | --- | --- |
| **Title review** | Under 55 chars, has a verb, uses reader language | Partial (length check) |
| **Link validation** | All internal/external links return 200 | Full (`check_links.py`) |
| **Code execution** | Every code block runs on copy-paste | Manual + unit tests |
| **Image check** | Caption present, alt text, 2x resolution | Full (`lint_captions.py`) |
| **Front matter** | status, targets, tags valid | Full (`check_frontmatter.py`) |
| **Structure** | TOC, references, tags in correct position | Full (`check_article_structure.py`) |
| **Style** | No AI slop, S1 rules pass | Partial (`check-ko.sh`) |
| **Peer review** | Logic flow, technical accuracy | Manual |
| **Post-publish** | Typo fixes within 24h, reader feedback | Manual |

Automate everything you can. Treat the manual items as a team routine with a fixed schedule.

## Automation tools worth knowing

### 1. markdownlint

Checks Markdown syntax: heading hierarchy, code block language tags, trailing whitespace.

```bash
npm install -g markdownlint-cli
markdownlint content/**/*.md
```

### 2. vale

Checks prose style and terminology consistency against custom rules.

```bash
brew install vale   # or pip install vale
vale content/technical-writing-101/en/
```

### 3. Link checker

Detects broken internal links and external 404s.

```bash
python3 scripts/check_links.py
```

### 4. Custom quality gates

This repository chains multiple checks into a single command:

```bash
make check          # hard failures block publish
make check-quality  # warnings for improvement
```

## The three-step final pass

Before hitting publish, run these three steps in order.

### Step 1 — Reread the title and first three paragraphs

Readers judge the whole post from this narrow slice. Check:

- Title under 55 characters with an active verb.
- First paragraph states the problem clearly.
- Second or third paragraph establishes what the reader will be able to do after reading.

### Step 2 — Execute every code block in a fresh environment

```bash
python3 -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
# Run each code block from the article
```

If any block fails, fix it before publishing. A single broken command destroys the reader's trust in the entire article.

### Step 3 — Check images on mobile viewport

Mobile traffic often exceeds 60% of total views. Verify:

- Images do not overflow the screen width.
- Tables are horizontally scrollable.
- Code blocks do not push content off-screen.

## Peer review request template

After automated checks pass, request peer review with a clear scope.

```markdown
## Review Request

### Purpose
This is episode 10 of Technical Writing 101, covering pre-publish checklists.

### Please check
- [ ] Logic flow: can the reader follow without backtracking?
- [ ] Technical accuracy: do commands and examples work?
- [ ] Example quality: is the code realistic and runnable?
- [ ] Captions: does every image have a visible caption?
- [ ] Tone: is the register consistent throughout?

### Automated checks
make check  # Pass

### Timeline
Review requested: 2026-05-21
Feedback hoped by: 2026-05-22
```

## Severity-based response after publish

Not every post-publish problem is equal. Use severity to decide response time.

| Severity | Example | Response Time | Action |
| --- | --- | --- | --- |
| **Critical** | Code does not run at all | Immediate | Unpublish, fix, republish |
| **Major** | Broken link, typo changes meaning | Within 1 hour | Fix in place, add correction notice |
| **Minor** | Whitespace issue, wording improvement | Within 24 hours | Fix silently |

### Correction notice template

```markdown
> **Correction** (2026-05-21 14:20): Fixed the install command in Step 3.
> The previous version used a deprecated flag. Thanks @username for reporting.
```

## Post-publish monitoring routine

The first 24 hours after publish matter most. Track these signals:

| Signal | Why It Matters | Tool |
| --- | --- | --- |
| Reader-reported typos | Direct quality signal | Comments, email |
| Search keywords driving traffic | Validates title choice | Google Search Console |
| High-exit sections | Identifies confusing parts | Google Analytics |
| Link click-through on code examples | Confirms readers follow along | Analytics events |

After one week, write a three-line retrospective:

```markdown
## Retrospective (2026-05-28)

- **Went well**: Code examples praised in 3 comments
- **Needs improvement**: Diagram explanation too brief (1 report)
- **Next post action**: Expand diagram captions
```

This retrospective becomes an input to the next article's quality, closing the feedback loop.

## CI/CD integration

For teams that publish from a Git repository, the checklist becomes a CI pipeline.

```yaml
name: Content Quality Check

on:
  pull_request:
    paths:
      - 'content/**/*.md'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run quality checks
        run: make check

      - name: Check links
        run: python3 scripts/check_links.py

      - name: Check front matter
        run: python3 scripts/check_frontmatter.py
```

When CI fails, the PR cannot merge. This enforces the checklist without relying on human discipline alone.

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

- The title fits 55 characters—short enough to display fully in search results and social shares.
- Links are validated automatically—no manual clicking required.
- The code really runs—every example is copy-paste safe.

## Five Common Mistakes

1. **Letting link rot sit.** External links break over months; schedule periodic checks.
2. **Code that does not run.** If you edited the surrounding text and forgot to retest the code block, readers will find it first.
3. **An image with no alt text.** Screen readers skip it; search engines cannot index it.
4. **A typo left in place.** One typo in the title is enough to make readers question the whole article.
5. **No post-mortem.** Without a retrospective, the same mistakes repeat in the next post.

## How This Shows Up in Production

Engineering blog teams run peer review, automated checks, and post-mortems together. Stripe's engineering blog uses CI to validate code examples before merge. The Cloudflare blog has an editorial calendar with review deadlines built in. The pattern is consistent: automation catches the mechanical errors, humans catch the logical ones, and retrospectives prevent repetition.

## How a Senior Engineer Thinks

- The checklist is a routine, not a one-time heroic effort.
- Links are validated automatically on every commit.
- Code runs on copy-paste—no `<placeholder>` substitution required.
- Typos are fixed within 24 hours with a correction notice.
- The post-mortem feeds the next post's quality improvement.

## Checklist

- [ ] Title under 55 characters with a verb.
- [ ] Link validation passes with zero failures.
- [ ] Code execution passes in a fresh environment.
- [ ] Image check passes (caption, alt text, resolution).
- [ ] Peer review completed before publish.

## Practice Problems

1. Write the meaning of *link rot* in one line.
2. Write the definition of *canary read* in one line.
3. Write an example of *errata* in one line.

## Answering the Opening Questions

- **What should you check last before hitting publish, and in what order?**
  Title accuracy, all links working, code blocks executing correctly, images loading with captions, metadata complete—in that order. A single broken link or non-running code example undermines the entire piece's credibility. The order moves from highest-visibility (title) to lowest-visibility (metadata).
- **Why should title, links, code, images, and post-publish response be treated as one routine rather than separate concerns?**
  They form a single quality chain: a misleading title attracts wrong readers, broken links strand them, non-working code frustrates them, missing images confuse them, and no post-publish monitoring means you never learn about these failures. Breaking the chain at any point degrades the reader's experience.
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
