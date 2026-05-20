---
title: "Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지"
series: python-package-101
episode: 5
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
- PyPI
- twine
- Publishing
- TestPyPI
- Distribution
last_reviewed: '2026-05-15'
seo_description: PyPI는 Python 패키지의 앱스토어이고, twine은 빌드된 패키지를 PyPI에 업로드하는 도구입니다.
---

# Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지

패키지를 빌드했다면 이제 다른 사람이 실제로 설치할 수 있는 저장소에 올려야 합니다. 이 단계부터는 단순한 로컬 연습을 넘어 배포 안정성, 인증 정보 관리, 버전 고정 같은 운영 감각이 중요해집니다.

이 글은 Python Package 101 시리즈의 5번째 글입니다. 여기서는 TestPyPI와 PyPI의 역할 차이, `twine` 업로드 흐름, 그리고 배포 실패를 피하기 위한 기본 원칙을 정리하겠습니다.

## 먼저 던지는 질문

- PyPI와 TestPyPI는 무엇이 다를까요?
- `twine`은 정확히 어떤 역할을 할까요?
- API 토큰은 어떻게 만들고 관리할까요?

## 큰 그림

![Python Package 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/05/05-01-mental-model.ko.png)

*Python Package 101 5장 흐름 개요*

이 그림에서는 PyPI에 배포하기 — TestPyPI부터 실제 배포까지를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> PyPI에 배포하기 — TestPyPI부터 실제 배포까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배우는 내용

- PyPI/TestPyPI 계정을 만들고 API 토큰을 발급하는 방법
- `twine`으로 패키지를 업로드하는 방법
- TestPyPI에서 먼저 검증한 뒤 PyPI에 배포하는 흐름
- 업로드 실패를 다루는 기본 원칙

## 왜 중요한가

패키지를 만들고 빌드해도, 다른 사람이 `pip install`로 설치할 수 없으면 사실상 배포한 것이 아닙니다. PyPI에 올리면 전 세계 어디서든 설치할 수 있고, 사내 저장소에 올리면 팀 내부 패키지 배포 체계를 만들 수 있습니다.

> 팀에서 공통 유틸리티 라이브러리를 Git URL로 직접 설치한다고 가정해 보겠습니다. `pip install git+https://...`는 브랜치가 바뀌면 동작도 함께 바뀌고, 설치 속도도 느리며, 정확한 버전 고정도 어렵습니다.

PyPI 배포는 이 문제를 버전 중심의 설치 흐름으로 바꿔 줍니다.

## 멘탈 모델

PyPI는 앱스토어이고, `twine`은 앱스토어에 제출하는 업로드 도구입니다. TestPyPI는 스테이징 환경이고, 실제 PyPI는 프로덕션입니다. 따라서 먼저 스테이징에서 검증한 뒤 프로덕션에 올리는 흐름이 자연스럽습니다.

```text
python -m build → dist/*.whl, dist/*.tar.gz
                     ↓
              twine check dist/*       (validate)
                     ↓
          twine upload --repository testpypi dist/*  (staging)
                     ↓
              pip install --index-url https://test.pypi.org/simple/ mylib  (test)
                     ↓
          twine upload dist/*          (production)
```

## 핵심 개념

| 용어 | 설명 | URL |
|---|---|---|
| PyPI | Python Package Index, 공식 패키지 저장소 | pypi.org |
| TestPyPI | PyPI의 테스트 환경 | test.pypi.org |
| twine | 패키지 업로드 도구 | `pip install twine` |
| API token | 비밀번호 대신 사용하는 인증 토큰 | `pypi-` 접두어 |
| Trusted Publisher | GitHub Actions에서 토큰 없이 배포하는 방식 | OIDC 기반 |

## Before / After

**Before (install directly from Git)**

```bash
pip install git+https://github.com/team/mylib.git@main
# → behavior changes when the branch changes
# → slow install (clone + build)
# → hard to pin versions
```

**After (install from PyPI)**

```bash
pip install mylib==0.1.0
# → pinned to a version
# → instant install if wheel exists
# → identical result everywhere
```

## 단계별 실습

### Step 1. TestPyPI 계정과 토큰 만들기

```text
1. Register at https://test.pypi.org/account/register/
2. Generate an API token at https://test.pypi.org/manage/account/
3. Save the token securely (a string starting with pypi-)
```

### Step 2. `twine` 설치와 빌드 검증

```bash
pip install twine
python -m build                 # build from previous post

twine check dist/*
# Checking dist/mylib-0.1.0-py3-none-any.whl: PASSED
# Checking dist/mylib-0.1.0.tar.gz: PASSED
```

### Step 3. TestPyPI에 업로드

```bash
twine upload --repository testpypi dist/*
# Enter your API token: pypi-...

# Uploading mylib-0.1.0-py3-none-any.whl
# Uploading mylib-0.1.0.tar.gz
# View at: https://test.pypi.org/project/mylib/0.1.0/
```

### Step 4. TestPyPI에서 설치 테스트

```bash
python -m venv /tmp/test-pypi
source /tmp/test-pypi/bin/activate

pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    mylib

python -c "from mylib.core import greet; print(greet('PyPI'))"
# Hello, PyPI!
deactivate
```

### Step 5. 실제 PyPI에 배포

```bash
# PyPI account and token are separate (pypi.org)
twine upload dist/*
# Enter your API token: pypi-...

# View at: https://pypi.org/project/mylib/0.1.0/
```

## 이 코드에서 눈여겨볼 점

- `twine check`는 업로드 전에 메타데이터 오류를 먼저 잡아 줍니다.
- TestPyPI에서는 의존성 패키지가 모두 존재하지 않을 수 있으므로 `--extra-index-url`이 필요합니다.
- API 토큰을 사용할 때 사용자명은 `__token__`, 비밀번호는 토큰 문자열입니다.
- 한 번 업로드한 버전은 수정할 수 없으므로, 문제가 있으면 버전을 올려 다시 배포해야 합니다.

## 자주 하는 실수

### 실수 1. 같은 버전을 다시 업로드하려 한다

PyPI는 이미 존재하는 버전을 덮어쓰지 못하게 막습니다. 작은 수정이라도 새 버전으로 다시 배포해야 합니다.

### 실수 2. API 토큰을 코드나 명령 기록에 하드코딩한다

```bash
# Wrong: token ends up in Git history
twine upload --password pypi-abc123 dist/*

# Correct: use environment variables or .pypirc
export TWINE_PASSWORD=pypi-abc123
```

### 실수 3. TestPyPI를 건너뛰고 곧바로 PyPI에 올린다

실수 한 번이 곧바로 공개 배포 사고로 이어질 수 있습니다. TestPyPI에서 설치와 README 렌더링, 의존성 동작을 먼저 확인하는 편이 안전합니다.

### 실수 4. 패키지 이름 선점을 확인하지 않는다

PyPI 이름은 선착순입니다. 이미 등록된 이름은 사용할 수 없으므로 배포 전 `pip index versions mylib`나 pypi.org 검색으로 먼저 확인해야 합니다.

### 실수 5. `dist/`에 오래된 파일이 남아 있는 상태로 업로드한다

```bash
rm -rf dist/
python -m build
twine upload dist/*    # upload only the current version
```

## 실무 적용

- **CI/CD 자동 배포**: GitHub Actions에서 태그 push를 감지해 자동 배포할 수 있습니다.
- **Trusted Publisher**: OIDC 기반으로 API 토큰 없이 배포를 자동화할 수 있습니다.
- **사내 저장소**: Artifactory, Nexus, devpi에 내부 패키지를 배포할 수 있습니다.
- **사전 릴리스**: `0.1.0rc1` 같은 버전으로 베타 테스트를 운영할 수 있습니다.
- **README 렌더링**: PyPI 페이지에 보일 README는 `[project.readme]` 설정으로 제어합니다.

## 실무에서는 이렇게 생각합니다

수동 배포는 실수를 부르기 쉽습니다. 빌드, 검증, 업로드를 CI/CD로 자동화하는 것이 지금은 기본 패턴에 가깝습니다. 특히 GitHub Actions와 Trusted Publisher를 조합하면 토큰 관리 부담까지 크게 줄일 수 있습니다.

패키지 이름도 초기에 신중하게 고르는 편이 좋습니다. 한 번 공개 배포를 시작하면 이름을 바꾸기 어렵기 때문입니다. 직관적이고, 기존 패키지와 충돌하지 않으며, 검색하기 쉬운 이름을 우선적으로 검토해야 합니다.

## 체크리스트

- [ ] TestPyPI 계정을 만들고 API 토큰을 발급할 수 있다
- [ ] `twine check`로 빌드 결과물을 검증할 수 있다
- [ ] TestPyPI에 업로드하고 설치 테스트할 수 있다
- [ ] 실제 PyPI에 배포할 수 있다
- [ ] API 토큰을 환경변수로 안전하게 관리할 수 있다

## 연습 문제

1. TestPyPI 계정을 만들고 이전 글에서 빌드한 패키지를 업로드해 보세요.
2. 새 가상환경에서 TestPyPI로부터 패키지를 설치하고 import가 동작하는지 확인해 보세요.
3. `~/.pypirc`를 작성해 `twine upload --repository testpypi dist/*`가 토큰을 자동으로 사용하도록 구성해 보세요.

## 정리 · 다음 글

- PyPI는 공식 패키지 저장소이고, TestPyPI는 그 테스트 환경입니다.
- `twine check`는 검증하고, `twine upload`는 업로드합니다.
- 실제 PyPI 배포 전에는 반드시 TestPyPI에서 먼저 검증하는 편이 안전합니다.
- 한 번 업로드한 버전은 수정할 수 없으므로 버전을 올려 다시 배포해야 합니다.
- API 토큰은 코드에 넣지 말고 환경변수나 `.pypirc`로 관리해야 합니다.

다음 글에서는 **버전 관리와 릴리스** — SemVer, Git 태그, CHANGELOG를 다룹니다.

## 처음 질문으로 돌아가기

- **PyPI와 TestPyPI는 무엇이 다를까요?**
  - 본문의 기준은 PyPI에 배포하기 — TestPyPI부터 실제 배포까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`twine`은 정확히 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **API 토큰은 어떻게 만들고 관리할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- **Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (현재 글)**
- Python Package 101 (6/10): 버전 관리와 릴리스 (예정)
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide - Uploading](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
- [PyPI - Publishing with Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [twine documentation](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
