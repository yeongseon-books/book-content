---
series: github-actions-101
episode: 8
title: "GitHub Actions 101 (8/10): 배포 자동화"
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

# GitHub Actions 101 (8/10): 배포 자동화

배포를 사람이 직접 수행하는 팀은 결국 같은 문제를 겪습니다. 누가 어떤 명령을 쳤는지 기록이 없고, staging은 자동인데 production은 메신저로 승인받고, 롤백 절차는 문서 어딘가에만 남아 있어 새벽 장애 때 바로 찾지 못합니다. 배포는 빨라야 하지만, 그보다 먼저 재현 가능해야 합니다.

이 글은 GitHub Actions 101 시리즈의 8번째 글입니다. 여기서는 GitHub Environments, 승인 게이트, OIDC, 롤백 워크플로우를 중심으로 배포 자동화를 어떻게 안전하게 설계할지 봅니다.

![GitHub Actions 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/08/08-01-diagram.ko.png)
*GitHub Actions 101 8장 흐름 개요*

## 먼저 던지는 질문

- staging 자동 배포와 production 승인 게이트는 어떻게 나눌까요?
- GitHub Environments는 왜 배포 정책의 중심이 될까요?
- OIDC는 장기 클라우드 키를 어떻게 대체할까요?

## 왜 중요한가

수동 배포는 재현성을 잃기 쉽습니다. 같은 사람이 같은 문서를 보고 실행해도 환경 변수, 명령 순서, 현재 체크아웃 상태가 조금만 달라지면 결과가 달라질 수 있습니다. 반대로 배포를 워크플로우로 만들면 어떤 커밋이 어떤 절차를 거쳐 어느 환경에 배포됐는지 한눈에 추적할 수 있습니다.

저는 배포 자동화의 가치를 속도보다 기록성에서 더 크게 봅니다. 기록이 남아야 사고가 나도 원인을 좁힐 수 있고, 승인 절차도 운영 규칙으로 남길 수 있습니다. GitHub Actions는 이 기록을 코드와 함께 묶는 데 잘 맞습니다.

## 한눈에 보는 배포 흐름

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

여기서 중요한 것은 `environment` 한 줄이 단순한 라벨이 아니라 정책과 연결된다는 사실입니다. production에 required reviewers를 걸어 두었다면, 이 잡은 승인 없이는 आगे로 못 갑니다.

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

## 배포 전략별 워크플로우 설계

배포 방식에 따라 워크플로우 구조가 달라집니다. 주요 전략을 비교하겠습니다.

| 전략 | 동작 | 위험도 | 적합한 환경 |
| --- | --- | --- | --- |
| 직접 교체 | 기존 인스턴스를 새 버전으로 교체 | 높음 | 개발/테스트 |
| 블루-그린 | 새 환경을 띄우고 트래픽을 전환 | 중간 | 스테이징/프로덕션 |
| 카나리 | 일부 트래픽만 새 버전으로 | 낮음 | 프로덕션 |
| 롤링 | 인스턴스를 순차적으로 교체 | 중간 | 프로덕션 |

### 블루-그린 배포 워크플로우

```yaml
jobs:
  deploy-blue-green:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6

      - name: 새 환경 배포 (Green)
        run: |
          ./scripts/deploy-green.sh ${{ github.sha }}

      - name: 헬스체크
        run: |
          timeout 120 bash -c '
            until curl -sf https://green.example.com/health; do
              sleep 5
            done
          '

      - name: 스모크 테스트
        run: |
          pytest tests/smoke -q --base-url=https://green.example.com

      - name: 트래픽 전환
        run: |
          ./scripts/switch-traffic.sh green

      - name: 이전 환경 정리 (Blue)
        run: |
          sleep 300  # 5분 대기 (롤백 여유)
          ./scripts/cleanup-blue.sh
```

이 패턴의 핵심은 새 환경에서 헬스체크와 스모크 테스트를 통과한 후에만 트래픽을 전환하는 것입니다. 실패하면 Green을 제거하고 기존 Blue를 유지하면 됩니다.

### 카나리 배포 워크플로우

```yaml
jobs:
  canary:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6

      - name: 카나리 배포 (10% 트래픽)
        run: ./scripts/deploy-canary.sh ${{ github.sha }} --weight=10

      - name: 메트릭 관찰 (10분)
        run: |
          sleep 600
          ERROR_RATE=$(./scripts/check-error-rate.sh canary)
          echo "Error rate: ${ERROR_RATE}%"
          if (( $(echo "$ERROR_RATE > 1.0" | bc -l) )); then
            echo "::error::Canary error rate too high: ${ERROR_RATE}%"
            ./scripts/rollback-canary.sh
            exit 1
          fi

      - name: 전체 배포
        run: ./scripts/promote-canary.sh --weight=100
```

카나리 배포는 자동화의 마지막 단계입니다. 에러율 같은 메트릭을 기준으로 자동 롤백을 결정합니다.

---

## GitHub Environments 심화 설정

Environments는 단순한 시크릿 그룹이 아니라 배포 정책의 중심입니다.

### 보호 규칙 설정

```yaml
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh production
```

GitHub UI에서 environment에 설정할 수 있는 보호 규칙입니다.

| 규칙 | 효과 |
| --- | --- |
| Required reviewers | 지정된 사람이 승인해야 배포 진행 |
| Wait timer | 승인 후 N분 대기 (최종 취소 기회) |
| Branch restrictions | 특정 브랜치에서만 배포 허용 |
| Custom deployment rules | 외부 시스템 검증 연동 |

```yaml
# staging은 자동, production은 승인 필요
jobs:
  deploy-staging:
    environment: staging
    # 보호 규칙 없음 → 자동 배포
    ...

  deploy-production:
    needs: deploy-staging
    environment: production
    # Required reviewers 설정 → 승인 대기
    ...
```

이 구조에서 staging 배포는 자동으로 진행되고, production 배포는 staging 성공 후 reviewer가 승인해야만 시작됩니다.

---

## OIDC 기반 클라우드 인증

장기 액세스 키를 GitHub Secrets에 저장하는 방식은 키 회전, 노출 위험, 권한 과다라는 세 가지 문제를 안고 있습니다. OIDC(OpenID Connect)는 이를 근본적으로 해결합니다.

### AWS OIDC 연동

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
          aws-region: ap-northeast-2

      - run: aws ecs update-service --cluster prod --service app --force-new-deployment
```

OIDC의 동작 방식입니다.

1. GitHub Actions가 JWT 토큰을 생성합니다 (워크플로우, 저장소, 브랜치 정보 포함).
2. AWS IAM이 이 토큰을 검증하고 임시 자격 증명을 발급합니다.
3. 임시 자격 증명은 잡 실행 동안만 유효합니다.

장기 키와의 차이를 비교하겠습니다.

| 구분 | 장기 키 | OIDC |
| --- | --- | --- |
| 유효 기간 | 수동 회전까지 영구 | 잡 실행 중에만 유효 (15분-1시간) |
| 저장 위치 | GitHub Secrets | 없음 (실시간 발급) |
| 권한 범위 | 키에 부여된 모든 권한 | IAM Role의 조건부 정책으로 제한 |
| 노출 위험 | 로그/포크에서 유출 가능 | 토큰 재사용 불가 |

### GCP OIDC 연동

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/repo
    service_account: deploy@project.iam.gserviceaccount.com

- uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: app
    image: gcr.io/project/app:${{ github.sha }}
```

AWS와 GCP 모두 `permissions: id-token: write`가 필수입니다. 이 권한이 없으면 JWT 토큰 생성이 실패합니다.

---

## 롤백 자동화

배포 후 문제가 발견됐을 때 빠르게 이전 버전으로 돌아가는 워크플로우입니다.

```yaml
name: rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        required: true
      version:
        description: "롤백할 버전 태그 또는 SHA"
        required: true
        type: string
      reason:
        description: "롤백 사유"
        required: true
        type: string

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ inputs.version }}

      - name: 롤백 시작 알림
        run: |
          echo "::notice::Rolling back ${{ inputs.environment }} to ${{ inputs.version }}"
          echo "Reason: ${{ inputs.reason }}"

      - name: 배포
        run: ./scripts/deploy.sh ${{ inputs.environment }} ${{ inputs.version }}

      - name: 헬스체크
        run: |
          timeout 60 bash -c '
            until curl -sf ${{ vars.HEALTH_URL }}/health; do sleep 5; done
          '

      - name: 롤백 완료 알림
        run: |
          ./scripts/notify.sh "Rollback complete: ${{ inputs.environment }} → ${{ inputs.version }} (Reason: ${{ inputs.reason }})"
```

롤백 워크플로우에서 중요한 점입니다.

- **reason 필드를 필수로 둡니다.** 나중에 왜 롤백했는지 추적할 수 있어야 합니다.
- **environment 보호 규칙이 적용됩니다.** production 롤백도 승인이 필요할 수 있습니다.
- **헬스체크를 포함합니다.** 롤백 자체가 실패할 수 있으므로 검증이 필요합니다.

---

## 배포 알림과 감사 로그

배포 자동화가 성숙해지면 "누가 언제 무엇을 배포했는가"를 추적하는 것이 중요해집니다.

```yaml
- name: 배포 기록 남기기
  run: |
    gh api repos/${{ github.repository }}/deployments \
      -f ref=${{ github.sha }} \
      -f environment=${{ inputs.environment || 'staging' }} \
      -f description="Deployed by ${{ github.actor }}"

- name: Slack 알림
  if: always()
  uses: slackapi/slack-github-action@v2.0.0
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {
        "text": "Deploy ${{ job.status }}: ${{ inputs.environment }} @ ${{ github.sha }}\nBy: ${{ github.actor }}\nRun: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
```

GitHub Deployments API를 사용하면 저장소의 Environments 탭에서 배포 이력을 시각적으로 확인할 수 있습니다. Slack 알림은 팀이 배포 상태를 실시간으로 파악하는 데 도움을 줍니다.

---

## 배포 검증 자동화

배포 후 자동으로 검증을 수행하는 패턴입니다. 수동 확인에 의존하면 사고 발견이 늦어집니다.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - uses: actions/checkout@v6
      - id: deploy
        run: |
          URL=$(./scripts/deploy.sh staging)
          echo "url=${URL}" >> "$GITHUB_OUTPUT"

  post-deploy-check:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: 헬스체크
        run: |
          for i in {1..10}; do
            STATUS=$(curl -so /dev/null -w "%{http_code}" ${{ needs.deploy.outputs.url }}/health)
            if [ "$STATUS" = "200" ]; then
              echo "Health check passed"
              exit 0
            fi
            sleep 10
          done
          echo "::error::Health check failed after 100s"
          exit 1

      - name: 스모크 테스트
        run: pytest tests/smoke -q --base-url=${{ needs.deploy.outputs.url }}

      - name: 성능 기본 확인
        run: |
          RESPONSE_TIME=$(curl -so /dev/null -w "%{time_total}" ${{ needs.deploy.outputs.url }}/api/ping)
          echo "Response time: ${RESPONSE_TIME}s"
          if (( $(echo "$RESPONSE_TIME > 2.0" | bc -l) )); then
            echo "::warning::Response time exceeds 2s: ${RESPONSE_TIME}s"
          fi

  auto-rollback:
    needs: [deploy, post-deploy-check]
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: 자동 롤백
        run: ./scripts/rollback.sh staging
      - name: 알림
        run: ./scripts/notify.sh "Auto-rollback triggered for staging"
```

이 워크플로우의 구조입니다.

1. **deploy**: 배포 후 URL을 출력합니다.
2. **post-deploy-check**: 헬스체크, 스모크 테스트, 응답 시간을 검증합니다.
3. **auto-rollback**: 검증 실패 시 자동으로 이전 버전으로 롤백합니다.

`if: failure()`가 핵심입니다. 앞선 잡이 실패했을 때만 롤백 잡이 실행됩니다. 이 패턴으로 사람의 개입 없이도 기본적인 안전망을 구축할 수 있습니다.

---

## 배포 빈도와 워크플로우 성숙도

팀의 배포 성숙도에 따라 워크플로우 구조도 발전합니다.

| 성숙도 | 배포 빈도 | 워크플로우 특징 |
| --- | --- | --- |
| 초기 | 주 1회 수동 | workflow_dispatch, 단일 환경 |
| 중간 | 매일 자동 | staging 자동 + production 승인 |
| 성숙 | PR 머지마다 | 카나리 + 자동 롤백 + 메트릭 기반 판단 |

초기에는 `workflow_dispatch`로 수동 배포를 자동화하는 것만으로도 큰 진전입니다. 수동 배포에서 발생하는 "순서를 빼먹었다", "환경을 잘못 지정했다" 같은 실수를 구조적으로 방지합니다.

중간 단계에서는 staging 자동 배포와 production 승인 게이트를 분리합니다. 매일 staging에 배포하고 팀이 확인한 뒤 production으로 올리는 리듬을 만듭니다.

성숙 단계에서는 PR 머지마다 자동으로 카나리 배포가 시작되고, 메트릭 기반으로 프로모션 또는 롤백이 결정됩니다. 여기까지 오면 배포가 팀의 일상이 되어 특별한 이벤트가 아니게 됩니다.

## 정리

배포 자동화의 목표는 무조건 빠른 배포가 아니라 재현 가능한 배포입니다. staging 자동 배포, production 승인, OIDC, 롤백 워크플로우를 함께 설계하면 배포 속도와 운영 안정성을 동시에 가져갈 수 있습니다.

다음 글에서는 Secret 관리를 다룹니다. 배포가 자동화될수록 비밀값 노출 면적도 넓어지므로, 자격 증명과 권한을 어떤 원칙으로 다룰지 함께 정리해야 합니다.

---

## 처음 질문으로 돌아가기

- **staging 자동 배포와 production 승인 게이트는 어떻게 나눌까요?**
  - staging environment에는 보호 규칙을 설정하지 않아 main push 시 자동으로 배포됩니다. production environment에는 required reviewers를 설정해 승인 없이는 배포가 시작되지 않습니다. `needs: deploy-staging`으로 순서를 강제하면 "staging에서 검증된 코드만 production 후보가 된다"는 규칙이 워크플로우에 내장됩니다.
- **GitHub Environments는 왜 배포 정책의 중심이 될까요?**
  - Environments는 시크릿 격리, 승인 게이트, 브랜치 제한, 대기 타이머를 하나의 설정으로 묶습니다. environment별로 다른 AWS 계정이나 GCP 프로젝트의 시크릿을 두면 staging 시크릿으로 production에 배포하는 사고를 구조적으로 막을 수 있습니다. 배포 이력도 environment별로 추적됩니다.
- **OIDC는 장기 클라우드 키를 어떻게 대체할까요?**
  - OIDC는 워크플로우 실행 시점에 임시 자격 증명을 발급받는 방식입니다. GitHub Secrets에 장기 키를 저장할 필요가 없고, 토큰은 잡 실행 중에만 유효하며, IAM 정책으로 저장소/브랜치/환경별 접근을 제한할 수 있습니다. 키 회전이 필요 없고, 유출되어도 재사용이 불가능하므로 보안이 근본적으로 강화됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint와 Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): 빌드 아티팩트](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker 빌드](./07-docker-build.md)
- **배포 자동화 (현재 글)**
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Using environments for deployment](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Configuring OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Deploy, Environments, OIDC, CICD
