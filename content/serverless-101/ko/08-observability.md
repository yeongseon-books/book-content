---
series: serverless-101
episode: 8
title: "Serverless 101 (8/10): 관측성"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Serverless
  - Observability
  - Logging
  - Tracing
  - Metrics
seo_description: 서버리스 관측성 전략, 구조화 로깅, 분산 추적, CloudWatch 알람 설정을 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (8/10): 관측성

서버리스 환경에서는 서버에 직접 SSH 접속해 로그를 보거나 프로세스 상태를 확인할 수 없습니다. 함수는 언제든지 다른 인스턴스에서 실행될 수 있고, 여러 서비스를 거쳐 요청이 처리됩니다. 이런 환경에서 문제를 발견하고 원인을 찾으려면 처음부터 관측 가능한 시스템으로 설계해야 합니다.

이 글은 Serverless 101 시리즈의 8번째 글입니다.

![Serverless 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/08/08-01-concept-at-a-glance.ko.png)
*Serverless 101 8장 흐름 개요*
> 관측성은 로그, 지표, 추적 세 가지 신호를 연결해서 볼 때 실현됩니다.

## 이 글에서 다룰 문제

- 서버리스에서 구조화 로깅은 왜 필수인가요?
- 분산 추적으로 요청 경로를 어떻게 따라갈 수 있을까요?
- 어떤 지표를 측정해야 의미 있는 알람을 만들 수 있을까요?
- 로그, 지표, 추적을 어떻게 연결해서 볼까요?
- CloudWatch와 X-Ray 설정의 실제 예시는 어떻게 될까요?

## 왜 관측성이 서버리스에서 더 중요한가

전통적인 서버 환경에서는 문제 발생 시 서버에 접속해 로그 파일을 직접 봅니다. 서버리스에서는 이 방법이 없습니다. 함수는 실행 후 사라지고, 로그는 CloudWatch에 비동기로 전송됩니다. 여러 함수가 연쇄적으로 실행되면 어느 단계에서 문제가 생겼는지 추적하기 어렵습니다.

그래서 서버리스 관측성은 사후 디버깅 도구가 아니라 시스템 설계의 일부입니다.

## 구조화 로깅

비정형 텍스트 로그는 CloudWatch Logs Insights로 분석하기 어렵습니다. JSON 형식의 구조화 로그를 사용하면 필드 기반 쿼리가 가능해집니다.

```python
import json
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Optional
import boto3


class StructuredLogger:
    """Lambda용 구조화 로거"""

    def __init__(self, function_name: str, function_version: str):
        self.function_name = function_name
        self.function_version = function_version
        self._correlation_id: Optional[str] = None

    def set_correlation_id(self, correlation_id: str) -> None:
        self._correlation_id = correlation_id

    def _base_fields(self) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "function_name": self.function_name,
            "function_version": self.function_version,
            "correlation_id": self._correlation_id,
        }

    def info(self, event: str, **kwargs) -> None:
        print(json.dumps({"level": "INFO", "event": event, **self._base_fields(), **kwargs}))

    def warning(self, event: str, **kwargs) -> None:
        print(json.dumps({"level": "WARNING", "event": event, **self._base_fields(), **kwargs}))

    def error(self, event: str, exc: Optional[Exception] = None, **kwargs) -> None:
        data = {"level": "ERROR", "event": event, **self._base_fields(), **kwargs}
        if exc:
            data["error"] = str(exc)
            data["error_type"] = type(exc).__name__
            data["traceback"] = traceback.format_exc()
        print(json.dumps(data))


# 전역 로거 초기화 (콜드 스타트 시 한 번)
import os
logger = StructuredLogger(
    function_name=os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "local"),
    function_version=os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", "local"),
)


def handler(event: dict, context: Any) -> dict:
    correlation_id = (
        event.get("headers", {}).get("x-correlation-id")
        or event.get("correlation_id")
        or context.aws_request_id
    )
    logger.set_correlation_id(correlation_id)

    start_time = time.perf_counter()
    logger.info("request_started", event_keys=list(event.keys()))

    try:
        result = process(event)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info("request_completed", duration_ms=duration_ms, status="success")
        return {"statusCode": 200, "body": json.dumps(result)}

    except ValueError as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning("validation_failed", error=str(e), duration_ms=duration_ms)
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error("request_failed", exc=e, duration_ms=duration_ms)
        raise


def process(event: dict) -> dict:
    return {"processed": True}
```

## CloudWatch Logs Insights 쿼리

구조화 로그를 활용하면 다음과 같은 운영 쿼리를 실행할 수 있습니다.

```sql
-- 최근 1시간 오류율 집계
fields @timestamp, level, event, error_type, correlation_id
| filter level = "ERROR"
| stats count() as error_count by error_type
| sort error_count desc
| limit 20
```

```sql
-- 요청별 실행 시간 분포 (p50, p95, p99)
fields @timestamp, duration_ms, correlation_id
| filter event = "request_completed"
| stats
    count() as request_count,
    avg(duration_ms) as avg_ms,
    pct(duration_ms, 50) as p50_ms,
    pct(duration_ms, 95) as p95_ms,
    pct(duration_ms, 99) as p99_ms
| sort @timestamp desc
```

```sql
-- 특정 상관관계 ID로 전체 요청 흐름 추적
fields @timestamp, level, event, function_name, duration_ms, error
| filter correlation_id = "req-abc123"
| sort @timestamp asc
```

## 커스텀 지표 발행

Lambda는 기본 지표(Duration, Invocations, Errors, Throttles)를 자동으로 수집합니다. 비즈니스 지표(주문 건수, 결제 성공률 등)는 직접 발행해야 합니다.

```python
import boto3
from datetime import datetime, timezone

cloudwatch = boto3.client("cloudwatch")

NAMESPACE = "OrderService/Lambda"


def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: dict = None) -> None:
    """CloudWatch 커스텀 지표 발행"""
    metric_data = {
        "MetricName": metric_name,
        "Value": value,
        "Unit": unit,
        "Timestamp": datetime.now(timezone.utc),
    }
    if dimensions:
        metric_data["Dimensions"] = [
            {"Name": k, "Value": v} for k, v in dimensions.items()
        ]

    cloudwatch.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[metric_data],
    )


def record_order_metrics(order: dict, processing_time_ms: float, success: bool) -> None:
    """주문 처리 지표 일괄 발행"""
    dims = {"Environment": os.environ.get("ENVIRONMENT", "unknown")}

    # 처리 건수
    put_metric("OrdersProcessed", 1, dimensions=dims)

    # 성공/실패 건수
    if success:
        put_metric("OrdersSucceeded", 1, dimensions=dims)
    else:
        put_metric("OrdersFailed", 1, dimensions=dims)

    # 처리 시간 (밀리초)
    put_metric("OrderProcessingTime", processing_time_ms, unit="Milliseconds", dimensions=dims)

    # 주문 금액
    put_metric("OrderAmount", float(order.get("amount", 0)), unit="None", dimensions=dims)
```

주의: CloudWatch API 호출 자체도 비용이 발생합니다. 매 요청마다 여러 지표를 개별 API 호출로 발행하면 비용이 커질 수 있습니다. EMF(Embedded Metrics Format)를 사용하면 로그와 지표를 함께 기록해 API 호출을 줄입니다.

## Embedded Metrics Format (EMF)

EMF는 CloudWatch가 인식하는 특수 JSON 형식으로, 로그를 통해 지표를 발행합니다.

```python
import json
import time
from datetime import datetime, timezone


def emit_emf(metrics: dict, dimensions: dict, namespace: str = "OrderService/Lambda") -> None:
    """Embedded Metrics Format으로 지표 발행"""
    emf = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": namespace,
                    "Dimensions": [list(dimensions.keys())],
                    "Metrics": [
                        {"Name": name, "Unit": unit}
                        for name, unit in metrics.items()
                    ],
                }
            ],
        },
        **dimensions,
        **{name: 0 for name in metrics},  # 기본값
    }
    print(json.dumps(emf))


def handler(event: dict, context) -> dict:
    start = time.perf_counter()

    try:
        result = process(event)
        duration = (time.perf_counter() - start) * 1000

        # EMF로 지표 발행 (CloudWatch API 호출 없음)
        print(json.dumps({
            "_aws": {
                "Timestamp": int(time.time() * 1000),
                "CloudWatchMetrics": [{
                    "Namespace": "OrderService",
                    "Dimensions": [["FunctionName", "Environment"]],
                    "Metrics": [
                        {"Name": "ProcessingTime", "Unit": "Milliseconds"},
                        {"Name": "OrdersProcessed", "Unit": "Count"},
                    ],
                }],
            },
            "FunctionName": context.function_name,
            "Environment": "prod",
            "ProcessingTime": round(duration, 2),
            "OrdersProcessed": 1,
        }))

        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        raise


def process(event: dict) -> dict:
    return {}
```

## CloudWatch 알람 설정

```yaml
Resources:
  ErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: order-processor-error-rate-high
      AlarmDescription: "오류율 5% 초과"
      Metrics:
        - Id: errors
          MetricStat:
            Metric:
              Namespace: AWS/Lambda
              MetricName: Errors
              Dimensions:
                - Name: FunctionName
                  Value: order-processor
            Period: 60
            Stat: Sum
        - Id: invocations
          MetricStat:
            Metric:
              Namespace: AWS/Lambda
              MetricName: Invocations
              Dimensions:
                - Name: FunctionName
                  Value: order-processor
            Period: 60
            Stat: Sum
        - Id: error_rate
          Expression: "errors / invocations * 100"
          Label: "ErrorRate"
      ComparisonOperator: GreaterThanThreshold
      Threshold: 5
      EvaluationPeriods: 3
      TreatMissingData: notBreaching
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"

  P99LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: order-processor-p99-latency
      MetricName: Duration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: order-processor
      ExtendedStatistic: p99
      Period: 60
      EvaluationPeriods: 5
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"
```

## X-Ray 분산 추적

X-Ray를 사용하면 Lambda 함수 간 호출과 AWS 서비스(DynamoDB, S3, SQS) 호출을 추적할 수 있습니다.

```python
from aws_xray_sdk.core import xray_recorder, patch_all

# 모든 boto3 클라이언트에 자동으로 X-Ray 세그먼트 추가
patch_all()

import boto3
import json

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


@xray_recorder.capture("process_order")
def process_order(order_id: str) -> dict:
    """X-Ray 세그먼트로 래핑된 처리 함수"""

    # 서브세그먼트로 세부 단계 추적
    with xray_recorder.in_subsegment("validate_order"):
        order = validate_order(order_id)

    with xray_recorder.in_subsegment("update_inventory"):
        update_inventory(order)

    # 메타데이터 추가
    xray_recorder.current_subsegment().put_metadata(
        "order_summary",
        {"order_id": order_id, "amount": order.get("amount")},
    )

    return order


def validate_order(order_id: str) -> dict:
    response = table.get_item(Key={"order_id": order_id})
    return response.get("Item", {})


def update_inventory(order: dict) -> None:
    pass


def handler(event: dict, context) -> dict:
    order_id = event.get("order_id")

    # 상관관계 ID를 X-Ray 어노테이션으로 추가 (검색 가능)
    xray_recorder.current_segment().put_annotation(
        "order_id", order_id
    )

    result = process_order(order_id)
    return {"statusCode": 200, "body": json.dumps(result)}
```

## 관측성 운영 런북

**오류율 알람 발생 시 대응 절차**

1. 오류 패턴 확인:
```bash
aws logs start-query \
  --log-group-name "/aws/lambda/order-processor" \
  --start-time $(date -d "30 minutes ago" +%s) \
  --end-time $(date +%s) \
  --query-string '
    fields error_type, error, correlation_id
    | filter level = "ERROR"
    | stats count() by error_type
    | sort count() desc
  '
```

2. 특정 요청 추적 (X-Ray 콘솔 또는 CLI):
```bash
aws xray get-service-graph \
  --start-time $(date -d "30 minutes ago" +%s) \
  --end-time $(date +%s)
```

3. 오류 비율과 시점 상관관계 분석: 배포 시점, 외부 서비스 장애, 트래픽 급증과 겹치는지 확인합니다.

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 비정형 텍스트 로그 사용 | Logs Insights 쿼리가 불가능하거나 복잡함 | 모든 로그를 JSON 구조로 출력 |
| 상관관계 ID 없음 | 분산 시스템에서 요청 추적 불가 | 입구 함수에서 ID 생성, 모든 로그와 이벤트에 전파 |
| 오류만 로깅, 정상도 로깅 안 함 | 정상 처리량 파악 불가, 오류율 계산 불가 | 성공/실패 모두 로깅하여 비율 계산 가능하게 |
| 평균 지연만 알람 | 콜드 스타트, 느린 요청을 놓침 | p95, p99 지표에 별도 알람 설정 |
| CloudWatch API로 매 요청마다 지표 발행 | API 호출 비용 증가 | EMF 사용으로 로그와 지표를 동시에 |
| X-Ray 미설정 | 서비스 간 지연 원인 파악 불가 | Lambda 함수에 X-Ray Active Tracing 활성화 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- **Serverless 101 (8/10): 관측성 (현재 글)**
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [OpenTelemetry 문서](https://opentelemetry.io/docs/)
- [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

### 패턴과 코드

- [서버리스 분산 추적](https://aws.amazon.com/blogs/compute/instrumenting-distributed-systems-for-operational-visibility/)
- [AWS Powertools for Lambda Python (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, Observability, Logging, Tracing, Metrics
