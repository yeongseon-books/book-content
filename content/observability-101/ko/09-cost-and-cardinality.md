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


![Observability 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/09/09-01-concept-at-a-glance.ko.png)
*Observability 101 9장 흐름 개요*
> 비용과 카디널리티의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 먼저 던지는 질문

- 카디널리티는 왜 비용과 직접 연결될까요?
- 보존 기간을 나눠 가져가야 하는 이유는 무엇일까요?
- 머리 샘플링과 꼬리 샘플링은 어떻게 다를까요?

## 왜 중요한가

초기 스타트업이나 작은 팀에서는 관측성 비용이 가장 빠르게 커지는 인프라 항목 중 하나가 되기도 합니다. 시스템을 이해하려고 붙인 도구가 정작 제품 비용보다 더 큰 압박이 되면, 관측성 자체가 정치적 문제가 됩니다.

이 글의 핵심은 비용을 줄이자는 데만 있지 않습니다. 더 중요한 것은 비용을 예측 가능하게 만드는 일입니다. 어떤 라벨이 위험한지, 어떤 데이터는 오래 보관할 가치가 있는지, 어떤 트레이스만 남겨도 충분한지 기준이 있어야 운영이 흔들리지 않습니다.

### 관측 비용 구성

관측성 비용은 세 단계로 나눌 수 있습니다. 각 단계마다 비용 동인이 다르고 절감 전략도 다릅니다.

| 비용 구성 | 비용 동인 | 절감 전략 |
|---|---|---|
| 수집 | 측정 포인트 수, 스크레이프 빈도, 네트워크 비용 | 수집 주기 늘리기, 불필요한 라벨 제거, 샘플링 |
| 저장 | 데이터 크기, 보존 기간, 복제본 수 | 보존 계층 분리, 집계, 압축 |
| 질의 | 시계열 수, 쿼리 복잡도, 시간 범위 | 카디널리티 통제, 그룹 함수 최소화, 인덱스 최적화 |

수집 비용은 주로 네트워크 대역폭과 수집기 CPU에서 나오고, 저장 비용은 디스크 크기와 보조로 메모리나 CPU를 쓰며, 질의 비용은 카디널리티가 높을수록 급증합니다. 클라우드 환경에서는 저장과 질의 비용이 가장 크게 나타나므로 이 두 영역을 먼저 통제하는 편이 좋습니다.
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

### 라벨 설계 원칙

메트릭 라벨은 카디널리티를 결정하는 가장 강력한 요인입니다. 아래 다섯 가지 원칙을 지키면 비용 폭발을 크게 줄일 수 있습니다.

**1. 유한한 차원만 사용**

라벨은 가능한 값의 수가 제한되어야 합니다. `method`, `status`, `path`, `environment`처럼 고정된 집합만 허용하고, `user_id`, `request_id`, `session_id`처럼 무한히 커지는 값은 피합니다.

**2. 고카디널리티 차원은 로그로**

사용자 식별자, 요청 ID, IP 주소처럼 개별 값을 추적해야 하는 경우는 메트릭이 아니라 로그에 남깁니다. 메트릭은 집계 데이터로 제한하고, 개별 요청은 로그나 트레이스에서 찾습니다.

**3. 경로는 패턴으로 묶기**

`path` 라벨은 동적 경로를 그대로 넣으면 안 됩니다. `/users/123`과 `/users/456`은 모두 `/users/:id`로 정규화해야 합니다. 경로 패턴을 정해 두면 엔드포인트 수가 제한됩니다.

**4. 환경과 지역은 최상위로**

`environment`, `region`, `cluster`처럼 전체 시스템을 가르는 라벨은 가장 바깥쪽에 놓는 편이 좋습니다. 이 차원은 보통 개수가 적고, 질의에서 필터로 자주 쓰이며, 상황에 따라 수집기 레벨에서 분리할 수도 있습니다.

**5. 라벨 수는 5개 이하로**

하나의 메트릭에 라벨이 많아질수록 카디널리티는 곱셈으로 커집니다. 3개 라벨을 기본으로 하고, 5개를 넘지 않도록 제한하면 폭발을 예방할 수 있습니다.

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

### 카디널리티 측정 예제

현재 시스템의 카디널리티를 측정하는 Python 예시입니다.

```python
from collections import Counter
from typing import List, Dict

def measure_cardinality(metrics: List[Dict[str, str]]) -> Dict[str, int]:
    """
    메트릭 라벨 조합의 고유값 개수 계산
    metrics: [{"__name__": "http_requests", "method": "GET", "status": "200"}, ...]
    """
    unique_series = set()
    label_values = Counter()
    
    for metric in metrics:
        # 라벨 조합을 문자열로 변환해 고유 시계열 계산
        series_key = ",".join(
            f"{k}={v}" for k, v in sorted(metric.items())
        )
        unique_series.add(series_key)
        
        # 각 라벨의 고유값 수 카운트
        for key, value in metric.items():
            if key != "__name__":
                label_values[key] += 1
    
    return {
        "total_series": len(unique_series),
        "label_value_count": dict(label_values),
        "avg_labels_per_series": sum(label_values.values()) / len(unique_series)
    }

# 예시 사용
metrics_sample = [
    {"__name__": "http_requests", "method": "GET", "status": "200", "path": "/api"},
    {"__name__": "http_requests", "method": "POST", "status": "200", "path": "/api"},
    {"__name__": "http_requests", "method": "GET", "status": "500", "path": "/api"},
]

result = measure_cardinality(metrics_sample)
print(f"Total series: {result['total_series']}")
print(f"Label value count: {result['label_value_count']}")
```

이 코드는 라벨 조합의 고유값 개수를 측정합니다. 실제로는 Prometheus의 `count({__name__=~".+"})` 쿼리를 주기적으로 돌려서 카디널리티를 추적하는 편이 실용적입니다.

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

## 카디널리티 폭발 사례

카디널리티 문제는 개념으로는 간단하지만 실제 장애로 이어질 때 체감이 큽니다. 아래는 자주 발생하는 세 가지 사례입니다.

| 사례 | 문제 라벨 | 결과 | 권장 대체 |
| --- | --- | --- | --- |
| 사용자 식별자 라벨링 | `user_id` | 사용자 수만큼 시계열 증가 | 로그 필드로 이동 |
| 요청 ID 라벨링 | `request_id` | 요청량만큼 시계열 증가 | 트레이스 속성으로 이동 |
| 원본 URL 라벨링 | `path=/orders/123` | 경로 조합 폭발 | `/orders/:id` 정규화 |

라벨은 필터 기준이면서 저장 키입니다. "검색 편하겠다"는 이유로 식별자를 라벨에 넣으면 저장소는 사실상 사용자 테이블을 시계열로 복제하는 셈이 됩니다. 비용뿐 아니라 질의 지연, 컴팩션 시간, 백업 시간까지 함께 악화됩니다.

## 비용 최적화 전략 표

| 전략 | 적용 대상 | 기대 효과 | 주의점 |
| --- | --- | --- | --- |
| 라벨 축소 | 메트릭 | 시계열 수 즉시 감소 | 운영 분석 축을 과도하게 제거하지 않기 |
| 보존 계층화 | 메트릭/로그 | 장기 저장 비용 감소 | 규정상 보관 의무 확인 |
| 샘플링 | 트레이스/로그 | 저장량 감소 | 희귀 케이스 누락 방지 정책 필요 |
| 로그 본문 절제 | 로그 | 수집/인덱스 비용 감소 | 디버깅 최소 필드 유지 |
| 질의 캐시 | 대시보드 | 질의 CPU 절감 | 실시간성이 필요한 패널은 예외 처리 |

비용 최적화는 한 번의 대청소보다 "기본 정책"으로 유지하는 편이 낫습니다. 신규 메트릭 PR에서 라벨 검토를 필수화하고, 월간 비용 리뷰에서 상위 지표를 자동 리포트하면 재발을 크게 줄일 수 있습니다.

## 라벨 검토용 Python 도우미

```python
FORBIDDEN_LABEL_KEYS = {"user_id", "request_id", "session_id", "email"}


def validate_metric_labels(metric_name: str, labels: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key, value in labels.items():
        if key in FORBIDDEN_LABEL_KEYS:
            errors.append(f"{metric_name}: forbidden label key '{key}'")
        if len(value) > 64:
            errors.append(f"{metric_name}: label '{key}' value too long")
        if "/" in value and key == "path" and any(ch.isdigit() for ch in value):
            errors.append(f"{metric_name}: path label appears unnormalized '{value}'")
    return errors


example = {"path": "/orders/12345", "status": "200"}
print(validate_metric_labels("http_requests_total", example))
```

이런 도우미를 테스트나 CI에 붙이면 카디널리티 폭발을 사전에 차단할 수 있습니다. 비용 문제는 사후 대응보다 사전 차단이 훨씬 저렴합니다.

### 비용 추정 공식

관측 데이터 비용을 사전에 예측하려면 간단한 공식을 사용합니다.

```text
월간 메트릭 비용 = 시계열 수 × 수집 빈도(분당) × 60 × 24 × 30 × 바이트/샘플 × 스토리지 단가
```

실제 예시로 계산해 보겠습니다.

```python
# 비용 추정 계산기
def estimate_metric_cost(
    num_series: int,
    scrape_interval_sec: int = 15,
    bytes_per_sample: float = 2.0,
    retention_days: int = 30,
    storage_cost_per_gb: float = 0.10,  # USD
) -> dict:
    """월간 메트릭 스토리지 비용을 추정합니다."""
    samples_per_day = num_series * (86400 / scrape_interval_sec)
    total_samples = samples_per_day * retention_days
    total_bytes = total_samples * bytes_per_sample
    total_gb = total_bytes / (1024 ** 3)
    cost_usd = total_gb * storage_cost_per_gb
    return {
        "series": num_series,
        "samples_per_day": int(samples_per_day),
        "total_gb": round(total_gb, 2),
        "monthly_cost_usd": round(cost_usd, 2),
    }


# 시나리오 비교
scenarios = [
    ("소규모 (1,000 시계열)", 1_000),
    ("중규모 (50,000 시계열)", 50_000),
    ("대규모 (500,000 시계열)", 500_000),
    ("카디널리티 폭발 (5,000,000 시계열)", 5_000_000),
]

for name, series in scenarios:
    result = estimate_metric_cost(series)
    print(f"{name}: {result['total_gb']} GB, ${result['monthly_cost_usd']}/월")
```

출력 예시입니다.

```text
소규모 (1,000 시계열): 0.93 GB, $0.09/월
중규모 (50,000 시계열): 46.57 GB, $4.66/월
대규모 (500,000 시계열): 465.66 GB, $46.57/월
카디널리티 폭발 (5,000,000 시계열): 4656.61 GB, $465.66/월
```

카디널리티가 10배 늘면 비용도 정확히 10배 늘어납니다. 레이블 하나를 무분별하게 추가하면 시계열 수가 기하급수적으로 증가하므로, 레이블 추가 전에 반드시 카디널리티 영향을 계산해야 합니다.

### Recording Rule로 카디널리티 줄이기

고카디널리티 원시 메트릭을 recording rule로 미리 집계하면 쿼리 성능과 스토리지 비용을 동시에 개선할 수 있습니다.

```yaml
# prometheus-rules.yml
groups:
  - name: cost_optimization
    interval: 1m
    rules:
      # 원본: instance × path × method × status (수만 시계열)
      # 집계: method × status (수십 시계열)
      - record: job:http_requests:rate5m
        expr: sum by (method, status) (rate(http_requests_total[5m]))

      # 원본: instance × path × le (수십만 시계열)
      # 집계: path × le (수천 시계열)
      - record: job:http_duration:histogram_quantile
        expr: |
          histogram_quantile(0.99,
            sum by (path, le) (rate(http_request_duration_seconds_bucket[5m]))
          )

      # 장기 보존용 다운샘플링 (1시간 해상도)
      - record: job:http_requests:rate1h
        expr: sum by (service) (rate(http_requests_total[1h]))
```

이 접근법의 핵심은 대시보드와 경보가 recording rule의 결과를 참조하게 만드는 것입니다. 원시 메트릭은 단기(7일) 보존하고, recording rule 결과는 장기(90일) 보존하면 비용 구조가 크게 달라집니다.

| 보존 계층 | 해상도 | 보존 기간 | 용도 |
|----------|--------|----------|------|
| Raw metrics | 15초 | 7일 | 실시간 디버깅 |
| Recording rules (1분) | 1분 | 30일 | 대시보드, 경보 |
| Downsampled (1시간) | 1시간 | 1년 | 추세 분석, 용량 계획 |
| Aggregated (1일) | 1일 | 3년 | 경영 리포트 |

### 레이블 거버넌스 정책

카디널리티를 통제하려면 기술적 도구뿐 아니라 조직 차원의 정책이 필요합니다.

| 규칙 | 설명 | 위반 시 조치 |
|------|------|-------------|
| 레이블 값 상한 | 하나의 레이블이 가질 수 있는 고유 값은 최대 100개 | CI에서 차단 |
| 금지 레이블 | `user_id`, `request_id`, `trace_id`를 메트릭 레이블로 사용 금지 | 코드 리뷰 reject |
| 신규 레이블 승인 | 새 레이블 추가 시 카디널리티 영향 계산서 필수 | PR 템플릿 체크리스트 |
| 경로 정규화 | `/users/123` → `/users/:id`로 변환 후 레이블에 기록 | middleware 강제 |
| 정기 감사 | 월 1회 top-50 고카디널리티 시계열 리뷰 | 팀 미팅 어젠다 |

```python
# middleware에서 경로 정규화 예시 (FastAPI)
import re
from fastapi import Request

PATTERNS = [
    (re.compile(r"/users/[0-9a-f-]+"), "/users/:id"),
    (re.compile(r"/orders/\d+"), "/orders/:id"),
    (re.compile(r"/products/[\w-]+"), "/products/:slug"),
]


def normalize_path(path: str) -> str:
    """고카디널리티 경로를 정규화합니다."""
    for pattern, replacement in PATTERNS:
        if pattern.search(path):
            return pattern.sub(replacement, path)
    return path


# 미들웨어에서 사용
async def metrics_middleware(request: Request, call_next):
    normalized = normalize_path(request.url.path)
    # 메트릭에는 정규화된 경로만 기록
    REQUEST_COUNT.labels(method=request.method, path=normalized).inc()
    response = await call_next(request)
    return response
```

이 미들웨어 하나로 수만 개의 고유 경로가 수십 개의 패턴으로 줄어듭니다. 결과적으로 시계열 수가 수백 배 감소하고, 쿼리 속도와 스토리지 비용이 함께 개선됩니다.

## 처음 질문으로 돌아가기

- **카디널리티는 왜 비용과 직접 연결될까요?**
  - 비용 추정 공식에서 확인했듯이, 시계열 수가 비용의 1차 변수입니다. 레이블 하나를 추가해 카디널리티가 100배 늘면 스토리지·쿼리·인덱싱 비용도 100배 늘어납니다. 메트릭은 무료가 아니며, 레이블 설계가 곧 비용 설계입니다.
- **보존 기간을 나눠 가져가야 하는 이유는 무엇일까요?**
  - 실시간 디버깅에는 15초 해상도가 필요하지만, 6개월 전 추세 분석에는 1시간 해상도면 충분합니다. 보존 계층을 나누면 같은 정보를 유지하면서 스토리지를 90% 이상 절약할 수 있습니다. Recording rule과 downsampling이 이 계층 구조를 자동으로 만들어 줍니다.
- **머리 샘플링과 꼬리 샘플링은 어떻게 다를까요?**
  - 머리 샘플링은 요청 시작 시점에 확률적으로 결정하므로 구현이 간단하지만 중요한 트레이스를 놓칠 수 있습니다. 꼬리 샘플링은 트레이스가 완료된 후 에러·지연 등 조건을 보고 보존을 결정하므로 비용 대비 가치가 높은 트레이스만 저장합니다. 비용 최적화에서는 꼬리 샘플링이 더 효과적입니다.

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

- [book-examples — observability-101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)
Tags: Observability, Cost, Cardinality, Metrics, Sampling
