---
series: linear-algebra-101
episode: 2
title: "Linear Algebra 101 (2/10): Vectors"
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
  - Vectors
  - NumPy
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to vectors — definition, addition, scalar multiplication, norms, and normalization with NumPy code and geometric intuition
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (2/10): Vectors

In machine learning, one row of data is a vector, an embedding is a vector, and a gradient is a vector too. But if you treat vectors as plain number bundles, the calculations may still work while the meaning slips away. A vector is both algebraic notation and a geometric object.

This is the 2nd post in the Linear Algebra 101 series. Here we will read vectors through three lenses at once: coordinates, arrows, and data representations.


![linear algebra 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/02/02-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 2 flow overview*
> A vector is both a container of numbers and the smallest unit of direction in a space. You need both views to connect linear algebra to machine learning.

## Questions to Keep in Mind

- What makes a vector different from an ordinary list?
- What do vector addition and scalar multiplication mean geometrically?
- Why does a norm mean more than just a length formula?

## Why It Matters

Feature rows, user embeddings, token embeddings, and gradients are all represented as vectors. Once you can read vectors cleanly, you can move from preprocessing to model internals without switching mental languages.

This matters quickly in practice. Similarity search, normalization, and metric choice all become fragile when you cannot tell whether direction matters, magnitude matters, or both matter. Vectors are the first chapter of linear algebra, but they remain the basic unit all the way to production systems.

## Vector Operations

Vector operations look simple at the coordinate level, but become much more powerful once you understand their geometric meaning. The table below shows the key operations, their geometric interpretation, and the NumPy code.

| Operation | Geometric Meaning | NumPy Code |
|---|---|---|
| Addition | Join arrows tip-to-tail | `v + w` |
| Scalar multiplication | Scale length + flip direction | `a * v` |
| Dot product | Degree of directional alignment | `v @ w` or `np.dot(v, w)` |
| Cross product (3D) | Vector orthogonal to both inputs | `np.cross(v, w)` |

The dot product is covered in post 4, and the cross product mainly appears in 3D geometry. For this post, addition, scalar multiplication, norms, and normalization are the focus.

## Concept at a Glance

Reading a vector through three views makes everything easier. In geometry it is an arrow, in algebra it is a coordinate tuple, and in machine learning it is one row of data. The representations differ but the underlying object is the same.

## Key Terms

- **Vector**: an *ordered bundle of numbers* — `[x1, x2, ..., xn]`.
- **Dimension**: the *number of entries* in the vector.
- **Norm ||v||**: the *magnitude* — usually *Euclidean length*.
- **Unit vector**: a vector with norm *1*.
- **Scalar multiplication**: changes the *length* and possibly *flips direction*.

## Before/After

**Before**: *"A vector is just a list."* — no geometric meaning.

**After**: *"A vector is a *point/arrow in space*, and *operations are geometric transformations*."*

## Hands-on: Five Steps with Vectors

### Step 1 — Build vectors

```python
import numpy as np
v = np.array([3.0, 4.0])
w = np.array([1.0, 2.0])
print("v:", v, "w:", w)
```

Two vectors prepared. What matters here is not the values but the dimension. Only vectors of the same dimension can be added or subtracted naturally.

### Step 2 — Addition and subtraction

```python
print("v+w:", v + w)
print("v-w:", v - w)
```

Vector addition can be seen as chaining two moves in the same space. Subtraction produces the difference pointing from one vector to the other.

### Step 3 — Scalar multiplication

```python
print("2v:", 2 * v)
print("-v:", -v)
```

Scalar multiplication adjusts a vector's length. Positive scalars change magnitude; negative scalars also flip direction. This is where the geometric nature of a vector becomes unmistakable.

### Step 4 — Norm

```python
norm_v = np.linalg.norm(v)
print("||v||:", norm_v)
```

A norm summarizes a vector's magnitude as a single number. It reappears constantly when you study dot products, distances, and cosine similarity, so building intuition here pays off.

### Step 5 — Normalize to a unit vector

```python
unit_v = v / np.linalg.norm(v)
print("unit v:", unit_v, "norm:", np.linalg.norm(unit_v))
```

Normalization keeps the direction and forces length to 1. In problems where direction comparison matters more than magnitude, this step is almost a default preprocessing.

## Read One Numeric Pass

- `v + w` becomes `[4., 6.]`, while `v - w` becomes `[2., 2.]`. The coordinate arithmetic is simple, but the geometric meaning is different.
- `||[3, 4]||` is `5.0`, so the familiar 3-4-5 triangle shows up immediately.
- Normalization gives roughly `[0.6, 0.8]`, which keeps direction and forces the norm to 1.

## What to Notice in This Code

- *NumPy* vector operations are *element-wise*.
- The *default norm* is *L2 (Euclidean)*.
- *Normalization* keeps *direction* and forces *length 1*.
- Row vs column vector distinction grows more important in later posts.

## Cosine Similarity with NumPy

Cosine similarity is one of the most common comparison metrics in document embeddings, recommender systems, and vector search. Below is a direct implementation.

```python
import numpy as np

def cosine_similarity(a, b):
    """
    Compute cosine similarity.
    cos(a, b) = (a · b) / (||a|| ||b||)
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Guard against zero vectors
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)

# Example: comparing two document embeddings
doc1 = np.array([0.5, 0.8, 0.2])
doc2 = np.array([0.6, 0.7, 0.3])
doc3 = np.array([0.1, 0.1, 0.9])

print('doc1 vs doc2:', cosine_similarity(doc1, doc2))
print('doc1 vs doc3:', cosine_similarity(doc1, doc3))
print('doc2 vs doc3:', cosine_similarity(doc2, doc3))

# Normalized vectors: dot product = cosine similarity
doc1_n = doc1 / np.linalg.norm(doc1)
doc2_n = doc2 / np.linalg.norm(doc2)
print('normalized dot:', np.dot(doc1_n, doc2_n))
print('cosine:', cosine_similarity(doc1, doc2))
```

For normalized vectors, the dot product itself equals cosine similarity. That is why in practice embeddings are often pre-normalized so only the dot product needs to be computed — faster and simpler.

## Extending Vector Operations to Practical Intuition

The three most common practical questions when working with vectors: compare magnitude, compare direction, or both. The code below computes all three metrics on the same vector pair.

```python
import numpy as np

a = np.array([3.0, 1.0, -2.0])
b = np.array([6.0, 2.0, -4.0])
c = np.array([1.0, -1.0, 0.0])

def cosine(u, v):
    return (u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))

print('||a||, ||b||, ||c|| =', np.linalg.norm(a), np.linalg.norm(b), np.linalg.norm(c))
print('cos(a,b) =', cosine(a, b))
print('cos(a,c) =', cosine(a, c))
print('L2(a,c) =', np.linalg.norm(a - c))
print('L1(a,c) =', np.abs(a - c).sum())
```

`a` and `b` differ only in magnitude — direction is identical — so cosine similarity is close to 1. `a` and `c` differ in both direction and magnitude, so both cosine and distance values diverge.

## Geometric Interpretation: What Normalization Keeps and Discards

Normalization discards magnitude and retains only direction. In recommendation, search, and sentence-embedding problems where "direction is meaning," this is powerful. In problems where magnitude itself carries information — payment amounts, sensor absolute values — normalizing blindly destroys useful signal.

Separating the two steps makes interpretation clear:

```python
x = np.array([10.0, 0.0])
y = np.array([1.0, 0.0])

x_n = x / np.linalg.norm(x)
y_n = y / np.linalg.norm(y)

print('raw dot:', x @ y)
print('normalized dot:', x_n @ y_n)
```

The raw dot product is 10 (reflecting the magnitude difference), but the normalized dot product is 1 (only direction remains).

## Application Table: Deciding How to Interpret Vectors

| Problem Type | Vector Meaning | Primary Metric | Watch Out For |
|---|---|---|---|
| Sentence/document embedding search | Semantic direction | Cosine similarity | Zero-vector guard, normalization required |
| Numeric feature regression | Absolute magnitude + direction | L2-based | State scaling decision explicitly |
| Anomaly detection | Deviation from normal center | Distance function | High-dimensional distance distortion |

The right answer for vector operations is not universal — it is "the comparison metric that matches the problem definition." If this judgment wavers, downstream model performance discussions will waver too.

## High-Dimensional Vector Intuition

Thinking of vectors only in 2D or 3D breaks intuition in high-dimensional problems. But the same rules apply in every dimension.

### High Dimensions = Feature Space

In ML, a 100-dimensional vector represents one data point with 100 features. You cannot visualize it, but the arithmetic rules are identical to 2D. Addition is still element-wise, and the norm still represents length.

```python
import numpy as np

# High-dimensional vector example
dim = 128
v = np.random.randn(dim)
w = np.random.randn(dim)

# Same operations work identically
v_plus_w = v + w
norm_v = np.linalg.norm(v)
unit_v = v / norm_v

print(f'{dim}-dim vector')
print('v + w shape:', v_plus_w.shape)
print('||v|| =', norm_v)
print('||unit_v|| =', np.linalg.norm(unit_v))

# Cosine similarity works the same way
cos_sim = np.dot(v, w) / (np.linalg.norm(v) * np.linalg.norm(w))
print('cosine similarity:', cos_sim)
```

### Curse of Dimensionality

In high dimensions, all points appear roughly equidistant. In 2D, points cluster visibly, but in 100D, distance distributions flatten out. This is why direction often matters more than raw distance in high-dimensional problems — and one reason cosine similarity is preferred in embedding search.

```python
# Observe how average distance changes with dimension
for d in [2, 10, 50, 100]:
    samples = np.random.randn(100, d)
    distances = []
    for i in range(10):
        for j in range(i+1, 10):
            dist = np.linalg.norm(samples[i] - samples[j])
            distances.append(dist)
    print(f'{d}-dim: mean distance = {np.mean(distances):.2f}, std = {np.std(distances):.2f}')
```

As dimension increases, the ratio of mean to standard deviation converges. This phenomenon is the *curse of dimensionality* — a critical property to account for when working with high-dimensional data.

## Practical Connection: Embedding Comparison Routine

The reason we learn vectors is ultimately for comparison and search. When working with text or user embeddings, direction usually matters more than magnitude, so the pattern of normalizing first and computing dot products is standard.

```python
import numpy as np

emb = np.array([
    [0.2, 0.1, 0.7, 0.3],
    [0.1, 0.0, 0.8, 0.2],
    [0.9, 0.1, 0.0, 0.0],
], dtype=float)

emb_n = emb / np.linalg.norm(emb, axis=1, keepdims=True)
sim = emb_n @ emb_n.T
print(sim)
```

Diagonal elements are always close to 1; off-diagonal elements that are large indicate semantically similar vectors. The same principle scales to query-document dot products for basic vector search ranking.

## Five Common Mistakes

1. **Relying on *implicit broadcasting* despite *shape mismatch*.**
2. **Normalizing a *zero vector* — *division by zero*.**
3. **Sloppy distinction between *row vs column vectors*.**
4. **Confusing *dot product* and *element-wise product*.**
5. **Ignoring *floating-point error*.**

## How This Shows Up in Production

ML feature inputs, *embedding vectors*, *user/item vectors* in recommenders, and *word embeddings* in NLP — all of these are *vector operations*.

## How a Senior Engineer Thinks

- *Always print* the *shape*.
- *Always check* the *norm*.
- Know *when normalization is required*.
- *Visualize* the *geometric meaning*.
- Care about *numerical stability*.

## Checklist

- [ ] You can do *vector addition / scalar multiplication*.
- [ ] You can compute *norms*.
- [ ] You can *normalize*.
- [ ] You understand the *geometric meaning*.

## Practice Problems

1. Compute by hand the *Euclidean norm* of `v = [3, 4]`.
2. Verify in code that the *normalized vector* has norm *1*.
3. Explain why *normalizing the zero vector* is *undefined*.

## Wrap-up and Next Steps

A vector is a *point/arrow in space* and *one row of your data*. The next post covers *matrices*.

## Answering the Opening Questions

- **How is a vector different from a plain list?**
  - A vector is not a simple array—it is a geometric object with addition and scalar multiplication defined on it. This gives rise to vector space structure, letting you express problems of any dimension in the same language.
- **What do vector addition and scalar multiplication mean geometrically?**
  - Addition joins two arrows tip-to-tail; scalar multiplication adjusts a vector's length and direction. These two operations being closed is what makes a vector space.
- **Why does a norm carry meaning beyond just length?**
  - A norm quantifies a vector's magnitude. In normalization you keep only direction and standardize magnitude to 1, so direction-comparison problems use normalized vectors. For quantity data, the norm is information that must be preserved.
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- **Vectors (current)**
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

- [3Blue1Brown — Vectors](https://www.3blue1brown.com/lessons/vectors)
- [MIT OpenCourseWare — Vectors and spaces](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [NumPy — Array creation](https://numpy.org/doc/stable/user/basics.creation.html)
- [Khan Academy — Vectors and spaces](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces)

Tags: LinearAlgebra, Vectors, NumPy, DataScience, Beginner
