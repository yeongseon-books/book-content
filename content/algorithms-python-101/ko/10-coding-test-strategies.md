---
series: algorithms-python-101
episode: 10
title: 코딩 테스트 문제 접근법
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Coding Test
  - Problem Solving
  - Interview
seo_description: 코딩 테스트 문제 해결을 위한 체계적 전략을 세웁니다. 투 포인터, 슬라이딩 윈도우 등 핵심 패턴과 파이썬 라이브러리 활용 팁을 배웁니다.
last_reviewed: '2026-05-12'
---

# 코딩 테스트 문제 접근법

알고리즘을 안다는 것과 시간 제한 안에서 적용하는 것은 다른 문제입니다. 코딩 테스트의 진짜 난점은 구현 전에 제약을 빠르게 읽고, 문제를 적절한 패턴에 연결하는 데 있습니다. 이 글은 Algorithms with Python 101 시리즈의 마지막 글입니다. 여기서는 앞선 글의 내용을 실제 문제 풀이 흐름으로 연결해 보겠습니다.

반복 가능한 접근법이 중요한 이유는 시간을 아끼고, 불필요한 실수를 줄이고, 처음 보는 문제에서도 다시 복구할 수 있게 해 주기 때문입니다.

## 이 글에서 다룰 문제

- 문제 유형을 알고리즘에 어떻게 연결할까요?
- 입력 크기 제약을 보고 어떤 알고리즘을 골라야 할까요?
- 문제를 푸는 네 단계 프레임워크는 무엇일까요?
- 제한 시간 안에 도움 되는 Python 패턴은 어떤 것들이 있을까요?

## 왜 중요한가

이 시리즈의 알고리즘을 모두 공부했더라도, 실제 문제 앞에서 무엇을 써야 할지 결정하지 못하면 소용이 없습니다. 핵심은 문제 유형을 빠르게 분류하고, 입력 제약에서 거꾸로 필요한 시간 복잡도를 추론하는 능력입니다.

> Problem-Solving Flow = Analyze Input → Classify Type → Choose Algorithm → Implement → Verify

코딩 테스트는 제한 시간 안에 정확한 코드를 작성하는 시험입니다. 체계적인 접근은 시간을 줄이고 실수를 줄여 줍니다.

## 개념 한눈에 보기

> 입력 크기에서 허용 가능한 시간 복잡도를 역산합니다

```text
Allowed time complexity by input size N (1-second limit):
N ≤ 10        → O(N!)       — brute force / permutations
N ≤ 20        → O(2^N)      — bitmask, backtracking
N ≤ 500       → O(N³)       — Floyd-Warshall
N ≤ 5,000     → O(N²)       — DP, nested loops
N ≤ 1,000,000 → O(N log N)  — sorting, binary search
N ≤ 10^8      → O(N)        — linear scan, two pointers
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Brute force | 가능한 모든 경우를 시도하는 가장 기본적인 접근입니다 |
| Two pointers | 두 포인터를 움직여 `O(N)`에 푸는 패턴입니다 |
| Sliding window | 일정 구간을 밀며 부분 배열 합 등을 계산하는 패턴입니다 |
| Backtracking | 조건이 맞지 않으면 되돌아가며 경우를 탐색합니다 |
| Edge case | 빈 입력, 최소값, 최대값처럼 경계 조건입니다 |

## Before / After

문제 접근 방식의 차이를 비교해 보겠습니다.

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

## 단계별 실습

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

이 네 단계는 문제를 빨리 푸는 요령이 아니라, 틀리지 않기 위한 절차입니다. 특히 `Understand`와 `Plan`을 건너뛰면 구현이 빨라도 방향이 틀릴 가능성이 큽니다.

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

정렬된 배열에서 `O(N^2)`을 `O(N)`으로 줄일 때 가장 먼저 떠올려야 하는 패턴이 두 포인터입니다.

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

부분 배열, 부분 문자열, 연속 구간 문제에서 슬라이딩 윈도우는 거의 기본 패턴입니다. 매번 구간을 새로 계산하지 않고 이전 상태를 재활용한다는 점이 핵심입니다.

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

문제를 읽고 바로 코드로 들어가기보다, 어떤 범주인지 먼저 분류하면 선택지가 급격히 줄어듭니다. 이 분류 습관이 시간을 가장 많이 절약해 줍니다.

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

코딩 테스트에서는 알고리즘 아이디어만큼 구현 속도도 중요합니다. 표준 라이브러리 활용과 흔한 함정 회피만으로도 큰 차이가 납니다.

## 이 코드에서 먼저 봐야 할 점

- 입력 크기에서 허용 시간 복잡도를 역산하는 것이 알고리즘 선택의 출발점입니다.
- 두 포인터와 슬라이딩 윈도우는 `O(N^2)`를 `O(N)`으로 줄일 때 핵심 패턴입니다.
- `defaultdict`, `Counter`, `heapq` 같은 표준 라이브러리는 구현 시간을 크게 줄여 줍니다.
- `[[0]*n]*m` 2차원 배열 초기화 버그는 매우 흔하므로 반드시 구분해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 입력 크기를 확인하지 않음 | 잘못된 복잡도의 알고리즘을 골라 시간 초과가 납니다 | 먼저 `N` 범위를 봅니다 |
| 경계 조건을 무시함 | 빈 입력이나 `N=1`에서 런타임 오류가 납니다 | 경계 조건을 먼저 처리합니다 |
| 브루트포스 없이 바로 최적화 | 기준선이 없어 방향을 잃기 쉽습니다 | 브루트포스로 시작한 뒤 최적화합니다 |
| 의사코드 없이 바로 구현 | 논리 오류를 늦게 발견합니다 | 먼저 간단한 설계나 의사코드를 씁니다 |
| 테스트 없이 제출 | 사소한 버그를 놓칩니다 | 예제와 엣지 케이스를 모두 확인합니다 |

## 실무에서는 이렇게 연결됩니다

- 코딩 면접은 알고리즘 문제 해결 능력을 평가합니다.
- 성능 최적화는 종종 `O(N^2)`를 `O(N log N)`으로 낮추는 일에서 시작합니다.
- 데이터 파이프라인 설계도 입력 크기에 맞는 처리 알고리즘 선택이 중요합니다.
- API 응답 시간 최적화 역시 알고리즘 선택과 밀접합니다.
- 시스템 설계 면접에서도 복잡도 분석 능력은 기본입니다.

## 현업에서는 이렇게 생각합니다

코딩 테스트의 본질은 "올바른 알고리즘을 고르고, 시간 안에 정확히 구현하는 것"입니다. 많은 문제를 푸는 것도 중요하지만, 접근을 체계화하는 편이 더 큰 효과를 냅니다.

이 사고방식은 실무에도 그대로 이어집니다. "이 데이터 크기에서 이 알고리즘이 충분히 빠른가?"라는 질문은 시스템 설계의 기본이기 때문입니다.

## 체크리스트

- [ ] 입력 크기에서 허용 시간 복잡도를 역산할 수 있습니다
- [ ] 문제를 탐색, DP, 그래프, 그리디 등으로 분류할 수 있습니다
- [ ] 두 포인터와 슬라이딩 윈도우 패턴을 적용할 수 있습니다
- [ ] Python 표준 라이브러리로 빠르게 구현할 수 있습니다
- [ ] 엣지 케이스를 체계적으로 테스트할 수 있습니다

## 연습 문제

1. 정수 배열에서 합이 0이 되는 서로 다른 세 수 조합을 모두 찾아 보세요.
2. 문자열에서 가장 긴 팰린드롬 부분 문자열을 찾아 보세요.
3. `N×N` 격자에서 `(0,0)`부터 `(N-1,N-1)`까지의 최소 비용 경로를 구해 보세요.

## 정리와 마무리

코딩 테스트에서 가장 중요한 능력은 문제 유형을 빠르게 알아보는 것입니다. 입력 크기, 시간 복잡도, 알고리즘 선택으로 이어지는 흐름이 몸에 익으면 처음 보는 문제도 체계적으로 접근할 수 있습니다. 이 시리즈에서 다룬 탐색, 정렬, 재귀, DP, 그래프, 그리디는 코딩 테스트의 핵심 도구 상자입니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법 기초](./06-dynamic-programming-basics.md)
- [그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [최단 경로 기초](./08-shortest-path-basics.md)
- [그리디 알고리즘](./09-greedy-algorithms.md)
- **코딩 테스트 문제 접근법 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [LeetCode — Top Interview Questions](https://leetcode.com/problem-list/top-interview-questions/)
- [Baekjoon Online Judge — Step-by-Step Problems](https://www.acmicpc.net/step)
- [Programmers — Coding Test Practice](https://programmers.co.kr/learn/challenges)
- [Real Python — Python Practice Problems](https://realpython.com/python-practice-problems/)

Tags: Python, Algorithms, Coding Test, Problem Solving, Interview
