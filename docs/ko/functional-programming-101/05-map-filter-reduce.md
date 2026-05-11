---
series: functional-programming-101
episode: 5
title: map, filter, reduce
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
  - map
  - filter
  - reduce
seo_description: map, filter, reduce의 원리와 리스트 컴프리헨션과의 비교를 다룹니다.
last_reviewed: '2026-05-04'
---

# map, filter, reduce

> Functional Programming 101 시리즈 (5/10)


## 이 글에서 다룰 문제

데이터 처리의 대부분은 "변환(map)", "선택(filter)", "집계(reduce)" 세 가지 패턴으로 나뉩니다. 이 세 가지를 익히면 대부분의 반복 로직을 간결하게 표현할 수 있습니다.

> map + filter + reduce = 데이터 처리의 기본 도구

Python에서는 리스트 컴프리헨션이 map/filter의 역할을 대체하는 경우가 많지만, 원리를 이해하면 적재적소에 더 나은 도구를 선택할 수 있습니다.

## 핵심 개념 잡기

> 세 연산의 역할

```
입력 리스트   [1, 2, 3, 4, 5]
              │
map(f)        [f(1), f(2), f(3), f(4), f(5)]    → 변환
filter(p)     [x for x if p(x)]                  → 선택
reduce(g)     g(g(g(g(x1, x2), x3), x4), x5)    → 집계
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| map | 각 원소에 함수를 적용하여 새 시퀀스를 생성합니다 |
| filter | 조건을 만족하는 원소만 선택합니다 |
| reduce | 시퀀스를 하나의 값으로 집계합니다 |
| 리스트 컴프리헨션 | Python의 선언적 리스트 생성 문법입니다 |
| 지연 평가(lazy evaluation) | map/filter는 iterator를 반환하여 필요할 때만 계산합니다 |

## Before / After

명령형 반복을 선언형으로 전환합니다.

```python
# before: 명령형 반복문
prices = [1200, 3400, 5600, 7800, 2300]
discounted = []
for p in prices:
    if p >= 3000:
        discounted.append(int(p * 0.9))
print(discounted)  # [3060, 5040, 7020]
```

```python
# after: map + filter 조합
prices = [1200, 3400, 5600, 7800, 2300]
discounted = list(map(
    lambda p: int(p * 0.9),
    filter(lambda p: p >= 3000, prices),
))
print(discounted)  # [3060, 5040, 7020]
```

## 단계별 실습

### Step 1: map — 변환

```python
# 기본 사용법
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25]

# 이름 있는 함수와 함께
def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

temps_c = [0, 20, 37, 100]
temps_f = list(map(celsius_to_fahrenheit, temps_c))
print(temps_f)  # [32.0, 68.0, 98.6, 212.0]

# 여러 시퀀스에 동시 적용
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)  # [11, 22, 33]

# 리스트 컴프리헨션 대안
squares_comp = [x ** 2 for x in numbers]
print(squares_comp)  # [1, 4, 9, 16, 25]
```

### Step 2: filter — 선택

```python
# 기본 사용법
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# 이름 있는 함수
def is_positive(x: float) -> bool:
    return x > 0

values = [-3, -1, 0, 2, 5, -4, 8]
positives = list(filter(is_positive, values))
print(positives)  # [2, 5, 8]

# None으로 falsy 값 제거
mixed = [0, "", "hello", None, 42, [], "world"]
truthy = list(filter(None, mixed))
print(truthy)  # ['hello', 42, 'world']

# 리스트 컴프리헨션 대안
evens_comp = [x for x in numbers if x % 2 == 0]
print(evens_comp)  # [2, 4, 6, 8, 10]
```

### Step 3: reduce — 집계

```python
from functools import reduce


# 합계
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 15

# 초기값 지정
total_with_init = reduce(lambda acc, x: acc + x, numbers, 100)
print(total_with_init)  # 115

# 최대값 (reduce 방식)
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

### Step 4: 컴프리헨션 vs map/filter

```python
# 간단한 경우: 컴프리헨션이 더 Pythonic
numbers = [1, 2, 3, 4, 5]

# map + filter
result1 = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# 컴프리헨션 — 더 읽기 쉬움
result2 = [x ** 2 for x in numbers if x % 2 == 0]

print(result1)  # [4, 16]
print(result2)  # [4, 16]


# map이 더 나은 경우: 이미 정의된 함수 적용
names = ["alice", "bob", "charlie"]

# map + 기존 메서드
upper1 = list(map(str.upper, names))

# 컴프리헨션
upper2 = [n.upper() for n in names]

print(upper1)  # ['ALICE', 'BOB', 'CHARLIE']
print(upper2)  # ['ALICE', 'BOB', 'CHARLIE']
# map이 약간 더 간결
```

### Step 5: 조합 활용 — 실전 데이터 처리

```python
from functools import reduce


# 주문 데이터 처리
orders = [
    {"product": "커피", "quantity": 2, "price": 4500},
    {"product": "케이크", "quantity": 1, "price": 6000},
    {"product": "주스", "quantity": 3, "price": 3000},
    {"product": "쿠키", "quantity": 5, "price": 1500},
    {"product": "샌드위치", "quantity": 1, "price": 5500},
]

# 1. 금액 계산 (map)
with_total = list(map(
    lambda o: {**o, "total": o["quantity"] * o["price"]},
    orders,
))

# 2. 5000원 이상 필터 (filter)
expensive = list(filter(lambda o: o["total"] >= 5000, with_total))

# 3. 총합 계산 (reduce)
grand_total = reduce(lambda acc, o: acc + o["total"], expensive, 0)

for o in expensive:
    print(f"  {o['product']}: {o['total']:,}원")
print(f"합계: {grand_total:,}원")
# 커피: 9,000원
# 케이크: 6,000원
# 주스: 9,000원
# 쿠키: 7,500원
# 샌드위치: 5,500원
# 합계: 37,000원
```

## 이 코드에서 주목할 점

- `map`과 `filter`는 iterator를 반환하므로 지연 평가됩니다
- 간단한 경우 리스트 컴프리헨션이 map/filter보다 Pythonic합니다
- `reduce`는 초기값을 항상 지정하는 것이 안전합니다
- 세 연산을 조합하면 복잡한 데이터 처리를 선언적으로 표현할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| reduce에 초기값 누락 | 빈 시퀀스에서 TypeError 발생합니다 | 항상 초기값을 지정합니다 |
| map 결과를 여러 번 순회 | iterator는 한 번만 순회 가능합니다 | `list()`로 변환하거나 다시 생성합니다 |
| 중첩된 map/filter | 가독성이 크게 떨어집니다 | 컴프리헨션이나 중간 변수를 사용합니다 |
| reduce로 모든 것을 해결 | 복잡한 reduce는 이해하기 어렵습니다 | `sum()`, `max()` 등 내장 함수를 사용합니다 |
| 부수효과 있는 lambda 사용 | map/filter의 함수는 순수해야 합니다 | 부수효과는 for 루프에서 처리합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터 파이프라인에서 map으로 스키마를 변환합니다
- 검증 실패 항목을 filter로 걸러냅니다
- 집계 보고서를 reduce로 생성합니다
- pandas의 `apply()`, `query()`가 같은 개념입니다
- 제너레이터 표현식으로 대용량 데이터를 지연 처리합니다

## 현업 개발자는 이렇게 생각합니다

Python에서는 map/filter보다 리스트 컴프리헨션이 관용적입니다. 하지만 map/filter/reduce의 개념을 아는 것은 매우 중요합니다. pandas, PySpark, SQL 모두 같은 패턴을 따르기 때문입니다.

`reduce`는 Python에서 `functools`로 이동될 만큼 남용되기 쉽습니다. `sum()`, `max()`, `min()`, `any()`, `all()` 같은 내장 함수가 있다면 그것을 사용하는 것이 더 명확합니다.

## 체크리스트

- [ ] map, filter, reduce의 차이를 코드로 보여줄 수 있다
- [ ] 리스트 컴프리헨션과 map/filter의 적절한 선택 기준을 알고 있다
- [ ] reduce에 초기값을 지정하여 안전하게 사용할 수 있다
- [ ] 세 연산을 조합하여 데이터 파이프라인을 구성할 수 있다
- [ ] map/filter가 iterator를 반환함을 이해하고 있다

## 정리 및 다음 글 안내

map, filter, reduce는 함수형 데이터 처리의 기본 도구입니다. Python에서는 리스트 컴프리헨션이 많은 경우를 대체하지만, 원리를 이해하면 더 넓은 도구를 활용할 수 있습니다. 다음 글에서는 함수 안에서 외부 변수를 기억하는 **클로저와 partial**을 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- **map, filter, reduce (현재 글)**
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Functions (map, filter)](https://docs.python.org/3/library/functions.html)
- [Python 공식 문서 — functools.reduce](https://docs.python.org/3/library/functools.html#functools.reduce)
- [Real Python — map, filter, reduce](https://realpython.com/python-map-function/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
