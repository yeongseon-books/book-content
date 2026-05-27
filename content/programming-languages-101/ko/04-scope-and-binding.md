---
series: programming-languages-101
episode: 4
title: "Programming Languages 101 (4/10): 스코프와 바인딩"
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
  - Scope
  - Binding
  - Lexical
  - Dynamic
seo_description: 이름을 값에 연결하는 바인딩과 스코프 규칙을 LEGB 사례로 풀이하고, 렉시컬 스코프가 왜 코드 가독성과 유지보수성에 중요한지 정리합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (4/10): 스코프와 바인딩

같은 변수 이름이 함수 안팎에서 서로 다른 값을 가리키는데도 프로그램은 대체로 예측 가능하게 동작합니다. 이 당연해 보이는 일이 사실은 언어 설계에서 아주 중요한 규칙 위에 서 있습니다.

이 글은 Programming Languages 101 시리즈의 4번째 글입니다.

이 글에서는 이름에 값을 붙이는 바인딩과, 그 바인딩이 보이는 범위인 스코프를 함께 보겠습니다. 특히 현대 언어 대부분이 택한 렉시컬 스코프가 왜 읽기 좋은 코드를 만들고, 어디서 흔히 헷갈리는지도 같이 정리하겠습니다.

![Programming Languages 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/04/04-01-concept-at-a-glance.ko.png)
*Programming Languages 101 4장 흐름 개요*

> '이 변수 이름이 가리키는 값은 어디서 결정되는가'라는 질문 하나가 lexical scope·dynamic scope·closure·hoisting을 모두 같은 그림으로 묶어 줍니다 — JavaScript의 `this`나 Python의 late binding은 이 한 모델 위에서만 일관되게 설명됩니다.

## 먼저 던지는 질문

- 스코프와 바인딩은 정확히 무엇이 다를까요?
- 렉시컬 스코프와 동적 스코프는 결과를 어떻게 바꿀까요?
- 같은 이름을 안쪽에서 다시 쓰는 섀도잉은 왜 위험할까요?

## 왜 중요한가

“왜 이 변수는 갱신되지 않았지?”, “왜 갑자기 NameError가 나지?” 같은 질문은 스코프를 모르면 미스터리처럼 보입니다. 하지만 스코프를 이해하면 함수, 모듈, 클로저가 모두 같은 규칙의 다른 표현이라는 사실이 보입니다.

## 핵심 개념 한눈에 보기

Python의 LEGB 규칙은 안쪽에서 바깥쪽으로 이름을 찾는 순서입니다. 가장 먼저 발견한 바인딩이 이깁니다. 이 단순한 규칙 하나가 함수 동작의 대부분을 설명해 줍니다.

## 먼저 알아둘 용어

- 바인딩: 이름에 값을 연결하는 일입니다.
- 스코프: 그 연결이 보이는 코드 범위입니다.
- 렉시컬 스코프: 코드가 어디에 쓰였는지를 기준으로 스코프를 정합니다.
- 동적 스코프: 실행 중 호출 경로를 따라 스코프를 정합니다.
- 섀도잉: 안쪽 스코프가 바깥쪽의 같은 이름을 가리는 현상입니다.

## 먼저 보는 예시

### 전역에 기대는 코드

```python
LIMIT = 10

def is_ok(x):
    return x < LIMIT

def main():
    LIMIT = 5      # a new local — has no effect on is_ok
    print(is_ok(7))  # True
```

`main` 안의 `LIMIT`은 `is_ok`에서 보이지 않습니다. `is_ok`는 자신이 정의된 위치를 기준으로 이름을 찾기 때문입니다. 이것이 렉시컬 스코프입니다.

### 의존성을 드러내는 코드

```python
def is_ok(x, limit=10):
    return x < limit

print(is_ok(7, limit=5))  # False
```

숨은 의존성을 매개변수로 끌어올리면 코드가 훨씬 읽기 쉬워집니다. 테스트도 쉬워집니다.

## 꼭 알아야 할 네 가지 예제

### 1단계 — 이름 탐색 순서 보기

```python
# 1_legb.py
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)
    inner()
    print(x)

outer()
print(x)
# 로컬/포함/글로벌
```

같은 이름이라도 가장 안쪽 바인딩부터 차례로 찾습니다. 이름 하나가 항상 값 하나만 뜻하는 것은 아닙니다.

### 2단계 — 지역 변수 바인딩 오류의 실제 원인

```python
# 2_unbound.py
x = 1
def f():
    print(x)   # UnboundLocalError
    x = 2

f()
```

함수 안에 `x = 2`가 등장하는 순간 Python은 함수 전체에서 `x`를 지역 변수로 봅니다. 그래서 `print(x)`는 아직 바인딩되지 않은 지역 변수를 읽으려다 실패합니다.

### 3단계 — 바깥 함수 값을 갱신할 때

```python
# 3_nonlocal.py
def make_counter():
    n = 0
    def step():
        nonlocal n
        n += 1
        return n
    return step

c = make_counter()
print(c(), c(), c())  # 1 2 3
```

`nonlocal` 없이 `n += 1`을 쓰면 새 지역 변수를 만들려다 같은 오류가 납니다. `nonlocal`은 의도적으로 바깥 스코프를 갱신하겠다는 표시입니다.

### 4단계 — 렉시컬 스코프와 동적 스코프 비교

```python
# 4_lexical.py
y = "outer"
def show():
    print(y)

def caller():
    y = "inner"
    show()   # lexical scope → prints 'outer'

caller()
```

동적 스코프였다면 `show()`는 호출한 쪽의 `y`를 보고 `inner`를 출력했을 것입니다. 현대 언어가 렉시컬 스코프를 선호하는 이유는 소스만 읽어도 값의 출처를 알 수 있기 때문입니다.

### 5단계 — 섀도잉의 함정

```python
# 5_shadow.py
def total(items):
    sum = 0   # shadowed the built-in sum
    for x in items:
        sum += x
    return sum  # works, but you cannot call sum(...) in this function anymore
```

짧은 함수라서 넘어가기 쉽지만, 내장 함수 이름을 가려 버리면 나중에 원래 `sum(...)`을 쓰고 싶을 때 곧바로 문제가 됩니다.

## 이 코드에서 먼저 볼 점

- 이름이 어떤 값을 가리키는지는 스코프 규칙이 결정합니다.
- 함수 안의 대입 한 줄이 그 함수 전체의 이름 해석 방식을 바꿀 수 있습니다.
- `nonlocal`과 `global`은 흔히 쓰는 도구가 아니라, 의도적인 갱신을 표시하는 표식입니다.
- 렉시컬 스코프의 강점은 “읽어서 알 수 있다”는 점입니다.

## 자주 하는 실수

1. 함수끼리 상태를 공유하려고 전역 변수를 늘립니다. 변경 출처가 흐려져 디버깅이 어려워집니다.
2. `list`, `dict`, `sum` 같은 내장 이름을 변수명으로 씁니다. 나중에 큰 혼란을 부릅니다.
3. `global`을 너무 쉽게 씁니다. 매개변수와 반환값으로 드러내는 편이 거의 항상 낫습니다.
4. 함수 중간에서 이름을 다시 대입해 UnboundLocalError를 만듭니다.
5. 현대 언어에서 동적 스코프처럼 동작할 것이라고 착각합니다.

## 실무에서는 이렇게 본다

좋은 코드는 “이 이름은 어디서 왔지?”라는 질문에 거의 즉시 답할 수 있어야 합니다. 큰 함수를 나누고, 숨은 의존성을 매개변수로 끌어올리고, 모듈 변수 갱신을 한곳에 모으는 습관은 모두 렉시컬 스코프의 장점을 극대화하는 방법입니다.

테스트도 같은 원리로 쉬워집니다. 전역 상태에 기대는 함수는 단위 테스트가 어렵고, 필요한 값을 매개변수로 받는 함수는 테스트가 단순해집니다. 스코프 규칙을 이해하는 일은 결국 읽기 쉬운 코드와 테스트 가능한 코드를 만드는 일과 맞닿아 있습니다.

## 체크리스트

- [ ] LEGB 네 단계를 말할 수 있는가?
- [ ] UnboundLocalError가 왜 생기는지 한 줄로 설명할 수 있는가?
- [ ] `nonlocal`과 `global`을 언제 써야 하는지 아는가?
- [ ] 숨은 의존성을 매개변수로 끌어올린 경험이 있는가?
- [ ] 렉시컬 스코프의 가독성 이점을 한 문장으로 설명할 수 있는가?

## 연습 문제

1. `sum`을 가리는 예제를 고쳐 함수 안에서 원래 `sum(...)`도 쓸 수 있게 바꿔 보세요.
2. 모듈 전역 변수 하나에 의존하는 함수를 골라, 그 값을 매개변수로 받도록 다시 작성해 보세요.
3. 렉시컬 스코프와 동적 스코프의 차이로 결과가 달라지는 상상 코드 한 조각을 직접 만들어 보세요.

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

### 추가 사례: 언어 설계 선택이 유지보수 비용에 미치는 영향

실무에서 타입, 스코프, 메모리 모델은 장애 보고서에서 따로 등장하지 않고 함께 엮여 나타납니다. 예를 들어 이벤트 소비자가 `dict[str, Any]`를 그대로 전달하면 타입 경계가 무너지고, 지연 실행 콜백이 외부 가변 상태를 캡처하면 스코프 결함이 생기며, 여러 워커가 같은 캐시 객체를 잠금 없이 접근하면 메모리 가시성 문제가 겹칩니다. 이런 결함은 단위 테스트 한두 개로는 쉽게 드러나지 않습니다.

그래서 언어 기능 선택을 할 때는 "지금 빨리 쓰기 쉬운가"보다 "오류를 조기에 막는가"를 기준으로 삼아야 합니다. 타입 힌트를 강제하고, 클로저 캡처 규칙을 리뷰 체크리스트에 넣고, 공유 상태 대신 메시지 전달을 우선하면 코드가 길어지더라도 운영 리스크가 크게 줄어듭니다. 결과적으로 좋은 설계는 문법의 화려함이 아니라, 팀이 반복 실수 없이 같은 문제를 안정적으로 푸는 능력으로 측정됩니다.

### 보강 메모: 리뷰에서 바로 쓰는 질문

이 코드는 타입 오류를 실행 전에 막는가, 클로저 캡처가 의도한 값 기준으로 고정되는가, 공유 상태 접근이 동시성 규칙을 만족하는가를 한 번에 점검해야 합니다. 세 질문 중 하나라도 답하지 못하면 기능이 맞아도 운영 위험이 남습니다.

스코프 규칙을 문서로만 아는 것과 리뷰에서 적용하는 것은 다릅니다. 이름 해석 시점, 캡처 대상, 수명 경계를 코드에서 명시하면 유지보수 난도가 눈에 띄게 낮아집니다.

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

## 정리

스코프는 이름이 보이는 범위이고, 바인딩은 이름에 값을 붙이는 행위입니다. 렉시컬 스코프를 제대로 이해하면 다음 글의 클로저는 훨씬 자연스럽게 이어집니다. 클로저는 결국 렉시컬 스코프와 일급 함수가 만나서 생기는 결과이기 때문입니다.

## 처음 질문으로 돌아가기

- **스코프와 바인딩은 정확히 무엇이 다를까요?**
  - 바인딩은 이름을 값에 연결하는 행위이고, 스코프는 그 연결이 어디까지 보이는지 정하는 범위입니다. `x = "global"`, `x = "enclosing"`, `x = "local"` 예시에서 같은 이름이 여러 값에 묶일 수 있었던 이유도 바인딩과 스코프가 함께 작동했기 때문입니다.
- **렉시컬 스코프와 동적 스코프는 결과를 어떻게 바꿀까요?**
  - `show()`가 `caller()` 안에서 호출돼도 `y = "inner"`가 아니라 바깥의 `y = "outer"`를 출력한 이유는 Python이 정의된 위치를 기준으로 이름을 찾는 렉시컬 스코프를 쓰기 때문입니다. 만약 동적 스코프였다면 호출 경로를 따라 `caller()`의 `y`를 읽었을 것이므로, 같은 코드라도 결과가 달라졌을 것입니다.
- **같은 이름을 안쪽에서 다시 쓰는 섀도잉은 왜 위험할까요?**
  - `sum = 0`은 내장 함수 `sum(...)`을 가려서 함수 안에서 원래 도구를 못 쓰게 만들고, `x = 2`가 있는 함수에서 `print(x)`를 먼저 쓰면 `UnboundLocalError`가 납니다. 안쪽 대입 한 줄이 함수 전체의 이름 해석을 바꿔 버리기 때문에, 섀도잉은 짧은 예제보다 큰 코드에서 더 위험합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- **스코프와 바인딩 (현재 글)**
- 함수와 클로저 (예정)
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python Language Reference — Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- [Structure and Interpretation of Computer Programs — Chapter 3](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-21.html)
- [Programming Language Pragmatics (Scott) — Chapter 3 Names, Scopes, and Bindings](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [MDN — Scope](https://developer.mozilla.org/en-US/docs/Glossary/Scope)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Scope, Binding, Lexical, Dynamic
