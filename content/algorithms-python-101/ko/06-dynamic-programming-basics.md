---
series: algorithms-python-101
episode: 6
title: 동적 계획법 기초
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

# 동적 계획법 기초

어떤 문제는 같은 부분 문제를 반복해서 풀면 끝없이 느려집니다. 동적 계획법이 중요한 이유는 그 낭비를 재사용 가능한 계산으로 바꿔 주기 때문입니다.

이 글은 Algorithms with Python 101 시리즈의 여섯 번째 글입니다. 여기서는 메모이제이션, 테뷸레이션, 그리고 대표적인 Python 예제로 동적 계획법을 소개합니다.

이 주제는 코딩 테스트와 경쟁 프로그래밍에서 특히 자주 나오지만, 더 중요한 가치는 겹치는 부분 문제와 재사용 가능한 상태를 알아보는 눈을 기르는 데 있습니다.

## 이 글에서 다룰 문제

- DP가 적용되는 두 조건은 무엇일까요?
- 메모이제이션을 쓰는 top-down 구현은 어떻게 할까요?
- 테이블을 채우는 bottom-up 구현은 어떻게 할까요?
- 피보나치, 계단 오르기, 동전 거스름돈, 배낭 문제는 어떤 전형을 보여 줄까요?

## 왜 중요한가

재귀만으로는 지수 시간이 걸릴 수 있습니다. DP는 부분 문제 결과를 저장해 그 비용을 다항 시간으로 줄입니다. 대표적으로 순진한 재귀 피보나치는 `O(2^n)`이지만, DP를 적용하면 `O(n)`이 됩니다.

> DP는 부분 문제 결과를 저장해 중복 계산을 피함으로써, 지수 문제를 다항 문제로 바꾸는 기법입니다.

동적 계획법은 코딩 테스트에서 가장 자주 나오는 범주 가운데 하나입니다. 패턴을 익혀 두면 최적화 문제를 더 체계적으로 풀 수 있습니다.

## 개념 한눈에 보기

> DP는 최적 부분 구조와 중복 부분 문제가 함께 있을 때 적용합니다

```text
Fibonacci fib(5) — redundant computation in naive recursion:
fib(5) → fib(4) + fib(3)
          fib(4) → fib(3) + fib(2)   ← fib(3) repeated
                    fib(3) → fib(2) + fib(1)  ← fib(2) repeated

After DP: each fib(n) computed only once
fib(1)=1 → fib(2)=1 → fib(3)=2 → fib(4)=3 → fib(5)=5
```

![순진한 재귀와 DP 상태 재사용 비교](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/06/06-01-concept-overview.ko.png)

*순진한 재귀는 같은 상태를 여러 번 계산하지만, DP는 상태를 한 번 채운 뒤 재사용합니다.*

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Optimal substructure | 최적해가 부분 문제들의 최적해로 구성됩니다 |
| Overlapping sub-problems | 같은 부분 문제가 반복 계산됩니다 |
| Memoization | 재귀 호출 결과를 캐시하는 top-down 방식입니다 |
| Tabulation | 가장 작은 문제부터 표를 채우는 bottom-up 방식입니다 |
| State transition | 이전 상태로부터 현재 상태를 계산하는 점화식입니다 |

## Before / After

피보나치 수열을 구하는 두 가지 방식입니다.

```python
# before: naive recursion — O(2^n)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

```python
# after: DP bottom-up — O(n)
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

### Step 1: Top-Down — Memoization

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fib_top_down(n: int) -> int:
    """Top-down Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fib_top_down(n - 1) + fib_top_down(n - 2)

print(fib_top_down(50))  # 12586269025

# Manual memoization
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

top-down 방식은 재귀 사고를 유지하면서도 중복 계산만 제거해 줍니다. 직관적으로 문제를 풀기 쉬운 대신, 입력이 아주 크면 재귀 깊이 제한을 고려해야 합니다.

### Step 2: Bottom-Up — Tabulation

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

bottom-up 방식은 작은 부분 문제부터 표를 차례대로 채웁니다. 필요한 이전 상태가 제한적이면 배열 대신 변수 몇 개로 공간까지 줄일 수 있습니다.

### Step 3: Stair Climbing Problem

```python
def climb_stairs(n: int) -> int:
    """Number of ways to climb n stairs taking 1 or 2 steps at a time."""
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# Recurrence: dp[i] = dp[i-1] + dp[i-2]
for n in range(1, 8):
    print(f"Stairs {n}: {climb_stairs(n)} ways")
# Stairs 1: 1 ways
# Stairs 2: 2 ways
# Stairs 3: 3 ways
# Stairs 4: 5 ways
# Stairs 5: 8 ways
# Stairs 6: 13 ways
# Stairs 7: 21 ways
```

계단 오르기는 DP의 전형적인 입문 문제입니다. 현재 상태가 직전 두 상태만으로 결정된다는 점을 통해 점화식의 감각을 잡을 수 있습니다.

### Step 4: Minimum Coin Change

```python
def coin_change(coins: list[int], amount: int) -> int:
    """Minimum coins to make amount — O(amount * len(coins))."""
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float("inf") else -1

print(coin_change([1, 5, 10], 13))   # 4 (10+1+1+1)
print(coin_change([1, 5, 10], 30))   # 3 (10+10+10)
print(coin_change([3, 7], 5))        # -1 (impossible)
```

거스름돈 문제는 "현재 금액을 만들기 위한 최소 동전 수"라는 상태를 세우는 연습에 좋습니다. 불가능한 경우를 `inf`로 표현하는 방식도 자주 쓰입니다.

### Step 5: 0-1 Knapsack

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """0-1 Knapsack — O(n * capacity)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # skip current item
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)

    return dp[n][capacity]

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
print(knapsack(weights, values, capacity))  # 10
```

배낭 문제는 DP 표가 왜 필요한지를 잘 보여 줍니다. 물건 개수와 남은 용량이라는 두 축을 동시에 관리해야 하기 때문입니다.

## 이 코드에서 먼저 봐야 할 점

- top-down은 필요한 부분 문제만 계산하고, bottom-up은 가능한 부분 문제를 순서대로 모두 채웁니다.
- 이전 값 몇 개만 필요하다면 배열 전체를 두 변수로 줄여 공간 최적화를 할 수 있습니다.
- DP의 핵심은 점화식입니다. 현재 상태가 이전 상태들로 어떻게 결정되는지 먼저 써야 합니다.
- 배낭 문제의 2차원 표는 "물건 수 × 용량"의 모든 조합을 기록합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 점화식 없이 바로 코딩함 | 구조가 없어 논리 오류가 납니다 | 먼저 점화식을 씁니다 |
| 기저 상태를 빠뜨림 | `dp[0]` 등이 초기화되지 않아 답이 틀립니다 | 가장 작은 문제를 먼저 정의합니다 |
| 테이블 크기를 잘못 잡음 | 인덱스 범위를 벗어납니다 | 보통 `n+1` 크기를 할당합니다 |
| 큰 입력에 top-down만 고집 | 재귀 깊이 제한에 걸릴 수 있습니다 | 필요하면 bottom-up으로 전환합니다 |
| 불필요한 2차원 테이블 사용 | 메모리를 낭비합니다 | 이전 행만 필요하면 1차원으로 줄입니다 |

## 실무에서는 이렇게 연결됩니다

- 경로 최적화는 최소 비용 계산에 DP를 활용할 수 있습니다.
- 편집 거리 계산은 맞춤법 검사기와 diff 도구의 기반입니다.
- NLP의 Viterbi 알고리즘도 DP 기반 시퀀스 디코딩입니다.
- 금융 포트폴리오 최적화도 DP 문제로 모델링할 수 있습니다.
- 게임 AI는 최적 전략 탐색에 DP적 사고를 사용합니다.

## 현업에서는 이렇게 생각합니다

실무에서 DP를 매번 처음부터 구현하지는 않더라도, DP적 사고는 매우 중요합니다. "이 계산을 캐시할 수 있을까?", "이 문제는 최적 부분 구조를 가지는가?" 같은 질문이 성능 개선의 출발점이 되기 때문입니다.

코딩 테스트에서는 점화식을 먼저 정의하고 bottom-up으로 구현하는 편이 안정적입니다. top-down은 직관적이지만 스택 오버플로우 위험이 있습니다.

## DP로 볼지 먼저 판단하는 기준

- 같은 계산이 로그, 요청, 상태 조합마다 반복된다면 캐시나 DP 관점에서 다시 볼 가치가 있습니다.
- 현재 결정이 이전 몇 개 상태만 보면 정해진다면, 테이블이나 롤링 변수로 줄일 수 있는지 확인하는 편이 좋습니다.
- 반대로 상태 차원이 너무 크거나 입력이 실시간 스트림처럼 계속 바뀐다면, DP보다 그리디·휴리스틱·근사 해법이 운영 비용에 더 맞을 수 있습니다.
- 구현 전에 상태 정의, 점화식, 초기값을 표로 먼저 적어 두면 테스트 실패 지점을 훨씬 빨리 좁힐 수 있습니다.

## 체크리스트

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
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- **동적 계획법 기초 (현재 글)**
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Dynamic Programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Real Python — Memoization with Python](https://realpython.com/lru-cache-python/)
- [GeeksforGeeks — Dynamic Programming](https://www.geeksforgeeks.org/dynamic-programming/)
- [LeetCode — Dynamic Programming Problems](https://leetcode.com/tag/dynamic-programming/)

Tags: Python, Algorithms, Dynamic Programming, DP, Memoization
