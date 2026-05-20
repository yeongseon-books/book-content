---
series: observability-101
episode: 9
title: "Observability 101 (9/10): 비용과 카디널리티"
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
  - Cost
  - Cardinality
  - Metrics
  - Sampling
seo_description: 카디널리티 폭발, 보존 기간, 샘플링이 관측성 비용을 어떻게 키우고 줄이는지 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (9/10): 비용과 카디널리티

관측성은 도입 초기에 비싸 보이지 않을 때가 많습니다. 메트릭 몇 개, 로그 몇 줄, 트레이스 조금만 남기면 될 것처럼 느껴지기 때문입니다. 그런데 어느 날부터 청구서가 갑자기 열 배쯤 커졌다는 이야기가 나옵니다. 대개는 수집량이 조금 늘어서가 아니라 구조가 잘못돼서 그렇습니다.

비용을 폭발시키는 대표 원인은 세 가지입니다. 고유값을 라벨에 넣어 카디널리티를 키우는 일, 모든 신호를 오래 보관하는 일, 샘플링 없이 전부 저장하는 일입니다. 이 세 가지를 이해하면 관측성 비용은 훨씬 예측 가능해집니다.

이 글은 Observability 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- 카디널리티는 왜 비용과 직접 연결될까요?
- 보존 기간을 나눠 가져가야 하는 이유는 무엇일까요?
- 머리 샘플링과 꼬리 샘플링은 어떻게 다를까요?

## 큰 그림

![Observability 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/09/09-01-concept-at-a-glance.ko.png)

*Observability 101 9장 흐름 개요*

비용과 카디널리티를 다루는 이번 장에서는 주요 개념과 실무 패턴을 봅니다. 시스템이 복잡해질수록 이 개념들이 어디에서 시작되고 어떤 결과를 만드는지 이해하는 것이 중요합니다.

> 비용과 카디널리티의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 왜 중요한가

초기 스타트업이나 작은 팀에서는 관측성 비용이 가장 빠르게 커지는 인프라 항목 중 하나가 되기도 합니다. 시스템을 이해하려고 붙인 도구가 정작 제품 비용보다 더 큰 압박이 되면, 관측성 자체가 정치적 문제가 됩니다.

이 글의 핵심은 비용을 줄이자는 데만 있지 않습니다. 더 중요한 것은 비용을 예측 가능하게 만드는 일입니다. 어떤 라벨이 위험한지, 어떤 데이터는 오래 보관할 가치가 있는지, 어떤 트레이스만 남겨도 충분한지 기준이 있어야 운영이 흔들리지 않습니다.

## 한눈에 보는 구조

관측성 비용은 수집, 저장, 질의 세 단계에서 발생합니다. 카디널리티가 높으면 저장 크기와 질의 시간이 급증하므로, 처음부터 통제해야 합니다.

## 핵심 용어

- 카디널리티: 고유한 라벨 조합의 개수입니다.
- 보존 계층: 뜨거운 데이터, 중간 데이터, 차가운 데이터를 나눠 저장하는 방식입니다.
- 머리 샘플링: 요청 시작 시점에 저장 여부를 결정하는 방식입니다.
- 꼬리 샘플링: 트레이스가 끝난 뒤 느리거나 실패한 것만 남기는 방식입니다.
- 집계: 오래된 데이터를 낮은 해상도로 줄여 저장량을 줄이는 전략입니다.

## 바꾸기 전과 후

바꾸기 전에는 `user_id` 같은 값을 라벨에 넣고, 로그와 트레이스를 전부 오래 보관합니다. 처음에는 편해 보여도 금방 시계열 수와 저장량이 감당하기 어려운 수준으로 커집니다.

바꾼 뒤에는 사용자 식별자는 로그에만 남기고, 메트릭 라벨은 유한한 차원으로 제한합니다. 오래된 데이터는 낮은 해상도로 내리고, 트레이스는 가치 있는 일부만 남깁니다. 비용이 줄어드는 것보다 더 중요한 변화는 예측 가능성이 생긴다는 점입니다.

## 실습: 비용 통제를 다섯 단계로 만들기

### 1단계 — 카디널리티 측정하기

```promql
count({__name__=~".+"})              # total series
topk(20, count by (__name__) (...))  # top metrics
```

비용 통제의 첫걸음은 현재 상태를 숫자로 보는 일입니다. 어떤 메트릭이 시계열을 많이 만들고 있는지 알아야 위험한 라벨을 찾을 수 있습니다.

### 2단계 — 위험한 라벨 빼기

```text
# Bad: per-user series
http_requests_total{user_id="42", path="/buy"}
# Good: dimension reduction
http_requests_total{path="/buy"}      # user_id goes to logs
```

메트릭 라벨에는 유한한 차원만 남겨야 합니다. 사용자별, 요청별, 세션별 식별자는 로그나 트레이스로 보내는 편이 맞습니다.

### 3단계 — 보존 계층 나누기

```yaml
prometheus:  retention: 15d
thanos:      retention.resolution-raw: 30d
             retention.resolution-5m: 90d
             retention.resolution-1h: 1y
```

오래된 데이터를 모두 같은 해상도로 유지할 필요는 없습니다. 최근 데이터는 정밀하게, 과거 데이터는 거칠게 보관하면 저장량을 크게 줄일 수 있습니다.

### 4단계 — 꼬리 샘플링 적용하기

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

모든 트레이스를 다 저장하지 않아도 중요한 트레이스를 놓치지 않을 수 있습니다. 실패, 느린 요청, 일부 무작위 표본만 남기면 가치 대비 비용이 훨씬 좋아집니다.

### 5단계 — 신호별 예산 세우기

```text
metric:  <= X million series
log:     <= Y GB per day
trace:   <= Z traces per minute after sampling
```

비용은 팀의 책임이어야 합니다. 신호별 상한선을 정해 두면 데이터 설계가 훨씬 신중해지고, 청구서가 나오기 전에 위험을 조정할 수 있습니다.

## 비용 점검은 이렇게 시작합니다

카디널리티 문제는 청구서가 나온 뒤에 보는 것보다, 시계열 상위 항목을 주기적으로 확인하는 편이 훨씬 낫습니다.

```promql
count({__name__=~".+"})
topk(10, count by (__name__) ({__name__=~".+"}))
```

```text
Expected output:
- 상위 메트릭 몇 개가 전체 시계열 대부분을 만들고 있는지 보입니다.
- path, status 같은 유한 라벨은 유지하고 user_id, request_id 같은 라벨은 제거해야 할지 판단할 수 있습니다.
- 팀별 예산선을 넘는 경우 즉시 라벨 축소나 보존 정책 조정을 논의할 수 있습니다.
```

## 이 코드에서 먼저 봐야 할 점

- 카디널리티는 라벨 곱셈으로 빠르게 커집니다.
- 낮은 해상도 보존은 오래된 데이터 비용을 크게 줄입니다.
- 꼬리 샘플링은 가치 있는 트레이스를 남기는 데 특히 효과적입니다.

## 자주 하는 실수 다섯 가지

1. `user_id`, `request_id`를 라벨에 넣습니다. 카디널리티가 폭발합니다.
2. 모든 신호를 영구 보관합니다. 비용이 복리처럼 쌓입니다.
3. 샘플링을 나쁜 것으로만 봅니다. 현실적인 운영이 어려워집니다.
4. 로그에 바이너리나 과도한 본문을 넣습니다. 저장량이 급격히 늘어납니다.
5. 팀별 비용 시야가 없습니다. 누구도 책임지지 않게 됩니다.

## 실무에서는 이렇게 생각한다

관측성 비용을 잘 관리하는 팀은 도구보다 데이터 모델을 먼저 통제합니다. 메트릭 라벨은 유한한 집합만 허용하고, 로그는 보존 기간과 민감도에 따라 계층화하고, 트레이스는 샘플링 정책을 명시적으로 운영합니다.

또한 비용을 운영 지표로 봅니다. 시스템 건강을 보는 것처럼 관측성 시스템의 비용 건강도 함께 본다는 뜻입니다. 측정 비용을 측정하지 않으면, 관측성은 오래 갈수록 부담이 됩니다.

## 체크리스트

- [ ] 카디널리티가 높은 메트릭을 파악했습니다.
- [ ] 보존 계층이 나뉘어 있습니다.
- [ ] 트레이스 샘플링 정책이 있습니다.
- [ ] 팀 단위 비용 예산이 있습니다.

## 연습 문제

1. 카디널리티 폭발 위험이 있는 라벨 세 개를 찾아 보세요.
2. 세 단계 보존 정책을 설계해 보세요.
3. 오류, 지연, 무작위 표본을 위한 꼬리 샘플링 정책을 써 보세요.

## 정리

관측성 비용은 갑자기 커지는 것처럼 보여도, 실제로는 라벨 설계와 보존 정책, 샘플링 전략이 만든 결과인 경우가 많습니다. 비용을 예측 가능하게 만들면 관측성은 부담이 아니라 장기 자산이 됩니다. 마지막 글에서는 지금까지의 내용을 묶어 작은 팀이 실제로 운영 가능한 관측성 스택을 어떻게 꾸릴지 정리하겠습니다.

## 처음 질문으로 돌아가기

- **카디널리티는 왜 비용과 직접 연결될까요?**
  - 본문의 기준은 비용과 카디널리티를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **보존 기간을 나눠 가져가야 하는 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **머리 샘플링과 꼬리 샘플링은 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
- **비용과 카디널리티 (현재 글)**
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Cardinality is the enemy](https://www.robustperception.io/cardinality-is-key/)
- [Thanos downsampling](https://thanos.io/tip/components/compact.md/)
- [OpenTelemetry tail sampling](https://opentelemetry.io/docs/collector/configuration/#processors)
- [Honeycomb on cost](https://www.honeycomb.io/blog/observability-cost)

Tags: Observability, Cost, Cardinality, Metrics, Sampling
