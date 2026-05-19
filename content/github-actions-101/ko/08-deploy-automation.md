---
series: github-actions-101
episode: 8
title: 배포 자동화
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
  - Deploy
  - Environments
  - OIDC
  - CICD
seo_description: GitHub Environments, 승인, OIDC 기반의 안전한 배포 자동화를 정리합니다.
last_reviewed: '2026-05-15'
---

# 배포 자동화

배포를 사람이 직접 수행하는 팀은 결국 같은 문제를 겪습니다. 누가 어떤 명령을 쳤는지 기록이 없고, staging은 자동인데 production은 메신저로 승인받고, 롤백 절차는 문서 어딘가에만 남아 있어 새벽 장애 때 바로 찾지 못합니다. 배포는 빨라야 하지만, 그보다 먼저 재현 가능해야 합니다.

이 글은 GitHub Actions 101 시리즈의 8번째 글입니다. 여기서는 GitHub Environments, 승인 게이트, OIDC, 롤백 워크플로우를 중심으로 배포 자동화를 어떻게 안전하게 설계할지 살펴보겠습니다.

## 이 글에서 다룰 문제

> 좋은 배포 자동화는 모든 단계를 무조건 자동으로 만드는 것이 아닙니다. 자주 해도 되는 일은 자동화하고, 위험한 구간만 승인 게이트로 좁게 막아야 속도와 안전을 함께 가져갈 수 있습니다.

- staging 자동 배포와 production 승인 게이트는 어떻게 나눌까요?
- GitHub Environments는 왜 배포 정책의 중심이 될까요?
- OIDC는 장기 클라우드 키를 어떻게 대체할까요?
- 롤백도 왜 워크플로우로 관리해야 할까요?
- staging과 production 매니페스트가 갈라지면 어떤 문제가 생길까요?

## 왜 중요한가

수동 배포는 재현성을 잃기 쉽습니다. 같은 사람이 같은 문서를 보고 실행해도 환경 변수, 명령 순서, 현재 체크아웃 상태가 조금만 달라지면 결과가 달라질 수 있습니다. 반대로 배포를 워크플로우로 만들면 어떤 커밋이 어떤 절차를 거쳐 어느 환경에 배포됐는지 한눈에 추적할 수 있습니다.

저는 배포 자동화의 가치를 속도보다 기록성에서 더 크게 봅니다. 기록이 남아야 사고가 나도 원인을 좁힐 수 있고, 승인 절차도 운영 규칙으로 남길 수 있습니다. GitHub Actions는 이 기록을 코드와 함께 묶는 데 잘 맞습니다.

## 한눈에 보는 배포 흐름

![main 머지 뒤 staging 자동 배포와 production 승인 게이트로 이어지는 배포 흐름](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/08/08-01-diagram.ko.png)

*main 머지 뒤 staging 자동 배포와 production 승인 게이트로 이어지는 배포 흐름*

이 흐름에서 핵심은 역할 분리입니다. staging은 빠른 자동 반영, production은 의식적인 승인 후 반영입니다. 둘을 같은 방식으로 다루면 배포 정책이 흐려집니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| Environment | GitHub의 배포 환경 단위 | staging, production 정책을 분리하기 좋습니다 |
| Required reviewers | 환경별 승인자 | production 게이트를 코드와 연결합니다 |
| OIDC | 단기 토큰 기반 클라우드 신뢰 | 장기 액세스 키를 줄이는 핵심 수단입니다 |
| Promotion | staging에서 production으로 승격 | 검증된 산출물을 다음 단계로 넘깁니다 |
| Rollback | 직전 안정 배포로 되돌리기 | 운영 절차도 자동화 대상입니다 |

## 자동화 전과 후를 비교해 보겠습니다

수동 배포에서는 누군가 로컬 터미널에서 `kubectl apply`를 실행합니다. 어떤 매니페스트를 썼는지, 어떤 이미지 태그가 반영됐는지, 중간에 무슨 경고가 있었는지 모두 사람 기억에 의존하게 됩니다. 이 구조에서는 실수가 있어도 되짚기가 어렵습니다.

반대로 PR 머지 후 staging으로 자동 배포하고, production은 승인 후 같은 흐름으로 올리면 모든 단계가 Actions 로그와 환경 기록에 남습니다. 이 차이는 장애 대응 속도와도 직접 연결됩니다.

## 배포 자동화를 5단계로 구성해 보겠습니다

### 1단계 — 환경을 먼저 정의하기

```text
Repo > Settings > Environments
- staging: no protection rules
- production: 1 required reviewer, 5-min wait timer
```

배포 코드를 쓰기 전에 환경 정책부터 정리하는 이유는 분명합니다. 어떤 환경에 자동 반영이 허용되고, 어떤 환경은 사람 승인 후에만 넘어갈지를 먼저 결정해야 하기 때문입니다.

### 2단계 — staging 자동 배포 만들기

```yaml
deploy-staging:
  needs: build
  environment: staging
  runs-on: ubuntu-latest
  steps:
    - run: kubectl apply -f k8s/staging/
```

staging은 배포 자체보다 빠른 검증 통로라는 성격이 강합니다. 따라서 main 기준으로 자동 배포하는 패턴이 자연스럽습니다.

### 3단계 — production 승인 게이트 붙이기

```yaml
deploy-production:
  needs: deploy-staging
  environment:
    name: production
    url: https://app.example.com
  runs-on: ubuntu-latest
  steps:
    - run: kubectl apply -f k8s/production/
```

여기서 중요한 것은 `environment` 한 줄이 단순한 라벨이 아니라 정책과 연결된다는 점입니다. production에 required reviewers를 걸어 두었다면, 이 잡은 승인 없이는 आगे로 못 갑니다.

### 4단계 — OIDC로 단기 자격 증명 쓰기

```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
      aws-region: us-west-2
  - run: aws s3 sync ./build s3://my-bucket
```

장기 AWS 키를 secret으로 오래 보관하는 구조는 위험합니다. OIDC는 실행 시점에만 짧게 신뢰를 받아 쓰는 방식이라 유출 면적을 줄이기에 훨씬 좋습니다.

### 5단계 — 롤백도 워크플로우로 만들기

```yaml
on:
  workflow_dispatch:
    inputs:
      sha:
        description: "git sha to roll back to"
        required: true
jobs:
  rollback:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh ${{ inputs.sha }}
```

롤백 절차가 문서에만 있으면 새벽 사고 때 찾기 어렵습니다. 실행 가능한 워크플로우로 만들어 두면 운영자가 훨씬 빠르게 대응할 수 있습니다.

## 여기까지 했을 때 기대할 결과

```text
deploy-staging  Pass
waiting on environment protection rules for production
deploy-production  Pending approval
```

이런 형태로 staging은 자동으로 끝나고, production은 environment 규칙 때문에 대기 상태로 멈추면 의도한 구조에 가깝습니다. 승인 뒤 production 잡이 같은 산출물과 같은 매니페스트를 사용해 이어져야 진짜 승격 흐름이 됩니다.

## 배포가 막히거나 실패하면 먼저 볼 지점

- **production이 바로 실행된다면**: repository 설정의 Environment protection rules가 실제로 연결됐는지 확인합니다.
- **OIDC 인증이 실패한다면**: `id-token: write` 권한과 클라우드 쪽 trust policy의 audience, subject 조건을 먼저 봅니다.
- **staging과 production 결과가 다르다면**: 이미지 태그나 매니페스트가 환경마다 달라진 것은 아닌지 점검합니다. 승격은 같은 산출물을 옮기는 흐름이어야 합니다.

## 자동 반영 구간과 승인 구간을 섞지 않는 편이 좋습니다

staging은 빠른 피드백 채널이므로 자동 반영이 맞는 경우가 많습니다. 반대로 production은 사람 승인, wait timer, 환경별 secret, 배포 URL 추적까지 함께 묶어 두는 편이 안전합니다. 둘을 같은 정책으로 다루면 결국 staging은 느려지고 production은 가벼워지는 어색한 구조가 되기 쉽습니다.

## 이 코드에서 먼저 봐야 할 점

- `environment` 선언만으로 승인 게이트를 연결할 수 있습니다.
- OIDC는 장기 키를 줄이는 가장 중요한 보안 개선 중 하나입니다.
- 롤백 역시 배포만큼 코드화해야 합니다.

즉, 배포 자동화의 성숙도는 “자동 배포가 된다”보다 “정책과 예외 흐름이 코드에 남아 있다”로 판단하는 편이 맞습니다.

## 자주 하는 실수 다섯 가지

1. production에 required reviewers를 두지 않습니다.
2. 장기 AWS 키를 secret에 그대로 저장합니다.
3. 롤백 절차를 문서에만 적어 둡니다.
4. staging과 production에 서로 다른 매니페스트를 쌓아 표류를 만듭니다.
5. 배포 결과를 Slack이나 이슈에 남기지 않습니다.

네 번째 실수는 특히 교묘합니다. 환경별 차이를 이유로 매니페스트를 따로 굴리기 시작하면, 결국 “staging에서는 되는데 production에서는 안 되는” 종류의 드리프트가 쌓이기 쉽습니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 PR 머지부터 카나리, 블루/그린, 전체 롤아웃까지를 하나의 흐름으로 관리합니다. 그리고 그 과정에서 메트릭 확인, 알림, 롤백 기준까지 자동화에 묶습니다. 배포 자동화는 결국 운영 정책 자동화에 가깝습니다.

또한 staging과 production을 최대한 같은 산출물과 같은 매니페스트로 다루려는 태도가 중요합니다. 환경마다 완전히 다른 것을 배포한다면 승격 개념 자체가 약해집니다.

## 체크리스트

- [ ] GitHub Environments가 정의돼 있다.
- [ ] production에는 승인자가 설정돼 있다.
- [ ] OIDC로 클라우드 인증을 수행한다.
- [ ] 롤백 워크플로우가 존재한다.

## 연습 문제

1. main push에서 staging으로 자동 배포되는 환경을 만들어 보세요.
2. production 환경에 승인 게이트를 추가해 보세요.
3. `workflow_dispatch` 기반 롤백 워크플로우를 작성해 보세요.

## 정리

배포 자동화의 목표는 무조건 빠른 배포가 아니라 재현 가능한 배포입니다. staging 자동 배포, production 승인, OIDC, 롤백 워크플로우를 함께 설계하면 배포 속도와 운영 안정성을 동시에 가져갈 수 있습니다.

다음 글에서는 Secret 관리를 다룹니다. 배포가 자동화될수록 비밀값 노출 면적도 넓어지므로, 자격 증명과 권한을 어떤 원칙으로 다룰지 함께 정리해야 합니다.

<!-- toc:begin -->
- [GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [Workflow와 Job](./02-workflow-and-job.md)
- [Trigger 이해하기](./03-triggers.md)
- [Python 테스트 자동화](./04-python-test-automation.md)
- [Lint와 Type Check](./05-lint-and-typecheck.md)
- [빌드 아티팩트](./06-build-artifact.md)
- [Docker 빌드](./07-docker-build.md)
- **배포 자동화 (현재 글)**
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)
<!-- toc:end -->

## 참고 자료

- [Using environments for deployment](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Configuring OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)

Tags: GitHubActions, Deploy, Environments, OIDC, CICD
