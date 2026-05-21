---
series: computer-science-101
episode: 4
title: "Computer Science 101 (4/10): 알고리즘과 복잡도"
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
  - 복잡도
  - Big-O
  - 자료구조
  - 성능
seo_description: 알고리즘, Big-O, 자료구조 선택이 성능을 어떻게 바꾸는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (4/10): 알고리즘과 복잡도

작은 입력에서는 멀쩡하던 코드가 운영에서 갑자기 느려지는 이유는 대개 하드웨어보다 알고리즘 차수에서 먼저 설명됩니다. 같은 문제를 풀어도 어떤 코드는 선형으로 늘고, 어떤 코드는 제곱으로 무너집니다.

이 글은 Computer Science 101 시리즈의 4번째 글입니다.

여기서는 알고리즘의 정의, 시간·공간 복잡도, Big-O 표기법, 그리고 자료구조 선택이 왜 성능을 바꾸는지 입문자 관점에서 정리하겠습니다.


![Computer Science 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/04/04-01-concept-at-a-glance.ko.png)
*Computer Science 101 4장 흐름 개요*

## 먼저 던지는 질문

- 같은 문제를 푸는 두 코드 중 무엇이 더 빠를지 어떻게 판단할까요?
- 시간 복잡도와 공간 복잡도는 무엇을 각각 뜻할까요?
- Big-O 표기법은 왜 코드를 실행하지 않고도 성능을 가늠하게 해 줄까요?

## 이 글에서 배울 것

- 좋은 알고리즘을 판단하는 기준
- 시간 복잡도와 공간 복잡도의 의미
- Big-O로 성능 증가율을 읽는 방법
- 자료구조 선택이 복잡도를 바꾸는 방식

## 왜 중요한가

코드가 100개 데이터에서 잘 돌아가도 100만 개에서는 멈출 수 있습니다. 데이터 크기에 따른 성능 변화를 예측하지 못하면 출시 후에 장애로 이어집니다. Big-O는 코드를 실행해 보지 않고도 성능 한계를 미리 판단하게 해 줍니다.

> 알고리즘 = 문제를 푸는 절차, 복잡도 = 그 절차의 비용

복잡도를 읽을 줄 아는 것이 시니어와 주니어를 가르는 가장 명확한 기준 중 하나입니다.

## 한눈에 보는 개념

> 같은 결과를 내는 두 알고리즘도 입력이 커지면 차이가 수천 배로 벌어집니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Algorithm | 입력을 원하는 출력으로 바꾸는 유한하고 명확한 절차 |
| Time complexity | 입력 크기가 커질 때 연산 수가 증가하는 비율 |
| Space complexity | 입력 크기에 따라 추가 메모리가 늘어나는 비율 |
| Big-O | 입력이 무한히 커질 때의 상한 증가율 표기 |
| Data structure | 데이터를 저장하고 접근하는 방식 |

## Before / After

**Before — 복잡도를 모를 때:**

```python
# Find common elements between two lists — O(n^2)
def common_slow(a: list[int], b: list[int]) -> list[int]:
    result = []
    for x in a:
        if x in b:        # `in` on a list is O(n)
            result.append(x)
    return result

# At n=10,000 that is roughly 100 million comparisons — several seconds
```

**After — 복잡도를 알 때:**

```python
# Same problem — O(n)
def common_fast(a: list[int], b: list[int]) -> list[int]:
    b_set = set(b)        # one-time O(n)
    return [x for x in a if x in b_set]   # `in` on a set is O(1)

# At n=10,000 that is roughly 20,000 comparisons — milliseconds
```

## 단계별로 따라하기

### 1단계: 선형 탐색과 이진 탐색

```python
def linear_search(arr: list[int], target: int) -> int:
    """Search an unsorted list for target — O(n)."""
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1

def binary_search(arr: list[int], target: int) -> int:
    """Search a sorted list for target — O(log n)."""
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

data = sorted(range(1_000_000))
print(linear_search(data, 999_999))   # 999999 — about 1,000,000 comparisons
print(binary_search(data, 999_999))   # 999999 — about 20 comparisons
```

### 2단계: 두 알고리즘의 실제 시간 비교

```python
import time

big = sorted(range(1_000_000))
target = 999_999

start = time.perf_counter()
linear_search(big, target)
print(f"linear : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
binary_search(big, target)
print(f"binary : {time.perf_counter() - start:.6f}s")
```

**Expected output:** 정렬된 입력에서는 `binary`가 `linear`보다 눈에 띄게 빠르고, 비교 횟수도 수십만 대 수십 수준으로 줄어듭니다.

### 3단계: 자료구조 선택이 복잡도를 바꾼다

```python
# list: `in` is O(n)
nums_list = list(range(1_000_000))

# set: `in` is O(1) on average
nums_set = set(nums_list)

start = time.perf_counter()
print(999_999 in nums_list)
print(f"list   : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
print(999_999 in nums_set)
print(f"set    : {time.perf_counter() - start:.6f}s")
```

### 4단계: 정렬 알고리즘 비교

```python
import random

def bubble_sort(arr: list[int]) -> list[int]:
    """O(n^2) — educational only. Do not use this in real code."""
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

small = [random.randint(0, 100) for _ in range(2000)]

start = time.perf_counter()
bubble_sort(small)
print(f"bubble (n=2000)  : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
sorted(small)             # Python's sorted is Timsort — O(n log n)
print(f"sorted (n=2000)  : {time.perf_counter() - start:.6f}s")
```

### 5단계: 복잡도 직관 익히기

```python
def complexity_table(sizes: list[int]) -> None:
    print(f"{'n':>10} {'O(log n)':>12} {'O(n)':>12} {'O(n log n)':>14} {'O(n^2)':>16}")
    for n in sizes:
        import math
        log_n = math.log2(n)
        print(f"{n:>10} {log_n:>12.1f} {n:>12} {n * log_n:>14.0f} {n * n:>16,}")

complexity_table([10, 100, 1_000, 10_000, 100_000])
```

## 이 코드에서 먼저 봐야 할 점

- 같은 문제를 푸는 알고리즘도 자료구조 선택에 따라 복잡도가 달라집니다
- `list`의 `in`은 O(n), `set`과 `dict`의 `in`은 평균 O(1)입니다
- 정렬은 가능하면 표준 라이브러리(`sorted`, `list.sort`)를 사용합니다 — Timsort가 O(n log n)을 보장합니다
- 이진 탐색은 입력이 정렬되어 있어야 적용할 수 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 작은 데이터에서 측정하고 안심 | n이 커지면 폭발적으로 느려짐 | 입력 크기를 10배, 100배로 늘려 가며 측정 |
| `list`에 `in` 연산을 반복 사용 | O(n²) 누적 | 조회 대상은 `set`이나 `dict`로 변환 |
| 미세 최적화에 집착 | 상수 항만 줄이고 차수는 그대로 | 먼저 알고리즘 차수를 낮춥니다 |
| 모든 코드를 O(1)로 만들려는 시도 | 가독성 저하, 메모리 폭증 | 병목 구간만 최적화 |
| 평균과 최악 복잡도를 혼동 | dict가 항상 O(1)이라고 가정 | 해시 충돌이 있으면 최악은 O(n) |

## 실무에서는 이렇게 쓰입니다

- API 응답 시간 분석에서 데이터 증가에 따른 회귀 측정
- 데이터베이스 쿼리 EXPLAIN 결과 해석 시 인덱스 유무에 따른 복잡도 차이
- 캐시 자료구조 선택 (LRU에는 `OrderedDict`, 빠른 멤버십 검사는 `set`)
- 대용량 로그 처리에서 스트리밍 알고리즘으로 공간 복잡도 절감
- 검색·추천 시스템에서 인덱스 자료구조(B-Tree, Trie, HNSW)의 복잡도 트레이드오프

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 중첩 루프를 보면 먼저 n이 커질 때 무슨 일이 생기는지 계산합니다. 작은 입력에서는 체감이 안 나도, 운영 규모에서는 낮은 차수가 거의 항상 이깁니다.

동시에 이론적인 Big-O와 실제 벽시계 시간이 다를 수 있다는 사실도 압니다. 그래서 차수를 낮춘 뒤에는 반드시 측정합니다. 측정하지 않은 최적화는 추측에 가깝기 때문입니다.


### 정렬 알고리즘 복잡도 비교표

실무에서 만나는 주요 정렬 알고리즘의 시간·공간 복잡도를 정리합니다.

| 알고리즘 | 최선 | 평균 | 최악 | 공간 | 안정성 | 특징 |
|----------|------|------|------|------|--------|------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | 안정 | 교육용, 실무 부적합 |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | 불안정 | 교환 횟수 최소 |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | 안정 | 거의 정렬된 입력에 강함 |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | 안정 | 외부 정렬에 적합 |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | 불안정 | 평균 상수가 작음 |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | 불안정 | 캐시 지역성 낮음 |
| Timsort | O(n) | O(n log n) | O(n log n) | O(n) | 안정 | Python/Java 기본 정렬 |
| Counting Sort | O(n+k) | O(n+k) | O(n+k) | O(k) | 안정 | 범위 k가 작을 때 |
| Radix Sort | O(d·n) | O(d·n) | O(d·n) | O(n+k) | 안정 | 자릿수 d가 작을 때 |

Timsort가 Python 표준 라이브러리에 채택된 이유는 실세계 데이터가 부분 정렬된 경우가 많기 때문입니다. 이미 정렬된 구간(run)을 감지해 합치므로, 최선 O(n)을 실전에서도 자주 달성합니다.

### 분할 상환 분석(Amortized Analysis)

파이썬 `list.append()`는 대부분 O(1)이지만 가끔 배열을 재할당합니다. 이때 한 번의 비용은 O(n)입니다. 하지만 n번 연속으로 `append`를 하면 총 비용이 O(n)이므로 평균(분할 상환) 비용은 O(1)입니다.

```python
import sys

sizes = []
prev_size = 0
arr = []
for i in range(100):
    arr.append(i)
    curr_size = sys.getsizeof(arr)
    if curr_size != prev_size:
        sizes.append((i, curr_size))
        prev_size = curr_size

print("append 횟수 | 내부 배열 크기(bytes)")
print("-" * 35)
for count, size in sizes[:12]:
    print(f"  {count:>5}      |  {size:>6}")
```

출력을 보면 배열 크기가 일정 비율(약 1.125배)로 증가합니다. 재할당은 드물게 발생하고, 이를 모든 연산에 나눠 부담하면 각 `append`는 상환 O(1)이 됩니다.

이 개념은 해시 테이블의 리사이징, 스택의 동적 확장, 스플레이 트리의 회전 등에도 동일하게 적용됩니다.

### 공간-시간 트레이드오프

알고리즘 설계에서 시간을 줄이려면 공간을 더 쓰고, 공간을 아끼려면 시간이 늘어나는 상충 관계가 자주 나타납니다.

| 문제 | 시간 우선 접근 | 공간 우선 접근 |
|------|---------------|---------------|
| 피보나치 수 | 메모이제이션 O(n) 시간, O(n) 공간 | 반복문 O(n) 시간, O(1) 공간 |
| 두 수 합 | 해시맵 O(n) 시간, O(n) 공간 | 정렬 후 투 포인터 O(n log n) 시간, O(1) 공간 |
| 중복 검사 | set 사용 O(n) 시간, O(n) 공간 | 정렬 후 인접 비교 O(n log n) 시간, O(1) 공간 |
| 최단 경로 | BFS/Dijkstra O(V+E) 시간, O(V) 공간 | DFS 반복 심화 O(V+E) 시간, O(깊이) 공간 |

```python
# 시간 우선: Two Sum with hash map — O(n) time, O(n) space
def two_sum_hash(nums: list[int], target: int) -> tuple[int, int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return (-1, -1)

# 공간 우선: Two Sum with sort + two pointers — O(n log n) time, O(1) extra space
def two_sum_sort(nums: list[int], target: int) -> tuple[int, int]:
    indexed = sorted(enumerate(nums), key=lambda x: x[1])
    lo, hi = 0, len(indexed) - 1
    while lo < hi:
        s = indexed[lo][1] + indexed[hi][1]
        if s == target:
            return (indexed[lo][0], indexed[hi][0])
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return (-1, -1)

nums = [2, 7, 11, 15, 1, 8]
print(two_sum_hash(nums, 9))   # (0, 1)
print(two_sum_sort(nums, 9))   # (0, 1)
```

운영 환경에서는 메모리가 넉넉한 서버라면 시간 우선을, 임베디드 시스템이나 엣지 디바이스라면 공간 우선을 선택합니다.

### 재귀와 반복의 복잡도 분석

같은 알고리즘도 재귀와 반복으로 구현하면 실제 성능이 달라집니다.

```python
# 재귀 피보나치 — O(2^n) 시간, O(n) 콜 스택
def fib_recursive(n: int) -> int:
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

# 메모이제이션 피보나치 — O(n) 시간, O(n) 공간
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# 반복 피보나치 — O(n) 시간, O(1) 공간
def fib_iterative(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

import time

n = 35
start = time.perf_counter()
fib_recursive(n)
print(f"recursive (n={n}): {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
fib_memo(n)
print(f"memoized  (n={n}): {time.perf_counter() - start:.6f}s")

start = time.perf_counter()
fib_iterative(n)
print(f"iterative (n={n}): {time.perf_counter() - start:.6f}s")
```

재귀의 지수적 폭발을 메모이제이션으로 선형으로 줄이고, 반복으로 바꾸면 콜 스택까지 제거합니다. Python은 기본 재귀 깊이가 1000이므로, 깊은 재귀는 `sys.setrecursionlimit` 또는 반복 변환이 필요합니다.

### 그래프 알고리즘의 복잡도

그래프 문제는 실무에서 자주 등장합니다. 소셜 네트워크, 라우팅, 의존성 해결 등이 모두 그래프 문제입니다.

| 알고리즘 | 시간 복잡도 | 공간 복잡도 | 용도 |
|----------|-------------|-------------|------|
| BFS | O(V + E) | O(V) | 최단 경로(비가중) |
| DFS | O(V + E) | O(V) | 연결 요소, 위상 정렬 |
| Dijkstra | O((V+E) log V) | O(V) | 최단 경로(가중, 양수) |
| Bellman-Ford | O(V · E) | O(V) | 음수 간선 허용 |
| Floyd-Warshall | O(V³) | O(V²) | 모든 쌍 최단 경로 |
| Kruskal | O(E log E) | O(V) | 최소 신장 트리 |
| Topological Sort | O(V + E) | O(V) | 빌드 순서, DAG |

```python
from collections import deque

def bfs_shortest_path(graph: dict[str, list[str]], start: str, end: str) -> list[str]:
    """BFS로 비가중 그래프의 최단 경로를 찾습니다."""
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []

# 예시: 서울 지하철 노선 일부를 그래프로 표현
metro = {
    "서울역": ["시청", "남영"],
    "시청": ["서울역", "종각", "을지로입구"],
    "종각": ["시청", "종로3가"],
    "종로3가": ["종각", "을지로3가"],
    "을지로입구": ["시청", "을지로3가"],
    "을지로3가": ["을지로입구", "종로3가"],
    "남영": ["서울역"],
}

path = bfs_shortest_path(metro, "남영", "종로3가")
print(f"최단 경로: {' → '.join(path)}")
# 최단 경로: 남영 → 서울역 → 시청 → 종각 → 종로3가
```

V(정점 수)와 E(간선 수)로 복잡도를 표현하는 이유는, 그래프의 크기가 두 가지 독립 변수로 결정되기 때문입니다. 밀집 그래프(E ≈ V²)에서는 BFS도 O(V²)가 되므로, 인접 행렬과 인접 리스트 중 어떤 표현을 쓰느냐가 성능에 영향을 줍니다.

### NP 문제와 현실적 한계

모든 문제에 효율적인 알고리즘이 존재하는 것은 아닙니다. NP-완전 문제(외판원, 배낭, 그래프 색칠 등)는 알려진 최선 알고리즘이 지수 시간입니다. 실무에서는 이런 문제를 만나면 세 가지 전략을 씁니다.

1. **근사 알고리즘**: 최적해의 일정 비율 이내 해를 다항 시간에 구합니다. 예를 들어 TSP의 2-근사는 최적의 2배 이내 경로를 O(n² log n)에 찾습니다.
2. **휴리스틱**: 최적 보장은 없지만 실전에서 충분히 좋은 해를 빠르게 구합니다. 유전 알고리즘, 시뮬레이티드 어닐링이 대표적입니다.
3. **문제 크기 제한**: 입력이 작으면(n < 20) 지수 알고리즘도 1초 안에 끝납니다. 비트마스크 DP가 이 범주에 해당합니다.

복잡도 이론을 아는 것의 실무적 가치는 "이 문제는 다항 시간에 풀 수 없다"는 판단을 빠르게 내려서, 완벽한 해를 찾느라 시간을 낭비하지 않는 데 있습니다.
## 체크리스트

- [ ] Big-O 표기법으로 알고리즘의 차수를 말할 수 있는가
- [ ] `list`, `set`, `dict`의 주요 연산 복잡도를 외우고 있는가
- [ ] 선형 탐색과 이진 탐색의 적용 조건을 구분하는가
- [ ] 정렬에 표준 라이브러리를 사용하는 이유를 설명할 수 있는가
- [ ] 작은 데이터의 결과만 보고 성능을 판단하지 않는가

## 연습 문제

1. 리스트의 중복 원소를 찾는 O(n^2) 버전과 O(n) 버전을 각각 구현하고 실행 시간을 비교해 보세요.
2. 정렬된 두 리스트를 O(n) 시간에 하나로 합치는 함수를 작성해 보세요.
3. 1..n 범위에서 빠진 정수 하나를 O(n) 시간, O(1) 추가 공간으로 찾는 방법을 구현해 보세요.

## 정리 및 다음 단계

알고리즘은 문제를 푸는 절차이고, 복잡도는 그 절차의 비용입니다. Big-O는 입력이 커질 때의 상한 증가율을 나타냅니다. 자료구조 선택이 복잡도를 결정하므로, `list`/`set`/`dict`의 연산 복잡도는 반드시 알아야 합니다. 측정 없이 최적화하지 않는 것이 시니어 엔지니어의 원칙입니다.

다음 글에서는 이 알고리즘이 실제로 돌아가는 컴퓨터의 내부 구조 — CPU, 메모리, 캐시 — 를 다룹니다.


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

복잡도 단원에서는 점근 표기뿐 아니라 실제 입력 분포에서의 상수항 영향을 함께 비교해 알고리즘 선택 정확도를 높입니다.

### 학습 팁: 복잡도 표를 실험 기록으로 바꾸기

복잡도는 정답표가 아니라 가설입니다. 입력 크기를 10배씩 늘려 실행 시간을 기록하고, 그래프 기울기가 예상과 맞는지 확인합니다. 만약 예상보다 완만하거나 급격하다면 자료구조 선택, 메모리 접근 패턴, 인터프리터 오버헤드 같은 요인을 분리해 다시 측정합니다. 이 반복이 알고리즘 직관을 실제 판단 능력으로 바꿉니다.

## 처음 질문으로 돌아가기

- **같은 문제를 푸는 두 코드 중 무엇이 더 빠를지 어떻게 판단할까요?**
  - 각 코드의 핵심 반복문이 입력 크기 n에 대해 몇 번 실행되는지 세고, Big-O로 표현합니다. O(n)과 O(n²)는 n=10에서 차이가 없어도 n=100만에서 수천 배 차이가 납니다. 차수를 비교한 뒤 실제 측정으로 상수항과 캐시 효과를 확인합니다.
- **시간 복잡도와 공간 복잡도는 무엇을 각각 뜻할까요?**
  - 시간 복잡도는 입력이 커질 때 연산 횟수의 증가율, 공간 복잡도는 추가 메모리의 증가율입니다. 둘은 트레이드오프 관계에 있어서, 해시맵으로 시간을 줄이면 공간이 늘고, 정렬 후 투 포인터로 공간을 줄이면 시간이 늘어납니다.
- **Big-O 표기법은 왜 코드를 실행하지 않고도 성능을 가늠하게 해 줄까요?**
  - Big-O는 입력이 무한히 커질 때의 상한 증가율만 남기므로, 하드웨어·언어·상수항에 관계없이 알고리즘의 본질적 비용을 비교할 수 있습니다. 실행 없이도 중첩 루프의 차수를 세면 운영 규모에서의 병목을 예측할 수 있습니다.


<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- **알고리즘과 복잡도 (현재 글)**
- 컴퓨터 구조 (예정)
- 운영체제 (예정)
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Donald Knuth — The Art of Computer Programming](https://www-cs-faculty.stanford.edu/~knuth/taocp.html)

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, 알고리즘, 복잡도, Big-O, 자료구조, 성능
