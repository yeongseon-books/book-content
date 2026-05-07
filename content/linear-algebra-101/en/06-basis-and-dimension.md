---
series: linear-algebra-101
episode: 6
title: Basis and Dimension
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-04'
---

# Basis and Dimension

> Linear Algebra 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: What determines *how many vectors* you need to *describe a space*?

> *A basis is a *set of axes*; the dimension is the *count of those axes*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The definition of *linear independence*
- The relationship between *basis* and *dimension*
- *Rank* and the *null space*
- A 5-step hands-on
- Five common pitfalls

## Why It Matters

*Singular matrices*, *overfitting*, *PCA's principal axes* — all are explained by *basis and dimension*.

> *Dimension is the count; basis is the choice of axes.*

## Concept at a Glance

```mermaid
flowchart LR
    Vecs["Set of vectors"] --> Indep["Linearly independent?"]
    Indep --> Basis["Basis"]
    Basis --> Dim["Dimension"]
    Dim --> Rank["Rank of matrix"]
```

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

- [3Blue1Brown — Basis vectors](https://www.3blue1brown.com/lessons/span)
- [Wikipedia — Basis (linear algebra)](https://en.wikipedia.org/wiki/Basis_(linear_algebra))
- [Wikipedia — Rank (linear algebra)](https://en.wikipedia.org/wiki/Rank_(linear_algebra))
- [NumPy — matrix_rank](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)

Tags: LinearAlgebra, Basis, Dimension, DataScience, Beginner
