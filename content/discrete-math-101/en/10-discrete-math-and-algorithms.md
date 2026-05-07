---
series: discrete-math-101
episode: 10
title: Discrete Mathematics and Algorithms
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
  - Algorithms
  - Complexity
  - NP
  - Applications
seo_description: How propositions, sets, proofs, recurrences, combinatorics, and graphs connect to algorithm analysis and real engineering decisions.
last_reviewed: '2026-05-04'
---

# Discrete Mathematics and Algorithms

> Discrete Math 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: Propositions, sets, proofs, recurrences, combinatorics, graphs — how do all the discrete-math ideas we have learned actually show up in real algorithms and code?

> Discrete math is the language of algorithms. Recurrences feed time-complexity analysis, combinatorics counts cases, graph theory powers routing and dependency resolution, and proof techniques validate correctness. This final article reorganizes the whole series from an algorithmic point of view and briefly steps up to higher concepts like P and NP.

<!-- a-grade-intro:end -->

## What You Will Learn

- Time complexity and Big-O — recurrences and the Master Theorem
- Algorithm correctness — induction and loop invariants
- Intuition for P, NP, and NP-completeness
- The whole series reframed as an algorithm toolbox

## Why It Matters

Discrete math studied in isolation feels abstract; paired with algorithms it becomes an immediate practical tool. The vocabulary of interviews, system design, and performance work is built directly on the concepts collected in this article.

> Without discrete math, algorithms look like magic; with it, they look like the result of reasoning.

## Concept at a Glance

> The three axes of algorithm analysis: (1) correctness = proof, (2) efficiency = complexity, (3) resource use = space/time trade-offs.

```text
discrete-math tool      algorithmic application
propositions, logic →   assertions, unit tests, formal verification
sets, functions    →    hash sets, indexing, functional programming
relations, eq.     →    Union-Find, graph classification
proof techniques   →    correctness, loop invariants
recurrences        →    time-complexity analysis (T(n) = 2T(n/2) + n)
combinatorics      →    counting, probability, backtracking
graphs             →    networks, dependencies, shortest paths
trees, traversal   →    BFS, DFS, MST, sorting
```

## Key Terms

| Term | Description |
| --- | --- |
| Big-O O(f) | Worst-case upper bound on running time |
| Master Theorem | General solution for divide-and-conquer recurrences |
| Loop invariant | Proposition that holds across loop iterations |
| P | Problems solvable in polynomial time |
| NP | Problems verifiable in polynomial time |

## Before / After

**Before — performance work via measurement only:**

```python
import time

start = time.time()
result = my_algorithm(big_input)
print(f"elapsed: {time.time() - start}")  # only comparable across input sizes
```

**After — predicting first, then measuring:**

```python
def analyze(n: int) -> str:
    """T(n) = 2T(n/2) + n → O(n log n) by the Master Theorem."""
    return f"for input size {n}, expect about {n * (n.bit_length() - 1)} comparisons"


print(analyze(1024))
```

A senior engineer's flow is to predict by theory, then verify by measurement.

## Hands-On: Step by Step

### Step 1: Recurrences and time complexity

```python
def merge_sort(arr: list) -> list:
    """T(n) = 2T(n/2) + n → O(n log n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(a: list, b: list) -> list:
    result, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result


print(merge_sort([5, 2, 8, 1, 9, 3]))
```

The Master Theorem reads off complexity directly from the relationship between a, b, and f(n) in T(n) = aT(n/b) + f(n).

### Step 2: Induction and loop invariants

```python
def sum_of_first_n(n: int) -> int:
    """The return value always equals 1 + 2 + ... + n — provable by induction."""
    total = 0
    for i in range(1, n + 1):
        # Loop invariant: total == i*(i-1)/2 at the top of each iteration
        total += i
    # On exit: total == n*(n+1)/2
    return total


assert sum_of_first_n(10) == 55
```

A loop invariant is a proposition the loop preserves; you prove it by induction. It explains why the algorithm gets the right answer.

### Step 3: Combinatorics and backtracking

```python
def subsets(nums: list) -> list:
    """All subsets of a set of size n — there are 2^n."""
    result = [[]]
    for x in nums:
        result.extend([s + [x] for s in result])
    return result


def permutations(nums: list) -> list:
    """All permutations of a set of size n — there are n!. Backtracking."""
    if not nums:
        return [[]]
    out = []
    for i, x in enumerate(nums):
        for rest in permutations(nums[:i] + nums[i + 1:]):
            out.append([x] + rest)
    return out


print(f"subset count:      {len(subsets([1, 2, 3]))}")
print(f"permutation count: {len(permutations([1, 2, 3]))}")
```

Knowing the count in advance keeps you from attempting impossible algorithms — once n exceeds 20 or so, exhaustive permutation search is hopeless, and combinatorics tells you instantly.

### Step 4: Graph algorithms in practice

```python
from collections import defaultdict, deque


def topological_sort(graph: dict) -> list:
    """Topological sort of a DAG — Kahn's algorithm (BFS-based)."""
    in_deg = defaultdict(int)
    for u in graph:
        for v in graph[u]:
            in_deg[v] += 1
    queue = deque([u for u in graph if in_deg[u] == 0])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                queue.append(v)
    return order


deps = {
    "compile": ["link"],
    "lex": ["parse"],
    "parse": ["compile"],
    "link": [],
}
print(f"build order: {topological_sort(deps)}")
```

Topological sort is the heart of dependency resolution and the default algorithm in build systems, package managers, and task schedulers.

### Step 5: Intuition for P, NP, and NP-completeness

```python
def subset_sum(nums: list, target: int) -> bool:
    """Subset Sum — NP-complete. Brute force is O(2^n) up to n."""
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask & (1 << i))
        if s == target:
            return True
    return False


print(subset_sum([3, 7, 1, 8, 5], 13))
```

P = problems solvable in polynomial time. NP = problems whose answers are verifiable in polynomial time. NP-complete = the hardest class inside NP. Whether P = NP is the biggest open question in computer science. In practice, the useful judgment is "if this problem is NP-complete, switch from exact solutions to approximations or heuristics."

## Notable Points

- Recurrences are a cost model for algorithms, and the Master Theorem is the standard tool for divide-and-conquer.
- Induction goes beyond pure math — it is the standard tool for proving algorithm correctness.
- Combinatorics builds intuition for what the input size can support.
- Recognizing NP-completeness is the signal to "stop chasing an exact solution."

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mixing average and worst case | Big-O is a worst-case bound | When the distribution is unknown, assume the worst |
| Forcing the Master Theorem | Recurrence does not match the form | Use direct expansion or the recursion-tree method |
| Underestimating input size | n=30 still allows 2^n | Always check the range of n first |
| Declaring "NP, so impossible" | Small n is still tractable | Weigh size against time budget |
| Skipping correctness proofs | Code runs but occasionally returns wrong answers | Pair loop invariants with unit tests |

## How This Is Used in Practice

- System-design interviews — comparing candidate algorithms by recurrence and Big-O
- Data pipeline optimization — choosing join order via graph search
- Package managers and build systems — topological sort and cycle detection
- Recommendation and search — graph embeddings and matrix factorization
- Compiler optimization — dataflow analysis as lattice theory plus graphs

## How a Senior Engineer Thinks

A senior engineer estimates input size, time complexity, and memory limits before writing a single line. That is reasoning by discrete math, not measurement. When they hit an NP-complete problem they switch strategies immediately to approximation or heuristic — the decision to "give up on optimality" is itself the result of analysis.

## Checklist

- [ ] Can you explain the relationship between Big-O and recurrences?
- [ ] Do you know when the Master Theorem applies?
- [ ] Can you verify algorithm correctness with loop invariants?
- [ ] Can you explain the difference between P and NP?
- [ ] Can you map the entire series back to algorithmic tools?

## Practice Problems

1. Use the Master Theorem to find the time complexity of T(n) = 3T(n/2) + n².

2. Prove the correctness of binary search using a loop invariant and induction.

3. Find an NP-complete (or similarly hard) problem in your own project and describe how you have routed around it — or how you would.

## Wrap-Up and Next Steps

Discrete math is the language of algorithms. Propositions, sets, proofs, recurrences, combinatorics, graphs — every concept feeds directly into time complexity, correctness, data-structure choice, and system-design decisions.

After finishing this series the next steps are: (1) deeper into the data-structures and algorithms series, (2) observing how these discrete-math tools combine in system design, and (3) making recurrence, proof, and complexity analysis a daily habit in your code.

<!-- toc:begin -->
- [What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Propositions and Logic](./02-propositions-and-logic.md)
- [Sets and Functions](./03-sets-and-functions.md)
- [Relations and Equivalence](./04-relations-and-equivalence.md)
- [Proof Techniques](./05-proof-techniques.md)
- [Sequences and Recurrence](./06-sequences-and-recurrence.md)
- [Combinatorics](./07-combinatorics.md)
- [Graph Theory Basics](./08-graph-theory-basics.md)
- [Trees and Graph Traversal](./09-trees-and-graph-traversal.md)
- **Discrete Mathematics and Algorithms (current)**
<!-- toc:end -->

## References

- [Introduction to Algorithms — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — P versus NP problem](https://en.wikipedia.org/wiki/P_versus_NP_problem)

Tags: Computer Science, Discrete Math, Algorithms, Complexity, NP, Applications
