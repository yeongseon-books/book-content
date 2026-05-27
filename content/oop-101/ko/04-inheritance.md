---
title: "Object-Oriented Programming 101 (4/10): 상속"
series: oop-101
episode: 4
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
  - 상속
  - 메서드 오버라이딩
  - super
last_reviewed: '2026-05-15'
seo_description: Python 상속, 오버라이딩, super(), MRO를 실무 기준으로 이해하기 쉽게 정리합니다.
---

# Object-Oriented Programming 101 (4/10): 상속

상속은 객체지향에서 가장 먼저 배우는 기능이지만, 현업에서는 가장 쉽게 남용되는 기능이기도 합니다. 공통 코드가 보이면 부모 클래스로 올리고 싶어지지만, 그 공통점이 정말 타입 관계인지 확인하지 않으면 계층만 깊어지고 변경 비용이 빠르게 커집니다.

그래서 상속을 볼 때는 재사용보다 관계를 먼저 봐야 합니다. 자식 객체를 부모 타입이 필요한 모든 자리에 무리 없이 넣을 수 있는가, 그리고 부모의 변경이 자식 전체를 흔들 위험을 감수할 만한가를 먼저 따져야 합니다.

이 글은 OOP 101 시리즈의 4번째 글입니다.


![Object-Oriented Programming 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/04/04-01-concept-overview.ko.png)
*Object-Oriented Programming 101 4장 흐름 개요*

## 먼저 던지는 질문

- 상속이 코드 중복을 줄일 수는 있지만, 왜 동시에 강한 결합도 만들까요?
- 오버라이딩과 `super()`는 어떤 식으로 함께 써야 안전할까요?
- `isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?

## 핵심 개념 잡기

> 상속 계층 구조

```text
Animal (parent class)
├── name, sound
├── speak()
├── __repr__()
│
├── Dog (child class)
│   └── speak() overridden
│   └── fetch() added
│
└── Cat (child class)
    └── speak() overridden
    └── purr() added
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 부모 클래스(parent/base) | 속성과 메서드를 물려주는 기존 클래스입니다 |
| 자식 클래스(child/derived) | 부모를 상속받아 확장하는 새 클래스입니다 |
| 오버라이딩(overriding) | 부모의 메서드를 자식에서 재정의하는 것입니다 |
| `super()` | 부모 클래스의 메서드를 호출하는 내장 함수입니다 |
| MRO(Method Resolution Order) | 다중 상속에서 메서드 탐색 순서입니다 |

## 전후 비교

도형 클래스의 코드 중복을 제거합니다.

```python
# before: inheritance 없음 — 코드 중복 발생
class Circle:
    def __init__(self, name, color, radius):
        self.name = name
        self.color = color
        self.radius = radius

    def describe(self):
        return f"{self.color} {self.name}"

class Square:
    def __init__(self, name, color, side):
        self.name = name      # duplicated
        self.color = color    # duplicated
        self.side = side

    def describe(self):       # duplicated
        return f"{self.color} {self.name}"
```

```python
# after: inheritance로 공통 로직 통합
class Shape:
    def __init__(self, name: str, color: str) -> None:
        self.name = name
        self.color = color

    def describe(self) -> str:
        return f"{self.color} {self.name}"

class Circle(Shape):
    def __init__(self, color: str, radius: float) -> None:
        super().__init__("circle", color)
        self.radius = radius

class Square(Shape):
    def __init__(self, color: str, side: float) -> None:
        super().__init__("square", color)
        self.side = side
```

## 단계별 실습

### 1단계: 기본 상속

```python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name}: {self.sound}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"

class Dog(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "woof")

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}"

class Cat(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "meow")

    def purr(self) -> str:
        return f"{self.name} is purring"

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())   # Buddy: woof
print(cat.speak())   # Whiskers: meow
print(dog.fetch("ball"))  # Buddy fetches the ball
```

### 2단계: 메서드 오버라이딩

```python
class Logger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}")

class TimestampLogger(Logger):
    def log(self, message: str) -> None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def error(self, message: str) -> None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")

logger = TimestampLogger()
logger.log("Server started")    # [2026-05-04 12:00:00] Server started
logger.error("Connection failed")  # [2026-05-04 12:00:00] ERROR: Connection failed
```

### 3단계: super()로 부모 기능 확장

```python
class Vehicle:
    def __init__(self, make: str, model: str, year: int) -> None:
        self.make = make
        self.model = model
        self.year = year

    def info(self) -> str:
        return f"{self.year} {self.make} {self.model}"

class ElectricVehicle(Vehicle):
    def __init__(self, make: str, model: str, year: int, battery_kwh: float) -> None:
        super().__init__(make, model, year)
        self.battery_kwh = battery_kwh

    def info(self) -> str:
        base = super().info()
        return f"{base} (Battery: {self.battery_kwh}kWh)"

ev = ElectricVehicle("Tesla", "Model 3", 2026, 75.0)
print(ev.info())  # 2026 Tesla Model 3 (Battery: 75.0kWh)
```

### 4단계: isinstance과 issubclass

```python
dog = Dog("Buddy")
cat = Cat("Whiskers")

print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog is a kind of Animal
print(isinstance(dog, Cat))     # False

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Animal))  # True
print(issubclass(Dog, Cat))     # False

animals: list[Animal] = [Dog("Buddy"), Cat("Whiskers"), Dog("Max")]
for animal in animals:
    print(animal.speak())
# Buddy: woof
# Whiskers: meow
# Max: woof
```

### 5단계: 다중 상속과 MRO

```python
class Flyable:
    def fly(self) -> str:
        return f"{self.name} is flying"

class Swimmable:
    def swim(self) -> str:
        return f"{self.name} is swimming"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name: str) -> None:
        super().__init__(name, "quack")

duck = Duck("Donald")
print(duck.speak())  # Donald: quack
print(duck.fly())    # Donald is flying
print(duck.swim())   # Donald is swimming

# Check MRO
print(Duck.__mro__)
# (Duck, Animal, Flyable, Swimmable, object)
```

## 이 코드에서 주목할 점

- `super().__init__()`은 부모 클래스의 초기화를 호출하여 속성을 설정합니다
- 오버라이딩 시 `super().method()`로 부모의 원래 동작을 유지하면서 확장합니다
- `isinstance()`은 상속 계층 전체를 검사하여 다형적 코드를 지원합니다
- MRO는 C3 선형화 알고리즘으로 결정되며 `__mro__`로 확인합니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `super().__init__()` 호출 누락 | 부모 속성이 초기화되지 않습니다 | 자식의 `__init__`에서 반드시 호출합니다 |
| 상속 깊이가 4단계 이상 | 디버깅과 이해가 어려워집니다 | 2~3단계로 제한하고 합성을 고려합니다 |
| "has-a" 관계에 상속 사용 | 자동차는 엔진의 "일종"이 아닙니다 | 합성(composition)을 사용합니다 |
| 다중 상속 남용 | MRO가 복잡해지고 다이아몬드 문제 발생입니다 | 믹스인(mixin) 패턴으로 제한합니다 |
| 부모 클래스의 내부 구현에 의존 | 부모 변경 시 자식이 깨집니다 | 부모의 공개 인터페이스만 사용합니다 |

## 실무에서 이렇게 쓰입니다

- Django의 `View` → `ListView` → `DetailView` 상속 계층으로 웹 뷰를 구현합니다
- Python의 `Exception` 계층으로 커스텀 에러를 정의합니다
- unittest의 `TestCase`를 상속하여 테스트 클래스를 작성합니다
- 로깅 핸들러를 상속하여 커스텀 로그 출력을 구현합니다
- ABC(Abstract Base Class)를 상속하여 인터페이스를 정의합니다

## 현업 개발자는 이렇게 생각합니다

상속은 강력하지만 가장 남용되기 쉬운 OOP 기능입니다. "이 관계가 정말 is-a인가?"라는 질문에 확신이 없으면 합성을 선택하는 것이 안전합니다.

실무에서는 상속보다 합성을 선호하는 추세입니다. 상속은 프레임워크가 제공하는 확장 포인트(Django View, Exception 등)에서 주로 사용하고, 비즈니스 로직에서는 합성과 인터페이스를 활용합니다.

## 이런 신호가 보이면 상속을 다시 의심합니다

| 신호 | 실제로 생기는 문제 | 먼저 해볼 리팩터링 |
|------|-------------------|--------------------|
| 자식 클래스마다 부모 메서드의 절반 이상을 덮어씀 | 공통 기반 클래스가 더 이상 공통이 아닙니다 | 공통 인터페이스만 남기고 합성이나 전략 패턴으로 분리합니다 |
| 부모 클래스에 옵션 플래그가 계속 늘어남 | `if self.kind == ...` 같은 분기가 부모 안에 쌓입니다 | 부모를 얇게 만들고 변하는 동작을 별도 객체로 뺍니다 |
| 특정 자식만 초기화 순서 예외가 많음 | `super()` 호출 규칙이 깨져 디버깅이 어려워집니다 | 생성 책임을 팩토리나 조립 코드로 이동합니다 |
| 부모 타입으로 받았는데 자식마다 사용 가능한 메서드가 다름 | 리스코프 치환 원칙이 흔들려 호출부가 타입 검사로 돌아갑니다 | 상속 계층을 나누거나, 공통 계약을 더 작은 인터페이스로 재정의합니다 |

## 체크리스트

- [ ] 단일 상속으로 부모 클래스를 확장할 수 있다
- [ ] `super()`로 부모 메서드를 호출할 수 있다
- [ ] 메서드 오버라이딩의 동작 원리를 이해한다
- [ ] `isinstance()`와 `issubclass()`를 활용할 수 있다
- [ ] 다중 상속의 MRO를 확인하고 이해할 수 있다

## 정리 및 다음 글 안내

상속은 코드 재사용과 계층적 관계 표현에 유용하지만, 남용하면 복잡성을 증가시킵니다. 다음 글에서는 다형성을 통해 같은 인터페이스로 다른 동작을 구현하는 방법을 알아봅니다.

## 상속은 코드 재사용 도구가 아니라 타입 관계 선언입니다

상속이 효과적인 경우는 `is-a` 관계가 분명하고, 하위 타입이 상위 계약을 깨지 않을 때입니다.

```text
[Notification]
  + send(message)
     ^
     |
+----+-------------------+
|                        |
[EmailNotification]   [SlackNotification]
```

## 적용 전후: 잘못된 상속에서 역할 분리로

```python
# before
class Report:
    def generate(self) -> str:
        return 'csv data'

class EmailReport(Report):
    def generate(self) -> str:
        data = super().generate()
        # 전송까지 담당
        return f'sent:{data}'
```

```python
# after
class Report:
    def generate(self) -> str:
        return 'csv data'

class EmailSender:
    def send(self, payload: str) -> str:
        return f'sent:{payload}'

class ReportDeliveryService:
    def __init__(self, report: Report, sender: EmailSender) -> None:
        self.report = report
        self.sender = sender

    def deliver(self) -> str:
        return self.sender.send(self.report.generate())
```

상속 계층 하나로 생성과 전송 책임을 묶으면 SRP 위반이 발생합니다. 생성과 전달을 분리하면 테스트와 확장이 쉬워집니다.

## LSP 위반 예시와 교정

```python
class Bird:
    def fly(self) -> str:
        return 'flying'

class Penguin(Bird):
    def fly(self) -> str:
        raise RuntimeError('cannot fly')
```

이 구조는 하위 타입이 상위 타입 계약을 깨므로 LSP 위반입니다.

```python
from typing import Protocol

class Swimmable(Protocol):
    def swim(self) -> str:
        ...

class Flyable(Protocol):
    def fly(self) -> str:
        ...
```

능력 기반 인터페이스로 분리하면 억지 상속을 피할 수 있습니다.

## 비교표: 상속과 조합

| 기준 | 상속 | 조합 |
|---|---|---|
| 런타임 교체 | 어려움 | 쉬움 |
| 결합도 | 계층 결합 큼 | 인터페이스 결합 |
| 변경 영향 | 상위 변경 파급 큼 | 구성 객체 단위 국소화 |
| 테스트 대체 | 상속 트리 준비 필요 | 목 객체 주입 단순 |

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


## 추가 비교표: 설계 결정 매트릭스

| 상황 | 권장 구조 | 피해야 할 선택 |
|---|---|---|
| 규칙이 자주 바뀜 | 정책 객체 분리 + 주입 | 하드코딩 분기 누적 |
| 상태 전이가 핵심 | 메서드 기반 전이 모델 | 외부에서 필드 직접 변경 |
| 외부 연동 잦음 | 포트/어댑터 분리 | 도메인에서 SDK 직접 호출 |
| 팀 온보딩 필요 | UML 텍스트와 용어 사전 유지 | 암묵 규칙 의존 |

이 매트릭스는 설계 정답을 고정하려는 목적이 아닙니다. 같은 팀 내에서 판단 언어를 통일해 코드 리뷰 시간을 줄이는 데 목적이 있습니다.

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


## 추가 코드 예시: 규칙 변경을 메서드로 고립

```python
class Membership:
    def __init__(self, level: str) -> None:
        self.level = level

    def discount_rate(self) -> int:
        if self.level == 'gold':
            return 20
        if self.level == 'silver':
            return 10
        return 0


class PriceCalculator:
    def __init__(self, membership: Membership) -> None:
        self.membership = membership

    def final_price(self, amount: int) -> int:
        rate = self.membership.discount_rate()
        return int(amount * (100 - rate) / 100)
```

이 구조에서 멤버십 정책이 바뀌면 `Membership` 구현만 수정하면 됩니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 짧은 리마인더

객체지향을 적용할 때는 "클래스를 몇 개 만들었는가"보다 "다음 변경에서 몇 파일을 수정해야 하는가"를 기준으로 품질을 평가합니다.

## 처음 질문으로 돌아가기

- **상속이 코드 중복을 줄일 수는 있지만, 왜 동시에 강한 결합도 만들까요?**
  - `Shape`가 `name`과 `color`를 공통으로 올려 `Circle`과 `Square`의 중복을 줄인 것은 분명한 이점이지만, 그만큼 자식은 부모 초기화 방식과 공개 인터페이스에 묶입니다. 글 후반의 `Penguin(Bird)` 예제와 `ReportDeliveryService` 리팩터링은 공통 코드만 보고 상속을 택하면 LSP 위반이나 책임 혼합으로 바로 되돌아온다는 점을 보여 주었습니다.
- **오버라이딩과 `super()`는 어떤 식으로 함께 써야 안전할까요?**
  - `ElectricVehicle.info()`는 부모의 `info()`를 `super()`로 먼저 호출한 뒤 배터리 정보만 덧붙여서, 기존 계약을 유지하면서 확장하는 안전한 패턴을 보여 줍니다. 반대로 자식이 부모 초기화나 기본 동작을 통째로 우회하면 `super().__init__()` 누락, 오버라이드 중복, 초기화 순서 꼬임이 생기므로, 본문은 부모 기능을 재사용하고 추가 책임만 덧붙이는 방식을 권장했습니다.
- **`isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?**
  - `Dog`가 `Animal` 목록 안에서 `speak()`를 호출받는 예제는, 런타임에서 실제 객체가 부모 계약을 만족하는지 읽는 데 `isinstance()`가 왜 필요한지 잘 보여 줍니다. 또한 `issubclass(Dog, Animal)`과 `Duck.__mro__` 확인은 계층을 그냥 믿지 말고 메서드 탐색과 타입 관계를 코드로 검증하라는 실무 감각을 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- **상속 (현재 글)**
- 다형성 (예정)
- 추상화 (예정)
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Python MRO 공식 문서](https://docs.python.org/3/library/stdtypes.html#class.__mro__)
- [Effective Python — Item 40: Initialize Parent Classes with super](https://effectivepython.com/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 상속, 메서드 오버라이딩, super
