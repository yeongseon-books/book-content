---
series: pytest-101
episode: 2
title: 첫 번째 pytest 테스트 작성하기
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
  - 테스트 작성
  - test discovery
  - 프로젝트 구조
seo_description: pytest 테스트 파일 구조와 실행 방법을 실습합니다.
last_reviewed: '2026-05-04'
---

# 첫 번째 pytest 테스트 작성하기

> pytest 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: pytest는 테스트 파일과 함수를 어떻게 자동으로 찾나요?

> pytest는 `test_` 접두사 규칙으로 파일과 함수를 자동 발견합니다. 이 글에서는 프로젝트 구조를 잡고, 테스트를 작성하고, 다양한 실행 옵션을 사용하는 방법을 배웁니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- pytest의 테스트 발견(test discovery) 규칙
- 프로덕션 코드와 테스트 코드의 디렉터리 분리
- pytest 실행 옵션과 출력 해석
- conftest.py의 역할과 위치

## 왜 중요한가

테스트가 아무리 잘 작성되어 있어도, pytest가 테스트를 찾지 못하면 실행되지 않습니다. 프로젝트 구조와 네이밍 규칙을 처음부터 올바르게 잡으면 테스트 관리가 수월해집니다.

> 테스트 코드의 위치와 이름이 곧 규칙입니다. 규칙을 따르면 설정 없이 pytest가 모든 것을 자동으로 처리합니다.

팀 프로젝트에서 테스트 구조가 일관되면, 새 팀원도 코드를 열기 전에 어디에 테스트가 있는지 바로 파악할 수 있습니다.

## 핵심 개념 잡기

> test discovery = pytest가 테스트 파일과 함수를 자동으로 찾는 메커니즘

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── calculator.py    ← 프로덕션 코드
└── tests/
    ├── conftest.py          ← 공유 fixture
    ├── test_calculator.py   ← 테스트 코드
    └── test_utils.py        ← 테스트 코드
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| test discovery | 파일명, 클래스명, 함수명 규칙으로 테스트를 자동 탐색합니다 |
| conftest.py | fixture를 여러 테스트 파일에서 공유하는 설정 파일입니다 |
| 테스트 노드 ID | `파일::클래스::함수` 형태로 개별 테스트를 식별합니다 |
| 테스트 마커 | `@pytest.mark`로 테스트를 분류하고 선택 실행합니다 |
| exit code | 0은 전체 통과, 1은 일부 실패, 2는 사용자 인터럽트입니다 |

## Before / After

테스트 없는 프로젝트와 구조화된 테스트 프로젝트를 비교합니다.

```python
# before: 프로덕션 코드와 테스트가 섞여 있음
# main.py
def greet(name):
    return f"Hello, {name}"

if __name__ == "__main__":
    print(greet("World"))  # 수동 확인
```

```python
# after: 분리된 구조
# src/myapp/greeting.py
def greet(name: str) -> str:
    if not name:
        raise ValueError("이름이 비어 있습니다")
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

### Step 1: 프로젝트 구조 생성

```bash
mkdir -p src/myapp tests
touch src/myapp/__init__.py
```

### Step 2: 프로덕션 코드 작성

```python
# src/myapp/string_utils.py
def reverse_string(s: str) -> str:
    """문자열을 뒤집습니다."""
    if not isinstance(s, str):
        raise TypeError("문자열만 입력할 수 있습니다")
    return s[::-1]

def count_vowels(s: str) -> int:
    """모음 개수를 셉니다."""
    return sum(1 for c in s.lower() if c in "aeiou")

def truncate(s: str, max_length: int = 10) -> str:
    """문자열을 최대 길이로 자릅니다."""
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."
```

### Step 3: 테스트 작성

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

### Step 4: pyproject.toml 설정

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Step 5: 다양한 방식으로 실행

```bash
# 전체 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 파일만
pytest tests/test_string_utils.py

# 특정 클래스만
pytest tests/test_string_utils.py::TestReverseString

# 특정 테스트만
pytest tests/test_string_utils.py::TestReverseString::test_basic

# 키워드로 필터
pytest -k "vowel"

# 첫 실패 시 중단
pytest -x
```

## 이 코드에서 주목할 점

- `class Test*`로 관련 테스트를 그룹화하면 가독성이 좋아집니다
- `pyproject.toml`의 `pythonpath`로 `src` 디렉터리를 인식시킵니다
- `-k` 옵션으로 테스트 이름의 일부만으로 필터링합니다
- 노드 ID(`파일::클래스::함수`)로 정확히 하나의 테스트만 실행합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `src/` 경로를 `pythonpath`에 추가하지 않음 | `ModuleNotFoundError`가 발생합니다 | `pyproject.toml`에 `pythonpath = ["src"]`를 추가합니다 |
| `__init__.py` 누락 | 패키지로 인식되지 않습니다 | 모든 패키지 디렉터리에 `__init__.py`를 생성합니다 |
| 테스트 클래스에 `__init__`을 정의 | pytest가 클래스를 테스트로 인식하지 못합니다 | 테스트 클래스에는 `__init__`을 정의하지 않습니다 |
| conftest.py를 import하려고 시도 | conftest.py는 pytest가 자동으로 로드합니다 | `import conftest`를 사용하지 않습니다 |
| 테스트 파일명에 하이픈 사용 | Python은 하이픈이 포함된 모듈을 import할 수 없습니다 | 하이픈 대신 언더스코어를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- `tests/` 디렉터리를 `src/`와 분리하여 배포 패키지에 테스트가 포함되지 않도록 합니다
- `conftest.py`에 데이터베이스 연결, HTTP 클라이언트 같은 공통 fixture를 정의합니다
- `-x` 플래그로 CI에서 첫 실패 시 빠르게 중단합니다
- `pytest.ini` 또는 `pyproject.toml`로 팀 전체가 동일한 설정을 사용합니다
- `-k` 필터로 특정 기능에 관련된 테스트만 빠르게 실행합니다

## 현업 개발자는 이렇게 생각합니다

프로젝트 초기에 테스트 구조를 잡아두면, 코드가 커져도 테스트 관리가 쉬워집니다. "나중에 테스트를 추가하겠다"는 말은 대부분 "절대 추가하지 않겠다"와 같습니다.

실무에서는 `src/` 레이아웃을 사용하여 프로덕션 코드와 테스트를 명확히 분리합니다. 이렇게 하면 `pip install .`로 설치할 때 테스트 코드가 포함되지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **이름이 명세** — 함수명이 곧 명세 문장이 되도록 작성합니다.
- **AAA 구조** — arrange/act/assert 단계를 분명히 합니다.
- **단일 단언** — 한 테스트는 한 가지를 검증합니다.
- **독립성** — 테스트 간 상태 공유를 만들지 않습니다.
- **실행 빠르게** — 느린 테스트는 별도 마커로 분리합니다.

## 체크리스트

- [ ] `src/` 레이아웃으로 프로젝트를 구성했다
- [ ] `pyproject.toml`에 `testpaths`와 `pythonpath`를 설정했다
- [ ] `pytest -v`로 전체 테스트를 실행했다
- [ ] 노드 ID로 특정 테스트를 실행했다
- [ ] `-k` 옵션으로 키워드 필터링을 사용했다

## 연습 문제

1. `capitalize_words(s)` 함수를 작성하고, 빈 문자열, 단일 단어, 여러 단어 입력에 대한 테스트를 클래스로 그룹화하세요.
2. `pyproject.toml` 없이 `pytest`를 실행했을 때 발생하는 에러를 확인하고, 설정을 추가하여 해결하세요.
3. `-k` 옵션으로 "reverse"가 포함된 테스트만 실행하고 결과를 확인하세요.

## 정리 및 다음 글 안내

pytest의 테스트 발견 규칙과 프로젝트 구조를 배웠습니다. `test_` 접두사와 `src/` 레이아웃이 핵심입니다. 다음 글에서는 `assert`의 다양한 사용법과 예외 테스트를 심도 있게 다룹니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
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
