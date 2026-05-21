---
series: pytest-101
episode: 3
title: "pytest 101 (3/10): assert와 예외 테스트"
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
  - assert
  - 예외 테스트
  - pytest.raises
seo_description: pytest의 assert 재작성, 예외 검증, 부동소수점 비교 패턴을 정리합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (3/10): assert와 예외 테스트

이 글은 pytest 101 시리즈의 세 번째 글입니다. pytest의 `assert`는 Python 내장 `assert`와 겉모습은 비슷하지만, 실패했을 때 훨씬 많은 정보를 보여 주도록 내부적으로 재작성됩니다. 이 글에서는 assertion introspection, `pytest.raises`, `pytest.approx`를 중심으로 실패 원인을 빨리 읽는 테스트를 만드는 방법을 설명합니다.

테스트는 실패했을 때 가치가 드러납니다. 왜 실패했는지 바로 읽히지 않는 테스트는 디버깅 시간을 늘리고, 예외 처리 검증이 빠진 테스트는 실제 운영에서 에러 핸들링이 깨져도 놓치기 쉽습니다.


![pytest 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/03/03-01-big-picture.ko.png)
*pytest 101 3장 흐름 개요*

## 먼저 던지는 질문

- pytest의 `assert`는 왜 더 읽기 좋은 실패 메시지를 제공할까요?
- 컬렉션, 문자열, 부동소수점은 어떤 방식으로 검증해야 할까요?
- `pytest.raises`로 예외 타입과 메시지를 어떻게 확인할 수 있을까요?

## 왜 이 글이 중요한가

테스트가 실패했는데 원인을 한눈에 읽을 수 없다면, 테스트가 디버깅을 돕는 것이 아니라 오히려 방해하게 됩니다. pytest는 이 지점에서 강합니다. `assert result == expected`처럼 단순한 표현만 써도, 실패 시 양쪽 값을 자세히 보여 주기 때문입니다.

> unittest의 `self.assertEqual(a, b)`보다 `assert a == b`가 읽기 쉽고, pytest의 실패 메시지는 오히려 더 상세합니다.

또한 예외는 프로덕션 코드의 핵심 계약입니다. 잘못된 입력에서 반드시 실패해야 하는 함수가 조용히 통과해 버리면, 실제 장애는 테스트를 모두 통과한 뒤에야 드러납니다.

## 핵심 개념 잡기

> assertion introspection = pytest가 assert 문을 분석해 실패 원인을 자세히 보여 주는 기능

```text
assert result == expected
       │          │
       │          └─ Expected value: displayed
       └─ Actual value: displayed

On failure:
  AssertionError: assert 3 == 5
    where 3 = add(1, 2)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| assertion rewriting | pytest가 AST 수준에서 `assert`를 변환해 자세한 메시지를 만듭니다 |
| pytest.raises | 특정 예외가 발생하는지 검증하는 컨텍스트 매니저입니다 |
| pytest.approx | 부동소수점 비교에서 허용 오차를 다룹니다 |
| match 파라미터 | 예외 메시지를 정규식으로 검증합니다 |
| ExceptionInfo | `pytest.raises`가 반환하는 예외 정보 객체입니다 |

## Before / After

unittest 스타일과 pytest 스타일을 비교해 보겠습니다.

```python
# before: unittest style — must memorize method names
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertIn("hello", result)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)
        self.assertRaises(ValueError, divide, 1, 0)
```

```python
# after: pytest style — unified with assert
import pytest

def test_add():
    assert add(1, 2) == 3
    assert "hello" in result
    assert 0.1 + 0.2 == pytest.approx(0.3)
    with pytest.raises(ValueError):
        divide(1, 0)
```

## 단계별 실습

### Step 1: Basic Assert Patterns

```python
# test_assert_patterns.py

def test_equality():
    assert 1 + 1 == 2

def test_inequality():
    assert 1 + 1 != 3

def test_truthiness():
    assert [1, 2, 3]    # non-empty list is truthy
    assert not []        # empty list is falsy

def test_membership():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits
    assert "mango" not in fruits

def test_identity():
    a = None
    assert a is None
```

### Step 2: Collection Comparison

```python
# test_collections.py

def test_list_comparison():
    expected = [1, 2, 3, 4, 5]
    result = list(range(1, 6))
    assert result == expected

def test_dict_comparison():
    expected = {"name": "Alice", "age": 30}
    result = {"name": "Alice", "age": 25}
    assert result == expected  # shows differing key-values on failure

def test_set_comparison():
    expected = {1, 2, 3}
    result = {1, 2, 4}
    assert result == expected  # shows set difference on failure
```

### Step 3: Floating-Point Comparison

```python
# test_float.py
import pytest

def test_float_naive():
    # This test would fail:
    # assert 0.1 + 0.2 == 0.3

    # Safe comparison with pytest.approx
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_approx_with_tolerance():
    assert 2.0 == pytest.approx(2.02, abs=0.05)
    assert 100.0 == pytest.approx(101.0, rel=0.02)

def test_approx_list():
    result = [0.1 + 0.2, 0.2 + 0.3]
    assert result == pytest.approx([0.3, 0.5])
```

### Step 4: Exception Testing

```python
# test_exceptions.py
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError(f"Cannot divide {a} by zero")
    return a / b

def test_raises_basic():
    with pytest.raises(ValueError):
        divide(10, 0)

def test_raises_with_match():
    with pytest.raises(ValueError, match="by zero"):
        divide(10, 0)

def test_raises_inspect_exception():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "by zero" in str(exc_info.value)
    assert exc_info.type is ValueError

def test_raises_wrong_exception():
    # This test fails because ValueError is raised, not TypeError
    with pytest.raises(TypeError):
        divide(10, 0)
```

### Step 5: Custom Error Messages

```python
# test_custom_message.py

def test_with_message():
    value = compute_score()
    assert value >= 0, f"Score cannot be negative. Got: {value}"

def test_complex_assertion():
    users = fetch_active_users()
    assert len(users) > 0, "No active users found"
```

## 이 코드에서 주목할 점

- dict 비교가 실패하면 어떤 키와 값이 다른지 바로 보여 줍니다.
- `pytest.approx`는 리스트 같은 컬렉션에도 적용할 수 있습니다.
- `match`는 정규식을 지원하므로 예외 메시지를 유연하게 검증할 수 있습니다.
- `exc_info.value`를 통해 예외 객체 자체의 속성을 검사할 수 있습니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `assert 0.1 + 0.2 == 0.3` | 부동소수점 오차 때문에 실패합니다 | `pytest.approx(0.3)`를 사용합니다 |
| `pytest.raises` 블록 안에서 추가 assert를 함 | 예외 발생 뒤 코드는 실행되지 않습니다 | `exc_info` 검사는 블록 밖에서 합니다 |
| 너무 넓은 예외 타입을 사용함 | 다른 버그까지 숨길 수 있습니다 | 정확한 예외 타입을 명시합니다 |
| `match`의 특수문자를 고려하지 않음 | 정규식으로 해석돼 의도와 다를 수 있습니다 | 필요하면 `re.escape()`를 사용합니다 |
| 함수 호출만 하고 assert를 하지 않음 | 결과 계약은 검증하지 못합니다 | 반환값이나 상태를 반드시 assert 합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답의 상태 코드와 본문 내용을 함께 검증합니다.
- 금융 계산처럼 오차 허용이 필요한 로직에 `pytest.approx`를 사용합니다.
- 입력 검증 실패 경로를 `pytest.raises`로 빠짐없이 테스트합니다.
- 커스텀 예외 객체의 속성도 `exc_info.value`로 확인합니다.
- CI 로그에서 바로 원인을 읽을 수 있도록 실패 메시지에 맥락을 남깁니다.

## 현업 개발자는 이렇게 생각합니다

좋은 테스트는 실패 메시지만 보고도 원인을 짐작할 수 있어야 합니다. pytest의 `assert`는 이 목표에 매우 잘 맞습니다. 별도의 `print()` 디버깅 없이도 실제값과 기대값을 바로 보여 주기 때문입니다.

예외 테스트도 같은 관점으로 보면 됩니다. “이 함수는 이 입력에서 반드시 실패해야 한다”는 계약을 명시하는 일입니다. 예외가 사라지면 테스트가 바로 실패하므로, 에러 핸들링 회귀를 빨리 잡을 수 있습니다.

## 체크리스트

- [ ] pytest의 assertion introspection 출력을 확인했다
- [ ] `pytest.approx`로 부동소수점을 비교했다
- [ ] `pytest.raises`로 예외 타입을 검증했다
- [ ] `match` 파라미터로 예외 메시지를 검증했다
- [ ] `exc_info`로 예외 객체를 확인했다

## 연습 문제

1. 두 dict가 다르게 생긴 테스트를 직접 작성하고, pytest의 diff 출력을 확인해 보세요.
2. 음수 입력에서 `ValueError`를 발생시키는 `sqrt(n)` 함수를 만들고 메시지까지 검증해 보세요.
3. `pytest.approx`의 `rel`, `abs` 옵션 차이를 직접 비교해 보세요.

## 정리 및 다음 글 안내

pytest의 `assert`는 읽기 쉽고, 실패했을 때도 유용합니다. `pytest.raises`와 `pytest.approx`까지 익히면 예외와 부동소수점처럼 자주 헷갈리는 영역도 안정적으로 검증할 수 있습니다. 다음 글에서는 테스트 데이터와 상태 준비를 반복 없이 관리하는 fixture를 살펴보겠습니다.

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

## 실패 메시지를 자산으로 만드는 assert 작성법

`assert`는 통과할 때가 아니라 실패할 때 팀 생산성을 결정합니다. 실패 메시지를 읽고 바로 조치할 수 있게 작성하는 패턴이 중요합니다.

```python
# tax.py

def calc_tax(amount: int, rate: float) -> int:
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(amount * rate)
```

```python
# test_tax.py
import pytest
from tax import calc_tax

@pytest.mark.parametrize(
    "amount,rate,expected",
    [
        (10000, 0.1, 1000),
        (0, 0.2, 0),
        (5500, 0.08, 440),
    ],
)
def test_calc_tax(amount, rate, expected):
    assert calc_tax(amount, rate) == expected


def test_calc_tax_rejects_negative_amount():
    with pytest.raises(ValueError, match=r"amount must be >= 0"):
        calc_tax(-1, 0.1)


def test_calc_tax_rejects_bad_rate():
    with pytest.raises(ValueError, match="between 0 and 1"):
        calc_tax(1000, 1.5)
```

## pytest 출력으로 원인 읽기

```bash
pytest test_tax.py -v
```

```text
test_tax.py::test_calc_tax[10000-0.1-1000] PASSED
...
========================= 5 passed =========================
```

의도적으로 실패시키면 출력 차이를 확인할 수 있습니다.

```python
def test_calc_tax():
    assert calc_tax(10000, 0.1) == 1200
```

```text
E       assert 1000 == 1200
E        +  where 1000 = calc_tax(10000, 0.1)
```

## 예외 테스트에서 자주 놓치는 포인트

| 항목 | 나쁜 예 | 좋은 예 |
|---|---|---|
| 타입 검증 | `with pytest.raises(Exception)` | `with pytest.raises(ValueError)` |
| 메시지 검증 | 예외 타입만 검증 | `match="between 0 and 1"` |
| 범위 | 블록이 너무 큼 | 예외 발생 줄만 블록에 배치 |

```python
# 나쁜 예: 블록이 너무 커서 다른 오류도 섞임
with pytest.raises(ValueError):
    x = calc_tax(1000, 0.1)
    y = x / 0
```

```python
# 좋은 예
with pytest.raises(ValueError, match="between 0 and 1"):
    calc_tax(1000, 1.5)
```

## 부동소수점 비교의 실전 패턴

```python
import pytest


def test_discount_ratio():
    ratio = 1 - (90 / 100)
    assert ratio == pytest.approx(0.1)


def test_vector_ratios():
    values = [1 / 3, 2 / 3]
    assert values == pytest.approx([0.333333, 0.666667], rel=1e-5)
```

## Before/After: assert 메시지 강화

```python
# before
assert total > 0
```

```python
# after
assert total > 0, f"total must be positive, got={total}, items={items}"
```

후자의 실패 메시지는 재현 시간을 줄여 줍니다.


## assert 표현력을 높이는 패턴 모음

### 문자열 비교

```python

def render_title(name: str) -> str:
    return f"[USER] {name.strip()}"


def test_render_title():
    assert render_title(" Alice ") == "[USER] Alice"
```

### 컬렉션 비교

```python

def ids(users):
    return [u["id"] for u in users]


def test_ids():
    data = [{"id": 1}, {"id": 2}]
    assert ids(data) == [1, 2]
```

### 예외와 메시지 검증

```python
import pytest


def parse_qty(value: str) -> int:
    qty = int(value)
    if qty <= 0:
        raise ValueError("qty must be positive")
    return qty


def test_parse_qty_error_message():
    with pytest.raises(ValueError, match="positive"):
        parse_qty("0")
```

## red/green 출력 예시

```bash
pytest -v test_parse_qty.py
```

```text
test_parse_qty.py::test_parse_qty_error_message PASSED
```

메시지를 잘못 기대하면 즉시 실패합니다.

```text
E   AssertionError: Regex pattern did not match.
```

## Before/After: try/except 제거

```python
# before
try:
    parse_qty("0")
    assert False
except ValueError:
    pass
```

```python
# after
with pytest.raises(ValueError, match="positive"):
    parse_qty("0")
```

## 실무 체크 항목

- 에러 타입을 구체적으로 검증했는가
- 메시지까지 검증해 의도를 고정했는가
- 부동소수점 비교에 `pytest.approx`를 썼는가
- assert 실패 메시지로 재현에 필요한 입력이 남는가


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

- **pytest의 `assert`는 왜 더 읽기 좋은 실패 메시지를 제공할까요?**
  - 본문의 기준은 assert와 예외 테스트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **컬렉션, 문자열, 부동소수점은 어떤 방식으로 검증해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`pytest.raises`로 예외 타입과 메시지를 어떻게 확인할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- **assert와 예외 테스트 (현재 글)**
- fixture 이해하기 (예정)
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — Assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- [pytest — pytest.raises](https://docs.pytest.org/en/stable/reference/reference.html#pytest-raises)
- [pytest — pytest.approx](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)
- [Real Python — Testing Exceptions](https://realpython.com/pytest-python-testing/#testing-for-exceptions)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, assert, 예외 테스트, pytest.raises
