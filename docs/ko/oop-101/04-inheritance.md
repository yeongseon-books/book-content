---
series: oop-101
episode: 4
title: 상속
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
  - 상속
  - 메서드 오버라이딩
  - super
seo_description: Python 상속의 기본 구조, 메서드 오버라이딩, super() 활용법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 상속

> Object-Oriented Programming 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 기존 클래스의 기능을 재사용하면서 새로운 기능을 추가하려면 어떻게 해야 할까요?

> 상속은 기존 클래스(부모)의 속성과 메서드를 새로운 클래스(자식)가 물려받는 메커니즘입니다. 코드 중복을 줄이고 계층적 관계를 표현합니다. 이 글에서는 단일 상속, 메서드 오버라이딩, `super()`, 다중 상속과 MRO까지 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 단일 상속의 기본 구조와 활용
- 메서드 오버라이딩과 `super()` 호출
- `isinstance()`와 `issubclass()` 활용
- 다중 상속과 MRO(Method Resolution Order)

## 왜 중요한가

비슷한 기능을 가진 여러 클래스를 만들 때 상속 없이는 같은 코드를 반복해야 합니다. 상속을 사용하면 공통 로직을 부모 클래스에 한 번만 작성하고, 자식 클래스에서 차이점만 구현합니다.

> 상속 = "is-a" 관계: 자식 클래스는 부모 클래스의 일종이다

다만, 상속은 강한 결합을 만듭니다. 부모 클래스가 변경되면 모든 자식 클래스에 영향을 미칩니다. 상속이 적절한 경우와 그렇지 않은 경우를 구분하는 것이 중요합니다.

## 핵심 개념 잡기

> 상속 계층 구조

```
Animal (부모 클래스)
├── name, sound
├── speak()
├── __repr__()
│
├── Dog (자식 클래스)
│   └── speak() 오버라이딩
│   └── fetch() 추가
│
└── Cat (자식 클래스)
    └── speak() 오버라이딩
    └── purr() 추가
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 부모 클래스(parent/base) | 속성과 메서드를 물려주는 기존 클래스입니다 |
| 자식 클래스(child/derived) | 부모를 상속받아 확장하는 새 클래스입니다 |
| 오버라이딩(overriding) | 부모의 메서드를 자식에서 재정의하는 것입니다 |
| `super()` | 부모 클래스의 메서드를 호출하는 내장 함수입니다 |
| MRO(Method Resolution Order) | 다중 상속에서 메서드 탐색 순서입니다 |

## Before / After

도형 클래스의 코드 중복을 제거합니다.

```python
# before: 상속 없이 — 중복 코드
class Circle:
    def __init__(self, name, color, radius):
        self.name = name
        self.color = color
        self.radius = radius

    def describe(self):
        return f"{self.color} {self.name}"

class Square:
    def __init__(self, name, color, side):
        self.name = name      # 중복
        self.color = color    # 중복
        self.side = side

    def describe(self):       # 중복
        return f"{self.color} {self.name}"
```

```python
# after: 상속으로 공통 로직 통합
class Shape:
    def __init__(self, name: str, color: str) -> None:
        self.name = name
        self.color = color

    def describe(self) -> str:
        return f"{self.color} {self.name}"

class Circle(Shape):
    def __init__(self, color: str, radius: float) -> None:
        super().__init__("원", color)
        self.radius = radius

class Square(Shape):
    def __init__(self, color: str, side: float) -> None:
        super().__init__("사각형", color)
        self.side = side
```

## 단계별 실습

### Step 1: 기본 상속

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
        super().__init__(name, "멍멍")

    def fetch(self, item: str) -> str:
        return f"{self.name}이(가) {item}을(를) 가져옵니다"


class Cat(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "야옹")

    def purr(self) -> str:
        return f"{self.name}이(가) 그르릉거립니다"


dog = Dog("바둑이")
cat = Cat("나비")
print(dog.speak())   # 바둑이: 멍멍
print(cat.speak())   # 나비: 야옹
print(dog.fetch("공"))  # 바둑이이(가) 공을(를) 가져옵니다
```

### Step 2: 메서드 오버라이딩

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
logger.log("서버 시작")    # [2026-05-04 12:00:00] 서버 시작
logger.error("연결 실패")  # [2026-05-04 12:00:00] ERROR: 연결 실패
```

### Step 3: super()로 부모 기능 확장

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
        return f"{base} (배터리: {self.battery_kwh}kWh)"


ev = ElectricVehicle("Tesla", "Model 3", 2026, 75.0)
print(ev.info())  # 2026 Tesla Model 3 (배터리: 75.0kWh)
```

### Step 4: isinstance과 issubclass

```python
dog = Dog("바둑이")
cat = Cat("나비")

print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog은 Animal의 일종
print(isinstance(dog, Cat))     # False

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Animal))  # True
print(issubclass(Dog, Cat))     # False

animals: list[Animal] = [Dog("바둑이"), Cat("나비"), Dog("초코")]
for animal in animals:
    print(animal.speak())
# 바둑이: 멍멍
# 나비: 야옹
# 초코: 멍멍
```

### Step 5: 다중 상속과 MRO

```python
class Flyable:
    def fly(self) -> str:
        return f"{self.name}이(가) 날아갑니다"

class Swimmable:
    def swim(self) -> str:
        return f"{self.name}이(가) 수영합니다"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name: str) -> None:
        super().__init__(name, "꽥꽥")

duck = Duck("도날드")
print(duck.speak())  # 도날드: 꽥꽥
print(duck.fly())    # 도날드이(가) 날아갑니다
print(duck.swim())   # 도날드이(가) 수영합니다

# MRO 확인
print(Duck.__mro__)
# (Duck, Animal, Flyable, Swimmable, object)
```

## 이 코드에서 주목할 점

- `super().__init__()`은 부모 클래스의 초기화를 호출하여 속성을 설정합니다
- 오버라이딩 시 `super().method()`로 부모의 원래 동작을 유지하면서 확장합니다
- `isinstance()`은 상속 계층 전체를 검사하여 다형적 코드를 지원합니다
- MRO는 C3 선형화 알고리즘으로 결정되며 `__mro__`로 확인합니다

## 흔한 실수 5가지

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

## 시니어 엔지니어는 이렇게 생각합니다

- **LSP 준수** — 하위 타입은 상위 계약을 깨지 않아야 합니다.
- **얕은 계층** — 2단 이상 깊어지면 합성을 검토합니다.
- **MRO** — 다중 상속은 MRO를 정확히 이해한 뒤에만 씁니다.
- **상속보다 합성** — 기본은 합성, 예외만 상속입니다.
- **Mixin 절제** — Mixin은 명확한 책임 한 가지로 제한합니다.

## 체크리스트

- [ ] 단일 상속으로 부모 클래스를 확장할 수 있다
- [ ] `super()`로 부모 메서드를 호출할 수 있다
- [ ] 메서드 오버라이딩의 동작 원리를 이해한다
- [ ] `isinstance()`와 `issubclass()`를 활용할 수 있다
- [ ] 다중 상속의 MRO를 확인하고 이해할 수 있다

## 연습 문제

1. `Shape` → `Rectangle` → `Square` 상속 계층을 만들고 넓이 메서드를 구현하세요.
2. `LogHandler` 부모 클래스를 만들고 `FileHandler`, `ConsoleHandler` 자식 클래스를 구현하세요.
3. `Serializable`과 `Printable` 믹스인을 만들어 `Document` 클래스에서 다중 상속하세요.

## 정리 및 다음 글 안내

상속은 코드 재사용과 계층적 관계 표현에 유용하지만, 남용하면 복잡성을 증가시킵니다. 다음 글에서는 다형성을 통해 같은 인터페이스로 다른 동작을 구현하는 방법을 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- **상속 (현재 글)**
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Python MRO 공식 문서](https://docs.python.org/3/library/stdtypes.html#class.__mro__)
- [Effective Python — Item 40: Initialize Parent Classes with super](https://effectivepython.com/)
