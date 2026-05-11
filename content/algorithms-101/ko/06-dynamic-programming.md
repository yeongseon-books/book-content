---
series: algorithms-101
episode: 6
title: 동적 계획법
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 알고리즘
  - 동적 계획법
  - 메모이제이션
  - 타뷸레이션
  - 최적 부분 구조
seo_description: 동적 계획법의 두 조건, 메모이제이션과 타붔레이션의 차이, 그리고 고전 DP 문제로 상태 정의 감각을 익힙니다.
last_reviewed: '2026-05-04'
---

# 동적 계획법

> Algorithms 101 시리즈 (6/10)


## 이 글에서 다룰 문제

DP는 알고리즘 면접의 핵심이자 실무에서도 최적화·스케줄링·문자열 비교에 등장합니다. 또한 DP의 사고 과정은 강화학습의 가치 함수, 동적 프로그래밍 기반 컨트롤러, 시퀀스-투-시퀀스 모델의 디코더까지 확장됩니다.

> DP는 "이미 푼 답을 두 번 풀지 않는다"는 단 하나의 원칙으로 시작됩니다.

## 전체 흐름
> DP는 상태 공간 위에서 점화식을 정의하고 풀어가는 기법입니다. 메모이제이션은 재귀 + 캐시이며 직관적입니다. 타뷸레이션은 작은 상태부터 채워 올라가며 메모리·속도가 더 좋습니다. 핵심은 "상태를 무엇으로 잡을지"이며 이것이 전체 풀이의 90%입니다.

```text
DP 적용 가능 신호
    1) 같은 부분 문제가 여러 번 등장 (중복 부분 문제)
    2) 부분 문제의 최적해 → 전체 최적해 (최적 부분 구조)

두 가지 구현 방식
    Top-down  (memoization)  : 재귀 + 캐시,  필요한 상태만 계산
    Bottom-up (tabulation)   : 반복문,      모든 상태를 순서대로 채움
```

## Before / After

**Before — 메모 없는 피보나치, O(2^n):**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(40) 부터 매우 느림
```

**After — 메모이제이션, O(n):**

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

## 단계별로 따라하기

### 1단계: 중복 부분 문제 시각화

```python
calls = 0
def fib_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

fib_naive(20)
print(calls)   # 13529 — n에 비해 폭발적
```

같은 fib(k)가 여러 번 호출됨을 직접 확인합니다. 이 반복이 DP의 출발점입니다.

### 2단계: Top-down (메모이제이션)

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))   # 354224848179261915075
```

재귀 구조를 그대로 유지한 채 데코레이터 한 줄로 캐시를 추가합니다. 직관적이고 확장하기 쉽습니다.

### 3단계: Bottom-up (타뷸레이션)

```python
def fib_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(fib_tab(100))
```

작은 상태부터 채웁니다. 재귀 깊이에 영향받지 않고 메모리도 두 변수로 더 줄일 수 있습니다(rolling).

### 4단계: 0/1 Knapsack — 상태 정의 연습

```python
def knapsack(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for cap in range(W + 1):
            dp[i][cap] = dp[i - 1][cap]
            if w <= cap:
                dp[i][cap] = max(dp[i][cap], dp[i - 1][cap - w] + v)
    return dp[n][W]

print(knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5))   # 7
```

상태: dp[i][cap] = i번째까지 고려, 용량 cap일 때 최대 가치. 상태 정의가 명확하면 점화식은 거의 자동으로 따라옵니다.

### 5단계: 최장 공통 부분 수열(LCS) — 두 시퀀스 위의 DP

```python
def lcs(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

print(lcs("ABCBDAB", "BDCABC"))   # 4
```

두 입력의 모든 접두사 쌍에 대한 최적값을 표로 채웁니다. diff 도구, DNA 정렬, 문서 비교의 기초 알고리즘입니다.

## 이 코드에서 주목할 점

- 상태 정의가 풀이의 90%다
- top-down은 직관적, bottom-up은 메모리·속도에 유리
- 2차원 DP에서 흔히 한 차원만 유지해도 충분(rolling array)
- 같은 문제도 상태 정의에 따라 시간·공간 비용이 크게 달라짐

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 상태 정의 없이 코드 시작 | 점화식 혼란 | "dp[...] = ?의 의미"를 한 문장으로 적기 |
| 베이스 케이스 누락 | 잘못된 결과 | dp[0], dp[i][0]을 명시적으로 초기화 |
| 캐시 키에 가변 객체 | 캐시 미스 | tuple로 변환 |
| 중복 부분 문제 없는데 DP 적용 | 단순 분할 정복이 더 적합 | 동일 부분 문제 등장 여부 확인 |
| 메모리 폭발 | 큰 입력에서 OOM | rolling array로 차원 줄이기 |

## 실무에서는 이렇게 쓰입니다

- diff/patch 알고리즘 (LCS의 응용)
- 문자열 유사도 (편집 거리)
- 음성 인식의 DTW (Dynamic Time Warping)
- 데이터베이스 쿼리 옵티마이저의 조인 순서 결정
- 강화학습의 가치 함수 갱신 (Bellman 방정식)

## 체크리스트

- [ ] DP의 두 조건을 점검할 수 있는가
- [ ] 상태와 점화식을 한 문장으로 표현할 수 있는가
- [ ] top-down과 bottom-up을 모두 작성할 수 있는가
- [ ] rolling array로 메모리를 줄여 본 적이 있는가
- [ ] 적용 가능성 신호를 인식할 수 있는가

## 정리 및 다음 단계

DP는 "이미 푼 답을 두 번 풀지 않는다"는 원칙으로 시작합니다. 같은 부분 문제가 반복되고 부분의 최적이 전체 최적을 이루면 적용 가능합니다. 상태 정의가 풀이의 거의 전부이며, top-down으로 시작해 bottom-up으로 다듬는 흐름이 학습에 효율적입니다.

다음 글에서는 그리디 알고리즘을 살펴봅니다. 그리디가 통하는 조건(교환 논증, 매트로이드 직관), 대표 문제, 그리고 그리디로 보일 뿐 실제로는 DP가 필요한 경우를 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- **동적 계획법 (현재 글)**
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [CLRS — Introduction to Algorithms, Chapter 15](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Competitive Programmer's Handbook — Chapter 7](https://cses.fi/book/book.pdf)

Tags: Computer Science, 알고리즘, 동적 계획법, 메모이제이션, 타뷸레이션, 최적 부분 구조
