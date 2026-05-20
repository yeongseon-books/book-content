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

이 그림에서는 시간 복잡도와 공간 복잡도를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 시간 복잡도와 공간 복잡도의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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
