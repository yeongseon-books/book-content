---
series: serverless-101
episode: 8
title: "Serverless 101 (8/10): 관측성"
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
  - Observability
  - Logging
  - Tracing
  - Metrics
seo_description: 서버리스 환경에서 로그, 지표, 분산 추적, 상관관계 ID, 샘플링을 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (8/10): 관측성

서버리스 시스템은 짧고 분산되어 있습니다. 한 요청이 하나의 함수에서 끝나지 않고 여러 함수, 큐, 데이터 저장소를 거칠 수 있습니다. 그래서 문제를 볼 때 로그만 보거나 메트릭만 봐서는 자주 길을 잃습니다.

이 글은 Serverless 101 시리즈의 8번째 글입니다.

![Serverless 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/08/08-01-concept-at-a-glance.ko.png)
*Serverless 101 8장 흐름 개요*
> 서버리스에서는 서버에 들어가 볼 수 없으므로, 관측성은 코드가 무엇을 했는지 보는 유일한 창이고 문제가 생기기 전에 미리 심어 두어야 합니다.

## 이 글에서 다룰 문제

- 함수가 왜 느렸는지, 어디서 느렸는지 어떻게 알 수 있을까요?
- 로그, 지표, 분산 추적은 각각 어떤 역할을 맡을까요?
- 상관관계 ID는 왜 거의 필수일까요?
- 왜 이 주제가 중요한가에서 가장 흔한 실수는 무엇일까요?
- 한눈에 보는 구조을 실무에 적용할 때 주의할 점은 무엇일까요?
- 핵심 용어 먼저 정리하기의 핵심 원리를 한 문장으로 설명하면 무엇일까요?

## 왜 이 주제가 중요한가

전통적인 긴 프로세스에서는 한 서버 안에서 로그를 따라가면 어느 정도 감이 왔습니다. 서버리스에서는 그렇지 않습니다. 함수는 짧게 끝나고, 같은 요청이 여러 실행 환경을 거치며, 일부는 비동기로 이어집니다. 신호를 연결해 두지 않으면 “느리다”, “가끔 실패한다” 같은 현상만 남고 원인 경로는 사라집니다.

관측성은 장애 대응 도구이기도 하지만 설계 도구이기도 합니다. 어느 필드를 로그에 남길지, 어떤 메트릭을 집계할지, 어디서 스팬을 열고 닫을지 결정하는 순간 시스템의 운영 가능성이 크게 달라집니다. 서버리스에서는 특히 이 준비를 나중으로 미루기 어렵습니다.

## 한눈에 보는 구조

이 그림이 말하는 핵심은 세 신호를 따로 모으는 것이 목적이 아니라, 서로 연결된 상태로 보는 것이 목적이라는 사실입니다. 그래야 특정 요청의 실패를 로그로 보고, 동일 시점의 지표 변화와 함께 읽고, 전체 경로를 추적으로 확인할 수 있습니다.

## 핵심 용어 먼저 정리하기

| 용어 | 뜻 | 실무에서 왜 중요한가 |
| --- | --- | --- |
| 구조화 로그 | 기계가 읽기 쉬운 형식의 로그 | 검색, 집계, 필터링이 쉬워집니다 |
| 지표 | 숫자로 표현한 운영 신호 | 추세와 임계값 감시에 적합합니다 |
| 추적 | 요청이 거친 경로를 보여 주는 신호 | 분산 호출 경로를 한 번에 볼 수 있습니다 |
| 상관관계 ID | 요청을 식별하는 공통 키 | 여러 함수 로그를 같은 요청으로 묶습니다 |
| 샘플링 | 관측 비용과 해상도를 조절하는 기법 | 추적 비용 폭증을 막아 줍니다 |

세 신호 중 하나만으로는 부족합니다. 로그는 세부 원인을 잘 보여 주지만 전체 추세를 보기 어렵고, 지표는 추세를 잘 보여 주지만 개별 요청 맥락이 부족합니다. 추적은 경로를 보여 주지만 이벤트 내용을 충분히 담지 않습니다.

## 무엇이 달라지는지 먼저 보기

**문제가 있는 상태**에서는 평문 로그만 남기고, 필요할 때마다 문자열 검색으로 원인을 추적합니다.

**개선된 상태**에서는 상관관계 ID와 분산 추적을 함께 써서 하나의 요청이 거친 전체 흐름을 빠르게 복원합니다.

이 차이는 장애 대응 시간에서 극적으로 드러납니다. 같은 정보가 있어도 연결 방식이 다르면 원인을 찾는 속도가 크게 달라집니다.

## 관측성의 기본을 코드로 보기

### 1단계 — 구조화 로그

```python
import json, time

def log(level, msg, **fields):
    print(json.dumps({"t": time.time(), "level": level, "msg": msg, **fields}))
```

평문 로그는 읽기엔 편할 수 있지만, 집계와 검색이 어려워집니다. 구조화 로그는 필드 단위로 필터링하고 대시보드에 연결하기 쉽습니다.

### 2단계 — 상관관계 식별자 전파

```python
def with_corr(handler):
    def wrap(event, ctx):
        cid = event.get("correlation_id", "unknown")
        log("info", "start", cid=cid)
        return handler(event, ctx)
    return wrap
```

상관관계 ID는 로그 몇 줄을 예쁘게 남기기 위한 장식이 아닙니다. 여러 함수와 비동기 경계를 건너는 요청을 한 덩어리로 복원하기 위한 생명선입니다.

### 3단계 — 지표 카운트

```python
metrics = {}
def incr(name, n=1):
    metrics[name] = metrics.get(name, 0) + n
```

에러 수, 호출 수, 지연 시간 분포는 로그를 읽어 합산하는 대신 지표로 바로 집계하는 편이 훨씬 낫습니다. 알람도 이 숫자들 위에서 설계할 수 있습니다.

### 4단계 — 추적 스팬

```python
import contextlib, time

@contextlib.contextmanager
def span(name):
    t0 = time.perf_counter()
    yield
    log("info", "span", name=name, ms=(time.perf_counter() - t0) * 1000)
```

스팬은 어느 단계가 오래 걸렸는지 보여 줍니다. 함수 내부에서도 외부 API 호출, 데이터베이스 접근, 큐 발행처럼 주요 경계를 스팬으로 나누면 병목이 더 잘 보입니다.

### 5단계 — 콜드 여부 기록

```python
COLD = True

def handler(event, ctx):
    global COLD
    log("info", "invoke", cold=COLD)
    COLD = False
```

## 검증 흐름: 한 요청을 끝까지 복원할 수 있어야 합니다

관측성을 붙였다고 해서 바로 운영 가능한 상태가 되지는 않습니다. 실제로는 한 요청을 골라 끝까지 따라갈 수 있는지 확인해야 합니다.

```text
request_id=8d6...
correlation_id=ord-2026-05-12-001
cold=true
duration_ms=842
downstream=db
```

**Expected output:** 같은 상관관계 ID로 엣지 함수, 큐 소비자, 다운스트림 호출 로그를 한 번에 묶어 볼 수 있어야 합니다.

아래 네 질문에 빨리 답할 수 없다면 아직 계측이 약합니다.

- 가장 먼저 실패한 요청은 무엇인가
- 지연 원인이 콜드 스타트인가, 다운스트림 지연인가
- 어느 함수가 몇 번 재시도했는가
- 알람이 실제 행동 가능한 신호를 가리키는가

관측성의 품질은 로그 양이 아니라 이 질문들에 답하는 속도로 드러납니다.

콜드 여부를 같이 기록하면 p99 지연이 초기화 비용인지, 실제 비즈니스 처리 지연인지 더 쉽게 구분할 수 있습니다.

- 구조화 로그는 집계 가능한 로그를 만듭니다.
- 상관관계 ID는 모든 함수가 이어서 전파해야 합니다.
- 콜드 여부 기록은 지연 시간 분석의 핵심 단서입니다.

관측성은 로그를 많이 남기는 일이 아닙니다. 나중에 문제를 재구성할 수 있도록 최소한의 신호를 일관되게 남기는 일입니다.

## 실무에서 자주 헷갈리는 지점

### 로그만 잘 남기면 충분할까

아닙니다. 로그는 개별 사건을 잘 보여 주지만, 전체 추세와 경보는 지표가 더 잘 보여 줍니다. 경로 복원은 추적이 더 잘합니다.

### 모든 요청을 100퍼센트 추적해야 할까

비용과 저장량을 생각하면 항상 그렇지 않습니다. 샘플링 전략이 필요합니다. 특히 고트래픽 시스템일수록 더 그렇습니다.

### 알람은 많을수록 좋을까

실제 행동으로 이어지지 않는 알람은 오히려 관측성을 망칩니다. 알람은 많기보다 정확해야 합니다.

## 자주 하는 실수 다섯 가지

1. 평문 로그만 사용합니다.
2. 민감 정보를 그대로 로그에 남깁니다.
3. 로그만 보고 지표를 무시합니다.
4. 샘플링 없이 추적 비용을 폭증시킵니다.
5. 실행 가능한 기준 없는 알람을 너무 많이 만듭니다.

이 실수들은 대부분 관측성을 기록 기능 정도로 볼 때 생깁니다. 실제로는 운영 비용과 연결된 설계 체계이므로, 신호의 품질과 비용을 함께 관리해야 합니다.

## 실무에서는 이렇게 생각합니다

- 관측성은 설계 단계에서부터 준비합니다.
- 상관관계는 분산 시스템의 생명선입니다.
- 관측 비용도 함께 관찰해야 합니다.
- 알람은 실제 행동으로 이어져야 의미가 있습니다.
- 샘플링은 해상도와 비용의 균형입니다.

## 운영 체크리스트

- [ ] 구조화 로그를 남기는가
- [ ] 상관관계 ID를 전파하는가
- [ ] 지표와 추적을 함께 수집하는가
- [ ] 알람이 실제 대응 절차와 연결되는가
## 실무 앵커: 로그, 메트릭, 트레이스를 하나의 질문으로 묶기

관측성의 목적은 데이터 수집이 아니라 원인 추적 속도 개선입니다. 따라서 "어떤 도구를 쓸까"보다 "장애 질문을 몇 분 안에 답할 수 있는가"를 기준으로 설계해야 합니다.

### 구조화 로그와 상관관계 식별자

```python
import json
import time
import uuid

def log(level, message, **fields):
    print(json.dumps({"level": level, "message": message, **fields}, ensure_ascii=False))

def handler(event, context):
    cid = (event.get("headers") or {}).get("x-correlation-id", str(uuid.uuid4()))
    started = time.time()

    log("INFO", "request.accepted", correlationId=cid, requestId=context.aws_request_id)
    try:
        # 도메인 처리
        elapsed = int((time.time() - started) * 1000)
        log("INFO", "request.completed", correlationId=cid, durationMs=elapsed)
        return {"statusCode": 200, "body": json.dumps({"ok": True})}
    except Exception as e:
        elapsed = int((time.time() - started) * 1000)
        log("ERROR", "request.failed", correlationId=cid, durationMs=elapsed, error=str(e))
        return {"statusCode": 500, "body": json.dumps({"error": "internal_error"})}
```

동일한 `correlationId`를 로그, 트레이스, 외부 응답 헤더까지 관통시키면 사용자 문의 한 건을 시스템 내부 이벤트와 바로 연결할 수 있습니다.

### 경보 규칙 예시

```yaml
alarms:
  - name: lambda-errors-high
    metric: Errors
    threshold: 5
    period: 60
    evaluationPeriods: 3
  - name: lambda-duration-p95-high
    metric: DurationP95
    threshold: 800
    period: 60
    evaluationPeriods: 5
  - name: queue-age-too-old
    metric: ApproximateAgeOfOldestMessage
    threshold: 120
    period: 60
    evaluationPeriods: 3
```

경보는 많이 만들수록 좋은 것이 아니라, 대응 가능한 수만 남겨야 좋습니다. 경보 폭증은 관측성 성숙이 아니라 운영 피로 누적 신호입니다.

### 장애 복기 템플릿

1. 탐지 시각: 최초 경보 수신 시각
2. 영향 범위: 실패율, 지연, 사용자 수
3. 근본 원인: 코드/설정/용량/외부 의존성 중 분류
4. 영구 대책: 재현 실험, 임계치 조정, 롤백 기준

복기 템플릿을 고정해 두면 담당자가 바뀌어도 품질이 흔들리지 않습니다. 관측성의 완성도는 도구보다 팀의 기록 습관에서 결정됩니다.

### 트레이스 샘플링 정책 설계

트레이스를 전량 수집하면 분석은 쉬워지지만 비용이 빠르게 증가합니다. 반대로 샘플링을 과도하게 낮추면 희귀 장애를 놓치기 쉽습니다. 일반적으로 정상 요청은 낮은 비율로, 오류 요청은 100% 수집하는 이중 정책이 실무에서 균형이 좋습니다.

### 운영 대시보드 최소 구성

1. 사용자 관점: 성공률, p95 지연, 주요 API 오류 코드
2. 시스템 관점: Lambda 오류, 동시성, 스로틀, 콜드 스타트 비율
3. 비동기 관점: 큐 적체 시간, DLQ 유입량, 재시도 비율

대시보드는 보기 좋은 화면보다 의사결정 속도가 중요합니다. 경보가 울렸을 때 3분 안에 "영향 범위"와 "우선 완화 조치"를 정할 수 있어야 좋은 관측성입니다.

### 비용 연동 관측 지표

관측성 지표에 비용을 연결해 두면 최적화 우선순위가 선명해집니다. 예를 들어 p95 지연이 낮아졌지만 로그 저장 비용이 급증했다면, 구조화 로그 필드와 보존 기간을 다시 조정해야 합니다. 품질 개선은 단일 지표가 아니라 균형 지표로 판단해야 합니다.

## 정리

서버리스 관측성의 핵심은 신호를 많이 모으는 것이 아니라 서로 연결된 신호를 남기는 데 있습니다. 로그는 사건을, 지표는 추세를, 추적은 경로를 보여 줍니다. 이 세 가지가 함께 있어야 짧고 분산된 함수들의 세계를 운영 가능한 시스템으로 바꿀 수 있습니다.

다음 글에서는 서버리스 비용을 어떻게 읽고 설계에 반영해야 하는지 봅니다.

## 처음 질문으로 돌아가기

- **함수가 왜 느렸는지, 어디서 느렸는지 어떻게 알 수 있을까요?**
  - 전통적인 긴 프로세스에서는 한 서버 안에서 로그를 따라가면 어느 정도 감이 왔습니다
- **로그, 지표, 분산 추적은 각각 어떤 역할을 맡을까요?**
  - 관측성의 목적은 데이터 수집이 아니라 원인 추적 속도 개선입니다. 따라서 "어떤 도구를 쓸까"보다 "장애 질문을 몇 분 안에 답할 수 있는가"를 기준으로 설계해야 합니다.
- **상관관계 ID는 왜 거의 필수일까요?**
  - 전통적인 긴 프로세스에서는 한 서버 안에서 로그를 따라가면 어느 정도 감이 왔습니다
- **왜 이 주제가 중요한가에서 가장 흔한 실수는 무엇일까요?**
  - 전통적인 긴 프로세스에서는 한 서버 안에서 로그를 따라가면 어느 정도 감이 왔습니다. 서버리스에서는 그렇지 않습니다.
- **한눈에 보는 구조을 실무에 적용할 때 주의할 점은 무엇일까요?**
  - 이 그림이 말하는 핵심은 세 신호를 따로 모으는 것이 목적이 아니라, 서로 연결된 상태로 보는 것이 목적이라는 사실입니다. 그래야 특정 요청의 실패를 로그로 보고, 동일 시점의 지표 변화와 함께 읽고, 전체 경로를 추적으로 확인할 수 있습니다.
- **핵심 용어 먼저 정리하기의 핵심 원리를 한 문장으로 설명하면 무엇일까요?**
  - 세 신호 중 하나만으로는 부족합니다. 로그는 세부 원인을 잘 보여 주지만 전체 추세를 보기 어렵고, 지표는 추세를 잘 보여 주지만 개별 요청 맥락이 부족합니다. 추적은 경로를 보여 주지만 이벤트 내용을 충분히 담지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- **Serverless 101 (8/10): 관측성 (현재 글)**
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [OpenTelemetry 문서](https://opentelemetry.io/docs/)
- [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

### 패턴과 코드

- [서버리스 분산 추적](https://aws.amazon.com/blogs/compute/instrumenting-distributed-systems-for-operational-visibility/)
- [AWS Powertools for Lambda Python (GitHub)](https://github.com/aws-powertools/powertools-lambda-python)

Tags: Serverless, Observability, Logging, Tracing, Metrics
