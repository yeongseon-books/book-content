---
series: linear-algebra-101
episode: 5
title: "Linear Algebra 101 (5/10): Linear Transformations"
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
  - LinearTransformation
  - Geometry
  - DataScience
  - Beginner
seo_description: A beginner-friendly intro to linear transformations — rotation, scaling, reflection, and shear with their matrix forms and NumPy code
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (5/10): Linear Transformations

After learning matrices, the natural follow-up is simple: what do those matrices actually do to a space? Linear transformation is the idea that answers that question. A matrix is the coordinate form of a transformation rule.

This is the 5th post in the Linear Algebra 101 series. Here we will read linear transformations geometrically through rotation, scaling, reflection, and shear.


![linear algebra 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/05/05-01-concept-at-a-glance.en.png)
*linear algebra 101 chapter 5 flow overview*
> A linear transformation is a rule that maps vectors to vectors while preserving addition and scalar multiplication. When you read matrix multiplication as composition of transformations, it becomes clear why order matters.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Linear Transformations?
- Which signal should the example or diagram make visible for Linear Transformations?
- What failure should be prevented first when Linear Transformations reaches a real system?

## Questions This Post Answers

- What does it really mean to multiply a vector by a matrix?
- How do rotation, scaling, reflection, and shear appear in matrix form?
- Why is transformation composition written as matrix multiplication?
- Where does the line between linear and nonlinear transformations actually sit?

> A linear transformation redraws a space, but it does so while preserving the structure of addition and scalar multiplication. That constraint is what makes the geometry readable.

## Why It Matters

Every neural-network layer is a linear transformation plus a nonlinearity. Graphics pipelines, coordinate transforms, and many augmentation steps in vision use the same language.

Once this intuition clicks, a matrix stops being a static object. Some matrices rotate space, some stretch it, some flip orientation, and some slant an entire grid. At that point, linear algebra becomes a language for movement and structure rather than a page of arithmetic rules.

## Key Terms

- **Linear transformation**: `T(av + bw) = a T(v) + b T(w)` — preserves *addition and scalar multiplication*.
- **Rotation matrix**: rotates by angle `theta`.
- **Scaling**: a *diagonal matrix* that *stretches/shrinks*.
- **Reflection**: *symmetry* across an axis.
- **Shear**: *slants* the space along a direction.

## Before/After

**Before**: *"A matrix is just a transformation."* — no idea what shape.

**After**: *"Rotation = *angles*; scaling = *diagonal*; reflection = *sign flip*; shear = *off-diagonal*."*

## Hands-on: Five Steps

### Step 1 — Rotation

```python
import numpy as np
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
v = np.array([1.0, 0.0])
print("rotated:", R @ v)
```

### Step 2 — Scaling

```python
S = np.diag([2.0, 0.5])
print("scaled:", S @ np.array([1.0, 1.0]))
```

### Step 3 — Reflection across x-axis

```python
F = np.array([[1.0, 0.0], [0.0, -1.0]])
print("reflected:", F @ np.array([1.0, 1.0]))
```

### Step 4 — Shear

```python
Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
print("sheared:", Sh @ np.array([1.0, 1.0]))
```

### Step 5 — Composition

```python
M = R @ S
print("compose RS:", M @ np.array([1.0, 0.0]))
```

## Read One Numeric Pass

- A 45-degree rotation maps `[1, 0]` to roughly `[0.707, 0.707]`, so the axis literally turns.
- `diag(2, 0.5)` sends `[1, 1]` to `[2., 0.5]`, which makes axis-by-axis scaling concrete.
- Building `R @ S` first means you can package multiple geometric changes into one matrix.

## What to Notice in This Code

- *Matrix multiplication* is *composition* of transformations.
- *Each transformation* has its own *matrix shape*.
- *Order* changes the result.

## Five Common Mistakes

1. **Mixing up *rotation sign* — clockwise vs counter-clockwise.**
2. **A *negative scale* secretly introduces a *reflection*.**
3. **Confusing *shear direction*.**
4. **Reversing the *composition order*.**
5. **Treating a *nonlinear transformation* as if it were *linear*.**

## How This Shows Up in Production

Graphics *model matrices*, *homographies* in computer vision, *data augmentation* (rotation/scaling), and neural network layers — all are *linear transformations*.

## How a Senior Engineer Thinks

- *Visualizes* transformations.
- Tracks *composition order*.
- Checks the *sign of the determinant* for orientation.
- Uses *eigenvectors* to find a transformation's *axes*.
- Knows that *nonlinear transformations* are a separate beast.

## Checklist

- [ ] You can build *rotation/scaling/reflection/shear* matrices.
- [ ] You can express *composition* as a *matrix product*.
- [ ] You understand the impact of *order*.
- [ ] You can read the *geometric meaning*.

## Practice Problems

1. Verify that applying a *45° rotation* twice equals a *90° rotation*.
2. Check whether *reflect-then-rotate* differs from *rotate-then-reflect*.
3. Describe the *effect* of scaling by `(-1, -1)`.

## Wrap-up and Next Steps

Linear transformations *reshape space*. The next post covers *basis and dimension*.

## Answering the Opening Questions

- **What does multiplying by a matrix actually do to a space?**
  - Multiplying a matrix by a vector is not just computing a few coordinates—it reshapes points and the entire grid together. For example, multiplying rotation matrix `R` by `[1, 0]` yields roughly `[0.707, 0.707]`: direction changes while length is preserved.
- **How do rotation, scaling, reflection, and shear show up in matrix form?**
  - Rotation is `[[cosθ, -sinθ], [sinθ, cosθ]]`, scaling is `np.diag([2.0, 0.5])`, reflection is `[[1,0],[0,-1]]`, shear is `[[1,1],[0,1]]`. Diagonal entries reveal per-axis scale, sign flips reveal reflection, and off-diagonal entries reveal tilt.
- **Why is composition of transformations expressed as matrix multiplication?**
  - In the article, `M = R @ S` applied scaling first then rotation, bundled into a single matrix. Writing composition as matrix products means even multi-step transformations reduce to one `M @ v`, and the fact that changing the order changes the result is preserved automatically.
<!-- toc:begin -->
## In this series

- [Linear Algebra 101 (1/10): What Is Linear Algebra?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): Vectors](./02-vectors.md)
- [Linear Algebra 101 (3/10): Matrices](./03-matrices.md)
- [Linear Algebra 101 (4/10): Inner Product and Distance](./04-inner-product-and-distance.md)
- **Linear Transformations (current)**
- Basis and Dimension (upcoming)
- Eigenvalues and Eigenvectors (upcoming)
- Matrix Decomposition (upcoming)
- PCA (upcoming)
- Linear Algebra in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [3Blue1Brown — Linear transformations](https://www.3blue1brown.com/lessons/linear-transformations)
- [MIT OpenCourseWare — Linear transformations and their matrices](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/video-lectures/)
- [Khan Academy — Matrix transformations](https://www.khanacademy.org/math/linear-algebra/matrix-transformations)
- [NumPy — Mathematical functions](https://numpy.org/doc/stable/reference/routines.math.html)

Tags: LinearAlgebra, LinearTransformation, Geometry, DataScience, Beginner
