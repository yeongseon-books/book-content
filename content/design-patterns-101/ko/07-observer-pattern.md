---
series: design-patterns-101
episode: 7
title: "디자인 패턴 101 (7/10): 옵저버 패턴"
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
  - Observer
  - PubSub
  - Events
  - Behavioral
seo_description: Observer 패턴으로 직접 호출을 통지 구조로 바꾸어 결합도를 낮추고 확장 지점을 분리하는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (7/10): 옵저버 패턴

주문이 제출되면 메일을 보내고, 슬랙에 알리고, 창고를 예약합니다. 처음에는 `Order.submit()` 안에 세 줄을 추가하면 끝입니다. 그런데 한 달 뒤 SMS 알림이 추가되고, 분석 이벤트 전송이 추가되고, 포인트 적립이 추가됩니다. 이제 `Order`는 주문 처리보다 후속 작업을 더 많이 알고 있습니다. 후속 작업 하나가 느려지면 주문 전체가 느려지고, 후속 작업 하나가 예외를 던지면 주문이 실패합니다. 저는 이 상황을 여러 프로젝트에서 반복해서 봤습니다.

이 글은 Design Patterns 101 시리즈의 일곱 번째 글입니다. 4장에서 Observer를 개요 수준으로 소개했으니, 여기서는 동기/비동기 차이, 메모리 누수, 에러 격리, 메시지 큐와의 경계까지 깊이 들어갑니다.

![Observer 패턴 발행자와 구독자의 결합 끊기](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/07/07-01-concept-at-a-glance.ko.png)
*발행자가 구독자를 모르는 상태에서 이벤트를 전파하는 구조*
> Observer 패턴은 '무슨 일이 일어났다'와 '누가 그것에 반응하는가'를 떼어 놓아, 송신자는 수신자를 모르고 수신자는 송신자를 소유하지 않습니다.

## 먼저 던지는 질문

- Observer 패턴을 도입하면 정확히 어떤 결합이 끊어지고, 대신 어떤 비용이 생길까요?
- 동기 Observer와 비동기 이벤트 버스는 언제 갈라져야 할까요?
- 구독자가 예외를 던지거나 느려지면 발행자에게 무슨 일이 생길까요?

## Observer가 풀려는 진짜 문제: 발신자와 수신자의 결합 끊기

직접 호출은 가장 단순한 통신입니다. `A`가 `B.do()`를 부르면 끝입니다. 문제는 `A`가 `B`, `C`, `D`, `E`를 전부 알아야 할 때 시작됩니다. 수신자가 늘어날 때마다 발신자를 열어야 하고, 수신자 하나를 제거할 때도 발신자를 수정해야 합니다.

Observer는 이 관계를 뒤집습니다. 발신자(Subject)는 "무슨 일이 일어났다"만 알리고, 누가 듣는지는 모릅니다. 수신자(Observer)는 자기가 관심 있는 이벤트에 스스로 등록합니다. 이제 확장은 발신자 수정이 아니라 구독자 추가로 이루어집니다.

```python
# before: Order가 모든 후속 작업을 직접 호출
class Order:
    def submit(self):
        self.save()
        send_email(self.user)
        slack_notify(self.channel)
        warehouse.reserve(self.items)
        analytics.track("order_submitted", self.id)
        points.accrue(self.user, self.total)
```

```python
# after: Order는 이벤트만 발행
class Order:
    def __init__(self, bus: "EventBus") -> None:
        self.bus = bus

    def submit(self) -> None:
        self.save()
        self.bus.publish(OrderSubmitted(user=self.user, items=self.items))
```

`Order`의 책임이 "주문 저장 + 이벤트 발행"으로 줄었습니다. 메일, 슬랙, 창고, 분석, 포인트는 각자 구독자로 존재합니다. 이 분리가 Observer의 전부입니다.

## Python에서 Observer를 표현하는 세 가지 방식

### 방식 1: 콜백 리스트 — 가장 작은 구현

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class EventBus:
    _subs: dict[str, list[Callable]] = field(default_factory=dict)

    def subscribe(self, topic: str, fn: Callable) -> None:
        self._subs.setdefault(topic, []).append(fn)

    def unsubscribe(self, topic: str, fn: Callable) -> None:
        self._subs.get(topic, []).remove(fn)

    def publish(self, topic: str, event: Any) -> None:
        for fn in self._subs.get(topic, []):
            fn(event)
```

15줄이면 동작하는 Observer입니다. 토픽별 콜백 리스트를 순회하며 호출합니다. 단순하지만 실무에서 이대로 쓰면 세 가지 문제가 생깁니다. 에러 격리가 없고, 느린 구독자가 발행자를 블로킹하고, 구독 해지를 잊으면 메모리가 샙니다. 이 문제들은 뒤에서 하나씩 다룹니다.

### 방식 2: Protocol 기반 — 타입 안전한 Observer

```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class OrderSubmitted:
    user: str
    items: list[str]

class OrderObserver(Protocol):
    def on_order_submitted(self, event: OrderSubmitted) -> None: ...

class EmailNotifier:
    def on_order_submitted(self, event: OrderSubmitted) -> None:
        print(f"메일 발송: {event.user}")

class SlackNotifier:
    def on_order_submitted(self, event: OrderSubmitted) -> None:
        print(f"슬랙 알림: #{event.user}")

@dataclass
class OrderService:
    observers: list[OrderObserver]

    def submit(self, user: str, items: list[str]) -> None:
        event = OrderSubmitted(user=user, items=items)
        for obs in self.observers:
            obs.on_order_submitted(event)
```

Protocol을 쓰면 IDE가 구독자의 메서드 시그니처를 검증합니다. 이벤트가 `dataclass`이므로 payload 구조도 명시적입니다. 이 방식은 이벤트 종류가 적고 구독자 인터페이스를 엄격하게 관리하고 싶을 때 적합합니다.

### 방식 3: 데코레이터 등록 — Django signals 스타일

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Signal:
    _receivers: list[Callable] = field(default_factory=list)

    def connect(self, fn: Callable) -> Callable:
        self._receivers.append(fn)
        return fn

    def send(self, **kwargs: Any) -> list[Any]:
        return [fn(**kwargs) for fn in self._receivers]

order_submitted = Signal()

@order_submitted.connect
def notify_email(user: str, **kwargs: Any) -> None:
    print(f"메일: {user}")

@order_submitted.connect
def notify_slack(user: str, **kwargs: Any) -> None:
    print(f"슬랙: {user}")

# 발행
order_submitted.send(user="alice", items=["book", "pen"])
```

데코레이터로 등록하면 구독자가 선언 시점에 바로 연결됩니다. Django의 `django.dispatch.Signal`이 정확히 이 구조입니다.

## 동기 Observer와 비동기 이벤트 버스의 차이

동기 Observer는 `publish()`가 모든 구독자를 순차 호출한 뒤에야 리턴합니다. 구독자가 10ms씩 걸리는 게 5개면 발행자는 50ms를 기다립니다. 이 지연이 허용 가능한지가 동기/비동기를 가르는 기준입니다.

```python
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

@dataclass
class AsyncEventBus:
    _subs: dict[str, list[Callable[..., Coroutine]]] = field(default_factory=dict)

    def subscribe(self, topic: str, fn: Callable[..., Coroutine]) -> None:
        self._subs.setdefault(topic, []).append(fn)

    async def publish(self, topic: str, event: Any) -> None:
        tasks = [fn(event) for fn in self._subs.get(topic, [])]
        await asyncio.gather(*tasks, return_exceptions=True)
```

`asyncio.gather`에 `return_exceptions=True`를 넘기면 한 구독자의 예외가 다른 구독자를 중단시키지 않습니다. 동기 버전에서는 이 격리를 직접 구현해야 합니다.

**판단 기준 정리:**

| 조건 | 선택 |
| --- | --- |
| 구독자 실행 시간 합 < 요청 SLA | 동기 Observer |
| 구독자 중 하나라도 네트워크 I/O 포함 | 비동기 이벤트 버스 |
| 구독자 실패가 발행자 트랜잭션에 영향 주면 안 됨 | 비동기 + 별도 재시도 |
| 이벤트 순서 보장 필수 | 동기 또는 단일 consumer 큐 |

## Observer가 조용히 만드는 세 가지 장애

### 장애 1: 느린 구독자가 발행자를 블로킹

동기 Observer에서 구독자 하나가 외부 API를 호출하며 3초를 기다리면, 발행자도 3초를 기다립니다. 주문 API의 응답 시간이 갑자기 3초가 되는 겁니다. 원인을 추적하면 `Order.submit()` → `EventBus.publish()` → `AnalyticsTracker.on_order()` → 외부 HTTP 호출로 이어지는 체인이 나옵니다.

**해결:** 네트워크 I/O가 있는 구독자는 비동기로 분리하거나, 동기 Observer 안에서 timeout을 겁니다.

### 장애 2: 한 구독자의 예외가 나머지를 중단

콜백 리스트를 순회하다가 두 번째 구독자가 `ValueError`를 던지면, 세 번째 이후 구독자는 실행되지 않습니다.

```python
# 에러 격리가 있는 publish
import logging

logger = logging.getLogger(__name__)

def publish_safe(self, topic: str, event: Any) -> None:
    for fn in self._subs.get(topic, []):
        try:
            fn(event)
        except Exception:
            logger.exception("Observer failed: %s on topic %s", fn, topic)
```

`try/except`로 감싸고 로깅하면 나머지 구독자는 정상 실행됩니다. 실패한 구독자는 별도 알림 채널로 보고합니다.

### 장애 3: 구독 해지를 잊으면 메모리가 샌다

구독자 객체가 이벤트 버스의 콜백 리스트에 참조로 남아 있으면, 해당 객체는 가비지 컬렉션 대상이 되지 않습니다. 웹 프레임워크에서 요청마다 구독자를 생성하고 해지하지 않으면, 메모리가 요청 수에 비례해 증가합니다.

## WeakRef로 메모리 누수 막기

Python의 `weakref` 모듈은 참조 카운트를 증가시키지 않는 약한 참조를 제공합니다. 구독자가 다른 곳에서 더 이상 참조되지 않으면 자동으로 사라집니다.

```python
import weakref
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class WeakEventBus:
    _subs: dict[str, list[weakref.WeakMethod | weakref.ref]] = field(
        default_factory=dict
    )

    def subscribe(self, topic: str, fn: Callable) -> None:
        if hasattr(fn, "__self__"):
            ref = weakref.WeakMethod(fn, self._make_cleanup(topic))
        else:
            ref = weakref.ref(fn, self._make_cleanup(topic))
        self._subs.setdefault(topic, []).append(ref)

    def _make_cleanup(self, topic: str) -> Callable:
        def cleanup(ref: weakref.ref) -> None:
            self._subs.get(topic, []).remove(ref)  # type: ignore[arg-type]
        return cleanup

    def publish(self, topic: str, event: Any) -> None:
        for ref in list(self._subs.get(topic, [])):
            fn = ref()
            if fn is not None:
                fn(event)
```

`WeakMethod`는 바운드 메서드에 대한 약한 참조입니다. 객체가 소멸되면 `cleanup` 콜백이 호출되어 구독 리스트에서 자동 제거됩니다. Django signals도 내부적으로 `weakref`를 사용합니다.

**주의:** 람다나 클로저는 `weakref`로 감싸면 즉시 수거됩니다. 다른 곳에서 강한 참조를 유지하지 않기 때문입니다. `weakref` 기반 버스에는 바운드 메서드나 모듈 수준 함수를 등록해야 합니다.

## Observer가 메시지 큐와 갈라지는 지점

Observer와 메시지 큐(RabbitMQ, Kafka, Redis Streams)는 둘 다 발행-구독 구조입니다. 그런데 운영 특성이 완전히 다릅니다.

| 특성 | In-process Observer | 메시지 큐 |
| --- | --- | --- |
| 전달 보장 | 없음 (프로세스 죽으면 유실) | 있음 (디스크 영속) |
| 순서 보장 | 등록 순서 (결정적) | 파티션/큐 단위 |
| 재시도 | 직접 구현 | 브로커가 제공 |
| 지연 | 함수 호출 수준 (ns~μs) | 네트워크 왕복 (ms) |
| 배포 경계 | 단일 프로세스 | 프로세스/서버 간 |
| 확장 | 구독자 수 = 함수 호출 수 | consumer 수평 확장 |

**판단 기준:** 같은 프로세스 안에서 결합만 끊으면 되면 Observer로 충분합니다. 프로세스가 죽어도 이벤트가 유실되면 안 되거나, 구독자가 별도 서비스에 있으면 메시지 큐가 필요합니다.

저는 이 경계를 "Observer는 설계 패턴이고, 메시지 큐는 인프라"라고 구분합니다. Observer로 시작해서 나중에 큐로 교체하는 경로가 자연스럽습니다. 이벤트 이름과 payload 구조를 처음부터 `dataclass`로 명시해 두면, 나중에 직렬화해서 큐에 넣을 때 변환 비용이 거의 없습니다.

## Django signals와 Flask blinker — 실무에서 쓰이는 Observer

### Django signals

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from myapp.models import Order

@receiver(post_save, sender=Order)
def on_order_saved(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(instance.user)
        track_analytics("order_created", instance.id)
```

Django signals는 모델 저장, 요청 시작/종료, 마이그레이션 등 프레임워크 내부 이벤트에 훅을 거는 Observer입니다. `@receiver` 데코레이터가 구독을 선언합니다.

**실무 주의점:** Django signals는 동기 실행입니다. `on_order_saved` 안에서 외부 API를 호출하면 HTTP 응답이 그만큼 느려집니다. 무거운 작업은 Celery task로 위임하는 게 일반적입니다.

### Flask blinker

```python
from blinker import signal

order_created = signal("order-created")

@order_created.connect
def handle_email(sender, **kwargs):
    print(f"메일 발송: {kwargs['user']}")

@order_created.connect
def handle_analytics(sender, **kwargs):
    print(f"분석 이벤트: {kwargs['order_id']}")

# 발행
order_created.send(current_app._get_current_object(), user="alice", order_id=42)
```

blinker는 Flask의 기본 시그널 라이브러리입니다. `weakref`를 내부적으로 사용하므로 구독자 객체가 소멸되면 자동 해지됩니다.

### pyee — Node.js EventEmitter의 Python 포트

```python
from pyee.base import EventEmitter

ee = EventEmitter()

@ee.on("order_submitted")
def on_order(event):
    print(f"처리: {event}")

ee.emit("order_submitted", {"user": "bob", "total": 50000})
```

pyee는 `on`, `emit`, `once`, `remove_listener` 등 Node.js EventEmitter API를 그대로 제공합니다. asyncio 버전(`AsyncIOEventEmitter`)도 있어서 비동기 구독자를 자연스럽게 등록할 수 있습니다.

## 이벤트 설계: 순서, 재생, 멱등성

Observer를 도입하면 이벤트가 시스템의 계약이 됩니다. 이 계약을 제대로 설계하지 않으면 나중에 디버깅이 극도로 어려워집니다.

**이벤트 이름은 과거형으로 짓습니다.** `order_submitted`, `payment_completed`, `user_registered`. 과거형은 "이미 일어난 사실"을 뜻하므로, 구독자가 이벤트를 받았을 때 발행자의 상태가 이미 확정되었음을 보장합니다.

**이벤트 payload는 dataclass로 명시합니다.**

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass(frozen=True)
class OrderSubmitted:
    order_id: UUID
    user: str
    items: list[str]
    total: int
    occurred_at: datetime
    event_id: UUID = field(default_factory=uuid4)
```

`frozen=True`로 불변성을 보장하고, `event_id`로 중복 처리를 방지합니다.

**멱등성:** 같은 이벤트가 두 번 전달되어도 결과가 같아야 합니다. 네트워크 재시도, 프로세스 재시작 등으로 이벤트가 중복 전달되는 상황은 분산 시스템에서 흔합니다. 구독자는 `event_id`를 기준으로 이미 처리한 이벤트를 건너뛰는 로직을 갖추는 게 안전합니다.

```python
processed_events: set[UUID] = set()

def handle_order(event: OrderSubmitted) -> None:
    if event.event_id in processed_events:
        return
    processed_events.add(event.event_id)
    # 실제 처리
```

**순서 보장:** 동기 Observer는 등록 순서대로 실행됩니다. 비동기에서는 `asyncio.gather`가 동시 실행하므로 순서가 보장되지 않습니다. 순서가 중요한 구독자는 동기로 유지하거나, 단일 consumer 큐를 사용합니다.

## Observer에서 이벤트 드리븐 아키텍처로

Observer 패턴은 이벤트 드리븐 아키텍처(EDA)의 출발점입니다. 단일 프로세스 안의 콜백 리스트에서 시작해, 프로세스 간 메시지 브로커로, 서비스 간 이벤트 스트림으로 확장되는 경로가 자연스럽습니다.

```text
콜백 리스트 (in-process)
    ↓ 구독자가 느려짐
asyncio.Queue (in-process, 비동기)
    ↓ 프로세스 장애 시 유실 불가
Redis Pub/Sub (cross-process, 비영속)
    ↓ 이벤트 재생·감사 필요
Kafka / RabbitMQ (cross-service, 영속)
```

각 단계에서 이벤트 이름과 payload 구조가 동일하면 전환 비용이 낮습니다. 처음부터 `dataclass` 이벤트를 정의하고, 직렬화 가능한 필드만 사용하는 습관이 이 확장을 가능하게 합니다.

## Observer의 비용: 무엇을 잃는가

Observer는 공짜가 아닙니다. 도입하면 다음을 잃습니다.

**흐름 추적이 어려워집니다.** 직접 호출은 IDE에서 "Go to Definition"으로 따라갈 수 있습니다. Observer를 거치면 "이 이벤트를 누가 구독하고 있지?"를 grep으로 찾아야 합니다. 구독자가 10개를 넘으면 전체 흐름을 머릿속에 그리기 어렵습니다.

**에러 전파가 복잡해집니다.** 직접 호출은 예외가 호출자에게 바로 올라갑니다. Observer에서는 구독자의 예외를 어디로 보낼지 별도로 설계해야 합니다. 삼키면 장애가 숨고, 올리면 발행자가 영향받습니다.

**디버깅 시간이 늘어납니다.** "주문 후 메일이 안 갔다"는 버그를 추적할 때, 직접 호출이면 `Order.submit()` 안을 보면 됩니다. Observer면 이벤트가 발행되었는지, 구독자가 등록되어 있는지, 구독자 안에서 예외가 발생했는지를 순서대로 확인해야 합니다.

**순서 의존성이 숨겨집니다.** 구독자 A가 구독자 B보다 먼저 실행되어야 하는 암묵적 의존이 있으면, 등록 순서에 의존하는 취약한 코드가 됩니다.

저는 이 비용을 감수할 가치가 있는 기준을 이렇게 잡습니다. **후속 작업이 3개 이상이고, 앞으로 더 늘어날 가능성이 높으며, 후속 작업의 실패가 발행자의 핵심 책임을 중단시키면 안 될 때.** 이 조건을 만족하지 않으면 직접 호출이 더 낫습니다.

## 처음 질문으로 돌아가기

- **Observer 패턴을 도입하면 정확히 어떤 결합이 끊어지고, 대신 어떤 비용이 생길까요?**
  - 발행자가 구독자의 존재와 수를 모르게 되므로, 후속 작업 추가/제거가 발행자 수정 없이 가능해집니다. 대신 흐름 추적이 grep 의존으로 바뀌고, 에러 전파 경로를 별도로 설계해야 하며, 순서 의존성이 암묵적으로 숨겨지는 비용이 생깁니다.

- **동기 Observer와 비동기 이벤트 버스는 언제 갈라져야 할까요?**
  - 구독자 실행 시간의 합이 요청 SLA를 넘기거나, 구독자 중 네트워크 I/O가 포함된 것이 하나라도 있으면 비동기로 분리해야 합니다. 본문의 `AsyncEventBus` 예시처럼 `asyncio.gather`와 `return_exceptions=True`를 조합하면 격리와 동시성을 함께 얻습니다.

- **구독자가 예외를 던지거나 느려지면 발행자에게 무슨 일이 생길까요?**
  - 동기 Observer에서 에러 격리 없이 순회하면, 예외를 던진 구독자 이후의 모든 구독자가 실행되지 않습니다. 느린 구독자는 발행자의 응답 시간을 그대로 늘립니다. `try/except` 격리와 timeout, 또는 비동기 분리가 해법입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter 패턴](./06-adapter-pattern.md)
- **Observer 패턴 (현재 글)**
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Domain Events (Martin Fowler)](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Python weakref — Weak references (Python docs)](https://docs.python.org/3/library/weakref.html)

### 실무 확장 읽을거리

- [Publish-Subscribe Pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
- [blinker — Fast Python in-process signal/event dispatching](https://blinker.readthedocs.io/)
- [pyee — A port of Node.js EventEmitter](https://pyee.readthedocs.io/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Observer, PubSub, Events, Behavioral
