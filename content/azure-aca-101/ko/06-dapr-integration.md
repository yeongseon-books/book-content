---
title: Dapr 통합 — 사이드카로 얻는 것
series: azure-aca-101
episode: 6
language: ko
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Serverless
- Containers
last_reviewed: '2026-04-29'
---

# Dapr 통합 — 사이드카로 얻는 것

> Azure Container Apps 101 시리즈 (6/7)

이번 글은 Dapr 사이드카가 어디에 붙고 무엇을 단순하게 만드는지 설명합니다. Service invocation, Pub/Sub, state store, secret store가 반복해서 등장하지만, 실무에서 더 중요한 포인트는 범위입니다. 앱 수준 설정과 Environment 수준 컴포넌트 구성이 어디서 갈리는지 알아야 Dapr를 안전하게 붙일 수 있습니다.

---

## Dapr가 붙는 위치

앱 옆에 사이드카가 붙고.
Environment 수준 컴포넌트와 외부 서비스를 중개합니다.

![앱 옆 Dapr 사이드카와 외부 서비스 연결 구조](../../../assets/azure-aca-101/06/06-01-where-dapr-sits.ko.png)
---

## enable 명령

```bash
az containerapp create   --name api-app   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --ingress external   --target-port 8000   --enable-dapr true   --dapr-app-id api-app   --dapr-app-port 8000

az containerapp dapr enable   --name api-app   --resource-group $RG   --dapr-app-id api-app   --dapr-app-port 8000
```

---

## App 수준과 Environment 수준

- App 수준 — enable 여부, app id, app port
- Environment 수준 — component 정의와 scope

---

## 대표 building blocks

- Service invocation
- Pub/Sub
- State store
- Secret store

---

## component 스케치 — 읽기용 예시, 그대로 적용하는 파일은 아님

```yaml
componentType: pubsub.azure.servicebus.queue
version: v1
metadata:
  - name: namespaceName
    value: mybus.servicebus.windows.net
  - name: queueName
    value: orders
  - name: connectionString
    secretRef: servicebus-connection-string
scopes:
  - publisher-app
  - subscriber-app
```

이 예시는 구조를 읽기 위한 스케치입니다. 실제로 동작하게 하려면 Environment 수준 secret가 먼저 있어야 하고, 인증 방식도 connection string, managed identity 등 어떤 경로를 택할지 함께 정해야 합니다.

---

## 운영에서 기억할 점

- 앱에서 Dapr를 켜는 일과 Environment에 component를 정의하는 일은 다른 결정입니다.
- 인증 연결이 빠진 component YAML은 배포 계획이 아니라 구조 설명에 가깝습니다.
- Dapr가 보일러플레이트를 줄여 주더라도 scope, retry, 실패 처리 정책까지 대신 정해 주지는 않습니다.

---

<!-- blog-only:start -->
다음 글: [모니터링과 운영 — Log Analytics와 Application Insights](./07-monitoring-and-ops.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — Revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- [스케일링 — KEDA scaler와 0-to-N](./05-scaling-with-keda.md)
- **Dapr 통합 — 사이드카로 얻는 것 (현재 글)**
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Configure Dapr on an Existing Container App — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/enable-dapr)
- [Microservice APIs powered by Dapr — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Dapr overview](https://docs.dapr.io/concepts/overview/)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
