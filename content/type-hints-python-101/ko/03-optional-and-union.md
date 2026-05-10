---
series: type-hints-python-101
episode: 3
title: Optional과 Union
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
  - Type Hints
  - Optional
  - Union
  - None
  - 타입 안전
seo_description: Optional과 Union으로 None 가능성과 여러 타입을 안전하게 표현하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# Optional과 Union

> Type Hints in Python 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 함수가 None을 반환할 수 있다면 타입 힌트로 어떻게 표현할까요?

> 실무 코드에서 값이 없을 수 있는 상황은 빈번합니다. `Optional`은 "값 또는 None"을, `Union`은 "여러 타입 중 하나"를 표현합니다. 이 글에서는 두 타입의 의미와 Python 3.10+ 문법, 안전한 None 처리 패턴을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `Optional[T]`의 의미와 사용법
- `Union[T1, T2]`의 의미와 사용법
- Python 3.10+ `X | Y` 문법
- None 안전 처리 패턴

## 왜 중요한가

함수가 `None`을 반환할 수 있는데 타입 힌트에 표시하지 않으면, 호출자가 `None` 체크 없이 결과를 사용하다 `AttributeError`를 만납니다. `Optional`로 None 가능성을 명시하면 mypy가 체크 누락을 잡아줍니다.

> Optional = "이 값은 None일 수 있다"는 경고

`Union`은 API 응답이 성공(dict) 또는 오류(str)일 수 있는 경우처럼 여러 타입을 하나의 힌트로 표현합니다.

## 핵심 개념 잡기

> Optional vs Union

```
Optional[str]            Union[str, int]
─────────────────       ─────────────────
str | None              str | int
값이 있거나 None         str이거나 int
검색 결과 없음 표현      여러 타입 허용
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Optional[T] | `T | None`과 같으며, 값이 없을 수 있음을 나타냅니다 |
| Union[T1, T2] | T1 또는 T2 중 하나의 타입임을 나타냅니다 |
| `X \| Y` | Python 3.10+에서 Union의 축약 문법입니다 |
| 타입 가드(type guard) | 조건문으로 타입을 좁히는 패턴입니다 |
| 타입 좁히기(narrowing) | mypy가 분기를 분석하여 타입을 확정하는 기능입니다 |

## Before / After

None 가능성이 숨겨진 코드를 Optional로 명시합니다.

```python
# before: None 반환이 숨겨져 있음
def find_user(user_id):
    users = {"1": "Alice", "2": "Bob"}
    return users.get(user_id)
```

```python
# after: None 가능성이 명시됨
def find_user(user_id: str) -> str | None:
    users = {"1": "Alice", "2": "Bob"}
    return users.get(user_id)
```

## 단계별 실습

### Step 1: Optional 기본

```python
from typing import Optional


# Optional[str] == str | None
def find_user(user_id: str) -> Optional[str]:
    """사용자를 찾습니다. 없으면 None을 반환합니다."""
    users = {"1": "Alice", "2": "Bob", "3": "Charlie"}
    return users.get(user_id)


result = find_user("1")
print(result)  # Alice

result = find_user("999")
print(result)  # None

# Python 3.10+ 문법
def find_email(name: str) -> str | None:
    emails = {"Alice": "alice@example.com"}
    return emails.get(name)
```

### Step 2: None 안전 처리

```python
def find_user(user_id: str) -> str | None:
    users = {"1": "Alice", "2": "Bob"}
    return users.get(user_id)


# 방법 1: if 체크
user = find_user("1")
if user is not None:
    print(user.upper())  # mypy OK — user는 str로 좁혀짐
else:
    print("사용자 없음")

# 방법 2: 기본값 제공
user = find_user("999") or "Unknown"
print(user.upper())  # UNKNOWN

# 방법 3: 조기 반환
def process_user(user_id: str) -> str:
    user = find_user(user_id)
    if user is None:
        return "사용자를 찾을 수 없습니다"
    # 여기서 user는 str로 확정됨
    return f"처리 완료: {user.upper()}"


print(process_user("1"))    # 처리 완료: ALICE
print(process_user("999"))  # 사용자를 찾을 수 없습니다
```

### Step 3: Union 기본

```python
from typing import Union


# Union[int, float] — 정수 또는 실수
def absolute(value: Union[int, float]) -> float:
    return abs(float(value))


print(absolute(-5))    # 5.0
print(absolute(-3.14)) # 3.14

# Python 3.10+ 문법
def parse_value(raw: str) -> int | float | str:
    """문자열을 숫자로 변환합니다. 변환 불가하면 그대로 반환합니다."""
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


print(parse_value("42"))     # 42 (int)
print(parse_value("3.14"))   # 3.14 (float)
print(parse_value("hello"))  # hello (str)
```

### Step 4: 타입 가드와 isinstance

```python
def format_value(value: int | str | list[int]) -> str:
    """다양한 타입의 값을 문자열로 변환합니다."""
    if isinstance(value, int):
        return f"정수: {value:,}"
    if isinstance(value, str):
        return f"문자열: '{value}'"
    if isinstance(value, list):
        return f"리스트: [{', '.join(str(v) for v in value)}]"
    # mypy: 여기에 도달하면 안 됨 (exhaustive check)
    raise TypeError(f"지원하지 않는 타입: {type(value)}")


print(format_value(1000))           # 정수: 1,000
print(format_value("hello"))        # 문자열: 'hello'
print(format_value([1, 2, 3]))      # 리스트: [1, 2, 3]


# 복합 Union 처리
def process_response(data: dict[str, str] | str | None) -> str:
    if data is None:
        return "응답 없음"
    if isinstance(data, str):
        return f"오류: {data}"
    return f"성공: {data.get('result', 'N/A')}"


print(process_response({"result": "OK"}))  # 성공: OK
print(process_response("timeout"))          # 오류: timeout
print(process_response(None))               # 응답 없음
```

### Step 5: Optional 매개변수와 기본값

```python
def create_user(
    name: str,
    email: str | None = None,
    age: int | None = None,
    role: str = "user",
) -> dict[str, str | int | None]:
    """사용자를 생성합니다. email과 age는 선택입니다."""
    user: dict[str, str | int | None] = {"name": name, "role": role}
    if email is not None:
        user["email"] = email
    if age is not None:
        user["age"] = age
    return user


# 다양한 조합으로 호출
print(create_user("Alice"))
# {'name': 'Alice', 'role': 'user'}

print(create_user("Bob", email="bob@example.com", age=30))
# {'name': 'Bob', 'role': 'user', 'email': 'bob@example.com', 'age': 30}

print(create_user("Charlie", role="admin"))
# {'name': 'Charlie', 'role': 'admin'}

# 주의: Optional 매개변수 ≠ 기본값이 None인 매개변수
# def f(x: Optional[int]) — x는 반드시 전달해야 하며, None도 가능
# def f(x: int | None = None) — x를 전달하지 않으면 None
```

## 이 코드에서 주목할 점

- `Optional[T]`는 `T | None`의 별칭이며, None 가능성을 명시합니다
- `isinstance` 체크 후 mypy가 타입을 자동으로 좁힙니다
- Python 3.10+에서는 `X | Y` 문법이 `Union[X, Y]`보다 간결합니다
- Optional 매개변수의 기본값은 `None`이 일반적입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| Optional을 쓰고 None 체크 누락 | AttributeError 발생합니다 | if/assert로 None을 먼저 처리합니다 |
| `Optional[int] = 0` 혼동 | 기본값이 0이면 Optional이 아닙니다 | 기본값이 None일 때만 Optional을 씁니다 |
| Union 타입에 isinstance 미사용 | 잘못된 속성 접근이 발생합니다 | isinstance로 타입을 좁힙니다 |
| `Optional[Optional[int]]` | 중첩 Optional은 무의미합니다 | `Optional[int]`로 충분합니다 |
| `Union[int, str, float]`에서 int 포함 | int는 float의 하위 타입입니다 | `Union[float, str]`로 단순화합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 조회 결과가 없을 때 `Optional[Model]`을 반환합니다
- API 응답이 성공(dict) 또는 오류(str)일 때 `Union`으로 표현합니다
- 설정 값이 존재하지 않을 수 있는 경우 `Optional`로 표시합니다
- FastAPI 쿼리 파라미터에 `None` 기본값과 함께 `Optional`을 사용합니다
- 에러 처리에서 `Result = Success | Failure` 패턴을 구현합니다

## 현업 개발자는 이렇게 생각합니다

`Optional`은 "이 값은 None일 수 있다"는 명시적 경고입니다. 타입 힌트 없이는 코드를 읽거나 런타임에서야 None 가능성을 알게 됩니다. mypy와 함께 사용하면 None 체크 누락을 컴파일 타임에 잡을 수 있습니다.

Python 3.10+를 사용한다면 `Optional[str]` 대신 `str | None`을, `Union[int, str]` 대신 `int | str`을 쓰는 것이 가독성과 현대적 스타일 모두에 좋습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Optional 의미** — Optional은 "기본값이 None"이 아니라 "None일 수 있음"입니다.
- **X | Y 문법** — 현대 코드는 union 연산자를 우선합니다.
- **Narrowing** — isinstance/None 검사로 타입을 좁힙니다.
- **리턴 다중성** — Union 리턴은 호출자에게 부담이라는 점을 인지합니다.
- **Result 패턴** — 복잡 분기는 Result/Maybe 패턴이 명료합니다.

## 체크리스트

- [ ] `Optional[T]`와 `T | None`이 같은 의미임을 설명할 수 있다
- [ ] `Union[T1, T2]`로 여러 타입을 표현할 수 있다
- [ ] isinstance로 Union 타입을 좁힐 수 있다
- [ ] Optional 반환값을 안전하게 처리할 수 있다
- [ ] Python 3.10+ `X | Y` 문법을 사용할 수 있다

## 연습 문제

1. 딕셔너리에서 키를 찾아 값을 반환하는 함수를 `Optional`로 작성하고, None 체크 패턴 3가지를 구현하세요.
2. JSON 파싱 결과가 `dict | list | str | int | float | bool | None`일 수 있는 재귀 타입을 정의하세요.
3. `Union[Success, Failure]` 결과 타입을 만들고 isinstance로 처리하는 패턴을 작성하세요.

## 정리 및 다음 글 안내

`Optional`은 None 가능성을, `Union`은 여러 타입의 가능성을 명시합니다. isinstance와 조건문을 통해 mypy가 타입을 좁히는 원리를 이해했습니다. 다음 글에서는 콜백, 데코레이터, 오버로드 등 **함수 타입 힌트**를 심화합니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- **Optional과 Union (현재 글)**
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [PEP 604 — Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [mypy 공식 문서 — Optional types](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#optional-types-and-the-none-type)
- [Real Python — Union and Optional](https://realpython.com/python-type-checking/#union-types)

Tags: Python, Type Hints, Optional, Union, None, 타입 안전
