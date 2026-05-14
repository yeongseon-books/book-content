---
series: discrete-math-101
episode: 5
title: Proof Techniques
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Discrete Math
  - Mathematical Proof
  - Induction
  - Contradiction
  - Algorithm Correctness
seo_description: Direct, contrapositive, contradiction, and inductive proofs — the core techniques and how to prove algorithm correctness.
last_reviewed: '2026-05-04'
---

# Proof Techniques

This is post 5 in the Discrete Math 101 series.

> Discrete Math 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: How do we guarantee that an algorithm "always" works correctly? Even if 100 tests pass, can't input 100,001 still fail?

> A proof is a rigorous argument that a statement holds in every possible case. Direct proof, contrapositive, contradiction, and mathematical induction are the four core techniques in discrete math, and they are the same tools used to prove algorithm correctness and termination. This article walks through each technique and shows how it applies to real code verification.

<!-- a-grade-intro:end -->

## What You Will Learn

- Direct and contrapositive proofs
- Proof by contradiction
- Mathematical induction (and strong induction)
- Proving algorithm correctness and termination

## Why It Matters

Tests can show the presence of bugs but not their absence. Distributed consensus algorithms, cryptographic protocols, and compiler optimizations all rely on formal proofs. Recursive functions are proven correct by induction; algorithm termination is proven via well-founded measures.

> A proof = a guarantee for every possible input.

## Concept at a Glance

> The proof technique you choose depends on the form of the statement: P → Q for direct/contrapositive, ¬P for contradiction, ∀n: P(n) for induction.

```text
   Statement to prove
        │
   ┌────┼────────────┬─────────────┐
   ↓    ↓            ↓             ↓
  P→Q  P→Q          ¬P            ∀n: P(n)
  Direct Contrap.   Contradict.   Induction
                                    │
                                    ↓
                             Base + Inductive step
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Direct proof | Assume P, derive Q |
| Contrapositive | Assume ¬Q, derive ¬P |
| Contradiction | Assume ¬P, derive a contradiction |
| Induction | Base P(0) + (P(k) → P(k+1)) |
| Tautology | A statement true in every case |

## Before / After

**Before — no proof:**

```python
# "100 tests passed, so it must work" — no guarantee on all inputs
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

**After — correctness reasoning attached:**

```python
def gcd(a: int, b: int) -> int:
    """Euclidean algorithm.

    Correctness: gcd(a, b) = gcd(b, a mod b) (mathematical theorem)
    Termination: b strictly decreases each iteration on the naturals → well-founded
    """
    while b:
        a, b = b, a % b
    return a
```

## Hands-On: Step by Step

### Step 1: Direct Proof

```python
# Claim: the square of an even number is even
# Proof: assume n = 2k. Then n² = 4k² = 2(2k²), which is even.

def verify_direct(limit: int = 1000) -> bool:
    """Empirical check (the math proof is what really establishes it)"""
    for k in range(limit):
        n = 2 * k
        assert (n ** 2) % 2 == 0
    return True


print(f"Verified: {verify_direct()}")
```

Verification and proof are different. Verification confirms a finite set of cases; a proof covers them all.

### Step 2: Contrapositive

```python
# Claim: if n² is even, then n is even
# Direct is awkward, but the contrapositive is easy:
# Contrapositive: if n is odd, then n² is odd.
# n = 2k + 1 → n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1 → odd

def contrapositive_check(limit: int = 1000) -> None:
    for n in range(limit):
        if n % 2 == 1:           # n odd
            assert (n ** 2) % 2 == 1   # n² odd


contrapositive_check()
print("Contrapositive cases verified")
```

The contrapositive proves P → Q by proving ¬Q → ¬P. Both have the same truth value.

### Step 3: Proof by Contradiction

```python
# Claim: √2 is irrational
# Assume √2 = p/q in lowest terms. Then 2q² = p².
# → p² is even → p is even → p = 2k
# → 2q² = 4k² → q² = 2k² → q² is even → q is even
# → both p and q even ⊥ "lowest terms" assumption

import math


def is_rational_approx(x: float, max_q: int = 10000) -> bool:
    """Empirical: does x have an exact fraction with denominator ≤ max_q?"""
    for q in range(1, max_q):
        p = round(x * q)
        if abs(x - p / q) < 1e-15:
            return True
    return False


print(f"Is √2 expressible as fraction with q ≤ 10000? {is_rational_approx(math.sqrt(2))}")
```

Contradiction assumes the negation of the conclusion and derives a contradiction. Distributed-systems impossibility results (FLP, CAP) are proofs by contradiction.

### Step 4: Mathematical Induction

```python
# Claim: 1 + 2 + ... + n = n(n+1)/2
# Base P(1): 1 = 1·2/2 = 1 ✓
# Inductive step: assuming P(k), prove P(k+1)
#   1 + 2 + ... + k + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2 ✓


def gauss_sum(n: int) -> int:
    return n * (n + 1) // 2


def actual_sum(n: int) -> int:
    return sum(range(1, n + 1))


for n in [1, 10, 100, 1000]:
    assert gauss_sum(n) == actual_sum(n)
    print(f"n={n}: formula={gauss_sum(n)}, actual={actual_sum(n)}")
```

Induction has two parts: (1) the base case — the smallest input — and (2) the inductive step — going from k to k+1. Together they cover every natural number.

### Step 5: Proving Algorithm Correctness

```python
# Claim: this returns the correct index of target in a sorted array,
# or -1 if absent.

def binary_search(arr: list, target: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        # Invariant: if target is in arr, it lies in arr[low..high]
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# Termination: high - low strictly decreases each iteration
# Correctness: loop invariant + termination condition
# Both formal proofs use induction.

for arr, target in [([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4)]:
    print(f"binary_search({arr}, {target}) = {binary_search(arr, target)}")
```

Loop invariants are the heart of algorithm correctness proofs. Hoare logic and Floyd–Hoare verification are both built on them.

## Notable Points

- Verification ≠ proof — verification covers some cases, proof covers all
- Contrapositive and contradiction are useful when direct proof is hard
- Induction is the standard technique for natural numbers and recursion
- Algorithm correctness is established by loop invariants

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mistake verification for proof | Some passes ≠ all cases proven | Use a formal proof or verifier |
| Skip the induction base | Only k → k+1, no starting point | Always state P(0) or P(1) |
| Wrong negation in contradiction | Unclear what "not P → Q" means | Use "P ∧ ¬Q" |
| Confuse converse with contrapositive | Converse is not equivalent | Only contrapositive (¬Q → ¬P) is |
| Skip termination proof | Loop may never end | Show a well-founded measure that decreases |

## How This Is Used in Practice

- Distributed consensus (Paxos, Raft) proofs of safety and liveness
- Cryptographic protocol security proofs (BAN logic, Tamarin)
- Semantics-preserving compiler optimization (CompCert)
- TLA+, Coq, and Lean for industrial formal verification
- Code review questions like "does this always hold? what about edge cases?" are informal proofs

## How a Senior Engineer Thinks

Senior engineers run informal proofs in their heads while reading code. "What is the loop invariant? What measure decreases? Is the exit condition reachable?" Even without writing formal proofs, this proof-style thinking governs correctness. In domains where tests cannot cover everything (such as distributed systems), they rely on formal models and proofs.

## Checklist

- [ ] I can explain the four proof techniques
- [ ] I remember the two parts of induction
- [ ] I distinguish converse from contrapositive
- [ ] I understand loop invariants
- [ ] I can clearly distinguish verification from proof

## Practice Problems

1. Prove directly: "if n is divisible by 3, so is n²".

2. Use induction to prove 1² + 2² + ... + n² = n(n+1)(2n+1)/6.

3. Pick one of your `while` loops and write down its loop invariant and termination measure.

## Wrap-Up and Next Steps

A proof guarantees correctness across every possible input. The four techniques — direct, contrapositive, contradiction, induction — cover almost every claim in discrete math, and the same tools prove algorithm correctness. The thinking of a senior engineer closely resembles informal proof.

Next, we cover sequences and recurrences — induction's natural partner and an essential tool for algorithm analysis.

<!-- toc:begin -->
- [What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Propositions and Logic](./02-propositions-and-logic.md)
- [Sets and Functions](./03-sets-and-functions.md)
- [Relations and Equivalence](./04-relations-and-equivalence.md)
- **Proof Techniques (current)**
- Sequences and Recurrence (upcoming)
- Combinatorics (upcoming)
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)
<!-- toc:end -->

## References

- [Book of Proof — Richard Hammack (Free)](https://www.people.vcu.edu/~rhammack/BookOfProof/)
- [How to Prove It — Daniel Velleman](https://www.cambridge.org/core/books/how-to-prove-it/6D2965D6905658D704B782B9D67E2989)
- [Wikipedia — Mathematical Proof](https://en.wikipedia.org/wiki/Mathematical_proof)
- [MIT OCW — Mathematics for Computer Science, Lectures 2-5](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, Discrete Math, Mathematical Proof, Induction, Contradiction, Algorithm Correctness
