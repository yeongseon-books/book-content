---
title: "Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements"
series: python-package-101
episode: 3
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
- venv
- pip
- uv
- Dependencies
- Virtual Environment
last_reviewed: '2026-05-15'
seo_description: 가상환경은 프로젝트마다 독립된 패키지 공간을 만드는 것이고, 의존성 관리는 어떤 패키지의 어떤 버전이 필요한지를 기록하는 것입니다.
---

# Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements

패키지를 만들었다면 이제 그 패키지가 어떤 환경에서 어떤 버전의 라이브러리와 함께 동작하는지 관리해야 합니다. 같은 코드라도 설치된 패키지 버전이 다르면 전혀 다른 결과가 나올 수 있기 때문입니다.

이 글은 Python Package 101 시리즈의 3번째 글입니다. 여기서는 가상환경이 왜 필요한지, `requirements.txt`와 `pyproject.toml`의 역할이 어떻게 다른지, 그리고 `uv`가 왜 빠르게 표준 도구가 되고 있는지 정리하겠습니다.

![Python Package 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/03/03-01-mental-model.ko.png)
*Python Package 101 3장 흐름 개요*

## 먼저 던지는 질문

- 왜 가상환경이 필요하고 어떻게 동작할까요?
- `pip freeze`와 `requirements.txt`는 어떤 관계일까요?
- `uv`는 `pip`와 무엇이 다를까요?

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

## 적용 전후 비교
**Before (시스템 Python 공유)**

```bash
pip install requests==2.28   # for Project A
pip install requests==2.31   # for Project B → A breaks
```

**After (격리된 가상 환경)**

```bash
cd project-a && python -m venv .venv && source .venv/bin/activate
pip install requests==2.28   # project-a only

cd project-b && python -m venv .venv && source .venv/bin/activate
pip install requests==2.31   # project-b only
```

## 단계별 실습

### 단계 1. 가상환경 만들기

```bash
cd ~/practice/mylib-project
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

which python
# /home/user/practice/mylib-project/.venv/bin/python
```

### 단계 2. 패키지 설치와 freeze

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

### 단계 3. `requirements.txt`로 재현하기

```bash
# Install the same packages in another environment
deactivate
python -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
pip list  # same packages, same versions
```

### 단계 4. `pyproject.toml`의 `dependencies`

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

### 단계 5. `uv`로 더 빠르게 관리하기

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

## 가상 환경 내부 구조

`python -m venv .venv`를 실행하면 실제로 어떤 디렉터리와 파일이 생성되는지 살펴보겠습니다.

```bash
python -m venv .venv
tree .venv -L 2
```

```text
.venv/
├── bin/                         # (Windows: Scripts/)
│   ├── activate                 # 셸 활성화 스크립트
│   ├── activate.fish
│   ├── pip                      # venv 전용 pip
│   ├── pip3
│   ├── python -> python3.11     # 시스템 Python 심볼릭 링크
│   └── python3
├── include/                     # C 확장 빌드용 헤더
├── lib/
│   └── python3.11/
│       └── site-packages/       # 이 venv의 패키지 설치 경로
├── lib64 -> lib
└── pyvenv.cfg                   # venv 설정
```

```ini
# pyvenv.cfg 내용
home = /usr/bin
include-system-site-packages = false
version = 3.11.9
executable = /usr/bin/python3.11
command = /usr/bin/python3.11 -m venv .venv
```

### activate가 실제로 하는 일

```bash
# activate 스크립트의 핵심 동작 (단순화):
export VIRTUAL_ENV="/path/to/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PS1="(.venv) $PS1"

# 비활성화
deactivate  # PATH와 PS1을 원래대로 복원
```

`activate`는 `PATH`의 맨 앞에 `.venv/bin`을 추가합니다. 이후 `python`이나 `pip`을 실행하면 시스템 것이 아닌 venv 안의 바이너리가 실행됩니다.

### activate 없이 venv 사용하기

```bash
# activate 없이도 직접 경로를 지정하면 동일하게 동작합니다
.venv/bin/python -m pip install requests
.venv/bin/python main.py

# CI에서는 activate 대신 직접 경로를 쓰는 경우가 많습니다
```

## pip의 의존성 해결 알고리즘

pip 20.3+는 backtracking resolver를 사용합니다. 이 해결기는 모든 패키지의 버전 요구사항이 동시에 만족되는 조합을 찾습니다.

### 해결 과정 시각화

```bash
pip install "packageA>=1.0" "packageB>=2.0" --verbose 2>&1 | grep -i "trying\|conflict"
```

```text
해결 과정:
1. packageA>=1.0 → 최신 버전 1.5 선택
2. packageA 1.5의 의존성: shared-lib>=3.0
3. packageB>=2.0 → 최신 버전 2.3 선택
4. packageB 2.3의 의존성: shared-lib>=2.0,<3.0
5. 충돌! shared-lib>=3.0 AND <3.0은 불가
6. 백트래킹: packageA 1.4 시도
7. packageA 1.4의 의존성: shared-lib>=2.5
8. shared-lib>=2.5 AND >=2.0,<3.0 → shared-lib 2.9 선택
9. 해결 완료!
```

### 의존성 충돌 디버깅

```bash
# 충돌 원인 확인
pip install "packageA>=1.0" "packageB>=2.0" --dry-run

# 의존성 트리 시각화
pip install pipdeptree
pipdeptree --warn fail  # 충돌이 있으면 에러 반환
pipdeptree -r -p shared-lib  # shared-lib를 의존하는 패키지 역추적
```

## requirements 파일 전략

### requirements.txt vs pyproject.toml dependencies

| 용도 | 파일 | 특징 |
|---|---|---|
| 라이브러리 의존성 | `pyproject.toml` `[project.dependencies]` | 범위 지정 (`>=1.0,<2.0`) |
| 애플리케이션 lock | `requirements.txt` | 정확한 버전 고정 (`==1.2.3`) |
| 개발 도구 | `pyproject.toml` `[project.optional-dependencies]` | 그룹별 관리 |

### 계층화된 requirements 구조

```text
requirements/
├── base.txt          # 프로덕션 의존성
├── dev.txt           # 개발 도구 (base 포함)
├── test.txt          # 테스트 전용 (base 포함)
└── ci.txt            # CI 전용 (test + lint)
```

```text
# requirements/base.txt
httpx==0.27.2
pydantic==2.8.2
sqlalchemy==2.0.31

# requirements/dev.txt
-r base.txt
pytest==8.3.2
ruff==0.5.5
mypy==1.11.0
ipython==8.26.0

# requirements/test.txt
-r base.txt
pytest==8.3.2
pytest-cov==5.0.0
factory-boy==3.3.0
```

### pip freeze의 함정

```bash
pip freeze > requirements.txt
```

이 방식의 문제점:
1. 직접 의존성과 간접 의존성이 구분되지 않습니다
2. 개발 도구까지 모두 포함됩니다
3. 나중에 어떤 패키지를 제거해도 되는지 판단하기 어렵습니다

```bash
# 더 나은 방식: pip-compile 사용
pip install pip-tools
echo "httpx>=0.27" > requirements.in
echo "pydantic>=2.5" >> requirements.in
pip-compile requirements.in -o requirements.txt
```

```text
# requirements.txt (pip-compile 생성)
# This file is autogenerated by pip-compile
anyio==4.4.0
    # via httpx
certifi==2024.7.4
    # via httpx
httpcore==1.0.5
    # via httpx
httpx==0.27.2
    # via -r requirements.in
pydantic==2.8.2
    # via -r requirements.in
# ... 간접 의존성에 출처가 명시됨
```

## uv: 차세대 패키지 관리 도구

uv는 Rust로 작성된 패키지 관리 도구로, pip보다 10-100배 빠른 의존성 해결과 설치를 제공합니다.

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# venv 생성 (pip보다 빠름)
uv venv .venv

# 패키지 설치
uv pip install httpx pydantic

# requirements.txt에서 설치
uv pip install -r requirements.txt

# lock 파일 생성
uv pip compile requirements.in -o requirements.txt
```

### uv vs pip 성능 비교

```bash
# 같은 requirements.txt로 설치 시간 비교 (대략적)
time pip install -r requirements.txt     # ~15초
time uv pip install -r requirements.txt  # ~1.5초
```

### uv의 프로젝트 관리 모드

```bash
# uv를 프로젝트 매니저로 사용 (pyproject.toml 기반)
uv init myproject
cd myproject
uv add httpx pydantic      # 의존성 추가 + lock
uv remove pydantic         # 의존성 제거 + lock 업데이트
uv sync                    # lock 기반 동기화
uv run pytest              # venv 안에서 명령 실행
```

```text
myproject/
├── pyproject.toml
├── uv.lock              # 정확한 버전 + 해시 lock
└── src/
    └── myproject/
```

## 의존성 버전 지정 전략

```toml
[project]
dependencies = [
    # 최소 버전만 지정 (라이브러리용)
    "httpx>=0.27",
    
    # 상한 포함 (호환 범위)
    "pydantic>=2.5,<3.0",
    
    # 호환 릴리스 (~= 연산자)
    "sqlalchemy~=2.0",      # >=2.0, <3.0과 동일
    
    # 정확한 버전 (드문 경우)
    "legacy-lib==1.2.3",
    
    # 환경 마커
    "tomli>=2.0; python_version < '3.11'",
]
```

### 라이브러리 vs 애플리케이션 전략

| | 라이브러리 | 애플리케이션 |
|---|---|---|
| 버전 지정 | 느슨하게 (`>=1.0,<3.0`) | 정확하게 (`==1.2.3`) |
| lock 파일 | 없음 | 필수 |
| 이유 | 사용자 환경 유연성 | 재현 가능한 배포 |

## GitHub Actions에서 의존성 캐싱

```yaml
name: ci
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"                    # pip 캐시 자동 활성화
          cache-dependency-path: |
            requirements/dev.txt
            pyproject.toml
      - run: python -m pip install -e ".[dev]"
      - run: pytest
```

캐시를 활성화하면 의존성이 변경되지 않은 경우 설치 시간이 수 초로 줄어듭니다.

## 보안: 의존성 취약점 관리

설치한 패키지에 보안 취약점이 있을 수 있습니다. 정기적인 점검이 필요합니다.

### pip-audit로 취약점 스캔

```bash
pip install pip-audit
pip-audit
```

```text
Name       Version  ID             Fix Versions
---------- -------- -------------- ------------
cryptography 41.0.0 GHSA-xxxx-yyyy >=41.0.2
urllib3      1.26.15 PYSEC-2023-212 >=1.26.18,>=2.0.7
```

### GitHub Dependabot 설정

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### 의존성 해시 검증

```bash
# requirements.txt에 해시 포함 (supply chain 보호)
pip-compile --generate-hashes requirements.in
```

```text
# requirements.txt
httpx==0.27.2 \
    --hash=sha256:abc123... \
    --hash=sha256:def456...
```

해시가 포함된 requirements.txt를 사용하면 패키지가 변조되었을 때 설치를 거부합니다.

## 가상 환경 관리 도구 비교

| 도구 | 특징 | 적합한 상황 |
|---|---|---|
| `python -m venv` | 표준 라이브러리, 추가 설치 불필요 | 간단한 프로젝트, CI |
| `virtualenv` | venv보다 빠름, 더 많은 옵션 | venv의 기능이 부족할 때 |
| `uv venv` | Rust 기반, 가장 빠름 | 속도가 중요할 때 |
| `conda` | Python 외 바이너리도 관리 | 데이터 과학, C 라이브러리 |
| `poetry` | lock + venv + 빌드 통합 | 올인원 도구 선호 시 |
| `pdm` | PEP 582 지원, 모던 | 표준 준수 + 편의성 |

### Poetry 기본 사용법

```bash
poetry init                    # pyproject.toml 생성
poetry add httpx               # 의존성 추가 + lock
poetry add --group dev pytest  # 개발 의존성
poetry install                 # lock 기반 설치
poetry run pytest              # venv 안에서 실행
poetry build                   # wheel + sdist 생성
```

```text
# poetry.lock (자동 생성, 커밋 대상)
[[package]]
name = "httpx"
version = "0.27.2"
python-versions = ">=3.8"

[package.dependencies]
anyio = "*"
certifi = "*"
httpcore = "==1.*"
```

## 의존성 업데이트 전략

의존성을 방치하면 보안 취약점이 쌓이고, 한꺼번에 업데이트하면 호환성 문제가 동시에 터집니다. 정기적이고 점진적인 업데이트가 핵심입니다.

### 주간 업데이트 루틴

```bash
# 1. 업데이트 가능한 패키지 확인
pip list --outdated

# 2. 마이너/패치 업데이트만 적용
pip-compile --upgrade-package "httpx" requirements.in

# 3. 테스트 실행
pytest

# 4. 문제 없으면 커밋
git add requirements.txt
git commit -m "deps: upgrade httpx to 0.27.2"
```

### 메이저 업데이트 체크리스트

메이저 버전 변경(`1.x → 2.x`)은 브레이킹 체인지를 포함할 수 있습니다.

```text
1. 변경 로그(CHANGELOG) 읽기
2. 마이그레이션 가이드 확인
3. 별도 브랜치에서 업그레이드
4. 전체 테스트 스위트 실행
5. 타입 검사(mypy) 실행
6. 스테이징 환경에서 동작 확인
7. 메인 브랜치에 병합
```

## 의존성 트리 시각화와 정리

프로젝트가 커지면 간접 의존성이 수십 개로 늘어납니다. 주기적으로 정리하면 설치 시간과 공격 표면을 줄일 수 있습니다.

```bash
# 전체 의존성 트리
pipdeptree

# 특정 패키지의 역의존성 (누가 이 패키지를 필요로 하는가)
pipdeptree -r -p certifi

# 사용하지 않는 패키지 찾기
pip install deptry
deptry .
```

```text
# deptry 출력 예시
DEP002: 'black' is in requirements but not used in source code
DEP003: 'tomli' is imported but not in requirements (transitive dependency)
```

`DEP003`은 간접 의존성을 직접 import하는 경우로, 해당 패키지가 업데이트로 사라지면 코드가 깨집니다. 명시적으로 `dependencies`에 추가하는 편이 안전합니다.

### lock 파일을 커밋해야 하는가?

| 프로젝트 유형 | lock 파일 커밋 | 이유 |
|---|---|---|
| 애플리케이션 | 예 | 배포 재현성 보장 |
| 라이브러리 | 아니오 | 사용자 환경 유연성 유지 |
| 모노레포 (앱) | 예 | 서비스별 정확한 버전 고정 |

## 처음 질문으로 돌아가기

- **`pip install`은 패키지를 어디에 설치할까요?**
  - `pip install`은 현재 활성화된 환경의 `site-packages/` 디렉터리에 패키지를 설치합니다. venv 안이라면 `.venv/lib/python3.11/site-packages/`이고, 시스템 Python이라면 `/usr/lib/python3.11/site-packages/`입니다. `pip show <package>`의 Location 필드로 확인할 수 있습니다.

- **가상 환경은 무엇을 격리하고, 왜 필요할까요?**
  - 가상 환경은 `site-packages` 경로를 프로젝트별로 분리합니다. 프로젝트 A가 `requests==2.28`을, 프로젝트 B가 `requests==2.32`를 필요로 할 때 시스템 전역에는 하나만 설치할 수 있지만, venv를 쓰면 각 프로젝트가 독립된 패키지 세트를 유지합니다. `PATH` 변경만으로 이 격리가 동작합니다.

- **의존성 버전 충돌이 생기면 어떻게 해결할까요?**
  - pip의 backtracking resolver가 모든 패키지의 버전 요구사항을 동시에 만족하는 조합을 자동으로 탐색합니다. 해결 불가능한 경우 에러를 출력합니다. `pipdeptree -r`로 충돌 원인을 역추적하고, 상한 버전을 조정하거나 대체 패키지를 찾아 해결합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- **Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements (현재 글)**
- Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist (예정)
- Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- Python Package 101 (6/10): 버전 관리와 릴리스 (예정)
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging User Guide - Managing Dependencies](https://packaging.python.org/en/latest/tutorials/managing-dependencies/)
- [PEP 405 - Python Virtual Environments](https://peps.python.org/pep-0405/)
- [uv - An extremely fast Python package installer](https://github.com/astral-sh/uv)
- [pip documentation - Requirements Files](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

Tags: Python, Packaging, PyPI, pyproject.toml
