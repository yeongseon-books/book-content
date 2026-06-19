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

이 글은 Functional Programming 101 시리즈의 첫 번째 글입니다.

Python은 순수 함수형 언어가 아닙니다. 그래서 오히려 배우기 좋습니다. 명령형 코드와 함수형 코드를 같은 프로젝트 안에서 비교해 볼 수 있고, 어느 지점에서 함수형 사고가 유지보수성을 높이는지도 현실적으로 판단할 수 있기 때문입니다.

![Functional Programming 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/01/01-01-big-picture.ko.png)
*Functional Programming 101 1장 흐름 개요*

## 이 글에서 다룰 문제

- 함수형 프로그래밍은 정확히 무엇이며, 명령형 프로그래밍과 무엇이 다를까요?
- Python에서 함수형 스타일은 어떤 기본 도구로 표현할 수 있을까요?
- 데이터 변환을 함수 조합으로 바라보면 코드가 왜 더 읽기 쉬워질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

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
# 이후: 함수형 방식 — filter로 선택하고 map으로 변환
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# filter: 짝수만 선택
evens = list(filter(lambda n: n % 2 == 0, numbers))

# map: 제곱 변환
result = list(map(lambda n: n * n, evens))
print(result)  # [4, 16]

# 또는 한 줄로 조합
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

### 단계 2: map으로 변환하기

`map`은 컬렉션의 모든 원소에 동일한 함수를 적용합니다. 변환 규칙이 명확히 드러나는 것이 핵심입니다.

```python
# 명령형: 상태를 변경하며 결과를 생성
words = ["hello", "world", "python"]
upper_words = []
for w in words:
    upper_words.append(w.upper())
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']

# map 방식: 변환 함수를 적용
words = ["hello", "world", "python"]
upper_words = list(map(str.upper, words))
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']

# 여러 시퀀스에 동시에 map 적용
prices = [100, 200, 300]
quantities = [2, 3, 1]
totals = list(map(lambda p, q: p * q, prices, quantities))
print(totals)  # [200, 600, 300]
```

### 단계 3: filter로 선택하기

`filter`는 조건을 만족하는 원소만 남깁니다. "어떤 항목을 남길지"만 표현하면 됩니다.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# filter: 짝수만 선택
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# 학생 데이터에서 조건 선택
students = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 92},
    {"name": "Charlie", "score": 78},
    {"name": "Diana", "score": 95},
    {"name": "Eve", "score": 60},
]

# 80점 이상인 학생만 선택
passing = list(filter(lambda s: s["score"] >= 80, students))
print([s["name"] for s in passing])  # ['Alice', 'Bob', 'Diana']
```

### 단계 4: reduce로 집계하기

`reduce`는 시퀀스를 하나의 값으로 축약합니다. `map`과 `filter`가 변환과 선택이라면, `reduce`는 최종 집계 역할입니다.

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# reduce: 합계
total = reduce(lambda acc, x: acc + x, numbers, 0)
print(total)  # 15

# 최댓값 구하기
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5

# map + filter + reduce 조합: 짝수의 제곱 합
even_square_sum = reduce(
    lambda acc, x: acc + x,
    map(lambda n: n * n, filter(lambda n: n % 2 == 0, numbers)),
    0,
)
print(even_square_sum)  # 4 + 16 = 20
```

### 단계 5: 선언형 데이터 처리

```python
# 학생 점수 처리 — 함수형 스타일
students = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 92},
    {"name": "Charlie", "score": 78},
    {"name": "Diana", "score": 95},
    {"name": "Eve", "score": 60},
]

# 단계 1: 80점 이상 필터링
passing = filter(lambda s: s["score"] >= 80, students)

# 단계 2: 점수 내림차순 정렬
ranked = sorted(passing, key=lambda s: s["score"], reverse=True)

# 단계 3: 이름만 추출
names = list(map(lambda s: s["name"], ranked))
print(names)  # ['Diana', 'Bob', 'Alice']
```

이 예제의 포인트는 학생 목록을 어떻게 순회할지가 아니라, 어떤 조건으로 걸러서 어떤 기준으로 정렬할지를 코드에 바로 드러낸다는 데 있습니다.

### 단계 6: 함수 합성으로 파이프라인 만들기

```python
from collections.abc import Callable

def pipeline(*funcs: Callable) -> Callable:
    """여러 함수를 순차적으로 실행하는 파이프라인을 구성합니다."""
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

### 단계 7: 부수효과 분리

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

### 단계 8: 실무 데이터 파이프라인 — 주문 처리 예시

개별 도구를 익혔다면 함께 쓸 때 힘이 어떻게 커지는지 보여주는 예시입니다.

```python
from functools import reduce

# 주문 목록 — 실무 데이터 형태 그대로
orders = [
    {"id": "O001", "product": "Laptop", "qty": 1, "price": 1_200_000, "status": "paid"},
    {"id": "O002", "product": "Mouse",  "qty": 3, "price":    25_000, "status": "paid"},
    {"id": "O003", "product": "Monitor","qty": 2, "price":   350_000, "status": "pending"},
    {"id": "O004", "product": "Keyboard","qty": 2,"price":    80_000, "status": "paid"},
    {"id": "O005", "product": "Webcam", "qty": 1, "price":    90_000, "status": "cancelled"},
]

# 단계 1 — filter: 결제 완료된 주문만 선택
paid = filter(lambda o: o["status"] == "paid", orders)

# 단계 2 — map: 각 주문에 총액(total) 필드 추가
with_total = map(lambda o: {**o, "total": o["qty"] * o["price"]}, paid)

# 단계 3 — filter: 총액 50,000원 이상 주문만 선택
significant = filter(lambda o: o["total"] >= 50_000, with_total)

# 단계 4 — reduce: 총 매출 집계
revenue = reduce(lambda acc, o: acc + o["total"], significant, 0)

print(f"Revenue: {revenue:,}원")   # Revenue: 1,520,000원
```

이 파이프라인은 루프 변수가 없습니다. 각 단계가 무엇을 하는지 함수 이름만 읽어도 알 수 있습니다. `filter`(선택) → `map`(변환) → `filter`(정제) → `reduce`(집계) 순서는 대부분의 데이터 처리 흐름에 자연스럽게 대응됩니다.

## 이 코드에서 주목할 점

- `map`, `filter`, `reduce`는 변환, 선택, 집계라는 서로 다른 역할을 명시적으로 표현합니다.
- 일급 함수를 사용하면 동작을 데이터처럼 전달할 수 있습니다.
- 파이프라인 패턴은 작은 함수를 조합해 복잡한 변환을 단계적으로 표현합니다.
- 순수 계산과 부수효과를 분리하면 테스트 범위를 작게 유지할 수 있습니다.
- `{**o, "key": value}` 패턴은 기존 딕셔너리를 유지하면서 새 필드를 추가하는 불변 방식입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 코드를 함수형 스타일로 밀어붙임 | Python다운 가독성이 오히려 떨어질 수 있습니다 | 문제에 맞는 스타일을 선택합니다 |
| `lambda`를 과도하게 사용함 | 디버깅과 코드 리뷰가 어려워집니다 | 복잡해지면 이름 있는 함수로 바꿉니다 |
| 부수효과를 숨긴 채 섞어 씀 | 테스트와 재사용이 어려워집니다 | 순수 로직과 IO를 분리합니다 |
| `reduce`에 초기값을 생략함 | 빈 시퀀스에서 오류가 납니다 | 항상 초기값을 함께 제공합니다 |
| 함수형은 느리다고 단정함 | 잘못된 최적화로 이어집니다 | 성능은 프로파일링으로 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터 파이프라인에서 변환 함수를 단계별로 조합합니다.
- API 미들웨어를 함수 체인 형태로 구성합니다.
- 비즈니스 규칙을 순수 함수로 분리해 mock 없이 단위 테스트합니다.
- 설정 검증과 포맷팅 로직을 부수효과 없는 함수로 작성합니다.
- `map`/`filter`/`reduce` 조합으로 선언형 데이터 처리 흐름을 만듭니다.
- `functools.partial`로 공통 인자를 고정한 특화 함수를 만들어 `map`에 전달합니다.
- 이벤트 버스, 미들웨어 체인, 데코레이터 시스템을 함수 조합으로 구성합니다.

## 현업에서는 이렇게 판단합니다

함수형 프로그래밍의 요지는 "모든 것을 함수로 만들기"가 아닙니다. 상태를 줄이고, 데이터 흐름을 드러내고, 순수한 계산 단위를 작게 유지하는 쪽이 더 안전한 영역에 함수형 사고를 적용하는 것입니다. Python에서는 리스트 컴프리헨션, 제너레이터, `itertools`가 이미 이 방향을 자연스럽게 지원합니다.

실무적으로 가장 강한 패턴은 비즈니스 로직을 순수 함수로 두고, DB 저장·로그 출력·HTTP 호출 같은 부수효과를 가장 바깥 경계에 두는 방식입니다. 이 구조를 잡으면 테스트 비용과 변경 비용이 함께 내려갑니다.

## 처음 질문으로 돌아가기

- **함수형 프로그래밍은 정확히 무엇이며, 명령형 프로그래밍과 무엇이 다를까요?**
  명령형은 루프와 변수 재할당으로 "어떻게 계산할지"를 기술합니다. 함수형은 `map`, `filter`, `reduce` 같은 변환 연산으로 "무엇을 계산할지"를 선언합니다. 같은 결과를 내도 코드가 드러내는 의도가 다릅니다.

- **Python에서 함수형 스타일은 어떤 기본 도구로 표현할 수 있을까요?**
  `map`(변환), `filter`(선택), `reduce`(집계)가 핵심 세 도구입니다. 여기에 리스트 컴프리헨션, 제너레이터 표현식, `functools` 모듈이 더해지면 대부분의 함수형 패턴을 표현할 수 있습니다.

- **데이터 변환을 함수 조합으로 바라보면 코드가 왜 더 읽기 쉬워질까요?**
  각 함수가 하나의 역할만 맡고, 그 역할을 함수 이름이 바로 드러냅니다. 중간 상태를 저장하는 변수가 줄어들고 데이터가 어떻게 흘러가는지 한눈에 볼 수 있습니다.

## 운영 체크리스트

- [ ] 함수형 프로그래밍의 핵심 원칙을 설명할 수 있다
- [ ] 명령형과 함수형 스타일의 차이를 코드로 보여줄 수 있다
- [ ] `map`, `filter`, `reduce`를 각각 언제 쓰는지 설명할 수 있다
- [ ] 작은 함수 조합으로 간단한 파이프라인을 만들 수 있다
- [ ] 순수 함수와 부수효과를 분리해야 하는 이유를 설명할 수 있다

## 연습 문제

1. 정수 리스트에서 홀수만 골라 세 배로 만든 뒤 합계를 `map`, `filter`, `reduce`만으로 구현해 보세요.
2. 문자열 정규화, 공백 제거, 역순 정렬을 각각 함수로 만든 뒤 하나의 파이프라인으로 조합해 보세요.
3. 순수 계산과 출력 로직이 섞인 함수를 둘로 나눠 보세요.

## 정리와 다음 글

함수형 프로그래밍은 데이터를 변환하는 함수들을 조합해 프로그램을 구성하는 사고방식입니다. `map`, `filter`, `reduce`는 그 사고를 코드로 표현하는 핵심 도구입니다. Python에서는 일급 함수, 컴프리헨션, 제너레이터 덕분에 이 스타일을 무리 없이 적용할 수 있습니다. 다음 글에서는 이 시리즈의 가장 중요한 기초인 **순수 함수와 부수효과**를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- **Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가? (현재 글)**
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- [Functional Programming 101 (7/10): 재귀와 꼬리 호출](./07-recursion.md)
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [Functional Programming 101 (9/10): 함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [Composing Programs — Chapter 2: Building Abstractions with Data](https://www.composingprograms.com/pages/23-sequences.html)
- [Why Functional Programming Matters — John Hughes](https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 패러다임, 선언형, 프로그래밍 기초
