---
series: observability-101
episode: 3
title: "바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Metrics
  - Prometheus
  - Grafana
seo_description: 바이브코딩으로 만든 서비스에 Prometheus pull 모델로 메트릭을 붙이고 Grafana로 시각화하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 세 번째 글입니다. AI가 만든 서비스에 메트릭을 붙이는 가장 빠른 방법과, 수집된 숫자를 실제로 운영에 도움이 되는 화면으로 만드는 방법을 다룹니다.

---

메트릭이 중요하다는 말은 많이 듣지만, 실제 운영에서는 두 번째 질문이 더 중요합니다. 그 숫자가 어디서 나오고, 누가 가져가고, 어떤 화면에서 읽히는가입니다. 바이브코딩으로 만든 앱에 `prometheus_client` 한 줄 추가하는 것만으로는 관측성이 완성되지 않습니다.

AI에게 "Prometheus 메트릭 붙여줘"라고 하면 `/metrics` 엔드포인트를 노출하는 코드는 받습니다. 하지만 그 코드가 실제로 수집되고, 저장되고, 그래프로 표현되려면 파이프라인 전체를 이해해야 합니다.

> "메트릭 파이프라인은 애플리케이션, 수집기, 저장소, 대시보드가 이어진 흐름입니다. 어느 하나라도 끊기면 장애 때 화면이 비어 있습니다."

## 이 글에서 다룰 문제

- 메트릭은 어떻게 수집되고 그래프로 바뀔까요?
- pull 방식과 push 방식은 무엇이 다를까요?
- `/metrics` 엔드포인트는 어떤 역할을 할까요?
- 카운터를 그대로 그리면 왜 안 될까요?
- AI가 메트릭 코드를 짤 때 자주 하는 실수는 무엇일까요?

---

AI에게 "CPU 사용량 모니터링 추가해줘"라고 하면 게이지 메트릭을 붙여줍니다. "요청 수 메트릭 추가해줘"라고 하면 카운터를 붙여줍니다. 그런데 그 카운터를 Grafana에서 그대로 선 그래프로 그리면 계속 올라가는 선만 보입니다. 지금 초당 요청이 얼마나 들어오는지 보려면 `rate()`를 써야 합니다.

AI가 주는 코드를 그대로 쓰면 이런 오해가 생기기 쉽습니다. 파이프라인의 각 단계를 이해해야 AI에게 올바른 질문을 던질 수 있습니다.

## 메트릭 유형 비교

| 유형 | 정의 | 예시 | 언제 쓰는가 |
| --- | --- | --- | --- |
| Counter | 계속 증가하는 값 | 총 요청 수, 에러 건수 | 누적량을 기록할 때 |
| Gauge | 오르내리는 값 | CPU 사용률, 큐 길이 | 현재 상태를 나타낼 때 |
| Histogram | 분포를 버킷으로 저장 | 응답 시간 분포 (p95, p99) | 꼬리 지연을 보려고 할 때 |

AI에게 메트릭 코드를 요청할 때 "응답 시간은 Histogram, 요청 수는 Counter, 큐 길이는 Gauge로 써줘"라고 타입을 지정하면 훨씬 정확한 코드를 받습니다.

## prometheus_client로 메트릭 노출하기

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

def handle_request(method: str, endpoint: str):
    active_connections.inc()

    start = time.time()
    status = 200 if random.random() > 0.1 else 500
    time.sleep(random.uniform(0.1, 1.0))
    duration = time.time() - start

    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    active_connections.dec()
    return status

# 메트릭 서버 시작 (8000번 포트에 /metrics 노출)
if __name__ == "__main__":
    start_http_server(8000)
    while True:
        handle_request("GET", "/api/users")
        time.sleep(1)
```

이 코드를 실행하고 `curl localhost:8000/metrics`를 호출하면 Prometheus 형식의 메트릭이 보입니다. 여기서 중요한 점은 `status` 라벨이 200, 500 등 유한한 값만 가진다는 것입니다. user_id나 request_id를 라벨로 넣으면 카디널리티가 폭발합니다.

## Pull vs Push 방식 비교

| 구분 | Pull (끌어오기) | Push (밀어넣기) |
| --- | --- | --- |
| 대표 도구 | Prometheus | Datadog, CloudWatch |
| 동작 | 수집기가 주기적으로 엔드포인트 호출 | 애플리케이션이 수집기로 전송 |
| 장점 | 수집 주기 통제 쉽고 타깃 발견 쉬움 | 방화벽 안에서도 동작 |
| 사용 상황 | 쿠버네티스, 마이크로서비스 | 서버리스, 단기 작업 |

바이브코딩으로 만든 서비스가 컨테이너 기반이라면 Prometheus pull 방식이 가장 자연스럽습니다. 서버리스(Lambda, Cloud Run)라면 push 방식이 필요합니다. AI에게 배포 환경을 알려주면 적합한 방식을 선택해줍니다.

## Before / After: 메트릭 파이프라인 없을 때와 있을 때

**Before**

```text
"지금 서비스 느린 것 같은데?"
→ 로그 확인 (느림)
→ SSH 접속해서 top 실행
→ 스냅샷만 보임, 추세 파악 불가
→ 5분 전에 무슨 일이 있었는지 알 수 없음
```

**After**

```text
Grafana 대시보드 열기
→ Request Rate: 평소 100 req/s → 지금 8 req/s (급감)
→ Error Rate: 0.5% → 12% (급증)
→ p95 Latency: 200ms → 2.3s (10배 증가)
→ 15분 전 배포 주석이 시작점과 정확히 일치
```

## PromQL 핵심 패턴

AI에게 Grafana 패널을 만들어달라고 할 때 이 패턴을 이해하면 더 정확한 요청을 할 수 있습니다.

```promql
# 초당 처리량 (카운터를 그대로 그리면 안 됨)
sum(rate(http_requests_total[1m]))

# 5xx 에러율
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# p95 지연 시간 (Histogram 필수)
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

카운터는 항상 `rate()`를 통해 읽어야 합니다. AI가 생성한 Grafana 패널이 카운터를 그대로 그린다면 즉시 `rate()`로 감싸도록 수정 요청하세요.

## 자주 하는 실수

| 실수 | 문제 | AI 코드에서 확인할 점 |
| --- | --- | --- |
| 카운터를 그대로 그래프로 그림 | 계속 올라가는 선만 보임 | PromQL에 `rate()` 없는지 확인 |
| 고유 식별자를 라벨에 넣음 | 카디널리티 급증 | `user_id`, `order_id` 라벨 없는지 확인 |
| 수집 주기를 1초로 설정 | 수집기와 앱 모두 부담 | `scrape_interval: 15s`가 기본 |
| 질문 없는 패널 추가 | 대시보드가 벽지가 됨 | 각 패널이 어떤 질문에 답하는지 정의 |
| 메타 경보 없음 | 수집기 죽으면 모든 경보 침묵 | Prometheus 자체 헬스체크 경보 필요 |

## AI 프롬프트 팁

```text
[메트릭 파이프라인 구성 요청]
"이 서비스에 메트릭 파이프라인 구성해줘:
1. prometheus_client로 다음 메트릭 노출:
   - http_requests_total (Counter, labels: method, status, path_pattern)
   - http_request_duration_seconds (Histogram, labels: method, path_pattern)
   - active_connections (Gauge)
2. path_pattern은 /users/123 같은 것을 /users/:id로 정규화
3. Prometheus scrape_interval은 15s로 설정
4. Grafana 패널: Request Rate, Error Rate, p95 Latency (rate() 사용)"
```

## 운영 체크리스트

- [ ] 애플리케이션이 `/metrics`를 노출합니다.
- [ ] Prometheus에서 대상이 정상으로 보입니다.
- [ ] PromQL 질의를 하나 이상 직접 쓸 수 있습니다.
- [ ] 카운터는 `rate()`로 읽는다는 것을 압니다.
- [ ] 카디널리티 폭발 조건을 예를 들어 설명할 수 있습니다.

## 처음 질문으로 돌아가기

- **메트릭은 어떻게 수집되고 그래프로 바뀔까요?**
  앱이 `/metrics`를 노출하고, Prometheus가 주기적으로 pull해서 저장하고, Grafana가 PromQL로 질의해 그래프로 만듭니다. 이 파이프라인의 어느 단계가 끊겨도 장애 때 화면이 비어 있습니다.

- **pull 방식과 push 방식은 무엇이 다를까요?**
  Prometheus는 pull: 수집기가 앱 엔드포인트를 호출합니다. Datadog 등은 push: 앱이 수집기로 전송합니다. 컨테이너 기반이면 pull, 서버리스면 push가 적합합니다.

- **카운터를 그대로 그리면 왜 안 될까요?**
  카운터는 누적값이라 계속 올라가는 선만 보입니다. `rate()`로 초당 증가량으로 변환해야 현재 처리량이 보입니다.

---

## 정리

메트릭 파이프라인이 붙으면 시스템은 그래프로 말하기 시작합니다. 바이브코딩으로 만든 서비스에 AI의 도움을 받아 메트릭을 붙일 때, 파이프라인의 전체 흐름을 이해하고 카운터/게이지/히스토그램을 올바르게 사용하는 것이 핵심입니다. 다음 글에서는 숫자만으로 부족한 이유와 구조화된 로그가 왜 필요한지 살펴봅니다.

## 참고 자료

- [Prometheus getting started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [prometheus_client (Python)](https://github.com/prometheus/client_python)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana docs](https://grafana.com/docs/grafana/latest/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스
- **바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅
- 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Metrics, Prometheus, Grafana
