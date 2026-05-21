---
series: pytest-101
episode: 2
title: "pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기"
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
  - 테스트 작성
  - test discovery
  - 프로젝트 구조
seo_description: pytest의 테스트 발견 규칙과 기본 프로젝트 구조를 실습 중심으로 정리합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기

이 글은 pytest 101 시리즈의 두 번째 글입니다. pytest가 테스트를 자동으로 찾는 규칙을 이해하면, 프로젝트가 커져도 테스트 구조가 흔들리지 않습니다. 이 글에서는 test discovery 규칙, `src/` 레이아웃, `conftest.py`의 역할, 그리고 다양한 실행 방법을 실제 예제와 함께 정리합니다.

테스트를 잘 써도 pytest가 파일과 함수를 발견하지 못하면 아무 의미가 없습니다. 그래서 테스트 작성의 출발점은 문법보다 구조입니다. 파일 위치, 이름 규칙, import 경로가 맞아야 팀 전체가 같은 방식으로 테스트를 실행할 수 있습니다.

## 먼저 던지는 질문

- pytest는 테스트 파일과 함수를 어떤 규칙으로 자동 탐색할까요?
- 프로덕션 코드와 테스트 코드는 어떤 디렉터리 구조로 나누는 편이 좋을까요?
- `pyproject.toml`은 왜 필요한가요?

## 큰 그림

![pytest 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/02/02-01-big-picture.ko.png)

*pytest 101 2장 흐름 개요*

## 왜 이 글이 중요한가

테스트 구조를 초기에 제대로 잡아 두면 프로젝트가 커질수록 이점이 더 커집니다. 새 팀원도 코드를 열기 전에 테스트가 어디 있는지 알 수 있고, CI 환경에서도 같은 명령으로 안정적으로 테스트를 실행할 수 있습니다.

> 테스트 코드의 위치와 이름이 곧 규칙입니다. 이 규칙만 지키면 pytest가 별도 설정 없이도 대부분을 자동으로 처리합니다.

반대로 구조가 들쭉날쭉하면, 실제 문제는 테스트 로직이 아니라 import 오류, 누락된 파일, 발견되지 않는 함수에서 시작하는 경우가 많습니다.

## 핵심 개념 잡기

> test discovery = pytest가 파일명, 클래스명, 함수명 규칙으로 테스트를 자동으로 찾는 메커니즘

```text
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── calculator.py    ← production code
└── tests/
    ├── conftest.py          ← shared fixtures
    ├── test_calculator.py   ← test code
    └── test_utils.py        ← test code
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| test discovery | 파일명·클래스명·함수명 규칙으로 테스트를 자동 탐색합니다 |
| conftest.py | fixture를 여러 테스트 파일에 공유하는 설정 파일입니다 |
| 테스트 노드 ID | `file::class::function` 형태로 개별 테스트를 식별합니다 |
| 테스트 마커 | `@pytest.mark`로 테스트를 분류하고 선택 실행합니다 |
| 종료 코드 | 0은 전체 성공, 1은 일부 실패, 2는 사용자 중단을 의미합니다 |

## Before / After

구조 없는 상태와 구조를 분리한 상태를 비교해 보겠습니다.

```python
# before: production code and test logic mixed together
# main.py
def greet(name):
    return f"Hello, {name}"

if __name__ == "__main__":
    print(greet("World"))  # manual verification
```

```python
# after: separated structure
# src/myapp/greeting.py
def greet(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"

# tests/test_greeting.py
import pytest
from myapp.greeting import greet

def test_greet():
    assert greet("World") == "Hello, World"

def test_greet_empty_name():
    with pytest.raises(ValueError):
        greet("")
```

## 단계별 실습

### Step 1: Create Project Structure

```bash
mkdir -p src/myapp tests
touch src/myapp/__init__.py
```

### Step 2: Write Production Code

```python
# src/myapp/string_utils.py
def reverse_string(s: str) -> str:
    """Reverses a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]

def count_vowels(s: str) -> int:
    """Counts the number of vowels."""
    return sum(1 for c in s.lower() if c in "aeiou")

def truncate(s: str, max_length: int = 10) -> str:
    """Truncates a string to the specified maximum length."""
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."
```

### Step 3: Write Tests

```python
# tests/test_string_utils.py
import pytest
from myapp.string_utils import reverse_string, count_vowels, truncate

class TestReverseString:
    def test_basic(self):
        assert reverse_string("hello") == "olleh"

    def test_empty(self):
        assert reverse_string("") == ""

    def test_palindrome(self):
        assert reverse_string("radar") == "radar"

    def test_type_error(self):
        with pytest.raises(TypeError):
            reverse_string(123)

class TestCountVowels:
    def test_basic(self):
        assert count_vowels("hello") == 2

    def test_no_vowels(self):
        assert count_vowels("xyz") == 0

    def test_all_vowels(self):
        assert count_vowels("aeiou") == 5

class TestTruncate:
    def test_short_string(self):
        assert truncate("hi", 10) == "hi"

    def test_long_string(self):
        assert truncate("hello world", 5) == "hello..."

    def test_exact_length(self):
        assert truncate("hello", 5) == "hello"
```

### Step 4: Configure pyproject.toml

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Step 5: Run Tests in Various Ways

```bash
# run all tests
pytest

# verbose output
pytest -v

# specific file
pytest tests/test_string_utils.py

# specific class
pytest tests/test_string_utils.py::TestReverseString

# specific test
pytest tests/test_string_utils.py::TestReverseString::test_basic

# filter by keyword
pytest -k "vowel"

# stop on first failure
pytest -x
```

## 이 코드에서 주목할 점

- `class Test*` 구조는 관련 테스트를 묶어 가독성을 높입니다.
- `pyproject.toml`의 `pythonpath`는 pytest가 `src` 디렉터리를 올바르게 찾게 해 줍니다.
- `-k` 옵션은 일부 이름만으로도 원하는 테스트를 빠르게 골라 실행하게 해 줍니다.
- 노드 ID를 쓰면 테스트 하나만 정확히 집어서 실행할 수 있습니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `src/`를 `pythonpath`에 추가하지 않음 | `ModuleNotFoundError`가 발생합니다 | `pyproject.toml`에 `pythonpath = ["src"]`를 추가합니다 |
| `__init__.py` 누락 | 패키지로 인식되지 않을 수 있습니다 | 패키지 디렉터리마다 `__init__.py`를 둡니다 |
| 테스트 클래스에 `__init__`을 정의함 | pytest가 테스트 클래스로 인식하지 않습니다 | 테스트 클래스에는 `__init__`을 두지 않습니다 |
| conftest.py를 import하려고 함 | pytest가 자동 로드하므로 불필요합니다 | fixture 이름만 직접 사용합니다 |
| 파일명에 하이픈을 씀 | Python import 경로로 쓰기 어렵습니다 | 언더스코어를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- `tests/`를 `src/`와 분리해 배포 패키지에 테스트 코드가 섞이지 않게 합니다.
- 데이터베이스 연결, HTTP 클라이언트 같은 공통 fixture는 `conftest.py`에 둡니다.
- CI에서는 `-x`로 첫 실패에서 빠르게 중단해 피드백 속도를 높이기도 합니다.
- `pyproject.toml` 또는 `pytest.ini`로 팀 공통 설정을 고정합니다.
- 특정 기능만 빠르게 검증할 때 `-k` 필터를 적극 활용합니다.

## 현업 개발자는 이렇게 생각합니다

테스트 구조는 초기에 잡아 둘수록 이득입니다. “나중에 정리하자”는 말은 대개 “계속 어수선한 상태로 남겨 두자”와 비슷하게 흘러갑니다.

특히 `src/` 레이아웃은 프로덕션 코드와 테스트 코드를 분리한다는 점에서 장기 유지보수에 유리합니다. 패키지 설치, import 경로, 배포 경계가 더 명확해지기 때문입니다.

## 체크리스트

- [ ] `src/` 레이아웃으로 프로젝트를 구성했다
- [ ] `pyproject.toml`에 `testpaths`와 `pythonpath`를 설정했다
- [ ] `pytest -v`로 전체 테스트를 실행했다
- [ ] 노드 ID로 특정 테스트를 실행했다
- [ ] `-k` 옵션으로 키워드 필터링을 사용했다

## 연습 문제

1. `capitalize_words(s)` 함수를 만들고, 빈 문자열·단어 하나·여러 단어 케이스를 테스트 클래스로 묶어 보세요.
2. `pyproject.toml` 없이 `pytest`를 실행해 본 뒤, 설정을 추가해 import 문제를 해결해 보세요.
3. `-k "reverse"`로 reverse 관련 테스트만 실행해 보세요.

## 정리 및 다음 글 안내

이제 pytest가 테스트를 어떻게 발견하는지, 그리고 왜 구조가 문법보다 먼저인지 감이 잡혔을 것입니다. 다음 글에서는 `assert`가 왜 pytest에서 특히 강력한지, 그리고 예외 테스트를 어떻게 읽기 좋게 작성하는지 살펴보겠습니다.

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

## 실전 구조 설계: 작은 프로젝트를 테스트 가능한 형태로 시작하기

다음 구조는 입문 단계에서 가장 실수가 적은 형태입니다.

```text
myapp/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── parser.py
│       └── service.py
└── tests/
    ├── conftest.py
    ├── test_parser.py
    └── test_service.py
```

`parser.py`와 `service.py`를 분리하면, 순수 로직과 외부 의존 경계를 분리해 테스트하기 쉽습니다.

```python
# src/myapp/parser.py

def parse_limit(value: str) -> int:
    num = int(value)
    if num <= 0:
        raise ValueError("limit must be positive")
    return num
```

```python
# src/myapp/service.py
from myapp.parser import parse_limit


def build_query(limit: str) -> str:
    n = parse_limit(limit)
    return f"SELECT * FROM users LIMIT {n}"
```

```python
# tests/test_service.py
import pytest
from myapp.service import build_query


def test_build_query():
    assert build_query("10") == "SELECT * FROM users LIMIT 10"


def test_build_query_rejects_non_positive():
    with pytest.raises(ValueError, match="positive"):
        build_query("0")
```

## pytest 실행 패턴과 출력 읽기

```bash
pytest -q
```

```text
..                                                                   [100%]
2 passed in 0.03s
```

```bash
pytest -v tests/test_service.py::test_build_query
```

```text
tests/test_service.py::test_build_query PASSED
========================= 1 passed =========================
```

실패 출력도 익숙해져야 합니다.

```python
def test_build_query():
    assert build_query("10") == "SELECT * FROM users LIMIT 20"
```

```text
E       AssertionError: assert 'SELECT * FROM users LIMIT 10' == 'SELECT * FROM users LIMIT 20'
```

## discovery 관련 실수 재현과 수정

### 실수 1: 파일명 규칙 위반

`tests/service_testcase.py`처럼 작성하면 기본 규칙에서 누락될 수 있습니다.

해결: `test_service.py` 또는 `service_test.py`를 사용합니다.

### 실수 2: 클래스명 규칙 위반

```python
class ServiceTests:
    def test_build_query(self):
        ...
```

해결: `class TestService:` 형태를 사용합니다.

### 실수 3: 잘못된 import 경로

```python
from src.myapp.service import build_query
```

이 방식은 로컬에서는 우연히 통과해도 CI에서 실패하기 쉽습니다.

해결: `pythonpath = ["src"]`를 설정하고 `from myapp.service import ...`를 사용합니다.

## conftest.py를 이용한 공통 준비

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_limits():
    return ["1", "10", "100"]
```

```python
# tests/test_parser.py
from myapp.parser import parse_limit


def test_parse_limit_values(sample_limits):
    assert [parse_limit(x) for x in sample_limits] == [1, 10, 100]
```

이 구조를 초기에 잡으면 이후 fixture, parametrization, mock을 추가해도 디렉터리 규칙이 흔들리지 않습니다.


## 프로젝트 부팅 체크: 처음부터 흔들리지 않는 pytest 셋업

처음 셋업에서 흔들리면 이후 모든 글의 실습이 불안정해집니다. 아래 순서로 고정하면 실패 확률이 크게 줄어듭니다.

### pyproject.toml 예시

```toml
[project]
name = "myapp"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra -q"
```

### 최소 코드와 테스트

```python
# src/myapp/math_ops.py

def multiply(a: int, b: int) -> int:
    return a * b
```

```python
# tests/test_math_ops.py
from myapp.math_ops import multiply


def test_multiply_positive():
    assert multiply(3, 4) == 12


def test_multiply_zero():
    assert multiply(3, 0) == 0
```

### 실행 출력

```bash
pytest -v
```

```text
tests/test_math_ops.py::test_multiply_positive PASSED
tests/test_math_ops.py::test_multiply_zero PASSED
========================= 2 passed =========================
```

## discovery 디버깅 루틴

1. `pytest --collect-only -q`로 수집 노드를 확인합니다.
2. 기대한 파일/함수가 없으면 이름 규칙을 먼저 점검합니다.
3. 그다음 import 경로(`pythonpath`)를 확인합니다.

```bash
pytest --collect-only -q
```

```text
tests/test_math_ops.py::test_multiply_positive
tests/test_math_ops.py::test_multiply_zero
```

## Before/After: 구조 개편 예시

```text
# before
project/
├── app.py
├── util_test_final.py
└── something.py
```

```text
# after
project/
├── src/myapp/
│   ├── __init__.py
│   └── something.py
└── tests/
    └── test_something.py
```

이 변경은 테스트 발견 실패, import 오류, 실행 방법 불일치 문제를 동시에 줄입니다.

## 팀 규칙 템플릿

- 테스트 파일명: `test_*.py`
- 테스트 함수명: `test_*`
- 기능 수정 PR: 최소 1개 테스트 추가
- 버그 수정 PR: 재현 테스트 필수


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


## 처음 질문으로 돌아가기

- **pytest는 테스트 파일과 함수를 어떤 규칙으로 자동 탐색할까요?**
  - 본문의 기준은 첫 번째 pytest 테스트 작성하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **프로덕션 코드와 테스트 코드는 어떤 디렉터리 구조로 나누는 편이 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`pyproject.toml`은 왜 필요한가요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- **첫 번째 pytest 테스트 작성하기 (현재 글)**
- assert와 예외 테스트 (예정)
- fixture 이해하기 (예정)
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — Test Discovery](https://docs.pytest.org/en/stable/goodpractices.html#test-discovery)
- [pytest — Configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [src layout vs flat layout — Python Packaging Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Real Python — Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, 테스트 작성, test discovery, 프로젝트 구조
