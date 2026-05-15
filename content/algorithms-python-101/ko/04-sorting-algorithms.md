---
series: algorithms-python-101
episode: 4
title: 정렬 알고리즘
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Sorting
  - Bubble Sort
  - Quick Sort
seo_description: 버블, 삽입, 퀵, 병합 정렬 원리를 파이썬으로 구현하며 비교합니다. 안정 정렬의 개념과 내장 정렬 함수의 효율성을 이해하고 활용법을 익힙니다.
last_reviewed: '2026-05-12'
---

# 정렬 알고리즘

정렬은 초보자가 생각하는 것보다 훨씬 많은 문제의 바닥에 깔려 있습니다. 이진 탐색, 랭킹, 그룹화, 중복 제거는 모두 데이터가 정렬되어 있으면 훨씬 쉬워집니다. 이 글은 Algorithms with Python 101 시리즈의 네 번째 글입니다. 여기서는 Python으로 대표적인 정렬 알고리즘을 구현하고, 전략 차이가 성능에 어떤 영향을 주는지 비교해 보겠습니다.

실무에서는 대부분 Python의 `sorted()`를 쓰겠지만, 고전 정렬 알고리즘의 트레이드오프를 이해해야 성능, 안정성, 데이터 형태를 더 정확하게 판단할 수 있습니다.

## 이 글에서 다룰 문제

- 세 가지 `O(n^2)` 정렬 알고리즘은 어떤 원리로 동작할까요?
- 병합 정렬과 퀵 정렬은 분할 정복을 어떻게 활용할까요?
- Python 내장 정렬은 어떻게 동작하며 `key` 함수는 언제 중요할까요?
- 안정 정렬과 불안정 정렬의 차이는 왜 중요할까요?

## 왜 중요한가

정렬은 컴퓨팅에서 가장 기본적인 작업 가운데 하나입니다. 이진 탐색, 중복 제거, 순위 계산은 모두 정렬된 데이터를 전제로 하거나 정렬의 도움을 크게 받습니다. 1만 개를 넘어가면 `O(n^2)`와 `O(n log n)`의 차이는 100배 이상 벌어질 수 있습니다.

> 정렬은 데이터를 특정 순서로 재배열하는 일입니다. 어떤 알고리즘을 고르느냐에 따라 작업이 밀리초 안에 끝날 수도 있고, 몇 분씩 걸릴 수도 있습니다.

실전에서는 `sorted()`를 거의 항상 사용합니다. 그래도 원리를 이해해야 `key`를 제대로 설계하고, 안정성을 의식하고, 병목을 진단할 수 있습니다.

## 개념 한눈에 보기

> 비교 기반 정렬은 원소끼리 비교해서 순서를 결정합니다

```text
Bubble sort:    compare and swap adjacent elements → O(n^2)
Selection sort: find the minimum and move it to front → O(n^2)
Insertion sort: insert each element at its correct position → O(n^2), fast on nearly sorted data
Merge sort:     split in half, sort, merge → O(n log n), stable
Quick sort:     partition around a pivot → average O(n log n)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Stable sort | 값이 같은 원소들의 기존 상대 순서를 보존합니다 |
| In-place sort | 추가 메모리를 거의 쓰지 않고 제자리에서 정렬합니다 |
| Comparison sort | 비교로 순서를 정하는 정렬로, 이론적 하한이 `O(n log n)`입니다 |
| Pivot | 퀵 정렬에서 분할 기준으로 쓰는 원소입니다 |
| Divide and conquer | 문제를 나누고, 각각을 풀고, 다시 합치는 전략입니다 |

## Before / After

리스트를 정렬하는 두 가지 방식입니다.

```python
# before: bubble sort — O(n^2)
def sort_data(data):
    n = len(data)
    for i in range(n):
        for j in range(n - 1 - i):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

```python
# after: built-in sort — O(n log n), Timsort
def sort_data(data):
    return sorted(data)
```

## 단계별 실습

### Step 1: Bubble Sort

```python
def bubble_sort(data: list[int]) -> list[int]:
    """Bubble sort — O(n^2), stable, in-place."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

버블 정렬은 구현이 단순해서 정렬의 기본 동작을 이해하기에 좋습니다. 다만 큰 입력에는 비효율적이므로 교육용 예제로 보는 편이 적절합니다.

### Step 2: Selection Sort and Insertion Sort

```python
def selection_sort(data: list[int]) -> list[int]:
    """Selection sort — O(n^2), unstable, in-place."""
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
    """Insertion sort — O(n^2), stable, fast on nearly sorted data."""
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

선택 정렬은 가장 작은 값을 골라 앞으로 보내고, 삽입 정렬은 현재 원소를 알맞은 자리에 끼워 넣습니다. 둘 다 `O(n^2)`이지만, 거의 정렬된 데이터에서는 삽입 정렬이 훨씬 유리할 수 있습니다.

### Step 3: Merge Sort

```python
def merge_sort(data: list[int]) -> list[int]:
    """Merge sort — O(n log n), stable, O(n) extra space."""
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
        if left[i] <= right[j]:  # <= ensures stability
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

병합 정렬은 분할 정복의 대표 예시입니다. 반으로 나누고, 각 절반을 정렬한 뒤, 다시 안정적으로 합칩니다.

### Step 4: Quick Sort

```python
def quick_sort(data: list[int]) -> list[int]:
    """Quick sort — average O(n log n), worst O(n^2)."""
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

퀵 정렬은 피벗을 기준으로 작은 값과 큰 값을 분리합니다. 평균적으로는 빠르지만, 피벗 선택이 나쁘면 최악의 경우 `O(n^2)`가 될 수 있습니다.

### Step 5: Built-in Sort and Benchmarks

```python
import time


def benchmark_sort(n: int):
    import random
    data = [random.randint(0, n) for _ in range(n)]

    algorithms = [
        ("Bubble", bubble_sort),
        ("Selection", selection_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
        ("Built-in", sorted),
    ]

    for name, func in algorithms:
        arr = data[:]
        start = time.perf_counter()
        func(arr)
        elapsed = time.perf_counter() - start
        print(f"  {name}: {elapsed:.4f}s")


for n in [1_000, 5_000]:
    print(f"n={n:,}")
    benchmark_sort(n)
```

이 비교를 통해 교육용 정렬과 실전용 정렬의 차이를 분명히 볼 수 있습니다. 실무에서 내장 정렬을 우선하는 이유가 성능과 안정성 모두에서 드러납니다.

## 이 코드에서 먼저 봐야 할 점

- 버블 정렬의 `swapped` 플래그는 이미 정렬된 데이터에서 `O(n)`까지 줄여 줍니다.
- 병합 정렬에서 `<=` 비교를 사용해야 안정성이 보장됩니다.
- 퀵 정렬은 피벗 선택에 따라 성능이 크게 달라집니다. 가운데 값을 고르면 최악 위험을 줄일 수 있습니다.
- Python의 `sorted()`는 삽입 정렬과 병합 정렬의 장점을 결합한 Timsort를 사용합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 원본 리스트를 바로 변경함 | 호출자가 예상하지 못한 부작용이 생깁니다 | 복사본에서 작업하거나 `sorted()`를 사용합니다 |
| 첫 원소를 무조건 피벗으로 사용 | 이미 정렬된 데이터에서 `O(n^2)`가 됩니다 | 가운데 값이나 랜덤 피벗을 사용합니다 |
| 안정성이 필요한데 불안정 정렬 사용 | 같은 값의 상대 순서가 깨집니다 | `sorted()`나 병합 정렬을 사용합니다 |
| 잘못된 정렬 기준 사용 | 원하는 순서와 다른 결과가 나옵니다 | `key` 함수를 명시적으로 설계합니다 |
| 큰 데이터에 `O(n^2)` 정렬 사용 | 수만 건만 되어도 급격히 느려집니다 | `O(n log n)` 또는 내장 정렬을 씁니다 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스의 `ORDER BY`는 내부적으로 정렬을 사용합니다.
- 로그 분석은 타임스탬프 기준 정렬이 기본입니다.
- 검색 엔진은 관련도 점수로 결과를 정렬합니다.
- pandas의 `sort_values()`도 내부적으로 정렬 알고리즘을 사용합니다.
- 리더보드와 랭킹 시스템은 실시간 정렬에 의존합니다.

## 현업에서는 이렇게 생각합니다

실제로는 정렬 알고리즘을 직접 구현할 일이 거의 없습니다. `sorted()`와 `list.sort()`가 대부분의 상황을 해결합니다. 대신 정말 중요한 능력은 올바른 `key` 함수를 설계하는 일입니다.

그래도 원리를 알고 있어야 "왜 이 정렬이 느리지?", "왜 여기서는 안정성이 중요하지?" 같은 질문에 답할 수 있습니다.

## 체크리스트

- [ ] 세 가지 `O(n^2)` 정렬의 차이를 설명할 수 있습니다
- [ ] 병합 정렬과 퀵 정렬의 분할 정복 과정을 설명할 수 있습니다
- [ ] 안정 정렬과 불안정 정렬의 차이를 설명할 수 있습니다
- [ ] `sorted()`에 사용자 정의 `key`를 적용할 수 있습니다
- [ ] 상황에 맞는 정렬 전략을 고를 수 있습니다

## 연습 문제

1. 딕셔너리 리스트를 여러 키 기준으로 정렬하는 함수를 작성해 보세요. 예를 들어 나이, 이름 순서입니다.
2. 퀵 정렬을 랜덤 피벗 방식으로 바꿔 보세요.
3. 거의 정렬된 데이터와 무작위 데이터에서 삽입 정렬의 성능을 비교하고 이유를 설명해 보세요.

## 정리와 다음 글

`O(n^2)` 정렬은 이해하기 쉽지만, 큰 데이터에는 비실용적입니다. 병합 정렬과 퀵 정렬 같은 `O(n log n)` 정렬은 분할 정복 전략을 사용합니다. 다음 글에서는 이 분할 정복 패턴과 재귀를 더 깊이 살펴봅니다.

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

- [Python Documentation — Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [Wikipedia — Sorting Algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm)
- [Visualgo — Sorting Visualization](https://visualgo.net/en/sorting)
- [Real Python — How to Use sorted() and sort()](https://realpython.com/python-sort/)

Tags: Python, Algorithms, Sorting, Bubble Sort, Quick Sort
