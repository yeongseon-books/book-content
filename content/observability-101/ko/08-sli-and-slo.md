---
series: observability-101
episode: 8
title: "Observability 101 (8/10): 서비스 수준 지표와 목표 기초"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Observability
  - SLO
  - SLI
  - SRE
  - Reliability
seo_description: SLI, SLO, 오류 예산으로 신뢰성을 감각이 아닌 숫자로 다루는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (8/10): 서비스 수준 지표와 목표 기초

"서비스가 안정적인가"라는 질문은 의외로 자주 감정 싸움이 됩니다. 어떤 팀은 충분히 괜찮다고 말하고, 어떤 팀은 이미 위험하다고 말합니다. 서로 다른 감각만 들고 있으면 배포와 기능 추가, 안정화 우선순위가 계속 흔들립니다.

서비스 수준 지표와 목표는 이 문제를 숫자로 바꿉니다. 측정된 신뢰성과 약속한 신뢰성을 분리하고, 얼마만큼의 실패를 허용할지까지 정하면 신뢰성 논의가 훨씬 선명해집니다.

이 글은 Observability 101 시리즈의 8번째 글입니다.

![Observability 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/08/08-01-concept-at-a-glance.ko.png)
*Observability 101 8장 흐름 개요*
> 서비스 수준 지표와 목표 기초의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 먼저 던지는 질문

- 서비스 수준 지표는 무엇을 어떻게 측정할까요?
- 서비스 수준 목표는 어떤 약속을 만들까요?
- 오류 예산은 왜 기능 개발과 안정화의 균형점이 될까요?

## 왜 중요한가

신뢰성 논의가 숫자 없이 진행되면, 모든 결론이 사람의 체감에 기대게 됩니다. 반대로 지표와 목표가 있으면 "이번 달 가용성이 99.87%라 목표를 밑돌았다"처럼 같은 문장을 함께 보게 됩니다. 그러면 배포를 멈출지, 기능 개발을 늦출지, 안정화에 시간을 더 쓸지 판단이 쉬워집니다.

특히 서비스 수준 목표는 엔지니어링과 비즈니스가 공통 언어를 갖게 해 줍니다. 사용자에게 무엇을 약속하는지, 어느 정도 실패는 감수할 수 있는지, 지금 속도로 가면 언제 위험해지는지를 숫자로 말할 수 있게 됩니다.

### SLI 유형

서비스 수준 지표는 여러 가지로 측정할 수 있습니다. 대표적인 네 가지 유형을 보겠습니다.

| SLI 유형 | 측정 방법 | 좋은 임계값 예시 |
|---|---|---|
| 가용성 | (2xx+3xx) / total requests | 99.9% (43.2분/월) |
| 지연 시간 | request duration p95 | 500ms 이하 |
| 처리량 | requests per second (RPS) | 최소 1000 RPS |
| 정확성 | non-error results / total | 99.99% |

가용성은 가장 기본적인 SLI입니다. 5xx 응답이 아닌 요청을 성공으로 보고, 전체 요청으로 나눗니다. 지연 시간은 평균이 아닌 p95나 p99로 측정하는 편이 현실적이고, 처리량은 특정 임계 이상을 유지하는 것으로 정의할 수 있습니다. 정확성은 데이터 파이프라인이나 검색 결과처럼 정확한 결과가 중요한 경우에 정의합니다.
## 한눈에 보는 구조

SLI는 서비스 수준을 측정하는 지표이고, SLO는 팀이 지켜야 할 목표입니다. 에러 버짓으로 변경과 안정성 사이의 균형을 맞춥니다.

## 핵심 용어

- 서비스 수준 지표: 성공률처럼 측정 가능한 비율입니다.
- 서비스 수준 목표: 99.9% 가용성처럼 합의한 목표값입니다.
- 서비스 수준 계약: 위반 시 법적 또는 금전적 책임이 따르는 계약입니다.
- 오류 예산: 목표 안에서 허용한 실패량입니다.
- 소진 속도: 오류 예산을 얼마나 빨리 쓰고 있는지 나타내는 속도입니다.

## 바꾸기 전과 후

바꾸기 전에는 "느리다", "괜찮다" 같은 말이 충돌합니다. 어느 쪽이 맞는지 정리하려면 회의가 길어집니다.

바꾼 뒤에는 "이번 달 가용성 99.92%, 목표 99.9% 통과"처럼 숫자로 말합니다. 논쟁보다 판단이 빨라지고, 기능 개발과 안정화의 우선순위도 훨씬 선명해집니다.

## 실습: 목표 체계를 다섯 단계로 만들기

### 1단계 — 서비스 수준 지표 정의하기

```promql
# Availability SLI = good / total
sli_good = sum(rate(http_requests_total{status!~"5.."}[5m]))
sli_total = sum(rate(http_requests_total[5m]))
sli = sli_good / sli_total
```

서비스 수준 지표는 거의 항상 비율입니다. 정상 요청과 전체 요청을 나누는 식으로, 사용자가 실제로 체감하는 성공률을 측정해야 합니다.

### 2단계 — 목표값 정하기

```text
SLO: 99.9% availability over 30 days
That allows 30 * 24 * 60 * 0.001 = 43.2 minutes/month
```

목표값은 기술적으로 가능한 최대치가 아니라, 조직이 감수할 실패량을 반영한 선택입니다. 99.9%는 숫자이면서 동시에 운영 정책입니다.

### 3단계 — 오류 예산 계산하기

```promql
1 - (sli_good / sli_total)         # current failure rate
# remaining 30-day budget = 0.001 * total - errors
```

오류 예산이 있어야 목표가 살아 움직입니다. 예산이 넉넉하면 더 빠르게 배포할 수 있고, 빠르게 소진되면 안정화에 집중해야 합니다.

### 4단계 — 소진 속도 경보 만들기

```yaml
- alert: FastBurn
  expr: error_rate_5m > 14.4 * 0.001
        and error_rate_1h > 14.4 * 0.001
  for: 2m
  labels: { severity: page }
```

짧은 구간과 긴 구간을 함께 보는 소진 속도 경보는 빠른 사고와 느린 잠식을 동시에 잡는 데 유용합니다. 임계값 하나만 보는 경보보다 훨씬 현실적입니다.

### 5단계 — 월간 보고 만들기

```text
- Availability: 99.92% (target 99.9% PASS)
- Latency: p95 320ms (target <= 500ms PASS)
- Budget burned: 38%
```

월간 보고는 지표를 조직 언어로 바꾸는 자리입니다. 숫자가 있어야 다음 달의 기능 우선순위와 안정화 계획도 설득력을 갖습니다.

### SLO burn-rate 계산 예제

오류 예산 소진 속도를 Python으로 계산하는 예시입니다.

```python
def calculate_burn_rate(actual_error_rate, slo_target, window_hours):
    """
    오류 예산 소진 속도 계산
    actual_error_rate: 현재 오류율 (0.0 - 1.0)
    slo_target: SLO 목표 (0.999 = 99.9%)
    window_hours: 평가 창 시간
    """
    allowed_error_rate = 1.0 - slo_target
    burn_rate = actual_error_rate / allowed_error_rate
    
    # 30일 기준 예산 소진 예측
    hours_in_month = 30 * 24
    budget_hours = hours_in_month * allowed_error_rate
    burned_hours = window_hours * actual_error_rate
    
    return {
        "burn_rate": burn_rate,
        "budget_hours": budget_hours,
        "burned_hours": burned_hours,
        "remaining_hours": budget_hours - burned_hours
    }

# 예시: 99.9% SLO, 현재 1시간 동안 0.5% 오류율
result = calculate_burn_rate(
    actual_error_rate=0.005,
    slo_target=0.999,
    window_hours=1
)
print(f"Burn rate: {result['burn_rate']:.1f}x")
print(f"Budget: {result['budget_hours']:.1f}h")
print(f"Burned: {result['burned_hours']:.3f}h")
print(f"Remaining: {result['remaining_hours']:.1f}h")
```

이 코드는 현재 오류율이 허용 오류율의 몇 배인지 계산합니다. burn rate가 1.0보다 크면 예산을 빠르게 소진하고 있다는 의미입니다.

## 오류 예산을 이렇게 운영합니다

서비스 수준 목표는 문서에 써 두는 것만으로는 힘이 없습니다. 배포 속도와 안정화 우선순위를 실제로 바꾸는지 확인해야 합니다.

```text
30-day SLO target: 99.9%
allowed downtime: 43.2m
this month burned: 31.4m (72.7%)
current burn rate: 2.1x
decision: 신규 배포는 유지, 고위험 변경은 보류
```

이런 보고가 있어야 "지금은 기능을 더 내도 되는가"를 감으로 말하지 않게 됩니다. 소진 속도가 급격히 오르면 경보가 울리고, 월간 보고에서는 남은 예산이 다음 배포 판단 기준이 됩니다.

```text
Expected output:
- 팀이 목표값, 남은 오류 예산, 최근 소진 속도를 같은 숫자로 봅니다.
- burn-rate 경보가 빠른 사고와 느린 악화를 모두 잡습니다.
- 월간 리뷰에서 기능 출시 속도와 안정화 우선순위를 데이터로 조정합니다.
```

### 에러 버짓 정책

에러 버짓은 숫자일 뿐이고, 이를 실제로 운영하려면 정책이 필요합니다. 아래는 실제 팀에서 사용하는 에러 버짓 정책의 예시입니다.

**정책 1: 예산 소진 70% 이하 (녹색 구간)**

- 정상 배포 속도를 유지합니다.
- 신규 기능 개발을 계속합니다.
- 주간 회고에서 예산 소진 현황만 보고합니다.

**정책 2: 예산 소진 70-90% (황색 구간)**

- 고위험 배포는 보류합니다 (예: 데이터베이스 스키마 변경).
- 기존 기능의 안정성 개선을 우선순위에 올립니다.
- 주간 회고에서 주요 장애 원인을 분석합니다.

**정책 3: 예산 소진 90% 초과 (빨간색 구간)**

- 모든 신규 기능 배포를 중단합니다.
- 안정화 태스크포스를 구성하고 집중합니다.
- 경영진에게 상황을 에스커레이션합니다.
- 예산이 70% 이하로 내려올 때까지 정책을 유지합니다.

이 정책은 숫자를 행동으로 바꾸는 핵심입니다. 예산이 없으면 기능 개발을 멈춘다는 규칙이 명확하면 개발 팀과 비즈니스 팀 모두 같은 기준으로 말하게 됩니다.

### SLA와의 차이점

실무에서는 SLI, SLO, SLA를 혼용하는 경우가 많습니다. 세 개는 명확히 다른 역할을 합니다.

**SLI (Service Level Indicator)**
측정 가능한 지표입니다. 성공률, 지연 시간, 처리량처럼 숫자로 정확하게 표현할 수 있어야 합니다. 예: `가용성 = (성공 요청 / 전체 요청) * 100%`

**SLO (Service Level Objective)**
팀이 지키기로 합의한 목표값입니다. 예: `가용성 99.9% 이상 유지`. 목표를 맞추지 못하더라도 법적 체벌은 없지만, 팀 내부 운영 기준이 됩니다.

**SLA (Service Level Agreement)**
고객과 맺은 계약입니다. 예: `가용성 99.9% 미달 시 서비스 요금 10% 환불`. SLA는 위반 시 금전적 또는 법적 책임이 따르므로 SLO보다 보수적으로 설정하는 편입니다.

일반적으로 SLO를 99.9%로 잡았다면 SLA는 99.5% 정도로 여유를 두는 것이 현명합니다. 내부 목표를 맞추지 못하더라도 고객과의 약속은 지킬 수 있는 보호 구간을 만들기 때문입니다.

### 다중 SLO 우선순위

하나의 서비스에 여러 SLO를 정하는 경우 우선순위를 명확히 해야 합니다. 모든 SLO를 동일한 비중으로 취급하면 어떤 것이 먼저 깨져도 괜찮은지 판단이 흔들립니다.

```python
slo_priority = {
    "availability": {
        "target": 0.999,
        "weight": 1.0,  # 최고 우선순위
        "action": "모든 배포 중단"
    },
    "latency_p95": {
        "target": 500,  # ms
        "weight": 0.8,
        "action": "성능 튜닝 우선"
    },
    "latency_p99": {
        "target": 1000,  # ms
        "weight": 0.6,
        "action": "긴 꼬리 최적화"
    }
}

def check_slo_breach(metrics, slo_priority):
    breached = []
    for name, config in sorted(
        slo_priority.items(),
        key=lambda x: x[1]["weight"],
        reverse=True
    ):
        if metrics[name] < config["target"]:
            breached.append((name, config))
    
    if breached:
        top = breached[0]
        print(f"Critical SLO breach: {top[0]}")
        print(f"Action required: {top[1]['action']}")
```

우선순위가 있으면 여러 SLO가 동시에 깨졌을 때 어느 것부터 복구할지 명확해집니다.

## 이 코드에서 먼저 봐야 할 점

- 서비스 수준 지표는 비율이어야 합니다.
- 소진 속도는 짧은 구간과 긴 구간을 함께 봐야 합니다.
- 오류 예산이 남아 있느냐가 배포 속도의 기준이 됩니다.

## 자주 하는 실수 다섯 가지

1. 목표를 100%로 잡습니다. 현실적으로 유지하기 어렵습니다.
2. 내부 지표를 그대로 서비스 수준 지표로 씁니다. 사용자 경험과 멀어집니다.
3. 임계값만 보고 소진 속도 경보를 만들지 않습니다. 느린 악화를 놓치기 쉽습니다.
4. 오류 예산을 기능 우선순위에 반영하지 않습니다. 목표가 장식으로 남습니다.
5. 목표를 너무 많이 잡아 한꺼번에 깨지게 만듭니다. 우선순위가 흐려집니다.

## 실무에서는 이렇게 생각한다

대부분의 팀은 가용성과 지연 시간을 첫 목표로 삼습니다. 사용자에게 직접 보이는 품질부터 수치로 약속해야 하기 때문입니다. 내부 큐 길이나 CPU 사용률은 보조 지표일 수 있지만, 서비스 수준 지표의 중심이 되기에는 부족한 경우가 많습니다.

시니어 엔지니어는 오류 예산을 일정 관리 도구로도 씁니다. 예산이 충분하면 기능 출시를 밀고, 빠르게 소진되면 안정화와 리팩터링을 우선합니다. 숫자가 우선순위를 정하게 만드는 것이 핵심입니다.

## 체크리스트

- [ ] 서비스 수준 지표를 하나 이상 정의했습니다.
- [ ] 서비스 수준 목표를 팀과 합의했습니다.
- [ ] 오류 예산을 계산할 수 있습니다.
- [ ] 소진 속도 경보가 하나 이상 있습니다.

## 연습 문제

1. 하나의 서비스에 대한 가용성 지표를 PromQL로 작성해 보세요.
2. 99.9% 목표의 월간 오류 예산 시간을 직접 계산해 보세요.
3. 빠른 소진과 느린 소진을 함께 잡는 경보 짝을 설계해 보세요.

## SLI 계산 코드 예시

지표 정의가 문서에만 있으면 운영 중 해석이 갈리기 쉽습니다. 아래처럼 계산 로직을 코드로 명시하면 팀 내 합의가 유지됩니다.

```python
from dataclasses import dataclass

@dataclass
class SLIResult:
    good: int
    total: int

    @property
    def value(self) -> float:
        return 0.0 if self.total == 0 else self.good / self.total

def availability_sli(status_codes: list[int]) -> SLIResult:
    total = len(status_codes)
    good = sum(1 for code in status_codes if 200 <= code < 500)
    return SLIResult(good=good, total=total)

samples = [200, 200, 201, 502, 503, 200, 429, 200]
result = availability_sli(samples)
print(f"SLI={result.value:.4f} ({result.good}/{result.total})")
```

여기서 성공 기준을 어떻게 둘지는 서비스 성격에 따라 달라집니다. 예를 들어 인증 시스템에서는 401을 정상 응답으로 볼 수 있고, 결제 API에서는 일부 4xx를 실패로 분류해야 할 수도 있습니다. 핵심은 기준을 명문화하고 변경 이력을 남기는 것입니다.

## 오류 예산 소진 공식 정리

운영에서 가장 많이 쓰는 공식은 아래 두 가지입니다.

```text
allowed_error_rate = 1 - slo_target
burn_rate = actual_error_rate / allowed_error_rate
```

예를 들어 SLO 99.9%라면 허용 오류율은 0.1%(0.001)입니다. 실제 오류율이 0.5%(0.005)라면 burn rate는 5.0입니다. 즉, 예산을 허용 속도보다 다섯 배 빠르게 소모하고 있다는 의미입니다. 이 수치를 이용하면 장애 심각도를 절대값이 아닌 상대 속도로 해석할 수 있습니다.

## 다중 윈도우 경보 템플릿

짧은 창과 긴 창을 함께 쓰는 이유는 순간 급등과 느린 악화를 동시에 잡기 위해서입니다.

```yaml
groups:
  - name: slo-burn
    rules:
      - alert: SLOFastBurn
        expr: (error_rate_5m > 14.4 * 0.001) and (error_rate_1h > 14.4 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "SLO fast burn detected"

      - alert: SLOSlowBurn
        expr: (error_rate_30m > 6 * 0.001) and (error_rate_6h > 6 * 0.001)
        for: 15m
        labels:
          severity: ticket
        annotations:
          summary: "SLO slow burn detected"
```

Fast burn은 즉시 대응을, slow burn은 계획된 안정화를 유도합니다. 둘을 분리하지 않으면 팀은 항상 과잉 대응하거나 항상 늦게 대응하게 됩니다.

### SLO 대시보드 Grafana JSON 예시

SLO 현황을 한눈에 보여주는 대시보드 패널 설정입니다.

```json
{
  "title": "SLO Status — checkout-service",
  "type": "stat",
  "datasource": "Prometheus",
  "targets": [
    {
      "expr": "1 - (sum(rate(http_requests_total{service=\"checkout\", code=~\"5..\"}[30d])) / sum(rate(http_requests_total{service=\"checkout\"}[30d])))",
      "legendFormat": "Availability (30d)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "steps": [
          { "value": 0, "color": "red" },
          { "value": 0.995, "color": "yellow" },
          { "value": 0.999, "color": "green" }
        ]
      },
      "unit": "percentunit",
      "decimals": 4
    }
  }
}
```

이 패널은 30일 rolling window 기준 가용성을 퍼센트로 표시합니다. 임계값에 따라 색상이 바뀌므로 현재 SLO 상태를 직관적으로 파악할 수 있습니다.

에러 버짓 소진률 패널도 함께 배치합니다.

```json
{
  "title": "Error Budget Remaining",
  "type": "gauge",
  "datasource": "Prometheus",
  "targets": [
    {
      "expr": "1 - (sum(increase(http_requests_total{service=\"checkout\", code=~\"5..\"}[30d])) / (sum(increase(http_requests_total{service=\"checkout\"}[30d])) * 0.001))",
      "legendFormat": "Budget Remaining"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "min": 0,
      "max": 1,
      "thresholds": {
        "steps": [
          { "value": 0, "color": "red" },
          { "value": 0.25, "color": "orange" },
          { "value": 0.5, "color": "green" }
        ]
      },
      "unit": "percentunit"
    }
  }
}
```

버짓이 25% 미만이면 주황색, 0%면 빨간색으로 전환됩니다. 이 시점에서 기능 배포를 동결하고 안정화에 집중해야 합니다.

### 에러 버짓 시나리오 분석

월간 요청량이 1,000만 건이고 SLO가 99.9%인 서비스를 기준으로 에러 버짓 시나리오를 살펴봅니다.

| 시나리오 | 월간 허용 실패 | 1회 장애 소진량 | 남은 버짓 | 조치 |
|---------|--------------|---------------|----------|------|
| 정상 운영 | 10,000건 | 0건 | 100% | 기능 배포 허용 |
| 5분 전면 장애 (100 RPS) | 10,000건 | 30,000건 | -200% | 즉시 동결 + RCA |
| 1시간 부분 장애 (10% 에러) | 10,000건 | 3,600건 | 64% | 주의 관찰 |
| 하루 간헐적 장애 (0.5% 에러) | 10,000건 | 4,320건 | 56.8% | 원인 분석 착수 |
| 주간 느린 열화 (0.1% 에러) | 10,000건 | 6,048건 | 39.5% | 다음 스프린트 우선 |

이 표에서 핵심은 짧은 전면 장애보다 긴 부분 장애가 더 많은 버짓을 소진할 수 있다는 점입니다. 5분 전면 장애는 극적이지만, 하루 종일 0.5% 에러가 지속되면 전체 버짓의 43%를 소모합니다.

### SLO 도입 로드맵

조직에 SLO를 처음 도입할 때 단계별로 접근해야 합니다. 한 번에 모든 서비스에 적용하면 측정 부담과 정치적 저항이 커집니다.

**1단계 — 측정 기반 구축 (2-4주)**

```yaml
actions:
  - 핵심 서비스 3개 선정
  - RED 메트릭 수집 파이프라인 구축
  - 현재 실제 성능 baseline 측정 (2주간)
  - SLI 정의서 작성 (서비스별 1페이지)
deliverables:
  - SLI 정의서
  - Prometheus recording rules
  - Grafana baseline 대시보드
```

**2단계 — SLO 설정과 관찰 (4-6주)**

```yaml
actions:
  - baseline 기반으로 SLO 목표 설정 (현실적 수준)
  - 에러 버짓 계산 자동화
  - burn rate alert 설정 (silent mode)
  - 주간 SLO 리뷰 미팅 시작
deliverables:
  - SLO 문서 (목표 + 근거)
  - burn rate alert rule (무음 관찰)
  - 주간 리뷰 템플릿
```

**3단계 — 운영 통합 (4-8주)**

```yaml
actions:
  - alert를 실제 온콜로 연결
  - 에러 버짓 정책 공식화 (동결 기준, 해제 기준)
  - 스프린트 계획에 SLO 상태 반영
  - 경영진 리포트에 SLO 추가
deliverables:
  - 에러 버짓 정책 문서
  - 온콜 런북 SLO 섹션
  - 월간 신뢰성 리포트
```

**4단계 — 확장과 성숙 (지속)**

```yaml
actions:
  - 나머지 서비스로 확대 (분기별 3-5개)
  - SLO 기반 용량 계획 도입
  - 내부 SLA와 SLO 연계
  - 자동 에러 버짓 동결/해제 파이프라인
deliverables:
  - 서비스 카탈로그에 SLO 상태 통합
  - 자동화된 동결/해제 워크플로
```

각 단계에서 가장 중요한 것은 팀이 SLO를 의사결정 도구로 사용하는 습관을 만드는 것입니다. 숫자를 만드는 것보다 숫자를 보고 행동하는 문화가 먼저입니다.

## 정리

서비스 수준 지표와 목표는 신뢰성을 감정이 아니라 숫자로 다루게 해 줍니다. 측정된 값, 약속한 값, 허용한 실패량이 분리되면 운영 우선순위가 선명해집니다. 다음 글에서는 이 모든 관측성을 오래 운영하기 위해 반드시 알아야 할 비용과 카디널리티를 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **서비스 수준 지표는 무엇을 어떻게 측정할까요?**
  - SLI는 사용자 경험의 수치화입니다. 가용성은 성공 응답 비율, 지연은 p99 응답 시간, 정확성은 올바른 결과 비율로 측정합니다. 본문의 Prometheus recording rule처럼 원시 메트릭을 비율로 집계해야 의미 있는 지표가 됩니다.
- **서비스 수준 목표는 어떤 약속을 만들까요?**
  - SLO는 "30일 rolling window에서 가용성 99.9% 이상"처럼 측정 가능한 내부 약속입니다. 이 약속은 에러 버짓이라는 구체적 숫자로 변환되어, 팀이 기능 배포와 안정화 사이에서 데이터 기반 의사결정을 내릴 수 있게 합니다.
- **오류 예산은 왜 기능 개발과 안정화의 균형점이 될까요?**
  - 시나리오 분석에서 보았듯이, 월 1,000만 요청 서비스의 99.9% SLO는 10,000건의 실패 허용량을 만듭니다. 이 숫자가 남아 있으면 배포하고, 소진되면 동결합니다. 감이 아닌 숫자가 결정하므로 개발팀과 운영팀의 갈등이 줄어듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- [Observability 101 (4/10): 구조화된 로깅](./04-structured-logging.md)
- [Observability 101 (5/10): 분산 트레이싱 기초](./05-distributed-tracing.md)
- [Observability 101 (6/10): 대시보드 설계](./06-dashboard-design.md)
- [Observability 101 (7/10): 경보와 온콜](./07-alert-and-oncall.md)
- **서비스 수준 지표와 목표 기초 (현재 글)**
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Google SRE — SLO chapter](https://sre.google/sre-book/service-level-objectives/)
- [The SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Multi-window burn rate](https://sre.google/workbook/alerting-on-slos/)
- [Sloth — SLO generator](https://sloth.dev/)
- [Google Cloud — Service monitoring SLO overview](https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring)
- [book-examples — observability-101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

Tags: Observability, SLO, SLI, SRE, Reliability
