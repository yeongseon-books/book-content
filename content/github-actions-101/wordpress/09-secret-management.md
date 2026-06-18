---
title: "바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 관리"
series: github-actions-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - GitHubActions
  - Secret
  - Security
  - OIDC
  - CICD
---

# 바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 관리

이 글은 "바이브코딩을 위한 GitHub Actions 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 워크플로우에 `${{ secrets.TOKEN }}`을 쉽게 넣어줍니다. 하지만 secret이 한 번 로그나 코드에 새면 사실상 되돌리기 어렵습니다. secret은 한 번 실수하지 말자는 수준이 아니라, 실수를 하더라도 유출 범위를 줄이는 구조를 만드는 것이 중요합니다.

repository, environment, organization secret의 차이와 `GITHUB_TOKEN` 최소 권한, OIDC, 동적 값 마스킹을 중심으로 GitHub Actions에서 비밀값을 다루는 기준을 정리합니다.

> **핵심 인사이트:** Secret 관리는 편의 기능이 아니라 기본 보안 설계입니다. repository·environment·organization 수준의 범위를 의식적으로 나누고 `GITHUB_TOKEN`을 최소 권한으로 좁히는 일이, 결국 '유출됐을 때 영향이 어디까지 가는가'를 미리 정하는 일입니다.

## 이 글에서 다룰 문제

- repository, environment, organization secret은 어떻게 구분할까요?
- `GITHUB_TOKEN` 권한은 왜 가능한 한 좁혀야 할까요?
- OIDC는 장기 키 문제를 어떻게 줄여 줄까요?
- 동적으로 생성한 값은 어떻게 마스킹할까요?
- AI가 secret 관리를 단순화할 때 어떻게 보완할까요?

## secret 관리 핵심 패턴

```yaml
# GITHUB_TOKEN 최소 권한
permissions:
  contents: read
  pull-requests: write
  # everything else defaults to 'none'

# 환경 변수로 secret 주입 (명령행 인자 대신)
jobs:
  publish:
    environment: production
    steps:
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

# 런타임 생성 값 마스킹
- name: Mask runtime token
  run: |
    TOKEN=$(curl -s https://auth.example.com/token | jq -r .token)
    echo "::add-mask::$TOKEN"
    echo "GENERATED_TOKEN=$TOKEN" >> "$GITHUB_ENV"
```

## 변경 전후 비교

**Before: secret을 광범위하게 노출**
```yaml
permissions: write-all  # 모든 권한
steps:
  - run: echo "$SECRET_KEY"  # 로그에 노출
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

**After: 최소 권한 + 올바른 주입**
```yaml
permissions:
  contents: read
  packages: write
steps:
  - run: deploy.sh
    env:
      SECRET_KEY: ${{ secrets.SECRET_KEY }}  # 환경 변수로 주입, echo 없음
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `echo $SECRET` 출력 | 로그에 영구 기록 | 절대 secret 값을 echo하지 않음 |
| `pull_request_target`에서 PR 코드 실행 | 공격자 코드에 secret 노출 | PR 코드 checkout 금지 |
| `GITHUB_TOKEN` 광범위 쓰기 권한 | 오작동 시 영향 반경 큼 | `permissions:` 최소 권한으로 시작 |
| 런타임 생성 값 마스킹 누락 | 동적 토큰이 로그에 노출 | `::add-mask::` 적용 |
| secret 회전 일정 없음 | 오래된 키 지속 사용 | 분기별 회전 일정 문서화 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"GitHub Actions 워크플로우에서 secret을 안전하게 사용하는 방법을 보여줘.
GITHUB_TOKEN 최소 권한, environment secret,
runtime 값 마스킹, fork PR 보안까지 포함해야 해"

# secret 범위 선택 기준:
# - repository secret: 단일 저장소 전용 자격증명
# - environment secret: production 비밀번호 등 환경별 분리
# - organization secret: 공용 인프라 시크릿 (접근 저장소 제한)
```

## 운영 체크리스트

- [ ] secret 범위가 repository/environment/organization 중 의도적으로 선택됐다
- [ ] `permissions:`를 최소 권한으로 설정했다
- [ ] 클라우드 인증에 OIDC를 사용한다 (장기 키 없음)
- [ ] 동적 생성 값에 `::add-mask::` 적용했다
- [ ] fork PR에서 `pull_request_target` 안전하게 사용 중이다
- [ ] secret 회전 주기가 문서화됐다

## 처음 질문으로 돌아가기

- **repository, environment, organization secret 구분은?** 범위가 좁을수록 좋습니다. production 값은 environment secret으로, 공통 값은 organization secret으로 분리합니다.
- **`GITHUB_TOKEN` 권한을 좁혀야 하는 이유는?** 기본값이 넓으면 한 잡의 오작동이 전체 저장소에 영향을 미칠 수 있습니다.
- **OIDC는 어떻게 도움이 되나요?** 장기 액세스 키 없이 클라우드 신뢰를 맺어 키 유출 위험을 줄입니다.

## 정리

GitHub Actions에서 secret 관리는 저장, 노출, 권한, 회전을 함께 설계하는 일입니다. 바이브코딩에서 AI가 만들어 준 워크플로우에서 secret 관련 부분을 반드시 검토하고, `permissions:` 최소화, environment scope, `::add-mask::` 적용을 확인하세요. 다음 글에서는 지금까지 배운 모든 요소를 하나의 실전 CI/CD 파이프라인으로 묶습니다.

## 참고 자료

- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
- [Security hardening for GitHub Actions](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions)
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
- **바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 관리 (현재 글)**
- 바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인
<!-- toc:end -->

Tags: 바이브코딩, GitHubActions, Secret, Security, OIDC, CICD
