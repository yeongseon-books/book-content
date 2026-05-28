---
series: discrete-math-101
episode: 1
title: "Discrete Math 101 (1/10): What Is Discrete Mathematics?"
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
  - Foundations
  - Logic
  - Sets
  - Mathematics
seo_description: What discrete mathematics is, how it differs from calculus, and why it is the universal language of computer science.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (1/10): What Is Discrete Mathematics?

This is the first post in the Discrete Math 101 series.

> Discrete Math 101 series (1/10)

**Core question**: How is discrete mathematics different from calculus, and why is it the first math course in every computer science curriculum?

> Discrete mathematics studies "countable" objects — integers, propositions, sets, graphs — entities that come in distinct, separated units. Computers are inherently discrete machines, so every theory in computer science is built on discrete math. This article maps the field, contrasts it with continuous math, and previews the topics covered in this series.


![discrete math 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/01/01-01-big-picture.en.png)
*discrete math 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Discrete Mathematics??
- Which signal should the example or diagram make visible for What Is Discrete Mathematics??
- What failure should be prevented first when What Is Discrete Mathematics? reaches a real system?

## What You Will Learn

- How discrete and continuous mathematics differ
- The five pillars of discrete mathematics
- Why discrete math is mandatory for computer scientists
- The roadmap for this entire series

## Why It Matters

Analyzing algorithms requires recurrences and combinatorics. Understanding databases requires set and relation theory. Designing networks requires graph theory. Discrete math is not just another math class — it is the shared language across all of computer science.

> Discrete math = the language a computer scientist uses to organize their thinking.

This series walks through the core concepts one episode at a time, drawing the link to computer science at every step.

> Discrete math rests on five pillars: logic, sets, functions, combinatorics, and graphs. They are unified by the property of "discreteness."

```text
            Logic (propositions, proofs)
                |
        Sets / Functions / Relations
                |
        ┌───────┼───────┐
   Combinatorics  Sequences   Graphs
       (count)   (recurrence) (structure)
        └───────┼───────┘
                |
        Algorithms / Data structures
                |
        Computer science applications
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Discrete | Countable in distinct, separated units |
| Continuous | Connected without breaks |
| Proposition | A sentence that is true or false |
| Set | A collection of distinct elements |
| Graph | A structure of vertices and edges |

## Before / After

**Before — without discrete math:**

```python
# Hard to answer "why is this O(log n)?"
def binary_search(data, target):
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

**After — with discrete math:**

```python
# Express it as the recurrence T(n) = T(n/2) + 1
# and prove O(log n) via the Master Theorem.
# Also recognize that "sorted array" is a total-order precondition.
def binary_search(data, target):
    """Precondition: data is sorted under a total order.
    Complexity: T(n) = T(n/2) + O(1) ⟹ O(log n)
    """
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

## Hands-On: Step by Step

### Step 1: Discrete vs Continuous

```python
# Continuous: infinitely many values in [0, 1]
# Discrete: {0, 1, 2, 3} is clearly countable
import math

continuous_sample = [i * 0.0001 for i in range(10001)]  # an approximation
discrete_set = list(range(11))                          # exact

print(f"Continuous samples: {len(continuous_sample)}")
print(f"Discrete size: {len(discrete_set)}")
print(f"Continuous gap: {continuous_sample[1] - continuous_sample[0]}")
print(f"Discrete gap: {discrete_set[1] - discrete_set[0]}")
```

Memory is segmented into bits, so computers are intrinsically discrete. Floating-point numbers only approximate the reals — they are never truly continuous.

### Step 2: Propositions and Truth Values

```python
# A proposition: a sentence that is unambiguously true or false
def is_prime(n: int) -> bool:
    """Return True if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# "7 is prime" is a true proposition
# "9 is prime" is a false proposition
print(f"7 is prime: {is_prime(7)}")  # True
print(f"9 is prime: {is_prime(9)}")  # False
```

Propositional logic underlies every computer reasoning task. `if`, `while`, and SQL `WHERE` clauses all evaluate the truth value of propositions.

### Step 3: Set Operations

```python
# Sets are the most basic discrete structure
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}

print(f"Union A ∪ B: {A | B}")
print(f"Intersection A ∩ B: {A & B}")
print(f"Difference A - B: {A - B}")
print(f"Symmetric difference A △ B: {A ^ B}")
print(f"Subset A ⊆ {A | B}: {A <= (A | B)}")
```

SQL `JOIN` is a direct application of set operations. `UNION`, `INTERSECT`, and `EXCEPT` correspond one-to-one with the operators above.

### Step 4: Modeling Relationships with Graphs

```python
# A graph is built from vertices and edges
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

def neighbors(g: dict, node: str) -> list:
    """Return neighbors of the given vertex."""
    return g.get(node, [])

for node in graph:
    print(f"{node} neighbors: {neighbors(graph, node)}")
```

Social networks, road maps, dependency trees, internet routing — almost every relationship in computer science is modeled as a graph.

### Step 5: The Series Roadmap

```python
roadmap = [
    (1, "What Is Discrete Mathematics?", "the big picture"),
    (2, "Propositions and Logic", "truth values, operators, inference"),
    (3, "Sets and Functions", "set ops, domain, range"),
    (4, "Relations and Equivalence", "properties, classes, partitions"),
    (5, "Proof Techniques", "direct, contradiction, induction"),
    (6, "Sequences and Recurrence", "recursion, Master Theorem"),
    (7, "Combinatorics", "permutations, combinations, pigeonhole"),
    (8, "Graph Theory Basics", "vertices, edges, paths, connectivity"),
    (9, "Trees and Graph Traversal", "BFS, DFS, spanning trees"),
    (10, "Discrete Math and Algorithms", "complexity, NP, applications"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## Notable Points

- Discrete structures are the only objects a computer can represent exactly
- Propositions, sets, and graphs are different abstractions sharing one property — discreteness
- Algorithm analysis depends on recurrences and combinatorics
- The tools of discrete math show up directly in SQL, routing, and dependency management

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Treat as abstract math | You stall on algorithm analysis | Pair every concept with code |
| Memorize proofs | Cannot apply to new problems | Understand structure and motivation |
| See graphs only visually | Breaks down on large inputs | Practice adjacency list and matrix forms |
| Confuse combinations and permutations | Wrong counting | Distinguish by whether order matters |
| Confuse propositions and predicates | Stuck on formal logic | Master quantifiers ∀ and ∃ |

## How This Is Used in Practice

- Database query optimization uses set theory and relational algebra
- Dependency tools (npm, pip) rely on topological sorting of graphs
- Distributed consensus algorithms use propositional logic and consistency proofs
- Recommendation systems use graph embeddings rooted in graph theory
- Compiler optimization analyzes data-flow graphs

## How a Senior Engineer Thinks

A senior engineer can grasp the essence of any new algorithm quickly because they can re-cast the problem in the vocabulary of discrete math. "This is graph traversal." "This is set partitioning." Naming the structure is half the solution.

Senior engineers are also obsessive about correctness. "Almost right" is not allowed. Discrete math is a world of true and false, and they bring that same standard to system design.

## Checklist

- [ ] I can explain in my own words how discrete and continuous differ
- [ ] I can list the five pillars (logic, sets, functions, combinatorics, graphs)
- [ ] I understand why computer science needs discrete math
- [ ] I see the link between SQL JOIN and set operations
- [ ] I have reviewed the full series roadmap

## Practice Problems

1. Find five examples of "discrete" and five examples of "continuous" objects from daily life. Which ones can a computer represent exactly?

2. Construct an unsorted array on which `binary_search` returns the wrong index. Which precondition was violated?

3. Sketch the friend graph of your social network. What are the vertices, and what does an edge mean?

## Wrap-Up and Next Steps

Discrete math is the study of countable objects, and it is the universal language of computer science. The five pillars — logic, sets, functions, combinatorics, graphs — connect directly to algorithms, databases, networks, and beyond.

Next, we examine the smallest unit of discrete math — the proposition — together with the logical operators that drive every computer's reasoning.

## Answering the Opening Questions

- **How do discrete and continuous mathematics differ?**
  - The article showed with `continuous_sample` and `discrete_set` examples that continuous subjects can only be handled through approximate samples, while discrete subjects allow exact element counting. Since computer memory and bits are inherently discrete, structures like propositions, sets, and graphs — not real numbers — become the fundamental language of computer science.
- **How do the five pillars of discrete math connect?**
  - As the ASCII diagram showed, it starts with logic, descends through sets, functions, and relations, then passes through combinatorics, sequences, and graphs to reach algorithms and data structures. The binary search recurrence, set operation code, and graph neighbor lookup examples demonstrate these five pillars are a connected toolbox, not separate chapters.
- **Why is discrete math mandatory in CS curricula?**
  - Algorithm analysis needs recurrences like `T(n)=T(n/2)+1`, databases read as set operations like `A ∪ B` and `A ∩ B`, and networks and dependency management are modeled as graphs. So discrete math isn't a separate elective but the common foundation for understanding algorithms, databases, and networks.
<!-- toc:begin -->
## In this series

- **What Is Discrete Mathematics? (current)**
- Propositions and Logic (upcoming)
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

- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [MIT OCW — Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
- [Wikipedia — Discrete Mathematics](https://en.wikipedia.org/wiki/Discrete_mathematics)
- [Book of Proof — Richard Hammack](https://www.people.vcu.edu/~rhammack/BookOfProof/)

Tags: Computer Science, Discrete Math, Foundations, Logic, Sets, Mathematics
