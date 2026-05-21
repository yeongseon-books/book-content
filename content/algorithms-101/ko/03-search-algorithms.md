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

정렬된 정수 백만 개가 있을 때, 원하는 값을 찾으려면 처음부터 끝까지 다 봐야 할까요? 이 글은 Algorithms 101 시리즈의 세 번째 글입니다. 여기서는 선형 탐색, 이진 탐색, Python의 `bisect`, 그리고 답 자체를 이진 탐색하는 parametric search까지 다룹니다.

## 먼저 던지는 질문

- 선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?
- 정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?
- lower bound와 upper bound는 각각 어디에 쓰일까요?

## 큰 그림

![Algorithms 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/03/03-01-big-picture.ko.png)

*Algorithms 101 3장 흐름 개요*

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


## 추가 실전 섹션: 복잡도·추적·구현 선택을 한 번에 연결하기

알고리즘 학습에서 가장 중요한 전환점은 "개념 이해"와 "문제 풀이" 사이를 잇는 기준을 갖는 것입니다. 아래 표는 정렬·탐색·재귀·DP·그리디·그래프·문자열 문제를 만났을 때 가장 먼저 결정해야 할 선택지를 한눈에 정리한 것입니다.

| 문제 신호 | 1차 후보 | 시간 복잡도 목표 | 확인할 함정 |
| --- | --- | --- | --- |
| 정렬 여부가 핵심 단서 | 이진 탐색 / bisect | O(log n) | 데이터 정렬 전제 누락 |
| 전체 순위가 필요 | 정렬(Timsort/merge) | O(n log n) | 안정 정렬 필요 여부 |
| 상위 k개만 필요 | heap | O(n log k) | 전체 정렬로 과투자 |
| 부분 문제가 반복 | DP | O(states * transition) | 상태 정의 모호 |
| 즉시 최선 선택이 유력 | 그리디 | 보통 O(n log n) 이하 | 교환 논증 부재 |
| 연결·최단·순서 제약 | 그래프(BFS/DFS/다익스트라) | O(V+E), O((V+E)logV) | 가중치 조건 혼동 |
| 긴 텍스트 패턴 검색 | KMP/Trie | O(n+m) | 정규식 백트래킹 비용 |

### 추적 예시 1: 이진 탐색 경계 버그를 잡는 로그

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    trace = []
    while lo < hi:
        mid = (lo + hi) // 2
        trace.append((lo, mid, hi, arr[mid]))
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo, trace

pos, trace = lower_bound([1, 2, 2, 2, 5, 9], 2)
print(pos)
for t in trace:
    print(t)
```

이런 추적은 오프바이원 버그를 빠르게 드러냅니다. 특히 `lo`, `hi` 경계 갱신이 틀렸을 때 무한 루프가 나는 문제는 값만 출력하는 디버깅보다 경계 튜플을 기록하는 편이 더 효율적입니다.

### 추적 예시 2: 정렬 알고리즘 선택 비교

| 입력 특성 | `sorted`(Timsort) | 직접 quicksort | heap 기반 |
| --- | --- | --- | --- |
| 이미 거의 정렬 | 매우 강함(run 활용) | pivot 품질에 따라 흔들림 | 순위 작업에서는 유리 |
| 무작위 대량 데이터 | 안정적 | 평균은 빠르지만 편차 존재 | top-k에 특화 |
| 다중 키 정렬 | 안정성 덕분에 단순 | 구현 복잡 | 부분 순위만 적합 |

실무에서는 "직접 구현"보다 "표준 라이브러리 + 문제 특화 자료구조" 조합이 장기 유지보수에 유리합니다. 코드 길이가 아니라 오류 가능성과 운영 신뢰성이 핵심 기준입니다.

### 문제 풀이 루틴: 5분 점검

1. 입력 크기로 불가능한 차수(O(n^2), O(2^n) 등)를 먼저 제거합니다.
2. 전제(정렬됨, DAG, 음수 가중치 없음, 중복 허용)를 명시합니다.
3. 템플릿(이진 탐색, BFS, DP 상태 전이)을 선택합니다.
4. 작은 반례 2개를 직접 넣어 경계 동작을 확인합니다.
5. 마지막에 복잡도와 메모리 사용량을 한 줄로 기록합니다.

이 루틴을 습관화하면 "코드가 돌아간다"와 "운영에서도 안전하다" 사이의 간격이 크게 줄어듭니다.


## 처음 질문으로 돌아가기

- **선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?**
  - 본문의 기준은 탐색 알고리즘를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **lower bound와 upper bound는 각각 어디에 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
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
