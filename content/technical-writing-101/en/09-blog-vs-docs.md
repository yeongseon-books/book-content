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

This is the 9th post in the Technical Writing 101 series. It distinguishes blogs from documentation by role, lifespan, and canonical ownership.


![technical writing 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/09/09-01-concept-at-a-glance.en.png)
*technical writing 101 chapter 9 flow overview*
> Blogs preserve experience and interpretation; documentation preserves the current operational truth.

## Questions to Keep in Mind

- Why should blog posts and official documentation never be mixed into one artifact?
- How do their lifecycles and ownership structures differ in practice?
- How does the Diátaxis model explain which quadrant each type belongs to?

## Why It Matters

When kinds of writing mix, the reader gets lost. A blog post cited as official documentation erodes trust the moment it goes stale. An official doc written in blog style makes the reader wonder whether it represents the team's current position or one person's past opinion.

> Mental model: blogs preserve context and interpretation, while docs preserve the current truth.

Blogs and docs both serve engineering teams, but they have different owners, freshness rules, and lifespans. Separating them with clear ownership and deliberate links prevents the reader from following stale advice or citing context as official policy.

## Key Terms

- **Diátaxis**: A four-quadrant documentation model that separates tutorials, how-tos, references, and explanations.
- **lifecycle**: The timeline from creation through updates to eventual archival or deletion.
- **freshness**: How current the content is relative to the system it describes.
- **canonical**: The single authoritative source of truth for a given topic.
- **archive**: A state where content is preserved but marked as no longer current.

## Before/After

**Before**: A blog post gets cited as official documentation—readers follow stale instructions.

**After**: Blogs hold experience; docs hold truth—each links to the other with clear roles.

## Separate ownership and freshness before channels

The difference between blogs and docs is not tone or format. It is ownership and freshness obligations.

| Dimension | Blog | Documentation |
| --- | --- | --- |
| Main owner | Individual author or editorial team | Product or platform owner |
| Freshness rule | Accurate at the time of writing | Kept current as the source of truth |
| Reader expectation | Context, experience, interpretation | Procedure, policy, reference |
| Update trigger | Revised when the author chooses | Updated when code or process changes |
| Link direction | Points readers to canonical docs | Links out to background and rationale |
| Review process | Optional (author discretion) | Mandatory (team PR review) |
| Versioning | Time-stamped at publication | Versioned alongside the codebase |
| Retirement | Archived with a note | Deprecated with migration guide |
| Example | "Why we chose session auth" | "Authentication implementation guide" |

This table matters because the same FastAPI deployment topic produces radically different outputs depending on which column you are writing in. A blog explains trade-offs the team debated. A doc tells you the exact commands, version constraints, and rollout order that are correct today.

## When to write a blog vs documentation

Use this decision flow to determine which format fits.

```text
Is this the team's current official standard?
  │
  ├─ Yes → Write documentation
  │       - Version-control alongside code
  │       - PR review required
  │       - Team ownership
  │
  └─ No  → Write a blog post
          - Share personal or team experience
          - Link to canonical docs for current truth
          - State the time of writing explicitly
```

### Write a blog post when

1. **Sharing personal experience** — "How our team adopted FastAPI" or "Why this approach worked for us."
2. **Writing a postmortem** — "May 10 incident retrospective" with the specific context and response.
3. **Explaining a controversial decision** — "Why we chose REST over GraphQL" with trade-off analysis.
4. **Comparing technologies at a point in time** — "Python async libraries in May 2026."

### Write documentation when

1. **Defining current procedure** — "API secret management policy" or "Deployment checklist."
2. **Specifying product behavior** — "FastAPI official guide" or "API reference."
3. **Matching the current codebase** — "Authentication flow (as of 2026-05-15)."
4. **Recording SLA or legal constraints** — "Service Level Agreement" or "Data retention policy."

## Promoting a blog post to documentation

Sometimes a blog post becomes so widely cited that it functions as de-facto documentation. At that point, consider formal promotion. The post qualifies for promotion when it meets all four criteria:

1. **Matches the current codebase.** If the blog describes code from six months ago, it needs rewriting first.
2. **Passes team review.** Official docs represent team consensus, not one person's take.
3. **Provides backlinks.** The original blog should be archived with a pointer to the new doc.
4. **States the current version.** Docs always carry a version stamp or last-updated date.

```markdown
> **Archived**: This post was written in October 2025.
> The current official documentation is at [docs.example.com/auth](https://docs.example.com/auth).
```

## Linking blogs and docs together

Blogs and docs should not compete. They should point at each other with clear intent.

**Blog → Docs (at the bottom of the blog post):**

```markdown
## References

This post was written against FastAPI 0.110. For the current official
guide, see [docs.example.com/auth](https://docs.example.com/auth).
```

**Docs → Blog (in a "Further Reading" section):**

```markdown
## Further Reading

- [Why we chose session auth over JWT](https://blog.example.com/session-decision-2025) — design rationale
- [May 10 incident retrospective](https://blog.example.com/incident-2025-05-10) — operational context
```

The rule is simple: docs link to blogs for background; blogs link to docs for current truth. Neither replaces the other.

## Same topic, different roles: a comparison

Below is the same authentication topic written as a blog post and as documentation. Notice how the questions each one answers are completely different.

**Blog version** — explains *why*:

```markdown
# Why Our Team Chose Session Auth Over JWT

*Written October 15, 2025*

We compared JWT and session-based auth for our FastAPI 0.104 API.
JWT is stateless and scales well but makes token revocation complex.
Sessions are stateful but revocation is trivial. With <1000 concurrent
users and mandatory revocation, sessions won.

## References
Current auth guide: [docs.example.com/auth](https://docs.example.com/auth)
```

**Documentation version** — explains *what* and *how*:

```markdown
# Authentication Implementation

*Last updated: 2026-05-21 | FastAPI 0.110, Python 3.11*

This project uses session-based authentication.

## Setup
[exact code]

## Session Creation
[exact code]

## Security Requirements
- Session expiry: 24 hours
- HTTPS required
- CSRF token enabled

## Further Reading
- [Why we chose sessions](https://blog.example.com/session-decision-2025)
```

The blog asks "why did we decide this?" The doc asks "what do I do right now?" Both are valuable. Neither can replace the other.

## The Diátaxis four quadrants in detail

Diátaxis classifies all technical content into four quadrants by purpose. Understanding where blogs and docs sit within this model prevents accidental mixing.

| Quadrant | Purpose | Reader's Question | Tone |
| --- | --- | --- | --- |
| **Tutorial** | Learning | "How do I get started?" | Creating an experience |
| **How-to** | Problem-solving | "How do I do X?" | Directing |
| **Reference** | Information | "What does this function accept?" | Describing |
| **Explanation** | Understanding | "Why is it designed this way?" | Discussing |

Blog posts typically live in the **Explanation** quadrant (and occasionally **Tutorial** for walkthrough posts). Official documentation spans **How-to**, **Reference**, and **Tutorial**. Knowing this prevents you from writing a blog post that accidentally tries to be a reference page, or a reference page that accidentally tries to tell a story.

## Hands-on: Mapping the Quadrants

### Step 1 — Tutorial

Use **tutorial** for first-time learning. Example: "Build your first API endpoint."

### Step 2 — How-to

Use **how-to** for solving a specific problem. Example: "Add rate limiting to an existing API."

### Step 3 — Reference

Use **reference** for API specifications and other authoritative lookups. Example: "`RateLimiter` class API."

### Step 4 — Explanation

Use **explanation** when the goal is to show why a design was chosen. Example: "Why we chose token bucket over sliding window."

### Step 5 — Blog vs docs

```python
blog = "My experience and opinion"
docs = "The team's official truth"
```

## What to Notice in This Code

- Blogs hold experience—they are time-stamped and personal.
- Docs hold truth—they are versioned and team-owned.
- The Diátaxis quadrants prevent mixing by clarifying the purpose of each piece.

## Five Common Mistakes

1. **Citing a blog as official docs.** The blog ages; the reader follows stale instructions.
2. **Letting the docs go stale.** Docs that do not match the current code are worse than no docs.
3. **Not stating the version.** Without a version stamp, the reader cannot judge freshness.
4. **No archive policy.** Old blogs without archive notices keep appearing in search results.
5. **No canonical link.** Without a pointer to the official source, readers cannot find current truth.

## How This Shows Up in Production

Engineering teams separate blogs from docs and version-control the docs alongside the code. Stripe publishes engineering blog posts for design rationale and maintains a separate docs site for API reference. Google's engineering blog explains decisions; Google Cloud docs specify procedures. The pattern scales from two-person startups to thousand-engineer organizations.

## How a Senior Engineer Thinks

- Blogs capture past decisions and the reasoning behind them.
- Docs are the living truth that must stay current or be deprecated.
- Old posts go to the archive with a clear pointer to the replacement.
- The canonical source is always in the docs, never in a blog.
- Blogs link to docs for current truth; docs link to blogs for background context.

## Checklist

- [ ] Four-quadrant mapping identifies where the content belongs.
- [ ] Freshness obligation is explicit (time-stamped vs kept-current).
- [ ] Canonical link connects blog to docs (or docs to blog).
- [ ] Archive policy exists for content that goes stale.

## Practice Problems

1. Write the four quadrants of Diátaxis in one line.
2. Write the meaning of *canonical* in one line.
3. Write the definition of *freshness* in one line.

## Answering the Opening Questions

- **Why should blog posts and official documentation never be mixed into one artifact?**
  Blogs and docs serve different roles—mixing them erodes trust. Readers expect docs to be current and authoritative; blogs to be personal and time-stamped. When docs read like blog posts, readers question accuracy. When blogs claim to be official, readers follow stale instructions.
- **How do their lifecycles and ownership structures differ in practice?**
  Blogs capture experience at a point in time (the author owns them, they age gracefully into archives). Docs represent current truth (the team owns them, they must be updated or deleted when the system changes). Different ownership means different update cadences, review processes, and retirement strategies.
- **How does the Diátaxis model explain which quadrant each type belongs to?**
  Diátaxis splits content into four zones by purpose: tutorials (learning), how-to guides (problem-solving), reference (lookup), and explanation (understanding). Blog posts typically live in the explanation quadrant. Docs span how-to, reference, and tutorial. This framework prevents channel confusion by making the purpose—not the format—the organizing principle.

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
