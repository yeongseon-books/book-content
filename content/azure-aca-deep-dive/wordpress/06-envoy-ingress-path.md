---
title: "바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로"
series: azure-aca-deep-dive
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps심화
- Envoy
- Ingress
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 심화 6편: Envoy Ingress 경로. 첫 HTTPS 요청이 ACA managed ingress, Envoy형 라우팅, ready replica를 거쳐 사용자 컨테이너에 닿는 경로를 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로

이 글은 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 마지막 글입니다.

Azure Container Apps의 Ingress 설명은 짧고 명확합니다. Ingress를 켜면 FQDN이 생기고, HTTPS를 받을 수 있고, 필요하면 Revision 사이에 트래픽을 나눌 수 있습니다. 하지만 첫 요청이 실제로 어디를 어떻게 지나가는지까지 보여 주지는 않습니다. ACA Ingress를 가장 정확하게 설명하는 방법은 두 층으로 나누는 것입니다. 문서화된 부분은 ACA-managed ingress surface이고, 그 뒤의 런타임 라우팅은 Envoy형 proxy behavior와 Kubernetes형 service pattern으로 제한적으로 추론하는 것입니다. Ingress 문제를 앱부터 의심하는 습관은 ACA에서 특히 비효율적입니다. 사용자 컨테이너 코드에 도달하기 전에 이미 public edge, TLS termination, forwarded header, revision selection, ready replica 선택 같은 여러 층을 통과하기 때문입니다. scale-to-zero 상태에서 들어온 첫 요청은 routing decision만 하는 것이 아니라 replica creation, app startup, probe 통과, sidecar startup을 함께 기다릴 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Ingress 장애 진단 코드를 요청할 때 경로 계층을 명시하지 않으면, 앱 코드만 확인하고 TLS 종료 계층이나 Revision 라우팅 계층 문제를 놓치는 코드가 생성되기 때문입니다.

> Envoy Ingress 경로의 핵심은 첫 요청이 public edge → TLS 종료 → Envoy 가중치 라우팅 → ready replica → 사용자 컨테이너 순서로 통과함을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA의 public ingress 표면과 숨은 라우팅 계층은 어떻게 구분해 이해해야 할까요?
- TLS는 어디서 종료되고, 앱은 원래 요청 정보를 어떤 header로 복구할까요?
- Revision traffic split은 요청 경로의 어느 지점에서 실제가 될까요?
- scale-to-zero 상태의 첫 요청은 왜 특히 느릴까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Envoy Ingress 경로를 이해하면 AI에게 "ACA Ingress 5xx 장애 진단 시 public edge 응답 코드, Revision active 상태, ready replica 수, sidecar 부팅 상태를 순서대로 확인하는 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 앱이 간헐적으로 502를 내는데 원인은?"
→ 앱 코드 예외 처리 확인
→ Ingress 경로 계층 구분 없음
→ scale-to-zero cold start 미고려
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA 간헐적 502 장애를 Ingress 경로 계층별로 진단해줘.
    1) public edge 응답: curl -v FQDN으로 헤더 확인
    2) Revision 라우팅: az revision list로 active 상태 확인
    3) ready replica: Log Analytics에서 replica=0 구간 확인
    4) cold start: scale-to-zero 앱이면 min-replicas 1로 조정
    5) sidecar 부팅: Dapr 켜진 앱이면 daprd 로그 KQL 확인"
→ 계층별 체계적 진단
→ cold start와 sidecar 부팅을 별개 원인으로 구분
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Ingress 5xx를 항상 앱 코드 버그로 가정 | Ingress 계층 자체 문제일 수 있음 | curl -v FQDN으로 edge 응답부터 확인 |
| forwarded header 없이 원본 IP 확인 시도 | TLS 종료 후 원본 IP가 사라짐 | X-Forwarded-For, X-Forwarded-Proto 헤더 사용 |
| scale-to-zero cold start를 앱 버그로 진단 | replica 0→1 대기 + startup + probe 시간 | Log Analytics에서 replica=0 구간 확인 |
| Revision traffic weight와 Ingress 응답 혼동 | 일부 요청이 구 버전 Revision으로 라우팅될 수 있음 | Revision weight 설정과 active Revision 함께 확인 |
| sidecar startup을 앱 startup과 동일하게 봄 | sidecar도 별도 startup 시간 존재 | Dapr 켜진 앱의 cold start는 sidecar 부팅 포함 |

## AI 협업 팁

Envoy Ingress 경로 관련 효과적인 AI 프롬프트 패턴:

1. **Ingress 장애 진단 요청**: "ACA 502 장애를 public edge → Revision → replica → sidecar 계층별로 진단하는 명령 시퀀스 작성해줘"
2. **cold start 분석 요청**: "Log Analytics에서 ACA 앱의 scale-to-zero cold start 구간을 식별하는 KQL 쿼리 작성해줘"
3. **forwarded header 처리 요청**: "FastAPI에서 ACA managed ingress의 X-Forwarded-For, X-Forwarded-Proto 헤더로 원본 IP와 프로토콜을 복구하는 코드 작성해줘"

예시 프롬프트:
> "ACA Ingress 경로 장애 진단 플레이북을 작성해줘. 1) curl -v FQDN으로 edge 응답 확인 2) az revision list로 active/ready 상태 3) Log Analytics replica 수 0 구간 KQL 4) daprd sidecar 로그 KQL. scale-to-zero cold start와 sidecar startup이 502 원인일 수 있음을 플레이북에 명시."

## 운영 체크리스트

- [ ] Ingress 장애 진단 시 public edge부터 계층별로 확인하는가?
- [ ] forwarded header로 원본 IP를 복구하는가?
- [ ] scale-to-zero 앱의 cold start를 모니터링하는가?
- [ ] Dapr 켜진 앱의 cold start가 sidecar 부팅을 포함함을 이해했는가?
- [ ] 이 시리즈에서 배운 계층 모델로 ACA를 진단할 준비가 됐는가?

## 처음 질문으로 돌아가기

Envoy Ingress 경로를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 요청 경로 계층과 cold start 원인을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Ingress 장애 진단 코드의 완성도는 크게 다릅니다.

## 정리

Envoy Ingress 경로는 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 마지막 단계입니다. ACA 아키텍처, Environment 격리, Revision 불변성, KEDA 스케일링, Dapr 사이드카가 Ingress 경로에서 모두 만납니다. public edge → TLS 종료 → Envoy형 가중치 라우팅 → ready replica → 사용자 컨테이너 경로를 이해하면 ACA의 모든 계층을 한 그림으로 연결할 수 있습니다.

## 참고 자료

- [Ingress in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/ingress-overview)
- [HTTP headers in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/ingress-how-to)
- [Envoy proxy](https://www.envoyproxy.io/docs/envoy/latest/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/06-envoy-ingress-path)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처
- 바이브코딩을 위한 Azure Container Apps 심화 (2/6): Environment 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA
- 바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부
- **바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps심화, Envoy, AI코딩
