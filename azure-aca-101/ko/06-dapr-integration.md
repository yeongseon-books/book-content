<!-- tags: Azure, Container Apps, Serverless, Containers -->
# Dapr 통합 — 사이드카로 얻는 것

> Azure Container Apps 101 시리즈 (6/7)

이번 글은 Dapr 사이드카가 어디에 붙고 무엇을 단순하게 만드는지 설명합니다.
Service invocation.
Pub/Sub.
State store.
Secret store가 중심입니다.

---

## Dapr가 붙는 위치

앱 옆에 사이드카가 붙고.
Environment 수준 컴포넌트와 외부 서비스를 중개합니다.

![Dapr가 붙는 위치](../../assets/azure-aca-101/06/06-01-where-dapr-sits.ko.png)
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

## component 적용 예시

```yaml
componentType: pubsub.azure.servicebus.queue
version: v1
metadata:
  - name: namespaceName
    value: mybus.servicebus.windows.net
scopes:
  - publisher-app
  - subscriber-app
```

---

## 실무 메모

- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.

---

## 자주 하는 오해

- 플랫폼이 관리형이라고 해서 운영 판단이 사라지는 것은 아닙니다.
- 새 Revision 준비 실패를 자동 롤백과 같은 뜻으로 읽으면 안 됩니다.
- scale-to-zero는 모든 규칙이 같은 방식으로 제공하는 기능이 아닙니다.
- Dapr를 켠다고 설계 책임이 사라지는 것은 아닙니다.
- Environment와 App를 같은 뜻으로 쓰면 경계 설계가 흔들립니다.

---

## 운영 체크리스트

- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.
- 비용과 안정성은 대개 replica 바닥값과 트래픽 패턴과 함께 움직입니다.
- 팀 규약으로 배포 절차를 고정하면 운영 리스크가 크게 줄어듭니다.
- 운영 단위를 먼저 명확히 잡으면 ACA가 훨씬 단순하게 보입니다.
- Environment와 App와 Revision을 섞어 부르지 않는 습관이 중요합니다.
- 문제 해결 속도는 구조를 얼마나 정확히 나눠 보느냐에 크게 좌우됩니다.
- 플랫폼이 많은 것을 숨겨 주지만 경계를 이해해야 운영이 쉬워집니다.
- 배포와 스케일링과 관측성은 같은 흐름의 다른 면입니다.
- CLI 명령을 외우는 것보다 어떤 계층을 바꾸는지 이해하는 편이 오래 갑니다.
- 새 Revision을 만드는 변경과 앱 전체 정책을 바꾸는 변경을 구분해야 합니다.
- 로그와 메트릭은 항상 Revision과 함께 읽는 습관이 좋습니다.

---

이 글은 Azure Container Apps 101 시리즈의 한 부분입니다.
앞의 글이 구조를 설명했다면 다음 글은 그 구조 위에서 배포와 운영 판단을 쌓습니다.
7편을 순서대로 읽으면 ACA를 기능 목록이 아니라 운영 모델로 이해하게 됩니다.

- 운영 체크리스트는 배포 직후 다시 보는 편이 좋습니다.

---

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
