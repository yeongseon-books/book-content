---
series: math-for-cs-101
episode: 5
title: "Math for CS 101 (5/10): Combinatorics"
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
  - Combinatorics
  - Counting
  - Probability
  - Beginner
seo_description: A beginner-friendly tour of product rule, sum rule, permutations, combinations, pigeonhole principle, and binomial coefficients
last_reviewed: '2026-05-04'
---

# Math for CS 101 (5/10): Combinatorics

If you want to explain why an algorithm suddenly becomes too slow, why test cases explode, or why collisions become unavoidable, you end up counting possibilities. The problem is that real systems produce too many cases to enumerate by hand.

Combinatorics is what lets you count without listing everything. Once you know whether order matters, whether repetition is allowed, and whether choices are independent or exclusive, the structure often tells you how to count.

This is post 5 in the Math for CS 101 series.

Here we treat combinatorics as the language of counting behind complexity and probability, not as a bag of disconnected formulas.

## Questions to Keep in Mind

- Why can we count accurately without enumerating every case?
- When should you use the product rule versus the sum rule?
- What is the practical difference between permutations and combinations?

## Big Picture

![math for cs 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/05/05-01-concept-at-a-glance.en.png)

*math for cs 101 chapter 5 flow overview*

This picture places Combinatorics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Combinatorial counting becomes essential the moment you face an exponential search space; it shifts you from guessing to systematic enumeration.

## Why It Matters

Complexity analysis, probability, collision analysis, and test generation all depend on counting. If you underestimate the size of the possibility space, you can choose an algorithm that already fails before optimization begins.

The useful habit is to ask structural questions first: does order matter, is repetition allowed, and are the choices independent? Those questions matter more than memorizing a formula in isolation.


## Concept at a Glance

Combinatorics counts *possibilities* systematically: permutations (order matters), combinations (order does not), and recurrence relations (recursive structure).

## Before/After

**Before**: Try all possibilities and hope the search finishes.

**After**: Calculate the bounds and decide if brute force is even viable.

## Key Terms

- **product rule**: multiply *sequential* choices.
- **sum rule**: add *exclusive* choices.
- **permutation**: *ordered* arrangement.
- **combination**: *unordered* selection.
- **pigeonhole**: *n+1* items in *n* boxes force a *collision*.

## Before/After

**Before**: enumerate every case by hand.

**After**: apply a *formula* in *constant time*.

## Hands-on: Mini Counting Kit

### Step 1 — Factorial

```python
def fact(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r
```

### Step 2 — Permutations

```python
def nPr(n, r):
    return fact(n) // fact(n - r)
```

### Step 3 — Combinations

```python
def nCr(n, r):
    return fact(n) // (fact(r) * fact(n - r))
```

### Step 4 — Pigeonhole Check

```python
def pigeon(items, holes):
    return items > holes
```

### Step 5 — Binomial Row

```python
def row(n):
    return [nCr(n, k) for k in range(n + 1)]
```

## What to Notice in This Code

- *Factorial* is the reusable building block.
- *nCr* is *symmetric*: (n,r) = (n,n-r).
- *Pigeonhole* is one inequality.

## Five Common Mistakes

1. **Confusing *permutations* and *combinations*.**
2. **Forgetting whether *repetition* is allowed.**
3. **Forgetting *0! = 1*.**
4. **Calling *factorial* directly on *huge n*.**
5. **Using *=* instead of *>* in pigeonhole.**

## How This Shows Up in Production

*A/B test bucketing*, *hash collision analysis*, *dataset sampling*, and *combinatorial explosion* checks all use these tools.

## How a Senior Engineer Thinks

- *Counting* is *modeling*.
- *Principles* over *formulas*.
- *Pigeonhole* proves *existence*.
- *Binomial* connects to *probability*.
- Watch for *combinatorial explosion*.

## Checklist

- [ ] Decide if *order matters*.
- [ ] Decide if *repetition* is allowed.
- [ ] Replace enumeration with a *formula*.
- [ ] Inspect *edge cases*.

## Practice Problems

1. State the difference between *nPr* and *nCr* in one line.
2. State *pigeonhole* in one line.
3. Why is *0! = 1*?

## Wrap-up and Next Steps

Combinatorics teaches you to read possibility spaces structurally instead of by brute force. That shift is what makes complexity analysis and probability feel connected instead of separate topics.

Next, we continue into probability, where counting becomes a way to reason about uncertainty instead of certainty alone.

## Answering the Opening Questions

- **Why can we count accurately without enumerating every case?**
  - The article treats Combinatorics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **When should you use the product rule versus the sum rule?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What is the practical difference between permutations and combinations?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- **Combinatorics (current)**
- Probability (upcoming)
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Combinatorics - Wolfram MathWorld](https://mathworld.wolfram.com/Combinatorics.html)
- [Counting - Khan Academy](https://www.khanacademy.org/math/statistics-probability/counting-permutations-and-combinations)
- [Concrete Mathematics - Graham, Knuth, Patashnik](https://www-cs-faculty.stanford.edu/~knuth/gkp.html)
- [Python math.comb Documentation](https://docs.python.org/3/library/math.html#math.comb)
- [SymPy GitHub repository](https://github.com/sympy/sympy)

Tags: Math, Combinatorics, Counting, Probability, Beginner
