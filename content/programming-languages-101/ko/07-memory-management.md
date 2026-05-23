---
series: programming-languages-101
episode: 7
title: "Programming Languages 101 (7/10): 메모리 관리"
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
  - Programming Languages
  - MemoryManagement
  - GC
  - Stack
  - Heap
seo_description: 스택/힙의 차이와 참조 카운팅, 순환 참조를 해결하는 GC 원리를 정리합니다. GC 환경에서도 누수가 생기는 이유와 관리 도구를 다룹니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (7/10): 메모리 관리

`del x`를 썼다고 해서 그 줄에서 객체가 바로 사라지는 것은 아닙니다. 이름과 객체, 참조와 수명은 서로 다른 층위에 있고, 언어는 그 관계를 각자 다른 방식으로 관리합니다.

이 글에서는 메모리 관리를 “이 객체는 언제 살아 있고 언제 죽는가”를 정하는 규칙으로 보겠습니다. 스택과 힙, 참조 카운팅, 가비지 컬렉션, 약한 참조를 차례로 보면서 GC가 있어도 누수가 생기는 이유까지 함께 정리하겠습니다.

![Programming Languages 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/07/07-01-concept-at-a-glance.ko.png)
*Programming Languages 101 7장 흐름 개요*

## 먼저 던지는 질문

- 스택과 힙은 어떻게 다를까요?
- Python의 참조 카운팅은 언제 객체를 즉시 해제할까요?
- 순환 참조는 왜 가비지 컬렉터가 따로 필요할까요?

## 왜 중요한가

오래 실행되는 서비스는 메모리가 조금씩 올라가는 문제를 자주 겪습니다. 그때 필요한 질문은 “왜 이 객체가 아직 살아 있지?”입니다. 메모리 모델을 모르면 이 질문에 답할 수 없고, 누수 원인을 찾는 일도 막연해집니다.

## 핵심 개념 한눈에 보기

함수 호출이 끝나면 스택 프레임은 자동으로 사라집니다. 반면 힙에 있는 객체는 누가 더 참조하는지 따로 추적해야 합니다. CPython은 참조 카운팅과 순환 수집기를 함께 사용해 이 문제를 풉니다.

## 먼저 알아둘 용어

- 스택: 함수 호출과 함께 생기고 사라지는 메모리 영역입니다.
- 힙: 객체를 할당해 두는 영역으로, 별도 회수가 필요합니다.
- 참조 카운팅: 객체를 가리키는 참조 수를 세다가 0이 되면 해제합니다.
- 가비지 컬렉션: 도달 가능한 객체를 따라가며 살아 있는 것만 남깁니다.
- 순환 참조: A가 B를, B가 다시 A를 가리키는 구조입니다.

## 먼저 보는 예시

### 수동 해제 방식의 감각

```python
# 의사코드: 무료는 잊어버리고 영원히 누출됨
buf = malloc(1024)
use(buf)
# free(buf) ← 이것을 건너뛰면 1KB가 계속 유지됩니다
```

수동 해제 모델에서는 마지막 `free`를 잊는 순간 누수가 시작됩니다.

### 이름이 사라질 때 객체 수명 보기

```python
def work() -> None:
    buf = bytearray(1024)
    use(buf)
# work()가 반환되면 buf는 갈 곳이 없어 회수됩니다
```

이름이 사라지고 다른 참조도 없다면 객체는 수명을 다합니다. 다만 “이름이 사라진다”와 “객체가 즉시 해제된다”를 같은 말로 보면 자꾸 헷갈립니다.

## 객체 수명을 직접 따라가 보기

### 1단계 — 참조 카운트 보기

```python
# 1_refcount.py
import sys

class Tag:
    def __del__(self) -> None:
        print("Tag deleted")

t = Tag()
print(sys.getrefcount(t))  # 2 (the variable t + getrefcount's argument)
ref = t
print(sys.getrefcount(t))  # 3
del ref, t                  # all references gone → __del__ fires immediately
```

CPython에서는 참조 수가 0이 되는 순간 객체가 곧바로 정리되는 경우가 많습니다. `sys.getrefcount`가 호출 인자로 인해 1 더 크게 보인다는 점만 기억하면 됩니다.

### 2단계 — 순환 참조와 가비지 컬렉터

```python
# 2_cycle.py
import gc

class Node:
    def __init__(self) -> None:
        self.peer: "Node | None" = None
    def __del__(self) -> None:
        print("Node deleted")

a, b = Node(), Node()
a.peer, b.peer = b, a   # they reference each other
del a, b                 # counts never reach zero
print("before collect")
gc.collect()             # the tracing GC sweeps up the cycle
print("after collect")
```

서로만 참조하는 객체는 참조 수만으로는 정리되지 않습니다. 그래서 CPython은 보조적인 추적 기반 수집기를 함께 둡니다.

### 3단계 — 죽지 않는 객체 만들기

```python
# 3_leak.py
cache: dict[int, bytes] = {}

def remember(i: int) -> None:
    cache[i] = b"x" * 1024  # cache only ever grows

for i in range(1000):
    remember(i)

print(len(cache), "items still alive")
```

GC가 있든 없든 참조가 남아 있으면 객체는 계속 살아 있습니다. 누수의 본질은 잊힌 해제가 아니라 잊히지 않은 참조인 경우가 많습니다.

### 4단계 — 약한 참조 사용하기

```python
# 4_weakref.py
import weakref

class Big:
    pass

obj = Big()
ref = weakref.ref(obj)
print(ref())   # <__main__.Big object ...>
del obj
print(ref())   # None  — a weak reference does not extend lifetime
```

캐시나 옵저버 목록처럼 수명을 늘리고 싶지 않은 참조에는 `weakref`가 표준 도구입니다.

### 5단계 — 블록으로 자원 수명 드러내기

```python
# 5_with.py
from contextlib import contextmanager

@contextmanager
def opened(name: str):
    print("open", name)
    try:
        yield name
    finally:
        print("close", name)

with opened("config.yml") as f:
    print("use", f)
# 블록을 벗어나면 close가 보장됩니다
```

메모리만 수명을 가지는 것은 아닙니다. 파일, 소켓, 락도 모두 수명 관리가 필요합니다. `with`는 그 의도를 코드 모양으로 드러내는 가장 좋은 패턴입니다.

## 이 코드에서 먼저 볼 점

- 참조 수가 0이 되면 객체가 즉시 정리될 수 있다는 점이 CPython의 중요한 특징입니다.
- 순환 참조는 참조 카운팅만으로 풀 수 없기 때문에 추적 기반 GC가 필요합니다.
- GC 언어에서도 참조가 남아 있으면 객체는 살아 있습니다.
- `weakref`와 `with`는 메모리뿐 아니라 자원 수명 전반을 다루는 도구입니다.

## 자주 하는 실수

1. `del`이 객체를 즉시 파괴한다고 믿습니다. 실제로는 이름 바인딩을 끊을 뿐입니다.
2. 크기 제한 없는 전역 캐시를 둡니다. 아주 흔한 누수 패턴입니다.
3. 순환 참조를 무시합니다. 도메인 객체가 서로를 오래 붙잡는 구조가 흔합니다.
4. `__del__`에 무거운 정리 로직을 넣습니다. 진짜 정리는 `with`나 명시적 `close`가 더 안전합니다.
5. 뜨거운 경로에서 `gc.collect()`를 남발합니다. CPU만 태우는 경우가 많습니다.

## 실무에서는 이렇게 본다

오래 실행되는 서버는 메모리 그래프를 지속적으로 봅니다. 이상 징후가 보이면 `tracemalloc`이나 `objgraph`로 어떤 객체가 늘어나는지 확인합니다. 캐시에는 항상 크기 제한이나 TTL을 넣고, 콜백이나 옵저버 목록에는 약한 참조나 명시적 해제를 기본값으로 둡니다.

C, C++, Rust는 또 다른 길을 갑니다. Rust는 GC 대신 소유권을 컴파일 시점에 검사합니다. 구현은 달라도 질문은 같습니다. “이 객체를 누가 소유하고, 언제 놓는가?” 이 질문에 답할 수 있어야 메모리 문제를 제대로 다룰 수 있습니다.

## 체크리스트

- [ ] 스택과 힙의 차이를 한 문장으로 말할 수 있는가?
- [ ] Python의 참조 카운팅과 GC가 어떻게 협력하는지 설명할 수 있는가?
- [ ] 최근 코드에서 잠재적 누수 지점을 하나 짚을 수 있는가?
- [ ] `weakref`를 써야 할 대표 상황을 하나 이상 말할 수 있는가?
- [ ] 자원 수명 관리에 `with`를 자연스럽게 쓰는가?

## 연습 문제

1. 순환 참조 예제에서 한쪽을 `weakref`로 바꿔 `gc.collect()` 없이도 정리되는지 확인해 보세요.
2. `tracemalloc`으로 객체를 많이 만들고 지우는 실험을 한 뒤, 관찰한 패턴을 한 단락으로 적어 보세요.
3. 최근에 만든 캐시 하나를 골라 크기 제한이 있는 형태로 바꿔 보세요.

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

## 정리

메모리 모델은 결국 “누가 붙잡고 있고, 언제 손을 놓는가”를 설명하는 규칙입니다. 다음 글에서는 이 객체와 코드를 실제로 실행하는 두 가지 큰 전략인 인터프리터와 컴파일러를 보겠습니다.

## 처음 질문으로 돌아가기

- **스택과 힙은 어떻게 다를까요?**
  - 본문의 기준은 메모리 관리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Python의 참조 카운팅은 언제 객체를 즉시 해제할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **순환 참조는 왜 가비지 컬렉터가 따로 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- **메모리 관리 (현재 글)**
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python — gc module](https://docs.python.org/3/library/gc.html)
- [Python — weakref module](https://docs.python.org/3/library/weakref.html)
- [Python — tracemalloc](https://docs.python.org/3/library/tracemalloc.html)
- [Garbage collection (Wikipedia)](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science))

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, MemoryManagement, GC, Stack, Heap
