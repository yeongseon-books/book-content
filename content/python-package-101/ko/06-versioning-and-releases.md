---
title: "Python Package 101 (6/10): 버전 관리와 릴리스"
series: python-package-101
episode: 6
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
- Versioning
- SemVer
- Release
- CHANGELOG
- Git Tag
last_reviewed: '2026-05-15'
seo_description: SemVer는 버전 번호에 의미를 부여하는 규칙이고, Git 태그는 특정 커밋을 릴리스 시점으로 표시하는 것입니다.
---

# Python Package 101 (6/10): 버전 관리와 릴리스

패키지를 한 번 배포하고 나면, 그다음부터는 “무엇이 바뀌었는지”를 사용자에게 일관되게 알려 주는 일이 중요해집니다. 버전 번호, Git 태그, CHANGELOG는 모두 그 신호 체계를 만드는 도구입니다.

이 글은 Python Package 101 시리즈의 6번째 글입니다. 여기서는 SemVer 규칙, 버전을 코드와 메타데이터에 동기화하는 방법, 그리고 릴리스 기록을 남기는 기본 흐름을 정리하겠습니다.

## 먼저 던지는 질문

- SemVer의 MAJOR.MINOR.PATCH는 언제 올려야 할까요?
- 버전은 코드의 어디에 기록해야 할까요?
- Git 태그와 릴리스는 어떤 관계일까요?

## 큰 그림

![Python Package 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/06/06-01-mental-model.ko.png)

*Python Package 101 6장 흐름 개요*

## 이 글에서 배우는 내용

- SemVer 규칙과 각 버전을 올리는 기준
- `pyproject.toml`과 `__version__`을 동기화하는 방법
- Git 태그로 릴리스를 표시하고 관리하는 방법
- CHANGELOG를 쓰고 자동화하는 방법

## 왜 중요한가

패키지를 업데이트할 때 사용자는 가장 먼저 “이 업데이트가 안전한가?”를 판단합니다. 그때 보는 신호가 버전 번호입니다. 의미 없이 버전을 올리면 신뢰를 잃고, 호환성을 깨는 변경을 PATCH로 배포하면 실제 사용자 코드를 망가뜨릴 수 있습니다.

> `pip install mylib --upgrade`로 패치 버전을 올렸는데 API가 바뀌어서 프로덕션이 깨졌다고 가정해 보겠습니다. `0.2.3 → 0.2.4`였기 때문에 안전한 수정이라고 믿었지만, 실제로는 함수 시그니처가 달라져 있었습니다.

## 멘탈 모델

SemVer는 신호등과 비슷합니다. PATCH는 비교적 안전한 수정, MINOR는 기존을 유지한 채 기능이 늘어난 상태, MAJOR는 사용자 코드 수정이 필요할 수 있는 변경을 의미합니다.

```text
MAJOR . MINOR . PATCH
  1   .   2   .   3

PATCH  (1.2.3 → 1.2.4): Bug fix, no API changes
MINOR  (1.2.4 → 1.3.0): New feature, existing API preserved
MAJOR  (1.3.0 → 2.0.0): API changed or removed (breaking)
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| SemVer | 의미 기반 버전 관리 규칙 | `1.2.3` |
| pre-release | 정식 릴리스 전 테스트 버전 | `1.0.0rc1`, `1.0.0a1` |
| Git tag | 특정 커밋에 붙이는 릴리스 라벨 | `git tag v1.0.0` |
| CHANGELOG | 버전별 변경 사항을 기록한 문서 | `CHANGELOG.md` |
| single source of truth | 버전을 정확히 한 곳에서 관리하는 원칙 | `pyproject.toml` 또는 `__version__` |

## Before / After

**Before (no version management)**

```text
# commit messages only
"fixed bug"
"added feature"
"more fixes"
# → no way to tell which commit is which release
```

**After (SemVer + Git tag + CHANGELOG)**

```text
v1.2.3 ← git tag
  CHANGELOG.md:
  ## 1.2.3 (2026-05-04)
  ### Fixed
  - Fixed timeout error in API client
```

## 단계별 실습

### Step 1. `pyproject.toml`에 버전 지정

```toml
[project]
name = "mylib"
version = "0.1.0"
```

### Step 2. `__version__` 동기화

```python
# src/mylib/__init__.py
"""mylib - A sample Python package."""
__version__ = "0.1.0"
```

```python
# How users check the version
import mylib
print(mylib.__version__)  # 0.1.0
```

### Step 3. Git 태그로 릴리스 표시

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags

# List tags
git tag
# v0.1.0
```

### Step 4. CHANGELOG 작성

```markdown
# CHANGELOG.md

## 0.1.0 (2026-05-04)

### Added
- Initial release
- `core.greet()` function
- src layout project structure
- pyproject.toml configuration
```

### Step 5. 버전 올리고 릴리스하기

```bash
# pyproject.toml: version = "0.2.0"
# src/mylib/__init__.py: __version__ = "0.2.0"

git add .
git commit -m "Release v0.2.0: add string utilities"
git tag v0.2.0
python -m build
twine upload dist/*
```

## 이 코드에서 눈여겨볼 점

- `pyproject.toml`의 `version`과 `__version__`은 항상 일치해야 합니다.
- Git 태그에 `v` 접두어를 붙이는 관례는 매우 널리 쓰입니다.
- CHANGELOG는 [Keep a Changelog](https://keepachangelog.com/) 형식을 따르면 읽기 쉽고 자동화도 편합니다.
- `git push`만으로는 태그가 올라가지 않으므로 `--tags`를 명시해야 합니다.

## 자주 하는 실수

### 실수 1. `pyproject.toml`과 `__version__`이 다르다

두 값이 어긋나면 `pip show` 결과와 `import mylib; print(mylib.__version__)` 결과가 달라질 수 있습니다. 사용자 입장에서는 어떤 버전이 진짜인지 헷갈리게 됩니다.

### 실수 2. 호환성 파괴를 PATCH로 배포한다

함수 시그니처 변경, 반환값 형식 변경, 필수 인자 추가처럼 기존 호출 코드를 수정해야 하는 변경은 보통 MAJOR로 봐야 합니다.

### 실수 3. `0.x` 버전에 안정성을 과도하게 기대한다

SemVer에서 `0.x.y`는 아직 초기 개발 단계라는 신호입니다. API가 언제든 바뀔 수 있으므로, 사용자 입장에서도 `1.0.0` 이전은 보수적으로 해석하는 편이 안전합니다.

### 실수 4. CHANGELOG를 쓰지 않는다

Git 로그만으로는 사용자가 “이번 버전에서 무엇이 바뀌었는지” 빠르게 파악하기 어렵습니다. CHANGELOG는 사용자와 유지보수자 모두를 위한 공식 기록입니다.

### 실수 5. 테스트 전에 태그를 먼저 단다

태그 push가 곧 배포 트리거인 경우가 많습니다. 검증 전에 태그를 만들면 깨진 릴리스가 자동으로 공개될 수 있습니다.

## 실무 적용

- **CI/CD 트리거**: Git 태그 push를 기준으로 자동 빌드와 PyPI 업로드를 실행합니다.
- **Dependabot/Renovate**: 의존 패키지의 새 버전에 대한 PR을 자동으로 생성합니다.
- **동적 버전 관리**: `setuptools-scm`으로 Git 태그에서 버전을 추출할 수 있습니다.
- **사전 릴리스**: `1.0.0a1 → 1.0.0b1 → 1.0.0rc1 → 1.0.0` 흐름으로 안정화할 수 있습니다.
- **GitHub Releases**: Git 태그와 CHANGELOG를 연결해 릴리스 노트를 구성할 수 있습니다.

## 실무에서는 이렇게 생각합니다

가장 어려운 질문은 대개 이것입니다. “이번 변경은 MINOR인가, 아니면 MAJOR인가?” 실무 기준은 단순한 편입니다. **기존 사용자의 코드가 수정 없이 계속 동작하면 MINOR, 사용자 코드를 바꿔야 하면 MAJOR**라고 보는 편이 가장 안전합니다.

버전을 두 군데에서 관리하는 것이 번거롭다면 `setuptools-scm` 같은 동적 버전 관리 도구를 검토할 수 있습니다. 다만 자동화 여부와 관계없이 중요한 것은 릴리스 기준을 팀 안에서 명확히 합의하는 일입니다.

## 체크리스트

- [ ] SemVer의 MAJOR.MINOR.PATCH 기준을 설명할 수 있다
- [ ] `pyproject.toml`과 `__version__`을 동기화할 수 있다
- [ ] Git 태그로 릴리스를 표시할 수 있다
- [ ] Keep a Changelog 형식의 CHANGELOG를 작성할 수 있다
- [ ] pre-release 버전의 의미를 이해한다

## 연습 문제

1. 이전 글에서 만든 프로젝트에 `v0.1.0` 태그를 붙이고 `git log --oneline --decorate`로 확인해 보세요.
2. 새 함수를 추가한 뒤 버전을 `0.2.0`으로 올리고, 변경 내용을 `CHANGELOG.md`에 기록해 보세요.
3. `setuptools-scm`을 설치하고 `pyproject.toml`에 동적 버전 설정을 추가해 보세요.

## 정리 · 다음 글

- SemVer는 MAJOR(호환성 깨짐).MINOR(새 기능).PATCH(버그 수정)입니다.
- `pyproject.toml`과 `__version__`은 항상 동기화되어야 합니다.
- Git 태그는 특정 커밋을 릴리스 시점으로 표시합니다.
- CHANGELOG는 사용자가 변경 사항을 확인하는 공식 문서입니다.
- 태그는 테스트 후에 만들어야 하며, 종종 실제 배포를 트리거합니다.

다음 글에서는 **CLI 패키지 만들기** — entry point와 `click`을 다룹니다.

## SemVer(Semantic Versioning) 상세 규칙

SemVer는 `MAJOR.MINOR.PATCH` 형식으로, 각 숫자가 변경의 성격을 전달합니다.

### 버전 올리기 판단 기준

| 변경 유형 | 올릴 자리 | 예시 |
|---|---|---|
| 기존 API 호환 깨짐 | MAJOR | `1.2.3 → 2.0.0` |
| 새 기능 추가 (하위 호환) | MINOR | `1.2.3 → 1.3.0` |
| 버그 수정 | PATCH | `1.2.3 → 1.2.4` |

### 실무 판단 흐름도

```text
변경사항이 있다
    │
    ▼
기존 사용자 코드가 깨지는가?
    ├── Yes → MAJOR 올리기
    │         - 함수/클래스 삭제
    │         - 매개변수 이름 변경
    │         - 반환 타입 변경
    │         - 예외 타입 변경
    │
    └── No → 새 기능인가?
              ├── Yes → MINOR 올리기
              │         - 새 함수 추가
              │         - 새 매개변수 (기본값 있음)
              │         - 새 클래스 추가
              │
              └── No → PATCH 올리기
                        - 버그 수정
                        - 성능 개선
                        - 내부 리팩터링
```

### PEP 440: Python의 버전 규칙

Python 패키지는 PEP 440 형식을 따라야 합니다. SemVer와 유사하지만 몇 가지 추가 표현이 있습니다.

```text
정식 릴리스:    1.0.0, 1.2.3
프리릴리스:     1.0.0a1 (alpha), 1.0.0b2 (beta), 1.0.0rc1 (release candidate)
포스트릴리스:   1.0.0.post1 (문서 수정 등)
개발 버전:     1.0.0.dev1 (아직 릴리스 전)

# 버전 비교 순서
1.0.0.dev1 < 1.0.0a1 < 1.0.0b1 < 1.0.0rc1 < 1.0.0 < 1.0.0.post1
```

```python
from packaging.version import Version

v1 = Version("1.0.0a1")
v2 = Version("1.0.0")
print(v1 < v2)  # True
print(v1.is_prerelease)  # True
```

## 버전을 코드에 기록하는 방법

### 방법 1: pyproject.toml에 정적 기록

```toml
[project]
version = "1.2.3"
```

```python
# src/acme_utils/__init__.py
__version__ = "1.2.3"  # pyproject.toml과 수동 동기화 필요
```

**단점**: 두 곳을 동시에 업데이트해야 합니다.

### 방법 2: 동적 버전 (Single Source of Truth)

```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "acme_utils.__version__"}
```

```python
# src/acme_utils/__init__.py
__version__ = "1.2.3"  # 이것이 유일한 버전 소스
```

### 방법 3: Git 태그에서 자동 추출 (setuptools-scm)

```toml
[build-system]
requires = ["setuptools>=68", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/acme_utils/_version.py"
version_scheme = "guess-next-dev"
```

```bash
git tag v1.2.3
python -m build
# 빌드 시 _version.py 자동 생성: __version__ = "1.2.3"

# 태그 이후 커밋이 있으면:
# __version__ = "1.2.4.dev3+g1234567"
```

### 방법 4: hatch-vcs

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/acme_utils/_version.py"
```

## CHANGELOG 관리

### Keep a Changelog 형식

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New `retry` decorator for HTTP calls

### Fixed
- Connection timeout handling in `Client.get()`

## [1.2.0] - 2024-03-15

### Added
- `Client.stream()` method for large responses
- Type stubs for all public APIs

### Changed
- Minimum Python version raised to 3.10

### Deprecated
- `Client.fetch()` - use `Client.get()` instead

## [1.1.0] - 2024-02-01

### Added
- `Config.from_env()` class method

[Unreleased]: https://github.com/acme/acme-utils/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/acme/acme-utils/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/acme/acme-utils/releases/tag/v1.1.0
```

### 자동 CHANGELOG 생성

```bash
# git-cliff: 커밋 메시지에서 CHANGELOG 생성
pip install git-cliff
git-cliff --output CHANGELOG.md

# Conventional Commits 형식을 따르면 자동화가 쉬움
# feat: add retry decorator
# fix: handle connection timeout
# BREAKING CHANGE: drop Python 3.9 support
```

## 릴리스 브랜치 전략

### 단순 전략 (소규모 프로젝트)

```text
main ─────●─────●─────●─────●──── (항상 릴리스 가능)
          v1.0  v1.1  v1.2  v2.0
```

### 릴리스 브랜치 (대규모 프로젝트)

```text
main ─────●─────●─────●─────●────
          │           │
          └── release/1.x ──●──●── (1.x 핫픽스)
                      │
                      └── release/2.x ──●── (2.x 핫픽스)
```

```bash
# 릴리스 절차
git checkout main
git pull
# CHANGELOG 업데이트, 버전 확인
git tag v1.3.0
git push --tags
# CI가 자동으로 PyPI 배포
```

## Deprecation 정책

API를 제거하기 전에 사용자에게 충분한 경고를 제공해야 합니다.

```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated, use new_function() instead. "
        "It will be removed in version 2.0.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_function()
```

### Deprecation 타임라인 예시

```text
v1.3.0: old_function()에 DeprecationWarning 추가
v1.4.0: 문서에서 old_function() 제거 (코드는 유지)
v2.0.0: old_function() 완전 제거
```

## CalVer: 날짜 기반 버전

일부 프로젝트는 SemVer 대신 CalVer(Calendar Versioning)를 사용합니다.

```text
형식 예시:
YYYY.MM.DD  → 2024.03.15
YYYY.MM     → 2024.3
YY.MM       → 24.3

사용 프로젝트:
- pip: 24.0, 24.1
- Ubuntu: 24.04
- Black: 24.3.0
```

CalVer는 릴리스 주기가 정기적이고 하위 호환성이 매번 보장되지 않는 프로젝트에 적합합니다. 라이브러리라면 SemVer가 사용자에게 더 명확한 신호를 줍니다.

## bump2version / bump-my-version 자동화

버전을 올릴 때 여러 파일을 동시에 수정하고 태그까지 자동으로 생성하는 도구입니다.

### 설정

```toml
# pyproject.toml
[tool.bumpversion]
current_version = "1.2.3"
commit = true
tag = true
tag_name = "v{new_version}"

[[tool.bumpversion.files]]
filename = "src/acme_utils/__init__.py"
search = '__version__ = "{current_version}"'
replace = '__version__ = "{new_version}"'

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'
```

### 사용법

```bash
pip install bump-my-version

# 패치 버전 올리기: 1.2.3 → 1.2.4
bump-my-version bump patch

# 마이너 버전: 1.2.3 → 1.3.0
bump-my-version bump minor

# 메이저 버전: 1.2.3 → 2.0.0
bump-my-version bump major

# 프리릴리스: 1.2.3 → 1.3.0a1
bump-my-version bump minor --new-version 1.3.0a1
```

```bash
# 실행 결과
$ bump-my-version bump patch
Bumping version from 1.2.3 to 1.2.4
  Updated src/acme_utils/__init__.py
  Updated pyproject.toml
  Created commit: Bump version: 1.2.3 → 1.2.4
  Created tag: v1.2.4
```

## GitHub Release와 연동

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 전체 히스토리 필요 (CHANGELOG 생성용)
      - name: Generate release notes
        run: |
          # 이전 태그와 현재 태그 사이의 커밋 추출
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^)
          git log --pretty=format:"- %s" ${PREV_TAG}..HEAD > release_notes.md
      - uses: softprops/action-gh-release@v2
        with:
          body_path: release_notes.md
          generate_release_notes: true
```

## 버전 호환성 선언과 지원 정책

### Python 버전 지원 정책

```text
NEP 29 (NumPy Enhancement Proposal 29) 기반 권장:
- 최신 Python 3개 마이너 버전 지원
- 현재(2024): 3.10, 3.11, 3.12

지원 종료 시 MAJOR 또는 MINOR 올리기:
- "Drop Python 3.9 support" → MINOR (일부 프로젝트)
- "Drop Python 3.9 support" → MAJOR (엄격한 프로젝트)
```

```toml
[project]
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

### CI에서 버전 매트릭스 테스트

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

## 실무 릴리스 시나리오

### 시나리오 1: 핫픽스 릴리스

```bash
# main에서 버그 발견, 즉시 패치 필요
git checkout main
git pull

# 수정 후
git add .
git commit -m "fix: handle null response in Client.get()"
bump-my-version bump patch  # 1.2.3 → 1.2.4
git push --tags
# CI가 자동 배포
```

### 시나리오 2: 기능 릴리스

```bash
# feature 브랜치에서 개발 완료 후 main 병합
git checkout main
git merge feature/retry-decorator

# CHANGELOG 업데이트
vim CHANGELOG.md  # [Unreleased] 내용을 새 버전으로 이동

bump-my-version bump minor  # 1.2.4 → 1.3.0
git push --tags
```

### 시나리오 3: 프리릴리스

```bash
# 큰 변경을 정식 전에 테스트
bump-my-version bump major --new-version 2.0.0a1
git push --tags
# 사용자: pip install acme-utils==2.0.0a1

# 피드백 반영 후
bump-my-version bump major --new-version 2.0.0b1
git push --tags

# 안정화 후 정식 릴리스
bump-my-version bump major --new-version 2.0.0
git push --tags
```

### 시나리오 4: 이전 버전 핫픽스

```bash
# v1.x 사용자를 위한 패치 (main은 이미 v2.x)
git checkout -b release/1.x v1.5.0
# 버그 수정
git cherry-pick <commit-hash>
bump-my-version bump patch  # 1.5.0 → 1.5.1
git push origin release/1.x --tags
```

## 의존성 버전 범위와 릴리스의 관계

패키지를 릴리스할 때 의존성의 버전 범위를 어떻게 설정하느냐가 사용자 경험에 직접 영향을 줍니다.

### 너무 좁은 범위의 문제

```toml
# 너무 좁음: 사용자 환경에서 충돌 가능성 높음
dependencies = ["httpx==0.27.2"]
```

사용자가 다른 패키지와 함께 설치할 때 정확히 `0.27.2`만 허용하면 버전 충돌이 빈번해집니다.

### 너무 넓은 범위의 문제

```toml
# 너무 넓음: 호환되지 않는 버전에서 런타임 에러
dependencies = ["httpx"]
```

상한 없이 모든 버전을 허용하면 미래의 메이저 업데이트에서 코드가 깨질 수 있습니다.

### 권장 범위

```toml
# 적절한 범위: 현재 메이저 내에서 유연하게
dependencies = [
    "httpx>=0.25,<1.0",
    "pydantic>=2.0,<3.0",
]
```

이 방식은 패치와 마이너 업데이트는 자동으로 수용하면서, 브레이킹 체인지가 예상되는 메이저 경계에서 차단합니다.

### 릴리스 시 의존성 테스트

```yaml
# CI에서 의존성 범위의 양 끝을 테스트
jobs:
  test-min-versions:
    steps:
      - run: pip install "httpx==0.25" "pydantic==2.0"  # 최소 지원 버전
      - run: pytest

  test-latest:
    steps:
      - run: pip install "httpx" "pydantic"  # 최신 버전
      - run: pytest
```

최소 버전과 최신 버전 모두에서 테스트를 통과해야 의존성 범위가 올바르다고 확신할 수 있습니다.

## 릴리스 후 모니터링

배포가 끝나도 릴리스는 완료되지 않았습니다. 사용자 반응을 모니터링해야 합니다.

```text
확인 항목:
□ GitHub Issues에 새 버그 리포트가 없는가
□ PyPI 다운로드 수가 정상 증가하는가
□ 사내 서비스에서 업그레이드 후 에러율 변화가 없는가
□ Dependabot PR이 이 버전에서 실패하지 않는가
```

```bash
# 릴리스 후 24시간 이내 Issues 확인
gh issue list --label bug --since "24 hours ago"
```

문제가 발견되면 즉시 패치 릴리스를 준비하거나, 심각한 경우 yank 처리를 고려합니다.

### 롤백 전략

```bash
# 사용자 측 롤백
pip install acme-utils==1.2.3  # 이전 안정 버전으로 되돌리기

# 패키지 관리자 측: yank + 핫픽스
# 1. PyPI에서 문제 버전 yank
# 2. 수정 후 새 패치 버전 릴리스
# 3. 사용자에게 업그레이드 안내
```

신규 릴리스 후 문제가 심각하면 yank는 즉시 실행하되, 완전 삭제보다는 핫픽스 릴리스로 대응하는 것이 표준입니다.

## 처음 질문으로 돌아가기

- **SemVer의 MAJOR.MINOR.PATCH는 언제 올려야 할까요?**
  - 기존 사용자 코드가 깨지면 MAJOR, 하위 호환되는 새 기능이면 MINOR, 버그 수정이면 PATCH를 올립니다. "사용자 코드가 깨지는가?"가 판단의 첫 번째 질문이고, 함수 삭제, 매개변수 이름 변경, 반환 타입 변경이 대표적인 브레이킹 체인지입니다.

- **버전은 코드의 어디에 기록해야 할까요?**
  - 가장 권장되는 방식은 Git 태그를 단일 출처로 사용하고 `setuptools-scm`이나 `hatch-vcs`로 빌드 시 자동 추출하는 것입니다. 수동 관리가 필요하다면 `__init__.py`의 `__version__`을 `pyproject.toml`의 `[tool.setuptools.dynamic]`으로 읽어오는 방식이 두 곳의 불일치를 방지합니다.

- **CHANGELOG는 어떻게 관리할까요?**
  - Keep a Changelog 형식으로 `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed` 카테고리를 사용합니다. Conventional Commits를 따르면 `git-cliff` 같은 도구로 자동 생성할 수 있습니다. 각 릴리스에 비교 링크를 달아 변경 범위를 한눈에 파악할 수 있게 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- **Python Package 101 (6/10): 버전 관리와 릴리스 (현재 글)**
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
- [setuptools-scm](https://setuptools-scm.readthedocs.io/)

Tags: Python, Packaging, PyPI, pyproject.toml
