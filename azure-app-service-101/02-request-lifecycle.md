# Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까

> Azure App Service 101 시리즈 (2/7)

새벽 3시, 알람이 울립니다. 프로덕션 API가 갑자기 `502`를 뱉기 시작했습니다.  
앱 로그는 비어 있고, 코드 배포도 없었고, 로컬에서는 멀쩡합니다.

이럴 때 제일 위험한 대응은 **아무 로그나 닥치는 대로 뒤지는 것**입니다. App Service 문제는 “앱이 죽었나?”만으로 설명되지 않습니다. 요청은 앱 코드에 닿기 전에도 여러 관문을 통과하고, 각 레이어는 서로 다른 방식으로 실패합니다.

이번 글은 그 관문을 하나씩 따라가며, **“이 에러는 어느 레이어의 냄새인가?”**를 구분하는 감각을 만드는 글입니다. DNS, TLS/SNI, Frontend 라우팅, Worker reverse proxy, 앱 프로세스 실행, timeout, session affinity, health check, deployment slot까지 모두 **디버깅 여정**으로 엮어 보겠습니다.

---

## 이 글에서 만들 멘탈 모델

사용자 요청은 대략 아래 순서로 앱에 도착합니다.

```text
Client → DNS → Azure Load Balancer → App Service Frontend → Worker Instance → App Process
```

그리고 응답은 역순으로 돌아갑니다.

![App Service 요청 수명주기 전체 흐름](./assets/azure-app-service-101/02/01-full-request-lifecycle.png)

이 흐름을 머릿속에 넣어두면 장애 대응이 훨씬 빨라집니다.

- **DNS/TLS 단계**에서 틀어지면: 도메인, 인증서, SNI, host name부터 봐야 합니다.
- **Frontend 단계**에서 막히면: 접근 제한, 호스트 검증, 건강한 백엔드 유무가 핵심입니다.
- **Worker/App 단계**에서 틀어지면: 포트 바인딩, 앱 시작 실패, 느린 의존성, resource saturation을 의심해야 합니다.
- **Response 단계**에서 늦어지면: timeout, outbound dependency, retry 폭주를 봐야 합니다.

즉, Request Lifecycle을 안다는 건 단순한 구조 설명이 아니라 **“문제가 난 지점을 빠르게 좁히는 기술”**입니다.

---

## 1. 첫 관문: DNS가 맞는 문으로 보내고 있는가

가장 먼저 확인할 것은 의외로 애플리케이션이 아닙니다. **클라이언트가 어디로 가고 있는지**입니다.

App Service 앱은 기본적으로 다음 호스트 이름을 가집니다.

- 기본 도메인: `<app-name>.azurewebsites.net`
- 커스텀 도메인: 예) `www.example.com`

사용자는 호스트 이름을 입력하지만, 실제 통신은 DNS 해석 결과를 따라갑니다.

```bash
# 기본 호스트 해석 확인
nslookup myapp.azurewebsites.net

# 커스텀 도메인 해석 확인
nslookup www.example.com
```

여기서 중요한 포인트는 두 가지입니다.

1. **커스텀 도메인이 올바르게 연결되어 있는가**  
   CNAME 또는 필요한 DNS 레코드가 App Service를 가리켜야 합니다.
2. **클라이언트가 기대한 호스트 이름으로 들어오는가**  
   App Service는 host name과 TLS 정보를 보고 어느 앱으로 보낼지 판단합니다.

### 실전 시나리오: “로컬에선 되는데 Azure에서만 안 돼요”

이 말은 생각보다 자주 **코드 문제가 아니라 도메인/호스트 문제**입니다.

- 로컬: `localhost:5000`으로 테스트 → 정상
- Azure 기본 도메인: 정상
- 커스텀 도메인: 간헐적 실패 또는 인증서 경고

이 경우 앱 코드보다 먼저 봐야 하는 건 다음입니다.

- DNS 전파가 끝났는가?
- 올바른 host name이 App Service에 등록되어 있는가?
- 요청이 기대한 SNI와 Host 헤더로 들어오는가?

---

## 2. TLS 핸드셰이크와 SNI: “어느 앱을 찾으시는 거죠?”

DNS 다음은 TLS입니다. HTTPS 요청에서는 단순히 암호화만 일어나는 게 아닙니다. App Service는 **SNI(Server Name Indication)** 와 Host 헤더를 이용해 어떤 앱으로 보내야 하는지 결정합니다.

```bash
openssl s_client -connect myapp.azurewebsites.net:443 -servername myapp.azurewebsites.net
```

이 단계에서 기억할 점:

- TLS는 Frontend에서 종료됩니다.
- SNI가 기대와 다르면 잘못된 인증서/앱으로 보일 수 있습니다.
- 커스텀 도메인 연결이 어긋나면 앱 코드까지 가지도 못하고 초입에서 실패할 수 있습니다.

### 놓치기 쉬운 핵심

많은 팀이 `502`, `403`, 인증서 경고를 보면 곧바로 앱 로그부터 찾습니다. 하지만 **앱 로그가 비어 있는 이유가 앱까지 요청이 오지 않았기 때문**일 수 있습니다.

즉, “로그가 없다”는 건 “문제가 없다”가 아니라, 오히려 **더 바깥 레이어에서 죽었다**는 신호일 수 있습니다.

---

## 3. Frontend: App Service의 진짜 문지기

TLS를 통과한 요청은 App Service **Frontend**로 들어옵니다. 여기서 끝나는 일이 생각보다 많습니다.

Frontend가 하는 일은 대략 이렇습니다.

| 역할 | 설명 |
|---|---|
| TLS 종료 | HTTPS 암호화 해제 |
| 호스트 검증 | 요청 host name이 어느 앱에 매핑되는지 확인 |
| 접근 제한 평가 | Access Restrictions, 인증/인가 관련 게이트 확인 |
| 인스턴스 선택 | 건강한 Worker 후보 중 어디로 보낼지 결정 |

![Frontend 라우팅 결정 흐름](./assets/azure-app-service-101/02/02-frontend-routing-decision.png)

여기서 핵심은 **Frontend가 건강한 백엔드를 찾지 못하면 앱 코드가 실행되기 전에 실패한다**는 점입니다.

### Frontend 레이어에서 자주 보이는 증상

| 증상 | 흔한 의미 |
|---|---|
| `403` | 접근 제한, 인증/인가 또는 정책에 의해 차단 |
| `502` | 백엔드 연결 실패 또는 준비되지 않은 인스턴스 |
| `503` | 사용할 수 있는 정상 인스턴스 부족 |

> 같은 5xx라도 “앱 코드에서 던진 500”과 “Frontend가 Worker를 못 붙인 502/503”은 완전히 다른 사건입니다.

### 실전 시나리오: 3am의 502

당직 엔지니어가 제일 먼저 해야 할 질문은 이것입니다.

**“이 502는 앱이 응답해서 만든 것인가, 아니면 Frontend가 백엔드에 붙지 못해 만든 것인가?”**

그 차이를 가르면 탐색 범위가 순식간에 절반 이하로 줄어듭니다.

먼저 Access Restrictions부터 확인합니다.

```bash
az webapp config access-restriction show \
  --resource-group $RG \
  --name $APP_NAME \
  --output json
```

예를 들어 사내 IP만 허용하는 규칙이 있는데, 배포 후 NAT가 바뀌었거나 테스트 트래픽이 다른 네트워크에서 들어오면 앱은 정상이어도 `403`이 납니다.

```json
{
  "ipSecurityRestrictions": [
    {
      "name": "corp-office",
      "priority": 100,
      "action": "Allow",
      "ipAddress": "203.0.113.0/24"
    }
  ]
}
```

앱 로그가 없고 `403`만 쌓이면, 애플리케이션보다 Frontend 정책을 먼저 봐야 하는 이유가 여기에 있습니다.

---

## 4. Worker Instance: 요청이 실제 실행 노드에 올라타는 순간

Frontend가 요청을 넘길 대상이 정해지면, 그다음은 **Worker Instance**입니다. 이 Worker 안에서 플랫폼의 로컬 reverse proxy가 앱 프로세스까지 요청을 전달합니다.

이 단계의 대표적인 함정이 바로 **포트 계약(port contract)** 입니다.

### “로컬에서는 되는데 Azure에서는 502”의 대표 원인

앱이 **플랫폼이 기대하는 포트에 바인딩하지 않으면**, 프로세스가 떠 있어 보여도 실제로는 요청을 받을 수 없습니다. 그러면 Frontend 입장에서는 백엔드 연결 실패처럼 보이고 `502`가 납니다.

```python
# ❌ 로컬 개발 포트를 하드코딩한 예
app.run(host="0.0.0.0", port=5000)

# ✅ 플랫폼이 제공한 포트 사용
import os

port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

Python/Flask 예시를 들었지만 핵심은 언어가 아닙니다.

- **Built-in runtime**: 플랫폼이 제공하는 포트에 맞춰 들어야 함
- **Custom container**: 호스팅 모델에 따라 `WEBSITES_PORT` 같은 설정을 정확히 맞춰야 함

### 디버깅 포인트

- 앱 시작 로그는 정상인가?
- 실제 리슨 포트가 플랫폼 기대와 일치하는가?
- startup command 변경 직후부터 실패했는가?
- health probe가 포트 문제 때문에 앱을 unhealthy로 보고 있진 않은가?

이 구간에서 중요한 건, **프로세스가 살아 있는 것과 요청을 받을 준비가 된 것은 다르다**는 사실입니다.

---

## 5. 앱 프로세스: 이제야 비즈니스 로직이 시작된다

요청이 앱 프로세스에 도달하면 그제야 우리가 익숙한 세상이 시작됩니다. 프레임워크, middleware, DB 호출, 외부 API, 캐시, 인증 코드가 모두 여기 있습니다.

하지만 운영에서 중요한 건 “앱 코드가 실행된다”보다 **“제시간에 응답하느냐”** 입니다.

### 성능을 흔드는 현실적인 요인

| 요소 | 운영에서 실제로 보이는 문제 |
|---|---|
| CPU/메모리 포화 | 특정 인스턴스만 느려짐, tail latency 증가 |
| 외부 의존성 지연 | DB/API 느려져 전체 요청이 줄줄이 대기 |
| 동시성 모델 한계 | worker thread/event loop 포화 |
| 커넥션 풀 문제 | 대기열 증가, timeout, 재시도 폭주 |

응답은 다시 아래 경로를 따라 돌아갑니다.

```text
App Process → Worker → Frontend → Azure Load Balancer → Client
```

플랫폼은 이 과정에서 압축, 보안 헤더, reverse proxy 메타데이터 같은 일부 처리를 추가할 수 있습니다.

---

## 6. Timeout: “느린 요청”은 결국 장애로 번진다

운영에서 가장 위험한 오해 중 하나는 이것입니다.

> “느릴 뿐이지 실패한 건 아니잖아요?”

App Service에서는 느린 요청이 결국 **timeout**, **queue 적체**, **retry 폭주**, **503 증가**로 이어질 수 있습니다.

### 기억해야 할 timeout 사고 방식

- Frontend 수준에서 너무 오래 걸리는 요청은 결국 `504 Gateway Timeout`으로 끝날 수 있습니다.
- 유휴 연결은 idle timeout에 걸려 닫힐 수 있습니다.
- 느린 외부 의존성 하나가 전체 요청 풀을 잠식할 수 있습니다.

### 실전 시나리오: 간헐적 timeout

증상은 이런 식입니다.

- 평균 응답은 괜찮음
- 그런데 피크 시간대에만 가끔 `504`
- 앱 CPU는 아주 높진 않음
- DB 또는 외부 API 호출 시간이 길어짐

이건 보통 “앱이 완전히 죽었다”기보다, **느린 의존성 때문에 요청 체인이 길어져 Frontend가 기다리다 포기하는 상황**입니다.

그래서 장시간 작업은 요청-응답 경로 안에 두지 않는 게 좋습니다.

```python
from flask import jsonify

@app.post("/exports")
def create_export():
    job_id = queue_export_job()
    return jsonify({"status": "accepted", "jobId": job_id}), 202
```

이 패턴이 중요한 이유는 간단합니다.

- 대화형 요청은 짧게 끝내고
- 긴 작업은 큐/백그라운드로 넘기고
- 클라이언트에는 `202 Accepted`를 반환해 폴링이나 웹훅으로 이어가야

웹 트래픽 경로가 병목의 희생양이 되지 않습니다.

---

## 7. Session Affinity: “같은 사용자”를 같은 인스턴스로 묶을 것인가

여러 인스턴스로 scale-out된 App Service에서 Frontend는 기본적으로 건강한 인스턴스들로 트래픽을 분산합니다. 이때 **ARR Affinity**를 켜면 특정 클라이언트를 같은 인스턴스로 더 오래 붙잡아 둘 수 있습니다.

```text
Client A ──(Affinity Cookie)──▶ Instance 2
Client B ──(Affinity Cookie)──▶ Instance 1
```

이 기능은 레거시 세션 코드를 살릴 때 유용하지만, 동시에 위험도 분명합니다.

| 장점 | 단점 |
|---|---|
| 인메모리 세션/캐시를 임시로 유지하기 쉬움 | 부하 분산이 고르지 않을 수 있음 |
| 상태 의존적인 레거시 앱에 유리 | 특정 인스턴스 장애 시 체감 영향이 커짐 |

그래서 장기적으로는 **세션과 상태를 외부 저장소(Redis, DB)로 분리**하는 것이 정석입니다.

```bash
az webapp update \
  --resource-group $RG \
  --name $APP_NAME \
  --client-affinity-enabled false
```

### 놓치기 쉬운 핵심

“왜 어떤 사용자만 느리죠?” 같은 문의가 들어오면, 코드보다 먼저 **특정 인스턴스에 세션이 고정되어 있지 않은지**를 떠올릴 가치가 있습니다. 문제 인스턴스 하나가 전체 장애처럼 보이지 않고, 일부 사용자만 아프게 만들기 때문입니다.

---

## 8. Health Check: 트래픽을 받을 자격을 심사하는 레이어

Health Check는 단순한 모니터링 기능이 아닙니다. **어느 인스턴스에 실제 트래픽을 보낼지 결정하는 운영 메커니즘**입니다.

App Service는 설정한 경로를 주기적으로 호출합니다. 문서 기준으로 기본 동작은 다음과 같습니다.

- 각 인스턴스의 Health Check 경로를 **1분 간격**으로 확인
- `200~299`를 반환하면 healthy로 간주
- 연속 실패가 누적되면 인스턴스를 load balancer 풀에서 제외
- 다시 정상 응답하면 라우팅 풀에 복귀
- 장시간 unhealthy 상태가 지속되면 인스턴스 교체를 시도

![Health Check 상태 전이](./assets/azure-app-service-101/02/03-health-check-state-machine.png)

문서에서 특히 중요한 디테일도 기억해둘 만합니다.

- Health Check는 기본적으로 **302 redirect를 따라가지 않습니다**.
- 응답이 **1분 안에 끝나지 않아도 unhealthy**로 간주될 수 있습니다.
- 단일 인스턴스에서는 라우팅 제외 효과가 제한적이므로, **2개 이상 인스턴스**에서 진가가 납니다.

### 좋은 Health 엔드포인트의 조건

```python
from flask import jsonify

@app.get("/health")
def health():
    try:
        db.execute("SELECT 1")
        return jsonify({"status": "healthy"}), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "reason": str(exc)}), 503
```

원칙은 이렇습니다.

1. **가벼워야 합니다.**  
   무거운 쿼리로 health check를 만들면 진단이 아니라 부하를 만듭니다.
2. **필수 의존성만 확인해야 합니다.**  
   실제 트래픽을 처리할 수 있는지 판단하는 데 필요한 최소한만 봐야 합니다.
3. **warm-up이 끝난 뒤에만 200을 반환해야 합니다.**  
   아직 준비 안 된 인스턴스를 너무 일찍 healthy 처리하면 오히려 502/503이 늘어납니다.

### 실전 시나리오: 재배포 후 간헐적 503

배포는 성공했는데 몇 분 동안만 에러가 튀고 곧 사라지는 경우가 있습니다. 이런 건 종종 코드 버그보다 **새 인스턴스가 준비되기 전에 트래픽을 받는 문제**, 혹은 health endpoint 설계가 부정확한 문제입니다.

---

## 9. Deployment Slots: 배포도 Request Lifecycle의 일부다

많은 사람들이 slot을 배포 편의 기능으로만 보지만, 운영 관점에서는 **요청 흐름을 안전하게 전환하는 장치**에 가깝습니다.

일반적인 흐름은 다음과 같습니다.

1. 새 버전을 staging slot에 배포
2. staging slot 인스턴스가 기동 및 warm-up 수행
3. production은 기존 트래픽을 계속 처리
4. swap 이후 라우팅이 새 버전으로 전환

이 패턴의 장점은 명확합니다.

- cold start를 사용자에게 직접 노출할 가능성을 줄여 줌
- 잘못 배포했을 때 이전 production으로 되돌리기 쉬움
- Health Check와 warm-up을 배포 파이프라인에 자연스럽게 녹일 수 있음

문서상으로도 slot swap은 대상 슬롯의 설정을 적용하고, source 슬롯 인스턴스를 재시작하고, warm-up을 거친 뒤 라우팅을 바꾸는 식으로 진행됩니다. 즉, **swap은 단순한 이름 바꾸기가 아니라 준비 상태를 검증하는 절차**입니다.

```bash
az webapp deployment slot swap \
  --resource-group $RG \
  --name $APP_NAME \
  --slot staging \
  --target-slot production
```

### 운영 팁

- Health Check가 production과 staging에서 일관되게 동작하는지 확인하세요.
- swap 전 warm-up 경로가 실제 앱 준비 상태를 반영하는지 검증하세요.
- “배포는 성공했는데 직후 몇 분만 아프다”는 문제는 slot/warm-up 설계로 크게 줄일 수 있습니다.

---

## 10. 관측성: 요청이 어느 레이어에서 죽었는지 연결해서 본다

좋은 트러블슈팅은 로그를 많이 보는 것이 아니라, **어떤 레이어의 시그널을 연결해서 보느냐**에 달려 있습니다.

### 어떤 시그널을 묶어 볼까

| 시그널 | 질문 |
|---|---|
| Request 로그/상태 코드 분포 | 실패가 4xx인가, 5xx인가? 특정 시점부터 증가했는가? |
| 인스턴스 재시작 이벤트 | 배포/설정 변경/플랫폼 이벤트 직후인가? |
| Health Check 상태 | 특정 인스턴스가 라우팅 풀에서 빠졌는가? |
| 의존성 타이밍 | DB/API가 레이턴시를 키우는가? |
| Correlation ID / Trace | 한 요청을 끝까지 추적할 수 있는가? |

로그 설정도 기본기입니다.

```bash
az webapp log config \
  --resource-group $RG \
  --name $APP_NAME \
  --application-logging filesystem \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --web-server-logging filesystem
```

```bash
az webapp log tail \
  --resource-group $RG \
  --name $APP_NAME
```

참고로 문서상 세부 사항도 알아둘 필요가 있습니다.

- Application logging은 Windows/Linux 모두 가능하지만 저장 위치와 방식이 다를 수 있습니다.
- Web server logging, detailed error, failed request tracing은 **주로 Windows 중심 기능**입니다.
- Linux 또는 custom container에서는 `/home/LogFiles` 중심으로 보는 흐름에 익숙해지는 게 좋습니다.

즉, “로그가 안 보인다”는 말도 **플랫폼/호스팅 모드 차이**를 같이 봐야 해석이 됩니다.

---

## 11. 실패 패턴 맵: 상태 코드로 레이어를 역추적하기

실전에서는 에러 메시지가 완전한 진실을 말해주지 않습니다. 하지만 어디를 먼저 볼지 정하는 데는 충분한 힌트가 됩니다.

![오류 코드와 실패 레이어 매핑](./assets/azure-app-service-101/02/04-failure-pattern-map.png)

### 빠른 해석표

| 증상 | 가장 먼저 의심할 레이어 | 첫 체크 포인트 |
|---|---|---|
| `403` + 앱 로그 거의 없음 | Frontend | Access Restrictions, 인증/인가, host routing |
| `502` 직후 재배포/설정변경 | Worker/App start | 포트 바인딩, startup command, warm-up |
| `503` 급증 | Health / instance pool | unhealthy 인스턴스, scale 상태, restart |
| `504` | 긴 요청 경로 | 느린 DB/API, timeout, request design |
| 일부 사용자만 문제 | Affinity / 특정 인스턴스 | ARR cookie, 인스턴스별 편차 |

### 3분 트러블슈팅 루틴

1. **앱 로그가 있는가?**  
   없다면 DNS/TLS/Frontend 쪽부터 의심합니다.
2. **최근 배포나 설정 변경이 있었는가?**  
   있었다면 포트, startup, slot swap, warm-up을 먼저 봅니다.
3. **모든 사용자에게 재현되는가? 일부만 그런가?**  
   일부라면 affinity 또는 특정 worker 문제일 수 있습니다.
4. **5xx가 즉시 나는가, 오래 기다리다 나는가?**  
   즉시면 start/routing, 오래 기다리다 나면 dependency/timeout 쪽입니다.

이 루틴만 익혀도 “무작정 로그 뒤지기”에서 “가설 기반 디버깅”으로 넘어갈 수 있습니다.

---

## 12. 운영 체크리스트: Request Lifecycle 관점에서 점검하기

배포 전이나 장애 후 점검 때는 아래 질문을 체크리스트처럼 써먹을 수 있습니다.

### 진입 경로

- [ ] 기본 도메인과 커스텀 도메인이 기대한 대로 해석되는가?
- [ ] TLS/SNI/host name 구성이 일치하는가?
- [ ] 접근 제한이 실제 클라이언트 경로와 맞는가?

### 실행 경로

- [ ] 앱이 플랫폼이 기대하는 포트에 바인딩하는가?
- [ ] startup command와 런타임 구성이 현재 호스팅 모드와 맞는가?
- [ ] 긴 작업을 request path 밖으로 분리했는가?

### 분산/복구 경로

- [ ] ARR Affinity가 꼭 필요한가?
- [ ] Health Check 경로가 가볍고 정확한가?
- [ ] 두 개 이상 인스턴스로 health-based rerouting이 가능하게 운영하는가?
- [ ] slot warm-up과 swap 전략이 준비돼 있는가?

### 관측 경로

- [ ] 상태 코드 분포와 인스턴스 이벤트를 같이 볼 수 있는가?
- [ ] 앱/플랫폼 로그 위치를 팀이 알고 있는가?
- [ ] dependency latency와 timeout을 추적할 수 있는가?

---

## 정리

Azure App Service의 Request Lifecycle을 이해하면, 장애가 났을 때 질문이 달라집니다.

- “앱이 죽었나?” 대신 **“어느 레이어에서 죽었나?”**를 묻게 되고
- “왜 로그가 없지?” 대신 **“앱까지 요청이 왔나?”**를 확인하게 되고
- “일단 재배포해보자” 대신 **“routing, warm-up, dependency 중 무엇이 문제인가?”**를 좁혀 갈 수 있습니다.

이게 바로 운영에서 큰 차이를 만듭니다. Request Lifecycle은 이론이 아니라, **502·503·504를 읽는 지도**이기 때문입니다.

다음 글에서는 이 지도를 바탕으로, 아예 **어떤 Hosting Model과 Plan을 선택해야 이런 문제를 덜 만들 수 있는지**로 넘어가 보겠습니다. 같은 App Service라도 Free, Basic, Standard, Premium, Linux, Windows, Code, Container의 선택이 운영 경험을 완전히 바꿉니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. **[현재 글] Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까**
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Monitor the Health of App Service Instances (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/monitor-instances-health-check)
- [Deployment Slots in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [Inbound and outbound IPs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-inbound-outbound-ips)
- [Troubleshoot diagnostic logs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)

---
