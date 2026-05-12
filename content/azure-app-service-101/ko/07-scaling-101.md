---
title: 'Scaling 101: 언제 Scale Up vs Scale Out?'
series: azure-app-service-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Cloud
- Web Apps
last_reviewed: '2026-05-12'
seo_description: App Service에서 Scale Up과 Scale Out을 언제 선택하고 Autoscale과 비용 상한을 어떻게 함께 설계할지 정리합니다.
---

# Scaling 101: 언제 Scale Up vs Scale Out?

트래픽이 늘고 앱이 느려지기 시작하면, 다음 질문은 거의 항상 같습니다. 인스턴스를 더 크게 키워야 할까, 아니면 개수를 늘려야 할까. 비용을 줄이면서 성능을 지키려면 이 차이를 먼저 분명히 알아야 합니다.

이 글은 Azure App Service 101 시리즈의 마지막 글입니다.

앞에서 본 플랫폼 구조, 배포, 설정, 모니터링을 실제 scale 결정으로 연결해 보겠습니다. App Service 운영은 결국 “언제 어떤 방식으로 용량을 바꿀지”까지 설명할 수 있을 때 비로소 완성됩니다.

---

> 비용 상한이 없는 scale rule은, 한 번의 잘못된 배포가 순식간에 큰 청구서로 이어지는 가장 빠른 경로입니다.

## 이 글에서 다룰 문제

- 수직 확장(scale up)과 수평 확장(scale out)은 신호와 비용이 어떻게 다를까요?
- 어떤 메트릭(CPU, queue, custom)을 auto-scale rule에 써야 할까요?
- 인스턴스가 scale in 될 때 ARR Affinity 세션은 어떻게 될까요?
- Premium의 always-ready는 cold start를 얼마나 줄여 줄까요?
- scale ceiling과 cost ceiling을 동시에 어떻게 지킬 수 있을까요?

## Two Directions of Scaling

```text
 ┌─────────────┐
 │ Larger │ ← Scale Up (Vertical)
 │ Instance │
 └─────────────┘
 ↑
┌───┐ ┌───┐ ┌───┐ ┌───┐
│ S │ │ S │ │ S │ ... │ S │ ← Scale Out (Horizontal)
└───┘ └───┘ └───┘ └───┘
 ↑
More instances
```

| Direction | Name | Description |
|-----------|------|-------------|
| **Vertical** | Scale Up/Down | Change instance size |
| **Horizontal** | Scale Out/In | Change instance count |

![Scaling up versus adding instances](../../../assets/azure-app-service-101/07/01-scale-up-vs-scale-out.en.png)

*인스턴스를 키우는 방식과 개수를 늘리는 방식의 차이*

---

## Scale Up (Vertical Scaling)

### When to Use?

- 인스턴스당 **더 많은 메모리**가 필요할 때
- **CPU가 포화**되어 있고 Scale Out으로 해결되지 않을 때
- 상위 티어 기능(VNet, Slots 등)이 필요할 때

### Trade-offs

| Pros | Cons |
|------|------|
| Simple configuration | Triggers restart |
| Feature upgrade | Cost can spike |
| - | Upper limit exists |

### Scale Up with CLI

```bash
# Upgrade S1 → P1v3
az appservice plan update \
 --resource-group $RG \
 --name $PLAN_NAME \
 --sku P1v3
```

### Check Current SKU

```bash
az appservice plan show \
 --resource-group $RG \
 --name $PLAN_NAME \
 --query "sku" \
 --output json
```

**Output:**
```json
{
 "name": "P1v3",
 "tier": "PremiumV3",
 "capacity": 2
}
```

---

## Scale Out (Horizontal Scaling)

### When to Use?

- **트래픽 증가**로 더 많은 처리량이 필요할 때
- **고가용성**을 위해 여러 인스턴스가 필요할 때
- 앱이 **stateless**하게 설계되어 있을 때

![Scaling choices by bottleneck type](../../../assets/azure-app-service-101/07/04-scaling-decision-tree.en.png)

*병목 유형에 따라 달라지는 scaling 선택*

### Prerequisite: Stateless Design

Scale Out이 제대로 동작하려면 앱 상태를 **외부 저장소**에 둬야 합니다.

| Stateless Pattern | Stateful Anti-pattern |
|---------------------|-------------------------|
| Store sessions in Redis | Store sessions in memory |
| Store state in DB | Store state in local files |
| Use distributed cache | Per-instance cache |

```python
# Stateful example that breaks scale-out
user_sessions = {} # Stored in memory

@app.route('/login')
def login():
 user_sessions[user_id] = session_data

# Stateless version backed by Redis
import json
import os
import redis
from flask import request

r = redis.Redis(host=os.environ["REDIS_HOST"])

@app.route('/login')
def login():
  user_id = request.json.get("user_id")
  session_data = {
   "logged_in": True,
   "roles": request.json.get("roles", []),
  }
  r.set(f"session:{user_id}", json.dumps(session_data))
```

### Scale Out with CLI

```bash
# Manually scale to 3 instances
az appservice plan update \
 --resource-group $RG \
 --name $PLAN_NAME \
 --number-of-workers 3
```

---

## Autoscale: Automatic Scaling

메트릭을 기준으로 인스턴스를 **자동으로** 늘리거나 줄일 수 있습니다.

![Autoscale loop from metrics to actions](../../../assets/azure-app-service-101/07/02-autoscale-feedback-loop.en.png)

*메트릭에서 액션으로 이어지는 Autoscale 피드백 루프*

### Autoscale Flow

```text
Collect Metrics → Evaluate Rules → Scale Action → Cooldown → Re-evaluate
```

### Basic Autoscale Configuration

```bash
# Create Autoscale profile
az monitor autoscale create \
 --resource-group $RG \
 --resource $PLAN_NAME \
 --resource-type "Microsoft.Web/serverfarms" \
 --name "autoscale-rule" \
 --min-count 2 \
 --max-count 10 \
 --count 2
```

### Add Scale Out Rule

```bash
# Add 1 instance when CPU > 70%
az monitor autoscale rule create \
 --resource-group $RG \
 --autoscale-name "autoscale-rule" \
 --condition "Percentage CPU > 70 avg 10m" \
 --scale out 1
```

### Add Scale In Rule

```bash
# Remove 1 instance when CPU < 35%
az monitor autoscale rule create \
 --resource-group $RG \
 --autoscale-name "autoscale-rule" \
 --condition "Percentage CPU < 35 avg 20m" \
 --scale in 1
```

### Verify Autoscale Configuration

```bash
az monitor autoscale show \
 --resource-group $RG \
 --name "autoscale-rule" \
 --output json
```

**Example output:**
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

---

## Autoscale Design Best Practices

### 1. Separate Scale Out/In Thresholds

```text
Scale Out: CPU > 70%
Scale In: CPU < 35% ← Gap prevents oscillation
```

**Oscillation**: threshold가 너무 가까우면 scale up/down이 계속 반복됩니다.

### 2. Set Cooldown Period

```bash
# Wait 5 minutes after Scale Out
--cooldown 5
```

### 3. Set Minimum/Maximum Instances

```text
Minimum: 2 ← Ensures availability (Health Check needs this)
Maximum: 10 ← Cost control
```

### 4. Combine Multiple Metrics

```bash
# CPU + Memory combination
az monitor autoscale rule create \
 --condition "Memory Percentage > 80 avg 5m" \
 --scale out 2
```

---

## Consider Dependencies

### Side Effects of Scale Out

인스턴스 수가 늘어나면 **외부 의존성에 가해지는 부하도 함께 증가**합니다.

![Instance growth cascading into dependency load](../../../assets/azure-app-service-101/07/03-dependency-cascade.en.png)

*인스턴스 증가가 의존성 부하로 전이되는 구조*

```text
2 instances → 20 DB connections
10 instances → 100 DB connections (!)
```

### Checklist

| Dependency | Check |
|------------|-------|
| Database | Connection pool limit, max connections |
| External API | Rate limit |
| Cache (Redis) | Throughput limit |
| Outbound | SNAT port exhaustion |

### Connection Pool Configuration Example

```python
from sqlalchemy import create_engine

engine = create_engine(
 DATABASE_URL,
 pool_size=5, # Connections per instance
 max_overflow=10, # Additional allowed
 pool_timeout=30,
 pool_recycle=1800
)
```

---

## Monitoring and Alerts

### Key Metrics

| Metric | Purpose | Example Alert Threshold |
|--------|---------|------------------------|
| CPU Percentage | Compute load | > 80% for 5min |
| Memory Percentage | Memory pressure | > 85% for 5min |
| HTTP Queue Length | Request backlog | > 100 |
| Response Time | User experience | p95 > 2s |
| Instance Count | Cost | > 8 |

### Configure Alerts

```bash
az monitor metrics alert create \
 --resource-group $RG \
 --name "High CPU Alert" \
 --scopes "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/serverfarms/$PLAN_NAME" \
 --condition "avg Percentage CPU > 80" \
 --window-size 5m
```

---

## Cost Optimization

### Schedule-based Scaling

업무 시간에만 인스턴스를 더 높게 유지합니다.

```bash
# Business hours: minimum 4
# Off-hours: minimum 2
```

Azure Portal → Scale out → Add a scale condition → Schedule

### Aggressive Scale In

```bash
# Generous Scale In rule
--condition "Percentage CPU < 30 avg 30m"
```

### Choose the Right Tier

| Situation | Recommended Approach |
|-----------|---------------------|
| Memory shortage | Consider Scale Up |
| Traffic increase | Scale Out first |
| Both | Scale Up then Scale Out |

---

## Scaling Playbook

### Traffic Spike Response

1. Immediate: Manually increase instances
2. Check Autoscale trigger delay
3. Check dependency bottlenecks
4. Revert after event ends

```bash
# Emergency Scale Out
az appservice plan update \
 --resource-group $RG \
 --name $PLAN_NAME \
 --number-of-workers 8
```

### Memory Pressure Response

1. Identify memory increase pattern (gradual vs sudden)
2. Gradual: Suspect memory leak → Review app code
3. Sudden: Traffic-based → Scale Up or Scale Out

### Cost Reduction

1. Set Scale In schedule for nights/weekends
2. Review Maximum instance limit
3. Monthly instance usage review

---

## Where this fits in the series

이 마지막 글은 시리즈 전체를 다시 묶어 줍니다. 배포, 설정, telemetry에서 정리한 내용이 결국 어떤 scaling 결정을 가능하게 하는지 보여 주기 때문입니다. 시리즈를 처음부터 다시 보면 공통된 줄기가 분명해집니다. App Service는 코드를 올리는 장소가 아니라, 운영 판단을 내릴 수 있는 플랫폼으로 다룰 때 가장 잘 맞습니다.

---

## 운영 체크리스트

- [ ] workload별로 vertical vs horizontal scaling 기준을 정했다
- [ ] auto-scale 메트릭과 threshold를 실제 측정값에 맞춰 보정했다
- [ ] scale-in이 sticky session에 주는 영향을 검증했다
- [ ] always-ready 인스턴스 수와 비용의 trade-off를 정했다
- [ ] max instance 수와 알림으로 runaway cost를 막았다

---

## 정리

Scaling 전략에서 기억할 기본 원칙은 아래와 같습니다.

| Situation | Strategy |
|-----------|----------|
| Memory shortage | Scale Up |
| Traffic increase | Scale Out |
| Availability | Minimum 2 instances |
| Cost control | Maximum setting + Schedule |
| Automation | Autoscale + Alerts |

**Remember:**
- Scale Out에는 **Stateless design**이 필요합니다.
- 의존성 한도도 함께 검토해야 합니다.
- Autoscale **oscillation**을 막아야 합니다.

App Service의 scaling은 버튼 하나를 누르는 기능이 아니라, 상태 저장 방식, 의존성 용량, 비용 상한까지 함께 설계하는 운영 작업입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service란? - 플랫폼 아키텍처 이해하기](./01-what-is-app-service.md)
- [Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까](./02-request-lifecycle.md)
- [Hosting Models: 어떤 플랜을 선택해야 할까?](./03-hosting-models.md)
- [첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)](./04-first-deploy.md)
- [Configuration 마스터하기: App Settings & 환경변수](./05-configuration.md)
- [로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기](./06-logging-monitoring.md)
- **Scaling 101: 언제 Scale Up vs Scale Out? (현재 글)**

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Scale up an app in Azure App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/manage-scale-up)
- [Get started with autoscale (Microsoft Learn)](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Best practices for Azure App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/app-service-best-practices)

### 관련 시리즈
- [Azure Functions 101](../../azure-functions-101/ko/)

---

Tags: Azure, App Service, Cloud, Web Apps
