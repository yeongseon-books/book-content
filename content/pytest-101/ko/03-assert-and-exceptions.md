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

## 적용 전후 비교
unittest 스타일과 pytest 스타일을 비교해 보겠습니다.

```python
# 기존: unittest 스타일 — 메서드 이름을 외워야 함
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertIn("hello", result)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)
        self.assertRaises(ValueError, divide, 1, 0)
```

```python
# 개선: pytest 스타일 — assert로 통일
import pytest

def test_add():
    assert add(1, 2) == 3
    assert "hello" in result
    assert 0.1 + 0.2 == pytest.approx(0.3)
    with pytest.raises(ValueError):
        divide(1, 0)
```

## 단계별 실습

### 단계 1: 기본 assert 패턴
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

### 단계 2: 컬렉션 비교
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

### 단계 3: 부동소수점 비교
```python
# test_float.py
import pytest

def test_float_naive():
    # 이 테스트는 실패합니다:
    # assert 0.1 + 0.2 == 0.3

    # pytest.approx를 사용한 안전한 비교
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_approx_with_tolerance():
    assert 2.0 == pytest.approx(2.02, abs=0.05)
    assert 100.0 == pytest.approx(101.0, rel=0.02)

def test_approx_list():
    result = [0.1 + 0.2, 0.2 + 0.3]
    assert result == pytest.approx([0.3, 0.5])
```

### 단계 4: 예외 테스트
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
    # TypeError가 아니라 ValueError가 발생하므로 이 테스트는 실패
    with pytest.raises(TypeError):
        divide(10, 0)
```

### 단계 5: 커스텀 에러 메시지
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

pytest의 `assert`는 읽기 쉽고, 실패했을 때도 유용합니다. `pytest.raises`와 `pytest.approx`까지 익히면 예외와 부동소수점처럼 자주 헷갈리는 영역도 안정적으로 검증할 수 있습니다. 다음 글에서는 테스트 데이터와 상태 준비를 반복 없이 관리하는 fixture를 봅니다.

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

## 적용 전과 후: assert 메시지 강화

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

## 적용 전과 후: try/except 제거

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
  - pytest는 `assert`를 내부적으로 재작성해 실제값과 기대값을 함께 보여 주므로, `assert calc_tax(10000, 0.1) == 1200`이 실패했을 때 `1000 == 1200`과 호출식까지 바로 드러납니다. 그래서 `print()`를 덧붙이지 않아도 어떤 계산이 어긋났는지 CI 로그만 보고 추적하기 쉬워집니다.
- **컬렉션, 문자열, 부동소수점은 어떤 방식으로 검증해야 할까요?**
  - dict와 set은 그대로 `assert`로 비교하면 다른 키와 원소 차이를 pytest가 자세히 보여 주고, 문자열도 `render_title(" Alice ") == "[USER] Alice"`처럼 결과를 직접 고정하는 편이 읽기 좋습니다. 부동소수점은 `0.1 + 0.2 == pytest.approx(0.3)`나 `pytest.approx([0.3, 0.5], rel=1e-5)`처럼 허용 오차를 명시해야 안정적인 테스트가 됩니다.
- **`pytest.raises`로 예외 타입과 메시지를 어떻게 확인할 수 있을까요?**
  - `with pytest.raises(ValueError, match="between 0 and 1"):`처럼 타입과 메시지를 함께 검증하면, 단순히 실패했는지가 아니라 올바른 이유로 실패했는지까지 고정할 수 있습니다. 더 자세한 확인이 필요하면 `exc_info.value`와 `exc_info.type`을 써서 `divide(10, 0)`나 `parse_qty("0")`가 기대한 예외 객체를 냈는지 직접 검사하면 됩니다.

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
