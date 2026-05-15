---
series: algorithms-python-101
episode: 10
title: Coding Test Problem-Solving Strategies
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

# Coding Test Problem-Solving Strategies

Knowing algorithms is not the same as applying them under time pressure. In a coding test, the real challenge is reading constraints quickly and mapping the problem to the right pattern before you get lost in implementation.

A repeatable approach matters because it saves time, reduces avoidable mistakes, and helps you recover even when the problem is unfamiliar.

This is the final post in the Algorithms with Python 101 series. Here, we'll connect the ideas from earlier posts into a practical framework for analyzing and solving coding test problems.

## What You Will Learn

- How to map problem types to algorithms
- How to choose algorithms based on input size constraints
- A systematic four-step problem-solving framework
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

### Step 1: The Four-Step Framework

```python
"""
Four steps for solving any problem:

1. Understand
   - Check input/output format
   - Check constraints (range of N, time limit)
   - Trace through examples by hand

2. Plan
   - Reverse-engineer allowed complexity from input size
   - Classify the problem type (search, sort, DP, graph, etc.)
   - Outline the key idea

3. Implement
   - Write pseudocode first
   - Implement one step at a time, verifying intermediate results
   - Handle edge cases

4. Verify
   - Test with provided examples
   - Test edge cases: empty input, minimum, maximum, duplicates
   - Re-check time complexity
"""
```

### Step 2: Two Pointers Pattern

```python
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int] | None:
    """Find two numbers in a sorted array that sum to target — O(N)"""
    left, right = 0, len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return (left, right)
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return None

nums = [1, 2, 4, 6, 8, 10]
print(two_sum_sorted(nums, 10))  # (1, 4) → 2+8=10


def remove_duplicates(nums: list[int]) -> int:
    """Remove duplicates from a sorted array in place — O(N)"""
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write

nums = [1, 1, 2, 2, 3, 4, 4, 5]
k = remove_duplicates(nums)
print(nums[:k])  # [1, 2, 3, 4, 5]
```

### Step 3: Sliding Window Pattern

```python
def max_subarray_sum(nums: list[int], k: int) -> int:
    """Maximum sum of a contiguous subarray of length k — O(N)"""
    if len(nums) < k:
        return 0

    window_sum = sum(nums[:k])
    max_sum = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum

nums = [2, 1, 5, 1, 3, 2]
print(max_subarray_sum(nums, 3))  # 9 (5+1+3)


def longest_unique_substring(s: str) -> int:
    """Longest substring without repeating characters — O(N)"""
    char_index: dict[str, int] = {}
    max_len = 0
    left = 0

    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len

print(longest_unique_substring("abcabcbb"))  # 3 ("abc")
print(longest_unique_substring("pwwkew"))    # 3 ("wke")
```

### Step 4: Problem Type Identification Checklist

```python
"""
Problem type identification checklist:

[Search / Sort]
- "Find ~" + sorted data → binary search
- "Sort ~" → sorted() or custom comparator
- "k-th largest/smallest" → sorting or heapq.nlargest

[DP]
- "Find minimum/maximum" + "number of ways" → DP
- "Number of ways to ~" → DP
- Recurrence relation visible → DP

[Graph]
- "Is it connected?" → BFS/DFS
- "Shortest path" + unweighted → BFS
- "Shortest path" + weighted → Dijkstra
- "Cycle detection" → DFS

[Greedy]
- "Minimum/maximum of ~" + solvable by sorting → greedy
- Each choice does not affect future choices → greedy

[String]
- "Substring" → sliding window or two pointers
- "Pattern matching" → KMP or regex
"""
```

### Step 5: Essential Python Tips for Coding Tests

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
- Two pointers and sliding window are the key patterns for reducing O(N²) to O(N)
- Python standard library tools like defaultdict, Counter, and heapq save significant implementation time
- The `[[0]*n]*m` 2D array initialization bug is extremely common

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Not checking input size | Algorithm with wrong complexity causes time limit exceeded | Check the range of N first |
| Ignoring edge cases | Empty input or N=1 causes runtime errors | Handle boundary conditions first |
| Not starting with brute force | No baseline to optimize from | Start brute force → then optimize |
| Coding without pseudocode | Logic errors discovered too late | Write pseudocode first |
| Submitting without testing | Misses trivial bugs | Test all examples and edge cases |

## Real-World Applications

- Coding interviews evaluate algorithm problem-solving ability
- Performance optimization often requires improving O(N²) to O(N log N)
- Data pipeline design relies on choosing the right processing algorithm for large datasets
- API response time optimization depends on algorithm selection
- System design interviews require complexity analysis skills

## How Senior Engineers Think About This

The essence of a coding test is "choosing the right algorithm and implementing it correctly within a time limit." Solving many problems matters, but systematizing your approach is far more effective.

The same mindset applies in production work. "Is this algorithm fast enough for this data size?" is a fundamental question in system design.

## Checklist

- [ ] I can reverse-engineer allowed time complexity from input size
- [ ] I can classify a problem as search, DP, graph, or greedy
- [ ] I can apply two pointers and sliding window patterns
- [ ] I can leverage Python standard library for fast implementation
- [ ] I can systematically test edge cases

## Exercises

1. Find all unique triplets in an integer array that sum to zero (remove duplicates).
2. Find the longest palindromic substring in a given string.
3. Find the minimum-cost path from (0,0) to (N-1,N-1) in an N×N grid.

## Summary and Next Steps

The most important skill in coding tests is identifying the problem type at a glance. Once you internalize the flow — input size → time complexity → algorithm choice — you can approach any problem systematically. The search, sorting, recursion, DP, graph, and greedy techniques covered in this series form the core toolkit for coding tests.

<!-- toc:begin -->
- [What Are Algorithms?](./01-what-are-algorithms.md)
- [Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- [Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Dynamic Programming Basics](./06-dynamic-programming-basics.md)
- [Graph Traversal — BFS and DFS](./07-graph-traversal-bfs-dfs.md)
- [Shortest Path Basics](./08-shortest-path-basics.md)
- [Greedy Algorithms](./09-greedy-algorithms.md)
- **Coding Test Problem-Solving Strategies (current)**
<!-- toc:end -->

## References

- [LeetCode — Top Interview Questions](https://leetcode.com/problem-list/top-interview-questions/)
- [Baekjoon Online Judge — Step-by-Step Problems](https://www.acmicpc.net/step)
- [Programmers — Coding Test Practice](https://programmers.co.kr/learn/challenges)
- [Real Python — Python Practice Problems](https://realpython.com/python-practice-problems/)

Tags: Python, Algorithms, Coding Test, Problem Solving, Interview
