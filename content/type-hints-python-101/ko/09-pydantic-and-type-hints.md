---
series: type-hints-python-101
episode: 9
title: Pydantic과 타입 힌트
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - Pydantic
  - BaseModel
  - 데이터 검증
  - FastAPI
seo_description: Pydantic BaseModel로 타입 힌트 기반의 런타임 데이터 검증과 직렬화를 구현하는 방법을 다룹니다.
last_reviewed: '2026-05-12'
---

# Pydantic과 타입 힌트

지금까지 본 타입 힌트는 정적 분석 단계에서 빛을 발했습니다. 그런데 실제 서비스는 외부에서 들어오는 데이터를 다룹니다. 잘못된 JSON, 누락된 필드, 문자열로 들어온 숫자는 mypy가 아니라 런타임 경계에서 걸러야 합니다.

이 글은 Type Hints (Python) 101 시리즈의 9번째 글입니다. 여기서는 Pydantic이 타입 힌트를 읽어 런타임 검증 규칙으로 바꾸는 방식과, `BaseModel`, `Field`, validator, FastAPI 연동 패턴을 살펴봅니다.

## 이 글에서 다룰 문제

- 타입 힌트를 런타임 데이터 검증으로 연결할 수 있을까요?
- 필드별 제약 조건은 어디에 적을까요?
- 단일 필드 검증과 교차 필드 검증은 어떻게 나눌까요?
- FastAPI는 왜 Pydantic을 기반으로 움직일까요?

> Pydantic은 타입 힌트를 실행 시점 계약으로 바꾸는 도구입니다.

## 왜 이 주제가 중요한가

외부 데이터는 신뢰할 수 없습니다. API 요청, 환경 변수, 큐 메시지, 서드파티 응답은 모두 기대와 다른 형태로 들어올 수 있습니다. 이를 매번 `if`와 `isinstance`로 수동 검증하면 코드가 길어지고, 누락과 중복이 생기기 쉽습니다.

Pydantic은 타입 힌트를 읽어 검증기를 만듭니다. 잘못된 값은 즉시 `ValidationError`로 거부하고, 올바른 값은 구조화된 모델 인스턴스로 바꿉니다. 타입 힌트가 문서와 정적 분석을 넘어 실행 시점까지 확장되는 지점입니다.

## 한눈에 보는 개념

```text
입력 데이터 (dict/JSON)
       │
  BaseModel.__init__
       │
  타입 힌트 기반 검증
       │
  ├── 통과 → 모델 인스턴스
  └── 실패 → ValidationError
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| BaseModel | Pydantic의 기본 검증 모델 클래스입니다 |
| Field | 필드별 제약 조건과 메타데이터를 적는 함수입니다 |
| field_validator | 단일 필드 검증 또는 변환 로직을 적는 데코레이터입니다 |
| model_validator | 여러 필드 사이의 관계를 검증하는 데코레이터입니다 |
| BaseSettings | 환경 변수에서 값을 읽는 설정 모델입니다 |

## 바꾸기 전과 후

```python
def create_user(data: dict) -> dict:
    if "name" not in data:
        raise ValueError("name is required")
    if not isinstance(data["name"], str):
        raise ValueError("name must be a string")
    if "age" not in data:
        raise ValueError("age is required")
    if not isinstance(data["age"], int) or data["age"] < 0:
        raise ValueError("age must be a non-negative integer")
    return data
```

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(ge=0)
```

수동 검증 로직이 모델 선언으로 정리되면서, 계약이 더 짧고 분명해집니다.

## 단계별로 익히기

### 1단계: `BaseModel` 기본

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


# 키워드 인자에서 생성
user = User(name="Alice", age=30, email="alice@example.com")
print(user.name)       # Alice
print(user.model_dump())  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}

# 호환 가능한 타입은 자동 변환
user2 = User(name="Bob", age="25", email="bob@example.com")
print(user2.age)       # 25 (str → int)
print(type(user2.age)) # <class 'int'>
```

Pydantic은 가능한 경우 타입 변환도 함께 수행합니다.

### 2단계: `Field`로 제약 조건 추가하기

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0, description="Price in cents")
    quantity: int = Field(ge=0, default=0)
    tags: list[str] = Field(default_factory=list, max_length=10)


product = Product(name="Python Book", price=3500)
print(product.quantity)  # 0

# Product(name="", price=-100)
# ValidationError 발생
```

길이, 범위, 기본값 같은 정책을 필드 선언에 모을 수 있습니다.

### 3단계: `field_validator`로 커스텀 규칙 넣기

```python
from pydantic import BaseModel, field_validator


class SignupRequest(BaseModel):
    username: str
    password: str
    email: str

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Only alphanumeric characters allowed")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
```

validator는 검증뿐 아니라 정규화도 할 수 있습니다. 여기서는 username을 소문자로 맞춥니다.

### 4단계: `model_validator`로 필드 간 관계 검증하기

```python
from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

단일 필드만으로 판단할 수 없는 규칙은 `model_validator`로 모으는 편이 깔끔합니다.

### 5단계: FastAPI와 연결하기

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    age: int


@app.post("/users", response_model=UserResponse)
def create_user(request: CreateUserRequest) -> UserResponse:
    # request는 이미 검증된 Pydantic 모델입니다
    return UserResponse(id=1, name=request.name, age=request.age)
```

FastAPI는 요청 본문을 Pydantic 모델로 자동 파싱하고, 실패하면 422 응답을 만들어 줍니다.

## 여기서 먼저 봐야 할 점

- `BaseModel`을 상속하는 순간 타입 힌트가 검증 규칙으로 읽힙니다.
- `Field`는 길이, 범위, 기본값 정책을 한곳에 모아 줍니다.
- validator는 검증과 값 변환을 함께 처리할 수 있습니다.
- FastAPI는 Pydantic 덕분에 요청/응답 계약을 자동화합니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `list[str] = []` 같은 mutable 기본값 사용 | 인스턴스 간 공유 위험이 있습니다 | `Field(default_factory=list)`를 사용합니다 |
| Pydantic v2에서 `@classmethod`를 빠뜨림 | validator 정의가 어색해질 수 있습니다 | `@field_validator` 아래에 `@classmethod`를 둡니다 |
| `.dict()`를 계속 사용함 | v2 기준 권장 API가 아닙니다 | `model_dump()`를 사용합니다 |
| 자동 변환에 과하게 의존함 | 의도치 않은 입력이 통과할 수 있습니다 | 필요하면 strict 정책을 검토합니다 |
| Optional 필드에 기본값을 주지 않음 | nullable인데도 필수 필드로 남습니다 | `str | None = None`처럼 적습니다 |

## 실무에서는 이렇게 연결됩니다

- FastAPI 요청/응답 모델로 API 계약을 명확히 합니다.
- `BaseSettings`로 환경 변수를 안전하게 읽습니다.
- 데이터 파이프라인 입구에서 raw 데이터를 검증하는 관문으로 둡니다.
- ORM 모델과 API 모델을 분리해 경계 책임을 분명히 합니다.

## 실무 판단 기준

시니어 엔지니어는 Pydantic을 시스템 경계에 둡니다. API 요청, 외부 서비스 응답, 설정 파일처럼 신뢰할 수 없는 데이터가 들어오는 지점에서 한 번 검증하고, 내부 로직에서는 이미 검증된 타입을 신뢰하는 편이 효율적입니다. 내부 도메인 객체까지 전부 `BaseModel`로 만드는 것은 과한 경우가 많습니다.

즉, 원칙은 단순합니다. 경계에서 검증하고, 내부에서는 단순한 `dataclass`나 `TypedDict`로 가볍게 흐르게 하는 것입니다. 이 구분이 있어야 검증 비용과 복잡도를 과하게 늘리지 않습니다.

## 체크리스트

- [ ] `BaseModel`로 데이터 모델을 정의했습니다
- [ ] `Field`로 필요한 제약 조건을 추가했습니다
- [ ] 단일 필드 규칙에는 `field_validator`를 사용했습니다
- [ ] 교차 필드 규칙에는 `model_validator`를 사용했습니다
- [ ] FastAPI와의 연결 방식을 이해했습니다

## 연습 문제

1. `OrderItem` 모델을 만들어 상품명 길이, 수량, 단가 검증을 넣어 보세요.

2. `password`와 `password_confirm`가 일치해야 하는 회원가입 모델을 `model_validator`로 작성해 보세요.

3. `DATABASE_URL`, `SECRET_KEY`, `DEBUG`를 읽는 `BaseSettings` 모델을 만들어 보세요.

## 정리와 다음 글

Pydantic은 타입 힌트를 런타임 검증 규칙으로 바꾸는 대표 도구입니다. `BaseModel`, `Field`, validator를 조합하면 짧은 선언으로도 강한 데이터 계약을 만들 수 있습니다. 특히 FastAPI와 결합할 때 API 경계가 훨씬 분명해집니다.

다음 글에서는 시리즈를 마무리하면서 타입 힌트를 어디에, 어느 정도까지 적용해야 하는지 실무 기준을 정리하겠습니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- **Pydantic과 타입 힌트 (현재 글)**
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [Pydantic 공식 문서](https://docs.pydantic.dev/latest/)
- [FastAPI 공식 문서 — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Real Python — Pydantic](https://realpython.com/python-pydantic/)

Tags: Python, Type Hints, Pydantic, BaseModel, 데이터 검증, FastAPI
