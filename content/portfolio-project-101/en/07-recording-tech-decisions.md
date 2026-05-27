---
series: portfolio-project-101
episode: 7
title: "Portfolio Project 101 (7/10): Recording Tech Decisions"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Portfolio
  - ADR
  - Decision
  - Architecture
  - Beginner
seo_description: How to use lightweight ADRs to record technical choices, alternatives, and trade-offs in a portfolio project.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (7/10): Recording Tech Decisions

When reviewers inspect a portfolio project, they care about more than the final code. They also want to know why a specific stack was chosen, what alternatives were considered, and what trade-offs were accepted. Code shows the outcome, but it rarely shows the judgment on its own.

This is the 7th post in the Portfolio Project 101 series. Here we will use a lightweight ADR-style format to record technical choices and make design judgment visible in a way that is easy to keep up.

---

> A good decision note does not declare a perfect answer. It records what options existed, why one was chosen, and what consequences came with it.


![portfolio project 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/07/07-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 7 flow overview*
> Recording technology choices shows why you picked each tool. Without explanation, you look like you chase trends. With explanation, you show judgment.

## Questions to Keep in Mind

- Why do technical choices usually stay invisible if you only show code?
- How do alternatives and consequences make a project more persuasive?
- How lightweight can an ADR be and still be useful?

## Why It Matters

Hiring loops often care as much about decision quality as implementation quality. Two projects may ship the same capability, but the one that explains why a framework was chosen and what was sacrificed for speed or simplicity usually reads much deeper.

Decision records help because they make constraint-aware thinking visible. They also help you later, when you need to remember why something was done a certain way.

## Mental Model

A useful decision record usually flows from context to options, then to the decision, the consequence, and the likely next step.

This order matters because choices only make sense inside a real situation. “We picked FastAPI” is weak on its own. “We picked FastAPI because we had a solo developer, a short deadline, and a need for fast API docs” is much more informative.

## Key Terms

- **ADR**: Architecture Decision Record, usually a short document for one decision.
- **Context**: the project constraints or conditions behind the choice.
- **Options**: the realistic alternatives you considered.
- **Decision**: the chosen direction.
- **Consequence**: what the decision improved and what it cost.

## Before and After

**Before**: “We just built it that way,” with no explanation of why the choice happened.

**After**: the project keeps a short note that captures the situation, options, decision, and result.

The second project makes judgment much easier to see.

## Step by Step

### Step 1 — Write the context first

A choice only becomes meaningful when its constraints are visible.

Write the context in plain language first: solo developer, two-week deadline, and strong familiarity with Python.

This prevents hindsight from flattening every decision into a generic “best practice.”

### Step 2 — List the real options

Comparison gives the final choice weight.

For example, listing only `FastAPI`, `Flask`, and `Django` is already enough to make the comparison real.

You do not need a giant matrix. Two or three realistic options are enough.

### Step 3 — State the decision clearly

The final choice should be plain and unambiguous.

Then state the decision directly: choose FastAPI.

The power comes from placing that line after the context and the options.

### Step 4 — Record the reasoning as criteria

The explanation is stronger when it uses criteria rather than taste.

It helps to state the reasoning as criteria right away:

- `async`
- `type_hints`
- `swagger_auto`

Those criteria are easy to connect back to the problem and the constraints.

### Step 5 — Record the consequence honestly

Good notes include both gains and costs.

For example, you can write that `build time was faster` while the trade-off was a `smaller ecosystem`.

That honesty is what makes the note feel like judgment instead of self-promotion.

## What to Notice in the Code

- Context belongs at the top because choices only make sense inside constraints.
- Options matter because they prove the decision was not arbitrary.
- Consequences matter because trade-offs are where engineering judgment becomes visible.

## Common Mistakes

1. Writing only the final decision without alternatives.
2. Using trend or preference as the whole justification.
3. Recording no consequence, so the note cannot be evaluated later.
4. Keeping ADRs outside the repository where reviewers never see them.
5. Forgetting numbering or dates, which makes the history hard to follow.

Decision records do not need to be long. They need to be clear and complete.

## How This Reads in Practice

Many teams keep notes like `docs/adr/0001-...md` for exactly this reason. As time passes, people forget why a decision happened. New contributors only see the final state. ADRs close that gap.

The same habit helps portfolio work. A small project starts to read like a thoughtful engineering artifact when reviewers can see not only what was built, but why.

## Checklist

- [ ] I chose a folder for ADR notes.
- [ ] I recorded at least a few meaningful technical choices.
- [ ] Each note includes context, options, decision, and consequence.
- [ ] The notes are ordered by number or date.

## Practice Problems

1. Choose one project decision that deserves an ADR today.
2. List two alternatives you genuinely considered.
3. Write one benefit and one cost of the chosen option.

## Wrap-up and Next Steps

Technical decision records reveal the judgment behind the result. When you write down the context, compare the alternatives, explain the decision criteria, and record the consequence honestly, even a small project becomes much easier to evaluate as real engineering work.

Next, we will expand the project beyond the repository and look at how to turn it into a technical post that others can discover through search.

## Appendix: ADR Table for README

A high-level overview of architectural decisions helps reviewers see that judgment went into the project.

```markdown
## Architectural Decisions

| # | Title | Status | Date |
| --- | --- | --- | --- |
| 1 | [Backend Framework](./docs/adr/0001-backend-framework.md) | Accepted | 2026-05-01 |
| 2 | [Database Choice](./docs/adr/0002-database-choice.md) | Accepted | 2026-05-03 |
| 3 | [Cache Strategy](./docs/adr/0003-cache-strategy.md) | Superseded | 2026-05-10 |
| 7 | [DB Index Tuning](./docs/adr/0007-db-index-tuning.md) | Accepted | 2026-05-18 |
```

This table at the end of your "Project Structure" section signals to reviewers that you made tech choices deliberately. When a hiring manager or senior developer sees Superseded status, the message is: 'This project was reviewed and improved over time.' That is the difference between looking like a bare implementer versus looking like someone who designs.

## Appendix: Decision Flow — When to Record, When to Skip

Not every choice needs an ADR. This flowchart helps decide.

```text
At a decision point
  |
  ├─ Are there two+ alternatives?
  |   ├─ Yes -> Have meaningful trade-offs?
  |   |        ├─ Yes -> Write ADR ✓
  |   |        └─ No -> Just comment in code
  |   └─ No -> Skip (only one option)
  |
  └─ Could this change later?
      ├─ Yes -> Write ADR ✓ (future reference)
      └─ No -> Code comment is enough
```

This flow prevents unnecessary documentation while ensuring important decisions never get lost.

## Appendix: Database Selection ADR Example

Database choice is usually an early decision. Here is an example recording SQLite selection for a small project.

```markdown
# ADR-0002: SQLite Adoption

## Status
Accepted

## Context
- Solo developer, initial data under 1000 rows
- Need to minimize external database server overhead
- Want test isolation from external services

## Options
1) PostgreSQL (Supabase free tier)
2) SQLite (file-based)
3) MongoDB Atlas (free tier)

## Decision
Use SQLite as the base database.

## Rationale
- No external network needed during tests
- Zero setup for local development
- SQLAlchemy makes future PostgreSQL migration easy

## Consequences
- Benefit: simple deploy, test isolation, zero cost
- Trade-off: concurrent request limits, must migrate if project grows
- Future condition: review PostgreSQL migration when user count reaches 100 (planned as ADR-0008)
```

The strength here is the 'future condition' clause. Pre-defining when to revisit a decision gives future judgment a clear anchor.

## Appendix: Connecting ADR to PR Template

Isolating ADRs makes it hard to trace 'when was this decision actually applied?' Link them to PRs.

```markdown
## PR Template Example (.github/PULL_REQUEST_TEMPLATE.md)

### Change summary
- 

### Related ADRs
- [ ] New tech decision included -> ADR added
- [ ] Existing ADR changed -> status updated
- [ ] None

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
```

This way, during PR review, you can instantly answer 'what is the basis for this change?' Solo projects benefit from this habit too, since it transfers cleanly to team environments later.

## Appendix: Tech Stack Decision Matrix

To make tech choices persuasive, compare candidates side-by-side using consistent criteria. Here is a backend framework example.

| Criterion | FastAPI | Flask | Django |
| --- | --- | --- | --- |
| Learning curve | Medium | Low | Medium-High |
| Docs/type support | Strong | Moderate | Strong |
| Fast MVP | Strong | Strong | Moderate |
| Built-in features | Moderate | Low | Very strong |
| Fit for this project | High | Medium | Low |

This is not about finding a 'correct' framework. It is about explaining 'the most rational choice given our constraints.' The same technology can have different verdicts depending on deadline, team, and operational needs.

## Appendix: Real ADR Template (Compact Form)

Here is a ready-to-use ADR that can go straight into your repository. Name it `docs/adr/0001-backend-framework.md` and number the rest sequentially.

```markdown
# ADR-0001: FastAPI Adoption

## Status
Accepted

## Context
- Demo must be complete in 2 weeks
- Need fast Python API development
- Must leverage type hints and auto-docs

## Options
1) Flask
2) FastAPI
3) Django

## Decision
Adopt FastAPI.

## Consequences
- Benefit: OpenAPI auto-generation, async support, type-driven development
- Trade-off: smaller team reference pool compared to Flask
```

This length is neither too verbose nor too terse. It captures enough reasoning without overhead.

## Appendix: Decision Record Maintenance Rules

ADRs are not write-once documents. They are living records. These rules keep them trustworthy.

1. Write initial version within 24 hours of the decision
2. Mark 'why' missing as Proposed, not Accepted
3. Never overwrite - add new ADRs when decisions change
4. Link follow-up ADRs with validation metrics

**Example of decision evolution:**

```markdown
## State History
- ADR-0003: Redis caching adopted (Accepted)
- ADR-0007: Redis removed, replaced with DB index tuning (Supersedes ADR-0003)
```

This history shows the project learned and adapted. In interviews, you can explain your revision experience systematically.

## Appendix: ADR Quality Checklist

Quality matters more than writing the ADR itself. If you can answer 'yes' to all these, your record is solid.

| Review Question | Yes/No |
| --- | --- |
| Are the constraints at the time clearly written? |  |
| Did I compare at least two real alternatives? |  |
| Are the decision criteria tied to requirements, not preference? |  |
| Did I record both benefits and trade-offs? |  |
| Did I include a future reference point or metric? |  |

## Appendix: ADR Numbering and Folder Structure

```markdown
docs/adr/
- 0001-backend-framework.md
- 0002-database-choice.md
- 0003-cache-strategy.md
- 0004-deployment-platform.md
```

Fixed numbering makes it easy to trace decisions even as projects grow. It also helps during interviews when you need to walk through the decision flow chronologically.

## Appendix: ADR Triggers and Topics

ADRs are not just for 'big' decisions. Any of these situations deserves a record.

| Trigger | Example | ADR Title Example |
| --- | --- | --- |
| Framework/library choice | FastAPI vs Flask | `0001-backend-framework.md` |
| Data storage decision | PostgreSQL vs SQLite | `0002-database-choice.md` |
| Auth approach | JWT vs Session | `0003-auth-strategy.md` |
| Deploy platform | Railway vs Fly.io | `0004-deployment-platform.md` |
| Architecture pattern | Monolith vs microservices | `0005-architecture-style.md` |
| Test strategy | E2E first vs Unit first | `0006-test-strategy.md` |
| External integration | Stripe vs custom payment | `0007-payment-integration.md` |

For portfolio projects, 3-5 ADRs usually suffice. The key is capturing every place where choice existed.

## Appendix: ADR Status Transitions

When the project evolves and earlier decisions need to change, do not edit the old ADR. Add a new one and update the status.

```markdown
# ADR-0003: Redis Caching Layer

## Status
Superseded by ADR-0007

## Context
- API response time averaging 800ms
- 60% of requests were repeated queries

## Decision
Introduce Redis as a cache layer.

## Consequences
- Benefit: sub-100ms responses for cached requests
- Trade-off: added operational complexity
- Note: Later replaced by database-level index tuning (see ADR-0007)
```

This approach keeps the history transparent. In interviews, you can show the full evolution and explain your learning journey.

## Answering the Opening Questions

- **Why do technical choices usually stay invisible if you only show code?**
  - The article treats Recording Tech Decisions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do alternatives and consequences make a project more persuasive?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How lightweight can an ADR be and still be useful?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): Writing the README](./03-writing-the-readme.md)
- [Portfolio Project 101 (4/10): Building the Demo](./04-building-the-demo.md)
- [Portfolio Project 101 (5/10): Deploying the Project](./05-deploying-the-project.md)
- [Portfolio Project 101 (6/10): Tests and Documentation](./06-tests-and-documentation.md)
- **Recording Tech Decisions (current)**
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Architecture Decision Records](https://adr.github.io/)
- [Thoughtworks Technology Radar — Lightweight ADRs](https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records)
- [ADR Tools](https://github.com/npryce/adr-tools)

Tags: Portfolio, ADR, Decision, Architecture, Beginner
