---
series: linear-algebra-101
episode: 7
title: "Linear Algebra 101 (7/10): Eigenvalues and Eigenvectors"
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
  - Eigenvalues
  - Eigenvectors
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to eigenvalues and eigenvectors — definition, geometric meaning, and uses in PCA and dynamics with NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (7/10): Eigenvalues and Eigenvectors

If you apply the same linear transformation again and again, some directions behave differently from the rest. Most directions get mixed or bent, but a few keep their direction and only change length. Eigenvalues and eigenvectors are the tools that describe those privileged axes.

This is the 7th post in the Linear Algebra 101 series. Here we will read eigenvalues and eigenvectors as the natural axes of a transformation.


![linear algebra 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/07/07-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 7 flow overview*
> Eigenvalues and eigenvectors are the essence of a linear transformation. An eigenvector keeps its direction; an eigenvalue is how much it stretches in that direction.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Eigenvalues and Eigenvectors?
- Which signal should the example or diagram make visible for Eigenvalues and Eigenvectors?
- What failure should be prevented first when Eigenvalues and Eigenvectors reaches a real system?

## Questions This Post Answers

- Why do some directions survive repeated matrix application?
- What do eigenvectors and eigenvalues each tell you?
- Why do symmetric matrices produce especially clean results?
- How does this connect to PCA, PageRank, and dynamical systems?

> An eigenvector is a direction that a transformation does not rotate away from. The eigenvalue tells you how strongly that direction is stretched or compressed.

## Why It Matters

Eigendecomposition lets you read a complicated transformation in a simpler coordinate system. If you can find the right axes, a messy matrix may reduce to mostly independent scaling behavior along those axes.

That is why the topic keeps returning in PCA, stability analysis, and ranking algorithms. Eigenvalues and eigenvectors are powerful not because they are formal, but because they tell you which modes dominate and which directions stay structurally meaningful.

## Key Terms

- **Eigenvector v**: a *non-zero vector* satisfying `A v = lambda v`.
- **Eigenvalue lambda**: the *scalar factor* along that axis.
- **Eigendecomposition**: `A = V D V^-1` (when diagonalizable).
- **Spectrum**: the *set of all eigenvalues*.
- **Symmetric matrix**: has *real eigenvalues* and *orthogonal eigenvectors*.

## Before/After

**Before**: *"Eigenvalues are something you solve with a formula."* — no idea why they matter.

**After**: *"They reveal the *axes of a transformation* — along which it acts as a *simple scalar*."*

## Hands-on: Five Steps with Eigendecomposition

### Step 1 — Define a matrix

```python
import numpy as np
A = np.array([[2.0, 1.0], [0.0, 3.0]])
```

### Step 2 — Eigenvalues / eigenvectors

```python
vals, vecs = np.linalg.eig(A)
print("eigenvalues:", vals)
print("eigenvectors:\n", vecs)
```

### Step 3 — Verify

```python
for i in range(len(vals)):
    Av = A @ vecs[:, i]
    lv = vals[i] * vecs[:, i]
    print("A v == lambda v:", np.allclose(Av, lv))
```

### Step 4 — Symmetric matrix

```python
S = np.array([[2.0, 1.0], [1.0, 2.0]])
sv, svc = np.linalg.eigh(S)  # for symmetric/Hermitian
print("sym eigenvalues:", sv)
print("orthogonal? ", np.allclose(svc.T @ svc, np.eye(2)))
```

### Step 5 — Power iteration and stability

```python
M = np.array([[0.9, 0.1], [0.2, 0.8]])
v = np.array([1.0, 0.0])
for _ in range(50):
    v = M @ v
print("steady state:", v / np.linalg.norm(v, 1))
```

## Read One Numeric Pass

- The matrix `[[2, 1], [0, 3]]` has eigenvalues `2` and `3`, so it has two especially readable directions.
- `np.allclose(A @ v, lambda * v)` returning `True` is the fastest sanity check that the computed vector is really an eigenvector.
- Repeated multiplication reveals the dominant direction. In this toy example, the direction settles near `[0.5, 0.5]`.

## What to Notice in This Code

- *Eigendecomposition* simplifies the *transformation*.
- For *symmetric* matrices, prefer *eigh* — it is more *stable*.
- *Power iteration* converges toward the *largest-eigenvalue direction*.

## Five Common Mistakes

1. **Assuming *every matrix* is *diagonalizable*.**
2. **Ignoring *complex eigenvalues*.**
3. **Using *eig* on symmetric matrices or *eigh* on non-symmetric ones.**
4. **Forgetting that *eigenvector sign / scale* is arbitrary.**
5. **Ignoring *numerical stability*.**

## How This Shows Up in Production

PCA (*eigendecomposition of the covariance matrix*), PageRank (*top eigenvector*), dynamical systems (*stability analysis*), quantum mechanics (*energy eigenstates*) — all are *eigendecompositions*.

## How a Senior Engineer Thinks

- Use *eigh* whenever the matrix is *symmetric*.
- Reads the *condition number* for stability.
- Interprets *complex eigenvalues* physically.
- Tracks *eigenvector signs*.
- Picks *power iteration* when appropriate.

## Checklist

- [ ] You can compute *eigenvalues / eigenvectors*.
- [ ] You know how *symmetric matrices* differ.
- [ ] You can *verify* with the eigenvector equation.
- [ ] You understand *power iteration convergence*.

## Practice Problems

1. Compute by hand the eigenvalues / eigenvectors of `diag(2, 3)`.
2. Verify that the *eigenvectors* of a *symmetric matrix* are *orthogonal*.
3. Estimate the *top eigenvector* using *power iteration*.

## Wrap-up and Next Steps

Eigendecomposition reveals a transformation's *natural axes*. The next post covers *matrix decomposition*.

## Answering the Opening Questions

- **Why do certain directions survive when a matrix is applied repeatedly?**
  - Some directions survive because the matrix doesn't deflect those vectors—it only scales them. In the article, repeated power iteration of `M @ v` showed the dominant direction persisting, which is exactly this phenomenon.
- **What do eigenvectors and eigenvalues each represent?**
  - An eigenvector is a special direction satisfying `A v = λ v`; the eigenvalue `λ` tells how much that direction stretches or shrinks. Computing with `np.linalg.eig(A)` then verifying `np.allclose(A @ v, lambda * v)` was the code equivalent of checking the definition.
- **Why are results especially clean for symmetric matrices?**
  - For the symmetric matrix `S = [[2,1],[1,2]]`, using `np.linalg.eigh(S)` produced eigenvectors that are mutually orthogonal with `svc.T @ svc ≈ I`. Axes separate cleanly, which is why problems like PCA that require orthogonal principal axes are especially convenient with symmetric matrices.
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- [Linear Algebra 101 (4/10): Inner Product and Distance](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): Linear Transformations](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): Basis and Dimension](./06-basis-and-dimension.md)
- **Eigenvalues and Eigenvectors (current)**
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Eigenvectors and eigenvalues](https://www.3blue1brown.com/lessons/eigenvalues)
- [MIT OpenCourseWare — Eigenvalues and eigenvectors](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — linalg.eig](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html)
- [NumPy — linalg.eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)

Tags: LinearAlgebra, Eigenvalues, Eigenvectors, DataScience, Beginner
