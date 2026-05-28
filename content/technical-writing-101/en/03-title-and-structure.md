---
series: technical-writing-101
episode: 3
title: "Technical Writing 101 (3/10): Title and Structure"
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
  - Title
  - Structure
  - Outline
  - Beginner
seo_description: Design technical titles and post structure together so the title promise matches the reader's path through the article.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (3/10): Title and Structure

Some posts earn the click and lose the reader two scrolls later. Others contain useful material but hide it behind a vague title, so the right reader never opens them in the first place. Those failures look different, but they come from the same source: the title promised one thing while the structure delivered another.

A strong title is not marketing copy—it compresses the reader action and the payoff into one sentence. The structure is the route that gets the reader there with the least friction. That is why these two pieces should be designed together during the draft stage, not fixed separately at the end.

This is the 3rd post in the Technical Writing 101 series. It focuses on shaping titles, outlines, headings, and summaries as one system.


![technical writing 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/03/03-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 3 flow overview*
> A title makes the promise, the outline shows the map, the body delivers, and the wrap-up pushes the reader toward their next action.

## Questions to Keep in Mind

- Why must a good title and good structure always move together?
- How does a title become a promise, and how does structure deliver it?
- In what order should title, outline, body, and wrap-up interlock?

## Why It Matters

The title earns the click; the structure earns the time. If only one is good, the post is either discovered but abandoned, or completed but never found. Both must work together for the document to reach its reader and carry them to the end.

> Mental model: the title is a promise, the outline is a map, the body is the delivery, and the wrap-up pushes toward the next action.

## Key Terms

- **SEO title**: A search-friendly title that includes the technology name and a verb.
- **outline**: A draft table of contents—H2 headings only.
- **heading**: A heading level (H1, H2, H3) that signals document hierarchy.
- **lede**: The first paragraph that determines whether the reader stays.
- **TL;DR**: A summary for readers who cannot read the entire post.

## Before/After

**Before**: "FastAPI notes"

**After**: "Ship your first FastAPI endpoint in five minutes"

## Run a Scannability Test on the Outline

Compare these two skeletons:

```markdown
# FastAPI notes

## Overview
## Part 1
## Part 2
## Summary
```

```markdown
# Ship your first FastAPI endpoint in five minutes

## Why this matters
## Install
## Write the code
## Run and verify
## Common blockers
```

The second outline is stronger because the headings expose the route. The title promise continues into the H2s, the verification point is visible, and the likely blocker is named early. A simple test: if a reader can skim only the title and H2s and still predict their next action, the structure is working.

## Heading Scan Test

Before finishing a draft, extract all H2 headings and read them as a standalone list. Ask three questions:

1. What will the reader do?
2. In what order?
3. What is this document's scope?

If you cannot answer clearly, the H2 headings need to be more specific.

**Test pass:**

```markdown
# Ship your first FastAPI endpoint in five minutes

## Check Python environment
## Install FastAPI
## Write the first endpoint
## Run the local server
## Verify in the browser
## Next step: connect a database
```

**Test fail:**

```markdown
# FastAPI overview

## Introduction
## Features
## Installation
## Example
## Summary
```

The first set tells the reader exactly what they will do at each step. The second gives no prediction of concrete actions.

## Designing Title and Structure Together

Write the title and outline before prose. This prevents drift.

### Step 1: Define the target action

Write one sentence describing what the reader can do after reading.

**Example**: "Run and verify a FastAPI endpoint locally."

### Step 2: Draft the title

Convert the target action into a title.

**Example**: "Ship your first FastAPI endpoint in five minutes"

### Step 3: List H2 headings

Break the target action into steps as H2s.

```markdown
## Check environment
## Install
## Write code
## Run
## Verify
## Next step
```

### Step 4: Run the scan test

Read only the title and H2s. Can you predict the reader's action at each step?

### Step 5: Write the body

Once the outline passes the scan test, fill each H2.

## Five Title Formulas

### 1. Time-promise

"Do [goal] in N minutes"

**Example**: "Ship your first FastAPI endpoint in five minutes"

**Strength**: Reader knows the time investment upfront and the goal is concrete.

### 2. Problem-solution

"Fix [problem] with [method]"

**Example**: "Find FastAPI async bottlenecks with profiling"

**Strength**: Reader instantly judges whether their problem matches.

### 3. Comparison

"[A] vs [B]: when to use which"

**Example**: "Flask vs FastAPI: which to pick for a new project"

**Strength**: Attracts readers making a decision.

### 4. Checklist

"N things to check before [goal]"

**Example**: "7 things to verify before deploying FastAPI"

**Strength**: Predictable structure; reader finds missed items quickly.

### 5. Step-by-step

"From [start state] to [end state]"

**Example**: "From local dev to AWS Lambda: deploying FastAPI"

**Strength**: Reader sees both starting point and destination clearly.

## Four Title Mistakes and Fixes

### Mistake 1: Noun-only title

- Bad: "FastAPI introduction"
- Fix: "Ship your first FastAPI endpoint in five minutes"
- Why: A verb makes the reader's outcome explicit.

### Mistake 2: Scope too broad

- Bad: "Complete web development guide"
- Fix: "Build a local FastAPI REST API"
- Why: Narrow scope lets the reader judge relevance instantly.

### Mistake 3: Missing from search

- Bad: "Tips for a fast API"
- Fix: "Reduce FastAPI async endpoint response time"
- Why: Including the technology name raises search hit rate.

### Mistake 4: Title-body mismatch

- Bad: Title says "Getting started with FastAPI" but half the body compares Django
- Fix: Deliver exactly what the title promises
- Why: A reader who clicked the title expects that specific promise fulfilled.

## Heading Hierarchy Rules

### Rule 1: One H1 only

A document has one H1 (the title). Two H1s signal the document should be split.

### Rule 2: Never skip levels

Do not jump from H2 to H4. Follow H2 → H3 → H4 in order.

### Rule 3: Five or fewer H2s for beginner posts

Introductory posts work best with five or fewer H2 headings. More than that suggests splitting or nesting.

### Rule 4: Include a verb in headings

"## Install" is weaker than "## Install FastAPI." A verb makes the reader's action at that section explicit.

## Transition Sentence Patterns

When moving from one section to the next, a transition sentence keeps flow smooth.

### Pattern 1: Result preview

**Example**: "Follow the next steps and your first endpoint will be running in five minutes."

**Effect**: Reader knows what the next section delivers and stays motivated.

### Pattern 2: Completion gate

**Example**: "If installation completed successfully, you are ready to write your first endpoint."

**Effect**: Only readers who finished the previous step proceed—others know to go back.

### Pattern 3: Question hook

**Example**: "But how do you deploy this to production?"

**Effect**: Poses the reader's next question, then answers it in the following section.

## Flat vs Nested Structure

| Structure type | Strengths | Weaknesses | Best for |
| --- | --- | --- | --- |
| Flat (H2 only) | Fast scanning, clear steps | Hard to express complex topics | Tutorials, quick starts, checklists |
| Nested (H2 > H3 > H4) | Logical hierarchy | Reader loses position | References, long guides, concept docs |

**Flat example:**

```markdown
# Getting started with FastAPI

## Install
## Write first endpoint
## Run
## Verify
## Next step
```

**Nested example:**

```markdown
# Understanding FastAPI architecture

## Router layer
### Path parameters
### Query parameters
## Dependency injection layer
### Function dependencies
### Class dependencies
```

For beginner posts, flat structure is more effective—readers follow steps easily and see progress at a glance. For reference docs and deep dives, nested structure expresses concept hierarchy better.

## 15-Minute Draft Check Routine

Before writing body prose, run this routine to catch title-structure misalignment early:

1. Confirm the title has a verb
2. Read H2s alone—is the reader's path visible?
3. Place one success criterion sentence under each H2
4. Close the wrap-up with one next-action sentence

## Title Pattern Comparison

| Pattern | Weak example | Improved example |
| --- | --- | --- |
| Noun-only | FastAPI guide | Ship your first FastAPI endpoint in 10 minutes |
| Scope overload | Complete backend development guide | FastAPI local execution and verification checklist |
| Result missing | API design notes | Reduce input validation failures with FastAPI request models |

## Structure Quality Checklist

| Check item | Pass criterion |
| --- | --- |
| H1 singularity | Exactly one H1 in the document |
| H2 readability | H2s alone convey the full flow |
| Transition sentences | Next-action preview exists between sections |
| Wrap-up quality | Contains 3 key takeaways + 1 next step |
| Target reader | Reader stated in one sentence in the introduction |
| Executability | Commands or procedures are concrete |
| Verifiability | Outputs, states, or checkpoints are shown |
| Scope control | Non-goals or boundaries are stated |

## Hands-on: A Skeleton for One Post

### Step 1 — Title

- Title draft: `Ship your first FastAPI endpoint in five minutes`

### Step 2 — Outline

- Outline:
  - `Install`
  - `Code`
  - `Run`
  - `Verify`
  - `Next step`

### Step 3 — First paragraph

- Opening promise: `Hello World result in five minutes`

### Step 4 — Body headings

```markdown
## Install
## Code
## Run
```

### Step 5 — Summary

- Summary sentence: `Now you can ship your own endpoint`

## What to Notice in This Code

- The title has a verb—it promises an action.
- The outline has five items or fewer—no cognitive overload.
- The summary ends with an action—the reader knows what to do next.

## Five Common Mistakes

1. **A noun-only title.** "FastAPI guide" has no promise. "Ship your first FastAPI endpoint in 10 minutes" shows a verb, a result, and a time boundary.
2. **An outline too deep.** H3 and H4 in the initial outline overwhelm first-time readers. Start with H2s only; add depth in the body where needed.
3. **A long first paragraph.** Keep the lede to three lines or fewer. Readers decide in the first paragraph whether the post addresses their problem.
4. **No wrap-up.** Without a summary and next action, the reader finishes and asks "now what?" The post floats unresolved.
5. **Multiple H1 headings.** Search engines and Markdown renderers treat H1 as the document title. More than one dilutes priority and weakens SEO.

## How This Shows Up in Production

News articles use the inverted pyramid. Technical blogs ask for conclusion-first writing. Internal design docs start with the decision, then show evidence. All share the same principle: the title's promise and the structure's delivery must match.

## How a Senior Engineer Thinks

- The title is a promise—break it and lose the reader's trust.
- The outline is a map—if the map is confusing, the territory will not help.
- The summary points to an action—never leave the reader hanging.
- Paragraphs stay short—walls of text lose scanning readers.
- There is one H1—no exceptions.

## Checklist

- [ ] A verb in the title
- [ ] Five or fewer H2 outline items
- [ ] Three lines or fewer in the first paragraph
- [ ] A one-line summary with a next action

## Practice Problems

1. Write the definition of an SEO title in one line.
2. Write the meaning of *outline* in one line.
3. Write the meaning of *TL;DR* in one line.

## Wrap-up and Next Steps

A title is a promise. An outline is a map. The body delivers the promise along the map. The wrap-up pushes the reader to their next action. Designing all four together at the draft stage prevents the most common structural failures. The next post covers how to explain concepts clearly.

## Answering the Opening Questions

- **Why must a good title and good structure always move together?**
  The title promises a reader outcome; the structure delivers that promise step by step. A good title with blurry structure loses readers mid-way; good structure with a vague title never gets found in search. Design both as a set during the draft stage.

- **How does a title become a promise, and how does structure deliver it?**
  The title compresses the reader's destination into one sentence; structure arranges the shortest path to that destination via headings and paragraphs. As the flat vs. nested comparison showed, heading order and depth dramatically change the reader's time-to-destination.

- **In what order should title, outline, body, and wrap-up interlock?**
  The title makes the promise, the outline shows the path, the body explains along that path, and the wrap-up pushes the reader toward their next action. The 15-minute draft check routine and structure quality checklist keep this sequence from breaking.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): Defining the Reader](./02-defining-the-reader.md)
- **Title and Structure (current)**
- Explaining Concepts (upcoming)
- Explaining Example Code (upcoming)
- Using Figures and Tables (upcoming)
- Writing the README (upcoming)
- Writing Tutorials (upcoming)
- Blog vs Documentation (upcoming)
- Pre-publish Checklist (upcoming)

<!-- toc:end -->

## References

- [On Writing Well - Zinsser](https://www.harpercollins.com/products/on-writing-well-william-zinsser)
- [The Elements of Style - Strunk & White](https://www.bartleby.com/141/)
- [Inverted Pyramid - Nielsen Norman Group](https://www.nngroup.com/articles/inverted-pyramid/)
- [Google Search Central Title Best Practices](https://developers.google.com/search/docs/appearance/title-link)

Tags: TechnicalWriting, Title, Structure, Outline, Beginner
