---
title: "바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화"
series: github-actions-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Deploy
- Environments
- CICD
seo_description: "바이브코딩 프로젝트에서 staging 자동 배포와 production 승인 게이트를 갖춘 안전한 배포 자동화를 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 8번째 글입니다.

AI로 빠르게 만든 서비스를 배포하는 과정을 생각해 봅니다. 테스트도 통과했고, 이미지도 올라갔습니다. 이제 실제 서버에 반영해야 합니다. 이 순간 "배포는 어떻게 하나요?"라는 질문이 나옵니다. 담당자가 터미널을 열고 직접 명령을 입력하거나, 메신저로 배포 요청을 보내거나, 아직 배포 프로세스 자체가 없는 경우도 있습니다. 바이브코딩으로 코드를 빨리 만들어도 배포가 수동이면 그 속도가 의미 없어집니다.

배포 자동화의 핵심은 속도가 아니라 재현성입니다. 누가 언제 어떤 버전을 배포했는지 로그로 남고, staging은 자동으로 반영되고, production은 팀원의 승인 후에만 진행되는 구조를 만들어야 합니다. GitHub Environments를 쓰면 배포 정책을 코드로 정의할 수 있습니다. 바이브코딩으로 만든 서비스도 이런 구조를 갖춰야 팀이 안심하고 배포할 수 있습니다.

> 배포 자동화는 빠른 배포를 위한 것이 아닙니다. 재현 가능하고 추적 가능한 배포를 만들기 위한 것입니다. 그래야 새벽 장애에서도 빠르게 대응할 수 있습니다.

---

## 이 글에서 다룰 문제
- staging 자동 배포와 production 수동 승인은 왜 분리해야 할까요?
- GitHub Environments는 단순한 이름표가 아니라 어떤 역할을 할까요?
- OIDC를 쓰면 AWS 키를 왜 저장하지 않아도 되나요?
- 롤백을 문서 대신 워크플로우로 만들어야 하는 이유는 무엇일까요?
- 바이브코딩 팀에서 배포 자동화를 처음 도입하는 현실적인 순서는?

---

## 수동 배포의 반복 문제

바이브코딩 팀에서 수동 배포를 하면 이런 패턴이 반복됩니다.

```text
개발자: "방금 main에 머지했는데 서버에 반영됐나요?"
운영자: (터미널 열고 kubectl apply 실행)
개발자: "어떤 버전 배포됐어요?"
운영자: "SHA가... 잠깐만요"
```

어떤 버전이 어느 환경에 배포됐는지 추적하기 어렵고, 사람의 기억에 의존합니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| Environment | GitHub 배포 환경 단위 | staging/production 정책을 코드로 분리합니다 |
| Required reviewers | 환경별 승인자 | production 배포에 사람의 확인을 강제합니다 |
| OIDC | 단기 토큰 기반 클라우드 신뢰 | 장기 AWS/GCP 키를 저장하지 않아도 됩니다 |
| 롤백 워크플로우 | 이전 버전으로 되돌리는 자동화 | 새벽 장애 대응을 빠르게 만듭니다 |
| `wait timer` | 승인 후 N분 대기 | 마지막 취소 기회를 만들어 줍니다 |

---

## Before / After

**배포 절차가 문서에만 있을 때**

```text
Confluence 페이지: "배포 방법"
1. main 브랜치로 체크아웃
2. docker build -t myapp .
3. docker push ...
4. kubectl apply -f k8s/production/
(이 문서를 마지막으로 업데이트한 게 6개월 전)
```

**GitHub Actions 배포 자동화**

```yaml
jobs:
  deploy-staging:
    needs: build
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh staging ${{ github.sha }}

  deploy-production:
    needs: deploy-staging
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh production ${{ github.sha }}
```

staging은 자동으로 반영되고, production은 GitHub UI에서 승인자가 클릭해야만 실행됩니다. 배포 이력은 Actions 탭에 SHA와 함께 남습니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| production에 required reviewers 없음 | 테스트 없이 production 배포 가능 | Environments 설정에서 승인자를 추가합니다 |
| staging과 production이 같은 정책 | staging이 느려지거나 production이 가벼워짐 | 역할을 명확히 분리합니다 |
| 롤백이 문서에만 있음 | 새벽 장애 시 문서를 찾아야 함 | `workflow_dispatch` 롤백 워크플로우를 만듭니다 |
| 장기 AWS 키를 secrets에 저장 | 키 노출 시 영구적인 접근 권한 부여됨 | OIDC로 임시 자격 증명을 사용합니다 |
| 배포 결과를 팀에 알리지 않음 | 누가 어디에 배포됐는지 팀이 모름 | Slack 알림 또는 GitHub Deployment API를 씁니다 |

## AI 팁: 배포 자동화 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions로 staging 자동 배포와 production 승인 배포를 만들어줘.
조건:
- staging: main push 시 자동 배포, environment: staging
- production: staging 완료 후 승인 필요, environment: production
- 배포 스크립트는 ./scripts/deploy.sh 환경 SHA 형식으로 호출
- OIDC로 AWS 자격 증명 (aws-actions/configure-aws-credentials)
- 롤백 workflow_dispatch 추가 (version 입력, reason 필수)"
```

받은 후에는 OIDC 사용 시 `permissions: id-token: write`가 포함됐는지 확인하세요.

## 운영 체크리스트
- [ ] GitHub Environments가 staging과 production으로 분리됐는가?
- [ ] production에 required reviewers가 설정됐는가?
- [ ] 롤백 워크플로우가 존재하는가?
- [ ] 장기 클라우드 키 대신 OIDC를 사용하는가?
- [ ] 배포 이력이 추적 가능한가?

## 처음 질문으로 돌아가기

- **staging과 production을 왜 분리해야 하나?**
  staging은 빠른 피드백을 위한 자동 반영이 맞고, production은 사람의 의식적인 승인이 필요합니다. 같은 정책으로 다루면 production 배포가 너무 가벼워지거나, staging이 불필요하게 느려집니다.

- **OIDC가 장기 키보다 나은 이유는?**
  장기 AWS 키는 한 번 노출되면 수동으로 폐기하기 전까지 계속 유효합니다. OIDC는 잡 실행 중에만 유효한 임시 자격 증명을 발급합니다. 키가 저장소에 저장될 필요조차 없습니다.

- **롤백을 워크플로우로 만드는 이유는?**
  새벽 2시에 서비스 장애가 나면 Confluence를 찾을 여유가 없습니다. `workflow_dispatch` 버튼 하나로 버전을 입력하고 롤백이 실행되면 대응 시간이 크게 줄어듭니다.

## 정리

배포 자동화는 코드를 빨리 배포하기 위한 것이 아니라, 배포를 재현 가능하고 추적 가능하게 만들기 위한 것입니다. GitHub Environments로 staging과 production 정책을 분리하고, OIDC로 보안을 강화하고, 롤백 워크플로우를 준비하면 바이브코딩으로 빠르게 만든 서비스도 안전하게 운영할 수 있습니다. 다음 글에서는 파이프라인에서 가장 중요한 비밀값을 안전하게 관리하는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [Using environments for deployment](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Configuring OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
### 관련 시리즈
- [DevOps 101](../../devops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- **바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Deploy, Environments, CICD
