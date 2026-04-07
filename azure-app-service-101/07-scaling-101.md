# Scaling 101: 언제 Scale Up vs Scale Out?

> Azure App Service 101 시리즈 (7/7) - 마지막

"트래픽이 늘었는데 앱이 느려요." "비용은 줄이고 싶은데 성능은 유지해야 해요."

**Scaling**은 이런 문제를 해결하는 핵심 전략입니다. 이 글에서는 Scale Up과 Scale Out의 차이, 언제 어떤 것을 선택할지, 그리고 Autoscale 설정 방법을 알아봅니다.

---

## Scaling의 두 가지 방향

```
                    ┌─────────────┐
                    │ 더 큰 인스턴스│ ← Scale Up (수직)
                    └─────────────┘
                           ↑
┌───┐ ┌───┐ ┌───┐     ┌───┐
│ S │ │ S │ │ S │ ... │ S │ ← Scale Out (수평)
└───┘ └───┘ └───┘     └───┘
  ↑
더 많은 인스턴스
```

| 방향 | 이름 | 설명 |
|------|------|------|
| **수직** | Scale Up/Down | 인스턴스 크기 변경 |
| **수평** | Scale Out/In | 인스턴스 개수 변경 |

![IMAGE: Scaling 개념 다이어그램]
`📸 캡처: Scale Up vs Scale Out 비교 다이어그램 (draw.io)`

---

## Scale Up (수직 확장)

### 언제 사용하나?

- 인스턴스당 **더 많은 메모리**가 필요할 때
- **CPU가 포화**되어 Scale Out으로 해결 안 될 때
- 높은 티어의 **기능이 필요**할 때 (VNet, Slots 등)

### 트레이드오프

| 장점 | 단점 |
|------|------|
| 설정 간단 | 재시작 발생 |
| 기능 업그레이드 | 비용 급증 가능 |
| - | 상한선 존재 |

### CLI로 Scale Up

```bash
# S1 → P1v3로 업그레이드
az appservice plan update \
    --resource-group $RG \
    --name $PLAN_NAME \
    --sku P1v3
```

### 현재 SKU 확인

```bash
az appservice plan show \
    --resource-group $RG \
    --name $PLAN_NAME \
    --query "sku" \
    --output json
```

**출력:**
```json
{
  "name": "P1v3",
  "tier": "PremiumV3",
  "capacity": 2
}
```

![IMAGE: Scale up 화면]
`📸 캡처: Azure Portal → App Service Plan → Scale up (App Service plan)`

---

## Scale Out (수평 확장)

### 언제 사용하나?

- **트래픽 증가**로 더 많은 처리량 필요
- **고가용성**을 위해 여러 인스턴스 필요
- 앱이 **stateless**하게 설계됨

### 전제 조건: Stateless 설계

Scale Out이 동작하려면 앱이 **상태를 외부에 저장**해야 합니다.

| Stateless 패턴 ✅ | Stateful 안티패턴 ❌ |
|-----------------|-------------------|
| 세션을 Redis에 저장 | 메모리에 세션 저장 |
| DB에 상태 저장 | 로컬 파일에 상태 저장 |
| 분산 캐시 사용 | 인스턴스별 캐시 |

```python
# ❌ Stateful - Scale Out 시 문제
user_sessions = {}  # 메모리에 저장

@app.route('/login')
def login():
    user_sessions[user_id] = session_data

# ✅ Stateless - Redis 사용
import redis
r = redis.Redis(host=os.environ["REDIS_HOST"])

@app.route('/login')
def login():
    r.set(f"session:{user_id}", json.dumps(session_data))
```

### CLI로 Scale Out

```bash
# 3개 인스턴스로 수동 확장
az appservice plan update \
    --resource-group $RG \
    --name $PLAN_NAME \
    --number-of-workers 3
```

![IMAGE: Scale out 화면]
`📸 캡처: Azure Portal → App Service Plan → Scale out (App Service plan) → Manual scale`

---

## Autoscale: 자동 확장

트래픽에 따라 **자동으로** 인스턴스를 늘리거나 줄입니다.

### Autoscale 흐름

```
메트릭 수집 → 규칙 평가 → 스케일 액션 → 쿨다운 → 재평가
```

### 기본 Autoscale 설정

```bash
# Autoscale 프로필 생성
az monitor autoscale create \
    --resource-group $RG \
    --resource $PLAN_NAME \
    --resource-type "Microsoft.Web/serverfarms" \
    --name "autoscale-rule" \
    --min-count 2 \
    --max-count 10 \
    --count 2
```

### Scale Out 규칙 추가

```bash
# CPU 70% 초과 시 1개 추가
az monitor autoscale rule create \
    --resource-group $RG \
    --autoscale-name "autoscale-rule" \
    --condition "Percentage CPU > 70 avg 10m" \
    --scale out 1
```

### Scale In 규칙 추가

```bash
# CPU 35% 미만 시 1개 감소
az monitor autoscale rule create \
    --resource-group $RG \
    --autoscale-name "autoscale-rule" \
    --condition "Percentage CPU < 35 avg 20m" \
    --scale in 1
```

### Autoscale 설정 확인

```bash
az monitor autoscale show \
    --resource-group $RG \
    --name "autoscale-rule" \
    --output json
```

**출력 예시:**
```json
{
  "enabled": true,
  "profiles": [{
    "capacity": {
      "default": "2",
      "maximum": "10",
      "minimum": "2"
    },
    "rules": [
      {"metricTrigger": {"metricName": "Percentage CPU", "operator": "GreaterThan", "threshold": 70}},
      {"metricTrigger": {"metricName": "Percentage CPU", "operator": "LessThan", "threshold": 35}}
    ]
  }]
}
```

![IMAGE: Autoscale 설정 화면]
`📸 캡처: Azure Portal → App Service Plan → Scale out → Custom autoscale`

---

## Autoscale 설계 Best Practices

### 1. Scale Out/In 임계값 분리

```
Scale Out: CPU > 70%
Scale In:  CPU < 35%  ← 간격을 두어 oscillation 방지
```

**Oscillation(요동)**: 임계값이 너무 가까우면 계속 확장/축소 반복

### 2. 쿨다운 기간 설정

```bash
# Scale Out 후 5분 대기
--cooldown 5
```

### 3. 최소/최대 인스턴스 설정

```
Minimum: 2  ← 가용성 확보 (Health Check가 의미 있으려면)
Maximum: 10 ← 비용 통제
```

### 4. 여러 메트릭 조합

```bash
# CPU + Memory 조합
az monitor autoscale rule create \
    --condition "Memory Percentage > 80 avg 5m" \
    --scale out 2
```

---

## 의존성 고려

### Scale Out의 부작용

인스턴스가 늘어나면 **외부 의존성 부하도 증가**합니다.

```
인스턴스 2개 → DB 연결 20개
인스턴스 10개 → DB 연결 100개 (!)
```

### 체크리스트

| 의존성 | 확인 사항 |
|--------|----------|
| Database | 연결 풀 한계, 최대 연결 수 |
| External API | Rate limit |
| Cache (Redis) | 처리량 한계 |
| Outbound | SNAT 포트 고갈 |

### Connection Pool 설정 예시

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # 인스턴스당 연결 수
    max_overflow=10,    # 추가 허용
    pool_timeout=30,
    pool_recycle=1800
)
```

---

## 모니터링과 알람

### 핵심 메트릭

| 메트릭 | 용도 | 알람 기준 예시 |
|--------|------|--------------|
| CPU Percentage | 컴퓨팅 부하 | > 80% for 5min |
| Memory Percentage | 메모리 압박 | > 85% for 5min |
| HTTP Queue Length | 요청 적체 | > 100 |
| Response Time | 사용자 경험 | p95 > 2s |
| Instance Count | 비용 | > 8 |

### 알람 설정

```bash
az monitor metrics alert create \
    --resource-group $RG \
    --name "High CPU Alert" \
    --scopes "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/serverfarms/$PLAN_NAME" \
    --condition "avg Percentage CPU > 80" \
    --window-size 5m
```

![IMAGE: Metrics 대시보드]
`📸 캡처: Azure Portal → App Service Plan → Metrics (CPU, Memory, Instances)`

---

## 비용 최적화

### Schedule-based Scaling

업무 시간에만 높은 인스턴스 유지:

```bash
# 업무 시간: 최소 4개
# 비업무 시간: 최소 2개
```

Azure Portal → Scale out → Add a scale condition → Schedule

### Scale In 적극 활용

```bash
# 여유로운 Scale In 규칙
--condition "Percentage CPU < 30 avg 30m"
```

### 적정 티어 선택

| 상황 | 권장 접근 |
|------|----------|
| 메모리 부족 | Scale Up 검토 |
| 트래픽 증가 | Scale Out 우선 |
| 둘 다 | Scale Up 후 Scale Out |

---

## Scaling Playbook

### 트래픽 스파이크 대응

1. 즉시: 수동으로 인스턴스 증가
2. Autoscale 트리거 지연 확인
3. 의존성 병목 확인
4. 이벤트 종료 후 원복

```bash
# 긴급 Scale Out
az appservice plan update \
    --resource-group $RG \
    --name $PLAN_NAME \
    --number-of-workers 8
```

### 메모리 압박 대응

1. 메모리 증가 패턴 파악 (점진적 vs 급격)
2. 점진적: 메모리 누수 의심 → 앱 코드 검토
3. 급격: 트래픽 기반 → Scale Up 또는 Scale Out

### 비용 절감

1. 야간/주말 Scale In 스케줄 설정
2. Maximum 인스턴스 상한 검토
3. 월별 인스턴스 사용량 리뷰

---

## 정리

Scaling 전략의 핵심:

| 상황 | 전략 |
|------|------|
| 메모리 부족 | Scale Up |
| 트래픽 증가 | Scale Out |
| 가용성 확보 | 최소 2개 인스턴스 |
| 비용 통제 | Maximum 설정 + Schedule |
| 자동화 | Autoscale + 알람 |

**기억하세요:**
- Scale Out은 **Stateless 설계** 필수
- 의존성 한계를 함께 검토
- Autoscale **oscillation** 방지 (임계값 간격)

---

## 시리즈를 마치며

**Azure App Service 101 시리즈**를 통해 다음을 배웠습니다:

1. ✅ 플랫폼 아키텍처 (3-Plane 모델)
2. ✅ 요청 흐름 (Request Lifecycle)
3. ✅ 호스팅 선택 (Plan, OS, 배포 모델)
4. ✅ 첫 배포 (Python/Flask)
5. ✅ 설정 관리 (App Settings, Key Vault)
6. ✅ 로그와 모니터링 (Application Insights)
7. ✅ 스케일링 전략 (Scale Up/Out, Autoscale)

이 기초 위에 **Deployment Slots**, **CI/CD**, **네트워킹**, **보안** 등 고급 주제를 쌓아갈 수 있습니다.

Happy deploying! 🚀

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. **[현재 글] Scaling 101: 언제 Scale Up vs Scale Out?**

---

## 참고 자료

- [Scale up an app in Azure App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/manage-scale-up)
- [Get started with autoscale (Microsoft Learn)](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Best practices for Azure App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/app-service-best-practices)

---

**태그:** `Azure` `App Service` `Scaling` `Autoscale` `Performance` `DevOps`
