---
series: technical-writing-101
episode: 2
title: "Technical Writing 101 (2/10): Defining the Reader"
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
  - Audience
  - Persona
  - Writing
  - Beginner
seo_description: Define the reader with persona, prior knowledge, goal, and non-goal so a technical post stays narrow and useful.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (2/10): Defining the Reader

The same FastAPI example can be a friendly introduction for a junior engineer and a useless wall of text for the on-call engineer trying to restore service. The writing is not necessarily wrong. The target moved.

Once the reader is blurry, everything else drifts with it: how much background to include, which terms need explanation, how hard the example can be, and what the post should deliberately leave out. A concrete reader makes those decisions faster.

This is the 2nd post in the Technical Writing 101 series. Here we turn the reader into a working model with persona, prior knowledge, goal, and non-goal.


![technical writing 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/02/02-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 2 flow overview*
> When the reader is blurry, everything else—depth, vocabulary, scope—drifts with it.

## Questions to Keep in Mind

- Building a *persona?
- Mapping *prior knowledge?
- Aligning the *goal?

## Why It Matters

A blurry *reader* leads to blurry *sentences*.

> Mental model: once one reader becomes concrete, scope and vocabulary stop drifting.

A persona is not a demographic profile; it is a decision boundary. It answers how much background to include, which terms need explanation, how hard examples can be, and what the post should deliberately skip.
## Key Terms

- **persona**: A *model of the reader*.
- **prerequisite**: *Prior knowledge*.
- **goal**: *What the reader does next*.
- **scope**: What the post *covers*.
- **non-goal**: What the post *does not cover*.

## Before/After

**Before**: "A post for *developers*."

**After**: "A post for a *first-year Python* engineer learning *FastAPI*."

## The same feature changes shape for different readers

| Reader | Already knows | Needs right now | Should be left out |
| --- | --- | --- | --- |
| Beginner | Python syntax, `pip` | A first FastAPI endpoint | Deployment strategy, performance tuning |
| Reviewer | API basics | Missing prerequisites in the draft | Full install walkthrough |
| On-call engineer | Production environment | Triage steps and logs | Refresher on beginner concepts |

The same `/health` endpoint example serves different purposes for each row. That is why a persona is not decorative UX language. It is an editing boundary for depth, vocabulary, and scope.

## Hands-on: A Persona Card

### Step 1 — Name and role

```python
persona = {"name": "Jimin", "role": "First-year Python backend"}
```

### Step 2 — Prior knowledge

```python
knows = ["variables", "functions", "git basics"]
```

### Step 3 — Gaps

```python
unknown = ["async", "type hints"]
```

### Step 4 — Goal

Write the goal as a concrete next action: ship the first FastAPI endpoint.

### Step 5 — Non-goal

```python
non_goal = ["deployment", "DB migrations"]
```

## What to Notice in This Code

- The persona has a *name*.
- The persona has *gaps*.
- The persona has *non-goals*.

## Five Common Mistakes

1. **Targeting *everyone*.**
2. **Skipping *prerequisites*.**
3. **Vague *goals*.**
4. **Missing *non-goals*.**
5. **Examples that are *too hard*.**

## How This Shows Up in Production

API references, user guides, and tutorials all split by *persona*.

## How a Senior Engineer Thinks

- The reader feels like *one person*.
- *Non-goals* shrink the post.
- Examples sit *inside* the prior knowledge.
- Goals are written as *verbs*.
- The *future you* in two weeks is also a reader.

## Checklist

- [ ] One *persona*.
- [ ] Three *prerequisites*.
- [ ] One *goal* line.
- [ ] At least one *non-goal*.

## Practice Problems

1. Write the definition of *persona* in one line.
2. Write the meaning of *non-goal* in one line.
3. Write an example of a *prerequisite* in one line.

## Wrap-up and Next Steps

The next post is *Title and Structure*.

## Answering the Opening Questions

- **Why does writing "for everyone" end up helping no one properly?**
  Targeting everyone means you can't decide explanation depth, terminology level, example difficulty, or non-goals. The result looks friendly but actually serves no one adequately.
- **Why do sentences sharpen when you build a persona?**
  A persona fixes your target reader as a clear reference point while writing. Every sentence aligns toward that reader—ambiguous phrasing becomes obvious when you ask "would my persona understand this?"
- **How does writing prerequisites and goals first shrink scope?**
  Listing non-goals alongside prerequisites clarifies what the document won't cover, enabling you to cut unnecessary explanations boldly.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- **Defining the Reader (current)**
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

- [The Persona Lifecycle - Pruitt & Adlin](https://www.elsevier.com/books/the-persona-lifecycle/pruitt/978-0-12-566251-2)
- [About Face - Cooper et al.](https://www.wiley.com/en-us/About+Face%3A+The+Essentials+of+Interaction+Design%2C+4th+Edition-p-9781118766576)
- [Nielsen Norman Group on Personas](https://www.nngroup.com/articles/persona/)
- [Writing for Developers - Karl Hughes](https://www.writingfordevelopers.com/)

Tags: TechnicalWriting, Audience, Persona, Writing, Beginner
