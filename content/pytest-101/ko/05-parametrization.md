---
series: pytest-101
episode: 5
title: parametrization으로 테스트 케이스 늘리기
status: publish-ready
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
  - parametrize
  - 테스트 케이스
  - 데이터 주도 테스트
seo_description: pytest parametrize로 같은 검증 로직에 여러 입력을 연결하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# parametrization으로 테스트 케이스 늘리기

이 글은 pytest 101 시리즈의 다섯 번째 글입니다. 같은 로직을 여러 입력값으로 반복 검증해야 할 때, 테스트 함수를 복사해 늘리는 대신 `@pytest.mark.parametrize`로 데이터만 추가하는 방식이 훨씬 낫습니다. 이 글에서는 기본 문법, 다중 파라미터, 테스트 ID, 중첩 parametrize 패턴을 정리합니다.

테스트 코드가 늘어나는 가장 흔한 이유는 검증 로직이 아니라 입력 데이터가 많아졌기 때문입니다. 이때 함수를 계속 복사하면 테스트는 금방 장황해지고, 케이스 하나를 추가할 때마다 중복도 함께 늘어납니다.

---

## 이 글에서 다룰 문제

- 같은 로직을 여러 입력으로 검증할 때 함수를 복사하지 않으려면 어떻게 해야 할까요?
- `@pytest.mark.parametrize`의 기본 문법은 어떻게 읽어야 할까요?
- 각 테스트 케이스에 읽기 좋은 이름을 붙이려면 어떻게 해야 할까요?
- 여러 parametrize를 겹치면 어떤 테스트가 만들어질까요?

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

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
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

Tags: Python, pytest, parametrize, 테스트 케이스, 데이터 주도 테스트
