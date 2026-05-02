---
title: 스케일링 — KEDA scaler와 0-to-N
series: azure-aca-101
episode: 5
language: ko
status: publish-ready
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

# 스케일링 — KEDA scaler와 0-to-N

> Azure Container Apps 101 시리즈 (5/7)

이번 글은 KEDA 기반 스케일링을 다룹니다.
내장 HTTP/TCP 규칙.
그리고 Service Bus, CPU, memory 같은 custom KEDA 규칙을 구분해서 봅니다.

---

## 스케일 경로 한 장

스케일 판단은 선언적입니다.
신호와 replica 범위를 정하면 플랫폼이 움직입니다.

![스케일 신호가 replica 수를 바꾸는 흐름](../../../assets/azure-aca-101/05/05-01-the-scaling-path.ko.png)
---

## 규칙 세 부류

- **HTTP 스케일 규칙** — ingress가 켜진 HTTP 앱에서 쓰는 내장 규칙이며, 동시 요청 수를 기준으로 스케일합니다.
- **TCP 스케일 규칙** — TCP 앱에서 쓰는 내장 규칙이며, 동시 연결 수를 기준으로 스케일합니다.
- **Custom KEDA 규칙** — Service Bus, Event Hubs, Kafka, Redis 같은 이벤트 소스와 CPU, memory 같은 리소스 기반 scaler를 모두 포함합니다.

---

## scale-to-zero

HTTP와 TCP 규칙은 0까지 내려갈 수 있습니다.
많은 custom 이벤트 기반 KEDA 규칙도 0까지 내려갈 수 있습니다.
CPU와 memory는 custom 규칙 범주에 속하지만, 문서 기준 scale-to-zero 대상은 아닙니다.

---

## HTTP 예시

```bash
az containerapp create   --name $APP_NAME   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --ingress external   --target-port 8000   --min-replicas 0   --max-replicas 5   --scale-rule-name http-rule   --scale-rule-type http   --scale-rule-http-concurrency 100
```

---

## Service Bus 예시

```bash
az containerapp create   --name queue-worker   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --min-replicas 0   --max-replicas 10   --secrets "sb-connection=<SERVICE_BUS_CONNECTION_STRING>"   --scale-rule-name servicebus-rule   --scale-rule-type azure-servicebus   --scale-rule-metadata "queueName=orders" "namespace=mybus.servicebus.windows.net" "messageCount=5"   --scale-rule-auth "connection=sb-connection"
```

---

## 운영에서 기억할 점

- 먼저 HTTP, TCP, custom 중 어떤 트리거 계열을 쓰는지부터 정해야 합니다.
- 최소 replica 수는 비용 값이면서 동시에 가용성과 지연시간 값입니다.
- 스케일링은 큐 길이, 요청 특성, 콜드 스타트 허용 범위와 함께 읽어야 제대로 판단할 수 있습니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — Revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- **스케일링 — KEDA scaler와 0-to-N (현재 글)**
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Scaling in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [KEDA scalers documentation](https://keda.sh/docs/scalers/)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
