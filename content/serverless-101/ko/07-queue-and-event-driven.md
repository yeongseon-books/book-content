---
series: serverless-101
episode: 7
title: "Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처"
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
  - Queue
  - EventDriven
  - PubSub
  - Cloud
seo_description: 서버리스 환경에서 SQS, SNS, EventBridge를 활용한 이벤트 기반 아키텍처와 DLQ 운영 전략을 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처

서버리스 함수는 HTTP 요청에만 응답하는 것이 아닙니다. 큐에 쌓인 메시지, 다른 서비스가 발행한 이벤트, 스케줄에 따라 실행됩니다. 이 이벤트 기반 방식이 서버리스를 단순한 API 실행기 이상으로 만드는 핵심 설계 패턴입니다.

이 글은 Serverless 101 시리즈의 7번째 글입니다.

![Serverless 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/07/07-01-concept-at-a-glance.ko.png)
*Serverless 101 7장 흐름 개요*
> 큐는 생산자와 소비자 사이의 완충지대이며, 이벤트 버스는 발행자와 구독자를 느슨하게 연결하는 중재자입니다.

## 이 글에서 다룰 문제

- SQS, SNS, EventBridge는 각각 언제 써야 할까요?
- 팬아웃 패턴은 어떻게 구성할까요?
- 메시지 처리 실패 시 DLQ는 어떻게 운영해야 할까요?
- 이벤트 순서 보장이 필요할 때는 어떻게 할까요?
- 이벤트 기반 아키텍처에서 운영 가시성은 어떻게 확보할까요?

## 메시지 서비스 선택 기준

| 서비스 | 전달 보장 | 소비자 수 | 주요 용도 |
|--------|----------|----------|----------|
| SQS Standard | At-least-once | 단일 소비자 그룹 | 작업 큐, 비동기 처리 |
| SQS FIFO | Exactly-once | 단일 소비자 그룹 | 순서 보장 필요한 처리 |
| SNS | At-least-once | 여러 구독자 | 팬아웃, 알림 발송 |
| EventBridge | At-least-once | 여러 규칙별 타겟 | 서비스 간 이벤트 라우팅 |

실제로는 이 서비스들을 조합해서 씁니다. SNS로 팬아웃하고, 각 구독자로 SQS 큐를 연결하면 독립적인 처리 속도와 DLQ 관리가 가능합니다.

## SQS + Lambda 기본 패턴

```python
import json
import time
import boto3
from typing import Any

sqs = boto3.client("sqs")


def handler(event: dict, context: Any) -> dict:
    """SQS 이벤트 핸들러 - 부분 실패 지원"""
    failed_items = []

    for record in event["Records"]:
        message_id = record["messageId"]
        receipt_handle = record["receiptHandle"]

        try:
            body = json.loads(record["body"])

            # 메시지 타입에 따라 처리 분기
            event_type = body.get("event_type")
            if event_type == "order.created":
                process_new_order(body)
            elif event_type == "order.cancelled":
                process_cancellation(body)
            else:
                # 알 수 없는 타입은 DLQ로 보내지 않고 무시 (또는 별도 처리)
                print(json.dumps({
                    "event": "unknown_event_type",
                    "message_id": message_id,
                    "event_type": event_type,
                }))

        except Exception as e:
            print(json.dumps({
                "event": "message_processing_failed",
                "message_id": message_id,
                "error": str(e),
                "error_type": type(e).__name__,
            }))
            failed_items.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failed_items}


def process_new_order(body: dict) -> None:
    order_id = body["order_id"]
    print(json.dumps({"event": "processing_order", "order_id": order_id}))
    # 실제 처리 로직


def process_cancellation(body: dict) -> None:
    order_id = body["order_id"]
    print(json.dumps({"event": "cancelling_order", "order_id": order_id}))
```

## SNS 팬아웃 패턴

주문이 생성되면 여러 서비스가 동시에 처리해야 하는 경우 SNS 팬아웃을 사용합니다.

```yaml
Resources:
  # 이벤트 발행 토픽
  OrderEventsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: order-events

  # 재고 처리 큐
  InventoryQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-inventory-updates
      VisibilityTimeout: 300
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt InventoryDLQ.Arn
        maxReceiveCount: 3

  InventoryDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-inventory-updates-dlq
      MessageRetentionPeriod: 1209600

  # 알림 처리 큐
  NotificationQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-notifications
      VisibilityTimeout: 60
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt NotificationDLQ.Arn
        maxReceiveCount: 3

  NotificationDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: order-notifications-dlq

  # SNS -> SQS 구독 (필터링 포함)
  InventorySubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref OrderEventsTopic
      Protocol: sqs
      Endpoint: !GetAtt InventoryQueue.Arn
      FilterPolicy:
        event_type:
          - "order.created"
          - "order.cancelled"

  NotificationSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref OrderEventsTopic
      Protocol: sqs
      Endpoint: !GetAtt NotificationQueue.Arn
      FilterPolicy:
        event_type:
          - "order.created"
          - "order.shipped"
          - "order.delivered"

  # Lambda 함수들
  InventoryProcessor:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: inventory-processor
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt InventoryQueue.Arn
            BatchSize: 10
            FunctionResponseTypes:
              - ReportBatchItemFailures

  NotificationSender:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: notification-sender
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt NotificationQueue.Arn
            BatchSize: 5
            FunctionResponseTypes:
              - ReportBatchItemFailures
```

## 이벤트 발행 코드

```python
import json
import boto3
from datetime import datetime, timezone

sns = boto3.client("sns")
ORDER_EVENTS_TOPIC_ARN = "arn:aws:sns:ap-northeast-2:123456789012:order-events"


def publish_order_event(
    event_type: str,
    order_id: str,
    payload: dict,
    correlation_id: str,
) -> str:
    """주문 이벤트 발행"""
    message = {
        "event_type": event_type,
        "order_id": order_id,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    response = sns.publish(
        TopicArn=ORDER_EVENTS_TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes={
            "event_type": {
                "DataType": "String",
                "StringValue": event_type,
            },
            "order_id": {
                "DataType": "String",
                "StringValue": order_id,
            },
        },
    )

    print(json.dumps({
        "event": "event_published",
        "event_type": event_type,
        "order_id": order_id,
        "message_id": response["MessageId"],
        "correlation_id": correlation_id,
    }))

    return response["MessageId"]
```

## EventBridge로 서비스 간 이벤트 라우팅

EventBridge는 이벤트 소스와 타겟 사이를 규칙으로 연결합니다. 이벤트 패턴 매칭으로 특정 조건의 이벤트만 선택적으로 라우팅할 수 있습니다.

```yaml
Resources:
  OrderEventBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: order-event-bus

  # 고액 주문 알림 규칙
  HighValueOrderRule:
    Type: AWS::Events::Rule
    Properties:
      EventBusName: !Ref OrderEventBus
      EventPattern:
        source:
          - "order-service"
        detail-type:
          - "OrderCreated"
        detail:
          amount:
            numeric:
              - ">="
              - 100000   # 10만원 이상
      Targets:
        - Id: "HighValueOrderProcessor"
          Arn: !GetAtt HighValueOrderFunction.Arn

  # 해외 주문 별도 처리 규칙
  InternationalOrderRule:
    Type: AWS::Events::Rule
    Properties:
      EventBusName: !Ref OrderEventBus
      EventPattern:
        source:
          - "order-service"
        detail-type:
          - "OrderCreated"
        detail:
          shipping_country:
            - anything-but: "KR"
      Targets:
        - Id: "InternationalOrderProcessor"
          Arn: !GetAtt InternationalOrderFunction.Arn
```

```python
import boto3
import json
from datetime import datetime, timezone

events_client = boto3.client("events")


def emit_order_created(order: dict) -> None:
    """EventBridge로 주문 생성 이벤트 발행"""
    events_client.put_events(
        Entries=[
            {
                "EventBusName": "order-event-bus",
                "Source": "order-service",
                "DetailType": "OrderCreated",
                "Time": datetime.now(timezone.utc),
                "Detail": json.dumps({
                    "order_id": order["id"],
                    "user_id": order["user_id"],
                    "amount": order["amount"],
                    "shipping_country": order["shipping"]["country"],
                    "items": order["items"],
                }),
            }
        ]
    )
```

## DLQ 운영 전략

DLQ(Dead Letter Queue)는 처리에 실패한 메시지의 최종 착지점입니다. DLQ 모니터링과 재처리 절차를 갖추지 않으면 사라진 메시지가 데이터 손실로 이어집니다.

```python
import boto3
import json
from typing import Iterator

sqs = boto3.client("sqs")
DLQ_URL = "https://sqs.ap-northeast-2.amazonaws.com/123456789012/order-inventory-updates-dlq"
MAIN_QUEUE_URL = "https://sqs.ap-northeast-2.amazonaws.com/123456789012/order-inventory-updates"


def inspect_dlq(max_messages: int = 10) -> list[dict]:
    """DLQ 메시지 내용 확인 (삭제 없이 조회)"""
    messages = []
    response = sqs.receive_message(
        QueueUrl=DLQ_URL,
        MaxNumberOfMessages=min(max_messages, 10),
        VisibilityTimeout=30,
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
    )
    for msg in response.get("Messages", []):
        messages.append({
            "message_id": msg["MessageId"],
            "receipt_handle": msg["ReceiptHandle"],
            "body": json.loads(msg["Body"]),
            "approximate_receive_count": msg["Attributes"].get("ApproximateReceiveCount"),
            "sent_timestamp": msg["Attributes"].get("SentTimestamp"),
        })
    return messages


def redrive_from_dlq(receipt_handle: str) -> bool:
    """DLQ 메시지를 메인 큐로 재전송"""
    # 1. 메시지 읽기
    response = sqs.receive_message(
        QueueUrl=DLQ_URL,
        MaxNumberOfMessages=1,
        VisibilityTimeout=60,
    )
    messages = response.get("Messages", [])
    if not messages:
        return False

    msg = messages[0]
    # 2. 메인 큐로 전송
    sqs.send_message(
        QueueUrl=MAIN_QUEUE_URL,
        MessageBody=msg["Body"],
        MessageAttributes=msg.get("MessageAttributes", {}),
    )
    # 3. DLQ에서 삭제
    sqs.delete_message(
        QueueUrl=DLQ_URL,
        ReceiptHandle=msg["ReceiptHandle"],
    )
    print(json.dumps({"event": "dlq_message_redriven", "message_id": msg["MessageId"]}))
    return True
```

DLQ 알람 설정:

```yaml
Resources:
  InventoryDLQAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: inventory-dlq-messages-visible
      MetricName: ApproximateNumberOfMessagesVisible
      Namespace: AWS/SQS
      Dimensions:
        - Name: QueueName
          Value: order-inventory-updates-dlq
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"
```

## 이벤트 기반 아키텍처 운영 런북

**DLQ 메시지 발생 시 대응 절차**

1. DLQ 메시지 수 확인:
```bash
aws sqs get-queue-attributes \
  --queue-url <DLQ_URL> \
  --attribute-names ApproximateNumberOfMessages
```

2. 실패 원인 분석 (CloudWatch Logs 확인):
```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/inventory-processor" \
  --filter-pattern "message_processing_failed" \
  --start-time $(date -d "1 hour ago" +%s)000
```

3. 코드 버그인지 데이터 문제인지 구분:
   - 코드 버그: 수정 후 배포, DLQ 메시지 재처리
   - 데이터 문제: 해당 메시지 격리, 개별 수동 처리

4. 재처리:
```bash
# AWS 콘솔에서 DLQ Redrive 또는 위 Python 스크립트 실행
aws sqs start-message-move-task \
  --source-arn <DLQ_ARN> \
  --destination-arn <MAIN_QUEUE_ARN>
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| DLQ 미설정 | 처리 실패 메시지가 maxReceiveCount 초과 후 사라짐 | 모든 큐에 DLQ 필수 설정 |
| DLQ 알람 없음 | 메시지 유실을 모름 | DLQ의 `ApproximateNumberOfMessagesVisible` 알람 설정 |
| 배치 전체 실패 반환 | 성공 메시지 중복 재처리 | `ReportBatchItemFailures` 로 부분 실패 반환 |
| SNS 필터 없이 전체 구독 | 불필요한 메시지를 모든 구독자가 받아 처리 | `FilterPolicy`로 필요한 이벤트만 구독 |
| 가시성 타임아웃을 함수 타임아웃보다 짧게 설정 | 처리 중 메시지가 다시 가시화되어 중복 처리 | VisibilityTimeout = Lambda 타임아웃 × 6 |
| 이벤트 스키마 버전 관리 없음 | 이벤트 구조 변경 시 구독자 일괄 장애 | 이벤트에 `version` 필드 포함, 하위 호환 유지 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- **Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처 (현재 글)**
- [Serverless 101 (8/10): 관측성](./08-observability.md)
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [Amazon SQS 개발자 가이드](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Amazon SNS 개발자 가이드](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
- [Amazon EventBridge 개요](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)

### 패턴과 추가 읽을거리

- [이벤트 기반 아키텍처 - Martin Fowler](https://martinfowler.com/articles/201701-event-driven.html)
- [Serverless Patterns Collection](https://serverlessland.com/patterns)
- [AWS serverless samples (GitHub)](https://github.com/aws-samples/serverless-patterns)

Tags: Serverless, Queue, EventDriven, PubSub, Cloud
