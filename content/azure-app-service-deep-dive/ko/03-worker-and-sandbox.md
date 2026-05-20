---
title: "Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가"
series: azure-app-service-deep-dive
episode: 3
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
last_reviewed: '2026-05-15'
seo_description: Windows 샌드박스와 Linux 컨테이너 경계를 비교해 App Service 실행 제약을 정리합니다.
---

# Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가

로컬에서는 잘 되는데 App Service에서는 실패한다는 말은 흔하지만, 원인은 생각보다 자주 프레임워크 내부가 아니라 실행 경계에 있습니다. App Service는 같은 이름 아래에서 Windows code app과 Linux app을 모두 제공하지만, 실제 사용자 코드가 놓이는 경계와 제약은 두 환경에서 꽤 다르게 나타납니다.

특히 Windows에서는 sandbox라는 단어를 보안 기능 정도로만 읽기 쉽습니다. 그러나 운영에서는 그것이 OS 기능 접근, 라이브러리 호환성, 파일시스템 기대, 프로세스 생명주기까지 바꾸는 실행 계약으로 작용합니다. Linux에서는 같은 질문이 registry나 GDI가 아니라 container startup contract와 `/home` storage semantics 쪽으로 옮겨갑니다.

이 글은 Azure App Service Deep Dive 시리즈의 세 번째 글입니다.

이번 글의 목적은 worker를 포털의 인스턴스 수라는 추상어가 아니라, 사용자 코드가 실제로 갇혀 실행되는 경계로 다시 이해하는 것입니다. 이 관점이 있어야 배포는 성공했는데 특정 라이브러리만 실패하는 문제, Windows에서만 깨지는 문제, Linux에서만 startup loop가 생기는 문제를 같은 바구니에 넣지 않게 됩니다.

이제 worker 안쪽에서 사용자 코드가 실제로 어디에 놓이는지 보겠습니다.

## 먼저 던지는 질문

- App Service의 worker는 실제로 어떤 실행 경계를 의미할까요?
- Windows code app에서 App Service sandbox는 무엇을 허용하고 무엇을 제한할까요?
- 왜 registry write와 GDI/User32 계열 제약이 Windows App Service에서 자주 문제를 만들까요?

## 큰 그림

![Azure App Service Deep Dive 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-01-the-two-worker-models-that-matter.ko.png)

*Azure App Service Deep Dive 3장 흐름 개요*

이 그림에서는 Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

운영에서 worker를 제대로 이해하지 못하면 런타임 문제와 플랫폼 계약 문제를 계속 섞게 됩니다. 예를 들어 특정 PDF 라이브러리가 Windows App Service에서만 실패하는데도 패키지 버전이나 코드 버그를 끝없이 의심하게 되고, Linux 컨테이너가 readiness를 통과하지 못하는데도 애플리케이션 예외 추적만 계속 보게 됩니다. 이 둘은 출발점부터 다른 문제입니다.

또한 App Service는 같은 서비스 이름 아래에서도 Windows와 Linux에서 전혀 다른 첫 질문을 요구합니다. Windows code app은 "sandbox가 이 OS 기능을 허용하는가"가 먼저이고, Linux app은 "컨테이너가 올바른 포트와 startup contract로 준비되는가"가 먼저입니다. 같은 App Service라는 이름만 보고 진단 순서를 통일하면 자주 엇나갑니다.

마지막으로 이 글은 4화의 배포 이야기와도 직접 이어집니다. 3화가 실행 경계를 설명한다면 4화는 아티팩트가 그 경계 안으로 어떻게 들어오는지를 설명합니다. 실행 경계와 배포 경계를 분리해 두어야 sandbox failure와 deployment-shape failure를 같은 문제로 오해하지 않게 됩니다.

## 핵심 관점

이 글에서 가장 먼저 고정해야 할 문장은 이것입니다. **App Service의 worker는 하나의 용어이지만, Windows에서는 sandbox 안의 IIS-hosted process이고, Linux에서는 container contract 안의 프로세스입니다.** 같은 "worker"라는 단어가 같은 제약을 뜻하는 것은 아닙니다.

이 구분이 중요한 이유는 장애가 붙는 자리가 완전히 달라지기 때문입니다. Windows에서는 registry write, GDI/User32 호출, 일부 OS 기능 접근이 핵심 제약으로 등장하고, Linux에서는 port binding, startup timeout, `/home` persistence, entrypoint readiness가 핵심 변수로 등장합니다. 두 환경을 같은 질문으로 디버깅하면 원인 후보가 너무 넓어집니다.

그리고 이 차이는 단순한 구현 디테일이 아니라 운영 계약입니다. Windows에서는 다중 테넌트 환경의 격리와 자원 공정을 위해 sandbox가 의도적으로 좁혀져 있고, Linux에서는 container startup과 mounted storage semantics가 app-platform contract의 핵심을 이룹니다.

> "worker"를 이해한다는 것은 인스턴스 수를 세는 것이 아니라, 내 코드가 어떤 경계 안에서 살고 어떤 OS 가정을 포기해야 하는지 아는 것입니다.

## 핵심 개념

### worker는 하나의 이름 아래 두 가지 다른 실행 모델을 가집니다

App Service 문맥에서 worker는 통일된 플랫폼 용어이지만, 운영자가 마주하는 실제 실행 경계는 OS와 호스팅 모드에 따라 달라집니다.

Windows code app에서는 앱이 IIS 아래에서 돌아가고 App Service sandbox 제약을 직접 받습니다. 반면 Linux built-in 또는 custom container에서는 컨테이너가 핵심 실행 경계입니다. 둘 다 격리는 제공하지만, 어떤 제약을 주고 어떤 실패를 유도하는지는 같지 않습니다.

### Windows에서는 `w3wp.exe`와 sandbox를 함께 봐야 합니다

Kudu의 공개 sandbox 자료는 Windows App Service를 각 앱이 자기 sandbox 안에서 실행되는 모델로 설명합니다. 실전적으로 중요한 문장은 세 가지입니다. 앱은 같은 machine의 다른 앱과 격리되고, multi-tenant 품질 보장을 위해 제약이 걸리며, 그 제약은 registry access, graphics API, 일부 networking behavior에 영향을 줍니다.

![w3wp.exe가 App Service sandbox 안에 놓인 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-02-windows-w3wp-exe-under-the-app-service-s.ko.png)

이 그림 하나면 Windows App Service에서 "왜 이 라이브러리만 유독 실패하지"라는 질문의 출발점이 보입니다. 사용자 코드는 단순히 IIS 위에서만 도는 것이 아니라, sandbox 안에서 허용된 OS 기능 범위 안에서만 돌 수 있습니다.

### registry와 GDI/User32가 자주 문제를 만드는 이유는 명확합니다

로컬 서버나 전통적인 Windows 호스팅에서는 설치형 소프트웨어가 registry write를 당연하게 가정하는 경우가 많습니다. Windows App Service sandbox에서는 이 가정이 깨집니다. 마찬가지로 많은 웹 워크로드는 Windows UI subsystem이 필요 없지만, 일부 PDF, 이미지, 폰트, 브라우저 자동화 라이브러리는 여전히 GDI/User32 계열 호출에 기대고 있습니다.

그래서 특정 실패 패턴이 반복됩니다. HTML-to-PDF 라이브러리가 실패하고, custom font rendering이 이상하며, Selenium이나 PhantomJS 계열 경로가 흔들리고, `System.Drawing` 기반 코드가 예상과 다르게 동작합니다. 이것은 신비한 Azure 버그라기보다, 다중 테넌트 웹 워크로드에 맞춰 의도적으로 좁혀 둔 Windows sandbox의 결과입니다.

### Linux에서는 container가 실행 경계이고 startup contract가 더 중요합니다

Linux App Service는 공개 문서가 훨씬 단순한 멘탈 모델을 제공합니다. 앱은 컨테이너 안에서 실행됩니다. built-in 이미지를 쓰든 custom image를 쓰든, 운영자가 먼저 확인해야 할 축은 프로세스가 컨테이너 안에 있는가, readiness가 언제 traffic eligibility를 열어 주는가, persistent storage가 `/home` mount에 어떻게 연결되는가입니다.

![컨테이너 안에서 앱이 도는 Linux 실행 경계](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-01-linux-the-container-is-the-execution-bou.ko.png)

Linux에서는 Windows와 동일한 registry/GDI 제약을 이야기할 수 없습니다. 공개 자료도 그런 언어로 설명하지 않습니다. 대신 포트 바인딩, startup timeout, entrypoint, storage mount가 훨씬 직접적으로 장애와 연결됩니다.

### `WEBSITES_ENABLE_APP_SERVICE_STORAGE`는 `/home`의 의미를 바꿉니다

Linux custom container에서 특히 중요한 설정은 `WEBSITES_ENABLE_APP_SERVICE_STORAGE`입니다. `true`이면 `/home`에 persistent shared storage가 마운트되고, `false`이면 그 경로가 훨씬 더 ephemeral한 container-local state처럼 동작합니다. 이 차이를 놓치면 scale-out 뒤 업로드 파일이 사라지거나, 재시작 후 생성 파일이 없어지거나, SCM에서 보는 파일과 앱이 보는 파일이 다르게 느껴지는 현상을 쉽게 만납니다.

![공유 home 마운트와 로컬 파일 계층의 차이](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-02-when-websites-enable-app-service-storage.ko.png)

![공유 home 마운트와 로컬 파일 계층의 차이](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-05-when-websites-enable-app-service-storage-2.ko.png)

같은 `/home`이라는 경로를 보고도 운영 의미가 완전히 달라질 수 있다는 점이 중요합니다. 파일 위치만 보는 것으로는 충분하지 않고, 그 경로가 shared persistent mount인지 container-local layer인지 같이 확인해야 합니다.

### sandbox는 보안 장치이면서 동시에 공정성 장치입니다

sandbox를 보안 기능으로만 읽으면 제약이 임의적이라고 느껴질 수 있습니다. 그러나 App Service에서는 그것이 품질 보장 장치이기도 합니다. 여러 고객 앱이 worker 인프라를 공유하는 만큼, 한 앱이 registry, graphics subsystem, local communication을 마음대로 사용해 다른 앱에 영향을 주지 못하게 해야 하기 때문입니다.

![sandbox 제한이 격리와 자원 공정을 지키는 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/03/03-06-the-sandbox-is-a-security-feature-and-a.ko.png)

이 관점으로 보면 제약이 훨씬 자연스럽습니다. registry write 차단, graphics subsystem 접근 제한, 일부 local communication 패턴 제약은 불편을 주기 위한 옵션이 아니라 다중 테넌트 웹 호스팅을 유지하는 계약입니다.

### 진단은 worker 경계를 먼저 확인하는 방식으로 접근해야 합니다

worker 문제를 디버깅할 때는 "내 코드에 무엇이 잘못됐는가"보다 먼저 "내 코드가 어떤 경계 안에 있는가"를 물어야 합니다. Windows code app이라면 IIS가 프로세스 생명주기를 쥐고 sandbox 제약이 직접 적용됩니다. Linux app이라면 container entrypoint와 startup command가 생명주기를 지배하고, readiness ping이 organic traffic 진입 시점을 결정합니다.

아래 명령은 앱 로그, SSH, 파일 경로를 빠르게 확인해 worker 경계를 가늠할 때 유용합니다.

```bash
az webapp log tail -n my-app -g my-rg

az webapp ssh -n my-app -g my-rg
# inside the sandbox
ps -ef | head
ls /home/site/wwwroot
cat /home/LogFiles/eventlog.xml 2>/dev/null | tail -40
```

이 명령은 정답을 한 번에 주지 않지만, 실행 중인 프로세스와 파일시스템 관찰 지점을 빠르게 확보하게 해 줍니다. 특히 Linux에서는 container 안의 실제 프로세스 상태를, Windows에서는 로그와 파일 경로 힌트를 통해 sandbox 제약의 흔적을 찾는 출발점이 됩니다.

### 진단 엔드포인트를 두면 실행 경계를 더 빨리 분리할 수 있습니다

"로컬에서는 되는데 App Service에서는 안 된다"는 상황에서는 앱이 실제로 어떤 실행 표면을 보고 있는지 먼저 출력해 보는 편이 빠릅니다. 아래 엔드포인트는 worker 식별자, `/home` storage 설정, 포트 계약을 한 번에 노출합니다.

```python
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.get("/diag/runtime")
def diag_runtime():
    return jsonify(
        hostname=socket.gethostname(),
        instance_id=os.environ.get("WEBSITE_INSTANCE_ID", "unknown"),
        site_name=os.environ.get("WEBSITE_SITE_NAME", "unknown"),
        storage=os.environ.get("WEBSITES_ENABLE_APP_SERVICE_STORAGE", "unset"),
        port=os.environ.get("PORT", "unset"),
    )
```

이 값을 app settings 조회와 나란히 보면 진단 속도가 훨씬 빨라집니다.

```bash
az webapp config appsettings list -n my-app -g my-rg \
  --query "[?name=='WEBSITES_ENABLE_APP_SERVICE_STORAGE' || name=='WEBSITES_PORT' || name=='PORT'].{name:name,value:value}" \
  -o table
```

**Expected output:** Linux custom container인데 `WEBSITES_ENABLE_APP_SERVICE_STORAGE`가 `false`로 보이면 `/home`을 영구 공유 저장소처럼 가정하면 안 됩니다. `PORT` 또는 `WEBSITES_PORT`가 기대와 다르면 startup contract 문제를 먼저 의심해야 합니다.

## 흔히 헷갈리는 지점

- **worker는 단순히 인스턴스 수의 다른 말이 아닙니다.** 사용자 코드가 실제로 놓이는 실행 경계입니다.
- **Windows와 Linux의 제약을 같은 언어로 설명하면 안 됩니다.** Windows는 sandbox 중심이고, Linux는 container startup contract 중심입니다.
- **`/home`이 보인다고 해서 항상 shared persistent storage인 것은 아닙니다.** Linux custom container에서는 설정에 따라 의미가 달라집니다.
- **sandbox 제한은 임의의 불편이 아닙니다.** multi-tenant 격리와 자원 공정성을 유지하기 위한 계약입니다.
- **"로컬에서는 된다"는 사실만으로 App Service 버그를 의심하면 안 됩니다.** 로컬 호스팅이 허용하는 OS 기능과 App Service가 허용하는 OS 기능이 다를 수 있습니다.

## 운영 체크리스트

- [ ] Windows code app에서 sandbox-forbidden OS 의존성을 코드 리뷰 규칙에 반영했습니다.
- [ ] Linux app에서 포트 바인딩과 startup command를 명시적으로 검증했습니다.
- [ ] `/home` persistence 여부를 `WEBSITES_ENABLE_APP_SERVICE_STORAGE`와 함께 문서화했습니다.
- [ ] worker process memory와 CPU 알림을 런타임 알림과 분리해 구성했습니다.
- [ ] Kudu/SCM 접근 권한을 최소화하고 worker 진단 절차를 별도 런북으로 정리했습니다.

## 정리

3화의 핵심은 worker가 추상적인 인스턴스 수가 아니라는 점입니다. Windows App Service에서는 사용자 코드가 IIS와 App Service sandbox 안에서 실행되며, registry write와 많은 User32/GDI32 호출이 제약됩니다. Linux App Service에서는 container가 핵심 경계이고, startup contract와 `/home` storage semantics가 더 직접적인 변수로 등장합니다.

운영자가 얻어야 할 가장 중요한 감각은 같은 서비스 이름이 같은 첫 질문을 보장하지 않는다는 사실입니다. Windows라면 "이 라이브러리가 sandbox 계약을 어기는가"를 먼저 봐야 하고, Linux라면 "컨테이너가 올바르게 준비되고 있는가"를 먼저 봐야 합니다. 이 순서가 바뀌면 진단 시간이 길어집니다.

다음 글에서는 실행 경계에서 한 걸음 더 나아가, 아티팩트가 이 경계 안으로 어떻게 들어오는지 보겠습니다. Kudu, Oryx, run-from-package, slot warm-up을 함께 놓고 배포 성공과 런타임 준비 완료가 왜 다른 질문인지 이어서 설명하겠습니다.

## 처음 질문으로 돌아가기

- **App Service의 worker는 실제로 어떤 실행 경계를 의미할까요?**
  - 본문의 기준은 Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Windows code app에서 App Service sandbox는 무엇을 허용하고 무엇을 제한할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 registry write와 GDI/User32 계열 제약이 Windows App Service에서 자주 문제를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service Deep Dive (1/6): App Service 플랫폼 아키텍처 — Front-End·Worker·File Server](./01-platform-architecture.md)
- [Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가](./02-front-end-and-arr.md)
- **Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 (현재 글)**
- Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 (예정)
- Azure App Service Deep Dive (5/6): 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 (예정)
- Azure App Service Deep Dive (6/6): 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Azure Web App sandbox](https://github.com/projectkudu/kudu/wiki/Azure-Web-App-sandbox/843a564005d4f1028c5e171cf37d35da731f0572)
- [Operating system functionality in Azure App Service](https://learn.microsoft.com/azure/app-service/operating-system-functionality)
- [Configure a custom container for Azure App Service](https://learn.microsoft.com/azure/app-service/configure-custom-container)
- [Environment variables and app settings reference](https://learn.microsoft.com/azure/app-service/reference-app-settings)

### 관련 시리즈
- [Azure App Service 101 — Hosting Models](../../azure-app-service-101/ko/03-hosting-models.md)
- [Azure Functions Deep Dive — Worker Process](../../azure-functions-deep-dive/ko/02-worker-process.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
