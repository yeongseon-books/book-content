---
title: "Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가"
series: azure-app-service-deep-dive
episode: 2
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
seo_description: ARR Affinity, 슬롯, 커스텀 도메인 기준으로 App Service 요청 라우팅 경로를 설명합니다.
---

# Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가

App Service 장애를 애플리케이션 코드부터 의심하는 습관은 생각보다 자주 시간을 낭비하게 만듭니다. 실제로는 요청이 사용자 코드에 닿기 전에 이미 Front-End에서 앱과 슬롯이 식별되고, ARR이 worker를 선택하며, affinity 여부에 따라 같은 사용자가 같은 인스턴스에 계속 붙을 수 있기 때문입니다.

운영에서 특히 헷갈리는 장면은 전체 장애가 아닌 부분 장애입니다. 일부 사용자만 계속 느리거나 에러를 보고, 다른 사용자는 멀쩡해 보일 때가 있습니다. 이 현상은 앱 로직보다도 먼저, 요청이 어떤 worker에 고정되었는지와 더 깊은 관련이 있을 때가 많습니다.

이번 글의 목표는 HTTP 요청 하나가 App Service Front-End를 통과해 특정 worker에 도달하는 과정을 운영자의 시선으로 다시 그리는 것입니다. 이 흐름이 보이면 ARR Affinity를 왜 꺼야 하는지, 언제 유지해야 하는지, custom domain과 slot이 라우팅 판단에 어떤 식으로 들어오는지가 함께 정리됩니다.

이제 공개 진입점에서 worker 선택까지의 경로를 단계별로 따라가 보겠습니다.

![Azure App Service Deep Dive 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-01-the-routing-path-in-three-stages.ko.png)
*Azure App Service Deep Dive 2장 흐름 개요*
> Front-End과 ARR — 요청은 어떻게 워커에 도달하는가의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Front-End는 단순 로드밸런서를 넘어 실제로 어떤 종류의 결정을 먼저 내릴까요?
- ARR Affinity 쿠키는 애플리케이션 세션 쿠키와 무엇이 다를까요?
- 요청이 어느 앱과 어느 슬롯에 속하는지 정하는 단계와 worker를 고르는 단계는 어떻게 다를까요?

## 왜 이 글이 중요한가

Front-End와 ARR을 이해하지 못하면 App Service의 많은 증상이 우연처럼 보입니다. 특정 사용자만 에러를 본다면 애플리케이션 세션이나 브라우저 캐시를 먼저 의심하게 되고, scale-out 뒤에도 같은 사용자가 계속 같은 문제를 겪는다면 재현 불가 장애처럼 느껴집니다. 그러나 worker stickiness를 먼저 생각하면 이런 장면이 훨씬 덜 신비롭게 보입니다.

또한 App Service가 stateless 설계를 반복해서 권하는 이유도 이 경로를 보면 훨씬 현실적으로 이해됩니다. Front-End는 요청을 worker에 분산시키고, worker는 교체되거나 늘어나거나 줄어들 수 있습니다. 어느 요청이 어느 worker에 가더라도 같은 결과가 나와야 플랫폼의 수평 확장 모델과 자연스럽게 맞물립니다.

마지막으로 이 글은 3화와 바로 이어집니다. 2화가 "요청이 어떤 worker에 도달하는가"를 설명한다면, 3화는 "그 worker 안에서 사용자 코드가 어떤 실행 경계 안에 놓이는가"를 설명합니다. 라우팅 경계와 실행 경계를 분리해 두어야 Windows sandbox 문제와 Linux container readiness 문제를 혼동하지 않게 됩니다.

## 핵심 관점

이 주제를 가장 명확하게 이해하는 방법은 Front-End 라우팅을 한 번에 뭉개지 않는 것입니다. **App Service Front-End는 먼저 이 요청이 어느 앱과 어느 슬롯에 속하는지 해석하고, 그다음 ARR이 해당 앱 컨텍스트 안에서 어느 worker에 보낼지 결정합니다.** 즉 "어느 앱인가"와 "어느 worker인가"는 같은 질문이 아닙니다.

이 분리가 중요한 이유는 운영 증상이 서로 다른 단계에 붙기 때문입니다. custom domain이나 hostname binding 문제는 앞 단계에서 나타나고, 일부 사용자만 특정 인스턴스에 고정되는 문제는 뒷단의 worker 선택과 affinity에서 더 자주 나타납니다. 두 질문을 섞으면 증상은 비슷해 보여도 진단 시작점이 잘못 잡힙니다.

그리고 이 경로는 deployment slot, Front Door, Application Gateway 같은 상위 구성요소가 있을 때 더 중요해집니다. 외부 프록시가 어느 origin을 고르는지와, App Service 내부에서 ARR이 어느 worker를 고르는지는 여전히 별개의 문제이기 때문입니다.

> Front-End를 이해한다는 것은 "요청이 들어온다"를 아는 것이 아니라, 앱 식별·슬롯 해석·worker 선택·affinity 유지가 서로 다른 단계라는 사실을 머리에 넣는 것입니다.

## 핵심 개념

### 요청 라우팅은 세 단계로 이해하는 편이 안전합니다

가장 단순하고 실용적인 멘탈 모델은 아래와 같습니다. 요청이 Front-End에 들어오고, Front-End가 앱과 슬롯을 해석한 뒤, ARR이 worker를 선택해 요청을 전달합니다.

이 세 단계 모델이 유용한 이유는 증상을 자연스럽게 분해해 주기 때문입니다. hostname binding이나 slot 문맥이 잘못되면 앞 단계에서 어긋나고, 일부 사용자만 같은 인스턴스에 붙는 문제는 뒷단에서 생깁니다. 운영자는 같은 5xx라도 어느 단계에서 해석을 시작할지 더 빨리 정할 수 있습니다.

### Front-End는 요청이 코드에 닿기 전 몇 가지를 먼저 결정합니다

공개 자료 수준에서 안전하게 말할 수 있는 Front-End의 역할은 다음과 같습니다. 들어온 host name이 어느 앱에 대응되는지, 어떤 슬롯 URL인지, 현재 요청을 받을 수 있는 worker 후보가 무엇인지, 그리고 affinity 쿠키가 있다면 같은 client를 같은 worker에 유지할지 판단합니다.

![호스트, 슬롯, affinity로 worker 후보를 거르는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-02-what-the-front-end-decides-first.ko.png)

*호스트, 슬롯, affinity로 worker 후보를 거르는 흐름*

여기서 중요한 점은 Front-End가 단지 트래픽을 넘기는 통로가 아니라는 사실입니다. 애플리케이션 코드가 시작되기 전에 이미 어느 앱 컨텍스트로 갈지, 어떤 worker 후보군이 유효한지가 정리됩니다. 따라서 사용자 코드가 실행되기도 전에 이미 일부 오류는 방향이 정해집니다.

### ARRAffinity는 앱 세션 쿠키가 아니라 플랫폼 라우팅 힌트입니다

ARR은 IIS Application Request Routing입니다. App Service는 Front-End 경로에서 이 기능을 활용해 client affinity를 유지할 수 있습니다. 여기서 핵심은 `ARRAffinity` 쿠키를 애플리케이션 세션 쿠키와 같은 것으로 착각하지 않는 것입니다.

앱 세션 쿠키는 애플리케이션 상태를 가리킵니다. 반면 ARRAffinity 쿠키는 같은 사용자의 후속 요청을 같은 worker로 계속 보내기 위한 플랫폼 차원의 힌트입니다. 겉으로는 둘 다 "세션처럼" 보일 수 있지만, 하나는 business state이고 다른 하나는 routing state입니다.

### affinity가 켜져 있을 때의 편의와 비용을 같이 봐야 합니다

ARR Affinity가 켜져 있으면 같은 사용자의 후속 요청이 같은 worker로 계속 붙을 수 있습니다. 이 동작은 레거시 앱에는 분명히 편리합니다. 프로세스 메모리에 세션을 두는 앱, 특정 인스턴스의 in-memory cache에 기대는 앱, 로그인 흐름이 같은 인스턴스에 머물 때 덜 흔들리는 앱에서는 단기적으로 운영 리스크를 줄여 줄 수 있습니다.

![Affinity 쿠키가 같은 worker를 다시 고르는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-03-request-flow-with-arr-affinity-enabled.ko.png)

*Affinity 쿠키가 같은 worker를 다시 고르는 경로*

문제는 이 편의가 App Service의 수평 확장 모델과 긴장 관계를 만든다는 사실입니다. worker는 교체될 수 있고, scale-out 뒤에는 더 많은 worker가 생기며, scale-in 과정에서는 기존 worker가 빠질 수 있습니다. 이런 플랫폼에서 인메모리 상태를 특정 worker에 묶어 두면 확장성과 장애 격리가 동시에 약해집니다.

### affinity를 끄면 App Service가 기대하는 기본 모델에 더 가까워집니다

Affinity를 끄면 플랫폼은 같은 client를 같은 worker에 계속 되돌려야 한다고 가정하지 않습니다. 따라서 부하가 더 고르게 퍼지고, 특정 worker 하나가 일부 사용자만 계속 붙잡는 현상이 줄어들며, scale-in과 worker replacement도 사용자에게 덜 직접적으로 드러납니다.

![쿠키 고정 없이 worker가 분산 선택되는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-04-request-flow-with-arr-affinity-disabled.ko.png)

*쿠키 고정 없이 worker가 분산 선택되는 경로*

물론 전제도 분명합니다. 어느 worker가 받든 같은 결과가 나와야 합니다. 그래서 App Service 문서와 Well-Architected 지침은 세션을 Redis나 데이터베이스로 빼고, 업로드 상태를 Blob Storage 같은 외부 저장소에 두며, in-memory cache를 source of truth가 아니라 최적화 수단으로만 다루는 설계를 반복해서 권합니다.

### partial outage는 affinity가 만든 증상일 수 있습니다

운영에서 가장 헷갈리는 장면 중 하나는 전체 앱은 살아 있는데 일부 사용자만 계속 느리거나 오류를 보는 경우입니다. 이때 worker 하나가 memory pressure, 느린 dependency, restart churn 같은 문제를 겪고 있고, 일부 사용자가 그 worker에 계속 pinned 되어 있다면 장애는 전역 장애가 아니라 부분 장애처럼 보입니다.

![ARR 고정이 부분 장애를 만드는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-05-why-only-some-users-fail-sometimes.ko.png)

*ARR 고정이 부분 장애를 만드는 경로*

이 현상은 ARR을 이해해야 하는 가장 실전적인 이유입니다. 같은 시각에 어떤 사용자는 정상이고 어떤 사용자는 계속 실패한다면, 애플리케이션 버그만 보지 말고 worker stickiness 가능성도 같이 봐야 합니다.

### slot과 upstream proxy도 같은 그림 안에 넣어야 합니다

deployment slot은 별도 worker pool을 갖는 구조가 아닙니다. production과 staging은 같은 App Service Plan capacity를 공유하고, Front-End가 host와 slot 문맥에 따라 올바른 slot으로 라우팅합니다. 따라서 slot swap은 "worker 집합 교체"라기보다, 준비가 끝난 slot으로 Front-End 라우팅 규칙을 뒤집는 작업으로 이해해야 맞습니다.

![같은 plan 안에서 slot만 바꾸는 라우팅 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/02/02-01-slots-are-also-part-of-request-routing.ko.png)

*같은 plan 안에서 slot만 바꾸는 라우팅 경로*

앞단에 Front Door나 Application Gateway가 있을 때도 마찬가지입니다. 외부 프록시의 cookie affinity는 origin 선택에 영향을 줄 수 있지만, App Service 내부 worker 선택을 대신하지는 않습니다. 외부 계층의 stickiness와 내부 계층의 stickiness를 같은 것으로 취급하면 진단이 어긋납니다.

### 라우팅 상태는 CLI로도 빠르게 점검할 수 있습니다

아래 명령은 Front-End와 직접 대화한다기보다, 앱의 호스트 바인딩과 SSL 상태, alwaysOn 등 라우팅에 영향을 줄 수 있는 공개 표면을 빠르게 확인할 때 유용합니다.

```bash
az webapp config show -n my-app -g my-rg \
  --query "{httpsOnly:httpsOnly, http20:http20Enabled, alwaysOn:alwaysOn, ftpsState:ftpsState, clientCertEnabled:clientCertEnabled}"

az webapp config hostname list -n my-app -g my-rg -o table
az webapp config ssl list -g my-rg -o table
```

이 값들은 단순한 설정 목록이 아닙니다. HTTPS 강제 여부, client certificate 사용 여부, custom domain 바인딩 상태는 모두 Front-End가 요청을 어떻게 해석하고 어떤 보안 경로를 적용할지와 연결됩니다.

### Affinity는 작은 진단 엔드포인트 하나로 바로 검증할 수 있습니다

운영에서 가장 실용적인 확인 방법은 같은 브라우저 세션이 정말 같은 worker에 계속 붙는지 직접 보는 것입니다. 아래처럼 worker 식별값을 돌려주는 아주 작은 진단 엔드포인트를 두면 ARR Affinity의 효과를 재현 없이 확인할 수 있습니다.

```python
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.get("/diag/worker")
def diag_worker():
    return jsonify(
        hostname=socket.gethostname(),
        instance_id=os.environ.get("WEBSITE_INSTANCE_ID", "unknown"),
        slot=os.environ.get("WEBSITE_SLOT_NAME", "production"),
    )
```

이 엔드포인트를 만든 뒤에는 cookie jar를 유지한 요청과 유지하지 않은 요청을 나눠 보면 됩니다.

```bash
# 같은 세션으로 두 번 호출
curl -s -c cookies.txt -b cookies.txt https://my-app.azurewebsites.net/diag/worker
curl -s -c cookies.txt -b cookies.txt https://my-app.azurewebsites.net/diag/worker

# 쿠키 없이 새 세션처럼 반복 호출
curl -s https://my-app.azurewebsites.net/diag/worker
curl -s https://my-app.azurewebsites.net/diag/worker
```

**Expected output:** affinity가 켜져 있으면 cookie jar를 유지한 두 호출에서 같은 `instance_id`가 반복될 가능성이 높습니다. 반대로 쿠키 없이 호출하면 응답 `instance_id`가 더 쉽게 바뀝니다. 부분 장애가 의심될 때도 이 방법으로 "특정 사용자만 같은 worker에 고정되는가"를 먼저 확인할 수 있습니다.

### ARR Affinity 디버깅 런북: 쿠키, 인스턴스, 지연 분포를 같이 본다

부분 장애를 빠르게 확인하려면 "누가 느린가"보다 "누가 어떤 worker에 고정됐는가"를 먼저 봐야 합니다. 실전에서는 브라우저 쿠키를 보존한 경로와 쿠키를 제거한 경로를 나눠 비교하고, 동일 endpoint의 `WEBSITE_INSTANCE_ID` 분포를 동시에 수집합니다.

```bash
# 1) 쿠키 보존 요청
for i in $(seq 1 8); do
  curl -s -c arr.txt -b arr.txt https://my-app.azurewebsites.net/diag/worker
  echo
done

# 2) 쿠키 없는 요청
for i in $(seq 1 8); do
  curl -s https://my-app.azurewebsites.net/diag/worker
  echo
done
```

여기에 지연 분포를 겹치면 더 강력합니다.

```bash
# 쿠키 보존 경로의 지연
for i in $(seq 1 30); do
  curl -o /dev/null -s -c arr.txt -b arr.txt -w "%{time_total}
"     https://my-app.azurewebsites.net/api/ping
done > sticky-latency.txt

# 쿠키 미보존 경로의 지연
for i in $(seq 1 30); do
  curl -o /dev/null -s -w "%{time_total}
"     https://my-app.azurewebsites.net/api/ping
done > spread-latency.txt
```

**Expected output:** sticky 경로에서 특정 worker로 고정되면 지연 분포가 한쪽으로 기울 수 있습니다. spread 경로는 인스턴스가 분산되며 극단값이 줄어드는 경우가 많습니다. 이 차이가 명확하면 앱 버그보다 degraded worker 고정 가능성을 먼저 조사하는 편이 맞습니다.

### 네트워크 트레이스 관점에서 본 Front-End 판단 경계

Front-End 문제를 잡을 때는 앱 로그만으로 부족합니다. 최소한 다음 세 가지를 네트워크 관점에서 분리해 기록합니다. 첫째, hostname binding이 올바른지, 둘째, TLS/redirect가 의도한지, 셋째, upstream proxy와 App Service 내부 경계에서 쿠키가 어떻게 전달되는지입니다.

```bash
# 리다이렉트와 최종 응답 체인 확인
curl -L -I -s https://my-custom-domain.example.com

# 요청/응답 헤더 전체 확인 (쿠키 전달 포함)
curl -v -s https://my-custom-domain.example.com/diag/worker -o /dev/null
```

이 기록을 남겨 두면 "custom domain에서는 느리고 default domain에서는 빠르다" 같은 이슈를 라우팅 경계 문제로 좁히기 쉬워집니다. 특히 Front Door 또는 Application Gateway를 앞에 둔 구성에서는 외부 계층의 cookie affinity와 App Service 내부 ARRAffinity를 분리해서 판단해야 합니다.

### ARR 관련 장애 타임라인을 남기는 표준 포맷

ARR 의심 장애는 재현보다 타임라인이 중요합니다. 아래 항목을 동일한 포맷으로 남기면 원인 분석이 빨라집니다: 요청 시각, client IP 대역, 쿠키 유무, 반환 instance_id, 응답 시간, 상태 코드. 같은 클라이언트가 장시간 같은 instance_id에 붙고 실패율이 높다면 stickiness가 장애 증폭에 기여했을 가능성이 큽니다.

```bash
for i in $(seq 1 40); do
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  body=$(curl -s -c arr.txt -b arr.txt https://my-app.azurewebsites.net/diag/worker)
  t=$(curl -o /dev/null -s -w "%{time_total}" -c arr.txt -b arr.txt https://my-app.azurewebsites.net/api/ping)
  printf "%s	%s	%s
" "$ts" "$t" "$body"
done
```

이 로그는 incident review에서 "일부 사용자만 실패"를 정량 데이터로 바꿔 줍니다. 감각 대신 분포를 남겨 두면 ARR 설정 변경의 효과도 바로 비교할 수 있습니다.

### ARR 설정 변경 후 회귀 점검

ARR Affinity 토글을 바꾼 뒤에는 로그인, 장바구니, 업로드 같은 상태 의존 경로를 반드시 재검증해야 합니다. sticky 해제 후 숨은 인메모리 의존성이 드러나는 경우가 실제로 자주 발생합니다.

## 흔히 헷갈리는 지점

- **ARRAffinity는 애플리케이션 세션 쿠키가 아닙니다.** 플랫폼이 같은 client를 같은 worker로 보내기 위한 routing hint입니다.
- **custom domain이나 slot 문제와 worker stickiness 문제는 같은 층위가 아닙니다.** 앞단의 앱 식별 단계와 뒷단의 worker 선택 단계를 분리해서 봐야 합니다.
- **앞단 프록시의 affinity가 App Service 내부 affinity를 대체하지는 않습니다.** origin 선택과 worker 선택은 서로 다른 계층의 판단입니다.
- **slot swap은 staging worker와 production worker를 통째로 바꾸는 작업이 아닙니다.** 같은 plan 안에서 warm-up이 끝난 slot으로 Front-End 라우팅 규칙을 바꾸는 흐름입니다.
- **일부 사용자만 실패한다고 해서 원인이 반드시 브라우저나 사용자 데이터에 있는 것은 아닙니다.** degraded worker에 pinned 된 partial outage일 수 있습니다.

## 운영 체크리스트

- [ ] ARR Affinity를 켜 두는지 여부와 그 이유를 문서화했습니다.
- [ ] partial outage 발생 시 worker stickiness를 확인하는 진단 절차를 런북에 넣었습니다.
- [ ] custom domain별 라우팅 우선순위와 redirect 규칙을 정리했습니다.
- [ ] Front-End 5xx와 Worker 5xx를 서로 다른 신호로 관측하도록 대시보드를 구성했습니다.
- [ ] client certificate가 필요한 경로와 그렇지 않은 경로를 분리해 검토했습니다.

## 정리

2화의 핵심은 요청이 worker에 도달하기 전에도 이미 중요한 판단이 여러 번 일어난다는 사실입니다. Front-End는 host와 slot 문맥을 해석하고, ARR은 적절한 worker를 선택하며, ARRAffinity가 켜져 있으면 같은 사용자를 같은 worker에 계속 붙일 수 있습니다. 이 흐름을 모르면 App Service 라우팅 문제는 계속 우연처럼 느껴집니다.

운영적으로 가장 중요한 교훈은 stateless 설계가 단지 미학적 취향이 아니라는 사실입니다. 어느 worker가 요청을 받아도 같은 결과가 나와야 Front-End와 ARR의 분산 모델, scale-out, worker replacement와 자연스럽게 맞물립니다. 반대로 인메모리 세션과 per-worker 로컬 상태에 기대면 routing 계층의 선택이 곧 장애 표면이 됩니다.

다음 글에서는 이 요청이 실제로 도달한 worker 안으로 들어가 보겠습니다. Windows에서는 App Service sandbox가 어떤 제약을 거는지, Linux에서는 container가 어떤 실행 경계가 되는지를 이어서 봅니다.

## 처음 질문으로 돌아가기

- **Front-End는 단순 로드밸런서를 넘어 실제로 어떤 종류의 결정을 먼저 내릴까요?**
  - Front-End는 먼저 host name, custom domain, slot 문맥으로 요청이 어느 앱과 어느 슬롯에 들어가야 하는지 해석합니다. 그다음 ARR이 현재 유효한 worker 후보와 affinity 쿠키를 함께 보고 실제 목적지를 정하므로, Front-End의 첫 판단은 단순 분산보다 앱 식별과 라우팅 문맥 결정에 더 가깝습니다.
- **ARR Affinity 쿠키는 애플리케이션 세션 쿠키와 무엇이 다를까요?**
  - 세션 쿠키는 로그인 상태나 장바구니 같은 business state를 들고 있지만, `ARRAffinity`는 같은 브라우저를 같은 worker에 붙여 두기 위한 플랫폼 쿠키입니다. 그래서 일부 사용자만 느리거나 실패할 때는 애플리케이션 로직보다 먼저, 그 사용자가 문제 있는 worker에 계속 pinned 되었는지를 확인해야 합니다.
- **요청이 어느 앱과 어느 슬롯에 속하는지 정하는 단계와 worker를 고르는 단계는 어떻게 다를까요?**
  - 앞단의 질문은 "이 host와 URL이 production인지 staging인지, 어느 앱으로 들어가야 하는가"이고, 뒷단의 질문은 "그 앱 컨텍스트 안에서 이번 요청을 어느 worker가 받을 것인가"입니다. 이 둘을 분리해야 slot swap을 라우팅 전환으로 읽을 수 있고, partial outage도 custom domain 문제와 worker stickiness 문제로 나눠서 설명할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service Deep Dive (1/6): App Service 플랫폼 아키텍처 — Front-End·Worker·File Server](./01-platform-architecture.md)
- **Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 (현재 글)**
- Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 (예정)
- Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 (예정)
- Azure App Service Deep Dive (5/6): 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 (예정)
- Azure App Service Deep Dive (6/6): 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Using the Application Request Routing Module](https://learn.microsoft.com/iis/extensions/planning-for-arr/using-the-application-request-routing-module)
- [Configure ARRAffinity cookie when accessing Azure App Service behind Azure Application Gateway](https://techcommunity.microsoft.com/blog/appsonazureblog/configure-arraffinity-cookie-when-accessing-azure-app-service-behind-azure-appli/3842511)
- [Overview of Azure App Service](https://learn.microsoft.com/azure/app-service/overview)
- [Architecture best practices for Azure App Service web apps](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps)
- [Deployment slots in Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)

### 관련 시리즈
- [Azure App Service 101 — Request Lifecycle](../../azure-app-service-101/ko/02-request-lifecycle.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-deep-dive/ko/02-front-end-and-arr)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
