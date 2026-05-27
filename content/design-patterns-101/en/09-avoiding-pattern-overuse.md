---
series: design-patterns-101
episode: 9
title: "Design Patterns 101 (9/10): Avoiding Pattern Overuse"
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
  - Antipatterns
  - Simplicity
  - YAGNI
  - Refactoring
seo_description: How to avoid pattern overuse by starting simple, waiting for repeated change, and letting abstractions emerge from refactoring.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (9/10): Avoiding Pattern Overuse

I once went through a phase where every function got a Strategy wrapper, every object creation passed through a Factory, and every configuration value lived inside a Singleton class. It was the fever that follows learning patterns for the first time. Whenever a code reviewer asked "why is this so complicated?" I answered "for extensibility" — but that extension never arrived, not in two years. I ended up being the sole maintainer of abstractions I had invented for nobody.

This is the 9th post in the Design Patterns 101 series. It explores why knowing patterns and restraining patterns are two different skills, and how to roll back over-applied patterns into simple code again.

![Flow from pattern overuse back to simple code](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/09/09-01-concept-at-a-glance.en.png)

*Recognizing the signals of pattern overuse and the decision flow back to simple code*

## Questions to Keep in Mind

- What signals indicate that a pattern is making code worse rather than better?
- Why does pre-emptive abstraction — "we might need it later" — almost always become a burden?
- When a pattern has already been over-applied, where do we start unwinding it?

## When Patterns Start Calling Problems

Patterns themselves are not bad. The trouble starts when a pattern arrives before the problem it is supposed to solve. I call this the "pattern golden hammer." Once Strategy is in the toolbox, every branch looks like a Strategy candidate; once Factory is learned, every constructor feels like it should be hidden behind one.

The following signals suggest a pattern is no longer solving a problem — it is creating one.

**An interface has exactly one implementation.** A Protocol was defined, but only one class implements it. The justification was "a second implementation might come later." That "later" almost never arrives.

**A Factory handles a single branch.** Open the Factory function and there is one `if` with a `return SomeClass()`. That is not a Factory — it is an unnecessary indirection.

**A class name contains two or more pattern names.** `StrategyFactoryAdapter`, `ObserverDecoratorProxy` — when names like these appear, the code is not solving a problem; it is exhibiting patterns.

**Decorators must be stacked three or more layers deep to function.** Understanding what each Decorator does requires reading from the innermost layer outward. When a stack trace fills up with Decorator chain frames, finding the root cause takes twice as long.

**DI container configuration is longer than the actual business logic.** Dependency injection is a good principle, but when the container config file runs hundreds of lines and the service code is a few dozen, the cost-benefit ratio has flipped.

## Rule of Three — Raise Abstraction at the Third Case

I use one simple rule for deciding when to abstract: **do not abstract until the same shape of change has appeared three times.**

At the first case, write it directly. At the second case, note "that looks similar" and move on. When the third case arrives in the same shape, extract the common structure. By that point the abstraction's shape comes from real code, not imagination.

```python
# First case: just write it
def send_welcome_email(user: User) -> None:
    subject = f"Welcome, {user.name}"
    body = render_template("welcome.html", user=user)
    smtp_client.send(user.email, subject, body)


# Second case: similar, but hold off
def send_password_reset_email(user: User, token: str) -> None:
    subject = "Password Reset"
    body = render_template("reset.html", user=user, token=token)
    smtp_client.send(user.email, subject, body)


# Third case: now the pattern is visible
def send_invoice_email(user: User, invoice: Invoice) -> None:
    subject = f"Invoice #{invoice.number}"
    body = render_template("invoice.html", user=user, invoice=invoice)
    smtp_client.send(user.email, subject, body)
```

All three functions share the same skeleton: render a template, send via SMTP. Only at this point is extracting the common structure justified.

```python
@dataclass
class EmailSpec:
    to: str
    subject: str
    template: str
    context: dict[str, Any]


def send_email(spec: EmailSpec) -> None:
    body = render_template(spec.template, **spec.context)
    smtp_client.send(spec.to, spec.subject, body)
```

Had I created this structure at the first function, what would have happened? The `context` field would have needed to be `dict[str, Any]` even though only `user` was required. Whether the second function would add `token`, or the third would pass an entire `invoice` object — none of that was knowable upfront. Only after seeing the third case does the decision "just make context a dict" have evidence behind it.

## Spotting a Protocol Hiding a Single Implementation

The most common over-abstraction is defining a Protocol "for the future second implementation." I call this Premature Strategy.

**Before — a Strategy with exactly one implementation:**

```python
from typing import Protocol


class NotificationSender(Protocol):
    def send(self, user_id: str, message: str) -> None: ...


class SlackNotificationSender:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, user_id: str, message: str) -> None:
        requests.post(self.webhook_url, json={"text": f"<@{user_id}> {message}"})


class AlertService:
    def __init__(self, sender: NotificationSender) -> None:
        self.sender = sender

    def alert(self, user_id: str, event: str) -> None:
        self.sender.send(user_id, f"Alert: {event}")
```

Three files, three classes, one Protocol. Yet `NotificationSender` has exactly one implementor: `SlackNotificationSender`. Who is this Protocol for? An imagined future where email notifications might also be needed.

**After — one function:**

```python
def send_slack_alert(webhook_url: str, user_id: str, event: str) -> None:
    requests.post(webhook_url, json={"text": f"<@{user_id}> Alert: {event}"})
```

If email notifications genuinely become necessary someday, introduce the Protocol then. Lifting a function into a Protocol-plus-class structure takes 30 minutes. Maintaining an unnecessary abstraction for two years costs far more.

**How to spot it:** Open any file that defines a Protocol or ABC and run "Find Implementations." If the result is exactly one, that Protocol is an over-abstraction candidate.

## Single-Branch Factory — An Indirection With No Reason to Exist

**Before — a Factory with one branch:**

```python
class DatabaseConnectionFactory:
    @staticmethod
    def create(config: dict[str, str]) -> PostgresConnection:
        return PostgresConnection(
            host=config["host"],
            port=int(config["port"]),
            dbname=config["dbname"],
        )


# call site
conn = DatabaseConnectionFactory.create(settings)
```

What is this Factory abstracting? Nothing. The entire justification is "we might support MySQL later." The return type is even hardcoded to `PostgresConnection`.

**After — direct construction:**

```python
conn = PostgresConnection(
    host=settings["host"],
    port=int(settings["port"]),
    dbname=settings["dbname"],
)
```

A Factory is justified only when at least one of the following is true:

1. The return type is determined at runtime (Postgres or MySQL depending on config).
2. The creation process is complex enough that callers should not know the steps.
3. The created object needs caching or pooling.

If none of these apply, the Factory is just wrapping `new` for no benefit.

## Four-Deep Decorator — An Unreadable Onion

The Decorator pattern is powerful, but when layers pile up, tracing execution order in your head becomes painful.

**Before — a four-layer Decorator stack:**

```python
class Handler(Protocol):
    def handle(self, request: Request) -> Response: ...


class LoggingDecorator:
    def __init__(self, inner: Handler) -> None:
        self.inner = inner

    def handle(self, request: Request) -> Response:
        log.info("start: %s", request.path)
        response = self.inner.handle(request)
        log.info("end: %s status=%d", request.path, response.status)
        return response


class AuthDecorator:
    def __init__(self, inner: Handler) -> None:
        self.inner = inner

    def handle(self, request: Request) -> Response:
        if not request.headers.get("Authorization"):
            return Response(status=401)
        return self.inner.handle(request)


class RateLimitDecorator:
    def __init__(self, inner: Handler, max_rps: int) -> None:
        self.inner = inner
        self.max_rps = max_rps

    def handle(self, request: Request) -> Response:
        if self.is_over_limit(request):
            return Response(status=429)
        return self.inner.handle(request)

    def is_over_limit(self, request: Request) -> bool: ...


class CacheDecorator:
    def __init__(self, inner: Handler, ttl: int) -> None:
        self.inner = inner
        self.ttl = ttl

    def handle(self, request: Request) -> Response:
        cached = self.cache_get(request)
        if cached:
            return cached
        response = self.inner.handle(request)
        self.cache_set(request, response)
        return response

    def cache_get(self, request: Request) -> Response | None: ...
    def cache_set(self, request: Request, response: Response) -> None: ...


# assembly
handler = CacheDecorator(
    RateLimitDecorator(
        AuthDecorator(
            LoggingDecorator(
                BusinessHandler()
            )
        ), max_rps=100
    ), ttl=60
)
```

Four classes, each with `__init__` plus `handle`. Over 80 lines total. Debugging means stepping through four layers to find where `handle` is actually called.

**After — one function with explicit steps:**

```python
def handle_request(request: Request) -> Response:
    log.info("start: %s", request.path)

    if not request.headers.get("Authorization"):
        return Response(status=401)

    if is_rate_limited(request, max_rps=100):
        return Response(status=429)

    cached = cache_get(request)
    if cached:
        log.info("end: %s status=%d (cached)", request.path, cached.status)
        return cached

    response = business_logic(request)
    cache_set(request, response, ttl=60)

    log.info("end: %s status=%d", request.path, response.status)
    return response
```

Execution order is visible top to bottom. Each step is named. A single breakpoint in the debugger traces the entire flow.

The Decorator pattern is justified when composition changes at runtime — like a middleware chain — or when a framework mandates the Decorator interface. But when the composition is fixed and the author controls the order, an explicit function is almost always better.

## Singleton Class vs. Module Variable

In Python, building a Singleton class is almost always unnecessary. A Python module is imported once, and a module-level variable acts as a single instance within the process.

**Before — Singleton class:**

```python
class AppConfig:
    _instance: "AppConfig | None" = None

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        self.debug = os.getenv("DEBUG", "false") == "true"
        self.db_url = os.getenv("DATABASE_URL", "")
        self.secret_key = os.getenv("SECRET_KEY", "")


# usage
config = AppConfig()
```

A `__new__` override, a `_instance` class variable, a `_load` method. To swap config in tests, call `AppConfig._instance = None` first.

**After — module variable:**

```python
# config.py
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    debug: bool
    db_url: str
    secret_key: str


def load_config() -> AppConfig:
    return AppConfig(
        debug=os.getenv("DEBUG", "false") == "true",
        db_url=os.getenv("DATABASE_URL", ""),
        secret_key=os.getenv("SECRET_KEY", ""),
    )


config = load_config()
```

`from config import config` gives the same instance everywhere. In tests, monkeypatch the module variable. The Singleton pattern's intent — a single global instance — is already provided by Python's module import mechanism, so there is no reason to implement the pattern separately.

## When a DI Container Is Overkill — Manual Wiring Is Clearer

Dependency injection is a good principle. But a DI container (an auto-wiring framework) is a separate tool, and it is not always needed.

**Before — DI container configuration:**

```python
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db_engine = providers.Singleton(create_engine, config.db_url)
    session_factory = providers.Singleton(sessionmaker, bind=db_engine)
    user_repo = providers.Factory(UserRepository, session_factory=session_factory)
    order_repo = providers.Factory(OrderRepository, session_factory=session_factory)
    payment_service = providers.Factory(
        PaymentService, user_repo=user_repo, order_repo=order_repo
    )
    notification_service = providers.Factory(
        NotificationService, webhook_url=config.slack_webhook
    )
    order_service = providers.Factory(
        OrderService,
        payment=payment_service,
        notification=notification_service,
        order_repo=order_repo,
    )
```

Five services, fifteen lines of container config. Understanding the dependency graph requires reading this file. IDE "Go to Definition" stops at the container config.

**After — manual wiring function:**

```python
def create_order_service(config: AppConfig) -> OrderService:
    engine = create_engine(config.db_url)
    session_factory = sessionmaker(bind=engine)

    user_repo = UserRepository(session_factory)
    order_repo = OrderRepository(session_factory)
    payment = PaymentService(user_repo, order_repo)
    notification = NotificationService(config.slack_webhook)

    return OrderService(payment, notification, order_repo)
```

The same dependency graph expressed in plain Python. The IDE tracks every type. To swap a dependency in tests, change a function argument. No need to learn a container framework's API.

A DI container is justified when services number fifty or more, scopes (request/session/singleton) interleave in complex ways, and dependencies must be swapped at runtime. Below ten services, manual wiring is almost always clearer.

## Why Pattern Names in Class Names Should Raise Suspicion

Putting a pattern name in a class name is not inherently bad. `PaymentStrategy`, `HttpAdapter` — these are fine when the role is clear. The problem arises when two or more pattern names combine, or when the pattern name replaces the actual role.

```python
# Bad names — exhibiting patterns
class UserRepositoryFactoryStrategy: ...
class NotificationObserverDecoratorProxy: ...
class ConfigSingletonBuilderAdapter: ...

# Good names — describing roles
class UserStore: ...
class AlertRouter: ...
class Settings: ...
```

When a class name contains two or more pattern names, two possibilities exist. One: the class carries too many responsibilities. Two: the designer is using pattern names to justify complexity. Either way, it is a refactoring target.

## How YAGNI Applies to Pattern Selection

YAGNI (You Aren't Gonna Need It) originated in XP (Extreme Programming). "Do not build features that are not needed right now." This principle applies equally to structure, not just features.

Patterns are structure. Strategy is "a structure that allows algorithm swapping." Factory is "a structure that delegates creation decisions." Observer is "a structure that enables event subscription." If that structure is not needed right now, not building it is YAGNI.

I use three questions when deciding whether to introduce a pattern:

1. **Is change actually repeating in this code right now?** Not "could repeat" — "has repeated."
2. **If I accommodate this change without a pattern, what specific pain results?** If the pain cannot be stated in one sentence, the pattern is not yet needed.
3. **Will introducing the pattern later cost significantly more than introducing it now?** In most cases the cost difference is small. Lifting a function into a Protocol-plus-class takes 30 minutes.

Only when all three answers are "yes" do I introduce the pattern. If any answer is "no," I keep the code simple.

## Refactoring Back From Factory and Strategy

When an over-applied pattern has already been discovered, here are the concrete steps to unwind it.

**Rolling a Strategy back to a function:**

```python
# Before: Protocol + one implementation class
class PricingStrategy(Protocol):
    def calculate(self, base: int) -> int: ...

class StandardPricing:
    def calculate(self, base: int) -> int:
        return base

class OrderService:
    def __init__(self, pricing: PricingStrategy) -> None:
        self.pricing = pricing

    def total(self, items: list[Item]) -> int:
        base = sum(item.price for item in items)
        return self.pricing.calculate(base)
```

```python
# After: one function
class OrderService:
    def total(self, items: list[Item]) -> int:
        return sum(item.price for item in items)
```

`StandardPricing.calculate` was returning `base` unchanged. When the sole implementation performs no transformation, delete both the Protocol and the class and inline.

**Rolling a Factory back to direct construction:**

```python
# Before
class ServiceFactory:
    @staticmethod
    def create_user_service(db_url: str) -> UserService:
        engine = create_engine(db_url)
        repo = UserRepository(engine)
        return UserService(repo)

# call site
service = ServiceFactory.create_user_service(config.db_url)
```

```python
# After
engine = create_engine(config.db_url)
repo = UserRepository(engine)
service = UserService(repo)
```

Delete the Factory class and inline the creation code at the call site. If the creation code repeats in multiple places, extract it into a plain function. It does not need to be a class.

**Safety net for unwinding:** Before refactoring, confirm existing tests pass. If the same tests still pass after removing the pattern, that is evidence the pattern was not contributing to behavior.

## Restraint Is a Skill Too

Early in my career I thought knowing many patterns was the mark of skill. After becoming a senior engineer I learned that restraining patterns is the real skill.

Before saying "this should be extracted into a Strategy" in a code review, I first ask: "how many times has this branch grown in the last three months?" If the answer is "not once," Strategy is not yet needed.

Patterns gain value when a problem repeats. When a problem appears once, solve it directly. When it appears twice, take a mental note. When it appears a third time, the pattern is finally justified. Maintaining this rhythm avoids over-engineering while still catching necessary abstractions.

The best code is not code with many patterns — it is code where patterns exist only where they are needed.

## Answering the Opening Questions

- **What signals indicate that a pattern is making code worse rather than better?**
  A Protocol with exactly one implementation, a Factory with a single branch, class names combining two or more pattern names, and Decorator stacks three layers deep are the classic signals. When these structures appear, the pattern is likely adding complexity rather than solving a problem.

- **Why does pre-emptive abstraction — "we might need it later" — almost always become a burden?**
  Future requirements arrive in shapes different from what was imagined. Pre-built abstractions either need modification when the real requirement lands, or sit unused while accumulating maintenance cost. As the Rule of Three showed, only after the third case does the correct shape of the abstraction reveal itself.

- **When a pattern has already been over-applied, where do we start unwinding it?**
  First confirm existing tests pass. Then find Protocols with a single implementation and inline them; replace single-branch Factories with direct construction. If tests still pass afterward, that is proof the pattern was not contributing to behavior, and it can be safely removed.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy Pattern](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter Pattern](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer Pattern](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory and Dependency Injection](./08-factory-and-di.md)
- **Avoiding Pattern Overuse (current)**
- Pythonic Patterns (upcoming)

<!-- toc:end -->

## References

### Core References

- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
- [Refactoring to Patterns (Joshua Kerievsky)](https://www.industriallogic.com/xp/refactoring/)
- [Premature Abstraction (C2 wiki)](https://wiki.c2.com/?PrematureGeneralization)

### Practical Extensions

- [Worse Is Better (Richard Gabriel)](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [Rule of Three (C2 wiki)](https://wiki.c2.com/?RuleOfThree)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Antipatterns, Simplicity, YAGNI, Refactoring
