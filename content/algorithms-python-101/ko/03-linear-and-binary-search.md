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

![Algorithms with Python 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/03/03-01-big-picture.ko.png)
*Algorithms with Python 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- 선형 탐색은 어떻게 동작하고, 한계는 무엇일까요?
- 이진 탐색은 어떤 원리로 동작하며 어떻게 구현할까요?
- Python의 `bisect` 모듈은 언제 유용할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> 이진 탐색은 매 단계마다 남은 데이터의 절반을 제거해, 정렬된 데이터에서 `O(log n)`을 달성합니다.

## 개념 한눈에 보기

> 탐색 = 데이터 집합에서 원하는 값을 찾는 과정

```text
Linear search: [1, 3, 5, 7, 9, 11, 13] — find 9
→ 1, 3, 5, 7, 9 (5 comparisons)

Binary search: [1, 3, 5, 7, 9, 11, 13] — find 9
Step 1: mid=7, 9>7 → right half
Step 2: mid=11, 9<11 → left half
Step 3: mid=9, found! (3 comparisons)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Linear search | 처음부터 끝까지 하나씩 확인하는 탐색으로 `O(n)`입니다 |
| Binary search | 가운데 값을 기준으로 절반씩 줄여 가는 탐색으로, 정렬 데이터에서 `O(log n)`입니다 |
| bisect | Python 표준 라이브러리의 이진 탐색 모듈입니다 |
| Upper/lower bound | 특정 값 이상 또는 초과가 처음 나타나는 위치를 찾는 변형입니다 |
| Parametric search | 정확한 값 대신 조건의 경계를 찾는 문제에 이진 탐색을 적용하는 방식입니다 |

## 적용 전후 비교

정렬된 리스트에서 값을 찾는 두 가지 방법입니다.

```python
# before: 선형 탐색 — O(n)
def search(data, target):
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1
```

```python
# after: 이진 탐색 — O(log n)
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

### 단계 1: 선형 탐색 구현

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

# 정렬이 필요 없음 — 어떤 리스트에서도 동작
```

선형 탐색의 장점은 단순함과 범용성입니다. 데이터가 정렬되어 있지 않아도 바로 사용할 수 있지만, 큰 데이터에서는 비용이 빠르게 커집니다.

### 단계 2: 이진 탐색 구현

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

이진 탐색의 핵심 전제는 정렬입니다. 정렬되지 않은 데이터에 적용하면 결과가 틀립니다.

### 단계 3: bisect 모듈 사용하기

```python
import bisect

data = [1, 3, 5, 7, 9, 11, 13, 15]

# 삽입 위치 찾기 (정렬 순서 유지)
pos = bisect.bisect_left(data, 9)
print(f"Position of 9: {pos}")  # 4

# 값 존재 여부 확인
def bisect_search(sorted_data: list[int], target: int) -> int:
    pos = bisect.bisect_left(sorted_data, target)
    if pos < len(sorted_data) and sorted_data[pos] == target:
        return pos
    return -1

print(bisect_search(data, 9))    # 4
print(bisect_search(data, 10))   # -1

# 정렬된 리스트에 삽입
scores = [70, 80, 90]
bisect.insort(scores, 85)
print(scores)  # [70, 80, 85, 90]
```

실무와 코딩 테스트 모두에서, 직접 이진 탐색을 매번 작성하기보다 `bisect`를 적절히 활용하는 편이 안전하고 빠른 경우가 많습니다.

### 단계 4: 하한과 상한 (lower bound / upper bound)

```python
import bisect

data = [1, 3, 5, 5, 5, 7, 9]

# bisect_left: 첫 번째 출현 위치
print(bisect.bisect_left(data, 5))   # 2

# bisect_right: 마지막 출현 다음 위치
print(bisect.bisect_right(data, 5))  # 5

# 5의 출현 횟수 세기
count = bisect.bisect_right(data, 5) - bisect.bisect_left(data, 5)
print(f"Count of 5: {count}")  # 3

# 직접 구현: lower bound
def lower_bound(nums: list[int], target: int) -> int:
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left

# 직접 구현: upper bound
def upper_bound(nums: list[int], target: int) -> int:
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left

arr = [1, 2, 2, 2, 5, 7]
print(lower_bound(arr, 2), upper_bound(arr, 2))  # 1, 4
```

### 단계 5: 성능 비교

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

## 단계별 실행 추적 — 이진 탐색

`binary_search([1, 3, 5, 7, 9, 11, 13, 15], 9)` 실행을 한 단계씩 따라가 보겠습니다.

```text
입력: [1, 3, 5, 7, 9, 11, 13, 15], target=9
인덱스:  0  1  2  3  4   5   6   7

Step 1: left=0, right=7
  mid = (0+7)//2 = 3
  data[3] = 7
  9 > 7 → left = mid+1 = 4

Step 2: left=4, right=7
  mid = (4+7)//2 = 5
  data[5] = 11
  9 < 11 → right = mid-1 = 4

Step 3: left=4, right=4
  mid = (4+4)//2 = 4
  data[4] = 9
  9 == 9 → return 4

결과: 인덱스 4 (총 3번 비교)
선형 탐색이라면 5번 비교 필요
```

`lower_bound([1, 2, 2, 2, 5, 7], 2)` 추적:

```text
입력: [1, 2, 2, 2, 5, 7], target=2
범위: [left=0, right=6)

Step 1: mid=3, nums[3]=2 → 2 < 2? No → right=3
  범위: [0, 3)

Step 2: mid=1, nums[1]=2 → 2 < 2? No → right=1
  범위: [0, 1)

Step 3: mid=0, nums[0]=1 → 1 < 2? Yes → left=1
  범위: [1, 1)

종료: left=1 (2가 처음 나타나는 위치)
```

## 코딩 테스트 풀이 예시

**문제**: 정렬된 배열에서 특정 값 이상인 원소 개수를 `O(log n)`에 구하라.

```python
import bisect

def count_greater_equal(sorted_data: list[int], threshold: int) -> int:
    """
    정렬된 배열에서 threshold 이상인 원소 수를 반환합니다.
    시간 복잡도: O(log n)
    """
    pos = bisect.bisect_left(sorted_data, threshold)
    return len(sorted_data) - pos


# 테스트
data = [1, 3, 5, 7, 9, 11, 13]
print(count_greater_equal(data, 7))   # 4  (7, 9, 11, 13)
print(count_greater_equal(data, 14))  # 0  (없음)
print(count_greater_equal(data, 1))   # 7  (전부)
```

**문제**: 정수 N의 제곱근을 이진 탐색으로 구하라 (정수 부분).

```python
def integer_sqrt(n: int) -> int:
    """
    n의 정수 제곱근을 이진 탐색으로 구합니다.
    시간 복잡도: O(log n)
    """
    if n < 0:
        raise ValueError("음수의 제곱근은 없습니다")
    if n == 0:
        return 0

    left, right = 1, n
    result = 0

    while left <= right:
        mid = (left + right) // 2
        if mid * mid <= n:
            result = mid  # 가능한 후보 저장
            left = mid + 1
        else:
            right = mid - 1

    return result


# 테스트
print(integer_sqrt(16))   # 4
print(integer_sqrt(17))   # 4  (floor)
print(integer_sqrt(25))   # 5
print(integer_sqrt(0))    # 0
```

**단계별 추적** (`integer_sqrt(17)` 입력):

```text
n=17, left=1, right=17

Step 1: mid=9, 9*9=81 > 17 → right=8
Step 2: mid=4, 4*4=16 <= 17 → result=4, left=5
Step 3: mid=6, 6*6=36 > 17 → right=5
Step 4: mid=5, 5*5=25 > 17 → right=4
Step 5: left=5 > right=4 → 종료

결과: 4 (√17 ≈ 4.123, floor=4)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 정렬되지 않은 데이터에 이진 탐색 사용 | 잘못된 결과를 냅니다 | 먼저 정렬하거나 정렬 상태를 보장합니다 |
| mid 계산을 부정확하게 이해함 | 일부 언어에서는 오버플로우 문제가 있습니다 | `left + (right - left) // 2` 패턴도 익혀 둡니다 |
| `while left < right`로 잘못 구현 | 마지막 원소를 놓칠 수 있습니다 | 기본형에서는 `<=`를 사용합니다 |
| left/right 갱신 실수 | 수렴하지 않아 무한 루프가 납니다 | 항상 `mid + 1`, `mid - 1`을 의식합니다 |
| bisect 결과를 바로 인덱스로 확정함 | 값이 없어도 삽입 위치는 반환됩니다 | 반환 위치의 실제 값을 다시 확인합니다 |

## 복잡도 비교표

| 접근 | 전제 | 시간 복잡도 | 용도 |
|------|------|-------------|------|
| 선형 탐색 | 없음 | `O(n)` | 작은 입력, 정렬 안 됨 |
| 이진 탐색 | 정렬 필요 | `O(log n)` | 대규모 조회 |
| 정렬 + 이진 탐색 | 초기 정렬 비용 허용 | `O(n log n) + q log n` | 다중 질의 |
| bisect 모듈 | 정렬 필요 | `O(log n)` (C 구현) | 실무 추천 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스 B-Tree 인덱스는 이진 탐색 원리를 활용합니다.
- 로그 분석 도구는 시간 범위의 시작점과 끝점을 찾을 때 이진 탐색을 사용합니다.
- 버그를 도입한 커밋을 찾는 `git bisect`도 같은 아이디어입니다.
- 게임 매치메이킹은 비슷한 실력 범위를 찾을 때 이진 탐색 응용이 가능합니다.
- A/B 테스트에서는 적절한 임계값을 찾는 데 파라메트릭 서치가 쓰이기도 합니다.

## 현업에서는 이렇게 생각합니다

실제로는 매번 이진 탐색을 처음부터 구현하지 않을 수 있습니다. `bisect`나 데이터베이스 인덱스가 대부분의 상황을 대신합니다. 그래도 이진 탐색을 이해하면, 조건의 경계를 찾는 파라메트릭 서치 같은 강력한 패턴을 다룰 수 있습니다.

정렬된 데이터에서 "조건을 처음 만족하는 지점" 또는 "마지막으로 만족하는 지점"을 찾는 감각은 코딩 테스트에서 매우 자주 등장합니다.

## 운영 체크리스트

- [ ] 선형 탐색과 이진 탐색의 시간 복잡도를 비교할 수 있습니다
- [ ] while 루프로 이진 탐색을 구현할 수 있습니다
- [ ] `bisect_left`와 `bisect_right`의 차이를 설명할 수 있습니다
- [ ] 이진 탐색의 전제 조건이 정렬임을 설명할 수 있습니다
- [ ] lower bound / upper bound를 직접 구현할 수 있습니다

## 연습 문제

1. 정렬된 리스트에서 특정 값 이상인 원소 개수를 `O(log n)`에 구하는 함수를 작성해 보세요.
2. 재귀 방식의 이진 탐색을 구현해 보세요.
3. 정수 `N`의 제곱근을 이진 탐색으로 소수점 여섯째 자리까지 구해 보세요.

## 정리와 다음 글

선형 탐색은 `O(n)`, 이진 탐색은 `O(log n)`입니다. 이진 탐색은 정렬이라는 전제가 필요하지만, 데이터가 커질수록 성능 차이는 매우 극적입니다. 다음 글에서는 데이터를 순서 있게 만드는 핵심 알고리즘, 정렬을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- **Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색 (현재 글)**
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — bisect](https://docs.python.org/3/library/bisect.html)
- [Real Python — Binary Search in Python](https://realpython.com/binary-search-python/)
- [GeeksforGeeks — Binary Search](https://www.geeksforgeeks.org/binary-search/)
- [LeetCode — Binary Search Problems](https://leetcode.com/tag/binary-search/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/03-linear-and-binary-search)

Tags: Python, Algorithms, Linear Search, Binary Search, bisect
