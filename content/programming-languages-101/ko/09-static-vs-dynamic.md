---
episode: 9
language: ko
last_reviewed: '2026-05-15'
seo_description: 정적 언어와 동적 언어가 타입 검사 시점을 달리하는 방식과 안정성, 표현력의 트레이드오프를 비교 분석합니다.
series: programming-languages-101
status: publish-ready
tags:
- Computer Science
- Programming Languages
- StaticTyping
- DynamicTyping
- Tradeoffs
- Safety
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Programming Languages 101 (9/10): 정적 언어와 동적 언어"
---

# Programming Languages 101 (9/10): 정적 언어와 동적 언어

정적 타입이 더 안전하다는 말은 자주 듣지만, 그 안전이 정확히 무엇을 덮는지 묻는 순간 답이 흐려지는 경우가 많습니다. 반대로 동적 언어가 더 빠르다는 말도 자주 나오지만, 실제로는 어떤 종류의 속도를 말하는지 구분이 필요합니다.

이 글은 Programming Languages 101 시리즈의 9번째 글입니다.

이 글에서는 정적 언어와 동적 언어를 우열의 문제가 아니라 검사 시점의 선택으로 보겠습니다. 같은 함수를 타입 힌트 없이 쓴 버전과 명시적으로 쓴 버전을 나란히 놓고, 어떤 종류의 오류를 언제 잡을 수 있는지 현실적으로 정리하겠습니다.

![Programming Languages 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/09/09-01-concept-at-a-glance.ko.png)
*Programming Languages 101 9장 흐름 개요*

> '정적 vs 동적'은 한 축이 아니라 '타입 / 바인딩 / 디스패치' 세 축에서 각각 다르게 갈라집니다 — Python은 동적 타입이지만 정적 바인딩이고, JS는 동적 타입·동적 바인딩이며, Java는 그 반대편입니다. 이 축들이 분리되어야 언어 비교가 흙탕물에서 빠져나옵니다.

## 먼저 던지는 질문

- 정적과 동적의 가장 짧은 정의는 무엇일까요?
- 같은 코드가 두 모델에서 어떻게 다르게 검증될까요?
- mypy나 pyright가 잡을 수 있는 것과 없는 것은 무엇일까요?

## 왜 중요한가

팀이 커질수록 “타입을 더 붙일까?”라는 논의가 반복됩니다. 이때 필요한 것은 신념이 아니라, 정적 검사가 무엇을 보장하고 무엇을 보장하지 않는지 한 문장으로 설명할 수 있는 감각입니다.

## 핵심 개념 한눈에 보기

같은 유형의 오류라도 어느 시점에 드러나는지가 다릅니다. 정적 타입은 실행 전에 막고, 동적 타입은 실행 흐름이 그 지점에 도달했을 때 드러냅니다.

## 먼저 알아둘 용어

- 정적 타입: 변수와 표현식의 타입을 실행 전에 검사합니다.
- 동적 타입: 값에 타입이 붙고, 검사는 실행 중에 이뤄집니다.
- 강한 타입과 약한 타입: 암묵적 형변환 허용 범위를 나타내는 별도 축입니다.
- 점진적 타입: 한 코드베이스 안에 정적 영역과 동적 영역을 함께 두는 방식입니다.
- 건전성: 검사기가 통과시킨 코드가 타입 규칙을 어기지 않는다는 보장입니다.

## 먼저 보는 예시

### 타입 힌트가 없는 함수

```python
def total(items):
    return sum(item.price for item in items)
```

호출자는 각 `item`이 `price`를 가진다고 스스로 가정해야 합니다. 잘못된 입력은 실행 중 `AttributeError`로 터집니다.

### 계약을 드러낸 함수

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    price: int

def total(items: list[Item]) -> int:
    return sum(item.price for item in items)
```

이제 호출자도 함께 검사 대상이 됩니다. 잘못된 입력을 더 앞 단계에서 막을 수 있습니다.

## 같은 코드를 두 모델로 비교하기

### 1단계 — 정적 검사기가 잡는 오류

```python
# 1_mypy.py
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))
print(add("1", "2"))   # mypy: error — incompatible argument
```

실행하지 않아도 두 번째 호출이 문제라는 사실을 알 수 있습니다. 정적 검사의 가장 직접적인 가치입니다.

### 2단계 — 여전히 실행 중에만 드러나는 오류

```python
# 2_runtime_only.py
import json

data = json.loads('{"price": "10"}')   # mypy sees dict[str, Any]
def total(items):
    return sum(i["price"] for i in items)
print(total([data]))                    # runtime TypeError
```

JSON, 데이터베이스, 환경 변수처럼 외부에서 들어오는 값은 컴파일 시점에 형태가 완전히 고정되지 않습니다. 정적 검사의 보장은 보통 코드 경계 안쪽까지입니다.

### 3단계 — 점진적 타입의 현실적인 쓰임

```python
# 3_gradual.py
def parse(raw: str) -> dict:        # only partly typed
    return eval(raw)                # dynamic region (and risky)

def use(d: dict[str, int]) -> int:  # precisely typed
    return sum(d.values())

print(use(parse('{"a": 1, "b": 2}')))
```

가장자리에서는 동적으로 받고, 안쪽 로직에서는 정적으로 다루는 식의 타협이 가능합니다. Python과 TypeScript가 널리 쓰이는 이유 중 하나가 여기에 있습니다.

### 4단계 — 구조가 같으면 통과시키기

```python
# 4_protocol.py
from typing import Protocol

class Pricable(Protocol):
    price: int

def total(items: list[Pricable]) -> int:
    return sum(i.price for i in items)

class Book:
    def __init__(self, price: int) -> None:
        self.price = price

print(total([Book(10), Book(20)]))   # OK — Book has the right shape
```

상속 관계가 없어도 필요한 형태만 맞으면 통과시킬 수 있습니다. 정적 검사 안에서도 덕 타이핑과 비슷한 감각을 살릴 수 있다는 말입니다.

### 5단계 — 동적 언어가 강한 지점

```python
# 5_dynamic_strength.py
def call_all(d: dict, *args):
    for name, fn in d.items():
        print(name, fn(*args))

ops = {
    "add": lambda x, y: x + y,
    "mul": lambda x, y: x * y,
}
call_all(ops, 3, 4)
```

플러그인이나 메타프로그래밍 같은 영역에서는 동적 언어의 표현력이 여전히 매력적입니다. 정적 언어로도 할 수 있지만 보일러플레이트가 늘어나는 경우가 많습니다.

### 6단계 — 경계 검증과 정적 검사를 함께 쓰기

```python
# 6_boundary_validation.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    price: int

def parse_item(raw: dict[str, object]) -> Item:
    price = raw.get("price")
    if not isinstance(price, int):
        raise ValueError("price must be int")
    return Item(price=price)

payload = {"price": 10}
item = parse_item(payload)
print(item.price + 5)  # 15
```

실무에서는 이 조합이 가장 자주 쓰입니다. 경계에서는 런타임 검증으로 데이터를 좁히고, 그다음부터는 정적 타입으로 도구 지원과 리팩터링 안전망을 얻습니다. 정적과 동적은 보통 경쟁자가 아니라 연속된 두 단계입니다.

## 이 코드에서 먼저 볼 점

- 정적 타입의 보장은 외부 입력이 들어오는 경계에서 끝나는 경우가 많습니다.
- 점진적 타입은 두 모델을 실용적으로 섞는 방식입니다.
- `Protocol`은 상속 없이도 “같은 모양”을 표현하게 해 줍니다.
- 짧은 스크립트나 메타프로그래밍처럼 동적 모델이 더 자연스러운 영역도 분명히 있습니다.

## 자주 하는 실수

1. 정적은 안전하고 동적은 위험하다고 단순화합니다. 둘은 다른 비용을 냅니다.
2. 타입 힌트만 붙이면 외부 입력 문제까지 해결된다고 믿습니다. 경계 검증은 별도입니다.
3. `Any`를 너무 많이 써서 점진적 타입을 사실상 포기합니다.
4. 힌트만 달고 검사기를 CI에 넣지 않습니다. 그러면 타입은 문서 이상의 역할을 못 합니다.
5. 타입과 테스트를 서로 대체재로 봅니다. 잡는 버그 종류가 다릅니다.

## 실무에서는 이렇게 본다

큰 Python 코드베이스는 이제 거의 예외 없이 mypy나 pyright를 CI에서 돌립니다. JavaScript 진영도 TypeScript를 사실상 표준처럼 받아들였습니다. 이때 성능보다 더 큰 이점은 유지보수입니다. 코드 경계가 많아질수록 타입 정보가 문서와 자동 완성과 리팩터링 안전망 역할을 같이 해 주기 때문입니다.

요즘 많이 쓰는 패턴은 경계에서 강하게 검증하고, 내부에서는 정밀하게 타입을 다루는 방식입니다. `pydantic`, `dataclass`, `Protocol`이 자주 함께 등장하는 이유도 이 조합이 실무에서 잘 맞기 때문입니다.

## 체크리스트

- [ ] 정적과 동적의 차이를 한 줄로 설명할 수 있는가?
- [ ] mypy나 pyright를 CI에서 돌리고 있는가?
- [ ] 외부 입력이 들어오는 경계에 검증이 있는가?
- [ ] `Any` 사용량을 의식적으로 관리하는가?
- [ ] 점진적 타입의 의미를 한 문장으로 설명할 수 있는가?

## 연습 문제

1. 최근 함수 하나에 타입 힌트를 추가하고 mypy를 돌린 뒤, 어떤 종류의 오류가 잡히는지 적어 보세요.
2. JSON을 받는 경계에 `pydantic` 모델을 적용해 보고, 이전과 이후의 오류 메시지를 비교해 보세요.
3. `Protocol` 예제를 ABC 기반 상속으로 바꾼 뒤 무엇이 더 번거로워졌는지 정리해 보세요.

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

핵심은 금액이 숫자라는 사실만으로 충분하지 않다는 사실입니다. 정수인지, 소수점 정책이 무엇인지, 통화별 반올림 규칙이 무엇인지가 타입 설계에 반영되어야 합니다. 실무에서는 `int` 하나로 시작해 빠르게 배포한 뒤 정산 단계에서 누적 오차를 발견하는 일이 자주 발생합니다. 따라서 도메인 타입을 좁히는 전략이 필요합니다. 예를 들어 금액을 `Money` 값 객체로 감싸고, 생성 시점에 통화와 스케일을 강제하면 연산 단계를 통과하는 데이터 품질이 크게 올라갑니다.

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

정적과 동적은 우열이 아니라 선택입니다. 중요한 것은 어떤 오류를 언제 발견하고 싶은가입니다. 다음 마지막 글에서는 지금까지 본 모든 개념을 묶어 좋은 언어 설계가 무엇인지로 넘어가겠습니다.

## 처음 질문으로 돌아가기

- **정적과 동적의 가장 짧은 정의는 무엇일까요?**
  - 정적은 타입 검사를 실행 전에 하는 모델이고, 동적은 실제 값이 흘러가는 실행 중에 타입 문제가 드러나는 모델입니다. `add("1", "2")`를 `mypy`가 미리 막는 예시와, `total([data])`가 런타임에서야 실패하는 예시가 이 차이를 가장 짧게 보여 줍니다.
- **같은 코드가 두 모델에서 어떻게 다르게 검증될까요?**
  - `Item` dataclass와 `total(items: list[Item])`처럼 내부 계약이 분명한 코드는 호출 지점부터 정적 검사 대상이 되지만, JSON처럼 바깥에서 들어온 값은 `parse_item`처럼 런타임 검증을 거쳐야 비로소 안전한 내부 타입이 됩니다. 그래서 실무에서는 경계에서는 동적으로 좁히고, 경계 안쪽에서는 정적으로 추론하고 리팩터링하는 두 단계가 자연스럽게 이어집니다.
- **mypy나 pyright가 잡을 수 있는 것과 없는 것은 무엇일까요?**
  - 검사기는 `add(1, 2)`와 `add("1", "2")`의 차이, `Protocol`을 만족하는 `Book.price` 같은 구조적 계약, 공개 함수 시그니처 불일치처럼 코드 안에 드러난 타입 모순을 잘 잡습니다. 반대로 `json.loads`가 돌려준 `dict[str, Any]` 안의 실제 값, 경계 검증을 통과하지 않은 외부 데이터, 과도한 `Any` 뒤에 숨은 문제는 실행 전에는 다 알 수 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- **정적 언어와 동적 언어 (현재 글)**
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [Pyright documentation](https://microsoft.github.io/pyright/)
- [TypeScript Handbook — Basic Types](https://www.typescriptlang.org/docs/handbook/2/basic-types.html)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, StaticTyping, DynamicTyping, Tradeoffs, Safety
