---
series: computer-science-101
episode: 2
title: "Computer Science 101 (2/10): 계산과 프로그램"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: 계산의 정의, 튜링 기계, 프로그래밍 패러다임을 한 흐름으로 이해합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (2/10): 계산과 프로그램

"프로그램으로 풀 수 있는 문제"라는 말은 익숙하지만, 어디까지가 계산 가능한 범위인지 정확히 묻기 시작하면 이야기가 달라집니다. 계산 가능성의 경계와 코드를 조직하는 방식은 생각보다 가까이 붙어 있습니다.

이 글은 Computer Science 101 시리즈의 2번째 글입니다.

여기서는 계산의 이론적 정의, 계산할 수 없는 문제, 그리고 프로그래밍 언어와 패러다임이 그 계산을 어떻게 사람의 언어로 옮기는지 함께 살펴보겠습니다.

## 먼저 던지는 질문

- 무엇을 두고 계산 가능하다고 말할 수 있을까요?
- 튜링 기계는 왜 오늘날의 컴퓨터를 설명하는 기준 모델로 남아 있을까요?
- 정지 문제처럼 원리적으로 풀 수 없는 문제는 무엇을 의미할까요?

## 큰 그림

![Computer Science 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/02/02-01-concept-at-a-glance.ko.png)

*Computer Science 101 2장 흐름 개요*

이 그림에서는 계산과 프로그램를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 계산과 프로그램의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 튜링 기계와 계산 가능성의 핵심 개념
- 정지 문제처럼 계산할 수 없는 문제의 의미
- 프로그래밍 언어의 발전 흐름
- 명령형·함수형·객체지향 패러다임의 차이

## 왜 중요한가

"모든 문제를 프로그램으로 풀 수 있을까?"라는 질문의 답은 "아니오"입니다. 계산 이론은 풀 수 있는 문제와 풀 수 없는 문제의 경계를 알려줍니다. 프로그래밍 패러다임은 풀 수 있는 문제를 어떤 방식으로 표현할지 결정합니다. 두 가지 모두 소프트웨어 설계의 기초입니다.

> 계산 이론 = CS의 헌법. 패러다임 = 코드를 조직하는 철학.

## 한눈에 보는 개념

> 계산은 입력을 규칙에 따라 변환하는 과정입니다. 튜링 기계는 이 과정의 가장 기본적인 모델이며, 프로그래밍 언어는 이를 인간이 읽을 수 있게 표현합니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Turing machine | 계산 가능성을 정의하는 이론적 계산 모델 |
| Halting problem | 프로그램이 끝나는지 일반적으로 판정할 수 없는 문제 |
| Compiler | 소스 코드를 다른 저수준 코드로 번역하는 프로그램 |
| Interpreter | 소스 코드를 실행하면서 해석하는 프로그램 |
| Paradigm | 코드를 조직하는 방식과 사고 체계 |

## Before / After

**Before — 패러다임을 모를 때:**

```python
# All logic crammed into one procedural function
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
    """A tiny state machine that flips 0 to 1 and 1 to 0."""
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
    """This function cannot be implemented."""
    # Decide whether `program` halts on `input_data`.
    # Proof sketch: assuming this function exists leads to a contradiction.
    raise NotImplementedError("The halting problem is undecidable")

# A practical workaround: use a timeout
import signal

def run_with_timeout(func, timeout_sec: int = 5):
    """Abort if the function does not finish within the time limit."""
    signal.alarm(timeout_sec)
    try:
        return func()
    except Exception:
        return None
```

정지 문제는 CS의 가장 유명한 불가능성 결과입니다. 완벽한 디버거나 완벽한 바이러스 검사기가 불가능한 이유의 근거입니다.

### 3단계: 명령형 프로그래밍

```python
# Imperative: you tell the computer "how" step by step
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

# Functional: you declare "what" to compute
def sum_of_squares_functional(n: int) -> int:
    return reduce(lambda acc, x: acc + x * x, range(1, n + 1), 0)

print(sum_of_squares_functional(5))  # 55
```

함수형 패러다임은 상태 변경 없이 함수 조합으로 계산을 표현합니다. Haskell, Scala, Python의 `map`/`filter`가 이 스타일입니다.

### 5단계: 컴파일과 인터프리트

```python
# Python is an interpreted language
# Source code -> bytecode -> executed on a virtual machine

import dis

def add(a: int, b: int) -> int:
    return a + b

# Inspect the Python bytecode
dis.dis(add)
# LOAD_FAST    0 (a)
# LOAD_FAST    1 (b)
# BINARY_ADD
# RETURN_VALUE
```

**Expected output:** `LOAD_FAST`, `BINARY_ADD`, `RETURN_VALUE` 같은 바이트코드가 출력되어, Python 코드도 내부적으로 더 낮은 단계 표현을 거친다는 점을 확인할 수 있어야 합니다.

컴파일러는 전체 코드를 미리 번역하고, 인터프리터는 한 줄씩 실행합니다. Python은 바이트코드로 컴파일한 뒤 가상 머신에서 인터프리트합니다.

## 이 코드에서 먼저 봐야 할 점

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

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 특정 패러다임을 신념처럼 밀지 않습니다. 상태를 명확히 보여야 할 때는 명령형이 낫고, 조합과 변환이 핵심일 때는 함수형이 더 읽히는 식으로 문제에 맞춰 고릅니다.

계산 이론의 한계도 실무에서 중요합니다. 완벽한 정적 분석기나 모든 버그를 잡는 테스트는 원리적으로 불가능하다는 사실을 알면, 현실적인 타임아웃과 가드레일 설계에 더 집중하게 됩니다.

## 체크리스트

- [ ] 튜링 기계의 개념을 설명할 수 있는가
- [ ] 정지 문제가 왜 풀 수 없는지 이해했는가
- [ ] 명령형, 함수형, 객체지향의 차이를 구분할 수 있는가
- [ ] 컴파일러와 인터프리터의 차이를 이해했는가
- [ ] Python의 실행 방식(바이트코드 + VM)을 파악했는가

## 연습 문제

1. 괄호 문자열의 균형을 판단하는 간단한 상태 기계를 직접 구현해 보세요.
2. 리스트에서 짝수만 골라 제곱합을 구하는 기능을 명령형과 함수형 두 스타일로 각각 작성해 보세요.
3. `dis.dis()`로 작은 함수 세 개의 바이트코드를 비교하고 어떤 연산이 생성되는지 적어 보세요.

## 정리 및 다음 단계

계산은 입력을 규칙에 따라 변환하는 과정이며, 튜링 기계가 그 이론적 모델입니다. 모든 문제가 계산으로 풀리는 것은 아닙니다(정지 문제). 프로그래밍 언어는 계산을 인간이 읽을 수 있게 표현하며, 패러다임은 코드를 조직하는 철학입니다.

다음 글에서는 컴퓨터가 데이터를 어떻게 표현하는지 — 이진수, 문자 인코딩, 자료형을 다룹니다.

## 처음 질문으로 돌아가기

- **무엇을 두고 계산 가능하다고 말할 수 있을까요?**
  - 본문의 기준은 계산과 프로그램를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **튜링 기계는 왜 오늘날의 컴퓨터를 설명하는 기준 모델로 남아 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **정지 문제처럼 원리적으로 풀 수 없는 문제는 무엇을 의미할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- **계산과 프로그램 (현재 글)**
- 데이터 표현 (예정)
- 알고리즘과 복잡도 (예정)
- 컴퓨터 구조 (예정)
- 운영체제 (예정)
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Alan Turing — On Computable Numbers (1936)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [Stanford Encyclopedia of Philosophy — The Church-Turing Thesis](https://plato.stanford.edu/entries/church-turing/)
- [SICP — Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Programming Paradigms for Dummies (Peter Van Roy)](https://www.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)

Tags: Computer Science, 계산 모델, 튜링 기계, 프로그래밍 패러다임, 컴파일러, 인터프리터
