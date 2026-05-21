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

재귀는 왜 어렵게 느껴질까요? 그리고 mergesort 같은 분할 정복 알고리즘은 왜 "올바른 이유로" 빠를까요? 이 글은 Algorithms 101 시리즈의 다섯 번째 글입니다. 여기서는 호출 스택, 점화식 기반 비용 분석, 그리고 분할 정복의 핵심 멘탈 모델을 정리합니다.

## 먼저 던지는 질문

- 올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?
- 호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?
- 분할 정복 점화식은 어떻게 읽어야 할까요?

## 큰 그림

![Algorithms 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/05/05-01-big-picture.ko.png)

*Algorithms 101 5장 흐름 개요*

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


## 추가 실전 섹션: 복잡도·추적·구현 선택을 한 번에 연결하기

알고리즘 학습에서 가장 중요한 전환점은 "개념 이해"와 "문제 풀이" 사이를 잇는 기준을 갖는 것입니다. 아래 표는 정렬·탐색·재귀·DP·그리디·그래프·문자열 문제를 만났을 때 가장 먼저 결정해야 할 선택지를 한눈에 정리한 것입니다.

| 문제 신호 | 1차 후보 | 시간 복잡도 목표 | 확인할 함정 |
| --- | --- | --- | --- |
| 정렬 여부가 핵심 단서 | 이진 탐색 / bisect | O(log n) | 데이터 정렬 전제 누락 |
| 전체 순위가 필요 | 정렬(Timsort/merge) | O(n log n) | 안정 정렬 필요 여부 |
| 상위 k개만 필요 | heap | O(n log k) | 전체 정렬로 과투자 |
| 부분 문제가 반복 | DP | O(states * transition) | 상태 정의 모호 |
| 즉시 최선 선택이 유력 | 그리디 | 보통 O(n log n) 이하 | 교환 논증 부재 |
| 연결·최단·순서 제약 | 그래프(BFS/DFS/다익스트라) | O(V+E), O((V+E)logV) | 가중치 조건 혼동 |
| 긴 텍스트 패턴 검색 | KMP/Trie | O(n+m) | 정규식 백트래킹 비용 |

### 추적 예시 1: 이진 탐색 경계 버그를 잡는 로그

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    trace = []
    while lo < hi:
        mid = (lo + hi) // 2
        trace.append((lo, mid, hi, arr[mid]))
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo, trace

pos, trace = lower_bound([1, 2, 2, 2, 5, 9], 2)
print(pos)
for t in trace:
    print(t)
```

이런 추적은 오프바이원 버그를 빠르게 드러냅니다. 특히 `lo`, `hi` 경계 갱신이 틀렸을 때 무한 루프가 나는 문제는 값만 출력하는 디버깅보다 경계 튜플을 기록하는 편이 더 효율적입니다.

### 추적 예시 2: 정렬 알고리즘 선택 비교

| 입력 특성 | `sorted`(Timsort) | 직접 quicksort | heap 기반 |
| --- | --- | --- | --- |
| 이미 거의 정렬 | 매우 강함(run 활용) | pivot 품질에 따라 흔들림 | 순위 작업에서는 유리 |
| 무작위 대량 데이터 | 안정적 | 평균은 빠르지만 편차 존재 | top-k에 특화 |
| 다중 키 정렬 | 안정성 덕분에 단순 | 구현 복잡 | 부분 순위만 적합 |

실무에서는 "직접 구현"보다 "표준 라이브러리 + 문제 특화 자료구조" 조합이 장기 유지보수에 유리합니다. 코드 길이가 아니라 오류 가능성과 운영 신뢰성이 핵심 기준입니다.

### 문제 풀이 루틴: 5분 점검

1. 입력 크기로 불가능한 차수(O(n^2), O(2^n) 등)를 먼저 제거합니다.
2. 전제(정렬됨, DAG, 음수 가중치 없음, 중복 허용)를 명시합니다.
3. 템플릿(이진 탐색, BFS, DP 상태 전이)을 선택합니다.
4. 작은 반례 2개를 직접 넣어 경계 동작을 확인합니다.
5. 마지막에 복잡도와 메모리 사용량을 한 줄로 기록합니다.

이 루틴을 습관화하면 "코드가 돌아간다"와 "운영에서도 안전하다" 사이의 간격이 크게 줄어듭니다.



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

## 처음 질문으로 돌아가기

- **올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?**
  - 본문의 기준은 재귀와 분할 정복를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **분할 정복 점화식은 어떻게 읽어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
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
