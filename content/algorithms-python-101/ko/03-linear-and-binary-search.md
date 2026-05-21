---
series: algorithms-python-101
episode: 3
title: "Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색"
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
  - Linear Search
  - Binary Search
  - bisect
seo_description: 선형 탐색과 이진 탐색의 차이를 파이썬 예제로 비교합니다. 정렬된 데이터에서 효율적인 이진 탐색 구현과 bisect 모듈 활용법을 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색

탐색은 프로그래밍에서 가장 자주 하는 작업 가운데 하나입니다. 작은 리스트라면 처음부터 끝까지 훑어도 충분하지만, 큰 정렬 리스트라면 매 단계마다 탐색 범위를 절반으로 줄이는 순간 문제의 성격이 완전히 달라집니다.

이 글은 Algorithms with Python 101 시리즈의 세 번째 글입니다. 여기서는 선형 탐색과 이진 탐색을 나란히 구현하고, 각각이 언제 적절한지 비교해 보겠습니다.

이진 탐색은 교과서 예제에만 머물지 않습니다. 정확히 같은 값을 찾는 문제뿐 아니라, 어떤 조건을 처음 만족하는 지점을 찾는 문제에도 자주 확장됩니다.

## 먼저 던지는 질문

- 선형 탐색은 어떻게 동작하고, 한계는 무엇일까요?
- 이진 탐색은 어떤 원리로 동작하며 어떻게 구현할까요?
- Python의 `bisect` 모듈은 언제 유용할까요?

## 큰 그림

![Algorithms with Python 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/03/03-01-big-picture.ko.png)

*Algorithms with Python 101 3장 흐름 개요*

## 왜 중요한가

탐색은 프로그래밍에서 가장 흔한 연산입니다. 데이터가 100개일 때는 선형 탐색으로 충분합니다. 하지만 100만 개가 되면 이진 탐색은 많아야 20번 정도 비교하면 되고, 선형 탐색은 최악의 경우 100만 번 모두 확인해야 합니다.

> 이진 탐색은 매 단계마다 남은 데이터의 절반을 제거해, 정렬된 데이터에서 `O(log n)`을 달성합니다.

단순 조회를 넘어서, "조건을 처음 만족하는 값"이나 "마지막으로 만족하는 값"을 찾는 문제로 확장된다는 점도 코딩 테스트에서 매우 중요합니다.

## 개념 한눈에 보기

> 탐색 = 데이터 집합에서 원하는 값을 찾는 과정

```text
Linear search: [1, 3, 5, 7, 9, 11, 13] — find 9
→ 1, 3, 5, 7, 9 (5 comparisons)

Binary search: [1, 3, 5, 7, 9, 11, 13] — find 9
→ 7 (middle), 11 (right half middle), 9 (3 comparisons)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Linear search | 처음부터 끝까지 하나씩 확인하는 탐색으로 `O(n)`입니다 |
| Binary search | 가운데 값을 기준으로 절반씩 줄여 가는 탐색으로, 정렬 데이터에서 `O(log n)`입니다 |
| bisect | Python 표준 라이브러리의 이진 탐색 모듈입니다 |
| Upper/lower bound | 특정 값 이상 또는 초과가 처음 나타나는 위치를 찾는 변형입니다 |
| Parametric search | 정확한 값 대신 조건의 경계를 찾는 문제에 이진 탐색을 적용하는 방식입니다 |

## Before / After

정렬된 리스트에서 값을 찾는 두 가지 방법입니다.

```python
# before: linear search — O(n)
def search(data, target):
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1
```

```python
# after: binary search — O(log n)
def search(data, target):
    left, right = 0, len(data) - 1
    while left <= right:
        mid = (left + right) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

## 단계별 실습

### Step 1: Implement Linear Search

```python
def linear_search(data: list, target) -> int:
    """Linear search — O(n)."""
    for i, value in enumerate(data):
        if value == target:
            return i
    return -1

data = [4, 2, 7, 1, 9, 3, 8]
print(linear_search(data, 9))   # 4
print(linear_search(data, 5))   # -1

# No sorting required — works on any list
```

선형 탐색의 장점은 단순함과 범용성입니다. 데이터가 정렬되어 있지 않아도 바로 사용할 수 있지만, 큰 데이터에서는 비용이 빠르게 커집니다.

### Step 2: Implement Binary Search

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """Binary search — O(log n), requires sorted data."""
    left, right = 0, len(sorted_data) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_data[mid] == target:
            return mid
        elif sorted_data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

data = [1, 3, 5, 7, 9, 11, 13, 15]
print(binary_search(data, 9))    # 4
print(binary_search(data, 10))   # -1
```

이진 탐색의 핵심 전제는 정렬입니다. 이 조건이 맞으면 비교 횟수를 급격히 줄일 수 있지만, 정렬되지 않은 데이터에 적용하면 결과가 틀립니다.

### Step 3: Use the bisect Module

```python
import bisect

data = [1, 3, 5, 7, 9, 11, 13, 15]

# Find insertion point (maintains sorted order)
pos = bisect.bisect_left(data, 9)
print(f"Position of 9: {pos}")  # 4

# Check whether a value exists
def bisect_search(sorted_data: list[int], target: int) -> int:
    pos = bisect.bisect_left(sorted_data, target)
    if pos < len(sorted_data) and sorted_data[pos] == target:
        return pos
    return -1

print(bisect_search(data, 9))    # 4
print(bisect_search(data, 10))   # -1

# Insert into a sorted list
scores = [70, 80, 90]
bisect.insort(scores, 85)
print(scores)  # [70, 80, 85, 90]
```

실무와 코딩 테스트 모두에서, 직접 이진 탐색을 매번 작성하기보다 `bisect`를 적절히 활용하는 편이 안전하고 빠른 경우가 많습니다.

### Step 4: Lower Bound and Upper Bound

```python
import bisect

data = [1, 3, 5, 5, 5, 7, 9]

# bisect_left: position of the first occurrence
print(bisect.bisect_left(data, 5))   # 2

# bisect_right: position after the last occurrence
print(bisect.bisect_right(data, 5))  # 5

# Count occurrences of 5
count = bisect.bisect_right(data, 5) - bisect.bisect_left(data, 5)
print(f"Count of 5: {count}")  # 3

# First index >= 5
lower = bisect.bisect_left(data, 5)
print(f"First position >= 5: {lower}")  # 2

# First index > 5
upper = bisect.bisect_right(data, 5)
print(f"First position > 5: {upper}")   # 5
```

이 차이를 이해하면 중복 구간 길이 계산, 특정 기준 이상 값의 시작점 찾기 같은 문제를 훨씬 깔끔하게 풀 수 있습니다.

### Step 5: Performance Comparison

```python
import time
import bisect

def benchmark_search(n: int):
    data = list(range(n))
    target = n - 1  # worst case

    # Linear search
    start = time.perf_counter()
    linear_search(data, target)
    t_linear = time.perf_counter() - start

    # Binary search
    start = time.perf_counter()
    binary_search(data, target)
    t_binary = time.perf_counter() - start

    # bisect
    start = time.perf_counter()
    bisect.bisect_left(data, target)
    t_bisect = time.perf_counter() - start

    print(f"n={n:>10,}: linear={t_linear:.6f}s  binary={t_binary:.6f}s  bisect={t_bisect:.6f}s")

for n in [10_000, 100_000, 1_000_000]:
    benchmark_search(n)
```

입력이 커질수록 선형 탐색과 이진 탐색의 차이는 눈에 띄게 벌어집니다. `bisect`가 직접 구현보다 더 빠른 이유도 함께 확인할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 선형 탐색은 정렬되지 않은 데이터에도 동작하지만, 이진 탐색은 정렬이 필수입니다.
- 이진 탐색은 100만 개 데이터도 많아야 20번 정도의 비교로 처리합니다.
- `bisect` 모듈은 C로 구현되어 있어 손으로 작성한 이진 탐색보다 더 빠른 경우가 많습니다.
- `bisect_left`와 `bisect_right`의 차이를 이해하면 문제 변형 대응력이 크게 올라갑니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 정렬되지 않은 데이터에 이진 탐색 사용 | 잘못된 결과를 냅니다 | 먼저 정렬하거나 정렬 상태를 보장합니다 |
| mid 계산을 부정확하게 이해함 | 일부 언어에서는 오버플로우 문제가 있습니다 | `left + (right - left) // 2` 패턴도 익혀 둡니다 |
| `while left < right`로 잘못 구현 | 마지막 원소를 놓칠 수 있습니다 | 기본형에서는 `<=`를 사용합니다 |
| left/right 갱신 실수 | 수렴하지 않아 무한 루프가 납니다 | 항상 `mid + 1`, `mid - 1`을 의식합니다 |
| bisect 결과를 바로 인덱스로 확정함 | 값이 없어도 삽입 위치는 반환됩니다 | 반환 위치의 실제 값을 다시 확인합니다 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스 B-Tree 인덱스는 이진 탐색 원리를 활용합니다.
- 로그 분석 도구는 시간 범위의 시작점과 끝점을 찾을 때 이진 탐색을 사용합니다.
- 버그를 도입한 커밋을 찾는 `git bisect`도 같은 아이디어입니다.
- 게임 매치메이킹은 비슷한 실력 범위를 찾을 때 이진 탐색 응용이 가능합니다.
- A/B 테스트에서는 적절한 임계값을 찾는 데 파라메트릭 서치가 쓰이기도 합니다.

## 현업에서는 이렇게 생각합니다

실제로는 매번 이진 탐색을 처음부터 구현하지 않을 수 있습니다. `bisect`나 데이터베이스 인덱스가 대부분의 상황을 대신합니다. 그래도 이진 탐색을 이해하면, 조건의 경계를 찾는 파라메트릭 서치 같은 강력한 패턴을 다룰 수 있습니다.

정렬된 데이터에서 "조건을 처음 만족하는 지점" 또는 "마지막으로 만족하는 지점"을 찾는 감각은 코딩 테스트에서 매우 자주 등장합니다.

## 체크리스트

- [ ] 선형 탐색과 이진 탐색의 시간 복잡도를 비교할 수 있습니다
- [ ] while 루프로 이진 탐색을 구현할 수 있습니다
- [ ] `bisect_left`와 `bisect_right`의 차이를 설명할 수 있습니다
- [ ] 이진 탐색의 전제 조건이 정렬임을 설명할 수 있습니다
- [ ] 이진 탐색의 실무 활용 예를 말할 수 있습니다

## 연습 문제

1. 정렬된 리스트에서 특정 값 이상인 원소 개수를 `O(log n)`에 구하는 함수를 작성해 보세요.
2. 재귀 방식의 이진 탐색을 구현해 보세요.
3. 정수 `N`의 제곱근을 이진 탐색으로 소수점 여섯째 자리까지 구해 보세요.

## 정리와 다음 글

선형 탐색은 `O(n)`, 이진 탐색은 `O(log n)`입니다. 이진 탐색은 정렬이라는 전제가 필요하지만, 데이터가 커질수록 성능 차이는 매우 극적입니다. 다음 글에서는 데이터를 순서 있게 만드는 핵심 알고리즘, 정렬을 다룹니다.

## 실전 패턴 추가: 정렬과 탐색 구현을 문제 유형별로 선택하기

알고리즘 문제에서는 코드 길이보다 선택 기준이 더 중요합니다. 입력 크기, 데이터 분포, 정렬 여부에 따라 정렬/탐색 전략이 달라집니다. 아래 예시는 같은 정수 배열을 다루더라도 어떤 조건에서 어떤 구현을 고르는지 보여 줍니다.

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def merge_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    less = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    greater = [x for x in nums if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)
```

실무 판단은 보통 이렇게 정리됩니다. 이미 정렬된 리스트에서 존재 여부를 반복 조회하면 이진 탐색이 기본 선택입니다. 입력이 계속 바뀌고 안정 정렬이 필요하면 병합 정렬 계열이 유리하고, 평균 성능과 구현 단순성을 우선하면 퀵 정렬 계열이 자주 선택됩니다. 코딩 테스트에서는 Python 내장 `sort()`가 Timsort 기반이라 거의 항상 가장 실용적인 기본값이지만, 원리를 직접 구현해 보면 경계 조건과 복잡도 해석 능력이 크게 좋아집니다.

## 처음 질문으로 돌아가기

- **선형 탐색은 어떻게 동작하고, 한계는 무엇일까요?**
  - 본문의 기준은 선형 탐색과 이진 탐색를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **이진 탐색은 어떤 원리로 동작하며 어떻게 구현할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python의 `bisect` 모듈은 언제 유용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- **선형 탐색과 이진 탐색 (현재 글)**
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — bisect](https://docs.python.org/3/library/bisect.html)
- [Real Python — Binary Search in Python](https://realpython.com/binary-search-python/)
- [GeeksforGeeks — Binary Search](https://www.geeksforgeeks.org/binary-search/)
- [LeetCode — Binary Search Problems](https://leetcode.com/tag/binary-search/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/03-linear-and-binary-search)

Tags: Python, Algorithms, Linear Search, Binary Search, bisect
