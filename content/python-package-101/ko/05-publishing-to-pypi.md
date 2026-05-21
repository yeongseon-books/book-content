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

![Python Package 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/05/05-01-mental-model.ko.png)
*Python Package 101 5장 흐름 개요*

## 먼저 던지는 질문

- PyPI와 TestPyPI는 무엇이 다를까요?
- `twine`은 정확히 어떤 역할을 할까요?
- API 토큰은 어떻게 만들고 관리할까요?

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

**Before (Git에서 직접 설치)**

```bash
pip install git+https://github.com/team/mylib.git@main
# → behavior changes when the branch changes
# → slow install (clone + build)
# → hard to pin versions
```

**After (PyPI에서 설치)**

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

## PyPI 업로드 전체 흐름

패키지를 PyPI에 배포하는 과정은 빌드 → 검증 → 업로드 → 확인의 네 단계로 이루어집니다.

```text
개발 완료
    │
    ▼
python -m build          # sdist + wheel 생성
    │
    ▼
python -m twine check dist/*   # 메타데이터 검증
    │
    ▼
python -m twine upload --repository testpypi dist/*  # TestPyPI에 먼저 업로드
    │
    ▼
pip install --index-url https://test.pypi.org/simple/ acme-utils  # 설치 확인
    │
    ▼
python -m twine upload dist/*   # 실제 PyPI 업로드
    │
    ▼
pip install acme-utils          # 최종 확인
```

## TestPyPI vs PyPI

| 항목 | TestPyPI | PyPI |
|---|---|---|
| URL | https://test.pypi.org | https://pypi.org |
| 용도 | 업로드 흐름 테스트 | 실제 배포 |
| 계정 | 별도 계정 필요 | 별도 계정 필요 |
| 패키지 수명 | 주기적 삭제 가능 | 영구 보관 |
| 의존성 | TestPyPI의 패키지만 참조 가능 | 전체 패키지 참조 |

### TestPyPI 사용 시 주의사항

```bash
# TestPyPI에서 설치할 때 의존성은 실제 PyPI에서 가져와야 함
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    acme-utils
```

TestPyPI에 올린 패키지의 의존성(`httpx`, `pydantic` 등)은 TestPyPI에 없으므로 `--extra-index-url`로 실제 PyPI를 추가해야 합니다.

## twine 상세 사용법

`twine`은 PyPI에 패키지를 안전하게 업로드하는 도구입니다. HTTPS를 강제하고, 메타데이터를 사전 검증합니다.

### twine check: 업로드 전 검증

```bash
python -m twine check dist/*
```

```text
Checking dist/acme_utils-0.1.0.tar.gz: PASSED
Checking dist/acme_utils-0.1.0-py3-none-any.whl: PASSED
```

twine check가 잡아내는 문제:
- README 렌더링 오류 (Markdown/RST 문법)
- 필수 메타데이터 누락
- 잘못된 classifier
- 유효하지 않은 URL

### twine upload: 업로드 실행

```bash
# TestPyPI에 업로드
python -m twine upload --repository testpypi dist/*

# 실제 PyPI에 업로드
python -m twine upload dist/*

# 특정 파일만 업로드
python -m twine upload dist/acme_utils-0.1.0-py3-none-any.whl
```

### .pypirc 설정 파일

```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxx

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxx
```

**보안 주의**: `.pypirc`에 토큰을 직접 넣는 대신, 환경 변수나 keyring을 사용하는 것이 더 안전합니다.

## API 토큰 관리

### PyPI 토큰 생성 절차

```text
1. https://pypi.org/manage/account/ 접속
2. "API tokens" 섹션
3. "Add API token" 클릭
4. Scope 선택:
   - "Entire account" (모든 프로젝트) — 초기 업로드 시
   - "Project: acme-utils" (특정 프로젝트) — 이후 업데이트 시
5. 토큰 복사 (pypi-로 시작)
```

### 토큰 저장 방식별 비교

| 방식 | 보안 | 편의성 | 적합한 상황 |
|---|---|---|---|
| `.pypirc` 파일 | 낮음 | 높음 | 개인 개발 머신 |
| 환경 변수 | 중간 | 중간 | CI/CD |
| keyring | 높음 | 중간 | 팀 환경 |
| GitHub Secrets | 높음 | 높음 | GitHub Actions |

### 환경 변수로 토큰 전달

```bash
# .pypirc 없이 환경 변수로 인증
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxxxxxxxxxxxxxxxxxxxx
python -m twine upload dist/*
```

### keyring 사용

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# 프롬프트에서 토큰 입력

# 이후 twine은 자동으로 keyring에서 토큰을 가져옴
python -m twine upload dist/*
```

## GitHub Actions 자동 배포

태그를 푸시하면 자동으로 PyPI에 배포하는 워크플로우입니다.

### Trusted Publisher (권장)

PyPI의 Trusted Publisher 기능을 사용하면 토큰 없이도 GitHub Actions에서 직접 업로드할 수 있습니다.

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Trusted Publisher에 필요
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # Trusted Publisher: 토큰 설정 불필요!
```

### Trusted Publisher 설정 절차

```text
1. PyPI에서 프로젝트 설정 → "Publishing" 탭
2. "Add a new publisher" 클릭
3. GitHub 저장소 정보 입력:
   - Owner: acme
   - Repository: acme-utils
   - Workflow name: publish.yml
   - Environment: (비워둠 또는 'release')
4. 저장
```

이 방식은 토큰 유출 위험이 없고, GitHub의 OIDC 토큰으로 인증합니다.

### 토큰 기반 배포 (대안)

```yaml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: python -m twine check dist/*
      - run: python -m twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## 배포 후 확인 절차

```bash
# 1. PyPI 페이지 확인
# https://pypi.org/project/acme-utils/0.1.0/

# 2. 깨끗한 환경에서 설치 테스트
python -m venv /tmp/test-deploy
source /tmp/test-deploy/bin/activate
pip install acme-utils==0.1.0
python -c "import acme_utils; print(acme_utils.__version__)"
# 0.1.0

# 3. CLI entry point 확인 (있는 경우)
acme --version
```

## 배포 실수 대응

### 같은 버전을 다시 올릴 수 없다

```bash
python -m twine upload dist/*
# HTTPError: 400 Bad Request
# "File already exists"
```

PyPI는 한 번 올린 버전을 덮어쓸 수 없습니다. 실수로 잘못된 버전을 올렸다면:

1. **버그 수정**: 새 패치 버전(`0.1.1`)으로 올립니다
2. **보안 문제**: PyPI에서 해당 버전을 yank합니다
3. **완전 삭제**: PyPI 지원팀에 요청 (매우 드문 경우)

### yank: 버전 숨기기

```bash
# PyPI 웹 UI에서 특정 버전을 yank
# 또는 API 사용
# yank된 버전은 명시적으로 지정하지 않으면 설치되지 않음
pip install acme-utils         # yanked 버전 건너뜀
pip install acme-utils==0.1.0  # yanked여도 명시하면 설치 가능 (경고 출력)
```

## Private PyPI 서버

사내 패키지를 공개 PyPI에 올릴 수 없을 때 사설 저장소를 사용합니다.

### 간단한 방법: devpi

```bash
pip install devpi-server devpi-client
devpi-server --init
devpi-server --start --port 3141

# 사용
pip install --index-url http://localhost:3141/root/pypi/+simple/ acme-utils
```

### AWS CodeArtifact

```bash
# AWS CodeArtifact에서 토큰 획득
aws codeartifact get-authorization-token --domain mycompany --query authorizationToken --output text

# pip 설정
pip install --index-url https://aws:TOKEN@mycompany-123456789.d.codeartifact.us-east-1.amazonaws.com/pypi/internal/simple/ acme-utils
```

### pip.conf로 기본 저장소 설정

```ini
# ~/.config/pip/pip.conf (Linux)
[global]
extra-index-url = https://pypi.mycompany.com/simple/
trusted-host = pypi.mycompany.com
```

## 릴리스 자동화 전체 파이프라인

실무에서 릴리스는 수동 명령이 아닌 자동화된 파이프라인으로 운영합니다.

### 릴리스 흐름 예시

```text
1. 개발자: git tag v0.2.0 && git push --tags
2. GitHub Actions: 태그 감지 → 빌드 → 테스트 → 배포
3. PyPI: 새 버전 등록
4. GitHub: Release 페이지 자동 생성
```

### 전체 워크플로우 (테스트 + 배포 + 릴리스)

```yaml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest -q
      - run: ruff check .
      - run: mypy src

  publish:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write  # GitHub Release 생성용
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: dist/*
```

### 릴리스 체크리스트

```text
배포 전:
□ CHANGELOG.md 업데이트
□ 버전 번호 확인 (pyproject.toml 또는 Git 태그)
□ 모든 테스트 통과
□ TestPyPI에서 설치 확인
□ README 렌더링 확인

배포 후:
□ PyPI 페이지에서 메타데이터 확인
□ pip install로 설치 확인
□ import + __version__ 출력 확인
□ GitHub Release 노트 확인
□ 문서 사이트 업데이트 확인
```

## 업로드 문제 해결

### 문제 1: 파일 크기 초과

```text
HTTPError: 400 Bad Request
"File too large"
```

PyPI의 기본 파일 크기 제한은 100MB입니다. 대용량 모델이나 데이터를 포함하지 말고, 별도 다운로드 메커니즘을 사용합니다.

### 문제 2: README 렌더링 오류

```bash
# 로컬에서 README 렌더링 미리 확인
pip install readme-renderer
python -m readme_renderer README.md -o /tmp/readme.html
# 브라우저에서 /tmp/readme.html 열어 확인
```

### 문제 3: 네트워크 타임아웃

```bash
# 재시도 옵션 추가
python -m twine upload --verbose --disable-progress-bar dist/*

# 또는 프록시 설정
export HTTPS_PROXY=http://proxy.company.com:8080
python -m twine upload dist/*
```

### 문제 4: 이미 존재하는 버전

```bash
# 이미 업로드된 버전을 다시 올리려 하면 에러 발생
# 해결: 버전 번호를 올려야 함
# pyproject.toml: version = "0.1.1"
# 또는 post-release: version = "0.1.0.post1"
```

## PyPI 프로젝트 페이지 최적화

PyPI 페이지는 패키지의 첫인상입니다. 메타데이터를 잘 채우면 검색 노출과 신뢰도가 올라갑니다.

```toml
[project]
name = "acme-utils"
description = "Production-ready utility library for Acme microservices"
readme = "README.md"
license = {text = "MIT"}
keywords = ["utility", "microservices", "acme"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/acme/acme-utils"
Documentation = "https://acme.github.io/acme-utils"
Changelog = "https://github.com/acme/acme-utils/blob/main/CHANGELOG.md"
"Bug Tracker" = "https://github.com/acme/acme-utils/issues"
```

### README 구조 권장

```markdown
# acme-utils

Production-ready utility library for Acme microservices.

## Installation

pip install acme-utils

## Quick Start

(3-5줄 코드 예시)

## Features

- Feature 1
- Feature 2

## Documentation

Full docs: https://acme.github.io/acme-utils

## License

MIT
```

### PyPI 다운로드 통계 확인

```bash
pip install pypistats
pypistats overall acme-utils        # 전체 다운로드 수
pypistats python_minor acme-utils   # Python 버전별 다운로드
pypistats system acme-utils         # OS별 다운로드
```

패키지의 사용 현황을 파악하면 어떤 Python 버전과 플랫폼을 지원해야 하는지 데이터 기반으로 판단할 수 있습니다.

## 처음 질문으로 돌아가기

- **PyPI와 TestPyPI는 무엇이 다를까요?**
  - TestPyPI는 업로드 흐름을 검증하기 위한 별도 환경으로 계정과 토큰이 PyPI와 독립되어 있습니다. TestPyPI에 올린 패키지는 주기적으로 삭제될 수 있고, 의존성 해결 시 실제 PyPI의 패키지를 참조하지 못합니다. 실제 배포 전 리허설 용도로 사용합니다.

- **`twine`은 정확히 어떤 역할을 할까요?**
  - twine은 빌드된 sdist/wheel을 PyPI에 HTTPS로 업로드하는 도구입니다. 업로드 전에 `twine check`으로 메타데이터 유효성, README 렌더링, classifier 정확성을 검증합니다. `setup.py upload`와 달리 빌드와 업로드를 분리하여 보안과 재현성을 보장합니다.

- **API 토큰은 어떻게 만들고 관리할까요?**
  - PyPI 계정 설정에서 프로젝트 범위를 지정하여 토큰을 생성합니다. 로컬에서는 keyring, CI에서는 GitHub Secrets나 Trusted Publisher를 사용합니다. Trusted Publisher는 OIDC 기반으로 토큰 자체를 불필요하게 만들어 유출 위험을 근본적으로 제거합니다.

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging User Guide - Uploading](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
- [PyPI - Publishing with Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [twine documentation](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
