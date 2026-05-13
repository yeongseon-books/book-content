---
series: algorithms-101
episode: 4
title: 정렬 알고리즘
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
  - 정렬
  - 퀵소트
  - 머지소트
  - Timsort
seo_description: 비교 기반 정렬의 하한과 대표 정렬 알고리즘의 트레이드오프, Timsort의 강점을 정리합니다.
last_reviewed: '2026-05-12'
---

# 정렬 알고리즘

Python의 `sorted`는 왜 그렇게 안정적으로 빠를까요? 그리고 교과서의 quicksort가 놓치는 것은 무엇일까요? 이 글은 Algorithms 101 시리즈의 네 번째 글입니다. 여기서는 대표 정렬 알고리즘의 트레이드오프와 Timsort가 실무에서 자주 이기는 이유를 다룹니다.

## 이 글에서 다룰 문제

- 비교 기반 정렬은 왜 O(n log n)보다 더 좋아질 수 없을까요?
- mergesort, quicksort, heapsort는 각각 무엇을 주고 무엇을 얻을까요?
- 안정 정렬과 비안정 정렬의 차이는 왜 중요할까요?
- Timsort는 실제 데이터에서 왜 자주 이길까요?

## 왜 중요한가

정렬은 거의 모든 다른 알고리즘의 전처리 단계입니다. 인덱스 생성, 배치 처리, 조인, 윈도우 집계, 머신러닝 전처리까지 모두 정렬 위에서 돌아갑니다. 어떤 정렬이 앞에 오는지가 뒤쪽 파이프라인 전체 비용을 좌우합니다.

> 정렬을 이해하는 일은 알고리즘 설계의 첫 번째 어휘를 익히는 일입니다.

## 한눈에 보는 개념

> 비교 기반 정렬의 결정 트리 깊이는 `log(n!) ≈ n log n`이므로 O(n log n)이 하한입니다. mergesort는 안정 정렬이고 O(n) 추가 메모리를 쓰며 O(n log n)을 보장합니다. quicksort는 제자리 정렬이고 평균 O(n log n)이지만 나쁜 pivot에서는 O(n²)로 무너집니다. heapsort는 제자리 정렬이며 O(n log n)을 보장하지만 안정적이지 않습니다. Timsort는 mergesort 위에 run 탐지를 얹은 적응형 정렬입니다.

```text
Lower bound for comparison sorting: O(n log n)

mergesort   stable,   O(n) extra memory,  guaranteed O(n log n)
quicksort   unstable, in-place,           average O(n log n) / worst O(n^2)
heapsort    unstable, in-place,           guaranteed O(n log n)
Timsort     stable,   adaptive,           best O(n) / worst O(n log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 비교 기반 정렬 | 원소끼리 비교해 순서를 정하는 정렬 |
| 안정 정렬 | 같은 키의 상대적 순서를 보존하는 정렬 |
| 제자리 정렬 | 추가 메모리를 거의 쓰지 않는 정렬 |
| 적응형 정렬 | 이미 어느 정도 정렬된 입력에서 더 빨라지는 정렬 |
| Timsort | mergesort와 run 탐지를 결합한 Python 표준 정렬 |

## Before / After

**Before — 손으로 짠 quicksort, 나쁜 입력에 취약:**

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    return quicksort(left) + [pivot] + quicksort(right)
# O(n^2) on already-sorted input
```

**After — 표준 라이브러리 사용:**

```python
sorted_arr = sorted(arr)        # Timsort, stable, adaptive
arr.sort()                      # in-place variant
```

## 단계별로 따라가기

### 1단계: Mergesort

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

전형적인 분할 정복 정렬입니다. 안정적이고 O(n log n)을 보장하지만 O(n) 추가 메모리를 지불합니다.

### 2단계: 랜덤 pivot을 쓰는 Quicksort

```python
import random

def quicksort_inplace(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot_idx = random.randint(lo, hi)
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    quicksort_inplace(arr, lo, i - 1)
    quicksort_inplace(arr, i + 1, hi)

a = [3, 1, 4, 1, 5, 9, 2, 6]
quicksort_inplace(a)
print(a)
```

첫 원소를 pivot으로 고정하면 이미 정렬된 입력에서 O(n²)까지 무너질 수 있습니다. 그래서 랜덤 pivot이나 median-of-three 같은 방어가 사실상 표준입니다.

### 3단계: Heapsort

```python
import heapq

def heapsort(arr):
    h = list(arr)
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heapsort([3, 1, 4, 1, 5, 9, 2, 6]))
```

안정 정렬은 아니지만 O(n log n)을 보장하고 추가 메모리도 mergesort보다 적습니다. 최악 시간 보장이 필요할 때 의미가 큽니다.

### 4단계: Timsort의 적응성 관찰

```python
import random, time

def measure(arr):
    t = time.perf_counter()
    sorted(arr)
    return time.perf_counter() - t

n = 1_000_000
random_arr = [random.random() for _ in range(n)]
sorted_arr = sorted(random_arr)
nearly_sorted = sorted_arr[:]
for _ in range(100):
    i = random.randrange(n); j = random.randrange(n)
    nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]

print(f"random        : {measure(random_arr):.3f}s")
print(f"already sorted: {measure(sorted_arr):.3f}s")
print(f"nearly sorted : {measure(nearly_sorted):.3f}s")
```

Timsort는 이미 존재하는 run을 감지해 싸게 병합합니다. 실전 데이터는 완전 난수보다 부분 정렬된 경우가 많기 때문에, 바로 여기서 성능 이득이 납니다.

### 5단계: 안정성을 이용한 다중 키 정렬

```python
people = [
    ("Alice", 30), ("Bob", 25), ("Carol", 30), ("Dan", 25),
]
people.sort(key=lambda p: p[0])     # secondary
people.sort(key=lambda p: p[1])     # primary
print(people)
```

안정 정렬이면 보조 키부터 먼저 정렬한 뒤 주 키를 정렬해 다중 키 정렬을 간결하게 표현할 수 있습니다. Python의 Timsort가 안정 정렬이기 때문에 가능한 패턴입니다.

## 이 글에서 먼저 가져갈 점

- mergesort는 안정성과 보장을 주는 대신 메모리를 더 씁니다.
- quicksort는 평균적으로 빠르지만 pivot 방어가 없으면 위험합니다.
- heapsort는 메모리를 아끼며 최악 시간 보장을 제공합니다.
- Timsort는 안정성과 현실 데이터 적응성을 함께 가져갑니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 별도 인덱스를 손으로 맞추며 정렬 | 동기화 버그 | `sorted(..., key=..., reverse=...)`를 활용합니다 |
| 첫 원소 pivot quicksort 고집 | 정렬 입력에서 O(n²) | 랜덤 또는 median-of-three를 씁니다 |
| 안정성 가정 없이 다중 키 정렬 | 결과 비결정성 | 안정 정렬인지 먼저 확인합니다 |
| 아주 큰 데이터를 메모리에서 통째로 정렬 | OOM | 외부 병합 정렬이나 청크 처리를 검토합니다 |
| 부작용이 있는 comparator 사용 | 비교 결과 불일치 | key 함수로 값만 뽑아 비교합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 `ORDER BY`와 인덱스 생성은 내부적으로 정렬을 사용합니다.
- 로그 파이프라인은 시간순 스트림을 k-way merge로 합칩니다.
- 검색 엔진은 후보를 점수 순으로 정렬합니다.
- 추천 시스템은 후보 순위를 매깁니다.
- ML 파이프라인은 stratified sampling 전에 정렬을 사용하기도 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "정말 전체 정렬이 필요한가"를 묻습니다. 상위 k개만 필요하다면 힙으로 O(n log k)에 끝낼 수 있고, 특정 순위 하나만 필요하다면 quickselect처럼 O(n)에 가까운 선택 알고리즘이 더 적절할 수 있습니다.

또한 "메모리에 들어가는가"를 빠르게 확인합니다. 데이터가 RAM을 넘는 순간부터는 외부 병합 정렬과 분산 셔플 비용이 알고리즘 자체보다 더 큰 문제가 되기 때문입니다.

## 체크리스트

- [ ] 비교 기반 정렬의 O(n log n) 하한을 설명할 수 있는가
- [ ] mergesort, quicksort, heapsort의 트레이드오프를 말할 수 있는가
- [ ] 안정 정렬의 의미와 효용을 이해하는가
- [ ] Timsort가 실전 데이터에서 빠른 이유를 설명할 수 있는가
- [ ] 전체 정렬이 정말 필요한지 먼저 묻는가

## 연습 문제

1. 단어 목록을 길이 오름차순으로 정렬하되 길이가 같으면 사전순으로 정렬해 보세요. Timsort의 안정성을 활용하면 한 줄로 표현할 수 있습니다.

2. `heapq.nlargest`를 직접 구현해 보세요. 리스트와 k가 주어졌을 때 O(n log k)로 상위 k개를 반환하고, 왜 전체 정렬보다 유리한지 설명해 보세요.

3. 메모리에 다 들어가지 않는 10^8개의 정수에 대해 external mergesort를 스케치해 보세요. 디스크 I/O 패스가 몇 번 필요한지도 추정해 보세요.

## 정리 및 다음 단계

같은 O(n log n) 울타리 안에서도 정렬 알고리즘은 안정성, 메모리, 적응성에서 큰 차이를 보입니다. 기본 선택은 `sorted`와 `sort()`이고, 트레이드오프가 분명할 때만 다른 정렬을 검토하면 됩니다.

다음 글에서는 재귀와 분할 정복을 다룹니다. 호출 스택, 점화식, 그리고 분할 정복에서 동적 계획법으로 이어지는 사고 흐름을 살펴보겠습니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- **정렬 알고리즘 (현재 글)**
- 재귀와 분할 정복 (예정)
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `sorted` documentation](https://docs.python.org/3/library/functions.html#sorted)
- [Python sort how-to](https://docs.python.org/3/howto/sorting.html)
- [Tim Peters — Timsort listsort.txt](https://github.com/python/cpython/blob/main/Objects/listsort.txt)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 2](https://algs4.cs.princeton.edu/20sorting/)

Tags: Computer Science, 알고리즘, 정렬, 퀵소트, 머지소트, Timsort
