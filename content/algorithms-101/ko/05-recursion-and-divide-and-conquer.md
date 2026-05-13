---
series: algorithms-101
episode: 5
title: 재귀와 분할 정복
status: publish-ready
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
  - 재귀
  - 분할 정복
  - 호출 스택
  - 메모이제이션
seo_description: 올바른 재귀의 세 가지 규칙, 호출 스택, 분할 정복 점화식, 그리고 메모이제이션으로 이어지는 사고를 정리합니다.
last_reviewed: '2026-05-12'
---

# 재귀와 분할 정복

재귀는 왜 어렵게 느껴질까요? 그리고 mergesort 같은 분할 정복 알고리즘은 왜 "올바른 이유로" 빠를까요? 이 글은 Algorithms 101 시리즈의 다섯 번째 글입니다. 여기서는 호출 스택, 점화식 기반 비용 분석, 그리고 분할 정복의 핵심 멘탈 모델을 정리합니다.

## 이 글에서 다룰 문제

- 올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?
- 호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?
- 분할 정복 점화식은 어떻게 읽어야 할까요?
- 반복되는 부분 문제가 보일 때 왜 메모이제이션을 떠올려야 할까요?

## 왜 중요한가

재귀가 익숙하지 않으면 트리, 그래프, 분할 정복, 동적 계획법, 백트래킹이 모두 더 어렵게 느껴집니다. 반대로 재귀 사고가 자리 잡으면 복잡한 문제를 "자기 자신과 같은 형태의 더 작은 문제"로 자연스럽게 분해할 수 있습니다.

> 재귀는 알고리즘의 두 번째 모국어입니다.

## 한눈에 보는 개념

> 재귀 함수는 베이스 케이스, 진행 단계, 자기 호출을 가집니다. 분할 정복은 입력을 크기 `n/b`인 부분 문제 `a`개로 나누고, 결과를 `f(n)` 비용으로 결합합니다. 전체 비용은 `T(n) = a · T(n/b) + f(n)`으로 표현할 수 있고, 대표적으로 mergesort는 O(n log n), binary search는 O(log n)이 됩니다.

```text
Recursive shape
    if base case: return
    self-call(smaller input)
    combine results

Divide-and-conquer recurrence
    T(n) = a · T(n/b) + f(n)
    e.g. mergesort     T(n) = 2T(n/2) + O(n) = O(n log n)
         binary search T(n) = T(n/2)   + O(1) = O(log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 베이스 케이스 | 더 이상 재귀하지 않고 끝나는 종료 조건 |
| 호출 스택 | 중첩된 함수 호출 문맥이 쌓이는 구조 |
| 분할 정복 | divide → conquer → combine 패턴 |
| 점화식 | 재귀 비용을 표현하는 식 |
| 메모이제이션 | 반복되는 부분 문제 결과를 캐싱하는 기법 |

## Before / After

**Before — 베이스 케이스 누락:**

```python
def factorial(n):
    return n * factorial(n - 1)        # no termination → RecursionError
```

**After — 명시적 베이스 케이스:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## 단계별로 따라가기

### 1단계: 재귀의 세 가지 규칙

```python
def power(base, exp):
    if exp == 0:                           # (1) base case
        return 1
    return base * power(base, exp - 1)     # (2) smaller input (3) self-call

print(power(2, 10))   # 1024
```

베이스 케이스는 실제로 도달 가능해야 하고, 모든 호출은 그쪽으로 엄격하게 가까워져야 합니다.

### 2단계: 호출 스택과 `RecursionError`

```python
import sys
print(sys.getrecursionlimit())     # 1000 by default

def deep(n):
    if n == 0:
        return 0
    return 1 + deep(n - 1)

try:
    deep(2000)
except RecursionError as e:
    print("RecursionError:", e)

sys.setrecursionlimit(10_000)
print(deep(2000))
```

CPython에는 tail-call optimisation이 없습니다. 깊은 재귀는 한도를 높이거나 반복문으로 바꿔야 합니다.

### 3단계: 분할 정복 거듭제곱, O(n) → O(log n)

```python
def fast_power(base, exp):
    if exp == 0:
        return 1
    half = fast_power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

print(fast_power(2, 30))   # 1073741824
```

지수를 절반으로 줄이면 호출 수가 O(log n)이 됩니다. 암호학의 modular exponentiation에서도 같은 아이디어를 씁니다.

### 4단계: Mergesort로 점화식 체감하기

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

print(mergesort([3, 1, 4, 1, 5, 9, 2, 6]))
```

`T(n) = 2T(n/2) + O(n)`이 O(n log n)이 되는 가장 친숙한 예입니다.

### 5단계: 반복 부분 문제에서 메모이제이션으로

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)
# Same subproblems repeated exponentially, very slow

from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(100))
```

캐싱을 추가하면 O(2^n)이 O(n)으로 무너집니다. 바로 다음 글인 동적 계획법으로 이어지는 핵심 전환점입니다.

## 이 글에서 먼저 가져갈 점

- 베이스 케이스가 실제로 도달 가능한지 항상 확인해야 합니다.
- 결합 비용 `f(n)`이 전체 복잡도를 지배할 수 있습니다.
- 반복 부분 문제를 발견하면 큰 폭의 최적화 기회가 생깁니다.
- Python의 깊은 재귀는 종종 반복문으로 바꿔야 합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 베이스 케이스가 없거나 도달 불가 | 무한 재귀 | 입력이 단조롭게 줄어드는지 확인합니다 |
| 가변 객체를 호출 간 공유 | 의도치 않은 누적 | 복사하거나 인덱스를 전달합니다 |
| Python에서 깊은 재귀를 그대로 사용 | `RecursionError` | 반복문으로 바꾸거나 한도를 조정합니다 |
| 분할 비율 `b`를 무시 | 복잡도 오판 | 점화식으로 적고 읽습니다 |
| 반복 부분 문제를 놓침 | 지수 시간 | `lru_cache` 같은 메모이제이션을 추가합니다 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템 재귀 순회
- 컴파일러 AST 순회와 변환
- 분산 reduce 단계의 k-way 병합
- 그래픽스의 quadtree, octree
- 결정 트리 학습의 재귀적 분할

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 문제가 자연스럽게 트리 구조를 가지면 재귀를 택하고, 깊은 선형 체인이라면 반복을 더 선호합니다. 표현력과 성능을 함께 보되, 성능 민감한 경로에서는 명시적 스택을 가진 반복 구현을 먼저 고려합니다.

또한 분할 정복을 보면 머릿속에서 바로 점화식을 그립니다. `T(n)=2T(n/2)+O(n)`은 O(n log n), `T(n)=T(n/2)+O(1)`은 O(log n)이라는 감각만 있어도 실전 분석의 상당수를 커버할 수 있습니다.

## 체크리스트

- [ ] 재귀의 세 가지 규칙을 점검할 수 있는가
- [ ] `RecursionError`가 무엇을 의미하는지 아는가
- [ ] 분할 정복 루틴의 점화식을 쓸 수 있는가
- [ ] 반복 부분 문제를 알아볼 수 있는가
- [ ] 깊은 재귀를 반복문으로 바꿀 수 있는가

## 연습 문제

1. 정수 배열의 합을 분할 정복으로 계산하고, 단순 반복과 비교해 보세요. 점화식과 복잡도도 함께 적어 보세요.

2. 두 정렬 리스트의 교집합을 재귀적으로 구해 보고, 두 리스트 크기가 크게 다를 때는 이진 탐색으로 어떻게 개선할 수 있는지 설명해 보세요.

3. 하노이 탑을 재귀로 풀고, 호출 횟수가 `2^n - 1`이 되는 이유를 점화식으로 증명해 보세요.

## 정리 및 다음 단계

재귀는 문제를 더 작은 자기 자신으로 표현하는 방식입니다. 분할 정복은 그중 가장 유용한 패턴이며, 비용은 점화식으로 분석합니다. 부분 문제가 반복되면 메모이제이션이 필요해지고, 바로 그 지점에서 동적 계획법으로 자연스럽게 이어집니다.

다음 글에서는 동적 계획법을 본격적으로 다룹니다. 메모이제이션과 타뷸레이션, 상태 설계, 그리고 0/1 knapsack과 LCS 같은 대표 문제를 살펴보겠습니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- **재귀와 분할 정복 (현재 글)**
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Python `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Wikipedia — Master theorem](https://en.wikipedia.org/wiki/Master_theorem)
- [CLRS — Introduction to Algorithms, Chapter 4](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 재귀, 분할 정복, 호출 스택, 메모이제이션
