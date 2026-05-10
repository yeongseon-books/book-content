---
series: serverless-101
episode: 1
title: Serverless란 무엇인가?
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
  - Cloud
  - FaaS
  - Architecture
  - DevOps
seo_description: Serverless의 정의와 FaaS, 사용량 기반 과금, 운영 부담 감소가 어떻게 결합되는지 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# Serverless란 무엇인가?

> Serverless 101 시리즈 (1/10)


## 이 글에서 다룰 문제

*인프라* 에 *시간* 을 덜 쓰면 *제품* 에 더 쓸 수 있습니다. *Serverless* 는 *작은 팀* 의 *지렛대* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Event["event"] --> Platform["serverless platform"]
    Platform --> Func["function"]
    Func --> Result["response / side effect"]
```

## Before/After

**Before**: *24시간* 떠 있는 *서버*, 트래픽 *0* 일 때도 *비용*.

**After**: *호출* 한 만큼만 *비용*, *프로비저닝* 없음.

## 실습: 가장 작은 함수

### 1단계 — Python 함수 작성

```python
def handler(event, context):
    name = event.get("name", "world")
    return {"message": f"hello, {name}"}
```

### 2단계 — 로컬에서 호출 시뮬레이션

```python
def invoke_local(handler, event):
    return handler(event, context=None)

print(invoke_local(handler, {"name": "Alice"}))
```

### 3단계 — 이벤트 형태 익히기

```python
http_event = {"path": "/hello", "method": "GET", "name": "Bob"}
queue_event = {"records": [{"body": "msg-1"}, {"body": "msg-2"}]}
```

### 4단계 — 타임아웃 인지

```python
import time

def slow_handler(event, context):
    time.sleep(0.1)
    return {"ok": True}
```

### 5단계 — 결과를 표준 형태로

```python
def http_response(status, body):
    return {"statusCode": status, "body": body}
```

## 이 코드에서 주목할 점

- *event* 와 *context* 두 인자 형태가 *공통*.
- *함수* 는 *짧고 결정적* 이어야 함.
- *상태* 는 *함수 외부* 에 둔다.

## 자주 하는 실수 5가지

1. ***장시간 실행* 작업을 *함수* 로 짜기.**
2. ***로컬 파일* 에 상태 저장.**
3. ***콜드 스타트* 무시.**
4. ***비용* 을 *호출 수* 만으로 추정.**
5. ***관측성* 없이 운영 시작.**

## 실무에서는 이렇게 쓰입니다

*이벤트 처리, ETL, API 백엔드, 스케줄 작업* 등 *짧고 독립적* 인 작업에 잘 맞습니다.

## 체크리스트

- [ ] *함수* 가 *짧고* *결정적*.
- [ ] *상태* 외부화.
- [ ] *비용 모델* 검토.
- [ ] *관측성* 준비.

## 정리 및 다음 단계

다음 글은 *FaaS* 의 구조와 사용 패턴을 자세히 다룹니다.

<!-- toc:begin -->
- **Serverless란 무엇인가? (현재 글)**
- Function as a Service (예정)
- Trigger와 Event (예정)
- Cold Start (예정)
- Scaling (예정)
- State 관리 (예정)
- Queue와 Event-driven Architecture (예정)
- Observability (예정)
- Cost (예정)
- Serverless 앱 설계 (예정)
<!-- toc:end -->

## 참고 자료

- [AWS Lambda 개요](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Google Cloud Functions](https://cloud.google.com/functions/docs)
- [Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- [Serverless 정의 (Martin Fowler)](https://martinfowler.com/articles/serverless.html)

Tags: Serverless, Cloud, FaaS, Architecture, DevOps
