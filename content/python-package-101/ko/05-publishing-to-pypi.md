---
title: PyPI에 배포하기 — TestPyPI부터 실제 배포까지
series: python-package-101
episode: 5
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
- PyPI
- twine
- Publishing
- TestPyPI
- Distribution
last_reviewed: '2026-05-04'
seo_description: PyPI는 Python 패키지의 앱스토어이고, twine은 빌드된 패키지를 PyPI에 업로드하는 도구입니다.
---

# PyPI에 배포하기 — TestPyPI부터 실제 배포까지

> Python Package 101 시리즈 (5/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- PyPI와 TestPyPI는 무엇이 다를까요?
- `twine`은 어떤 역할을 할까요?
- API 토큰은 어떻게 발급하고 관리할까요?
- 한 번 업로드한 버전을 수정할 수 있을까요?

> PyPI는 Python 패키지의 앱스토어이고, twine은 빌드된 패키지를 PyPI에 업로드하는 도구입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- PyPI와 TestPyPI 계정 생성 및 API 토큰 발급
- `twine`으로 패키지를 업로드하는 법
- TestPyPI에서 테스트 배포 후 실제 PyPI에 배포하는 흐름
- 업로드 실패 시 대처법

## 왜 중요한가

패키지를 만들고 빌드했으면 배포해야 다른 사람이 `pip install`로 설치할 수 있습니다. PyPI에 올리면 전 세계 누구나 설치할 수 있고, 사내 저장소에 올리면 팀 내에서 공유됩니다.

> 팀에서 공통 유틸리티 라이브러리를 Git에서 직접 설치합니다: `pip install git+https://...`. 브랜치가 바뀌면 동작이 달라지고, 설치 시간도 깁니다.

PyPI에 배포하면 버전으로 고정되어 안정적입니다.

## Mental Model

> PyPI는 앱스토어이고, twine은 앱을 제출하는 도구입니다. TestPyPI는 스테이징 환경이고, PyPI가 프로덕션입니다. 스테이징에서 먼저 테스트하고 프로덕션에 배포합니다.

```text
python -m build → dist/*.whl, dist/*.tar.gz
                     ↓
              twine check dist/*       (유효성 검사)
                     ↓
          twine upload --repository testpypi dist/*  (스테이징)
                     ↓
              pip install --index-url https://test.pypi.org/simple/ mylib  (테스트)
                     ↓
          twine upload dist/*          (프로덕션)
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

**Before (Git에서 직접 설치)**

```bash
pip install git+https://github.com/team/mylib.git@main
# → 브랜치가 바뀌면 동작 변경
# → 설치 시간이 김 (clone + build)
# → 버전 고정이 어려움
```

**After (PyPI에서 설치)**

```bash
pip install mylib==0.1.0
# → 버전으로 고정
# → wheel이 있으면 즉시 설치
# → 어디서든 동일한 결과
```

## 단계별 실습

### Step 1. TestPyPI 계정과 토큰 발급

```text
1. https://test.pypi.org/account/register/ 에서 계정 생성
2. https://test.pypi.org/manage/account/ 에서 API token 생성
3. 토큰을 안전한 곳에 저장 (pypi-으로 시작하는 문자열)
```

### Step 2. twine 설치와 빌드 검증

```bash
pip install twine
python -m build                 # 이전 글에서 빌드

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
# PyPI 계정과 토큰은 별도 발급 (pypi.org)
twine upload dist/*
# Enter your API token: pypi-...

# View at: https://pypi.org/project/mylib/0.1.0/
```

## 이 코드에서 봐야 할 것

- `twine check`는 메타데이터 오류를 사전에 잡아줍니다
- TestPyPI에서 `--extra-index-url`을 추가하는 이유는 의존성 패키지가 TestPyPI에 없을 수 있기 때문입니다
- API 토큰은 `__token__`을 사용자명으로, 토큰 문자열을 비밀번호로 입력합니다
- 한 번 업로드한 버전은 수정할 수 없습니다. 버전을 올려서 다시 배포해야 합니다

## 자주 하는 실수

### 실수 1. 같은 버전을 다시 업로드하려 한다

PyPI는 동일 버전 덮어쓰기를 허용하지 않습니다. 수정 사항이 있으면 반드시 버전을 올려야 합니다.

### 실수 2. API 토큰을 코드에 하드코딩한다

```bash
# 잘못: 토큰이 Git 히스토리에 남음
twine upload --password pypi-abc123 dist/*

# 올바름: 환경변수 또는 .pypirc 사용
export TWINE_PASSWORD=pypi-abc123
```

### 실수 3. TestPyPI를 건너뛰고 바로 PyPI에 올린다

TestPyPI에서 먼저 테스트하세요. PyPI에 올린 후에는 삭제할 수 없습니다(72시간 이내 프로젝트 삭제만 가능).

### 실수 4. 패키지 이름이 이미 있는지 확인하지 않는다

PyPI에서 이름이 먼저 등록되면 사용할 수 없습니다. `pip index versions mylib`이나 pypi.org 검색으로 미리 확인하세요.

### 실수 5. dist/에 이전 버전 파일이 남아있는 채로 업로드한다

```bash
rm -rf dist/
python -m build
twine upload dist/*    # 현재 버전만 업로드
```

## 실무 적용

- **CI/CD 자동 배포**: GitHub Actions에서 태그 push 시 자동으로 PyPI에 배포합니다
- **Trusted Publisher**: OIDC 기반으로 API 토큰 없이 GitHub Actions에서 직접 배포합니다
- **사내 저장소**: Artifactory, Nexus, devpi에 사내 패키지를 배포합니다
- **pre-release**: `0.1.0rc1` 같은 pre-release 버전으로 베타 테스트합니다
- **README 렌더링**: PyPI 페이지에 표시되는 README는 `[project.readme]`로 지정합니다

## 실무에서는 이렇게 생각한다

수동 배포는 실수를 유발합니다. "빌드 → 테스트 → 업로드"를 CI/CD로 자동화하는 것이 표준입니다. GitHub Actions + Trusted Publisher를 쓰면 토큰 관리도 필요 없습니다.

패키지 이름은 한번 정하면 바꾸기 어렵습니다. 이름이 직관적이고, 기존 패키지와 충돌하지 않으며, 검색하기 쉬운 이름을 고르세요. PyPI에서 검색해보고, `pip index versions`로 확인한 뒤 배포하세요.

## 체크리스트

- [ ] TestPyPI 계정을 만들고 API 토큰을 발급할 수 있다
- [ ] `twine check`로 빌드 결과물의 유효성을 검증할 수 있다
- [ ] TestPyPI에 업로드하고 설치 테스트할 수 있다
- [ ] 실제 PyPI에 배포할 수 있다
- [ ] API 토큰을 환경변수로 안전하게 관리할 수 있다

## 연습 문제

1. TestPyPI 계정을 만들고, 이전 글에서 빌드한 패키지를 TestPyPI에 업로드해보세요.
2. 새 가상환경에서 TestPyPI의 패키지를 설치하고 import가 되는지 확인해보세요.
3. `~/.pypirc` 파일을 작성하여 `twine upload --repository testpypi dist/*` 실행 시 토큰을 자동으로 사용하도록 설정해보세요.

## 정리 · 다음 글

- PyPI는 Python 패키지의 공식 저장소이고, TestPyPI는 테스트 환경입니다.
- `twine check`로 유효성을 검증하고, `twine upload`로 업로드합니다.
- TestPyPI에서 먼저 테스트한 뒤 실제 PyPI에 배포합니다.
- 한 번 업로드한 버전은 수정할 수 없으므로 버전을 올려야 합니다.
- API 토큰은 코드에 넣지 않고 환경변수나 `.pypirc`로 관리합니다.

다음 글에서는 **버전 관리와 릴리스** — SemVer, Git 태그, CHANGELOG를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- **PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (현재 글)**
- 버전 관리와 릴리스 (예정)
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide - Uploading](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
- [PyPI - Publishing with Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [twine documentation](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)

Tags: Python, PyPI, twine, Publishing, TestPyPI, Distribution
