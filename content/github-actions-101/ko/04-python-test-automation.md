---
series: github-actions-101
episode: 4
title: "GitHub Actions 101 (4/10): Python 테스트 자동화"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - GitHubActions
  - Python
  - Pytest
  - Testing
  - CICD
seo_description: pytest, coverage, matrix 기반의 Python 테스트 자동화를 실무 흐름으로 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (4/10): Python 테스트 자동화

로컬에서만 `pytest`를 돌리는 팀은 결국 같은 문제를 반복해서 만납니다. 내 환경에서는 통과했는데 CI에서는 실패하고, 누군가는 테스트를 건너뛰고, 누군가는 다른 Python 버전에서만 깨지는 문제를 머지 뒤에 발견합니다. 테스트가 존재하는 것과 자동으로 실행되는 것은 전혀 다른 단계입니다.

이 글은 GitHub Actions 101 시리즈의 4번째 글입니다. 여기서는 GitHub Actions에서 Python 테스트를 자동화하는 기본 흐름을 정리하고, 캐시, 리포트, 커버리지, 매트릭스까지 어떤 기준으로 붙여야 하는지 설명하겠습니다.


![GitHub Actions 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/04/04-01-diagram.ko.png)
*GitHub Actions 101 4장 흐름 개요*

## 먼저 던지는 질문

- `setup-python`과 pip 캐시는 왜 함께 다뤄야 할까요?
- `pytest` 결과를 PR 체크와 리포트로 드러내려면 무엇이 필요할까요?
- 커버리지는 왜 숫자 자체보다 추세와 기준이 중요할까요?

## 왜 중요한가

수동 테스트는 꼭 빠집니다. 일정이 급할수록 더 그렇습니다. 반대로 자동 테스트는 사람이 바쁘더라도 같은 절차를 반복합니다. 저는 CI의 핵심 가치를 “좋은 습관을 강제하는 것”이라고 생각합니다. 테스트 자동화가 붙는 순간, 품질 기준은 개인의 기억에서 저장소 규칙으로 옮겨 갑니다.

또 하나 중요한 점은 속도입니다. 테스트가 너무 느리면 팀은 CI를 덜 신뢰합니다. 느린 CI는 결국 건너뛰는 CI가 됩니다. 그래서 테스트 자동화는 많이 붙이는 것보다 빠르고 일관되게 붙이는 편이 더 중요합니다.

## 한눈에 보는 테스트 흐름

이 흐름은 단순하지만 운영 감각을 잘 보여 줍니다. 실행 환경을 맞추고, 의존성을 설치하고, 테스트를 돌리고, 결과를 남깁니다. 어느 단계에서 시간이 오래 걸리는지 보는 것만으로도 개선 포인트가 드러납니다.

## 먼저 핵심 용어를 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| `setup-python` | 러너에 Python을 설치하는 액션 | 버전 고정과 캐시 설정의 출발점입니다 |
| pip 캐시 | 의존성 설치 결과를 재사용하는 기능 | 설치 시간을 줄여 피드백을 빠르게 만듭니다 |
| `pytest` | Python 테스트 러너 | 가장 흔한 표준 조합입니다 |
| `junitxml` | 테스트 결과를 XML로 남기는 형식 | PR 리포트, 아티팩트와 연동하기 좋습니다 |
| coverage | 테스트가 닿은 코드 범위를 측정 | 목표 숫자보다 변화 추이를 보는 편이 중요합니다 |
| Codecov | 커버리지 리포팅 서비스 | PR에서 변화량을 보여 주는 데 유용합니다 |

## 자동화 전과 후를 비교해 보겠습니다

자동화가 없으면 `pytest`는 로컬에서만 돌아갑니다. 이 구조에서는 누가 어느 버전의 Python을 쓰는지, 가상환경이 깨끗한지, 테스트가 실제로 최신 코드 기준인지 확신하기 어렵습니다. “머지하고 나서 main이 깨졌다”는 사고가 자주 나는 이유도 여기에 있습니다.

자동화가 붙으면 PR마다 같은 절차가 실행됩니다. Python 3.10, 3.11, 3.12를 모두 통과해야 머지할 수 있게 만들 수도 있습니다. 이 순간부터 테스트는 개인의 습관이 아니라 저장소의 규칙이 됩니다.

## 테스트 자동화를 5단계로 구성해 보겠습니다

### 1단계 — Python과 캐시 설정하기

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.11"
    cache: "pip"
- run: pip install -r requirements.txt
```

이 설정의 핵심은 `cache: "pip"`입니다. 의존성 설치 시간을 매번 처음부터 내지 않게 해 주므로, 작은 한 줄이지만 체감 성능에 큰 차이를 만듭니다.

### 2단계 — 테스트 결과를 리포트로 남기기

```yaml
- run: pytest -q --junitxml=report.xml
- uses: actions/upload-artifact@v7
  if: always()
  with:
    name: pytest-report
    path: report.xml
```

테스트는 통과 여부만 보는 것으로 끝나지 않습니다. 실패했을 때 어떤 테스트가 어떻게 깨졌는지 남겨야 이후 분석이 쉬워집니다. `if: always()`가 중요한 이유도 여기에 있습니다.

### 3단계 — 커버리지 측정하기

```yaml
- run: pytest --cov=src --cov-report=xml
- uses: codecov/codecov-action@v4
  with:
    files: coverage.xml
```

커버리지는 숫자를 모으는 게임이 아닙니다. 어떤 PR이 중요한 경로를 빠뜨렸는지, 시간이 지나며 품질 기준이 낮아지고 있는지 읽기 위한 신호에 가깝습니다.

### 4단계 — 여러 Python 버전에서 검증하기

```yaml
strategy:
  matrix:
    python: ["3.10", "3.11", "3.12"]
steps:
  - uses: actions/setup-python@v6
    with:
      python-version: ${{ matrix.python }}
```

라이브러리나 SDK처럼 호환성이 중요한 프로젝트라면 매트릭스가 큰 가치가 있습니다. 반대로 사내 서비스처럼 실제 운영 버전이 하나로 고정돼 있다면, 매트릭스는 꼭 필요한 범위로만 두는 편이 좋습니다.

### 5단계 — 실패 시 로그 남기기

```yaml
- name: dump logs on failure
  if: failure()
  run: |
    cat pytest.log || true
```

테스트가 흔들릴 때 가장 아쉬운 것은 재현 재료가 없는 상황입니다. 실패 시점의 로그를 남기면 다시 돌렸을 때 사라지는 문제도 어느 정도 추적할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `cache: "pip"` 한 줄이 설치 시간을 크게 줄일 수 있습니다.
- `junitxml`은 사람이 읽는 로그와 별개로 도구가 읽을 결과물을 만듭니다.
- `if: always()` 덕분에 실패한 실행에서도 아티팩트를 남길 수 있습니다.

즉, 테스트 자동화는 “테스트를 돌린다”에서 끝나지 않습니다. 결과를 남기고, 실패를 읽을 수 있게 만들고, 반복 실행 비용을 낮추는 것까지 포함해야 실무에서 오래 갑니다.

## 자주 하는 실수 다섯 가지

1. pip 캐시 없이 매번 전체 의존성을 다시 설치합니다.
2. CI에서 `pytest -v`를 남발해 로그만 과도하게 키웁니다.
3. 외부 네트워크에 의존하는 테스트를 그대로 넣어 흔들리는 CI를 만듭니다.
4. `junitxml` 없이 통과 여부만 남깁니다.
5. 커버리지를 목표 없이 측정해 숫자만 쌓습니다.

특히 세 번째는 운영에서 자주 문제를 만듭니다. 네트워크 상태, 외부 서비스 레이트 리밋, 테스트 데이터 오염이 겹치면 CI 신뢰가 빠르게 무너집니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 빠른 단위 테스트와 느린 통합 테스트를 분리합니다. PR에서는 빠른 테스트만 돌리고, 야간이나 main push에서는 더 무거운 검증을 붙이는 방식이 흔합니다. 또 흔들리는 테스트는 그냥 두지 않고 격리하거나 재실행 정책을 둡니다.

커버리지도 같은 기준으로 봅니다. 100%를 목표로 세우기보다, 핵심 경로를 빠뜨리지 않았는지, 중요한 모듈이 지속적으로 빈약해지지 않는지 보는 편이 훨씬 실용적입니다.

## 체크리스트

- [ ] pip 캐시가 켜져 있다.
- [ ] `junit XML` 결과를 업로드한다.
- [ ] 커버리지를 측정한다.
- [ ] 매트릭스 범위가 실제 필요에 맞는다.

## 연습 문제

1. 현재 프로젝트에 `pytest` 워크플로우를 추가해 보세요.
2. Python 3.11과 3.12 매트릭스를 붙여 보세요.
3. 커버리지가 80% 아래로 떨어지면 PR을 실패시키도록 바꿔 보세요.

## 정리

Python 테스트 자동화의 핵심은 같은 환경에서 같은 명령을 반복 실행하게 만드는 것입니다. 캐시로 피드백 시간을 줄이고, 리포트와 커버리지로 결과를 남기고, 필요할 때만 매트릭스로 검증 범위를 넓히면 됩니다.

다음 글에서는 lint와 type check를 다룹니다. 테스트가 동작을 검증한다면, 그다음 단계는 스타일과 정적 타입 규칙을 자동으로 막는 품질 게이트를 세우는 일입니다.


---

## Python 테스트 환경 설정을 더 깊이 보겠습니다

### setup-python의 캐시 전략

`actions/setup-python`의 `cache` 옵션은 pip 다운로드 캐시를 워크플로우 실행 간에 보존합니다. 이 한 줄만으로 의존성 설치 시간을 50-80% 줄일 수 있습니다.

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"
    cache-dependency-path: |
      requirements.txt
      requirements-dev.txt
```

캐시 키는 `cache-dependency-path`에 지정한 파일들의 해시로 결정됩니다. 의존성 파일이 바뀌면 캐시가 무효화되고, 새 의존성을 다운로드합니다. 여러 의존성 파일이 있다면 모두 명시해야 캐시 적중률이 올라갑니다.

캐시가 올바르게 동작하는지 확인하는 방법입니다.

```text
Run actions/setup-python@v6
  Cache restored successfully  ← 캐시 적중
  or
  Cache not found for key: ...  ← 캐시 미스 (첫 실행 또는 의존성 변경)
```

### pip install 전략 비교

```yaml
# 방법 1: requirements.txt 기반 (단순)
- run: pip install -r requirements.txt -r requirements-dev.txt

# 방법 2: pyproject.toml 기반 (권장)
- run: pip install -e ".[dev]"

# 방법 3: pip-tools로 잠금 파일 기반 (재현성 최고)
- run: pip install -r requirements.lock
```

방법 2가 현대 Python 프로젝트에서 가장 일반적입니다. `pyproject.toml`의 optional-dependencies에 개발 의존성을 선언하면, 로컬과 CI에서 동일한 명령으로 설치할 수 있습니다. 방법 3은 재현성이 가장 높지만 잠금 파일 관리 부담이 있습니다.

---

## pytest 실행 최적화

테스트 수가 많아지면 실행 시간도 길어집니다. CI에서 pytest를 효율적으로 실행하는 기법을 정리하겠습니다.

### 병렬 실행 (pytest-xdist)

```yaml
- run: pip install pytest-xdist
- run: pytest -q -n auto --dist loadscope
```

`-n auto`는 CPU 코어 수에 맞춰 워커를 생성합니다. `--dist loadscope`는 같은 모듈의 테스트를 같은 워커에 배치해서 fixture 공유를 최적화합니다.

GitHub-hosted 러너는 보통 2코어이므로 `-n 2`로 명시하는 것도 괜찮습니다. 코어 수보다 워커를 많이 만들면 오히려 컨텍스트 스위칭으로 느려질 수 있습니다.

### 실패 우선 실행

```yaml
- run: pytest -q --lf --ff
```

`--lf`(last failed)는 이전 실행에서 실패한 테스트만 재실행하고, `--ff`(failed first)는 실패한 테스트를 먼저 실행합니다. CI에서는 캐시가 없으므로 `--ff`가 더 유용합니다. 빠른 피드백을 위해 실패 가능성이 높은 테스트를 먼저 돌리는 전략입니다.

### 테스트 마킹과 선택 실행

```yaml
# PR에서는 느린 테스트 제외
- run: pytest -q -m "not slow"

# 야간 실행에서는 전체 포함
- run: pytest -q
```

```python
# tests/test_integration.py
import pytest

@pytest.mark.slow
def test_full_pipeline():
    """전체 파이프라인 통합 테스트 - 5분 이상 소요"""
    ...
```

`@pytest.mark.slow`로 느린 테스트를 표시하고, PR 검증에서는 제외합니다. 야간 schedule 실행에서 전체 테스트를 돌리면 빠른 피드백과 완전한 검증을 모두 확보할 수 있습니다.

---

## 테스트 리포트를 PR에 표시하기

테스트가 실패했을 때 "로그를 열어서 직접 찾아라"보다 PR 코멘트에 결과가 바로 보이면 개발자 경험이 크게 좋아집니다.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      checks: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"

      - name: 테스트 실행
        run: pytest --junitxml=report.xml --cov=src --cov-report=xml

      - name: 테스트 결과 PR 표시
        uses: mikepenz/action-junit-report@v5
        if: always()
        with:
          report_paths: report.xml
          check_name: "pytest results"

      - name: 커버리지 코멘트
        uses: orgoro/coverage@v3.2
        if: github.event_name == 'pull_request'
        with:
          coverageFile: coverage.xml
          token: ${{ secrets.GITHUB_TOKEN }}
```

`if: always()`가 중요합니다. 이 조건이 없으면 테스트 실패 시 리포트 업로드 스텝이 건너뛰어져서, 정작 실패 정보가 필요한 상황에서 리포트를 볼 수 없습니다.

---

## 커버리지 관리 전략

커버리지 숫자 자체보다 중요한 것은 추세와 기준입니다. 80%가 좋은지 나쁜지는 프로젝트마다 다르지만, "이번 PR이 커버리지를 낮추지 않았는가"는 보편적으로 유용한 기준입니다.

### 커버리지 게이트 설정

```yaml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

`fail_under`를 설정하면 커버리지가 기준 아래로 떨어질 때 pytest가 실패합니다. 이 값은 현재 프로젝트 수준에 맞춰 시작하고 점진적으로 올리는 편이 현실적입니다.

### Codecov / Coveralls 연동

```yaml
- name: 커버리지 업로드
  uses: codecov/codecov-action@v5
  with:
    files: coverage.xml
    flags: unittests
    fail_ci_if_error: false
```

외부 서비스를 연동하면 커버리지 추세 그래프, PR별 diff 커버리지, 파일별 히트맵을 볼 수 있습니다. 특히 diff 커버리지(이번 PR에서 변경한 코드의 커버리지)는 전체 커버리지보다 실행 가능한 피드백을 줍니다.

---

## 테스트 매트릭스 실전 구성

Python 프로젝트에서 자주 쓰는 테스트 매트릭스 패턴입니다.

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ["3.10", "3.11", "3.12"]
        include:
          - os: macos-latest
            python-version: "3.12"
          - os: windows-latest
            python-version: "3.12"
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

이 매트릭스는 Ubuntu에서 세 Python 버전을, macOS와 Windows에서는 최신 버전만 테스트합니다. 총 5개 조합으로 호환성을 확인하면서도 비용을 합리적으로 유지합니다.

### 데이터베이스 서비스가 필요한 테스트

```yaml
jobs:
  test-with-db:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/testdb
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest tests/integration -q
```

`services`는 잡에서 사용할 컨테이너를 함께 실행합니다. health check 옵션을 설정해야 서비스가 준비된 뒤에 테스트가 시작됩니다. 이 설정이 없으면 PostgreSQL이 아직 뜨지 않은 상태에서 테스트가 연결을 시도해 실패할 수 있습니다.

---

## 테스트 실패 시 디버깅 지원

CI에서 테스트가 실패했을 때 원인을 빠르게 파악하려면 충분한 정보를 남겨야 합니다.

```yaml
- name: 테스트 실행
  run: pytest -q --tb=short --junitxml=report.xml -v
  continue-on-error: true
  id: test

- name: 실패 시 상세 로그
  if: steps.test.outcome == 'failure'
  run: pytest --lf --tb=long -v

- name: 아티팩트 저장
  if: always()
  uses: actions/upload-artifact@v7
  with:
    name: test-results
    path: |
      report.xml
      .coverage
      tests/output/
    retention-days: 3
```

이 패턴은 첫 실행에서 빠르게 결과를 확인하고, 실패한 경우에만 상세 로그를 출력합니다. 성공 시에는 불필요한 출력을 줄이고, 실패 시에는 디버깅에 충분한 정보를 제공합니다.


---

## 테스트 안정성 관리

CI에서 간헐적으로 실패하는 테스트(flaky test)는 팀의 CI 신뢰를 빠르게 떨어뜨립니다. flaky 테스트를 다루는 전략을 정리하겠습니다.

### flaky 테스트 감지

```yaml
- run: pytest -q --count=3 -x
  # pytest-repeat으로 3회 반복 실행
```

같은 테스트를 여러 번 돌려서 간헐 실패를 재현합니다. CI에서만 실패하는 경우는 대부분 타이밍, 네트워크, 파일시스템 순서에 의존하는 테스트입니다.

### flaky 테스트 격리

```python
# conftest.py
import pytest

def pytest_collection_modifyitems(items):
    """flaky 마크가 있는 테스트를 별도 그룹으로 분리"""
    for item in items:
        if "flaky" in item.keywords:
            item.add_marker(pytest.mark.xfail(
                reason="known flaky", strict=False
            ))
```

`xfail(strict=False)`로 표시하면 실패해도 전체 테스트 스위트를 깨뜨리지 않으면서, 성공하면 `XPASS`로 표시되어 안정화되었는지 추적할 수 있습니다.

### 재시도 전략

```yaml
- name: 테스트 (재시도 포함)
  uses: nick-fields/retry@v3
  with:
    max_attempts: 3
    timeout_minutes: 10
    command: pytest tests/integration -q
```

통합 테스트처럼 외부 의존성이 있는 테스트는 일시적 실패가 불가피합니다. 재시도를 두면 일시적 실패로 인한 불필요한 재실행을 줄일 수 있습니다. 다만 재시도는 근본 원인을 숨길 수 있으므로, 재시도 횟수와 실패 빈도를 모니터링해야 합니다.

---

## 전체 워크플로우 예제

지금까지 다룬 내용을 종합한 실무 수준의 Python 테스트 워크플로우입니다.

```yaml
name: python-test

on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"

concurrency:
  group: test-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      checks: write
      pull-requests: write
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: 의존성 설치
        run: pip install -e ".[dev]"

      - name: 단위 테스트
        run: pytest tests/unit -q -n auto --cov=src --cov-report=xml --junitxml=unit-report.xml

      - name: 통합 테스트
        run: pytest tests/integration -q --junitxml=integration-report.xml
        env:
          REDIS_URL: redis://localhost:6379

      - name: 테스트 리포트
        uses: mikepenz/action-junit-report@v5
        if: always()
        with:
          report_paths: "*-report.xml"
          check_name: "pytest-${{ matrix.python-version }}"

      - name: 커버리지 업로드
        if: matrix.python-version == '3.12'
        uses: codecov/codecov-action@v5
        with:
          files: coverage.xml
          flags: unittests
```

이 워크플로우의 설계 포인트를 정리하면 다음과 같습니다.

- `paths` 필터로 관련 없는 변경에서는 실행하지 않습니다.
- `concurrency`로 같은 PR의 중복 실행을 취소합니다.
- 두 Python 버전으로 호환성을 확인하되, `fail-fast: false`로 모든 결과를 수집합니다.
- 단위 테스트는 병렬(`-n auto`)로 빠르게 실행하고, 통합 테스트는 Redis 서비스와 함께 실행합니다.
- 커버리지는 한 버전에서만 업로드해서 중복을 피합니다.
- `if: always()`로 실패해도 리포트가 올라갑니다.


## 처음 질문으로 돌아가기

- **`setup-python`과 pip 캐시는 왜 함께 다뤄야 할까요?**
  - `setup-python`의 `cache: "pip"` 옵션은 pip 다운로드 캐시를 실행 간에 보존해서 의존성 설치 시간을 50-80% 줄입니다. `cache-dependency-path`로 캐시 키를 의존성 파일 해시에 연결하면, 의존성이 바뀔 때만 새로 다운로드하고 나머지 실행에서는 캐시를 재사용합니다. 이 한 줄 설정이 전체 워크플로우 시간에 미치는 영향이 크기 때문에 반드시 함께 설정해야 합니다.
- **`pytest` 결과를 PR 체크와 리포트로 드러내려면 무엇이 필요할까요?**
  - `--junitxml=report.xml`로 결과를 XML로 남기고, `mikepenz/action-junit-report` 같은 액션으로 PR 체크에 표시합니다. `if: always()`가 핵심인데, 이 조건이 없으면 실패 시 리포트 스텝이 건너뛰어져 정작 필요한 상황에서 정보를 볼 수 없습니다. `permissions: checks: write`도 잊지 말아야 합니다.
- **커버리지는 왜 숫자 자체보다 추세와 기준이 중요할까요?**
  - 80%라는 숫자는 프로젝트마다 의미가 다릅니다. 중요한 것은 "이번 PR이 커버리지를 낮추지 않았는가"(diff coverage)와 "시간이 지나며 커버리지가 어떤 방향으로 움직이는가"(추세)입니다. `fail_under`로 하한선을 잡고, Codecov의 diff coverage로 PR별 피드백을 주면, 팀이 테스트를 쓰는 습관을 자연스럽게 유지할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- **Python 테스트 자동화 (현재 글)**
- Lint와 Type Check (예정)
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py](https://coverage.readthedocs.io/)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Python, Pytest, Testing, CICD
