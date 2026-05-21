---
title: "Python Package 101 (10/10): 실전 패키지 템플릿 만들기"
series: python-package-101
episode: 10
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
- Template
- cookiecutter
- copier
- GitHub Template
- Best Practices
last_reviewed: '2026-05-15'
seo_description: 패키지 템플릿은 프로젝트를 시작할 때 반복되는 설정 작업을 자동화하는 것이고, cookiecutter와 copier는 그 도구입니다.
---

# Python Package 101 (10/10): 실전 패키지 템플릿 만들기

이 시리즈에서 다룬 구조, 의존성, 빌드, 배포, 타입 힌트, 문서화까지를 매번 처음부터 다시 설정하는 것은 비효율적입니다. 좋은 템플릿 하나는 팀의 베스트 프랙티스를 반복 가능한 기본값으로 바꿔 줍니다.

이 글은 Python Package 101 시리즈의 마지막 글입니다. 여기서는 `cookiecutter`, `copier`, GitHub Template Repository를 활용해 프로덕션 수준 패키지 템플릿을 만드는 방법을 정리하겠습니다.

## 먼저 던지는 질문

- 새 패키지마다 반복되는 설정을 어떻게 자동화할까요?
- `cookiecutter`와 `copier`는 무엇이 다를까요?
- GitHub Template Repository는 언제 쓰면 좋을까요?

## 큰 그림

![Python Package 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/10/10-01-mental-model.ko.png)

*Python Package 101 10장 흐름 개요*

## 이 글에서 배우는 내용

- `cookiecutter`, `copier`로 프로젝트 템플릿을 만드는 방법
- GitHub Template Repository를 활용하는 방법
- 시리즈 전체 내용을 통합한 프로덕션 템플릿 구조
- CI/CD, 문서, 테스트까지 포함한 패키지 기본 골격

## 왜 중요한가

새 패키지를 만들 때마다 `pyproject.toml`, src layout, mypy 설정, CI/CD, README, `.gitignore`를 매번 손으로 쓰는 것은 반복 비용이 큽니다. 잘 만든 템플릿이 있으면 30초 안에 배포 가능한 수준의 프로젝트 골격을 만들고 바로 코드 작성으로 들어갈 수 있습니다.

> 팀에서 새 마이크로서비스를 만들 때마다 기존 저장소에서 설정 파일을 복사한다고 가정해 보겠습니다. 불필요한 코드가 따라오고, `pyproject.toml`의 패키지 이름을 바꾸지 않아 CI가 깨지고, 문서·테스트 설정도 프로젝트마다 조금씩 달라집니다.

템플릿은 이런 수작업 편차를 줄이는 가장 현실적인 수단입니다.

## 멘탈 모델

템플릿은 쿠키 틀과 비슷합니다. 반죽은 프로젝트 이름과 설명 같은 입력값이고, 틀은 프로젝트 구조와 설정입니다. 틀이 잘 설계되어 있으면 매번 같은 품질의 프로젝트가 나옵니다.

```text
cookiecutter/copier + template
        +
  user input (name, description)
        ↓
  complete project structure
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
| GitHub Template | 저장소를 템플릿으로 쓰는 GitHub 기능 | “Use this template” 버튼 |
| Jinja2 | 템플릿 변수 치환 문법 | `{{ project_name }}` |
| .github/workflows | GitHub Actions CI/CD 설정 | `ci.yml`, `publish.yml` |

## Before / After

**Before (manual setup)**

```bash
mkdir myproject && cd myproject
# write pyproject.toml (10 min)
# set up src layout (5 min)
# write .gitignore, README (5 min)
# configure CI/CD (15 min)
# configure mypy, ruff (5 min)
# → 40 minutes before writing the first line of code
```

**After (template)**

```bash
copier copy gh:yourname/python-template myproject
# Project name? myproject
# Description? A useful tool
# → 30 seconds, all config done, start coding immediately
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

### Step 2. `copier` 설정 파일 작성

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

### Step 3. 템플릿 `pyproject.toml`

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

## 이 코드에서 눈여겨볼 점

- `{{ }}` 문법은 Jinja2 템플릿 엔진으로, 사용자 입력을 파일 이름과 내용에 치환합니다.
- `copier`는 `copier update`로 기존 프로젝트에 템플릿 개선 사항을 반영할 수 있어 유지보수성이 높습니다.
- CI 워크플로는 `ruff`, `mypy`, `pytest`를 기본 검증선으로 포함하고 있습니다.
- `[project.scripts]`가 미리 설정되어 있어 CLI 기능도 바로 붙일 수 있습니다.

## 자주 하는 실수

### 실수 1. 템플릿을 만든 뒤 업데이트하지 않는다

Python 생태계는 빠르게 바뀝니다. 의존성 버전, 린트 설정, CI 액션 버전은 정기적으로 갱신해야 템플릿이 살아 있습니다.

### 실수 2. 질문을 너무 많이 만든다

템플릿이 열 개 넘는 질문을 던지기 시작하면 사용자가 피곤해집니다. 핵심 정보만 묻고, 나머지는 합리적인 기본값을 제공하는 편이 좋습니다.

### 실수 3. 생성된 프로젝트가 바로 테스트를 통과하지 않는다

템플릿에서 생성한 프로젝트는 즉시 `pip install -e ".[dev]" && pytest`가 통과해야 합니다. 처음부터 깨지는 템플릿은 곧 버려집니다.

### 실수 4. GitHub Template만 쓰고 변수 치환을 기대한다

GitHub Template Repository는 저장소를 복사할 뿐 파일 내용의 변수까지 바꾸지는 않습니다. 내용 치환이 필요하면 `cookiecutter`나 `copier`가 필요합니다.

### 실수 5. 라이선스를 빼먹는다

라이선스가 없으면 사용 권한이 법적으로 모호해집니다. 최소한 MIT나 Apache 2.0 같은 기본 라이선스를 포함하는 편이 안전합니다.

## 실무 적용

- **사내 템플릿**: 팀의 코딩 규칙, CI/CD, 공통 의존성을 템플릿으로 표준화할 수 있습니다.
- **오픈소스 시작점**: `hypermodern-python`, `scikit-hep` 같은 공개 템플릿을 참고할 수 있습니다.
- **마이크로서비스 템플릿**: FastAPI, Docker, Kubernetes 설정까지 포함한 서비스 템플릿으로 확장할 수 있습니다.
- **`copier update`**: 템플릿 개선 사항을 기존 프로젝트에도 전파할 수 있습니다.
- **템플릿 자체 CI**: 템플릿으로 프로젝트를 실제 생성해 빌드·테스트하는 CI를 붙일 수 있습니다.

## 실무에서는 이렇게 생각합니다

좋은 템플릿은 팀의 베스트 프랙티스를 코드화한 스냅샷입니다. 새 프로젝트마다 “이번에는 어떻게 설정하지?”를 다시 토론하지 않아도 되게 만들어 줍니다.

`cookiecutter`와 `copier` 사이의 선택도 비교적 단순합니다. 한 번 생성하고 끝나는 템플릿이면 `cookiecutter`도 충분하지만, 시간이 지나며 템플릿 개선을 기존 프로젝트에 되돌려 적용하고 싶다면 `copier`가 훨씬 유리합니다. 새 프로젝트 기준으로는 `copier`를 우선 검토할 만합니다.

## 체크리스트

- [ ] `copier` 또는 `cookiecutter`로 프로젝트 템플릿을 만들 수 있다
- [ ] 템플릿에서 생성된 프로젝트가 즉시 테스트를 통과한다
- [ ] CI/CD 워크플로가 템플릿에 포함되어 있다
- [ ] GitHub Template Repository를 언제 써야 하는지 안다
- [ ] `copier update`로 템플릿 변경을 기존 프로젝트에 반영할 수 있다

## 연습 문제

1. 이 시리즈 전체 내용을 포함하는 `copier` 템플릿을 만들어 보세요. src layout, `pyproject.toml`, mypy, CLI entry point, README, CI를 포함해야 합니다.
2. 템플릿으로 새 프로젝트를 생성하고 `pip install -e ".[dev]" && pytest && mypy src/`가 통과하는지 검증해 보세요.
3. GitHub에 Template Repository를 만들고 “Use this template” 버튼으로 새 프로젝트를 생성해 보세요.

## 정리 · 마무리

- 패키지 템플릿은 반복되는 프로젝트 초기 설정을 자동화합니다.
- `copier`는 변수 치환과 업데이트 기능을 지원해 유지보수성이 높습니다.
- 템플릿에서 생성된 프로젝트는 즉시 테스트를 통과해야 합니다.
- CI/CD, 문서, 타입 검사, 린트를 템플릿에 넣어 두면 프로젝트 시작 속도가 빨라집니다.
- 좋은 템플릿은 팀의 베스트 프랙티스를 코드로 고정한 결과물입니다.

이것으로 Python Package 101 시리즈가 끝났습니다. 패키지의 개념부터 구조, 의존성, 빌드, 배포, 버전 관리, CLI, 타입 힌트, 문서화, 템플릿까지 Python 패키징의 전체 흐름을 한 바퀴 돌았습니다. 이제 여러분의 코드를 패키지로 만들고, 다른 사람이 설치해 쓸 수 있는 형태로 자신 있게 공유해 보시기 바랍니다.

## cookiecutter vs copier 상세 비교

### cookiecutter 동작 흐름

```text
cookiecutter gh:acme/template
    │
    ▼
cookiecutter.json 읽기 (변수 정의)
    │
    ▼
사용자에게 변수값 프롬프트
    │
    ▼
Jinja2로 파일명 + 내용 렌더링
    │
    ▼
hooks/post_gen_project.py 실행
    │
    ▼
완성된 프로젝트 디렉터리 출력
```

### copier 동작 흐름

```text
copier copy gh:acme/template ./my-project
    │
    ▼
copier.yml 읽기 (변수 + 타입 + 검증)
    │
    ▼
사용자에게 변수값 프롬프트 (타입 검증 포함)
    │
    ▼
Jinja2로 렌더링 + 조건부 파일 생성
    │
    ▼
.copier-answers.yml 생성 (답변 기록)
    │
    ▼
완성된 프로젝트 출력
```

```yaml
# .copier-answers.yml (자동 생성, 커밋 대상)
_commit: v1.2.0
_src_path: gh:acme/python-package-template
project_name: acme-auth
package_name: acme_auth
python_version: "3.11"
use_cli: true
build_backend: hatchling
```

### copier update: 템플릿 동기화

```bash
# 6개월 후 팀 템플릿에 새 린트 규칙 추가됨
cd acme-auth
copier update

# copier가 수행하는 작업:
# 1. 원본 템플릿의 최신 버전 다운로드
# 2. .copier-answers.yml의 답변으로 새 버전 렌더링
# 3. 현재 프로젝트와 3-way merge
# 4. 충돌 발생 시 사용자에게 해결 요청
```

## GitHub Template Repository

GitHub Template은 가장 단순한 프로젝트 템플릿 방식입니다.

### 설정 방법

```text
1. GitHub 저장소 Settings
2. "Template repository" 체크박스 활성화
3. 사용자: "Use this template" → "Create a new repository"
```

### 한계

| 항목 | cookiecutter/copier | GitHub Template |
|---|---|---|
| 변수 치환 | 자동 | 수동 |
| 조건부 파일 | 지원 | 불가 |
| 템플릿 업데이트 | copier update | 수동 diff |
| 사용 편의성 | CLI 필요 | 웹 버튼 한 번 |
| 적합한 상황 | 팀 표준화 | 간단한 시작점 |

## 실전 템플릿에 포함할 파일 목록

### 최소 구성 (모든 프로젝트)

```text
├── src/{{package_name}}/
│   ├── __init__.py
│   └── py.typed
├── tests/
│   ├── conftest.py
│   └── test_placeholder.py
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── Makefile
```

### 표준 구성 (팀 프로젝트)

```text
위 최소 구성 +
├── .github/
│   ├── workflows/ci.yml
│   ├── workflows/publish.yml
│   └── dependabot.yml
├── .pre-commit-config.yaml
├── .editorconfig
├── CHANGELOG.md
└── docs/
    └── index.md
```

### 풀 구성 (오픈소스)

```text
위 표준 구성 +
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── docs/
│   ├── getting-started/
│   ├── guide/
│   └── api/
└── mkdocs.yml
```

## 템플릿 Makefile 상세

Makefile은 프로젝트의 모든 일상 명령을 표준화합니다. 새 팀원이 합류해도 `make help`만 실행하면 가능한 작업을 한눈에 파악합니다.

```makefile
.DEFAULT_GOAL := help
.PHONY: help install dev test lint format typecheck build check clean publish docs

PACKAGE := acme_utils
SRC := src/$(PACKAGE)

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install in development mode
	python -m pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest --cov=$(PACKAGE) --cov-report=term-missing -q

lint:  ## Run linter
	ruff check $(SRC) tests

format:  ## Format code
	ruff format $(SRC) tests
	ruff check --fix $(SRC) tests

typecheck:  ## Run type checker
	mypy $(SRC)

build:  ## Build packages
	rm -rf dist/
	python -m build

check: build  ## Verify built packages
	twine check dist/*

clean:  ## Clean build artifacts
	rm -rf dist/ build/ src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true

docs:  ## Serve documentation locally
	mkdocs serve

docs-build:  ## Build documentation
	mkdocs build --strict

ci: lint format typecheck test build check  ## Run full CI locally
```

## 템플릿 테스트 자동화

템플릿 자체도 CI로 테스트합니다. 템플릿에서 생성한 프로젝트가 정상 동작하는지 검증합니다.

```yaml
# 템플릿 저장소의 .github/workflows/test-template.yml
name: Test Template
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        build-backend: ["setuptools", "hatchling"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install copier
      - name: Generate project
        run: |
          copier copy --defaults \
            --data "project_name=test-project" \
            --data "build_backend=${{ matrix.build-backend }}" \
            . /tmp/test-project
      - name: Verify project
        working-directory: /tmp/test-project
        run: |
          pip install -e ".[dev]"
          make ci
```

## 팀 온보딩 경험 설계

좋은 템플릿은 새 팀원의 온보딩 시간을 줄여 줍니다.

```text
Day 1 (신규 팀원):
1. copier copy gh:acme/python-package-template ./my-service
2. cd my-service
3. make install
4. make test    (녹색 통과!)
5. make ci      (전체 파이프라인 로컬 검증!)

→ 30분 안에 첫 PR을 올릴 수 있는 환경이 준비됩니다.
```

이것이 템플릿의 가치입니다. 프로젝트 시작의 마찰을 줄이고, 팀 표준을 코드화하며, "이 프로젝트는 어떻게 빌드하지?"라는 질문을 없애는 것입니다.

## 템플릿 버전 관리 전략

템플릿도 SemVer로 버전을 관리하면 `copier update`시 어떤 변경이 반영되는지 추적할 수 있습니다.

```text
v1.0.0: 초기 템플릿 (setuptools)
v1.1.0: hatchling 옵션 추가
v1.2.0: Python 3.12 지원, ruff 설정 업데이트
v2.0.0: src layout 강제 (breaking: flat layout 제거)
```

```bash
# 특정 버전으로 생성
copier copy --vcs-ref v1.2.0 gh:acme/template ./project

# 업데이트 시 버전 범위 확인
copier update  # .copier-answers.yml의 _commit과 최신 비교
```

### 템플릿 변경 로그 관리

```markdown
# Template CHANGELOG

## [1.2.0] - 2024-07-01

### Added
- Python 3.12 support in CI matrix
- Ruff 0.5+ configuration
- `make docs` command

### Changed
- Default ruff rules expanded (added SIM, TCH)
- pytest minimum version: 8.0

### Migration
After `copier update`:
- Review new ruff rules in pyproject.toml
- Update CI Python version matrix if needed
```

## 사내 패키지 생태계 관리

대규모 조직에서는 여러 템플릿을 계층적으로 관리합니다.

```text
조직 레벨:
├── base-template/          # 공통 (LICENSE, .editorconfig, CI 기본)
├── library-template/       # 라이브러리용 (src layout, PyPI 배포)
├── service-template/       # 마이크로서비스용 (Docker, K8s)
├── cli-template/           # CLI 도구용 (Click, entry points)
└── ml-template/            # ML 프로젝트용 (notebooks, DVC)
```

### 표준화 검증 도구

```bash
# 생성된 프로젝트가 팀 표준을 따르는지 검증하는 스크립트
#!/bin/bash
# scripts/check-standards.sh

echo "Checking project standards..."

# pyproject.toml 존재
[ -f pyproject.toml ] || { echo "FAIL: pyproject.toml missing"; exit 1; }

# src layout 사용
[ -d src ] || { echo "FAIL: src/ directory missing"; exit 1; }

# py.typed 존재
find src -name "py.typed" | grep -q . || { echo "FAIL: py.typed missing"; exit 1; }

# CI 워크플로우 존재
[ -f .github/workflows/ci.yml ] || { echo "FAIL: CI workflow missing"; exit 1; }

# pre-commit 설정
[ -f .pre-commit-config.yaml ] || { echo "FAIL: pre-commit config missing"; exit 1; }

echo "All standards met!"
```

이 스크립트를 CI의 첫 번째 단계로 넣어 두면, 누군가 표준을 벗어나는 변경을 하더라도 PR에서 즉시 발견됩니다.

실무에서 템플릿은 한 번 만들고 잊는 것이 아닙니다. 분기별로 의존성 버전, 린트 규칙, CI 설정을 업데이트하고, `copier update`로 모든 프로젝트에 일괄 반영하는 루틴을 만들어야 합니다. 이 루틴이 정착되면 20개 이상의 마이크로서비스가 있어도 설정 드리프트 없이 일관된 품질을 유지할 수 있습니다.

결국 좋은 템플릿은 "새 프로젝트를 시작하는 데 가장 좋은 방법은 무엇인가?"라는 팀의 합의를 코드로 표현한 것입니다.

## 처음 질문으로 돌아가기

- **새 패키지마다 반복되는 설정을 어떻게 자동화할까요?**
  - cookiecutter나 copier로 프로젝트 템플릿을 만들고, `pyproject.toml`, CI 워크플로우, Makefile, pre-commit 설정, 테스트 보일러플레이트를 변수화합니다. `copier copy` 한 번으로 팀 표준에 맞는 프로젝트가 즉시 생성되고, `make ci`로 바로 검증할 수 있는 상태가 됩니다.
- **`cookiecutter`와 `copier`는 무엇이 다를까요?**
  - cookiecutter는 생성 후 템플릿과의 연결이 끊기지만, copier는 `copier update`로 템플릿 개선사항을 기존 프로젝트에 3-way merge할 수 있습니다. 팀 템플릿이 자주 개선된다면 copier가 유지보수 비용을 크게 줄여 줍니다.
- **GitHub Template Repository는 언제 쓰면 좋을까요?**
  - GitHub Template은 "Use this template" 버튼으로 저장소를 복제합니다. 변수 치환이 없으므로 프로젝트명 등을 수동으로 바꿔야 합니다. 간단한 구조의 프로젝트나 외부 도구 설치가 어려운 환경에서 빠르게 시작할 때 적합합니다.

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
- [Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference](./09-documentation.md)
- **Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [copier documentation](https://copier.readthedocs.io/)
- [cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Hypermodern Python - Claudio Jolowicz](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [GitHub - Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: Python, Packaging, PyPI, pyproject.toml
