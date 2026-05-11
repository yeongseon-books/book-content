---
series: algorithms-101
episode: 5
title: 재귀와 분할 정복
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
  - 재귀
  - 분할 정복
  - 호출 스택
  - 메모이제이션
seo_description: 재귀의 정의와 호출 스택, 분할 정복의 사고 패턴, 점화식으로 비용을 분석하는 법, 그리고 메모이제이션의 출발점을 정리합니다.
last_reviewed: '2026-05-04'
---

# 재귀와 분할 정복

> Algorithms 101 시리즈 (5/10)


## 이 글에서 다룰 문제

재귀를 자유롭게 다루지 못하면 트리·그래프 알고리즘, 분할 정복, 동적 계획법, 백트래킹 모두 어렵게 느껴집니다. 반대로 재귀의 사고 모델이 자리 잡으면 복잡한 문제를 "원래 문제와 같은 형태의 더 작은 문제"로 자연스럽게 분해할 수 있습니다.

> 재귀는 알고리즘의 두 번째 모국어입니다.

## 전체 흐름
> 재귀 함수는 베이스 케이스 + 진행 단계 + 자기 호출의 세 부분으로 구성됩니다. 분할 정복은 입력을 a개의 크기 n/b 부분 문제로 나누고 결합 비용 f(n)을 더한 것입니다. 점화식 T(n) = a·T(n/b) + f(n)으로 표현하며 마스터 정리로 비용을 가늠합니다.

```text
재귀 구조
    if 베이스 케이스: return
    재귀 호출(더 작은 입력)
    결과 결합

분할 정복 점화식
    T(n) = a · T(n/b) + f(n)
    예: mergesort  T(n) = 2T(n/2) + O(n) = O(n log n)
        binary search T(n) = T(n/2) + O(1) = O(log n)
```

## Before / After

**Before — 베이스 케이스 누락:**

```python
def factorial(n):
    return n * factorial(n - 1)        # 종료 조건 없음 → RecursionError
```

**After — 베이스 케이스 명시:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## 단계별로 따라하기

### 1단계: 재귀의 세 가지 조건 확인

```python
def power(base, exp):
    if exp == 0:                    # (1) 베이스 케이스
        return 1
    return base * power(base, exp - 1)   # (2) 더 작은 입력 (3) 자기 호출

print(power(2, 10))   # 1024
```

베이스 케이스가 도달 가능해야 하고, 매 호출마다 입력이 베이스에 가까워져야 합니다.

### 2단계: 호출 스택과 RecursionError

```python
import sys
print(sys.getrecursionlimit())     # 기본 1000

def deep(n):
    if n == 0:
        return 0
    return 1 + deep(n - 1)

try:
    deep(2000)
except RecursionError as e:
    print("RecursionError:", e)

sys.setrecursionlimit(10_000)
print(deep(2000))   # 2000
```

CPython의 호출 스택 한계는 기본 1000 프레임입니다. 큰 깊이가 필요하면 한도를 늘리거나 반복문으로 바꾸어야 합니다.

### 3단계: 분할 정복으로 거듭제곱 — O(n) → O(log n)

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

지수를 절반씩 줄이는 분할 정복으로 호출 횟수가 O(log n)이 됩니다. 큰 지수의 모듈러 거듭제곱(암호학)에서 그대로 쓰입니다.

### 4단계: mergesort로 분할 정복 점화식 체험

```python
def mergesort(arr):
    if len(arr) <= 1:                          # 베이스
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])                # divide
    right = mergesort(arr[mid:])
    return merge(left, right)                  # combine

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

T(n) = 2T(n/2) + O(n) → O(n log n). 분할 정복의 가장 친숙한 예입니다.

### 5단계: 같은 부분 문제 발견 — 메모이제이션의 시작

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# 같은 부분 문제가 지수적으로 반복 → 매우 느림

from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(100))   # 354224848179261915075
```

같은 입력이 여러 번 호출된다면 캐싱하여 O(2^n) → O(n)으로 줄일 수 있습니다. 다음 글의 동적 계획법으로 자연스럽게 이어집니다.

## 이 코드에서 주목할 점

- 베이스 케이스가 진짜로 도달 가능한지 항상 점검
- 분할 정복의 결합 비용 f(n)이 전체 복잡도를 결정할 수 있음
- 같은 부분 문제 발견 → 캐싱으로 차원이 다른 속도 향상
- CPython은 꼬리 호출 최적화가 없으므로 깊은 재귀는 반복문 고려

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 베이스 케이스 누락/도달 불가 | 무한 재귀 | 입력 감소 단조성 점검 |
| 가변 객체를 재귀 인자로 공유 | 의도치 않은 누적 | 호출마다 사본 또는 인덱스 전달 |
| Python에서 깊은 재귀 그대로 사용 | RecursionError | 반복문 또는 limit 상향 |
| 분할 비율 b 분석 누락 | 잘못된 복잡도 추정 | 점화식과 마스터 정리로 확인 |
| 같은 부분 문제 반복을 못 봄 | 지수 시간 | `lru_cache`로 메모이제이션 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템 트리 순회 (디렉터리 재귀 탐색)
- 컴파일러의 추상 구문 트리(AST) 처리
- 분산 시스템의 reduce 단계 (k-way 병합)
- 그래픽스의 quadtree, octree 분할
- 머신러닝의 결정 트리 학습 (재귀적 분할)

## 체크리스트

- [ ] 재귀의 세 가지 조건을 점검할 수 있는가
- [ ] 호출 스택과 RecursionError의 의미를 이해하는가
- [ ] 분할 정복의 점화식을 쓸 수 있는가
- [ ] 같은 부분 문제 반복을 알아볼 수 있는가
- [ ] 깊은 재귀를 반복문으로 바꿀 수 있는가

## 정리 및 다음 단계

재귀는 자기 자신과 같은 형태의 더 작은 문제로 표현하는 기법이며, 분할 정복은 그 대표적 사고 패턴입니다. 점화식으로 비용을 분석하고, 같은 부분 문제가 반복되면 메모이제이션으로 진화시킵니다. 이 진화의 끝에 동적 계획법이 있습니다.

다음 글에서는 동적 계획법(DP)을 살펴봅니다. 메모이제이션과 타뷸레이션의 차이, 상태 정의의 기술, 그리고 고전 DP 문제(피보나치, knapsack, 최장 공통 부분 수열)를 다룹니다.

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
