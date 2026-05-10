---
series: serverless-101
episode: 5
title: Scaling
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
  - Scaling
  - Concurrency
  - Throttling
  - Cloud
seo_description: Serverless의 자동 스케일 동작과 동시성, 버스트 한도, 다운스트림 보호를 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# Scaling

> Serverless 101 시리즈 (5/10)


## 이 글에서 다룰 문제

*무한 확장* 처럼 보이지만 *DB* 와 *외부 API* 는 *유한* 합니다. *스케일* 이 *장애* 를 만들 수 있습니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Burst["request burst"] --> Func["function instances"]
    Func --> DB["downstream db"]
    Func --> API["external api"]
```

## Before/After

**Before**: *대량 호출* 로 *DB 커넥션* 폭주.

**After**: *예약 동시성* + *큐 버퍼링* 으로 *흐름 제어*.

## 실습: 스케일과 보호

### 1단계 — 동시성 추정

```python
def concurrency(rps, duration_s):
    return rps * duration_s
```

### 2단계 — 버스트 시뮬레이션

```python
import concurrent.futures as cf

def burst(call, n):
    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(lambda i: call(i), range(n)))
```

### 3단계 — 예약 동시성 (의사 코드)

```python
"""
reserved_concurrency:
  function: web
  value: 50
"""
```

### 4단계 — 큐 버퍼링

```python
def enqueue(queue, msg):
    queue.append(msg)

def drain(queue, handler, batch=10):
    chunk, queue[:] = queue[:batch], queue[batch:]
    for m in chunk:
        handler(m, None)
```

### 5단계 — 백프레셔

```python
def backoff(attempt):
    return min(2 ** attempt, 30)
```

## 이 코드에서 주목할 점

- *예약 동시성* 은 *DB 보호*.
- *큐* 는 *충격 흡수*.
- *백오프* 는 *재시도 폭주* 방지.

## 자주 하는 실수 5가지

1. ***DB 커넥션 풀* 무방비.**
2. ***버스트* 를 *지속* 으로 가정.**
3. ***외부 API* 의 *레이트 리밋* 무시.**
4. ***예약 동시성* 미설정으로 *경쟁* 함수가 *기아*.**
5. ***백오프* 없이 *즉시 재시도*.**

## 실무에서는 이렇게 쓰입니다

*스파이크* 를 *큐* 가 받고, *함수* 가 *예약 동시성* 으로 *DB* 를 보호하며 처리합니다.

## 체크리스트

- [ ] *DB* 보호 전략.
- [ ] *예약 동시성* 검토.
- [ ] *백오프* 적용.
- [ ] *외부 API* 한도 인지.

## 정리 및 다음 단계

다음 글은 *State 관리* 를 다룹니다.

<!-- toc:begin -->
- [Serverless란 무엇인가?](./01-what-is-serverless.md)
- [Function as a Service](./02-function-as-a-service.md)
- [Trigger와 Event](./03-trigger-and-event.md)
- [Cold Start](./04-cold-start.md)
- **Scaling (현재 글)**
- State 관리 (예정)
- Queue와 Event-driven Architecture (예정)
- Observability (예정)
- Cost (예정)
- Serverless 앱 설계 (예정)
<!-- toc:end -->

## 참고 자료

- [Lambda 동시성](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [Reserved/Provisioned 동시성](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)
- [SQS 버퍼링 패턴](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Throttling 가이드](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html)

Tags: Serverless, Scaling, Concurrency, Throttling, Cloud
