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

When beginners hear *technical writing*, they often picture polish first: clean grammar, nice headings, maybe a few screenshots. In real engineering teams, the harder problem is direction. If the writer does not know who the reader is, what action should follow, and what counts as success, even elegant prose turns into a document nobody can execute.

Technical writing matters because it keeps working after the meeting ends. A README, runbook, tutorial, or migration note gets read by someone who still has to install, run, compare, debug, or decide something. That operational handoff is what separates it from everyday explanatory prose.

This is the first post in the Technical Writing 101 series. It establishes the reader-task-output-boundary frame that the rest of the series builds on.


![technical writing 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/01/01-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 1 flow overview*
> Technical writing succeeds when it changes what readers can do, not just what they know.

## Questions to Keep in Mind

- How does technical writing differ from general writing?
- Why must technical writing extend beyond explanation to reader action?
- What becomes clearer when you split a document's purpose into reader, task, outcome, and scope?

## Why It Matters

Technical writing tends to outlive the code it describes. A sentence you write today will influence someone's install, execution, judgment, or recovery work weeks or months from now. That long tail makes precision worth the upfront effort.

> Mental model: technical writing is not prose that lists information—it is prose that connects a reader's question to an answer, then turns that answer into an action.

## Key Terms

- **technical writing**: Prose that delivers technical information to enable action.
- **audience**: The reader—specifically, their role, knowledge, and goal.
- **task**: The job the reader needs to accomplish.
- **outcome**: The measurable result proving the task succeeded.
- **scope**: The boundary that separates what the document covers from what it does not.

## Before/After

**Before**: "Python is a great language."

**After**: "A beginner can run Hello World in five minutes."

## One Frame That Sharpens the Whole Paragraph

| Element | Weak version | Stronger version |
| --- | --- | --- |
| Reader | Developers | A junior backend engineer building a first FastAPI endpoint |
| Task | Environment setup | Create a virtual environment and install dependencies |
| Output | Success | `(.venv)` appears and `pip list` shows the package |
| Boundary | Python basics | Local setup only—not deployment, CI, or Docker |

This table matters because technical vagueness usually begins in the opening promise. If the reader is broad, the task widens, the output becomes invisible, and the post sounds friendly while remaining hard to execute. Filling in these four cells before writing a single paragraph often fixes the direction before the prose stage even begins.

## The Three-Layer Model

Technical writing is easier to structure when you think of it as three layers rather than a flat explanation.

### Layer 1: What (the goal)

State the outcome the reader will achieve. Use a verb phrase: "Create and activate a virtual environment."

### Layer 2: How (the steps)

Provide copy-paste commands and expected outputs at each step. The reader should never have to guess whether a step succeeded.

### Layer 3: Why (the reasoning)

Explain why this approach matters, how it differs from alternatives, and what goes wrong if skipped. Without this layer, readers can follow steps but cannot adapt them to new situations.

**Example — virtual environment:**

- **What**: A virtual environment isolates Python packages per project.
- **How**: `python3 -m venv .venv && source .venv/bin/activate`
- **Why**: Prevents global package conflicts and makes dependency lists reproducible.

## Writing Order

Most people start writing from the top down. Technical writing is more efficient in this order:

### Step 1 — Fix reader and goal

Before writing prose, write down the reader, prerequisite knowledge, goal, and non-goals. These four anchors prevent drift during the actual writing.

### Step 2 — Outline first

List only the title and H2 headings. If someone can understand the flow from headings alone, the structure works.

### Step 3 — Secure code examples

Before writing body prose, create working code examples. Verify they run. Capture their output.

### Step 4 — Fill the body

Expand the outline, place code, and write explanations. Each section should cover What, How, and Why.

### Step 5 — Validate

Ask a colleague to review, or find someone matching the target reader to test. Follow every command from scratch and note where they get stuck.

## Types of Technical Writing

Technical writing splits into types by purpose, reader, and format. Each type demands different style, maintenance frequency, and depth.

| Type | Purpose | Reader | Length | Key trait |
| --- | --- | --- | --- | --- |
| API reference | Function/class reference | Integration developers | Short, repetitive | Accuracy, completeness, searchability |
| Tutorial | Guided learning path | Beginners | Medium | Step-by-step, runnable examples, checkpoints |
| README | Project introduction | Contributors, users | Short | Quick start, install, example, license |
| Blog post | Experience sharing | Peer engineers | Medium–long | Story, troubleshooting, decision context |

The formats differ, but they share one rule: every type must enable the reader's next action. API docs enable a function call, tutorials enable a finished project, READMEs enable installation, blogs enable problem-solving.

## Five Traits of Good Technical Documents

Regardless of format, strong technical writing shares these traits.

### 1. The reader is specific

Not "developers" but "a junior backend engineer building a first FastAPI endpoint." The narrower the reader, the clearer the prerequisite knowledge, example difficulty, and terminology choices become.

### 2. Commands are executable

Copy-paste must work. Environment variables, versions, and paths must all be present. An example that cannot run does not teach—it frustrates.

### 3. Results are visible

Not "installation succeeds" but "the terminal shows `(.venv)` and `pip list` outputs the package." Without a visible checkpoint, readers cannot confidently proceed to the next step.

### 4. Scope is explicit

State what the document covers and what it does not. A non-goals line lets readers quickly judge whether the document answers their question.

### 5. Stale information is removed

Outdated versions, deprecated methods, and broken links erode trust. Either keep the document current or attach an archive warning at the top.

## Bad vs Good Sentence Patterns

The same content can differ enormously in clarity depending on sentence structure. Three common patterns:

**Pattern 1 — vague reader:**
- Bad: "This guide is for developers."
- Good: "This guide is for junior backend engineers learning Python for the first time."
- Why: A specific reader makes prerequisite knowledge, example difficulty, and omission boundaries clear.

**Pattern 2 — invisible result:**
- Bad: "Once installation completes, you are ready."
- Good: "Once installation completes, the terminal shows `(.venv)` and `pip show requests` prints the package metadata."
- Why: A visible result gives the reader confidence to proceed.

**Pattern 3 — non-executable command:**
- Bad: "Create a virtual environment."
- Good: "Run `python3 -m venv .venv` in your terminal."
- Why: A copy-paste-safe command turns explanation into action.

## Ten AI-Slop Phrases to Delete

Technical writing must be concrete and executable. These vague fillers should be replaced with specifics:

1. **"robust"** → specify which errors it handles
2. **"seamlessly"** → list the integration steps
3. **"powerful"** → enumerate the concrete capabilities
4. **"easily"** → state how many lines of code or steps
5. **"intuitive"** → point to the part that needs no explanation
6. **"simply"** → state the actual number of steps
7. **"leverage"** → say "use"
8. **"cutting-edge"** → give the version number and release date
9. **"innovative"** → describe the concrete difference from prior approaches
10. **"efficient"** → provide execution time, memory usage, or another metric

## Evaluation Criteria for Technical Writing

Technical documents can be evaluated against four criteria:

| Criterion | Question | How to verify |
| --- | --- | --- |
| Executability | Can the reader follow the commands exactly? | Copy-paste and run every command |
| Verifiability | Can the reader confirm success visually? | Check that result statements are concrete |
| Scope clarity | Is the boundary between covered and not-covered explicit? | Look for a non-goals statement |
| Maintainability | Can the document be kept current over time? | Verify links and code quarterly |

These criteria apply not only before publishing but also when requesting peer review or improving existing documentation.

## Document Lifecycle and Maintenance

Technical writing requires ongoing maintenance after publication. Code examples especially need re-verification whenever library versions change.

| Phase | Timeframe | Actions |
| --- | --- | --- |
| Post-publish | 0–1 week | Collect reader feedback, fix typos, fill missing examples |
| Stabilization | 1 week – 3 months | Re-verify code on major version updates, add troubleshooting from reader questions |
| Maintenance | 3–12 months | Quarterly link checks, quarterly code execution verification |
| Archive | 12+ months | Add archive warning at top, note the version the document targets |

## Collaboration Review Checklist

Before requesting a peer review on team documentation, verify these items:

- [ ] Followed all commands from scratch end-to-end
- [ ] All links are alive
- [ ] Code examples run on the current library version
- [ ] No typos
- [ ] Reader, prerequisite knowledge, goal, and non-goals are stated
- [ ] Title matches the actual content
- [ ] Sections follow a hierarchical structure (What → How → Why)

A document that passes this checklist saves the reviewer's time and raises feedback quality.

## Hands-on: One Technical Paragraph

### Step 1 — Pick the audience

Start by naming the audience: Python beginners.

### Step 2 — Pick the task

Narrow the task: create and activate a virtual environment.

### Step 3 — The commands

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4 — The result

State the visible result: the prompt now shows `(.venv)`.

### Step 5 — The next action

End with the next step: `pip install requests`.

## What to Notice in This Code

- The reader comes first.
- The commands are short and copy-paste safe.
- The result is visible to the naked eye.

## Common Mistake Correction Table

| Mistake | Why it hurts | Quick fix |
| --- | --- | --- |
| Reader omitted | Difficulty and terminology drift | Pin reader and prerequisites in one sentence at the top |
| Result not stated | Reader cannot confirm success | Attach one visible output per step |
| Scope too wide | Document grows long, completion rate drops | Declare non-goals upfront |
| No next step | Learning flow breaks | End with 2–3 links to the next document or exercise |

## Five Common Mistakes

1. **A vague audience.**
2. **Too much theory, not enough action.**
3. **Commands that are not copy-paste safe.**
4. **No visible result.**
5. **No next step.**

## How This Shows Up in Production

Internal company docs, open-source READMEs, conference talk slides, and incident postmortems are all technical writing. The format varies but the rule is constant: someone reads it and must do something afterward.

## How a Senior Engineer Thinks

- Save the reader's time above all.
- Commands must work as written.
- Results must be visible.
- Stale information gets deleted, not left to mislead.
- Links must be alive.

## Checklist

- [ ] The audience is named specifically
- [ ] The task fits in one sentence
- [ ] Every command runs as written
- [ ] Every step has a visible result

## Practice Problems

1. Write the definition of technical writing in one line.
2. Write the meaning of *audience* in one line.
3. Write the definition of *outcome* in one line.

## Wrap-up and Next Steps

Technical writing does not stop at explanation—it must enable immediate action. That requires a clear reader, a concrete task, executable commands, visible results, and a pointer to the next step. The next post covers how the same content changes when you write for a different reader.

## Answering the Opening Questions

- **How does technical writing differ from general writing?**
  Technical writing doesn't end at explanation—it's designed so readers can act immediately. Every section should move the reader toward a concrete outcome they can verify.

- **Why must technical writing extend beyond explanation to reader action?**
  Because it must save reader time: commands should actually execute, results should be visible, and the reader should be able to verify success without guessing.

- **What becomes clearer when you split a document's purpose into reader, task, outcome, and scope?**
  Defining each element upfront prevents the writing from drifting and makes scope boundaries explicit—you know what to include, what to exclude, and when to stop.

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
