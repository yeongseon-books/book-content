---
title: Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기
series: azure-aca-101
episode: 1
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

# Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기

> Azure Container Apps 101 시리즈 (1/7)

컨테이너는 만들 수 있습니다.
로컬에서도 잘 뜹니다.
문제는 그 다음입니다.
어디에 올릴지.
HTTPS는 누가 붙일지.
스케일링은 누가 할지.
로그와 추적은 어디서 볼지 정해야 합니다.
Azure Container Apps는 그 구간을 겨냥합니다.
컨테이너는 직접 가져가되 클러스터 운영은 직접 맡지 않는 모델입니다.

---

<!-- ebook-only:start -->
## 이 장의 위치

이 글은 시리즈 7편 중 1번째 장입니다.
이 장을 마치면 다음 장에서 **Environment·Container App·Revision — 세 단어로 보는 ACA**으로 이어집니다.
<!-- ebook-only:end -->

## 전체 그림 — Azure Container Apps 환경 한 장면

이 그림이 시리즈 전체의 지도입니다.
뒤의 화들은 각 박스를 하나씩 확대합니다.
클라이언트와 Ingress는 4화.
Environment·Container App·Revision은 2화.
첫 배포는 3화.
KEDA는 5화.
Dapr는 6화.
관측성은 7화입니다.

![ACA Environment 안의 ingress와 앱 배치 구조](../../../assets/azure-aca-101/01/01-01-the-big-picture-one-aca-environment-at-a.ko.png)
---

## 한 문장 정의

ACA는 관리형 서버리스 컨테이너 플랫폼입니다.
Microsoft가 관리하는 Kubernetes 기반 위에 KEDA 기반 스케일링, 선택적 Dapr 통합, 관리형 Ingress를 얹어 제공하지만 사용자는 클러스터 자체를 직접 보거나 제어하지 않습니다.

- 컨테이너 이미지가 배포 단위입니다.
- 유휴 시에는 줄고 조건이 맞으면 0까지 내려갈 수 있습니다.
- Ingress와 Revision과 관측성이 제품 안에 묶여 있습니다.

---

## 왜 ACA를 고르나

- HTTP API와 워커를 같은 플랫폼에서 운영
- 트래픽이 없을 때 비용 절감
- Revision 기반 Canary와 Blue-Green
- 필요할 때만 Dapr 사용

---

## 요청 하나의 흐름

가장 단순한 HTTP 요청 경로를 보면 플랫폼의 책임이 선명해집니다.

- 이미지 만들기
- 포트와 헬스 경로 맞추기
- 스케일 규칙 정하기
- 트래픽 전략 정하기
- 로그와 추적 남기기

![클라이언트 요청이 Revision에 닿는 흐름](../../../assets/azure-aca-101/01/01-02-the-path-of-one-request.ko.png)
---

## 어떤 시나리오에 맞나

- FastAPI 기반 API
- 트래픽이 들쭉날쭉한 워커
- 마이크로서비스 조합
- Canary와 Blue-Green이 필요한 서비스

---

## 개요에서 남겨야 할 감각

- Environment는 공용 경계이고, App와 Revision은 실제 운영 단위입니다.
- ACA가 클러스터를 숨겨 준다고 해서 Ingress, 스케일링, 롤아웃, 관측성 결정을 대신 내려 주는 것은 아닙니다.
- 이 경계만 분명하면 뒤의 글들도 훨씬 쉽게 읽힙니다.

---

<!-- blog-only:start -->
다음 글: [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- **Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 (현재 글)**
- Environment·Container App·Revision — 세 단어로 보는 ACA (예정)
- 첫 앱 배포하기 — Python/FastAPI (예정)
- Ingress와 트래픽 분할 — Revision 기반 배포 전략 (예정)
- 스케일링 — KEDA scaler와 0-to-N (예정)
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Ingress in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
