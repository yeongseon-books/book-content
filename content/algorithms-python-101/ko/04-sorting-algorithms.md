---
series: algorithms-python-101
episode: 4
title: "Algorithms with Python 101 (4/10): 정렬 알고리즘"
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

# Algorithms with Python 101 (4/10): 정렬 알고리즘

> 비교 기반 정렬에서는 "무엇을 기준으로 비교하느냐"와 "같은 값의 순서를 보존하느냐"를 함께 봐야 합니다.

이 글은 Algorithms with Python 101 시리즈의 네 번째 글입니다. 정렬은 초보자가 생각하는 것보다 훨씬 많은 문제의 바닥에 깔려 있으며, 이진 탐색·랭킹·그룹화·중복 제거는 모두 데이터가 정렬되어 있으면 훨씬 쉬워집니다.

이번 글에서는 "실무에서는 왜 대부분 `sorted()`를 쓰는가?"라는 질문을 중심축으로 잡고, 고전 정렬 알고리즘을 비교 재료로 활용하겠습니다.

![Algorithms with Python 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/04/04-01-big-picture.ko.png)
*Algorithms with Python 101 4장 흐름 개요*

## 이 글에서 다룰 문제

- 실무에서 직접 정렬 알고리즘을 구현하는 대신 `sorted()`를 우선해야 하는 이유는 무엇일까요?
- 세 가지 `O(n^2)` 정렬 알고리즘은 어떤 원리로 동작하며 어디까지 학습용으로 봐야 할까요?
- 병합 정렬과 퀵 정렬은 분할 정복을 어떻게 활용할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> 정렬은 데이터를 특정 순서로 재배열하는 일이며, 실무에서는 알고리즘 재구현보다 올바른 정렬 기준과 검증 루프를 설계하는 능력이 더 자주 필요합니다.

## 개념 한눈에 보기

| 선택지 | 핵심 아이디어 | 시간 복잡도 | 언제 떠올리면 좋은가 |
|------|---------------|-------------|-----------------------|
| `sorted(data, key=...)` | 검증된 내장 정렬에 정렬 기준만 전달합니다 | `O(n log n)` | 실무 기본값 |
| Bubble / Selection / Insertion | 비교와 이동 원리를 직접 구현합니다 | `O(n^2)` | 학습용, 작은 입력 |
| Merge sort | 나누고 정렬하고 합칩니다 | `O(n log n)` | 안정성이 중요한 분할 정복 예제 |
| Quick sort | 피벗 기준으로 분할합니다 | 평균 `O(n log n)` | 평균 성능과 피벗 전략 설명 |

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Stable sort | 값이 같은 원소들의 기존 상대 순서를 보존합니다 |
| In-place sort | 추가 메모리를 거의 쓰지 않고 제자리에서 정렬합니다 |
| Comparison sort | 비교로 순서를 정하는 정렬로, 이론적 하한이 `O(n log n)`입니다 |
| Pivot | 퀵 정렬에서 분할 기준으로 쓰는 원소입니다 |
| Divide and conquer | 문제를 나누고, 각각을 풀고, 다시 합치는 전략입니다 |

## 적용 전후 비교

같은 "직원 목록을 부서, 입사 순서 기준으로 정렬"하는 문제라도 접근은 크게 다를 수 있습니다.

```python
# before: 직접 재구현부터 시작하면 기준 설계보다 구현 세부에 시간을 씁니다
def sort_people(records):
    data = records[:]
    n = len(data)
    for i in range(n):
        for j in range(n - 1 - i):
            if (data[j]["department"], data[j]["joined_at"]) > (
                data[j + 1]["department"],
                data[j + 1]["joined_at"],
            ):
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

```python
# after: 실무 기본값은 내장 정렬 + 명시적인 key 입니다
def sort_people(records):
    return sorted(records, key=lambda record: (record["department"], record["joined_at"]))
```

## 단계별 실습

### 단계 1: 실무 기본값 — `sorted(..., key=...)`

```python
records = [
    {"name": "Mina", "score": 90, "submitted_at": 3},
    {"name": "Joon", "score": 75, "submitted_at": 1},
    {"name": "Sora", "score": 90, "submitted_at": 2},
    {"name": "Luca", "score": 75, "submitted_at": 4},
]

# 단일 키 정렬
sorted_records = sorted(records, key=lambda record: record["score"])
print([(record["name"], record["score"]) for record in sorted_records])
# [('Joon', 75), ('Luca', 75), ('Mina', 90), ('Sora', 90)]

# 안정 정렬 검증
score_75_order = [record["name"] for record in sorted_records if record["score"] == 75]
assert score_75_order == ["Joon", "Luca"], "안정 정렬 위반"

# 다중 키 정렬 (점수 내림차순, 제출 시간 오름차순)
sorted_by_two_keys = sorted(
    records,
    key=lambda record: (-record["score"], record["submitted_at"]),
)
print([
    (record["name"], record["score"], record["submitted_at"])
    for record in sorted_by_two_keys
])
# [('Sora', 90, 2), ('Mina', 90, 3), ('Joon', 75, 1), ('Luca', 75, 4)]
```

Python의 내장 정렬은 안정 정렬(Timsort)이므로 같은 점수의 상대 순서가 유지됩니다.

### 단계 2: O(n^2) 고전 정렬

```python
def verify_sort(name: str, func, cases: dict[str, list[int]]) -> None:
    for case_name, values in cases.items():
        expected = sorted(values)
        actual = func(values)
        assert actual == expected, f"{name} failed on {case_name}"
        print(f"{name:>10} | {case_name:>14} | OK")

test_cases = {
    "random": [5, 3, 8, 1, 2],
    "sorted": [1, 2, 3, 4, 5],
    "reversed": [5, 4, 3, 2, 1],
    "duplicates": [4, 2, 4, 1, 2, 1],
}

def bubble_sort(data: list[int]) -> list[int]:
    """O(n^2) — 인접 원소를 비교해 교환"""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # 이미 정렬된 경우 O(n)으로 조기 종료
    return arr

def insertion_sort(data: list[int]) -> list[int]:
    """O(n^2) — 현재 원소를 알맞은 자리에 삽입"""
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

verify_sort("bubble", bubble_sort, test_cases)
verify_sort("insertion", insertion_sort, test_cases)
```

### 단계 3: 병합 정렬 — 안정성의 원리

```python
def merge_sort(data: list[int]) -> list[int]:
    """O(n log n) — 분할 정복, 안정 정렬"""
    if len(data) <= 1:
        return data[:]
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    return _merge(left, right)

def _merge(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:   # <= 덕분에 안정 정렬 유지
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

verify_sort("merge", merge_sort, test_cases)
```

병합 단계에서 `<=`를 사용하는 이유: 왼쪽(먼저 나타난 원소)을 우선 선택해야 기존 순서가 유지됩니다.

### 단계 4: 퀵 정렬 — 피벗 기반 분할

```python
def quick_sort(data: list[int]) -> list[int]:
    """평균 O(n log n) — 피벗 기준 분할"""
    if len(data) <= 1:
        return data[:]
    pivot = data[len(data) // 2]  # 가운데 원소를 피벗으로
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

verify_sort("quick", quick_sort, test_cases)
```

피벗 선택이 나쁘면(정렬된 입력에 첫 원소 피벗) 최악의 경우 `O(n^2)`가 됩니다.

### 단계 5: 벤치마크 — 성장 추세 비교

```python
import random
import time

def benchmark_sort(n: int) -> None:
    data = [random.randint(0, n) for _ in range(n)]
    algorithms = [
        ("Bubble", bubble_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
        ("Built-in", sorted),
    ]
    print(f"\nn={n:,}")
    for name, func in algorithms:
        start = time.perf_counter()
        actual = func(data[:])
        elapsed = time.perf_counter() - start
        is_correct = actual == sorted(data)
        print(f"  {name:>8}: {elapsed:.4f}s | correct={is_correct}")

for n in [1_000, 5_000]:
    benchmark_sort(n)
```

## 단계별 실행 추적 — 삽입 정렬

`insertion_sort([5, 2, 4, 1, 3])` 실행을 한 단계씩 따라가 보겠습니다.

```text
초기: [5, 2, 4, 1, 3]

i=1, key=2:
  arr[0]=5 > 2 → arr[1]=arr[0]=5, j=-1
  arr[0]=2
  상태: [2, 5, 4, 1, 3]

i=2, key=4:
  arr[1]=5 > 4 → arr[2]=arr[1]=5, j=0
  arr[0]=2 > 4? No → 멈춤
  arr[1]=4
  상태: [2, 4, 5, 1, 3]

i=3, key=1:
  arr[2]=5 > 1 → arr[3]=5, j=1
  arr[1]=4 > 1 → arr[2]=4, j=0
  arr[0]=2 > 1 → arr[1]=2, j=-1
  arr[0]=1
  상태: [1, 2, 4, 5, 3]

i=4, key=3:
  arr[3]=5 > 3 → arr[4]=5, j=2
  arr[2]=4 > 3 → arr[3]=4, j=1
  arr[1]=2 > 3? No → 멈춤
  arr[2]=3
  상태: [1, 2, 3, 4, 5]

결과: [1, 2, 3, 4, 5]
```

## 코딩 테스트 풀이 예시

**문제**: 딕셔너리 리스트를 여러 키 기준으로 정렬하라.

```python
from functools import cmp_to_key

def sort_students(students: list[dict]) -> list[dict]:
    """
    학생을 점수 내림차순, 같은 점수면 이름 오름차순으로 정렬합니다.
    시간 복잡도: O(n log n)
    """
    return sorted(
        students,
        key=lambda s: (-s["score"], s["name"])
    )


students = [
    {"name": "Charlie", "score": 85},
    {"name": "Alice", "score": 92},
    {"name": "Bob", "score": 85},
    {"name": "Diana", "score": 92},
]

result = sort_students(students)
for s in result:
    print(f"{s['name']}: {s['score']}")
# Alice: 92
# Diana: 92
# Bob: 85
# Charlie: 85
```

**문제**: 회의 시간표를 정렬해 겹치는 회의를 찾아라.

```python
def find_overlapping_meetings(
    meetings: list[tuple[int, int]]
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    겹치는 회의 쌍을 반환합니다.
    정렬 후 선형 스캔으로 O(n log n)에 처리합니다.
    """
    sorted_meetings = sorted(meetings, key=lambda m: m[0])
    overlaps = []

    for i in range(len(sorted_meetings) - 1):
        curr_start, curr_end = sorted_meetings[i]
        next_start, next_end = sorted_meetings[i + 1]
        if next_start < curr_end:  # 겹침
            overlaps.append((sorted_meetings[i], sorted_meetings[i + 1]))

    return overlaps


meetings = [(9, 11), (10, 12), (13, 15), (14, 16)]
print(find_overlapping_meetings(meetings))
# [((9, 11), (10, 12)), ((13, 15), (14, 16))]
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 원본 리스트를 바로 변경함 | 호출자가 예상하지 못한 부작용이 생깁니다 | 복사본에서 작업하거나 `sorted()`를 사용합니다 |
| 첫 원소를 무조건 피벗으로 사용 | 이미 정렬된 데이터에서 `O(n^2)`가 됩니다 | 가운데 값이나 랜덤 피벗을 사용합니다 |
| 안정성이 필요한데 불안정 정렬을 사용 | 같은 값의 상대 순서가 깨집니다 | `sorted()`나 병합 정렬을 사용합니다 |
| 잘못된 정렬 기준 사용 | 원하는 순서와 다른 결과가 나옵니다 | `key` 함수를 명시적으로 설계합니다 |
| 큰 데이터에 `O(n^2)` 정렬 사용 | 수만 건만 되어도 급격히 느려집니다 | `O(n log n)` 또는 내장 정렬을 씁니다 |

## 알고리즘 비교표

| 알고리즘 | 평균 시간 | 최악 시간 | 안정성 | 실무 기본값 여부 |
|----------|-----------|-----------|--------|------------------|
| Bubble / Selection | `O(n^2)` | `O(n^2)` | 구현별 상이 | 아니오 |
| Insertion | `O(n^2)` | `O(n^2)` | 예 | 거의 정렬 입력에서 보조 |
| Merge | `O(n log n)` | `O(n log n)` | 예 | 안정성 강조 시 |
| Quick | `O(n log n)` | `O(n^2)` | 보통 불안정 | 피벗 전략 중요 |
| Python Timsort | `O(n log n)` | `O(n log n)` | 예 | 예 (기본값) |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스의 `ORDER BY`는 내부적으로 정렬을 사용합니다.
- 로그 분석은 타임스탬프 기준 정렬이 기본입니다.
- 검색 엔진은 관련도 점수로 결과를 정렬합니다.
- pandas의 `sort_values()`도 내부적으로 정렬 알고리즘을 사용합니다.
- 리더보드와 랭킹 시스템은 실시간 정렬에 의존합니다.

## 현업에서는 이렇게 생각합니다

실제로는 정렬 알고리즘을 직접 구현할 일이 거의 없습니다. `sorted()`와 `list.sort()`가 대부분의 상황을 해결합니다. 대신 정말 중요한 능력은 올바른 `key` 함수를 설계하고, 같은 키를 가진 데이터의 순서가 기대대로 유지되는지 검증하는 일입니다.

그래도 원리를 알고 있어야 "왜 이 정렬이 느리지?", "왜 여기서는 안정성이 중요하지?"라는 질문에 답할 수 있습니다.

## 운영 체크리스트

- [ ] 세 가지 `O(n^2)` 정렬의 차이를 설명할 수 있습니다
- [ ] 병합 정렬과 퀵 정렬의 분할 정복 과정을 설명할 수 있습니다
- [ ] 안정 정렬과 불안정 정렬의 차이를 설명할 수 있습니다
- [ ] `sorted()`에 사용자 정의 `key`를 적용하고, 같은 키 그룹의 순서를 검증할 수 있습니다
- [ ] 상황에 맞는 정렬 전략을 고를 수 있습니다

## 연습 문제

1. 딕셔너리 리스트를 여러 키 기준으로 정렬하는 함수를 작성해 보세요. 예를 들어 나이, 이름 순서입니다.
2. 퀵 정렬을 랜덤 피벗 방식으로 바꿔 보세요.
3. 거의 정렬된 데이터와 무작위 데이터에서 삽입 정렬의 성능을 비교하고 이유를 설명해 보세요.

## 정리와 다음 글

정렬 학습의 핵심은 "모든 정렬을 외우는 것"이 아니라 "실무 기본값은 `sorted(..., key=...)`이고, 고전 알고리즘은 그 선택을 더 잘 이해하기 위한 대비 재료"라는 점을 체득하는 것입니다. 다음 글에서는 이 분할 정복 패턴과 재귀를 더 깊이 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- **Algorithms with Python 101 (4/10): 정렬 알고리즘 (현재 글)**
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [Wikipedia — Sorting Algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm)
- [Visualgo — Sorting Visualization](https://visualgo.net/en/sorting)
- [Real Python — How to Use sorted() and sort()](https://realpython.com/python-sort/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/04-sorting-algorithms)

Tags: Python, Algorithms, Sorting, Bubble Sort, Quick Sort
