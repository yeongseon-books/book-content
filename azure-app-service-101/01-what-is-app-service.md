# Azure App Service란? - 플랫폼 아키텍처 이해하기

> Azure App Service 101 시리즈 (1/7)

웹 애플리케이션을 Azure에 배포하려고 할 때, 가장 먼저 마주치는 서비스가 바로 **Azure App Service**입니다. VM을 직접 관리할 필요 없이 코드만 배포하면 되는 PaaS(Platform as a Service)인데요, 이 서비스를 제대로 활용하려면 내부 구조를 이해하는 것이 중요합니다.

이 글에서는 App Service의 **3-Plane 아키텍처**를 중심으로, 플랫폼이 어떻게 동작하는지 알아보겠습니다.

---

## App Service가 뭔가요?

Azure App Service는 웹 앱, REST API, 모바일 백엔드를 호스팅하기 위한 **완전 관리형 플랫폼**입니다.

여러분은 애플리케이션 코드에만 집중하면 되고, Microsoft가 다음을 담당합니다:

- 서버 인프라 관리 및 패칭
- 로드 밸런싱과 트래픽 라우팅
- 자동 스케일링
- 배포 파이프라인 통합

![IMAGE: Azure Portal에서 App Service 개요 화면]
`📸 캡처: Azure Portal → App Service → Overview 페이지`

---

## 3-Plane 아키텍처: 핵심 멘탈 모델

App Service를 이해하는 가장 중요한 개념은 **세 개의 Plane**입니다.

| Plane | 역할 | 주요 도구 |
|-------|------|----------|
| **Management Plane** | 설정과 구성 관리 | Azure Portal, CLI, ARM/Bicep |
| **Runtime Plane** | 실제 요청 처리 | Frontend + Worker 인스턴스 |
| **SCM Plane** | 배포와 진단 | Kudu (`.scm.azurewebsites.net`) |

### 왜 이게 중요한가?

각 Plane은 **독립적인 API와 장애 모드**를 가집니다. 예를 들어:

- Management Plane에서 App Setting을 바꾸면 → Runtime Plane이 재시작될 수 있음
- SCM(Kudu) 사이트에 접속이 안 되어도 → 앱 자체는 정상 동작할 수 있음

![IMAGE: 3-Plane 아키텍처 다이어그램]
`📸 캡처: 3-Plane 구조도 (직접 그리거나 draw.io 사용)`

---

## Management Plane: 설정의 중심

Management Plane은 여러분이 **원하는 상태(Desired State)**를 선언하는 곳입니다.

### 주요 설정 항목

- **App Service Plan**: SKU, 인스턴스 수
- **App Settings**: 환경 변수
- **Deployment Slots**: 스테이징 환경
- **Custom Domains**: 도메인 연결
- **Managed Identity**: 보안 인증

### ⚠️ 주의: 설정 변경 = 재시작 가능

많은 설정들이 프로세스 시작 시점에 적용되기 때문에, 변경하면 앱이 재시작됩니다.

**재시작을 유발하는 설정들:**
- App Settings 변경
- Startup Command 변경
- Runtime Stack 변경
- Slot Swap

```bash
# 현재 앱 상태 확인
az webapp show \
    --resource-group $RG \
    --name $APP_NAME \
    --query "{state:state, hostNames:hostNames, httpsOnly:httpsOnly}" \
    --output json
```

![IMAGE: Azure Portal의 Configuration 화면]
`📸 캡처: Azure Portal → App Service → Configuration → Application settings`

---

## Runtime Plane: 요청이 처리되는 곳

Runtime Plane은 실제 사용자 요청이 처리되는 영역입니다.

### 요청 흐름

```
Client → App Service Frontend → Worker Instance → App Process
```

1. **Frontend**: TLS 종료, 호스트 검증, 라우팅
2. **Worker**: 건강한 인스턴스 선택, 요청 전달
3. **App**: 비즈니스 로직 실행, 응답 반환

### 인스턴스 생명주기

Worker 인스턴스는 다음 상황에서 재활용됩니다:

- 플랫폼 유지보수
- Scale Out/In
- 설정 변경으로 인한 재시작

**설계 원칙:**
- ✅ 상태는 외부 저장소에 (Redis, DB)
- ✅ 시작 로직은 멱등성 있게
- ✅ 종료 시 graceful shutdown
- ❌ 로컬 파일에 중요 데이터 저장 금지

![IMAGE: App Service 메트릭 화면]
`📸 캡처: Azure Portal → App Service → Monitoring → Metrics (CPU, Memory)`

---

## SCM Plane (Kudu): 배포와 디버깅

SCM 사이트는 `<app-name>.scm.azurewebsites.net`으로 접근하는 관리 도구입니다.

### Kudu가 제공하는 기능

| 기능 | 엔드포인트 |
|------|-----------|
| ZIP 배포 | `/api/zipdeploy` |
| 배포 이력 | `/api/deployments` |
| 환경 정보 | `/api/environment` |
| 로그 스트림 | `/api/logstream` |
| 파일 브라우저 | `/api/vfs/` |

### 🚨 중요: SCM ≠ 앱 컨테이너

Linux 커스텀 컨테이너를 사용할 때, SCM 사이트는 **별도의 컨테이너**에서 실행됩니다.

- SCM에서 앱 컨테이너의 파일시스템/프로세스를 직접 볼 수 없음
- 디버깅은 앱 컨테이너 SSH나 로그를 사용해야 함

```bash
# SCM 접근 제한 확인
az webapp config access-restriction show \
    --resource-group $RG \
    --name $APP_NAME \
    --output json
```

![IMAGE: Kudu 대시보드 화면]
`📸 캡처: https://<app-name>.scm.azurewebsites.net 메인 화면`

---

## 호스팅 모드별 차이점

App Service는 여러 호스팅 모드를 지원하며, 각각 동작이 다릅니다.

| 측면 | Windows Code | Linux Built-in | Linux Custom Container |
|------|-------------|----------------|----------------------|
| **시작 방식** | IIS/플랫폼이 시작 | 빌트인 이미지 + 명령 | 이미지 Pull 후 시작 |
| **포트** | 플랫폼 관리 | `PORT` 환경변수 | `WEBSITES_PORT` 설정 |
| **저장소** | 영구 저장 | `/home` 영구 | 설정에 따라 다름 |
| **진단** | Kudu 풍부 | Kudu 풍부 | SSH가 주요 수단 |

### 포트 바인딩 규칙

```python
# Python (Flask) 예시 - 올바른 포트 바인딩
import os
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

![IMAGE: App Service Configuration에서 Startup Command 설정]
`📸 캡처: Azure Portal → App Service → Configuration → General settings → Startup Command`

---

## 파일시스템: 임시 vs 영구

스토리지 동작을 이해하는 것은 프로덕션 문제를 예방하는 핵심입니다.

### 임시 저장소 (Ephemeral)

- 빠른 로컬 I/O
- 인스턴스 재시작 시 **삭제됨**
- 인스턴스 간 **공유 안 됨**

**적합한 용도:** 임시 캐시, 업로드 스테이징, 중간 처리 파일

### 영구 저장소 (`/home`)

- 네트워크 기반, 느림
- 재시작 후에도 **유지됨**
- 모든 인스턴스가 **공유**

| 경로 | 용도 |
|------|------|
| `/home/site/wwwroot` | 배포된 앱 코드 |
| `/home/LogFiles` | 앱/플랫폼 로그 |
| `/home/data` | 앱 데이터 |

### ❌ 안티패턴: SQLite를 `/home`에?

`/home`은 네트워크 파일시스템이므로:
- Lock 경합 발생 가능
- 레이턴시 변동
- 멀티 인스턴스에서 데이터 손상 위험

**→ 프로덕션에서는 Azure SQL, PostgreSQL 등 관리형 DB 사용**

---

## Health Check: 앱 상태 확인

Health Check는 단순한 모니터링이 아니라, **트래픽 라우팅의 핵심**입니다.

### 동작 방식

1. 플랫폼이 Health 엔드포인트에 주기적으로 요청
2. `200 OK` → 인스턴스 정상, 트래픽 수신
3. 실패/타임아웃 → 인스턴스 제외, 복구 시도

### Health 엔드포인트 설계 원칙

```python
@app.route('/health')
def health():
    # ✅ 가벼운 체크
    # ✅ 핵심 의존성만 확인
    # ❌ 무거운 DB 쿼리 금지
    return {"status": "healthy"}, 200
```

**주의사항:**
- `302 Redirect`는 성공으로 안 침
- 1분 타임아웃 = unhealthy 처리
- 2개 이상 인스턴스에서 효과적

![IMAGE: Azure Portal Health Check 설정 화면]
`📸 캡처: Azure Portal → App Service → Monitoring → Health check`

---

## 운영 체크리스트

프로덕션 배포 전, 최소한 이것들은 확인하세요:

### ✅ 신뢰성

- [ ] Health 엔드포인트 구현 및 테스트
- [ ] Health Check 설정 활성화
- [ ] 2개 이상 인스턴스 (가용성 확보)
- [ ] 시작 시간 측정 및 최적화

### ✅ 배포 안전성

- [ ] CI/CD로 불변 아티팩트 생성
- [ ] 롤백 방법 문서화 및 테스트
- [ ] 배포 자격증명 최소화

### ✅ 관측성

- [ ] 구조화된 로깅 활성화
- [ ] 로그 보존/내보내기 설정
- [ ] 에러율, 재시작, 레이턴시 알람

### ✅ 설정

- [ ] 포트 바인딩 검증 (호스팅 모드별)
- [ ] 스토리지 동작 확인
- [ ] 비밀값은 Key Vault에

---

## 정리

Azure App Service의 3-Plane 모델을 이해하면:

- **Management Plane**: 설정 변경이 왜 재시작을 유발하는지 이해
- **Runtime Plane**: 요청 흐름과 인스턴스 동작 파악
- **SCM Plane**: 배포와 디버깅 도구 활용

다음 글에서는 **Request Lifecycle** - 요청이 실제로 앱에 도달하기까지의 전체 여정을 살펴보겠습니다.

---

## 시리즈 목차

1. **[현재 글] Azure App Service란? - 플랫폼 아키텍처 이해하기**
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Azure App Service overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview)
- [Kudu service overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/resources-kudu)
- [Monitor App Service instances by using Health Check (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/monitor-instances-health-check)

---

**태그:** `Azure` `App Service` `Cloud` `Architecture` `DevOps`
