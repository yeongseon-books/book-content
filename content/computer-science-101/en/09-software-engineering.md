---
series: computer-science-101
episode: 9
title: "Computer Science 101 (9/10): Software Engineering"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Software Engineering
  - Testing
  - Version Control
  - Code Review
  - Refactoring
seo_description: Coding vs software engineering — covered through testing, version control, code review, and refactoring in the CS 101 series.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (9/10): Software Engineering

There is a big difference between a script that runs once for you and a system that many people can keep changing for years. Software engineering is the set of habits that preserves “still works” while time passes, teammates change, and requirements shift.

This is post 9 in the Computer Science 101 series.

In this article, we'll use testing, version control, code review, and refactoring to show where coding turns into engineering.


![Computer Science 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/09/09-01-concept-at-a-glance.en.png)
*Computer Science 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Software Engineering?
- Which signal should the example or diagram make visible for Software Engineering?
- What failure should be prevented first when Software Engineering reaches a real system?

## Questions This Article Answers

- What separates coding from software engineering in practice?
- Why are tests the minimum safety mechanism for change?
- What habits make a Git-based workflow sustainable for a team?
- Why should refactoring be managed separately from feature work?
- What happens to speed and quality when technical debt accumulates?

## What You Will Learn

- The difference between coding and software engineering
- The effect tests have on code quality
- A Git-based collaboration model
- Refactoring and managing technical debt

## Why It Matters

The ability to write code that works will plateau by year five. The same code has to be kind to your future self and your teammates, and it must not break under change. Engineering habits — tests, reviews, small commits, clear names — make the difference.

> Code is written once and read a hundred times.

Good code is not the code that's quickest to write today; it's the code that's easiest to change for years.

> Engineering is the activity of guaranteeing "still works tomorrow" on top of "works today."

## Key Terms

| Term | Description |
| --- | --- |
| Unit test | Verifies that a small unit (function/class) behaves as intended |
| Version control | A system that tracks code history and enables collaboration (Git) |
| Code review | The process where another engineer reads a change and gives feedback |
| Refactoring | A change that improves internal structure while preserving external behavior |
| CI/CD | Automated build, test, and deploy pipelines |
| Technical debt | The accumulated cost of structural improvements deferred for short-term convenience |

## Before / After

**Before — a function written without tests:**

```python
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    elif user_type == "member":
        return price * 0.9
    else:
        return price
# You don't know which input will break it until production calls it
```

**After — a function whose behavior is specified by tests:**

```python
# discount.py
def calc_discount(price: float, user_type: str) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    rates = {"vip": 0.7, "member": 0.9}
    return price * rates.get(user_type, 1.0)

# test_discount.py
import pytest
from discount import calc_discount

def test_vip_gets_30_percent_off():
    assert calc_discount(100, "vip") == 70

def test_member_gets_10_percent_off():
    assert calc_discount(100, "member") == 90

def test_unknown_user_type_pays_full_price():
    assert calc_discount(100, "guest") == 100

def test_negative_price_raises():
    with pytest.raises(ValueError):
        calc_discount(-1, "vip")
```

## Hands-On: Step by Step

### Step 1: Your first test with pytest

```bash
# In a virtual environment
pip install pytest

# Place the two files above in the same folder and run
pytest -v
```

**Expected output:** all four tests should pass, giving you a baseline that you can rerun after a refactor to confirm behavior stayed the same.

### Step 2: Use regression tests to keep bugs from coming back

```python
# When you find a bug, first write a test that reproduces it
def test_zero_price_returns_zero():
    """A 0-priced item bought by a VIP must still be 0 (was broken in a previous version)."""
    assert calc_discount(0, "vip") == 0
```

### Step 3: A Git workflow

```bash
# Create a new feature branch
git checkout -b feature/discount-vip

# Work and commit in small units
git add discount.py test_discount.py
git commit -m "feat: add VIP discount tier"

# Push and open a PR
git push origin feature/discount-vip
# Open a Pull Request on GitHub/GitLab
```

### Step 4: Refactoring — same behavior, better structure

```python
# Before: the function grows every time a new tier is added
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    if user_type == "member":
        return price * 0.9
    if user_type == "student":
        return price * 0.85
    return price

# After: pulled out into a data table — adding a tier is one line
DISCOUNT_RATES = {
    "vip":     0.70,
    "member":  0.90,
    "student": 0.85,
}

def calc_discount(price: float, user_type: str) -> float:
    return price * DISCOUNT_RATES.get(user_type, 1.0)

# If the same tests still pass, this is a safe refactor
```

### Step 5: A simple CI setup (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest
      - run: pytest -v
```

## Notable Points in This Code

- With tests, refactoring stops being scary.
- Small commits with clear messages are letters to your future self.
- Expressing branching as data shortens functions and makes change easy.
- CI handles the verification a human will eventually forget to run.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| "I'll add tests later" | They never get added; regressions show up | At least one test alongside every new feature |
| One huge commit | Impossible to review, hard to revert | Small, frequent commits per logical unit |
| Pushing straight to main without review | Human errors accumulate | PRs with at least one approver |
| Leaving "temporary" TODOs forever | Tech debt piles up | Each TODO carries an issue ID and a deadline |
| Trying to write every line perfectly | Late releases, over-engineering | YAGNI — only what's needed now |

## How This Is Used in Practice

- CI that runs lint, type check, and tests automatically on every change.
- PR templates that capture intent and impact area of the change.
- A unified branching strategy — trunk-based development or Git Flow.
- Feature flags for partial rollouts and instant rollbacks.
- Regular refactoring sprints to repay technical debt.

## How a Senior Engineer Thinks

A senior engineer spends more time reading and polishing code than writing it. They clean up existing code before adding a feature, and they become the first reviewer of their own PR before opening it. The yardstick is: "Will the teammate who reads this in six months be angry?"

They also value changeability over perfection. Rather than designing for every possible future, they ship something small and make it easy to fix quickly. Tests and reviews are the safety net that makes that fixing safe.

## Checklist

- [ ] I add a test whenever I add a new function
- [ ] My commit messages tell — in one line — what changed and why
- [ ] I read other people's PRs honestly and give real feedback
- [ ] I consider refactoring when I see the same code twice
- [ ] I belong to a team where a broken CI is fixed immediately

## Practice Problems

1. Add a new tier (`partner`, 80% discount) to `calc_discount` above and write tests for it.

2. Pick an old function of yours over 50 lines long and refactor it by extracting functions and improving names — keeping behavior identical. Verify with tests.

3. Build a GitHub Actions workflow that runs `pytest` and `ruff` in parallel, and surfaces both results on the PR.

## Wrap-Up and Next Steps

Software engineering is the practice of writing code that survives time. Tests are the safety net for change, version control is the foundation of collaboration, review is the quality gate, and refactoring is the prescription for technical debt. The difference in great engineers is not the speed of writing new code; it's the willingness to touch old code without fear.

The next article ties everything together — how all of this CS foundation feeds into AI and data science, and what to study next.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Software Engineering?**
  - The article treats Software Engineering as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Software Engineering?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Software Engineering reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): Data Representation](./03-data-representation.md)
- [Computer Science 101 (4/10): Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): Computer Architecture](./05-computer-architecture.md)
- [Computer Science 101 (6/10): Operating Systems](./06-operating-systems.md)
- [Computer Science 101 (7/10): Networks](./07-networks.md)
- [Computer Science 101 (8/10): Databases](./08-databases.md)
- **Software Engineering (current)**
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [The Pragmatic Programmer — David Thomas, Andrew Hunt](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [pytest — Documentation](https://docs.pytest.org/)
- [Pro Git — Scott Chacon (free)](https://git-scm.com/book/en/v2)

Tags: Computer Science, Software Engineering, Testing, Version Control, Code Review, Refactoring
