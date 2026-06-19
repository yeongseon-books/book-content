---
series: functional-programming-101
episode: 7
title: "Functional Programming 101 (7/10): 재귀와 꼬리 호출"
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
  - Functional Programming
  - 재귀
  - 꼬리 호출
  - 스택
seo_description: 재귀의 종료 조건 설계와 메모이제이션을 학습하고, Python 스택 한계를 고려해 반복으로 전환하거나 트리 탐색에 적용하는 기준을 제시합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (7/10): 재귀와 꼬리 호출

재귀는 반복문 없이 문제를 풀게 해 주는 기법이지만, 단순히 "함수가 자기 자신을 다시 부른다" 정도로만 이해하면 실무에서는 금방 한계를 만납니다. 중요한 것은 언제 재귀가 구조를 더 잘 드러내는지, 그리고 Python에서는 어디서부터 반복으로 바꿔야 하는지를 아는 것입니다.

이 글은 Functional Programming 101 시리즈의 7번째 글입니다.

특히 Python은 꼬리 호출 최적화(TCO)를 지원하지 않습니다. 그래서 함수형 언어에서 자연스럽게 쓰는 재귀 패턴도 Python에서는 깊이에 따라 위험해질 수 있습니다. 이 차이를 이해해야 재귀를 예쁘기만 한 코드가 아니라 안전한 도구로 사용할 수 있습니다.

![Functional Programming 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/07/07-01-big-picture.ko.png)
*Functional Programming 101 7장 흐름 개요*

## 이 글에서 다룰 문제

- 재귀 함수는 어떤 구조를 가져야 안전하게 동작할까요?
- base case는 왜 항상 먼저 생각해야 할까요?
- Python에서 꼬리 재귀는 왜 이론만큼 실용적이지 않을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

트리 순회, 분할 정복, 중첩 구조 해제, 수학적 정의 같은 문제는 재귀로 표현할 때 가장 자연스럽습니다. 반복문으로도 풀 수는 있지만, 문제 구조 자체가 사라져 코드가 오히려 덜 읽힐 수 있습니다.

하지만 Python에서는 재귀 깊이 한계가 기본 1000이기 때문에, 구조가 재귀적이라는 이유만으로 무조건 재귀를 택하면 안 됩니다. 읽기 쉬움과 실행 안전성 사이에서 균형을 잡는 것이 실무 감각입니다.

## 개념 개요

> 재귀를 읽을 때는 내려가는 과정보다 base case에 도달한 뒤 값이 어떻게 되돌아오는지를 보는 것이 중요합니다.

```text
factorial(4)
  -> 4 * factorial(3)
       -> 3 * factorial(2)
            -> 2 * factorial(1)
                 -> 1  (base case)
            <- 2 * 1 = 2
       <- 3 * 2 = 6
  <- 4 * 6 = 24
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 재귀(recursion) | 함수가 자기 자신을 다시 호출하는 기법입니다 |
| base case | 재귀를 멈추는 종료 조건입니다 |
| 꼬리 재귀(tail recursion) | 함수의 마지막 연산이 재귀 호출인 형태입니다 |
| 스택 오버플로우(stack overflow) | 재귀 깊이가 한계를 넘어서 발생하는 오류입니다 |
| 분할 정복(divide and conquer) | 문제를 더 작은 하위 문제로 나누어 푸는 전략입니다 |

## 적용 전후 비교

반복문의 누적 합도 재귀로 표현할 수 있습니다. 다만 그 표현이 실제로 더 적절한지는 별도의 판단이 필요합니다.

```python
# 이전: 반복문 기반 합계
def sum_iterative(numbers: list[int]) -> int:
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_iterative([1, 2, 3, 4, 5]))  # 15
```

```python
# 이후: 재귀 기반 합계
def sum_recursive(numbers: list[int]) -> int:
    if not numbers:  # base case
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

print(sum_recursive([1, 2, 3, 4, 5]))  # 15
# 주의: 큰 리스트에는 적합하지 않음 — 반복 버전이 더 안전
```

## 단계별 실습

### 단계 1: 기본 재귀 — 팩토리얼

```python
def factorial(n: int) -> int:
    """n! = n * (n-1) * ... * 1"""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800

# call stack 시각화
def factorial_verbose(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n <= 1:
        print(f"{indent}-> 1")
        return 1
    result = n * factorial_verbose(n - 1, depth + 1)
    print(f"{indent}-> {result}")
    return result

factorial_verbose(4)
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1)
#       -> 1
#     -> 2
#   -> 6
# -> 24
```

재귀를 이해하는 가장 좋은 방법은 호출 스택을 눈으로 따라가는 것입니다. base case가 왜 중요한지, 반환값이 어떻게 쌓여 올라오는지가 바로 보입니다.

### 단계 2: 피보나치와 메모이제이션

```python
from functools import lru_cache

# 단순 재귀: O(2^n) — 매우 느림
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# memoization: O(n) — 중복 계산 제거
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_naive(10))  # 55 (slow)
print(fib_memo(100))  # 354224848179261915075 (fast)

# cache 통계 확인
print(fib_memo.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)

# map으로 피보나치 수열 생성
fib_sequence = list(map(fib_memo, range(10)))
print(fib_sequence)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

재귀가 느린 것이 아니라, 같은 하위 문제를 중복 계산하는 재귀가 느린 것입니다. 이 차이를 이해하면 메모이제이션이 왜 강력한지 바로 연결됩니다.

### 단계 3: 꼬리 재귀와 Python의 한계

```python
import sys

# 일반 재귀 — stack frame이 누적됨
def factorial_normal(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_normal(n - 1)  # multiplication is pending

# 꼬리 재귀 — 결과를 인자로 전달
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)  # last operation is the recursive call

# Python은 tail call optimization(TCO)을 지원하지 않음
print(sys.getrecursionlimit())  # default 1000
print(factorial_tail(900))      # works
# factorial_tail(1500)  # RecursionError!

# 해결 방법: 반복문으로 변환
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(10000))  # no problem
```

많은 입문자가 여기서 한 번 헷갈립니다. 꼬리 재귀는 이론적으로 스택을 줄일 수 있는 형태이지만, Python 런타임이 그 최적화를 해 주지 않기 때문에 깊이가 깊어지면 결국 반복이 더 안전합니다.

### 단계 4: 트리 순회와 재귀의 궁합

```python
from typing import Any

# 중첩 dict(tree 구조) 순회
def flatten_dict(
    d: dict,
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """Flattens a nested dictionary."""
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

중첩 딕셔너리, 트리, AST처럼 구조 자체가 재귀적일 때는 재귀가 문제 도메인을 가장 직접적으로 반영합니다.

### 단계 5: 재귀를 반복으로 바꾸기

```python
# 재귀 버전: 모의 파일 트리의 전체 크기
def total_size_recursive(tree: dict) -> int:
    """Total size of a file tree represented as nested dicts."""
    total = 0
    for name, value in tree.items():
        if isinstance(value, dict):
            total += total_size_recursive(value)
        else:
            total += value
    return total

# 반복 버전: 명시적 stack 관리
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

실무에서는 이 전환이 매우 중요합니다. 구조는 재귀적으로 이해하되, 실행은 명시적 스택으로 바꿔 안정성을 확보하는 경우가 많습니다.

### 단계 6: 재귀와 map/filter 조합

```python
from functools import lru_cache

# 재귀로 모든 중첩 리스트를 평탄화
def flatten(lst: list) -> list:
    """Recursively flattens a nested list."""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

nested = [1, [2, [3, 4], 5], [6, 7], 8]
flat = flatten(nested)
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8]

# 평탄화 후 filter와 map 적용
evens = list(filter(lambda x: x % 2 == 0, flat))
doubled = list(map(lambda x: x * 2, evens))
print(evens)    # [2, 4, 6, 8]
print(doubled)  # [4, 8, 12, 16]
```

## 이 코드에서 주목할 점

- 모든 재귀에는 반드시 base case가 있어야 합니다.
- `@lru_cache`는 중복 호출을 제거해 재귀 성능을 크게 개선합니다.
- Python은 꼬리 호출 최적화를 지원하지 않으므로 깊은 재귀는 반복으로 바꾸는 편이 안전합니다.
- 재귀로 평탄화한 결과에 `map`/`filter`를 조합하면 강력한 파이프라인이 됩니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| base case를 빼먹음 | 무한 재귀로 스택 오버플로우가 납니다 | 종료 조건을 먼저 작성합니다 |
| 깊은 재귀를 그대로 사용함 | Python 기본 한계를 쉽게 넘깁니다 | 깊이가 크면 반복으로 전환합니다 |
| 메모이제이션 없이 중복 계산함 | 시간 복잡도가 폭증합니다 | `@lru_cache`를 적용합니다 |
| 매 호출마다 리스트 슬라이싱을 함 | 호출마다 O(n) 복사가 생깁니다 | 인덱스를 인자로 넘기는 방식을 고려합니다 |
| 꼬리 재귀면 안전하다고 믿음 | Python은 TCO를 하지 않습니다 | 반복문으로 바꿉니다 |

## 실무에서 이렇게 쓰입니다

- 파싱한 JSON의 중첩 구조를 재귀로 순회합니다.
- 파일 시스템 트리 탐색 로직을 재귀적으로 표현합니다.
- 퀵정렬, 병합정렬 같은 분할 정복 알고리즘에 적용합니다.
- AST 처리에서 재귀 패턴을 사용합니다.
- 깊이가 불확실하면 명시적 스택 기반 반복으로 바꿉니다.

## 현업에서는 이렇게 판단합니다

재귀는 트리, 그래프, 중첩 구조를 설명하는 가장 자연스러운 도구입니다. 하지만 Python에서는 언제나 재귀 깊이 제한을 먼저 떠올려야 합니다. 깊이가 얕고 구조 표현이 중요한 경우에만 재귀를 그대로 유지하고, 깊이가 크거나 입력이 불확실하면 반복으로 전환하는 편이 안전합니다.

결국 재귀와 반복의 선택은 우아함과 안정성의 균형입니다. 구조를 드러내는 데 재귀가 압도적으로 좋다면 쓰되, 운영 환경에서 스택 리스크가 생기면 주저 없이 명시적 스택으로 옮기는 것이 실전적인 판단입니다.

## 처음 질문으로 돌아가기

- **재귀 함수는 어떤 구조를 가져야 안전하게 동작할까요?**
  두 가지가 반드시 있어야 합니다. 첫째, 재귀를 멈추는 base case입니다. base case가 없으면 무한 재귀로 `RecursionError`가 납니다. 둘째, 재귀 호출마다 입력이 base case에 가까워지는 방향성입니다. `factorial(n)`이 `factorial(n-1)`을 부르는 것처럼, 문제 크기가 단조롭게 줄어야 합니다.

- **base case는 왜 항상 먼저 생각해야 할까요?**
  재귀 함수를 설계할 때 "가장 작은 입력에서 답은 무엇인가"를 먼저 잡으면 전체 구조가 저절로 따라옵니다. `factorial(0) = 1`, `sum([]) = 0`처럼 base case를 먼저 결정하면 재귀 케이스에서 "이 base case로 수렴하는가"만 확인하면 됩니다. 반대로 재귀 케이스부터 쓰면 종료 조건을 나중에 끼워 맞추게 됩니다.

- **Python에서 꼬리 재귀는 왜 이론만큼 실용적이지 않을까요?**
  꼬리 재귀 최적화(TCO)는 컴파일러나 런타임이 마지막 재귀 호출을 반복문으로 변환해 스택 프레임을 재사용하는 최적화입니다. Python 인터프리터는 이 최적화를 의도적으로 지원하지 않습니다(Guido van Rossum의 결정). 그래서 꼬리 재귀 형태로 작성해도 스택은 똑같이 쌓입니다. 깊이 제한에 걸릴 것 같으면 반복문으로 직접 변환하는 것이 유일한 안전한 방법입니다.

## 운영 체크리스트

- [ ] 재귀 함수의 올바른 base case를 설정할 수 있다
- [ ] 재귀 호출에서 스택 프레임이 어떻게 쌓이는지 설명할 수 있다
- [ ] `@lru_cache`로 재귀 성능을 개선할 수 있다
- [ ] 명시적 스택을 사용해 재귀를 반복으로 바꿀 수 있다
- [ ] 재귀와 반복 중 무엇을 택할지 기준을 설명할 수 있다

## 연습 문제

1. 이진 탐색을 재귀 버전과 반복 버전으로 각각 구현해 보세요.
2. 중첩 리스트 `[1, [2, [3, 4], 5], 6]`를 평탄화하는 재귀 함수를 작성하고 결과에 `map`으로 제곱을 적용해 보세요.
3. `@lru_cache` 대신 dict를 직접 사용해 메모이제이션을 구현해 보세요.

## 정리와 다음 글

재귀는 문제를 더 작은 같은 문제로 분해해 푸는 방식입니다. 다만 Python은 꼬리 호출 최적화를 지원하지 않으므로 깊이 제한을 항상 염두에 두어야 합니다. 다음 글에서는 값이 정말 필요해질 때까지 계산을 미루는 **지연 평가와 제너레이터**를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- **Functional Programming 101 (7/10): 재귀와 꼬리 호출 (현재 글)**
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [Functional Programming 101 (9/10): 함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — sys.setrecursionlimit](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Real Python — Recursion in Python](https://realpython.com/python-recursion/)
- [Python 공식 문서 — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [The Little Schemer — Daniel P. Friedman](https://mitpress.mit.edu/9780262560993/the-little-schemer/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 재귀, 꼬리 호출, 스택
