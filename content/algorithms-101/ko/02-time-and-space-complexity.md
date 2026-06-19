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

코드를 쓰기 전에도 이 알고리즘이 충분히 빠를지 예측할 수 있을까요? 여기서는 Big-O와 관련 표기법, 그리고 벤치마크 전에 알고리즘을 비교하기 위한 비용 모델을 정리합니다.

이 글은 Algorithms 101 시리즈의 2번째 글입니다.

![Algorithms 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/02/02-01-big-picture.ko.png)
*Algorithms 101 2장 흐름 개요*

## 이 글에서 다룰 문제

- Big-O, Big-Omega, Big-Theta는 각각 무엇을 뜻할까요?
- 코드 조각만 보고 복잡도를 어떻게 추정할 수 있을까요?
- 반드시 즉시 떠올릴 수 있어야 하는 비용 계층은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

점근 분석은 엔지니어가 성능을 논의할 때 쓰는 공통 언어입니다. 이 언어가 없으면 "이게 충분히 빠른가"라는 질문은 추측에 머무릅니다. 반대로 이 언어가 있으면 코드를 실행하기 전에도 두 알고리즘을 비교할 수 있고, 현재보다 100배 큰 부하에서 버틸지 미리 가늠할 수 있습니다.

> Big-O는 성능 논증이 이루어지는 언어입니다.

> 복잡도는 절대 시간이 아니라 증가율을 설명합니다. O(n) 알고리즘이 작은 입력에서는 O(n log n)보다 느릴 수 있지만, 입력이 충분히 커지면 결국 이깁니다. 점근 표기법은 상수와 하드웨어 차이를 숨김으로써 서로 다른 환경에서도 공정하게 비교할 수 있게 해 줍니다.

```text
Cost classes (low to high)
    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n^2)     quadratic
    O(2^n)     exponential
    O(n!)      factorial
```

| 용어 | 설명 |
| --- | --- |
| Big-O | 점근적 상한, 보통 최악 비용을 설명할 때 사용 |
| Big-Omega | 점근적 하한 |
| Big-Theta | 상한과 하한이 같은 타이트한 경계 |
| 최악 경우 | 크기 n인 입력 중 가장 큰 비용 |
| 분할 상환 | 긴 연산 시퀀스 전체로 평균 낸 비용 |

## 개선 전 / 개선 후

**Before — 코드가 충분히 빠를지 감으로 판단:**

```python
# "내 노트북에서는 1초 안에 돌아가니까 배포하자."
# 생산 데이터는 1000배 더 큽니다.
def sum_pairs(arr):
    results = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):   # O(n^2)
            results.append(arr[i] + arr[j])
    return results
```

**After — 입력 크기에서 비용 추정, 더 나은 접근 선택:**

```python
def sum_pairs_linear(arr):
    # 합만 필요하다면 O(n)으로 충분한 경우도 있습니다.
    total = sum(arr)
    # 각 원소가 (n-1)번 다른 원소와 짝을 이룸
    return [total - v for v in arr]    # O(n)
```

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
    return arr[0]                 # O(1) — 인덱스 접근

def logarithmic(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2     # O(log n) — 절반씩 줄임
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def linear(arr):
    return sum(arr)               # O(n) — 모든 원소 한 번

def quadratic(arr):
    out = 0
    for x in arr:
        for y in arr:             # O(n^2) — 중첩 루프
            out += x * y
    return out
```

비용 계층은 언어가 아니라 루프와 호출 구조의 모양이 결정합니다.

### 2단계: 선형로그 시간 패턴 읽기

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)     # O(n log n)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out
```

절반으로 나누는 단계가 `log n`층, 각 층에서 하는 일이 O(n)이므로 전체는 O(n log n)입니다.

### 3단계: 입력 크기에서 역으로 추정

```text
n ≤ 10               → O(n!) 가능, 완전 탐색 가능
n ≤ 20               → O(2^n) 가능, 비트마스크 DP
n ≤ 500              → O(n^3) 가능
n ≤ 5,000            → O(n^2) 가능
n ≤ 10^5 ~ 10^6      → O(n log n) 필요
n ≥ 10^7             → O(n) 또는 O(log n) 필요
```

이 표를 외우는 일은 투자 대비 효과가 매우 큽니다. 많은 문제는 이 단계에서 절반 이상 풀립니다.

### 4단계: 최악 경우와 분할 상환 구분

```python
import time

arr = []
t0 = time.perf_counter()
for i in range(10**6):
    arr.append(i)        # 평균 O(1), resize 발생 시 O(n)
t1 = time.perf_counter()
print(f"total {t1 - t0:.3f}s, avg per op: {(t1 - t0) / 10**6 * 1e9:.1f}ns")
```

Python 리스트의 `append`는 분할 상환 O(1)입니다. 대부분의 호출은 O(1)이지만, 가끔 일어나는 resize에서는 전체 배열을 복사합니다. 최악의 순간과 긴 시퀀스 평균을 구분해야 할 때 분할 상환 분석이 필요합니다.

### 5단계: 공간 복잡도도 별도로 추정

```python
# O(1) 공간 — 변수만 사용
def sum_inplace(arr):
    total = 0
    for v in arr:
        total += v
    return total

# O(n) 공간 — 보조 배열
def prefix_sums(arr):
    ps = [0] * (len(arr) + 1)
    for i, v in enumerate(arr):
        ps[i + 1] = ps[i] + v
    return ps

# O(n log n) 공간 — 재귀 스택과 임시 배열
def mergesort_space(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(mergesort_space(arr[:mid]), mergesort_space(arr[mid:]))
```

시간 복잡도와 공간 복잡도는 독립된 두 축입니다. 종종 시간을 줄이면 공간이 늘어나는 트레이드오프가 발생합니다.

### 6단계: 실제 측정으로 확인

```python
import time

def measure(fn, *args, repeat=5):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best

sizes = [1_000, 10_000, 100_000]
for n in sizes:
    arr = list(range(n))
    t = measure(sum, arr)
    print(f"n={n:7d}  sum={t*1000:.3f}ms")
```

측정값이 예측한 비용 계층과 일치하는지 확인하는 습관이 중요합니다.

## 복잡도 계층 비교표

| 복잡도 | 이름 | n=10^3 연산 수 | n=10^6 연산 수 | 대표 알고리즘 |
| --- | --- | --- | --- | --- |
| O(1) | 상수 | 1 | 1 | 해시 조회, 배열 인덱싱 |
| O(log n) | 로그 | ~10 | ~20 | 이진 탐색, 트리 조회 |
| O(n) | 선형 | 10^3 | 10^6 | 선형 탐색, 합 계산 |
| O(n log n) | 선형로그 | ~10^4 | ~2×10^7 | 병합 정렬, 힙 정렬 |
| O(n^2) | 이차 | 10^6 | 10^12 | 버블 정렬, 나이브 탐색 |
| O(2^n) | 지수 | 엄청남 | 불가 | 부분집합 열거, 백트래킹 |
| O(n!) | 팩토리얼 | 불가 | 불가 | TSP 완전 탐색 |

## 이 글에서 먼저 가져갈 점

- Big-O는 상수를 숨기지만, 작은 n에서는 상수도 중요합니다.
- 운영에서는 시간이 흐르며 최악 경우가 결국 드러나는 일이 많습니다.
- 공간 복잡도는 시간 복잡도와 별개의 축입니다.
- 로그의 밑은 무시합니다. O(log n)과 O(log₂ n)은 같은 계층입니다.
- 분할 상환 복잡도는 시퀀스 전체를 보아야 정확하게 계산됩니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 작은 입력의 실제 시간만 보고 비교 | 큰 입력에서 승자가 바뀜 | 밀리초보다 비용 계층을 먼저 봅니다 |
| 바깥 루프만 세고 안쪽 비용을 무시 | 중첩 비용 누락 | 중첩 루프는 곱해서 계산합니다 |
| 상수를 완전히 무시 | 핫패스가 의외로 느림 | 계층과 상수 둘 다 봅니다 |
| 평균과 최악을 혼동 | 운영 지연 급증 | 지연 민감한 시스템은 최악 기준으로 봅니다 |
| O(log n)을 거의 상수라고 오해 | 큰 n에서 비용 과소평가 | 작지만 공짜는 아니라는 감각을 유지합니다 |
| 공간 복잡도를 분석에서 제외 | 메모리 부족 운영 장애 | 시간과 공간을 항상 함께 추정합니다 |

## 실무에서는 이렇게 쓰입니다

- 코드 리뷰에서는 큰 입력에 대한 O(n²) 루프를 먼저 경계합니다.
- 데이터베이스 쿼리 플랜도 같은 점근 언어로 비교합니다.
- 용량 계획은 부하 증가와 알고리즘 계층을 함께 봅니다.
- 핫패스 최적화는 계층과 상수를 동시에 낮추는 일입니다.
- 알고리즘 면접은 사실상 점근 분석 면접에 가깝습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드를 보는 순간 복잡도 계층을 대략 읽습니다. 같은 입력을 중첩 루프로 돌면 O(n²)이고, 분할 정복 뒤 병합이 선형이면 O(n log n)이라는 식의 패턴 인식이 몸에 배어 있습니다.

또한 비용 계층과 상수 계수를 분리해서 생각합니다. 입력이 작을 때는 계층이 나빠도 상수가 작은 구현이 이길 수 있습니다. 입력이 충분히 크면 결국 계층이 지배합니다. 자신의 입력이 그 곡선의 어디쯤 있는지 파악하는 일이 성능 엔지니어링의 절반입니다.

분할 상환 분석은 실제 시스템에서 매우 중요합니다. Python 리스트, Java ArrayList, 해시 맵의 리해싱이 모두 분할 상환 O(1) 삽입에 기반합니다. 단일 최악 케이스를 이유로 이런 구조를 기피하면 더 나쁜 선택을 하게 됩니다.

## 운영 체크리스트

- [ ] 함수의 비용 계층을 30초 안에 읽을 수 있는가
- [ ] 코딩 전에 복잡도를 추정하는가
- [ ] 최악, 평균, 분할 상환을 구분할 수 있는가
- [ ] 입력 크기 표를 거의 외우고 있는가
- [ ] 왜 O(log n)이 O(n)보다 극적으로 작은지 설명할 수 있는가
- [ ] 공간 복잡도도 시간 복잡도와 함께 추정하는가

## 연습 문제

1. 다음 세 경우의 시간 복잡도를 Big-O로 적고 한 문장씩 근거를 설명해 보세요. 삼중 중첩 루프, `T(n)=2T(n/2)+O(n)`, `T(n)=T(n/2)+O(1)`.

2. 정렬된 배열에서 합이 target이 되는 두 인덱스를 찾는 함수를 작성해 보세요. 먼저 O(n²) 브루트포스를 쓰고, 그다음 투 포인터로 O(n)으로 개선한 뒤 차이를 설명해 보세요.

3. 실제 코드에서 함수 하나를 골라 시간 복잡도와 공간 복잡도를 적어 보세요. 그리고 그중 하나를 적어도 한 계층 낮출 수 있는 변경을 하나 제안해 보세요.

4. Python의 `list.append`, `list.insert(0, x)`, `dict[key]` 연산의 시간 복잡도를 각각 적고, 분할 상환 분석이 필요한 경우를 설명해 보세요.

## 정리 및 다음 단계

점근 분석은 성능을 논의하는 공통 언어입니다. Big-O는 상한, Omega는 하한, Theta는 타이트한 경계입니다. 자주 나오는 비용 계층을 눈에 익히고 입력 크기와 연결하면 코드가 확장될지 미리 예측할 수 있습니다.

다음 글에서는 이 언어를 탐색 알고리즘에 적용합니다. O(n)과 O(log n)의 차이가 실제로 어떤 의미인지, 선형 탐색과 이진 탐색을 통해 구체적으로 보겠습니다.

## 처음 질문으로 돌아가기

- **Big-O, Big-Omega, Big-Theta는 각각 무엇을 뜻할까요?**
  - Big-O는 점근적 상한으로 최악 비용을 표현합니다. Big-Omega는 점근적 하한으로 최선 비용을 표현합니다. Big-Theta는 상한과 하한이 같을 때 쓰는 타이트한 경계로, 알고리즘의 정확한 비용 계층을 표현합니다.
- **코드 조각만 보고 복잡도를 어떻게 추정할 수 있을까요?**
  - 루프의 반복 횟수를 n의 함수로 표현하고, 중첩 루프는 곱하며, 재귀는 점화식으로 표현합니다. 단일 루프는 O(n), 이중 중첩은 O(n²), 절반씩 줄이는 패턴은 O(log n)이 됩니다.
- **반드시 즉시 떠올릴 수 있어야 하는 비용 계층은 무엇일까요?**
  - O(1), O(log n), O(n), O(n log n), O(n²), O(2^n)의 6개 계층입니다. 각각의 대표 알고리즘과 입력 크기에서의 연산 수를 함께 외워 두어야 즉각적인 판단이 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- **Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도 (현재 글)**
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Wikipedia — Big O notation](https://en.wikipedia.org/wiki/Big_O_notation)
- [CLRS — Introduction to Algorithms, Chapter 3](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Open Data Structures — Asymptotic Notation](https://opendatastructures.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)

Tags: Computer Science, 알고리즘, Big-O, 복잡도, 성능, 점근 분석
