---
series: technical-writing-101
episode: 5
title: "Technical Writing 101 (5/10): Explaining Example Code"
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
  - Code
  - Examples
  - Walkthrough
  - Beginner
seo_description: Walk readers through example code with minimal snippets, callouts, runnable commands, and visible output.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (5/10): Explaining Example Code

Long code samples often look generous, but they are one of the fastest ways to lose a reader. If the post does not show where to focus, what to run, and what success looks like, the example becomes a copy-paste gamble instead of a teaching tool.

Good code walkthroughs are intentionally small. They isolate the interesting lines, pair them with a short callout, and close the loop with an actual command and visible output. That is what turns a snippet into a reusable learning step.

This is the 5th post in the Technical Writing 101 series. It shows how to choose a minimal example, explain it, and prove that it works.


![technical writing 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/05/05-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 5 flow overview*
> A snippet only teaches when the reader can isolate the interesting lines, understand them, and verify the result with one command.

## Questions to Keep in Mind

- Why do readers get lost even when code is included?
- In what order should minimal example, explanation lines, and expected output be arranged?
- When should you split between in-code comments and prose explanation?

## Why It Matters

A runnable example must reach the reader's hands to teach. Code that can only be read—not executed—is reference material at best, not a learning tool.

> Mental model: show the smallest runnable snippet, point at the key line, then prove the output.

## Key Terms

- **MWE**: A Minimal Working Example—the fewest lines that compile, run, and demonstrate the point.
- **callout**: A highlight line outside the code block that tells the reader where to look.
- **inline comment**: A comment inside the code, for single-line essentials only.
- **fixture**: Example data used to make the code runnable without external dependencies.
- **snippet**: A short excerpt, typically 3–10 lines, showing one idea.

## Before/After

**Before**: A 200-line code dump with no guidance on what matters.

**After**: An 8-line MWE with a 2-line callout, a run command, and expected output.

## Three Layers of Code Examples

Code examples serve different purposes at different scales. Choose the right layer for your goal.

### Layer 1: Snippet (3–5 lines)

**Purpose**: Syntax check, quick reference.

```python
from fastapi import FastAPI

app = FastAPI()
```

### Layer 2: MWE (10–20 lines)

**Purpose**: First success experience—the reader runs it and sees a result.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Run: uvicorn main:app --reload
```

### Layer 3: Production-like Example (50–100 lines)

**Purpose**: Show error handling, validation, logging—patterns that transfer to real systems.

```python
from fastapi import FastAPI, HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info(f"Fetching user {user_id}")
    
    if user_id < 0:
        logger.warning(f"Invalid user_id: {user_id}")
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    # In production, fetch from DB
    return {"user_id": user_id, "name": "Jimin"}
```

Most tutorial posts live in Layer 2. Reserve Layer 3 for "putting it all together" sections.

## A Better Walkthrough Gives Setup, Focus, and Proof

Here is a slightly more realistic example:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
def add(a: int, b: int) -> dict[str, int]:
    return {"result": a + b}
```

```bash
uvicorn main:app --reload
curl "http://127.0.0.1:8000/add?a=2&b=3"
```

**Expected output:**

```json
{"result":5}
```

The first line many readers need is not the function body. It is the route declaration and the verification command. One shows the entry point. The other proves that the example really works.

## Code Placement Strategies

Where you put the code depends on the article's goal.

### Strategy 1: Concept first, then code (Tutorial)

1. Concept definition
2. Analogy
3. **Code example**
4. Code explanation

**Best for**: Beginners learning a concept for the first time.

### Strategy 2: Code first, explanation later (Quick Start)

1. **Code example**
2. Run command
3. Verify output
4. Explain how it works

**Best for**: Experienced developers who want to run something immediately.

### Strategy 3: Problem–solution pattern (Troubleshooting)

1. Problem scenario
2. **Bad code example**
3. Explain the problem
4. **Good code example**
5. Explain the improvement

**Best for**: Preventing common mistakes or improving existing code.

## Five Principles for Writing Code Examples

### Principle 1: Start with an MWE

**Bad**: Pasting a 200-line project in one block.

**Good**: Core functionality in 8 lines:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**Why**: Shorter code means faster comprehension, faster execution, faster confirmation of success.

### Principle 2: Put the run command directly below

**Bad**: "Run this code." (No command.)

**Good**:

```bash
uvicorn main:app --reload
```

**Why**: Readers should never have to search for what to do next.

### Principle 3: Show expected output

**Bad**: (No output.)

**Good**:

```json
{"message": "Hello World"}
```

**Why**: Readers can immediately confirm their result is correct.

### Principle 4: Pin versions

**Bad**: "Install FastAPI."

**Good**:

```bash
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0
```

**Why**: The example still works six months later.

### Principle 5: Link to full code

**Bad**: (No link.)

**Good**: "Full source: [GitHub repo](https://github.com/example/fastapi-examples/blob/main/01-hello/main.py)."

**Why**: Readers who want to extend or debug have a complete reference.

## Inline Comments vs Prose Explanation

Code comments and surrounding prose serve different purposes. Mix them appropriately so the example is neither over-commented nor under-explained.

| Situation | Inline comment | Prose explanation | Example |
| --- | --- | --- | --- |
| One line is the key | Use | Skip | `result = a + b  # core operation` |
| Explaining overall flow | Skip (too long) | Use | "This function validates, queries, then responds." |
| Reader must edit one line | Use | Reinforce | `# TODO: insert your API key here` |
| Code is already obvious | Skip | Skip | `x = 1  # assigns 1 to x` (bad comment) |
| Explaining a trade-off | Skip (disrupts flow) | Use | "Using async here avoids blocking the event loop…" |

**Good combination:**

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")  # reject negative IDs
    return {"user_id": user_id, "name": "Jimin"}
```

**Prose explanation:**

"This endpoint takes `user_id` as a path parameter and validates it. Negative values return HTTP 400; valid values return the user as JSON."

## Progressive Disclosure: Simple to Complex

Dumping a complex example up front causes readers to quit at step one. Instead, build from a minimal working state and add features incrementally.

### Step 1: Hello World (verify the setup works)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**Run**: `uvicorn main:app --reload`

**Verify**: `curl http://127.0.0.1:8000/` → `{"message": "Hello World"}`

### Step 2: Add a path parameter

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

**Verify**: `curl http://127.0.0.1:8000/users/42` → `{"user_id": 42}`

### Step 3: Add validation

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    return {"user_id": user_id}
```

**Verify**: `curl http://127.0.0.1:8000/users/-1` → HTTP 400 error

### Step 4: Database connection (preview for next post)

"So far we returned hard-coded values. The next article shows how to query a real SQLite database."

**Effect**: Readers confirm success at each stage, build confidence, and transition naturally to the next layer of complexity.

## MWE Package Structure

For reproducibility, package your example as a small directory:

```text
example/
  main.py
  requirements.txt
  README-snippet.md
```

- `main.py`: Core code, 20 lines or fewer.
- `requirements.txt`: Pinned versions.
- `README-snippet.md`: Run command + expected output.

## Code Explanation Block Standard

Every code walkthrough should follow this sequence:

1. Code block
2. Run command
3. Expected output
4. Recovery hint (what to do if it fails)

```bash
pip install fastapi==0.115.0 "uvicorn[standard]==0.32.0"
uvicorn main:app --reload
```

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

Recovery hint: If you see `ModuleNotFoundError`, activate your virtual environment and reinstall.

## Bad vs Good Code Explanations

| Aspect | Bad | Good |
| --- | --- | --- |
| Code length | 200-line full dump | 10–20 focused lines |
| Version info | Missing | Package versions pinned |
| Result verification | Missing | Expected output shown |
| Extension path | Missing | Link to full repository |

## Hands-on: One Example

### Step 1 — Minimal code

```python
def add(a, b):
    return a + b
```

### Step 2 — Callout

Add the callout in prose outside the snippet: this function takes two numbers and returns their sum.

### Step 3 — Run

```bash
python3 -c "from m import add; print(add(2, 3))"
```

### Step 4 — Output

```text
5
```

### Step 5 — Link the full code

Link the full code separately: `https://github.com/example/repo/blob/main/m.py`.

## What to Notice in This Code

- The code is minimal.
- The comment sits outside the snippet.
- The output is visible.

## Five Common Mistakes

1. **Code that is too long.** Keep MWEs under 20 lines.
2. **Too many comments.** If every line has a comment, none stand out.
3. **No output shown.** Readers cannot verify success.
4. **No version noted.** The example breaks silently after an upgrade.
5. **A snippet that breaks on copy-paste.** Test it yourself before publishing.

## How This Shows Up in Production

Open-source README "Quick Start" sections nearly always follow the MWE-plus-output pattern. It works because readers confirm success in under 60 seconds.

## How a Senior Engineer Thinks

- The code is minimal.
- The comment lives outside.
- The output is real.
- The version is pinned.
- The full code is a link.

## Review Checkpoints

Before publishing, verify:

- Can a reader copy just the code block and run it?
- Does the prose explanation point to the key line?
- Does the shown output match an actual execution?

## Checklist

- [ ] An MWE of ten lines or fewer.
- [ ] A callout of one or two lines.
- [ ] Output is shown.
- [ ] Version is noted.
- [ ] Run command is directly below the code.

## Practice Problems

1. Write the meaning of *MWE* in one line.
2. Write the definition of *callout* in one line.
3. Write an example of a *fixture* in one line.

## Wrap-up and Next Steps

The next post is *Using Figures and Tables*—how to replace slow text explanations with diagrams and comparison tables.

## Answering the Opening Questions

- **Why do readers get lost even when code is included?**
  Without marking what's core, what to execute, and what output is normal, code becomes an obstacle rather than explanation.
- **In what order should minimal example, explanation lines, and expected output be arranged?**
  Code → run command → expected output → explanation lines. This lets readers execute and verify first, then understand—matching how practitioners actually learn.
- **When should you split between in-code comments and prose explanation?**
  Single-line essentials go in inline comments; overall flow and trade-offs go in surrounding prose. This prevents code blocks from becoming walls of comments while keeping context accessible.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): Defining the Reader](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): Title and Structure](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): Explaining Concepts](./04-explaining-concepts.md)
- **Explaining Example Code (current)**
- Using Figures and Tables (upcoming)
- Writing the README (upcoming)
- Writing Tutorials (upcoming)
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [The Art of Readable Code - Boswell & Foucher](https://www.oreilly.com/library/view/the-art-of/9781449318482/)
- [Stack Overflow MCVE Guide](https://stackoverflow.com/help/minimal-reproducible-example)
- [Python Tutorial Style Guide](https://docs.python.org/3/tutorial/index.html)
- [Diátaxis Framework - Code Examples](https://diataxis.fr/)

Tags: TechnicalWriting, Code, Examples, Walkthrough, Beginner
