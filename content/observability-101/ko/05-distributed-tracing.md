---
series: observability-101
episode: 5
title: 분산 트레이싱 기초
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
  - Tracing
  - OpenTelemetry
  - SRE
  - Microservices
seo_description: span, trace, context propagation과 OpenTelemetry로 첫 추적을 만드는 흐름을 설명합니다
last_reviewed: '2026-05-12'
---

# 분산 트레이싱 기초

메트릭으로는 느려졌다는 사실을 볼 수 있고, 로그로는 어떤 사건이 있었는지 읽을 수 있습니다. 그런데 요청 하나가 다섯 개 서비스와 두 개 저장소를 거친 뒤 실패했다면, 어느 구간이 병목이었는지 찾는 일은 여전히 어렵습니다.

분산 트레이싱은 이 빈칸을 메웁니다. 요청 하나를 여러 구간으로 나눠 기록하고, 그 구간들을 하나의 흐름으로 묶어 주면 어디서 오래 걸렸는지 바로 보이기 시작합니다.

이 글은 Observability 101 시리즈의 5번째 글입니다.

## 이 글에서 다룰 문제

- 스팬과 트레이스는 각각 무엇일까요?
- 요청이 여러 서비스를 지날 때 문맥 전파는 왜 중요할까요?
- 샘플링은 왜 비용 통제의 핵심일까요?
- OpenTelemetry로 첫 트레이스를 어떻게 만들 수 있을까요?
- 분산 트레이싱 없이 운영하면 무엇이 가장 어려울까요?

> 트레이스는 요청 하나의 지도입니다. 로그가 사건의 주석이라면, 트레이스는 그 사건이 어디서 일어났는지 보여 주는 경로입니다.

## 왜 중요한가

마이크로서비스 환경에서는 느린 요청의 원인을 로그만으로 찾기 어렵습니다. 서비스 A의 로그는 정상처럼 보이고, 서비스 B의 로그도 큰 문제가 없어 보이는데, 실제로는 둘 사이 호출이 길어졌을 수 있습니다. 메트릭도 어느 시점부터 느려졌는지는 알려 주지만, 한 요청이 어디에서 막혔는지는 설명하지 못합니다.

분산 트레이싱이 필요한 이유는 요청을 전체 흐름으로 보기 위해서입니다. 하나의 요청이 어떤 서비스와 데이터베이스를 거쳤고, 어느 스팬이 길었고, 어떤 부모-자식 관계로 이어졌는지를 한눈에 보여 주면 원인 파악 시간이 크게 줄어듭니다.

## 한눈에 보는 구조

```mermaid
flowchart LR
    R["요청"] --> A["서비스 A 스팬"]
    A --> B["서비스 B 스팬"]
    A --> C["서비스 C 스팬"]
    B --> D["데이터베이스 스팬"]
```

## 핵심 용어

- 트레이스: 하나의 요청 전체 흐름입니다.
- 스팬: 트레이스 안의 개별 구간입니다.
- 부모와 자식: 스팬 사이의 호출 관계입니다.
- 문맥 전파: trace_id 같은 정보를 헤더로 전달해 다음 서비스가 같은 요청으로 이어받게 하는 과정입니다.
- 샘플링: 모든 트레이스를 저장하지 않고 일부만 남기는 전략입니다.

## 바꾸기 전과 후

바꾸기 전에는 로그를 검색하며 어느 서비스가 느렸는지 추측합니다. 같은 요청의 로그를 겨우 모아도 실제 병목 구간을 확신하기 어렵습니다.

바꾼 뒤에는 트레이스 화면에서 느린 스팬이 바로 보입니다. 어느 서비스 호출이 길었는지, 부모 스팬과 자식 스팬이 어떻게 이어졌는지 한눈에 읽을 수 있습니다.

## 실습: 첫 트레이스를 다섯 단계로 만들기

### 1단계 — 추적 라이브러리 설치

```bash
pip install opentelemetry-api opentelemetry-sdk \
            opentelemetry-exporter-otlp
```

첫 단계는 표준 도구를 준비하는 일입니다. OpenTelemetry는 수집 표준을 통일해 주기 때문에, 나중에 백엔드를 바꾸더라도 코드 구조를 크게 흔들지 않게 도와줍니다.

### 2단계 — 추적기 설정

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

추적기를 초기화하면 애플리케이션이 스팬을 만들 수 있습니다. 처음에는 콘솔 출력만으로도 흐름을 이해하기에 충분합니다.

### 3단계 — 첫 스팬 만들기

```python
with tracer.start_as_current_span("handle_request") as s:
    s.set_attribute("user_id", 42)
    with tracer.start_as_current_span("db_query"):
        pass
```

한 요청을 상위 스팬과 하위 스팬으로 나누면 호출 구조가 드러납니다. 어느 구간이 자식 스팬인지 보이기 시작하면 병목 위치를 훨씬 빨리 좁힐 수 있습니다.

### 4단계 — 문맥 전파하기

```python
from opentelemetry.propagate import inject, extract

headers = {}
inject(headers)                  # before call: inject trace_id
ctx = extract(incoming_headers)  # at receiver: restore from headers
```

문맥 전파가 빠지면 트레이스는 중간에서 끊깁니다. 서비스가 둘 이상이면 헤더로 trace_id를 넘기는 일은 선택이 아니라 기본입니다.

### 5단계 — 샘플링 걸기

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
TracerProvider(sampler=TraceIdRatioBased(0.1))   # 10% only
```

모든 트레이스를 100% 저장하면 비용이 빠르게 커집니다. 샘플링은 부끄러운 절충이 아니라, 분산 트레이싱을 오래 운영하기 위한 기본 장치입니다.

## 이 코드에서 먼저 봐야 할 점

- 하나의 트레이스는 여러 스팬으로 이루어진 트리입니다.
- `traceparent` 헤더는 문맥 전파의 표준입니다.
- 샘플링 비율은 곧 비용과 가치의 균형점입니다.

## 자주 하는 실수 다섯 가지

1. 모든 트레이스를 100% 저장합니다. 비용이 빠르게 폭증합니다.
2. 문맥 전파를 빼먹습니다. 트레이스가 중간에서 끊깁니다.
3. 스팬 속성을 너무 많이 붙입니다. 카디널리티가 커집니다.
4. 비동기 코드에서 문맥을 잃습니다. 부모-자식 관계가 흐려집니다.
5. 트레이스만 보고 메트릭을 무시합니다. 전체 추세를 놓칩니다.

## 실무에서는 이렇게 생각한다

실무에서는 OpenTelemetry로 수집한 트레이스를 Tempo, Jaeger, Honeycomb 같은 백엔드로 보내고, 로그와 메트릭과 연결해서 봅니다. 이 연결이 있어야 느린 요청 하나를 전체 흐름 속에서 읽을 수 있습니다.

시니어 엔지니어는 스팬 이름과 문맥 전파를 특히 신경 씁니다. 이름이 제각각이면 읽기가 어렵고, 전파가 끊기면 트레이스 자체가 신뢰를 잃습니다. 좋은 트레이싱은 도구보다 일관성에서 나옵니다.

## 체크리스트

- [ ] 첫 스팬을 콘솔이나 백엔드에서 확인했습니다.
- [ ] `traceparent` 헤더의 역할을 이해합니다.
- [ ] 샘플링 비율을 정했습니다.
- [ ] 로그에 trace_id를 함께 남깁니다.

## 연습 문제

1. 두 서비스 사이에 문맥 전파를 연결해 보세요.
2. 환경별로 다른 샘플링 비율을 설계해 보세요.
3. 가장 느린 스팬을 찾는 질의를 하나 구상해 보세요.

## 정리

분산 트레이싱은 요청 하나의 흐름을 지도처럼 보여 줍니다. 스팬, 문맥 전파, 샘플링이 자리 잡으면 여러 서비스를 가로지르는 장애도 훨씬 빨리 좁힐 수 있습니다. 다음 글에서는 이렇게 모인 신호를 어떤 화면으로 보여 줘야 운영에 도움이 되는지, 대시보드 설계를 다루겠습니다.

<!-- toc:begin -->
- [관측성이란 무엇인가?](./01-what-is-observability.md)
- [메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [메트릭 수집과 시각화](./03-metric-collection.md)
- [구조화된 로깅](./04-structured-logging.md)
- **분산 트레이싱 기초 (현재 글)**
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)
<!-- toc:end -->

## 참고 자료

- [OpenTelemetry tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Jaeger architecture](https://www.jaegertracing.io/docs/latest/architecture/)
- [Sampling strategies](https://opentelemetry.io/docs/concepts/sampling/)

Tags: Observability, Tracing, OpenTelemetry, SRE, Microservices
