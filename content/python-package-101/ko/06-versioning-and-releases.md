---
title: 버전 관리와 릴리스
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
last_reviewed: '2026-05-12'
seo_description: SemVer는 버전 번호에 의미를 부여하는 규칙이고, Git 태그는 특정 커밋을 릴리스 시점으로 표시하는 것입니다.
---

# 버전 관리와 릴리스

패키지를 한 번 배포하고 나면, 그다음부터는 “무엇이 바뀌었는지”를 사용자에게 일관되게 알려 주는 일이 중요해집니다. 버전 번호, Git 태그, CHANGELOG는 모두 그 신호 체계를 만드는 도구입니다. 이 글은 Python Package 101 시리즈의 6번째 글입니다. 여기서는 SemVer 규칙, 버전을 코드와 메타데이터에 동기화하는 방법, 그리고 릴리스 기록을 남기는 기본 흐름을 정리하겠습니다.

## 이 글에서 다룰 문제

- SemVer의 MAJOR.MINOR.PATCH는 언제 올려야 할까요?
- 버전은 코드의 어디에 기록해야 할까요?
- Git 태그와 릴리스는 어떤 관계일까요?
- CHANGELOG는 왜 필요하고 어떻게 써야 할까요?

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

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- **버전 관리와 릴리스 (현재 글)**
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
- [setuptools-scm](https://setuptools-scm.readthedocs.io/)

Tags: Python, Versioning, SemVer, Release, CHANGELOG, Git Tag
