---
series: devops-101
episode: 8
title: "DevOps 101 (8/10): 로그 수집과 분석"
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
  - Logging
  - Loki
  - ELK
  - Observability
seo_description: 구조화 로그 설계, Loki와 Promtail 설정, 로그 기반 알림 전략을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (8/10): 로그 수집과 분석

로그는 가장 원시적이지만 가장 유연한 관측 신호입니다. 하지만 비정형 텍스트 로그가 수십 기가바이트 쌓이면 검색도 분석도 어렵습니다. 구조화 로깅과 중앙 집중식 수집이 이 문제를 해결합니다.

이 글은 DevOps 101 시리즈의 여덟 번째 글입니다.

![DevOps 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/08/08-01-diagram.ko.png)
*DevOps 101 8장 흐름 개요*
> 로그는 무엇이 일어났는지 알려주고, 지표는 얼마나 자주 일어났는지 알려줍니다. 둘을 연결해야 전체 그림이 보입니다.

## 이 글에서 다룰 문제

- 비정형 로그와 구조화 로그의 차이는 무엇인가요?
- 로그에 반드시 포함해야 하는 필드는 무엇일까요?
- Loki와 ELK Stack 중 어떤 것을 선택할까요?
- 로그 기반 알림은 어떻게 설계할까요?

## 구조화 로깅

비정형 텍스트 로그는 grep으로는 찾을 수 있지만, 집계와 분석이 어렵습니다. JSON 형식의 구조화 로그를 사용하면 필드 기반 쿼리와 집계가 가능해집니다.

```python
# logging_config.py
import json
import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """JSON 구조화 로그 포매터"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 추가 필드 병합
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # 예외 정보
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """구조화 로거 생성"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

```python
# app_logging.py - 애플리케이션에서 사용
import structlog
import logging
from logging_config import get_logger

logger = get_logger("order-service")


class RequestContext:
    """요청 컨텍스트 추적"""

    def __init__(self, request_id: str, user_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self._start = time.perf_counter()

    def log(self, level: str, event: str, **kwargs):
        extra = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "elapsed_ms": round((time.perf_counter() - self._start) * 1000, 2),
            **kwargs,
        }
        getattr(logger, level)(event, extra=extra)


def process_order(order: dict, ctx: RequestContext) -> dict:
    ctx.log("info", "order_processing_started", order_id=order["id"])

    try:
        # 처리 로직
        result = {"order_id": order["id"], "status": "processed"}
        ctx.log("info", "order_processing_completed", order_id=order["id"], status="success")
        return result

    except Exception as e:
        ctx.log("error", "order_processing_failed", order_id=order["id"], error=str(e))
        raise
```

## 로그에 반드시 포함해야 하는 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| timestamp | ISO 8601 UTC 타임스탬프 | 2026-06-20T10:30:00.000Z |
| level | 로그 레벨 | INFO, WARNING, ERROR |
| request_id | 요청별 고유 ID (추적용) | req-abc123 |
| user_id | 사용자 식별자 | usr-456 |
| service | 서비스 이름 | order-service |
| event | 이벤트 이름 (분류 가능한 형태) | order_created, payment_failed |
| duration_ms | 처리 시간 (성능 분석용) | 145.3 |

## 로깅 플랫폼 선택

| 플랫폼 | 장점 | 단점 | 적합 상황 |
|--------|------|------|----------|
| Loki + Grafana | 경량, Prometheus와 통합, 저렴 | 전문 검색 기능 제한 | Grafana 스택 사용 팀 |
| ELK Stack | 강력한 검색, 성숙한 생태계 | 리소스 많이 필요, 복잡 | 대용량, 복잡한 쿼리 |
| CloudWatch Logs | AWS 통합, 관리형 | 비용 높음, 쿼리 언어 제한 | AWS 기반 소규모 팀 |
| Datadog | 올인원, 사용 쉬움 | 비용 매우 높음 | 예산 충분한 팀 |

## Loki + Promtail 설정

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod

    relabel_configs:
      # 로그 수집할 파드 선택 (어노테이션 기반)
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape_logs]
        action: keep
        regex: "true"

      # 레이블 추출
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app

    pipeline_stages:
      # JSON 파싱
      - json:
          expressions:
            level: level
            event: event
            request_id: request_id
            duration_ms: duration_ms

      # 레이블로 승격 (인덱싱)
      - labels:
          level:
          event:

      # 타임스탬프 추출
      - timestamp:
          source: timestamp
          format: RFC3339Nano
```

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: s3
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/index_cache
  aws:
    s3: s3://loki-logs-bucket/
    region: ap-northeast-2

limits_config:
  retention_period: 30d
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
```

## LogQL 쿼리 예제

```logql
# 최근 1시간 오류 로그
{app="order-service", namespace="production"}
  | json
  | level = "ERROR"
  | line_format "{{.timestamp}} {{.event}} {{.error}}"

# 오류율 집계 (지표화)
sum(rate({app="order-service"} | json | level="ERROR" [5m]))
/
sum(rate({app="order-service"} | json [5m]))
* 100

# 특정 주문 ID 추적
{app="order-service"}
  | json
  | request_id = "req-abc123"
  | line_format "{{.timestamp}} [{{.level}}] {{.event}}"

# p99 응답 시간 (로그에서 집계)
quantile_over_time(0.99,
  {app="order-service"} | json | unwrap duration_ms [5m]
) by (app)
```

## 로그 기반 알림 설정

```yaml
# Grafana 알림 규칙 (Loki)
apiVersion: 1
groups:
  - orgId: 1
    name: order-service-logs
    folder: Alerts
    interval: 1m
    rules:
      - uid: order-error-rate-log
        title: "주문 서비스 오류 로그 급증"
        condition: error_rate_condition
        data:
          - refId: error_count
            queryType: ""
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: loki
            model:
              expr: |
                sum(count_over_time({app="order-service"} | json | level="ERROR" [5m]))
              instant: true
              range: false

          - refId: error_rate_condition
            queryType: ""
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: __expr__
            model:
              conditions:
                - evaluator:
                    params: [10]
                    type: gt
                  operator:
                    type: and
                  query:
                    params: [error_count]
                  reducer:
                    params: []
                    type: last
                  type: query
              type: classic_conditions

        noDataState: OK
        execErrState: Alerting
        for: 2m
        annotations:
          description: "5분간 오류 로그 {{ $values.error_count }}건 발생"
          runbook: "https://wiki.example.com/runbooks/order-service-errors"
        labels:
          severity: warning
```

## 로그 보존 정책

```python
def calculate_log_cost(
    daily_log_gb: float,
    retention_days: int,
    cost_per_gb_ingest: float = 0.10,
    cost_per_gb_store: float = 0.03,
) -> dict:
    """로그 비용 추정"""
    monthly_ingest_gb = daily_log_gb * 30
    storage_gb = daily_log_gb * retention_days

    ingest_cost = monthly_ingest_gb * cost_per_gb_ingest
    storage_cost = storage_gb * cost_per_gb_store
    total_monthly = ingest_cost + storage_cost

    return {
        "daily_log_gb": daily_log_gb,
        "retention_days": retention_days,
        "monthly_ingest_gb": round(monthly_ingest_gb, 1),
        "storage_gb": round(storage_gb, 1),
        "ingest_cost_usd": round(ingest_cost, 2),
        "storage_cost_usd": round(storage_cost, 2),
        "total_monthly_usd": round(total_monthly, 2),
    }


# 환경별 보존 정책 권장
RETENTION_POLICY = {
    "dev": 7,        # 7일
    "stage": 14,     # 14일
    "prod": 90,      # 90일 (규정 준수 요건 확인)
    "audit": 365,    # 감사 로그는 1년
}
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 비정형 텍스트 로그만 사용 | 분석이 grep 수준에 머물고 집계 불가 | JSON 구조화 로그로 전환 |
| 로그에 request_id 없음 | 분산 환경에서 요청 추적 불가 | 모든 로그에 요청 ID 포함 |
| 로그 보존 기간 미설정 | 스토리지 비용이 계속 증가 | 환경별 보존 기간 설정 (dev: 7일, prod: 90일) |
| 민감 정보를 로그에 포함 | 로그 저장소에서 패스워드, 카드번호 노출 | 마스킹 처리 후 로깅 |
| 오류 레벨 남용 | 모든 것이 ERROR라 실제 오류를 찾기 어려움 | INFO/WARNING/ERROR 기준 명확화 |
| 로그와 지표를 연결 안 함 | 지표로 문제를 발견해도 로그에서 원인 찾기 어려움 | correlation_id로 지표와 로그 연결 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- **DevOps 101 (8/10): 로그 수집과 분석 (현재 글)**
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [Loki 문서](https://grafana.com/docs/loki/)
- [structlog (Python)](https://www.structlog.org/)
- [ELK Stack 가이드](https://www.elastic.co/guide/index.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
