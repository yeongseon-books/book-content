---
series: linear-algebra-101
episode: 2
title: "Linear Algebra 101 (2/10): Vectors"
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
  - Vectors
  - NumPy
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to vectors — definition, addition, scalar multiplication, norms, and normalization with NumPy code and geometric intuition
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (2/10): Vectors

In machine learning, one row of data is a vector, an embedding is a vector, and a gradient is a vector too. But if you treat vectors as plain number bundles, the calculations may still work while the meaning slips away. A vector is both algebraic notation and a geometric object.

This is the 2nd post in the Linear Algebra 101 series. Here we will read vectors through three lenses at once: coordinates, arrows, and data representations.


![linear algebra 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/02/02-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 2 flow overview*
> A vector is both a container of numbers and the smallest unit of direction in a space. You need both views to connect linear algebra to machine learning.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Vectors?
- Which signal should the example or diagram make visible for Vectors?
- What failure should be prevented first when Vectors reaches a real system?

## Questions This Post Answers

- What makes a vector different from an ordinary list?
- What do vector addition and scalar multiplication mean geometrically?
- Why does a norm mean more than just a length formula?
- When does normalization help, and when can it hide useful information?

> A vector is both a container of numbers and the smallest unit of direction in a space. You need both views to connect linear algebra to machine learning.

## Why It Matters

Feature rows, user embeddings, token embeddings, and gradients are all represented as vectors. Once you can read vectors cleanly, you can move from preprocessing to model internals without switching mental languages.

This matters quickly in practice. Similarity search, normalization, and metric choice all become fragile when you cannot tell whether direction matters, magnitude matters, or both matter. Vectors are the first chapter of linear algebra, but they remain the basic unit all the way to production systems.

## Key Terms

- **Vector**: an *ordered bundle of numbers* — `[x1, x2, ..., xn]`.
- **Dimension**: the *number of entries* in the vector.
- **Norm ||v||**: the *magnitude* — usually *Euclidean length*.
- **Unit vector**: a vector with norm *1*.
- **Scalar multiplication**: changes the *length* and possibly *flips direction*.

## Before/After

**Before**: *"A vector is just a list."* — no geometric meaning.

**After**: *"A vector is a *point/arrow in space*, and *operations are geometric transformations*."*

## Hands-on: Five Steps with Vectors

### Step 1 — Build vectors

```python
import numpy as np
v = np.array([3.0, 4.0])
w = np.array([1.0, 2.0])
print("v:", v, "w:", w)
```

### Step 2 — Addition and subtraction

```python
print("v+w:", v + w)
print("v-w:", v - w)
```

### Step 3 — Scalar multiplication

```python
print("2v:", 2 * v)
print("-v:", -v)
```

### Step 4 — Norm

```python
norm_v = np.linalg.norm(v)
print("||v||:", norm_v)
```

### Step 5 — Normalize to a unit vector

```python
unit_v = v / np.linalg.norm(v)
print("unit v:", unit_v, "norm:", np.linalg.norm(unit_v))
```

## Read One Numeric Pass

- `v + w` becomes `[4., 6.]`, while `v - w` becomes `[2., 2.]`. The coordinate arithmetic is simple, but the geometric meaning is different.
- `||[3, 4]||` is `5.0`, so the familiar 3-4-5 triangle shows up immediately.
- Normalization gives roughly `[0.6, 0.8]`, which keeps direction and forces the norm to 1.

## What to Notice in This Code

- *NumPy* vector operations are *element-wise*.
- The *default norm* is *L2 (Euclidean)*.
- *Normalization* keeps *direction* and forces *length 1*.

## Five Common Mistakes

1. **Relying on *implicit broadcasting* despite *shape mismatch*.**
2. **Normalizing a *zero vector* — *division by zero*.**
3. **Sloppy distinction between *row vs column vectors*.**
4. **Confusing *dot product* and *element-wise product*.**
5. **Ignoring *floating-point error*.**

## How This Shows Up in Production

ML feature inputs, *embedding vectors*, *user/item vectors* in recommenders, and *word embeddings* in NLP — all of these are *vector operations*.

## How a Senior Engineer Thinks

- *Always print* the *shape*.
- *Always check* the *norm*.
- Know *when normalization is required*.
- *Visualize* the *geometric meaning*.
- Care about *numerical stability*.

## Checklist

- [ ] You can do *vector addition / scalar multiplication*.
- [ ] You can compute *norms*.
- [ ] You can *normalize*.
- [ ] You understand the *geometric meaning*.

## Practice Problems

1. Compute by hand the *Euclidean norm* of `v = [3, 4]`.
2. Verify in code that the *normalized vector* has norm *1*.
3. Explain why *normalizing the zero vector* is *undefined*.

## Wrap-up and Next Steps

A vector is a *point/arrow in space* and *one row of your data*. The next post covers *matrices*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Vectors?**
  - The article treats Vectors as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Vectors?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Vectors reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- **Vectors (current)**
- Matrices (upcoming)
- Inner Product and Distance (upcoming)
- Linear Transformations (upcoming)
- Basis and Dimension (upcoming)
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Vectors](https://www.3blue1brown.com/lessons/vectors)
- [MIT OpenCourseWare — Vectors and spaces](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — Array creation](https://numpy.org/doc/stable/user/basics.creation.html)
- [Khan Academy — Vectors and spaces](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces)

Tags: LinearAlgebra, Vectors, NumPy, DataScience, Beginner
