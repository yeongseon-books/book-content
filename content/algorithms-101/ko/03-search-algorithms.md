---
series: algorithms-101
episode: 3
title: 탐색 알고리즘
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

# 탐색 알고리즘

정렬된 정수 백만 개가 있을 때, 원하는 값을 찾으려면 처음부터 끝까지 다 봐야 할까요? 이 글은 Algorithms 101 시리즈의 세 번째 글입니다. 여기서는 선형 탐색, 이진 탐색, Python의 `bisect`, 그리고 답 자체를 이진 탐색하는 parametric search까지 다룹니다.

## 이 글에서 다룰 문제

- 선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?
- 정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?
- lower bound와 upper bound는 각각 어디에 쓰일까요?
- `bisect` 모듈은 어떻게 안전하게 활용할 수 있을까요?

## 왜 중요한가

탐색은 거의 모든 시스템의 기본 연산입니다. 데이터베이스 조회, 로그 검색, 추천 후보 탐색, 게임 매칭은 모두 탐색 문제로 환원됩니다. 잘못된 선택 하나가 시스템 전체 응답 시간을 끌어내릴 수 있습니다. 또한 이진 탐색은 단순 조회를 넘어 parametric search라는 더 큰 패턴으로 확장됩니다.

> 이진 탐색을 모르면 알고리즘 책의 절반을 놓친 셈입니다.

## 한눈에 보는 개념

> 선형 탐색은 첫 원소부터 차례로 비교하므로 O(n)입니다. 이진 탐색은 정렬된 순서를 이용해 매 단계 후보의 절반을 버리므로 O(log n)입니다. 백만 개 원소에서는 선형 탐색이 백만 번 가까이 비교할 수 있지만, 이진 탐색은 대략 20번이면 충분합니다. 이 차이는 오직 입력이 정렬되어 있다는 전제에서 나옵니다.

```text
Linear  [3, 1, 4, 1, 5, 9, 2, 6]   target=9
            8 comparisons → O(n)

Binary  [1, 1, 2, 3, 4, 5, 6, 9]   target=5
            4 < 5 < 6 → right half
            5 == 5 → found
            ≈ log(8) = 3 comparisons → O(log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 선형 탐색 | 첫 원소부터 차례로 비교하는 탐색 |
| 이진 탐색 | 정렬된 데이터에서 후보를 절반씩 줄이는 탐색 |
| lower bound | target 이상이 처음 나타나는 위치 |
| upper bound | target 초과가 처음 나타나는 위치 |
| parametric search | 답 자체를 이진 탐색하는 기법 |

## Before / After

**Before — 정렬된 데이터에서도 선형 탐색:**

```python
def contains(sorted_arr, x):
    for v in sorted_arr:
        if v == x:
            return True
    return False
# O(n) — wastes the sortedness
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
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 5))   # 4
print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 7))   # -1
```

정렬 여부와 무관하게 동작하지만 비용은 언제나 O(n)을 냅니다.

### 2단계: 이진 탐색 구현

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

arr = sorted([3, 1, 4, 1, 5, 9, 2, 6])
print(binary_search(arr, 5))
```

핵심은 `mid = (lo + hi) // 2`입니다. 종료 조건 `lo <= hi`와 `lo`, `hi` 갱신이 한 글자만 어긋나도 무한 루프로 이어질 수 있습니다.

### 3단계: lower bound와 upper bound

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

arr = [1, 2, 2, 2, 3, 4, 5]
print(lower_bound(arr, 2))                                  # 1
print(upper_bound(arr, 2))                                  # 4
print(upper_bound(arr, 2) - lower_bound(arr, 2))            # 3
```

이 두 변형만 익혀도 개수 세기, 삽입 위치 찾기, 첫 등장 위치 찾기 같은 문제를 한 도구로 처리할 수 있습니다.

### 4단계: `bisect` 사용

```python
import bisect

arr = [1, 2, 4, 4, 4, 6, 8]
print(bisect.bisect_left(arr, 4))    # 2
print(bisect.bisect_right(arr, 4))   # 5

bisect.insort(arr, 5)
print(arr)
```

표준 라이브러리는 이미 검증된 구현을 제공합니다. 연습 목적이 아니라면 직접 구현보다 `bisect`를 우선하는 편이 안전합니다.

### 5단계: Parametric search

```python
# Cut n logs into m equal pieces. Find the maximum length per piece.
def can_make(logs, length, m):
    return sum(log // length for log in logs) >= m

def max_cut_length(logs, m):
    lo, hi = 1, max(logs)
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_make(logs, mid, m):
            lo = mid + 1
        else:
            hi = mid - 1
    return hi

print(max_cut_length([802, 743, 457, 539], 11))   # 200
```

답의 가능 여부가 단조롭다면, 즉 짧으면 가능하고 길면 불가능한 구조라면 답 자체를 이진 탐색할 수 있습니다. 많은 최적화 문제가 이 패턴으로 단순화됩니다.

## 이 글에서 먼저 가져갈 점

- 정렬된 데이터에 선형 탐색을 쓰는 것은 기회를 버리는 일입니다.
- 이진 탐색의 버그는 주로 `mid` 갱신과 종료 조건에 숨어 있습니다.
- lower/upper bound 변형이 실전 문제 대부분을 덮습니다.
- `bisect`는 임시 구현보다 빠르고 안전합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정렬되지 않은 데이터에 이진 탐색 적용 | 잘못된 결과 | 정렬 전제를 문서와 코드에 명시합니다 |
| `(lo + hi) / 2` 오버플로우 패턴 무시 | C/C++에서 음수 인덱스 가능 | Python은 안전하지만 일반식은 `lo + (hi - lo) // 2`를 기억합니다 |
| 경계 갱신을 잘못 씀 | 무한 루프 | lower/upper bound 템플릿을 익힙니다 |
| `bisect` 대신 매번 직접 구현 | 미묘한 버그 | 표준 라이브러리를 먼저 사용합니다 |
| 모든 원소가 비교 가능하다고 가정 | TypeError | 필요하면 key 기준을 별도로 둡니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스 조회는 이진 탐색의 일반화입니다.
- 시계열 조회는 정렬된 로그에서 시간값을 이진 탐색합니다.
- 게임 매칭은 정렬된 점수대에서 비슷한 상대를 찾습니다.
- 메모리 할당기 내부에도 이진 탐색 변형이 등장합니다.
- 반복 조회가 많다면 "한 번 정렬 + 여러 번 이진 탐색"이 선형 탐색 반복보다 훨씬 낫습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "정렬됨"이라는 단어를 보는 순간 이진 탐색 가능성을 떠올립니다. 또한 한 번 정렬해 두고 여러 번 이진 탐색하는 비용과, 그때그때 선형 탐색하는 비용을 함께 비교합니다. 반복 조회가 있는 문제에서는 전처리 비용이 거의 항상 이깁니다.

또한 "가장 큰 X such that ..." 같은 문장을 보면 답의 단조성을 먼저 확인합니다. 가능 여부가 한 방향으로만 바뀐다면, 그것은 parametric search를 적용하라는 강한 신호입니다.

## 체크리스트

- [ ] 선형 탐색과 이진 탐색의 비용 차이를 직관적으로 느끼는가
- [ ] 이진 탐색의 종료 조건을 정확히 쓸 수 있는가
- [ ] lower bound와 upper bound의 차이를 이해하는가
- [ ] `bisect` 사용이 익숙한가
- [ ] 언제 parametric search를 써야 하는지 감을 잡았는가

## 연습 문제

1. 정렬된 배열에서 target의 첫 위치와 마지막 위치를 반환하는 함수를 작성해 보세요. `lower_bound`와 `upper_bound`를 활용해 보세요.

2. `[4,5,6,7,0,1,2]`처럼 회전된 정렬 배열에서 O(log n)으로 값을 찾는 함수를 구현해 보세요. 이진 탐색의 변형 문제입니다.

3. 크기 n, m인 두 정렬 배열의 합집합에서 k번째 작은 원소를 O(log(n+m))에 찾는 방법을 설계해 보세요. 고전적인 이진 탐색 응용입니다.

## 정리 및 다음 단계

탐색 비용은 데이터에 구조가 있는지에 따라 크게 달라집니다. 정렬이 있으면 O(n)을 O(log n)으로 줄일 수 있고, 같은 발상은 parametric search로 확장됩니다. lower/upper bound 템플릿을 몸에 익히고, 일상적인 작업에는 `bisect`를 적극적으로 활용하는 것이 좋습니다.

다음 글에서는 정렬 알고리즘을 다룹니다. mergesort, quicksort, heapsort의 트레이드오프와 Python의 `sorted`가 왜 Timsort를 쓰는지 살펴보겠습니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- **탐색 알고리즘 (현재 글)**
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `bisect` documentation](https://docs.python.org/3/library/bisect.html)
- [Wikipedia — Binary Search Algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)
- [Open Data Structures — Searching](https://opendatastructures.org/)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 3](https://algs4.cs.princeton.edu/30searching/)

Tags: Computer Science, 알고리즘, 탐색, 이진 탐색, 선형 탐색, bisect
