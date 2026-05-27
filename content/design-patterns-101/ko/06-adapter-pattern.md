---
series: design-patterns-101
episode: 6
title: "디자인 패턴 101 (6/10): 어댑터 패턴"
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
  - DesignPatterns
  - Adapter
  - Structural
  - Compatibility
  - Wrapper
seo_description: Adapter 패턴으로 외부 SDK 인터페이스를 도메인 경계 뒤에 가두고 테스트 가능성과 교체 가능성을 높이는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (6/10): 어댑터 패턴

결제 SDK를 교체해야 하는 날이 옵니다. 저는 이 상황을 세 번 겪었습니다. 첫 번째는 Stripe에서 Toss Payments로 바꿀 때였고, 두 번째는 SES에서 SendGrid로 메일 발송을 옮길 때였고, 세 번째는 사내 인증 서버가 OAuth2 표준으로 전환될 때였습니다. 세 번 모두 같은 교훈을 남겼습니다. 외부 SDK의 시그니처가 도메인 코드 곳곳에 박혀 있으면, 교체 작업은 "SDK 하나 바꾸기"가 아니라 "서비스 전체 리팩터링"이 됩니다.

이 글은 Design Patterns 101 시리즈의 여섯 번째 글입니다. 3장에서 Adapter를 개요 수준으로 소개했으니, 여기서는 실무에서 Adapter가 어떤 경계를 만들고, 그 경계가 어떤 비용을 부르는지 깊이 파고듭니다.

![Design Patterns 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/06/06-01-concept-at-a-glance.ko.png)
*외부 SDK 호출이 Adapter 경계를 거쳐 도메인에 도달하는 흐름*
> Adapter 패턴은 어느 한쪽도 다시 쓰지 않고, 거의 맞지만 정확히는 다른 두 인터페이스 사이에 얇은 번역기를 끼워 넣는 도구입니다.

## 먼저 던지는 질문

- Adapter를 두면 정확히 어떤 의존성이 끊어질까요?
- Anti-Corruption Layer와 Adapter는 같은 것일까요, 다른 것일까요?
- Adapter가 많아지면 어떤 비용이 쌓일까요?

## 외부 SDK를 도메인이 원하는 모양으로 바꾸기

Adapter의 핵심은 한 문장입니다. **도메인이 외부 SDK의 언어를 배우지 않게 만드는 것.** 도메인은 자기가 정의한 Protocol만 알면 되고, 외부 SDK의 메서드 이름, 예외 타입, 응답 구조는 Adapter 안에 갇힙니다.

Stripe SDK를 감싸는 예시를 봅시다.

```python
from dataclasses import dataclass
from typing import Protocol


class PaymentGateway(Protocol):
    """도메인이 정의한 결제 계약."""

    def charge(self, customer_id: str, amount_krw: int) -> str:
        """결제를 실행하고 트랜잭션 ID를 반환합니다."""
        ...

    def refund(self, transaction_id: str) -> None: ...


@dataclass
class StripeAdapter:
    """Stripe SDK를 PaymentGateway 계약으로 번역합니다."""

    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe

        stripe.api_key = self.api_key
        intent = stripe.PaymentIntent.create(
            amount=amount_krw,
            currency="krw",
            customer=customer_id,
            confirm=True,
        )
        return intent.id

    def refund(self, transaction_id: str) -> None:
        import stripe

        stripe.api_key = self.api_key
        stripe.Refund.create(payment_intent=transaction_id)
```

도메인 서비스는 `PaymentGateway`만 봅니다.

```python
def process_order(gateway: PaymentGateway, customer_id: str, total: int) -> str:
    tx_id = gateway.charge(customer_id, total)
    # 주문 상태 업데이트, 이벤트 발행 등
    return tx_id
```

Stripe를 Toss Payments로 교체할 때 `process_order`는 한 글자도 바뀌지 않습니다. 새 `TossAdapter`를 만들어 주입하면 끝입니다. 이것이 Adapter가 주는 가장 현실적인 가치입니다.

## Adapter를 두는 순간 끊어지는 의존성

Adapter가 없을 때 의존 그래프는 이렇습니다.

```text
[OrderService] → [stripe 패키지]
[RefundService] → [stripe 패키지]
[WebhookHandler] → [stripe 패키지]
```

세 모듈 모두 `stripe`를 직접 import합니다. Stripe가 메이저 버전을 올리면 세 곳을 동시에 고쳐야 합니다.

Adapter를 두면 그래프가 바뀝니다.

```text
[OrderService] → [PaymentGateway (Protocol)]
[RefundService] → [PaymentGateway (Protocol)]
[WebhookHandler] → [PaymentGateway (Protocol)]
                         ↑
                   [StripeAdapter] → [stripe 패키지]
```

`stripe` 패키지에 의존하는 모듈이 하나로 줄었습니다. 변경 영향 범위가 Adapter 한 파일로 수렴합니다. 이 구조에서 테스트도 자연스러워집니다. `OrderService` 단위 테스트에서 Stripe 서버를 호출할 이유가 없으니, InMemory 구현을 끼우면 됩니다.

```python
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
```

## Anti-Corruption Layer로서의 Adapter

Domain-Driven Design에서 Anti-Corruption Layer(ACL)는 외부 바운디드 컨텍스트의 모델이 내부 도메인을 오염시키지 못하게 막는 번역 계층입니다. Adapter는 이 ACL을 구현하는 가장 흔한 수단입니다.

외부 결제 API가 다음과 같은 응답을 준다고 합시다.

```python
# 외부 API 응답 (우리가 통제할 수 없는 구조)
external_response = {
    "txn_ref": "TXN-9912",
    "amt": 50000,
    "ccy": "KRW",
    "sts": "OK",
    "ts": "2026-05-23T10:00:00Z",
}
```

이 구조를 도메인 곳곳에서 직접 파싱하면, 외부 API가 필드 이름을 바꾸는 순간 도메인 전체가 흔들립니다. ACL Adapter는 이 번역을 한 곳에서 처리합니다.

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaymentResult:
    """도메인이 이해하는 결제 결과."""

    transaction_id: str
    amount: int
    currency: str
    success: bool
    completed_at: datetime


class ExternalPaymentAdapter:
    """외부 결제 API 응답을 도메인 모델로 번역합니다."""

    def translate(self, raw: dict) -> PaymentResult:
        return PaymentResult(
            transaction_id=raw["txn_ref"],
            amount=raw["amt"],
            currency=raw["ccy"],
            success=raw["sts"] == "OK",
            completed_at=datetime.fromisoformat(raw["ts"]),
        )
```

ACL과 단순 Adapter의 차이는 의도에 있습니다. 단순 Adapter는 시그니처를 맞추는 데 집중하고, ACL은 **외부 모델의 개념 자체가 내부로 침투하지 못하게** 막습니다. 외부에서 `sts`라고 부르는 것을 내부에서는 `success: bool`로 재해석하는 것이 ACL의 핵심입니다.

## Adapter vs Facade vs Wrapper — 무엇이 다른가

이 세 용어는 자주 혼용됩니다. 차이를 코드로 보겠습니다.

**Adapter**: 하나의 인터페이스를 다른 인터페이스로 번역합니다. 호출자가 기대하는 계약이 이미 존재하고, 외부 구현이 그 계약과 맞지 않을 때 씁니다.

```python
class NotificationSender(Protocol):
    def send(self, recipient: str, body: str) -> None: ...

class SlackWebhookAdapter:
    """Slack webhook API를 NotificationSender 계약으로 번역."""

    def __init__(self, webhook_url: str) -> None:
        self._url = webhook_url

    def send(self, recipient: str, body: str) -> None:
        import httpx

        httpx.post(self._url, json={"channel": recipient, "text": body})
```

**Facade**: 여러 하위 시스템을 하나의 단순한 진입점 뒤에 숨깁니다. 기존 계약이 없고, 복잡한 조합을 단순화하려는 목적입니다.

```python
class DeployFacade:
    """빌드 + 테스트 + 배포를 한 번에 실행하는 진입점."""

    def __init__(self, builder, tester, deployer) -> None:
        self._builder = builder
        self._tester = tester
        self._deployer = deployer

    def release(self, version: str) -> None:
        artifact = self._builder.build(version)
        self._tester.run_all(artifact)
        self._deployer.push(artifact)
```

**Wrapper**: 패턴 이름이 아니라 일반 용어입니다. Adapter도 Wrapper이고, Decorator도 Wrapper입니다. "감싼다"는 행위를 가리킬 뿐, 구조적 의도를 구분하지 않습니다.

정리하면 이렇습니다.

| 구분 | 목적 | 대상 |
| --- | --- | --- |
| Adapter | 기존 계약에 맞추기 위한 번역 | 인터페이스 1개 |
| Facade | 복잡한 하위 시스템을 단순화 | 하위 시스템 여러 개 |
| Wrapper | 일반 용어 (감싸는 행위) | 특정 구조 없음 |

## Python에서 다중상속 기반 Class Adapter를 피해야 하는 이유

GoF 책은 Adapter를 두 가지로 나눕니다. Object Adapter(합성)와 Class Adapter(다중 상속). C++에서는 Class Adapter가 자연스러운 선택지였지만, Python에서는 거의 항상 Object Adapter가 낫습니다.

Class Adapter를 Python으로 억지로 만들면 이렇게 됩니다.

```python
class LegacyPrinter:
    def print_old(self, text: str) -> None:
        print(f"[LEGACY] {text}")


class Printer(Protocol):
    def print_text(self, text: str) -> None: ...


class PrinterClassAdapter(LegacyPrinter):
    """다중 상속으로 LegacyPrinter를 Printer 계약에 맞춤."""

    def print_text(self, text: str) -> None:
        self.print_old(text)
```

문제점은 세 가지입니다.

1. **LegacyPrinter의 모든 public 메서드가 노출됩니다.** `print_old`를 외부에서 직접 호출할 수 있어 캡슐화가 깨집니다.
2. **LegacyPrinter가 변경되면 Adapter도 깨집니다.** 상속은 부모의 내부 구현에 결합하기 때문입니다.
3. **다중 상속이 겹치면 MRO(Method Resolution Order) 충돌이 발생합니다.** 두 개 이상의 Adaptee를 동시에 상속하면 디버깅이 극도로 어려워집니다.

Object Adapter는 이 문제를 모두 피합니다.

```python
@dataclass
class PrinterObjectAdapter:
    """합성으로 LegacyPrinter를 감쌈."""

    _legacy: LegacyPrinter

    def print_text(self, text: str) -> None:
        self._legacy.print_old(text)
```

`_legacy`는 private이고, 외부에서 `print_old`를 직접 호출할 경로가 없습니다. 저는 Python 프로젝트에서 Class Adapter를 선택한 적이 한 번도 없습니다. 합성이 항상 더 안전하고 유연합니다.

## API 버전 마이그레이션에서 Adapter가 자연스러운 이유

API v1에서 v2로 마이그레이션할 때, 모든 클라이언트를 한 번에 전환하는 것은 현실적으로 불가능합니다. 이때 Adapter는 v1 인터페이스를 유지하면서 내부적으로 v2를 호출하는 호환 계층 역할을 합니다.

```python
from dataclasses import dataclass


@dataclass
class UserV1:
    """v1 API가 반환하던 사용자 모델."""

    id: int
    name: str
    email: str


@dataclass
class UserV2:
    """v2 API의 사용자 모델 — 필드가 분리됨."""

    user_id: str  # UUID로 변경
    display_name: str
    contact: dict  # {"email": ..., "phone": ...}


class UserServiceV1Protocol(Protocol):
    def get_user(self, user_id: int) -> UserV1: ...


class V1ToV2Adapter:
    """v1 계약을 유지하면서 내부적으로 v2 서비스를 호출합니다."""

    def __init__(self, v2_client) -> None:
        self._v2 = v2_client

    def get_user(self, user_id: int) -> UserV1:
        v2_user: UserV2 = self._v2.get_user_by_legacy_id(user_id)
        return UserV1(
            id=user_id,
            name=v2_user.display_name,
            email=v2_user.contact["email"],
        )
```

v1 클라이언트는 아무것도 모른 채 기존 인터페이스를 계속 호출합니다. 내부에서는 이미 v2 서비스가 돌고 있습니다. 클라이언트가 모두 v2로 전환되면 이 Adapter를 제거하면 됩니다. Adapter는 영구적인 구조가 아니라 **마이그레이션 기간 동안만 존재하는 임시 번역층**으로도 쓸 수 있습니다.

## 테스트 경계에서의 Adapter

Adapter가 만드는 경계는 테스트 전략에 직접적인 영향을 줍니다. 저는 테스트를 세 층으로 나눕니다.

1. **도메인 단위 테스트**: Fake Adapter를 주입합니다. 외부 네트워크 호출 없이 밀리초 단위로 실행됩니다.
2. **Adapter 통합 테스트**: 실제 외부 서비스(또는 sandbox)를 호출합니다. 느리지만 번역 로직이 정확한지 검증합니다.
3. **E2E 테스트**: 전체 시스템을 관통합니다.

이 분리가 가능한 이유는 Adapter가 명확한 이음새(seam)를 제공하기 때문입니다. Adapter 없이 도메인 코드가 SDK를 직접 호출하면, 단위 테스트에서 mock을 남발해야 합니다. mock은 외부 API의 내부 구현을 테스트 코드에 복제하는 것이라서, API가 바뀌면 mock도 함께 깨집니다. Adapter를 두면 mock 대상이 "우리가 정의한 Protocol"이 되므로, 외부 변경과 무관하게 테스트가 안정됩니다.

```python
def test_order_charges_correct_amount() -> None:
    gateway = FakePaymentGateway()
    tx_id = process_order(gateway, customer_id="cust-1", total=30000)

    assert tx_id == "fake-0"
    assert gateway.charged == [("cust-1", 30000)]
```

이 테스트는 Stripe가 v3로 올라가든, Toss로 교체되든 깨지지 않습니다.

## Two-Way Adapter: 양방향 번역이 필요한 경우

대부분의 Adapter는 단방향입니다. 외부 → 내부로 번역하거나, 내부 → 외부로 번역합니다. 그런데 레거시 시스템과 신규 시스템이 공존하는 마이그레이션 기간에는 양방향 번역이 필요할 수 있습니다.

```python
from dataclasses import dataclass


@dataclass
class LegacyEvent:
    event_type: str  # "ORDER_CREATED"
    payload: str  # JSON string


@dataclass
class DomainEvent:
    name: str  # "order.created"
    data: dict


class BidirectionalEventAdapter:
    """레거시 이벤트 ↔ 도메인 이벤트 양방향 번역."""

    def to_domain(self, legacy: LegacyEvent) -> DomainEvent:
        import json

        return DomainEvent(
            name=legacy.event_type.lower().replace("_", "."),
            data=json.loads(legacy.payload),
        )

    def to_legacy(self, domain: DomainEvent) -> LegacyEvent:
        import json

        return LegacyEvent(
            event_type=domain.name.upper().replace(".", "_"),
            payload=json.dumps(domain.data),
        )
```

양방향 Adapter는 편리하지만 위험합니다. 번역 규칙이 양쪽에서 일관되어야 하고, 한쪽에서 표현할 수 없는 개념이 있으면 정보가 손실됩니다. 저는 양방향 Adapter를 쓸 때 반드시 왕복 테스트(roundtrip test)를 작성합니다.

```python
def test_roundtrip() -> None:
    adapter = BidirectionalEventAdapter()
    original = DomainEvent(name="order.created", data={"id": 1})

    legacy = adapter.to_legacy(original)
    restored = adapter.to_domain(legacy)

    assert restored == original
```

왕복 테스트가 깨지면 번역 과정에서 정보가 유실되고 있다는 신호입니다.

## Adapter가 너무 많아지면 생기는 비용

Adapter는 공짜가 아닙니다. 프로젝트에 Adapter가 쌓이면 다음 비용이 누적됩니다.

**호출 경로가 길어집니다.** 도메인 → Protocol → Adapter → SDK. 디버깅할 때 스택 트레이스를 한 단계 더 거슬러 올라가야 합니다. 장애 상황에서 "이 에러가 Adapter 안에서 난 건지, SDK에서 난 건지" 구분하는 데 시간이 걸립니다.

**프로토콜 불일치를 숨길 수 있습니다.** 외부 SDK가 비동기인데 도메인 Protocol이 동기로 정의되어 있으면, Adapter가 내부에서 `asyncio.run()`을 호출하는 식으로 불일치를 감추게 됩니다. 이런 Adapter는 동작은 하지만 성능 병목이 됩니다.

**Adapter 자체가 비대해집니다.** 외부 SDK의 메서드가 20개인데 도메인이 3개만 쓴다면, Adapter는 3개만 번역하면 됩니다. 그런데 "나중에 쓸 수도 있으니까" 하고 20개를 모두 감싸면, Adapter가 SDK의 거울이 되어 버립니다. 이 상태에서는 SDK가 바뀔 때 Adapter도 통째로 바뀌므로 경계의 의미가 사라집니다.

저는 다음 기준으로 Adapter 비용을 관리합니다.

- Adapter 하나가 번역하는 메서드가 5개를 넘으면, 도메인 Protocol이 너무 넓은 것은 아닌지 의심합니다.
- Adapter 안에 조건 분기가 생기면, 비즈니스 로직이 침투한 것이므로 도메인으로 빼냅니다.
- Adapter가 다른 Adapter를 호출하면, 경계가 중첩된 것이므로 하나로 합칩니다.

## 예외 번역은 Adapter의 책임이다

외부 SDK가 던지는 예외를 도메인에 그대로 흘리면, 도메인 코드가 SDK의 예외 계층을 알아야 합니다. Adapter는 이 예외를 도메인 예외로 번역해야 합니다.

```python
class PaymentError(Exception):
    """도메인 결제 예외."""

    def __init__(self, message: str, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable


@dataclass
class StripeAdapterWithErrorTranslation:
    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe

        stripe.api_key = self.api_key
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_krw,
                currency="krw",
                customer=customer_id,
                confirm=True,
            )
            return intent.id
        except stripe.error.CardError as e:
            raise PaymentError(str(e), retriable=False) from e
        except stripe.error.RateLimitError as e:
            raise PaymentError(str(e), retriable=True) from e
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe 내부 오류: {e}", retriable=True) from e
```

도메인은 `PaymentError`만 알면 됩니다. `retriable` 플래그를 보고 재시도 여부를 결정할 수 있고, Stripe 고유의 예외 계층은 Adapter 밖으로 새지 않습니다.

## 처음 질문으로 돌아가기

- **Adapter를 두면 정확히 어떤 의존성이 끊어질까요?**
  - 도메인 모듈이 외부 SDK 패키지를 직접 import하는 의존성이 끊어집니다. 본문의 의존 그래프에서 본 것처럼, Adapter 도입 전에는 세 모듈이 모두 `stripe`에 의존했지만 도입 후에는 Adapter 한 파일만 의존합니다. 변경 영향 범위가 수렴하고, 테스트에서 Fake를 주입할 이음새가 생깁니다.

- **Anti-Corruption Layer와 Adapter는 같은 것일까요, 다른 것일까요?**
  - ACL은 DDD의 전략적 개념이고, Adapter는 그 개념을 구현하는 전술적 수단입니다. 단순 Adapter는 시그니처만 맞추지만, ACL로서의 Adapter는 외부 모델의 개념 자체가 내부로 침투하지 못하게 막습니다. 본문의 `ExternalPaymentAdapter`가 `sts`를 `success: bool`로 재해석한 것이 그 차이입니다.

- **Adapter가 많아지면 어떤 비용이 쌓일까요?**
  - 호출 경로가 길어져 디버깅 시간이 늘고, 프로토콜 불일치를 감출 위험이 생기며, Adapter 자체가 비대해지면 경계의 의미가 사라집니다. 저는 메서드 5개 초과, 내부 조건 분기, Adapter 간 호출을 경고 신호로 삼아 관리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- **Adapter 패턴 (현재 글)**
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Anti-Corruption Layer (Martin Fowler)](https://docs.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)

### 실무 확장 읽을거리

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [Domain-Driven Design (Eric Evans) — Chapter 14: Maintaining Model Integrity](https://www.domainlanguage.com/ddd/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Adapter, Structural, Compatibility, Wrapper
