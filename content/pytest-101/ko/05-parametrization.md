---
series: pytest-101
episode: 5
title: "pytest 101 (5/10): parametrization으로 테스트 케이스 늘리기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - parametrize
  - 테스트 케이스
  - 데이터 주도 테스트
seo_description: pytest parametrize로 같은 검증 로직에 여러 입력을 연결하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (5/10): parametrization으로 테스트 케이스 늘리기

이 글은 pytest 101 시리즈의 다섯 번째 글입니다. 같은 로직을 여러 입력값으로 반복 검증해야 할 때, 테스트 함수를 복사해 늘리는 대신 `@pytest.mark.parametrize`로 데이터만 추가하는 방식이 훨씬 낫습니다. 이 글에서는 기본 문법, 다중 파라미터, 테스트 ID, 중첩 parametrize 패턴을 정리합니다.

테스트 코드가 늘어나는 가장 흔한 이유는 검증 로직이 아니라 입력 데이터가 많아졌기 때문입니다. 이때 함수를 계속 복사하면 테스트는 금방 장황해지고, 케이스 하나를 추가할 때마다 중복도 함께 늘어납니다.


![pytest 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/05/05-01-big-picture.ko.png)
*pytest 101 5장 흐름 개요*

## 먼저 던지는 질문

- 같은 로직을 여러 입력으로 검증할 때 함수를 복사하지 않으려면 어떻게 해야 할까요?
- `@pytest.mark.parametrize`의 기본 문법은 어떻게 읽어야 할까요?
- 각 테스트 케이스에 읽기 좋은 이름을 붙이려면 어떻게 해야 할까요?

## 왜 이 글이 중요한가

입력 조합이 늘어날수록 테스트 품질은 두 방향으로 갈립니다. 하나는 복사-붙여넣기로 테스트 파일이 비대해지는 방향이고, 다른 하나는 같은 로직을 유지한 채 데이터만 늘리는 방향입니다. parametrization은 두 번째 방향을 가능하게 합니다.

> 테스트 5개를 복사하는 대신 데이터 5줄을 추가합니다. 로직은 하나이고, 달라지는 것은 입력과 기대값뿐입니다.

경계값, 빈 문자열, 특수문자처럼 꼭 검증해야 하는 케이스는 많습니다. parametrization이 없으면 이런 케이스를 빠짐없이 추가하기가 점점 번거로워집니다.

## 핵심 개념 잡기

> parametrize = 하나의 테스트 함수 + 여러 데이터 세트 → N개의 독립 테스트

```text
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),      ← test 1
    ("", 0),            ← test 2
    ("hi", 2),          ← test 3
])
def test_length(input, expected):
    assert len(input) == expected
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| parametrize | 테스트 파라미터를 주입하는 데코레이터입니다 |
| 테스트 ID | 각 파라미터 조합에 붙는 식별자입니다 |
| pytest.param | 개별 케이스에 ID나 마크를 부여합니다 |
| indirect | parametrize 값을 fixture로 전달합니다 |
| 데카르트 곱 | 여러 parametrize 데코레이터를 쌓으면 조합 수가 곱해집니다 |

## Before / After

복사-붙여넣기 방식과 parametrize 방식을 비교해 보겠습니다.

```python
# before: duplicate function per input
def test_is_palindrome_radar():
    assert is_palindrome("radar") is True

def test_is_palindrome_hello():
    assert is_palindrome("hello") is False

def test_is_palindrome_empty():
    assert is_palindrome("") is True

def test_is_palindrome_single():
    assert is_palindrome("a") is True
```

```python
# after: just list the data
import pytest

@pytest.mark.parametrize("word,expected", [
    ("radar", True),
    ("hello", False),
    ("", True),
    ("a", True),
])
def test_is_palindrome(word, expected):
    assert is_palindrome(word) is expected
```

## 단계별 실습

### Step 1: Basic Parametrize

```python
# test_math.py
import pytest

def add(a, b):
    return a + b

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
    (-5, -3, -8),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Step 2: String Parameters

```python
# test_string.py
import pytest

def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-")

@pytest.mark.parametrize("input_text,expected", [
    ("Hello World", "hello-world"),
    ("  spaces  ", "spaces"),
    ("UPPER CASE", "upper-case"),
    ("already-slug", "already-slug"),
    ("multiple   spaces", "multiple---spaces"),
])
def test_slugify(input_text, expected):
    assert slugify(input_text) == expected
```

### Step 3: Exception Case Parametrize

```python
# test_validation.py
import pytest

def parse_age(value: str) -> int:
    age = int(value)
    if age < 0 or age > 150:
        raise ValueError(f"Invalid age: {age}")
    return age

@pytest.mark.parametrize("value,expected", [
    ("25", 25),
    ("0", 0),
    ("150", 150),
])
def test_parse_age_valid(value, expected):
    assert parse_age(value) == expected

@pytest.mark.parametrize("value", ["-1", "151", "999"])
def test_parse_age_invalid(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

### Step 4: Custom IDs

```python
# test_with_ids.py
import pytest

@pytest.mark.parametrize("email,valid", [
    pytest.param("user@example.com", True, id="normal-email"),
    pytest.param("@example.com", False, id="missing-local"),
    pytest.param("user@", False, id="missing-domain"),
    pytest.param("", False, id="empty-string"),
    pytest.param("user@exam ple.com", False, id="space-in-domain"),
])
def test_validate_email(email, valid):
    result = "@" in email and len(email.split("@")) == 2
    has_domain = result and len(email.split("@")[1]) > 0
    has_local = result and len(email.split("@")[0]) > 0
    has_no_space = " " not in email
    assert (has_domain and has_local and has_no_space) == valid
```

### Step 5: Cartesian Product (Stacked Parametrize)

```python
# test_cartesian.py
import pytest

@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
@pytest.mark.parametrize("status", [200, 404, 500])
def test_http_response(method, status):
    """3 methods x 3 statuses = 9 tests generated."""
    response = {"method": method, "status": status}
    assert response["method"] in ["GET", "POST", "PUT", "DELETE"]
    assert isinstance(response["status"], int)
```

## 이 코드에서 주목할 점

- 각 파라미터 조합은 독립 테스트로 실행되므로 하나가 실패해도 나머지는 계속 확인됩니다.
- `pytest.param(..., id=...)`를 쓰면 테스트 출력이 훨씬 읽기 좋아집니다.
- 여러 parametrize를 쌓으면 조합 수가 곱해집니다.
- 정상 케이스와 예외 케이스를 분리하면 테스트 의도가 더 선명해집니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 파라미터 이름 문자열에 공백을 넣음 | 파싱 오류가 날 수 있습니다 | `"a,b"`처럼 쓰거나 리스트를 사용합니다 |
| 튜플 길이가 제각각임 | 파라미터 개수와 맞지 않아 실패합니다 | 모든 케이스의 요소 수를 맞춥니다 |
| 한 블록에 너무 많은 케이스를 넣음 | 가독성이 급격히 떨어집니다 | 범주별로 parametrize를 나눕니다 |
| 가변 객체를 그대로 파라미터로 넘김 | 테스트 사이에 상태가 공유될 수 있습니다 | 복사하거나 tuple처럼 불변 구조를 사용합니다 |
| ID 없이 복잡한 데이터를 씀 | 실패 출력이 읽기 어려워집니다 | 의미 있는 `id`를 붙입니다 |

## 실무에서 이렇게 쓰입니다

- 유효성 검사 함수의 경계값을 묶어서 한 번에 검증합니다.
- 여러 HTTP 상태 코드 응답을 빠르게 확인합니다.
- 국제화 테스트에서 언어별 입력 데이터를 정리합니다.
- 쿼리 필터 조합을 데카르트 곱으로 커버합니다.
- JSON/YAML에 테스트 데이터를 분리해 데이터 주도 테스트로 확장하기도 합니다.

## 현업 개발자는 이렇게 생각합니다

parametrize는 “같은 검증 로직, 다른 데이터”라는 상황을 가장 깔끔하게 해결합니다. 테스트 수는 늘어나도 함수 수는 늘리지 않기 때문에, 읽기와 유지보수가 모두 쉬워집니다.

실무에서는 버그가 재현된 입력값을 parametrize 목록에 추가해 회귀 테스트로 남기는 경우가 많습니다. 이렇게 하면 같은 버그가 다시 들어와도 바로 잡을 수 있습니다.

## 체크리스트

- [ ] `@pytest.mark.parametrize`로 테스트를 작성했다
- [ ] 정상 케이스와 예외 케이스를 분리했다
- [ ] `pytest.param`으로 테스트 ID를 붙였다
- [ ] 중첩 parametrize로 조합 테스트를 만들었다
- [ ] `-v` 출력에서 개별 테스트 케이스를 확인했다

## 연습 문제

1. `fizzbuzz(n)` 함수를 만들고 1부터 15까지의 케이스를 parametrize로 작성해 보세요.
2. 비밀번호 검증 함수를 만들고 최소 길이, 대문자, 숫자 포함 조건을 parametrize로 테스트해 보세요.
3. HTTP method와 Content-Type 조합을 중첩 parametrize로 만든 뒤 총 몇 개 테스트가 생성되는지 확인해 보세요.

## 정리 및 다음 글 안내

parametrize는 데이터 주도 테스트의 핵심입니다. 같은 로직을 반복 복사하는 대신, 입력 데이터만 추가해 테스트 범위를 넓힐 수 있습니다. 다음 글에서는 외부 API, DB, 환경처럼 테스트 바깥 의존성을 다루기 위한 mock과 monkeypatch를 살펴보겠습니다.

## 실전 패턴 추가: fixture, parametrization, mock을 함께 설계하기

테스트 파일이 커질수록 중요한 것은 개별 문법보다 테스트 경계를 일정하게 유지하는 일입니다. 특히 fixture로 상태를 준비하고, `@pytest.mark.parametrize`로 입력 집합을 확장하고, mock으로 외부 의존성을 분리하는 세 가지를 한 흐름으로 묶으면 테스트 유지보수 비용이 크게 줄어듭니다.

```python
# tests/test_order_service.py
from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

import pytest


@dataclass
class Order:
    item: str
    qty: int


class InventoryClient:
    def reserve(self, item: str, qty: int) -> bool:  # pragma: no cover
        raise NotImplementedError


class OrderService:
    def __init__(self, client: InventoryClient) -> None:
        self.client = client

    def place(self, order: Order) -> str:
        if order.qty <= 0:
            raise ValueError("qty must be positive")
        ok = self.client.reserve(order.item, order.qty)
        return "confirmed" if ok else "rejected"


@pytest.fixture
def inventory_client() -> Mock:
    return Mock(spec=InventoryClient)


@pytest.fixture
def order_service(inventory_client: Mock) -> OrderService:
    return OrderService(client=inventory_client)


@pytest.mark.parametrize(
    "order,expected",
    [
        (Order("book", 1), "confirmed"),
        (Order("book", 3), "confirmed"),
        (Order("book", 5), "rejected"),
    ],
)
def test_place_orders(order_service: OrderService, inventory_client: Mock, order: Order, expected: str) -> None:
    inventory_client.reserve.return_value = expected == "confirmed"
    assert order_service.place(order) == expected


def test_place_rejects_invalid_quantity(order_service: OrderService) -> None:
    with pytest.raises(ValueError, match="qty must be positive"):
        order_service.place(Order("book", 0))
```

위 구조의 핵심은 테스트 목적별 분리입니다. fixture는 준비, parametrization은 입력 공간, mock은 외부 의존성 제어를 담당합니다. 팀 단위에서는 이 분리를 지켜야 테스트를 고칠 때 영향 범위를 빠르게 읽을 수 있습니다.

또한 fixture scope를 무조건 넓히지 않는 편이 안전합니다. DB 연결이나 임시 디렉터리처럼 생성 비용이 큰 자원만 `module` 또는 `session`으로 올리고, 나머지는 `function` scope로 두어 테스트 독립성을 유지하는 것이 좋습니다.

## 파라미터 설계 심화: 데이터만 바꾸고 검증 로직은 유지하기

parametrize의 장점은 테스트 함수 수를 늘리지 않고 입력 공간을 넓히는 점입니다.

```python
# validator.py

def validate_username(name: str) -> bool:
    if not 3 <= len(name) <= 20:
        return False
    return name.replace("_", "").isalnum()
```

```python
# test_validator.py
import pytest
from validator import validate_username

@pytest.mark.parametrize(
    "name,expected",
    [
        pytest.param("abc", True, id="min-length"),
        pytest.param("ab", False, id="too-short"),
        pytest.param("user_name", True, id="underscore"),
        pytest.param("bad name", False, id="space"),
        pytest.param("x" * 21, False, id="too-long"),
    ],
)
def test_validate_username(name, expected):
    assert validate_username(name) is expected
```

## CLI 출력 확인

```bash
pytest test_validator.py -v
```

```text
test_validator.py::test_validate_username[min-length] PASSED
test_validator.py::test_validate_username[too-short] PASSED
...
========================= 5 passed =========================
```

## 정상/실패 케이스를 한 함수에서 다루는 패턴

```python
# parser.py

def parse_port(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError("port out of range")
    return port
```

```python
# test_parser.py
import pytest
from parser import parse_port

@pytest.mark.parametrize("value,expected", [("80", 80), ("443", 443)])
def test_parse_port_ok(value, expected):
    assert parse_port(value) == expected

@pytest.mark.parametrize("value", ["0", "70000", "-1"])
def test_parse_port_fail(value):
    with pytest.raises(ValueError, match="out of range"):
        parse_port(value)
```

## 조합 폭발 제어

중첩 parametrize는 강력하지만 조합 수가 빠르게 커집니다.

| method 수 | status 수 | 생성 테스트 수 |
|---|---|---|
| 3 | 3 | 9 |
| 5 | 6 | 30 |
| 8 | 10 | 80 |

필요한 경계만 추려 조합을 제한해야 테스트 시간이 유지됩니다.

## Before/After 리팩터링

```python
# before

def test_price_case1():
    assert discount(10000, "VIP") == 9000

def test_price_case2():
    assert discount(10000, "NEW") == 9500

def test_price_case3():
    assert discount(10000, "NONE") == 10000
```

```python
# after
import pytest

@pytest.mark.parametrize(
    "price,tier,expected",
    [
        (10000, "VIP", 9000),
        (10000, "NEW", 9500),
        (10000, "NONE", 10000),
    ],
)
def test_discount(price, tier, expected):
    assert discount(price, tier) == expected
```

테스트 추가는 함수 복사가 아니라 데이터 한 줄 추가로 끝납니다.


## 데이터셋 관리 패턴

파라미터 목록이 길어지면 테스트 파일 가독성이 떨어집니다. 범주별로 묶어 분리합니다.

```python
VALID_CASES = [
    ("alice", True),
    ("bob_01", True),
]

INVALID_CASES = [
    ("ab", False),
    ("bad name", False),
    ("x" * 30, False),
]
```

```python
import pytest
from validator import validate_username

@pytest.mark.parametrize("name,expected", VALID_CASES, ids=["alice", "bob_01"])
def test_username_valid(name, expected):
    assert validate_username(name) is expected

@pytest.mark.parametrize("name,expected", INVALID_CASES, ids=["short", "space", "long"])
def test_username_invalid(name, expected):
    assert validate_username(name) is expected
```

## 실패 출력 해석

```text
FAILED test_username_invalid[space] - assert True is False
```

ID가 있으면 어떤 케이스가 실패했는지 바로 읽을 수 있습니다.

## parametrize + raises 결합

```python
import pytest


def to_int(v: str) -> int:
    if not v.strip().isdigit():
        raise ValueError("not integer")
    return int(v)


@pytest.mark.parametrize("bad", ["", "a1", "-1", "1.2"])
def test_to_int_invalid(bad):
    with pytest.raises(ValueError):
        to_int(bad)
```

## 리팩터링 체크리스트

- 테스트 함수 복사가 시작되면 parametrize 전환 고려
- 케이스별 id 부여
- 정상/오류 케이스 분리
- 조합 폭발 시 범주별 샘플링


## 심화 실습 세트: 실패를 빠르게 재현하고 고정하는 루틴

아래 실습은 글 주제와 무관하게 pytest 프로젝트에서 반복적으로 쓰는 루틴입니다. 핵심은 실패를 의도적으로 만들고, 실패 메시지를 읽고, 테스트를 보강하고, 다시 통과시키는 사이클을 짧게 반복하는 것입니다.

### 실습 A: 입력 검증 함수

```python
# app/input_guard.py

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    if value.strip() == "":
        raise ValueError("value cannot be blank")
    return value.strip()
```

```python
# tests/test_input_guard.py
import pytest
from app.input_guard import require_non_empty


def test_require_non_empty_ok():
    assert require_non_empty("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_require_non_empty_blank(bad):
    with pytest.raises(ValueError, match="blank"):
        require_non_empty(bad)


def test_require_non_empty_none():
    with pytest.raises(TypeError, match="None"):
        require_non_empty(None)
```

```bash
pytest tests/test_input_guard.py -v
```

```text
tests/test_input_guard.py::test_require_non_empty_ok PASSED
tests/test_input_guard.py::test_require_non_empty_blank[] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[   ] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[\n\t] PASSED
tests/test_input_guard.py::test_require_non_empty_none PASSED
========================= 5 passed =========================
```

### 실습 B: 실패 유도 후 원인 파악

함수 구현을 일부러 아래처럼 바꿉니다.

```python
# 잘못된 구현 예시
# if value.strip() == "":
#     return value
```

다시 실행하면 실패가 즉시 재현됩니다.

```text
FAILED tests/test_input_guard.py::test_require_non_empty_blank[]
E   Failed: DID NOT RAISE <class 'ValueError'>
```

이 출력 하나로 계약 위반 지점을 바로 확인할 수 있습니다.

### 실습 C: 리팩터링 안정성 확인

```python
# app/input_guard.py (refactor)

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    normalized = value.strip()
    if normalized == "":
        raise ValueError("value cannot be blank")
    return normalized
```

같은 테스트를 실행해 모두 통과하면, 구조를 바꿔도 계약은 유지된 것입니다.

## 터미널 옵션 조합

| 명령 | 목적 |
|---|---|
| `pytest -q` | 빠른 성공/실패 확인 |
| `pytest -v` | 케이스별 통과/실패 확인 |
| `pytest -x` | 첫 실패에서 즉시 중단 |
| `pytest -k "keyword"` | 특정 범위만 선택 실행 |
| `pytest --maxfail=3` | 최대 실패 수 제한 |

## 운영 회귀 테스트 템플릿

```python
import pytest

BUG_CASES = [
    ("", ValueError),
    ("   ", ValueError),
    (None, TypeError),
]

@pytest.mark.parametrize("raw,exc", BUG_CASES)
def test_regression_cases(raw, exc):
    with pytest.raises(exc):
        require_non_empty(raw)
```

이 템플릿은 버그 이슈를 테스트 코드로 영구 보존하는 가장 단순한 형태입니다.

## 품질 체크 질문

- 실패 메시지만 보고 원인을 추론할 수 있는가
- 테스트가 실행 순서에 의존하지 않는가
- 경계값 입력이 포함되어 있는가
- 정상/오류 경로를 모두 검증하는가
- 테스트 추가가 함수 복사 대신 데이터 추가로 끝나는가


## 추가 케이스 스터디: PR 리뷰에서 자주 보는 개선 포인트

### 코드 예시

```python
# app/discount.py

def discount_price(price: int, rate: float) -> int:
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(price * (1 - rate))
```

```python
# tests/test_discount.py
import pytest
from app.discount import discount_price

@pytest.mark.parametrize(
    "price,rate,expected",
    [
        (10000, 0.0, 10000),
        (10000, 0.1, 9000),
        (10000, 1.0, 0),
    ],
)
def test_discount_price(price, rate, expected):
    assert discount_price(price, rate) == expected

@pytest.mark.parametrize("price,rate", [(-1, 0.1), (1000, -0.1), (1000, 1.1)])
def test_discount_price_invalid(price, rate):
    with pytest.raises(ValueError):
        discount_price(price, rate)
```

### 출력 예시

```bash
pytest tests/test_discount.py -v
```

```text
tests/test_discount.py::test_discount_price[10000-0.0-10000] PASSED
tests/test_discount.py::test_discount_price[10000-0.1-9000] PASSED
tests/test_discount.py::test_discount_price[10000-1.0-0] PASSED
tests/test_discount.py::test_discount_price_invalid[-1-0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000--0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000-1.1] PASSED
========================= 6 passed =========================
```

### 리뷰 포인트

- 경계값(`0`, `1.0`)이 포함되어 있는가
- 예외 타입이 구체적인가
- 실패 시 메시지로 원인을 알 수 있는가
- 데이터 추가만으로 케이스 확장이 가능한 구조인가


## 미니 점검표

- 실패 케이스를 최소 3개 이상 유지합니다.
- 경계값(최소/최대/빈값)을 포함합니다.
- 실패 메시지가 의미 있는지 확인합니다.
- CI에서 동일 명령으로 재현 가능한지 확인합니다.


## 처음 질문으로 돌아가기

- **같은 로직을 여러 입력으로 검증할 때 함수를 복사하지 않으려면 어떻게 해야 할까요?**
  - 본문의 기준은 parametrization으로 테스트 케이스 늘리기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`@pytest.mark.parametrize`의 기본 문법은 어떻게 읽어야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **각 테스트 케이스에 읽기 좋은 이름을 붙이려면 어떻게 해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [pytest 101 (3/10): assert와 예외 테스트](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): fixture 이해하기](./04-fixtures.md)
- **parametrization으로 테스트 케이스 늘리기 (현재 글)**
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — pytest.param](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param)
- [Real Python — Parametrize Tests](https://realpython.com/pytest-python-testing/#parametrize)
- [Effective Python Testing with pytest — Parametrize](https://testdriven.io/blog/testing-python/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, parametrize, 테스트 케이스, 데이터 주도 테스트
