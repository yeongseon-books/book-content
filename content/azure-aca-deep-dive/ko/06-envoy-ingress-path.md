---
title: "Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지"
series: azure-aca-deep-dive
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Container Apps
- KEDA
- Dapr
- Envoy
last_reviewed: '2026-05-15'
seo_description: ACA의 첫 HTTPS 요청이 Ingress, Envoy형 라우팅, ready replica를 거쳐 사용자 컨테이너에 닿는 경로를 따라갑니다.
---

# Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지

Azure Container Apps의 Ingress 설명은 짧고 명확합니다. Ingress를 켜면 FQDN이 생기고, HTTPS를 받을 수 있고, 필요하면 Revision 사이에 트래픽을 나눌 수 있습니다. 서비스 출시에는 충분한 설명이지만, 첫 요청이 실제로 어디를 어떻게 지나가는지까지 보여 주지는 않습니다.

그 경로를 이해하려면 Microsoft가 직접 문서화한 부분과, Envoy 및 Kubernetes 패턴을 통해 조심스럽게 추론해야 하는 부분을 나눠 봐야 합니다. 그렇지 않으면 TLS 종료, forwarded header, weighted routing, ready replica, scale-to-zero wake-up이 한 문장으로 섞여 버립니다.

이 글은 Azure Container Apps Deep Dive 시리즈의 마지막 글입니다. 여기서는 첫 외부 HTTP 요청이 ACA-managed ingress 표면을 지나, Envoy형 라우팅 계층과 Kubernetes형 service hop을 거쳐 사용자 컨테이너에 도달한다고 보는 가장 방어 가능한 모델을 정리하겠습니다.

이 마지막 그림을 이해하면 앞의 다섯 편이 한 번에 연결됩니다. Environment는 네트워크 경계가 되고, Revision은 트래픽 대상이 되며, KEDA는 ready replica를 만들고, Dapr는 최종 Pod 안의 또 다른 런타임 참가자가 됩니다.

이제 첫 요청 경로를 앱이 아니라 바깥 edge부터 따라가 보겠습니다.

## 먼저 던지는 질문

- ACA의 public ingress 표면과 숨은 라우팅 계층은 어떻게 구분해 이해해야 할까요?
- TLS는 어디서 종료되고, 앱은 원래 요청 정보를 어떤 header로 복구할까요?
- Revision traffic split은 요청 경로의 어느 지점에서 실제가 될까요?

## 큰 그림

![Azure Container Apps Deep Dive 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-01-start-with-the-full-path-not-with-the-ap.ko.png)

*Azure Container Apps Deep Dive 6장 흐름 개요*

이 그림에서는 Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

Ingress 문제를 앱부터 의심하는 습관은 ACA에서 특히 비효율적입니다. 사용자가 컨테이너 코드에 도달하기 전에 이미 public edge, TLS termination, host 처리, forwarded header, revision selection, ready replica 선택 같은 여러 층을 통과하기 때문입니다. 따라서 “앱이 5xx를 냈다”와 “Ingress가 5xx를 냈다”는 전혀 다른 사건일 수 있습니다.

또한 이 경로는 시리즈 전체를 묶는 최종 접점입니다. Revision과 traffic split은 Ingress에서 실제가 되고, KEDA가 만든 ready replica가 없으면 요청은 성공할 수 없으며, Dapr가 켜진 앱이라면 최종 Pod 안에서 sidecar까지 같은 요청 체인에 포함됩니다. 즉 Ingress 경로는 ACA의 모든 런타임 계층이 만나는 자리입니다.

마지막으로 첫 요청의 지연을 설명할 때도 이 경로가 필요합니다. scale-to-zero 상태에서 들어온 요청은 routing decision만 하는 것이 아니라 replica creation, app startup, probe 통과, sidecar startup을 함께 기다릴 수 있기 때문입니다. 이 사실을 모르면 cold first request를 계속 잘못 해석하게 됩니다.

## 핵심 관점

ACA Ingress를 가장 정확하게 설명하는 방법은 두 층으로 나누는 것입니다. **문서화된 부분은 ACA-managed ingress surface이고, 그 뒤의 런타임 라우팅은 Envoy형 proxy behavior와 Kubernetes형 service pattern으로 제한적으로 추론**하는 것입니다.

이 구분이 중요합니다. FQDN, TLS termination, forwarded headers, traffic split, session affinity는 Microsoft가 문서화한 제품 계약입니다. 반면 weighted upstream selection, service-style fan-out, private 0→1 request path의 상세 buffering 전략은 제품 내부 구현에 속하며 공개되지 않습니다.

이렇게 나눠야만 closed-source 제품을 과장하지 않고도 정확하게 설명할 수 있습니다. 공개 사실은 사실대로 쓰고, 추론은 Envoy와 Kubernetes의 표준 semantic에 기댄 방어 가능한 수준으로 유지하는 방식입니다.

> ACA의 첫 요청 경로를 이해하려면 “제품이 약속한 ingress 기능”과 “그 약속을 실행하기 위해 내부에서 일어날 법한 표준 프록시·서비스 패턴”을 분리해서 봐야 합니다.

## 핵심 개념

### 시작점은 앱이 아니라 전체 경로입니다

Ingress 디버깅에서 가장 흔한 실수는 사용자 컨테이너부터 보는 것입니다. 하지만 요청은 이미 그 전에 여러 플랫폼 계층을 통과합니다. 연결 실패, TLS 문제, host 문제, header 문제, Revision 선택, readiness 문제는 모두 앱 코드보다 앞 단계에서 일어날 수 있습니다.

이 순서를 머리에 넣어 두면 사고 범위를 훨씬 빨리 줄일 수 있습니다. 연결 자체가 안 되면 Pod 밖 문제일 수 있고, host/TLS/header 문제는 service hop 이전일 가능성이 높으며, Revision 선택은 프록시 계층의 일입니다.

### Microsoft가 직접 문서화한 Ingress 계약

ACA의 ingress overview는 제품 수준 계약을 꽤 명확하게 제시합니다. HTTP ingress는 TLS termination, HTTP/1.1·HTTP/2, WebSocket과 gRPC 지원, 80/443 포트, 기본 HTTP→HTTPS redirect, FQDN, Revision 간 traffic split, session affinity를 제공합니다.

이 목록의 모든 항목은 proxy behavior를 암시합니다. 그래서 Envoy를 runtime anchor로 두는 편이 맞습니다. 즉 사용자가 받는 기능은 제품 약속이고, 그 기능을 구현하는 HTTP-aware routing layer를 설명하는 기준점이 Envoy입니다.

### 첫 managed edge는 사용자 컨테이너가 아닙니다

사용자는 Pod와 직접 통신하지 않습니다. 외부 요청은 먼저 ACA의 managed edge infrastructure에 닿습니다. public endpoint는 플랫폼 endpoint이고, 사용자 컨테이너는 그 뒤의 downstream destination입니다.

![Managed edge and Envoy routing split](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-02-the-load-balancer-is-the-first-managed-e.ko.png)

*Managed edge and Envoy routing split*

Microsoft는 public ingress edge를 제품 기능으로 소유합니다. 그 뒤의 HTTP-aware routing decision은 Envoy를 기준점으로 설명하는 편이 가장 방어 가능합니다. 내부 object 이름과 hop-by-hop wiring은 공개되지 않았지만, 역할 분리는 분명합니다.

### TLS는 기본적으로 Ingress에서 끝납니다

ACA 문서는 HTTP ingress의 TLS termination이 ingress point에서 일어난다고 설명합니다. 즉 클라이언트와의 HTTPS 연결은 사용자 컨테이너에 도착하기 전에 종료됩니다.

![TLS termination and internal HTTP forwarding](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-03-tls-ends-at-ingress-not-at-your-containe.ko.png)

*TLS termination and internal HTTP forwarding*

이 사실은 운영에서 여러 의미를 가집니다. 앱은 원래 TLS socket 대신 forwarded header를 보게 되고, 인증서 관리는 ingress 표면의 책임이 되며, 앱이 클라이언트-facing TLS를 직접 소유한다고 착각하면 redirect나 absolute URL 생성에서 혼선이 생길 수 있습니다.

### forwarded header는 선택 사항이 아니라 실제 계약입니다

ACA ingress는 `X-Forwarded-Proto`, `X-Forwarded-For`, 적절한 인증서 모드의 `X-Forwarded-Client-Cert` 같은 header를 문서화합니다. 이는 앱이 프록시 뒤에 있다는 사실을 반영합니다.

![Forwarded headers and original request context](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-04-forwarded-headers-are-part-of-the-ingres.ko.png)

*Forwarded headers and original request context*

절대 URL 생성, scheme-aware redirect, client IP 로깅을 할 때 이 header들은 optional decoration이 아닙니다. 실제 런타임 경로의 일부입니다.

### routing step은 service hop보다 먼저 일어납니다

TLS 종료가 끝나면 프록시는 upstream destination을 골라야 합니다. 한 Revision만 active라면 단순할 수 있지만, 여러 Revision이 active라면 weighted selection이 필요합니다. Microsoft는 Revision traffic split을 ingress 기능이라고 문서화합니다.

![Revision routing before the service hop](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-05-the-routing-step-happens-before-the-serv.ko.png)

*Revision routing before the service hop*

Envoy upstream 동작을 기준으로 보면, 가장 방어 가능한 설명은 weighted upstream selection입니다. 핵심은 선택이 여기서 일어나야 한다는 점입니다. 앱 안에 들어간 뒤에는 이미 어떤 Revision인지 결정된 뒤이기 때문입니다.

### Envoy의 weight는 upstream cluster weight입니다

여기서도 용어를 반복해서 바로잡아야 합니다. Envoy에서 cluster는 Kubernetes cluster가 아니라 upstream service target입니다. 이 의미를 기준으로 보면 ACA의 80/20 split이 “어디에 사는가”라는 질문에 대한 가장 안전한 답은 ingress routing state 안의 weighted destination입니다.

![Envoy weights across revision upstreams](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-06-envoy-weight-means-upstream-cluster-weig.ko.png)

*Envoy weights across revision upstreams*

즉 사용자가 포털에서 설정한 traffic percentage는 product config로 시작하고, 가장 설득력 있는 추론에 따르면 Envoy형 routing layer에서 Revision upstream 간 가중치로 적용됩니다.

### ACA가 Kubernetes를 감춰도 service-style hop은 사라지지 않습니다

사용자 시점에서는 요청이 “그 Revision”으로 간다고 느껴집니다. 하지만 숨은 data plane을 설명하는 가장 방어 가능한 모델은 ingress routing 뒤에 service-style hop이 있다는 것입니다. 선택된 upstream은 보통 개별 Pod 하나가 아니라, ready replica 집합을 향한 endpoint set으로 보는 편이 Kubernetes 패턴과 가장 잘 맞습니다.

![Service-style fan-out behind ingress routing](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-07-the-service-hop-is-easy-to-forget-becaus.ko.png)

*Service-style fan-out behind ingress routing*

이 hop에서 scaling과 ingress가 만납니다. 선택된 Revision 뒤에 ready replica가 있어야만 요청이 성공할 수 있기 때문입니다.

### readiness는 Ingress 경로의 일부입니다

3편에서 본 readiness gate와 4편에서 본 replica creation은 여기서 만납니다. ACA는 새 Revision이 준비되기 전에는 트래픽을 넘기지 않습니다. 그리고 Ingress가 Revision의 존재를 안다고 해도, 실제 요청이 끝까지 성공하려면 선택된 Revision 뒤에 healthy upstream endpoint가 있어야 합니다.

![Revision readiness and ready replica availability](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-08-readiness-is-part-of-the-ingress-path-wh.ko.png)

*Revision readiness and ready replica availability*

그래서 ingress debugging은 revision state와 replica readiness를 분리해서 볼 수 없습니다. 요청 경로가 원래 cross-cutting하게 설계되어 있기 때문입니다.

### scale-to-zero Revision의 첫 요청은 특별합니다

ACA는 scale-to-zero를 지원합니다. 따라서 첫 요청이 replica가 하나도 없는 Revision을 향할 수 있습니다. 이 순간부터 ingress와 autoscaling은 더 이상 별도 주제가 아닙니다.

![Wake-up path for a scale-to-zero revision](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-09-the-first-request-to-a-scale-to-zero-rev.ko.png)

*Wake-up path for a scale-to-zero revision*

Microsoft는 scale rule 차원에서 wake-from-zero 동작을 문서화하지만, private 0→1 전환 동안의 정확한 Envoy·queueing·buffering 동작은 공개하지 않습니다. 운영자가 안전하게 말할 수 있는 범위는 “첫 요청이 ready upstream이 생길 때까지 기다릴 수 있다”입니다.

### 첫 요청이 느린 이유는 플랫폼 이상이 아니라 숨은 단계들의 합일 수 있습니다

Revision이 0에 있다면 첫 요청은 activation decision, replica creation, image start path, app startup, probe success, Dapr가 켜져 있다면 sidecar startup까지 함께 비용을 냅니다.

![Hidden stages behind first-request latency](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-10-why-the-first-request-can-feel-slower-ev.ko.png)

*Hidden stages behind first-request latency*

즉 첫 요청 지연은 ingress 품질만의 문제가 아닙니다. 플랫폼은 건강해도, downstream 경로에 필요한 런타임 단계가 많으면 느려질 수 있습니다.

### Dapr가 켜져 있으면 Pod 안의 또 다른 참가자가 생깁니다

최종 Pod에 요청이 도달했을 때 Dapr가 켜져 있다면, 그 Pod에는 사용자 컨테이너와 `daprd` sidecar가 함께 있을 수 있습니다. ingress path는 Pod endpoint에서 끝나지만, 그 뒤 애플리케이션 동작은 sidecar 참여 여부에 따라 달라질 수 있습니다.

![Dapr participation inside the target pod](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-11-dapr-adds-another-runtime-participant-be.ko.png)

*Dapr participation inside the target pod*

그래서 최종 사용자 한 번의 요청 실패가 ingress routing, revision readiness, pod startup, sidecar behavior를 모두 가로지를 수 있습니다.

### session affinity도 ingress에 속합니다

ACA는 sticky session을 ingress feature로 문서화합니다. 이것은 ingress가 coarse routing 이상을 담당한다는 또 하나의 증거입니다. concrete mechanism은 Envoy형 proxy-level affinity로 이해하는 편이 자연스럽지만, 제품이 공개한 것은 “stickiness가 ingress에 있다”는 사실입니다.

즉 Revision 선택과 replica 선택은 여전히 proxy concern입니다. 앱 안에 들어간 뒤에 붙는 기능이 아닙니다.

### internal ingress도 큰 그림은 같습니다

internal-only 앱에서는 인터넷-facing edge가 사라집니다. 하지만 앱은 여전히 ACA ingress 뒤에 있습니다. edge transport만 달라질 뿐, downstream proxy-routing과 service-upstream logic의 큰 형태는 여전히 비슷하다고 보는 편이 가장 방어 가능합니다.

![Internal ingress on the same routing shape](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-12-internal-ingress-follows-the-same-broad.ko.png)

*Internal ingress on the same routing shape*

이 점을 이해하면 external/internal ingress를 완전히 다른 서비스로 상상하지 않게 됩니다. edge 조건만 바뀌고, 내부 라우팅 모델은 상당 부분 공통입니다.

### 운영자는 경로를 사다리처럼 내려가며 봐야 합니다

요청이 실패했을 때는 순서를 바꾸지 않는 것이 중요합니다.

![Ordered ingress debugging checks](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-13-a-practical-ingress-debugging-ladder.ko.png)

*Ordered ingress debugging checks*

1. 클라이언트가 public FQDN을 해석하고 도달할 수 있는가
2. 기대한 external/internal posture로 ingress가 켜져 있는가
3. TLS termination과 scheme handling이 맞는가
4. 요청이 기대한 Revision 또는 label로 라우팅되는가
5. 선택된 Revision 뒤에 ready replica가 존재하는가
6. 요청이 도달한 뒤 사용자 컨테이너가 올바르게 응답하는가

이 사다리는 시리즈 전체의 내용을 운영 절차로 바꾼 것입니다.

### 전체 요청 경로를 한 장에 연결하면 시리즈가 닫힙니다

![Full ACA request path end to end](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/06/06-14-the-whole-request-path-in-one-diagram.ko.png)

*Full ACA request path end to end*

Environment는 네트워크 경계를 제공하고, Revision은 immutable target을 제공하며, KEDA는 replica를 만들고, Dapr는 필요할 때 sidecar runtime을 추가합니다. Envoy형 routing layer는 그 위에서 어떤 Revision upstream으로 요청을 보낼지 결정합니다. 이 그림이 시리즈 전체의 최종 합본입니다.

### 운영자가 즉시 확인할 명령

아래 명령은 ingress 설정과 hostname, traffic 상태를 확인하는 기본 점검입니다.

```bash
az containerapp ingress show -n my-app -g my-rg \
  --query "{external:external, target:targetPort, transport:transport, traffic:traffic}"

az containerapp ingress traffic show -n my-app -g my-rg -o table
az containerapp hostname list -n my-app -g my-rg -o table
```

이 출력은 단순 조회가 아닙니다. external/internal posture, target port, transport, traffic rule, hostname이 모두 “문서화된 ingress 표면”에 속한다는 사실을 다시 확인시켜 줍니다.

## 흔히 헷갈리는 지점

- **Ingress 문제를 앱 코드부터 의심하면 안 됩니다.** 요청은 그 전에 여러 플랫폼 계층을 통과합니다.
- **TLS는 기본적으로 앱 컨테이너가 아니라 ingress에서 종료됩니다.** 앱은 forwarded header를 봅니다.
- **traffic split은 앱 안의 로직이 아닙니다.** ingress routing state입니다.
- **첫 요청 지연은 ingress 장애와 같은 뜻이 아닙니다.** scale-to-zero wake-up과 startup 단계의 합일 수 있습니다.
- **internal ingress는 완전히 다른 서비스가 아닙니다.** public edge만 다르고 내부 라우팅 형식은 상당 부분 닮아 있습니다.

## 운영 체크리스트

- [ ] hostname별로 external/internal ingress 사용이 일관적인지 확인했습니다.
- [ ] 자동 TLS 인증서 갱신이 정상 동작하는지 검증했습니다.
- [ ] websocket 및 장수 연결 timeout을 ingress와 앱 양쪽에서 맞췄습니다.
- [ ] ingress 5xx 비율과 p95 지연 경보를 분리해 설정했습니다.
- [ ] backend health check 실패 시 traffic split 동작을 시뮬레이션했습니다.

## 정리

ACA의 Ingress를 정확하게 이해하려면 제품이 문서화한 ingress 표면과, 그 뒤에서 추론되는 Envoy형 라우팅 계층을 분리해서 봐야 합니다. FQDN, TLS termination, forwarded header, traffic split, session affinity는 공개 계약이고, weighted upstream selection과 service-style fan-out은 그 계약을 설명하는 가장 방어 가능한 내부 모델입니다.

또한 첫 요청 경로는 시리즈 전체의 개념이 한곳에 모이는 자리입니다. Environment는 네트워크 경계가 되고, Revision은 트래픽 대상이 되며, KEDA는 ready replica를 만들고, Dapr는 최종 Pod 안에서 추가 런타임으로 참여할 수 있습니다. 요청 경로 하나를 따라가면 ACA 전체 구조가 다시 보입니다.

이것으로 Azure Container Apps Deep Dive 시리즈를 마칩니다. 제품 표면만 볼 때는 단순했던 기능들이, 실제로는 서로 다른 경계와 제어 루프 위에 세워진 구조라는 점이 이제는 더 분명하게 보일 것입니다.

## 처음 질문으로 돌아가기

- **ACA의 public ingress 표면과 숨은 라우팅 계층은 어떻게 구분해 이해해야 할까요?**
  - 본문의 기준은 Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **TLS는 어디서 종료되고, 앱은 원래 요청 정보를 어떤 header로 복구할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Revision traffic split은 요청 경로의 어느 지점에서 실제가 될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps Deep Dive (1/6): ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- [Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계](./02-environment-internals.md)
- [Azure Container Apps Deep Dive (3/6): Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가](./03-revision-and-traffic-split.md)
- [Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것](./04-keda-in-aca.md)
- [Azure Container Apps Deep Dive (5/6): Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스](./05-dapr-sidecar-internals.md)
- **Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Ingress in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Traffic splitting in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
