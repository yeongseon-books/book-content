
# fixture 이해하기

> pytest 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 여러 테스트에서 같은 데이터를 반복 생성하는 코드를 어떻게 줄일 수 있나요?

> pytest fixture는 테스트에 필요한 데이터나 상태를 함수로 정의하고, 파라미터 이름만으로 자동 주입합니다. 이 글에서는 fixture의 생성, scope 관리, yield를 활용한 정리(teardown)를 배웁니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- fixture를 정의하고 테스트에 주입하는 방법
- fixture scope(function, class, module, session)의 차이
- yield fixture로 setup과 teardown을 분리하는 패턴
- conftest.py로 fixture를 여러 파일에서 공유하는 구조

## 왜 중요한가

테스트마다 동일한 객체를 생성하는 코드가 반복되면, 테스트 코드가 비대해지고 유지보수가 어려워집니다. fixture는 이 반복을 제거하고, 테스트가 "무엇을 검증하는지"에 집중하게 합니다.

> fixture는 테스트의 "Given" 단계입니다. Given-When-Then에서 Given을 fixture로 분리하면, 테스트 본문은 When과 Then만 남습니다.

데이터베이스 연결, API 클라이언트, 임시 파일 같은 리소스는 fixture로 관리해야 안전하게 생성하고 정리할 수 있습니다.

## 핵심 개념 잡기

> fixture = 테스트 실행 전에 준비하고, 실행 후에 정리하는 재사용 가능한 컴포넌트

```
@pytest.fixture
def user():          ← fixture 정의
    return User("Alice")

def test_greet(user):  ← 파라미터 이름으로 자동 주입
    assert user.name == "Alice"
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| fixture | 테스트에 필요한 데이터나 상태를 제공하는 함수입니다 |
| scope | fixture의 생명주기를 결정합니다 (function, class, module, session) |
| yield fixture | yield 이전이 setup, 이후가 teardown입니다 |
| conftest.py | fixture를 여러 테스트 파일에서 공유하는 설정 파일입니다 |
| autouse | 명시적 요청 없이 자동으로 적용되는 fixture입니다 |

## Before / After

setup/teardown 메서드와 fixture를 비교합니다.

```python
# before: unittest 스타일 — setUp/tearDown
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
# after: pytest fixture — 선언적이고 재사용 가능
import pytest
import tempfile
import os

@pytest.fixture
def text_file(tmp_path):
    filepath = tmp_path / "test.txt"
    filepath.write_text("hello")
    return filepath

def test_read(text_file):
    assert text_file.read_text() == "hello"
# teardown 불필요 — tmp_path가 자동 정리
```

## 단계별 실습

### Step 1: 기본 fixture 정의

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

### Step 2: fixture 사용

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

### Step 3: yield fixture로 리소스 관리

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
    yield conn  # 테스트에 conn 제공
    conn.close()  # 테스트 완료 후 정리

# test_db.py
def test_query_user(db_connection):
    cursor = db_connection.execute("SELECT name FROM users")
    row = cursor.fetchone()
    assert row[0] == "Alice"
```

### Step 4: scope 활용

```python
# conftest.py
import pytest

@pytest.fixture(scope="module")
def expensive_resource():
    """모듈 내 모든 테스트가 공유합니다."""
    print("리소스 생성 (한 번만 실행)")
    resource = {"data": list(range(10000))}
    yield resource
    print("리소스 정리 (모듈 끝에 한 번)")

# test_scope.py
def test_first(expensive_resource):
    assert len(expensive_resource["data"]) == 10000

def test_second(expensive_resource):
    # 같은 리소스를 재사용합니다
    assert expensive_resource["data"][0] == 0
```

### Step 5: fixture 합성

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
    """다른 fixture를 조합합니다."""
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

- fixture 이름이 곧 파라미터 이름입니다 — 명시적 호출 없이 자동 주입됩니다
- `yield` 이전 코드가 setup, 이후 코드가 teardown입니다
- `scope="module"`로 비용이 큰 리소스의 생성 횟수를 줄입니다
- fixture를 다른 fixture의 파라미터로 사용하여 합성합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| fixture에서 직접 assert를 사용 | fixture는 데이터를 제공하는 역할이지 검증 역할이 아닙니다 | assert는 테스트 함수에서만 사용합니다 |
| function scope fixture를 module scope에서 사용 | scope 불일치로 에러가 발생합니다 | 의존하는 fixture의 scope를 맞춥니다 |
| yield 없이 리소스를 열기만 함 | 파일이나 연결이 닫히지 않습니다 | yield를 사용하여 정리 코드를 추가합니다 |
| conftest.py를 import하려 함 | pytest가 자동으로 로드하므로 import가 불필요합니다 | import 없이 fixture 이름만 사용합니다 |
| autouse를 남용 | 모든 테스트에 불필요한 fixture가 적용됩니다 | autouse는 로깅, 타이밍 같은 공통 관심사에만 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 연결을 session scope fixture로 관리하여 테스트 속도를 높입니다
- `tmp_path` 내장 fixture로 임시 파일을 생성하고 자동 정리합니다
- API 테스트에서 인증 토큰을 fixture로 제공합니다
- 여러 conftest.py를 디렉터리별로 배치하여 테스트 계층에 맞는 fixture를 제공합니다
- factory fixture 패턴으로 다양한 변형의 테스트 데이터를 생성합니다

## 현업 개발자는 이렇게 생각합니다

fixture는 테스트의 가독성과 유지보수성을 결정하는 핵심 요소입니다. 잘 설계된 fixture는 테스트 코드를 "시나리오 설명"처럼 읽을 수 있게 만듭니다.

scope 선택은 "이 데이터가 테스트 간에 공유되어도 안전한가?"를 기준으로 판단합니다. 불변 데이터는 module이나 session scope를, 변경 가능한 데이터는 function scope를 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **스코프 명시** — function/module/session 스코프를 의도적으로 정합니다.
- **teardown** — 리소스 종료를 yield로 보장합니다.
- **autouse 절제** — autouse는 디버깅을 어렵게 만들 수 있습니다.
- **conftest 정리** — 공용 fixture는 conftest.py에 둡니다.
- **의존성 주입** — fixture가 곧 DI 메커니즘입니다.

## 체크리스트

- [ ] `@pytest.fixture`로 fixture를 정의하고 테스트에 주입했다
- [ ] yield fixture로 setup/teardown을 분리했다
- [ ] scope의 차이를 이해하고 적절히 선택했다
- [ ] conftest.py에 공통 fixture를 배치했다
- [ ] fixture 합성으로 복잡한 테스트 데이터를 구성했다

## 연습 문제

1. SQLite in-memory 데이터베이스를 fixture로 제공하고, INSERT와 SELECT를 검증하는 테스트를 작성하세요.
2. `tmp_path` 내장 fixture를 사용하여 임시 JSON 파일을 생성하고 읽는 테스트를 작성하세요.
3. `scope="session"` fixture와 `scope="function"` fixture의 실행 횟수 차이를 `-s` 플래그로 확인하세요.

## 정리 및 다음 글 안내

fixture는 테스트 데이터를 관리하는 pytest의 핵심 메커니즘입니다. scope와 yield를 이해하면 리소스를 안전하고 효율적으로 관리할 수 있습니다. 다음 글에서는 parametrization으로 하나의 테스트 함수에서 여러 입력을 검증하는 방법을 배웁니다.

- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- **fixture 이해하기 (현재 글)**
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)
## 참고 자료

- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest — conftest.py](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-files)
- [pytest — Built-in Fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [Real Python — pytest Fixtures](https://realpython.com/pytest-python-testing/#fixtures-managing-state-and-dependencies)

Tags: Python, pytest, fixture, conftest, 테스트 데이터

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
