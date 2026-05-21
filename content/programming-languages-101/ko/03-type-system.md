---
series: programming-languages-101
episode: 3
title: "Programming Languages 101 (3/10): 타입 시스템"
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
  - TypeSystem
  - Static
  - Dynamic
  - Inference
seo_description: 정적/동적 타입과 강한/약한 타입의 차이를 정리하고, 제네릭과 타입 추론이 안전성과 생산성을 어떻게 동시에 보장하는지 코드 예시로 설명합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (3/10): 타입 시스템

동적 언어로도 코드는 잘 돌아갑니다. 그런데 프로젝트가 커질수록 사람들은 다시 타입 힌트를 붙이고, 검사기를 CI에 넣고, 인터페이스를 더 정확히 적기 시작합니다. 왜 이런 수고를 되풀이할까요.

이 글은 Programming Languages 101 시리즈의 세 번째 글입니다.

이 글에서는 타입 시스템을 단순한 자료형 표기가 아니라, 프로그램이 말도 안 되는 조합을 실행 전에 걸러 내는 장치로 보겠습니다. 정적 타입과 동적 타입, 강한 타입과 약한 타입, 타입 추론과 제네릭이 각각 무엇을 사고파는지 차분히 정리해 보겠습니다.

## 먼저 던지는 질문

- 타입은 정확히 어떤 역할을 할까요?
- 정적 타입과 동적 타입은 무엇을 언제 검사할까요?
- 강한 타입과 약한 타입은 왜 다른 축일까요?

## 큰 그림

![Programming Languages 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/03/03-01-concept-at-a-glance.ko.png)

*Programming Languages 101 3장 흐름 개요*

## 왜 중요한가

현대 언어 대부분은 어떤 형태로든 타입 시스템을 품고 있습니다. Python도 타입 힌트와 mypy, JavaScript도 TypeScript를 통해 점점 더 정적인 방향을 받아들였습니다. 자동 완성, 안전한 리팩터링, 빌드 단계의 오류 검출을 잘 활용하려면 타입이 무엇을 보장하고 무엇을 보장하지 않는지부터 알아야 합니다.

## 핵심 개념 한눈에 보기

타입 검사는 실행 전에 불가능한 호출을 먼저 걸러 냅니다. 동시에 IDE는 타입 정보를 바탕으로 자동 완성, 호출 추적, 안전한 이름 바꾸기 같은 기능을 제공합니다. 타입은 검사 규칙이면서 문서이자 도구 입력이기도 합니다.

## 먼저 알아둘 용어

- 정적 타입: 실행 전에 타입을 검사합니다.
- 동적 타입: 실행 중에 타입 오류가 드러납니다.
- 강한 타입: 암묵적 형변환이 드뭅니다.
- 약한 타입: 암묵적 형변환이 자주 일어납니다.
- 타입 추론: 명시하지 않아도 컴파일러나 검사기가 타입을 알아냅니다.
- 제네릭: 여러 타입에 대해 안전하게 재사용되도록 코드를 매개변수화합니다.

## 먼저 보는 예시

### 타입 정보가 없을 때

```python
def discount(price, rate):
    return price - price * rate

# Someone calls it like this
discount("1000", 0.1)  # TypeError at runtime
```

함수 시그니처만으로는 호출자가 무엇을 넘겨야 하는지 알기 어렵고, 잘못된 값이 들어와도 실행하기 전까지는 모릅니다.

### 타입을 적어 두었을 때

```python
def discount(price: int, rate: float) -> float:
    return price - price * rate

discount("1000", 0.1)  # mypy rejects this at the call site
```

이제 `mypy` 같은 정적 검사기가 호출 지점에서 문제를 잡아 줍니다. 시그니처 자체도 작은 문서 역할을 합니다.

## 타입을 단계적으로 붙여 보기

### 1단계 — 타입 힌트 추가하기

```python
# 1_hints.py
def to_kebab(s: str) -> str:
    return s.strip().lower().replace(" ", "-")

print(to_kebab("Hello World"))
```

동작은 같지만 호출 계약이 생겼습니다. 이 작은 차이가 코드베이스가 커질수록 크게 쌓입니다.

### 2단계 — 정적 검사기로 확인하기

```bash
pip install mypy
mypy 1_hints.py    # Success: no issues
```

이 단계에서 생기는 습관이 중요합니다. 실행하기 전에 검사하는 루프가 하나 더 들어옵니다.

### 3단계 — 제네릭 함수 만들기

```python
# 3_generic.py
from typing import TypeVar, Iterable

T = TypeVar("T")

def first(xs: Iterable[T]) -> T:
    for x in xs:
        return x
    raise ValueError("empty")

reveal_type(first([1, 2, 3]))   # Revealed type is "int"
reveal_type(first(["a", "b"]))  # Revealed type is "str"
```

한 함수가 여러 타입을 받아도 반환 타입을 정확히 보존합니다. 재사용성과 정확성을 함께 챙기는 방식입니다.

### 4단계 — 유니온 타입과 좁히기

```python
# 4_union.py
def length(x: str | list) -> int:
    if isinstance(x, str):
        return len(x)
    return sum(len(item) for item in x)
```

`isinstance`를 통과한 뒤 검사기는 각 분기에서 타입을 더 좁게 이해합니다. 동적 언어의 직관을 정적 검사로 끌고 오는 대표적인 패턴입니다.

### 5단계 — 타입이 진짜 버그를 드러내는 순간

```python
# 5_real_bug.py
def total_price(items: list[dict]) -> int:
    return sum(item["price"] for item in items)  # mypy points out the dict value type is unclear
```

정확한 타입을 적으려다 보면 데이터 모델의 애매함이 먼저 드러납니다. 실제 버그는 대개 그 애매한 경계에 숨어 있습니다.

### 6단계 — 경계에서는 입력을 검증하고, 안쪽에서는 구체 타입으로 좁히기

```python
# 6_boundary.py
from typing import TypedDict

class LineItem(TypedDict):
    price: int
    quantity: int

def parse_line_item(raw: dict[str, object]) -> LineItem:
    price = raw.get("price")
    quantity = raw.get("quantity")
    if not isinstance(price, int) or not isinstance(quantity, int):
        raise ValueError("price and quantity must be integers")
    return {"price": price, "quantity": quantity}

def subtotal(item: LineItem) -> int:
    return item["price"] * item["quantity"]

payload = {"price": 1200, "quantity": 3}
item = parse_line_item(payload)
print(subtotal(item))  # 3600
```

정적 타입이 강해지는 지점은 보통 함수 경계 안쪽입니다. 외부 JSON이나 폼 입력처럼 동적으로 들어오는 값은 먼저 런타임 검증으로 좁히고, 그 결과를 `TypedDict`나 dataclass로 넘겨야 타입 검사기의 이점이 제대로 살아납니다.

## 이 코드에서 먼저 볼 점

- 타입은 검사 규칙이면서 문서이면서 도구 입력입니다.
- 정적 검사는 모든 버그를 잡지 못하지만, 값싸고 흔한 오류를 아주 일찍 잡아 줍니다.
- 제네릭은 “한 번 작성해 여러 타입에 안전하게 쓰기”를 가능하게 합니다.
- 유니온 타입과 좁히기는 동적 언어 감각과 정적 검사 사이를 자연스럽게 이어 줍니다.

## 자주 하는 실수

1. `Any`를 너무 쉽게 씁니다. 검사기가 조용해지는 대신 안전성도 함께 사라집니다.
2. 모든 곳에 한꺼번에 타입을 붙이려 합니다. 공개 함수와 모듈 경계부터 시작하는 편이 낫습니다.
3. 타입과 실행 시 검증을 같은 것으로 봅니다. 외부 입력은 여전히 별도 검증이 필요합니다.
4. 지나치게 정교한 타입을 쫓습니다. 90%를 깔끔하게 막는 단순한 타입이 더 실용적일 때가 많습니다.
5. 정적 대 동적을 신념 싸움처럼 다룹니다. 실제로는 팀 규모와 변경 빈도에 따른 선택입니다.

## 실무에서는 이렇게 본다

큰 Python 코드베이스는 대개 공개 함수에 타입을 붙이고, CI에서 mypy나 pyright를 돌립니다. JavaScript 생태계에서 TypeScript가 사실상 기본이 된 이유도 같은 맥락입니다. 타입은 라이브러리 사용자에게 가장 먼저 보이는 문서이자, 자동 완성과 리팩터링의 기반입니다.

타입은 리팩터링 안전망으로도 강합니다. 함수 인자 순서를 바꿨을 때 호출 지점이 한꺼번에 드러나면 변경을 훨씬 자신 있게 진행할 수 있습니다. 결국 타입 시스템의 실익은 이론보다 운영과 유지보수에서 더 크게 체감됩니다.

## 체크리스트

- [ ] 정적 타입과 동적 타입, 강한 타입과 약한 타입을 각각 구분할 수 있는가?
- [ ] 점진적으로 타입을 도입할 때 어디부터 시작해야 하는지 아는가?
- [ ] `Any`를 만났을 때 한 단계라도 좁히는 전략이 있는가?
- [ ] 타입과 실행 시 검증의 차이를 설명할 수 있는가?
- [ ] 제네릭이 단순 복사보다 왜 강한지 설명할 수 있는가?

## 연습 문제

1. `total_price` 예제에 `TypedDict`를 도입해 `item` 구조를 정확히 적어 보세요.
2. 자주 쓰는 동적 언어 함수 하나를 골라 입력 타입과 출력 타입을 글로 적어 보세요.
3. 타입을 붙인 뒤에야 드러난 실제 버그 사례를 떠올리고, 왜 더 일찍 발견되지 않았는지 설명해 보세요.

## 정리

타입 시스템은 안전성, 문서성, 도구 지원을 한 번에 제공합니다. 모든 언어가 같은 정도의 타입 강도를 필요로 하지는 않지만, 경계가 많은 큰 시스템일수록 그 이점이 커집니다. 다음 글에서는 또 다른 기본 축인 스코프와 바인딩으로 넘어가겠습니다.

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

## 처음 질문으로 돌아가기

- **타입은 정확히 어떤 역할을 할까요?**
  - 본문의 기준은 타입 시스템를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **정적 타입과 동적 타입은 무엇을 언제 검사할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **강한 타입과 약한 타입은 왜 다른 축일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- **타입 시스템 (현재 글)**
- 스코프와 바인딩 (예정)
- 함수와 클로저 (예정)
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Types and Programming Languages (Pierce)](https://www.cis.upenn.edu/~bcpierce/tapl/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)

Tags: Computer Science, Programming Languages, TypeSystem, Static, Dynamic, Inference
