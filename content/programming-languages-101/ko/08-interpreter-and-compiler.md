---
episode: 8
language: ko
last_reviewed: '2026-05-15'
seo_description: 인터프리터와 컴파일러가 소스 코드 번역 시점을 달리하는 방식과 실행 성능, 디버깅 경험에 미치는 영향을 비교합니다.
series: programming-languages-101
status: publish-ready
tags:
- Computer Science
- Programming Languages
- Interpreter
- Compiler
- JIT
- Bytecode
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Programming Languages 101 (8/10): 인터프리터와 컴파일러"
---

# Programming Languages 101 (8/10): 인터프리터와 컴파일러

Python을 흔히 인터프리터 언어라고 부릅니다. 그런데 `.pyc` 파일도 있습니다. 그렇다면 Python은 해석하는 언어일까요, 컴파일하는 언어일까요.

이 글에서는 인터프리터와 컴파일러를 서로 반대 진영으로 보지 않고, 번역이 언제 일어나는지가 다른 두 전략으로 보겠습니다. Python 바이트코드를 직접 들여다보고, AOT와 JIT가 어디서 갈라지는지도 함께 정리하겠습니다.

![Programming Languages 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/08/08-01-concept-at-a-glance.ko.png)
*Programming Languages 101 8장 흐름 개요*

## 먼저 던지는 질문

- 인터프리터와 컴파일러의 가장 짧은 차이는 무엇일까요?
- Python은 실제로 어떤 실행 경로를 거칠까요?
- `.pyc` 파일은 정확히 무엇일까요?

## 왜 중요한가

성능 문제가 생겼을 때 “이 줄이 실제로 어떤 형태로 실행되는가”를 설명할 수 있으면 감으로 디버깅하지 않게 됩니다. 같은 코드가 인터프리터, JIT, AOT 환경에서 왜 다르게 보이는지도 이 시점 차이로 정리할 수 있습니다.

## 핵심 개념 한눈에 보기

CPython은 보통 소스 코드를 바이트코드로 만든 뒤 가상 머신이 한 명령씩 실행합니다. JVM 계열은 자주 실행되는 경로를 JIT로 네이티브 코드로 올리고, C나 Rust는 아예 미리 기계어로 컴파일합니다.

## 먼저 알아둘 용어

- 컴파일러: 소스 코드를 다른 형태로 미리 번역합니다.
- 인터프리터: 실행 중에 코드를 한 단계씩 처리합니다.
- AOT: 전체를 미리 컴파일하고 실행합니다.
- JIT: 실행 중 자주 쓰이는 부분만 골라 컴파일합니다.
- 바이트코드: 소스와 기계어 사이에 놓인 중간 표현입니다.

## 먼저 보는 예시

### 막연한 그림

```text
.py file → ??? → result
```

### 실제로 일어나는 일

```text
.py → tokenize → parse → AST → compile → .pyc bytecode → VM executes one op at a time
```

`.pyc`는 캐시된 바이트코드입니다. Python에도 분명한 컴파일 단계가 있고, 다만 그 결과를 인터프리터가 실행한다는 점이 중요합니다.

## 파이썬 실행 내부를 직접 들여다보기

### 1단계 — 바이트코드 읽기

```python
# 1_dis.py
import dis

def add(a: int, b: int) -> int:
    return a + b

dis.dis(add)
```

여기서 보이는 `LOAD_FAST`, `BINARY_OP`, `RETURN_VALUE` 같은 한 줄이 Python 가상 머신의 한 단계입니다. 성능을 얘기할 때 생각보다 유용한 단위입니다.

### 2단계 — 같은 알고리즘, 다른 명령 수

```python
# 2_optimization.py
import dis

def slow(xs):
    s = 0
    for x in xs:
        s = s + x
    return s

def fast(xs):
    return sum(xs)

print("--- slow ---"); dis.dis(slow)
print("--- fast ---"); dis.dis(fast)
```

`fast`는 훨씬 짧습니다. `sum` 내부 루프가 C로 구현돼 있기 때문에 Python VM이 처리해야 할 명령 수가 크게 줄어듭니다.

### 3단계 — 바이트코드 캐시 파일 확인하기

```python
# 3_pyc.py
import py_compile, dis, marshal, importlib.util, pathlib

src = pathlib.Path("/tmp/sample.py")
src.write_text("def f(): return 42\n")
pyc = py_compile.compile(str(src), doraise=True)

with open(pyc, "rb") as f:
    f.read(16)                # 16-byte header on Python 3.7+
    code = marshal.load(f)
dis.dis(code)
```

`.pyc`는 헤더와 직렬화된 코드 객체의 조합입니다. 이후 import에서는 이 결과를 재사용해 파싱과 컴파일 비용을 줄입니다.

### 4단계 — 미리 번역해 두는 감각 보기

```python
# 4_compile_call.py
import time

PY_SRC = "result = sum(range(10_000_000))"
code = compile(PY_SRC, "<inline>", "exec")

t0 = time.perf_counter(); exec(code, {}); t1 = time.perf_counter()
print("compiled-once exec:", t1 - t0)

t0 = time.perf_counter()
for _ in range(3):
    exec(PY_SRC, {})           # compiled fresh each iteration
print("recompiled each time:", time.perf_counter() - t0)
```

한 번 번역한 결과를 여러 번 실행하면 더 빠릅니다. 이것이 AOT가 주는 기본 직관입니다.

### 5단계 — 뜨거운 경로만 올리는 전략 보기

```python
# 5_hot_path.py
from collections import Counter

calls: Counter[str] = Counter()

def trace(name: str) -> None:
    calls[name] += 1

for _ in range(1_000_000):
    trace("inner")             # one million calls — JIT would target this
trace("outer")                  # only once

print(calls.most_common(2))
```

JIT는 이런 호출 빈도를 보다가 충분히 뜨거운 경로만 골라 네이티브 코드로 올립니다. 모든 것을 미리 컴파일하지도 않고, 모든 것을 끝까지 해석하지도 않는 실용적인 절충안입니다.

## 이 코드에서 먼저 볼 점

- Python을 인터프리터 언어라고 부르는 말은 주로 실행 단계를 가리킵니다.
- `dis` 출력 한 줄은 VM의 한 사이클에 가깝습니다.
- `.pyc`는 신비한 실행 파일이 아니라 캐시된 바이트코드입니다.
- JIT는 “전부 컴파일”과 “전부 해석” 사이의 현실적인 중간 지점입니다.

## 자주 하는 실수

1. 인터프리터와 컴파일러를 진영 싸움처럼 봅니다. 실제로는 번역 시점의 차이입니다.
2. `.pyc`를 독립 실행 파일처럼 생각합니다. 여전히 Python VM이 필요합니다.
3. 진짜 해결책이 C 구현 라이브러리 사용인데도 알고리즘을 먼저 갈아엎습니다.
4. JIT가 언제나 빠르다고 생각합니다. 짧은 실행에서는 워밍업 비용이 더 클 수 있습니다.
5. `dis`를 한 번도 열어 보지 않고 성능을 추측합니다.

## 실무에서는 이렇게 본다

CPython은 바이트코드 캐시와 인터프리터만으로도 대부분의 작업을 충분히 처리합니다. 수치 계산처럼 뜨거운 경로는 NumPy나 PyTorch처럼 내부가 C/C++로 구현된 라이브러리에 넘기는 편이 흔합니다. PyPy는 같은 Python 코드를 JIT로 돌려 단순 루프에서 큰 차이를 보이기도 합니다.

JVM은 기본적으로 JIT 경로를 탑니다. Go, Rust, C는 AOT라서 시작이 빠르고 배포 형태도 단순합니다. 결국 중요한 것은 “어느 쪽이 더 우월한가”가 아니라 “이 워크로드에 어떤 실행 모델이 맞는가”입니다.

## 체크리스트

- [ ] 인터프리터와 컴파일러의 차이를 한 줄로 설명할 수 있는가?
- [ ] `dis`로 함수 바이트코드를 읽어 본 적이 있는가?
- [ ] `.pyc`가 무엇인지 한 문장으로 설명할 수 있는가?
- [ ] AOT와 JIT의 차이를 말할 수 있는가?
- [ ] 뜨거운 루프를 C 구현 라이브러리로 내리는 패턴을 알고 있는가?

## 연습 문제

1. `slow`와 `fast`를 큰 입력으로 측정한 뒤, 성능 차이를 `dis` 출력과 연결해 설명해 보세요.
2. 같은 루프를 PyPy나 Cython 같은 다른 실행 모델에서 돌려 보고 차이를 적어 보세요.
3. 자주 쓰는 모듈 하나에서 `compileall`을 돌린 뒤 import 시간 변화를 관찰해 보세요.

## 심화 실전 노트: 타입, 스코프, 메모리 모델을 한 번에 연결하기

프로그래밍 언어를 실제로 운영 코드에 적용할 때는 문법 지식만으로 충분하지 않습니다. 타입 시스템이 어떤 오류를 언제 잡는지, 스코프 규칙이 상태 변경과 캡처를 어떻게 제한하는지, 메모리 모델이 동시성에서 어떤 가시성을 보장하는지를 한 묶음으로 이해해야 합니다. 이 세 축은 각각 독립 주제가 아니라, 코드 리뷰에서 같은 결함을 다른 이름으로 반복해서 만나게 만드는 공통 원인입니다.

### 타입 시스템 관점에서 보는 실패 패턴

다음 예시는 입력 파싱 이후 비즈니스 계층으로 전달되는 값의 타입이 느슨할 때 생기는 대표적인 문제를 보여줍니다.

```python
from typing import TypedDict, Literal

class PaymentCommand(TypedDict):
    order_id: str
    amount: int
    currency: Literal["KRW", "USD"]

def apply_discount(cmd: PaymentCommand) -> PaymentCommand:
    if cmd["currency"] == "KRW":
        cmd["amount"] = int(cmd["amount"] * 0.95)
    return cmd
```

핵심은 금액이 숫자라는 사실만으로 충분하지 않다는 점입니다. 정수인지, 소수점 정책이 무엇인지, 통화별 반올림 규칙이 무엇인지가 타입 설계에 반영되어야 합니다. 실무에서는 `int` 하나로 시작해 빠르게 배포한 뒤 정산 단계에서 누적 오차를 발견하는 일이 자주 발생합니다. 따라서 도메인 타입을 좁히는 전략이 필요합니다. 예를 들어 금액을 `Money` 값 객체로 감싸고, 생성 시점에 통화와 스케일을 강제하면 연산 단계를 통과하는 데이터 품질이 크게 올라갑니다.

### 스코프와 클로저를 리뷰할 때 보는 체크 포인트

클로저 자체는 강력한 도구이지만, 루프 변수 캡처와 가변 상태 결합이 만나면 예상과 다른 동작이 나옵니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda: i)
    return handlers

print([h() for h in make_handlers()])  # [2, 2, 2]
```

위 코드는 각 단계의 `i`를 복사하지 않고 같은 이름 해석 지점을 참조합니다. 의도한 결과가 `[0, 1, 2]`라면 기본 인자로 값을 고정해야 합니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda i=i: i)
    return handlers
```

이 차이는 단순 문법 이슈가 아니라 스코프 체계의 본질입니다. 변수의 "값"을 캡처하는지, "이름 해석 규칙"을 캡처하는지 구분하지 못하면 비동기 콜백, 이벤트 핸들러, 지연 실행 코드에서 재현 어려운 버그가 생깁니다.

### 메모리 모델을 읽는 최소 다이어그램

동시성 코드를 검토할 때는 아래처럼 책임 경계를 먼저 그려 두면 문제 재현과 해결 속도가 빨라집니다.

```text
[Thread A] write shared_flag=True
      |
      |  (reorder 가능성, 캐시 지연)
      v
[Memory Visibility Boundary]
      |
      v
[Thread B] read shared_flag
```

언어와 런타임은 이 경계에서 서로 다른 규칙을 제공합니다. 어떤 언어는 메모리 장벽이나 원자 연산을 명시적으로 요구하고, 어떤 언어는 메시지 전달 모델로 공유 메모리 자체를 줄입니다. 따라서 "동작한다"는 테스트 한 번으로 안전성을 결론 내리면 안 됩니다. 스레드 스케줄이 바뀌어도 같은 결과가 유지되는지, happens-before 관계가 코드 구조에 드러나는지 확인해야 합니다.

### 통합 적용 예시: 타입 + 스코프 + 메모리

작은 작업 큐 소비자를 예로 들면, 메시지 스키마를 엄격히 정의하고, 핸들러 생성 시 캡처 대상을 고정하고, 상태 공유를 최소화하는 세 가지를 함께 적용해야 안정성이 올라갑니다. 이 세 가지 중 하나만 빠져도 나머지 두 가지가 문제를 완전히 막아주지 못합니다. 결국 좋은 언어 사용 습관은 "문법 숙련"보다 "오류를 설계 단계에서 조기 차단하는 구조"에 가깝습니다.

### 추가 사례: 언어 설계 선택이 유지보수 비용에 미치는 영향

실무에서 타입, 스코프, 메모리 모델은 장애 보고서에서 따로 등장하지 않고 함께 엮여 나타납니다. 예를 들어 이벤트 소비자가 `dict[str, Any]`를 그대로 전달하면 타입 경계가 무너지고, 지연 실행 콜백이 외부 가변 상태를 캡처하면 스코프 결함이 생기며, 여러 워커가 같은 캐시 객체를 잠금 없이 접근하면 메모리 가시성 문제가 겹칩니다. 이런 결함은 단위 테스트 한두 개로는 쉽게 드러나지 않습니다.

그래서 언어 기능 선택을 할 때는 "지금 빨리 쓰기 쉬운가"보다 "오류를 조기에 막는가"를 기준으로 삼아야 합니다. 타입 힌트를 강제하고, 클로저 캡처 규칙을 리뷰 체크리스트에 넣고, 공유 상태 대신 메시지 전달을 우선하면 코드가 길어지더라도 운영 리스크가 크게 줄어듭니다. 결과적으로 좋은 설계는 문법의 화려함이 아니라, 팀이 반복 실수 없이 같은 문제를 안정적으로 푸는 능력으로 측정됩니다.

## 실전 시나리오: 장애를 줄이는 언어 설계 점검

현업에서 언어 개념을 배울 때 가장 빠른 방법은 장애 시나리오를 기준으로 역추적하는 것입니다. 아래는 주문 이벤트 처리 파이프라인을 가정한 점검 예시입니다. 핵심은 기능 구현보다 경계 확인입니다.

```text
입력(JSON) -> 역직렬화 -> 타입 검증 -> 규칙 실행 -> 상태 반영 -> 로그/메트릭
```

각 단계에서 질문을 고정하면 품질이 크게 올라갑니다. 역직렬화 단계에서는 필수 필드 누락을 즉시 중단하는가, 타입 검증 단계에서는 문자열/숫자 혼합을 허용하지 않는가, 규칙 실행 단계에서는 부수효과를 최소화했는가, 상태 반영 단계에서는 재시도 시 멱등성이 보장되는가를 확인해야 합니다.

### 미니 구현: 입력 검증과 멱등 키

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderEvent:
    event_id: str
    amount: int

def parse_event(raw: dict) -> OrderEvent:
    if "event_id" not in raw or "amount" not in raw:
        raise ValueError("missing required field")
    event_id = str(raw["event_id"]).strip()
    amount = int(raw["amount"])
    if amount < 0:
        raise ValueError("amount must be >= 0")
    return OrderEvent(event_id=event_id, amount=amount)
```

이 예시는 단순하지만 기준이 분명합니다. 입력을 받는 즉시 도메인 객체로 변환해 이후 단계의 가정을 안정화하고, `event_id`를 멱등 키로 사용해 중복 처리를 통제할 수 있습니다. 언어 기능 자체보다도, 타입 경계를 어디에서 확정하는지가 운영 안정성을 좌우합니다.

### REPL 확인

```text
$ python3
>>> from order_demo import parse_event
>>> parse_event({"event_id": "ev-1", "amount": "120"})
OrderEvent(event_id='ev-1', amount=120)
>>> parse_event({"event_id": "ev-2", "amount": -1})
Traceback (most recent call last):
  ...
ValueError: amount must be >= 0
```

짧은 REPL 검증을 반복하면 설계 문서의 문장이 실제 런타임에서 유지되는지 빠르게 확인할 수 있습니다. 이 습관이 쌓이면 언어를 바꿔도 문제 분석 속도와 리뷰 품질이 함께 유지됩니다.

### 리뷰 메모: 팀 합의로 남겨야 할 기준

- 실패 사례를 재현하는 입력 샘플을 저장소에 함께 보관합니다.
- 경계 타입은 문서가 아니라 코드 시그니처로 표현합니다.
- 동시성 또는 지연 실행 지점은 로그 키를 고정해 추적 가능하게 만듭니다.

이 세 가지를 릴리스 전 점검표에 포함하면, 언어와 프레임워크가 바뀌어도 품질 기준이 흔들리지 않습니다.

짧게 말해, 번역 단계별 관찰 포인트를 코드와 로그로 함께 남기면 성능 튜닝과 장애 분석 속도가 동시에 올라갑니다.

## 정리

인터프리터, 컴파일러, JIT는 서로 적대적인 개념이 아니라 같은 번역 문제에 대한 다른 답입니다. 다음 글에서는 실행 모델과 더불어 언어 성격을 크게 바꾸는 또 하나의 축, 정적과 동적 언어의 차이를 보겠습니다.

## 처음 질문으로 돌아가기

- **인터프리터와 컴파일러의 가장 짧은 차이는 무엇일까요?**
  - 본문의 기준은 인터프리터와 컴파일러를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Python은 실제로 어떤 실행 경로를 거칠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`.pyc` 파일은 정확히 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- **인터프리터와 컴파일러 (현재 글)**
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python — dis module](https://docs.python.org/3/library/dis.html)
- [Python — py_compile module](https://docs.python.org/3/library/py_compile.html)
- [PyPy — How does PyPy work?](https://doc.pypy.org/en/latest/architecture.html)
- [Just-in-time compilation (Wikipedia)](https://en.wikipedia.org/wiki/Just-in-time_compilation)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Interpreter, Compiler, JIT, Bytecode
