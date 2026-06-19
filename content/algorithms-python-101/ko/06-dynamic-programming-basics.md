---
series: algorithms-python-101
episode: 6
title: "Algorithms with Python 101 (6/10): 동적 계획법 기초"
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
  - Dynamic Programming
  - DP
  - Memoization
seo_description: 동적 계획법의 핵심인 메모이제이션과 테뷸레이션의 차이를 파이썬 예제로 배웁니다. 중복 계산을 줄이는 점화식 설계와 공간 최적화 기법을 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (6/10): 동적 계획법 기초

어떤 문제는 같은 부분 문제를 반복해서 풀면 끝없이 느려집니다. 동적 계획법이 중요한 이유는 그 낭비를 재사용 가능한 계산으로 바꿔 주기 때문입니다.

이 글은 Algorithms with Python 101 시리즈의 여섯 번째 글입니다. 여기서는 메모이제이션, 테뷸레이션, 그리고 대표적인 Python 예제로 동적 계획법을 소개합니다.

이 주제는 코딩 테스트와 경쟁 프로그래밍에서 특히 자주 나오지만, 더 중요한 가치는 겹치는 부분 문제와 재사용 가능한 상태를 알아보는 눈을 기르는 데 있습니다.

![Algorithms with Python 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/06/06-01-concept-overview.ko.png)
*Algorithms with Python 101 6장 흐름 개요*

## 이 글에서 다룰 문제

- DP가 적용되는 두 조건은 무엇일까요?
- 메모이제이션을 쓰는 top-down 구현은 어떻게 할까요?
- 테이블을 채우는 bottom-up 구현은 어떻게 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> DP는 부분 문제 결과를 저장해 중복 계산을 피함으로써, 지수 문제를 다항 문제로 바꾸는 기법입니다.

## 개념 한눈에 보기

> DP는 최적 부분 구조와 중복 부분 문제가 함께 있을 때 적용합니다

```text
Fibonacci fib(5) — 순진한 재귀의 중복 계산:
fib(5) → fib(4) + fib(3)
          fib(4) → fib(3) + fib(2)   ← fib(3) 중복!
                    fib(3) → fib(2) + fib(1)

DP 적용 후: 각 fib(n)을 정확히 한 번만 계산
fib(1)=1 → fib(2)=1 → fib(3)=2 → fib(4)=3 → fib(5)=5
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Optimal substructure | 최적해가 부분 문제들의 최적해로 구성됩니다 |
| Overlapping sub-problems | 같은 부분 문제가 반복 계산됩니다 |
| Memoization | 재귀 호출 결과를 캐시하는 top-down 방식입니다 |
| Tabulation | 가장 작은 문제부터 표를 채우는 bottom-up 방식입니다 |
| State transition | 이전 상태로부터 현재 상태를 계산하는 점화식입니다 |

## DP 설계 4단계

DP 문제를 풀 때는 이 순서를 지키면 실수가 줄어듭니다.

```text
1. 상태 정의: dp[i]는 무엇을 의미하는가?
2. 점화식:    dp[i] = f(dp[i-1], dp[i-2], ...)
3. 초기값:    dp[0], dp[1] 등 기저 상태를 설정
4. 답의 위치: dp[n]인가, min(dp[n-1], dp[n-2])인가?
```

## 적용 전후 비교

피보나치 수열을 구하는 두 가지 방식입니다.

```python
# before: naive recursion 방식 — O(2^n)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

```python
# after: DP bottom-up 방식 — O(n)
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

## 단계별 실습

### 단계 1: Top-Down — 메모이제이션

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_top_down(n: int) -> int:
    """Top-down Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fib_top_down(n - 1) + fib_top_down(n - 2)

print(fib_top_down(50))  # 12586269025

# 수동 메모이제이션
def fib_memo(n: int, memo: dict | None = None) -> int:
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

print(fib_memo(50))  # 12586269025
```

top-down 방식은 재귀 사고를 유지하면서도 중복 계산만 제거합니다.

### 단계 2: Bottom-Up — 테이블 채우기

```python
def fib_bottom_up(n: int) -> int:
    """Bottom-up Fibonacci — O(n), O(n) space."""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(fib_bottom_up(50))  # 12586269025

def fib_optimized(n: int) -> int:
    """Space-optimized Fibonacci — O(n), O(1) space."""
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1

print(fib_optimized(50))  # 12586269025
```

이전 값 두 개만 필요하므로 배열 대신 변수 두 개로 공간을 줄일 수 있습니다.

### 단계 3: 계단 오르기 문제

```python
def climb_stairs(n: int) -> int:
    """1칸 또는 2칸씩 오를 때 n계단을 오르는 방법 수."""
    # 상태: dp[i] = i번째 계단에 도달하는 방법 수
    # 점화식: dp[i] = dp[i-1] + dp[i-2]
    # (바로 앞에서 1칸 or 두 칸 앞에서 2칸)
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

for n in range(1, 8):
    print(f"Stairs {n}: {climb_stairs(n)} ways")
# Stairs 1: 1 ways
# Stairs 2: 2 ways
# Stairs 3: 3 ways
# Stairs 4: 5 ways
```

### 단계 4: 최소 동전 교환

```python
def coin_change(coins: list[int], amount: int) -> int:
    """최소 동전 수로 amount를 만들기 — O(amount * len(coins))."""
    # 상태: dp[i] = 금액 i를 만들기 위한 최소 동전 수
    # 점화식: dp[i] = min(dp[i], dp[i - coin] + 1) for each coin
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0  # 0원을 만드는 데 동전 0개

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float("inf") else -1

print(coin_change([1, 5, 10], 13))   # 4 (10+1+1+1)
print(coin_change([1, 5, 10], 30))   # 3 (10+10+10)
print(coin_change([3, 7], 5))        # -1 (불가능)
```

### 단계 5: 0-1 배낭 문제

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """0-1 Knapsack — O(n * capacity)."""
    # 상태: dp[i][c] = 물건 i개를 용량 c 안에 넣을 때 최대 가치
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # 현재 물건 스킵
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)

    return dp[n][capacity]

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
print(knapsack(weights, values, capacity))  # 10
```

## 단계별 실행 추적 — 계단 오르기

`climb_stairs(5)` 테이블 채우기:

```text
상태 정의: dp[i] = i번째 계단에 도달하는 방법 수

초기값:
  dp[1] = 1  (1칸: {1})
  dp[2] = 2  (2칸: {1,1}, {2})

점화식 적용:
  dp[3] = dp[2] + dp[1] = 2 + 1 = 3
    ({1,1,1}, {1,2}, {2,1})

  dp[4] = dp[3] + dp[2] = 3 + 2 = 5

  dp[5] = dp[4] + dp[3] = 5 + 3 = 8

결과: 8가지 방법
```

`coin_change([1, 5, 10], 13)` 추적:

```text
dp = [0, inf, inf, inf, ..., inf]  (길이 14)

동전 1: dp[1]=1, dp[2]=2, dp[3]=3, ...
동전 5: dp[5]=1, dp[6]=2, dp[10]=2, dp[11]=3, dp[12]=4
동전 10: dp[10]=1, dp[11]=2, dp[12]=3, dp[13]=4

dp[13] = min(dp[12]+1, dp[8]+1, dp[3]+1)
       = min(4, -, 4)
       = 4  (10+1+1+1)
```

## 코딩 테스트 풀이 예시

**문제**: 가장 긴 증가 부분 수열(LIS)의 길이를 구하라.

```python
def longest_increasing_subsequence(nums: list[int]) -> int:
    """
    LIS 길이를 O(n^2) DP로 구합니다.
    상태: dp[i] = nums[i]로 끝나는 LIS 길이
    점화식: dp[i] = max(dp[j]+1) for all j < i if nums[j] < nums[i]
    """
    if not nums:
        return 0

    n = len(nums)
    dp = [1] * n  # 자기 자신만으로 길이 1

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)


# 테스트
print(longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18]))  # 4 (2,5,7,101 또는 2,3,7,101)
print(longest_increasing_subsequence([0, 1, 0, 3, 2, 3]))            # 4
print(longest_increasing_subsequence([7, 7, 7, 7]))                   # 1
```

**단계별 추적** (`[10, 9, 2, 5, 3, 7, 101, 18]` 입력):

```text
초기: dp = [1, 1, 1, 1, 1, 1, 1, 1]

i=1 (nums[1]=9):
  j=0: nums[0]=10 > 9 → 갱신 안 함
  dp[1] = 1

i=2 (nums[2]=2):
  j=0: 10 > 2 → 갱신 안 함
  j=1: 9 > 2  → 갱신 안 함
  dp[2] = 1

i=3 (nums[3]=5):
  j=2: nums[2]=2 < 5 → dp[3]=max(1, dp[2]+1)=2
  dp[3] = 2  (수열: 2,5)

i=4 (nums[4]=3):
  j=2: 2 < 3 → dp[4]=max(1,2)=2
  dp[4] = 2  (수열: 2,3)

i=5 (nums[5]=7):
  j=2: 2<7 → dp[5]=2
  j=3: 5<7 → dp[5]=max(2,3)=3
  j=4: 3<7 → dp[5]=max(3,3)=3
  dp[5] = 3  (수열: 2,5,7 또는 2,3,7)

i=6 (nums[6]=101):
  모든 이전 값보다 크므로 dp[6]=dp[5]+1=4

결과: max(dp) = 4
```

**문제**: 2×n 직사각형을 1×2 타일로 채우는 방법 수.

```python
def tile_ways(n: int) -> int:
    """
    2×n 직사각형을 1×2 타일로 채우는 방법 수.
    점화식: dp[i] = dp[i-1] + dp[i-2]
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    dp = [0] * (n + 1)
    dp[1] = 1   # 세로 1개
    dp[2] = 2   # 세로 2개 or 가로 2개
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


for n in range(1, 7):
    print(f"2×{n}: {tile_ways(n)}가지")
# 2×1: 1가지, 2×2: 2가지, 2×3: 3가지, 2×4: 5가지, ...
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 점화식 없이 바로 코딩함 | 구조가 없어 논리 오류가 납니다 | 상태/점화식/초기값을 먼저 종이에 씁니다 |
| 기저 상태를 빠뜨림 | `dp[0]` 등이 초기화되지 않아 답이 틀립니다 | 가장 작은 문제를 먼저 정의합니다 |
| 테이블 크기를 잘못 잡음 | 인덱스 범위를 벗어납니다 | 보통 `n+1` 크기를 할당합니다 |
| 큰 입력에 top-down만 고집 | 재귀 깊이 제한에 걸릴 수 있습니다 | 필요하면 bottom-up으로 전환합니다 |
| 불필요한 2차원 테이블 사용 | 메모리를 낭비합니다 | 이전 행만 필요하면 1차원으로 줄입니다 |

## 복잡도 비교표

| 접근 | 시간 | 공간 | 특징 |
|------|------|------|------|
| 순진 재귀 | 지수 | 호출 스택 | 중복 계산 심함 |
| 메모이제이션 | `O(n)` 또는 상태 수 기반 | 캐시 + 스택 | 필요한 상태만 계산 |
| 테뷸레이션 | `O(n)` 또는 상태 수 기반 | 테이블 | 구현 안정적 |
| 롤링 변수 | 동일 | `O(1)` | 이전 상태 적을 때 유리 |

## 실무에서는 이렇게 연결됩니다

- 경로 최적화는 최소 비용 계산에 DP를 활용할 수 있습니다.
- 편집 거리 계산은 맞춤법 검사기와 diff 도구의 기반입니다.
- NLP의 Viterbi 알고리즘도 DP 기반 시퀀스 디코딩입니다.
- 금융 포트폴리오 최적화도 DP 문제로 모델링할 수 있습니다.
- 게임 AI는 최적 전략 탐색에 DP적 사고를 사용합니다.

## 현업에서는 이렇게 생각합니다

실무에서 DP를 매번 처음부터 구현하지는 않더라도, DP적 사고는 매우 중요합니다. "이 계산을 캐시할 수 있을까?", "이 문제는 최적 부분 구조를 가지는가?" 같은 질문이 성능 개선의 출발점이 되기 때문입니다.

코딩 테스트에서는 점화식을 먼저 정의하고 bottom-up으로 구현하는 편이 안정적입니다. top-down은 직관적이지만 스택 오버플로우 위험이 있습니다.

## 운영 체크리스트

- [ ] DP를 적용할 수 있는 두 조건을 설명할 수 있습니다
- [ ] top-down과 bottom-up 방식을 비교할 수 있습니다
- [ ] 점화식을 정의하고 DP 테이블을 채울 수 있습니다
- [ ] DP 해답에 공간 최적화를 적용할 수 있습니다
- [ ] 계단 오르기와 거스름돈 문제를 풀 수 있습니다

## 연습 문제

1. 1×2 타일로 2×n 직사각형을 채우는 방법 수를 구해 보세요.
2. DP로 가장 긴 증가 부분 수열(LIS)의 길이를 구해 보세요.
3. 동전 거스름돈 해답에서 실제 사용한 동전까지 출력하도록 확장해 보세요.

## 정리와 다음 글

동적 계획법은 중복 계산을 없애 지수 문제를 다항 문제로 바꾸는 강력한 도구입니다. 핵심은 항상 점화식을 정의하는 데 있습니다. 다음 글에서는 BFS와 DFS로 그래프를 탐색하는 방법을 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- **Algorithms with Python 101 (6/10): 동적 계획법 기초 (현재 글)**
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Dynamic Programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Real Python — Memoization with Python](https://realpython.com/lru-cache-python/)
- [GeeksforGeeks — Dynamic Programming](https://www.geeksforgeeks.org/dynamic-programming/)
- [LeetCode — Dynamic Programming Problems](https://leetcode.com/tag/dynamic-programming/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/06-dynamic-programming-basics)

Tags: Python, Algorithms, Dynamic Programming, DP, Memoization
