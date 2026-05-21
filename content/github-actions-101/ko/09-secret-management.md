---
series: github-actions-101
episode: 9
title: "GitHub Actions 101 (9/10): Secret 관리"
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
  - Secret
  - Security
  - OIDC
  - CICD
seo_description: GitHub Actions에서 secret, 권한, OIDC를 안전하게 다루는 기준을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (9/10): Secret 관리

자동화가 성숙해질수록 더 많은 비밀값이 파이프라인을 지나갑니다. 패키지 배포 토큰, 데이터베이스 비밀번호, 클라우드 접근 권한, 인증서 같은 값이 모두 여기에 포함됩니다. 문제는 secret이 한 번 로그나 코드에 새면 사실상 되돌리기 어렵다는 점입니다. 그래서 secret 관리는 편의 기능이 아니라 기본 보안 설계에 가깝습니다.

이 글은 GitHub Actions 101 시리즈의 9번째 글입니다. 여기서는 repository, environment, organization secret의 차이와 `GITHUB_TOKEN` 최소 권한, OIDC, 동적 값 마스킹을 중심으로 GitHub Actions에서 비밀값을 다루는 기준을 정리하겠습니다.

![GitHub Actions 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/09/09-01-secret.ko.png)
*GitHub Actions 101 9장 흐름 개요*

## 먼저 던지는 질문

- repository, environment, organization secret은 어떻게 구분할까요?
- `GITHUB_TOKEN` 권한은 왜 가능한 한 좁혀야 할까요?
- OIDC는 장기 키 문제를 어떻게 줄여 줄까요?

## 왜 중요한가

비밀값 유출은 복구 비용이 큽니다. 테스트 실패는 다시 고치면 되지만, 공개 로그에 찍힌 토큰은 이미 인터넷에 남습니다. 그래서 secret 문제는 “한 번 실수하지 말자” 수준이 아니라, 실수를 하더라도 유출 범위를 줄이는 구조를 만드는 것이 중요합니다.

또한 secret은 보안팀만의 관심사가 아닙니다. CI를 설계하는 개발자가 어떤 권한을 주고 어떤 환경에 노출할지 결정하기 때문에, 파이프라인 설계 자체가 보안 태세를 크게 좌우합니다. 저는 GitHub Actions에서 secret을 다루는 태도가 팀의 운영 성숙도를 잘 보여 준다고 생각합니다.

## 한눈에 보는 secret 흐름

이 그림은 secret이 한 군데에만 존재하는 값이 아니라는 점을 보여 줍니다. 어디서 저장하고, 어느 환경에서만 열어 주고, 런타임에 어떻게 가리는지가 모두 별도 결정입니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| Repository secret | 저장소 하나에만 적용되는 secret | 단일 저장소 전용 자격 증명에 적합합니다 |
| Environment secret | 특정 환경에만 열리는 secret | production 비밀번호처럼 범위를 좁히기 좋습니다 |
| Organization secret | 여러 저장소에 공유하는 secret | 중앙 관리에 유리하지만 범위를 조심해야 합니다 |
| `GITHUB_TOKEN` | 실행마다 자동 발급되는 단기 토큰 | 최소 권한 원칙으로 다뤄야 합니다 |
| OIDC | 키 없이 클라우드 신뢰를 맺는 방식 | 장기 액세스 키를 줄이는 데 핵심입니다 |

## 자동화 전과 후를 비교해 보겠습니다

secret 관리가 약한 팀은 `.env` 파일을 커밋하거나, 메신저로 액세스 키를 전달하거나, 퇴사한 사람이 알던 키를 몇 년째 그대로 쓰기도 합니다. 이 구조는 평소에는 조용하지만 사고가 났을 때 피해가 큽니다.

반대로 secret을 GitHub UI에서 관리하고, production 값은 environment scope로 좁히고, 클라우드 인증은 OIDC로 바꾸면 공격 표면이 훨씬 줄어듭니다. 완벽한 보안은 없지만, 최소한 쉽게 새는 구조는 피할 수 있습니다.

## secret 관리를 5단계로 정리해 보겠습니다

### 1단계 — secret을 올바른 범위에 등록하기

```bash
# Use the gh CLI instead of clicking
gh secret set NPM_TOKEN --body "npm_xxx"
gh secret set --env production DB_PASSWORD --body "***"
```

어디에 secret을 등록할지는 기술 문제가 아니라 범위 문제입니다. production에서만 필요한 값이라면 repository 전체에 열 이유가 없습니다.

### 2단계 — 워크플로우에서 환경 변수로 주입하기

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

secret은 환경 변수로 주입하는 편이 일반적으로 더 안전합니다. 명령행 인자로 넘기면 프로세스 목록이나 로그 노출 위험이 커질 수 있습니다.

### 3단계 — `GITHUB_TOKEN` 권한을 최소화하기

```yaml
permissions:
  contents: read
  pull-requests: write
  # everything else defaults to 'none'
```

기본 권한을 넓게 주는 습관은 위험합니다. 어떤 액션 하나가 오작동하거나 악성 동작을 해도 영향 반경이 커지기 때문입니다.

### 4단계 — 런타임 생성 값을 마스킹하기

```yaml
- name: Mask runtime token
  run: |
    TOKEN=$(curl -s https://auth.example.com/token | jq -r .token)
    echo "::add-mask::$TOKEN"
    echo "GENERATED_TOKEN=$TOKEN" >> "$GITHUB_ENV"
```

GitHub에 저장된 secret만 secret은 아닙니다. 실행 중 새로 발급받은 토큰도 동일하게 보호해야 합니다. `::add-mask::`는 이런 값에 꼭 필요합니다.

### 5단계 — 회전 정책을 운영에 넣기

```text
Settings > Secrets > Dependabot
- dependency update PRs can also access secrets
- put rotation on the calendar quarterly (gh secret set to refresh)
```

회전은 언젠가 해야 하는 일이 아니라, 애초에 정기 운영 절차여야 합니다. 캘린더에만 적는 것보다 갱신 방식까지 함께 문서화해 두는 편이 좋습니다.

## 이 코드에서 먼저 봐야 할 점

- secret은 명령행 인자보다 환경 변수로 넣는 편이 안전합니다.
- `permissions:`는 최소 권한 기준에서 시작해야 합니다.
- `::add-mask::`는 런타임 생성 값에도 적용됩니다.

즉, secret 관리는 “값을 숨긴다”보다 “값이 어디까지 보일 수 있는가를 통제한다”에 더 가깝습니다.

## 자주 하는 실수 다섯 가지

1. 디버깅하려고 `echo $SECRET`를 그대로 출력합니다.
2. `pull_request_target`로 외부 PR에 secret 접근을 열어 둡니다.
3. `GITHUB_TOKEN`을 광범위한 쓰기 권한으로 둡니다.
4. fork PR에도 secret을 노출할 수 있는 구조를 만듭니다.
5. 회전 일정을 만들지 않아 오래된 키를 계속 씁니다.

특히 두 번째와 네 번째는 “편해서” 선택했다가 크게 후회하기 쉬운 패턴입니다. 외부 코드가 실행될 수 있는 경로에는 비밀값이 닿지 않는다고 생각하는 편이 안전합니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 secret의 단일 출처를 Vault, Doppler, 1Password 같은 외부 시스템으로 두고, GitHub Actions는 그 값을 오래 저장하기보다 짧게 빌려 오는 방향으로 갑니다. 이때 OIDC가 핵심 역할을 합니다.

또한 권한은 넓게 주고 나중에 줄이는 것이 아니라, 가능한 한 좁게 시작하고 꼭 필요한 범위만 추가하는 편이 맞습니다. 보안에서 넓게 시작하는 기본값은 거의 항상 비용이 큽니다.

## 체크리스트

- [ ] secret 범위가 repository, environment, organization 중 의도적으로 선택됐다.
- [ ] `permissions:`를 최소 권한으로 설정했다.
- [ ] 클라우드 인증에 OIDC를 사용한다.
- [ ] 회전 일정과 갱신 절차가 있다.

## 연습 문제

1. production 환경에 `DB_PASSWORD` secret을 추가하고 워크플로우에서 안전하게 써 보세요.
2. 기존 워크플로우의 `permissions:`를 최소 권한 기준으로 줄여 보세요.
3. 런타임에 발급한 토큰을 `::add-mask::`로 보호하는 단계를 추가해 보세요.

## Secret 범위를 더 자세히 이해하겠습니다

GitHub Actions의 secret은 세 가지 범위로 나뉩니다. 각 범위의 특성과 적절한 사용 시점을 정리하겠습니다.

### 저장소 시크릿(Repository Secret)

```text
Settings > Secrets and variables > Actions > Repository secrets
```

특정 저장소에서만 접근 가능합니다. 대부분의 시크릿은 여기에 둡니다.

### 환경 시크릿(Environment Secret)

```text
Settings > Environments > [environment name] > Secrets
```

특정 environment가 설정된 잡에서만 접근 가능합니다. staging과 production의 데이터베이스 URL이 다를 때 가장 유용합니다.

```yaml
jobs:
  deploy-staging:
    environment: staging
    # DATABASE_URL은 staging environment의 값
    steps:
      - run: echo "${{ secrets.DATABASE_URL }}"

  deploy-production:
    environment: production
    # DATABASE_URL은 production environment의 값
    steps:
      - run: echo "${{ secrets.DATABASE_URL }}"
```

같은 이름(`DATABASE_URL`)이지만 environment에 따라 다른 값이 주입됩니다. 이 구조로 "staging 시크릿으로 production에 접속"하는 사고를 구조적으로 방지합니다.

### 조직 시크릿(Organization Secret)

```text
Organization > Settings > Secrets and variables > Actions
```

조직 내 여러 저장소에서 공유할 수 있습니다. 접근 가능한 저장소를 제한할 수 있으므로, 공통 인프라 시크릿(Slack webhook, 공용 레지스트리 인증 등)에 적합합니다.

### 범위 우선순위

같은 이름의 시크릿이 여러 범위에 있을 때 우선순위입니다.

1. Environment secret (가장 높음)
2. Repository secret
3. Organization secret (가장 낮음)

이 우선순위를 활용하면 조직 기본값을 Organization에 두고, 특수한 저장소에서만 Repository secret으로 덮어쓰는 패턴이 가능합니다.

---

## GITHUB_TOKEN 권한 관리

`GITHUB_TOKEN`은 워크플로우 실행마다 자동으로 생성되는 토큰입니다. 별도 설정 없이 사용할 수 있지만, 기본 권한이 넓을 수 있으므로 최소 권한 원칙을 적용해야 합니다.

### 저장소 기본 권한 설정

```text
Settings > Actions > General > Workflow permissions
→ "Read repository contents and packages permissions" 선택
```

기본 권한을 `read`로 설정하면 모든 워크플로우에서 명시적으로 권한을 선언해야 합니다. 처음엔 번거롭지만 "이 워크플로우가 어떤 권한을 가지는가"가 YAML에 명확히 드러납니다.

### 잡 수준 권한 선언

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # checkout만 필요
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write     # GHCR push
      id-token: write     # OIDC
      deployments: write  # deployment status
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh
```

각 잡에 필요한 최소 권한만 부여하면, 린트 잡이 탈취되어도 패키지 push나 배포는 불가능합니다.

### 사용 가능한 권한 목록

| 권한 | 용도 |
| --- | --- |
| contents | 저장소 코드 읽기/쓰기 |
| packages | 패키지 레지스트리 접근 |
| pull-requests | PR 코멘트, 라벨 |
| issues | 이슈 관리 |
| deployments | 배포 상태 업데이트 |
| id-token | OIDC 토큰 발급 |
| checks | 체크 결과 작성 |
| actions | 워크플로우 관리 |
| security-events | CodeQL 결과 업로드 |

---

## Secret 노출 방지 기법

비밀값이 로그에 노출되는 경로와 방지법을 정리하겠습니다.

### 자동 마스킹의 한계

GitHub Actions는 `secrets.*`로 참조한 값을 로그에서 자동으로 `***`로 마스킹합니다. 하지만 다음 경우에는 마스킹이 동작하지 않습니다.

1. **시크릿을 가공한 경우**: base64 인코딩이나 부분 문자열은 마스킹되지 않습니다.
2. **구조화된 출력**: JSON 안에 시크릿이 포함되면 전체 JSON이 마스킹되지 않을 수 있습니다.
3. **다른 스텝에서 환경변수로 재참조**: 환경변수 확장이 먼저 일어나는 경우.

### 수동 마스킹

```yaml
- name: 임시 토큰 생성 및 마스킹
  run: |
    TOKEN=$(./scripts/get-token.sh)
    echo "::add-mask::${TOKEN}"
    echo "token=${TOKEN}" >> "$GITHUB_OUTPUT"
```

`::add-mask::`는 이후 로그에서 해당 값을 마스킹합니다. 동적으로 생성된 값(임시 토큰, API 응답에서 추출한 키 등)에 반드시 적용해야 합니다.

### 시크릿 스캔

```yaml
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: gitleaks 스캔
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

gitleaks는 커밋 이력에서 실수로 커밋된 시크릿을 탐지합니다. PR 검증에 포함하면 시크릿이 머지되기 전에 차단할 수 있습니다.

---

## Secret 회전 자동화

시크릿은 정기적으로 교체해야 하지만, 수동 회전은 놓치기 쉽습니다. 자동화할 수 있는 부분을 정리하겠습니다.

```yaml
name: rotate-secrets

on:
  schedule:
    - cron: "0 9 1 * *"  # 매월 1일
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v6

      - name: 새 키 생성
        id: new-key
        run: |
          NEW_KEY=$(openssl rand -hex 32)
          echo "::add-mask::${NEW_KEY}"
          echo "key=${NEW_KEY}" >> "$GITHUB_OUTPUT"

      - name: 서비스에 새 키 등록
        run: ./scripts/update-service-key.sh "${{ steps.new-key.outputs.key }}"

      - name: GitHub Secret 업데이트
        run: |
          gh secret set API_KEY --body "${{ steps.new-key.outputs.key }}"

      - name: 이전 키 폐기 (grace period 후)
        run: |
          sleep 300  # 5분간 양쪽 키 유효
          ./scripts/revoke-old-key.sh
```

이 패턴의 핵심은 grace period입니다. 새 키를 등록한 직후 이전 키를 폐기하면, 아직 이전 키를 사용하는 요청이 실패할 수 있습니다. 적절한 대기 시간을 두고 양쪽 키가 모두 유효한 기간을 만들어야 합니다.

---

## Fork PR에서의 Secret 보안

오픈소스 프로젝트에서 fork PR을 받을 때 시크릿 처리는 특별한 주의가 필요합니다.

| 이벤트 | Fork PR에서 시크릿 접근 | 안전한 사용법 |
| --- | --- | --- |
| `pull_request` | 불가 | 안전 - 시크릿 필요 없는 검증용 |
| `pull_request_target` | 가능 | 위험 - PR 코드 실행 금지 |
| `workflow_run` | 가능 | 안전 - 신뢰된 코드만 실행 |

```yaml
# 안전한 패턴: pull_request_target에서 라벨링만
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      # PR 코드를 checkout하지 않음!
      - uses: actions/labeler@v5
```

```yaml
# 위험한 패턴: PR 코드를 checkout하고 실행
on:
  pull_request_target:

jobs:
  dangerous:
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.event.pull_request.head.ref }}  # 공격자의 코드!
      - run: make test  # Makefile에 시크릿 탈취 코드가 있을 수 있음
```

두 번째 패턴은 절대 사용하면 안 됩니다. 공격자가 PR의 Makefile이나 테스트 코드에 시크릿을 외부로 전송하는 코드를 넣을 수 있습니다.

---

## 실무 시크릿 관리 체크리스트

| 항목 | 확인 |
| --- | --- |
| 기본 워크플로우 권한이 `read`로 설정됨 | |
| 모든 잡에 `permissions`가 명시적으로 선언됨 | |
| Environment secret으로 환경별 분리됨 | |
| OIDC로 클라우드 인증 (장기 키 없음) | |
| fork PR에서 `pull_request_target` 미사용 또는 안전하게 사용 | |
| gitleaks 또는 유사 도구로 시크릿 스캔 활성화 | |
| 시크릿 회전 주기가 문서화됨 | |
| 불필요한 시크릿이 제거됨 | |
| 동적 생성 값에 `::add-mask::` 적용 | |
| `set -x` 사용 구간에 시크릿이 노출되지 않음 | |

---

## Variables vs Secrets 구분

GitHub Actions에는 Secrets 외에 Variables도 있습니다. 민감하지 않은 설정값은 Variables에 두는 것이 적절합니다.

| 구분 | Secrets | Variables |
| --- | --- | --- |
| 용도 | 비밀값 (토큰, 비밀번호) | 설정값 (URL, 플래그) |
| 로그 마스킹 | 자동 | 없음 |
| 접근 방법 | `${{ secrets.NAME }}` | `${{ vars.NAME }}` |
| 범위 | repo/env/org | repo/env/org |
| 수정 후 확인 | 값을 다시 볼 수 없음 | 언제든 확인 가능 |

```yaml
jobs:
  deploy:
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: |
          # Variables: 민감하지 않은 설정
          echo "Deploying to: ${{ vars.DEPLOY_URL }}"
          echo "Region: ${{ vars.AWS_REGION }}"
          
          # Secrets: 민감한 인증 정보
          ./scripts/deploy.sh \
            --url "${{ vars.DEPLOY_URL }}" \
            --token "${{ secrets.DEPLOY_TOKEN }}"
```

Variables에 넣어야 할 값을 Secrets에 넣으면 디버깅이 어려워집니다. 마스킹 때문에 로그에서 URL이나 설정값을 확인할 수 없기 때문입니다. 반대로 비밀값을 Variables에 넣으면 로그에 노출됩니다.

---

## 외부 시크릿 매니저 연동

대규모 조직에서는 GitHub Secrets만으로는 부족한 경우가 있습니다. HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager 같은 외부 도구와 연동하는 패턴입니다.

### AWS Secrets Manager 연동

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
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: ap-northeast-2

      - name: 시크릿 가져오기
        id: secrets
        run: |
          DB_PASSWORD=$(aws secretsmanager get-secret-value \
            --secret-id prod/db-password \
            --query SecretString --output text)
          echo "::add-mask::${DB_PASSWORD}"
          echo "db_password=${DB_PASSWORD}" >> "$GITHUB_OUTPUT"

      - name: 배포
        env:
          DB_PASSWORD: ${{ steps.secrets.outputs.db_password }}
        run: ./scripts/deploy.sh
```

외부 시크릿 매니저의 장점입니다.

- **중앙 집중 관리**: 모든 시크릿을 한 곳에서 관리하고 감사합니다.
- **세밀한 접근 제어**: IAM 정책으로 누가 어떤 시크릿에 접근하는지 제어합니다.
- **자동 회전**: AWS Secrets Manager는 Lambda와 연동해 자동 회전을 설정할 수 있습니다.
- **버전 관리**: 시크릿 변경 이력을 추적할 수 있습니다.

### HashiCorp Vault 연동

```yaml
- name: Vault에서 시크릿 가져오기
  uses: hashicorp/vault-action@v3
  with:
    url: https://vault.example.com
    method: jwt
    role: github-actions
    secrets: |
      secret/data/prod/db password | DB_PASSWORD ;
      secret/data/prod/api key | API_KEY
```

Vault의 JWT 인증은 GitHub OIDC와 연동되므로 장기 토큰 없이 접근할 수 있습니다.

---

## 시크릿 감사와 모니터링

시크릿이 제대로 관리되고 있는지 주기적으로 확인하는 워크플로우입니다.

```yaml
name: secret-audit

on:
  schedule:
    - cron: "0 9 * * 1"  # 매주 월요일

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: 사용되지 않는 시크릿 확인
        run: |
          echo "## Secret Usage Audit" > audit.md
          echo "" >> audit.md
          
          # 워크플로우에서 참조되는 시크릿 목록 추출
          USED_SECRETS=$(grep -roh 'secrets\.\w\+' .github/workflows/ | sort -u | sed 's/secrets\.//')
          
          echo "### 워크플로우에서 참조되는 시크릿:" >> audit.md
          echo "$USED_SECRETS" >> audit.md
          echo "" >> audit.md
          
          # 등록된 시크릿과 비교 (gh cli)
          echo "### 저장소에 등록된 시크릿:" >> audit.md
          gh secret list >> audit.md

      - uses: actions/upload-artifact@v7
        with:
          name: secret-audit
          path: audit.md
          retention-days: 30
```

이 워크플로우는 "등록은 돼 있지만 사용하지 않는 시크릿"을 찾는 출발점입니다. 사용하지 않는 시크릿은 공격 표면만 넓히므로 즉시 제거해야 합니다.

---

## 실수로 커밋된 시크릿 대응 절차

시크릿이 실수로 커밋되었을 때의 대응 절차입니다. git history에서 완전히 제거하는 것보다 더 중요한 것은 즉시 해당 시크릿을 폐기하는 것입니다.

1. **즉시 시크릿 폐기/회전**: 노출된 키, 토큰, 비밀번호를 즉시 무효화합니다.
2. **GitHub 알림 확인**: GitHub Secret Scanning이 활성화되어 있다면 이미 알림이 와 있을 수 있습니다.
3. **영향 범위 확인**: 해당 시크릿으로 접근 가능한 시스템과 데이터를 파악합니다.
4. **git history 정리** (선택): `git filter-repo`나 BFG로 이력에서 제거할 수 있지만, 이미 clone된 복사본에는 남아 있으므로 1번이 더 중요합니다.
5. **재발 방지**: pre-commit 훅에 gitleaks를 추가하고, CI에서도 스캔을 활성화합니다.

```bash
# git filter-repo로 파일 제거 (주의: force push 필요)
pip install git-filter-repo
git filter-repo --path credentials.json --invert-paths
```

핵심은 "history에서 지웠으니 안전하다"가 아니라 "노출된 시크릿은 이미 탈취되었다고 가정하고 폐기한다"입니다.

## 정리

GitHub Actions에서 secret 관리는 저장, 노출, 권한, 회전을 함께 설계하는 일입니다. secret을 코드 밖에 두고, 환경별로 범위를 좁히고, `GITHUB_TOKEN`과 클라우드 인증 권한을 최소화하면 대부분의 사고 가능성을 크게 줄일 수 있습니다.

다음 글에서는 지금까지 배운 모든 요소를 하나의 실전 CI/CD 파이프라인으로 묶어 보겠습니다. 트리거, 테스트, 품질 게이트, 아티팩트, Docker, 배포, secret이 실제로 어떻게 연결되는지 보는 마지막 단계입니다.

---

## 처음 질문으로 돌아가기

- **repository, environment, organization secret은 어떻게 구분할까요?**
  - Repository secret은 해당 저장소 전체에서 접근 가능하고, environment secret은 특정 environment가 설정된 잡에서만 접근 가능하며, organization secret은 조직 내 여러 저장소에서 공유됩니다. 우선순위는 environment > repository > organization 순입니다. staging과 production의 DB 인증이 다르면 environment secret으로 분리하고, 조직 공통 Slack webhook은 organization secret으로 두는 것이 일반적입니다.
- **`GITHUB_TOKEN` 권한은 왜 가능한 한 좁혀야 할까요?**
  - 기본 권한이 넓으면 린트 잡이 탈취되었을 때 패키지 push, PR 승인, 코드 수정까지 가능해집니다. 저장소 기본 권한을 `read`로 설정하고 잡마다 필요한 권한만 명시하면, 한 잡의 보안 사고가 다른 잡의 권한으로 확대되지 않습니다. YAML에 권한이 명시되므로 코드 리뷰에서도 "이 잡에 이 권한이 왜 필요한가"를 자연스럽게 검토하게 됩니다.
- **OIDC는 장기 키 문제를 어떻게 줄여 줄까요?**
  - OIDC는 워크플로우 실행 시점에 임시 토큰을 발급받으므로 GitHub Secrets에 장기 키를 저장할 필요가 없습니다. 토큰은 15분-1시간만 유효하고, 재사용이 불가능합니다. IAM 정책으로 특정 저장소/브랜치/환경에서만 토큰이 유효하도록 제한할 수 있어, "키가 유출되면 무엇이 위험한가"라는 질문 자체가 사라집니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint와 Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): 빌드 아티팩트](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker 빌드](./07-docker-build.md)
- [GitHub Actions 101 (8/10): 배포 자동화](./08-deploy-automation.md)
- **Secret 관리 (현재 글)**
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
- [Automatic token authentication](https://docs.github.com/actions/security-guides/automatic-token-authentication)
- [Security hardening for GitHub Actions](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions)
- [Workflow commands - add-mask](https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-a-log)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Secret, Security, OIDC, CICD
