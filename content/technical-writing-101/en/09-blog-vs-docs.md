---
series: technical-writing-101
episode: 9
title: "Technical Writing 101 (9/10): Blog vs Documentation"
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
  - Blog
  - Documentation
  - Diataxis
  - Beginner
seo_description: Separate blog posts from documentation by ownership, freshness, and canonical truth so teams do not mix the two jobs.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (9/10): Blog vs Documentation

A postmortem article can be excellent context and still be the wrong place to store today's official rollout steps. A reference page can be correct and still fail to explain why the team made a controversial design choice. Blogs and docs both help engineering teams, but they do different jobs.

Strong teams do not force one format to replace the other. They separate ownership, freshness rules, and publication goals, then connect the two with deliberate links.

This is post 9 in the Technical Writing 101 series. It distinguishes blogs from documentation by role, lifespan, and canonical ownership.

## Questions to Keep in Mind

- The four quadrants of *Diátaxis?
- The *lifespan* of blog vs docs?
- What *blogs* do well?

## Big Picture

![technical writing 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/09/09-01-concept-at-a-glance.en.png)

*technical writing 101 chapter 9 flow overview*

This picture places Blog vs Documentation inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Blog vs Documentation is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

When *kinds of writing* mix up, the *reader* gets *lost*.

> Mental model: blogs preserve context and interpretation, while docs preserve the current truth.

## Concept at a Glance

## Key Terms

- **Diátaxis**: A *four quadrant* documentation model.
- **lifecycle**: The *life cycle*.
- **freshness**: *How current* the content is.
- **canonical**: The *official source*.
- **archive**: *Storage* of older posts.

## Before/After

**Before**: A *blog post* gets cited as *official documentation*.

**After**: *Blogs* hold *experience*; *docs* hold *truth*.

## Separate ownership and freshness before channels

| Dimension | Blog | Documentation |
| --- | --- | --- |
| Main owner | Individual author or editorial team | Product or platform owner |
| Freshness rule | Accurate at the time of writing | Kept current as the source of truth |
| Reader expectation | Context, experience, interpretation | Procedure, policy, reference |
| Update style | Revised when needed | Updated alongside code or process changes |
| Link direction | Points readers to canonical docs | Links out to background and rationale |

The difference matters operationally more than stylistically. A deployment blog post can explain trade-offs well, while the official document must keep today's commands, version limits, and rollout order correct. Mixing those jobs usually hurts both.

## Hands-on: Mapping the Quadrants

### Step 1 — Tutorial

```python
tutorial = "First-time learning"
```

### Step 2 — How-to

```python
how_to = "Solving a specific problem"
```

### Step 3 — Reference

```python
reference = "API specification"
```

### Step 4 — Explanation

```python
explanation = "Why a design was chosen"
```

### Step 5 — Blog vs docs

```python
blog = "My experience and opinion"
docs = "The team's official truth"
```

## What to Notice in This Code

- *Blogs* hold *experience*.
- *Docs* hold *truth*.
- They split into *four quadrants*.

## Five Common Mistakes

1. **Citing a *blog* as *official docs*.**
2. **Letting the *docs* go *stale*.**
3. **Not stating the *version*.**
4. **No *archive* policy.**
5. **No *canonical* link.**

## How This Shows Up in Production

Engineering teams *separate* blogs from docs and *version control* the docs alongside the *code*.

## How a Senior Engineer Thinks

- *Blogs* capture *past decisions*.
- *Docs* are the *living truth*.
- Old posts go to the *archive*.
- The *canonical* source is in the *docs*.
- *Blogs* link to *docs*.

## Checklist

- [ ] *Four quadrant* mapping.
- [ ] *Freshness* shown.
- [ ] *Canonical* link.
- [ ] *Archive* policy.

## Practice Problems

1. Write the four quadrants of *Diátaxis* in one line.
2. Write the meaning of *canonical* in one line.
3. Write the definition of *freshness* in one line.

## Wrap-up and Next Steps

The next post is *Pre-publish Checklist*.

## Answering the Opening Questions

- **The four quadrants of *Diátaxis?**
  - The article treats Blog vs Documentation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The *lifespan* of blog vs docs?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What *blogs* do well?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
- **Blog vs Documentation (current)**
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [Diátaxis - Procida](https://diataxis.fr/)
- [Docs Like Code - Anne Gentle](https://www.docslikecode.com/)
- [Docs as Code - Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)
- [Stripe Engineering Blog](https://stripe.com/blog/engineering)

Tags: TechnicalWriting, Blog, Documentation, Diataxis, Beginner
