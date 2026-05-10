---
title: 의존성 관리 — venv, pip, uv, requirements
series: python-package-101
episode: 3
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
- venv
- pip
- uv
- Dependencies
- Virtual Environment
last_reviewed: '2026-05-04'
seo_description: 가상환경은 프로젝트마다 독립된 패키지 공간을 만드는 것이고, 의존성 관리는 어떤 패키지의 어떤 버전이 필요한지를 기록하는 것입니다.
---

# 의존성 관리 — venv, pip, uv, requirements

> Python Package 101 시리즈 (3/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 가상환경은 왜 필요하고 어떻게 동작할까요?
- `pip freeze`와 `requirements.txt`의 관계는 무엇일까요?
- `uv`는 `pip`과 무엇이 다를까요?
- pyproject.toml의 `dependencies`와 `requirements.txt`는 어떻게 다를까요?

> 가상환경은 프로젝트마다 독립된 패키지 공간을 만드는 것이고, 의존성 관리는 어떤 패키지의 어떤 버전이 필요한지를 기록하는 것입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `python -m venv`로 가상환경을 만들고 활성화하는 법
- `pip install`과 `pip freeze`로 의존성을 관리하는 법
- `requirements.txt`와 pyproject.toml `dependencies`의 차이
- `uv`로 더 빠르게 가상환경과 패키지를 관리하는 법

## 왜 중요한가

프로젝트 A는 `requests==2.28`을 쓰고, 프로젝트 B는 `requests==2.31`을 씁니다. 가상환경 없이 시스템 Python에 설치하면 버전이 충돌합니다.

> 프로젝트 A에서 `pip install requests==2.28`을 했더니 프로젝트 B가 깨졌습니다. B는 2.31에서 추가된 기능을 쓰고 있었습니다.

가상환경은 프로젝트마다 독립된 `site-packages`를 만들어 이 문제를 해결합니다.

## Mental Model

> 가상환경은 프로젝트마다 전용 냉장고를 쓰는 것입니다. 공용 냉장고(시스템 Python)에 모든 식재료를 넣으면 누군가 실수로 내 재료를 써버립니다. 전용 냉장고에 넣으면 다른 프로젝트에 영향을 주지 않습니다.

```text
시스템 Python               가상환경
─────────────              ─────────
site-packages/             project-a/.venv/site-packages/
  requests 2.28               requests 2.28
  flask 2.3
                           project-b/.venv/site-packages/
                              requests 2.31
                              django 4.2
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| venv | Python 내장 가상환경 모듈 | `python -m venv .venv` |
| site-packages | 패키지가 설치되는 디렉터리 | `.venv/lib/python3.11/site-packages/` |
| pip freeze | 설치된 패키지와 정확한 버전을 출력 | `pip freeze > requirements.txt` |
| requirements.txt | 재현 가능한 설치를 위한 버전 고정 파일 | `requests==2.31.0` |
| uv | Rust로 작성된 고속 패키지 관리자 | `uv pip install requests` |

## Before / After

**Before (시스템 Python 공유)**

```bash
pip install requests==2.28   # 프로젝트 A용
pip install requests==2.31   # 프로젝트 B용 → A가 깨짐
```

**After (가상환경 분리)**

```bash
cd project-a && python -m venv .venv && source .venv/bin/activate
pip install requests==2.28   # project-a 전용

cd project-b && python -m venv .venv && source .venv/bin/activate
pip install requests==2.31   # project-b 전용
```

## 단계별 실습

### Step 1. 가상환경 만들기

```bash
cd ~/practice/mylib-project
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

which python
# /home/user/practice/mylib-project/.venv/bin/python
```

### Step 2. 패키지 설치와 freeze

```bash
pip install requests flask
pip list
# requests  2.31.0
# flask     3.0.0
# ...

pip freeze > requirements.txt
cat requirements.txt
# blinker==1.7.0
# certifi==2024.2.2
# flask==3.0.0
# requests==2.31.0
# ...
```

### Step 3. requirements.txt로 재현

```bash
# 다른 환경에서 동일하게 설치
deactivate
python -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
pip list  # 동일한 패키지, 동일한 버전
```

### Step 4. pyproject.toml의 dependencies

```toml
# pyproject.toml
[project]
name = "mylib"
version = "0.1.0"
dependencies = [
    "requests>=2.28",
    "flask>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```

```bash
pip install -e .            # dependencies 설치
pip install -e ".[dev]"     # dev 의존성까지 설치
```

### Step 5. uv로 빠르게 관리

```bash
pip install uv

uv venv .venv               # 가상환경 생성 (0.1초)
source .venv/bin/activate
uv pip install requests     # 설치 (pip 대비 10-100배 빠름)
uv pip freeze               # freeze
uv pip install -r requirements.txt  # 재현
```

## 이 코드에서 봐야 할 것

- `source .venv/bin/activate`는 `PATH`의 앞에 `.venv/bin`을 추가하여 가상환경의 Python을 우선 사용하게 합니다
- `pip freeze`는 간접 의존성(transitive dependencies)까지 모두 출력합니다
- pyproject.toml의 `dependencies`는 최소 버전(`>=`)을 쓰고, `requirements.txt`는 정확한 버전(`==`)을 씁니다
- `uv`는 pip의 드롭인 대체로, 동일한 명령어 구조에 속도만 다릅니다

## 자주 하는 실수

### 실수 1. 가상환경을 Git에 커밋한다

`.venv/`는 수십 MB이고 OS마다 다릅니다. `.gitignore`에 `.venv/`를 추가하세요.

### 실수 2. pip freeze의 출력을 그대로 dependencies에 넣는다

```toml
# 잘못: pyproject.toml에 정확한 버전을 넣으면 호환성이 떨어짐
dependencies = ["requests==2.31.0", "certifi==2024.2.2"]

# 올바름: 최소 호환 버전 범위
dependencies = ["requests>=2.28"]
```

### 실수 3. 가상환경 활성화를 잊는다

`pip install`이 시스템 Python에 설치됩니다. `which python`으로 경로를 확인하세요.

### 실수 4. requirements.txt를 갱신하지 않는다

패키지를 추가/제거한 후 `pip freeze > requirements.txt`를 잊으면, 다른 환경에서 재현이 안 됩니다.

### 실수 5. dependencies와 requirements.txt의 역할을 혼동한다

`dependencies`는 "이 패키지가 동작하려면 무엇이 필요한가"이고, `requirements.txt`는 "이 환경을 정확히 재현하려면 무엇이 필요한가"입니다.

## 실무 적용

- **CI/CD**: `pip install -r requirements.txt`로 빌드 환경을 재현합니다
- **Docker**: `COPY requirements.txt . && pip install -r requirements.txt`로 캐시 레이어를 활용합니다
- **개발 의존성 분리**: `[project.optional-dependencies]`로 prod/dev 의존성을 분리합니다
- **보안 감사**: `pip audit`으로 설치된 패키지의 취약점을 검사합니다
- **속도 개선**: `uv`로 CI/CD 파이프라인의 설치 시간을 10배 단축합니다

## 실무에서는 이렇게 생각한다

의존성 관리의 핵심은 **재현 가능성**입니다. "내 컴퓨터에서는 되는데"는 대부분 환경 차이에서 옵니다. `requirements.txt`(또는 `uv.lock`)로 정확한 버전을 고정하면 어디서든 같은 결과를 얻습니다.

최근에는 `uv`가 빠르게 표준이 되고 있습니다. `uv`는 가상환경 생성, 패키지 설치, lock 파일 생성을 하나의 도구로 처리하며, pip 대비 10~100배 빠릅니다. 새 프로젝트라면 `uv`를 먼저 고려하세요.

## 시니어 엔지니어는 이렇게 생각합니다

- **Lock 파일** — 재현성은 lock으로만 보장됩니다.
- **uv/pip** — 현대 워크플로는 uv가 효율적입니다.
- **버전 범위** — 의존성 범위는 보수적으로 시작합니다.
- **Security** — 취약점 스캔을 CI에 포함합니다.
- **Editable install** — 개발은 -e로 빠른 피드백을 만듭니다.

## 체크리스트

- [ ] `python -m venv`로 가상환경을 만들고 활성화할 수 있다
- [ ] `pip freeze > requirements.txt`로 환경을 고정할 수 있다
- [ ] pyproject.toml `dependencies`와 `requirements.txt`의 차이를 설명할 수 있다
- [ ] `optional-dependencies`로 dev 의존성을 분리할 수 있다
- [ ] `uv`의 기본 사용법을 알고 있다

## 연습 문제

1. 새 가상환경을 만들고, `httpx`와 `rich`를 설치한 뒤, `requirements.txt`를 생성해보세요.
2. pyproject.toml에 `dependencies`와 `[project.optional-dependencies]` `dev`를 모두 작성하고, `pip install -e ".[dev]"`로 설치해보세요.
3. `uv`를 설치하고, `uv venv` + `uv pip install`을 사용해서 `pip` 대비 속도 차이를 체감해보세요.

## 정리 · 다음 글

- 가상환경은 프로젝트마다 독립된 패키지 공간을 제공합니다.
- `pip freeze`로 정확한 버전을 고정하고, `requirements.txt`로 재현합니다.
- pyproject.toml `dependencies`는 최소 호환 버전, `requirements.txt`는 정확한 버전을 기록합니다.
- `optional-dependencies`로 개발 전용 패키지를 분리합니다.
- `uv`는 pip의 고속 대체제로 빠르게 표준이 되고 있습니다.

다음 글에서는 **패키지 빌드하기** — wheel과 sdist를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- **의존성 관리 — venv, pip, uv, requirements (현재 글)**
- 패키지 빌드하기 — wheel과 sdist (예정)
- PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- 버전 관리와 릴리스 (예정)
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide - Managing Dependencies](https://packaging.python.org/en/latest/tutorials/managing-dependencies/)
- [PEP 405 - Python Virtual Environments](https://peps.python.org/pep-0405/)
- [uv - An extremely fast Python package installer](https://github.com/astral-sh/uv)
- [pip documentation - Requirements Files](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

Tags: Python, venv, pip, uv, Dependencies, Virtual Environment
