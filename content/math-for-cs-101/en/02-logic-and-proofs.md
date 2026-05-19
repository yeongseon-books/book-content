---
series: math-for-cs-101
episode: 2
title: Logic and Proofs
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - Logic
  - Proof
  - Boolean
  - Beginner
seo_description: A beginner-friendly tour of propositions, truth tables, implication, direct proof, contradiction, induction, and counterexamples
last_reviewed: '2026-05-04'
---

# Logic and Proofs

Developers make logical claims all the time: this condition is sufficient, that state transition is safe, and this algorithm stays correct for every valid input. At first you can test a few examples and move on, but important logic eventually demands a stronger explanation.

As the number of branches and state transitions grows, writing more tests alone is not enough. You also need a clean way to separate the claim itself, the assumptions behind it, and the counterexamples that would invalidate it.

This is post 2 in the Math for CS 101 series.

Here we treat logic and proof as a practical grammar for explaining correctness in code, not as an isolated math ritual.

## Questions this chapter answers

- How is a proof different from running a handful of examples?
- How do propositions, implication, and equivalence map to real code?
- When is a direct proof clearer than proof by contradiction?
- Why does induction feel so close to loop reasoning?
- Why is a single counterexample often enough to overturn a broad claim?

> Logic gives you the grammar for true and false statements. Proof turns that grammar into a disciplined way to explain why an algorithm or program behavior should hold in all relevant cases.

## Why It Matters

A test checks specific cases. A proof targets the whole claim. Those two tools are complementary, but they are not interchangeable. Three passing examples do not establish correctness for every `n`, every input ordering, or every edge case.

That distinction matters far beyond textbook exercises. Type systems encode logical constraints on values. Consensus algorithms try to preserve safety under specific failure assumptions. Authentication and authorization flows become fragile when the logic between conditions is vague.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/02/02-01-concept-at-a-glance.en.png)
*Logic organizes the claim, and proof chooses the route from assumption to conclusion: direct reasoning, contradiction, or induction.*

## Key Terms

- **proposition**: a *true/false* statement.
- **implication**: `p → q`.
- **direct proof**: from *premise* to *conclusion*.
- **contradiction**: assume the *opposite*, derive a *contradiction*.
- **induction**: *base case* plus *inductive step*.

## Before/After

**Before**: conclude *correct* from *three examples*.

**After**: prove for *all n* by *mathematical induction*.

## Hands-on: A Tiny Proof Kit

### Step 1 — Truth table

```python
def truth_imply():
    return [(p, q, (not p) or q) for p in (False, True) for q in (False, True)]
```

### Step 2 — Equivalence

```python
def equiv(p, q):
    return p == q
```

### Step 3 — Direct proof sketch

```python
def even_sum(a, b):
    assert a % 2 == 0 and b % 2 == 0
    return (a + b) % 2 == 0
```

### Step 4 — Contradiction sketch

```python
def assume_not(claim):
    return f"suppose not {claim}, derive contradiction"
```

### Step 5 — Induction

```python
def sum_to(n):
    return n * (n + 1) // 2
```

## What to Notice in This Code

- *Implication* is `not p or q`.
- The *sum* of *even* numbers is *even*.
- The *sum* formula is a *closed form*.

## Five Common Mistakes

1. **Replacing a *proof* with *examples*.**
2. **Confusing *implication* with its *converse*.**
3. **Skipping the *base case* in induction.**
4. **One *counterexample* is *disproof*.**
5. **Following *symbols* without grasping *meaning*.**

## How This Shows Up in Production

*Compiler* type checkers and *distributed* consensus algorithms are validated via *formal proofs*.

## How a Senior Engineer Thinks

- *Proof* is *documentation*.
- *Counterexamples* are *friends*.
- *Induction* is the cousin of a *loop*.
- *Equivalence* is a *refactoring* tool.
- *Implication* is a *guard*.

## Checklist

- [ ] Build a *truth table*.
- [ ] Distinguish *implication*, *converse*, *contrapositive*.
- [ ] Verify the *base case*.
- [ ] Hunt for *counterexamples*.

## Practice Problems

1. Define *implication* in one line.
2. Define *contradiction* in one line.
3. Define *induction* in one line.

## Wrap-up and Next Steps

Logic and proofs give you a way to explain correctness instead of only hoping repeated examples are representative. Once you can separate assumptions, implications, and counterexamples, design reviews become far more precise.

Next, we move into sets and functions, where that logical precision starts shaping data boundaries and transformation rules.

<!-- toc:begin -->
- [Why Math for CS](./01-why-math-for-cs.md)
- **Logic and Proofs (current)**
- Sets and Functions (upcoming)
- Graphs (upcoming)
- Combinatorics (upcoming)
- Probability (upcoming)
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)
<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications - Rosen](https://en.wikipedia.org/wiki/Discrete_Mathematics_and_Its_Applications)
- [How to Prove It - Velleman](https://www.cambridge.org/core/books/how-to-prove-it/)
- [Mathematical Induction - Khan Academy](https://www.khanacademy.org/math/precalculus/x9e81a4f98389efdf:series/x9e81a4f98389efdf:induction/v/proof-by-induction)
- [Logic in Computer Science - Huth, Ryan](https://www.cambridge.org/core/books/logic-in-computer-science/)
- [Z3 Theorem Prover GitHub repository](https://github.com/Z3Prover/z3)

Tags: Math, Logic, Proof, Boolean, Beginner
