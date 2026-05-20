---
series: type-hints-python-101
episode: 9
title: "Type Hints in Python 101 (9/10): Pydantic과 타입 힌트"
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
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (9/10): Pydantic과 타입 힌트

정적 타입 검사는 코드를 작성하는 사람을 돕지만, 실제 서비스는 외부에서 들어오는 데이터를 상대합니다. 문자열로 들어온 나이, 형식이 잘못된 이메일, 서로 맞지 않는 비밀번호 확인 값은 mypy가 아니라 런타임 경계에서 막아야 합니다.

이 글은 Type Hints (Python) 101 시리즈의 9번째 글입니다. 여기서는 하나의 `CreateUserRequest` → FastAPI 엔드포인트 → `UserResponse` 흐름을 기준으로, Pydantic이 타입 힌트를 런타임 검증으로 바꾸는 과정과 잘못된 요청이 422로 거절된 뒤 올바른 요청이 성공 응답으로 이어지는 전체 수명 주기를 살펴봅니다.

## 먼저 던지는 질문

- 타입 힌트를 런타임 검증으로 어떻게 연결할 수 있을까요?
- `Field`, `field_validator`, `model_validator`는 한 요청 흐름에서 각각 어디에 들어갈까요?
- FastAPI는 잘못된 요청을 실제로 어떤 422 응답으로 돌려줄까요?

## 큰 그림

![Type Hints in Python 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/09/09-01-big-picture.ko.png)

*Type Hints in Python 101 9장 흐름 개요*

이 그림에서는 Pydantic과 타입 힌트를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Pydantic과 타입 힌트의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 주제가 중요한가

실제 서비스의 버그는 내부 로직보다 경계에서 더 자주 시작합니다. 클라이언트가 빈 이름을 보내거나, 숫자여야 할 값을 문자열로 보내거나, 두 필드 사이의 관계를 깨뜨리는 데이터가 들어오면 내부 로직은 그 데이터를 신뢰하지 못합니다.

Pydantic은 타입 힌트를 읽어 그 경계에 검증 규칙을 세웁니다. 중요한 점은 기능을 개별 문법으로 외우는 것이 아니라, 하나의 요청이 **모델 선언 → 필드 제약 → 커스텀 validator → FastAPI 422 → 수정된 성공 응답**으로 이어지는 흐름을 이해하는 것입니다.

## 한눈에 보는 개념

```text
HTTP 요청 JSON
      │
CreateUserRequest 검증
      │
  ├── 실패 → 422 응답
  └── 통과 → 엔드포인트 실행
                │
          UserResponse 반환
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| BaseModel | Pydantic의 기본 검증 모델 클래스입니다 |
| Field | 길이, 범위, 기본값 같은 필드 제약을 선언하는 함수입니다 |
| field_validator | 단일 필드 값을 검사하거나 정규화하는 데코레이터입니다 |
| model_validator | 여러 필드 관계를 함께 검사하는 데코레이터입니다 |
| 422 Unprocessable Entity | 요청 JSON은 읽었지만, 검증 규칙을 통과하지 못했을 때 FastAPI가 돌려주는 응답입니다 |

## 바꾸기 전과 후

```python
def create_user(data: dict) -> dict:
    if not data.get("username"):
        raise ValueError("username is required")
    if len(data.get("password", "")) < 8:
        raise ValueError("password is too short")
    if data.get("password") != data.get("password_confirm"):
        raise ValueError("passwords do not match")
    return data
```

```python
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self
```

수동 `if` 문 여러 개를 흩뿌리는 대신, 요청 계약이 모델 선언으로 모입니다.

## 하나의 요청 생명주기로 따라가기

이 글 전체에서는 회원가입 API 하나를 계속 확장합니다.

### 1단계: `BaseModel`로 요청/응답 뼈대 만들기

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    username: str
    email: str
    age: int
    password: str
    password_confirm: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int
```

이 단계만으로도 "어떤 필드가 들어오고 어떤 필드가 나가는지"가 문서화됩니다. 하지만 아직은 길이, 범위, 필드 간 관계 같은 정책이 빠져 있습니다.

### 2단계: `Field`로 경계 제약을 선언하기

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)
```

여기서 요청 경계의 기본 규칙이 정해집니다.

- `username`은 3자 이상 20자 이하입니다.
- `email`은 이메일 형식이어야 합니다.
- `age`는 13세 이상 120세 이하입니다.
- 비밀번호는 최소 길이를 가집니다.

### 3단계: `field_validator`로 단일 필드 정규화하기

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized
```

이 validator는 두 가지 일을 합니다.

- 앞뒤 공백을 제거하고 소문자로 정규화합니다.
- 허용하지 않는 문자가 있으면 즉시 거절합니다.

즉, Pydantic validator는 검증뿐 아니라 **입력 정리(normalization)**도 함께 담당할 수 있습니다.

### 4단계: `model_validator`로 필드 간 관계를 묶기

```python
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self
```

여기서는 단일 필드만으로는 판단할 수 없는 규칙, 즉 `password`와 `password_confirm`의 일치 여부를 모델 전체 관점에서 검사합니다.

### 5단계: FastAPI 엔드포인트에 연결하기

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

app = FastAPI()

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=13, le=120)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username must contain only letters, numbers, or underscores")
        return normalized

    @model_validator(mode="after")
    def passwords_match(self) -> "CreateUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("password_confirm must match password")
        return self

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(request: CreateUserRequest) -> UserResponse:
    return UserResponse(
        id=101,
        username=request.username,
        email=request.email,
        age=request.age,
    )
```

이제 요청 본문이 엔드포인트에 도달하기 전에 Pydantic 검증을 거칩니다. 즉, 잘못된 값은 함수 본문에 들어오기 전에 422로 차단됩니다.

### 6단계: 잘못된 요청이 실제로 422가 되는지 보기

```http
POST /users
Content-Type: application/json

{
  "username": "  Min!  ",
  "email": "not-an-email",
  "age": 10,
  "password": "short",
  "password_confirm": "different"
}
```

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "username"],
      "msg": "Value error, username must contain only letters, numbers, or underscores",
      "input": "  Min!  "
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "not-an-email"
    },
    {
      "type": "greater_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 13",
      "input": 10,
      "ctx": {"ge": 13}
    },
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

중요한 점은 FastAPI가 막연히 "422가 납니다"라고만 말하는 것이 아니라, **어느 필드가 어떤 규칙을 어겼는지 구조화된 본문으로 돌려준다**는 점입니다. 이 정보는 프런트엔드와 API 클라이언트가 오류를 바로 표시하는 데도 유용합니다.

비밀번호 확인 불일치처럼 모델 전체 검사에 걸리는 경우에는 아래처럼 추가 오류가 생깁니다.

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, password_confirm must match password"
    }
  ]
}
```

### 7단계: 요청을 고치고 성공 응답까지 확인하기

```http
POST /users
Content-Type: application/json

{
  "username": "  Min_Jun  ",
  "email": "minjun@example.com",
  "age": 24,
  "password": "securepass1",
  "password_confirm": "securepass1"
}
```

```json
{
  "id": 101,
  "username": "min_jun",
  "email": "minjun@example.com",
  "age": 24
}
```

성공 응답에서 눈여겨볼 점은 두 가지입니다.

- `username`이 validator를 거치며 `min_jun`으로 정규화되었습니다.
- 엔드포인트 본문은 이미 검증된 모델만 받기 때문에, 내부 로직은 입력 형식 방어 코드에서 훨씬 자유로워집니다.

## 여기서 먼저 봐야 할 점

- 정적 타입 검사는 코드를 쓰는 사람을 돕고, Pydantic은 들어오는 데이터를 막습니다.
- `Field`는 필드 제약, `field_validator`는 단일 필드 규칙, `model_validator`는 교차 필드 규칙에 적합합니다.
- FastAPI는 검증 실패를 구조화된 422 응답으로 자동 변환합니다.
- 검증이 끝난 뒤의 내부 로직은 더 단순한 타입 계약을 신뢰할 수 있습니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `BaseModel`, `Field`, validator 예제를 모두 따로 봄 | 실제 요청 흐름에서 연결 지점이 보이지 않습니다 | 하나의 요청 모델에 단계적으로 누적합니다 |
| 422를 설명만 하고 예시 본문을 안 보여 줌 | 독자가 실패 형태를 상상만 하게 됩니다 | 잘못된 요청과 응답 JSON을 함께 보여 줍니다 |
| `list[str] = []` 같은 mutable 기본값 사용 | 인스턴스 간 공유 문제가 생길 수 있습니다 | `Field(default_factory=list)`를 사용합니다 |
| 모든 내부 모델까지 Pydantic으로 감쌈 | 검증 비용과 복잡도가 불필요하게 늘어납니다 | 시스템 경계에 우선 배치합니다 |
| 자동 형변환을 무조건 신뢰함 | 의도하지 않은 입력이 통과할 수 있습니다 | 중요한 경계는 제약과 validator를 더 명시합니다 |

## 실무에서는 이렇게 연결됩니다

- FastAPI 요청 본문을 Pydantic 모델로 받아 API 계약을 명시합니다.
- 환경 변수, 큐 메시지, 외부 API 응답처럼 신뢰할 수 없는 입력에도 같은 패턴을 적용합니다.
- 경계에서 한 번 검증한 뒤, 내부 서비스 계층은 이미 검증된 타입을 사용합니다.
- 응답 모델도 함께 선언해 반환 스키마 드리프트를 줄입니다.

## 실무 판단 기준

경험 많은 개발자는 Pydantic을 "모든 곳에 붙이는 도구"가 아니라 **입력 경계에 두는 검증 장치**로 봅니다. 외부에서 들어오는 값은 한 번 강하게 검증하고, 그 안쪽에서는 `dataclass`, `TypedDict`, 명확한 함수 시그니처처럼 더 가벼운 구조를 쓰는 편이 운영 효율이 좋습니다.

즉, 원칙은 분명합니다. 정적 타입 검사는 작성 시점에, Pydantic은 런타임 경계에 둡니다. 둘을 겹치게 쓰는 것이 아니라, 서로 다른 실패 지점을 메우도록 배치하는 것입니다.

## 체크리스트

- [ ] 하나의 요청/응답 모델 흐름으로 Pydantic 예제를 정리했습니다
- [ ] `Field` 제약, `field_validator`, `model_validator`를 각각 어디에 쓰는지 이해했습니다
- [ ] 잘못된 요청과 422 응답 본문을 확인했습니다
- [ ] 수정된 요청이 성공 응답으로 이어지는 흐름을 확인했습니다
- [ ] 정적 타입 검사와 런타임 검증의 역할 차이를 설명할 수 있습니다

## 연습 문제

1. `CreateOrderRequest` 모델을 만들고 `items`, `currency`, `total_amount` 검증을 한 뒤, 잘못된 요청 하나와 성공 요청 하나를 직접 만들어 보세요.

2. `password`와 `password_confirm` 대신 `start_date`와 `end_date`를 검사하는 `model_validator` 예제를 작성해 보세요.

3. 성공 응답에 `created_at`을 추가하고, 응답 모델이 어떤 직렬화 계약을 보장하는지 확인해 보세요.

## 정리와 다음 글

Pydantic은 타입 힌트를 런타임 검증 계약으로 바꾸는 도구입니다. 하지만 개별 문법을 따로 외우는 것보다 중요한 것은, 하나의 요청이 모델 선언에서 시작해 422 실패와 성공 응답까지 이어지는 흐름을 이해하는 일입니다. 그 흐름이 잡혀야 FastAPI와 타입 힌트의 경계 설계가 명확해집니다.

다음 글에서는 시리즈를 마무리하면서, 지금까지 본 정적 검사와 런타임 검증을 실제 팀 규칙으로 바꾸는 타입 힌트 운영 기준을 정리하겠습니다.

## 처음 질문으로 돌아가기

- **타입 힌트를 런타임 검증으로 어떻게 연결할 수 있을까요?**
  - 본문의 기준은 Pydantic과 타입 힌트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`Field`, `field_validator`, `model_validator`는 한 요청 흐름에서 각각 어디에 들어갈까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **FastAPI는 잘못된 요청을 실제로 어떤 422 응답으로 돌려줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): 함수 타입 힌트](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Type Hints in Python 101 (7/10): Generic 이해하기](./07-generic.md)
- [Type Hints in Python 101 (8/10): mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- **Pydantic과 타입 힌트 (현재 글)**
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Pydantic 공식 문서](https://docs.pydantic.dev/latest/)
- [FastAPI 공식 문서 — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI 공식 문서 — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Real Python — Pydantic](https://realpython.com/python-pydantic/)

Tags: Python, Type Hints, Pydantic, BaseModel, 데이터 검증, FastAPI
