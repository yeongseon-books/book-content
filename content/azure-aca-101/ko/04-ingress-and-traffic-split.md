---
title: Ingress와 트래픽 분할 — Revision 기반 배포 전략
series: azure-aca-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Ingress
- Canary
- Blue-Green
- Traffic Split
last_reviewed: '2026-05-03'
seo_description: Ingress는 ACA의 "건물 정문"이고, traffic weight는 "엘리베이터 호출 비율"입니다.
---

# Ingress와 트래픽 분할 — Revision 기반 배포 전략

Ingress와 트래픽 분할은 ACA에서 가장 자주 만지는 운영 레버입니다. 설정 한두 줄 차이로 외부 노출 방식과 배포 안전성이 함께 달라지기 때문에 둘을 따로 보면 자주 놓칩니다.

이 글은 Azure Container Apps 101 시리즈의 4번째 글입니다. 여기서는 Revision 기반 배포 전략까지 한 흐름으로 묶어 보겠습니다.

---

## 핵심 질문

Ingress와 트래픽 분할을 어떻게 설계해야 점진적 배포가 안전할까요?

이 글은 그 질문에 답하기 위해 Ingress와 트래픽 분할의 핵심 결정과 운영 함정을 살펴봅니다.

## 이 글에서 다룰 문제

ACA의 가장 강력한 production feature 하나가 바로 Revision 기반 traffic split입니다. 그런데 이걸 제대로 쓰려면 ingress 설정이 먼저 맞아야 합니다.

흔한 incident:

- "external ingress가 켜져 있는데도 외부에서 연결이 안 된다" → `target-port` 불일치
- "canary로 10%만 보내려 했는데 100%가 새 버전으로 갔다" → Single mode였음
- "rollback이 새 deployment처럼 몇 분 걸린다고 들었다" → 실제로는 weight 조정이라 수 초
- "internal ingress라고 만들었는데 인터넷에서 접근된다" → ingress mode를 제대로 안 본 것

이 글은 ingress와 traffic split을 한 흐름으로 묶어 그 사고들의 원인을 끊어줍니다.

## Mental Model

> Ingress는 ACA의 "건물 정문"이고, traffic weight는 "엘리베이터 호출 비율"입니다.

정문(Ingress)은 외부 손님을 받느냐(`external`), 같은 건물 사람만 받느냐(`internal`), 아예 닫느냐(`disabled`)를 결정합니다. 정문을 통과한 손님은 엘리베이터(traffic split rule)에 따라 사무실의 어느 자리(Revision)로 갈지 비율로 결정됩니다.

이 두 단계가 분리돼 있어서 "외부 노출"과 "버전 분배"를 따로 운영할 수 있습니다.

## 요청 경로

ACA의 관리형 Ingress 계층이 앞문 역할을 맡고, weight에 따라 활성 Revision으로 트래픽을 분배합니다.

![Ingress가 요청을 활성 Revision으로 보내는 경로](../../../assets/azure-aca-101/04/04-01-the-request-path.ko.png)

*Ingress가 요청을 활성 Revision으로 보내는 경로*

핵심 단계:

1. Client가 `https://<app>.<env-id>.<region>.azurecontainerapps.io`로 접속
2. ACA 관리형 envoy proxy가 TLS 종료 처리
3. 같은 Container App에 묶인 Revision들의 weight 표를 조회
4. 비율에 따라 한 Revision의 replica 중 하나로 routing
5. Replica가 응답을 돌려주고, 로그가 Log Analytics로 흐름

## 핵심 개념 1 — Ingress 모드 세 가지

| 모드 | 노출 범위 | URL | 적합한 워크로드 |
|---|---|---|---|
| `external` | 인터넷 전체 | `https://<app>.<env-id>.<region>.azurecontainerapps.io` | public API, 웹 프론트엔드 |
| `internal` | 같은 Environment 내부만 | `https://<app>.internal.<env-id>.<region>.azurecontainerapps.io` | microservice 간 호출 |
| `disabled` | 노출 안 함 | (없음) | worker, batch, 메시지 컨슈머 |

CLI 예시:

```bash
az containerapp ingress enable \
  --name myapi --resource-group $RG \
  --type external --target-port 8000 --transport auto
```

`--transport`는 `auto`(권장), `http`, `http2`, `tcp` 중 하나입니다.

## 핵심 개념 2 — Single vs Multiple revision mode

| 항목 | Single mode | Multiple mode |
|---|---|---|
| 활성 Revision 개수 | 항상 1개 | N개 동시 활성 |
| 새 Revision 배포 시 | 100% 트래픽 즉시 이동 | weight 그대로 유지 |
| Canary | 불가 | 가능 |
| Blue-Green | 불가 | 가능 |
| 적합한 service | 단순 service, dev 환경 | production API |

기본값은 Single입니다. **production은 Multiple로 만드는 것이 안전합니다.**

```bash
az containerapp revision set-mode \
  --name $APP_NAME --resource-group $RG \
  --mode multiple
```

## Before / After

**Before — Single mode에서 canary를 시도**

```bash
# Single mode 상태
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2
# → 새 Revision 생성과 동시에 100% 트래픽이 v2로 이동
# 사용자 일부에게만 보내려던 의도와 정반대 결과
```

**After — Multiple mode + weight split**

```bash
# 1. Multiple mode로 전환
az containerapp revision set-mode --name myapi --resource-group $RG --mode multiple

# 2. 새 Revision 배포 (트래픽은 아직 0%)
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# 3. 점진적으로 weight 조정
az containerapp ingress traffic set --name myapi --resource-group $RG \
  --revision-weight myapi--v1=90 myapi--v2=10
```

차이는 **의도한 비율로** 흘려보낼 수 있느냐입니다.

## 단계별 실습 — 90/10 canary와 즉시 rollback

### Step 1. Multiple mode로 전환

```bash
RG=rg-aca-demo
APP=myapi

az containerapp revision set-mode --name $APP --resource-group $RG --mode multiple
```

### Step 2. v1 배포 (단일 Revision으로 100%)

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v1 --revision-suffix v1
```

### Step 3. v2 배포 (트래픽 0%로 시작)

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# 처음에는 v1=100, v2=0으로 잡아두기
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

### Step 4. 90/10 canary 시작

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=90 $APP--v2=10
```

이제 Log Analytics에서 `RevisionName`별로 error rate, latency를 비교합니다.

### Step 5a. 좋아 보이면 50/50 → 0/100 진행

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=50 $APP--v2=50
# 모니터링 후
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=0 $APP--v2=100
```

### Step 5b. 문제 보이면 즉시 rollback

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

수 초 안에 v2 트래픽이 0이 됩니다.

## 자주 하는 실수

### 실수 1. `target-port`를 ingress port와 혼동한다

`--target-port`는 **컨테이너 안의** listening port입니다. 외부에 노출되는 port는 항상 443 (HTTPS)입니다. ACA가 알아서 매핑합니다.

### 실수 2. `internal` ingress인데 NSG/방화벽이 풀려 있다고 안심한다

`internal`이면 같은 Environment 안에서만 routing 가능합니다. Environment가 VNet integration 없이 만들어졌다면 internal endpoint도 같은 ACA region 안의 다른 Container App만 호출할 수 있습니다. on-prem이나 다른 VNet에서 부르려면 VNet-integrated Environment가 필요합니다.

### 실수 3. canary 시작할 때 v2의 min-replicas를 0으로 둔다

Canary로 10%만 흘려도 v2가 처음 호출될 때 cold start가 발생합니다. canary 기간 중에는 v2도 `--min-replicas 1` 이상으로 두는 것이 user-facing latency 측정에 깔끔합니다.

### 실수 4. weight를 조정한 직후 바로 metric을 본다

ingress의 weight 변경은 즉시 반영되지만, Log Analytics의 query 결과는 1-3분 지연이 있습니다. 5-10분 정도는 두고 봐야 의미 있는 비교가 됩니다.

### 실수 5. label 기반 routing(header, cookie)을 기대한다

ACA의 traffic split은 **percentage 기반**입니다. "특정 user-agent만 v2로" 같은 routing은 불가능합니다. 그게 필요하면 application gateway나 front door를 앞에 둬야 합니다.

## 실무에서는 이렇게 생각한다

production canary 운영 룰:

- **시작 weight는 1-10%** — 너무 작으면 통계 의미 없음, 너무 크면 blast radius 큼
- **각 단계 사이에 최소 10-15분 대기** — Log 지연과 traffic 다양성 확보
- **rollback trigger를 미리 합의** — 5xx > 1%, p95 latency 20% 증가 등
- **두 Revision 모두 `min-replicas` 같게** — cold start 차이로 인한 측정 왜곡 방지
- **Revision suffix를 의미 있게** — `v1`, `v2`보다는 `v2-fix-bug-1234` 같은 식

## 체크리스트

- [ ] external/internal/disabled 세 ingress 모드의 차이를 안다
- [ ] Single mode와 Multiple mode가 canary 가능 여부에 미치는 영향을 안다
- [ ] CLI로 traffic weight를 조정하는 명령을 외운다
- [ ] Rollback이 weight 조정으로 수 초 안에 끝남을 확인했다
- [ ] header/cookie 기반 routing은 ACA traffic split으로 안 됨을 안다

## 정리

- ACA Ingress는 TLS, 외부/내부 노출, Revision routing을 모두 책임집니다.
- `external` / `internal` / `disabled` 세 모드 중 워크로드에 맞는 것을 고르는 게 첫 결정입니다.
- Production은 Multiple revision mode로 만들어야 canary와 instant rollback이 가능합니다.
- Traffic split은 percentage 기반 — header/cookie routing은 안 됩니다.
- Rollback은 새 deploy가 아니라 weight 조정 — 수 초 안에 끝납니다.

## 다음 글

다음 글에서는 KEDA 기반 scaling을 다룹니다. HTTP 트래픽뿐 아니라 queue length, CPU, 사용자 정의 metric으로 0-to-N 스케일링을 구성하는 법을 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- **Ingress와 트래픽 분할 — Revision 기반 배포 전략 (현재 글)**
- 스케일링 — KEDA scaler와 0-to-N (예정)
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Ingress in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Configure ingress for your app in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-how-to)
- [Traffic splitting in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
