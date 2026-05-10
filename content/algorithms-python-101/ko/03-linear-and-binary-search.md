---
series: algorithms-python-101
episode: 3
title: 선형 탐색과 이진 탐색
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
  - 선형 탐색
  - 이진 탐색
  - bisect
seo_description: Python으로 선형 탐색과 이진 탐색을 구현하고 성능을 비교합니다.
last_reviewed: '2026-05-04'
---

# 선형 탐색과 이진 탐색

> Algorithms with Python 101 시리즈 (3/10)


## 이 글에서 다룰 문제

탐색은 프로그래밍에서 가장 빈번한 연산입니다. 데이터가 100개일 때는 선형 탐색으로 충분하지만, 100만 개가 되면 이진 탐색은 최대 20번, 선형 탐색은 최대 100만 번 비교해야 합니다.

> 이진 탐색 = 정렬된 데이터에서 매번 절반을 제거하여 O(log n)에 검색

이진 탐색은 단순히 값을 찾는 것을 넘어, "조건을 만족하는 최솟값/최댓값"을 찾는 패턴으로 확장됩니다. 이 패턴은 코딩 면접에서 자주 출제됩니다.

## 핵심 개념 잡기

> 탐색 = 데이터에서 원하는 값을 찾는 과정

```
선형 탐색: [1, 3, 5, 7, 9, 11, 13]에서 9 찾기
→ 1, 3, 5, 7, 9 (5번 비교)

이진 탐색: [1, 3, 5, 7, 9, 11, 13]에서 9 찾기
→ 7(중간), 11(오른쪽 중간), 9 (3번 비교)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 선형 탐색 | 처음부터 끝까지 순서대로 확인하는 O(n) 탐색입니다 |
| 이진 탐색 | 정렬된 데이터에서 중간값을 기준으로 반씩 줄이는 O(log n) 탐색입니다 |
| bisect | Python 표준 라이브러리의 이진 탐색 모듈입니다 |
| 상한/하한(upper/lower bound) | 특정 값 이상/초과의 첫 위치를 찾는 변형입니다 |
| 매개변수 탐색(parametric search) | 이진 탐색을 "조건 만족 범위"에 적용하는 기법입니다 |

## Before / After

정렬된 리스트에서 값을 찾는 두 가지 방법을 비교합니다.

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

### Step 1: 선형 탐색 구현

```python
def linear_search(data: list, target) -> int:
    """선형 탐색 — O(n)"""
    for i, value in enumerate(data):
        if value == target:
            return i
    return -1

data = [4, 2, 7, 1, 9, 3, 8]
print(linear_search(data, 9))   # 4
print(linear_search(data, 5))   # -1

# 정렬 필요 없음 — 어떤 리스트에서도 동작
```

### Step 2: 이진 탐색 구현

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """이진 탐색 — O(log n), 정렬된 데이터 필요"""
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

### Step 3: bisect 모듈 활용

```python
import bisect

data = [1, 3, 5, 7, 9, 11, 13, 15]

# 삽입 위치 찾기 (정렬 유지)
pos = bisect.bisect_left(data, 9)
print(f"9의 위치: {pos}")  # 4

# 값이 존재하는지 확인
def bisect_search(sorted_data: list[int], target: int) -> int:
    pos = bisect.bisect_left(sorted_data, target)
    if pos < len(sorted_data) and sorted_data[pos] == target:
        return pos
    return -1

print(bisect_search(data, 9))    # 4
print(bisect_search(data, 10))   # -1

# 정렬된 리스트에 값 삽입
scores = [70, 80, 90]
bisect.insort(scores, 85)
print(scores)  # [70, 80, 85, 90]
```

### Step 4: 하한과 상한

```python
import bisect

data = [1, 3, 5, 5, 5, 7, 9]

# bisect_left: 같은 값이 있으면 왼쪽(첫 번째) 위치
print(bisect.bisect_left(data, 5))   # 2

# bisect_right: 같은 값이 있으면 오른쪽(마지막+1) 위치
print(bisect.bisect_right(data, 5))  # 5

# 5의 개수
count = bisect.bisect_right(data, 5) - bisect.bisect_left(data, 5)
print(f"5의 개수: {count}")  # 3

# 5 이상인 첫 번째 값의 인덱스
lower = bisect.bisect_left(data, 5)
print(f"5 이상 첫 위치: {lower}")  # 2

# 5 초과인 첫 번째 값의 인덱스
upper = bisect.bisect_right(data, 5)
print(f"5 초과 첫 위치: {upper}")  # 5
```

### Step 5: 성능 비교

```python
import time
import bisect

def benchmark_search(n: int):
    data = list(range(n))
    target = n - 1  # 최악의 경우

    # 선형 탐색
    start = time.perf_counter()
    linear_search(data, target)
    t_linear = time.perf_counter() - start

    # 이진 탐색
    start = time.perf_counter()
    binary_search(data, target)
    t_binary = time.perf_counter() - start

    # bisect
    start = time.perf_counter()
    bisect.bisect_left(data, target)
    t_bisect = time.perf_counter() - start

    print(f"n={n:>10,}: 선형={t_linear:.6f}초  이진={t_binary:.6f}초  bisect={t_bisect:.6f}초")

for n in [10_000, 100_000, 1_000_000]:
    benchmark_search(n)
```

## 이 코드에서 주목할 점

- 선형 탐색은 정렬이 필요 없지만, 이진 탐색은 정렬된 데이터에서만 동작합니다
- 이진 탐색은 100만 개 데이터에서도 최대 20번 비교로 충분합니다
- bisect 모듈은 C로 구현되어 직접 구현한 이진 탐색보다 빠릅니다
- bisect_left와 bisect_right의 차이를 이해하면 다양한 문제를 풀 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 정렬 안 된 데이터에 이진 탐색 | 잘못된 결과를 반환합니다 | 이진 탐색 전에 정렬을 확인합니다 |
| mid 계산에서 오버플로 | `(left + right)`가 정수 범위를 초과합니다 | `left + (right - left) // 2`를 사용합니다 |
| left <= right 대신 left < right | 원소 1개인 경우를 놓칩니다 | `<=`를 사용합니다 |
| 무한 루프 | left, right 갱신이 잘못되어 수렴하지 않습니다 | mid+1, mid-1로 범위를 반드시 축소합니다 |
| bisect 결과를 인덱스로 바로 사용 | 값이 없어도 삽입 위치를 반환합니다 | 반환된 위치의 값을 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 B-Tree 인덱스가 이진 탐색 원리로 레코드를 찾습니다
- 로그 파일에서 특정 시간대의 로그를 이진 탐색으로 빠르게 찾습니다
- 버전 관리에서 버그가 도입된 커밋을 이진 탐색(git bisect)으로 찾습니다
- 게임 매칭에서 비슷한 실력의 상대를 이진 탐색으로 찾습니다
- A/B 테스트에서 최적 임계값을 이진 탐색으로 결정합니다

## 현업 개발자는 이렇게 생각합니다

직접 이진 탐색을 구현할 일은 드뭅니다. bisect 모듈이나 데이터베이스 인덱스가 대부분을 처리합니다. 하지만 이진 탐색의 원리를 이해하면 "매개변수 탐색"이라는 강력한 패턴을 활용할 수 있습니다.

"정렬된 데이터에서 조건을 만족하는 첫 번째/마지막 값 찾기"는 이진 탐색의 핵심 응용입니다. 이 패턴을 익히면 코딩 면접에서 큰 도움이 됩니다.

## 체크리스트

- [ ] 선형 탐색과 이진 탐색의 시간 복잡도를 비교할 수 있다
- [ ] 이진 탐색을 반복문으로 구현할 수 있다
- [ ] bisect_left와 bisect_right의 차이를 설명할 수 있다
- [ ] 이진 탐색의 전제조건(정렬)을 설명할 수 있다
- [ ] 이진 탐색의 실무 응용 사례를 설명할 수 있다

## 정리 및 다음 글 안내

선형 탐색은 O(n)이고 이진 탐색은 O(log n)입니다. 이진 탐색은 정렬된 데이터에서만 동작하지만, 성능 차이는 데이터가 커질수록 극적입니다. 다음 글에서는 데이터를 정렬하는 핵심 알고리즘들을 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
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

- [Python 공식 문서 — bisect](https://docs.python.org/3/library/bisect.html)
- [Real Python — Binary Search in Python](https://realpython.com/binary-search-python/)
- [GeeksforGeeks — Binary Search](https://www.geeksforgeeks.org/binary-search/)
- [LeetCode — Binary Search Problems](https://leetcode.com/tag/binary-search/)

Tags: Python, 알고리즘, 선형 탐색, 이진 탐색, bisect
