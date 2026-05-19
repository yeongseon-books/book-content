---
series: observability-101
episode: 10
title: 운영 가능한 관측성 스택
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Observability
  - SRE
  - OpenTelemetry
  - Grafana
  - Prometheus
seo_description: OpenTelemetry, Prometheus, Loki, Tempo, Grafana로 작은 팀의 첫 관측성 스택을 구성하는 법을 설명합니다
last_reviewed: '2026-05-15'
---

# 운영 가능한 관측성 스택

작은 팀이 관측성 스택을 고를 때 가장 흔한 실수는 완벽한 답을 기다리는 일입니다. 모든 기능이 있고, 비용도 낮고, 운영도 쉬우며, 나중에 교체도 쉬운 조합을 찾다 보면 시작 자체가 늦어집니다. 하지만 관측성은 내일의 완벽한 도구보다 오늘의 운영 가능한 조합이 더 중요합니다.

좋은 첫 스택은 화려한 스택이 아닙니다. 수집이 표준화되어 있고, 메트릭·로그·트레이스를 한 화면에서 연결해 볼 수 있고, 팀이 실제로 운영할 수 있어야 합니다. 그리고 필요할 때 일부를 바꿀 수 있어야 합니다.

이 글은 Observability 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- 작은 팀이 바로 시작할 수 있는 최소 관측성 스택은 어떤 모습일까요?
- OpenTelemetry 수집기를 왜 중심에 두는 편이 좋을까요?
- 메트릭, 로그, 트레이스를 한 화면에서 연결하려면 무엇이 필요할까요?
- 운영자 관점의 서비스 수준 목표는 왜 별도로 잡아야 할까요?
- 벤더 종속을 줄이면서도 현실적인 선택을 하려면 무엇을 봐야 할까요?

> 좋은 첫 스택은 수집과 저장, 질의가 분리되어 있고 교체 가능합니다. 수집은 표준으로 묶고, 저장소는 필요에 따라 바꿀 수 있게 두는 편이 오래 버팁니다.

## 왜 중요한가

관측성 스택은 한 번 정하면 오래 갑니다. 그래서 처음 선택이 과하게 복잡하면 운영팀이 스택 자체를 돌보느라 시간을 쓰게 됩니다. 반대로 너무 단순해서 세 신호가 서로 연결되지 않으면, 장애가 났을 때 화면 다섯 개를 오가느라 시간이 낭비됩니다.

운영 가능한 스택이 중요한 이유는 교체 가능성과 일상성에 있습니다. 작은 팀이라면 오늘 바로 올릴 수 있어야 하고, 내일 문제가 생겼을 때 누구나 흐름을 따라가 볼 수 있어야 합니다.

## 한눈에 보는 구조

![한눈에 보는 구조](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/10/10-01-concept-at-a-glance.ko.png)
*애플리케이션 신호가 OpenTelemetry 수집기를 거쳐 Prometheus, Loki, Tempo에 저장되고 Grafana에서 다시 만나는 구조*

## 핵심 용어

- 수집기: 여러 신호를 받아 적절한 저장소로 보내는 관문입니다.
- 저장 백엔드: 메트릭, 로그, 트레이스를 저장하는 시스템입니다.
- 상관관계: trace_id를 기준으로 세 신호를 연결해 보는 방식입니다.
- 데이터 소스: Grafana가 읽는 각 저장소 연결입니다.
- 대표 표본: 메트릭 지점에서 대표 trace_id를 연결하는 기능입니다.

## 바꾸기 전과 후

바꾸기 전에는 도구는 여러 개인데 서로 연결되어 있지 않습니다. 메트릭은 한 화면, 로그는 다른 화면, 트레이스는 또 다른 화면에서 보고, 같은 요청을 따라가려면 계속 복사하고 붙여 넣어야 합니다.

바꾼 뒤에는 Grafana 한 곳에서 세 신호를 오갑니다. 메트릭에서 이상 지점을 보고, 대표 trace_id로 트레이스로 점프하고, 같은 trace_id로 로그까지 내려가면 장애 대응 흐름이 훨씬 짧아집니다.

## 실습: 첫 스택을 다섯 단계로 올리기

### 1단계 — 수집기 구성하기

```yaml
receivers:
  otlp: { protocols: { grpc: {}, http: {} } }
exporters:
  prometheus:    { endpoint: ":9464" }
  loki:          { endpoint: http://loki:3100/loki/api/v1/push }
  otlp/tempo:    { endpoint: tempo:4317, tls: { insecure: true } }
service:
  pipelines:
    metrics:  { receivers: [otlp], exporters: [prometheus] }
    logs:     { receivers: [otlp], exporters: [loki] }
    traces:   { receivers: [otlp], exporters: [otlp/tempo] }
```

수집기를 하나로 통일하면 언어와 프레임워크가 달라도 수집 방식이 단순해집니다. 나중에 저장소를 바꾸더라도 애플리케이션 쪽 변경을 줄일 수 있다는 점이 특히 중요합니다.

### 2단계 — 로컬 스택 띄우기

```yaml
services:
  otel-collector: { image: otel/opentelemetry-collector }
  prometheus:     { image: prom/prometheus }
  loki:           { image: grafana/loki }
  tempo:          { image: grafana/tempo }
  grafana:        { image: grafana/grafana, ports: ["3000:3000"] }
```

Compose 기반 시작은 작은 팀에 특히 유리합니다. 전체 흐름을 한 번에 올려 보고, 어느 지점에서 신호가 끊기는지 빠르게 확인할 수 있기 때문입니다.

### 3단계 — 애플리케이션에서 신호 보내기

```python
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

애플리케이션은 가능한 한 표준 프로토콜로만 말하게 두는 편이 좋습니다. 수집기가 그다음 경로를 결정하게 만들면 코드와 인프라의 결합이 줄어듭니다.

### 4단계 — 화면 연결하기

```text
Datasources: Prometheus, Loki, Tempo
Tempo -> Loki: derived field "trace_id" -> log search
Loki  -> Tempo: log "trace_id" -> trace view
```

세 신호를 한 화면에서 연결하는 핵심은 trace_id 상관관계입니다. 이것이 없으면 도구는 세 개 있지만 스택은 절반만 완성된 상태에 가깝습니다.

### 5단계 — 운영자 목표 세우기

```text
1) /metrics scrape success > 99.5%
2) Loki ingest p95 < 5s
3) Tempo trace arrival > 99%
4) Grafana dashboard p95 < 2s
5) Alertmanager dispatch latency < 30s
```

관측성 시스템도 운영 대상입니다. 스택 자체가 느리거나 자주 끊기면 정작 장애 순간에 가장 먼저 배신합니다. 그래서 운영자 목표를 별도로 두는 편이 좋습니다.

## 스택 연결은 이렇게 검증합니다

작은 팀의 첫 스택은 기능 수보다 연결 상태가 더 중요합니다. 아래 세 가지가 모두 통과해야 "메트릭, 로그, 트레이스가 한 스택"이라고 말할 수 있습니다.

```bash
docker compose ps
curl -s http://localhost:9464/metrics | grep otelcol
curl -s http://localhost:3000/api/health
```

```text
Expected output:
- collector, prometheus, loki, tempo, grafana 컨테이너가 모두 running 입니다.
- collector metrics 에서 exporter/send 관련 카운터가 증가합니다.
- Grafana health 가 ok 를 반환하고, trace_id 기준으로 로그와 트레이스를 오갈 수 있습니다.
```

## 이 코드에서 먼저 봐야 할 점

- 수집기를 통일하면 수집 표준이 생깁니다.
- trace_id 상관관계가 있어야 메트릭, 로그, 트레이스가 한 스택으로 묶입니다.
- 대표 표본을 쓰면 메트릭에서 트레이스로 바로 이동할 수 있습니다.

## 자주 하는 실수 다섯 가지

1. 신호마다 다른 수집기를 둡니다. 운영 복잡도가 빠르게 커집니다.
2. 상관관계를 설정하지 않습니다. 화면을 계속 오가게 됩니다.
3. 백업과 보존 정책이 없습니다. 비용과 복구 가능성이 모두 흔들립니다.
4. 특정 벤더 기능에 깊게 묶입니다. 나중에 교체하기 어렵습니다.
5. 관측성 시스템 자체의 목표가 없습니다. 도구가 블랙박스가 됩니다.

## 실무에서는 이렇게 생각한다

작은 팀은 보통 OpenTelemetry와 Grafana 계열 스택으로 시작합니다. 수집은 표준으로 묶고, 메트릭·로그·트레이스 저장은 개방형 도구로 두면 학습 곡선과 교체 비용이 비교적 낮습니다. 팀이 커지면 일부를 관리형 서비스로 옮길 수 있지만, 출발점의 원리는 그대로 유지됩니다.

시니어 엔지니어는 "지금 쓸 수 있는가"와 "나중에 바꿀 수 있는가"를 함께 봅니다. 오늘 운영이 가능해야 하고, 내일 더 큰 요구가 왔을 때 일부를 갈아끼울 수 있어야 좋은 첫 스택입니다.

## 체크리스트

- [ ] 수집이 하나의 OpenTelemetry 수집기로 통일되어 있습니다.
- [ ] Grafana에서 세 신호를 모두 볼 수 있습니다.
- [ ] trace_id로 로그와 트레이스를 오갈 수 있습니다.
- [ ] 관측성 스택 자체의 운영 목표를 정의했습니다.

## 연습 문제

1. Compose로 기본 스택을 올려 보세요.
2. 하나의 요청을 세 신호에서 모두 따라가 보세요.
3. 운영자 목표 다섯 개를 각자 환경에 맞게 다시 써 보세요.

## 정리

작은 팀의 첫 관측성 스택은 완벽할 필요가 없지만 운영 가능해야 합니다. 수집은 표준으로 묶고, 메트릭·로그·트레이스를 연결하고, 스택 자체의 건강도 함께 관리하면 출발선으로 충분합니다. 이 시리즈는 여기서 마치지만, 다음 단계는 자연스럽게 사고 대응, 용량 계획, 비용 운영으로 이어집니다.

<!-- toc:begin -->
- [관측성이란 무엇인가?](./01-what-is-observability.md)
- [메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [메트릭 수집과 시각화](./03-metric-collection.md)
- [구조화된 로깅](./04-structured-logging.md)
- [분산 트레이싱 기초](./05-distributed-tracing.md)
- [대시보드 설계](./06-dashboard-design.md)
- [경보와 온콜](./07-alert-and-oncall.md)
- [서비스 수준 지표와 목표 기초](./08-sli-and-slo.md)
- [비용과 카디널리티](./09-cost-and-cardinality.md)
- **운영 가능한 관측성 스택 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Grafana LGTM stack](https://grafana.com/oss/)
- [Tempo docs](https://grafana.com/docs/tempo/latest/)
- [Loki docs](https://grafana.com/docs/loki/latest/)

Tags: Observability, SRE, OpenTelemetry, Grafana, Prometheus
