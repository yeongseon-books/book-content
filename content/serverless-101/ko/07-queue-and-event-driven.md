---
series: serverless-101
episode: 7
title: Queue와 Event-driven Architecture
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Serverless
  - Queue
  - EventDriven
  - PubSub
  - Cloud
seo_description: 큐와 이벤트 드리븐 아키텍처에서 디커플링, fan-out, FIFO, 재시도, DLQ를 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# Queue와 Event-driven Architecture

> Serverless 101 시리즈 (7/10)


## 이 글에서 다룰 문제

*동기 호출 체인* 은 *한 곳* 의 *장애* 가 *전체* 를 무너뜨립니다. *비동기 메시지* 가 *복원력* 을 제공합니다.

## 전체 흐름
```mermaid
flowchart LR
    Producer["producer"] --> Queue["queue / topic"]
    Queue --> C1["consumer A"]
    Queue --> C2["consumer B"]
```

## Before/After

**Before**: *주문 API* → *결제 → 메일 → 통계* 동기 체인.

**After**: *주문 이벤트* 를 *토픽* 에 발행, 각 *함수* 가 *독립적* 처리.

## 간단 메시징

### 1단계 — 인메모리 큐

```python
from collections import deque
queue = deque()
def publish(msg): queue.append(msg)
def consume(): return queue.popleft() if queue else None
```

### 2단계 — fan-out

```python
subs = []
def subscribe(fn): subs.append(fn)
def emit(event):
    for fn in subs:
        fn(event)
```

### 3단계 — 소비자 함수

```python
def billing(event): print("bill", event)
def mail(event): print("mail", event)
```

### 4단계 — 재시도와 DLQ

```python
def retry(handler, dlq, attempts=3):
    def wrap(event):
        for i in range(attempts):
            try:
                return handler(event)
            except Exception:
                if i == attempts - 1:
                    dlq.append(event)
                    raise
    return wrap
```

### 5단계 — FIFO 순서 키

```python
def fifo_key(order):
    return order["customer_id"]
```

## 이 코드에서 주목할 점

- *fan-out* 으로 *결합도* 감소.
- *FIFO 키* 가 *순서 단위*.
- *DLQ* 가 *문제 가시화*.

## 자주 하는 실수 5가지

1. ***순서* 가 *모든 곳* 에서 *필요하다* 가정.**
2. ***경쟁 소비자* 동작 모름.**
3. ***멱등성* 없이 *fan-out* 도입.**
4. ***DLQ* 미설정.**
5. ***메시지 크기* 한도 무시.**

## 실무에서는 이렇게 쓰입니다

*주문, 결제, 통계* 같은 *팀별 도메인* 을 *이벤트 버스* 로 *느슨하게* 연결합니다.

## 체크리스트

- [ ] *이벤트 스키마* 문서화.
- [ ] *DLQ* + 알람.
- [ ] *멱등성* 점검.
- [ ] *FIFO* 필요 여부.

## 정리 및 다음 단계

다음 글은 *Observability* 입니다.

<!-- toc:begin -->
- [Serverless란 무엇인가?](./01-what-is-serverless.md)
- [Function as a Service](./02-function-as-a-service.md)
- [Trigger와 Event](./03-trigger-and-event.md)
- [Cold Start](./04-cold-start.md)
- [Scaling](./05-scaling.md)
- [State 관리](./06-state-management.md)
- **Queue와 Event-driven Architecture (현재 글)**
- Observability (예정)
- Cost (예정)
- Serverless 앱 설계 (예정)
<!-- toc:end -->

## 참고 자료

- [SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [SNS](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
- [EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)
- [Event-driven architecture](https://martinfowler.com/articles/201701-event-driven.html)

Tags: Serverless, Queue, EventDriven, PubSub, Cloud
