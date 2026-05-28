---
series: linear-algebra-101
episode: 1
title: "Linear Algebra 101 (1/10): What Is Linear Algebra?"
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
  - Foundations
  - Vectors
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to linear algebra — vectors, matrices, and linear transformations, why they matter for ML, with hands-on NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (1/10): What Is Linear Algebra?

If you learn machine learning through formulas, there is usually a moment when the notation suddenly gets dense. Data becomes vectors, parameters become matrices, and one model layer starts to look like a transformation. If linear algebra still feels like a table of numbers, the formulas remain memorized procedures instead of connected ideas.

This is the first post in the Linear Algebra 101 series. Here we will treat linear algebra as the language that ties vectors, matrices, and linear transformations into one picture.


![linear algebra 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/01/01-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 1 flow overview*
> Linear algebra is not a bag of calculations. It is a language for expressing space with coordinates and turning geometric rules into computation.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Linear Algebra??
- Which signal should the example or diagram make visible for What Is Linear Algebra??
- What failure should be prevented first when What Is Linear Algebra? reaches a real system?

## Questions This Post Answers

- What does linear algebra actually study beyond symbol manipulation?
- Why do vectors and matrices keep reappearing in ML, graphics, and statistics?
- Why is matrix multiplication easier to understand as composition of transformations?
- How does the linear-transformation viewpoint connect the rest of the series?

> Linear algebra is not a bag of calculations. It is a language for expressing space with coordinates and turning geometric rules into computation.

## Why It Matters

In machine learning, input data arrives as vectors, parameters live in matrices, and an entire layer is usually a linear transformation followed by a nonlinearity. Recommender systems, graphics, and signal processing are not all the same field, but they keep returning to the same vector-and-matrix grammar.

If your linear algebra intuition is weak, the inside of a model stays opaque. Once you can read what a vector stores, what a matrix compresses, and why multiplication depends on order, the notation stops feeling like decoration and starts revealing structure.

## Key Terms

- **Vector**: a *bundle of numbers* with *direction and magnitude*.
- **Matrix**: a *collection of vectors* or a *representation of a linear transformation*.
- **Linear transformation**: a rule that *maps vectors to vectors* and preserves *addition and scalar multiplication*.
- **Dimension**: the number of coordinates needed to describe a space.
- **Basis**: the *minimal set* that can *represent every point* in a space.

## Before/After

**Before**: *"A matrix is just a number grid."* — no idea *why* we multiply them.

**After**: *"Matrix multiplication = composition of linear transformations — a rule that rotates, scales, or reflects space."*

## Hands-on: Five Steps to Linear Algebra Intuition

### Step 1 — Build a vector

```python
import numpy as np
v = np.array([3.0, 4.0])
print("v:", v, "norm:", np.linalg.norm(v))
```

### Step 2 — Build a matrix

```python
A = np.array([[1.0, 2.0],
              [3.0, 4.0]])
print("A shape:", A.shape)
```

### Step 3 — Apply a linear transformation

```python
y = A @ v
print("Av:", y)
```

### Step 4 — A rotation matrix

```python
theta = np.pi / 2
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
print("R v:", R @ v)
```

### Step 5 — Compose transformations

```python
print("R(A v):", R @ (A @ v))
print("(R A) v:", (R @ A) @ v)
```

## Read One Numeric Pass

- `np.linalg.norm([3, 4])` returns `5.0`. One vector length already gives you a geometric anchor.
- `A @ v` becomes `array([11., 25.])`, which shows that the same input vector can be reinterpreted by a matrix rule.
- A 90-degree rotation sends `[3, 4]` to `[-4., 3.]`, making the idea of a transformation visible instead of purely symbolic.

## What to Notice in This Code

- A *vector* has *direction + magnitude* — not just a list of numbers.
- *Matrix multiplication* is *composition* — order matters.
- *NumPy* is the standard *linear algebra* library.

## Five Common Mistakes

1. **Mismatched *row/column* shapes.**
2. **Confusing *matrix product* and *element-wise product*.**
3. **Forgetting that *matrix multiplication is non-commutative*.**
4. **Treating *vectors as plain number lists* only.**
5. **Memorizing *dimension/basis* without intuition.**

## How This Shows Up in Production

Recommender systems, image processing, graphics, and every layer of deep learning — *matrix operations* are the *engine of computation*. *NumPy / PyTorch / TensorFlow* are essentially *linear algebra accelerators*.

## How a Senior Engineer Thinks

- *Always print* the *shape*.
- *Sketch* the *meaning of the transformation*.
- Be aware of *order and non-commutativity*.
- Combine *geometric intuition* with *algebraic computation*.
- Care about *numerical stability*.

## Checklist

- [ ] You can build *vectors and matrices*.
- [ ] You can multiply matrices.
- [ ] You understand *linear transformations*.
- [ ] You can match *shapes*.

## Practice Problems

1. Compute by hand the result of *rotating* the 2D vector `[1, 0]` by *90 degrees*.
2. Construct two matrices `A`, `B` such that `A B` and `B A` are *not equal*.
3. Describe what the *identity matrix* `I` does to *any vector*.

## Wrap-up and Next Steps

Linear algebra is the *language of space*. The next post explores *vector operations* and their *geometric meaning* in depth.

## Answering the Opening Questions

- **What exactly does linear algebra study?**
  - Linear algebra systematically handles space transformations through two fundamental objects—vectors and matrices—and their composition operation, matrix multiplication. This is why it appears repeatedly in machine learning, graphics, and signal processing.
- **Why do vectors and matrices keep appearing in machine learning, graphics, and statistics?**
  - All these fields deal with high-dimensional data or spatial transformations. Vectors represent individual data points; matrices compress rules and patterns. The same mathematical language solves different problems.
- **Why should you read matrix multiplication as composition of transformations?**
  - The product `AB` means apply `B` first, then apply `A` to the result. Order matters, and understanding what transformation each matrix represents makes the computation meaningful. Without this perspective, matrix multiplication is just a mechanical procedure.
<!-- toc:begin -->
## In this series

- **What Is Linear Algebra? (current)**
- Vectors (upcoming)
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

- [3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)
- [MIT OpenCourseWare — 18.06 Linear Algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/)
- [NumPy — Linear algebra routines](https://numpy.org/doc/stable/reference/routines.linalg.html)
- [Khan Academy — Linear algebra](https://www.khanacademy.org/math/linear-algebra)

Tags: LinearAlgebra, Foundations, Vectors, DataScience, Beginner
