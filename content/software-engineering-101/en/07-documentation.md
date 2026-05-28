---
series: software-engineering-101
episode: 7
title: "Software Engineering 101 (7/10): Documentation"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - SoftwareEngineering
  - Documentation
  - README
  - ADR
  - Knowledge
seo_description: README, ADR, docstring, and runbook roles, plus the Diataxis four-quadrant model in a practical short form.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (7/10): Documentation

It is tempting to say that good code should make documentation unnecessary. Strong names, small modules, and readable tests do carry a lot of information. But code alone rarely explains why a decision was made, when an operator should follow a procedure, or where a new teammate should start on day one.

The biggest failure mode of weak documentation is not inconvenience. It is dependency on specific people. Every unanswered question routes through memory, availability, and interruption cost. That is why documentation is not a side artifact. It is a core part of asynchronous engineering work.

This is the 7th post in the Software Engineering 101 series. In this chapter, we split documentation by reader need, then look at the minimum useful shapes for a README, ADR, runbook, docstring, and onboarding checklist.


![software engineering 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/07/07-01-concept-at-a-glance.en.png)
*software engineering 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Documentation?
- Which signal should the example or diagram make visible for Documentation?
- What failure should be prevented first when Documentation reaches a real system?

## What You Will Learn

- The minimum sections of a useful README
- Recording decisions with ADRs
- Docstrings and type hints
- Runbooks and onboarding documents
- The Diataxis four quadrants (tutorial / how-to / reference / explanation)

## Why It Matters

Without docs, every question routes through a person. The moment a person becomes the bottleneck, team speed depends on their work hours.

> Documentation is the infrastructure of async collaboration.

Diataxis splits docs by reader intent.

## Key Terms

- **README**: First impression and entry point.
- **ADR**: A short record of a decision and its reasoning.
- **Docstring**: The usage contract of a function or class.
- **Runbook**: Step-by-step procedure for incidents.
- **Diataxis**: Four-quadrant documentation model.

## Before/After

**Before — one giant wiki**

```text
"It's all on the wiki" -> nobody knows where
```

**After — four quadrants + index**

```text
docs/tutorials/  docs/how-to/  docs/reference/  docs/explanation/
```

Folders split by reader intent.

## Hands-on: A Small Doc Set

### Step 1 — README in 5 blocks

```markdown
# 1_readme.md
## What — one-sentence description
## Why — why it exists
## Quick start — working in 60 seconds
## Configuration — env var table
## Links — go deeper
```

The reader sees value within 60 seconds.

### Step 2 — One-page ADR

```markdown
# 2_adr.md
# ADR 0012: introduce cache
- Context, Decision, Alternatives, Consequences
- Date, Owners
```

A decision outlives the code that implements it.

### Step 3 — Docstring and types

```python
# 3_docstring.py
def compute_invoice(amount: int, tax_rate: float) -> int:
    """Return cents amount including tax.

    Raises:
        ValueError: when amount is negative.
    """
```

The signature is half the documentation.

### Step 4 — Runbook

```markdown
# 4_runbook.md
## Symptom
- 5xx error rate > 2% for 5 min
## Diagnose
1. Check Grafana dashboard X
2. Look at the latest deploy log
## Action
- Roll back immediately (`kubectl rollout undo ...`)
```

It must be followable at 3 a.m.

### Step 5 — Onboarding checklist

```markdown
# 5_onboarding.md
- [ ] Clone repo, run dev environment
- [ ] Land first PR (typo fix)
- [ ] Shadow first incident within a week
```

Designs the new hire's first thirty days.

## A document-set verification check

Documentation quality is easier to see through a real journey than through word count. Walk the repo like a new engineer or an on-call responder and see whether the right document appears at the right moment.

### Verification steps

1. Try to understand the project from the README alone for the first five minutes.
2. Pick one major decision and look for an ADR or RFC that explains it.
3. Follow an incident runbook and see whether the steps are executable as written.

**Expected output:**

- A strong README reveals project value and startup path quickly.
- ADRs reduce repeated "why did we do this?" discussions.
- A runbook gives an operator an order of operations under pressure.

### Failure modes to watch

- The answer is "it is somewhere in the wiki."
- There is no owner or review date, so readers cannot trust the document.
- The same onboarding question always routes through the same person.

## What to Notice in This Code

- Splitting by intent makes docs findable.
- ADRs make decisions recoverable.
- Runbooks reduce the cost of 3 a.m. incidents.
- The README is both first impression and recruiting tool.

## Five Common Mistakes

1. **Everything in one wiki page.** Nobody finds anything.
2. **Auto-generated docs only.** Intent disappears.
3. **Mixed tense.** Trust leaks.
4. **Unrehearsed runbooks.** The first run is the real incident.
5. **No doc owner.** It rots into a lie.

## How This Shows Up in Production

Mature teams use docs-as-code (markdown in the repo, change via PR, build in CI). New features ship as RFC -> code -> doc updates inside one PR.

## How a Senior Engineer Thinks

- Documentation is the infrastructure of async collaboration.
- Code is "how"; docs are "why" and "when".
- A repo with a weak README is a future debt.
- Every doc needs an owner and a last_reviewed date.
- Review docs as carefully as code.

## Checklist

- [ ] Are the 5 README blocks present?
- [ ] Do major decisions have ADRs?
- [ ] Do docstrings express usage contracts?
- [ ] Is there an incident runbook?
- [ ] Does every document have an owner?

## Practice Problems

1. Rewrite your repo README into the 5 blocks.
2. Convert one recent decision into an ADR.
3. Write a one-page runbook for your last real incident.

## Wrap-up and Next Steps

Documentation frees people. Next, we look at how those people work together — the collaboration process.

## Answering the Opening Questions

- **What blocks must a good README contain at minimum?**
  This article proposed minimum README blocks: what it changes, why, a 60-second quick start, configuration, and further reading. The extended example added local run/test, deployment path, and frequent ops questions—making project value and entry path visible within the first 5 minutes.
- **What does an ADR record, and how does it differ from code comments?**
  An ADR records `Context, Decision, Alternatives, Consequences`—why a structure was chosen and which alternatives were rejected. Code comments and docstrings explain usage contracts for functions and classes; ADRs preserve decision background and impact scope outside the code.
- **What role do docstrings and type hints play in documentation?**
  Type hints like `compute_invoice(amount: int, tax_rate: float)` reveal the closest contract for expected input/output. When the docstring adds that `ValueError` is raised for negative input, users understand both happy and failure paths immediately upon opening the code.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): Understanding Requirements](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): Design vs Implementation](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): Code Review](./04-code-review.md)
- [Software Engineering 101 (5/10): Testing Strategy](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): Version Control and Release](./06-version-control-and-release.md)
- **Documentation (current)**
- Collaboration Process (upcoming)
- Maintenance and Tech Debt (upcoming)
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Diataxis Framework](https://diataxis.fr/)
- [The Documentation System — Daniele Procida](https://documentation.divio.com/)
- [Write the Docs — Documentation Guide](https://www.writethedocs.org/guide/)
- [Google — Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)

Tags: Computer Science, SoftwareEngineering, Documentation, README, ADR, Knowledge
