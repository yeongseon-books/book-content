---
series: functional-programming-101
episode: 5
title: "Functional Programming 101 (5/10): map, filter, reduce"
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
  - map
  - filter
  - reduce
seo_description: map, filter, reduce의 원리와 컴프리헨션과의 차이를 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (5/10): map, filter, reduce

함수형 프로그래밍을 처음 배울 때 가장 먼저 만나는 실전 도구가 `map`, `filter`, `reduce`입니다. 셋 다 결국 반복을 다루지만, 중요한 것은 루프 문법이 아니라 역할 분담입니다. 값을 바꾸는지, 걸러내는지, 하나로 합치는지를 명시적으로 표현하게 해 줍니다.

Python에서는 리스트 컴프리헨션이 더 자주 쓰이기 때문에 이 세 함수를 낡은 문법처럼 오해하기도 합니다. 하지만 개념 자체는 여전히 중요합니다. pandas, SQL, Spark 같은 도구를 이해할 때도 결국 같은 사고방식이 반복되기 때문입니다.

![Functional Programming 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/05/05-01-big-picture.ko.png)
*Functional Programming 101 5장 흐름 개요*

## 먼저 던지는 질문

- `map`, `filter`, `reduce`는 각각 어떤 역할을 맡을까요?
- 반복문으로 쓰던 데이터를 선언형 파이프라인으로 어떻게 바꿀 수 있을까요?
- 리스트 컴프리헨션과 `map`/`filter`는 언제 각각 더 적합할까요?

## 왜 중요한가

실무 데이터 처리의 대부분은 세 가지 패턴으로 압축됩니다. 값을 다른 형태로 바꾸거나, 조건에 맞는 항목만 고르거나, 여러 항목을 하나의 결과로 합칩니다. 이 세 가지를 명확히 구분해 표현할 수 있으면 반복 로직이 훨씬 간결해집니다.

Python에서는 단순한 경우 컴프리헨션이 더 관용적이지만, 도구 선택은 개념 이해 위에 서야 합니다. 어떤 상황에서 무엇이 더 읽기 쉬운지 판단하려면 먼저 역할 자체를 분리해 볼 수 있어야 합니다.

## 개념 개요

> 세 함수는 모두 반복을 숨기지만, 무엇을 하려는지는 서로 다릅니다.

```text
Input list    [1, 2, 3, 4, 5]
              |
map(f)        [f(1), f(2), f(3), f(4), f(5)]    -> transform
filter(p)     [x for x if p(x)]                  -> select
reduce(g)     g(g(g(g(x1, x2), x3), x4), x5)    -> aggregate
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| map | 각 원소에 함수를 적용해 새 시퀀스를 만듭니다 |
| filter | 조건을 만족하는 원소만 남깁니다 |
| reduce | 시퀀스를 하나의 값으로 축약합니다 |
| 리스트 컴프리헨션 | Python의 선언형 리스트 생성 문법입니다 |
| 지연 평가 | `map`과 `filter`가 필요할 때만 값을 계산하는 방식입니다 |

## 적용 전후 비교
명령형 반복문이 나쁜 것은 아니지만, 변환과 선택의 의도가 루프 제어 속에 묻히기 쉽습니다.

```python
# 이전: 명령형 loop
prices = [1200, 3400, 5600, 7800, 2300]
discounted = []
for p in prices:
    if p >= 3000:
        discounted.append(int(p * 0.9))
print(discounted)  # [3060, 5040, 7020]
```

```python
# 이후: map + filter 조합
prices = [1200, 3400, 5600, 7800, 2300]
discounted = list(map(
    lambda p: int(p * 0.9),
    filter(lambda p: p >= 3000, prices),
))
print(discounted)  # [3060, 5040, 7020]
```

## 단계별 실습

### 단계 1: map으로 변환하기

```python
# basic usage
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25]

# 기명 함수와 함께 사용
def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

temps_c = [0, 20, 37, 100]
temps_f = list(map(celsius_to_fahrenheit, temps_c))
print(temps_f)  # [32.0, 68.0, 98.6, 212.0]

# 여러 시퀀스에 동시에 적용
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)  # [11, 22, 33]

# list comprehension 대안
squares_comp = [x ** 2 for x in numbers]
print(squares_comp)  # [1, 4, 9, 16, 25]
```

`map`은 "모든 원소에 같은 규칙을 적용한다"는 사실을 코드에 직접 드러냅니다. 기존 함수가 이미 있을 때 특히 간결합니다.

### 단계 2: filter로 선택하기

```python
# basic usage
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# 기명 함수와 함께 사용
def is_positive(x: float) -> bool:
    return x > 0

values = [-3, -1, 0, 2, 5, -4, 8]
positives = list(filter(is_positive, values))
print(positives)  # [2, 5, 8]

# None은 falsy 값을 제거
mixed = [0, "", "hello", None, 42, [], "world"]
truthy = list(filter(None, mixed))
print(truthy)  # ['hello', 42, 'world']

# list comprehension 대안
evens_comp = [x for x in numbers if x % 2 == 0]
print(evens_comp)  # [2, 4, 6, 8, 10]
```

`filter`는 선택 규칙을 분리해 보여 주는 도구입니다. 어떤 항목을 남길지 명확할 때 읽기 좋습니다.

### 단계 3: reduce로 집계하기

```python
from functools import reduce

# sum
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 15

# 초기값과 함께 사용
total_with_init = reduce(lambda acc, x: acc + x, numbers, 100)
print(total_with_init)  # 115

# 최댓값(reduce 방식)
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5

# 중첩 리스트 평탄화
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda acc, lst: acc + lst, nested, [])
print(flat)  # [1, 2, 3, 4, 5, 6]

# 단어 빈도 계산
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = reduce(
    lambda acc, w: {**acc, w: acc.get(w, 0) + 1},
    words,
    {},
)
print(freq)  # {'apple': 3, 'banana': 2, 'cherry': 1}
```

`reduce`는 시퀀스를 하나의 결과로 압축하는 힘이 있지만, 그만큼 과도하게 쓰면 읽기 어려워집니다. 그래서 역할을 분명히 알고 절제해서 써야 합니다.

### 단계 4: 컴프리헨션과 map/filter 비교

```python
# 단순한 경우: comprehension이 더 Pythonic
numbers = [1, 2, 3, 4, 5]

# map + filter
result1 = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# comprehension — 가독성이 더 좋음
result2 = [x ** 2 for x in numbers if x % 2 == 0]

print(result1)  # [4, 16]
print(result2)  # [4, 16]

# map이 더 나은 경우: 기존 함수 적용
names = ["alice", "bob", "charlie"]

# map + 기존 method
upper1 = list(map(str.upper, names))

# comprehension
upper2 = [n.upper() for n in names]

print(upper1)  # ['ALICE', 'BOB', 'CHARLIE']
print(upper2)  # ['ALICE', 'BOB', 'CHARLIE']
# map이 약간 더 간결함
```

여기서 핵심은 우열이 아니라 선택 기준입니다. 간단한 변환과 필터링은 컴프리헨션이 더 Pythonic한 경우가 많고, 이미 존재하는 함수를 적용할 때는 `map`이 더 간결할 수 있습니다.

### 단계 5: 함께 조합해 실무 데이터 처리하기

```python
from functools import reduce

# 주문 데이터 처리
orders = [
    {"product": "Coffee", "quantity": 2, "price": 4500},
    {"product": "Cake", "quantity": 1, "price": 6000},
    {"product": "Juice", "quantity": 3, "price": 3000},
    {"product": "Cookie", "quantity": 5, "price": 1500},
    {"product": "Sandwich", "quantity": 1, "price": 5500},
]

# 1. 총액 계산(map)
with_total = list(map(
    lambda o: {**o, "total": o["quantity"] * o["price"]},
    orders,
))

# 2. 50달러 이상 주문 필터링(filter)
expensive = list(filter(lambda o: o["total"] >= 5000, with_total))

# 3. 전체 합계 계산(reduce)
grand_total = reduce(lambda acc, o: acc + o["total"], expensive, 0)

for o in expensive:
    print(f"  {o['product']}: ${o['total']:,}")
print(f"Grand total: ${grand_total:,}")
# Coffee: $9,000
# Cake: $6,000
# Juice: $9,000
# Cookie: $7,500
# Sandwich: $5,500
# Grand total: $37,000
```

이 세 함수를 함께 쓰면 변환 → 선택 → 집계라는 데이터 흐름이 코드에 그대로 드러납니다. 실무 데이터 처리 파이프라인이 읽기 좋아지는 이유가 바로 여기 있습니다.

## 이 코드에서 주목할 점

- `map`과 `filter`는 iterator를 반환하므로 지연 평가됩니다.
- 단순한 경우에는 컴프리헨션이 `map`/`filter`보다 더 Pythonic합니다.
- `reduce`는 안전하게 초기값을 함께 주는 습관이 중요합니다.
- 세 연산을 조합하면 복잡한 처리도 선언형으로 표현할 수 있습니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `reduce` 초기값을 생략함 | 빈 시퀀스에서 오류가 납니다 | 가능하면 항상 초기값을 제공합니다 |
| `map` 결과를 여러 번 순회함 | iterator는 한 번 소모되면 끝납니다 | `list()`로 변환하거나 다시 생성합니다 |
| `map`/`filter`를 너무 깊게 중첩함 | 가독성이 급격히 떨어집니다 | 컴프리헨션이나 중간 변수를 사용합니다 |
| 모든 집계를 `reduce`로 처리함 | `sum`, `max`보다 이해하기 어려워집니다 | 내장 함수가 있으면 우선 사용합니다 |
| 부수효과 있는 `lambda`를 사용함 | 실행 순서가 불명확해집니다 | 부수효과는 일반 루프에서 처리합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터 파이프라인에서 스키마 변환을 `map`으로 표현합니다.
- 검증 실패 항목 제거를 `filter`로 구현합니다.
- 요약 리포트 집계를 `reduce`나 적절한 내장 함수로 만듭니다.
- pandas의 `apply()`와 `query()`도 같은 사고방식 위에 있습니다.
- 큰 데이터는 generator expression과 함께 지연 처리합니다.

## 현업에서는 이렇게 판단합니다

Python에서는 컴프리헨션이 더 자연스러운 경우가 많습니다. 그렇다고 `map`/`filter`/`reduce` 개념이 덜 중요해지는 것은 아닙니다. 오히려 pandas, PySpark, SQL처럼 대규모 데이터 도구로 갈수록 같은 패턴이 더 자주 등장합니다.

특히 `reduce`는 의도를 명확히 드러낼 때만 쓰는 편이 좋습니다. `sum()`, `max()`, `min()`, `any()`, `all()` 같은 내장 함수가 이미 있다면 그쪽이 더 읽기 쉽습니다. 좋은 함수형 코드는 추상적이기보다 분명해야 합니다.

## 체크리스트

- [ ] `map`, `filter`, `reduce`의 차이를 코드로 설명할 수 있다
- [ ] 언제 컴프리헨션을 쓰고 언제 `map`/`filter`를 쓸지 판단할 수 있다
- [ ] `reduce`에 초기값을 안전하게 제공할 수 있다
- [ ] 세 연산을 조합해 데이터 파이프라인을 만들 수 있다
- [ ] `map`/`filter`가 iterator를 반환한다는 점을 이해한다

## 연습 문제

1. 학생 dict 목록에서 `map`으로 이름을 추출하고 `filter`로 90점 이상만 남겨 보세요.
2. 문자열 리스트를 `reduce`로 하나의 CSV 문자열로 합쳐 보세요.
3. 같은 작업을 `map`/`filter`/`reduce` 버전과 컴프리헨션 버전으로 각각 구현해 비교해 보세요.

## 정리와 다음 글

`map`, `filter`, `reduce`는 함수형 데이터 처리의 기본 도구입니다. Python에서는 컴프리헨션이 많은 자리를 대신하지만, 원리를 이해해야 도구를 넓게 선택할 수 있습니다. 다음 글에서는 외부 변수를 기억하는 함수인 **클로저와 partial**을 다룹니다.

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

## 추가 메모: reduce를 안전하게 쓰는 기준

`reduce`를 사용할 때는 반드시 초기값을 명시하고, 축약 연산이 결합법칙을 만족하는지 먼저 확인하는 편이 안전합니다. 이 기준을 지키면 빈 입력과 부분 집계 병합에서 버그가 크게 줄어듭니다.

```python
from functools import reduce

values = [3, 5, 7]
assert reduce(lambda a, b: a + b, values, 0) == 15
assert reduce(lambda a, b: a + b, [], 0) == 0
print("Pass")
```

### 체크 포인트 한 줄 요약

`map`은 변환, `filter`는 선택, `reduce`는 축약이라는 역할 경계를 끝까지 유지하면 파이프라인 디버깅 속도가 안정적으로 올라갑니다.

## 처음 질문으로 돌아가기

- **`map`, `filter`, `reduce`는 각각 어떤 역할을 맡을까요?**
  - 본문의 기준은 map, filter, reduce를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **반복문으로 쓰던 데이터를 선언형 파이프라인으로 어떻게 바꿀 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **리스트 컴프리헨션과 `map`/`filter`는 언제 각각 더 적합할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- **map, filter, reduce (현재 글)**
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Functions (map, filter)](https://docs.python.org/3/library/functions.html)
- [Python 공식 문서 — functools.reduce](https://docs.python.org/3/library/functools.html#functools.reduce)
- [Real Python — map, filter, reduce](https://realpython.com/python-map-function/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, map, filter, reduce
