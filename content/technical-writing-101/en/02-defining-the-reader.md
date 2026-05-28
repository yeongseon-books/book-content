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

The same FastAPI example can be a friendly introduction for a junior engineer and a useless wall of text for the on-call engineer trying to restore service. The writing is not necessarily wrong—the target moved.

Once the reader is blurry, everything else drifts with it: how much background to include, which terms need explanation, how hard the example can be, and what the post should deliberately leave out. A concrete reader makes those decisions faster.

This is the 2nd post in the Technical Writing 101 series. Here we turn the reader into a working model with persona, prior knowledge, goal, and non-goal.


![technical writing 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/02/02-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 2 flow overview*
> When the reader is blurry, everything else—depth, vocabulary, scope—drifts with it.

## Questions to Keep in Mind

- Why does writing "for everyone" end up helping no one properly?
- Why do sentences sharpen when you build a persona?
- How does writing prerequisites and goals first shrink scope?

## Why It Matters

A blurry reader leads to blurry sentences. When you have not decided who you are helping, explanation depth, example length, terminology choices, and non-goals all drift.

> Mental model: pin down one concrete reader and scope, vocabulary, and depth automatically align around that person.

## Key Terms

- **persona**: A model of the reader—their role, knowledge, and current situation.
- **prerequisite**: Prior knowledge the reader already has.
- **goal**: What the reader will be able to do after reading.
- **scope**: What the post covers.
- **non-goal**: What the post deliberately does not cover.

## Before/After

**Before**: "A post for developers."

**After**: "A post for a first-year Python engineer learning FastAPI."

## The Same Feature Changes Shape for Different Readers

| Reader | Already knows | Needs right now | Should be left out |
| --- | --- | --- | --- |
| Beginner | Python syntax, `pip` | A first FastAPI endpoint | Deployment strategy, performance tuning |
| Reviewer | API basics | Missing prerequisites in the draft | Full install walkthrough |
| On-call engineer | Production environment | Triage steps and logs | Refresher on beginner concepts |

The same `/health` endpoint example serves different purposes for each row. For the beginner, route declaration and the run command matter most. For the on-call engineer, log location and reproduction path matter most. That is why a persona is not decorative UX language—it is an editing boundary that decides what stays and what gets cut.

## Three Realistic Persona Examples

### Persona A: Junior Developer

```python
persona_junior = {
    "name": "Jimin",
    "role": "Junior backend developer (6 months experience)",
    "knows": ["Python basics", "pip install", "git add/commit/push"],
    "unknown": ["async/await", "ORM", "writing tests", "Docker"],
    "goal": "Build a user CRUD API assigned by the team within 3 days",
    "non_goal": ["production deployment", "performance tuning", "CI/CD setup"],
    "pain_point": "FastAPI docs are overwhelming—unsure where to start"
}
```

**Document traits for this persona:**
- Explain every step in detail
- Keep code examples under 10 lines
- Always show expected output
- Include a "why do it this way?" explanation

### Persona B: Mid-Level Developer

```python
persona_mid = {
    "name": "Alex",
    "role": "Backend developer (3 years experience)",
    "knows": ["Flask", "REST API design", "PostgreSQL", "Docker basics"],
    "unknown": ["FastAPI dependency injection", "Pydantic advanced features", "WebSocket"],
    "goal": "Migrate an existing Flask project to FastAPI",
    "non_goal": ["basic syntax learning", "Python installation"],
    "pain_point": "Unclear on Flask-to-FastAPI differences, especially DI"
}
```

**Document traits for this persona:**
- Explain via Flask comparisons
- Skip basic concept introductions
- Focus on tradeoffs
- Include migration script examples

### Persona C: On-Call Engineer

```python
persona_oncall = {
    "name": "Sam",
    "role": "SRE engineer (5 years experience)",
    "knows": ["multiple frameworks", "K8s operations", "monitoring"],
    "unknown": ["FastAPI internals"],
    "goal": "Resolve a production incident at 3 AM within 5 minutes",
    "non_goal": ["following tutorials", "learning basic concepts"],
    "pain_point": "Needs to find the problem in logs and recover fast"
}
```

**Document traits for this persona:**
- Checklist format
- Skip all basic explanation
- Focus on log locations and metric queries
- "If this symptom → this fix" pattern

## Reader Matrix: Experience × Empathy Level

Splitting readers into beginner/intermediate/advanced alone misses an important dimension. Adding empathy level (awareness of the problem) creates a more precise reader model.

| Experience \ Awareness | Unaware of problem | Aware of problem | Experiencing problem now |
| --- | --- | --- | --- |
| **Beginner** | Introductory tutorial | Problem-focused starter guide | Troubleshooting guide |
| **Intermediate** | Deep-dive guide | Comparison guide | Experience-sharing blog |
| **Advanced** | Reference docs | Design discussion | System design blog |

Even among beginners, the type of document needed changes based on whether they are currently stuck. Considering empathy level alongside experience helps you write for the reader's actual situation.

## Persona Quality Test

After building a persona, verify it can answer these five questions:

1. **What can this reader do right now?** → Checks whether prerequisites are specific
2. **What can this reader NOT do?** → Checks whether knowledge gaps are specific
3. **What will this reader do after finishing the document?** → Checks whether the goal is clear
4. **What should this reader NOT need to do after reading?** → Checks whether non-goals are clear
5. **Where will this reader get stuck?** → Identifies what the troubleshooting section must cover

If you cannot answer these five questions concretely, the persona needs more detail.

## Three Non-Goal Patterns

Non-goals are the most powerful tool for narrowing scope. Three patterns for writing them:

### Pattern 1: Stage boundary

**Example**: "This post covers local development only—not production deployment."

**Effect**: The reader knows exactly how far they will go and expects a separate post for the next stage.

### Pattern 2: Technology boundary

**Example**: "This post covers FastAPI only—it does not include Django comparisons."

**Effect**: The reader understands the technology scope and does not expect cross-framework analysis.

### Pattern 3: Level boundary

**Example**: "This post does not cover performance optimization, security hardening, or custom middleware."

**Effect**: Advanced readers quickly identify this as an introductory post and move on.

## Documentation Strategy by Reader Level

The same topic requires completely different vocabulary, depth, and examples depending on reader level.

| Reader level | Terminology | Explanation depth | Example type | Can omit |
| --- | --- | --- | --- | --- |
| Beginner (0–6 mo) | One-line explanation per technical term | Every step detailed | Hello World, minimal executable | Nothing—state all prerequisites |
| Intermediate (6 mo–2 yr) | Standard terms need no explanation | Key steps only | Real-world scenarios, extensions | Installation, basic syntax |
| Advanced (2+ yr) | Domain jargon acceptable | Tradeoffs over concepts | Optimization, edge cases, architecture | Basic concepts, common usage |

Using intermediate vocabulary in a beginner post causes readers to drop off at paragraph one. Repeating basic concepts in an advanced post exhausts patience. Fix the reader level before writing.

## The "Writing for Everyone" Anti-Pattern

"This document is for beginners through advanced users" is the most dangerous opening sentence. Writing for everyone produces three cascading problems:

### Problem 1: Cannot decide explanation depth

Explaining basics for beginners bores advanced readers. Skipping basics for advanced readers loses beginners. Neither is satisfied.

### Problem 2: Example difficulty oscillates

Beginners need Hello World. Advanced readers need complex real-world scenarios. Mixing both in one document breaks structure.

### Problem 3: Cannot define non-goals

When the reader range is unlimited, "what this post does not cover" becomes impossible to state. The document grows endlessly.

### Solution: Split readers, split documents

Instead of one document for all levels, split by reader:

- **Beginner**: "Getting Started with FastAPI: Your First Endpoint"
- **Intermediate**: "Clean Router Structure with FastAPI Dependency Injection"
- **Advanced**: "Optimizing FastAPI Async: Finding the Bottleneck"

Each document now has a clear persona, prerequisites, goal, and non-goals. Readers find their level instantly.

## Persona-Based Sentence Transformation

- Vague: "This document is for API developers."
- Fixed: "This document is for backend developers with 1–3 years of Flask experience who find FastAPI dependency injection unfamiliar."

- Vague: "We will proceed with deployment."
- Fixed: "This post does not cover deployment—it ends at local execution verification."

## Hands-on: A Persona Card

### Step 1 — Name and role

- Persona: `{"name": "Jimin", "role": "First-year Python backend"}`

### Step 2 — Prior knowledge

- Knows: `variables`, `functions`, `git basics`

### Step 3 — Gaps

- Unknown: `async`, `type hints`

### Step 4 — Goal

- Goal: `Ship the first FastAPI endpoint`

### Step 5 — Non-goal

- Non-goal: `deployment`, `DB migrations`

## What to Notice in This Code

- The persona has a name—it feels like one person.
- The persona has explicit gaps—these determine what to explain.
- The persona has non-goals—these determine what to cut.

## Five Common Mistakes

1. **Targeting everyone.**
2. **Skipping prerequisites.**
3. **Vague goals (no verb, no outcome).**
4. **Missing non-goals.**
5. **Examples too hard for the stated reader.**

## How This Shows Up in Production

API references, user guides, and tutorials all split by persona. Internal docs for a platform team look nothing like onboarding guides for new hires—even when they describe the same system.

## How a Senior Engineer Thinks

- The reader feels like one person, not a demographic.
- Non-goals shrink the post more than any editing pass.
- Examples sit inside the prior-knowledge boundary.
- Goals are written as verbs—"build," "deploy," "verify."
- The future you in two weeks is also a reader.

## Checklist

- [ ] One persona with a name
- [ ] Three or more prerequisites listed
- [ ] One goal stated as a verb phrase
- [ ] At least one non-goal declared

## Practice Problems

1. Write the definition of *persona* in one line.
2. Write the meaning of *non-goal* in one line.
3. Write an example of a *prerequisite* in one line.

## Wrap-up and Next Steps

A clear reader makes sentences, examples, and scope all sharper. Especially when prerequisites, goals, and non-goals are written together, the document becomes shorter and more useful. The next post covers how to design titles and structure once the reader is fixed.

## Answering the Opening Questions

- **Why does writing "for everyone" end up helping no one properly?**
  Targeting everyone means you cannot decide explanation depth, terminology level, example difficulty, or non-goals. The result looks friendly but serves no one adequately—beginners get lost and experts get bored.

- **Why do sentences sharpen when you build a persona?**
  A persona fixes your target reader as a concrete reference point. Every sentence aligns toward that reader—ambiguous phrasing becomes obvious when you ask "would my persona understand this without extra context?"

- **How does writing prerequisites and goals first shrink scope?**
  Listing non-goals alongside prerequisites clarifies what the document will not cover. This enables bold cuts of unnecessary explanation and prevents scope creep before it starts.

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
