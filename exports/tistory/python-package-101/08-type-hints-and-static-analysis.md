
# 타입 힌트와 정적 검사

> Python Package 101 시리즈 (8/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 타입 힌트는 왜 필요하고 런타임에 영향을 줄까요?
- `mypy`는 어떤 오류를 잡아줄까요?
- `py.typed` 마커 파일은 왜 필요할까요?
- 제네릭 타입과 Union 타입은 어떻게 쓸까요?

> 타입 힌트는 함수의 입력과 출력 타입을 명시하는 것이고, mypy는 코드를 실행하지 않고 타입 오류를 찾아주는 도구입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 함수, 변수, 반환값에 타입 힌트를 추가하는 법
- `mypy`로 정적 타입 검사를 실행하는 법
- `py.typed` 마커로 패키지를 타입 안전하게 만드는 법
- 제네릭, Union, Optional 등 고급 타입 활용

## 왜 중요한가

Python은 동적 타입 언어지만, 프로젝트가 커지면 "이 함수에 무엇을 넘겨야 하지?"를 코드만 보고 판단하기 어렵습니다. 타입 힌트를 쓰면 IDE가 자동완성하고, mypy가 실행 전에 오류를 잡습니다.

> 함수가 dict를 반환하는데 어떤 키가 있는지 모릅니다. 호출하는 쪽에서 `result["username"]`을 썼는데 실제 키는 `result["user_name"]`이었습니다. 런타임 KeyError가 프로덕션에서 발생했습니다.

## Mental Model

> 타입 힌트는 택배 상자에 붙이는 라벨입니다. "깨지기 쉬운 물건"이라는 라벨이 있으면 배송 기사(mypy)가 주의해서 다루고, 라벨이 없으면 깨져도 알 수 없습니다.

```text
def greet(name: str) -> str:
         ↑ 입력 라벨    ↑ 출력 라벨

mypy가 검사:
  greet(42)    # Error: expected str, got int
  x: int = greet("Alice")  # Error: str assigned to int
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 타입 힌트 | 변수/인자/반환값의 타입 주석 | `name: str` |
| mypy | Python 정적 타입 검사기 | `mypy src/` |
| py.typed | 패키지가 타입 힌트를 포함함을 표시하는 마커 | 빈 파일 |
| Generic | 타입을 매개변수로 받는 타입 | `list[str]`, `dict[str, int]` |
| Union | 여러 타입 중 하나 | `str \| None` (Python 3.10+) |

## Before / After

**Before (타입 힌트 없음)**

```python
def process(data):
    # data가 뭐지? dict? list? str?
    return data["name"]  # KeyError 가능성

result = process({"username": "alice"})  # 런타임 에러
```

**After (타입 힌트 + mypy)**

```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int

def process(data: UserData) -> str:
    return data["name"]

result = process({"username": "alice"})  # mypy가 사전에 에러 감지
```

## 단계별 실습

### Step 1. 기본 타입 힌트

```python
# src/mylib/core.py
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def find_user(user_id: int) -> dict[str, str] | None:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)
```

### Step 2. mypy 설치와 실행

```bash
pip install mypy
mypy src/
# Success: no issues found in 2 source files
```

```python
# 의도적 오류 추가
result: int = greet("Alice")  # str을 int에 할당
```

```bash
mypy src/
# error: Incompatible types in assignment
#   (expression has type "str", variable has type "int")
```

### Step 3. pyproject.toml에 mypy 설정

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

```bash
mypy src/
```

### Step 4. py.typed 마커 추가

```bash
touch src/mylib/py.typed
```

```toml
# pyproject.toml에 포함 설정
[tool.setuptools.package-data]
mylib = ["py.typed"]
```

### Step 5. 고급 타입 활용

```python
# src/mylib/utils.py
from typing import TypeVar, Callable

T = TypeVar("T")

def retry(func: Callable[..., T], attempts: int = 3) -> T | None:
    """함수를 최대 N번까지 재시도합니다."""
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                return None
    return None

# 사용
def fetch_data() -> dict[str, str]:
    return {"key": "value"}

result = retry(fetch_data)  # mypy: dict[str, str] | None
```

## 이 코드에서 봐야 할 것

- 타입 힌트는 런타임에 영향을 주지 않습니다. 순전히 도구(mypy, IDE)를 위한 것입니다
- `py.typed`가 있으면 이 패키지를 사용하는 프로젝트에서도 mypy 검사가 동작합니다
- `strict = true`는 가장 엄격한 검사 모드로, 새 프로젝트에서 시작하기 좋습니다
- Python 3.10+에서는 `X | None`이 `Optional[X]`를 대체합니다

## 자주 하는 실수

### 실수 1. Any를 남용한다

```python
from typing import Any
def process(data: Any) -> Any:  # 타입 힌트를 쓰는 의미가 없음
    ...
```

구체적인 타입을 쓰세요. `dict[str, Any]`라도 `Any`보다 낫습니다.

### 실수 2. py.typed를 빌드에 포함하지 않는다

`py.typed`를 만들었지만 `[tool.setuptools.package-data]`에 포함하지 않으면 wheel에 들어가지 않습니다.

### 실수 3. 기존 코드에 strict를 바로 적용한다

수천 개의 에러가 나옵니다. 기존 코드는 `--disallow-untyped-defs` 등을 점진적으로 활성화하세요.

### 실수 4. 런타임에 타입을 검증한다고 착각한다

```python
def greet(name: str) -> str: ...
greet(42)  # 런타임에서는 정상 실행됨! mypy에서만 에러
```

런타임 검증이 필요하면 `isinstance` 또는 `pydantic`을 쓰세요.

### 실수 5. 서드파티 라이브러리의 타입 스텁을 설치하지 않는다

```bash
pip install types-requests  # requests의 타입 스텁
mypy src/  # import requests의 타입 에러 해소
```

## 실무 적용

- **CI 게이트**: `mypy --strict src/`를 CI에 추가하여 타입 오류 PR을 차단합니다
- **IDE 지원**: VSCode의 Pylance가 타입 힌트를 읽어 자동완성과 에러 표시를 합니다
- **API 문서**: 타입 힌트에서 API 문서를 자동 생성합니다 (Sphinx autodoc)
- **리팩터링 안전망**: 함수 시그니처를 변경하면 모든 호출 지점에서 에러가 발생하여 누락을 방지합니다
- **Pydantic 연동**: 타입 힌트로 데이터 모델을 정의하면 런타임 검증까지 처리됩니다

## 실무에서는 이렇게 생각한다

타입 힌트는 "미래의 나와 팀원을 위한 문서"입니다. 코드를 읽을 때 `data: dict[str, list[int]]`가 있으면 docstring을 읽지 않아도 구조를 알 수 있습니다.

새 프로젝트에서는 처음부터 `strict = true`로 시작하세요. 기존 프로젝트에서는 새 파일부터 타입을 추가하고 점진적으로 확장합니다. "전부 또는 전무"가 아니라 "점진적 도입"이 현실적인 전략입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **py.typed** — 공개 패키지는 py.typed 마커를 둡니다.
- **mypy 엄격도** — strict 옵션을 점진적으로 키웁니다.
- **Public API 우선** — 공개 API에 타입을 가장 먼저 적용합니다.
- **Stub** — 외부 라이브러리 stub 부재는 wrapper로 대처합니다.
- **CI 게이트** — 타입 검사를 CI에 강제합니다.

## 체크리스트

- [ ] 함수의 인자와 반환값에 타입 힌트를 추가할 수 있다
- [ ] `mypy`로 타입 오류를 검사할 수 있다
- [ ] `py.typed` 마커의 역할을 알고 패키지에 포함할 수 있다
- [ ] Generic, Union, Optional 타입을 적절히 사용할 수 있다
- [ ] pyproject.toml에서 mypy 설정을 구성할 수 있다

## 연습 문제

1. 이전 글에서 만든 CLI 패키지의 모든 함수에 타입 힌트를 추가하고, `mypy --strict src/`를 통과시켜보세요.
2. `TypedDict`로 사용자 정보 구조를 정의하고, 잘못된 키 접근을 mypy가 잡는지 확인해보세요.
3. `py.typed`를 추가하고 wheel을 빌드한 뒤, wheel 내부에 `py.typed`가 포함되었는지 확인해보세요.

## 정리 · 다음 글

- 타입 힌트는 코드의 입출력 타입을 명시하여 도구가 오류를 사전에 잡게 합니다.
- `mypy`는 실행 없이 타입 오류를 검사하는 정적 분석기입니다.
- `py.typed` 마커가 있어야 패키지 사용자도 타입 검사 혜택을 받습니다.
- `strict = true`는 새 프로젝트에서 시작하고, 기존 프로젝트는 점진적으로 도입합니다.
- `Any` 남용은 타입 힌트의 효과를 무력화합니다.

다음 글에서는 **문서화** — README, MkDocs, API Reference를 다룹니다.

## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [버전 관리와 릴리스](./06-versioning-and-releases.md)
- [CLI 패키지 만들기](./07-cli-packages.md)
- **타입 힌트와 정적 검사 (현재 글)**
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

## 참고 자료

- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)

Tags: Python, Type Hints, mypy, py.typed, Static Analysis, Typing

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
