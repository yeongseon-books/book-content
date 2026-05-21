---
series: distributed-systems-101
episode: 3
title: "Distributed Systems 101 (3/10): RPC와 메시지 전달"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Distributed Systems
  - RPC
  - Messaging
  - Async
  - Idempotency
seo_description: 분산 시스템의 핵심인 RPC와 메시지 전달의 차이를 동기/비동기 관점에서 구조적으로 비교하고 상황별 선택 기준을 제시합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (3/10): RPC와 메시지 전달

서비스를 나누고 나면 다음 질문은 거의 항상 같습니다. "이 둘은 어떻게 말하게 할 것인가?" 응답을 기다리는 RPC를 쓸지, 큐를 사이에 둔 비동기 흐름을 쓸지에 따라 지연 예산과 장애 전파 범위가 완전히 달라집니다.

이 글은 Distributed Systems 101 시리즈의 세 번째 글입니다.

여기서는 RPC와 메시지 전달을 각각 하나의 통신 계약으로 보고, 어느 경계에서 어떤 방식을 택해야 하는지 선택 기준을 세웁니다.

## 먼저 던지는 질문

- RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?
- 동기와 비동기, 요청-응답과 발행-구독은 어디서 갈릴까요?
- 두 모델은 각각 어떤 장단점이 있고 어디에 어울릴까요?

## 큰 그림

![Distributed Systems 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/03/03-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 3장 흐름 개요*

## 왜 중요한가

서비스를 분리한 뒤 가장 먼저 내려야 하는 결정 중 하나는 어떻게 통신할 것인가입니다. 이 선택이 지연 예산, 장애 전파 범위, 운영 복잡도를 함께 결정합니다. 잘못 고르면 한 노드의 지연이 전체 RPC 체인을 잡아끌고, 반대로 추적 불가능한 메시지 흐름이 생길 수도 있습니다.

> 통신 모델은 시스템의 결합도를 결정합니다.

## 한눈에 보는 개념

RPC는 양방향 계약이고, 메시지 전달은 중간 저장소를 둔 단방향 흐름입니다.

## 핵심 용어

- **RPC (Remote Procedure Call)**: 원격 함수를 로컬 함수처럼 호출하는 방식입니다. gRPC, JSON-RPC가 대표적입니다.
- **Message passing**: 생산자가 브로커에 메시지를 넣고 소비자가 나중에 가져가는 방식입니다. Kafka, RabbitMQ가 대표적입니다.
- **Synchronous**: 응답이 올 때까지 기다립니다.
- **Asynchronous**: 응답을 기다리지 않고 다음 작업으로 넘어갑니다.
- **At-least-once / exactly-once**: 브로커가 제공하려는 전달 보장 수준입니다.

## Before / After

**Before — 모든 호출을 RPC로 설계**

```text
service A -> B -> C -> D: if D slows down, A's response slows
```

**After — 중요한 경계는 메시지로 분리**

```text
A drops a message and returns; D processes asynchronously
```

이 전환으로 장애 전파 범위를 줄이고 사용자 응답 예산을 더 촘촘히 관리할 수 있습니다.

## 실습: 두 모델을 한 화면에 놓고 보기

### 1단계 — RPC(FastAPI)

```python
# 1_rpc_server.py
from fastapi import FastAPI
app = FastAPI()
@app.post("/charge")
def charge(amount: int):
    # process payment synchronously
    return {"ok": True, "id": "txn_1"}
```

```python
# 1_rpc_client.py
import requests
r = requests.post("http://127.0.0.1:8000/charge", json={"amount": 100}, timeout=2)
print(r.json())
```

응답이 도착해야 다음 줄이 실행됩니다. 실제로는 거의 함수 호출과 같은 감각입니다.

### 2단계 — 메시지 전달(메모리 큐)

```python
# 2_queue.py
from queue import Queue
import threading, time

q = Queue()

def consumer():
    while True:
        msg = q.get()
        time.sleep(0.5)
        print("processed:", msg)

threading.Thread(target=consumer, daemon=True).start()
q.put({"amount": 100, "id": "txn_1"})
print("producer returned immediately")
```

생산자는 즉시 반환되고, 소비자는 자기 속도로 큐를 비웁니다.

### 3단계 — RPC 체인의 위험

```python
# 3_chain.py (pseudocode)
def order():
    inv = rpc_inventory()    # 100ms
    pay = rpc_payment()      # 200ms
    ship = rpc_shipping()    # 150ms
    return ok                # total 450ms plus retry/timeout
```

모든 단계가 살아 있어야 응답 하나가 돌아옵니다. 한 노드가 느려지면 전체 호출이 함께 느려집니다.

### 4단계 — 비동기와 큐로 분리

```python
# 4_async.py (pseudocode)
def order():
    save_order_local()
    publish("order.created", payload)
    return "accepted"  # respond immediately
# separate workers handle inventory/payment/shipping
```

사용자는 빠른 응답을 받고, 느린 하위 단계는 뒤에서 처리됩니다.

### 5단계 — 전달 보장과 중복 처리

```python
# 5_dedup.py
seen = set()
def consume(msg):
    if msg["id"] in seen:
        return  # idempotent: ignore duplicates
    seen.add(msg["id"])
    process(msg)
```

대부분의 브로커는 at-least-once를 전제로 하므로, 소비자는 멱등성 키로 중복을 흡수해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- RPC는 기다림 자체가 강한 결합을 만듭니다.
- 메시지 전달은 지금 당장 끝낼 필요가 없는 작업에 잘 맞습니다.
- 체인이 깊어질수록 RPC의 위험은 커집니다.
- exactly-once는 거의 항상 허상이고, 현실적인 답은 멱등적 소비자입니다.

## 자주 하는 실수 5가지

1. **모든 것을 RPC로 만듭니다.** 체인이 길어지며 지연과 장애 면적이 폭발합니다.
2. **모든 것을 큐 기반으로 만듭니다.** 즉시 응답이 필요한 사용자 경로가 불편해집니다.
3. **exactly-once를 그대로 믿습니다.** 현실은 브로커 보장과 멱등성 소비자의 조합입니다.
4. **멱등성 키를 생략합니다.** 재시도 한 번이 중복 결제로 이어질 수 있습니다.
5. **타임아웃과 재시도를 클라이언트에만 둡니다.** 브로커 쪽 DLQ와 재시도 정책도 함께 필요합니다.

## 실무에서는 이렇게 드러납니다

즉시 응답이 필요한 사용자 경로는 RPC를 사용하고, 메일 발송이나 분석처럼 오래 걸리는 작업은 큐로 넘깁니다. 많은 마이크로서비스 아키텍처는 내부 모듈 간 호출은 RPC로, 도메인 경계는 메시지로 나눥니다. Event sourcing과 CQRS는 이 메시지 모델을 끝까지 밀어붙인 설계라고 볼 수 있습니다.

대표적인 조합 예시:

| 서비스 | 통신 방식 | 이유 |
|---------|-----------|------|
| 사용자 인증 | 동기 RPC | 로그인 결과를 즉시 보여줘야 함 |
| 결제 처리 | 동기 RPC + 멱등성 | 결과 확인 필수, 재시도 안전성 필요 |
| 이메일 발송 | 비동기 메시지 | 실패 시 재시도만 하면 됨, 지연 허용 |
| 로그 수집 | 비동기 메시지 | 대량 처리, 순서 무관 |
| 주문 상태 변경 | 이벤트 발행 | 여러 소비자가 각자 반응 |

## 시니어 엔지니어는 이렇게 생각합니다

- 정말 동기 응답이 필요한지부터 먼저 묻습니다.
- RPC 체인의 깊이를 제한합니다. 대부분 3단계 이상이면 중간에 비동기 경계를 넣습니다.
- 첫 커밋부터 멱등성 키를 설계에 넣습니다.
- 브로커는 기본적으로 at-least-once라고 가정합니다.
- DLQ와 재시도 정책을 운영 책임의 일부로 봅니다.
- gRPC를 쓸 때는 deadline propagation을 반드시 활성화합니다. 전파되지 않는 데드라인은 하위 서비스에 불필요한 부하를 줍니다.

## 체크리스트

- [ ] RPC와 메시지 전달의 차이를 한 줄로 설명할 수 있는가?
- [ ] 깊은 RPC 체인이 왜 위험한지 설명할 수 있는가?
- [ ] at-least-once와 exactly-once의 의미를 알고 있는가?
- [ ] 멱등성 키를 설계해 본 적이 있는가?
- [ ] DLQ가 무엇이며 언제 쓰는지 말할 수 있는가?

## 연습 문제

1. 현재 서비스에서 RPC를 메시지로 바꿀 만한 호출 하나를 찾아 이유를 설명해 보세요.
2. 멱등성 키를 사용하는 결제 API를 한 단락으로 설계해 보세요.
3. at-least-once 전달에서 안전한 소비자가 갖춰야 할 조건 세 가지를 적어 보세요.

## 정리와 다음 글

RPC와 메시지 전달은 동기와 비동기, 결합도와 회복력을 서로 다르게 교환하는 두 모델입니다. 다음 글에서는 데이터가 여러 노드에 놓이는 순간 바로 등장하는 가장 큰 트레이드오프, 일관성과 CAP를 다룹니다.

## gRPC 서비스 메시 구성

마이크로서비스가 10개를 넘어가면 서비스 간 통신을 개별 코드로 관리하기 어렵습니다. 이때 서비스 메시가 RPC 계층의 공통 관심사를 인프라로 내립니다.

### gRPC 서비스 정의

```protobuf
// payment.proto
syntax = "proto3";

package payment.v1;

service PaymentService {
  rpc Charge(ChargeRequest) returns (ChargeResponse);
  rpc Refund(RefundRequest) returns (RefundResponse);
}

message ChargeRequest {
  string idempotency_key = 1;
  int64 amount_cents = 2;
  string currency = 3;
  string customer_id = 4;
}

message ChargeResponse {
  string transaction_id = 1;
  Status status = 2;
  enum Status {
    SUCCESS = 0;
    DECLINED = 1;
    TIMEOUT = 2;
  }
}
```

gRPC는 HTTP/2 위에서 바이너리 직렬화(Protocol Buffers)를 사용하므로 JSON 기반 REST보다 페이로드가 작고 파싱이 빠릅니다. 하지만 진짜 이점은 `.proto` 파일 하나로 클라이언트와 서버의 계약이 코드 생성까지 자동화된다는 점입니다.

### Envoy 사이드카 구성

서비스 메시에서는 각 Pod에 Envoy 프록시를 사이드카로 붙입니다. 애플리케이션은 localhost로만 통신하고, 실제 라우팅·재시도·서킷 브레이커는 Envoy가 처리합니다.

```yaml
# envoy-sidecar.yaml (Istio 스타일)
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: payment-service
spec:
  host: payment.default.svc.cluster.local
  trafficPolicy:
    connectionPool:
      http:
        h2UpgradePolicy: UPGRADE  # gRPC는 HTTP/2 필수
        maxRequestsPerConnection: 100
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
    loadBalancer:
      simple: ROUND_ROBIN
  subsets:
    - name: v1
      labels:
        version: v1
```

이 설정의 핵심은 `outlierDetection`입니다. 연속 3회 5xx 오류가 나면 해당 인스턴스를 30초간 풀에서 제거합니다. 애플리케이션 코드를 건드리지 않고도 장애 인스턴스를 격리할 수 있습니다.

### 재시도 정책

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: payment-retry
spec:
  hosts:
    - payment.default.svc.cluster.local
  http:
    - route:
        - destination:
            host: payment.default.svc.cluster.local
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: unavailable,deadline-exceeded,resource-exhausted
```

`retryOn`에 `unavailable`만 넣고 `internal`은 빼는 이유가 있습니다. 결제처럼 부작용이 있는 RPC는 서버 내부 오류 시 무조건 재시도하면 이중 청구 위험이 있습니다. 멱등성이 보장된 호출만 재시도 대상에 포함해야 합니다.

---

## RPC 패턴 심화: 타임아웃 전파와 데드라인

gRPC는 deadline propagation을 기본 지원합니다. 클라이언트가 설정한 데드라인이 서버로 전파되어, 중간 서비스가 이미 시간이 초과된 요청을 계속 처리하는 낭비를 막습니다.

```python
# deadline propagation 예시
import grpc
from payment_pb2_grpc import PaymentServiceStub
from payment_pb2 import ChargeRequest

channel = grpc.insecure_channel("payment:50051")
stub = PaymentServiceStub(channel)

# 클라이언트 데드라인: 2초
try:
    response = stub.Charge(
        ChargeRequest(
            idempotency_key="order-12345",
            amount_cents=5000,
            currency="KRW",
            customer_id="cust-001",
        ),
        timeout=2.0,  # 이 데드라인이 downstream으로 전파
    )
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        # 타임아웃 — 결과를 모르는 상태
        check_idempotency_key("order-12345")
    elif e.code() == grpc.StatusCode.UNAVAILABLE:
        # 서버 접근 불가 — 재시도 가능
        retry_with_backoff()
```

데드라인이 전파되면 A → B → C 체인에서 A가 2초를 설정하고 B에서 1.5초를 소모하면, C는 남은 0.5초만 갖습니다. C가 0.5초 안에 끝내지 못하면 즉시 DEADLINE_EXCEEDED를 반환합니다. 이렇게 하면 이미 실패한 요청이 하위 서비스 자원을 계속 점유하는 문제를 방지합니다.

---

## 메시지 전달 심화: 순서 보장과 파티셔닝

메시지 큐에서 가장 흔한 오해는 "큐니까 순서가 보장된다"입니다. 실제로 대부분의 분산 큐는 파티션 내 순서만 보장합니다.

```text
토픽: order.events (파티션 4개)

파티션 키: customer_id
→ 같은 고객의 이벤트는 같은 파티션으로 → 순서 보장
→ 다른 고객의 이벤트 간에는 순서 보장 없음

파티션 0: [cust-A 주문생성, cust-A 결제완료, cust-A 배송시작]
파티션 1: [cust-B 주문생성, cust-B 결제완료]
파티션 2: [cust-C 주문생성]
파티션 3: (비어있음)
```

파티션 키 선택은 순서 보장 범위를 결정합니다. 고객 ID를 키로 쓰면 한 고객의 이벤트 순서는 보장되지만, 전체 이벤트의 글로벌 순서는 보장되지 않습니다. 글로벌 순서가 필요하면 파티션을 1개로 줄여야 하는데, 이는 처리량을 심각하게 제한합니다.

### Dead Letter Queue 운영

소비자가 처리에 실패한 메시지는 무한 재시도 대신 DLQ로 분리합니다.

```python
# DLQ 처리 패턴
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeadLetter:
    original_topic: str
    payload: dict
    error: str
    retry_count: int
    first_failed_at: datetime
    last_failed_at: datetime

def consume_with_dlq(msg, max_retries: int = 5):
    try:
        process(msg)
        ack(msg)
    except TransientError:
        if msg.retry_count < max_retries:
            nack_with_backoff(msg)
        else:
            send_to_dlq(msg, reason="max_retries_exceeded")
    except PermanentError as e:
        # 재시도해도 안 되는 오류는 즉시 DLQ
        send_to_dlq(msg, reason=str(e))
```

DLQ에 쌓인 메시지는 수동 검토 후 원본 토픽으로 재주입하거나, 보정 로직을 적용합니다. 운영 대시보드에서 DLQ 유입률이 갑자기 치솟으면 소비자 코드에 버그가 들어갔거나 스키마가 변경된 신호입니다.

---

## 하이브리드 패턴: 동기 확인 + 비동기 처리

실무에서 가장 흔한 패턴은 순수 RPC도 순수 메시지도 아닌 하이브리드입니다.

```python
# 주문 API: 동기 확인 + 비동기 처리
from fastapi import FastAPI, HTTPException
from uuid import uuid4

app = FastAPI()

@app.post("/orders")
async def create_order(order: OrderRequest):
    # 1. 동기: 입력 검증 + 재고 확인 (RPC)
    stock = await inventory_client.check(order.sku, order.qty)
    if not stock.available:
        raise HTTPException(409, "out of stock")

    # 2. 동기: 주문 저장
    order_id = str(uuid4())
    await db.save_order(order_id, order, status="pending")

    # 3. 비동기: 결제/배송은 메시지로 위임
    await publisher.publish("order.created", {
        "order_id": order_id,
        "amount": order.total,
        "customer_id": order.customer_id,
    })

    # 4. 즉시 응답: 사용자는 기다리지 않음
    return {"order_id": order_id, "status": "accepted"}
```

이 패턴의 핵심은 사용자 응답 경로(동기)와 후속 처리 경로(비동기)를 분리하는 것입니다. 재고 확인은 즉시 답이 필요하므로 RPC로, 결제와 배송은 수초~수분 걸릴 수 있으므로 메시지로 위임합니다. 사용자는 "주문 접수됨" 응답을 즉시 받고, 이후 상태 변화는 폴링이나 웹소켓으로 확인합니다.

---

## 통신 모델 선택 의사결정 트리

```text
사용자가 즉시 결과를 봐야 하는가?
├── 예 → 동기 RPC
│   ├── 체인 깊이 ≤ 2? → 직접 호출
│   └── 체인 깊이 > 2? → API Gateway + 병렬 호출
└── 아니오 → 비동기 메시지
    ├── 순서가 중요한가?
    │   ├── 예 → 파티션 키 기반 큐 (Kafka)
    │   └── 아니오 → 작업 큐 (RabbitMQ, SQS)
    └── 실패 시 재처리가 안전한가?
        ├── 예 → at-least-once + 멱등성
        └── 아니오 → 트랜잭션 아웃박스 패턴
```

이 트리를 설계 리뷰 체크리스트로 사용하면 "왜 이 호출을 RPC로 했는가"에 대한 근거를 팀 전체가 공유할 수 있습니다.

---

## 운영 지표: RPC vs 메시지

| 계층 | 지표 | 의미 |
|------|------|------|
| RPC | P99 응답 시간 | 꼬리 지연이 데드라인에 근접하면 위험 |
| RPC | 재시도 비율 | 10% 넘으면 서버 불안정 신호 |
| RPC | 서킷 브레이커 open 횟수 | 하류 서비스 장애 빈도 |
| 메시지 | consumer lag | 소비 속도 < 생산 속도면 적체 |
| 메시지 | DLQ 유입률 | 처리 실패 메시지 비율 |
| 메시지 | end-to-end 지연 | 발행~소비 완료까지 시간 |

```python
# 운영 지표 수집 예시
from prometheus_client import Counter, Histogram

rpc_duration = Histogram(
    "rpc_duration_seconds",
    "RPC call duration",
    ["service", "method"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
)

rpc_retries = Counter(
    "rpc_retries_total",
    "RPC retry count",
    ["service", "method", "reason"],
)

consumer_lag = Histogram(
    "consumer_lag_seconds",
    "Time from publish to consume",
    ["topic", "consumer_group"],
)

dlq_messages = Counter(
    "dlq_messages_total",
    "Messages sent to DLQ",
    ["topic", "reason"],
)
```

RPC의 P99가 데드라인의 80%에 도달하면 경보를 울려야 합니다. consumer lag이 5분을 넘으면 소비자를 스케일아웃하거나 배치 크기를 조정해야 합니다. 이 지표들이 평상시 기준선(baseline)과 얼마나 벗어났는지를 자동으로 감지하는 것이 운영 성숙도의 핵심입니다.

---

## RPC 커넥션 풀링과 부하 제어

gRPC 채널은 TCP 커넥션 위에 HTTP/2 스트림을 다중화합니다. 커넥션 하나로 여러 호출을 병렬할 수 있지만, 서버가 많아지면 커넥션 풀 관리가 필수입니다.

```python
# gRPC 커넥션 풀 설정 예시
import grpc

# 채널 옵션으로 커넥션 동작 제어
options = [
    ("grpc.keepalive_time_ms", 10000),       # 10초마다 keepalive ping
    ("grpc.keepalive_timeout_ms", 5000),     # 5초 내 응답 없으면 재연결
    ("grpc.max_connection_idle_ms", 300000), # 5분 유휴 시 연결 닫기
    ("grpc.max_connection_age_ms", 600000),  # 10분 후 연결 갱신 (로드 밸런싱용)
]

channel = grpc.insecure_channel("payment:50051", options=options)
```

`max_connection_age_ms`는 로드 밸런서 뒤에서 중요합니다. gRPC는 연결이 오래 유지되면 특정 서버에 트래픽이 쾌이는 현상이 생깁니다. 주기적으로 연결을 갱신하면 로드 밸런서가 새 연결을 다른 백엔드로 분배할 기회를 얻습니다.

### 마감 시간 계층화

RPC 채인에서 마감 시간을 올바르게 설정하는 원칙은 "외부 호출자의 마감 > 내부 호출의 마감 합계"입니다.

```text
API Gateway (timeout: 10s)
└── Order Service (timeout: 8s)
    ├── Inventory RPC (timeout: 2s)
    ├── Payment RPC (timeout: 3s)
    └── Notification (async, no timeout)

내부 동기 호출 합계: 2 + 3 = 5s < 8s (여유 3s)
Order Service timeout 8s < API Gateway 10s (여유 2s)
```

이 여유를 두지 않으면 하위 서비스가 정상 응답했는데도 상위에서 타임아웃이 먼저 터지는 상황이 발생합니다. 이런 불필요한 타임아웃은 재시도를 유발하고, 재시도는 부하를 늘리고, 부하는 다시 타임아웃을 유발하는 악순환으로 이어집니다.

### 백프레셔와 부하 제한

메시지 큐의 소비자 측에서는 `prefetch_count`가 백프레셔 역할을 합니다. 한 번에 너무 많이 가져오면 메모리가 터지고, 너무 적게 가져오면 네트워크 왔복이 많아져 처리량이 떨어집니다.

```python
# 적응적 prefetch 예시
import time

class AdaptivePrefetch:
    def __init__(self, min_pf=1, max_pf=100):
        self.current = 10
        self.min_pf = min_pf
        self.max_pf = max_pf
        self.last_process_time = 0.0

    def adjust(self, process_time: float):
        if process_time < 0.01:  # 처리가 빠르면 더 가져오기
            self.current = min(self.current * 2, self.max_pf)
        elif process_time > 1.0:  # 처리가 느리면 줄이기
            self.current = max(self.current // 2, self.min_pf)
        self.last_process_time = process_time
        return self.current
```

이 패턴은 소비자의 처리 속도에 따라 큐에서 가져오는 양을 동적으로 조절합니다. 트래픽이 급증할 때 소비자가 과부하로 죽지 않게 보호하면서도, 여유가 있을 때는 치리량을 최대화합니다.

## 처음 질문으로 돌아가기

- **RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?**
  - RPC는 호출자가 응답을 기다리는 동기 계약이고, 메시지 전달은 브로커를 사이에 두고 생산자와 소비자가 독립적으로 동작하는 비동기 계약입니다. RPC는 강한 결합과 즉시 결과를, 메시지는 느슨한 결합과 지연 처리를 교환합니다.
- **동기와 비동기, 요청-응답과 발행-구독은 어디서 갈릴까요?**
  - 사용자가 즉시 결과를 봐야 하는 경로는 동기 RPC, 후속 처리나 이벤트 전파는 비동기 메시지입니다. 의사결정 트리에서 보았듯이 체인 깊이와 실패 시 재처리 안전성이 갈림점입니다.
- **두 모델은 각각 어떤 장단점이 있고 어디에 어울릴까요?**
  - RPC는 간단하고 디버깅이 쉽지만 체인이 깊어지면 지연과 장애가 전파됩니다. 메시지는 회복력이 높고 부하를 분산하지만 순서 보장과 중복 처리라는 복잡도를 안습니다. 실무에서는 하이브리드 패턴으로 두 모델의 장점을 조합합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- **RPC와 메시지 전달 (현재 글)**
- 일관성과 CAP (예정)
- 복제 (예정)
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Remote procedure call (Wikipedia)](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [Message passing (Wikipedia)](https://en.wikipedia.org/wiki/Message_passing)
- [gRPC documentation](https://grpc.io/docs/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)
Tags: Computer Science, Distributed Systems, RPC, Messaging, Async, Idempotency
