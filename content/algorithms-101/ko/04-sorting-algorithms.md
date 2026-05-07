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
last_reviewed: '2026-05-04'
---

# 정렬 알고리즘

> Algorithms 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 파이썬의 `sorted()`는 왜 거의 항상 빠를까요? 단순한 quicksort와는 무엇이 다를까요?

> 정렬은 거의 모든 알고리즘의 전처리 단계로 등장하는 기본 연산입니다. 비교 기반 정렬은 O(n log n)이 한계이며, mergesort/quicksort/heapsort는 같은 점근 복잡도 안에서 안정성·메모리·캐시 친화성으로 차별화됩니다. 파이썬은 실세계 데이터의 부분 정렬성을 활용하는 Timsort를 표준으로 채택했습니다. "어떤 정렬을 쓰느냐"는 데이터 특성과 외부 제약을 함께 보아야 결정할 수 있습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 비교 기반 정렬의 O(n log n) 하한
- mergesort, quicksort, heapsort의 트레이드오프
- 안정 정렬과 비안정 정렬의 차이
- Timsort가 빠른 이유와 파이썬 sorted의 동작

## 왜 중요한가

정렬은 거의 모든 시스템의 기본 도구입니다. 인덱스 빌드, 배치 처리, 데이터베이스 조인, 윈도우 집계, 머신러닝 데이터 전처리까지 모두 정렬을 깐 위에서 동작합니다. 정렬 알고리즘의 트레이드오프를 모르면 다음 단계 알고리즘의 비용도 가늠할 수 없습니다.

> 정렬을 이해한다는 것은 알고리즘 설계의 첫 어휘를 익힌 것입니다.

## 개념 한눈에 보기

> 비교 기반 정렬은 비교의 결정 트리 깊이가 log(n!) ≈ n log n이므로 O(n log n)이 하한입니다. mergesort는 분할 정복으로 안정·O(n) 추가 메모리, quicksort는 in-place·평균 O(n log n)·최악 O(n²), heapsort는 in-place·O(n log n)·비안정. Timsort는 mergesort에 부분 정렬 탐지를 결합한 적응형 정렬입니다.

```text
비교 기반 정렬 하한: O(n log n)

mergesort   : 안정,  추가 메모리 O(n),  보장 O(n log n)
quicksort   : 비안정, in-place,         평균 O(n log n) / 최악 O(n²)
heapsort    : 비안정, in-place,         보장 O(n log n)
Timsort     : 안정,  적응형,            최선 O(n) / 최악 O(n log n)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 비교 기반 정렬 | 원소 간 비교만으로 순서를 결정 |
| 안정 정렬 | 같은 키의 상대 순서를 보존 |
| in-place | O(1) 추가 메모리만 사용 |
| 적응형 정렬 | 부분 정렬된 입력에서 더 빠름 |
| Timsort | mergesort + run 탐지의 결합 |

## Before / After

**Before — 손으로 짠 quicksort, 최악 입력에 약함:**

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

**After — 표준 sorted 사용:**

```python
sorted_arr = sorted(arr)        # Timsort, 안정, 적응형
arr.sort()                      # in-place 변형
```

## 실습: 단계별로 따라하기

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

분할 정복의 교과서. 안정 정렬이며 보장된 O(n log n)을 제공합니다. 단점은 O(n)의 추가 메모리.

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

피벗을 첫 원소로 두면 정렬된 입력에서 O(n²)이 됩니다. 랜덤 피벗 또는 median-of-three가 표준 방어책입니다.

### 3단계: heapsort 구현

```python
import heapq

def heapsort(arr):
    h = list(arr)
    heapq.heapify(h)                # O(n)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heapsort([3, 1, 4, 1, 5, 9, 2, 6]))
```

표준 라이브러리의 heap을 활용하면 보장된 O(n log n)을 얻습니다. 안정성은 없지만 추가 메모리가 적고 최악 시간이 보장됩니다.

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
# already sorted, nearly sorted가 훨씬 빠름
```

Timsort는 부분 정렬된 run을 탐지해 병합 단계를 줄입니다. 실세계 데이터는 완전한 무작위가 거의 없기 때문에 이 적응성이 큰 이득을 줍니다.

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

안정 정렬을 보조키 → 주키 순으로 두 번 적용하면 다중 키 정렬을 간결히 표현합니다. Timsort가 안정 정렬이라서 가능한 패턴입니다.

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

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "어떤 정렬"보다 "정말 정렬이 필요한가, 부분 정렬로 충분한가"를 먼저 묻습니다. 상위 k개만 필요하면 heap으로 O(n log k)에 끝낼 수 있고, 분할 통계만 필요하면 quickselect로 O(n)에 처리합니다.

또한 "메모리 안에 다 들어오는가"를 항상 봅니다. 디스크 정렬이 필요하면 external mergesort, 분산 환경이면 sort by/distribute by의 데이터 셔플 비용까지 고려합니다.

## 체크리스트

- [ ] 비교 기반 정렬의 하한 O(n log n)을 이해하는가
- [ ] mergesort/quicksort/heapsort의 트레이드오프를 말할 수 있는가
- [ ] 안정 정렬의 의미와 효용을 이해하는가
- [ ] Timsort가 빠른 이유를 설명할 수 있는가
- [ ] "정렬이 정말 필요한가"를 먼저 묻는가

## 연습 문제

1. `key` 함수를 활용해 단어 리스트를 길이 오름차순, 같은 길이면 사전순 오름차순으로 정렬하는 코드를 한 줄로 작성하세요. Timsort의 안정성을 활용해도 됩니다.

2. `heapq.nlargest`를 직접 구현하세요. 즉, 입력 리스트와 k가 주어졌을 때 상위 k개의 원소를 O(n log k)에 반환하는 함수를 작성하고, 정렬보다 빠른 이유를 설명하세요.

3. 1억 개의 정수를 메모리에 다 담을 수 없는 환경에서 정렬해야 한다고 가정하고, external mergesort의 단계를 의사코드로 설계하세요. 디스크 입출력 횟수를 추정해 봅니다.

## 정리 및 다음 단계

정렬 알고리즘은 같은 점근 복잡도 안에서 안정성·메모리·적응성으로 차별화됩니다. 파이썬의 sorted는 실세계 데이터에 강한 Timsort를 사용하므로, 일반적으로는 표준을 그대로 쓰고 트레이드오프가 분명할 때만 다른 정렬을 고민하면 됩니다.

다음 글에서는 재귀와 분할 정복을 살펴봅니다. 재귀의 정의, 호출 스택, 분할 정복의 사고 패턴, 메모이제이션의 시작점까지 다룹니다.

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
