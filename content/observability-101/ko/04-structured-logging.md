---
series: observability-101
episode: 4
title: 구조화된 로깅
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Observability
  - Logging
  - Python
  - JSON
  - DevOps
seo_description: print 대신 JSON 로깅, level과 context를 갖춘 구조화된 log로 검색 가능한 운영
last_reviewed: '2026-05-11'
---

# 구조화된 로깅

## 이 글에서 다룰 문제

장애가 났을 때 로그는 가장 먼저 열어 보는 자료이지만, 자유 형식 문자열만 쌓아 두면 의외로 답을 빨리 찾기 어렵습니다. 검색어를 바꿔 가며 `grep` 을 반복해도 필요한 조건이 정확히 걸리지 않고, 요청 하나를 따라가기도 힘듭니다. 구조화된 로깅은 로그를 문장이 아니라 데이터로 다루게 만듭니다. 이 글에서는 왜 free-text 로그가 금방 한계에 부딪히는지, JSON 로그와 level, context, correlation ID가 운영 속도를 어떻게 바꾸는지 정리합니다.

> Observability 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

핵심 질문: 자유 형식 로그는 왜 검색 지옥 이 되고, 로그가 구조화 되면 무엇이 달라질까요?

> 구조화된 로그는 기계가 읽을 수 있는 데이터입니다. 한 줄이 JSON이면 `grep` 보다 질의가 먼저 가능합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 비정형 로그 와 구조화된 로그 의 차이
- log level 을 나누는 기준
- `request_id`, `user_id` 같은 context 를 어떻게 흘릴지
- Python `logging` 으로 JSON 로그를 내보내는 방법
- 입문 단계에서 자주 나오는 다섯 가지 실수

## 왜 중요한가

운영 장애에서 처음 5분은 매우 중요합니다. 그 시간 안에 책임 구간을 좁히려면 로그가 그냥 읽히는 수준을 넘어, 바로 질의할 수 있어야 합니다. `print` 중심 로그는 개발 초기에는 빠르지만, 요청 수가 늘고 서비스가 나뉘기 시작하면 금방 한계가 드러납니다. 반대로 이벤트 이름과 필드가 분리된 JSON 로그는 필터, 집계, 상관관계 분석이 쉬워집니다.

> 로그는 문장이 아니라 데이터입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Code["코드"] --> Logger["logger.info(event, **fields)"]
    Logger --> JSON["JSON 한 줄"]
    JSON --> Sink["수집기 (Loki / ELK)"]
    Sink --> Query["질의"]
```

## 핵심 용어

- Level: DEBUG / INFO / WARNING / ERROR / CRITICAL 구분입니다.
- Structured fields: 키와 값으로 나뉜 로그 필드입니다.
- Correlation ID: 하나의 요청을 묶는 식별자입니다.
- Sink: 로그가 모이는 저장소나 수집 시스템입니다.
- Sampling: 로그 양이 너무 많을 때 일부만 남기는 방식입니다.

## Before / After

Before: `print(f"user {uid} failed: {e}")` 같은 문자열 로그를 남깁니다. 정규식과 문자열 검색에 의존하게 됩니다.

After: `logger.error("login_failed", user_id=uid, reason=str(e))` 처럼 이벤트 이름과 필드를 나눠 남깁니다. 질의 한 번으로 조건을 좁힐 수 있습니다.

## 실습: 구조화된 로깅을 5단계로 붙이기

### 1단계 — Python `logging` 기본

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

표준 `logging` 모듈부터 시작해도 충분합니다. 중요한 것은 출력 라이브러리 자체보다 어떤 형식으로, 어떤 필드를 담아 보낼지 정하는 일입니다.

### 2단계 — JSON formatter

```python
import json, logging

class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"lvl": r.levelname, "msg": r.getMessage(),
                            **getattr(r, "extra", {})})

h = logging.StreamHandler(); h.setFormatter(JsonFmt())
log = logging.getLogger("app"); log.addHandler(h); log.setLevel("INFO")
```

이 단계에서 로그는 사람이 읽는 문장 중심 출력에서 기계가 읽는 JSON 이벤트로 바뀝니다. 로그 수집기가 어떤 제품이든, 키와 값이 분리되어 있으면 검색과 집계가 훨씬 쉬워집니다.

### 3단계 — Context 필드

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

구조화된 로깅의 핵심은 메시지에 모든 정보를 우겨 넣지 않는 데 있습니다. 사용자 ID, 경로, 주문 번호, 테넌트 ID 같은 값은 별도 필드로 남겨야 나중에 조건 필터를 바로 걸 수 있습니다.

### 4단계 — Correlation ID

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

하나의 요청이 여러 함수와 서비스를 지날수록 correlation ID의 가치가 커집니다. 이 값이 모든 로그 줄에 함께 남아 있으면 특정 요청만 뽑아 추적할 수 있고, 트레이스와 로그도 훨씬 쉽게 연결됩니다.

### 5단계 — Level 정책

```text
DEBUG    → 개발 디테일
INFO     → 정상 사건
WARNING  → 경고 (조치 가능)
ERROR    → 실패한 요청
CRITICAL → 시스템 위험
```

level은 단순한 꾸밈이 아닙니다. 알람 기준, 저장 기간, 검색 우선순위가 모두 여기서 갈립니다. 그래서 “일단 다 INFO로 남기자”는 접근은 오래 버티기 어렵습니다.

## 이 코드에서 주목할 점

- `extra` 를 이용하면 임의 필드를 추가할 수 있습니다.
- correlation ID는 모든 줄에 함께 흘러야 합니다.
- JSON 한 줄은 Loki, ELK, BigQuery 같은 도구에 고르게 잘 들어갑니다.

## 자주 하는 실수 5가지

1. `print` 만 씁니다. 검색과 집계가 금방 막힙니다.
2. 모든 로그를 INFO로 남깁니다. 진짜 신호가 소음에 묻힙니다.
3. 개인정보를 그대로 기록합니다. 운영 편의보다 규정 위반 리스크가 더 커집니다.
4. 메시지 문자열 안에 값만 보간합니다. 필드가 없으면 질의가 어려워집니다.
5. 스택 트레이스를 한 줄로 억지로 합칩니다. 읽기도 어렵고 분석도 힘들어집니다.

## 실무에서는 이렇게 보입니다

많은 팀이 JSON 로그를 Loki나 ELK로 보내고, Grafana나 Kibana에서 질의합니다. 이때 correlation ID가 있으면 로그와 트레이스를 같은 요청 단위로 묶을 수 있습니다. 구조화된 로깅은 도구를 바꾸기 쉽게 만드는 효과도 큽니다. 형식이 이미 잘 잡혀 있으면 저장소를 옮겨도 분석 방식이 크게 흔들리지 않습니다.

## 실무자는 이렇게 생각합니다

- 로그는 문장이 아니라 이벤트입니다.
- 모든 요청에는 correlation ID가 따라다녀야 합니다.
- level은 중요도보다 조치 가능성을 기준으로 나누는 편이 실용적입니다.
- 개인정보는 마스킹하거나 해시 처리합니다.
- DEBUG는 운영에서 기본적으로 끄고, 필요할 때만 켤 수 있어야 합니다.

## 체크리스트

- [ ] JSON 로그 한 줄을 출력할 수 있습니다.
- [ ] level 정책이 있습니다.
- [ ] correlation ID를 전파합니다.
- [ ] 민감 필드를 마스킹합니다.

## 연습 문제

1. 기존 `print` 한 줄을 구조화된 로그로 바꿔 보세요.
2. 미들웨어에서 correlation ID를 주입하는 흐름을 설계해 보세요.
3. 특정 user ID에 대한 ERROR 로그만 질의하는 조건을 적어 보세요.

## 다음 글로 이어가기

로그가 데이터가 되는 순간부터 질의가 시작됩니다. 다음 글에서는 여러 서비스를 가로지르는 요청 흐름을 추적하는 분산 트레이싱을 살펴보겠습니다.

<!-- toc:begin -->
- [Observability란 무엇인가?](./01-what-is-observability.md)
- [Metric, Log, Trace](./02-metric-log-trace.md)
- [Metric 수집과 시각화](./03-metric-collection.md)
- **구조화된 로깅 (현재 글)**
- 분산 트레이싱 기초 (예정)
- Dashboard 설계 (예정)
- Alert와 On-Call (예정)
- SLI와 SLO 기초 (예정)
- Cost와 Cardinality (예정)
- 운영 가능한 Observability 스택 (예정)
<!-- toc:end -->

## 참고 자료

- [Python logging](https://docs.python.org/3/library/logging.html)
- [structlog](https://www.structlog.org/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [Twelve-factor logs](https://12factor.net/logs)

Tags: Observability, Logging, Python, JSON, DevOps
