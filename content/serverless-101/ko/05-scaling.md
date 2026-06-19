---
series: serverless-101
episode: 5
title: "Serverless 101 (5/10): 스케일링"
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
  - Scaling
  - Concurrency
  - Throttling
  - Cloud
seo_description: 서버리스 스케일링, 동시성, 버스트 한도, 예약 동시성, 백프레셔를 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (5/10): 스케일링

서버리스는 자주 "자동으로 무한 확장된다"는 말로 소개됩니다. 처음에는 맞는 말처럼 들리지만, 실무에서는 이 문장이 가장 위험한 오해가 되기도 합니다. 함수는 빠르게 늘어나도 데이터베이스와 외부 API, 연결 풀은 유한하기 때문입니다.

이 글은 Serverless 101 시리즈의 5번째 글입니다.

![Serverless 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/05/05-01-concept-at-a-glance.ko.png)
*Serverless 101 5장 흐름 개요*
> 서버리스는 같은 함수의 복사본을 더 많이 띄워 확장하므로, 확장 단위가 서버가 아닌 요청 한 건이고, 그 차이가 상태·제한·동시성에 대한 사고방식을 바꿉니다.

## 이 글에서 다룰 문제

- 서버리스의 동시성 모델은 어떻게 이해해야 할까요?
- 버스트와 지속 트래픽은 왜 다르게 봐야 할까요?
- 예약 동시성은 무엇을 보호하기 위한 장치일까요?
- 함수가 늘어날 때 다운스트림에 어떤 압력이 가해질까요?
- 백프레셔는 어떻게 구현해야 할까요?

## 왜 이 주제가 중요한가

서버리스의 강점은 확장 속도입니다. 트래픽이 몰리면 함수 인스턴스를 빠르게 늘릴 수 있습니다. 문제는 시스템 전체가 그 속도를 감당하지 못할 수 있다는 사실입니다. 함수가 열 배로 늘었는데 데이터베이스 연결 수는 그대로라면, 자동 확장은 성능 개선이 아니라 장애 가속기가 됩니다.

그래서 스케일링은 "얼마나 많이 늘릴 수 있는가"보다 "어디까지 늘리는 것이 안전한가"를 묻는 주제입니다.

## 동시성 모델 이해하기

Lambda의 동시성은 "동시에 처리 중인 요청 수"입니다. 요청 하나가 처리되는 동안 인스턴스 하나가 점유됩니다.

```
동시성 = 초당 요청 수 × 평균 실행 시간(초)

예시:
- 초당 100 요청, 평균 실행 시간 200ms
- 동시성 = 100 × 0.2 = 20 인스턴스
```

계정 기본 동시성 한도는 리전당 1,000입니다. 이 한도를 초과하면 스로틀링이 발생하고 호출이 `TooManyRequestsException`으로 실패합니다.

```python
import boto3
import json
from botocore.exceptions import ClientError

lambda_client = boto3.client("lambda")

def check_concurrency_headroom(function_name: str) -> dict:
    """현재 동시성 사용량과 여유 공간 확인"""

    # 계정 레벨 동시성 한도
    account_settings = lambda_client.get_account_settings()
    total_limit = account_settings["AccountLimit"]["ConcurrentExecutions"]
    unreserved = account_settings["AccountLimit"]["UnreservedConcurrentExecutions"]

    # 함수별 예약 동시성 확인
    try:
        config = lambda_client.get_function_concurrency(FunctionName=function_name)
        reserved = config.get("ReservedConcurrentExecutions", 0)
    except ClientError:
        reserved = 0

    return {
        "total_limit": total_limit,
        "unreserved_available": unreserved,
        "function_reserved": reserved,
        "headroom_pct": round((unreserved / total_limit) * 100, 1),
    }
```

## 버스트 한도와 초기 확장 속도

Lambda는 한 번에 무제한으로 늘어나지 않습니다. 버스트 시 초당 500개 인스턴스씩 늘어나는 제한이 있습니다(리전에 따라 다름).

| 리전 | 초기 버스트 한도 | 분당 확장 속도 |
|------|----------------|--------------|
| us-east-1 | 3,000 | +500/분 |
| us-west-2 | 3,000 | +500/분 |
| ap-northeast-1 | 1,000 | +500/분 |
| ap-northeast-2 | 500  | +500/분 |

트래픽이 갑자기 10배로 뛰는 상황에서 인스턴스가 따라잡기까지 몇 분이 걸릴 수 있습니다. 이 구간에서 스로틀링이 발생합니다.

## 예약 동시성으로 함수 격리

예약 동시성은 두 가지 목적으로 씁니다.

**1. 중요 함수 보호**: 결제 함수가 다른 함수의 트래픽 폭발로 인해 스로틀되는 것을 막습니다.

**2. 하위 서비스 보호**: 데이터베이스나 외부 API가 감당할 수 있는 최대 동시 요청 수를 넘지 않도록 제한합니다.

```yaml
# SAM 템플릿에서 예약 동시성 설정
Resources:
  PaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: payment-processor
      ReservedConcurrentExecutions: 50  # 최대 50개 인스턴스로 제한
      Environment:
        Variables:
          DB_MAX_CONNECTIONS: "10"  # RDS Proxy나 연결 풀 크기에 맞게 설정

  SearchFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: search-handler
      ReservedConcurrentExecutions: 200

  # 낮은 우선순위 배치 함수: 0으로 설정하면 실행 차단
  LowPriorityBatchFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: low-priority-batch
      ReservedConcurrentExecutions: 10
```

예약 동시성을 설정하면 그 수만큼 계정 전체 동시성 풀에서 빠져나갑니다. 너무 많은 함수에 예약 동시성을 설정하면 미예약 풀이 줄어들어 다른 함수가 스로틀될 수 있습니다.

## 백프레셔 패턴

함수가 다운스트림 서비스를 보호하려면 요청이 몰릴 때 스스로 속도를 조절해야 합니다. SQS와 함께 사용하면 자연스러운 백프레셔 메커니즘을 만들 수 있습니다.

```python
import boto3
import json
import time
from dataclasses import dataclass
from typing import Optional

sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")

@dataclass
class ProcessingResult:
    success: bool
    item_id: str
    error: Optional[str] = None


def handler(event, context):
    """SQS 트리거 핸들러 - 배치 처리 + 부분 실패 지원"""
    results = []
    failed_items = []

    for record in event["Records"]:
        item_id = None
        try:
            body = json.loads(record["body"])
            item_id = body["id"]

            # 처리 전 다운스트림 헬스 확인
            if not check_downstream_health():
                # 재처리를 위해 메시지를 큐에 남김 (가시성 타임아웃 초과 대기)
                failed_items.append({
                    "itemIdentifier": record["messageId"]
                })
                continue

            result = process_item(body)
            results.append(ProcessingResult(success=True, item_id=item_id))

        except Exception as e:
            failed_items.append({
                "itemIdentifier": record["messageId"]
            })
            print(json.dumps({
                "event": "processing_failed",
                "item_id": item_id,
                "error": str(e),
            }))

    print(json.dumps({
        "event": "batch_complete",
        "total": len(event["Records"]),
        "succeeded": len(results),
        "failed": len(failed_items),
    }))

    # 부분 실패 응답: Lambda가 실패 메시지만 재처리
    return {"batchItemFailures": failed_items}


def check_downstream_health() -> bool:
    """다운스트림 서비스 상태 확인"""
    # 간단한 연결 확인 또는 Circuit Breaker 패턴
    return True


def process_item(body: dict) -> dict:
    return {"processed": body["id"]}
```

## SQS 기반 스케일링 제어

SQS에서 Lambda를 트리거할 때 배치 크기와 최대 동시성으로 처리 속도를 제어합니다.

```yaml
Resources:
  OrderQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-processing-queue
      VisibilityTimeout: 300        # 함수 타임아웃보다 6배 이상 크게 설정
      MessageRetentionPeriod: 86400 # 24시간
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt OrderDLQ.Arn
        maxReceiveCount: 3

  OrderDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-processing-dlq
      MessageRetentionPeriod: 1209600  # 14일

  OrderProcessor:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: order-processor
      ReservedConcurrentExecutions: 30  # DB 연결 풀 크기 기준
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt OrderQueue.Arn
            BatchSize: 10
            MaximumBatchingWindowInSeconds: 5
            FunctionResponseTypes:
              - ReportBatchItemFailures
            ScalingConfig:
              MaximumConcurrency: 30  # 예약 동시성과 일치시킴
```

## 데이터베이스 연결 문제와 RDS Proxy

Lambda가 확장되면 각 인스턴스가 독립적인 DB 연결을 시도합니다. RDS는 연결 수에 제한이 있어 수백 개의 Lambda 인스턴스가 동시에 연결하면 연결 풀이 고갈됩니다.

```python
import os
import boto3
import pymysql
from contextlib import contextmanager

# RDS Proxy 엔드포인트 사용 시 연결 풀 관리를 Proxy에 위임
DB_HOST = os.environ.get("DB_HOST")  # RDS Proxy 엔드포인트
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")

_connection = None


def get_connection():
    global _connection
    try:
        if _connection and _connection.open:
            _connection.ping(reconnect=True)
            return _connection
    except Exception:
        pass

    _connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=get_db_password(),
        database=DB_NAME,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )
    return _connection


def get_db_password() -> str:
    """Secrets Manager에서 DB 패스워드 조회"""
    secrets_client = boto3.client("secretsmanager")
    response = secrets_client.get_secret_value(
        SecretId=os.environ["DB_SECRET_ARN"]
    )
    import json
    secret = json.loads(response["SecretString"])
    return secret["password"]


@contextmanager
def db_transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

RDS Proxy를 사용하면 Lambda 인스턴스 수가 늘어도 RDS는 Proxy로부터 제한된 수의 연결만 받습니다. RDS Proxy가 연결을 다중화해 줍니다.

## 스로틀링 모니터링

```yaml
Resources:
  ThrottleAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: order-processor-throttles-high
      MetricName: Throttles
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: order-processor
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"

  ConcurrencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: order-processor-concurrency-near-limit
      MetricName: ConcurrentExecutions
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: order-processor
      Statistic: Maximum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 27    # 예약 동시성 30의 90%
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"
```

## 스케일링 이슈 진단 런북

**1단계: 스로틀 발생 확인**

```bash
# 최근 15분 스로틀 건수 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=order-processor \
  --start-time $(date -u -d "15 minutes ago" +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Sum
```

**2단계: 현재 동시성 확인**

```bash
# 계정 동시성 현황
aws lambda get-account-settings \
  --query 'AccountLimit.{Total:ConcurrentExecutions,Unreserved:UnreservedConcurrentExecutions}'

# 함수별 예약 동시성
aws lambda list-functions \
  --query 'Functions[].FunctionName' \
  --output text | tr '\t' '\n' | while read fn; do
    reserved=$(aws lambda get-function-concurrency \
      --function-name "$fn" \
      --query 'ReservedConcurrentExecutions' 2>/dev/null || echo 0)
    echo "$fn: $reserved"
  done
```

**3단계: 원인 판별**

- 스로틀이 계속되면: 예약 동시성 한도 증가 또는 계정 한도 증가 요청 검토
- DB 오류가 함께 발생하면: RDS Proxy 설정 및 연결 풀 크기 검토
- 특정 시간대에만 발생하면: Auto Scaling 또는 예약 동시성 스케줄 설정 검토

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| "서버리스는 무한 확장" 믿음 | 갑작스러운 스로틀, DB 연결 고갈 | 동시성 한도와 다운스트림 제한을 함께 설계 |
| 예약 동시성 미설정 | 중요 함수가 낮은 우선순위 함수에 밀려 스로틀 | 중요 경로에 예약 동시성 명시적 할당 |
| DB 연결을 함수 내부에서 직접 관리 | 인스턴스 증가 시 연결 고갈 | RDS Proxy 또는 연결 풀러 사용 |
| SQS 배치 실패 전체 재처리 | 성공한 메시지가 중복 처리됨 | `ReportBatchItemFailures` 설정으로 부분 재처리 |
| 버스트 속도 무시 | 급격한 트래픽 증가 시 처음 수 분간 스로틀 | 큐 버퍼링으로 트래픽 평탄화 |
| 스로틀 알람 없음 | 장애 후에야 스로틀 발생 사실 인지 | Throttles 지표에 실시간 알람 설정 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- **Serverless 101 (5/10): 스케일링 (현재 글)**
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- [Serverless 101 (8/10): 관측성](./08-observability.md)
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [Lambda 동시성](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [Reserved/Provisioned concurrency](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)
- [Amazon SQS 개발자 가이드](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Lambda 스로틀링과 스케일링](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html)

### 패턴과 코드

- [RDS Proxy for Lambda](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html)
- [Lambda SQS 이벤트 소스 매핑](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)

Tags: Serverless, Scaling, Concurrency, Throttling, Cloud
