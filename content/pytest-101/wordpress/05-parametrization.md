---
title: "바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기"
series: pytest-101
episode: 5
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - parametrize
  - 테스트 케이스
  - 데이터 주도 테스트
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 다섯 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 코드를 생성하면 경계값, 특수 케이스, 오류 경로를 빠짐없이 검증해야 합니다. 같은 검증 로직을 여러 입력값으로 반복 실행해야 할 때, 테스트 함수를 복사해 늘리는 대신 `@pytest.mark.parametrize`로 데이터만 추가하는 방식이 훨씬 효율적입니다. AI에게 "parametrize로 경계값 케이스를 추가해 달라"고 요청하면 빠르게 범위를 넓힐 수 있습니다.

테스트 코드가 늘어나는 가장 흔한 이유는 검증 로직이 아니라 입력 데이터가 많아졌기 때문입니다. 이때 함수를 계속 복사하면 테스트는 금방 장황해지고, 케이스 하나를 추가할 때마다 중복도 함께 늘어납니다.

> "AI에게 'parametrize로 경계값, 빈값, 오류값을 포함한 테스트 케이스를 만들어 달라'고 요청하면 한 번에 폭넓은 검증을 얻을 수 있습니다."

---

## 이 글에서 다룰 문제

- 같은 로직을 여러 입력으로 검증할 때 함수를 복사하지 않으려면 어떻게 해야 할까요?
- `@pytest.mark.parametrize`의 기본 문법은 어떻게 읽어야 할까요?
- 각 테스트 케이스에 읽기 좋은 이름을 붙이려면 어떻게 해야 할까요?
- AI가 생성한 케이스에서 빠진 경계값을 어떻게 보완할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

AI가 생성한 코드는 "일반적인 케이스"에서는 잘 동작하지만, 경계값(0, -1, 빈 문자열, None)이나 특수 문자에서 예상치 못한 동작을 보이는 경우가 많습니다. parametrize를 이용하면 이런 케이스를 체계적으로 추가할 수 있습니다.

경계값, 빈 문자열, 특수문자처럼 꼭 검증해야 하는 케이스는 많습니다. parametrization이 없으면 이런 케이스를 빠짐없이 추가하기가 점점 번거로워집니다.

---

## 핵심 개념 잡기

> parametrize = 하나의 테스트 함수 + 여러 데이터 세트 → N개의 독립 테스트

```text
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),      ← 테스트 1
    ("", 0),            ← 테스트 2
    ("hi", 2),          ← 테스트 3
])
def test_length(input, expected):
    assert len(input) == expected
```

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| parametrize | 테스트 파라미터를 주입하는 데코레이터입니다 |
| 테스트 ID | 각 파라미터 조합에 붙는 식별자입니다 |
| pytest.param | 개별 케이스에 ID나 마크를 부여합니다 |
| indirect | parametrize 값을 fixture로 전달합니다 |
| 데카르트 곱 | 여러 parametrize 데코레이터를 쌓으면 조합 수가 곱해집니다 |

---

## Before / After: 복사-붙여넣기 vs parametrize

**Before: AI가 함수를 복사해 생성한 패턴**

```python
def test_is_palindrome_radar():
    assert is_palindrome("radar") is True

def test_is_palindrome_hello():
    assert is_palindrome("hello") is False

def test_is_palindrome_empty():
    assert is_palindrome("") is True

def test_is_palindrome_single():
    assert is_palindrome("a") is True
```

**After: parametrize 방식으로 리팩터링**

```python
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

AI에게 "이 반복 테스트들을 parametrize로 통합해 달라"고 요청하면 더 간결한 구조를 얻을 수 있습니다.

---

## 실습: parametrize 단계별 구현

**단계 1: 기본 parametrize**

```python
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

**단계 2: 예외 케이스 parametrize**

```python
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

**단계 3: 커스텀 ID로 가독성 향상**

```python
@pytest.mark.parametrize("email,valid", [
    pytest.param("user@example.com", True, id="normal-email"),
    pytest.param("@example.com", False, id="missing-local"),
    pytest.param("user@", False, id="missing-domain"),
    pytest.param("", False, id="empty-string"),
])
def test_validate_email(email, valid):
    result = "@" in email and len(email.split("@")) == 2
    has_domain = result and len(email.split("@")[1]) > 0
    has_local = result and len(email.split("@")[0]) > 0
    assert (has_domain and has_local) == valid
```

**단계 4: 조합 테스트 (중첩 parametrize)**

```python
@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
@pytest.mark.parametrize("status", [200, 404, 500])
def test_http_response(method, status):
    """3 메서드 x 3 상태코드 = 9개 테스트 자동 생성"""
    response = {"method": method, "status": status}
    assert response["method"] in ["GET", "POST", "PUT", "DELETE"]
    assert isinstance(response["status"], int)
```

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 파라미터 이름 문자열에 공백을 넣음 | 파싱 오류가 날 수 있습니다 | `"a,b"`처럼 쓰거나 리스트를 사용합니다 |
| 튜플 길이가 제각각임 | 파라미터 개수와 맞지 않아 실패합니다 | 모든 케이스의 요소 수를 맞춥니다 |
| AI가 경계값을 빠뜨림 | 정상 케이스만 검증하고 오류 케이스 누락됩니다 | 0, -1, 빈값, 최댓값+1 케이스를 직접 추가합니다 |
| ID 없이 복잡한 데이터를 씀 | 실패 출력이 읽기 어려워집니다 | 의미 있는 `id`를 붙입니다 |
| 조합 폭발로 테스트 시간이 느려짐 | 중첩 parametrize가 무한정 늘어납니다 | 핵심 경계만 추려 조합을 제한합니다 |

---

## AI 코딩 팁

AI에게 경계값 케이스를 포함한 parametrize 테스트를 요청하는 효과적인 프롬프트입니다.

```text
"아래 함수에 대해 pytest.mark.parametrize를 사용해 테스트를 작성해 주세요.
- 정상 케이스 3개 이상
- 경계값 (최솟값, 최댓값, 경계 바로 위/아래)
- 오류 케이스 (잘못된 입력, None, 빈 문자열)
- 각 케이스에 의미 있는 id를 붙여 주세요"
```

AI가 생성한 테스트를 평가할 때 이 점을 확인하세요.

- 경계값(0, -1, 빈 문자열, 최대 허용값)이 포함됐는가?
- 정상 케이스와 오류 케이스가 분리됐는가?
- 각 케이스에 id가 붙어 실패 시 원인을 바로 알 수 있는가?

실패 출력에서 ID가 있으면 원인 파악이 훨씬 빠릅니다.

```text
FAILED test_username_invalid[space] - assert True is False
```

---

## 실제 예시: AI 생성 할인 함수 검증

```python
# AI가 생성한 할인 계산 함수
def discount_price(price: int, rate: float) -> int:
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(price * (1 - rate))
```

```python
import pytest
from discount import discount_price

@pytest.mark.parametrize(
    "price,rate,expected",
    [
        pytest.param(10000, 0.0, 10000, id="no-discount"),
        pytest.param(10000, 0.1, 9000, id="10-percent-off"),
        pytest.param(10000, 1.0, 0, id="full-discount"),
    ],
)
def test_discount_price(price, rate, expected):
    assert discount_price(price, rate) == expected

@pytest.mark.parametrize("price,rate", [
    pytest.param(-1, 0.1, id="negative-price"),
    pytest.param(1000, -0.1, id="negative-rate"),
    pytest.param(1000, 1.1, id="rate-over-100"),
])
def test_discount_price_invalid(price, rate):
    with pytest.raises(ValueError):
        discount_price(price, rate)
```

```text
test_discount.py::test_discount_price[no-discount] PASSED
test_discount.py::test_discount_price[10-percent-off] PASSED
test_discount.py::test_discount_price[full-discount] PASSED
test_discount.py::test_discount_price_invalid[negative-price] PASSED
test_discount.py::test_discount_price_invalid[negative-rate] PASSED
test_discount.py::test_discount_price_invalid[rate-over-100] PASSED
========================= 6 passed =========================
```

---

## 체크리스트

- [ ] `@pytest.mark.parametrize`로 테스트를 작성했다
- [ ] 정상 케이스와 예외 케이스를 분리했다
- [ ] `pytest.param`으로 테스트 ID를 붙였다
- [ ] 경계값(최솟값, 최댓값, 빈값)을 포함했다
- [ ] AI가 빠뜨린 케이스를 직접 추가했다
- [ ] `-v` 출력에서 개별 테스트 케이스를 확인했다

---

## 처음 질문으로 돌아가기

- **같은 로직을 여러 입력으로 검증할 때 함수를 복사하지 않으려면?**
  - `@pytest.mark.parametrize`를 사용하면 하나의 테스트 함수로 N개의 독립 테스트를 실행합니다. AI에게 반복 테스트를 parametrize로 통합해 달라고 요청하세요.
- **각 테스트 케이스에 읽기 좋은 이름을 붙이려면?**
  - `pytest.param(..., id="name")`을 사용합니다. AI에게 케이스마다 의미 있는 id를 붙이도록 요청하면 실패 시 원인 파악이 빨라집니다.
- **AI가 경계값을 빠뜨렸을 때 어떻게 보완할 수 있을까요?**
  - 0, -1, 빈 문자열, 최댓값+1 같은 경계값을 직접 추가합니다. 또는 AI에게 "경계값 케이스를 추가해 달라"고 다시 요청합니다.

---

## 정리

parametrize는 데이터 주도 테스트의 핵심입니다. AI가 생성한 코드를 검증할 때 정상 케이스뿐 아니라 경계값과 오류 케이스까지 체계적으로 추가하면 코드 신뢰도가 크게 올라갑니다. 다음 글에서는 외부 API, DB, 환경처럼 테스트 바깥 의존성을 다루기 위한 mock과 monkeypatch를 봅니다.

---

## 참고 자료

- [pytest — Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — pytest.param](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param)
- [Real Python — Parametrize Tests](https://realpython.com/pytest-python-testing/#parametrize)
- [Effective Python Testing with pytest](https://testdriven.io/blog/testing-python/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?
- 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기
- 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기
- **바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기 (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, parametrize, 테스트 케이스, 데이터 주도 테스트, 바이브코딩
