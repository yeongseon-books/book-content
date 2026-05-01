---
title: Environment·Container App·Revision — 세 단어로 보는 ACA
series: azure-aca-101
episode: 2
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

# Environment·Container App·Revision — 세 단어로 보는 ACA

> Azure Container Apps 101 시리즈 (2/7)

1화에서 전체 그림을 잡았다면 이번 글은 가운데 구조를 분해하는 시간입니다.
Environment와 Container App과 Revision을 운영 단위로 읽어야 ACA가 쉬워집니다.

---

## 계층 먼저 보기

Environment는 경계입니다.
Container App은 논리 서비스입니다.
Revision은 이미지와 설정의 불변 스냅샷입니다.

![Environment와 Container App와 Revision의 계층 관계](../../../assets/azure-aca-101/02/02-01-start-with-the-hierarchy.ko.png)
---

## Environment

- 같은 VNet 경계
- 같은 로그 대상
- 같은 Dapr 공통 구성
- 관련 앱 묶음의 경계

---

## Container App

Container App은 시간을 따라 여러 Revision을 가질 수 있습니다.

- 이미지
- 환경변수
- 비밀 값
- Ingress
- 리소스
- 스케일 규칙

---

## Revision

- 이미지와 설정의 불변 스냅샷
- 트래픽 대상이 될 수 있음
- 자동 롤백과 같은 뜻은 아님

---

## Single과 Multiple 모드

Single은 기본값입니다.
Multiple은 Canary와 Blue-Green을 가능하게 합니다.

---

## 어떤 변경이 새 Revision을 만드는가

- 이미지 변경
- CPU/메모리 변경
- 스케일 규칙 변경

---

## 이 모델에서 남겨야 할 감각

- Environment는 공용 플랫폼 경계입니다.
- App는 오래 유지되는 서비스 정체성입니다.
- Revision은 배포, 되돌리기, 문제 분석 때 실제로 관찰하는 실행 스냅샷입니다.

---

<!-- blog-only:start -->
다음 글: [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- **Environment·Container App·Revision — 세 단어로 보는 ACA (현재 글)**
- 첫 앱 배포하기 — Python/FastAPI (예정)
- Ingress와 트래픽 분할 — Revision 기반 배포 전략 (예정)
- 스케일링 — KEDA scaler와 0-to-N (예정)
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

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

Tags: Azure, Container Apps, Serverless, Containers
