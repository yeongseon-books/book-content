---
series: programming-languages-101
episode: 5
title: "Programming Languages 101 (5/10): 함수와 클로저"
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
  - Functions
  - Closure
  - FirstClass
  - Capture
seo_description: 일급 함수와 렉시컬 스코프가 결합된 클로저 원리를 정리합니다. 캡처와 늦은 바인딩 함정, 데코레이터로 함수가 환경을 보존하는 법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (5/10): 함수와 클로저

함수가 자신이 정의된 자리의 변수를 기억하는 것처럼 보일 때가 있습니다. 처음 보면 마법처럼 느껴지지만, 실제로는 지난 글의 스코프 규칙과 함수가 값처럼 다뤄질 수 있다는 사실이 자연스럽게 합쳐진 결과입니다.

이 글은 Programming Languages 101 시리즈의 다섯 번째 글입니다.

이 글에서는 클로저를 “설명하기 어려운 특별한 기능”이 아니라, 렉시컬 스코프와 일급 함수가 만났을 때 생기는 평범한 결과로 보겠습니다. 함수가 값을 붙잡는 것이 아니라 바인딩을 붙잡는다는 점까지 분명히 이해하면 콜백, 데코레이터, 메모이제이션이 한 번에 연결됩니다.

![Programming Languages 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/05/05-01-concept-at-a-glance.ko.png)
*Programming Languages 101 5장 흐름 개요*

## 먼저 던지는 질문

- 일급 함수와 고차 함수는 무엇이 다를까요?
- 클로저는 정확히 무엇을 캡처할까요?
- 왜 반복문 안에서 만든 람다가 같은 값만 출력할까요?

## 왜 중요한가

클로저는 콜백, 데코레이터, 부분 적용, 모듈 스타일 캡슐화의 바탕입니다. 이 구조를 정확히 이해하지 못하면 반복문 안 람다가 모두 같은 값을 출력하는 고전적인 문제를 계속 만나게 됩니다. 반대로 클로저를 이해하면 상태를 숨기면서 동작을 전달하는 구조를 훨씬 단순하게 설계할 수 있습니다.

## 핵심 개념 한눈에 보기

`make_adder(10)`이 반환한 `add`는 단순한 함수 객체가 아닙니다. `x = 10`이라는 바인딩까지 함께 들고 다닙니다. 호출자는 안쪽을 볼 수 없지만, `add`는 그 환경을 바탕으로 계속 계산할 수 있습니다.

## 먼저 알아둘 용어

- 일급 함수: 함수를 변수에 담고, 인자로 넘기고, 반환값으로 돌려줄 수 있습니다.
- 고차 함수: 함수를 인자로 받거나 함수를 반환하는 함수입니다.
- 클로저: 바깥 스코프의 바인딩을 붙잡은 함수입니다.
- 참조 캡처: 값 복사본이 아니라 같은 바인딩을 참조합니다.
- 늦은 바인딩: 캡처한 이름의 현재 값을 호출 시점에 읽습니다.

## 먼저 보는 예시

### 전역 상태에 기대는 방식

```python
total = 0
def add(n):
    global total
    total += n
add(3); add(4)
print(total)  # 7
```

전역 상태를 쓰면 함수 하나를 두 군데에서 독립적으로 쓰기 어렵습니다. 상태가 한곳에 묶여 있기 때문입니다.

### 클로저로 상태를 분리하는 방식

```python
def make_accumulator():
    total = 0
    def add(n):
        nonlocal total
        total += n
        return total
    return add

a = make_accumulator()
b = make_accumulator()
print(a(3), a(4))  # 3 7
print(b(10))       # 10  (independent of a)
```

각 호출은 자기만의 `total`을 따로 붙잡습니다. 이 고립된 상태가 바로 클로저의 힘이고, 다음 글에서 볼 객체의 감각과도 이어집니다.

## 클로저를 다섯 각도에서 보기

### 1단계 — 가장 단순한 클로저

```python
# 1_basic.py
def make_adder(x):
    def add(n):
        return x + n
    return add

add10 = make_adder(10)
add20 = make_adder(20)
print(add10(5), add20(5))  # 15 25
```

`add10`과 `add20`은 같은 함수 모양을 가졌지만 서로 다른 바인딩을 붙잡고 있습니다.

### 2단계 — 값이 아니라 바인딩을 공유한다는 증거

```python
# 2_reference.py
def make_pair():
    state = {"n": 0}
    def get(): return state["n"]
    def inc(): state["n"] += 1
    return get, inc

g, i = make_pair()
i(); i(); i()
print(g())  # 3
```

두 함수가 같은 `state`를 함께 바라봅니다. 복사본을 들고 있는 것이 아니라 같은 바인딩을 공유한다는 말입니다.

### 3단계 — 늦은 바인딩 함정

```python
# 3_late_binding.py
fns = []
for i in range(3):
    fns.append(lambda: i)

print([f() for f in fns])  # [2, 2, 2]  — same i!
```

세 람다는 모두 같은 `i`를 붙잡았습니다. 호출 시점에는 반복문이 이미 끝났기 때문에 전부 2를 봅니다.

### 4단계 — 정의 시점 값으로 고정하기

```python
# 4_fix.py
fns = [(lambda i=i: i) for i in range(3)]
print([f() for f in fns])  # [0, 1, 2]
```

기본 인자는 함수 정의 시점에 계산됩니다. 그래서 그 순간의 값을 얼려 둘 수 있습니다.

### 5단계 — 메모이제이션 만들기

```python
# 5_memo.py
def memo(fn):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memo
def slow_square(n):
    return n * n

print(slow_square(7), slow_square(7))  # 49 49 — second is cached
```

`cache`는 `wrapper`의 클로저 안에 살아 있습니다. 바깥에서는 보이지 않지만, 호출 사이에서는 계속 유지됩니다.

## 이 코드에서 먼저 볼 점

- 클로저는 함수만이 아니라 함수와 환경의 묶음입니다.
- 캡처는 값 복사가 아니라 바인딩 참조입니다.
- 늦은 바인딩 문제는 “정의 시점에 값을 고정할 것인가, 참조를 살아 있게 둘 것인가”의 차이에서 나옵니다.
- 데코레이터와 콜백과 팩토리 함수는 대부분 클로저 위에 서 있습니다.

## 자주 하는 실수

1. 반복문 안 람다가 캡처한 변수를 모두 공유한다는 사실을 잊습니다.
2. 클로저와 객체를 전혀 다른 것으로 봅니다. 둘 다 상태와 동작을 묶는 방식입니다.
3. 바깥에서 캡처된 상태를 직접 바꾸려 합니다. 클로저는 일부러 그 상태를 감춥니다.
4. `nonlocal`을 빼먹습니다. `+=`는 새 지역 변수를 만들려 하기 때문입니다.
5. 큰 객체를 캡처한 클로저를 오래 들고 있어 메모리 누수를 만듭니다.

## 실무에서는 이렇게 본다

JavaScript의 이벤트 핸들러, Python의 데코레이터, 함수형 라이브러리의 부분 적용은 모두 클로저를 바탕으로 움직입니다. 버튼을 눌렀을 때 특정 상태를 바꾸는 UI 코드가 자연스럽게 표현되는 이유도 결국 함수가 주변 상태를 함께 들고 다닐 수 있기 때문입니다.

라이브러리를 설계할 때도 “사용자가 넘긴 함수를 우리 환경 안에서 호출한다”는 구조는 대개 클로저로 가장 깔끔하게 표현됩니다. 다만 상태가 너무 커지거나 수명이 길어지면 클래스로 올리는 편이 더 읽기 쉬워질 수 있습니다.

## 체크리스트

- [ ] 일급 함수와 고차 함수의 차이를 한 줄로 설명할 수 있는가?
- [ ] 클로저가 값을 복사하는 것이 아니라 바인딩을 참조한다는 점을 아는가?
- [ ] 늦은 바인딩 함정과 회피법을 설명할 수 있는가?
- [ ] 클로저 안에서 `nonlocal`이 왜 필요한지 설명할 수 있는가?
- [ ] 작은 메모이제이션 함수를 직접 써 본 적이 있는가?

## 연습 문제

1. `memo` 예제에 최대 크기를 넣고 가장 오래된 항목부터 버리게 만들어 보세요.
2. 여러 버튼에 콜백을 등록하는 상황을 떠올리고, 늦은 바인딩 문제가 어떻게 드러나는지 설명해 보세요.
3. 클로저만으로 만든 개인용 카운터와 클래스로 만든 카운터를 각각 작성해 보고, 어느 쪽이 더 자연스러운지 한 줄로 적어 보세요.

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

### 보강 메모: 리뷰에서 바로 쓰는 질문

이 코드는 타입 오류를 실행 전에 막는가, 클로저 캡처가 의도한 값 기준으로 고정되는가, 공유 상태 접근이 동시성 규칙을 만족하는가를 한 번에 점검해야 합니다. 세 질문 중 하나라도 답하지 못하면 기능이 맞아도 운영 위험이 남습니다.

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

클로저는 함수와 환경의 결합입니다. 렉시컬 스코프와 일급 함수가 만나면 거의 자연스럽게 생깁니다. 다음 글에서는 같은 아이디어를 다른 모양으로 표현한 객체와 프로토타입을 보겠습니다.

## 처음 질문으로 돌아가기

- **일급 함수와 고차 함수는 무엇이 다를까요?**
  - 본문의 기준은 함수와 클로저를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **클로저는 정확히 무엇을 캡처할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 반복문 안에서 만든 람다가 같은 값만 출력할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- **함수와 클로저 (현재 글)**
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [SICP — Procedures and the Processes They Generate](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-11.html)
- [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures)
- [Python functools — partial, lru_cache](https://docs.python.org/3/library/functools.html)
- [On Lambdas, Captures and Closures (PLT)](https://wiki.c2.com/?ClosuresThatWorkLikeObjects)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Functions, Closure, FirstClass, Capture
