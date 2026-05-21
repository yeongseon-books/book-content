---
series: observability-101
episode: 3
title: "Observability 101 (3/10): 메트릭 수집과 시각화"
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
  - Metrics
  - Prometheus
  - Grafana
  - Monitoring
seo_description: Prometheus pull 모델, PromQL, Grafana까지 메트릭 파이프라인의 첫 구성을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (3/10): 메트릭 수집과 시각화

메트릭이 중요하다는 말은 많이 듣지만, 실제 운영에서는 두 번째 질문이 더 중요합니다. 그 숫자가 어디서 나오고, 누가 가져가고, 어떤 화면에서 읽히는가입니다. 숫자를 노출하는 코드 한 줄만으로는 관측성이 만들어지지 않습니다.

메트릭 파이프라인은 애플리케이션, 수집기, 저장소, 대시보드가 이어진 흐름입니다. 이 흐름을 이해하면 왜 Prometheus가 pull 모델을 택했는지, 왜 카운터를 그대로 그리면 안 되는지, 왜 대시보드는 질문 중심이어야 하는지까지 함께 정리됩니다.

이 글은 Observability 101 시리즈의 3번째 글입니다.

## 먼저 던지는 질문

- 메트릭은 어떻게 수집되고 그래프로 바뀔까요?
- pull 방식과 push 방식은 무엇이 다를까요?
- `/metrics` 엔드포인트는 어떤 역할을 할까요?

## 큰 그림

![Observability 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/03/03-01-concept-at-a-glance.ko.png)

*Observability 101 3장 흐름 개요*

메트릭 수집과 시각화를 다루는 이번 장에서는 주요 개념과 실무 패턴을 봅니다. 시스템이 복잡해질수록 이 개념들이 어디에서 시작되고 어떤 결과를 만드는지 이해하는 것이 중요합니다.

> 메트릭 수집과 시각화의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 왜 중요한가

메트릭 파이프라인은 관측성의 출발선입니다. 첫 바이트가 흐르는 순간부터 시스템은 숫자로 말을 하기 시작합니다. 요청 수가 늘고 있는지, 에러율이 올라가는지, 지연 시간이 흔들리는지처럼 운영의 기본 질문은 대부분 메트릭에서 출발합니다.

문제는 메트릭을 잘못 수집하거나 잘못 그리면 오히려 오해가 커진다는 점입니다. 카운터를 그대로 선 그래프로 그리거나, 라벨을 과하게 붙이거나, 1초마다 무리하게 수집하면 숫자는 많아져도 판단은 더 느려집니다. 그래서 수집과 시각화는 함께 배워야 합니다.

## 메트릭 유형 비교

메트릭은 네 가지 주요 유형으로 나뉩니다. 각각의 정의, 예시, 사용 상황을 정리하면 언제 무엇을 쓸지 판단하기 쉬워집니다.

| 유형 | 정의 | 예시 | 언제 쓰는가 |
| --- | --- | --- | --- |
| Counter | 계속 증가하는 값 | 총 요청 수, 에러 건수 | 누적량을 기록할 때 |
| Gauge | 오르내리는 값 | CPU 사용률, 큐 길이, 메모리 | 현재 상태를 나타낼 때 |
| Histogram | 분포를 버킷으로 저장 | 응답 시간 분포 (p50, p95, p99) | 꼬리 지연을 보려고 할 때 |
| Summary | 분위를 클라이언트에서 계산 | p95, p99 (클라이언트 측 계산) | 서버 부담을 줄이고 싶을 때 |

Prometheus에서는 Histogram을 더 권장합니다. Summary는 클라이언트에서 분위를 계산하기 때문에 여러 인스턴스를 합치기 어렵고, Histogram은 서버에서 나중에 임의의 분위를 계산할 수 있습니다.

## prometheus_client로 메트릭 노출하기

Python에서 prometheus_client 라이브러리를 쓰면 간단하게 메트릭을 노출할 수 있습니다.

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
import random

# 메트릭 정의
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# 사용 예시
def handle_request(method: str, endpoint: str):
    active_connections.inc()
    
    start = time.time()
    status = 200 if random.random() > 0.1 else 500
    
    # 요청 처리 시뮬레이션
    time.sleep(random.uniform(0.1, 1.0))
    
    duration = time.time() - start
    
    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    active_connections.dec()
    return status

# 메트릭 서버 시작 (8000번 포트에 /metrics 노출)
if __name__ == "__main__":
    start_http_server(8000)
    print("Metrics server running on :8000/metrics")
    
    while True:
        handle_request("GET", "/api/users")
        time.sleep(1)
```

이 코드를 실행하고 `curl localhost:8000/metrics`를 호출하면 Prometheus 형식의 메트릭을 볼 수 있습니다. Prometheus는 이 엔드포인트를 주기적으로 읽어 저장합니다.

## 카디널리티 폭발 방지

카디널리티는 라벨 조합이 얼마나 많이 생기는지를 뜻합니다. 예를 들어 user_id를 라벨로 붙이면 사용자 수만큼 메트릭 종류가 늘어나고, Prometheus는 각각을 별도 시계열로 저장하기 때문에 메모리와 디스크 비용이 폭발합니다.

### 피해야 할 패턴

1. **고유 식별자를 라벨에 넣지 말기**: user_id, order_id, session_id 같은 값은 로그나 트레이스 속성으로 남깁니다.
2. **라벨 값을 제한하기**: HTTP 경로를 라벨로 쓸 때 `/api/users/123` 대신 `/api/users/:id`처럼 패턴으로 정규화합니다.
3. **필요한 라벨만 남기기**: method, status, endpoint처럼 집계할 가치가 있는 차원만 라벨로 붙입니다.

### 카디널리티 추정

라벨 값이 각각 N개씩이면 카디널리티는 곱입니다. method 3가지 × endpoint 10가지 × status 5가지 = 150 시계열입니다. 라벨 하나를 더하기 전에 정말 필요한지, 대신 로그로 남길 수 있는지 먼저 물어봐야 합니다.

## 한눈에 보는 구조

메트릭은 애플리케이션에서 시작해 저장소로 모여 대시보드로 표현됩니다. Pull과 push 방식이 있고, 각각 운영 환경에서 다른 장단점을 가집니다.

## 핵심 용어

- 익스포터: HTTP로 메트릭을 노출하는 구성 요소입니다.
- 수집 주기: Prometheus가 메트릭을 읽어 오는 간격입니다.
- 시계열: 라벨 집합, 값, 시각으로 이루어진 데이터입니다.
- PromQL: Prometheus 질의 언어입니다.
- 패널: 대시보드 안의 개별 그래프입니다.

## Pull vs Push 방식 비교

메트릭 수집에는 크게 두 가지 방식이 있습니다.

| 구분 | Pull (끝어오기) | Push (밀어넣기) |
| --- | --- | --- |
| 대표 도구 | Prometheus | Datadog, CloudWatch |
| 동작 | 수집기가 주기적으로 엔드포인트 호출 | 애플리케이션이 수집기로 전송 |
| 장점 | 수집 주기 통제 쉽고, 타깃 발견 쉽음 | 방화벽 안에서도 동작, 짧은 수명 작업 수집 가능 |
| 단점 | 수집기가 엔드포인트에 도달 불가하면 실패 | 애플리케이션에 수집기 주소 설정 필요 |
| 사용 상황 | 쿠버네티스, 마이크로서비스 | 서버리스, 단기 작업 |

Prometheus는 pull 모델을 택했습니다. 수집기가 주도권을 가지기 때문에 어떤 타깃을 언제 읽을지 통제하기 쉽고, 타깃 발견도 서비스 디스커버리와 연결하면 자동화할 수 있습니다.

## 바꾸기 전과 후

바꾸기 전에는 로그 몇 줄을 보며 "아마 지금도 요청이 늘고 있겠지"라고 짐작합니다. 추세를 읽는 데 시간이 오래 걸리고, 지난 10분과 지금을 비교하기도 어렵습니다.

바꾼 뒤에는 초 단위 그래프가 바로 보입니다. 요청 수가 늘었는지, 특정 경로만 올라가는지, 지연 시간이 어느 시점부터 흔들렸는지 화면 한 줄로 확인할 수 있습니다. 추세를 추측하는 대신 읽을 수 있게 됩니다.

## 실습: 메트릭 파이프라인을 다섯 단계로 만들기

### 1단계 — 파이썬에서 메트릭 엔드포인트 노출하기

```python
from prometheus_client import Counter, start_http_server

reqs = Counter("http_requests_total", "Total requests", ["path"])

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        reqs.labels(path="/health").inc()
```

애플리케이션은 먼저 메트릭을 바깥으로 보여 줄 수 있어야 합니다. `/metrics` 엔드포인트는 사람보다 수집기가 읽는 표준 출입구라고 생각하면 됩니다.

### 2단계 — 수집기 설정하기

```yaml
scrape_configs:
  - job_name: app
    scrape_interval: 5s
    static_configs:
      - targets: ["app:8000"]
```

Prometheus는 push를 기다리지 않고 pull로 읽어 옵니다. 어느 대상을 몇 초마다 읽을지 선언해 두면, 수집기가 주기적으로 `/metrics`를 호출합니다.

### 3단계 — 수집기 실행하기

```bash
docker run -d --name prom -p 9090:9090 \
  -v $(pwd)/prom.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

이 단계부터 메트릭은 메모리 안 숫자가 아니라 저장되는 시계열이 됩니다. 수집기가 붙지 않으면 노출된 메트릭은 흘러가 버리는 값에 가깝습니다.

### 4단계 — 첫 질의 써 보기

```promql
rate(http_requests_total[1m])
sum by (path) (rate(http_requests_total[5m]))
```

카운터는 누적값이기 때문에 그대로 그리면 해석이 어렵습니다. `rate()`로 초당 증가량으로 바꿔야 현재 처리량이 보입니다. 이 한 줄이 메트릭 해석에서 가장 자주 쓰는 기본기입니다.

### 5단계 — 첫 대시보드 패널 만들기

```bash
docker run -d --name graf -p 3000:3000 grafana/grafana
# Browser: http://localhost:3000
# Datasource: Prometheus → http://prom:9090
# Panel: rate(http_requests_total[1m])
```

대시보드는 숫자를 꾸미는 화면이 아니라 질문을 붙이는 화면입니다. 첫 패널은 "지금 요청이 얼마나 들어오는가"처럼 하나의 질문만 정확히 답하게 두는 편이 좋습니다.

## 수집 경로를 이렇게 검증합니다

메트릭 파이프라인은 코드가 아니라 경로가 끊겨도 바로 무용지물이 됩니다. 그래서 애플리케이션, 수집기, 대시보드를 각각 한 번씩 확인하는 절차가 필요합니다.

```bash
# 1) 애플리케이션이 메트릭을 노출하는지 확인
curl -s http://localhost:8000/metrics | grep http_requests_total

# 2) Prometheus 타깃이 살아 있는지 확인
curl -s http://localhost:9090/api/v1/targets | grep '"health":"up"'
```

```text
Expected output:
- /metrics 응답에 http_requests_total 이 보입니다.
- Prometheus /targets 에서 app 타깃이 up 으로 보입니다.
- Grafana 패널에서 rate(http_requests_total[1m]) 값이 0이 아닌 선으로 그려집니다.
```

## 이 코드에서 먼저 봐야 할 점

- Prometheus는 끌어오고, 애플리케이션은 노출합니다.
- `/metrics`는 평문 형식의 메트릭을 반환합니다.
- 카운터는 거의 항상 `rate()`를 거쳐 읽는다고 생각하면 됩니다.

## 자주 하는 실수 다섯 가지

1. 카운터를 그대로 그래프로 그립니다. 증가량이 아니라 누적값이라 해석이 어렵습니다.
2. 고유 식별자를 라벨에 넣습니다. 카디널리티가 급격히 커집니다.
3. 수집 주기를 1초로 과하게 줄입니다. 대상 서비스와 수집기 모두 부담이 커집니다.
4. 방화벽 때문에 pull이 막히는데도 애플리케이션 문제로 오해합니다.
5. 질문 없는 패널을 계속 추가합니다. 대시보드가 벽지처럼 변합니다.

## 실무에서는 이렇게 생각한다

작은 팀은 대개 Prometheus와 Grafana로 시작합니다. 규모가 커지면 장기 저장과 집계를 위해 Thanos나 Mimir 같은 구성을 더하지만, 출발점의 원리는 같습니다. 메트릭은 먼저 잘 노출되고, 안정적으로 수집되고, 질문 중심으로 그려져야 합니다.

시니어 엔지니어는 대시보드보다 먼저 파이프라인을 봅니다. 수집 주기가 적절한지, 라벨이 통제되고 있는지, 쿼리가 누적값과 증가량을 헷갈리지 않는지부터 점검합니다. 숫자가 많다고 관측성이 좋아지는 것은 아니기 때문입니다.

## 체크리스트

- [ ] 애플리케이션이 `/metrics`를 노출합니다.
- [ ] Prometheus에서 대상이 정상으로 보입니다.
- [ ] PromQL 질의를 하나 이상 직접 쓸 수 있습니다.
- [ ] Grafana에서 첫 패널을 만들 수 있습니다.

## 연습 문제

1. Counter와 Gauge를 하나씩 노출해 보세요.
2. `rate()`와 `increase()`의 차이를 설명해 보세요.
3. 5분 평균 처리량을 보여 주는 패널을 설계해 보세요.

## 정리

메트릭 파이프라인이 붙으면 시스템은 그래프로 말을 하기 시작합니다. 애플리케이션은 메트릭을 노출하고, Prometheus는 수집하고, Grafana는 질문 단위의 화면으로 바꿉니다. 다음 글에서는 숫자만으로 부족한 이유, 곧 구조화된 로그가 왜 필요한지 이어서 보겠습니다.

## Prometheus 스크레이프 구성 예시

실무에서는 서비스 수가 늘면서 스크레이프 설정이 빠르게 복잡해집니다. 아래 예시는 정적 타깃과 Kubernetes 서비스 디스커버리를 함께 쓰는 기본 구성입니다.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 30s

scrape_configs:
  - job_name: "app-static"
    scrape_interval: 5s
    static_configs:
      - targets: ["app-1:8000", "app-2:8000"]
        labels:
          team: "checkout"
          env: "prod"

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-a:9100", "node-b:9100"]

  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: ${1}
```

구성 포인트는 두 가지입니다. 첫째, 모든 잡에 동일 간격을 쓰지 않습니다. 변화가 빠른 API는 5초, 상대적으로 완만한 노드 지표는 15초 이상으로 분리하면 수집 비용을 줄일 수 있습니다. 둘째, `team`, `env` 같은 운영 라벨을 명시적으로 붙여 질의와 라우팅을 단순화합니다.

## Counter, Gauge, Histogram 실전 코드

아래 예시는 동일 요청에서 세 메트릭 타입을 어떻게 함께 쓰는지 보여 줍니다.

```python
import random
import time
from prometheus_client import Counter, Gauge, Histogram

REQUEST_TOTAL = Counter(
    "checkout_requests_total",
    "Total checkout requests",
    ["route", "status"],
)

INFLIGHT = Gauge(
    "checkout_inflight_requests",
    "In-flight checkout requests",
)

LATENCY = Histogram(
    "checkout_request_duration_seconds",
    "Checkout request duration",
    ["route"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)


def handle_checkout(route: str = "/checkout") -> int:
    INFLIGHT.inc()
    started = time.time()
    try:
        time.sleep(random.uniform(0.03, 0.7))
        status = 500 if random.random() < 0.08 else 200
        REQUEST_TOTAL.labels(route=route, status=str(status)).inc()
        return status
    finally:
        LATENCY.labels(route=route).observe(time.time() - started)
        INFLIGHT.dec()
```

Counter는 누적 사실을 기록합니다. Gauge는 현재 순간 상태를 기록합니다. Histogram은 분포를 기록합니다. 세 타입을 분리하지 않고 하나로 뭉개면, 나중에 경보를 설계할 때 의미가 섞여 잘못된 결론으로 이어질 수 있습니다.

## PromQL 해석 패턴

대시보드 품질은 질의 품질과 같습니다. 아래 세 질의는 가장 자주 쓰는 기본 패턴입니다.

```promql
# 초당 처리량
sum(rate(checkout_requests_total[1m]))

# 5xx 비율
sum(rate(checkout_requests_total{status=~"5.."}[5m]))
/
sum(rate(checkout_requests_total[5m]))

# p95 지연
histogram_quantile(
  0.95,
  sum by (le) (rate(checkout_request_duration_seconds_bucket[5m]))
)
```

해석 순서는 항상 동일하게 가져가는 편이 좋습니다. 먼저 분모와 분자가 맞는지 확인하고, 다음으로 집계 축(`by`)이 과하거나 부족하지 않은지 봅니다. 마지막으로 윈도우 길이가 질문에 맞는지 점검합니다. 30초 단위 흔들림을 보려면 5분 윈도우는 너무 느리고, 월간 추세를 보려면 1분 윈도우는 너무 시끄럽습니다.

## 처음 질문으로 돌아가기

- **메트릭은 어떻게 수집되고 그래프로 바뀔까요?**
  - 본문의 기준은 메트릭 수집과 시각화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **pull 방식과 push 방식은 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`/metrics` 엔드포인트는 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- **메트릭 수집과 시각화 (현재 글)**
- 구조화된 로깅 (예정)
- 분산 트레이싱 기초 (예정)
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Prometheus getting started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [prometheus_client (Python)](https://github.com/prometheus/client_python)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana docs](https://grafana.com/docs/grafana/latest/)

Tags: Observability, Metrics, Prometheus, Grafana, Monitoring
