---
series: design-patterns-101
episode: 9
title: "디자인 패턴 101 (9/10): 패턴을 남용하지 않는 법"
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
  - Antipatterns
  - Simplicity
  - YAGNI
  - Refactoring
seo_description: 패턴 남용을 피하고 반복되는 변화가 생겼을 때만 추상화를 올리는 실무적 기준을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (9/10): 패턴을 남용하지 않는 법

저는 한때 모든 함수에 Strategy를 씌우고, 객체 하나 만들 때마다 Factory를 거치게 하고, 설정값 하나에도 Singleton 클래스를 만들던 시절이 있었습니다. 패턴을 배운 직후의 열병이었습니다. 코드 리뷰에서 "이거 왜 이렇게 복잡해요?"라는 질문을 받을 때마다 "확장성을 위해서요"라고 답했지만, 그 확장은 2년이 지나도 오지 않았습니다. 결국 저 혼자 만든 추상화를 저 혼자 유지보수하는 상황이 되었습니다.

이 글은 Design Patterns 101 시리즈의 아홉 번째 글입니다. 패턴을 아는 것과 패턴을 참는 것이 왜 다른 능력인지, 그리고 과하게 적용된 패턴을 어떻게 다시 단순한 코드로 되돌리는지 이야기합니다.

![패턴 과잉 적용에서 단순 코드로 되돌리는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/09/09-01-concept-at-a-glance.ko.png)

*패턴 과잉 적용의 신호를 인식하고 단순 코드로 되돌리는 판단 흐름*

## 먼저 던지는 질문

- 패턴을 적용했는데 오히려 코드가 나빠지는 순간은 어떤 신호로 알 수 있을까요?
- "나중에 필요할 것 같아서" 미리 넣은 추상화는 왜 거의 항상 짐이 될까요?
- 이미 과하게 적용된 패턴을 되돌리려면 어디서부터 시작해야 할까요?

## 패턴이 문제를 부르기 시작하는 신호

패턴 자체는 나쁘지 않습니다. 문제는 패턴이 풀어야 할 문제보다 먼저 도착할 때 생깁니다. 저는 이걸 "패턴 골든 해머"라고 부릅니다. 망치를 들면 모든 게 못으로 보이듯, Strategy를 배우면 모든 분기가 Strategy 후보로 보이고, Factory를 배우면 모든 생성이 Factory를 거쳐야 할 것 같습니다.

다음 신호가 보이면 패턴이 문제를 풀고 있는 게 아니라 문제를 만들고 있을 가능성이 큽니다.

**구현체가 하나뿐인 인터페이스가 있습니다.** Protocol을 정의했는데 그걸 구현하는 클래스가 딱 하나입니다. "나중에 두 번째가 생길 수 있으니까"라는 이유로 만들었지만, 그 "나중"은 대개 오지 않습니다.

**Factory가 분기 하나만 처리합니다.** Factory 함수를 열어 보면 `if` 하나에 `return SomeClass()`가 전부입니다. 이건 Factory가 아니라 불필요한 간접 호출입니다.

**클래스 이름에 패턴명이 두 개 이상 들어갑니다.** `StrategyFactoryAdapter`, `ObserverDecoratorProxy` 같은 이름이 보이면, 코드가 문제를 풀고 있는 게 아니라 패턴을 전시하고 있는 겁니다.

**Decorator를 세 겹 이상 쌓아야 동작합니다.** 각 Decorator가 무엇을 하는지 파악하려면 안쪽부터 바깥쪽까지 순서대로 읽어야 합니다. 디버깅할 때 스택 트레이스가 Decorator 체인으로 가득 차면 원인을 찾는 데 시간이 배로 걸립니다.

**DI 컨테이너 설정이 실제 비즈니스 로직보다 깁니다.** 의존성 주입은 좋은 원칙이지만, 컨테이너 설정 파일이 수백 줄이고 실제 서비스 코드가 수십 줄이면 비용과 이득의 비율이 뒤집힌 겁니다.

## Rule of Three — 추상화는 세 번째 케이스에서 올립니다

저는 추상화를 올리는 시점에 대해 단순한 규칙 하나를 씁니다. **같은 모양의 변화가 세 번 반복되기 전에는 추상화하지 않습니다.**

첫 번째 케이스에서는 그냥 직접 씁니다. 두 번째 케이스에서는 "비슷하네" 하고 메모만 합니다. 세 번째 케이스가 정말 같은 모양으로 나타나면, 그때 공통 구조를 뽑아냅니다. 이 시점이면 추상화의 모양이 상상이 아니라 실제 코드에서 나옵니다.

```python
# 첫 번째: 그냥 직접 씁니다
def send_welcome_email(user: User) -> None:
    subject = f"환영합니다, {user.name}님"
    body = render_template("welcome.html", user=user)
    smtp_client.send(user.email, subject, body)


# 두 번째: 비슷하지만 아직 참습니다
def send_password_reset_email(user: User, token: str) -> None:
    subject = "비밀번호 재설정"
    body = render_template("reset.html", user=user, token=token)
    smtp_client.send(user.email, subject, body)


# 세 번째: 이제 패턴이 보입니다
def send_invoice_email(user: User, invoice: Invoice) -> None:
    subject = f"청구서 #{invoice.number}"
    body = render_template("invoice.html", user=user, invoice=invoice)
    smtp_client.send(user.email, subject, body)
```

세 함수 모두 "템플릿 렌더링 → SMTP 전송"이라는 동일한 뼈대를 가집니다. 이 시점에서야 공통 구조를 뽑는 게 정당화됩니다.

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

첫 번째 함수를 쓸 때 이 구조를 미리 만들었다면 어떻게 되었을까요? `EmailSpec`의 `context` 필드가 `user`만 받으면 되는데 `dict[str, Any]`로 열어 놓아야 했을 겁니다. 두 번째 함수가 `token`을 추가로 넘겨야 하는지, 세 번째가 `invoice` 객체를 통째로 넘기는지 미리 알 수 없었을 겁니다. 세 번째 케이스를 본 뒤에야 "아, context는 그냥 dict로 열어 두면 되겠구나"라는 판단이 근거를 갖습니다.

## 단일 구현체 뒤에 숨어 있는 Protocol을 발견하는 법

가장 흔한 과잉 추상화는 "미래의 두 번째 구현체"를 위해 Protocol을 미리 정의하는 것입니다. 저는 이걸 Premature Strategy라고 부릅니다.

**Before — 구현체가 하나뿐인 Strategy:**

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

파일 세 개, 클래스 세 개, Protocol 하나. 그런데 `NotificationSender`를 구현하는 클래스는 `SlackNotificationSender` 하나뿐입니다. 이 Protocol은 누구를 위해 존재할까요? "나중에 이메일 알림도 추가할 수 있으니까"라는 상상을 위해서입니다.

**After — 함수 하나:**

```python
def send_slack_alert(webhook_url: str, user_id: str, event: str) -> None:
    requests.post(webhook_url, json={"text": f"<@{user_id}> Alert: {event}"})
```

이메일 알림이 정말 필요해지는 날이 오면, 그때 Protocol을 도입해도 됩니다. 함수 하나를 Protocol + 클래스 구조로 올리는 데 걸리는 시간은 30분입니다. 하지만 불필요한 추상화를 2년간 유지보수하는 비용은 그보다 훨씬 큽니다.

**발견 방법:** IDE에서 Protocol이나 ABC를 정의한 파일을 열고, "Find Implementations"를 실행합니다. 결과가 하나뿐이면 그 Protocol은 과잉 추상화 후보입니다.

## Factory 하나에 분기 하나 — 존재 이유가 없는 간접 호출

**Before — 분기 하나짜리 Factory:**

```python
class DatabaseConnectionFactory:
    @staticmethod
    def create(config: dict[str, str]) -> PostgresConnection:
        return PostgresConnection(
            host=config["host"],
            port=int(config["port"]),
            dbname=config["dbname"],
        )


# 사용처
conn = DatabaseConnectionFactory.create(settings)
```

이 Factory는 무엇을 추상화하고 있을까요? 아무것도 아닙니다. "나중에 MySQL도 지원할 수 있으니까"라는 상상이 전부입니다. 반환 타입조차 `PostgresConnection`으로 고정되어 있습니다.

**After — 직접 생성:**

```python
conn = PostgresConnection(
    host=settings["host"],
    port=int(settings["port"]),
    dbname=settings["dbname"],
)
```

Factory가 정당화되려면 최소한 다음 중 하나가 참이어야 합니다.

1. 반환 타입이 런타임에 결정됩니다 (config에 따라 Postgres 또는 MySQL).
2. 생성 과정이 복잡해서 호출자가 알 필요 없는 단계가 있습니다.
3. 생성된 객체를 캐싱하거나 풀링해야 합니다.

셋 다 아니라면 Factory는 `new`를 한 번 감싼 것에 불과합니다.

## Decorator 네 겹 — 읽을 수 없는 양파

Decorator 패턴은 강력하지만, 겹겹이 쌓이면 실행 순서를 머릿속에서 추적하기 어려워집니다.

**Before — 4단 Decorator 스택:**

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


# 조립
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

클래스 4개, 각각 `__init__` + `handle` 메서드. 총 80줄 이상입니다. 디버깅할 때 `handle`이 어디서 호출되는지 따라가려면 4단계를 거쳐야 합니다.

**After — 명시적 단계를 가진 함수 하나:**

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

실행 순서가 위에서 아래로 한눈에 보입니다. 각 단계가 무엇을 하는지 함수 이름으로 드러납니다. 디버거에서 breakpoint 하나면 전체 흐름을 추적할 수 있습니다.

Decorator 패턴이 정당화되는 경우는 있습니다. 미들웨어 체인처럼 조합이 런타임에 바뀌거나, 프레임워크가 Decorator 인터페이스를 강제할 때입니다. 하지만 조합이 고정되어 있고 코드를 작성하는 사람이 순서를 통제할 수 있다면, 명시적 함수가 거의 항상 더 낫습니다.

## Singleton 클래스 대신 모듈 변수

Python에서 Singleton 클래스를 만드는 건 대부분 불필요합니다. Python 모듈은 한 번만 import되고, 모듈 수준 변수는 프로세스 내에서 단일 인스턴스로 동작합니다.

**Before — Singleton 클래스:**

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


# 사용처
config = AppConfig()
```

`__new__` 오버라이드, `_instance` 클래스 변수, `_load` 메서드. 테스트에서 설정을 바꾸려면 `AppConfig._instance = None`을 호출해야 합니다.

**After — 모듈 변수:**

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

`from config import config`로 어디서든 같은 인스턴스를 씁니다. 테스트에서는 `config` 모듈 변수를 monkeypatch하면 됩니다. Singleton 패턴의 의도(전역 단일 인스턴스)를 Python 언어 기능(모듈 import 메커니즘)이 이미 제공하고 있으므로, 패턴을 별도로 구현할 이유가 없습니다.

## DI 컨테이너가 과할 때 — 수동 조립이 더 명확한 경우

의존성 주입은 좋은 원칙입니다. 하지만 DI 컨테이너(자동 배선 프레임워크)는 별개의 도구이고, 항상 필요한 건 아닙니다.

**Before — DI 컨테이너 설정:**

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

서비스가 5개인데 컨테이너 설정이 15줄입니다. 의존성 그래프를 파악하려면 이 설정 파일을 읽어야 합니다. IDE의 "Go to Definition"이 컨테이너 설정에서 멈춥니다.

**After — 수동 조립 함수:**

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

같은 의존성 그래프를 평범한 Python 코드로 표현했습니다. IDE가 모든 타입을 추적합니다. 테스트에서 특정 의존성을 교체하려면 함수 인자를 바꾸면 됩니다. 컨테이너 프레임워크의 API를 별도로 배울 필요가 없습니다.

DI 컨테이너가 정당화되는 경우도 있습니다. 서비스가 50개 이상이고, 스코프(request/session/singleton)가 복잡하게 얽히고, 런타임에 의존성을 교체해야 할 때입니다. 서비스가 10개 미만이면 수동 조립이 거의 항상 더 명확합니다.

## 이름에 패턴명이 들어가면 의심해야 하는 이유

클래스 이름에 패턴명을 넣는 것 자체가 나쁜 건 아닙니다. `PaymentStrategy`, `HttpAdapter`처럼 역할이 명확하면 괜찮습니다. 문제는 패턴명이 두 개 이상 결합되거나, 패턴명이 실제 역할을 대체할 때 생깁니다.

```python
# 나쁜 이름 — 패턴을 전시하는 이름
class UserRepositoryFactoryStrategy: ...
class NotificationObserverDecoratorProxy: ...
class ConfigSingletonBuilderAdapter: ...

# 좋은 이름 — 역할을 설명하는 이름
class UserStore: ...
class AlertRouter: ...
class Settings: ...
```

이름에 패턴명이 두 개 이상 들어가면 두 가지 가능성이 있습니다. 하나는 클래스가 너무 많은 책임을 지고 있다는 신호입니다. 다른 하나는 설계자가 패턴 이름으로 복잡성을 정당화하고 있다는 신호입니다. 어느 쪽이든 리팩토링 대상입니다.

## YAGNI가 패턴 선택에 적용되는 방식

YAGNI(You Aren't Gonna Need It)는 XP(Extreme Programming)에서 나온 원칙입니다. "지금 필요하지 않은 기능을 미리 만들지 마라." 이 원칙은 기능뿐 아니라 구조에도 동일하게 적용됩니다.

패턴은 구조입니다. Strategy는 "알고리즘을 교체할 수 있는 구조"이고, Factory는 "생성 결정을 위임하는 구조"이고, Observer는 "이벤트를 구독할 수 있는 구조"입니다. 이 구조가 지금 필요하지 않다면, 지금 만들지 않는 게 YAGNI입니다.

저는 패턴 도입을 결정할 때 다음 질문을 씁니다.

1. **지금 이 코드에서 변화가 실제로 반복되고 있는가?** "반복될 수 있다"가 아니라 "반복되었다"인지 확인합니다.
2. **패턴 없이 이 변화를 수용하면 구체적으로 어떤 고통이 생기는가?** 고통을 한 문장으로 적을 수 없다면 패턴이 아직 필요하지 않습니다.
3. **패턴을 나중에 도입하면 비용이 지금보다 크게 늘어나는가?** 대부분의 경우 나중에 도입해도 비용 차이가 크지 않습니다. 함수를 Protocol + 클래스로 올리는 건 30분이면 됩니다.

세 질문 모두에 "예"가 나올 때만 패턴을 도입합니다. 하나라도 "아니오"면 단순한 코드를 유지합니다.

## Factory와 Strategy를 도로 풀어내는 리팩토링

이미 과하게 적용된 패턴을 발견했을 때, 되돌리는 구체적인 단계입니다.

**Strategy를 함수로 되돌리기:**

```python
# Before: Protocol + 구현 클래스 1개
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
# After: 함수 하나
class OrderService:
    def total(self, items: list[Item]) -> int:
        return sum(item.price for item in items)
```

`StandardPricing.calculate`가 `base`를 그대로 반환하고 있었습니다. 구현체가 하나이고 그 하나가 아무 변환도 하지 않는다면, Protocol과 클래스를 모두 지우고 인라인합니다.

**Factory를 직접 생성으로 되돌리기:**

```python
# Before
class ServiceFactory:
    @staticmethod
    def create_user_service(db_url: str) -> UserService:
        engine = create_engine(db_url)
        repo = UserRepository(engine)
        return UserService(repo)

# 사용처
service = ServiceFactory.create_user_service(config.db_url)
```

```python
# After
engine = create_engine(config.db_url)
repo = UserRepository(engine)
service = UserService(repo)
```

Factory 클래스를 지우고 생성 코드를 사용처에 인라인합니다. 생성 코드가 여러 곳에서 반복된다면 일반 함수로 추출하면 됩니다. 클래스일 필요가 없습니다.

**되돌리기의 안전망:** 리팩토링 전에 기존 테스트가 통과하는지 확인합니다. 패턴을 제거한 뒤에도 같은 테스트가 통과하면, 그 패턴은 동작에 기여하지 않고 있었다는 증거입니다.

## 패턴을 참는 것도 실력입니다

저는 주니어 시절에 패턴을 많이 아는 게 실력이라고 생각했습니다. 시니어가 되고 나서는 패턴을 참는 게 실력이라는 걸 알게 되었습니다.

코드 리뷰에서 "여기 Strategy로 빼면 좋겠는데요"라고 말하기 전에, 저는 먼저 이렇게 물어봅니다. "이 분기가 최근 3개월간 몇 번 늘었나요?" 답이 "한 번도 안 늘었어요"라면, Strategy는 아직 필요하지 않습니다.

패턴은 문제가 반복될 때 가치를 가집니다. 문제가 한 번 나타났을 때는 직접 풀면 됩니다. 두 번 나타났을 때는 메모합니다. 세 번 나타났을 때 비로소 패턴이 정당화됩니다. 이 리듬을 지키면 과잉 설계를 피하면서도 필요한 추상화를 놓치지 않습니다.

가장 좋은 코드는 패턴이 많은 코드가 아니라, 패턴이 필요한 곳에만 있는 코드입니다.

## 처음 질문으로 돌아가기

- **패턴을 적용했는데 오히려 코드가 나빠지는 순간은 어떤 신호로 알 수 있을까요?**
  - 구현체가 하나뿐인 Protocol, 분기 하나짜리 Factory, 이름에 패턴명이 두 개 이상 결합된 클래스, 세 겹 이상의 Decorator 스택이 대표적인 신호입니다. 이런 구조가 보이면 패턴이 문제를 풀고 있는 게 아니라 복잡성을 추가하고 있을 가능성이 큽니다.

- **"나중에 필요할 것 같아서" 미리 넣은 추상화는 왜 거의 항상 짐이 될까요?**
  - 미래의 요구사항은 상상과 다른 모양으로 옵니다. 미리 만든 추상화는 실제 요구가 왔을 때 맞지 않아서 수정해야 하거나, 아예 쓰이지 않은 채 유지보수 비용만 발생시킵니다. Rule of Three에서 본 것처럼, 세 번째 케이스를 본 뒤에야 추상화의 올바른 모양이 드러납니다.

- **이미 과하게 적용된 패턴을 되돌리려면 어디서부터 시작해야 할까요?**
  - 먼저 기존 테스트가 통과하는지 확인합니다. 그다음 구현체가 하나뿐인 Protocol을 찾아 인라인하고, 분기 하나짜리 Factory를 직접 생성으로 바꿉니다. 테스트가 여전히 통과하면 그 패턴은 동작에 기여하지 않고 있었다는 증거이므로 안전하게 제거할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter 패턴](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer 패턴](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory와 의존성 주입](./08-factory-and-di.md)
- **패턴을 남용하지 않는 법 (현재 글)**
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
- [Refactoring to Patterns (Joshua Kerievsky)](https://www.industriallogic.com/xp/refactoring/)
- [Premature Abstraction (C2 wiki)](https://wiki.c2.com/?PrematureGeneralization)

### 실무 확장 읽을거리

- [Worse Is Better (Richard Gabriel)](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [Rule of Three (C2 wiki)](https://wiki.c2.com/?RuleOfThree)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Antipatterns, Simplicity, YAGNI, Refactoring
