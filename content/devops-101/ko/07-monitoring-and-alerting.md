---
series: devops-101
episode: 7
title: 모니터링과 알림
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - Monitoring
  - Prometheus
  - Alerting
  - SRE
seo_description: Prometheus와 Grafana를 바탕으로 의미 있는 알림을 설계하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# 모니터링과 알림

이 글은 DevOps 101 시리즈의 일곱 번째 글입니다.

## 이 글에서 다룰 문제

- 모니터링의 세 신호인 로그, 메트릭, 트레이스는 어떻게 역할이 다를까요?
- Prometheus와 Grafana는 어떤 흐름으로 함께 동작할까요?
- RED와 USE 같은 메트릭 패턴은 왜 운영에서 자주 언급될까요?
- 정말 행동이 필요한 알림은 어떻게 설계해야 할까요?
- 모니터링을 붙이고도 팀이 자주 빠지는 함정은 무엇일까요?

> **멘탈 모델**: 모니터링의 목적은 예쁜 대시보드를 만드는 데 있지 않습니다. 고객보다 먼저 문제를 감지하고, 장애가 나면 어디서부터 좁혀야 하는지 빠르게 판단할 수 있게 만드는 데 있습니다.

## 왜 중요한가

장애는 언젠가 반드시 옵니다. 차이는 장애가 오느냐가 아니라, 얼마나 빨리 알아차리고 얼마나 빨리 범위를 좁힐 수 있느냐입니다. 모니터링은 이 두 속도를 동시에 올리는 도구입니다.

로그만 읽는 운영은 이미 한계가 있습니다. 시스템이 분산될수록 상태를 수치로 요약하고 추세를 보는 능력이 더 중요해집니다.

> 모니터링 없이 운영하는 것은 눈을 감고 운전하는 것과 비슷합니다.

## 한눈에 보는 개념

![한눈에 보는 개념](../../../assets/devops-101/07/07-01-diagram.ko.png)

*한눈에 보는 개념*

애플리케이션이 메트릭을 노출하고, Prometheus가 이를 수집하고, Grafana가 시각화하며, Alertmanager가 기준을 넘는 이상 신호를 알립니다. 좋은 운영은 이 흐름이 팀의 대응 절차와 자연스럽게 연결될 때 만들어집니다.

## 핵심 용어

- **Metric**: 시간에 따라 변하는 수치입니다.
- **Counter**: 오직 증가만 하는 메트릭입니다.
- **Gauge**: 증가와 감소가 모두 가능한 메트릭입니다.
- **Histogram**: 응답 시간 같은 분포를 기록하는 메트릭입니다.
- **SLO**: 팀이 서비스 품질 목표로 약속하는 수준입니다.

이 용어는 개념 설명보다 운영 질문에 더 직접적으로 쓰입니다. 예를 들어 응답 시간이 느려졌을 때 평균이 아니라 p95를 보는 이유도 histogram과 tail latency 개념을 이해해야 자연스럽습니다.

## Before/After

**Before (logs only)**

```text
- During an incident, you *grep -i error*
- No trends, no idea *why it slowed down*
- Alerts arrive as *customer emails*
```

이 상태에서는 문제를 발견하는 주체가 팀이 아니라 고객이 됩니다. 그리고 장애가 나도 현재 상태만 볼 수 있을 뿐, 10분 전부터 어떤 추세가 쌓였는지는 알기 어렵습니다.

**After (metrics + alerts)**

```python
from prometheus_client import Counter, Histogram

requests = Counter("http_requests_total", "Total", ["path", "status"])
latency = Histogram("http_latency_seconds", "Latency", ["path"])
```

메트릭이 있으면 장애를 "느리다"처럼 모호하게 말하지 않고, 에러율과 요청률, p95 지연시간 같은 수치로 좁힐 수 있습니다.

## 모니터링을 위한 5단계

### 1단계 - 애플리케이션에 /metrics 노출

모니터링은 애플리케이션이 상태를 읽을 수 있게 노출하는 것에서 시작합니다. 수집 시스템이 아무리 좋아도 원천 신호가 없으면 관측은 불가능합니다.

```python
from prometheus_client import make_asgi_app
app.mount("/metrics", make_asgi_app())
```

### 2단계 - Prometheus 수집 설정

메트릭을 노출했다면 이제 누가 언제 긁어 갈지 정해야 합니다. 수집 주기와 대상 정의가 모니터링 파이프라인의 기본입니다.

```yaml
scrape_configs:
  - job_name: myapp
    static_configs:
      - targets: ['myapp:8000']
```

### 3단계 - RED 메트릭 추적

처음부터 수백 개 지표를 붙일 필요는 없습니다. 요청률, 에러율, 응답 시간 세 가지만 잘 봐도 대부분의 웹 서비스 상태를 빠르게 읽을 수 있습니다.

```text
- Rate (request rate)
- Errors (error ratio)
- Duration (response time p95)
```

### 4단계 - Grafana 대시보드 구성

대시보드는 예쁘게 만드는 것이 목적이 아닙니다. 1분 안에 서비스 상태를 판단할 수 있어야 합니다. 그래서 핵심 지표가 가장 먼저 보여야 합니다.

```text
- Panel 1: rate(http_requests_total[5m])
- Panel 2: rate(http_requests_total{status=~"5.."}[5m])
- Panel 3: p95 latency
```

### 5단계 - 의미 있는 알림 설계

알림은 수치가 아니라 행동을 유발해야 합니다. 잠깐 튀는 스파이크보다 지속되는 이상 징후에 반응하도록 설계해야 on-call 피로도를 줄일 수 있습니다.

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  for: 5m
  annotations:
    summary: "5xx error rate above 1%"
```

## 이 코드에서 먼저 봐야 할 점

- 5분 지속 조건은 순간적인 스파이크를 무시하게 해 줍니다.
- 에러율은 절대값보다 비율로 보는 편이 훨씬 의미 있습니다.
- 평균보다 p95가 사용자 체감에 더 가까운 신호입니다.

좋은 알림은 문제를 더 많이 말해 주는 알림이 아니라, 새벽 3시에 울렸을 때 정말 행동해야 하는 알림입니다.

## 자주 하는 실수 5가지

1. **알림을 너무 많이 만드는 실수**입니다. 알림 피로가 쌓이면 중요한 알림도 놓칩니다.
2. **평균 지연시간만 보는 실수**입니다. 실제 사용자 불만은 대개 tail latency에서 드러납니다.
3. **라벨 카디널리티를 폭발시키는 실수**입니다. `user_id` 같은 값은 메트릭 저장 비용을 급격히 키웁니다.
4. **알림에 대응 가이드가 없는 실수**입니다. 알림만 울리고 무엇을 해야 할지 모르면 운영은 멈춥니다.
5. **모니터링 시스템 자체를 감시하지 않는 실수**입니다. Prometheus가 죽으면 나머지 신호도 함께 사라집니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 SLO 기반 알림을 사용합니다. 단순 임계치보다 에러 예산 소진 속도를 기준으로 삼아, 정말 서비스 품질이 빠르게 악화될 때만 강하게 반응합니다.

작은 팀이라면 먼저 RED 지표, p95, runbook 링크가 있는 알림부터 갖추는 편이 좋습니다. 이 세 가지가 대응 속도를 가장 크게 바꿉니다.

## 시니어 엔지니어는 이렇게 봅니다

- 알림은 반드시 행동을 요구해야 합니다.
- 대시보드는 1분 안에 답을 줘야 합니다.
- 카디널리티는 곧 비용입니다.
- SLO는 팀과 비즈니스 사이의 약속입니다.
- 모니터링도 코드 리뷰 대상입니다.

## 체크리스트

- [ ] 모든 서비스에 RED 메트릭이 있습니다.
- [ ] p95 지연시간이 대시보드에 있습니다.
- [ ] 알림에 runbook 링크가 포함됩니다.
- [ ] 알림 노이즈를 측정합니다.

## 연습 문제

1. 애플리케이션에 /metrics 엔드포인트를 추가해 보세요.
2. Grafana에서 RED 대시보드를 만들어 보세요.
3. 5분 지속 5xx 1% 초과 알림을 하나 설계해 보세요.

## 정리 및 다음 단계

모니터링은 운영의 눈입니다. 다음 글에서는 눈으로 본 현상을 더 깊게 추적하게 해 주는 로그 수집과 분석을 다룹니다.

<!-- toc:begin -->
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
<!-- toc:end -->

## 참고 자료

- [Prometheus docs](https://prometheus.io/docs/)
- [Grafana docs](https://grafana.com/docs/)
- [Google SRE — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The RED Method (Tom Wilkie)](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)

Tags: DevOps, Monitoring, Prometheus, Alerting, SRE
