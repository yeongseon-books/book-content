---
series: algorithms-101
episode: 4
title: 정렬 알고리즘
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
  - 정렬
  - 퀵소트
  - 머지소트
  - Timsort
seo_description: mergesort·quicksort·heapsort의 트레이드오프와 Timsort의 실전 동작을 정리합니다.
last_reviewed: '2026-05-11'
---

# 정렬 알고리즘

정렬은 뒤에 오는 거의 모든 처리의 비용을 결정하는 전처리입니다. 어떤 정렬을 고르느냐에 따라 메모리 사용량, 안정성, 최악 시간까지 함께 달라집니다.

이 글은 Algorithms 101 시리즈의 4번째 글입니다. 여기서는 mergesort·quicksort·heapsort의 트레이드오프와 Timsort의 실전 동작을 함께 살펴봅니다.

## 이 글에서 다룰 문제

정렬은 거의 모든 시스템의 기본 도구입니다. 인덱스 빌드, 배치 처리, 데이터베이스 조인, 윈도우 집계, 머신러닝 데이터 전처리까지 많은 작업이 정렬을 바탕으로 돌아갑니다. 정렬 알고리즘의 트레이드오프를 모르면 뒤이어 오는 알고리즘의 비용도 정확히 가늠하기 어렵습니다.

> 정렬을 이해한다는 것은 알고리즘 설계의 첫 어휘를 익히는 일입니다.

## 전체 흐름
> 비교 기반 정렬은 비교의 결정 트리 깊이가 log(n!) ≈ n log n이므로 O(n log n)이 하한입니다. mergesort는 분할 정복으로 안정·O(n) 추가 메모리, quicksort는 in-place·평균 O(n log n)·최악 O(n²), heapsort는 in-place·O(n log n)·비안정. Timsort는 mergesort에 부분 정렬 탐지를 결합한 적응형 정렬입니다.

```text
비교 기반 정렬 하한: O(n log n)

mergesort   : 안정,  추가 메모리 O(n),  보장 O(n log n)
quicksort   : 비안정, in-place,         평균 O(n log n) / 최악 O(n²)
heapsort    : 비안정, in-place,         보장 O(n log n)
Timsort     : 안정,  적응형,            최선 O(n) / 최악 O(n log n)
```

## Before / After

Before — 손으로 짠 quicksort, 최악 입력에 약합니다.

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    return quicksort(left) + [pivot] + quicksort(right)
# 이미 정렬된 입력에서 O(n²)
```

After — 표준 `sorted`를 사용합니다.

```python
sorted_arr = sorted(arr)        # Timsort, 안정, 적응형
arr.sort()                      # in-place 변형
```

## 단계별로 따라하기

### 1단계: mergesort 구현

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
# [1, 1, 2, 3, 4, 5, 6, 9]
```

mergesort는 분할 정복의 교과서 같은 알고리즘입니다. 안정 정렬이며 O(n log n) 성능을 안정적으로 보장합니다. 대신 O(n)의 추가 메모리가 필요합니다.

### 2단계: quicksort와 pivot 전략

```python
import random

def quicksort_inplace(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot_idx = random.randint(lo, hi)        # 랜덤 피벗
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

피벗을 첫 원소로 고정하면 이미 정렬된 입력에서 O(n²)까지 무너질 수 있습니다. 그래서 실무에서는 랜덤 피벗이나 median-of-three 같은 방어 전략을 함께 사용합니다.

### 3단계: heapsort 구현

```python
import heapq

def heapsort(arr):
    h = list(arr)
    heapq.heapify(h)                # O(n)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heapsort([3, 1, 4, 1, 5, 9, 2, 6]))
```

표준 라이브러리의 heap을 활용하면 O(n log n)을 안정적으로 얻을 수 있습니다. 안정 정렬은 아니지만 추가 메모리가 비교적 적고 최악 시간도 보장됩니다.

### 4단계: Timsort의 부분 정렬 적응성 확인

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
# 이미 정렬된 경우와 거의 정렬된 경우가 훨씬 빠름
```

Timsort는 부분 정렬된 run을 탐지해 병합 단계를 줄입니다. 실무 데이터는 완전한 무작위인 경우가 드물기 때문에, 이런 적응성이 실제 성능 차이로 이어집니다.

### 5단계: 안정 정렬을 활용한 다중 키 정렬

```python
people = [
    ("Alice", 30), ("Bob", 25), ("Carol", 30), ("Dan", 25),
]
# 1차: 이름 오름차순, 2차: 나이 오름차순
people.sort(key=lambda p: p[0])
people.sort(key=lambda p: p[1])
print(people)
# [('Bob', 25), ('Dan', 25), ('Alice', 30), ('Carol', 30)]
```

안정 정렬을 보조키에서 주키 순으로 두 번 적용하면 다중 키 정렬을 간결하게 표현할 수 있습니다. 파이썬의 Timsort가 안정 정렬이기 때문에 가능한 패턴입니다.

## 이 코드에서 주목할 점

- mergesort는 안정·보장 O(n log n)·O(n) 메모리
- quicksort는 평균은 빠르지만 피벗 전략이 없으면 위험
- heapsort는 보장 시간이 필요할 때 유용
- Timsort는 적응성과 안정성을 동시에 가진 실용적 선택

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정렬 후 별도 인덱스를 손으로 관리 | 동기화 버그 | `sorted(..., key=..., reverse=...)` 활용 |
| quicksort에 첫 원소 피벗 | 정렬 입력에서 O(n²) | 랜덤·median-of-three |
| 안정성 가정 없이 다중 정렬 | 결과 비결정성 | Timsort/`sort()`는 안정 |
| 큰 데이터 메모리 정렬 | OOM | external sort, 분할 처리 |
| 비교 함수 부작용 | 비교 결과 비일관 | key 함수로 추출 후 비교 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 ORDER BY와 인덱스 빌드의 내부 정렬
- 로그 파이프라인의 시간순 병합 (k-way merge)
- 검색 엔진의 결과 점수 정렬
- 추천 시스템의 후보 랭킹
- 머신러닝 데이터 분할에서 stratified sampling 전 정렬

## 체크리스트

- [ ] 비교 기반 정렬의 하한 O(n log n)을 이해하는가
- [ ] mergesort/quicksort/heapsort의 트레이드오프를 말할 수 있는가
- [ ] 안정 정렬의 의미와 효용을 이해하는가
- [ ] Timsort가 빠른 이유를 설명할 수 있는가
- [ ] "정렬이 정말 필요한가"를 먼저 묻는가

## 정리 및 다음 단계

정렬 알고리즘은 같은 점근 복잡도 안에서도 안정성, 메모리 사용량, 적응성에서 차이가 납니다. 파이썬의 `sorted`는 실무 데이터에 강한 Timsort를 사용하므로, 대부분의 경우에는 표준 구현을 그대로 쓰고 트레이드오프가 분명할 때만 다른 정렬을 검토하면 됩니다.

다음 글에서는 재귀와 분할 정복을 살펴봅니다. 재귀의 정의, 호출 스택, 분할 정복의 사고 패턴, 그리고 메모이제이션의 출발점까지 함께 정리하겠습니다.

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
