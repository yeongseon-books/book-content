---
title: Ingress와 트래픽 분할 — revision 기반 배포 전략
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
last_reviewed: '2026-05-12'
seo_description: Ingress는 ACA의 정문이고, 트래픽 가중치는 엘리베이터 배차 비율로 이해하면 쉽습니다.
---

# Ingress와 트래픽 분할 — revision 기반 배포 전략

Ingress와 트래픽 분할은 ACA에서 가장 중요한 운영 레버 두 개입니다. 설정 한 줄만 바뀌어도 외부 노출 방식과 배포 안전성이 함께 달라지므로, 둘은 따로보다 함께 볼 때 더 잘 이해됩니다.

이 글은 Azure Container Apps 101 시리즈의 4번째 글입니다. 여기서는 ingress 설계와 revision 기반 배포 전략을 하나의 흐름으로 연결해 보겠습니다.

---

## 이 글에서 다룰 문제

- ACA의 관리형 Ingress는 무엇을 책임지고(TLS, external/internal 노출, Revision 라우팅), 무엇은 책임지지 않을까요?
- `external`, `internal`, `disabled` ingress mode의 차이는 정확히 무엇일까요?
- Single mode와 Multiple mode는 트래픽 분배 동작을 어떻게 바꿀까요?
- Revision 가중치로 canary와 blue-green을 구현하고, 문제 시 즉시 rollback하려면 어떻게 할까요?

## 왜 이 글이 중요한가

ACA의 가장 강력한 프로덕션 기능 중 하나가 revision 기반 traffic split입니다. 하지만 이 기능을 제대로 쓰려면 먼저 ingress 설정이 맞아 있어야 합니다.

자주 보는 사고는 아래와 같습니다.

- "external ingress를 켰는데 인터넷에서 접속이 안 됩니다" → `target-port`가 맞지 않았습니다
- "canary로 10%만 보내려 했는데 100%가 새 버전으로 갔습니다" → Single mode였습니다
- "rollback은 재배포처럼 몇 분 걸린다고 들었습니다" → 실제로는 가중치 변경이고 수 초 안에 끝납니다
- "internal ingress로 만들었는데 외부에서 접근됩니다" → ingress mode를 잘못 이해했습니다

이 글은 ingress와 traffic split을 하나의 흐름으로 묶어, 이런 사고의 뿌리를 끊어 줍니다.

## 멘탈 모델

> Ingress는 ACA의 "정문"이고, 트래픽 가중치는 "엘리베이터 배차 비율"입니다.

정문(Ingress)은 외부 방문자를 받을지(`external`), 같은 건물 사람만 받을지(`internal`), 아예 닫아 둘지(`disabled`)를 결정합니다. 정문을 통과한 뒤에는 엘리베이터(traffic split rule)가 설정된 비율에 따라 각 방문자를 어느 사무실(Revision)로 보낼지 결정합니다.

이 두 단계는 서로 분리돼 있으므로, "외부 노출"과 "버전 분배"를 독립적으로 운영할 수 있습니다.

## 요청 경로

ACA의 관리형 Ingress 레이어는 정문 역할을 하고, 그 뒤에서 가중치에 따라 active Revision으로 트래픽을 보냅니다.

![Ingress routing requests to active Revisions](../../../assets/azure-aca-101/04/04-01-the-request-path.en.png)

*Ingress routing requests to active Revisions*

핵심 단계는 다음과 같습니다.

1. 클라이언트가 `https://<app>.<env-id>.<region>.azurecontainerapps.io`로 요청합니다
2. ACA의 관리형 envoy proxy가 TLS를 종료합니다
3. 해당 Container App의 Revision 가중치 테이블을 참조합니다
4. 비율에 따라 하나의 Revision의 하나의 replica로 트래픽을 보냅니다
5. Replica가 응답하고, 로그는 Log Analytics로 흘러갑니다

## 핵심 개념 1 — 세 가지 ingress mode

| Mode | 노출 범위 | URL | 잘 맞는 용도 |
|---|---|---|---|
| `external` | 퍼블릭 인터넷 | `https://<app>.<env-id>.<region>.azurecontainerapps.io` | 공개 API, 웹 프런트엔드 |
| `internal` | 같은 Environment 내부만 | `https://<app>.internal.<env-id>.<region>.azurecontainerapps.io` | 마이크로서비스 간 호출 |
| `disabled` | 노출되지 않음 | (none) | worker, 배치 작업, 메시지 소비자 |

CLI 예시는 다음과 같습니다.

```bash
az containerapp ingress enable \
  --name myapi --resource-group $RG \
  --type external --target-port 8000 --transport auto
```

`--transport`에는 `auto`(권장), `http`, `http2`, `tcp` 중 하나를 씁니다.

## 핵심 개념 2 — Single vs Multiple revision mode

| 항목 | Single mode | Multiple mode |
|---|---|---|
| Active Revision 수 | 항상 1 | N개 동시 active |
| 새 Revision 배포 시 | 트래픽 100%가 즉시 넘어감 | 가중치는 설정값 유지 |
| Canary | 불가능 | 가능 |
| Blue-Green | 불가능 | 가능 |
| 잘 맞는 용도 | 단순한 서비스, dev | 프로덕션 API |

기본값은 Single입니다. 프로덕션에서는 Multiple을 써야 합니다.

```bash
az containerapp revision set-mode \
  --name $APP_NAME --resource-group $RG \
  --mode multiple
```

## Before / After

**Before — Single mode에서 canary를 시도하는 경우**

```bash
# Single mode is the default
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2
# → New Revision is created and 100% of traffic moves to v2 instantly
# The exact opposite of "send only some users."
```

**After — Multiple mode + 가중치 분할**

```bash
# 1. Switch to Multiple mode
az containerapp revision set-mode --name myapi --resource-group $RG --mode multiple

# 2. Deploy the new Revision (traffic still 0%)
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# 3. Adjust weights gradually
az containerapp ingress traffic set --name myapi --resource-group $RG \
  --revision-weight myapi--v1=90 myapi--v2=10
```

핵심 차이는 트래픽을 정말 의도한 비율로 흘릴 수 있느냐입니다.

## 실습 — 90/10 canary와 즉시 rollback

### Step 1. Multiple mode로 전환하기

```bash
RG=rg-aca-demo
APP=myapi

az containerapp revision set-mode --name $APP --resource-group $RG --mode multiple
```

### Step 2. v1 배포하기(하나의 Revision이 100%)

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v1 --revision-suffix v1
```

### Step 3. v2를 트래픽 0%로 배포하기

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# Pin v1=100, v2=0 first
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

### Step 4. 90/10 canary 시작하기

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=90 $APP--v2=10
```

이제 Log Analytics에서 `RevisionName` 기준으로 에러율과 지연 시간을 비교합니다.

### Step 5a. 건강하면 50/50 → 0/100으로 진행하기

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=50 $APP--v2=50
# After more monitoring
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=0 $APP--v2=100
```

### Step 5b. 문제가 보이면 즉시 rollback하기

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

v2 트래픽은 수 초 안에 0이 됩니다.

## 자주 하는 실수

### 실수 1. `target-port`를 ingress 포트로 착각하는 것

`--target-port`는 컨테이너가 듣는 포트입니다. 외부에 노출되는 포트는 항상 443(HTTPS)이고, 매핑은 ACA가 처리합니다.

### 실수 2. `internal`이면 NSG 없이도 무조건 안전하다고 생각하는 것

`internal`은 같은 Environment 안에서만 라우팅됩니다. Environment를 VNet 통합 없이 만들었다면, internal 엔드포인트는 같은 ACA 리전 안의 다른 Container App만 호출할 수 있습니다. 온프레미스나 다른 VNet에서 호출하려면 VNet 통합 Environment가 필요합니다.

### 실수 3. canary를 시작하면서 v2의 `min-replicas`를 0으로 두는 것

트래픽이 10%뿐이어도 v2의 첫 요청은 cold start 비용을 지불합니다. canary 동안에는 v2의 `--min-replicas 1`로 두어야 지연 시간 측정이 깔끔합니다.

### 실수 4. 가중치를 바꾸자마자 메트릭을 보는 것

Ingress 가중치 변경은 즉시 반영되지만, Log Analytics 쿼리는 1-3분 정도 지연될 수 있습니다. 결론을 내리기 전 5-10분은 기다리는 편이 안전합니다.

### 실수 5. header나 cookie 기반 라우팅을 기대하는 것

ACA traffic split은 비율 기반입니다. "이 user-agent만 v2로 보내기" 같은 라우팅은 지원하지 않습니다. 그런 요구가 있으면 앞단에 Application Gateway나 Front Door를 둬야 합니다.

## 실무에서는 이렇게 생각한다

프로덕션 canary 플레이북은 대개 아래처럼 갑니다.

- 시작 가중치는 1-10% — 너무 작으면 통계적 신호가 약하고, 너무 크면 blast radius가 커집니다
- 단계 사이에 최소 10-15분 대기 — 로그 지연과 트래픽 다양성을 흡수해야 합니다
- rollback 기준을 미리 합의 — 예: 5xx > 1%, p95 latency +20%
- 두 Revision의 `min-replicas`를 같게 유지 — cold start 편향을 피해야 합니다
- 의미 있는 Revision suffix 사용 — 단순 `v2`보다 `v2-fix-bug-1234`가 낫습니다

## 체크리스트

- [ ] external/internal/disabled ingress mode 차이를 설명할 수 있습니다
- [ ] Single과 Multiple mode 차이가 canary 가능 여부를 어떻게 바꾸는지 알고 있습니다
- [ ] 트래픽 가중치를 설정하는 CLI 명령을 외우고 있습니다
- [ ] rollback이 가중치 변경으로 수 초 안에 끝난다는 점을 확인했습니다
- [ ] header/cookie 기반 라우팅은 ACA traffic split의 범위가 아니라는 점을 알고 있습니다

## 연습 문제

1. Step 1-5a를 따라 v1 → v2 100% 전환을 90/10 → 50/50 → 0/100 순서로 진행해 보세요. 각 단계에서 Log Analytics로 `RevisionName`별 요청 수를 조회하고, 의도한 비율과 실제 비율을 비교해 보세요.
2. v2에 의도적으로 500 에러를 넣고 90/10 canary를 시작한 뒤 rollback 명령을 실행해 보세요. v2 트래픽이 0이 되기까지 걸리는 시간을 측정해 보세요.

## 정리

- ACA Ingress는 TLS, external/internal 노출, Revision 라우팅을 맡습니다.
- 첫 번째 결정은 `external` / `internal` / `disabled` 중 무엇을 고를지입니다.
- 프로덕션에서 canary와 즉시 rollback을 하려면 Multiple revision mode가 필요합니다.
- Traffic split은 비율 기반이며, header/cookie 기반 라우팅은 지원하지 않습니다.
- rollback은 새 배포가 아니라 가중치 변경이므로 수 초 안에 끝납니다.

다음 글에서는 KEDA 기반 스케일링을 다룹니다. HTTP 트래픽뿐 아니라 큐 길이, CPU, 사용자 정의 메트릭까지 신호로 삼아 0-to-N 스케일링을 구성해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [첫 배포하기 — Python/FastAPI](./03-first-deploy.md)
- <strong>Ingress와 트래픽 분할 — revision 기반 배포 전략 (현재 글)</strong>
- Scaling — KEDA scalers and zero-to-N (예정)
- Dapr integration — what you get from a sidecar (예정)
- Monitoring and ops — Log Analytics and Application Insights (예정)

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
