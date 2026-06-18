---
series: design-patterns-101
episode: 6
title: "바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Adapter
  - Structural
  - AI코딩
  - SDK연동
seo_description: AI가 생성한 외부 SDK 연동 코드를 Adapter 패턴으로 분리해서 교체 가능성과 테스트 가능성을 높이는 바이브코딩 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 여섯 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 "Stripe로 결제 연동해줘"라고 하면 도메인 코드 안에 `stripe.PaymentIntent.create()`가 직접 박힙니다. 나중에 Toss Payments로 바꾸거나 테스트를 짜려고 할 때 문제가 생깁니다. Adapter 패턴을 알면 AI에게 처음부터 올바른 구조를 요청할 수 있습니다.

---

결제 SDK를 교체해야 하는 날이 옵니다. Stripe에서 Toss Payments로 바꿀 때, SES에서 SendGrid로 메일 발송을 옮길 때, 사내 인증 서버가 OAuth2 표준으로 전환될 때. 바이브코딩으로 외부 SDK를 빠르게 연동하다 보면 이 순간이 더 빨리 옵니다. AI가 만들어 준 코드에 SDK 시그니처가 도메인 코드 곳곳에 박혀 있으면, 교체 작업은 "SDK 하나 바꾸기"가 아니라 "서비스 전체 리팩터링"이 됩니다.

> "Adapter 패턴은 어느 한쪽도 다시 쓰지 않고, 거의 맞지만 정확히는 다른 두 인터페이스 사이에 얇은 번역기를 끼워 넣는 도구입니다. AI가 SDK를 도메인에 직접 연결했다면, Adapter로 분리해 달라고 요청하세요."

## 이 글에서 다룰 문제

- AI가 외부 SDK를 도메인에 직접 연결했을 때 어떻게 Adapter로 분리할까요?
- Adapter와 Facade는 어떻게 다를까요?
- AI가 만든 Adapter 코드에서 예외 번역이 왜 중요할까요?
- 바이브코딩에서 Adapter를 잘못 적용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Adapter를 두는 순간 끊어지는 의존성

AI가 만들어 준 코드에서 가장 흔한 문제는 외부 SDK가 도메인 전체에 흩어지는 것입니다.

**Adapter 없이:**

```text
[OrderService] → [stripe 패키지]
[RefundService] → [stripe 패키지]
[WebhookHandler] → [stripe 패키지]
```

세 모듈 모두 `stripe`를 직접 import합니다. Stripe가 메이저 버전을 올리면 세 곳을 동시에 고쳐야 합니다.

**Adapter를 두면:**

```text
[OrderService] → [PaymentGateway (Protocol)]
[RefundService] → [PaymentGateway (Protocol)]
[WebhookHandler] → [PaymentGateway (Protocol)]
                         ↑
                   [StripeAdapter] → [stripe 패키지]
```

`stripe` 패키지에 의존하는 모듈이 하나로 줄었습니다. 변경 영향 범위가 Adapter 한 파일로 수렴합니다.

## AI에게 Adapter 패턴 요청하기

AI에게 이렇게 요청하면 올바른 Adapter 구조를 받을 수 있습니다.

```
"OrderService가 stripe SDK를 직접 호출하고 있어.
Adapter 패턴으로 리팩토링해줘:
1. 도메인이 원하는 PaymentGateway Protocol 정의
2. StripeAdapter가 Protocol을 구현
3. OrderService는 Protocol만 알도록
4. FakePaymentGateway도 만들어줘 (테스트용)"
```

결과 코드:

```python
from typing import Protocol
from dataclasses import dataclass

class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount_krw: int) -> str: ...
    def refund(self, transaction_id: str) -> None: ...

@dataclass
class StripeAdapter:
    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe
        stripe.api_key = self.api_key
        intent = stripe.PaymentIntent.create(
            amount=amount_krw, currency="krw",
            customer=customer_id, confirm=True,
        )
        return intent.id

    def refund(self, transaction_id: str) -> None:
        import stripe
        stripe.api_key = self.api_key
        stripe.Refund.create(payment_intent=transaction_id)

@dataclass
class FakePaymentGateway:
    charged: list[tuple[str, int]] = None

    def __post_init__(self) -> None:
        self.charged = self.charged or []

    def charge(self, customer_id: str, amount_krw: int) -> str:
        tx_id = f"fake-{len(self.charged)}"
        self.charged.append((customer_id, amount_krw))
        return tx_id

    def refund(self, transaction_id: str) -> None:
        pass

class OrderService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway

    def process_order(self, customer_id: str, total: int) -> str:
        return self._gateway.charge(customer_id, total)
```

## 예외 번역: Adapter의 또 다른 책임

AI가 만든 Adapter에서 가장 자주 빠뜨리는 부분이 예외 번역입니다. 외부 SDK가 던지는 예외를 도메인에 그대로 흘리면, 도메인 코드가 SDK의 예외 계층을 알아야 합니다.

```python
class PaymentError(Exception):
    def __init__(self, message: str, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable

@dataclass
class StripeAdapter:
    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe
        stripe.api_key = self.api_key
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_krw, currency="krw",
                customer=customer_id, confirm=True,
            )
            return intent.id
        except stripe.error.CardError as e:
            raise PaymentError(str(e), retriable=False) from e
        except stripe.error.RateLimitError as e:
            raise PaymentError(str(e), retriable=True) from e
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe 내부 오류: {e}", retriable=True) from e
```

도메인은 `PaymentError`만 알면 됩니다. Stripe 고유의 예외 계층은 Adapter 밖으로 새지 않습니다.

## Before / After: SDK 교체 비용 차이

**Before — SDK가 도메인에 직접 박힌 경우:**

Toss Payments로 교체 시 `OrderService`, `RefundService`, `WebhookHandler` 세 파일을 동시에 열어야 합니다.

**After — Adapter로 분리된 경우:**

```python
# TossAdapter 새로 추가
@dataclass
class TossAdapter:
    secret_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        # Toss API 호출
        ...

    def refund(self, transaction_id: str) -> None:
        # Toss 환불 API 호출
        ...

# 진입점에서만 교체
gateway = TossAdapter(secret_key=os.environ["TOSS_SECRET"])
service = OrderService(gateway=gateway)
```

`OrderService`, `RefundService`, `WebhookHandler`는 한 글자도 바뀌지 않습니다.

## Adapter vs Facade vs Wrapper 비교

| 구분 | 목적 | 대상 |
| --- | --- | --- |
| Adapter | 기존 계약에 맞추기 위한 번역 | 인터페이스 1개 |
| Facade | 복잡한 하위 시스템을 단순화 | 하위 시스템 여러 개 |
| Wrapper | 일반 용어 (감싸는 행위) | 특정 구조 없음 |

AI가 "Wrapper로 감싸줘"라고 하면 의도가 불분명합니다. "Adapter로 인터페이스를 번역해줘" 또는 "Facade로 단순화해줘"처럼 패턴 이름을 명시하세요.

## AI 활용 팁

**Adapter 패턴 적용 요청:**

```
"지금 OrderService에서 stripe.PaymentIntent.create()를 직접 호출해.
Adapter 패턴으로 리팩토링해서:
- PaymentGateway Protocol 정의 (charge, refund)
- StripeAdapter가 Protocol 구현
- 예외를 도메인 PaymentError로 번역
- 테스트용 FakePaymentGateway 포함
OrderService는 Protocol만 알도록 해줘."
```

**API 버전 마이그레이션 요청:**

```
"결제 API v1에서 v2로 마이그레이션 중이야.
기존 v1 클라이언트를 유지하면서 내부적으로 v2를 호출하는
V1ToV2Adapter를 만들어줘. 마이그레이션이 끝나면 Adapter를
제거하는 계획도 설명해줘."
```

## 운영 체크리스트

- [ ] Adapter 패턴이 끊어내는 의존성을 그래프로 설명할 수 있습니다.
- [ ] AI가 만든 SDK 코드에 예외 번역을 추가할 수 있습니다.
- [ ] FakeAdapter를 만들어 테스트에서 외부 API 없이 검증할 수 있습니다.
- [ ] Adapter와 Facade의 차이를 설명할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 Adapter는 외부 SDK 의존성을 한 파일로 수렴시킵니다. 둘째 예외 번역은 Adapter의 책임입니다. SDK 예외가 도메인으로 새지 않아야 합니다. 셋째 Fake Adapter를 만들면 테스트에서 외부 API 없이도 도메인 로직을 검증할 수 있습니다.

## 처음 질문으로 돌아가기

- **AI가 외부 SDK를 도메인에 직접 연결했을 때 어떻게 Adapter로 분리할까요?**
  - 도메인이 원하는 Protocol을 먼저 정의하고, SDK 호출을 Protocol을 구현하는 Adapter 클래스 안으로 옮기면 됩니다. AI에게 이 구조를 명시해서 요청하세요.
- **Adapter와 Facade는 어떻게 다를까요?**
  - Adapter는 하나의 인터페이스를 다른 인터페이스로 번역합니다. Facade는 여러 하위 시스템을 단순한 진입점 뒤에 숨깁니다.
- **AI가 만든 Adapter 코드에서 예외 번역이 왜 중요할까요?**
  - SDK가 바뀌어도 도메인 코드가 처리하는 예외 타입은 바뀌지 않아야 합니다. 예외 번역이 없으면 SDK 예외가 도메인 전체에 퍼집니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Anti-Corruption Layer (Martin Fowler)](https://docs.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)

### 실무 확장 읽을거리

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Adapter, Structural, AI코딩, SDK연동
