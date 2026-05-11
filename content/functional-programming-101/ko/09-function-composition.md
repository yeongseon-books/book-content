---
series: functional-programming-101
episode: 9
title: 함수 합성과 파이프라인
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
  - 함수 합성
  - 파이프라인
  - 데이터 변환
seo_description: 작은 함수를 조합하여 복잡한 데이터 변환 파이프라인을 구성하는 방법을 다룹니다.
last_reviewed: '2026-05-11'
---

# 함수 합성과 파이프라인

> Functional Programming 101 시리즈 (9/10)


## 이 글에서 다룰 문제

복잡한 데이터 처리 로직을 하나의 거대한 함수로 작성하면 테스트와 재사용이 어렵습니다. 작은 단위 함수를 조합하면 각 단계를 독립적으로 테스트하고 재조합할 수 있습니다.

> 함수 합성 = 작은 부품으로 큰 시스템 구축

UNIX의 파이프(`cat file | grep error | sort | uniq`)와 같은 철학입니다. 각 도구는 한 가지 일을 잘 하고, 조합으로 복잡한 작업을 수행합니다.

## 핵심 개념 잡기

> compose vs pipe — 방향의 차이

```text
compose(f, g, h)(x)  =  f(g(h(x)))     ← 오른쪽에서 왼쪽
pipe(h, g, f)(x)     =  f(g(h(x)))     ← 왼쪽에서 오른쪽

파이프라인 시각화:
  x → [h] → [g] → [f] → result
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 함수 합성(composition) | 두 함수 f, g를 결합하여 f(g(x))를 만드는 연산입니다 |
| 파이프라인(pipeline) | 데이터가 함수 체인을 순차적으로 통과하는 패턴입니다 |
| compose | 함수를 오른쪽에서 왼쪽으로 합성합니다 |
| pipe | 함수를 왼쪽에서 오른쪽으로 합성합니다 |
| 포인트프리 스타일(point-free) | 인자를 명시하지 않고 함수 조합만으로 표현하는 스타일입니다 |

## Before / After

중첩 함수 호출을 파이프라인으로 전환합니다.

```python
# before: 중첩 호출 — 안에서 바깥으로 읽어야 함
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
# after: 파이프라인 — 위에서 아래로 읽기
result = pipe(
    load_data,
    calculate_totals,
    filter_passing,
    sort_by_score,
    format_output,
)()
```

## 단계별 실습

### Step 1: 기본 compose와 pipe

```python
from typing import Callable, Any
from functools import reduce


def compose(*funcs: Callable) -> Callable:
    """오른쪽에서 왼쪽으로 함수를 합성합니다."""
    def composed(x: Any) -> Any:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed

def pipe(*funcs: Callable) -> Callable:
    """왼쪽에서 오른쪽으로 함수를 합성합니다."""
    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result
    return piped


# compose 예시: f(g(h(x)))
add_one = lambda x: x + 1
double = lambda x: x * 2
to_str = lambda x: f"Result: {x}"

transform_c = compose(to_str, double, add_one)
print(transform_c(5))  # Result: 12  — (5+1)*2 = 12

# pipe: 읽기 순서와 실행 순서가 같음
transform_p = pipe(add_one, double, to_str)
print(transform_p(5))  # Result: 12
```

### Step 2: 실전 문자열 처리 파이프라인

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


# 슬러그 생성 파이프라인
slugify = pipe(
    strip_whitespace,
    normalize_spaces,
    to_lowercase,
    replace_special,
    spaces_to_hyphens,
    truncate(50),
)

print(slugify("  Hello, World!  This is  a Test  "))
# 출력 예시: hello-world-this-is-a-test

print(slugify("  Functional Programming — 함수 합성 가이드  "))
# 출력 예시: functional-programming--
```

### Step 3: 데이터 처리 파이프라인

```python
from typing import Callable


def pipe_data(*funcs: Callable) -> Callable:
    """데이터 처리 파이프라인입니다."""
    def process(data):
        result = data
        for func in funcs:
            result = func(result)
        return result
    return process


# 각 단계를 독립 함수로 정의
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
    lines = [f"{'이름':<10} {'점수':>5} {'등급':>4}"]
    lines.append("-" * 22)
    for r in records:
        lines.append(f"{r['name']:<10} {r['score']:>5} {r['grade']:>4}")
    return "\n".join(lines)


# 파이프라인 조립
process_students = pipe_data(
    parse_records,
    add_grade,
    filter_passing,
    sort_by_score,
    format_table,
)

# 실행
raw_data = [
    "Alice, 85",
    "Bob, 92",
    "Charlie, 78",
    "Diana, 95",
    "Eve, 60",
]

print(process_students(raw_data))
# 이름          점수   등급
# ----------------------
# 출력 예시: Diana          95    A
# 출력 예시: Bob            92    A
# 출력 예시: Alice          85    B
# 출력 예시: Charlie        78    C
```

### Step 4: 제너레이터 파이프라인

```python
from typing import Iterator, Callable


def gen_pipe(*funcs: Callable) -> Callable:
    """제너레이터 기반 지연 파이프라인입니다."""
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


# 지연 파이프라인 조립
clean_text = gen_pipe(
    strip_lines,
    skip_empty,
    skip_comments,
    to_upper,
)

text = """
  # 설정 파일
  host = localhost

  port = 8080

  # 디버그 모드
  debug = true
"""

for line in clean_text(lines(text)):
    print(line)
# HOST = LOCALHOST
# PORT = 8080
# DEBUG = TRUE
```

### Step 5: 조건부 파이프라인

```python
from typing import Callable, Any


def conditional(
    predicate: Callable[[Any], bool],
    if_true: Callable,
    if_false: Callable | None = None,
) -> Callable:
    """조건에 따라 다른 함수를 적용합니다."""
    def apply(value: Any) -> Any:
        if predicate(value):
            return if_true(value)
        return if_false(value) if if_false else value
    return apply

def when(predicate: Callable[[Any], bool], func: Callable) -> Callable:
    """조건이 참일 때만 함수를 적용합니다."""
    return conditional(predicate, func)


# 조건부 단계가 포함된 파이프라인
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

## 이 코드에서 주목할 점

- `pipe`는 실행 순서와 코드 순서가 일치하여 가독성이 높습니다
- 각 단계 함수가 독립적이므로 개별 테스트가 가능합니다
- 제너레이터 파이프라인은 대용량 데이터를 메모리 효율적으로 처리합니다
- 조건부 파이프라인으로 분기 로직을 선언적으로 표현할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 함수 시그니처 불일치 | 앞 함수의 출력이 뒤 함수의 입력과 맞지 않습니다 | 타입 힌트로 호환성을 확인합니다 |
| 파이프라인이 너무 길어짐 | 디버깅이 어려워집니다 | 중간 변수나 로깅 단계를 추가합니다 |
| 부수효과를 파이프라인 중간에 배치 | 테스트와 재사용이 어렵습니다 | 부수효과는 파이프라인의 끝에 배치합니다 |
| 에러 처리 누락 | 중간 단계 실패 시 전체가 멈춥니다 | 에러 처리 단계를 파이프라인에 포함합니다 |
| compose와 pipe 혼용 | 실행 방향이 혼란스럽습니다 | 프로젝트 내에서 하나를 통일합니다 |

## 실무에서 이렇게 쓰입니다

- ETL 파이프라인(Extract → Transform → Load)을 함수 합성으로 구성합니다
- 데이터 검증을 여러 검증 함수의 파이프라인으로 구현합니다
- 텍스트 전처리(정규화, 토큰화, 필터링)를 파이프라인으로 구성합니다
- API 미들웨어 체인을 함수 합성으로 구현합니다
- CI/CD 파이프라인의 각 단계를 독립 함수로 정의합니다

## 현업 개발자는 이렇게 생각합니다

함수 합성의 핵심 가치는 "관심사의 분리"입니다. 각 함수가 한 가지 변환만 담당하면 테스트가 쉽고 재조합이 자유롭습니다. UNIX 철학 "한 가지 일을 잘 하라"를 코드 수준에서 실천하는 것입니다.

Python에는 Haskell의 `.` 연산자 같은 내장 합성 문법이 없지만, `pipe()` 유틸리티 하나면 충분합니다. 핵심은 도구가 아니라 "작은 함수를 조합하는 사고방식"입니다.

## 체크리스트

- [ ] compose와 pipe의 차이를 설명할 수 있다
- [ ] 작은 함수를 조합하여 데이터 파이프라인을 구성할 수 있다
- [ ] 제너레이터 파이프라인으로 지연 평가를 구현할 수 있다
- [ ] 조건부 파이프라인을 작성할 수 있다
- [ ] 파이프라인의 각 단계를 독립적으로 테스트할 수 있다

## 정리 및 다음 글 안내

함수 합성은 작은 함수를 결합하여 복잡한 변환을 만드는 기법입니다. `pipe`는 실행 순서와 코드 순서를 일치시켜 가독성을 높입니다. 다음 글에서는 시리즈의 마무리로 **객체지향과 함수형의 균형**을 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- **함수 합성과 파이프라인 (현재 글)**
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)
- [Real Python — Functional Programming in Python](https://realpython.com/python-functional-programming/)
- [UNIX Philosophy — Doug McIlroy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Composing Software — Eric Elliott](https://medium.com/javascript-scene/composing-software-the-book-f31c77fc3ddc)

Tags: Python, Functional Programming, 함수 합성, 파이프라인, 데이터 변환
