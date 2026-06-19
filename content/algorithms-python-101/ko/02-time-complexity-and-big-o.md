---
series: algorithms-python-101
episode: 2
title: "Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O"
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
  - Time Complexity
  - Big-O
  - Performance
seo_description: 시간 복잡도와 Big-O 표기법으로 알고리즘 성능을 객관적으로 분석합니다. 입력 증가에 따른 시간 변화를 파이썬 예제로 비교하는 법을 배웁니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O

내 노트북에서 몇 초가 걸렸는지만으로 알고리즘을 평가하는 것은 위험합니다. 하드웨어도 바뀌고, 런타임도 바뀌고, 테스트 데이터도 바뀌지만, 입력이 커질 때 실행 시간이 얼마나 빨리 증가하는지는 그대로 남기 때문입니다.

이 글은 Algorithms with Python 101 시리즈의 두 번째 글입니다. 여기서는 시간 복잡도에 대한 감을 잡고, Big-O 표기법으로 알고리즘을 더 엄밀하게 비교해 보겠습니다.

Big-O는 코드를 실서비스에 넣기 전이나 코딩 테스트 화이트보드 앞에 서기 전에도 성장 패턴을 비교할 수 있게 해 주는 실용적인 언어입니다.

![Algorithms with Python 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/02/02-01-big-picture.ko.png)
*Algorithms with Python 101 2장 흐름 개요*

## 이 글에서 다룰 문제

- 시간 복잡도는 무엇이며, 실제 실행 시간만으로는 왜 부족할까요?
- Big-O 표기법은 어떻게 읽고 써야 할까요?
- `O(1)`부터 `O(n!)`까지의 대표 복잡도는 어떻게 구분할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> Big-O 표기법은 입력 크기가 무한히 커질 때 알고리즘 실행 시간의 최악 성장률을, 상수항과 낮은 차수항을 무시하고 표현합니다.

시간 복잡도를 이해하는 일은 코딩 테스트, 코드 리뷰, 시스템 설계에서 이루어지는 거의 모든 알고리즘 대화의 출발점입니다.

## 개념 한눈에 보기

> Big-O = 알고리즘 실행 시간 증가율의 상한

```text
Input Size vs Operations (approximate):
n=1,000  | O(1): 1       | O(log n): 10    | O(n): 1,000
         | O(n log n): 10,000 | O(n^2): 1,000,000 | O(2^n): ∞
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Time complexity | 입력 크기에 따라 실행 시간이 얼마나 늘어나는지를 나타냅니다 |
| Big-O notation | 최악의 성장률을 표현하는 상한 표기입니다 |
| O(1) — constant | 입력 크기와 무관하게 시간이 거의 일정합니다 |
| O(n) — linear | 실행 시간이 입력 크기에 비례해 증가합니다 |
| O(n^2) — quadratic | 실행 시간이 입력 크기의 제곱에 비례해 증가합니다 |

## 복잡도 계열 정리

입력이 커질 때 각 복잡도 계열이 어떻게 성장하는지 숫자로 살펴보겠습니다.

| 복잡도 | n=10 | n=100 | n=1,000 | n=1,000,000 |
|--------|------|-------|---------|-------------|
| O(1) | 1 | 1 | 1 | 1 |
| O(log n) | 3 | 7 | 10 | 20 |
| O(n) | 10 | 100 | 1,000 | 1,000,000 |
| O(n log n) | 33 | 664 | 10,000 | 20,000,000 |
| O(n^2) | 100 | 10,000 | 1,000,000 | 10^12 |
| O(2^n) | 1,024 | 10^30 | 불가 | 불가 |

## 적용 전후 비교

컬렉션 안에 값이 있는지 확인하는 두 가지 방법입니다.

```python
# before: 리스트에서 선형 탐색 — O(n)
def contains(data: list, target) -> bool:
    for item in data:
        if item == target:
            return True
    return False
```

```python
# after: set에서 조회 — 평균 O(1)
def contains(data: set, target) -> bool:
    return target in data
```

## 단계별 실습

### 단계 1: O(1) — 상수 시간

```python
def get_first(data: list) -> int:
    """Access the first element — O(1)."""
    return data[0]

def get_by_key(data: dict, key: str):
    """Dictionary lookup — O(1) average."""
    return data.get(key)

numbers = list(range(1_000_000))
print(get_first(numbers))  # 0

lookup = {"name": "Alice", "age": 30}
print(get_by_key(lookup, "name"))  # Alice
```

배열의 첫 원소 접근이나 해시 기반 딕셔너리 조회처럼, 입력이 커져도 비용이 거의 늘지 않는 연산이 `O(1)`입니다.

### 단계 2: O(n) — 선형 시간

```python
def linear_sum(data: list[int]) -> int:
    """Sum all elements — O(n)."""
    total = 0
    for x in data:
        total += x
    return total

def find_value(data: list[int], target: int) -> int:
    """Linear search — O(n)."""
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1

data = list(range(100))
print(linear_sum(data))       # 4950
print(find_value(data, 42))   # 42
```

데이터를 처음부터 끝까지 한 번 훑어야 하면 보통 `O(n)`입니다.

### 단계 3: O(n^2) — 이차 시간

```python
def bubble_sort(data: list[int]) -> list[int]:
    """Bubble sort — O(n^2)."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def all_pairs(data: list) -> int:
    """Count all pairs — O(n^2)."""
    count = 0
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            count += 1
    return count

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
print(all_pairs(list(range(100))))    # 4950
```

중첩 반복문이 들어가면 가장 먼저 `O(n^2)` 가능성을 의심해야 합니다.

### 단계 4: O(log n)과 O(n log n)

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """Binary search — O(log n)."""
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

data = list(range(1_000_000))
print(binary_search(data, 999_999))  # 999999

# Python built-in sort는 O(n log n) — Timsort
import random
random_data = [random.randint(0, 1000) for _ in range(1000)]
sorted_data = sorted(random_data)  # O(n log n)
print(sorted_data[:5])
```

이진 탐색처럼 문제 공간을 절반씩 줄이는 알고리즘은 `O(log n)`입니다.

### 단계 5: 실험적 측정

```python
import time

def measure(func, *args) -> float:
    start = time.perf_counter()
    func(*args)
    return time.perf_counter() - start

sizes = [1_000, 5_000, 10_000]
for n in sizes:
    data = list(range(n))
    t_linear = measure(linear_sum, data)
    t_quadratic = measure(all_pairs, data)
    ratio = t_quadratic / t_linear if t_linear > 0 else 0
    print(f"n={n:>6}: linear={t_linear:.5f}s  quadratic={t_quadratic:.5f}s  ratio={ratio:.0f}x")
```

실측 시간은 환경 영향을 받지만, 입력이 커질수록 어떤 알고리즘의 증가율이 훨씬 가파른지는 분명하게 드러납니다.

## 단계별 실행 추적 — 연산 카운터

복잡도를 직관적으로 이해하는 가장 좋은 방법은 실제 연산 수를 세는 것입니다.

```python
def count_linear_ops(n: int) -> int:
    ops = 0
    data = list(range(n))
    for _ in data:
        ops += 1
    return ops

def count_quadratic_ops(n: int) -> int:
    ops = 0
    for i in range(n):
        for j in range(i + 1, n):
            ops += 1
    return ops

for n in [100, 500, 1_000]:
    linear = count_linear_ops(n)
    quadratic = count_quadratic_ops(n)
    ratio = quadratic / linear
    print(f"n={n:>5} | linear={linear:>8} | quadratic={quadratic:>10} | ratio={ratio:.1f}x")
```

실행 결과:

```text
n=  100 | linear=     100 | quadratic=      4950 | ratio=49.5x
n=  500 | linear=     500 | quadratic=    124750 | ratio=249.5x
n= 1000 | linear=    1000 | quadratic=    499500 | ratio=499.5x
```

입력을 10배 늘리면 선형은 10배, 제곱은 100배 이상 늘어납니다. Big-O의 핵심은 절대 시간보다 기울기입니다.

## 코딩 테스트 풀이 예시

**문제**: 배열에서 중복 원소를 `O(n)`에 찾아라.

```python
def find_duplicates(data: list[int]) -> list[int]:
    """
    O(n) 시간, O(n) 공간으로 중복 원소를 찾습니다.
    set을 사용해 이미 본 원소를 추적합니다.
    """
    seen: set[int] = set()
    duplicates: list[int] = []
    for num in data:
        if num in seen:
            if num not in duplicates:
                duplicates.append(num)
        else:
            seen.add(num)
    return sorted(duplicates)


# 테스트
print(find_duplicates([1, 2, 3, 2, 4, 3, 5]))  # [2, 3]
print(find_duplicates([1, 2, 3]))               # []
print(find_duplicates([]))                       # []
```

**단계별 추적** (`[1, 2, 3, 2, 4, 3, 5]` 입력):

```text
초기: seen={}, duplicates=[]

num=1: 1 in seen? No → seen={1}
num=2: 2 in seen? No → seen={1,2}
num=3: 3 in seen? No → seen={1,2,3}
num=2: 2 in seen? Yes → duplicates=[2]
num=4: 4 in seen? No → seen={1,2,3,4}
num=3: 3 in seen? Yes → duplicates=[2,3]
num=5: 5 in seen? No → seen={1,2,3,4,5}

결과: [2, 3]
```

**브루트포스와 비교**:

```python
def find_duplicates_brute(data: list[int]) -> list[int]:
    """O(n^2) 접근 — 비교용"""
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return sorted(duplicates)

# n=200,000에서 O(n^2)는 4*10^10 연산 → 시간 초과
# O(n)은 200,000 연산 → 통과
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `O(n)`과 `O(1)`을 혼동함 | 리스트와 집합의 조회 비용은 다릅니다 | 자료구조별 연산 복잡도 표를 익힙니다 |
| 중첩 반복문을 놓침 | 내부 루프 때문에 전체가 `O(n^2)`가 됩니다 | 중첩 깊이를 세어 봅니다 |
| 숨은 비용을 무시함 | 리스트에서 `in`은 `O(n)`입니다 | 자료구조 복잡도 표를 확인합니다 |
| 너무 이른 미세 최적화 | 큰 병목은 놔두고 작은 부분만 손봅니다 | 먼저 가장 큰 병목을 찾습니다 |
| 최선/평균/최악을 섞어 말함 | Big-O 관례와 설명이 어긋납니다 | 어떤 경우를 말하는지 명확히 합니다 |

## 알고리즘 선택 가이드

입력 크기 N에 따라 허용되는 복잡도를 역산하는 표입니다.

| 최대 입력 N | 우선 검토 복잡도 | 회피해야 할 복잡도 |
|-------------|------------------|--------------------|
| 1,000 | `O(n^2)` 가능 | `O(2^n)` |
| 100,000 | `O(n log n)` 이하 | `O(n^2)` |
| 1,000,000 | `O(n)` 중심 | `O(n log n)`도 상수 비용 점검 필요 |

## 실무에서는 이렇게 연결됩니다

- 데이터베이스 쿼리 플래너는 시간 복잡도 관점에서 인덱스를 선택합니다.
- 검색 엔진은 역색인 조회에 해시 기반 `O(1)` 접근을 활용합니다.
- 추천 순위 계산에서는 `O(n log n)` 정렬이 자주 등장합니다.
- 네트워크 라우터는 포워딩 테이블 탐색에 로그 시간 구조를 사용합니다.
- 머신러닝 학습 시간도 결국 알고리즘 복잡도의 영향을 받습니다.

## 현업에서는 이렇게 생각합니다

모든 복잡도 계열을 외우는 것이 목적은 아닙니다. 더 중요한 것은 감을 만드는 일입니다. 입력을 두 배로 늘렸을 때 실행 시간이 두 배인지, 네 배인지, 거의 안 늘어나는지를 떠올릴 수 있어야 합니다.

코드 리뷰에서 숙련된 엔지니어는 큰 데이터 위의 중첩 루프를 보면 바로 복잡도를 묻습니다. 이 습관 하나가 많은 성능 문제를 배포 전에 막아 줍니다.

## 운영 체크리스트

- [ ] Big-O 표기법이 무엇을 표현하는지 설명할 수 있습니다
- [ ] 간단한 Python 코드의 시간 복잡도를 식별할 수 있습니다
- [ ] 대표 복잡도 계열을 빠른 순서대로 비교할 수 있습니다
- [ ] 중첩 루프에서 `O(n)`과 `O(n^2)`를 구분할 수 있습니다
- [ ] 알고리즘 성능을 실측하고 비교할 수 있습니다

## 연습 문제

1. Python의 `list.index()`와 `dict.__getitem__()`의 시간 복잡도를 분석해 보세요.
2. 리스트에서 중복을 찾는 `O(n)` 알고리즘을 작성해 보세요. 힌트는 `set`입니다.
3. `n=10,000`에서 1초가 걸리는 `O(n^2)` 알고리즘이 `n=100,000`에서는 얼마나 걸릴지 예측해 보세요.

## 정리와 다음 글

시간 복잡도와 Big-O 표기법은 알고리즘 성능을 비교하는 공통 언어입니다. 특히 기억해야 할 계열은 `O(1)`, `O(log n)`, `O(n)`, `O(n log n)`, `O(n^2)`입니다. 다음 글에서는 가장 대표적인 두 탐색 알고리즘인 선형 탐색과 이진 탐색을 구현하고 비교합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- **Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O (현재 글)**
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — Time Complexity](https://wiki.python.org/moin/TimeComplexity)
- [Real Python — Big O Notation in Python](https://realpython.com/sorting-algorithms-python/)
- [GeeksforGeeks — Analysis of Algorithms | Big-O Analysis](https://www.geeksforgeeks.org/analysis-algorithms-big-o-analysis/)
- [Khan Academy — Asymptotic Notation](https://www.khanacademy.org/computing/computer-science/algorithms/asymptotic-notation)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/02-time-complexity-and-big-o)

Tags: Python, Algorithms, Time Complexity, Big-O, Performance
