---
series: algorithms-101
episode: 3
title: 탐색 알고리즘
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
  - 탐색
  - 이진 탐색
  - 선형 탐색
  - bisect
seo_description: 선형 탐색과 이진 탐색의 차이, 정렬된 데이터의 위력, 그리고 파이썬 bisect 모듈을 통한 실전 사용법을 정리합니다.
last_reviewed: '2026-05-04'
---

# 탐색 알고리즘

> Algorithms 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 100만 개의 정렬된 정수에서 특정 값을 찾는다면, 처음부터 끝까지 읽는 것 외에 더 좋은 방법이 있을까요?

> 탐색 알고리즘은 컬렉션 안에서 원하는 값을 찾는 절차입니다. 정렬되지 않은 데이터에서는 한 번에 하나씩 보는 선형 탐색 외에 방법이 없지만, 정렬된 데이터에서는 매 단계 절반을 버리는 이진 탐색으로 O(log n)에 찾을 수 있습니다. "정렬되어 있다"는 사전 조건 하나가 알고리즘의 차원을 바꿉니다. 파이썬에서는 `bisect` 모듈이 이를 표준으로 제공합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 선형 탐색과 이진 탐색의 동작과 비용
- 정렬된 데이터가 만드는 차원의 차이
- 이진 탐색의 변형들(좌측·우측 경계, 첫 등장 위치)
- `bisect` 모듈 사용법과 활용

## 왜 중요한가

탐색은 거의 모든 시스템의 기본 연산입니다. 잘못된 탐색 알고리즘은 시스템의 응답 시간을 통째로 망칩니다. 한편 이진 탐색의 사고는 단순한 검색을 넘어 "답이 단조롭다면 매개 변수 자체를 이진 탐색"하는 패턴(parametric search)으로도 확장됩니다.

> 이진 탐색을 모르면 알고리즘의 절반을 못 본 것과 같습니다.

## 개념 한눈에 보기

> 선형 탐색은 처음부터 끝까지 비교하므로 O(n)입니다. 이진 탐색은 정렬된 배열에서 매 단계 절반을 버리므로 O(log n)입니다. 100만 개에서 선형은 100만 번, 이진은 약 20번이면 충분합니다.

```text
선형 탐색  [3, 1, 4, 1, 5, 9, 2, 6]   target=9
              비교 8번 → O(n)

이진 탐색  [1, 1, 2, 3, 4, 5, 6, 9]   target=5
              4 < 5 < 6 → 우측 절반
              5 == 5 → 발견
              비교 ≈ log(8)=3번 → O(log n)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 선형 탐색 | 첫 원소부터 순서대로 비교 |
| 이진 탐색 | 정렬된 데이터에서 절반씩 버림 |
| 좌측 경계 | target 이상이 처음 나타나는 위치 |
| 우측 경계 | target 초과가 처음 나타나는 위치 |
| Parametric search | 답을 직접 이진 탐색하는 기법 |

## Before / After

**Before — 정렬된 데이터에서도 선형 탐색:**

```python
def contains(sorted_arr, x):
    for v in sorted_arr:
        if v == x:
            return True
    return False
# O(n) — 정렬을 활용 못 함
```

**After — 이진 탐색 사용:**

```python
import bisect
def contains(sorted_arr, x):
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x
# O(log n)
```

## 실습: 단계별로 따라하기

### 1단계: 선형 탐색 직접 구현

```python
def linear_search(arr, target):
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 5))   # 4
print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 7))   # -1
```

데이터의 정렬 여부와 무관하게 동작하지만 비용은 O(n)입니다.

### 2단계: 이진 탐색 직접 구현

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
print(binary_search(arr, 5))   # 5의 위치
print(binary_search(arr, 7))   # -1
```

핵심은 `mid = (lo + hi) // 2`와 절반 버리기. 종료 조건 `lo <= hi`와 `lo = mid + 1`, `hi = mid - 1`을 정확히 적어야 무한 루프를 피합니다.

### 3단계: 이진 탐색의 변형 — 좌측/우측 경계

```python
def lower_bound(arr, target):
    """target 이상이 처음 나오는 위치"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(arr, target):
    """target 초과가 처음 나오는 위치"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

arr = [1, 2, 2, 2, 3, 4, 5]
print(lower_bound(arr, 2))   # 1
print(upper_bound(arr, 2))   # 4
print(upper_bound(arr, 2) - lower_bound(arr, 2))   # 3 (2의 개수)
```

좌측·우측 경계만 알면 "범위 안의 개수", "삽입 위치", "첫 등장 위치"를 모두 풀 수 있습니다.

### 4단계: 파이썬 bisect 모듈

```python
import bisect

arr = [1, 2, 4, 4, 4, 6, 8]
print(bisect.bisect_left(arr, 4))    # 2
print(bisect.bisect_right(arr, 4))   # 5
print(bisect.bisect(arr, 4))         # 5 (= bisect_right)

# 정렬 유지하며 삽입
bisect.insort(arr, 5)
print(arr)   # [1, 2, 4, 4, 4, 5, 6, 8]
```

표준 라이브러리에 이미 검증된 구현이 있습니다. 직접 구현하는 것보다 안전합니다.

### 5단계: Parametric Search — 답을 이진 탐색

```python
# 문제: 길이가 정해진 통나무 n개에서 m개를 같은 길이로 자를 때 최대 길이
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

답이 단조 함수(길이가 짧으면 가능, 길면 불가능)이면 답 자체를 이진 탐색합니다. 알고리즘 대회에서 흔한 패턴입니다.

## 이 코드에서 주목할 점

- 정렬된 데이터에서 선형 탐색을 사용하면 알고리즘적 손실
- 이진 탐색의 종료 조건과 mid 갱신은 한 글자 차이로 무한 루프
- 좌측·우측 경계 변형으로 다양한 문제를 풀 수 있음
- `bisect`는 직접 구현보다 안전하고 빠름

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정렬 안 된 배열에 이진 탐색 | 잘못된 결과 | 정렬 보장을 코드 주석으로 명시 |
| `(lo + hi) / 2` 정수 오버플로우 | 큰 인덱스에서 음수 | Python은 안전, C++ 등에서는 `lo + (hi-lo)//2` |
| 경계 처리 오류 | 무한 루프 또는 off-by-one | 좌측/우측 경계 변형 외워두기 |
| bisect를 잊고 직접 구현 | 버그 | 표준 라이브러리 우선 |
| 비교 가능한 객체 가정 누락 | TypeError | 키 함수 분리 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스 조회: B-Tree 위에서 이진 탐색의 일반화
- 시계열 데이터: 시간으로 정렬된 로그에서 특정 시각 찾기
- 게임 매칭: 점수 기반 매칭에서 적정 상대를 이진 탐색
- 머신러닝 추론: 정렬된 임베딩에서 근접 이웃을 이진 탐색
- 운영체제: 빈 메모리 블록 탐색에 변형 이진 탐색 사용

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "정렬되어 있다면" 자동으로 이진 탐색을 떠올립니다. 또한 정렬되지 않은 데이터에 대해 "정렬 비용 + 이진 탐색이 더 빠른가?"를 비교합니다. 한 번 정렬하고 여러 번 탐색하는 패턴이 있다면 사전 정렬이 거의 항상 이깁니다.

또한 시니어는 "답이 단조롭다"는 신호를 놓치지 않습니다. 그러면 답 자체를 이진 탐색하는 parametric search로 시간 복잡도를 한 차원 떨어뜨릴 수 있습니다.

## 체크리스트

- [ ] 선형 탐색과 이진 탐색의 비용 차이를 직관적으로 갖고 있는가
- [ ] 이진 탐색의 종료 조건을 정확히 쓸 수 있는가
- [ ] 좌측·우측 경계의 의미를 이해했는가
- [ ] `bisect` 모듈을 자유롭게 사용하는가
- [ ] Parametric search 패턴을 인식할 수 있는가

## 연습 문제

1. 정렬된 배열에서 target의 첫 등장과 마지막 등장 인덱스를 반환하는 함수를 작성하세요. lower_bound와 upper_bound로 풀어 봅니다.

2. 회전된 정렬 배열(예: `[4,5,6,7,0,1,2]`)에서 특정 값의 인덱스를 O(log n)에 찾는 알고리즘을 구현하세요. 일반 이진 탐색의 변형이 필요합니다.

3. 길이 n의 정렬된 두 배열 A, B의 합집합에서 k번째 작은 값을 O(log(n+m))에 찾는 알고리즘을 작성하세요. 이진 탐색의 응용 문제입니다.

## 정리 및 다음 단계

탐색 알고리즘은 데이터에 사전 조건이 있는지에 따라 비용이 한 차원 달라집니다. 정렬된 데이터에서는 이진 탐색이 표준이며, 좌측·우측 경계 변형만 익히면 다양한 문제를 풀 수 있습니다. 답이 단조롭다면 답 자체를 이진 탐색하는 parametric search 패턴까지 확장됩니다.

다음 글에서는 정렬 알고리즘을 살펴봅니다. 비교 기반 정렬의 한계, mergesort/quicksort/heapsort의 트레이드오프, 그리고 파이썬 sorted의 알고리즘인 Timsort까지 다룹니다.

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
