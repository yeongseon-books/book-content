
# 모니터링과 알림

> DevOps 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *서비스가 죽었다는 사실* 을 *고객이 먼저 알게* 된 적이 있나요?

> 좋은 모니터링은 *고객보다 먼저* 우리에게 알려줍니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *모니터링* 의 *세 가지 신호* (logs, metrics, traces)
- *Prometheus* 와 *Grafana* 기본 흐름
- *RED / USE* 메트릭 패턴
- *의미 있는 알림* 설계
- 흔한 함정 5가지

## 왜 중요한가

장애는 *언제나 옵니다*. 차이는 *얼마나 빨리 아느냐* 와 *어디가 문제인지 얼마나 빨리 좁히느냐* 입니다.

> 모니터링 없는 운영은 *눈 감고 운전* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    App["app /metrics"] --> Scrape["Prometheus scrape"]
    Scrape --> TSDB["time-series DB"]
    TSDB --> Grafana["Grafana 대시보드"]
    TSDB --> Alert["Alertmanager"]
    Alert --> Slack["Slack/PagerDuty"]
```

## 핵심 용어 정리

- **Metric**: 시간에 따른 *수치* (예: 요청 수, latency).
- **Counter**: *증가만* 하는 메트릭.
- **Gauge**: *오르내릴* 수 있는 메트릭.
- **Histogram**: *분포* 를 기록 (p50, p95, p99).
- **SLO**: 우리가 약속한 *서비스 수준 목표*.

## Before/After

**Before (로그만)**

```text
- 장애 시 *grep -i error* 로 찾기
- 추세 모름, *왜 느려졌는지* 모름
- 알림은 *고객 이메일*
```

**After (메트릭 + 알림)**

```python
from prometheus_client import Counter, Histogram

requests = Counter("http_requests_total", "Total", ["path", "status"])
latency = Histogram("http_latency_seconds", "Latency", ["path"])
```

## 실습: 모니터링 5단계

### 1단계 — 앱에 /metrics 노출

```python
from prometheus_client import make_asgi_app
app.mount("/metrics", make_asgi_app())
```

### 2단계 — Prometheus 설정

```yaml
scrape_configs:
  - job_name: myapp
    static_configs:
      - targets: ['myapp:8000']
```

### 3단계 — RED 메트릭 추적

```text
- Rate (요청률)
- Errors (에러율)
- Duration (응답 시간 p95)
```

### 4단계 — Grafana 대시보드

```text
- 패널 1: 요청률 (rate(http_requests_total[5m]))
- 패널 2: 에러율 (rate(http_requests_total{status=~"5.."}[5m]))
- 패널 3: p95 latency
```

### 5단계 — 의미 있는 알림

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  for: 5m
  annotations:
    summary: "5xx 에러율 1% 초과"
```

## 이 코드에서 주목할 점

- *5분 지속* 후 알림 — *순간 스파이크* 무시.
- *에러율* 은 *비율* 로. 절대값은 트래픽에 따라 다릅니다.
- *p95* 가 *평균* 보다 의미 있습니다.

## 자주 하는 실수 5가지

1. **알림이 *너무 많다*.** *알림 피로* 로 *진짜 알림* 무시.
2. ***평균 latency* 만 본다.** *꼬리(p99)* 가 진짜 문제.
3. **메트릭 *카디널리티 폭발*.** user_id 같은 *고유값* 을 라벨로 쓰면 안 됩니다.
4. **알림에 *대응 가이드 없음*.** 새벽 3시에 *어떻게 해야* 할까요?
5. **모니터링 자체가 *모니터링 안 됨*.** *Prometheus 다운* 을 외부에서 감시.

## 실무에서는 이렇게 쓰입니다

성숙한 팀은 *SLO 기반 알림* 을 씁니다. *에러 예산* 을 정의하고, *예산 소진 속도* 가 빠를 때만 알림이 울립니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *알림은 행동을 요구* 한다. 정보성이면 *대시보드* 에.
- *대시보드는 1분 안에* 답을 줘야 한다.
- *카디널리티* 는 비용. 라벨을 신중히.
- *SLO* 는 *팀과 비즈니스의 합의*.
- *모니터링도 코드 리뷰* 의 대상.

## 체크리스트

- [ ] *RED 메트릭* 이 모든 서비스에 있다.
- [ ] *p95 latency* 가 대시보드에 있다.
- [ ] *알림에 runbook 링크* 가 있다.
- [ ] *알림 노이즈* 가 측정되고 있다.

## 연습 문제

1. 본인 앱에 */metrics* 엔드포인트를 추가하세요.
2. *RED 대시보드* 를 Grafana에 만드세요.
3. *5xx 1% 5분 지속* 알림을 만드세요.

## 정리 및 다음 단계

모니터링은 *눈* 입니다. 다음 글에서는 *귀* 에 해당하는 *로그* 를 다룹니다.

- [DevOps란 무엇인가?](./01-what-is-devops.md)
- [CI 파이프라인](./02-ci-pipeline.md)
- [CD와 배포 전략](./03-cd-and-deployment.md)
- [환경 분리와 설정 관리](./04-environments-and-config.md)
- [Infrastructure as Code](./05-infrastructure-as-code.md)
- [컨테이너와 빌드](./06-containers-and-build.md)
- **모니터링과 알림 (현재 글)**
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)
## 참고 자료

- [Prometheus docs](https://prometheus.io/docs/)
- [Grafana docs](https://grafana.com/docs/)
- [Google SRE — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The RED Method (Tom Wilkie)](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)

Tags: DevOps, Monitoring, Prometheus, Alerting, SRE

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
