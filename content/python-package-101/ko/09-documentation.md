---
title: "Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference"
series: python-package-101
episode: 9
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
- Documentation
- MkDocs
- README
- API Reference
- Sphinx
last_reviewed: '2026-05-15'
seo_description: README는 패키지의 현관문이고, API Reference는 모든 함수의 사용 설명서입니다. 문서가 없는 패키지는 쓰이지 않습니다.
---

# Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference

패키지가 아무리 잘 만들어져 있어도, 사용자가 30초 안에 “이걸 어떻게 설치하고 어디서 시작해야 하는지” 파악할 수 없다면 실제 채택으로 이어지기 어렵습니다. 문서는 코드의 부록이 아니라 패키지 자체의 일부입니다.

이 글은 Python Package 101 시리즈의 9번째 글입니다. 여기서는 좋은 README의 구조, MkDocs 기반 문서 사이트, docstring에서 API Reference를 생성하는 흐름을 정리하겠습니다.

## 먼저 던지는 질문

- 좋은 README에는 무엇이 들어가야 할까요?
- MkDocs와 Sphinx는 무엇이 다를까요?
- docstring에서 API Reference를 자동 생성하려면 어떻게 해야 할까요?

## 큰 그림

![Python Package 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/09/09-01-mental-model.ko.png)

*Python Package 101 9장 흐름 개요*

## 이 글에서 배우는 내용

- 좋은 README에 꼭 필요한 섹션
- MkDocs로 문서 사이트를 만드는 방법
- docstring에서 API Reference를 자동 생성하는 방법
- GitHub Pages에 문서를 배포하는 방법

## 왜 중요한가

아무리 좋은 패키지라도 사용법이 없으면 실제로는 쓰이지 않습니다. 사용자가 PyPI나 GitHub에서 패키지를 발견했을 때 가장 먼저 묻는 질문은 “내 문제를 이 패키지가 해결하나?”입니다. README는 그 질문에 30초 안에 답해야 합니다.

> 기능은 좋아 보이지만 README에 설치 방법도, 예제도 없는 패키지를 찾았다고 가정해 보겠습니다. 사용법을 알려면 소스 코드를 직접 읽어야 합니다. 대부분의 사용자는 그 시점에서 비슷한 기능을 제공하는 다른 패키지로 이동합니다.

## 멘탈 모델

문서는 세 층으로 나누어 생각하면 편합니다. 1층 README는 “무엇이고 어떻게 시작하는가”를 설명하고, 2층 가이드는 “실제로 어떻게 쓰는가”를 보여 주며, 3층 API Reference는 “각 함수와 클래스가 정확히 무엇을 하는가”를 기록합니다.

```text
README.md          →  30-second decision: install, quick start
docs/guide.md      →  5-minute tutorial: main features
docs/api.md        →  detailed reference: specs for every function/class
```

## 핵심 개념

| 용어 | 설명 | 파일 |
|---|---|---|
| README | 프로젝트 소개, 설치, 빠른 시작 | `README.md` |
| docstring | 함수·클래스에 붙는 문서 문자열 | `"""..."""` |
| MkDocs | Markdown 기반 문서 사이트 생성기 | `mkdocs.yml` |
| mkdocstrings | docstring에서 API 문서를 자동 생성하는 MkDocs 플러그인 | MkDocs plugin |
| GitHub Pages | 무료 정적 사이트 호스팅 | `gh-pages` branch |

## Before / After

**Before (no documentation)**

```text
README.md:
# mylib
A Python library.
```

**After (structured documentation)**

```text
README.md:
# mylib
One-line description.

## Installation
pip install mylib

## Quick Start
from mylib import greet
print(greet("World"))

## Documentation
https://yourname.github.io/mylib/
```

## 단계별 실습

### Step 1. README 작성

````markdown
# mylib

A simple greeting library for Python.

## Installation

```bash
pip install mylib
```

## Quick Start

```python
from mylib.core import greet

print(greet("World"))  # Hello, World!
```

## Features

- Simple and lightweight
- Type-annotated
- CLI support via `greet` command

## Development

```bash
git clone https://github.com/yourname/mylib
cd mylib
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
````

### Step 2. docstring 추가

```python
# src/mylib/core.py
def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.

    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"
```

### Step 3. MkDocs 설정

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]

cat > mkdocs.yml << 'EOF'
site_name: mylib
theme:
  name: material

nav:
  - Home: index.md
  - Guide: guide.md
  - API Reference: api.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
EOF

mkdir docs
echo "# mylib" > docs/index.md
echo "# Guide" > docs/guide.md
```

### Step 4. API Reference 자동 생성

```markdown
<!-- docs/api.md -->
# API Reference

::: mylib.core
    options:
      show_root_heading: true
      show_source: true
```

```bash
mkdocs serve
# INFO - Serving on http://127.0.0.1:8000/
```

### Step 5. GitHub Pages 배포

```bash
mkdocs gh-deploy
# INFO - Deployed to https://yourname.github.io/mylib/
```

## 이 코드에서 눈여겨볼 점

- Google style docstring(`Args:`, `Returns:`)은 Python 생태계에서 가장 널리 쓰이는 형식입니다.
- `mkdocstrings`는 `::: mylib.core` 구문으로 해당 모듈의 docstring을 자동 렌더링합니다.
- `mkdocs serve`는 로컬 미리보기이고, `mkdocs gh-deploy`는 실제 배포입니다.
- `Examples:` 섹션의 `>>>` 예제는 `doctest`로 자동 검증할 수 있습니다.

## 자주 하는 실수

### 실수 1. README에 설치 방법을 빼먹는다

사용자가 가장 먼저 시도하는 것은 설치입니다. `pip install mylib` 같은 최소 설치 방법은 반드시 README에 들어가야 합니다.

### 실수 2. docstring이 코드와 어긋난다

코드는 바뀌었는데 docstring을 갱신하지 않으면 문서가 사실과 달라집니다. 예제가 계속 유효한지 `doctest`로 확인하는 습관이 중요합니다.

### 실수 3. 문서 사이트만 있고 README가 약하다

사용자가 PyPI와 GitHub에서 가장 먼저 보는 것은 README입니다. 문서 사이트 링크를 README에 걸어 두되, README 자체만 읽어도 시작할 수 있어야 합니다.

### 실수 4. API Reference만 있고 가이드가 없다

API Reference는 함수 목록을 알려 주지만, 사용자가 정말 알고 싶은 것은 “어떤 순서로 무엇을 써야 하는가”입니다. 이 간격을 메우는 것이 가이드 문서입니다.

### 실수 5. 문서를 배포하지 않는다

로컬에서 `mkdocs serve`만 해 보고 끝내면 사용자에게는 아무것도 전달되지 않습니다. `mkdocs gh-deploy`나 CI 자동 배포를 반드시 연결하는 편이 좋습니다.

## 실무 적용

- **PyPI README**: `[project.readme]`로 PyPI 페이지에 README를 렌더링합니다.
- **CI 문서 빌드**: 모든 PR에서 문서 빌드를 검증해 깨진 링크를 빨리 찾습니다.
- **버전별 문서**: `mike` 플러그인으로 여러 버전의 문서를 함께 운영할 수 있습니다.
- **Jupyter 연동**: 노트북에서 `?` 또는 `help()`로 docstring을 바로 확인할 수 있습니다.
- **자동 CHANGELOG**: `towncrier`로 PR 단위 변경 사항을 자동 취합할 수 있습니다.

## 실무에서는 이렇게 생각합니다

문서는 코드와 분리된 부속물이 아니라 코드의 일부입니다. PR에서 코드가 바뀌었는데 문서가 그대로라면, 그 자체가 기술 부채로 누적됩니다.

현재 Python 생태계에서는 MkDocs + Material 조합이 사실상 기본 선택지에 가깝습니다. Sphinx는 더 강력하지만 진입 장벽이 높습니다. 새 프로젝트라면 일단 MkDocs로 시작하고, 이후 필요에 따라 확장하는 편이 보통 더 효율적입니다.

## 체크리스트

- [ ] README에 설치, 빠른 시작, 라이선스가 포함되어 있다
- [ ] 모든 public 함수에 docstring이 있다
- [ ] MkDocs로 문서 사이트를 생성할 수 있다
- [ ] `mkdocstrings`로 API Reference를 자동 생성할 수 있다
- [ ] GitHub Pages에 문서를 배포할 수 있다

## 연습 문제

1. 이전 글의 패키지를 기준으로 README.md를 직접 작성해 보세요. 설치, 빠른 시작, 기능, 개발 환경, 라이선스를 포함해야 합니다.
2. 모든 public 함수에 Google style docstring을 추가하고 `python -m doctest`로 예제가 동작하는지 확인해 보세요.
3. MkDocs를 설정하고 `mkdocs serve`로 로컬 미리보기를 확인해 보세요.

## 정리 · 다음 글

- README는 패키지의 현관문이며, 설치·빠른 시작·기능 소개가 핵심입니다.
- docstring은 Google style로 쓰고 `doctest`로 예제를 검증할 수 있습니다.
- MkDocs + `mkdocstrings`로 API Reference를 자동 생성할 수 있습니다.
- `mkdocs gh-deploy`로 GitHub Pages에 문서를 무료로 배포할 수 있습니다.
- 문서는 코드의 일부이므로 코드 변경과 함께 항상 갱신해야 합니다.

다음 글에서는 **실전 패키지 템플릿 만들기** — cookiecutter, copier, GitHub Template을 다룹니다.

## 실전 패턴 추가: pyproject.toml, 빌드 명령, CI까지 한 번에 정리

패키징은 파일 한두 개를 만드는 작업이 아니라, 메타데이터와 빌드 백엔드, 배포 검증을 같은 계약으로 묶는 작업입니다. `pyproject.toml`을 기준으로 로컬 빌드와 CI 검증 경로를 맞추면 릴리스 직전의 불일치를 크게 줄일 수 있습니다.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "acme-utils"
version = "0.1.0"
description = "Utility package for internal services"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "httpx>=0.27,<0.29",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "ruff>=0.5",
  "mypy>=1.10",
  "build>=1.2",
  "twine>=5.1",
]

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m build
python -m twine check dist/*
```

```yaml
name: package-ci
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -U pip
      - run: python -m pip install -e ".[dev]"
      - run: pytest -q
      - run: ruff check .
      - run: mypy src
      - run: python -m build
      - run: python -m twine check dist/*
```

실무에서 중요한 포인트는 로컬과 CI가 같은 명령 세트를 사용하도록 고정하는 것입니다. 개발자가 로컬에서 `python -m build`를 통과시킨 산출물이 CI에서도 같은 방식으로 통과해야 릴리스 리스크가 줄어듭니다. 또한 `twine check`를 CI에 넣어 두면 README 렌더링 오류나 메타데이터 누락을 배포 전에 잡을 수 있습니다.

## 처음 질문으로 돌아가기

- **좋은 README에는 무엇이 들어가야 할까요?**
  - 본문의 기준은 문서화 — README, MkDocs, API Reference를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **MkDocs와 Sphinx는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **docstring에서 API Reference를 자동 생성하려면 어떻게 해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): 버전 관리와 릴리스](./06-versioning-and-releases.md)
- [Python Package 101 (7/10): CLI 패키지 만들기](./07-cli-packages.md)
- [Python Package 101 (8/10): 타입 힌트와 정적 검사](./08-type-hints-and-static-analysis.md)
- **Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (현재 글)**
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [MkDocs documentation](https://www.mkdocs.org/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

Tags: Python, Packaging, PyPI, pyproject.toml
