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

이 그림에서는 첫 번째 pytest 테스트 작성하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 첫 번째 pytest 테스트 작성하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

Tags: Python, pytest, 테스트 작성, test discovery, 프로젝트 구조
