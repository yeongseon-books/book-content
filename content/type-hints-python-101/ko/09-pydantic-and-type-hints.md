---
series: type-hints-python-101
episode: 9
title: Pydantic과 타입 힌트
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
  - Pydantic
  - BaseModel
  - 데이터 검증
  - FastAPI
seo_description: Pydantic BaseModel로 타입 힌트 기반의 런타임 데이터 검증과 직렬화를 구현하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# Pydantic과 타입 힌트

> Type Hints in Python 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 타입 힌트를 런타임에서도 강제하여 잘못된 데이터가 시스템에 들어오는 것을 막을 수 있을까요?

> Python의 타입 힌트는 기본적으로 런타임에 강제되지 않습니다. mypy 같은 도구가 정적으로 검사할 뿐입니다. Pydantic은 타입 힌트를 런타임 검증 규칙으로 활용하여 잘못된 데이터를 즉시 거부합니다. FastAPI가 Pydantic 위에 구축된 이유이기도 합니다. 이 글에서는 Pydantic의 핵심 기능과 실전 패턴을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- Pydantic BaseModel의 원리와 사용법
- Field로 세밀한 검증 규칙 추가
- validator와 model_validator로 커스텀 검증
- FastAPI와의 연동 패턴

## 왜 중요한가

외부에서 들어오는 데이터는 신뢰할 수 없습니다. API 요청, 설정 파일, 데이터베이스 조회 결과 모두 예상과 다른 형태일 수 있습니다. 수동으로 if 문을 나열하면 코드가 복잡해지고 누락이 생깁니다. Pydantic은 타입 힌트에서 검증 로직을 자동 생성하여 이 문제를 해결합니다.

> Pydantic = 타입 힌트 기반의 런타임 데이터 검증

타입 힌트를 "문서화"에서 "실행 가능한 계약"으로 격상시킵니다.

## 개념 한눈에 보기

> Pydantic은 클래스의 타입 힌트를 읽어 검증기를 자동 생성합니다. 데이터가 모델에 맞지 않으면 상세한 오류 메시지와 함께 거부합니다.

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

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| BaseModel | Pydantic의 기반 모델 클래스 |
| Field | 필드별 검증 규칙과 메타데이터를 정의하는 도구 |
| field_validator | 개별 필드에 커스텀 검증 로직을 추가하는 데코레이터 |
| model_validator | 모델 전체에 걸친 교차 필드 검증 데코레이터 |
| BaseSettings | 환경 변수에서 설정을 자동으로 읽는 모델 |

## Before / After

**Before — 수동 검증:**

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

**After — Pydantic 모델:**

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(ge=0)
```

## 실습: 단계별로 따라하기

### 1단계: BaseModel 기본 사용

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


# dict에서 생성
user = User(name="김철수", age=30, email="kim@example.com")
print(user.name)       # 김철수
print(user.model_dump())  # {'name': '김철수', 'age': 30, 'email': 'kim@example.com'}

# 타입 변환 자동 수행
user2 = User(name="이영희", age="25", email="lee@example.com")
print(user2.age)       # 25 (str → int 자동 변환)
print(type(user2.age)) # <class 'int'>
```

Pydantic은 가능한 경우 타입을 자동 변환합니다. `"25"`를 `int`로, `"true"`를 `bool`로 변환합니다.

### 2단계: Field로 검증 규칙 추가

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0, description="원 단위 가격")
    quantity: int = Field(ge=0, default=0)
    tags: list[str] = Field(default_factory=list, max_length=10)


product = Product(name="Python 입문서", price=25000)
print(product.quantity)  # 0 (기본값)

# 검증 실패
# Product(name="", price=-100)
# ValidationError: name must have at least 1 character,
#                  price must be greater than 0
```

### 3단계: field_validator로 커스텀 검증

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
            raise ValueError("영문자와 숫자만 허용됩니다")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        if not any(c.isdigit() for c in v):
            raise ValueError("숫자를 하나 이상 포함해야 합니다")
        return v
```

`field_validator`는 값을 변환하여 반환할 수도 있습니다. `username`을 소문자로 정규화하는 것이 그 예입니다.

### 4단계: model_validator로 교차 필드 검증

```python
from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end_date <= self.start_date:
            raise ValueError("end_date는 start_date보다 뒤여야 합니다")
        return self


# DateRange(start_date="2026-01-10", end_date="2026-01-01")
# ValidationError: end_date는 start_date보다 뒤여야 합니다
```

`mode="after"`는 개별 필드 검증이 모두 끝난 후에 실행됩니다.

### 5단계: FastAPI와 연동

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

FastAPI는 요청 본문을 Pydantic 모델로 자동 파싱하고 검증합니다. 검증 실패 시 422 응답을 자동으로 반환합니다.

## 이 코드에서 주목할 점

- BaseModel을 상속하면 타입 힌트가 곧 검증 규칙이 됩니다
- Field로 범위, 길이, 기본값 등 세밀한 조건을 추가합니다
- validator는 검증과 동시에 값 변환도 수행할 수 있습니다
- FastAPI와 결합하면 요청/응답 검증이 자동화됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| mutable 기본값 사용 | `list[str] = []`는 공유 참조 위험이 있습니다 | `Field(default_factory=list)`를 사용합니다 |
| validator에서 @classmethod 누락 | Pydantic v2에서 오류가 발생합니다 | `@field_validator` 아래에 `@classmethod`를 추가합니다 |
| model_dump 대신 dict 사용 | Pydantic v2에서 deprecated입니다 | `model_dump()`와 `model_dump_json()`을 사용합니다 |
| 과도한 자동 변환 의존 | `"abc"`를 `int`로 변환할 수 없어 오류가 납니다 | strict 모드로 자동 변환을 비활성화합니다 |
| Optional 필드에 기본값 미설정 | 필수 필드가 되어 의도와 다릅니다 | `Optional[str] = None`으로 기본값을 지정합니다 |

## 실무에서는 이렇게 쓰입니다

- FastAPI 엔드포인트에서 요청/응답 모델로 API 계약을 명시
- BaseSettings로 환경 변수 기반 설정 관리 (12-Factor App)
- 데이터 파이프라인에서 원본 데이터 검증 게이트로 활용
- ORM 모델과 API 모델을 분리하여 계층 간 데이터 변환에 사용
- JSON Schema 자동 생성으로 API 문서화와 클라이언트 코드 생성에 활용

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 시스템 경계에서 Pydantic을 활용합니다. API 요청, 외부 서비스 응답, 설정 파일 등 "신뢰할 수 없는 데이터"가 들어오는 지점에 모델을 배치하여 내부 로직은 항상 검증된 데이터만 다루도록 합니다.

내부 로직에서는 dataclass나 일반 클래스로 충분한 경우가 많습니다. 모든 데이터 클래스를 BaseModel로 만들면 불필요한 검증 오버헤드가 생깁니다. 경계에서 한 번 검증하고, 내부에서는 타입 힌트만으로 안전을 확보하는 것이 균형 잡힌 접근입니다.

## 체크리스트

- [ ] BaseModel로 데이터 모델을 정의했는가
- [ ] Field로 필요한 검증 규칙을 추가했는가
- [ ] 커스텀 검증이 필요한 필드에 validator를 적용했는가
- [ ] 교차 필드 검증에 model_validator를 사용했는가
- [ ] FastAPI와의 연동 패턴을 이해했는가

## 연습 문제

1. 상품 주문 모델(`OrderItem`)을 Pydantic으로 작성하세요. `product_name`(1자 이상), `quantity`(1 이상), `unit_price`(0 초과) 필드를 포함하고 `total_price` computed field를 추가하세요.

2. 회원가입 요청 모델에서 `password`와 `password_confirm` 필드가 일치하는지 `model_validator`로 검증하세요.

3. `BaseSettings`를 사용하여 `DATABASE_URL`, `SECRET_KEY`, `DEBUG`(기본값 False) 환경 변수를 읽는 설정 모델을 작성하세요.

## 정리 및 다음 단계

Pydantic은 타입 힌트를 런타임 검증 규칙으로 변환하는 라이브러리입니다. BaseModel, Field, validator를 조합하면 간결하면서도 강력한 데이터 검증이 가능합니다. FastAPI와 결합하면 API의 입출력 검증이 자동화됩니다.

다음 글에서는 시리즈의 마무리로 타입 힌트를 잘 쓰는 기준과 팀 단위 가이드라인을 정리합니다.

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
- [Pydantic v2 마이그레이션 가이드](https://docs.pydantic.dev/latest/migration/)
- [Real Python — Pydantic](https://realpython.com/python-pydantic/)

Tags: Python, Type Hints, Pydantic, BaseModel, 데이터 검증, FastAPI
