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

## 먼저 던지는 질문

- 선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?
- 정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?
- lower bound와 upper bound는 각각 어디에 쓰일까요?

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
# O(로그 n)
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
# n개의 통나무를 m개의 동일한 조각으로 자릅니다. 조각당 최대 길이를 구합니다.
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

또한 "가장 큰 X such that ..." 같은 문장을 보면 답의 단조성을 먼저 확인합니다. 가능 여부가 한 방향으로만 바뀐다면, 이는 parametric search를 적용하라는 강한 신호입니다.

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

다음 글에서는 정렬 알고리즘을 다룹니다. mergesort, quicksort, heapsort의 트레이드오프와 Python의 `sorted`가 왜 Timsort를 쓰는지 봅니다.

## 실전 확장 워크북

이 절은 탐색 알고리즘 선택를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

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
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    trace = []
    while lo <= hi:
        mid = (lo + hi) // 2
        trace.append((lo, mid, hi, arr[mid]))
        if arr[mid] == target:
            return mid, trace
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, trace
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 704 Binary Search | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 35 Search Insert Position | 상태/포인터 유지 | 경계 인덱스 처리 |
| 33 Search in Rotated Sorted Array | 자료구조 선택 | 복잡도 목표 미달 |

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

- **선형 탐색과 이진 탐색의 비용 차이는 얼마나 클까요?**
  - `[3, 1, 4, 1, 5, 9, 2, 6]`를 처음부터 훑는 `linear_search()`는 O(n)이지만, 정렬된 배열에서 `binary_search()`는 후보를 절반씩 줄여 O(log n)으로 끝납니다. 본문의 8개 원소 예시에서 8번 비교와 약 3번 비교로 대비한 이유가 그 차이를 눈에 보이게 하려는 것이었습니다.
- **정렬 여부 하나가 왜 알고리즘 계층을 바꿀까요?**
  - 정렬이 되어 있으면 `arr[mid] < target`인지 한 번 보고 왼쪽 절반이나 오른쪽 절반 전체를 버릴 수 있습니다. 정렬이 없으면 그 근거가 사라져서 결국 `contains(sorted_arr, x)` 같은 코드도 O(n)으로 되돌아갑니다.
- **lower bound와 upper bound는 각각 어디에 쓰일까요?**
  - `lower_bound(arr, 2)`는 target 이상이 처음 나오는 위치를, `upper_bound(arr, 2)`는 target 초과가 처음 나오는 위치를 줍니다. 본문처럼 둘의 차이를 빼면 중복 개수를 세고, `bisect_left`·`bisect_right`로 삽입 위치도 바로 구할 수 있습니다.

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

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `bisect` documentation](https://docs.python.org/3/library/bisect.html)
- [Wikipedia — Binary Search Algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)
- [Open Data Structures — Searching](https://opendatastructures.org/)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 3](https://algs4.cs.princeton.edu/30searching/)

Tags: Computer Science, 알고리즘, 탐색, 이진 탐색, 선형 탐색, bisect
