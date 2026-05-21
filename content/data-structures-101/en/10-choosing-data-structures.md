---
series: data-structures-101
episode: 10
title: "Data Structures 101 (10/10): Choosing Data Structures"
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
  - Data Structures
  - Decision Making
  - Time Complexity
  - Workload
  - Design
seo_description: A closing guide to choosing data structures with a decision tree, workload analysis, and the most common bad picks plus their fixes.
last_reviewed: '2026-05-04'
---

# Data Structures 101 (10/10): Choosing Data Structures

> Data Structures 101 series (10/10)

**Core question**: You've now studied nine data structures. When you face a brand-new problem, what should come to mind first?

> Choosing a data structure is decided by "which operations happen most often", not by "what kind of data you store". Even with the same user records, frequent lookups want a hash table; frequent sorted iteration wants a BST; frequent push and pop at both ends wants a deque; frequent priority access wants a heap. This closing article wraps up the series with how to analyse workloads, a decision tree, and the bad picks you'll encounter most often in real projects.

This is the final post in the Data Structures 101 series.


![data structures 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/10/10-01-big-picture.en.png)
*data structures 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Choosing Data Structures?
- Which signal should the example or diagram make visible for Choosing Data Structures?
- What failure should be prevented first when Choosing Data Structures reaches a real system?

## What You Will Learn

- The five core questions that define a workload
- A decision tree for choosing a data structure
- A side-by-side time-complexity comparison
- The most common bad picks and how to correct them

## Why It Matters

Algorithms run on top of data structures, so the data structure you pick sets the upper bound on system performance. A bad choice is hard to recover from with algorithmic optimisation alone. But picking a data structure without analysing the workload is just as risky. "What I know" or "the theoretically fastest one" is not always the right answer.

> Choosing a data structure = workload analysis + understanding trade-offs + measurement.

> A good choice starts not from "the shape of the data" but from "the frequency and pattern of operations". You first define which operations are on the hot path, how big the input is, and what the memory constraints are.

```text
                "Which operation dominates?"
                       │
        ┌──────────────┼──────────────┐
       Search        Insert/Delete   Iterate
        │                │              │
   ┌────┴───┐       ┌────┴────┐    ┌────┴────┐
  by key?  by range? both ends? arbitrary?  in order?  sorted?
   │       │       │        │         │        │
  dict    BST    deque   linked    list/array  BST
                                              /sorted
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Workload | The kinds of operations the system actually performs and their frequency |
| Hot path | The most frequently executed code path |
| Big-O | The upper bound on growth as input size increases |
| Amortized | The average cost of an operation across many calls |
| Cache locality | An access pattern that fits well into the CPU cache |

## Before / After

**Before — "let's just use a dict":**

```python
# Sequence matters, but a dict is used anyway
events = {}
events["e1"] = 1; events["e2"] = 2; events["e3"] = 3
# Priority handling now means sorting on every access — slow
```

**After — analyse the workload, then use a heap:**

```python
import heapq
events = []
heapq.heappush(events, (1, "e1"))
heapq.heappush(events, (2, "e2"))
# Pop the highest-priority item in O(log n) every time
```

## Hands-On: Step by Step

### Step 1: Define the workload with five questions

```python
# Five questions to answer before you pick a data structure
workload_questions = [
    "1. Which operation happens most frequently?",
    "2. How large is the input? (tens, tens of thousands, billions?)",
    "3. Does the data need order or sorting?",
    "4. What are the memory constraints?",
    "5. Are there concurrency or persistence requirements?",
]
for q in workload_questions:
    print(q)
```

Once you answer these five, the candidate set usually narrows down to one or two.

### Step 2: Time-complexity table per data structure

```python
table = {
    "list (Python)":          {"index": "O(1)",     "search": "O(n)",     "append": "O(1)*", "prepend": "O(n)"},
    "deque":                  {"index": "O(n)",     "search": "O(n)",     "append": "O(1)",  "prepend": "O(1)"},
    "linked list":            {"index": "O(n)",     "search": "O(n)",     "append": "O(1)",  "prepend": "O(1)"},
    "dict / set":             {"index": "—",        "search": "O(1)*",   "insert": "O(1)*",  "sorted iter": "O(n log n)"},
    "balanced BST (Sorted)":  {"index": "O(log n)", "search": "O(log n)", "insert": "O(log n)", "sorted iter": "O(n)"},
    "heap":                   {"index": "—",        "min": "O(1)",        "insert": "O(log n)", "arbitrary search": "O(n)"},
    "graph (adj list)":       {"neighbors": "O(deg)", "edge exists": "O(deg)", "BFS/DFS": "O(V+E)"},
}

for ds, ops in table.items():
    print(f"{ds:<25} {ops}")
```

Look up which structure is fast for the hot-path operation. `*` denotes amortised.

### Step 3: Encode the decision tree as code

```python
def recommend_structure(workload):
    """Take a workload dict and return a recommended structure."""
    primary = workload["primary_op"]
    needs_order = workload.get("ordered", False)

    if primary == "key_lookup":
        return "dict / set" if not needs_order else "SortedDict"
    if primary == "min_or_max":
        return "heap (heapq)"
    if primary == "both_ends":
        return "deque"
    if primary == "range_query":
        return "BST / sorted array (with bisect)"
    if primary == "graph_traversal":
        return "Graph (adjacency list) + BFS/DFS"
    if primary == "ordered_iteration":
        return "list / array"
    return "list (default)"

print(recommend_structure({"primary_op": "key_lookup"}))     # dict / set
print(recommend_structure({"primary_op": "min_or_max"}))      # heap
print(recommend_structure({"primary_op": "both_ends"}))       # deque
```

Once you express the workload explicitly, choosing a data structure becomes almost mechanical.

### Step 4: Measure the cost of a bad choice

```python
import time
from collections import deque

# Wrong choice: a list as a queue
def queue_with_list(n):
    q = []
    for i in range(n):
        q.append(i)
    while q:
        q.pop(0)

# Right choice: a deque as a queue
def queue_with_deque(n):
    q = deque()
    for i in range(n):
        q.append(i)
    while q:
        q.popleft()

N = 50_000

start = time.perf_counter()
queue_with_list(N)
print(f"list:  {(time.perf_counter() - start) * 1000:.0f} ms")

start = time.perf_counter()
queue_with_deque(N)
print(f"deque: {(time.perf_counter() - start) * 1000:.0f} ms")
```

Same behaviour; the timing differs by 100x or more. Ignore Big-O analysis and you pay for it quantitatively.

### Step 5: Real-world catalogue

```python
cases = [
    ("LRU cache",            "dict + doubly linked list",      "O(1) get/put"),
    ("Task scheduler",       "heap (priority queue)",          "O(log n) for next task"),
    ("Live friend suggestions", "graph + BFS (k-hop)",          "O(V + E)"),
    ("Autocomplete",         "trie (prefix tree)",             "O(prefix length)"),
    ("API request dedup",    "set",                            "O(1) check"),
    ("DB index",             "B+Tree (generalised balanced BST)", "O(log n) sorted lookup"),
    ("undo / redo",          "two stacks",                     "O(1) push/pop"),
    ("Event-driven simulation", "heap (event queue)",          "O(log n) next event"),
]
for use_case, ds, complexity in cases:
    print(f"  {use_case:<25} → {ds:<35} ({complexity})")
```

Real systems are usually built from a *combination* of structures rather than a single one. The trick is to analyse each component's workload separately.

## Notable Points

- Choice of data structure must start from workload analysis
- Even for the same ADT, the right implementation depends on the input pattern
- The cost of a bad choice shows up exactly where Big-O says it should
- Real-world systems combine multiple data structures rather than rely on one

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| "dict for everything" | Inefficient when you need sorted iteration or priority access | Match the structure to the workload |
| Deciding on Big-O alone | Ignoring constants and cache locality | Verify with measurements |
| Premature optimisation | Adopting a complex structure that becomes a maintenance burden | Start simple, replace after measurement |
| Avoiding libraries | Reimplementing what is already battle-tested | Reach for the standard or well-known library first |
| Asking one structure to do everything | Trying to make every operation fast on one structure | Combine structures (e.g., dict + linked list) |

## How This Is Used in Practice

- Databases: index types (B+Tree, Hash, GIN, GiST) are picked by workload
- Caching systems: TTL/LRU/LFU policies use different structural combinations
- Search engines: an inverted index is a hash table plus sorted postings lists
- Recommendation systems: a user-item graph plus dense embeddings
- Stream processing: sliding windows use a deque; top-k uses a min-heap

## How a Senior Engineer Thinks

A senior engineer "starts from the basics". They build the first version with list and dict, then measure, and only swap in a more sophisticated structure when a bottleneck appears. Premature optimisation is the enemy at the data-structure level too.

A senior also knows that "the limit of the data structure is the limit of the system". You cannot recover from a bad core data structure with algorithmic tweaks or infrastructure scaling. So they take time at the design phase to choose the data structure that holds the core data, and they accept up front that changing it later will be hard.

Finally, a senior treats "data structure = domain model". A well-chosen structure improves readability and maintainability too. The right structure makes algorithms shorter and clearer.

## Checklist

- [ ] Can you answer the five workload-defining questions
- [ ] Have you mapped each hot-path operation to its complexity in the chosen structure
- [ ] Have you considered cache locality, memory, and implementation complexity beyond Big-O
- [ ] Do you start with the standard library and replace only after measuring
- [ ] Do you understand that real systems combine multiple data structures

## Practice Problems

1. Pick a piece of code you wrote recently. List every data structure it uses and analyse the hot-path operations on each one. Was there a better-fit structure available?

2. Implement an LRU cache two ways: (a) using `OrderedDict`, (b) using a dict plus a doubly linked list of your own. Compare the time and code complexity of each.

3. Design a system that takes one million events per second and (a) keeps the most recent ten thousand, (b) keeps only the top one hundred by priority, (c) supports fast count-by-category queries. Which combination of structures fits each requirement?

## Wrap-Up and Next Steps

Choosing a data structure is the final gate of computer-science fundamentals and a decision you make every day in real projects. Start from "frequency and pattern of operations", not "shape of data", and weigh cache locality, memory, and implementation complexity alongside Big-O. Do not ask one structure to do everything; combine them based on the workload — that's the practical approach.

The nine data structures covered in this series — array, linked list, stack, queue, hash table, tree, BST, heap, graph — are the vocabulary of nearly every algorithm and system design. The next series covers algorithms: sorting, searching, dynamic programming, and graph algorithms — what you build on top of these structures.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Choosing Data Structures?**
  - The article treats Choosing Data Structures as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Choosing Data Structures?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Choosing Data Structures reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): Linked Lists](./03-linked-lists.md)
- [Data Structures 101 (4/10): Stacks and Queues](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): Hash Tables](./05-hash-tables.md)
- [Data Structures 101 (6/10): Trees](./06-trees.md)
- [Data Structures 101 (7/10): Binary Search Trees](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): Heaps](./08-heaps.md)
- [Data Structures 101 (9/10): Graphs](./09-graphs.md)
- **Choosing Data Structures (current)**

<!-- toc:end -->

## References

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)
- [System Design Primer — Data Structures](https://github.com/donnemartin/system-design-primer)

Tags: Computer Science, Data Structures, Decision Making, Time Complexity, Workload, Design
