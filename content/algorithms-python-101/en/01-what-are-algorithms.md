---
series: algorithms-python-101
episode: 1
title: "Algorithms with Python 101 (1/10): What Are Algorithms?"
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
  - Problem Solving
  - Programming Basics
  - Time Complexity
seo_description: Learn what algorithms are, why they matter, and write your first algorithm in Python with hands-on examples.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (1/10): What Are Algorithms?

Programming is ultimately about solving problems. Two pieces of code can produce the same answer and still behave very differently once the input gets large. That difference usually starts with the algorithm.

Algorithms matter well beyond coding interviews. They shape performance tuning, data processing, and the way you reason about trade-offs in real systems.

This is the first post in the Algorithms with Python 101 series. Here, we'll define what an algorithm is, look at its core properties, and write a simple Python example.


![Algorithms with Python 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/01/01-01-big-picture.en.png)
*Algorithms with Python 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Are Algorithms??
- Which signal should the example or diagram make visible for What Are Algorithms??
- What failure should be prevented first when What Are Algorithms? reaches a real system?

## What You Will Learn

- The definition and five key properties of algorithms
- How to represent algorithms with pseudocode
- How to implement simple algorithms in Python
- The difference between correctness and efficiency

## Why It Matters

Programming is problem solving. For the same problem, one algorithm can be thousands of times faster than another. Understanding algorithms lets you write faster, more correct code.

> An algorithm is a clear, finite set of steps that takes input and produces the desired output.

Algorithmic thinking is a core skill across coding interviews, performance optimization, and system design.

## Concept Overview

> Algorithm = a finite procedure that transforms input into the desired output

```text
[Problem] → [Algorithm] → [Solution]

Example: Find the maximum value in a list
Input:  [3, 7, 2, 9, 4]
Algorithm:
  1. Set the first value as the maximum
  2. Compare each remaining value
  3. Update maximum when a larger value is found
Output: 9
```

## Key Concepts

| Term | Description |
|------|-------------|
| Algorithm | A clear, finite set of steps to solve a problem |
| Input | The data provided to an algorithm |
| Output | The result produced by an algorithm |
| Correctness | The property of producing the right output for every valid input |
| Efficiency | How sparingly an algorithm uses time and memory |

## Before / After

Two approaches to finding the maximum value in a list.

```python
# before: sort the list then take the last element — O(n log n)
data = [3, 7, 2, 9, 4]
sorted_data = sorted(data)
maximum = sorted_data[-1]
```

```python
# after: single pass through the list — O(n)
data = [3, 7, 2, 9, 4]
maximum = data[0]
for x in data[1:]:
    if x > maximum:
        maximum = x
```

## Hands-On Steps

### Step 1: Find the Maximum Value

```python
def find_max(numbers: list[int]) -> int:
    """Find the maximum value in a list."""
    if not numbers:
        raise ValueError("Cannot find maximum of an empty list")
    maximum = numbers[0]
    for num in numbers[1:]:
        if num > maximum:
            maximum = num
    return maximum

data = [3, 7, 2, 9, 4]
print(f"Maximum: {find_max(data)}")  # Maximum: 9
```

### Step 2: Compute Basic Statistics

```python
def compute_stats(numbers: list[int]) -> dict:
    """Compute sum, average, min, and max of a list."""
    if not numbers:
        raise ValueError("Empty list")
    total = 0
    minimum = numbers[0]
    maximum = numbers[0]
    for num in numbers:
        total += num
        if num < minimum:
            minimum = num
        if num > maximum:
            maximum = num
    return {
        "sum": total,
        "average": total / len(numbers),
        "min": minimum,
        "max": maximum,
    }

stats = compute_stats([10, 20, 30, 40, 50])
print(stats)
# {'sum': 150, 'average': 30.0, 'min': 10, 'max': 50}
```

### Step 3: Reverse a String

```python
def reverse_string(text: str) -> str:
    """Reverse a string without slicing."""
    result = []
    for i in range(len(text) - 1, -1, -1):
        result.append(text[i])
    return "".join(result)

print(reverse_string("algorithm"))  # mhtirogla
print(reverse_string("Python"))    # nohtyP

# Compare with Python built-in
print("algorithm"[::-1])  # mhtirogla
```

### Step 4: Compare Two Algorithms

```python
import time

def has_duplicate_brute(data: list[int]) -> bool:
    """Check for duplicates — brute force O(n^2)."""
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                return True
    return False

def has_duplicate_set(data: list[int]) -> bool:
    """Check for duplicates — set-based O(n)."""
    return len(data) != len(set(data))

test_data = list(range(10_000))

start = time.perf_counter()
has_duplicate_brute(test_data)
brute_time = time.perf_counter() - start

start = time.perf_counter()
has_duplicate_set(test_data)
set_time = time.perf_counter() - start

print(f"Brute force: {brute_time:.4f}s")
print(f"Set-based:   {set_time:.6f}s")
```

### Step 5: Verify the Five Properties

```python
def is_palindrome(text: str) -> bool:
    """Check whether a string is a palindrome.

    Demonstrates the five properties of an algorithm:
    1. Input: string text
    2. Output: True or False
    3. Definiteness: every step is unambiguous
    4. Finiteness: the loop runs at most len(text)/2 times
    5. Effectiveness: uses only basic comparisons
    """
    cleaned = text.lower().replace(" ", "")
    left = 0
    right = len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

## What to Notice in This Code

- The same problem can have vastly different performance depending on the algorithm (O(n^2) vs O(n))
- An algorithm has five properties: input, output, definiteness, finiteness, and effectiveness
- Python built-in functions like `max` and `sorted` are algorithms — implementing them manually helps you understand the principles
- Handling edge cases (empty list, empty string) is a hallmark of a well-designed algorithm

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Skipping edge cases | Crashes on empty input | Always validate input first |
| Infinite loops | Missing or wrong termination condition | Verify loop variable converges to exit |
| Off-by-one errors | Index off by 1 | Test boundary values carefully |
| Choosing an inefficient algorithm | Runtime explodes with larger data | Analyze time complexity first |
| Not verifying correctness | Works for some inputs but not all | Test with diverse cases |

## Real-World Applications

- Search engines return results from billions of pages in milliseconds
- Recommendation systems analyze user preferences to suggest content
- Navigation apps compute optimal routes in real time
- Compression algorithms reduce file sizes to save storage
- Encryption algorithms protect data in transit and at rest

## How Senior Engineers Think About This

In day-to-day work, you rarely implement algorithms from scratch. Libraries and frameworks provide optimized implementations. But algorithmic thinking is essential for analyzing problems and choosing the right tool.

Answering "Why is this code slow?" or "Is there a better approach?" requires a solid grasp of algorithm fundamentals.

## What this changes in production code reviews

- When input size grows, the first question is usually not “Can this code be cleaner?” but “What algorithm is hidden underneath this loop?”
- Replacing a sort-plus-scan with a single pass or a repeated scan with a set lookup often matters more than micro-optimizing syntax.
- Edge-case handling is part of algorithm quality. Empty input, duplicated values, and invalid states are where production bugs surface first.

## Checklist

- [ ] Explain the definition and five properties of an algorithm
- [ ] Compare the efficiency of two algorithms that solve the same problem
- [ ] Implement simple algorithms (find max, palindrome check) in Python
- [ ] Write algorithms that handle edge cases
- [ ] Measure the performance difference between brute force and optimized approaches

## Exercises

1. Write an algorithm that finds the second-largest value in a list in a single pass.
2. Write an algorithm that finds the most frequent character in a string.
3. Implement three ways to compute the sum from 1 to N (loop, math formula, recursion) and compare their performance.

## Summary and Next Steps

An algorithm is a clear procedure for solving a problem, and efficiency is the key criterion for choosing one. In the next article, we cover the tool for objectively measuring efficiency: time complexity and Big-O notation.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Are Algorithms??**
  - The article treats What Are Algorithms? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Are Algorithms??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Are Algorithms? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Are Algorithms? (current)**
- Time Complexity and Big-O (upcoming)
- Linear Search and Binary Search (upcoming)
- Sorting Algorithms (upcoming)
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming Basics (upcoming)
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Introduction to Algorithms (CLRS) — MIT Press](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Real Python — Sorting Algorithms in Python](https://realpython.com/sorting-algorithms-python/)
- [GeeksforGeeks — Fundamentals of Algorithms](https://www.geeksforgeeks.org/fundamentals-of-algorithms/)
- [Khan Academy — Algorithms](https://www.khanacademy.org/computing/computer-science/algorithms)

Tags: Python, Algorithms, Problem Solving, Programming Basics, Time Complexity
