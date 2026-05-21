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

## 먼저 던지는 질문

- is-a 관계와 has-a 관계는 실무 설계에서 어떻게 구분하면 좋을까요?
- 왜 많은 경우 상속보다 합성이 더 안전한 기본 선택이 될까요?
- 위임과 의존성 주입은 합성의 장점을 어떻게 극대화할까요?

## 큰 그림

![Object-Oriented Programming 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/07/07-01-concept-overview.ko.png)

*Object-Oriented Programming 101 7장 흐름 개요*

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
# before: logging via inheritance — multiple inheritance needed
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService(Logger):  # UserService is-a Logger? No.
    def create_user(self, name: str) -> None:
        self.log(f"Creating user: {name}")
```

```python
# after: logging via composition — natural has-a relationship
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
# 200hp engine started
# Navigating to downtown
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
# [404] User not found
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

## 처음 질문으로 돌아가기

- **is-a 관계와 has-a 관계는 실무 설계에서 어떻게 구분하면 좋을까요?**
  - 본문의 기준은 합성과 상속를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 많은 경우 상속보다 합성이 더 안전한 기본 선택이 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **위임과 의존성 주입은 합성의 장점을 어떻게 극대화할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Python, OOP, 합성, 상속, 설계 패턴
