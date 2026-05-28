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

## Before/After

**Before**: "Matrices are just tables of numbers."

**After**: "A matrix is a linear transformation; multiplication composes transformations.

## Key Terms

- **vector**: *direction and magnitude*.
- **matrix**: a *collection of vectors*.
- **dot product**: a *similarity* score.
- **transpose**: swap *rows and columns*.
- **basis**: the *axes* of a space.

## Before/After

**Before**: element-wise *for loops*.

**After**: a single *vectorized* line.

## Hands-on: Mini Linear Algebra Kit

### Step 1 — Vector Add

```python
def vadd(a, b):
    return [x + y for x, y in zip(a, b)]
```

### Step 2 — Dot Product

```python
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))
```

### Step 3 — Matrix-Vector

```python
def matvec(M, v):
    return [dot(row, v) for row in M]
```

### Step 4 — Transpose

```python
def transpose(M):
    return [list(col) for col in zip(*M)]
```

### Step 5 — Matrix-Matrix

```python
def matmul(A, B):
    Bt = transpose(B)
    return [[dot(row, col) for col in Bt] for row in A]
```

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

## How a Senior Engineer Thinks

- *Vectors* are *data*.
- *Matrices* are *transforms*.
- *Vectorization* is *performance*.
- *Basis* is *interpretation*.
- Mind *numerical stability* too.

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
