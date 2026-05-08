
# 버전 관리와 릴리스

> Python Package 101 시리즈 (6/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- SemVer(Semantic Versioning)의 MAJOR.MINOR.PATCH는 각각 언제 올릴까요?
- 버전은 코드 어디에 적어야 할까요?
- Git 태그와 릴리스의 관계는 무엇일까요?
- CHANGELOG는 왜 필요하고 어떻게 쓸까요?

> SemVer는 버전 번호에 의미를 부여하는 규칙이고, Git 태그는 특정 커밋을 릴리스 시점으로 표시하는 것입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- SemVer 규칙과 올바른 버전 업 시점
- pyproject.toml과 `__version__`의 버전 동기화
- Git 태그로 릴리스를 표시하고 관리하는 법
- CHANGELOG 작성법과 자동화 도구

## 왜 중요한가

패키지를 업데이트했을 때 사용자는 "이 업데이트가 안전한가?"를 판단해야 합니다. 버전 번호가 그 기준이 됩니다. 의미 없는 버전을 올리면 사용자가 혼란스럽고, 호환성을 깨는 변경을 PATCH로 올리면 사용자의 코드가 깨집니다.

> `pip install mylib --upgrade`로 패치 버전을 올렸는데 API가 바뀌어서 프로덕션이 깨졌습니다. `0.2.3 → 0.2.4`라서 안전할 줄 알았는데, 함수 시그니처가 달라졌습니다.

## Mental Model

> SemVer는 신호등입니다. PATCH(초록)은 안전하게 올릴 수 있고, MINOR(노랑)은 새 기능이 추가되었지만 기존은 유지되고, MAJOR(빨강)은 기존 코드를 수정해야 할 수 있습니다.

```text
MAJOR . MINOR . PATCH
  1   .   2   .   3

PATCH  (1.2.3 → 1.2.4): 버그 수정, 기존 API 변경 없음
MINOR  (1.2.4 → 1.3.0): 새 기능 추가, 기존 API 유지
MAJOR  (1.3.0 → 2.0.0): 기존 API 변경/삭제 (호환성 깨짐)
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| SemVer | 의미 기반 버전 관리 규칙 | `1.2.3` |
| pre-release | 정식 릴리스 전 테스트 버전 | `1.0.0rc1`, `1.0.0a1` |
| Git tag | 특정 커밋에 이름을 붙이는 기능 | `git tag v1.0.0` |
| CHANGELOG | 버전별 변경 사항을 기록한 문서 | `CHANGELOG.md` |
| single source of truth | 버전이 하나의 출처에서만 관리됨 | pyproject.toml 또는 `__version__` |

## Before / After

**Before (버전 관리 없음)**

```text
# commit message만으로 버전 관리
"fixed bug"
"added feature"
"more fixes"
# → 어떤 커밋이 어떤 릴리스인지 알 수 없음
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

### Step 1. pyproject.toml에 버전 설정

```toml
[project]
name = "mylib"
version = "0.1.0"
```

### Step 2. __version__ 동기화

```python
# src/mylib/__init__.py
"""mylib - A sample Python package."""
__version__ = "0.1.0"
```

```python
# 사용자가 확인하는 법
import mylib
print(mylib.__version__)  # 0.1.0
```

### Step 3. Git 태그로 릴리스 표시

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags

# 태그 목록 확인
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

### Step 5. 버전 업 후 릴리스

```bash
# pyproject.toml: version = "0.2.0"
# src/mylib/__init__.py: __version__ = "0.2.0"

git add .
git commit -m "Release v0.2.0: add string utilities"
git tag v0.2.0
python -m build
twine upload dist/*
```

## 이 코드에서 봐야 할 것

- pyproject.toml의 `version`과 `__version__`이 항상 일치해야 합니다
- Git 태그에 `v` 접두어를 붙이는 것이 관례입니다 (`v0.1.0`)
- CHANGELOG는 [Keep a Changelog](https://keepachangelog.com/) 형식을 따르는 것이 표준입니다
- `--tags` 옵션 없이 push하면 태그가 원격에 올라가지 않습니다

## 자주 하는 실수

### 실수 1. pyproject.toml과 __version__이 다르다

두 곳의 버전이 다르면 `pip show`와 `import` 결과가 달라집니다. 하나의 출처에서 관리하세요.

### 실수 2. 호환성을 깨는 변경을 PATCH로 올린다

함수 시그니처 변경, 반환값 변경, 필수 인자 추가 등은 MAJOR 업입니다.

### 실수 3. 0.x 버전에서 안정성을 기대한다

SemVer에서 `0.x.y`는 초기 개발 단계이며 언제든 API가 바뀔 수 있음을 의미합니다. 1.0.0이 첫 안정 릴리스입니다.

### 실수 4. CHANGELOG를 쓰지 않는다

사용자는 "이번 업데이트에 무엇이 바뀌었는가?"를 알아야 합니다. Git log만으로는 부족합니다.

### 실수 5. 태그를 먼저 올리고 테스트한다

태그는 빌드 + 테스트가 통과한 후에 붙입니다. CI/CD에서는 태그 push가 배포 트리거이므로, 미리 붙이면 깨진 버전이 배포됩니다.

## 실무 적용

- **CI/CD 트리거**: Git 태그 push → 자동 빌드 → 자동 PyPI 업로드
- **Dependabot/Renovate**: 의존하는 패키지의 새 버전을 자동으로 PR 생성
- **동적 버전 관리**: `setuptools-scm`이 Git 태그에서 자동으로 버전을 추출합니다
- **pre-release**: `1.0.0a1 → 1.0.0b1 → 1.0.0rc1 → 1.0.0`으로 단계적 릴리스
- **GitHub Releases**: Git 태그와 CHANGELOG를 연결하여 릴리스 노트를 자동 생성합니다

## 실무에서는 이렇게 생각한다

버전 관리에서 가장 어려운 것은 "이 변경이 MINOR인가 MAJOR인가?"를 판단하는 것입니다. 기준은 단순합니다: **기존 사용자의 코드가 수정 없이 동작하면 MINOR, 수정이 필요하면 MAJOR**입니다.

버전을 두 곳에서 관리하는 것이 번거롭다면 `setuptools-scm`을 쓰세요. Git 태그(`v0.1.0`)만 붙이면 pyproject.toml의 버전이 자동으로 결정됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **SemVer** — 주.부.수 의미를 팀에서 합의합니다.
- **Pre-release** — alpha/beta/rc로 호환성 신호를 보냅니다.
- **자동화** — tag → CI → 빌드 → 배포 파이프라인을 자동화합니다.
- **Deprecation** — 최소 한 마이너 버전 전 deprecation 경고를 둡니다.
- **문서 동기화** — 버전과 문서를 함께 릴리스합니다.

## 체크리스트

- [ ] SemVer의 MAJOR.MINOR.PATCH 각각의 기준을 설명할 수 있다
- [ ] pyproject.toml과 `__version__`을 동기화하는 방법을 알고 있다
- [ ] Git 태그로 릴리스를 표시할 수 있다
- [ ] CHANGELOG를 Keep a Changelog 형식으로 작성할 수 있다
- [ ] pre-release 버전의 의미를 알고 있다

## 연습 문제

1. 이전 글에서 만든 프로젝트에 `v0.1.0` 태그를 붙이고, `git log --oneline --decorate`로 확인해보세요.
2. 새 함수를 추가하고 버전을 `0.2.0`으로 올린 뒤, CHANGELOG.md에 변경 사항을 기록해보세요.
3. `setuptools-scm`을 설치하고 pyproject.toml에서 동적 버전을 설정해보세요.

## 정리 · 다음 글

- SemVer는 MAJOR(호환성 깨짐).MINOR(새 기능).PATCH(버그 수정)입니다.
- 버전은 pyproject.toml과 `__version__`에서 동기화해야 합니다.
- Git 태그는 특정 커밋을 릴리스 시점으로 표시합니다.
- CHANGELOG는 사용자가 변경 사항을 확인하는 공식 문서입니다.
- 테스트 통과 후에 태그를 붙이고, 태그가 배포를 트리거합니다.

다음 글에서는 **CLI 패키지 만들기** — entry point와 click을 다룹니다.

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

## 참고 자료

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
- [setuptools-scm](https://setuptools-scm.readthedocs.io/)

Tags: Python, Versioning, SemVer, Release, CHANGELOG, Git Tag

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
