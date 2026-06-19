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

이 글은 Functional Programming 101 시리즈의 5번째 글입니다.

Python에서는 리스트 컴프리헨션이 더 자주 쓰이기 때문에 이 세 함수를 낡은 문법처럼 오해하기도 합니다. 하지만 개념 자체는 여전히 중요합니다. pandas, SQL, Spark 같은 도구를 이해할 때도 결국 같은 사고방식이 반복되기 때문입니다.

![Functional Programming 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/05/05-01-big-picture.ko.png)
*Functional Programming 101 5장 흐름 개요*

## 이 글에서 다룰 문제

- `map`, `filter`, `reduce`는 각각 어떤 역할을 맡을까요?
- 반복문으로 쓰던 데이터를 선언형 파이프라인으로 어떻게 바꿀 수 있을까요?
- 리스트 컴프리헨션과 `map`/`filter`는 언제 각각 더 적합할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

실무 데이터 처리의 대부분은 세 가지 패턴으로 압축됩니다. 값을 다른 형태로 바꾸거나, 조건에 맞는 항목만 고르거나, 여러 항목을 하나의 결과로 합칩니다. 이 세 가지를 명확히 구분해 표현할 수 있으면 반복 로직이 훨씬 간결해집니다.

Python에서는 단순한 경우 컴프리헨션이 더 관용적이지만, 도구 선택은 개념 이해 위에 서야 합니다. 어떤 상황에서 무엇이 더 읽기 쉬운지 판단하려면 먼저 역할 자체를 분리해 볼 수 있어야 합니다.

## 개념 개요

> 세 함수는 모두 반복을 숨기지만, 무엇을 하려는지는 서로 다릅니다.

```text
Input list    [1, 2, 3, 4, 5]
              |
map(f)        [f(1), f(2), f(3), f(4), f(5)]    -> transform each element
filter(p)     [x for x in input if p(x)]         -> select matching elements
reduce(g)     g(g(g(g(x1, x2), x3), x4), x5)    -> aggregate to one value
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
# 이전: 명령형 loop — 변환과 선택이 뒤섞임
prices = [1200, 3400, 5600, 7800, 2300]
discounted = []
for p in prices:
    if p >= 3000:
        discounted.append(int(p * 0.9))
print(discounted)  # [3060, 5040, 7020]
```

```python
# 이후: filter로 선택, map으로 변환 — 역할이 분리됨
prices = [1200, 3400, 5600, 7800, 2300]

eligible = filter(lambda p: p >= 3000, prices)          # 선택
discounted = list(map(lambda p: int(p * 0.9), eligible))  # 변환

print(discounted)  # [3060, 5040, 7020]
```

## 단계별 실습

### 단계 1: map으로 변환하기

```python
# 기본 사용
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

# 기존 메서드를 그대로 넘기기
names = ["alice", "BOB", "charlie"]
normalized = list(map(str.lower, names))
print(normalized)  # ['alice', 'bob', 'charlie']
```

`map`은 "모든 원소에 같은 규칙을 적용한다"는 사실을 코드에 직접 드러냅니다. 기존 함수가 이미 있을 때 특히 간결합니다.

### 단계 2: filter로 선택하기

```python
# 기본 사용
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

# 딕셔너리 목록 필터링
products = [
    {"name": "A", "stock": 10},
    {"name": "B", "stock": 0},
    {"name": "C", "stock": 5},
]
in_stock = list(filter(lambda p: p["stock"] > 0, products))
print([p["name"] for p in in_stock])  # ['A', 'C']
```

`filter`는 선택 규칙을 분리해 보여 주는 도구입니다. 어떤 항목을 남길지 명확할 때 읽기 좋습니다.

### 단계 3: reduce로 집계하기

```python
from functools import reduce

# 합계
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda acc, x: acc + x, numbers, 0)
print(total)  # 15

# 초기값은 항상 제공하는 습관
total_with_init = reduce(lambda acc, x: acc + x, numbers, 100)
print(total_with_init)  # 115

# 최댓값 (내장 max보다 이해에 집중)
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
numbers = [1, 2, 3, 4, 5]

# map + filter 조합
result1 = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# comprehension — 단순한 경우 더 가독성이 좋음
result2 = [x ** 2 for x in numbers if x % 2 == 0]

print(result1)  # [4, 16]
print(result2)  # [4, 16]

# map이 더 나은 경우: 기존 함수 적용
names = ["alice", "bob", "charlie"]

# map + 기존 method — lambda 불필요
upper1 = list(map(str.upper, names))

# comprehension
upper2 = [n.upper() for n in names]

print(upper1)  # ['ALICE', 'BOB', 'CHARLIE']
print(upper2)  # ['ALICE', 'BOB', 'CHARLIE']

# 판단 기준: 기존 함수가 있으면 map, 조건+변환이 간단하면 comprehension
```

핵심은 우열이 아니라 선택 기준입니다. 간단한 변환과 필터링은 컴프리헨션이 더 Pythonic한 경우가 많고, 이미 존재하는 함수를 적용할 때는 `map`이 더 간결할 수 있습니다.

### 단계 5: 세 연산을 조합해 실무 데이터 처리하기

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

# 1. map: 총액 계산
with_total = list(map(
    lambda o: {**o, "total": o["quantity"] * o["price"]},
    orders,
))

# 2. filter: 5000원 이상 주문
expensive = list(filter(lambda o: o["total"] >= 5000, with_total))

# 3. reduce: 전체 합계
grand_total = reduce(lambda acc, o: acc + o["total"], expensive, 0)

for o in expensive:
    print(f"  {o['product']}: {o['total']:,}원")
print(f"합계: {grand_total:,}원")
# Coffee: 9,000원
# Cake: 6,000원
# Juice: 9,000원
# Cookie: 7,500원
# Sandwich: 5,500원
# 합계: 37,000원
```

이 세 함수를 함께 쓰면 변환 → 선택 → 집계라는 데이터 흐름이 코드에 그대로 드러납니다. 실무 데이터 처리 파이프라인이 읽기 좋아지는 이유가 바로 여기 있습니다.

### 단계 6: reduce를 안전하게 쓰는 기준

```python
from functools import reduce

# 빈 시퀀스에서 초기값의 중요성
values = [3, 5, 7]
assert reduce(lambda a, b: a + b, values, 0) == 15
assert reduce(lambda a, b: a + b, [], 0) == 0  # 초기값 없으면 오류

# 결합법칙을 만족하는 연산: 병렬 분산 처리에 안전
# (a + b) + c == a + (b + c) ✓
# (a - b) - c != a - (b - c) ✗  <- reduce로 조심해야 함

# 딕셔너리 병합 (초기값 필수)
configs = [{"a": 1}, {"b": 2}, {"c": 3}]
merged = reduce(lambda acc, d: {**acc, **d}, configs, {})
print(merged)  # {'a': 1, 'b': 2, 'c': 3}

# 내장 함수로 대체 가능한 경우는 내장 함수를 우선
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print(sum(numbers))  # 31 — reduce(lambda a,b: a+b, numbers, 0)보다 명확
print(max(numbers))  # 9  — reduce(lambda a,b: a if a>b else b, numbers)보다 명확
```

`reduce`를 사용할 때는 반드시 초기값을 명시하고, 내장 함수로 표현 가능하면 내장 함수를 우선하는 것이 좋습니다.

### 단계 7: `map`/`filter`/`reduce`로 보고서 파이프라인 만들기

실제 업무에 가까운 예시로 세 연산이 어떻게 유기적으로 연결되는지 확인합니다.

```python
from functools import reduce

# 월간 거래 내역
transactions = [
    {"date": "2026-06-01", "type": "sale",   "amount": 150_000, "region": "seoul"},
    {"date": "2026-06-03", "type": "refund",  "amount":  20_000, "region": "busan"},
    {"date": "2026-06-07", "type": "sale",   "amount": 320_000, "region": "seoul"},
    {"date": "2026-06-10", "type": "sale",   "amount":  80_000, "region": "daegu"},
    {"date": "2026-06-15", "type": "refund",  "amount":  15_000, "region": "seoul"},
    {"date": "2026-06-20", "type": "sale",   "amount": 540_000, "region": "seoul"},
]

# 단계 1 — filter: 판매 거래만
sales = filter(lambda t: t["type"] == "sale", transactions)

# 단계 2 — filter: 서울 지역만
seoul_sales = filter(lambda t: t["region"] == "seoul", sales)

# 단계 3 — map: 부가세(10%) 포함 금액 계산
with_vat = map(lambda t: {**t, "total": t["amount"] * 1.1}, seoul_sales)

# 단계 4 — reduce: 총 매출 합산
total = reduce(lambda acc, t: acc + t["total"], with_vat, 0)

print(f"서울 판매 부가세 포함 총액: {total:,.0f}원")
# 서울 판매 부가세 포함 총액: 1,111,000원

# 지역별 집계로 확장 — reduce로 dict 누적
region_totals = reduce(
    lambda acc, t: {**acc, t["region"]: acc.get(t["region"], 0) + t["amount"]},
    filter(lambda t: t["type"] == "sale", transactions),
    {},
)
print(region_totals)
# {'seoul': 1_010_000, 'daegu': 80_000}
```

이 파이프라인에서 각 단계는 이전 단계의 결과만 받고 다음으로 넘깁니다. 중간 변수를 쓴 것은 가독성을 위한 선택이지 필수가 아닙니다. `filter` → `filter` → `map` → `reduce`로 이어지는 구성은 SQL의 `WHERE` → `SELECT` → `GROUP BY` 흐름과 같은 사고입니다.

## 이 코드에서 주목할 점

- `map`과 `filter`는 iterator를 반환하므로 지연 평가됩니다.
- 단순한 경우에는 컴프리헨션이 `map`/`filter`보다 더 Pythonic합니다.
- `reduce`는 안전하게 초기값을 함께 주는 습관이 중요합니다.
- 세 연산을 조합하면 복잡한 처리도 선언형으로 표현할 수 있습니다.
- `reduce`로 dict를 누적하면 `GROUP BY` 스타일 집계를 표현할 수 있습니다.

## 자주 하는 실수

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

## 처음 질문으로 돌아가기

- **`map`, `filter`, `reduce`는 각각 어떤 역할을 맡을까요?**
  `map`은 "모든 원소를 같은 규칙으로 변환"합니다. `filter`는 "조건을 만족하는 원소만 선택"합니다. `reduce`는 "여러 원소를 하나의 값으로 축약"합니다. 세 역할을 분리해서 생각하는 것이 핵심입니다.

- **반복문으로 쓰던 데이터를 선언형 파이프라인으로 어떻게 바꿀 수 있을까요?**
  반복문 안에서 "이 줄은 무엇을 하는가"를 묻고, 변환이면 `map`, 선택이면 `filter`, 집계면 `reduce`로 분리합니다. 단계가 명확히 나뉘면 코드가 읽는 방향과 데이터가 흐르는 방향이 일치해 집니다.

- **리스트 컴프리헨션과 `map`/`filter`는 언제 각각 더 적합할까요?**
  이미 이름 있는 함수가 있을 때는 `map(func, data)`가 더 간결합니다. 변환과 조건이 간단하고 새로 lambda를 써야 할 때는 `[expr for x in data if cond]` 컴프리헨션이 더 읽기 쉽습니다. `map`과 `filter`를 두 단계 이상 중첩해야 한다면 컴프리헨션을 먼저 고려합니다.

## 운영 체크리스트

- [ ] `map`, `filter`, `reduce`의 차이를 코드로 설명할 수 있다
- [ ] 언제 컴프리헨션을 쓰고 언제 `map`/`filter`를 쓸지 판단할 수 있다
- [ ] `reduce`에 초기값을 안전하게 제공할 수 있다
- [ ] 세 연산을 조합해 데이터 파이프라인을 만들 수 있다
- [ ] `map`/`filter`가 iterator를 반환한다는 점을 이해한다

## 연습 문제

1. 학생 dict 목록에서 `map`으로 이름을 추출하고 `filter`로 90점 이상만 남긴 뒤 `reduce`로 평균을 구해 보세요.
2. 문자열 리스트를 `reduce`로 하나의 CSV 문자열로 합쳐 보세요.
3. 같은 작업을 `map`/`filter`/`reduce` 버전과 컴프리헨션 버전으로 각각 구현해 비교해 보세요.

## 정리와 다음 글

`map`, `filter`, `reduce`는 함수형 데이터 처리의 기본 도구입니다. Python에서는 컴프리헨션이 많은 자리를 대신하지만, 원리를 이해해야 도구를 넓게 선택할 수 있습니다. 다음 글에서는 외부 변수를 기억하는 함수인 **클로저와 partial**을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- **Functional Programming 101 (5/10): map, filter, reduce (현재 글)**
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- [Functional Programming 101 (7/10): 재귀와 꼬리 호출](./07-recursion.md)
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [Functional Programming 101 (9/10): 함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Functions (map, filter)](https://docs.python.org/3/library/functions.html)
- [Python 공식 문서 — functools.reduce](https://docs.python.org/3/library/functools.html#functools.reduce)
- [Real Python — map, filter, reduce](https://realpython.com/python-map-function/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, map, filter, reduce
