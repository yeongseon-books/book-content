---
title: App Service 플랫폼 아키텍처 — Front-End·Worker·File Server
series: azure-app-service-deep-dive
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Distributed Systems
- Platform Engineering
last_reviewed: '2026-05-12'
seo_description: App Service의 Front-End, Worker, File Server 구현 세부사항은 Microsoft가 공개하지
  않았습니다.
---

# App Service 플랫폼 아키텍처 — Front-End·Worker·File Server

App Service를 오래 운영할수록 가장 자주 듣는 말은 의외로 비슷합니다. "플랫폼이 뭔가 이상합니다." 그런데 이 문장은 원인을 설명하지 못합니다. 재시작이 반복되는 것인지, 첫 요청이 느린 것인지, 특정 사용자만 한 인스턴스에 붙는 것인지, 배포는 성공했는데 런타임이 준비되지 않은 것인지가 모두 같은 문장 안에 섞여 있기 때문입니다.

이 시리즈를 제대로 읽으려면 먼저 App Service를 하나의 서비스 이름이 아니라 몇 개의 물리적 박스로 다시 그려야 합니다. 요청이 들어오는 위치, 실제 사용자 코드가 실행되는 위치, 여러 인스턴스가 함께 보는 파일 기준점, 그리고 배포를 실행하는 SCM buddy site를 나눠 놓아야 이후의 세부 동작이 한 줄로 연결됩니다.

이 글은 Azure App Service Deep Dive 시리즈의 첫 번째 글입니다.

이번 글의 목적은 기능 목록을 다시 소개하는 데 있지 않습니다. 대신 이후 다섯 편을 읽을 수 있게 만드는 공통 지도를 먼저 깔아 두겠습니다. 여기서 지도가 선명해지면 Front-End, ARR, Worker, Kudu, 스케일링, warm-up이 서로 다른 주제가 아니라 하나의 운영 모델로 읽히기 시작합니다.

이제 App Service를 추상적인 PaaS가 아니라 요청·실행·파일·배포 경계가 분리된 플랫폼으로 보겠습니다.

## 이 글에서 다룰 문제

- App Service의 "플랫폼"은 실제로 어떤 박스들로 나눠서 이해해야 할까요?
- App Service Plan은 단순한 과금 단위가 아니라 어떤 격리와 용량의 의미를 가질까요?
- Front-End, Worker, shared storage는 각자 어떤 책임을 맡고 어디서 서로 연결될까요?
- 여러 인스턴스가 같은 `/home`을 본다는 말은 운영에서 정확히 무엇을 의미할까요?
- Azure Functions와 App Service Deep Dive는 어떤 경계에서 서로 이어질까요?

## 왜 이 글이 중요한가

App Service를 잘못 이해하면 거의 모든 운영 증상이 "플랫폼 문제"라는 한 단어로 뭉개집니다. 그러면 배포 문제를 런타임 문제처럼 보고, 런타임 준비 지연을 Front-End 문제처럼 보고, sticky routing을 애플리케이션 버그처럼 해석하게 됩니다. 반대로 아키텍처 박스를 먼저 분리해 두면 증상이 붙는 위치가 빠르게 좁혀집니다.

특히 이 시리즈는 문서에 공개된 사실만으로 운영 가능한 멘탈 모델을 세우는 데 집중합니다. App Service는 완전한 오픈소스 플랫폼이 아니므로, 공개되지 않은 내부 배치 알고리즘을 상상으로 메우기 시작하면 deep dive가 금방 허구가 됩니다. 실전에서 중요한 것은 모르는 내부를 추측하는 능력이 아니라, 공개된 표면만으로도 어디까지 설명할 수 있는지 아는 능력입니다.

또 하나 중요한 이유는 이후 글 다섯 편이 모두 이 지도 위에 서 있기 때문입니다. 2화는 Front-End와 ARR이 worker를 어떻게 고르는지, 3화는 worker 안에서 어떤 실행 경계가 적용되는지, 4화는 Kudu와 Oryx가 파일을 어떻게 배치하는지, 5화는 scale-out 결정이 어떻게 worker 증가로 이어지는지, 6화는 새 worker가 언제 traffic-eligible 상태가 되는지를 이 구조 위에서 설명합니다.

## App Service 플랫폼을 이해하는 가장 좋은 방법: 다섯 개의 박스를 하나의 요청 경로로 묶어 보는 것입니다

App Service를 깊게 이해할 때 가장 도움이 되는 문장은 이것입니다. **App Service는 단일 서버도, 단일 프로세스도, 단일 배포 엔드포인트도 아닙니다. Front-End, ARR 기반 라우팅, Worker, shared file server, Kudu라는 다섯 개의 박스가 서로 연결된 플랫폼입니다.** 이 관점을 먼저 잡아야 "요청은 들어오는데 앱이 아직 준비되지 않았다" 같은 문장이 정확히 어느 층을 가리키는지 보입니다.

이 멘탈 모델이 유용한 이유는 요청·실행·파일·배포를 같은 선 위에 올려 주기 때문입니다. 사용자는 Front-End를 통해 들어오고, ARR은 적절한 worker를 고르고, worker는 shared content를 읽으며, Kudu는 그 shared content 경로에 배포를 집어넣습니다. 다시 말해 요청이 흐르는 경로와 코드가 배치되는 경로가 완전히 별개가 아니라, 같은 substrate 위에서 만납니다.

또 하나 중요한 점은 이 시리즈가 비공개 내부를 추정하지 않는다는 사실입니다. Learn 문서가 말하는 구조, Kudu 공개 저장소가 보여 주는 API와 배포 경로, Oryx 공개 자료가 설명하는 detect-build-startup 계약만으로도 운영 판단에 필요한 지도는 충분히 만들 수 있습니다.

> 이 시리즈에서 deep dive란 닫힌 내부를 상상으로 채우는 일이 아니라, 공개된 구조를 끝까지 정확하게 따라가서 어디서 문제가 붙는지 설명 가능한 지도로 바꾸는 일입니다.

## 핵심 개념

### 시리즈 전체 지도를 먼저 머리에 넣어야 합니다

아래 그림은 이 시리즈 전체를 관통하는 기본 지도입니다. 각 화는 이 그림의 한 박스를 확대하는 방식으로 이어집니다.

![요청 하나가 Front-End부터 warm-up까지 지나는 경로](../../../assets/azure-app-service-deep-dive/01/01-01-the-big-picture-one-request-through-app.ko.png)

왼쪽의 외부 클라이언트와 진입점은 요청 유입부입니다. 가운데의 Front-End와 ARR은 사용자 요청을 어떤 앱과 어떤 worker로 보낼지 결정합니다. 오른쪽의 Worker는 실제 사용자 코드가 실행되는 경계입니다. 옆의 Kudu는 배포와 진단을 담당하는 SCM buddy site이며, 파일 배치와 앱 재기동 흐름에 연결됩니다. 마지막의 스케일링과 warm-up은 새 worker가 실제로 traffic-eligible 상태가 되는 시점을 결정합니다.

### 공개 문서가 반복해서 보여 주는 표준 구조는 Front-End, Worker, shared storage입니다

Microsoft가 공개적으로 설명하는 App Service 아키텍처의 핵심은 복잡하지 않습니다. HTTP/HTTPS 진입점인 Front-End, 실제 앱 실행을 담당하는 Worker, 그리고 여러 인스턴스가 같은 앱 콘텐츠를 보게 하는 shared storage가 기본 뼈대입니다. 이 모델을 먼저 받아들이면 App Service를 VM 여러 대에 각각 파일을 복사하는 구조로 오해할 가능성이 크게 줄어듭니다.

![Front-End, worker, shared storage의 연결 구조](../../../assets/azure-app-service-deep-dive/01/01-02-canonical-public-architecture-front-end.ko.png)

중요한 것은 속도가 아니라 성질입니다. 기본 모델에서 storage는 공유되고, 재시작 뒤에도 남고, 여러 worker가 같은 mounted path를 봅니다. 그래서 `/home/site/wwwroot` 아래의 배포 결과는 scale-out 뒤에도 worker마다 따로 갈라진 복사본이라기보다 공통 기준점에 가깝게 동작합니다.

다만 Linux custom container에는 예외가 있습니다. `WEBSITES_ENABLE_APP_SERVICE_STORAGE=false`이면 `/home`이 공유 영속 스토리지로 마운트되지 않으므로, 그 경로를 여러 인스턴스가 함께 보는 안정적인 기준점으로 일반화하면 안 됩니다. 이 차이는 3화에서 다시 자세히 봅니다.

### Front-End는 단순한 네트워크 홉이 아니라 요청을 worker로 넘기는 첫 번째 판단 지점입니다

Front-End를 로드밸런서 한 단어로만 이해하면 절반만 본 셈입니다. Front-End는 먼저 요청이 어느 앱과 슬롯에 속하는지 해석하고, 그다음 ARR을 통해 어떤 worker가 그 요청을 받을지 결정하는 진입부입니다. 이 진입부를 분리해 보지 않으면, 일부 사용자만 특정 인스턴스에 계속 붙는 현상이나 affinity 때문에 생기는 partial outage를 이해하기 어렵습니다.

### worker는 포털의 인스턴스 수가 실제 실행 용량으로 풀리는 자리입니다

포털에서 인스턴스를 3개로 늘렸다는 말은, 앱이 사용할 수 있는 실행 용량이 worker pool 안에서 세 개의 실행 단위로 물질화된다는 뜻에 가깝습니다. 이것을 "앱 하나가 VM 하나를 가진다"로 이해하면 App Service Plan과 app instance 사이의 관계를 계속 오해하게 됩니다.

![인스턴스 수가 worker 수로 풀리는 구조](../../../assets/azure-app-service-deep-dive/01/01-03-workers-are-what-instance-count-actually.ko.png)

Windows code app에서는 IIS-hosted `w3wp.exe` 계열 프로세스가 핵심 실행 단위이고, Linux 앱에서는 컨테이너가 핵심 실행 단위입니다. 같은 App Service라는 이름 아래에서도 운영자가 먼저 던져야 할 질문이 OS와 호스팅 모드에 따라 달라지는 이유가 여기에 있습니다.

### Kudu는 배포와 진단을 수행하는 SCM buddy site입니다

Kudu를 단순한 보조 콘솔로 이해하면 배포 문제를 너무 좁게 보게 됩니다. 공개된 Kudu 아키텍처 자료는 Kudu를 실사이트 옆에 붙은 single-tenant SCM buddy site로 설명합니다. 이 buddy site는 배포 요청을 받고, 배포 이력을 남기고, 파일과 로그를 노출하고, 필요한 경우 배포 로직을 실행합니다.

![Kudu SCM 사이트와 실사이트의 배포 관계](../../../assets/azure-app-service-deep-dive/01/01-01-kudu-is-the-deployment-buddy-site.ko.png)

이 구분은 운영에서 결정적입니다. Kudu success는 artifact 수신과 파일 배치 측면의 성공일 수 있지만, 그것이 곧 앱 startup success를 의미하지는 않습니다. 따라서 배포 문제와 런타임 문제를 같은 스트림으로 읽지 않는 습관이 중요합니다.

### Azure Functions는 이 substrate 위에 올라가는 별도 런타임입니다

Functions Deep Dive를 이미 읽었다면 자연스럽게 질문이 생깁니다. Functions host는 이 지도에서 어디에 있을까요. 답은 worker 안쪽입니다. App Service가 worker, filesystem, request substrate를 제공하고, 그 위에서 Functions host가 올라오며, 다시 그 host가 language worker와 gRPC 채널을 엽니다.

![App Service worker 위에 Functions host가 놓인 구조](../../../assets/azure-app-service-deep-dive/01/01-05-where-functions-fits-in-this-picture.ko.png)

따라서 두 시리즈는 경쟁 관계가 아닙니다. Functions 시리즈는 App Service 위에서 살아가는 특정 런타임의 내부를 보고, 이번 시리즈는 그 런타임을 떠받치는 범용 웹 플랫폼의 구조를 봅니다. 이 경계가 잡히면 두 시리즈의 설명이 서로 충돌하지 않고 정확히 맞물립니다.

### 이 구조는 CLI로도 빠르게 확인할 수 있습니다

아래 명령은 plan의 SKU, worker 수, per-site scaling 여부, 그리고 같은 plan에 붙은 앱들을 빠르게 확인할 때 유용합니다. 아키텍처 그림을 운영 표면과 연결하는 가장 쉬운 출발점 중 하나입니다.

```bash
az appservice plan show -n my-plan -g my-rg \
  --query "{sku:sku.name, tier:sku.tier, workers:numberOfWorkers, perSite:perSiteScaling, kind:kind, reserved:reserved}"

az webapp list --plan my-plan -g my-rg \
  --query "[].{name:name, state:state, hostNames:defaultHostName}" -o table
```

이 명령이 보여 주는 값은 단순한 인벤토리가 아닙니다. plan이 실제로 어떤 체급을 갖는지, worker capacity가 몇 개인지, 같은 substrate를 공유하는 앱이 무엇인지가 드러나므로 noisy-neighbour 가능성과 격리 수준을 점검하는 기본 재료가 됩니다.

## 흔히 헷갈리는 지점

- **App Service Plan은 단순한 과금 바구니가 아닙니다.** worker capacity와 격리 수준을 함께 정의하는 실행 단위입니다.
- **scale-out은 앱이 VM을 직접 늘리는 과정이 아닙니다.** plan의 원하는 인스턴스 수가 바뀌고, 그 결과 worker capacity가 더 배정되는 과정으로 보는 편이 정확합니다.
- **`/home/site/wwwroot`는 항상 로컬 디스크 복사본이 아닙니다.** 기본 모델에서는 shared content path이고, Linux custom container에서는 storage 설정에 따라 의미가 달라질 수 있습니다.
- **Kudu는 런타임 그 자체가 아닙니다.** SCM buddy site로서 배포와 진단을 담당하며, Kudu success와 runtime success는 서로 다른 판정입니다.
- **Functions를 이해했다고 App Service substrate를 자동으로 이해한 것은 아닙니다.** Functions host는 worker 위에 올라가는 런타임일 뿐, Front-End·storage·Kudu 구조를 대신 설명하지는 않습니다.

## 운영 체크리스트

- [ ] App Service Plan을 비용 항목이 아니라 격리 단위와 worker capacity 단위로 문서화했습니다.
- [ ] Linux와 Windows 중 어떤 호스팅 경로를 선택했는지와 그 이유를 ADR에 남겼습니다.
- [ ] 같은 plan에 여러 앱을 올릴 때 noisy-neighbour 시나리오를 검토했습니다.
- [ ] shared `/home` 경로와 local state의 차이를 팀 운영 문서에 반영했습니다.
- [ ] Kudu 성공과 런타임 성공을 분리해서 보는 로그 확인 절차를 정했습니다.

## 정리

1화의 목적은 세부 동작을 모두 설명하는 것이 아니라, 시리즈 전체를 읽을 수 있는 기본 지도를 머리에 넣는 것입니다. App Service 요청은 Front-End로 들어오고, ARR은 worker를 고르며, worker는 shared content를 읽고, Kudu는 그 shared content 경로에 배포를 밀어 넣습니다. 이 선이 잡히면 "플랫폼이 이상하다"는 말이 훨씬 구체적인 질문으로 바뀝니다.

운영적으로 가장 큰 수확은 문제를 박스별로 자를 수 있게 된다는 점입니다. 일부 사용자만 계속 문제를 겪는다면 Front-End와 affinity를 먼저 보고, 배포 직후 앱이 안 뜬다면 Kudu와 startup readiness를 분리해서 보고, 여러 인스턴스에서 파일이 어긋나게 보인다면 shared storage semantics를 먼저 확인할 수 있습니다. deep dive의 가치는 이처럼 증상을 물리적 경계에 붙여 읽게 만드는 데 있습니다.

다음 글부터는 이 큰 그림을 하나씩 확대합니다. 2화에서는 Front-End와 ARR이 실제로 어떻게 worker를 고르는지 보고, 그다음 worker 내부 실행 경계, 배포 경로, scale-out 제어 루프, warm-up 순서로 내려가겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **App Service 플랫폼 아키텍처 — Front-End·Worker·File Server (현재 글)**
- Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 (예정)
- Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 (예정)
- 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 (예정)
- 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 (예정)
- 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Overview of Azure App Service](https://learn.microsoft.com/azure/app-service/overview)
- [Local Cache in Azure App Service](https://learn.microsoft.com/azure/app-service/overview-local-cache)
- [Run your app in Azure App Service directly from a ZIP package](https://learn.microsoft.com/azure/app-service/deploy-run-package)
- [Kudu service overview](https://learn.microsoft.com/azure/app-service/resources-kudu)
- [Kudu architecture](https://github.com/projectkudu/kudu/wiki/Kudu-architecture/863125fba81e8b30950676bf495c7b7d74c00b92)
- [Oryx README @ 20240408.1](https://github.com/microsoft/Oryx/blob/20240408.1/README.md)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/01-host-bootstrap.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
