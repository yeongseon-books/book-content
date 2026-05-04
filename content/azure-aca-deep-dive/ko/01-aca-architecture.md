---
title: ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것
series: azure-aca-deep-dive
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Container Apps
- KEDA
- Dapr
- Envoy
last_reviewed: '2026-04-29'
seo_description: '이 글의 외부 인용은 다음 upstream 기준으로 고정했습니다: - Dapr: v1.13.x…'
---

# ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것

## Source Version

이 글의 외부 인용은 다음 upstream 기준으로 고정했습니다:
- Dapr: v1.13.x (https://github.com/dapr/dapr)
- KEDA: v2.14.x (https://github.com/kedacore/keda)
- Envoy: v1.30.x (https://github.com/envoyproxy/envoy)

ACA 내부 구현은 Microsoft가 공개하지 않으므로, 위 버전은 비교 기준으로만 사용합니다.

## Evidence Model

- **Microsoft가 문서로 직접 밝힌 범위**: ACA는 Kubernetes 기반이며, Environment·Revision·Ingress·Dapr·Autoscaling을 제품 기능으로 노출합니다.
- **업스트림 동작을 바탕으로 한 추론**: 숨겨진 기저 계층은 Kubernetes primitive 위에 Envoy, KEDA, Dapr류 런타임 조각을 조합한 형태일 가능성이 높습니다.
- **이 글이 넘지 않는 선**: Microsoft가 공개하지 않은 정확한 클러스터 토폴로지, private control plane 바이너리, 환경별 내부 구현 세부사항.

> Azure Container Apps Deep Dive 시리즈 (1/6)

Azure Container Apps의 공개 설명은 일부러 단순합니다.
컨테이너 이미지를 올립니다.
Ingress나 Dapr, 스케일 규칙을 켭니다.
플랫폼 운영은 Microsoft가 맡습니다.

이 단순화는 분명 편합니다.
동시에 내부 구조를 한 덩어리로 오해하게 만들기도 합니다.

Container Apps는 raw Kubernetes 서비스가 아닙니다.
그렇다고 "AKS에 편의 기능만 얹은 것"으로 끝나는 제품도 아닙니다.
Microsoft는 ACA가 Kubernetes 기반이라고 문서화하지만, 각 Environment 뒤의 정확한 substrate는 공개하지 않습니다.
가장 안전한 설명은, Microsoft가 운영하는 Kubernetes 인프라 위에 Revision, Ingress, Autoscaling, Dapr 통합, 로깅, Environment 경계 같은 제품 기능을 얹은 서버리스 컨테이너 플랫폼이라는 것입니다.

이번 시리즈는 그 겹을 하나씩 벗겨 보는 작업입니다.
1화는 지도를 그립니다.
뒤의 화들은 그 지도 안의 박스를 하나씩 확대합니다.

---

## 이 글에서 답할 질문

- ACA는 결국 어떤 추상화 위에 어떤 추상화를 또 쌓은 플랫폼인가?
- managed environment 안의 component(KEDA, Dapr, Envoy)는 누가 소유하고 누가 업그레이드하는가?
- ACA가 AKS 위에서 돈다는 사실은 사용자에게 어떤 의무를 남기고 어떤 의무를 가져가는가?
- control plane 장애가 나면 우리 앱은 어떻게 보이고 어떻게 회복되는가?
- 한 environment 안에서 격리는 어디서 끊어지는가, 어디서 끊어지지 않는가?

## 전체 그림 — Azure Container Apps Environment

이 그림이 이번 심화 시리즈 전체의 지도입니다.
뒤의 글들은 아래 박스 하나씩을 확대해서 보는 구조입니다.
먼저 모양을 잡아 두면, 이후의 세부 동작이 훨씬 덜 낯섭니다.

![요청 경로와 숨은 substrate 계층 구조](../../../assets/azure-aca-deep-dive/01/01-01-the-big-picture-one-container-apps-envir.ko.png)

*요청 경로와 숨은 substrate 계층 구조*
왼쪽은 사용자가 보는 요청 경로입니다.
가운데는 여러분이 Container Apps라는 이름으로 다루는 런타임 표면입니다.
점선 경계는 직접 제어할 수 없는 Kubernetes 계층입니다.
오른쪽은 이미지와 텔레메트리가 요청 경로 밖으로 빠져나가는 지점입니다.

2화는 Environment 경계와 네트워크, 공용 관측 계층을 확대합니다.
3화는 Revision과 트래픽 가중치를 봅니다.
4화는 KEDA 박스를 엽니다.
5화는 Dapr 사이드카 박스를 엽니다.
6화는 첫 패킷부터 Pod까지 Envoy ingress 경로를 따라갑니다.

---

## 첫 번째 교정: Kubernetes가 안 보인다고 없는 것은 아닙니다

ACA를 볼 때 가장 흔한 실수는, 클러스터가 노출되지 않으니 Kubernetes를 머릿속에서 지워 버리는 일입니다.
그 추상화는 잘못된 출발점입니다.

어떤 형태로든 관리형 Kubernetes substrate는 있습니다.
다만 여러분이 운영하지 않을 뿐이고, Microsoft도 그 정확한 구현을 제품 표면에 공개하지 않습니다.

Microsoft 문서는 Environment를 하나 이상의 앱과 잡을 감싸는 secure boundary로 설명하고, 런타임이 OS 업그레이드, 스케일 작업, 장애 조치, 리소스 밸런싱을 처리한다고 적습니다.
이 표현은 중요합니다.
단순한 VM 묶음이 아니라, 오케스트레이터 계층 위에 제품 표면이 올라가 있음을 뜻하기 때문입니다.

AKS와 비교해 잃는 것은 직접 제어권입니다.

- 클러스터 API endpoint 직접 관리
- 노드 직접 접근
- 기저 제어면에 대한 `kubectl` 운영
- 임의의 클러스터 전역 add-on 설치

대신 여러분이 여전히 접하게 되는 것은 Kubernetes와 닮은 동작들입니다.

- 각 Revision 뒤에서 돌아가는 Pod류 런타임 단위
- Ingress와 Replica 사이의 Service성 홉이라는, Kubernetes 관점에서 가장 방어 가능한 추론
- 불변 스냅샷처럼 동작하는 Revision
- KEDA 기반 수평 스케일링
- Upstream 런타임 동작에 닻을 내린 Dapr 사이드카 통합
- Envoy 기반 Ingress와 트래픽 분할

이번 시리즈 전체는 이 관점을 유지한 채 읽어야 맞습니다.

---

## 더 단순한 모델: ACA는 여러 계층 위의 제품 표면입니다

스택은 층으로 나누면 훨씬 덜 복잡합니다.

![선언 계층과 런타임 번역 계층](../../../assets/azure-aca-deep-dive/01/01-02-a-simpler-model-aca-is-a-product-surface.ko.png)

*선언 계층과 런타임 번역 계층*
맨 위는 여러분이 선언하는 층입니다.
가운데는 그 선언이 실제 동작으로 바뀌는 층입니다.
맨 아래는 실행 자원이 놓인 인프라 층입니다.

ACA에서 예상 밖의 일이 벌어졌다면, 대개는 이 층 사이의 경계에서 설명됩니다.

- Environment 설정 하나가 그 안의 모든 앱 동작을 바꿉니다.
- Revision 범위 변경 하나가 새 불변 스냅샷을 만듭니다.
- Scale rule 하나가 KEDA 오브젝트와 HPA 동작으로 번역됩니다.
- Dapr 설정 하나가 사이드카 프로세스와 localhost 포트로 바뀝니다.
- Traffic split 하나가 Envoy route와 upstream cluster 가중치로 번역된다고 보는 편이 가장 설득력 있습니다.

---

## Environment는 무엇을 실제로 경계 짓는가

Environment는 보기 좋은 상위 리소스가 아닙니다.
실제 격리 경계입니다.

Microsoft 문서도 Environment를 하나 이상의 앱과 잡을 둘러싼 secure boundary라고 설명합니다.
같은 Environment 안의 앱은 같은 가상 네트워크 경계, 같은 로그 대상, 같은 Dapr 구성 표면을 공유합니다.

즉 Environment에서 다음 관심사가 현실이 됩니다.

- 네트워크 도달성
- DNS와 ingress 표면
- 공용 Log Analytics workspace
- Dapr component 범위
- 같은 Environment 안의 앱 간 service invocation

그래서 Environment 선택은 장식이 아니라 아키텍처 결정입니다.

![Environment가 묶는 네트워크·로그·Dapr 경계](../../../assets/azure-aca-deep-dive/01/01-03-what-the-environment-really-is.ko.png)

*Environment가 묶는 네트워크·로그·Dapr 경계*
서로 절대 같은 네트워크·로깅·Dapr 경계를 공유하면 안 되는 앱이라면 같은 Environment에 두면 안 됩니다.
반대로 같은 Dapr invocation 평면과 같은 관측 계층을 공유해야 한다면, Environment가 바로 그 묶음 단위입니다.

2화는 이 경계 하나만 깊게 다룹니다.

---

## Container App은 런타임에서 무엇으로 펼쳐지는가

Container App 자체가 최종 런타임 단위는 아닙니다.
그보다 Revision이 더 가깝습니다.

플랫폼은 앱 전역 설정과 Revision 템플릿성 설정을 분리해 다룹니다.
이미지, 컨테이너 템플릿, 스케일 규칙처럼 Revision 범위 설정을 바꾸면 새 Revision이 만들어집니다.
그 Revision은 불변입니다.

런타임 확장을 그리면 대략 다음과 같습니다.

![App·Revision·Replica로 이어지는 런타임 구조](../../../assets/azure-aca-deep-dive/01/01-04-what-a-container-app-becomes-at-runtime.ko.png)

*App·Revision·Replica로 이어지는 런타임 구조*
사용자 경험은 "앱을 업데이트했다"입니다.
런타임 현실은 "플랫폼이 새 불변 Revision 템플릿을 만들고, 그 스냅샷에 트래픽과 스케일 정책을 붙여 Replica를 띄웠다"에 가깝습니다.

그래서 ACA 운영에서는 Revision 사고방식이 중심입니다.

---

## Revision이 운영의 중심인 이유

많은 Azure 서비스에도 배포 이력은 있습니다.
ACA는 그 이력을 1급 개체로 다룹니다.

Revision은 기록만이 아닙니다.
실제로 주소를 갖고 살아 있는 단위입니다.

가능한 일은 다음과 같습니다.

- 한 번에 하나의 active revision만 유지
- 여러 revision 동시 실행
- revision 사이 ingress traffic 분할
- direct revision access용 label 부여
- 인프라 교체 대신 weight 이동으로 roll forward / rollback

그래서 ACA는 canary와 blue-green을 별도 설계 없이 제품 기능으로 제공합니다.

![Revision 중심 운영 제어 구조](../../../assets/azure-aca-deep-dive/01/01-05-revisions-are-the-operational-center-of.ko.png)

*Revision 중심 운영 제어 구조*
여기서 중요한 미묘함 하나.
트래픽 정책은 앱 바깥에서 보이지만, 스케일은 Revision 단위로 일어납니다.
이 분리가 롤아웃 동작 대부분을 설명합니다.

3화에서 이 부분을 자세히 봅니다.

---

## ScaledObject를 보지 못해도 KEDA를 알아야 하는 이유

ACA 스케일링은 선언형입니다.
Container App에 scale rule을 씁니다.
플랫폼이 나머지를 처리합니다.

하지만 그 엔진은 KEDA입니다.

Microsoft 문서도 Container Apps 스케일링이 KEDA 기반이라고 분명히 적습니다.
이 한 줄만으로도 어떤 기계를 상상해야 하는지가 정해집니다.

- 이벤트 기반 scale decision
- Revision 단위 min / max replica 제한
- scale-to-zero
- external metric을 거친 HPA류 판단

Custom rule은 대응이 비교적 직접적입니다.
ACA의 rule 의도가 KEDA scaler 의도로 번역된다고 보면 됩니다.
HTTP는 주의가 필요합니다.
ACA는 request concurrency 기반 built-in HTTP scaling을 노출합니다.
이 개념은 KEDA HTTP add-on과 닮았지만, ACA가 upstream `kedacore/http-add-on`을 1:1로 그대로 노출한다고 말하면 안 됩니다.
제품 표면은 ACA의 것입니다.

![ACA scale rule과 KEDA 번역 경로](../../../assets/azure-aca-deep-dive/01/01-06-why-keda-matters-even-if-you-never-see-a.ko.png)

*ACA scale rule과 KEDA 번역 경로*
4화가 이 블랙박스를 엽니다.

---

## ACA의 Dapr는 흉내 낸 API가 아닙니다

Dapr도 추상화 때문에 오해가 많습니다.

ACA는 Dapr 비슷한 API를 새로 만든 것이 아닙니다.
Upstream Dapr runtime을 통합하고, 그 관리 표면을 플랫폼에 맞게 제한한 것입니다.

가장 유용한 그림은 단순합니다.

- 앱에 Dapr를 켜면 Pod에 `daprd`류 사이드카가 붙는다고 이해하는 편이 맞습니다.
- 사용자 컨테이너는 localhost로 그 사이드카에 붙습니다.
- ACA 문서는 사이드카가 HTTP 3500, gRPC 50001 포트로 Dapr API를 노출한다고 설명합니다.
- Component는 Environment 수준에서 구성되고, Dapr scope에 따라 로드됩니다.

![앱 컨테이너와 daprd 사이드카 결합 구조](../../../assets/azure-aca-deep-dive/01/01-07-dapr-in-aca-is-not-a-mock-integration.ko.png)

*앱 컨테이너와 daprd 사이드카 결합 구조*
즉 실제로 옆에 붙는 사이드카 프로세스입니다.
제어면이 대신 흉내 내는 구조가 아닙니다.

5화에서는 injector와 Go 런타임 프로세스 자체를 따라갑니다.

---

## Envoy는 ingress가 실제 라우팅으로 바뀌는 지점입니다

Portal에서 보이는 ACA ingress 설정은 간단합니다.
실제 런타임 경로는 그렇지 않습니다.

HTTP ingress는 TLS 종료, HTTP/1.1·HTTP/2, gRPC, 안정적인 FQDN, session affinity, traffic splitting을 제공합니다.
이건 reverse proxy의 일입니다.
ACA에서 그 프록시 층을 이해하려면 Envoy를 머릿속에 두는 편이 맞습니다.

이번 시리즈에서 특히 중요한 점은 가중치가 어디에 적용되는가입니다.
Envoy 용어에서 cluster는 Kubernetes cluster가 아니라 upstream service target입니다.
ACA의 revision traffic split은 weighted upstream cluster 선택으로 설명하는 편이 가장 자연스럽지만, 이 역시 공개 구현 세부사항이 아니라 최선의 추론입니다.

![Ingress 설정과 Envoy 라우팅 연결](../../../assets/azure-aca-deep-dive/01/01-08-envoy-is-where-ingress-becomes-runtime-r.ko.png)

*Ingress 설정과 Envoy 라우팅 연결*
6화에서 이 경로를 처음 패킷부터 끝까지 따라갑니다.

---

## ACA의 control plane과 data plane을 나누어 보기

문제 분석 때 이 분리가 특히 유용합니다.

![ACA control plane과 data plane 분리](../../../assets/azure-aca-deep-dive/01/01-09-control-plane-versus-data-plane-in-aca.ko.png)

*ACA control plane과 data plane 분리*
새 Revision은 생겼는데 트래픽을 못 받는다면 대개 control plane 쪽 결정입니다.
트래픽은 들어오는데 앱 응답 전에 실패한다면 data plane 경로 문제일 가능성이 큽니다.
Scale rule은 있는데 replica가 0에 머문다면, 경계는 KEDA metric과 activation logic 근처입니다.

결국 이번 시리즈 전체는 이 경계들을 차례로 걷는 일입니다.

---

## 운영 관점에서 ACA와 AKS가 갈리는 지점

짧게 말하면 제어권입니다.

AKS에서는 클러스터 표면을 훨씬 더 많이 선택하고 운영합니다.
ACA에서는 Microsoft가 더 많은 결정을 대신 내려, 서버리스 컨테이너 계약을 유지합니다.

이 차이는 트러블슈팅 방식도 바꿉니다.

AKS에서는 native Kubernetes object를 직접 확인하는 경우가 많습니다.
ACA에서는 제품 기능, 로그, revision 상태, Dapr health, ingress 동작, scaling 결과를 통해 아래층 상태를 역으로 추론하는 경우가 많습니다.

ACA가 모호하다는 뜻은 아닙니다.
단지 디버깅 진입점이 다르다는 뜻입니다.

그래서 closed-source인 ACA 동작은 Microsoft Learn에 기대어 설명해야 하고, KEDA·Dapr·Envoy 동작은 pinned upstream source에 기대어 설명해야 합니다.

---

## 1화 정리

이번 글에서 한 모델만 남긴다면 이것입니다.

> Azure Container Apps는 정확한 substrate가 공개되지 않은 Microsoft 관리 Kubernetes 인프라 위의 관리형 제품 표면입니다. Environment는 격리 경계입니다. Revision은 불변 런타임 스냅샷입니다. KEDA는 스케일 엔진입니다. Dapr는 사이드카 런타임입니다. Envoy는 ingress와 가중치 라우팅 계층입니다.

뒤의 화들은 이 문장 안의 명사를 하나씩 실제 동작으로 바꿔 줍니다.

---

## 시리즈 안에서의 위치

이 1화는 Azure Container Apps Deep Dive 시리즈의 아키텍처 지도입니다. 제품 표면을 먼저 가볍게 잡고 싶다면 ACA 101 시리즈를 먼저 읽고, 제어면 관점 비교를 원한다면 AKS와 Azure Functions 심화 시리즈를 함께 보는 편이 좋습니다.

---

## Evidence Boundaries

이 장은 Microsoft 문서가 직접 말하는 제품 사실과, upstream 동작을 이용한 제한적 추론을 함께 사용합니다.

**Documented (Microsoft Learn / 1차 출처):**
- ACA는 Kubernetes와 KEDA·Dapr·Envoy 같은 오픈소스 기술 위에 구축되지만, 기저 Kubernetes API는 노출하지 않습니다.
- Environment는 앱과 잡을 감싸는 secure boundary이며, 네트워크·로깅·Ingress·Dapr 관련 표면이 여기서 묶입니다.
- Revision은 immutable snapshot이고, ACA 스케일링은 KEDA 기반입니다.

**Inferred from upstream behavior:**
- Revision traffic percentage는 Envoy weighted upstream selection으로 설명하는 편이 가장 설득력 있습니다.
- Dapr enablement는 upstream `daprd` 사이드카 런타임 모델로 이해하는 편이 맞습니다.
- Ingress와 Replica 사이의 Service성 홉은 숨은 데이터 평면을 설명하는 가장 방어 가능한 Kubernetes형 추론입니다.

**Speculation (ACA-internal, not exposed):**
- 정확한 Kubernetes substrate, 클러스터 토폴로지, 내부 오브젝트 이름은 공개되지 않았습니다.
- ACA 리소스를 Envoy·KEDA·Dapr 설정으로 바꾸는 private adapter 코드는 공개되지 않았습니다.

### environment와 그 안의 component를 한눈에 보기

```bash
az containerapp env show \
  --name my-env --resource-group my-rg \
  --query "{name:name, vnet:vnetConfiguration.infrastructureSubnetId, dapr:daprAIInstrumentationKey, workload:workloadProfiles[].name}"

az containerapp env workload-profile list \
  --name my-env --resource-group my-rg \
  -o table
```

## 운영 체크리스트

- [ ] environment 단위 책임 분담(Microsoft vs 우리 팀)을 ADR로 남겼다
- [ ] control plane 장애 시 데이터 플레인 영향 범위를 시뮬레이션해 봤다
- [ ] 동일 environment 내 앱들의 신뢰 경계를 검토했다
- [ ] managed component(KEDA, Dapr, Envoy) 버전 업그레이드 정책을 확인했다
- [ ] 환경 재생성이 필요한 변경(VNet, log workspace)을 사전에 분류했다

<!-- toc:begin -->
## 시리즈 목차

- **ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 (현재 글)**
- Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 (예정)
- Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 (예정)
- ACA 안의 KEDA — Scale Rule이 만드는 것 (예정)
- Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 (예정)
- Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (예정)

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [`kedacore/keda` tree at `v2.14.0`](https://github.com/kedacore/keda/tree/v2.14.0)
- [KEDA의 `ScaledObject` 타입](https://github.com/kedacore/keda/blob/v2.14.0/apis/keda/v1alpha1/scaledobject_types.go)
- [KEDA의 `ScaledObjectReconciler`](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/scaledobject_controller.go)
- [KEDA의 HPA 생성 코드](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/hpa.go)
- [`dapr/dapr` tree at `v1.13.0`](https://github.com/dapr/dapr/tree/v1.13.0)
- [`daprd` 진입점](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/main.go)
- [`daprd` 부팅 코드](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/app/app.go)
- [Dapr runtime 기본 포트와 설정](https://github.com/dapr/dapr/blob/v1.13.0/pkg/runtime/config.go)
- [Dapr injector의 pod patch](https://github.com/dapr/dapr/blob/v1.13.0/pkg/injector/service/pod_patch.go)
- [`Envoy` route 구성 at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/api/envoy/config/route/v3/route_components.proto)
- [`Envoy` router 구현 at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/source/common/router/config_impl.cc)

### 2차 출처
- [Comparing Container Apps with other Azure container options](https://learn.microsoft.com/en-us/azure/container-apps/compare-options)
- [Azure Container Apps environments](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Traffic splitting in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Microservice APIs Powered by Dapr](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Ingress in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
