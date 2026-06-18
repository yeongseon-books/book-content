---
title: "바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트"
series: pytest-101
episode: 3
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - assert
  - 예외 테스트
  - pytest.raises
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 세 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 생성한 코드가 실패할 때 원인을 바로 읽을 수 없다면, 테스트가 디버깅을 돕는 것이 아니라 오히려 방해합니다. pytest의 `assert`는 실패했을 때 양쪽 값을 자세히 보여 주고, `pytest.raises`는 예외 경로를 명확하게 검증합니다. AI 코드에서 예외 처리가 제대로 구현됐는지 확인하는 가장 효율적인 도구입니다.

테스트는 실패했을 때 가치가 드러납니다. 왜 실패했는지 바로 읽히지 않는 테스트는 디버깅 시간을 늘리고, 예외 처리 검증이 빠진 테스트는 실제 운영에서 에러 핸들링이 깨져도 놓치기 쉽습니다.

> "AI가 생성한 에러 처리 코드는 특히 주의해야 합니다. 정상 케이스는 잘 처리해도 예외 경로가 빠지는 경우가 많습니다."

---

## 이 글에서 다룰 문제

- pytest의 `assert`는 왜 더 읽기 좋은 실패 메시지를 제공할까요?
- 컬렉션, 문자열, 부동소수점은 어떤 방식으로 검증해야 할까요?
- `pytest.raises`로 예외 타입과 메시지를 어떻게 확인할 수 있을까요?
- AI가 생성한 예외 처리 코드를 어떻게 체계적으로 검증할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

pytest의 `assert`는 Python 내장 `assert`와 겉모습은 비슷하지만, 실패했을 때 훨씬 많은 정보를 보여 주도록 내부적으로 재작성됩니다. AI가 생성한 코드에서 버그를 찾으려면 실패 메시지가 풍부해야 합니다.

또한 예외는 프로덕션 코드의 핵심 계약입니다. AI는 주로 정상 경로 코드를 잘 생성하지만, "잘못된 입력에서 반드시 실패해야 하는" 예외 경로를 빠뜨리거나 너무 광범위한 `except Exception`으로 처리하는 경우가 많습니다. `pytest.raises`는 이런 빈틈을 잡아냅니다.

---

## 핵심 개념 잡기

> assertion introspection = pytest가 assert 문을 분석해 실패 원인을 자세히 보여 주는 기능

```text
assert result == expected
       │          │
       │          └─ 기대값: 출력됨
       └─ 실제값: 출력됨

실패 시:
  AssertionError: assert 3 == 5
    where 3 = add(1, 2)
```

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| assertion rewriting | pytest가 AST 수준에서 `assert`를 변환해 자세한 메시지를 만듭니다 |
| pytest.raises | 특정 예외가 발생하는지 검증하는 컨텍스트 매니저입니다 |
| pytest.approx | 부동소수점 비교에서 허용 오차를 다룹니다 |
| match 파라미터 | 예외 메시지를 정규식으로 검증합니다 |
| ExceptionInfo | `pytest.raises`가 반환하는 예외 정보 객체입니다 |

---

## Before / After: unittest 스타일 vs pytest 스타일

AI가 테스트를 생성할 때 unittest 스타일로 작성하는 경우가 있습니다.

**Before: unittest 스타일**

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)
        self.assertRaises(ValueError, divide, 1, 0)
```

**After: pytest 스타일 (AI에게 이 형식으로 재작성 요청)**

```python
import pytest

def test_add():
    assert add(1, 2) == 3
    assert 0.1 + 0.2 == pytest.approx(0.3)
    with pytest.raises(ValueError):
        divide(1, 0)
```

pytest 스타일이 읽기 쉽고, 실패 메시지도 더 상세합니다.

---

## 실습: assert 패턴

**기본 assert**

```python
def test_equality():
    assert 1 + 1 == 2

def test_membership():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits
    assert "mango" not in fruits

def test_identity():
    a = None
    assert a is None
```

**컬렉션 비교**

```python
def test_dict_comparison():
    expected = {"name": "Alice", "age": 30}
    result = {"name": "Alice", "age": 25}
    assert result == expected  # 실패 시 어떤 키가 다른지 보여 줌
```

**부동소수점 비교**

```python
import pytest

def test_float_comparison():
    # AI 생성 코드에서 자주 발생하는 실수
    # assert 0.1 + 0.2 == 0.3  # 실패!

    # pytest.approx를 사용한 올바른 비교
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_approx_with_tolerance():
    assert 2.0 == pytest.approx(2.02, abs=0.05)
```

**예외 테스트**

```python
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
```

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `assert 0.1 + 0.2 == 0.3` | 부동소수점 오차 때문에 실패합니다 | `pytest.approx(0.3)`를 사용합니다 |
| `pytest.raises` 블록 안에서 추가 assert를 함 | 예외 발생 뒤 코드는 실행되지 않습니다 | `exc_info` 검사는 블록 밖에서 합니다 |
| 너무 넓은 예외 타입 사용 (`Exception`) | 다른 버그까지 숨길 수 있습니다 | 정확한 예외 타입을 명시합니다 |
| AI 생성 코드에서 예외 경로 미검증 | 운영에서 에러 핸들링이 깨져도 테스트 통과합니다 | 각 `raise` 구문마다 테스트를 추가합니다 |
| 함수 호출만 하고 assert를 하지 않음 | 결과 계약을 검증하지 못합니다 | 반환값이나 상태를 반드시 assert 합니다 |

---

## AI 코딩 팁

AI가 생성한 코드에서 예외 처리를 검증하는 프롬프트 예시입니다.

```text
"아래 함수에서 발생할 수 있는 모든 예외 경로를 pytest.raises로 테스트해 주세요.
예외 타입뿐만 아니라 에러 메시지도 match 파라미터로 검증해 주세요.

def parse_age(value: str) -> int:
    age = int(value)
    if age < 0 or age > 150:
        raise ValueError(f'Invalid age: {age}')
    return age"
```

AI가 생성한 테스트를 평가할 때 이 점을 확인하세요.

- 정상 케이스뿐 아니라 `ValueError`, `TypeError` 같은 예외 케이스가 있는가?
- `pytest.raises`에서 예외 타입이 `Exception`처럼 너무 광범위하지 않은가?
- `match` 파라미터로 에러 메시지까지 검증하는가?

---

## 실제 예시: AI 생성 세금 계산 함수 검증

```python
# AI가 생성한 세금 계산 함수
def calc_tax(amount: int, rate: float) -> int:
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(amount * rate)
```

```python
# 검증 테스트
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

```bash
pytest test_tax.py -v
```

```text
test_tax.py::test_calc_tax[10000-0.1-1000] PASSED
test_tax.py::test_calc_tax[0-0.2-0] PASSED
test_tax.py::test_calc_tax[5500-0.08-440] PASSED
test_tax.py::test_calc_tax_rejects_negative_amount PASSED
test_tax.py::test_calc_tax_rejects_bad_rate PASSED
========================= 5 passed =========================
```

---

## 체크리스트

- [ ] pytest의 assertion introspection 출력을 확인했다
- [ ] `pytest.approx`로 부동소수점을 비교했다
- [ ] `pytest.raises`로 예외 타입을 검증했다
- [ ] `match` 파라미터로 예외 메시지를 검증했다
- [ ] AI 생성 코드의 모든 예외 경로를 테스트했다
- [ ] `exc_info`로 예외 객체 속성을 확인했다

---

## 처음 질문으로 돌아가기

- **pytest의 `assert`는 왜 더 읽기 좋은 실패 메시지를 제공할까요?**
  - pytest는 AST 수준에서 `assert` 문을 재작성해 실패 시 실제값과 기대값을 함께 보여 줍니다. AI 코드를 디버깅할 때 이 정보가 핵심입니다.
- **컬렉션, 문자열, 부동소수점은 어떻게 검증해야 할까요?**
  - dict 비교는 실패한 키까지 보여 줍니다. 부동소수점은 반드시 `pytest.approx`를 사용합니다. AI 코드에서 금액 계산이 있다면 특히 주의합니다.
- **`pytest.raises`로 예외 타입과 메시지를 어떻게 확인할 수 있을까요?**
  - `pytest.raises(ValueError, match="...")` 패턴으로 타입과 메시지를 동시에 검증합니다. AI 생성 에러 메시지가 실제로 올바른지 이 방법으로 확인합니다.

---

## 정리

pytest의 `assert`는 읽기 쉽고, 실패했을 때도 유용합니다. `pytest.raises`와 `pytest.approx`까지 익히면 AI가 생성한 예외 처리와 수치 계산 코드도 안정적으로 검증할 수 있습니다. 다음 글에서는 테스트 데이터와 상태 준비를 반복 없이 관리하는 fixture를 봅니다.

---

## 참고 자료

- [pytest — Assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- [pytest — pytest.raises](https://docs.pytest.org/en/stable/reference/reference.html#pytest-raises)
- [pytest — pytest.approx](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)
- [Real Python — Testing Exceptions](https://realpython.com/pytest-python-testing/#testing-for-exceptions)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?
- 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기
- **바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트 (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기
- 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기
- 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, assert, 예외 테스트, pytest.raises, 바이브코딩
