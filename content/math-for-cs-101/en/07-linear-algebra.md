---
series: math-for-cs-101
episode: 7
title: "Math for CS 101 (7/10): Linear Algebra"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - LinearAlgebra
  - Vectors
  - Matrices
  - Beginner
seo_description: A beginner-friendly tour of vectors, matrices, dot products, matrix multiplication, transpose, and basis intuition for CS
last_reviewed: '2026-05-04'
---

# Math for CS 101 (7/10): Linear Algebra

Linear algebra often feels intimidating to beginners because the notation becomes dense fast. In practice, though, the topic is less about ceremonial symbols and more about one useful idea: representing data and transformations in a compact, reusable form.

Embeddings, dimensionality reduction, camera transforms, and neural network forward passes all become easier to understand once vectors and matrices stop looking like mysterious tables and start looking like data plus movement rules.

This is the 7th post in the Math for CS 101 series.

Here we use linear algebra as a practical language for data, similarity, and transformation.


![math for cs 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/07/07-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 7 flow overview*
> Vectors and matrices structure data transformations and form the foundation of machine learning, recommender systems, and optimization.

## Questions to Keep in Mind

- How do vectors and matrices represent data in a useful way?
- Why is the dot product so central to similarity and scoring?
- What is the difference between a matrix as a table and a matrix as a transform?

## Why It Matters

Embedding search, recommenders, PCA, 3D graphics, and neural nets all depend on linear algebra. The common theme is not just computation speed. It is that vectors and matrices give you a way to describe meaning, similarity, and transformation in one framework.

That shift matters in engineering work because many bugs are not arithmetic mistakes. They are interpretation mistakes: using the wrong axis, misunderstanding the shape, or forgetting what a column actually means.

Linear algebra studies *vectors* (direction and magnitude), *matrices* (transformations), and *eigenvalues* (intrinsic properties). It is the language of scale and symmetry.

## How a Senior Engineer Thinks About Linear Algebra

Embedding search runs on vector similarity. Recommender systems use matrix factorization or score computation backed by linear algebra. 3D graphics depend on coordinate transforms. Neural network computation is ultimately large matrix operations. Linear algebra is not domain-specific knowledge—it is a shared foundation reused extremely broadly across modern software systems.

A good engineer, when looking at an array of numbers, asks about dimensions and meaning first: What does this axis represent? Is this matrix data or a transformation? Why is the transpose needed? Are there numerical stability concerns?

## Before/After

**Before**: "Matrices are just tables of numbers."

**After**: "A matrix is a linear transformation; multiplication composes transformations."

## Key Terms

- **vector**: *direction and magnitude*.
- **matrix**: a *collection of vectors*.
- **dot product**: a *similarity* score.
- **transpose**: swap *rows and columns*.
- **basis**: the *axes* of a space.

## Hands-on: Mini Linear Algebra Kit

### Step 1 — Vector Add

```python
def vadd(a, b):
    return [x + y for x, y in zip(a, b)]
```

The simplest operation, yet it builds the intuition that vectors are objects you manipulate position-by-position. Thinking of a vector as a single entity rather than a list of independent numbers is the starting point for everything that follows.

### Step 2 — Dot Product

```python
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))
```

The dot product appears in recommendation scores, similarity measures, and projection calculations. It tells you how much two vectors point in the same direction—in practice it is felt more as a comparison grammar than a raw computation.

### Step 3 — Matrix-Vector

```python
def matvec(M, v):
    return [dot(row, v) for row in M]
```

Reading a matrix as a transformation device makes it click: feed in one vector, get a transformed vector out. A matrix is less a table of numbers and more a machine that recombines directions and magnitudes.

### Step 4 — Transpose

```python
def transpose(M):
    return [list(col) for col in zip(*M)]
```

Transpose swaps rows and columns. It shows up whenever you need to switch between row-oriented and column-oriented views—common when reshaping data for algorithms that expect a specific layout.

### Step 5 — Matrix-Matrix

```python
def matmul(A, B):
    Bt = transpose(B)
    return [[dot(row, col) for col in Bt] for row in A]
```

Matrix multiplication is a grid of dot products. Understanding this decomposition demystifies neural network layers, coordinate transforms, and any pipeline where transformations chain together.

## NumPy Vector and Matrix Operations

The fastest way to build linear algebra intuition is to manipulate the same operations directly in `numpy`.

```python
import numpy as np

A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[2.0, 0.0], [1.0, 2.0]])
v = np.array([5.0, 6.0])

mat_vec = A @ v
mat_mul = A @ B
transposed = A.T
```

The `@` operator here is not simple multiplication—it is linear transformation composition. The same operator carries different meanings depending on operand shapes, and keeping that distinction clear is essential.

## Eigenvalues and Eigenvectors

An eigenvalue represents the scaling factor along a direction that remains unchanged after the transformation.

```python
eigvals, eigvecs = np.linalg.eig(A)
print("eigvals", eigvals)
print("eigvecs", eigvecs)
```

In recommender systems, PCA, and dynamical-system stability analysis, eigenvalues summarize the dominant patterns of a system. They are a compression tool that lets you read structure without examining every value.

## Geometric Transformation Example

A 2D rotation matrix is expressed as:

```python
def rotation(theta_rad: float) -> np.ndarray:
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    return np.array([[c, -s], [s, c]])

p = np.array([1.0, 0.0])
p_rot = rotation(np.pi / 2) @ p
```

When you read a matrix as "a function that changes space" rather than "a table of numbers," most of linear algebra becomes far more intuitive. Rotation, scaling, and translation composed as matrices make transformation chaining explicit. In graphics and robotics, operation order determines the result, so coordinate-system conventions must be managed strictly.

## Dimension Interpretation Table

| Notation | Meaning | Example |
|---|---|---|
| `(n,)` | Length-n vector | User embedding |
| `(m, n)` | m-row, n-column matrix | Batch input |
| `(n, k)` | n-dim → k-dim transformation | Weight matrix |

Dimensions are types. Just as missing type checks produce runtime errors, missing dimension analysis produces semantic errors in mathematics.

## Numerical Stability Notes

- Prefer solving linear systems `Ax = b` via `np.linalg.solve` over computing the inverse directly.
- When very large and very small values coexist, normalize to equalize scale.
- Matrices with large condition numbers are sensitive to error—interpret results with caution.

These points cause problems more often in implementation than in theory. Understanding them prevents subtle bugs in production numerical code.

## Cosine Similarity and Embedding Search

The most common computation in recommendation and search is cosine similarity.

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def batch_cosine_similarity(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    """Compute similarity between a query vector and an entire corpus."""
    norms = np.linalg.norm(corpus, axis=1)
    norms[norms == 0] = 1.0  # prevent zero-division
    normalized = corpus / norms[:, np.newaxis]
    query_norm = query / (np.linalg.norm(query) or 1.0)
    return normalized @ query_norm

# Example
corpus = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 0]], dtype=float)
query = np.array([1, 0, 0], dtype=float)
scores = batch_cosine_similarity(query, corpus)
print(f"similarities: {scores}")  # first and third are highest
```

The dot product alone is sensitive to vector magnitude. Cosine similarity normalizes by norms, comparing direction only—making it magnitude-independent. In embedding-based search (vector search), both query and documents are normalized and then ranked by dot product alone. This is why vector databases like FAISS, Pinecone, and Weaviate accelerate this operation with GPU/SIMD.

## PCA: Dimensionality Reduction

When you need to visualize high-dimensional data or reduce model input size, PCA (Principal Component Analysis) finds the directions of greatest variance and projects onto them.

```python
import numpy as np

def pca(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Reduce X to n_components dimensions."""
    # 1. Center the data
    X_centered = X - X.mean(axis=0)

    # 2. Covariance matrix
    cov = np.cov(X_centered, rowvar=False)

    # 3. Eigen-decomposition
    eigvals, eigvecs = np.linalg.eigh(cov)

    # 4. Sort by eigenvalue magnitude
    idx = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, idx]

    # 5. Project onto top components
    W = eigvecs[:, :n_components]
    return X_centered @ W

# Example: 5-dimensional data to 2 dimensions
np.random.seed(42)
X = np.random.randn(100, 5)
X_reduced = pca(X, 2)
print(f"original: {X.shape} -> reduced: {X_reduced.shape}")
```

The key insight: the eigenvectors of the covariance matrix point along directions of maximum variance, and the eigenvalues quantify how much information each axis carries. Large eigenvalue = informative axis. PCA is used in embedding visualization, noise removal, and feature selection. In production you use `sklearn.decomposition.PCA`, but understanding the internals helps you choose `n_components` and interpret explained variance ratios correctly.

## Sparse Matrices

Most real-world matrices are overwhelmingly zero. Sparse matrix formats save memory and computation.

```python
from scipy import sparse
import numpy as np

# 10000x10000 matrix with only 0.1% nonzero
n = 10000
density = 0.001
A_sparse = sparse.random(n, n, density=density, format="csr")

# Memory comparison
dense_memory = n * n * 8  # float64
sparse_memory = A_sparse.data.nbytes + A_sparse.indices.nbytes + A_sparse.indptr.nbytes
print(f"dense: {dense_memory / 1e6:.1f} MB")
print(f"sparse: {sparse_memory / 1e6:.1f} MB")
print(f"ratio: {sparse_memory / dense_memory:.4f}")

# Sparse matrix-vector product
x = np.random.randn(n)
result = A_sparse @ x
print(f"result shape: {result.shape}")
```

User-item matrices in recommender systems, graph adjacency matrices, and TF-IDF matrices in NLP are all sparse. Treating them as dense hits memory limits and blocks scaling. Understanding CSR/CSC format characteristics lets you predict which operations will be fast.

## Solving Linear Systems: Ax = b

Many practical problems reduce to the linear system Ax = b—regression, circuit equations, optimization sub-problems.

```python
import numpy as np

# 3 equations, 3 unknowns
A = np.array([
    [2, 1, -1],
    [-3, -1, 2],
    [-2, 1, 2]
], dtype=float)
b = np.array([8, -11, -3], dtype=float)

# Solve
x = np.linalg.solve(A, b)
print(f"solution: {x}")  # [2. 3. -1.]

# Verify
residual = np.linalg.norm(A @ x - b)
print(f"residual: {residual:.2e}")  # ~0

# Check condition number
cond = np.linalg.cond(A)
print(f"condition number: {cond:.2f}")
```

A large condition number (say 10⁶ or above) means small input errors get amplified into large output errors. In that case, consider normalization, SVD-based pseudo-inverse, or iterative solvers (CG, GMRES). In numerical linear algebra, getting an answer is not the finish line—evaluating how trustworthy that answer is matters equally.

## Linear Algebra Debugging Order

When matrix computations produce unexpected results, check axes before values. Verify input tensor axis definitions, transpose presence, and broadcasting behavior first, then check numerical ranges. Most errors narrow down quickly with this order. In model inference, automating NaN-origin tracking is especially valuable.

Additionally, splitting per-operation unit tests by axis catches regressions much faster.

## What to Notice in This Code

- *Dot product* is the core op.
- *Transpose* is one *zip* call.
- *Matmul* is a *grid of dot products*.

## Five Common Mistakes

1. **Mismatching *row/column* dimensions.**
2. **Assuming matrix multiplication is *commutative*.**
3. **Confusing *dot* and *cross* products.**
4. **Skipping *numpy* and losing performance.**
5. **Thinking *transpose* mutates the original.**

## How This Shows Up in Production

*Embedding search*, *ranking scores*, *camera transforms*, and *neural net forward passes* are all matrix ops.

## Checklist

- [ ] State *dimensions*.
- [ ] *Vectorize* loops.
- [ ] Make *transpose* intent explicit.
- [ ] Inspect *numerical stability*.

## Practice Problems

1. Define the *dot product* in one line.
2. Define *transpose* in one line.
3. State the *condition* for matrix multiplication.

## Wrap-up and Next Steps

Linear algebra gives you a compact way to talk about direction, similarity, and transformation. Once those concepts feel natural, modern data and ML systems look much less like black boxes.

Next, we move into calculus, where the focus becomes change, direction, and optimization.

## Answering the Opening Questions

- **How do vectors and matrices represent data?**
  - This article described vectors as individual data objects and matrices as transformations that move them. The examples `A @ v`, rotation `rotation(theta) @ p`, PCA's `X_centered @ W`, and sparse `A_sparse @ x` showed that reading matrices as data-and-transformation contracts (not number tables) makes meaning clear.
- **Why is the inner product the core operation for similarity computation?**
  - The inner product summarizes how much two vectors point the same direction, making it the center of recommendation scores and embedding comparison. Especially with norm-division like `cosine_similarity` and `batch_cosine_similarity`, magnitude differences are removed, leaving only direction—ready for search and recommendation.
- **How is matrix multiplication different from simple repeated calculation?**
  - Matrix multiplication is not a shortcut for loops—it's a mathematical operation that composes transformations. `matmul(A, B)` and `A @ B` mean "apply one transformation then another," so `B @ A` can differ. Dimension, axis interpretation, and transpose must all be checked for a correct model.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- [Math for CS 101 (5/10): Combinatorics](./05-combinatorics.md)
- [Math for CS 101 (6/10): Probability](./06-probability.md)
- **Linear Algebra (current)**
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Linear Algebra - 3Blue1Brown](https://www.3blue1brown.com/topics/linear-algebra)
- [Linear Algebra - Khan Academy](https://www.khanacademy.org/math/linear-algebra)
- [Introduction to Linear Algebra - Strang](https://math.mit.edu/~gs/linearalgebra/)
- [NumPy Linear Algebra Documentation](https://numpy.org/doc/stable/reference/routines.linalg.html)
- [NumPy GitHub repository](https://github.com/numpy/numpy)

Tags: Math, LinearAlgebra, Vectors, Matrices, Beginner
