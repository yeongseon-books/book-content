---
series: devops-101
episode: 3
title: "DevOps 101 (3/10): CD와 배포 전략"
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

# DevOps 101 (3/10): CD와 배포 전략

이 글은 DevOps 101 시리즈의 세 번째 글입니다.

![DevOps 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/03/03-01-diagram.ko.png)
*DevOps 101 3장 흐름 개요*
> CD의 핵심은 배포 가능성과 기능 활성화를 분리하여 더 자주, 더 안전하게 배포하는 것입니다.

## 먼저 던지는 질문

- CD는 CI와 무엇이 같고 무엇이 다를까요?
- Rolling, Blue-Green, Canary 전략은 각각 어떤 위험을 줄이기 위해 쓰일까요?
- 코드 배포와 기능 활성화를 왜 분리해야 할까요?

## 왜 중요한가

배포는 운영에서 가장 위험한 순간입니다. 새 코드가 실제 트래픽을 받기 시작하는 시점이기 때문입니다. 그래서 좋은 전략은 성공률을 막연히 높이는 것이 아니라, 실패했을 때 영향 범위를 얼마나 작게 만들 수 있는지에 집중합니다.

특히 많은 팀이 놓치는 지점이 하나 있습니다. 코드를 프로덕션에 올리는 일과 기능을 사용자에게 노출하는 일은 같은 문제가 아닙니다. 둘을 분리해야 배포는 더 자주 할 수 있고, 기능 공개는 더 신중하게 할 수 있습니다.

> 배포 가능성과 기능 활성화는 분리되어야 합니다.

## 한눈에 보는 개념

이 그림이 말하는 핵심은 단순합니다. 배포는 한 번에 100%로 가는 점프가 아니라, 검증과 관찰, 확대와 철회를 포함한 흐름이어야 합니다.

## 핵심 용어

- **CD**: 검증된 코드를 지속적으로 전달하거나 배포하는 자동화 흐름입니다.
- **Rolling**: 서버를 하나씩 새 버전으로 교체하는 방식입니다.
- **Blue-Green**: 두 환경을 유지하다가 트래픽을 전환하는 방식입니다.
- **Canary**: 일부 트래픽만 새 버전에 먼저 보내는 방식입니다.
- **Feature flag**: 코드는 배포하되 기능 노출은 스위치로 제어하는 방식입니다.

같은 자동 배포라도 어떤 전략을 고르느냐에 따라 장애 양상이 완전히 달라집니다. 그래서 배포 전략은 배포 도구 설정이 아니라 서비스 위험 모델의 일부로 봐야 합니다.

## 배포 전략 비교

배포 전략은 단순히 새 코드를 올리는 방식의 차이가 아닙니다. 실패했을 때 얼마나 빠르게 되돌릴 수 있고, 영향 범위를 얼마나 작게 제한할 수 있는지를 결정하는 구조적 차이입니다.

| 전략 | 다운타임 | 롤백 속도 | 복잡도 | 적합 상황 |
|---|---|---|---|---|
| 롤링 (Rolling) | 거의 없음 | 빠름 (1-5분) | 낮음 | 상태 없는 서비스, 부분 장애 허용 |
| 블루그린 (Blue-Green) | 없음 | 매우 빠름 (트래픽 전환만) | 중간 (이중 환경 유지) | 즐각 롤백 필요, 인프라 비용 감당 가능 |
| 카나리 (Canary) | 없음 | 빠름 (5-10분 관찰 후) | 높음 (지표 모니터링 필수) | 대규모 트래픽, 점진적 검증 선호 |
| 피처 플래그 (Feature Flag) | 없음 | 즉시 (플래그 off) | 고등 (코드베이스 분기 증가) | 기능 단위 통제, A/B 테스트 |

중요한 것은 한 가지 전략이 다른 것보다 항상 나을 것은 없다는 사실입니다. 조직의 위험 허용도, 트래픽 규모, 인프라 비용, 팀 역량에 따라 최적 선택이 달라집니다. 현실에서는 롤링 + 피처플래그 조합이 가장 흔합니다.

## 배포 파이프라인 설계

배포 파이프라인은 배포 자체보다 배포 전후 검증 단계를 어떻게 구조화하느냐가 더 중요합니다. 아래는 현실적으로 운영 가능한 5단계 CD 파이프라인입니다.

### 1단계 - 스테이징 자동 배포

main 브랜치에 코드가 머지되면 스테이징 환경에 자동으로 배포됩니다. 이 단계가 없으면 프로덕션 배포 전 최종 검증이 불가능합니다.

### 2단계 - 스모크 테스트

배포 직후 핵심 기능이 동작하는지 자동으로 확인합니다. 실패하면 프로덕션 승격을 차단합니다.

### 3단계 - 프로덕션 Canary (10%)

전체 트래픽의 10%만 새 버전으로 보냅니다. 이 단계에서 문제가 발견되면 영향 범위는 10%로 제한됩니다.

### 4단계 - 5분 관찰

Canary 지표를 모니터링합니다. 5xx 비율, p95 지연시간, 에러 로그를 확인합니다.

### 5단계 - 승격 또는 롤백

지표가 정상이면 50% → 100%로 확대합니다. 문제가 발견되면 즉시 롤백합니다.

이 5단계를 파이프라인으로 코드화하면 배포는 이벤트가 아니라 반복 가능한 절차가 됩니다.

## 야믈 지속적 배포 파이프라인 예시

CD는 CI와 전혀 다른 에세를 가집니다. CI는 코드 품질을 검증하지만, CD는 실제 환경에 노출하는 순간을 다룹니다. 아래는 스테이징과 프로덕션 배포를 병렬로 관리하는 예시입니다.

```yaml
# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        run: ./scripts/deploy.sh staging
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.example.com/health
          pytest tests/smoke/ --base-url=https://staging.example.com
      
      - name: Notify deployment
        if: success()
        run: echo "Staging deployment successful"

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy canary (10%)
        run: ./scripts/deploy.sh prod --canary 10
      
      - name: Wait and monitor
        run: sleep 300  # 5 minutes
      
      - name: Check canary metrics
        id: canary-check
        run: |
          ERROR_RATE=$(curl -s https://metrics.example.com/api/error_rate)
          if (( $(echo "$ERROR_RATE > 0.001" | bc -l) )); then
            echo "Canary failed: error rate too high"
            exit 1
          fi
      
      - name: Promote to 100%
        if: success()
        run: ./scripts/deploy.sh prod --promote 100
      
      - name: Rollback on failure
        if: failure()
        run: ./scripts/rollback.sh prod
```

이 파이프라인은 스테이징 성공 후에만 프로덕션 배포를 진행합니다. Canary 지표가 임계값을 넘으면 자동으로 롤백합니다. 이것이 안전한 CD의 핵심입니다.
## 전환 전후

**Before (빅뱅 배포)**

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

## 지속적 배포 전략을 선택할 때 보는 실무 기준

CD는 자동 배포 자체보다 "위험을 통제한 채로 변경을 전달하는 운영 규칙"에 가깝습니다. 같은 자동 배포라도 전환 방식, 모니터링 기준, 롤백 경로에 따라 결과는 완전히 달라집니다.

### 배포 전략 비교표

| 전략 | 전환 방식 | 장점 | 단점 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| Blue-Green | 두 환경 준비 후 트래픽 스위치 | 즉시 롤백 용이 | 인프라 비용 증가 | 상태 비저장 서비스 |
| Canary | 일부 트래픽부터 점진 확대 | 위험 국소화 | 관측 설계 필요 | 사용자 규모 큰 서비스 |
| Rolling | 인스턴스 순차 교체 | 추가 비용 낮음 | 버전 혼재 시간 존재 | 전통적 VM/K8s 환경 |

전략 선택은 정답 문제가 아닙니다. 서비스 특성, 트래픽 패턴, 데이터 마이그레이션 제약을 함께 고려해야 합니다.

### GitHub Actions 기반 CD 예시

```yaml
name: cd
on:
  push:
    branches: [main]
jobs:
  deploy-stage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_stage.sh

  smoke-test:
    runs-on: ubuntu-latest
    needs: deploy-stage
    steps:
      - run: ./scripts/smoke_test.sh https://stage.example.com

  deploy-prod:
    runs-on: ubuntu-latest
    needs: smoke-test
    steps:
      - run: ./scripts/deploy_prod_canary.sh
```

### Argo CD 애플리케이션 선언 예시

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-prod
spec:
  project: default
  source:
    repoURL: https://github.com/example/platform-manifests
    targetRevision: main
    path: apps/api/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: api
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

GitOps 기반 CD에서는 배포 명령보다 선언 상태의 수렴이 중요합니다. 누가 어떤 커밋으로 어떤 환경을 바꿨는지가 남아 운영 가시성이 높아집니다.

### 승격 기준 예시

| 단계 | 필수 조건 |
| --- | --- |
| stage -> canary | 스모크 테스트 통과, 주요 에러율 정상 범위 |
| canary 10% -> 50% | 5분 관찰, p95 지연시간 기준 충족 |
| canary 50% -> 100% | 고객 영향 없음, 로그 이상 패턴 없음 |
| rollback | 에러율 임계 초과 또는 비정상 지표 지속 |

### 기능 플래그와 배포 분리

```python
from fastapi import FastAPI

app = FastAPI()
FEATURE_NEW_CHECKOUT = False

@app.get('/checkout')
def checkout():
    if FEATURE_NEW_CHECKOUT:
        return {'path': 'new'}
    return {'path': 'legacy'}
```

실무에서는 플래그 값을 원격 구성으로 빼고 점진 활성화합니다. 핵심은 코드 배포와 사용자 노출 시점을 분리해 사고 반경을 줄이는 것입니다.

### CD 품질을 높이는 운영 규칙

1. 롤백 명령을 문서가 아니라 자동화 스크립트로 검증합니다.
2. 배포 직후 10분 체크리스트를 팀 공통으로 사용합니다.
3. DB 마이그레이션은 expand/contract로 하위 호환을 유지합니다.
4. 배포 성공 정의를 "완료"가 아니라 "관찰 통과"로 둡니다.

이 규칙이 자리 잡으면 CD는 속도만 빠른 배포가 아니라, 학습 가능한 운영 프로세스로 진화합니다.

### 배포 전략 선택 체크리스트

실무에서는 전략 이름보다 전제 조건을 먼저 확인해야 합니다. Blue-Green은 전환은 빠르지만 두 환경을 동시에 유지할 인프라 여유가 필요합니다. Canary는 비용 효율이 좋지만 관측성과 자동 판단 기준이 없으면 운영자가 매번 수동으로 결정을 내려야 합니다. Rolling은 단순하지만 버전 혼재 구간에서 세션/캐시 호환성을 점검해야 합니다.

| 질문 | Yes면 추천 |
| --- | --- |
| 트래픽 일부만 먼저 흘려 검증 가능한가 | Canary |
| 즉시 전환/즉시 철회가 중요한가 | Blue-Green |
| 비용 제약이 강하고 구조가 단순한가 | Rolling |

배포 전략은 한 번 정하고 끝나는 설정이 아닙니다. 서비스 트래픽과 장애 패턴이 바뀌면 승격 기준도 함께 조정해야 합니다.

추가로 배포 전환 자동화에서는 사람 승인 지점을 최소화하되, 고위험 변경만 선택적으로 승인하도록 정책을 나누는 것이 좋습니다. 예를 들어 스키마 변경 포함 배포는 승인 필요, 단순 애플리케이션 패치 배포는 자동 승격처럼 규칙을 분리하면 속도와 안정성을 함께 확보할 수 있습니다.

```text
## 0-5분
1. SEV 판정 (SEV1/SEV2)
2. incident 채널 개설
3. 최근 배포 커밋 확인

## 5-10분
1. canary/최근 릴리스 롤백 시도
2. 에러율, p95, DB 연결수 확인
3. 고객 영향 범위 요약 공지

## 10-20분
1. 임시 완화 조치 적용
2. 영구 수정 owner 지정
3. postmortem 일정 예약
```

운영에서는 "잘 아는 사람"보다 "같은 순서를 따르는 팀"이 더 빠르게 복구합니다. 그래서 runbook은 설명 문서가 아니라 실행 문서여야 하며, 경보에서 한 번에 열 수 있어야 합니다.

## 처음 질문으로 돌아가기

- **CD는 CI와 무엇이 같고 무엇이 다를까요?**
  - CI와 CD 모두 자동화된 흐름이지만, 이 글에서 CI는 코드 품질을 검증하는 단계이고 CD는 그 결과를 스테이징과 프로덕션에 전달하는 단계입니다. 예시 파이프라인의 `deploy-staging -> smoke tests -> canary -> promote/rollback` 순서가 바로 CD가 다루는 운영 영역입니다.
- **Rolling, Blue-Green, Canary 전략은 각각 어떤 위험을 줄이기 위해 쓰일까요?**
  - Rolling은 서버를 순차 교체해 추가 비용을 줄이고, Blue-Green은 두 환경을 두어 트래픽 전환만으로 즉시 롤백할 수 있게 합니다. Canary는 10% 트래픽과 5분 관찰처럼 영향 범위를 작게 제한하며, Feature flag는 코드 배포 후에도 기능 노출을 따로 끌 수 있게 해 사고 반경을 더 줄여 줍니다.
- **코드 배포와 기능 활성화를 왜 분리해야 할까요?**
  - 본문은 `FEATURE_NEW_CHECKOUT` 예시처럼 코드는 먼저 배포하고 사용자 노출은 플래그로 제어하는 방식을 권합니다. 이렇게 해야 문제 발생 시 이미지 전체를 다시 내리지 않아도 기능만 즉시 차단할 수 있고, 카나리 관찰과 롤백 판단도 더 유연해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
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

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, CD, Deployment, BlueGreen, Canary
