---
series: algorithms-101
episode: 6
title: "Algorithms 101 (6/10): 동적 계획법"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: 동적 계획법이 적용되는 두 조건, 메모이제이션과 타뷸레이션의 차이, 그리고 상태 설계의 감각을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (6/10): 동적 계획법

이 글은 Algorithms 101 시리즈의 6번째 글입니다.

왜 우리는 같은 부분 문제를 자꾸 다시 풀게 될까요? 그리고 그 패턴은 어떻게 알아챌 수 있을까요? 여기서는 DP가 적용되는 조건, 메모이제이션과 타뷸레이션의 차이, 그리고 상태를 설계하는 감각을 다룹니다.

![Algorithms 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/06/06-01-big-picture.ko.png)
*Algorithms 101 6장 흐름 개요*

## 먼저 던지는 질문

- 동적 계획법이 성립하려면 어떤 두 조건이 필요할까요?
- 메모이제이션과 타뷸레이션은 어떻게 다를까요?
- 상태는 어떻게 정의하고 점화식은 어떻게 세워야 할까요?

## 왜 중요한가

동적 계획법은 알고리즘 면접의 핵심이면서도, 실무에서는 최적화, 스케줄링, 문자열 비교에 자주 등장합니다. 같은 사고방식은 강화학습의 가치 함수, 동적 계획 기반 제어, 시퀀스 모델의 디코더 같은 영역에도 이어집니다.

> DP는 "같은 부분 문제를 두 번 풀지 않는다"는 원칙에서 시작합니다.

## 한눈에 보는 개념

> DP는 상태 공간 위에 점화식을 정의하고 그 값을 채우는 방식입니다. 메모이제이션은 재귀에 캐시를 붙이는 top-down 방식이라 직관적입니다. 타뷸레이션은 작은 상태부터 표를 채워 올라가는 bottom-up 방식이라 보통 더 빠르고 메모리도 절약합니다. 하지만 진짜 어려운 부분은 구현 방식이 아니라 상태를 무엇으로 정의할지 결정하는 일입니다. 그 선택이 풀이의 90%를 차지합니다.

```text
DP applicability signals
    1) The same subproblem appears many times (overlapping subproblems)
    2) Optimal subproblem solutions compose into optimal whole (optimal substructure)

Two implementations
    Top-down  (memoization) : recursion + cache, computes only needed states
    Bottom-up (tabulation)  : iteration,         fills every state in order
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 상태 | DP 테이블의 한 칸이 의미하는 부분 문제 |
| 점화식 | 상태들 사이의 관계식 |
| 중복 부분 문제 | 같은 부분 문제가 반복해서 등장하는 성질 |
| 최적 부분 구조 | 부분 최적해가 전체 최적해를 이루는 성질 |
| 메모이제이션 | 중복 계산을 없애기 위한 결과 캐싱 |

## 개선 전 / 개선 후

**Before — 캐시 없는 피보나치, O(2^n):**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(40) 이상은 고통스러울 정도로 느려집니다.
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

## 단계별로 따라가기

### 1단계: 중복 부분 문제를 눈으로 보기

```python
calls = 0
def fib_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

fib_naive(20)
print(calls)   # 13529 — explosive in n
```

같은 `fib(k)`가 여러 번 다시 계산되는 것을 직접 볼 수 있습니다. 이 반복이 바로 DP의 출발 신호입니다.

### 2단계: Top-down 메모이제이션

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))   # 354224848179261915075
```

재귀 구조는 그대로 유지되고, 캐시가 중복 계산만 없애 줍니다. 이해하기 쉽고 문제를 확장할 때도 편합니다.

### 3단계: Bottom-up 타뷸레이션

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

작은 상태부터 순서대로 채우므로 재귀 깊이 문제를 피할 수 있습니다. 필요하면 배열을 두 개의 rolling 변수로 줄일 수도 있습니다.

### 4단계: 0/1 knapsack으로 상태 정의 연습

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

상태 `dp[i][cap]`는 "앞의 i개 물건만 사용하고 용량 cap일 때 얻을 수 있는 최대 가치"입니다. 상태의 뜻이 분명해지는 순간 점화식은 거의 자동으로 나옵니다.

### 5단계: LCS로 두 시퀀스 위의 DP 보기

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

두 문자열의 모든 접두사 쌍을 상태로 잡아 표를 채웁니다. diff 도구, DNA 정렬, 문서 비교 같은 실제 문제의 핵심 패턴이 여기서 나옵니다.

## 이 글에서 먼저 가져갈 점

- 상태 정의가 풀이의 거의 전부입니다.
- top-down은 자연스럽고, bottom-up은 대체로 더 빠르고 메모리 효율적입니다.
- 2차원 DP는 종종 한 행만 남기는 rolling array로 줄일 수 있습니다.
- 같은 문제도 상태를 어떻게 잡느냐에 따라 비용이 크게 달라집니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 상태 정의 없이 곧바로 코딩 | 점화식이 흐려짐 | `dp[...]`의 의미를 한 문장으로 먼저 씁니다 |
| 베이스 케이스 누락 | 오답 | `dp[0]`, `dp[i][0]` 초기화를 명시합니다 |
| 가변 객체를 캐시 키로 사용 | 캐시 미스 | tuple 등 불변형으로 바꿉니다 |
| 중복 부분 문제가 없는데 DP 적용 | 과한 풀이 | 부분 문제가 정말 반복되는지 먼저 확인합니다 |
| 메모리 폭발 | OOM | rolling array로 차원을 줄입니다 |

## 실무에서는 이렇게 쓰입니다

- diff/patch 알고리즘의 기반인 LCS
- 문자열 유사도 계산인 편집 거리
- 음성 인식의 Dynamic Time Warping
- 데이터베이스 쿼리 최적화의 조인 순서 결정
- 강화학습의 Bellman 방정식 기반 값 갱신

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "같은 부분 문제가 반복되는가"를 묻습니다. 그렇다면 상태를 정의하고 점화식을 적습니다. 보통은 이해하기 쉬운 top-down으로 먼저 풀고, 성능이 중요할 때 bottom-up으로 옮긴 뒤 마지막에 메모리를 줄입니다.

또한 DP를 "기억하는 분할 정복"으로 봅니다. 재귀에 캐시를 붙인 것이 자연스럽게 느껴진다면, 이미 DP의 핵심을 잡은 것입니다. 표를 억지로 그리며 시작하기보다 재귀 → 메모이제이션 → 타뷸레이션 순서로 배우는 편이 훨씬 부드럽습니다.

## 체크리스트

- [ ] DP의 두 조건을 확인할 수 있는가
- [ ] 상태와 점화식의 의미를 한 문장으로 설명할 수 있는가
- [ ] top-down과 bottom-up 둘 다 작성할 수 있는가
- [ ] rolling array로 메모리를 줄여 본 적이 있는가
- [ ] 적용 가능 신호를 알아볼 수 있는가

## 연습 문제

1. 동전 종류와 목표 금액이 주어졌을 때 최소 동전 개수를 반환하는 함수를 작성해 보세요. 먼저 상태와 점화식을 말로 정의한 뒤 코드로 옮겨 보세요.

2. 두 문자열의 편집 거리(Levenshtein distance)를 구해 보세요. 삽입, 삭제, 치환의 비용은 모두 1로 둡니다.

3. 양의 가중치를 가진 그래프에서 두 노드 사이의 총 길이가 5 이하인 경로 수를 세는 DP를 설계해 보세요. 상태는 현재 노드와 남은 길이를 가집니다.

## 정리 및 다음 단계

DP는 "같은 부분 문제를 두 번 풀지 않는다"에서 출발합니다. 중복 부분 문제와 최적 부분 구조가 동시에 있을 때 적용되며, 상태 정의가 사실상 풀이 전체를 결정합니다. 먼저 top-down으로 의미를 잡고, 필요하면 bottom-up으로 다듬는 흐름이 학습과 실전 모두에 잘 맞습니다.

다음 글에서는 그리디 알고리즘을 다룹니다. 그리디가 정말 통하는 조건, 교환 논증, 그리고 겉보기에는 그리디 같지만 실제로는 DP가 필요한 문제를 봅니다.

## 추가 보강: 검증 가능한 예제 세트

### 입력 크기 대비 알고리즘/학습 선택 표

| 상황 | 빠른 선택 | 검증 기준 |
| --- | --- | --- |
| 작은 입력, 빠른 프로토타입 | 단순 구현 우선 | 정답 검증 테스트 3종 |
| 큰 입력, 지연시간 민감 | 차수 낮은 알고리즘 또는 안정적 optimizer | 시간/메모리 동시 측정 |
| 운영 장애 재현 필요 | 로그/추적 필드 강화 | 동일 입력 재실행 가능성 |

### 짧은 비교 코드

```python
import time

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best
```

측정 코드는 화려할 필요가 없습니다. 같은 입력, 같은 환경, 같은 반복 기준을 유지하는 것이 더 중요합니다. 이 습관이 있어야 최적화 전후의 차이를 신뢰할 수 있습니다.

### 실전 점검 질문

1. 지금 선택한 방법의 시간/공간 비용을 한 문장으로 설명할 수 있는가
2. 경계 입력에서 동작이 바뀌는 지점을 테스트로 고정했는가
3. 운영 로그만으로 실패 원인을 분리할 수 있는가

이 질문에 즉답할 수 있으면 구현이 아니라 설계 수준에서 품질을 확보한 상태에 가깝습니다.

## 실전 확장 워크북

이 절은 동적 계획법 상태 설계를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

### 1) 시간 복잡도와 입력 제약을 먼저 맞추기

| 입력 조건 | 우선 배제할 접근 | 현실적인 후보 | 확인 포인트 |
| --- | --- | --- | --- |
| n <= 10^3 | 없음(학습 목적 실험 가능) | 브루트포스, 정렬, 해시 | 구현 명확성 |
| n <= 10^5 | O(n^2) 대부분 배제 | O(n log n), O(n), BFS/DFS | 경계값 테스트 |
| n <= 10^6 이상 | O(n log n)도 부담 가능 | 단일 패스, 압축, 스트리밍 | 메모리 상한 |

복잡도 판단은 코드 스타일 논쟁보다 우선합니다. 같은 팀에서 코드 품질 기준이 달라도, 입력 제약과 차수를 맞추는 원칙은 공통으로 적용됩니다. 이 단계를 건너뛰면 구현이 아무리 깔끔해도 제출 실패나 운영 지연으로 이어집니다.

### 2) 단계별 추적 표로 경계 버그를 조기에 찾기

| 단계 | 관찰 값 | 기대 신호 | 실패 신호 |
| --- | --- | --- | --- |
| 초기화 | 포인터/상태/큐/테이블 | 문제 정의와 일치 | 초기값 누락 |
| 1회 반복 | 상태 전이 | 단조 증가 또는 감소 | 제자리 반복 |
| 종료 직전 | 반환 후보 | 문제 요구와 직접 연결 | 보조값 반환 |

경계 버그는 대부분 "한 줄"에서 발생하지만, 원인은 상태 전이 설계에 있습니다. 그래서 디버깅할 때는 출력값 하나만 보지 말고, 전이 로그를 함께 봐야 합니다. 특히 인덱스 기반 문제는 `lo, mid, hi`, DP 문제는 `state, transition`, 그래프 문제는 `queue size, visited count`를 같이 기록하면 원인 분리가 훨씬 빨라집니다.

### 3) Python 구현 앵커

```python
def coin_change(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if a - c >= 0:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] == INF else dp[amount]
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 70 Climbing Stairs | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 198 House Robber | 상태/포인터 유지 | 경계 인덱스 처리 |
| 322 Coin Change | 자료구조 선택 | 복잡도 목표 미달 |

문제 매핑의 목적은 정답 암기가 아닙니다. 같은 구조를 빠르게 인식하고, "왜 이 패턴을 쓰는가"를 재현하는 데 있습니다. 시리즈 전체를 관통하는 실력 차이는 여기서 발생합니다.

### 5) 비교 벤치마크를 읽는 기준

| 비교 항목 | A 접근 | B 접근 | 의사결정 기준 |
| --- | --- | --- | --- |
| 시간 | 평균적으로 빠름 | 최악 케이스 안정적 | 입력 분포가 고정인지 |
| 메모리 | 추가 배열 필요 | 제자리 처리 가능 | 메모리 제한 강도 |
| 구현 난이도 | 짧음 | 디버깅 난이도 높음 | 팀 유지보수 역량 |

벤치마크 숫자는 환경에 따라 달라집니다. 하지만 차수와 메모리 계층에서 발생하는 방향성은 반복됩니다. 그래서 한 번 측정한 결과를 절대값으로 외우기보다, 어떤 조건에서 우위가 바뀌는지(입력 크기, 정렬 여부, 중복 비율)를 함께 기록해야 다음 의사결정에 도움이 됩니다.

### 6) 제출/배포 전 점검 루틴

1. 문제 제약을 한 줄로 요약하고 불가능한 차수를 먼저 제거합니다.
2. 핵심 자료구조 선택 이유를 "삽입/조회/삭제 비용" 기준으로 적습니다.
3. 경계 입력 3종(빈값, 최소값, 중복/극단값) 테스트를 고정합니다.
4. 시간·공간 복잡도를 코드 옆에 기록하고, 실제 측정값을 짧게 남깁니다.
5. 같은 패턴의 변형 문제를 1개 더 풀어 일반화 여부를 확인합니다.

이 루틴을 꾸준히 적용하면 "이번 문제를 맞춤"에서 끝나지 않고 "같은 유형을 안정적으로 재현"하는 상태로 넘어갈 수 있습니다. 알고리즘 학습은 지식 축적이 아니라 판단 체계 구축이라는 점을 계속 기억하는 것이 중요합니다.

## 처음 질문으로 돌아가기

- **동적 계획법이 성립하려면 어떤 두 조건이 필요할까요?**
  - 같은 부분 문제가 반복되는 중복 부분 문제와, 부분 최적해가 전체 최적해로 이어지는 최적 부분 구조가 필요합니다. 본문이 `fib_naive(20)` 호출 수와 knapsack 점화식을 같이 보여 준 이유가 바로 그 두 조건을 눈으로 확인시키기 위해서입니다.
- **메모이제이션과 타뷸레이션은 어떻게 다를까요?**
  - `@lru_cache`를 붙인 top-down은 필요한 상태만 재귀로 계산하고, `dp = [0] * (n + 1)`로 채우는 bottom-up은 작은 상태부터 순서대로 모두 채웁니다. 그래서 본문도 이해하기는 memoization이 쉽고, 재귀 깊이를 피하기에는 tabulation이 편하다고 정리했습니다.
- **상태는 어떻게 정의하고 점화식은 어떻게 세워야 할까요?**
  - `dp[i][cap]`를 “앞의 i개 물건으로 용량 cap에서 얻는 최대 가치”라고 먼저 문장으로 정의하면, 그다음 `dp[i - 1][cap]`와 `dp[i - 1][cap - w] + v` 비교는 거의 자동으로 나옵니다. 이 글이 계속 상태의 뜻을 먼저 쓰라고 한 이유가 바로 그 지점입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- **동적 계획법 (현재 글)**
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [CLRS — Introduction to Algorithms, Chapter 15](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Competitive Programmer's Handbook — Chapter 7](https://cses.fi/book/book.pdf)

Tags: Computer Science, 알고리즘, 동적 계획법, 메모이제이션, 타뷸레이션, 최적 부분 구조
