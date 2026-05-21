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


![Computer Science 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/02/02-01-concept-at-a-glance.ko.png)
*Computer Science 101 2장 흐름 개요*

## 먼저 던지는 질문

- 무엇을 두고 계산 가능하다고 말할 수 있을까요?
- 튜링 기계는 왜 오늘날의 컴퓨터를 설명하는 기준 모델로 남아 있을까요?
- 정지 문제처럼 원리적으로 풀 수 없는 문제는 무엇을 의미할까요?

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

## 튜링 기계를 Python으로 시뮬레이션하기

앞서 상태 기계의 기본 개념을 봤습니다. 이제 좀 더 정교한 튜링 기계를 직접 구현해 보겠습니다. 이 시뮬레이터는 테이프, 헤드, 상태 전이 규칙을 갖춘 완전한 형태입니다.

```python
class TuringMachine:
    """간단한 튜링 기계 시뮬레이터."""

    def __init__(self, tape: list[str], rules: dict, start_state: str, halt_states: set[str]):
        self.tape = list(tape)
        self.head = 0
        self.state = start_state
        self.halt_states = halt_states
        self.rules = rules  # (state, symbol) -> (new_state, write_symbol, direction)
        self.steps = 0

    def step(self) -> bool:
        if self.state in self.halt_states:
            return False
        symbol = self.tape[self.head] if self.head < len(self.tape) else "B"
        key = (self.state, symbol)
        if key not in self.rules:
            return False
        new_state, write, direction = self.rules[key]
        if self.head >= len(self.tape):
            self.tape.append("B")
        self.tape[self.head] = write
        self.head += 1 if direction == "R" else -1 if direction == "L" else 0
        self.state = new_state
        self.steps += 1
        return True

    def run(self, max_steps: int = 1000) -> str:
        while self.step() and self.steps < max_steps:
            pass
        return "".join(self.tape).rstrip("B")


# 이진수에 1을 더하는 튜링 기계
# 입력: "1011" (11 in decimal) -> 출력: "1100" (12 in decimal)
rules = {
    # 오른쪽 끝으로 이동
    ("start", "0"): ("start", "0", "R"),
    ("start", "1"): ("start", "1", "R"),
    ("start", "B"): ("carry", "B", "L"),
    # 캐리 전파
    ("carry", "0"): ("done", "1", "L"),
    ("carry", "1"): ("carry", "0", "L"),
    ("carry", "B"): ("done", "1", "S"),
}

tm = TuringMachine(
    tape=list("1011"),
    rules=rules,
    start_state="start",
    halt_states={"done"},
)
result = tm.run()
print(f"1011 + 1 = {result}")  # 1100
print(f"수행한 단계 수: {tm.steps}")
```

이 예제의 핵심은 단순합니다. 튜링 기계는 테이프(메모리), 헤드(현재 위치), 상태(프로그램 카운터), 규칙(프로그램)으로 구성됩니다. 오늘날의 컴퓨터는 이 모델의 물리적 구현입니다. RAM이 테이프이고, CPU 레지스터가 헤드와 상태이며, 명령어 세트가 규칙입니다.

### 계산 가능성의 경계: 실용적 의미

정지 문제가 풀 수 없다는 사실은 이론적 호기심으로 끝나지 않습니다. 실무에서 만나는 여러 문제가 이 한계에서 직접 파생됩니다.

| 불가능한 것 | 실무적 대안 |
| --- | --- |
| 모든 프로그램의 종료를 판정 | 타임아웃, 워치독 |
| 완벽한 바이러스 탐지기 | 서명 기반 + 행동 기반 휴리스틱 |
| 완벽한 정적 분석기 | 근사 분석 + 테스트 병행 |
| 두 프로그램의 동치 판정 | 같은 테스트 슈트 통과 확인 |
| 최적 컴파일러 | 휴리스틱 최적화 패스 |

이 표가 말해주는 것은, "완벽한 자동화"가 원리적으로 불가능한 영역이 있다는 점입니다. 그래서 엔지니어는 완벽함 대신 "충분히 좋은" 근사와 안전장치를 조합합니다.

## 프로그래밍 패러다임 비교: 같은 문제를 세 가지로 풀기

명령형, 함수형, 객체지향 패러다임을 같은 문제에 적용해 보겠습니다. 문제는 "단어 목록에서 길이가 4 이상인 단어만 골라 대문자로 바꾸기"입니다.

```python
words = ["cat", "elephant", "dog", "butterfly", "ant", "whale"]

# 명령형: 어떻게(how) 하는지 단계별로 지시
result_imperative = []
for word in words:
    if len(word) >= 4:
        result_imperative.append(word.upper())
print(f"명령형: {result_imperative}")

# 함수형: 무엇을(what) 원하는지 선언
result_functional = list(map(str.upper, filter(lambda w: len(w) >= 4, words)))
print(f"함수형: {result_functional}")

# 리스트 내포 (Python 고유의 선언적 스타일)
result_comprehension = [w.upper() for w in words if len(w) >= 4]
print(f"내포식: {result_comprehension}")
```

세 접근 모두 같은 결과를 냅니다. 차이는 의도를 드러내는 방식입니다.

| 패러다임 | 장점 | 단점 | 적합한 상황 |
| --- | --- | --- | --- |
| 명령형 | 실행 흐름이 명확, 디버깅 쉬움 | 길어지면 의도가 묻힘 | 상태 변화가 핵심인 로직 |
| 함수형 | 부수효과 없음, 조합성 높음 | 깊은 중첩 시 가독성 저하 | 데이터 변환 파이프라인 |
| 객체지향 | 상태와 행동을 캡슐화 | 과도한 클래스 계층 위험 | 도메인 모델링, 상태 관리 |

### 컴파일과 인터프리트: 바이트코드 깊이 보기

Python의 실행 과정을 한 단계 더 들여다보겠습니다.

```python
import dis
import sys

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 바이트코드 출력
print("=== fibonacci 바이트코드 ===")
dis.dis(fibonacci)

# 코드 객체의 상수와 변수 정보
code = fibonacci.__code__
print(f"\n상수(co_consts): {code.co_consts}")
print(f"지역변수(co_varnames): {code.co_varnames}")
print(f"바이트코드 크기: {len(code.co_code)} bytes")
print(f"Python 버전: {sys.version}")
```

바이트코드를 읽을 줄 알면 두 가지 실무 이점이 있습니다. 첫째, 성능 병목을 코드 수준이 아니라 연산 수준에서 파악할 수 있습니다. 둘째, 동일한 로직을 다르게 쓴 코드가 실제로 같은 바이트코드를 생성하는지 확인해 불필요한 최적화를 피할 수 있습니다.

## 계산 모델과 현대 시스템의 연결

튜링 기계는 1936년에 제안되었지만, 오늘날의 시스템에서도 그 핵심 원리가 그대로 적용됩니다.

| 튜링 기계 구성 요소 | 현대 시스템 대응 | 설명 |
| --- | --- | --- |
| 무한 테이프 | RAM + 디스크 + 클라우드 스토리지 | 가상 메모리로 거의 무한하게 확장 |
| 헤드 이동 | 메모리 주소 접근 | 포인터, 인덱스가 헤드 역할 |
| 상태 전이 | CPU의 명령어 실행 | Program Counter가 현재 상태 |
| 전이 규칙 | 프로그램 (명령어 집합) | 코드가 곧 규칙 |
| 정지 상태 | 프로그램 종료, return | exit code 반환 |

분산 시스템도 이 프레임워크를 확장한 것입니다. 여러 튜링 기계가 네트워크로 연결되어 메시지를 교환하는 모델로 설명됩니다. 합의 알고리즘(Raft, Paxos)은 분산된 상태 기계들이 같은 상태 전이를 보장하는 방법입니다.


### 컴파일 파이프라인 단계별 변환 예시

소스 코드가 실행 파일이 되기까지 거치는 단계를 C 언어로 추적합니다.

```text
[소스 코드]  →  [전처리]  →  [컴파일]  →  [어셈블리]  →  [링킹]  →  [실행 파일]
 hello.c        hello.i       hello.s       hello.o        a.out
```

```c
// hello.c
#include <stdio.h>
#define MSG "Hello"
int main(void) {
    printf("%s\n", MSG);
    return 0;
}
```

**전처리 단계** (`gcc -E hello.c -o hello.i`): `#include`가 헤더 내용으로 치환되고, `MSG`가 `"Hello"`로 대체됩니다. 이 단계는 텍스트 치환이므로 계산 이론의 문자열 재작성 시스템과 대응됩니다.

**컴파일 단계** (`gcc -S hello.i -o hello.s`): 토큰화 → 구문 분석 → 의미 분석 → 중간 표현(IR) → 최적화 → 어셈블리 생성 순서를 거칩니다. 최적화 단계에서 상수 전파, 죽은 코드 제거, 루프 언롤링 등이 적용됩니다.

**어셈블리 단계** (`as hello.s -o hello.o`): 사람이 읽을 수 있는 어셈블리를 기계어 바이트로 변환합니다. 이 시점에서 심볼 테이블이 생성되고, 외부 함수(`printf`)는 아직 주소가 미정입니다.

**링킹 단계** (`ld hello.o -lc -o a.out`): 미정이던 외부 심볼을 라이브러리에서 찾아 주소를 확정합니다. 정적 링킹은 라이브러리 코드를 복사하고, 동적 링킹은 런타임에 공유 라이브러리를 로드합니다.
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


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

계산 가능성과 프로그램 모델을 학습할 때는 동일 문제를 명령형과 함수형 스타일로 각각 표현해 모델 차이를 체감하는 연습이 효과적입니다.

### 학습 팁: 계산 모델을 문제 해결 습관으로 전환하기

같은 문제를 단계적 정제 방식으로 세 번 표현해 보면 계산 모델의 차이가 명확해집니다. 첫 번째는 자연어 절차, 두 번째는 의사코드, 세 번째는 실제 코드로 작성합니다. 이때 각 단계에서 상태 변화, 종료 조건, 실패 조건을 명시하면 프로그램의 정확성을 빠르게 검토할 수 있습니다. 특히 반례 입력을 먼저 고르는 습관을 들이면 구현 전에 결함 가능성을 줄일 수 있습니다.

### 과목 연결: 계산 이론에서 시스템 설계로

계산 모델 이해는 이후 분산 시스템과 데이터 처리 파이프라인 설계에서 직접 활용됩니다. 어떤 연산을 어디에서 수행할지 결정할 때 계산 비용과 통신 비용을 분리해 보는 습관이 필요합니다. 예를 들어 동일한 집계를 클라이언트에서 할지 서버에서 할지 결정할 때, 입력 크기 증가에 따른 계산량과 네트워크 전송량을 함께 비교하면 더 안정적인 설계를 선택할 수 있습니다.

## 처음 질문으로 돌아가기

- **무엇을 두고 계산 가능하다고 말할 수 있을까요?**
  - 유한한 단계 안에 답을 내는 절차(알고리즘)가 존재하면 계산 가능합니다. 튜링 기계로 시뮬레이션할 수 있는 문제가 곧 계산 가능한 문제입니다. 이 정의가 중요한 이유는 "풀 수 없는 문제"의 존재를 알아야 실무에서 완벽한 자동화 대신 실용적 근사를 선택할 수 있기 때문입니다.
- **튜링 기계는 왜 오늘날의 컴퓨터를 설명하는 기준 모델로 남아 있을까요?**
  - 본문에서 구현한 것처럼 튜링 기계는 테이프(메모리), 헤드(접근 위치), 상태(프로그램 카운터), 규칙(프로그램)이라는 최소 구성으로 모든 계산을 표현합니다. 이보다 더 강력한 계산 모델은 알려져 있지 않으며(처치-튜링 논제), 따라서 어떤 프로그래밍 언어든 계산 능력은 동일합니다.
- **정지 문제처럼 원리적으로 풀 수 없는 문제는 무엇을 의미할까요?**
  - 완벽한 정적 분석기, 완벽한 바이러스 탐지기, 두 프로그램이 같은 결과를 내는지 판정하는 도구는 원리적으로 만들 수 없습니다. 그래서 실무에서는 타임아웃, 테스트, 휴리스틱 같은 근사적 접근을 조합하여 "충분히 좋은" 수준의 검증을 달성합니다.

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
- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)

Tags: Computer Science, 계산 모델, 튜링 기계, 프로그래밍 패러다임, 컴파일러, 인터프리터
