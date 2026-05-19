---
series: technical-writing-101
episode: 4
title: Explaining Concepts
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
  - Concept
  - Explanation
  - Analogy
  - Beginner
seo_description: Explain technical concepts with definition, analogy, counterexample, and worked example so first-time readers grasp the boundary.
last_reviewed: '2026-05-15'
---

# Explaining Concepts

The most common failure in concept writing is accuracy without traction. The definition may be technically correct, yet the reader still cannot predict where the concept applies, where it breaks, or how it should affect code and design decisions.

Useful concept writing needs more than a polished sentence. It needs a boundary. That usually means pairing a definition with an analogy, a counterexample, and a worked example so the reader can test the idea instead of just memorizing it.

This is post 4 in the Technical Writing 101 series. Here we build that four-part concept explanation pattern.

## Questions this post answers

- A *one line* definition
- Using an *analogy*
- Using a *counterexample*
- Using a *diagram*
- Building a *worked example*

## Why It Matters

If the *concept* stays blurry, everything after it is a *sandcastle*.

> Mental model: define the concept, mark the boundary, then prove it with an example.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/04/04-01-concept-at-a-glance.en.png)

*Concept at a Glance*
## Key Terms

- **definition**: A *one line definition*.
- **analogy**: An *analogy*.
- **counterexample**: A *counterexample*.
- **worked example**: An *example with the steps shown*.
- **misconception**: A *common mistake in understanding*.

## Before/After

**Before**: "*Async* means *running at the same time*." (Wrong.)

**After**: "*Async* means *doing other work while you wait*."

## The fastest way to test whether a definition works

This explanation is technically correct but still weak.

```text
A cache stores frequently used data.
```

It does not tell the reader what belongs in the cache, what should stay out, or where the boundary breaks. Adding a boundary and counterexample turns the concept into a decision tool.

```text
A cache stores answers that are expensive to fetch or compute again.
A large file read once during a migration is usually a poor cache candidate.
```

A strong concept explanation helps the reader classify the next example without asking you again. That is why edge cases and counterexamples often teach more than an expanded definition alone.

## Hands-on: One Concept Explained

### Step 1 — Definition

```python
definition = "A cache stores frequent answers ahead of time"
```

### Step 2 — Analogy

```python
analogy = "Side dishes you keep at the front of the fridge"
```

### Step 3 — Counterexample

```python
counterexample = "Data you read only once does not belong in a cache"
```

### Step 4 — Code example

```python
cache = {}
cache["user:1"] = {"name": "Jimin"}
```

### Step 5 — Common misconception

```python
misconception = "A cache can grow forever"
```

## What to Notice in This Code

- The *definition* is *one line*.
- The *analogy* is *everyday*.
- The *counterexample* draws the *boundary*.

## Five Common Mistakes

1. **A *long* definition.**
2. **A *stretched* analogy.**
3. **No *counterexample*.**
4. **A *huge* code example.**
5. **Skipping the *common misconception*.**

## How This Shows Up in Production

The best internal wiki pages always open with *definition*, *analogy*, *counterexample*, and *example*.

## How a Senior Engineer Thinks

- The *definition* is *one line*.
- The *analogy* sits in the *familiar zone*.
- The *counterexample* is the *boundary*.
- The *example* is *runnable*.
- The *misconception* is *broken first*.

## Checklist

- [ ] One line *definition*.
- [ ] One *analogy*.
- [ ] One *counterexample*.
- [ ] *Five lines or fewer* of example code.

## Practice Problems

1. Write the length of a *definition* in one line.
2. Write the meaning of *counterexample* in one line.
3. Write the definition of a *worked example* in one line.

## Wrap-up and Next Steps

The next post is *Explaining Example Code*.

<!-- toc:begin -->
- [What Is Technical Writing](./01-what-is-technical-writing.md)
- [Defining the Reader](./02-defining-the-reader.md)
- [Title and Structure](./03-title-and-structure.md)
- **Explaining Concepts (current)**
- Explaining Example Code (upcoming)
- Using Figures and Tables (upcoming)
- Writing the README (upcoming)
- Writing Tutorials (upcoming)
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)
<!-- toc:end -->

## References

- [Made to Stick - Heath Brothers](https://heathbrothers.com/books/made-to-stick/)
- [Explain Like I am Five - Reddit](https://www.reddit.com/r/explainlikeimfive/)
- [Refactoring UI - Adam Wathan](https://www.refactoringui.com/)
- [Mental Models - Farnam Street](https://fs.blog/mental-models/)

Tags: TechnicalWriting, Concept, Explanation, Analogy, Beginner
