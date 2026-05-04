---
series: functional-programming-101
episode: 4
title: 고차 함수
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
  - 고차 함수
  - 콜백
  - 데코레이터
seo_description: 함수를 인자로 받고 반환하는 고차 함수의 원리와 Python 활용법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 고차 함수

> Functional Programming 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 함수를 다른 함수의 인자로 전달하거나, 함수를 반환하는 것이 왜 강력할까요?

> 고차 함수는 함수를 인자로 받거나 함수를 반환하는 함수입니다. 이 패턴으로 동작을 추상화하고, 중복을 제거하며, 유연한 코드를 작성할 수 있습니다. 이 글에서는 고차 함수의 원리와 Python에서의 실용적 활용을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 고차 함수의 정의와 동작 원리
- `sorted`, `map`, `filter`에서 고차 함수 활용
- 함수를 반환하는 팩토리 패턴
- 데코레이터의 고차 함수 본질

## 왜 중요한가

반복되는 패턴을 함수로 추출할 때 "동작 자체"가 달라지는 경우가 있습니다. 고차 함수는 동작을 인자로 전달하여 코드 중복을 제거하고, 전략 패턴을 클래스 없이 구현합니다.

> 고차 함수 = 동작을 데이터처럼 다루는 도구

Python의 `sorted(key=...)`, `map(func, ...)`, 데코레이터 모두 고차 함수입니다. 이미 사용하고 있지만 원리를 이해하면 더 강력하게 활용할 수 있습니다.

## 핵심 개념 잡기

> 고차 함수의 두 가지 형태

```
형태 1: 함수를 인자로 받음      형태 2: 함수를 반환
─────────────────────          ─────────────────
sorted(data, key=func)         def make_adder(n):
map(func, data)                    return lambda x: x + n
filter(func, data)             adder = make_adder(5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 고차 함수(higher-order function) | 함수를 인자로 받거나 함수를 반환하는 함수입니다 |
| 콜백(callback) | 다른 함수에 인자로 전달되는 함수입니다 |
| 일급 객체(first-class object) | 변수 할당, 인자 전달, 반환이 가능한 객체입니다 |
| 팩토리 함수(factory function) | 새로운 함수나 객체를 생성하여 반환하는 함수입니다 |
| 데코레이터(decorator) | 함수를 받아 기능을 추가한 새 함수를 반환하는 고차 함수입니다 |

## Before / After

중복 코드를 고차 함수로 제거합니다.

```python
# before: 로직이 거의 같은 함수 세 개
def get_adults(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 18:
            result.append(p)
    return result

def get_seniors(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 65:
            result.append(p)
    return result
```

```python
# after: 고차 함수로 조건을 인자로 전달
from typing import Callable

def filter_people(
    people: list[dict],
    predicate: Callable[[dict], bool],
) -> list[dict]:
    return [p for p in people if predicate(p)]

adults = filter_people(people, lambda p: p["age"] >= 18)
seniors = filter_people(people, lambda p: p["age"] >= 65)
```

## 단계별 실습

### Step 1: 함수를 인자로 전달

```python
from typing import Callable


def apply_operation(
    values: list[int],
    operation: Callable[[int], int],
) -> list[int]:
    return [operation(v) for v in values]


numbers = [1, 2, 3, 4, 5]

doubled = apply_operation(numbers, lambda x: x * 2)
print(doubled)  # [2, 4, 6, 8, 10]

squared = apply_operation(numbers, lambda x: x ** 2)
print(squared)  # [1, 4, 9, 16, 25]

def negate(x: int) -> int:
    return -x

negated = apply_operation(numbers, negate)
print(negated)  # [-1, -2, -3, -4, -5]
```

### Step 2: sorted의 key 파라미터

```python
from dataclasses import dataclass


@dataclass
class Student:
    name: str
    score: int
    grade: int


students = [
    Student("Alice", 85, 3),
    Student("Bob", 92, 2),
    Student("Charlie", 78, 3),
    Student("Diana", 95, 1),
]

# 점수순 정렬
by_score = sorted(students, key=lambda s: s.score, reverse=True)
for s in by_score:
    print(f"{s.name}: {s.score}")
# Diana: 95
# Bob: 92
# Alice: 85
# Charlie: 78

# 학년순 → 점수순 다중 정렬
by_grade_score = sorted(students, key=lambda s: (s.grade, -s.score))
for s in by_grade_score:
    print(f"  {s.grade}학년 {s.name}: {s.score}")
#   1학년 Diana: 95
#   2학년 Bob: 92
#   3학년 Alice: 85
#   3학년 Charlie: 78
```

### Step 3: 함수를 반환하는 팩토리

```python
from typing import Callable


def make_multiplier(factor: int) -> Callable[[int], int]:
    """곱셈 함수를 생성합니다."""
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

def make_validator(min_val: float, max_val: float) -> Callable[[float], bool]:
    """범위 검증 함수를 생성합니다."""
    def validate(value: float) -> bool:
        return min_val <= value <= max_val
    return validate


double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15

is_valid_score = make_validator(0, 100)
is_valid_rate = make_validator(0.0, 1.0)
print(is_valid_score(85))   # True
print(is_valid_score(150))  # False
print(is_valid_rate(0.75))  # True
```

### Step 4: 데코레이터 — 고차 함수의 문법적 설탕

```python
import time
from typing import Callable, Any
from functools import wraps


def timer(func: Callable) -> Callable:
    """실행 시간을 측정하는 데코레이터입니다."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper

def retry(max_attempts: int) -> Callable:
    """재시도 데코레이터를 생성합니다."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"  시도 {attempt} 실패: {e}")
            return None
        return wrapper
    return decorator


@timer
def slow_sum(n: int) -> int:
    return sum(range(n))

@retry(max_attempts=3)
def unstable_operation() -> str:
    import random
    if random.random() < 0.7:
        raise ValueError("일시적 오류")
    return "성공"


result = slow_sum(1_000_000)
print(f"결과: {result}")
# slow_sum: 0.0234초
# 결과: 499999500000
```

### Step 5: 고차 함수로 파이프라인 구성

```python
from typing import Callable, TypeVar

T = TypeVar("T")


def compose(*funcs: Callable) -> Callable:
    """함수를 오른쪽에서 왼쪽으로 합성합니다."""
    def composed(value):
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result
    return composed


def strip_whitespace(text: str) -> str:
    return text.strip()

def to_lower(text: str) -> str:
    return text.lower()

def replace_spaces(text: str) -> str:
    return text.replace(" ", "-")

def truncate_20(text: str) -> str:
    return text[:20]


slugify = compose(truncate_20, replace_spaces, to_lower, strip_whitespace)

print(slugify("  Hello World Python  "))  # hello-world-python
print(slugify("  Functional Programming Guide  "))  # functional-programmi
```

## 이 코드에서 주목할 점

- 고차 함수는 동작을 인자로 전달하여 코드 중복을 제거합니다
- 팩토리 함수는 설정이 다른 여러 함수를 동적으로 생성합니다
- 데코레이터는 고차 함수의 문법적 설탕이며 `@wraps`로 메타데이터를 보존합니다
- 함수 합성으로 작은 함수를 조합하여 복잡한 변환을 구성합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 복잡한 lambda 사용 | 디버깅이 어렵습니다 | 이름 있는 함수로 정의합니다 |
| `@wraps` 누락 | 함수 이름과 docstring이 사라집니다 | 데코레이터에 항상 `@wraps`를 추가합니다 |
| 고차 함수 과도한 중첩 | 가독성이 떨어집니다 | 2단계 이상이면 중간 변수를 사용합니다 |
| 타입 힌트 누락 | Callable의 시그니처가 불명확합니다 | `Callable[[int], str]`처럼 명시합니다 |
| 부수효과가 있는 콜백 | 실행 순서에 민감해집니다 | 콜백은 가능하면 순수 함수로 작성합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 `Depends()`는 의존성 주입을 고차 함수로 구현합니다
- `sorted(key=...)`, `min(key=...)`, `max(key=...)`는 모두 고차 함수입니다
- 로깅, 인증, 캐싱 데코레이터를 고차 함수로 구현합니다
- 이벤트 핸들러 등록은 콜백 패턴을 사용합니다
- 테스트 픽스처를 팩토리 함수로 생성합니다

## 현업 개발자는 이렇게 생각합니다

고차 함수는 "추상화의 도구"입니다. 반복되는 패턴에서 "변하는 부분"을 함수로 뽑아내면 코드 중복이 사라집니다. Python에서는 데코레이터, `sorted(key=...)`, 콜백 패턴 등 고차 함수를 이미 널리 사용하고 있습니다.

다만 과도한 추상화는 오히려 가독성을 해칩니다. "이 함수를 인자로 받을 필요가 있는가?"를 항상 자문하고, 단순한 경우에는 직접 작성하는 것이 나을 수 있습니다.

## 체크리스트

- [ ] 고차 함수의 두 가지 형태를 설명할 수 있다
- [ ] `sorted(key=...)`에 적절한 함수를 전달할 수 있다
- [ ] 팩토리 함수를 작성하여 동적으로 함수를 생성할 수 있다
- [ ] 데코레이터가 고차 함수임을 이해하고 간단한 데코레이터를 작성할 수 있다
- [ ] 고차 함수로 코드 중복을 제거할 수 있다

## 연습 문제

1. `make_formatter(format_str)`를 작성하여 숫자 포매팅 함수를 동적으로 생성하세요.
2. 실행 시간, 호출 횟수, 결과를 로깅하는 `@trace` 데코레이터를 작성하세요.
3. `filter_by(predicate)`, `sort_by(key)`, `transform(func)`를 조합하는 데이터 처리 파이프라인을 구현하세요.

## 정리 및 다음 글 안내

고차 함수는 함수를 인자로 받거나 반환하여 동작을 추상화합니다. 팩토리 패턴과 데코레이터는 고차 함수의 대표적 활용입니다. 다음 글에서는 가장 널리 쓰이는 고차 함수인 **map, filter, reduce**를 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- **고차 함수 (현재 글)**
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)

Tags: Python, Functional Programming, 고차 함수, 콜백, 데코레이터
