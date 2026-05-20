---
series: functional-programming-101
episode: 8
title: "Functional Programming 101 (8/10): 지연 평가와 제너레이터"
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
  - 제너레이터
  - 지연 평가
  - itertools
seo_description: 제너레이터와 itertools로 메모리 효율적인 지연 파이프라인을 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (8/10): 지연 평가와 제너레이터

작은 데이터만 다룰 때는 리스트를 한 번에 만들어도 문제가 없습니다. 하지만 입력이 커지는 순간 이야기가 달라집니다. 로그 파일, 이벤트 스트림, 대용량 CSV처럼 전부 메모리에 올릴 수 없는 데이터를 다루기 시작하면 계산 시점을 늦추는 설계가 필요합니다.

이 글은 Functional Programming 101 시리즈의 여덟 번째 글입니다.

지연 평가는 "값이 정말 필요해질 때까지 계산하지 않는다"는 전략입니다. Python에서는 제너레이터와 iterator 프로토콜이 이 전략의 핵심 도구입니다. 이 글을 이해하면 `range`, `map`, `filter`, 파일 객체가 왜 메모리 효율적인지까지 함께 연결됩니다.

## 먼저 던지는 질문

- eager evaluation과 lazy evaluation은 무엇이 다를까요?
- 제너레이터 함수와 제너레이터 표현식은 어떤 상황에서 유용할까요?
- 무한 시퀀스와 큰 데이터를 Python에서는 어떻게 안전하게 다룰 수 있을까요?

## 큰 그림

![Functional Programming 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/08/08-01-lazy-pipeline-pull-model.ko.png)

*Functional Programming 101 8장 흐름 개요*

이 그림에서는 지연 평가와 제너레이터를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 지연 평가와 제너레이터의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

10GB 로그 파일을 분석한다고 가정해 보겠습니다. 전체를 리스트로 올리는 접근은 바로 한계에 부딪힙니다. 반대로 한 줄씩 읽고, 필요한 줄만 통과시키고, 마지막 소비 단계에서만 처리하면 입력 크기와 무관하게 메모리를 안정적으로 유지할 수 있습니다.

이 사고방식은 대용량 데이터 처리에서만 중요한 것이 아닙니다. 파이프라인 각 단계를 독립적으로 조합하고, 계산 시점을 늦추고, 필요 이상으로 일을 하지 않게 만드는 점에서 함수형 프로그래밍과도 아주 잘 맞습니다.

## 개념 개요

> eager는 값을 즉시 만들고, lazy는 필요해질 때까지 미룹니다.

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 지연 평가(lazy evaluation) | 값이 필요할 때만 계산하는 전략입니다 |
| 제너레이터(generator) | `yield`를 사용해 값을 하나씩 만들어 내는 함수입니다 |
| iterator | `__next__()`를 통해 순차적으로 값을 반환하는 객체입니다 |
| 제너레이터 표현식 | `(expr for x in iterable)` 형태의 지연 표현식입니다 |
| itertools | 효율적인 iterator 조합 도구를 제공하는 표준 라이브러리입니다 |

## Before / After

리스트 전체를 만드는 코드와 값을 하나씩 내보내는 코드는 겉보기엔 비슷하지만, 메모리 사용량은 완전히 다릅니다.

```python
# before: build the entire list in memory
def get_squares(n: int) -> list[int]:
    return [i ** 2 for i in range(n)]

squares = get_squares(1_000_000)  # millions of items stored at once
```

```python
# after: yield one value at a time
def get_squares(n: int):
    for i in range(n):
        yield i ** 2

squares = get_squares(1_000_000)  # almost no memory used
```

## 단계별 실습

### Step 1: 제너레이터 함수의 기본

```python
def countdown(n: int):
    """Counts down from n to 1."""
    while n > 0:
        yield n
        n -= 1

# create a generator object
gen = countdown(5)
print(type(gen))  # <class 'generator'>

# pull values one at a time with next()
print(next(gen))  # 5
print(next(gen))  # 4

# iterate over the rest with a for loop
for n in gen:
    print(n, end=" ")
# 3 2 1

# the generator is now exhausted
# next(gen)  # StopIteration
```

제너레이터는 함수처럼 보이지만, 실제로는 "다음 값을 요청받을 때마다 이어서 실행되는 상태 기계"에 가깝습니다. 이 관점을 잡으면 동작이 훨씬 명확해집니다.

### Step 2: 제너레이터 표현식

```python
# list comprehension — eager evaluation
squares_list = [x ** 2 for x in range(10)]
print(type(squares_list))  # <class 'list'>

# generator expression — lazy evaluation
squares_gen = (x ** 2 for x in range(10))
print(type(squares_gen))  # <class 'generator'>

# memory comparison
import sys

big_list = [x ** 2 for x in range(1_000_000)]
big_gen = (x ** 2 for x in range(1_000_000))

print(f"List: {sys.getsizeof(big_list):,} bytes")       # ~8,000,000 bytes
print(f"Generator: {sys.getsizeof(big_gen):,} bytes")    # ~200 bytes

# pass a generator expression directly to sum()
total = sum(x ** 2 for x in range(1_000_000))
print(f"Total: {total:,}")
```

제너레이터 표현식은 문법 비용이 거의 없으면서 지연 평가의 장점을 바로 가져옵니다. 집계 함수에 직접 넘길 수 있다는 점도 실용적입니다.

### Step 3: 무한 시퀀스 다루기

```python
from itertools import count, islice

# infinite generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# take only what you need with islice
fib_10 = list(islice(fibonacci(), 10))
print(fib_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# infinite counter
def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

# first 5 perfect squares
squares = list(islice(
    (n ** 2 for n in natural_numbers()),
    5,
))
print(squares)  # [1, 4, 9, 16, 25]
```

지연 평가의 진짜 힘은 여기서 드러납니다. 끝이 없는 데이터도 "필요한 만큼만" 가져오면 안전하게 다룰 수 있습니다.

### Step 4: itertools 활용하기

```python
from itertools import chain, takewhile, dropwhile, accumulate, groupby

# chain: concatenate multiple iterables
combined = list(chain([1, 2], [3, 4], [5, 6]))
print(combined)  # [1, 2, 3, 4, 5, 6]

# takewhile / dropwhile: condition-based selection
numbers = [2, 4, 6, 1, 3, 5, 8]
taken = list(takewhile(lambda x: x % 2 == 0, numbers))
dropped = list(dropwhile(lambda x: x % 2 == 0, numbers))
print(taken)    # [2, 4, 6]
print(dropped)  # [1, 3, 5, 8]

# accumulate: running totals
running_total = list(accumulate([1, 2, 3, 4, 5]))
print(running_total)  # [1, 3, 6, 10, 15]

# groupby: group consecutive elements by key
data = sorted(["a", "b", "a", "c", "b", "a"])
for key, group in groupby(data):
    print(f"  {key}: {list(group)}")
# a: ['a', 'a', 'a']
# b: ['b', 'b']
# c: ['c']
```

`itertools`는 표준 라이브러리 안에 들어 있는 함수형 도구상자에 가깝습니다. 직접 루프를 짜기 전에 여기서 이미 해결되는지 먼저 보는 습관이 좋습니다.

### Step 5: 지연 파이프라인 만들기

```python
from itertools import chain
from pathlib import Path
from typing import Iterator

def read_lines(path: Path) -> Iterator[str]:
    """Yields lines from a CSV file one at a time."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            yield line.rstrip("\n")

def parse_csv(lines: Iterator[str]) -> Iterator[dict]:
    """Converts CSV lines into dictionaries."""
    headers = [header.strip() for header in next(lines).split(",")]
    for line in lines:
        values = [value.strip() for value in line.split(",")]
        yield dict(zip(headers, values))

def filter_by_score(records: Iterator[dict], min_score: int) -> Iterator[dict]:
    """Yields only records above the minimum score."""
    for record in records:
        if int(record["score"]) >= min_score:
            yield record

def format_output(records: Iterator[dict]) -> Iterator[str]:
    """Formats records for display."""
    for r in records:
        yield f"{r['name']}: {r['score']} points"

# create a tiny sample file so the pipeline behaves like a real stream
sample_path = Path("scores.csv")
sample_path.write_text(
    "\n".join(
        [
            "name,score",
            "Alice,85",
            "Bob,92",
            "Charlie,78",
            "Diana,95",
            "Eve,60",
        ]
    ),
    encoding="utf-8",
)

try:
    # keep stage handles separate so you can inspect them in isolation
    lines_stage = read_lines(sample_path)
    header = next(lines_stage)
    print(f"Header preview: {header}")

    pipeline = format_output(
        filter_by_score(
            parse_csv(chain([header], lines_stage)),
            min_score=80,
        )
    )

    # consume results one at a time
    for line in pipeline:
        print(line)
    # Alice: 85 points
    # Bob: 92 points
    # Diana: 95 points

    print(list(pipeline))
    # []
finally:
    sample_path.unlink(missing_ok=True)
```

좋은 지연 파이프라인은 각 단계가 입력 iterator를 받아 출력 iterator를 돌려주는 형태를 유지합니다. 그 덕분에 단계별 테스트와 재조합이 쉬워집니다.

#### 예상 출력

```text
Header preview: name,score
Alice: 85 points
Bob: 92 points
Diana: 95 points
[]
```

#### 결과가 다르면 먼저 확인할 점

- 헤더가 `name,score`로 읽혔는지 확인합니다. 첫 줄을 잘못 건너뛰면 `score` 컬럼을 찾을 수 없습니다.
- `min_score=80` 비교가 `>=`인지 확인합니다. `>`로 바뀌면 `Alice`가 빠집니다.
- `rstrip("\n")`이나 `strip()`이 빠지면 이름 끝 개행 때문에 출력이 어긋날 수 있습니다.
- 마지막 `print(list(pipeline))`가 `[]`인지 확인합니다. generator는 한 번 소비하면 다시 비어 있어야 정상입니다.

## 이 코드에서 주목할 점

- 제너레이터는 값을 한 번에 하나씩 만들어 메모리를 절약합니다.
- 제너레이터 표현식은 `sum()`, `max()`, `min()`에 직접 전달할 수 있습니다.
- 무한 시퀀스는 `islice()`나 `takewhile()`로 안전하게 유한화해야 합니다.
- 지연 파이프라인에서는 각 단계가 generator이므로 데이터가 레코드 단위로 흐릅니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 같은 제너레이터를 두 번 순회함 | 한 번 소진되면 더 이상 값이 나오지 않습니다 | `list()`로 저장하거나 다시 생성합니다 |
| 무한 제너레이터에 `list()`를 호출함 | 메모리가 고갈됩니다 | `islice()`로 개수를 제한합니다 |
| 제너레이터에 `len()`을 호출함 | `TypeError`가 발생합니다 | 길이가 필요하면 리스트로 변환합니다 |
| 제너레이터 내부 예외를 무시함 | 데이터 손실이 조용히 발생할 수 있습니다 | 예외를 처리하거나 상위로 전파합니다 |
| 너무 일찍 `list()`로 변환함 | 지연 평가의 이점을 잃습니다 | 최종 소비 직전까지 generator를 유지합니다 |

## 실무에서 이렇게 쓰입니다

- 큰 로그 파일을 한 줄씩 처리합니다.
- API pagination 결과를 generator로 감쌉니다.
- ETL 파이프라인을 여러 generator 단계로 조합합니다.
- 스트리밍 데이터를 실시간으로 변환합니다.
- `itertools`로 조합, 순열, 그룹화를 효율적으로 처리합니다.

## 현업에서는 이렇게 판단합니다

Python의 제너레이터는 함수형 프로그래밍의 지연 평가를 아주 실용적으로 구현한 도구입니다. "이 데이터를 정말 전부 메모리에 올려야 하나?"라는 질문이 떠오르는 순간 제너레이터를 검토하면 됩니다.

운영 코드에서는 각 파이프라인 단계를 generator로 만들고, 마지막 소비자만 실제 계산을 밀어붙이게 하는 패턴이 가장 강합니다. `for` 루프, `sum()`, 파일 쓰기 같은 최종 소비자가 파이프 전체를 구동하는 구조는 UNIX 파이프와도 같은 철학을 가집니다.

## 체크리스트

- [ ] 일반 함수와 제너레이터 함수의 차이를 설명할 수 있다
- [ ] 제너레이터 표현식을 작성할 수 있다
- [ ] `itertools`의 핵심 함수를 활용할 수 있다
- [ ] 무한 시퀀스를 안전하게 다룰 수 있다
- [ ] 큰 데이터를 위한 지연 파이프라인을 설계할 수 있다

## 연습 문제

1. 소수를 무한히 생성하는 제너레이터를 만들고 `islice`로 앞 20개를 출력해 보세요.
2. 큰 CSV 파일을 한 줄씩 읽어 특정 컬럼 평균을 계산하는 지연 파이프라인을 설계해 보세요.
3. 여러 로그 파일의 항목을 `itertools.chain`과 `groupby`로 날짜별 묶음으로 만들어 보세요.

## 정리와 다음 글

지연 평가는 값이 정말 필요해지는 순간까지 계산을 미뤄 메모리 사용량을 안정적으로 유지하는 전략입니다. Python에서는 제너레이터와 `itertools`가 그 중심 도구입니다. 다음 글에서는 작은 함수를 큰 변환으로 연결하는 **함수 합성과 파이프라인**을 다룹니다.

## 처음 질문으로 돌아가기

- **eager evaluation과 lazy evaluation은 무엇이 다를까요?**
  - 본문의 기준은 지연 평가와 제너레이터를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **제너레이터 함수와 제너레이터 표현식은 어떤 상황에서 유용할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **무한 시퀀스와 큰 데이터를 Python에서는 어떻게 안전하게 다룰 수 있을까요?**
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
- **지연 평가와 제너레이터 (현재 글)**
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Generators](https://docs.python.org/3/howto/functional.html#generators)
- [Python 공식 문서 — itertools](https://docs.python.org/3/library/itertools.html)
- [Real Python — Introduction to Python Generators](https://realpython.com/introduction-to-python-generators/)
- [David Beazley — Generator Tricks for Systems Programmers](http://www.dabeaz.com/generators/)

Tags: Python, Functional Programming, 제너레이터, 지연 평가, itertools
