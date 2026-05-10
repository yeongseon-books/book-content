---
series: observability-101
episode: 9
title: Cost와 Cardinality
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
  - Cost
  - Cardinality
  - Metrics
  - Sampling
seo_description: cardinality 폭발과 retention 정책, sampling으로 observability 비용을 통제하는 법
last_reviewed: '2026-05-04'
---

# Cost와 Cardinality

> Observability 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: observability 비용은 *왜* 갑자기 *10배* 가 됩니까?

> *Cardinality 폭발, retention, sampling 부재 — 이 셋이 *비용 폭탄* 의 99% 입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *Cardinality* 가 비용을 만드는 법
- *Retention* 정책의 단계화
- *Sampling* 의 두 모델
- 신호별 *비용 곡선*
- 흔한 함정 5가지

## 왜 중요한가

신생 회사의 *AWS 비용 1위* 가 종종 *observability* 입니다. 모니터링이 *제품보다 비싸지면* 정치 문제가 됩니다.

> *측정의 비용을 모르면 *측정이 적이 된다*.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Labels["label 조합"] --> Series["time series 수"]
    Series --> Storage["저장 비용"]
    Logs["log 부피"] --> Index["index 비용"]
    Traces["trace 수"] --> Sample["sampling"]
```

## 핵심 용어 정리

- **Cardinality**: label 조합의 *고유 개수*.
- **Retention tier**: hot / warm / cold *분리*.
- **Head sampling**: 시작 시점에 결정.
- **Tail sampling**: 끝난 후 결정 (느린 trace 우선).
- **Aggregation**: 보존 전 *집계* 로 부피 축소.

## Before/After

**Before**: `user_id` 가 label, *5천만 series*, 비용 *폭발*.

**After**: `user_id` 는 *log* 로, label 은 *유한 차원*, 비용 *예측 가능*.

## 실습: 비용 통제 5단계

### 1단계 — Cardinality 측정

```promql
count({__name__=~".+"})              # 전체 series 수
topk(20, count by (__name__) (...))   # 상위 metric
```

### 2단계 — 위험 label 제거

```python
# 나쁨: 사용자별 series
http_requests_total{user_id="42", path="/buy"}
# 좋음: 차원 축소
http_requests_total{path="/buy"}      # user_id 는 log 에
```

### 3단계 — Retention tier

```yaml
prometheus:  retention: 15d
thanos:      retention.resolution-raw: 30d
             retention.resolution-5m: 90d
             retention.resolution-1h: 1y
```

### 4단계 — Tail sampling

```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### 5단계 — 신호별 예산

```text
metric:  ≤ X 백만 series
log:     ≤ Y GB/일
trace:   샘플링 후 ≤ Z 트레이스/분
```

## 이 코드에서 주목할 점

- *Cardinality* 는 *label 곱셈* 으로 폭발.
- *Resolution downsampling* 으로 *오래된 데이터* 부피 축소.
- *Tail sampling* 은 *가치 있는 trace* 만 보관.

## 자주 하는 실수 5가지

1. **`user_id`, `request_id` 를 *label* 로.** Cardinality 폭발.
2. **모든 신호 *영원히 보관*.** 비용 *복리*.
3. **Sampling 을 *나쁘게 본다*.** 부도 위험.
4. **Log 에 *바이너리* 를 박는다.** 부피 폭발.
5. **비용을 *팀 단위* 로 안 본다.** 책임이 *분산*.

## 실무에서는 이렇게 쓰입니다

대부분의 회사는 *팀별 cardinality budget*, *retention tier*, *tail sampling* 을 조합해 *예측 가능한* observability 비용을 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *Cardinality 는 *세금* 이다.*
- *오래된 데이터는 *해상도를 낮춰* 보관.*
- *Sampling 은 *부끄러운 일이 아니다*.*
- *비용에 *오너* 가 있어야 한다.*
- *측정 비용 자체를 *측정* 한다.*

## 체크리스트

- [ ] *Cardinality* 상위 metric 을 안다.
- [ ] *Retention tier* 가 단계화되어 있다.
- [ ] Trace 에 *sampling* 이 있다.
- [ ] 팀별 *비용 예산* 이 있다.

## 연습 문제

1. Cardinality 가 위험한 label 3개를 찾아보세요.
2. Retention 3-tier 를 설계해 보세요.
3. *Error / slow / random* tail sampling 정책을 작성해 보세요.

## 정리 및 다음 단계

비용을 모르면 *observability 가 적* 이 됩니다. 다음 글은 *운영 가능한 스택* 입니다.

<!-- toc:begin -->
- [Observability란 무엇인가?](./01-what-is-observability.md)
- [Metric, Log, Trace](./02-metric-log-trace.md)
- [Metric 수집과 시각화](./03-metric-collection.md)
- [구조화된 로깅](./04-structured-logging.md)
- [분산 트레이싱 기초](./05-distributed-tracing.md)
- [Dashboard 설계](./06-dashboard-design.md)
- [Alert와 On-Call](./07-alert-and-oncall.md)
- [SLI와 SLO 기초](./08-sli-and-slo.md)
- **Cost와 Cardinality (현재 글)**
- 운영 가능한 Observability 스택 (예정)
<!-- toc:end -->

## 참고 자료

- [Cardinality is the enemy](https://www.robustperception.io/cardinality-is-key/)
- [Thanos downsampling](https://thanos.io/tip/components/compact.md/)
- [OpenTelemetry tail sampling](https://opentelemetry.io/docs/collector/configuration/#processors)
- [Honeycomb on cost](https://www.honeycomb.io/blog/observability-cost)
