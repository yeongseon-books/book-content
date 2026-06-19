---
title: "바이브코딩을 위한 Python 기초 (9/10): AI가 클래스를 만들어줬는데 왜 이렇게 짰는지 이해하기"
series: python-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- Python
- AI코딩
- 클래스
- 객체지향
- dataclass
seo_description: "바이브코딩 시대, AI가 만든 클래스 코드의 구조를 읽고 수정하는 법. self, dunder 메서드, dataclass 완전 정리"
---

# 바이브코딩을 위한 Python 기초 (9/10): AI가 클래스를 만들어줬는데 왜 이렇게 짰는지 이해하기

이 글은 바이브코딩을 위한 Python 기초 시리즈의 9번째 글입니다.

AI에게 "사용자 데이터 관리하는 코드 만들어줘"라고 하면 이런 코드가 돌아올 때가 있습니다.

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class UserProfile:
    name: str
    email: str
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.email = self.email.lower()

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def __repr__(self) -> str:
        return f"UserProfile({self.name!r}, tags={self.tags})"
```

이걸 보고 "아, 이렇게 쓰면 되겠다"라고 이해할 수 있나요? `@dataclass`가 뭔지, `field(default_factory=list)`는 왜 저렇게 쓴 건지, `__post_init__`은 언제 불리는지, `__repr__`는 왜 직접 정의했는지.

더 흔한 상황은 이겁니다. AI가 클래스를 만들어줬는데 뭔가 수정하고 싶습니다. 속성 하나 더 추가하거나, 메서드 하나 바꾸거나. 근데 어디를 어떻게 건드려야 할지 모릅니다. 잘못 건드리면 `TypeError: __init__() takes 2 positional arguments but 3 were given` 같은 에러가 납니다.

클래스의 기본 구조를 이해하면 AI가 만든 코드를 읽고, 내 상황에 맞게 수정하고, AI에게 더 정확한 요청을 할 수 있게 됩니다.

> 클래스는 "데이터와 그 데이터를 다루는 동작을 함께 묶은 것"입니다. AI는 이 구조를 자주 씁니다.

---

## 이 글에서 다룰 문제

- AI가 만든 클래스에서 `self`는 뭘 가리키나요?
- `__init__`, `__repr__`, `__eq__` 같은 `__` 이름 메서드들은 언제 호출되나요?
- `@dataclass`를 쓴 클래스는 어떻게 수정해야 하나요?
- 클래스에 속성을 추가할 때 기존 코드가 깨지지 않으려면?
- AI가 상속을 썼는데, `super()`는 어떻게 동작하나요?

---

## AI 코드를 읽으려면 이것을 알아야

### `self`는 "이 객체 자신"을 가리킨다

```python
class User:
    def __init__(self, name, email):
        self.name = name    # 이 객체의 name 속성
        self.email = email  # 이 객체의 email 속성

    def label(self):
        return f"{self.name} <{self.email}>"  # 이 객체의 속성에 접근
```

`u = User("Ada", "a@x")`를 만들면 `u`가 "이 객체"입니다. `u.label()`을 호출하면 Python이 내부적으로 `User.label(u)`로 바꿔 실행합니다. 그래서 메서드 첫 번째 인자가 항상 `self`입니다.

**AI가 만든 클래스에서 `self`를 빠뜨린 메서드가 있으면?**

```python
class Broken:
    def greet():  # self 없음!
        return "hello"

b = Broken()
b.greet()  # TypeError: greet() takes 0 positional arguments but 1 was given
```

`self`가 빠진 메서드를 인스턴스에서 호출하면 에러가 납니다. AI가 가끔 정적 메서드가 아닌데 `self`를 빠뜨리는 실수를 합니다.

### dunder 메서드들 — 언제 자동으로 불리나

이름 양쪽에 `__`가 붙은 메서드들은 Python이 특정 상황에서 자동으로 호출합니다.

| 메서드 | 언제 불리나 | 역할 |
|--------|------------|------|
| `__init__` | `User("Ada")` 호출 시 | 객체 초기화 |
| `__repr__` | REPL에서 `u` 입력 시, `repr(u)` | 디버깅용 문자열 |
| `__str__` | `print(u)`, `str(u)` | 사람이 읽을 문자열 |
| `__eq__` | `u1 == u2` | 동등 비교 |
| `__len__` | `len(u)` | 길이 반환 |
| `__enter__/__exit__` | `with u as x:` | 컨텍스트 매니저 |

AI가 `__repr__`을 정의했다면 "디버깅할 때 이 객체가 어떻게 보일지 정의한 것"입니다.

### 클래스 속성 vs 인스턴스 속성

```python
class User:
    role = "member"     # 클래스 속성 — 모든 인스턴스가 공유

    def __init__(self, name):
        self.name = name  # 인스턴스 속성 — 각자 따로 가짐
```

```python
u1 = User("Ada")
u2 = User("Bob")
print(u1.role)   # "member" — 클래스에서 옴
print(u2.role)   # "member" — 같은 값

User.role = "admin"  # 클래스 속성 변경
print(u1.role)   # "admin" — u1도 바뀜
print(u2.role)   # "admin" — u2도 바뀜
```

**AI가 자주 저지르는 실수:** 클래스 속성에 `[]`를 쓰면 모든 인스턴스가 같은 리스트를 공유합니다.

```python
class BuggyUser:
    tags = []  # 위험! 모든 인스턴스가 이 리스트를 공유

u1 = BuggyUser()
u2 = BuggyUser()
u1.tags.append("python")
print(u2.tags)  # ["python"] — u2 것도 바뀜!
```

### `@dataclass`가 자동으로 만드는 것들

`@dataclass`는 반복적인 boilerplate 코드를 자동 생성합니다.

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
```

이 몇 줄이 자동으로 다음을 만들어줍니다.
- `__init__(self, name: str, email: str)` — 생성자
- `__repr__` — `User(name='Ada', email='a@x')` 형태
- `__eq__` — 같은 필드 값이면 동등하다고 판단

**dataclass에 속성 추가하는 법:**

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    name: str
    email: str
    tags: List[str] = field(default_factory=list)  # 기본값이 mutable이면 field() 필수
    active: bool = True  # 기본값이 immutable이면 그냥 = 사용
```

기본값이 `[]`나 `{}`같은 mutable 타입이면 반드시 `field(default_factory=list)`로 써야 합니다. 그냥 `tags: List[str] = []`로 쓰면 모든 인스턴스가 같은 리스트를 공유하는 버그가 생깁니다.

### 상속과 `super()`

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def label(self):
        return f"{self.name} <{self.email}>"

class Admin(User):
    def __init__(self, name, email, level):
        super().__init__(name, email)  # 부모 __init__ 호출
        self.level = level             # 추가 속성

    def label(self):
        return f"[Admin-{self.level}] {super().label()}"  # 부모 메서드 호출
```

`super()`는 "부모 클래스의 해당 메서드를 호출"합니다. `Admin.__init__`에서 `super().__init__`을 호출하지 않으면 `name`, `email` 속성이 설정되지 않습니다.

---

## Before / After

### AI 초안 — dict로 사용자 데이터 다루기

```python
def make_user(name, email):
    return {"name": name, "email": email}

def user_label(user):
    return f"{user['name']} <{user['email']}>"

def users_equal(a, b):
    return a["name"] == b["name"] and a["email"] == b["email"]
```

필드를 하나 추가하려면 `make_user`, `user_label`, `users_equal` 모두 수정해야 합니다. 오타로 `user['neme']`를 써도 런타임에야 발견됩니다.

### 바이브코딩으로 개선 — dataclass 적용

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    name: str
    email: str
    tags: List[str] = field(default_factory=list)

    def label(self) -> str:
        return f"{self.name} <{self.email}>"

# 이제 이렇게 씁니다
u1 = User("Ada", "a@x")
u2 = User("Ada", "a@x")
print(u1.label())   # "Ada <a@x>"
print(u1 == u2)     # True — __eq__ 자동 생성됨
print(u1)           # User(name='Ada', email='a@x', tags=[])
```

AI에게 요청: "이 dict 기반 코드를 @dataclass를 써서 클래스로 만들어줘. 비교(`==`)와 디버깅 출력이 자동으로 동작하게 해줘."

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 메서드에 `self` 빠뜨리기 | `TypeError: takes 0 positional arguments but 1 was given` | 메서드 첫 번째 인자로 `self` 추가 |
| 클래스 속성에 `[]` 사용 | 모든 인스턴스가 같은 리스트 공유 | `__init__`에서 `self.items = []`로 |
| dataclass에 mutable 기본값 | `ValueError: mutable default ... is not allowed` | `field(default_factory=list)` 사용 |
| `__init__`에서 `return self` | `TypeError` 발생 | `__init__`은 `None`을 반환해야 함 |
| `is`와 `==` 혼동 | `is`는 같은 객체, `==`은 같은 값 | 값 비교엔 `==`, 동일 객체 비교엔 `is` |

---

## AI에게 이 주제 관련 질문하는 팁

**클래스 설명 요청:**
"이 클래스에서 `__post_init__`은 언제 호출되고 왜 여기서 처리하는지 설명해줘."

**dataclass 속성 추가:**
"이 dataclass에 `created_at: datetime` 필드를 추가해줘. 기본값은 현재 시각으로 하고, 비교에서는 제외해줘."

**상속 구조 수정:**
"이 Admin 클래스가 User를 상속받는데, `super().__init__()`이 빠져있어. 추가해줘."

**클래스 vs 함수 판단:**
"이 코드를 클래스로 만들어야 할지 함수로 유지할지 판단해줘. 상태를 계속 들고 다녀야 하는지 기준으로."

---

## 운영 체크리스트

- [ ] AI가 만든 클래스에서 `self`가 뭘 가리키는지 설명할 수 있다
- [ ] `__init__`, `__repr__`, `__eq__`가 언제 자동으로 불리는지 안다
- [ ] `@dataclass`에서 mutable 기본값은 `field(default_factory=...)`를 써야 함을 안다
- [ ] 클래스 속성과 인스턴스 속성의 차이, 클래스 속성에 `[]` 쓰면 안 되는 이유를 안다
- [ ] `super().__init__()`이 없으면 부모 클래스 초기화가 안 됨을 안다
- [ ] `is`와 `==`의 차이를 안다

---

## 처음 질문으로 돌아가기

**`self`는 뭘 가리키나요?**
메서드를 호출한 인스턴스 자신입니다. `u.label()`을 호출하면 `label` 안에서 `self`가 `u`를 가리킵니다.

**`__init__`, `__repr__` 같은 메서드들은 언제 호출되나요?**
Python이 특정 연산(`User(...)`, `repr(u)`, `u1 == u2`)에서 자동으로 호출합니다. 내가 직접 `u.__repr__()`을 부를 일은 거의 없습니다.

**`@dataclass` 클래스에 속성을 추가하려면?**
클래스 본문에 `필드명: 타입 = 기본값` 형태로 추가합니다. mutable 기본값이면 `field(default_factory=...)` 필수입니다.

**상속에서 `super()`는 왜 쓰나요?**
자식 클래스의 `__init__`에서 부모 클래스의 초기화를 실행하기 위해서입니다. 빠뜨리면 부모에서 정의한 속성들이 설정되지 않습니다.

---

## 정리

AI가 클래스를 만들어줄 때는 `self`, dunder 메서드, `@dataclass`, 상속 같은 패턴을 씁니다. 이것들이 "왜 이렇게 짰는지"를 이해하면 단순히 복붙하는 게 아니라 내 상황에 맞게 조정할 수 있게 됩니다.

특히 `@dataclass`는 AI가 자주 쓰는 현대적인 패턴입니다. 속성을 추가하거나 수정할 때 어디를 건드려야 하는지 알면 AI에게 더 구체적인 수정 요청을 할 수 있습니다.

마지막 편에서는 AI에게 시키기 전에 표준 라이브러리로 이미 해결할 수 있는 것들을 먼저 확인하는 방법을 다룹니다.

## 참고 자료

### 공식 문서
- [Python 공식 문서 (python.org)](https://docs.python.org/3/)
- [Python Tutorial (python.org)](https://docs.python.org/3/tutorial/)

### 관련 시리즈
- [Python DB-API 101](../../python-dbapi-101/ko/)
- [Pytest 101](../../pytest-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Python 기초 (1/10): 왜 Python이고, 어떻게 설치할까?](./01-why-python-and-install.md)
- [바이브코딩을 위한 Python 기초 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [바이브코딩을 위한 Python 기초 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [바이브코딩을 위한 Python 기초 (5/10): 제어 흐름](./05-control-flow.md)
- [바이브코딩을 위한 Python 기초 (6/10): 함수와 인자](./06-functions-and-arguments.md)
- [바이브코딩을 위한 Python 기초 (7/10): 모듈과 패키지](./07-modules-and-packages.md)
- [바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- **바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체 (현재 글)**
- [바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어](./10-standard-library-tour.md)

<!-- toc:end -->
Tags: 바이브코딩, Python, AI코딩, 클래스, 객체지향, dataclass
