---
title: 실전 패키지 템플릿 만들기
series: python-package-101
episode: 10
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
- Template
- cookiecutter
- copier
- GitHub Template
- Best Practices
last_reviewed: '2026-05-04'
seo_description: 패키지 템플릿은 프로젝트를 시작할 때 반복되는 설정 작업을 자동화하는 것이고, cookiecutter와 copier는 그 도구입니다.
---

# 실전 패키지 템플릿 만들기

> Python Package 101 시리즈 (10/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 패키지를 만들 때마다 반복되는 설정을 어떻게 자동화할까요?
- cookiecutter와 copier의 차이는 무엇일까요?
- GitHub Template Repository는 어떤 경우에 쓸까요?
- 이 시리즈에서 배운 모든 요소를 하나의 템플릿에 어떻게 통합할까요?

> 패키지 템플릿은 프로젝트를 시작할 때 반복되는 설정 작업을 자동화하는 것이고, cookiecutter와 copier는 그 도구입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- cookiecutter와 copier로 프로젝트 템플릿을 만드는 법
- GitHub Template Repository 활용법
- 이 시리즈의 모든 요소를 통합한 프로덕션 템플릿 구조
- CI/CD, 문서, 테스트를 포함한 완성된 패키지 설정

## 왜 중요한가

새 패키지를 만들 때마다 pyproject.toml, src layout, mypy 설정, CI/CD, README, .gitignore를 처음부터 작성하는 것은 비효율적입니다. 한 번 잘 만든 템플릿이 있으면 30초 만에 프로덕션 수준의 프로젝트를 시작할 수 있습니다.

> 새 마이크로서비스를 만들 때마다 기존 프로젝트에서 설정 파일을 복사합니다. 불필요한 코드가 섞이고, pyproject.toml의 패키지 이름을 빼먹어 CI가 실패합니다.

## Mental Model

> 템플릿은 쿠키 틀입니다. 반죽(프로젝트 이름, 설명 등)만 넣으면 같은 모양의 쿠키(프로젝트 구조)가 나옵니다. 틀을 잘 만들면 매번 일정한 품질의 프로젝트가 생성됩니다.

```text
cookiecutter/copier + 템플릿
        +
  사용자 입력 (이름, 설명)
        ↓
  완성된 프로젝트 구조
    src/mylib/
    tests/
    pyproject.toml
    .github/workflows/
    README.md
    ...
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| cookiecutter | Jinja2 기반 프로젝트 템플릿 도구 | `cookiecutter gh:user/template` |
| copier | 업데이트 가능한 프로젝트 템플릿 도구 | `copier copy gh:user/template .` |
| GitHub Template | 저장소를 템플릿으로 사용하는 GitHub 기능 | "Use this template" 버튼 |
| Jinja2 | 템플릿 내 변수 치환 문법 | `{{ project_name }}` |
| .github/workflows | GitHub Actions CI/CD 설정 | `ci.yml`, `publish.yml` |

## Before / After

**Before (수동 설정)**

```bash
mkdir myproject && cd myproject
# pyproject.toml 작성 (10분)
# src layout 설정 (5분)
# .gitignore, README 작성 (5분)
# CI/CD 설정 (15분)
# mypy, ruff 설정 (5분)
# → 40분 후 첫 코드 작성 시작
```

**After (템플릿)**

```bash
copier copy gh:yourname/python-template myproject
# 프로젝트 이름? myproject
# 설명? A useful tool
# → 30초 후 모든 설정 완료, 바로 코드 작성 시작
```

## 단계별 실습

### Step 1. 프로덕션 템플릿 구조 설계

```text
python-template/
├── {{ project_slug }}/
│   ├── src/
│   │   └── {{ project_slug }}/
│   │       ├── __init__.py
│   │       ├── core.py
│   │       ├── cli.py
│   │       └── py.typed
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_core.py
│   ├── docs/
│   │   ├── index.md
│   │   └── api.md
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── publish.yml
│   ├── pyproject.toml
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── LICENSE
│   ├── .gitignore
│   └── mkdocs.yml
└── copier.yml
```

### Step 2. copier 설정 파일 작성

```yaml
# copier.yml
_subdirectory: "{{ project_slug }}"

project_name:
  type: str
  help: "Project name (e.g., My Library)"

project_slug:
  type: str
  default: "{{ project_name | lower | replace(' ', '-') }}"
  help: "Package directory name"

module_name:
  type: str
  default: "{{ project_slug | replace('-', '_') }}"
  help: "Python module name"

description:
  type: str
  default: "A Python package"

author_name:
  type: str
  help: "Author full name"

author_email:
  type: str
  help: "Author email"

python_version:
  type: str
  default: "3.11"
  choices: ["3.9", "3.10", "3.11", "3.12"]
```

### Step 3. 템플릿 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ project_slug }}"
version = "0.1.0"
description = "{{ description }}"
requires-python = ">={{ python_version }}"
license = {text = "MIT"}
authors = [
    {name = "{{ author_name }}", email = "{{ author_email }}"},
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1",
]

[project.scripts]
{{ project_slug }} = "{{ module_name }}.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.mypy]
python_version = "{{ python_version }}"
strict = true

[tool.ruff]
target-version = "py{{ python_version | replace('.', '') }}"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

### Step 4. CI/CD 워크플로 템플릿

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["{{ python_version }}"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ "{{" }} matrix.python-version {{ "}}" }}
      - run: pip install -e ".[dev]"
      - run: ruff check src/
      - run: mypy src/
      - run: pytest tests/
```

### Step 5. 템플릿으로 프로젝트 생성

```bash
pip install copier
copier copy ./python-template my-new-project

# ? project_name: My New Project
# ? project_slug: my-new-project
# ? module_name: my_new_project
# ? description: A useful Python tool
# ? author_name: Your Name
# ? author_email: you@example.com
# ? python_version: 3.11

cd my-new-project
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/    # 1 passed
mypy src/        # Success
```

## 이 코드에서 봐야 할 것

- copier의 `{{ }}` 문법은 Jinja2 템플릿 엔진으로, 사용자 입력을 파일 내용과 이름에 치환합니다
- copier는 `copier update`로 템플릿 업데이트를 기존 프로젝트에 반영할 수 있어 cookiecutter보다 유지보수에 유리합니다
- CI 워크플로에서 `ruff check`, `mypy`, `pytest`를 순서대로 실행하여 코드 품질을 보장합니다
- `[project.scripts]`가 이미 설정되어 있어 CLI를 바로 구현할 수 있습니다

## 자주 하는 실수

### 실수 1. 템플릿을 만들고 업데이트하지 않는다

Python 생태계는 빠르게 변합니다. 템플릿의 의존성 버전과 설정을 정기적으로 갱신하세요.

### 실수 2. 너무 많은 옵션을 넣는다

템플릿에 10개 이상의 질문이 있으면 사용자가 지칩니다. 핵심 옵션만 남기고 나머지는 기본값으로 설정하세요.

### 실수 3. 생성된 프로젝트가 바로 테스트를 통과하지 않는다

템플릿에서 생성된 프로젝트는 `pip install -e ".[dev]" && pytest`가 바로 통과해야 합니다. 깨진 템플릿은 신뢰를 잃습니다.

### 실수 4. GitHub Template만 쓰고 변수 치환을 안 한다

GitHub Template은 저장소를 복사하지만 파일 내용의 변수를 바꾸지 않습니다. `my-template`이라는 이름이 그대로 남습니다.

### 실수 5. 라이선스를 빼먹는다

라이선스가 없으면 법적으로 사용 권한이 불명확합니다. MIT 또는 Apache 2.0을 기본으로 포함하세요.

## 실무 적용

- **사내 템플릿**: 팀의 코딩 규칙, CI/CD 설정, 공통 의존성을 템플릿으로 표준화합니다
- **오픈소스 시작**: hypermodern-python, scikit-hep 등의 공개 템플릿을 참고합니다
- **마이크로서비스**: FastAPI + Docker + Kubernetes 설정을 포함한 서비스 템플릿을 만듭니다
- **copier update**: 템플릿을 개선하면 기존 프로젝트에 `copier update`로 반영합니다
- **CI에서 템플릿 테스트**: 템플릿 자체를 CI에서 생성 + 빌드 + 테스트하여 항상 동작을 보장합니다

## 실무에서는 이렇게 생각한다

좋은 템플릿은 "베스트 프랙티스의 스냅샷"입니다. 팀에서 합의한 코딩 규칙, CI/CD 패턴, 문서 구조를 템플릿에 녹이면, 새 프로젝트마다 "이번에는 어떻게 설정하지?"를 고민할 필요가 없습니다.

cookiecutter vs copier의 선택은 단순합니다: 템플릿을 한번 쓰고 끝이면 cookiecutter, 템플릿 업데이트를 기존 프로젝트에도 반영하고 싶으면 copier입니다. 새 프로젝트라면 copier를 추천합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Cookiecutter** — 표준 템플릿으로 시작 비용을 줄입니다.
- **CI 포함** — 테스트·빌드·배포 워크플로를 기본 포함합니다.
- **Lint/Format** — ruff·black을 기본으로 둡니다.
- **Pre-commit** — 로컬 게이트를 자동화합니다.
- **최소 의존** — 초기 의존성은 최소로 유지합니다.

## 체크리스트

- [ ] copier 또는 cookiecutter로 프로젝트 템플릿을 만들 수 있다
- [ ] 템플릿에서 생성된 프로젝트가 바로 테스트를 통과한다
- [ ] CI/CD 워크플로가 템플릿에 포함되어 있다
- [ ] GitHub Template Repository의 활용 시점을 알고 있다
- [ ] copier update로 기존 프로젝트에 템플릿 변경을 반영할 수 있다

## 연습 문제

1. copier로 이 시리즈에서 배운 모든 요소(src layout, pyproject.toml, mypy, CLI entry point, README, CI)를 포함한 템플릿을 만들어보세요.
2. 만든 템플릿으로 새 프로젝트를 생성하고, `pip install -e ".[dev]" && pytest && mypy src/`가 통과하는지 확인해보세요.
3. GitHub에 템플릿 저장소를 만들고, "Use this template" 버튼으로 새 프로젝트를 생성해보세요.

## 정리 · 다음 글

- 패키지 템플릿은 반복되는 프로젝트 설정을 자동화합니다.
- copier는 변수 치환 + 업데이트 기능으로 cookiecutter보다 유지보수에 유리합니다.
- 템플릿에서 생성된 프로젝트는 바로 테스트가 통과해야 합니다.
- CI/CD, 문서, 타입 검사, 린터를 템플릿에 포함하면 프로젝트 시작이 빨라집니다.
- 좋은 템플릿은 팀의 베스트 프랙티스를 코드화한 것입니다.

이것으로 Python Package 101 시리즈가 끝났습니다. 패키지의 개념부터 구조, 빌드, 배포, 버전 관리, CLI, 타입 힌트, 문서화, 템플릿까지 — Python 패키징의 전체 흐름을 다루었습니다. 이제 여러분의 코드를 패키지로 만들어 공유해보세요.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [버전 관리와 릴리스](./06-versioning-and-releases.md)
- [CLI 패키지 만들기](./07-cli-packages.md)
- [타입 힌트와 정적 검사](./08-type-hints-and-static-analysis.md)
- [문서화 — README, MkDocs, API Reference](./09-documentation.md)
- **실전 패키지 템플릿 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [copier documentation](https://copier.readthedocs.io/)
- [cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Hypermodern Python - Claudio Jolowicz](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [GitHub - Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: Python, Template, cookiecutter, copier, GitHub Template, Best Practices
