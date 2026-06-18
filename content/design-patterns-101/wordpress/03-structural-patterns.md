---
series: design-patterns-101
episode: 3
title: "바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Structural
  - Adapter
  - Decorator
  - Facade
seo_description: AI가 생성한 코드에서 구조 패턴을 발견하고 외부 SDK 연결과 기능 추가를 깔끔하게 처리하는 바이브코딩 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 세 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 외부 결제 API를 연결해 달라고 하면, 도메인 코드 안에 SDK 메서드 호출이 직접 박히는 경우가 많습니다. 결제사를 바꾸는 날, 코드 전체를 뒤져야 합니다. AI에게 로깅이나 캐시를 추가해 달라고 하면, 기존 클래스에 메서드를 추가하거나 조건문을 넣는 구조를 만들어 줍니다. 구조 패턴은 이런 문제를 "합성"으로 푸는 방법입니다.

---

객체를 만드는 문제를 정리하고 나면, 그다음에 부딪히는 벽은 "이미 있는 객체들을 어떻게 엮을 것인가"입니다. 외부 SDK를 도메인에 연결할 때, 기존 객체에 로깅이나 캐시를 덧붙여야 할 때, 복잡한 하위 시스템을 호출자에게 단순하게 보여줘야 할 때. 이 세 가지 상황은 전부 "구조를 어떻게 조립하느냐"의 문제이고, GoF는 이 문제를 Structural 패턴이라는 이름으로 묶었습니다.

> "구조 패턴은 클래스와 객체를 어떻게 조합하느냐에 관한 것이라, 시스템이 커져도 모든 연결을 다시 잇지 않아도 됩니다. AI가 만든 코드가 이 구조를 따르고 있다면, 확장 지점이 이미 준비된 셈입니다."

## 이 글에서 다룰 문제

- AI가 외부 SDK를 직접 호출하는 코드를 만들었을 때 어떻게 구조를 개선할까요?
- Decorator와 Proxy는 둘 다 "감싸는" 패턴인데, AI에게 어떻게 구분해서 요청할까요?
- AI에게 복잡한 하위 시스템을 단순화해 달라고 할 때 어떤 패턴을 요청해야 할까요?
- 바이브코딩에서 구조 패턴을 잘못 적용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Adapter: AI가 만든 SDK 연결 코드를 도메인과 분리하기

AI에게 "Stripe로 결제 처리해줘"라고 하면 이런 코드를 받을 수 있습니다.

```python
class OrderService:
    def place_order(self, user_id: str, amount: int) -> str:
        import stripe
        stripe.api_key = os.environ["STRIPE_KEY"]
        intent = stripe.PaymentIntent.create(
            amount=amount, currency="krw", customer=user_id, confirm=True
        )
        return intent.id
```

이 코드는 동작하지만, Toss Payments로 바꾸는 날 `OrderService` 전체를 고쳐야 합니다. "Adapter 패턴으로 리팩토링해 줘"라고 요청하면 이렇게 바뀝니다.

```python
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount_krw: int) -> str: ...
    def refund(self, transaction_id: str) -> None: ...

class StripeAdapter:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe
        stripe.api_key = self._api_key
        intent = stripe.PaymentIntent.create(
            amount=amount_krw, currency="krw",
            customer=customer_id, confirm=True,
        )
        return intent.id

    def refund(self, transaction_id: str) -> None:
        import stripe
        stripe.api_key = self._api_key
        stripe.Refund.create(payment_intent=transaction_id)

class OrderService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway

    def place_order(self, user_id: str, amount: int) -> str:
        return self._gateway.charge(user_id, amount)
```

이제 결제사를 바꿀 때 `TossAdapter`를 만들어 주입하면 `OrderService`는 한 글자도 바뀌지 않습니다.

## Facade: 여러 시스템을 하나의 진입점으로

AI에게 주문 처리 로직을 짜달라고 하면 재고, 결제, 배송, 알림을 각각 다루는 긴 함수가 나올 수 있습니다. Facade는 이를 깔끔하게 묶어줍니다.

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier) -> None:
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notifier = notifier

    def place_order(self, user_id: str, item_id: str, amount: int) -> str:
        self._inventory.reserve(item_id)
        tx_id = self._payment.charge(user_id, amount)
        tracking = self._shipping.schedule(user_id, item_id)
        self._notifier.send(user_id, f"주문 완료: {tracking}")
        return tx_id
```

Facade의 함정은 "편하니까 여기에 기능을 더 넣자"는 유혹입니다. Facade는 조율만 하고, 판단은 각 하위 시스템에 남겨야 합니다.

## Decorator: 기능 추가를 상속 없이 해결하기

AI에게 HTTP 클라이언트에 로깅과 재시도를 추가해 달라고 하면, Decorator 체이닝 구조를 받을 수 있습니다.

```python
from typing import Protocol

class HttpClient(Protocol):
    def get(self, url: str) -> bytes: ...

class LoggingClient:
    def __init__(self, inner: HttpClient) -> None:
        self._inner = inner

    def get(self, url: str) -> bytes:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result

class RetryClient:
    def __init__(self, inner: HttpClient, max_retries: int = 3) -> None:
        self._inner = inner
        self._max_retries = max_retries

    def get(self, url: str) -> bytes:
        for attempt in range(self._max_retries):
            try:
                return self._inner.get(url)
            except OSError:
                if attempt == self._max_retries - 1:
                    raise

# 조립
client = RetryClient(LoggingClient(RealHttpClient()))
```

이 구조에서 새 기능을 추가하려면 새 래퍼 클래스 하나를 만들면 됩니다. 기존 클래스를 수정할 필요가 없습니다.

## Before / After: Adapter가 만드는 구조 변화

**Before — SDK 의존성이 도메인에 박혀 있는 코드:**

```python
# 의존 그래프
# [OrderService] → [stripe 패키지]
# [RefundService] → [stripe 패키지]
# [WebhookHandler] → [stripe 패키지]

class OrderService:
    def place_order(self, ...):
        import stripe
        stripe.PaymentIntent.create(...)
```

**After — Adapter로 의존성을 한 곳에 모은 코드:**

```python
# 의존 그래프
# [OrderService] → [PaymentGateway (Protocol)]
# [RefundService] → [PaymentGateway (Protocol)]
# [WebhookHandler] → [PaymentGateway (Protocol)]
#                          ↑
#                   [StripeAdapter] → [stripe 패키지]

class OrderService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway
```

`stripe` 패키지에 의존하는 모듈이 하나로 줄었습니다. 변경 영향 범위가 Adapter 한 파일로 수렴합니다.

## 구조 패턴 선택 기준

| 패턴 | 언제 쓰나 | AI에게 요청하는 방법 |
| --- | --- | --- |
| Adapter | 외부 SDK 인터페이스가 도메인과 맞지 않을 때 | "Adapter 패턴으로 SDK 분리해줘" |
| Facade | 여러 하위 시스템을 단순한 진입점으로 묶을 때 | "Facade 패턴으로 주문 처리 통합해줘" |
| Decorator | 기존 객체에 기능을 동적으로 추가할 때 | "Decorator로 로깅/캐시 추가해줘" |
| Proxy | 접근 제어, 캐시, 지연 로딩이 필요할 때 | "캐시 Proxy 패턴으로 감싸줘" |
| Composite | 트리 구조 데이터를 균일하게 다룰 때 | "Composite 패턴으로 트리 구조 표현해줘" |

## AI 활용 팁

**Adapter 패턴 요청:**

```
"현재 OrderService가 stripe SDK를 직접 호출하고 있어.
Adapter 패턴을 적용해서 결제사를 쉽게 교체할 수 있는 구조로
바꿔줘. Python Protocol로 PaymentGateway 인터페이스를 정의하고,
StripeAdapter가 그 인터페이스를 구현하도록 해줘."
```

**Decorator 패턴 요청:**

```
"HTTP 클라이언트에 로깅, 재시도, 타이밍 기능을 추가해야 해.
상속 없이 Decorator 패턴으로 각 기능을 독립적으로 추가할 수 있게 해줘.
각 Decorator를 체이닝해서 조합하는 방식으로."
```

## 운영 체크리스트

- [ ] Adapter와 Facade의 차이를 설명할 수 있습니다.
- [ ] AI가 만든 SDK 직접 호출 코드를 Adapter로 분리할 수 있습니다.
- [ ] Decorator와 Proxy의 의도 차이를 설명할 수 있습니다.
- [ ] 구조 패턴을 도입할 때 잃는 것을 말할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 Adapter는 외부 SDK의 인터페이스를 도메인이 원하는 모양으로 번역합니다. 둘째 Facade는 복잡한 하위 시스템을 단순한 진입점 뒤에 숨깁니다. 셋째 Decorator는 기존 객체에 기능을 상속 없이 추가하는 방법입니다. 바이브코딩에서는 AI에게 패턴 이름을 명시하면 원하는 구조를 더 정확하게 받을 수 있습니다.

## 처음 질문으로 돌아가기

- **AI가 외부 SDK를 직접 호출하는 코드를 만들었을 때 어떻게 구조를 개선할까요?**
  - Adapter 패턴을 요청하세요. 도메인 Protocol을 정의하고 SDK 호출을 Adapter 클래스 안에 가두면, SDK가 바뀌어도 도메인 코드는 영향받지 않습니다.
- **Decorator와 Proxy는 어떻게 다를까요?**
  - Decorator는 기능을 추가하고, Proxy는 접근을 제어합니다. 로깅이나 재시도는 Decorator, 캐시나 지연 로딩은 Proxy가 적합합니다.
- **복잡한 하위 시스템을 단순화하려면 어떤 패턴을 요청해야 할까요?**
  - Facade를 요청하세요. 여러 시스템을 하나의 메서드 뒤에 묶어 호출자가 복잡도를 모르게 만듭니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Decorator Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/decorator)
- [Facade Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/facade)

### 실무 확장 읽을거리

- [Proxy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/proxy)
- [Python typing — Protocol (Python docs)](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Structural, Adapter, Decorator, Facade
