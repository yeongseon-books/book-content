---
series: design-patterns-101
episode: 8
title: "Design Patterns 101 (8/10): Factory and Dependency Injection"
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
  - Factory
  - DependencyInjection
  - Composition
  - IoC
seo_description: How Factory and Dependency Injection separate assembly from use so teams can test, swap, and reason about object graphs more easily.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (8/10): Factory and Dependency Injection

The most frequent comment I leave in code reviews is "does this object really need to create that collaborator itself?" When a service class instantiates its own dependencies — opening DB connections, connecting to SMTP servers, initializing external SDKs — right in the middle of business logic, testing that service means spinning up the entire infrastructure. The fix is surprisingly simple: separate the act of making things from the act of using them.

This is the eighth article in the Design Patterns 101 series. In article 2, Factory Method was introduced as "delegating creation decisions to subclasses." Here, we follow Factory as it meets Dependency Injection and evolves into the Composition Root — the practical structure that production codebases actually rely on.

![Assembly flow from Factory to Composition Root](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/08/08-01-concept-at-a-glance.en.png)

*How assembly responsibility migrates out of domain code*

## Questions to Keep in Mind

- Why does testing become painful when an object creates its own collaborators?
- Among constructor injection, setter injection, and method injection, which should be the default?
- What exactly do DI containers give, and what do they cost?

## Why Mixing Assembly and Use in One Place Hurts

Consider this code:

```python
class OrderService:
    def __init__(self) -> None:
        self.repo = PostgresOrderRepo(os.environ["DATABASE_URL"])
        self.mailer = SmtpMailer(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"]))
        self.event_bus = RabbitEventBus(os.environ["AMQP_URL"])

    def place_order(self, order: Order) -> None:
        self.repo.save(order)
        self.mailer.send_confirmation(order.customer_email, order.id)
        self.event_bus.publish("order.placed", order.id)
```

Three problems coexist here.

First, it is untestable. The moment `OrderService` is instantiated, Postgres, SMTP, and RabbitMQ must all be running. Even if the goal is to verify `place_order` logic alone, the entire infrastructure gets dragged in.

Second, it is unswappable. To suppress real emails in staging, an `if env == "staging"` branch must be added inside `OrderService`. Every new environment pollutes domain code.

Third, lifetime control is impossible. Whether the DB connection pool is created per-request or shared app-wide is a decision `OrderService` is making — but that decision belongs to the infrastructure layer.

The fix is to make `OrderService` receive its collaborators instead of building them:

```python
class OrderService:
    def __init__(
        self,
        repo: OrderRepository,
        mailer: Mailer,
        event_bus: EventBus,
    ) -> None:
        self.repo = repo
        self.mailer = mailer
        self.event_bus = event_bus

    def place_order(self, order: Order) -> None:
        self.repo.save(order)
        self.mailer.send_confirmation(order.customer_email, order.id)
        self.event_bus.publish("order.placed", order.id)
```

The business logic in `place_order` did not change by a single character. Only `__init__` changed. That one modification unlocks testability, swappability, and lifetime control. This is the entirety of Dependency Injection — not magic, just a constructor signature change.

## Constructor Injection as the Default

DI comes in three injection styles:

```python
# Constructor injection — all dependencies fixed at creation time
class OrderService:
    def __init__(self, repo: OrderRepository, mailer: Mailer) -> None:
        self.repo = repo
        self.mailer = mailer


# Setter injection — injected after construction
class OrderService:
    def __init__(self) -> None:
        self.repo: OrderRepository | None = None
        self.mailer: Mailer | None = None

    def set_repo(self, repo: OrderRepository) -> None:
        self.repo = repo


# Method injection — dependency passed per call
class OrderService:
    def place_order(self, order: Order, repo: OrderRepository) -> None:
        repo.save(order)
```

Constructor injection should be the default. The reasons are clear.

**Immutability guaranteed.** Once the object is created, collaborators never change. No state-mutation worries in multithreaded environments.

**Completeness enforced.** Omit a required argument and `TypeError` fires immediately. Setter injection allows objects to exist in an incomplete state — runtime `AttributeError` or `None` dereference waits around the corner.

**Excess-dependency signal.** When constructor arguments exceed five, the design smell "this class does too much" is visible right in the signature. Setter injection hides that signal.

Setter injection is useful only in legacy environments where frameworks mandate a default constructor. Method injection applies when each call needs a different context (e.g., current user, request-scoped object). Both are exceptions, not defaults.

## Composition Root — The Graph Drawn Once

Once constructor injection is in place, the next question follows naturally: "Who actually creates these objects and passes them in?" The answer is the Composition Root. Near the application entry point, the object graph is assembled once; from that point on, domain code only uses the assembled objects.

```python
# bootstrap.py — Composition Root
import os
from order.service import OrderService
from order.repo import PostgresOrderRepo
from order.mailer import SmtpMailer, LogMailer
from order.events import RabbitEventBus, InMemoryEventBus


def bootstrap() -> OrderService:
    env = os.environ.get("APP_ENV", "dev")

    repo = PostgresOrderRepo(os.environ["DATABASE_URL"])

    if env == "prod":
        mailer = SmtpMailer(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"]))
        event_bus = RabbitEventBus(os.environ["AMQP_URL"])
    else:
        mailer = LogMailer()  # prints to console
        event_bus = InMemoryEventBus()

    return OrderService(repo=repo, mailer=mailer, event_bus=event_bus)
```

```python
# main.py
from bootstrap import bootstrap

def main() -> None:
    service = bootstrap()
    # Whether the entry point is FastAPI, CLI, or a worker — service gets passed in
    ...

if __name__ == "__main__":
    main()
```

The rules of a Composition Root are simple:

1. Exactly one per application.
2. Placed right next to the entry point (`main`, `create_app`, `worker_entrypoint`).
3. Environment branching happens here and only here. If `if env ==` appears in domain code, assembly responsibility has leaked.
4. Libraries do not have a Composition Root. Libraries leave assembly decisions to the caller.

The biggest benefit of this structure: "how the system is assembled" is readable in a single file. A new team member opens `bootstrap.py` and within 30 seconds knows which implementation fills which interface slot.

## Factory's Role Inside the Composition Root

The Factory Method from article 2 encapsulates "which implementation to create." Inside a Composition Root, Factory serves as a tool for organizing conditional branches cleanly.

```python
# factories.py
from typing import Protocol
from order.mailer import SmtpMailer, LogMailer, SesMailer


class Mailer(Protocol):
    def send_confirmation(self, to: str, order_id: str) -> None: ...


def create_mailer(env: str) -> Mailer:
    match env:
        case "prod":
            return SmtpMailer(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"]))
        case "staging":
            return SesMailer(region=os.environ["AWS_REGION"])
        case _:
            return LogMailer()
```

Extracting factories into separate functions keeps the Composition Root short and makes each factory independently testable. However, the moment a factory escapes the Composition Root and gets injected into domain code, the domain regains knowledge of "what to create." Injecting a factory should be reserved for the exceptional case where objects must be created dynamically at runtime.

## FastAPI Depends as Enough DI

If the project already uses FastAPI, DI is likely already happening. `Depends` is exactly that mechanism.

```python
from fastapi import FastAPI, Depends
from typing import Annotated

app = FastAPI()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_order_repo(db: Annotated[Session, Depends(get_db)]) -> PostgresOrderRepo:
    return PostgresOrderRepo(db)


def get_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repo)],
) -> OrderService:
    return OrderService(repo=repo, mailer=LogMailer(), event_bus=InMemoryEventBus())


@app.post("/orders")
def create_order(
    order: OrderCreate,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> dict:
    service.place_order(order.to_domain())
    return {"status": "created"}
```

Overriding dependencies in tests is straightforward:

```python
from fastapi.testclient import TestClient


def get_fake_order_service() -> OrderService:
    return OrderService(
        repo=InMemoryOrderRepo(),
        mailer=LogMailer(),
        event_bus=InMemoryEventBus(),
    )


app.dependency_overrides[get_order_service] = get_fake_order_service
client = TestClient(app)

response = client.post("/orders", json={"item": "book", "qty": 1})
assert response.status_code == 200
```

The `Depends` chain effectively acts as a Composition Root. For small-to-medium projects, this alone suffices without a separate DI container. I have seen multiple FastAPI projects add dependency-injector on top, and in most cases the result was an unnecessary abstraction layer over problems that `Depends` chains already solved.

## What DI Containers Actually Give and Cost

As projects grow, manual wiring becomes burdensome. Thirty services with 3-5 dependencies each push `bootstrap.py` past 200 lines. That is when DI containers start looking attractive.

```python
# dependency-injector example
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_session = providers.Singleton(
        SessionLocal,
        url=config.database_url,
    )

    order_repo = providers.Factory(
        PostgresOrderRepo,
        session=db_session,
    )

    mailer = providers.Selector(
        config.app_env,
        prod=providers.Factory(SmtpMailer, host=config.smtp_host, port=config.smtp_port),
        staging=providers.Factory(SesMailer, region=config.aws_region),
        dev=providers.Factory(LogMailer),
    )

    order_service = providers.Factory(
        OrderService,
        repo=order_repo,
        mailer=mailer,
        event_bus=providers.Factory(RabbitEventBus, url=config.amqp_url),
    )
```

**What is gained:**

- Lifetime management becomes declarative. Provider types like `Singleton`, `Factory`, `Resource` explicitly state "one per app" vs "one per request."
- The container resolves the dependency graph automatically. If A needs B and B needs C, it builds C then B then A without manual ordering.
- Configuration injection is clean. Environment variables bind in one place via `config.database_url`.

**What is lost:**

- **"Where is this object created?" becomes hard to trace with an IDE.** `Ctrl+Click` on a constructor leads to container DSL, not the actual instantiation site. The real creation moment is determined at runtime.
- **The entire team must learn the container DSL.** Concepts like `providers.Selector`, `providers.Resource`, `providers.Coroutine` add learning overhead.
- **Type checker compatibility suffers.** dependency-injector's provider objects differ from actual types, so mypy/pyright emit warnings. `# type: ignore` comments proliferate.
- **Circular dependencies can hide.** With manual wiring, a cycle surfaces immediately as an `ImportError`. Containers use lazy resolution to bypass this, letting design problems fester until they explode in a larger form later.

My rule of thumb: if the service count is under 15 and dependency depth stays within 3 levels, manual wiring wins. Beyond that, consider a container — but start with something lightweight like punq. dependency-injector is powerful, but its DSL complexity is high enough that adoption should require team-wide agreement.

## Why Service Locator Should Be Avoided

A pattern that looks similar to DI but works in the opposite direction: Service Locator.

```python
# Service Locator — anti-pattern
class ServiceLocator:
    _services: dict[type, object] = {}

    @classmethod
    def register(cls, interface: type, instance: object) -> None:
        cls._services[interface] = instance

    @classmethod
    def get(cls, interface: type) -> object:
        return cls._services[interface]


class OrderService:
    def place_order(self, order: Order) -> None:
        repo = ServiceLocator.get(OrderRepository)  # here is the problem
        repo.save(order)
```

On the surface, `OrderService` no longer creates `PostgresOrderRepo` directly, so it resembles DI. But problems remain.

**Dependencies are invisible in the signature.** Looking at `OrderService.__init__` alone reveals nothing about what this class needs. Every `ServiceLocator.get` call must be hunted down in the method bodies.

**Test isolation breaks.** `ServiceLocator` is global state. A fake registered in test A bleeds into test B. Test-order-dependent flaky failures follow.

**Compile-time verification is impossible.** Requesting an unregistered service yields a runtime `KeyError`. With constructor injection, failure would have been immediate at object creation time.

Service Locator survives in practice because it serves as a stepping stone when migrating legacy code toward DI. When rewriting every constructor at once is infeasible, a temporary Service Locator allows gradual migration to constructor injection. But the end goal must always be removing the Service Locator entirely.

## Factory to DI: A Typical Refactoring Path

The most common evolution in production codebases follows this trajectory:

**Stage 1: Direct creation scattered everywhere**

```python
class NotificationService:
    def notify(self, user_id: str, message: str) -> None:
        sender = SlackSender(webhook_url=os.environ["SLACK_WEBHOOK"])
        sender.send(f"[{user_id}] {message}")
```

Every method creates its own collaborator. Testing requires environment variables and a live Slack webhook.

**Stage 2: Factory consolidates creation**

```python
def create_sender() -> MessageSender:
    env = os.environ.get("APP_ENV", "dev")
    if env == "prod":
        return SlackSender(webhook_url=os.environ["SLACK_WEBHOOK"])
    return ConsoleSender()


class NotificationService:
    def notify(self, user_id: str, message: str) -> None:
        sender = create_sender()  # service still decides when to create
        sender.send(f"[{user_id}] {message}")
```

Creation branching is organized, but `NotificationService` still creates a sender on every call.

**Stage 3: Constructor injection**

```python
class NotificationService:
    def __init__(self, sender: MessageSender) -> None:
        self.sender = sender

    def notify(self, user_id: str, message: str) -> None:
        self.sender.send(f"[{user_id}] {message}")
```

**Stage 4: Assembly in the Composition Root**

```python
# bootstrap.py
def bootstrap() -> NotificationService:
    sender = create_sender()  # Factory called only inside Composition Root
    return NotificationService(sender=sender)
```

Factory does not disappear in this path. It remains as a helper inside the Composition Root. What changed is where the factory gets called — it moved from inside domain code to the entry-point boundary.

## DI in Tests

The most immediate payoff of constructor injection is testing.

```python
from dataclasses import dataclass, field


@dataclass
class FakeSender:
    sent: list[str] = field(default_factory=list)

    def send(self, message: str) -> None:
        self.sent.append(message)


def test_notify_sends_formatted_message() -> None:
    sender = FakeSender()
    service = NotificationService(sender=sender)

    service.notify("user-42", "deploy complete")

    assert sender.sent == ["[user-42] deploy complete"]
```

This test touches no network, sets no environment variables, and finishes in under a millisecond. It verifies `NotificationService` logic and nothing else. Had `NotificationService` created `SlackSender` internally, writing this test would require `unittest.mock.patch` to intercept module-level imports. Patch-based tests are fragile under refactoring — moving a class to a different module breaks the patch path.

With DI, tests assemble objects the same way production code does. The only difference is which implementation gets plugged in. That symmetry is what makes the tests trustworthy.

## Trade-offs by Assembly Approach

| Approach | Strengths | Weaknesses | Suitable Scale |
| --- | --- | --- | --- |
| Manual wiring (`bootstrap.py`) | IDE-traceable, full type-checker support, zero learning cost | Wiring code grows with service count | Up to ~15 services |
| FastAPI `Depends` | Framework-native, automatic request-scope management, easy override | Tied to FastAPI, not reusable outside web context | Any FastAPI project |
| punq / lagom | Lightweight, type-based auto-resolution, low learning curve | Small community, limited advanced lifetime support | Medium projects |
| dependency-injector | Declarative DSL, Singleton/Factory/Resource lifetimes, config integration | DSL learning cost, poor type-checker fit, harder debugging | Large projects |

I always start new projects with manual wiring. Only when the wiring code exceeds 100 lines and the feeling of "this pattern keeps repeating" sets in do I evaluate a container. Adopting the tool first and finding the problem later almost always ends in over-engineering.

## The Hidden Cost: Debugging

The largest cost of DI surfaces when reading code. A bug in `OrderService.place_order` raises the question "what is `self.repo` actually?" — answering it requires tracing back to the Composition Root. With manual wiring, opening `bootstrap.py` is enough. With a container, the provider chain must be followed.

Two practical tips reduce this cost.

First, do not annotate Protocols with implementation names in comments. Instead, place a short docstring in the Composition Root:

```python
def bootstrap() -> OrderService:
    """Production object graph.

    repo: PostgresOrderRepo (connection pool shared)
    mailer: SmtpMailer (prod) / LogMailer (dev)
    event_bus: RabbitEventBus (prod) / InMemoryEventBus (dev)
    """
    ...
```

Second, add `self.repo.__class__.__name__` to the debugger watch list. It reveals which implementation was injected at runtime, instantly.

## Answering the Opening Questions

- **Why does testing become painful when an object creates its own collaborators?**
  When `OrderService` directly creates `PostgresOrderRepo`, a live database must be running at test time. Switching to constructor injection allows plugging in `InMemoryOrderRepo` and verifying logic without a network. The root cause of test difficulty is that creation decisions are embedded inside domain code, making external substitution impossible.

- **Among constructor injection, setter injection, and method injection, which should be the default?**
  Constructor injection. All dependencies are fixed at creation time, guaranteeing immutability. Omitting a required argument fails immediately with `TypeError`. Setter injection opens a time window where incomplete objects exist. Method injection pushes assembly responsibility onto every caller.

- **What exactly do DI containers give, and what do they cost?**
  They give declarative lifetime management, automatic graph resolution, and centralized configuration binding. They cost IDE traceability, type-checker compatibility, and immediate visibility into "where is this object created." As the dependency-injector example showed, the provider DSL is powerful but raises learning overhead and debugging difficulty for the entire team.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy Pattern](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter Pattern](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer Pattern](./07-observer-pattern.md)
- **Factory and Dependency Injection (current)**
- Avoiding Pattern Overuse (upcoming)
- Patterns That Fit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Inversion of Control Containers and the Dependency Injection pattern (Martin Fowler)](https://martinfowler.com/articles/injection.html)
- [Composition Root (Mark Seemann)](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)
- [Dependency Injection Principles, Practices, and Patterns (Mark Seemann, Steven van Deursen)](https://www.manning.com/books/dependency-injection-principles-practices-and-patterns)

### Practical Extensions

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [python-dependency-injector documentation](https://python-dependency-injector.ets-labs.org/)
- [punq — a simple DI container for Python](https://github.com/bobthemighty/punq)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Factory, DependencyInjection, Composition, IoC
