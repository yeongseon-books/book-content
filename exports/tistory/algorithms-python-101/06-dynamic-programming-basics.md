
# 동적 계획법 기초

> Algorithms with Python 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 계산을 반복하지 않으면서 최적의 답을 어떻게 구할까요?

> 동적 계획법(DP)은 큰 문제를 작은 하위 문제로 나누고, 각 하위 문제의 결과를 저장하여 중복 계산을 제거하는 기법입니다. 이 글에서는 탑다운(메모이제이션)과 바텀업(테이블) 접근법을 실전 문제로 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- DP가 적용 가능한 조건: 최적 부분 구조와 중복 하위 문제
- 탑다운(메모이제이션) 구현
- 바텀업(테이블) 구현
- 대표 DP 문제: 피보나치, 계단 오르기, 배낭 문제

## 왜 중요한가

재귀만으로는 지수 시간이 걸리는 문제를 DP로 다항 시간에 풀 수 있습니다. 피보나치 수열의 단순 재귀는 O(2^n)이지만, DP를 적용하면 O(n)이 됩니다.

> DP = 하위 문제의 결과를 저장하여 중복 계산을 제거하는 최적화 기법

DP는 코딩 면접에서 가장 자주 출제되는 유형입니다. 패턴을 익혀두면 다양한 최적화 문제에 체계적으로 접근할 수 있습니다.

## 핵심 개념 잡기

> DP 적용 조건 = 최적 부분 구조 + 중복 하위 문제

```
피보나치 fib(5) — 단순 재귀의 중복 계산:
fib(5) → fib(4) + fib(3)
          fib(4) → fib(3) + fib(2)   ← fib(3) 중복
                    fib(3) → fib(2) + fib(1)  ← fib(2) 중복

DP 적용 후: 각 fib(n)을 한 번만 계산하고 저장
fib(1)=1 → fib(2)=1 → fib(3)=2 → fib(4)=3 → fib(5)=5
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 최적 부분 구조(optimal substructure) | 큰 문제의 최적해가 작은 문제의 최적해로 구성되는 성질입니다 |
| 중복 하위 문제(overlapping subproblems) | 같은 하위 문제가 여러 번 반복 계산되는 성질입니다 |
| 메모이제이션(memoization) | 계산 결과를 캐시하여 재활용하는 탑다운 기법입니다 |
| 테이블(tabulation) | 작은 문제부터 순서대로 채워가는 바텀업 기법입니다 |
| 상태 전이(state transition) | 현재 상태를 이전 상태로부터 계산하는 점화식입니다 |

## Before / After

피보나치 수열을 구하는 두 가지 방법을 비교합니다.

```python
# before: 단순 재귀 — O(2^n)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

```python
# after: DP 바텀업 — O(n)
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

### Step 1: 탑다운 — 메모이제이션

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fib_top_down(n: int) -> int:
    """탑다운 피보나치 — O(n)"""
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

### Step 2: 바텀업 — 테이블

```python
def fib_bottom_up(n: int) -> int:
    """바텀업 피보나치 — O(n), 공간 O(n)"""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(fib_bottom_up(50))  # 12586269025


def fib_optimized(n: int) -> int:
    """공간 최적화 피보나치 — O(n), 공간 O(1)"""
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1

print(fib_optimized(50))  # 12586269025
```

### Step 3: 계단 오르기 문제

```python
def climb_stairs(n: int) -> int:
    """n개의 계단을 1칸 또는 2칸씩 오르는 방법의 수"""
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# 점화식: dp[i] = dp[i-1] + dp[i-2]
# 마지막에 1칸 오른 경우 + 마지막에 2칸 오른 경우
for n in range(1, 8):
    print(f"계단 {n}개: {climb_stairs(n)}가지")
# 계단 1개: 1가지
# 계단 2개: 2가지
# 계단 3개: 3가지
# 계단 4개: 5가지
# 계단 5개: 8가지
# 계단 6개: 13가지
# 계단 7개: 21가지
```

### Step 4: 최소 동전 교환 문제

```python
def coin_change(coins: list[int], amount: int) -> int:
    """금액을 만드는 최소 동전 개수 — O(amount × len(coins))"""
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float("inf") else -1

print(coin_change([1, 5, 10], 13))   # 4 (10+1+1+1)
print(coin_change([1, 5, 10], 30))   # 3 (10+10+10)
print(coin_change([3, 7], 5))        # -1 (불가능)
```

### Step 5: 0-1 배낭 문제

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """0-1 배낭 문제 — O(n × capacity)"""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # 현재 물건을 안 넣는 경우
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)

    return dp[n][capacity]

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
print(knapsack(weights, values, capacity))  # 10 (물건 1+3 또는 2+4)
```

## 이 코드에서 주목할 점

- 탑다운은 필요한 하위 문제만 계산하고, 바텀업은 모든 하위 문제를 순서대로 계산합니다
- 공간 최적화는 이전 값만 필요한 경우 배열 대신 변수 두 개로 충분합니다
- 점화식을 세우는 것이 DP의 핵심입니다. "마지막 선택"을 기준으로 생각합니다
- 배낭 문제에서 2차원 테이블은 "물건 수 × 용량"으로 모든 조합을 기록합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 점화식을 세우지 않고 코딩 시작 | 구조 없이 작성하면 논리 오류가 생깁니다 | 점화식을 먼저 수식으로 정리합니다 |
| 기저 조건 누락 | dp[0] 등 초기값이 없으면 결과가 틀립니다 | 가장 작은 하위 문제부터 정의합니다 |
| 테이블 크기 오류 | 인덱스 범위를 넘기면 IndexError입니다 | n+1 크기로 할당합니다 |
| 탑다운에서 재귀 깊이 초과 | n이 크면 RecursionError입니다 | 바텀업으로 변환합니다 |
| 불필요한 2차원 테이블 | 공간을 낭비합니다 | 이전 행만 필요하면 1차원으로 최적화합니다 |

## 실무에서 이렇게 쓰입니다

- 경로 최적화에서 최소 비용 경로를 DP로 계산합니다
- 텍스트 편집 거리(Levenshtein distance)가 맞춤법 검사에 사용됩니다
- 자연어 처리에서 Viterbi 알고리즘이 DP를 활용합니다
- 재무에서 포트폴리오 최적화 문제를 DP로 풀기도 합니다
- 게임 AI에서 최적 전략을 DP로 탐색합니다

## 현업 개발자는 이렇게 생각합니다

DP를 실무에서 직접 구현할 일은 드물지만, DP적 사고방식은 매우 유용합니다. "이 계산을 캐시할 수 있는가?", "이 문제에 최적 부분 구조가 있는가?"라는 질문은 성능 최적화의 핵심입니다.

코딩 면접에서 DP 문제를 만나면 점화식을 먼저 세우고, 바텀업으로 구현하는 것이 가장 안전합니다. 탑다운은 직관적이지만 재귀 깊이 문제가 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **점화식 우선** — 코드 전에 점화식과 상태 정의가 정확해야 합니다.
- **Top-down vs Bottom-up** — 직관·디버깅은 top-down, 성능은 bottom-up이 보통 유리합니다.
- **공간 최적화** — 필요 상태만 유지해 공간을 줄입니다.
- **경계** — 빈 입력·최소 입력에서 점화식이 무너지지 않는지 검증합니다.
- **실전 적용** — 실무에서는 라이브러리/캐시로 대체 가능한지 먼저 확인합니다.

## 체크리스트

- [ ] DP 적용 조건 두 가지를 설명할 수 있다
- [ ] 탑다운과 바텀업의 차이를 설명할 수 있다
- [ ] 점화식을 세우고 테이블을 채울 수 있다
- [ ] 공간 최적화 기법을 적용할 수 있다
- [ ] 계단 오르기, 동전 교환 문제를 풀 수 있다

## 연습 문제

1. 1×2 타일로 2×n 직사각형을 채우는 방법의 수를 구하세요.
2. 최장 증가 부분수열(LIS)의 길이를 DP로 구하세요.
3. 동전 교환 문제에서 최소 동전 개수뿐 아니라 실제 사용된 동전 목록도 출력하세요.

## 정리 및 다음 글 안내

동적 계획법은 중복 계산을 제거하여 지수 시간 문제를 다항 시간으로 바꿉니다. 핵심은 점화식을 세우는 것입니다. 다음 글에서는 그래프를 탐색하는 BFS와 DFS 알고리즘을 다룹니다.

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
## 참고 자료

- [Wikipedia — Dynamic Programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Real Python — Memoization with Python](https://realpython.com/lru-cache-python/)
- [GeeksforGeeks — Dynamic Programming](https://www.geeksforgeeks.org/dynamic-programming/)
- [LeetCode — Dynamic Programming Problems](https://leetcode.com/tag/dynamic-programming/)

Tags: Python, 알고리즘, 동적 계획법, DP, 메모이제이션

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
