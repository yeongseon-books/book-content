---
series: design-patterns-101
episode: 7
title: "Design Patterns 101 (7/10): The Observer Pattern"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Observer
  - PubSub
  - Events
  - Behavioral
seo_description: How the Observer pattern turns direct calls into notifications so systems can grow handlers without tightening coupling.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (7/10): The Observer Pattern

When an order is submitted, the system sends an email, posts to Slack, and reserves warehouse inventory. At first it is three lines inside `Order.submit()`. A month later SMS notifications arrive, then analytics tracking, then loyalty points. Now `Order` knows more about downstream side effects than about orders themselves. If one side effect slows down, the entire order slows down. If one side effect throws, the order fails. I have watched this happen across multiple projects.

This is the 7th post in the Design Patterns 101 series. Article 4 introduced Observer at overview level; here we go deeper into sync vs async differences, memory leaks, error isolation, and the boundary with message queues.

![Observer pattern: decoupling publisher from subscribers](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/07/07-01-concept-at-a-glance.en.png)
*A publisher propagates events without knowing who listens*
> The Observer pattern decouples 'something happened' from 'who cares' — the source publishes events without knowing its listeners, and listeners subscribe without owning the source.

## Questions to Keep in Mind

- What coupling does Observer break, and what cost does it introduce instead?
- When should a synchronous Observer give way to an asynchronous event bus?
- What happens to the publisher when a subscriber throws or runs slow?

## The Real Problem Observer Solves: Decoupling Sender from Receivers

A direct call is the simplest form of communication. `A` calls `B.do()` and that is it. Trouble starts when `A` must know `B`, `C`, `D`, and `E`. Every new receiver means opening the sender. Every removed receiver means modifying the sender.

Observer inverts this relationship. The sender (Subject) announces "something happened" without knowing who listens. Receivers (Observers) register themselves for events they care about. Extension now happens by adding subscribers, not by editing the sender.

```python
# before: Order directly calls every downstream action
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
# after: Order publishes an event
class Order:
    def __init__(self, bus: "EventBus") -> None:
        self.bus = bus

    def submit(self) -> None:
        self.save()
        self.bus.publish(OrderSubmitted(user=self.user, items=self.items))
```

`Order`'s responsibility shrinks to "save the order and publish an event." Email, Slack, warehouse, analytics, and points each exist as independent subscribers. That separation is the entirety of Observer.

## Three Ways to Express Observer in Python

### Form 1: Callback List — The Smallest Implementation

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

Fifteen lines and it works. The bus iterates a per-topic callback list and invokes each function. Simple, but three problems surface in production: no error isolation, a slow subscriber blocks the publisher, and forgetting to unsubscribe leaks memory. Each problem is addressed later.

### Form 2: Protocol-Based — Type-Safe Observer

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
        print(f"Sending email to {event.user}")

class SlackNotifier:
    def on_order_submitted(self, event: OrderSubmitted) -> None:
        print(f"Slack alert: #{event.user}")

@dataclass
class OrderService:
    observers: list[OrderObserver]

    def submit(self, user: str, items: list[str]) -> None:
        event = OrderSubmitted(user=user, items=items)
        for obs in self.observers:
            obs.on_order_submitted(event)
```

With a Protocol the IDE validates subscriber method signatures. The event is a `dataclass`, so payload structure is explicit. This form fits when event types are few and subscriber interfaces need strict governance.

### Form 3: Decorator Registration — Django Signals Style

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
    print(f"Email: {user}")

@order_submitted.connect
def notify_slack(user: str, **kwargs: Any) -> None:
    print(f"Slack: {user}")

# publish
order_submitted.send(user="alice", items=["book", "pen"])
```

Decorator registration wires subscribers at declaration time. Django's `django.dispatch.Signal` uses exactly this structure.

## Synchronous Observer vs Asynchronous Event Bus

A synchronous Observer means `publish()` returns only after every subscriber finishes. If five subscribers each take 10 ms, the publisher waits 50 ms. Whether that latency is acceptable is the dividing line between sync and async.

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

Passing `return_exceptions=True` to `asyncio.gather` prevents one subscriber's exception from aborting the others. In the synchronous version that isolation must be built by hand.

**Decision criteria:**

| Condition | Choice |
| --- | --- |
| Sum of subscriber execution times < request SLA | Synchronous Observer |
| Any subscriber involves network I/O | Async event bus |
| Subscriber failure must not affect publisher transaction | Async + separate retry |
| Event ordering is mandatory | Sync or single-consumer queue |

## Three Quiet Failure Modes of Observer

### Failure 1: A Slow Subscriber Blocks the Publisher

In a synchronous Observer, if one subscriber calls an external API and waits three seconds, the publisher also waits three seconds. The order API's response time suddenly jumps to three seconds. Tracing the cause reveals a chain: `Order.submit()` -> `EventBus.publish()` -> `AnalyticsTracker.on_order()` -> external HTTP call.

**Fix:** Move subscribers with network I/O to async, or enforce a timeout inside the synchronous Observer.

### Failure 2: One Subscriber's Exception Kills the Rest

When iterating a callback list, if the second subscriber raises `ValueError`, the third and all subsequent subscribers never execute.

```python
# publish with error isolation
import logging

logger = logging.getLogger(__name__)

def publish_safe(self, topic: str, event: Any) -> None:
    for fn in self._subs.get(topic, []):
        try:
            fn(event)
        except Exception:
            logger.exception("Observer failed: %s on topic %s", fn, topic)
```

Wrapping each call in `try/except` and logging ensures the remaining subscribers run normally. Failed subscribers get reported through a separate alerting channel.

### Failure 3: Forgetting to Unsubscribe Leaks Memory

When a subscriber object remains referenced in the event bus's callback list, it cannot be garbage-collected. In a web framework that creates a subscriber per request without unsubscribing, memory grows proportionally to request count.

## WeakRef to Prevent Memory Leaks

Python's `weakref` module provides references that do not increment the reference count. When a subscriber is no longer referenced elsewhere, it disappears automatically.

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

`WeakMethod` is a weak reference to a bound method. When the owning object is destroyed, the `cleanup` callback fires and removes the entry from the subscription list automatically. Django signals use `weakref` internally for the same reason.

**Caveat:** Lambdas and closures get collected immediately when wrapped in `weakref` because nothing else holds a strong reference. A `weakref`-based bus should receive bound methods or module-level functions.

## Where Observer Diverges from a Message Queue

Observer and message queues (RabbitMQ, Kafka, Redis Streams) both follow publish-subscribe structure. Their operational characteristics, however, are entirely different.

| Property | In-process Observer | Message Queue |
| --- | --- | --- |
| Delivery guarantee | None (lost if process dies) | Yes (disk persistence) |
| Ordering guarantee | Registration order (deterministic) | Per-partition/queue |
| Retry | Must build manually | Broker provides |
| Latency | Function-call level (ns to us) | Network round-trip (ms) |
| Deployment boundary | Single process | Cross-process/server |
| Scaling | Subscriber count = function calls | Horizontal consumer scaling |

**Decision criterion:** If decoupling within a single process is all that is needed, Observer suffices. If events must survive process death, or if subscribers live in separate services, a message queue is required.

I draw this boundary as: "Observer is a design pattern; a message queue is infrastructure." Starting with Observer and migrating to a queue later is a natural path. Defining event names and payload structures as `dataclass` objects from the start means serialization for the queue costs almost nothing later.

## Django Signals and Flask Blinker — Observer in Production Frameworks

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

Django signals hook into framework-internal events: model saves, request start/end, migrations. The `@receiver` decorator declares the subscription.

**Production note:** Django signals execute synchronously. If `on_order_saved` calls an external API, the HTTP response slows by that amount. Heavy work is typically delegated to a Celery task.

### Flask blinker

```python
from blinker import signal

order_created = signal("order-created")

@order_created.connect
def handle_email(sender, **kwargs):
    print(f"Sending email: {kwargs['user']}")

@order_created.connect
def handle_analytics(sender, **kwargs):
    print(f"Analytics event: {kwargs['order_id']}")

# publish
order_created.send(current_app._get_current_object(), user="alice", order_id=42)
```

Blinker is Flask's default signal library. It uses `weakref` internally, so subscriber objects that are destroyed get unsubscribed automatically.

### pyee — A Python Port of Node.js EventEmitter

```python
from pyee.base import EventEmitter

ee = EventEmitter()

@ee.on("order_submitted")
def on_order(event):
    print(f"Processing: {event}")

ee.emit("order_submitted", {"user": "bob", "total": 50000})
```

pyee provides the Node.js EventEmitter API (`on`, `emit`, `once`, `remove_listener`) in Python. An asyncio variant (`AsyncIOEventEmitter`) supports async subscribers natively.

## Event Design: Ordering, Replay, Idempotency

Once Observer is in place, events become the system's contracts. Designing those contracts poorly makes debugging extremely difficult later.

**Name events in past tense.** `order_submitted`, `payment_completed`, `user_registered`. Past tense signals "a fact that already happened," guaranteeing that the publisher's state is settled by the time a subscriber receives the event.

**Define event payloads as dataclasses.**

```python
from dataclasses import dataclass, field
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

`frozen=True` enforces immutability. `event_id` enables duplicate detection.

**Idempotency:** Processing the same event twice must produce the same result. Network retries, process restarts, and at-least-once delivery make duplicate events common in distributed systems. Subscribers should skip already-processed events using `event_id`.

```python
processed_events: set[UUID] = set()

def handle_order(event: OrderSubmitted) -> None:
    if event.event_id in processed_events:
        return
    processed_events.add(event.event_id)
    # actual processing
```

**Ordering:** A synchronous Observer executes in registration order. In async mode, `asyncio.gather` runs concurrently so ordering is not guaranteed. Subscribers that depend on order should remain synchronous or use a single-consumer queue.

## From Observer to Event-Driven Architecture

Observer is the starting point of event-driven architecture (EDA). The progression from an in-process callback list to a cross-process message broker to a cross-service event stream is natural.

```text
Callback list (in-process)
    | subscribers get slow
asyncio.Queue (in-process, async)
    | events must not be lost on process failure
Redis Pub/Sub (cross-process, non-persistent)
    | event replay and audit required
Kafka / RabbitMQ (cross-service, persistent)
```

When event names and payload structures remain identical at each stage, migration cost stays low. Defining `dataclass` events from the start and using only serializable fields is the habit that makes this progression possible.

## The Cost of Observer: What Gets Lost

Observer is not free. Adopting it means losing the following.

**Flow tracing becomes harder.** Direct calls can be followed with "Go to Definition" in an IDE. Through Observer, finding "who subscribes to this event?" requires grep. Once subscriber count exceeds ten, holding the full flow in working memory becomes difficult.

**Error propagation gets complex.** Direct calls let exceptions bubble straight to the caller. With Observer, where to route a subscriber's exception requires separate design. Swallowing it hides failures; re-raising it affects the publisher.

**Debugging time increases.** Tracking "the email did not go out after the order" with direct calls means looking inside `Order.submit()`. With Observer it means checking whether the event was published, whether the subscriber was registered, and whether an exception occurred inside the subscriber, in sequence.

**Order dependencies become implicit.** If subscriber A must run before subscriber B, relying on registration order produces fragile code.

I apply this threshold for deciding whether the cost is worth it: **three or more downstream actions, likely to grow further, and failure in any downstream action must not abort the publisher's core responsibility.** When those conditions are not met, direct calls are better.

## Answering the Opening Questions

- **What coupling does Observer break, and what cost does it introduce instead?**
  The publisher no longer knows the existence or count of subscribers, so adding or removing downstream actions requires no publisher modification. In return, flow tracing shifts to grep, error propagation paths need separate design, and order dependencies become implicitly hidden.

- **When should a synchronous Observer give way to an asynchronous event bus?**
  When the sum of subscriber execution times exceeds the request SLA, or when any subscriber involves network I/O, async separation is needed. Combining `asyncio.gather` with `return_exceptions=True` as shown in the `AsyncEventBus` example provides both isolation and concurrency.

- **What happens to the publisher when a subscriber throws or runs slow?**
  In a synchronous Observer without error isolation, all subscribers after the one that threw never execute. A slow subscriber inflates the publisher's response time directly. `try/except` isolation with timeout, or async separation, are the remedies.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): The Strategy Pattern](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): The Adapter Pattern](./06-adapter-pattern.md)
- **The Observer Pattern (current)**
- Factory and Dependency Injection (upcoming)
- When Patterns Do More Harm Than Good (upcoming)
- Patterns That Fit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Domain Events (Martin Fowler)](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Python weakref — Weak references (Python docs)](https://docs.python.org/3/library/weakref.html)

### Practical Extensions

- [Publish-Subscribe Pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
- [blinker — Fast Python in-process signal/event dispatching](https://blinker.readthedocs.io/)
- [pyee — A port of Node.js EventEmitter](https://pyee.readthedocs.io/)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Observer, PubSub, Events, Behavioral
