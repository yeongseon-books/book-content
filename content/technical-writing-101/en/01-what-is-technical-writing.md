---
series: technical-writing-101
episode: 1
title: "Technical Writing 101 (1/10): What Is Technical Writing"
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
  - Writing
  - Documentation
  - Communication
  - Beginner
seo_description: Define technical writing with a reader-task-output model so engineering prose leads to action instead of vague explanation.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (1/10): What Is Technical Writing

When beginners hear *technical writing*, they often picture polish first: clean grammar, nice headings, maybe a few screenshots. In real engineering teams, the harder problem is direction. If the writer does not know who the reader is, what action should follow, and what counts as success, even elegant prose turns into a slow document.

Technical writing matters because it keeps working after the meeting ends. A README, runbook, tutorial, or migration note gets read by someone who still has to install, run, compare, debug, or decide something. That operational handoff is what separates it from everyday explanatory prose.

This is the first post in the Technical Writing 101 series. It establishes the reader-task-output-boundary frame that the rest of the series builds on.

## Questions to Keep in Mind

- A definition of *technical writing?
- The difference from *everyday* prose?
- The *three purposes?

## Big Picture

![technical writing 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/01/01-01-concept-at-a-glance.en.png)

*technical writing 101 chapter 1 flow overview*

This picture places What Is Technical Writing inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Technical writing succeeds when it changes what readers can do, not just what they know.

## Why It Matters

Writing tends to *outlive* the *code* it describes.

> Mental model: the post only works when a reader can turn the explanation into an action.

## Concept at a Glance

Technical writing differs from everyday prose because it must close the loop: reader → task → measurable outcome. That closure is what separates a document that stalls on confusion from one that drives action.
## Key Terms

- **technical writing**: Prose that *delivers technical information*.
- **audience**: The *reader*.
- **task**: A *job to do*.
- **outcome**: A *result*.
- **scope**: The *boundary*.

## Before/After

**Before**: "*Python* is a *great language*."

**After**: "A *beginner* can *run Hello World* in *five minutes*."

## One frame that sharpens the whole paragraph

| Element | Weak version | Stronger version |
| --- | --- | --- |
| Reader | Developers | A junior backend engineer building a first FastAPI endpoint |
| Task | Environment setup | Create a virtual environment and install dependencies |
| Output | Success | `(.venv)` appears and `pip list` shows the package |
| Boundary | Python basics | Local setup only, not deployment |

This table matters because technical vagueness usually begins in the opening promise. If the reader is broad, the task widens, the output becomes invisible, and the post starts to sound friendly while remaining hard to execute. Filling in these four cells before writing often fixes the paragraph before the prose stage even begins.

## Hands-on: One Technical Paragraph

### Step 1 — Pick the audience

```python
audience = "Python beginners"
```

### Step 2 — Pick the task

```python
task = "Create and activate a virtual environment"
```

### Step 3 — The commands

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4 — The result

```python
result = "(.venv) shows up in the prompt"
```

### Step 5 — The next action

```python
next_step = "pip install requests"
```

## What to Notice in This Code

- The *reader* comes *first*.
- The *commands* are *short*.
- The *result* is *visible*.

## Five Common Mistakes

1. **A *vague* audience.**
2. **Too much *theory*.**
3. **Commands that are *not copy paste safe*.**
4. **No *visible result*.**
5. **No *next step*.**

## How This Shows Up in Production

Internal company docs, open source READMEs, and conference talk slides are all *technical writing*.

## How a Senior Engineer Thinks

- Saves the *reader's time*.
- Commands work *as written*.
- Results are *visible*.
- Stale information is *deleted*.
- Links are *alive*.

## Checklist

- [ ] The *audience* is *named*.
- [ ] The *task* is *one line*.
- [ ] The *commands* run.
- [ ] The *result* is stated.

## Practice Problems

1. Write the definition of *technical writing* in one line.
2. Write the meaning of *audience* in one line.
3. Write the definition of *outcome* in one line.

## Wrap-up and Next Steps

The next post is *Defining the Reader*.

## Answering the Opening Questions

- **A definition of *technical writing?**
  - The article treats What Is Technical Writing as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The difference from *everyday* prose?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The *three purposes?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Technical Writing (current)**
- Defining the Reader (upcoming)
- Title and Structure (upcoming)
- Explaining Concepts (upcoming)
- Explaining Example Code (upcoming)
- Using Figures and Tables (upcoming)
- Writing the README (upcoming)
- Writing Tutorials (upcoming)
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [Docs for Developers - Bhatti et al.](https://docsfordevelopers.com/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [Write the Docs Community](https://www.writethedocs.org/)

Tags: TechnicalWriting, Writing, Documentation, Communication, Beginner
