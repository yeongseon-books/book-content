---
title: "바이브코딩을 위한 Serverless 기초 (10/10): 서버리스 앱 설계"
series: serverless-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Serverless
  - Architecture
  - DesignPattern
  - Cloud
---

# 바이브코딩을 위한 Serverless 기초 (10/10): 서버리스 앱 설계

이 글은 "바이브코딩을 위한 Serverless 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 함수 하나를 만들 때는 빠르고 정확합니다. 그런데 실제 제품은 함수 하나로 끝나지 않습니다. 업로드를 받고, 후속 처리를 큐에 넘기고, 변환 결과를 저장하고, 알림을 보내고, 실패를 격리해야 합니다. 이 순간부터 우리는 여전히 분산 시스템을 설계하는 중입니다.

AI에게 "이미지 처리 서버리스 시스템을 만들어줘"라고 하면 함수 여러 개와 SAM 템플릿을 빠르게 만들어 줍니다. 그런데 "업로드 함수 안에서 변환까지 같이 처리"하거나, "멱등 키 없이 중복 처리 허용"하거나, "DLQ 없이 반복 실패 방치"하는 패턴이 나오기 쉽습니다.

서버리스 앱 설계에서 중요한 것은 함수 수가 아니라 경계입니다. 요청 경계에서 끝내야 할 일과 백그라운드로 넘겨야 할 일, 재시도로 흡수할 실패와 DLQ로 격리할 실패를 구분해야 합니다. 그래야 각 단계가 독립적으로 확장되고 독립적으로 실패할 수 있습니다.

> **핵심 인사이트:** 서버리스 앱은 트리거와 큐로 연결된 작은 함수들의 그래프이고, 아키텍처 작업의 핵심은 함수 안이 아니라 함수 사이의 경계에 있습니다. 큐는 경계를 드러내고, 멱등성은 재시도를 안전하게 만들고, DLQ는 실패를 숨기지 않게 합니다.

## 이 글에서 다룰 문제

- 여러 함수를 하나의 앱으로 엮을 때 경계를 어떻게 나눌까요?
- 업로드, 변환, 알림을 왜 한 함수에 몰아넣지 말아야 할까요?
- 멱등 키와 DLQ는 설계에서 어떤 역할을 맡을까요?
- 장애가 났을 때 어디서부터 다시 시작할 수 있어야 할까요?
- AI가 만든 서버리스 아키텍처에서 확인해야 할 것은 무엇인가요?

## 서버리스 앱 설계 핵심 패턴

```python
# 1. 엣지 함수: 얇게 유지 - 업로드만 처리하고 큐에 넘김
def upload(event):
    user = event["user_id"]
    key = f"raw/{user}/{event['filename']}"
    s3.put_object(Bucket="uploads", Key=key, Body=event["body"])
    return {"key": key}   # 변환은 여기서 하지 않음

# 2. 큐 연결: 스토리지 이벤트 → 처리 큐
def on_object_created(event):
    for r in event["Records"]:
        sqs.send_message(
            QueueUrl=Q,
            MessageBody=json.dumps({"key": r["s3"]["object"]["key"]}),
        )

# 3. 멱등 워커: 중복 메시지를 안전하게 처리
def worker(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        key = msg["key"]
        if already_done(key):   # 멱등 키 확인
            continue
        thumb = make_thumbnail(key)
        save(key, thumb)
        mark_done(key)          # 완료 기록

# 4. 알림 함수: 핵심 처리와 분리
def notify(event):
    for r in event["Records"]:
        msg = json.loads(r["body"])
        push(msg["user_id"], "썸네일이 준비되었습니다")
```

```yaml
# SAM 템플릿: 함수 경계를 인프라로 표현
Resources:
  IngestFn:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: ingest.handler
      MemorySize: 512
      Timeout: 10

  WorkQueue:
    Type: AWS::SQS::Queue
    Properties:
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt WorkDLQ.Arn
        maxReceiveCount: 5    # 5회 실패 후 DLQ로 격리

  WorkerFn:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: worker.handler
      MemorySize: 1024
      Timeout: 20
      Events:
        QueueRoute:
          Type: SQS
          Properties:
            Queue: !GetAtt WorkQueue.Arn
            BatchSize: 10
            FunctionResponseTypes:
              - ReportBatchItemFailures   # 부분 실패 처리
```

## 변경 전후 비교

**Before: 책임이 섞인 함수**
```text
- 업로드 함수가 변환, 저장, 알림까지 처리
- 알림 실패 → 전체 처리 실패로 전파
- 재시도 시 처음부터 전체 흐름 재실행
- 어디서 실패했는지 추적 어려움
```

**After: 경계가 명확한 파이프라인**
```text
- 업로드 → 큐 → 변환 → 알림 (단계별 분리)
- 알림 실패가 변환 성공에 영향 없음
- 실패한 단계부터만 재시작 가능
- DLQ로 반복 실패 메시지 격리 및 추적
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 엣지 함수에 변환 로직 포함 | 응답 지연 + 실패 범위 증가 | 변환은 백그라운드 워커로 분리 |
| 멱등 키 없이 재시도 | 중복 처리로 부작용 발생 | 이벤트 ID로 멱등 처리 필수 |
| DLQ 설정 없음 | 반복 실패 메시지 조용히 사라짐 | 모든 큐에 DLQ + 알람 연결 |
| ReportBatchItemFailures 없음 | 성공 메시지까지 전체 재처리 | 배치 부분 실패 응답 설정 |
| 타임아웃 기본값 사용 | 긴 처리가 중간에 끊김 | 실제 처리 시간 기반으로 타임아웃 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이미지 처리 서버리스 파이프라인을 설계해줘.
업로드 엣지 함수 → S3 이벤트 → SQS → 썸네일 워커 → 알림 함수,
각 큐에 DLQ 연결, 워커에 멱등 처리 포함,
SAM 템플릿으로 ReportBatchItemFailures 설정"

# AI 결과물 검증 체크포인트:
# - 업로드 함수가 변환까지 같이 하는가? (분리해야 함)
# - 모든 SQS 큐에 DLQ가 연결되어 있는가?
# - 워커 함수에 멱등 키 검증이 있는가?
# - ReportBatchItemFailures가 설정되어 있는가?
# - 장애 시 어느 단계부터 재시작 가능한지 명시되어 있는가?
```

## 운영 체크리스트

- [ ] 엣지 함수는 얇게, 변환/처리는 백그라운드 워커로 분리되어 있다
- [ ] 모든 큐에 DLQ와 알람이 연결되어 있다
- [ ] 워커 함수에 멱등 키 검증이 있다
- [ ] `ReportBatchItemFailures`로 배치 부분 실패 처리가 설정되어 있다
- [ ] 장애 시 각 단계별 재시작 경로가 명확히 정의되어 있다

## 처음 질문으로 돌아가기

- **경계를 어떻게 나눌까요?** 사용자에게 빠른 응답이 필요한 부분(엣지 함수)과 시간이 걸려도 되는 처리(워커 함수)를 먼저 구분합니다. 큐로 연결하면 각 단계가 독립적으로 확장되고 실패해도 서로 영향을 주지 않습니다.
- **멱등성이 왜 기본값이어야 하는가?** 네트워크 문제로 같은 메시지가 두 번 전달될 수 있습니다. 이미지가 두 번 변환되는 건 무해해 보여도, 결제가 두 번 일어나면 심각합니다. 모든 워커 함수는 멱등 처리를 기본으로 설계해야 합니다.
- **DLQ 없으면 어떻게 되는가?** 반복 실패 메시지가 계속 재시도되다가 버려집니다. 어떤 메시지가 실패했는지, 왜 실패했는지 알 수 없습니다. DLQ가 있어야 실패 메시지를 격리하고 원인을 분석한 후 재처리할 수 있습니다.

## 정리

바이브코딩에서 AI가 만든 서버리스 아키텍처에서 경계 분리, 멱등 처리, DLQ, `ReportBatchItemFailures`를 반드시 확인하세요. 서버리스 앱 설계의 핵심은 함수를 잘게 쪼개는 데 있지 않습니다. 요청 경계, 백그라운드 작업, 실패 격리, 관측 지점을 어디에 둘지 분명히 나누는 데 있습니다. Serverless 101 시리즈를 통해 FaaS, 콜드 스타트, 스케일링, 상태 관리, 이벤트 기반, 관측성, 비용, 설계까지 서버리스 운영의 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [AWS Serverless Application Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)
- [Idempotency in AWS Powertools for Lambda](https://docs.powertools.aws.dev/lambda/python/latest/utilities/idempotency/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Serverless 기초 (1/10): 서버리스란 무엇인가?
- 바이브코딩을 위한 Serverless 기초 (2/10): 함수형 서비스(FaaS)
- 바이브코딩을 위한 Serverless 기초 (3/10): 트리거와 이벤트
- 바이브코딩을 위한 Serverless 기초 (4/10): 콜드 스타트
- 바이브코딩을 위한 Serverless 기초 (5/10): 스케일링
- 바이브코딩을 위한 Serverless 기초 (6/10): 상태 관리
- 바이브코딩을 위한 Serverless 기초 (7/10): 큐와 이벤트 기반 아키텍처
- 바이브코딩을 위한 Serverless 기초 (8/10): 관측성
- 바이브코딩을 위한 Serverless 기초 (9/10): 비용
- **바이브코딩을 위한 Serverless 기초 (10/10): 서버리스 앱 설계 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Serverless, Architecture, DesignPattern, Cloud
