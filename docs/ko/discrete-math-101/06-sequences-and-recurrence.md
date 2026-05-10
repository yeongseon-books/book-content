---
series: discrete-math-101
episode: 6
title: 수열과 점화식
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
  - 이산수학
  - 점화식
  - 수열
  - 마스터 정리
  - 알고리즘 분석
seo_description: 수열의 정의, 점화식 풀이, 마스터 정리를 통해 재귀 알고리즘의 시간 복잡도를 정확히 분석하는 방법.
last_reviewed: '2026-05-04'
---

# 수열과 점화식

> Discrete Math 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 병합 정렬이 O(n log n)이라는 것을 어떻게 증명할까요? 재귀 함수의 호출 횟수를 어떻게 정확히 계산할까요?

> 수열(sequence)은 순서가 있는 수의 나열이며, 점화식(recurrence)은 수열의 다음 항을 이전 항으로 정의하는 식입니다. 재귀 함수의 시간 복잡도는 점화식으로 표현되고, 마스터 정리(Master Theorem)와 풀이 기법을 통해 닫힌 형식(closed form)으로 변환됩니다. 이 글에서는 수열·점화식의 정의, 풀이 방법, 그리고 알고리즘 분석에의 직접 응용을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 수열의 정의와 닫힌 형식
- 점화식의 수학적 표현
- 치환법과 재귀 트리법
- 마스터 정리(Master Theorem)

## 왜 중요한가

`mergesort(n) = 2·mergesort(n/2) + O(n)` — 이것이 점화식입니다. 이 식을 풀면 O(n log n)이 나옵니다. 모든 분할 정복 알고리즘, 동적 계획법, 재귀 함수의 분석은 점화식 풀이입니다. 점화식을 모르면 코드를 작성할 수는 있어도 분석할 수 없습니다.

> 점화식 = 재귀 알고리즘의 수학적 거울

## 개념 한눈에 보기

> 점화식 T(n) = aT(n/b) + f(n)은 분할 정복의 표준 형태. 마스터 정리로 즉시 닫힌 형식 유도.

```text
   재귀 알고리즘
        │
        ↓
   점화식 표현
        │
   ┌────┼─────────┐
   ↓    ↓         ↓
 치환법 재귀트리  마스터 정리
   │    │         │
   └────┴────┬────┘
             ↓
        닫힌 형식 (Big-O)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 수열 | a₁, a₂, a₃, ... |
| 닫힌 형식 | n으로 직접 계산 가능한 식 |
| 점화식 | aₙ = f(aₙ₋₁, ...) 형태 |
| 마스터 정리 | T(n) = aT(n/b) + f(n) 풀이 공식 |
| 등비수열 | aₙ = a₁·rⁿ⁻¹ |

## Before / After

**Before — 분석 없이:**

```python
# "재귀니까 느릴 거야" — 정확한 복잡도 모름
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**After — 점화식으로 분석:**

```python
# T(n) = T(n-1) + T(n-2) + O(1)
# 풀이: T(n) = O(φⁿ) ≈ O(1.618ⁿ) — 지수 시간
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


# 메모이제이션: T(n) = T(n-1) + O(1) → O(n)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)
```

## 실습: 단계별로 따라하기

### 1단계: 수열의 표현

```python
# 등차수열: aₙ = a₁ + (n-1)d
def arithmetic(a1: float, d: float, n: int) -> list:
    return [a1 + (i - 1) * d for i in range(1, n + 1)]


# 등비수열: aₙ = a₁ · rⁿ⁻¹
def geometric(a1: float, r: float, n: int) -> list:
    return [a1 * (r ** (i - 1)) for i in range(1, n + 1)]


print(f"등차 (a=2, d=3, n=5): {arithmetic(2, 3, 5)}")
print(f"등비 (a=1, r=2, n=8): {geometric(1, 2, 8)}")
```

등차·등비수열은 닫힌 형식이 명확합니다. 더 복잡한 점화식도 같은 형태로 환원하는 것이 풀이 전략입니다.

### 2단계: 점화식의 직접 계산

```python
# 점화식: T(n) = T(n-1) + n, T(0) = 0
# 의미: 매 단계마다 n번 작업
def T(n: int) -> int:
    if n == 0:
        return 0
    return T(n - 1) + n


# 닫힌 형식: T(n) = n(n+1)/2
def T_closed(n: int) -> int:
    return n * (n + 1) // 2


for n in [1, 5, 10, 100]:
    assert T(n) == T_closed(n)
    print(f"T({n}) = {T(n)} (closed: {T_closed(n)})")
```

### 3단계: 치환법으로 점화식 풀기

```python
# 점화식: T(n) = 2T(n/2) + n, T(1) = 1
# 치환:
# T(n) = 2T(n/2) + n
#      = 2[2T(n/4) + n/2] + n = 4T(n/4) + 2n
#      = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + 3n
#      ...
#      = 2^k T(n/2^k) + kn
# n/2^k = 1 → k = log n
# T(n) = n·T(1) + n log n = O(n log n)


def merge_sort_count(arr: list) -> tuple:
    """병합 정렬과 비교 횟수 반환"""
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, lc = merge_sort_count(arr[:mid])
    right, rc = merge_sort_count(arr[mid:])
    merged, mc = merge_count(left, right)
    return merged, lc + rc + mc


def merge_count(a: list, b: list) -> tuple:
    result = []
    i = j = c = 0
    while i < len(a) and j < len(b):
        c += 1
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result, c


import math

for n in [16, 64, 256]:
    arr = list(range(n, 0, -1))
    _, count = merge_sort_count(arr)
    print(f"n={n}: 비교 {count}회, n log n = {n * int(math.log2(n))}")
```

### 4단계: 마스터 정리

```python
# 마스터 정리: T(n) = aT(n/b) + f(n)
# n^(log_b a)와 f(n)의 비교로 세 경우:
# 1. f(n) = O(n^(log_b a - ε))     → T(n) = Θ(n^(log_b a))
# 2. f(n) = Θ(n^(log_b a))          → T(n) = Θ(n^(log_b a) · log n)
# 3. f(n) = Ω(n^(log_b a + ε)) (정칙) → T(n) = Θ(f(n))

import math


def master_theorem(a: int, b: int, f_exponent: float) -> str:
    """T(n) = aT(n/b) + n^f_exponent의 닫힌 형식 추정"""
    critical = math.log(a, b)
    if f_exponent < critical:
        return f"Θ(n^{critical:.2f})"
    elif abs(f_exponent - critical) < 1e-9:
        return f"Θ(n^{critical:.2f} · log n)"
    else:
        return f"Θ(n^{f_exponent})"


# 병합 정렬: T(n) = 2T(n/2) + n  → a=2, b=2, f(n)=n¹
print(f"병합 정렬: {master_theorem(2, 2, 1)}")
# 이진 탐색: T(n) = T(n/2) + 1
print(f"이진 탐색: {master_theorem(1, 2, 0)}")
# Strassen: T(n) = 7T(n/2) + n²
print(f"Strassen 행렬 곱: {master_theorem(7, 2, 2)}")
```

### 5단계: 피보나치 수열의 닫힌 형식

```python
# 피보나치: F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1
# 특성방정식: x² = x + 1 → x = (1±√5)/2 = φ, ψ
# 닫힌 형식: F(n) = (φⁿ - ψⁿ) / √5

import math

PHI = (1 + math.sqrt(5)) / 2
PSI = (1 - math.sqrt(5)) / 2


def fib_closed(n: int) -> int:
    return round((PHI ** n - PSI ** n) / math.sqrt(5))


def fib_iter(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


for n in [10, 20, 30]:
    assert fib_closed(n) == fib_iter(n)
    print(f"F({n}) = {fib_closed(n)} (closed = iter)")
```

선형 점화식은 특성방정식으로 닫힌 형식을 유도할 수 있습니다. 피보나치의 황금비 등장은 이 기법의 결과입니다.

## 이 코드에서 주목할 점

- 점화식은 재귀 알고리즘의 시간 복잡도를 표현
- 마스터 정리는 분할 정복의 표준 풀이 도구
- 닫힌 형식을 얻으면 임의의 n에 대해 즉시 계산 가능
- 메모이제이션은 점화식의 중복 계산을 제거하여 지수 → 다항으로 변환

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 마스터 정리 조건 무시 | 정칙 조건(case 3) 놓침 | 세 경우 모두 명시적으로 검사 |
| 기저 조건 누락 | 점화식만 정의, T(1) 빠뜨림 | 항상 시작 항 명시 |
| log의 밑 혼동 | log₂와 log₁₀ 결과 다름 | Big-O에서는 상수배 무시되나 추적 필요 |
| 비균등 분할 | T(n)=T(n-1)+T(n-2)에 마스터 정리 적용 | 마스터 정리는 균등 분할만 |
| 메모이제이션 누락 | 지수 시간 알고리즘 작성 | 중복 부분문제는 항상 메모이제이션 |

## 실무에서는 이렇게 쓰입니다

- 알고리즘 면접에서 시간 복잡도 분석 (병합 정렬, 퀵 정렬, 이진 탐색)
- 동적 계획법 문제의 점화식 도출 (배낭 문제, LIS, 편집 거리)
- 데이터베이스 인덱스(B-tree)의 탐색 깊이 분석
- 분산 시스템의 메시지 복잡도 추정
- 캐시 무효화 빈도, 재시도 백오프 설계

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 새 알고리즘을 보면 즉시 점화식을 머릿속에 그립니다. "이 함수가 자기 자신을 몇 번, 어떤 크기로 호출하는가?" 그리고 마스터 정리로 즉답합니다. 또한 캐시 정책이나 백오프 전략을 설계할 때도 점화식 사고를 적용합니다 — "n번째 재시도 간격은 어떤 수열을 따라야 하는가?"

## 체크리스트

- [ ] 등차·등비수열의 닫힌 형식을 기억하는가
- [ ] 점화식 T(n) = aT(n/b) + f(n) 형태를 인식할 수 있는가
- [ ] 마스터 정리의 세 경우를 구분할 수 있는가
- [ ] 병합 정렬의 점화식을 풀어 O(n log n)을 유도할 수 있는가
- [ ] 메모이제이션이 왜 복잡도를 낮추는지 이해했는가

## 연습 문제

1. T(n) = 3T(n/2) + n²의 닫힌 형식을 마스터 정리로 구하세요.

2. 피보나치 수열의 반복 구현(O(n))과 단순 재귀 구현(O(φⁿ))의 실행 시간을 n=30, 35, 40에서 측정해 비교하세요.

3. 자신이 작성한 재귀 함수 하나를 골라 점화식으로 표현하고, 시간 복잡도를 도출하세요.

## 정리 및 다음 단계

수열은 순서 있는 수의 나열, 점화식은 재귀적 정의입니다. 마스터 정리·치환법·재귀 트리법으로 닫힌 형식을 얻으면 알고리즘의 정확한 복잡도를 도출할 수 있습니다. 이는 분할 정복과 동적 계획법 분석의 표준 도구입니다.

다음 글에서는 "셈"의 수학 — 조합과 경우의 수 — 를 살펴봅니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- **수열과 점화식 (현재 글)**
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms — CLRS, Chapter 4 (Master Theorem)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — Recurrence Relation](https://en.wikipedia.org/wiki/Recurrence_relation)
- [MIT OCW — Mathematics for Computer Science, Lecture 19-21](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
