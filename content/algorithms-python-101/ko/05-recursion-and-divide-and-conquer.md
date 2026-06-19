---
series: algorithms-python-101
episode: 5
title: "Algorithms with Python 101 (5/10): 재귀와 분할 정복"
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

# Algorithms with Python 101 (5/10): 재귀와 분할 정복

재귀는 겉으로 보면 단순한데, 실제로 구현할 때는 갑자기 어렵게 느껴지는 개념입니다. 하지만 한 번 감이 잡히면 많은 알고리즘 패턴이 훨씬 일관되게 보이기 시작합니다.

이 글은 Algorithms with Python 101 시리즈의 다섯 번째 글입니다. 여기서는 먼저 재귀를 구체적으로 이해하고, 그다음 분할 정복으로 문제를 푸는 감각을 만들어 보겠습니다.

분할 정복은 그 패턴 가운데에서도 특히 중요합니다. 이진 탐색, 병합 정렬, 퀵 정렬처럼 이미 본 알고리즘들이 모두 이 아이디어 위에 서 있습니다.

![Algorithms with Python 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/05/05-01-big-picture.ko.png)
*Algorithms with Python 101 5장 흐름 개요*

## 이 글에서 다룰 문제

- 재귀 함수는 어떻게 동작하고 호출 스택은 어떤 모양일까요?
- 기저 조건은 왜 그렇게 중요할까요?
- 분할 정복의 세 단계는 어떻게 구분할 수 있을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> 분할 정복은 문제를 더 작은 조각으로 나누고(Divide), 각 조각을 해결하고(Conquer), 결과를 합치는(Combine) 전략입니다.

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

## 재귀 설계의 세 단계

모든 재귀 함수는 아래 세 줄기로 이루어집니다.

```python
def recursive_template(data):
    # 1) 기저 조건 (Base case) — 반드시 먼저!
    if len(data) == 1:
        return data[0]

    # 2) 진행 (Progress) — 입력 크기가 반드시 줄어야 함
    mid = len(data) // 2
    left = recursive_template(data[:mid])
    right = recursive_template(data[mid:])

    # 3) 결합 (Combine) — 부분 결과를 합침
    return max(left, right)
```

이 세 단계 중 하나라도 흐리면 디버깅 난이도가 급격히 올라갑니다.

## 적용 전후 비교

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
    if not data:      # base case
        return 0
    return data[0] + sum_list(data[1:])
```

## 단계별 실습

### 단계 1: 기본 재귀 — 팩토리얼과 피보나치

```python
def factorial(n: int) -> int:
    """Factorial — O(n)."""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800

def fibonacci(n: int) -> int:
    """Fibonacci — O(2^n), 메모이제이션 없이는 비효율적."""
    if n <= 1:  # base case
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # 55
```

팩토리얼은 재귀의 기본 구조를, 피보나치는 중복 계산의 위험성을 보여 줍니다.

### 단계 2: 호출 스택 시각화

```python
def factorial_trace(n: int, depth: int = 0) -> int:
    """Factorial with call stack visualization."""
    indent = "  " * depth
    print(f"{indent}factorial({n}) 호출")

    if n <= 1:
        print(f"{indent}기저 조건: 1 반환")
        return 1

    result = n * factorial_trace(n - 1, depth + 1)
    print(f"{indent}factorial({n}) = {result}")
    return result

factorial_trace(4)
```

실행 출력:

```text
factorial(4) 호출
  factorial(3) 호출
    factorial(2) 호출
      factorial(1) 호출
      기저 조건: 1 반환
    factorial(2) = 2
  factorial(3) = 6
factorial(4) = 24
```

재귀가 어렵게 느껴지는 이유는 "내려가는 호출"과 "올라오는 결과"를 동시에 머릿속에 그려야 하기 때문입니다.

### 단계 3: 분할 정복 — 빠른 거듭제곱

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
```

짝수 지수에서는 `a^n = (a^(n/2))^2`를 이용해 문제 크기를 절반으로 줄입니다.

### 단계 4: 하노이 탑

```python
def hanoi(n: int, source: str, target: str, auxiliary: str) -> None:
    """Tower of Hanoi — O(2^n)."""
    if n == 1:
        print(f"원판 {n}: {source} -> {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"원판 {n}: {source} -> {target}")
    hanoi(n - 1, auxiliary, target, source)

hanoi(3, "A", "C", "B")
```

실행 출력:

```text
원판 1: A -> C
원판 2: A -> B
원판 1: C -> B
원판 3: A -> C
원판 1: B -> A
원판 2: B -> C
원판 1: A -> C
```

### 단계 5: 재귀를 최적화하기

```python
# 반복형 팩토리얼
def factorial_iter(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# 메모이제이션 피보나치
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """Memoized Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

print(fibonacci_memo(50))  # 12586269025

# Python 재귀 깊이 제한
import sys
print(f"Max recursion depth: {sys.getrecursionlimit()}")  # default 1000
```

## 단계별 실행 추적 — 분할 정복 최댓값

`find_max([5, 1, 9, 3])` 실행 추적:

```text
find_max([5, 1, 9, 3])
  └── left: find_max([5, 1])
        ├── left:  find_max([5]) → 5  (기저)
        ├── right: find_max([1]) → 1  (기저)
        └── combine: max(5, 1) = 5
  └── right: find_max([9, 3])
        ├── left:  find_max([9]) → 9  (기저)
        ├── right: find_max([3]) → 3  (기저)
        └── combine: max(9, 3) = 9
  └── combine: max(5, 9) = 9

결과: 9
```

`power(2, 10)` 호출 깊이:

```text
power(2, 10) → 짝수: power(2, 5)^2
  power(2, 5) → 홀수: 2 * power(2, 4)
    power(2, 4) → 짝수: power(2, 2)^2
      power(2, 2) → 짝수: power(2, 1)^2
        power(2, 1) → 홀수: 2 * power(2, 0)
          power(2, 0) → 1  (기저)
        = 2 * 1 = 2
      = 2^2 = 4
    = 4^2 = 16
  = 2 * 16 = 32
= 32^2 = 1024

총 5번 호출 (단순 반복 10번 대비)
```

## 코딩 테스트 풀이 예시

**문제**: 리스트를 재귀적으로 뒤집어라.

```python
def reverse_list(data: list) -> list:
    """
    재귀로 리스트를 뒤집습니다.
    시간 복잡도: O(n), 공간 복잡도: O(n) (호출 스택)
    """
    if len(data) <= 1:  # 기저 조건
        return data[:]
    return [data[-1]] + reverse_list(data[:-1])


print(reverse_list([1, 2, 3, 4, 5]))  # [5, 4, 3, 2, 1]
print(reverse_list([]))               # []
print(reverse_list([42]))             # [42]
```

**문제**: 리스트 합을 분할 정복으로 구하라.

```python
def sum_divide_conquer(data: list[int], left: int, right: int) -> int:
    """
    분할 정복으로 리스트 합을 구합니다.
    시간 복잡도: O(n)
    """
    if left == right:  # 원소 1개: 기저 조건
        return data[left]
    mid = (left + right) // 2
    left_sum = sum_divide_conquer(data, left, mid)
    right_sum = sum_divide_conquer(data, mid + 1, right)
    return left_sum + right_sum  # 결합


data = [1, 2, 3, 4, 5, 6, 7, 8]
print(sum_divide_conquer(data, 0, len(data) - 1))  # 36
```

**문제**: 중첩 리스트를 평탄화하라 (재귀 활용).

```python
def flatten(nested: list) -> list:
    """
    중첩 리스트를 재귀로 평탄화합니다.
    시간 복잡도: O(n) (n = 총 원소 수)
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))  # 재귀 호출
        else:
            result.append(item)
    return result


print(flatten([1, [2, 3], [4, [5, 6]], 7]))  # [1, 2, 3, 4, 5, 6, 7]
print(flatten([]))                            # []
print(flatten([[1, [2]], [3]]))               # [1, 2, 3]
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 기저 조건 누락 | 무한 재귀로 `RecursionError`가 납니다 | 기저 조건을 먼저 작성합니다 |
| 재귀 깊이 초과 | Python 기본 제한(1000)에 걸립니다 | 반복문으로 바꾸거나 `sys.setrecursionlimit`를 검토합니다 |
| 중복 계산 방치 | 같은 값을 반복 계산해 지수 시간이 됩니다 | `@lru_cache` 또는 DP를 사용합니다 |
| 슬라이싱으로 새 리스트 남발 | 메모리와 시간이 추가로 듭니다 | 가능하면 인덱스를 전달합니다 |
| Combine 단계를 잊음 | 부분 결과를 최종 답으로 합치지 못합니다 | Divide, Conquer, Combine 세 단계를 모두 점검합니다 |

## 복잡도 비교표

| 문제 | 단순 접근 | 분할 정복 접근 | 복잡도 차이 |
|------|-----------|---------------|-------------|
| 거듭제곱 `a^n` | `n`번 곱셈 | 지수 절반 분할 | `O(n)` → `O(log n)` |
| 최댓값 찾기 | 선형 순회 | 분할 후 결합 | 둘 다 `O(n)` |
| 정렬 | 버블 정렬 | 병합 정렬 | `O(n^2)` → `O(n log n)` |

## 실무에서는 이렇게 연결됩니다

- 파일 시스템 탐색기는 디렉터리 트리를 재귀적으로 순회합니다.
- 파서는 JSON, XML 같은 중첩 구조를 재귀적으로 처리합니다.
- MapReduce는 큰 데이터를 나누어 병렬 처리하는 분할 정복 사고를 활용합니다.
- 컴파일러는 AST를 재귀적으로 평가합니다.
- 프랙털 그래픽은 재귀 패턴으로 생성됩니다.

## 현업에서는 이렇게 생각합니다

재귀는 코드를 간결하게 만들지만, 성능과 스택 깊이를 항상 함께 봐야 합니다. 트리처럼 본질적으로 재귀적인 구조에는 자연스럽지만, 단순 반복에는 `for` 루프가 더 나은 경우가 많습니다.

더 중요한 가치는 분할 정복 패턴을 알아보는 눈입니다. "이 문제를 반으로 나눌 수 있을까?"라는 질문을 습관처럼 던지면 효율적인 풀이에 더 빨리 도달할 수 있습니다.

## 운영 체크리스트

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
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- **Algorithms with Python 101 (5/10): 재귀와 분할 정복 (현재 글)**
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Python Documentation — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Divide-and-Conquer Algorithm](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Real Python — Thinking Recursively in Python](https://realpython.com/python-thinking-recursively/)
- [GeeksforGeeks — Divide and Conquer](https://www.geeksforgeeks.org/divide-and-conquer/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/05-recursion-and-divide-and-conquer)

Tags: Python, Algorithms, Recursion, Divide and Conquer, Tower of Hanoi
