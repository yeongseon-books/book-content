---
series: algorithms-python-101
episode: 5
title: 재귀와 분할 정복
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - 알고리즘
  - 재귀
  - 분할 정복
  - 하노이 탑
seo_description: Python으로 재귀와 분할 정복 패턴을 이해하고 실전 문제에 적용합니다.
last_reviewed: '2026-05-04'
---

# 재귀와 분할 정복

> Algorithms with Python 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 큰 문제를 작은 문제로 쪼개면 왜 더 쉬워질까요?

> 재귀는 함수가 자기 자신을 호출하는 기법이고, 분할 정복은 재귀를 활용해 문제를 체계적으로 쪼개는 전략입니다. 이 글에서는 재귀의 동작 원리를 이해하고, 분할 정복 패턴을 실전 문제에 적용합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 재귀 함수의 동작 원리와 호출 스택
- 기저 조건(base case)의 중요성
- 분할 정복의 세 단계: 분할, 정복, 결합
- 재귀 → 반복 변환과 꼬리 재귀

## 왜 중요한가

재귀는 트리 탐색, 그래프 탐색, 정렬, 동적 계획법 등 거의 모든 고급 알고리즘의 기반입니다. 재귀를 이해하지 못하면 이후 알고리즘을 배우기 어렵습니다.

> 분할 정복 = 문제를 작은 부분으로 나누고(Divide), 각각 해결한 뒤(Conquer), 결과를 합치는(Combine) 전략

분할 정복은 병합 정렬, 퀵 정렬, 이진 탐색의 공통 패턴입니다. 이 패턴을 인식하면 새로운 문제도 체계적으로 풀 수 있습니다.

## 핵심 개념 잡기

> 재귀 = 함수가 자기 자신을 호출하여 반복 작업을 수행하는 기법

```
factorial(4) 호출 과정:
factorial(4) → 4 × factorial(3)
               → 3 × factorial(2)
                    → 2 × factorial(1)
                         → 1 (기저 조건)
                    ← 2 × 1 = 2
               ← 3 × 2 = 6
          ← 4 × 6 = 24
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 재귀(recursion) | 함수가 자기 자신을 호출하는 프로그래밍 기법입니다 |
| 기저 조건(base case) | 재귀 호출을 멈추는 종료 조건입니다 |
| 호출 스택(call stack) | 재귀 호출마다 쌓이는 함수 실행 컨텍스트입니다 |
| 분할 정복(divide and conquer) | 문제를 분할 → 정복 → 결합하는 알고리즘 설계 전략입니다 |
| 꼬리 재귀(tail recursion) | 재귀 호출이 함수의 마지막 연산인 형태입니다 |

## Before / After

리스트의 합을 구하는 두 가지 방법을 비교합니다.

```python
# before: 반복문
def sum_list(data):
    total = 0
    for x in data:
        total += x
    return total
```

```python
# after: 재귀
def sum_list(data):
    if not data:
        return 0
    return data[0] + sum_list(data[1:])
```

## 단계별 실습

### Step 1: 기본 재귀 — 팩토리얼과 피보나치

```python
def factorial(n: int) -> int:
    """팩토리얼 — O(n)"""
    if n <= 1:  # 기저 조건
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800


def fibonacci(n: int) -> int:
    """피보나치 — O(2^n), 비효율적"""
    if n <= 1:  # 기저 조건
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # 55
```

### Step 2: 재귀 시각화 — 호출 스택 추적

```python
def factorial_trace(n: int, depth: int = 0) -> int:
    """호출 스택을 시각적으로 보여주는 팩토리얼"""
    indent = "  " * depth
    print(f"{indent}factorial({n}) 호출")

    if n <= 1:
        print(f"{indent}기저 조건: 1 반환")
        return 1

    result = n * factorial_trace(n - 1, depth + 1)
    print(f"{indent}factorial({n}) = {result}")
    return result

factorial_trace(4)
# factorial(4) 호출
#   factorial(3) 호출
#     factorial(2) 호출
#       factorial(1) 호출
#       기저 조건: 1 반환
#     factorial(2) = 2
#   factorial(3) = 6
# factorial(4) = 24
```

### Step 3: 분할 정복 — 거듭제곱 계산

```python
def power(base: int, exp: int) -> int:
    """분할 정복 거듭제곱 — O(log n)"""
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    return base * power(base, exp - 1)

print(power(2, 10))   # 1024
print(power(3, 5))    # 243

# 비교: 단순 반복은 O(n), 분할 정복은 O(log n)
# 2^1000을 구할 때 1000번 vs ~10번 곱셈
```

### Step 4: 분할 정복 — 최대값 찾기와 하노이 탑

```python
def find_max(data: list[int], left: int, right: int) -> int:
    """분할 정복으로 최대값 찾기"""
    if left == right:
        return data[left]

    mid = (left + right) // 2
    left_max = find_max(data, left, mid)
    right_max = find_max(data, mid + 1, right)
    return max(left_max, right_max)

data = [3, 7, 2, 9, 1, 8, 4]
print(find_max(data, 0, len(data) - 1))  # 9


def hanoi(n: int, source: str, target: str, auxiliary: str):
    """하노이 탑 — O(2^n)"""
    if n == 1:
        print(f"원반 1: {source} → {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"원반 {n}: {source} → {target}")
    hanoi(n - 1, auxiliary, target, source)

hanoi(3, "A", "C", "B")
# 원반 1: A → C
# 원반 2: A → B
# 원반 1: C → B
# 원반 3: A → C
# 원반 1: B → A
# 원반 2: B → C
# 원반 1: A → C
```

### Step 5: 재귀 → 반복 변환

```python
# 재귀 팩토리얼 → 반복 팩토리얼
def factorial_iter(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iter(10))  # 3628800


# 재귀 피보나치 → 메모이제이션
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """메모이제이션 피보나치 — O(n)"""
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

print(fibonacci_memo(50))  # 12586269025

# Python 재귀 깊이 제한 확인
import sys
print(f"최대 재귀 깊이: {sys.getrecursionlimit()}")  # 기본 1000
```

## 이 코드에서 주목할 점

- 기저 조건이 없는 재귀는 RecursionError를 일으킵니다. 항상 기저 조건을 먼저 작성합니다
- 분할 정복 거듭제곱은 곱셈 횟수를 O(n)에서 O(log n)으로 줄입니다
- 단순 재귀 피보나치는 O(2^n)이지만, 메모이제이션을 추가하면 O(n)이 됩니다
- Python의 기본 재귀 깊이 제한은 1000입니다. 깊은 재귀는 반복으로 변환하는 것이 안전합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 기저 조건 누락 | 무한 재귀로 RecursionError가 발생합니다 | 기저 조건을 항상 먼저 작성합니다 |
| 재귀 깊이 초과 | Python 기본 제한 1000을 넘깁니다 | 반복문으로 변환하거나 sys.setrecursionlimit을 조정합니다 |
| 중복 계산 | 같은 값을 반복 계산하여 지수 시간이 됩니다 | 메모이제이션이나 DP를 적용합니다 |
| 슬라이싱으로 매번 새 리스트 생성 | 메모리와 시간을 낭비합니다 | 인덱스를 전달합니다 |
| 분할 정복에서 결합 단계 누락 | 부분 결과가 합쳐지지 않습니다 | 분할, 정복, 결합 세 단계를 모두 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 파일 시스템 탐색에서 디렉터리 트리를 재귀적으로 순회합니다
- JSON/XML 같은 중첩 구조를 재귀로 파싱합니다
- 분할 정복으로 대규모 데이터를 병렬 처리합니다 (MapReduce)
- 컴파일러가 AST(추상 구문 트리)를 재귀적으로 평가합니다
- 프랙탈 그래픽이 재귀적 패턴으로 생성됩니다

## 현업 개발자는 이렇게 생각합니다

재귀는 코드를 간결하게 만들지만, 성능과 스택 깊이에 주의해야 합니다. 트리 탐색처럼 구조 자체가 재귀적인 문제에서는 재귀가 자연스럽지만, 단순 반복은 for 루프가 낫습니다.

분할 정복 패턴을 인식하는 능력이 중요합니다. "이 문제를 반으로 나눌 수 있는가?"라는 질문을 습관적으로 하면 효율적인 해법에 더 빨리 도달합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **종료 조건** — base case가 명확하지 않으면 작성 자체를 멈춥니다.
- **스택 한계** — Python 재귀 한도와 메모리 비용을 인지합니다.
- **메모이제이션** — 중복 부분 문제는 lru_cache로 즉시 해결합니다.
- **반복으로 변환** — 병목 경로는 반복으로 풀어 안정성을 확보합니다.
- **분할 비용** — 분할·병합 자체 비용이 무시되지 않는다는 점을 잊지 않습니다.

## 체크리스트

- [ ] 재귀 함수에서 기저 조건의 역할을 설명할 수 있다
- [ ] 호출 스택의 동작 과정을 그려볼 수 있다
- [ ] 분할 정복의 세 단계를 구분할 수 있다
- [ ] 재귀와 반복의 장단점을 비교할 수 있다
- [ ] 메모이제이션으로 중복 계산을 제거할 수 있다

## 연습 문제

1. 리스트를 재귀적으로 뒤집는 함수를 작성하세요.
2. 분할 정복으로 리스트의 합을 구하는 함수를 작성하세요.
3. 하노이 탑에서 원반 4개일 때 최소 이동 횟수와 과정을 출력하세요.

## 정리 및 다음 글 안내

재귀는 함수가 자기 자신을 호출하는 기법이고, 분할 정복은 재귀를 활용해 문제를 체계적으로 쪼개는 전략입니다. 다음 글에서는 재귀의 중복 계산 문제를 해결하는 동적 계획법을 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- **재귀와 분할 정복 (현재 글)**
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Divide-and-Conquer Algorithm](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Real Python — Thinking Recursively in Python](https://realpython.com/python-thinking-recursively/)
- [GeeksforGeeks — Divide and Conquer](https://www.geeksforgeeks.org/divide-and-conquer/)

Tags: Python, 알고리즘, 재귀, 분할 정복, 하노이 탑
