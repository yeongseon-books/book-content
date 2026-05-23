---
series: design-patterns-101
episode: 8
title: "디자인 패턴 101 (8/10): 팩토리와 의존성 주입"
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
  - Factory
  - DependencyInjection
  - Composition
  - IoC
seo_description: Factory와 의존성 주입으로 객체 조립과 사용을 분리해 테스트성과 교체 가능성을 높이는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (8/10): 팩토리와 의존성 주입

저는 코드 리뷰에서 가장 자주 남기는 코멘트가 "이 객체를 여기서 직접 만들어야 하나요?"입니다. 서비스 클래스가 자기 협력자를 직접 생성하는 코드를 보면, 테스트를 어떻게 짤지부터 걱정이 됩니다. DB 커넥션을 열고, SMTP 서버에 연결하고, 외부 SDK를 초기화하는 코드가 비즈니스 로직 한가운데 박혀 있으면, 그 서비스를 테스트하려면 실제 인프라를 전부 띄워야 합니다. 이 문제의 해법은 놀랍도록 단순합니다. 만드는 일과 쓰는 일을 분리하면 됩니다.

이 글은 Design Patterns 101 시리즈의 여덟 번째 글입니다. 2장에서 Factory Method를 "생성 결정을 서브클래스에 위임하는 패턴"으로 소개했다면, 이번 글에서는 Factory가 Dependency Injection과 만나 Composition Root라는 실무 구조로 발전하는 과정을 다룹니다.

![Factory에서 Composition Root까지의 조립 흐름](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/08/08-01-concept-at-a-glance.ko.png)

*조립 책임이 도메인 밖으로 빠져나가는 과정*

## 먼저 던지는 질문

- 객체가 자기 협력자를 직접 만들면 왜 테스트가 어려워질까요?
- Constructor injection, setter injection, method injection 중 어떤 것을 기본으로 삼아야 할까요?
- DI 컨테이너를 도입하면 정확히 무엇을 얻고 무엇을 잃을까요?

## 왜 조립과 사용을 한 곳에서 하면 안 되는가

다음 코드를 봅시다.

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

이 코드에는 세 가지 문제가 동시에 존재합니다.

첫째, 테스트할 수 없습니다. `OrderService`를 인스턴스화하는 순간 Postgres, SMTP, RabbitMQ가 모두 떠 있어야 합니다. 단위 테스트에서 `place_order`의 로직만 검증하고 싶어도 인프라 전체를 끌고 옵니다.

둘째, 교체할 수 없습니다. 스테이징에서 메일을 실제로 보내지 않으려면 `OrderService` 내부에 `if env == "staging"` 분기를 넣어야 합니다. 환경이 늘어날 때마다 도메인 코드가 오염됩니다.

셋째, 수명 주기를 제어할 수 없습니다. DB 커넥션 풀을 요청마다 새로 만들지, 앱 전체에서 하나를 공유할지를 `OrderService`가 결정하고 있습니다. 이 결정은 인프라 계층의 몫인데 도메인이 가져간 셈입니다.

해법은 `OrderService`가 협력자를 받기만 하게 바꾸는 것입니다.

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

`place_order`의 비즈니스 로직은 한 글자도 바뀌지 않았습니다. 바뀐 것은 `__init__`뿐입니다. 이 한 가지 변경으로 테스트, 교체, 수명 주기 제어가 모두 가능해집니다. 이것이 Dependency Injection의 전부입니다. 마법이 아니라 생성자 시그니처를 바꾸는 것입니다.

## Constructor Injection을 기본으로 두는 이유

DI에는 세 가지 주입 방식이 있습니다.

```python
# Constructor injection — 객체 생성 시점에 모든 의존성 확정
class OrderService:
    def __init__(self, repo: OrderRepository, mailer: Mailer) -> None:
        self.repo = repo
        self.mailer = mailer


# Setter injection — 생성 후 나중에 주입
class OrderService:
    def __init__(self) -> None:
        self.repo: OrderRepository | None = None
        self.mailer: Mailer | None = None

    def set_repo(self, repo: OrderRepository) -> None:
        self.repo = repo


# Method injection — 호출마다 의존성 전달
class OrderService:
    def place_order(self, order: Order, repo: OrderRepository) -> None:
        repo.save(order)
```

저는 Constructor injection을 기본으로 권합니다. 이유는 명확합니다.

**불변성 보장.** 객체가 생성된 뒤에는 협력자가 바뀌지 않습니다. 멀티스레드 환경에서 상태 변이를 걱정할 필요가 없습니다.

**완전성 강제.** 생성자에 필수 인자를 빠뜨리면 즉시 `TypeError`가 납니다. Setter injection은 `set_repo`를 호출하지 않아도 객체가 만들어지기 때문에, 런타임에 `AttributeError`나 `None` 참조로 터집니다.

**의존성 과다 신호.** 생성자 인자가 다섯 개를 넘기면 "이 클래스가 너무 많은 일을 하고 있다"는 설계 냄새가 시그니처에 바로 드러납니다. Setter injection은 이 신호를 숨깁니다.

Setter injection이 유용한 경우는 프레임워크가 기본 생성자를 강제하는 레거시 환경뿐입니다. Method injection은 호출마다 다른 컨텍스트(예: 현재 사용자, 요청 스코프 객체)를 넘겨야 할 때 씁니다. 둘 다 예외적 상황이지 기본값이 아닙니다.

## Composition Root — 그래프가 한 번만 그려지는 지점

Constructor injection을 적용하면 자연스럽게 다음 질문이 옵니다. "그러면 누가 이 객체들을 실제로 만들어서 넘겨 주는가?" 답은 Composition Root입니다. 애플리케이션 진입점 근처에서 객체 그래프를 한 번 조립하고, 이후 도메인 코드는 조립된 객체를 사용만 합니다.

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
        mailer = LogMailer()  # 콘솔에 출력만
        event_bus = InMemoryEventBus()

    return OrderService(repo=repo, mailer=mailer, event_bus=event_bus)
```

```python
# main.py
from bootstrap import bootstrap

def main() -> None:
    service = bootstrap()
    # FastAPI, CLI, worker 등 어떤 진입점이든 service를 넘겨 사용
    ...

if __name__ == "__main__":
    main()
```

Composition Root의 규칙은 단순합니다.

1. 애플리케이션당 하나만 존재합니다.
2. 진입점(`main`, `create_app`, `worker_entrypoint`) 바로 옆에 둡니다.
3. 환경 분기는 여기서만 합니다. 도메인 코드에 `if env ==` 가 나타나면 조립 책임이 새어 나간 것입니다.
4. 라이브러리 코드에는 Composition Root가 없습니다. 라이브러리는 조립 결정을 호출자에게 맡깁니다.

이 구조의 가장 큰 이점은 "시스템이 어떻게 조립되는지"를 한 파일에서 읽을 수 있다는 점입니다. 새로 합류한 동료가 `bootstrap.py`만 열면 어떤 구현체가 어떤 인터페이스 자리에 들어가는지 30초 안에 파악할 수 있습니다.

## Factory가 Composition Root 안에서 하는 역할

2장에서 본 Factory Method는 "어떤 구현체를 만들지"를 캡슐화합니다. Composition Root 안에서 Factory는 조건 분기를 깔끔하게 정리하는 도구로 쓰입니다.

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

Factory를 별도 함수로 빼면 Composition Root가 짧아지고, 각 Factory를 독립적으로 테스트할 수 있습니다. 하지만 Factory가 Composition Root 밖으로 나가서 도메인 코드에 주입되는 순간, 도메인이 다시 "무엇을 만들지"를 알게 됩니다. Factory를 주입하는 것은 DI의 예외적 케이스(런타임에 동적으로 객체를 만들어야 할 때)에만 허용하는 편이 좋습니다.

## FastAPI의 Depends가 DI 컨테이너 없이도 충분한 경우

FastAPI를 쓰고 있다면 이미 DI를 하고 있을 가능성이 높습니다. `Depends`가 바로 그 역할을 합니다.

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

테스트에서 의존성을 교체하는 방법도 명확합니다.

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

`Depends` 체인이 사실상 Composition Root 역할을 합니다. 프로젝트 규모가 중소형이라면 별도 DI 컨테이너 없이 이것만으로 충분합니다. 저는 FastAPI 프로젝트에서 dependency-injector를 추가로 도입한 경우를 여러 번 봤는데, 대부분 `Depends` 체인만으로 해결 가능한 문제에 불필요한 추상 계층을 얹은 결과였습니다.

## DI 컨테이너를 도입할 때 실제로 얻는 것과 잃는 것

프로젝트가 커지면 수동 배선이 부담이 됩니다. 서비스가 30개이고 각각 3-5개의 의존성을 가지면, `bootstrap.py`가 200줄을 넘기 시작합니다. 이때 DI 컨테이너가 유혹합니다.

```python
# dependency-injector 예시
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

**얻는 것:**

- 수명 주기 관리가 선언적입니다. `Singleton`, `Factory`, `Resource` 같은 provider 타입으로 "이 객체는 앱 전체에서 하나" vs "요청마다 새로" 를 명시합니다.
- 의존성 그래프를 컨테이너가 자동으로 해석합니다. A가 B를 필요로 하고 B가 C를 필요로 하면, C → B → A 순서로 알아서 만들어 줍니다.
- 설정 주입이 깔끔합니다. `config.database_url`처럼 환경 변수를 한곳에서 바인딩합니다.

**잃는 것:**

- **"이 객체는 어디서 만들어지는가?"를 IDE로 추적하기 어렵습니다.** `Ctrl+Click`으로 생성자를 따라가면 컨테이너 DSL에서 끝납니다. 실제 인스턴스화 시점은 런타임에 결정됩니다.
- **컨테이너 DSL을 팀 전체가 배워야 합니다.** `providers.Selector`, `providers.Resource`, `providers.Coroutine` 같은 개념이 추가 학습 비용입니다.
- **타입 체커와의 궁합이 나쁩니다.** dependency-injector의 provider 객체는 실제 타입과 다르기 때문에 mypy/pyright가 경고를 냅니다. `# type: ignore`가 늘어납니다.
- **순환 의존성을 숨길 수 있습니다.** 수동 배선에서는 순환이 즉시 `ImportError`로 드러나지만, 컨테이너는 lazy resolution으로 이를 우회합니다. 설계 문제가 나중에 더 큰 형태로 터집니다.

저는 다음 기준으로 판단합니다. 서비스가 15개 이하이고 의존성 깊이가 3단계 이내라면 수동 배선이 낫습니다. 그 이상이면 컨테이너를 고려하되, punq처럼 가벼운 것부터 시작합니다. dependency-injector는 강력하지만 DSL 복잡도가 높아서, 팀 전체가 동의한 뒤에만 도입하는 편이 안전합니다.

## Service Locator를 피해야 하는 이유

DI와 비슷해 보이지만 정반대인 패턴이 있습니다. Service Locator입니다.

```python
# Service Locator — 안티패턴
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
        repo = ServiceLocator.get(OrderRepository)  # 여기가 문제
        repo.save(order)
```

겉보기에는 `OrderService`가 `PostgresOrderRepo`를 직접 만들지 않으니 DI처럼 보입니다. 하지만 문제가 있습니다.

**의존성이 시그니처에 드러나지 않습니다.** `OrderService.__init__`만 보면 이 클래스가 무엇을 필요로 하는지 알 수 없습니다. `ServiceLocator.get` 호출을 본문 전체에서 찾아야 합니다.

**테스트 격리가 깨집니다.** `ServiceLocator`는 전역 상태입니다. 테스트 A에서 등록한 가짜 객체가 테스트 B에 영향을 줍니다. 테스트 순서에 따라 결과가 달라지는 flaky test의 원인이 됩니다.

**컴파일 타임 검증이 불가능합니다.** 등록하지 않은 서비스를 요청하면 런타임에야 `KeyError`가 납니다. Constructor injection이었다면 객체 생성 시점에 즉시 실패합니다.

그럼에도 Service Locator가 살아남는 이유는 레거시 코드에서 DI로 전환하는 중간 단계로 쓰이기 때문입니다. 모든 클래스의 생성자를 한 번에 바꿀 수 없을 때, 임시로 Service Locator를 두고 점진적으로 Constructor injection으로 이동하는 전략은 현실적입니다. 하지만 최종 목표는 항상 Service Locator를 제거하는 것이어야 합니다.

## Factory에서 DI로: 전형적인 리팩토링 경로

실무에서 가장 흔한 진화 경로를 정리하면 다음과 같습니다.

**1단계: 직접 생성이 흩어져 있는 상태**

```python
class NotificationService:
    def notify(self, user_id: str, message: str) -> None:
        sender = SlackSender(webhook_url=os.environ["SLACK_WEBHOOK"])
        sender.send(f"[{user_id}] {message}")
```

모든 메서드가 협력자를 직접 만듭니다. 테스트하려면 환경 변수와 실제 Slack webhook이 필요합니다.

**2단계: Factory로 생성을 한곳에 모음**

```python
def create_sender() -> MessageSender:
    env = os.environ.get("APP_ENV", "dev")
    if env == "prod":
        return SlackSender(webhook_url=os.environ["SLACK_WEBHOOK"])
    return ConsoleSender()


class NotificationService:
    def notify(self, user_id: str, message: str) -> None:
        sender = create_sender()  # 여전히 서비스가 생성 시점을 결정
        sender.send(f"[{user_id}] {message}")
```

생성 분기는 정리됐지만, `NotificationService`가 여전히 매 호출마다 sender를 만듭니다.

**3단계: Constructor injection으로 전환**

```python
class NotificationService:
    def __init__(self, sender: MessageSender) -> None:
        self.sender = sender

    def notify(self, user_id: str, message: str) -> None:
        self.sender.send(f"[{user_id}] {message}")
```

**4단계: Composition Root에서 조립**

```python
# bootstrap.py
def bootstrap() -> NotificationService:
    sender = create_sender()  # Factory는 Composition Root 안에서만 호출
    return NotificationService(sender=sender)
```

이 경로에서 Factory가 사라지는 게 아닙니다. Factory는 Composition Root 내부의 도우미로 남습니다. 달라진 것은 Factory를 호출하는 위치입니다. 도메인 안에서 호출하던 것이 진입점 경계로 이동한 것입니다.

## 테스트에서 DI가 만드는 차이

Constructor injection의 가장 직접적인 보상은 테스트입니다.

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

    service.notify("user-42", "배포 완료")

    assert sender.sent == ["[user-42] 배포 완료"]
```

이 테스트는 네트워크를 타지 않고, 환경 변수를 설정하지 않고, 0.001초 안에 끝납니다. `NotificationService`의 로직만 검증합니다. 만약 `NotificationService`가 내부에서 `SlackSender`를 직접 만들었다면, 이 테스트를 작성하려면 `unittest.mock.patch`로 모듈 레벨 import를 가로채야 합니다. patch 기반 테스트는 리팩토링에 취약합니다. 클래스를 다른 모듈로 옮기기만 해도 patch 경로가 깨집니다.

DI를 적용한 코드에서는 테스트가 프로덕션 코드와 같은 방식으로 객체를 조립합니다. 차이는 어떤 구현체를 넣느냐뿐입니다. 이 대칭성이 테스트의 신뢰도를 높입니다.

## 조립 방식별 트레이드오프 비교

| 방식 | 장점 | 단점 | 적합한 규모 |
| --- | --- | --- | --- |
| 수동 배선 (`bootstrap.py`) | IDE 추적 가능, 타입 체커 완벽 지원, 학습 비용 제로 | 서비스 수 증가 시 배선 코드가 길어짐 | 서비스 15개 이하 |
| FastAPI `Depends` | 프레임워크 내장, 요청 스코프 자동 관리, override 간편 | FastAPI에 종속, 비-웹 컨텍스트에서 재사용 불가 | FastAPI 프로젝트 전반 |
| punq / lagom | 가볍고 타입 기반 자동 해석, 학습 곡선 낮음 | 커뮤니티 작음, 고급 수명 주기 미지원 | 중형 프로젝트 |
| dependency-injector | 선언적 DSL, Singleton/Factory/Resource 수명 주기, 설정 통합 | DSL 학습 비용, 타입 체커 궁합 나쁨, 디버깅 어려움 | 대형 프로젝트 |

저는 새 프로젝트를 시작할 때 항상 수동 배선부터 시작합니다. 배선 코드가 100줄을 넘기고 "이 패턴이 반복되고 있다"는 느낌이 들 때 비로소 컨테이너를 검토합니다. 도구를 먼저 도입하고 문제를 나중에 찾는 순서는 거의 항상 과잉 설계로 끝납니다.

## 디버깅 비용이라는 숨은 대가

DI의 가장 큰 비용은 코드를 읽을 때 나타납니다. `OrderService`의 `place_order`에서 버그가 발생했을 때, "이 `self.repo`는 실제로 어떤 구현체인가?"를 알려면 Composition Root까지 거슬러 올라가야 합니다. 수동 배선이면 `bootstrap.py`를 열면 끝이지만, 컨테이너를 쓰면 provider 체인을 따라가야 합니다.

이 비용을 줄이는 실무 팁 두 가지가 있습니다.

첫째, Protocol에 구현체 이름을 주석으로 남기지 마세요. 대신 Composition Root에 짧은 docstring을 둡니다.

```python
def bootstrap() -> OrderService:
    """운영 환경 객체 그래프.

    repo: PostgresOrderRepo (connection pool shared)
    mailer: SmtpMailer (prod) / LogMailer (dev)
    event_bus: RabbitEventBus (prod) / InMemoryEventBus (dev)
    """
    ...
```

둘째, 디버거에서 `self.repo.__class__.__name__`을 watch에 추가합니다. 런타임에 어떤 구현체가 들어왔는지 즉시 확인할 수 있습니다.

## 처음 질문으로 돌아가기

- **객체가 자기 협력자를 직접 만들면 왜 테스트가 어려워질까요?**
  - `OrderService`가 `PostgresOrderRepo`를 직접 생성하면, 테스트 시점에 실제 DB가 떠 있어야 합니다. Constructor injection으로 바꾸면 `InMemoryOrderRepo`를 넣어 네트워크 없이 로직만 검증할 수 있습니다. 테스트 어려움의 본질은 "생성 결정이 도메인 안에 박혀 있어서 외부에서 교체할 수 없다"는 점입니다.

- **Constructor injection, setter injection, method injection 중 어떤 것을 기본으로 삼아야 할까요?**
  - Constructor injection입니다. 객체 생성 시점에 모든 의존성이 확정되므로 불변성이 보장되고, 필수 인자를 빠뜨리면 즉시 `TypeError`로 실패합니다. Setter injection은 불완전한 객체가 존재할 수 있는 시간 창을 만들고, method injection은 호출자에게 조립 책임을 떠넘깁니다.

- **DI 컨테이너를 도입하면 정확히 무엇을 얻고 무엇을 잃을까요?**
  - 얻는 것은 수명 주기 선언, 자동 그래프 해석, 설정 통합입니다. 잃는 것은 IDE 추적성, 타입 체커 호환성, 그리고 "이 객체가 어디서 만들어지는가"에 대한 즉각적 가시성입니다. dependency-injector 예시에서 본 것처럼, provider DSL은 강력하지만 팀 전체의 학습 비용과 디버깅 난이도를 올립니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter 패턴](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer 패턴](./07-observer-pattern.md)
- **팩토리와 의존성 주입 (현재 글)**
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Inversion of Control Containers and the Dependency Injection pattern (Martin Fowler)](https://martinfowler.com/articles/injection.html)
- [Composition Root (Mark Seemann)](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)
- [Dependency Injection Principles, Practices, and Patterns (Mark Seemann, Steven van Deursen)](https://www.manning.com/books/dependency-injection-principles-practices-and-patterns)

### 실무 확장 읽을거리

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [python-dependency-injector documentation](https://python-dependency-injector.ets-labs.org/)
- [punq — a simple DI container for Python](https://github.com/bobthemighty/punq)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Factory, DependencyInjection, Composition, IoC
