
# 문서화 — README, MkDocs, API Reference

> Python Package 101 시리즈 (9/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 좋은 README에는 무엇이 포함되어야 할까요?
- MkDocs와 Sphinx의 차이는 무엇일까요?
- docstring에서 API Reference를 자동 생성하는 법은 무엇일까요?
- GitHub Pages에 문서를 배포하는 법은 무엇일까요?

> README는 패키지의 현관문이고, API Reference는 모든 함수의 사용 설명서입니다. 문서가 없는 패키지는 쓰이지 않습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 좋은 README의 구조와 필수 항목
- MkDocs로 문서 사이트를 만드는 법
- docstring에서 API Reference를 자동 생성하는 법
- GitHub Pages에 문서를 배포하는 법

## 왜 중요한가

아무리 좋은 패키지도 사용법이 없으면 쓰이지 않습니다. PyPI에서 패키지를 발견한 사용자가 30초 안에 "이 패키지가 내 문제를 해결하는가?"를 판단할 수 있어야 합니다. README가 그 역할을 합니다.

> 유용한 패키지를 발견했지만 README에 설치 방법과 예제가 없습니다. 소스 코드를 읽어봐야 사용법을 알 수 있습니다. 결국 비슷한 기능의 다른 패키지를 선택합니다.

## Mental Model

> 문서는 3층 구조입니다. 1층(README)은 "무엇이고 어떻게 시작하는가", 2층(가이드)은 "어떻게 쓰는가", 3층(API Reference)은 "모든 함수의 상세 스펙"입니다. 사용자는 1층에서 시작해서 필요한 만큼 깊이 들어갑니다.

```text
README.md          →  30초 판단: 설치, 빠른 시작
docs/guide.md      →  5분 튜토리얼: 주요 기능 사용법
docs/api.md        →  상세 참조: 모든 함수/클래스의 스펙
```

## 핵심 개념

| 용어 | 설명 | 파일 |
|---|---|---|
| README | 프로젝트 소개, 설치, 빠른 시작 | `README.md` |
| docstring | 함수/클래스에 달린 문서 문자열 | `"""..."""` |
| MkDocs | Markdown 기반 문서 사이트 생성기 | `mkdocs.yml` |
| mkdocstrings | docstring에서 API 문서 자동 생성 | MkDocs 플러그인 |
| GitHub Pages | 무료 정적 사이트 호스팅 | `gh-pages` 브랜치 |

## Before / After

**Before (문서 없음)**

```text
README.md:
# mylib
A Python library.
```

**After (구조화된 문서)**

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

```markdown
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
```

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

## 이 코드에서 봐야 할 것

- Google style docstring(`Args:`, `Returns:`)이 가장 널리 쓰이는 형식입니다
- `mkdocstrings`의 `::: mylib.core`가 해당 모듈의 docstring을 자동으로 렌더링합니다
- `mkdocs serve`로 로컬에서 문서를 미리보고, `mkdocs gh-deploy`로 배포합니다
- `Examples:` 섹션의 `>>>` 코드는 `doctest`로 자동 테스트할 수 있습니다

## 자주 하는 실수

### 실수 1. README에 설치 방법을 빼먹는다

사용자의 첫 행동은 "어떻게 설치하지?"입니다. `pip install mylib`을 반드시 포함하세요.

### 실수 2. docstring이 코드와 다르다

코드를 수정한 후 docstring을 갱신하지 않으면 문서가 거짓말을 합니다. CI에서 `doctest`를 실행하여 예제가 동작하는지 확인하세요.

### 실수 3. 문서 사이트만 있고 README가 없다

PyPI와 GitHub에서 사용자가 가장 먼저 보는 것은 README입니다. 문서 사이트 링크는 README에 넣되, README 자체도 독립적으로 유용해야 합니다.

### 실수 4. API Reference만 있고 가이드가 없다

API Reference는 "모든 함수의 목록"이지만, 사용자가 알고 싶은 것은 "어떤 순서로 어떤 함수를 써야 하는가"입니다. 가이드가 그 역할을 합니다.

### 실수 5. 문서를 배포하지 않는다

로컬에서 `mkdocs serve`만 하고 배포하지 않으면 사용자가 접근할 수 없습니다. `mkdocs gh-deploy`나 CI에서 자동 배포하세요.

## 실무 적용

- **PyPI README**: `[project.readme]`로 PyPI 페이지에 README를 렌더링합니다
- **CI 문서 빌드**: PR마다 문서 빌드를 확인하여 깨진 링크나 렌더링 오류를 방지합니다
- **버전별 문서**: `mike`(MkDocs 플러그인)로 버전별 문서를 호스팅합니다
- **Jupyter 연동**: 노트북에서 `?` 또는 `help()`로 docstring을 바로 확인합니다
- **자동 CHANGELOG**: `towncrier`로 PR 단위 변경 로그를 자동 취합합니다

## 실무에서는 이렇게 생각한다

문서는 코드의 일부입니다. PR에 코드 변경이 있으면 문서 변경도 함께 리뷰합니다. "코드는 바뀌었는데 문서는 그대로"는 기술 부채입니다.

MkDocs + Material 테마가 현재 Python 생태계의 사실상 표준입니다. Sphinx는 더 강력하지만 진입 장벽이 높습니다. 새 프로젝트라면 MkDocs부터 시작하세요.

## 시니어 엔지니어는 이렇게 생각합니다

- **Quickstart 우선** — 첫 5분 경험에 투자합니다.
- **실행 가능한 예제** — 복붙으로 동작하는 예제를 만듭니다.
- **MkDocs/Sphinx** — 도구는 정착된 것으로 통일합니다.
- **API 자동** — docstring → API ref 자동화로 동기화합니다.
- **버저닝** — 문서도 버전과 함께 보존합니다.

## 체크리스트

- [ ] README에 설치 방법, 빠른 시작, 라이선스가 포함되어 있다
- [ ] 모든 public 함수에 docstring이 있다
- [ ] MkDocs로 문서 사이트를 생성할 수 있다
- [ ] mkdocstrings으로 API Reference를 자동 생성할 수 있다
- [ ] GitHub Pages에 문서를 배포할 수 있다

## 연습 문제

1. 이전 글에서 만든 패키지의 README.md를 작성하세요. 설치, 빠른 시작, 기능 목록, 개발 방법, 라이선스를 포함합니다.
2. 모든 public 함수에 Google style docstring을 추가하고, `python -m doctest`로 예제가 동작하는지 확인해보세요.
3. MkDocs를 설정하고 `mkdocs serve`로 로컬에서 문서를 미리보세요.

## 정리 · 다음 글

- README는 패키지의 현관문으로, 설치 · 빠른 시작 · 기능 소개가 필수입니다.
- docstring은 Google style로 작성하고, 예제는 doctest로 검증합니다.
- MkDocs + mkdocstrings로 docstring에서 API Reference를 자동 생성합니다.
- `mkdocs gh-deploy`로 GitHub Pages에 무료로 문서를 호스팅합니다.
- 문서는 코드의 일부이며, PR에 코드 변경이 있으면 문서도 함께 갱신합니다.

다음 글에서는 **실전 패키지 템플릿 만들기** — cookiecutter, copier, GitHub Template을 다룹니다.

## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [버전 관리와 릴리스](./06-versioning-and-releases.md)
- [CLI 패키지 만들기](./07-cli-packages.md)
- [타입 힌트와 정적 검사](./08-type-hints-and-static-analysis.md)
- **문서화 — README, MkDocs, API Reference (현재 글)**
- 실전 패키지 템플릿 만들기 (예정)

## 참고 자료

- [MkDocs documentation](https://www.mkdocs.org/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

Tags: Python, Documentation, MkDocs, README, API Reference, Sphinx

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
