---
series: pytest-101
episode: 9
title: GitHub Actions에서 테스트 자동화하기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - GitHub Actions
  - CI/CD
  - 테스트 자동화
seo_description: GitHub Actions로 pytest를 자동 실행하는 CI 파이프라인을 구축합니다.
last_reviewed: '2026-05-11'
---

# GitHub Actions에서 테스트 자동화하기

> pytest 101 시리즈 (9/10)


## 이 글에서 다룰 문제

로컬에서 테스트가 통과해도 다른 환경에서 실패할 수 있습니다. CI는 일관된 환경에서 모든 테스트를 자동으로 실행하여, 코드가 머지되기 전에 문제를 발견합니다.

> "내 컴퓨터에서는 되는데요"는 CI가 해결합니다. CI에서 통과하면 팀원 모두의 환경에서 동작한다는 보장입니다.

테스트가 아무리 잘 작성되어 있어도, 실행하지 않으면 의미가 없습니다. CI는 테스트 실행을 자동화하여 "깜빡하고 안 돌림"을 방지합니다.

## 핵심 개념 잡기

> CI = push/PR 이벤트 → 자동으로 테스트 실행 → 결과를 PR에 표시

```text
개발자 push → GitHub Actions 트리거
  → Python 설치
  → 의존성 설치
  → pytest 실행
  → 커버리지 리포트
  → 결과: ✓ 통과 / ✗ 실패
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| workflow | `.github/workflows/`에 정의하는 자동화 파이프라인입니다 |
| job | 워크플로우 안의 실행 단위입니다 |
| step | job 안의 개별 명령입니다 |
| matrix | 여러 환경 조합을 동시에 테스트합니다 |
| artifact | CI 실행 중 생성된 파일을 저장하고 다운로드합니다 |

## Before / After

수동 테스트와 CI 자동화를 비교합니다.

```bash
# 이전 방식: 수동 — 개발자가 직접 실행합니다
git push origin feature-branch
# PR 생성 후... 테스트를 깜빡하고 안 돌림
# 리뷰어: "테스트 돌려봤어요?" → "아... 안 돌렸어요"
```

```yaml
# 개선 방식: 자동 — push하면 자동으로 실행합니다
# .github/workflows/test.yml 파일
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[test]"
      - run: pytest --cov
```

## 단계별 실습

### Step 1: 기본 워크플로우 작성

```yaml
# .github/workflows/test.yml 파일
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: 코드 체크아웃
        uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: 의존성 설치
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: 테스트 실행
        run: pytest -v --tb=short

      - name: 커버리지 포함 테스트 실행
        run: pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Step 2: 매트릭스 빌드

```yaml
# .github/workflows/test.yml 파일
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Python ${{ matrix.python-version }} 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: 의존성 설치
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: 테스트 실행
        run: pytest -v --cov=src --cov-report=term-missing
```

### Step 3: 의존성 캐싱

```yaml
      - name: pip 패키지 캐시
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

### Step 4: 커버리지 아티팩트 업로드

```yaml
      - name: HTML 커버리지 리포트 생성
        run: pytest --cov=src --cov-report=html
        if: matrix.python-version == '3.12'

      - name: 커버리지 리포트 업로드
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
        if: matrix.python-version == '3.12'
```

### Step 5: pyproject.toml에 test 의존성 설정

```toml
# pyproject.toml 파일
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "freezegun>=1.2",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

## 이 코드에서 주목할 점

- `on: [push, pull_request]`로 두 이벤트 모두에서 실행됩니다
- 매트릭스 빌드로 3개 Python 버전을 동시에 테스트합니다
- 캐싱으로 `pip install` 시간을 절약합니다
- 커버리지 리포트를 아티팩트로 저장하여 나중에 다운로드할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `pip install .` 대신 `pip install -r requirements.txt`만 실행 | 패키지 자체가 설치되지 않아 import 에러가 발생합니다 | `pip install -e ".[test]"`로 패키지와 테스트 의존성을 함께 설치합니다 |
| Python 버전을 따옴표 없이 지정 | `3.10`이 `3.1`로 해석됩니다 | `"3.10"` 처럼 따옴표로 감쌉니다 |
| 캐시 키에 lock 파일을 사용하지 않음 | 의존성 변경 시 캐시가 갱신되지 않습니다 | `hashFiles('pyproject.toml')`로 키를 설정합니다 |
| 커버리지 임계값 없이 실행 | 커버리지가 떨어져도 CI가 통과합니다 | `--cov-fail-under=80`을 추가합니다 |
| main 브랜치만 테스트 | PR에서 테스트하지 않으면 머지 후 실패합니다 | `pull_request` 이벤트도 포함합니다 |

## 실무에서 이렇게 쓰입니다

- PR을 올리면 자동으로 테스트가 실행되어, 테스트 통과 전에는 머지할 수 없도록 브랜치 보호를 설정합니다
- 매트릭스 빌드로 Python 3.10, 3.11, 3.12에서 모두 통과하는지 확인합니다
- 커버리지 리포트를 PR 댓글로 자동 게시합니다
- 느린 테스트를 별도 job으로 분리하여 빠른 피드백을 제공합니다
- 워크플로우 상태 배지를 README에 추가하여 프로젝트 건강 상태를 표시합니다

## 현업 개발자는 이렇게 생각합니다

CI는 "테스트를 돌리는 것을 깜빡하는" 인간의 한계를 보완합니다. 한 번 설정하면 모든 push마다 자동으로 실행되므로, 테스트 실행을 의식적으로 신경 쓸 필요가 없습니다.

실무에서는 CI가 통과하지 않으면 PR을 머지하지 않는 규칙을 팀 차원에서 설정합니다. 이 규칙 하나만으로도 코드 품질이 크게 개선됩니다.

## 체크리스트

- [ ] `.github/workflows/test.yml`을 작성했다
- [ ] push와 pull_request 이벤트에서 실행되도록 설정했다
- [ ] 매트릭스 빌드로 여러 Python 버전을 테스트했다
- [ ] 의존성 캐싱을 설정했다
- [ ] 커버리지 임계값을 설정하고 아티팩트를 업로드했다

## 정리 및 다음 글 안내

GitHub Actions로 테스트를 자동화하면 모든 코드 변경이 검증됩니다. 매트릭스 빌드, 캐싱, 커버리지 리포트로 CI를 효과적으로 구성할 수 있습니다. 다음 글에서는 테스트하기 쉬운 코드 구조를 만드는 설계 원칙을 배웁니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
- [parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- [mock과 monkeypatch](./06-mock-and-monkeypatch.md)
- [파일, 환경변수, 시간 테스트하기](./07-testing-files-env-time.md)
- [coverage와 테스트 품질 보기](./08-coverage.md)
- **GitHub Actions에서 테스트 자동화하기 (현재 글)**
- 테스트하기 쉬운 코드 구조 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Actions — 공식 문서](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest-cov — CI Configuration](https://pytest-cov.readthedocs.io/en/latest/config.html)
- [Real Python — CI/CD with GitHub Actions](https://realpython.com/python-continuous-integration/)

Tags: Python, pytest, GitHub Actions, CI/CD, 테스트 자동화
