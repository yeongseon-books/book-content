---
series: observability-101
episode: 4
title: 구조화된 로깅
status: publish-ready
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
seo_description: JSON 로그와 상관관계 ID로 운영 로그를 질의 가능한 데이터로 바꾸는 방법을 설명합니다
last_reviewed: '2026-05-12'
---

# 구조화된 로깅

장애가 났을 때 로그가 있는데도 답을 찾지 못하는 경우가 많습니다. 로그 줄 수는 많은데 검색어를 조금만 바꾸면 결과가 달라지고, 같은 요청의 여러 줄이 서로 이어지지 않기 때문입니다. 자유 형식 문장은 읽기에는 편하지만 질의에는 약합니다.

구조화된 로깅은 이 문제를 정면으로 다룹니다. 로그를 설명문이 아니라 데이터로 남기면, 운영자는 문자열을 감으로 뒤지는 대신 필드 기반 질의를 할 수 있습니다.

이 글은 Observability 101 시리즈의 4번째 글입니다.

## 이 글에서 다룰 문제

- 왜 자유 형식 로그는 운영에서 금방 한계에 부딪힐까요?
- 구조화된 로그는 무엇이 다를까요?
- 로그 수준은 어떤 기준으로 나눠야 할까요?
- 요청 단위 상관관계 ID는 어떻게 흘려야 할까요?
- 민감 정보는 로그에서 어떻게 다뤄야 할까요?

> 좋은 로그는 사람이 읽기 좋은 문장보다 기계가 질의하기 좋은 이벤트에 가깝습니다. 로그 한 줄이 JSON이 되는 순간, 검색은 추측이 아니라 질의가 됩니다.

## 왜 중요한가

운영에서는 장애 후 5분이 특히 중요합니다. 그 시간 안에 책임 서비스와 실패 이유를 좁히지 못하면, 팀은 금방 여러 가설을 동시에 따라가기 시작합니다. 로그가 질의 가능하지 않으면 이 첫 5분이 길어집니다.

구조화된 로그는 이 시간을 줄입니다. level, event, request_id, user_id, reason 같은 필드가 분리되어 있으면 특정 사용자, 특정 요청, 특정 에러 유형만 바로 골라 볼 수 있습니다. 로그가 데이터가 되는 순간, 장애 대응 속도가 달라집니다.

## 한눈에 보는 구조

```mermaid
flowchart LR
    Code["애플리케이션 코드"] --> Logger["로거"]
    Logger --> JSON["JSON 한 줄"]
    JSON --> Sink["수집 저장소"]
    Sink --> Query["질의"]
```

## 핵심 용어

- 로그 수준: DEBUG, INFO, WARNING, ERROR, CRITICAL처럼 중요도를 나누는 기준입니다.
- 구조화 필드: 이벤트를 설명하는 key=value 데이터입니다.
- 상관관계 ID: 하나의 요청을 여러 로그 줄로 묶는 식별자입니다.
- 저장 대상: 로그가 최종적으로 적재되는 위치입니다.
- 샘플링: 로그 양이 너무 많을 때 일부만 남기는 전략입니다.

## 바꾸기 전과 후

바꾸기 전에는 `print(f"user {uid} failed: {e}")` 같은 줄이 쌓입니다. 사람 눈으로는 이해되지만, 사용자별 실패 건수를 집계하거나 같은 요청의 흐름만 모아 보려면 곧 한계가 옵니다.

바꾼 뒤에는 `logger.error("login_failed", user_id=uid, reason=str(e))`처럼 이벤트와 필드가 나뉩니다. 이제 로그는 읽는 문장인 동시에 질의 가능한 데이터가 됩니다.

## 실습: 구조화된 로깅을 다섯 단계로 붙이기

### 1단계 — 기본 로거 만들기

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

기본 로거만으로도 print보다 낫습니다. 최소한 수준 구분이 생기고, 출력 경로를 통제할 수 있기 때문입니다.

### 2단계 — 구조화 출력 형식 붙이기

```python
import json, logging

class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"lvl": r.levelname, "msg": r.getMessage(),
                            **getattr(r, "extra", {})})

h = logging.StreamHandler(); h.setFormatter(JsonFmt())
log = logging.getLogger("app"); log.addHandler(h); log.setLevel("INFO")
```

한 줄이 JSON으로 바뀌는 순간 필드 기반 검색이 가능해집니다. 이 변화 하나만으로도 로그 분석 방식이 크게 달라집니다.

### 3단계 — 맥락 필드 넣기

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

로그는 사건만 남기면 부족합니다. 누구 요청이었는지, 어떤 주문이었는지, 어느 경로였는지 같은 맥락이 있어야 장애를 좁힐 수 있습니다.

### 4단계 — 상관관계 식별자 전달하기

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

상관관계 ID가 있으면 같은 요청의 여러 줄을 하나로 묶을 수 있습니다. 분산 시스템에서는 trace_id나 request_id가 로그의 기본 필드라고 생각하는 편이 좋습니다.

### 5단계 — 수준 정책 정하기

```text
DEBUG    → development detail
INFO     → normal events
WARNING  → cautions (actionable)
ERROR    → failed requests
CRITICAL → system risk
```

모든 로그를 INFO로 남기면 중요한 줄이 묻힙니다. 수준 정책은 저장량과 주목도를 동시에 통제하는 장치입니다.

## 이 코드에서 먼저 봐야 할 점

- `extra`를 이용하면 임의의 필드를 자연스럽게 붙일 수 있습니다.
- 상관관계 ID는 가능한 한 모든 요청 로그에 실려야 합니다.
- JSON 한 줄 형식은 Loki, ELK, BigQuery 같은 여러 저장소로 쉽게 보낼 수 있습니다.

## 자주 하는 실수 다섯 가지

1. print만 사용합니다. 검색과 집계가 금방 막힙니다.
2. 모든 로그를 INFO로 남깁니다. 진짜 신호가 묻힙니다.
3. 개인정보를 그대로 기록합니다. 보안과 규정 준수 문제가 생깁니다.
4. 메시지 문자열 안에만 정보를 넣습니다. 필드가 없으니 질의가 약해집니다.
5. 스택 트레이스를 한 줄로 뭉개서 남깁니다. 읽기와 분석이 모두 어려워집니다.

## 실무에서는 이렇게 생각한다

대부분의 팀은 JSON 로그를 Loki나 ELK로 보내고, 상관관계 ID로 트레이스와 연결합니다. 로그는 더 많이 남기는 것보다 더 잘 질의할 수 있게 남기는 편이 중요합니다.

또 하나 잊기 쉬운 점은 개인정보 처리입니다. 운영에 유용하다는 이유로 원문 데이터를 전부 남기기 시작하면, 로그는 가장 빠르게 위험해지는 저장소가 됩니다. 마스킹과 해시 정책은 로깅 설계의 일부여야 합니다.

## 체크리스트

- [ ] JSON 한 줄 형식으로 로그를 남깁니다.
- [ ] 로그 수준 정책이 있습니다.
- [ ] 상관관계 ID를 전파합니다.
- [ ] 민감 정보 마스킹 규칙이 있습니다.

## 연습 문제

1. 기존 print 한 줄을 구조화된 로그로 바꿔 보세요.
2. 미들웨어에서 상관관계 ID를 주입해 보세요.
3. 특정 사용자 ID의 ERROR 로그만 조회하는 질의를 설계해 보세요.

## 정리

구조화된 로그는 운영 로그를 설명문에서 데이터로 바꿉니다. 로그 수준, 맥락 필드, 상관관계 ID가 자리 잡으면 장애 대응의 첫 5분이 짧아집니다. 다음 글에서는 요청이 여러 서비스를 가로지를 때 왜 분산 트레이싱이 필요한지 이어서 보겠습니다.

<!-- toc:begin -->
- [관측성이란 무엇인가?](./01-what-is-observability.md)
- [메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [메트릭 수집과 시각화](./03-metric-collection.md)
- **구조화된 로깅 (현재 글)**
- 분산 트레이싱 기초 (예정)
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)
<!-- toc:end -->

## 참고 자료

- [Python logging](https://docs.python.org/3/library/logging.html)
- [structlog](https://www.structlog.org/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [Twelve-factor logs](https://12factor.net/logs)

Tags: Observability, Logging, Python, JSON, DevOps
