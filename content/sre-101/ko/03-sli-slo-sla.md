---
series: sre-101
episode: 3
title: "SRE 101 (3/10): SLI, SLO, SLA"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - SRE
  - SLI
  - SLO
  - SLA
  - Reliability
seo_description: SLI, SLO, SLA의 차이와 문서화 방법을 입문자 관점에서 정리합니다
last_reviewed: '2026-05-14'
---

# SRE 101 (3/10): SLI, SLO, SLA

신뢰성 이야기를 시작하면 거의 반드시 세 약어가 따라옵니다. SLI, SLO, SLA입니다. 셋 다 숫자와 관련 있고 이름도 비슷해서, 실무에서도 섞여 쓰이는 경우가 적지 않습니다.

문제는 이 셋을 섞어 쓰는 순간부터 목표와 약속의 경계가 무너진다는 사실입니다. 무엇을 재는지, 어디까지를 내부 기준으로 삼는지, 외부에 무엇을 약속하는지를 분리하지 않으면 운영도 계약도 불안해집니다.

이 글은 SRE 101 시리즈의 3번째 글입니다. 여기서는 SLI, SLO, SLA를 측정, 목표, 약속의 순서로 구분하고, 각 문서에 무엇이 빠지면 안 되는지 정리합니다.


![SRE 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/03/03-01-concept-at-a-glance.ko.png)
*SRE 101 3장 흐름 개요*
> SLI는 무엇을 측정할지 정하고, SLO는 그 지표의 목표치와 오너를 명시하며, SLA는 외부 약속으로 보상과 예외를 포함합니다.

## 먼저 던지는 질문

- SLI, SLO, SLA는 각각 어떤 역할을 맡고 어디서 경계가 갈릴까요?
- 내부 목표와 외부 약속은 왜 같은 문서가 아니어야 할까요?
- 좋은 SLO에는 목표 수치 외에 어떤 정보가 반드시 들어가야 할까요?

## 왜 이 주제가 중요한가

셋을 구분하지 않으면 팀 대화가 금방 흐려집니다. 운영팀은 “99.9%를 지키고 있다”고 말하는데, 제품팀은 그 숫자가 무엇을 기준으로 한 것인지 모르고, 영업팀은 그 수치를 외부 약속처럼 전달해 버릴 수 있습니다. 이 상태가 오래가면 분쟁은 늘고 개선은 느려집니다.

반대로 SLI, SLO, SLA를 분리해 두면 역할이 선명해집니다. SLI는 관찰 도구이고, SLO는 내부 운영 기준이며, SLA는 외부 약속입니다. 이 순서를 잡아 두면 숫자가 많아져도 구조는 오히려 단순해집니다.

## 한 문장으로 잡는 멘탈 모델

> SLI는 무엇을 재는지, SLO는 어디까지를 목표로 삼는지, SLA는 그중 무엇을 외부에 약속하는지 정리한 층위입니다.

## 한눈에 보는 구조

이 흐름을 머릿속에 넣어 두면 문서 구조가 바로 정리됩니다. 먼저 측정 대상을 정하고, 그다음 내부 목표를 세우고, 마지막으로 외부 약속이 필요하면 별도 합의를 문서화합니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 빠지면 생기는 문제 |
| --- | --- | --- |
| SLI | 서비스 수준을 재는 지표 | 무엇을 측정하는지 불분명해집니다 |
| SLO | 내부 운영 목표 | 출시와 안정성 판단 기준이 없어집니다 |
| SLA | 외부 고객과의 서비스 수준 약속 | 약속 위반 시 책임 범위가 모호해집니다 |
| window | 지표를 평가하는 기간 | 같은 숫자도 다르게 해석됩니다 |
| threshold | 목표 수치 또는 허용 한계 | 위반 여부 판단이 흔들립니다 |

## 셋을 같은 층위에 놓으면 왜 위험할까

예를 들어 누군가 “우리 서비스는 99.9%를 보장합니다”라고 말했다고 해 보겠습니다. 여기에는 적어도 네 가지 빈칸이 있습니다. 무엇을 99.9%로 보는지, 어떤 기간 동안 재는지, 누가 이 목표를 책임지는지, 지키지 못했을 때 어떤 일이 생기는지입니다.

SLI, SLO, SLA는 이 빈칸을 메우는 역할을 나눕니다. SLI는 측정 공식을 명확히 하고, SLO는 목표와 오너를 정하고, SLA는 보상과 예외까지 포함한 약속을 남깁니다. 이 분리가 없으면 숫자는 있어도 운영은 여전히 모호합니다.

## SLI/SLO/SLA 관계 표

SLI, SLO, SLA의 차이를 명확히 하려면 다음 표가 도움이 됩니다.

| 항목 | SLI | SLO | SLA |
| --- | --- | --- | --- |
| **정의** | 서비스 수준을 측정하는 지표 | 내부 운영 목표 | 외부 고객과의 약속 |
| **소유자** | 플랫폼/운영팀 | 제품/SRE팀 | 법무/영업팀 |
| **예시** | `http_2xx / http_total` | 30일간 99.9% 가용성 | 99.5% 위반 시 10% 크레딧 |
| **위반 시 결과** | 대시보드 주황색 | 배포 freeze, 리뷰 강화 | 보상 지급, 계약 해지 위험 |

이 표를 보면 SLO는 팀 내부 기준이고, SLA는 외부 약속이라는 점이 명확해집니다. SLO를 SLA로 착각하면 부담을 느끼거나, SLA를 SLO처럼 느슨하게 관리하면 법적 분쟁이 생깁니다.

## SLO 위반 시 에러 버짓 소진 예시

에러 버짓이란 SLO에서 허용한 실패 범위를 뜻합니다. 예를 들어 30일간 99.9% 가용성을 목표로 하면, 0.1%만큼 실패를 감당할 수 있습니다. 이 실패 한도를 에러 버짓이라고 부릅니다.

```python
def error_budget(total_requests, target_availability):
    allowed_errors = total_requests * (1 - target_availability)
    return allowed_errors

# 30일간 총 100만 요청 예상, 99.9% 목표
print(error_budget(1_000_000, 0.999))  # 1000개 실패까지 허용
```

에러 버짓이 남아 있으면 새 기능을 배포하거나 리팩토링을 진행할 수 있습니다. 버짓을 다 소진하면 배포를 멈추고 안정화에 집중합니다. 이 구조가 속도와 안정성을 조율하는 기준이 됩니다. 에러 버짓의 상세한 운영 방법은 다음 글에서 다룹니다.
## 좋은 SLO에 반드시 들어가야 할 것

좋은 SLO는 단순히 숫자가 높은 목표가 아닙니다. 어떤 SLI를 기준으로 하는지, 어느 기간 동안 평가하는지, 누가 오너인지가 분명해야 합니다. 그래야 목표 위반이 실제 행동으로 이어집니다. 이 세 요소가 빠진 SLO는 성과 대시보드에 있어도 누구에게도 영향을 주지 못합니다.

특히 오너가 없는 SLO는 실무에서 거의 존재하지 않는 것과 같습니다. 숫자는 적혀 있어도 아무도 책임 있게 읽지 않기 때문입니다. 강한 팀일수록 SLO를 문서가 아니라 운영 기준으로 취급합니다.

## 구체적인 SLO 예시 (가용성 99.9%)

추상적인 99.9%보다 실제 허용 다운타임으로 표현하면 목표가 더 구체적이 됩니다.

```python
# 99.9% 가용성 = 월간 43분 다운타임 허용
def monthly_downtime(availability):
    total_minutes = 30 * 24 * 60  # 43200분
    downtime = (1 - availability) * total_minutes
    return downtime

print(f"99.9%: {monthly_downtime(0.999):.1f}min")  # 43.2분
print(f"99.95%: {monthly_downtime(0.9995):.1f}min")  # 21.6분
print(f"99.99%: {monthly_downtime(0.9999):.1f}min")  # 4.3분
```

99.9% 가용성은 월간 43분의 다운타임을 허용합니다. 이 숫자를 보면 목표가 현실적인지, 달성하려면 어떤 투자가 필요한지 판단하기 쉬워집니다.

## 좋은 SLI 선택 기준

SLI를 고를 때 다음 기준을 충족하면 운영에서 유용합니다.

**사용자 경험을 직접 반영합니다.** CPU 사용률보다 HTTP 성공률이 사용자가 실제로 느끼는 품질에 더 가깝습니다.

**측정이 간단합니다.** 복잡한 계산식이나 여러 소스를 합치는 지표는 논쟁을 만듭니다.

**역치 계산이 가능합니다.** 지표가 나빠졌을 때 어느 구간에서 문제가 발생했는지 역으로 추적할 수 있어야 합니다.

**행동으로 연결됩니다.** 지표가 목표를 위반했을 때 무엇을 해야 할지 분명해야 합니다.
## 단계별로 명세 작성하기

### 1단계 — SLI 정의

```python
sli = {
    "name": "http_success_ratio",
    "formula": "http_2xx / http_total",
    "source": "ingress logs",
}
```

SLI는 측정의 출발점입니다. 이름과 공식만으로는 부족하고, 데이터 출처도 함께 적어야 합니다. 출처가 모호하면 지표 값이 달라졌을 때 누구도 원인을 설명하기 어렵습니다.

### 2단계 — SLO 정의

```python
slo = {
    "sli": sli["name"],
    "target": 0.999,
    "window_days": 30,
    "owner": "payments-team",
}
```

SLO에는 목표 수치, 측정 기간, 오너가 함께 들어가야 합니다. 목표가 있어도 오너가 없으면 운영 기준이 살아 움직이지 않습니다. 누가 보고, 누가 조정할지를 명시해야 합니다.

### 3단계 — SLA 정의

```python
sla = {
    "slo": slo,
    "remedy": "service credit 10%",
    "exclusions": ["scheduled maintenance"],
}
```

SLA는 외부 약속이므로 보상과 예외 조항이 필요합니다. 내부에서 공격적으로 잡은 SLO를 그대로 외부 계약으로 내보내면 지나치게 강한 약속이 되거나, 반대로 아무 의미 없는 문서가 될 수 있습니다.

### 4단계 — 위반 판정

```python
def violated(success, total, target):
    return (success / total) < target
```

좋은 목표는 위반 여부를 즉시 판정할 수 있어야 합니다. 숫자만 있고 판정 규칙이 모호하면 운영 판단은 다시 감으로 돌아갑니다.

### 5단계 — 보고 형식 정리

```python
def report(success, total, target):
    return {
        "value": success / total,
        "violated": (success / total) < target,
    }
```

운영에서는 측정 결과를 읽기 쉬운 형식으로 정리하는 일도 중요합니다. 값과 위반 여부가 함께 보여야 주간 리뷰, 장애 회고, 고객 커뮤니케이션까지 자연스럽게 이어집니다.

### 6단계 — 남은 버짓까지 함께 보고하기

```python
def budget_summary(success, total, target):
    errors = total - success
    allowed = (1 - target) * total
    remaining = allowed - errors
    return {
        "availability": success / total,
        "allowed_errors": allowed,
        "remaining_errors": remaining,
    }
```

여기까지 오면 SLI, SLO, SLA가 단순한 정의 암기가 아니라 운영 숫자로 연결됩니다. 현재 값이 얼마인지, 목표를 넘겼는지, 앞으로 얼마나 더 실패를 감당할 수 있는지를 한 보고 안에서 같이 보여 줄 수 있기 때문입니다.

### 7단계 — 숫자가 다르게 보일 때 먼저 확인할 것

운영 대시보드와 고객 보고서의 수치가 다를 때는 곧바로 목표를 의심하지 않는 편이 좋습니다. 먼저 같은 요청 집합을 보고 있는지, 성공과 실패 정의가 같은지, 측정 기간이 같은지부터 확인해야 합니다. 많은 SLO 논쟁은 사실 지표 정의 불일치에서 시작합니다.

| 먼저 볼 항목 | 왜 중요한가 |
| --- | --- |
| 같은 요청 집합을 보고 있는가 | 엣지 트래픽과 앱 내부 트래픽은 가용성 값이 다르게 나올 수 있습니다. |
| redirect, client error를 어떻게 셌는가 | 공식은 같아 보여도 성공 기준이 다르면 결과가 달라집니다. |
| 30일 rolling window인가, 달력 월 기준인가 | 같은 99.9%라도 해석해야 할 위험이 달라집니다. |
| 유지보수 시간을 제외했는가 | 내부 목표와 외부 약속 문서는 예외 처리 방식이 다를 수 있습니다. |


## 실무 SLI 정의 예시 (서비스별)

SLI는 서비스마다 다릅니다. 같은 공식이라도 무엇을 성공으로 볼지, 어떤 요청을 포함할지에 따라 지표의 의미가 완전히 달라집니다. 다음은 서비스 유형별 SLI 정의 예시입니다.

### API 서비스

```python
sli_api = {
    "name": "api_availability",
    "formula": "http_2xx / (http_total - http_4xx)",
    "source": "ingress controller logs",
    "note": "클라이언트 오류(4xx)는 서비스 책임이 아니므로 제외",
}
```

4xx를 제외하는 이유가 중요합니다. 클라이언트가 잘못된 요청을 보낸 것은 서비스의 신뢰성 문제가 아닙니다. SLI 공식을 정할 때 이런 경계를 명확히 해야 팀 간 논쟁이 줄어듭니다.

### 데이터 파이프라인

```python
sli_pipeline = {
    "name": "pipeline_freshness",
    "formula": "current_time - last_successful_run_time < threshold",
    "source": "Airflow metadata DB",
    "threshold": "15분",
    "note": "데이터가 15분 이상 지연되면 신선하지 않은 것으로 판단",
}
```

데이터 파이프라인은 HTTP 응답으로 측정할 수 없는 경우가 많습니다. 대신 데이터 신선도(freshness)를 SLI로 사용합니다. 마지막 성공 실행 시각과 현재 시각의 차이가 임계값을 넘으면 SLO 위반입니다.

### 저장소 서비스

```python
sli_storage = {
    "name": "storage_durability",
    "formula": "verified_objects / total_objects",
    "source": "integrity check batch job",
    "frequency": "daily",
    "note": "일 1회 무결성 검증 배치에서 확인",
}
```

### PromQL 기반 SLI 계산

실제 운영 환경에서 SLI를 PromQL로 정의하면 자동 계산과 알림 연결이 가능합니다.

```promql
# API 가용성 SLI (30일 rolling window)
sum(increase(http_requests_total{status=~"2..",service="payments"}[30d]))
/
(
  sum(increase(http_requests_total{service="payments"}[30d]))
  -
  sum(increase(http_requests_total{status=~"4..",service="payments"}[30d]))
)
```

```promql
# Latency SLI: 300ms 이내 응답 비율
sum(increase(http_request_duration_seconds_bucket{le="0.3",service="search"}[30d]))
/
sum(increase(http_request_duration_seconds_count{service="search"}[30d]))
```

이 쿼리는 30일 동안 검색 서비스에서 300ms 이내에 응답한 요청의 비율을 계산합니다. 이 값이 SLO 목표(예: 99%) 아래로 떨어지면 에러 버짓이 소진됩니다.

## SLO 문서 실전 템플릿

SLO를 운영 가능하게 만들려면 목표 수치 외에 여러 정보를 함께 문서화해야 합니다. 다음은 실무에서 바로 쓸 수 있는 SLO 문서 템플릿입니다.

```yaml
# SLO Document: Payments API
service: payments-api
version: "2026-05-01"
owner: payments-team
approver: platform-lead

slis:
  - name: availability
    formula: "http_2xx / (http_total - http_4xx)"
    source: "ingress controller access logs"
    
  - name: latency
    formula: "requests_under_300ms / total_requests"
    source: "Prometheus histogram"

slos:
  - sli: availability
    target: 99.9%
    window: 30d (rolling)
    consequence:
      warning: "소진 50% → 배포 리뷰 강화"
      critical: "소진 80% → 배포 freeze"
      violated: "소진 100% → 전면 안정화, 포스트모템"
    
  - sli: latency
    target: 99.0%
    window: 30d (rolling)
    threshold: "p99 < 300ms"
    consequence:
      warning: "p99 500ms 초과 → 성능 분석"
      critical: "p99 1초 초과 → 긴급 대응"

error_budget:
  availability:
    monthly_requests: 10_000_000
    allowed_errors: 10_000
    
  latency:
    monthly_requests: 10_000_000
    allowed_slow: 100_000

review:
  frequency: weekly
  participants: [sre-lead, payments-lead, product-manager]
  dashboard: "https://grafana.internal/d/payments-slo"
```

이 템플릿의 핵심은 목표 수치만 적는 것이 아니라, 위반 시 행동(consequence)과 리뷰 일정(review)까지 함께 명시하는 것입니다. 이 구조가 있어야 SLO가 문서에서 멈추지 않고 운영 판단으로 이어집니다.

## SLA 계약서에 들어가야 할 핵심 항목

SLA는 법적 구속력이 있는 외부 약속입니다. 기술팀이 내부적으로 관리하는 SLO와 달리, SLA는 법무팀, 영업팀과 함께 만들어야 합니다. 다음은 SLA 계약서에 반드시 포함해야 할 항목입니다.

| 항목 | 설명 | 예시 |
| --- | --- | --- |
| 서비스 범위 | SLA가 적용되는 서비스와 기능 | "결제 API의 POST /payments 엔드포인트" |
| 측정 방법 | 가용성을 어떻게 계산하는지 | "5분 단위 성공 응답 비율, 모니터링 시스템 기준" |
| 목표 수치 | 보장하는 서비스 수준 | "월간 99.5% 가용성" |
| 제외 조건 | SLA에서 제외되는 상황 | "정기 유지보수, 고객 네트워크 문제, 불가항력" |
| 보상 정책 | 위반 시 고객에게 제공하는 보상 | "99.5% 미달 시 월 요금 10% 크레딧" |
| 보고 주기 | SLA 달성 여부를 보고하는 빈도 | "월 1회, 고객 포털에서 확인 가능" |
| 분쟁 해결 | 측정 결과 불일치 시 절차 | "양측 합의된 제3자 모니터링 기준 적용" |

```python
# SLA 보상 계산 예시
def calculate_credit(monthly_fee, availability, sla_tiers):
    """
    SLA 위반 시 크레딧 계산
    sla_tiers: [(threshold, credit_pct), ...]
    """
    for threshold, credit_pct in sorted(sla_tiers, reverse=True):
        if availability < threshold:
            return monthly_fee * credit_pct
    return 0

sla_tiers = [
    (0.995, 0.10),  # 99.5% 미달 → 10% 크레딧
    (0.990, 0.25),  # 99.0% 미달 → 25% 크레딧
    (0.950, 0.50),  # 95.0% 미달 → 50% 크레딧
]

# 이번 달 가용성 99.3%, 월 요금 100만원
credit = calculate_credit(1_000_000, 0.993, sla_tiers)
print(f"보상 크레딧: ₩{credit:,.0f}")  # ₩100,000
```

SLA의 목표 수치는 반드시 내부 SLO보다 낮게 설정해야 합니다. 내부적으로 99.9%를 목표로 운영하고, 외부에는 99.5%를 약속하면 버퍼가 생깁니다. 이 버퍼가 없으면 SLO를 약간만 놓쳐도 바로 SLA 위반으로 이어져 보상이 발생합니다.

## SLI/SLO 도입 시 자주 하는 실수와 대응

| 실수 | 왜 문제인가 | 대응 방법 |
| --- | --- | --- |
| 모든 API에 동일한 SLO 적용 | 중요도가 다른 서비스를 같은 기준으로 관리 | 핵심 경로와 부수 경로를 분리하여 차등 적용 |
| SLO를 만들고 리뷰하지 않음 | 문서만 존재하고 운영에 반영 안 됨 | 주간 SLO 리뷰 미팅 필수화 |
| SLA 수치를 SLO와 동일하게 설정 | 내부 목표 미달 시 바로 보상 발생 | SLA < SLO로 버퍼 확보 |
| 측정 기간을 명시하지 않음 | 같은 수치도 해석이 달라짐 | 30일 rolling window 명시 |
| SLI 정의에 데이터 소스 누락 | 숫자 재현 불가, 팀 간 논쟁 발생 | 쿼리문과 데이터 소스를 함께 기록 |

## 이 코드에서 먼저 봐야 할 점

- SLI는 지표 정의와 데이터 출처를 함께 가져야 합니다.
- SLO는 목표 수치만이 아니라 기간과 오너를 포함해야 합니다.
- SLA는 외부 약속이므로 보상과 예외 조항이 빠지면 안 됩니다.
- 위반 판정과 보고 형식까지 있어야 숫자가 실제 운영에 쓰입니다.


## SLO 리뷰 미팅 운영법

SLO 문서를 만들어 놓고 아무도 보지 않는다면 그 문서는 이미 죽은 것입니다. SLO를 살려 두려면 정기적인 리뷰 미팅이 필요합니다.

**주간 SLO 리뷰 체크리스트:**

- [ ] 지난 7일간 각 SLI의 실제 달성률을 확인했는가?
- [ ] 에러 버짓 소진 속도(burn rate)를 확인했는가?
- [ ] SLO 위반이 있었다면 원인을 파악했는가?
- [ ] 다음 주 예정된 배포가 버짓에 미칠 영향을 예측했는가?
- [ ] 액션 아이템이 있다면 오너와 기한을 정했는가?

리뷰 미팅은 15-20분이면 충분합니다. 대시보드를 함께 보면서 "지금 괜찮은가?" → "괜찮지 않다면 왜인가?" → "무엇을 할 것인가?" 순서로 대화합니다. 이 습관이 SLO를 문서에서 운영 도구로 전환시킵니다.

## 여기서 자주 헷갈립니다

가장 흔한 실수는 SLO를 SLA처럼 말하는 것입니다. 내부 목표는 더 공격적일 수 있지만, 외부 약속은 보상과 예외를 고려해 신중하게 정해야 합니다.

또 하나는 SLI를 공식만으로 정의하는 것입니다. 데이터 출처가 빠지면 숫자를 재현하기 어렵고, 팀 간 논쟁이 길어집니다. 측정 도구와 로그 위치까지 명시하는 습관이 필요합니다.

마지막으로 측정 기간을 적지 않는 경우도 많습니다. 99.9%라는 값은 하루 기준인지 한 달 기준인지에 따라 운영 의미가 완전히 달라집니다.

에러 버짓을 처음 도입할 때는 수치 계산보다 팀 합의가 먼저입니다. 목표를 지키지 못했을 때 배포를 멈출지, 추가 리뷰를 할지, 큰 리팩토링을 미룰지를 미리 정해두면 번아웃이 줄고 판단이 빨라집니다.

## 운영 체크리스트

- [ ] SLI의 이름, 공식, 데이터 출처를 문서화했다.
- [ ] SLO에 목표 수치, 측정 기간, 오너를 적었다.
- [ ] SLA에 보상과 예외 조항을 명시했다.
- [ ] 위반 여부를 자동 판정할 수 있다.
- [ ] 내부 목표와 외부 약속을 혼동하지 않는다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 “측정할 수 없으면 목표가 아니다”라는 태도를 갖습니다. 실제로 측정할 수 없는 SLO는 결국 회의 자료로만 남고, 운영 기준으로 기능하지 못합니다.

또한 B2B 환경에서는 SLA가 법무와 영업이 함께 보는 문서가 되기도 합니다. 이때 SLO와 SLA의 경계를 명확히 해 두지 않으면 운영 숫자가 계약 분쟁으로 번질 수 있습니다. 기술 문서와 비즈니스 문서가 만나는 지점이라서 더 신중해야 합니다.

SLO 위반 시 에러 버짓이 소진되면 어떻게 대응할지도 미리 정해두면 번아웃을 줄일 수 있습니다. 공격적인 목표를 세우더라도 위반 시 행동 규칙이 명확하면 불안 없이 운영할 수 있습니다.

## 정리

SLI, SLO, SLA는 비슷한 약어가 아니라 서로 다른 책임층입니다. SLI는 측정, SLO는 내부 목표, SLA는 외부 약속을 뜻합니다. 이 구분이 선명해야 신뢰성 숫자가 운영 판단과 고객 기대를 함께 지탱할 수 있습니다.

다음 글에서는 에러 버짓을 다룹니다. 목표를 세운 뒤 어느 정도 실패를 허용하고, 그 범위 안에서 어떻게 출시 속도를 조절할지 이어서 정리하겠습니다.

## 처음 질문으로 돌아가기

- **SLI, SLO, SLA는 각각 어떤 역할을 맡고 어디서 경계가 갈릴까요?**
  - SLI는 측정 단계에서 지표를, SLO는 운영 단계에서 목표를, SLA는 계약 단계에서 보상 제도를 정합니다. 측정부터 시작해 목표로 중간을 거쳐 약속으로 마무리하는 세 층위로 나뉩니다.
- **내부 목표와 외부 약속은 왜 같은 문서가 아니어야 할까요?**
  - SLO는 내부 팀이 빠르게 판단하고 실험할 수 있도록 오너를 명시한 운영 기준입니다. 반면 SLA는 계약 문서로 외부 고객에게 보상 책임을 명시한 약속입니다. 오너가 다르고 리스크도 다릅니다.
- **좋은 SLO에는 목표 수치 외에 어떤 정보가 반드시 들어가야 할까요?**
  - 목표 수치만으로는 운영 판단이 이루어지지 않습니다. 측정 기간, 오너, 데이터 출처가 함께 있어야 목표 위반 시 누가 무엇을 보고 어떤 조치를 취할지 판단할 수 있습니다. SLO를 글자가 아니라 행동으로 연결하려면 이 세 가지가 반드시 명시되어야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- **SLI, SLO, SLA (현재 글)**
- Error Budget (예정)
- Monitoring (예정)
- Incident Response (예정)
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Service Level Objectives - Google SRE Book](https://sre.google/sre-book/service-level-objectives/)
- [Implementing SLOs - Google SRE Workbook](https://sre.google/workbook/implementing-slos/)
- [SLI vs SLO vs SLA - Atlassian](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
- [SLA, SLO, SLI - DigitalOcean](https://www.digitalocean.com/community/tutorials/what-is-sla-slo-sli)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, SLI, SLO, SLA, Reliability
