---
title: "바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기"
series: github-actions-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Trigger
- Schedule
- CICD
seo_description: "바이브코딩 프로젝트에서 CI 비용을 줄이고 필요한 시점에만 자동화를 실행하는 트리거 설계를 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 3번째 글입니다.

바이브코딩으로 코드를 빠르게 만들다 보면 커밋이 잦아집니다. AI에게 조금씩 수정을 요청하면서 금방 10번, 20번 push가 쌓입니다. CI가 매번 전체 파이프라인을 돌리면 어느 순간 GitHub Actions 사용량이 예상보다 훨씬 많아져 있습니다. 문서 파일 하나 고쳤는데 5분짜리 빌드가 돌고, 같은 PR에 연속으로 push를 했더니 이전 실행들이 대기열에 쌓여 있습니다.

트리거 설계는 "언제 실행할까"뿐 아니라 "언제 실행하지 않을까"를 함께 결정하는 일입니다. `paths` 필터로 코드 파일이 바뀔 때만 CI를 돌리고, `concurrency`로 중복 실행을 취소하고, `schedule`로 무거운 테스트는 야간에만 돌리면 비용과 피드백 속도를 동시에 잡을 수 있습니다. 바이브코딩처럼 커밋 빈도가 높은 환경일수록 트리거 설계가 더 중요합니다.

> 트리거 설계는 자동화가 언제 실행되는가를 정하는 일이자, 불필요한 실행에 돈과 시간을 쓰지 않는 정책 결정입니다.

---

## 이 글에서 다룰 문제
- push와 pull_request 트리거는 각각 어떤 상황에 쓰는 편이 맞을까요?
- `paths` 필터는 어떻게 비용을 줄여 줄까요?
- `schedule`의 cron 표현식에서 UTC와 KST를 혼동하면 어떤 일이 생길까요?
- `workflow_dispatch`는 바이브코딩 배포 과정에서 어떻게 활용할 수 있을까요?
- 같은 PR에 연속 push할 때 대기열이 쌓이는 문제를 어떻게 해결할까요?

---

## 트리거를 잘 설계하면 달라지는 것

바이브코딩 프로젝트에서 AI의 도움을 받아 코드를 자주 수정하는 상황을 상상해 봅니다. `docs/README.md` 한 줄을 고쳤는데 pytest가 3분 동안 돌아갑니다. PR에 5번 연속으로 push했더니 5개 실행이 대기열에 쌓였고, 앞의 4개는 이미 의미 없어진 상태입니다.

`paths` 필터 하나로 첫 번째 문제가 해결됩니다. `concurrency`로 두 번째 문제가 해결됩니다.

### 핵심 용어 정리

| 트리거 | 언제 실행되나 | 주로 쓰는 상황 |
|--------|------------|------------|
| `push` | 브랜치에 커밋이 들어올 때 | main에 반영된 코드 검증 |
| `pull_request` | PR이 열리거나 갱신될 때 | 빠른 피드백, 머지 전 게이트 |
| `schedule` | cron 기반 주기 실행 | 야간 전체 테스트, 취약점 스캔 |
| `workflow_dispatch` | 수동 실행 버튼 | 배포, 롤백, 긴급 운영 작업 |
| `paths` | 특정 파일 변경 시에만 실행 | 불필요한 실행 차단 |
| `concurrency` | 동시 실행 제어 | 대기열 낭비 방지 |

---

## Before / After

**모든 push에서 전체 파이프라인이 돌 때**

```yaml
on:
  push:
  pull_request:
```

문서 파일 수정, 테스트 추가, 소스 코드 변경이 모두 같은 무게로 전체 파이프라인을 실행합니다.

**트리거를 다듬은 버전**

```yaml
on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

`docs/` 아래 파일만 바뀌면 CI가 실행되지 않습니다. 같은 PR에 연속 push가 들어오면 이전 실행이 자동으로 취소됩니다. 비용이 줄고, 피드백이 더 빨라집니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `schedule` cron을 로컬 시간으로 작성 | UTC 기준이라 엉뚱한 시각에 실행됨 | UTC로 변환해서 작성합니다 |
| `concurrency` 없이 자주 push | 대기열에 불필요한 실행 누적 | `cancel-in-progress: true`를 추가합니다 |
| `paths` 없이 모든 변경에서 CI 실행 | 문서 수정에도 비용 발생 | 소스 코드 경로만 포함합니다 |
| `pull_request_target` 남용 | 외부 PR이 secret에 접근 가능해짐 | fork PR은 기본 `pull_request`를 씁니다 |
| `workflow_dispatch` 입력 문서화 안 함 | 운영자가 어떤 값을 넣어야 할지 모름 | `description`에 예시를 적습니다 |

## AI 팁: 트리거 설계 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions 워크플로우 트리거를 설계해줘.
요구사항:
- PR과 main push 시 src/, tests/, pyproject.toml이 변경된 경우만 실행
- 같은 브랜치의 중복 실행은 이전 것을 취소
- 한국 시간 새벽 2시에 전체 테스트를 야간 실행 (schedule)
- 배포를 수동으로 실행할 수 있는 버튼 추가 (staging/production 선택 가능)"
```

cron의 UTC 변환을 자동으로 해 주지만, 결과를 반드시 확인하세요. KST 새벽 2시는 UTC 17시(전날)입니다.

## 운영 체크리스트
- [ ] `paths` 필터로 불필요한 실행을 줄였는가?
- [ ] `concurrency`로 중복 실행을 막았는가?
- [ ] `schedule` cron이 UTC 기준으로 작성됐는가?
- [ ] `workflow_dispatch` 입력의 description이 있는가?
- [ ] push와 pull_request 트리거의 역할이 구분돼 있는가?

## 처음 질문으로 돌아가기

- **push와 pull_request 트리거의 차이는?**
  PR은 머지 전 빠른 피드백용이고, main push는 실제 기준 브랜치 코드를 검증하는 용도입니다. 두 트리거를 함께 쓸 때 PR 머지 시 중복 실행이 생길 수 있으므로 역할을 분명히 나눠야 합니다.

- **schedule의 UTC 변환은?**
  KST는 UTC+9이므로, KST 새벽 2시에 실행하려면 cron에 전날 UTC 17시를 적어야 합니다: `0 17 * * *`.

- **concurrency로 뭘 절약하나?**
  같은 PR에 빠르게 5번 push하면 5개의 실행이 대기열에 쌓입니다. `cancel-in-progress: true`는 새 실행이 시작되면 이전 실행을 취소합니다. 결국 마지막 실행만 유효하므로 러너 비용이 줄고 대기도 없어집니다.

## 정리

트리거는 자동화의 시작 시점이지만, 동시에 비용 정책이기도 합니다. 바이브코딩처럼 커밋이 잦은 환경일수록 `paths` 필터와 `concurrency`는 필수 설정입니다. 다음 글에서는 트리거가 실행한 워크플로우 안에서 Python 테스트를 제대로 자동화하는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [Events that trigger workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
- [Concurrency](https://docs.github.com/actions/using-jobs/using-concurrency)
### 관련 시리즈
- [DevOps 101](../../devops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- **바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Trigger, Schedule, CICD
