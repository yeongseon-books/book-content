---
series: discrete-math-101
episode: 10
title: "Discrete Math 101 (10/10): Discrete Mathematics and Algorithms"
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
  - Algorithms
  - Complexity
  - NP
  - Applications
seo_description: How propositions, sets, proofs, recurrences, combinatorics, and graphs connect to algorithm analysis and real engineering decisions.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (10/10): Discrete Mathematics and Algorithms

This is the final post in the Discrete Math 101 series.

> Discrete Math 101 series (10/10)

**Core question**: Propositions, sets, proofs, recurrences, combinatorics, graphs — how do all the discrete-math ideas we have learned actually show up in real algorithms and code?

> Discrete math is the language of algorithms. Recurrences feed time-complexity analysis, combinatorics counts cases, graph theory powers routing and dependency resolution, and proof techniques validate correctness. This final article reorganizes the whole series from an algorithmic point of view and briefly steps up to higher concepts like P and NP.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Discrete Mathematics and Algorithms?
- Which signal should the example or diagram make visible for Discrete Mathematics and Algorithms?
- What failure should be prevented first when Discrete Mathematics and Algorithms reaches a real system?

## Big Picture

![discrete math 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/10/10-01-big-picture.en.png)

*discrete math 101 chapter 10 flow overview*

This picture places Discrete Mathematics and Algorithms inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Time complexity and Big-O — recurrences and the Master Theorem
- Algorithm correctness — induction and loop invariants
- Intuition for P, NP, and NP-completeness
- The whole series reframed as an algorithm toolbox

## Why It Matters

Discrete math studied in isolation feels abstract; paired with algorithms it becomes an immediate practical tool. The vocabulary of interviews, system design, and performance work is built directly on the concepts collected in this article.

> Without discrete math, algorithms look like magic; with it, they look like the result of reasoning.

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
print(f"elapsed: {time.time() - start}")
```

**After — predict first, then measure and compare:**

```python
def predicted_n_log_n(n: int) -> int:
    """A quick reference scale for T(n) = 2T(n/2) + n."""
    return n * (n.bit_length() - 1)

print(predicted_n_log_n(32))
```

A senior engineer's flow is to predict by theory, then verify by experiment.

## Hands-On: Step by Step

### Step 1: Predict first — why should merge sort be `O(n log n)`?

```python
def predicted_n_log_n(n: int) -> int:
    """Reference scale: n * log2(n), ignoring constant factors."""
    return n * (n.bit_length() - 1)

for n in [8, 16, 32, 64]:
    print(f"n={n:>2} -> prediction scale ≈ {predicted_n_log_n(n)}")
```

For merge sort the recurrence is `T(n) = 2T(n/2) + n`: two recursive subproblems plus one linear merge. In Master Theorem terms, `a=2`, `b=2`, and `f(n)=n`, so the predicted growth is `O(n log n)`. At this stage we are not timing anything yet. We first write down the expected shape of the work.

**Expected output**

```text
n= 8 -> prediction scale ≈ 24
n=16 -> prediction scale ≈ 64
n=32 -> prediction scale ≈ 160
n=64 -> prediction scale ≈ 384
```

- The important thing is the growth scale, not the exact constant.
- The values grow faster than linear `n` but nowhere near quadratic `n²`.

### Step 2: Run and compare — do the measured comparisons follow the prediction?

```python
def merge_and_count(left: list[int], right: list[int]) -> tuple[list[int], int]:
    merged = []
    i = j = comparisons = 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, comparisons

def merge_sort_count(arr: list[int]) -> tuple[list[int], int]:
    if len(arr) <= 1:
        return arr[:], 0
    mid = len(arr) // 2
    left, left_count = merge_sort_count(arr[:mid])
    right, right_count = merge_sort_count(arr[mid:])
    merged, merge_count = merge_and_count(left, right)
    return merged, left_count + right_count + merge_count

for n in [8, 16, 32, 64]:
    sample = list(range(n, 0, -1))
    sorted_sample, comparisons = merge_sort_count(sample)
    predicted = predicted_n_log_n(n)
    print(
        f"n={n:>2} | comparisons={comparisons:>3} | "
        f"prediction-scale={predicted:>3} | first={sorted_sample[:5]}"
    )
```

Now the recurrence turns into an experiment. The goal is not “match the formula exactly” — the formula is asymptotic. The goal is to verify that measured work grows with the same `n log n` shape.

**Expected output**

```text
n= 8 | comparisons= 12 | prediction-scale= 24 | first=[1, 2, 3, 4, 5]
n=16 | comparisons= 32 | prediction-scale= 64 | first=[1, 2, 3, 4, 5]
n=32 | comparisons= 80 | prediction-scale=160 | first=[1, 2, 3, 4, 5]
n=64 | comparisons=192 | prediction-scale=384 | first=[1, 2, 3, 4, 5]
```

**How to read the result**

- The comparison counts `12 → 32 → 80 → 192` grow faster than linear but much slower than quadratic, which fits the `n log n` story.
- `first=[1, 2, 3, 4, 5]` is the correctness check: performance analysis matters only if the algorithm still sorts correctly.
- Your exact counts may differ with a different input pattern, and that is fine. What should remain stable is the growth shape.
- If the counts look closer to `n²`, inspect the merge logic first or check whether the split is no longer balanced.

### Step 3: Connect complexity to correctness — induction and loop invariants

```python
def prefix_sum(nums: list[int]) -> list[int]:
    """Invariant: after processing index i, result[-1] equals sum(nums[:i+1])."""
    result = []
    running = 0
    for x in nums:
        running += x
        result.append(running)
    return result

values = [3, 1, 4, 1]
print(prefix_sum(values))
assert prefix_sum(values) == [3, 4, 8, 9]
```

If the recurrence is the language of performance, the loop invariant is the language of correctness. This is the other half of algorithm reasoning: not just “how fast?” but “why is the answer right?”

**Expected output**

```text
[3, 4, 8, 9]
```

- Each position must equal the sum of all previous inputs up to that point.
- If it differs, inspect the update order of `running` and `append` first.

### Step 4: Extend the workflow to graphs — topological sort is dependency validation

```python
from collections import defaultdict, deque

def topological_sort(graph: dict[str, list[str]]) -> list[str]:
    """Deterministic topological sort with cycle detection."""
    in_deg = defaultdict(int)
    for u in graph:
        in_deg[u] += 0
        for v in graph[u]:
            in_deg[v] += 1
    queue = deque(sorted(u for u in graph if in_deg[u] == 0))
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in sorted(graph[u]):
            in_deg[v] -= 1
            if in_deg[v] == 0:
                queue.append(v)
    if len(order) != len(graph):
        raise ValueError("cycle detected")
    return order

deps = {
    "lint": ["test"],
    "test": ["build"],
    "build": ["deploy"],
    "deploy": [],
}
print(f"build order: {topological_sort(deps)}")

cyclic_deps = {
    "parse": ["compile"],
    "compile": ["link"],
    "link": ["parse"],
}

try:
    topological_sort(cyclic_deps)
except ValueError as exc:
    print(exc)
```

This is the graph-version extension of the same mindset: predict the legal structure first, then validate it mechanically. A build graph should produce an order if it is a DAG and should fail loudly if it contains a cycle.

**Expected output**

```text
build order: ['lint', 'test', 'build', 'deploy']
cycle detected
```

- The sample DAG yields one deterministic order.
- If `cycle detected` never appears for the cyclic example, your safety check is incomplete.

### Step 5: Combinatorics and hardness — why does subset sum get expensive so quickly?

```python
def subset_sum(nums: list[int], target: int) -> bool:
    """Subset Sum — NP-complete. Brute force is O(2^n)."""
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask & (1 << i))
        if s == target:
            return True
    return False

print(f"target 13 exists: {subset_sum([3, 7, 1, 8, 5], 13)}")
print(f"target 2 exists:  {subset_sum([3, 7, 1, 8, 5], 2)}")
```

Subset Sum now plays a supporting role rather than competing with the merge-sort experiment. Its job is to sharpen the final intuition: once the search space grows like `2^n`, exact exhaustive search stops being the default plan.

**Expected output**

```text
target 13 exists: True
target 2 exists:  False
```

- `13` exists because `8 + 5 = 13`.
- `2` does not exist for the sample set.
- The point is the explosive search space, not the specific boolean values.

### Intuition for P, NP, and NP-completeness

P = problems solvable in polynomial time. NP = problems whose answers are verifiable in polynomial time. NP-complete = the hardest problems inside NP. In practice, the most useful judgment is not philosophical but operational: when a problem smells NP-complete, start looking for approximation, pruning, or heuristics.

## Notable Points

- Recurrences are most useful when they become explicit predictions that you later test against measurements.
- Loop invariants and induction explain correctness, not just runtime.
- Graph algorithms like topological sort should validate both the success path and the failure path.
- Recognizing NP-completeness is the signal to stop chasing exact exhaustive solutions by default.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Discrete Mathematics and Algorithms?**
  - The article treats Discrete Mathematics and Algorithms as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Discrete Mathematics and Algorithms?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Discrete Mathematics and Algorithms reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Discrete Math 101 (1/10): What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): Propositions and Logic](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): Relations and Equivalence](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): Proof Techniques](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): Sequences and Recurrence](./06-sequences-and-recurrence.md)
- [Discrete Math 101 (7/10): Combinatorics](./07-combinatorics.md)
- [Discrete Math 101 (8/10): Graph Theory Basics](./08-graph-theory-basics.md)
- [Discrete Math 101 (9/10): Trees and Graph Traversal](./09-trees-and-graph-traversal.md)
- **Discrete Mathematics and Algorithms (current)**

<!-- toc:end -->

## References

- [Introduction to Algorithms — Cormen et al., Chapters 2, 4, 22, 34](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Mathematics for Computer Science — Lehman, Leighton, Meyer](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Algorithms, 4th Edition — Sedgewick & Wayne, Section 2.2 Mergesort](https://algs4.cs.princeton.edu/22mergesort/)
- [Algorithms, 4th Edition — Sedgewick & Wayne, Section 4.2 Directed Graphs](https://algs4.cs.princeton.edu/42digraphs/)
- [MIT OpenCourseWare 6.046J — Design and Analysis of Algorithms](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/)
- [Clay Mathematics Institute — P vs NP Problem](https://www.claymath.org/millennium/p-vs-np)

Tags: Computer Science, Discrete Math, Algorithms, Complexity, NP, Applications
