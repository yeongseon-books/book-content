---
series: design-patterns-101
episode: 3
title: "디자인 패턴 101 (3/10): 구조 패턴"
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
  - Structural
  - Adapter
  - Decorator
  - Facade
seo_description: Structural 패턴으로 합성과 위임을 활용해 구조 변경 비용을 낮추는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (3/10): 구조 패턴

객체를 만드는 문제를 정리하고 나면, 그다음에 부딪히는 벽은 "이미 있는 객체들을 어떻게 엮을 것인가"입니다. 저는 실무에서 이 벽을 가장 자주 만나는 순간이 외부 SDK를 도메인에 연결할 때, 기존 객체에 로깅이나 캐시를 덧붙여야 할 때, 그리고 복잡한 하위 시스템을 호출자에게 단순하게 보여줘야 할 때라고 봤습니다. 이 세 가지 상황은 전부 "구조를 어떻게 조립하느냐"의 문제이고, GoF는 이 문제를 Structural 패턴이라는 이름으로 묶었습니다.

이 글은 Design Patterns 101 시리즈의 세 번째 글입니다. Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy 일곱 가지를 다루되, Adapter는 6장에서 깊게 파고들 예정이므로 여기서는 개요 수준으로 다룹니다.

![Structural 패턴 책임 경계](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/03/03-01-concept-at-a-glance.ko.png)

*호출자와 구현 사이에 구조 패턴이 만드는 경계*
> Structural 패턴은 클래스와 객체를 어떻게 조합하느냐에 관한 것이라, 시스템이 커져도 모든 연결을 다시 잇지 않아도 됩니다.

## 먼저 던지는 질문

- 상속 대신 합성을 쓰면 구체적으로 무엇이 달라질까요?
- Decorator와 Proxy는 둘 다 "감싸는" 패턴인데, 언제 어느 쪽을 골라야 할까요?
- Structural 패턴을 도입했을 때 잃는 것은 무엇일까요?

## 객체를 묶을 때 생기는 두 가지 문제

구조를 설계할 때 반복해서 나타나는 문제는 크게 두 가지입니다.

**첫째, 인터페이스 불일치.** 외부 라이브러리가 제공하는 메서드 시그니처와 우리 도메인이 기대하는 시그니처가 다릅니다. 이걸 호출 지점마다 변환하면 변환 로직이 코드 전체에 흩어집니다.

**둘째, 책임 누적.** 하나의 객체에 로깅, 캐시, 접근 제어, 지연 로딩 같은 횡단 관심사가 쌓이면 클래스가 비대해집니다. 상속으로 풀면 조합 폭발이 일어나고, 조건문으로 풀면 분기가 끝없이 늘어납니다.

Structural 패턴은 이 두 문제를 **합성(composition)** 으로 풉니다. 객체를 감싸거나, 변환하거나, 트리로 엮어서 호출자가 보는 인터페이스는 안정적으로 유지하면서 내부 구현만 교체할 수 있게 만듭니다.

## Adapter와 Facade는 같은 문제를 다른 거리에서 푼다

Adapter는 **하나의 인터페이스**를 다른 인터페이스로 번역합니다. Facade는 **여러 하위 시스템**을 하나의 단순한 진입점 뒤에 숨깁니다. 둘 다 "호출자가 알아야 할 것을 줄인다"는 목적은 같지만, 작동하는 거리가 다릅니다.

### Adapter: 계약 번역

레거시 결제 SDK가 `execute_payment(merchant_id, cents, currency_code)`를 요구하는데, 우리 도메인은 `PaymentGateway.charge(order: Order)` 형태를 기대한다고 해 봅시다.

```python
from typing import Protocol
from dataclasses import dataclass


@dataclass
class Order:
    merchant: str
    amount_cents: int
    currency: str


class PaymentGateway(Protocol):
    def charge(self, order: Order) -> str: ...


class LegacySDKAdapter:
    """레거시 SDK를 도메인 인터페이스에 맞추는 얇은 번역 층."""

    def __init__(self, sdk) -> None:
        self._sdk = sdk

    def charge(self, order: Order) -> str:
        return self._sdk.execute_payment(
            order.merchant, order.amount_cents, order.currency
        )
```

Adapter 안에는 비즈니스 로직이 없습니다. 있는 것은 시그니처 변환뿐입니다. 비즈니스 로직이 섞이는 순간 Adapter는 "번역기"가 아니라 "정책 결정자"가 되어 버리고, 테스트와 교체가 어려워집니다. 6장에서 이 경계를 더 깊이 다룹니다.

### Facade: 하위 시스템 단순화

주문 처리에 재고 확인, 결제, 배송 예약, 알림 발송이 필요하다면, 호출자가 네 시스템을 직접 조율하는 것은 부담입니다.

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier) -> None:
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notifier = notifier

    def place_order(self, user_id: str, item_id: str, amount: int) -> str:
        self._inventory.reserve(item_id)
        tx_id = self._payment.charge(user_id, amount)
        tracking = self._shipping.schedule(user_id, item_id)
        self._notifier.send(user_id, f"주문 완료: {tracking}")
        return tx_id
```

Facade의 함정은 "편하니까 여기에 기능을 더 넣자"는 유혹입니다. Facade가 새로운 비즈니스 규칙을 품기 시작하면 만능 객체(God Object)가 됩니다. Facade는 **조율만** 하고, 판단은 각 하위 시스템에 남겨야 합니다.

## Decorator가 Python에서 자연스러운 이유

Python에는 `@decorator` 문법이 언어에 내장되어 있습니다. 그래서 GoF의 Decorator 패턴이 다른 언어보다 훨씬 자연스럽게 녹아듭니다. 핵심 아이디어는 동일합니다. **같은 인터페이스를 유지한 채 객체를 감싸서 책임을 추가한다.**

아래는 HTTP 클라이언트에 로깅, 재시도, 타이밍을 체이닝하는 예시입니다.

```python
from typing import Protocol
import time


class HttpClient(Protocol):
    def get(self, url: str) -> bytes: ...


class LoggingClient:
    def __init__(self, inner: HttpClient) -> None:
        self._inner = inner

    def get(self, url: str) -> bytes:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result


class RetryClient:
    def __init__(self, inner: HttpClient, max_retries: int = 3) -> None:
        self._inner = inner
        self._max_retries = max_retries

    def get(self, url: str) -> bytes:
        for attempt in range(self._max_retries):
            try:
                return self._inner.get(url)
            except OSError:
                if attempt == self._max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")


class TimingClient:
    def __init__(self, inner: HttpClient) -> None:
        self._inner = inner

    def get(self, url: str) -> bytes:
        start = time.perf_counter()
        result = self._inner.get(url)
        elapsed = time.perf_counter() - start
        print(f"[TIME] {url} → {elapsed:.3f}s")
        return result
```

조립은 한 줄입니다.

```python
client = TimingClient(RetryClient(LoggingClient(RealHttpClient())))
```

순서를 바꾸면 동작이 달라집니다. `TimingClient`를 가장 바깥에 두면 재시도 시간까지 포함한 총 시간을 측정하고, `RetryClient` 안쪽에 두면 개별 시도 시간만 측정합니다. 이 순서 제어가 Decorator 체이닝의 핵심 장점이자, 동시에 디버깅을 어렵게 만드는 원인이기도 합니다.

저는 Decorator 체인을 3단계 이내로 유지하는 것을 권합니다. 4단계 이상이 되면 스택 트레이스를 읽기가 급격히 어려워집니다.

## Proxy를 도입할 때 따져야 할 단 한 가지

Proxy는 실제 객체와 **동일한 인터페이스**를 노출하면서, 그 앞에서 접근 제어, 캐시, 지연 로딩 같은 부가 책임을 수행합니다. Decorator와 비슷해 보이지만 의도가 다릅니다. Decorator는 "기능을 추가"하고, Proxy는 "접근을 제어"합니다.

Proxy를 도입할 때 따져야 할 단 한 가지는 **투명성**입니다. 호출자가 Proxy를 쓰고 있다는 사실을 의식하지 않아야 합니다. 시그니처가 달라지거나, 예외 타입이 바뀌거나, 반환값의 의미가 미묘하게 달라지면 Proxy가 아니라 별도 서비스입니다.

```python
from typing import Protocol


class UserRepository(Protocol):
    def find(self, user_id: str) -> dict: ...


class CachedUserRepository:
    """지연 로딩 + 캐시 Proxy."""

    def __init__(self, real: UserRepository) -> None:
        self._real = real
        self._cache: dict[str, dict] = {}

    def find(self, user_id: str) -> dict:
        if user_id not in self._cache:
            self._cache[user_id] = self._real.find(user_id)
        return self._cache[user_id]
```

이 Proxy는 호출자 입장에서 `UserRepository`와 완전히 동일하게 동작합니다. 캐시 무효화 정책만 추가하면 운영에서 바로 쓸 수 있습니다.

## Composite가 트리 구조에서만 빛나는 이유

Composite는 단일 객체와 객체 집합을 **같은 인터페이스**로 다루게 해 줍니다. 파일 시스템의 파일/폴더, UI의 위젯/컨테이너, 메뉴의 항목/하위 메뉴가 전형적인 예입니다.

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class MenuItem:
    name: str
    price: int

    def total(self) -> int:
        return self.price

    def display(self, indent: int = 0) -> str:
        return f"{'  ' * indent}{self.name}: {self.price}원"


@dataclass
class Menu:
    name: str
    children: list[MenuItem | Menu] = field(default_factory=list)

    def total(self) -> int:
        return sum(child.total() for child in self.children)

    def display(self, indent: int = 0) -> str:
        lines = [f"{'  ' * indent}[{self.name}]"]
        for child in self.children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)
```

```python
lunch = Menu("점심 세트", [
    MenuItem("된장찌개", 8000),
    MenuItem("공기밥", 1000),
    Menu("사이드", [
        MenuItem("계란말이", 3000),
        MenuItem("김치", 0),
    ]),
])

print(lunch.display())
print(f"합계: {lunch.total()}원")
```

출력:

```text
[점심 세트]
  된장찌개: 8000원
  공기밥: 1000원
  [사이드]
    계란말이: 3000원
    김치: 0원
합계: 12000원
```

Composite가 빛나는 조건은 명확합니다. **데이터가 실제로 트리 형태일 때.** 데이터가 그래프이거나 플랫 리스트인데 Composite를 억지로 적용하면, 부모-자식 관계를 인위적으로 만들어야 하고 모델이 부자연스러워집니다.

## Bridge와 Flyweight: 자주 쓰이지 않지만 알아야 할 때

### Bridge

Bridge는 추상화와 구현을 독립적으로 확장할 수 있게 분리합니다. "도형(Shape)"과 "렌더러(Renderer)"가 각각 독립적으로 늘어나야 할 때, 상속으로 풀면 `CircleSVGRenderer`, `CircleCanvasRenderer`, `RectSVGRenderer`... 조합이 폭발합니다. Bridge는 이 두 축을 분리합니다.

```python
class Renderer(Protocol):
    def render_circle(self, x: int, y: int, radius: int) -> str: ...

class SVGRenderer:
    def render_circle(self, x: int, y: int, radius: int) -> str:
        return f'<circle cx="{x}" cy="{y}" r="{radius}"/>'

class Shape:
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def draw(self) -> str:
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, renderer: Renderer, x: int, y: int, radius: int) -> None:
        super().__init__(renderer)
        self._x, self._y, self._radius = x, y, radius

    def draw(self) -> str:
        return self._renderer.render_circle(self._x, self._y, self._radius)
```

실무에서 Bridge를 명시적으로 도입하는 경우는 드뭅니다. 하지만 DB 드라이버 추상화(`sqlalchemy.Engine` + 각 dialect)나 로깅 핸들러(`logging.Handler` + 각 출력 대상) 같은 곳에서 이미 Bridge 구조가 쓰이고 있습니다.

### Flyweight

Flyweight는 대량의 유사 객체가 메모리를 과도하게 차지할 때, 공유 가능한 상태(intrinsic)와 개별 상태(extrinsic)를 분리해서 메모리를 절약합니다. 게임의 총알 수천 개가 같은 텍스처를 공유하거나, 텍스트 에디터에서 같은 글리프 객체를 재사용하는 것이 전형적인 예입니다.

Python에서는 `__slots__`, 문자열 인터닝(`sys.intern`), `functools.lru_cache`가 Flyweight의 정신을 이미 구현하고 있어서, 패턴을 명시적으로 구현할 일은 많지 않습니다.

## 각 패턴이 요구하는 비용

패턴은 공짜가 아닙니다. 도입할 때 잃는 것을 미리 알아야 합니다.

| 패턴 | 얻는 것 | 잃는 것 |
| --- | --- | --- |
| Adapter | 인터페이스 호환, 교체 용이 | 간접 호출 1단계 추가, 변환 버그 가능성 |
| Bridge | 추상화/구현 독립 확장 | 초기 설계 복잡도 증가 |
| Composite | 트리 순회 통일 | 리프와 컨테이너 구분이 흐려짐 |
| Decorator | 동적 책임 추가, 조합 자유 | 스택 트레이스 복잡, 순서 의존성 |
| Facade | 호출자 단순화 | Facade 뒤 세부 접근이 어려워짐 |
| Flyweight | 메모리 절약 | 상태 분리 로직 복잡, 스레드 안전 주의 |
| Proxy | 접근 제어, 캐시, 지연 로딩 | 캐시 무효화 복잡, 디버깅 시 실제 객체 추적 필요 |

저는 팀에서 Structural 패턴을 도입할 때마다 "이 패턴으로 잃는 것이 현재 문제의 비용보다 작은가"를 한 문장으로 적어 보라고 권합니다. 적을 수 없으면 아직 도입할 때가 아닙니다.

## 처음 질문으로 돌아가기

- **상속 대신 합성을 쓰면 구체적으로 무엇이 달라질까요?**
  - 인터페이스를 안정적으로 유지한 채 구현만 교체할 수 있게 됩니다. Adapter가 레거시 SDK를 감싸면서 도메인 코드는 한 줄도 바꾸지 않은 것, Decorator 체인의 순서만 바꿔서 동작을 조정한 것이 모두 합성이 주는 유연성입니다. 상속이었다면 클래스 계층 전체를 재설계해야 했을 장면입니다.

- **Decorator와 Proxy는 둘 다 "감싸는" 패턴인데, 언제 어느 쪽을 골라야 할까요?**
  - 의도로 구분합니다. "기능을 추가"하고 싶으면 Decorator, "접근을 제어"하고 싶으면 Proxy입니다. `TimingClient`는 측정이라는 기능을 추가했으므로 Decorator이고, `CachedUserRepository`는 실제 DB 접근을 제어(지연+캐시)했으므로 Proxy입니다. 구현 모양은 비슷하지만 코드 리뷰에서 의도를 명확히 전달하려면 이름을 구분해서 쓰는 편이 좋습니다.

- **Structural 패턴을 도입했을 때 잃는 것은 무엇일까요?**
  - 간접 호출이 늘어나고, 디버깅 시 실제 동작 지점을 찾기까지 한두 단계를 더 거쳐야 합니다. 비용 표에서 본 것처럼 Decorator는 스택 트레이스를, Facade는 세부 접근을, Proxy는 캐시 무효화를 각각 어렵게 만듭니다. 이 비용이 현재 구조 문제의 고통보다 작을 때만 도입할 가치가 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Creational 패턴](./02-creational-patterns.md)
- **Structural 패턴 (현재 글)**
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
- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Decorator Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/decorator)
- [Facade Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/facade)
- [Composite Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/composite)
- [Proxy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/proxy)

### 실무 확장 읽을거리

- [Python typing — Protocol (Python docs)](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Head First Design Patterns — Structural Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Structural, Adapter, Decorator, Facade
