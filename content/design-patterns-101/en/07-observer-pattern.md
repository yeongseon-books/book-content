---
series: design-patterns-101
episode: 7
title: The Observer Pattern
status: content-ready
targets:
  tistory: true
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
seo_description: The Observer pattern notifies many subscribers when one object changes. Domain events and pub/sub thinking explained for working engineers.
last_reviewed: '2026-05-04'
---

# The Observer Pattern

> Design Patterns 101 series (7/10)

<!-- a-grade-intro:begin -->

**Core question**: When A changes, how do B, C, and D follow naturally?

> A only announces "I changed". B, C, and D *choose* to listen. That is Observer.

<!-- a-grade-intro:end -->

## What You Will Learn

- The problem Observer solves (tight coupling)
- Subject, Observer, subscribe, notify
- Synchronous vs asynchronous notification
- The link to domain events
- What to watch for when scaling to pub/sub

## Why It Matters

If A *directly calls* B, C, and D when it changes, A knows all three. Observer turns those calls into *notifications*, so A no longer needs to know who is listening.

> Observer dissolves coupling into *notification*.

## Concept at a Glance

```mermaid
flowchart LR
    Subject["Subject"] --> Notify["notify(event)"]
    Notify --> ObsA["Observer A"]
    Notify --> ObsB["Observer B"]
    Notify --> ObsC["Observer C"]
```

Subject pushes a message; Observers listen at will.

## Key Terms

- **Subject**: the publisher of changes.
- **Observer**: the listener of notifications.
- **Subscribe/Unsubscribe**: registering and removing listeners.
- **Event**: the unit of data being notified.
- **Sync/Async**: in-process call vs queued processing.

## Before/After

**Before**

```python
class Order:
    def submit(self):
        self.save()
        send_email_to(self.user)        # direct call
        slack_notify(self.user)         # direct call
        warehouse.reserve(self.items)   # direct call
```

**After**

```python
class Order:
    def __init__(self, bus): self.bus = bus
    def submit(self):
        self.save()
        self.bus.publish("order_submitted", {"user": self.user, "items": self.items})
```

`Order` does not know who is listening.

## Hands-on: Five Steps to Practice Observer

### Step 1 — A simple EventBus

```python
# 1_bus.py
class EventBus:
    def __init__(self): self._subs = {}
    def subscribe(self, topic, fn): self._subs.setdefault(topic, []).append(fn)
    def publish(self, topic, event):
        for fn in self._subs.get(topic, []):
            fn(event)
```

The smallest possible Subject.

### Step 2 — Register subscribers

```python
# 2_subscribe.py
bus = EventBus()
bus.subscribe("order_submitted", lambda e: print("EMAIL:", e["user"]))
bus.subscribe("order_submitted", lambda e: print("SLACK:", e["user"]))
```

Add new channels — the Subject stays the same.

### Step 3 — Publish from the Subject

```python
# 3_publish.py
bus.publish("order_submitted", {"user": "u1", "items": ["a", "b"]})
```

Subject only announces "something happened".

### Step 4 — Sync vs async

```python
# 4_async.py
import queue, threading
q = queue.Queue()

def worker():
    while True:
        topic, event = q.get()
        for fn in bus._subs.get(topic, []):
            fn(event)

threading.Thread(target=worker, daemon=True).start()

def async_publish(topic, event): q.put((topic, event))
```

Move to async and the Subject is no longer hostage to handler latency.

### Step 5 — Unsubscribe

```python
# 5_unsubscribe.py
def unsubscribe(bus, topic, fn):
    bus._subs.get(topic, []).remove(fn)
```

Tests and dynamic handlers must be able to detach.

## What to Notice in This Code

- Subject knows neither the *number* nor the *kind* of Observers.
- Adding a new behavior is not a *Subject change*.
- A path to async notification stays open.

## Five Common Mistakes

1. **Cyclic notification.** A→B→A loops forever.
2. **Heavy work in synchronous notification.** Subject slows down.
3. **Observer mutating the Subject directly.** Notification becomes two-way.
4. **Free-form event schemas.** Producers and subscribers drift.
5. **Swallowing handler errors.** A failed Observer disappears silently.

## How This Shows Up in Production

Django signals, Spring's `ApplicationEventPublisher`, Kafka/Redis pub-sub, GitHub Webhooks — all bigger siblings of Observer. They often appear under the name *domain event*.

## How a Senior Engineer Thinks

- Force notifications to flow one direction.
- Name events in *past tense* — `order_submitted`.
- Make schemas explicit — dataclasses, not free-form dicts.
- Report handler failures on a separate channel.
- Leave a path open for async dispatch.

## Checklist

- [ ] Does the Subject avoid knowing its subscribers?
- [ ] Are notifications one-directional?
- [ ] Do event names describe *what happened*?
- [ ] Are handler errors isolated?
- [ ] Is the structure ready to go async?

## Practice Problems

1. Split mail/Slack/warehouse-reserve actions on payment success into Observers.
2. Apply a dataclass-based event schema to your EventBus.
3. Implement `unsubscribe` and write a unit test for it.

## Wrap-up and Next Steps

Observer dissolves coupling into notification. The next post moves to object creation — Factory and Dependency Injection.

<!-- toc:begin -->
- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- [Structural Patterns](./03-structural-patterns.md)
- [Behavioral Patterns](./04-behavioral-patterns.md)
- [The Strategy Pattern](./05-strategy-pattern.md)
- [The Adapter Pattern](./06-adapter-pattern.md)
- **The Observer Pattern (current)**
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)
<!-- toc:end -->

## References

- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Domain Events (Martin Fowler)](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Publish-Subscribe Pattern (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)

Tags: Computer Science, DesignPatterns, Observer, PubSub, Events, Behavioral
