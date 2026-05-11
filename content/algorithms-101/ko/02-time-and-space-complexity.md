---
series: algorithms-101
episode: 2
title: 시간 복잡도와 공간 복잡도
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
  - 시간 복잡도
  - 공간 복잡도
  - 빅오
  - 분석
seo_description: 빅오 표기법, 평균·최악·분할 상환의 차이, 그리고 이론과 측정을 함께 보는 알고리즘 비용 분석법을 정리합니다.
last_reviewed: '2026-05-04'
---

# 시간 복잡도와 공간 복잡도

> Algorithms 101 시리즈 (2/10)


## 이 글에서 다룰 문제

복잡도 분석은 알고리즘 비교의 공통 언어입니다. "더 빠르다"라는 주장은 측정 환경에 따라 달라지지만 빅오는 입력 크기에 따른 점근적 증가율이라는 보편적 척도를 제공합니다. 또한 복잡도 분석을 통해 측정 없이도 "n이 100배 커지면 시간이 어떻게 될지"를 미리 예측할 수 있습니다.

> 복잡도 = 미래 비용을 미리 보는 망원경.

## 전체 흐름
> 빅오는 "최악의 경우 이보다 더 나빠지지는 않는다"는 상한입니다. n^2 알고리즘은 n이 두 배가 되면 시간이 약 네 배가 됩니다. log n 알고리즘은 n이 두 배가 되어도 시간이 거의 변하지 않습니다. 이 차이를 직관적으로 갖는 것이 분석의 출발점입니다.

```text
n=10                n=1000              n=1,000,000
O(1)        1            1                  1
O(log n)    3            10                 20
O(n)        10           1000               1,000,000
O(n log n)  33           10,000             20,000,000
O(n^2)      100          1,000,000          10^12
O(2^n)      1024         🔥                 ☠️
```

## Before / After

**Before — 빅오 무시:**

```python
# 정렬 후 set으로 중복 제거
def dedup(arr):
    return list(set(sorted(arr)))   # 정렬 O(n log n) 불필요
```

**After — 분석 후 단순화:**

```python
def dedup(arr):
    return list(set(arr))           # set 자체로 O(n)
```

빅오를 의식하면 불필요한 연산을 자연스럽게 제거할 수 있습니다.

## 단계별로 따라하기

### 1단계: 코드에서 빅오 읽기

```python
def example_a(n):
    return n * 2                    # O(1)

def example_b(n):
    total = 0
    for i in range(n):              # O(n)
        total += i
    return total

def example_c(n):
    pairs = []
    for i in range(n):              # O(n)
        for j in range(n):          # O(n)
            pairs.append((i, j))    # 합쳐서 O(n^2)
    return pairs

def example_d(n):
    while n > 1:                    # n이 매번 절반 → O(log n)
        n //= 2
```

루프와 호출 구조만 보고도 빅오를 추정할 수 있습니다. 깊이 보지 말고 "주요 반복 횟수"를 셉니다.

### 2단계: 평균과 최악의 차이

```python
def linear_search(arr, target):
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1

# 최악: target이 마지막 원소 → O(n)
# 최선: target이 첫 원소 → O(1)
# 평균: 균등 분포 가정 시 O(n/2) ≈ O(n)
```

빅오는 보통 최악을 가정하지만 실무에서는 평균이 더 의미 있을 때도 많습니다. 둘을 구분해서 말하는 습관이 중요합니다.

### 3단계: 분할 상환 분석

```python
# Python list의 append: 보통 O(1), 가끔 O(n) (재할당)
arr = []
for i in range(10**6):
    arr.append(i)
# 10^6번 append 총 비용 ≈ O(n) → 1회당 분할 상환 O(1)
```

가끔 비싼 연산이 있어도 전체로 평균 내면 싸다면 분할 상환 복잡도로 표현합니다. Python의 list, 해시 테이블 rehash가 대표적입니다.

### 4단계: 공간 복잡도

```python
# O(1) 공간: 입력에 비례하지 않는 추가 메모리
def sum_iterative(nums):
    total = 0
    for n in nums:
        total += n
    return total

# O(n) 공간: 결과 배열을 새로 만듦
def double_all(nums):
    return [n * 2 for n in nums]

# O(n) 공간: 재귀 호출 스택
def sum_recursive(nums, i=0):
    if i == len(nums):
        return 0
    return nums[i] + sum_recursive(nums, i + 1)
```

시간 복잡도만 보면 위험합니다. 큰 입력에서 메모리 한계가 먼저 옵니다. 재귀 알고리즘은 특히 호출 스택의 공간을 잊지 마세요.

### 5단계: 이론과 측정의 비교

```python
import time

def measure(fn, n):
    data = list(range(n))
    start = time.perf_counter()
    fn(data)
    return (time.perf_counter() - start) * 1000

def linear_op(arr):
    return sum(arr)

def quadratic_op(arr):
    return [(i, j) for i in arr[:1000] for j in arr[:1000]]

for n in [10_000, 100_000, 1_000_000]:
    print(f"n={n:,}: linear {measure(linear_op, n):.2f} ms")
```

측정으로 빅오 예측을 검증합니다. n을 10배 늘렸을 때 O(n)은 10배, O(n^2)은 100배가 되어야 합니다. 그렇지 않다면 가정에 오류가 있습니다.

## 이 코드에서 주목할 점

- 빅오는 "어떻게 자라는가"를 보는 도구이지 절대 시간이 아닙니다
- 평균과 최악을 구분해 말해야 합니다
- 공간 복잡도를 잊으면 메모리 한계로 무너집니다
- 측정으로 이론을 검증하는 습관이 분석을 정확하게 만듭니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 상수 무시 | 같은 빅오인데 100배 차이 | 측정으로 보완 |
| 최악만 본다 | 평균이 훨씬 좋은 경우 놓침 | 평균/최악 구분 |
| 공간 무시 | OOM 발생 | 시간/공간 함께 본다 |
| log n 무시 | 사실상 상수 시간 | 빅오 단순화에 익숙해진다 |
| 빅오를 절대 시간으로 오해 | n=10에 빅오 무의미 | 점근적 의미 이해 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 쿼리 플래너: 통계 기반 비용 추정으로 알고리즘 선택
- 클라우드 비용 모델: 입력 크기 대비 비용을 빅오로 표현
- 면접 시스템 설계: "n이 1억일 때" 가정으로 알고리즘 비교
- 머신러닝: 학습 시간을 데이터 크기와 모델 파라미터의 빅오로 표현
- 게임 엔진: 프레임당 처리 가능한 객체 수를 빅오로 추정

## 체크리스트

- [ ] 빅오·빅오메가·빅세타의 차이를 설명할 수 있는가
- [ ] 평균과 최악을 구분해서 말할 수 있는가
- [ ] 공간 복잡도를 시간과 함께 분석하는가
- [ ] 분할 상환의 의미와 예를 알고 있는가
- [ ] 측정으로 빅오 예측을 검증하는가

## 정리 및 다음 단계

복잡도 분석은 알고리즘의 비용을 보편적으로 표현하는 도구입니다. 빅오는 점근적 상한이며 평균·최악·분할 상환은 다른 관점입니다. 시간만이 아니라 공간도 함께 봐야 하며, 이론과 측정은 서로를 보완합니다. 시니어는 빅오를 도구로 사용하지 절대 진리로 사용하지 않습니다.

다음 글에서는 가장 기본적인 알고리즘인 탐색을 다룹니다. 선형 탐색과 이진 탐색의 비용 차이, 그리고 자료구조의 정렬 여부가 만드는 차이를 봅니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
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

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Wikipedia — Big O Notation](https://en.wikipedia.org/wiki/Big_O_notation)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [CLRS — Chapter 3: Growth of Functions](https://mitpress.mit.edu/9780262033848/introduction-to-algorithms/)

Tags: Computer Science, 알고리즘, 시간 복잡도, 공간 복잡도, 빅오, 분석
