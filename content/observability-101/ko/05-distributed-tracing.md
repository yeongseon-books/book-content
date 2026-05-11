---
series: observability-101
episode: 5
title: 분산 트레이싱 기초
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
  - Tracing
  - OpenTelemetry
  - SRE
  - Microservices
seo_description: Span, trace, context propagation 그리고 OpenTelemetry로 첫 trace 만들기
last_reviewed: '2026-05-11'
---

# 분산 트레이싱 기초

> Observability 101 시리즈 (5/10)


## 이 글에서 다룰 문제

Microservice 환경에서 느린 요청의 원인을 찾으려면, log 와 metric 만으로는 한계가 분명합니다. 이때 trace 가 가장 직접적인 답을 줍니다.

> Trace 없이 분산 시스템을 디버깅하는 일은 눈을 감고 미로를 걷는 것과 비슷합니다.

## 전체 흐름
```mermaid
flowchart LR
    R["요청"] --> A["service A (span)"]
    A --> B["service B (span)"]
    A --> C["service C (span)"]
    B --> D["DB span"]
```

## Before/After

**Before**: log 를 `grep` 하며 어느 서비스가 느렸는지 짐작합니다.

**After**: trace UI 에서 느린 span 이 즉시 보입니다.

## 첫 Trace 5단계

### 1단계 — OpenTelemetry 설치

```bash
pip install opentelemetry-api opentelemetry-sdk \
            opentelemetry-exporter-otlp
```

### 2단계 — Tracer 설정

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, ConsoleSpanExporter)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer("app")
```

### 3단계 — 첫 span

```python
with tracer.start_as_current_span("handle_request") as s:
    s.set_attribute("user_id", 42)
    with tracer.start_as_current_span("db_query"):
        pass
```

### 4단계 — Context propagation (HTTP 헤더)

```python
from opentelemetry.propagate import inject, extract

headers = {}
inject(headers)              # 호출 전: trace_id 를 헤더에 주입
ctx = extract(incoming_headers)  # 수신 측: 헤더에서 복원
```

### 5단계 — Sampling

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
TracerProvider(sampler=TraceIdRatioBased(0.1))   # 10% 만
```

## 이 코드에서 주목할 점

- 한 trace 는 여러 span 으로 이루어진 트리입니다.
- 헤더 `traceparent` 가 표준입니다 (W3C Trace Context).
- Sampling 은 비용 통제의 핵심입니다.

## 자주 하는 실수 5가지

1. **모든 trace 를 100% 저장합니다.** 비용이 급격히 커집니다.
2. **Context 를 전달하지 않습니다.** trace 가 중간에서 끊깁니다.
3. **Span 에 attribute 를 너무 많이 넣습니다.** cardinality 가 폭발합니다.
4. **Async 코드에서 context 를 잃습니다.** 부모 추적이 실패합니다.
5. **Trace 만 보고 metric 을 무시합니다.** 전체 추세를 놓칩니다.

## 실무에서는 이렇게 쓰입니다

실무에서는 OpenTelemetry 데이터를 Tempo / Jaeger / Honeycomb 으로 보내고, Grafana 에서 trace, log, metric 을 한 화면에서 함께 봅니다.

## 체크리스트

- [ ] 첫 span 을 콘솔에서 확인합니다.
- [ ] `traceparent` 헤더의 의미를 이해합니다.
- [ ] Sampling 비율을 정합니다.
- [ ] log 에 `trace_id` 를 넣습니다.

## 정리 및 다음 단계

Trace 가 흐르면 요청의 전체 흐름이 보입니다. 다음 글은 Dashboard 설계입니다.

<!-- toc:begin -->
- [Observability란 무엇인가?](./01-what-is-observability.md)
- [Metric, Log, Trace](./02-metric-log-trace.md)
- [Metric 수집과 시각화](./03-metric-collection.md)
- [구조화된 로깅](./04-structured-logging.md)
- **분산 트레이싱 기초 (현재 글)**
- Dashboard 설계 (예정)
- Alert와 On-Call (예정)
- SLI와 SLO 기초 (예정)
- Cost와 Cardinality (예정)
- 운영 가능한 Observability 스택 (예정)
<!-- toc:end -->

## 참고 자료

- [OpenTelemetry tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Jaeger architecture](https://www.jaegertracing.io/docs/latest/architecture/)
- [Sampling strategies](https://opentelemetry.io/docs/concepts/sampling/)

Tags: Observability, Tracing, OpenTelemetry, SRE, Microservices
