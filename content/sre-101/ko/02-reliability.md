---
episode: 2
language: ko
last_reviewed: '2026-05-14'
seo_description: 신뢰성을 가용성, 지연 시간, 정확성, 내구성으로 정의하고 분위수와 비즈니스별 핵심 지표 선택법을 정리합니다.
series: sre-101
status: content-ready
tags:
- SRE
- Reliability
- Availability
- Latency
- Quality
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (2/10): Reliability"
---

# SRE 101 (2/10): Reliability

서비스가 안정적인지 물으면 많은 팀이 먼저 분위기를 말합니다. 요즘 큰 불만이 없었다, 장애가 자주 나지는 않았다, 체감상 괜찮다는 식입니다. 이런 말은 팀 분위기를 설명할 수는 있어도 신뢰성을 정의하지는 못합니다.

신뢰성은 감상이 아니라 숫자로 증명할 수 있어야 합니다. 그래야 제품팀과 운영팀이 같은 대상을 보고도 다른 언어를 쓰지 않게 됩니다.

이 글은 SRE 101 시리즈의 2번째 글입니다. 여기서는 reliability를 가용성, 지연 시간, 정확성, 내구성이라는 네 차원으로 나눠 보고, 왜 평균값 하나로는 신뢰성을 설명하기 어려운지 정리합니다.


![SRE 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/02/02-01-concept-at-a-glance.ko.png)
*SRE 101 2장 흐름 개요*
> Reliability는 하나의 숫자가 아니라 여러 차원의 조합입니다. 각 차원은 서로 다른 실패 양상을 드러내며, 서비스 특성에 따라 어떤 차원을 우선할지가 달라집니다.

## 먼저 던지는 질문

- reliability를 막연한 안정감이 아니라 측정 가능한 값으로 보려면 무엇이 필요할까요?
- 가용성과 지연 시간은 왜 비슷해 보이지만 다른 문제일까요?
- 정확성과 내구성은 어떤 시스템에서 특히 더 중요해질까요?

## 왜 이 주제가 중요한가

숫자가 없으면 같은 시스템을 보고도 대화가 흔들립니다. 제품팀은 충분히 안정적이라고 느끼는데, 운영팀은 아직 위험하다고 판단할 수 있습니다. 이런 충돌은 의견 차이처럼 보이지만, 실제로는 무엇을 신뢰성으로 볼지 합의가 없는 경우가 많습니다.

또한 서비스마다 중요한 차원이 다릅니다. 결제 시스템은 정확성과 내구성이 특히 중요하고, 검색 서비스는 지연 시간에 훨씬 민감할 수 있습니다. 신뢰성을 한 개의 점수처럼 다루면 이런 차이를 놓치기 쉽습니다.

## 한 문장으로 잡는 멘탈 모델

> 신뢰성은 한 가지 기분 좋은 느낌이 아니라, 사용자가 기대한 결과를 여러 차원의 숫자로 증명하는 일입니다.

## 한눈에 보는 구조

이 그림이 보여 주는 메시지는 단순합니다. 서비스가 살아 있었는지만으로는 충분하지 않습니다. 빨랐는지, 결과가 맞았는지, 저장한 데이터가 유지됐는지도 함께 봐야 신뢰성이라는 말을 제대로 쓸 수 있습니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 실무에서 보는 포인트 |
| --- | --- | --- |
| availability | 서비스가 사용 가능한 상태였던 비율 | 요청을 받을 수 있었는지 보여 줍니다 |
| latency | 요청을 처리하는 데 걸린 시간 | 느린 사용자 경험을 드러냅니다 |
| correctness | 결과가 기대한 값과 맞는 정도 | 빠르게 틀리는 시스템을 잡아냅니다 |
| durability | 저장한 데이터가 유지되는 정도 | 데이터 손실 위험을 드러냅니다 |
| MTTR | 장애 뒤 복구까지 걸린 평균 시간 | 회복 능력의 수준을 보여 줍니다 |

## 신뢰성은 왜 여러 차원으로 나눠야 할까

가용성 하나만 보면 서비스는 멀쩡해 보일 수 있습니다. 그런데 응답이 10초씩 걸리거나, 결과가 틀리거나, 저장한 데이터가 사라진다면 사용자는 이미 실패를 경험한 것입니다. 그래서 신뢰성은 하나의 숫자보다는, 서로 다른 실패 양상을 포착하는 지표 묶음에 가깝습니다.

현업에서는 이 구분이 특히 중요합니다. 예를 들어 결제 API가 99.99% 가용성을 유지해도 금액 계산이 틀리면 신뢰성은 낮습니다. 반대로 추천 시스템이 약간 틀린 결과를 내더라도 빠르게 응답하는 편이 더 중요한 경우도 있습니다. 어떤 차원을 가장 우선으로 둘지는 서비스의 업무 의미에 따라 달라집니다.

## 숫자가 없을 때 생기는 문제

신뢰성을 수치로 정의하지 않으면 회의가 금방 추상적으로 흐릅니다. “요즘 느리다”, “예전보다 덜 안정적이다”, “사용자 불만이 좀 늘었다” 같은 표현은 방향을 알려 주지만, 설계나 투자 우선순위로 연결되기는 어렵습니다.

반대로 차원별 숫자가 있으면 판단이 빨라집니다. 지연 시간이 문제인지, 오류 비율이 문제인지, 데이터 손실 위험이 문제인지 분리해서 볼 수 있기 때문입니다. 강한 팀일수록 신뢰성을 감정이 아니라 분해 가능한 품질 속성으로 다룹니다.

## Reliability 차원별 비즈니스 영향

각 Reliability 차원이 외로워졌을 때 사용자와 비즈니스에 미치는 영향은 서로 다릅니다.

| 차원 | 문제 상황 | 사용자 체감 | 비즈니스 영향 |
| --- | --- | --- | --- |
| **Availability** | 서비스에 접속할 수 없음 | 즉각적 불만, 대체 서비스 탐색 | 매출 손실, 신뢰 하락 |
| **Latency** | 응답이 느림 (p95 > 1s) | 답답함, 이탈 고려 | 전환율 하락, 이탈률 상승 |
| **Correctness** | 결과가 틀림 (결제 금액 오류) | 신뢰 상실, 환불 요구 | 법적 분쟁, 보상 비용 |
| **Durability** | 데이터 손실 (주문 기록 사라짐) | 치명적 불신, 탈퇴 | 복구 불가, 규제 문제 |

이 표는 서비스별로 어떤 차원을 가장 엄격하게 관리해야 할지를 판단하는 기준이 됩니다.

## 좋은 SLI 선택 기준

신뢰성을 측정하려면 먼저 좋은 SLI(Service Level Indicator)를 고르는 것이 중요합니다. 다음 기준을 충족하는 지표가 좋은 SLI입니다.

**사용자 경험과 직접 연결됩니다.** CPU 사용률이나 메모리 사용률은 서버 상태를 보여 주지만 사용자가 실제로 느끼는 문제와는 거리가 멉니다. 반면 HTTP 성공률이나 응답 시간은 사용자가 느끼는 품질을 직접 반영합니다.

**측정과 재현이 간단합니다.** 복잡한 계산식이나 여러 시스템의 데이터를 합쳐야 하는 지표는 논쟁을 만듭니다. 한 곳에서 명확하게 측정할 수 있어야 합니다.

**행동으로 연결됩니다.** 지표가 나빠졌을 때 무엇을 해야 할지 분명해야 합니다. 관찰만 하고 대응할 수 없는 지표는 운영 가치가 낮습니다.

**비즈니스 중요도를 반영합니다.** 모든 API를 동등하게 보지 말고, 핵심 사용자 경로(결제, 로그인 등)에 더 엄격한 목표를 세워야 합니다.

## 구체적인 SLO 설정 예시

추상적인 99.9% 가용성보다, 실제 다운타임 허용치로 변환하면 목표의 현실성이 더 명확해집니다.

```python
def slo_to_downtime(availability, window_days):
    uptime_ratio = availability
    downtime_ratio = 1 - uptime_ratio
    total_minutes = window_days * 24 * 60
    allowed_downtime_min = total_minutes * downtime_ratio
    return allowed_downtime_min

# 예시
print(f"99.9% (monthly): {slo_to_downtime(0.999, 30):.1f}min")  # 43.2분
print(f"99.95% (monthly): {slo_to_downtime(0.9995, 30):.1f}min")  # 21.6분
print(f"99.99% (monthly): {slo_to_downtime(0.9999, 30):.1f}min")  # 4.3분
```

이 계산을 통해 99.99% 가용성은 월간 4.3분의 다운타임만 허용한다는 점을 명확히 할 수 있습니다. 이 숫자는 현실적으로 달성 가능한지, 어떤 투자가 필요한지 판단하는 기준이 됩니다.
## 단계별로 네 가지 차원 측정하기

### 1단계 — 가용성 측정

```python
def availability(uptime_s, total_s):
    return uptime_s / total_s
```

가용성은 가장 익숙한 출발점입니다. 서비스가 살아 있었는지, 요청을 받을 수 있었는지를 보여 줍니다. 다만 이 값이 높다고 해서 사용자 경험이 자동으로 좋다고 보기는 어렵습니다.

### 2단계 — p95 지연 시간 측정

```python
def p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

평균값은 보기 좋게 나올 때가 많습니다. 하지만 사용자는 평균이 아니라 느린 순간을 기억합니다. 그래서 실무에서는 p95, p99 같은 분위수를 더 자주 봅니다. 꼬리 지연이 길어지면 체감 품질이 빠르게 나빠집니다.

### 3단계 — 정확성 측정

```python
def correctness(correct, total):
    return correct / total
```

정확성은 종종 운영 지표에서 뒤로 밀립니다. 그러나 결제, 권한, 정산, 주문 처리처럼 결과가 틀리면 바로 비즈니스 문제가 되는 시스템에서는 가장 먼저 점검해야 할 차원입니다.

### 4단계 — 내구성 측정

```python
def lost_ratio(lost, stored):
    return lost / stored
```

내구성은 저장된 데이터가 어느 정도 보존되는지를 보여 줍니다. 백업을 갖고 있다는 사실만으로 충분하지 않습니다. 실제로 얼마나 잃을 수 있는지, 잃었을 때 얼마나 복구할 수 있는지까지 함께 봐야 합니다.

### 5단계 — 차원을 하나의 목표 묶음으로 정리

```python
slos = {
    "availability": 0.999,
    "p95_ms": 200,
    "correctness": 0.9999,
    "lost_ratio": 1e-9,
}
```

이제 신뢰성은 한 문장이 아니라 운영 가능한 목표 묶음이 됩니다. 서비스 특성에 따라 어떤 차원을 더 엄격하게 잡을지는 달라지지만, 최소한 무엇을 중요하게 보는지는 선명해집니다.

### 6단계 — 다중 차원 SLO를 한 번에 평가하기

실무에서는 여러 차원의 목표를 한번에 평가하는 함수가 유용합니다.

```python
def evaluate_slos(metrics, slos):
    results = {}
    results["availability"] = metrics["uptime"] / metrics["total_time"] >= slos["availability"]
    results["latency"] = metrics["p95_ms"] <= slos["p95_ms"]
    results["correctness"] = metrics["correct"] / metrics["total"] >= slos["correctness"]
    results["durability"] = metrics["lost"] / metrics["stored"] <= slos["lost_ratio"]
    results["overall"] = all(results.values())
    return results
```

## MTTR vs MTBF

Reliability를 이야기할 때 자주 등장하는 두 지표가 MTTR(Mean Time To Repair)과 MTBF(Mean Time Between Failures)입니다.

**MTTR은 회복 속도**를 보여 줍니다. 장애가 발생한 후 정상 상태로 돌아오는 데 걸린 평균 시간입니다. MTTR이 짧을수록 장애의 영향이 작아집니다.

**MTBF는 안정성**을 보여 줍니다. 장애 사이의 평균 시간으로, 길수록 장애가 드물다는 뜻입니다.

두 지표를 함께 보면 서비스의 전체적인 신뢰성 동작을 이해할 수 있습니다. MTBF가 길고 MTTR이 짧으면 가용성은 높아집니다.
## 처음 Reliability 목표를 세울 때 피할 실수

**모든 차원에 동일한 목표를 적용합니다.** 내부 관리 API와 결제 API에 동일한 99.99% 가용성을 요구하면, 중요도가 낮은 경로에 과도한 투자가 발생합니다.

**평균만 보고 만족합니다.** 평균 응답 시간이 100ms로 좋아 보여도, p99가 2초라면 일부 사용자는 매우 나쁨 경험을 하고 있습니다.

**차원 간 관계를 무시합니다.** Saturation이 높아지면 latency가 함께 나빠지고, latency가 길어지면 timeout으로 errors가 늘어납니다. 차원을 따로 보지 말고 함께 봐야 원인을 정확히 읽을 수 있습니다.
이 함수는 네 가지 차원을 동시에 평가하고, 모두 충족했을 때만 `overall`이 참이 됩니다. 한 차원만 나빠도 신뢰성이 외로워졌다고 판단하는 논리입니다.

## PromQL로 네 차원 측정하기

Reliability를 네 차원으로 나눴다면, 각 차원을 실제로 어떻게 측정하는지 구체적인 쿼리로 확인해야 합니다. 다음은 Prometheus에서 각 차원을 측정하는 PromQL 예시입니다.

### 가용성 측정 쿼리

```promql
# 5분 윈도우 가용성 (성공 요청 / 전체 요청)
sum(rate(http_requests_total{status=~"2.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

이 쿼리는 HTTP 2xx 응답 비율을 계산합니다. 서비스별로 label을 붙이면 개별 서비스의 가용성을 따로 추적할 수 있습니다. 가용성이 SLO 목표 아래로 떨어지면 에러 버짓이 소진되기 시작합니다.

### 지연 시간 분위수 쿼리

```promql
# p50, p95, p99 지연 시간을 한번에 비교
histogram_quantile(0.50,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

p50과 p99의 격차가 클수록 꼬리 지연 문제가 심합니다. 예를 들어 p50이 50ms인데 p99가 3초라면, 100명 중 1명은 매우 느린 경험을 하고 있다는 뜻입니다. 이런 격차는 데이터베이스 잠금, 캐시 미스, 외부 API 타임아웃에서 자주 발생합니다.

### 정확성 측정 쿼리

정확성은 단순 HTTP 상태 코드로는 측정하기 어려운 경우가 많습니다. 응답이 200 OK여도 내용이 틀릴 수 있기 때문입니다. 그래서 비즈니스 로직 수준의 검증 메트릭을 별도로 만들어야 합니다.

```promql
# 결제 정확성: 정산 결과가 일치한 비율
sum(rate(payment_reconciliation_total{result="match"}[1h]))
/
sum(rate(payment_reconciliation_total[1h]))
```

```python
# 정확성 검증 예시: 실제 결과와 기대 결과 비교
def correctness_check(actual_amount, expected_amount, tolerance=0.01):
    """금액 정확성 검증 (1% 오차 허용)"""
    if expected_amount == 0:
        return actual_amount == 0
    diff_ratio = abs(actual_amount - expected_amount) / expected_amount
    return diff_ratio <= tolerance

# 정산 검증 배치
results = [
    correctness_check(10000, 10000),   # True
    correctness_check(9950, 10000),    # True (0.5% 차이)
    correctness_check(9800, 10000),    # False (2% 차이)
]
accuracy = sum(results) / len(results)
print(f"정확성: {accuracy*100:.1f}%")  # 66.7%
```

### 내구성 측정

내구성은 저장한 데이터가 손실 없이 유지되는지를 보여 줍니다. 클라우드 스토리지는 일반적으로 99.999999999%(11 nines) 내구성을 제공하지만, 애플리케이션 레벨에서의 데이터 손실은 별도 측정이 필요합니다.

```promql
# 데이터 동기화 실패 비율
sum(rate(data_sync_failures_total[1h]))
/
sum(rate(data_sync_attempts_total[1h]))
```

```python
def durability_score(objects_stored, objects_verified):
    """내구성 점수: 검증된 객체 / 저장된 객체"""
    if objects_stored == 0:
        return 1.0
    return objects_verified / objects_stored

# 백업 검증 결과
score = durability_score(1_000_000, 999_998)
print(f"내구성: {score*100:.6f}%")  # 99.999800%
```

## 서비스 유형별 Reliability 우선순위

모든 서비스가 네 차원을 동일한 비중으로 관리할 필요는 없습니다. 서비스의 비즈니스 특성에 따라 어떤 차원을 가장 엄격하게 관리해야 할지 달라집니다.

| 서비스 유형 | 1순위 | 2순위 | 근거 |
| --- | --- | --- | --- |
| 결제/정산 | 정확성 | 내구성 | 금액이 틀리면 법적 문제, 데이터 손실은 복구 불가 |
| 실시간 검색 | 지연 시간 | 가용성 | 0.5초만 느려도 이탈률 급증 |
| 파일 스토리지 | 내구성 | 가용성 | 데이터를 잃으면 복구 불가, 잠시 접속 불가는 용납 가능 |
| 소셜 피드 | 가용성 | 지연 시간 | 접속 자체가 안 되면 이탈, 약간 느려도 체감 영향 낮음 |
| IoT 센서 수집 | 가용성 | 내구성 | 데이터 유실 방지가 핵심, 지연은 수초까지 허용 |

이 표는 SLO를 처음 설계할 때 어떤 차원부터 목표를 세울지 결정하는 데 도움이 됩니다. 핵심 차원에는 더 엄격한 목표를 설정하고, 상대적으로 덜 중요한 차원에는 현실적인 목표를 둡니다.

## Reliability 측정 대시보드 설계

네 차원을 한눈에 볼 수 있는 대시보드 구성은 다음 순서가 효과적입니다.

### 첫 번째 행: 핵심 요약

| 패널 | 내용 | 형식 |
| --- | --- | --- |
| 현재 가용성 | 최근 5분 성공률 | Stat (초록/빨강) |
| SLO 달성률 | 30일 윈도우 기준 | Gauge (목표선 포함) |
| 에러 버짓 잔량 | 남은 실패 허용량 | Stat (%) |

### 두 번째 행: 차원별 상세

| 패널 | 내용 | 형식 |
| --- | --- | --- |
| 가용성 추이 | 24시간 가용성 그래프 | Time series |
| 지연 시간 분위수 | p50, p95, p99 | Time series (3 lines) |
| 오류 비율 | 5xx 비율 추이 | Time series |
| 포화도 | CPU, 메모리, 커넥션 풀 | Time series |

### 세 번째 행: 진단 정보

| 패널 | 내용 | 형식 |
| --- | --- | --- |
| 최근 배포 | 배포 시점 표시 | Annotations |
| 알림 이력 | 최근 발화된 알림 목록 | Table |
| 서비스 의존성 | 외부 API 상태 | Status map |

대시보드는 위에서 아래로 "지금 문제가 있는가?" → "어떤 차원에서 문제인가?" → "원인은 무엇인가?"의 질문에 답하는 순서로 구성해야 합니다. 이 순서가 없으면 그래프는 많은데 판단은 느린 상태가 됩니다.

## Reliability 목표를 비즈니스 언어로 번역하기

기술팀은 99.9%, p99 같은 숫자로 신뢰성을 이야기하지만, 비즈니스팀은 이 숫자가 실제로 무엇을 의미하는지 궁금해합니다. Reliability 목표를 비즈니스 영향으로 번역하면 팀 간 커뮤니케이션이 훨씬 쉬워집니다.

```python
def availability_to_business_impact(
    availability, monthly_revenue, monthly_users
):
    """가용성을 비즈니스 영향으로 번역"""
    downtime_minutes = (1 - availability) * 30 * 24 * 60
    revenue_at_risk = monthly_revenue * (1 - availability)
    affected_users = monthly_users * (1 - availability)
    
    return {
        "availability": f"{availability*100:.3f}%",
        "monthly_downtime_min": f"{downtime_minutes:.1f}분",
        "revenue_at_risk": f"₩{revenue_at_risk:,.0f}",
        "affected_users": f"{affected_users:,.0f}명",
    }

# 예시: 월매출 10억, 월간 사용자 100만
for avail in [0.99, 0.999, 0.9999]:
    impact = availability_to_business_impact(avail, 1_000_000_000, 1_000_000)
    print(f"\n{impact['availability']}:")
    print(f"  월간 다운타임: {impact['monthly_downtime_min']}")
    print(f"  매출 위험: {impact['revenue_at_risk']}")
    print(f"  영향 사용자: {impact['affected_users']}")
```

출력 예시:
```
99.000%:
  월간 다운타임: 432.0분
  매출 위험: ₩10,000,000
  영향 사용자: 10,000명

99.900%:
  월간 다운타임: 43.2분
  매출 위험: ₩1,000,000
  영향 사용자: 1,000명

99.990%:
  월간 다운타임: 4.3분
  매출 위험: ₩100,000
  영향 사용자: 100명
```

이 번역이 있으면 비즈니스팀과 기술팀이 같은 언어로 SLO를 논의할 수 있습니다. "99.9%에서 99.99%로 올리려면 얼마나 투자해야 하는가"라는 질문에도 비용 대비 효과를 구체적으로 비교할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 신뢰성은 단일 척도가 아니라 여러 차원의 조합입니다.
- p95, p99 같은 분위수는 평균보다 실제 사용자 경험에 더 가깝습니다.
- 정확성과 내구성은 데이터 중심 시스템에서 특히 중요합니다.
- 차원별 목표를 함께 놓아야 서비스 성격에 맞는 운영 판단이 가능합니다.

## 여기서 자주 헷갈립니다

가장 흔한 오해는 availability가 곧 reliability라고 생각하는 것입니다. 서비스가 살아 있어도 응답이 지나치게 느리거나 결과가 틀리면 사용자는 이미 실패를 경험합니다.

또 다른 오해는 평균 latency만 보고 안심하는 것입니다. 평균은 안정적으로 보여도 일부 요청이 심하게 느리면 사용자는 그 느린 구간에서 서비스를 평가합니다. 분위수를 별도로 보는 이유가 여기에 있습니다.

그리고 durability를 백업 유무와 같은 말처럼 다루는 경우도 많습니다. 실제 운영에서는 손실 허용 범위와 복구 가능성이 함께 있어야 내구성 이야기를 할 수 있습니다.

## 운영 체크리스트

- [ ] 가용성, 지연 시간, 정확성, 내구성을 분리해서 정의했다.
- [ ] 평균 외에 p95 또는 p99를 함께 보고 있다.
- [ ] 정확성이 중요한 경로에는 자동 검증 수단이 있다.
- [ ] 데이터 손실 허용 범위와 복구 기대치를 문서화했다.
- [ ] 서비스 성격에 따라 어떤 차원을 더 우선하는지 팀이 합의했다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 신뢰성을 하나의 예쁜 숫자로 포장하려 하지 않습니다. 어떤 시스템은 지연 시간에, 어떤 시스템은 정확성에, 어떤 시스템은 내구성에 더 민감하다는 사실을 전제로 설계합니다.

또한 신뢰성 논의는 운영팀만의 언어가 아닙니다. 제품팀이 어떤 경험을 사용자에게 약속하는지와 바로 연결됩니다. 그래서 좋은 신뢰성 지표는 인프라 상태를 넘어서 제품 품질의 일부가 됩니다.

## 정리

reliability는 막연한 안정감이 아니라, 서비스가 기대한 방식으로 동작했음을 여러 차원의 숫자로 보여 주는 일입니다. 가용성, 지연 시간, 정확성, 내구성을 구분해서 보기 시작하면, 무엇이 흔들리고 있는지 훨씬 더 정확하게 읽을 수 있습니다.

다음 글에서는 SLI, SLO, SLA를 구분합니다. 무엇을 측정하고, 무엇을 목표로 삼고, 무엇을 외부 약속으로 문서화해야 하는지 이어서 정리하겠습니다.

## 처음 질문으로 돌아가기

- **reliability를 막연한 안정감이 아니라 측정 가능한 값으로 보려면 무엇이 필요할까요?**
  - Reliability를 네 개의 차원(가용성, 지연 시간, 정확성, 내구성)으로 나누면 각각을 측정하고 그 값으로 현재 상태를 판단할 수 있습니다. 단일 지표만 보면 놓치는 문제를 발견하는 데도 도움이 됩니다.
- **가용성과 지연 시간은 왜 비슷해 보이지만 다른 문제일까요?**
  - 가용성은 서비스가 살아 있는지를 보여 주지만, 지연 시간은 사용자가 실제로 기다린 시간을 측정합니다. p95, p99 같은 분위수로 보면 평균보다 느린 구간의 체감 품질을 더 잘 드러낼 수 있습니다.
- **정확성과 내구성은 어떤 시스템에서 특히 더 중요해질까요?**
  - 정확성과 내구성은 데이터가 중심인 시스템(결제, 권한, 정산, 메시지 등)에서 가장 먼저 점검해야 할 차원으로, 빠르게 틀리거나 데이터를 잃는 문제는 비즈니스 신뢰를 직접 흔듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- **Reliability (현재 글)**
- SLI, SLO, SLA (예정)
- Error Budget (예정)
- Monitoring (예정)
- Incident Response (예정)
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Reliability - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Tail at Scale](https://research.google/pubs/pub40801/)
- [The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Availability vs Durability - AWS](https://aws.amazon.com/s3/storage-classes/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, Reliability, Availability, Latency, Quality
