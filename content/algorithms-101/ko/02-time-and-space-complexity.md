---
series: algorithms-101
episode: 2
title: "Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도"
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
  - Big-O
  - 복잡도
  - 성능
  - 점근 분석
seo_description: Big-O, Big-Omega, Big-Theta의 의미와 입력 크기에서 복잡도를 추정하는 방법을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도

코드를 쓰기 전에도 이 알고리즘이 충분히 빠를지 예측할 수 있을까요? 이 글은 Algorithms 101 시리즈의 두 번째 글입니다. 여기서는 Big-O와 관련 표기법, 그리고 벤치마크 전에 알고리즘을 비교하기 위한 비용 모델을 정리합니다.

## 먼저 던지는 질문

- Big-O, Big-Omega, Big-Theta는 각각 무엇을 뜻할까요?
- 코드 조각만 보고 복잡도를 어떻게 추정할 수 있을까요?
- 반드시 즉시 떠올릴 수 있어야 하는 비용 계층은 무엇일까요?

## 큰 그림

![Algorithms 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/02/02-01-big-picture.ko.png)

*Algorithms 101 2장 흐름 개요*

## 왜 중요한가

점근 분석은 엔지니어가 성능을 논의할 때 쓰는 공통 언어입니다. 이 언어가 없으면 "이게 충분히 빠른가"라는 질문은 추측에 머무릅니다. 반대로 이 언어가 있으면 코드를 실행하기 전에도 두 알고리즘을 비교할 수 있고, 현재보다 100배 큰 부하에서 버틸지 미리 가늠할 수 있습니다.

> Big-O는 성능 논증이 이루어지는 언어입니다.

## 한눈에 보는 개념

> 복잡도는 절대 시간이 아니라 증가율을 설명합니다. O(n) 알고리즘이 작은 입력에서는 O(n log n)보다 느릴 수 있지만, 입력이 충분히 커지면 결국 이깁니다. 점근 표기법은 상수와 하드웨어 차이를 숨김으로써 서로 다른 환경에서도 공정하게 비교할 수 있게 해 줍니다.

```text
Cost classes (low to high)
    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n^2)     quadratic
    O(2^n)     exponential
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Big-O | 점근적 상한, 보통 최악 비용을 설명할 때 사용 |
| Big-Omega | 점근적 하한 |
| Big-Theta | 상한과 하한이 같은 타이트한 경계 |
| 최악 경우 | 크기 n인 입력 중 가장 큰 비용 |
| 분할 상환 | 긴 연산 시퀀스 전체로 평균 낸 비용 |

## Before / After

**Before — 코드가 충분히 빠를지 감으로 판단:**

```python
# "내 노트북에서는 1초 안에 돌아가니까 배포하자."
# Production data is 1000x larger.
```

**After — 입력 크기에서 비용 추정:**

```text
n = 10^6, time budget = 1s
→ O(n^2) = 10^12 ops, impossible
→ O(n log n) ≈ 2 × 10^7 ops, feasible
→ Pick an O(n log n) algorithm
```

## 단계별로 따라가기

### 1단계: 자주 나오는 패턴 알아보기

```python
def constant(arr):
    return arr[0]                 # O(1)

def linear(arr):
    return sum(arr)               # O(n)

def quadratic(arr):
    out = 0
    for x in arr:
        for y in arr:             # nested loop over n
            out += x * y
    return out                    # O(n^2)
```

비용 계층은 언어가 아니라 루프와 호출 구조의 모양이 결정합니다.

### 2단계: 로그 시간 패턴 읽기

```python
def binary_search(arr, x):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                     # O(log n) — halves each step
```

매 단계마다 탐색 공간을 절반으로 줄이면 O(log n)입니다. 같은 패턴은 트리 높이, 거듭제곱 계산, 분할 정복 재귀에도 반복해서 나타납니다.

### 3단계: 선형로그 시간 패턴 읽기

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)     # O(n log n)
```

절반으로 나누는 단계가 `log n`층, 각 층에서 하는 일이 O(n)이므로 전체는 O(n log n)입니다. 효율적인 비교 기반 정렬의 전형적 비용입니다.

### 4단계: 입력 크기에서 역으로 추정

```text
n = 10              → almost anything (even O(n!))
n = 10^3            → O(n^2) okay
n = 10^5            → O(n log n) required
n = 10^7            → O(n) required
n = 10^9            → O(log n) or streaming
```

이 표를 외우는 일은 투자 대비 효과가 매우 큽니다. 실제로 많은 문제는 이 단계에서 절반 이상 풀립니다.

### 5단계: 최악 경우와 분할 상환 구분

```python
arr = []
for i in range(10**6):
    arr.append(i)                 # average O(1), worst O(n) on resize
```

Python 리스트의 `append`는 분할 상환 O(1)입니다. 대부분의 호출은 O(1)이지만, 가끔 일어나는 resize에서는 전체 배열을 복사합니다. 최악의 순간과 긴 시퀀스 평균을 구분해야 할 때 분할 상환 분석이 필요합니다.

## 이 글에서 먼저 가져갈 점

- Big-O는 상수를 숨기지만, 작은 n에서는 상수도 중요합니다.
- 운영에서는 시간이 흐르며 최악 경우가 결국 드러나는 일이 많습니다.
- 공간 복잡도는 시간 복잡도와 별개의 축입니다.
- 로그의 밑은 무시합니다. O(log n)과 O(log₂ n)은 같은 계층입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 작은 입력의 실제 시간만 보고 비교 | 큰 입력에서 승자가 바뀜 | 밀리초보다 비용 계층을 먼저 봅니다 |
| 바깥 루프만 세고 안쪽 비용을 무시 | 중첩 비용 누락 | 중첩 루프는 곱해서 계산합니다 |
| 상수를 완전히 무시 | 핫패스가 의외로 느림 | 계층과 상수 둘 다 봅니다 |
| 평균과 최악을 혼동 | 운영 지연 급증 | 지연 민감한 시스템은 최악 기준으로 봅니다 |
| O(log n)을 거의 상수라고 오해 | 큰 n에서 비용 과소평가 | 작지만 공짜는 아니라는 감각을 유지합니다 |

## 실무에서는 이렇게 쓰입니다

- 코드 리뷰에서는 큰 입력에 대한 O(n²) 루프를 먼저 경계합니다.
- 데이터베이스 쿼리 플랜도 같은 점근 언어로 비교합니다.
- 용량 계획은 부하 증가와 알고리즘 계층을 함께 봅니다.
- 핫패스 최적화는 계층과 상수를 동시에 낮추는 일입니다.
- 알고리즘 면접은 사실상 점근 분석 면접에 가깝습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드를 보는 순간 복잡도 계층을 대략 읽습니다. 같은 입력을 중첩 루프로 돌면 O(n²)이고, 분할 정복 뒤 병합이 선형이면 O(n log n)이라는 식의 패턴 인식이 몸에 배어 있습니다.

또한 비용 계층과 상수 계수를 분리해서 생각합니다. 입력이 작을 때는 계층이 나빠도 상수가 작은 구현이 이길 수 있습니다. 입력이 충분히 크면 결국 계층이 지배합니다. 자신의 입력이 그 곡선의 어디쯤 있는지 파악하는 일이 성능 엔지니어링의 절반입니다.

## 체크리스트

- [ ] 함수의 비용 계층을 30초 안에 읽을 수 있는가
- [ ] 코딩 전에 복잡도를 추정하는가
- [ ] 최악, 평균, 분할 상환을 구분할 수 있는가
- [ ] 입력 크기 표를 거의 외우고 있는가
- [ ] 왜 O(log n)이 O(n)보다 극적으로 작은지 설명할 수 있는가

## 연습 문제

1. 다음 세 경우의 시간 복잡도를 Big-O로 적고 한 문장씩 근거를 설명해 보세요. 삼중 중첩 루프, `T(n)=2T(n/2)+O(n)`, `T(n)=T(n/2)+O(1)`.

2. 정렬된 배열에서 합이 target이 되는 두 인덱스를 찾는 함수를 작성해 보세요. 먼저 O(n²) 브루트포스를 쓰고, 그다음 투 포인터로 O(n)으로 개선한 뒤 차이를 설명해 보세요.

3. 실제 코드에서 함수 하나를 골라 시간 복잡도와 공간 복잡도를 적어 보세요. 그리고 그중 하나를 적어도 한 계층 낮출 수 있는 변경을 하나 제안해 보세요.

## 정리 및 다음 단계

점근 분석은 성능을 논의하는 공통 언어입니다. Big-O는 상한, Omega는 하한, Theta는 타이트한 경계입니다. 자주 나오는 비용 계층을 눈에 익히고 입력 크기와 연결하면 코드가 확장될지 미리 예측할 수 있습니다.

다음 글에서는 이 언어를 탐색 알고리즘에 적용합니다. O(n)과 O(log n)의 차이가 실제로 어떤 의미인지, 선형 탐색과 이진 탐색을 통해 구체적으로 보겠습니다.


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



### 보강 메모: 경계 입력과 수치 검증

경계 입력을 별도 표로 관리하면 알고리즘/학습 루프의 취약점을 빠르게 찾을 수 있습니다.

| 케이스 | 기대 동작 |
| --- | --- |
| 빈 입력 또는 최소 크기 | 예외 없이 명시적 반환 |
| 중복값 다수 | 안정성/경계 갱신 유지 |
| 극단적으로 큰 값 | 오버플로우/수치 불안정 방어 |

```python
def sanity_cases(fn, cases):
    out=[]
    for c in cases:
        out.append(fn(*c) if isinstance(c, tuple) else fn(c))
    return out
```

작은 검증 루틴을 글과 코드에 함께 남기면 이후 변경에서 같은 종류의 실수를 반복할 가능성이 크게 줄어듭니다.

## 처음 질문으로 돌아가기

- **Big-O, Big-Omega, Big-Theta는 각각 무엇을 뜻할까요?**
  - 본문의 기준은 시간 복잡도와 공간 복잡도를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **코드 조각만 보고 복잡도를 어떻게 추정할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **반드시 즉시 떠올릴 수 있어야 하는 비용 계층은 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- **시간 복잡도와 공간 복잡도 (현재 글)**
- 탐색 알고리즘 (예정)
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 (예정)
- 그리디 알고리즘 (예정)
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Big O notation](https://en.wikipedia.org/wiki/Big_O_notation)
- [CLRS — Introduction to Algorithms, Chapter 3](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Open Data Structures — Asymptotic Notation](https://opendatastructures.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)

Tags: Computer Science, 알고리즘, Big-O, 복잡도, 성능, 점근 분석
