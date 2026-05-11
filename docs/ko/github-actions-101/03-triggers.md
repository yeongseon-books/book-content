---
series: github-actions-101
episode: 3
title: Trigger 이해하기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - GitHubActions
  - Trigger
  - Event
  - Schedule
  - CICD
seo_description: push, PR, schedule, workflow_dispatch까지. 워크플로우를 언제 돌릴지 정확히 통제하기.
last_reviewed: '2026-05-04'
---

# Trigger 이해하기

> GitHub Actions 101 시리즈 (3/10)


## 이 글에서 다룰 문제

트리거 설계가 *비용과 노이즈* 를 결정합니다. *모든 commit 마다 모든 워크플로우* 를 돌리면 *비용 폭발 + 알림 피로* 가 옵니다.

> *정확한 시점* 에만 도는 워크플로우가 *좋은 워크플로우* 입니다.

## 전체 흐름
```mermaid
flowchart LR
    Push["push"] --> WF["workflow"]
    PR["pull_request"] --> WF
    Cron["schedule"] --> WF
    Manual["workflow_dispatch"] --> WF
```

## Before/After

**Before**: docs만 고쳐도 *전체 빌드 + 테스트* 가 돈다.

**After**: `paths` 필터로 *코드 변경* 에서만 빌드가 돈다.

## Trigger 5단계

### 1단계 — push와 PR 분리

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### 2단계 — paths 필터로 비용 절감

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

### 3단계 — schedule(cron) 야간 빌드

```yaml
on:
  schedule:
    - cron: "0 17 * * 0-4"  # UTC 17:00 = KST 02:00, 일~목
```

### 4단계 — workflow_dispatch 수동 실행

```yaml
on:
  workflow_dispatch:
    inputs:
      env:
        description: "deploy target"
        required: true
        default: staging
        type: choice
        options: [staging, production]
```

### 5단계 — concurrency 로 중복 실행 방지

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

## 이 코드에서 주목할 점

- *paths-ignore* 보다 *paths* 가 *명시적* 입니다.
- *cron* 은 *UTC* 입니다. KST 변환 주의.
- *cancel-in-progress* 는 *PR 푸시 연타* 비용을 줄입니다.

## 자주 하는 실수 5가지

1. **모든 트리거에 *전체 워크플로우*.** 비용 폭발.
2. **`schedule` 을 *KST 로 적음*.** UTC 만 인정.
3. **`pull_request_target` 오용.** *secret 노출* 위험.
4. **`concurrency` 누락.** *중복 빌드* 가 큐를 막음.
5. **`workflow_dispatch` 만 두고 *문서 없음*.** 누가 어떻게 누르는지 모름.

## 실무에서는 이렇게 쓰입니다

성숙한 팀은 *PR* = *빠른 검증*, *main push* = *full test + build*, *nightly cron* = *느린 e2e*, *workflow_dispatch* = *프로덕션 배포* 로 트리거를 *역할별* 로 나눕니다.

## 체크리스트

- [ ] *paths 필터* 로 불필요한 실행 제거됨.
- [ ] *cron* 은 *UTC 로* 작성됨.
- [ ] *concurrency* 가 설정돼 있다.
- [ ] *workflow_dispatch* 가 문서화됐다.

## 정리 및 다음 단계

트리거는 *워크플로우의 시점* 입니다. 다음 글에서는 *Python 테스트 자동화* 를 다룹니다.

<!-- toc:begin -->
- [GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [Workflow와 Job](./02-workflow-and-job.md)
- **Trigger 이해하기 (현재 글)**
- Python 테스트 자동화 (예정)
- Lint와 Type Check (예정)
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)
<!-- toc:end -->

## 참고 자료

- [Events that trigger workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
- [Schedule events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
- [workflow_dispatch](https://docs.github.com/actions/using-workflows/manually-running-a-workflow)
- [Concurrency](https://docs.github.com/actions/using-jobs/using-concurrency)
