---
series: serverless-101
episode: 6
title: "Serverless 101 (6/10): 상태 관리"
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
  - State
  - Database
  - Cache
  - Cloud
seo_description: 서버리스 상태 관리 전략, DynamoDB 멱등성, TTL, 세션 캐시, Step Functions 워크플로를 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (6/10): 상태 관리

서버리스 함수는 기본적으로 무상태입니다. 인스턴스가 재사용될 수도 있고, 다른 인스턴스가 다음 요청을 받을 수도 있습니다. 이 특성은 확장이 쉬워지는 이점이 있지만, 동시에 상태를 어디에 어떻게 저장할지를 설계 초기에 명확히 정해야 한다는 의미이기도 합니다.

이 글은 Serverless 101 시리즈의 6번째 글입니다.

![Serverless 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/06/06-01-concept-at-a-glance.ko.png)
*Serverless 101 6장 흐름 개요*
> 함수는 상태를 소유하는 주체가 아니라 상태를 읽고 갱신하는 작업자입니다.

## 이 글에서 다룰 문제

- 서버리스 함수에서 상태는 어디에 두어야 할까요?
- 세션, 캐시, 데이터 저장소, 워크플로 상태는 어디에 둬야 할까요?
- TTL과 멱등 토큰은 왜 상태 관리의 핵심일까요?
- 분산 환경에서 중복 처리를 어떻게 막을 수 있을까요?
- 여러 단계로 이어지는 상태 흐름은 어떻게 관리할까요?

## 왜 이 주제가 중요한가

"서버리스는 무상태"라는 말을 들으면 상태를 생각하지 않아도 된다고 오해하기 쉽습니다. 하지만 실제로는 반대입니다. 인스턴스가 언제든 교체될 수 있으므로, 어떤 상태가 어디에 저장되어야 하는지를 코드가 아닌 아키텍처 수준에서 설계해야 합니다.

함수 내부 메모리에 상태를 두면 다른 인스턴스가 그 값을 볼 수 없습니다. 외부 저장소 없이 세션을 구현하거나 중간 결과를 추적하면 재처리나 장애 복구 시 데이터가 유실됩니다.

## 상태 유형별 저장소 선택

| 상태 유형 | 예시 | 권장 저장소 | 이유 |
|-----------|------|------------|------|
| 짧은 세션 (수 분~수 시간) | 로그인 세션, 인증 토큰 | ElastiCache (Redis) | 빠른 읽기, TTL 지원 |
| 영속 데이터 | 주문, 사용자 정보 | DynamoDB, RDS | 내구성, 쿼리 유연성 |
| 워크플로 진행 상태 | 다단계 승인, 처리 파이프라인 | Step Functions | 단계 추적, 재시도, 타임아웃 |
| 임시 집계 결과 | 카운터, 점수 | ElastiCache (Redis) | 원자적 증가 연산 |
| 대용량 파일 | 이미지, 문서 | S3 | 대용량, 지속성 |

## DynamoDB로 멱등성 구현

분산 환경에서 같은 이벤트가 두 번 처리되는 것은 흔한 문제입니다. SQS의 at-least-once 전달 보장은 중복 메시지 가능성을 내포합니다. 멱등 키를 DynamoDB에 저장해 중복 처리를 막을 수 있습니다.

```python
import json
import time
import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from typing import Optional

dynamodb = boto3.resource("dynamodb")
_idempotency_table = dynamodb.Table("idempotency-store")


@dataclass
class IdempotencyRecord:
    key: str
    status: str      # "in_progress" | "completed" | "failed"
    result: Optional[dict]
    created_at: int
    ttl: int         # Unix timestamp - DynamoDB TTL로 자동 삭제


def idempotent_handler(event, context):
    """멱등성을 보장하는 핸들러 래퍼"""
    idempotency_key = event.get("idempotency_key") or context.aws_request_id
    now = int(time.time())
    ttl = now + 86400  # 24시간 후 만료

    # 1. 기존 처리 결과 확인
    try:
        response = _idempotency_table.get_item(
            Key={"pk": f"idem#{idempotency_key}"},
        )
        if "Item" in response:
            item = response["Item"]
            if item["status"] == "completed":
                print(json.dumps({
                    "event": "idempotency_hit",
                    "key": idempotency_key,
                    "cached_result": item.get("result"),
                }))
                return item["result"]
            elif item["status"] == "in_progress":
                raise RuntimeError(f"Processing already in progress for {idempotency_key}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    # 2. 처리 시작 - 조건부 쓰기로 경쟁 방지
    try:
        _idempotency_table.put_item(
            Item={
                "pk": f"idem#{idempotency_key}",
                "status": "in_progress",
                "created_at": now,
                "ttl": ttl,
            },
            ConditionExpression="attribute_not_exists(pk)",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise RuntimeError("Concurrent processing detected")
        raise

    # 3. 실제 처리
    try:
        result = process_order(event)

        # 4. 완료 기록
        _idempotency_table.update_item(
            Key={"pk": f"idem#{idempotency_key}"},
            UpdateExpression="SET #status = :s, #result = :r",
            ExpressionAttributeNames={"#status": "status", "#result": "result"},
            ExpressionAttributeValues={":s": "completed", ":r": result},
        )
        return result

    except Exception as e:
        # 5. 실패 기록 (재처리 허용을 위해 삭제)
        _idempotency_table.delete_item(
            Key={"pk": f"idem#{idempotency_key}"}
        )
        raise


def process_order(event: dict) -> dict:
    """실제 주문 처리 로직"""
    return {"order_id": event.get("order_id"), "status": "processed"}
```

## DynamoDB TTL로 세션 관리

```python
import json
import time
import secrets
import boto3
from typing import Optional

dynamodb = boto3.resource("dynamodb")
_session_table = dynamodb.Table("user-sessions")

SESSION_TTL_SECONDS = 3600  # 1시간


def create_session(user_id: str, metadata: dict) -> str:
    """새 세션 생성 후 세션 ID 반환"""
    session_id = secrets.token_urlsafe(32)
    now = int(time.time())

    _session_table.put_item(
        Item={
            "pk": f"session#{session_id}",
            "user_id": user_id,
            "metadata": metadata,
            "created_at": now,
            "last_accessed": now,
            "ttl": now + SESSION_TTL_SECONDS,
        }
    )
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """세션 조회 및 TTL 갱신"""
    response = _session_table.get_item(
        Key={"pk": f"session#{session_id}"},
    )
    item = response.get("Item")
    if not item:
        return None

    now = int(time.time())
    if item["ttl"] < now:
        return None  # 만료됨 (DynamoDB TTL이 아직 삭제 안 했을 수 있음)

    # 슬라이딩 TTL 갱신
    _session_table.update_item(
        Key={"pk": f"session#{session_id}"},
        UpdateExpression="SET last_accessed = :t, #ttl = :ttl",
        ExpressionAttributeNames={"#ttl": "ttl"},
        ExpressionAttributeValues={
            ":t": now,
            ":ttl": now + SESSION_TTL_SECONDS,
        },
    )
    return item


def invalidate_session(session_id: str) -> None:
    """로그아웃 시 세션 삭제"""
    _session_table.delete_item(
        Key={"pk": f"session#{session_id}"}
    )
```

## 낙관적 잠금으로 동시성 충돌 방지

여러 함수 인스턴스가 같은 항목을 동시에 수정하려 할 때 낙관적 잠금으로 충돌을 감지합니다.

```python
from botocore.exceptions import ClientError


def update_inventory(product_id: str, quantity_delta: int, max_retries: int = 3) -> dict:
    """재고 수량 업데이트 - 낙관적 잠금 사용"""
    table = dynamodb.Table("inventory")

    for attempt in range(max_retries):
        # 현재 값과 버전 읽기
        response = table.get_item(Key={"product_id": product_id})
        item = response.get("Item")
        if not item:
            raise ValueError(f"Product {product_id} not found")

        current_version = item["version"]
        current_quantity = item["quantity"]
        new_quantity = current_quantity + quantity_delta

        if new_quantity < 0:
            raise ValueError("Insufficient inventory")

        try:
            # 버전이 읽었을 때와 같은 경우에만 업데이트
            table.update_item(
                Key={"product_id": product_id},
                UpdateExpression="SET quantity = :q, version = :v",
                ConditionExpression="version = :cv",
                ExpressionAttributeValues={
                    ":q": new_quantity,
                    ":v": current_version + 1,
                    ":cv": current_version,
                },
            )
            return {"product_id": product_id, "new_quantity": new_quantity}

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                if attempt == max_retries - 1:
                    raise RuntimeError("Update failed after max retries due to concurrent modifications")
                time.sleep(0.1 * (2 ** attempt))  # 지수 백오프
                continue
            raise

    raise RuntimeError("Update failed")
```

## Step Functions으로 워크플로 상태 관리

여러 단계를 거치는 처리 흐름은 함수 내부에서 관리하면 재시도와 오류 처리가 복잡해집니다. Step Functions에 상태 머신을 위임하면 각 함수는 단일 단계만 담당합니다.

```yaml
# Step Functions 상태 머신 정의 (ASL)
OrderProcessingStateMachine:
  Type: AWS::StepFunctions::StateMachine
  Properties:
    StateMachineName: order-processing
    Definition:
      Comment: "주문 처리 워크플로"
      StartAt: ValidateOrder
      States:
        ValidateOrder:
          Type: Task
          Resource: !GetAtt ValidateOrderFunction.Arn
          Retry:
            - ErrorEquals: ["Lambda.ServiceException", "Lambda.AWSLambdaException"]
              IntervalSeconds: 2
              MaxAttempts: 3
              BackoffRate: 2
          Catch:
            - ErrorEquals: ["ValidationError"]
              Next: OrderFailed
          Next: ReserveInventory

        ReserveInventory:
          Type: Task
          Resource: !GetAtt ReserveInventoryFunction.Arn
          TimeoutSeconds: 30
          Catch:
            - ErrorEquals: ["InsufficientInventory"]
              Next: OrderFailed
          Next: ProcessPayment

        ProcessPayment:
          Type: Task
          Resource: !GetAtt ProcessPaymentFunction.Arn
          TimeoutSeconds: 60
          Catch:
            - ErrorEquals: ["PaymentDeclined"]
              Next: ReleaseInventory
          Next: SendConfirmation

        SendConfirmation:
          Type: Task
          Resource: !GetAtt SendConfirmationFunction.Arn
          End: true

        ReleaseInventory:
          Type: Task
          Resource: !GetAtt ReleaseInventoryFunction.Arn
          Next: OrderFailed

        OrderFailed:
          Type: Fail
          Error: "OrderProcessingFailed"
```

## 상태 관리 런북

**세션 만료 관련 장애 대응**

1. 증상 확인: 사용자가 갑자기 로그아웃되거나 세션을 찾을 수 없다는 오류 발생
2. DynamoDB TTL 설정 확인:
```bash
aws dynamodb describe-table \
  --table-name user-sessions \
  --query 'Table.TimeToLiveDescription'
```
3. 세션 TTL 값 직접 확인:
```bash
aws dynamodb get-item \
  --table-name user-sessions \
  --key '{"pk": {"S": "session#<SESSION_ID>"}}'
```
4. TTL 컬럼이 과거 시각이면 DynamoDB가 아직 삭제하지 않은 만료 항목입니다. 애플리케이션 레이어에서 TTL 비교 로직을 추가합니다.

**멱등성 테이블 크기 증가 대응**

1. 멱등성 레코드에 TTL을 설정했는지 확인합니다.
2. TTL이 없으면 레코드가 무한 누적됩니다.
3. 기존 레코드에 TTL 일괄 추가:
```python
def backfill_ttl(table_name: str, ttl_seconds: int = 86400):
    table = dynamodb.Table(table_name)
    now = int(time.time())
    scan_kwargs = {}
    while True:
        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            if "ttl" not in item:
                table.update_item(
                    Key={"pk": item["pk"]},
                    UpdateExpression="SET #ttl = :t",
                    ExpressionAttributeNames={"#ttl": "ttl"},
                    ExpressionAttributeValues={":t": now + ttl_seconds},
                )
        if "LastEvaluatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 핸들러 전역 변수에 요청별 데이터 저장 | 인스턴스 재사용 시 다른 사용자 데이터 노출 | 요청별 데이터는 핸들러 내부 지역 변수로 관리 |
| TTL 없이 DynamoDB에 임시 데이터 저장 | 테이블 무한 증가, 비용 상승 | TTL 속성 필수 설정 |
| 멱등성 없이 SQS 메시지 처리 | 중복 처리로 데이터 오염 | 멱등 키 + 조건부 쓰기 패턴 사용 |
| 다단계 처리를 단일 함수에서 관리 | 중간 실패 시 전체 재처리, 타임아웃 위험 | Step Functions으로 워크플로 분리 |
| 낙관적 잠금 없이 동시 업데이트 | 재고 음수, 데이터 불일치 | 버전 기반 조건부 업데이트 사용 |
| 세션을 함수 메모리에 저장 | 다른 인스턴스에서 세션 인식 불가 | ElastiCache 또는 DynamoDB에 저장 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- **Serverless 101 (6/10): 상태 관리 (현재 글)**
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- [Serverless 101 (8/10): 관측성](./08-observability.md)
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [DynamoDB 단일 테이블 설계](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-modeling-nosql-B.html)
- [ElastiCache 개요](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)
- [Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)

### 패턴과 코드

- [멱등성 패턴](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/idempotency.html)
- [AWS Powertools for Lambda Python (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, State, Database, Cache, Cloud
