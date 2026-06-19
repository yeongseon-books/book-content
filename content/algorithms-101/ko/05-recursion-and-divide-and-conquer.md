---
series: algorithms-101
episode: 5
title: "Algorithms 101 (5/10): 재귀와 분할 정복"
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
  - 재귀
  - 분할 정복
  - 호출 스택
  - 메모이제이션
seo_description: 올바른 재귀의 세 가지 규칙, 호출 스택, 분할 정복 점화식, 그리고 메모이제이션으로 이어지는 사고를 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (5/10): 재귀와 분할 정복

재귀는 왜 어렵게 느껴질까요? 그리고 mergesort 같은 분할 정복 알고리즘은 왜 "올바른 이유로" 빠를까요? 여기서는 호출 스택, 점화식 기반 비용 분석, 그리고 분할 정복의 핵심 멘탈 모델을 정리합니다.

이 글은 Algorithms 101 시리즈의 5번째 글입니다.

![Algorithms 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/05/05-01-big-picture.ko.png)
*Algorithms 101 5장 흐름 개요*

## 이 글에서 다룰 문제

- 올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?
- 호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?
- 분할 정복 점화식은 어떻게 읽어야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

재귀가 익숙하지 않으면 트리, 그래프, 분할 정복, 동적 계획법, 백트래킹이 모두 더 어렵게 느껴집니다. 반대로 재귀 사고가 자리 잡으면 복잡한 문제를 "자기 자신과 같은 형태의 더 작은 문제"로 자연스럽게 분해할 수 있습니다.

> 재귀는 알고리즘의 두 번째 모국어입니다.

> 재귀 함수는 베이스 케이스, 진행 단계, 자기 호출을 가집니다. 분할 정복은 입력을 크기 `n/b`인 부분 문제 `a`개로 나누고, 결과를 `f(n)` 비용으로 결합합니다. 전체 비용은 `T(n) = a · T(n/b) + f(n)`으로 표현할 수 있고, 대표적으로 mergesort는 O(n log n), binary search는 O(log n)이 됩니다.

```text
Recursive shape
    if base case: return fixed value
    self-call(strictly smaller input)
    combine results

Divide-and-conquer recurrence
    T(n) = a · T(n/b) + f(n)
    mergesort     T(n) = 2T(n/2) + O(n) = O(n log n)
    binary search T(n) = T(n/2)   + O(1) = O(log n)
    fast power    T(n) = T(n/2)   + O(1) = O(log n)
```

| 용어 | 설명 |
| --- | --- |
| 베이스 케이스 | 더 이상 재귀하지 않고 끝나는 종료 조건 |
| 호출 스택 | 중첩된 함수 호출 문맥이 쌓이는 구조 |
| 분할 정복 | divide → conquer → combine 패턴 |
| 점화식 | 재귀 비용을 표현하는 식 |
| 메모이제이션 | 반복되는 부분 문제 결과를 캐싱하는 기법 |

## 개선 전 / 개선 후

**Before — 베이스 케이스 누락:**

```python
def factorial(n):
    return n * factorial(n - 1)   # 종료 조건 없음 → RecursionError
```

**After — 명시적 베이스 케이스:**

```python
def factorial(n):
    if n <= 1:         # 베이스 케이스: 도달 가능하고 자명한 값
        return 1
    return n * factorial(n - 1)   # 입력이 엄격하게 줄어듦

assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120
```

## 단계별로 따라가기

### 1단계: 재귀의 세 가지 규칙

```python
def power(base, exp):
    # 규칙 1: 베이스 케이스 — 가장 단순한 경우
    if exp == 0:
        return 1
    # 규칙 2: 입력이 엄격하게 줄어들어야 함 (exp - 1 < exp)
    # 규칙 3: 자기 호출로 더 작은 문제를 해결
    return base * power(base, exp - 1)

print(power(2, 10))   # 1024

# 베이스 케이스 도달 가능성 확인
# exp=10 → exp=9 → ... → exp=0 (베이스 케이스)
```

베이스 케이스는 실제로 도달 가능해야 하고, 모든 호출은 그쪽으로 엄격하게 가까워져야 합니다.

### 2단계: 호출 스택과 `RecursionError`

```python
import sys
print(sys.getrecursionlimit())   # 기본 1000

def trace_depth(n, depth=0):
    if n == 0:
        print(f"최대 깊이: {depth}")
        return
    trace_depth(n - 1, depth + 1)

trace_depth(10)   # 최대 깊이: 10

try:
    trace_depth(2000)
except RecursionError as e:
    print(f"RecursionError: {e}")

# 한도 조정 (필요할 때만)
sys.setrecursionlimit(10_000)
trace_depth(2000)   # 최대 깊이: 2000
```

CPython에는 tail-call optimisation이 없습니다. 깊은 재귀는 한도를 높이거나 반복문으로 바꿔야 합니다.

### 3단계: 분할 정복 거듭제곱, O(n) → O(log n)

```python
def slow_power(base, exp):
    """O(exp) = O(n) 시간."""
    if exp == 0:
        return 1
    return base * slow_power(base, exp - 1)

def fast_power(base, exp):
    """분할 정복으로 O(log exp) = O(log n) 시간."""
    if exp == 0:
        return 1
    half = fast_power(base, exp // 2)
    if exp % 2 == 0:
        return half * half            # exp = 2k: base^(2k) = (base^k)^2
    return half * half * base         # exp = 2k+1: base^(2k+1) = (base^k)^2 * base

import time

base, exp = 2, 100_000
t0 = time.perf_counter()
slow_power(base, exp)
t1 = time.perf_counter()
fast_power(base, exp)
t2 = time.perf_counter()
print(f"slow: {(t1-t0)*1000:.1f}ms, fast: {(t2-t1)*1000:.1f}ms")
```

지수를 절반으로 줄이면 호출 수가 O(log n)이 됩니다. 점화식은 `T(n) = T(n/2) + O(1)` → O(log n).

### 4단계: Mergesort로 점화식 체감하기

```python
def mergesort(arr):
    """T(n) = 2T(n/2) + O(n) → O(n log n)."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])    # T(n/2)
    right = mergesort(arr[mid:])   # T(n/2)
    return merge(left, right)      # O(n) — 결합 비용

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

result = mergesort([3, 1, 4, 1, 5, 9, 2, 6])
print(result)   # [1, 1, 2, 3, 4, 5, 6, 9]
```

`T(n) = 2T(n/2) + O(n)`이 O(n log n)이 되는 가장 친숙한 예입니다. log n 층이 있고 각 층의 총 작업량이 O(n)이므로 전체가 O(n log n)입니다.

### 5단계: 반복 부분 문제에서 메모이제이션으로

```python
def fib_naive(n, calls=[0]):
    calls[0] += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

calls = [0]
def fib_count(n, c):
    c[0] += 1
    if n <= 1:
        return n
    return fib_count(n - 1, c) + fib_count(n - 2, c)

c = [0]
fib_count(30, c)
print(f"fib(30) without cache: {c[0]} calls")   # 2,692,537 calls

from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(100))   # 354224848179261915075 — 순식간에
```

캐싱을 추가하면 O(2^n)이 O(n)으로 무너집니다. 바로 다음 글인 동적 계획법으로 이어지는 핵심 전환점입니다.

### 6단계: 재귀를 반복문으로 변환

```python
# 재귀 피보나치 → 반복 피보나치
def fib_iterative(n):
    """O(n) 시간, O(1) 공간 — 깊은 재귀 없음."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# 재귀 트리 순회 → 명시적 스택 반복 순회
def dfs_iterative(adj, start):
    """DFS를 명시적 스택으로 구현."""
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
    return order
```

## 분할 정복 알고리즘 Big-O 비교

| 알고리즘 | 점화식 | 시간 복잡도 | 공간 복잡도 | 특징 |
| --- | --- | --- | --- | --- |
| Binary search | T(n) = T(n/2) + O(1) | O(log n) | O(log n) 재귀 또는 O(1) 반복 | 정렬 전제 |
| Fast power | T(n) = T(n/2) + O(1) | O(log n) | O(log n) | 암호학 기초 |
| Mergesort | T(n) = 2T(n/2) + O(n) | O(n log n) | O(n) | 안정 정렬 |
| Quicksort (평균) | T(n) = 2T(n/2) + O(n) | O(n log n) | O(log n) | 제자리 |
| Strassen 행렬 곱 | T(n) = 7T(n/2) + O(n²) | O(n^2.807) | O(n²) | 나이브보다 빠름 |
| 카라츠바 곱셈 | T(n) = 3T(n/2) + O(n) | O(n^1.585) | O(n log n) | 큰 수 곱셈 |
| 최근접 점 쌍 | T(n) = 2T(n/2) + O(n log n) | O(n log n) | O(n) | 기하 알고리즘 |

## 이 글에서 먼저 가져갈 점

- 베이스 케이스가 실제로 도달 가능한지 항상 확인해야 합니다.
- 결합 비용 `f(n)`이 전체 복잡도를 지배할 수 있습니다.
- 반복 부분 문제를 발견하면 큰 폭의 최적화 기회가 생깁니다.
- Python의 깊은 재귀는 종종 반복문으로 바꿔야 합니다.
- 점화식을 쓰면 복잡도를 기계적으로 읽을 수 있습니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 베이스 케이스가 없거나 도달 불가 | 무한 재귀 | 입력이 단조롭게 줄어드는지 확인합니다 |
| 가변 객체를 호출 간 공유 | 의도치 않은 누적 | 복사하거나 인덱스를 전달합니다 |
| Python에서 깊은 재귀를 그대로 사용 | RecursionError | 반복문으로 바꾸거나 한도를 조정합니다 |
| 점화식 없이 복잡도를 직관으로 추정 | 오판 | 점화식으로 적고 Master theorem을 적용합니다 |
| 반복 부분 문제를 놓침 | 지수 시간 | `lru_cache` 같은 메모이제이션을 추가합니다 |
| 재귀 함수에 가변 기본 인자 사용 | 상태 누적 버그 | 기본 인자에 가변 객체를 쓰지 않습니다 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템 재귀 순회
- 컴파일러 AST 순회와 변환
- 분산 reduce 단계의 k-way 병합
- 그래픽스의 quadtree, octree
- 결정 트리 학습의 재귀적 분할
- 병렬 알고리즘의 divide-and-conquer 단계

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 문제가 자연스럽게 트리 구조를 가지면 재귀를 택하고, 깊은 선형 체인이라면 반복을 더 선호합니다. 표현력과 성능을 함께 보되, 성능 민감한 경로에서는 명시적 스택을 가진 반복 구현을 먼저 고려합니다.

또한 분할 정복을 보면 머릿속에서 바로 점화식을 그립니다. `T(n)=2T(n/2)+O(n)`은 O(n log n), `T(n)=T(n/2)+O(1)`은 O(log n)이라는 감각만 있어도 실전 분석의 상당수를 커버할 수 있습니다.

재귀 함수를 작성할 때는 항상 세 가지를 먼저 적습니다: 베이스 케이스의 조건, 입력이 줄어드는 이유, 결합 단계가 하는 일. 이 세 줄이 명확하면 구현은 거의 자동으로 따라옵니다.

## 운영 체크리스트

- [ ] 재귀의 세 가지 규칙을 점검할 수 있는가
- [ ] RecursionError가 무엇을 의미하는지 아는가
- [ ] 분할 정복 루틴의 점화식을 쓸 수 있는가
- [ ] 반복 부분 문제를 알아볼 수 있는가
- [ ] 깊은 재귀를 반복문으로 바꿀 수 있는가
- [ ] Master theorem의 세 가지 케이스를 구분할 수 있는가

## 연습 문제

1. 정수 배열의 합을 분할 정복으로 계산하고, 단순 반복과 비교해 보세요. 점화식과 복잡도도 함께 적어 보세요.

2. 두 정렬 리스트의 교집합을 재귀적으로 구해 보고, 두 리스트 크기가 크게 다를 때는 이진 탐색으로 어떻게 개선할 수 있는지 설명해 보세요.

3. 하노이 탑을 재귀로 풀고, 호출 횟수가 `2^n - 1`이 되는 이유를 점화식으로 증명해 보세요.

4. `fast_power(base, exp, mod)`를 구현해 모듈러 거듭제곱을 O(log exp)에 계산해 보세요. 왜 암호학에서 이 함수가 필수적인지 설명하세요.

## 정리 및 다음 단계

재귀는 문제를 더 작은 자기 자신으로 표현하는 방식입니다. 분할 정복은 그중 가장 유용한 패턴이며, 비용은 점화식으로 분석합니다. 부분 문제가 반복되면 메모이제이션이 필요해지고, 바로 그 지점에서 동적 계획법으로 자연스럽게 이어집니다.

다음 글에서는 동적 계획법을 본격적으로 다룹니다. 메모이제이션과 타뷸레이션, 상태 설계, 그리고 0/1 knapsack과 LCS 같은 대표 문제를 봅니다.

## 처음 질문으로 돌아가기

- **올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?**
  - 첫째, 베이스 케이스가 존재하고 실제로 도달 가능해야 합니다. 둘째, 재귀 호출의 입력이 베이스 케이스 방향으로 엄격하게 줄어들어야 합니다. 셋째, 더 작은 문제의 해답을 결합해 원래 문제의 해답을 만들어야 합니다.
- **호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?**
  - 함수가 호출될 때마다 매개변수, 지역 변수, 반환 주소가 스택에 쌓입니다. CPython은 기본 1000 깊이 제한을 두고 있으며, 이를 초과하면 RecursionError를 발생시킵니다. 꼬리 재귀 최적화가 없기 때문에 깊은 선형 재귀는 반복문으로 바꿔야 합니다.
- **분할 정복 점화식은 어떻게 읽어야 할까요?**
  - `T(n) = a·T(n/b) + f(n)`에서 a는 부분 문제 수, b는 분할 비율, f(n)은 분할/결합 비용입니다. Master theorem으로 세 케이스를 구분합니다. mergesort의 `T(n) = 2T(n/2) + O(n)`에서 a=2, b=2, f(n)=O(n)이고 n^log_b(a) = n^1 = n이므로 Case 2: O(n log n)입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- **Algorithms 101 (5/10): 재귀와 분할 정복 (현재 글)**
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Python `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Wikipedia — Master theorem](https://en.wikipedia.org/wiki/Master_theorem)
- [CLRS — Introduction to Algorithms, Chapter 4](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 재귀, 분할 정복, 호출 스택, 메모이제이션
