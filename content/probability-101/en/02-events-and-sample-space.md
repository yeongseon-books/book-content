---
series: probability-101
episode: 2
title: "Probability 101 (2/10): Events and Sample Space"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Probability
  - SampleSpace
  - Events
  - SetTheory
  - Beginner
seo_description: Learn how sample spaces and events turn probability questions into set problems, with unions, intersections, complements, and code examples.
last_reviewed: '2026-05-15'
---

# Probability 101 (2/10): Events and Sample Space

People often miss probability questions not because the arithmetic is hard, but because they start from a vague picture of the problem. If you jump straight to the calculation without writing down all possible outcomes, two people can read the same sentence and quietly solve two different problems.

In probability, the sample space and the event are closer to grammar than to decoration. If that grammar is shaky, the final number can look clean while meaning something else entirely.

This is the 2nd post in the Probability 101 series. Here we define sample spaces and events in set language, then use unions, intersections, complements, and independence to show why a careful setup often does half the work for you.


![probability 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/02/02-01-concept-at-a-glance.en.png)
*probability 101 chapter 2 flow overview*
> The sample space defines the universe of discourse. Every probability statement is relative to that universe.

## Questions to Keep in Mind

- Why must the sample space come before any probability calculation?
- What becomes easier when you express events as sets?
- What do union, intersection, and complement mean in practice?

## Why It Matters

Many wrong answers in probability come from the wrong sample space. If you treat (1,6) and (6,1) as the same outcome in one step and different outcomes in the next, everything after that can be numerically tidy and conceptually wrong.

Once the sample space is explicit, many probability problems turn into set problems. Events become subsets. "A or B" becomes a union. "A and B" becomes an intersection. That shift makes the structure of the problem much more stable.

## Set Operations and Probability

Viewing events as sets converts probability problems into set-arithmetic problems. The correspondence between set operations and probability formulas gives a systematic way to approach even complex questions.

| Operation | Symbol | Probability formula | Example |
| --- | --- | --- | --- |
| Union | A ∪ B | P(A ∪ B) = P(A) + P(B) − P(A ∩ B) | Sum is even OR ≥ 3 |
| Intersection | A ∩ B | P(A ∩ B) = P(A) × P(B) (if independent) | Sum is even AND doubles |
| Complement | Aᶜ | P(Aᶜ) = 1 − P(A) | Sum is NOT even |

The union formula subtracts the intersection to avoid double-counting — the inclusion-exclusion principle. The intersection formula only simplifies to a product when A and B are independent; otherwise you must use conditional probability: `P(A ∩ B) = P(A | B) × P(B)`. The complement is the simplest but most useful formula: it turns hard problems into easier ones by computing "not the event."

## Python Set Operations Example

Representing sample spaces and events as Python sets lets you verify formulas directly.

```python
# Two dice sample space
omega = {(i, j) for i in range(1, 7) for j in range(1, 7)}

# Event definitions
A = {o for o in omega if (o[0] + o[1]) % 2 == 0}  # even sum
B = {o for o in omega if o[0] == o[1]}             # doubles
C = {o for o in omega if o[0] + o[1] >= 10}       # sum >= 10

# Union
union_AB = A | B
print(f"P(A or B) = {len(union_AB) / len(omega):.3f}")

# Intersection
inter_AB = A & B
print(f"P(A and B) = {len(inter_AB) / len(omega):.3f}")

# Complement
not_A = omega - A
print(f"P(not A) = {len(not_A) / len(omega):.3f}")
print(f"P(A) + P(not A) = {len(A)/len(omega) + len(not_A)/len(omega):.1f}")

# Inclusion-exclusion verification
P_A = len(A) / len(omega)
P_B = len(B) / len(omega)
P_AB = len(inter_AB) / len(omega)
P_union = len(union_AB) / len(omega)
print(f"P(A) + P(B) - P(A∩B) = {P_A + P_B - P_AB:.3f}")
print(f"P(A∪B) = {P_union:.3f}")
```

This code shows how set operations correspond to probability formulas. The inclusion-exclusion check verifies numerically why the subtraction is necessary.

## Inclusion-Exclusion via Venn Diagrams

The inclusion-exclusion principle corrects for overlap when computing the size of a union. Think of it through a Venn diagram:

- A only: the part of A that does not overlap with B
- B only: the part of B that does not overlap with A
- Both A and B: the intersection region

The union size is the sum of these three parts. But `P(A) + P(B)` counts the intersection twice, so you subtract it once:

```
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
```

For three events, the formula extends:

```
P(A ∪ B ∪ C) = P(A) + P(B) + P(C)
                 - P(A ∩ B) - P(A ∩ C) - P(B ∩ C)
                 + P(A ∩ B ∩ C)
```

The alternating pattern — add, subtract, add — repeats. This principle appears not only in probability but in combinatorics, logic circuits, and database cardinality estimation.

In practice, you use inclusion-exclusion whenever multiple conditions overlap and you need to count correctly. For example, counting "users of feature A OR feature B" requires subtracting users who use both, to avoid double-counting.

## Key Terms

- **Sample space Ω**: the set of all possible outcomes.
- **Event A**: a subset of Ω.
- **Union A∪B**: A or B occurs.
- **Intersection A∩B**: A and B occur together.
- **Complement Aᶜ**: A does not occur.
- **Mutually exclusive**: A∩B = ∅.
- **Independent**: P(A∩B) = P(A)·P(B).

Mutually exclusive and independent are especially easy to confuse. "Cannot happen together" and "does not influence each other" are entirely different claims. Separating these two early saves considerable confusion later.

## Turning Problems into Sets

"What is the probability that the sum of two dice is even?" can feel daunting. But define Ω = {(i,j) : 1≤i,j≤6}, define event A = "sum is even," and it becomes a counting problem. Total outcomes: 36. Even-sum outcomes: 18. Probability: 18/36 = 1/2.

The representation matters more than the computation technique. The moment you write the problem as a set, what counts as "everything" and what counts as "the event" become unambiguous.

## Hands-on: 5-step Events

### Step 1 — Build the sample space

```python
omega = [(i, j) for i in range(1, 7) for j in range(1, 7)]
print(len(omega))  # 36
```

Two dice thrown with order distinguished gives 36 outcomes. Already at this step, the assumption that order matters is baked in. Probability calculation starts with surfacing assumptions.

### Step 2 — Define events

```python
A = [o for o in omega if (o[0] + o[1]) % 2 == 0]   # even sum
B = [o for o in omega if o[0] == o[1]]              # doubles
```

Events should not stay as words — write them as sets. That way union, intersection, and complement become code you can run.

### Step 3 — Union and intersection

```python
union = list(set(A) | set(B))
inter = list(set(A) & set(B))
print(len(union), len(inter))
```

"A or B" is a union; "A and B" is an intersection. Familiar when spoken, but far more precise when expressed as set operations.

### Step 4 — Complement

```python
not_A = [o for o in omega if o not in A]
print(len(A) + len(not_A))  # 36
```

The complement is everything in Ω that is not in the event. The event size plus the complement size must always equal the total. A basic sanity check that catches mistakes.

### Step 5 — Check independence

```python
def P(E): return len(E) / len(omega)
print("indep?", round(P(set(A) & set(B)) - P(A) * P(B), 6))
```

To check independence, compare P(A∩B) to P(A)·P(B). "Not overlapping" does not imply "independent." This distinction breaks most often at the introductory level.

## Combinatorics and Probability

Counting the size of the sample space is often a combinatorics problem. Whether order matters and whether replacement is allowed changes the count.

**Permutation**: Order-aware selection

- Choose r from n with order: `P(n, r) = n! / (n-r)!`
- Example: Elect president and VP from 5 people = P(5, 2) = 20

**Combination**: Order-ignored selection

- Choose r from n: `C(n, r) = n! / (r!(n-r)!)`
- Example: Select 2 from 5 people = C(5, 2) = 10

**With vs without replacement**

- With replacement: same item can be drawn multiple times
- Without replacement: once drawn, cannot appear again

```python
from math import factorial, comb, perm

# Permutation
print(f"P(5, 2) = {perm(5, 2)}")

# Combination
print(f"C(5, 2) = {comb(5, 2)}")

# Ratio
print(f"Permutation/Combination = {perm(5, 2) / comb(5, 2):.0f}")
```

Practical examples:

- 4-digit PIN (order yes, replacement yes): `10^4 = 10,000`
- Lottery 6 numbers (order no, replacement no): `C(45, 6) = 8,145,060`
- Choose 3 followers (order no, replacement no): `C(100, 3)`

Getting combinatorics wrong means the sample space size (the denominator) is wrong, which makes every probability calculation wrong.

## Defining Sample Spaces for Real Problems

How you define the sample space is the first step. The same problem yields different answers under different sample space choices.

**Example 1: Flipping two coins**

```python
# Method 1: Distinguish order
omega1 = [("H", "H"), ("H", "T"), ("T", "H"), ("T", "T")]
# 4 outcomes, each with probability 1/4

# Method 2: Ignore order, record only head count
omega2 = [0, 1, 2]  # 0, 1, 2 heads
# 3 outcomes, but probabilities are 1/4, 1/2, 1/4 (NOT uniform)

print(f"Method 1: |Ω| = {len(omega1)}")
print(f"Method 2: |Ω| = {len(omega2)} (non-uniform probabilities)")
```

Method 1 allows uniform probability assignment. Method 2 requires non-uniform weights — assigning 1/3 to each would be wrong.

**Example 2: Card draw**

```python
# One card from a 52-card deck
suits = ["spades", "hearts", "diamonds", "clubs"]
ranks = list(range(1, 14))  # 1(A) through 13(K)
omega = [(suit, rank) for suit in suits for rank in ranks]

print(f"|Ω| = {len(omega)}")  # 52

# Event: ace of spades
event = [("spades", 1)]
print(f"P(ace of spades) = {len(event) / len(omega)}")
```

In practice, teams that explicitly document their sample space — A/B test bucket definitions, event log schemas, metric computation formulas — reduce miscommunication significantly.

## De Morgan's Laws

De Morgan's laws relate complements to unions and intersections:

```
(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
```

In probability terms:

```
P(not (A or B)) = P(not A and not B)
P(not (A and B)) = P(not A or not B)
```

**Python verification**

```python
omega = [(i, j) for i in range(1, 7) for j in range(1, 7)]
A = {o for o in omega if o[0] + o[1] >= 10}
B = {o for o in omega if o[0] == o[1]}

# De Morgan's first law
not_A_or_B = set(omega) - (set(A) | set(B))
not_A_and_not_B = (set(omega) - set(A)) & (set(omega) - set(B))

print(f"|(A∪B)ᶜ| = {len(not_A_or_B)}")
print(f"|Aᶜ∩Bᶜ| = {len(not_A_and_not_B)}")
print(f"De Morgan 1: {not_A_or_B == not_A_and_not_B}")

# De Morgan's second law
not_A_and_B = set(omega) - (set(A) & set(B))
not_A_or_not_B = (set(omega) - set(A)) | (set(omega) - set(B))

print(f"|(A∩B)ᶜ| = {len(not_A_and_B)}")
print(f"|Aᶜ∪Bᶜ| = {len(not_A_or_not_B)}")
print(f"De Morgan 2: {not_A_and_B == not_A_or_not_B}")
```

De Morgan's laws are used in logic circuit design, database query optimization, and filtering with negated conditions. They let you transform complex conditions into simpler equivalent forms.

## Mutually Exclusive vs Independent

The most common confusion at the introductory level: mutually exclusive and independent are different concepts with different meanings.

| Property | Mutually exclusive | Independent |
| --- | --- | --- |
| Definition | A∩B = ∅ | P(A∩B) = P(A)·P(B) |
| Meaning | Cannot happen together | One does not influence the other |
| P(A∩B) | 0 | P(A)·P(B) |
| Relationship | If A occurs, B is impossible | If A occurs, B's probability unchanged |

```python
# Verifying the difference
omega = set(range(1, 7))  # single die

# Mutually exclusive: A={1,2,3}, B={4,5,6}
A_excl = {1, 2, 3}
B_excl = {4, 5, 6}
print(f"Mutually exclusive: A∩B = {A_excl & B_excl}")  # empty
print(f"P(A)·P(B) = {len(A_excl)/6 * len(B_excl)/6:.3f}")
print(f"P(A∩B) = {len(A_excl & B_excl)/6:.3f}")
print(f"Independent? {len(A_excl & B_excl)/6 == len(A_excl)/6 * len(B_excl)/6}")  # False

print()
# Independent: A={even}, B={>= 3}
A_ind = {2, 4, 6}
B_ind = {3, 4, 5, 6}
P_A = len(A_ind) / 6
P_B = len(B_ind) / 6
P_AB = len(A_ind & B_ind) / 6
print(f"Independent: P(A)={P_A:.3f}, P(B)={P_B:.3f}")
print(f"P(A)·P(B) = {P_A * P_B:.3f}")
print(f"P(A∩B) = {P_AB:.3f}")
print(f"Independent? {abs(P_AB - P_A * P_B) < 1e-10}")  # True
```

Output:

```
Mutually exclusive: A∩B = set()
P(A)·P(B) = 0.250
P(A∩B) = 0.000
Independent? False

Independent: P(A)=0.500, P(B)=0.667
P(A)·P(B) = 0.333
P(A∩B) = 0.333
Independent? True
```

Mutually exclusive events are strongly dependent — if one happens, the other is impossible. Therefore mutual exclusivity and independence cannot coexist (when both events have positive probability). Nailing this distinction early makes conditional probability and Bayes' theorem far smoother.

## Monte Carlo Probability Estimation

When counting set sizes analytically is hard, simulation estimates the probability.

```python
import random

def simulate_event(n_trials: int = 100_000) -> dict:
    """Two dice: P(sum=7) vs P(sum=12)"""
    count_7 = 0
    count_12 = 0
    for _ in range(n_trials):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        if total == 7:
            count_7 += 1
        elif total == 12:
            count_12 += 1
    return {
        "P(sum=7)": count_7 / n_trials,
        "P(sum=12)": count_12 / n_trials,
    }

random.seed(42)
results = simulate_event()
print(f"Simulation P(sum=7) = {results['P(sum=7)']:.4f} (theory: {6/36:.4f})")
print(f"Simulation P(sum=12) = {results['P(sum=12)']:.4f} (theory: {1/36:.4f})")
```

Sum 7 has six ways: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1). Sum 12 has only one: (6,6). Watching the simulation converge to theory builds confidence that the same approach works for problems too complex to solve analytically.

## From Events to Conditional Thinking

Once sample spaces and events are properly defined, the next natural step is conditional probability — what happens when new information narrows the sample space.

```python
# Single die: given "3 or higher"
omega = set(range(1, 7))
B = {3, 4, 5, 6}  # condition: 3 or higher

# P(even | 3 or higher) in the restricted sample space
A = {2, 4, 6}  # even
A_given_B = A & B  # {4, 6}
P_A_given_B = len(A_given_B) / len(B)
print(f"P(even | ≥3) = {P_A_given_B:.3f}")
print(f"P(even) = {len(A)/len(omega):.3f}")
print(f"Did the condition change the probability? {P_A_given_B != len(A)/len(omega)}")
```

Learning that a condition holds eliminates impossible outcomes, and you recalculate proportions within the remaining set. This is the essence of conditional probability, covered in the next post.

## Practical Examples: Event Definition in Production

In production systems, event definition is the starting point of every metric.

**A/B test bucket design**

```python
# Defining sample space for user assignment
buckets = {"control", "variant_A", "variant_B"}
# Mutually exclusive: each user belongs to exactly one bucket
# Total probability: 1.0
allocation = {"control": 0.50, "variant_A": 0.25, "variant_B": 0.25}
assert abs(sum(allocation.values()) - 1.0) < 1e-10

# Success event definition
# "Conversion" = session where a purchase event occurred
# Sample space: all sessions
# Event: sessions with conversion (a subset)
print("Sample space: all sessions")
print("Event: sessions with conversion")
print("Probability: conversion rate = |event| / |sample space|")
```

**Fraud detection rules**

```python
# Transaction event sample space
# Ω = all transactions
# A = "anomalous transaction" (fraud detection target)
# Aᶜ = "normal transaction"

# Practical challenges:
# 1. Definition of A varies across teams ("what counts as anomalous?")
# 2. Base rate is very low: P(A) ≈ 0.001
# 3. Ignoring the base rate means most positive predictions are false alarms

base_rate = 0.001
# TPR = 0.95, FPR = 0.01
tpr, fpr = 0.95, 0.01
# Precision: proportion of positive predictions that are truly fraud
precision = (tpr * base_rate) / (tpr * base_rate + fpr * (1 - base_rate))
print(f"Precision = {precision:.3f}")
print(f"{1-precision:.1%} of positive predictions are false alarms")
```

When the base rate is low, precision drops even with a good model. This happens because the sample space structure (normal transactions vastly outnumber fraud) is ignored when you focus only on the event. Bayes' theorem (Episode 4) tackles this problem formally.

## Five Common Mistakes

1. **Computing without writing Ω.** Feels fast at first but creates hidden disagreements about what is being calculated.

2. **Mixing up mutually exclusive and independent.** Events that cannot co-occur are strongly dependent, not independent.

3. **Mixing ordered and unordered outcomes.** In dice, cards, and drawing problems, this almost always changes the answer.

4. **Ignoring with- vs without-replacement.** Same-looking draw problems have different probability structures under different assumptions.

5. **Failing to state symmetry assumptions.** Whether the die is fair, the coin is unbiased, or each outcome is equally likely must be stated explicitly.

## Checklist

- [ ] I can define the sample space before any calculation.
- [ ] I can distinguish union, intersection, and complement events.
- [ ] I can explain the difference between mutually exclusive and independent.
- [ ] I can state whether order and replacement apply, and know how it changes counts.
- [ ] I can apply inclusion-exclusion for two or more events.
- [ ] I can verify De Morgan's laws in a probability context.
- [ ] I can estimate probability via Monte Carlo simulation.
- [ ] I can explain why sample space and event definition matter in A/B tests and fraud detection.

## Wrap-up

Sample spaces and events are the grammar of probability. Three things to remember: the sample space must come first, events are clearest when defined as sets, and mutually exclusive vs independent looks similar but asks entirely different questions.

The next post covers conditional probability. This post was about drawing the map of possible outcomes; the next shows how that map changes when new information arrives.

## Answering the Opening Questions

- **Why must the sample space come before any probability calculation?**
  - Listing all possible outcomes defines the domain. Only within that domain can events be defined as subsets and assigned probabilities.
- **What becomes easier when you express events as sets?**
  - Set notation gives you union, intersection, and complement — a systematic toolkit for combining, comparing, and negating events.
- **What do union, intersection, and complement mean in practice?**
  - Union is "A or B" (inclusion-exclusion handles overlap), intersection is "A and B," complement is "not A." Each maps directly to a probability formula.

<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- **Events and Sample Space (current)**
- Conditional Probability (upcoming)
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Sample spaces](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Wikipedia — Event (probability theory)](https://en.wikipedia.org/wiki/Event_(probability_theory))
- [Wikipedia — Sample space](https://en.wikipedia.org/wiki/Sample_space)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, SampleSpace, Events, SetTheory, Beginner
