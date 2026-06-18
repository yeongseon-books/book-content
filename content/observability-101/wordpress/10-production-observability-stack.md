---
title: "바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택"
series: observability-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - OpenTelemetry
  - Grafana
  - Prometheus
---

# 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택

이 글은 "바이브코딩을 위한 Observability 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 관측성 스택 설정 파일을 빠르게 만들어 줍니다. 그런데 작은 팀이 관측성 스택을 고를 때 가장 흔한 실수는 완벽한 답을 기다리는 일입니다. 모든 기능이 있고, 비용도 낮고, 운영도 쉬우며, 나중에 교체도 쉬운 조합을 찾다 보면 시작 자체가 늦어집니다.

좋은 첫 스택은 화려한 스택이 아닙니다. 수집이 표준화되어 있고, 메트릭·로그·트레이스를 한 화면에서 연결해 볼 수 있고, 팀이 실제로 운영할 수 있어야 합니다.

관측성 스택의 핵심 문제는 세 신호가 연결되지 않을 때 발생합니다. 메트릭은 한 화면, 로그는 다른 화면, 트레이스는 또 다른 화면을 보고, 같은 요청을 따라가려면 계속 복사하고 붙여 넣어야 하면 장애 대응 시간이 길어집니다. trace_id가 세 신호를 연결하는 핵심입니다.

OpenTelemetry Collector, Prometheus, Loki, Tempo, Grafana 조합으로 첫 스택을 구성하는 방법을 정리합니다.

> **핵심 인사이트:** 관측성 스택에서 가장 중요한 것은 trace_id로 메트릭 → 트레이스 → 로그를 한 화면에서 연결하는 일입니다. 이 연결이 없으면 도구는 세 개 있지만 장애 조사 흐름은 이전과 같습니다.

## 이 글에서 다룰 문제

- 작은 팀이 바로 시작할 수 있는 최소 관측성 스택은 어떤 모습일까요?
- OpenTelemetry Collector를 왜 중심에 두는 편이 좋을까요?
- 메트릭, 로그, 트레이스를 한 화면에서 연결하려면 무엇이 필요할까요?
- 오픈소스와 상용 서비스는 어떻게 선택할까요?
- AI가 만든 관측성 설정에서 확인해야 할 것은 무엇인가요?

## 운영 가능한 관측성 스택 핵심 패턴

```yaml
# OpenTelemetry Collector: 단일 수집 게이트웨이
receivers:
  otlp: { protocols: { grpc: {}, http: {} } }
exporters:
  prometheus:  { endpoint: ":9464" }
  loki:        { endpoint: "http://loki:3100/loki/api/v1/push" }
  otlp/tempo:  { endpoint: "tempo:4317", tls: { insecure: true } }
service:
  pipelines:
    metrics: { receivers: [otlp], exporters: [prometheus] }
    logs:    { receivers: [otlp], exporters: [loki] }
    traces:  { receivers: [otlp], exporters: [otlp/tempo] }
```

```yaml
# Docker Compose로 전체 스택 한 번에 올리기
services:
  otel-collector: { image: otel/opentelemetry-collector-contrib }
  prometheus:     { image: prom/prometheus }
  loki:           { image: grafana/loki }
  tempo:          { image: grafana/tempo }
  grafana:        { image: grafana/grafana, ports: ["3000:3000"] }

# Grafana에서 세 신호 연결 (trace_id 기반)
# Tempo → Loki: derived field "trace_id" → log search
# Loki  → Tempo: log "trace_id" → trace view
# Prometheus → Tempo: 메트릭 이상 지점 → 대표 트레이스
```

## 변경 전후 비교

**Before: 연결 없는 도구 집합**
```text
- 메트릭: Grafana 화면 1
- 로그: Kibana 화면 2
- 트레이스: Jaeger 화면 3
- 같은 요청 추적: 화면 3개 오가며 복사-붙여넣기
- 장애 대응 시간: 길어짐
```

**After: trace_id로 연결된 단일 화면**
```text
- Grafana 한 화면에서 메트릭 이상 감지
- 대표 trace_id로 Tempo 트레이스로 점프
- 같은 trace_id로 Loki 로그까지 드릴다운
- 장애 대응 흐름이 훨씬 짧아짐
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 세 신호 연결 없음 | 화면 3개를 오가며 trace_id를 손으로 복사 | trace_id 기반 신호 연결 설정 |
| 벤더 SDK 직접 사용 | 저장소 교체 시 코드 전체 변경 필요 | OpenTelemetry 표준으로 추상화 |
| 완벽한 스택 기다림 | 시작이 늦어짐 | 최소 스택으로 시작 후 점진 확장 |
| 모든 데이터를 같은 기간 보관 | 비용 폭발 | 보존 계층 분리 |
| 작은 팀이 오픈소스 직접 운영 | 운영 부담 > 편익 | 3명 이하면 SaaS 고려 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"OpenTelemetry + Prometheus + Loki + Tempo + Grafana 스택을
Docker Compose로 구성해줘.
Python FastAPI 앱에서 메트릭/로그/트레이스를 OTel Collector로 전송,
Grafana에서 trace_id로 세 신호 연결,
SLO 대시보드 포함"

# AI 결과물 검증 체크포인트:
# - OpenTelemetry Collector가 중간에 있는가?
# - 세 파이프라인(metrics/logs/traces)이 분리되어 있는가?
# - Grafana에서 trace_id 기반 신호 연결이 설정되어 있는가?
# - 애플리케이션 코드가 특정 벤더 SDK에 의존하지 않는가?
# - 보존 기간이 적절히 설정되어 있는가?
```

## 운영 체크리스트

- [ ] OpenTelemetry Collector가 수집 중심에 있다
- [ ] 메트릭, 로그, 트레이스를 trace_id로 Grafana에서 연결할 수 있다
- [ ] 팀이 실제로 운영 가능한 수준의 스택인가 평가한다
- [ ] 보존 계층이 비용을 고려해 설정되어 있다
- [ ] 스택 교체 시 애플리케이션 코드 변경 최소화를 고려한다

## 처음 질문으로 돌아가기

- **OpenTelemetry Collector를 중심에 두는 이유는?** 수집기가 단일 창구가 되면 저장 백엔드를 바꿔도 애플리케이션 코드를 변경하지 않아도 됩니다. 언어와 프레임워크가 달라도 표준 프로토콜로 수집이 통일됩니다.
- **trace_id 연결이 중요한 이유는?** 메트릭에서 이상 지점을 발견해도 원인을 찾으려면 어떤 요청이 문제인지 알아야 합니다. trace_id가 있으면 메트릭 → 트레이스 → 로그를 한 화면에서 따라갈 수 있습니다.
- **오픈소스 vs 상용 선택 기준은?** 팀이 3명 이하면 운영 부담 때문에 SaaS(Datadog, Grafana Cloud)가 현실적입니다. 5명 이상이면 오픈소스 직접 운영을 고려할 수 있습니다. 데이터 보안/규정 요건도 함께 고려합니다.

## 정리

바이브코딩에서 AI가 만들어 준 관측성 설정에서 세 신호 연결(trace_id), 벤더 독립성(OpenTelemetry), 팀 운영 가능성을 반드시 확인하세요. 완벽한 스택을 기다리지 말고 운영 가능한 최소 조합으로 시작하세요. Observability 101 시리즈를 통해 메트릭, 로그, 트레이스부터 SLO, 비용 관리, 스택 구성까지 관측성 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [OpenTelemetry — Getting Started](https://opentelemetry.io/docs/getting-started/)
- [Grafana — LGTM Stack (Loki + Grafana + Tempo + Mimir)](https://grafana.com/oss/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭
- 바이브코딩을 위한 Observability 기초 (3/10): 로그
- 바이브코딩을 위한 Observability 기초 (4/10): 트레이스
- 바이브코딩을 위한 Observability 기초 (5/10): 세 신호 연결
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): SLI와 SLO
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- **바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Observability, OpenTelemetry, Grafana, Prometheus
