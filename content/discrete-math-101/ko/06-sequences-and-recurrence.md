---
series: discrete-math-101
episode: 6
title: 수열과 점화식
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
  - 이산수학
  - 점화식
  - 수열
  - 마스터 정리
  - 알고리즘 분석
seo_description: 수열, 점화식, 마스터 정리로 재귀 알고리즘의 시간 복잡도를 푸는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# 수열과 점화식

이 글은 Discrete Math 101 시리즈의 6번째 글입니다.

## 이 글에서 다룰 문제

- 수열과 닫힌 형식은 어떻게 연결될까요?
- 점화식은 어떤 수학적 표기인가요?
- 치환법과 재귀 트리법은 언제 유용할까요?
- 마스터 정리는 어떤 형태의 점화식에 적용될까요?

> 수열은 순서 있는 수의 나열이고, 점화식은 이전 항을 이용해 다음 항을 정의하는 식입니다. 재귀 함수의 실행 시간도 결국 점화식이므로, 치환법, 재귀 트리, 마스터 정리 같은 도구를 통해 닫힌 형식이나 Big-O로 바꿀 수 있습니다. 이 글에서는 정의, 풀이법, 알고리즘 분석과의 연결을 함께 다룹니다.

## 왜 중요한가

`mergesort(n) = 2·mergesort(n/2) + O(n)`은 점화식입니다. 이 식을 풀면 `O(n log n)`이 나옵니다. 분할 정복, 동적 계획법, 재귀 함수 분석은 모두 점화식을 푸는 문제로 귀결됩니다. 점화식을 모르면 재귀 코드는 쓸 수 있어도 그 비용은 설명하지 못합니다.

> 점화식은 재귀 알고리즘을 비추는 수학적 거울입니다.

## 한눈에 보는 개념

> `T(n) = aT(n/b) + f(n)`은 분할 정복의 표준형입니다. 마스터 정리는 이 식에서 닫힌 형식을 빠르게 읽어 내는 도구입니다.

```text
   recursive algorithm
            │
            ↓
     recurrence form
            │
   ┌────────┼────────────┐
   ↓        ↓            ↓
 substitution recursion  Master
            tree       Theorem
   │        │            │
   └────────┴──────┬─────┘
                   ↓
            closed form (Big-O)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Sequence | `a₁, a₂, a₃, ...` 형태의 순서열 |
| Closed form | n으로부터 `aₙ`을 직접 계산하는 식 |
| Recurrence | 이전 항으로 다음 항을 정의하는 식 |
| Master Theorem | `T(n) = aT(n/b) + f(n)`의 표준 해법 |
| Geometric sequence | `aₙ = a₁·rⁿ⁻¹` 꼴의 등비수열 |

## Before / After

**Before — without analysis:**

```python
# "Recursion is slow" — no exact complexity known
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**After — analyzed via recurrence:**

```python
# T(n) = T(n-1) + T(n-2) + O(1)
# Solution: T(n) = O(φⁿ) ≈ O(1.618ⁿ) — exponential
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


# Memoized: T(n) = T(n-1) + O(1) → O(n)
from functools import lru_cache


@lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)
```

## 단계별로 따라가기

### 1단계: 수열 표현하기

```python
# Arithmetic: aₙ = a₁ + (n-1)d
def arithmetic(a1: float, d: float, n: int) -> list:
    return [a1 + (i - 1) * d for i in range(1, n + 1)]


# Geometric: aₙ = a₁ · rⁿ⁻¹
def geometric(a1: float, r: float, n: int) -> list:
    return [a1 * (r ** (i - 1)) for i in range(1, n + 1)]


print(f"arithmetic (a=2, d=3, n=5): {arithmetic(2, 3, 5)}")
print(f"geometric  (a=1, r=2, n=8): {geometric(1, 2, 8)}")
```

등차수열과 등비수열은 닫힌 형식이 명확합니다. 어려운 점화식을 풀 때도 결국 이런 익숙한 형태로 바꿀 수 있는지가 핵심입니다.

### 2단계: 점화식을 직접 계산하기

```python
# Recurrence: T(n) = T(n-1) + n, T(0) = 0
# Meaning: do n units of work at each level
def T(n: int) -> int:
    if n == 0:
        return 0
    return T(n - 1) + n


# Closed form: T(n) = n(n+1)/2
def T_closed(n: int) -> int:
    return n * (n + 1) // 2


for n in [1, 5, 10, 100]:
    assert T(n) == T_closed(n)
    print(f"T({n}) = {T(n)} (closed: {T_closed(n)})")
```

점화식의 의미를 코드로 계산해 보면 왜 닫힌 형식이 필요한지 감이 옵니다. 값을 하나씩 누적하는 방식은 개념을 보여 주지만, 복잡도 자체를 설명해 주지는 못합니다.

### 3단계: 치환법으로 풀기

```python
# Recurrence: T(n) = 2T(n/2) + n, T(1) = 1
# Substitute repeatedly:
# T(n) = 2T(n/2) + n
#      = 2[2T(n/4) + n/2] + n = 4T(n/4) + 2n
#      = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + 3n
#      ...
#      = 2^k T(n/2^k) + kn
# n/2^k = 1 → k = log n
# T(n) = n·T(1) + n log n = O(n log n)


def merge_sort_count(arr: list) -> tuple:
    """Merge sort that also returns the comparison count."""
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
    print(f"n={n}: {count} comparisons, n log n = {n * int(math.log2(n))}")
```

치환법은 점화식의 구조를 손으로 펼쳐 보는 방식입니다. 병합 정렬이 왜 `n log n`인지 이해할 때 가장 교육적인 방법이기도 합니다.

### 4단계: 마스터 정리

```python
# Master Theorem: T(n) = aT(n/b) + f(n)
# Compare n^(log_b a) and f(n) — three cases:
# 1. f(n) = O(n^(log_b a - ε))           → T(n) = Θ(n^(log_b a))
# 2. f(n) = Θ(n^(log_b a))                → T(n) = Θ(n^(log_b a) · log n)
# 3. f(n) = Ω(n^(log_b a + ε)) (regular)  → T(n) = Θ(f(n))

import math


def master_theorem(a: int, b: int, f_exponent: float) -> str:
    """Estimate the closed form of T(n) = aT(n/b) + n^f_exponent."""
    critical = math.log(a, b)
    if f_exponent < critical:
        return f"Θ(n^{critical:.2f})"
    elif abs(f_exponent - critical) < 1e-9:
        return f"Θ(n^{critical:.2f} · log n)"
    else:
        return f"Θ(n^{f_exponent})"


# Merge sort: T(n) = 2T(n/2) + n  → a=2, b=2, f(n)=n¹
print(f"merge sort:        {master_theorem(2, 2, 1)}")
# Binary search: T(n) = T(n/2) + 1
print(f"binary search:     {master_theorem(1, 2, 0)}")
# Strassen: T(n) = 7T(n/2) + n²
print(f"Strassen multiply: {master_theorem(7, 2, 2)}")
```

마스터 정리는 분할 정복 알고리즘을 빠르게 분류하는 표준 도구입니다. 다만 아무 점화식에나 붙일 수 있는 만능 공식은 아니라는 점을 함께 기억해야 합니다.

### 5단계: 피보나치의 닫힌 형식

```python
# Fibonacci: F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1
# Characteristic equation: x² = x + 1 → x = (1±√5)/2 = φ, ψ
# Closed form: F(n) = (φⁿ - ψⁿ) / √5

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

선형 점화식은 특성방정식으로 닫힌 형식을 얻을 수 있습니다. 피보나치에서 황금비가 나오는 것은 우연이 아니라 이 기법의 직접적인 결과입니다.

## 주목할 점

- 점화식은 재귀 알고리즘의 시간 복잡도를 수학적으로 표현합니다.
- 마스터 정리는 분할 정복 문제의 표준 도구입니다.
- 닫힌 형식을 얻으면 임의의 n에 대한 비용을 즉시 예측할 수 있습니다.
- 메모이제이션은 중복 부분문제를 제거해 지수 시간을 다항 시간으로 낮춥니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 마스터 정리 조건을 무시한다 | case 3의 정칙 조건 등을 놓친다 | 세 경우와 전제를 함께 확인한다 |
| 기저 조건을 빼먹는다 | 점화식만 있고 시작점이 없다 | T(1) 또는 T(0)을 명시한다 |
| 로그의 밑을 대충 본다 | 정확한 수치 해석이 흐려진다 | Big-O와 정확한 값 계산을 구분한다 |
| 비균등 분할에도 마스터 정리를 쓴다 | 적용 자체가 틀린다 | 직접 전개나 다른 방법을 쓴다 |
| 메모이제이션을 빠뜨린다 | 의도치 않게 지수 시간이 된다 | 중복 부분문제가 있으면 먼저 의심한다 |

## 실무에서는 이렇게 사용합니다

- 면접에서 병합 정렬, 퀵 정렬, 이진 탐색의 복잡도를 설명합니다.
- 배낭 문제, LIS, 편집 거리 같은 DP 문제의 점화식을 세웁니다.
- B-tree 인덱스의 탐색 깊이를 추정합니다.
- 분산 시스템의 메시지 비용을 계산합니다.
- 재시도 백오프나 캐시 갱신 간격도 수열로 설계할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 알고리즘을 보면 먼저 “이 함수가 자기 자신을 몇 번, 어떤 크기로 호출하는가”를 묻습니다. 즉시 점화식을 세우고, 가능하면 마스터 정리나 전개법으로 비용을 읽어 냅니다. 이런 사고는 알고리즘 밖에서도 반복 간격, 캐시 압력 증가, 재시도 전략 설계에 그대로 적용됩니다.

## 체크리스트

- [ ] 등차수열과 등비수열의 닫힌 형식을 기억한다
- [ ] `T(n) = aT(n/b) + f(n)` 꼴을 알아볼 수 있다
- [ ] 마스터 정리의 세 경우를 구분할 수 있다
- [ ] 병합 정렬이 왜 `O(n log n)`인지 설명할 수 있다
- [ ] 메모이제이션이 복잡도를 낮추는 이유를 이해한다

## 연습 문제

1. 마스터 정리로 `T(n) = 3T(n/2) + n²`의 닫힌 형식을 구해 보세요.

2. 반복형 피보나치와 순진한 재귀 피보나치를 `n = 30, 35, 40`에서 비교해 보세요.

3. 자신이 작성한 재귀 함수 하나를 골라 점화식으로 바꾸고 시간 복잡도를 유도해 보세요.

## 정리 및 다음 단계

수열은 순서 있는 값의 나열이고, 점화식은 그 값을 재귀적으로 정의하는 방식입니다. 치환법, 재귀 트리, 마스터 정리는 점화식을 닫힌 형식이나 Big-O로 바꾸어 재귀 알고리즘의 비용을 읽게 해 줍니다.

다음 글에서는 경우의 수를 세는 수학, 조합론으로 넘어가겠습니다.

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

Tags: Computer Science, 이산수학, 점화식, 수열, 마스터 정리, 알고리즘 분석
