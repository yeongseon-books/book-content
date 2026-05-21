---
series: discrete-math-101
episode: 7
title: "Discrete Math 101 (7/10): Combinatorics"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Discrete Math
  - Combinatorics
  - Permutations
  - Probability
  - Pigeonhole
seo_description: Permutations, combinations, the binomial theorem, the pigeonhole principle, and inclusion-exclusion — the math of counting and probability.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (7/10): Combinatorics

This is post 7 in the Discrete Math 101 series.

> Discrete Math 101 series (7/10)

**Core question**: Why are hash collisions inevitable? How long does it take to brute-force every possible password?

> Combinatorics is the math of counting "how many cases are there?" Permutations, combinations, the binomial theorem, and the pigeonhole principle are the tools we use to size an algorithm's input space, a cipher's key space, or the probability of a hash collision. This article walks through the basic counting laws, the pigeonhole principle, and inclusion-exclusion, with code to verify each result.


![discrete math 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/07/07-01-big-picture.en.png)
*discrete math 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Combinatorics?
- Which signal should the example or diagram make visible for Combinatorics?
- What failure should be prevented first when Combinatorics reaches a real system?

## What You Will Learn

- The product rule and the sum rule
- The difference between permutations and combinations
- Binomial coefficients and Pascal's triangle
- The pigeonhole principle and inclusion-exclusion

## Why It Matters

Cipher key-space size, brute-force attack time, the birthday paradox — all combinatorics. To analyze how an algorithm behaves over every possible input, you need to know how big the input space is, and that calculation is combinatorics.

> Combinatorics is the tool for measuring the exact size of possibility.

> Two basic counting laws (product, sum) extend into permutations, combinations, the binomial theorem, the pigeonhole principle, and inclusion-exclusion.

```text
   basic laws
  ┌─────────────┐
  │ product rule │ — independent choices multiply
  │ sum rule     │ — exclusive choices add
  └──────┬───────┘
         ↓
  ┌──────┬──────────┐
  ↓      ↓          ↓
perm. P  comb. C   binomial thm
  │      │          │
  └──┬───┴──────────┘
     ↓
 pigeonhole / inclusion-exclusion
```

## Key Terms

| Term | Notation | Description |
| --- | --- | --- |
| Permutation | P(n, r) = n!/(n-r)! | Ordered selection of r from n |
| Combination | C(n, r) = n!/(r!(n-r)!) | Unordered selection of r from n |
| Binomial coefficient | (n choose r) | Same as C(n, r) |
| Pigeonhole principle | n+1 → n | At least one box holds two items |
| Inclusion-exclusion | |A∪B| = |A| + |B| - |A∩B| | Removes double counting |

## Before / After

**Before — brute force without counting:**

```python
# "Just try everything" — no idea how long it takes
import itertools
for password in itertools.product("abc", repeat=4):
    pass  # 81 cases — looks small, but...
```

**After — analyzing the space size:**

```python
# 4-char lowercase: 26⁴ = 456,976
# 8-char alphanumeric+symbols: 94⁸ ≈ 6.1 × 10¹⁵
charset = 26
length = 4
print(f"space size: {charset ** length:,}")
```

## Hands-On: Step by Step

### Step 1: Product rule and sum rule

```python
# Product rule: multiply when choices are independent
# Example: 5 shirts, 3 pants → 5 × 3 = 15 outfits

shirts = ["white", "black", "gray", "navy", "beige"]
pants = ["jeans", "chinos", "slacks"]

outfits = [(s, p) for s in shirts for p in pants]
print(f"outfits: {len(outfits)} = {len(shirts)} × {len(pants)}")

# Sum rule: add when choices are exclusive
# Example: lunch is either 4 Korean dishes or 3 Japanese → 4 + 3 = 7
korean = 4; japanese = 3
print(f"lunch options: {korean + japanese}")
```

### Step 2: Permutations and combinations

```python
from math import factorial

def permutation(n: int, r: int) -> int:
    """Ordered selection of r items from n."""
    return factorial(n) // factorial(n - r)

def combination(n: int, r: int) -> int:
    """Unordered selection of r items from n."""
    return factorial(n) // (factorial(r) * factorial(n - r))

# Line up 3 people from 5 (order matters)
print(f"P(5, 3) = {permutation(5, 3)}")
# Pick a 3-person committee from 5 (order does not matter)
print(f"C(5, 3) = {combination(5, 3)}")

# Built-in
from itertools import permutations, combinations
print(f"permutations: {len(list(permutations(range(5), 3)))}")
print(f"combinations: {len(list(combinations(range(5), 3)))}")
```

If order matters, use permutations; otherwise combinations. Passwords are permutations; poker hands are combinations.

### Step 3: Binomial theorem and Pascal's triangle

```python
# Binomial theorem: (x + y)ⁿ = Σ C(n, k) xⁿ⁻ᵏ yᵏ
# The coefficients are exactly the combinations.

def pascal_triangle(rows: int) -> list[list[int]]:
    triangle = [[1]]
    for i in range(1, rows):
        prev = triangle[-1]
        new_row = [1] + [prev[j] + prev[j + 1] for j in range(len(prev) - 1)] + [1]
        triangle.append(new_row)
    return triangle

for row in pascal_triangle(7):
    print(" ".join(str(x).rjust(3) for x in row).center(40))

# (x + y)⁴ expansion: coefficients 1, 4, 6, 4, 1
n = 4
print(f"(x+y)^{n} coefficients: {[combination(n, k) for k in range(n + 1)]}")
```

### Step 4: The pigeonhole principle

```python
# Pigeonhole: put n+1 items in n boxes → at least one box has 2
# Application: hash collisions are inevitable when input > output space

def will_collide(input_space: int, hash_space: int) -> bool:
    return input_space > hash_space

# A 32-bit hash has 4 × 10⁹ outputs.
# Hashing 10 billion IDs into 32 bits guarantees a collision.
print(f"10B → 32-bit collision? {will_collide(10 ** 10, 2 ** 32)}")

# Birthday paradox: with just 23 people, two share a birthday with prob ~50%.
def birthday_collision_prob(n: int, days: int = 365) -> float:
    no_collision = 1.0
    for i in range(n):
        no_collision *= (days - i) / days
    return 1 - no_collision

for n in [10, 23, 50, 100]:
    print(f"n={n}: collision probability = {birthday_collision_prob(n):.3f}")
```

The pigeonhole principle is simple but powerful. The fact that no lossless compression algorithm can shrink every possible input is a direct corollary.

### Step 5: Inclusion-exclusion

```python
# |A ∪ B| = |A| + |B| - |A ∩ B|
# |A ∪ B ∪ C| = |A| + |B| + |C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|

# Example: 100 students, 60 study English, 40 Japanese, 20 both
def union_two(a: int, b: int, ab: int) -> int:
    return a + b - ab

print(f"studying at least one: {union_two(60, 40, 20)} students")

# Multiples of 2 or 3 or 5 between 1 and 100
def multiples_count(limit: int, n: int) -> int:
    return limit // n

limit = 100
m2, m3, m5 = multiples_count(limit, 2), multiples_count(limit, 3), multiples_count(limit, 5)
m6, m10, m15 = multiples_count(limit, 6), multiples_count(limit, 10), multiples_count(limit, 15)
m30 = multiples_count(limit, 30)

answer = m2 + m3 + m5 - m6 - m10 - m15 + m30
print(f"multiples of 2, 3, or 5 in 1..100: {answer}")
```

Inclusion-exclusion is the right tool whenever you need to remove double counting precisely. Database query optimizers use it to estimate OR cardinality.

## Notable Points

- Combinatorics measures the exact size of an input space.
- Permutations care about order; combinations do not.
- The pigeonhole principle explains why collisions are unavoidable.
- Inclusion-exclusion is the standard tool for OR counts.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mixing permutations and combinations | Wrong count | Ask "does order matter?" |
| Mixing product and sum rules | Confusing independent vs exclusive | Ask "both at once, or one of?" |
| Ignoring repetition | Same element re-picked | With repetition, permutations are nʳ |
| Loose pigeonhole application | Applied without n+1 condition | Verify the precise condition |
| Sign errors in inclusion-exclusion | Even-size intersections flipped | Use the general signed formula |

## How This Is Used in Practice

- Designing password policies (computing key-space size)
- Hash collision probability analysis (birthday paradox)
- Sample-size calculation for A/B tests
- Cardinality estimation in database query optimizers
- Avoiding ID collisions in distributed systems (UUID, Snowflake)

## How a Senior Engineer Thinks

A senior engineer answers "is this design enough?" quantitatively. UUID v4 collision odds, the limits of a 32-bit hash, the strength of a password policy — all answered with combinatorics on the spot. They also reach for it when picking algorithms: "What is the worst-case number of inputs we have to handle?"

## Checklist

- [ ] Can you tell the product and sum rules apart?
- [ ] Can you safely choose between permutations and combinations?
- [ ] Can you explain hash-collision inevitability via the pigeonhole principle?
- [ ] Can you compute OR cardinality with inclusion-exclusion?
- [ ] Do you have intuition for the birthday paradox?

## Practice Problems

1. Compute the key-space size of an 8-character password (uppercase + lowercase + digits + 8 symbols), and estimate the average cracking time at 10⁹ guesses per second.

2. Use inclusion-exclusion to count multiples of 7 or 11 or 13 between 1 and 1000.

3. Estimate the UUID v4 collision probability via the birthday paradox. After generating one trillion UUIDs, what is the collision chance?

## Wrap-Up and Next Steps

Combinatorics is the math of measuring possibility. The product/sum rules, permutations and combinations, the binomial theorem, the pigeonhole principle, and inclusion-exclusion are the standard toolkit for security, hashing, and probability analysis.

The next article enters another major area of discrete math: graph theory.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Combinatorics?**
  - The article treats Combinatorics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Combinatorics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Combinatorics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Discrete Math 101 (1/10): What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): Propositions and Logic](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): Relations and Equivalence](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): Proof Techniques](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): Sequences and Recurrence](./06-sequences-and-recurrence.md)
- **Combinatorics (current)**
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)

<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 6](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Combinatorics](https://en.wikipedia.org/wiki/Combinatorics)
- [Wikipedia — Pigeonhole Principle](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Wikipedia — Birthday Problem](https://en.wikipedia.org/wiki/Birthday_problem)

Tags: Computer Science, Discrete Math, Combinatorics, Permutations, Probability, Pigeonhole
