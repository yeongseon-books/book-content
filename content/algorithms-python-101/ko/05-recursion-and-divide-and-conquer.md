---
series: algorithms-python-101
episode: 5
title: 재귀와 분할 정복
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Recursion
  - Divide and Conquer
  - Tower of Hanoi
seo_description: 재귀 함수의 동작 원리와 기저 조건의 중요성을 호출 스택 시각화로 이해합니다. 문제를 쪼개어 해결하는 분할 정복 전략을 파이썬 예제로 배웁니다.
last_reviewed: '2026-05-12'
---

# 재귀와 분할 정복

재귀는 겉으로 보면 단순한데, 실제로 구현할 때는 갑자기 어렵게 느껴지는 개념입니다. 하지만 한 번 감이 잡히면 많은 알고리즘 패턴이 훨씬 일관되게 보이기 시작합니다. 이 글은 Algorithms with Python 101 시리즈의 다섯 번째 글입니다. 여기서는 먼저 재귀를 구체적으로 이해하고, 그다음 분할 정복으로 문제를 푸는 감각을 만들어 보겠습니다.

분할 정복은 그 패턴 가운데에서도 특히 중요합니다. 이진 탐색, 병합 정렬, 퀵 정렬처럼 이미 본 알고리즘들이 모두 이 아이디어 위에 서 있습니다.

## 이 글에서 다룰 문제

- 재귀 함수는 어떻게 동작하고 호출 스택은 어떤 모양일까요?
- 기저 조건은 왜 그렇게 중요할까요?
- 분할 정복의 세 단계는 어떻게 구분할 수 있을까요?
- 재귀를 반복문으로 바꾸는 이유와 메모이제이션의 가치는 무엇일까요?

## 왜 중요한가

재귀는 트리 순회, 그래프 순회, 정렬, 동적 계획법의 기반입니다. 재귀를 이해하지 못하면 이후 알고리즘 주제들이 갑자기 훨씬 불투명해집니다.

> 분할 정복은 문제를 더 작은 조각으로 나누고(Divide), 각 조각을 해결하고(Conquer), 결과를 합치는(Combine) 전략입니다.

병합 정렬, 퀵 정렬, 이진 탐색을 하나의 패턴으로 묶어 이해할 수 있다는 점이 중요합니다. 새로운 문제를 봐도 "쪼개서 풀 수 있는가"를 먼저 떠올릴 수 있게 됩니다.

## 개념 한눈에 보기

> 재귀 = 함수가 자기 자신을 다시 호출해 반복 작업을 처리하는 방식

```text
factorial(4) call trace:
factorial(4) → 4 × factorial(3)
               → 3 × factorial(2)
                    → 2 × factorial(1)
                         → 1 (base case)
                    ← 2 × 1 = 2
               ← 3 × 2 = 6
          ← 4 × 6 = 24
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Recursion | 함수가 자기 자신을 호출하는 프로그래밍 기법입니다 |
| Base case | 재귀 호출을 멈추게 하는 종료 조건입니다 |
| Call stack | 재귀 호출이 쌓이는 실행 문맥의 스택입니다 |
| Divide and conquer | 문제를 나누고, 풀고, 합치는 전략입니다 |
| Tail recursion | 마지막 연산이 재귀 호출인 형태입니다 |

## Before / After

리스트 합계를 구하는 두 가지 방법입니다.

```python
# before: iterative
def sum_list(data):
    total = 0
    for x in data:
        total += x
    return total
```

```python
# after: recursive
def sum_list(data):
    if not data:
        return 0
    return data[0] + sum_list(data[1:])
```

## 단계별 실습

### Step 1: Basic Recursion — Factorial and Fibonacci

```python
def factorial(n: int) -> int:
    """Factorial — O(n)."""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800


def fibonacci(n: int) -> int:
    """Fibonacci — O(2^n), inefficient."""
    if n <= 1:  # base case
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # 55
```

팩토리얼은 재귀의 기본 구조를 보여 주고, 피보나치는 재귀만으로는 중복 계산이 얼마나 쉽게 폭증하는지를 보여 줍니다.

### Step 2: Visualizing the Call Stack

```python
def factorial_trace(n: int, depth: int = 0) -> int:
    """Factorial with call stack visualization."""
    indent = "  " * depth
    print(f"{indent}factorial({n}) called")

    if n <= 1:
        print(f"{indent}base case: return 1")
        return 1

    result = n * factorial_trace(n - 1, depth + 1)
    print(f"{indent}factorial({n}) = {result}")
    return result

factorial_trace(4)
# factorial(4) called
#   factorial(3) called
#     factorial(2) called
#       factorial(1) called
#       base case: return 1
#     factorial(2) = 2
#   factorial(3) = 6
# factorial(4) = 24
```

재귀가 어렵게 느껴지는 이유는 호출이 내려가는 과정과 결과가 올라오는 과정을 동시에 머릿속에 그려야 하기 때문입니다. 호출 스택을 출력해 보면 그 흐름이 훨씬 선명해집니다.

### Step 3: Divide and Conquer — Fast Exponentiation

```python
def power(base: int, exp: int) -> int:
    """Divide-and-conquer exponentiation — O(log n)."""
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    return base * power(base, exp - 1)

print(power(2, 10))   # 1024
print(power(3, 5))    # 243

# Comparison: naive approach is O(n), D&C is O(log n)
# Computing 2^1000 takes ~1000 vs ~10 multiplications
```

문제를 반씩 줄이면 반복 횟수가 크게 줄어든다는 점을 잘 보여 주는 예시입니다. 분할 정복이 단순한 설명이 아니라 실제 성능 개선으로 이어진다는 사실이 중요합니다.

### Step 4: Divide and Conquer — Find Max and Tower of Hanoi

```python
def find_max(data: list[int], left: int, right: int) -> int:
    """Find maximum using divide and conquer."""
    if left == right:
        return data[left]
    mid = (left + right) // 2
    left_max = find_max(data, left, mid)
    right_max = find_max(data, mid + 1, right)
    return max(left_max, right_max)

data = [3, 7, 2, 9, 1, 8, 4]
print(find_max(data, 0, len(data) - 1))  # 9


def hanoi(n: int, source: str, target: str, auxiliary: str):
    """Tower of Hanoi — O(2^n)."""
    if n == 1:
        print(f"Disk 1: {source} -> {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"Disk {n}: {source} -> {target}")
    hanoi(n - 1, auxiliary, target, source)

hanoi(3, "A", "C", "B")
# Disk 1: A -> C
# Disk 2: A -> B
# Disk 1: C -> B
# Disk 3: A -> C
# Disk 1: B -> A
# Disk 2: B -> C
# Disk 1: A -> C
```

하노이 탑은 재귀 구조를 이해하기에 아주 좋은 문제입니다. 작은 문제를 먼저 해결해야 큰 문제를 풀 수 있다는 분할 정복 감각도 분명하게 드러납니다.

### Step 5: Converting Recursion to Iteration

```python
# Recursive factorial → iterative factorial
def factorial_iter(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iter(10))  # 3628800


# Recursive fibonacci → memoized fibonacci
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """Memoized Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

print(fibonacci_memo(50))  # 12586269025

# Python recursion depth limit
import sys
print(f"Max recursion depth: {sys.getrecursionlimit()}")  # default 1000
```

재귀가 항상 최선은 아닙니다. 스택 깊이 제한이나 중복 계산 때문에 반복문이나 메모이제이션으로 바꾸는 편이 더 나은 경우가 많습니다.

## 이 코드에서 먼저 봐야 할 점

- 기저 조건이 없는 재귀 함수는 `RecursionError`를 일으킵니다. 항상 기저 조건부터 먼저 써야 합니다.
- 분할 정복 거듭제곱은 곱셈 횟수를 `O(n)`에서 `O(log n)`으로 줄입니다.
- 순진한 재귀 피보나치는 `O(2^n)`이지만, 메모이제이션을 추가하면 `O(n)`이 됩니다.
- Python의 기본 재귀 깊이 제한은 1000입니다. 깊은 재귀는 반복문으로 바꾸는 편이 안전합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 기저 조건 누락 | 무한 재귀로 `RecursionError`가 납니다 | 기저 조건을 먼저 작성합니다 |
| 재귀 깊이 초과 | Python 기본 제한에 걸립니다 | 반복문으로 바꾸거나 `sys.setrecursionlimit`를 검토합니다 |
| 중복 계산 방치 | 같은 값을 반복 계산해 지수 시간이 됩니다 | 메모이제이션이나 DP를 사용합니다 |
| 슬라이싱으로 새 리스트 남발 | 메모리와 시간이 추가로 듭니다 | 가능하면 인덱스를 전달합니다 |
| Combine 단계를 잊음 | 부분 결과를 최종 답으로 합치지 못합니다 | Divide, Conquer, Combine 세 단계를 모두 점검합니다 |

## 실무에서는 이렇게 연결됩니다

- 파일 시스템 탐색기는 디렉터리 트리를 재귀적으로 순회합니다.
- 파서는 JSON, XML 같은 중첩 구조를 재귀적으로 처리합니다.
- MapReduce는 큰 데이터를 나누어 병렬 처리하는 분할 정복 사고를 활용합니다.
- 컴파일러는 AST를 재귀적으로 평가합니다.
- 프랙털 그래픽은 재귀 패턴으로 생성됩니다.

## 현업에서는 이렇게 생각합니다

재귀는 코드를 간결하게 만들지만, 성능과 스택 깊이를 항상 함께 봐야 합니다. 트리처럼 본질적으로 재귀적인 구조에는 자연스럽지만, 단순 반복에는 `for` 루프가 더 나은 경우가 많습니다.

더 중요한 가치는 분할 정복 패턴을 알아보는 눈입니다. "이 문제를 반으로 나눌 수 있을까?"라는 질문을 습관처럼 던지면 효율적인 풀이에 더 빨리 도달할 수 있습니다.

## 체크리스트

- [ ] 재귀 함수에서 기저 조건의 역할을 설명할 수 있습니다
- [ ] 간단한 재귀 함수의 호출 스택을 추적할 수 있습니다
- [ ] 분할 정복의 세 단계를 구분할 수 있습니다
- [ ] 재귀와 반복문의 장단점을 비교할 수 있습니다
- [ ] 메모이제이션으로 중복 계산을 제거할 수 있습니다

## 연습 문제

1. 리스트를 재귀적으로 뒤집는 함수를 작성해 보세요.
2. 리스트의 합을 분할 정복 방식으로 구하는 함수를 작성해 보세요.
3. 디스크 4개짜리 하노이 탑의 최소 이동 횟수와 전체 이동 순서를 출력해 보세요.

## 정리와 다음 글

재귀는 함수가 자기 자신을 호출하는 기법이고, 분할 정복은 그 재귀를 이용해 문제를 체계적으로 쪼개는 전략입니다. 다음 글에서는 중복 계산을 본격적으로 줄이는 도구인 동적 계획법을 다룹니다.

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

- [Python Documentation — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Divide-and-Conquer Algorithm](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Real Python — Thinking Recursively in Python](https://realpython.com/python-thinking-recursively/)
- [GeeksforGeeks — Divide and Conquer](https://www.geeksforgeeks.org/divide-and-conquer/)

Tags: Python, Algorithms, Recursion, Divide and Conquer, Tower of Hanoi
