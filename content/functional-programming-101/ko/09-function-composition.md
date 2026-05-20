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

이 글은 Functional Programming 101 시리즈의 아홉 번째 글입니다.

작은 함수는 이해하기 쉽습니다. 문제는 그런 함수가 많아졌을 때입니다. 함수가 많아질수록 오히려 흩어지고 읽기 어려워질 수도 있습니다. 함수 합성과 파이프라인은 그 작은 조각들을 의미 있는 흐름으로 다시 묶는 방법입니다.

현업에서 이 패턴이 중요한 이유는 테스트성과 변경 용이성 때문입니다. 거대한 함수 하나에 모든 로직을 넣는 대신, 각 단계가 하나의 변환만 맡게 만들면 수정 범위가 작아지고 파이프라인 전체를 안전하게 재구성할 수 있습니다.

## 먼저 던지는 질문

- 함수 합성은 수학적으로 어떤 의미를 가지며 Python에서는 어떻게 구현할까요?
- `compose`와 `pipe`는 무엇이 다르고, 왜 `pipe`가 더 읽기 쉬운 경우가 많을까요?
- 데이터 처리와 텍스트 처리에서 파이프라인은 어떤 장점을 줄까요?

## 큰 그림

![Functional Programming 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/09/09-01-how-a-readable-pipeline-flows.ko.png)

*Functional Programming 101 9장 흐름 개요*

이 그림에서는 함수 합성과 파이프라인를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 함수 합성과 파이프라인의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

복잡한 데이터 처리 로직을 하나의 거대한 함수에 넣으면 테스트하기 어렵고 재사용도 힘들어집니다. 반대로 단일 목적 함수들을 조합하면 각 단계를 독립적으로 검증할 수 있고, 다른 파이프라인에서도 같은 함수를 다시 쓸 수 있습니다.

이것은 UNIX 철학과도 닿아 있습니다. `cat file | grep error | sort | uniq`처럼 각 도구가 한 가지 일만 잘하고, 조합으로 복잡한 작업을 처리합니다. 함수형 파이프라인은 이 철학을 코드 수준으로 가져오는 방법입니다.

## 개념 개요

> `compose`와 `pipe`의 차이는 방향입니다. 계산 자체는 같아도 읽는 순서가 달라집니다.

```text
compose(f, g, h)(x)  =  f(g(h(x)))     <- right to left
pipe(h, g, f)(x)     =  f(g(h(x)))     <- left to right

Pipeline visualization:
  x -> [h] -> [g] -> [f] -> result
```

## 파이프라인이 읽히는 방식

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 함수 합성(function composition) | 두 함수 `f`, `g`를 `f(g(x))`로 결합하는 연산입니다 |
| 파이프라인(pipeline) | 데이터가 여러 함수를 순차적으로 통과하는 패턴입니다 |
| compose | 함수를 오른쪽에서 왼쪽으로 합성합니다 |
| pipe | 함수를 왼쪽에서 오른쪽으로 합성합니다 |
| point-free style | 인자 이름을 드러내지 않고 함수 조합만으로 로직을 표현하는 스타일입니다 |

## Before / After

중첩 호출은 안쪽부터 해석해야 해서 읽기가 어렵습니다. 파이프라인은 실행 순서를 코드 순서와 맞춰 줍니다.

```python
# before: nested calls — read from inside out
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
# after: pipeline — read top to bottom
result = pipe(
    load_data,
    calculate_totals,
    filter_passing,
    sort_by_score,
    format_output,
)()
```

## 단계별 실습

### Step 1: compose와 pipe의 기본

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

# compose: f(g(h(x)))
add_one = lambda x: x + 1
double = lambda x: x * 2
to_str = lambda x: f"Result: {x}"

transform_c = compose(to_str, double, add_one)
print(transform_c(5))  # Result: 12  — (5+1)*2 = 12

# pipe: read order matches execution order
transform_p = pipe(add_one, double, to_str)
print(transform_p(5))  # Result: 12
```

실무에서는 `pipe`가 더 자주 읽기 좋습니다. 코드 순서와 실행 순서가 같아서 디버깅과 리뷰가 수월하기 때문입니다.

### Step 2: 문자열 처리 파이프라인

```python
import re

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

def truncate(max_len: int):
    def _truncate(text: str) -> str:
        return text[:max_len]
    return _truncate

# slug generation pipeline
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

print(slugify("  Functional Programming — A Composition Guide  "))
# functional-programming--a-composition-guide
```

문자열 정규화는 파이프라인의 장점을 가장 직관적으로 보여 줍니다. 단계마다 역할이 뚜렷해서 수정 포인트를 찾기도 쉽습니다.

### Step 3: 데이터 처리 파이프라인

```python
from collections.abc import Callable

def pipe_data(*funcs: Callable) -> Callable:
    """Data processing pipeline."""
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process

# define each stage as an independent function
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
    return [{**r, "grade": grade(r["score"])} for r in records]

def filter_passing(records: list[dict]) -> list[dict]:
    return [r for r in records if r["grade"] != "F"]

def sort_by_score(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda r: r["score"], reverse=True)

def format_table(records: list[dict]) -> str:
    lines = [f"{'Name':<10} {'Score':>5} {'Grade':>5}"]
    lines.append("-" * 22)
    for r in records:
        lines.append(f"{r['name']:<10} {r['score']:>5} {r['grade']:>5}")
    return "\n".join(lines)

# assemble the pipeline
process_students = pipe_data(
    parse_records,
    add_grade,
    filter_passing,
    sort_by_score,
    format_table,
)

# execute
raw_data = [
    "Alice, 85",
    "Bob, 92",
    "Charlie, 78",
    "Diana, 95",
    "Eve, 60",
]

print(process_students(raw_data))
# Name        Score Grade
# ----------------------
# Diana          95     A
# Bob            92     A
# Alice          85     B
# Charlie        78     C
```

좋은 파이프라인은 각 단계가 순수 함수이기 때문에 독립 테스트가 가능합니다. 어느 단계에서 데이터가 잘못됐는지도 빠르게 찾을 수 있습니다.

### Step 4: 제너레이터 파이프라인

```python
from collections.abc import Callable
from typing import Iterator

def gen_pipe(*funcs: Callable) -> Callable:
    """Generator-based lazy pipeline."""
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process

def lines(text: str) -> Iterator[str]:
    for line in text.strip().split("\n"):
        yield line

def strip_lines(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        yield line.strip()

def skip_empty(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        if line:
            yield line

def skip_comments(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        if not line.startswith("#"):
            yield line

def to_upper(it: Iterator[str]) -> Iterator[str]:
    for line in it:
        yield line.upper()

# assemble the lazy pipeline
clean_text = gen_pipe(
    strip_lines,
    skip_empty,
    skip_comments,
    to_upper,
)

text = """
  # config file
  host = localhost

  port = 8080

  # debug mode
  debug = true
"""

for line in clean_text(lines(text)):
    print(line)
# HOST = LOCALHOST
# PORT = 8080
# DEBUG = TRUE
```

파이프라인은 eager 데이터에만 쓰는 패턴이 아닙니다. generator와 결합하면 큰 입력도 메모리 효율적으로 처리할 수 있습니다.

### Step 5: 조건부 파이프라인

```python
from collections.abc import Callable
from typing import Any

def conditional(
    predicate: Callable[[Any], bool],
    if_true: Callable,
    if_false: Callable | None = None,
) -> Callable:
    """Applies different functions based on a condition."""
    def apply(value: Any) -> Any:
        if predicate(value):
            return if_true(value)
        return if_false(value) if if_false else value
    return apply

def when(predicate: Callable[[Any], bool], func: Callable) -> Callable:
    """Applies a function only when the condition is true."""
    return conditional(predicate, func)

# pipeline with conditional steps
process = pipe(
    lambda x: x.strip(),
    when(lambda x: x.startswith("http"), lambda x: x.replace("http://", "https://")),
    lambda x: x.lower(),
    when(lambda x: len(x) > 30, lambda x: x[:27] + "..."),
)

print(process("  http://Example.COM/Very-Long-Path-Name-Here  "))
# https://example.com/very-l...
print(process("  Short URL  "))
# short url
```

조건부 단계까지 조합할 수 있으면 파이프라인은 단순 직선 구조를 넘어서도 충분히 실용적이 됩니다.

## 실무 예시: 주문 이벤트 정산 파이프라인

```python
from dataclasses import dataclass, replace

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
    return [replace(e, amount=e.amount * rates[e.currency], currency="KRW") for e in events]

def drop_cancelled(events: list[OrderEvent]) -> list[OrderEvent]:
    return [e for e in events if e.status != "cancelled"]

def enrich_margin(events: list[OrderEvent]) -> list[OrderEvent]:
    return [replace(e, margin=int(e.amount * 0.18)) for e in events]

def keep_marketplace(events: list[OrderEvent]) -> list[OrderEvent]:
    return [e for e in events if e.source == "marketplace"]

def to_store_report(events: list[OrderEvent]) -> dict[str, dict[str, int]]:
    report: dict[str, dict[str, int]] = {}
    for event in events:
        store = report.setdefault(event.store, {"revenue": 0, "margin": 0, "orders": 0})
        store["revenue"] += event.amount
        store["margin"] += event.margin
        store["orders"] += 1
    return report

settle_orders = pipe(
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

normalized = normalize_currency(events)
assert [(e.order_id, e.amount, e.currency) for e in normalized] == [
    ("A-1", 48000, "KRW"),
    ("A-2", 57960, "KRW"),
    ("A-3", 31000, "KRW"),
    ("A-4", 27000, "KRW"),
]

active = drop_cancelled(normalized)
assert [e.order_id for e in active] == ["A-1", "A-2", "A-4"]

marketplace_only = keep_marketplace(active)
assert [e.order_id for e in marketplace_only] == ["A-1", "A-2"]

with_margin = enrich_margin(marketplace_only)
assert [(e.order_id, e.margin) for e in with_margin] == [
    ("A-1", 8640),
    ("A-2", 10432),
]

report = to_store_report(with_margin)
assert report == {
    "seoul": {"revenue": 105960, "margin": 19072, "orders": 2}
}

print("Normalized IDs:", [e.order_id for e in normalized])
print("After cancellation filter:", [e.order_id for e in active])
print("Marketplace IDs:", [e.order_id for e in marketplace_only])
print("Store report:", report)

print("Pipeline report:", settle_orders(events))
# Normalized IDs: ['A-1', 'A-2', 'A-3', 'A-4']
# After cancellation filter: ['A-1', 'A-2', 'A-4']
# Marketplace IDs: ['A-1', 'A-2']
# Store report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
# Pipeline report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
```

이 예시는 장난감 문자열 변환보다 실무에 더 가깝습니다. 통화 정규화, 취소 주문 제외, 채널 필터링, 마진 보강, 매장별 집계가 순차적으로 드러나기 때문에, 장애가 나도 어느 단계에서 값이 달라졌는지 바로 추적할 수 있습니다.

#### 예상 출력

```text
Normalized IDs: ['A-1', 'A-2', 'A-3', 'A-4']
After cancellation filter: ['A-1', 'A-2', 'A-4']
Marketplace IDs: ['A-1', 'A-2']
Store report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
Pipeline report: {'seoul': {'revenue': 105960, 'margin': 19072, 'orders': 2}}
```

#### 결과가 다르면 먼저 확인할 점

- USD 환율이 `1380`인지 확인합니다. 여기 값이 달라지면 `A-2` 금액과 최종 집계가 모두 달라집니다.
- `drop_cancelled()`가 `cancelled` 상태를 정확히 제외하는지 확인합니다. `A-3`가 남아 있으면 부산 매장이 보고서에 등장합니다.
- `keep_marketplace()`가 `source == "marketplace"`만 남기는지 확인합니다. `A-4`가 남아 있으면 direct 주문이 섞입니다.
- 마진 공식이 `int(e.amount * 0.18)`인지 확인합니다. 반올림 방식이 달라지면 `19072`가 맞지 않을 수 있습니다.

## 이 코드에서 주목할 점

- `pipe`는 코드 순서와 실행 순서를 맞춰 읽기 쉽게 만듭니다.
- 각 단계 함수는 독립적이어서 개별 테스트가 쉽습니다.
- generator 파이프라인은 큰 데이터를 메모리 효율적으로 처리합니다.
- 조건부 파이프라인은 분기 로직도 선언형으로 표현하게 해 줍니다.

## 흔한 실수 5가지

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
- CI/CD 각 단계를 독립 함수처럼 설계하는 데 같은 사고방식을 적용합니다.

## 현업에서는 이렇게 판단합니다

함수 합성의 핵심 가치는 관심사 분리입니다. 각 함수가 정확히 하나의 변환만 담당하면 테스트가 쉬워지고 조합 비용이 낮아집니다. 결국 중요한 것은 `pipe()`라는 도구 자체가 아니라, 작은 함수를 조립 가능한 단위로 설계하는 사고방식입니다.

Python에는 Haskell의 `.` 같은 내장 합성 연산자가 없지만, 그건 본질이 아닙니다. 프로젝트 안에서 읽기 좋은 방향으로 `pipe` 또는 `compose` 하나만 정해 두고 일관되게 쓰는 편이 훨씬 중요합니다.

## 체크리스트

- [ ] `compose`와 `pipe`의 차이를 설명할 수 있다
- [ ] 작은 함수를 조합해 데이터 파이프라인을 만들 수 있다
- [ ] generator 기반 지연 파이프라인을 구현할 수 있다
- [ ] 조건부 파이프라인을 작성할 수 있다
- [ ] 각 단계를 독립적으로 테스트할 수 있다

## 연습 문제

1. `compose`와 `pipe`를 둘 다 구현하고 같은 결과를 내는지 검증해 보세요.
2. JSON 데이터를 읽어 필터링, 변환, 정렬, 포맷팅까지 하는 4단계 파이프라인을 설계해 보세요.
3. `Result` 타입을 가정하고 오류 처리가 포함된 파이프라인을 구현해 보세요.

## 정리와 다음 글

함수 합성은 작은 함수를 결합해 큰 변환을 만드는 방법입니다. 특히 `pipe`는 코드 순서와 실행 순서를 맞춰 주기 때문에 Python에서 읽기 좋은 파이프라인을 만들기 좋습니다. 다음 글에서는 시리즈를 마무리하며 **객체지향과 함수형의 균형**을 다룹니다.

## 처음 질문으로 돌아가기

- **함수 합성은 수학적으로 어떤 의미를 가지며 Python에서는 어떻게 구현할까요?**
  - 본문의 기준은 함수 합성과 파이프라인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`compose`와 `pipe`는 무엇이 다르고, 왜 `pipe`가 더 읽기 쉬운 경우가 많을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **데이터 처리와 텍스트 처리에서 파이프라인은 어떤 장점을 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
- **함수 합성과 파이프라인 (현재 글)**
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [UNIX Philosophy — Doug McIlroy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Composing Software — Eric Elliott](https://medium.com/javascript-scene/composing-software-the-book-f31c77fc3ddc)

Tags: Python, Functional Programming, 함수 합성, 파이프라인, 데이터 변환
