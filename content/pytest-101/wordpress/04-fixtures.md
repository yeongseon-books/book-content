---
title: "바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기"
series: pytest-101
episode: 4
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - fixture
  - conftest
  - 테스트 데이터
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 네 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 여러 테스트 파일을 생성하다 보면 같은 데이터 준비 코드가 반복됩니다. fixture는 이 준비 코드를 밖으로 빼내어 테스트를 더 짧고 명확하게 만들어 줍니다. 바이브코딩에서 AI에게 "공통 fixture를 conftest.py에 작성해 달라"고 요청하면, 이후 모든 테스트에서 재사용할 수 있습니다.

테스트마다 같은 객체 생성 코드가 반복되기 시작하면, 테스트 본문이 무엇을 검증하는지보다 무엇을 준비하는지가 더 눈에 띄게 됩니다. fixture는 이 준비 코드를 분리해 테스트 의도를 선명하게 만들어 줍니다.

> "fixture는 Given-When-Then에서 Given을 밖으로 빼내는 도구입니다. AI가 생성한 반복 준비 코드를 fixture로 통합하면 테스트가 훨씬 간결해집니다."

---

## 이 글에서 다룰 문제

- fixture는 일반 함수와 무엇이 다를까요?
- fixture를 테스트 함수에 어떻게 자동으로 주입할까요?
- `function`, `module`, `session` scope는 언제 선택해야 할까요?
- AI에게 fixture를 생성하도록 어떻게 지시할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

AI가 테스트를 생성할 때 공통 데이터를 각 테스트에 직접 포함시키는 경우가 많습니다. 이런 코드는 동작하지만 유지보수가 어렵습니다. fixture 패턴을 이해하면 AI에게 더 나은 테스트 구조를 요청할 수 있습니다.

데이터베이스 연결, API 클라이언트, 임시 파일 같은 자원은 생성보다 정리가 더 중요할 때가 많습니다. fixture는 이 생명주기를 통제하기 위한 가장 자연스러운 장치입니다.

---

## 핵심 개념 잡기

> fixture = 테스트 전에 상태를 준비하고, 필요하면 테스트 후 정리까지 맡는 재사용 가능한 구성요소

```text
@pytest.fixture
def user():            ← fixture 정의
    return User("Alice")

def test_greet(user):  ← 파라미터 이름으로 자동 주입
    assert user.name == "Alice"
```

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| fixture | 테스트에 필요한 데이터나 상태를 제공하는 함수입니다 |
| scope | fixture 생명주기를 결정합니다 |
| yield fixture | `yield` 앞은 setup, 뒤는 teardown입니다 |
| conftest.py | 여러 테스트 파일에 fixture를 공유하는 설정 파일입니다 |
| autouse | 명시적으로 요청하지 않아도 자동 적용되는 fixture입니다 |

---

## Before / After: unittest 스타일 vs pytest fixture

**Before: unittest setUp/tearDown**

```python
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

**After: pytest fixture (AI에게 이 형식으로 요청)**

```python
import pytest

@pytest.fixture
def text_file(tmp_path):
    filepath = tmp_path / "test.txt"
    filepath.write_text("hello")
    return filepath

def test_read(text_file):
    assert text_file.read_text() == "hello"
# teardown 불필요 — tmp_path가 자동 정리
```

AI에게 "unittest 스타일이 아닌 pytest fixture 스타일로 작성해 달라"고 명시하면 더 간결한 코드를 얻을 수 있습니다.

---

## 실습: fixture 단계별 구현

**단계 1: 기본 fixture 정의**

```python
# tests/conftest.py
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

**단계 2: fixture 사용**

```python
# tests/test_user.py
def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"

def test_youngest_user(sample_users):
    youngest = min(sample_users, key=lambda u: u["age"])
    assert youngest["name"] == "Bob"
```

**단계 3: yield로 리소스 관리**

```python
# tests/conftest.py
import pytest
import sqlite3

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.commit()
    yield conn          # 테스트에 연결 제공
    conn.close()        # 테스트 후 자동 정리

def test_query_user(db_connection):
    cursor = db_connection.execute("SELECT name FROM users")
    row = cursor.fetchone()
    assert row[0] == "Alice"
```

**단계 4: scope 설정**

```python
@pytest.fixture(scope="module")
def expensive_resource():
    """모듈 내 모든 테스트가 공유합니다."""
    resource = {"data": list(range(10000))}
    yield resource
    # 정리 코드
```

**단계 5: fixture 합성**

```python
@pytest.fixture
def base_url():
    return "https://api.example.com"

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def api_client(base_url, auth_headers):
    """다른 fixture를 조합합니다."""
    return {"base_url": base_url, "headers": auth_headers}

def test_api_client_has_auth(api_client):
    assert "Authorization" in api_client["headers"]
```

---

## scope 비교

| scope | 생성 시점 | 해제 시점 | 사용 추천 |
|---|---|---|---|
| function | 각 테스트 시작 | 각 테스트 종료 | 기본값, 독립성 최우선 |
| class | 클래스 시작 | 클래스 종료 | 클래스 단위 공유 데이터 |
| module | 파일 시작 | 파일 종료 | 비용 큰 초기화 |
| session | 테스트 세션 시작 | 세션 종료 | 외부 서버, 테스트 DB |

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| fixture 안에서 assert를 함 | fixture는 준비 역할이지 검증 역할이 아닙니다 | 검증은 테스트 함수에서만 합니다 |
| scope가 맞지 않는 fixture를 조합함 | 생명주기 충돌로 오류가 납니다 | 의존 fixture의 scope를 맞춥니다 |
| 리소스를 열어 놓고 정리하지 않음 | 파일과 연결이 누수될 수 있습니다 | `yield` 뒤에 cleanup 코드를 둡니다 |
| AI가 conftest.py를 import하려고 함 | pytest가 자동 로드하므로 불필요합니다 | fixture 이름만 직접 사용합니다 |
| AI 생성 테스트에서 데이터가 중복됨 | 변경 시 여러 곳을 수정해야 합니다 | 공통 데이터를 fixture로 추출합니다 |

---

## AI 코딩 팁

AI에게 fixture를 활용한 테스트를 요청할 때 효과적인 프롬프트 예시입니다.

```text
"아래 테스트들에서 반복되는 데이터 준비 코드를 pytest fixture로 추출해 주세요.
conftest.py에 fixture를 정의하고, 테스트 파일에서 파라미터 주입 방식으로 사용해 주세요.
DB 연결처럼 정리가 필요한 자원은 yield fixture로 작성해 주세요."
```

factory fixture 패턴은 AI 코드 검증에서 특히 유용합니다.

```python
# AI 생성 코드의 다양한 상태를 테스트할 때
@pytest.fixture
def order_factory():
    def _make(**kwargs):
        base = {"id": 1, "amount": 10000, "status": "new"}
        base.update(kwargs)
        return base
    return _make

def test_order_paid(order_factory):
    order = order_factory(status="paid")
    assert order["status"] == "paid"

def test_order_cancelled(order_factory):
    order = order_factory(status="cancelled", amount=0)
    assert order["amount"] == 0
```

---

## 체크리스트

- [ ] `@pytest.fixture`로 fixture를 정의하고 주입했다
- [ ] `yield` fixture로 setup과 teardown을 분리했다
- [ ] scope 차이를 이해하고 적절히 선택했다
- [ ] 공통 fixture를 `conftest.py`에 배치했다
- [ ] AI 생성 테스트의 중복 데이터를 fixture로 추출했다
- [ ] factory fixture로 테스트 데이터 변형을 관리했다

---

## 처음 질문으로 돌아가기

- **fixture는 일반 함수와 무엇이 다를까요?**
  - fixture는 pytest가 파라미터 이름으로 자동 주입하고, scope에 따라 생명주기를 관리합니다. 일반 함수는 수동으로 호출해야 하지만, fixture는 선언만 하면 됩니다.
- **fixture를 테스트 함수에 어떻게 자동으로 주입할까요?**
  - 테스트 함수의 파라미터 이름이 fixture 이름과 일치하면 pytest가 자동으로 주입합니다. AI에게 "fixture 이름을 파라미터로 받는 테스트 함수를 작성해 달라"고 요청하면 됩니다.
- **`function`, `module`, `session` scope는 언제 선택해야 할까요?**
  - 기본값은 `function`입니다. AI 생성 코드에서 비용이 큰 초기화(DB 연결, 외부 서버)는 `module` 또는 `session`으로 올리되, 가변 상태는 공유하지 않아야 합니다.

---

## 정리

fixture는 pytest에서 테스트 데이터를 다루는 중심 도구입니다. scope와 yield를 이해하면 반복 준비 코드를 줄이고, 리소스도 더 안전하게 관리할 수 있습니다. 바이브코딩 환경에서 AI가 생성한 중복 준비 코드를 fixture로 통합하면 테스트 품질이 크게 올라갑니다. 다음 글에서는 하나의 테스트 함수에 여러 입력 세트를 연결하는 parametrization을 봅니다.

---

## 참고 자료

- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest — conftest.py](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-files)
- [pytest — Built-in Fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [Real Python — pytest Fixtures](https://realpython.com/pytest-python-testing/#fixtures-managing-state-and-dependencies)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?
- 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기
- 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트
- **바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기 (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기
- 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, fixture, conftest, 테스트 데이터, 바이브코딩
