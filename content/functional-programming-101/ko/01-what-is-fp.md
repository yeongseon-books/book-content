---
series: functional-programming-101
episode: 1
title: "Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?"
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
  - 패러다임
  - 선언형
  - 프로그래밍 기초
seo_description: Python에서 함수형 프로그래밍의 핵심 원리와 명령형과의 차이를 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?

함수형 프로그래밍을 처음 접하면 대개 문법부터 떠올립니다. `map`, `filter`, `lambda` 같은 도구를 많이 쓰는 스타일이라고 생각하기 쉽습니다. 하지만 현업에서 더 중요한 것은 문법이 아니라 관점입니다. 상태를 계속 바꾸며 문제를 푸는 대신, 데이터를 어떤 변환 단계로 흘려보낼지 먼저 생각하는 방식이 함수형 프로그래밍의 출발점입니다.

Python은 순수 함수형 언어가 아닙니다. 그래서 오히려 배우기 좋습니다. 명령형 코드와 함수형 코드를 같은 프로젝트 안에서 비교해 볼 수 있고, 어느 지점에서 함수형 사고가 유지보수성을 높이는지도 현실적으로 판단할 수 있기 때문입니다.

![Functional Programming 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/01/01-01-big-picture.ko.png)
*Functional Programming 101 1장 흐름 개요*

## 먼저 던지는 질문

- 함수형 프로그래밍은 정확히 무엇이며, 명령형 프로그래밍과 무엇이 다를까요?
- Python에서 함수형 스타일은 어떤 기본 도구로 표현할 수 있을까요?
- 데이터 변환을 함수 조합으로 바라보면 코드가 왜 더 읽기 쉬워질까요?

## 왜 중요한가

소프트웨어가 복잡해질수록 가장 자주 문제를 만드는 것은 상태 관리입니다. 어디선가 값이 바뀌었는데 그 시점과 이유를 추적하기 어려워지고, 그 결과 테스트는 무거워지고 버그는 재현하기 어려워집니다. 함수형 프로그래밍은 상태 변경을 줄이고 데이터 변환을 명시적으로 드러내서 이런 문제를 완화합니다.

Python은 다중 패러다임 언어라서 함수형 스타일을 이해해 두면 선택지가 늘어납니다. 모든 코드를 함수형으로 작성하라는 말이 아니라, 데이터 처리와 비즈니스 규칙처럼 예측 가능성이 중요한 영역에서 더 안정적인 출발점을 확보하자는 이야기입니다.

## 개념 개요

> 명령형은 "어떻게 할지"를 중심으로, 함수형은 "무엇을 계산할지"를 중심으로 사고합니다.

```text
Imperative                       Functional
─────────────────                ─────────────────
"How" to do it                   "What" to compute
Mutate state                     Produce new values
Loop to iterate                  Transform with functions
Reassign variables               Prefer immutable data
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 함수형 프로그래밍(FP) | 함수를 조합해 프로그램을 구성하는 패러다임입니다 |
| 순수 함수(pure function) | 같은 입력에 항상 같은 출력을 반환하는 함수입니다 |
| 불변성(immutability) | 한 번 만든 데이터를 직접 수정하지 않는 원칙입니다 |
| 일급 함수(first-class function) | 함수를 변수에 담고, 인자로 넘기고, 반환값으로 다룰 수 있는 특성입니다 |
| 선언형(declarative) | "어떻게"보다 "무엇을"에 집중하는 스타일입니다 |

## 적용 전후 비교
명령형 반복문을 선언형 변환으로 바꾸면, 코드의 관심사가 루프 제어가 아니라 데이터 변환 규칙으로 이동합니다.

```python
# 이전: 명령형 방식 — 상태를 변경하고 loop를 사용
numbers = [1, 2, 3, 4, 5]
result = []
for n in numbers:
    if n % 2 == 0:
        result.append(n * n)
print(result)  # [4, 16]
```

```python
# 이후: 함수형 방식 — 변환을 조합
numbers = [1, 2, 3, 4, 5]
result = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, numbers)))
print(result)  # [4, 16]
```

## 단계별 실습

### 단계 1: 일급 함수

```python
# 함수를 변수에 할당하고 인자로 전달
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def apply(func, a: int, b: int) -> int:
    return func(a, b)

print(apply(add, 10, 3))       # 13
print(apply(subtract, 10, 3))  # 7

# 함수를 리스트에 저장
operations = [add, subtract]
for op in operations:
    print(f"{op.__name__}(5, 2) = {op(5, 2)}")
# add(5, 2) = 7
# subtract(5, 2) = 3
```

일급 함수는 동작을 값처럼 다루게 해 줍니다. 이 순간부터 함수는 단순한 실행 단위가 아니라, 다른 함수에 전달하고 조합할 수 있는 구성 요소가 됩니다.

### 단계 2: 명령형과 함수형 비교

```python
# 명령형: 상태를 변경하며 결과를 생성
words = ["hello", "world", "python"]
upper_words = []
for w in words:
    upper_words.append(w.upper())
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']

# 함수형: 변환 함수를 적용
words = ["hello", "world", "python"]
upper_words = list(map(str.upper, words))
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']

# 더 Pythonic한 방식: list comprehension
upper_words = [w.upper() for w in words]
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']
```

현업에서는 세 번째 형태를 가장 자주 봅니다. 중요한 것은 특정 문법을 외우는 것이 아니라, 상태를 직접 조작하지 않고 변환 규칙을 표현하는 방식이 함수형 사고의 핵심이라는 점입니다.

### 단계 3: 선언형 데이터 처리

```python
# 학생 점수 처리 — 함수형 스타일
students = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 92},
    {"name": "Charlie", "score": 78},
    {"name": "Diana", "score": 95},
    {"name": "Eve", "score": 60},
]

# 80점 이상 학생 이름을 점수 내림차순으로 정렬
passing = sorted(
    [s["name"] for s in students if s["score"] >= 80],
    key=lambda name: next(s["score"] for s in students if s["name"] == name),
    reverse=True,
)
print(passing)  # ['Diana', 'Bob', 'Alice']
```

이 예제의 포인트는 학생 목록을 어떻게 순회할지가 아니라, 어떤 조건으로 걸러서 어떤 기준으로 정렬할지를 코드에 바로 드러낸다는 데 있습니다.

### 단계 4: 함수 합성으로 파이프라인 만들기

```python
from collections.abc import Callable

def pipeline(*funcs: Callable) -> Callable:
    """Compose multiple functions into a sequential pipeline."""
    def apply(value):
        result = value
        for func in funcs:
            result = func(result)
        return result
    return apply

double = lambda x: x * 2
add_ten = lambda x: x + 10
to_string = lambda x: f"Result: {x}"

transform = pipeline(double, add_ten, to_string)
print(transform(5))   # Result: 20
print(transform(10))  # Result: 30
```

파이프라인은 함수형 프로그래밍을 실무 코드로 연결해 주는 가장 실용적인 패턴입니다. 각 단계가 하나의 일만 하게 만들면 테스트, 교체, 재사용이 모두 쉬워집니다.

### 단계 5: 부수효과 분리

```python
# 순수 함수: 계산만 처리
def calculate_total(prices: list[float], tax_rate: float) -> float:
    subtotal = sum(prices)
    return round(subtotal * (1 + tax_rate), 2)

def format_receipt(total: float) -> str:
    return f"Total: ${total:,.2f}"

# 부수 효과: IO만 처리
def print_receipt(prices: list[float], tax_rate: float) -> None:
    total = calculate_total(prices, tax_rate)
    message = format_receipt(total)
    print(message)  # side effect lives here only

print_receipt([10.00, 20.00, 5.00], 0.1)
# Total: $38.50
```

이 분리는 이후 글 전체를 관통하는 기준이기도 합니다. 계산은 순수 함수로 두고, 출력·저장·네트워크 호출 같은 IO는 경계로 밀어내는 것이 유지보수성의 핵심입니다.

## 이 코드에서 주목할 점

- 일급 함수를 사용하면 동작을 데이터처럼 전달할 수 있습니다.
- 함수형 스타일은 계산 규칙을 전면에 드러내서 코드의 의도를 읽기 쉽게 만듭니다.
- 파이프라인 패턴은 작은 함수를 조합해 복잡한 변환을 단계적으로 표현합니다.
- 순수 계산과 부수효과를 분리하면 테스트 범위를 작게 유지할 수 있습니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 코드를 함수형 스타일로 밀어붙임 | Python다운 가독성이 오히려 떨어질 수 있습니다 | 문제에 맞는 스타일을 선택합니다 |
| `lambda`를 과도하게 사용함 | 디버깅과 코드 리뷰가 어려워집니다 | 복잡해지면 이름 있는 함수로 바꿉니다 |
| 부수효과를 숨긴 채 섞어 씀 | 테스트와 재사용이 어려워집니다 | 순수 로직과 IO를 분리합니다 |
| 컴프리헨션보다 무조건 `map`/`filter`를 선호함 | Python 관용 표현을 놓치게 됩니다 | 단순한 경우는 컴프리헨션을 우선합니다 |
| 함수형은 느리다고 단정함 | 잘못된 최적화로 이어집니다 | 성능은 프로파일링으로 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터 파이프라인에서 변환 함수를 단계별로 조합합니다.
- API 미들웨어를 함수 체인 형태로 구성합니다.
- 비즈니스 규칙을 순수 함수로 분리해 mock 없이 단위 테스트합니다.
- 설정 검증과 포맷팅 로직을 부수효과 없는 함수로 작성합니다.
- 이벤트 핸들러 등록을 일급 함수 패턴으로 단순화합니다.

## 현업에서는 이렇게 판단합니다

함수형 프로그래밍의 요지는 "모든 것을 함수로 만들기"가 아닙니다. 상태를 줄이고, 데이터 흐름을 드러내고, 순수한 계산 단위를 작게 유지하는 쪽이 더 안전한 영역에 함수형 사고를 적용하는 것입니다. Python에서는 리스트 컴프리헨션, 제너레이터, `itertools`가 이미 이 방향을 자연스럽게 지원합니다.

실무적으로 가장 강한 패턴은 비즈니스 로직을 순수 함수로 두고, DB 저장·로그 출력·HTTP 호출 같은 부수효과를 가장 바깥 경계에 두는 방식입니다. 이 구조를 잡으면 테스트 비용과 변경 비용이 함께 내려갑니다.

## 체크리스트

- [ ] 함수형 프로그래밍의 핵심 원칙을 설명할 수 있다
- [ ] 명령형과 함수형 스타일의 차이를 코드로 보여줄 수 있다
- [ ] 일급 함수를 사용해 동작을 추상화할 수 있다
- [ ] 작은 함수 조합으로 간단한 파이프라인을 만들 수 있다
- [ ] 순수 함수와 부수효과를 분리해야 하는 이유를 설명할 수 있다

## 연습 문제

1. 문자열 정규화, 공백 제거, 역순 정렬을 각각 함수로 만든 뒤 하나의 파이프라인으로 조합해 보세요.
2. 명령형으로 작성된 평균 계산 함수를 함수형 스타일로 다시 작성해 보세요.
3. 순수 계산과 출력 로직이 섞인 함수를 둘로 나눠 보세요.

## 정리와 다음 글

함수형 프로그래밍은 데이터를 변환하는 함수들을 조합해 프로그램을 구성하는 사고방식입니다. Python에서는 일급 함수, 컴프리헨션, 제너레이터 덕분에 이 스타일을 무리 없이 적용할 수 있습니다. 다음 글에서는 이 시리즈의 가장 중요한 기초인 **순수 함수와 부수효과**를 다룹니다.

## 함수형 사고가 특히 빛나는 상황

입문 단계에서는 스타일 비교에만 집중하기 쉽지만, 실제로는 "어떤 문제에서 이 사고가 비용을 줄이는지"를 먼저 잡는 편이 좋습니다.

- **데이터 변환 단계가 많은 ETL 작업**: 단계별 함수를 나누고 조합하면 중간 산출물 검증이 쉬워집니다.
- **규칙 기반 검증 로직**: 조건 분기를 작은 순수 함수로 분리하면 테스트 케이스 작성이 단순해집니다.
- **파이프라인형 API 처리**: 입력 정제, 검증, 매핑, 출력 포맷팅을 함수 체인으로 표현하면 흐름이 명확해집니다.

반대로 사용자 인터랙션, DB 트랜잭션, 외부 API 재시도처럼 부수효과가 중심인 영역은 무리하게 함수형 문법을 늘리기보다 경계를 분명히 나누는 접근이 더 실용적입니다. 즉, 함수형 프로그래밍의 목적은 문법 취향이 아니라 변경 비용 관리입니다.

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

- **함수형 프로그래밍은 정확히 무엇이며, 명령형 프로그래밍과 무엇이 다를까요?**
  - 이 글에서 함수형 프로그래밍은 상태를 계속 바꾸는 대신 데이터를 변환 단계로 흘려보내는 방식입니다. `for` 루프와 `append()`로 결과를 쌓는 예제를 `filter()`와 `map()` 조합으로 바꾼 비교, 그리고 `calculate_total()`과 `print_receipt()`를 나눈 예제가 그 차이를 직접 보여 줍니다.
- **Python에서 함수형 스타일은 어떤 기본 도구로 표현할 수 있을까요?**
  - Python에서는 일급 함수, `map()`, `filter()`, 리스트 컴프리헨션, 작은 함수 조합이 기본 도구입니다. `apply(add, 10, 3)`, `map(str.upper, words)`, `pipeline(double, add_ten, to_string)`처럼 함수를 값처럼 넘기고 묶는 방식이 본문 전체에 반복해서 나옵니다.
- **데이터 변환을 함수 조합으로 바라보면 코드가 왜 더 읽기 쉬워질까요?**
  - 함수 조합으로 바꾸면 루프 제어나 임시 상태보다 변환 규칙이 앞에 드러나기 때문입니다. 학생 점수 예제의 필터링·정렬 규칙이나 `double → add_ten → to_string` 파이프라인처럼 각 단계가 한 가지 일만 맡으면 어디서 값이 바뀌는지 빠르게 추적할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- **함수형 프로그래밍이란 무엇인가? (현재 글)**
- 순수 함수와 부수효과 (예정)
- immutable 데이터 (예정)
- 고차 함수 (예정)
- map, filter, reduce (예정)
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [Composing Programs — Chapter 2: Building Abstractions with Data](https://www.composingprograms.com/pages/23-sequences.html)
- [Why Functional Programming Matters — John Hughes](https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 패러다임, 선언형, 프로그래밍 기초
