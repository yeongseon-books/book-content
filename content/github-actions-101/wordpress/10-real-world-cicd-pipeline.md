---
title: "바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인"
series: github-actions-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - GitHubActions
  - Pipeline
  - CICD
  - ReusableWorkflow
---

# 바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인

이 글은 "바이브코딩을 위한 GitHub Actions 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 단일 워크플로우 파일에 모든 것을 넣어줍니다. 하지만 실무에서는 trigger만 따로 존재하지 않고, 테스트, Docker 빌드, 배포, secret 관리가 하나의 흐름으로 엮입니다. 파이프라인은 부품의 개수가 아니라, 부품들이 어떤 책임으로 연결되어 있는가를 설명하는 구조입니다.

PR, main, tag를 서로 다른 단계로 분리하고, reusable workflow와 composite action으로 공통 부분을 재사용하는 방법을 정리합니다. 한 번 잘 만든 구조를 여러 저장소에서 오래 재사용하는 것이 목표입니다.

> **핵심 인사이트:** PR은 빠른 피드백, main은 통합과 staging, tag는 공식 릴리스와 production 승격. 세 단계의 책임이 분리될 때 reusable workflow도 자기 자리를 찾습니다.

## 이 글에서 다룰 문제

- PR, main, tag를 왜 서로 다른 책임으로 나눠야 할까요?
- reusable workflow는 어떤 중복을 줄여 줄까요?
- composite action은 어디까지 묶는 편이 좋을까요?
- 바이브코딩에서 AI가 만든 파이프라인의 구조적 문제는 무엇인가요?
- 파이프라인 성능을 어떻게 측정하고 개선할까요?

## 실전 파이프라인 구조

```yaml
# PR 단계: 빠른 피드백 (ci.yml)
on:
  pull_request:
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
    with:
      python-version: "3.12"

# main 단계: 통합 + staging (build.yml)
on:
  push:
    branches: [main]
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
  docker:
    needs: ci
    uses: org/template-repo/.github/workflows/_docker.yml@v1
  deploy-staging:
    needs: docker
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/staging/

# tag 단계: 공식 릴리스 + production (deploy-prod.yml)
on:
  push:
    tags: ["v*"]
jobs:
  deploy-prod:
    environment: production  # required reviewers ON
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/production/
```

## 변경 전후 비교

**Before: 모든 것을 하나의 워크플로우에**
```yaml
on: [push, pull_request]
jobs:
  everything:
    steps:
      - run: pytest
      - run: docker build
      - run: kubectl apply -f k8s/production/  # PR에서도 production 배포!
```

**After: 단계별 책임 분리**
```text
PR    → lint, test, typecheck (5분 피드백)
main  → build, docker, staging 배포
tag   → release, production 승인 배포
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 모든 PR에서 전체 e2e 실행 | 피드백이 느려 CI를 무시하게 됨 | PR은 빠른 검증만 |
| main에서 바로 production 직행 | staging 검증 없이 production 위험 | staging → production 단계 분리 |
| reusable workflow를 `@main`으로 호출 | 상위 변경이 갑자기 모든 저장소를 깨뜨림 | `@v1` 같은 버전 태그 고정 |
| 태그 없이 production 배포 | 어떤 버전이 나갔는지 추적 불가 | tag push를 production 승격 기준으로 |
| 저장소마다 다른 YAML 복사 | 유지비 상승, 표류 발생 | reusable workflow로 공통화 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"GitHub Actions 파이프라인을 PR/main/tag 단계로 나눠줘.
reusable workflow로 테스트 공통화,
production에는 승인 게이트,
비용 최적화를 위한 path filter와 concurrency 취소도 포함해야 해"

# 파이프라인 품질 확인:
- PR 피드백이 5분 안에 오는가
- staging 검증 후 production으로 승격하는가
- 같은 이미지가 staging → production으로 흐르는가
- rollback 워크플로우가 있는가
```

## 운영 체크리스트

- [ ] PR, main, tag 단계가 분리돼 있다
- [ ] 공통 검증을 reusable workflow로 추출했다
- [ ] production에는 승인 게이트(required reviewers)가 있다
- [ ] reusable workflow 호출 버전을 고정했다 (`@v1`)
- [ ] concurrency 취소로 중복 실행을 방지한다
- [ ] path filter로 불필요한 실행을 줄였다

## 처음 질문으로 돌아가기

- **PR, main, tag를 왜 나눠야 할까요?** 각 단계의 책임이 다르기 때문입니다. PR은 피드백, main은 통합, tag는 릴리스입니다.
- **reusable workflow의 가치는?** 공통 규칙을 한 곳에서 관리하고 저장소별 차이만 입력값으로 받으면 유지비가 크게 줄어듭니다.
- **composite action은 어디까지?** 스텝 수준 재사용에 씁니다. reusable workflow가 잡 단위라면 composite action은 스텝 단위입니다.

## 정리

실전 CI/CD 파이프라인은 부품을 많이 붙이는 작업이 아니라, 책임을 분명히 나눈 작은 흐름들을 조합하는 작업입니다. 바이브코딩에서 AI가 만들어 준 단일 워크플로우를 PR/main/tag로 분리하고, reusable workflow로 공통화하면 팀 전체의 CI/CD 품질이 올라갑니다. 이 시리즈를 통해 GitHub Actions의 전체 구조를 설계하는 능력을 갖추셨기를 바랍니다.

## 참고 자료

- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)
- [Creating a composite action](https://docs.github.com/actions/creating-actions/creating-a-composite-action)
- [DORA - Accelerate State of DevOps](https://dora.dev/)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?
- 바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job
- 바이브코딩을 위한 GitHub Actions 기초 (3/10): Trigger 이해하기
- 바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화
- 바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check
- 바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트
- 바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 빌드
- 바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화
- 바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 관리
- **바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, GitHubActions, Pipeline, CICD, ReusableWorkflow
