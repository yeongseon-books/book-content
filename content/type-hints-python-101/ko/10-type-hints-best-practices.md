---
series: type-hints-python-101
episode: 10
title: "Type Hints in Python 101 (10/10): 타입 힌트를 잘 쓰는 기준"
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
  - 베스트 프랙티스
  - 점진적 타이핑
  - 코드 품질
  - 팀 가이드라인
seo_description: 점진적 타이핑 전략, 팀 가이드라인, 실무 패턴으로 타입 힌트를 효과적으로 도입하는 기준을 정리합니다.
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (10/10): 타입 힌트를 잘 쓰는 기준

타입 힌트는 많이 적는다고 자동으로 좋아지지 않습니다. 반대로 중요한 경계와 공개 시그니처를 비워 두면, 앞선 글에서 본 mypy와 Pydantic도 제대로 힘을 쓰지 못합니다. 결국 중요한 것은 "어디를 어떤 순서로 단단하게 만들 것인가"입니다.

이 글은 Type Hints (Python) 101 시리즈의 마지막 글입니다. 여기서는 느슨한 주문 처리 모듈 하나를 출발점으로 삼아, `Any`가 퍼진 코드와 빈약한 시그니처를 어떻게 정리하는지, 왜 그 순서가 실무적으로 효과적인지, 그리고 마지막에 어떤 검증 단계까지 연결해야 하는지를 runnable한 before/after 흐름으로 정리합니다.

## 먼저 던지는 질문

- 타입 힌트는 어디에 먼저 붙여야 투자 대비 효과가 클까요?
- `Any`가 퍼진 코드는 어떤 순서로 줄여야 할까요?
- 반환 타입, 공개 API, 내부 헬퍼 중 무엇을 먼저 단단하게 만들어야 할까요?

## 큰 그림

![Type Hints in Python 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/10/10-01-big-picture.ko.png)

*Type Hints in Python 101 10장 흐름 개요*

이 그림에서는 타입 힌트를 잘 쓰는 기준를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 타입 힌트를 잘 쓰는 기준의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 주제가 중요한가

레거시 코드베이스는 대개 두 가지 문제를 함께 가집니다. 하나는 공개 함수 시그니처가 비어 있어 호출자가 계약을 알 수 없다는 점이고, 다른 하나는 `Any`가 한 군데에서 시작해 아래 코드 전체로 전염된다는 점입니다.

이 글의 목적은 조언 목록을 더 늘리는 것이 아닙니다. 앞선 8화의 정적 검사, 9화의 런타임 경계 검증을 실제 팀 규칙으로 연결하려면, 한 모듈을 어떻게 단계적으로 단단하게 만드는지 보여 줘야 합니다. 그래서 이번 글은 느슨한 모듈 하나를 끝까지 개선하는 흐름으로 설명합니다.

## 한눈에 보는 개념

```text
느슨한 시그니처 / Any 확산
            │
공개 함수 반환 타입 보강
            │
입력/출력 타입 구체화
            │
Union 좁히기 + 헬퍼 분리
            │
검사기 통과 + 팀 규칙 반영
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 점진적 타이핑 | 코드베이스 전체를 한 번에 바꾸지 않고 중요한 경로부터 타입을 보강하는 전략입니다 |
| 공개 API | 다른 모듈이 호출하는 함수, 메서드, 클래스 인터페이스입니다 |
| 타입 좁히기 | `isinstance`, `is None` 같은 분기로 Union 타입을 더 구체적으로 만드는 방식입니다 |
| Any | 모든 타입과 호환되지만, 그만큼 검사기의 추적을 끊어 버리는 타입입니다 |
| hardening pass | 느슨한 구현을 더 강한 계약과 검증으로 보강하는 한 번의 정리 작업입니다 |

## 바꾸기 전과 후

```python
from typing import Any

def process_order(payload: Any) -> Any:
    order_id = payload.get("order_id")
    user = payload.get("user")
    return {"order_id": order_id, "email": user.get("email")}
```

```python
class OrderPayload(TypedDict):
    order_id: int | str
    user: dict[str, str | None]

def process_order(payload: OrderPayload) -> dict[str, str]:
    order_id = parse_order_id(payload["order_id"])
    email = require_user_email(payload["user"])
    return {"order_id": str(order_id), "email": email}
```

핵심은 지역 변수에 타입을 잔뜩 적는 것이 아니라, 시그니처와 경계 헬퍼를 먼저 단단하게 바꾸는 데 있습니다.

## 한 모듈을 before/after로 단단하게 만들기

이 글 전체에서는 `order_service.py` 하나를 개선합니다.

### 1단계: 느슨한 시작점 보기

```python
# order_service.py
from typing import Any

def find_user(user_id):
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> Any:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

class OrderService:
    def create_order(self, payload):
        user = find_user(payload.get("user_id"))
        config = get_config()
        total = sum(item["price"] * item["quantity"] for item in payload.get("items", []))
        return {
            "order_id": payload.get("order_id"),
            "user_email": user.get("email"),
            "currency": config["currency"],
            "total": total,
        }
```

이 코드의 문제는 한두 개가 아닙니다.

- `find_user()`와 `create_order()`에 시그니처가 거의 없습니다.
- `get_config()`가 `Any`를 반환해서 아래 코드 전체가 느슨해집니다.
- `payload.get()` 중심 구현이라 필수 필드가 빠져도 조용히 지나갑니다.
- `user`가 `None`일 수 있는데 바로 `user.get()`을 호출합니다.

### 2단계: 공개 함수와 반환 타입부터 먼저 적기

실무에서는 지역 변수보다 시그니처가 우선입니다. 호출자가 가장 먼저 보는 계약이기 때문입니다.

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}
```

이 시점부터 검사기는 최소한 아래 사실을 추적할 수 있습니다.

- `find_user()`는 없을 수도 있습니다.
- `order_id`는 문자열이나 정수일 수 있습니다.
- `get_config()`는 더 이상 무제한 `Any`가 아닙니다.

### 3단계: `Any`를 없애고 경계 헬퍼를 분리하기

이제 "무엇이 들어오는가"보다 "무엇을 신뢰할 수 있는가"를 코드로 분리합니다.

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

class OrderSummary(TypedDict):
    order_id: str
    user_email: str
    currency: str
    total: int

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

def parse_order_id(order_id: int | str) -> int:
    if isinstance(order_id, int):
        return order_id
    if order_id.isdigit():
        return int(order_id)
    raise ValueError("order_id must be an int or numeric string")

def require_user_email(user: UserRecord | None) -> str:
    if user is None:
        raise LookupError("user not found")
    if not user["is_active"]:
        raise ValueError("inactive user cannot create orders")
    return user["email"]
```

여기서 중요한 변화는 `...` 같은 빈 본문을 두지 않고, 실제로 복사해 실행할 수 있는 코드를 제공한다는 점입니다. 좋은 예시는 조언이 아니라 동작하는 기준선이어야 합니다.

### 4단계: 서비스 메서드를 명확한 계약으로 다시 쓰기

```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    email: str
    is_active: bool

class OrderItem(TypedDict):
    name: str
    price: int
    quantity: int

class OrderPayload(TypedDict):
    order_id: int | str
    user_id: int
    items: list[OrderItem]

class OrderSummary(TypedDict):
    order_id: str
    user_email: str
    currency: str
    total: int

def find_user(user_id: int) -> UserRecord | None:
    if user_id == 1:
        return {"id": 1, "email": "buyer@example.com", "is_active": True}
    return None

def get_config() -> dict[str, str | int | bool]:
    return {"currency": "KRW", "retry_limit": 3, "sandbox": False}

def parse_order_id(order_id: int | str) -> int:
    if isinstance(order_id, int):
        return order_id
    if order_id.isdigit():
        return int(order_id)
    raise ValueError("order_id must be an int or numeric string")

def require_user_email(user: UserRecord | None) -> str:
    if user is None:
        raise LookupError("user not found")
    if not user["is_active"]:
        raise ValueError("inactive user cannot create orders")
    return user["email"]

class OrderService:
    def create_order(self, payload: OrderPayload) -> OrderSummary:
        order_id = parse_order_id(payload["order_id"])
        user_email = require_user_email(find_user(payload["user_id"]))
        config = get_config()
        currency_value = config["currency"]
        if not isinstance(currency_value, str):
            raise ValueError("currency config must be a string")

        total = sum(item["price"] * item["quantity"] for item in payload["items"])
        return {
            "order_id": str(order_id),
            "user_email": user_email,
            "currency": currency_value,
            "total": total,
        }
```

이제 함수 본문은 세 가지를 분명히 합니다.

- 입력은 `OrderPayload`여야 합니다.
- 존재하지 않는 사용자와 잘못된 `order_id`는 조용히 지나가지 않습니다.
- 반환값도 `OrderSummary`로 고정되어 호출자가 구조를 예측할 수 있습니다.

### 5단계: 검사기 통과를 확인해 hardening pass를 닫기

위처럼 정리한 뒤에는 검사 결과까지 확인해야 합니다.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
files = ["order_service.py"]
disallow_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true
no_implicit_optional = true
```

```text
$ mypy order_service.py
Success: no issues found in 1 source file
```

이 검증이 있어야 "좋아 보이는 조언"이 아니라 "실제로 통과하는 기준"이 됩니다.

### 6단계: 우선순위 규칙을 이 모듈에서 추출하기

방금 한 정리 작업을 일반화하면, 타입 힌트 우선순위는 다음 순서가 됩니다.

1. **공개 함수 시그니처와 반환 타입을 먼저 적습니다.** `find_user()`, `create_order()`가 여기에 해당합니다.
2. **`Any`가 퍼지는 경계를 먼저 끊습니다.** `get_config()` 같은 함수가 대표적입니다.
3. **Union은 타입 좁히기 헬퍼로 처리합니다.** `parse_order_id()`처럼 분기 의미를 이름으로 끌어올립니다.
4. **도구 설정으로 팀 규칙을 남깁니다.** `disallow_untyped_defs`, `warn_return_any`처럼 반복 가능한 기준이어야 합니다.

즉, 좋은 베스트 프랙티스는 추상 체크리스트가 아니라 **모듈을 안전하게 바꾸는 순서**입니다.

## 여기서 먼저 봐야 할 점

- 지역 변수 전체보다 공개 시그니처와 반환 타입이 우선입니다.
- `Any`는 한 번 퍼지면 아래 코드 전체의 검사를 약화시킵니다.
- `Union`은 헬퍼 함수와 타입 좁히기로 정리하는 편이 읽기 쉽습니다.
- 마지막에는 반드시 검사기 통과 같은 검증 단계가 따라와야 합니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| 예제 본문을 `...`로 비워 둠 | 독자가 바로 실행하거나 복사할 수 없습니다 | 실제로 동작하는 코드로 끝까지 채웁니다 |
| 지역 변수 타입부터 전부 적음 | 장황한데 비해 계약 강화 효과가 작습니다 | 공개 시그니처와 반환 타입부터 적습니다 |
| `Any`를 임시 해결책으로 남겨 둠 | 아래 코드 전체가 느슨해집니다 | 구체 타입이나 좁은 Union으로 바꿉니다 |
| Optional/Union을 분기 없이 바로 사용함 | 런타임 오류와 타입 오류가 동시에 생깁니다 | helper 함수로 의미 있는 좁히기를 합니다 |
| 문서 조언만 남기고 검증 결과를 안 보여 줌 | 팀 기준으로 연결되기 어렵습니다 | mypy/pyright 같은 통과 결과를 남깁니다 |

## 실무에서는 이렇게 연결됩니다

- 새 프로젝트는 첫 공개 API부터 시그니처와 반환 타입을 명시합니다.
- 레거시 프로젝트는 파일을 건드릴 때 hardening pass를 같이 수행합니다.
- Pydantic은 입력 경계에 두고, 내부 서비스 계층은 정확한 함수 시그니처로 단단하게 만듭니다.
- 팀은 `pyproject.toml` 같은 설정 파일로 새 코드 기준을 남깁니다.

## 실무 판단 기준

경험 많은 개발자는 타입 힌트를 "코드 장식"이 아니라 리팩터링 안전장치로 봅니다. 그래서 가장 먼저 손대는 곳도 항상 비슷합니다. 다른 모듈이 호출하는 공개 함수, 실패 비용이 큰 경계, `Any`가 새어 나오는 중심 헬퍼, 그리고 팀이 반복적으로 실수하는 경로입니다.

중요한 것은 100% 표기율이 아니라 중요한 경로의 계약 품질입니다. 한 모듈을 제대로 단단하게 만드는 작업이, 저장소 전체에 얕은 타입을 뿌리는 것보다 훨씬 큰 효과를 냅니다.

## 체크리스트

- [ ] 공개 함수 시그니처와 반환 타입부터 먼저 보강했습니다
- [ ] `Any`가 퍼지는 함수를 구체 타입으로 줄였습니다
- [ ] `Union` 처리 경로를 helper 함수로 분리했습니다
- [ ] before/after 예제가 실제로 실행 가능한 코드가 되도록 비어 있는 본문을 없앴습니다
- [ ] 검사기 설정과 통과 결과로 hardening pass를 검증했습니다

## 연습 문제

1. 기존 서비스 모듈 하나를 골라 `find_*`, `get_*`, `create_*` 같은 공개 함수의 반환 타입만 먼저 보강해 보세요.

2. `Any`를 반환하는 설정 함수나 파서 함수를 찾아, 구체 타입 또는 좁은 Union으로 바꾼 뒤 영향 범위를 적어 보세요.

3. `order_service.py` 예제에 할인 쿠폰 필드를 추가하고, `coupon_code: str | None`을 안전하게 처리하는 helper를 직접 작성해 보세요.

## 정리

타입 힌트를 잘 쓴다는 것은 모든 줄에 주석을 다는 일이 아닙니다. 공개 시그니처와 반환 타입을 먼저 단단하게 만들고, `Any`가 퍼지는 지점을 끊고, Union을 의미 있는 helper로 좁히고, 마지막에 검사기 통과로 검증하는 일이 더 중요합니다. 그 순서가 잡혀 있어야 앞선 정적 검사와 런타임 검증도 실제 팀 규칙으로 이어집니다.

이 시리즈에서는 기본 타입, `Optional`, `Union`, `Callable`, `TypedDict`, `dataclass`, `Protocol`, `Generic`, mypy, pyright, Pydantic까지 Python 타입 힌트의 전체 그림을 살펴봤습니다. 이제 남은 일은 완벽주의가 아니라, 중요한 경로부터 반복 가능한 hardening pass를 계속 쌓아 가는 것입니다.

## 처음 질문으로 돌아가기

- **타입 힌트는 어디에 먼저 붙여야 투자 대비 효과가 클까요?**
  - 본문의 기준은 타입 힌트를 잘 쓰는 기준를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`Any`가 퍼진 코드는 어떤 순서로 줄여야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **반환 타입, 공개 API, 내부 헬퍼 중 무엇을 먼저 단단하게 만들어야 할까요?**
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
- [Type Hints in Python 101 (9/10): Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- **타입 힌트를 잘 쓰는 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing](https://docs.python.org/3/library/typing.html)
- [mypy 문서 — Using mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide — Type Annotations](https://google.github.io/styleguide/pyguide.html#319-type-annotations)
- [Typing Python Libraries](https://typing.python.org/en/latest/guides/libraries.html)

Tags: Python, Type Hints, 베스트 프랙티스, 점진적 타이핑, 코드 품질, 팀 가이드라인
