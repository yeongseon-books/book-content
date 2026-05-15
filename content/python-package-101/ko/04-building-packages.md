---
title: 패키지 빌드하기 — wheel과 sdist
series: python-package-101
episode: 4
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
- wheel
- sdist
- Build
- Packaging
- Distribution
last_reviewed: '2026-05-12'
seo_description: wheel은 이미 빌드된 패키지 파일이고, sdist는 소스 코드를 묶은 원본 아카이브입니다. 둘 다 만들어야 어디서든 설치할 수 있습니다.
---

# 패키지 빌드하기 — wheel과 sdist

패키지를 구조화하고 의존성을 정리했다면, 이제 실제로 배포 가능한 파일을 만들어야 합니다. `pip install`은 소스 저장소를 직접 읽는 것이 아니라 배포판 아카이브를 설치하기 때문입니다. 이 글은 Python Package 101 시리즈의 4번째 글입니다. 여기서는 wheel과 sdist의 차이, `python -m build`가 생성하는 결과물, 그리고 빌드 후 반드시 확인해야 할 검증 포인트를 정리하겠습니다.

## 이 글에서 다룰 문제

- wheel과 sdist는 무엇이 다를까요?
- `python -m build`는 어떤 파일을 만들까요?
- `.whl` 파일 안에는 무엇이 들어 있을까요?
- PyPI에는 어떤 파일을 올려야 할까요?

## 이 글에서 배우는 내용

- sdist(source distribution)와 wheel(built distribution)의 차이
- `python -m build`로 두 가지 배포판을 생성하는 방법
- `.whl` 파일의 내부 구조를 확인하는 방법
- 어떤 파일이 빌드 결과물에 포함되는지 제어하는 방법

## 왜 중요한가

`pip install`은 PyPI에서 패키지를 내려받아 설치합니다. 이때 내려받는 파일이 wheel이거나 sdist입니다. 따라서 직접 패키지를 배포하려면 결국 이 두 가지 형식을 이해하고 생성할 수 있어야 합니다.

> `pip install mylib`을 실행하면 pip은 먼저 wheel을 찾습니다. wheel이 없으면 sdist를 내려받아 로컬에서 직접 빌드합니다. 그래서 wheel이 없는 패키지는 설치가 느리고, 빌드 도구까지 추가로 필요할 수 있습니다.

## 멘탈 모델

sdist는 요리 레시피이고, wheel은 이미 완성된 냉동식품에 가깝습니다. 레시피를 전달하면 받는 쪽에서 직접 조리해야 하지만, 완성품은 곧바로 꺼내 쓸 수 있습니다.

```text
source code → python -m build → dist/
                                ├── mylib-0.1.0.tar.gz     (sdist)
                                └── mylib-0.1.0-py3-none-any.whl  (wheel)
```

## 핵심 개념

| 용어 | 설명 | 파일 형식 |
|---|---|---|
| sdist | 소스 코드 + 메타데이터 아카이브 | `.tar.gz` |
| wheel | 미리 빌드된 배포판 | `.whl` (ZIP 형식) |
| build frontend | 빌드를 실행하는 도구 | `python -m build`, `uv build` |
| build backend | 실제 빌드 로직을 수행하는 도구 | `setuptools`, `hatchling` |
| dist/ | 빌드 결과물이 저장되는 디렉터리 | `dist/mylib-0.1.0.tar.gz` |

## Before / After

**Before (sdist only)**

```bash
pip install mylib
# Downloading mylib-0.1.0.tar.gz
# Building wheel from source...  ← local build (slow)
# Successfully installed mylib
```

**After (wheel available)**

```bash
pip install mylib
# Downloading mylib-0.1.0-py3-none-any.whl
# Successfully installed mylib  ← no build needed (fast)
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
# .whl is a ZIP file
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

### Step 5. 빌드 결과물 설치 테스트

```bash
# Test wheel install in a fresh virtual environment
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install dist/mylib-0.1.0-py3-none-any.whl

python -c "from mylib.core import greet; print(greet('Test'))"
# Hello, Test!
deactivate
```

## 이 코드에서 눈여겨볼 점

- `mylib-0.1.0-py3-none-any.whl`에서 `py3`은 Python 3용, `none`은 ABI 없음, `any`는 플랫폼 독립을 뜻합니다.
- sdist에는 `pyproject.toml`이 포함되므로 받은 쪽에서 소스 빌드를 다시 수행할 수 있습니다.
- `dist-info/METADATA`는 `pyproject.toml`의 `[project]` 내용이 설치 메타데이터로 변환된 결과입니다.
- `dist-info/RECORD`는 설치된 모든 파일의 해시와 경로를 기록합니다.

## 자주 하는 실수

### 실수 1. `dist/`를 Git에 커밋한다

빌드 결과물은 산출물이므로 보통 버전 관리 대상이 아닙니다. `.gitignore`에 `dist/`를 추가하는 편이 맞습니다.

### 실수 2. wheel만 올리고 sdist를 생략한다

C 확장이 있는 패키지는 플랫폼별 wheel이 필요합니다. sdist가 함께 있으면 wheel이 없는 환경에서도 소스에서 직접 빌드할 수 있습니다.

### 실수 3. 오래된 결과물이 남아 있는 상태로 다시 빌드한다

```bash
rm -rf dist/ build/ *.egg-info
python -m build    # build from a clean state
```

### 실수 4. 빌드 후 설치 테스트를 하지 않는다

빌드가 성공했다는 사실이 곧 설치 성공을 보장하지는 않습니다. 파일 누락이나 패키지 탐색 설정 오류는 설치해 보기 전까지 드러나지 않을 수 있습니다.

### 실수 5. wheel 파일명 태그를 이해하지 못한다

`py3-none-any`는 순수 Python 패키지라는 뜻입니다. C 확장이 섞이면 `cp311-cp311-manylinux_2_17_x86_64`처럼 특정 Python 버전과 플랫폼을 가리키는 태그가 붙습니다.

## 실무 적용

- **CI/CD 파이프라인**: `python -m build`는 빌드 → 테스트 → 업로드 흐름의 출발점입니다.
- **사내 패키지 저장소**: Artifactory, Nexus에 wheel을 올려 팀 내부 공유에 활용할 수 있습니다.
- **Docker 최적화**: wheel을 미리 만들어 두면 이미지 빌드 시간을 줄이기 쉽습니다.
- **크로스 플랫폼 배포**: `cibuildwheel`로 여러 플랫폼용 wheel을 한 번에 만들 수 있습니다.
- **재현 가능성 검증**: 아티팩트 해시를 기록해 동일 입력이 동일 출력을 내는지 확인할 수 있습니다.

## 실무에서는 이렇게 생각합니다

순수 Python 패키지라면 빌드는 비교적 단순합니다. `python -m build` 한 줄이면 충분한 경우가 많습니다. 복잡성이 급격히 올라가는 시점은 C 확장이 섞일 때입니다. NumPy나 pandas가 운영체제와 Python 버전 조합별로 수많은 wheel을 제공하는 이유도 여기에 있습니다.

대부분의 애플리케이션 개발자는 순수 Python 패키지를 만들기 때문에 `py3-none-any` wheel로 충분합니다. 중요한 습관은 빌드 자체보다 **빌드 후 새 환경에 설치해 보는 검증**입니다.

## 체크리스트

- [ ] sdist와 wheel의 차이를 설명할 수 있다
- [ ] `python -m build`로 두 가지 배포판을 생성할 수 있다
- [ ] wheel 파일의 내부 구조를 확인할 수 있다
- [ ] 빌드 결과물을 새 가상환경에서 설치 테스트할 수 있다
- [ ] wheel 파일명의 태그(`py3-none-any`)를 해석할 수 있다

## 연습 문제

1. 이전 글에서 만든 프로젝트를 `python -m build`로 빌드하고 `dist/` 내용을 직접 확인해 보세요.
2. `unzip -l`로 `.whl` 파일 안에 어떤 파일이 들어 있는지 보고, `METADATA` 파일도 읽어 보세요.
3. 새 가상환경을 만든 뒤 빌드한 wheel을 설치하고 import가 정상 동작하는지 검증해 보세요.

## 정리 · 다음 글

- sdist는 소스 아카이브이고, wheel은 미리 빌드된 배포판입니다.
- `python -m build`는 두 가지를 모두 생성합니다.
- wheel은 설치를 빠르게 하고, sdist는 어떤 환경에서든 빌드 가능성을 보장합니다.
- 빌드가 끝나면 반드시 새 환경에서 설치 테스트를 해야 합니다.
- 순수 Python 패키지는 보통 `py3-none-any` wheel을 만듭니다.

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

Tags: Python, wheel, sdist, Build, Packaging, Distribution
