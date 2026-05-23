---
series: functional-programming-101
episode: 4
title: "Functional Programming 101 (4/10): 고차 함수"
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
  - 고차 함수
  - 콜백
  - 데코레이터
seo_description: 함수를 받고 반환하는 고차 함수의 원리와 Python 실전 패턴을 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (4/10): 고차 함수

고차 함수는 이름만 들으면 추상적인 개념처럼 느껴집니다. 하지만 Python 개발자는 이미 매일 쓰고 있습니다. `sorted(key=...)`, `map(func, ...)`, 데코레이터, 콜백 등록 모두 함수 자체를 값처럼 전달한다는 점에서 고차 함수입니다.

중요한 이유는 단순합니다. 코드에서 반복되는 것은 종종 데이터가 아니라 "동작의 뼈대"이기 때문입니다. 변하는 부분을 함수로 분리해 인자로 넘기거나, 설정이 들어간 새 함수를 만들어 반환하면 중복을 줄이면서도 유연성을 확보할 수 있습니다.

![Functional Programming 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/04/04-01-big-picture.ko.png)
*Functional Programming 101 4장 흐름 개요*

## 먼저 던지는 질문

- 고차 함수는 어떤 두 형태로 나타날까요?
- `sorted`, `map`, `filter`는 왜 고차 함수의 대표 예시일까요?
- 함수를 반환하는 팩토리 패턴은 어떤 상황에서 유용할까요?

## 왜 중요한가

반복 패턴을 함수로 추출하다 보면 어느 시점부터는 로직의 뼈대는 같고, 실제로 달라지는 것은 조건식이나 후처리 방식뿐인 경우가 많습니다. 이때 동작을 함수로 받아들이면 전략 패턴을 클래스 없이도 간결하게 구현할 수 있습니다.

또한 Python 생태계 자체가 고차 함수에 크게 기대고 있습니다. 정렬 기준, 검증 콜백, 미들웨어, 데코레이터, 의존성 주입까지 모두 같은 원리로 연결됩니다. 개념을 이해하고 쓰는 것과, 그냥 관용구로 외워서 쓰는 것 사이에는 유지보수 품질 차이가 큽니다.

## 개념 개요

> 고차 함수는 크게 두 가지입니다. 함수를 인자로 받거나, 함수를 반환합니다.

```text
Form 1: Accept a function          Form 2: Return a function
─────────────────────              ─────────────────
sorted(data, key=func)             def make_adder(n):
map(func, data)                        return lambda x: x + n
filter(func, data)                 adder = make_adder(5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 고차 함수(higher-order function) | 함수를 인자로 받거나 함수를 반환하는 함수입니다 |
| 콜백(callback) | 다른 함수에 인자로 전달되는 함수입니다 |
| 일급 객체(first-class object) | 변수 할당, 인자 전달, 반환이 가능한 객체입니다 |
| 팩토리 함수(factory function) | 새로운 함수나 객체를 만들어 반환하는 함수입니다 |
| 데코레이터(decorator) | 함수를 받아 기능이 추가된 새 함수를 반환하는 고차 함수입니다 |

## 적용 전후 비교
비슷한 함수가 계속 늘어나는 신호는 대개 "변하는 조건만 분리하라"는 뜻입니다.

```python
# 이전: 거의 동일한 로직의 함수 3개
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
# 이후: 조건을 인자로 받는 고차 함수
from collections.abc import Callable

def filter_people(
    people: list[dict],
    predicate: Callable[[dict], bool],
) -> list[dict]:
    return [p for p in people if predicate(p)]

adults = filter_people(people, lambda p: p["age"] >= 18)
seniors = filter_people(people, lambda p: p["age"] >= 65)
```

## 단계별 실습

### 단계 1: 함수를 인자로 전달하기

```python
from collections.abc import Callable

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

같은 순회 구조 안에서 어떤 연산을 할지만 바뀌는 경우, 고차 함수는 중복을 제거하면서 의도를 더 선명하게 만듭니다.

### 단계 2: sorted의 key 파라미터 이해하기

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

# 점수로 정렬
by_score = sorted(students, key=lambda s: s.score, reverse=True)
for s in by_score:
    print(f"{s.name}: {s.score}")
# Diana: 95
# Bob: 92
# Alice: 85
# Charlie: 78

# 다중 키 정렬: grade 후 score
by_grade_score = sorted(students, key=lambda s: (s.grade, -s.score))
for s in by_grade_score:
    print(f"  Grade {s.grade} {s.name}: {s.score}")
#   Grade 1 Diana: 95
#   Grade 2 Bob: 92
#   Grade 3 Alice: 85
#   Grade 3 Charlie: 78
```

`sorted(key=...)`는 실무에서 가장 많이 만나는 고차 함수입니다. 정렬 알고리즘을 다시 쓰는 대신, "무엇을 기준으로 정렬할지"만 함수로 넘기면 됩니다.

### 단계 3: 함수를 반환하는 팩토리 함수

```python
from collections.abc import Callable

def make_multiplier(factor: int) -> Callable[[int], int]:
    """Creates a multiplier function."""
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

def make_validator(min_val: float, max_val: float) -> Callable[[float], bool]:
    """Creates a range validation function."""
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

함수를 반환하는 패턴은 설정이 들어간 동작을 만드는 데 강력합니다. "지금 당장 값을 계산하는 함수"가 아니라 "나중에 호출할 규칙 자체"를 생성하는 셈입니다.

### 단계 4: 데코레이터와 고차 함수

```python
import time
from collections.abc import Callable
from typing import Any
from functools import wraps

def timer(func: Callable) -> Callable:
    """A decorator that measures execution time."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}s")
        return result
    return wrapper

def retry(max_attempts: int) -> Callable:
    """Creates a retry decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"  Attempt {attempt} failed: {e}")
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
        raise ValueError("transient error")
    return "success"

result = slow_sum(1_000_000)
print(f"Result: {result}")
# slow_sum: 0.0234s
# Result: 499999500000
```

데코레이터는 결국 함수를 받아 함수를 돌려주는 고차 함수입니다. 이 관점을 잡으면 `@wraps`가 왜 필요한지, 재시도·로깅·권한 검사 같은 횡단 관심사를 왜 데코레이터로 분리하는지 자연스럽게 이해됩니다.

### 단계 5: 고차 함수로 파이프라인 만들기

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def compose(*funcs: Callable) -> Callable:
    """Composes functions from right to left."""
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

고차 함수는 파이프라인과도 자연스럽게 이어집니다. 작은 변환 함수를 조합하는 방식은 이후 함수 합성 글에서 더 확장됩니다.

## 이 코드에서 주목할 점

- 고차 함수는 변하는 동작을 인자로 받아 중복을 제거합니다.
- 팩토리 함수는 설정이 다른 함수를 동적으로 만들어 냅니다.
- 데코레이터는 고차 함수의 문법 설탕이며 `@wraps`는 메타데이터 보존에 중요합니다.
- 함수 합성은 작은 함수를 묶어 더 큰 변환을 만드는 대표 패턴입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 복잡한 `lambda`를 남발함 | 디버깅과 리뷰가 어려워집니다 | 이름 있는 함수로 분리합니다 |
| `@wraps`를 빼먹음 | 함수 이름과 docstring이 사라집니다 | 데코레이터에 항상 `@wraps`를 넣습니다 |
| 고차 함수 중첩이 과도함 | 가독성이 급격히 떨어집니다 | 두 단계가 넘으면 중간 변수를 둡니다 |
| 타입 힌트를 생략함 | `Callable` 시그니처가 अस्पष्ट해집니다 | `Callable[[int], str]`처럼 명시합니다 |
| 부수효과 있는 콜백을 넘김 | 실행 순서와 상태에 민감해집니다 | 가능하면 순수 함수 콜백을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 `Depends()`는 의존성 주입을 고차 함수 패턴으로 활용합니다.
- `sorted(key=...)`, `min(key=...)`, `max(key=...)`는 모두 고차 함수입니다.
- 로깅, 인증, 캐싱 데코레이터를 같은 구조로 구현합니다.
- 이벤트 핸들러 등록은 콜백 패턴을 사용합니다.
- 테스트 픽스처 생성에 팩토리 함수를 활용합니다.

## 현업에서는 이렇게 판단합니다

고차 함수의 핵심 가치는 추상화입니다. 반복되는 흐름에서 "변하는 부분"만 함수로 끌어내면 클래스 계층 없이도 전략을 교체할 수 있습니다. Python에서 데코레이터와 정렬 키 함수가 널리 쓰이는 이유도 결국 같은 추상화 비용 대비 효과가 크기 때문입니다.

다만 추상화가 항상 정답은 아닙니다. 정말로 함수 인자를 받아야 하는지, 단순한 코드를 괜히 일반화하고 있지는 않은지 계속 점검해야 합니다. 좋은 고차 함수는 중복을 줄이지만, 나쁜 고차 함수는 읽는 사람의 인지 부하만 늘립니다.

## 체크리스트

- [ ] 고차 함수의 두 형태를 설명할 수 있다
- [ ] `sorted(key=...)`에 적절한 함수를 전달할 수 있다
- [ ] 팩토리 함수를 작성해 함수를 동적으로 생성할 수 있다
- [ ] 데코레이터가 고차 함수라는 점을 이해하고 간단한 데코레이터를 작성할 수 있다
- [ ] 고차 함수로 중복 로직을 줄일 수 있다

## 연습 문제

1. `make_formatter(format_str)` 함수를 만들어 숫자 포맷 함수를 동적으로 생성해 보세요.
2. 실행 시간, 호출 횟수, 결과를 기록하는 `@trace` 데코레이터를 작성해 보세요.
3. `filter_by(predicate)`, `sort_by(key)`, `transform(func)`를 조합한 데이터 처리 파이프라인을 구현해 보세요.

## 정리와 다음 글

고차 함수는 함수를 인자로 받거나 반환하면서 동작을 추상화합니다. 팩토리 패턴과 데코레이터는 가장 자주 만나는 응용 형태입니다. 다음 글에서는 이 개념이 가장 직접적으로 드러나는 **map, filter, reduce**를 다룹니다.

## 검증 시나리오: 경계 조건을 먼저 잠그기

실무에서 함수형 스타일이 유지되는 팀은 구현보다 먼저 검증 포인트를 고정합니다. 입력 경계, 빈 컬렉션, 정렬 안정성, 타입 변환 실패를 먼저 적어 두면 리팩터링 과정에서도 동작이 흔들리지 않습니다.

```python
from functools import reduce

def pipeline(values: list[int]) -> dict[str, int]:
    filtered = [v for v in values if v >= 0]
    squared = [v * v for v in filtered]
    total = reduce(lambda acc, x: acc + x, squared, 0)
    return {
        "count": len(squared),
        "total": total,
        "max": max(squared) if squared else 0,
    }

# 경계 조건 검증
assert pipeline([]) == {"count": 0, "total": 0, "max": 0}
assert pipeline([-3, -1]) == {"count": 0, "total": 0, "max": 0}
assert pipeline([0, 2, 3]) == {"count": 3, "total": 13, "max": 9}

print("Pass")
```

또한 지연 평가를 사용할 때는 소비 시점을 테스트에 명시해 두는 편이 좋습니다. generator는 한 번 소비하면 비어야 정상이며, 이 성질이 깨지면 중간 단계에서 의도치 않은 materialize가 발생했을 가능성이 큽니다.

```python
from itertools import islice

def naturals():
    n = 0
    while True:
        yield n
        n += 1

stream = naturals()
first_five = list(islice(stream, 5))
next_three = list(islice(stream, 3))

assert first_five == [0, 1, 2, 3, 4]
assert next_three == [5, 6, 7]
print("Pass")
```

이런 검증 코드는 예제 코드가 아니라 운영 안전장치입니다. 새 규칙을 추가할 때도 기존 성질이 유지되는지 빠르게 확인할 수 있습니다.

## 리뷰 포인트: 코드 리뷰에서 바로 확인할 항목

함수형 스타일을 적용한 코드 리뷰에서는 다음 네 가지를 빠르게 확인합니다. 첫째, 계산 함수가 외부 상태를 직접 읽거나 쓰지 않는지 확인합니다. 둘째, mutable 인자를 제자리에서 수정하지 않는지 확인합니다. 셋째, 파이프라인 단계의 입력과 출력 타입이 자연스럽게 연결되는지 확인합니다. 넷째, 실패 경로가 값으로 표현되는지 확인합니다.

```python
def reviewer_checklist() -> list[str]:
    return [
        "pure-core",
        "immutable-update",
        "typed-boundary",
        "explicit-failure-path",
    ]

assert len(reviewer_checklist()) == 4
print("Pass")
```

이 항목을 PR 템플릿에 고정해 두면 스타일 논쟁보다 설계 품질을 빠르게 맞출 수 있습니다.

## 처음 질문으로 돌아가기

- **고차 함수는 어떤 두 형태로 나타날까요?**
  - 고차 함수는 함수를 인자로 받거나, 함수를 반환하는 두 형태로 나타납니다. `apply_operation()`과 `filter_people()`는 동작을 인자로 받고, `make_multiplier()`와 `make_validator()`는 설정이 들어간 새 함수를 돌려준다는 점에서 두 형태를 정확히 보여 줍니다.
- **`sorted`, `map`, `filter`는 왜 고차 함수의 대표 예시일까요?**
  - 세 함수 모두 반복 구조는 라이브러리가 맡고, 우리는 정렬 기준이나 변환 규칙만 함수로 넘기기 때문입니다. `sorted(students, key=lambda s: s.score)`처럼 무엇을 기준으로 볼지만 드러내면 루프를 다시 쓰지 않아도 의도가 바로 읽힙니다.
- **함수를 반환하는 팩토리 패턴은 어떤 상황에서 유용할까요?**
  - 팩토리 함수는 같은 계산 틀에 설정만 바뀌는 상황에서 특히 강합니다. `make_multiplier(2)`, `make_validator(0, 100)`, `retry(max_attempts=3)`처럼 한 번 정한 규칙을 함수로 묶어 두면, 호출부는 매번 조건을 다시 조립하지 않고 바로 재사용할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- **고차 함수 (현재 글)**
- map, filter, reduce (예정)
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 고차 함수, 콜백, 데코레이터
