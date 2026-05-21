---
title: "Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated"
series: azure-functions-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-05-12'
seo_description: 배포 장에서는 함수를 Flex Consumption에 올렸습니다. 그 경로가 현재 새 서버리스 앱의 기본 후보에 가장
  가깝기 때문입니다.
---

# Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated

배포 글에서는 Azure Functions를 **Flex Consumption** 기준으로 만들었습니다. 현재 Microsoft의 권장 방향에서 새 서버리스 앱의 기본 후보가 여기에 가장 가깝기 때문입니다. 그렇다고 해서 classic Consumption이나 Premium, Dedicated를 몰라도 된다는 뜻은 아닙니다. 실제 선택은 언제나 워크로드, 운영 제약, 성능 요구사항, 네트워크 요구사항을 같이 봐야 하기 때문입니다.

처음 Azure Functions를 접하면 “서버리스니까 자동으로 늘어나고, 쓰는 만큼만 돈을 낸다” 정도로 기억하기 쉽습니다. 하지만 이 문장은 플랜 선택 단계에서 너무 약합니다. 어떤 플랜은 scale to zero가 강점이고, 어떤 플랜은 warm capacity를 미리 확보하는 데 돈을 쓰며, 어떤 플랜은 아예 App Service 운영 모델에 더 가깝습니다. 같은 Functions라도 **운영 자세 자체가 달라지는 것**입니다.

이 글은 Azure Functions 101 시리즈의 다섯 번째 글입니다. 여기서는 Consumption, Flex Consumption, Premium, Dedicated(App Service Plan)를 제품 이름이 아니라 **운영 trade-off가 다른 호스팅 모델**로 비교합니다. 목표는 단순합니다. 가격표를 외우는 것이 아니라, 내 워크로드에 어느 플랜이 맞는지 빠르게 판단할 기준을 만드는 것입니다.

특히 이번 장에서는 현재 공식 권장 방향도 그대로 반영하되, 그 문장을 그대로 외우는 대신 제약까지 함께 보겠습니다. “새 앱은 Flex부터 본다”는 말은 맞지만, Blob trigger 제약, Linux 전용, 기능 차이 같은 단서가 빠지면 실무에서는 오히려 오판이 됩니다.

이제 Azure Functions 플랜을 마케팅 이름이 아니라 비용·성능·네트워크·운영 방식의 조합으로 읽어 보겠습니다.

![Azure Functions 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/05/05-01-big-picture.ko.png)
*Azure Functions 101 5장 흐름 개요*
> 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 각 플랜은 정확히 무엇을 기준으로 과금하고 무엇을 제약할까요?
- 플랜 선택에서 가격보다 콜드 스타트 허용 범위가 먼저 중요해지는 경우는 언제일까요?
- VNet 통합, Always Ready 같은 플랫폼 기능은 어떤 플랜 선택을 사실상 강제할까요?

## 왜 이 글이 중요한가

플랜 선택은 Azure Functions에서 가장 과소평가되기 쉬운 초기 결정입니다. 코드는 나중에도 바꿀 수 있지만, 플랜이 잘못 맞춰져 있으면 콜드 스타트, 네트워크 제약, 기능 지원 범위, 비용 구조가 전부 뒤에서 문제로 돌아옵니다. 특히 새 프로젝트일수록 “지금 편한가”보다 “몇 달 뒤 운영이 어디서 막힐까”를 먼저 봐야 합니다.

또한 같은 서버리스라고 해도 운영 감각은 플랜마다 꽤 다릅니다. Consumption과 Flex Consumption은 scale to zero와 실행 기반 과금이 중심이고, Premium은 warm capacity를 비용으로 사는 모델에 가깝고, Dedicated는 Functions 프로그래밍 모델을 App Service 위에서 운영하는 성격이 강합니다. 이 차이를 모르고 “Functions니까 다 비슷하다”고 접근하면, 기대한 자동 스케일이 안 보이거나 비용 모델이 예상과 달라지는 일이 흔합니다.

무엇보다 이 장은 다음 글의 스케일링과 콜드 스타트 설명을 위한 전제입니다. 어떤 플랜을 골랐는지에 따라 첫 요청 지연을 어떻게 읽어야 하는지, 인스턴스가 어떤 식으로 늘어나는지, warm capacity를 어디서 어떻게 확보할 수 있는지가 달라집니다. 즉 플랜 선택은 제품 비교가 아니라, 이후 운영 현상을 읽기 위한 해석 프레임입니다.

## 핵심 관점

Azure Functions 플랜은 “더 싸다/더 비싸다”로만 보면 거의 항상 틀립니다. 더 정확한 질문은 세 가지입니다. **비용이 무엇을 기준으로 붙는가, warm capacity를 미리 유지할 수 있는가, 스케일과 네트워크와 배포가 어떤 운영 모델을 따르는가**입니다. 이 세 가지를 함께 봐야 실제 선택이 가능합니다.

예를 들어 Consumption은 가장 단순한 종량제이지만 콜드 스타트와 VNet 제약이 있습니다. Flex Consumption은 새 서버리스 앱의 기본 후보이지만 Linux 전용이고 일부 기능 차이가 있습니다. Premium은 첫 요청 지연을 더 강하게 통제할 수 있지만 warm baseline 비용이 생깁니다. Dedicated는 예측 가능한 고정 비용과 App Service 통합이 장점이지만, 이벤트 기반 서버리스 스케일 감각은 약해집니다.

즉 좋은 플랜 선택은 “서버리스니까 당연히 Consumption 계열” 같은 반사적 판단이 아니라, **내 워크로드가 어떤 제약을 먼저 만족해야 하는지 순서를 정하고 후보를 지우는 과정**에 가깝습니다. OS, VNet, 콜드 스타트 허용 범위, 스케일 방식, 비용 구조를 차례로 보면 훨씬 덜 흔들립니다.

> Azure Functions 플랜 선택의 핵심은 가장 싼 플랜을 찾는 것이 아니라, 워크로드가 감당할 수 없는 제약을 가진 플랜을 먼저 제거하는 것입니다.

## 핵심 개념

### 네 가지 플랜을 한 줄씩 정의합니다

| 플랜 | 한 줄 정의 |
|---|---|
| **Consumption** | 원래의 종량제 서버리스 플랜입니다. 기존 앱에는 여전히 중요하지만, 신규 앱 기준으로는 이제 레거시 경로에 가깝습니다. |
| **Flex Consumption** | Microsoft가 새 서버리스 앱의 기본 후보로 권장하는 Linux 기반 종량제 플랜입니다. VNet, 메모리 선택, per-function scaling이 핵심입니다. |
| **Premium** | warm capacity를 유지해 콜드 스타트를 줄이거나 회피하는 고급 서버리스 플랜입니다. |
| **Dedicated (App Service Plan)** | Functions를 일반 App Service 인프라 위에서 운영하는 모델입니다. |

이 표만 보면 간단해 보이지만, 실제 판단은 다음 비교표에서 갈립니다.

### 한 화면 비교표가 가장 빠릅니다

| 항목 | Consumption | Flex Consumption | Premium | Dedicated |
|---|---|---|---|---|
| **현재 위치** | 신규 앱 기준 레거시 경로 | 새 서버리스 기본 후보 | 고급 서버리스 | 일반 App Service 계열 |
| **과금 모델** | 실행 기준 종량제 | 실행 기준 종량제 + Always Ready가 있으면 그 용량도 과금 | 인스턴스 시간 + 실행 용량 | App Service Plan SKU 기준 |
| **트래픽 0일 때 비용** | 0 | Always Ready가 0이면 0 | 최소 인스턴스 비용 발생 | 항상 발생 |
| **콜드 스타트** | 있음 | Always Ready로 줄일 수 있음 | 대체로 회피 가능 | 상시 실행이면 사실상 없음 |
| **OS** | Windows 지원. Linux Consumption은 Retired 상태 | Linux 전용 | Windows / Linux | Windows / Linux |
| **VNet 통합** | 없음 | 있음 | 있음 | 있음 |
| **최대 인스턴스 수** | 대략 200, 조건에 따라 더 낮을 수 있음 | 앱 기본값 100, 최대 1000까지 구성 가능. 여전히 지역별 250코어 기본 쿼터 영향 가능 | 대략 20~100+, 조건에 따라 달라짐 | App Service Plan SKU와 autoscale 설정에 따름 |
| **이벤트 기반 자동 스케일** | 지원 | 지원 (per-function, target-based) | 지원 | App Service autoscale 규칙 기반 |
| **Per-function scaling** | 없음 | 있음 | 없음 | 없음 |
| **인스턴스 메모리** | 1.5 GB 고정 | 512 / 2048 / 4096 MB 선택 | SKU별 상이 | App Service Plan SKU 기준 |
| **배포 슬롯** | 제한적 | 없음, rolling update 경로만 있음 (preview, 프로덕션 비권장) | 있음 | 있음 |
| **Warmup 트리거** | 없음 | 있음 | 있음 | 있음 |

이 표를 볼 때는 비용보다 먼저 **OS, VNet, 스케일 방식**을 보는 편이 좋습니다. 실제로는 이 세 조건에서 후보가 빨리 갈리는 경우가 많습니다.

실무에서는 이 표를 "최종 결정표"로 쓰기보다 "탈락표"로 씁니다. 예를 들어 Windows가 필수면 Flex는 바로 탈락이고, VNet이 필수인데 classic Consumption을 보고 있다면 역시 즉시 탈락입니다. 이렇게 1차 필터를 통과한 1~2개 후보만 비용과 운영 난이도로 비교해야 결정이 빨라집니다.

아래는 실제 회의에서 자주 쓰는 1차 필터 표입니다.

| 질문 | Yes일 때 우선 후보 | No일 때 우선 후보 |
|---|---|---|
| Windows 런타임이 필요한가? | Premium / Dedicated | Flex Consumption |
| VNet 통합이 필수인가? | Flex / Premium / Dedicated | Consumption 포함 가능 |
| 첫 요청 지연을 강하게 통제해야 하는가? | Premium (또는 Flex + Always Ready) | Flex / Consumption |
| 이벤트 기반 자동 스케일이 핵심인가? | Flex / Consumption / Premium | Dedicated도 가능 |
| 슬롯 기반 배포가 필수인가? | Premium / Dedicated | Flex도 검토 가능 |

### Consumption: 가장 단순하지만 이제는 기본 출발점이 아닙니다

Consumption은 설명하기 쉽습니다. 호출이 없으면 거의 비용이 없고, 구조도 단순합니다. 다만 신규 앱의 기본 출발점으로 보기에는 제약이 분명합니다.

**선택 기준**

- 가장 단순한 데모, 실험, PoC가 필요합니다.
- Windows 제약이 있습니다.
- VNet 통합이 필요 없습니다.
- 첫 호출 지연을 어느 정도 받아들일 수 있습니다.

주요 약점

- 콜드 스타트
- VNet 통합 부재
- 1.5 GB 고정 메모리
- 신규 앱 기준으로는 이미 레거시 경로라 장기적 플랫폼 방향의 중심이 아닙니다.
- Linux Consumption이 Retired 상태라 새 Linux 아키텍처의 선택지로 보기 어렵습니다.

즉 Consumption은 여전히 유효하지만, “아무 제약 없는 새 서버리스 앱의 당연한 기본값”은 아닙니다. 현재 기준에서는 먼저 Flex를 보고, 필요 시 Consumption으로 내려오는 흐름이 더 자연스럽습니다. 신규 앱에서는 classic Consumption을 중립적 기본값이 아니라, 의도를 갖고 선택하는 레거시 분기로 보는 편이 정확합니다.

운영에서는 이 순서가 생각보다 중요합니다. 기본 후보를 하나 정해 두고 예외를 문서화하면 팀 안에서 플랜 선택 논의가 훨씬 빨라집니다. 반대로 모든 플랜을 항상 동등한 출발점으로 놓으면 작은 차이를 계속 비교하다가 중요한 제약을 놓치기 쉽습니다.

### Flex Consumption: 새 서버리스 앱의 기본 후보입니다

Flex Consumption은 현재 Azure Functions에서 가장 먼저 검토해야 할 새 서버리스 플랜입니다. Consumption의 경제성을 유지하면서도, 실무에서 자주 걸리던 제약을 꽤 많이 완화했습니다.

**핵심 차별점**

- **VNet 통합** 가능
- **메모리 크기 선택** 가능
- **Always Ready** 사용 가능
- **Per-function scaling** 지원
- **앱 기본 최대 100 인스턴스**, 필요 시 최대 1000까지 구성 가능

하지만 강점만 보면 안 됩니다.

**중요한 제약**

- **Linux 전용**입니다.
- **Blob trigger는 Event Grid 기반만 지원**합니다.
- **일부 바인딩과 기능 차이**가 있습니다.
- **배포 슬롯이 없고 rolling update 경로만 있지만, 이 경로는 아직 preview이며 프로덕션에는 권장되지 않습니다.**
- **스케일은 함수별 완전 독립이 아니라 scale group 단위**로 이해해야 합니다.

즉 Flex는 “Consumption의 약점을 거의 다 고친 플랜”이라고 볼 수는 있어도, “제약이 없는 만능 기본값”으로 보면 위험합니다. 기본 후보라는 말과 무조건 정답이라는 말은 다릅니다. 특히 프로덕션 배포에서 성숙한 슬롯 교체 워크플로가 필요하다면, Flex의 rolling update 경로를 동급 대안으로 보지 말고 Premium이나 Dedicated 요구사항으로 분류하는 편이 안전합니다.

### Premium: 콜드 스타트 제어와 Windows 요구사항이 같이 중요할 때

Premium은 warm capacity를 미리 유지하는 방식으로 접근합니다. 호출이 없어도 비용이 들지만, 대신 첫 요청 지연과 갑작스러운 부하 반응을 더 강하게 통제할 수 있습니다.

**선택 기준**

- 첫 요청 지연이 비즈니스적으로 허용되지 않습니다.
- Windows와 VNet을 동시에 써야 합니다.
- 더 큰 CPU/메모리 SKU가 필요합니다.
- 여러 Function App을 같은 Premium Plan에 묶고 싶습니다.

주요 약점

- 최소 인스턴스 비용이 남습니다.
- Linux 신규 앱이라면 Flex와 비교 검토가 거의 필수입니다.
- 실제 최대 인스턴스 수는 OS·지역·네트워크에 따라 달라집니다.

Premium은 순수 종량제라기보다, **Functions의 운영 모델을 유지하면서 성능 예측 가능성을 더 사는 플랜**에 가깝습니다.

콜드 스타트 완화 관점에서 보면 Premium과 Flex(Always Ready)는 비슷해 보이지만, 운영 결은 다릅니다. Premium은 최소 인스턴스를 명시적으로 유지하는 전통적인 접근이고, Flex는 서버리스 경제성을 최대한 유지하면서 필요한 함수 경로만 예열하는 접근에 가깝습니다. 따라서 "전체 앱을 넓게 예열할지", "핵심 함수 경로만 예열할지"를 기준으로도 판단할 수 있습니다.

그래서 Premium은 “돈을 더 쓰면 더 좋다”가 아니라 “예측 가능한 warm baseline이 꼭 필요한가”를 묻는 선택입니다. 이 질문이 명확하지 않으면 Premium 비용은 쉽게 과하게 느껴지고, 반대로 이 질문이 명확하면 비용의 이유도 비교적 분명해집니다.

### Dedicated: Functions를 App Service 방식으로 운영합니다

Dedicated(App Service Plan)는 이름보다 행동을 보는 편이 이해가 쉽습니다. 이 플랜은 **Functions를 App Service Plan 위에서 돌리는 모델**입니다. 즉 프로그래밍 모델은 Functions이지만, 운영 방식은 App Service에 더 가깝습니다.

**선택 기준**

- 이미 App Service Plan 여유 용량이 있습니다.
- 다른 웹 앱과 같은 인프라에 놓고 싶습니다.
- 비용을 고정적으로 보고 싶습니다.
- 이벤트 기반 플랫폼 스케일이 필수는 아닙니다.

가장 큰 trade-off는 분명합니다. **Consumption/Flex/Premium 같은 방식의 이벤트 기반 서버리스 스케일은 기대하면 안 됩니다.** App Service autoscale 규칙을 직접 설계하거나 수동으로 운영하게 됩니다.

### 의사결정 트리로 보면 더 빠릅니다

![요구사항별 호스팅 플랜 선택 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/05/05-02-decision-tree.ko.png)

*요구사항별 호스팅 플랜 선택 경로*

이 트리에서 중요한 점은 Dedicated가 기본 경로 바깥에 놓인다는 사실입니다. 나쁜 플랜이라서가 아니라, **Functions 고유의 이벤트 기반 스케일 이점을 일부 포기해도 되는 경우에만 맞기 때문**입니다.

실제로 Dedicated는 이미 App Service 운영 역량과 예산 구조가 정해져 있는 조직에서 매우 합리적일 수 있습니다. 다만 그때도 기대치를 정확히 맞춰야 합니다. 큐가 늘면 자동으로 서버리스처럼 반응할 것이라고 기대하면 안 되고, App Service autoscale 규칙을 명시적으로 설계해야 합니다.

### 새 프로젝트의 기본 추천은 이렇게 정리할 수 있습니다

1. **새 서버리스 프로젝트라면 Flex Consumption을 먼저 검토합니다.**
2. **Windows 제약이나 더 강한 콜드 스타트 제어가 필요하면 Premium을 봅니다.**
3. **Consumption은 단순한 데모, Windows 제약이 있는 레거시 시나리오, 또는 기존 자산 유지에 더 가깝습니다.**

하지만 여기에도 단서가 있습니다. Flex Consumption은 강하지만, Blob trigger 제약과 기능 차이를 반드시 확인해야 합니다. 따라서 정확한 메시지는 “무조건 Flex”가 아니라 **“기본 후보는 Flex, 제약 검토는 필수”**입니다.

여기에 cold start 완화 패턴을 함께 메모해 두면 플랜 결정과 운영 설계가 분리되지 않습니다.

| 패턴 | 주로 쓰는 플랜 | 핵심 아이디어 |
|---|---|---|
| Always Ready 인스턴스 설정 | Flex Consumption | 핵심 함수 경로의 초기 지연을 줄입니다. |
| 최소 인스턴스 상시 유지 | Premium | 호출이 없어도 warm baseline을 유지합니다. |
| 트래픽 워밍 타이머 | Flex / Premium / Dedicated | 비핵심 시간대에도 주기 호출로 기동 상태를 유지합니다. |
| 지연 민감 경로 분리 배포 | 모든 플랜 | 지연 민감 함수와 배치성 함수를 앱 단위로 분리합니다. |

특히 "하나의 Function App에 모든 트리거를 몰아넣는 구조"는 콜드 스타트와 스케일 예측을 어렵게 만듭니다. 지연 민감 HTTP 함수와 대용량 배치 트리거를 분리하면 플랜 비용은 조금 늘어도 운영 예측 가능성은 크게 좋아지는 경우가 많습니다.

### 플랜 변경이나 별도 계획 리소스도 결국 운영 선택입니다

Dedicated나 Premium 쪽으로 움직일 때는 별도 plan 리소스를 직접 관리하게 됩니다.

```bash
az functionapp plan create \
  --resource-group $RG --name $PLAN \
  --location koreacentral \
  --sku EP1 --is-linux
```

이 예시는 명령 자체보다 의미가 중요합니다. 특정 플랜으로 이동한다는 것은 단순한 비용 변경이 아니라, 런타임과 warm capacity와 스케일 모델을 함께 바꾸는 선택입니다.

따라서 플랜 전환은 인프라 리소스 변경이면서 동시에 운영 계약 변경입니다. migration 계획에 비용 추정만 넣는 것이 아니라, 콜드 스타트 기대치, 네트워크 경로, 배포 방식, 모니터링 기준까지 같이 적어 두는 편이 좋습니다.

## 흔히 헷갈리는 지점

- **“새 앱은 Flex가 권장된다”와 “항상 Flex가 정답이다”는 다른 말입니다.**
- **Premium은 단순히 비싼 Consumption이 아니라, warm capacity를 사는 운영 모델에 가깝습니다.**
- **Dedicated를 고르면 Functions의 프로그래밍 모델은 유지되지만 서버리스 운영 감각은 약해집니다.**
- **VNet 통합 여부는 생각보다 빠르게 후보를 좁힙니다.** 비용 비교보다 먼저 봐야 할 때가 많습니다.
- **플랜 선택은 가격표보다 콜드 스타트 허용 범위와 기능 제약에서 더 자주 갈립니다.**

이 오해들이 반복되는 이유는 비교표를 기능 목록으로만 읽기 쉽기 때문입니다. 하지만 실제 운영에서는 표의 각 항목이 따로 움직이지 않습니다. VNet 요구는 곧 후보를 줄이고, warm capacity 요구는 곧 비용 구조를 바꾸고, Blob trigger 제약은 이벤트 흐름 설계까지 바꿀 수 있습니다. 그래서 플랜 표는 기능 표가 아니라 운영 조건 표로 읽어야 합니다.

또 하나 기억할 점은, 플랜 선택이 끝난 뒤에도 요구사항이 바뀌면 다시 이 표로 돌아와야 한다는 사실입니다. 예를 들어 처음에는 내부 네트워크 연결이 필요 없었지만 나중에 private resource 접근이 필요해질 수 있고, 처음에는 허용되던 첫 요청 지연이 SLA 강화 이후에는 허용되지 않을 수 있습니다. 플랜은 고정된 신분이 아니라 운영 제약의 현재 표현입니다.

## 운영 체크리스트

- [ ] 플랜별 과금 단위를 한 표로 정리했습니다.
- [ ] 콜드 스타트 허용 범위를 플랜 선택의 1차 기준으로 합의했습니다.
- [ ] VNet, 배포 슬롯, Blob trigger 제약 같은 기능 요구사항을 비교표에 반영했습니다.
- [ ] 플랜별 인스턴스 상한과 워크로드 피크를 대조했습니다.
- [ ] 월간 비용을 평시·피크·장애 시나리오로 나눠 시뮬레이션했습니다.

## 정리

이번 글의 핵심은 Azure Functions 플랜을 제품 이름이 아니라 **운영 trade-off가 다른 실행 모델**로 읽는 것입니다. Consumption은 가장 단순한 종량제이지만 제약이 있고, Flex Consumption은 새 앱의 기본 후보이지만 여전히 Linux 전용과 기능 차이가 있습니다. Premium은 warm capacity로 콜드 스타트를 제어하고, Dedicated는 Functions를 App Service 방식으로 운영하는 선택입니다.

따라서 좋은 플랜 선택은 “무조건 최신 권장안”을 따르는 일이 아니라, 워크로드가 감당할 수 없는 제약을 먼저 제거하는 과정에 가깝습니다. OS, VNet, 콜드 스타트, 스케일 방식, 비용 구조를 차례로 보면 후보가 빠르게 정리됩니다. 특히 새 프로젝트라면 Flex Consumption을 먼저 검토하되, 제약을 반드시 문서로 확인하는 습관이 중요합니다.

다음 글에서는 여기서 고른 플랜이 실제 운영에서 어떤 행동으로 나타나는지 봅니다. **인스턴스는 어떤 신호를 보고 늘어나는가, 첫 요청은 왜 느릴 수 있는가, 그리고 동시성과 비용은 어떻게 연결되는가**를 스케일링과 콜드 스타트 관점에서 정리하겠습니다.

플랜 선택은 한 번 끝내는 체크박스가 아니라 이후의 배포 방식과 운영 기대치를 정하는 설계 결정입니다. 그래서 지금 이 장에서 시간을 들이는 것은 뒤의 장애와 비용 논의를 줄이는 가장 싼 투자이기도 합니다.

## 처음 질문으로 돌아가기

- **각 플랜은 정확히 무엇을 기준으로 과금하고 무엇을 제약할까요?**
  - 본문의 기준은 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **플랜 선택에서 가격보다 콜드 스타트 허용 범위가 먼저 중요해지는 경우는 언제일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **VNet 통합, Always Ready 같은 플랫폼 기능은 어떤 플랜 선택을 사실상 강제할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions 101 (1/7): Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- [Azure Functions 101 (2/7): 트리거와 바인딩 — 함수 입출력의 모든 것](./02-triggers-and-bindings.md)
- [Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가](./03-host-and-worker.md)
- [Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지](./04-first-deploy.md)
- **Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated (현재 글)**
- Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 (예정)
- Azure Functions 101 (7/7): 모니터링과 운영 기초 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Function scale and hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Target-based scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Azure Functions Premium plan](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Dedicated hosting plans for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [Migrate from Consumption to Flex Consumption](https://learn.microsoft.com/en-us/azure/azure-functions/migration/migrate-plan-consumption-to-flex)

### 관련 시리즈

- [Azure Functions 101 — 스케일링과 콜드 스타트](./06-scaling-and-cold-start.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/) — 플랜 차이가 런타임 내부 동작에 어떻게 연결되는지 더 보고 싶다면

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/05-choosing-a-plan)

Tags: Azure, Azure Functions, Serverless, Cloud
