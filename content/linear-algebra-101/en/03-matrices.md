---
series: linear-algebra-101
episode: 3
title: "Linear Algebra 101 (3/10): Matrices"
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

# Linear Algebra 101 (3/10): Matrices

Matrices are the notation you see most often in linear algebra. Sometimes they look like tables that hold data. Sometimes they act like rules that move one vector into another. If you only remember the table view, you can still run the arithmetic without understanding why multiplication deserves so much attention.

This is the 3rd post in the Linear Algebra 101 series. Here we will read matrices through two linked perspectives: shape and transformation.


![linear algebra 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/03/03-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 3 flow overview*
> A matrix is not just a number grid. It is a transformation rule, and its structure (especially the number of rows and columns) defines not just the size but the very spaces of input and output.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Matrices?
- Which signal should the example or diagram make visible for Matrices?
- What failure should be prevented first when Matrices reaches a real system?

## Questions This Post Answers

- What makes a matrix more than a rectangular table of numbers?
- Why is matrix multiplication easier to read as composition of transformations?
- What do transpose, identity, and inverse each mean operationally?
- Why does checking shape first prevent so many practical mistakes?

> A matrix is both a compact display of numbers and a compressed rule acting on a vector space. Matrix multiplication comes alive only when those two readings stay connected.

## Why It Matters

Design matrices in regression, weight matrices in neural networks, user-item structures in recommenders, and transformation matrices in graphics all rely on the same object. A matrix is simultaneously storage and engine.

Many production mistakes start as shape mistakes. If you cannot read how many dimensions go in, how many come out, and what kind of transformation is implied, code may run while the meaning is already wrong. Matrices reward the habit of reading structure before values.

## Key Terms

- **Matrix**: an `m x n` *array of numbers*.
- **Transpose**: *swap rows and columns* — `A^T`.
- **Identity I**: ones on the diagonal, zeros elsewhere — `I v = v`.
- **Inverse**: `A A^-1 = I` — only for *square* matrices, and not always exists.
- **Matrix product**: `(m x k)(k x n) = (m x n)` — *inner dimensions must match*.
- **Condition number**: measures how much small input errors get amplified in the solution.

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

## Extended NumPy Matrix Operations

NumPy provides comprehensive matrix functions. Below is a pattern covering the operations you encounter most in practice:

```python
import numpy as np

# 1. Build a 3x3 matrix (intentionally non-singular)
A = np.array([[1.0, 2.0, 3.0],
              [4.0, 5.0, 6.0],
              [7.0, 8.0, 10.0]])

print('A:', A)
print('shape:', A.shape)
print('dtype:', A.dtype)

# 2. Transpose
print('A^T:', A.T)
print('A^T shape:', A.T.shape)

# 3. Matrix product (inner dimensions must match)
B = np.array([[1.0, 0.0],
              [0.0, 1.0],
              [1.0, 1.0]])
C = A @ B
print('A @ B:', C)
print('result shape:', C.shape)

# 4. Element-wise product (Hadamard product)
D = np.array([[1.0, 2.0, 3.0],
              [1.0, 2.0, 3.0],
              [1.0, 2.0, 3.0]])
E = A * D
print('A * D (element-wise):', E)

# 5. Inverse (exists only for square, full-rank matrices)
try:
    A_inv = np.linalg.inv(A)
    print('A^-1:', A_inv)
    print('A @ A^-1:', A @ A_inv)
except np.linalg.LinAlgError:
    print('A has no inverse (singular matrix)')

# 6. Determinant
det = np.linalg.det(A)
print('det(A):', det)

# 7. Diagonal matrix
diag_vals = np.array([2.0, 3.0, 4.0])
D_matrix = np.diag(diag_vals)
print('diagonal matrix:', D_matrix)

# 8. Special matrices
I = np.eye(3)
zeros = np.zeros((3, 3))
ones = np.ones((3, 3))
print('identity:', I)
print('zeros:', zeros)
print('ones:', ones)
```

In practice, distinguishing `@` (matrix product) from `*` (element-wise product) is critical. Also, since an inverse does not always exist, wrapping with `try-except` or preferring `np.linalg.solve` is safer.

## Reading a Matrix as an Interpretable Operation

A matrix is stored like a table but acts like a transformation device. This example performs multiplication, linear-system solving, and condition-number checking on the same matrix:

```python
import numpy as np

A = np.array([[3.0, 1.0],
              [1.0, 2.0]])
b = np.array([9.0, 8.0])

x = np.linalg.solve(A, b)
A_inv = np.linalg.inv(A)

print('solution x =', x)
print('check A@x =', A @ x)
print('cond(A) =', np.linalg.cond(A))
print('inv-based x =', A_inv @ b)
```

`solve` and `inv @ b` are mathematically identical, but numerically `solve` is generally more stable. As `cond(A)` grows, small input errors amplify significantly in the solution — monitoring the condition number is useful in production code.

## Verifying Matrix Multiplication Meaning Step by Step

To strengthen the habit of reading matrix multiplication as "composition of transformations," print intermediate results explicitly:

```python
B = np.array([[1.0, -1.0],
              [2.0,  0.0]])
v = np.array([2.0, 1.0])

first = B @ v
second = A @ first
direct = (A @ B) @ v

print('Bv =', first)
print('A(Bv) =', second)
print('(AB)v =', direct)
print('same?', np.allclose(second, direct))
```

Once this verification becomes habitual, you can logically trace operation order even in complex models.

## Application Connection Table

| Task | Matrix Role | Recommended Approach |
|---|---|---|
| Linear regression | Design matrix | `lstsq`, QR/SVD-based solver |
| Recommender systems | User-item interaction | Low-rank factorization, missing-value handling |
| Graphics | Coordinate transformation | Composition order, homogeneous coordinate check |

A matrix is not just something to observe for size and values — it is a design object where numerical stability, interpretability, and computational cost must be considered together.

## Three Interpretations of Matrix Multiplication

Matrix multiplication `AB` can be read from three perspectives, each useful in different contexts.

### 1. Composition of linear transformations

This is the most fundamental reading. `AB` means "apply `B` first, then apply `A`."

```python
import numpy as np

# Compose rotation and scaling
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.array([[2.0, 0.0],
              [0.0, 0.5]])

v = np.array([1.0, 0.0])

# Two equivalent approaches
result1 = R @ (S @ v)   # scale first, then rotate
result2 = (R @ S) @ v   # pre-compose the transformation matrix

print('R(Sv):', result1)
print('(RS)v:', result2)
print('same?', np.allclose(result1, result2))
```

### 2. Collection of dot products

From a row perspective, element `C[i, j]` of `C = AB` is the dot product of row `i` of `A` and column `j` of `B`.

```python
A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])

C = A @ B

# Manual verification
c00 = np.dot(A[0, :], B[:, 0])
c01 = np.dot(A[0, :], B[:, 1])
c10 = np.dot(A[1, :], B[:, 0])
c11 = np.dot(A[1, :], B[:, 1])

C_manual = np.array([[c00, c01],
                     [c10, c11]])

print('C:', C)
print('C_manual:', C_manual)
print('same?', np.allclose(C, C_manual))
```

### 3. Graph adjacency matrix

In graph theory, if `A` is an adjacency matrix, then `A^2[i, j]` counts the number of length-2 paths from node `i` to node `j`.

```python
# Directed graph: 0->1, 1->2, 2->0
A = np.array([[0, 1, 0],
              [0, 0, 1],
              [1, 0, 0]])

A2 = A @ A
print('A (1-hop):', A)
print('A^2 (2-hop):', A2)
# A^2[i, j] = number of length-2 paths from i to j
```

All three interpretations describe the same computation, but different problems make different perspectives natural. Composition of transformations dominates in geometry and ML; dot-product collections appear in statistics and optimization; the graph reading drives network analysis.

## NumPy Routines and Interpretation Checkpoints

The routine below serves as a reusable verification template across chapters. Recording shape checks, numerical stability, and geometric interpretation alongside every matrix/vector operation accelerates learning:

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

# Symmetric matrix construction + eigenvalue check
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

1. **Shape preservation**: confirm `X @ v` yields shape `(6,)` immediately. Even correct values with wrong shape cascade errors downstream.
2. **Symmetric positive semi-definite structure**: `A.T @ A` is always symmetric and eigenvalues must be non-negative. Large negative values indicate numerical error or implementation bugs.
3. **Singular value distribution**: if singular values drop sharply, a low-rank approximation can retain most of the structure.
4. **Relative reconstruction error**: judge compression quality by numbers, not intuition.

## Translating Computation Results into Sentences

The most common reason linear algebra skill plateaus is performing computations without recording interpretations. Asking these questions after every operation builds interpretive muscle:

- What does this operation preserve in the space, and what does it change?
- Did the result magnitude grow because of the transformation scale or the input scale?
- If reversing the order changes the result, which transformation was applied first?
- Does recomputing via decomposition (LU/QR/SVD) improve stability?

## Application Scenarios

| Scenario | Linear Algebra Operation | Checkpoint Metric |
|---|---|---|
| Feature compression | SVD/PCA low-dimensional projection | Cumulative variance, reconstruction error |
| Similarity search | Normalize then dot product / cosine | Top-k accuracy, scale sensitivity |
| Regression training | `lstsq` or gradient descent | Residual norm, condition number |
| Transformation pipeline | Matrix composition `A @ B @ x` | Intermediate shapes, order sensitivity |

Using this table as a lab-notebook template naturally connects one chapter's computations to the next chapter's concepts.

## Shape Checking and Transformation Interpretation in Practice

More than half of matrix errors in production start not from wrong values but from wrong shapes. Check `shape` before computing, then interpret what each matrix means as a transformation:

```python
import numpy as np

X = np.array([[1.0, 2.0, 3.0],
              [0.5, 0.1, 0.2]])   # (2, 3)
W = np.array([[0.2, -0.3],
              [1.1,  0.4],
              [0.7,  0.2]])       # (3, 2)

Y = X @ W                         # (2, 2)
print('X:', X.shape, 'W:', W.shape, 'Y:', Y.shape)
```

Each column of `W` defines an axis in the output space — it shows how the three input features are mixed to produce two new axes. Reading neural-network weights with this same perspective makes it clearer how the model re-represents its inputs in a new coordinate system.

Visualization matters too. Plotting a 2D point cloud before and after applying a rotation or shear matrix confirms intuitively that matrix multiplication is a structural transformation of space, not just arithmetic.

## Read One Numeric Pass

- `A @ B` yields `[[19., 22.], [43., 50.]]`, while `B @ A` yields `[[23., 34.], [31., 46.]]`. The numbers make non-commutativity impossible to ignore.
- `A @ I` returns `A`, which is the algebraic version of "do nothing."
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

A senior engineer reads structure before values. How many dimensions go in, how many come out, and whether this matrix represents data or a transformation — that distinction comes first. Only then does debugging separate shape issues from semantic issues.

- *Avoid explicit inverses* — solve via *decompositions* (QR, SVD, LU).
- *Always check shapes*.
- Be aware of *non-commutativity*.
- Use *purpose-built solvers* for *numerical stability*.
- *Visualize* the *geometric meaning*.

Mastering matrices means less "knowing formulas" and more "judging which tool solves a given problem stably."

## Checklist

- [ ] You can do *matrix multiplication*.
- [ ] You can *transpose*.
- [ ] You know when an *inverse exists*.
- [ ] You are aware of *non-commutativity*.
- [ ] You can distinguish `@` (matrix product) from `*` (element-wise).
- [ ] You check condition number before using inverse in production.

## Practice Problems

1. Compute by hand the *transpose* and *inverse* of a 2x2 matrix `A`.
2. Multiply the *identity matrix* `I` with an arbitrary vector and check the result is unchanged.
3. Build an example of a *singular matrix* and explain why its *inverse does not exist*.

## Wrap-up and Next Steps

A matrix is a *compressed transformation*. Transpose swaps axis roles, the identity matrix applies no change, and matrix multiplication chains transformations together. Once this perspective clicks, matrices stop being a collection of arithmetic rules and become a practical tool for manipulating spaces.

The next post covers *inner product and distance* — now that you have seen how matrices transform vectors, it is time to measure how similar or far apart vectors are.

## Answering the Opening Questions

- **How is a matrix different from a plain number table?**
  - A matrix is an `m × n` array of numbers, but in this article we read `A.shape` as the rule determining which vectors go in and which come out. So `A = np.array([[1.0, 2.0], [3.0, 4.0]])` is simultaneously a table of values and a linear transformation sending 2D vectors to other 2D vectors.
- **Why should you read matrix multiplication as composition of transformations?**
  - `A @ B` and `B @ A` gave different results (`[[19., 22.], [43., 50.]]` vs. `[[23., 34.], [31., 46.]]`) precisely because the composition order differs. Reading matrix products as "first `B`, then `A`" makes non-commutativity feel natural.
- **What do transpose, identity matrix, and inverse each mean?**
  - `A.T` swaps the roles of rows and columns. `np.eye(2)` produces `I` such that `A @ I = A` — a reference point that applies no transformation. `np.linalg.inv(A)` gives `A_inv` that brings `A @ A_inv` close to the identity, so the inverse restores the original transformation when it exists.
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
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
