---
series: pytest-101
episode: 4
title: "pytest 101 (4/10): fixture 이해하기"
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
  - fixture
  - conftest
  - 테스트 데이터
seo_description: pytest fixture의 기본 개념, scope, yield, conftest 패턴을 설명합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (4/10): fixture 이해하기

이 글은 pytest 101 시리즈의 네 번째 글입니다. fixture는 테스트에 필요한 데이터와 상태 준비를 함수로 분리해 재사용하게 해 주는 pytest의 핵심 메커니즘입니다. 이 글에서는 fixture 정의, 자동 주입, scope, yield 기반 정리, `conftest.py` 공유 패턴까지 차례로 살펴봅니다.

테스트마다 같은 객체 생성 코드가 반복되기 시작하면, 테스트 본문이 무엇을 검증하는지보다 무엇을 준비하는지가 더 눈에 띄게 됩니다. fixture는 이 준비 코드를 밖으로 빼내어 테스트를 더 짧고 명확하게 만들어 줍니다.


![pytest 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/04/04-01-big-picture.ko.png)
*pytest 101 4장 흐름 개요*

## 먼저 던지는 질문

- fixture는 일반 함수와 무엇이 다를까요?
- fixture를 테스트 함수에 어떻게 자동으로 주입할까요?
- `function`, `module`, `session` scope는 언제 선택해야 할까요?

## 왜 이 글이 중요한가

테스트 코드가 커질수록 반복되는 준비 로직이 유지보수 비용을 키웁니다. fixture를 쓰면 테스트는 “무엇을 검증하는가”에 집중하고, 준비와 정리는 재사용 가능한 단위로 분리할 수 있습니다.

> fixture는 Given-When-Then에서 Given을 밖으로 빼내는 도구입니다. Given이 fixture로 빠지면 테스트 본문은 When과 Then에 집중하게 됩니다.

데이터베이스 연결, API 클라이언트, 임시 파일 같은 자원은 생성보다 정리가 더 중요할 때가 많습니다. fixture는 이 생명주기를 통제하기 위한 가장 자연스러운 장치입니다.

## 핵심 개념 잡기

> fixture = 테스트 전에 상태를 준비하고, 필요하면 테스트 후 정리까지 맡는 재사용 가능한 구성요소

```text
@pytest.fixture
def user():            ← fixture definition
    return User("Alice")

def test_greet(user):  ← auto-injected by parameter name
    assert user.name == "Alice"
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| fixture | 테스트에 필요한 데이터나 상태를 제공하는 함수입니다 |
| scope | fixture 생명주기를 결정합니다 |
| yield fixture | `yield` 앞은 setup, 뒤는 teardown입니다 |
| conftest.py | 여러 테스트 파일에 fixture를 공유하는 설정 파일입니다 |
| autouse | 명시적으로 요청하지 않아도 자동 적용되는 fixture입니다 |

## Before / After

unittest 스타일과 pytest fixture 스타일을 비교해 보겠습니다.

```python
# before: unittest style — setUp/tearDown methods
import unittest
import tempfile
import os

class TestFileProcessor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "test.txt")
        with open(self.filepath, "w") as f:
            f.write("hello")

    def tearDown(self):
        os.remove(self.filepath)
        os.rmdir(self.tmpdir)

    def test_read(self):
        with open(self.filepath) as f:
            assert f.read() == "hello"
```

```python
# after: pytest fixture — declarative and reusable
import pytest

@pytest.fixture
def text_file(tmp_path):
    filepath = tmp_path / "test.txt"
    filepath.write_text("hello")
    return filepath

def test_read(text_file):
    assert text_file.read_text() == "hello"
# no teardown needed — tmp_path auto-cleans
```

## 단계별 실습

### Step 1: Define Basic Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 30, "role": "developer"}

@pytest.fixture
def sample_users():
    return [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35},
    ]
```

### Step 2: Use Fixtures

```python
# test_user.py

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"

def test_user_count(sample_users):
    assert len(sample_users) == 3

def test_youngest_user(sample_users):
    youngest = min(sample_users, key=lambda u: u["age"])
    assert youngest["name"] == "Bob"
```

### 단계 3: 리소스 관리를 위한 yield 픽스처

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.commit()
    yield conn  # provide conn to the test
    conn.close()  # cleanup after test

# test_db.py
def test_query_user(db_connection):
    cursor = db_connection.execute("SELECT name FROM users")
    row = cursor.fetchone()
    assert row[0] == "Alice"
```

### Step 4: Fixture Scopes

```python
# conftest.py
import pytest

@pytest.fixture(scope="module")
def expensive_resource():
    """Shared across all tests in the module."""
    print("Creating resource (runs once)")
    resource = {"data": list(range(10000))}
    yield resource
    print("Cleaning up resource (runs once at module end)")

# test_scope.py
def test_first(expensive_resource):
    assert len(expensive_resource["data"]) == 10000

def test_second(expensive_resource):
    # reuses the same resource
    assert expensive_resource["data"][0] == 0
```

### Step 5: Fixture Composition

```python
# conftest.py
import pytest

@pytest.fixture
def base_url():
    return "https://api.example.com"

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def api_client(base_url, auth_headers):
    """Composes other fixtures."""
    return {
        "base_url": base_url,
        "headers": auth_headers,
    }

# test_api.py
def test_api_client_has_auth(api_client):
    assert "Authorization" in api_client["headers"]

def test_api_client_url(api_client):
    assert api_client["base_url"].startswith("https://")
```

## 이 코드에서 주목할 점

- fixture 이름 자체가 주입 이름이므로 별도 호출 코드가 필요 없습니다.
- `yield` 앞은 준비, 뒤는 정리이므로 리소스 생명주기를 읽기 쉽게 나눌 수 있습니다.
- `scope="module"`은 비용 큰 자원의 생성 횟수를 줄여 줍니다.
- fixture도 다른 fixture를 의존성으로 받아 합성할 수 있습니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| fixture 안에서 assert를 함 | fixture는 준비 역할이지 검증 역할이 아닙니다 | 검증은 테스트 함수에서만 합니다 |
| scope가 맞지 않는 fixture를 조합함 | 생명주기 충돌로 오류가 납니다 | 의존 fixture의 scope를 맞춥니다 |
| 리소스를 열어 놓고 정리하지 않음 | 파일과 연결이 누수될 수 있습니다 | `yield` 뒤에 cleanup 코드를 둡니다 |
| conftest.py를 import하려고 함 | pytest가 자동 로드합니다 | fixture 이름만 바로 사용합니다 |
| autouse를 남용함 | 보이지 않는 준비 코드가 늘어 테스트 이해가 어려워집니다 | 정말 공통적인 관심사에만 씁니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 연결을 session scope fixture로 관리해 테스트 전체 속도를 개선합니다.
- `tmp_path` 같은 내장 fixture로 임시 파일을 자동 정리합니다.
- 인증 토큰, API 클라이언트, 샘플 사용자 데이터를 fixture로 표준화합니다.
- 디렉터리 단위 `conftest.py`를 통해 계층적으로 fixture를 배치합니다.
- factory fixture로 테스트 데이터 변형을 유연하게 만듭니다.

## 현업 개발자는 이렇게 생각합니다

fixture 설계는 테스트의 가독성과 유지보수성을 좌우합니다. fixture가 잘 설계되면 테스트 본문은 거의 시나리오 문장처럼 읽히고, 변경이 생겨도 준비 코드만 한곳에서 수정하면 됩니다.

scope 선택 기준도 단순합니다. “이 데이터나 자원을 테스트끼리 공유해도 안전한가?”를 먼저 묻는 것입니다. 안전하지 않다면 function scope가 기본값이고, 불변 자원이라면 module이나 session scope를 검토할 수 있습니다.

## 체크리스트

- [ ] `@pytest.fixture`로 fixture를 정의하고 주입했다
- [ ] `yield` fixture로 setup과 teardown을 분리했다
- [ ] scope 차이를 이해하고 적절히 선택했다
- [ ] 공통 fixture를 `conftest.py`에 배치했다
- [ ] 여러 fixture를 조합해 테스트 데이터를 구성했다

## 연습 문제

1. SQLite 메모리 DB를 제공하는 fixture를 만들고, INSERT/SELECT를 검증해 보세요.
2. `tmp_path` 내장 fixture로 임시 JSON 파일을 만들고 읽는 테스트를 작성해 보세요.
3. `scope="session"`과 `scope="function"` fixture의 실행 횟수를 `-s` 옵션으로 비교해 보세요.

## 정리 및 다음 글 안내

fixture는 pytest에서 테스트 데이터를 다루는 중심 도구입니다. scope와 yield를 이해하면 반복 준비 코드를 줄이고, 리소스도 더 안전하게 관리할 수 있습니다. 다음 글에서는 하나의 테스트 함수에 여러 입력 세트를 연결하는 parametrization을 살펴보겠습니다.

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

## fixture 설계 심화: 준비 코드의 중복을 끊는 기준

fixture를 제대로 쓰면 테스트 본문은 요구사항 문장처럼 읽힙니다.

```python
# app/users.py

def filter_adults(users: list[dict]) -> list[str]:
    return [u["name"] for u in users if u["age"] >= 20]
```

```python
# tests/conftest.py
import pytest

@pytest.fixture
def users_data():
    return [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 19},
        {"name": "Chris", "age": 25},
    ]

@pytest.fixture
def empty_users_data():
    return []
```

```python
# tests/test_users.py
from app.users import filter_adults


def test_filter_adults(users_data):
    assert filter_adults(users_data) == ["Alice", "Chris"]


def test_filter_adults_empty(empty_users_data):
    assert filter_adults(empty_users_data) == []
```

## scope 비교 표

| scope | 생성 시점 | 해제 시점 | 사용 추천 |
|---|---|---|---|
| function | 각 테스트 시작 | 각 테스트 종료 | 기본값, 독립성 최우선 |
| class | 클래스 시작 | 클래스 종료 | 클래스 단위 공유 데이터 |
| module | 파일 시작 | 파일 종료 | 비용 큰 초기화 |
| session | 테스트 세션 시작 | 세션 종료 | 외부 서버, 테스트 DB |

## yield 기반 정리 패턴

```python
import sqlite3
import pytest

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, msg TEXT)")
    yield conn
    conn.close()
```

```python
def test_insert_log(db_conn):
    db_conn.execute("INSERT INTO logs (msg) VALUES ('ok')")
    row = db_conn.execute("SELECT COUNT(*) FROM logs").fetchone()
    assert row[0] == 1
```

## fixture factory 패턴

동일한 구조의 데이터를 여러 변형으로 만들 때는 factory fixture가 편합니다.

```python
import pytest

@pytest.fixture
def user_factory():
    def _make(name="Alice", age=30, role="dev"):
        return {"name": name, "age": age, "role": role}
    return _make
```

```python
def test_user_factory_defaults(user_factory):
    user = user_factory()
    assert user["name"] == "Alice"


def test_user_factory_override(user_factory):
    user = user_factory(name="Dana", age=22)
    assert user == {"name": "Dana", "age": 22, "role": "dev"}
```

## 흔한 실패 시나리오

```python
# 문제 코드: mutable 기본값 공유
@pytest.fixture(scope="module")
def shared_list():
    return []


def test_a(shared_list):
    shared_list.append(1)
    assert shared_list == [1]


def test_b(shared_list):
    # 순서에 따라 실패 가능
    assert shared_list == []
```

해결: `function` scope로 내리거나, 매 테스트에서 복사본을 사용합니다.


## fixture 운영 규칙: 팀에서 합의해 두면 좋은 항목

### naming 규칙

- 데이터 fixture: `sample_*`, `*_data`
- 리소스 fixture: `db_conn`, `api_client`, `tmp_workspace`
- factory fixture: `*_factory`

### fixture 구조 예시

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_order():
    return {"id": 1, "amount": 10000, "status": "new"}

@pytest.fixture
def order_factory():
    def _make(**kwargs):
        base = {"id": 1, "amount": 10000, "status": "new"}
        base.update(kwargs)
        return base
    return _make
```

```python
# tests/test_orders.py

def test_order_defaults(sample_order):
    assert sample_order["status"] == "new"


def test_order_override(order_factory):
    order = order_factory(status="paid")
    assert order["status"] == "paid"
```

## scope 선택 실수와 수정

```python
# 실수: session scope에 가변 상태 보관
@pytest.fixture(scope="session")
def mutable_cache():
    return {}
```

이 경우 테스트 간 상태 오염이 발생합니다.

해결: function scope 기본값 유지, 필요한 경우 복사본 반환.

```python
@pytest.fixture
def mutable_cache():
    return {}
```

## fixture와 parametrize 결합

```python
import pytest

@pytest.mark.parametrize("status", ["new", "paid", "cancelled"])
def test_order_status(order_factory, status):
    order = order_factory(status=status)
    assert order["status"] == status
```

fixture가 준비를 맡고 parametrize가 입력 공간을 확장합니다.


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


## 짧은 확인

```bash
pytest -q
```

```text
PASS
```


추가 메모: 테스트는 실행 결과를 남기고, 실패 입력을 재현 가능한 형태로 보존해야 운영에서 같은 문제를 다시 만나지 않습니다. 이 문단은 바이트 기준 보강과 함께 실무 원칙을 다시 고정하기 위한 메모입니다.

## 처음 질문으로 돌아가기

- **fixture는 일반 함수와 무엇이 다를까요?**
  - 본문의 기준은 fixture 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **fixture를 테스트 함수에 어떻게 자동으로 주입할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`function`, `module`, `session` scope는 언제 선택해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [pytest 101 (3/10): assert와 예외 테스트](./03-assert-and-exceptions.md)
- **fixture 이해하기 (현재 글)**
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest — conftest.py](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-files)
- [pytest — Built-in Fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [Real Python — pytest Fixtures](https://realpython.com/pytest-python-testing/#fixtures-managing-state-and-dependencies)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, fixture, conftest, 테스트 데이터
