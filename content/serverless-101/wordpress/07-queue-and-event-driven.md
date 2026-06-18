---
title: "바이브코딩을 위한 Serverless 기초 (7/10): 큐와 이벤트 기반 아키텍처"
series: serverless-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Serverless
  - Queue
  - EventDriven
  - Cloud
---

# 바이브코딩을 위한 Serverless 기초 (7/10): 큐와 이벤트 기반 아키텍처

이 글은 "바이브코딩을 위한 Serverless 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 서비스 간 연결 코드를 빠르게 만들어 줍니다. 그런데 A 서비스가 B를 직접 부르고, B가 다시 C를 부르는 동기 호출 사슬은 한 지점이 느려지거나 실패하는 순간 전체를 함께 흔듭니다. 주문 API가 결제, 메일, 통계를 순서대로 직접 호출한다면, 메일 서비스 하나만 느려져도 주문 응답 전체가 늦어집니다.

서버리스 환경에서 이 문제는 더 심각해집니다. 함수는 짧고 빠르게 확장되지만, 모든 후속 작업을 한 번의 요청 안에서 끝내려 하면 지연 시간과 실패 범위가 함께 커집니다. 큐와 이벤트 버스는 생산자와 소비자의 시간 축을 분리하고 책임을 분리합니다.

AI가 만든 코드에서 서비스 간 직접 호출이 체인으로 이어져 있다면, 큐와 팬아웃으로 분리할 수 있는지 확인해야 합니다. 특히 재시도와 실패 격리가 빠진 이벤트 기반 코드는 DLQ 없이 메시지를 조용히 잃을 수 있습니다.

> **핵심 인사이트:** 큐는 단순한 버퍼가 아니라 설계 경계입니다. 생산자와 소비자가 서로의 내부를 몰라도 되고, 각자의 속도와 재시도 정책을 독립적으로 가질 수 있습니다. DLQ 없이 이벤트 기반 아키텍처를 구성하면 반복 실패 메시지가 조용히 사라집니다.

## 이 글에서 다룰 문제

- 직접 호출 없이 서비스를 연결하려면 무엇이 필요할까요?
- 큐와 토픽(팬아웃)은 어떤 점이 다를까요?
- 멱등성이 없으면 이벤트 기반 시스템에서 왜 위험할까요?
- DLQ(Dead Letter Queue)는 어떤 역할을 하나요?
- AI가 만든 이벤트 기반 코드에서 확인해야 할 것은 무엇인가요?

## 큐와 이벤트 기반 아키텍처 핵심 패턴

```python
# 1단계: 인메모리 큐 - 생산 속도와 소비 속도 분리
from collections import deque

queue = deque()
def publish(msg): queue.append(msg)
def consume(): return queue.popleft() if queue else None

# 2단계: 팬아웃 - 하나의 이벤트에서 여러 후속 작업 분기
subs = []
def subscribe(fn): subs.append(fn)
def emit(event):
    for fn in subs:
        fn(event)

# 소비자 함수: 자신의 책임만 알면 됨
def billing(event): print("bill", event)
def mail(event):    print("mail", event)
subscribe(billing)
subscribe(mail)
```

```python
# 3단계: 재시도와 DLQ - 실패 격리
def retry(handler, dlq, attempts=3):
    def wrap(event):
        for i in range(attempts):
            try:
                return handler(event)
            except Exception:
                if i == attempts - 1:
                    dlq.append(event)   # 최종 실패 격리
                    raise
    return wrap

# 멱등 처리: 같은 이벤트가 다시 와도 안전하게 처리
processed = set()
def idempotent_handler(event):
    event_id = event["id"]
    if event_id in processed:
        return   # 이미 처리됨, 건너뜀
    do_work(event)
    processed.add(event_id)
```

```yaml
# AWS SQS + Lambda: 부분 실패 응답으로 성공 메시지 재처리 방지
Events:
  StandardTrigger:
    Type: SQS
    Properties:
      Queue: !GetAtt StandardQueue.Arn
      BatchSize: 10
      FunctionResponseTypes:
        - ReportBatchItemFailures   # 실패 메시지만 재시도
```

## 변경 전후 비교

**Before: 동기 호출 체인**
```text
- 주문 API → 결제 → 메일 → 통계 (순서대로 직접 호출)
- 메일 서비스 지연 → 주문 응답 전체 지연
- 메일 서비스 실패 → 주문 처리 실패로 전파
- 재시도 없음, 실패 메시지 조용히 사라짐
```

**After: 이벤트 기반 분리**
```text
- 주문 API → 주문 이벤트 발행 (빠른 응답)
- 결제/메일/통계가 각자 구독하여 독립 처리
- 한 소비자 실패가 다른 소비자에 영향 없음
- DLQ로 실패 메시지 격리 및 재처리 가능
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 모든 곳에 FIFO 큐 사용 | 처리량 제한, 불필요한 비용 | 순서가 꼭 필요한 경계에만 FIFO 적용 |
| DLQ 없이 이벤트 발행 | 반복 실패 메시지가 조용히 사라짐 | 모든 큐에 DLQ 연결 |
| 멱등성 없이 팬아웃 도입 | 중복 이벤트로 부작용 발생 | 이벤트 ID 기반 멱등 처리 |
| 이벤트 스키마 문서 없음 | 소비자가 필드 변경에 깨짐 | 이벤트 스키마를 공개 API처럼 관리 |
| 메시지 크기 한도 무시 | 큰 페이로드로 전송 실패 | S3에 저장 후 참조 키만 메시지에 포함 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"주문 처리 서버리스 아키텍처를 만들어줘.
주문 API → SQS → 결제/메일/통계 소비자 분리,
각 소비자에 DLQ 연결,
Lambda SQS 트리거에 ReportBatchItemFailures 설정,
멱등 키로 중복 처리 방지"

# AI 결과물 검증 체크포인트:
# - 모든 큐에 DLQ가 연결되어 있는가?
# - ReportBatchItemFailures가 설정되어 있는가?
# - 소비자 함수에 멱등 처리가 있는가?
# - 이벤트 스키마가 문서화되어 있는가?
# - FIFO가 꼭 필요한 경우에만 사용하는가?
```

## 운영 체크리스트

- [ ] 모든 큐에 DLQ와 알람이 함께 설정되어 있다
- [ ] 소비자 함수에 멱등 키 검증이 있다
- [ ] `ReportBatchItemFailures`로 부분 실패 처리가 설정되어 있다
- [ ] DLQ 유입률이 0.1% 미만으로 유지되는지 모니터링한다
- [ ] 이벤트 스키마가 문서화되어 있고 호환성 정책이 있다

## 처음 질문으로 돌아가기

- **직접 호출 없이 서비스를 연결하려면?** 큐나 이벤트 버스를 통해 생산자와 소비자를 분리합니다. 생산자는 이벤트를 발행하고 끝납니다. 소비자는 자기 속도로 처리합니다. 한 소비자의 실패가 전체 흐름을 멈추지 않습니다.
- **큐와 토픽(팬아웃)의 차이는?** 큐는 하나의 소비자 그룹이 메시지를 나눠 처리합니다(작업 분산). 토픽은 하나의 이벤트를 여러 소비자가 각자 처리합니다(팬아웃). 결제, 메일, 통계를 분리하려면 토픽이 적합합니다.
- **멱등성이 중요한 이유는?** 네트워크 문제로 같은 메시지가 두 번 이상 전달될 수 있습니다. 멱등 처리가 없으면 결제가 두 번 청구되거나 메일이 두 번 발송됩니다. 이벤트 ID를 저장해 중복 처리를 건너뛰는 패턴이 필수입니다.

## 정리

바이브코딩에서 AI가 만든 이벤트 기반 코드에서 DLQ, 멱등 처리, `ReportBatchItemFailures`, 이벤트 스키마 문서를 반드시 확인하세요. 큐는 단순 전송 수단이 아니라 시스템 경계를 정의하는 아키텍처 도구입니다. 다음 글에서는 서버리스 환경에서의 관측성을 다룹니다.

## 참고 자료

- [Amazon SQS 개발자 가이드](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [이벤트 기반 아키텍처 — Martin Fowler](https://martinfowler.com/articles/201701-event-driven.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Serverless 기초 (1/10): 서버리스란 무엇인가?
- 바이브코딩을 위한 Serverless 기초 (2/10): 함수형 서비스(FaaS)
- 바이브코딩을 위한 Serverless 기초 (3/10): 트리거와 이벤트
- 바이브코딩을 위한 Serverless 기초 (4/10): 콜드 스타트
- 바이브코딩을 위한 Serverless 기초 (5/10): 스케일링
- 바이브코딩을 위한 Serverless 기초 (6/10): 상태 관리
- **바이브코딩을 위한 Serverless 기초 (7/10): 큐와 이벤트 기반 아키텍처 (현재 글)**
- 바이브코딩을 위한 Serverless 기초 (8/10): 관측성
- 바이브코딩을 위한 Serverless 기초 (9/10): 비용
- 바이브코딩을 위한 Serverless 기초 (10/10): 서버리스 앱 설계
<!-- toc:end -->

Tags: 바이브코딩, Serverless, Queue, EventDriven, Cloud
