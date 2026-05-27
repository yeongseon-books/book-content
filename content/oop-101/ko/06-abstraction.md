---
title: "Object-Oriented Programming 101 (6/10): 추상화"
series: oop-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 추상화
  - ABC
  - 인터페이스
last_reviewed: '2026-05-17'
seo_description: ABC와 abstractmethod로 공통 인터페이스를 강제하는 Python 추상화 설계를 설명합니다.
---

# Object-Oriented Programming 101 (6/10): 추상화

추상화가 진짜 필요해지는 순간은 구현체가 두세 개로 늘어나면서 호출부가 어떤 메서드 이름을 불러야 할지 추측하기 시작할 때입니다. 이 글은 OOP 101 시리즈의 6번째 글입니다.

Python에서 추상화는 이론 용어로 끝나지 않습니다. 어떤 메서드를 반드시 구현해야 하는지, 어떤 단계는 부모가 공통으로 가져가야 하는지, 어디까지를 팀의 계약으로 강제할지를 정하는 실무 설계 문제에 더 가깝습니다.


![Object-Oriented Programming 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/06/06-01-concept-overview.ko.png)
*Object-Oriented Programming 101 6장 흐름 개요*

> 추상화는 '복잡한 걸 숨기는 일'이 아니라 '독자에게 필요한 결정만 남기고 나머지를 보이지 않게 옮기는 일'입니다 — 잘못된 추상화는 숨기는 게 아니라 미루는 일이고, 그 빚은 항상 한참 뒤에 청구됩니다.

## 먼저 던지는 질문

- 덕 타이핑 관례만으로는 언제부터 부족해질까요?
- 추상 클래스는 어떤 메서드와 프로퍼티를 반드시 강제해야 할까요?
- 템플릿 메서드 패턴은 부모가 흐름을 지키고 자식이 세부 구현을 맡게 만드는 데 어떻게 도움이 될까요?

## 핵심 개념 잡기

계약이 없으면 어떤 구현체는 `read_file()`을 쓰고, 다른 구현체는 `fetch_rows()`를 쓰고, 또 다른 구현체는 `pull()`을 씁니다. 그러면 오케스트레이터는 구현체별 분기문 덩어리가 됩니다. 추상화의 첫 목적은 그 분기문을 없애는 공통 언어를 정하는 데 있습니다.

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 추상 클래스 | 직접 인스턴스화할 수 없고 하위 클래스에 특정 멤버 구현을 강제하는 클래스입니다 |
| `@abstractmethod` | 하위 클래스가 반드시 구현해야 하는 메서드나 프로퍼티를 표시합니다 |
| ABC | `abc` 모듈이 제공하는 명시적 계약 메커니즘입니다 |
| 템플릿 메서드 패턴 | 부모가 워크플로 골격을 가지고, 자식이 가변 단계를 채우는 패턴입니다 |
| Protocol | 상속 없이도 필요한 모양을 만족하면 되는 구조적 계약입니다 |

## 전후 비교

이 글에서 바꾸려는 핵심은 작지만 실무적입니다.

```python
# before: 호출부가 구현체마다 다른 사적 용어를 알아야 합니다
class CsvFeed:
    def read_file(self, path: str) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed:
    def fetch_rows(self, table: str) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]
```

```python
# after: 모든 구현체가 하나의 계약을 공유합니다
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...
```

## 하나의 워크플로로 보는 추상화 설계

### 1단계: 호출부가 어디서부터 깨지는지 확인합니다

하나의 고객 적재 파이프라인을 만들고 있는데, 각 개발자가 소스 클래스를 제각각 만들었다고 가정해 보겠습니다.

```python
class CsvFeed:
    def read_file(self, path: str) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed:
    def fetch_rows(self, table: str) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]

class PartnerApiFeed:
    def pull(self) -> list[dict]:
        return [{"email": "carol@example.com", "active": True}]

def ingest(source: object) -> list[dict]:
    return source.fetch_records()  # 호출부는 존재하지 않는 메서드를 가정합니다

ingest(CsvFeed())
```

#### 실패 신호

```text
AttributeError: 'CsvFeed' object has no attribute 'fetch_records'
```

이 문제의 본질은 메서드 하나가 빠진 것이 아니라, 워크플로 전체에 공통 언어가 없다는 데 있습니다.

### 2단계: ABC로 팀 계약을 고정합니다

이 시점의 다음 선택은 `if isinstance(...)` 분기를 더 늘리는 것이 아니라, 최소 계약을 명시적으로 고정하는 것입니다.

```python
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """로그와 메트릭에서 사용할 이름입니다."""

    @abstractmethod
    def fetch_records(self) -> list[dict]:
        """이 소스의 원시 고객 레코드를 반환합니다."""

class CsvFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [{"email": "alice@example.com", "active": True}]

class WarehouseFeed(FeedSource):
    @property
    def source_name(self) -> str:
        return "warehouse"

    def fetch_records(self) -> list[dict]:
        return [{"email": "bob@example.com", "active": False}]
```

여기서 추상화는 두 가지를 해냅니다.

- 메서드 이름과 반환 모양을 하나로 고정합니다.
- 반쪽 구현체가 조용히 인스턴스화되는 일을 막습니다.

### 3단계: 템플릿 메서드로 공통 흐름을 부모에 둡니다

여러 소스가 같은 적재 단계를 공유한다면, 각 구현체가 매번 같은 순서를 다시 쓰게 두지 말고 부모가 골격을 가져가야 합니다.

```python
from abc import ABC, abstractmethod

class IngestionPipeline(ABC):
    def run(self) -> list[dict]:
        raw = self.fetch_records()
        normalized = [self.normalize(row) for row in raw]
        valid = [row for row in normalized if self.is_valid(row)]
        self.store(valid)
        print(f"[{self.source_name}] loaded {len(valid)} records")
        return valid

    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

    def normalize(self, row: dict) -> dict:
        return {
            "email": row["email"].strip().lower(),
            "active": bool(row["active"]),
        }

    def is_valid(self, row: dict) -> bool:
        return "@" in row["email"]

    @abstractmethod
    def store(self, rows: list[dict]) -> None: ...

class CsvCustomerPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "csv"

    def fetch_records(self) -> list[dict]:
        return [
            {"email": " Alice@example.com ", "active": 1},
            {"email": "broken-email", "active": 1},
        ]

    def store(self, rows: list[dict]) -> None:
        for row in rows:
            print(f"store -> {row}")

class PartnerApiPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "partner-api"

    def fetch_records(self) -> list[dict]:
        return [{"email": "Carol@Example.com", "active": True}]

    def store(self, rows: list[dict]) -> None:
        for row in rows:
            print(f"store -> {row}")
```

이제 자식 클래스는 달라지는 부분만 설명합니다. 데이터를 어디서 가져오는지, 어디에 저장하는지만 다르고, 정규화·검증·적재 순서는 부모가 책임집니다.

### 4단계: 수정할 수 없는 외부 구현체를 연결합니다

워크플로는 괜찮지만 클래스가 외부 라이브러리 소유라면 상속을 강제하기 어려울 수 있습니다.

```python
from abc import ABC, abstractmethod

class FeedSource(ABC):
    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

class VendorSnapshot:
    """실제로는 외부 패키지에 있다고 가정합니다."""

    def fetch_records(self) -> list[dict]:
        return [{"email": "vendor@example.com", "active": True}]

FeedSource.register(VendorSnapshot)

snapshot = VendorSnapshot()
print(isinstance(snapshot, FeedSource))
print(snapshot.fetch_records())
```

`register()`는 외부 클래스의 모양을 신뢰하고 런타임 검사에만 포함시키고 싶을 때 유용합니다.

### 5단계: ABC와 Protocol 중 무엇을 쓸지 명시적으로 결정합니다

모든 통합 지점에 상속을 강제할 필요는 없습니다.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class InternalFeed(ABC):
    @abstractmethod
    def fetch_records(self) -> list[dict]: ...

class FeedLike(Protocol):
    def fetch_records(self) -> list[dict]: ...

class BackfillExport:
    def fetch_records(self) -> list[dict]:
        return [{"email": "backfill@example.com", "active": True}]

def preview(feed: FeedLike) -> int:
    return len(feed.fetch_records())

print(preview(BackfillExport()))
```

- **ABC**는 내부 프레임워크처럼 명시적 상속, 공통 기본 동작, 인스턴스화 시점 검사가 필요할 때 적합합니다.
- **Protocol**은 필요한 모양만 맞으면 되는 통합 지점, 특히 외부 라이브러리 호환성에 더 적합합니다.

## 실행·검증·실패 경로

### 실행

3단계 코드를 `abstraction_workflow.py`에 넣고 실행합니다.

```bash
python abstraction_workflow.py
```

예상 출력은 다음과 같습니다.

```text
store -> {'email': 'alice@example.com', 'active': True}
[csv] loaded 1 records
store -> {'email': 'carol@example.com', 'active': True}
[partner-api] loaded 1 records
```

### 검증

실행 후에는 세 가지를 확인합니다.

1. `normalize()`가 대소문자와 공백을 정리했는가
2. `is_valid()`가 잘못된 이메일을 걸러냈는가
3. 원본 소스는 달라도 최종 출력 계약은 동일한가

### 실패 경로 1: 필수 메서드를 빼먹은 경우

```python
class BrokenPipeline(IngestionPipeline):
    @property
    def source_name(self) -> str:
        return "broken"

    def fetch_records(self) -> list[dict]:
        return []

BrokenPipeline()
```

예상 실패:

```text
TypeError: Can't instantiate abstract class BrokenPipeline with abstract method store
```

이 오류는 불편한 것이 아니라 유용합니다. 팀이 반쪽짜리 구현체를 배포하지 못하게 막아 주기 때문입니다.

### 실패 경로 2: 잘못된 계약 스타일을 고른 경우

외부 라이브러리가 이미 `fetch_records()` 모양을 안정적으로 제공하고 있다면, 그 객체에 우리 ABC 상속을 강제하는 순간 불필요한 래핑 비용이 생깁니다. 그 지점이 바로 Protocol 기반 경계가 더 단순한 순간입니다.

다음 기준으로 판단하면 됩니다.

| 질문 | 예라면 | 더 적합한 선택 |
|------|--------|----------------|
| 구현체를 우리가 대부분 소유하는가 | 예 | ABC |
| 공통 기본 동작이 필요한가 | 예 | ABC |
| 모양 호환만 있으면 되는가 | 예 | Protocol |
| 외부 라이브러리 구현체인가 | 예 | Protocol 또는 `register()` |

## 이 워크플로에서 주목할 점

- 첫 번째 추상화 문제는 "추상 클래스를 어떻게 쓰지?"가 아니라 "왜 호출부가 구현체별 사전 용어를 다 알아야 하지?"였습니다.
- `@abstractmethod`는 팀 협업이 시작되는 시점에서 특히 가치가 커집니다.
- 템플릿 메서드 패턴은 워크플로 순서를 고정하면서 소스별 차이만 열어 둡니다.
- `register()`와 Protocol은 둘 다 호환성 문제를 풀지만, 해결하는 상황은 다릅니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 더 나은 선택 |
|------|------------|--------------|
| 모든 인터페이스를 ABC로 만듦 | 외부 통합까지 불필요한 상속을 강제합니다 | 모양 호환이면 Protocol을 사용합니다 |
| 부모 클래스에 로직을 너무 많이 넣음 | 추상 클래스가 거대한 god object가 됩니다 | 진짜 공통 단계만 부모에 둡니다 |
| 추상 멤버 없는 ABC 사용 | 계약이 실제로 아무것도 강제하지 않습니다 | 최소 하나의 필수 메서드나 프로퍼티를 둡니다 |
| 자식마다 같은 책임의 메서드 이름을 바꿈 | 호출부가 구현 상세에 분기합니다 | 먼저 공통 어휘를 고정합니다 |
| 출력 계약을 검증하지 않음 | 적재는 됐지만 행 모양이 서로 달라집니다 | 실행 후 정규화된 결과를 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 표준 라이브러리의 `collections.abc`는 명시적 컨테이너 계약을 제공합니다.
- Django 클래스 기반 뷰는 템플릿 메서드 스타일 흐름을 자주 보여 줍니다.
- 플러그인 시스템은 내부에서는 ABC, 외부 경계에서는 Protocol을 함께 쓰는 경우가 많습니다.
- ETL 파이프라인은 하나의 적재 골격에 소스별 어댑터를 붙이는 구조가 흔합니다.

## 현업 개발자는 이렇게 생각합니다

현업에서는 코드를 "더 객체지향적으로 보이게" 하려고 추상화를 요구하지 않습니다. 구현체가 여러 개로 늘어나면서 호출부가 그 대가를 치르기 시작했기 때문에 추상화를 꺼내 듭니다. 좋은 추상화는 가장 작은 계약으로 구현체의 드리프트를 멈추게 합니다.

그래서 Python 코드베이스에서는 두 방식을 자주 섞습니다. 팀이 소유한 내부 프레임워크에는 ABC를 쓰고, 외부 호환이 중요한 경계에는 Protocol을 둡니다.

## 체크리스트

- [ ] 구현체마다 다른 메서드 이름이 왜 워크플로 문제인지 설명할 수 있다
- [ ] 필수 프로퍼티 1개와 필수 메서드 1개를 가진 ABC를 설계할 수 있다
- [ ] 템플릿 메서드 패턴으로 공통 흐름을 부모에 둘 수 있다
- [ ] 외부 클래스에는 언제 `register()`만으로 충분한지 판단할 수 있다
- [ ] 구조적 호환이 필요할 때 ABC 대신 Protocol을 선택할 수 있다

## 정리 및 다음 글 안내

추상화는 하나의 워크플로에 여러 구현체가 들어오는 순간부터 가치가 커집니다. 팀 계약과 공통 기본 동작이 중요하면 ABC를 쓰고, 상속보다 호환성이 중요하면 Protocol을 선택하면 됩니다. 다음 글에서는 합성과 상속을 비교하면서, 이 계약을 어디에 배치하는 것이 더 자연스러운지 이어서 살펴봅니다.

## 추상화의 품질은 숨긴 양이 아니라 남긴 계약으로 결정됩니다

좋은 추상화는 세부 구현을 감추되, 호출자가 의존해야 하는 규칙은 명확하게 남깁니다.

```text
[OrderUseCase]
  + execute(command)
     |
     +--> [OrderRepository] (abstract)
     +--> [PaymentGateway] (abstract)

구현체
OrderRepository <- SqlOrderRepository, InMemoryOrderRepository
PaymentGateway  <- MockGateway, RealGateway
```

## 적용 전후: 구체 구현 의존에서 포트-어댑터 구조로

```python
# before
class OrderUseCase:
    def execute(self, order_id: str, amount: int) -> str:
        conn = sqlite3.connect('orders.db')
        # 저장, 결제, 로그가 모두 혼재
        return 'ok'
```

```python
# after
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order_id: str, amount: int) -> None:
        pass

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, order_id: str, amount: int) -> str:
        pass

class OrderUseCase:
    def __init__(self, repo: OrderRepository, gateway: PaymentGateway) -> None:
        self.repo = repo
        self.gateway = gateway

    def execute(self, order_id: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError('amount must be positive')
        self.repo.save(order_id, amount)
        return self.gateway.charge(order_id, amount)
```

## 위반 사례

| 위반 | 증상 | 수정 |
|---|---|---|
| 추상 클래스에 구체 SQL가 섞임 | 계층 경계 붕괴 | 포트에는 계약만 남김 |
| use case가 외부 SDK 타입을 직접 반환 | 상위 계층 오염 | 도메인 DTO로 변환 |
| 추상화가 너무 세분화됨 | 구현 클래스 폭증 | 변경 축 기준으로 인터페이스 통합 |

## 비교표: 얕은 추상화 vs 과도한 추상화

| 항목 | 얕은 추상화 | 과도한 추상화 |
|---|---|---|
| 장점 | 이해가 빠름 | 교체 유연성 큼 |
| 단점 | 구현 누수 가능 | 학습 비용 큼 |
| 적용 기준 | 변동이 적은 내부 코드 | 외부 의존성, 교체 가능성 높은 영역 |

## 실전 시나리오: 요구사항 변경을 견디는 구조로 바꾸기

현업에서는 기능 추가보다 규칙 변경이 더 자주 발생합니다. 따라서 클래스 구조를 평가할 때는 "지금 동작하는가"보다 "다음 변경을 어디까지 건드려야 하는가"를 기준으로 보는 편이 안전합니다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

이 코드는 할인 규칙이 바뀌어도 `Invoice.total()`을 수정할 필요가 없습니다. 확장은 구현 클래스 추가로 닫히고, 핵심 흐름은 안정적으로 유지됩니다.

## UML 스타일로 보는 협력 관계

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

협력 구조를 이렇게 텍스트로 적어 두면 코드 리뷰에서 "어디가 정책 축이고 어디가 도메인 축인가"를 빠르게 맞출 수 있습니다.

## 안티패턴과 교정 절차

| 안티패턴 | 발견 신호 | 교정 순서 |
|---|---|---|
| 거대 클래스(God Object) | 메서드가 20개 이상, 변경 이력이 분산됨 | 책임 축 분해 → 협력 인터페이스 도출 |
| 데이터만 가진 빈 클래스 | 메서드 없이 getter/setter만 존재 | 규칙 메서드 이동 또는 dataclass로 단순화 |
| 상속 트리 우회 분기 | 하위 클래스 타입 체크 분기 존재 | 다형성 계약 재정의 |
| 인프라 타입 누수 | 도메인 계층이 SDK 응답 객체 의존 | DTO 변환 계층 추가 |

## 전후 비교: 테스트 유지비

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 테스트 준비 | 전역 상태 초기화 필요 | 객체 단위 상태 생성 |
| 실패 원인 추적 | 함수 체인 전체 역추적 | 클래스 메서드 단위 추적 |
| 회귀 범위 | 넓고 불명확 | 좁고 예측 가능 |

## 팀 적용 체크리스트

- 도메인 용어와 클래스 이름이 일치하는지 확인합니다.
- 인스턴스 생성 시점에 불변식이 완성되는지 확인합니다.
- 정책 변경이 기존 코드 수정이 아닌 구현 추가로 가능한지 점검합니다.
- 코드 리뷰에서 UML 텍스트 10줄로 협력 구조를 먼저 합의합니다.
- 테스트 이름이 메서드명보다 비즈니스 규칙을 설명하는지 확인합니다.

## 미니 케이스 스터디: 규칙 추가 한 번으로 검증하기

아래 예시는 정책 확장을 기존 코드 수정 없이 추가하는 최소 단위입니다.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

핵심은 새로운 정책이 호출 경로를 깨지 않고 들어온다는 사실입니다. 변경 이력이 정책 클래스에만 남도록 경계를 유지하면 회귀 위험이 줄어듭니다.

| 확인 질문 | Pass 기준 |
|---|---|
| 새 정책 추가 시 기존 함수 수정이 필요한가 | 아니오 |
| 예외 정책이 기존 계약과 같은가 | 예 |
| 테스트가 정책별로 분리되어 있는가 | 예 |

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 한 줄 정리 확장

객체지향 품질은 클래스 개수가 아니라 변경 영향 범위를 얼마나 줄였는지로 판단합니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 처음 질문으로 돌아가기

- **덕 타이핑 관례만으로는 언제부터 부족해질까요?**
  - `CsvFeed.read_file()`, `WarehouseFeed.fetch_rows()`, `PartnerApiFeed.pull()`처럼 구현체마다 용어가 제각각이면 호출부가 `fetch_records()`를 기대하는 순간 바로 `AttributeError`가 납니다. 글은 이 지점이 바로 덕 타이핑 관례만으로는 부족해지는 순간이며, 팀 차원의 공통 언어가 필요해진 시점이라고 설명합니다.
- **추상 클래스는 어떤 메서드와 프로퍼티를 반드시 강제해야 할까요?**
  - 이 글에서는 로그와 메트릭에 쓰일 `source_name` 프로퍼티, 실제 데이터를 가져오는 `fetch_records()`, 그리고 파이프라인 저장 단계인 `store()`를 추상 멤버로 강제했습니다. 공통 흐름을 유지하는 데 꼭 필요한 표면만 추상 계약으로 남기고, `normalize()`나 `is_valid()` 같은 기본 동작은 부모가 제공하는 구성이 왜 중요한지도 함께 보여 주었습니다.
- **템플릿 메서드 패턴은 부모가 흐름을 지키고 자식이 세부 구현을 맡게 만드는 데 어떻게 도움이 될까요?**
  - `IngestionPipeline.run()`은 `fetch_records() → normalize() → is_valid() → store()` 순서를 부모가 고정하고, `CsvCustomerPipeline`과 `PartnerApiPipeline`은 소스별 수집과 저장만 구현합니다. 덕분에 이메일 정규화와 잘못된 주소 필터링 같은 핵심 규칙은 한곳에 남고, 자식 클래스는 달라지는 부분만 채워 넣는 구조가 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- **추상화 (현재 글)**
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [PEP 544 — Protocols: Structural Subtyping](https://peps.python.org/pep-0544/)
- [Python collections.abc 문서](https://docs.python.org/3/library/collections.abc.html)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 추상화, ABC, 인터페이스
