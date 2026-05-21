---
episode: 4
language: ko
last_reviewed: '2026-05-14'
seo_description: 에러 버짓 계산법과 burn rate로 위험을 관리하는 법, 버짓 상태에 따른 릴리스 정책 수립 원칙을 정리합니다.
series: sre-101
status: content-ready
tags:
- SRE
- ErrorBudget
- Reliability
- Release
- Risk
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (4/10): Error Budget"
---

# SRE 101 (4/10): Error Budget

신뢰성 목표를 세우고 나면 곧바로 현실적인 질문이 따라옵니다. 그러면 어느 정도 실패까지는 허용할 것인가 하는 질문입니다. 목표가 있다는 말이 곧 실패를 0으로 만들겠다는 뜻은 아닙니다.

서비스는 늘 변화하고, 팀은 늘 새로운 기능을 내보내야 합니다. 그래서 운영에서는 실패를 완전히 제거하겠다는 태도보다, 어느 정도 위험까지 감수할지를 명확히 정하는 태도가 더 실용적입니다.

이 글은 SRE 101 시리즈의 4번째 글입니다. 여기서는 에러 버짓이 무엇인지, SLO에서 어떻게 계산하는지, burn rate를 왜 같이 봐야 하는지, 그리고 버짓이 실제 릴리스 정책을 어떻게 바꾸는지 설명합니다.


![SRE 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/04/04-01-concept-at-a-glance.ko.png)
*SRE 101 4장 흐름 개요*
> Error Budget은 허용 단계에서 계산되고, 누적 차감에서 상태를 보여 주며, 속도 범위에서 위험 신호를 납니다.

## 먼저 던지는 질문

- 에러 버짓은 왜 속도와 안정성 사이의 공통 언어가 될까요?
- SLO를 세운 뒤 허용 가능한 실패 범위는 어떻게 계산할까요?
- 누적 소진량과 burn rate는 왜 다른 질문에 답할까요?

## 왜 이 주제가 중요한가

에러 버짓이 없으면 장애가 날 때마다 조직 반응이 제각각입니다. 어떤 팀은 바로 배포 중단을 주장하고, 어떤 팀은 어쩔 수 없는 일이라고 넘깁니다. 이렇게 되면 같은 규모의 장애라도 매번 다른 결론이 나옵니다.

반대로 에러 버짓이 있으면 남은 허용 범위를 기준으로 판단할 수 있습니다. 아직 여유가 있으면 실험을 계속하고, 빠르게 소진되고 있으면 안정화 작업을 우선합니다. 이 구조가 생기면 속도와 안정성 논의가 감정 싸움에서 정책 논의로 바뀝니다.

## 한 문장으로 잡는 멘탈 모델

> 에러 버짓은 목표와 현실 사이에서 팀이 감수하기로 한 실패 여유분이며, 그 숫자가 릴리스 행동을 바꿔야 의미가 있습니다.

## 한눈에 보는 구조

이 그림은 에러 버짓이 단지 계산식이 아니라 의사결정 체계라는 점을 보여 줍니다. 목표에서 버짓이 나오고, 실제 오류가 그 버짓을 소모하며, 남은 정도에 따라 팀의 릴리스 속도와 우선순위가 바뀝니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 운영에서 하는 역할 |
| --- | --- | --- |
| error budget | 목표가 허용하는 실패량 | 위험 감수 범위를 수치로 보여 줍니다 |
| burn rate | 버짓이 소모되는 속도 | 조기 경고 신호가 됩니다 |
| freeze | 새 릴리스나 위험한 변경을 멈추는 정책 | 버짓이 바닥날 때 안정화를 우선하게 합니다 |
| window | 버짓을 평가하는 기간 | 소진량 해석 기준이 됩니다 |
| policy | 버짓 상태에 따라 취하는 행동 규칙 | 숫자를 실제 행동으로 바꿉니다 |

## 에러 버짓은 왜 문화까지 바꾸는가

에러 버짓의 강점은 실패를 허용하는 데 있지 않습니다. 어느 정도 실패까지는 감수한다고 미리 합의함으로써, 불필요한 논쟁을 줄이는 데 있습니다. 목표를 만족하는 범위 안에서는 더 빠르게 움직일 수 있고, 목표를 위협하는 순간에는 안정화에 집중할 이유가 생깁니다.

그래서 에러 버짓은 운영 지표이면서 팀 문화 장치이기도 합니다. 장애가 났을 때 누가 잘못했는지부터 보는 팀보다, 버짓이 얼마나 남았고 어떤 정책을 발동해야 하는지부터 보는 팀이 더 차분하게 움직입니다.

## 에러 버짓 사용 시나리오 표

에러 버짓 상태에 따라 팀이 취할 행동은 달라집니다. 버짓이 남아 있으면 공격적인 배포가 가능하고, 버짓이 바닥나면 안정화를 우선해야 합니다.

| 버짓 상태 | 소진 비율 | 행동 방향 | 예시 |
| --- | --- | --- | --- |
| **버짓 남음** | 50% 이하 | 공격적 배포, 실험 기능 출시 | 주 3회 배포, 새 API 실험 |
| **버짓 경계** | 50~80% | 추가 리뷰, 테스트 강화 | 카나리 배포, 로그 점검 강화 |
| **버짓 초과** | 80% 이상 | 배포 freeze, 안정화 작업 우선 | hotfix만 허용, 기술 부채 제거 |
| **버짓 소진** | 100% 또는 SLO 위반 | 모든 배포 중단, 책임자 회고 | 임시 운영 체제, 포스트모텀 작성 |

이 표를 보면 버짓은 단순 계산이 아니라 팀의 행동 규칙이라는 점이 명확해집니다. 포트폴리오 투자처럼 여유가 있을 때는 위험을 감수하고, 위기에 가까우면 보수적으로 타이트하게 관리합니다. 이 규칙을 다음 회고 미팅에서 팀원 전체가 합의하면 의사결정 비용이 크게 줄어듭니다.
## 누적 소진량만 보면 놓치는 것

월간 버짓이 아직 많이 남아 있어 보여도, 최근 1시간 동안 소진 속도가 비정상적으로 빠를 수 있습니다. 이럴 때 누적 비율만 보면 대응이 늦어집니다. 그래서 burn rate를 같이 봐야 합니다.

누적 소진량은 지금까지 얼마를 썼는지 보여 주고, burn rate는 지금 어떤 속도로 나빠지고 있는지 보여 줍니다. 하나는 상태판이고, 다른 하나는 경고등에 가깝습니다.

## 단계별로 버짓 운영하기

### 1단계 — 버짓 계산

```python
def budget(target, total):
    return (1 - target) * total
```

에러 버짓은 SLO에서 바로 나옵니다. 목표가 99.9%라면 0.1% 실패가 허용됩니다. 이 계산이 가능해지는 순간 신뢰성은 이상론이 아니라 운영 숫자가 됩니다.

### 2단계 — 소진 비율 계산

```python
def spent(errors, allowed):
    return errors / allowed
```

현재까지 허용량 가운데 얼마를 썼는지 보는 지표입니다. 장애 한 번의 강도보다, 누적 흐름이 어떤 방향으로 가고 있는지 읽는 데 도움이 됩니다.

### 3단계 — burn rate 계산

```python
def burn_rate(errors_in_h, allowed_per_h):
    return errors_in_h / allowed_per_h
```

burn rate는 짧은 시간 안에 버짓이 얼마나 빠르게 녹고 있는지 보여 줍니다. 누적 소진량이 아직 낮더라도, 현재 속도가 빠르면 큰 장애의 전조일 수 있습니다.

### 4단계 — 정책 분기

```python
def policy(spent_ratio):
    if spent_ratio > 1.0:
        return "freeze"
    if spent_ratio > 0.5:
        return "review"
    return "ship"
```

숫자만 있어서는 행동이 바뀌지 않습니다. 어느 수준에서 리뷰하고, 어느 수준에서 배포를 멈출지 미리 정해야 합니다. 그래야 장애 중에도 매번 처음부터 토론하지 않아도 됩니다.

### 5단계 — 조기 경고

```python
def alert(burn):
    return burn > 14.4  # 14.4x: fast burn
```

빠른 소진 경고는 초기에 상황을 잡는 데 도움이 됩니다. 조직마다 임계값은 달라질 수 있지만, 속도 기반 경고를 두어야 큰 문제를 더 일찍 읽을 수 있습니다.

## 에러 버짓 계산 예제 (Python)

SLO와 요청 수가 주어졌을 때 에러 버짓을 계산하고, 현재 상태와 남은 여유를 확인하는 예제입니다.

```python
def calculate_error_budget(total_requests, target_availability, current_errors):
    """
    에러 버짓 계산 및 현재 상태 분석
    """
    allowed_errors = total_requests * (1 - target_availability)
    remaining_errors = allowed_errors - current_errors
    spent_ratio = current_errors / allowed_errors if allowed_errors > 0 else 0
    
    return {
        "allowed_errors": allowed_errors,
        "current_errors": current_errors,
        "remaining_errors": remaining_errors,
        "spent_ratio": spent_ratio,
        "status": get_status(spent_ratio)
    }

def get_status(spent_ratio):
    if spent_ratio >= 1.0:
        return "EXHAUSTED"
    elif spent_ratio >= 0.8:
        return "CRITICAL"
    elif spent_ratio >= 0.5:
        return "WARNING"
    else:
        return "HEALTHY"

# 30일간 100만 요청, 99.9% 목표, 현재 800개 실패
result = calculate_error_budget(1_000_000, 0.999, 800)
print(f"허용 에러: {result['allowed_errors']}")
print(f"현재 에러: {result['current_errors']}")
print(f"남은 여유: {result['remaining_errors']}")
print(f"소진 비율: {result['spent_ratio']*100:.1f}%")
print(f"상태: {result['status']}")
```

출력 예시:
```
허용 에러: 1000.0
현재 에러: 800
남은 여유: 200.0
소진 비율: 80.0%
상태: CRITICAL
```

이 코드는 버짓 상태를 하나의 함수로 요약합니다. 허용량, 현재값, 남은 여유, 상태를 한 번에 볼 수 있어 운영 의사결정이 빠라집니다.


## Burn Rate 기반 알림 설계

에러 버짓을 실시간으로 감시하려면 burn rate 기반 알림이 효과적입니다. 단순히 오류 비율 임계값을 거는 것보다, 버짓이 소진되는 속도를 보고 알림을 보내면 더 정확한 조기 경고를 받을 수 있습니다.

### Burn Rate란?

burn rate는 현재 속도로 오류가 계속 발생하면 윈도우가 끝나기 전에 버짓이 바닥나는지를 보여 줍니다.

```
burn_rate = (현재 오류 발생 속도) / (허용된 오류 발생 속도)
```

- burn rate = 1: 정확히 예산대로 소진 중 (월말에 딱 맞게 바닥남)
- burn rate = 2: 2배 속도로 소진 중 (15일 만에 바닥남)
- burn rate = 14.4: 매우 빠르게 소진 중 (약 2일 만에 바닥남)

### PromQL로 Burn Rate 알림 설정

Google SRE Workbook에서 권장하는 multi-window, multi-burn-rate 알림 방식입니다.

```promql
# Fast burn: 1시간 윈도우에서 14.4배 속도 초과
(
  sum(rate(http_requests_total{status=~"5..",service="payments"}[1h]))
  /
  sum(rate(http_requests_total{service="payments"}[1h]))
) > (14.4 * 0.001)

# Slow burn: 6시간 윈도우에서 6배 속도 초과
(
  sum(rate(http_requests_total{status=~"5..",service="payments"}[6h]))
  /
  sum(rate(http_requests_total{service="payments"}[6h]))
) > (6 * 0.001)
```

### 알림 계층 설계

```yaml
# Prometheus alerting rules
groups:
  - name: error_budget_burn
    rules:
      - alert: ErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            / sum(rate(http_requests_total[1h]))
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "에러 버짓이 14.4배 속도로 소진 중 (약 2일 내 고갈)"
          runbook: "https://wiki.internal/runbooks/error-budget-fast-burn"

      - alert: ErrorBudgetSlowBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[6h]))
            / sum(rate(http_requests_total[6h]))
          ) > (6 * 0.001)
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "에러 버짓이 6배 속도로 소진 중 (약 5일 내 고갈)"
```

Fast burn은 즉시 대응이 필요한 급격한 장애에 대응하고, slow burn은 점진적으로 품질이 나빠지는 상황을 잡아냅니다. 두 알림을 함께 써야 큰 장애도, 느린 악화도 모두 감지할 수 있습니다.

## 에러 버짓 소진 시뮬레이션

에러 버짓이 실제로 어떻게 소진되는지 시뮬레이션해 보면 burn rate의 의미가 더 명확해집니다.

```python
def simulate_budget_burn(
    total_requests_per_day,
    target_availability,
    window_days,
    daily_error_rates
):
    """
    에러 버짓 소진 시뮬레이션
    daily_error_rates: 각 날의 오류 비율 리스트
    """
    total_requests = total_requests_per_day * window_days
    total_budget = total_requests * (1 - target_availability)
    
    cumulative_errors = 0
    daily_report = []
    
    for day, error_rate in enumerate(daily_error_rates, 1):
        daily_errors = total_requests_per_day * error_rate
        cumulative_errors += daily_errors
        spent_ratio = cumulative_errors / total_budget
        
        daily_report.append({
            "day": day,
            "daily_error_rate": f"{error_rate*100:.3f}%",
            "cumulative_errors": int(cumulative_errors),
            "budget_spent": f"{spent_ratio*100:.1f}%",
            "status": get_status(spent_ratio)
        })
    
    return daily_report

def get_status(ratio):
    if ratio >= 1.0: return "EXHAUSTED"
    if ratio >= 0.8: return "CRITICAL"
    if ratio >= 0.5: return "WARNING"
    return "HEALTHY"

# 시나리오: 일 100만 요청, 99.9% 목표, 30일 윈도우
# 처음 5일은 정상, 6일째 장애 발생
daily_rates = [0.0005] * 5 + [0.005] + [0.001] * 4 + [0.0005] * 20

report = simulate_budget_burn(
    total_requests_per_day=1_000_000,
    target_availability=0.999,
    window_days=30,
    daily_error_rates=daily_rates
)

print(f"{'Day':<5} {'Error Rate':<12} {'Cumul Errors':<14} {'Budget':<10} {'Status'}")
print("-" * 55)
for r in report[:10]:  # 처음 10일만 출력
    print(f"{r['day']:<5} {r['daily_error_rate']:<12} {r['cumulative_errors']:<14} {r['budget_spent']:<10} {r['status']}")
```

출력 예시:
```
Day   Error Rate   Cumul Errors   Budget     Status
-------------------------------------------------------
1     0.050%       500            1.7%       HEALTHY
2     0.050%       1000           3.3%       HEALTHY
3     0.050%       1500           5.0%       HEALTHY
4     0.050%       2000           6.7%       HEALTHY
5     0.050%       2500           8.3%       HEALTHY
6     0.500%       7500           25.0%      HEALTHY
7     0.100%       8500           28.3%      HEALTHY
8     0.100%       9500           31.7%      HEALTHY
9     0.100%       10500          35.0%      HEALTHY
10    0.100%       11500          38.3%      HEALTHY
```

6일째 장애(0.5% 오류율)가 하루 만에 버짓의 16.7%를 소진합니다. 평소 0.05% 오류율에서는 하루에 1.7%밖에 소진하지 않으므로, 장애 하루가 평소 10일치 버짓을 소모한 셈입니다.

## 에러 버짓과 릴리스 의사결정 흐름

에러 버짓을 실제 릴리스 판단에 연결하는 흐름도입니다.

```python
def release_decision(budget_spent_pct, burn_rate, change_risk):
    """
    릴리스 의사결정 함수
    change_risk: 'low', 'medium', 'high'
    """
    # 버짓 소진 100% 이상: 모든 배포 중단
    if budget_spent_pct >= 100:
        return {
            "decision": "BLOCK",
            "reason": "에러 버짓 소진, 안정화만 허용",
            "allowed": ["hotfix", "rollback"],
        }
    
    # 버짓 80% 이상: 고위험 변경 차단
    if budget_spent_pct >= 80:
        if change_risk == "high":
            return {
                "decision": "BLOCK",
                "reason": "버짓 위험 구간, 고위험 변경 차단",
                "allowed": ["hotfix", "low-risk config"],
            }
        return {
            "decision": "REVIEW",
            "reason": "버짓 위험 구간, 추가 리뷰 필요",
            "required": ["SRE approval", "canary 1% 시작"],
        }
    
    # 버짓 50% 이상: 리뷰 강화
    if budget_spent_pct >= 50:
        return {
            "decision": "REVIEW",
            "reason": "버짓 절반 소진, 리뷰 강화",
            "required": ["peer review", "canary 5%"],
        }
    
    # 버짓 여유: 정상 배포
    return {
        "decision": "APPROVE",
        "reason": "버짓 여유, 정상 배포 가능",
        "required": ["standard review"],
    }

# 예시
print(release_decision(45, 1.2, "medium"))
print(release_decision(82, 3.0, "high"))
print(release_decision(100, 14.4, "low"))
```

이 함수는 단순하지만 중요한 원칙을 보여 줍니다. 에러 버짓이 의사결정 규칙과 연결되지 않으면 단순 관찰 지표에 불과합니다. 버짓 상태에 따라 배포 허용 범위가 자동으로 바뀌는 구조가 있어야 팀이 매번 논쟁 없이 움직일 수 있습니다.

## 에러 버짓 대시보드 구성

에러 버짓을 효과적으로 운영하려면 대시보드에 다음 정보가 한눈에 보여야 합니다.

| 패널 | 내용 | 형식 |
| --- | --- | --- |
| 버짓 잔량 | 남은 에러 버짓 (%) | Gauge (초록→노랑→빨강) |
| 소진 추이 | 30일간 누적 소진 그래프 | Time series + 목표선 |
| Burn rate | 현재 소진 속도 (1h, 6h 윈도우) | Stat (1x, 2x, 14.4x) |
| 정책 상태 | 현재 적용 중인 릴리스 정책 | Text (SHIP/REVIEW/FREEZE) |
| 최근 배포 | 배포 시점과 이후 오류 변화 | Annotations + overlay |

```promql
# 에러 버짓 잔량 계산 (Grafana 변수 사용)
1 - (
  sum(increase(http_requests_total{status=~"5..",service="$service"}[30d]))
  /
  (sum(increase(http_requests_total{service="$service"}[30d])) * (1 - $target))
)
```

대시보드는 "지금 배포해도 되는가?"라는 단일 질문에 답하는 도구로 설계해야 합니다. 그래프가 많다고 좋은 대시보드가 아닙니다. 판단에 필요한 정보만 보여 주는 대시보드가 좋은 대시보드입니다.

## 에러 버짓 운영 시 팀 간 협업

에러 버짓은 SRE팀만의 지표가 아닙니다. 제품팀, 개발팀, 경영진이 모두 같은 숫자를 보고 움직일 때 진짜 효과가 나타납니다.

**제품팀과의 협업:**

제품팀은 새로운 기능을 빨리 출시하고 싶어합니다. 에러 버짓이 충분히 남아 있으면 "지금 실험해도 괜찮습니다"라고 데이터로 말할 수 있습니다. 반대로 버짓이 부족하면 "이번 주는 안정화를 먼저 하고, 다음 주에 출시합시다"라고 제안할 근거가 됩니다.

**개발팀과의 협업:**

배포 후 버짓 소진 속도가 올라가면 해당 배포가 문제를 만들었다는 신호입니다. 개발팀은 이 신호를 보고 빠르게 롤백하거나 hotfix를 적용할 수 있습니다. 번아웃 없이 판단할 수 있습니다.

**경영진과의 협업:**

경영진은 "우리 서비스가 충분히 안정적인가?"라는 질문에 답을 원합니다. 에러 버짓 달성률을 월간 보고에 포함하면 신뢰성 투자의 효과를 정량적으로 보여 줄 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 에러 버짓은 계산 가능한 숫자입니다.
- burn rate는 누적 값보다 더 빠른 조기 신호를 줄 수 있습니다.
- 정책 분기가 있어야 버짓이 실제 행동 규칙이 됩니다.
- 버짓은 릴리스 속도와 안정화 우선순위를 조정하는 기준이 됩니다.

## 여기서 자주 헷갈립니다

첫 번째 실수는 에러 버짓을 문서에만 적어 두는 것입니다. 그러면 숫자는 있지만 팀 행동은 그대로입니다. 리뷰 기준과 freeze 조건이 함께 있어야 합니다.

두 번째 실수는 누적 소진량만 보고 안심하는 것입니다. 최근 몇 시간 동안 burn rate가 비정상적으로 높다면 상황은 이미 빠르게 악화되고 있을 수 있습니다.

세 번째 실수는 에러 버짓을 사람을 혼내는 도구로 쓰는 것입니다. 그러면 팀은 숫자를 숨기거나 방어적으로 행동합니다. 에러 버짓은 학습과 의사결정을 돕는 도구여야 합니다.

## 운영 체크리스트

- [ ] SLO에서 에러 버짓을 계산할 수 있다.
- [ ] 누적 소진 비율과 burn rate를 함께 본다.
- [ ] review와 freeze 정책이 문서화되어 있다.
- [ ] 버짓 상태가 실제 릴리스 판단에 반영된다.
- [ ] 버짓을 비난 도구가 아니라 운영 기준으로 사용한다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 에러 버짓을 벌점표가 아니라 계기판으로 봅니다. 목표를 지키는 범위 안에서는 더 빠르게 움직이고, 목표를 위협하는 순간에는 안정화로 전환하는 장치로 이해합니다.

또한 버짓은 SRE만 보는 숫자가 아닙니다. 제품팀, 플랫폼팀, 온콜 담당자가 모두 같은 숫자를 보고 움직일 때 의미가 커집니다. 강한 팀은 에러 버짓을 기술 지표이자 운영 정책 언어로 함께 씁니다.

## 에러 버짓 정책 템플릿

에러 버짓을 운영 규칙으로 만들려면 정책 문서가 필요합니다. 다음은 팀이 처음 버짓 정책을 도입할 때 쓸 수 있는 템플릿 예시입니다.

### Error Budget Policy Template

```yaml
team: payments-api
slo:
  target: 99.9%
  window: 30d
  sli: http_success_ratio

error_budget:
  allowed_errors_per_month: 1000
  
policy:
  - condition: spent < 50%
    action: SHIP
    description: 정상 배포, 실험 기능 허용
    approval: 팀 리드 승인
  
  - condition: spent >= 50% and spent < 80%
    action: REVIEW
    description: 모든 배포에 SRE 리뷰 필수, 카나리 배포 및 추가 모니터링 강화
    approval: SRE + 팀 리드 승인
  
  - condition: spent >= 80%
    action: FREEZE
    description: 모든 새 기능 배포 중단, hotfix 및 안정화 작업만 허용
    approval: VP Engineering 승인
  
  - condition: slo_violated (spent >= 100%)
    action: INCIDENT
    description: 임시 운영 체제, 포스트모텀 작성, 재발 방지 계획 수립
    approval: 임원 회의 보고

alerts:
  - type: burn_rate
    threshold: 14.4
    window: 1h
    description: 1시간 동안 14.4배 속도 초과 시 on-call 알림
  
  - type: cumulative
    threshold: 80%
    description: 누적 소진 80% 도달 시 팀 전체 알림

review_schedule:
  - frequency: weekly
    participants: [team-lead, sre, product]
    agenda: [버짓 상태, burn rate 추이, 향후 2주 리스크 평가]
```

이 템플릿을 팀 상황에 맞게 조정하면 에러 버짓이 문서가 아니라 실제 운영 규칙이 됩니다. 소진 비율별 행동, 승인 규칙, 알림 기준, 주간 리뷰 일정이 모두 명시되어 있어 장애 상황에서도 판단이 빠릅니다.

## 정리

에러 버짓은 목표와 현실 사이의 허용 가능한 실패 범위를 숫자로 드러내는 장치입니다. 중요한 점은 숫자를 계산하는 데서 끝나지 않고, 그 숫자를 릴리스 정책과 안정화 우선순위에 연결하는 데 있습니다.

다음 글에서는 monitoring을 다룹니다. 어떤 신호를 봐야 지금 움직여야 하는지 판단할 수 있는지, 그리고 알림 피로 없이 시스템 상태를 읽는 방법을 이어서 정리하겠습니다.

## 처음 질문으로 돌아가기

- **에러 버짓은 왜 속도와 안정성 사이의 공통 언어가 될까요?**
  - Error Budget를 냈으로 돌려무기단 연를 닱 도나 비라 스딤를 내 넌 윚을 낤낰님니다. 곧 단계는 Error Budget를 본꨸ 닝 동안 중욕단 답 비라 스딤를 내단 남으로 끝낸는 메떰랜 보중닜드를 째나 넌 낤달니다.
- **SLO를 세운 뒤 허용 가능한 실패 범위는 어떻게 계산할까요?**
  - Error Budget을 나누 단계로 나누어 보메냐, Error Budget 지출 스딤가 단계 메 가링 비좠을 나나 남 메 낤낰 곧멌맙갬니다. 난 비좠을 남메는 드돐 난다 빠밐 단계 메 낤낰 곧멌맙갬니다.
- **누적 소진량과 burn rate는 왜 다른 질문에 답할까요?**
  - burn rate를 보메나 모닞 가까운 당른 갈헴맙냁 답다 멙 낤난 비좠을 남 분 낤낰 드돐 남 메는 비좠을 남 낌 빌냐른 뛄 단계 메 낤낰 드돐 난 비좠답니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- **Error Budget (현재 글)**
- Monitoring (예정)
- Incident Response (예정)
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Embracing Risk - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Alerting on SLOs - Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/)
- [Error Budgets - Atlassian](https://www.atlassian.com/incident-management/kpis/error-budget)
- [Error Budget Policy - Google](https://sre.google/workbook/error-budget-policy/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, ErrorBudget, Reliability, Release, Risk
