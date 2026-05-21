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

## README 작성 실전 가이드

README는 패키지의 첫인상이자 사용자가 가장 먼저 읽는 문서입니다. PyPI, GitHub, 문서 사이트 모두에서 표시됩니다.

### 필수 섹션 구조

```markdown
# acme-utils

> Production-ready utility library for Acme microservices.

[![PyPI version](https://img.shields.io/pypi/v/acme-utils.svg)](https://pypi.org/project/acme-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/acme-utils.svg)](https://pypi.org/project/acme-utils/)
[![CI](https://github.com/acme/acme-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/acme-utils/actions)

## Installation

```bash
pip install acme-utils
```

## Quick Start

```python
from acme_utils import Engine, Settings

settings = Settings.from_env()
engine = Engine(settings)
result = engine.run("SELECT * FROM users")
```

## Features

- **Type-safe configuration** — Pydantic-based settings with env var support
- **Retry logic** — Configurable retry with exponential backoff
- **Structured logging** — JSON logging for production environments

## Documentation

Full documentation: https://acme.github.io/acme-utils

## Development

```bash
git clone https://github.com/acme/acme-utils.git
cd acme-utils
pip install -e ".[dev]"
pytest
```

## License

MIT License. See [LICENSE](LICENSE) for details.
```

### README 작성 원칙

| 원칙 | 설명 |
|---|---|
| 30초 규칙 | 30초 안에 패키지가 무엇인지 파악 가능해야 함 |
| 복사-붙여넣기 가능한 코드 | Quick Start는 그대로 실행 가능해야 함 |
| 배지 | 빌드 상태, 버전, Python 지원 버전을 한눈에 |
| 링크 | 상세 문서, 변경 로그, 이슈 트래커로 연결 |

## MkDocs로 문서 사이트 구축

MkDocs는 Markdown 기반 정적 문서 사이트 생성기입니다. Material 테마와 함께 사용하면 현대적인 문서를 빠르게 만들 수 있습니다.

### 초기 설정

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs new docs
```

```yaml
# mkdocs.yml
site_name: Acme Utils
site_url: https://acme.github.io/acme-utils
repo_url: https://github.com/acme/acme-utils

theme:
  name: material
  features:
    - content.code.copy
    - navigation.sections
    - navigation.expand
    - search.suggest
  palette:
    - scheme: default
      primary: indigo

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            docstring_style: google

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - User Guide:
    - Configuration: guide/configuration.md
    - Retry Logic: guide/retry.md
  - API Reference:
    - Core: api/core.md
    - Config: api/config.md
  - Changelog: changelog.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - admonitions
  - pymdownx.tabbed:
      alternate_style: true
```

### 디렉터리 구조

```text
docs/
├── index.md                    # 홈페이지
├── getting-started/
│   ├── installation.md
│   └── quickstart.md
├── guide/
│   ├── configuration.md
│   └── retry.md
├── api/
│   ├── core.md                 # API 자동 생성
│   └── config.md
└── changelog.md
```

### API Reference 자동 생성

```markdown
<!-- docs/api/core.md -->
# Core Module

::: acme_utils.core
    options:
      members:
        - Engine
        - Result
      show_source: true
```

mkdocstrings는 소스 코드의 docstring을 읽어 API 문서를 자동 생성합니다.

### 로컬 미리보기

```bash
mkdocs serve
# INFO - Serving on http://127.0.0.1:8000/
# 파일 수정 시 자동 리로드
```

## Docstring 작성 규칙

### Google 스타일 (권장)

```python
def retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    """지수 백오프를 적용하여 함수를 재시도합니다.

    지정된 횟수만큼 함수를 실행하고, 실패할 때마다 대기 시간을
    지수적으로 늘립니다.

    Args:
        func: 실행할 함수. 인자 없이 호출 가능해야 합니다.
        max_attempts: 최대 시도 횟수. 기본값 3.
        delay: 첫 번째 재시도 전 대기 시간(초). 기본값 1.0.
        backoff: 대기 시간 증가 배수. 기본값 2.0.

    Returns:
        함수의 반환값.

    Raises:
        RetryError: 모든 시도가 실패한 경우.

    Example:
        >>> result = retry(lambda: fetch_data(), max_attempts=5)
    """
```

### NumPy 스타일

```python
def calculate_mean(values: list[float]) -> float:
    """
    주어진 값들의 산술 평균을 계산합니다.

    Parameters
    ----------
    values : list[float]
        평균을 계산할 숫자 목록. 비어 있으면 안 됩니다.

    Returns
    -------
    float
        산술 평균값.

    Raises
    ------
    ValueError
        values가 비어 있는 경우.
    """
```

## GitHub Pages 자동 배포

```yaml
# .github/workflows/docs.yml
name: Deploy docs
on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

```bash
# 수동 배포
mkdocs gh-deploy
# GitHub Pages에 자동으로 배포됨
# https://acme.github.io/acme-utils/
```

## Sphinx vs MkDocs 비교

| 항목 | MkDocs | Sphinx |
|---|---|---|
| 문법 | Markdown | reStructuredText (기본) |
| 설정 | YAML | Python (conf.py) |
| 테마 | Material (모던) | Read the Docs (전통적) |
| API 자동 생성 | mkdocstrings | autodoc (내장) |
| 빌드 속도 | 빠름 | 보통 |
| 생태계 | 성장 중 | 매우 넓음 |
| 적합한 경우 | 새 프로젝트, 간결한 문서 | 대규모, 학술, 레거시 |

### Sphinx 최소 설정 (참고용)

```python
# docs/conf.py
project = "acme-utils"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google/NumPy docstring 지원
    "sphinx_rtd_theme",
]
html_theme = "sphinx_rtd_theme"
```

## 문서 품질 관리

### 링크 검증

```bash
# mkdocs-linkcheck 플러그인
pip install mkdocs-linkcheck
# mkdocs.yml에 추가:
# plugins:
#   - linkcheck
```

### 코드 예시 실행 검증

```bash
# pytest의 doctest 기능 활용
pytest --doctest-modules src/acme_utils/

# 또는 mkdocs에서 실행 가능한 코드 블록
# pymdownx.superfences + pytest-examples 조합
```

### 문서 커버리지

```bash
# interrogate: docstring 커버리지 측정
pip install interrogate
interrogate src/acme_utils/ -v
```

```text
Name                              Stmts  Miss  Cover
---------------------------------------------------
src/acme_utils/__init__.py            5     0   100%
src/acme_utils/core.py               45     3    93%
src/acme_utils/config.py             20     5    75%
---------------------------------------------------
TOTAL                                70     8    89%
```

```toml
# pyproject.toml
[tool.interrogate]
ignore-init-method = true
ignore-init-module = true
fail-under = 80
```

## 버전별 문서 관리

```bash
# mike: MkDocs 버전 관리 도구
pip install mike

# 버전별 배포
mike deploy 1.0 latest --push
mike deploy 1.1 latest --push --update-aliases

# 사용자는 버전을 선택하여 문서를 볼 수 있음
# https://acme.github.io/acme-utils/1.0/
# https://acme.github.io/acme-utils/latest/
```

## CHANGELOG 문서화

CHANGELOG는 릴리스 노트이자 사용자와의 계약서입니다.

### Keep a Changelog 형식 실전 예시

```markdown
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- `Engine.stream()` method for large result sets (#45)

### Fixed
- Connection pool exhaustion under high concurrency (#42)

## [1.3.0] - 2024-07-01

### Added
- Retry decorator with configurable backoff strategy
- `Settings.from_toml()` class method

### Changed
- Default timeout increased from 5s to 30s

### Deprecated
- `Engine.execute()` - use `Engine.run()` instead

## [1.2.0] - 2024-05-15

### Added
- Python 3.12 support
- Type stubs for all public APIs

### Removed
- Python 3.9 support (EOL)

[Unreleased]: https://github.com/acme/acme-utils/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/acme/acme-utils/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/acme/acme-utils/releases/tag/v1.2.0
```

### CHANGELOG 자동 생성 도구

```bash
# git-cliff: Conventional Commits에서 CHANGELOG 생성
pip install git-cliff

# cliff.toml 설정
cat > cliff.toml << 'EOF'
[changelog]
header = "# Changelog\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{% endfor %}
{% endfor %}
"""

[git]
conventional_commits = true
commit_parsers = [
    { message = "^feat", group = "Added" },
    { message = "^fix", group = "Fixed" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Changed" },
]
EOF

# 실행
git-cliff --output CHANGELOG.md
```

## 문서 사이트의 검색 최적화

MkDocs Material의 내장 검색은 클라이언트 사이드 인덱싱을 사용합니다.

```yaml
# mkdocs.yml
plugins:
  - search:
      lang: en
      separator: '[\s\-\.]+'
  - tags:
      tags_file: tags.md

# 각 페이지에 메타데이터 추가
# docs/guide/configuration.md 상단:
# ---
# tags:
#   - configuration
#   - settings
#   - environment variables
# ---
```

### SEO를 위한 메타데이터

```yaml
# mkdocs.yml
plugins:
  - social  # Open Graph 이미지 자동 생성
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/acme/acme-utils
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/acme-utils/
```

## 실전 문서 워크플로우

```text
코드 변경
    │
    ▼
docstring 작성/업데이트
    │
    ▼
mkdocs serve로 로컬 확인
    │
    ▼
PR 생성 → 리뷰
    │
    ▼
main 병합 → CI가 자동 배포
    │
    ▼
https://acme.github.io/acme-utils/ 업데이트
```

### 문서 리뷰 체크리스트

```text
□ 새 공개 API에 docstring이 있는가
□ 코드 예시가 실행 가능한가
□ 내부 링크가 깨지지 않았는가
□ 스크린샷/다이어그램이 최신인가
□ CHANGELOG가 업데이트되었는가
```

## Admonitions 활용법

MkDocs Material에서 admonition(경고/정보 박스)을 활용하면 문서의 가독성이 크게 높아집니다.

```markdown
!!! tip "Best Practice"
    설정값은 환경 변수에서 읽되, 기본값을 항상 제공하세요.

!!! warning "Breaking Change"
    v2.0부터 `Engine.execute()`는 제거됩니다. `Engine.run()`을 사용하세요.

!!! example "사용 예시"
    ```python
    from acme_utils import Engine
    engine = Engine.from_env()
    ```

!!! note
    이 기능은 Python 3.11 이상에서만 사용할 수 있습니다.
```

이 문법은 Markdown의 표준이 아니라 MkDocs Material 확장입니다. Sphinx에서는 `.. note::`, `.. warning::` 디렉티브가 같은 역할을 합니다.

문서는 코드와 동일한 수준으로 리뷰하고 테스트해야 합니다. 오래된 문서는 문서가 없는 것보다 해로울 수 있습니다.

## 처음 질문으로 돌아가기

- **좋은 README에는 무엇이 들어가야 할까요?**
  - 30초 안에 패키지의 용도를 파악할 수 있는 한 줄 설명, 복사해서 바로 실행 가능한 설치 명령과 Quick Start 코드, 주요 기능 목록, 상세 문서 링크가 필수입니다. 배지(CI 상태, 버전, Python 지원)로 신뢰도를 보여주고, 개발 참여 방법까지 안내하면 좋습니다.

- **MkDocs와 Sphinx는 무엇이 다를까요?**
  - MkDocs는 Markdown + YAML로 설정이 간단하고 Material 테마로 모던한 문서를 빠르게 만듭니다. Sphinx는 reStructuredText 기반으로 기능이 풍부하지만 설정이 복잡합니다. 새 Python 프로젝트에는 MkDocs + mkdocstrings 조합이 가장 생산적이고, 레거시 대규모 프로젝트에는 Sphinx가 더 적합합니다.

- **API 문서는 어떻게 자동 생성할까요?**
  - mkdocstrings 플러그인이 소스 코드의 docstring을 읽어 API 문서를 자동 생성합니다. Google 스타일 docstring으로 `Args`, `Returns`, `Raises`, `Example`을 작성하면 구조화된 API 문서가 됩니다. CI에서 `mkdocs gh-deploy`로 GitHub Pages에 자동 배포하면 코드 변경 시 문서도 자동으로 업데이트됩니다.

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [MkDocs documentation](https://www.mkdocs.org/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

Tags: Python, Packaging, PyPI, pyproject.toml
