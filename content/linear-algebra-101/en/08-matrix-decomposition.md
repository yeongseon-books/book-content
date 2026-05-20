---
series: linear-algebra-101
episode: 8
title: "Linear Algebra 101 (8/10): Matrix Decomposition"
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
  - Decomposition
  - SVD
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to matrix decomposition — LU, QR, eigendecomposition, and SVD with their meaning, use cases, and NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (8/10): Matrix Decomposition

Once you work with matrices long enough, direct manipulation starts to hit limits. Computing an inverse can be slow or unstable, and different problems prefer different computational paths. Matrix decomposition enters at that point: break one complicated matrix into pieces that are easier to solve with, interpret, or approximate.

This is post 8 in the Linear Algebra 101 series. Here we will place LU, QR, eigendecomposition, and SVD on the same map.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Matrix Decomposition?
- Which signal should the example or diagram make visible for Matrix Decomposition?
- What failure should be prevented first when Matrix Decomposition reaches a real system?

## Big Picture

![linear algebra 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/08/08-01-concept-at-a-glance.en.png)

*linear algebra 101 chapter 8 flow overview*

This picture places Matrix Decomposition inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Matrix Decomposition is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Post Answers

- Why should decomposition come to mind before explicit inversion?
- What kinds of problems fit LU, QR, eigendecomposition, and SVD best?
- Why can’t every decomposition be applied to every matrix?
- How do you verify that a decomposition still explains the original matrix?

> Matrix decomposition breaks a complicated transformation into simpler parts. In practical numerical linear algebra, that is usually how the real work gets done.

## Why It Matters

Solving linear systems, fitting least-squares models, compressing data, and building low-rank approximations all depend on decomposition. The choice affects both speed and numerical stability.

This is one of the most useful mindset shifts in the series. Stable linear algebra is usually about selecting the right factorization for the question in front of you, not about reaching for the inverse because the formula looks short.

## Concept at a Glance

## Key Terms

- **LU**: product of *lower / upper triangular* — for *equation solving*.
- **QR**: *orthogonal* times *upper triangular* — for *least squares*.
- **Eigendecomposition**: `V D V^-1` — for *diagonalization*.
- **SVD**: `U S V^T` — works on *any matrix*, the *foundation of PCA*.
- **Singular values**: *diagonal entries of S* — *always non-negative*.

## Before/After

**Before**: *"Solve everything with the inverse."*

**After**: *"Use the right *decomposition* for the situation — *much faster and more stable*."*

## Hands-on: Five Steps with Decomposition

### Step 1 — LU decomposition

```python
import numpy as np
from scipy.linalg import lu
A = np.array([[4.0, 3.0], [6.0, 3.0]])
P, L, U = lu(A)
print("L:", L)
print("U:", U)
```

### Step 2 — QR decomposition

```python
Q, R = np.linalg.qr(A)
print("Q^T Q ~ I:", np.allclose(Q.T @ Q, np.eye(2)))
print("R:", R)
```

### Step 3 — Eigendecomposition

```python
vals, vecs = np.linalg.eig(A)
print("vals:", vals)
```

### Step 4 — SVD

```python
U, S, Vt = np.linalg.svd(A)
print("U:", U)
print("S:", S)
print("Vt:", Vt)
```

### Step 5 — Reconstruct from SVD

```python
A_reconstructed = U @ np.diag(S) @ Vt
print("close to A:", np.allclose(A_reconstructed, A))
```

## Read One Numeric Pass

- LU decomposition rewrites the original matrix into triangular factors, which is exactly why linear-system solving becomes easier.
- In QR decomposition, `Q.T @ Q` comes out very close to the identity matrix, confirming that the basis stayed orthogonal.
- For SVD, `np.allclose(A_reconstructed, A)` returning `True` tells you the factorization still explains the full original matrix.

## What to Notice in This Code

- *Each decomposition* has its own *use case*.
- *SVD* exists for *every matrix*.
- *Reconstruction* is a useful *verification*.

## Five Common Mistakes

1. **Trying to use *LU* on a *rectangular* matrix.**
2. **Not knowing the *difference between QR and SVD*.**
3. **Forgetting that *SVD singular values* come in a *fixed order*.**
4. **Comparing floats with *==*.**
5. **Using *np.linalg.inv* for *least squares* — numerically *unstable*.**

## How This Shows Up in Production

Linear systems (*LU*), least squares (*QR*), PCA (*SVD*), *recommender matrix factorization (MF)*, *image compression (low-rank SVD)* — all are *matrix decompositions*.

## How a Senior Engineer Thinks

- Uses *decompositions* instead of explicit inverses.
- Treats *SVD* as the *most general / powerful* tool.
- Watches the *condition number* and *numerical stability*.
- Uses *low-rank approximations* for *compression / denoising*.
- Knows the *cost / benefit* of each decomposition.

## Checklist

- [ ] You know the *use case* of *LU/QR/Eig/SVD*.
- [ ] You can compute decompositions with *NumPy*.
- [ ] You can *verify by reconstruction*.
- [ ] You *prefer decompositions to inverses*.

## Practice Problems

1. Compute the *SVD* of a *3x2 rectangular matrix* and report the *shapes*.
2. Solve a *least squares* problem using *QR decomposition*.
3. Approximate a matrix with a *low-rank SVD* and measure the *error from the original*.

## Wrap-up and Next Steps

Matrix decompositions are the *core of numerical linear algebra*. The next post covers *PCA*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Matrix Decomposition?**
  - The article treats Matrix Decomposition as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Matrix Decomposition?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Matrix Decomposition reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- [Linear Algebra 101 (4/10): Inner Product and Distance](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): Linear Transformations](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): Basis and Dimension](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): Eigenvalues and Eigenvectors](./07-eigenvalues-and-eigenvectors.md)
- **Matrix Decomposition (current)**
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [MIT OpenCourseWare — Factorization methods](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — linalg.svd](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
- [SciPy — linalg.lu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

Tags: LinearAlgebra, Decomposition, SVD, DataScience, Beginner
