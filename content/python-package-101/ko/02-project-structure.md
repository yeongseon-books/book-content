---
title: "Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml"
series: python-package-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- pyproject.toml
- src layout
- Project Structure
- Packaging
- setuptools
last_reviewed: '2026-05-15'
seo_description: src layout과 pyproject.toml로 Python 프로젝트 구조를 잡는 방법을 설명합니다.
---

# Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml

패키징은 파일 몇 개를 묶는 수준에서 끝나지 않습니다. 어디에 소스를 두고, 어떤 파일에 메타데이터를 적고, 테스트가 실제 설치된 패키지를 검증하도록 구조를 어떻게 잡을지까지 함께 결정해야 합니다.

이 글은 Python Package 101 시리즈의 2번째 글입니다. 여기서는 flat layout과 src layout의 차이, `pyproject.toml`이 `setup.py`를 대체한 이유, 그리고 패키지 프로젝트의 최소 표준 구조를 정리하겠습니다.

## 먼저 던지는 질문

- flat layout과 src layout은 무엇이 다를까요?
- `pyproject.toml`은 무엇이고 왜 `setup.py`를 대체할까요?
- `[build-system]`과 `[project]`에는 무엇이 들어갈까요?

## 큰 그림

![Python Package 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/02/02-01-mental-model.ko.png)

*Python Package 101 2장 흐름 개요*

## 이 글에서 배우는 내용

- flat layout과 src layout의 차이와 선택 기준
- `pyproject.toml`에서 꼭 알아야 할 섹션
- 최소 구성을 갖춘 `pyproject.toml` 작성법
- 실무에서 많이 쓰는 프로젝트 디렉터리 구조

## 왜 중요한가

프로젝트 구조가 어긋나면 `import`가 꼬이고, 빌드 도구가 파일을 찾지 못하고, 로컬에서는 통과하던 테스트가 CI에서는 실패합니다. 이런 문제는 대개 로직보다 구조에서 먼저 시작합니다. 따라서 초기에 표준 구조를 잡아두는 편이 나중에 훨씬 저렴합니다.

> 프로젝트 루트에서 `pytest`를 실행하면 모든 테스트가 통과합니다. 그런데 `pip install .`로 설치한 뒤 다른 디렉터리에서 import하면 실패합니다. 테스트가 설치된 패키지를 검증한 것이 아니라, 로컬 소스를 우연히 직접 읽고 있었기 때문입니다.

src layout은 이런 착시를 구조적으로 막아 줍니다.

## 멘탈 모델

flat layout은 가게 앞 진열대에 상품을 바로 올려두는 방식이고, src layout은 상품을 창고(`src/`)에 넣고 선반(설치)으로만 꺼내는 방식입니다. 창고를 거치면 “설치하지 않아도 잘 되네”라는 착각이 원천적으로 줄어듭니다.

```text
flat layout              src layout
────────────            ────────────
mylib/                  src/
  __init__.py             mylib/
  core.py                   __init__.py
tests/                      core.py
pyproject.toml          tests/
                        pyproject.toml
```

## 핵심 개념

| 용어 | 설명 | 비고 |
|---|---|---|
| flat layout | 패키지가 프로젝트 루트에 바로 있는 구조 | 간단하지만 import 착시가 생기기 쉽습니다 |
| src layout | 패키지가 `src/` 아래에 있는 구조 | install-before-import를 강제합니다 |
| pyproject.toml | PEP 518/621 표준 프로젝트 설정 파일 | `setup.py`, `setup.cfg`를 대체합니다 |
| build-system | 빌드 도구를 지정하는 섹션 | `[build-system]` |
| [project] | 이름, 버전, 의존성 등 메타데이터 | PEP 621 |

## Before / After

**Before (setup.py + flat layout)**

```python
# setup.py
from setuptools import setup, find_packages
setup(
    name="mylib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests>=2.28"],
)
```

**After (pyproject.toml + src layout)**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mylib"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["requests>=2.28"]
```

## 단계별 실습

### Step 1. src layout 프로젝트 만들기

```bash
mkdir -p ~/practice/mylib-project/src/mylib
mkdir -p ~/practice/mylib-project/tests
cd ~/practice/mylib-project

cat > src/mylib/__init__.py << 'EOF'
"""mylib - A sample Python package."""
__version__ = "0.1.0"
EOF

cat > src/mylib/core.py << 'EOF'
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"
EOF
```

### Step 2. `pyproject.toml` 작성

```bash
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mylib"
version = "0.1.0"
description = "A sample Python package"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"},
]
dependencies = []

[project.urls]
Repository = "https://github.com/yourname/mylib"
EOF
```

### Step 3. 개발 모드 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

python -c "from mylib.core import greet; print(greet('World'))"
# Hello, World!
```

### Step 4. 테스트 추가

```bash
cat > tests/test_core.py << 'EOF'
from mylib.core import greet

def test_greet():
    assert greet("Alice") == "Hello, Alice!"

def test_greet_empty():
    assert greet("") == "Hello, !"
EOF

pip install pytest
pytest tests/
# 2 passed
```

### Step 5. setuptools 패키지 탐색 설정

```toml
# Add to pyproject.toml
[tool.setuptools.packages.find]
where = ["src"]
```

```bash
# Verify install
pip install -e .
python -c "import mylib; print(mylib.__version__)"
# 0.1.0
```

## 이 코드에서 눈여겨볼 점

- `[build-system]`은 빌드 도구를 지정하며 `setuptools` 외에도 `hatchling`, `flit-core`, `pdm-backend`를 선택할 수 있습니다.
- `pip install -e .`은 editable install이므로 재설치 없이 소스 변경을 반영할 수 있습니다.
- `[tool.setuptools.packages.find]`의 `where = ["src"]`가 src layout에서 가장 중요한 설정입니다.
- `requires-python`은 이 패키지가 지원하는 Python 버전 범위를 문서이자 계약으로 남깁니다.

## 자주 하는 실수

### 실수 1. src layout에서 `where` 설정을 빼먹는다

```toml
# Wrong: cannot find packages under src/
[tool.setuptools.packages.find]

# Correct
[tool.setuptools.packages.find]
where = ["src"]
```

### 실수 2. `setup.py`와 `pyproject.toml`을 동시에 유지한다

두 파일이 함께 있으면 빌드 도구가 어느 쪽을 기준으로 삼아야 할지 혼란스러워질 수 있습니다. 특별한 이유가 없다면 `pyproject.toml` 하나로 정리하는 편이 좋습니다.

### 실수 3. editable install 없이 로컬 import만 테스트한다

`pip install -e .` 없이 테스트하면 flat layout에서는 우연히 통과하지만, 실제 설치 환경에서는 실패하는 테스트를 놓치기 쉽습니다.

### 실수 4. `__init__.py`에 무거운 초기화 코드를 넣는다

`import mylib`만 했는데 느려지는 패키지는 사용성이 떨어집니다. `__init__.py`에는 버전과 최소한의 public API 정도만 두는 편이 안전합니다.

### 실수 5. `tests/`를 패키지 내부에 둔다

`tests/`가 `src/` 아래에 들어가면 배포판에 테스트 코드가 포함될 수 있습니다. 테스트는 프로젝트 루트에 두는 편이 명확합니다.

## 실무 적용

- **사내 라이브러리**: src layout + `pyproject.toml`로 표준화하면 신규 프로젝트 시작이 빨라집니다.
- **오픈소스**: `black`, `ruff`, `httpx`처럼 현대적인 Python 프로젝트 대부분이 src layout을 사용합니다.
- **모노레포**: 하나의 저장소에 여러 패키지를 둘 때 경로 충돌을 줄여 줍니다.
- **CI/CD**: `pip install .`을 첫 번째 검증 단계로 넣어 빌드 가능성을 빠르게 확인합니다.
- **Docker**: `COPY . . && pip install .`만으로 컨테이너 내부 설치 흐름을 단순화할 수 있습니다.

## 실무에서는 이렇게 생각합니다

구조를 잡는 데 초반 5분을 쓰면, 나중에 “왜 import가 안 되지?”에 몇 시간을 쓰는 일을 줄일 수 있습니다. src layout은 약간의 추가 설정이 필요하지만, 로컬 소스와 설치된 패키지를 혼동하는 문제를 구조적으로 차단합니다.

빌드 백엔드로는 `setuptools`가 여전히 가장 널리 쓰입니다. 다만 새 프로젝트라면 `hatchling`이나 `flit-core`도 충분히 검토할 만합니다. 중요한 점은 백엔드가 무엇이든 `[project]` 섹션이라는 공통 표준이 유지된다는 사실입니다.

## 체크리스트

- [ ] flat layout과 src layout의 차이를 설명할 수 있다
- [ ] 최소한의 `pyproject.toml`을 작성할 수 있다
- [ ] `pip install -e .`로 editable install을 할 수 있다
- [ ] `[build-system]`과 `[project]`의 역할을 이해한다
- [ ] 테스트가 설치된 패키지를 기준으로 실행되는지 확인할 수 있다

## 연습 문제

1. src layout으로 `myutils` 패키지를 만들고, `string_utils.py` 안에 `capitalize_words` 함수를 구현한 뒤 테스트해 보세요.
2. `description`, `authors`, `license`, `requires-python`을 포함한 `pyproject.toml`을 직접 작성해 보세요.
3. flat layout 프로젝트와 src layout 프로젝트를 각각 만든 뒤 `pip install -e .`을 실행하고, 다른 디렉터리에서 import가 어떻게 달라지는지 비교해 보세요.

## 정리 · 다음 글

- src layout은 소스를 `src/` 아래에 두어 설치 없이 직접 import되는 착시를 막습니다.
- `pyproject.toml`은 PEP 518/621 표준으로 `setup.py`를 대체합니다.
- `[build-system]`은 빌드 도구를, `[project]`는 패키지 메타데이터를 정의합니다.
- `pip install -e .`을 쓰면 개발 중에도 실제 설치 경로를 기준으로 import를 검증할 수 있습니다.
- 테스트는 `src/` 밖에 두어 배포판에 섞이지 않게 유지하는 편이 좋습니다.

다음 글에서는 **의존성 관리** — venv, pip, uv, requirements를 다룹니다.

## pyproject.toml 심층 분석

`pyproject.toml`은 PEP 518(빌드 시스템 선언)과 PEP 621(프로젝트 메타데이터)의 결합입니다. 하나의 파일로 빌드 도구, 메타데이터, 도구 설정을 모두 관리합니다.

### 전체 구조 맵

```toml
# === 빌드 시스템 (PEP 518) ===
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

# === 프로젝트 메타데이터 (PEP 621) ===
[project]
name = "acme-utils"
version = "0.1.0"
description = "Internal utility library for Acme Corp"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Platform Team", email = "platform@acme.dev"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.27,<0.29",
    "pydantic>=2.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
    "build>=1.2",
    "twine>=5.1",
]
docs = [
    "mkdocs>=1.6",
    "mkdocstrings[python]>=0.25",
]

[project.urls]
Homepage = "https://github.com/acme/acme-utils"
Documentation = "https://acme.github.io/acme-utils"
Changelog = "https://github.com/acme/acme-utils/blob/main/CHANGELOG.md"

[project.scripts]
acme = "acme_utils.cli:main"

# === 도구별 설정 ===
[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.mypy]
strict = true
```

### `[build-system]` 상세

| 필드 | 역할 | 예시 |
|---|---|---|
| `requires` | 빌드에 필요한 패키지 목록 | `["setuptools>=68", "wheel"]` |
| `build-backend` | 빌드 진입점 | `"setuptools.build_meta"` |
| `backend-path` | 커스텀 백엔드 경로 (드문 경우) | `["."]` |

`pip install .`을 실행하면 pip은 먼저 격리된 환경을 만들고, `requires`에 명시된 패키지를 설치한 뒤, `build-backend`가 가리키는 모듈의 `build_wheel()` 또는 `build_sdist()`를 호출합니다.

### `[project]` 필수 필드 vs 선택 필드

```text
필수 (PyPI 업로드 시):
├── name          # 배포 이름
├── version       # 시맨틱 버전
필수 (사실상):
├── description   # 한 줄 설명
├── requires-python
권장:
├── readme
├── license
├── authors
├── classifiers
├── dependencies
선택:
├── optional-dependencies
├── urls
├── scripts / gui-scripts
├── entry-points
```

### 빌드 백엔드 비교

| 백엔드 | 장점 | 단점 |
|---|---|---|
| setuptools | 생태계 최대, 레거시 호환 | 설정이 많을 수 있음 |
| hatchling | 빠른 빌드, 간결한 설정 | 비교적 신생 |
| flit-core | 매우 단순 | 기능이 적음 (C 확장 불가) |
| maturin | Rust 확장 빌드 | Rust 전용 |
| pdm-backend | pdm 생태계 통합 | 독자적 lock 방식 |

```toml
# hatchling 예시
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
```

```toml
# flit-core 예시
[build-system]
requires = ["flit_core>=3.9,<4"]
build-backend = "flit_core.buildapi"
```

## src layout이 import 착시를 막는 원리

flat layout에서 테스트가 통과하지만 설치 후 실패하는 시나리오를 재현해 보겠습니다.

```bash
# flat layout 구조
myproject/
├── mylib/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

```bash
# 프로젝트 루트에서 pytest 실행
cd myproject
pytest tests/
# PASSED - 현재 디렉터리의 mylib/을 직접 import

# 다른 디렉터리에서 import 시도 (설치 안 한 상태)
cd /tmp
python -c "import mylib"
# ModuleNotFoundError!
```

```bash
# src layout 구조
myproject/
├── src/
│   └── mylib/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

```bash
# 프로젝트 루트에서 pytest 실행 (설치 안 한 상태)
cd myproject
pytest tests/
# ModuleNotFoundError - src/mylib/이 sys.path에 없음!
# -> 반드시 pip install -e . 후 테스트해야 함
```

src layout은 "설치 없이 테스트 통과"라는 착시를 구조적으로 불가능하게 만듭니다. CI와 동일한 조건에서 항상 테스트를 실행하게 됩니다.

## 실전 프로젝트 디렉터리 완전체

```text
acme-utils/
├── src/
│   └── acme_utils/
│       ├── __init__.py          # __version__, public API
│       ├── py.typed             # PEP 561 마커
│       ├── core.py              # 핵심 비즈니스 로직
│       ├── config.py            # 설정 로드
│       ├── exceptions.py        # 커스텀 예외
│       └── _internal.py         # 내부 전용 (_prefix)
├── tests/
│   ├── conftest.py              # 공용 fixture
│   ├── test_core.py
│   └── test_config.py
├── docs/
│   ├── index.md
│   └── api.md
├── pyproject.toml               # 단일 설정 파일
├── README.md                    # PyPI 렌더링용
├── CHANGELOG.md                 # 릴리스 기록
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml               # CI 파이프라인
```

### 각 파일의 역할

| 파일 | 역할 |
|---|---|
| `py.typed` | 빈 파일. 이 패키지가 타입 힌트를 제공함을 선언 (PEP 561) |
| `_internal.py` | `_` 접두사로 외부 사용 불가임을 명시 |
| `conftest.py` | pytest가 자동 로드하는 fixture 모듈 |
| `CHANGELOG.md` | 버전별 변경사항. Keep a Changelog 형식 권장 |

## setup.py에서 pyproject.toml로의 마이그레이션

레거시 프로젝트에서 모던 구조로 전환하는 단계별 절차입니다.

### 마이그레이션 전 (레거시)

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="acme-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27",
        "pydantic>=2.5",
    ],
    python_requires=">=3.10",
)
```

### 마이그레이션 후 (모던)

```toml
# pyproject.toml - setup.py 내용을 그대로 옮김
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "acme-utils"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.5",
]

[tool.setuptools.packages.find]
where = ["src"]
```

### 마이그레이션 체크리스트

```bash
# 1. pyproject.toml 작성
# 2. 소스를 src/ 아래로 이동
mkdir -p src
mv acme_utils src/

# 3. setup.py 제거 (또는 shim으로 유지)
# shim: 레거시 도구 호환용
cat > setup.py << 'EOF'
from setuptools import setup
setup()
EOF

# 4. editable install 확인
pip install -e .
python -c "import acme_utils; print(acme_utils.__version__)"

# 5. 테스트 통과 확인
pytest

# 6. 빌드 확인
python -m build
python -m twine check dist/*
```

## GitHub Actions CI 연동

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install -e ".[dev]"
      - run: pytest --cov=acme_utils --cov-report=term-missing
      - run: ruff check .
      - run: mypy src
      - run: python -m build
      - run: python -m twine check dist/*
```

이 워크플로우는 세 가지 Python 버전에서 lint, 타입 검사, 테스트, 빌드 검증을 모두 실행합니다. `pip install -e ".[dev]"`로 개발 의존성까지 한 번에 설치합니다.

## pyproject.toml 동적 버전 관리

버전을 `pyproject.toml`에 하드코딩하는 대신 동적으로 가져오는 패턴이 실무에서 자주 사용됩니다.

### setuptools-scm: Git 태그에서 버전 추출

```toml
[build-system]
requires = ["setuptools>=68", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "acme-utils"
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/acme_utils/_version.py"
```

```bash
git tag v0.1.0
python -m build
# 빌드 시 자동으로 0.1.0 버전이 설정됨
```

### hatchling의 동적 버전

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "acme-utils"
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"
```

### __init__.py에서 버전 읽기 패턴

```python
# src/acme_utils/__init__.py
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"
```

이 패턴을 사용하면 Git 태그가 버전의 단일 출처가 됩니다. `pyproject.toml`, `__init__.py`, Git 태그 세 곳의 버전이 항상 일치합니다.

## 모노레포에서의 패키지 구조

하나의 저장소에 여러 패키지를 두는 모노레포 구조도 실무에서 흔합니다.

```text
monorepo/
├── packages/
│   ├── acme-core/
│   │   ├── src/acme_core/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── acme-auth/
│   │   ├── src/acme_auth/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── acme-cli/
│       ├── src/acme_cli/
│       ├── tests/
│       └── pyproject.toml
├── pyproject.toml              # 루트: 개발 도구 설정
└── Makefile
```

```toml
# packages/acme-auth/pyproject.toml
[project]
name = "acme-auth"
dependencies = [
    "acme-core",  # 같은 모노레포의 다른 패키지 참조
]
```

```bash
# 개발 시 모든 패키지를 editable로 설치
pip install -e packages/acme-core
pip install -e packages/acme-auth
pip install -e packages/acme-cli
```

## EditorConfig와 개발 도구 설정 파일 배치

프로젝트 루트에는 `pyproject.toml` 외에도 개발 경험을 일관되게 만드는 설정 파일이 필요합니다.

```text
acme-utils/
├── .editorconfig           # 에디터 공통 설정
├── .gitignore              # Git 무시 패턴
├── .pre-commit-config.yaml # 커밋 전 자동 검사
└── pyproject.toml          # 모든 Python 도구 설정 통합
```

```ini
# .editorconfig
root = true

[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 4

[*.{yml,yaml,toml}]
indent_size = 2
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

이 설정들은 팀원 간 코드 스타일 차이를 줄이고, 리뷰에서 형식 문제에 시간을 쓰지 않게 만듭니다.

## 처음 질문으로 돌아가기

- **flat layout과 src layout은 무엇이 다를까요?**
  - flat layout은 패키지 디렉터리가 프로젝트 루트에 바로 위치하여 설치 없이도 import됩니다. src layout은 패키지를 `src/` 아래에 두어 `pip install -e .` 없이는 import할 수 없게 만듭니다. 이 차이가 "로컬에서는 되는데 CI에서 실패" 문제를 구조적으로 방지합니다.

- **`pyproject.toml`은 무엇이고 왜 `setup.py`를 대체할까요?**
  - `pyproject.toml`은 PEP 518/621 표준으로, 선언적 TOML 파일 하나에 빌드 시스템과 메타데이터를 모두 담습니다. `setup.py`는 임의의 Python 코드를 실행할 수 있어 보안과 재현성 문제가 있었고, `pyproject.toml`은 정적 분석이 가능하고 도구 간 상호운용성을 보장합니다.

- **`[build-system]`과 `[project]`에는 무엇이 들어갈까요?**
  - `[build-system]`은 빌드 도구(`requires`)와 진입점(`build-backend`)을 선언합니다. pip은 이 정보를 읽어 격리 환경에서 빌드합니다. `[project]`는 패키지 이름, 버전, 의존성, Python 요구 버전 등 메타데이터를 담으며, PyPI 페이지에 표시되는 정보의 원천입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- **Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml (현재 글)**
- Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements (예정)
- Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist (예정)
- Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- Python Package 101 (6/10): 버전 관리와 릴리스 (예정)
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging User Guide - Project Structure](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [setuptools - src layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)
- [Hynek Schlawack - Testing & Packaging](https://hynek.me/articles/testing-packaging/)

Tags: Python, Packaging, PyPI, pyproject.toml
