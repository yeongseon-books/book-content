---
series: design-patterns-101
episode: 2
title: "바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Creational
  - Factory
  - Singleton
  - Builder
seo_description: AI가 생성한 객체 생성 코드를 읽고 Creational 패턴으로 리팩토링하는 바이브코딩 실전 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 두 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 서비스 클래스를 만들어 달라고 하면, 종종 환경별 분기를 `__init__` 안에 가득 채운 코드를 받게 됩니다. 처음에는 잘 동작하지만, 테스트를 짜려고 하면 막히고 환경이 추가되면 도메인 코드가 오염됩니다. 이 글은 그 순간 Creational 패턴이 어떤 역할을 하는지, AI와의 대화에서 어떻게 요청해야 하는지를 다룹니다.

---

프로젝트 초기에는 객체를 만드는 코드가 눈에 띄지 않습니다. `SomeService(config)`를 호출하면 끝이니까요. 그런데 서비스가 환경별로 다른 DB 커넥션을 받아야 하고, 테스트에서는 가짜 저장소를 끼워야 하고, 생성 인자가 열 개를 넘기 시작하면, 객체를 만드는 코드 자체가 시스템에서 가장 변경이 잦은 지점이 됩니다.

AI에게 이런 서비스를 만들어 달라고 하면 보통 이렇게 나옵니다.

```python
class OrderService:
    def __init__(self, env: str) -> None:
        if env == "prod":
            self.repo = PostgresRepository(dsn="host=db port=5432 ...")
            self.cache = RedisCache(url="redis://cache:6379")
        elif env == "staging":
            self.repo = PostgresRepository(dsn="host=staging-db ...")
            self.cache = RedisCache(url="redis://staging-cache:6379")
        else:
            self.repo = MemoryRepository()
            self.cache = DictCache()
```

이 코드를 테스트하려면 `env` 문자열을 조작해야 하고, 새 환경이 추가되면 비즈니스 로직이 없는 `OrderService`를 열어야 합니다. Creational 패턴은 바로 이 문제를 풉니다.

> "Creational 패턴은 '어떻게 만들지'를 도메인 밖으로 밀어내서, 비즈니스 로직이 객체 생성의 복잡성을 모르게 만드는 도구입니다."

## 이 글에서 다룰 문제

- 객체 생성 코드를 분리하면 정확히 무엇이 좋아지고, 무엇이 나빠질까요?
- Factory Method와 Builder는 둘 다 "만드는 일"을 하는데, 언제 어느 쪽을 고를까요?
- AI가 Singleton 클래스를 만들어 줬을 때, Python에서 그게 필요한 경우는 언제일까요?
- 바이브코딩에서 생성 패턴을 잘못 활용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Factory Method: "어떤 구현체를 만들지"를 분리하기

Factory Method의 핵심은 간단합니다. **어떤 구체 클래스를 만들지를 호출자가 아니라 별도 함수가 결정하게 하는 것**입니다.

AI에게 "Factory Method 패턴으로 OrderService를 리팩토링해 줘"라고 하면 이렇게 나옵니다.

```python
from typing import Protocol
import os

class OrderRepository(Protocol):
    def save(self, order_id: str, data: dict) -> None: ...
    def find(self, order_id: str) -> dict | None: ...

def create_repository() -> OrderRepository:
    """환경 변수를 보고 적절한 저장소를 반환합니다."""
    env = os.getenv("APP_ENV", "local")
    if env == "prod":
        from app.infra.postgres import PostgresRepository
        return PostgresRepository(dsn=os.environ["DATABASE_URL"])
    return MemoryRepository()

class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    def place_order(self, order_id: str, items: list[str]) -> None:
        self.repo.save(order_id, {"items": items, "status": "placed"})
```

이제 `OrderService`는 `OrderRepository` Protocol만 압니다. 테스트에서는 `OrderService(FakeRepository())`로 바로 주입합니다.

## Builder: "복잡한 조립"을 단계별로 표현하기

Factory Method는 "무엇을 만들지"를 결정합니다. Builder는 다른 문제를 풉니다. **인자가 많고 조합이 다양한 객체를 단계별로 조립하는 것**입니다.

AI가 HTTP 요청 빌더를 만들어 줬다면:

```python
request = (
    HttpRequestBuilder("POST", "https://api.example.com/orders")
    .header("Authorization", f"Bearer {token}")
    .header("Content-Type", "application/json")
    .body(payload)
    .timeout(10.0)
    .retries(3)
    .build()
)
```

이 구조를 보면 Builder 패턴이 사용되었음을 알 수 있습니다. Builder가 들어간 코드에 새 옵션을 추가하려면 Builder 클래스에 새 메서드 하나만 추가하면 됩니다.

Builder를 도입할 가치가 있는 기준:
- 생성 인자가 5개를 넘고, 그중 선택적 인자가 절반 이상일 때
- 조립 순서에 따라 유효성이 달라질 때
- 같은 타입의 객체를 여러 변형으로 자주 만들 때

## Singleton: Python에서 주의해야 하는 패턴

AI가 설정 클래스를 Singleton으로 만들어 줬을 때 가장 주의가 필요합니다. Python에서는 모듈 자체가 한 번만 import되기 때문에, 대부분의 경우 Singleton 클래스가 불필요합니다.

```python
# AI가 만들어 준 Singleton 클래스 (대부분 과잉)
class ConnectionPool:
    _instance: "ConnectionPool | None" = None

    def __new__(cls, max_size: int = 10) -> "ConnectionPool":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._max_size = max_size
            cls._instance._connections: list = []
        return cls._instance
```

이것을 Python 방식으로 단순화하면:

```python
# config.py — 모듈 수준 객체가 이미 Singleton 역할
import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///local.db")
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
```

Singleton 클래스가 정당화되는 경우는 커넥션 풀처럼 초기화 비용이 크고 스레드 안전성이 필요한 경우뿐입니다.

## Before / After: 생성 패턴이 만드는 차이

**Before — 도메인이 구체 클래스를 직접 알고 있는 코드:**

```python
class NotificationService:
    def __init__(self):
        self.sender = SlackSender(os.environ["SLACK_WEBHOOK"])
        self.logger = PostgresLogger(os.environ["DATABASE_URL"])

    def notify(self, user: str, msg: str) -> None:
        self.sender.send(f"@{user}: {msg}")
        self.logger.log(user, msg)
```

**After — Factory + DI로 분리한 코드:**

```python
from typing import Protocol

class MessageSender(Protocol):
    def send(self, message: str) -> None: ...

class NotificationService:
    def __init__(self, sender: MessageSender) -> None:
        self.sender = sender

    def notify(self, user: str, msg: str) -> None:
        self.sender.send(f"@{user}: {msg}")

# Factory (진입점에서만 호출)
def create_sender() -> MessageSender:
    if os.environ.get("APP_ENV") == "prod":
        return SlackSender(os.environ["SLACK_WEBHOOK"])
    return ConsoleSender()
```

## 생성 패턴 선택 기준 정리

| 패턴 | 언제 쓰나 | 잃는 것 |
| --- | --- | --- |
| Factory Method | 구현이 2개 이상이고 선택이 런타임에 결정될 때 | 간접 호출 1단계 추가 |
| Abstract Factory | 관련 객체 묶음이 2개 이상이고 조합 실수가 위험할 때 | 인터페이스 수 급증 |
| Builder | 인자가 5개 이상이고 선택적 조합이 다양할 때 | 클래스 하나 추가 |
| Prototype | 초기화가 무겁고 대부분 동일한 설정에서 일부만 바꿀 때 | deepcopy 비용 |
| Singleton | 반드시 하나여야 하고 모듈 변수로는 부족할 때 | 테스트 격리 파괴 |

## AI 활용 팁

**Factory 패턴 요청:**

```
"이 서비스 클래스가 환경별로 다른 DB 커넥션을 써야 해.
Factory Method 패턴을 적용해서 도메인 코드에서 구체 클래스
의존성을 제거해줘. Python Protocol을 사용해서."
```

**Builder 패턴 요청:**

```
"HTTP 요청 객체를 만드는데 선택적 인자가 너무 많아.
Builder 패턴으로 메서드 체이닝이 가능하게 만들어줘."
```

**Singleton 대안 요청:**

```
"이 설정 클래스를 Singleton으로 만들려고 하는데,
Python에서 모듈 변수로 대신할 수 있는지 확인해줘.
가능하면 더 단순한 방식으로 리팩토링해줘."
```

## 운영 체크리스트

- [ ] Factory Method와 Builder의 차이를 설명할 수 있습니다.
- [ ] AI가 만든 Singleton 코드를 Python 모듈 변수로 대체할 수 있습니다.
- [ ] 객체 생성 코드를 Composition Root로 분리할 수 있습니다.
- [ ] 생성 패턴이 해결하는 공통 문제를 말할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 생성 패턴은 "어떻게 만드는가"를 도메인 바깥으로 밀어내는 도구입니다. 둘째 Python에서 AI가 만들어 준 Singleton 클래스는 대부분 모듈 변수로 단순화할 수 있습니다. 셋째 바이브코딩에서 AI에게 패턴 이름을 명시하면 원하는 구조를 더 정확하게 받을 수 있습니다.

## 처음 질문으로 돌아가기

- **객체 생성 코드를 분리하면 정확히 무엇이 좋아지고, 무엇이 나빠질까요?**
  - 테스트에서 구체 클래스 의존 없이 가짜를 주입할 수 있고, 환경 분기가 한 곳에만 존재합니다. 반면 간접 호출이 늘어나고 "어디서 만들어지지?"를 추적하는 비용이 생깁니다.
- **Factory Method와 Builder는 언제 갈라질까요?**
  - Factory Method는 "어떤 타입을 만들지"를 결정하고, Builder는 "하나의 타입을 어떤 설정으로 조립할지"를 단계별로 표현합니다. 둘은 다른 문제를 풉니다.
- **AI가 Singleton 클래스를 만들어 줬을 때, Python에서 그게 필요한 경우는 언제일까요?**
  - 커넥션 풀처럼 초기화 비용이 크고 스레드 안전성이 필요한 경우입니다. 설정값이나 단순 객체는 모듈 변수가 더 낫습니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- **바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Builder (refactoring.guru)](https://refactoring.guru/design-patterns/builder)

### 실무 확장 읽을거리

- [Abstract Factory (refactoring.guru)](https://refactoring.guru/design-patterns/abstract-factory)
- [copy — Shallow and deep copy operations (Python docs)](https://docs.python.org/3/library/copy.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Creational, Factory, Singleton, Builder
