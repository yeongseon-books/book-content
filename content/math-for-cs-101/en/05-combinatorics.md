---
series: math-for-cs-101
episode: 5
title: "Math for CS 101 (5/10): Combinatorics"
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
  - Combinatorics
  - Counting
  - Probability
  - Beginner
seo_description: A beginner-friendly tour of product rule, sum rule, permutations, combinations, pigeonhole principle, and binomial coefficients
last_reviewed: '2026-05-04'
---

# Math for CS 101 (5/10): Combinatorics

If you want to explain why an algorithm suddenly becomes too slow, why test cases explode, or why collisions become unavoidable, you end up counting possibilities. The problem is that real systems produce too many cases to enumerate by hand.

Combinatorics is what lets you count without listing everything. Once you know whether order matters, whether repetition is allowed, and whether choices are independent or exclusive, the structure often tells you how to count.

This is the 5th post in the Math for CS 101 series.

Here we treat combinatorics as the language of counting behind complexity and probability, not as a bag of disconnected formulas.


![math for cs 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/05/05-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 5 flow overview*
> Combinatorial counting becomes essential the moment you face an exponential search space; it shifts you from guessing to systematic enumeration.

## Questions to Keep in Mind

- Why can we count accurately without enumerating every case?
- When should you use the product rule versus the sum rule?
- What is the practical difference between permutations and combinations?

## Why It Matters

Complexity analysis, probability, collision analysis, and test generation all depend on counting. If you underestimate the size of the possibility space, you can choose an algorithm that already fails before optimization begins.

The useful habit is to ask structural questions first: does order matter, is repetition allowed, and are the choices independent? Those questions matter more than memorizing a formula in isolation.

Combinatorics counts *possibilities* systematically: permutations (order matters), combinations (order does not), and recurrence relations (recursive structure).

## Before/After

**Before**: Try all possibilities and hope the search finishes.

**After**: Calculate the bounds and decide if brute force is even viable.

## Key Terms

- **product rule**: multiply *sequential* choices.
- **sum rule**: add *exclusive* choices.
- **permutation**: *ordered* arrangement.
- **combination**: *unordered* selection.
- **combination with repetition**: selection where the same item can be chosen multiple times — `C(n+r-1, r)`.
- **pigeonhole**: *n+1* items in *n* boxes force a *collision*.
- **inclusion-exclusion**: subtract overlaps when counting unions.

## Permutation / Combination / Repetition Comparison

| Type | Question | Formula |
|---|---|---|
| Permutation `nPr` | Does order matter? | `n! / (n-r)!` |
| Combination `nCr` | Order ignored, just pick? | `n! / (r!(n-r)!)` |
| Combination with repetition | Same item can be picked multiple times? | `C(n+r-1, r)` |

Being able to recall this table quickly prevents most modeling errors.

## Hands-on: Mini Counting Kit

### Step 1 — Product Rule and Sum Rule in Code

The first step in any counting problem is decomposing the selection structure into products or sums. Independent sequential choices → product rule. Mutually exclusive choices → sum rule.

```python
def multiplication_rule(*counts: int) -> int:
    out = 1
    for c in counts:
        out *= c
    return out

def addition_rule(*counts: int) -> int:
    return sum(counts)
```

Example: a password of length 4 drawn from 26 lowercase letters and 10 digits, each position independent → `26 * 10 * 26 * 10` (product rule). Login failure being either "wrong password" or "account locked" (mutually exclusive categories) → sum rule.

### Step 2 — Factorial

```python
def fact(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r
```

Factorial is the most reused building block in combinatorics. Both permutation and combination formulas depend on it. Simple as it looks, it compresses the idea of shrinking choices into a single product.

### Step 3 — Permutations

```python
def nPr(n, r):
    return fact(n) // fact(n - r)
```

Permutations count arrangements where order matters. Password digit placement, task execution order, presentation sequence — whenever the arrangement itself carries meaning, you reach for this formula.

### Step 4 — Combinations

```python
def nCr(n, r):
    return fact(n) // (fact(r) * fact(n - r))
```

Combinations count selections where only membership matters, not order. Team composition, sample selection, feature subset choice — the quickest way to distinguish from permutations is to ask: does swapping two items produce a different case?

### Step 5 — Pigeonhole Check

```python
def pigeon(items, holes):
    return items > holes
```

The pigeonhole principle says if you have more items than containers, at least one container must hold multiple items. This single inequality powers surprisingly many impossibility and collision arguments.

### Step 6 — Binomial Row

```python
def row(n):
    return [nCr(n, k) for k in range(n + 1)]
```

Pascal's triangle row gives all binomial coefficients for a given n. It reveals symmetry (nCr = nC(n-r)) and provides a quick way to verify your combination calculations.

## Verifying with itertools

Rather than trusting formulas alone, cross-check with enumeration on small inputs:

```python
import itertools
import math

items = ['A', 'B', 'C', 'D']
perms = list(itertools.permutations(items, 2))
combs = list(itertools.combinations(items, 2))

assert len(perms) == math.perm(4, 2)
assert len(combs) == math.comb(4, 2)
```

This pattern doubles as test code. If you write a complex counting function, verifying it against enumeration for small n builds confidence.

## Pigeonhole Principle for Collision Analysis

If you have 100 hash buckets and 101 keys, a collision is guaranteed. This is a deterministic fact, not a probability estimate. In design reviews, use the pigeonhole principle to decide "is collision avoidable?" before discussing "how likely is collision?"

```python
def must_collide(num_keys: int, num_buckets: int) -> bool:
    return num_keys > num_buckets
```

Once collision is inevitable, the concern shifts from collision avoidance to collision handling strategy — rehash policies, chaining length caps, resizing thresholds.

## Binomial Coefficients and Probability

Flipping a coin n times, the number of ways to get exactly k heads is `C(n, k)`. This coefficient is the core term of the binomial distribution that appears in the probability chapter. Skip combinatorics, and you end up memorizing probability formulas without understanding where they come from.

## Birthday Problem

The most famous intuition-breaker in combinatorics. The probability that at least two people in a group of n share a birthday grows faster than most people expect:

```python
def birthday_collision_prob(n: int, days: int = 365) -> float:
    """
    Probability that at least one pair shares a birthday among n people.
    P(collision) = 1 - P(all different)
    """
    if n > days:
        return 1.0
    no_collision = 1.0
    for i in range(n):
        no_collision *= (days - i) / days
    return 1 - no_collision

# With 23 people, collision probability exceeds 50%
for n in [10, 23, 50, 70]:
    print(f"n={n:3d}: {birthday_collision_prob(n):.4f}")
# n= 10: 0.1169
# n= 23: 0.5073
# n= 50: 0.9704
# n= 70: 0.9992
```

This directly applies to hash collisions, UUID duplicates, and random ID assignment. Predicting collision probability for 128-bit UUIDs uses the same logic — the domain just becomes 2^128 instead of 365.

## Stars and Bars: Distributing Identical Items

The number of ways to distribute n identical items into k distinct bins is `C(n+k-1, k-1)`. This formula appears in resource allocation, load balancing, and partition problems:

```python
import math

def distribute(items: int, bins: int) -> int:
    """Number of ways to distribute items into bins (empty bins allowed)."""
    return math.comb(items + bins - 1, bins - 1)

# 10 requests distributed across 3 servers
print(distribute(10, 3))  # 66

# 5 credits allocated to 4 projects
print(distribute(5, 4))   # 56
```

Understanding how a load balancer distributes requests across backend servers lets you quantitatively explain why certain distribution strategies produce bias.

## Inclusion-Exclusion Principle

Counting the union of overlapping sets via simple addition double-counts the intersections. Inclusion-exclusion removes that overlap systematically:

```python
def inclusion_exclusion(a, b, inter):
    return a + b - inter

print(inclusion_exclusion(120, 90, 30))
```

For three or more sets, you alternate adding and subtracting intersection terms:

```python
def inclusion_exclusion_3(a: int, b: int, c: int,
                          ab: int, ac: int, bc: int,
                          abc: int) -> int:
    """Union size for three sets."""
    return a + b + c - ab - ac - bc + abc

# 1000 people: Python users 400, Java 300, Go 200
# Python&Java 100, Python&Go 50, Java&Go 30, all three 10
print(inclusion_exclusion_3(400, 300, 200, 100, 50, 30, 10))  # 730
```

This appears in access control, rule engines, and monitoring alarm aggregation — anywhere you need "events not matching any rule."

## Catalan Numbers

Catalan numbers count "valid parenthesizations," "distinct BST structures," and "non-crossing connections":

```python
def catalan(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = sum(dp[j] * dp[i-1-j] for j in range(i))
    return dp[n]

for i in range(6):
    print(i, catalan(i))
```

If you can map a problem to a Catalan structure, you replace exponential brute-force with a closed-form calculation or DP — a significant cost reduction.

## Detecting Combinatorial Explosion Early

Before starting a brute-force search, estimate the search space roughly:

```python
import math

def search_space_bits(count: int) -> float:
    return math.log2(count)
```

Once the possibility count exceeds `2^40`, exhaustive search on a single machine is effectively impossible. At that point, switch immediately to branch-and-bound, dynamic programming, approximation, or random sampling. Combinatorics is both a tool for computing exact answers and a tool for quickly declaring "this approach will not work."

## Password and Token Strength

Password/token strength is ultimately a counting problem. An attacker's brute-force probability maps directly to combinatorics:

| Token Composition | Possibility Count | Brute-Force Time (1M/sec) |
|---|---|---|
| 4-digit numeric | 10^4 = 10,000 | 0.01 seconds |
| 8-char lowercase | 26^8 ≈ 2×10^11 | ~58 hours |
| 12-char mixed (upper+lower+digit+special) | 94^12 ≈ 5×10^23 | Exceeds age of universe |

Increasing character variety helps, but increasing length makes the count explode faster. This is the product rule in action. In security audits, "is the token entropy sufficient?" relies on exactly this calculation. Without combinatorics, you fall back on the vague intuition "longer is safer" with no quantitative backing.

## Multinomial Permutations

When items repeat, the number of distinct arrangements requires dividing by the factorial of each group size:

```python
import math

def multinomial_permutation(total: int, *groups: int) -> int:
    denom = 1
    for g in groups:
        denom *= math.factorial(g)
    return math.factorial(total) // denom

# MISSISSIPPI: 11 letters, M=1, I=4, S=4, P=2
print(multinomial_permutation(11, 1, 4, 4, 2))  # 34650
```

## Practice Problem Set

| Problem | Hint | Answer |
|---|---|---|
| Select 3 from 8 people (order irrelevant) | Combination C(8,3) | 56 |
| 4-digit password (0-9, repetition allowed) | Product rule 10^4 | 10,000 |
| 5 coin flips, exactly 3 heads | C(5,3) × (1/2)^5 | 5/16 |
| Choose 3 floors from 10-story building (order matters) | Permutation P(10,3) | 720 |
| Arrangements of MISSISSIPPI | Multinomial 11!/(4!4!2!) | 34,650 |

The most important first step in any combinatorics problem: "Does order matter?" If yes → permutation. If no → combination. Next: "Is repetition allowed?" These two questions route most problems to the correct formula.

## What to Notice in This Code

- *Factorial* is the reusable building block.
- *nCr* is *symmetric*: (n,r) = (n,n-r).
- *Pigeonhole* is one inequality.
- Product rule vs sum rule is the structural decision that precedes all formulas.

## Five Common Mistakes

1. **Confusing *permutations* and *combinations*.**
2. **Forgetting whether *repetition* is allowed.**
3. **Forgetting *0! = 1*.**
4. **Calling *factorial* directly on *huge n*.**
5. **Using *=* instead of *>* in pigeonhole.**

## How This Shows Up in Production

*A/B test bucketing*, *hash collision analysis*, *dataset sampling*, and *combinatorial explosion* checks all use these tools.

## How a Senior Engineer Thinks

- *Counting* is *modeling*.
- *Principles* over *formulas*.
- *Pigeonhole* proves *existence*.
- *Binomial* connects to *probability*.
- Watch for *combinatorial explosion*.

## Checklist

- [ ] Decide if *order matters*.
- [ ] Decide if *repetition* is allowed.
- [ ] Replace enumeration with a *formula*.
- [ ] Inspect *edge cases* (0!, empty set).
- [ ] Verify with `itertools` on small inputs.
- [ ] Estimate search space before brute-forcing.

## Practice Problems

1. State the difference between *nPr* and *nCr* in one line.
2. State *pigeonhole* in one line.
3. Why is *0! = 1*?

## Wrap-up and Next Steps

Combinatorics teaches you to read possibility spaces structurally instead of by brute force. That shift is what makes complexity analysis and probability feel connected instead of separate topics.

Next, we continue into probability, where counting becomes a way to reason about uncertainty instead of certainty alone.

## Answering the Opening Questions

- **How can you count exactly without listing every case?**
  - Combinatorics decomposes selection structure instead of enumerating results. `multiplication_rule`, `addition_rule`, `npr`, `ncr` separate independent choices, exclusive choices, and order significance. For small inputs, `itertools.permutations` and `itertools.combinations` verify that formulas match enumeration.
- **When do you use the multiplication rule versus the addition rule?**
  - When consecutive independent choices accumulate (like password positions), use multiplication. When categories are mutually exclusive (like login failure being either wrong password or locked account), use addition. Getting this distinction right first keeps the counting model from wobbling.
- **What's the difference between permutations and combinations?**
  - Permutations `nPr(n, r)` count different orderings as different cases; combinations `nCr(n, r)` count only the chosen set. For team selection, feature picking, the birthday problem, and token-strength calculation, deciding whether to treat the scenario as an arrangement or a selection must come before choosing the formula.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- **Combinatorics (current)**
- Probability (upcoming)
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Combinatorics - Wolfram MathWorld](https://mathworld.wolfram.com/Combinatorics.html)
- [Counting - Khan Academy](https://www.khanacademy.org/math/statistics-probability/counting-permutations-and-combinations)
- [Concrete Mathematics - Graham, Knuth, Patashnik](https://www-cs-faculty.stanford.edu/~knuth/gkp.html)
- [Python math.comb Documentation](https://docs.python.org/3/library/math.html#math.comb)
- [SymPy GitHub repository](https://github.com/sympy/sympy)

Tags: Math, Combinatorics, Counting, Probability, Beginner
