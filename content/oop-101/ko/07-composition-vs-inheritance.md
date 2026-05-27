---
title: "Object-Oriented Programming 101 (7/10): 합성과 상속"
series: oop-101
episode: 7
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
  - 합성
  - 상속
  - 설계 패턴
last_reviewed: '2026-05-15'
seo_description: 합성과 상속의 차이, 위임, 의존성 주입까지 실무 선택 기준으로 비교합니다.
---

# Object-Oriented Programming 101 (7/10): 합성과 상속

객체지향 설계에서 가장 자주 나오는 질문 하나를 꼽으라면 이것입니다. 기존 클래스를 확장할 때 상속을 써야 할까, 아니면 다른 객체를 내부에 두는 합성을 써야 할까. 둘 다 재사용을 돕지만, 변경 비용과 테스트 방식은 크게 달라집니다.

실무에서는 상속보다 합성을 먼저 떠올리는 팀이 많습니다. 부모 클래스의 내부 구조를 알지 않아도 되고, 런타임에 전략을 갈아 끼우거나 의존성을 주입하기 쉽기 때문입니다. 그래도 상속이 더 자연스러운 자리도 분명히 있습니다.

이 글은 OOP 101 시리즈의 7번째 글입니다.


![Object-Oriented Programming 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/07/07-01-concept-overview.ko.png)
*Object-Oriented Programming 101 7장 흐름 개요*

## 먼저 던지는 질문

- is-a 관계와 has-a 관계는 실무 설계에서 어떻게 구분하면 좋을까요?
- 왜 많은 경우 상속보다 합성이 더 안전한 기본 선택이 될까요?
- 위임과 의존성 주입은 합성의 장점을 어떻게 극대화할까요?

## 핵심 개념 잡기

> 상속 vs 합성

```text
Inheritance (is-a)                Composition (has-a)
┌─────────────┐               ┌─────────────┐
│ Parent class │               │ Car         │
└──────┬──────┘               │  ├─ Engine  │
       │                      │  ├─ Wheel   │
┌──────┴──────┐               │  └─ GPS     │
│ Child class  │               └─────────────┘
└─────────────┘
Tight coupling                 Loose coupling
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 합성(composition) | 객체가 다른 객체를 속성으로 포함하는 관계입니다 |
| 위임(delegation) | 요청을 내부 객체에게 전달하는 패턴입니다 |
| is-a 관계 | "자식은 부모의 일종이다" — 상속에 적합합니다 |
| has-a 관계 | "이 객체 안에 저 객체가 들어 있다" — 합성에 적합합니다 |
| 의존성 주입(DI) | 외부에서 의존 객체를 전달하는 합성 패턴입니다 |

## 전후 비교

로깅 기능 추가를 비교합니다.

```python
# before: inheritance 기반 로깅 — multiple inheritance 필요
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService(Logger):  # UserService is-a Logger? No.
    def create_user(self, name: str) -> None:
        self.log(f"Creating user: {name}")
```

```python
# after: composition 기반 로깅 — 자연스러운 has-a 관계
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger  # has-a relationship

    def create_user(self, name: str) -> None:
        self._logger.log(f"Creating user: {name}")
```

## 단계별 실습

### 1단계: 합성 기본 — 자동차 조립

```python
class Engine:
    def __init__(self, horsepower: int) -> None:
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        self.running = True
        return f"{self.horsepower}hp engine started"

    def stop(self) -> str:
        self.running = False
        return "Engine stopped"

class GPS:
    def navigate(self, destination: str) -> str:
        return f"Navigating to {destination}"

class Car:
    def __init__(self, engine: Engine, gps: GPS) -> None:
        self._engine = engine
        self._gps = gps

    def drive(self, destination: str) -> None:
        print(self._engine.start())
        print(self._gps.navigate(destination))

    def park(self) -> None:
        print(self._engine.stop())

car = Car(Engine(200), GPS())
car.drive("downtown")
# 200hp 엔진 시작됨
# 도심으로 이동 중
car.park()
# Engine stopped
```

### 2단계: 위임 패턴

```python
class Printer:
    def print_document(self, content: str) -> None:
        print(f"Printing: {content}")

class Scanner:
    def scan(self) -> str:
        return "Scan complete"

class Fax:
    def send_fax(self, number: str, content: str) -> None:
        print(f"Faxing to {number}: {content}")

class MultiFunctionDevice:
    """Composition + delegation: each function delegated to an internal object"""

    def __init__(self) -> None:
        self._printer = Printer()
        self._scanner = Scanner()
        self._fax = Fax()

    def print_document(self, content: str) -> None:
        self._printer.print_document(content)

    def scan(self) -> str:
        return self._scanner.scan()

    def send_fax(self, number: str, content: str) -> None:
        self._fax.send_fax(number, content)

mfd = MultiFunctionDevice()
mfd.print_document("Report")       # Printing: Report
print(mfd.scan())                   # Scan complete
mfd.send_fax("02-1234", "Contract")  # Faxing to 02-1234: Contract
```

### 3단계: 전략 패턴 — 런타임 교체

```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list[int]) -> list[int]: ...

class BubbleSort:
    def sort(self, data: list[int]) -> list[int]:
        arr = data[:]
        for i in range(len(arr)):
            for j in range(len(arr) - 1 - i):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort:
    def sort(self, data: list[int]) -> list[int]:
        return sorted(data)

class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        return self._strategy.sort(data)

data = [5, 3, 8, 1, 9]
sorter = Sorter(BubbleSort())
print(sorter.execute(data))  # [1, 3, 5, 8, 9]

sorter.set_strategy(QuickSort())  # runtime replacement
print(sorter.execute(data))  # [1, 3, 5, 8, 9]
```

### 4단계: 의존성 주입

```python
from typing import Protocol

class Database(Protocol):
    def save(self, data: dict) -> None: ...
    def find(self, key: str) -> dict | None: ...

class InMemoryDB:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def save(self, data: dict) -> None:
        self._store[data["id"]] = data

    def find(self, key: str) -> dict | None:
        return self._store.get(key)

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db  # injected from outside

    def create(self, user_id: str, name: str) -> None:
        self._db.save({"id": user_id, "name": name})

    def get(self, user_id: str) -> dict | None:
        return self._db.find(user_id)

db = InMemoryDB()
repo = UserRepository(db)
repo.create("u1", "Kim")
print(repo.get("u1"))  # {'id': 'u1', 'name': 'Kim'}
```

### 5단계: 상속이 적절한 경우

```python
class HttpError(Exception):
    """HTTP error base class — inheritance is appropriate for is-a relationships"""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code

class NotFoundError(HttpError):
    def __init__(self, resource: str) -> None:
        super().__init__(404, f"{resource} not found")

class UnauthorizedError(HttpError):
    def __init__(self) -> None:
        super().__init__(401, "Authentication required")

try:
    raise NotFoundError("User")
except HttpError as e:
    print(f"[{e.status_code}] {e}")
# [404] 사용자를 찾을 수 없음
```

## 이 코드에서 주목할 점

- 합성은 내부 객체를 교체할 수 있어 런타임 유연성이 높습니다
- 의존성 주입으로 테스트 시 mock 객체를 쉽게 주입할 수 있습니다
- 전략 패턴은 합성의 대표적 활용으로 알고리즘을 런타임에 교체합니다
- Exception 계층은 is-a 관계가 명확한 상속의 좋은 예입니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| has-a 관계에 상속 사용 | Car is-a Engine은 성립하지 않습니다 | 합성으로 변경합니다 |
| 코드 재사용만을 위한 상속 | 의미 없는 계층이 생깁니다 | 합성 또는 유틸리티 함수를 사용합니다 |
| 합성 객체를 외부에 직접 노출 | 캡슐화가 깨집니다 | 위임 메서드로 감쌉니다 |
| 의존성을 내부에서 직접 생성 | 테스트와 교체가 어렵습니다 | 생성자에서 주입받습니다 |
| 모든 상속을 합성으로 변경 | Exception 등 상속이 적절한 경우가 있습니다 | is-a 관계가 명확하면 상속합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 Depends()는 의존성 주입 기반 합성 패턴입니다
- Django의 CBV는 Mixin 기반 합성으로 기능을 조합합니다
- 로깅, 캐시, 인증 등 횡단 관심사를 합성으로 분리합니다
- 테스트에서 실제 DB 대신 InMemoryDB를 주입합니다
- 마이크로서비스에서 HTTP 클라이언트를 합성으로 주입합니다

## 현업 개발자는 이렇게 생각합니다

"상속보다 합성을 선호하라"는 원칙은 맞지만, "상속을 쓰지 마라"는 뜻이 아닙니다. Exception 계층, Enum 확장, ABC 구현처럼 is-a 관계가 명확한 곳에서는 상속이 자연스럽습니다.

판단 기준은 간단합니다. "자식 객체를 부모 타입으로 사용할 수 있는가?"(리스코프 치환 원칙) 대답이 "예"면 상속, "아니오"면 합성입니다.

## 이런 실패 모드가 보이면 합성 쪽으로 리팩터링합니다

| 실패 모드 | 처음 드러나는 증상 | 리팩터링 방향 |
|-----------|-------------------|----------------|
| 부모 클래스 수정 후 자식 테스트가 연쇄적으로 깨짐 | unrelated 변경인데 여러 하위 클래스가 동시에 실패합니다 | 공통 정책만 남기고 세부 동작을 전략 객체로 분리합니다 |
| 한 자식만 예외 규칙이 계속 늘어남 | 오버라이드 안에 `if`, `try`, 특수 케이스가 몰립니다 | 그 자식이 가진 별도 책임을 내부 협력 객체로 뺍니다 |
| 런타임마다 다른 동작을 골라야 함 | 객체를 새로 상속하기보다 설정값 분기가 늘어납니다 | 생성자 주입 + 전략 패턴으로 전환합니다 |
| 테스트에서 부모 초기화가 너무 무거움 | 자식 단위 테스트에도 부모 의존성을 모두 준비해야 합니다 | 조립 코드를 분리하고 필요한 협력 객체만 주입받게 만듭니다 |

## 체크리스트

- [ ] is-a 관계와 has-a 관계를 구분할 수 있다
- [ ] 합성과 위임 패턴을 구현할 수 있다
- [ ] 전략 패턴으로 런타임 동작 교체를 구현할 수 있다
- [ ] 의존성 주입의 목적과 구현 방법을 이해한다
- [ ] 상속이 적절한 경우와 합성이 적절한 경우를 판단할 수 있다

## 정리 및 다음 글 안내

합성은 느슨한 결합과 런타임 유연성을 제공하여 대부분의 상황에서 상속보다 적합합니다. 상속은 is-a 관계가 명확한 곳에서만 사용합니다. 다음 글에서는 SOLID 원칙을 통해 객체지향 설계의 기본 원칙을 알아봅니다.

## 합성과 상속을 고를 때 보는 판단 축

합성과 상속의 선택은 취향이 아니라 변경 방향과 결합도를 기준으로 해야 합니다.

```text
상속
[BaseDiscountPolicy]
      ^
      |
[SeasonalPolicy] [VipPolicy]

합성
[Checkout]
  - discount_policy: DiscountPolicy
  - tax_policy: TaxPolicy
```

## 적용 전후: 상속 트리 폭증에서 정책 합성으로

```python
# before
class BaseCheckout:
    def total(self, amount: int) -> int:
        return amount

class VipSeasonalCheckout(BaseCheckout):
    def total(self, amount: int) -> int:
        return int(amount * 0.8)

class VipSeasonalTaxCheckout(BaseCheckout):
    def total(self, amount: int) -> int:
        return int(amount * 0.8 * 1.1)
```

```python
# after
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...

class TaxPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...

class TenPercentDiscount:
    def apply(self, amount: int) -> int:
        return int(amount * 0.9)

class VatTenPercent:
    def apply(self, amount: int) -> int:
        return int(amount * 1.1)

class Checkout:
    def __init__(self, discount: DiscountPolicy, tax: TaxPolicy) -> None:
        self.discount = discount
        self.tax = tax

    def total(self, amount: int) -> int:
        return self.tax.apply(self.discount.apply(amount))
```

## 위반 시나리오

| 위반 | 신호 | 교정 |
|---|---|---|
| 기능 조합마다 서브클래스 생성 | 클래스 개수 급증 | 전략 객체로 분리 후 합성 |
| 상위 클래스 protected 상태에 과의존 | 하위 클래스 디버깅 난이도 상승 | 명시적 협력 인터페이스 정의 |
| 상속만으로 확장을 강제 | 런타임 교체 불가 | 생성자 주입 방식으로 전환 |

## 비교표: 운영 관점

| 질문 | 상속 | 합성 |
|---|---|---|
| 특정 정책만 A/B 테스트 가능한가 | 어려움 | 쉬움 |
| 테스트에서 일부 정책만 더블 교체 가능한가 | 제한적 | 용이 |
| 신규 요구에 기존 클래스 수정이 필요한가 | 자주 필요 | 대개 불필요 |

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


## 리팩터링 회고: 변경 비용을 수치로 보는 방법

- 수정 파일 수가 기능 하나당 5개를 넘으면 경계 재설계를 검토합니다.
- 타입 분기 if/elif가 3개 이상 누적되면 다형성 또는 전략 객체로 이동합니다.
- 회귀 테스트 작성 시간이 구현 시간보다 길어지면 책임 배치를 재검토합니다.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

위 방식은 엄밀한 메트릭은 아니지만, 팀이 감각이 아니라 기준으로 논의하게 만드는 데 유용합니다.

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

## 추가 비교: 변경 요청 대응 시간

| 변경 요청 | 경계가 약한 코드 | 경계가 선명한 코드 |
|---|---|---|
| 할인 규칙 추가 | 분기문 탐색 후 다중 수정 | 정책 구현 추가 |
| 상태 전이 수정 | 여러 함수 동시 수정 | 도메인 메서드 수정 |
| 테스트 보강 | 통합 테스트 중심 | 단위 테스트 우선 |

이 비교는 성능 수치가 아니라 유지보수 리드타임을 줄이는 관점에서 중요합니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 짧은 리마인더

객체지향을 적용할 때는 "클래스를 몇 개 만들었는가"보다 "다음 변경에서 몇 파일을 수정해야 하는가"를 기준으로 품질을 평가합니다.

## 마지막 점검 문장

이 글의 예제는 모두 변경 파급을 줄이는 경계 설계를 기준으로 구성했습니다.


설계 의도와 테스트 계약을 함께 유지하는 것이 핵심입니다.

## 처음 질문으로 돌아가기

- **is-a 관계와 has-a 관계는 실무 설계에서 어떻게 구분하면 좋을까요?**
  - `HttpError`와 `NotFoundError`처럼 부모 타입으로 받아도 자연스러운 경우는 is-a 관계라서 상속이 맞습니다. 반대로 `UserService`가 `Logger`를 쓰거나 `Car`가 `Engine`과 `GPS`를 품는 구조는 역할상 has-a 관계이므로, 글은 상속 대신 합성으로 읽어야 한다고 분명히 나눴습니다.
- **왜 많은 경우 상속보다 합성이 더 안전한 기본 선택이 될까요?**
  - `Sorter`가 `BubbleSort`와 `QuickSort`를 런타임에 갈아 끼우는 예제처럼, 합성은 내부 전략을 교체해도 상위 객체의 타입 자체를 바꾸지 않아도 됩니다. 또 `VipSeasonalCheckout` 같은 조합별 서브클래스 폭증 대신 `Checkout(discount, tax)`로 정책을 주입하면 클래스 수와 결합도가 함께 줄어든다는 점이 본문 전체의 핵심입니다.
- **위임과 의존성 주입은 합성의 장점을 어떻게 극대화할까요?**
  - `MultiFunctionDevice`는 인쇄·스캔·팩스를 각각 내부 객체에 위임해서 외부에는 하나의 장치처럼 보이게 만들고, `UserRepository`는 `InMemoryDB`를 생성자에서 주입받아 테스트 더블 교체를 쉽게 했습니다. 즉 위임은 인터페이스를 단순하게 유지하고, 의존성 주입은 조립과 테스트를 분리해서 합성의 유연성을 실전에서 바로 쓰게 해 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- **합성과 상속 (현재 글)**
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Design Patterns — GoF (Gang of Four)](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Effective Python — Item 41: Consider Composing Functionality with Mix-in Classes](https://effectivepython.com/)
- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 합성, 상속, 설계 패턴
