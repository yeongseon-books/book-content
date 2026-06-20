---
series: devops-101
episode: 7
title: "DevOps 101 (7/10): 모니터링과 알림"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - Monitoring
  - Alerting
  - Prometheus
  - Grafana
seo_description: Prometheus와 Grafana로 서비스 상태를 측정하고 의미 있는 알림을 설계하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (7/10): 모니터링과 알림

알림이 너무 많으면 아무도 보지 않게 되고, 너무 적으면 장애를 놓칩니다. 좋은 모니터링은 수집 데이터가 많은 것이 아니라, 올바른 신호를 올바른 사람에게 올바른 시간에 전달하는 것입니다.

이 글은 DevOps 101 시리즈의 일곱 번째 글입니다.

![DevOps 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/07/07-01-diagram.ko.png)
*DevOps 101 7장 흐름 개요*
> 모니터링은 데이터를 많이 모으는 것이 아니라, 서비스 상태에 대한 올바른 질문에 답하는 것입니다.

## 이 글에서 다룰 문제

- 황금 지표(4 Golden Signals)는 무엇이며 왜 중요한가요?
- Prometheus에서 의미 있는 지표를 어떻게 노출할까요?
- 알림 피로(alert fatigue)를 어떻게 방지할까요?
- SLO 기반 알림은 임계값 기반 알림과 어떻게 다를까요?

## 4대 황금 지표

Google SRE Book에서 제시한 네 가지 핵심 지표입니다.

| 지표 | 의미 | 예시 |
|------|------|------|
| Latency (지연) | 요청 처리 시간 | p99 응답 시간 |
| Traffic (트래픽) | 요청 부하 | 초당 요청 수 (RPS) |
| Errors (오류) | 실패 비율 | 5xx 오류율 |
| Saturation (포화) | 리소스 사용률 | CPU, 메모리, 큐 깊이 |

이 네 가지 지표만 제대로 측정하고 있어도 대부분의 장애를 사전에 감지하거나 빠르게 진단할 수 있습니다.

## Prometheus 지표 노출

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps

# 4대 황금 지표 정의
REQUEST_COUNT = Counter(
    "http_requests_total",
    "HTTP 요청 총 수",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP 요청 처리 시간 (초)",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "HTTP 오류 수",
    ["method", "endpoint", "error_type"],
)

ACTIVE_CONNECTIONS = Gauge(
    "http_active_connections",
    "현재 처리 중인 HTTP 연결 수",
)

# 비즈니스 지표
ORDER_CREATED = Counter(
    "orders_created_total",
    "생성된 주문 수",
    ["channel", "payment_method"],
)

ORDER_PROCESSING_TIME = Histogram(
    "order_processing_seconds",
    "주문 처리 시간",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

DB_CONNECTION_POOL = Gauge(
    "db_connection_pool_size",
    "데이터베이스 연결 풀 현황",
    ["state"],  # active, idle, waiting
)


def track_request(endpoint: str):
    """요청 지표 추적 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            method = kwargs.get("method", "GET")
            ACTIVE_CONNECTIONS.inc()
            start = time.perf_counter()
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result
            except ValueError:
                status_code = 400
                ERROR_COUNT.labels(method=method, endpoint=endpoint, error_type="validation").inc()
                raise
            except Exception:
                status_code = 500
                ERROR_COUNT.labels(method=method, endpoint=endpoint, error_type="internal").inc()
                raise
            finally:
                duration = time.perf_counter() - start
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=str(status_code),
                ).inc()
                REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
                ACTIVE_CONNECTIONS.dec()
        return wrapper
    return decorator
```

FastAPI에 지표 엔드포인트 추가:

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()

# /metrics 엔드포인트 마운트
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/orders")
@track_request("/orders")
def create_order(order: dict):
    # 주문 처리
    ORDER_CREATED.labels(
        channel=order.get("channel", "web"),
        payment_method=order.get("payment_method", "card"),
    ).inc()
    return {"order_id": "123", "status": "created"}
```

## Prometheus 알람 규칙

```yaml
# prometheus-rules.yaml
groups:
  - name: order-service.slo
    interval: 30s
    rules:
      # 오류율 SLO: 99.9% 가용성 목표
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_errors_total{endpoint="/orders"}[5m]))
            /
            sum(rate(http_requests_total{endpoint="/orders"}[5m]))
          ) * 100 > 0.1
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "주문 API 오류율 SLO 위반"
          description: "오류율 {{ $value | humanize }}% (임계값: 0.1%)"
          runbook: "https://wiki.example.com/runbooks/order-service-high-error-rate"

      # p99 지연 시간 SLO: 1초 미만
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket{endpoint="/orders"}[5m]))
            by (le)
          ) > 1.0
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "주문 API p99 지연 시간 SLO 위반"
          description: "p99 지연 {{ $value | humanize }}s (임계값: 1.0s)"

      # 심각한 오류율: 즉시 대응 필요
      - alert: CriticalErrorRate
        expr: |
          (
            sum(rate(http_errors_total{endpoint="/orders"}[1m]))
            /
            sum(rate(http_requests_total{endpoint="/orders"}[1m]))
          ) * 100 > 5
        for: 2m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "주문 API 긴급 - 오류율 5% 초과"
          description: "즉시 확인 필요. 오류율: {{ $value | humanize }}%"

  - name: infrastructure
    rules:
      # 메모리 사용률 높음
      - alert: HighMemoryUsage
        expr: |
          (
            container_memory_working_set_bytes{container="order-service"}
            /
            container_spec_memory_limit_bytes{container="order-service"}
          ) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "컨테이너 메모리 사용률 80% 초과"
          description: "메모리: {{ $value | humanize }}%"
```

## Alertmanager 라우팅 설정

```yaml
# alertmanager.yaml
global:
  resolve_timeout: 5m
  slack_api_url: "https://hooks.slack.com/services/XXXXX"

route:
  group_by: ["alertname", "cluster", "service"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: "default"

  routes:
    # Critical 알림: PagerDuty + Slack
    - match:
        severity: critical
      receiver: "critical-alerts"
      repeat_interval: 30m

    # Warning 알림: Slack만
    - match:
        severity: warning
      receiver: "slack-warnings"
      repeat_interval: 4h

receivers:
  - name: "default"
    slack_configs:
      - channel: "#alerts"
        title: "{{ .CommonAnnotations.summary }}"
        text: "{{ .CommonAnnotations.description }}"

  - name: "critical-alerts"
    pagerduty_configs:
      - service_key: "YOUR_PAGERDUTY_KEY"
    slack_configs:
      - channel: "#incidents"
        title: "CRITICAL: {{ .CommonAnnotations.summary }}"
        text: "{{ .CommonAnnotations.description }}\n런북: {{ .CommonAnnotations.runbook }}"
        color: "danger"

  - name: "slack-warnings"
    slack_configs:
      - channel: "#alerts"
        title: "WARNING: {{ .CommonAnnotations.summary }}"
        color: "warning"

inhibit_rules:
  # Critical 발생 시 동일 서비스의 Warning 억제
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ["alertname", "service"]
```

## 알림 피로 방지

좋은 알림 설계 원칙:

1. **행동을 요구하는 알림만 보냅니다.** 대응 절차가 없는 알림은 노이즈입니다.
2. **알림 수신자가 올바른 사람인지 확인합니다.** 담당자가 아닌 사람이 받는 알림은 무시됩니다.
3. **for 옵션으로 일시적 스파이크를 걸러냅니다.** 1분짜리 스파이크로 새벽에 깨울 필요는 없습니다.
4. **런북 링크를 포함합니다.** 알림만으로 무엇을 해야 할지 모르면 대응이 느려집니다.

```python
def evaluate_alert_quality(alert: dict) -> list[str]:
    """알림 품질 체크리스트"""
    issues = []

    if not alert.get("annotations", {}).get("runbook"):
        issues.append("런북 링크 없음: 대응 절차를 찾기 어렵습니다")

    if not alert.get("labels", {}).get("team"):
        issues.append("담당 팀 없음: 누가 대응해야 할지 불명확합니다")

    for_duration = alert.get("for", "0m")
    if for_duration in ("0m", "0s", ""):
        issues.append("for 미설정: 일시적 스파이크로 불필요한 알림 발생 가능")

    return issues
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 임계값을 추측으로 설정 | 알림이 너무 많거나 적음 | 실제 지표 분포를 보고 p95, p99 기준으로 설정 |
| 알림에 런북 링크 없음 | 알림 수신 후 무엇을 해야 할지 모름 | 모든 알림에 runbook URL 필수 포함 |
| 모든 알림을 동일 채널로 전송 | 중요한 알림이 노이즈에 묻힘 | severity별 채널 분리 (critical/warning) |
| `for` 없이 알림 설정 | 일시적 스파이크로 불필요한 호출 | 최소 2-5분 `for` 설정 |
| 비즈니스 지표 미측정 | 오류율은 낮아도 주문 건수가 0인 걸 모름 | 핵심 비즈니스 지표를 별도로 측정 |
| 알림 피로 방치 | 팀이 알림을 무시하기 시작 | 월간 알림 리뷰로 불필요한 알림 제거 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- **DevOps 101 (7/10): 모니터링과 알림 (현재 글)**
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [Prometheus 문서](https://prometheus.io/docs/)
- [Grafana 문서](https://grafana.com/docs/)
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
