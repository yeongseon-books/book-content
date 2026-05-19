---
series: math-for-cs-101
episode: 9
title: Information Theory
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
  - InformationTheory
  - Entropy
  - Compression
  - Beginner
seo_description: A beginner-friendly tour of bits, entropy, cross entropy, KL divergence, Shannon, and compression intuition for CS
last_reviewed: '2026-05-04'
---

# Information Theory

To understand why compression works, why cross entropy appears in classifier loss functions, or why language-model perplexity drops when predictions improve, you need a common concept underneath all three. That concept is information theory.

Information theory treats information as something measurable instead of something merely descriptive. It lets you ask how surprising an event is, how uncertain a distribution is, and how far a predictive distribution is from the real one, all in a shared quantitative language.

This is post 9 in the Math for CS 101 series.

Here we connect information content, entropy, cross entropy, KL divergence, and compression limits into one mental model.

## Questions this chapter answers

- What does it mean to measure information in bits?
- Why is entropy called average information content?
- Why is cross entropy so common as an ML loss function?
- What does KL divergence reveal that entropy alone does not?
- How does information theory tell us both what is possible and what is impossible in compression?

> Information theory measures uncertainty in bits. That is why it can connect compression, communication, and predictive modeling without changing languages.

## Why It Matters

Classifier losses, communication codes, compression formats, and language-model evaluation all rely on information-theoretic ideas. The formulas differ by domain, but the underlying questions are similar: how surprising is this event, how uncertain is this source, and how expensive is it to encode reality with the wrong distribution?

Once you see that connection, entropy stops feeling like a standalone definition. It becomes the lower-level quantity that explains why common messages should be short, rare messages should be long, and wrong probability models get penalized.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/09/09-01-concept-at-a-glance.en.png)
*Information theory links distributional uncertainty to coding cost, model loss, and the floor that compression cannot cross.*

## Key Terms

- **bit**: a *binary* unit.
- **entropy**: *average information content*.
- **cross entropy**: cost of coding *truth* with *predictions*.
- **KL divergence**: a *distance* between distributions.
- **compression**: bounded *below* by entropy.

## Before/After

**Before**: every message gets the *same length*.

**After**: *common* messages short, *rare* ones long.

## Hands-on: Mini Information Kit

### Step 1 — Information Content

```python
import math

def info(p):
    return -math.log2(p)
```

### Step 2 — Entropy

```python
def entropy(probs):
    return sum(-p * math.log2(p) for p in probs if p > 0)
```

### Step 3 — Cross Entropy

```python
def cross_entropy(p, q):
    return sum(-pi * math.log2(qi) for pi, qi in zip(p, q) if qi > 0)
```

### Step 4 — KL Divergence

```python
def kl(p, q):
    return cross_entropy(p, q) - entropy(p)
```

### Step 5 — Average Code Length

```python
def avg_len(probs, lengths):
    return sum(p * L for p, L in zip(probs, lengths))
```

## What to Notice in This Code

- *log2* gives *bits*.
- *KL* is *asymmetric*.
- *Cross entropy* is the standard *loss*.

## Five Common Mistakes

1. **Forgetting to handle *log(0)*.**
2. **Assuming *KL* is *symmetric*.**
3. **Mixing up *entropy* and *cross entropy*.**
4. **Inputs whose *probabilities* do not sum to *1*.**
5. **Confusing *units* (bits vs nats).**

## How This Shows Up in Production

*Classifier loss*, *language model perplexity*, *zip/gzip*, and *ML regularization* all use information theory.

## How a Senior Engineer Thinks

- *Information* is *bits*.
- *Entropy* is the *compression floor*.
- *KL* is *distributional distance*.
- *Loss* is *cross entropy*.
- *Models* estimate *distributions*.

## Checklist

- [ ] Verify *probabilities sum to 1*.
- [ ] Guard *log(0)*.
- [ ] State the *units*.
- [ ] State the *direction* of *KL*.

## Practice Problems

1. Define *entropy* in one line.
2. Define *KL divergence* in one line.
3. Define *cross entropy* in one line.

## Wrap-up and Next Steps

Information theory gives you a way to read surprise, uncertainty, and coding cost as parts of the same system. That makes compression, language modeling, and classification losses much easier to interpret.

Next, we close the series by tying these mathematical tools back into algorithm design as one capstone view.

<!-- toc:begin -->
- [Why Math for CS](./01-why-math-for-cs.md)
- [Logic and Proofs](./02-logic-and-proofs.md)
- [Sets and Functions](./03-sets-and-functions.md)
- [Graphs](./04-graphs.md)
- [Combinatorics](./05-combinatorics.md)
- [Probability](./06-probability.md)
- [Linear Algebra](./07-linear-algebra.md)
- [Calculus](./08-calculus.md)
- **Information Theory (current)**
- Algorithms and Math (upcoming)
<!-- toc:end -->

## References

- [Information Theory - Stanford Encyclopedia](https://plato.stanford.edu/entries/information-theory/)
- [A Mathematical Theory of Communication - Shannon](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [Elements of Information Theory - Cover and Thomas](https://www.wiley.com/en-us/Elements+of+Information+Theory%2C+2nd+Edition-p-9780471241959)
- [SciPy Stats Entropy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html)
- [SciPy GitHub repository](https://github.com/scipy/scipy)

Tags: Math, InformationTheory, Entropy, Compression, Beginner
