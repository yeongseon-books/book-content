---
series: pytest-101
episode: 9
title: GitHub Actions에서 테스트 자동화하기
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - GitHub Actions
  - CI/CD
  - 테스트 자동화
seo_description: GitHub Actions로 pytest를 자동 실행하는 CI 파이프라인 구성 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# GitHub Actions에서 테스트 자동화하기

이 글은 pytest 101 시리즈의 아홉 번째 글입니다. 로컬에서만 테스트를 돌리는 습관으로는 팀 전체 품질을 지키기 어렵습니다. 이 글에서는 GitHub Actions를 이용해 push와 pull request마다 pytest를 자동 실행하고, 커버리지와 Python 버전 매트릭스까지 함께 검증하는 방법을 설명합니다.

테스트는 작성하는 것만큼 꾸준히 실행되는 것이 중요합니다. 사람이 직접 실행해야 하는 절차에 기대면 결국 누락이 생기기 때문에, CI는 테스트 문화를 습관이 아니라 시스템으로 바꿔 줍니다.

---

## 이 글에서 다룰 문제

- PR을 열 때마다 테스트를 수동으로 돌려야 할까요?
- GitHub Actions workflow는 어떤 구조로 작성할까요?
- 여러 Python 버전을 동시에 검증하려면 어떻게 해야 할까요?
- 캐시와 커버리지 리포트는 어떻게 연결할 수 있을까요?

## 왜 이 글이 중요한가

내 로컬 환경에서 통과한 테스트가 다른 환경에서는 실패할 수 있습니다. CI는 일관된 환경에서 같은 절차를 반복하므로, 코드가 머지되기 전에 문제를 더 일찍 발견하게 해 줍니다.

> “내 컴퓨터에서는 되는데요”라는 말은 CI가 해결합니다. CI에서 통과하면 적어도 팀이 합의한 환경에서는 모두 같은 결과를 볼 수 있습니다.

아무리 좋은 테스트도 실행되지 않으면 존재 가치가 없습니다. 자동화는 테스트를 잘 쓰는 문제를 넘어, 테스트를 반드시 돌리게 만드는 운영 문제이기도 합니다.

## 핵심 개념 잡기

> CI = push/PR event → automatic test run → results displayed on PR

```text
Developer pushes → GitHub Actions triggered
  → Install Python
  → Install dependencies
  → Run pytest
  → Coverage report
  → Result: Pass / Fail
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| workflow | `.github/workflows/` 아래에 정의하는 자동화 파이프라인입니다 |
| job | workflow 안의 실행 단위입니다 |
| step | job을 구성하는 개별 명령입니다 |
| matrix | 여러 환경 조합을 병렬로 검증하는 방식입니다 |
| artifact | CI 실행 중 생성한 파일을 저장·다운로드하는 기능입니다 |

## Before / After

수동 실행과 자동 실행을 비교해 보겠습니다.

```bash
# before: manual — developer runs tests themselves
git push origin feature-branch
# PR created... forgot to run tests
# reviewer: "Did you run the tests?" → "Uh... no"
```

```yaml
# after: automatic — runs on every push
# .github/workflows/test.yml
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

### Step 1: Write the Basic Workflow

```yaml
# .github/workflows/test.yml
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
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        run: pytest -v --tb=short

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Step 2: Matrix Build

```yaml
# .github/workflows/test.yml
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

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        run: pytest -v --cov=src --cov-report=term-missing
```

### Step 3: Dependency Caching

```yaml
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

### Step 4: Upload Coverage Artifact

```yaml
      - name: Generate HTML coverage report
        run: pytest --cov=src --cov-report=html
        if: matrix.python-version == '3.12'

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
        if: matrix.python-version == '3.12'
```

### Step 5: Configure Test Dependencies in pyproject.toml

```toml
# pyproject.toml
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

- `push`와 `pull_request` 둘 다 걸어 두어야 머지 전 검증이 가능합니다.
- matrix build는 여러 Python 버전을 동시에 확인하게 해 줍니다.
- 캐시는 `pip install` 시간을 줄여 CI 피드백 속도를 개선합니다.
- 커버리지 HTML 리포트를 artifact로 남기면 실패 원인 분석이 쉬워집니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `requirements.txt`만 설치함 | 패키지 자체가 설치되지 않아 import 오류가 납니다 | `pip install -e ".[test]"`를 사용합니다 |
| Python 버전에 따옴표를 빼먹음 | YAML이 `3.10`을 `3.1`처럼 해석할 수 있습니다 | `"3.10"`처럼 문자열로 씁니다 |
| 캐시 키에 의존성 파일 해시를 넣지 않음 | 의존성 변경이 캐시에 반영되지 않습니다 | `hashFiles('pyproject.toml')`를 사용합니다 |
| 커버리지 기준을 두지 않음 | 테스트 품질이 떨어져도 CI가 통과합니다 | `--cov-fail-under`를 설정합니다 |
| main 브랜치만 검증함 | PR 단계에서 문제를 못 잡습니다 | `pull_request` 이벤트도 포함합니다 |

## 실무에서 이렇게 쓰입니다

- 브랜치 보호와 연결해 CI가 통과하지 않으면 머지할 수 없게 합니다.
- Python 3.10, 3.11, 3.12 호환성을 matrix로 동시에 확인합니다.
- 커버리지 변화를 PR 코멘트나 아티팩트로 공유합니다.
- 느린 테스트는 별도 job으로 나눠 피드백 시간을 줄입니다.
- README에 status badge를 붙여 저장소 건강 상태를 드러냅니다.

## 현업 개발자는 이렇게 생각합니다

CI는 사람이 테스트를 “기억해서 실행하는” 문제를 시스템이 대신 해결하는 방식입니다. 한 번 구성해 두면, 테스트 실행이 개인 습관이 아니라 저장소 기본 동작이 됩니다.

실무에서 가장 효과적인 규칙 중 하나는 단순합니다. “CI가 통과하지 않으면 PR을 머지하지 않는다.” 이 규칙 하나만으로도 회귀 버그와 기본적인 실수를 크게 줄일 수 있습니다.

## 체크리스트

- [ ] `.github/workflows/test.yml`을 만들었다
- [ ] `push`와 `pull_request` 트리거를 설정했다
- [ ] 여러 Python 버전을 matrix로 검증했다
- [ ] 의존성 캐시를 추가했다
- [ ] 커버리지 기준과 artifact 업로드를 설정했다

## 연습 문제

1. lint job(ruff 또는 flake8)을 추가해 test job과 병렬로 실행해 보세요.
2. `fail-fast: false`를 설정해 한 버전이 실패해도 나머지 버전이 계속 실행되게 해 보세요.
3. README에 workflow status badge를 추가해 보세요.

## 정리 및 다음 글 안내

GitHub Actions를 이용하면 테스트 실행이 수동 절차가 아니라 저장소의 기본 안전장치가 됩니다. matrix, 캐시, 커버리지 리포트까지 연결하면 CI는 단순 실행기를 넘어 품질 게이트 역할을 하게 됩니다. 다음 글에서는 마지막으로, 애초에 mock을 덜 쓰게 만드는 테스트하기 쉬운 코드 구조를 살펴보겠습니다.

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

- [GitHub Actions — Documentation](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest-cov — CI Configuration](https://pytest-cov.readthedocs.io/en/latest/config.html)
- [Real Python — CI/CD with GitHub Actions](https://realpython.com/python-continuous-integration/)

Tags: Python, pytest, GitHub Actions, CI/CD, 테스트 자동화
