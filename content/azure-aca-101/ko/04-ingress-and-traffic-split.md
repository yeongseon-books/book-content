---
title: Ingress와 트래픽 분할 — Revision 기반 배포 전략
series: azure-aca-101
episode: 4
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

# Ingress와 트래픽 분할 — Revision 기반 배포 전략

> Azure Container Apps 101 시리즈 (4/7)

이번 글은 Ingress와 Revision 기반 트래픽 제어를 연결합니다. 프록시 내부 구현을 추측하는 대신, 공개 진입점을 여는 설정이 무엇인지, 이전 Revision을 살려 두는 조건이 무엇인지, revision weight가 왜 배포 안전장치가 되는지를 운영 관점에서 정리합니다.

---

<!-- ebook-only:start -->
## 이 장의 위치

이 글은 시리즈 7편 중 4번째 장입니다.
앞 장에서는 **첫 앱 배포하기 — Python/FastAPI**을 다뤘습니다.
이 장을 마치면 다음 장에서 **스케일링 — KEDA scaler와 0-to-N**으로 이어집니다.
<!-- ebook-only:end -->

## 요청 경로

ACA의 관리형 Ingress 계층이 앞문 역할을 맡고 활성 Revision으로 트래픽을 보냅니다.

![Ingress가 요청을 활성 Revision으로 보내는 경로](../../../assets/azure-aca-101/04/04-01-the-request-path.ko.png)
---

## Ingress가 맡는 일

- TLS 종료
- 외부 또는 내부 노출
- Revision 간 트래픽 분배

---

## Single과 Multiple

Single은 새 Revision이 준비되면 이전 Revision을 비활성화합니다.
Multiple은 둘 이상의 Revision을 동시에 살려 둡니다.

---

## traffic 명령

```bash
az containerapp revision set-mode   --name $APP_NAME   --resource-group $RG   --mode multiple

az containerapp ingress traffic set   --name $APP_NAME   --resource-group $RG   --revision-weight myapp--rev-a=80 myapp--rev-b=20
```

---

## Canary와 Blue-Green

- 작은 비율부터 시작
- 로그와 지연시간 비교
- 필요 시 이전 Revision으로 트래픽 이동

---

## 운영에서 기억할 점

- Single 모드는 단순성을 우선할 때 적합합니다.
- Multiple 모드는 점진 배포와 즉시 되돌리기가 필요할 때 빛납니다.
- 트래픽 비율을 움직일 때는 숫자만 바꾸지 말고 Revision별 로그, 지연시간, 오류율을 함께 봐야 합니다.

---

<!-- blog-only:start -->
다음 글: [스케일링 — KEDA scaler와 0-to-N](./05-scaling-with-keda.md)
<!-- blog-only:end -->

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
