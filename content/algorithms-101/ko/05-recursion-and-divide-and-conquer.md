---
series: algorithms-101
episode: 5
title: "Algorithms 101 (5/10): 재귀와 분할 정복"
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
  - 재귀
  - 분할 정복
  - 호출 스택
  - 메모이제이션
seo_description: 올바른 재귀의 세 가지 규칙, 호출 스택, 분할 정복 점화식, 그리고 메모이제이션으로 이어지는 사고를 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (5/10): 재귀와 분할 정복

이 글은 Algorithms 101 시리즈의 5번째 글입니다.

재귀는 왜 어렵게 느껴질까요? 그리고 mergesort 같은 분할 정복 알고리즘은 왜 "올바른 이유로" 빠를까요? 여기서는 호출 스택, 점화식 기반 비용 분석, 그리고 분할 정복의 핵심 멘탈 모델을 정리합니다.

![Algorithms 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/05/05-01-big-picture.ko.png)
*Algorithms 101 5장 흐름 개요*

## 먼저 던지는 질문

- 올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?
- 호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?
- 분할 정복 점화식은 어떻게 읽어야 할까요?

## 왜 중요한가

재귀가 익숙하지 않으면 트리, 그래프, 분할 정복, 동적 계획법, 백트래킹이 모두 더 어렵게 느껴집니다. 반대로 재귀 사고가 자리 잡으면 복잡한 문제를 "자기 자신과 같은 형태의 더 작은 문제"로 자연스럽게 분해할 수 있습니다.

> 재귀는 알고리즘의 두 번째 모국어입니다.

## 한눈에 보는 개념

> 재귀 함수는 베이스 케이스, 진행 단계, 자기 호출을 가집니다. 분할 정복은 입력을 크기 `n/b`인 부분 문제 `a`개로 나누고, 결과를 `f(n)` 비용으로 결합합니다. 전체 비용은 `T(n) = a · T(n/b) + f(n)`으로 표현할 수 있고, 대표적으로 mergesort는 O(n log n), binary search는 O(log n)이 됩니다.

```text
Recursive shape
    if base case: return
    self-call(smaller input)
    combine results

Divide-and-conquer recurrence
    T(n) = a · T(n/b) + f(n)
    e.g. mergesort     T(n) = 2T(n/2) + O(n) = O(n log n)
         binary search T(n) = T(n/2)   + O(1) = O(log n)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 베이스 케이스 | 더 이상 재귀하지 않고 끝나는 종료 조건 |
| 호출 스택 | 중첩된 함수 호출 문맥이 쌓이는 구조 |
| 분할 정복 | divide → conquer → combine 패턴 |
| 점화식 | 재귀 비용을 표현하는 식 |
| 메모이제이션 | 반복되는 부분 문제 결과를 캐싱하는 기법 |

## 개선 전 / 개선 후

**Before — 베이스 케이스 누락:**

```python
def factorial(n):
    return n * factorial(n - 1)        # no termination → RecursionError
```

**After — 명시적 베이스 케이스:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## 단계별로 따라가기

### 1단계: 재귀의 세 가지 규칙

```python
def power(base, exp):
    if exp == 0:                           # (1) base case
        return 1
    return base * power(base, exp - 1)     # (2) smaller input (3) self-call

print(power(2, 10))   # 1024
```

베이스 케이스는 실제로 도달 가능해야 하고, 모든 호출은 그쪽으로 엄격하게 가까워져야 합니다.

### 2단계: 호출 스택과 `RecursionError`

```python
import sys
print(sys.getrecursionlimit())     # 1000 by default

def deep(n):
    if n == 0:
        return 0
    return 1 + deep(n - 1)

try:
    deep(2000)
except RecursionError as e:
    print("RecursionError:", e)

sys.setrecursionlimit(10_000)
print(deep(2000))
```

CPython에는 tail-call optimisation이 없습니다. 깊은 재귀는 한도를 높이거나 반복문으로 바꿔야 합니다.

### 3단계: 분할 정복 거듭제곱, O(n) → O(log n)

```python
def fast_power(base, exp):
    if exp == 0:
        return 1
    half = fast_power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

print(fast_power(2, 30))   # 1073741824
```

지수를 절반으로 줄이면 호출 수가 O(log n)이 됩니다. 암호학의 modular exponentiation에서도 같은 아이디어를 씁니다.

### 4단계: Mergesort로 점화식 체감하기

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

`T(n) = 2T(n/2) + O(n)`이 O(n log n)이 되는 가장 친숙한 예입니다.

### 5단계: 반복 부분 문제에서 메모이제이션으로

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)
# 동일한 하위 문제가 기하급수적으로 반복되고 매우 느림

from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(100))
```

캐싱을 추가하면 O(2^n)이 O(n)으로 무너집니다. 바로 다음 글인 동적 계획법으로 이어지는 핵심 전환점입니다.

## 이 글에서 먼저 가져갈 점

- 베이스 케이스가 실제로 도달 가능한지 항상 확인해야 합니다.
- 결합 비용 `f(n)`이 전체 복잡도를 지배할 수 있습니다.
- 반복 부분 문제를 발견하면 큰 폭의 최적화 기회가 생깁니다.
- Python의 깊은 재귀는 종종 반복문으로 바꿔야 합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 베이스 케이스가 없거나 도달 불가 | 무한 재귀 | 입력이 단조롭게 줄어드는지 확인합니다 |
| 가변 객체를 호출 간 공유 | 의도치 않은 누적 | 복사하거나 인덱스를 전달합니다 |
| Python에서 깊은 재귀를 그대로 사용 | `RecursionError` | 반복문으로 바꾸거나 한도를 조정합니다 |
| 분할 비율 `b`를 무시 | 복잡도 오판 | 점화식으로 적고 읽습니다 |
| 반복 부분 문제를 놓침 | 지수 시간 | `lru_cache` 같은 메모이제이션을 추가합니다 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템 재귀 순회
- 컴파일러 AST 순회와 변환
- 분산 reduce 단계의 k-way 병합
- 그래픽스의 quadtree, octree
- 결정 트리 학습의 재귀적 분할

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 문제가 자연스럽게 트리 구조를 가지면 재귀를 택하고, 깊은 선형 체인이라면 반복을 더 선호합니다. 표현력과 성능을 함께 보되, 성능 민감한 경로에서는 명시적 스택을 가진 반복 구현을 먼저 고려합니다.

또한 분할 정복을 보면 머릿속에서 바로 점화식을 그립니다. `T(n)=2T(n/2)+O(n)`은 O(n log n), `T(n)=T(n/2)+O(1)`은 O(log n)이라는 감각만 있어도 실전 분석의 상당수를 커버할 수 있습니다.

## 체크리스트

- [ ] 재귀의 세 가지 규칙을 점검할 수 있는가
- [ ] `RecursionError`가 무엇을 의미하는지 아는가
- [ ] 분할 정복 루틴의 점화식을 쓸 수 있는가
- [ ] 반복 부분 문제를 알아볼 수 있는가
- [ ] 깊은 재귀를 반복문으로 바꿀 수 있는가

## 연습 문제

1. 정수 배열의 합을 분할 정복으로 계산하고, 단순 반복과 비교해 보세요. 점화식과 복잡도도 함께 적어 보세요.

2. 두 정렬 리스트의 교집합을 재귀적으로 구해 보고, 두 리스트 크기가 크게 다를 때는 이진 탐색으로 어떻게 개선할 수 있는지 설명해 보세요.

3. 하노이 탑을 재귀로 풀고, 호출 횟수가 `2^n - 1`이 되는 이유를 점화식으로 증명해 보세요.

## 정리 및 다음 단계

재귀는 문제를 더 작은 자기 자신으로 표현하는 방식입니다. 분할 정복은 그중 가장 유용한 패턴이며, 비용은 점화식으로 분석합니다. 부분 문제가 반복되면 메모이제이션이 필요해지고, 바로 그 지점에서 동적 계획법으로 자연스럽게 이어집니다.

다음 글에서는 동적 계획법을 본격적으로 다룹니다. 메모이제이션과 타뷸레이션, 상태 설계, 그리고 0/1 knapsack과 LCS 같은 대표 문제를 봅니다.

## 추가 보강: 검증 가능한 예제 세트

### 입력 크기 대비 알고리즘/학습 선택 표

| 상황 | 빠른 선택 | 검증 기준 |
| --- | --- | --- |
| 작은 입력, 빠른 프로토타입 | 단순 구현 우선 | 정답 검증 테스트 3종 |
| 큰 입력, 지연시간 민감 | 차수 낮은 알고리즘 또는 안정적 optimizer | 시간/메모리 동시 측정 |
| 운영 장애 재현 필요 | 로그/추적 필드 강화 | 동일 입력 재실행 가능성 |

### 짧은 비교 코드

```python
import time

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best
```

측정 코드는 화려할 필요가 없습니다. 같은 입력, 같은 환경, 같은 반복 기준을 유지하는 것이 더 중요합니다. 이 습관이 있어야 최적화 전후의 차이를 신뢰할 수 있습니다.

### 실전 점검 질문

1. 지금 선택한 방법의 시간/공간 비용을 한 문장으로 설명할 수 있는가
2. 경계 입력에서 동작이 바뀌는 지점을 테스트로 고정했는가
3. 운영 로그만으로 실패 원인을 분리할 수 있는가

이 질문에 즉답할 수 있으면 구현이 아니라 설계 수준에서 품질을 확보한 상태에 가깝습니다.

## 실전 확장 워크북

이 절은 재귀/분할 정복 설계를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

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
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 50 Pow(x, n) | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 169 Majority Element | 상태/포인터 유지 | 경계 인덱스 처리 |
| 148 Sort List | 자료구조 선택 | 복잡도 목표 미달 |

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

- **올바른 재귀가 되기 위한 세 가지 규칙은 무엇일까요?**
  - `power(base, exp)` 예시처럼 베이스 케이스가 있어야 하고, 입력이 더 작은 쪽으로 줄어야 하며, 그 작은 입력에 자기 자신을 호출해야 합니다. 셋 중 하나라도 빠지면 본문의 잘못된 `factorial(n)`처럼 재귀가 설계가 아니라 사고가 됩니다.
- **호출 스택은 어떻게 동작하며, `RecursionError`는 왜 생길까요?**
  - `deep(2000)` 예시에서 보듯 호출할 때마다 스택 프레임이 쌓이고, CPython 기본 한도인 `sys.getrecursionlimit()`을 넘기면 `RecursionError`가 납니다. 그래서 깊은 문제는 한도를 조정하거나 반복문으로 바꾸라는 결론이 나옵니다.
- **분할 정복 점화식은 어떻게 읽어야 할까요?**
  - `T(n) = a · T(n/b) + f(n)`은 “크기 n/b 하위 문제를 a개 풀고, 마지막에 f(n)만큼 합친다”로 읽으면 됩니다. `mergesort`의 `2T(n/2) + O(n)`과 `binary search`의 `T(n/2) + O(1)`를 나란히 본 이유가 바로 그 해석 감각을 만들기 위해서였습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- **재귀와 분할 정복 (현재 글)**
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Python `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Wikipedia — Master theorem](https://en.wikipedia.org/wiki/Master_theorem)
- [CLRS — Introduction to Algorithms, Chapter 4](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 재귀, 분할 정복, 호출 스택, 메모이제이션
