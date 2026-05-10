---
title: 패키지 빌드하기 — wheel과 sdist
series: python-package-101
episode: 4
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
- wheel
- sdist
- Build
- Packaging
- Distribution
last_reviewed: '2026-05-04'
seo_description: wheel은 이미 빌드된 패키지 파일이고, sdist는 소스 코드를 묶은 원본 아카이브입니다. 둘 다 만들어야 어디서든 설치할 수 있습니다.
---

# 패키지 빌드하기 — wheel과 sdist

> Python Package 101 시리즈 (4/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- wheel과 sdist는 무엇이 다를까요?
- `python -m build`는 어떤 파일을 생성할까요?
- `.whl` 파일 안에는 무엇이 들어있을까요?
- 어떤 파일을 PyPI에 올려야 할까요?

> wheel은 이미 빌드된 패키지 파일이고, sdist는 소스 코드를 묶은 원본 아카이브입니다. 둘 다 만들어야 어디서든 설치할 수 있습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- sdist(source distribution)와 wheel(built distribution)의 차이
- `python -m build`로 두 가지 배포판을 생성하는 법
- `.whl` 파일의 내부 구조
- MANIFEST.in과 빌드에 포함되는 파일 제어

## 왜 중요한가

`pip install`은 PyPI에서 패키지를 다운로드하여 설치합니다. 이때 다운로드되는 파일이 wheel 또는 sdist입니다. 직접 패키지를 배포하려면 이 파일을 만들어야 합니다.

> `pip install mylib`을 실행하면 pip은 먼저 wheel을 찾습니다. wheel이 없으면 sdist를 다운로드하고 로컬에서 빌드합니다. wheel이 없는 패키지는 설치가 느리고 빌드 도구가 필요합니다.

## Mental Model

> sdist는 요리 레시피(소스 코드 + 재료 목록)이고, wheel은 완성된 냉동 식품(바로 먹을 수 있는 상태)입니다. 레시피를 줄 수도 있고, 완성품을 줄 수도 있지만, 완성품이 더 빠르게 먹을 수 있습니다.

```text
소스 코드 → python -m build → dist/
                                ├── mylib-0.1.0.tar.gz     (sdist)
                                └── mylib-0.1.0-py3-none-any.whl  (wheel)
```

## 핵심 개념

| 용어 | 설명 | 파일 형태 |
|---|---|---|
| sdist | 소스 코드 + 메타데이터 아카이브 | `.tar.gz` |
| wheel | 빌드 완료된 배포판 | `.whl` (ZIP 형식) |
| build frontend | 빌드를 실행하는 도구 | `python -m build`, `uv build` |
| build backend | 실제 빌드 로직을 수행하는 도구 | `setuptools`, `hatchling` |
| dist/ | 빌드 결과물이 저장되는 디렉터리 | `dist/mylib-0.1.0.tar.gz` |

## Before / After

**Before (sdist만 제공)**

```bash
pip install mylib
# Downloading mylib-0.1.0.tar.gz
# Building wheel from source...  ← 로컬에서 빌드 (느림)
# Successfully installed mylib
```

**After (wheel도 제공)**

```bash
pip install mylib
# Downloading mylib-0.1.0-py3-none-any.whl
# Successfully installed mylib  ← 빌드 없이 바로 설치 (빠름)
```

## 단계별 실습

### Step 1. build 도구 설치

```bash
cd ~/practice/mylib-project
source .venv/bin/activate
pip install build
```

### Step 2. 빌드 실행

```bash
python -m build

# * Creating sdist...
# * Creating wheel...
# Successfully built mylib-0.1.0.tar.gz and mylib-0.1.0-py3-none-any.whl

ls dist/
# mylib-0.1.0-py3-none-any.whl
# mylib-0.1.0.tar.gz
```

### Step 3. wheel 파일 내부 확인

```bash
# .whl은 ZIP 파일
unzip -l dist/mylib-0.1.0-py3-none-any.whl
# mylib/__init__.py
# mylib/core.py
# mylib-0.1.0.dist-info/METADATA
# mylib-0.1.0.dist-info/WHEEL
# mylib-0.1.0.dist-info/RECORD
```

### Step 4. sdist 파일 내부 확인

```bash
tar tzf dist/mylib-0.1.0.tar.gz
# mylib-0.1.0/
# mylib-0.1.0/pyproject.toml
# mylib-0.1.0/src/mylib/__init__.py
# mylib-0.1.0/src/mylib/core.py
# mylib-0.1.0/PKG-INFO
```

### Step 5. 빌드된 패키지 설치 테스트

```bash
# 새 가상환경에서 wheel 설치 테스트
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install dist/mylib-0.1.0-py3-none-any.whl

python -c "from mylib.core import greet; print(greet('Test'))"
# Hello, Test!
deactivate
```

## 이 코드에서 봐야 할 것

- wheel 파일명 `mylib-0.1.0-py3-none-any.whl`에서 `py3`은 Python 3, `none`은 ABI 없음, `any`는 모든 플랫폼을 의미합니다
- sdist에는 `pyproject.toml`이 포함되어 수신자가 직접 빌드할 수 있습니다
- `dist-info/METADATA`는 pyproject.toml의 `[project]` 내용이 변환된 것입니다
- `dist-info/RECORD`는 설치된 모든 파일의 해시를 기록합니다

## 자주 하는 실수

### 실수 1. dist/ 디렉터리를 Git에 커밋한다

빌드 결과물은 커밋하지 않습니다. `.gitignore`에 `dist/`를 추가하세요.

### 실수 2. wheel만 올리고 sdist를 빼먹는다

C 확장이 있는 패키지는 플랫폼별 wheel이 필요합니다. sdist가 있으면 어떤 플랫폼에서도 소스에서 빌드할 수 있습니다.

### 실수 3. 이전 빌드 결과가 남아있는 채로 다시 빌드한다

```bash
rm -rf dist/ build/ *.egg-info
python -m build    # 깨끗한 상태에서 빌드
```

### 실수 4. 빌드 후 설치 테스트를 하지 않는다

빌드가 성공해도 파일이 누락될 수 있습니다. 항상 새 가상환경에서 설치하여 import를 확인하세요.

### 실수 5. wheel 파일명의 태그를 이해하지 못한다

`py3-none-any`는 순수 Python 패키지를 의미합니다. C 확장이 있으면 `cp311-cp311-manylinux_2_17_x86_64` 같은 플랫폼 특정 태그가 붙습니다.

## 실무 적용

- **CI/CD 파이프라인**: 빌드 → 테스트 → 업로드의 첫 단계가 `python -m build`입니다
- **내부 패키지 저장소**: 사내 Artifactory/Nexus에 wheel을 업로드하여 팀 내 공유합니다
- **Docker 최적화**: wheel을 미리 빌드하면 Docker 이미지 빌드 시간이 단축됩니다
- **크로스 플랫폼**: C 확장 패키지는 `cibuildwheel`로 여러 플랫폼의 wheel을 한 번에 만듭니다
- **재현 가능성**: 빌드 결과물의 해시를 기록하여 동일한 입력이 동일한 출력을 만드는지 검증합니다

## 실무에서는 이렇게 생각한다

순수 Python 패키지라면 빌드는 단순합니다. `python -m build` 한 줄이면 됩니다. 복잡해지는 것은 C 확장이 있을 때입니다. NumPy, pandas 같은 패키지가 각 OS/Python 버전별로 수십 개의 wheel을 제공하는 이유입니다.

대부분의 애플리케이션 개발자는 순수 Python 패키지만 만들기 때문에 `py3-none-any` wheel이면 충분합니다. 중요한 것은 "빌드한 뒤 새 환경에서 설치해보는" 습관입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **표준 빌드** — python -m build를 표준으로 씁니다.
- **Sdist 포함 파일** — MANIFEST.in 또는 SCM 통합으로 누락을 막습니다.
- **Wheel 호환성** — pure Python이면 universal wheel을 검토합니다.
- **Native 의존** — C 확장은 cibuildwheel로 매트릭스 빌드합니다.
- **재현성** — 같은 커밋이 같은 sha를 만드는지 확인합니다.

## 체크리스트

- [ ] sdist와 wheel의 차이를 설명할 수 있다
- [ ] `python -m build`로 두 가지 배포판을 생성할 수 있다
- [ ] wheel 파일의 내부 구조를 확인할 수 있다
- [ ] 빌드 결과물을 새 가상환경에서 설치 테스트할 수 있다
- [ ] wheel 파일명의 태그(py3-none-any)를 해석할 수 있다

## 연습 문제

1. 이전 글에서 만든 프로젝트를 `python -m build`로 빌드하고, `dist/` 디렉터리의 내용을 확인해보세요.
2. `.whl` 파일을 `unzip -l`로 열어 어떤 파일이 포함되어 있는지 확인하고, `METADATA` 파일의 내용을 읽어보세요.
3. 새 가상환경을 만들어 빌드된 wheel을 설치하고, import가 정상적으로 되는지 확인해보세요.

## 정리 · 다음 글

- sdist는 소스 코드 아카이브, wheel은 빌드 완료된 배포판입니다.
- `python -m build`로 두 가지를 모두 생성합니다.
- wheel이 있으면 설치가 빠르고, sdist가 있으면 어디서든 빌드 가능합니다.
- 빌드 후에는 반드시 새 환경에서 설치 테스트를 합니다.
- 순수 Python 패키지의 wheel 태그는 `py3-none-any`입니다.

다음 글에서는 **PyPI에 배포하기** — TestPyPI부터 실제 배포까지를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- **패키지 빌드하기 — wheel과 sdist (현재 글)**
- PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- 버전 관리와 릴리스 (예정)
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide - Packaging your project](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)
- [PEP 427 - The Wheel Binary Package Format](https://peps.python.org/pep-0427/)
- [PyPA build - A simple PEP 517 build frontend](https://build.pypa.io/en/stable/)
- [Real Python - Python Wheels](https://realpython.com/python-wheels/)
