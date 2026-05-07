---
series: oop-101
episode: 1
title: 객체지향이란 무엇인가?
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
  - 객체지향
  - 프로그래밍 패러다임
  - 클래스
seo_description: 객체지향 프로그래밍의 기본 개념과 절차지향과의 차이를 알아봅니다.
last_reviewed: '2026-05-04'
---

# 객체지향이란 무엇인가?

> Object-Oriented Programming 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 왜 프로그램을 "객체" 단위로 구성하면 유지보수가 쉬워질까요?

> 프로그래밍 패러다임은 코드를 구성하는 방식에 대한 사고방식입니다. 절차지향은 함수 중심, 객체지향은 데이터와 행위를 묶는 객체 중심입니다. 이 글에서는 객체지향이 무엇이고, 왜 등장했으며, 어떤 상황에서 유리한지 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 프로그래밍 패러다임의 종류와 비교
- 객체지향의 핵심 아이디어: 데이터와 행위의 결합
- 절차지향 코드와 객체지향 코드의 구조적 차이
- Python에서 객체지향이 어떻게 사용되는지

## 왜 중요한가

소규모 스크립트에서는 함수만으로 충분합니다. 그러나 코드가 수천 줄을 넘어가면 관련된 데이터와 로직이 흩어져 변경할 때마다 여러 함수를 동시에 수정해야 합니다. 객체지향은 관련된 데이터와 행위를 하나의 단위로 묶어 이 문제를 해결합니다.

> 객체지향 = 데이터 + 행위를 하나의 단위(객체)로 묶는 프로그래밍 방식

대부분의 현대 언어(Python, Java, C++, C#)가 객체지향을 지원합니다. 프레임워크와 라이브러리도 객체지향 설계를 기반으로 만들어져 있어서, 이 개념을 이해하지 못하면 코드를 읽는 것조차 어렵습니다.

## 핵심 개념 잡기

> 절차지향 vs 객체지향 비교

```
절차지향 (Procedural)          객체지향 (Object-Oriented)
┌────────────────────┐        ┌────────────────────┐
│ 함수 A             │        │ 객체 A             │
│ 함수 B             │        │  ├─ 데이터         │
│ 함수 C             │        │  └─ 메서드         │
│                    │        ├────────────────────┤
│ 전역 데이터        │        │ 객체 B             │
│  ├─ 변수 1         │        │  ├─ 데이터         │
│  └─ 변수 2         │        │  └─ 메서드         │
└────────────────────┘        └────────────────────┘
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 클래스(class) | 객체를 생성하기 위한 템플릿(설계도)입니다 |
| 인스턴스(instance) | 클래스를 기반으로 생성된 실제 객체입니다 |
| 속성(attribute) | 객체가 가진 데이터입니다 |
| 메서드(method) | 객체가 수행하는 행위(함수)입니다 |
| 캡슐화(encapsulation) | 데이터와 메서드를 하나로 묶고 외부 접근을 제한하는 것입니다 |

## Before / After

사용자 관리 로직을 비교합니다.

```python
# before: 절차지향 — 데이터와 함수가 분리
users = []

def create_user(name, email):
    user = {"name": name, "email": email, "active": True}
    users.append(user)
    return user

def deactivate_user(user):
    user["active"] = False

def get_user_display(user):
    status = "active" if user["active"] else "inactive"
    return f"{user['name']} ({status})"
```

```python
# after: 객체지향 — 데이터와 행위가 하나의 클래스에
class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def display(self) -> str:
        status = "active" if self.active else "inactive"
        return f"{self.name} ({status})"
```

## 단계별 실습

### Step 1: 첫 번째 클래스 만들기

```python
class Dog:
    """간단한 강아지 클래스"""

    def __init__(self, name: str, breed: str) -> None:
        self.name = name
        self.breed = breed

    def bark(self) -> str:
        return f"{self.name}이(가) 멍멍 짖습니다!"

    def __repr__(self) -> str:
        return f"Dog(name={self.name!r}, breed={self.breed!r})"


my_dog = Dog("바둑이", "진돗개")
print(my_dog.bark())   # 바둑이이(가) 멍멍 짖습니다!
print(my_dog)           # Dog(name='바둑이', breed='진돗개')
```

### Step 2: 여러 인스턴스 생성

```python
dog1 = Dog("바둑이", "진돗개")
dog2 = Dog("초코", "푸들")
dog3 = Dog("맥스", "래브라도")

dogs = [dog1, dog2, dog3]
for dog in dogs:
    print(f"{dog.name} ({dog.breed}): {dog.bark()}")
# 바둑이 (진돗개): 바둑이이(가) 멍멍 짖습니다!
# 초코 (푸들): 초코이(가) 멍멍 짖습니다!
# 맥스 (래브라도): 맥스이(가) 멍멍 짖습니다!

print(dog1 is dog2)  # False — 서로 다른 인스턴스
```

### Step 3: 절차지향 → 객체지향 리팩터링

```python
# 절차지향 버전
def create_rect(width, height):
    return {"width": width, "height": height}

def area(rect):
    return rect["width"] * rect["height"]

def perimeter(rect):
    return 2 * (rect["width"] + rect["height"])

r = create_rect(5, 3)
print(area(r))       # 15
print(perimeter(r))  # 16
```

```python
# 객체지향 버전
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __repr__(self) -> str:
        return f"Rectangle({self.width}, {self.height})"

r = Rectangle(5, 3)
print(r.area())       # 15
print(r.perimeter())  # 16
```

### Step 4: self의 의미

```python
class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> None:
        self.count += 1

    def reset(self) -> None:
        self.count = 0

    def value(self) -> int:
        return self.count

c1 = Counter()
c2 = Counter()
c1.increment()
c1.increment()
c2.increment()
print(c1.value())  # 2
print(c2.value())  # 1 — 각 인스턴스는 독립적
```

### Step 5: 클래스 변수 vs 인스턴스 변수

```python
class Student:
    school = "Python Academy"  # 클래스 변수: 모든 인스턴스가 공유

    def __init__(self, name: str, grade: int) -> None:
        self.name = name    # 인스턴스 변수: 인스턴스마다 다름
        self.grade = grade

    def introduce(self) -> str:
        return f"{self.school}의 {self.name}, {self.grade}학년"

s1 = Student("김철수", 3)
s2 = Student("이영희", 2)
print(s1.introduce())  # Python Academy의 김철수, 3학년
print(s2.introduce())  # Python Academy의 이영희, 2학년

Student.school = "Code Academy"  # 클래스 변수 변경 → 모든 인스턴스에 영향
print(s1.introduce())  # Code Academy의 김철수, 3학년
```

## 이 코드에서 주목할 점

- `__init__`은 인스턴스 생성 시 자동 호출되는 초기화 메서드입니다
- `self`는 현재 인스턴스를 가리키며, 모든 인스턴스 메서드의 첫 번째 매개변수입니다
- 클래스 변수는 모든 인스턴스가 공유하고, 인스턴스 변수는 각 인스턴스에 독립적입니다
- `__repr__`을 정의하면 디버깅 시 객체를 읽기 쉬운 형태로 출력합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `__init__`에서 self를 빠뜨림 | 인스턴스 변수가 아닌 지역 변수가 됩니다 | 반드시 `self.속성 = 값` 형태로 작성합니다 |
| 클래스 변수에 가변 객체 사용 | 모든 인스턴스가 같은 리스트를 공유합니다 | 가변 객체는 `__init__`에서 인스턴스 변수로 선언합니다 |
| 클래스와 인스턴스를 혼동 | `Dog.bark()` 호출 시 TypeError입니다 | 반드시 인스턴스를 생성한 후 메서드를 호출합니다 |
| 모든 것을 클래스로 감쌈 | 불필요한 복잡성이 추가됩니다 | 간단한 로직은 함수만으로 충분합니다 |
| `__repr__` 미정의 | 디버깅 시 `<__main__.Dog object>` 출력입니다 | `__repr__`을 정의하여 유용한 정보를 출력합니다 |

## 실무에서 이렇게 쓰입니다

- Django, Flask 등 웹 프레임워크의 모델은 클래스 기반입니다
- REST API에서 요청/응답 데이터를 클래스로 표현합니다
- 게임 개발에서 캐릭터, 아이템 등을 객체로 모델링합니다
- 데이터 파이프라인에서 각 처리 단계를 클래스로 추상화합니다
- 테스트 프레임워크(pytest, unittest)가 클래스 기반 테스트를 지원합니다

## 현업 개발자는 이렇게 생각합니다

객체지향은 만능이 아닙니다. 작은 스크립트에 클래스를 도입하면 오히려 복잡해집니다. 그러나 코드가 성장하면서 같은 데이터를 여러 함수가 공유할 때, 객체지향은 자연스러운 해결책이 됩니다.

실무에서는 "이것을 클래스로 만들어야 할까?"라는 질문을 자주 합니다. 답은 대부분 "관련 데이터와 행위가 함께 변경되는가?"입니다. 함께 변경된다면 하나의 클래스로 묶는 것이 유지보수에 유리합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **도구 선택** — OOP는 도구이지 정답이 아닙니다.
- **상태 캡슐** — 변경 가능한 상태가 명확히 있을 때 OOP가 빛납니다.
- **계약 우선** — 메서드 시그니처가 객체 계약입니다.
- **결합도** — 결합도를 낮추는 것이 객체 설계의 첫 목표입니다.
- **FP 혼합** — 변환은 FP로, 상태는 OOP로 가는 균형이 현실적입니다.

## 체크리스트

- [ ] 절차지향과 객체지향의 차이를 설명할 수 있다
- [ ] 클래스와 인스턴스의 관계를 이해한다
- [ ] `__init__`과 `self`의 역할을 설명할 수 있다
- [ ] 클래스 변수와 인스턴스 변수를 구분할 수 있다
- [ ] 간단한 클래스를 직접 설계하고 구현할 수 있다

## 연습 문제

1. `BankAccount` 클래스를 만들어 입금, 출금, 잔액 조회 메서드를 구현하세요.
2. `Book` 클래스를 만들고 여러 인스턴스를 리스트에 저장한 뒤 제목으로 검색하는 함수를 작성하세요.
3. 절차지향으로 작성된 계산기 코드를 객체지향으로 리팩터링하세요.

## 정리 및 다음 글 안내

객체지향은 데이터와 행위를 하나의 단위로 묶어 코드의 구조를 명확하게 만드는 프로그래밍 방식입니다. 다음 글에서는 클래스와 인스턴스를 더 깊이 살펴보겠습니다.

<!-- toc:begin -->
- **객체지향이란 무엇인가? (현재 글)**
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Classes](https://docs.python.org/3/tutorial/classes.html)
- [Real Python — Object-Oriented Programming in Python](https://realpython.com/python3-object-oriented-programming/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Python Crash Course — Eric Matthes](https://nostarch.com/python-crash-course-3rd-edition)

Tags: Python, OOP, 객체지향, 프로그래밍 패러다임, 클래스
