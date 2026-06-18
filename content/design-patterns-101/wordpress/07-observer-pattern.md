---
series: design-patterns-101
episode: 7
title: "바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Observer
  - PubSub
  - Events
  - AI코딩
seo_description: AI가 생성한 직접 호출 코드를 Observer 패턴으로 분리해서 결합도를 낮추고 확장 지점을 만드는 바이브코딩 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 일곱 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 "주문이 완료되면 이메일을 보내고 슬랙에 알려줘"라고 하면 `Order.submit()` 안에 직접 호출 코드가 들어갑니다. 다음 달에 SMS와 포인트 적립을 추가해야 한다면? AI에게 다시 `Order.submit()`을 수정하게 됩니다. Observer 패턴을 알면 AI에게 처음부터 확장 가능한 구조를 요청할 수 있습니다.

---

주문이 제출되면 메일을 보내고, 슬랙에 알리고, 창고를 예약합니다. 처음에는 `Order.submit()` 안에 세 줄을 추가하면 끝입니다. 그런데 한 달 뒤 SMS 알림이 추가되고, 분석 이벤트 전송이 추가되고, 포인트 적립이 추가됩니다. 이제 `Order`는 주문 처리보다 후속 작업을 더 많이 알고 있습니다.

AI에게 기능을 하나씩 추가해 달라고 요청하다 보면 이 상황이 더 빨리 옵니다. Observer 패턴을 알면 AI에게 "Order는 이벤트만 발행하고, 각 후속 작업은 구독자로 분리해줘"라고 요청할 수 있습니다.

> "Observer 패턴은 '무슨 일이 일어났다'와 '누가 그것에 반응하는가'를 떼어 놓아, 송신자는 수신자를 모르고 수신자는 송신자를 소유하지 않습니다. AI에게 기능을 추가해달라고 할 때마다 발행자를 수정하지 않아도 됩니다."

## 이 글에서 다룰 문제

- AI가 만든 직접 호출 코드를 Observer 패턴으로 어떻게 분리할까요?
- 동기 Observer와 비동기 이벤트 버스는 언제 갈라져야 할까요?
- AI가 만든 Observer 코드에서 메모리 누수와 에러 격리를 어떻게 처리할까요?
- 바이브코딩에서 Observer를 잘못 적용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Observer가 풀려는 진짜 문제: 발신자와 수신자의 결합 끊기

AI에게 "주문 제출 로직 짜줘"라고 하면 이렇게 나옵니다.

```python
# AI가 만든 직접 호출 코드 (확장에 취약)
class Order:
    def submit(self):
        self.save()
        send_email(self.user)
        slack_notify(self.channel)
        warehouse.reserve(self.items)
        analytics.track("order_submitted", self.id)
        points.accrue(self.user, self.total)
```

"Observer 패턴으로 리팩토링해줘"라고 요청하면:

```python
# Observer로 분리된 코드 (확장에 열려 있음)
class Order:
    def __init__(self, bus: "EventBus") -> None:
        self.bus = bus

    def submit(self) -> None:
        self.save()
        self.bus.publish(OrderSubmitted(user=self.user, items=self.items))
```

`Order`의 책임이 "주문 저장 + 이벤트 발행"으로 줄었습니다. SMS 알림이 추가되어도 `Order`는 수정하지 않습니다. 새 구독자만 추가하면 됩니다.

## Python에서 Observer를 표현하는 세 가지 방식

### 방식 1: 콜백 리스트 (가장 단순한 구현)

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class EventBus:
    _subs: dict[str, list[Callable]] = field(default_factory=dict)

    def subscribe(self, topic: str, fn: Callable) -> None:
        self._subs.setdefault(topic, []).append(fn)

    def publish(self, topic: str, event: Any) -> None:
        for fn in self._subs.get(topic, []):
            fn(event)
```

### 방식 2: Protocol 기반 (타입 안전한 Observer)

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

@dataclass
class OrderService:
    observers: list[OrderObserver]

    def submit(self, user: str, items: list[str]) -> None:
        event = OrderSubmitted(user=user, items=items)
        for obs in self.observers:
            obs.on_order_submitted(event)
```

### 방식 3: Django signals 스타일

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Signal:
    _receivers: list[Callable] = field(default_factory=list)

    def connect(self, fn: Callable) -> Callable:
        self._receivers.append(fn)
        return fn

    def send(self, **kwargs: Any) -> None:
        for fn in self._receivers:
            fn(**kwargs)

order_submitted = Signal()

@order_submitted.connect
def notify_email(user: str, **kwargs: Any) -> None:
    print(f"메일: {user}")
```

## 에러 격리: AI가 자주 빠뜨리는 부분

AI가 만들어 준 Observer 코드에서 가장 자주 빠진 부분이 에러 격리입니다. 구독자 하나가 예외를 던지면 나머지가 실행되지 않습니다.

```python
import logging
logger = logging.getLogger(__name__)

def publish_safe(self, topic: str, event: Any) -> None:
    for fn in self._subs.get(topic, []):
        try:
            fn(event)
        except Exception:
            logger.exception(
                "Observer failed: %s on topic %s", fn, topic
            )
```

AI에게 "에러 격리 포함해서 Observer EventBus 만들어줘"라고 요청하면 이 부분을 포함한 코드를 받을 수 있습니다.

## Before / After: 동기 vs 비동기 Observer

**Before — 동기 Observer (느린 구독자가 발행자를 블로킹):**

```python
# 구독자 중 하나가 외부 API를 호출하면 전체가 기다림
def publish(self, topic: str, event: Any) -> None:
    for fn in self._subs.get(topic, []):
        fn(event)  # 이 안에서 3초짜리 HTTP 호출이 있으면...
```

**After — 비동기 Observer (구독자가 독립적으로 실행):**

```python
import asyncio

@dataclass
class AsyncEventBus:
    _subs: dict[str, list] = field(default_factory=dict)

    async def publish(self, topic: str, event: Any) -> None:
        tasks = [fn(event) for fn in self._subs.get(topic, [])]
        await asyncio.gather(*tasks, return_exceptions=True)
```

`return_exceptions=True`를 넘기면 한 구독자의 예외가 다른 구독자를 중단시키지 않습니다.

## 동기/비동기 Observer 선택 기준

| 조건 | 선택 |
| --- | --- |
| 구독자 실행 시간 합이 짧고 I/O 없음 | 동기 Observer |
| 구독자 중 하나라도 네트워크 I/O 포함 | 비동기 이벤트 버스 |
| 구독자 실패가 발행자에 영향 주면 안 됨 | 비동기 + 에러 격리 |
| 이벤트 순서 보장이 필수 | 동기 또는 단일 consumer 큐 |
| 이벤트 유실이 절대 불가 | 메시지 큐 (Kafka, RabbitMQ) |

## AI 활용 팁

**Observer 패턴 요청:**

```
"주문 제출 시 메일 발송, 슬랙 알림, 포인트 적립이 필요해.
이 후속 작업이 앞으로 더 늘어날 수 있어.
Observer 패턴으로 Order가 이벤트만 발행하고
구독자들이 각자 처리하는 구조로 만들어줘.
에러 격리 포함해서, 구독자 하나가 실패해도
나머지는 계속 실행되어야 해."
```

**비동기 Observer 요청:**

```
"구독자 중 이메일 발송이 외부 SMTP를 호출해서 느려.
동기 Observer를 비동기로 바꿔줘.
asyncio.gather로 구독자들을 동시 실행하고
각 구독자 예외는 로깅하되 다른 구독자에 영향 주지 않도록."
```

## 운영 체크리스트

- [ ] Observer 패턴의 구성 요소를 나열할 수 있습니다.
- [ ] AI가 만든 Observer 코드에 에러 격리를 추가할 수 있습니다.
- [ ] 동기와 비동기 Observer를 언제 선택할지 말할 수 있습니다.
- [ ] Observer를 도입할 가치가 있는 조건을 설명할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 Observer는 발행자가 수신자를 모르는 상태에서 이벤트를 전파합니다. 새 기능 추가가 발행자 수정 없이 가능해집니다. 둘째 에러 격리는 Observer의 필수 요소입니다. AI에게 요청할 때 명시하세요. 셋째 구독자에 I/O가 있으면 비동기 Observer를 요청하세요.

## 처음 질문으로 돌아가기

- **AI가 만든 직접 호출 코드를 Observer 패턴으로 어떻게 분리할까요?**
  - 발행자가 "이벤트 발행"만 하고, 각 후속 작업을 구독자로 분리하도록 AI에게 요청하세요. 새 후속 작업은 새 구독자를 추가하면 됩니다.
- **동기와 비동기 Observer는 언제 갈라져야 할까요?**
  - 구독자에 네트워크 I/O가 있거나 실행 시간이 긴 경우 비동기가 필요합니다. 발행자의 응답 시간이 구독자 수에 비례해 늘어나면 비동기로 전환하세요.
- **메모리 누수는 언제 생기고 어떻게 막을까요?**
  - 구독 해지를 잊으면 구독자 객체가 가비지 컬렉션 대상이 되지 않습니다. Python의 `weakref`를 사용하거나 명시적 `unsubscribe`를 호출하세요.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Domain Events (Martin Fowler)](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)

### 실무 확장 읽을거리

- [Python weakref — Weak references (Python docs)](https://docs.python.org/3/library/weakref.html)
- [blinker — Fast Python in-process signal/event dispatching](https://blinker.readthedocs.io/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Observer, PubSub, Events, AI코딩
