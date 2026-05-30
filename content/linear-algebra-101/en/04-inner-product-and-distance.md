---
series: linear-algebra-101
episode: 4
title: "Linear Algebra 101 (4/10): Inner Product and Distance"
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
  - InnerProduct
  - Distance
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to inner products and distance — dot product, cosine similarity, Euclidean and Manhattan distance with NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (4/10): Inner Product and Distance

Once vectors are in play, the next question comes immediately: how similar are two vectors, and how far apart are they? Recommenders, embedding search, and nearest-neighbor lookups are all versions of that question turned into numbers.

This is the 4th post in the Linear Algebra 101 series. Here we will connect the inner product, cosine similarity, Euclidean distance, and Manhattan distance into one comparison toolkit.


![linear algebra 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/04/04-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 4 flow overview*
> Inner product and distance are the two foundations of vector comparison. Inner product measures directional relationship; distance measures the gap between points. Which you use depends on your problem's nature.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Inner Product and Distance?
- Which signal should the example or diagram make visible for Inner Product and Distance?
- What failure should be prevented first when Inner Product and Distance reaches a real system?

## Questions This Post Answers

- Why does the inner product collapse two vectors into one scalar?
- How does cosine similarity grow out of the inner product?
- What changes when you compare Euclidean distance with Manhattan distance?
- Why are "similar" and "close" not always the same claim?

> The inner product measures directional alignment. Distance measures separation in space. Because the questions differ, the numbers should be read differently too.

## Why It Matters

Document embeddings often care about direction, which is why cosine similarity shows up everywhere. Coordinate differences, travel costs, and physical displacement often care about actual gap size, where Euclidean or Manhattan distance can be a better fit.

Without that distinction, metric choice becomes habit instead of judgment. You start using cosine everywhere or L2 everywhere, even though search rankings, clusters, and neighbor sets can shift dramatically when the metric changes. This chapter is about choosing the comparison question, not memorizing one more formula.

## Key Terms

- **Inner product**: `v . w = sum(v_i * w_i)` — a *scalar*.
- **Cosine similarity**: `(v . w) / (||v|| ||w||)` — compares *direction only*.
- **Orthogonal**: `v . w = 0` — *perpendicular*.
- **Euclidean distance**: `||v - w||` — *straight-line distance*.
- **Manhattan distance**: `sum(|v_i - w_i|)` — *grid distance*.

## Before/After

**Before**: *"Inner product is just multiply and add."*

**After**: *"Inner product measures *alignment*; *cosine* gives *directional similarity*."*

## Hands-on: Five Steps with Inner Product and Distance

### Step 1 — Prepare vectors

```python
import numpy as np
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])
```

### Step 2 — Inner product

```python
print("v . w:", np.dot(v, w))
print("v . w:", v @ w)
```

### Step 3 — Cosine similarity

```python
cos_sim = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print("cosine similarity:", cos_sim)
```

### Step 4 — Euclidean distance

```python
print("Euclidean:", np.linalg.norm(v - w))
```

### Step 5 — Manhattan distance

```python
print("Manhattan:", np.sum(np.abs(v - w)))
```

## Read One Numeric Pass

- `v @ w` is `32.0`, so one scalar is already summarizing how strongly the two vectors align.
- Cosine similarity is about `0.975`, which tells you the directions are close even before you look at raw distance.
- Euclidean distance is about `5.196`, while Manhattan distance is `9.0`. Same vectors, different question, different number.

## What to Notice in This Code

- The *inner product* reflects both *direction and magnitude*.
- *Cosine similarity* reflects only *direction* — *scale-invariant*.
- *Distance* is *dissimilarity* — *smaller means closer*.

## SciPy Distance Functions

In production, use validated libraries instead of hand-rolling distance calculations. SciPy provides 20+ distance functions with batch support via `pdist` and `cdist`.

```python
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine, mahalanobis

# Sample vectors
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])

# 1. Euclidean distance (L2)
dist_l2 = euclidean(v, w)
print('Euclidean distance:', dist_l2)
print('NumPy equivalent:', np.linalg.norm(v - w))

# 2. Manhattan distance (L1)
dist_l1 = cityblock(v, w)
print('Manhattan distance:', dist_l1)
print('NumPy equivalent:', np.sum(np.abs(v - w)))

# 3. Cosine distance (1 - cosine similarity)
dist_cos = cosine(v, w)
print('Cosine distance:', dist_cos)
cos_sim = np.dot(v, w) / (np.linalg.norm(v) * np.linalg.norm(w))
print('Cosine similarity:', cos_sim)
print('1 - cos_sim:', 1 - cos_sim)

# 4. Mahalanobis distance
# Requires a covariance matrix
X = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9],
              [2, 3, 4],
              [5, 6, 7]])
cov = np.cov(X.T)
cov_inv = np.linalg.pinv(cov)  # pseudo-inverse for stability

dist_maha = mahalanobis(v, w, cov_inv)
print('Mahalanobis distance:', dist_maha)

# 5. Pairwise distance matrix
from scipy.spatial.distance import pdist, squareform

points = np.array([[0, 0],
                   [1, 0],
                   [0, 1],
                   [1, 1]])

# All-pairs Euclidean distances
distances = pdist(points, metric='euclidean')
dist_matrix = squareform(distances)
print('Distance matrix:\n', dist_matrix)
```

`scipy.spatial.distance` supports 20+ distance functions, and `pdist`/`cdist` handle batch computation efficiently. In production, these provide better numerical stability and performance than manual implementations.

## Geometric Interpretation of the Inner Product

The inner product encodes both length and angle information simultaneously:

$$a \cdot b = \|a\|\,\|b\|\cos\theta$$

- `> 0`: same general direction
- `= 0`: orthogonal (perpendicular)
- `< 0`: opposite direction

This interpretation goes beyond simple score comparison in embedding search — it explains *why* certain results rank higher.

## Metric Selection Guide

| Situation | Preferred Metric | Reason |
|---|---|---|
| Embedding search / recommendations | Cosine similarity | Directional similarity is the core signal |
| Coordinate-based error analysis | Euclidean distance | Direct interpretation as physical distance |
| Sparse vectors / robustness needed | Manhattan distance | Sum of per-axis changes is interpretable |

Additionally, in high dimensions, distance concentration reduces L2 discriminability. Consider normalization, dimensionality reduction (PCA), or approximate nearest-neighbor strategies.

## Connecting Metric Choice to Data Properties

The same data produces different rankings depending on the comparison metric. This code computes cosine similarity and both L2/L1 distances side by side:

```python
import numpy as np

q = np.array([0.2, 0.8, 0.0])
d1 = np.array([0.1, 0.9, 0.0])
d2 = np.array([0.9, 0.1, 0.0])

def cosine(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

for name, d in [('d1', d1), ('d2', d2)]:
    print(name)
    print('  cosine =', cosine(q, d))
    print('  L2     =', np.linalg.norm(q - d))
    print('  L1     =', np.abs(q - d).sum())
```

In document search, cosine is usually more natural. In physical coordinate error analysis, L2 is more natural. Without defining "similarity" first, evaluation metric choices cannot be consistent either.

## Curse of Dimensionality: When Distance Breaks Down

In high-dimensional spaces, all points appear roughly equidistant — the "curse of dimensionality." This is the main reason distance-based comparisons lose discriminability.

### The Problem: Distance Concentration

In high dimensions, the gap between the nearest and farthest points shrinks relative to the mean distance. Everything looks similarly far away.

```python
import numpy as np

def measure_distance_concentration(dim, n_samples=100):
    """Measure distance distribution by dimensionality."""
    samples = np.random.randn(n_samples, dim)

    # Distances from the first point to all others
    distances = []
    for i in range(1, n_samples):
        dist = np.linalg.norm(samples[0] - samples[i])
        distances.append(dist)

    distances = np.array(distances)
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    min_dist = np.min(distances)
    max_dist = np.max(distances)

    # Discriminability: (max - min) / mean
    discriminability = (max_dist - min_dist) / mean_dist

    return {
        'dim': dim,
        'mean': mean_dist,
        'std': std_dist,
        'min': min_dist,
        'max': max_dist,
        'discriminability': discriminability
    }

# Compare across dimensions
for d in [2, 10, 50, 100, 500]:
    result = measure_distance_concentration(d)
    print(f"Dim {result['dim']:3d}: mean={result['mean']:6.2f}, "
          f"std={result['std']:5.2f}, disc={result['discriminability']:.3f}")
```

### Mitigation Strategies

1. **Normalize + cosine similarity**: Comparing direction instead of magnitude alleviates the high-dimensional problem.
2. **Dimensionality reduction (PCA, t-SNE, UMAP)**: Keep only meaningful dimensions.
3. **Approximate Nearest Neighbor (ANN)**: Libraries like FAISS and Annoy enable efficient search.
4. **Manhattan distance or fractional norms**: Emphasize structure over magnitude.

```python
# Normalization effect demonstration
high_dim = 100
v = np.random.randn(high_dim)
w = np.random.randn(high_dim)

# Raw distances vary widely
print('Before normalization:')
print('  L2 distance:', np.linalg.norm(v - w))
print('  ||v||:', np.linalg.norm(v))
print('  ||w||:', np.linalg.norm(w))

# After normalization
v_n = v / np.linalg.norm(v)
w_n = w / np.linalg.norm(w)
print('\nAfter normalization:')
print('  L2 distance:', np.linalg.norm(v_n - w_n))
print('  cosine similarity:', np.dot(v_n, w_n))
```

Normalization projects vectors onto the unit sphere surface, making direction comparison more stable. This is the primary reason cosine similarity is the standard in high-dimensional embedding search.

## NumPy Computation Routines and Interpretation Checkpoints

This routine works as a reusable verification template across chapters. Recording shape checks, numerical stability, and geometric interpretation together accelerates learning significantly.

```python
import numpy as np

rng = np.random.default_rng(123)
X = rng.normal(size=(6, 4))
v = rng.normal(size=4)
A = rng.normal(size=(4, 4))

print('X shape:', X.shape)
print('v shape:', v.shape)
print('A shape:', A.shape)

# Basic operations
xv = X @ v
Av = A @ v
print('Xv shape:', xv.shape)
print('Av shape:', Av.shape)

# Symmetric matrix and eigenvalue check
S = A.T @ A
eigvals = np.linalg.eigvalsh(S)
print('eigvals(S):', eigvals)

# SVD and rank approximation
U, s, Vt = np.linalg.svd(X, full_matrices=False)
rank = np.linalg.matrix_rank(X)
X2 = U[:, :2] @ np.diag(s[:2]) @ Vt[:2, :]
rel_err = np.linalg.norm(X - X2) / np.linalg.norm(X)

print('rank(X):', rank)
print('singular values:', s)
print('relative error(rank-2):', rel_err)
```

Four items to always verify:

1. **Shape preservation**: Confirm `X @ v` produces shape `(6,)` immediately. Correct values with wrong shapes accumulate errors downstream.
2. **Symmetric positive semi-definite structure**: `A.T @ A` is always symmetric with non-negative eigenvalues. Large negative eigenvalues indicate numerical error or implementation bugs.
3. **Singular value distribution**: Rapidly decaying singular values suggest low-rank approximation can preserve most structure.
4. **Relative reconstruction error**: Judge compression quality with numbers, not intuition.

## Application Scenarios

| Scenario | Linear Algebra Operation | Verification Metric |
|---|---|---|
| Feature compression | SVD/PCA low-dimensional projection | Cumulative variance, reconstruction error |
| Similarity search | Normalize then inner product / cosine | top-k accuracy, scale sensitivity |
| Regression training | `lstsq` or gradient descent | Residual norm, condition number |
| Transform pipeline | Matrix composition `A @ B @ x` | Intermediate shapes, order sensitivity |

## Translating Computations into Sentences

The most common reason linear algebra skills plateau is computing without interpreting. Ask these questions after every calculation:

- What does this operation preserve in space, and what does it change?
- Is the result large because of the transform itself or because of input scale?
- If order matters, which transform applied first?
- Does solving the same problem via a different decomposition (LU/QR/SVD) improve stability?

## Practical Metric Selection: Cosine vs L2 Side by Side

The most common failure in vector comparison is choosing the metric without aligning it to the problem's purpose.

```python
import numpy as np

q = np.array([0.4, 0.2, 0.9])
docs = np.array([
    [0.3, 0.2, 0.8],
    [0.8, 0.1, 0.2],
    [0.1, 0.0, 1.1],
], dtype=float)

docs_n = docs / np.linalg.norm(docs, axis=1, keepdims=True)
q_n = q / np.linalg.norm(q)
cos_score = docs_n @ q_n
l2_dist = np.linalg.norm(docs - q, axis=1)
print('cos:', cos_score)
print('l2 :', l2_dist)
```

The top-ranked document by cosine may differ from the top-ranked by L2. This is not a bug — they answer different questions. Before model evaluation, confirm that your defined "similarity" matches product requirements.

In high-dimensional embeddings, normalization is particularly important. Skipping it lets longer vectors dominate unfairly, distorting search results. Agreeing on inner product vs distance at the design level improves both reproducibility and interpretability of subsequent experiments.

## Five Common Mistakes

1. **Confusing *inner product* with *element-wise product*.**
2. **Forgetting to *normalize* before computing *cosine similarity*.**
3. **Computing the *cosine* of a *zero vector* — *division by zero*.**
4. **Ignoring the *geometric difference* between *Euclidean* and *Manhattan*.**
5. **Forgetting that *distance intuition breaks down in high dimensions* (curse of dimensionality).**

## How This Shows Up in Production

Recommenders (*item similarity*), vector databases (*ANN search*), NLP (*embedding similarity*), clustering (*KMeans*) — all run on *inner products and distances*. Senior engineers choose the metric first then interpret results. For sentence embeddings where direction matters, normalized cosine is natural. For data where absolute magnitude differences matter, distance-based approaches may fit better.

Metric choice also connects to preprocessing outside the model — whether you normalized, whether scales match, whether vectors are sparse or dense. A good comparison metric is the starting point for good search and recommendation quality.

## How a Senior Engineer Thinks

- Choose *cosine vs L2* deliberately.
- Knows that *distance intuition fails in high dimensions*.
- Knows that *normalize-then-dot equals cosine*.
- Sees that *metric choice drives model behavior*.
- Picks *vector database indexes* carefully.

## Checklist

- [ ] You can compute the *inner product*.
- [ ] You can compute *cosine similarity*.
- [ ] You know the difference between *Euclidean* and *Manhattan*.
- [ ] You understand *orthogonality*.

## Practice Problems

1. Compute the *inner product* of `v = [1, 0]` and `w = [0, 1]` and confirm they are *orthogonal*.
2. Build pairs of vectors with *cosine similarity* equal to *1, 0, -1*.
3. Build an example where *Euclidean* and *Manhattan* distances differ.

## Wrap-up and Next Steps

The inner product tells you how aligned two vectors are; cosine similarity isolates direction; distance measures spatial separation. Distinguishing these three lets you read topics like vector search, recommendations, and clustering with much more clarity.

The next post covers linear transformations — now that you have comparison tools, we will see how matrices change the vector space itself.

## Answering the Opening Questions

- **Why does the inner product collapse to a single number?**
  - The inner product computes `v @ w` by multiplying coordinates pairwise and summing everything into one scalar. In the example with `v = [1,2,3]` and `w = [4,5,6]`, the result was `32.0`—a single number summarizing how aligned the two vectors are.
- **How does cosine similarity connect to the inner product?**
  - Cosine similarity is `(v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))`—the inner product divided by both vector lengths. It removes magnitude effects and leaves only direction. The example's ~`0.975` means the two vectors point in quite similar directions.
- **What distinguishes Euclidean distance from Manhattan distance?**
  - Euclidean distance `np.linalg.norm(v - w)` measures the straight-line length of the difference vector; Manhattan distance `np.sum(np.abs(v - w))` sums coordinate-wise travel. For the same `v, w` one gave ~`5.196` and the other `9.0`—two different definitions of "closeness."
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- **Inner Product and Distance (current)**
- Linear Transformations (upcoming)
- Basis and Dimension (upcoming)
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Dot products](https://www.3blue1brown.com/lessons/dot-products)
- [Stanford CS229 — Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)
- [scikit-learn — Pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html)
- [Khan Academy — Dot and cross products](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces/dot-cross-products)

Tags: LinearAlgebra, InnerProduct, Distance, DataScience, Beginner
