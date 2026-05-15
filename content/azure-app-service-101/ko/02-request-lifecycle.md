---
title: 'Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까'
series: azure-app-service-101
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
- Cloud
- Web Apps
last_reviewed: '2026-05-12'
seo_description: 502, 503, timeout이 날 때 App Service 요청 경로를 단계별로 좁혀 가는 기준을 정리합니다.
---

# Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까

새벽 3시에 `502` 알람이 울리면, 가장 먼저 해야 할 일은 로그를 많이 여는 것이 아닙니다. 요청이 앱 코드까지 오기 전에 어디에서 멈췄는지부터 구간을 나눠 보는 일입니다.

이 글은 Azure App Service 101 시리즈의 2번째 글입니다.

App Service의 요청 경로는 한 번에 보이지 않지만, DNS부터 Frontend, Worker, 앱 프로세스까지 단계를 나눠 보면 장애 대응 속도가 크게 빨라집니다. 여기서는 요청이 앱에 도달하기까지 어떤 홉을 지나고, 각 단계에서 어떤 실패 신호가 나타나는지 운영자 관점으로 따라가 보겠습니다.

---

> App Service의 요청 수명 주기는 안정적인 홉이 이어진 체인입니다. 체감 지연은 대개 가운데 warm-up 단계에서 생깁니다.

## 이 글에서 다룰 문제

- 요청이 앱에 도달하기 전에 Front End, ARR, Worker 같은 Azure 구성 요소를 어떤 순서로 거칠까요?
- ARR Affinity 쿠키는 무엇을 위해 존재하고, 언제 끄는 편이 맞을까요?
- Worker가 idle 상태에서 깨어날 때 warm-up 단계는 어느 정도 지연을 만들까요?
- 어떤 신호가 Worker 종료나 재시작을 유발하고, 그 영향이 사용자 요청에 어떻게 나타날까요?
- sticky routing은 수평 확장(horizontal scaling)과 어디에서 충돌할까요?

## 전체 요청 흐름

사용자 HTTP 요청은 앱에 도달하기 전에 아래 레이어를 지납니다.

```text
Client → DNS → Azure Load Balancer → App Service Frontend → Worker Instance → App Process
```

각 단계마다 다른 문제가 생길 수 있고, 그 결과로 보이는 에러 코드도 달라집니다.

![Request path from client to app](../../../assets/azure-app-service-101/02/01-full-request-lifecycle.ko.png)

*클라이언트에서 앱까지 이어지는 요청 경로*

---

## Stage 1: DNS와 글로벌 진입점

### DNS Resolution

요청은 앱 호스트 이름의 DNS 해석부터 시작합니다.

- **기본 도메인:** `<app-name>.azurewebsites.net`
- **커스텀 도메인:** `www.myapp.com` (`CNAME` 구성)

### TLS Handshake

DNS 해석이 끝나면 다음 순서가 이어집니다.

1. TLS handshake 수행
2. SNI(Server Name Indication)로 앱 식별
3. Host header로 올바른 앱에 라우팅

```bash
# Verify DNS resolution
nslookup myapp.azurewebsites.net

# Check TLS certificate
openssl s_client -connect myapp.azurewebsites.net:443 -servername myapp.azurewebsites.net
```

---

## Stage 2: Frontend Routing

App Service Frontend는 아래 역할을 맡습니다.

| 역할 | 설명 |
|------|-------------|
| TLS Termination | HTTPS 복호화 |
| Host Validation | 요청이 올바른 앱으로 향하는지 검증 |
| Access Restriction Evaluation | IP 제한, 인증 검사 |
| Instance Selection | 정상 Worker로 라우팅 |

![Frontend routing and rejection checks](../../../assets/azure-app-service-101/02/02-frontend-routing-decision.ko.png)

*Frontend의 라우팅과 차단 검사*

### Frontend가 실패 지점일 때

정상 backend가 하나도 없으면 요청은 **앱 코드가 실행되기 전에** 실패합니다.

| Error Code | Meaning |
|------------|---------|
| `403` | 접근 제한에 의해 차단 |
| `502` | backend 연결 실패 |
| `503` | 서비스 사용 불가 |

```bash
# Check access restriction settings
az webapp config access-restriction show \
 --resource-group $RG \
 --name $APP_NAME \
 --output json
```

**예시 출력:**
```json
{
 "ipSecurityRestrictions": [
 {
 "action": "Allow",
 "ipAddress": "203.0.113.0/24",
 "name": "corp-office",
 "priority": 100
 }
 ]
}
```

앱 로그가 비어 있는데 `403`만 보인다면, 애플리케이션보다 Frontend 정책을 먼저 확인해야 합니다.

---

## Stage 3: Worker Reverse Proxy

Worker 인스턴스 안에서는 로컬 reverse proxy가 요청을 앱 프로세스로 전달합니다.

### Port Contract

핵심은 하나입니다. 앱은 반드시 **플랫폼이 제공한 포트에 바인딩**해야 합니다.

```python
# Hardcoded local port
app.run(host="0.0.0.0", port=5000)

# Read the port from the environment
import os
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

**자주 하는 실수:**
- 로컬에서는 되는데 배포 후 실패함
- 프로세스는 떠 있지만 요청은 실패함

이 문제는 결국 “프로세스가 실행 중인가”가 아니라 “플랫폼과 실행 계약을 맞췄는가”의 문제입니다.

---

## Stage 4: Application Execution

이제 요청이 앱 코드에 도달합니다.

### 성능에 영향을 주는 요소

| Factor | Description |
|--------|-------------|
| CPU/Memory usage | 인스턴스 리소스 포화 |
| External dependencies | DB, API 호출 지연 |
| Threads/Event loop | 동시성 한계 |
| Connection pools | outbound 연결 관리 |

### 응답 반환 경로

응답은 반대 순서로 돌아갑니다.

```text
App → Worker → Frontend → Load Balancer → Client
```

플랫폼은 이 경로에서 다음 헤더를 추가할 수 있습니다.

- 압축 관련 헤더
- 보안 헤더
- reverse proxy 메타데이터

---

## Timeouts and Connection Behavior

### Platform Timeouts

App Service에는 여러 층의 timeout이 있습니다.

| Timeout | Impact |
|---------|--------|
| Frontend request timeout | 긴 요청이 `504 Gateway Timeout`으로 끝남 |
| Idle connection timeout | idle 소켓 종료 |
| Slow dependencies | 큐 적체, tail latency 증가 |

### 설계 가이드라인

```python
# Long-running work inside the request path
@app.route('/export')
def export():
 # 10-minute data processing...
 return huge_result # Timeout risk!

# Hand the long job off to async processing
@app.route('/export')
def export():
 job_id = queue_export_job()
 return {"status": "accepted", "jobId": job_id}, 202
```

**원칙:**
- 대화형 요청은 짧게 유지합니다 (`< 30`초 권장).
- 긴 작업은 background로 넘깁니다.
- `202 Accepted`를 반환하고 poll 또는 webhook으로 이어갑니다.

---

## Instance Selection and Session Affinity

### 기본 동작: Round Robin

Frontend는 기본적으로 정상 인스턴스들 사이에 트래픽을 분산합니다.

### Session Affinity (ARR Affinity)

특정 클라이언트를 같은 인스턴스에 고정할 수도 있습니다.

```text
Client A ─(Affinity Cookie)─→ Instance 2
Client B ─(Affinity Cookie)─→ Instance 1
```

**트레이드오프:**

| Pros | Cons |
|------|------|
| 레거시 세션 코드 지원 | 부하 분산 불균형 |
| 인메모리 캐시 활용 | 인스턴스 장애에 취약 |

**권장:** 세션과 상태는 **외부 저장소**(Redis, DB)에 둡니다.

```bash
# Disable ARR Affinity
az webapp update \
 --resource-group $RG \
 --name $APP_NAME \
 --client-affinity-enabled false
```

---

## Health Check and Traffic Eligibility

Health Check는 인스턴스가 트래픽을 받을 자격이 있는지 판단합니다.

### 상태별 동작

| State | Traffic |
|-------|---------|
| Healthy | 라우팅 풀에 포함 |
| Unhealthy | 라우팅 풀에서 제거 |
| Recovering | probe 통과 후 다시 포함 |

![Instance state changes from health checks](../../../assets/azure-app-service-101/02/03-health-check-state-machine.ko.png)

*Health Check에 따른 인스턴스 상태 변화*

### Health Probe 설계 원칙

```python
@app.route('/health')
def health():
 # 1. Keep it lightweight
 # 2. Check only dependencies critical for traffic handling
 # 3. Avoid slow external calls
 
 try:
 # Simple check of critical dependencies
 db.execute("SELECT 1")
 return {"status": "healthy"}, 200
 except Exception as e:
 return {"status": "unhealthy", "reason": str(e)}, 503
```

Health endpoint는 진단 보고서가 아니라 라우팅 신호입니다. 무거운 외부 호출을 몰아넣으면 정상 인스턴스도 unhealthy 판정을 받을 수 있습니다.

---

## Impact of Deployment Slots

Deployment Slot은 배포 중 사용자 영향도를 줄이는 데 도움이 됩니다.

### Slot Swap Process

1. 새 버전을 Staging Slot에 배포
2. Staging에서 warm-up 완료
3. Production은 계속 트래픽 처리
4. Slot Swap으로 트래픽 전환

**장점:**
- cold start 노출 감소
- 실패한 배포를 쉽게 rollback 가능

---

## Observability: Tracing the Entire Lifecycle

문제를 진단하려면 각 단계를 관측 신호와 연결해야 합니다.

### Correlation Signals

| Signal | Purpose |
|--------|---------|
| Request logs | 상태 코드 분포 파악 |
| Frontend diagnostics | 플랫폼 레벨 오류 파악 |
| Instance restarts | 안정성 문제 파악 |
| Dependency timing | 외부 호출 병목 파악 |
| Correlation ID | 요청 단위 추적 |

### Log Configuration

```bash
# Enable HTTP logging
az webapp log config \
 --resource-group $RG \
 --name $APP_NAME \
 --application-logging filesystem \
 --detailed-error-messages true \
 --failed-request-tracing true \
 --web-server-logging filesystem

# Real-time log stream
az webapp log tail \
 --resource-group $RG \
 --name $APP_NAME
```

---

## Common Failure Patterns

![Status codes mapped to failure layers](../../../assets/azure-app-service-101/02/04-failure-pattern-map.ko.png)

*상태 코드와 실패 레이어의 대응 관계*

| Symptom | Suspected Layer | First Check |
|---------|----------------|-------------|
| 403 (no app logs) | Frontend | 접근 제한, 인증 설정 |
| 502/503 spike | Worker/app startup | 재시작 이벤트, Health probe |
| 504 responses | Long request path | 의존성 지연, 요청 설계 |
| Intermittent timeouts | Outbound | SNAT, connection pool |

### Troubleshooting Workflow

1. **Check Frontend**: DNS/TLS/access restrictions
2. **Check Worker**: Health status, restart events
3. **Check App Process**: Ready state, port binding
4. **Check Dependencies**: External call latency, connection issues

---

## 운영 체크리스트

- [ ] Front End -> ARR -> Worker 경로를 타이밍 예산과 함께 다이어그램으로 남겼다
- [ ] ARR Affinity를 유지할 조건과 끌 조건을 문서화했다
- [ ] 대표 앱에서 cold-start와 warm-instance latency를 직접 측정했다
- [ ] Worker recycle 이벤트에 대한 알림을 연결했다
- [ ] sticky routing이 scale에 미치는 영향을 용량 계획에 반영했다

---

## 정리

Request Lifecycle을 단계별로 이해하면 장애 대응의 출발점이 분명해집니다.

- **문제가 난 레이어를 빠르게 좁힐 수 있습니다.**
- **어떤 로그와 메트릭을 먼저 봐야 할지 정해집니다.**
- **증상에 맞는 해결책을 더 빨리 적용할 수 있습니다.**

`502` 하나만 봐도 DNS, Frontend, Worker, 앱 프로세스, 외부 의존성 중 어디를 먼저 봐야 할지 감이 생기면 절반은 끝난 셈입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service란? - 플랫폼 아키텍처 이해하기](./01-what-is-app-service.md)
- **Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 (현재 글)**
- Hosting Models: 어떤 플랜을 선택해야 할까? (예정)
- 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) (예정)
- Configuration 마스터하기: App Settings & 환경변수 (예정)
- 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 (예정)
- Scaling 101: 언제 Scale Up vs Scale Out? (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Deployment Slots in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [Inbound and outbound IPs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-inbound-outbound-ips)
- [Troubleshoot diagnostic logs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)

### 관련 시리즈
- [Azure Functions 101](../../azure-functions-101/ko/)

---

Tags: Azure, App Service, Cloud, Web Apps
