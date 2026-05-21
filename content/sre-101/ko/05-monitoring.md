---
episode: 5
language: ko
last_reviewed: '2026-05-14'
seo_description: 행동으로 이어지는 모니터링을 위한 골든 시그널과 알림 설계, 알림 피로 감소와 대시보드 구성법을 정리합니다.
series: sre-101
status: content-ready
tags:
- SRE
- Monitoring
- Metrics
- Alerting
- Observability
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (5/10): Monitoring"
---

# SRE 101 (5/10): Monitoring

운영 초기에 팀은 가능한 한 많은 수치를 모으는 데 안심을 느끼곤 합니다. CPU, 메모리, 요청 수, 큐 길이, 오류 로그를 다 저장해 두면 언젠가 쓸모가 있을 것 같기 때문입니다. 하지만 많이 모은다고 해서 모니터링이 좋아지는 것은 아닙니다.

좋은 모니터링은 데이터를 많이 쌓는 체계가 아니라, 지금 움직여야 하는지 바로 판단하는 체계입니다. 알림이 울렸는데도 누구도 무엇을 해야 할지 모르면 그 신호는 이미 역할을 잃은 상태입니다.

이 글은 SRE 101 시리즈의 5번째 글입니다. 여기서는 monitoring을 행동으로 이어지는 측정으로 정의하고, 네 가지 핵심 운영 신호, 알림 설계 원칙, 대시보드 구성 방식, 알림 피로를 줄이는 관점을 정리합니다.

## 먼저 던지는 질문

- monitoring은 단순 수집과 어떻게 다를까요?
- latency, traffic, errors, saturation은 왜 함께 봐야 할까요?
- 메트릭과 로그는 각각 어떤 질문에 답할까요?

## 큰 그림

![SRE 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/05/05-01-concept-at-a-glance.ko.png)

*SRE 101 5장 흐름 개요*

Monitoring을 세 층으로 분해하면 수집 단계, 판단 단계, 대응 단계로 나뇉니다. 메트릭과 로그는 수집을 담당하고, 알림은 판단을 보조하며, 대시보드는 상황 파악과 신속한 대응을 돕습니다.

> 메트릭은 현재 상태를 숫자로 보여 주고, 로그는 구체적인 사건을 기록하며, 알림은 기준 위반 시 즉시 행동을 요구합니다.

## 왜 이 주제가 중요한가

알림이 너무 많으면 중요한 신호가 묻힙니다. 반대로 알림이 너무 약하면 사용자가 먼저 장애를 발견합니다. 모니터링의 품질은 데이터 양보다 행동 연결성이 좌우합니다.

또한 팀이 자주 보는 지표는 곧 팀이 중요하다고 여기는 품질 기준이 됩니다. 어떤 메트릭에 알림을 걸고, 어떤 그래프를 첫 화면에 두는지는 운영 문화 자체를 형성합니다.

## 한 문장으로 잡는 멘탈 모델

> 모니터링은 많이 보는 기술이 아니라, 필요한 순간에 바로 행동하게 만드는 측정 설계입니다.

## 한눈에 보는 구조

메트릭과 로그는 그냥 저장되는 데이터가 아니라, 알림과 대시보드를 거쳐 대응으로 이어져야 합니다. 이 연결이 없으면 관측은 하고 있어도 운영 판단은 여전히 느립니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 실무에서 보는 포인트 |
| --- | --- | --- |
| golden signals | latency, traffic, errors, saturation 네 신호 | 시스템 상태를 빠르게 읽는 공통 언어가 됩니다 |
| alert | 즉시 행동이 필요한 신호 | 설명용이 아니라 행동용이어야 합니다 |
| threshold | 경고를 발생시키는 기준값 | 팀 합의가 없으면 남발되기 쉽습니다 |
| dashboard | 상태를 한눈에 읽는 화면 | 질문에 답하는 순서가 있어야 합니다 |
| paging | 사람을 깨우는 수준의 호출 | 정말 즉시 대응이 필요한 경우에만 써야 합니다 |

## 핵심 관점

모니터링은 모든 것을 수집하는 일이 아닙니다. **행동으로 이어지는 측정만 남기는 일**에 더 가깝습니다. 그래서 좋은 모니터링 체계는 메트릭을 무한히 늘리기보다, 어떤 수치가 실제로 대응을 바꾸는지를 먼저 따집니다.

현업에서 강한 팀은 대시보드와 알림을 구분해서 봅니다. 대시보드는 상황을 이해하는 데 쓰고, 알림은 지금 바로 움직일지 여부를 판단하는 데 씁니다. 이 경계가 무너지면 그래프는 많은데 행동은 느린 상태가 됩니다.

## 모니터링 유형 표

모니터링 방식은 어디서 측정하는지, 어떻게 수집하는지에 따라 나뇉니다. 각 유형은 서로 다른 장점과 용도를 갖습니다.

| 유형 | 설명 | 용도 | 대표 도구 |
| --- | --- | --- | --- |
| **블랙박스** | 외부에서 사용자 관점으로 측정 | 실제 사용자 경험 분석 | Synthetic monitoring, Uptime check |
| **화이트박스** | 시스템 내부 메트릭 수집 | 원인 분석, 병목 현상 파악 | Prometheus, Datadog, CloudWatch |
| **푸시 (Push)** | 애플리케이션이 메트릭을 전송 | 단기 실행 프로세스, 배치 작업 | StatsD, CloudWatch custom metrics |
| **풀 (Pull)** | 모니터링 시스템이 정기적 수집 | 장기 실행 서비스 | Prometheus /metrics endpoint |

블랙박스는 사용자 체감을 먼저 보고, 화이트박스는 원인을 파고듭니다. 푸시는 불규칙 이벤트를 빠르게 보내고, 풀은 수집 서버가 타겟 목록을 중앙에서 관리하는 구조입니다.
## 네 가지 신호를 함께 봐야 하는 이유

latency는 느린가를, traffic은 평소와 같은 수요가 들어오고 있는가를, errors는 실패가 늘고 있는가를, saturation은 곧 자원이 한계에 닿는가를 보여 줍니다. 네 신호는 서로 다른 질문에 답합니다.

예를 들어 오류 비율이 낮아도 saturation이 95%에 가까우면 큰 장애 직전일 수 있습니다. 반대로 트래픽이 평소보다 급감했다면, 오류가 보이지 않아도 라우팅이나 수집 계층 문제가 있을 수 있습니다. 네 축을 함께 봐야 상황을 입체적으로 읽을 수 있습니다.

## 단계별로 핵심 네 신호 측정하기

### 1단계 — 지연 시간

```python
def latency_p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

사용자는 평균이 아니라 느린 요청을 기억합니다. 그래서 latency는 평균보다 p95, p99 같은 분위수로 보는 편이 실제 체감과 더 잘 맞습니다.

### 2단계 — 트래픽

```python
def rps(reqs, seconds):
    return reqs / seconds
```

트래픽은 시스템에 들어오는 수요를 보여 줍니다. 갑자기 늘어나는 것도 문제지만, 갑자기 줄어드는 것도 문제일 수 있습니다. 예상했던 요청이 보이지 않는 상태는 사용자 진입 경로나 상위 시스템 이상을 뜻할 수 있습니다.

### 3단계 — 오류 비율

```python
def error_ratio(err, total):
    return err / total
```

오류 개수보다 오류 비율이 더 유용한 경우가 많습니다. 전체 요청이 늘어난 상황과 아닌 상황을 구분할 수 있기 때문입니다. 사용자가 실제로 얼마나 넓게 영향을 받는지도 더 잘 드러납니다.

### 4단계 — 포화도

```python
def saturation(used, capacity):
    return used / capacity
```

포화도는 아직 장애가 나지 않았더라도, 곧 자원 한계가 문제를 만들지 읽게 해 줍니다. CPU, 메모리, 큐 길이, 연결 수처럼 한계에 가까워질수록 대기 시간이 길어지는 자원이 대표적입니다.

### 5단계 — 페이지 알림 규칙

```python
def should_page(err_ratio, p95_ms, sat):
    return err_ratio > 0.01 or p95_ms > 500 or sat > 0.9
```

페이지 알림은 사람이 즉시 개입해야 할 때만 울려야 합니다. 밤에 사람을 깨울 만큼 중요한 조건인지 먼저 묻는 습관이 있으면 알림 설계가 훨씬 단단해집니다.

### 6단계 — 지연 시간 급증 시 첫 확인 순서 정하기

골든 시그널은 많이 보는 지표 묶음이 아니라, 대응 순서를 줄여 주는 질문 묶음이기도 합니다. latency 알림이 울렸을 때 무엇부터 확인할지 정리되어 있지 않으면, 좋은 메트릭이 있어도 대응은 여전히 느립니다.

| 증상 | 첫 확인 대상 | 왜 여기부터 보는가 |
| --- | --- | --- |
| p95 latency 상승, traffic은 평소와 비슷 | saturation과 외부 의존성 지연 | 수요 변화 없이 느려지면 자원 압박이나 downstream 지연이 먼저 의심됩니다. |
| traffic 급감 | ingress, CDN, 상위 라우팅 상태 | 앱은 멀쩡해도 요청이 도달하지 못하면 트래픽이 먼저 줄어듭니다. |
| errors와 saturation 동시 상승 | 큐 길이, timeout, 연결 풀 | 용량 한계에 닿기 직전의 전형적인 신호입니다. |
| errors 상승, latency 변화는 작음 | 최근 배포, 인증·권한 경로 | 빠르게 실패하는 문제는 로직이나 설정 이상일 가능성이 큽니다. |

### 7단계 — 구조화 이벤트를 알림 판단과 연결하기

```python
def classify_event(status_code, latency_ms, cache_hit):
    page = status_code >= 500 or latency_ms > 800
    investigate = latency_ms > 300 and not cache_hit
    return {"page": page, "investigate": investigate}
```

이 예시는 단순하지만 중요한 감각을 보여 줍니다. 같은 지연 시간 급증이라도 캐시 미스가 늘어난 상황인지, 5xx가 함께 올라가는 상황인지에 따라 대응 우선순위가 달라집니다. 메트릭을 맥락과 함께 읽을수록 알림의 품질도 좋아집니다.

## Prometheus 메트릭 예제

Prometheus는 풀 기반 메트릭 시스템의 대표적인 도구입니다. 세 가지 주요 메트릭 타입(counter, gauge, histogram)을 이해하면 골든 시그널을 구체화할 수 있습니다.

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Counter: 누적 카운터 (요청 수, 에러 수 등)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Gauge: 현재 값 (CPU, 메모리, 큐 길이 등)
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Histogram: 분포 (지연 시간, 요청 크기 등)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# 메트릭 사용 예시
def handle_request(method, endpoint):
    active_connections.inc()  # 연결 증가
    
    start = time.time()
    try:
        # ... 요청 처리 ...
        status = 200
    except Exception:
        status = 500
    finally:
        duration = time.time() - start
        
        # 메트릭 기록
        http_requests_total.labels(method, endpoint, status).inc()
        http_request_duration_seconds.labels(method, endpoint).observe(duration)
        active_connections.dec()  # 연결 감소

# Prometheus 메트릭 서버 시작 (:9090/metrics)
start_http_server(9090)
```

Counter는 traffic과 errors를, Gauge는 saturation을, Histogram은 latency를 측정하는 데 적합합니다. 이 세 타입만으로도 골든 시그널을 모두 커버할 수 있습니다.


## 골든 시그널 기반 대시보드 설계

대시보드는 그래프 묶음이 아니라, 질문에 답하는 화면이어야 합니다. 좋은 대시보드는 장애 상황에서 "무엇이 문제인가?"를 30초 안에 파악할 수 있게 해 줍니다.

### 대시보드 레이아웃 설계 원칙

| 행 | 목적 | 패널 예시 |
| --- | --- | --- |
| 1행 | 지금 문제가 있는가? | SLO 달성률, 에러 버짓 잔량, 활성 알림 수 |
| 2행 | 어떤 신호에서 문제인가? | Latency p95/p99, Error rate, Saturation |
| 3행 | 언제부터 문제인가? | 배포 시점 표시, Traffic 변화, 최근 이벤트 |
| 4행 | 어디에서 문제인가? | 서비스별 상태, 의존성 지연, 지역별 차이 |

### 실전 PromQL 대시보드 쿼리 모음

```promql
# 1행: SLO 달성률 (30일 rolling)
sum(rate(http_requests_total{status=~"2.."}[30d]))
/ sum(rate(http_requests_total[30d]))

# 2행: Latency p95 (5분 윈도우)
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)

# 2행: Error rate by service
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
/ sum(rate(http_requests_total[5m])) by (service)

# 2행: Saturation (커넥션 풀 사용률)
sum(active_db_connections) by (service)
/ sum(max_db_connections) by (service)

# 3행: Traffic (RPS) - 전주 대비
sum(rate(http_requests_total[5m]))
# vs
sum(rate(http_requests_total[5m] offset 7d))
```

### 대시보드 안티패턴

| 안티패턴 | 왜 문제인가 | 개선 방향 |
| --- | --- | --- |
| 그래프 30개 이상 | 정보 과부하, 핵심을 놓침 | 7-12개로 제한, 행별 목적 명확화 |
| 모두 같은 시간 범위 | 장기 트렌드와 단기 이상을 구분 못함 | 1행은 30일, 2-4행은 6시간 |
| 제목 없는 패널 | 무엇을 보는지 추측해야 함 | 질문 형태의 제목 사용 |
| 임계선 없음 | 정상과 비정상 구분 불가 | SLO 목표선, 경고 임계선 표시 |

## Observability 3요소: 메트릭, 로그, 트레이스

모니터링을 넘어서 observability를 이야기할 때는 메트릭, 로그, 트레이스를 함께 봐야 합니다. 각각 서로 다른 질문에 답합니다.

| 요소 | 답하는 질문 | 특징 | 도구 예시 |
| --- | --- | --- | --- |
| 메트릭 | 무엇이 일어나고 있는가? (숫자) | 집계 가능, 저장 비용 낮음 | Prometheus, Datadog |
| 로그 | 왜 일어났는가? (텍스트) | 상세하지만 대량, 검색 필요 | Loki, Elasticsearch |
| 트레이스 | 어디서 느려졌는가? (경로) | 요청별 흐름 추적 | Jaeger, Tempo |

### 세 요소의 연결

좋은 observability 스택은 세 요소가 서로 연결되어 있습니다.

```python
# 구조화 로그 예시 (메트릭과 트레이스를 연결)
import logging
import json

def structured_log(level, message, **kwargs):
    """메트릭, 트레이스와 연결 가능한 구조화 로그"""
    log_entry = {
        "level": level,
        "message": message,
        "service": "payments-api",
        "trace_id": kwargs.get("trace_id", ""),
        "span_id": kwargs.get("span_id", ""),
        "duration_ms": kwargs.get("duration_ms", 0),
        "status_code": kwargs.get("status_code", 0),
        "endpoint": kwargs.get("endpoint", ""),
    }
    print(json.dumps(log_entry))

# 사용 예시
structured_log(
    "info",
    "Request completed",
    trace_id="abc123",
    span_id="def456",
    duration_ms=245,
    status_code=200,
    endpoint="/api/payments"
)
```

trace_id를 로그에 포함하면, 메트릭에서 이상을 발견했을 때 → 해당 시간대의 로그를 검색하고 → 특정 요청의 트레이스를 따라가는 흐름이 가능해집니다. 이 연결이 없으면 각 도구가 따로 놀게 됩니다.

## SLO 기반 알림 vs 증상 기반 알림

전통적인 모니터링은 증상 기반(symptom-based) 알림을 사용합니다. CPU > 80%, 메모리 > 90% 같은 임계값입니다. SRE에서는 SLO 기반 알림을 더 권장합니다.

| 비교 항목 | 증상 기반 | SLO 기반 |
| --- | --- | --- |
| 알림 조건 | CPU > 80% | 에러 버짓 burn rate > 14.4x |
| 장점 | 설정 간단, 직관적 | 사용자 영향과 직결, 오탐 적음 |
| 단점 | 오탐 많음, 실제 사용자 영향 불명 | 설정 복잡, SLO 선행 필요 |
| 언제 사용 | 인프라 자원 모니터링 | 서비스 수준 모니터링 |

SLO 기반 알림의 핵심은 "사용자가 영향을 받고 있는가?"라는 질문에 답하는 것입니다. CPU가 90%여도 사용자 응답이 빠르면 문제가 아닐 수 있고, CPU가 50%여도 외부 의존성 타임아웃으로 사용자가 에러를 보고 있을 수 있습니다.

```promql
# SLO 기반 알림: 에러 버짓이 빠르게 소진될 때만 페이지
(
  1 - (
    sum(rate(http_requests_total{status=~"2.."}[1h]))
    / sum(rate(http_requests_total[1h]))
  )
) > (14.4 * (1 - 0.999))
```

이 방식이 "CPU > 80%"보다 훨씬 적게 울리면서도, 실제 사용자에게 영향이 있는 상황을 더 정확하게 잡아냅니다.

## 이 코드에서 먼저 봐야 할 점

- 네 가지 신호는 운영에서 공통 언어 역할을 합니다.
- 알림은 행동 가능한 조건에만 걸어야 합니다.
- 대시보드는 그래프 묶음이 아니라 질문에 답하는 화면이어야 합니다.
- 메트릭은 고객 경험과 연결될수록 운영 판단이 빨라집니다.

## 여기서 자주 헷갈립니다

가장 흔한 실수는 모든 지표에 알림을 붙이는 것입니다. 알림 수가 많다고 통제가 잘되는 것이 아닙니다. 오히려 중요한 호출을 묻어 버릴 가능성이 큽니다.

또 다른 실수는 평균값만 보는 것입니다. 평균이 안정적으로 보여도 p95, p99가 나쁘면 사용자는 이미 문제를 겪고 있습니다. 특히 latency는 꼬리 구간을 별도로 봐야 합니다.

대시보드를 크게 만드는 것이 좋은 설계라고 믿는 경우도 많습니다. 하지만 질문 순서가 없는 대시보드는 그래프 묘지에 가깝습니다. 먼저 무엇을 확인해야 할지 드러나야 합니다.

## 알림 피로 방지

알림 피로는 알림이 너무 자주 울려서 팀이 무감각해지는 상태를 뜻합니다. 중요한 신호를 놓치거나, 알림을 무시하는 분위기가 생기면 모니터링 시스템이 무력화됩니다.

### 알림 피로를 줄이는 원칙

**페이지 알림은 즉시 행동이 필요한 경우만.** 밤에 사람을 깨울 만한 기준인지 먼저 물어야 합니다. 가중치를 낮추고 싶다면 페이지 대신 Slack 메시지나 대시보드 경고로 내리는 것을 고려합니다.

**Threshold는 현실적으로 설정합니다.** 이론적 목표가 아니라, 실제로 문제가 생기기 직전 구간을 잡아야 합니다. 평소 p95 latency가 100ms라면, 300ms를 경고로, 500ms를 페이지로 잡는 식입니다.

**알림을 정기적으로 리뷰합니다.** 분기마다 알림 목록을 점검하고, 최근 3개월간 한 번도 울리지 않은 알림은 삭제합니다. 반대로 매일 울리지만 아무도 대응하지 않는 알림도 재설계해야 합니다.

**행동 가능한 메시지를 작성합니다.** "높은 CPU 사용률" 같은 메시지 대신 "payments-api CPU > 80% for 5min, 런북 링크: wiki.internal/runbooks/high-cpu"처럼 구체적인 정보와 다음 단계를 함께 제공합니다.

**알림을 그룹화하고 여과합니다.** 같은 원인으로 여러 알림이 동시에 발생하면 하나로 묶어서 보냅니다. 1분 안에 같은 조건이 5번 울린다면 메시지를 하나로 통합하는 규칙을 둕니다.

### 알림 피로 지표 예시

```python
def alert_fatigue_score(alerts_last_week, actionable_alerts):
    """
    알림 피로 지표: 전체 알림 대비 실제 대응한 비율
    """
    if alerts_last_week == 0:
        return 0
    return 1 - (actionable_alerts / alerts_last_week)

# 예시: 지난 주 100건 알림, 실제 대응 20건
fatigue = alert_fatigue_score(100, 20)
print(f"알림 피로 지표: {fatigue*100:.0f}%")  # 80%

# 80% 이상이면 알림 리뷰 필요
if fatigue > 0.8:
    print("경고: 대다수 알림이 행동으로 연결되지 않음")
```

알림 피로를 줄이려면 숫자를 추적하고, 정기적으로 리뷰하며, 알림을 행동 규칙과 결합해야 합니다. 알림이 적을수록 더 강해지는 역설이 SRE의 핵심 가치 중 하나입니다.

### Prometheus Alerting Rules 예시

Prometheus에서 골든 시그널 기반 알림을 설정하는 YAML 예시입니다.

```yaml
groups:
  - name: golden_signals
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.01
        for: 3m
        labels:
          severity: page
        annotations:
          summary: "5xx 오류 비율이 1%를 초과했습니다"
          runbook: "https://wiki.internal/runbooks/high-error-rate"

      - alert: HighP95Latency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency가 500ms를 초과했습니다"
```

이 규칙에서 `for` 절은 일시적인 스파이크에 알림이 울리지 않도록 지속 시간을 지정합니다. severity를 나누면 page와 warning을 별도 채널로 라우팅할 수 있습니다.

## 운영 체크리스트

- [ ] latency, traffic, errors, saturation을 모두 본다.
- [ ] 페이지 알림은 즉시 행동이 필요한 경우에만 울린다.
- [ ] 평균 외에 분위수 지표를 함께 본다.
- [ ] 대시보드는 질문 순서에 맞춰 구성되어 있다.
- [ ] 알림 피로를 정기적으로 측정하고 정리한다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 알림을 예약된 전화처럼 취급합니다. 이 신호가 울렸을 때 정말 사람이 바로 움직여야 하는가를 먼저 묻습니다. 이 기준이 분명할수록 알림은 적어도 더 강해집니다.

또한 메트릭과 로그는 경쟁 관계가 아닙니다. 메트릭으로 이상 시점을 찾고, 로그로 원인 후보를 좁히는 식으로 함께 써야 합니다. 여기에 트레이스까지 더해지면 요청 경로를 더 정밀하게 읽을 수 있습니다.

## 정리

monitoring은 데이터를 많이 쌓는 일이 아니라, 시스템 상태를 보고 바로 행동할 수 있게 만드는 일입니다. 네 가지 핵심 신호를 공통 언어로 삼고, 알림과 대시보드를 서로 다른 역할로 설계하면 운영 판단 속도와 품질이 함께 좋아집니다.

다음 글에서는 incident response를 다룹니다. 실제 장애가 터졌을 때 누가 어떤 순서로 움직여야 하는지, 그리고 모니터링 신호가 대응으로 어떻게 이어지는지 정리하겠습니다.

## 처음 질문으로 돌아가기

- **monitoring은 단순 수집과 어떻게 다를까요?**
  - Monitoring은 단순히 데이터를 수집하는 것이 아니라, 수집한 메트릭을 기준으로 즉시 행동할지 판단하는 체계입니다. 알림이 울렸을 때 무엇을 해야 할지 명확하지 않다면 그 메트릭은 단순 기록일 뿐입니다.
- **latency, traffic, errors, saturation은 왜 함께 봐야 할까요?**
  - 네 메트릭은 각각 다른 질문에 답합니다. latency는 느린가, traffic은 평소와 같은 수요가 들어오는가, errors는 실패가 늘고 있는가, saturation은 곱 자원이 한계에 닿는가를 보여줍니다. 하나만 보면 전체 상황을 오해하기 쉬습니다.
- **메트릭과 로그는 각각 어떤 질문에 답할까요?**
  - 메트릭은 현재 상태를 숫자로 보여주고 이상 시점을 찾는 데 적합합니다. 로그는 구체적인 요청, 오류 메시지, 스택 트레이스를 기록하며 원인 분석에 적합합니다. 메트릭으로 언제가 이상한지 찾고, 로그로 왜 이상했는지 분석합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- **Monitoring (현재 글)**
- Incident Response (예정)
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Monitoring Distributed Systems - Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Practical Alerting - Google SRE Book](https://sre.google/sre-book/practical-alerting/)
- [USE Method - Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, Monitoring, Metrics, Alerting, Observability
