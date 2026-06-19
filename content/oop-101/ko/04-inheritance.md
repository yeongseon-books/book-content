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

## 이 글에서 다룰 문제

- 상속이 코드 중복을 줄일 수는 있지만, 왜 동시에 강한 결합도 만들까요?
- 오버라이딩과 `super()`는 어떤 식으로 함께 써야 안전할까요?
- `isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- 단일 상속과 다중 상속의 구조적 차이를 이해합니다
- `super()`와 메서드 오버라이딩을 안전하게 조합하는 패턴을 익힙니다
- MRO(Method Resolution Order)가 다중 상속에서 어떻게 작동하는지 확인합니다
- `isinstance()`와 `issubclass()`로 타입 관계를 검사하는 방법을 배웁니다
- 상속 남용을 피하고 합성(composition)을 고려할 타이밍을 파악합니다

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
# before: 상속 없음 — 공통 코드가 중복됨
class Circle:
    def __init__(self, name, color, radius):
        self.name = name
        self.color = color
        self.radius = radius

    def describe(self):
        return f"{self.name} ({self.color})"

class Rectangle:
    def __init__(self, name, color, width, height):
        self.name = name
        self.color = color
        self.width = width
        self.height = height

    def describe(self):
        return f"{self.name} ({self.color})"
```

```python
# after: 상속으로 공통 속성과 메서드를 부모에서 관리
class Shape:
    def __init__(self, name: str, color: str) -> None:
        self.name = name
        self.color = color

    def describe(self) -> str:
        return f"{self.name} ({self.color})"

    def area(self) -> float:
        raise NotImplementedError("Subclasses must implement area()")

class Circle(Shape):
    def __init__(self, name: str, color: str, radius: float) -> None:
        super().__init__(name, color)
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, name: str, color: str, width: float, height: float) -> None:
        super().__init__(name, color)
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

shapes = [Circle("Circle A", "red", 5), Rectangle("Rect B", "blue", 4, 6)]
for s in shapes:
    print(f"{s.describe()}: area = {s.area():.2f}")
```

`super().__init__(name, color)`를 호출하면 부모의 초기화 로직을 재사용합니다. 자식은 자신만의 속성(radius, width, height)만 추가하면 됩니다.

## 단계별 실습

### 1단계: 기본 상속과 오버라이딩

```python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}!"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"

class Dog(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "woof")

    def speak(self) -> str:
        base = super().speak()
        return f"{base} (tail wagging)"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}!"

class Cat(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "meow")

    def purr(self) -> str:
        return f"{self.name} purrs..."

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())      # Buddy says woof! (tail wagging)
print(cat.speak())      # Whiskers says meow!
print(dog.fetch("ball"))  # Buddy fetches the ball!
```

### 2단계: isinstance와 issubclass

```python
animals: list[Animal] = [Dog("Rex"), Cat("Luna"), Dog("Max")]

for animal in animals:
    print(f"{animal}: is Animal? {isinstance(animal, Animal)}")
    if isinstance(animal, Dog):
        print(f"  {animal.fetch('stick')}")

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Dog))     # False

# isinstance는 상속 체인 전체를 검사합니다
class GoldenRetriever(Dog):
    pass

gr = GoldenRetriever("Charlie")
print(isinstance(gr, Dog))     # True
print(isinstance(gr, Animal))  # True
```

### 3단계: super()로 부모 로직 확장

```python
class Vehicle:
    def __init__(self, make: str, model: str, year: int) -> None:
        self.make = make
        self.model = model
        self.year = year

    def describe(self) -> str:
        return f"{self.year} {self.make} {self.model}"

    def start(self) -> str:
        return "Engine started"

class ElectricVehicle(Vehicle):
    def __init__(self, make: str, model: str, year: int, battery_kwh: float) -> None:
        super().__init__(make, model, year)
        self.battery_kwh = battery_kwh
        self._charge_level = 100.0

    def describe(self) -> str:
        base = super().describe()
        return f"{base} (EV, {self.battery_kwh}kWh)"

    def start(self) -> str:
        return "Silent motor activated"

    def charge_status(self) -> str:
        return f"Battery: {self._charge_level:.0f}%"

ev = ElectricVehicle("Tesla", "Model 3", 2024, 75)
print(ev.describe())       # 2024 Tesla Model 3 (EV, 75kWh)
print(ev.start())          # Silent motor activated
print(ev.charge_status())  # Battery: 100%
```

### 4단계: MRO와 다중 상속

```python
class A:
    def method(self) -> str:
        return "A"

class B(A):
    def method(self) -> str:
        return f"B -> {super().method()}"

class C(A):
    def method(self) -> str:
        return f"C -> {super().method()}"

class D(B, C):
    def method(self) -> str:
        return f"D -> {super().method()}"

d = D()
print(d.method())   # D -> B -> C -> A
print(D.__mro__)    # (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

Python의 MRO는 C3 선형화 알고리즘을 사용합니다. `D -> B -> C -> A` 순서로 메서드를 탐색합니다. `super()`를 일관되게 사용하면 다중 상속에서도 각 부모의 메서드가 한 번씩만 호출됩니다.

### 5단계: 직원 급여 계산 — 상속 실전 예시

```python
class Employee:
    def __init__(self, name: str, base_salary: int) -> None:
        self.name = name
        self.base_salary = base_salary

    def monthly_pay(self) -> int:
        return self.base_salary

    def annual_pay(self) -> int:
        return self.monthly_pay() * 12

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"

class Manager(Employee):
    def __init__(self, name: str, base_salary: int, bonus: int) -> None:
        super().__init__(name, base_salary)
        self.bonus = bonus

    def monthly_pay(self) -> int:
        return super().monthly_pay() + self.bonus

class Contractor(Employee):
    def __init__(self, name: str, hourly_rate: int, hours_per_month: int) -> None:
        super().__init__(name, base_salary=0)
        self.hourly_rate = hourly_rate
        self.hours_per_month = hours_per_month

    def monthly_pay(self) -> int:
        return self.hourly_rate * self.hours_per_month

employees: list[Employee] = [
    Employee("Alice", 4_000_000),
    Manager("Bob", 5_000_000, 1_000_000),
    Contractor("Carol", 50_000, 160),
]

for emp in employees:
    print(f"{emp}: monthly={emp.monthly_pay():,}, annual={emp.annual_pay():,}")
```

`monthly_pay()`를 오버라이딩하면 `annual_pay()`는 수정 없이 올바르게 동작합니다. 부모의 템플릿 구조를 자식이 채우는 패턴입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `super().__init__()` 호출 누락 | 부모 속성이 초기화되지 않아 AttributeError가 납니다 | 자식 `__init__`에서 반드시 `super().__init__()`을 먼저 호출합니다 |
| 상속 계층을 3단계 이상 깊게 만듦 | 변경 영향이 전체 계층으로 퍼집니다 | 2단계 이상이면 합성(composition)을 고려합니다 |
| "is-a"가 아닌 "has-a"에 상속 사용 | 불필요한 결합을 만듭니다 | 포함 관계는 합성, 타입 관계만 상속을 씁니다 |
| 부모 메서드를 완전히 교체 | LSP를 위반하고 부모의 계약을 깹니다 | `super()`로 부모 동작을 확장하는 방향으로 작성합니다 |
| 다중 상속에서 `super()` 없이 직접 부모 호출 | MRO 체인이 끊어집니다 | 항상 `super()`를 사용합니다 |

## 실무에서 이렇게 쓰입니다

```python
class BaseRepository:
    """공통 CRUD 로직을 제공하는 기반 클래스"""

    def __init__(self) -> None:
        self._store: dict = {}

    def save(self, entity_id: str, data: dict) -> None:
        self._store[entity_id] = data

    def find(self, entity_id: str) -> dict | None:
        return self._store.get(entity_id)

    def delete(self, entity_id: str) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False

class UserRepository(BaseRepository):
    def find_by_email(self, email: str) -> dict | None:
        return next(
            (v for v in self._store.values() if v.get("email") == email),
            None
        )

class ProductRepository(BaseRepository):
    def find_by_category(self, category: str) -> list[dict]:
        return [v for v in self._store.values() if v.get("category") == category]

user_repo = UserRepository()
user_repo.save("u1", {"name": "Alice", "email": "alice@example.com"})
print(user_repo.find_by_email("alice@example.com"))  # {'name': 'Alice', ...}
```

Django의 `Model`, pytest의 `TestCase`, Python의 `Exception` 계층 모두 이 패턴을 기반으로 합니다.

## 현업 개발자는 이렇게 생각합니다

상속을 선택할 때 LSP(리스코프 치환 원칙)를 기준으로 삼습니다. 자식 객체를 부모 타입 변수에 넣어서 기존 코드가 그대로 동작하는가를 확인합니다. 동작하지 않는다면 상속 관계가 아니라 합성이 더 적합합니다.

"상속보다 합성을 선호하라"는 GoF의 조언은 상속을 쓰지 말라는 뜻이 아닙니다. 타입 계층이 명확하고 LSP가 성립하는 곳에서는 상속이 강력합니다. 하지만 "코드 재사용만을 위한 상속"은 결합도를 높여 변경 비용을 키웁니다.

## 운영 체크리스트

- [ ] `super().__init__()`을 올바르게 호출할 수 있다
- [ ] 메서드 오버라이딩과 `super()` 확장 패턴을 구분할 수 있다
- [ ] MRO를 `__mro__`로 확인할 수 있다
- [ ] `isinstance()`와 `issubclass()`를 적절하게 사용할 수 있다
- [ ] "is-a" vs "has-a" 관계를 판단하여 상속/합성을 선택할 수 있다

## 연습 문제

1. `Exception`을 상속한 커스텀 예외 계층을 만드세요. `AppError`, `ValidationError`, `NotFoundError`를 정의하고 각각에 메시지와 에러 코드를 포함합니다.
2. `BaseLogger` 클래스에서 `ConsoleLogger`와 `FileLogger`를 상속하세요. `log(message)` 메서드를 각각 다르게 구현합니다.
3. 다중 상속을 활용한 `Mixin` 패턴을 실습하세요. `TimestampMixin`과 `SerializableMixin`을 만들고 기존 클래스에 적용합니다.

## 정리 및 다음 단계

상속은 타입 관계가 명확하고 LSP가 성립할 때 강력한 도구입니다. 단순 코드 재사용을 위한 상속은 합성으로 대체하는 것이 유지보수에 유리합니다.

다음 글에서는 다형성을 다룹니다. 상속 기반 다형성, 덕 타이핑, `Protocol`을 활용해 타입 분기문 없이 확장 가능한 코드를 만드는 방법을 알아봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- **Object-Oriented Programming 101 (4/10): 상속 (현재 글)**
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Python 공식 문서 — super()](https://docs.python.org/3/library/functions.html#super)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Python MRO 공식 문서](https://docs.python.org/3/howto/mro.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 상속, 메서드 오버라이딩, super
