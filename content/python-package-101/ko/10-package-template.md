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

## 처음 질문으로 돌아가기

- **새 패키지마다 반복되는 설정을 어떻게 자동화할까요?**
  - 본문의 기준은 실전 패키지 템플릿 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`cookiecutter`와 `copier`는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **GitHub Template Repository는 언제 쓰면 좋을까요?**
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
- [Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference](./09-documentation.md)
- **Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [copier documentation](https://copier.readthedocs.io/)
- [cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Hypermodern Python - Claudio Jolowicz](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [GitHub - Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: Python, Packaging, PyPI, pyproject.toml
