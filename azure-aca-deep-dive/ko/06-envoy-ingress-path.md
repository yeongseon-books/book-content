# Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지

> Azure Container Apps Deep Dive 시리즈 (6/6)

Azure Container Apps의 ingress 공개 설명은 짧습니다.

Ingress를 켭니다.
FQDN을 받습니다.
HTTPS 트래픽을 받습니다.
필요하면 Revision 사이에 traffic을 나눕니다.

서비스를 올리는 데는 이 설명으로도 충분합니다.
첫 요청의 경로를 설명하기에는 부족합니다.

이번 마지막 화는 ACA 운영자에게 필요한 해상도로 그 경로를 따라갑니다.

external client -> ACA-managed load balancer -> Envoy ingress -> Service -> Pod

이 경로에서 Envoy는 TLS를 종료하고, route를 매칭하고, Revision weight를 적용하고, 선택된 Revision의 upstream service로 요청을 넘깁니다.

---

## 시작점은 앱이 아니라 전체 경로입니다

Ingress 디버깅에서 가장 흔한 실수는 사용자 컨테이너부터 보는 것입니다.
요청은 그 지점에 도달하기 전에 이미 여러 플랫폼 계층을 지납니다.

![시작점은 앱이 아니라 전체 경로입니다](../../assets/azure-aca-deep-dive/06/06-01-start-with-the-full-path-not-with-the-ap.ko.png)
이 순서를 머릿속에 두면 ingress 사고를 훨씬 빨리 국소화할 수 있습니다.

- 아예 연결이 안 되면 Pod 바깥 문제일 수 있습니다.
- Host, TLS, header 문제는 대개 service 홉 이전입니다.
- Revision 선택은 proxy 계층에서 일어납니다.
- 앱 버그는 경로의 마지막 단계입니다.

---

## Microsoft 문서가 직접 말해 주는 ACA ingress 계약

Ingress overview 문서는 제품 수준 계약을 분명히 적습니다.

HTTP ingress는 다음을 제공합니다.

- TLS termination
- HTTP/1.1과 HTTP/2
- WebSocket과 gRPC
- 80, 443 포트
- 기본 HTTP -> HTTPS redirect
- FQDN
- Revision 간 traffic splitting
- Session affinity

이 목록의 각 항목은 proxy 동작을 암시합니다.
그래서 Envoy가 정확한 런타임 고정점이 됩니다.

---

## Load Balancer는 첫 번째 관리형 edge이지 최종 router가 아닙니다

사용자는 Pod와 직접 통신하지 않습니다.
외부 요청은 먼저 ACA의 관리형 edge 인프라에 닿습니다.

즉 공용 endpoint는 플랫폼 endpoint입니다.
여러분 컨테이너는 그 뒤에 있는 downstream destination 중 하나입니다.

![Load Balancer는 첫 번째 관리형 edge이지 최종 router가 아닙니다](../../assets/azure-aca-deep-dive/06/06-02-the-load-balancer-is-the-first-managed-e.ko.png)
Load Balancer는 요청을 Environment의 ingress plane으로 넣습니다.
그 이후의 HTTP 인지형 라우팅 결정은 Envoy가 맡습니다.

이 분리 덕분에 TLS termination, route matching, weighted traffic policy 같은 기능이 Pod를 직접 노출하지 않고도 가능합니다.

---

## 기본적으로 TLS는 컨테이너가 아니라 ingress에서 끝납니다

Microsoft 문서는 HTTP ingress에서 TLS termination이 ingress point에서 일어난다고 설명합니다.
즉 클라이언트와의 HTTPS 연결은 사용자 컨테이너로 들어가기 전에 종료됩니다.

![기본적으로 TLS는 컨테이너가 아니라 ingress에서 끝납니다](../../assets/azure-aca-deep-dive/06/06-03-tls-ends-at-ingress-not-at-your-containe.ko.png)
운영적으로는 이 사실이 여러 현상을 설명합니다.

- 앱은 원래 TLS 소켓 대신 forwarded header를 보게 됩니다.
- 인증서 처리는 ingress 표면의 책임입니다.
- 앱이 forwarded header를 무시하고 스스로 client-facing TLS 경계를 갖는다고 가정하면 protocol confusion이 생길 수 있습니다.

이건 일반적인 reverse proxy 동작이며, ACA는 원래 요청 맥락을 복원할 수 있도록 forwarded header를 문서화해 둡니다.

---

## Forwarded header는 ingress 계약의 일부입니다

ACA ingress 문서는 다음 같은 header를 설명합니다.

- `X-Forwarded-Proto`
- `X-Forwarded-For`
- 적절한 certificate mode에서의 `X-Forwarded-Client-Cert`

이 header가 존재하는 이유는 앱이 proxy 뒤에 있기 때문입니다.

![Forwarded header는 ingress 계약의 일부입니다](../../assets/azure-aca-deep-dive/06/06-04-forwarded-headers-are-part-of-the-ingres.ko.png)
앱이 absolute URL을 만들거나, scheme에 따라 redirect를 하거나, client IP를 로그로 남긴다면, 이 header는 선택 기능이 아니라 실제 런타임 경로 일부입니다.

---

## 라우팅 단계는 service 홉 이전에 일어납니다

TLS termination과 route matching이 끝나면, Envoy는 upstream destination을 골라야 합니다.
이 선택은 단순할 수도 있고, weighted일 수도 있습니다.

App에 active Revision이 하나뿐이고 split이 없다면 목적지는 단순합니다.
여러 Revision이 active면 Envoy가 선택된 upstream으로 전달하기 전에 traffic weight를 적용합니다.

![라우팅 단계는 service 홉 이전에 일어납니다](../../assets/azure-aca-deep-dive/06/06-05-the-routing-step-happens-before-the-serv.ko.png)
3화가 traffic splitting을 ingress routing data라고 본 이유가 바로 이것입니다.
선택은 여기서 일어나야 합니다.
앱 안쪽이 아닙니다.

---

## Envoy의 weight는 upstream cluster weight입니다

용어를 다시 정확히 고정합니다.

Envoy에서 cluster는 upstream service target입니다.
Kubernetes cluster가 아닙니다.

Pinned Envoy route API source는 routing 계층의 weighted cluster 구성을 정의합니다.
이것이 ACA Revision traffic splitting에 가장 잘 맞는 개념입니다.

![Envoy의 weight는 upstream cluster weight입니다](../../assets/azure-aca-deep-dive/06/06-06-envoy-weight-means-upstream-cluster-weig.ko.png)
즉 ACA의 80/20 split이 "실제로 어디에 사는가"라는 질문에는, Revision upstream 사이를 고르는 ingress routing state라고 답하는 편이 가장 정확합니다.

---

## ACA가 Kubernetes를 숨기기 때문에 Service 홉을 잊기 쉽습니다

사용자 입장에서는 traffic이 그냥 "Revision으로 간다"고 보입니다.
런타임에서는 ingress와 Pod replica 사이에 service성 홉이 여전히 있습니다.

![ACA가 Kubernetes를 숨기기 때문에 Service 홉을 잊기 쉽습니다](../../assets/azure-aca-deep-dive/06/06-07-the-service-hop-is-easy-to-forget-becaus.ko.png)
이 홉이 중요한 이유는, Envoy가 고르는 upstream destination이 보통 단일 Pod가 아니기 때문입니다.
선택된 Revision의 Service endpoint 집합이며, 그 뒤에서 ready replica로 fan-out됩니다.

여기서 scaling과 ingress가 처음으로 실제로 만납니다.
Envoy는 그 Service 뒤에 존재하고 ready한 replica에게만 요청을 보낼 수 있습니다.

---

## Readiness는 ingress 경로의 일부입니다

3화는 새 Revision으로 traffic이 넘어가기 전 readiness가 필요하다고 설명했습니다.
4화는 scale activation과 replica 생성을 설명했습니다.
이번 화에서는 그 두 개념이 한 경로에서 만납니다.

Envoy는 Revision의 존재를 알 수 있습니다.
그래도 요청 경로를 완성하려면 그 Revision Service 뒤에 healthy upstream endpoint가 있어야 합니다.

![Readiness는 ingress 경로의 일부입니다](../../assets/azure-aca-deep-dive/06/06-08-readiness-is-part-of-the-ingress-path-wh.ko.png)
그래서 ingress 디버깅은 revision 상태와 replica readiness를 떼고 볼 수 없습니다.
요청 경로 자체가 원래 그렇게 설계되어 있습니다.

---

## Scale-to-zero Revision의 첫 요청은 특별합니다

ACA는 scale-to-zero를 지원합니다.
즉 첫 요청이 아직 warm replica가 하나도 없는 Revision을 향할 수 있습니다.

정확한 내부 orchestration은 Microsoft 소유의 closed-source 영역입니다.
그래도 운영자가 봐야 할 모양은 분명합니다.

![Scale-to-zero Revision의 첫 요청은 특별합니다](../../assets/azure-aca-deep-dive/06/06-09-the-first-request-to-a-scale-to-zero-rev.ko.png)
이 지점부터 ingress와 autoscaling은 더 이상 별도 주제가 아닙니다.
첫 요청 자체가 scale path를 깨우고, 그 결과가 ready upstream으로 돌아와야 실제 응답이 나갑니다.

---

## 플랫폼이 건강해도 첫 요청이 느릴 수 있는 이유

Revision이 0에 있었다면, 첫 요청은 여러 숨은 단계를 함께 지불합니다.

- activation decision
- replica creation
- 필요 시 image start path
- app startup
- probe success
- Dapr가 켜져 있다면 sidecar startup

![플랫폼이 건강해도 첫 요청이 느릴 수 있는 이유](../../assets/azure-aca-deep-dive/06/06-10-why-the-first-request-can-feel-slower-ev.ko.png)
이 지연은 앱만의 문제가 아닙니다.
Ingress에서 readiness까지의 전체 경로가 사용자 눈앞 한 순간에 압축되어 나타난 것입니다.

---

## Dapr가 켜져 있으면 ingress 뒤의 런타임 참여자가 하나 더 늘어납니다

Dapr가 enable된 Pod라면, 최종적으로 요청을 받는 Pod 안에는 사용자 컨테이너와 `daprd`가 함께 있을 수 있습니다.

Ingress 경로 자체는 여전히 Pod와 사용자 컨테이너 endpoint에서 끝납니다.
그러나 그 직후 동작은 곧바로 sidecar를 호출할 수 있습니다.

![Dapr가 켜져 있으면 ingress 뒤의 런타임 참여자가 하나 더 늘어납니다](../../assets/azure-aca-deep-dive/06/06-11-dapr-adds-another-runtime-participant-be.ko.png)
즉 최종 사용자 요청 하나가 ingress routing, revision readiness, pod startup, sidecar 동작까지 한 번에 걸칠 수 있습니다.

---

## Session affinity도 ingress 계층의 기능입니다

ACA 문서는 sticky session을 ingress 기능으로 설명합니다.
이 사실도 ingress가 단순 coarse routing 이상을 맡고 있다는 단서입니다.

Session affinity가 켜져 있으면 Envoy류 ingress 동작이 같은 client의 요청을 일관되게 같은 방향으로 묶으려 합니다.
이 결정 역시 앱에 도달하기 전에 일어납니다.

이번 시리즈에서 중요한 것은 sticky session 세부 구현 전부가 아닙니다.
Revision과 replica 선택이 여전히 proxy concern이라는 사실입니다.

---

## Internal ingress도 공용 edge만 없을 뿐 큰 모양은 같습니다

Internal-only app에서는 인터넷 쪽 edge가 사라집니다.
그래도 서비스는 Environment 안의 ingress와 service-routing 기계 뒤에 놓입니다.

![Internal ingress도 공용 edge만 없을 뿐 큰 모양은 같습니다](../../assets/azure-aca-deep-dive/06/06-12-internal-ingress-follows-the-same-broad.ko.png)
Edge 쪽 transport는 달라집니다.
그러나 proxy-routing과 service-upstream 논리는 크게 다르지 않습니다.

---

## 실무용 ingress 디버깅 사다리

요청이 실패했을 때는 경로 순서대로 확인하는 편이 빠릅니다.

1. Public FQDN을 resolve하고 reach할 수 있는가
2. Ingress가 기대한 external / internal posture로 켜져 있는가
3. TLS termination과 scheme 처리가 올바른가
4. Traffic이 기대한 revision 또는 label로 가고 있는가
5. 선택된 Revision 뒤에 ready replica가 있는가
6. 요청이 도착했을 때 사용자 컨테이너가 제대로 응답하는가

![실무용 ingress 디버깅 사다리](../../assets/azure-aca-deep-dive/06/06-13-a-practical-ingress-debugging-ladder.ko.png)
이 사다리는 결국 요청 경로를 운영자 체크리스트로 바꾼 것에 불과합니다.

---

## 전체 요청 경로를 한 장으로

![전체 요청 경로를 한 장으로](../../assets/azure-aca-deep-dive/06/06-14-the-whole-request-path-in-one-diagram.ko.png)
이 그림이 시리즈 전체를 다시 묶는 마지막 도식입니다.

Environment는 네트워크 경계를 제공했습니다.
Revision은 불변 traffic target을 제공했습니다.
KEDA는 ready replica를 보장했습니다.
Dapr는 필요하면 앱 옆에 sidecar를 제공했습니다.
Envoy는 이 모든 외부 경로를 실제로 이어 주는 router입니다.

---

## 6화 정리

압축 모델은 다음과 같습니다.

> Azure Container Apps에서 첫 외부 HTTP 요청은 곧바로 사용자 컨테이너로 가지 않습니다. ACA 관리 Load Balancer를 거쳐 Envoy로 들어가고, 거기서 TLS가 종료되고 route가 매칭되며 Revision traffic weight가 적용됩니다. 그 다음 선택된 Revision의 Service를 거쳐 ready Pod replica로 전달됩니다.

이 ingress 경로가 이번 시리즈 전체를 하나로 묶습니다.

---

## 시리즈 안에서의 위치

이번 마지막 화는 시리즈 앞의 모든 개념을 실제 요청 경로에서 다시 만나는 글입니다. Environment는 네트워크 경계를 제공했고, Revision은 불변 traffic target을 제공했으며, KEDA는 replica를 준비했고, Dapr는 요청이 Pod에 닿은 뒤 추가 런타임 계층이 될 수 있었습니다. 제품 표면부터 다시 가볍게 훑고 싶다면 ACA 101 시리즈가 좋은 동반자이고, 기저 플랫폼 노출 정도를 비교해 보고 싶다면 AKS와 Azure Functions 심화 시리즈를 함께 읽는 편이 유익합니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- [Environment 내부 — 네트워크·관측·Dapr 스코프의 경계](./02-environment-internals.md)
- [Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가](./03-revision-and-traffic-split.md)
- [ACA 안의 KEDA — Scale Rule이 만드는 것](./04-keda-in-aca.md)
- [Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스](./05-dapr-sidecar-internals.md)
- **Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [`Envoy` route 구성 at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/api/envoy/config/route/v3/route_components.proto)
- [`Envoy` router 구현 at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/source/common/router/config_impl.cc)

### 2차 출처
- [Ingress in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Traffic splitting in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
