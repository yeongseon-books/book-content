---
series: design-patterns-101
episode: 2
title: "디자인 패턴 101 (2/10): 생성 패턴"
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
  - Creational
  - Factory
  - Singleton
  - Builder
seo_description: Creational 패턴으로 객체 생성 책임을 분리하고 결합도를 낮추는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (2/10): 생성 패턴

프로젝트 초기에는 객체를 만드는 코드가 눈에 띄지 않습니다. `SomeService(config)`를 호출하면 끝이니까요. 그런데 서비스가 환경별로 다른 DB 커넥션을 받아야 하고, 테스트에서는 가짜 저장소를 끼워야 하고, 생성 인자가 열 개를 넘기 시작하면, 객체를 만드는 코드 자체가 시스템에서 가장 변경이 잦은 지점이 됩니다. 저는 이 시점을 "생성 책임이 비명을 지르는 순간"이라고 부릅니다.

이 글은 Design Patterns 101 시리즈의 두 번째 글입니다. GoF가 분류한 다섯 가지 Creational 패턴 — Factory Method, Abstract Factory, Builder, Prototype, Singleton — 이 각각 어떤 문제를 풀고, 무엇을 잃게 하는지를 Python 코드와 함께 봅니다.

![Creational 패턴 다섯 가지의 책임 경계](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/02/02-01-concept-at-a-glance.ko.png)

*다섯 Creational 패턴이 각각 담당하는 생성 책임의 범위*

## 먼저 던지는 질문

- 객체 생성 코드를 분리하면 정확히 무엇이 좋아지고, 무엇이 나빠질까요?
- Factory Method와 Builder는 둘 다 "만드는 일"을 하는데, 언제 어느 쪽을 고를까요?
- Python에서 Singleton 클래스를 직접 구현해야 할 상황이 실제로 있을까요?

## 객체 생성을 왜 분리해야 하는가

저는 팀에서 코드 리뷰를 할 때 가장 자주 지적하는 패턴이 "호출자가 구체 클래스를 직접 알고 있는 코드"입니다. 예를 들어 다음과 같은 서비스 계층을 봅시다.

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

이 코드의 문제는 세 가지입니다.

1. **테스트가 어렵습니다.** `OrderService`를 테스트하려면 `env` 문자열을 조작해야 하고, 그래도 `MemoryRepository`와 `DictCache`라는 구체 클래스에 묶여 있습니다.
2. **변경이 전파됩니다.** 새 환경(예: `canary`)이 추가되면 `OrderService` 내부를 열어야 합니다. 서비스의 비즈니스 로직은 바뀐 게 없는데도요.
3. **생성 지식이 중복됩니다.** `PostgresRepository(dsn=...)`가 다른 서비스에도 복사되면, DSN 형식이 바뀔 때 모든 곳을 찾아 고쳐야 합니다.

Creational 패턴은 이 세 문제를 공통으로 다룹니다. 생성 결정을 호출자 바깥으로 밀어내서, 호출자는 "무엇을 받는가"만 알고 "어떻게 만들어지는가"는 모르게 만드는 것입니다.

## Factory Method가 풀려는 문제

Factory Method의 핵심은 간단합니다. **어떤 구체 클래스를 만들지를 호출자가 아니라 별도 함수(또는 메서드)가 결정하게 하는 것**입니다.

위의 `OrderService` 예시를 Factory Method로 정리하면 이렇게 됩니다.

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

변경된 점을 정리하면:

- `OrderService`는 `OrderRepository` Protocol만 압니다. 구체 클래스를 import하지 않습니다.
- 생성 분기는 `create_repository()` 한 곳에만 존재합니다.
- 테스트에서는 `OrderService(FakeRepository())`로 바로 주입합니다. 환경 변수를 조작할 필요가 없습니다.

Factory Method가 빛나는 순간은 **구현이 2개 이상이고, 선택 기준이 런타임에 결정될 때**입니다. 구현이 하나뿐이라면 Factory를 만들 이유가 없습니다. 직접 생성하는 편이 읽기 쉽습니다.

## Builder가 풀려는 문제와 다른 점

Factory Method는 "무엇을 만들지"를 결정합니다. Builder는 다른 문제를 풉니다. **인자가 많고 조합이 다양한 객체를 단계별로 조립하는 것**입니다.

HTTP 요청 객체를 예로 들겠습니다.

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes | None = None
    timeout_seconds: float = 30.0
    retry_count: int = 0


class HttpRequestBuilder:
    def __init__(self, method: str, url: str) -> None:
        self._method = method
        self._url = url
        self._headers: dict[str, str] = {}
        self._body: bytes | None = None
        self._timeout: float = 30.0
        self._retries: int = 0

    def header(self, key: str, value: str) -> "HttpRequestBuilder":
        self._headers[key] = value
        return self

    def body(self, data: bytes) -> "HttpRequestBuilder":
        self._body = data
        return self

    def timeout(self, seconds: float) -> "HttpRequestBuilder":
        self._timeout = seconds
        return self

    def retries(self, count: int) -> "HttpRequestBuilder":
        self._retries = count
        return self

    def build(self) -> HttpRequest:
        if not self._url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {self._url}")
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=self._headers,
            body=self._body,
            timeout_seconds=self._timeout,
            retry_count=self._retries,
        )
```

사용하는 쪽은 이렇게 됩니다.

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

Builder가 Factory Method와 다른 점은 명확합니다. Factory Method는 "어떤 타입을 만들지"를 결정하고, Builder는 "하나의 타입을 어떤 설정으로 조립할지"를 단계별로 표현합니다. 둘은 경쟁 관계가 아니라 다른 축의 문제를 풉니다.

Builder를 도입할 가치가 있는 기준은 제 경험상 이렇습니다.

- 생성 인자가 5개를 넘고, 그중 선택적 인자가 절반 이상일 때
- 조립 순서에 따라 유효성이 달라질 때 (예: `body`가 있으면 `Content-Type` 헤더가 필수)
- 같은 타입의 객체를 여러 변형으로 자주 만들 때

반대로, 인자가 3개이고 모두 필수라면 Builder는 과합니다. `dataclass`의 생성자를 그대로 쓰는 편이 낫습니다.

## Python에서 Singleton이 가장 자주 잘못 쓰이는 이유

Singleton은 개념이 단순합니다. "인스턴스를 하나만 만들고, 어디서든 그 하나를 공유한다." 문제는 이 단순함이 남용을 부른다는 사실입니다.

저는 Python 코드베이스에서 Singleton 클래스를 직접 구현한 코드를 볼 때마다 "이게 정말 필요한가"를 먼저 묻습니다. Python에서는 모듈 자체가 한 번만 import되기 때문입니다.

```python
# config.py — 모듈 수준 객체가 이미 Singleton 역할을 합니다
import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///local.db")
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
```

이 모듈을 `from app.config import DATABASE_URL`로 가져오면, 어디서 가져오든 같은 객체입니다. 별도 클래스가 필요 없습니다.

그럼에도 Singleton 클래스가 필요한 경우가 있습니다. **초기화 비용이 크고, 수명 주기를 명시적으로 관리해야 할 때**입니다. 대표적인 예가 커넥션 풀입니다.

```python
import threading


class ConnectionPool:
    _instance: "ConnectionPool | None" = None
    _lock = threading.Lock()

    def __new__(cls, max_size: int = 10) -> "ConnectionPool":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._max_size = max_size
                    cls._instance._connections: list = []
        return cls._instance

    def acquire(self) -> object:
        # 풀에서 커넥션 하나를 꺼냅니다
        ...

    def release(self, conn: object) -> None:
        # 커넥션을 풀에 반환합니다
        ...
```

이 코드가 모듈 변수보다 나은 점은 `_lock`으로 스레드 안전성을 보장하고, `max_size` 같은 초기화 파라미터를 받을 수 있다는 사실입니다.

하지만 Singleton의 비용은 분명합니다.

- **테스트 격리가 깨집니다.** 테스트 A에서 만든 인스턴스가 테스트 B에 영향을 줍니다. 매 테스트마다 `ConnectionPool._instance = None`으로 리셋해야 합니다.
- **의존성이 숨겨집니다.** 함수 시그니처에 드러나지 않고 내부에서 `ConnectionPool()`을 호출하면, 그 함수가 전역 상태에 의존한다는 사실이 보이지 않습니다.
- **수명 주기 제어가 어렵습니다.** 애플리케이션 종료 시 풀을 정리해야 하는데, "누가 마지막으로 쓰는지"를 추적하기 어렵습니다.

저는 Python에서 Singleton이 정당화되는 경우를 세 가지로 좁힙니다: (1) 커넥션 풀처럼 자원 수명 관리가 필수인 경우, (2) 멀티스레드 환경에서 초기화 경합을 막아야 하는 경우, (3) 프레임워크가 요구하는 경우(예: Django의 `AppConfig`). 그 외에는 모듈 변수나 DI 컨테이너의 스코프 설정으로 충분합니다.

## Abstract Factory를 도입할 가치가 있는 드문 경우

Abstract Factory는 **관련된 객체 묶음을 일관되게 생성**합니다. GoF 책의 대표 예시는 크로스 플랫폼 UI입니다. Mac 버튼과 Mac 텍스트박스, Windows 버튼과 Windows 텍스트박스를 섞이지 않게 만드는 것이죠.

```python
from typing import Protocol


class Button(Protocol):
    def render(self) -> str: ...

class TextInput(Protocol):
    def render(self) -> str: ...


class UIFactory(Protocol):
    def create_button(self, label: str) -> Button: ...
    def create_text_input(self, placeholder: str) -> TextInput: ...


class WebUIFactory:
    def create_button(self, label: str) -> Button:
        return HtmlButton(label)

    def create_text_input(self, placeholder: str) -> TextInput:
        return HtmlTextInput(placeholder)


class TerminalUIFactory:
    def create_button(self, label: str) -> Button:
        return TerminalButton(label)

    def create_text_input(self, placeholder: str) -> TextInput:
        return TerminalTextInput(placeholder)
```

솔직히 말하면, 저는 Python 백엔드 프로젝트에서 Abstract Factory를 직접 구현한 적이 거의 없습니다. 이 패턴이 빛나려면 두 가지 조건이 동시에 필요합니다.

1. **객체 가족이 2개 이상 존재해야 합니다.** 가족이 하나뿐이면 그냥 Factory Method로 충분합니다.
2. **가족 내 객체들이 반드시 같은 가족끼리 조합되어야 합니다.** Mac 버튼 + Windows 텍스트박스 조합이 런타임 오류를 일으키는 상황이어야 의미가 있습니다.

Python 웹 백엔드에서 이 두 조건이 동시에 성립하는 경우는 드뭅니다. 대부분은 Factory Method 하나로 해결됩니다. Abstract Factory를 도입하면 인터페이스 수가 급격히 늘어나고(Factory + 각 제품 Protocol), 코드를 따라가기가 어려워집니다. 저는 "가족이 셋 이상이고, 조합 실수가 실제 장애를 일으킨 적이 있을 때"만 도입을 권합니다.

## Prototype — 복제가 생성보다 싼 경우

Prototype은 기존 객체를 복제해서 새 객체를 만듭니다. Python에서는 `copy.deepcopy`가 이 역할을 합니다.

```python
import copy
from dataclasses import dataclass, field


@dataclass
class ReportConfig:
    title: str
    columns: list[str] = field(default_factory=list)
    filters: dict[str, str] = field(default_factory=dict)
    page_size: int = 50


# 기본 템플릿
monthly_template = ReportConfig(
    title="Monthly Sales",
    columns=["date", "product", "revenue", "region"],
    filters={"status": "completed"},
    page_size=100,
)


def create_monthly_report(month: str) -> ReportConfig:
    """템플릿을 복제한 뒤 월별 필터만 추가합니다."""
    report = copy.deepcopy(monthly_template)
    report.filters["month"] = month
    return report
```

Prototype이 유용한 상황은 제한적입니다. 객체 초기화가 무겁고(예: 외부 API 호출, 파일 파싱), 결과물의 대부분이 동일하며, 일부만 바꿔서 여러 변형을 만들어야 할 때입니다.

주의할 점은 `deepcopy`의 비용입니다. 중첩된 객체 그래프가 깊으면 복제 자체가 느려질 수 있고, 순환 참조가 있으면 예상치 못한 동작이 생깁니다. 저는 Prototype을 쓸 때 반드시 복제 대상의 크기를 측정하고, 정말 생성보다 싼지 확인합니다.

## 다섯 패턴의 비용 정리

패턴을 도입하면 반드시 무언가를 잃습니다. 저는 팀에 Creational 패턴을 제안할 때 아래 표를 함께 보여줍니다.

| 패턴 | 얻는 것 | 잃는 것 |
| --- | --- | --- |
| Factory Method | 호출자와 구체 클래스의 결합 제거 | 간접 호출 1단계 추가, "어디서 만들어지지?" 추적 비용 |
| Abstract Factory | 객체 가족 간 조합 실수 방지 | 인터페이스 수 폭증 (Factory + 제품 N개), 가족이 하나면 과설계 |
| Builder | 복잡한 조립을 읽기 쉬운 단계로 분해 | 클래스 하나 추가, 단순 객체에 쓰면 오히려 장황 |
| Prototype | 무거운 초기화를 복제로 회피 | deepcopy 비용, 가변 상태 공유 위험, 디버깅 시 원본 추적 어려움 |
| Singleton | 전역 단일 인스턴스 보장 | 테스트 격리 파괴, 숨겨진 의존성, 수명 주기 관리 부담 |

이 표에서 "잃는 것"이 현재 프로젝트에서 감당할 수 없는 비용이라면, 그 패턴은 도입하지 않는 편이 맞습니다. 패턴은 문제가 있을 때 꺼내는 도구이지, 미리 깔아 두는 인프라가 아닙니다.

## 언제 어떤 패턴을 꺼낼지 판단하는 기준

저는 코드 리뷰에서 Creational 패턴 도입 여부를 판단할 때 다음 질문을 순서대로 던집니다.

1. **구현이 2개 이상이고, 선택이 런타임에 결정되는가?** — Factory Method를 검토합니다.
2. **생성 인자가 5개를 넘고, 선택적 조합이 다양한가?** — Builder를 검토합니다.
3. **관련 객체가 반드시 같은 가족끼리 조합되어야 하고, 가족이 2개 이상인가?** — Abstract Factory를 검토합니다.
4. **초기화가 무겁고, 대부분 동일한 설정에서 일부만 바꾸는가?** — Prototype을 검토합니다.
5. **인스턴스가 반드시 하나여야 하고, 모듈 변수로는 부족한가?** — 그때만 Singleton을 검토합니다.

이 순서에서 5번까지 도달하는 경우는 드뭅니다. 대부분의 생성 문제는 1번이나 2번에서 해결됩니다.

## 처음 질문으로 돌아가기

- **객체 생성 코드를 분리하면 정확히 무엇이 좋아지고, 무엇이 나빠질까요?**
  - 좋아지는 것은 호출자가 구체 클래스를 모르게 되어 테스트 주입이 쉬워지고, 새 구현 추가 시 기존 코드 변경이 줄어든다는 사실입니다. 나빠지는 것은 간접 호출이 늘어 "이 객체가 어디서 만들어지는지" 추적하는 비용이 생긴다는 사실입니다. `OrderService` 예시에서 Factory를 도입한 뒤 테스트는 한 줄 주입으로 끝나지만, 프로덕션 코드를 처음 읽는 사람은 `create_repository()`를 찾아가야 전체 그림이 보입니다.

- **Factory Method와 Builder는 둘 다 "만드는 일"을 하는데, 언제 어느 쪽을 고를까요?**
  - Factory Method는 "어떤 타입을 만들지"를 결정하고, Builder는 "하나의 타입을 어떤 설정으로 조립할지"를 단계별로 표현합니다. DB 커넥션을 환경별로 골라야 하면 Factory Method, HTTP 요청처럼 선택적 헤더와 타임아웃과 재시도 횟수를 조합해야 하면 Builder입니다. 둘은 경쟁이 아니라 다른 축의 문제를 풉니다.

- **Python에서 Singleton 클래스를 직접 구현해야 할 상황이 실제로 있을까요?**
  - 있지만 드뭅니다. 커넥션 풀처럼 스레드 안전한 초기화와 명시적 수명 관리가 필요한 경우에 한정됩니다. 설정값 공유, 로거, 레지스트리 같은 용도는 모듈 수준 변수로 충분하고, 테스트 격리도 더 쉽습니다. Singleton 클래스를 만들기 전에 "모듈 변수로 안 되는 이유가 뭐지?"를 먼저 답할 수 있어야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- **생성 패턴 (현재 글)**
- Structural 패턴 (예정)
- Behavioral 패턴 (예정)
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Builder (refactoring.guru)](https://refactoring.guru/design-patterns/builder)

### 실무 확장 읽을거리

- [Abstract Factory (refactoring.guru)](https://refactoring.guru/design-patterns/abstract-factory)
- [Singleton — Why You Should Use It Sparingly](https://martinfowler.com/bliki/InversionOfControl.html)
- [copy — Shallow and deep copy operations (Python docs)](https://docs.python.org/3/library/copy.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Creational, Factory, Singleton, Builder
