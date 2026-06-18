---
series: design-patterns-101
episode: 8
title: "바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Factory
  - DependencyInjection
  - AI코딩
  - IoC
seo_description: AI가 생성한 코드에서 의존성 주입을 적용해 테스트 가능성을 높이고 Composition Root를 구성하는 바이브코딩 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 여덟 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 서비스를 만들어 달라고 하면 `__init__`에서 DB 연결을 열고, SMTP 서버에 연결하고, 외부 SDK를 초기화하는 코드가 비즈니스 로직 한가운데 박혀 있는 경우가 많습니다. 테스트하려면 실제 인프라가 모두 떠 있어야 합니다. 의존성 주입을 알면 AI에게 처음부터 테스트 가능한 구조를 요청할 수 있습니다.

---

바이브코딩으로 빠르게 서비스를 만들다 보면 어느 순간 테스트가 막히는 경험을 하게 됩니다. 서비스 클래스를 인스턴스화하는 순간 Postgres, SMTP, RabbitMQ가 모두 떠 있어야 하고, 환경 변수를 17개 설정해야만 실행됩니다. 이 문제의 해법은 단순합니다. 만드는 일과 쓰는 일을 분리하면 됩니다.

> "Factory와 DI는 둘 다 '누가 이 객체를 만드는가?'라는 같은 질문에 답하면서, 객체 생성을 객체를 쓰는 자리 바깥으로 옮겨 테스트성과 설정 가능성을 동시에 살립니다. AI에게 테스트 가능한 코드를 요청하려면 DI 구조를 명시하세요."

## 이 글에서 다룰 문제

- AI가 만든 코드에서 협력자를 직접 생성하는 패턴을 어떻게 고칠까요?
- Constructor injection, setter injection, method injection 중 어떤 것을 기본으로 삼아야 할까요?
- Composition Root는 무엇이고 어디에 두어야 할까요?
- FastAPI에서 DI를 어떻게 활용할 수 있을까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## AI가 만든 코드에서 DI가 필요한 신호

AI가 생성한 코드에서 이런 패턴이 보이면 DI가 필요합니다.

```python
# 신호 1: __init__에서 직접 생성
class OrderService:
    def __init__(self) -> None:
        self.repo = PostgresOrderRepo(os.environ["DATABASE_URL"])
        self.mailer = SmtpMailer(os.environ["SMTP_HOST"], ...)
        self.event_bus = RabbitEventBus(os.environ["AMQP_URL"])
```

이 코드는 세 가지 문제가 있습니다. 테스트하려면 실제 인프라가 필요하고, 스테이징 환경에서 메일을 차단하려면 도메인 코드를 수정해야 하고, DB 커넥션 풀 설정이 서비스 코드에 박혀 있습니다.

## Constructor Injection으로 고치기

AI에게 "Constructor injection으로 리팩토링해줘"라고 하면:

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

`place_order`의 비즈니스 로직은 한 글자도 바뀌지 않았습니다. 바뀐 것은 `__init__`뿐입니다. 이제 테스트에서 가짜 구현체를 주입할 수 있습니다.

```python
def test_place_order_sends_email() -> None:
    fake_mailer = FakeMailer()
    service = OrderService(
        repo=InMemoryRepo(),
        mailer=fake_mailer,
        event_bus=InMemoryEventBus(),
    )
    service.place_order(Order(customer_email="test@example.com", id="1"))
    assert fake_mailer.sent_to == ["test@example.com"]
```

## Composition Root: 조립은 한 곳에서

Constructor injection을 적용하면 "그러면 누가 이 객체들을 실제로 만들어서 넘겨 주는가?"라는 질문이 옵니다. 답은 Composition Root입니다.

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
        mailer = LogMailer()
        event_bus = InMemoryEventBus()

    return OrderService(repo=repo, mailer=mailer, event_bus=event_bus)
```

Composition Root의 규칙:
1. 애플리케이션당 하나만 존재합니다.
2. 진입점(`main`, `create_app`) 바로 옆에 둡니다.
3. 환경 분기는 여기서만 합니다. 도메인 코드에 `if env ==`가 나타나면 조립 책임이 새어 나간 것입니다.

## FastAPI에서 DI 활용하기

FastAPI에서 바이브코딩을 하고 있다면 `Depends`가 이미 DI 역할을 합니다.

```python
from fastapi import FastAPI, Depends
from typing import Annotated

app = FastAPI()

def get_order_service() -> OrderService:
    return OrderService(
        repo=PostgresOrderRepo(os.environ["DATABASE_URL"]),
        mailer=SmtpMailer(...),
        event_bus=RabbitEventBus(...),
    )

@app.post("/orders")
def create_order(
    order: OrderCreate,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> dict:
    service.place_order(order.to_domain())
    return {"status": "created"}
```

테스트에서 의존성 교체:

```python
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

## Before / After: DI가 만드는 테스트 차이

**Before — 테스트에 실제 인프라가 필요한 코드:**

```python
# 이 테스트를 실행하려면 Postgres, SMTP, RabbitMQ가 모두 실행 중이어야 함
def test_place_order():
    service = OrderService()  # 내부에서 직접 연결
    service.place_order(...)
```

**After — 가짜를 주입해서 격리 테스트:**

```python
def test_place_order_sends_confirmation():
    fake_mailer = FakeMailer()
    service = OrderService(
        repo=InMemoryRepo(),
        mailer=fake_mailer,
        event_bus=InMemoryEventBus(),
    )
    service.place_order(Order(customer_email="test@ex.com", id="1"))
    assert len(fake_mailer.sent) == 1  # 메일이 한 번 발송됨
```

이 테스트는 네트워크를 타지 않고, 환경 변수를 설정하지 않고, 0.001초 안에 끝납니다.

## 조립 방식별 트레이드오프

| 방식 | 장점 | 단점 | 적합한 규모 |
| --- | --- | --- | --- |
| 수동 배선 (bootstrap.py) | IDE 추적 가능, 학습 비용 제로 | 서비스 증가 시 코드가 길어짐 | 서비스 15개 이하 |
| FastAPI Depends | 프레임워크 내장, 요청 스코프 자동 관리 | FastAPI에 종속 | FastAPI 프로젝트 |
| punq / lagom | 가볍고 타입 기반 | 커뮤니티 작음 | 중형 프로젝트 |
| dependency-injector | 선언적 DSL, 수명 주기 관리 | DSL 학습 비용, 타입 체커 궁합 | 대형 프로젝트 |

## AI 활용 팁

**DI 구조로 리팩토링 요청:**

```
"OrderService가 __init__에서 PostgresRepo와 SmtpMailer를
직접 생성하고 있어. Constructor injection으로 바꿔줘.
Protocol 인터페이스를 정의하고, 테스트용 InMemory 구현체도
만들어줘. Composition Root를 bootstrap.py에 분리해줘."
```

**FastAPI DI 설정 요청:**

```
"FastAPI OrderService를 Depends로 주입받도록 해줘.
테스트에서 dependency_overrides로 FakeOrderService를
주입할 수 있도록 구조화해줘."
```

## 운영 체크리스트

- [ ] AI가 만든 코드에서 DI가 필요한 신호를 발견할 수 있습니다.
- [ ] Constructor injection으로 리팩토링할 수 있습니다.
- [ ] Composition Root를 어디에 두어야 하는지 말할 수 있습니다.
- [ ] FastAPI의 Depends로 DI를 활용할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 DI는 생성자 시그니처를 바꾸는 것입니다. 협력자를 직접 만들지 않고 받기만 하면 테스트, 교체, 수명 주기 제어가 모두 가능해집니다. 둘째 Composition Root는 조립이 일어나는 유일한 지점입니다. 도메인 코드에 환경 분기가 있다면 Composition Root로 이동시키세요. 셋째 FastAPI의 `Depends`는 이미 DI를 구현하고 있습니다. 별도 컨테이너 없이 시작하세요.

## 처음 질문으로 돌아가기

- **AI가 만든 코드에서 협력자를 직접 생성하는 패턴을 어떻게 고칠까요?**
  - 생성자 인자로 받도록 바꾸고, 실제 생성은 Composition Root로 이동시키세요. AI에게 "Constructor injection으로 리팩토링해줘"라고 요청하면 됩니다.
- **Constructor, setter, method injection 중 어떤 것을 기본으로 삼아야 할까요?**
  - Constructor injection이 기본입니다. 객체 생성 시점에 모든 의존성이 확정되어 불변성이 보장되고, 의존성 과다 신호가 시그니처에 드러납니다.
- **Composition Root는 무엇이고 어디에 두어야 할까요?**
  - 객체 그래프를 한 번만 조립하는 지점입니다. 진입점(`main.py`, `create_app`) 바로 옆에 두고, 환경 분기는 여기서만 합니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Inversion of Control (Martin Fowler)](https://martinfowler.com/articles/injection.html)
- [Composition Root (Mark Seemann)](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

### 실무 확장 읽을거리

- [python-dependency-injector documentation](https://python-dependency-injector.ets-labs.org/)
- [punq — a simple DI container for Python](https://github.com/bobthemighty/punq)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Factory, DependencyInjection, AI코딩, IoC
