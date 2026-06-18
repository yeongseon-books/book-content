---
series: testing-101
episode: 9
title: "바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기"
status: content-ready
targets:
  wordpress: true
  tistory: false
  medium: false
  hashnode: false
  mkdocs: false
  ebook: false
language: ko
tags:
  - 바이브코딩
  - Testing
  - CI
  - GitHub Actions
  - Automation
  - Quality
seo_description: AI가 만든 코드가 PR마다 자동으로 검증되는 CI 환경 구축하기. GitHub Actions로 바이브코딩 팀의 테스트를 팀 공통 안전망으로 만드는 방법.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 아홉 번째 글입니다. AI가 만든 코드가 PR마다 자동으로 검증되는 CI 환경을 구축하는 방법을 설명합니다.

---

바이브코딩 팀에서는 코드 변경이 매우 자주 일어납니다. AI에게 기능을 추가하고, 리팩토링하고, 버그를 수정하는 일이 빠르게 반복됩니다. 이 속도에서 테스트를 개인 습관에만 맡기면 반드시 구멍이 생깁니다. "로컬에서 됐는데요"라는 말이 반복되는 팀은 CI가 없는 팀입니다.

CI는 AI가 만든 코드가 팀 전체 기준에서 검증되도록 강제합니다. 테스트 실행이 선택이 아니라 기본 경로가 됩니다.

> CI 없는 테스트는 개발자의 책임이지만, CI가 있는 테스트는 팀 전체의 안전망이 됩니다.

## 이 글에서 다룰 문제

- CI는 바이브코딩 팀에 왜 특히 더 중요할까요?
- GitHub Actions 워크플로는 어떤 구조로 작성할까요?
- AI가 만든 코드의 테스트를 CI에 연결하는 최소 구성은 무엇일까요?
- CI에서만 깨지는 플래키 테스트를 어떻게 다룰까요?
- AI 코드 PR마다 자동 검증 흐름을 어떻게 만들까요?

바이브코딩 환경에서 CI는 "AI가 만든 코드가 팀의 기준을 통과했는가"를 자동으로 확인하는 게이트입니다. 이 게이트 없이는 AI 코드의 품질이 개인의 성실함에만 의존하게 됩니다.

## 한눈에 보는 구조

AI가 코드를 수정하고 PR을 올리면 워크플로가 실행되고, 테스트를 돌리고, 결과를 알려 줍니다. 테스트가 실패하면 머지가 막힙니다.

- **CI**: Continuous Integration의 약자. AI 코드를 포함한 모든 커밋을 자동으로 검증합니다.
- **워크플로(workflow)**: GitHub Actions에서 실행 규칙을 정의한 YAML 파일입니다.
- **매트릭스(matrix)**: 여러 파이썬 버전 조합을 병렬 실행하는 설정입니다.
- **캐시(cache)**: 의존 설치 결과를 재사용해 시간을 줄이는 방식입니다.
- **아티팩트(artifact)**: 커버리지 보고서처럼 CI가 남기는 파일입니다.

## CI 서비스 비교

| CI 서비스 | 무료 한도 | 권장 상황 |
|---|---|---|
| GitHub Actions | 2000분/월 (public 무제한) | GitHub 저장소 기본 선택 |
| GitLab CI | Shared runner 400분/월 | GitLab 저장소 |
| Jenkins | self-hosted 무제한 | 온프레미스 환경 |

바이브코딩 팀에는 GitHub Actions가 설정이 가장 간단하고 GitHub PR 워크플로와 잘 통합됩니다.

## 바꾸기 전과 후

**바꾸기 전 — AI 코드를 수동으로만 확인**

```text
- AI가 PR을 만들 때 테스트를 돌리는 것은 개인 몫
- 한 번 빠뜨리면 실패한 코드가 그대로 머지됨
- "로컬에서는 됐어요" 반복
```

**바꾼 뒤 — CI로 AI 코드 자동 검증**

```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: pytest -v
# AI가 PR을 올리면 자동으로 이 워크플로가 실행됨
```

## 다섯 단계로 GitHub Actions 구성하기

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
    with: { python-version: ${{ matrix.python-version }} }
```

### 3단계 — 의존 캐시 켜기

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'pip'
- run: pip install -r requirements.txt
```

### 4단계 — 병렬 실행으로 피드백 시간 줄이기

```bash
pip install pytest-xdist
pytest -n auto  # CPU 코어 기준 병렬 실행
```

### 5단계 — 커버리지 결과 아티팩트로 저장

```yaml
- run: pytest --cov=src --cov-report=html
- uses: actions/upload-artifact@v4
  with:
    name: coverage-html
    path: htmlcov/
```

## 바이브코딩 팀을 위한 완전한 GitHub Actions 워크플로

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=html --cov-report=term

      - name: Upload coverage report
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

## CI에서만 깨지는 플래키 테스트 다루기

바이브코딩에서 AI가 만든 코드에는 CI에서만 간헐적으로 깨지는 테스트가 생기기 쉽습니다. 주요 원인과 해결 방법입니다.

| 원인 | 증상 | 해결책 |
|---|---|---|
| `time.sleep` 과도 사용 | 타이밍에 따라 실패 | 조건부 대기로 교체 |
| 테스트 간 상태 공유 | 실행 순서에 따라 실패 | fixture 격리 |
| 외부 API 직접 호출 | 네트워크 상태에 따라 실패 | Mock/Stub으로 대체 |
| 전역 변수 사용 | 병렬 실행 시 실패 | 의존성 주입으로 수정 |

## AI에게 CI 통과 코드 요청하기

```text
효과적인 프롬프트:
"다음 GitHub Actions 워크플로에서 테스트가 통과하도록
코드를 작성해 줘:

[워크플로 YAML 첨부]

특히 외부 API는 Mock을 사용하고,
time.sleep 대신 조건부 대기를 사용해 줘."
```

## 자주 하는 실수

첫 번째 문제는 CI에서만 플래키하게 깨지는 테스트입니다. AI가 만든 코드에는 `time.sleep`, 외부 API 직접 호출, 전역 상태 의존이 포함될 수 있습니다.

둘째, 모든 E2E 테스트를 PR마다 돌리는 구성입니다. 바이브코딩에서 빠른 피드백이 중요합니다. 단위 테스트와 통합 테스트는 PR에서, E2E는 야간이나 머지 뒤에 돌리세요.

셋째, 로그에 비밀 값(API 키, DB 비밀번호)이 찍히는 실수입니다. AI가 만든 테스트 코드에 하드코딩된 비밀 값이 없는지 확인하세요.

## 운영 체크리스트

- [ ] `.github/workflows/test.yml`이 존재합니다.
- [ ] AI가 PR을 올리면 자동으로 테스트가 실행됩니다.
- [ ] 의존 캐시를 켰습니다.
- [ ] 테스트가 실패한 PR은 머지되지 않도록 설정했습니다.
- [ ] E2E 테스트는 PR 필수 검증과 분리했습니다.

## 처음 질문으로 돌아가기

- **CI는 바이브코딩 팀에 왜 특히 더 중요할까요?**
  AI가 코드를 빠르게 많이 만들고 수정하기 때문에 수동 검증만으로는 따라갈 수 없습니다. CI가 모든 변경을 자동으로 검증합니다.

- **AI가 만든 코드의 테스트를 CI에 연결하는 최소 구성은?**
  `push`와 `pull_request` 트리거에 `pytest` 실행 단계를 추가하는 것이 최소입니다.

- **CI에서만 깨지는 플래키 테스트를 어떻게 다룰까요?**
  원인 파악이 우선입니다. `time.sleep`, 외부 API, 공유 상태를 제거하고 조건부 대기와 Mock을 사용합니다.

## 정리

CI는 AI가 만든 코드를 개인 확인에서 팀 공통 검증으로 바꾸는 핵심 장치입니다. PR마다 테스트가 자동 실행되면 AI가 실수한 코드는 머지 전에 발견됩니다. 다음 글에서는 지금까지 본 모든 계층을 묶어 바이브코딩 팀에 맞는 테스트 전략을 세우는 방법을 정리하겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- **바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, CI, GitHub Actions, Automation, Quality
