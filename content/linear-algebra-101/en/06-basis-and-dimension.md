---
series: linear-algebra-101
episode: 6
title: Basis and Dimension
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
  - Basis
  - Dimension
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to basis and dimension — linear independence, rank, and choosing axes for a vector space, with NumPy code
last_reviewed: '2026-05-15'
---

# Basis and Dimension

As soon as you go one step deeper into linear algebra, a natural question appears: why can one space be described by multiple sets of axes, and how many axes do you really need? Basis and dimension answer that question. Rank, PCA, and rank-deficient models all come back here.

This is post 6 in the Linear Algebra 101 series. Here we will tie linear independence, basis, dimension, and rank into one picture.

## Questions This Post Answers

- What does it mean for a set of vectors to describe a space completely?
- Why is linear independence the key condition behind a basis?
- How are dimension and rank connected?
- What does it mean for the same space to admit multiple bases?

> A basis is a choice of axes for a space, and dimension is the answer to how many axes are required. Separating those ideas makes the geometry far easier to read.

## Why It Matters

Multicollinearity, dimensionality reduction, principal components, and singular matrices all depend on these concepts. This is not an isolated definitions chapter. It feeds directly into model stability and data representation quality.

In practice, some features add almost no new information because they are nearly explained by others. Good basis choices can make the same data easier to compress, inspect, and reason about. Basis and dimension are tools for reading the real complexity of a space.

## Concept at a Glance

![Concept at a Glance](../../../assets/linear-algebra-101/06/06-01-concept-at-a-glance.en.png)

*This diagram condenses the flow from linear independence to basis, dimension, and matrix rank.*

## Key Terms

- **Linear combination**: `c1 v1 + c2 v2 + ...`
- **Linearly independent**: no vector is a *linear combination of the others*.
- **Basis**: a set of vectors that *spans* a space and is *linearly independent*.
- **Dimension**: the *size of a basis*.
- **Rank**: the *number of linearly independent columns (or rows)* of a matrix.

## Before/After

**Before**: *"A basis is the standard unit vectors."* — that is the only one you know.

**After**: *"A basis is a *choice* — the same space admits *many coordinate systems*."*

## Hands-on: Five Steps with Basis and Dimension

### Step 1 — Standard basis

```python
import numpy as np
e1 = np.array([1.0, 0.0])
e2 = np.array([0.0, 1.0])
print("e1, e2:", e1, e2)
```

### Step 2 — Linear combination

```python
v = 3 * e1 + 4 * e2
print("v:", v)
```

### Step 3 — Independence via rank

```python
A = np.column_stack([e1, e2])
print("rank:", np.linalg.matrix_rank(A))  # 2
```

### Step 4 — Dependent example

```python
B = np.column_stack([np.array([1.0, 2.0]), np.array([2.0, 4.0])])
print("rank:", np.linalg.matrix_rank(B))  # 1
```

### Step 5 — Coordinates in a different basis

```python
b1 = np.array([1.0, 1.0])
b2 = np.array([1.0, -1.0])
B = np.column_stack([b1, b2])
v = np.array([3.0, 4.0])
coords = np.linalg.solve(B, v)
print("coords in {b1,b2}:", coords)
```

## Read One Numeric Pass

- The standard basis stacked into a matrix has rank `2`, which means it spans the full 2D plane.
- The pair `[1, 2]` and `[2, 4]` has rank `1`, so the second vector adds no new direction.
- Expressing `[3, 4]` in the basis `{[1,1], [1,-1]}` gives coordinates `[3.5, -0.5]`. Same vector, different coordinate system.

## What to Notice in This Code

- *Rank* tells you the *dimension*.
- A *basis is not unique*.
- If vectors are *linearly dependent*, they fail to *fill the space*.

## Five Common Mistakes

1. **Trying to *invert a rank-deficient* matrix.**
2. **Believing the *basis is unique*.**
3. **Floating-point errors causing *rank miscalculation*.**
4. **Confusing *dimension* with *matrix size*.**
5. **Judging *linear independence* purely by *visual intuition*.**

## How This Shows Up in Production

PCA's *principal components* form a *new basis*. *Feature selection / dimensionality reduction* is a *basis change*. *Multicollinearity* equals *rank deficiency*.

## How a Senior Engineer Thinks

- *Always check rank*.
- Uses the *condition number* to detect *near-dependence*.
- Uses *basis change* to *simplify problems*.
- Uses *PCA / SVD* to find an *optimal basis*.
- *Resolves multicollinearity* explicitly.

## Checklist

- [ ] You can test for *linear independence*.
- [ ] You can compute *rank*.
- [ ] You can express *coordinates in a different basis*.
- [ ] You know the difference between *dimension* and *rank*.

## Practice Problems

1. Explain why *three 2D vectors* cannot be *linearly independent*.
2. What is the *maximum rank* of a *2x3 matrix*?
3. Use a *basis change* to express the vector `[3, 4]` in a new coordinate system.

## Wrap-up and Next Steps

A basis is a *choice of axes*; dimension is *their count*. The next post covers *eigenvalues and eigenvectors*.

<!-- toc:begin -->
- [What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Vectors](./02-vectors.md)
- [Matrices](./03-matrices.md)
- [Inner Product and Distance](./04-inner-product-and-distance.md)
- [Linear Transformations](./05-linear-transformation.md)
- **Basis and Dimension (current)**
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)
<!-- toc:end -->

## References

- [3Blue1Brown — Span, basis, and linear independence](https://www.3blue1brown.com/lessons/span)
- [MIT OpenCourseWare — Basis and dimension](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — matrix_rank](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)
- [Khan Academy — Linear independence and basis](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces/linear-independence-basis)

Tags: LinearAlgebra, Basis, Dimension, DataScience, Beginner
