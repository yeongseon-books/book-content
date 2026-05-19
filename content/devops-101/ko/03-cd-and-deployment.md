---
series: devops-101
episode: 3
title: CD와 배포 전략
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - CD
  - Deployment
  - BlueGreen
  - Canary
seo_description: 되돌릴 수 있는 자동 배포를 위해 CD와 배포 전략의 핵심을 비교합니다.
last_reviewed: '2026-05-12'
---

# CD와 배포 전략

이 글은 DevOps 101 시리즈의 세 번째 글입니다.

## 이 글에서 다룰 문제

- CD는 CI와 무엇이 같고 무엇이 다를까요?
- Rolling, Blue-Green, Canary 전략은 각각 어떤 위험을 줄이기 위해 쓰일까요?
- 코드 배포와 기능 활성화를 왜 분리해야 할까요?
- 배포 설계에서 롤백은 왜 사후 대책이 아니라 핵심 요구사항일까요?
- 자동 배포를 붙이고도 실무에서 자주 놓치는 함정은 무엇일까요?

> **멘탈 모델**: 좋은 배포 전략은 릴리스를 큰 이벤트로 만들지 않습니다. 변경을 작게 나누고, 문제를 빨리 감지하고, 쉽게 되돌릴 수 있게 만들어 배포를 일상적인 운영 흐름으로 바꿉니다.

## 왜 중요한가

배포는 운영에서 가장 위험한 순간입니다. 새 코드가 실제 트래픽을 받기 시작하는 시점이기 때문입니다. 그래서 좋은 전략은 성공률을 막연히 높이는 것이 아니라, 실패했을 때 영향 범위를 얼마나 작게 만들 수 있는지에 집중합니다.

특히 많은 팀이 놓치는 지점이 하나 있습니다. 코드를 프로덕션에 올리는 일과 기능을 사용자에게 노출하는 일은 같은 문제가 아닙니다. 둘을 분리해야 배포는 더 자주 할 수 있고, 기능 공개는 더 신중하게 할 수 있습니다.

> 배포 가능성과 기능 활성화는 분리되어야 합니다.

## 한눈에 보는 개념

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/03/03-01-diagram.ko.png)

*한눈에 보는 개념*

이 그림이 말하는 핵심은 단순합니다. 배포는 한 번에 100%로 가는 점프가 아니라, 검증과 관찰, 확대와 철회를 포함한 흐름이어야 합니다.

## 핵심 용어

- **CD**: 검증된 코드를 지속적으로 전달하거나 배포하는 자동화 흐름입니다.
- **Rolling**: 서버를 하나씩 새 버전으로 교체하는 방식입니다.
- **Blue-Green**: 두 환경을 유지하다가 트래픽을 전환하는 방식입니다.
- **Canary**: 일부 트래픽만 새 버전에 먼저 보내는 방식입니다.
- **Feature flag**: 코드는 배포하되 기능 노출은 스위치로 제어하는 방식입니다.

같은 자동 배포라도 어떤 전략을 고르느냐에 따라 장애 양상이 완전히 달라집니다. 그래서 배포 전략은 배포 도구 설정이 아니라 서비스 위험 모델의 일부로 봐야 합니다.

## Before/After

**Before (big-bang deploy)**

```text
- All servers move to the new version *at once*
- A problem means *full outage*
- Rollback takes *more than 30 minutes*
```

이 방식은 배포가 드문 팀에서 특히 자주 보입니다. 한 번 배포할 때 변경이 너무 많아지고, 그래서 더 무서워지고, 무서우니 더 자주 못 하게 되는 악순환이 생깁니다.

**After (Canary + flag)**

```text
- New version receives *10%* of traffic
- After 5 minutes of monitoring, *50% then 100%*
- On failure, *flag off* blocks it *immediately*
```

작게 배포하고, 지표를 보고, 필요하면 즉시 되돌리는 구조가 갖춰지면 배포는 이벤트가 아니라 반복 가능한 운영 절차가 됩니다.

## 안전한 배포를 위한 5단계

### 1단계 - 스테이징 자동 배포

프로덕션 전에 반드시 한 번 더 검증할 수 있는 환경이 필요합니다. 다만 스테이징이 프로덕션과 너무 다르면 이 단계는 형식만 남게 됩니다.

```yaml
deploy-stage:
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ./deploy.sh stage
```

### 2단계 - 스모크 테스트

배포 직후 최소 기능이 살아 있는지 자동으로 확인해야 합니다. 스테이징에서 이 단계를 통과하지 못하면 프로덕션으로 올릴 이유가 없습니다.

```bash
curl -f https://stage.example.com/health || exit 1
pytest tests/smoke/ --base-url=https://stage.example.com
```

### 3단계 - Canary (10%)

처음부터 전체 트래픽을 보내지 않고 일부만 새 버전에 붙이면 문제를 더 작게 드러낼 수 있습니다. Canary의 핵심은 기술보다도 팀이 미리 합의한 관찰 기준입니다.

```bash
kubectl set image deploy/api api=myapp:v2 --record
kubectl scale deploy/api-v2 --replicas=1   # 10%
```

### 4단계 - 5분 관찰

Canary를 붙였다면 지표를 봐야 합니다. 그렇지 않으면 Canary는 단지 천천히 배포하는 것에 불과합니다.

```text
- error rate < 0.1%
- p95 latency < 200ms
- 5xx counts within normal range
```

### 5단계 - 승격 또는 롤백

마지막 단계는 확장과 철수 모두가 자동화 가능한지 확인하는 것입니다. 되돌리기 명령이 문서에만 있고 실전에서 안 되면 좋은 전략이라고 보기 어렵습니다.

```bash
# OK
kubectl scale deploy/api-v2 --replicas=10

# NG
kubectl rollout undo deploy/api
```

## 배포 직후 10분 검증 순서

Canary를 붙였다고 자동으로 안전해지는 것은 아닙니다. 실제로 중요한 것은 배포 직후 첫 10분에 팀이 같은 순서로 같은 신호를 확인하는지입니다. 아래처럼 확인 순서를 미리 런북에 적어 두면 배포 품질이 눈에 띄게 안정됩니다.

```text
T+0m  health endpoint 200 확인
T+2m  5xx 비율과 p95 지연시간 비교
T+5m  신규 버전 로그에서 예외 패턴 확인
T+7m  DB connection pool, queue depth, cache hit ratio 확인
T+10m 승격 또는 롤백 결정
```

이 순서는 단순해 보이지만 효과가 큽니다. 애플리케이션 메트릭만 보고 끝내지 않고, 배포가 자주 건드리는 의존성 계층까지 함께 확인하기 때문입니다. 특히 연결 수, 큐 적체, 캐시 미스율은 신규 코드가 직접 문제를 일으키지 않았더라도 바로 나빠지기 쉬운 지표입니다.

## 롤백을 배포 설계의 일부로 만드는 방법

롤백은 장애가 난 뒤에 떠올리는 비상 버튼이 아니라, 배포 설계 문서에 처음부터 들어 있어야 하는 요구사항입니다. 예를 들어 애플리케이션 버전 롤백과 데이터베이스 마이그레이션 롤백은 전혀 같은 문제가 아닙니다. 스키마 변경이 하위 호환이 아니면 앱만 되돌려도 서비스가 복구되지 않을 수 있습니다.

그래서 운영팀은 보통 아래 질문을 배포 전 체크리스트에 함께 넣습니다.

- 이번 배포는 기능 플래그만 끄면 영향 차단이 가능한가?
- 애플리케이션 이미지만 되돌리면 복구되는가?
- DB 스키마는 expand/contract 방식으로 하위 호환을 유지하는가?
- 롤백 후 다시 앞으로 가는 재배포 경로도 검증했는가?

이 네 가지가 답되지 않으면 자동 배포가 있어도 실제 운영 안정성은 크게 올라가지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 스테이징은 프로덕션과 최대한 닮아 있어야 합니다.
- Canary 판단에 쓸 기준 지표는 미리 정의되어 있어야 합니다.
- 롤백 명령은 런북에 살아 있는 형태로 남아 있어야 합니다.

배포 전략의 실전 품질은 "어떤 방식을 쓴다"보다 "실패했을 때 팀이 어디를 보고 무엇을 누르는지 분명한가"에서 갈립니다.

## 자주 하는 실수 5가지

1. **CI는 자동인데 CD는 수동인 실수**입니다. 마지막 단계에 사람이 끼면 실수와 편차가 다시 들어옵니다.
2. **스테이징과 프로덕션이 다른 실수**입니다. 버그를 재현하기 가장 어려운 구조가 됩니다.
3. **Canary 뒤 지표를 보지 않고 100%로 가는 실수**입니다. 그 순간 Canary의 의미가 사라집니다.
4. **Feature flag를 정리하지 않는 실수**입니다. 몇 달 지나면 무엇이 살아 있는지 아무도 모르게 됩니다.
5. **롤백 훈련이 없는 실수**입니다. 실제 장애가 첫 훈련이 되면 이미 늦습니다.

## 실무에서는 이렇게 이어집니다

대규모 서비스는 Canary Analysis를 자동화해서 지표 비교까지 도구가 대신하게 만듭니다. Spinnaker나 Argo Rollouts를 쓰는 이유도 배포 자체보다, 배포 이후 판단 과정을 더 일관되게 만들기 위해서입니다.

작은 팀이라면 처음부터 복잡한 도구를 붙일 필요는 없습니다. 스테이징 자동 배포, 스모크 테스트, 롤백 명령 문서화, 기능 플래그 네 가지부터 갖추는 편이 훨씬 실용적입니다.

## 시니어 엔지니어는 이렇게 봅니다

- 모든 배포는 되돌릴 수 있어야 합니다.
- 기능 공개는 기능 플래그를 통해 배포와 분리해야 합니다.
- Canary 지표는 팀 전체가 합의해야 합니다.
- 데이터베이스 마이그레이션은 하위 호환을 전제로 설계해야 합니다.
- 배포를 더 자주 할수록 오히려 더 안전해질 수 있습니다.

## 체크리스트

- [ ] 스테이징 자동 배포가 존재합니다.
- [ ] 스모크 테스트가 자동화되어 있습니다.
- [ ] 롤백 명령이 문서화되어 있습니다.
- [ ] 기능 플래그 시스템이 존재합니다.

## 연습 문제

1. 현재 서비스의 배포 단계를 그림으로 그려 보세요.
2. 런북에 롤백 명령을 실제로 추가해 보세요.
3. 팀과 함께 Canary 판단에 쓸 지표 세 가지를 정해 보세요.

## 정리 및 다음 단계

CD는 되돌릴 수 있는 작은 변경의 흐름입니다. 다음 글에서는 여러 환경에 같은 코드를 안전하게 배포하기 위한 설정 관리 방식을 다룹니다.

<!-- toc:begin -->
- [DevOps란 무엇인가?](./01-what-is-devops.md)
- [CI 파이프라인](./02-ci-pipeline.md)
- **CD와 배포 전략 (현재 글)**
- 환경 분리와 설정 관리 (예정)
- Infrastructure as Code (예정)
- 컨테이너와 빌드 (예정)
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [LaunchDarkly — Feature Flags](https://launchdarkly.com/blog/what-are-feature-flags/)
- [Spinnaker](https://spinnaker.io/)

Tags: DevOps, CD, Deployment, BlueGreen, Canary
