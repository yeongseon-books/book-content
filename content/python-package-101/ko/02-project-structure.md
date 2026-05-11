---
title: 프로젝트 구조 잡기 — src layout과 pyproject.toml
series: python-package-101
episode: 2
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- pyproject.toml
- src layout
- Project Structure
- Packaging
- setuptools
last_reviewed: '2026-05-04'
seo_description: src layout과 pyproject.toml로 Python 프로젝트 구조를 잡는 방법을 설명합니다.
---

# 프로젝트 구조 잡기 — src layout과 pyproject.toml

> Python Package 101 시리즈 (2/10)

---


## 이 글에서 다룰 문제

프로젝트 구조가 잘못되면 `import`가 꼬이고, 빌드 도구가 파일을 못 찾고, CI에서 테스트가 실패합니다. 처음부터 표준 구조를 쓰면 이런 문제를 예방합니다.

> 프로젝트 루트에서 `pytest`를 실행하면 통과하지만, `pip install .`로 설치한 뒤 다른 디렉터리에서 import하면 실패합니다. 테스트가 설치된 패키지가 아니라 로컬 소스를 직접 읽고 있었기 때문입니다.

src layout은 이 문제를 구조적으로 방지합니다.

## Mental Model

> flat layout은 가게 앞에 물건을 바로 진열하는 것이고, src layout은 창고(src/)에 넣고 선반(설치)을 통해서만 꺼내는 것입니다. 창고를 거치면 "설치 안 한 상태에서 동작하는 착각"이 불가능합니다.

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
| flat layout | 패키지가 프로젝트 루트에 바로 있는 구조 | 간단하지만 import 착각 가능 |
| src layout | 패키지가 `src/` 아래에 있는 구조 | 설치 후 테스트를 강제 |
| pyproject.toml | PEP 518/621 표준 프로젝트 설정 파일 | setup.py/setup.cfg 대체 |
| build-system | 빌드에 필요한 도구를 지정하는 섹션 | `[build-system]` |
| [project] | 패키지 이름, 버전, 의존성 등 메타데이터 | PEP 621 |

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

### Step 2. pyproject.toml 작성

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

### Step 5. setuptools 자동 패키지 탐색 설정

```toml
# pyproject.toml에 추가
[tool.setuptools.packages.find]
where = ["src"]
```

```bash
# 설치 재확인
pip install -e .
python -c "import mylib; print(mylib.__version__)"
# 0.1.0
```

## 이 코드에서 봐야 할 것

- `[build-system]`은 빌드에 필요한 도구를 지정하며, `setuptools` 외에 `hatchling`, `flit-core`, `pdm-backend`도 쓸 수 있습니다
- `pip install -e .`은 editable install로, 소스를 수정하면 재설치 없이 바로 반영됩니다
- `[tool.setuptools.packages.find]`의 `where = ["src"]`가 src layout의 핵심 설정입니다
- `requires-python`은 지원하는 Python 버전 범위를 지정합니다

## 자주 하는 실수

### 실수 1. src layout에서 where 설정을 빼먹는다

```toml
# 잘못: src/ 아래 패키지를 못 찾음
[tool.setuptools.packages.find]

# 올바름
[tool.setuptools.packages.find]
where = ["src"]
```

### 실수 2. setup.py와 pyproject.toml을 동시에 쓴다

두 파일이 충돌하면 빌드 도구가 혼란스러워집니다. pyproject.toml만 쓰세요.

### 실수 3. editable install 없이 로컬 import를 테스트한다

`pip install -e .` 없이 테스트하면 flat layout에서는 통과하지만 설치 후에는 실패하는 테스트가 생깁니다.

### 실수 4. __init__.py에 무거운 코드를 넣는다

`__init__.py`에 무거운 초기화 코드를 넣으면 `import mylib`만으로도 느려집니다. 버전과 최소한의 public API만 노출하세요.

### 실수 5. 테스트 디렉터리를 패키지에 포함한다

`tests/`가 `src/` 안에 있으면 배포 패키지에 테스트가 포함됩니다. 테스트는 프로젝트 루트에 둡니다.

## 실무 적용

- **사내 라이브러리**: src layout + pyproject.toml로 표준화하면 신규 프로젝트 시작이 빨라집니다
- **오픈소스**: 대부분의 현대 Python 프로젝트(black, ruff, httpx)가 src layout을 사용합니다
- **모노레포**: src layout은 여러 패키지를 한 저장소에 둘 때 경로 충돌을 방지합니다
- **CI/CD**: `pip install .`로 빌드 가능 여부를 확인하는 것이 첫 번째 게이트입니다
- **Docker**: `COPY . . && pip install .`만으로 컨테이너 내부에 패키지를 설치합니다

## 실무에서는 이렇게 생각한다

프로젝트 초기에 구조를 잡는 데 5분을 쓰면, 나중에 "왜 import가 안 되지?"로 허비하는 시간을 절약합니다. src layout은 약간의 추가 설정(`where = ["src"]`)이 필요하지만, "로컬에서는 되는데 설치하면 안 되는" 문제를 원천 차단합니다.

빌드 백엔드는 `setuptools`가 가장 널리 쓰이지만, 새 프로젝트라면 `hatchling`이나 `flit-core`도 고려하세요. 어떤 백엔드를 쓰든 `pyproject.toml`의 `[project]` 섹션은 동일합니다.

## 체크리스트

- [ ] flat layout과 src layout의 차이를 설명할 수 있다
- [ ] 최소한의 pyproject.toml을 작성할 수 있다
- [ ] `pip install -e .`로 editable install을 할 수 있다
- [ ] `[build-system]`과 `[project]` 섹션의 역할을 알고 있다
- [ ] 테스트가 설치된 패키지를 대상으로 실행되는지 확인할 수 있다

## 정리 · 다음 글

- src layout은 소스를 `src/` 아래에 두어 설치 없이 직접 import되는 것을 방지합니다.
- `pyproject.toml`은 PEP 518/621 표준으로 `setup.py`를 대체합니다.
- `[build-system]`은 빌드 도구를, `[project]`는 패키지 메타데이터를 정의합니다.
- `pip install -e .`로 개발 중에도 import를 테스트할 수 있습니다.
- 테스트는 `src/` 밖에 두어 배포 패키지에 포함되지 않게 합니다.

다음 글에서는 **의존성 관리** — venv, pip, uv, requirements를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- **프로젝트 구조 잡기 — src layout과 pyproject.toml (현재 글)**
- 의존성 관리 — venv, pip, uv, requirements (예정)
- 패키지 빌드하기 — wheel과 sdist (예정)
- PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- 버전 관리와 릴리스 (예정)
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide - Project Structure](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [setuptools - src layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)
- [Hynek Schlawack - Testing & Packaging](https://hynek.me/articles/testing-packaging/)

Tags: Python, pyproject.toml, src layout, Project Structure, Packaging, setuptools
