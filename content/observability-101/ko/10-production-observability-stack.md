---
series: observability-101
episode: 10
title: "Observability 101 (10/10): 운영 가능한 관측성 스택"
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

# Observability 101 (10/10): 운영 가능한 관측성 스택

작은 팀이 관측성 스택을 고를 때 가장 흔한 실수는 완벽한 답을 기다리는 일입니다. 모든 기능이 있고, 비용도 낮고, 운영도 쉬우며, 나중에 교체도 쉬운 조합을 찾다 보면 시작 자체가 늦어집니다. 하지만 관측성은 내일의 완벽한 도구보다 오늘의 운영 가능한 조합이 더 중요합니다.

좋은 첫 스택은 화려한 스택이 아닙니다. 수집이 표준화되어 있고, 메트릭·로그·트레이스를 한 화면에서 연결해 볼 수 있고, 팀이 실제로 운영할 수 있어야 합니다. 그리고 필요할 때 일부를 바꿀 수 있어야 합니다.

이 글은 Observability 101 시리즈의 마지막 글입니다.


![Observability 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/10/10-01-concept-at-a-glance.ko.png)
*Observability 101 10장 흐름 개요*
> 운영 가능한 관측성 스택의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 먼저 던지는 질문

- 작은 팀이 바로 시작할 수 있는 최소 관측성 스택은 어떤 모습일까요?
- OpenTelemetry 수집기를 왜 중심에 두는 편이 좋을까요?
- 메트릭, 로그, 트레이스를 한 화면에서 연결하려면 무엇이 필요할까요?

## 왜 중요한가

관측성 스택은 한 번 정하면 오래 갑니다. 그래서 처음 선택이 과하게 복잡하면 운영팀이 스택 자체를 돌보느라 시간을 쓰게 됩니다. 반대로 너무 단순해서 세 신호가 서로 연결되지 않으면, 장애가 났을 때 화면 다섯 개를 오가느라 시간이 낭비됩니다.

운영 가능한 스택이 중요한 이유는 교체 가능성과 일상성에 있습니다. 작은 팀이라면 오늘 바로 올릴 수 있어야 하고, 내일 문제가 생겼을 때 누구나 흐름을 따라가 볼 수 있어야 합니다.

### 오픈소스 vs 상용 비교

작은 팀이 관측성 스택을 고르는 과정에서 가장 자주 마주치는 질문은 "오픈소스를 직접 운영할까, 아니면 상용 서비스를 사용할까?"입니다.

| 항목 | Prometheus + Grafana | Datadog | New Relic |
|---|---|---|---|
| 초기 비용 | 서버 비용만 (EC2/VM) | 월 $15/호스트 부터 | 월 $25/사용자 부터 |
| 데이터 보존 | 직접 설정 (15일~1년) | 15개월 기본 | 8일 기본 |
| 운영 부담 | 높음 (업데이트, 복제, 백업) | 낮음 (SaaS) | 낮음 (SaaS) |
| 기능 폭 | Prometheus 생태계 | APM, RUM, 통합 모니터링 | Full-stack 관측성 |
| 커스터마이징 | 높음 | 중간 | 중간 |
| 보안/통제 | 내부 관리 | 벤더 신뢰 필요 | 벤더 신뢰 필요 |

오픈소스는 초기 비용이 낮고 데이터를 내부에 둡 수 있지만, 운영 시간이 많이 필요합니다. 상용 서비스는 설치가 빠르고 기능이 풍부하지만, 데이터량이 늘면 비용이 빠르게 커집니다. 팀이 3명 이하라면 상용, 5명 이상이면 오픈소스를 고려하는 편이 현실적입니다.
## 한눈에 보는 구조

완벽한 관측성 스택은 없습니다. 팀이 감당할 수 있는 범위에서 점진적으로 확장하며, 오픈소스와 SaaS의 장단점을 고려해 선택합니다.

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

### 스택 선택 의사결정 트리

관측성 스택 선택은 단순히 도구 리스트를 고르는 것이 아니라 팀의 상황에 맞는 조합을 찾는 과정입니다. 아래 의사결정 트리를 따라가면 방향을 잡는 데 도움이 됩니다.

```text
Q1: 팀 크기가 3명 이하인가?
  YES -> 상용 SaaS 고려 (Datadog, New Relic)
  NO  -> Q2로

Q2: 데이터를 내부에 보관해야 하는가?
  YES -> 오픈소스 필수 (Prometheus + Grafana)
  NO  -> Q3으로

Q3: 매월 모니터링 비용 예산이 $500 이하인가?
  YES -> 오픈소스 우선 (Prometheus + Loki + Tempo + Grafana)
  NO  -> Q4로

Q4: 운영 인력이 1명 이상 할당 가능한가?
  YES -> 오픈소스 직접 운영
  NO  -> 하이브리드 (Grafana Cloud 또는 부분 SaaS)

Q5: APM, RUM, 로그 분석이 모두 필요한가?
  YES -> Full-stack SaaS (Datadog, New Relic, Elastic)
  NO  -> 가벼운 조합 (Prometheus + Loki + Tempo)
```

이 트리는 절대적인 정답이 아니라 출발점입니다. 실제로는 오픈소스로 시작했다가 특정 신호만 상용으로 옮기거나, 상용으로 시작했다가 비용 문제로 오픈소스로 전환하는 팀도 많습니다.

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

### Day-2 운영

관측성 스택을 올렸다고 끝이 아닉니다. 실제로 오래 운영하려면 Day-2 운영 계획이 필요합니다.

**Retention (보존 정책)**

데이터를 얼마나 오래 보관할지 정해야 합니다. Prometheus는 기본 15일, Loki는 7일, Tempo는 1일을 기본값으로 하지만, 실제로는 팀의 요구에 맞춰 조정해야 합니다. 최근 30일은 원본으로, 90일까지는 5분 해상도로, 1년은 1시간 해상도로 내리면 비용과 유용성을 균형 있게 가져갈 수 있습니다.

```yaml
# Prometheus retention
prometheus:
  retention.time: 15d
  retention.size: 50GB

# Thanos downsampling
thanos:
  retention.resolution-raw: 30d
  retention.resolution-5m: 90d
  retention.resolution-1h: 1y
```

**Compaction (압축)**

오래된 데이터를 압축해 저장 공간을 줄입니다. Prometheus는 자체적으로 2시간 블록을 합치고, Thanos나 Cortex는 이를 더 긴 기간으로 압축합니다. Loki도 compactor를 돌리면 블록 파일을 합쳐 저장 효율을 높일 수 있습니다.

```yaml
compactor:
  working_directory: /loki/compactor
  shared_store: s3
  compaction_interval: 10m
```

**Federation (연합)**

여러 리전이나 클러스터가 있는 경우 중앙 Prometheus가 하위 Prometheus로부터 집계 데이터를 가져옵니다. 이를 통해 전체 시스템의 건강 상태를 한곳에서 볼 수 있습니다.

```yaml
scrape_configs:
  - job_name: federate
    honor_labels: true
    metrics_path: /federate
    params:
      match[]:
        - '{job="api"}'
        - '{job="worker"}'
    static_configs:
      - targets: ['prometheus-region1:9090', 'prometheus-region2:9090']
```

이 세 가지는 첫 스택을 올린 뒤 바로 계획해야 하는 항목입니다. 특히 보존 정책을 명확하게 하지 않으면 디스크가 가득 차거나 비용이 폭발합니다.

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

## 운영 스택 아키텍처 텍스트 다이어그램

아래 다이어그램은 작은 팀이 자주 채택하는 LGTM 기반 흐름을 텍스트로 표현한 것입니다.

```text
[App Services]
  |- metrics/logs/traces via OTLP
  v
[OpenTelemetry Collector]
  |- metrics -> [Prometheus] -> [Grafana]
  |- logs    -> [Loki]       -> [Grafana]
  |- traces  -> [Tempo]      -> [Grafana]
  `- alerts  -> [Alertmanager] -> [PagerDuty/Slack]

Correlation key: trace_id
```

Collector를 중심에 두면 애플리케이션은 OTLP만 알면 되고, 저장소 교체는 Collector 파이프라인에서 처리할 수 있습니다. 이 구조는 "앱 코드 최소 변경"이라는 운영 원칙에 잘 맞습니다.

## 아키텍처 의사결정 표

| 결정 항목 | 선택지 A | 선택지 B | 기준 | 권장 |
| --- | --- | --- | --- | --- |
| 수집 방식 | 앱 -> 저장소 직접 전송 | 앱 -> Collector | 변경 유연성 | Collector 중심 |
| 메트릭 저장 | 단일 Prometheus | Prometheus + 장기 저장 | 보존 요구 | 초기 단일, 이후 확장 |
| 로그 저장 | Loki | Elasticsearch 계열 | 운영 복잡도/검색 요구 | 팀 역량 기준 선택 |
| 트레이스 저장 | Tempo | Jaeger | 운영 단순성 | Grafana 연동 우선 |
| 시각화 | 도구별 개별 UI | Grafana 통합 | 대응 속도 | 통합 UI 권장 |

모든 팀에 정답인 조합은 없습니다. 다만 작은 팀 출발점에서는 "통합 화면"과 "구성 단순성"의 가치를 높게 두는 편이 안정적입니다. 기능이 부족하면 확장하면 되지만, 복잡도는 초기 설계에서 과도하게 올리면 되돌리기 어렵습니다.

## 운영 점검 체크 자동화 예시

```python
import requests


def health_check() -> dict[str, bool]:
    checks = {
        "collector_metrics": "http://localhost:9464/metrics",
        "prometheus_ready": "http://localhost:9090/-/ready",
        "loki_ready": "http://localhost:3100/ready",
        "tempo_ready": "http://localhost:3200/ready",
        "grafana_health": "http://localhost:3000/api/health",
    }
    result: dict[str, bool] = {}
    for name, url in checks.items():
        try:
            response = requests.get(url, timeout=3)
            result[name] = response.status_code == 200
        except Exception:
            result[name] = False
    return result


if __name__ == "__main__":
    status = health_check()
    for k, v in status.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")
```

관측성 플랫폼도 제품처럼 헬스체크가 필요합니다. 이 점검 스크립트를 크론이나 CI 파이프라인에 붙이면 "장애가 난 순간 관측 도구도 죽어 있는" 최악의 상황을 줄일 수 있습니다.

### Docker Compose로 구성하는 전체 스택

아래는 소규모 팀이 로컬 환경이나 개발 환경에서 전체 스택을 띄울 수 있는 Docker Compose 설정입니다.

```yaml
# docker-compose.observability.yml
version: "3.9"
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.96.0
    command: ["--config=/etc/otel/config.yaml"]
    volumes:
      - ./otel-config.yaml:/etc/otel/config.yaml:ro
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus exporter
    depends_on:
      - tempo
      - loki

  prometheus:
    image: prom/prometheus:v2.51.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=15d"
      - "--storage.tsdb.retention.size=10GB"
    ports:
      - "9090:9090"

  loki:
    image: grafana/loki:2.9.4
    volumes:
      - loki_data:/loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

  tempo:
    image: grafana/tempo:2.4.0
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml:ro
      - tempo_data:/tmp/tempo
    command: ["-config.file=/etc/tempo.yaml"]
    ports:
      - "3200:3200"   # Tempo API
      - "4320:4317"   # OTLP gRPC (Tempo direct)

  grafana:
    image: grafana/grafana:10.3.3
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    environment:
      GF_AUTH_ANONYMOUS_ENABLED: "true"
      GF_AUTH_ANONYMOUS_ORG_ROLE: Admin
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
      - loki
      - tempo

volumes:
  prometheus_data:
  loki_data:
  tempo_data:
  grafana_data:
```

`docker compose -f docker-compose.observability.yml up -d`로 실행하면 메트릭(Prometheus), 로그(Loki), 트레이스(Tempo), 대시보드(Grafana), 수집기(OTel Collector)가 모두 떠오릅니다.

### 프로덕션 하드닝 체크리스트

로컬 환경에서 프로덕션으로 옮길 때 확인해야 할 항목입니다.

| 영역 | 항목 | 로컬 | 프로덕션 |
|------|------|------|---------|
| 스토리지 | Prometheus 보존 | 15일 | retention.time + retention.size 설정 |
| 스토리지 | Loki 청크 압축 | 기본값 | S3/GCS 백엔드 + compactor 활성화 |
| 스토리지 | Tempo 블록 저장소 | 로컬 디스크 | S3/GCS 백엔드 + 압축 |
| 가용성 | Prometheus HA | 단일 인스턴스 | Thanos/Mimir sidecar + 이중화 |
| 가용성 | Collector HA | 단일 인스턴스 | 로드밸런서 뒤에 2+ 인스턴스 |
| 가용성 | Grafana HA | 단일 인스턴스 | PostgreSQL 세션 + 로드밸런서 |
| 보안 | 네트워크 격리 | 모두 같은 네트워크 | 내부 전용 네트워크 + mTLS |
| 보안 | 인증 | anonymous | Grafana OIDC + Prometheus basic auth |
| 보안 | 시크릿 관리 | 환경변수 | Vault / Sealed Secrets |
| 운영 | 백업 | 없음 | Prometheus snapshot + Grafana provisioning git |
| 운영 | 업그레이드 전략 | latest | 버전 고정 + 카나리 배포 |
| 모니터링 | 자기 관측 | 없음 | 각 컴포넌트 /metrics + 헬스체크 스크립트 |

### 용량 계획 기준

프로덕션 환경의 리소스 산정 기준입니다.

```text
── Prometheus ──
메모리: 시계열 수 × 120 bytes (대략적 기준)
  50,000 시계열 → ~6 GB RAM
  200,000 시계열 → ~24 GB RAM
디스크: scrape_interval × 시계열 수 × 2 bytes × 보존일수
  50,000 시계열, 15초, 15일 → ~43 GB

── Loki ──
압축 후 로그 크기: 원본의 ~10-15%
  일 10 GB 로그 × 30일 × 12% → ~36 GB 스토리지

── Tempo ──
트레이스 크기: span 당 ~200-500 bytes (압축 후)
  초당 1,000 span × 86,400초 × 7일 × 300 bytes → ~170 GB

── OTel Collector ──
CPU: 초당 span/로그 10,000건 기준 ~0.5 core
메모리: batch + queue 설정에 따라 512 MB - 2 GB
```

용량 계획에서 가장 흔한 실수는 시계열 증가를 과소평가하는 것입니다. 서비스가 성장하면 인스턴스, 엔드포인트, 레이블 조합이 모두 늘어납니다. 분기별로 실제 시계열 수를 측정하고 예측치를 업데이트해야 합니다.

초기 산정이 어려우면 보수적으로 2배 여유를 두고 시작하되, Prometheus의 `prometheus_tsdb_head_series` 메트릭과 Loki의 `loki_ingester_chunk_stored_bytes_total`을 주기적으로 관찰하면서 실제 사용량에 맞게 조정합니다. 관측성 플랫폼 자체의 리소스 사용량도 관측 대상이어야 합니다.

## 처음 질문으로 돌아가기

- **작은 팀이 바로 시작할 수 있는 최소 관측성 스택은 어떤 모습일까요?**
  - Docker Compose 하나로 Prometheus + Loki + Tempo + Grafana + OTel Collector를 띄울 수 있습니다. 본문의 예시처럼 5개 컴포넌트면 메트릭·로그·트레이스 세 신호를 모두 수집하고 상관 분석할 수 있는 환경이 만들어집니다.
- **OpenTelemetry 수집기를 왜 중심에 두는 편이 좋을까요?**
  - 애플리케이션은 OTLP라는 하나의 프로토콜로만 내보내면 됩니다. 수집기가 백엔드(Prometheus, Loki, Tempo, Jaeger 등)로의 라우팅을 담당하므로, 백엔드를 교체할 때 애플리케이션 코드를 변경할 필요가 없습니다. 샘플링, 필터링, 변환도 수집기 설정에서 처리할 수 있어 운영 유연성이 높아집니다.
- **메트릭, 로그, 트레이스를 한 화면에서 연결하려면 무엇이 필요할까요?**
  - Grafana의 Explore 화면에서 trace ID로 검색하면 해당 트레이스와 연관된 로그, 그 시점의 메트릭을 한 화면에서 볼 수 있습니다. 이를 위해 로그에 trace_id 필드를 삽입하고, Grafana 데이터 소스에서 Loki→Tempo, Tempo→Prometheus 간 연결(derived fields, exemplars)을 설정해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- [Observability 101 (4/10): 구조화된 로깅](./04-structured-logging.md)
- [Observability 101 (5/10): 분산 트레이싱 기초](./05-distributed-tracing.md)
- [Observability 101 (6/10): 대시보드 설계](./06-dashboard-design.md)
- [Observability 101 (7/10): 경보와 온콜](./07-alert-and-oncall.md)
- [Observability 101 (8/10): 서비스 수준 지표와 목표 기초](./08-sli-and-slo.md)
- [Observability 101 (9/10): 비용과 카디널리티](./09-cost-and-cardinality.md)
- **운영 가능한 관측성 스택 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Grafana LGTM stack](https://grafana.com/oss/)
- [Tempo docs](https://grafana.com/docs/tempo/latest/)
- [Loki docs](https://grafana.com/docs/loki/latest/)

- [book-examples — observability-101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)
Tags: Observability, SRE, OpenTelemetry, Grafana, Prometheus
