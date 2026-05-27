---
series: technical-writing-101
episode: 8
title: "Technical Writing 101 (8/10): Writing Tutorials"
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
  - Tutorial
  - Learning
  - HandsOn
  - Beginner
seo_description: Write tutorials with short verified steps, recovery notes, and a fast first success that keeps readers moving.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (8/10): Writing Tutorials

Writers often respond to uncertainty by adding more explanation. Tutorial readers usually need the opposite. They need a short path, clear checkpoints, and quick recovery when one step fails.

A tutorial earns trust by making success predictable. Each step should leave behind a visible proof, and each likely failure should have at least one short recovery note. That is what keeps a hands-on chapter from turning into a lecture transcript.

This is the 8th post in the Technical Writing 101 series. It turns tutorials into verified step-by-step paths instead of broad conceptual overviews.


![technical writing 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/08/08-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 8 flow overview*
> A tutorial step is only strong when it leaves behind a checkpoint the reader can verify before moving on.

## Questions to Keep in Mind

- Where a tutorial sits in *Diátaxis?
- Stating *prerequisites?
- Designing a *small win?

## Why It Matters

A *first success* creates the will to keep *learning*.

> Mental model: every tutorial step needs a checkpoint the reader can verify before moving on.

Tutorials differ from reference docs because they prioritize momentum and small wins over completeness. Each step should reveal visible proof of progress and include a recovery path for the most likely failure.
## Key Terms

- **tutorial**: A *learning* oriented post.
- **prerequisite**: A *pre-condition*.
- **small win**: A *small success*.
- **recovery**: An *error recovery* path.
- **next step**: The *next thing to learn*.

## Before/After

**Before**: "Let us learn about *FastAPI*." (lecture)

**After**: "*Run Hello World in five minutes*." (tutorial)

## Make every tutorial step behave like a test case

A tutorial is easier to trust when each step leaves behind a visible checkpoint. For a FastAPI hello-world, that can look like this.

```bash
cat > main.py <<'PY'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}
PY

fastapi dev main.py
```

**Expected output:**

```text
Uvicorn running on http://127.0.0.1:8000
```

Recovery notes matter too. If the reader sees `fastapi: command not found`, tell them to rerun `python3 -m pip install "fastapi[standard]"` and retry. That single line often keeps the tutorial self-contained instead of sending the reader into search results.

## Hands-on: A Five Minute Tutorial

### Step 1 — Prerequisites

```bash
python3 --version  # 3.11 or newer
```

### Step 2 — Install

```bash
pip install "fastapi[standard]"
```

### Step 3 — Code

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}
```

### Step 4 — Run

```bash
fastapi dev main.py
```

### Step 5 — Verify

```text
{"hello":"world"}
```

## What to Notice in This Code

- *Prerequisites* go *first*.
- *Commands* are *ordered*.
- The *result* is *stated*.

## Five Common Mistakes

1. **No *prerequisites*.**
2. ***Commands* in the wrong *order*.**
3. **No *small win*.**
4. **No *error recovery* notes.**
5. **No *next step*.**

## How This Shows Up in Production

Great libraries finish their *official tutorial* in *under five minutes*.

## How a Senior Engineer Thinks

- *Prerequisites* are *stated*.
- *Small win* arrives in *three minutes*.
- Every error has a *recovery* line.
- The *next step* is a *small jump*.
- A *tutorial* is *learning*, not *reference*.

## Checklist

- [ ] *Prerequisites* stated.
- [ ] *Five steps or fewer*.
- [ ] One *small win*.
- [ ] *Next step* shown.

## Practice Problems

1. Write the definition of *tutorial* in one line.
2. Write the meaning of *small win* in one line.
3. Write an example of *recovery* in one line.

## Wrap-up and Next Steps

The next post is *Blog vs Documentation*.

## Answering the Opening Questions

- **Where a tutorial sits in *Diátaxis?**
  - The article treats Writing Tutorials as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Stating *prerequisites?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Designing a *small win?**
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
- **Writing Tutorials (current)**
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [Diátaxis Framework](https://diataxis.fr/)
- [Django Tutorial Style](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Teach Tech with Tutorials - Write the Docs](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/)

Tags: TechnicalWriting, Tutorial, Learning, HandsOn, Beginner
