---
series: algorithms-101
episode: 10
title: Algorithm Problem-Solving Strategies
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
  - Algorithms
  - Problem Solving
  - Pattern Recognition
  - Interviews
  - Practice
seo_description: A five-step procedure for algorithm problems — recognise patterns, pick tools, verify, code. What skill means in interviews and production.
last_reviewed: '2026-05-04'
---

# Algorithm Problem-Solving Strategies

**Core question**: Does being good at algorithms mean memorising lots of solutions, or having a thinking procedure that decomposes new problems?

Solving algorithm problems is a game of pattern recognition and tool selection. The sorting, searching, recursion, DP, greedy, graph, and string topics in this series form a toolbox, but the real leverage comes from the procedure you use to choose among them.

This is the final post in the Algorithms 101 series. Here we wrap up the series with a practical thinking procedure for reading constraints, choosing tools, and verifying an approach before coding.

## What You Will Learn

- The standard thinking procedure to apply to any algorithm problem
- How to estimate an upper bound on time complexity from the input size
- Pattern recognition: which signals call for which tool
- What it really means to be good at algorithms in interviews and in production

## Why It Matters

The point of studying algorithms is not memorising solutions but gaining the ability to decompose new problems. That matters in interviews and just as much in production system design. Two engineers with the same toolbox produce very different work depending on how they pick from it.

> A good solution is the product of a consistent procedure, not a memorised answer.

## Concept at a Glance

> The standard procedure has five steps. (1) Restate the problem. (2) Write down inputs, outputs, and constraints. (3) Estimate the allowed complexity from input size. (4) Recognise the pattern and narrow the candidate tools. (5) Verify on a small example before writing code. The same procedure works in interviews.

```text
Input size -> allowed complexity (rough upper bound)
    n <= 10            : backtracking, every subset (2^n)
    n <= 20            : bitmask DP (2^n)
    n <= 100..500      : up to O(n^3) (Floyd-Warshall, 3D DP)
    n <= 5,000         : O(n^2)
    n <= 10^5..10^6    : O(n log n)
    n >= 10^7          : O(n) or O(log n)
```

## Key Terms

| Term | Description |
| --- | --- |
| Restatement | Re-write the problem in your own words |
| Allowed complexity | Bound estimated from time limit and input size |
| Pattern recognition | Recall a tool from input structure |
| Small-example verification | Trace by hand before coding |
| Sanity test | Edge, empty, and maximum-input checks |

## Before / After

**Before — coding the moment you see the problem:**

```text
"Hmm, I think this is BFS."
-> code -> works -> some cases fail -> debugging spiral
```

**After — the five-step procedure:**

```text
1) Restate the problem
2) Write down inputs/outputs/constraints
3) Estimate allowed complexity from n
4) Use pattern recognition to narrow tool candidates
5) Verify on a small example, then code
```

## Hands-On: Step by Step

### Step 1: Restate the problem in your own words

```text
Original: "Given an array, find the maximum sum of a contiguous subarray."

Restated: Among all contiguous segments of an integer array, find the one with the largest sum.
Edges: Is the answer for an empty array 0, or undefined?
If all values are negative, is the answer the largest single value, or 0?
```

Re-writing the prompt in your own words removes half the bugs before you ever code.

### Step 2: Estimate allowed complexity from input size

```text
n = 10^6, time limit 1 second
-> O(n^2) is out; you need O(n log n) or O(n)
-> Strong hint: "this problem wants a linear or near-linear algorithm"
```

Input size is almost always the strongest cue for narrowing algorithm candidates.

### Step 3: A pattern-recognition signal table

```python
signals = {
    "search in a sorted array":          "binary search",
    "nearest / largest / smallest":      "sort or heap",
    "range sum / min / max":             "prefix sum or segment tree",
    "contiguous subarray":               "two pointers or sliding window",
    "overlapping subproblems":           "DP",
    "shortest path, non-negative":       "Dijkstra",
    "topological order / dependencies":  "topological sort",
    "prefix matters":                    "trie",
    "pattern matching, large text":      "KMP / Aho-Corasick",
    "optimum + greedy plausible":        "try an exchange argument",
}
for k, v in signals.items():
    print(f"- {k:36s} -> {v}")
```

Memorising this mapping gives you an index that fires immediately when a new problem arrives.

### Step 4: Verify on a small example by hand

```text
Problem: maximum contiguous subarray sum (Kadane's algorithm)

Hand trace
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
cur, best = 0, -inf
i=0  cur = max(-2, -2)        = -2,  best = -2
i=1  cur = max(1, -2+1)       = 1,   best = 1
i=2  cur = max(-3, 1-3)       = -2,  best = 1
i=3  cur = max(4, -2+4)       = 4,   best = 4
i=4  cur = max(-1, 4-1)       = 3,   best = 4
i=5  cur = max(2, 3+2)        = 5,   best = 5
i=6  cur = max(1, 5+1)        = 6,   best = 6
i=7  cur = max(-5, 6-5)       = 1,   best = 6
i=8  cur = max(4, 1+4)        = 5,   best = 6
Answer: 6
```

After tracing once by hand, coding becomes close to transcription.

### Step 5: Translate to code and test the edges

```python
def max_subarray(arr):
    if not arr:
        return 0
    cur = best = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([-1]) == -1
assert max_subarray([1]) == 1
assert max_subarray([]) == 0
```

Always check four edges beyond the core case: empty input, single element, all negative, all positive.

## Notable Points

- The five-step procedure applies uniformly to every problem
- Estimating allowed complexity from n is the single strongest cue
- The pattern-recognition mapping acts as a mental index
- A solution traced once by hand is the most trustworthy

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Coding before reading fully | Wrong solution | Restate in your own words |
| Skipping complexity estimation | Time limit exceeded | Bound it from n first |
| Heuristics without pattern recognition | Wandering | Use the signal-to-tool mapping |
| Ignoring edge cases | Sporadic failures | Always check empty / single / extremes |
| Relying purely on memorised solutions | Weak on novel problems | Decompose with the procedure |

## How This Is Used in Practice

- System design: input size narrows data-structure choice first
- Performance tuning: analyse bottlenecks through algorithmic complexity
- Code review: validate someone else's solution against the procedure
- Interviews: candidates are evaluated on procedural consistency
- Learning: decompose a new problem with the procedure to grow the toolbox

## How a Senior Engineer Thinks

A senior engineer does not start typing on contact with a new problem. They read the size and structure, narrow tool candidates from the toolbox, verify on a small example, and only then touch the keyboard. The same procedure applies in production decisions, not just interviews.

A senior engineer also does not measure themselves by the number of solutions they have memorised. The real definition of skill is the confidence that you can stably decompose a problem you have never seen — through the procedure. Growing the toolbox helps, but consistency of the procedure is what matters.

## Checklist

- [ ] Have you memorised the five-step procedure?
- [ ] Do you estimate allowed complexity from input size?
- [ ] Do you carry the signal-to-tool mapping in your head?
- [ ] Do you check edge cases automatically?
- [ ] Can you decompose a new problem with the same procedure?

## Practice Problems

1. Build a single table summarising the algorithm tools from this series. For each tool list the average and worst complexity, the applicability signals, and the limits in one line. The table itself is a powerful learning artifact.

2. Pick one external algorithm problem, write the five-step procedure as prose, then implement the solution. Note which step felt hardest.

3. Spend five minutes explaining to a colleague (or to yourself) "what signals make me reach for graph algorithms?" If you can explain it, you own that tool.

## Wrap-Up and Next Steps

The essence of studying algorithms is not the volume of solutions but the consistency of the procedure. Estimating complexity from input size, narrowing tools from signals, verifying on small examples, and translating to code — that five-step loop works the same in interviews and in production.

This concludes the Algorithms 101 series. Natural next steps include advanced data structures (tree/heap/hash variants), advanced graphs (flows, matching, SCC), or domain applications (search engines, recommender systems, compilers). The thinking procedure you built here transfers directly to all of them.

<!-- toc:begin -->
- [What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Time and Space Complexity](./02-time-and-space-complexity.md)
- [Search Algorithms](./03-search-algorithms.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- [Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Dynamic Programming](./06-dynamic-programming.md)
- [Greedy Algorithms](./07-greedy-algorithms.md)
- [Graph Algorithms](./08-graph-algorithms.md)
- [String Algorithm Basics](./09-string-algorithms.md)
- **Algorithm Problem-Solving Strategies (current)**
<!-- toc:end -->

## References

- [Competitive Programmer's Handbook (Antti Laaksonen)](https://cses.fi/book/book.pdf)
- [LeetCode — Patterns and study plans](https://leetcode.com/explore/)
- [CLRS — Introduction to Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)

Tags: Computer Science, Algorithms, Problem Solving, Pattern Recognition, Interviews, Practice
