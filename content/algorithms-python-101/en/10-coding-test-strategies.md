---
series: algorithms-python-101
episode: 10
title: "Algorithms with Python 101 (10/10): Coding Test Problem-Solving Strategies"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Algorithms
  - Coding Test
  - Problem Solving
  - Interview
seo_description: Learn systematic strategies for coding tests — from analyzing input size to choosing algorithms, with Python patterns and practical tips.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (10/10): Coding Test Problem-Solving Strategies

This is the final post in the Algorithms with Python 101 series. Knowing algorithms is not the same as applying them under time pressure, and in a coding test the real challenge is reading constraints quickly and mapping the problem to the right pattern before you get lost in implementation.

This chapter connects the earlier posts through one continuous flow: read constraints first, reject the wrong complexity first, then carry the problem all the way through implementation and verification. A repeatable approach matters because it saves time, reduces avoidable mistakes, and helps you recover even when the problem is unfamiliar.


![Algorithms with Python 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/10/10-01-big-picture.en.png)
*Algorithms with Python 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Coding Test Problem-Solving Strategies?
- Which signal should the example or diagram make visible for Coding Test Problem-Solving Strategies?
- What failure should be prevented first when Coding Test Problem-Solving Strategies reaches a real system?

## What You Will Learn

- How to reject the wrong algorithm from constraints alone
- How to map problem types to algorithms
- How to carry one problem through understand → plan → implement → verify
- Common patterns and Python coding tips for timed tests

## Why It Matters

Even if you have studied every algorithm in this series, it means nothing if you cannot decide which one to use when facing a real problem. The core skill is classifying the problem type quickly and reasoning backward from constraints to determine the required time complexity.

> Problem-Solving Flow = Analyze Input → Classify Type → Choose Algorithm → Implement → Verify

A coding test is an exam where you write correct code within a time limit. A systematic approach saves time and reduces mistakes.

## Concept Overview

> Reverse-engineer the allowed time complexity from input size

```text
Allowed time complexity by input size N (1-second limit):
N ≤ 10        → O(N!)       — brute force / permutations
N ≤ 20        → O(2^N)      — bitmask, backtracking
N ≤ 500       → O(N³)       — Floyd-Warshall
N ≤ 5,000     → O(N²)       — DP, nested loops
N ≤ 1,000,000 → O(N log N)  — sorting, binary search
N ≤ 10^8      → O(N)        — linear scan, two pointers
```

## Key Concepts

| Term | Description |
|------|-------------|
| Brute force | Explores every possible case — the most basic approach |
| Two pointers | Moves two pointers inward to solve in O(N) |
| Sliding window | Slides a fixed-size window to compute subarray sums and similar |
| Backtracking | Explores possibilities and backtracks when a condition fails |
| Edge case | Boundary conditions such as empty input, maximum, or minimum values |

## Before / After

Comparing problem-solving approaches.

```python
# before: start coding immediately — risk of picking the wrong algorithm
def solve(data):
    # jump into nested loops without thinking → time limit exceeded
    for i in range(len(data)):
        for j in range(len(data)):
            pass  # O(N²) — exceeds time limit when N is 1,000,000
```

```python
# after: analyze input size first, then choose the algorithm
def solve(data):
    # N=1,000,000 → need O(N) or O(N log N)
    # approach with sorting + two pointers
    data.sort()  # O(N log N)
    left, right = 0, len(data) - 1
    # ... O(N) scan
```

## Hands-On Steps

### Step 1: Read the constraints before touching the code

```python
problem = {
    "name": "Two Sum to Target",
    "input": "integer array nums, integer target",
    "goal": "return the indices of two numbers whose sum equals target, or None",
    "constraints": {
        "n_max": 200_000,
        "time_limit_seconds": 1,
        "values": "negative values and duplicates are allowed",
    },
}

print(problem)
```

When `N = 200,000`, an O(N²) double loop is disqualified immediately. A 1-second limit means you should reject billions of comparisons before writing a single implementation detail.

### Step 2: Reject the wrong approach on purpose

```python
def wrong_two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
```

This code can still be correct on small input, which is exactly why coding tests are tricky. The important habit is not merely saying "this is slow" but deciding "this is invalid under the stated constraints."

### Step 3: Classify the problem and choose the target complexity

| Question | Answer for this problem | Meaning |
|------|--------------------------|---------|
| Is the array already sorted? | No | Sorting may be part of the plan |
| Are we combining two values to hit a target? | Yes | Two pointers is a strong candidate |
| Must we inspect every pair explicitly? | No | Brute force is unnecessary |
| What complexity do we need? | `O(N log N)` or better | Sort + linear scan fits |

This is not DP and not a graph problem. There is no state transition to optimize and no node/edge structure to traverse. The strongest signal is "two values + target sum + sortable input," which points to sorting plus two pointers.

### Step 4: Implement sorting + two pointers

```python
def solve_two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    indexed = sorted((value, index) for index, value in enumerate(nums))
    left, right = 0, len(indexed) - 1

    while left < right:
        current = indexed[left][0] + indexed[right][0]
        if current == target:
            i, j = indexed[left][1], indexed[right][1]
            return tuple(sorted((i, j)))
        if current < target:
            left += 1
        else:
            right -= 1

    return None

sample_nums = [7, 1, 11, 2, 9]
sample_target = 10
sample_answer = solve_two_sum(sample_nums, sample_target)

print(sample_answer)
assert sample_answer == (0, 3)
```

Three implementation details matter here.

1. We sort `(value, original_index)` pairs so that we do not lose the required output format.
2. When the sum is too small, we move the left pointer rightward; when it is too large, we move the right pointer leftward.
3. We normalize the answer with `tuple(sorted((i, j)))` so the output order stays predictable.

If even the sample fails, inspect whether you lost the original indices during sorting before anything else.

### Step 5: Close the loop with edge-case verification

```python
verification_cases = [
    {
        "name": "sample",
        "nums": [7, 1, 11, 2, 9],
        "target": 10,
        "expected": (0, 3),
        "inspect_first": "check whether original indices were preserved after sorting",
    },
    {
        "name": "no_solution",
        "nums": [1, 4, 8],
        "target": 20,
        "expected": None,
        "inspect_first": "check the while left < right termination path and the final None return",
    },
    {
        "name": "duplicates",
        "nums": [3, 3, 4, 5],
        "target": 6,
        "expected": (0, 1),
        "inspect_first": "check that duplicates are allowed and that left < right prevents reusing one element twice",
    },
    {
        "name": "negative_values",
        "nums": [-5, -1, 2, 8],
        "target": 3,
        "expected": (0, 3),
        "inspect_first": "check whether the pointer-movement rule still follows sum comparison with negative values",
    },
    {
        "name": "minimal_input",
        "nums": [42],
        "target": 42,
        "expected": None,
        "inspect_first": "check that the while loop exits immediately when fewer than two elements exist",
    },
]

for case in verification_cases:
    actual = solve_two_sum(case["nums"], case["target"])
    print(f"{case['name']:>14} | expected={case['expected']} | actual={actual}")
    assert actual == case["expected"], (
        f"{case['name']} failed. Inspect first: {case['inspect_first']}"
    )
```

The purpose of this loop is not just to add more tests. It is to make failure diagnosis faster.

- If a no-solution case returns something anyway, inspect termination logic first.
- If the duplicates case fails, inspect whether you accidentally reused the same element or mishandled equal values.
- If negative values fail, re-check pointer movement in terms of sum comparison rather than intuition about sign.
- If minimal input crashes, inspect boundary handling before the main algorithm.

### Step 6: Essential Python Tips for Coding Tests

```python
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations, permutations
import heapq

# 1. Fast input
input = sys.stdin.readline

# 2. defaultdict — automatic key initialization
graph: dict[int, list[int]] = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
print(dict(graph))  # {1: [2, 3]}

# 3. Counter — frequency counting
text = "hello world"
freq = Counter(text)
print(freq.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# 4. heapq — priority queue
heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(heap, x)
print(heapq.heappop(heap))  # 1

# 5. Combinations and permutations
print(list(combinations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,3)]
print(list(permutations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,1), ...]

# 6. Infinity
INF = float("inf")
print(min(INF, 42))  # 42

# 7. 2D array initialization
rows, cols = 3, 4
grid = [[0] * cols for _ in range(rows)]  # correct
# wrong = [[0] * cols] * rows  # bug: all rows reference the same list
```

## What to Notice in This Code

- Reverse-engineering time complexity from input size is the starting point for algorithm selection
- Two pointers are the key pattern here because sorting turns an impossible O(N²) search into an O(N log N) workflow
- After implementation, the safest verification order is sample → no solution → duplicates → negative values → minimal input
- Python standard library tools like defaultdict, Counter, and heapq save significant implementation time
- The `[[0]*n]*m` 2D array initialization bug is extremely common

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Not checking input size | Algorithm with wrong complexity causes time limit exceeded | Check the range of N first and eliminate invalid approaches early |
| Ignoring edge cases | Empty input or N=1 causes runtime errors | Handle boundary conditions first |
| Coding before classifying the problem | You drift toward DP, graph, or brute force without evidence | Write down sorted/unsorted state, target operation, and allowed complexity first |
| Losing original indices after sorting | Values are correct but the answer format is wrong | Sort `(value, index)` pairs instead of raw values |
| Submitting without diagnostic tests | Trivial bugs survive to submission | Test examples and edge cases, and decide what to inspect first for each failure class |

## Real-World Applications

- Coding interviews evaluate algorithm problem-solving ability
- Performance optimization often requires improving O(N²) to O(N log N)
- Data pipeline design relies on choosing the right processing algorithm for large datasets
- API response time optimization depends on algorithm selection
- System design interviews require complexity analysis skills

## How Senior Engineers Think About This

The essence of a coding test is "choosing the right algorithm and implementing it correctly within a time limit." Solving many problems matters, but building the habit of reading constraints first and rejecting the wrong complexity early is even more effective.

The same mindset applies in production work. "Is this algorithm fast enough for this data size?" is a fundamental question in system design.

## Why this matters beyond interviews

- Production incidents often start with the same mistake as a failed coding test: choosing an algorithm that does not match the input scale.
- Constraint-first thinking transfers directly to batch jobs, API latency budgets, and memory-sensitive data pipelines.
- A reusable problem-solving checklist is valuable because it reduces debugging time even when the task is not presented as an “algorithm problem.”

## Checklist

- [ ] I can reverse-engineer allowed time complexity from input size
- [ ] I can classify a problem as search, DP, graph, or greedy
- [ ] I can reject a wrong O(N²) approach before implementing a two-pointers solution
- [ ] I can leverage Python standard library for fast implementation
- [ ] I can systematically test edge cases and know what to inspect first when one fails

## Exercises

1. Find all unique triplets in an integer array that sum to zero (remove duplicates).
2. Find the longest palindromic substring in a given string.
3. Find the minimum-cost path from (0,0) to (N-1,N-1) in an N×N grid.

## Summary and Next Steps

The most important skill in coding tests is identifying the problem type quickly and discarding the approaches that cannot possibly meet the constraints. Once you internalize the full flow — input size → time complexity → algorithm choice → implementation → verification — you can approach unfamiliar problems systematically. The search, sorting, recursion, DP, graph, and greedy techniques in this series form the toolkit, but the final level of reliability comes from the verification loop.

## Answering the Opening Questions

- **How do you use input-size constraints to eliminate algorithms early?**
  - First reverse-engineer the allowable complexity from the maximum input size and time limit, then immediately discard approaches that are slower. In the article's `N = 200,000` example, ruling out `O(N²)` double loops like `wrong_two_sum()` before implementing was the key judgment.
- **How do you connect problem types to algorithms?**
  - Ask whether it involves arrays, graphs, state storage, or post-sort two-pointer narrowing—these questions quickly link problem types to approaches. The article classified Two Sum as a sort + two-pointer problem and traced from `(value, original_index)` pair sorting to `solve_two_sum()`.
- **How do you carry a problem through understand, plan, implement, and verify?**
  - In the understand phase, read constraints and goals; in plan, set target complexity and data structures; after implementation, close the verification loop with sample, no-solution, duplicate, negative, and minimum-input cases. `verification_cases` and `defaultdict`, `Counter`, `heapq` examples turned problem-solving from a one-time hunch into a reproducible procedure.
<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): Dynamic Programming Basics](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): Graph Traversal — BFS and DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): Shortest Path Basics](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): Greedy Algorithms](./09-greedy-algorithms.md)
- **Coding Test Problem-Solving Strategies (current)**

<!-- toc:end -->

## References

### Language and library references

- [Python Documentation — collections](https://docs.python.org/3/library/collections.html)
- [Python Documentation — heapq](https://docs.python.org/3/library/heapq.html)
- [Python Documentation — itertools](https://docs.python.org/3/library/itertools.html)

### Practice sets

- [Baekjoon Online Judge — Step-by-Step Problems](https://www.acmicpc.net/step)
- [Programmers — Coding Test Practice](https://programmers.co.kr/learn/challenges)

Tags: Python, Algorithms, Coding Test, Problem Solving, Interview
