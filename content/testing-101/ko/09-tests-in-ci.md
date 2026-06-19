---
series: testing-101
episode: 9
title: "Testing 101 (9/10): CI에서 테스트 실행하기"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - CI
  - GitHub Actions
  - Automation
  - Quality
seo_description: GitHub Actions로 테스트를 자동화하고 매트릭스, 캐시, 병렬화로 빠르게 만드는 법.
last_reviewed: '2026-05-12'
---

# Testing 101 (9/10): CI에서 테스트 실행하기

노트북에서는 통과했는데 동료 환경이나 머지 뒤 파이프라인에서는 깨지는 일은 흔합니다. 파이썬 버전이 다르거나, 의존 패키지 캐시 상태가 다르거나, 로컬에만 있는 파일 하나가 원인일 수도 있습니다. 로컬 통과만으로는 팀 전체 기준을 만들기 어렵습니다.

그래서 테스트는 개인 습관에만 맡기지 않고 공통 환경에서 자동으로 돌려야 합니다. 그 역할을 맡는 것이 CI입니다.

이 글은 Testing 101 시리즈의 아홉 번째 글입니다. 여기서는 CI의 목적, GitHub Actions 워크플로의 기본 구조, 매트릭스와 캐시로 속도를 줄이는 방법, 플래키 테스트 관리, 그리고 테스트 결과를 팀 공통 신호로 운영하는 감각을 정리하겠습니다.

![Testing 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/09/09-01-diagram.ko.png)
*Testing 101 9장 흐름 개요*
> CI 없는 테스트는 개발자의 책임이지만, CI가 있는 테스트는 팀의 안전망이 됩니다.

## 이 글에서 다룰 문제

- CI는 왜 필요한 공통 검증 장치일까요?
- GitHub Actions 워크플로는 어떤 구조로 작성할까요?
- 파이썬 버전 매트릭스와 캐시는 언제 도움이 될까요?
- 계층별 테스트를 CI에서 어떻게 분리해 실행할까요?
- 플래키 테스트는 어떻게 감지하고 관리할까요?

로컬 환경은 사람마다 다릅니다. 어떤 사람은 파이썬 3.11을 쓰고, 어떤 사람은 3.12를 쓰며, 어떤 사람은 캐시 덕분에 우연히 통과할 수도 있습니다. CI는 같은 컨테이너 환경에서 모든 PR을 검증해 이런 편차를 줄입니다.

또한 CI는 팀 규율을 강제합니다. 테스트가 실패하면 머지를 막고, 그 압력 덕분에 팀은 작은 PR과 빠른 피드백을 선호하게 됩니다. 테스트 문화는 도구 없이 잘 유지되지 않습니다.

## 한눈에 보는 구조

커밋이나 PR이 올라오면 워크플로가 실행되고, 파이썬과 의존을 준비한 뒤, 테스트를 돌리고, 결과나 커버리지 보고서를 남깁니다. 흐름은 단순하지만 팀 전체 품질 게이트 역할을 합니다.

- **CI**: Continuous Integration의 약자로, 커밋마다 자동 검증을 수행하는 흐름입니다.
- **워크플로(workflow)**: GitHub Actions에서 실행 규칙을 정의한 YAML 파일입니다.
- **매트릭스(matrix)**: 여러 파이썬 버전이나 운영체제 조합을 병렬 실행하는 설정입니다.
- **캐시(cache)**: 의존 설치 결과를 재사용해 시간을 줄이는 방식입니다.
- **아티팩트(artifact)**: 커버리지 보고서나 로그처럼 CI가 남기는 파일입니다.
- **플래키 테스트(flaky test)**: 같은 코드에서 실행 결과가 일관되지 않은 테스트입니다.

## 지속적 통합 서비스 비교 — 테스트 관점

| CI 서비스 | 무료 한도 | 병렬 지원 | 설정 난이도 | 권장 상황 |
|---|---|---|---|---|
| GitHub Actions | 2000분/월 (public 무제한) | 매트릭스, 병렬 잡 | 낮음 | GitHub 저장소 기본 선택 |
| GitLab CI | Shared runner 400분/월 | 병렬 잡 | 중간 | GitLab 저장소 또는 self-hosted |
| Jenkins | self-hosted 무제한 | 플러그인 기반 | 높음 | 온프레미스 환경 또는 복잡한 파이프라인 |

GitHub Actions는 설정이 쉽고 public 저장소에서는 무제한 실행이 가능해 오픈소스 프로젝트에 적합합니다.

## 바꾸기 전과 후

**바꾸기 전 — 수동 실행 중심**

```text
- 개발자가 자기 노트북에서만 pytest를 돌린다
- 한 번 빼먹으면 실패한 코드가 그대로 머지된다
- "제 로컬에서는 됐는데요"가 반복된다
```

**바꾼 뒤 — CI 자동화 적용**

```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest -v --cov=src --cov-fail-under=80
```

이 차이는 습관이 아니라 시스템 차이입니다. CI가 붙는 순간 테스트 실행이 선택이 아니라 기본 경로가 됩니다.

## 다섯 단계로 지속적 통합 구성하기

### 1단계 — 워크플로 파일 만들기

```bash
mkdir -p .github/workflows
touch .github/workflows/test.yml
```

### 2단계 — 매트릭스로 여러 버전 확인하기

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
      cache: 'pip'
```

매트릭스는 유용하지만 조합이 많아지면 시간이 급격히 늘 수 있습니다. 지원하는 버전만 포함합니다.

### 3단계 — 의존 캐시 켜기

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'pip'           # requirements.txt 해시를 자동 감지
- run: pip install -r requirements.txt
```

캐시를 끈 상태와 켠 상태의 실행 시간을 비교하면 보통 1~3분 단축 효과가 있습니다.

### 4단계 — 병렬 실행으로 시간 줄이기

```bash
pip install pytest-xdist
pytest -n auto             # CPU 코어 기준 병렬 실행
```

### 5단계 — 커버리지 결과 업로드하기

```yaml
- run: pytest --cov=src --cov-report=html --cov-report=term --cov-fail-under=80
- uses: actions/upload-artifact@v4
  if: matrix.python-version == '3.12'
  with:
    name: coverage-html
    path: htmlcov/
```

## 완전한 깃허브 액션 워크플로 예시

다음은 pytest와 커버리지, 계층별 분리를 포함한 실전 워크플로 전체 예시입니다.

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 빠른 단위 테스트 — PR에서 필수
  unit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist

      - name: Run unit tests
        run: |
          pytest tests/unit \
            -n auto \
            --cov=src \
            --cov-report=term-missing \
            --cov-fail-under=80 \
            --tb=short \
            -q

      - name: Upload coverage (3.12 only)
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/

  # 통합 테스트 — PR에서 실행
  integration:
    runs-on: ubuntu-latest
    needs: unit   # 단위 테스트 통과 후 실행

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-xdist

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        run: |
          pytest tests/integration -n auto --tb=short -q

  # E2E 테스트 — main 브랜치 push에만 실행
  e2e:
    runs-on: ubuntu-latest
    needs: [unit, integration]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt pytest playwright pytest-playwright
          playwright install chromium

      - name: Run E2E tests
        run: |
          pytest tests/e2e \
            --headed=false \
            --tb=short \
            -v

      - name: Upload E2E artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-screenshots
          path: tests/e2e/screenshots/
```

이 워크플로는 단위 테스트 → 통합 테스트 → E2E 순서로 실행됩니다. 단위 테스트가 먼저 실패하면 통합 테스트와 E2E는 건너뜁니다. 빠른 피드백을 먼저 받을 수 있습니다.

## 계층별 실행 시간 기준

CI 설정에서 가장 중요한 숫자 중 하나는 총 실행 시간입니다. 테스트가 아무리 좋아도 PR 하나 확인하는 데 20분이 걸리면 팀은 우회로를 찾기 시작합니다.

| 계층 | 목표 실행 시간 | 실행 트리거 | 비고 |
|---|---|---|---|
| 단위 테스트 | 2분 이내 | 모든 PR | pytest-xdist 병렬화 |
| 통합 테스트 | 5분 이내 | 모든 PR | DB 서비스 컨테이너 |
| 회귀 테스트 | 3분 이내 | 모든 PR | 마커로 분리 |
| E2E 테스트 | 15분 이내 | main push, 야간 | 브라우저 자동화 |
| 전체 스위트 | 10분 이내 | main push | 병렬 잡 분리 |

속도는 품질과 별개가 아니라 품질을 지속시키는 조건입니다.

## 플래키 테스트 감지와 관리

CI에서만 간헐적으로 깨지는 테스트는 로컬 재현이 어렵습니다. 다음 전략이 도움이 됩니다.

**pytest-rerunfailures로 자동 재시도**

```bash
pip install pytest-rerunfailures
```

```python
# 특정 테스트에만 재시도 설정
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_external_health_check():
    response = requests.get("https://api.example.com/health", timeout=5)
    assert response.status_code == 200
```

```bash
# 전체 테스트에 재시도 적용 (임시 방편)
pytest tests/e2e --reruns 2 --reruns-delay 1
```

재시도는 근본 원인 해결이 아니라 임시 방편입니다. 플래키 테스트 목록을 분기마다 리뷰하는 것이 중요합니다.

**플래키 테스트 자동 감지**

```python
# tests/conftest.py
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.outcome == "failed":
        # CI 환경에서만 플래키 로그 수집
        import os
        if os.getenv("CI"):
            print(f"\n[FLAKY CANDIDATE] {item.nodeid}", flush=True)
```

**CI에서 실패 아티팩트 저장**

```yaml
- name: Run tests
  run: pytest --tb=short
  continue-on-error: true

- name: Upload failure logs
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: test-failure-logs-${{ github.run_id }}
    path: |
      pytest-logs/
      tests/e2e/screenshots/
    retention-days: 7
```

실패 시에만 로그를 업로드하면 스토리지 사용량을 줄일 수 있습니다.

## 플래키 테스트의 주요 원인과 대응

| 원인 | 증상 | 해결책 |
|---|---|---|
| 실행 순서 의존 | 단독 실행은 통과, 전체 실행에서 실패 | 테스트 간 상태 격리, `autouse` fixture 정리 |
| 외부 자원 의존 | 네트워크 타임아웃, API 응답 불안정 | Mock으로 대체 또는 재시도 로직 |
| 시간 기반 로직 | 자정이나 월말에만 실패 | `freezegun`으로 시간 고정 |
| 공유 DB 상태 | 병렬 실행 시 데이터 충돌 | 각 테스트에 격리된 트랜잭션 또는 스키마 |
| 랜덤 순서 의존 | 간헐적으로만 실패 | `pytest --randomly-seed=last`로 재현 |

**freezegun으로 시간 고정하기**

```python
from freezegun import freeze_time
import pytest

@freeze_time("2026-01-15 10:00:00")
def test_subscription_expires_after_30_days():
    sub = Subscription(start_date="2026-01-15")
    assert not sub.is_expired()    # 시작 당일

@freeze_time("2026-02-15 10:00:01")
def test_subscription_is_expired_after_31_days():
    sub = Subscription(start_date="2026-01-15")
    assert sub.is_expired()        # 31일 후
```

## 비밀 값 관리

테스트 자동화가 늘어날수록 비밀 관리도 더 엄격해야 합니다.

```yaml
# GitHub Secrets 사용
- name: Run integration tests
  env:
    API_KEY: ${{ secrets.TEST_API_KEY }}
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
  run: pytest tests/integration
```

**절대 하지 말아야 할 것**

```yaml
# 잘못된 예 — 비밀 값을 직접 노출
- run: |
    export API_KEY="sk-prod-actual-key-here"  # CI 로그에 노출됨
    pytest tests/
```

로그에 비밀 값이 찍히면 테스트 안정성보다 먼저 보안 사고로 이어질 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|---|---|---|
| 모든 E2E를 모든 PR에서 실행 | CI 시간 20분 이상, 팀이 PR을 미룸 | 단위/통합 PR 필수, E2E는 main push에 분리 |
| 캐시 없이 의존 설치 | 매 실행마다 pip install 2~3분 소요 | `cache: 'pip'` 또는 캐시 키 설정 |
| 플래키 테스트 방치 | CI 결과를 신뢰하지 않게 됨 | 분기마다 플래키 목록 리뷰, 격리 또는 삭제 |
| 로컬과 CI 명령이 다름 | 로컬 통과 = CI 통과가 보장되지 않음 | Makefile로 명령 통일 |
| 비밀 값 하드코딩 | CI 로그에 키 노출 | GitHub Secrets 사용 |
| 실패 이유를 로그에서 찾기 어려움 | 디버깅에 오랜 시간 소요 | `--tb=short`, 아티팩트 업로드 설정 |

## 실무에서는 이렇게 생각합니다

큰 팀일수록 테스트 계층을 잡 단위로 나눕니다. 단위 테스트는 1~2분, 통합 테스트는 5분 안팎, E2E는 15분 정도로 별도 운영하는 식입니다. PR에는 빠른 계층만 필수로 걸고, 무거운 계층은 야간이나 머지 뒤 검증으로 옮깁니다.

경험 많은 엔지니어는 빨간 PR이 머지되는 일을 시스템 실패로 봅니다. 개인 실수로 넘기지 않습니다. 머지 규칙, 브랜치 보호, 캐시 전략, 플래키 테스트 격리까지 모두 운영 설계의 일부로 다룹니다.

CI 파이프라인의 평균 실행 시간을 팀 메트릭으로 추적하는 것도 좋은 습관입니다. 시간이 늘어나기 시작하면 어떤 계층이 병목인지 찾아 최적화 우선순위를 정할 수 있습니다.

## 운영 체크리스트

- [ ] `.github/workflows/test.yml`이 존재합니다.
- [ ] 단위 테스트는 모든 PR에서 2분 이내에 끝납니다.
- [ ] 의존 캐시를 켰습니다.
- [ ] 실패한 PR은 머지되지 않도록 브랜치 보호 규칙을 설정했습니다.
- [ ] 비밀 값을 GitHub Secrets로 관리합니다.
- [ ] 플래키 테스트 목록을 분기마다 리뷰합니다.
- [ ] 실패 시 로그나 스크린샷 아티팩트를 수집합니다.

## 연습 문제

1. 프로젝트에 `test.yml` 워크플로를 추가하고 첫 초록색 빌드를 만들어 보세요.
2. Python 3.11과 3.12를 매트릭스에 추가해 보세요.
3. `pytest-xdist`를 도입하고 실행 전후 시간을 비교해 기록해 보세요.
4. 단위 테스트와 통합 테스트를 별도 잡으로 분리하고 `needs`로 연결해 보세요.

## 정리

CI는 테스트를 팀 공통 기준으로 바꾸는 장치입니다. 노트북에서 우연히 통과한 결과를, 누구에게나 같은 방식으로 검증된 결과로 바꿔 줍니다. 계층별로 잡을 분리하고, 캐시로 속도를 유지하고, 플래키 테스트를 정기적으로 정리하면 CI가 팀의 안전망이 됩니다.

다음 글에서는 지금까지 본 모든 계층을 묶어 팀에 맞는 테스트 전략을 세우는 방법을 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- **Testing 101 (9/10): CI에서 테스트 실행하기 (현재 글)**
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko

### 공식 문서

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [Caching dependencies to speed up workflows](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

### 실무 참고

- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)

Tags: Testing, CI, GitHub Actions, Automation, Quality
