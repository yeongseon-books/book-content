---
series: devops-101
episode: 2
title: CI 파이프라인
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - CI
  - GitHub Actions
  - Automation
  - Pipeline
seo_description: 빌드, 테스트, 린트, 보안 검사를 자동화하는 CI 파이프라인 설계와 구현법.
last_reviewed: '2026-05-04'
---

# CI 파이프라인

> DevOps 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *모든 PR* 에 *같은 검증* 을 들이대는 *하나의 파이프* 가 있나요?

> CI 파이프라인은 *팀의 기준선* 입니다. *합격선이 코드로* 박제됩니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *CI 파이프라인* 의 정의와 단계
- 단계별 *책임 분리* (build/test/lint/scan)
- *빠른 피드백* 을 위한 설계
- *실패한 빌드* 의 명확한 신호
- 흔한 함정 5가지

## 왜 중요한가

테스트만으로는 부족합니다. *린트, 타입, 보안 스캔* 까지 *한 흐름* 으로 묶어야 *주관* 이 끼어들지 않습니다.

> CI 없는 PR은 *희망회로* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Push["push/PR"] --> Lint["lint"]
    Lint --> Build["build"]
    Build --> Test["test"]
    Test --> Scan["security scan"]
    Scan --> Pass["green check"]
```

## 핵심 용어 정리

- **Pipeline**: *순서 있는 단계들* 의 집합.
- **Stage**: 파이프라인 안의 *논리적 단위* (build, test 등).
- **Job**: 실제 *실행 단위*. 병렬 가능.
- **Artifact**: 단계 사이에 *전달되는 파일*.
- **Status check**: PR이 머지 가능한지 *결정하는 신호*.

## Before/After

**Before (수동 검증)**

```text
- 리뷰어가 *체크아웃 후 직접 빌드*
- 누가 빠뜨리면 *빨간 코드* 가 main에 진입
```

**After (CI 파이프라인)**

```yaml
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check .
  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

## 실습: 파이프라인 5단계

### 1단계 — Lint (가장 빠름, 먼저)

```yaml
- run: ruff check .
- run: ruff format --check .
```

### 2단계 — Type check

```yaml
- run: mypy src/
```

### 3단계 — Build

```yaml
- run: python -m build
- uses: actions/upload-artifact@v4
  with: { name: dist, path: dist/ }
```

### 4단계 — Test (병렬)

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pytest --shard ${{ matrix.shard }}/4
```

### 5단계 — Security scan

```yaml
- uses: aquasecurity/trivy-action@master
  with: { scan-type: fs, severity: HIGH,CRITICAL }
```

## 이 코드에서 주목할 점

- *빠른 단계* 가 *먼저* 와야 *빠른 실패* 가 가능합니다.
- 단계 간 *artifact* 로 *재빌드 비용* 을 줄입니다.
- 보안 스캔은 *마지막 게이트* 로 둡니다.

## 자주 하는 실수 5가지

1. **모든 단계를 *직렬* 로.** 병렬화로 *50%* 까지 단축 가능합니다.
2. **린트를 *마지막* 에 둠.** 30분 빌드 후 *공백 1줄* 으로 빨간색.
3. **CI에서만 *동작하는 환경*.** 로컬 재현이 어려워 *디버깅 지옥*.
4. **Required check 미설정.** 빨간 PR이 *그냥 머지* 됩니다.
5. **로그가 *너무 길어* 원인 못 찾음.** *요약 단계* 를 추가하세요.

## 실무에서는 이렇게 쓰입니다

큰 모노레포는 *변경된 패키지만* 빌드/테스트하는 *영향 분석* 을 적용합니다. Bazel, Nx, Turbo 등이 대표적입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *5분 룰* — PR 피드백은 5분 안에 와야 한다.
- *실패 시 다음 단계* 를 *건너뛴다*.
- *재현 가능성* — CI는 *결정적* 이어야 한다.
- *시크릿* 은 *환경 분리*.
- *파이프라인도 코드 리뷰* 의 대상이다.

## 체크리스트

- [ ] *Lint, type, test, scan* 이 모두 있다.
- [ ] *Required check* 가 설정되어 있다.
- [ ] *피드백 5분* 이내.
- [ ] *artifact* 로 단계가 연결된다.

## 연습 문제

1. 본인 프로젝트의 CI를 *4단계 이상* 으로 분리해보세요.
2. *병렬화* 로 시간을 *측정/비교* 하세요.
3. *required check* 를 PR 머지 조건에 추가하세요.

## 정리 및 다음 단계

CI 파이프라인은 *합격선의 코드화* 입니다. 다음 글에서는 *통과한 코드* 를 어떻게 *안전하게 배포* 할지 다룹니다.

<!-- toc:begin -->
- [DevOps란 무엇인가?](./01-what-is-devops.md)
- **CI 파이프라인 (현재 글)**
- CD와 배포 전략 (예정)
- 환경 분리와 설정 관리 (예정)
- Infrastructure as Code (예정)
- 컨테이너와 빌드 (예정)
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [Trivy](https://trivy.dev/)
- [Bazel](https://bazel.build/)

Tags: DevOps, CI, GitHub Actions, Automation, Pipeline
