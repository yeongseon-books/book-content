---
series: linear-algebra-101
episode: 10
title: "Linear Algebra 101 (10/10): Linear Algebra in Machine Learning"
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
  - MachineLearning
  - DeepLearning
  - DataScience
  - Beginner
seo_description: A capstone tour of where linear algebra shows up in ML — linear regression, neural networks, embeddings, and optimizers — with runnable code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (10/10): Linear Algebra in Machine Learning

If you have followed the series this far, one question remains: where does all of this actually surface in machine learning? The short answer is that it shows up almost everywhere. Data representation, model definition, loss computation, and optimization all run on top of vectors and matrices.

This is the final post in the Linear Algebra 101 series. Here we will pull linear regression, neural-network layers, embeddings, gradients, and PCA into one closing picture.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Linear Algebra in Machine Learning?
- Which signal should the example or diagram make visible for Linear Algebra in Machine Learning?
- What failure should be prevented first when Linear Algebra in Machine Learning reaches a real system?

## Big Picture

![linear algebra 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/10/10-01-concept-at-a-glance.en.png)

*linear algebra 101 chapter 10 flow overview*

This picture places Linear Algebra in Machine Learning inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Linear algebra is the language beneath machine learning. Regression, classification, and dimensionality reduction are all expressed through vector and matrix operations, and the concepts of eigenvalues, decomposition, and orthogonality decide algorithmic efficiency and stability.

## Questions This Post Answers

- Where do vectors and matrices appear across an ML pipeline?
- How can linear regression and neural networks be read in linear-algebra terms?
- Why are embedding similarity and gradient updates both linear-algebra problems?
- How do the ideas from the earlier posts connect inside real ML systems?

> Linear algebra is not background trivia for machine learning. It is the skeleton. Data is represented as vectors and matrices, models are defined as transformations, and training keeps adjusting that structure.

## Why It Matters

Without linear-algebra intuition, the inside of a model stays opaque. Shape mismatches, strange embedding behavior, unstable gradients, and PCA outputs all feel like unrelated failures.

With the right mental model, the internals get much less mysterious. A layer becomes matrix multiplication plus a nonlinearity. Embedding retrieval becomes a vector-comparison problem. Optimization becomes repeated updates to a parameter vector. That intuition survives even when the framework changes.

## Key Terms

- **Design matrix X**: rows = samples, columns = features.
- **Weights W**: *learnable parameters* of a *linear transformation*.
- **Embedding**: a *high-dimensional object* represented as a *vector*.
- **Gradient**: the *derivative* of the *loss* w.r.t. vectors/matrices.
- **Batched matmul**: process *many inputs at once*.

## Before/After

**Before**: *"ML is magic."* — the inside is a *black box*.

**After**: *"Every layer is *linear transformation + nonlinearity* — *a sequence of matrices and vectors*."*

## Hands-on: Five Steps in ML × Linear Algebra

### Step 1 — Linear regression (normal equations)

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 3))
y = X @ np.array([1.0, -2.0, 0.5]) + rng.normal(scale=0.1, size=100)
w_hat, *_ = np.linalg.lstsq(X, y, rcond=None)
print("w_hat:", w_hat)
```

### Step 2 — One neural network layer

```python
W1 = rng.normal(size=(3, 4))
b1 = np.zeros(4)
h = np.maximum(0, X @ W1 + b1)  # ReLU
print("hidden shape:", h.shape)
```

### Step 3 — Cosine similarity (embeddings)

```python
emb = rng.normal(size=(5, 8))
norms = np.linalg.norm(emb, axis=1, keepdims=True)
emb_n = emb / norms
sim = emb_n @ emb_n.T
print("sim matrix shape:", sim.shape)
```

### Step 4 — One gradient step

```python
def loss_and_grad(w, X, y):
    pred = X @ w
    err = pred - y
    loss = (err ** 2).mean()
    grad = 2 * X.T @ err / len(y)
    return loss, grad

w = np.zeros(3)
for _ in range(50):
    L, g = loss_and_grad(w, X, y)
    w -= 0.05 * g
print("learned w:", w)
```

### Step 5 — Compress features with PCA

```python
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
X_2d = Xc @ Vt[:2].T
print("compressed:", X_2d.shape)
```

## Read One Numeric Pass

- `np.linalg.lstsq` recovers weights close to `[1, -2, 0.5]`, which is exactly the hidden linear rule used to generate the target.
- The hidden layer has shape `(100, 4)`, and the embedding similarity matrix has shape `(5, 5)`. Even the shapes already tell you what kind of transformation happened.
- Gradient descent moves `w` toward the same neighborhood as the least-squares solution, which connects optimization back to the same linear-algebra backbone.

## What to Notice in This Code

- *Every layer* is *matrix product + nonlinearity*.
- The *gradient* is a *vector/matrix derivative*.
- *Embedding similarity* is *cosine*.

## Five Common Mistakes

1. **Avoiding *shape-mismatch* debugging.**
2. **Skipping *normalization / standardization*.**
3. **Confusing *matrix product* with *element-wise product*.**
4. **Wrong *gradient shape* — misplaced *transpose*.**
5. **Ignoring *numerical stability* — using `inv` directly.**

## How This Shows Up in Production

Linear regression, logistic regression, *MLP / CNN / RNN / Transformer*, *embedding search*, *recommender systems* — all run on *linear algebra*.

## How a Senior Engineer Thinks

- *Always print* the *shape*.
- Uses *decompositions / normalization* for *numerical stability*.
- Derives *gradient shapes* by hand.
- Has *intuition for embedding spaces*.
- Uses *PCA / SVD* to *understand data* quickly.

## Checklist

- [ ] You can solve *linear regression* with lstsq.
- [ ] You can build *one MLP layer*.
- [ ] You can compute the *cosine similarity matrix*.
- [ ] You can implement *one gradient descent step*.

## Practice Problems

1. Train *logistic regression* on *iris* using gradient descent (no normal equations).
2. Implement a *2-layer MLP* in NumPy with only the *forward pass*.
3. Extract the *top-2 cosine similarities* among *5 embeddings*.

## Wrap-up and Next Steps

Linear algebra is the *skeleton of ML*. I hope this series gave you the *eye to see inside models*. The next step is the *Calculus for ML* series.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Linear Algebra in Machine Learning?**
  - The article treats Linear Algebra in Machine Learning as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Linear Algebra in Machine Learning?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Linear Algebra in Machine Learning reaches a real system?**
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
- [Linear Algebra 101 (8/10): Matrix Decomposition](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- **Linear Algebra in Machine Learning (current)**

<!-- toc:end -->

## References

- [Deep Learning Book — Linear Algebra](https://www.deeplearningbook.org/contents/linear_algebra.html)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)
- [NumPy — linalg.lstsq](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)
- [fast.ai — Computational Linear Algebra](https://github.com/fastai/numerical-linear-algebra)

Tags: LinearAlgebra, MachineLearning, DeepLearning, DataScience, Beginner
