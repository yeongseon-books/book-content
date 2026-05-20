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

이 글은 Algorithms with Python 101 시리즈의 네 번째 글입니다. 정렬은 초보자가 생각하는 것보다 훨씬 많은 문제의 바닥에 깔려 있으며, 이진 탐색·랭킹·그룹화·중복 제거는 모두 데이터가 정렬되어 있으면 훨씬 쉬워집니다.

이번 글에서는 "실무에서는 왜 대부분 `sorted()`를 쓰는가?"라는 질문을 중심축으로 잡고, 고전 정렬 알고리즘을 비교 재료로 활용하겠습니다. 즉, 구현 자체보다도 언제 내장 정렬이 기본 선택이고, 언제 안정성과 `key` 설계가 진짜 핵심인지까지 연결해 보겠습니다.

## 먼저 던지는 질문

- 실무에서 직접 정렬 알고리즘을 구현하는 대신 `sorted()`를 우선해야 하는 이유는 무엇일까요?
- 세 가지 `O(n^2)` 정렬 알고리즘은 어떤 원리로 동작하며 어디까지 학습용으로 봐야 할까요?
- 병합 정렬과 퀵 정렬은 분할 정복을 어떻게 활용할까요?

## 큰 그림

![Algorithms with Python 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/04/04-01-big-picture.ko.png)

*Algorithms with Python 101 4장 흐름 개요*

이 그림에서는 정렬 알고리즘를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 정렬 알고리즘의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

정렬은 컴퓨팅에서 가장 기본적인 작업 가운데 하나입니다. 이진 탐색, 중복 제거, 순위 계산은 모두 정렬된 데이터를 전제로 하거나 정렬의 도움을 크게 받습니다. 1만 개를 넘어가면 `O(n^2)`와 `O(n log n)`의 차이는 금방 체감 가능한 수준으로 벌어집니다.

> 정렬은 데이터를 특정 순서로 재배열하는 일이며, 실무에서는 알고리즘 재구현보다 올바른 정렬 기준과 검증 루프를 설계하는 능력이 더 자주 필요합니다.

실전에서는 `sorted()`를 거의 항상 사용합니다. 그래도 원리를 이해해야 `key`를 제대로 설계하고, 안정성을 의식하고, 병목이 "정렬 알고리즘 선택" 때문인지 "정렬 기준 설계" 때문인지 구분할 수 있습니다.

## 개념 한눈에 보기

> 비교 기반 정렬에서는 "무엇을 기준으로 비교하느냐"와 "같은 값의 순서를 보존하느냐"를 함께 봐야 합니다.

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

## Before / After

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

### Step 1: 실무 기본값부터 확인하기 — `sorted(..., key=...)`

```python
records = [
    {"name": "Mina", "score": 90, "submitted_at": 3},
    {"name": "Joon", "score": 75, "submitted_at": 1},
    {"name": "Sora", "score": 90, "submitted_at": 2},
    {"name": "Luca", "score": 75, "submitted_at": 4},
]

sorted_records = sorted(records, key=lambda record: record["score"])
print([(record["name"], record["score"]) for record in sorted_records])
# [('Joon', 75), ('Luca', 75), ('Mina', 90), ('Sora', 90)]

score_75_order = [record["name"] for record in sorted_records if record["score"] == 75]
score_90_order = [record["name"] for record in sorted_records if record["score"] == 90]

assert score_75_order == ["Joon", "Luca"]
assert score_90_order == ["Mina", "Sora"]

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

여기서 핵심은 두 가지입니다. 첫째, 실무에서는 알고리즘을 다시 쓰는 대신 `key`를 정확히 정의하는 편이 훨씬 중요합니다. 둘째, Python의 내장 정렬은 안정 정렬이므로 같은 점수의 상대 순서가 유지됩니다.

검증 포인트도 명확합니다.

- 점수 75 그룹의 순서가 `Joon → Luca`로 유지되어야 합니다.
- 점수 90 그룹의 순서가 `Mina → Sora`로 유지되어야 합니다.
- 둘 중 하나라도 바뀌면 `key`를 잘못 주었는지보다 먼저 안정 정렬이 보장되는 도구를 쓰고 있는지 확인해야 합니다.

### Step 2: 고전 정렬은 학습용 대비 재료로 보기

```python
def verify_sort(name: str, func, cases: dict[str, list[int]]) -> None:
    for case_name, values in cases.items():
        expected = sorted(values)
        actual = func(values)
        print(f"{name:>10} | {case_name:>14} | expected={expected} | actual={actual}")
        assert actual == expected, f"{name} failed on {case_name}"

test_cases = {
    "random": [5, 3, 8, 1, 2],
    "sorted": [1, 2, 3, 4, 5],
    "reversed": [5, 4, 3, 2, 1],
    "duplicates": [4, 2, 4, 1, 2, 1],
}

def bubble_sort(data: list[int]) -> list[int]:
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

def selection_sort(data: list[int]) -> list[int]:
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
verify_sort("selection", selection_sort, test_cases)
verify_sort("insertion", insertion_sort, test_cases)
```

검증 루프를 일부러 네 가지 경우로 나눠 둔 이유는 실패 원인을 빠르게 좁히기 위해서입니다.

- 이미 정렬된 리스트에서 버블 정렬이 틀리면 먼저 내부 반복 범위 `n - 1 - i`를 확인합니다.
- 중복이 많은 입력에서 삽입 정렬이 틀리면 `while j >= 0 and arr[j] > key:` 조건을 먼저 봅니다. `>=`로 바꾸면 불필요하게 안정성이 깨질 수 있습니다.
- 선택 정렬이 맞게 정렬되더라도 안정 정렬이 아니라는 점은 그대로 남습니다. 따라서 "정답은 맞지만 기존 순서가 깨지는가"까지 분리해서 생각해야 합니다.

선택 정렬은 가장 작은 값을 앞으로 보내고, 삽입 정렬은 현재 원소를 알맞은 자리에 끼워 넣습니다. 둘 다 `O(n^2)`이지만, 거의 정렬된 데이터에서는 삽입 정렬이 상대적으로 유리할 수 있습니다.

### Step 3: Merge sort는 안정성의 원인을 보여 줍니다

```python
def merge_sort(data: list[int]) -> list[int]:
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
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

verify_sort("merge", merge_sort, test_cases)

def merge_sort_records(records: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
    if len(records) <= 1:
        return records[:]
    mid = len(records) // 2
    left = merge_sort_records(records[:mid])
    right = merge_sort_records(records[mid:])
    return merge_records(left, right)

def merge_records(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]["score"] <= right[j]["score"]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

stable_records = merge_sort_records(records)
assert [record["name"] for record in stable_records if record["score"] == 75] == ["Joon", "Luca"]
assert [record["name"] for record in stable_records if record["score"] == 90] == ["Mina", "Sora"]
```

병합 정렬은 분할 정복의 대표 예시입니다. 반으로 나누고, 각 절반을 정렬한 뒤, 다시 합칩니다. 여기서 같은 점수의 순서가 유지되는 이유는 병합 단계의 `<=` 때문입니다.

만약 숫자 정렬은 맞는데 같은 점수의 이름 순서가 바뀐다면, 먼저 `merge_records()`의 `<=`를 `<`로 잘못 바꾸지 않았는지 확인하면 됩니다.

### Step 4: Quick sort는 빠르지만 똑같이 검증해야 합니다

```python
def quick_sort(data: list[int]) -> list[int]:
    if len(data) <= 1:
        return data[:]
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

verify_sort("quick", quick_sort, test_cases)
```

퀵 정렬은 피벗을 기준으로 작은 값과 큰 값을 분리합니다. 평균적으로는 빠르지만, 피벗 선택이 나쁘면 최악의 경우 `O(n^2)`가 될 수 있습니다. 뒤집힌 입력에서 실패하거나 지나치게 느리면 먼저 피벗 전략과 분할 조건을 의심해야 합니다.

### Step 5: 벤치마크는 단일 숫자보다 성장 추세를 봅니다

```python
import random
import time

def benchmark_sort(n: int) -> list[tuple[str, float, bool]]:
    data = [random.randint(0, n) for _ in range(n)]

    algorithms = [
        ("Bubble", bubble_sort),
        ("Selection", selection_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
        ("Built-in", sorted),
    ]

    results = []
    for name, func in algorithms:
        start = time.perf_counter()
        actual = func(data[:])
        elapsed = time.perf_counter() - start
        is_correct = actual == sorted(data)
        results.append((name, elapsed, is_correct))
    return results

for n in [1_000, 5_000]:
    print(f"n={n:,}")
    for name, elapsed, is_correct in benchmark_sort(n):
        print(f"  {name:>8}: {elapsed:.4f}s | correct={is_correct}")
        assert is_correct, f"{name} produced a wrong result for n={n}"
```

이 벤치마크의 목적은 "누가 0.001초 더 빠른가"를 외우는 것이 아닙니다. 입력이 커질수록 `O(n^2)` 계열과 `O(n log n)` 계열의 증가 폭이 어떻게 달라지는지를 보는 쪽이 중요합니다.

만약 아주 작은 입력에서 버블 정렬이 생각보다 덜 느려 보여도 과하게 해석하지 않는 편이 좋습니다. 단일 실행 노이즈보다 입력 크기가 커질 때의 추세를 보아야 합니다.

## 이 코드에서 먼저 봐야 할 점

- 실무 기본값은 정렬 알고리즘 재구현이 아니라 `sorted(..., key=...)`입니다.
- 버블 정렬의 `swapped` 플래그는 이미 정렬된 데이터에서 `O(n)`까지 줄여 줍니다.
- 병합 정렬에서 `<=` 비교를 사용해야 같은 값의 기존 순서가 보존됩니다.
- 퀵 정렬은 피벗 선택에 따라 성능이 크게 달라집니다.
- 검증 루프는 랜덤, 이미 정렬됨, 역순, 중복 입력을 분리해서 돌려야 실패 원인을 빨리 좁힐 수 있습니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 원본 리스트를 바로 변경함 | 호출자가 예상하지 못한 부작용이 생깁니다 | 복사본에서 작업하거나 `sorted()`를 사용합니다 |
| 첫 원소를 무조건 피벗으로 사용 | 이미 정렬된 데이터에서 `O(n^2)`가 됩니다 | 가운데 값이나 랜덤 피벗을 사용합니다 |
| 안정성이 필요한데 학습용 불안정 정렬을 그대로 씀 | 같은 값의 상대 순서가 깨집니다 | `sorted()`나 병합 정렬을 사용하고, 같은 키 그룹의 순서를 직접 검증합니다 |
| 잘못된 정렬 기준 사용 | 원하는 순서와 다른 결과가 나옵니다 | `key` 함수를 명시적으로 설계합니다 |
| 큰 데이터에 `O(n^2)` 정렬 사용 | 수만 건만 되어도 급격히 느려집니다 | `O(n log n)` 또는 내장 정렬을 씁니다 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스의 `ORDER BY`는 내부적으로 정렬을 사용합니다.
- 로그 분석은 타임스탬프 기준 정렬이 기본입니다.
- 검색 엔진은 관련도 점수로 결과를 정렬합니다.
- pandas의 `sort_values()`도 내부적으로 정렬 알고리즘을 사용합니다.
- 리더보드와 랭킹 시스템은 실시간 정렬에 의존합니다.

## 현업에서는 이렇게 생각합니다

실제로는 정렬 알고리즘을 직접 구현할 일이 거의 없습니다. `sorted()`와 `list.sort()`가 대부분의 상황을 해결합니다. 대신 정말 중요한 능력은 올바른 `key` 함수를 설계하고, 같은 키를 가진 데이터의 순서가 기대대로 유지되는지 검증하는 일입니다.

그래도 원리를 알고 있어야 "왜 이 정렬이 느리지?", "왜 여기서는 안정성이 중요하지?", "왜 값은 맞는데 순서가 어색하지?" 같은 질문에 답할 수 있습니다.

## 체크리스트

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

정렬 학습의 핵심은 "모든 정렬을 외우는 것"이 아니라 "실무 기본값은 `sorted(..., key=...)`이고, 고전 알고리즘은 그 선택을 더 잘 이해하기 위한 대비 재료"라는 점을 체득하는 것입니다. `O(n^2)` 정렬은 이해하기 쉽지만 큰 데이터에는 비실용적이고, 병합 정렬과 퀵 정렬 같은 `O(n log n)` 정렬은 분할 정복 전략을 사용합니다. 다음 글에서는 이 분할 정복 패턴과 재귀를 더 깊이 살펴봅니다.

## 처음 질문으로 돌아가기

- **실무에서 직접 정렬 알고리즘을 구현하는 대신 `sorted()`를 우선해야 하는 이유는 무엇일까요?**
  - 본문의 기준은 정렬 알고리즘를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **세 가지 `O(n^2)` 정렬 알고리즘은 어떤 원리로 동작하며 어디까지 학습용으로 봐야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **병합 정렬과 퀵 정렬은 분할 정복을 어떻게 활용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
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
