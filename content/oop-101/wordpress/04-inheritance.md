---
title: "바이브코딩을 위한 객체지향 기초 (4/10): 상속"
series: oop-101
episode: 4
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 상속
  - 바이브코딩
  - 메서드 오버라이딩
  - super
last_reviewed: '2026-06-18'
seo_description: AI가 만드는 상속 계층을 이해하고 안전하게 수정하는 방법을 설명합니다. super(), 오버라이딩, MRO를 바이브코딩 관점으로 정리합니다.
---

# 바이브코딩을 위한 객체지향 기초 (4/10): 상속

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 네 번째 글입니다.

---

AI에게 동물 시뮬레이션을 만들어 달라고 하면 `Animal` → `Dog`, `Cat` 같은 상속 계층이 나옵니다. "직원 시스템을 만들어 줘"라고 하면 `Employee` → `Manager`, `Developer`가 나오기도 합니다. 코드는 동작하는데, `super().__init__()`은 왜 필요한지, 오버라이딩을 하면 부모 메서드는 어떻게 되는지 헷갈립니다.

상속은 OOP에서 가장 먼저 배우는 기능이지만, 현업에서는 가장 쉽게 남용되는 기능이기도 합니다. AI도 마찬가지입니다. 때로 AI가 만든 상속 계층은 과하게 깊어지거나, 상속 대신 합성을 쓰는 편이 더 나은 경우도 있습니다. 그 판단을 하려면 상속의 기본을 알아야 합니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "AI가 만든 상속 계층이 3단계 이상이면 잠깐 멈추고 물어보세요. '이걸 합성으로 바꾸면 어떻게 달라지나?'"

## 이 글에서 다룰 문제

- 상속이 코드 중복을 줄이면서 동시에 강한 결합을 만드는 이유는 무엇인가요?
- `super()`와 오버라이딩은 어떻게 안전하게 함께 쓸 수 있을까요?
- AI가 상속 대신 합성을 써야 하는 자리에 상속을 쓰는 경우를 어떻게 알 수 있을까요?
- `isinstance()`와 `issubclass()`는 상속 관계를 읽을 때 왜 중요할까요?
- 다중 상속과 MRO는 언제 문제가 되고 어떻게 확인할까요?

## 핵심 개념 잡기

```text
Animal (부모 클래스)
├── name, sound
├── speak()
│
├── Dog (자식 클래스)
│   └── speak() 오버라이딩
│   └── fetch() 추가
│
└── Cat (자식 클래스)
    └── speak() 오버라이딩
    └── purr() 추가
```

| 용어 | 설명 |
|------|------|
| 부모 클래스(parent/base) | 속성과 메서드를 물려주는 기존 클래스입니다 |
| 자식 클래스(child/derived) | 부모를 상속받아 확장하는 새 클래스입니다 |
| 오버라이딩(overriding) | 부모의 메서드를 자식에서 재정의하는 것입니다 |
| `super()` | 부모 클래스의 메서드를 호출하는 내장 함수입니다 |
| MRO(Method Resolution Order) | 다중 상속에서 메서드 탐색 순서입니다 |

## Before / After: AI가 상속으로 중복을 제거하는 패턴

```python
# Before: 상속 없음 — 코드 중복 발생
class Circle:
    def __init__(self, name, color, radius):
        self.name = name      # 중복
        self.color = color    # 중복
        self.radius = radius

    def describe(self):
        return f"{self.color} {self.name}"  # 중복

class Square:
    def __init__(self, name, color, side):
        self.name = name      # 중복
        self.color = color    # 중복
        self.side = side

    def describe(self):       # 중복
        return f"{self.color} {self.name}"
```

```python
# After: 상속으로 공통 로직 통합
class Shape:
    def __init__(self, name: str, color: str) -> None:
        self.name = name
        self.color = color

    def describe(self) -> str:
        return f"{self.color} {self.name}"

class Circle(Shape):
    def __init__(self, color: str, radius: float) -> None:
        super().__init__("circle", color)  # 부모 생성자 호출
        self.radius = radius

class Square(Shape):
    def __init__(self, color: str, side: float) -> None:
        super().__init__("square", color)  # 부모 생성자 호출
        self.side = side
```

`super().__init__()`은 부모 클래스의 초기화 코드를 실행합니다. 이 줄을 빠뜨리면 부모 속성이 설정되지 않아 에러가 납니다.

## 바이브코딩 관점: AI의 상속 계층 읽기

AI가 만든 상속 계층을 분석할 때는 **is-a 관계**를 확인하세요. `Dog`는 `Animal`의 일종(is-a)입니다. 이 관계가 성립하지 않으면 상속이 잘못된 것입니다.

```python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name}: {self.sound}"

class Dog(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "woof")  # sound는 항상 "woof"

    def fetch(self, item: str) -> str:
        return f"{self.name}가 {item}을 가져옵니다"

class Cat(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "meow")

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())        # Buddy: woof
print(cat.speak())        # Whiskers: meow
print(dog.fetch("공"))    # Buddy가 공을 가져옵니다
```

`isinstance()`로 상속 관계를 확인할 수 있습니다.

```python
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog는 Animal의 일종
print(isinstance(dog, Cat))     # False

# 다형성: Animal 타입으로 Dog, Cat 모두 처리 가능
animals: list[Animal] = [Dog("Buddy"), Cat("Whiskers"), Dog("Max")]
for animal in animals:
    print(animal.speak())
```

## 오버라이딩과 super() 함께 쓰기

오버라이딩할 때 부모 기능을 완전히 대체하지 않고 **확장**하고 싶다면 `super()`를 사용합니다.

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
        super().__init__(make, model, year)  # 부모 초기화 실행
        self.battery_kwh = battery_kwh

    def info(self) -> str:
        base = super().info()  # 부모의 info() 결과를 가져와서
        return f"{base} (배터리: {self.battery_kwh}kWh)"  # 확장

ev = ElectricVehicle("Tesla", "Model 3", 2026, 75.0)
print(ev.info())  # 2026 Tesla Model 3 (배터리: 75.0kWh)
```

## AI가 만든 상속이 잘못된 신호

AI도 가끔 실수합니다. 이런 신호가 보이면 상속 구조를 다시 검토하세요.

| 신호 | 실제로 생기는 문제 | 먼저 해볼 리팩터링 |
|------|-------------------|--------------------|
| 자식 클래스가 부모 메서드 절반 이상을 오버라이딩 | 공통 기반이 실제로 공통이 아님 | 합성이나 전략 패턴으로 분리 |
| 부모 클래스에 옵션 플래그가 계속 늘어남 | `if self.kind == ...` 분기가 쌓임 | 변하는 동작을 별도 객체로 분리 |
| 상속 깊이가 4단계 이상 | 디버깅과 이해가 어려워짐 | 2~3단계로 제한하고 합성 검토 |

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `super().__init__()` 호출 누락 | 부모 속성이 초기화되지 않습니다 | 자식의 `__init__`에서 반드시 호출합니다 |
| is-a가 아닌 has-a 관계에 상속 사용 | 자동차는 엔진의 일종이 아닙니다 | 합성(composition)을 사용합니다 |
| 다중 상속 남용 | MRO가 복잡해집니다 | 믹스인(mixin) 패턴으로 제한합니다 |
| 부모 클래스 내부 구현에 의존 | 부모 변경 시 자식이 깨집니다 | 부모의 공개 인터페이스만 사용합니다 |
| 상속 깊이 4단계 이상 | 디버깅과 이해가 어렵습니다 | 2~3단계로 제한합니다 |

## AI 팁: 상속 구조 평가하기

AI가 만든 상속 계층을 평가할 때 이렇게 물어보세요.

```python
# 상속 관계 확인 방법
print(Dog.__mro__)  # Dog의 메서드 탐색 순서
# (Dog, Animal, object)

# AI에게 물어볼 질문들:
# "이 상속 구조에서 is-a 관계가 성립하는가?"
# "이걸 합성으로 바꾸면 코드가 어떻게 달라지나?"
# "자식 클래스를 부모 타입으로 사용해도 문제없는가?"
```

## 체크리스트

- [ ] 단일 상속으로 부모 클래스를 확장할 수 있다
- [ ] `super()`로 부모 메서드를 호출할 수 있다
- [ ] 메서드 오버라이딩의 동작 원리를 이해한다
- [ ] is-a 관계와 has-a 관계를 구분할 수 있다
- [ ] AI 코드에서 잘못된 상속 신호를 식별할 수 있다

## 처음 질문으로 돌아가기

- **상속이 강한 결합을 만드는 이유는 무엇인가요?**
  부모 클래스가 변경되면 자식 클래스 전체에 영향을 줍니다. 부모의 내부 구현을 자식이 의존하고 있다면 더 심해집니다. AI가 상속 계층을 만들 때 이 결합도를 고려하지 않으면 나중에 수정이 어려워집니다.

- **`super()`와 오버라이딩은 어떻게 안전하게 함께 쓸까요?**
  오버라이딩에서 `super().method()`를 쓰면 부모 동작을 유지하면서 확장할 수 있습니다. 부모를 완전히 대체해야 할 때만 `super()` 없이 오버라이딩합니다.

- **언제 상속 대신 합성을 선택해야 할까요?**
  "자식은 부모의 일종인가(is-a)?" 질문에 확신이 없으면 합성을 선택합니다. `UserService`가 `Logger`를 상속하는 것은 is-a가 아닙니다. `UserService`가 `Logger`를 속성으로 가지는 has-a가 맞습니다.

## 정리

상속은 코드 재사용과 계층적 관계 표현에 유용하지만, is-a 관계가 명확할 때만 사용해야 합니다. AI가 만든 상속 계층이 복잡하다면 합성으로 바꾸는 것이 나을 수 있습니다. 다음 글에서는 다형성을 통해 같은 인터페이스로 다른 동작을 구현하는 방법과, AI가 `isinstance()` 분기 대신 다형성을 쓰는 이유를 알아봅니다.

## 참고 자료

- [Python 공식 문서 — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- **바이브코딩을 위한 객체지향 기초 (4/10): 상속 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 상속, 바이브코딩, 메서드 오버라이딩, super
