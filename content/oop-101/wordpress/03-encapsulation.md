---
title: "바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화"
series: oop-101
episode: 3
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 캡슐화
  - 바이브코딩
  - Property
  - 정보 은닉
last_reviewed: '2026-06-18'
seo_description: AI가 생성한 코드에서 밑줄 관례와 property 패턴이 나오는 이유를 설명합니다. 바이브코딩 관점에서 캡슐화를 이해합니다.
---

# 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 세 번째 글입니다.

---

AI에게 계좌 관리 클래스를 만들어 달라고 하면 `self._balance`처럼 밑줄이 붙은 변수가 나옵니다. `@property` 데코레이터가 붙은 메서드도 등장합니다. `account.balance`로 읽을 수는 있는데 `account.balance = -500`을 하면 에러가 납니다. 왜 이렇게 만들었을까요?

AI가 이 패턴을 쓰는 이유는 **객체 상태를 보호하기 위해서**입니다. 잔액이 음수가 되면 안 되는데, 외부에서 `account.balance = -500`을 아무 제약 없이 할 수 있다면 버그가 생깁니다. 캡슐화는 값을 숨기는 장식이 아니라 상태를 지키기 위한 계약입니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다. 캡슐화는 그 이유 중 하나입니다.

> "AI가 `_balance` 앞에 밑줄을 붙였다면, '직접 건드리지 말라'는 신호입니다. 그 신호를 무시하면 예상치 못한 버그가 생깁니다."

## 이 글에서 다룰 문제

- Python에서 `_protected`와 `__private` 관례는 각각 어떤 의미인가요?
- `@property`는 단순 getter/setter 문법을 넘어 어떤 설계 이점을 줄까요?
- AI가 만든 클래스에서 `@property`를 보면 어떻게 이해해야 할까요?
- 유효성 검증을 속성 접근에 녹이면 왜 버그가 줄어들까요?
- 캡슐화를 과하게 적용하면 어떤 문제가 생길까요?

## 핵심 개념 잡기

Python의 접근 제어는 이름 관례로 표현합니다.

```text
Naming Pattern           Access Level
─────────────────────────────────────
name                    public — 누구나 접근 가능
_name                   protected — 내부/하위 클래스용 (관례)
__name                  private — 이름 맹글링 적용 (_Class__name)
__name__                dunder — Python 내장 프로토콜
```

| 용어 | 설명 |
|------|------|
| 캡슐화(encapsulation) | 데이터와 메서드를 묶고 내부 구현을 숨기는 원칙입니다 |
| 정보 은닉(information hiding) | 내부 상태를 외부에서 직접 접근할 수 없게 하는 것입니다 |
| property | Python 내장 데코레이터로 속성 접근을 메서드로 제어합니다 |
| getter/setter | 속성 값을 읽거나 설정할 때 호출되는 메서드입니다 |

## Before / After: AI가 property를 추가하는 이유

```python
# Before: 직접 접근 — 잘못된 상태가 가능함
class BankAccount:
    def __init__(self, balance):
        self.balance = balance  # 아무나 변경 가능

account = BankAccount(1000)
account.balance = -500  # 음수 잔액이 허용됨 — 버그
```

```python
# After: property 보호 — 유효성 검증이 자동으로 적용됨
class BankAccount:
    def __init__(self, balance: int) -> None:
        self._balance = balance  # 직접 접근 비권장

    @property
    def balance(self) -> int:
        return self._balance  # 읽기는 허용

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("잔액 부족")
        self._balance -= amount

account = BankAccount(1000)
account.deposit(500)    # 1500
account.withdraw(200)   # 1300
# account.balance = -500  # AttributeError — setter가 없으므로 오류
```

`@property`를 쓰면 `account.balance`는 읽기는 되지만 직접 쓰기는 안 됩니다. 잔액 변경은 반드시 `deposit()`이나 `withdraw()` 메서드를 통해야 합니다. 검증 로직이 한 곳에 모입니다.

## 바이브코딩 관점: AI가 `_` 밑줄을 붙이는 이유

AI가 `self._balance`처럼 밑줄을 붙이면 "외부에서 직접 건드리지 말라"는 신호입니다. Python에는 강제 접근 제한이 없지만, 이 관례를 지키면 의도하지 않은 수정을 방지할 수 있습니다.

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius  # 직접 접근 비권장

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"반지름은 양수여야 합니다: {value}")
        self._radius = value

    @property
    def area(self) -> float:
        """읽기 전용 계산 속성"""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)   # 5
print(c.area)     # 78.539...

c.radius = 10     # setter를 통한 검증 있는 변경
# c.radius = -1   # ValueError 발생
# c.area = 100    # AttributeError — 읽기 전용
```

`@property`만 있고 `@radius.setter`가 없으면 읽기 전용 속성이 됩니다. AI가 만든 클래스에서 setter 없는 property를 보면 "이 값은 외부에서 변경하면 안 된다"는 의도입니다.

## 실전 패턴: 생성자에서 setter를 통한 검증

AI가 종종 만드는 패턴 중 하나입니다.

```python
class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name    # setter를 통해 검증이 자동으로 적용됨
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("이름은 비어있을 수 없습니다")
        self._name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError(f"유효하지 않은 이메일: {value}")
        self._email = value

user = User("Alice", 30, "alice@example.com")
print(user.name)   # Alice
# user.email = "invalid"  # ValueError 발생
```

`__init__`에서 `self.name = name`을 하면 setter가 자동으로 호출됩니다. 덕분에 생성 시점부터 유효성 검증이 보장됩니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 속성을 `__`로 만듦 | 상속 시 하위 클래스에서 접근 불가합니다 | `_` 관례로 충분합니다 |
| property에서 무거운 계산 | 속성 접근마다 비용이 발생합니다 | 무거운 연산은 메서드로 분리합니다 |
| setter 없이 `__init__`에서 직접 할당 | 유효성 검증을 우회합니다 | `__init__`에서도 setter를 사용합니다 |
| 이름 맹글링을 보안으로 오해 | `_Class__name`으로 접근 가능합니다 | 관례적 보호이며 강제가 아닙니다 |
| getter/setter만 있는 property | Java 스타일 보일러플레이트입니다 | 검증이나 계산이 없으면 public 속성을 사용합니다 |

## AI 팁: AI 코드에서 캡슐화 패턴 읽기

AI가 만든 클래스에서 캡슐화 패턴을 파악하는 방법입니다.

```python
# 이런 패턴이 보이면 다음을 확인하세요:

# 1. _로 시작하는 속성: 직접 접근을 피해야 함
self._balance = 0

# 2. @property만 있고 setter 없음: 읽기 전용
@property
def balance(self) -> int:
    return self._balance

# 3. @property + setter: 검증이 포함된 변경 허용
@balance.setter
def balance(self, value: int) -> None:
    if value < 0:
        raise ValueError("잔액은 음수일 수 없습니다")
    self._balance = value

# AI에게 물어보세요:
# "이 클래스에서 외부에서 직접 변경하면 안 되는 속성은 무엇인가?"
# "이 property의 setter가 없는 이유는 무엇인가?"
```

## 체크리스트

- [ ] `_`와 `__` 관례의 차이를 설명할 수 있다
- [ ] `@property` 데코레이터로 getter/setter를 구현할 수 있다
- [ ] 읽기 전용 속성을 만들 수 있다
- [ ] `__init__`에서 setter를 통한 검증 패턴을 이해한다
- [ ] AI 코드에서 캡슐화 패턴을 식별할 수 있다

## 처음 질문으로 돌아가기

- **`_protected`와 `__private` 관례는 어떻게 받아들이면 될까요?**
  `_`는 "내부 구현이니 직접 건드리지 마세요"라는 관례입니다. `__`는 이름 맹글링이 적용되어 실수로 덮어쓰기를 방지합니다. AI가 `_balance`를 쓰면 "이 변수는 메서드를 통해 접근하라"는 의도입니다.

- **`@property`는 어떤 설계 이점을 줄까요?**
  속성 접근 시 자동으로 검증이 적용됩니다. 나중에 공개 속성을 property로 바꿔도 호출자 코드를 수정할 필요가 없습니다. AI가 처음부터 property를 쓰는 이유입니다.

- **캡슐화를 과하게 적용하면 어떤 문제가 생길까요?**
  검증이나 계산이 없는 단순 속성에 property를 쓰면 코드가 불필요하게 복잡해집니다. AI가 `@property`를 쓸 때는 이유가 있습니다. 이유가 명확하지 않다면 AI에게 "이 property가 필요한 이유가 무엇인가?"라고 물어보세요.

## 정리

캡슐화는 객체 내부 상태를 보호하는 원칙입니다. Python에서는 밑줄 관례와 `@property`로 구현합니다. AI가 이 패턴을 쓸 때는 "외부에서 직접 변경하면 버그가 생길 수 있다"는 신호입니다. 다음 글에서는 상속을 통해 기존 클래스를 확장하는 방법과 AI가 상속 계층을 만드는 기준을 알아봅니다.

## 참고 자료

- [Python 공식 문서 — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- **바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 캡슐화, 바이브코딩, Property, 정보 은닉
