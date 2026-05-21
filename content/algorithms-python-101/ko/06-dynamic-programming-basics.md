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

## 먼저 던지는 질문

- DP가 적용되는 두 조건은 무엇일까요?
- 메모이제이션을 쓰는 top-down 구현은 어떻게 할까요?
- 테이블을 채우는 bottom-up 구현은 어떻게 할까요?

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

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Optimal substructure | 최적해가 부분 문제들의 최적해로 구성됩니다 |
| Overlapping sub-problems | 같은 부분 문제가 반복 계산됩니다 |
| Memoization | 재귀 호출 결과를 캐시하는 top-down 방식입니다 |
| Tabulation | 가장 작은 문제부터 표를 채우는 bottom-up 방식입니다 |
| State transition | 이전 상태로부터 현재 상태를 계산하는 점화식입니다 |

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

bottom-up 방식은 작은 부분 문제부터 표를 차례대로 채웁니다. 필요한 이전 상태가 제한적이면 배열 대신 변수 몇 개로 공간까지 줄일 수 있습니다.

### 단계 3: 계단 오르기 문제
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

# 점화식: dp[i] = dp[i-1] + dp[i-2]
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

### 단계 4: 최소 동전 교환
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

### 단계 5: 0-1 배낭 문제
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

## 심화 실전 노트: DP를 점화식-표-검증 루프로 고정하기

### 구현 앵커: 상태 정의를 코드 주석으로 명시

```python
def min_cost_climb(cost: list[int]) -> int:
    # state: dp[i] = i번째 계단에 도달하는 최소 비용
    n = len(cost)
    if n == 0:
        return 0
    if n == 1:
        return cost[0]

    dp = [0] * n
    dp[0], dp[1] = cost[0], cost[1]
    for i in range(2, n):
        dp[i] = min(dp[i - 1], dp[i - 2]) + cost[i]
    return min(dp[-1], dp[-2])
```

상태 정의를 코드에 남기면, 나중에 식을 바꿀 때도 의도를 잃지 않습니다.

### 테이블 추적 예시

```text
cost = [10, 15, 20, 1]
dp[0]=10
 dp[1]=15
 dp[2]=min(15,10)+20=30
 dp[3]=min(30,15)+1=16
정답=min(dp[3],dp[2])=16
```

### 복잡도 비교표

| 접근 | 시간 | 공간 | 특징 |
|------|------|------|------|
| 순진 재귀 | 지수 | 호출 스택 | 중복 계산 심함 |
| 메모이제이션 | `O(n)` 또는 상태 수 기반 | 캐시 + 스택 | 필요한 상태만 계산 |
| 테뷸레이션 | `O(n)` 또는 상태 수 기반 | 테이블 | 구현 안정적 |
| 롤링 변수 | 동일 | `O(1)` 또는 축소 | 이전 상태 적을 때 유리 |

### 인터뷰형 분해 질문

- 상태를 한 줄로 정의할 수 있는가
- 점화식에서 참조하는 이전 상태가 무엇인가
- 초기값은 어떤 입력에서 결정되는가
- 답이 테이블의 어느 칸인가

### 증명 스케치: 피보나치 DP

`dp[i]=dp[i-1]+dp[i-2]`에서 각 `i`는 정확히 한 번 계산됩니다. 각 계산은 상수 시간 연산이므로 총 시간은 `O(n)`입니다. `dp[i-1], dp[i-2]`만 사용하면 공간은 `O(1)`까지 줄일 수 있습니다.

### 실수-수정 페어

| 실수 | 결과 | 수정 |
|------|------|------|
| 점화식보다 코드 먼저 작성 | 논리 흔들림 | 상태/식/초기값 순서 고정 |
| `inf` 초기화 누락 | 최소값 비교 실패 | 도달 불가 상태를 명시적으로 초기화 |
| 2차원 표가 필요 없는데 유지 | 메모리 낭비 | 이전 행만 쓰면 1차원으로 축소 |

## 실전 검증 부록: 성능 측정과 반례 설계

알고리즘 학습에서 구현 자체보다 오래 남는 자산은 검증 습관입니다. 아래 체크는 주제와 무관하게 거의 모든 문제에서 공통으로 적용됩니다.

### 1) 마이크로 벤치마크 규칙

```python
import time

def benchmark(func, *args, repeat: int = 5) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best
```

- 단일 실행 시간은 노이즈가 큽니다.
- 최소/중앙값 기준으로 비교하는 편이 안정적입니다.
- 입력 크기를 여러 단계로 늘려 증가 추세를 기록해야 합니다.

### 2) 반례 세트 템플릿

```text
A. 최소 입력: 빈 배열, 원소 1개
B. 중복 입력: 같은 값 다수
C. 정렬/역정렬 입력: 경계 인덱스 오류 탐지
D. 음수/0 포함 입력: 비교식 방향 오류 탐지
E. 해답 없음 케이스: 종료 조건 검증
```

테스트를 통과했는지보다, 어떤 종류의 실패를 막았는지 기록하는 편이 품질에 더 직접적입니다.

### 3) 복잡도-메모리 트레이드오프 표

| 개선 전략 | 시간 영향 | 공간 영향 | 적용 판단 |
|-----------|-----------|-----------|-----------|
| 캐시/메모이제이션 | 감소 | 증가 | 중복 계산이 명확할 때 |
| 정렬 후 탐색 | 대체로 감소 | 동일/약간 증가 | 질의가 여러 번일 때 |
| 해시 사용 | 평균 감소 | 증가 | 순서보다 조회가 중요할 때 |
| 힙 사용 | 상위/최소 유지에 유리 | 증가 | 우선순위 선택이 핵심일 때 |

### 4) 인터뷰 답변 스크립트

- "먼저 입력 제약을 보고 가능한 복잡도 상한을 정하겠습니다."
- "현재 접근의 시간/공간 복잡도를 계산해 보겠습니다."
- "경계 입력 다섯 가지로 검증 계획을 먼저 제시하겠습니다."
- "필요하면 정답 유지 조건을 짧게 증명하겠습니다."

이 스크립트를 반복하면 설명의 밀도가 올라가고, 구현 중 길을 잃는 빈도가 줄어듭니다.

## 처음 질문으로 돌아가기

- **DP가 적용되는 두 조건은 무엇일까요?**
  - 본문의 기준은 동적 계획법 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **메모이제이션을 쓰는 top-down 구현은 어떻게 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **테이블을 채우는 bottom-up 구현은 어떻게 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/06-dynamic-programming-basics)

Tags: Python, Algorithms, Dynamic Programming, DP, Memoization
