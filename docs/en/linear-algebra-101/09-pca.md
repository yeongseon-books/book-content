---
series: linear-algebra-101
episode: 9
title: PCA
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
  - PCA
  - DimensionalityReduction
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to PCA — its definition, SVD-based mechanics, and how it powers dimensionality reduction in ML, with NumPy code
last_reviewed: '2026-05-04'
---

# PCA

> Linear Algebra 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you find the *most important directions* in *high-dimensional data*?

> *PCA finds the *axes of greatest variance* and *projects the data* onto them.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *definition and intuition* behind *PCA*
- The two views: *SVD-based* and *covariance-based*
- *Variance preservation* and *dimensionality reduction*
- A 5-step hands-on
- Five common pitfalls

## Why It Matters

Dimensionality reduction, visualization, denoising, *feature compression* — *PCA* is the most fundamental and powerful tool.

> *PCA finds the directions that explain the most variance.*

## Concept at a Glance

```mermaid
flowchart LR
    Data["High-dim data X"] --> Center["Center"]
    Center --> Cov["Covariance or SVD"]
    Cov --> PC["Principal components"]
    PC --> Proj["Project to top-k axes"]
```

## Key Terms

- **PC (principal component)**: *orthogonal axes* sorted by *variance*.
- **Explained variance ratio**: the *fraction of variance* each PC explains.
- **Covariance matrix**: `(1/n) X^T X` (centered).
- **SVD-based PCA**: `X = U S V^T` — columns of `V` are the PCs.
- **Reconstruction error**: error after *low-dim projection and back*.

## Before/After

**Before**: *"Dimensionality reduction? Just drop some features."*

**After**: *"PCA performs an *optimal rotation* and keeps the *top k axes* — *minimal variance loss*."*

## Hands-on: Five Steps with PCA

### Step 1 — Generate data

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3)) @ np.array([[1, 0.8, 0],
                                          [0, 0.6, 0],
                                          [0, 0,   1]])
```

### Step 2 — Center

```python
Xc = X - X.mean(axis=0)
```

### Step 3 — SVD

```python
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
print("singular values:", S)
print("explained variance ratio:", (S**2) / (S**2).sum())
```

### Step 4 — Project onto the top 2 PCs

```python
k = 2
X_2d = Xc @ Vt[:k].T
print("projected shape:", X_2d.shape)
```

### Step 5 — Reconstruction error

```python
X_rec = X_2d @ Vt[:k]
err = np.linalg.norm(Xc - X_rec) / np.linalg.norm(Xc)
print("relative reconstruction error:", err)
```

## What to Notice in This Code

- *Centering* is *mandatory*.
- *SVD* is *numerically stable*.
- Use the *explained variance ratio* to pick *k*.

## Five Common Mistakes

1. **Skipping *centering / scaling*.**
2. **Letting *features with large scale* dominate the *PCs*.**
3. **Forgetting that *PC signs* are *arbitrary*.**
4. **Applying *PCA* to *nonlinear* relationships — limited effect.**
5. **Choosing *k* arbitrarily.**

## How This Shows Up in Production

Image compression, denoising, *EDA visualization*, *feature compression*, *genomics analysis* — all are applications of *PCA*.

## How a Senior Engineer Thinks

- *Standardize before PCA* by default.
- Pick *k* using *cumulative explained variance*.
- Tries to *interpret PCs*.
- Considers *t-SNE / UMAP* for *nonlinear* structure.
- Validates with *reconstruction error*.

## Checklist

- [ ] You can implement *PCA* with NumPy.
- [ ] You can compute the *explained variance ratio*.
- [ ] You know how to *choose k*.
- [ ] You can measure *reconstruction error*.

## Practice Problems

1. Apply *PCA* to the *iris dataset* and visualize it in *2D*.
2. Find the smallest *k* that reaches *90% cumulative explained variance*.
3. Describe the *difference between PCA and feature selection*.

## Wrap-up and Next Steps

PCA is the *standard for dimensionality reduction*. The next post brings everything together for *linear algebra in ML*.

<!-- toc:begin -->
- [What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Vectors](./02-vectors.md)
- [Matrices](./03-matrices.md)
- [Inner Product and Distance](./04-inner-product-and-distance.md)
- [Linear Transformations](./05-linear-transformation.md)
- [Basis and Dimension](./06-basis-and-dimension.md)
- [Eigenvalues and Eigenvectors](./07-eigenvalues-and-eigenvectors.md)
- [Matrix Decomposition](./08-matrix-decomposition.md)
- **PCA (current)**
- Linear Algebra in Machine Learning (upcoming)
<!-- toc:end -->

## References

- [Wikipedia — Principal component analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [scikit-learn — PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [Setosa — Principal Component Analysis](https://setosa.io/ev/principal-component-analysis/)
- [Stanford CS229 — Notes on PCA](https://cs229.stanford.edu/notes2020spring/cs229-notes10.pdf)
