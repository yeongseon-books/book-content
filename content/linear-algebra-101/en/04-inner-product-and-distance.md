---
series: linear-algebra-101
episode: 4
title: "Linear Algebra 101 (4/10): Inner Product and Distance"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - LinearAlgebra
  - InnerProduct
  - Distance
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to inner products and distance — dot product, cosine similarity, Euclidean and Manhattan distance with NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (4/10): Inner Product and Distance

Once vectors are in play, the next question comes immediately: how similar are two vectors, and how far apart are they? Recommenders, embedding search, and nearest-neighbor lookups are all versions of that question turned into numbers.

This is the 4th post in the Linear Algebra 101 series. Here we will connect the inner product, cosine similarity, Euclidean distance, and Manhattan distance into one comparison toolkit.


![linear algebra 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/04/04-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 4 flow overview*
> Inner product and distance are the two foundations of vector comparison. Inner product measures directional relationship; distance measures the gap between points. Which you use depends on your problem's nature.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Inner Product and Distance?
- Which signal should the example or diagram make visible for Inner Product and Distance?
- What failure should be prevented first when Inner Product and Distance reaches a real system?

## Questions This Post Answers

- Why does the inner product collapse two vectors into one scalar?
- How does cosine similarity grow out of the inner product?
- What changes when you compare Euclidean distance with Manhattan distance?
- Why are “similar” and “close” not always the same claim?

> The inner product measures directional alignment. Distance measures separation in space. Because the questions differ, the numbers should be read differently too.

## Why It Matters

Document embeddings often care about direction, which is why cosine similarity shows up everywhere. Coordinate differences, travel costs, and physical displacement often care about actual gap size, where Euclidean or Manhattan distance can be a better fit.

Without that distinction, metric choice becomes habit instead of judgment. You start using cosine everywhere or L2 everywhere, even though search rankings, clusters, and neighbor sets can shift dramatically when the metric changes. This chapter is about choosing the comparison question, not memorizing one more formula.

## Key Terms

- **Inner product**: `v . w = sum(v_i * w_i)` — a *scalar*.
- **Cosine similarity**: `(v . w) / (||v|| ||w||)` — compares *direction only*.
- **Orthogonal**: `v . w = 0` — *perpendicular*.
- **Euclidean distance**: `||v - w||` — *straight-line distance*.
- **Manhattan distance**: `sum(|v_i - w_i|)` — *grid distance*.

## Before/After

**Before**: *"Inner product is just multiply and add."*

**After**: *"Inner product measures *alignment*; *cosine* gives *directional similarity*."*

## Hands-on: Five Steps with Inner Product and Distance

### Step 1 — Prepare vectors

```python
import numpy as np
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])
```

### Step 2 — Inner product

```python
print("v . w:", np.dot(v, w))
print("v . w:", v @ w)
```

### Step 3 — Cosine similarity

```python
cos_sim = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print("cosine similarity:", cos_sim)
```

### Step 4 — Euclidean distance

```python
print("Euclidean:", np.linalg.norm(v - w))
```

### Step 5 — Manhattan distance

```python
print("Manhattan:", np.sum(np.abs(v - w)))
```

## Read One Numeric Pass

- `v @ w` is `32.0`, so one scalar is already summarizing how strongly the two vectors align.
- Cosine similarity is about `0.975`, which tells you the directions are close even before you look at raw distance.
- Euclidean distance is about `5.196`, while Manhattan distance is `9.0`. Same vectors, different question, different number.

## What to Notice in This Code

- The *inner product* reflects both *direction and magnitude*.
- *Cosine similarity* reflects only *direction* — *scale-invariant*.
- *Distance* is *dissimilarity* — *smaller means closer*.

## Five Common Mistakes

1. **Confusing *inner product* with *element-wise product*.**
2. **Forgetting to *normalize* before computing *cosine similarity*.**
3. **Computing the *cosine* of a *zero vector* — *division by zero*.**
4. **Ignoring the *geometric difference* between *Euclidean* and *Manhattan*.**
5. **Forgetting that *distance intuition breaks down in high dimensions* (curse of dimensionality).**

## How This Shows Up in Production

Recommenders (*item similarity*), vector databases (*ANN search*), NLP (*embedding similarity*), clustering (*KMeans*) — all run on *inner products and distances*.

## How a Senior Engineer Thinks

- Choose *cosine vs L2* deliberately.
- Knows that *distance intuition fails in high dimensions*.
- Knows that *normalize-then-dot equals cosine*.
- Sees that *metric choice drives model behavior*.
- Picks *vector database indexes* carefully.

## Checklist

- [ ] You can compute the *inner product*.
- [ ] You can compute *cosine similarity*.
- [ ] You know the difference between *Euclidean* and *Manhattan*.
- [ ] You understand *orthogonality*.

## Practice Problems

1. Compute the *inner product* of `v = [1, 0]` and `w = [0, 1]` and confirm they are *orthogonal*.
2. Build pairs of vectors with *cosine similarity* equal to *1, 0, -1*.
3. Build an example where *Euclidean* and *Manhattan* distances differ.

## Wrap-up and Next Steps

Inner product is *similarity*; distance is *dissimilarity*. The next post covers *linear transformations*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Inner Product and Distance?**
  - The article treats Inner Product and Distance as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Inner Product and Distance?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Inner Product and Distance reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- **Inner Product and Distance (current)**
- Linear Transformations (upcoming)
- Basis and Dimension (upcoming)
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Dot products](https://www.3blue1brown.com/lessons/dot-products)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)
- [scikit-learn — Pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html)
- [Khan Academy — Dot and cross products](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces/dot-cross-products)

Tags: LinearAlgebra, InnerProduct, Distance, DataScience, Beginner
