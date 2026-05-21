---
title: "Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist"
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
last_reviewed: '2026-05-15'
seo_description: wheel은 이미 빌드된 패키지 파일이고, sdist는 소스 코드를 묶은 원본 아카이브입니다. 둘 다 만들어야 어디서든 설치할 수 있습니다.
---

# Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist

패키지를 구조화하고 의존성을 정리했다면, 이제 실제로 배포 가능한 파일을 만들어야 합니다. `pip install`은 소스 저장소를 직접 읽는 것이 아니라 배포판 아카이브를 설치하기 때문입니다.

이 글은 Python Package 101 시리즈의 4번째 글입니다. 여기서는 wheel과 sdist의 차이, `python -m build`가 생성하는 결과물, 그리고 빌드 후 반드시 확인해야 할 검증 포인트를 정리하겠습니다.

![Python Package 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/04/04-01-mental-model.ko.png)
*Python Package 101 4장 흐름 개요*

## 먼저 던지는 질문

- wheel과 sdist는 무엇이 다를까요?
- `python -m build`는 어떤 파일을 만들까요?
- `.whl` 파일 안에는 무엇이 들어 있을까요?

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

## 적용 전후 비교
**Before (sdist만 제공)**

```bash
pip install mylib
# Downloading mylib-0.1.0.tar.gz
# Building wheel from source...  ← local build (slow)
# Successfully installed mylib
```

**After (wheel 제공)**

```bash
pip install mylib
# Downloading mylib-0.1.0-py3-none-any.whl
# Successfully installed mylib  ← no build needed (fast)
```

## 단계별 실습

### 단계 1. build 도구 설치

```bash
cd ~/practice/mylib-project
source .venv/bin/activate
pip install build
```

### 단계 2. 빌드 실행

```bash
python -m build

# * Creating sdist...
# * Creating wheel...
# Successfully built mylib-0.1.0.tar.gz and mylib-0.1.0-py3-none-any.whl

ls dist/
# mylib-0.1.0-py3-none-any.whl
# mylib-0.1.0.tar.gz
```

### 단계 3. wheel 파일 내부 확인

```bash
# .whl is a ZIP file
unzip -l dist/mylib-0.1.0-py3-none-any.whl
# mylib/__init__.py
# mylib/core.py
# mylib-0.1.0.dist-info/METADATA
# mylib-0.1.0.dist-info/WHEEL
# mylib-0.1.0.dist-info/RECORD
```

### 단계 4. sdist 파일 내부 확인

```bash
tar tzf dist/mylib-0.1.0.tar.gz
# mylib-0.1.0/
# mylib-0.1.0/pyproject.toml
# mylib-0.1.0/src/mylib/__init__.py
# mylib-0.1.0/src/mylib/core.py
# mylib-0.1.0/PKG-INFO
```

### 단계 5. 빌드 결과물 설치 테스트

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

## 빌드 과정 내부 동작

`python -m build`를 실행하면 내부적으로 어떤 일이 일어나는지 단계별로 살펴보겠습니다.

### 빌드 격리 환경

```text
python -m build 실행 시:
    │
    ▼
1. 임시 디렉터리 생성 (/tmp/build-env-xxxx/)
    │
    ▼
2. pyproject.toml의 [build-system].requires 읽기
    │
    ▼
3. 격리 환경에 빌드 의존성 설치
   (setuptools, wheel 등)
    │
    ▼
4. build-backend의 build_sdist() 호출 → .tar.gz 생성
    │
    ▼
5. build-backend의 build_wheel() 호출 → .whl 생성
    │
    ▼
6. dist/ 디렉터리에 산출물 배치
```

```bash
# 빌드 과정을 상세 로그로 확인
python -m build --no-isolation 2>&1 | head -30
# --no-isolation: 격리 없이 현재 환경의 도구로 빌드 (디버깅용)
```

### sdist vs wheel 상세 비교

| 속성 | sdist (.tar.gz) | wheel (.whl) |
|---|---|---|
| 내용물 | 소스 코드 + 빌드 스크립트 | 빌드 완료된 파일 |
| 설치 시 빌드 | 필요 (setup.py 실행) | 불필요 (압축 해제만) |
| C 확장 | 사용자 환경에서 컴파일 | 미리 컴파일된 바이너리 |
| 설치 속도 | 느림 | 빠름 |
| 플랫폼 의존성 | 빌드 시 결정 | 파일명에 명시 |
| PyPI 권장 | sdist + wheel 함께 업로드 | 주 설치 대상 |

### sdist 내부 구조

```bash
tar tzf dist/acme_utils-0.1.0.tar.gz | head -15
```

```text
acme_utils-0.1.0/
├── PKG-INFO                    # 메타데이터 (METADATA와 유사)
├── pyproject.toml              # 빌드 설정 원본
├── README.md
├── src/
│   └── acme_utils/
│       ├── __init__.py
│       ├── core.py
│       └── config.py
└── tests/                      # 포함 여부는 설정에 따라 다름
    └── test_core.py
```

### wheel 내부 구조

```bash
unzip -l dist/acme_utils-0.1.0-py3-none-any.whl
```

```text
acme_utils/__init__.py
acme_utils/core.py
acme_utils/config.py
acme_utils/py.typed
acme_utils-0.1.0.dist-info/METADATA
acme_utils-0.1.0.dist-info/WHEEL
acme_utils-0.1.0.dist-info/RECORD
acme_utils-0.1.0.dist-info/entry_points.txt
acme_utils-0.1.0.dist-info/top_level.txt
```

## MANIFEST.in과 파일 포함/제외

sdist에 어떤 파일이 포함되는지 제어하는 방법입니다.

### setuptools의 기본 포함 규칙

```text
자동 포함:
- pyproject.toml, setup.py, setup.cfg
- README, README.md, README.rst
- LICENSE, LICENCE
- src/ 아래 Python 파일 (.py)

자동 제외:
- __pycache__/
- *.pyc, *.pyo
- .git/, .hg/
- dist/, build/, *.egg-info/
```

### MANIFEST.in으로 추가 파일 포함

```text
# MANIFEST.in
include CHANGELOG.md
include src/acme_utils/py.typed
recursive-include src *.pyi        # 타입 스텁
recursive-include tests *.py       # 테스트 포함 (선택)
global-exclude *.pyc __pycache__
```

### pyproject.toml로 제어 (setuptools)

```toml
[tool.setuptools.package-data]
acme_utils = ["py.typed", "*.pyi"]

[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*"]
```

## C 확장 패키지의 빌드

순수 Python이 아닌 패키지는 빌드 과정이 더 복잡합니다.

```toml
# C 확장을 포함하는 pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel", "cython>=3.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
ext-modules = [
    {name = "acme_utils._speedups", sources = ["src/acme_utils/_speedups.c"]}
]
```

```bash
# 플랫폼별 wheel 생성
python -m build
ls dist/
# acme_utils-0.1.0.tar.gz
# acme_utils-0.1.0-cp311-cp311-linux_x86_64.whl    <- 플랫폼 특정!
```

### cibuildwheel로 멀티 플랫폼 wheel 생성

```yaml
# .github/workflows/wheels.yml
name: Build wheels
on: [push]
jobs:
  build_wheels:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: pypa/cibuildwheel@v2.19
        env:
          CIBW_SKIP: "cp36-* cp37-* cp38-* cp39-*"
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: wheelhouse/*.whl
```

## 빌드 검증 체크리스트

빌드 산출물을 배포하기 전에 반드시 확인해야 할 사항입니다.

```bash
# 1. dist/ 정리 후 빌드
rm -rf dist/
python -m build

# 2. twine check: 메타데이터 유효성 검증
python -m twine check dist/*
# PASSED acme_utils-0.1.0.tar.gz
# PASSED acme_utils-0.1.0-py3-none-any.whl

# 3. wheel 내용물 확인
unzip -l dist/*.whl | grep -v dist-info

# 4. 설치 테스트 (깨끗한 venv에서)
python -m venv /tmp/test-install
/tmp/test-install/bin/pip install dist/*.whl
/tmp/test-install/bin/python -c "import acme_utils; print(acme_utils.__version__)"

# 5. sdist에서 빌드 가능한지 확인
pip install dist/*.tar.gz
```

### twine check가 잡아내는 문제들

```text
WARNING: The long_description is not valid rst.    # README 렌더링 오류
ERROR: `long_description_content_type` missing.    # content type 미지정
WARNING: No `project_urls` found.                  # URL 없음
```

## 재현 가능한 빌드

같은 소스에서 항상 동일한 빌드 산출물을 생성하려면 추가 설정이 필요합니다.

```bash
# 타임스탬프를 고정하여 재현 가능한 빌드
SOURCE_DATE_EPOCH=0 python -m build

# 결과 검증: 두 번 빌드하여 해시 비교
sha256sum dist/acme_utils-0.1.0-py3-none-any.whl
# 두 번 모두 같은 해시가 나와야 함
```

```toml
# hatchling은 기본적으로 reproducible build 지원
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## setuptools vs hatchling 빌드 비교

같은 프로젝트를 두 백엔드로 빌드할 때의 차이를 비교합니다.

### setuptools로 빌드

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
time python -m build
# real    0m4.2s (격리 환경 생성 + setuptools 설치 + 빌드)
ls dist/
# acme_utils-0.1.0.tar.gz  (sdist)
# acme_utils-0.1.0-py3-none-any.whl  (wheel)
```

### hatchling으로 빌드

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
```

```bash
time python -m build
# real    0m2.1s (hatchling이 더 가벼움)
ls dist/
# acme_utils-0.1.0.tar.gz
# acme_utils-0.1.0-py3-none-any.whl
```

### 결과물 비교

두 백엔드의 wheel 내용물은 동일합니다. 차이는 빌드 속도와 설정 방식에 있습니다. setuptools는 레거시 호환이 뛰어나고, hatchling은 설정이 간결하고 빌드가 빠릅니다.

## 빌드 캐시와 정리

```bash
# 빌드 아티팩트 정리
rm -rf dist/ build/ src/*.egg-info/

# .egg-info가 남아있으면 editable install이 꼬일 수 있음
find . -name "*.egg-info" -type d -exec rm -rf {} +

# __pycache__ 정리
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Makefile로 빌드 자동화

```makefile
.PHONY: clean build check publish

clean:
	rm -rf dist/ build/ src/*.egg-info/

build: clean
	python -m build

check: build
	python -m twine check dist/*

publish-test: check
	python -m twine upload --repository testpypi dist/*

publish: check
	python -m twine upload dist/*
```

```bash
make build    # 정리 + 빌드
make check    # 정리 + 빌드 + 검증
make publish  # 정리 + 빌드 + 검증 + PyPI 업로드
```

## 빌드 시 자주 만나는 에러와 해결

### 에러 1: 패키지를 찾지 못함

```text
error: No packages found in `src`
```

```toml
# 원인: packages.find 설정 누락 또는 __init__.py 없음
[tool.setuptools.packages.find]
where = ["src"]  # 이 설정이 있는지 확인

# src/acme_utils/__init__.py가 있는지 확인
```

### 에러 2: README 렌더링 실패

```text
WARNING: The long_description is not valid reStructuredText
```

```toml
# 해결: content-type을 명시적으로 지정
[project]
readme = {file = "README.md", content-type = "text/markdown"}
```

### 에러 3: 버전 형식 오류

```text
Invalid version: '0.1.0-beta'
```

```text
# PEP 440 유효한 버전:
0.1.0
0.1.0a1        # alpha
0.1.0b2        # beta
0.1.0rc1       # release candidate
0.1.0.post1    # post release
0.1.0.dev1     # development

# 유효하지 않은 버전:
0.1.0-beta     # 하이픈 불가
v0.1.0         # 접두사 v 불가
```

### 에러 4: 의존성 빌드 실패

```text
error: subprocess-exited-with-error
× pip subprocess to install build dependencies did not run successfully
```

```bash
# 해결: 빌드 도구 업데이트
pip install --upgrade pip setuptools wheel
# 또는 격리 없이 빌드하여 디버깅
python -m build --no-isolation
```

## GitHub Actions 빌드 + 아티팩트 저장

```yaml
name: build
on:
  push:
    tags: ["v*"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: python -m twine check dist/*
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

태그 푸시 시 자동으로 빌드하고 아티팩트를 저장합니다. 이 아티팩트는 후속 배포 job에서 사용할 수 있습니다.

## 빌드 아티팩트 크기 최적화

배포 패키지에 불필요한 파일이 포함되면 설치 시간이 늘어나고 보안 위험이 커집니다.

### 포함되면 안 되는 파일 확인

```bash
# wheel 내용물 크기 확인
python -m zipfile -l dist/acme_utils-0.1.0-py3-none-any.whl

# 불필요한 파일이 포함되었는지 확인
unzip -l dist/*.whl | grep -E "test_|__pycache__|.pyc"
```

### 제외 설정

```toml
# setuptools
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*", "docs*", "benchmarks*"]

# hatchling
[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
exclude = ["*.test", "tests/"]
```

### 실무 크기 기준

```text
순수 Python 유틸리티: 50-500 KB (wheel)
웹 프레임워크: 1-5 MB
데이터 과학 (NumPy 등): 10-50 MB (바이너리 포함)
```

wheel 크기가 비정상적으로 크다면 데이터 파일이나 테스트가 실수로 포함된 것은 아닌지 확인합니다.

## 로컬 빌드와 CI 빌드 일치시키기

로컬에서 `python -m build`가 통과해도 CI에서 실패하는 경우가 있습니다. 원인과 해결책을 정리합니다.

### 원인 1: Python 버전 차이

```bash
# 로컬
python --version  # 3.12.4
# CI
python --version  # 3.11.9

# pyproject.toml에 requires-python = ">=3.11"이면
# 3.11에서도 빌드와 테스트가 통과해야 합니다.
```

### 원인 2: 시스템 패키지 의존성

```bash
# 로컬에 시스템 레벨로 설치된 라이브러리가 있으면
# CI의 깨끗한 환경에서는 찾지 못할 수 있습니다.
# 해결: 모든 의존성을 pyproject.toml에 명시
```

### 원인 3: 파일 권한과 라인 엔딩

```bash
# Git이 CRLF를 변환하면서 해시가 달라질 수 있음
# .gitattributes로 통일
echo "* text=auto eol=lf" > .gitattributes
```

### 해결 전략: 동일한 명령 세트 사용

```makefile
# Makefile (로컬과 CI 모두 동일하게 실행)
.PHONY: ci
ci: install lint typecheck test build check

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest -q

build:
	python -m build

check:
	python -m twine check dist/*
```

CI의 워크플로우에서 `make ci`만 실행하면 로컬과 동일한 검증을 보장합니다.

### sdist만으로 배포해도 되는가?

sdist만 올리면 사용자 환경에서 빌드가 실행됩니다. 순수 Python 패키지라면 문제없지만, C 확장이 있으면 사용자에게 컴파일러가 필요합니다. 가능하면 wheel과 sdist를 함께 올리는 것이 표준입니다.

```bash
# PyPI 업로드 시 권장: sdist + wheel 모두 포함
ls dist/
# acme_utils-0.1.0.tar.gz           <- sdist
# acme_utils-0.1.0-py3-none-any.whl <- wheel
python -m twine upload dist/*        # 둘 다 업로드
```

pip은 wheel이 있으면 wheel을 우선 선택하고, 해당 플랫폼의 wheel이 없을 때만 sdist를 내려받아 빌드합니다.

순수 Python wheel의 `py3-none-any` 태그는 어떤 Python 3 환경에서든 동일하게 동작한다는 의미입니다. 따라서 한 번만 빌드하면 Linux, macOS, Windows 모두에서 사용할 수 있습니다.

## 처음 질문으로 돌아가기

- **sdist와 wheel은 무엇이 다를까요?**
  - sdist는 소스 코드 아카이브로 설치 시 빌드 과정이 필요합니다. wheel은 빌드가 완료된 바이너리 배포 형식으로 압축을 풀기만 하면 설치가 끝납니다. PyPI에는 sdist와 wheel을 함께 올리되, pip은 wheel을 우선 선택합니다.

- **`python -m build`는 내부에서 어떤 일을 할까요?**
  - 격리된 임시 환경을 만들고 `[build-system].requires`의 도구를 설치한 뒤, `build-backend`가 가리키는 모듈의 `build_sdist()`와 `build_wheel()` 함수를 순서대로 호출합니다. 결과물은 `dist/` 디렉터리에 `.tar.gz`과 `.whl` 파일로 생성됩니다.

- **빌드 산출물이 올바른지 어떻게 검증할까요?**
  - `twine check dist/*`로 메타데이터와 README 렌더링을 검증하고, 깨끗한 venv에서 wheel을 설치하여 import와 버전 출력이 정상인지 확인합니다. sdist에서도 빌드가 되는지 별도로 검증하면 소스 배포 시의 문제를 미리 잡을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- **Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist (현재 글)**
- Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- Python Package 101 (6/10): 버전 관리와 릴리스 (예정)
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging User Guide - Packaging your project](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)
- [PEP 427 - The Wheel Binary Package Format](https://peps.python.org/pep-0427/)
- [PyPA build - A simple PEP 517 build frontend](https://build.pypa.io/en/stable/)
- [Real Python - Python Wheels](https://realpython.com/python-wheels/)

Tags: Python, Packaging, PyPI, pyproject.toml
