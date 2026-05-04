---
series: algorithms-python-101
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
  - Python
  - 알고리즘
  - 정렬
  - 버블 정렬
  - 퀵 정렬
seo_description: Python으로 버블·선택·삽입·병합·퀵 정렬을 구현하고 성능을 비교합니다.
last_reviewed: '2026-05-04'
---

# 정렬 알고리즘

> Algorithms with Python 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 데이터를 정렬하는데 왜 알고리즘마다 성능이 다를까요?

> 정렬은 탐색, 중복 제거, 통계 등 거의 모든 데이터 처리의 전제 조건입니다. 이 글에서는 O(n²) 정렬(버블, 선택, 삽입)과 O(n log n) 정렬(병합, 퀵)을 Python으로 구현하고, 내장 sorted()와 비교합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- O(n²) 정렬 세 가지의 원리와 구현
- 병합 정렬과 퀵 정렬의 분할 정복 전략
- Python 내장 정렬의 특성과 key 함수 활용
- 정렬 안정성(stability)의 의미와 중요성

## 왜 중요한가

정렬은 알고리즘의 기본 중 기본입니다. 이진 탐색, 중복 제거, 순위 계산 등 수많은 연산이 정렬된 데이터를 전제로 합니다. 데이터 1만 개만 넘어도 O(n²)와 O(n log n)의 차이는 100배 이상입니다.

> 정렬 = 데이터를 특정 기준에 따라 순서대로 배치하는 연산

실무에서는 대부분 내장 sorted()를 사용하지만, 정렬 알고리즘의 원리를 이해하면 key 함수 설계, 안정 정렬 활용, 성능 병목 분석에 큰 도움이 됩니다.

## 핵심 개념 잡기

> 비교 기반 정렬 = 원소 간 대소 비교로 순서를 결정하는 정렬

```
버블 정렬: 인접 원소를 비교·교환 → O(n²)
선택 정렬: 최솟값을 찾아 앞으로 → O(n²)
삽입 정렬: 올바른 위치에 삽입 → O(n²), 거의 정렬된 데이터에 강함
병합 정렬: 반으로 나누고 합치기 → O(n log n), 안정 정렬
퀵 정렬:   피벗 기준 분할 → 평균 O(n log n)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 안정 정렬(stable sort) | 같은 값의 원래 순서가 유지되는 정렬입니다 |
| 제자리 정렬(in-place sort) | 추가 메모리 O(1)만 사용하는 정렬입니다 |
| 비교 정렬(comparison sort) | 원소 간 대소 비교로 정렬하며 하한이 O(n log n)입니다 |
| 피벗(pivot) | 퀵 정렬에서 분할 기준이 되는 원소입니다 |
| 분할 정복(divide and conquer) | 문제를 작은 부분으로 나누어 해결하는 전략입니다 |

## Before / After

같은 리스트를 정렬하는 두 가지 접근을 비교합니다.

```python
# before: 버블 정렬 — O(n²)
def sort_data(data):
    n = len(data)
    for i in range(n):
        for j in range(n - 1 - i):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

```python
# after: 내장 정렬 — O(n log n), Timsort
def sort_data(data):
    return sorted(data)
```

## 단계별 실습

### Step 1: 버블 정렬

```python
def bubble_sort(data: list[int]) -> list[int]:
    """버블 정렬 — O(n²), 안정, 제자리"""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # 이미 정렬 완료
    return arr

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### Step 2: 선택 정렬과 삽입 정렬

```python
def selection_sort(data: list[int]) -> list[int]:
    """선택 정렬 — O(n²), 불안정, 제자리"""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(data: list[int]) -> list[int]:
    """삽입 정렬 — O(n²), 안정, 제자리, 거의 정렬된 데이터에 빠름"""
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

data = [64, 25, 12, 22, 11]
print(selection_sort(data))   # [11, 12, 22, 25, 64]
print(insertion_sort(data))   # [11, 12, 22, 25, 64]
```

### Step 3: 병합 정렬

```python
def merge_sort(data: list[int]) -> list[int]:
    """병합 정렬 — O(n log n), 안정, 추가 메모리 O(n)"""
    if len(data) <= 1:
        return data[:]

    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= 로 안정 정렬 보장
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
# [3, 9, 10, 27, 38, 43, 82]
```

### Step 4: 퀵 정렬

```python
def quick_sort(data: list[int]) -> list[int]:
    """퀵 정렬 — 평균 O(n log n), 최악 O(n²)"""
    if len(data) <= 1:
        return data[:]

    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

print(quick_sort([3, 6, 8, 10, 1, 2, 1]))
# [1, 1, 2, 3, 6, 8, 10]
```

### Step 5: 내장 정렬과 성능 비교

```python
import time


def benchmark_sort(n: int):
    import random
    data = [random.randint(0, n) for _ in range(n)]

    algorithms = [
        ("버블", bubble_sort),
        ("선택", selection_sort),
        ("삽입", insertion_sort),
        ("병합", merge_sort),
        ("퀵", quick_sort),
        ("내장", sorted),
    ]

    for name, func in algorithms:
        arr = data[:]
        start = time.perf_counter()
        func(arr)
        elapsed = time.perf_counter() - start
        print(f"  {name}: {elapsed:.4f}초")


for n in [1_000, 5_000]:
    print(f"n={n:,}")
    benchmark_sort(n)
```

## 이 코드에서 주목할 점

- 버블 정렬의 early termination(swapped 플래그)은 이미 정렬된 데이터에서 O(n)입니다
- 병합 정렬의 `<=` 비교가 안정 정렬을 보장합니다
- 퀵 정렬의 피벗 선택이 성능을 좌우합니다. 중간값을 선택하면 최악의 경우를 줄입니다
- Python의 sorted()는 Timsort로, 삽입 정렬과 병합 정렬의 하이브리드입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 원본 리스트를 직접 수정 | 호출자가 의도하지 않은 변경입니다 | 복사본을 만들거나 sorted()를 사용합니다 |
| 퀵 정렬에서 첫 원소를 피벗으로 선택 | 이미 정렬된 데이터에서 O(n²)입니다 | 중간값이나 랜덤 피벗을 사용합니다 |
| 안정 정렬이 필요한 곳에서 불안정 정렬 사용 | 같은 값의 원래 순서가 깨집니다 | sorted()나 병합 정렬을 사용합니다 |
| 정렬 기준을 잘못 설정 | 의도와 다른 결과가 나옵니다 | key 함수를 명시적으로 지정합니다 |
| O(n²) 정렬을 대규모 데이터에 사용 | 수만 건에서 수 초 이상 걸립니다 | O(n log n) 알고리즘이나 내장 정렬을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 ORDER BY 절이 내부적으로 정렬 알고리즘을 사용합니다
- 로그 분석에서 타임스탬프 기준으로 이벤트를 정렬합니다
- 검색 엔진이 관련도 점수로 결과를 정렬합니다
- pandas의 sort_values()가 Timsort를 사용합니다
- 리더보드, 랭킹 시스템이 실시간 정렬에 의존합니다

## 현업 개발자는 이렇게 생각합니다

실무에서 직접 정렬 알고리즘을 구현할 일은 거의 없습니다. sorted()와 list.sort()가 대부분의 상황을 커버합니다. 중요한 것은 key 함수를 잘 설계하는 것입니다.

하지만 정렬 알고리즘의 원리를 아는 것은 중요합니다. "왜 이 정렬이 느린가", "안정 정렬이 왜 필요한가"를 이해하면 올바른 도구를 선택할 수 있습니다.

## 체크리스트

- [ ] O(n²) 정렬 세 가지의 차이점을 설명할 수 있다
- [ ] 병합 정렬과 퀵 정렬의 분할 정복 과정을 설명할 수 있다
- [ ] 안정 정렬과 불안정 정렬의 차이를 설명할 수 있다
- [ ] sorted()의 key 함수를 활용할 수 있다
- [ ] 상황에 따라 적절한 정렬 전략을 선택할 수 있다

## 연습 문제

1. 딕셔너리 리스트를 특정 키 기준으로 정렬하는 함수를 작성하세요 (예: 나이 → 이름 순).
2. 퀵 정렬에서 랜덤 피벗을 선택하도록 수정하세요.
3. 삽입 정렬이 거의 정렬된 데이터에서 왜 빠른지 벤치마크로 확인하세요.

## 정리 및 다음 글 안내

O(n²) 정렬은 이해하기 쉽지만 대규모 데이터에 부적합합니다. O(n log n) 정렬인 병합 정렬과 퀵 정렬은 분할 정복 전략을 사용합니다. 다음 글에서는 이 분할 정복 패턴과 재귀를 깊이 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- **정렬 알고리즘 (현재 글)**
- 재귀와 분할 정복 (예정)
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [Wikipedia — Sorting Algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm)
- [Visualgo — Sorting Visualization](https://visualgo.net/en/sorting)
- [Real Python — How to Use sorted() and sort()](https://realpython.com/python-sort/)

Tags: Python, 알고리즘, 정렬, 버블 정렬, 퀵 정렬
