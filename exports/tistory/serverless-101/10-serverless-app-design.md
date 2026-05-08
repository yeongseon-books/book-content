
# Serverless 앱 설계

> Serverless 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 지금까지 배운 *조각* 들을 *하나의 앱* 으로 *어떻게* 묶을까요?

> *Serverless 앱* 은 *작은 함수* 들이 *트리거* 와 *큐* 로 *연결* 된 *분산 시스템* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *설계 원칙*
- *이미지 처리 파이프라인* 예제
- *경계* 와 *책임 분리*
- *실패* 와 *재시도* 설계
- *비용* 과 *운영* 관점

## 왜 중요한가

*함수* 하나는 *쉽지만*, *수십 개* 가 *얽히면* *분산 시스템* 의 *함정* 이 *그대로* 등장합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Client["client"] --> API["API Gateway"]
    API --> Upload["upload fn"]
    Upload --> S3["object store"]
    S3 --> Trigger["s3 event"]
    Trigger --> Queue["queue"]
    Queue --> Worker["worker fn"]
    Worker --> DB["dynamo / sql"]
    Worker --> Notify["notify fn"]
```

## 핵심 용어 정리

- **edge function**: *요청 진입점* 의 *얇은 함수*.
- **worker function**: *백그라운드 처리* 함수.
- **idempotency key**: *중복 처리* 방지 키.
- **dead-letter queue**: *실패 메시지* 격리.
- **bounded context**: *책임 단위*.

## Before/After

**Before**: *모놀리식 함수* 하나가 *업로드*, *변환*, *알림* 을 *모두* 처리.

**After**: *업로드*, *변환*, *알림* 을 *큐* 로 *분리* 하고 *각자* *재시도*.

## 실습: 이미지 처리 파이프라인

### 1단계 — 업로드 함수

```python
def upload(event):
    user = event["user_id"]
    key = f"raw/{user}/{event['filename']}"
    s3.put_object(Bucket="uploads", Key=key, Body=event["body"])
    return {"key": key}
```

### 2단계 — S3 이벤트 → 큐

```python
def on_object_created(event):
    for r in event["Records"]:
        sqs.send_message(
            QueueUrl=Q,
            MessageBody=json.dumps({"key": r["s3"]["object"]["key"]}),
        )
```

### 3단계 — 워커 함수 (멱등)

```python
def worker(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        key = msg["key"]
        if already_done(key):
            continue
        thumb = make_thumbnail(key)
        save(key, thumb)
        mark_done(key)
```

### 4단계 — 알림 함수

```python
def notify(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        push(msg["user_id"], "썸네일이 준비되었습니다")
```

### 5단계 — 실패 격리

```python
# 큐 정책 (의사 코드)
queue_policy = {
    "VisibilityTimeout": 60,
    "MaxReceiveCount": 5,
    "DeadLetterQueue": "arn:.../thumb-dlq",
}
```

## 이 코드에서 주목할 점

- *경계* 가 *큐* 로 *명시*.
- *멱등성* 이 *재시도* 의 *전제*.
- *DLQ* 가 *조용한 실패* 를 *드러냄*.

## 자주 하는 실수 5가지

1. ***업로드* 함수에서 *변환* 까지 처리.**
2. ***멱등 키* 누락으로 *중복* 처리.**
3. ***DLQ* 미설정으로 *메시지 유실*.**
4. ***재시도* 폭주로 *DB* 과부하.**
5. ***로그* 만 보고 *지표* 무시.**

## 실무에서는 이렇게 쓰입니다

*모바일 앱* 의 *프로필 사진 업로드*, *영수증 OCR*, *동영상 트랜스코딩* 모두 *같은 패턴* 입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *경계* 가 *시스템* 의 *진짜 설계*.
- *큐* 는 *시간* 을 *완충* 함.
- *멱등성* 은 *비용* 이 아니라 *기본*.
- *DLQ* 는 *운영* 의 *눈*.
- *비용* 과 *복잡도* 는 *함께* 본다.

## 체크리스트

- [ ] *함수 경계* 정의.
- [ ] *멱등 키* 적용.
- [ ] *DLQ* 설정.
- [ ] *비용 모델* 작성.

## 연습 문제

1. *멱등 키* 의 의미 한 줄로.
2. *DLQ* 의 역할 한 줄로.
3. *큐* 가 *완충* 한다는 의미 한 줄로.

## 정리 및 다음 단계

10화 완주 축하합니다. *작은 함수* 들이 *큐* 와 *트리거* 로 *엮인* *분산 시스템* 으로 한 단계 나아가세요.

- [Serverless란 무엇인가?](./01-what-is-serverless.md)
- [Function as a Service](./02-function-as-a-service.md)
- [Trigger와 Event](./03-trigger-and-event.md)
- [Cold Start](./04-cold-start.md)
- [Scaling](./05-scaling.md)
- [State 관리](./06-state-management.md)
- [Queue와 Event-driven Architecture](./07-queue-and-event-driven.md)
- [Observability](./08-observability.md)
- [Cost](./09-cost.md)
- **Serverless 앱 설계 (현재 글)**
## 참고 자료

- [AWS Serverless Application Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)
- [Serverless Patterns Collection](https://serverlessland.com/patterns)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Idempotency in Serverless](https://docs.powertools.aws.dev/lambda/python/latest/utilities/idempotency/)

Tags: Serverless, Architecture, DesignPattern, Cloud, FinOps

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
