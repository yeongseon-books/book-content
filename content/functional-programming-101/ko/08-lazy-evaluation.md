---
series: functional-programming-101
episode: 8
title: 지연 평가와 제너레이터
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
  - 제너레이터
  - 지연 평가
  - itertools
seo_description: 제너레이터와 지연 평가로 메모리 효율적인 데이터 처리를 구현하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 지연 평가와 제너레이터

> Functional Programming 101 시리즈 (8/10)


## 이 글에서 다룰 문제

10GB 로그 파일을 분석할 때 전체를 메모리에 올릴 수 없습니다. 지연 평가는 데이터를 한 줄씩 처리하여 메모리 사용을 일정하게 유지합니다.

> 지연 평가 = 필요한 만큼만 계산

Python의 `range()`, `map()`, `filter()`, 파일 객체 모두 지연 평가를 사용합니다. 제너레이터를 이해하면 이 모든 도구의 원리를 파악할 수 있습니다.

## 핵심 개념 잡기

> 즉시 평가 vs 지연 평가

```
즉시 평가 (Eager)              지연 평가 (Lazy)
─────────────────             ─────────────────
[1, 4, 9, 16, 25]            (계산 대기 중...)
메모리에 전부 저장              요청 시 하나씩 생성
list()                        generator / iterator
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 지연 평가(lazy evaluation) | 값이 필요한 시점에 계산하는 전략입니다 |
| 제너레이터(generator) | `yield`로 값을 하나씩 생성하는 함수입니다 |
| 이터레이터(iterator) | `__next__()`로 값을 순차 반환하는 객체입니다 |
| 제너레이터 표현식 | `(expr for x in iterable)` 형태의 지연 평가 표현식입니다 |
| itertools | 효율적인 이터레이터 조합을 제공하는 표준 라이브러리입니다 |

## Before / After

전체 리스트 생성을 제너레이터로 교체합니다.

```python
# before: 전체 리스트를 메모리에 생성
def get_squares(n: int) -> list[int]:
    return [i ** 2 for i in range(n)]

squares = get_squares(1_000_000)  # 수백만 개를 한번에 저장
```

```python
# after: 제너레이터로 하나씩 생성
def get_squares(n: int):
    for i in range(n):
        yield i ** 2

squares = get_squares(1_000_000)  # 메모리 거의 사용하지 않음
```

## 단계별 실습

### Step 1: 제너레이터 함수 기초

```python
def countdown(n: int):
    """n부터 1까지 카운트다운합니다."""
    while n > 0:
        yield n
        n -= 1


# 제너레이터 객체 생성
gen = countdown(5)
print(type(gen))  # <class 'generator'>

# next()로 하나씩 가져오기
print(next(gen))  # 5
print(next(gen))  # 4

# for 루프로 나머지 순회
for n in gen:
    print(n, end=" ")
# 3 2 1

# 이미 소진된 제너레이터
# next(gen)  # StopIteration
```

### Step 2: 제너레이터 표현식

```python
# 리스트 컴프리헨션 — 즉시 평가
squares_list = [x ** 2 for x in range(10)]
print(type(squares_list))  # <class 'list'>

# 제너레이터 표현식 — 지연 평가
squares_gen = (x ** 2 for x in range(10))
print(type(squares_gen))  # <class 'generator'>


# 메모리 비교
import sys

big_list = [x ** 2 for x in range(1_000_000)]
big_gen = (x ** 2 for x in range(1_000_000))

print(f"리스트: {sys.getsizeof(big_list):,} bytes")  # ~8,000,000 bytes
print(f"제너레이터: {sys.getsizeof(big_gen):,} bytes")  # ~200 bytes

# 합계 계산 — 제너레이터를 sum()에 직접 전달
total = sum(x ** 2 for x in range(1_000_000))
print(f"합계: {total:,}")
```

### Step 3: 무한 시퀀스

```python
from itertools import count, islice


# 무한 제너레이터
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# islice로 필요한 만큼만 가져오기
fib_10 = list(islice(fibonacci(), 10))
print(fib_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# 무한 카운터
def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

# 처음 5개의 제곱수
squares = list(islice(
    (n ** 2 for n in natural_numbers()),
    5,
))
print(squares)  # [1, 4, 9, 16, 25]
```

### Step 4: itertools 활용

```python
from itertools import chain, takewhile, dropwhile, accumulate, groupby


# chain: 여러 이터러블을 연결
combined = list(chain([1, 2], [3, 4], [5, 6]))
print(combined)  # [1, 2, 3, 4, 5, 6]

# takewhile / dropwhile: 조건 기반 선택
numbers = [2, 4, 6, 1, 3, 5, 8]
taken = list(takewhile(lambda x: x % 2 == 0, numbers))
dropped = list(dropwhile(lambda x: x % 2 == 0, numbers))
print(taken)    # [2, 4, 6]
print(dropped)  # [1, 3, 5, 8]

# accumulate: 누적 합계
running_total = list(accumulate([1, 2, 3, 4, 5]))
print(running_total)  # [1, 3, 6, 10, 15]

# groupby: 연속된 동일 키로 그룹화
data = sorted(["a", "b", "a", "c", "b", "a"])
for key, group in groupby(data):
    print(f"  {key}: {list(group)}")
# a: ['a', 'a', 'a']
# b: ['b', 'b']
# c: ['c']
```

### Step 5: 지연 파이프라인 구성

```python
from typing import Iterator


def read_lines(text: str) -> Iterator[str]:
    """텍스트를 줄 단위로 생성합니다."""
    for line in text.strip().split("\n"):
        yield line.strip()

def parse_csv(lines: Iterator[str]) -> Iterator[dict]:
    """CSV 줄을 딕셔너리로 변환합니다."""
    headers = next(lines).split(",")
    for line in lines:
        values = line.split(",")
        yield dict(zip(headers, values))

def filter_by_score(records: Iterator[dict], min_score: int) -> Iterator[dict]:
    """최소 점수 이상인 레코드만 선택합니다."""
    for record in records:
        if int(record["score"]) >= min_score:
            yield record

def format_output(records: Iterator[dict]) -> Iterator[str]:
    """출력 형식으로 변환합니다."""
    for r in records:
        yield f"{r['name']}: {r['score']}점"


# 파이프라인 실행 — 모든 단계가 지연 평가
csv_text = """name,score
Alice,85
Bob,92
Charlie,78
Diana,95
Eve,60"""

pipeline = format_output(
    filter_by_score(
        parse_csv(read_lines(csv_text)),
        min_score=80,
    )
)

# 결과를 하나씩 소비
for line in pipeline:
    print(line)
# Alice: 85점
# Bob: 92점
# Diana: 95점
```

## 이 코드에서 주목할 점

- 제너레이터는 값을 하나씩 생성하여 메모리를 절약합니다
- 제너레이터 표현식은 `sum()`, `max()`, `min()`에 직접 전달할 수 있습니다
- 무한 시퀀스는 `islice()`나 `takewhile()`로 유한하게 자릅니다
- 지연 파이프라인은 각 단계가 제너레이터이므로 데이터가 한 줄씩 흐릅니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 제너레이터를 여러 번 순회 | 한 번 소진되면 끝입니다 | `list()`로 변환하거나 다시 생성합니다 |
| 무한 제너레이터에 `list()` 호출 | 메모리 부족으로 멈춥니다 | `islice()`로 제한합니다 |
| 제너레이터에 `len()` 호출 | TypeError가 발생합니다 | 길이가 필요하면 리스트로 변환합니다 |
| 제너레이터 안에서 예외 무시 | 데이터 손실이 발생합니다 | 예외를 적절히 처리하거나 전파합니다 |
| 불필요한 `list()` 변환 | 지연 평가의 이점을 잃습니다 | 최종 소비 시점까지 제너레이터를 유지합니다 |

## 실무에서 이렇게 쓰입니다

- 대용량 로그 파일을 줄 단위로 처리합니다
- API 페이지네이션 결과를 제너레이터로 추상화합니다
- ETL 파이프라인을 제너레이터 체이닝으로 구성합니다
- 스트리밍 데이터를 실시간으로 변환합니다
- `itertools`로 조합, 순열, 그룹화를 효율적으로 처리합니다

## 현업 개발자는 이렇게 생각합니다

Python의 제너레이터는 함수형 프로그래밍의 지연 평가를 실용적으로 구현한 도구입니다. "이 데이터를 전부 메모리에 올려야 하는가?"라는 질문에 "아니오"라면 제너레이터를 사용합니다.

실무에서는 파이프라인의 각 단계를 제너레이터로 구성하고, 최종 소비자(for 루프, `sum()`, 파일 쓰기)에서만 실제 계산이 발생하게 하는 패턴이 효과적입니다. 이는 UNIX의 파이프(`|`) 철학과 동일합니다.

## 체크리스트

- [ ] 제너레이터 함수와 일반 함수의 차이를 설명할 수 있다
- [ ] 제너레이터 표현식을 작성할 수 있다
- [ ] `itertools`의 주요 함수를 활용할 수 있다
- [ ] 무한 시퀀스를 안전하게 다룰 수 있다
- [ ] 지연 파이프라인을 구성하여 대용량 데이터를 처리할 수 있다

## 정리 및 다음 글 안내

지연 평가는 필요한 시점에 계산하여 메모리를 절약합니다. Python의 제너레이터와 `itertools`는 지연 파이프라인을 구성하는 핵심 도구입니다. 다음 글에서는 작은 함수를 조합하여 복잡한 변환을 만드는 **함수 합성과 파이프라인**을 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- **지연 평가와 제너레이터 (현재 글)**
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Generators](https://docs.python.org/3/howto/functional.html#generators)
- [Python 공식 문서 — itertools](https://docs.python.org/3/library/itertools.html)
- [Real Python — Introduction to Python Generators](https://realpython.com/introduction-to-python-generators/)
- [David Beazley — Generator Tricks for Systems Programmers](http://www.dabeaz.com/generators/)

Tags: Python, Functional Programming, 제너레이터, 지연 평가, itertools
