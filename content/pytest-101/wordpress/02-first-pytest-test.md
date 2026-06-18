---
title: "바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기"
series: pytest-101
episode: 2
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - 테스트 작성
  - test discovery
  - 프로젝트 구조
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 두 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 코드를 생성해도 pytest가 그 코드를 찾지 못하면 검증이 시작되지 않습니다. 바이브코딩 환경에서 AI에게 테스트 파일을 함께 생성해 달라고 요청할 때, pytest의 탐색 규칙을 알고 있어야 올바른 구조를 지시할 수 있습니다. 파일 위치, 이름 규칙, import 경로가 맞아야 팀 전체가 같은 방식으로 테스트를 실행할 수 있습니다.

테스트를 잘 써도 pytest가 파일과 함수를 발견하지 못하면 아무 의미가 없습니다. 그래서 테스트 작성의 출발점은 문법보다 구조입니다.

> "테스트 코드의 위치와 이름이 곧 규칙입니다. 이 규칙만 지키면 pytest가 별도 설정 없이도 대부분을 자동으로 처리합니다."

---

## 이 글에서 다룰 문제

- pytest는 테스트 파일과 함수를 어떤 규칙으로 자동 탐색할까요?
- 프로덕션 코드와 테스트 코드는 어떤 디렉터리 구조로 나누는 편이 좋을까요?
- `pyproject.toml`은 왜 필요한가요?
- AI에게 올바른 구조로 테스트를 생성하도록 어떻게 지시할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

바이브코딩에서 AI는 프로젝트 구조를 알아야 올바른 위치에 테스트 파일을 생성합니다. 구조 규칙을 모르면 AI가 생성한 테스트가 pytest에게 발견되지 않는 상황이 반복됩니다. 테스트 구조를 초기에 제대로 잡아 두면 프로젝트가 커질수록 이점이 더 커집니다.

반대로 구조가 들쭉날쭉하면, 실제 문제는 테스트 로직이 아니라 import 오류, 누락된 파일, 발견되지 않는 함수에서 시작하는 경우가 많습니다.

---

## 핵심 개념 잡기

> test discovery = pytest가 파일명, 클래스명, 함수명 규칙으로 테스트를 자동으로 찾는 메커니즘

```text
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── calculator.py    ← 프로덕션 코드 (AI 생성)
└── tests/
    ├── conftest.py          ← 공유 fixture
    ├── test_calculator.py   ← 테스트 코드 (AI + 직접 작성)
    └── test_utils.py
```

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| test discovery | 파일명·클래스명·함수명 규칙으로 테스트를 자동 탐색합니다 |
| conftest.py | fixture를 여러 테스트 파일에 공유하는 설정 파일입니다 |
| 테스트 노드 ID | `file::class::function` 형태로 개별 테스트를 식별합니다 |
| 테스트 마커 | `@pytest.mark`로 테스트를 분류하고 선택 실행합니다 |
| 종료 코드 | 0은 전체 성공, 1은 일부 실패, 2는 사용자 중단을 의미합니다 |

---

## Before / After: 구조 없는 상태 vs 분리된 구조

AI가 코드를 생성할 때 구조를 명시하지 않으면 이런 결과가 나올 수 있습니다.

**Before: 프로덕션 코드와 테스트가 섞임**

```python
# main.py (AI가 생성한 구조)
def greet(name):
    return f"Hello, {name}"

if __name__ == "__main__":
    print(greet("World"))  # 수동 확인
```

**After: 구조를 명시해 AI에게 요청한 결과**

```python
# src/myapp/greeting.py
def greet(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"
```

```python
# tests/test_greeting.py
import pytest
from myapp.greeting import greet

def test_greet():
    assert greet("World") == "Hello, World"

def test_greet_empty_name():
    with pytest.raises(ValueError):
        greet("")
```

AI에게 "src/ 레이아웃으로 프로덕션 코드를 만들고, tests/ 폴더에 pytest 테스트를 작성해 달라"고 명시적으로 요청하면 올바른 구조를 얻을 수 있습니다.

---

## 실습: 프로젝트 구조 설정

**단계 1: 프로젝트 구조 생성**

```bash
mkdir -p src/myapp tests
touch src/myapp/__init__.py
```

**단계 2: pyproject.toml 설정**

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**단계 3: 프로덕션 코드 작성**

```python
# src/myapp/string_utils.py
def reverse_string(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]

def count_vowels(s: str) -> int:
    return sum(1 for c in s.lower() if c in "aeiou")
```

**단계 4: 테스트 작성**

```python
# tests/test_string_utils.py
import pytest
from myapp.string_utils import reverse_string, count_vowels

class TestReverseString:
    def test_basic(self):
        assert reverse_string("hello") == "olleh"

    def test_empty(self):
        assert reverse_string("") == ""

    def test_type_error(self):
        with pytest.raises(TypeError):
            reverse_string(123)

class TestCountVowels:
    def test_basic(self):
        assert count_vowels("hello") == 2

    def test_no_vowels(self):
        assert count_vowels("xyz") == 0
```

**단계 5: 다양한 방식으로 실행**

```bash
# 전체 테스트 실행
pytest

# 특정 클래스만 실행
pytest tests/test_string_utils.py::TestReverseString

# 키워드 필터
pytest -k "vowel"

# 첫 실패에서 중단
pytest -x
```

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `src/`를 `pythonpath`에 추가하지 않음 | `ModuleNotFoundError`가 발생합니다 | `pyproject.toml`에 `pythonpath = ["src"]`를 추가합니다 |
| `__init__.py` 누락 | 패키지로 인식되지 않을 수 있습니다 | 패키지 디렉터리마다 `__init__.py`를 둡니다 |
| 테스트 클래스에 `__init__`을 정의함 | pytest가 테스트 클래스로 인식하지 않습니다 | 테스트 클래스에는 `__init__`을 두지 않습니다 |
| AI가 `from src.myapp import ...`으로 생성함 | CI에서 실패하기 쉽습니다 | `pythonpath = ["src"]` 설정 후 `from myapp import ...`을 사용합니다 |
| 파일명에 하이픈을 씀 | Python import 경로로 쓰기 어렵습니다 | 언더스코어를 사용합니다 |

---

## AI 코딩 팁

AI에게 테스트를 요청할 때 다음 프롬프트가 효과적입니다.

```text
"src/myapp/ 폴더에 있는 calculator.py 코드를 tests/test_calculator.py에
pytest 스타일로 테스트해 주세요.
- test_ 접두사 규칙을 따르세요
- 정상 케이스, 경계값, 오류 케이스를 모두 포함하세요
- pytest.raises로 예외를 검증하세요"
```

discovery 디버깅이 필요하면 이 명령이 유용합니다.

```bash
pytest --collect-only -q
```

```text
tests/test_string_utils.py::TestReverseString::test_basic
tests/test_string_utils.py::TestReverseString::test_empty
tests/test_string_utils.py::TestCountVowels::test_basic
```

---

## 체크리스트

- [ ] `src/` 레이아웃으로 프로젝트를 구성했다
- [ ] `pyproject.toml`에 `testpaths`와 `pythonpath`를 설정했다
- [ ] `pytest -v`로 전체 테스트를 실행했다
- [ ] 노드 ID로 특정 테스트를 실행했다
- [ ] `-k` 옵션으로 키워드 필터링을 사용했다
- [ ] AI가 생성한 테스트가 올바른 경로에 배치됐는지 확인했다

---

## 처음 질문으로 돌아가기

- **pytest는 테스트 파일과 함수를 어떤 규칙으로 자동 탐색할까요?**
  - `test_*.py` 파일, `Test*` 클래스, `test_*` 함수를 자동으로 찾습니다. `--collect-only`로 수집 목록을 미리 확인할 수 있습니다.
- **프로덕션 코드와 테스트 코드는 어떻게 나눠야 할까요?**
  - `src/` 레이아웃이 가장 실수가 적습니다. AI에게 이 구조를 명시적으로 요청하면 import 오류를 예방할 수 있습니다.
- **`pyproject.toml`은 왜 필요한가요?**
  - `pythonpath = ["src"]` 설정이 없으면 AI가 생성한 import 경로가 CI에서 실패하기 쉽습니다.

---

## 정리

pytest가 테스트를 어떻게 발견하는지, 그리고 왜 구조가 문법보다 먼저인지 감이 잡혔을 것입니다. 바이브코딩 환경에서 AI에게 올바른 구조를 요청하는 것이 테스트 작성의 첫 단추입니다. 다음 글에서는 `assert`가 왜 pytest에서 특히 강력한지, 그리고 예외 테스트를 어떻게 읽기 좋게 작성하는지 봅니다.

---

## 참고 자료

- [pytest — Test Discovery](https://docs.pytest.org/en/stable/goodpractices.html#test-discovery)
- [pytest — Configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [src layout vs flat layout — Python Packaging Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Real Python — Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?
- **바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기 (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기
- 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기
- 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, 테스트 작성, test discovery, 프로젝트 구조, 바이브코딩
