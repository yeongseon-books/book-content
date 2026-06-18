---
title: "바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속"
series: oop-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 합성
  - 상속
  - 바이브코딩
  - 설계 패턴
last_reviewed: '2026-06-18'
seo_description: AI가 상속 대신 합성과 의존성 주입을 선택하는 이유를 설명합니다. 바이브코딩 관점에서 합성 패턴을 이해하고 수정하는 방법을 정리합니다.
---

# 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 일곱 번째 글입니다.

---

AI에게 주문 처리 시스템을 만들어 달라고 하면 `OrderService`가 `Logger`를 **상속받지 않고** 생성자에서 `logger: Logger`를 **주입받는** 형태로 만들어 줍니다. 처음엔 "왜 상속을 안 쓰고 이렇게 복잡하게 만들었지?"라는 생각이 들 수 있습니다.

AI가 합성을 선택한 데는 이유가 있습니다. `UserService`가 `Logger`의 일종(is-a)은 아닙니다. `UserService`는 `Logger`를 가지고 있을(has-a) 뿐입니다. 이 차이를 구분하는 것이 합성과 상속을 선택하는 기준입니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "AI가 생성자에 의존성을 주입받는 코드를 만들었다면, '테스트와 교체가 쉽도록 설계했다'는 의미입니다."

## 이 글에서 다룰 문제

- is-a 관계와 has-a 관계를 실무에서 어떻게 구분하면 좋을까요?
- 왜 많은 경우 상속보다 합성이 더 안전한 기본 선택이 될까요?
- 의존성 주입(DI)은 합성의 장점을 어떻게 극대화할까요?
- AI가 만든 합성 패턴을 어떻게 수정하고 확장할 수 있을까요?
- 상속이 여전히 적절한 경우는 언제인가요?

## 핵심 개념 잡기

```text
상속 (is-a)                    합성 (has-a)
┌─────────────┐               ┌─────────────┐
│ Animal      │               │ Car         │
└──────┬──────┘               │  ├─ Engine  │
       │                      │  ├─ Wheel   │
┌──────┴──────┐               │  └─ GPS     │
│ Dog         │               └─────────────┘
└─────────────┘
강한 결합                       느슨한 결합
```

| 용어 | 설명 |
|------|------|
| 합성(composition) | 객체가 다른 객체를 속성으로 포함하는 관계입니다 |
| 위임(delegation) | 요청을 내부 객체에게 전달하는 패턴입니다 |
| is-a 관계 | "자식은 부모의 일종이다" — 상속에 적합합니다 |
| has-a 관계 | "이 객체 안에 저 객체가 들어 있다" — 합성에 적합합니다 |
| 의존성 주입(DI) | 외부에서 의존 객체를 전달하는 합성 패턴입니다 |

## Before / After: AI가 상속 대신 합성을 쓰는 이유

```python
# Before: 상속 기반 로깅 — UserService is-a Logger? 아닙니다
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService(Logger):  # UserService는 Logger의 일종이 아님
    def create_user(self, name: str) -> None:
        self.log(f"사용자 생성: {name}")
        # Logger와 UserService가 강하게 결합됨
```

```python
# After: 합성 기반 로깅 — has-a 관계가 자연스러움
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger  # has-a 관계

    def create_user(self, name: str) -> None:
        self._logger.log(f"사용자 생성: {name}")

# 테스트할 때 다른 Logger를 주입할 수 있음
class SilentLogger:
    def log(self, msg: str) -> None:
        pass  # 테스트에서 출력 없애기

service = UserService(logger=SilentLogger())  # 교체 가능
```

합성을 쓰면 `UserService`를 테스트할 때 실제 Logger 대신 다른 구현을 주입할 수 있습니다. 상속을 쓰면 이것이 불가능합니다.

## 바이브코딩 관점: 의존성 주입 패턴 읽기

AI가 생성자에서 인터페이스를 받는 코드를 자주 만듭니다. 이것이 **의존성 주입(Dependency Injection)** 패턴입니다.

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
        self._db = db  # 외부에서 주입받음 — 어떤 구현이든 교체 가능

    def create(self, user_id: str, name: str) -> None:
        self._db.save({"id": user_id, "name": name})

    def get(self, user_id: str) -> dict | None:
        return self._db.find(user_id)

# 실제 사용: InMemoryDB 주입
db = InMemoryDB()
repo = UserRepository(db)
repo.create("u1", "김개발")
print(repo.get("u1"))  # {'id': 'u1', 'name': '김개발'}

# 테스트: 다른 DB 구현 주입 가능
```

AI가 이 패턴을 쓰면 "이 클래스는 특정 구현에 의존하지 않도록 설계했다"는 의미입니다. 나중에 DB를 교체하거나 테스트할 때 유용합니다.

## 전략 패턴: 런타임에 동작 교체

합성의 대표적 활용 패턴입니다. AI가 알고리즘을 런타임에 교체 가능하게 만들 때 사용합니다.

```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list[int]) -> list[int]: ...

class QuickSort:
    def sort(self, data: list[int]) -> list[int]:
        return sorted(data)  # 간단히 Python 내장 정렬 사용

class ReversedSort:
    def sort(self, data: list[int]) -> list[int]:
        return sorted(data, reverse=True)

class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy  # 런타임 교체

    def execute(self, data: list[int]) -> list[int]:
        return self._strategy.sort(data)

data = [5, 3, 8, 1, 9]
sorter = Sorter(QuickSort())
print(sorter.execute(data))  # [1, 3, 5, 8, 9]

sorter.set_strategy(ReversedSort())  # 런타임에 전략 교체
print(sorter.execute(data))  # [9, 8, 5, 3, 1]
```

## 상속이 적절한 경우

상속이 여전히 적합한 자리도 있습니다. 주로 is-a 관계가 명확할 때입니다.

```python
class HttpError(Exception):
    """HTTP 에러 기반 클래스 — Exception은 is-a 관계가 명확함"""
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code

class NotFoundError(HttpError):
    def __init__(self, resource: str) -> None:
        super().__init__(404, f"{resource}을 찾을 수 없습니다")

class UnauthorizedError(HttpError):
    def __init__(self) -> None:
        super().__init__(401, "인증이 필요합니다")

# NotFoundError는 HttpError의 일종 — 상속이 적합
try:
    raise NotFoundError("사용자")
except HttpError as e:
    print(f"[{e.status_code}] {e}")  # [404] 사용자을 찾을 수 없습니다
```

## AI가 만든 합성이 잘못된 신호

| 실패 모드 | 처음 드러나는 증상 | 리팩터링 방향 |
|-----------|-------------------|----------------|
| 부모 수정 후 자식 테스트가 연쇄적으로 깨짐 | 관련 없는 변경인데 여러 자식이 동시에 실패 | 공통 동작을 전략 객체로 분리 |
| 한 자식만 예외 규칙이 계속 늘어남 | 오버라이드 안에 if/else가 쌓임 | 해당 자식의 별도 책임을 내부 협력 객체로 분리 |
| 런타임마다 다른 동작을 골라야 함 | 설정값 분기가 늘어남 | 생성자 주입 + 전략 패턴으로 전환 |

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| has-a 관계에 상속 사용 | Car is-a Engine은 성립하지 않습니다 | 합성으로 변경합니다 |
| 코드 재사용만을 위한 상속 | 의미 없는 계층이 생깁니다 | 합성 또는 유틸리티 함수를 사용합니다 |
| 합성 객체를 외부에 직접 노출 | 캡슐화가 깨집니다 | 위임 메서드로 감쌉니다 |
| 의존성을 내부에서 직접 생성 | 테스트와 교체가 어렵습니다 | 생성자에서 주입받습니다 |
| 모든 상속을 합성으로 변경 | Exception 등 상속이 적절한 경우도 있습니다 | is-a 관계가 명확하면 상속합니다 |

## AI 팁: 합성 패턴 수정하기

AI가 만든 의존성 주입 패턴을 수정할 때 이렇게 접근하세요.

```python
# AI가 만든 클래스에 새 기능 추가 방법:
class EmailNotifier:
    def send_receipt(self, email: str, total: int) -> None:
        print(f"영수증 발송: {email}, {total}원")

class SlackNotifier:
    def send_receipt(self, email: str, total: int) -> None:
        print(f"Slack 알림: {email}, {total}원")

# AI에게 이렇게 요청하세요:
# "CheckoutService에서 이메일 대신 Slack 알림을 쓰도록 수정해 줘"
# -> AI는 SlackNotifier를 주입하는 방식으로 변경해 줌

# 합성 패턴이면 기존 코드를 거의 수정하지 않아도 됨
```

## 체크리스트

- [ ] is-a 관계와 has-a 관계를 구분할 수 있다
- [ ] 합성과 위임 패턴을 구현할 수 있다
- [ ] 의존성 주입의 목적과 구현 방법을 이해한다
- [ ] AI가 생성자에 인터페이스를 주입받는 이유를 설명할 수 있다
- [ ] 상속이 적절한 경우와 합성이 적절한 경우를 판단할 수 있다

## 처음 질문으로 돌아가기

- **is-a와 has-a 관계를 어떻게 구분할까요?**
  "A는 B의 일종인가?"라고 물어보세요. `Dog`는 `Animal`의 일종(is-a)입니다. `UserService`는 `Logger`의 일종이 아닙니다(not is-a). 확신이 없으면 합성을 선택합니다.

- **왜 합성이 더 안전한 기본 선택일까요?**
  합성은 내부 객체를 교체할 수 있어 테스트와 유지보수가 쉽습니다. 상속은 부모-자식 간 강한 결합이 생겨 부모 변경이 자식 전체에 영향을 줍니다.

- **의존성 주입은 어떻게 합성을 극대화할까요?**
  생성자에서 의존성을 받으면 외부에서 구현을 교체할 수 있습니다. 테스트할 때는 가짜 구현을 주입하고, 프로덕션에서는 실제 구현을 주입합니다. AI가 이 패턴을 만드는 이유입니다.

## 정리

합성은 느슨한 결합과 런타임 유연성을 제공합니다. AI가 생성자에서 의존성을 주입받는 코드를 만들면 "테스트와 교체가 쉽도록 설계했다"는 의미입니다. 상속은 is-a 관계가 명확한 곳에서만 사용합니다. 다음 글에서는 SOLID 원칙이 왜 필요한지와 AI 코드에서 이 원칙들을 어떻게 식별하는지 알아봅니다.

## 참고 자료

- [Design Patterns — GoF (Gang of Four)](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- **바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 합성, 상속, 바이브코딩, 설계 패턴
