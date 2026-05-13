---
title: 의존성 관리 — venv, pip, uv, requirements
series: python-package-101
episode: 3
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: 가상환경은 프로젝트마다 독립된 패키지 공간을 만드는 것이고, 의존성 관리는 어떤 패키지의 어떤 버전이 필요한지를 기록하는 것입니다.
---

# 의존성 관리 — venv, pip, uv, requirements

패키지를 만들었다면 이제 그 패키지가 어떤 환경에서 어떤 버전의 라이브러리와 함께 동작하는지 관리해야 합니다. 같은 코드라도 설치된 패키지 버전이 다르면 전혀 다른 결과가 나올 수 있기 때문입니다. 이 글은 Python Package 101 시리즈의 3번째 글입니다. 여기서는 가상환경이 왜 필요한지, `requirements.txt`와 `pyproject.toml`의 역할이 어떻게 다른지, 그리고 `uv`가 왜 빠르게 표준 도구가 되고 있는지 정리하겠습니다.

## 이 글에서 다룰 문제

- 왜 가상환경이 필요하고 어떻게 동작할까요?
- `pip freeze`와 `requirements.txt`는 어떤 관계일까요?
- `uv`는 `pip`와 무엇이 다를까요?
- `pyproject.toml`의 `dependencies`와 `requirements.txt`는 어떻게 다를까요?

## 이 글에서 배우는 내용

- `python -m venv`로 가상환경을 만들고 활성화하는 방법
- `pip install`, `pip freeze`로 의존성을 관리하는 방법
- `requirements.txt`와 `pyproject.toml` `dependencies`의 차이
- `uv`로 더 빠르게 환경과 패키지를 관리하는 방법

## 왜 중요한가

프로젝트 A는 `requests==2.28`을 쓰고, 프로젝트 B는 `requests==2.31`을 쓸 수 있습니다. 두 프로젝트가 시스템 Python 하나를 공유하면, 한쪽을 위해 설치한 버전이 다른 쪽을 깨뜨릴 수 있습니다. 의존성 관리는 결국 이런 충돌을 피하면서 재현 가능한 환경을 만드는 일입니다.

> 프로젝트 A에서 `pip install requests==2.28`을 실행했더니 프로젝트 B가 갑자기 깨졌다고 가정해 보겠습니다. B는 2.31에서 추가된 기능을 사용하고 있었기 때문입니다.

가상환경은 프로젝트마다 독립된 `site-packages`를 만들어 이 문제를 구조적으로 해결합니다.

## 멘탈 모델

가상환경은 프로젝트마다 전용 냉장고를 하나씩 두는 것과 비슷합니다. 모두가 시스템 Python 하나를 공유하면 누군가가 내 재료를 바꾸거나 치워 버릴 수 있습니다. 프로젝트마다 냉장고를 분리하면 서로 영향을 주지 않습니다.

```text
System Python               Virtual Environment
─────────────              ─────────────────────
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
| uv | Rust로 만든 고속 패키지 관리자 | `uv pip install requests` |

## Before / After

**Before (shared system Python)**

```bash
pip install requests==2.28   # for Project A
pip install requests==2.31   # for Project B → A breaks
```

**After (isolated virtual environments)**

```bash
cd project-a && python -m venv .venv && source .venv/bin/activate
pip install requests==2.28   # project-a only

cd project-b && python -m venv .venv && source .venv/bin/activate
pip install requests==2.31   # project-b only
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

### Step 3. `requirements.txt`로 재현하기

```bash
# Install the same packages in another environment
deactivate
python -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
pip list  # same packages, same versions
```

### Step 4. `pyproject.toml`의 `dependencies`

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
pip install -e .            # install dependencies
pip install -e ".[dev]"     # install dev dependencies too
```

### Step 5. `uv`로 더 빠르게 관리하기

```bash
pip install uv

uv venv .venv               # create venv (0.1 seconds)
source .venv/bin/activate
uv pip install requests     # install (10-100x faster than pip)
uv pip freeze               # freeze
uv pip install -r requirements.txt  # reproduce
```

## 이 코드에서 눈여겨볼 점

- `source .venv/bin/activate`는 `.venv/bin`을 `PATH` 앞쪽에 두어 가상환경 Python이 우선 선택되게 합니다.
- `pip freeze`는 직접 설치한 패키지뿐 아니라 간접 의존성까지 함께 출력합니다.
- `pyproject.toml`의 `dependencies`는 보통 최소 호환 버전(`>=`)을 적고, `requirements.txt`는 정확한 버전(`==`)을 고정합니다.
- `uv`는 pip와 유사한 명령 구조를 유지하면서 속도를 크게 개선한 도구입니다.

## 자주 하는 실수

### 실수 1. 가상환경 디렉터리를 Git에 커밋한다

`.venv/`는 용량이 크고 운영체제별 차이가 큽니다. `.gitignore`에 반드시 추가해야 합니다.

### 실수 2. `pip freeze` 결과를 그대로 `dependencies`에 복사한다

```toml
# Wrong: exact versions in pyproject.toml reduce compatibility
dependencies = ["requests==2.31.0", "certifi==2024.2.2"]

# Correct: minimum compatible version ranges
dependencies = ["requests>=2.28"]
```

### 실수 3. 가상환경 활성화를 잊는다

이 경우 `pip install`이 시스템 Python에 설치됩니다. `which python` 또는 `python -c "import sys; print(sys.executable)"`로 현재 경로를 확인하는 습관이 중요합니다.

### 실수 4. `requirements.txt`를 갱신하지 않는다

패키지를 추가하거나 제거한 뒤 `pip freeze > requirements.txt`를 빼먹으면, 다른 개발자나 CI 환경이 같은 환경을 재현할 수 없습니다.

### 실수 5. `dependencies`와 `requirements.txt`의 목적을 혼동한다

`dependencies`는 “이 패키지가 동작하려면 무엇이 필요한가”를 설명하고, `requirements.txt`는 “이 환경을 정확히 재현하려면 무엇이 필요한가”를 기록합니다. 둘은 서로 대체재가 아닙니다.

## 실무 적용

- **CI/CD**: `pip install -r requirements.txt`로 빌드 환경을 재현합니다.
- **Docker**: `COPY requirements.txt . && pip install -r requirements.txt`로 레이어 캐시를 활용합니다.
- **개발 의존성 분리**: `[project.optional-dependencies]`로 prod/dev 의존성을 나눕니다.
- **보안 점검**: `pip audit`으로 설치된 패키지의 취약점을 검사할 수 있습니다.
- **속도 개선**: `uv`로 CI/CD 설치 시간을 크게 줄일 수 있습니다.

## 실무에서는 이렇게 생각합니다

의존성 관리의 핵심은 결국 **재현 가능성**입니다. “내 컴퓨터에서는 되는데요”라는 말은 거의 항상 환경 차이에서 시작합니다. `requirements.txt`나 `uv.lock`으로 정확한 버전을 고정해야 어디서든 같은 결과를 재현할 수 있습니다.

최근에는 `uv`가 빠르게 표준 도구로 자리 잡고 있습니다. 가상환경 생성, 패키지 설치, lock 파일 관리까지 한 도구에서 처리하고 실행 속도도 빠르기 때문입니다. 새 프로젝트라면 초반부터 `uv`를 적극적으로 고려할 만합니다.

## 체크리스트

- [ ] `python -m venv`로 가상환경을 만들고 활성화할 수 있다
- [ ] `pip freeze > requirements.txt`로 환경을 고정할 수 있다
- [ ] `pyproject.toml` `dependencies`와 `requirements.txt`의 차이를 설명할 수 있다
- [ ] `optional-dependencies`로 dev 의존성을 분리할 수 있다
- [ ] `uv`의 기본 사용법을 이해한다

## 연습 문제

1. 새 가상환경을 만들고 `httpx`, `rich`를 설치한 뒤 `requirements.txt`를 생성해 보세요.
2. `pyproject.toml`에 `dependencies`와 `[project.optional-dependencies]` `dev`를 모두 작성하고, `pip install -e ".[dev]"`로 설치해 보세요.
3. `uv`를 설치하고 `uv venv`, `uv pip install`을 사용해 `pip`와 체감 속도를 비교해 보세요.

## 정리 · 다음 글

- 가상환경은 프로젝트마다 독립된 패키지 공간을 제공합니다.
- `pip freeze`는 정확한 버전을 고정하고, `requirements.txt`는 그 환경을 재현합니다.
- `pyproject.toml` `dependencies`는 최소 호환 버전을, `requirements.txt`는 정확한 버전을 기록합니다.
- `optional-dependencies`로 개발 전용 패키지를 분리할 수 있습니다.
- `uv`는 빠르게 표준이 되어 가는 고속 pip 대체 도구입니다.

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
