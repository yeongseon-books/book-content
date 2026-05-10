---
series: functional-programming-101
episode: 7
title: 재귀와 꼬리 호출
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
  - Functional Programming
  - 재귀
  - 꼬리 호출
  - 스택
seo_description: 재귀 함수의 원리, 스택 오버플로우 방지, Python에서의 실용적 재귀 패턴을 다룹니다.
last_reviewed: '2026-05-04'
---

# 재귀와 꼬리 호출

> Functional Programming 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 반복문 없이 자기 자신을 호출하여 문제를 풀 수 있을까요?

> 재귀는 함수가 자기 자신을 호출하여 문제를 작은 하위 문제로 분할하는 기법입니다. 함수형 프로그래밍에서는 상태 변경 없이 반복을 표현하는 핵심 도구입니다. 이 글에서는 재귀의 원리, 꼬리 호출 최적화, Python에서의 실용적 활용법을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 재귀의 기본 구조와 동작 원리
- 기저 조건의 중요성과 스택 오버플로우 방지
- 꼬리 재귀와 Python의 한계
- 재귀를 반복으로 변환하는 패턴

## 왜 중요한가

트리 순회, 분할 정복, 수학적 정의 등 많은 문제는 재귀로 표현하면 자연스럽습니다. 재귀를 이해하면 복잡한 구조를 다루는 알고리즘을 직관적으로 구현할 수 있습니다.

> 재귀 = 문제를 자기 자신의 작은 버전으로 분해

Python은 꼬리 호출 최적화를 지원하지 않으므로 실무에서는 재귀 깊이를 인지하고, 필요하면 반복으로 변환하는 판단이 중요합니다.

## 핵심 개념 잡기

> 재귀 호출의 흐름

```
factorial(4)
  → 4 * factorial(3)
       → 3 * factorial(2)
            → 2 * factorial(1)
                 → 1  (기저 조건)
            ← 2 * 1 = 2
       ← 3 * 2 = 6
  ← 4 * 6 = 24
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 재귀(recursion) | 함수가 자기 자신을 호출하는 기법입니다 |
| 기저 조건(base case) | 재귀를 멈추는 조건입니다 |
| 꼬리 재귀(tail recursion) | 재귀 호출이 함수의 마지막 연산인 형태입니다 |
| 스택 오버플로우(stack overflow) | 재귀 깊이가 한계를 초과하여 발생하는 오류입니다 |
| 분할 정복(divide and conquer) | 문제를 작은 하위 문제로 나누어 해결하는 전략입니다 |

## Before / After

반복문을 재귀로 표현합니다.

```python
# before: 반복문으로 합계 계산
def sum_iterative(numbers: list[int]) -> int:
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_iterative([1, 2, 3, 4, 5]))  # 15
```

```python
# after: 재귀로 합계 계산
def sum_recursive(numbers: list[int]) -> int:
    if not numbers:  # 기저 조건
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

print(sum_recursive([1, 2, 3, 4, 5]))  # 15
```

## 단계별 실습

### Step 1: 기본 재귀 — 팩토리얼

```python
def factorial(n: int) -> int:
    """n! = n * (n-1) * ... * 1"""
    if n <= 1:  # 기저 조건
        return 1
    return n * factorial(n - 1)


print(factorial(5))   # 120
print(factorial(10))  # 3628800

# 호출 과정 시각화
def factorial_verbose(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n <= 1:
        print(f"{indent}→ 1")
        return 1
    result = n * factorial_verbose(n - 1, depth + 1)
    print(f"{indent}→ {result}")
    return result

factorial_verbose(4)
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1)
#       → 1
#     → 2
#   → 6
# → 24
```

### Step 2: 피보나치와 메모이제이션

```python
from functools import lru_cache


# 순수 재귀: O(2^n) — 매우 느림
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# 메모이제이션: O(n) — 중복 계산 제거
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


print(fib_naive(10))  # 55 (느림)
print(fib_memo(100))  # 354224848179261915075 (빠름)

# 캐시 정보 확인
print(fib_memo.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
```

### Step 3: 꼬리 재귀와 Python의 한계

```python
import sys

# 일반 재귀 — 스택 프레임 누적
def factorial_normal(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_normal(n - 1)  # 곱셈이 대기 중

# 꼬리 재귀 — 결과를 인자로 전달
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)  # 마지막 연산이 재귀 호출


# Python은 꼬리 호출 최적화(TCO)를 지원하지 않음
print(sys.getrecursionlimit())  # 기본 1000
print(factorial_tail(900))  # 동작하지만...
# factorial_tail(1500)  # RecursionError!

# 해결: 반복으로 변환
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(10000))  # 문제 없음
```

### Step 4: 트리 순회 — 재귀의 자연스러운 활용

```python
from typing import Any


# 중첩 딕셔너리(트리 구조) 탐색
def flatten_dict(
    d: dict,
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """중첩 딕셔너리를 평탄화합니다."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret",
        },
    },
    "debug": True,
}

flat = flatten_dict(config)
for k, v in flat.items():
    print(f"  {k}: {v}")
# database.host: localhost
# database.port: 5432
# database.credentials.user: admin
# database.credentials.password: secret
# debug: True
```

### Step 5: 재귀를 반복으로 변환

```python
# 재귀 버전: 디렉터리 내 모든 파일 크기 합계 (시뮬레이션)
def total_size_recursive(tree: dict) -> int:
    """중첩 딕셔너리로 표현된 파일 트리의 크기 합계입니다."""
    total = 0
    for name, value in tree.items():
        if isinstance(value, dict):
            total += total_size_recursive(value)
        else:
            total += value
    return total


# 반복 버전: 스택을 명시적으로 관리
def total_size_iterative(tree: dict) -> int:
    total = 0
    stack = [tree]
    while stack:
        current = stack.pop()
        for name, value in current.items():
            if isinstance(value, dict):
                stack.append(value)
            else:
                total += value
    return total


file_tree = {
    "src": {
        "main.py": 1200,
        "utils": {
            "helpers.py": 800,
            "config.py": 400,
        },
    },
    "README.md": 300,
    "tests": {
        "test_main.py": 600,
    },
}

print(total_size_recursive(file_tree))  # 3300
print(total_size_iterative(file_tree))  # 3300
```

## 이 코드에서 주목할 점

- 모든 재귀에는 반드시 기저 조건이 필요합니다
- `@lru_cache`는 중복 호출을 제거하여 재귀 성능을 극적으로 개선합니다
- Python은 꼬리 호출 최적화를 지원하지 않으므로 깊은 재귀는 반복으로 변환합니다
- 트리 구조 순회는 재귀가 가장 자연스러운 표현입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 기저 조건 누락 | 무한 재귀 → 스택 오버플로우가 발생합니다 | 먼저 기저 조건을 작성합니다 |
| 깊은 재귀 사용 | Python의 기본 한도는 1000입니다 | 깊이가 깊으면 반복으로 변환합니다 |
| 메모이제이션 누락 | 지수 시간 복잡도가 됩니다 | `@lru_cache`를 적용합니다 |
| 매번 리스트 슬라이싱 | O(n) 복사가 매 호출마다 발생합니다 | 인덱스를 인자로 전달합니다 |
| 꼬리 재귀에 의존 | Python에서는 최적화되지 않습니다 | 반복문을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- JSON 파싱 결과의 중첩 구조를 재귀로 탐색합니다
- 파일 시스템 트리 순회에 재귀를 사용합니다
- 분할 정복 알고리즘(퀵소트, 머지소트)에서 활용합니다
- AST(추상 구문 트리) 처리에 재귀 패턴이 필수적입니다
- 깊이 제한이 있는 경우 명시적 스택으로 변환합니다

## 현업 개발자는 이렇게 생각합니다

재귀는 트리, 그래프, 중첩 구조를 다룰 때 가장 자연스러운 도구입니다. 하지만 Python에서는 재귀 깊이 한도(기본 1000)를 항상 인지해야 합니다. 실무에서 깊이가 불확실한 재귀는 반복으로 변환하는 것이 안전합니다.

"재귀 vs 반복"은 가독성과 안전성의 트레이드오프입니다. 깊이가 얕고(수십 단계) 구조가 재귀적인 문제는 재귀로, 깊이가 깊거나 불확실한 경우는 반복으로 작성하는 것이 실용적인 판단입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **재귀 한도** — Python은 꼬리 재귀 최적화가 없다는 점을 잊지 않습니다.
- **반복 변환** — 성능·안정성이 필요하면 반복으로 풀어 둡니다.
- **memoization** — lru_cache로 중복 호출을 즉시 제거합니다.
- **스택 추적** — 예외 추적이 길어지므로 핵심 로직을 분리합니다.
- **기저 사례** — 기저 사례 명확성이 곧 정합성입니다.

## 체크리스트

- [ ] 재귀 함수의 기저 조건을 올바르게 설정할 수 있다
- [ ] 재귀 호출의 스택 프레임 축적을 이해하고 있다
- [ ] `@lru_cache`로 재귀 성능을 개선할 수 있다
- [ ] 재귀를 명시적 스택을 사용한 반복으로 변환할 수 있다
- [ ] 재귀와 반복의 선택 기준을 설명할 수 있다

## 연습 문제

1. 이진 탐색을 재귀 버전과 반복 버전 두 가지로 구현하세요.
2. 중첩 리스트 `[1, [2, [3, 4], 5], 6]`을 평탄화하는 재귀 함수를 작성하세요.
3. `@lru_cache`를 사용하지 않고 딕셔너리로 메모이제이션을 직접 구현하세요.

## 정리 및 다음 글 안내

재귀는 문제를 자기 자신의 작은 버전으로 분해하는 기법입니다. Python에서는 꼬리 호출 최적화가 없으므로 깊이를 인지하고 필요하면 반복으로 변환해야 합니다. 다음 글에서는 필요할 때만 계산하는 **지연 평가와 제너레이터**를 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- **재귀와 꼬리 호출 (현재 글)**
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — sys.setrecursionlimit](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Real Python — Recursion in Python](https://realpython.com/python-recursion/)
- [Python 공식 문서 — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [The Little Schemer — Daniel P. Friedman](https://mitpress.mit.edu/9780262560993/the-little-schemer/)

Tags: Python, Functional Programming, 재귀, 꼬리 호출, 스택
