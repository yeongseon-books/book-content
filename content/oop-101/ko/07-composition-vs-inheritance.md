---
series: oop-101
episode: 7
title: 합성과 상속
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - OOP
  - 합성
  - 상속
  - 설계 패턴
seo_description: 합성과 상속의 차이를 비교하고 실무에서의 올바른 선택 기준을 다룹니다.
last_reviewed: '2026-05-11'
---

# 합성과 상속

> Object-Oriented Programming 101 시리즈 (7/10)


## 이 글에서 다룰 문제

상속은 부모 클래스와 강하게 결합됩니다. 부모의 내부 구현이 바뀌면 자식이 깨질 수 있습니다. 합성은 객체를 "포함"하므로 내부 구현에 의존하지 않고, 런타임에 교체도 가능합니다.

> 상속 = 컴파일 타임 결합, 합성 = 런타임 유연성

잘못된 상속은 코드를 수정할수록 복잡해지는 주요 원인입니다. "이 관계가 정말 is-a인가?"를 항상 자문해야 합니다.

## 핵심 개념 잡기

> 상속 vs 합성

```text
상속 (is-a)                    합성 (has-a)
┌─────────────┐               ┌─────────────┐
│ 부모 클래스  │               │ Car         │
└──────┬──────┘               │  ├─ Engine  │
       │                      │  ├─ Wheel   │
┌──────┴──────┐               │  └─ GPS     │
│ 자식 클래스  │               └─────────────┘
└─────────────┘
강한 결합                      느슨한 결합
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 합성(composition) | 객체가 다른 객체를 속성으로 포함하는 관계입니다 |
| 위임(delegation) | 요청을 내부 객체에게 전달하는 패턴입니다 |
| is-a 관계 | "자식은 부모의 일종이다" — 상속에 적합합니다 |
| has-a 관계 | "이 객체는 저 객체를 가지고 있다" — 합성에 적합합니다 |
| 의존성 주입(DI) | 외부에서 의존 객체를 전달하는 합성 패턴입니다 |

## Before / After

로깅 기능 추가를 비교합니다.

```python
# before: 상속으로 로깅 추가 — 다중 상속 필요
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService(Logger):  # UserService is-a Logger? 아닙니다
    def create_user(self, name: str) -> None:
        self.log(f"사용자 생성: {name}")
```

```python
# after: 합성으로 로깅 — 자연스러운 has-a 관계
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger  # has-a 관계

    def create_user(self, name: str) -> None:
        self._logger.log(f"사용자 생성: {name}")
```

## 단계별 실습

### Step 1: 합성 기본 — 자동차 조립

```python
class Engine:
    def __init__(self, horsepower: int) -> None:
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        self.running = True
        return f"{self.horsepower}마력 엔진 시동"

    def stop(self) -> str:
        self.running = False
        return "엔진 정지"


class GPS:
    def navigate(self, destination: str) -> str:
        return f"{destination}까지 경로 안내 시작"


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
car.drive("서울")
# 200마력 엔진 시동
# 서울까지 경로 안내 시작
car.park()
# 엔진 정지
```

### Step 2: 위임 패턴

```python
class Printer:
    def print_document(self, content: str) -> None:
        print(f"인쇄: {content}")

class Scanner:
    def scan(self) -> str:
        return "스캔 완료"

class Fax:
    def send_fax(self, number: str, content: str) -> None:
        print(f"{number}로 팩스 전송: {content}")


class MultiFunctionDevice:
    """합성 + 위임: 각 기능을 내부 객체에 위임"""

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
mfd.print_document("보고서")    # 인쇄: 보고서
print(mfd.scan())               # 스캔 완료
mfd.send_fax("02-1234", "계약서")  # 02-1234로 팩스 전송: 계약서
```

### Step 3: 전략 패턴 — 런타임 교체

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

sorter.set_strategy(QuickSort())  # 런타임 교체
print(sorter.execute(data))  # [1, 3, 5, 8, 9]
```

### Step 4: 의존성 주입

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
        self._db = db  # 외부에서 주입

    def create(self, user_id: str, name: str) -> None:
        self._db.save({"id": user_id, "name": name})

    def get(self, user_id: str) -> dict | None:
        return self._db.find(user_id)


db = InMemoryDB()
repo = UserRepository(db)
repo.create("u1", "김개발")
print(repo.get("u1"))  # {'id': 'u1', 'name': '김개발'}
```

### Step 5: 상속이 적절한 경우

```python
class HttpError(Exception):
    """HTTP 에러 기본 클래스 — 상속이 적절한 is-a 관계"""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code

class NotFoundError(HttpError):
    def __init__(self, resource: str) -> None:
        super().__init__(404, f"{resource}을(를) 찾을 수 없습니다")

class UnauthorizedError(HttpError):
    def __init__(self) -> None:
        super().__init__(401, "인증이 필요합니다")


try:
    raise NotFoundError("사용자")
except HttpError as e:
    print(f"[{e.status_code}] {e}")
# [404] 사용자을(를) 찾을 수 없습니다
```

## 이 코드에서 주목할 점

- 합성은 내부 객체를 교체할 수 있어 런타임 유연성이 높습니다
- 의존성 주입으로 테스트 시 mock 객체를 쉽게 주입할 수 있습니다
- 전략 패턴은 합성의 대표적 활용으로 알고리즘을 런타임에 교체합니다
- Exception 계층은 is-a 관계가 명확한 상속의 좋은 예입니다

## 흔한 실수 5가지

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

## 체크리스트

- [ ] is-a 관계와 has-a 관계를 구분할 수 있다
- [ ] 합성과 위임 패턴을 구현할 수 있다
- [ ] 전략 패턴으로 런타임 동작 교체를 구현할 수 있다
- [ ] 의존성 주입의 목적과 구현 방법을 이해한다
- [ ] 상속이 적절한 경우와 합성이 적절한 경우를 판단할 수 있다

## 정리 및 다음 글 안내

합성은 느슨한 결합과 런타임 유연성을 제공하여 대부분의 상황에서 상속보다 적합합니다. 상속은 is-a 관계가 명확한 곳에서만 사용합니다. 다음 글에서는 SOLID 원칙을 통해 객체지향 설계의 기본 원칙을 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- **합성과 상속 (현재 글)**
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Design Patterns — GoF (Gang of Four)](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Effective Python — Item 41: Consider Composing Functionality with Mix-in Classes](https://effectivepython.com/)
- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)

Tags: Python, OOP, 합성, 상속, 설계 패턴
