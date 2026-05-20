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

## 먼저 던지는 질문

- 상속이 코드 중복을 줄일 수는 있지만, 왜 동시에 강한 결합도 만들까요?
- 오버라이딩과 `super()`는 어떤 식으로 함께 써야 안전할까요?
- `isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?

## 큰 그림

![Object-Oriented Programming 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/04/04-01-concept-overview.ko.png)

*Object-Oriented Programming 101 4장 흐름 개요*

이 그림에서는 상속를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 상속의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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
# before: no inheritance — duplicated code
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
# after: inheritance consolidates common logic
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

## 처음 질문으로 돌아가기

- **상속이 코드 중복을 줄일 수는 있지만, 왜 동시에 강한 결합도 만들까요?**
  - 본문의 기준은 상속를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **오버라이딩과 `super()`는 어떤 식으로 함께 써야 안전할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Python, OOP, 상속, 메서드 오버라이딩, super
