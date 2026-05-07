---
series: computer-science-101
episode: 4
title: 알고리즘과 복잡도
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
  - 복잡도
  - Big-O
  - 자료구조
  - 성능
seo_description: 알고리즘과 시간/공간 복잡도, Big-O 표기법을 입문자 눈높이로 설명하는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 알고리즘과 복잡도

> Computer Science 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 문제를 푸는 코드가 두 개 있을 때, 어떤 코드가 더 빠른지 어떻게 판단할까요?

> 알고리즘은 문제를 푸는 명확한 절차입니다. 복잡도는 그 절차가 데이터 크기에 따라 얼마나 더 오래 걸리는지를 측정하는 언어입니다. 두 정렬 알고리즘이 같은 결과를 내더라도 데이터가 100만 개일 때 한쪽은 1초, 다른 쪽은 1시간이 걸릴 수 있습니다. 이 글에서는 알고리즘의 정의, Big-O 표기법, 자료구조 선택의 기준을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 알고리즘의 정의와 좋은 알고리즘의 조건
- 시간 복잡도와 공간 복잡도
- Big-O 표기법으로 성능 비교하기
- 자료구조 선택이 복잡도에 미치는 영향

## 왜 중요한가

코드가 100개 데이터에서 잘 돌아가도 100만 개에서는 멈출 수 있습니다. 데이터 크기에 따른 성능 변화를 예측하지 못하면 출시 후에 장애로 이어집니다. Big-O는 코드를 실행해 보지 않고도 성능 한계를 미리 판단하게 해 줍니다.

> 알고리즘 = 문제를 푸는 절차, 복잡도 = 그 절차의 비용

복잡도를 읽을 줄 아는 것이 시니어와 주니어를 가르는 가장 명확한 기준 중 하나입니다.

## 개념 한눈에 보기

> 같은 결과를 내는 두 알고리즘도 입력이 커지면 차이가 수천 배로 벌어집니다.

```text
입력 크기 n            n=10    n=1,000   n=1,000,000
─────────────────────────────────────────────────────
O(1)    상수            1        1            1
O(log n) 로그            3       10           20
O(n)    선형           10     1,000    1,000,000
O(n log n) 선형로그     33    10,000   20,000,000
O(n²)   제곱           100  1,000,000   10¹²(불가능)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 알고리즘(algorithm) | 입력에서 출력으로 가는 유한한 명확한 절차 |
| 시간 복잡도 | 입력 크기에 따른 연산 횟수의 증가율 |
| 공간 복잡도 | 입력 크기에 따른 메모리 사용량의 증가율 |
| Big-O | 입력이 무한히 커질 때의 상한 증가율 |
| 자료구조(data structure) | 데이터를 저장하고 접근하는 방식 (list, dict, set 등) |

## Before / After

**Before — 복잡도를 모를 때:**

```python
# 두 리스트의 공통 원소 찾기 — O(n²)
def common_slow(a: list[int], b: list[int]) -> list[int]:
    result = []
    for x in a:
        if x in b:        # b에 대한 in 연산은 O(n)
            result.append(x)
    return result

# n=10,000일 때 약 1억 번의 비교 — 수 초 소요
```

**After — 복잡도를 알 때:**

```python
# 같은 문제 — O(n)
def common_fast(a: list[int], b: list[int]) -> list[int]:
    b_set = set(b)        # 한 번에 O(n)
    return [x for x in a if x in b_set]   # in은 O(1)

# n=10,000일 때 약 2만 번의 비교 — 수 밀리초
```

## 실습: 단계별로 따라하기

### 1단계: 선형 탐색과 이진 탐색

```python
def linear_search(arr: list[int], target: int) -> int:
    """정렬되지 않은 리스트에서 target을 찾습니다 — O(n)."""
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1


def binary_search(arr: list[int], target: int) -> int:
    """정렬된 리스트에서 target을 찾습니다 — O(log n)."""
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
print(linear_search(data, 999_999))   # 999999 — 100만 번 비교
print(binary_search(data, 999_999))   # 999999 — 약 20번 비교
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

### 3단계: 자료구조 선택이 복잡도를 바꾼다

```python
# list: in 연산은 O(n)
nums_list = list(range(1_000_000))

# set: in 연산은 평균 O(1)
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
    """O(n²) — 교육용. 실무에서는 사용하지 않습니다."""
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
sorted(small)             # Python의 sorted는 Timsort — O(n log n)
print(f"sorted (n=2000)  : {time.perf_counter() - start:.6f}s")
```

### 5단계: 복잡도 직관 익히기

```python
def complexity_table(sizes: list[int]) -> None:
    print(f"{'n':>10} {'O(log n)':>12} {'O(n)':>12} {'O(n log n)':>14} {'O(n²)':>16}")
    for n in sizes:
        import math
        log_n = math.log2(n)
        print(f"{n:>10} {log_n:>12.1f} {n:>12} {n * log_n:>14.0f} {n * n:>16,}")


complexity_table([10, 100, 1_000, 10_000, 100_000])
```

## 이 코드에서 주목할 점

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

시니어 엔지니어는 코드를 읽을 때 자동으로 머릿속에서 복잡도를 계산합니다. 중첩 반복문이 보이면 "n이 커지면 어떻게 될까?"를 먼저 묻습니다. 작은 n에서는 무엇이 빠른지 모르지만, 큰 n에서는 차수가 낮은 알고리즘이 항상 이깁니다.

또한 이론적인 Big-O와 실제 성능이 다를 수 있다는 점도 압니다. 캐시 친화성, 분기 예측, 메모리 할당 비용 등 하드웨어 특성이 상수 항을 좌우합니다. 그래서 "측정하지 않은 최적화는 추측"이라는 원칙을 따릅니다.

## 체크리스트

- [ ] Big-O 표기법으로 알고리즘의 차수를 말할 수 있는가
- [ ] `list`, `set`, `dict`의 주요 연산 복잡도를 외우고 있는가
- [ ] 선형 탐색과 이진 탐색의 적용 조건을 구분하는가
- [ ] 정렬에 표준 라이브러리를 사용하는 이유를 설명할 수 있는가
- [ ] 작은 데이터의 결과만 보고 성능을 판단하지 않는가

## 연습 문제

1. 길이가 n인 리스트에 중복이 있는지 확인하는 함수를 두 가지 방법(O(n²)과 O(n))으로 구현하고 시간을 비교하세요.

2. 정렬된 두 리스트를 합쳐 정렬된 리스트를 만드는 함수를 O(n) 시간 안에 구현하세요. (`sorted(a + b)`는 O(n log n)이므로 사용하지 마세요.)

3. 1부터 n까지 정수 중에서 빠진 하나의 수를 찾는 함수를 O(n) 시간, O(1) 공간으로 구현하세요.

## 정리 및 다음 단계

알고리즘은 문제를 푸는 절차이고, 복잡도는 그 절차의 비용입니다. Big-O는 입력이 커질 때의 상한 증가율을 나타냅니다. 자료구조 선택이 복잡도를 결정하므로, `list`/`set`/`dict`의 연산 복잡도는 반드시 알아야 합니다. 측정 없이 최적화하지 않는 것이 시니어 엔지니어의 원칙입니다.

다음 글에서는 이 알고리즘이 실제로 돌아가는 컴퓨터의 내부 구조 — CPU, 메모리, 캐시 — 를 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- **알고리즘과 복잡도 (현재 글)**
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Donald Knuth — The Art of Computer Programming](https://www-cs-faculty.stanford.edu/~knuth/taocp.html)

Tags: Computer Science, 알고리즘, 복잡도, Big-O, 자료구조, 성능
