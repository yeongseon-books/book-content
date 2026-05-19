---
series: github-actions-101
episode: 9
title: Secret 관리
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

# Secret 관리

자동화가 성숙해질수록 더 많은 비밀값이 파이프라인을 지나갑니다. 패키지 배포 토큰, 데이터베이스 비밀번호, 클라우드 접근 권한, 인증서 같은 값이 모두 여기에 포함됩니다. 문제는 secret이 한 번 로그나 코드에 새면 사실상 되돌리기 어렵다는 점입니다. 그래서 secret 관리는 편의 기능이 아니라 기본 보안 설계에 가깝습니다.

이 글은 GitHub Actions 101 시리즈의 9번째 글입니다. 여기서는 repository, environment, organization secret의 차이와 `GITHUB_TOKEN` 최소 권한, OIDC, 동적 값 마스킹을 중심으로 GitHub Actions에서 비밀값을 다루는 기준을 정리하겠습니다.

## 이 글에서 다룰 문제

> Secret은 코드가 아니라 런타임 자원입니다. 저장 위치, 노출 범위, 회전 주기를 분리해서 생각해야 안전해집니다. 무심코 한 번 출력하는 순간 모든 설계가 무너질 수 있습니다.

- repository, environment, organization secret은 어떻게 구분할까요?
- `GITHUB_TOKEN` 권한은 왜 가능한 한 좁혀야 할까요?
- OIDC는 장기 키 문제를 어떻게 줄여 줄까요?
- 런타임에 생성된 값은 어떻게 마스킹해야 할까요?
- fork PR과 `pull_request_target`은 왜 특히 조심해야 할까요?

## 왜 중요한가

비밀값 유출은 복구 비용이 큽니다. 테스트 실패는 다시 고치면 되지만, 공개 로그에 찍힌 토큰은 이미 인터넷에 남습니다. 그래서 secret 문제는 “한 번 실수하지 말자” 수준이 아니라, 실수를 하더라도 유출 범위를 줄이는 구조를 만드는 것이 중요합니다.

또한 secret은 보안팀만의 관심사가 아닙니다. CI를 설계하는 개발자가 어떤 권한을 주고 어떤 환경에 노출할지 결정하기 때문에, 파이프라인 설계 자체가 보안 태세를 크게 좌우합니다. 저는 GitHub Actions에서 secret을 다루는 태도가 팀의 운영 성숙도를 잘 보여 준다고 생각합니다.

## 한눈에 보는 secret 흐름

![조직, 저장소, 환경 secret이 잡 런타임으로 전달되고 add-mask로 보호되는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/09/09-01-secret.ko.png)

*조직, 저장소, 환경 secret이 잡 런타임으로 전달되고 add-mask로 보호되는 흐름*

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

## 정리

GitHub Actions에서 secret 관리는 저장, 노출, 권한, 회전을 함께 설계하는 일입니다. secret을 코드 밖에 두고, 환경별로 범위를 좁히고, `GITHUB_TOKEN`과 클라우드 인증 권한을 최소화하면 대부분의 사고 가능성을 크게 줄일 수 있습니다.

다음 글에서는 지금까지 배운 모든 요소를 하나의 실전 CI/CD 파이프라인으로 묶어 보겠습니다. 트리거, 테스트, 품질 게이트, 아티팩트, Docker, 배포, secret이 실제로 어떻게 연결되는지 보는 마지막 단계입니다.

<!-- toc:begin -->
- [GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [Workflow와 Job](./02-workflow-and-job.md)
- [Trigger 이해하기](./03-triggers.md)
- [Python 테스트 자동화](./04-python-test-automation.md)
- [Lint와 Type Check](./05-lint-and-typecheck.md)
- [빌드 아티팩트](./06-build-artifact.md)
- [Docker 빌드](./07-docker-build.md)
- [배포 자동화](./08-deploy-automation.md)
- **Secret 관리 (현재 글)**
- 실전 CI/CD 파이프라인 (예정)
<!-- toc:end -->

## 참고 자료

- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
- [Automatic token authentication](https://docs.github.com/actions/security-guides/automatic-token-authentication)
- [Security hardening for GitHub Actions](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions)
- [Workflow commands - add-mask](https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-a-log)

Tags: GitHubActions, Secret, Security, OIDC, CICD
