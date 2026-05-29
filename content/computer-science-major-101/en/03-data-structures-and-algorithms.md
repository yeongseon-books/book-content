---
series: computer-science-major-101
episode: 3
title: "Computer Science Major 101 (3/10): Data Structures and Algorithms"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - CS
  - DataStructures
  - Algorithms
  - Complexity
  - Beginner
seo_description: A beginner-friendly tour of data structures and algorithms covering complexity, study order, and interview preparation.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (3/10): Data Structures and Algorithms

Many students feel that this course is where the major truly begins. If everything before was warm-up, this is where you start learning the criteria for solving problems *better* — not just correctly.

This is the 3rd post in the Computer Science Major 101 series.


![computer science major 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/03/03-01-dsa-problem-solving-map.en.png)
*computer science major 101 chapter 3 flow overview*
> Data structures and algorithms are not things to memorize—they are *patterns*. When you see a problem, the right structure should come to mind automatically.

## Questions to Keep in Mind

- Why are data structures and algorithms the core course for nearly every CS major?
- How do learning data structures and learning algorithms differ, and why must they go together?
- What do time complexity and space complexity let you judge in real code?

## What You Will Learn

- Meaning of *data structures*
- Meaning of *algorithms*
- *Time and space complexity*
- Study *order*
- Link to coding *interviews*

## Why It Matters

Complexity thinking is the first standard of code quality. Moving beyond "does it produce the right output" to "how does cost grow as input grows" is where professional problem-solving begins.

## Concept at a Glance

> A data structure is how you store data. An algorithm is how you process it. Complexity is the cost table for those choices.

A data structure is a choice about *how* to hold data; an algorithm is a choice about *what procedure* to apply to that data. Both choices must align before complexity becomes meaningful, and that complexity sense carries through to problem-solving and interviews alike.

## Key Terms

- **Array**: contiguous memory — fast index access.
- **Linked list**: pointer-based structure — fast insert/delete at known positions.
- **Tree**: hierarchical structure — good for sorted data and search.
- **Graph**: relation structure — connections, paths, cycles.
- **Complexity**: growth rate of cost as input scales.

## Before/After

**Before**: You only write for loops and assume correctness is enough.

**After**: You ask which approach solves the problem at lower cost, and you can explain why.

## Hands-on: Mini DSA Kit

### Step 1 — Array sum

```python
def total(xs):
    return sum(xs)
```

The simplest traversal example. The feel of scanning the entire input once becomes the reference point for understanding complexity later.

### Step 2 — Linear search

```python
def find(xs, t):
    return any(x == t for x in xs)
```

The most natural search when you do not know whether the data is sorted. The downside: in the worst case you scan everything.

### Step 3 — Binary search

```python
def bsearch(xs, t):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        m = (lo + hi) // 2
        if xs[m] == t:
            return m
        if xs[m] < t:
            lo = m + 1
        else:
            hi = m - 1
    return -1
```

With sorted data, you can halve the search range each step. This is the most intuitive demonstration of why complexity thinking matters.

### Step 4 — Stack

```python
stack = []
stack.append(1)
stack.pop()
```

Simple, yet the backbone of many problems. Function calls, bracket matching, undo operations — all share the same axis.

### Step 5 — Graph BFS

```python
from collections import deque
def bfs(g, s):
    seen, q = {s}, deque([s])
    while q:
        u = q.popleft()
        for v in g[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return seen
```

Breadth-first search expands outward layer by layer. It is the starting point for shortest-path and connectivity problems.

## What to Notice in This Code

- The gap between linear and logarithmic widens dramatically as input grows.
- Stack and queue are simple but fundamental building blocks.
- BFS is the starting point for shortest-path problems.

## Five Common Mistakes

1. **Never writing down complexity for your solutions.**
2. **Forgetting the stack cost of recursion.**
3. **Treating hash tables as a universal solution.**
4. **Mixing graph representations and getting confused.**
5. **Underestimating input size and testing only with tiny cases.**

## Data Structure Selection Is the Language of Problem Interpretation

The most common misconception in this course is "memorize the correct data structure." In reality it is the opposite: first read the operation pattern of the problem, then choose the structure that performs those operations most cheaply. Whether inserts/deletes are frequent, whether random access dominates, whether sorted order must be maintained, whether range queries are common — these factors drive the choice. Once you internalize this perspective, you can predict the time-complexity upper bound before writing any code.

The table below compares common undergraduate-level data structures by operation cost.

| Data Structure | Access | Search | Insert | Delete | Use Case |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | Index access is the priority |
| Linked List | O(n) | O(n) | O(1) (at known position) | O(1) (at known position) | Insert/delete position already given |
| Hash Table | — | Avg O(1) | Avg O(1) | Avg O(1) | Fast key-based lookup needed |
| Binary Search Tree | O(log n) | O(log n) | O(log n) | O(log n) | Maintain sorted order + dynamic updates |
| Heap | — | O(n) | O(log n) | O(log n) | Priority queue, top-k |
| Graph (adjacency list) | — | O(V+E) | O(1)~O(V) | O(1)~O(V) | Connectivity, path problems |

When reading this table, do not look only at Big O — also consider constant factors and implementation complexity. A hash table averages O(1), but real performance varies with collision handling, memory usage, and hash function choice.

## Algorithm Paradigm Comparison

Algorithms are retained better when grouped by paradigm rather than memorized individually.

| Paradigm | Core Question | Representative Problems | Watch Out |
|---|---|---|---|
| Brute Force | Can we check all possibilities? | Subsets, permutations | Explodes without pruning |
| Divide and Conquer | Can the problem be split into smaller identical subproblems? | Merge sort, quicksort | Check merge/combine cost |
| Greedy | Does the local optimum lead to the global optimum? | Interval scheduling, Huffman | Verify exchange argument |
| Dynamic Programming | Can sub-problem solutions be reused? | Knapsack, LIS | State definition is half the battle |
| Graph Search | Does the problem ask about reachability, shortest path, or connectivity? | BFS, DFS, Dijkstra | Keep representation consistent |

Building the habit of picking the paradigm (first column) before implementing cuts solve time. What matters more than coding speed is explaining *why* this paradigm fits.

## Python Implementation Reading Points

When implementing data structures in Python, distinguish between language-provided types and manual implementations. `list` is a dynamic array; for queues use `collections.deque`; for priority queues use `heapq`. During learning, do both: manual implementation builds understanding of internals; standard library usage builds production speed.

Minimum verification loop during practice:

- Per-operation unit tests: push/pop, enqueue/dequeue, insert/search
- Edge-case tests: empty structure, single element, duplicate keys
- Complexity estimation note: best/average/worst case recorded
- Failure classification: wrong data-structure choice vs. implementation bug

Repeating this loop transforms the algorithms course from interview prep into a design-sense course.

## Turning Complexity Into a Practical Habit

To truly internalize complexity, leave a three-line memo with every solution:

1. **Input size upper bound**
2. **Number of critical operations**
3. **Memory usage justification**

With these three lines, you can explain why even a correct solution passed or might time out.

Problem-solving order matters too. Spend the first 10 minutes *not* coding — write only the state definition and data structure choice. For DP problems, the state definition comes before the recurrence. For graph problems, the representation comes before the algorithm. Following this order dramatically reduces debugging time.

The same principle applies in interview preparation: the person who explains selection reasoning structurally earns more trust than the person who merely produces correct output.

## Course Dependency Diagram

Data structures and algorithms sit at the central hub of the CS prerequisite graph. If you stall here, implementation speed in systems, data, and AI courses slows with it.

| Prerequisite Axis | Ability Required in DSA | Where It Reappears Downstream |
|---|---|---|
| Discrete Math | Proofs, recurrences, graph thinking | Algorithm correctness arguments, complexity analysis |
| Programming Fundamentals | Function decomposition, debugging | Systems assignment implementation, SQL optimization |
| Probability/Statistics | Expected value and distribution sense | Randomized algorithms, performance experiment interpretation |

When solving problems, write three lines *before* the code: `input bound`, `key operation`, `data structure choice rationale`. Once this habit sticks, you handle interview-style and assignment-style problems with the same framework.

## How This Shows Up in Production

Most API latency problems start at data structure choice. Repeating full scans, failing to use a better lookup structure, or leaving redundant computations in place — performance issues originate in code structure before server scale.

## How a Senior Engineer Thinks

- Complexity is intuition, not a memorized table.
- Data shape drives the algorithm choice.
- Look at worst-case and average-case together.
- If you can write the invariant, the implementation is more stable.
- Tests are the strongest evidence of correctness.

## Checklist

- [ ] I label time complexity on my solutions.
- [ ] I check input size limits first.
- [ ] I state the invariant my code maintains in one line.
- [ ] I test representative and boundary cases.

## Practice Problems

1. Define *hash table* in one line.
2. Define *graph* in one line.
3. State the meaning of *Big O* in one line.

## Wrap-up and Next Steps

Data structures and algorithms are not a course for a specific exam — they are the common language of problem-solving. Being able to explain how you store data, what procedure you apply, and how cost grows is what raises code quality. Next post: understanding systems subjects.

## Answering the Opening Questions

- **Why are data structures and algorithms the core course for nearly every CS major?**
  - Data structures address how to store and efficiently access data, while algorithms address what sequence of computations to perform on that data. Their combination forms the backbone of practical programming.
- **How do learning data structures and learning algorithms differ, and why must they go together?**
  - Arrays work best for ordered data, hashes for fast lookups, trees for hierarchical structures, and graphs for connection relationships. The goal is building the intuition to automatically identify which data structure fits when you see a problem.
- **What do time complexity and space complexity let you judge in real code?**
  - Notations like O(n log n) sorting, O(1) hash lookup, and O(log n) tree search are not meant to be memorized — the point is understanding why they work that way structurally, and experiencing how much it matters in practice.
<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): Understanding First Year Subjects](./02-first-year-subjects.md)
- **Data Structures and Algorithms (current)**
- Understanding Systems Subjects (upcoming)
- Database and Network (upcoming)
- AI and Data Science (upcoming)
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [CLRS Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Open Data Structures](https://opendatastructures.org/)
- [Visualgo - Algorithm Visualization](https://visualgo.net/en)
- [LeetCode Patterns](https://seanprashad.com/leetcode-patterns/)

Tags: CS, DataStructures, Algorithms, Complexity, Beginner
