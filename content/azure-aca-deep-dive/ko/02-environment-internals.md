---
title: "Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계"
series: azure-aca-deep-dive
episode: 2
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
seo_description: Container Apps Environment를 네트워크, 로그, Dapr 스코프를 함께 묶는 격리 경계로 읽고 분리 기준까지 정리합니다.
---

# Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계

1편에서 ACA의 큰 지도를 봤다면, 이제 그 지도에서 가장 바깥 경계를 먼저 확대해야 합니다. 겉으로는 관리용 상위 리소스처럼 보이지만, 실제로는 네트워크, 로그, Dapr 범위를 묶는 핵심 경계가 있기 때문입니다. 그 리소스가 바로 Container Apps Environment입니다.

Microsoft Learn이 Environment를 설명할 때 반복하는 문장이 있습니다. Environment는 하나 이상의 앱과 잡을 둘러싼 secure boundary라는 설명입니다. 이 한 문장을 제대로 읽으면, 왜 네트워크 범위가 여기서 정해지고, 왜 로그 대상이 여기서 묶이며, 왜 Dapr component가 앱이 아니라 Environment 수준에 놓이는지 동시에 이해할 수 있습니다.

이 글은 Azure Container Apps Deep Dive 시리즈의 두 번째 글입니다. 여기서는 Container Apps Environment를 네트워크, 관측, Dapr 스코프를 함께 결정하는 플랫폼의 격리 단위로 읽겠습니다.

이 경계를 먼저 이해해야 뒤의 Revision, KEDA, Dapr, Envoy 글도 제자리를 찾습니다. Revision은 Environment 바깥으로 나가지 못하고, Dapr component는 Environment 범위에서 로드되며, Ingress와 관측 역시 결국 같은 바깥 경계 안에서 작동하기 때문입니다.

이제 Environment를 “상위 폴더”가 아니라 “플랫폼 경계”로 보겠습니다.

![Azure Container Apps Deep Dive 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-01-the-environment-is-the-platform-s-isolat.ko.png)
*Azure Container Apps Deep Dive 2장 흐름 개요*
> Environment 내부 — 네트워크·관측·Dapr 스코프의 경계의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Environment는 왜 단순한 부모 리소스가 아니라 실제 격리 경계일까요?
- 네트워크 범위는 Revision이나 App이 아니라 왜 Environment에서 시작될까요?
- Log Analytics workspace를 Environment 수준에서 공유한다는 말은 운영상 무엇을 뜻할까요?

## 왜 이 글이 중요한가

Environment를 잘못 이해하면 ACA의 여러 기능을 제각각 따로 보게 됩니다. Ingress는 네트워크 기능, Dapr는 미들웨어 기능, 로그는 관측 기능, Revision은 배포 기능처럼 흩어져 보입니다. 하지만 실제 운영에서 이 기능들은 Environment라는 한 경계 안에서 얽혀 움직입니다. 이 사실을 놓치면 경계가 잘못 그어진 설계를 뒤늦게 수정하느라 큰 비용을 치를 수 있습니다.

특히 팀 경계와 신뢰 경계가 다른 워크로드를 한 Environment에 섞어 넣으면 나중에 제일 먼저 문제가 됩니다. 같은 로그 대상, 같은 Dapr component 카탈로그, 같은 네트워크 평면을 공유하는 것이 의도였는지 아닌지를 뒤늦게 묻게 되기 때문입니다. 많은 경우 이는 기능 문제가 아니라 경계 모델의 문제입니다.

또한 Environment는 이후 모든 런타임 이야기의 전제입니다. Revision도, Scale도, Dapr sidecar도 결국 이 경계 안에서만 의미를 갖습니다. 그래서 2편은 단지 “환경 리소스 소개”가 아니라 시리즈 전체의 운영 경계를 정하는 글입니다.

## 핵심 관점

Environment를 볼 때 가장 먼저 머리에 남겨야 할 문장은 이것입니다. **Environment는 ACA가 플랫폼처럼 동작하기 시작하는 지점이며, 네트워크·로그·Dapr 범위를 함께 묶는 격리 단위**입니다. 앱 하나를 호스팅하는 상자가 아니라, 여러 앱이 어떤 경계를 공유할지 정하는 플랫폼 단위에 가깝습니다.

이 관점이 실용적인 이유는, 앱 단위에서 할 수 있는 선택과 Environment 단위에서 이미 결정된 선택을 분리해 주기 때문입니다. 예를 들어 앱마다 ingress를 켜거나 끌 수는 있지만, 그것이 놓이는 네트워크 perimeter는 Environment에 속합니다. 앱마다 Dapr enablement는 다를 수 있지만, component registry의 경계는 Environment에 속합니다.

즉 Environment는 “무엇을 공유할 것인가”를 정하는 바깥 계약입니다. 그 안에서 개별 앱과 Revision이 자기 런타임 행동을 가집니다. 이 순서를 거꾸로 이해하면 설계가 자꾸 엇나갑니다.

> ACA에서 Environment는 배포 편의용 컨테이너가 아니라, 네트워크와 관측과 Dapr 정책이 동시에 걸리는 플랫폼의 바깥 경계입니다.

## 핵심 개념

### Environment는 공유 경계의 시작점입니다

같은 Environment 안의 앱은 여러 플랫폼 면을 공유할 수 있습니다. 가상 네트워크 경계, DNS suffix, Log Analytics 대상, Dapr component registry, 환경 내부 서비스 도달성이 대표적입니다. Environment 밖의 앱은 이 경계를 자동으로 공유하지 않습니다.

운영상 의미는 단순합니다. 두 앱이 같은 장애 반경과 관측 경계를 공유해도 된다면 하나의 Environment가 합리적일 수 있습니다. 반대로 네트워크, 로그, Dapr 구성 경계를 분리해야 한다면 Environment부터 나누는 편이 맞습니다.

### 네트워크 범위는 Revision이 아니라 Environment에서 시작합니다

Revision은 런타임 스냅샷이지 네트워크 섬이 아닙니다. ACA에서 네트워크 경계는 Environment 수준의 결정입니다. Microsoft 문서도 각 Environment가 managed VNet 또는 사용자 제공 VNet에 기대어 동작한다고 설명합니다. 따라서 내부 서비스 도달성과 ingress posture는 앱 설정 이전에 Environment 설정입니다.

![Per-app ingress choices inside one environment](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-02-network-scope-begins-at-the-environment.ko.png)

*Per-app ingress choices inside one environment*

앱마다 ingress on/off, external/internal 선택은 다를 수 있습니다. 하지만 그 선택이 놓이는 네트워크 perimeter는 여전히 하나의 Environment입니다. 그래서 동일 Environment를 “서로 절대 만나면 안 되는 내부 mesh”에 쓰려는 시도는 설계 단계에서 다시 봐야 합니다.

### External ingress와 internal ingress도 같은 Environment 표면 위에 있습니다

외부 공개 앱 하나와 내부 전용 앱 여러 개를 함께 두는 패턴은 ACA에서 자연스럽습니다. 공용 Ingress 앱은 인터넷과 Environment 양쪽에 열고, 내부 앱은 Environment 안에서만 열 수 있습니다. 이 조합은 north-south와 east-west 트래픽을 제품이 미리 배선해 준다는 장점이 있습니다.

![External and internal ingress within one environment](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-03-external-versus-internal-ingress-still-s.ko.png)

*External and internal ingress within one environment*

하지만 이 편의는 동시에 제약입니다. 같은 Environment 안에 넣는 순간 네트워크 경계의 가장 중요한 단위는 개별 앱보다 Environment가 됩니다. 즉 “앱 하나만 내부 전용이면 충분한가”가 아니라 “이 앱들이 같은 Environment에 있어도 되는가”를 먼저 물어야 합니다.

### DNS 맥락도 Environment가 결정합니다

ACA는 각 앱에 FQDN을 주지만, 그 FQDN은 Environment의 DNS suffix와 naming context 위에 놓입니다. 이 때문에 앱을 다른 Environment로 옮기는 일은 단순한 placement 변경이 아니라 네트워크 정체성 변경입니다.

같은 Environment 안에서는 앱 endpoint, Revision label, app FQDN이 공통 naming context를 공유합니다. 그래서 multi-app 통신이나 rollout 시 direct URL 전략을 설계할 때 Environment는 폴더가 아니라 이름 체계의 일부가 됩니다.

### 관측은 Environment 경계에서 중앙화됩니다

Environment 문서는 `appLogsConfiguration`이 Environment-level property라고 설명합니다. 즉 같은 Environment 안의 앱은 같은 logging destination으로 로그를 보냅니다. 덕분에 cross-app troubleshooting이 하나의 workspace 안에서 이어지지만, 동시에 telemetry governance 결정도 Environment 수준에서 일어납니다.

![Environment-level shared observability boundary](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-04-observability-is-centralized-at-the-envi.ko.png)

*Environment-level shared observability boundary*

이 구조가 좋은 이유는 여러 서비스를 한 workspace에서 읽을 수 있기 때문입니다. 하지만 retention, access control, cost accounting을 분리해야 한다면 Environment 분리가 더 깔끔한 해결책일 수 있습니다.

### 같은 workspace를 쓴다고 모든 신호가 같은 것은 아닙니다

여기서 흔한 과잉 보정이 나옵니다. Environment가 workspace를 공유하니 모든 신호도 Environment 수준이라고 생각하는 것입니다. 그렇지 않습니다. Environment는 “어디로 보낼지”를 정하고, App·Revision·Dapr sidecar·Ingress 경로는 “무엇을 보낼지”를 결정합니다.

![Shared workspace and per-runtime signal sources](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-05-shared-logs-do-not-mean-all-signals-are.ko.png)

*Shared workspace and per-runtime signal sources*

즉 Environment는 collector boundary이고, 실제 producer는 런타임 단위들입니다. 이 구분을 알아야 여러 앱이 섞인 workspace에서 플랫폼 노이즈와 특정 Revision 문제를 분리해 읽을 수 있습니다.

### Dapr component는 앱보다 먼저 Environment 리소스입니다

ACA의 Dapr 통합은 Environment 범위를 가장 명확하게 보여 줍니다. Dapr component는 앱 리소스가 아니라 Environment 리소스이며, 그 위에 scope를 통해 특정 Dapr app ID에만 로드되도록 제한할 수 있습니다.

![Environment-scoped components and app-level consumers](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-06-dapr-components-are-environment-resource.ko.png)

*Environment-scoped components and app-level consumers*

따라서 component를 볼 때는 두 질문을 함께 해야 합니다. 첫째, 이 component는 어느 Environment에 존재하는가. 둘째, 그 Environment 안의 어떤 Dapr-enabled 앱이 이 component를 로드할 수 있는가. shared infra를 모델링할 때 이 두 단계가 매우 중요합니다.

### Scope는 Container App 이름이 아니라 Dapr app ID에 대응합니다

프로덕션에서 자주 헷갈리는 지점입니다. Component scope는 Container App 리소스 이름이 아니라 Dapr app ID와 연결됩니다. Azure 리소스 정체성과 Dapr 정체성은 관련은 있지만 같은 개념이 아닙니다.

![Dapr app ID to component scope mapping](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-07-scope-means-dapr-app-id-not-container-ap.ko.png)

*Dapr app ID to component scope mapping*

예상한 component가 어떤 앱에서 로드되지 않는다면, 가장 먼저 확인해야 할 것 중 하나가 이 매핑입니다. 정의는 Environment에 있고, 실제 로딩 여부는 Dapr scope가 결정합니다.

### Environment는 Dapr가 정책이 되는 지점입니다

Raw Kubernetes 위의 upstream Dapr에서는 component, configuration, injector, app ID를 더 직접적으로 다룹니다. ACA에서는 sidecar 동작은 upstream Dapr와 닮았지만, 관리 표면은 더 좁습니다. 이 축소가 바로 Environment 수준에서 일어납니다.

- Component는 Environment에 붙습니다.
- 제품이 지원하는 component 유형은 curated surface로 제공됩니다.
- 앱은 Dapr를 켜고, scope가 허용한 component만 로드합니다.

즉 Environment는 단순 저장 위치가 아니라 shared middleware가 정책으로 바뀌는 지점입니다.

### Cross-app Dapr communication도 Environment 안에서 가장 자연스럽습니다

여러 앱이 built-in Dapr service invocation으로 통신해야 한다면 같은 Environment가 자연스러운 선택입니다. 반대로 두 서비스가 같은 Dapr communication plane을 공유하면 안 된다면 Environment 분리가 더 명확한 경계가 됩니다.

![Cross-app Dapr calls inside one environment](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-08-cross-app-dapr-communication-only-makes.ko.png)

*Cross-app Dapr calls inside one environment*

핵심은 우회 방법의 존재 여부가 아닙니다. 제품이 어떤 신뢰 경계와 네트워크 구성을 기본값으로 여기는가를 읽는 것입니다. ACA는 이 통신을 Environment 내부의 기본 패턴으로 취급합니다.

### 비용과 운영도 결국 Environment 선택의 일부입니다

하나의 Environment를 쓰면 shared observability, shared Dapr management, internal communication, deployment target 수를 단순화할 수 있습니다. 여러 Environment를 쓰면 blast radius, production/non-production separation, telemetry ownership, network segmentation, Dapr config isolation을 더 쉽게 가져갈 수 있습니다.

![Shared control loops terminating at environment boundary](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/02/02-09-control-loops-that-terminate-at-the-envi.ko.png)

*Shared control loops terminating at environment boundary*

이 그림의 중요한 점은 중심에 단일 Revision이 없다는 것입니다. Environment는 하나의 런타임 객체가 아니라, 여러 앱에 동시에 제약과 공유 자원을 배포하는 control surface입니다. 그래서 강력하지만, 잘못 그으면 위험합니다.

### 아키텍트가 바로 써먹을 수 있는 경계 테스트

두 앱을 같은 Environment에 넣어도 되는지 애매할 때는 기능 목록보다 경계 질문을 먼저 던지는 편이 좋습니다. 저는 보통 네 가지를 묻습니다. 같은 네트워크 boundary를 공유해도 되는가, 같은 Log Analytics destination에 쌓여도 되는가, 같은 Dapr component catalog를 공유해도 되는가, built-in internal communication이 자연스러운가입니다.

네 질문 모두에 예라고 답할 수 있다면 shared Environment가 충분히 방어 가능합니다. 반대로 답이 갈리기 시작한다면 이미 경계가 잘못 그어지고 있을 가능성이 큽니다. 이때 앱별 ingress 옵션이나 개별 component scope로만 해결하려 들면 나중에 더 큰 복잡도를 떠안게 됩니다.

### outbound path와 IP도 Environment 수준 계약입니다

외부 시스템과 연결할 때 많은 팀이 앱 기준으로 allowlist를 생각합니다. 하지만 ACA에서는 outbound path와 static IP 같은 속성도 Environment 경계에서 읽어야 합니다. 이 말은 방화벽 등록, 외부 SaaS allowlist, 파트너 연동 문서가 앱 단위가 아니라 Environment 단위로 정리되어야 한다는 뜻이기도 합니다.

운영상 이 관점은 아주 현실적입니다. 동일 Environment 안의 여러 앱이 같은 outbound identity를 공유할 수 있기 때문입니다. 따라서 어떤 앱 하나의 변경이 아니라, Environment 수준 변경이 여러 서비스의 외부 통신에 동시에 영향을 줄 수 있습니다.

### 이후의 Revision·KEDA·Dapr·Ingress도 이 경계 안에서만 읽힙니다

Environment 이해가 중요한 또 다른 이유는 뒤의 모든 동작이 이 경계 밖으로 나가지 못하기 때문입니다. Revision은 Environment 바깥의 네트워크 정체성을 새로 만들지 않고, KEDA는 Environment 안의 replica 집합을 조절하며, Dapr sidecar는 Environment component catalog를 참조하고, Ingress는 결국 Environment 경계 안의 endpoint를 향합니다.

즉 Environment는 나중에 다시 잊어도 되는 서론이 아닙니다. 뒤의 기능 설명을 계속 묶어 주는 공통 외곽선입니다. 이 공통 외곽선을 놓치면 각 기능이 독립 옵션처럼 보이고, 운영 설계가 자꾸 조각납니다.

### production과 non-production을 나눌 때도 가장 먼저 보는 경계

팀들이 흔히 하는 질문 중 하나는 “dev와 prod를 같은 Environment에 둘 수 있나”입니다. 기술적으로 가능한 조합을 묻는 것보다, 같은 네트워크·로그·Dapr 경계에 묶이는 것이 괜찮은지를 먼저 물어야 합니다. 대부분의 프로덕션 환경에서는 운영 책임, 접근 제어, 장애 반경, 비용 추적이 다르기 때문에 분리된 Environment가 더 자연스럽습니다.

반대로 매우 작은 실험 환경이나 교육용 워크로드라면 하나의 Environment가 운영 단순성을 줄 수 있습니다. 핵심은 가능 여부가 아니라 경계 의도가 분명한가입니다. Environment는 나중에 수정하기 쉬운 cosmetic choice가 아니라, 초기 설계의 기본 선입니다.

### 관측 평면을 공유한다는 말은 팀 경계도 공유한다는 뜻일 수 있습니다

같은 workspace에 로그가 쌓인다는 것은 기술적 편의 이상을 의미합니다. 누가 어떤 로그를 볼 수 있는지, 어떤 retention 정책을 적용하는지, 비용을 어느 팀에 귀속할지까지 함께 연결되기 때문입니다. 그래서 observability boundary를 소홀히 보면, 나중에 보안과 운영 소유권 이슈가 한꺼번에 드러납니다.

저는 Environment를 정할 때 네트워크와 Dapr만큼이나 observability ownership을 같이 봐야 한다고 생각합니다. 같은 workspace를 공유해도 되는 팀과 워크로드인지 먼저 답하지 못한다면, Environment 경계도 다시 검토하는 편이 안전합니다.

### 운영자가 먼저 확인할 정보

아래 명령은 Environment의 IP, workload profile, outbound path를 확인하는 기본 점검입니다.

```bash
az containerapp env show -n my-env -g my-rg \
  --query "{infraSubnet:vnetConfiguration.infrastructureSubnetId, internal:vnetConfiguration.internal, staticIp:staticIp, outbound:vnetConfiguration.outboundType}"

az containerapp env workload-profile list -n my-env -g my-rg -o table
```

이 출력은 단순 정보 조회가 아닙니다. subnet 여유, 내부/외부 posture, static IP, outbound type, workload profile이 모두 Environment 경계에서 결정되는 운영 속성이라는 사실을 다시 보여 줍니다.

같은 리소스 그룹 안의 앱들이 실제로 어느 경계를 공유하는지도 바로 확인할 수 있습니다.

```bash
az containerapp list -g my-rg \
  --query "[].{app:name, env:properties.managedEnvironmentId, external:properties.configuration.ingress.external}" \
  -o table
```

**Expected output:**

- 같은 `env` 값을 가진 앱은 같은 Environment 경계 안에 있습니다.
- `external` 값이 달라도 네트워크 바깥 경계가 자동으로 분리되는 것은 아닙니다.
- 같은 Environment인데 분리 의도가 강한 앱이 섞여 있다면, ingress 설정이 아니라 Environment 설계를 다시 봐야 합니다.

이 표 한 장만 봐도 “앱마다 설정이 다르다”와 “플랫폼 경계가 다르다”를 구분할 수 있습니다. Environment를 폴더가 아니라 실제 경계로 읽어야 하는 이유가 여기에 있습니다.

## 흔히 헷갈리는 지점

- **Environment는 앱을 묶는 폴더가 아닙니다.** 네트워크, 로그, Dapr를 공유하는 플랫폼 경계입니다.
- **Ingress를 앱마다 나눌 수 있어도 네트워크 경계는 자동으로 분리되지 않습니다.** 그 바깥 경계는 여전히 Environment입니다.
- **같은 workspace를 쓴다고 모든 로그 해석이 Environment 수준인 것은 아닙니다.** 신호 생산자는 App·Revision·sidecar입니다.
- **Dapr component scope는 Container App 이름이 아니라 Dapr app ID에 대응합니다.** 이 매핑을 틀리면 로딩이 어긋납니다.
- **Environment 통합은 편의 기능이 아니라 신뢰 경계 선택입니다.** 나중에 분리하기 어렵기 때문에 처음 설계가 중요합니다.

## 운영 체크리스트

- [ ] subnet 크기와 예상 replica 수 사이의 안전 여유를 계산했습니다.
- [ ] outbound IP를 downstream 방화벽과 allowlist에 등록했습니다.
- [ ] Log Analytics workspace 변경이 RPO/RTO에 주는 영향을 검토했습니다.
- [ ] workload profile별 비용과 격리 trade-off를 표로 정리했습니다.
- [ ] internal/external ingress 결정이 DNS 전략과 일관되는지 확인했습니다.

## 정리

Environment는 ACA에서 가장 과소평가되기 쉬운 리소스이지만, 실제로는 가장 강한 아키텍처 경계입니다. 네트워크 범위, DNS 맥락, logging destination, Dapr component registry가 모두 여기서 묶입니다. 그래서 Environment를 잘못 그리면 나중에 앱 단위 설정으로는 해결되지 않는 문제가 생깁니다.

또한 Environment는 뒤의 모든 런타임 주제를 위한 공통 배경입니다. Revision은 이 경계 안에서만 살아 있고, KEDA는 이 경계 안의 Replica를 늘리고 줄이며, Dapr sidecar는 이 경계의 component catalog를 읽고, Ingress는 이 경계 안의 앱 endpoint로 요청을 보냅니다.

다음 글에서는 이 Environment 경계 안에서 가장 운영 체감이 큰 단위인 Revision으로 들어갑니다. 불변 스냅샷, 활성 Revision, label, weighted traffic이 어떻게 하나의 rollout 모델을 이루는지 보겠습니다.

## 처음 질문으로 돌아가기

- **Environment는 왜 단순한 부모 리소스가 아니라 실제 격리 경계일까요?**
  - 본문의 기준은 Environment 내부 — 네트워크·관측·Dapr 스코프의 경계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **네트워크 범위는 Revision이나 App이 아니라 왜 Environment에서 시작될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Log Analytics workspace를 Environment 수준에서 공유한다는 말은 운영상 무엇을 뜻할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps Deep Dive (1/6): ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- **Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 (현재 글)**
- Azure Container Apps Deep Dive (3/6): Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 (예정)
- Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것 (예정)
- Azure Container Apps Deep Dive (5/6): Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 (예정)
- Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Azure Container Apps environments](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Ingress in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Microservice APIs Powered by Dapr](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/02-environment-internals)

Tags: Container Apps, KEDA, Dapr, Envoy
