---
title: "바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략"
series: devops-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 기능을 사용자에게 안전하게 전달하려면 CD와 배포 전략을 알아야 합니다. Rolling, Blue-Green, Canary의 차이와 실무 적용법을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 3번째 글입니다.

AI 코딩 도구로 기능을 빠르게 만들다 보면 배포가 발목을 잡는 경우가 많습니다. 코드는 완성됐는데 서버에 올리는 과정에서 서비스가 잠깐 멈추거나, 배포했더니 사용자 일부에게 에러가 납니다. 또는 배포를 되돌리려는데 방법을 몰라 허둥댑니다.

CD(Continuous Delivery/Deployment)는 검증된 코드를 자동으로, 안전하게 사용자에게 전달하는 흐름입니다. 중요한 것은 배포를 자동화하는 것뿐 아니라, 문제가 생겼을 때 빠르게 되돌릴 수 있도록 설계하는 것입니다.

많은 사람들이 AI에게 "배포 스크립트 만들어줘"라고 요청합니다. 그런데 어떤 배포 전략을 원하는지, 롤백 조건은 무엇인지 알지 못하면 AI가 만들어준 스크립트가 실제 상황에서 쓸 수 없는 경우가 생깁니다. 배포 전략은 단순한 기술 설정이 아니라 서비스 위험을 어떻게 관리할지의 선택입니다.

> 배포는 최대한 작게, 되돌릴 수 있게, 관찰 가능하게 설계해야 합니다.

---

## 이 글에서 다룰 문제
- CD는 CI와 무엇이 같고 무엇이 다를까요?
- Rolling, Blue-Green, Canary 전략은 각각 어떤 위험을 줄이기 위해 쓰일까요?
- 코드 배포와 기능 활성화를 왜 분리해야 할까요?
- 바이브코딩 환경에서 배포 전략을 어떻게 선택해야 할까요?
- 롤백을 설계에 포함하지 않으면 어떤 일이 생길까요?

## 배포 전략 비교: 어떤 위험을 줄이는가

배포 전략의 핵심 질문은 "문제가 생겼을 때 영향 범위를 얼마나 작게 만들 수 있는가"입니다.

| 전략 | 방식 | 다운타임 | 롤백 속도 | 추천 상황 |
|---|---|---|---|---|
| Rolling | 서버를 하나씩 새 버전으로 교체 | 거의 없음 | 빠름 | 상태 없는 서비스, 소규모 팀 |
| Blue-Green | 두 환경 준비 후 트래픽 전환 | 없음 | 매우 빠름 | 즉시 롤백 필요, 인프라 여유 있을 때 |
| Canary | 일부 트래픽만 새 버전에 보내고 관찰 | 없음 | 빠름 | 대규모 트래픽, 점진 검증 필요 |
| Feature flag | 코드는 배포 후 기능만 스위치로 제어 | 없음 | 즉시 | 기능 단위 통제, A/B 테스트 |

바이브코딩으로 빠르게 기능을 만든다면 Feature flag 조합을 고려하세요. 코드를 배포하되 기능을 켜지 않으면 배포 위험과 기능 공개를 분리할 수 있습니다.

## 최소 CD 파이프라인 구조

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy.sh staging
      - run: curl -f https://staging.example.com/health

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy.sh production
      - run: curl -f https://production.example.com/health
```

`environment: production`을 설정하면 GitHub에서 프로덕션 배포에 수동 승인 게이트를 붙일 수 있습니다.

## Before / After

**Before**: "배포할 때마다 모든 서버를 한 번에 새 버전으로 올렸다. 한 번은 버그가 있어서 전체 서비스가 5분간 중단됐다. 롤백하는 데도 10분이 걸렸다."

**After**: "먼저 10%의 트래픽만 새 버전으로 보내고 5분간 에러율을 봤다. 정상이면 100%로 확대, 문제면 즉시 롤백. 최악의 경우에도 사용자 10%만 영향을 받는다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 롤백 방법을 배포 후에 생각하는 실수 | 장애 중에 롤백 명령을 처음 찾으면 너무 늦음 | 배포 설계 단계에서 롤백 명령을 런북에 기록 |
| 스테이징 없이 바로 프로덕션 배포하는 실수 | 버그를 사용자가 먼저 발견하게 됨 | main 머지 → 스테이징 자동 배포 → 승인 → 프로덕션 |
| AI가 만든 배포 스크립트를 검토 없이 쓰는 실수 | 환경 변수 노출, 권한 설정 누락 등이 있을 수 있음 | AI 생성 스크립트도 반드시 보안 관점에서 리뷰 |
| Feature flag를 정리하지 않는 실수 | 몇 달 후엔 어떤 플래그가 어디에 쓰이는지 아무도 모름 | 플래그 목록과 만료 날짜를 함께 관리 |
| Canary 후 지표를 보지 않는 실수 | Canary는 천천히 배포하는 것이 아니라 관찰이 목적임 | 5분 관찰 체크리스트를 런북에 미리 작성 |

## AI에게 배포 관련 질문하는 팁

배포 파이프라인이나 전략을 AI에게 요청할 때 이 정보를 포함하면 더 정확한 결과를 받습니다:

```
배포 대상: [AWS EC2, Kubernetes, Heroku 등]
현재 배포 방식: [수동 SSH, 기존 스크립트 등]
원하는 전략: [Rolling / Blue-Green / Canary]
롤백 조건: [에러율 X% 초과, 지연시간 Y ms 초과]
승인 게이트: [자동 / 수동 승인 필요]
```

AI에게 배포 전략을 요청할 때 "빠르게 배포해줘"보다 "스테이징 자동 배포, 스모크 테스트 통과 후 수동 승인, 프로덕션 Canary 10% → 5분 관찰 → 100%로 확대하는 GitHub Actions 워크플로를 만들어줘"처럼 구체적으로 요청하세요.

## 운영 체크리스트

- [ ] 스테이징 자동 배포가 존재합니다
- [ ] 스모크 테스트가 배포 직후 자동으로 실행됩니다
- [ ] 롤백 명령이 런북에 작성되어 있습니다
- [ ] 배포 직후 에러율과 응답 시간을 확인하는 절차가 있습니다
- [ ] Feature flag 또는 Canary로 기능 공개를 단계적으로 할 수 있습니다

## 처음 질문으로 돌아가기

"배포 전략이 왜 중요한가요? 그냥 서버에 올리면 되지 않나요?"

배포는 운영에서 가장 위험한 순간입니다. 문제가 생겼을 때 영향을 받는 사용자를 10%로 제한하는 것과 100%를 영향받게 하는 것의 차이가 배포 전략입니다. 바이브코딩으로 기능을 빠르게 만들수록, 그 기능을 안전하게 사용자에게 전달하는 배포 전략이 더 중요해집니다.

## 정리

CD는 검증된 코드를 자동으로, 안전하게 사용자에게 전달하는 흐름입니다. 배포 전략의 핵심은 "되돌릴 수 있게 설계하는 것"입니다. 다음 글에서는 같은 코드를 여러 환경에 안전하게 배포하기 위한 환경 분리와 설정 관리를 다룹니다.

## 참고 자료
### 공식 문서
- [Martin Fowler — Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [LaunchDarkly — Feature Flags](https://launchdarkly.com/blog/what-are-feature-flags/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- **바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, CD, Deployment
