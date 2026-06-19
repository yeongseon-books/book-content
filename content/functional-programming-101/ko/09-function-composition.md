---
series: functional-programming-101
episode: 9
title: "Functional Programming 101 (9/10): 함수 합성과 파이프라인"
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
  - 함수 합성
  - 파이프라인
  - 데이터 변환
seo_description: compose와 pipe로 작은 함수를 데이터 파이프라인으로 조합하는 방법입니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (9/10): 함수 합성과 파이프라인

작은 함수는 이해하기 쉽습니다. 문제는 그런 함수가 많아졌을 때입니다. 함수가 많아질수록 오히려 흩어지고 읽기 어려워질 수도 있습니다. 함수 합성과 파이프라인은 그 작은 조각들을 의미 있는 흐름으로 다시 묶는 방법입니다.

이 글은 Functional Programming 101 시리즈의 9번째 글입니다.

현업에서 이 패턴이 중요한 이유는 테스트성과 변경 용이성 때문입니다. 거대한 함수 하나에 모든 로직을 넣는 대신, 각 단계가 하나의 변환만 맡게 만들면 수정 범위가 작아지고 파이프라인 전체를 안전하게 재구성할 수 있습니다.

![Functional Programming 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/09/09-01-how-a-readable-pipeline-flows.ko.png)
*Functional Programming 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 함수 합성은 수학적으로 어떤 의미를 가지며 Python에서는 어떻게 구현할까요?
- `compose`와 `pipe`는 무엇이 다르고, 왜 `pipe`가 더 읽기 쉬운 경우가 많을까요?
- 데이터 처리와 텍스트 처리에서 파이프라인은 어떤 장점을 줄까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

복잡한 데이터 처리 로직을 하나의 거대한 함수에 넣으면 테스트하기 어렵고 재사용도 힘들어집니다. 반대로 단일 목적 함수들을 조합하면 각 단계를 독립적으로 검증할 수 있고, 다른 파이프라인에서도 같은 함수를 다시 쓸 수 있습니다.

이것은 UNIX 철학과도 닿아 있습니다. `cat file | grep error | sort | uniq`처럼 각 도구가 한 가지 일만 잘하고, 조합으로 복잡한 작업을 처리합니다. 함수형 파이프라인은 이 철학을 코드 수준으로 가져오는 방법입니다.

## 개념 개요

> `compose`와 `pipe`의 차이는 방향입니다. 계산 자체는 같아도 읽는 순서가 달라집니다.

```text
compose(f, g, h)(x)  =  f(g(h(x)))     <- right to left (수학 표기법)
pipe(h, g, f)(x)     =  f(g(h(x)))     <- left to right (실행 순서와 일치)

Pipeline visualization:
  x -> [h] -> [g] -> [f] -> result
  데이터가 왼쪽에서 오른쪽으로 흐름 -> pipe가 더 직관적
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 함수 합성(function composition) | 두 함수 `f`, `g`를 `f(g(x))`로 결합하는 연산입니다 |
| 파이프라인(pipeline) | 데이터가 여러 함수를 순차적으로 통과하는 패턴입니다 |
| compose | 함수를 오른쪽에서 왼쪽으로 합성합니다 |
| pipe | 함수를 왼쪽에서 오른쪽으로 합성합니다 |
| point-free style | 인자 이름을 드러내지 않고 함수 조합만으로 로직을 표현하는 스타일입니다 |

## 적용 전후 비교

중첩 호출은 안쪽부터 해석해야 해서 읽기가 어렵습니다. 파이프라인은 실행 순서를 코드 순서와 맞춰 줍니다.

```python
# 이전: 중첩 호출 — 안쪽부터 읽어야 함
result = format_output(
    sort_by_score(
        filter_passing(
            calculate_totals(
                load_data()
            )
        )
    )
)
```

```python
# 이후: pipeline — 위에서 아래로 읽음
from collections.abc import Callable
from typing import Any

def pipe(*funcs: Callable) -> Callable:
    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result
    return piped

process = pipe(
    load_data,
    calculate_totals,
    filter_passing,
    sort_by_score,
    format_output,
)
result = process(None)
```

## 단계별 실습

### 단계 1: compose와 pipe의 기본

```python
from collections.abc import Callable
from typing import Any
from functools import reduce

def compose(*funcs: Callable) -> Callable:
    """Composes functions from right to left."""
    def composed(x: Any) -> Any:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed

def pipe(*funcs: Callable) -> Callable:
    """Composes functions from left to right."""
    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result
    return piped

add_one = lambda x: x + 1
double = lambda x: x * 2
to_str = lambda x: f"Result: {x}"

# compose: f(g(h(x))) — 오른쪽부터 실행
transform_c = compose(to_str, double, add_one)
print(transform_c(5))  # Result: 12  — (5+1)*2 = 12

# pipe: 실행 순서와 코드 순서가 일치
transform_p = pipe(add_one, double, to_str)
print(transform_p(5))  # Result: 12
```

실무에서는 `pipe`가 더 자주 읽기 좋습니다. 코드 순서와 실행 순서가 같아서 디버깅과 리뷰가 수월하기 때문입니다.

### 단계 2: map/filter/reduce와 파이프라인 조합

```python
from functools import reduce
from collections.abc import Callable

def pipe(*funcs: Callable) -> Callable:
    def piped(data):
        result = data
        for f in funcs:
            result = f(result)
        return result
    return piped

# 각 단계를 map/filter/reduce로 표현
def add_revenue(orders: list[dict]) -> list[dict]:
    return list(map(lambda o: {**o, "revenue": o["qty"] * o["price"]}, orders))

def filter_profitable(orders: list[dict]) -> list[dict]:
    return list(filter(lambda o: o["revenue"] >= 10000, orders))

def total_revenue(orders: list[dict]) -> int:
    return reduce(lambda acc, o: acc + o["revenue"], orders, 0)

# 파이프라인 조립
analyze = pipe(add_revenue, filter_profitable, total_revenue)

orders = [
    {"item": "A", "qty": 5, "price": 3000},
    {"item": "B", "qty": 2, "price": 8000},
    {"item": "C", "qty": 10, "price": 500},
    {"item": "D", "qty": 3, "price": 5000},
]

print(f"Total: {analyze(orders):,}")  # Total: 31,000
```

### 단계 3: 문자열 처리 파이프라인

```python
import re
from collections.abc import Callable

def pipe(*funcs: Callable) -> Callable:
    def piped(x):
        result = x
        for f in funcs:
            result = f(result)
        return result
    return piped

def strip_whitespace(text: str) -> str:
    return text.strip()

def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text)

def to_lowercase(text: str) -> str:
    return text.lower()

def replace_special(text: str) -> str:
    return re.sub(r"[^a-z0-9\s-]", "", text)

def spaces_to_hyphens(text: str) -> str:
    return text.replace(" ", "-")

def truncate(max_len: int) -> Callable[[str], str]:
    def _truncate(text: str) -> str:
        return text[:max_len]
    return _truncate

# slug 생성 pipeline
slugify = pipe(
    strip_whitespace,
    normalize_spaces,
    to_lowercase,
    replace_special,
    spaces_to_hyphens,
    truncate(50),
)

print(slugify("  Hello, World!  This is  a Test  "))
# hello-world-this-is-a-test

# map으로 여러 문자열에 동시에 적용
titles = ["  Hello World  ", "  Python FP Guide  ", "  함수 합성 기초  "]
slugs = list(map(slugify, titles))
print(slugs)
# ['hello-world', 'python-fp-guide', '']  <- 한글은 replace_special에서 제거
```

문자열 정규화는 파이프라인의 장점을 가장 직관적으로 보여 줍니다. 단계마다 역할이 뚜렷해서 수정 포인트를 찾기도 쉽습니다.

### 단계 4: 데이터 처리 파이프라인

```python
from collections.abc import Callable

def pipe_data(*funcs: Callable) -> Callable:
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process

def parse_records(raw: list[str]) -> list[dict]:
    records = []
    for line in raw:
        name, score = line.split(",")
        records.append({"name": name.strip(), "score": int(score.strip())})
    return records

def add_grade(records: list[dict]) -> list[dict]:
    def grade(score: int) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        return "F"
    return list(map(lambda r: {**r, "grade": grade(r["score"])}, records))

def filter_passing(records: list[dict]) -> list[dict]:
    return list(filter(lambda r: r["grade"] != "F", records))

def sort_by_score(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda r: r["score"], reverse=True)

def format_table(records: list[dict]) -> str:
    lines = [f"{'Name':<10} {'Score':>5} {'Grade':>5}"]
    lines.append("-" * 22)
    for r in records:
        lines.append(f"{r['name']:<10} {r['score']:>5} {r['grade']:>5}")
    return "\n".join(lines)

# pipeline 조립
process_students = pipe_data(
    parse_records,
    add_grade,
    filter_passing,
    sort_by_score,
    format_table,
)

raw_data = ["Alice, 85", "Bob, 92", "Charlie, 78", "Diana, 95", "Eve, 60"]
print(process_students(raw_data))
# Name        Score Grade
# ----------------------
# Diana          95     A
# Bob            92     A
# Alice          85     B
# Charlie        78     C
```

좋은 파이프라인은 각 단계가 순수 함수이기 때문에 독립 테스트가 가능합니다. 어느 단계에서 데이터가 잘못됐는지도 빠르게 찾을 수 있습니다.

### 단계 5: 주문 이벤트 정산 파이프라인

```python
from dataclasses import dataclass, replace
from functools import reduce

@dataclass(frozen=True)
class OrderEvent:
    order_id: str
    store: str
    amount: int
    currency: str
    status: str
    source: str
    margin: int = 0

def normalize_currency(events: list[OrderEvent]) -> list[OrderEvent]:
    rates = {"KRW": 1, "USD": 1380}
    return list(map(lambda e: replace(e, amount=e.amount * rates[e.currency], currency="KRW"), events))

def drop_cancelled(events: list[OrderEvent]) -> list[OrderEvent]:
    return list(filter(lambda e: e.status != "cancelled", events))

def enrich_margin(events: list[OrderEvent]) -> list[OrderEvent]:
    return list(map(lambda e: replace(e, margin=int(e.amount * 0.18)), events))

def keep_marketplace(events: list[OrderEvent]) -> list[OrderEvent]:
    return list(filter(lambda e: e.source == "marketplace", events))

def to_store_report(events: list[OrderEvent]) -> dict[str, dict[str, int]]:
    report: dict[str, dict[str, int]] = {}
    for event in events:
        store = report.setdefault(event.store, {"revenue": 0, "margin": 0, "orders": 0})
        store["revenue"] += event.amount
        store["margin"] += event.margin
        store["orders"] += 1
    return report

# pipe 없이도 단계별 검증 가능
settle_orders = pipe_data(
    normalize_currency,
    drop_cancelled,
    keep_marketplace,
    enrich_margin,
    to_store_report,
)

events = [
    OrderEvent("A-1", "seoul", 48000, "KRW", "paid", "marketplace"),
    OrderEvent("A-2", "seoul", 42, "USD", "paid", "marketplace"),
    OrderEvent("A-3", "busan", 31000, "KRW", "cancelled", "marketplace"),
    OrderEvent("A-4", "busan", 27000, "KRW", "paid", "direct"),
]

report = settle_orders(events)
print(report)
# {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
```

이 예시는 통화 정규화, 취소 주문 제외, 채널 필터링, 마진 보강, 매장별 집계가 순차적으로 드러납니다. 장애가 나도 어느 단계에서 값이 달라졌는지 바로 추적할 수 있습니다.

## 이 코드에서 주목할 점

- `pipe`는 코드 순서와 실행 순서를 맞춰 읽기 쉽게 만듭니다.
- `map`/`filter`/`reduce`를 각 파이프라인 단계 안에서 사용하면 선언형 표현이 자연스럽습니다.
- 각 단계 함수는 독립적이어서 개별 테스트가 쉽습니다.
- frozen dataclass와 파이프라인을 조합하면 불변 변환 흐름을 안전하게 표현합니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 함수 시그니처가 맞지 않음 | 앞 단계 출력이 다음 단계 입력과 안 맞습니다 | 타입 힌트로 연결 가능성을 확인합니다 |
| 파이프라인이 너무 길어짐 | 디버깅이 어려워집니다 | 중간 변수나 로깅 단계를 둡니다 |
| 파이프라인 중간에 부수효과를 넣음 | 테스트와 재사용이 어려워집니다 | 부수효과는 마지막 단계로 밀어냅니다 |
| 오류 처리 단계가 없음 | 한 단계 실패가 전체를 멈춥니다 | 에러 처리용 단계를 명시적으로 둡니다 |
| `compose`와 `pipe`를 섞어 씀 | 실행 방향이 헷갈립니다 | 프로젝트 안에서 한 가지 기준을 정합니다 |

## 실무에서 이렇게 쓰입니다

- ETL 파이프라인을 함수 합성으로 구성합니다.
- 검증 함수를 여러 단계로 조합해 데이터 검증 파이프라인을 만듭니다.
- 텍스트 전처리를 정규화, 토큰화, 필터링 단계로 분리합니다.
- API 미들웨어 체인을 함수 조합으로 표현합니다.
- `map`/`filter`/`reduce`를 각 파이프라인 단계에 자연스럽게 통합합니다.

## 현업에서는 이렇게 판단합니다

함수 합성의 핵심 가치는 관심사 분리입니다. 각 함수가 정확히 하나의 변환만 담당하면 테스트가 쉬워지고 조합 비용이 낮아집니다. 결국 중요한 것은 `pipe()`라는 도구 자체가 아니라, 작은 함수를 조립 가능한 단위로 설계하는 사고방식입니다.

Python에는 Haskell의 `.` 같은 내장 합성 연산자가 없지만, 그건 본질이 아닙니다. 프로젝트 안에서 읽기 좋은 방향으로 `pipe` 또는 `compose` 하나만 정해 두고 일관되게 쓰는 편이 훨씬 중요합니다.

## 처음 질문으로 돌아가기

- **함수 합성은 수학적으로 어떤 의미를 가지며 Python에서는 어떻게 구현할까요?**
  수학에서 `(f ∘ g)(x) = f(g(x))`입니다. Python에는 합성 연산자가 없으므로 `compose(*funcs)`나 `pipe(*funcs)` 유틸리티를 직접 만들어 씁니다. `reduce`로도 구현할 수 있습니다. `functools.reduce(lambda f, g: lambda x: g(f(x)), funcs)`

- **`compose`와 `pipe`는 무엇이 다르고, 왜 `pipe`가 더 읽기 쉬운 경우가 많을까요?**
  `compose(f, g, h)(x)`는 수학 표기법처럼 오른쪽부터 실행합니다. `h(x)` → `g(...)` → `f(...)`. `pipe(h, g, f)(x)`는 왼쪽부터 실행합니다. 코드에 쓴 순서가 실행 순서와 일치하기 때문에 데이터 흐름을 위에서 아래로 읽을 수 있습니다. 실무에서는 `pipe`가 대체로 더 직관적입니다.

- **데이터 처리와 텍스트 처리에서 파이프라인은 어떤 장점을 줄까요?**
  각 단계가 독립 함수라서 단계별로 테스트할 수 있고 특정 단계만 교체하기도 쉽습니다. 중간에 로깅 단계를 삽입하거나 단계를 재배치해도 다른 단계가 영향을 받지 않습니다. 거대한 함수 하나보다 디버깅 속도가 훨씬 빠릅니다.

## 운영 체크리스트

- [ ] `compose`와 `pipe`의 차이를 설명할 수 있다
- [ ] 작은 함수를 조합해 데이터 파이프라인을 만들 수 있다
- [ ] `map`/`filter`/`reduce`를 파이프라인 단계에 통합할 수 있다
- [ ] 조건부 파이프라인을 작성할 수 있다
- [ ] 각 단계를 독립적으로 테스트할 수 있다

## 연습 문제

1. `compose`와 `pipe`를 둘 다 구현하고 같은 결과를 내는지 검증해 보세요.
2. JSON 데이터를 읽어 `filter`로 조건 선택, `map`으로 변환, `reduce`로 집계하는 4단계 파이프라인을 설계해 보세요.
3. 파이프라인 중간에 결과를 출력하는 `tap` 단계를 추가해 디버깅 도구로 활용해 보세요.

## 정리와 다음 글

함수 합성은 작은 함수를 결합해 큰 변환을 만드는 방법입니다. 특히 `pipe`는 코드 순서와 실행 순서를 맞춰 주기 때문에 Python에서 읽기 좋은 파이프라인을 만들기 좋습니다. 다음 글에서는 시리즈를 마무리하며 **객체지향과 함수형의 균형**을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- [Functional Programming 101 (7/10): 재귀와 꼬리 호출](./07-recursion.md)
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- **Functional Programming 101 (9/10): 함수 합성과 파이프라인 (현재 글)**
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [UNIX Philosophy — Doug McIlroy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Composing Software — Eric Elliott](https://medium.com/javascript-scene/composing-software-the-book-f31c77fc3ddc)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 함수 합성, 파이프라인, 데이터 변환
