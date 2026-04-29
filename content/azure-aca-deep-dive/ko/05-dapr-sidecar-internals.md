# Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스

> Azure Container Apps Deep Dive 시리즈 (5/6)

독자가 Azure Container Apps에서 Dapr를 처음 켜 보면 기능이 놀랄 만큼 가볍게 보입니다.

체크박스 몇 개를 누르거나 필드 몇 개를 채웁니다.
App ID가 생깁니다.
갑자기 서비스가 localhost 3500 또는 50001에 붙어 state store, pub/sub, service invocation, secret API를 쓸 수 있게 됩니다.

표면은 작습니다.
런타임 변화는 전혀 작지 않습니다.

실제로는 upstream Dapr sidecar 프로세스인 `daprd`가 사용자 컨테이너 옆에 붙도록 플랫폼이 배치한 것입니다.
이 프로세스는 Go로 작성되어 있습니다.
Pod에 주입됩니다.
자기 포트, 인자, probe, 인증서, component 로딩 경로를 모두 가집니다.

이번 화는 pod mutation부터 localhost API 호출까지 이 경로를 따라갑니다.

---

## 가장 짧고 정확한 문장

ACA의 Dapr는 Container Apps 제품 표면에 통합된 upstream Dapr runtime입니다.

이 문장이 중요한 이유는 두 가지 잘못된 모델을 바로 지우기 때문입니다.

첫째, ACA가 제어면에서 Dapr 비슷한 API만 흉내 내는 것은 아닙니다.
둘째, Dapr를 켠다는 것이 앱 metadata 몇 개 추가하는 일로 끝나지 않습니다.

Pod 모양 자체가 바뀝니다.

![가장 짧고 정확한 문장](../../../assets/azure-aca-deep-dive/05/05-01-the-shortest-accurate-sentence.ko.png)
앱은 로컬에 붙습니다.
사이드카는 바깥과 통신합니다.
이게 기본 계약입니다.

---

## 출발점은 pod mutation 모델입니다

Upstream Dapr on Kubernetes는 mutating admission webhook으로 sidecar를 주입합니다.
Pinned Dapr source의 injector service 코드와 pod patch 경로가 그 사실을 보여 줍니다.

Injector는 admission review를 받고, pod annotation과 환경 상태에서 sidecar config를 만들고, Dapr sidecar container를 추가하는 patch operation을 생성합니다.

![출발점은 pod mutation 모델입니다](../../../assets/azure-aca-deep-dive/05/05-02-start-with-the-pod-mutation-model.ko.png)
ACA는 raw Kubernetes admission mechanics를 직접 보여 주지 않습니다.
그래도 런타임 모양을 설명하려면 upstream injector 모델이 가장 맞습니다.
실제로 붙는 sidecar가 같은 계열의 프로세스이기 때문입니다.

---

## Injector의 일은 "컨테이너 하나 추가"보다 훨씬 큽니다

Pinned upstream Dapr source를 보면 pod patch 코드는 단순히 `daprd`를 붙이라고 말하는 수준이 아닙니다.

다음 값을 계산합니다.

- sidecar image
- trust anchor와 certificate material
- control plane address
- mode와 namespace 값
- app ID와 app protocol
- health와 readiness 설정
- port number
- volume mount와 environment variable

그래서 sidecar는 generic helper container가 아니라, 구성된 runtime process로 봐야 합니다.

---

## Sidecar container의 실체는 `daprd`입니다

Upstream `sidecar_container.go` 파일은 주입되는 컨테이너의 실체를 잘 보여 줍니다.
이 코드는 command가 `/daprd`인 컨테이너를 만들고, sidecar config에서 조합한 CLI flag를 붙입니다.

이 파일 하나만 봐도 핵심이 드러납니다.

- 실제 실행 파일입니다.
- 명시적인 CLI flag를 받습니다.
- 명시적인 port를 엽니다.
- readiness / liveness probe를 가집니다.

![Sidecar container의 실체는 `daprd`입니다](../../../assets/azure-aca-deep-dive/05/05-01-the-sidecar-container-is-literally-daprd.ko.png)
즉 제품 표면에서 Dapr를 켠다는 짧은 설정은, 런타임에서는 이렇게 구성된 두 번째 프로세스를 Pod 안에 띄우는 일입니다.

---

## 이것을 Go 프로세스라고 부르는 이유

독자는 sidecar라는 말을 듣고 막연한 보조 통로를 떠올리기 쉽습니다.
여기서 `daprd`를 Go 프로세스라고 부르는 편이 유용한 이유는, 실제 런타임 단위를 중심에 놓기 때문입니다.

이 프로세스는 다음을 모두 가집니다.

- 자체 부팅 경로
- 자체 장애 형태
- 자체 로그
- 자체 health probe
- 자체 listener
- 자체 설정 로딩 경로

ACA에서 Dapr가 이상하다면, 더 이상 여러분 앱만 디버깅하는 것이 아닙니다.
옆에서 같이 도는 런타임 프로세스를 함께 디버깅해야 합니다.

---

## 부팅 경로: `main.go`에서 `app.Run()`을 거쳐 runtime 생성까지

Pinned upstream Dapr code는 이 부팅 경로를 깔끔하게 보여 줍니다.

`cmd/daprd/main.go`는 매우 짧습니다.
`app.Run()`을 호출합니다.
그 뒤 bootstrap 경로가 runtime option, logging, security, 최종 Dapr runtime object를 만든 뒤 `Run`을 호출합니다.

![부팅 경로: `main.go`에서 `app.Run()`을 거쳐 runtime 생성까지](../../../assets/azure-aca-deep-dive/05/05-04-boot-path-main-go-to-app-run-to-runtime.ko.png)
ACA 독자에게 중요한 것은 부팅 세부사항 전부가 아닙니다.
Dapr를 켜면 실제로 완전한 런타임 프로그램이 하나 더 떠서, 정상적인 프로세스 생명주기와 설정 파이프라인을 돈다는 사실입니다.

---

## Sidecar 포트는 구체적이며 중요합니다

Upstream runtime config 기본값은 Dapr HTTP와 gRPC API 포트를 명시합니다.

- HTTP API: 3500
- Public HTTP port: 3501
- gRPC API: 50001

Microsoft의 ACA Dapr overview도 sidecar가 HTTP 3500, gRPC 50001을 노출한다고 설명합니다.

![Sidecar 포트는 구체적이며 중요합니다](../../../assets/azure-aca-deep-dive/05/05-05-the-sidecar-ports-are-concrete-and-impor.ko.png)
이 포트는 추상적 개념이 아닙니다.
여러분 코드와 sidecar 사이의 로컬 계약입니다.

ACA 앱이 Dapr service invocation이나 state operation을 쓸 때는, 대부분 이 로컬 listener 중 하나에 붙고 있는 셈입니다.

---

## 왜 localhost가 그렇게 중요한가

Sidecar 패턴의 핵심은 앱이 외부 의존성의 최종 네트워크 경로를 몰라도 된다는 점입니다.
localhost API 계약만 알면 됩니다.

이 구조가 portability와 decoupling을 줍니다.

앱은 말합니다.

- 서비스 X를 호출해 달라
- key Y를 저장해 달라
- topic Z에 publish해 달라

Sidecar는 말합니다.

- 어떤 component가 그 요청을 담당하는지 안다
- 어디로 라우팅할지 안다
- 어떻게 인증하고 직렬화할지 안다

![왜 localhost가 그렇게 중요한가](../../../assets/azure-aca-deep-dive/05/05-06-why-localhost-matters-so-much.ko.png)
그래서 Dapr는 앱은 단순하게 만들고, Pod 모양은 더 복잡하게 만듭니다.

---

## Component 로딩에서 다시 등장하는 Environment 경계

2화에서 Dapr component가 ACA에서 environment-level resource라고 했습니다.
이번 화는 그 말이 런타임에서 왜 중요한지 보여 줍니다.

Sidecar runtime은 Dapr app ID와 scope에 따라 component 정의를 로드합니다.
Microsoft의 components 문서도 scope가 Container App 이름이 아니라 Dapr app ID에 대응한다고 분명히 적습니다.

![Component 로딩에서 다시 등장하는 Environment 경계](../../../assets/azure-aca-deep-dive/05/05-07-component-loading-is-where-aca-s-environ.ko.png)
즉 Environment는 component registry 경계를 소유합니다.
실제 어떤 scoped component가 살아나는지는 sidecar가 최종 런타임 판단을 합니다.

---

## ACA에서 Dapr enablement는 app-level 스위치이면서 environment-level 의존성을 가집니다

이 분리는 미묘하지만 중요합니다.

여러분은 app에서 Dapr를 켭니다.
하지만 sidecar는 environment-level component와 configuration 상태에 의존할 수 있습니다.

즉 ACA의 Dapr 동작은 최소 두 스코프를 항상 가로지릅니다.

- enablement와 sidecar attachment를 위한 app scope
- component availability와 sharing을 위한 environment scope

![ACA에서 Dapr enablement는 app-level 스위치이면서 environment-level 의존성을 가집니다](../../../assets/azure-aca-deep-dive/05/05-08-enabling-dapr-in-aca-is-an-app-level-swi.ko.png)
App 설정은 멀쩡해 보이는데 런타임 동작이 실패한다면, 빠진 조각은 app scope가 아니라 environment scope에 있을 수 있습니다.

---

## Injector 코드는 ACA 사용자에게도 꽤 많은 힌트를 줍니다

Upstream sidecar container builder에는 ACA 사용자가 실제로 체감하는 flag가 많이 보입니다.

대표적으로 다음과 같습니다.

- `--dapr-http-port`
- `--dapr-grpc-port`
- `--app-id`
- `--app-port`
- `--app-protocol`
- `--control-plane-address`
- `--sentry-address`
- `--enable-mtls`

ACA에서 여러분이 이 값을 전부 직접 주지는 않습니다.
중요한 것은 런타임 프로세스가 이 값들을 실제로 필요로 한다는 점입니다.
관리형 플랫폼이 이 값을 여러분 대신 결정하거나 파생하고 있을 뿐입니다.

이것이 관리형 sidecar 통합이란 무엇인지 보여 주는 또 하나의 단서입니다.

---

## Dapr는 building block API만이 아니라 health / metadata API이기도 합니다

Microsoft의 ACA용 Dapr overview는 building block API와 operational API를 구분합니다.
이 구분은 중요합니다.
Sidecar는 기능 API만 제공하는 것이 아니라, 관측 가능한 runtime이기도 하기 때문입니다.

State, pub/sub, invocation, bindings 외에도 sidecar는 다음 같은 operational surface를 가집니다.

- health
- metadata

![Dapr는 building block API만이 아니라 health / metadata API이기도 합니다](../../../assets/azure-aca-deep-dive/05/05-09-dapr-is-not-only-the-building-block-apis.ko.png)
즉 sidecar는 원격 호출 편의 래퍼에 그치지 않습니다.
Pod 안에서 직접 접근 가능한 운영 endpoint이기도 합니다.

---

## App -> sidecar와 sidecar -> app는 다른 채널입니다

기억해야 할 로컬 관계는 사실 두 개입니다.

1. 앱이 localhost로 sidecar를 호출합니다.
2. 특정 패턴에서는 sidecar도 앱을 호출합니다.

예를 들어 service invocation delivery나 pub/sub handler 호출이 그렇습니다.

![App -> sidecar와 sidecar -> app는 다른 채널입니다](../../../assets/azure-aca-deep-dive/05/05-10-app-to-sidecar-and-sidecar-to-app-are-se.ko.png)
그래서 app port와 app protocol 설정은 장식이 아닙니다.
Sidecar가 여러분 코드를 어떤 방식으로 호출해야 하는지 알려 주는 값입니다.

---

## Incident timeline에 sidecar 로그를 반드시 넣어야 하는 이유

Microsoft의 environment 문서도 Dapr sidecar log가 공용 logging destination에 포함된다고 설명합니다.
사고 분석에서는 이 점이 매우 중요합니다.

요청이 실패했을 때, 사용자 컨테이너보다 sidecar가 더 많은 사실을 알고 있을 수 있습니다.

- component load failure
- auth issue
- service invocation resolution issue
- backing service timeout
- sidecar startup failure

![Incident timeline에 sidecar 로그를 반드시 넣어야 하는 이유](../../../assets/azure-aca-deep-dive/05/05-11-why-sidecar-logs-belong-in-your-incident.ko.png)
Sidecar 로그를 부수 데이터로 보지 말고, 1급 증거로 다루는 편이 맞습니다.

---

## mTLS와 trust material도 이게 진짜 런타임이라는 증거입니다

Injector 코드는 trust anchor, certificate material, Sentry address, identity 관련 설정을 다룹니다.
이건 장식용 metadata가 아닙니다.

보안 인지형 분산 런타임이 실제로 동작하기 위해 필요한 구성입니다.

이 점이 중요한 이유는, Dapr service invocation이 단순한 친절한 client library 경험만은 아니기 때문입니다.
실제 sidecar-to-sidecar 인프라와 identity plumbing이 아래에 있습니다.

ACA가 관리 세부사항을 감추더라도, 런타임 복잡도 자체는 남아 있습니다.

---

## Sidecar 전체 생명주기를 한 장으로

![Sidecar 전체 생명주기](../../../assets/azure-aca-deep-dive/05/05-12-putting-the-whole-sidecar-lifecycle-in-o.ko.png)
이 그림이 체크박스 하나가 Pod 안의 두 번째 런타임 프로세스로 이어지는 전체 압축본입니다.

---

## ACA 운영자에게 이 구조가 뜻하는 것

실무적으로는 세 가지를 가져가면 됩니다.

첫째, Dapr 문제는 "내 앱 코드가 틀렸다"로 끝나지 않습니다.
Sidecar bootstrap, component scope, environment config, sidecar-to-backing-service 경로 문제일 수 있습니다.

둘째, Dapr에서 Environment 설계는 component scope가 거기 살기 때문에 특히 중요합니다.

셋째, localhost 호출이 성공했다는 사실은 외부 의존성 경로 전체가 건강하다는 뜻이 아닙니다.
앱이 sidecar까지 도달했다는 뜻일 뿐입니다.

Timeout 분석에서는 이 마지막 구분이 특히 중요합니다.

---

## 5화 정리

압축 모델은 다음과 같습니다.

> Azure Container Apps에서 Dapr를 켜면, upstream `daprd` sidecar 프로세스가 실제로 Pod에 주입됩니다. 이 Go 프로세스는 localhost에 Dapr HTTP / gRPC API를 열고, Dapr app ID scope에 따라 Environment 수준 component를 로드하며, 여러분 코드와 외부 서비스 사이의 런타임 중계자가 됩니다.

런타임에서 "Dapr enabled"가 뜻하는 것은 바로 이것입니다.

---

## 시리즈 안에서의 위치

앞선 4화가 ACA가 Revision을 어떻게 스케일하는지 설명했다면, 이번 5화는 Dapr를 켰을 때 그 Revision의 Pod 모양이 어떻게 바뀌는지 설명한 글입니다. 마지막 6화에서는 다시 ingress로 돌아가, ACA 관리 Load Balancer와 Envoy, Service, Pod를 거쳐 첫 외부 요청이 어떻게 사용자 컨테이너까지 도달하는지 따라갑니다. 그 Pod 안에는 이번 화에서 본 sidecar가 함께 있을 수도 있습니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- [Environment 내부 — 네트워크·관측·Dapr 스코프의 경계](./02-environment-internals.md)
- [Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가](./03-revision-and-traffic-split.md)
- [ACA 안의 KEDA — Scale Rule이 만드는 것](./04-keda-in-aca.md)
- **Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 (현재 글)**
- Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (예정)

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [`dapr/dapr` tree at `v1.13.0`](https://github.com/dapr/dapr/tree/v1.13.0)
- [`daprd` 진입점](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/main.go)
- [`daprd` 부팅 코드](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/app/app.go)
- [Dapr runtime 기본 포트와 설정](https://github.com/dapr/dapr/blob/v1.13.0/pkg/runtime/config.go)
- [Dapr injector의 pod patch 로직](https://github.com/dapr/dapr/blob/v1.13.0/pkg/injector/service/pod_patch.go)
- [Dapr sidecar container 구성 코드](https://github.com/dapr/dapr/blob/v1.13.0/pkg/injector/patcher/sidecar_container.go)

### 2차 출처
- [Microservice APIs Powered by Dapr](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Azure Container Apps environments](https://learn.microsoft.com/en-us/azure/container-apps/environment)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
