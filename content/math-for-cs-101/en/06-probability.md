---
series: math-for-cs-101
episode: 6
title: "Math for CS 101 (6/10): Probability"
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
  - Probability
  - Statistics
  - Bayes
  - Beginner
seo_description: A beginner-friendly tour of sample space, events, conditional probability, Bayes theorem, expectation, and variance
last_reviewed: '2026-05-04'
---

# Math for CS 101 (6/10): Probability

Engineering work is full of uncertainty. Was that A/B test result luck or a real signal? Is a false positive rate acceptable? How likely is a failure pattern to repeat? If you do not have a probability model, those questions often collapse into intuition dressed up as confidence.

Probability does not eliminate uncertainty. It gives you a structured way to compare and update beliefs under uncertainty. Once you separate the possible outcomes, the event you care about, and the conditions already known, fuzzy judgment becomes something you can reason about.

This is post 6 in the Math for CS 101 series.

Here we use probability as the language for uncertainty in engineering decisions, connecting sample spaces, conditional probability, Bayes updates, expectation, and variance.


![math for cs 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/06/06-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 6 flow overview*
> Probability lets you stop hand-waving about uncertainty and instead reason quantitatively about expectations and distributions.

## Questions to Keep in Mind

- How do you turn uncertainty into a model instead of a vague guess?
- What is the difference between a sample space and an event?
- Why is conditional probability really about changing the denominator world?

## Why It Matters

A/B testing, recommendation ranking, classifier evaluation, and reliability work all rely on probability. Without the model, the numbers are still there, but the interpretation is shaky because the conditions behind the numbers stay hidden.

The main habit is to ask what world the denominator describes. Many practical mistakes in probability are not bad multiplication. They are failures to notice that the conditioning changed the space you are talking about.

Probability quantifies *likelihood* through events, conditional probabilities, distributions, and Bayes' theorem. It turns vague "probably" into precise numbers.

## Before/After

**Before**: "This might fail sometimes."

**After**: "This fails with probability 0.001 under these assumptions.

## Key Terms

- **sample space**: set of *possible outcomes*.
- **event**: a *subset* of outcomes.
- **conditional**: probability *given* something.
- **Bayes**: update *posterior* from *prior*.
- **expectation**: *average* outcome.

## Before/After

**Before**: guess by intuition.

**After**: quantify with a *formula*.

## Hands-on: Mini Probability Kit

### Step 1 — Probability

```python
def prob(favorable, total):
    return favorable / total
```

### Step 2 — Conditional

```python
def cond(p_a_and_b, p_b):
    return p_a_and_b / p_b
```

### Step 3 — Bayes

```python
def bayes(p_b_given_a, p_a, p_b):
    return p_b_given_a * p_a / p_b
```

### Step 4 — Expectation

```python
def expect(values, probs):
    return sum(v * p for v, p in zip(values, probs))
```

### Step 5 — Variance

```python
def variance(values, probs):
    mu = expect(values, probs)
    return sum(p * (v - mu) ** 2 for v, p in zip(values, probs))
```

## What to Notice in This Code

- Probabilities *sum to 1*.
- Conditional is a *division*.
- Expectation is a *weighted average*.

## Five Common Mistakes

1. **Overusing the *independence* assumption.**
2. **Setting a *prior* to zero in Bayes.**
3. **Confusing *expectation* with *mode*.**
4. **Forgetting the *denominator zero* case.**
5. **Confusing *variance* with *standard deviation*.**

## How This Shows Up in Production

*Spam filters (Bayes)*, *ranking scores*, *SLA breach probabilities*, and *A/B test confidence intervals* all use probability.

## How a Senior Engineer Thinks

- Every estimate is a *distribution*.
- *Bayes* is an *update* procedure.
- *Expectation* drives decisions.
- *Variance* is *risk*.
- *Independence* is just an assumption.

## Checklist

- [ ] Define the *sample space*.
- [ ] Separate *events* clearly.
- [ ] State the *conditioning*.
- [ ] Validate *distributional* assumptions.

## Practice Problems

1. Define *conditional probability* in one line.
2. Write *Bayes theorem* in one line.
3. State the difference between *expectation* and *variance*.

## Wrap-up and Next Steps

Probability gives you a way to reason about uncertainty without pretending that uncertainty disappears. Once you can describe events, conditions, priors, averages, and spread clearly, many engineering discussions become less emotional and more precise.

Next, we move into linear algebra, where the focus shifts from uncertainty to representing data and transformations in a compact form.

## Answering the Opening Questions

- **How do you turn uncertainty into a model instead of a vague guess?**
  - The article treats Probability as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What is the difference between a sample space and an event?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why is conditional probability really about changing the denominator world?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- [Math for CS 101 (5/10): Combinatorics](./05-combinatorics.md)
- **Probability (current)**
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Probability - Khan Academy](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Bayes Theorem - Stanford Encyclopedia](https://plato.stanford.edu/entries/bayes-theorem/)
- [Introduction to Probability - Blitzstein](https://projects.iq.harvard.edu/stat110)
- [Python statistics Module](https://docs.python.org/3/library/statistics.html)
- [SciPy GitHub repository](https://github.com/scipy/scipy)

Tags: Math, Probability, Statistics, Bayes, Beginner
