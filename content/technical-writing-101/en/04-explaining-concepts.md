---
series: technical-writing-101
episode: 4
title: "Technical Writing 101 (4/10): Explaining Concepts"
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

# Technical Writing 101 (4/10): Explaining Concepts

The most common failure in concept writing is accuracy without traction. The definition may be technically correct, yet the reader still cannot predict where the concept applies, where it breaks, or how it should affect code and design decisions.

Useful concept writing needs more than a polished sentence. It needs a boundary. That usually means pairing a definition with an analogy, a counterexample, and a worked example so the reader can test the idea instead of just memorizing it.

This is the 4th post in the Technical Writing 101 series. Here we build that four-part concept explanation pattern.


![technical writing 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/04/04-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 4 flow overview*
> A concept without a boundary is just a fact to memorize; with a boundary, it becomes a tool to apply.

## Questions to Keep in Mind

- What should you show first to help a new reader understand a concept immediately?
- Why must analogies and counterexamples move together?
- Why doesn't a one-line definition make an explanation stick?

## Why It Matters

If the concept stays blurry, everything after it is a sandcastle. A mis-formed concept warps code, design, and operational decisions downstream—sometimes for months before anyone notices.

> Mental model: define the concept, mark the boundary, then prove it with an example.

## Key Terms

- **definition**: A single sentence that states what the concept is and what it does.
- **analogy**: A comparison to something familiar that conveys the concept's purpose.
- **counterexample**: A case where the concept does *not* apply, drawing its boundary.
- **worked example**: An example with visible steps so readers can reproduce the reasoning.
- **misconception**: A common mistake in understanding that must be broken early.

## Before/After

**Before**: "*Async* means *running at the same time*." (Wrong—conflates concurrency with parallelism.)

**After**: "*Async* means *doing other work while you wait for I/O*—it does not make CPU-bound code faster."

## The Fastest Way to Test Whether a Definition Works

This explanation is technically correct but still weak:

```text
A cache stores frequently used data.
```

It does not tell the reader what belongs in the cache, what should stay out, or where the boundary breaks. Adding a boundary and counterexample turns the concept into a decision tool:

```text
A cache stores answers that are expensive to fetch or compute again.
A large file read once during a migration is usually a poor cache candidate.
```

A strong concept explanation helps the reader classify the next example without asking you again. Edge cases and counterexamples often teach more than an expanded definition alone.

## Adjusting Explanation Depth by Audience

The same concept needs different treatment depending on the reader's background. Over-explain and senior readers leave; under-explain and beginners get lost.

| Reader level | Explanation depth | Example complexity | Analogy use | Assumed knowledge |
| --- | --- | --- | --- | --- |
| Beginner | Every step spelled out | Hello World level | Heavily used | Basic Python syntax only |
| Intermediate | Core concept only | Production scenario | Selective | Web framework experience |
| Advanced | Trade-offs, not definitions | Complex optimization | Rarely used | Architecture design experience |

### Beginner audience

**Concept**: Cache

1. **Start with analogy**: "Like keeping side dishes at the front of the fridge because you reach for them often…"
2. **Simple definition**: "A cache stores frequently reused values in a fast layer."
3. **Short code example**:

```python
cache = {}
cache["user:1"] = {"name": "Jimin"}
result = cache.get("user:1")
```

4. **Counterexample**: "Data you read only once usually does not belong in a cache."

### Intermediate audience

**Concept**: Cache

1. **Definition up front**: "A cache is a layer that holds copies in faster storage than the origin."
2. **Jump to Redis example**:

```python
import redis

r = redis.Redis()
r.set("user:1", '{"name": "Jimin"}')
r.get("user:1")
```

3. **Trade-off**: "Uses more memory but saves time on repeated reads."

### Advanced audience

**Concept**: Cache

1. **Comparison table**:

| Strategy | Cost | Complexity | Best fit |
| --- | --- | --- | --- |
| In-memory (dict) | Low | Low | Single process |
| Redis | Medium | Medium | Distributed system |
| CDN | High | High | Static assets |

2. **Invalidation strategy comparison**: LRU vs TTL vs manual purge—each with failure modes.

## Three Patterns for Introducing Technical Terms

When a term first appears, pick one of these approaches:

### Pattern 1: Immediate definition

**Example**: "FastAPI is an ASGI (Asynchronous Server Gateway Interface) framework."

**When to use**: The term is central to the article and must be understood immediately.

### Pattern 2: Defer

**Example**: "This article does not cover ASGI internals. See [the ASGI spec](https://asgi.readthedocs.io/) if curious."

**When to use**: The term is off-scope but must be mentioned.

### Pattern 3: Progressive disclosure

**Example**: Article 1 never mentions ASGI. Article 2 introduces it briefly. Article 3 covers it in depth.

**When to use**: A series explains a complex concept across multiple posts.

## Four Patterns for Explaining Abstract Concepts

Definitions alone leave readers passive. Combine these patterns so readers engage from multiple angles.

### Pattern 1: Analogy — connect unfamiliar to familiar

**Concept**: Cache

**Analogy**: "Like keeping side dishes at the front of the fridge—you store frequently computed values in faster storage."

**Effect**: Readers grasp purpose quickly through everyday experience. But stop the analogy early; switch to a precise definition before it misleads.

### Pattern 2: Contrast — draw the boundary

**Concept**: Sync vs Async

**Contrast**:

- **Sync**: Wait for one task to finish before starting the next.
- **Async**: Do other work while waiting for I/O to complete.

**Effect**: Side-by-side comparison makes the difference vivid and helps readers choose the right tool.

### Pattern 3: Visualization — show structure

**Concept**: FastAPI request flow

**Visualization**: A diagram showing "Client → Router → Dependency → Business Logic → Response."

**Effect**: Compresses multiple paragraphs into one image. Essential when layers, flows, or boundaries are the point.

### Pattern 4: Step decomposition — show process

**Concept**: HTTP request-response cycle

**Steps**:

1. Client sends HTTP request.
2. Server receives it and routes to a handler.
3. Handler executes business logic.
4. Handler builds a response object.
5. Server sends HTTP response back to the client.

**Effect**: Numbering the steps lets readers follow a complex process in sequence.

## Three Layers of Concept Explanation

When explaining a concept, surface → context → implication lets readers stop at their comfort level.

### Example: "async"

**Layer 1 — Surface (what it is):**
"Async means asynchronous."

**Layer 2 — Context (when it matters):**
"Async is a programming style that lets you do other work while waiting for I/O—network calls, file reads, or database queries."

**Layer 3 — Implication (where it breaks):**
"Async improves throughput only for I/O-bound work. If every task is CPU-bound, async adds overhead without parallelism gains."

Beginners stop at layer 2 and still have a useful mental model. Advanced readers get the trade-off from layer 3.

## Technical Term Handling Strategies

You cannot avoid jargon in technical writing, but you can prevent readers from hitting an unknown term unprepared.

### Strategy 1: Define on first appearance

**Bad**: "FastAPI supports ASGI."

**Good**: "FastAPI supports ASGI (Asynchronous Server Gateway Interface)."

### Strategy 2: Full name before abbreviation

First appearance uses the full name; subsequent references use the abbreviation.

### Strategy 3: Distinguish must-know vs nice-to-know

Not every term needs explanation. Focus on terms essential to the reader's goal.

- **Must-know**: router, dependency, endpoint
- **Nice-to-know**: ASGI internals, Starlette implementation details

For off-scope terms: "This article does not cover X. See [link] if curious."

## Five Anti-Patterns in Concept Explanation

### 1. Repeating the definition

**Bad**: "A cache is a cache because it caches…"

**Good**: "A cache stores frequently reused values in faster storage."

### 2. Stretching the analogy too far

**Bad**: "A cache is like the fridge—and opening the fridge door is like a network call, and the fridge light is like…"

**Good**: "A cache is like side dishes at the front of the fridge. (Now let's move to the precise definition.)"

### 3. Definition without counterexample

**Bad**: "A cache stores values in fast storage." (No boundary.)

**Good**: "A cache stores values in fast storage. But data read only once should not be cached."

### 4. Abstract explanation without code

**Bad**: "A cache stores values in memory." (Where is the proof?)

**Good**: "A cache stores values in memory: `cache = {}; cache['user:1'] = {'name': 'Jimin'}`"

### 5. Skipping the common misconception

**Bad**: "Caches are fast." (Leaves the reader assuming caches always help.)

**Good**: "Caches are fast for repeated reads. But without an invalidation strategy, a stale cache creates bugs worse than no cache."

## Hands-on: One Concept Explained

### Step 1 — Definition

Start with a direct definition: a cache stores frequent answers ahead of time.

### Step 2 — Analogy

An everyday analogy helps here: think of the side dishes you keep at the front of the fridge because you reach for them often.

### Step 3 — Counterexample

Then draw the boundary with a counterexample: data you read only once usually does not belong in a cache.

### Step 4 — Code example

```python
cache = {}
cache["user:1"] = {"name": "Jimin"}
```

### Step 5 — Common misconception

A useful misconception to break early: "A cache can grow forever." In practice, memory is finite—you need an eviction policy (LRU, TTL) from day one.

## Concept Card Template

Use this template in team wikis to keep concept explanations consistent:

| Field | Content |
| --- | --- |
| One-line definition | 10–20 words, states what and why |
| Analogy | One everyday comparison |
| Counterexample | One case where it does not apply |
| Code example | 5–12 lines |
| Common misconception | One sentence readers often get wrong |

### Example: Async processing

- **Definition**: Async is a style that does other work while waiting for I/O to complete.
- **Analogy**: Like doing dishes while the laundry runs.
- **Counterexample**: CPU-only tasks see limited benefit from async.

```python
import asyncio

async def fetch_user():
    await asyncio.sleep(1)
    return {"id": 1}
```

- **Misconception**: "Using async makes all code faster automatically."

## Depth Adjustment Quick-Reference

| Reader level | Definition | Counterexample | Code | Trade-off |
| --- | --- | --- | --- | --- |
| Beginner | Required | Required | Short | Optional |
| Intermediate | Required | Required | Medium | Required |
| Advanced | Summary | Required | Core only | Required |

Use this table to avoid over-explaining for experts and under-explaining for newcomers.

## What to Notice in This Code

- The definition is one line.
- The analogy is everyday.
- The counterexample draws the boundary.

## Five Common Mistakes

1. **A long definition.** Keep it to one sentence.
2. **A stretched analogy.** Stop before it misleads.
3. **No counterexample.** Without a boundary, the concept floats.
4. **A huge code example.** Five lines teach more than fifty.
5. **Skipping the common misconception.** Readers carry wrong assumptions forward.

## How This Shows Up in Production

The best internal wiki pages open with definition, analogy, counterexample, and example—in that order. When every page follows this structure, teams use the same word with the same meaning, and onboarding time drops measurably.

## How a Senior Engineer Thinks

- The definition is one line.
- The analogy sits in the familiar zone.
- The counterexample is the boundary.
- The example is runnable.
- The misconception is broken first.

## Checklist

- [ ] One-line definition.
- [ ] One analogy from everyday experience.
- [ ] One counterexample that draws the boundary.
- [ ] Five lines or fewer of example code.
- [ ] Common misconception addressed.
- [ ] Reader can classify the next case without asking.

## Practice Problems

1. Write a one-line definition of *cache*.
2. Write a counterexample for *microservice*.
3. Explain *idempotency* using the four-part pattern (definition, analogy, counterexample, code).

## Wrap-up and Next Steps

The next post is *Explaining Example Code*—how to present code so readers learn the concept, not just copy the snippet.

## Answering the Opening Questions

- **What should you show first to help a new reader understand a concept immediately?**
  Anchor with a definition, open the door with an analogy, draw boundaries with a counterexample, and make it tangible with a concrete example—in that order.
- **Why must analogies and counterexamples move together?**
  Analogies create intuition, but counterexamples prevent over-generalization. Without counterexamples, readers extend the analogy beyond its valid scope.
- **Why doesn't a one-line definition make an explanation stick?**
  Definitions are abstract—readers struggle to apply them to real situations. Analogy, counterexample, and example together make concepts memorable and actionable.

<!-- toc:begin -->
## In this series

- [Technical Writing 101 (1/10): What Is Technical Writing](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): Defining the Reader](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): Title and Structure](./03-title-and-structure.md)
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
