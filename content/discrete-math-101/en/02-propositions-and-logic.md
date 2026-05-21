---
series: discrete-math-101
episode: 2
title: "Discrete Math 101 (2/10): Propositions and Logic"
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
  - Propositional Logic
  - Inference
  - Truth Tables
  - Predicates
seo_description: Propositions, truth values, logical connectives, truth tables, predicates, and quantifiers — the foundation of all computer reasoning.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (2/10): Propositions and Logic

This is post 2 in the Discrete Math 101 series.

> Discrete Math 101 series (2/10)

**Core question**: How is `if x > 0 and y < 10` actually evaluated, and what is its mathematical foundation?

> Propositional logic deals with sentences that are unambiguously true or false (propositions) and the operators (AND, OR, NOT) that combine them. Every conditional in every programming language, every SQL `WHERE` clause, and every digital logic gate is a direct application. This article covers propositions, truth tables, equivalence transformations, and predicate logic.


![discrete math 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/02/02-01-big-picture.en.png)
*discrete math 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Propositions and Logic?
- Which signal should the example or diagram make visible for Propositions and Logic?
- What failure should be prevented first when Propositions and Logic reaches a real system?

## What You Will Learn

- The distinction between propositions and non-propositions
- The five basic logical connectives
- Building truth tables and proving logical equivalence
- Predicates and the quantifiers ∀ and ∃

## Why It Matters

Every `if` statement is the evaluation of a proposition. Every database query asks whether a predicate is satisfied. Every digital circuit gate is a logical operation. Without propositional logic, you cannot simplify complex conditionals or debug them with confidence.

> Propositional logic = a symbolic system for precise reasoning.

This article builds the logical foundation that the next chapter (set theory) extends.

> Propositions carry truth values, combined by connectives whose meaning is defined by truth tables.

```text
  Props P, Q  ──→  Operators  ──→  Compound prop.
                 ┌──────────┐
                 │ ¬ (NOT)  │
                 │ ∧ (AND)  │
                 │ ∨ (OR)   │
                 │ → (impl) │
                 │ ↔ (iff)  │
                 └──────────┘
                       ↓
                  Truth tables
                       ↓
                Logical equivalence
```

## Key Terms

| Term | Symbol | Meaning |
| --- | --- | --- |
| Negation | ¬P | True iff P is false |
| Conjunction | P ∧ Q | True iff both are true |
| Disjunction | P ∨ Q | True iff at least one is true |
| Implication | P → Q | False only when P true, Q false |
| Biconditional | P ↔ Q | True iff truth values match |

## Before / After

**Before — without logic:**

```python
# Nested conditions, no simplification
if not (x > 0 and y > 0):
    if not (x > 0):
        handle_x()
    if not (y > 0):
        handle_y()
```

**After — De Morgan's law applied:**

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
if x <= 0 or y <= 0:
    if x <= 0:
        handle_x()
    if y <= 0:
        handle_y()
```

## Hands-On: Step by Step

### Step 1: Propositions and Truth Values

```python
# A proposition is unambiguously true or false
# A question is not a proposition

propositions = {
    "2 is even": True,
    "Paris is the capital of the United States": False,
    "100 is prime": False,
    "1 + 1 = 2": True,
}

for statement, truth in propositions.items():
    print(f"{statement}: {truth}")
```

### Step 2: Basic Connectives

```python
def NOT(p: bool) -> bool:
    return not p

def AND(p: bool, q: bool) -> bool:
    return p and q

def OR(p: bool, q: bool) -> bool:
    return p or q

def IMPLIES(p: bool, q: bool) -> bool:
    """P → Q: false only when P true and Q false"""
    return (not p) or q

def IFF(p: bool, q: bool) -> bool:
    """P ↔ Q: true when both have the same value"""
    return p == q

print(IMPLIES(True, False))  # False
print(IMPLIES(False, True))  # True (false premise → always true)
print(IFF(True, True))       # True
```

The fact that P → Q is true whenever P is false often surprises beginners. "If it rains, I'll bring an umbrella" is not violated on dry days.

### Step 3: Generate a Truth Table

```python
from itertools import product

def truth_table(variables: list[str], expr) -> None:
    """Print the truth table for a given expression."""
    header = " | ".join(variables) + " | result"
    print(header)
    print("-" * len(header))
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        result = expr(**env)
        row = " | ".join(str(v)[0] for v in values) + f" | {str(result)[0]}"
        print(row)

# Truth table for (P ∧ Q) → P
truth_table(["P", "Q"], lambda P, Q: IMPLIES(AND(P, Q), P))
```

A truth table is the "execution" of propositional logic. Because it enumerates every input combination, you can always check equivalence.

### Step 4: Verify De Morgan's Laws

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
# ¬(P ∨ Q) ≡ ¬P ∧ ¬Q

def equivalent(expr1, expr2, variables: list[str]) -> bool:
    """Two expressions are equivalent if they agree on every input."""
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        if expr1(**env) != expr2(**env):
            return False
    return True

lhs = lambda P, Q: NOT(AND(P, Q))
rhs = lambda P, Q: OR(NOT(P), NOT(Q))

print(f"De Morgan holds: {equivalent(lhs, rhs, ['P', 'Q'])}")
```

### Step 5: Predicates and Quantifiers

```python
# A predicate is a proposition-valued function over a variable
def is_even(n: int) -> bool:
    return n % 2 == 0

# Universal ∀: "for all n"
def for_all(domain, predicate) -> bool:
    return all(predicate(x) for x in domain)

# Existential ∃: "there exists an n"
def there_exists(domain, predicate) -> bool:
    return any(predicate(x) for x in domain)

numbers = [2, 4, 6, 8, 10]

print(f"∀x ∈ {numbers}: x is even = {for_all(numbers, is_even)}")
print(f"∃x ∈ [1,2,3]: x is even = {there_exists([1, 2, 3], is_even)}")
```

Quantifiers map directly onto SQL's `ALL` and `ANY`. `WHERE x > ALL(SELECT ...)` is universal quantification.

## Notable Points

- Every connective is defined by its truth table
- P → Q is logically equivalent to ¬P ∨ Q
- De Morgan's laws control how negation distributes
- Quantifiers ∀ and ∃ turn predicates into propositions

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Misreading implication | "False premise → true" feels wrong | Remember "from false, anything follows" |
| Confusing AND/OR precedence | Missing parens cause bugs | Always parenthesize explicitly |
| Wrong distribution of negation | ¬(P ∧ Q) ≠ ¬P ∧ ¬Q | Memorize De Morgan |
| Swapping ∀ and ∃ order | "For all x, some y" ≠ "Some y for all x" | Preserve quantifier order |
| Treating predicates as propositions | P(x) with free x is not a proposition | Bind it with a quantifier |

## How This Is Used in Practice

- SQL `WHERE` optimization uses logical equivalence transformations
- Code review simplifies complex conditionals via De Morgan
- Digital circuit design uses AND, OR, NOT, NAND, NOR gates
- Formal verification expresses system properties as propositions
- Search engines accept Boolean queries (`apple AND NOT pie`)

## How a Senior Engineer Thinks

When senior engineers see complex `if` statements, their first reaction is "can this be simplified?" They mentally sketch a truth table and often reduce conditions by half through equivalence transformations. They also reason with quantifiers — "is this always true, or only sometimes?" — which is how they avoid missing edge cases.

## Checklist

- [ ] I can sketch the truth table for all five connectives
- [ ] I can explain implication intuitively
- [ ] I can apply De Morgan to real code
- [ ] I can illustrate ∀ vs ∃ with a SQL example
- [ ] I can distinguish predicates from propositions

## Practice Problems

1. Build the truth table for `(P → Q) ∧ (Q → R) → (P → R)` and confirm it is a tautology.

2. Pick one nested `if` from your own code and simplify it using De Morgan's laws.

3. Decide whether "∀x ∃y: x + y = 0" and "∃y ∀x: x + y = 0" are true or false over the integers, and justify each answer.

## Wrap-Up and Next Steps

Propositional logic is the foundation of all computer reasoning. With five connectives, truth tables, and equivalence laws, you can manipulate complex conditions precisely. Quantifiers extend propositions into predicate logic for richer expression.

Next, together with logic we cover the other foundation of discrete math — sets and functions.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Propositions and Logic?**
  - The article treats Propositions and Logic as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Propositions and Logic?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Propositions and Logic reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Discrete Math 101 (1/10): What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- **Propositions and Logic (current)**
- Sets and Functions (upcoming)
- Relations and Equivalence (upcoming)
- Proof Techniques (upcoming)
- Sequences and Recurrence (upcoming)
- Combinatorics (upcoming)
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)

<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 1](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Stanford Encyclopedia of Philosophy — Propositional Logic](https://plato.stanford.edu/entries/logic-propositional/)
- [Wikipedia — De Morgan's Laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [MIT OCW — Mathematics for Computer Science, Lectures 1-3](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, Discrete Math, Propositional Logic, Inference, Truth Tables, Predicates
