---
title: "Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words"
series: azure-aca-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Revision
- Environment
- Blue-Green
- Canary
last_reviewed: '2026-05-12'
seo_description: Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다.
---

# Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words

ACA에서는 Environment, Container App, Revision이라는 세 단어를 계속 만나게 됩니다. 이름은 비슷하게 들리지만 수명과 책임은 전혀 다르고, 그 차이가 배포 방식과 운영 습관을 결정합니다.

이 글은 Azure Container Apps 101 시리즈의 2번째 글입니다. 여기서는 운영자 관점에서 이 세 단어를 분명히 갈라 보겠습니다.

![Azure Container Apps 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/02/02-01-start-with-the-hierarchy.ko.png)
*Azure Container Apps 101 2장 흐름 개요*
> Environment, Container App, Revision — ACA in three words의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- ACA의 세 가지 운영 단위인 Environment, Container App, Revision은 정확히 어떤 책임을 가질까요?
- 어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?
- Single Revision mode와 Multiple Revision mode는 무엇이 다르고, 각각 언제 맞을까요?

## 왜 이 글이 중요한가

ACA를 처음 만지면 포털과 CLI에 같은 세 단어가 반복해서 등장합니다. Environment, Container App, Revision. 이름은 비슷해 보여도 실제로는 수명, 가변성, 소유 범위가 모두 다릅니다.

이 셋을 헷갈리면 익숙한 사고가 바로 따라옵니다.

- 팀과 서비스마다 Environment를 따로 만들어 비용과 운영 부담이 폭증합니다
- "환경 변수만 바꿨는데요" 했지만 새 Revision이 생기고 트래픽이 잠깐 흔들립니다
- "롤백했습니다"라고 말했지만 실제로는 또 다른 새 Revision이 생겨 있습니다
- Single mode에서 canary를 시도했다가 새 버전에 트래픽 100%가 한 번에 넘어갑니다

이 글은 운영 관점에서 그 세 단어를 분리해 줍니다.

## 멘탈 모델

> Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다.

건물(Environment)은 한 번 지으면 오래 갑니다. 공유 인프라, 예를 들면 VNet, 로그 목적지, Dapr 공통 설정은 이 수준에 놓입니다.

사무실(Container App)은 건물 안의 한 회사입니다. "orders API"나 "payments worker" 같은 서비스 정체성을 가지며, 시간이 흘러도 같은 이름과 엔드포인트를 유지합니다.

자리 배치(Revision)는 그 사무실의 특정 시점 스냅샷입니다. 의자 하나만 옮겨도 새 배치가 됩니다. 마음에 들지 않으면 어제 배치로 되돌아가면 됩니다.

## 계층부터 먼저 보기

Environment는 경계입니다. Container App은 논리적인 서비스입니다. Revision은 이미지와 설정의 불변 스냅샷입니다.

개수 관계는 다음과 같습니다.

- 하나의 Environment 안에 여러 Container App이 들어갈 수 있습니다.
- 하나의 Container App은 시간에 따라 여러 Revision을 가질 수 있습니다.
- 하나의 Revision은 정확히 하나의 이미지와 하나의 설정 집합에 묶입니다.

## 핵심 개념 1 — Environment

Environment는 ACA의 공유 경계입니다. 하나의 Environment 안에 있는 모든 앱은 아래를 공유합니다.

- 같은 VNet(네트워크 경계, 내부 통신 가능)
- 같은 Log Analytics workspace(로그 목적지)
- 같은 Dapr component 정의
- 같은 리전(리전마다 별도의 Environment가 필요합니다)

> Environment는 자주 만드는 리소스가 아닙니다. 팀, 환경(dev/staging/prod), 규제 경계 기준으로 묶어야 비용, 운영, 관측성을 모두 관리하기 쉽습니다.

## 핵심 개념 2 — Container App

Container App은 시간의 흐름을 가로질러 유지되는 서비스 정체성입니다. URL 엔드포인트, 이름, ingress 설정, secret은 이 수준에 있습니다.

Container App은 아래 요소를 소유합니다.

- 이미지 참조
- 환경 변수와 secret 참조
- Ingress(external / internal / disabled)
- CPU/메모리 리소스 제한
- 스케일 규칙(min/max replica, KEDA scaler)

이 속성 중 일부를 바꾸면 변경을 반영하기 위해 Container App이 자동으로 새 Revision을 만듭니다. 바로 다음 섹션에서 어떤 변경이 여기에 해당하는지 정리합니다.

## 핵심 개념 3 — Revision

Revision은 이미지 + 설정의 불변 스냅샷입니다. 한번 만들어진 Revision은 수정되지 않습니다. 변경을 적용하려면 새 Revision을 만들고, 그쪽으로 트래픽을 옮겨야 합니다.

- 0%–100% 사이의 트래픽 가중치를 받을 수 있습니다
- active/inactive 상태를 가집니다
- 트래픽을 이전 Revision으로 즉시 되돌릴 수 있는데, 이것이 rollback입니다
- "rollback"은 새 Revision을 만드는 작업이 아니라 기존 Revision 사이의 가중치를 조정하는 작업입니다

## 적용 전후 비교
**Before — (team × service × stage)마다 Environment 하나**

```bash
az containerapp env create --name env-orders-dev ...
az containerapp env create --name env-orders-staging ...
az containerapp env create --name env-orders-prod ...
az containerapp env create --name env-payments-dev ...
# ... Environment count explodes
# Cost: separate Log Analytics workspace, separate VNet
# Ops: register Dapr components in each environment
```

**After — (team × stage)마다 Environment 하나**

```bash
az containerapp env create --name env-team-a-dev ...
az containerapp env create --name env-team-a-prod ...
# Place orders, payments, notifications inside one environment
az containerapp create --name orders --environment env-team-a-prod ...
az containerapp create --name payments --environment env-team-a-prod ...
az containerapp create --name notifications --environment env-team-a-prod ...
```

차이는 꽤 구체적입니다. 두 번째 구조에서는 같은 VNet 안에서 내부 호출이 자유롭고, 로그는 하나의 workspace로 모이며, Dapr component도 한 번만 등록하면 됩니다.

## 실습 — Revision이 실제로 어떻게 움직이는지 보기

### 단계 1. Multiple revision mode로 Container App 만들기

```bash
RG=rg-aca-demo
ENV=aca-env-demo

az containerapp create \
  --name myapi \
  --resource-group $RG \
  --environment $ENV \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --ingress external \
  --target-port 80 \
  --revisions-mode multiple
```

### 단계 2. 새 이미지로 두 번째 Revision 만들기

```bash
az containerapp update \
  --name myapi \
  --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 \
  --revision-suffix v2
```

### 단계 3. 두 Revision 사이에 트래픽 나누기(canary)

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=90 myapi--<v2-suffix>=10
```

### 단계 4. 문제가 생기면 즉시 rollback 하기

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=100 myapi--<v2-suffix>=0
```

핵심은 이것입니다. **rollback은 새 배포가 아니라 가중치 조정**입니다. 수 초 안에 끝납니다.

## 자주 하는 실수

### 실수 1. 서비스마다 Environment를 하나씩 만드는 것

위 Before 예시처럼 개수가 폭증합니다. 기본값은 팀 × 스테이지 기준으로 Environment를 나누는 것입니다.

### 실수 2. Single mode에서 canary를 하려는 것

Single revision mode에서는 새 Revision이 생기는 순간 트래픽 100%가 자동으로 넘어갑니다. Canary나 blue-green을 하려면 처음부터 `--revisions-mode multiple`이어야 합니다.

### 실수 3. rollback을 이전 이미지 재배포라고 생각하는 것

ACA에서 rollback은 이전 Revision의 가중치를 다시 100%로 올리는 일입니다. 새 배포도, 재빌드도, 이미지 푸시도 필요 없습니다. 같은 이유로 최근 Revision은 한동안 남겨 두는 편이 좋습니다.

### 실수 4. 환경 변수 수정은 무중단일 거라고 가정하는 것

환경 변수, 이미지 태그, 스케일 규칙 변경은 새 Revision을 만들고 그쪽으로 트래픽을 보냅니다. ingress가 라우팅을 갱신하는 동안 짧은 시작 지연이 생길 수 있습니다. 확실한 무중단을 원한다면 health probe와 startup probe를 따로 구성해야 합니다.

### 실수 5. inactive Revision을 너무 많이 남겨 두는 것

Inactive Revision 자체가 비싸지는 않지만, 포털과 CLI 목록이 금방 지저분해집니다. "최근 N개 유지" 같은 정책을 정하고 오래된 것은 주기적으로 비활성화하는 편이 좋습니다.

## 실무에서는 이렇게 생각한다

프로덕션에서 이 세 단어를 분리하는 일은 결국 변경의 blast radius를 분리하는 일입니다.

- **Environment 변경**은 드물어야 합니다. 일어나면 VNet, 리전, 로그 workspace 같은 큰 인프라 결정입니다.
- **Container App 변경**은 신중해야 합니다. 이름 변경이나 ingress 변경은 외부 URL을 바꿀 수 있습니다.
- **Revision 변경**은 자주 일어납니다. 배포마다 새 Revision이 생기는 것이 정상입니다.

건강한 ACA 운영은 이 비대칭을 지킵니다. Environment는 드물게, Container App은 가끔, Revision은 거의 매일 바뀝니다.

## 어떤 변경이 새 Revision을 만들까

다음 변경은 새 Revision을 만듭니다.

- 컨테이너 이미지 변경
- 환경 변수 추가, 수정, 삭제
- Secret 변경
- CPU/메모리 제한 변경
- 스케일 규칙 변경(min/max, KEDA scaler)
- Dapr 설정 변경

다음 변경은 새 Revision을 만들지 않습니다.

- 트래픽 가중치 조정(rollback이 여기에 해당합니다)
- Revision active/inactive 전환
- Container App 수준의 태그 변경

## 운영 심화 — Revision 기반 배포 시나리오

Revision 모델을 이해했다면 다음은 실제 배포 규칙을 문서화하는 단계입니다. 아래 두 시나리오는 프로덕션에서 가장 자주 쓰는 패턴입니다.

### 시나리오 A: 점진 배포(10% → 30% → 100%)

```bash
# v3 배포
az containerapp update \
  --name orders-api --resource-group $RG \
  --image myacr.azurecr.io/orders-api:v3 \
  --revision-suffix v3

# 초기 10%
az containerapp ingress traffic set \
  --name orders-api --resource-group $RG \
  --revision-weight orders-api--v2=90 orders-api--v3=10
```

10분 관찰 후 오류율이 안정적이면 30%, 이후 100%로 올립니다.

```bash
az containerapp ingress traffic set --name orders-api --resource-group $RG \
  --revision-weight orders-api--v2=70 orders-api--v3=30
az containerapp ingress traffic set --name orders-api --resource-group $RG \
  --revision-weight orders-api--v2=0 orders-api--v3=100
```

예상 출력 요약:

```text
Latest Revision: orders-api--v3
Active Revisions: 2
Traffic: v2=70, v3=30
```

### 시나리오 B: Blue-Green + 승인 전환

Blue(v2)와 Green(v3)을 동시에 active로 두고, 외부 synthetic 테스트가 통과하면 100% 전환합니다. 실패하면 100/0으로 되돌립니다.

```bash
# 전환
az containerapp ingress traffic set --name orders-api --resource-group $RG \
  --revision-weight orders-api--v2=0 orders-api--v3=100

# 즉시 복귀
az containerapp ingress traffic set --name orders-api --resource-group $RG \
  --revision-weight orders-api--v2=100 orders-api--v3=0
```

### ARM JSON으로 revision mode 고정

```json
{
  "type": "Microsoft.App/containerApps",
  "apiVersion": "2024-03-01",
  "name": "orders-api",
  "properties": {
    "configuration": {
      "activeRevisionsMode": "Multiple",
      "ingress": {
        "external": true,
        "targetPort": 8000,
        "traffic": [
          { "revisionName": "orders-api--v2", "weight": 90 },
          { "revisionName": "orders-api--v3", "weight": 10 }
        ]
      }
    }
  }
}
```

코드 리뷰에서는 `activeRevisionsMode=Multiple`와 traffic 배열 변경을 항상 같이 확인해야 합니다. 둘 중 하나만 바뀌면 의도와 다른 배포가 일어날 수 있습니다.

## 변경 관리 규칙 — 무엇을 승인하고 무엇을 자동화할지

Environment/App/Revision을 분리하면 승인 흐름도 분리할 수 있습니다. 이 구분이 없으면 작은 코드 배포도 인프라 변경과 같은 절차를 거치게 되어 속도가 급격히 떨어집니다.

### 권장 승인 체계

- Environment 변경: 인프라 승인(네트워크, 규제, 로그 보존 영향)
- Container App 구성 변경: 서비스 오너 승인(ingress, 자원, secret)
- Revision 배포/가중치 변경: 배포 오너 자동화 + 사후 기록

### revision 수명주기 정책 예시

```bash
# active revision 조회
az containerapp revision list --name orders-api --resource-group $RG \
  --query "[?properties.active==\`true\`].name" -o tsv

# 오래된 inactive revision 비활성 정리
az containerapp revision list --name orders-api --resource-group $RG \
  --query "[?properties.active==\`false\`].name" -o tsv
```

운영 정책으로 "최근 5개 revision 보존"을 두면 디버깅과 롤백 사이 균형을 맞추기 쉽습니다.

### IaC diff 리뷰 포인트

ARM/Bicep diff에서 아래 필드는 위험도 상위 항목으로 봅니다.

- `managedEnvironmentId`: 서비스 환경 이동 여부
- `configuration.ingress.external`: 외부 노출 여부 변경
- `configuration.ingress.traffic`: 트래픽 가중치 변경
- `template.scale`: min/max 경계 변경
- `template.containers[].image`: 실제 배포 버전 변경

```bash
az deployment group what-if \
  --resource-group $RG \
  --template-file infra/app.bicep \
  --parameters @infra/prod.parameters.json
```

예상 출력에서 `Modify` 대상이 위 필드에 걸리면, 배포 전에 런북 링크를 함께 첨부하는 것을 권장합니다.

### 실패 사례에서 얻는 규칙

- 환경 변수 수정 후 예상치 못한 새 revision 생성: revision 생성 규칙 문서 미흡
- Single mode 상태에서 canary 명령 실행: mode 검사 자동화 누락
- rollback 시 재배포 시도: 트래픽 가중치 기반 롤백 원칙 미정의

이 세 가지는 도구 문제가 아니라 운영 규칙 문제입니다. 규칙을 코드로 옮기면 대부분 예방됩니다.

## 실전 FAQ

### Q1. 포털에서는 정상인데 실제 응답은 불안정한 이유는 무엇일까요?

포털의 Provisioning 성공은 control plane 기준 신호입니다. 실제 사용자 품질은 data plane에서 결정됩니다. 따라서 항상 FQDN 호출 결과, revision health, system log를 함께 봐야 합니다. 운영 체크는 "설정이 저장됐는가"가 아니라 "요청이 안정적으로 처리되는가"로 마무리해야 합니다.

### Q2. `latest` 태그를 쓰면 왜 문제가 될까요?

`latest`는 사람이 보기에는 편하지만 감사/롤백/재현성에 모두 불리합니다. 같은 태그가 다른 이미지를 가리킬 수 있기 때문입니다. 프로덕션에서는 `v1.2.3` 또는 commit SHA처럼 불변 태그를 사용해야 합니다.

### Q3. 스케일과 배포를 동시에 바꾸면 어떤 위험이 있나요?

문제 원인 분리가 어려워집니다. 예를 들어 새 이미지와 새 스케일 규칙을 동시에 올리면 오류가 코드 문제인지 스케일 정책 문제인지 즉시 구분하기 어렵습니다. 안전한 팀은 배포와 스케일 변경을 분리하고, 각 변경마다 관측 지표를 따로 확인합니다.

### Q4. 멀티 서비스에서 네이밍 규칙은 어느 정도로 엄격해야 하나요?

매우 엄격해야 합니다. `orders-api--v12`처럼 서비스명과 revision suffix 패턴을 고정하면 로그, 알림, 런북 자동화가 쉬워집니다. 네이밍이 흔들리면 같은 쿼리를 서비스마다 다르게 써야 하고, 온콜 대응 속도가 느려집니다.

### Q5. 운영 문서에는 최소 무엇이 들어가야 하나요?

- 생성/변경 명령
- 예상 출력
- 실패 시 증상
- 확인할 로그 위치
- 즉시 복구 명령

이 다섯 가지를 글과 저장소 문서에 같이 유지하면, 팀 내 경험 차이가 있어도 대응 품질이 크게 흔들리지 않습니다.

## 참고용 명령 모음

```bash
# 앱 목록
az containerapp list --resource-group $RG -o table

# 단일 앱 상세
az containerapp show --name $APP --resource-group $RG -o json

# revision 목록
az containerapp revision list --name $APP --resource-group $RG -o table

# 트래픽 가중치
az containerapp ingress traffic show --name $APP --resource-group $RG -o table

# 최근 로그
az containerapp logs show --name $APP --resource-group $RG --tail 100
```

운영에서 중요한 것은 명령의 개수가 아니라 실행 순서입니다. 앱 상세 → revision 상태 → 트래픽 가중치 → 로그 순서로 보면 대부분의 이슈를 짧은 시간에 분류할 수 있습니다.

Revision 모델의 장점은 배포를 이벤트처럼 다룰 수 있다는 점입니다. 각 revision은 "무엇이 배포되었는가"를 정확히 가리키는 불변 기록이므로, 장애 분석에서 시간축을 복원하기 쉽습니다. 반대로 이 기록을 관리하지 않으면 revision 목록이 빠르게 오염되어 오히려 추적이 어려워집니다.

실무에서는 revision suffix 규칙을 업무 도메인과 연결해 두는 편이 유리합니다. 예를 들어 `v24-payments-timeout-fix`처럼 원인과 목적을 드러내면, 장애 대응 중에도 어떤 변경이 들어갔는지 즉시 파악할 수 있습니다.

변경 승인 체계와 revision 전략을 분리해 설계하면, 인프라 변경 승인 속도를 높이지 않고도 배포 빈도를 충분히 올릴 수 있습니다. 이 분리는 빠른 팀이 공통으로 갖는 운영 습관입니다.

## 운영 메모 — 팀 합의가 필요한 항목

실제 운영에서는 기술 선택만큼 팀 합의가 중요합니다. 아래 항목은 서비스별로 값이 달라도 되지만, 같은 서비스 안에서는 반드시 고정해야 합니다.

- 배포 단위: 이미지 태그 규칙, revision suffix 규칙
- 검증 단위: healthz 통과 기준, canary 관찰 시간
- 복구 단위: 즉시 rollback 임계치, 단계적 복구 절차
- 기록 단위: 변경 이력, 영향 범위, 후속 액션

합의가 없는 상태에서는 같은 장애라도 담당자마다 전혀 다른 대응을 하게 됩니다. 반대로 합의를 문서와 자동화에 같이 넣으면, 야간 온콜에서도 대응 품질이 안정적으로 유지됩니다.

### 권장 문서 구조

1. 아키텍처 개요와 경계
2. 배포 절차와 검증 절차
3. 장애 분류와 즉시 조치
4. 모니터링 쿼리와 알림 임계치
5. 사후 분석(RCA) 템플릿

이 다섯 장이 준비되면 서비스 성숙도는 빠르게 올라갑니다. 특히 신입 엔지니어가 투입되어도 동일한 기준으로 운영할 수 있어 팀 전체의 평균 대응 시간이 짧아집니다.

## 체크리스트

- [ ] Environment, Container App, Revision 사이의 1:N:N 관계를 직접 그릴 수 있습니다
- [ ] 새 Revision을 만드는 변경을 다섯 가지 이상 말할 수 있습니다
- [ ] 우리 서비스에 Single mode와 Multiple mode 중 무엇이 맞는지 고를 수 있습니다
- [ ] rollback이 재배포가 아니라 가중치 조정이라는 점을 알고 있습니다
- [ ] 서비스마다 Environment를 만들면 왜 안 되는지 설명할 수 있습니다

## 연습 문제

1. 아래 시나리오마다 변경 수준이 Environment, Container App, Revision 중 어디인지 구분해 보세요.
   - "orders API 이미지 태그를 v1.2.3에서 v1.2.4로 올린다"
   - "payments 서비스의 ingress를 internal에서 external로 바꾼다"
   - "팀이 staging 전체를 다른 리전으로 옮기기로 했다"
   - "프로덕션 트래픽의 5%를 새 버전으로 보낸다"
2. 위 Step 1-4를 따라 두 개의 Revision을 만들고 가중치를 50/50으로 나눠 보세요. 그런 다음 각 엔드포인트를 100번씩 호출해서 실제 분포를 측정해 보세요.

## 정리

- Environment는 공유 인프라이며, 드물게 만들어야 합니다.
- Container App은 시간을 가로질러 유지되는 서비스 정체성입니다.
- Revision은 이미지와 설정의 불변 스냅샷이며, 실제 배포 단위입니다.
- Single mode는 단순한 서비스에 맞고, canary나 blue-green에는 Multiple mode가 필요합니다.
- ACA에서 rollback은 가중치 조정이지 새 배포가 아닙니다. 수 초 안에 끝납니다.

다음 글에서는 이 모델을 손으로 다뤄 봅니다. Python/FastAPI 앱을 처음으로 ACA에 배포하고, Container App과 Revision이 실제로 만들어지는 과정을 단계별로 보겠습니다.

## 처음 질문으로 돌아가기

- **ACA의 세 가지 운영 단위인 Environment, Container App, Revision은 정확히 어떤 책임을 가질까요?**
  - `Environment`는 VNet, Log Analytics, Dapr component를 공유하는 큰 경계이고, `Container App`은 `orders`, `payments`, `notifications`처럼 시간에 걸쳐 유지되는 서비스 정체성입니다. `Revision`은 `orders-api--v2`, `orders-api--v3`처럼 이미지와 설정이 고정된 불변 스냅샷이어서 실제 트래픽 가중치와 rollback 대상이 됩니다. 그래서 본문에서는 건물·사무실·자리 배치 비유로 이 세 수준의 수명과 책임을 분리했습니다.
- **어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?**
  - 이미지 태그, 환경 변수, secret, CPU/메모리, `template.scale`, Dapr 설정이 바뀌면 새 Revision이 생깁니다. 반대로 `az containerapp ingress traffic set`으로 하는 트래픽 가중치 조정이나 active/inactive 전환은 새 Revision을 만들지 않고 기존 Revision 상태만 바꿉니다. 이 구분 때문에 rollback을 재배포가 아니라 "가중치 복귀"로 이해해야 한다고 본문에서 반복해서 강조했습니다.
- **Single Revision mode와 Multiple Revision mode는 무엇이 다르고, 각각 언제 맞을까요?**
  - Single mode는 새 Revision이 생기면 트래픽 100%가 즉시 넘어가므로 단순 서비스나 dev 환경에는 편하지만 canary와 blue-green에는 맞지 않습니다. Multiple mode에서는 `az containerapp ingress traffic set --revision-weight orders-api--v2=90 orders-api--v3=10`처럼 두 Revision을 동시에 active로 두고 가중치를 조절할 수 있습니다. 그래서 프로덕션 API라면 보통 `activeRevisionsMode=Multiple`을 기본으로 두고, 관찰 창과 rollback 기준을 함께 운영합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- **Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words (현재 글)**
- Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI (예정)
- Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략 (예정)
- Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N (예정)
- Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 (예정)
- Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Manage revisions in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions-manage)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/02-environment-app-revision)

Tags: Azure, Container Apps, Serverless, Containers
