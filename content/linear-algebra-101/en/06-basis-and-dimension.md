---
series: linear-algebra-101
episode: 6
title: "Linear Algebra 101 (6/10): Basis and Dimension"
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

# Linear Algebra 101 (6/10): Basis and Dimension

As soon as you go one step deeper into linear algebra, a natural question appears: why can one space be described by multiple sets of axes, and how many axes do you really need? Basis and dimension answer that question. Rank, PCA, and rank-deficient models all come back here.

This is the 6th post in the Linear Algebra 101 series. Here we will tie linear independence, basis, dimension, and rank into one picture.


![linear algebra 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/06/06-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 6 flow overview*
> Basis and dimension are the language that defines a vector space. Once a basis is fixed, every point in that space has a unique representation, and changing basis is just a change of coordinates.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Basis and Dimension?
- Which signal should the example or diagram make visible for Basis and Dimension?
- What failure should be prevented first when Basis and Dimension reaches a real system?

## Questions This Post Answers

- What does it mean for a set of vectors to describe a space completely?
- Why is linear independence the key condition behind a basis?
- How are dimension and rank connected?
- What does it mean for the same space to admit multiple bases?

> A basis is a choice of axes for a space, and dimension is the answer to how many axes are required. Separating those ideas makes the geometry far easier to read.

## Why It Matters

Multicollinearity, dimensionality reduction, principal components, and singular matrices all depend on these concepts. This is not an isolated definitions chapter. It feeds directly into model stability and data representation quality.

In practice, some features add almost no new information because they are nearly explained by others. Good basis choices can make the same data easier to compress, inspect, and reason about. Basis and dimension are tools for reading the real complexity of a space.

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

## Answering the Opening Questions

- **What does it mean for a set of vectors to "fully describe" a space?**
  - It means every vector in the space can be written as a linear combination of that set. For example, with `e1 = [1,0]` and `e2 = [0,1]`, any 2D plane vector can be expressed as `v = 3*e1 + 4*e2`, making them a standard basis.
- **Why is linear independence the key condition for a basis?**
  - A basis must be a minimal, non-redundant set of axes—not just any spanning set. When the matrix with columns `[[1,2],[2,4]]` has rank `1`, it means the two vectors point the same direction and add no new axis.
- **How do dimension and rank connect?**
  - Dimension is the number of independent directions describing a space; rank measures how many of those directions are actually alive inside a matrix. So `np.linalg.matrix_rank(A)` returning `2` means full 2D information is preserved, while `1` means only one information axis exists regardless of shape.
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- [Linear Algebra 101 (4/10): Inner Product and Distance](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): Linear Transformations](./05-linear-transformation.md)
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
