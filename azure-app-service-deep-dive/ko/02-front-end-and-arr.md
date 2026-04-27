# Front-End과 ARR — 요청은 어떻게 워커에 도달하는가

> Azure App Service Deep Dive 시리즈 (2/6)

1화에서는 App Service를 Front-End, Worker, File Server, Kudu, 관측성 박스로 나눠 봤습니다.
이번 화는 그중 가장 왼쪽의 진입부를 확대합니다.

질문은 하나입니다.
**HTTP 요청 하나가 어떤 기준으로 특정 worker에 도달하는가.**

이 질문을 정확히 이해하면,
ARR Affinity를 언제 꺼야 하는지,
왜 어떤 사용자만 특정 인스턴스에서 계속 문제를 겪는지,
왜 stateless 설계가 App Service에서 유난히 중요하게 반복되는지 한 번에 연결됩니다.

---

## 큰 그림 — 요청 라우팅의 세 단계

```mermaid
flowchart LR
    C[Client] --> FE[Front-End]
    FE --> HOST[Host name validation]
    HOST --> ARR[ARR routing]
    ARR --> W1[Worker 1]
    ARR --> W2[Worker 2]
    ARR --> W3[Worker N]
```

공개 문서 기준으로 요약하면 App Service 진입부는 이렇게 이해하는 편이 안전합니다.

1. 요청이 Front-End에 들어옵니다.
2. Front-End가 앱과 슬롯을 식별합니다.
3. ARR이 worker를 선택해 요청을 전달합니다.

여기서 2단계와 3단계를 분리해서 보는 것이 중요합니다.
어느 앱으로 갈지와,
그 앱의 어느 worker로 갈지는 같은 질문이 아니기 때문입니다.

---

## Front-End가 먼저 결정하는 것들

Front-End를 “로드밸런서” 한 단어로만 이해하면 자주 놓치는 부분이 있습니다.
실제로는 다음 성질이 먼저 작동합니다.

- 들어온 호스트 이름이 어느 앱에 대응되는가
- 어떤 슬롯 URL인지
- 현재 요청을 받을 수 있는 worker 후보가 무엇인가
- affinity cookie가 있다면 기존 worker를 유지할 것인가

```mermaid
flowchart TB
    R[Incoming request] --> H[Resolve host and slot]
    H --> A{ARR Affinity cookie?}
    A -->|Yes| SAME[Prefer same worker]
    A -->|No| PICK[Pick healthy worker]
    SAME --> SEND[Forward request]
    PICK --> SEND
```

이 글에서 세부 알고리즘을 추측하지는 않습니다.
다만 공개 문서와 Microsoft 블로그가 일관되게 말하는 사실은 명확합니다.
**ARR Affinity가 켜져 있으면 같은 사용자의 후속 요청이 같은 worker로 계속 붙을 수 있습니다.**

---

## ARR이 왜 여기 있는가

ARR은 IIS의 Application Request Routing입니다.
IIS ARR 자체 문서는 이것을 프록시 기반 HTTP 라우팅 모듈로 설명합니다.
그리고 cookie를 사용한 client affinity 기능을 지원합니다.

App Service는 이 ARR 기능을 Front-End 경로에서 활용합니다.

즉,
사용자가 받는 `ARRAffinity` 쿠키는 애플리케이션 프레임워크가 만든 세션 쿠키가 아니라,
플랫폼 라우팅 힌트에 가깝습니다.

이 차이를 이해해야 운영 판단이 쉬워집니다.

- 앱 세션 쿠키는 애플리케이션 상태를 의미합니다.
- ARR Affinity 쿠키는 worker stickiness를 의미합니다.

둘은 이름이 비슷한 “세션”처럼 보이지만 성격이 다릅니다.

---

## ARR Affinity가 켜져 있을 때의 요청 경로

```mermaid
sequenceDiagram
    participant U as Client
    participant F as Front-End + ARR
    participant W as Worker 2

    U->>F: First request
    F->>W: Forward request
    W-->>F: Response
    F-->>U: Response + ARRAffinity cookie
    U->>F: Next request + same cookie
    F->>W: Forward to same worker
```

이 동작은 전혀 이상한 것이 아닙니다.
오히려 legacy app에는 편리합니다.

- 프로세스 메모리에 세션을 들고 있는 앱
- 특정 인스턴스 로컬 캐시에 의존하는 앱
- 로그인 직후 같은 인스턴스로 묶이면 덜 흔들리는 앱

문제는 이것이 App Service의 scale-out 모델과 긴장 관계에 있다는 점입니다.

---

## ARR Affinity가 꺼져 있을 때의 요청 경로

```mermaid
flowchart LR
    C1[Request 1] --> FE[Front-End + ARR]
    FE --> W1[Worker 1]
    C2[Request 2] --> FE
    FE --> W2[Worker 2]
    C3[Request 3] --> FE
    FE --> W3[Worker 3]
```

Affinity를 끄면 같은 클라이언트의 요청이 항상 같은 worker로 돌아간다는 가정이 사라집니다.
이게 바로 stateless 앱에 더 유리한 이유입니다.

장점은 분명합니다.

- 부하가 더 고르게 퍼집니다.
- 특정 worker 하나가 일부 사용자만 계속 붙잡는 현상이 줄어듭니다.
- scale-in이나 worker 교체 때 체감 불안정성이 낮아집니다.

대신 전제가 하나 붙습니다.
**어느 worker가 받든 같은 결과가 나와야 합니다.**

---

## 왜 stateless가 반복해서 나오는가

App Service 문서와 Well-Architected 가이드가 ARR Affinity 비활성화를 자주 권장하는 이유는 단순합니다.
platform이 수평 확장에 유리하게 설계되어 있기 때문입니다.

worker는 교체될 수 있고,
늘어날 수 있고,
줄어들 수 있고,
항상 같은 인스턴스가 살아 있다는 보장은 없습니다.

그래서 다음 설계가 App Service와 잘 맞습니다.

- 세션은 Redis나 DB에 저장
- 업로드 상태는 Blob Storage에 저장
- in-memory cache는 최적화일 뿐 진실 원천이 아님
- 요청은 어느 worker가 처리해도 안전

반대로 이런 구조는 scale-out에서 흔들립니다.

- 로그인 세션을 프로세스 메모리에 저장
- 마지막 작업 상태를 worker 로컬 파일에 저장
- 특정 worker 로컬 캐시에만 데이터가 존재

---

## 일부 사용자만 문제를 겪는 이유

운영에서 제일 헷갈리는 장면 중 하나가 이것입니다.

“전체 장애는 아닌데,
특정 사용자만 계속 느리거나 에러를 본다.”

이때 ARR Affinity는 아주 강한 후보입니다.

```mermaid
flowchart TB
    U1[User A] -->|ARR cookie A| W1[Worker 1 healthy]
    U2[User B] -->|ARR cookie B| W2[Worker 2 degraded]
    U3[User C] -->|ARR cookie C| W1
```

Worker 2가 메모리 압박,
느린 dependency,
비정상 재시작 루프를 겪고 있는데,
일부 사용자가 그 worker에 계속 붙어 있다면,
문제는 전역 장애가 아니라 “sticky partial outage”처럼 보입니다.

이것이 ARR Affinity를 이해해야 하는 가장 실전적인 이유입니다.

---

## reverse proxy 앞단이 있으면 더 복잡해지는 이유

Front Door나 Application Gateway가 App Service 앞에 있으면,
세션 고정은 두 층으로 나뉠 수 있습니다.

1. 글로벌/외부 프록시가 어느 origin으로 보낼지
2. App Service Front-End가 어느 worker로 보낼지

App Service 팀 블로그가 반복해서 설명하듯,
앞단 프록시의 cookie affinity만으로는 App Service 내부 worker stickiness를 대신하지 못합니다.
App Service 내부의 worker 선택은 여전히 App Service Front-End와 ARR의 책임이기 때문입니다.

이 말은 반대로도 중요합니다.
App Service 내부 stickiness를 원하지 않는다면,
앱 자체를 stateless하게 만들고,
App Service의 affinity도 필요 없게 가져가는 편이 구조가 단순합니다.

---

## 요청 라우팅과 deployment slot

slot도 이 흐름에 들어갑니다.
Front-End는 host와 slot 문맥을 구분해서 해당 slot의 worker 집합으로 요청을 보냅니다.

```mermaid
flowchart LR
    C[Client] --> FE[Front-End]
    FE --> PROD[Production slot workers]
    FE --> STAGE[Staging slot workers]
```

그래서 slot swap은 단순 URL 장난이 아닙니다.
트래픽을 어느 worker 집합으로 보낼지의 기준점이 바뀌는 작업입니다.
warm-up이 중요한 이유도 여기에 있습니다.

---

## ARR를 켤 때와 끌 때의 판단 기준

### 켜 둘 이유가 남아 있는 경우

- 레거시 앱이 프로세스 메모리 세션에 강하게 의존
- 외부 세션 저장소로 바로 옮기기 어렵다
- 단기 이행 단계에서만 stickiness가 필요하다

### 끄는 편이 좋은 경우

- 이미 stateless 설계다
- scale-out 효율을 높이고 싶다
- 특정 worker 편중을 줄이고 싶다
- 일부 사용자만 느린 현상을 구조적으로 없애고 싶다

이 결정은 취향 문제가 아닙니다.
애플리케이션의 상태 저장 전략과 직결됩니다.

---

## 2화 정리

이번 화의 요지는 단순합니다.

> App Service 요청은 Front-End로 들어오고, ARR이 worker를 선택합니다. ARRAffinity 쿠키가 있으면 같은 사용자를 같은 worker에 붙일 수 있습니다. 이 기능은 stateful 레거시 앱에는 편하지만, 수평 확장과 worker 교체 관점에서는 stateless 설계보다 불리합니다. 특정 사용자만 문제를 겪는 partial outage도 이 구조에서 자주 발생합니다.

다음 3화에서는 이 요청이 도착한 자리,
즉 worker 내부와 sandbox를 봅니다.
Windows 코드 앱에서는 무엇이 `w3wp.exe` 안에서 제한되는지,
Linux 앱에서는 왜 container 경계가 핵심인지 이어서 다룹니다.

---

## 이 시리즈에서의 위치

1화가 전체 지도를 펼쳤다면 이번 글은 그중 Front-End와 ARR 박스를 확대합니다.
다음 글에서는 요청이 도착한 worker 내부의 실행 경계와 sandbox 제약을 살펴보며, 왜 일부 라이브러리가 Windows App Service에서 실패하는지도 이어서 설명합니다.

---

## 참고 자료

### 1차 출처
- [Using the Application Request Routing Module](https://learn.microsoft.com/iis/extensions/planning-for-arr/using-the-application-request-routing-module)
- [Configure ARRAffinity cookie when accessing Azure App Service behind Azure Application Gateway](https://techcommunity.microsoft.com/blog/appsonazureblog/configure-arraffinity-cookie-when-accessing-azure-app-service-behind-azure-appli/3842511)

### 2차 출처
- [Overview of Azure App Service](https://learn.microsoft.com/azure/app-service/overview)
- [Architecture best practices for Azure App Service web apps](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps)
- [Deployment slots in Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)

### 관련 시리즈
- [Azure App Service 101 — Request Lifecycle](../../azure-app-service-101/ko/02-request-lifecycle.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md)
