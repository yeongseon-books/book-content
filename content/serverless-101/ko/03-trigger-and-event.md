---
series: serverless-101
episode: 3
title: "Serverless 101 (3/10): 트리거와 이벤트"
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
  - Trigger
  - Event
  - EventDriven
  - Cloud
seo_description: HTTP 요청에서 큐 소비, 멱등성, DLQ, 재처리까지 이어지는 실제 트리거 흐름을 예제로 설명합니다
last_reviewed: '2026-05-16'
---

# Serverless 101 (3/10): 트리거와 이벤트

서버리스 함수는 스스로 실행되지 않습니다. 누가 함수를 깨우는지, 같은 이벤트가 다시 들어오면 무엇이 달라지는지, 반복 실패 메시지는 어디로 가는지를 이해하지 못하면 함수 본문이 아무리 깔끔해도 운영은 빠르게 흔들립니다.

이 글은 Serverless 101 시리즈의 3번째 글입니다.

그래서 이번 글은 이벤트 분류표만 나열하지 않습니다. 대신 하나의 운영 흐름을 끝까지 따라가 보겠습니다. **HTTP 요청이 큐 메시지로 바뀌고, 소비자가 이를 처리하고, 중복 메시지는 멱등성 저장소에서 건너뛰고, 반복 실패 메시지는 DLQ로 보내고, 운영자는 그 메시지를 다시 재처리하는 흐름**입니다. 이 한 흐름을 이해하면 트리거 이야기가 더 이상 추상적이지 않습니다.

![Serverless 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/03/03-01-concept-at-a-glance.ko.png)
*Serverless 101 3장 흐름 개요*
> Trigger는 함수를 깨우는 사건이고 Event는 그 사건이 가져오는 데이터입니다 — 서버리스 코드의 입력은 이 둘로만 들어옵니다.

## 먼저 던지는 질문

- HTTP, 큐, 스케줄 트리거는 호출 의미가 어떻게 다를까요?
- 비동기 소비자에서는 왜 멱등성이 기본 전제가 될까요?
- DLQ는 단순한 보조 기능이 아니라 왜 운영의 핵심 관찰 지점일까요?

## 왜 이 주제가 중요한가

입문자는 함수 코드에 먼저 시선이 갑니다. 하지만 실무에서 더 큰 문제를 만드는 것은 종종 함수 본문이 아니라 **호출 계약**입니다. HTTP 요청은 지연 시간과 사용자 응답이 핵심이고, 큐 메시지는 중복 처리와 재시도가 핵심이며, 스케줄 트리거는 실행 겹침과 재진입성이 핵심입니다.

이 차이를 무시하면 로컬에서는 그럴듯해 보이는 코드가 운영에서 무너지기 쉽습니다. 한 번만 실행하면 잘 돌아가는 함수라도, 실제 환경에서는 네트워크 지연, 배치 전달, at-least-once 재전달, 순서 뒤바뀜, 독성 메시지(poison message)가 동시에 들어오기 때문입니다.

## 한눈에 보는 구조

이 그림에서 운영상 중요한 것은 역할 분리입니다. HTTP 엔드포인트는 요청을 받고, 큐는 비동기 경계를 만들고, 소비자는 실제 작업을 수행하고, DLQ는 반복 실패 메시지를 격리합니다. 문제 해결도 같은 순서로 좁혀 가야 합니다.

## 이번 글의 예제 시나리오

이번 글도 같은 주문 예제를 이어 갑니다. 시나리오는 아래와 같습니다.

1. HTTP 요청이 `/orders`로 들어옵니다.
2. 요청 핸들러는 검증 후 큐에 메시지를 넣고 `202 Accepted`를 반환합니다.
3. 큐 소비자는 메시지를 읽고, `idempotency_key`를 외부 저장소에 기록한 뒤 주문 후처리를 수행합니다.
4. 같은 메시지가 다시 오면 소비자는 중복 처리를 건너뜁니다.
5. 반복 실패 메시지는 DLQ 이벤트로 바꿔 저장하고, 운영자는 그 페이로드를 기준으로 재처리합니다.

여기서 핵심은 “함수 하나가 모든 것을 처리한다”가 아닙니다. **동기 경계와 비동기 경계, 성공 경로와 실패 경로를 분리한다**는 점입니다.

## 하이퍼텍스트요청에서 큐 소비와 멱등 처리까지의 워크플로

아래 예제는 학습용으로 파일 하나에 모았지만, 실제 운영에서는 HTTP 핸들러와 소비자 핸들러를 보통 별도 함수로 분리합니다.

```python
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

DB_PATH = "idempotency.db"

def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }

def init_store() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_messages (
                idempotency_key TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL,
                order_id TEXT NOT NULL
            )
            """
        )

def already_processed(idempotency_key: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM processed_messages WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
    return row is not None

def mark_processed(idempotency_key: str, order_id: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO processed_messages VALUES (?, ?, ?)",
            (idempotency_key, datetime.now(UTC).isoformat(), order_id),
        )
        conn.commit()

@dataclass
class QueueMessage:
    message_id: str
    retry_count: int
    body: dict

QUEUE: list[QueueMessage] = []
DLQ: list[dict] = []

def http_ingress_handler(event: dict, context) -> dict:
    payload = json.loads(event.get("body") or "{}")
    order_id = payload.get("order_id")
    items = payload.get("items", [])

    if not order_id or not items:
        return build_response(400, {"ok": False, "error": "invalid order payload"})

    message = QueueMessage(
        message_id=f"msg-{order_id}",
        retry_count=0,
        body={
            "order_id": order_id,
            "items": items,
            "idempotency_key": payload.get("idempotency_key", f"order:{order_id}"),
        },
    )
    QUEUE.append(message)

    return build_response(
        202,
        {
            "ok": True,
            "order_id": order_id,
            "queued": True,
            "message_id": message.message_id,
        },
    )

def apply_fulfillment(order_id: str, items: list[dict]) -> None:
    if any(item["sku"] == "poison-pill" for item in items):
        raise RuntimeError("downstream inventory reservation failed")

def send_to_dlq(message: QueueMessage, error: Exception) -> None:
    DLQ.append(
        {
            "message_id": message.message_id,
            "order_id": message.body["order_id"],
            "idempotency_key": message.body["idempotency_key"],
            "retry_count": message.retry_count,
            "error": str(error),
            "failed_at": datetime.now(UTC).isoformat(),
        }
    )

def queue_consumer_handler(event: dict, context) -> dict:
    processed = []
    skipped = []
    failed = []

    for record in event["records"]:
        message = QueueMessage(**record)
        key = message.body["idempotency_key"]
        order_id = message.body["order_id"]

        if already_processed(key):
            skipped.append({"message_id": message.message_id, "reason": "duplicate"})
            continue

        try:
            apply_fulfillment(order_id, message.body["items"])
            mark_processed(key, order_id)
            processed.append({"message_id": message.message_id, "order_id": order_id})
        except Exception as exc:
            message.retry_count += 1
            if message.retry_count >= 3:
                send_to_dlq(message, exc)
                failed.append({"message_id": message.message_id, "sent_to": "dlq"})
            else:
                QUEUE.append(message)
                failed.append({"message_id": message.message_id, "sent_to": "retry-queue"})

    return {
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
    }
```

이 예제는 세 가지를 동시에 보여 줍니다.

- HTTP 핸들러는 빠르게 `202 Accepted`를 반환하고, 실제 작업은 큐 뒤로 넘깁니다.
- 멱등성은 메모리 집합이 아니라 외부 저장소 계약으로 처리합니다. 여기서는 SQLite로 시뮬레이션했지만, 실제 운영에서는 DynamoDB, Redis, Cloud SQL 같은 관리형 저장소를 둡니다.
- DLQ는 “에러를 숨기는 곳”이 아니라 재처리 가능한 실패 페이로드를 남기는 곳입니다.

## 기대 결과 세 가지

### 1) 첫 번째 정상 소비

HTTP 요청 예시는 아래처럼 둘 수 있습니다.

```python
http_event = {
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "idempotency_key": "order:ord-1001",
            "items": [{"sku": "keyboard", "quantity": 1}],
        }
    )
}
```

먼저 `http_ingress_handler(http_event, None)`를 실행하고, 그 뒤 큐 메시지를 소비하면 기대 결과는 아래와 같습니다.

```json
{
  "processed": [
    {
      "message_id": "msg-ord-1001",
      "order_id": "ord-1001"
    }
  ],
  "skipped": [],
  "failed": []
}
```

### 2) 같은 메시지가 다시 들어온 경우

같은 `idempotency_key`로 한 번 더 소비하면 기대 결과는 아래처럼 바뀝니다.

```json
{
  "processed": [],
  "skipped": [
    {
      "message_id": "msg-ord-1001",
      "reason": "duplicate"
    }
  ],
  "failed": []
}
```

여기서 핵심은 “재시도가 일어나지 않는다”가 아닙니다. 핵심은 **재시도가 일어나도 중복 부작용이 없게 만든다**는 것입니다.

### 3) 독성 메시지가 실패대기열로 가는 경우

`sku`가 `poison-pill`인 메시지는 의도적으로 실패하게 만들었습니다. 세 번째 시도까지 실패하면 결과는 아래처럼 남습니다.

```json
{
  "message_id": "msg-ord-9999",
  "order_id": "ord-9999",
  "idempotency_key": "order:ord-9999",
  "retry_count": 3,
  "error": "downstream inventory reservation failed",
  "failed_at": "2026-05-16T10:20:00+00:00"
}
```

이 페이로드가 있어야 운영자는 단순히 “실패했다”가 아니라 **무엇이, 몇 번째 재시도에서, 어떤 키로 실패했는지**를 기준으로 재처리할 수 있습니다.

## 트리거 선택 매트릭스

개념 설명만으로는 늘 부족한 지점이 바로 여기입니다. 트리거는 문법이 아니라 운영 계약이므로, 선택 기준을 표로 보는 편이 좋습니다.

| 트리거 | 지연 시간 기대치 | 재시도 기본값 | 순서 기대치 | 잘 맞는 작업 |
| --- | --- | --- | --- | --- |
| HTTP | 즉시 응답, 사용자 체감이 중요 | 보통 클라이언트나 API 게이트웨이 재시도와 결합 | 보장하지 않음 | API 요청, 동기 검증, 빠른 승인 응답 |
| Queue | 수 초~수 분 지연 허용 | at-least-once 재전달을 기본 가정 | 기본적으로 약함, 별도 FIFO 필요 | 비동기 후처리, 배치 소비, 버퍼링 |
| Schedule | 주기 기준 실행 | 플랫폼 재시도 또는 다음 주기 재실행 가능 | 순서보다 겹침 방지가 중요 | 정기 집계, 정리 작업, 동기화 |

이 표의 핵심은 트리거가 단순한 진입점 선택이 아니라는 사실입니다. HTTP를 고르면 사용자 지연 시간이 설계 중심이 되고, 큐를 고르면 중복 처리와 DLQ가 설계 중심이 되며, 스케줄을 고르면 재진입성과 겹침 방지가 설계 중심이 됩니다.

## 중복 처리 문제가 생겼을 때 운영자가 보는 순서

“같은 주문이 두 번 처리됐다”는 보고는 서버리스 운영에서 매우 흔합니다. 이때 막연히 코드부터 뜯어보면 느립니다. 아래 순서가 더 빠릅니다.

1. **메시지 ID를 확인합니다.**
   - 정말 같은 메시지가 재전달된 것인지, 비슷하지만 다른 메시지인지 구분합니다.
2. **멱등성 키 기록을 조회합니다.**
   - 키가 저장되지 않았는지, 저장 시점이 작업 후여서 너무 늦었는지 봅니다.
3. **재시도 횟수와 마지막 오류를 확인합니다.**
   - 일시 실패 후 재전달된 것인지, 영구 실패가 반복된 것인지 구분합니다.
4. **DLQ 페이로드를 읽습니다.**
   - 실패 메시지가 이미 격리되어 있다면 원인 파악과 재처리를 여기서 시작하는 편이 빠릅니다.

이 순서를 지키면 “트리거 문제인지, 멱등성 저장소 문제인지, 다운스트림 장애 문제인지”를 훨씬 빨리 좁힐 수 있습니다.

## 실무에서 자주 헷갈리는 지점

### 재시도는 정말 그렇게 자주 일어나나요?

그렇습니다. 네트워크 오류, 플랫폼 타임아웃, 다운스트림 일시 실패만으로도 같은 메시지는 쉽게 다시 들어옵니다. 그래서 비동기 트리거는 기본적으로 at-least-once라고 가정하는 편이 안전합니다.

### 순서 보장은 기본 제공인가요?

대부분 그렇지 않습니다. 순서가 중요하다면 FIFO 큐, 파티션 키, 단일 소비자 전략 같은 별도 설계를 명시적으로 선택해야 합니다.

### 실패대기열만 있으면 운영이 안전한가요?

아닙니다. DLQ는 실패를 보이게 해 주는 장치일 뿐입니다. 멱등성 키, 재시도 횟수, 원본 메시지 정보가 함께 남아야 재처리가 가능합니다.

## 체크리스트

- [ ] HTTP와 큐 트리거의 성공 의미를 분리해서 설계했는가
- [ ] 멱등성 키를 외부 저장소에 기록하는 계약이 있는가
- [ ] 재시도 한도와 DLQ 이동 기준이 명시되어 있는가
- [ ] 중복 처리 사고 시 무엇부터 확인할지 운영 순서를 알고 있는가

## 심화 실전 노트: 람다 구성, 콜드 스타트, 이벤트 소스 매핑 운영

서버리스 운영에서는 함수 코드보다 구성값이 장애를 만드는 경우가 더 많습니다. 메모리, 타임아웃, 동시성, 재시도 정책, 이벤트 소스 매핑 배치 크기 같은 설정이 처리량과 비용을 동시에 바꾸기 때문입니다. 따라서 기능 구현과 설정 검토를 분리하지 않고, 배포 단위마다 같이 점검해야 합니다.

### 람다 구성에서 먼저 고정할 항목

아래 예시는 AWS SAM 템플릿 기준으로 자주 사용하는 안전 기본값입니다.

```yaml
Resources:
  OrdersWorker:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: app.handler
      MemorySize: 1024
      Timeout: 20
      ReservedConcurrentExecutions: 30
      Environment:
        Variables:
          LOG_LEVEL: INFO
          POWERTOOLS_SERVICE_NAME: orders-worker
```

메모리를 올리면 비용만 증가한다고 오해하기 쉽지만, CPU 비율도 함께 올라가서 실행 시간이 줄어 전체 비용이 내려가는 구간이 자주 나타납니다. 그래서 메모리 값은 감으로 정하지 않고, 대표 워크로드를 기준으로 512/1024/1536MB를 비교 측정하는 방식이 필요합니다.

### 콜드 스타트 분석 포인트

콜드 스타트는 "있다/없다" 문제가 아니라 지연 분포를 어떻게 관리하느냐의 문제입니다. 운영에서는 p50보다 p95, p99 구간을 먼저 확인해야 합니다. Python 함수 기준으로는 패키지 크기, import 시점 초기화, VPC 연결 여부가 주요 변수입니다.

- 패키지 크기: 불필요한 의존성을 줄이면 초기 로드 시간이 줄어듭니다.
- 초기화 전략: DB 연결 풀 생성, 모델 로딩, 대형 설정 파싱을 모듈 로딩 시점에 몰아넣지 않습니다.
- 동시성 전략: 예측 가능한 트래픽 구간에는 Provisioned Concurrency를 제한적으로 적용합니다.

단순 평균 지연만 보면 개선 효과가 숨겨질 수 있으므로, 배포 전후의 `Init Duration` 분포와 타임아웃 비율을 같이 비교하는 습관이 중요합니다.

### 이벤트 소스 매핑(이벤트 소스 매핑) 설계

SQS, Kinesis, DynamoDB Streams를 사용할 때는 배치 크기와 실패 재처리 정책이 핵심입니다.

```yaml
Events:
  OrdersQueue:
    Type: SQS
    Properties:
      Queue: !GetAtt OrdersQueue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 5
      FunctionResponseTypes:
        - ReportBatchItemFailures
```

`ReportBatchItemFailures`를 사용하면 배치 전체 재시도를 줄이고 실패 레코드만 다시 처리할 수 있습니다. 이 설정이 없으면 정상 처리된 메시지까지 반복 실행되어 비용과 중복 부작용이 늘어납니다. 또한 DLQ 정책을 함께 설정해 영구 실패 메시지를 격리해야 운영자가 원인을 빠르게 분석할 수 있습니다.

### 구성값과 코드의 책임 분리

서버리스에서 흔한 안티패턴은 재시도, 타임아웃, 멱등성 처리를 코드 내부 if 분기로만 해결하려는 접근입니다. 운영 가능한 구조는 다음처럼 책임을 분리합니다.

1. 인프라 설정: 동시성, 재시도, 배치, DLQ
2. 애플리케이션 코드: 멱등 키 검증, 비즈니스 규칙, 오류 분류
3. 관측 체계: 구조화 로그, 지연/오류 메트릭, 알람 임계값

이렇게 분리하면 이벤트 소스가 바뀌어도 코드 수정 범위를 줄일 수 있고, 비용 최적화 실험도 설정 레벨에서 안전하게 반복할 수 있습니다.

### 배포 전 점검 항목

배포 직전에는 함수 코드 테스트와 함께 설정 검증을 반드시 포함해야 합니다. 메모리/타임아웃 조합, 최대 동시성 제한, DLQ 연결, 이벤트 매핑 배치 정책, 콜드 스타트 완화 전략까지 체크리스트로 남기면 장애 복구 시간이 크게 단축됩니다.

## 실무 앵커: 이벤트 계약을 코드와 인프라에서 동시에 검증하기

트리거 설계의 핵심은 "어떤 이벤트가 온다"가 아니라 "어떤 이벤트만 통과시킬 것인가"입니다. 이벤트 스키마를 코드와 설정 양쪽에서 제한해야 독성 메시지와 중복 처리 위험을 낮출 수 있습니다.

### 인터페이스 게이트웨이에서 메시지큐서비스로 넘기는 경로

```yaml
Resources:
  IngressApi:
    Type: AWS::Serverless::HttpApi

  IntakeQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 60
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt IntakeDlq.Arn
        maxReceiveCount: 5

  IntakeDlq:
    Type: AWS::SQS::Queue

  QueueConsumer:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: consumer.handler
      Timeout: 30
      Events:
        QueueTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt IntakeQueue.Arn
            BatchSize: 10
            MaximumBatchingWindowInSeconds: 5
            FunctionResponseTypes:
              - ReportBatchItemFailures
```

여기서 `ReportBatchItemFailures`를 켜 두면 배치 전체 재처리 대신 실패 메시지 단위로 재시도할 수 있어 중복 비용과 지연을 줄일 수 있습니다.

### 소비자 코드: 멱등성 키와 부분 실패 응답

```python
import json
import os

import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource("dynamodb")
locks = ddb.Table(os.environ["IDEMPOTENCY_TABLE"])

def handler(event, context):
    failures = []

    for record in event["Records"]:
        message_id = record["messageId"]
        payload = json.loads(record["body"])
        idem_key = payload["eventId"]

        try:
            locks.put_item(
                Item={"pk": idem_key},
                ConditionExpression="attribute_not_exists(pk)",
            )
            process(payload)
        except ClientError:
            continue
        except Exception:
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}

def process(payload):
    # 도메인 처리 로직
    return payload
```

이 패턴은 실패를 숨기지 않으면서도 재처리 범위를 최소화합니다. 이벤트 기반 시스템에서 "한 번 더 처리"는 정상 경로이기 때문에, 멱등성 저장소는 선택이 아니라 기본 구성입니다.

### 비용과 지연을 함께 보는 트리거 표

| 항목 | 즉시 동기 처리 | 큐 기반 비동기 처리 |
| --- | --- | --- |
| 사용자 응답 지연 | 길어질 수 있음 | 짧게 유지 가능 |
| 실패 격리 | 낮음 | 높음 |
| 재시도 비용 | 호출 전체 재실행 | 실패 메시지만 재시도 |
| 운영 복잡도 | 낮음 | 중간 |

트리거를 나누면 복잡도가 늘지만, 장애 격리와 비용 통제 능력이 커집니다. "단순한 경로"보다 "회복 가능한 경로"를 먼저 설계하는 것이 서버리스 운영에서 더 안전합니다.

### 인터페이스 게이트웨이 입력 검증 예시

입력 검증을 애플리케이션 코드에만 두면 무효 요청도 함수 실행 비용을 발생시킵니다. 간단한 스키마 검증은 게이트웨이 단계에서 차단하는 편이 비용과 지연 양쪽에 유리합니다.

```yaml
RequestModel:
  type: object
  required:
    - eventId
    - orderId
    - amount
  properties:
    eventId:
      type: string
    orderId:
      type: string
    amount:
      type: integer
      minimum: 1
```

### 콜드 스타트가 트리거 설계에 미치는 영향

동기 API 경로에서는 콜드 스타트가 사용자 체감 지연으로 직접 드러납니다. 반면 큐 소비 경로에서는 큐 지연으로 흡수될 수 있습니다. 따라서 사용자 응답을 엄격히 관리해야 하는 기능은 동기 경로를 짧게 유지하고, 무거운 처리는 이벤트로 분리하는 전략이 안정적입니다.

이 판단을 문서화할 때는 "어떤 작업을 분리했는가"보다 "분리해서 무엇을 보호했는가"를 명시해야 합니다. 예를 들어 결제 승인 API에서 고객 응답 시간을 보호하기 위해 영수증 발행을 큐로 분리했다는 식으로 기록하면, 이후 변경 검토가 훨씬 명확해집니다.

## 정리

트리거와 이벤트를 이해한다는 것은 함수 진입점을 외우는 일이 아닙니다. **호출 방식이 곧 실패 방식이고, 실패 방식이 곧 재시도·멱등성·DLQ 설계로 이어진다**는 사실을 이해하는 일입니다.

이번 글의 핵심은 하나입니다. HTTP 요청은 빠르게 받아들이고, 실제 작업은 큐 뒤로 넘기고, 중복은 멱등성 저장소에서 막고, 반복 실패는 DLQ에 남겨 운영 가능한 형태로 격리해야 합니다. 다음 글에서는 이 흐름 위에서 왜 콜드 스타트가 지연 시간에 큰 영향을 주는지 봅니다.

## 처음 질문으로 돌아가기

- **HTTP, 큐, 스케줄 트리거는 호출 의미가 어떻게 다를까요?**
  - HTTP는 사용자에게 바로 `202 Accepted` 같은 응답을 돌려주는 동기 경계이고, 큐는 실제 후처리를 뒤로 미루는 비동기 경계이며, 스케줄은 정해진 주기에 재진입성과 겹침 방지를 먼저 보는 호출 방식입니다. 본문 표에서도 각 트리거마다 지연 시간 기대치, 재시도 기본값, 잘 맞는 작업이 다르다는 점을 분리해 설명했습니다.
- **비동기 소비자에서는 왜 멱등성이 기본 전제가 될까요?**
  - `queue_consumer_handler()`는 같은 `idempotency_key`가 다시 오면 `processed_messages` 저장소를 조회해 `duplicate`로 건너뜁니다. 큐 재전달과 재시도는 정상 경로이므로, `mark_processed()` 같은 외부 기록이 없으면 같은 주문이 여러 번 후처리되는 부작용을 막을 수 없습니다.
- **DLQ는 단순한 보조 기능이 아니라 왜 운영의 핵심 관찰 지점일까요?**
  - 독성 메시지가 세 번 실패했을 때 `message_id`, `order_id`, `retry_count`, `error`, `failed_at`를 담아 DLQ로 보내는 예시가 바로 그 이유입니다. 이 페이로드가 있어야 운영자가 무엇이 몇 번째 시도에서 실패했는지 확인하고, 처음부터 전체 흐름을 다시 돌리지 않고 필요한 메시지만 재처리할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- **트리거와 이벤트 (현재 글)**
- 콜드 스타트 (예정)
- 스케일링 (예정)
- 상태 관리 (예정)
- 큐와 이벤트 기반 아키텍처 (예정)
- 관측성 (예정)
- 비용 (예정)
- 서버리스 앱 설계 (예정)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [Lambda 이벤트 소스 매핑](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [Amazon SQS 데드 레터 큐](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Azure Functions 트리거와 바인딩 개요](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)

### 패턴과 코드

- [멱등성 패턴](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/idempotency.html)
- [AWS Powertools for Lambda Python - Idempotency](https://docs.powertools.aws.dev/lambda/python/latest/utilities/idempotency/)
- [Azure Architecture Center - Queue-based load leveling pattern](https://learn.microsoft.com/azure/architecture/patterns/queue-based-load-leveling)

Tags: Serverless, Trigger, Event, EventDriven, Cloud
