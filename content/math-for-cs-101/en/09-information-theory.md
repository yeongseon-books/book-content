---
series: math-for-cs-101
episode: 9
title: "Math for CS 101 (9/10): Information Theory"
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

# Math for CS 101 (9/10): Information Theory

To understand why compression works, why cross entropy appears in classifier loss functions, or why language-model perplexity drops when predictions improve, you need a common concept underneath all three. That concept is information theory.

Information theory treats information as something measurable instead of something merely descriptive. It lets you ask how surprising an event is, how uncertain a distribution is, and how far a predictive distribution is from the real one, all in a shared quantitative language.

This is the 9th post in the Math for CS 101 series.

Here we connect information content, entropy, cross entropy, KL divergence, and compression limits into one mental model.


![math for cs 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/09/09-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 9 flow overview*
> Entropy and information measure the theoretical limits of communication, compression, and storage; they set the boundaries of what is possible.

## Questions to Keep in Mind

- What does it mean to measure information in bits?
- Why is entropy called average information content?
- Why is cross entropy so common as an ML loss function?

## Why It Matters

Classifier losses, communication codes, compression formats, and language-model evaluation all rely on information-theoretic ideas. The formulas differ by domain, but the underlying questions are similar: how surprising is this event, how uncertain is this source, and how expensive is it to encode reality with the wrong distribution?

Once you see that connection, entropy stops feeling like a standalone definition. It becomes the lower-level quantity that explains why common messages should be short, rare messages should be long, and wrong probability models get penalized.

Information theory measures *entropy* (uncertainty), *mutual information* (shared knowledge), and compression ratios. It defines what is theoretically possible.

## Before/After

**Before**: "Compress this data as much as you can."

**After**: "The Shannon limit sets an absolute lower bound; anything better is impossible.

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

## Answering the Opening Questions

- **What measures the quantity of information?**
  - This article defined a single event's information as `-log2(p)`, measured in bits. In `info(p)`, lower-probability events yield larger values—capturing the intuition that rare events are more surprising, expressed as a number.
- **Why is entropy called average information?**
  - Entropy weights each event's information by its probability and sums—representing the distribution's average surprise. Comparing `entropy([0.5, 0.5])` vs. `entropy([0.9, 0.1])` for fair vs. biased coins, plus Huffman/zlib compression experiments, showed that entropy equals the lower bound on average code length.
- **Why is cross-entropy so commonly used as a loss function?**
  - Cross-entropy is the average extra cost of describing true distribution `p` using model distribution `q`—so cost grows as predictions worsen. The article's `H(p, q) = H(p) + KL(p||q)` relationship and `target`/`model_good`/`model_bad` examples explained that minimizing cross-entropy is ultimately reducing KL divergence to push the model distribution toward the true one.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- [Math for CS 101 (5/10): Combinatorics](./05-combinatorics.md)
- [Math for CS 101 (6/10): Probability](./06-probability.md)
- [Math for CS 101 (7/10): Linear Algebra](./07-linear-algebra.md)
- [Math for CS 101 (8/10): Calculus](./08-calculus.md)
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
