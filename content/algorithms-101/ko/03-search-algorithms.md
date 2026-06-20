---
series: algorithms-101
episode: 3
title: "Algorithms 101 (3/10): 탐색 알고리즘"
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
  - 탐색
  - 이진 탐색
  - 선형 탐색
  - bisect
seo_description: 선형 탐색과 이진 탐색의 차이, 정렬된 데이터의 위력, 그리고 Python bisect의 실전 사용법을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (3/10): 탐색 알고리즘

정렬된 정수 백만 개가 있을 때, 원하는 값을 찾으려면 처음부터 끝까지 다 봐야 할까요? 여기서는 선형 탐색, 이진 탐색, Python의 `bisect`, 그리고 답 자체를 이진 탐색하는 parametric search까지 다룹니다.

이 글은 Algorithms 101 시리즈의 3번째 글입니다.

![Algorithms 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/03/03-01-big-picture.ko.png)
*Algorithms 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- 선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?
- 정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?
- lower bound와 upper bound는 각각 어디에 쓰일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

탐색은 거의 모든 시스템의 기본 연산입니다. 데이터베이스 조회, 로그 검색, 추천 후보 탐색, 게임 매칭은 모두 탐색 문제로 환원됩니다. 잘못된 선택 하나가 시스템 전체 응답 시간을 끌어내릴 수 있습니다. 또한 이진 탐색은 단순 조회를 넘어 parametric search라는 더 큰 패턴으로 확장됩니다.

> 이진 탐색을 모르면 알고리즘 책의 절반을 놓친 셈입니다.

> 선형 탐색은 첫 원소부터 차례로 비교하므로 O(n)입니다. 이진 탐색은 정렬된 순서를 이용해 매 단계 후보의 절반을 버리므로 O(log n)입니다. 백만 개 원소에서는 선형 탐색이 백만 번 가까이 비교할 수 있지만, 이진 탐색은 대략 20번이면 충분합니다. 이 차이는 오직 입력이 정렬되어 있다는 전제에서 나옵니다.

```text
Linear  [3, 1, 4, 1, 5, 9, 2, 6]   target=9
            8 comparisons → O(n)

Binary  [1, 1, 2, 3, 4, 5, 6, 9]   target=5
            mid=4 → 4 < 5 → right half
            mid=5 → 5 == 5 → found
            ≈ log(8) = 3 comparisons → O(log n)
```

| 용어 | 설명 |
| --- | --- |
| 선형 탐색 | 첫 원소부터 차례로 비교하는 탐색 |
| 이진 탐색 | 정렬된 데이터에서 후보를 절반씩 줄이는 탐색 |
| lower bound | target 이상이 처음 나타나는 위치 |
| upper bound | target 초과가 처음 나타나는 위치 |
| parametric search | 답 자체를 이진 탐색하는 기법 |

## 개선 전 / 개선 후

**Before — 정렬된 데이터에서도 선형 탐색:**

```python
def contains(sorted_arr, x):
    for v in sorted_arr:
        if v == x:
            return True
    return False
# O(n) — 정렬을 낭비합니다.
```

**After — `bisect` 기반 이진 탐색:**

```python
import bisect
def contains(sorted_arr, x):
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x
# O(log n)
```

## 단계별로 따라가기

### 1단계: 선형 탐색 구현

```python
def linear_search(arr, target):
    """정렬 여부와 무관하게 동작. O(n) 시간, O(1) 공간."""
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

# 경계 케이스 검증
assert linear_search([3, 1, 4, 1, 5, 9, 2, 6], 5) == 4
assert linear_search([3, 1, 4, 1, 5, 9, 2, 6], 7) == -1
assert linear_search([], 1) == -1
assert linear_search([7], 7) == 0
```

정렬 여부와 무관하게 동작하지만 비용은 언제나 O(n)입니다. 정렬된 데이터에서 이 함수를 쓰는 것은 기회를 버리는 일입니다.

### 2단계: 이진 탐색 구현

```python
def binary_search(arr, target):
    """정렬된 배열에서 target을 찾아 인덱스 반환. O(log n) 시간, O(1) 공간."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2   # 오버플로우 방지
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

arr = sorted([3, 1, 4, 1, 5, 9, 2, 6])
assert binary_search(arr, 5) == arr.index(5)
assert binary_search(arr, 7) == -1
assert binary_search([], 1) == -1
```

핵심은 `mid = lo + (hi - lo) // 2`입니다. `(lo + hi) // 2`는 Python에서는 안전하지만 정수 오버플로우가 발생하는 언어(C, Java)에서는 위험합니다.

### 3단계: lower bound와 upper bound

```python
def lower_bound(arr, target):
    """target 이상이 처음 나타나는 위치 반환. bisect_left와 동일."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo   # arr[lo] >= target인 가장 작은 lo

def upper_bound(arr, target):
    """target 초과가 처음 나타나는 위치 반환. bisect_right와 동일."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo   # arr[lo] > target인 가장 작은 lo

arr = [1, 2, 2, 2, 3, 4, 5]
lb = lower_bound(arr, 2)   # 1 — 첫 번째 2의 위치
ub = upper_bound(arr, 2)   # 4 — 마지막 2 다음 위치
count = ub - lb            # 3 — 2가 나타나는 횟수
print(f"lower={lb}, upper={ub}, count={count}")
```

이 두 변형만 익혀도 개수 세기, 삽입 위치 찾기, 첫/마지막 등장 위치 찾기 같은 문제를 한 도구로 처리할 수 있습니다.

### 4단계: `bisect` 사용

```python
import bisect

arr = [1, 2, 4, 4, 4, 6, 8]
print(bisect.bisect_left(arr, 4))    # 2 — lower bound
print(bisect.bisect_right(arr, 4))   # 5 — upper bound

# 정렬 상태를 유지하며 삽입
bisect.insort(arr, 5)
print(arr)   # [1, 2, 4, 4, 4, 5, 6, 8]

# 조회
def contains_bisect(sorted_arr, x):
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x

assert contains_bisect([1, 2, 4, 4, 4, 6, 8], 4) == True
assert contains_bisect([1, 2, 4, 4, 4, 6, 8], 3) == False
```

표준 라이브러리는 이미 검증된 구현을 제공합니다. 연습 목적이 아니라면 직접 구현보다 `bisect`를 우선하는 편이 안전합니다.

### 5단계: Parametric search

```python
def can_make(logs, length, m):
    """주어진 길이로 m개 이상 자를 수 있는가?"""
    return sum(log // length for log in logs) >= m

def max_cut_length(logs, m):
    """n개의 통나무를 m개의 동일한 조각으로 자를 때 최대 길이."""
    lo, hi = 1, max(logs)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if can_make(logs, mid, m):
            lo = mid + 1    # 더 길게 자를 수 있음
        else:
            hi = mid - 1    # 너무 길음
    return hi

result = max_cut_length([802, 743, 457, 539], 11)
print(result)   # 200
assert can_make([802, 743, 457, 539], 200, 11)
assert not can_make([802, 743, 457, 539], 201, 11)
```

답의 가능 여부가 단조롭다면, 즉 짧으면 가능하고 길면 불가능한 구조라면 답 자체를 이진 탐색할 수 있습니다. 많은 최적화 문제가 이 패턴으로 단순화됩니다.

### 6단계: 이진 탐색 응용 — 회전된 정렬 배열

```python
def search_rotated(arr, target):
    """회전된 정렬 배열에서 O(log n) 탐색."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        # 왼쪽 절반이 정렬됨
        if arr[lo] <= arr[mid]:
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:  # 오른쪽 절반이 정렬됨
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
```

## 심화: 이진 탐색 버그 패턴과 방어법

이진 탐색은 구현이 쉬워 보이지만 실제로 버그가 많습니다. 대표적인 버그 4가지와 방어법을 정리합니다.

```python
# 버그 1: lo <= hi 대신 lo < hi 사용 → 요소 하나를 놓침
def buggy_search_1(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:    # 버그: lo == hi 일 때 검사 안 함
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1  # arr[lo]가 target일 수도 있는데 놓침

# 버그 2: hi = mid 대신 hi = mid - 1 → 무한 루프 (lower_bound 패턴에서)
def buggy_lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1  # 버그: hi = mid 여야 함
    return lo

# 버그 3: mid 계산 시 오버플로우 (Python은 안전하지만 C/Java는 위험)
def safe_mid(lo, hi):
    return lo + (hi - lo) // 2   # 안전
    # return (lo + hi) // 2      # C에서는 위험

# 버그 4: 빈 배열 처리 누락
def robust_binary_search(arr, target):
    if not arr:    # 명시적 방어
        return -1
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

# 검증으로 버그 포착
assert robust_binary_search([], 5) == -1
assert robust_binary_search([5], 5) == 0
assert robust_binary_search([1, 3, 5, 7], 5) == 2
assert robust_binary_search([1, 3, 5, 7], 6) == -1
```

**이진 탐색 변형 선택 가이드:**

```text
"값이 존재하는지"           → bisect_left + 일치 확인
"첫 번째 등장 위치"         → lower_bound (bisect_left)
"마지막 등장 위치"          → upper_bound - 1 (bisect_right - 1)
"삽입 위치 (중복 앞)"       → bisect_left
"삽입 위치 (중복 뒤)"       → bisect_right
"범위 내 개수"              → bisect_right(target) - bisect_left(target)
"최솟값 such that f(x)≥k" → parametric search
```

## 탐색 알고리즘 Big-O 비교

| 알고리즘 | 시간 복잡도 | 공간 복잡도 | 전제 조건 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| 선형 탐색 | O(n) | O(1) | 없음 | 비정렬, 소규모, 단발성 탐색 |
| 이진 탐색 | O(log n) | O(1) | 정렬된 배열 | 반복 조회, 대규모 정렬 데이터 |
| bisect_left/right | O(log n) | O(1) | 정렬된 배열 | Python 실무, 삽입 위치 |
| 해시 탐색(dict) | O(1) 평균 | O(n) | 해시 가능 키 | 키-값 조회, 중복 체크 |
| 보간 탐색 | O(log log n) 평균 | O(1) | 균등 분포 정렬 배열 | 균등 분포 데이터 |
| 지수 탐색 | O(log n) | O(1) | 정렬된 배열 | 무한 또는 크기 불명 배열 |
| Parametric search | O(log(범위) × f(n)) | O(1) | 단조 조건 함수 | 최적화 문제, 결정 문제 |

## 이 글에서 먼저 가져갈 점

- 정렬된 데이터에 선형 탐색을 쓰는 것은 기회를 버리는 일입니다.
- 이진 탐색의 버그는 주로 `mid` 갱신과 종료 조건에 숨어 있습니다.
- lower/upper bound 변형이 실전 문제 대부분을 덮습니다.
- `bisect`는 임시 구현보다 빠르고 안전합니다.
- 단조 조건 함수가 있으면 parametric search를 고려하세요.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정렬되지 않은 데이터에 이진 탐색 적용 | 잘못된 결과 | 정렬 전제를 문서와 코드에 명시합니다 |
| `(lo + hi) // 2` 오버플로우 무시 | C/C++에서 음수 인덱스 가능 | `lo + (hi - lo) // 2` 형식을 습관화합니다 |
| `lo <= hi` vs `lo < hi` 혼용 | 무한 루프 또는 요소 누락 | 표준 조건 함수를 익히고 그대로 사용합니다 |
| `bisect` 대신 매번 직접 구현 | 미묘한 버그 | 표준 라이브러리를 먼저 사용합니다 |
| 반환값이 인덱스인지 값인지 혼동 | 런타임 에러 | 함수 시그니처에 반환 타입을 명시합니다 |
| parametric search에서 단조성 검증 생략 | 오답 | 작은 입력에서 단조성을 직접 확인합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스 조회는 이진 탐색의 일반화입니다.
- 시계열 조회는 정렬된 로그에서 시간값을 이진 탐색합니다.
- 게임 매칭은 정렬된 점수대에서 비슷한 상대를 찾습니다.
- 메모리 할당기 내부에도 이진 탐색 변형이 등장합니다.
- 반복 조회가 많다면 "한 번 정렬 + 여러 번 이진 탐색"이 선형 탐색 반복보다 훨씬 낫습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "정렬됨"이라는 단어를 보는 순간 이진 탐색 가능성을 떠올립니다. 또한 한 번 정렬해 두고 여러 번 이진 탐색하는 비용과, 그때그때 선형 탐색하는 비용을 함께 비교합니다. 반복 조회가 있는 문제에서는 전처리 비용이 거의 항상 이깁니다.

또한 "가장 큰 X such that ..." 같은 문장을 보면 답의 단조성을 먼저 확인합니다. 가능 여부가 한 방향으로만 바뀐다면, 이는 parametric search를 적용하라는 강한 신호입니다.

## 운영 체크리스트

- [ ] 선형 탐색과 이진 탐색의 비용 차이를 직관적으로 느끼는가
- [ ] 이진 탐색의 종료 조건을 정확히 쓸 수 있는가
- [ ] lower bound와 upper bound의 차이를 이해하는가
- [ ] `bisect` 사용이 익숙한가
- [ ] 언제 parametric search를 써야 하는지 감을 잡았는가
- [ ] 회전된 정렬 배열 같은 변형 문제에 대응할 수 있는가

## 연습 문제

1. 정렬된 배열에서 target의 첫 위치와 마지막 위치를 반환하는 함수를 작성해 보세요. `lower_bound`와 `upper_bound`를 활용해 보세요.

2. `[4,5,6,7,0,1,2]`처럼 회전된 정렬 배열에서 O(log n)으로 값을 찾는 함수를 구현해 보세요. 이진 탐색의 변형 문제입니다.

3. 크기 n, m인 두 정렬 배열의 합집합에서 k번째 작은 원소를 O(log(n+m))에 찾는 방법을 설계해 보세요. 고전적인 이진 탐색 응용입니다.

4. Parametric search를 이용해 "n명의 학생이 m개의 방에 들어갈 때, 각 방의 최대 학생 수를 최소화하라"는 문제를 O(n log n)으로 풀어 보세요.

## 정리 및 다음 단계

탐색 비용은 데이터에 구조가 있는지에 따라 크게 달라집니다. 정렬이 있으면 O(n)을 O(log n)으로 줄일 수 있고, 같은 발상은 parametric search로 확장됩니다. lower/upper bound 템플릿을 몸에 익히고, 일상적인 작업에는 `bisect`를 적극적으로 활용하는 것이 좋습니다.

다음 글에서는 정렬 알고리즘을 다룹니다. mergesort, quicksort, heapsort의 트레이드오프와 Python의 `sorted`가 왜 Timsort를 쓰는지 봅니다.

## 처음 질문으로 돌아가기

- **선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?**
  - n=10^6에서 선형 탐색은 최대 백만 번 비교하지만 이진 탐색은 약 20번으로 충분합니다. 이 차이는 O(n)과 O(log n)의 계층 차이로, 입력이 커질수록 격차가 기하급수적으로 벌어집니다.
- **정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?**
  - 정렬은 데이터에 "순서"라는 구조를 추가합니다. 이 구조를 활용하면 매 단계에서 탐색 후보의 절반을 제거할 수 있어 O(n)이 O(log n)으로 바뀝니다. 정렬 비용 O(n log n)을 지불하면 이후 모든 탐색이 O(log n)이 됩니다.
- **lower bound와 upper bound는 각각 어디에 쓰일까요?**
  - lower bound는 target 이상이 처음 나타나는 위치를 반환하므로 삽입 위치, 첫 등장 위치 찾기에 씁니다. upper bound는 target 초과가 처음 나타나는 위치를 반환하므로 마지막 등장 위치 다음, 범위 내 개수 계산(`ub - lb`)에 씁니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- **Algorithms 101 (3/10): 탐색 알고리즘 (현재 글)**
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `bisect` documentation](https://docs.python.org/3/library/bisect.html)
- [Wikipedia — Binary Search Algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)
- [Open Data Structures — Searching](https://opendatastructures.org/)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 3](https://algs4.cs.princeton.edu/30searching/)

Tags: Computer Science, 알고리즘, 탐색, 이진 탐색, 선형 탐색, bisect
