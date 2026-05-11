---
series: algorithms-python-101
episode: 2
title: 시간 복잡도와 Big-O
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
  - 시간 복잡도
  - Big-O
  - 성능 분석
seo_description: Big-O 표기법으로 알고리즘의 시간 복잡도를 분석하고 비교합니다.
last_reviewed: '2026-05-04'
---

# 시간 복잡도와 Big-O

> Algorithms with Python 101 시리즈 (2/10)


## 이 글에서 다룰 문제

"이 코드가 얼마나 빠른가?"라는 질문에 "내 컴퓨터에서 0.3초 걸렸다"는 답은 부족합니다. 하드웨어, 데이터 크기, 운영체제에 따라 달라지기 때문입니다. Big-O는 이런 변수를 제거하고 알고리즘 자체의 성능을 비교하는 도구입니다.

> Big-O = 입력 크기 n이 커질 때 연산 횟수의 증가율

면접에서 "이 알고리즘의 시간 복잡도는?"이라는 질문은 거의 반드시 나옵니다. Big-O로 답할 수 있어야 합니다.

## 핵심 개념 잡기

> Big-O = 최악의 경우 연산 횟수가 입력 크기에 비례하여 증가하는 비율

```
n=1000일 때 대략적인 연산 횟수:
O(1)      →           1
O(log n)  →          10
O(n)      →       1,000
O(n log n)→      10,000
O(n²)     →   1,000,000
O(2^n)    → 불가능 (우주 나이보다 긺)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| O(1) | 상수 시간 — 입력 크기와 무관합니다 |
| O(log n) | 로그 시간 — 매 단계마다 탐색 범위가 반으로 줄어듭니다 |
| O(n) | 선형 시간 — 입력 크기에 비례합니다 |
| O(n²) | 이차 시간 — 이중 반복문에서 나타납니다 |
| 최악의 경우(worst case) | 가장 많은 연산이 필요한 입력입니다 |

## Before / After

리스트에서 특정 값의 존재를 확인하는 두 가지 방법을 비교합니다.

```python
# before: 정렬 후 검색 — O(n log n)
data = [5, 3, 8, 1, 9, 2, 7]
data.sort()
found = 7 in data
```

```python
# after: set 변환 후 검색 — O(n) 변환 + O(1) 검색
data = [5, 3, 8, 1, 9, 2, 7]
data_set = set(data)
found = 7 in data_set
```

## 단계별 실습

### Step 1: O(1) — 상수 시간

```python
def get_first(data: list) -> object:
    """리스트의 첫 번째 원소 반환 — O(1)"""
    return data[0]

def get_by_index(data: list, index: int) -> object:
    """인덱스로 접근 — O(1)"""
    return data[index]

data = list(range(1_000_000))
print(get_first(data))         # 0
print(get_by_index(data, 500_000))  # 500000
# 리스트 크기와 무관하게 즉시 반환
```

### Step 2: O(n) — 선형 시간

```python
def linear_search(data: list[int], target: int) -> int:
    """선형 탐색 — O(n)"""
    for i, value in enumerate(data):
        if value == target:
            return i
    return -1

def sum_all(data: list[int]) -> int:
    """합계 — O(n)"""
    total = 0
    for num in data:
        total += num
    return total

data = list(range(100))
print(linear_search(data, 73))  # 73
print(sum_all(data))            # 4950
```

### Step 3: O(n²) — 이차 시간

```python
def bubble_sort(data: list[int]) -> list[int]:
    """버블 정렬 — O(n²)"""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def find_pairs(data: list[int], target: int) -> list[tuple]:
    """합이 target인 모든 쌍 — O(n²)"""
    pairs = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] + data[j] == target:
                pairs.append((data[i], data[j]))
    return pairs

print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
# [11, 12, 22, 25, 34, 64, 90]
print(find_pairs([1, 2, 3, 4, 5], 6))
# [(1, 5), (2, 4)]
```

### Step 4: O(log n) — 로그 시간

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """이진 탐색 — O(log n)"""
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

data = list(range(0, 100, 2))  # [0, 2, 4, ..., 98]
print(binary_search(data, 42))  # 21
print(binary_search(data, 43))  # -1
```

### Step 5: 시간 복잡도 실측 비교

```python
import time

def measure(func, *args, repeat=3):
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return min(times)

sizes = [1000, 5000, 10000]
for n in sizes:
    data = list(range(n))
    t_linear = measure(linear_search, data, n - 1)
    t_binary = measure(binary_search, data, n - 1)
    print(f"n={n:>6}: 선형={t_linear:.6f}초  이진={t_binary:.6f}초")
```

## 이 코드에서 주목할 점

- O(1)은 리스트 크기가 100만이어도 즉시 반환됩니다
- O(n)과 O(n²)는 데이터 크기가 10배 되면 각각 10배, 100배 느려집니다
- O(log n)은 데이터가 100만이어도 약 20단계면 충분합니다
- 실측 시간은 하드웨어에 따라 다르지만, 증가율은 Big-O를 따릅니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 상수 계수에 집착 | Big-O는 증가율이 핵심입니다 | 상수를 무시하고 최고 차수에 집중합니다 |
| 최선의 경우로 판단 | 최선 O(1)이어도 최악이 O(n²)일 수 있습니다 | 항상 최악의 경우를 기준으로 분석합니다 |
| 중첩 루프를 항상 O(n²)로 판단 | 내부 루프가 상수이면 O(n)입니다 | 실제 반복 횟수를 세어봅니다 |
| 공간 복잡도 무시 | 시간은 빠르지만 메모리가 부족할 수 있습니다 | 시간과 공간을 함께 분석합니다 |
| 숨겨진 비용 무시 | `in` 연산이 list에서 O(n)인 것을 모릅니다 | 내장 연산의 시간 복잡도를 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 쿼리 최적화에서 인덱스 사용 여부를 결정합니다 (O(n) → O(log n))
- API 응답 시간을 줄이기 위해 알고리즘을 개선합니다
- 대규모 데이터 파이프라인에서 O(n²) 병목을 찾아 제거합니다
- 캐싱 전략을 시간 복잡도 분석을 기반으로 설계합니다
- 코드 리뷰에서 비효율적인 알고리즘을 식별합니다

## 현업 개발자는 이렇게 생각합니다

Big-O는 대략적인 가이드라인입니다. 실제 성능은 캐시 히트율, 메모리 접근 패턴, 상수 계수에 따라 달라집니다. O(n log n) 알고리즘이 O(n) 알고리즘보다 실제로 빠른 경우도 있습니다.

하지만 Big-O를 모르면 O(n²)와 O(n)의 차이를 인식하지 못합니다. 데이터가 작을 때는 괜찮지만, 프로덕션에서 데이터가 커지면 장애로 이어질 수 있습니다.

## 체크리스트

- [ ] O(1), O(log n), O(n), O(n log n), O(n²)를 설명할 수 있다
- [ ] 주어진 코드의 시간 복잡도를 분석할 수 있다
- [ ] 최악의 경우와 평균의 경우의 차이를 설명할 수 있다
- [ ] 공간 복잡도의 개념을 설명할 수 있다
- [ ] Big-O가 실제 실행 시간과 다를 수 있는 이유를 설명할 수 있다

## 정리 및 다음 글 안내

Big-O 표기법은 알고리즘의 확장성을 객관적으로 비교하는 도구입니다. 입력 크기가 커질 때 연산 횟수의 증가율을 나타냅니다. 다음 글에서는 가장 기본적인 탐색 알고리즘인 선형 탐색과 이진 탐색을 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- **시간 복잡도와 Big-O (현재 글)**
- 선형 탐색과 이진 탐색 (예정)
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Khan Academy — Asymptotic Notation](https://www.khanacademy.org/computing/computer-science/algorithms/asymptotic-notation/a/asymptotic-notation)
- [Real Python — Big O Notation and Algorithm Analysis](https://realpython.com/sorting-algorithms-python/#measuring-efficiency-with-big-o-notation)

Tags: Python, 알고리즘, 시간 복잡도, Big-O, 성능 분석
