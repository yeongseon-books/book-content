---
series: linear-algebra-101
episode: 3
title: Matrices
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
  - Matrices
  - NumPy
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to matrices — definition, multiplication, transpose, identity, and inverse with NumPy code and geometric intuition
last_reviewed: '2026-05-15'
---

# Matrices

Matrices are the notation you see most often in linear algebra. Sometimes they look like tables that hold data. Sometimes they act like rules that move one vector into another. If you only remember the table view, you can still run the arithmetic without understanding why multiplication deserves so much attention.

This is post 3 in the Linear Algebra 101 series. Here we will read matrices through two linked perspectives: shape and transformation.

## Questions This Post Answers

- What makes a matrix more than a rectangular table of numbers?
- Why is matrix multiplication easier to read as composition of transformations?
- What do transpose, identity, and inverse each mean operationally?
- Why does checking shape first prevent so many practical mistakes?

> A matrix is both a compact display of numbers and a compressed rule acting on a vector space. Matrix multiplication comes alive only when those two readings stay connected.

## Why It Matters

Design matrices in regression, weight matrices in neural networks, user-item structures in recommenders, and transformation matrices in graphics all rely on the same object. A matrix is simultaneously storage and engine.

Many production mistakes start as shape mistakes. If you cannot read how many dimensions go in, how many come out, and what kind of transformation is implied, code may run while the meaning is already wrong. Matrices reward the habit of reading structure before values.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/03/03-01-concept-at-a-glance.en.png)

*This diagram summarizes how multiplication, transpose, and inversion make matrices readable as transformation rules.*

## Key Terms

- **Matrix**: an `m x n` *array of numbers*.
- **Transpose**: *swap rows and columns* — `A^T`.
- **Identity I**: ones on the diagonal, zeros elsewhere — `I v = v`.
- **Inverse**: `A A^-1 = I` — only for *square* matrices, and not always exists.
- **Matrix product**: `(m x k)(k x n) = (m x n)` — *inner dimensions must match*.

## Before/After

**Before**: *"Matrix multiplication is just sums of rows times columns."* — no idea *why*.

**After**: *"Matrix multiplication = *composition of transformations*. Apply one, then the next."*

## Hands-on: Five Steps with Matrices

### Step 1 — Build a matrix

```python
import numpy as np
A = np.array([[1.0, 2.0], [3.0, 4.0]])
print("A:", A, "shape:", A.shape)
```

### Step 2 — Transpose

```python
print("A^T:", A.T)
```

### Step 3 — Matrix multiplication

```python
B = np.array([[5.0, 6.0], [7.0, 8.0]])
print("A B:", A @ B)
print("B A:", B @ A)  # different! non-commutative
```

### Step 4 — Identity matrix

```python
I = np.eye(2)
print("I:", I)
print("A I = A:", A @ I)
```

### Step 5 — Inverse

```python
A_inv = np.linalg.inv(A)
print("A^-1:", A_inv)
print("A A^-1 ~ I:", A @ A_inv)
```

## Read One Numeric Pass

- `A @ B` yields `[[19., 22.], [43., 50.]]`, while `B @ A` yields `[[23., 34.], [31., 46.]]`. The numbers make non-commutativity impossible to ignore.
- `A @ I` returns `A`, which is the algebraic version of “do nothing.”
- `A @ A^{-1}` lands very close to the identity matrix, apart from floating-point noise.

## What to Notice in This Code

- *Matrix multiplication* is *non-commutative* — `A B != B A`.
- An *inverse* does *not always exist*.
- In *NumPy*, `@` is *matrix product* and `*` is *element-wise*.

## Five Common Mistakes

1. **Confusing `@` and `*`.**
2. **Triggering accidental *broadcasting* due to shape mismatch.**
3. **Inverting a *singular* matrix.**
4. **Forgetting that *matrix multiplication is non-commutative*.**
5. **Ignoring that *floating-point error* makes `A A^-1` only *approximately* `I`.**

## How This Shows Up in Production

The *normal equations* in linear regression, *weight matrices* in neural networks, *transformation matrices* in graphics, and *user-item matrices* in recommenders — all are *matrix operations*.

## How a Senior Engineer Thinks

- *Avoid explicit inverses* — solve via *decompositions*.
- *Always check shapes*.
- Be aware of *non-commutativity*.
- Use *purpose-built solvers* for *numerical stability*.
- *Visualize* the *geometric meaning*.

## Checklist

- [ ] You can do *matrix multiplication*.
- [ ] You can *transpose*.
- [ ] You know when an *inverse exists*.
- [ ] You are aware of *non-commutativity*.

## Practice Problems

1. Compute by hand the *transpose* and *inverse* of a 2x2 matrix `A`.
2. Multiply the *identity matrix* `I` with an arbitrary vector and check the result is unchanged.
3. Build an example of a *singular matrix* and explain why its *inverse does not exist*.

## Wrap-up and Next Steps

A matrix is a *compressed transformation*. The next post covers *inner product and distance*.

<!-- toc:begin -->
- [What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Vectors](./02-vectors.md)
- **Matrices (current)**
- Inner Product and Distance (upcoming)
- Linear Transformations (upcoming)
- Basis and Dimension (upcoming)
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)
<!-- toc:end -->

## References

- [3Blue1Brown — Matrix multiplication as composition](https://www.3blue1brown.com/lessons/matrix-multiplication)
- [MIT OpenCourseWare — Matrix algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — linalg.inv](https://numpy.org/doc/stable/reference/generated/numpy.linalg.inv.html)
- [Khan Academy — Matrices](https://www.khanacademy.org/math/algebra-home/alg-matrices)

Tags: LinearAlgebra, Matrices, NumPy, DataScience, Beginner
