---
series: computer-science-101
episode: 2
title: 계산과 프로그램
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 계산 모델
  - 튜링 기계
  - 프로그래밍 패러다임
  - 컴파일러
  - 인터프리터
seo_description: 계산의 정의, 튜링 기계, 프로그래밍 언어의 발전과 패러다임을 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 계산과 프로그램

> Computer Science 101 시리즈 (2/10)


## 이 글에서 다룰 문제

"모든 문제를 프로그램으로 풀 수 있을까?"라는 질문의 답은 "아니오"입니다. 계산 이론은 풀 수 있는 문제와 풀 수 없는 문제의 경계를 알려줍니다. 프로그래밍 패러다임은 풀 수 있는 문제를 어떤 방식으로 표현할지 결정합니다. 두 가지 모두 소프트웨어 설계의 기초입니다.

> 계산 이론 = CS의 헌법. 패러다임 = 코드를 조직하는 철학.

## 전체 흐름
> 계산은 입력을 규칙에 따라 변환하는 과정입니다. 튜링 기계는 이 과정의 가장 기본적인 모델이며, 프로그래밍 언어는 이를 인간이 읽을 수 있게 표현합니다.

```text
수학적 함수 (이론)
     │
튜링 기계 (계산 모델)
     │
기계어 (하드웨어)
     │
어셈블리 (저수준)
     │
고급 언어 (Python, Java)
     │
패러다임 (명령형, 함수형, OOP)
```

## Before / After

**Before — 패러다임을 모를 때:**

```python
# 모든 로직을 하나의 함수에 절차적으로 나열합니다
def process_orders(orders):
    total = 0
    for order in orders:
        if order["status"] == "paid":
            price = order["price"] * order["quantity"]
            if order["discount"]:
                price = price * 0.9
            total += price
    return total
```

**After — 패러다임을 알 때:**

```python
from dataclasses import dataclass


@dataclass
class Order:
    price: int
    quantity: int
    status: str
    discount: bool

    def total_price(self) -> int:
        base = self.price * self.quantity
        return int(base * 0.9) if self.discount else base


def process_orders(orders: list[Order]) -> int:
    return sum(o.total_price() for o in orders if o.status == "paid")
```

## 단계별로 따라하기

### 1단계: 상태 기계로 이해하는 계산

```python
def simple_state_machine(tape: list[str]) -> list[str]:
    """단순 상태 기계: 0을 1로, 1을 0으로 뒤집습니다."""
    state = "flip"
    result = []
    for symbol in tape:
        if state == "flip":
            result.append("1" if symbol == "0" else "0")
    return result


tape = ["1", "0", "1", "1", "0"]
print(simple_state_machine(tape))  # ['0', '1', '0', '0', '1']
```

튜링 기계의 핵심 아이디어입니다. 현재 상태와 현재 기호를 보고 다음 행동을 결정합니다.

### 2단계: 계산할 수 없는 문제

```python
def halts(program, input_data):
    """이 함수는 구현할 수 없습니다."""
    # program이 input_data에 대해 멈추는지 판별
    # 증명: 이 함수가 존재한다고 가정하면 모순이 발생합니다
    raise NotImplementedError("정지 문제는 풀 수 없습니다")


# 대신 실용적 접근: 타임아웃을 설정합니다
import signal


def run_with_timeout(func, timeout_sec: int = 5):
    """일정 시간 내에 끝나지 않으면 중단합니다."""
    signal.alarm(timeout_sec)
    try:
        return func()
    except Exception:
        return None
```

정지 문제는 CS의 가장 유명한 불가능성 결과입니다. 완벽한 디버거나 완벽한 바이러스 검사기가 불가능한 이유의 근거입니다.

### 3단계: 명령형 프로그래밍

```python
# 명령형: "어떻게" 할지를 단계별로 지시합니다
def sum_of_squares_imperative(n: int) -> int:
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total


print(sum_of_squares_imperative(5))  # 55
```

명령형 패러다임은 컴퓨터에게 단계별 명령을 내립니다. C, Go, 초기 Python 코드가 이 스타일입니다.

### 4단계: 함수형 프로그래밍

```python
from functools import reduce

# 함수형: "무엇"을 계산할지 선언합니다
def sum_of_squares_functional(n: int) -> int:
    return reduce(lambda acc, x: acc + x * x, range(1, n + 1), 0)


print(sum_of_squares_functional(5))  # 55
```

함수형 패러다임은 상태 변경 없이 함수 조합으로 계산을 표현합니다. Haskell, Scala, Python의 `map`/`filter`가 이 스타일입니다.

### 5단계: 컴파일과 인터프리트

```python
# Python은 인터프리터 언어입니다
# 소스 코드 → 바이트코드 → 가상 머신에서 실행

import dis


def add(a: int, b: int) -> int:
    return a + b


# Python 바이트코드를 확인합니다
dis.dis(add)
# LOAD_FAST    0 (a)
# LOAD_FAST    1 (b)
# BINARY_ADD
# RETURN_VALUE
```

컴파일러는 전체 코드를 미리 번역하고, 인터프리터는 한 줄씩 실행합니다. Python은 바이트코드로 컴파일한 뒤 가상 머신에서 인터프리트합니다.

## 이 코드에서 주목할 점

- 상태 기계는 튜링 기계의 단순화된 형태로 계산의 본질을 보여줍니다
- 정지 문제는 이론적으로 풀 수 없지만 실용적 대안(타임아웃)이 존재합니다
- 같은 계산을 명령형과 함수형으로 각각 표현할 수 있습니다
- Python은 컴파일과 인터프리트를 모두 사용하는 하이브리드 방식입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 모든 문제가 프로그램으로 풀린다고 가정 | 계산 불가능한 문제가 존재합니다 | 정지 문제와 계산 이론을 학습합니다 |
| 패러다임을 하나만 고집 | 상황에 맞지 않는 코드가 됩니다 | 문제에 맞는 패러다임을 선택합니다 |
| 컴파일러와 인터프리터를 혼동 | 언어 특성을 잘못 이해합니다 | 실행 방식의 차이를 명확히 구분합니다 |
| 고급 언어만 사용하며 저수준을 무시 | 성능 문제를 이해할 수 없습니다 | 기계어와 메모리 구조를 기본 수준에서 파악합니다 |
| 이론을 실무와 무관하다고 무시 | 근본적인 한계를 모릅니다 | 이론이 실무 의사결정에 미치는 영향을 파악합니다 |

## 실무에서는 이렇게 쓰입니다

- 다중 패러다임 언어(Python, Kotlin)에서 상황에 맞는 스타일 선택
- 컴파일 타임 vs 런타임 오류 이해로 타입 시스템 활용
- 정지 문제의 실용적 대안으로 타임아웃, 회로 차단기 패턴 설계
- 바이트코드 분석으로 Python 성능 병목 파악
- 함수형 패턴(map, filter, reduce)으로 데이터 파이프라인 구성

## 체크리스트

- [ ] 튜링 기계의 개념을 설명할 수 있는가
- [ ] 정지 문제가 왜 풀 수 없는지 이해했는가
- [ ] 명령형, 함수형, 객체지향의 차이를 구분할 수 있는가
- [ ] 컴파일러와 인터프리터의 차이를 이해했는가
- [ ] Python의 실행 방식(바이트코드 + VM)을 파악했는가

## 정리 및 다음 단계

계산은 입력을 규칙에 따라 변환하는 과정이며, 튜링 기계가 그 이론적 모델입니다. 모든 문제가 계산으로 풀리는 것은 아닙니다(정지 문제). 프로그래밍 언어는 계산을 인간이 읽을 수 있게 표현하며, 패러다임은 코드를 조직하는 철학입니다.

다음 글에서는 컴퓨터가 데이터를 어떻게 표현하는지 — 이진수, 문자 인코딩, 자료형을 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- **계산과 프로그램 (현재 글)**
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [Alan Turing — On Computable Numbers (1936)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [Wikipedia — Halting Problem](https://en.wikipedia.org/wiki/Halting_problem)
- [SICP — Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Programming Paradigms for Dummies (Peter Van Roy)](https://www.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)

Tags: Computer Science, 계산 모델, 튜링 기계, 프로그래밍 패러다임, 컴파일러, 인터프리터
