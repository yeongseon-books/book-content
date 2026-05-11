---
series: pytest-101
episode: 3
title: assert와 예외 테스트
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
  - pytest
  - assert
  - 예외 테스트
  - pytest.raises
seo_description: pytest assert 재작성과 예외 테스트 패턴을 실습합니다.
last_reviewed: '2026-05-11'
---

# assert와 예외 테스트

> pytest 101 시리즈 (3/10)


## 이 글에서 다룰 문제

테스트가 실패했을 때 "왜 실패했는지"를 빠르게 파악하는 것이 중요합니다. pytest의 assertion introspection은 실패 원인을 즉시 보여주어 디버깅 시간을 크게 줄여줍니다.

> unittest의 `self.assertEqual(a, b)`보다 `assert a == b`가 읽기 쉽고, 실패 메시지는 오히려 더 상세합니다.

예외 처리는 프로덕션 코드의 핵심입니다. 예외가 올바르게 발생하는지 검증하지 않으면, 에러 핸들링이 깨져도 발견하지 못합니다.

## 핵심 개념 잡기

> assertion introspection = pytest가 assert 문을 분석하여 실패 시 상세 정보를 제공하는 기능

```text
assert result == expected
       │          │
       │          └─ 기대값: 표시됨
       └─ 실제값: 표시됨

실패 시 출력:
  AssertionError: assert 3 == 5
    where 3 = add(1, 2)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| assertion rewriting | pytest가 AST 수준에서 assert를 변환하여 상세 메시지를 생성합니다 |
| pytest.raises | 특정 예외가 발생하는지 검증하는 컨텍스트 매니저입니다 |
| pytest.approx | 부동소수점 비교 시 오차 범위를 허용합니다 |
| match 파라미터 | 예외 메시지를 정규식으로 검증합니다 |
| ExceptionInfo | pytest.raises가 반환하는 예외 정보 객체입니다 |

## Before / After

unittest 스타일과 pytest 스타일의 assert를 비교합니다.

```python
# 이전 방식: unittest 스타일 — 메서드 이름을 외워야 합니다
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertIn("hello", result)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)
        self.assertRaises(ValueError, divide, 1, 0)
```

```python
# 개선 방식: pytest 스타일 — assert 하나로 통일합니다
import pytest

def test_add():
    assert add(1, 2) == 3
    assert "hello" in result
    assert 0.1 + 0.2 == pytest.approx(0.3)
    with pytest.raises(ValueError):
        divide(1, 0)
```

## 단계별 실습

### Step 1: 기본 assert 패턴

```python
# test_assert_patterns.py 파일

def test_equality():
    assert 1 + 1 == 2

def test_inequality():
    assert 1 + 1 != 3

def test_truthiness():
    assert [1, 2, 3]    # 비어 있지 않은 리스트는 True
    assert not []        # 빈 리스트는 False

def test_membership():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits
    assert "mango" not in fruits

def test_identity():
    a = None
    assert a is None
```

### Step 2: 컬렉션 비교

```python
# test_collections.py 파일

def test_list_comparison():
    expected = [1, 2, 3, 4, 5]
    result = list(range(1, 6))
    assert result == expected

def test_dict_comparison():
    expected = {"name": "Alice", "age": 30}
    result = {"name": "Alice", "age": 25}
    assert result == expected  # 실패 시 다른 키-값 표시

def test_set_comparison():
    expected = {1, 2, 3}
    result = {1, 2, 4}
    assert result == expected  # 실패 시 차집합 표시
```

### Step 3: 부동소수점 비교

```python
# test_float.py 파일
import pytest

def test_float_naive():
    # 이 테스트는 실패합니다
    # assert 0.1 + 0.2 == 0.3

    # pytest.approx로 안전하게 비교
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_approx_with_tolerance():
    assert 2.0 == pytest.approx(2.02, abs=0.05)
    assert 100.0 == pytest.approx(101.0, rel=0.02)

def test_approx_list():
    result = [0.1 + 0.2, 0.2 + 0.3]
    assert result == pytest.approx([0.3, 0.5])
```

### Step 4: 예외 테스트

```python
# test_exceptions.py 파일
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError(f"{a}을(를) 0으로 나눌 수 없습니다")
    return a / b

def test_raises_basic():
    with pytest.raises(ValueError):
        divide(10, 0)

def test_raises_with_match():
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(10, 0)

def test_raises_inspect_exception():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "0으로 나눌 수 없습니다" in str(exc_info.value)
    assert exc_info.type is ValueError

def test_raises_wrong_exception():
    # TypeError가 아니라 ValueError가 발생하므로 이 테스트는 실패합니다
    with pytest.raises(TypeError):
        divide(10, 0)
```

### Step 5: 커스텀 에러 메시지

```python
# test_custom_message.py 파일

def test_with_message():
    value = compute_score()
    assert value >= 0, f"점수는 음수일 수 없습니다. 실제값: {value}"

def test_complex_assertion():
    users = fetch_active_users()
    assert len(users) > 0, "활성 사용자가 한 명도 없습니다"
```

## 이 코드에서 주목할 점

- dict 비교 실패 시 다른 키와 값을 정확히 보여줍니다
- `pytest.approx`는 리스트, dict 값에도 적용됩니다
- `match` 파라미터는 정규식을 지원하여 유연한 메시지 검증이 가능합니다
- `exc_info.value`로 예외 객체에 직접 접근하여 속성을 검증합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `assert 0.1 + 0.2 == 0.3` | 부동소수점 오차로 항상 실패합니다 | `pytest.approx(0.3)`를 사용합니다 |
| `pytest.raises` 블록 안에서 assert | 예외 발생 후 코드가 실행되지 않습니다 | `exc_info`를 블록 밖에서 검사합니다 |
| 너무 넓은 예외 타입으로 검증 | `Exception`으로 검증하면 다른 버그를 숨깁니다 | 정확한 예외 타입을 명시합니다 |
| `match`에 특수문자 이스케이프 누락 | 정규식으로 해석되어 의도와 다른 매칭이 됩니다 | `re.escape()`를 사용합니다 |
| assert 없이 함수만 호출 | 에러가 발생하지 않는 것만 확인됩니다 | 반환값도 반드시 assert로 검증합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답의 상태 코드와 본문을 assert로 동시에 검증합니다
- 금융 계산 로직에서 `pytest.approx`로 소수점 오차를 허용합니다
- 입력 유효성 검사 코드에 대해 `pytest.raises`로 에러 케이스를 빠짐없이 테스트합니다
- 커스텀 예외 클래스의 속성(error_code, detail)을 `exc_info.value`로 검증합니다
- 실패 메시지에 컨텍스트를 추가하여 CI 로그에서 원인을 빠르게 파악합니다

## 현업 개발자는 이렇게 생각합니다

좋은 테스트는 실패 메시지만 보고도 원인을 파악할 수 있어야 합니다. `assert result == expected`가 실패하면, pytest가 양쪽 값을 보여주기 때문에 별도의 print 디버깅이 필요 없습니다.

예외 테스트를 작성할 때는 "이 함수가 이 입력에서 반드시 실패해야 한다"는 관점으로 접근합니다. 예외가 발생하지 않으면 테스트가 실패하므로, 에러 핸들링이 실수로 제거되는 것을 방지합니다.

## 체크리스트

- [ ] pytest의 assertion introspection 출력을 확인했다
- [ ] `pytest.approx`로 부동소수점을 비교했다
- [ ] `pytest.raises`로 예외 타입을 검증했다
- [ ] `match` 파라미터로 예외 메시지를 검증했다
- [ ] `exc_info`로 예외 객체의 속성을 검사했다

## 정리 및 다음 글 안내

pytest의 assert는 읽기 쉽고, 실패 시 상세한 정보를 제공합니다. `pytest.raises`와 `pytest.approx`는 예외와 부동소수점 테스트의 필수 도구입니다. 다음 글에서는 테스트 데이터를 관리하는 fixture를 배웁니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
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

Tags: Python, pytest, assert, 예외 테스트, pytest.raises
