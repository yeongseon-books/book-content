---
series: probability-101
episode: 2
title: "Probability 101 (2/10): Events and Sample Space"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Probability
  - SampleSpace
  - Events
  - SetTheory
  - Beginner
seo_description: Learn how sample spaces and events turn probability questions into set problems, with unions, intersections, complements, and code examples.
last_reviewed: '2026-05-15'
---

# Probability 101 (2/10): Events and Sample Space

People often miss probability questions not because the arithmetic is hard, but because they start from a vague picture of the problem. If you jump straight to the calculation without writing down all possible outcomes, two people can read the same sentence and quietly solve two different problems.

In probability, the sample space and the event are closer to grammar than to decoration. If that grammar is shaky, the final number can look clean while meaning something else entirely.

This is the 2nd post in the Probability 101 series. Here we define sample spaces and events in set language, then use unions, intersections, complements, and independence to show why a careful setup often does half the work for you.


![probability 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/02/02-01-concept-at-a-glance.en.png)
*probability 101 chapter 2 flow overview*
> Events and Sample Space requires both definition and intuition, learned through concrete examples.

## Questions to Keep in Mind

- Why the sample space must come before the probability?
- How events become subsets once the setup is explicit?
- What union, intersection, and complement mean in practice?

## Why It Matters

Many wrong answers in probability come from the wrong sample space. If you treat (1,6) and (6,1) as the same outcome in one step and different outcomes in the next, everything after that can be numerically tidy and conceptually wrong.

Once the sample space is explicit, many probability problems turn into set problems. Events become subsets. “A or B” becomes a union. “A and B” becomes an intersection. That shift makes the structure of the problem much more stable.

> In many probability problems, the moment you write down the sample space carefully, half the solution is already visible.

## Key Terms

- **Sample space Ω**: the set of all outcomes.
- **Event A**: a subset of Ω.
- **Union A∪B**: A or B.
- **Intersection A∩B**: A and B.
- **Complement Aᶜ**: not A.
- **Mutually exclusive**: A∩B = ∅.
- **Independent**: P(A∩B) = P(A)·P(B).

## Before / After

**Before**: “What is the probability that the sum of two dice is even?” The question feels simple, but the setup is often left implicit.

**After**: Ω = {(i,j) : 1≤i,j≤6} gives 36 ordered outcomes, A = {sum is even} gives 18 of them, so the answer is 18/36 = 1/2.

## Hands-on: 5-step Events

### Step 1 — Sample space

```python
omega = [(i, j) for i in range(1, 7) for j in range(1, 7)]
print(len(omega))  # 36
```

### Step 2 — Define events

```python
A = [o for o in omega if (o[0] + o[1]) % 2 == 0]   # even sum
B = [o for o in omega if o[0] == o[1]]              # doubles
```

### Step 3 — Union and intersection

```python
union = list(set(A) | set(B))
inter = list(set(A) & set(B))
print(len(union), len(inter))
```

### Step 4 — Complement

```python
not_A = [o for o in omega if o not in A]
print(len(A) + len(not_A))  # 36
```

### Step 5 — Check independence

```python
def P(E): return len(E) / len(omega)
print("indep?", round(P(set(A) & set(B)) - P(A) * P(B), 6))
```

## What to Notice in This Code

- Stating Ω explicitly turns probability into set arithmetic.
- Mutually exclusive ≠ independent — a frequent confusion.
- A fair die assumption means uniform probability.

## Five Common Mistakes

1. **Computing without writing Ω.**
2. **Mixing up mutually exclusive and independent.**
3. **Mixing ordered and unordered outcomes.**
4. **Ignoring with- vs without-replacement draws.**
5. **Failing to state symmetry assumptions.**

## How This Shows Up in Production

A/B test group definitions, fraud-detection rule events, search-evaluation relevance events — defining the event set is the starting point of every metric.

## How a Senior Engineer Thinks

- Always writes Ω.
- Reasons in set operations.
- Distinguishes independent and mutually exclusive.
- States symmetry assumptions.
- Verifies with code.

## Checklist

- [ ] I can define Ω.
- [ ] I know union/intersection/complement.
- [ ] I separate mutually exclusive from independent.
- [ ] I verify with a simulation.

## Practice Problems

1. Write the sample space of a card draw (52) and find P(face card).
2. Give an example that is mutually exclusive but not independent.
3. Show the size difference between ordered and unordered sampling spaces.

## Wrap-up and Next Steps

Sample spaces and events are the grammar of probability. The next episode covers conditional probability — what changes when we are given new information.

## Answering the Opening Questions

- **Why the sample space must come before the probability?**
  - The article treats Events and Sample Space as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How events become subsets once the setup is explicit?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What union, intersection, and complement mean in practice?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- **Events and Sample Space (current)**
- Conditional Probability (upcoming)
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Sample spaces](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Wikipedia — Event (probability theory)](https://en.wikipedia.org/wiki/Event_(probability_theory))
- [Wikipedia — Sample space](https://en.wikipedia.org/wiki/Sample_space)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, SampleSpace, Events, SetTheory, Beginner
