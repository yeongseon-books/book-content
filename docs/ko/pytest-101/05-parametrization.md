---
series: pytest-101
episode: 5
title: parametrization으로 테스트 케이스 늘리기
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
  - parametrize
  - 테스트 케이스
  - 데이터 주도 테스트
seo_description: pytest parametrize로 데이터 주도 테스트를 작성하는 방법을 실습합니다.
last_reviewed: '2026-05-04'
---

# parametrization으로 테스트 케이스 늘리기

> pytest 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 로직을 다른 입력으로 반복 테스트할 때 함수를 복사해야 하나요?

> `@pytest.mark.parametrize`를 사용하면 하나의 테스트 함수로 여러 입력-출력 조합을 검증할 수 있습니다. 이 글에서는 parametrize의 기본 사용법, 다중 파라미터, ID 커스터마이징을 배웁니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `@pytest.mark.parametrize`의 기본 문법
- 여러 파라미터를 동시에 전달하는 방법
- 테스트 ID를 커스터마이징하는 방법
- parametrize와 fixture를 조합하는 패턴

## 왜 중요한가

하나의 함수에 다양한 입력을 테스트해야 할 때, 입력마다 함수를 복사하면 코드가 폭발적으로 늘어납니다. parametrize는 입력-출력 데이터만 나열하면 pytest가 각각을 독립 테스트로 실행합니다.

> 테스트 5개를 복사-붙여넣기하는 대신, 데이터 5줄을 추가합니다. 로직은 하나, 데이터만 다릅니다.

경계값, 빈 입력, 특수문자 같은 엣지 케이스를 빠짐없이 커버하려면 parametrize가 필수입니다.

## 핵심 개념 잡기

> parametrize = 하나의 테스트 함수 + 여러 데이터 세트 → N개의 독립 테스트

```
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),      ← 테스트 1
    ("", 0),            ← 테스트 2
    ("hi", 2),          ← 테스트 3
])
def test_length(input, expected):
    assert len(input) == expected
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| parametrize | 데코레이터로 테스트 파라미터를 주입합니다 |
| 테스트 ID | 각 파라미터 조합에 부여되는 고유 식별자입니다 |
| pytest.param | 개별 테스트 케이스에 ID나 마크를 지정합니다 |
| indirect | parametrize 값을 fixture에 전달합니다 |
| 데카르트 곱 | 여러 parametrize를 중첩하면 조합이 곱해집니다 |

## Before / After

복사-붙여넣기 테스트와 parametrize를 비교합니다.

```python
# before: 입력마다 함수를 복사
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
# after: 데이터만 나열
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

### Step 1: 기본 parametrize

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

### Step 2: 문자열 파라미터

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

### Step 3: 예외 케이스 parametrize

```python
# test_validation.py
import pytest

def parse_age(value: str) -> int:
    age = int(value)
    if age < 0 or age > 150:
        raise ValueError(f"유효하지 않은 나이: {age}")
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

### Step 4: ID 커스터마이징

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

### Step 5: 데카르트 곱 (중첩 parametrize)

```python
# test_cartesian.py
import pytest

@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
@pytest.mark.parametrize("status", [200, 404, 500])
def test_http_response(method, status):
    """3 methods × 3 statuses = 9 테스트가 생성됩니다."""
    response = {"method": method, "status": status}
    assert response["method"] in ["GET", "POST", "PUT", "DELETE"]
    assert isinstance(response["status"], int)
```

## 이 코드에서 주목할 점

- 각 파라미터 조합은 독립 테스트로 실행됩니다 — 하나가 실패해도 나머지는 계속 실행됩니다
- `pytest.param`의 `id`로 테스트 출력에서 의미 있는 이름을 볼 수 있습니다
- 중첩 parametrize는 데카르트 곱을 생성합니다
- 예외 케이스와 정상 케이스를 별도 parametrize로 분리하면 가독성이 좋아집니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 파라미터 이름에 공백 사용 | `"a, b"` 처럼 공백이 있으면 파싱 에러가 발생합니다 | `"a,b"` 또는 리스트 `["a", "b"]`를 사용합니다 |
| 파라미터 수 불일치 | 튜플 원소 수와 파라미터 수가 다르면 에러가 발생합니다 | 모든 튜플의 원소 수를 맞춥니다 |
| 너무 많은 케이스를 한 parametrize에 | 50개 이상이면 가독성이 떨어집니다 | 카테고리별로 parametrize를 나눕니다 |
| 가변 객체를 파라미터에 사용 | 리스트, dict가 테스트 간에 공유될 수 있습니다 | 테스트 내부에서 복사하거나 tuple을 사용합니다 |
| ID 없이 복잡한 파라미터 사용 | 실패 시 `test[param0-param1]`처럼 알아보기 어렵습니다 | `pytest.param(..., id="설명")`을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 유효성 검사 함수의 경계값(빈 문자열, 최대 길이, 특수문자)을 parametrize로 일괄 테스트합니다
- HTTP 엔드포인트의 다양한 상태 코드 응답을 parametrize로 검증합니다
- 국제화(i18n) 테스트에서 여러 언어의 입출력을 parametrize로 커버합니다
- 데이터베이스 쿼리의 다양한 필터 조합을 데카르트 곱으로 테스트합니다
- 파라미터 데이터를 JSON/YAML 파일에서 로드하여 테스트 데이터를 코드와 분리합니다

## 현업 개발자는 이렇게 생각합니다

parametrize는 "같은 검증 로직, 다른 데이터"라는 패턴의 완벽한 해결책입니다. 코드 한 줄 추가 없이 테스트 케이스 5개를 50개로 늘릴 수 있습니다.

실무에서는 버그 리포트를 받으면 해당 입력을 parametrize에 추가하여 회귀 테스트로 남깁니다. 이렇게 하면 같은 버그가 다시 발생했을 때 즉시 감지됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **케이스 명명** — ids 인자로 케이스 이름을 명료화합니다.
- **표 형태 데이터** — 튜플 리스트로 가독성을 유지합니다.
- **크로스 곱 절제** — 파라미터 곱은 빠르게 폭발합니다.
- **실패 격리** — 실패 케이스만 재실행이 가능하도록 ids를 둡니다.
- **회귀 자산** — 버그 케이스를 파라미터로 추가해 회귀를 막습니다.

## 체크리스트

- [ ] `@pytest.mark.parametrize`로 테스트를 작성했다
- [ ] 정상 케이스와 예외 케이스를 분리했다
- [ ] `pytest.param`으로 테스트 ID를 커스터마이징했다
- [ ] 중첩 parametrize로 데카르트 곱을 생성했다
- [ ] `-v` 옵션으로 개별 테스트 케이스를 확인했다

## 연습 문제

1. `fizzbuzz(n)` 함수를 작성하고, 1부터 15까지의 입출력을 parametrize로 테스트하세요.
2. 비밀번호 검증 함수를 작성하고, 최소 길이, 대문자 포함, 숫자 포함 규칙을 parametrize로 테스트하세요.
3. HTTP method와 Content-Type의 데카르트 곱으로 테스트를 생성하고, 총 몇 개의 테스트가 실행되는지 확인하세요.

## 정리 및 다음 글 안내

parametrize는 데이터 주도 테스트의 핵심 도구입니다. 하나의 테스트 함수로 다양한 입력을 커버하여 코드 중복을 제거합니다. 다음 글에서는 외부 의존성을 대체하는 mock과 monkeypatch를 배웁니다.

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
