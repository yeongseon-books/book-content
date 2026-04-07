# Request Lifecycle: 요청이 앱에 도달하기까지

> Azure App Service 101 시리즈 (2/7)

"왜 내 앱이 502 에러를 반환하지?" "갑자기 응답이 느려졌는데 원인이 뭘까?"

이런 질문에 답하려면 **요청이 앱에 도달하기까지의 전체 여정**을 이해해야 합니다. 이 글에서는 Azure App Service의 Request Lifecycle을 단계별로 살펴보겠습니다.

---

## 전체 요청 흐름

사용자의 HTTP 요청이 여러분의 앱에 도달하기까지, 다음 레이어를 거칩니다:

```
Client → DNS → Azure Load Balancer → App Service Frontend → Worker Instance → App Process
```

각 단계에서 문제가 발생할 수 있으며, 에러 메시지가 다르게 나타납니다.

![IMAGE: Request Lifecycle 전체 흐름도]
`📸 캡처: Request Lifecycle 다이어그램 (draw.io로 그리기)`

---

## Stage 1: DNS와 Global Entry

### DNS 해석

요청은 앱 호스트네임의 DNS 해석부터 시작합니다.

- **기본 도메인:** `<app-name>.azurewebsites.net`
- **커스텀 도메인:** `www.myapp.com` (CNAME 설정 시)

### TLS Handshake

DNS 해석 후:
1. TLS 핸드셰이크 발생
2. SNI(Server Name Indication)로 앱 식별
3. Host 헤더로 정확한 앱에 라우팅

```bash
# DNS 해석 확인
nslookup myapp.azurewebsites.net

# TLS 인증서 확인
openssl s_client -connect myapp.azurewebsites.net:443 -servername myapp.azurewebsites.net
```

![IMAGE: Custom Domain 설정 화면]
`📸 캡처: Azure Portal → App Service → Custom domains`

---

## Stage 2: Frontend 라우팅

App Service Frontend는 다음 역할을 수행합니다:

| 역할 | 설명 |
|------|------|
| TLS 종료 | HTTPS 암호화 해제 |
| 호스트 검증 | 요청이 올바른 앱으로 가는지 확인 |
| 접근 제한 평가 | IP 제한, 인증 체크 |
| 인스턴스 선택 | 건강한 Worker로 라우팅 |

### ⚠️ Frontend에서 실패하면?

건강한 백엔드가 없으면, **앱 코드가 실행되기도 전에** 요청이 실패합니다.

| 에러 코드 | 의미 |
|----------|------|
| `403` | 접근 제한에 의해 차단 |
| `502` | 백엔드 연결 실패 |
| `503` | 서비스 이용 불가 |

```bash
# 접근 제한 설정 확인
az webapp config access-restriction show \
    --resource-group $RG \
    --name $APP_NAME \
    --output json
```

**출력 예시:**
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

![IMAGE: Access Restrictions 설정 화면]
`📸 캡처: Azure Portal → App Service → Networking → Access restrictions`

---

## Stage 3: Worker Reverse Proxy

Worker 인스턴스 내부에서, 로컬 리버스 프록시가 요청을 앱 프로세스로 전달합니다.

### 포트 계약 (Port Contract)

**핵심:** 앱은 반드시 **플랫폼이 제공하는 포트**에 바인딩해야 합니다.

```python
# ❌ 잘못된 예 - 하드코딩된 포트
app.run(host="0.0.0.0", port=5000)

# ✅ 올바른 예 - 환경변수에서 포트 읽기
import os
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

**흔한 실수:**
- 로컬에서는 잘 되는데 배포하면 안 됨
- 시작은 성공하지만 요청이 실패함

![IMAGE: General Settings에서 Startup Command]
`📸 캡처: Azure Portal → App Service → Configuration → General settings`

---

## Stage 4: 애플리케이션 실행

드디어 요청이 앱 코드에 도달했습니다!

### 성능에 영향을 주는 요소

| 요소 | 설명 |
|------|------|
| CPU/Memory 사용량 | 인스턴스 리소스 포화 |
| 외부 의존성 | DB, API 호출 지연 |
| 스레드/이벤트 루프 | 동시성 처리 한계 |
| 커넥션 풀 | 아웃바운드 연결 관리 |

### 응답 반환 경로

응답은 역순으로 돌아갑니다:

```
App → Worker → Frontend → Load Balancer → Client
```

플랫폼이 추가하는 헤더들:
- 압축 관련 헤더
- 보안 헤더
- 리버스 프록시 메타데이터

---

## 타임아웃과 연결 동작

### 플랫폼 타임아웃

App Service에는 여러 레벨의 타임아웃이 있습니다:

| 타임아웃 | 영향 |
|---------|------|
| Frontend 요청 타임아웃 | 장시간 요청 → 504 Gateway Timeout |
| Idle 연결 타임아웃 | 유휴 소켓이 닫힘 |
| 느린 의존성 | 큐 누적, 테일 레이턴시 증가 |

### 설계 가이드라인

```python
# ❌ 나쁜 패턴 - HTTP 요청 내에서 오래 걸리는 작업
@app.route('/export')
def export():
    # 10분 걸리는 데이터 처리...
    return huge_result  # 타임아웃 위험!

# ✅ 좋은 패턴 - 비동기 처리
@app.route('/export')
def export():
    job_id = queue_export_job()
    return {"status": "accepted", "jobId": job_id}, 202
```

**원칙:**
- 대화형 요청은 짧게 (< 30초)
- 긴 작업은 백그라운드로
- `202 Accepted` 반환 후 폴링/웹훅

---

## 인스턴스 선택과 Session Affinity

### 기본 동작: 라운드 로빈

Frontend는 기본적으로 트래픽을 건강한 인스턴스에 **분산**합니다.

### Session Affinity (ARR Affinity)

특정 클라이언트를 같은 인스턴스에 고정할 수 있습니다:

```
Client A ─(Affinity Cookie)─→ Instance 2
Client B ─(Affinity Cookie)─→ Instance 1
```

**트레이드오프:**

| 장점 | 단점 |
|------|------|
| 레거시 세션 코드 지원 | 불균등한 로드 분산 |
| 인메모리 캐시 활용 | 인스턴스 장애 시 취약 |

**권장:** 세션/상태를 **외부 저장소에 분리** (Redis, DB)

```bash
# ARR Affinity 비활성화
az webapp update \
    --resource-group $RG \
    --name $APP_NAME \
    --client-affinity-enabled false
```

![IMAGE: Configuration에서 ARR Affinity 설정]
`📸 캡처: Azure Portal → App Service → Configuration → General settings → ARR affinity`

---

## Health Check와 트래픽 자격

Health Check는 인스턴스가 트래픽을 받을 **자격**을 결정합니다.

### 상태별 동작

| 상태 | 트래픽 |
|------|--------|
| Healthy | 라우팅 풀에 포함 ✅ |
| Unhealthy | 풀에서 제외 ❌ |
| Recovering | 프로브 통과 후 재포함 |

### Health Probe 설계 원칙

```python
@app.route('/health')
def health():
    # 1. 가볍게 유지
    # 2. 트래픽 처리에 필수적인 의존성만 체크
    # 3. 느린 외부 호출 피하기
    
    try:
        # 필수 의존성만 간단히 체크
        db.execute("SELECT 1")
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}, 503
```

![IMAGE: Health check 설정 화면]
`📸 캡처: Azure Portal → App Service → Monitoring → Health check`

---

## Deployment Slots의 영향

Deployment Slots를 사용하면 배포 시 사용자 영향을 최소화할 수 있습니다.

### Slot Swap 과정

1. 새 버전을 Staging Slot에 배포
2. Staging이 warm-up 완료
3. Production은 계속 트래픽 처리
4. Slot Swap으로 트래픽 전환

**장점:**
- Cold start 노출 감소
- 실패한 배포 롤백 용이

![IMAGE: Deployment slots 화면]
`📸 캡처: Azure Portal → App Service → Deployment slots`

---

## 관측성: Lifecycle 전체 추적

각 단계를 연결해서 문제를 진단하세요:

### 상관관계 시그널

| 시그널 | 용도 |
|--------|------|
| Request 로그 | 상태 코드 분포 |
| Frontend 진단 | 플랫폼 레벨 에러 |
| 인스턴스 재시작 | 안정성 문제 |
| 의존성 타이밍 | 외부 호출 병목 |
| Correlation ID | 요청별 추적 |

### 로그 설정

```bash
# HTTP 로그 활성화
az webapp log config \
    --resource-group $RG \
    --name $APP_NAME \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem

# 실시간 로그 스트림
az webapp log tail \
    --resource-group $RG \
    --name $APP_NAME
```

![IMAGE: Log stream 화면]
`📸 캡처: Azure Portal → App Service → Monitoring → Log stream`

---

## 일반적인 실패 패턴

| 증상 | 의심 레이어 | 첫 번째 체크 |
|------|------------|-------------|
| 403 (앱 로그 없음) | Frontend | 접근 제한, 인증 설정 |
| 502/503 급증 | Worker/앱 시작 | 재시작 이벤트, Health probe |
| 504 응답 | 긴 요청 경로 | 의존성 지연, 요청 설계 |
| 간헐적 타임아웃 | 아웃바운드 | SNAT, 커넥션 풀 |

### 트러블슈팅 워크플로

1. **Frontend 확인**: DNS/TLS/접근 제한
2. **Worker 확인**: Health 상태, 재시작 이벤트
3. **앱 프로세스 확인**: 준비 상태, 포트 바인딩
4. **의존성 확인**: 외부 호출 지연, 연결 문제

---

## 정리

Request Lifecycle의 각 단계를 이해하면:

- **어디서 문제가 발생했는지** 빠르게 파악
- **적절한 로그/메트릭**을 확인
- **올바른 해결책**을 적용

다음 글에서는 **Hosting Models** - App Service Plan 선택과 배포 모델에 대해 알아보겠습니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. **[현재 글] Request Lifecycle: 요청이 앱에 도달하기까지**
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Deployment Slots in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [Inbound and outbound IPs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-inbound-outbound-ips)
- [Troubleshoot diagnostic logs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)

---

**태그:** `Azure` `App Service` `Cloud` `Networking` `DevOps`
