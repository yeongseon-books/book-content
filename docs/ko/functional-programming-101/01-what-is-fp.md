---
series: functional-programming-101
episode: 1
title: 함수형 프로그래밍이란 무엇인가?
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
  - 패러다임
  - 선언형
  - 프로그래밍 기초
seo_description: 함수형 프로그래밍의 핵심 개념과 명령형 프로그래밍과의 차이를 알아봅니다.
last_reviewed: '2026-05-04'
---

# 함수형 프로그래밍이란 무엇인가?

> Functional Programming 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 함수형 프로그래밍은 무엇이고, 왜 관심을 가져야 할까요?

> 함수형 프로그래밍은 데이터를 변환하는 함수의 조합으로 프로그램을 구성하는 패러다임입니다. 상태 변경을 최소화하고 예측 가능한 코드를 작성하는 데 집중합니다. 이 글에서는 함수형 프로그래밍의 핵심 철학과 Python에서의 적용 가능성을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 함수형 프로그래밍의 정의와 핵심 원칙
- 명령형 프로그래밍과의 비교
- Python에서 함수형 스타일을 적용하는 방법
- 함수형 프로그래밍이 유용한 상황

## 왜 중요한가

소프트웨어가 복잡해질수록 상태 관리가 버그의 주요 원인이 됩니다. 함수형 프로그래밍은 상태 변경을 최소화하여 코드의 예측 가능성을 높이고, 테스트와 디버깅을 쉽게 만듭니다.

> 함수형 사고 = 데이터 흐름 중심 설계

Python은 다중 패러다임 언어입니다. 함수형 스타일을 이해하면 상황에 따라 가장 적절한 도구를 선택할 수 있습니다.

## 핵심 개념 잡기

> 명령형 vs 함수형 — 관점의 차이

```
명령형 (Imperative)              함수형 (Functional)
─────────────────                ─────────────────
"어떻게" 할 것인가               "무엇을" 할 것인가
상태를 변경                      새 값을 생성
반복문으로 순회                   함수로 변환
변수 재할당                      불변 데이터 선호
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 함수형 프로그래밍(FP) | 함수 조합으로 프로그램을 구성하는 패러다임입니다 |
| 순수 함수(pure function) | 같은 입력에 항상 같은 출력을 반환하는 함수입니다 |
| 불변성(immutability) | 한번 생성된 데이터를 변경하지 않는 원칙입니다 |
| 일급 함수(first-class function) | 함수를 변수에 담고 인자로 전달할 수 있는 특성입니다 |
| 선언형(declarative) | "무엇을"에 집중하는 프로그래밍 스타일입니다 |

## Before / After

명령형 스타일을 함수형 스타일로 전환합니다.

```python
# before: 명령형 — 상태 변경, 반복문
numbers = [1, 2, 3, 4, 5]
result = []
for n in numbers:
    if n % 2 == 0:
        result.append(n * n)
print(result)  # [4, 16]
```

```python
# after: 함수형 — 변환 함수 조합
numbers = [1, 2, 3, 4, 5]
result = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, numbers)))
print(result)  # [4, 16]
```

## 단계별 실습

### Step 1: 일급 함수

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

# 함수를 리스트에 담기
operations = [add, subtract]
for op in operations:
    print(f"{op.__name__}(5, 2) = {op(5, 2)}")
# add(5, 2) = 7
# subtract(5, 2) = 3
```

### Step 2: 명령형 vs 함수형 비교

```python
# 명령형: 상태를 변경하며 결과 구축
words = ["hello", "world", "python"]
upper_words = []
for w in words:
    upper_words.append(w.upper())
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']


# 함수형: 변환 함수 적용
words = ["hello", "world", "python"]
upper_words = list(map(str.upper, words))
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']


# 더 Pythonic한 방법: 리스트 컴프리헨션
upper_words = [w.upper() for w in words]
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']
```

### Step 3: 선언형 데이터 처리

```python
# 학생 점수 데이터 처리 — 함수형 스타일
students = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 92},
    {"name": "Charlie", "score": 78},
    {"name": "Diana", "score": 95},
    {"name": "Eve", "score": 60},
]

# 80점 이상인 학생의 이름을 점수 내림차순으로 정렬
passing = sorted(
    [s["name"] for s in students if s["score"] >= 80],
    key=lambda name: next(s["score"] for s in students if s["name"] == name),
    reverse=True,
)
print(passing)  # ['Diana', 'Bob', 'Alice']
```

### Step 4: 함수 조합으로 파이프라인 구성

```python
from typing import Callable


def pipeline(*funcs: Callable) -> Callable:
    """여러 함수를 순차적으로 적용하는 파이프라인을 구성합니다."""
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

### Step 5: 부수효과 분리

```python
# 순수 함수: 계산 로직만 담당
def calculate_total(prices: list[float], tax_rate: float) -> float:
    subtotal = sum(prices)
    return round(subtotal * (1 + tax_rate), 2)

def format_receipt(total: float) -> str:
    return f"총액: {total:,.0f}원"


# 부수효과: IO만 담당
def print_receipt(prices: list[float], tax_rate: float) -> None:
    total = calculate_total(prices, tax_rate)
    message = format_receipt(total)
    print(message)  # 부수효과는 여기에만 존재


print_receipt([10000, 20000, 5000], 0.1)
# 총액: 38,500원
```

## 이 코드에서 주목할 점

- 일급 함수를 활용하면 동작을 데이터처럼 다룰 수 있습니다
- 함수형 스타일은 "무엇을"에 집중하여 의도를 명확히 드러냅니다
- 파이프라인 패턴은 작은 함수를 조합하여 복잡한 변환을 구성합니다
- 순수 함수와 부수효과를 분리하면 테스트가 쉬워집니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 코드를 함수형으로 작성 | 가독성이 오히려 떨어집니다 | 상황에 맞는 스타일을 선택합니다 |
| lambda 남용 | 복잡한 lambda는 읽기 어렵습니다 | 이름 있는 함수로 정의합니다 |
| 부수효과를 무시 | IO, 로깅은 불가피합니다 | 순수 로직과 부수효과를 분리합니다 |
| 리스트 컴프리헨션 무시 | map/filter보다 Pythonic합니다 | 간단한 경우 컴프리헨션을 사용합니다 |
| 함수형 = 느리다고 오해 | 적절한 사용은 성능에 영향 없습니다 | 프로파일링 후 최적화합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터 파이프라인에서 변환 함수를 조합합니다
- API 미들웨어를 함수 체이닝으로 구성합니다
- 테스트에서 순수 함수는 mock 없이 검증합니다
- 설정 검증 로직을 순수 함수로 분리합니다
- 이벤트 핸들러를 일급 함수로 등록합니다

## 현업 개발자는 이렇게 생각합니다

함수형 프로그래밍은 "모든 것을 함수로"가 아니라 "적절한 곳에 함수형 사고를" 적용하는 것입니다. Python에서는 리스트 컴프리헨션, 제너레이터, itertools 같은 도구가 함수형 스타일을 자연스럽게 지원합니다.

실무에서는 순수 함수로 비즈니스 로직을 작성하고, 부수효과를 경계에 몰아넣는 패턴이 가장 실용적입니다. 이 접근은 테스트 용이성과 코드 재사용성을 크게 높여줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **부수효과 격리** — 효과를 외곽으로 밀고 코어를 순수하게 유지합니다.
- **값 중심 사고** — 상태 변경보다 값 변환으로 모델링합니다.
- **타입 우선** — 함수 시그니처가 곧 명세입니다.
- **균형** — 파이썬에서는 OOP·FP를 혼합하는 편이 현실적입니다.
- **테스트성** — 순수 함수는 테스트 가성비가 가장 큽니다.

## 체크리스트

- [ ] 함수형 프로그래밍의 핵심 원칙을 설명할 수 있다
- [ ] 명령형과 함수형 스타일의 차이를 코드로 보여줄 수 있다
- [ ] 일급 함수를 활용하여 동작을 추상화할 수 있다
- [ ] 간단한 파이프라인을 함수 조합으로 구성할 수 있다
- [ ] 순수 함수와 부수효과를 분리하는 이유를 설명할 수 있다

## 연습 문제

1. 세 개의 변환 함수(소문자 변환, 공백 제거, 역순 정렬)를 조합하는 파이프라인을 작성하세요.
2. 명령형으로 작성된 평균 계산 코드를 함수형 스타일로 리팩터링하세요.
3. 순수 함수와 부수효과가 혼재된 코드를 분리하여 리팩터링하세요.

## 정리 및 다음 글 안내

함수형 프로그래밍은 데이터 변환과 함수 조합에 집중하는 패러다임입니다. Python에서는 일급 함수, 리스트 컴프리헨션, 제너레이터 등을 통해 자연스럽게 함수형 스타일을 적용할 수 있습니다. 다음 글에서는 함수형의 가장 기본이 되는 **순수 함수와 부수효과**를 자세히 다룹니다.

<!-- toc:begin -->
- **함수형 프로그래밍이란 무엇인가? (현재 글)**
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [Composing Programs — Chapter 2: Building Abstractions with Data](https://www.composingprograms.com/pages/23-sequences.html)
- [Why Functional Programming Matters — John Hughes](https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf)
