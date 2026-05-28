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

- How does a tutorial differ from a how-to guide or a reference page in the Diátaxis model?
- What makes a prerequisite list trustworthy instead of just a formality?
- How do you design verification checkpoints that actually keep readers on track?

## Why It Matters

A first success creates the will to keep learning. A first failure—especially one that could have been prevented by a single prerequisite line—destroys momentum and trust.

> Mental model: every tutorial step needs a checkpoint the reader can verify before moving on.

Tutorials differ from reference docs because they prioritize momentum and small wins over completeness. Each step should reveal visible proof of progress and include a recovery path for the most likely failure.

## Key Terms

- **tutorial**: A learning-oriented post where the reader builds something step by step.
- **prerequisite**: A precondition that must be true before the first step begins.
- **small win**: A visible proof of progress at the end of a step.
- **recovery**: A short note explaining what to do when a step fails.
- **next step**: A pointer to what to learn after the tutorial succeeds.

## Before/After

**Before**: "Let us learn about FastAPI." — a lecture with no runnable path.

**After**: "Run Hello World in five minutes." — a tutorial with clear checkpoints.

## Tutorial vs How-to vs Reference

Before writing a tutorial, confirm that a tutorial is actually what the reader needs. The Diátaxis framework separates content into four types, and confusing them produces a hybrid that serves none well.

| Dimension | Tutorial | How-to Guide | Reference |
| --- | --- | --- | --- |
| **Goal** | Learning through doing | Solving a specific problem | Looking up precise facts |
| **Reader state** | Beginner, no prior context | Has context, needs a recipe | Knows what to look for |
| **Structure** | Sequential steps, no skipping | Steps can be entered mid-way | Alphabetical or categorical |
| **Tone** | Encouraging, patient | Direct, practical | Neutral, complete |
| **Success metric** | Reader built something | Problem is solved | Fact is found quickly |
| **Example** | "Build your first API" | "Add auth to an existing API" | "`HTTPBearer` class reference" |

If the reader already has a working project and wants to add one feature, write a how-to. If they need to look up a function signature, write reference docs. Tutorials are for the blank-slate moment when nothing exists yet.

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

### Four types of verification checkpoints

Not every step produces terminal output. Here are four checkpoint patterns that work for different situations.

| Checkpoint Type | When to Use | Example |
| --- | --- | --- |
| **Terminal output** | CLI commands | `Uvicorn running on http://...` |
| **HTTP response** | API or web server steps | `curl localhost:8000` → `{"hello":"world"}` |
| **File existence** | Code generation or config steps | `ls main.py` → file appears |
| **Assertion** | Logic verification | `python3 -c "assert 1+1 == 2"` |

Each type tells the reader: "If you see this, you are on track. If you do not, stop and fix before continuing."

### Progressive code: show the journey, not just the destination

Tutorials that dump a complete file and say "run this" miss the point. Readers learn more when they see code grow across steps.

**Step 1 — Minimal version:**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}
```

**Step 2 — Add a parameter:**

```python
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}"}
```

**Step 3 — Add validation:**

```python
from pydantic import BaseModel

class GreetRequest(BaseModel):
    name: str
    language: str = "en"

@app.post("/greet")
def greet_post(req: GreetRequest):
    if req.language == "en":
        return {"message": f"Hello, {req.name}"}
    return {"message": f"Bonjour, {req.name}"}
```

Each step adds exactly one concept. The reader verifies after each addition, so when something breaks they know exactly which change caused it.

## Tutorial structure template

Below is a template showing how to organize a tutorial with proper prerequisites, steps, and recovery.

```markdown
# Tutorial: [Goal in imperative form]

## Prerequisites

- Python 3.11+ installed (`python3 --version`)
- pip available (`pip --version`)
- No prior project setup needed

## Step 1 — [Action]

[One paragraph of context—why this step exists.]

[Code block]

**Checkpoint:** [What the reader should see]

**If it fails:** [One-line recovery]

## Step 2 — [Action]

...

## Step 3 — [Action]

...

## What You Built

[One paragraph summarizing the result]

## Next Steps

- [Link to the next logical tutorial]
- [Link to related how-to guide]
```

The pattern is: context → action → proof → recovery. Repeating this rhythm across every step makes the tutorial predictable and scannable.

## Hands-on: A Five Minute Tutorial

### Step 1 — Prerequisites

```bash
python3 --version  # 3.11 or newer
```

**If it fails:** Install Python 3.11+ from [python.org](https://python.org) or use `pyenv install 3.11`.

### Step 2 — Install

```bash
pip install "fastapi[standard]"
```

**Checkpoint:** `pip show fastapi` prints version info without errors.

### Step 3 — Code

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}
```

Save as `main.py`.

### Step 4 — Run

```bash
fastapi dev main.py
```

**Checkpoint:** Terminal shows `Uvicorn running on http://127.0.0.1:8000`.

**If it fails:** Check that you saved `main.py` in the current directory and that the virtual environment is activated.

### Step 5 — Verify

```bash
curl http://127.0.0.1:8000
```

**Expected output:**

```text
{"hello":"world"}
```

## What to Notice in This Code

- Prerequisites go first so the reader does not start and fail mid-way.
- Commands are ordered—each builds on the previous step.
- The result is stated explicitly so the reader can compare their screen against it.
- Recovery notes appear inline instead of at the end of the article.

## Five Common Mistakes

1. **No prerequisites.** The reader starts, hits a version mismatch at step 3, and blames the tutorial.
2. **Commands in the wrong order.** Running the server before creating the file produces a confusing error.
3. **No small win.** Without visible proof at each step, the reader does not know whether they are on track.
4. **No error recovery notes.** A single "command not found" without explanation sends the reader to search results.
5. **No next step.** The tutorial ends abruptly and the reader does not know where to go.

## How This Shows Up in Production

Great libraries finish their official tutorial in under five minutes. FastAPI's first example is eight lines. Django's tutorial uses explicit checkpoints after every migration. Stripe's quickstart shows the API response inline. The pattern is consistent: small steps, visible proof, fast success.

## How a Senior Engineer Thinks

- Prerequisites are stated—never assumed.
- Small win arrives in three minutes or the tutorial is too long.
- Every likely error has a recovery line so readers stay self-sufficient.
- The next step is a small jump, not a cliff.
- A tutorial is learning-oriented—it is not a reference page with extra words.

## Checklist

- [ ] Prerequisites stated with version numbers and verification commands.
- [ ] Five steps or fewer to first success.
- [ ] One visible checkpoint per step.
- [ ] Recovery note for the most likely failure at each step.
- [ ] Next step shown at the end.

## Practice Problems

1. Write the definition of *tutorial* in one line.
2. Write the meaning of *small win* in one line.
3. Write an example of *recovery* in one line.

## Answering the Opening Questions

- **How does a tutorial differ from a how-to guide or a reference page in the Diátaxis model?**
  A tutorial is learning-oriented: the reader follows sequential steps to build something from nothing, gaining confidence through doing. How-to guides solve a specific problem for readers who already have context. References provide lookup for precise facts. Mixing these modes confuses the reader's expectations and makes the content serve none well.
- **What makes a prerequisite list trustworthy instead of just a formality?**
  Each prerequisite includes a verification command (`python3 --version`, `pip show fastapi`) so the reader can confirm it before starting. Version numbers are explicit. If a prerequisite is missing, the reader finds out at line 1 instead of failing mysteriously at step 4.
- **How do you design verification checkpoints that actually keep readers on track?**
  Match the checkpoint type to the step: terminal output for CLI commands, HTTP responses for server steps, file existence for generation steps, assertions for logic. State the expected result explicitly so the reader can compare. Include a one-line recovery for the most common failure mode.

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
