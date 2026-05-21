---
series: algorithms-101
episode: 4
title: "Algorithms 101 (4/10): 정렬 알고리즘"
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
  - 정렬
  - 퀵소트
  - 머지소트
  - Timsort
seo_description: 비교 기반 정렬의 하한과 대표 정렬 알고리즘의 트레이드오프, Timsort의 강점을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (4/10): 정렬 알고리즘

이 글은 Algorithms 101 시리즈의 4번째 글입니다.

Python의 `sorted`는 왜 그렇게 안정적으로 빠를까요? 그리고 교과서의 quicksort가 놓치는 것은 무엇일까요? 여기서는 대표 정렬 알고리즘의 트레이드오프와 Timsort가 실무에서 자주 이기는 이유를 다룹니다.

![Algorithms 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/04/04-01-big-picture.ko.png)
*Algorithms 101 4장 흐름 개요*

## 먼저 던지는 질문

- 비교 기반 정렬은 왜 O(n log n)보다 더 좋아질 수 없을까요?
- mergesort, quicksort, heapsort는 각각 무엇을 주고 무엇을 얻을까요?
- 안정 정렬과 비안정 정렬의 차이는 왜 중요할까요?

## 왜 중요한가

정렬은 거의 모든 다른 알고리즘의 전처리 단계입니다. 인덱스 생성, 배치 처리, 조인, 윈도우 집계, 머신러닝 전처리까지 모두 정렬 위에서 돌아갑니다. 어떤 정렬이 앞에 오는지가 뒤쪽 파이프라인 전체 비용을 좌우합니다.

> 정렬을 이해하는 일은 알고리즘 설계의 첫 번째 어휘를 익히는 일입니다.

## 한눈에 보는 개념

> 비교 기반 정렬의 결정 트리 깊이는 `log(n!) ≈ n log n`이므로 O(n log n)이 하한입니다. mergesort는 안정 정렬이고 O(n) 추가 메모리를 쓰며 O(n log n)을 보장합니다. quicksort는 제자리 정렬이고 평균 O(n log n)이지만 나쁜 pivot에서는 O(n²)로 무너집니다. heapsort는 제자리 정렬이며 O(n log n)을 보장하지만 안정적이지 않습니다. Timsort는 mergesort 위에 run 탐지를 얹은 적응형 정렬입니다.

```text
Lower bound for comparison sorting: O(n log n)

mergesort   stable,   O(n) extra memory,  guaranteed O(n log n)
quicksort   unstable, in-place,           average O(n log n) / worst O(n^2)
heapsort    unstable, in-place,           guaranteed O(n log n)
Timsort     stable,   adaptive,           best O(n) / worst O(n log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 비교 기반 정렬 | 원소끼리 비교해 순서를 정하는 정렬 |
| 안정 정렬 | 같은 키의 상대적 순서를 보존하는 정렬 |
| 제자리 정렬 | 추가 메모리를 거의 쓰지 않는 정렬 |
| 적응형 정렬 | 이미 어느 정도 정렬된 입력에서 더 빨라지는 정렬 |
| Timsort | mergesort와 run 탐지를 결합한 Python 표준 정렬 |

## 개선 전 / 개선 후

**Before — 손으로 짠 quicksort, 나쁜 입력에 취약:**

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    return quicksort(left) + [pivot] + quicksort(right)
# 이미 정렬된 입력에 대해 O(n^2)
```

**After — 표준 라이브러리 사용:**

```python
sorted_arr = sorted(arr)        # Timsort, stable, adaptive
arr.sort()                      # in-place variant
```

## 단계별로 따라가기

### 1단계: Mergesort

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

print(mergesort([3, 1, 4, 1, 5, 9, 2, 6]))
```

전형적인 분할 정복 정렬입니다. 안정적이고 O(n log n)을 보장하지만 O(n) 추가 메모리를 지불합니다.

### 2단계: 랜덤 pivot을 쓰는 Quicksort

```python
import random

def quicksort_inplace(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot_idx = random.randint(lo, hi)
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    quicksort_inplace(arr, lo, i - 1)
    quicksort_inplace(arr, i + 1, hi)

a = [3, 1, 4, 1, 5, 9, 2, 6]
quicksort_inplace(a)
print(a)
```

첫 원소를 pivot으로 고정하면 이미 정렬된 입력에서 O(n²)까지 무너질 수 있습니다. 그래서 랜덤 pivot이나 median-of-three 같은 방어가 사실상 표준입니다.

### 3단계: Heapsort

```python
import heapq

def heapsort(arr):
    h = list(arr)
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heapsort([3, 1, 4, 1, 5, 9, 2, 6]))
```

안정 정렬은 아니지만 O(n log n)을 보장하고 추가 메모리도 mergesort보다 적습니다. 최악 시간 보장이 필요할 때 의미가 큽니다.

### 4단계: Timsort의 적응성 관찰

```python
import random, time

def measure(arr):
    t = time.perf_counter()
    sorted(arr)
    return time.perf_counter() - t

n = 1_000_000
random_arr = [random.random() for _ in range(n)]
sorted_arr = sorted(random_arr)
nearly_sorted = sorted_arr[:]
for _ in range(100):
    i = random.randrange(n); j = random.randrange(n)
    nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]

print(f"random        : {measure(random_arr):.3f}s")
print(f"already sorted: {measure(sorted_arr):.3f}s")
print(f"nearly sorted : {measure(nearly_sorted):.3f}s")
```

Timsort는 이미 존재하는 run을 감지해 싸게 병합합니다. 실전 데이터는 완전 난수보다 부분 정렬된 경우가 많기 때문에, 바로 여기서 성능 이득이 납니다.

### 5단계: 안정성을 이용한 다중 키 정렬

```python
people = [
    ("Alice", 30), ("Bob", 25), ("Carol", 30), ("Dan", 25),
]
people.sort(key=lambda p: p[0])     # secondary
people.sort(key=lambda p: p[1])     # primary
print(people)
```

안정 정렬이면 보조 키부터 먼저 정렬한 뒤 주 키를 정렬해 다중 키 정렬을 간결하게 표현할 수 있습니다. Python의 Timsort가 안정 정렬이기 때문에 가능한 패턴입니다.

## 이 글에서 먼저 가져갈 점

- mergesort는 안정성과 보장을 주는 대신 메모리를 더 씁니다.
- quicksort는 평균적으로 빠르지만 pivot 방어가 없으면 위험합니다.
- heapsort는 메모리를 아끼며 최악 시간 보장을 제공합니다.
- Timsort는 안정성과 현실 데이터 적응성을 함께 가져갑니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 별도 인덱스를 손으로 맞추며 정렬 | 동기화 버그 | `sorted(..., key=..., reverse=...)`를 활용합니다 |
| 첫 원소 pivot quicksort 고집 | 정렬 입력에서 O(n²) | 랜덤 또는 median-of-three를 씁니다 |
| 안정성 가정 없이 다중 키 정렬 | 결과 비결정성 | 안정 정렬인지 먼저 확인합니다 |
| 아주 큰 데이터를 메모리에서 통째로 정렬 | OOM | 외부 병합 정렬이나 청크 처리를 검토합니다 |
| 부작용이 있는 comparator 사용 | 비교 결과 불일치 | key 함수로 값만 뽑아 비교합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 `ORDER BY`와 인덱스 생성은 내부적으로 정렬을 사용합니다.
- 로그 파이프라인은 시간순 스트림을 k-way merge로 합칩니다.
- 검색 엔진은 후보를 점수 순으로 정렬합니다.
- 추천 시스템은 후보 순위를 매깁니다.
- ML 파이프라인은 stratified sampling 전에 정렬을 사용하기도 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "정말 전체 정렬이 필요한가"를 묻습니다. 상위 k개만 필요하다면 힙으로 O(n log k)에 끝낼 수 있고, 특정 순위 하나만 필요하다면 quickselect처럼 O(n)에 가까운 선택 알고리즘이 더 적절할 수 있습니다.

또한 "메모리에 들어가는가"를 빠르게 확인합니다. 데이터가 RAM을 넘는 순간부터는 외부 병합 정렬과 분산 셔플 비용이 알고리즘 자체보다 더 큰 문제가 되기 때문입니다.

## 체크리스트

- [ ] 비교 기반 정렬의 O(n log n) 하한을 설명할 수 있는가
- [ ] mergesort, quicksort, heapsort의 트레이드오프를 말할 수 있는가
- [ ] 안정 정렬의 의미와 효용을 이해하는가
- [ ] Timsort가 실전 데이터에서 빠른 이유를 설명할 수 있는가
- [ ] 전체 정렬이 정말 필요한지 먼저 묻는가

## 연습 문제

1. 단어 목록을 길이 오름차순으로 정렬하되 길이가 같으면 사전순으로 정렬해 보세요. Timsort의 안정성을 활용하면 한 줄로 표현할 수 있습니다.

2. `heapq.nlargest`를 직접 구현해 보세요. 리스트와 k가 주어졌을 때 O(n log k)로 상위 k개를 반환하고, 왜 전체 정렬보다 유리한지 설명해 보세요.

3. 메모리에 다 들어가지 않는 10^8개의 정수에 대해 external mergesort를 스케치해 보세요. 디스크 I/O 패스가 몇 번 필요한지도 추정해 보세요.

## 정리 및 다음 단계

같은 O(n log n) 울타리 안에서도 정렬 알고리즘은 안정성, 메모리, 적응성에서 큰 차이를 보입니다. 기본 선택은 `sorted`와 `sort()`이고, 트레이드오프가 분명할 때만 다른 정렬을 검토하면 됩니다.

다음 글에서는 재귀와 분할 정복을 다룹니다. 호출 스택, 점화식, 그리고 분할 정복에서 동적 계획법으로 이어지는 사고 흐름을 살펴보겠습니다.

## 실전 확장 워크북

이 절은 정렬 알고리즘 비교를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

### 1) 시간 복잡도와 입력 제약을 먼저 맞추기

| 입력 조건 | 우선 배제할 접근 | 현실적인 후보 | 확인 포인트 |
| --- | --- | --- | --- |
| n <= 10^3 | 없음(학습 목적 실험 가능) | 브루트포스, 정렬, 해시 | 구현 명확성 |
| n <= 10^5 | O(n^2) 대부분 배제 | O(n log n), O(n), BFS/DFS | 경계값 테스트 |
| n <= 10^6 이상 | O(n log n)도 부담 가능 | 단일 패스, 압축, 스트리밍 | 메모리 상한 |

복잡도 판단은 코드 스타일 논쟁보다 우선합니다. 같은 팀에서 코드 품질 기준이 달라도, 입력 제약과 차수를 맞추는 원칙은 공통으로 적용됩니다. 이 단계를 건너뛰면 구현이 아무리 깔끔해도 제출 실패나 운영 지연으로 이어집니다.

### 2) 단계별 추적 표로 경계 버그를 조기에 찾기

| 단계 | 관찰 값 | 기대 신호 | 실패 신호 |
| --- | --- | --- | --- |
| 초기화 | 포인터/상태/큐/테이블 | 문제 정의와 일치 | 초기값 누락 |
| 1회 반복 | 상태 전이 | 단조 증가 또는 감소 | 제자리 반복 |
| 종료 직전 | 반환 후보 | 문제 요구와 직접 연결 | 보조값 반환 |

경계 버그는 대부분 "한 줄"에서 발생하지만, 원인은 상태 전이 설계에 있습니다. 그래서 디버깅할 때는 출력값 하나만 보지 말고, 전이 로그를 함께 봐야 합니다. 특히 인덱스 기반 문제는 `lo, mid, hi`, DP 문제는 `state, transition`, 그래프 문제는 `queue size, visited count`를 같이 기록하면 원인 분리가 훨씬 빨라집니다.

### 3) Python 구현 앵커

```python
import heapq

def top_k(nums, k):
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 912 Sort an Array | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 56 Merge Intervals | 상태/포인터 유지 | 경계 인덱스 처리 |
| 215 Kth Largest Element | 자료구조 선택 | 복잡도 목표 미달 |

문제 매핑의 목적은 정답 암기가 아닙니다. 같은 구조를 빠르게 인식하고, "왜 이 패턴을 쓰는가"를 재현하는 데 있습니다. 시리즈 전체를 관통하는 실력 차이는 여기서 발생합니다.

### 5) 비교 벤치마크를 읽는 기준

| 비교 항목 | A 접근 | B 접근 | 의사결정 기준 |
| --- | --- | --- | --- |
| 시간 | 평균적으로 빠름 | 최악 케이스 안정적 | 입력 분포가 고정인지 |
| 메모리 | 추가 배열 필요 | 제자리 처리 가능 | 메모리 제한 강도 |
| 구현 난이도 | 짧음 | 디버깅 난이도 높음 | 팀 유지보수 역량 |

벤치마크 숫자는 환경에 따라 달라집니다. 하지만 차수와 메모리 계층에서 발생하는 방향성은 반복됩니다. 그래서 한 번 측정한 결과를 절대값으로 외우기보다, 어떤 조건에서 우위가 바뀌는지(입력 크기, 정렬 여부, 중복 비율)를 함께 기록해야 다음 의사결정에 도움이 됩니다.

### 6) 제출/배포 전 점검 루틴

1. 문제 제약을 한 줄로 요약하고 불가능한 차수를 먼저 제거합니다.
2. 핵심 자료구조 선택 이유를 "삽입/조회/삭제 비용" 기준으로 적습니다.
3. 경계 입력 3종(빈값, 최소값, 중복/극단값) 테스트를 고정합니다.
4. 시간·공간 복잡도를 코드 옆에 기록하고, 실제 측정값을 짧게 남깁니다.
5. 같은 패턴의 변형 문제를 1개 더 풀어 일반화 여부를 확인합니다.

이 루틴을 꾸준히 적용하면 "이번 문제를 맞춤"에서 끝나지 않고 "같은 유형을 안정적으로 재현"하는 상태로 넘어갈 수 있습니다. 알고리즘 학습은 지식 축적이 아니라 판단 체계 구축이라는 점을 계속 기억하는 것이 중요합니다.

## 처음 질문으로 돌아가기

- **비교 기반 정렬은 왜 O(n log n)보다 더 좋아질 수 없을까요?**
  - 본문의 기준은 정렬 알고리즘를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **mergesort, quicksort, heapsort는 각각 무엇을 주고 무엇을 얻을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **안정 정렬과 비안정 정렬의 차이는 왜 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- **정렬 알고리즘 (현재 글)**
- 재귀와 분할 정복 (예정)
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `sorted` documentation](https://docs.python.org/3/library/functions.html#sorted)
- [Python sort how-to](https://docs.python.org/3/howto/sorting.html)
- [Tim Peters — Timsort listsort.txt](https://github.com/python/cpython/blob/main/Objects/listsort.txt)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 2](https://algs4.cs.princeton.edu/20sorting/)

Tags: Computer Science, 알고리즘, 정렬, 퀵소트, 머지소트, Timsort
