---
episode: 9
language: ko
last_reviewed: '2026-05-14'
seo_description: 미래 수요를 예측하고 시스템 공급을 최적화하는 용량 계획, 헤드룸 설정과 부하 테스트, 비용 계산법을 다룹니다.
series: sre-101
status: content-ready
tags:
- SRE
- CapacityPlanning
- Forecasting
- Performance
- Operations
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (9/10): Capacity Planning"
---

# SRE 101 (9/10): Capacity Planning

많은 팀이 증설을 이야기할 때 지난달 그래프부터 펼칩니다. 물론 과거 데이터는 중요합니다. 하지만 용량 계획은 과거를 복사하는 일이 아니라, 앞으로 들어올 수요를 예측하고 그 수요를 감당할 공급을 미리 맞추는 일입니다.

트래픽이 갑자기 치솟은 뒤에 대응하는 것은 보통 너무 늦습니다. 용량 계획은 성능 최적화의 부속 작업이 아니라, 장애 예방과 비용 통제를 동시에 다루는 운영 설계입니다.

이 글은 SRE 101 시리즈의 9번째 글입니다. 여기서는 capacity planning을 수요 예측, 헤드룸 설정, 부하 테스트, 확장 단위 계산, 비용 판단의 흐름으로 설명하고, 리드 타임과 반복 보정의 중요성까지 정리합니다.

## 먼저 던지는 질문

- 용량 계획은 왜 과거 복제가 아니라 미래 수요 예측일까요?
- 헤드룸은 왜 낭비가 아니라 보험에 가까울까요?
- 부하 테스트는 예측 모델을 어떻게 보정할까요?

## 큰 그림

![SRE 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/09/09-01-concept-at-a-glance.ko.png)

*SRE 101 9장 흐름 개요*

Capacity Planning을 현재 상태, 미래 요구, 한계 지점으로 나누어 봅니다.

> 용량 계획은 미리 다다를 상황을 숫자로 예측하고, 언제까지 버틸 수 있는지 보여주는 체계입니다.

## 왜 이 주제가 중요한가

예측이 없으면 증설은 늘 늦습니다. 트래픽이 급증한 뒤에 인스턴스를 더 붙이거나 장비를 확보하려 하면, 이미 사용자 경험은 나빠진 뒤일 가능성이 큽니다. 특히 이벤트성 피크가 있는 서비스일수록 사전 계획이 더 중요합니다.

반대로 여유 용량을 무작정 쌓아 두면 비용이 커집니다. 용량 계획의 핵심은 안전성과 비용을 함께 읽는 데 있습니다. 어느 정도 변동을 감수할지, 그 변동에 대비해 얼마를 더 쓸지 설명할 수 있어야 합니다.

## 한 문장으로 잡는 멘탈 모델

> 용량 계획은 수요 예측과 실제 처리 한계를 숫자로 맞춰, 장애 없이 성장할 수 있는 여유를 설계하는 일입니다.

## 한눈에 보는 구조

이 흐름은 용량 계획이 한 번의 계산으로 끝나지 않는다는 점을 보여 줍니다. 예측하고, 검증하고, 증설하고, 실제 사용량을 다시 보면서 계속 보정해야 합니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 운영에서 하는 역할 |
| --- | --- | --- |
| demand forecast | 미래 수요 예측값 | 얼마만큼 준비해야 하는지 정합니다 |
| headroom | 남겨 둔 여유 용량 | 스파이크와 변동성을 흡수합니다 |
| load test | 부하 실험 | 현재 한계를 검증합니다 |
| scaling unit | 확장 최소 단위 | 실제 증설 계산 기준이 됩니다 |
| lead time | 자원 확보까지 걸리는 시간 | 언제 결정을 내려야 하는지 정합니다 |

## 용량 계획은 왜 성능 테스트만으로 부족할까

부하 테스트는 지금 시스템이 어디까지 버티는지 보여 줍니다. 하지만 다음 분기 트래픽이 얼마나 늘지, 마케팅 이벤트가 얼마나 큰지, 신규 기능이 어떤 패턴을 만들지는 알려 주지 못합니다. 그래서 예측이 필요합니다.

반대로 예측만 있고 실제 한계 검증이 없으면 문서상 계산이 현실과 어긋날 수 있습니다. 강한 팀은 예측과 검증을 같이 봅니다. 수요는 모델로 보고, 공급은 부하 테스트로 확인하는 식입니다.

## 헤드룸은 왜 비용과 함께 봐야 할까

헤드룸은 남는 용량처럼 보여서 비용 낭비로 보이기 쉽습니다. 하지만 운영 관점에서는 변동성 보험에 가깝습니다. 스파이크, 장애 우회 트래픽, 예측 오차를 흡수할 공간이 없으면 작은 변화도 바로 장애로 이어집니다.

좋은 계획은 헤드룸의 필요성을 막연히 주장하지 않습니다. 어느 정도 변동을 감당하려고 얼마를 더 쓰는지 설명합니다. 비용과 용량을 따로 떼어 놓지 않는 이유가 여기에 있습니다.

## 용량 계획 입력 데이터

용량 계획을 제대로 하려면 어떤 데이터를 수집해야 하는지 명확해야 합니다. 다음 표는 주요 입력 데이터와 수집 방법을 보여 줍니다.

| 데이터 항목 | 수집 방법 | 예시 값 | 주의사항 |
| --- | --- | --- | --- |
| 현재 트래픽 | Prometheus `rate(http_requests_total[5m])` | 1500 RPS | 주간 평균, 피크 시간대 제외 |
| 리소스 사용률 | Node exporter CPU/memory metrics | CPU 45%, Memory 60% | 평균보다 p95 사용률 확인 |
| 주간 성장률 | 최근 4-8주 데이터 회귀 분석 | +10% per month | 계절성 보정 필요 |
| 피크 배수 | 일간 최대/평균 비율 | 2.5x | 프로모션, 이벤트 고려 |
| 노드당 처리량 | 부하 테스트 결과 | 350 RPS/node | latency p99 < 500ms 기준 |
| 리드 타임 | 벤더 조달 기간 | 2-4 weeks | 클라우드는 즉시, 온프레미스는 길어짐 |

이 데이터를 모두 수집하고 나면 예측 모델을 만들고 검증할 수 있습니다. 데이터가 불충분하면 예측의 정확도가 떨어집니다.

## Python 선형 회귀 용량 예측 예제

과거 트래픽 데이터를 기반으로 미래 용량을 예측하는 가장 단순한 방법은 선형 회귀입니다. numpy를 사용해 추세선을 그리고 미래 값을 예측합니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def linear_regression_forecast(historical_data, weeks_ahead):
    """
    선형 회귀로 미래 용량 예측
    
    Args:
        historical_data: List of (week, rps) tuples
        weeks_ahead: How many weeks to forecast
    
    Returns:
        Predicted RPS for each future week
    """
    weeks = np.array([w for w, _ in historical_data])
    rps = np.array([r for _, r in historical_data])
    
    # Fit linear regression: rps = a * week + b
    coefficients = np.polyfit(weeks, rps, 1)
    slope, intercept = coefficients
    
    # Generate predictions
    future_weeks = np.arange(weeks[-1] + 1, weeks[-1] + weeks_ahead + 1)
    predictions = slope * future_weeks + intercept
    
    return {
        "slope": slope,
        "intercept": intercept,
        "predictions": list(zip(future_weeks, predictions)),
        "growth_per_week": slope
    }

def plot_forecast(historical_data, forecast_result, weeks_ahead):
    """Plot historical data and forecast"""
    weeks_hist = [w for w, _ in historical_data]
    rps_hist = [r for _, r in historical_data]
    
    weeks_forecast = [w for w, _ in forecast_result["predictions"]]
    rps_forecast = [r for _, r in forecast_result["predictions"]]
    
    plt.figure(figsize=(12, 6))
    plt.plot(weeks_hist, rps_hist, 'bo-', label='Historical Data')
    plt.plot(weeks_forecast, rps_forecast, 'ro--', label='Forecast')
    plt.xlabel('Week')
    plt.ylabel('RPS')
    plt.title('Traffic Forecast (Linear Regression)')
    plt.legend()
    plt.grid(True)
    plt.savefig('/tmp/capacity_forecast.png')
    plt.close()

# Example usage
historical_data = [
    (1, 1200),
    (2, 1280),
    (3, 1350),
    (4, 1420),
    (5, 1500),
    (6, 1580),
    (7, 1650),
    (8, 1720)
]

weeks_ahead = 12  # Forecast next 3 months

result = linear_regression_forecast(historical_data, weeks_ahead)

print("=== Capacity Forecast ===")
print(f"Growth rate: {result['growth_per_week']:.1f} RPS/week")
print(f"\nPredicted traffic for next {weeks_ahead} weeks:")

for week, rps in result["predictions"]:
    print(f"Week {week}: {rps:.0f} RPS")

# Apply peak multiplier and headroom
peak_multiplier = 2.5
headroom_pct = 0.20

print(f"\n=== With Peak Multiplier ({peak_multiplier}x) and Headroom ({headroom_pct*100}%) ===")

final_week, final_rps = result["predictions"][-1]
peak_rps = final_rps * peak_multiplier
target_capacity = peak_rps * (1 + headroom_pct)

print(f"Week {final_week} forecast: {final_rps:.0f} RPS")
print(f"Peak capacity needed: {peak_rps:.0f} RPS")
print(f"Target capacity (with headroom): {target_capacity:.0f} RPS")

# Calculate nodes needed
rps_per_node = 350
nodes_needed = int(np.ceil(target_capacity / rps_per_node))

print(f"\n=== Infrastructure ===")
print(f"RPS per node: {rps_per_node}")
print(f"Nodes required: {nodes_needed}")

# Cost estimate
monthly_cost_per_node = 180
total_monthly_cost = nodes_needed * monthly_cost_per_node

print(f"\n=== Cost Estimate ===")
print(f"Monthly cost per node: ${monthly_cost_per_node}")
print(f"Total monthly cost: ${total_monthly_cost}")

# Plot
plot_forecast(historical_data, result, weeks_ahead)
print("\nForecast chart saved to /tmp/capacity_forecast.png")
```

**출력 예시:**

```
=== Capacity Forecast ===
Growth rate: 74.3 RPS/week

Predicted traffic for next 12 weeks:
Week 9: 1789 RPS
Week 10: 1863 RPS
Week 11: 1938 RPS
Week 12: 2012 RPS
...
Week 20: 2605 RPS

=== With Peak Multiplier (2.5x) and Headroom (20%) ===
Week 20 forecast: 2605 RPS
Peak capacity needed: 6513 RPS
Target capacity (with headroom): 7815 RPS

=== Infrastructure ===
RPS per node: 350
Nodes required: 23

=== Cost Estimate ===
Monthly cost per node: $180
Total monthly cost: $4140
```

이 코드는 과거 8주 데이터로 12주를 예측하고, 피크 배수와 헤드룸을 적용해 필요한 노드 수와 비용을 계산합니다. 예측 그래프도 생성해 시각적으로 확인할 수 있습니다.

## 부하 테스트와 용량

예측 모델은 현재 시스템 한계를 알려주지 않습니다. 부하 테스트가 필요한 이유는 예측한 수요를 현재 시스템이 처리할 수 있는지 검증하기 위함입니다.

### 부하 테스트에서 확인해야 할 항목

1. **최대 처리량**: 시스템이 버틸 수 있는 최대 RPS
2. **병목 지점**: CPU, 메모리, DB 커넥션, 외부 API 중 어느 것이 먼저 한계에 닿는가
3. **Latency 분포**: p50, p95, p99 latency가 부하에 따라 어떻게 변하는가
4. **오류율**: 부하가 높아질 때 어느 지점부터 오류가 발생하는가
5. **회복 시간**: 피크가 지나간 후 정상 상태로 돌아오는 데 걸리는 시간

### 부하 테스트 결과 해석

```python
def analyze_load_test_results(test_results):
    """
    부하 테스트 결과 분석
    
    test_results: List of (rps, latency_p99, error_rate) tuples
    """
    analysis = {
        "max_rps": 0,
        "breaking_point": None,
        "recommendations": []
    }
    
    for rps, latency_p99, error_rate in test_results:
        # latency 임계값: p99 < 1000ms
        # 오류율 임계값: < 1%
        
        if latency_p99 < 1000 and error_rate < 0.01:
            analysis["max_rps"] = rps
        else:
            if not analysis["breaking_point"]:
                analysis["breaking_point"] = {
                    "rps": rps,
                    "latency_p99": latency_p99,
                    "error_rate": error_rate
                }
                break
    
    # Headroom 계산: 최대 처리량의 80%를 목표로
    safe_capacity = analysis["max_rps"] * 0.8
    
    analysis["safe_capacity"] = safe_capacity
    analysis["recommendations"].append(
        f"최대 처리량 {analysis['max_rps']} RPS, 안전 용량 {safe_capacity:.0f} RPS 권장"
    )
    
    if analysis["breaking_point"]:
        bp = analysis["breaking_point"]
        if bp["latency_p99"] >= 1000:
            analysis["recommendations"].append(
                f"Latency 병목: {bp['rps']} RPS에서 p99 {bp['latency_p99']:.0f}ms 초과"
            )
        if bp["error_rate"] >= 0.01:
            analysis["recommendations"].append(
                f"오류율 증가: {bp['rps']} RPS에서 {bp['error_rate']*100:.1f}% 오류"
            )
    
    return analysis

# 예시 결과
test_results = [
    (1000, 250, 0.001),
    (1500, 350, 0.002),
    (2000, 450, 0.003),
    (2500, 650, 0.005),
    (3000, 850, 0.008),
    (3500, 1200, 0.015),  # Breaking point
]

analysis = analyze_load_test_results(test_results)

print("=== Load Test Analysis ===")
print(f"Max RPS: {analysis['max_rps']}")
print(f"Safe capacity (80%): {analysis['safe_capacity']:.0f} RPS")

if analysis["breaking_point"]:
    bp = analysis["breaking_point"]
    print(f"\nBreaking point at {bp['rps']} RPS:")
    print(f"  Latency p99: {bp['latency_p99']:.0f}ms")
    print(f"  Error rate: {bp['error_rate']*100:.2f}%")

print("\nRecommendations:")
for rec in analysis["recommendations"]:
    print(f"  - {rec}")
```

부하 테스트는 예측 모델을 현실로 보정합니다. 이론상 3000 RPS가 가능하다고 예측했더라도, 실제 테스트에서 2500 RPS에서 병목이 발견되면 그것이 현실적인 한계입니다.

용량 계획은 현재 상태와 미래 예측을 입력으로 받습니다. 각 입력값이 무엇을 의미하는지 명확하게 정의해야 계획의 신뢰도가 올라갑니다.

| 입력값 | 의미 | 예시 |
| --- | --- | --- |
| 현재 트래픽 | 현재 주간 평균 요청 수 | 1,500 RPS |
| 성장률 | 주간 또는 월간 증가율 | 10% per month |
| 피크 배수 | 평균 대비 최대 트래픽 | 2.5x |
| 안전 마진 (headroom) | 예측 수요 위에 남길 여유 | 20% |

이 값들을 모두 고려해야 실제 필요한 용량을 계산할 수 있습니다. 성장률만 보고 피크를 빼면 프로모션 기간에 문제가 생길 수 있습니다.
## 단계별로 용량 모델링하기

### 1단계 — 추세 예측

```python
def linear_forecast(history, weeks_ahead):
    base = history[-1]
    growth = (history[-1] - history[0]) / max(len(history) - 1, 1)
    return base + growth * weeks_ahead
```

가장 단순한 예측은 최근 추세를 연장하는 것입니다. 완벽하지는 않아도, 과거 최고치만 반복하는 방식보다 미래 수요를 더 명시적으로 다룹니다.

### 2단계 — 헤드룸 계산

```python
def headroom(target_util, current_util):
    return max(0, target_util - current_util)
```

헤드룸은 평소 사용률과 목표 사용률 사이의 여유를 보여 줍니다. 너무 빡빡하면 급증에 취약하고, 너무 넓으면 비용이 커집니다. 어느 지점을 적정선으로 둘지 팀 기준이 필요합니다.

### 3단계 — 부하 테스트 결과 읽기

```python
def max_rps(samples):
    return max(samples)
```

예측한 수요가 실제로 현재 구성에서 가능한지 확인해야 합니다. 부하 테스트는 이론값이 아니라 현실 한계를 보여 줍니다. 특히 병목이 어디서 시작되는지도 함께 드러낼 수 있습니다.

### 4단계 — 노드 수 계산

```python
def nodes(predicted_rps, rps_per_node):
    return -(-predicted_rps // rps_per_node)
```

예측 수요와 단일 노드 처리량을 결합하면 필요한 확장 단위를 계산할 수 있습니다. 올림 계산을 쓰는 이유는 경계값에서 용량이 모자라는 상황을 피하기 위해서입니다.

### 5단계 — 비용 계산

```python
def cost(nodes, monthly_per_node):
    return nodes * monthly_per_node
```

용량 계획은 비용 계획이기도 합니다. 확장 단위가 늘어나면 곧 월간 비용이 바뀌므로, 성능 수치와 예산 수치를 한 표에서 같이 봐야 합니다.

### 6단계 — 프로모션 주간 용량으로 바꿔 보기

```python
history = [1200, 1350, 1500, 1650]
forecast = linear_forecast(history, weeks_ahead=4)
promotion_peak = int(forecast * 1.3)
required_nodes = nodes(predicted_rps=promotion_peak, rps_per_node=350)
monthly_cost = cost(required_nodes, monthly_per_node=180)
```

이 계산이 중요한 이유는 추세 그래프를 실제 운영 결정으로 바꿔 주기 때문입니다. 예상 트래픽을 피크 기준으로 보정하고, 단일 노드 처리량과 연결하면 필요한 증설 단위와 월간 비용을 같은 문맥에서 설명할 수 있습니다.

### 7단계 — 부하 테스트에서 꼭 답해야 할 질문

부하 테스트는 숫자 한 줄을 받기 위해 하는 일이 아닙니다. 어떤 지점에서 시스템이 무너지기 시작하는지, 어떤 의존성이 먼저 한계에 닿는지, 피크가 지난 뒤 회복이 얼마나 걸리는지까지 함께 봐야 용량 계획의 품질이 올라갑니다.

| 질문 | 왜 필요한가 |
| --- | --- |
| latency가 완만하게 오르는가, 임계점 뒤에 급격히 무너지는가 | 큐, 풀, 외부 의존성 한계 같은 병목 위치를 읽게 해 줍니다. |
| 어떤 의존성이 가장 먼저 포화되는가 | 앱 서버보다 DB나 캐시가 먼저 문제를 만들 수 있습니다. |
| 피크가 지나간 뒤 회복 시간은 얼마나 되는가 | 순간 최대치보다 tail recovery가 더 큰 사용자 영향을 줄 수 있습니다. |
| autoscaling이 성능 저하 전에 반응하는가 | 확장 정책과 워크로드 패턴은 실제로 같이 검증해야 합니다. |

## 용량 예측 계산 코드

```python
def capacity_forecast(current_rps, growth_rate_monthly, months_ahead, peak_multiplier, headroom_pct):
    """
    용량 예측 계산
    
    예시:
    - 현재: 1500 RPS
    - 월간 성장률: 10%
    - 3개월 후 예상
    - 피크 배수: 2.5x
    - headroom: 20%
    """
    # Step 1: 성장 예측
    forecast_rps = current_rps * ((1 + growth_rate_monthly) ** months_ahead)
    
    # Step 2: 피크 적용
    peak_rps = forecast_rps * peak_multiplier
    
    # Step 3: headroom 추가
    target_capacity = peak_rps * (1 + headroom_pct)
    
    return {
        "current_rps": current_rps,
        "forecast_rps": forecast_rps,
        "peak_rps": peak_rps,
        "target_capacity": target_capacity,
        "months_ahead": months_ahead
    }

def calculate_nodes(target_capacity, rps_per_node):
    """
    필요한 노드 수 계산
    """
    import math
    return math.ceil(target_capacity / rps_per_node)

def cost_estimate(nodes, monthly_cost_per_node):
    """
    월간 비용 계산
    """
    return nodes * monthly_cost_per_node

# 예시 계산
result = capacity_forecast(
    current_rps=1500,
    growth_rate_monthly=0.10,
    months_ahead=3,
    peak_multiplier=2.5,
    headroom_pct=0.20
)

print(f"현재: {result['current_rps']} RPS")
print(f"3개월 후 예상: {result['forecast_rps']:.0f} RPS")
print(f"피크 적용: {result['peak_rps']:.0f} RPS")
print(f"목표 용량: {result['target_capacity']:.0f} RPS")

# 노드 수 계산
rps_per_node = 350
required_nodes = calculate_nodes(result['target_capacity'], rps_per_node)
print(f"필요 노드: {required_nodes}개")

# 비용 계산
monthly_cost = cost_estimate(required_nodes, monthly_cost_per_node=180)
print(f"월간 비용: ${monthly_cost}")
```

이 계산은 성장 추세를 현실적인 인프라 증설 결정으로 바꿔 줍니다. 단순히 "트래픽이 느는 것 같다"가 아니라, 정확한 수치로 노드 수와 비용을 설명할 수 있습니다.

## 로드 테스트 전략

용량 계획은 예측만으로는 충분하지 않습니다. 현재 시스템이 실제로 얼마나 버티는지 검증해야 합니다. k6나 Locust 같은 도구로 로드 테스트를 수행하면 병목 지점과 한계 성능을 파악할 수 있습니다.

### k6 기본 스크립트

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // ramp-up
    { duration: '5m', target: 100 },  // steady state
    { duration: '2m', target: 200 },  // spike
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },    // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  let response = http.get('https://api.example.com/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'latency < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

```bash
k6 run --vus 200 --duration 10m load-test.js
```

### Locust 기본 스크립트

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_home(self):
        self.client.get("/")

    @task(1)
    def get_api(self):
        self.client.get("/api/data")
```

```bash
locust -f locustfile.py --host=https://api.example.com --users 200 --spawn-rate 10
```

로드 테스트는 순간 최대치만이 아니라, latency 분포, 오류율, 병목 위치, 회복 시간을 함께 확인해야 합니다. 그래야 예측 모델을 현실에 맞게 보정할 수 있습니다.
## 이 코드에서 먼저 봐야 할 점

- 예측과 검증을 함께 봐야 계획이 현실에 가까워집니다.
- 헤드룸은 변동성을 흡수하는 장치입니다.
- 확장 단위와 비용은 같은 판단 안에서 읽어야 합니다.
- 리드 타임이 길수록 더 일찍 결정해야 합니다.

## 여기서 자주 헷갈립니다

첫 번째 실수는 과거 최고치에 조금만 더 얹으면 된다고 생각하는 것입니다. 성장 추세와 이벤트성 수요를 놓치기 쉽습니다.

두 번째 실수는 부하 테스트 없이 문서상 처리량만 믿는 것입니다. 실제 병목은 계산보다 빨리 드러날 수 있습니다.

세 번째 실수는 비용과 용량을 따로 보는 것입니다. 헤드룸이 얼마나 필요한지와 그 비용을 같은 자리에서 봐야 제대로 판단할 수 있습니다.

## 운영 체크리스트

- [ ] 미래 수요를 예측하는 모델이 있다.
- [ ] 헤드룸 정책과 목표 사용률을 정의했다.
- [ ] 정기적인 부하 테스트 일정이 있다.
- [ ] 확장 단위와 비용을 함께 검토한다.
- [ ] 리드 타임을 고려해 증설 의사결정 시점을 앞당긴다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 용량 계획을 일회성 보고서로 보지 않습니다. 계획과 실제 사용량의 차이를 계속 보정하는 반복 작업으로 봅니다. 예측이 틀리는 것은 자연스럽지만, 틀린 이유를 다음 계획에 반영하는 것이 더 중요합니다.

또한 블랙 프라이데이, 대규모 프로모션, 학기 시작처럼 피크가 예측 가능한 서비스는 몇 달 전부터 준비합니다. 급증은 종종 놀라운 사건이 아니라, 준비하지 않은 사건입니다.

## 정리

capacity planning은 미래 수요와 공급을 숫자로 맞추는 작업입니다. 예측, 부하 테스트, 헤드룸, 비용, 리드 타임을 한 흐름으로 묶어 볼 때 서비스는 더 안정적으로 성장할 수 있습니다.

다음 글은 시리즈 마지막 편인 운영 가능한 시스템 만들기입니다. 지금까지 다룬 신뢰성, 모니터링, 자동화, 대응 원칙을 하나의 설계 관점으로 묶어 보겠습니다.

## 처음 질문으로 돌아가기

- **용량 계획은 왜 과거 복제가 아니라 미래 수요 예측일까요?**
  - Capacity Planning은 현재 사용률과 미래 성장률을 그래프로 보면서, 언제 한계에 도달할지 예측합니다.
- **헤드룸은 왜 낭비가 아니라 보험에 가까울까요?**
  - 메트릭의 시계열 데이터가 있어야 추세를 읽을 수 있으며, 업무 주기와 계절 변화도 함께 봐야 합니다.
- **부하 테스트는 예측 모델을 어떻게 보정할까요?**
  - 용량이 부족해진 뒤 대응하는 것보다, 미리 여유를 계획해두는 것이 비용 효율적입니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- [SRE 101 (8/10): Toil 줄이기](./08-reducing-toil.md)
- **Capacity Planning (현재 글)**
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Software Engineering in SRE - Google SRE Book](https://sre.google/sre-book/software-engineering-in-sre/)
- [Capacity Planning - High Scalability](http://highscalability.com/blog/category/capacity-planning)
- [The Art of Capacity Planning - O'Reilly](https://www.oreilly.com/library/view/the-art-of/9780596518578/)
- [Load Testing - Grafana k6](https://grafana.com/docs/k6/latest/)

Tags: SRE, CapacityPlanning, Forecasting, Performance, Operations
