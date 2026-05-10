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
last_reviewed: '2026-05-04'
---

# 구조화된 로깅

> Observability 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 자유 텍스트 log 는 왜 *검색이 지옥* 이고, *구조화* 하면 무엇이 달라집니까?

> *구조화된 log 는 *기계가 읽는 데이터* 입니다. 한 줄이 *JSON* 이면 *grep* 대신 *질의* 가 가능합니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *비구조* vs *구조* log 의 차이
- *Log level* 과 사용 기준
- *Context* (request_id, user_id) 전파
- Python `logging` 모듈로 *JSON* 출력
- 흔한 함정 5가지

## 왜 중요한가

장애가 났을 때 *5분 안에* 원인 줄을 찾으려면, log 가 *질의 가능* 해야 합니다. `print` 의 시대는 끝났습니다.

> *Log 는 *문장이 아니라 데이터* 다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Code["코드"] --> Logger["logger.info(event, **fields)"]
    Logger --> JSON["JSON 한 줄"]
    JSON --> Sink["수집기 (Loki / ELK)"]
    Sink --> Query["질의"]
```

## 핵심 용어 정리

- **Level**: DEBUG / INFO / WARNING / ERROR / CRITICAL.
- **Structured fields**: key=value 한 쌍씩.
- **Correlation ID**: 한 요청을 *묶는* ID.
- **Sink**: log 가 흘러가는 *목적지*.
- **Sampling**: 너무 많을 때 *일부만* 남기기.

## Before/After

**Before**: `print(f"user {uid} failed: {e}")` — 정규식 *지옥*.

**After**: `logger.error("login_failed", user_id=uid, reason=str(e))` — *질의 한 줄*.

## 실습: 구조화된 로깅 5단계

### 1단계 — Python `logging` 기본

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

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

### 3단계 — Context 필드

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

### 4단계 — Correlation ID

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

### 5단계 — Level 정책

```text
DEBUG    → 개발 디테일
INFO     → 정상 사건
WARNING  → 경고 (조치 가능)
ERROR    → 실패한 요청
CRITICAL → 시스템 위험
```

## 이 코드에서 주목할 점

- `extra` 로 *임의 필드* 를 추가한다.
- *correlation ID* 가 모든 줄에 *함께* 흐른다.
- JSON 한 줄은 *Loki, ELK, BigQuery* 어디든 들어간다.

## 자주 하는 실수 5가지

1. **`print` 만 쓴다.** 검색이 *불가능*.
2. **모든 줄을 *INFO*.** 진짜 신호가 *묻힌다*.
3. **개인정보를 *그대로* 남긴다.** 컴플라이언스 위반.
4. **메시지에 *변수 보간* 만 한다.** 필드가 없으니 *질의 불가*.
5. **Stack trace 를 *한 줄로 합친다*.** 가독성 *최악*.

## 실무에서는 이렇게 쓰입니다

대부분의 회사는 *JSON log → Loki 또는 ELK → Grafana / Kibana* 로 흐름을 만듭니다. correlation ID 가 trace 와 *연결* 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *Log 는 *문장* 이 아니라 *이벤트*.*
- *모든 요청은 *correlation ID* 를 가진다.*
- *Level 은 *조치 가능성* 으로 나눈다.*
- *PII 는 *마스킹* 또는 *해시*.*
- *DEBUG 는 *프로덕션에서 끈다*, 끄는 *스위치* 를 둔다.*

## 체크리스트

- [ ] 한 줄을 *JSON* 으로 출력한다.
- [ ] *Level* 정책을 정한다.
- [ ] *Correlation ID* 를 흘린다.
- [ ] 민감 필드를 *마스킹* 한다.

## 연습 문제

1. `print` 한 줄을 *구조화된 log* 로 바꾸세요.
2. *correlation ID* 를 미들웨어로 주입하세요.
3. 한 사용자 ID 의 모든 ERROR 를 *질의* 해 보세요.

## 정리 및 다음 단계

Log 가 *데이터* 가 되면 *질의* 가 시작됩니다. 다음 글은 *분산 트레이싱* 입니다.

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
