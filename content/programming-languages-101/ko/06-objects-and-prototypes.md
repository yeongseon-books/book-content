---
series: programming-languages-101
episode: 6
title: "Programming Languages 101 (6/10): 객체와 프로토타입"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Programming Languages
  - Objects
  - Prototype
  - Class
  - Inheritance
seo_description: 상태와 동작을 묶는 객체지향의 본질을 정의하고, 클래스와 프로토타입 기반 모델의 메서드 탐색 차이를 위임과 MRO 관점에서 비교 설명합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (6/10): 객체와 프로토타입

Java의 클래스도 객체지향이고, JavaScript의 프로토타입도 객체지향이라고 합니다. 그런데 둘의 표면은 꽤 다릅니다. 무엇이 같고 무엇이 다를까요.

이 글은 Programming Languages 101 시리즈의 6번째 글입니다.

이 글에서는 객체를 상태와 동작을 묶는 단위로 먼저 정의한 뒤, 그 묶음을 만드는 두 가지 대표 방식인 클래스 기반 모델과 프로토타입 기반 모델을 비교하겠습니다. 핵심 차이는 결국 메서드를 어디서 어떻게 찾느냐에 있습니다.

![Programming Languages 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/06/06-01-concept-at-a-glance.ko.png)
*Programming Languages 101 6장 흐름 개요*

> 객체 시스템에는 클래스 기반과 프로토타입 기반 두 종류가 있고, 둘 다 결국 '메서드 디스패치를 어디로 위임할 것인가'라는 한 가지 질문을 다르게 푸는 답입니다 — JavaScript의 prototype chain과 Python의 MRO가 닮아 보이는 건 우연이 아닙니다.

## 이 글에서 다룰 문제

- 객체를 가장 간단히 정의하면 무엇일까요?
- 클래스 기반 모델과 프로토타입 기반 모델은 메서드 탐색이 어떻게 다를까요?
- Python에서 클래스 자체가 객체라는 말은 무슨 뜻일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

객체 모델을 정확히 이해하면 "왜 이 메서드가 호출되지?", "왜 `super`가 이렇게 동작하지?" 같은 질문이 하나의 설명으로 정리됩니다. 새로운 객체지향 언어를 만나도 표면 문법보다 탐색 규칙을 먼저 보면 훨씬 빠르게 적응할 수 있습니다.

## 먼저 알아둘 용어

- **인스턴스**: 어떤 시점의 실제 상태를 담는 구체 객체입니다.
- **클래스**: 인스턴스의 형태와 동작을 정의하는 청사진입니다.
- **프로토타입**: 다른 객체가 위임할 수 있는 기준 객체입니다.
- **메서드 해석 순서(MRO)**: 메서드를 찾을 때 어떤 경로를 따라 올라갈지 정한 규칙입니다.
- **위임**: 현재 객체에 값이 없을 때 다른 객체에 조회를 넘기는 일입니다.

## 두 모델의 핵심 차이

두 모델 모두 "없으면 위로 위임한다"는 원리를 공유하지만, 위임 경로의 출발점이 다릅니다.

```text
클래스 기반 (Python, Java, C++)
    인스턴스 → 클래스 → 부모 클래스 → 조부모 클래스 → object

프로토타입 기반 (JavaScript)
    객체 → __proto__ (다른 객체) → __proto__.__proto__ → null
```

클래스 기반은 인스턴스와 클래스가 분리돼 있고, 프로토타입 기반은 모든 것이 객체이며 다른 객체를 직접 참조합니다.

## 먼저 보는 예시

### 데이터와 함수가 분리돼 있을 때

```python
def make_user(name, age):
    return {"name": name, "age": age}

def greet(user):
    return f"hi, {user['name']}"

u = make_user("kim", 30)
print(greet(u))
```

호출자는 데이터와 함수를 함께 들고 다녀야 합니다. 구조가 단순할 때는 괜찮지만, 책임이 늘수록 관리가 어려워집니다.

### 클래스에 묶었을 때

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name, self.age = name, age
    def greet(self) -> str:
        return f"hi, {self.name}"

print(User("kim", 30).greet())
```

상태와 동작이 한 단위로 묶였기 때문에 호출자는 하나의 객체만 다루면 됩니다. 객체지향의 가장 실질적인 장점이 여기에 있습니다.

## 두 모델을 단계적으로 따라가기

### 1단계 — 클래스 기반 탐색

```python
# 1_class.py
class A:
    def hi(self): return "A.hi"

class B(A):
    pass

print(B().hi())          # 'A.hi' — not on B, delegated upward
print(B.__mro__)          # the lookup order
```

`B`에 `hi`가 없으니 상위 클래스로 올라갑니다. `__mro__`는 Python이 실제로 따르는 탐색 경로를 그대로 보여 줍니다.

### 2단계 — 클래스도 객체다

```python
# 2_class_is_object.py
class A: ...
print(type(A))         # <class 'type'>  — a class is an instance of type
A.tag = "v1"            # you can attach attributes to a class object
print(A.tag)
```

Python에서는 클래스도 일급 객체입니다. 그래서 클래스에 속성을 붙이거나, 메타프로그래밍으로 동작을 바꾸는 일이 가능합니다.

### 3단계 — 사전으로 흉내 내는 프로토타입 방식

```python
# 3_prototype.py
base = {"hi": lambda self: "base.hi"}

def lookup(obj, key):
    if key in obj: return obj[key]
    if "__proto__" in obj: return lookup(obj["__proto__"], key)
    raise KeyError(key)

inst = {"__proto__": base}
print(lookup(inst, "hi")(inst))   # 'base.hi'
```

Python에는 실제 프로토타입 체인이 없지만, "없으면 위로 넘긴다"는 감각은 동일합니다. 클래스가 아닌 객체 자체를 기준으로 위임하는 것이 핵심 차이입니다.

### 4단계 — 재정의와 상위 호출

```python
# 4_super.py
class A:
    def hi(self): return "A"
class B(A):
    def hi(self): return "B+" + super().hi()

print(B().hi())  # B+A
```

`super()`는 막연히 "부모"를 가리키는 것이 아니라 MRO에서 다음 항목으로 이동합니다. 다중 상속에서도 이 한 줄이 일관된 탐색 규칙을 유지해 줍니다.

### 5단계 — 클로저로 객체 흉내 내기

```python
# 5_object_as_closure.py
def make_user(name):
    def greet(): return f"hi, {name}"
    return {"greet": greet}

u = make_user("kim")
print(u["greet"]())  # hi, kim
```

상태인 `name`과 동작인 `greet`가 클로저로 묶였습니다. 클래스 키워드가 없어도 객체의 핵심이 성립한다는 말입니다.

## 언어별 객체 모델 비교

같은 계층 구조를 Python, JavaScript, Go, Rust에서 어떻게 표현하는지 비교해 보겠습니다.

```python
# Python: 클래스 기반, MRO로 다중 상속 해결
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow"

# 다형성: 공통 인터페이스
animals: list[Animal] = [Dog(), Cat()]
for a in animals:
    print(a.speak())  # Woof, Meow
```

```javascript
// JavaScript: 프로토타입 기반 (class 문법은 편의 문법)
class Animal {
    speak() { return "..."; }
}

class Dog extends Animal {
    speak() { return "Woof"; }
}

// 프로토타입 체인 직접 보기
const d = new Dog();
console.log(Object.getPrototypeOf(d) === Dog.prototype);          // true
console.log(Object.getPrototypeOf(Dog.prototype) === Animal.prototype);  // true
```

```go
// Go: 인터페이스로 다형성 (상속 없음, 구조적 타이핑)
type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "Woof" }

type Cat struct{}
func (c Cat) Speak() string { return "Meow" }

// 인터페이스를 명시적으로 구현하지 않아도 메서드가 맞으면 통과
animals := []Speaker{Dog{}, Cat{}}
for _, a := range animals {
    fmt.Println(a.Speak())
}
```

```rust
// Rust: 트레이트로 다형성 (상속 없음, 트레이트 객체)
trait Speaker {
    fn speak(&self) -> &str;
}

struct Dog;
impl Speaker for Dog {
    fn speak(&self) -> &str { "Woof" }
}

struct Cat;
impl Speaker for Cat {
    fn speak(&self) -> &str { "Meow" }
}

let animals: Vec<Box<dyn Speaker>> = vec![Box::new(Dog), Box::new(Cat)];
for a in &animals {
    println!("{}", a.speak());
}
```

Python은 클래스 상속, JavaScript는 프로토타입 체인, Go는 인터페이스 암묵적 구현, Rust는 트레이트 명시적 구현으로 같은 다형성을 표현합니다. 상속이 없는 Go와 Rust도 객체지향의 핵심인 다형성과 캡슐화를 완전히 지원합니다.

## 이 코드에서 먼저 볼 점

- 두 모델 모두 "없으면 위로 위임한다"는 공통 원리를 갖습니다.
- Python 클래스가 객체라는 사실이 메타프로그래밍의 기반입니다.
- `super`는 부모라는 감각보다 MRO의 다음 항목이라는 감각으로 이해하는 편이 정확합니다.
- 클로저와 객체는 상태와 동작을 묶는다는 점에서 서로 닮아 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 상속 트리를 너무 깊게 구성 | 메서드 하나를 바꾸면 여러 곳이 연쇄적으로 영향받음 | 조합(composition)을 기본 선택으로, 상속은 is-a 관계가 명확할 때만 |
| MRO를 모른 채 다중 상속 사용 | `super` 호출 순서가 예상과 달라 디버깅이 어려움 | `ClassName.__mro__`를 직접 출력해 확인 |
| 상태 없이 메서드만 가득한 클래스 생성 | 함수 묶음일 뿐인 클래스가 과도하게 늘어남 | 모듈 함수 또는 `@staticmethod`로 대체 고려 |
| 프로토타입을 클래스의 열등한 흉내로 봄 | 개별 객체 단위로 동작을 커스터마이징하는 강점을 놓침 | JavaScript 객체 설계 시 프로토타입 체인 이해 필수 |
| 클로저와 객체를 무관한 개념으로 봄 | 설계 선택지가 좁아짐 | 둘 다 상태+동작을 묶는 방식임을 인식 |

## 실무에서는 이렇게 본다

대부분의 백엔드 코드는 클래스 기반 객체지향 위에 서 있습니다. 도메인 모델은 클래스가 되고, 동작은 메서드가 됩니다. 반면 JavaScript는 `class` 문법을 받아들였어도 엔진 내부에서는 여전히 프로토타입 체인을 사용합니다. 그래서 `Object.create`나 `Object.getPrototypeOf` 같은 API가 살아 있습니다.

설계를 시작할 때는 "이 객체가 실제로 어떤 상태를 들고 있나?"를 먼저 묻는 편이 좋습니다. 답이 빈약하다면 클래스를 만들 이유가 약할 수 있습니다. 기본값은 조합이고, 상속은 정말로 is-a 관계가 강할 때만 쓰는 편이 안정적입니다.

### 데이터클래스로 간결한 값 객체 만들기

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    ORIGIN: ClassVar["Point"]

    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

Point.ORIGIN = Point(0.0, 0.0)

p1 = Point(3.0, 4.0)
print(p1.distance_from_origin())  # 5.0
print(p1 + Point(1.0, 0.0))       # Point(x=4.0, y=4.0)
```

`frozen=True`로 불변 객체를 만들면 값 의미론(value semantics)을 자연스럽게 얻을 수 있습니다. 두 `Point` 인스턴스가 같은 좌표면 같은 것으로 취급합니다.

## Rust의 트레이트: 상속 없는 다형성

Rust는 클래스도 프로토타입도 없습니다. 대신 트레이트(trait)로 다형성을 표현합니다. 상속 계층 없이도 코드 재사용과 인터페이스 정의가 가능합니다.

```rust
// Rust: 트레이트로 공통 동작 정의
trait Animal {
    fn name(&self) -> &str;
    fn sound(&self) -> &str;
    fn describe(&self) -> String {  // 기본 구현 제공
        format!("{} goes {}", self.name(), self.sound())
    }
}

struct Dog { name: String }
struct Cat { name: String }

impl Animal for Dog {
    fn name(&self) -> &str { &self.name }
    fn sound(&self) -> &str { "woof" }
}

impl Animal for Cat {
    fn name(&self) -> &str { &self.name }
    fn sound(&self) -> &str { "meow" }
    fn describe(&self) -> String {  // 기본 구현 오버라이드
        format!("{} says {} quietly", self.name(), self.sound())
    }
}

fn print_animal(animal: &dyn Animal) {  // 트레이트 객체로 다형성
    println!("{}", animal.describe());
}

fn main() {
    let dog = Dog { name: "Rex".to_string() };
    let cat = Cat { name: "Luna".to_string() };

    print_animal(&dog);  // "Rex goes woof"
    print_animal(&cat);  // "Luna says meow quietly"
}
```

Rust의 트레이트는 Python의 Protocol, Go의 interface와 비슷하지만 더 강력합니다. 동일한 트레이트를 외부 타입에도 구현할 수 있어 기존 타입에 새 동작을 추가할 수 있습니다(오프닝/확장 원칙).

## 메타클래스: 클래스를 만드는 클래스

Python에서 클래스 자체가 객체라는 사실은 메타클래스로 이어집니다. 클래스가 생성되는 방식 자체를 제어할 수 있습니다.

```python
# 메타클래스: 클래스 생성 과정에 개입
class SingletonMeta(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self, url: str) -> None:
        self.url = url
        print(f"Connecting to {url}")

# 메타클래스가 __call__을 가로채 싱글턴 패턴 구현
db1 = DatabaseConnection("postgresql://localhost/mydb")
db2 = DatabaseConnection("postgresql://localhost/mydb")

print(db1 is db2)     # True — 같은 인스턴스
print(db1.url)        # "postgresql://localhost/mydb"
```

메타클래스는 ORM, 직렬화 라이브러리, 테스트 프레임워크처럼 클래스 정의 자체를 자동화해야 하는 경우에 쓰입니다. Django의 Model, SQLAlchemy의 Base가 대표적입니다. "클래스도 객체"라는 Python 설계 원칙이 만들어 낸 강력한 메타프로그래밍 도구입니다.

## 운영 체크리스트

- [ ] 클래스 기반과 프로토타입 기반의 차이를 한 줄로 설명할 수 있는가?
- [ ] Python의 `__mro__`를 직접 출력해 본 적이 있는가?
- [ ] `super`가 무엇을 하는지 한 문장으로 설명할 수 있는가?
- [ ] 기본 선택으로 조합을 더 선호하는가?
- [ ] 클로저로 객체를 흉내 내 본 적이 있는가?

## 연습 문제

1. 다중 상속 클래스를 두 개 만들고 `__mro__`를 출력한 뒤, 그 순서가 왜 그렇게 나오는지 적어 보세요.
2. 클로저 기반 객체 예제에 상태를 바꾸는 연산을 추가해 보세요. `nonlocal`이 필요합니다.
3. 최근에 상속을 쓴 클래스 하나를 골라 조합 기반 대안을 설계해 보세요.

## 정리

객체는 상태와 동작을 묶는 단위이고, 클래스와 프로토타입은 그 묶음을 만드는 두 가지 방식입니다. 어느 쪽이든 핵심은 위임입니다. 다음 글에서는 이 객체들이 메모리 안에서 어떻게 살아 있고 사라지는지 보겠습니다.

## 처음 질문으로 돌아가기

- **객체를 가장 간단히 정의하면 무엇일까요?**
  - 객체는 상태(데이터)와 동작(메서드)을 한 단위로 묶은 것입니다. 클래스 키워드가 없어도 클로저로 같은 구조를 만들 수 있습니다.
- **클래스 기반 모델과 프로토타입 기반 모델은 메서드 탐색이 어떻게 다를까요?**
  - 클래스 기반은 인스턴스에서 시작해 클래스, 부모 클래스 순서로 올라갑니다. 프로토타입 기반은 객체에서 시작해 `__proto__` 체인을 따라 올라갑니다. 둘 다 "없으면 위임한다"는 원리는 같습니다.
- **Python에서 클래스 자체가 객체라는 말은 무슨 뜻일까요?**
  - `type(MyClass)`를 출력하면 `<class 'type'>`이 나옵니다. 즉 클래스는 `type`의 인스턴스입니다. 이 덕분에 클래스에 속성을 동적으로 추가하거나, 메타클래스로 클래스 생성 과정 자체를 제어하는 메타프로그래밍이 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- **Programming Languages 101 (6/10): 객체와 프로토타입 (현재 글)**
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [Python Data Model — object](https://docs.python.org/3/reference/datamodel.html)
- [MDN — Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
- [Self: The Power of Simplicity (Ungar & Smith)](https://bibliography.selflanguage.org/_static/self-power.pdf)
- [Composition over inheritance (Wikipedia)](https://en.wikipedia.org/wiki/Composition_over_inheritance)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Objects, Prototype, Class, Inheritance
