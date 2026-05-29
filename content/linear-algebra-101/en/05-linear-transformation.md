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

- What does multiplying a vector by a matrix actually do to a space?
- How do rotation, scaling, reflection, and shear appear in matrix form?
- Why is transformation composition written as matrix multiplication?

## Questions This Post Answers

- What does it really mean to multiply a vector by a matrix?
- How do rotation, scaling, reflection, and shear appear in matrix form?
- Why is transformation composition written as matrix multiplication?
- Where does the line between linear and nonlinear transformations actually sit?

> A linear transformation redraws a space, but it does so while preserving the structure of addition and scalar multiplication. That constraint is what makes the geometry readable.

## Why It Matters

Every neural-network layer is a linear transformation plus a nonlinearity. Graphics pipelines, coordinate transforms, and many augmentation steps in vision use the same language.

Once this intuition clicks, a matrix stops being a static object. Some matrices rotate space, some stretch it, some flip orientation, and some slant an entire grid. At that point, linear algebra becomes a language for movement and structure rather than a page of arithmetic rules.

## Common Linear Transformations at a Glance

A linear transformation is a rule that reshapes vector space. Each transformation has a characteristic matrix shape and geometric effect. The table below summarizes the ones you encounter most in practice.

| Transformation | Matrix | Geometric Effect |
| --- | --- | --- |
| Rotation (θ radians) | `[[cosθ, -sinθ], [sinθ, cosθ]]` | Preserves angles and lengths, changes direction only |
| Reflection (x-axis) | `[[1, 0], [0, -1]]` | Flips y-coordinate sign, reverses orientation |
| Scaling | `[[s_x, 0], [0, s_y]]` | Independent per-axis stretch/shrink |
| Projection (onto x-axis) | `[[1, 0], [0, 0]]` | Removes y-component, reduces dimension |
| Shear (x-direction) | `[[1, k], [0, 1]]` | Parallelogram distortion, area preserved |

Rotation and reflection preserve length; shear preserves parallelism. Projection reduces dimension and has no inverse. In practice, these transformations are composed together to perform complex spatial manipulations.

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

Rotation changes direction while preserving structure — a canonical linear transformation where coordinates change but spatial order is maintained.

```python
import numpy as np
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
v = np.array([1.0, 0.0])
print("rotated:", R @ v)
```

### Step 2 — Scaling

A diagonal matrix stretches or shrinks each axis independently. You can read axis-specific scaling directly from the diagonal entries.

```python
S = np.diag([2.0, 0.5])
print("scaled:", S @ np.array([1.0, 1.0]))
```

### Step 3 — Reflection across x-axis

Reflection flips the sign along one axis. It is a clear example of orientation reversal.

```python
F = np.array([[1.0, 0.0], [0.0, -1.0]])
print("reflected:", F @ np.array([1.0, 1.0]))
```

### Step 4 — Shear

Shear tilts the grid. Think of a rectangle becoming a parallelogram.

```python
Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
print("sheared:", Sh @ np.array([1.0, 1.0]))
```

### Step 5 — Composition

Composition is the real power of linear transformations. You can package multiple geometric changes into a single matrix.

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
- Linear transformations preserve the structure of the space.

## Five Common Mistakes

1. **Mixing up *rotation sign* — clockwise vs counter-clockwise.**
2. **A *negative scale* secretly introduces a *reflection*.**
3. **Confusing *shear direction*.**
4. **Reversing the *composition order*.**
5. **Treating a *nonlinear transformation* as if it were *linear*.**

## How This Shows Up in Production

Graphics *model matrices*, *homographies* in computer vision, *data augmentation* (rotation/scaling), and neural network layers — all are *linear transformations*.

A senior engineer reads a matrix by asking what it does to space: does it rotate? Scale per-axis? Flip orientation? They are especially careful about composition order — whether in a graphics pipeline or stacked neural network layers, changing the order means a completely different transformation.

## How a Senior Engineer Thinks

- *Visualizes* transformations.
- Tracks *composition order*.
- Checks the *sign of the determinant* for orientation.
- Uses *eigenvectors* to find a transformation's *axes*.
- Knows that *nonlinear transformations* are a separate beast.

## Visualizing Transformations with Matplotlib

Visualizing the effect of linear transformations strengthens geometric intuition significantly. The code below applies various transformations to a unit square and compares the results.

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_transformation(T, title):
    """Apply matrix T to a unit square and plot the result."""
    # Unit square vertices
    square = np.array([[0, 1, 1, 0, 0],
                       [0, 0, 1, 1, 0]])

    # Apply transformation
    transformed = T @ square

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Original
    ax1.plot(square[0], square[1], 'b-o', linewidth=2, markersize=8)
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(0, color='k', linewidth=0.5)
    ax1.axvline(0, color='k', linewidth=0.5)
    ax1.set_title('Original')

    # Transformed
    ax2.plot(transformed[0], transformed[1], 'r-o', linewidth=2, markersize=8)
    ax2.plot(square[0], square[1], 'b--', alpha=0.3, linewidth=1)
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='k', linewidth=0.5)
    ax2.axvline(0, color='k', linewidth=0.5)
    ax2.set_title(title)

    plt.tight_layout()
    return fig

# 1. Rotation (45 degrees)
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
fig1 = plot_transformation(R, 'Rotation 45 degrees')

# 2. Scaling
S = np.array([[2.0, 0.0], [0.0, 0.5]])
fig2 = plot_transformation(S, 'Scaling (2x, 0.5y)')

# 3. Reflection (x-axis)
F = np.array([[1.0, 0.0], [0.0, -1.0]])
fig3 = plot_transformation(F, 'Reflection (x-axis)')

# 4. Shear
Sh = np.array([[1.0, 0.5], [0.0, 1.0]])
fig4 = plot_transformation(Sh, 'Shear (x-direction)')

# 5. Composite
M = Sh @ R @ S
fig5 = plot_transformation(M, 'Composite: Shear . Rotation . Scale')
```

This code visually demonstrates each transformation's effect on space. The composite transformation in particular shows how order significantly affects the result. In practice, such visualizations verify transformation correctness.

## Composition with Determinant Check

Applying multiple transformations to the same point set makes composition order tangible.

```python
import numpy as np

pts = np.array([
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.0, 1.0],
]).T

S = np.array([[2.0, 0.0], [0.0, 1.0]])
R = np.array([[0.0, -1.0], [1.0, 0.0]])
H = np.array([[1.0, 0.5], [0.0, 1.0]])

M = H @ R @ S
out = M @ pts

print('transform matrix M:\n', M)
print('transformed points:\n', out.T)
print('det(M) =', np.linalg.det(M))
```

`det(M)` tells you the area scaling factor and whether orientation flips. Changing the transformation order produces very different output points — in any pipeline, `R @ S` and `S @ R` must be strictly distinguished.

## Verifying the Linearity Condition in Code

A quick check to confirm whether an arbitrary transformation is truly linear:

```python
T = M
u = np.array([1.0, 2.0])
v = np.array([-1.0, 3.0])
a, b = 2.5, -0.7

lhs = T @ (a * u + b * v)
rhs = a * (T @ u) + b * (T @ v)
print(np.allclose(lhs, rhs))  # True
```

If `True`, addition and scalar multiplication are preserved. Nonlinear activations (ReLU, sigmoid) fail this condition — which is why neural networks are expressed as "linear transformation + nonlinearity" combinations.

## Applications Table

| Transformation | Key Matrix Feature | Real-World Application |
| --- | --- | --- |
| Rotation | Orthogonal matrix, det=1 | Pose correction, coordinate system conversion |
| Reflection | Axis sign flip, det<0 | Symmetry processing, image horizontal flip |
| Shear | Off-diagonal emphasis | Geometric correction, animation effects |
| Per-axis scaling | Diagonal entries | Feature re-weighting, pixel axis transform |

When you read transformations as "space manipulation" rather than formulas, linear algebra becomes a far more practical tool.

## Linear vs. Nonlinear Transformations

Understanding why linear transformations matter requires comparison with nonlinear ones. Linear transformations preserve addition and scalar multiplication; nonlinear ones do not.

### The Linearity Condition

A transformation `T` is linear if and only if for all vectors `u`, `v` and scalars `a`, `b`:

T(au + bv) = aT(u) + bT(v)

```python
import numpy as np

# Linear transformation example: rotation
theta = np.pi / 3
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])

u = np.array([1.0, 2.0])
v = np.array([3.0, 4.0])
a, b = 2.5, -1.3

# Linearity check
lhs = R @ (a * u + b * v)
rhs = a * (R @ u) + b * (R @ v)

print('T(au + bv):', lhs)
print('aT(u) + bT(v):', rhs)
print('Linearity satisfied:', np.allclose(lhs, rhs))
```

### Nonlinear Transformation Example

Nonlinear transformations fail this condition. Neural network activation functions (ReLU, sigmoid) are the classic examples.

```python
def relu(x):
    return np.maximum(0, x)

u = np.array([1.0, -1.0])
v = np.array([2.0, -2.0])
a, b = 0.5, 0.5

# ReLU is nonlinear
lhs = relu(a * u + b * v)
rhs = a * relu(u) + b * relu(v)

print('ReLU(au + bv):', lhs)
print('a ReLU(u) + b ReLU(v):', rhs)
print('Linearity satisfied:', np.allclose(lhs, rhs))  # False
```

### Neural Networks = Linear + Nonlinear

A single neural network layer combines a linear transformation (W @ x + b) with a nonlinear activation (sigma). Linear transformations alone cannot represent complex functions — nonlinearity is essential for expressiveness.

```python
# Single neural network layer simulation
W = np.random.randn(3, 4)
b = np.random.randn(3)
x = np.random.randn(4)

# Linear part
z = W @ x + b
print('linear output z:', z)

# Nonlinear activation
a = relu(z)
print('activated output a:', a)

# Linear part alone cannot represent complex decision boundaries
# Nonlinearity adds the required expressiveness
```

### Linear vs. Nonlinear Comparison

| Property | Linear Transformation | Nonlinear Transformation |
| --- | --- | --- |
| Preserves addition/scalar multiplication | Yes | No |
| Representable as matrix | Yes | No |
| Composition rule | Matrix multiplication | Function composition |
| Examples | Rotation, reflection, scaling | ReLU, sigmoid, squaring |
| Role in neural nets | Weight matrices | Activation functions |

Linear transformations are simple to analyze and compute but limited in expressiveness. Nonlinear transformations are complex but powerful. In practice, you combine both appropriately to solve problems. Understanding the limits of linearity makes it clear why ML models require nonlinear activations — and simultaneously why designing the linear part well is the starting point for efficient learning.

## Order Sensitivity: Verifying Composition

The fastest way to internalize non-commutativity is to apply the same matrices in different orders to the same points.

```python
import numpy as np

points = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
theta = np.deg2rad(30)
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.array([[2.0, 0.0], [0.0, 0.5]])

p1 = points @ (R @ S).T
p2 = points @ (S @ R).T
print('R@S result:\n', p1)
print('S@R result:\n', p2)
```

This computation connects directly to graphics pipelines and data preprocessing. In any system that applies coordinate transformations in multiple stages, order is meaning — and wrong order produces predictable bugs.

The same intuition applies in machine learning. Preprocessing that rotates or scales inputs along specific axes is a linear transformation; projecting onto principal component bases is the same operation structure. The habit of reading transformations as matrices is a powerful reference point for both model interpretation and debugging.

## Checklist

- [ ] You can build *rotation/scaling/reflection/shear* matrices.
- [ ] You can express *composition* as a *matrix product*.
- [ ] You understand the impact of *order*.
- [ ] You can read the *geometric meaning*.

## Practice Problems

1. Verify that applying a *45-degree rotation* twice equals a *90-degree rotation*.
2. Check whether *reflect-then-rotate* differs from *rotate-then-reflect*.
3. Describe the *effect* of scaling by `(-1, -1)`.

## Wrap-up and Next Steps

Linear transformations *reshape space*. The next post covers *basis and dimension*.

## Answering the Opening Questions

- **What does multiplying a vector by a matrix actually do to a space?**
  - Multiplying a matrix by a vector is not just computing a few coordinates — it reshapes points and the entire grid together. As the rotation example showed, multiplying R by `[1, 0]` yields roughly `[0.707, 0.707]`: direction changes while length is preserved. The visualization code confirmed this by showing how the unit square deforms under each transformation.
- **How do rotation, scaling, reflection, and shear appear in matrix form?**
  - Rotation is `[[cos, -sin], [sin, cos]]`, scaling is `np.diag([2.0, 0.5])`, reflection is `[[1,0],[0,-1]]`, shear is `[[1,k],[0,1]]`. As the summary table showed, diagonal entries reveal per-axis scale, sign flips reveal reflection, and off-diagonal entries reveal tilt. The determinant tells you area scaling and orientation.
- **Why is transformation composition written as matrix multiplication?**
  - In the composition examples, `M = R @ S` applied scaling first then rotation, bundled into a single matrix. The order-sensitivity demo confirmed that `R @ S` and `S @ R` produce different outputs. Writing composition as matrix products means multi-step transformations reduce to one `M @ v`, and the non-commutativity is preserved automatically.
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
