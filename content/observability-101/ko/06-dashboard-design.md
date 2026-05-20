---
series: observability-101
episode: 6
title: "Observability 101 (6/10): 대시보드 설계"
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
  - Dashboard
  - Grafana
  - SRE
  - Monitoring
seo_description: RED와 USE 패턴으로 장식이 아닌 질문에 답하는 대시보드를 설계하는 법을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (6/10): 대시보드 설계

패널이 많은 대시보드가 좋은 대시보드처럼 보일 때가 있습니다. 화면은 화려하고 숫자는 빽빽하지만, 막상 장애가 나면 어디부터 봐야 할지 모르겠다는 말이 바로 나옵니다. 흥미로운 패널이 많은 것과 운영에 도움이 되는 것은 전혀 다른 문제입니다.

좋은 대시보드는 질문에 답합니다. 첫 화면을 보는 사람에게 지금 서비스가 건강한지, 느려졌다면 어디를 더 파야 하는지, 배포 직후 흔들린 것인지까지 빠르게 알려 줘야 합니다.

이 글은 Observability 101 시리즈의 6번째 글입니다.

## 먼저 던지는 질문

- 좋은 대시보드와 벽지 같은 대시보드는 무엇이 다를까요?
- RED와 USE 패턴은 각각 어떤 질문에 답할까요?
- 평균 대신 분포를 봐야 하는 이유는 무엇일까요?

## 큰 그림

![Observability 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/06/06-01-concept-at-a-glance.ko.png)

*Observability 101 6장 흐름 개요*

이 그림에서는 대시보드 설계를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 대시보드 설계의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

운영 중에는 30개의 패널을 차례로 읽을 시간이 없습니다. 첫 화면에서 지금이 장애인지, 성능 저하인지, 자원 포화인지 감이 와야 다음 행동이 빨라집니다. 질문 없는 대시보드는 숫자를 보여 주지만 결정을 돕지 못합니다.

대시보드 설계는 시각화 기술보다 정보 압축 기술에 가깝습니다. 무엇을 넣을지보다 무엇을 빼야 하는지가 더 중요합니다. 첫 화면은 건강 요약이고, 깊은 분석은 드릴다운 화면으로 넘기는 편이 좋습니다.

## 한눈에 보는 구조

## 핵심 용어

- USE: 자원 관점에서 사용률, 포화도, 오류를 보는 방법입니다.
- RED: 요청 관점에서 요청 수, 오류, 지연 시간을 보는 방법입니다.
- 핵심 신호: 서비스 건강도를 읽는 네 축입니다.
- 히트맵: 시간에 따른 분포 변화를 보여 주는 그래프입니다.
- 주석: 배포처럼 시점 정보를 그래프 위에 표시하는 장치입니다.

## 바꾸기 전과 후

바꾸기 전에는 화면 하나에 패널을 계속 추가합니다. CPU도 있고 메모리도 있고 요청 수도 있고 느려 보이는 수치도 있지만, 막상 장애가 나면 어느 패널을 먼저 믿어야 할지 모르겠습니다.

바꾼 뒤에는 첫 화면이 건강 요약 역할을 합니다. 요청 수, 오류율, p95 지연 시간, 자원 포화도를 먼저 보고, 이상한 축이 보이면 그때 드릴다운 화면으로 내려갑니다. 숫자가 아니라 판단 순서가 생깁니다.

## 실습: 대시보드를 다섯 단계로 설계하기

### 1단계 — 요청 관점 패널 만들기

```promql
# Rate
sum(rate(http_requests_total[1m]))
# Errors
sum(rate(http_requests_total{status=~"5.."}[1m]))
# Duration p95
histogram_quantile(0.95, sum by (le) (rate(http_duration_seconds_bucket[5m])))
```

RED는 사용자 바깥에서 보이는 건강도입니다. 얼마나 많이 들어오는지, 얼마나 실패하는지, 얼마나 느린지를 먼저 보여 주기 때문에 첫 화면의 기본 뼈대가 됩니다.

### 2단계 — 자원 관점 패널 만들기

```promql
# CPU utilization
avg(rate(node_cpu_seconds_total{mode!="idle"}[1m]))
# Memory saturation
1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
```

USE는 서비스 안쪽의 상태를 보여 줍니다. 요청이 느린데 CPU와 메모리가 멀쩡하다면 다른 병목을 의심할 수 있고, 반대로 포화도가 올라간다면 원인 후보를 빠르게 좁힐 수 있습니다.

### 3단계 — 건강 요약 행 만들기

```text
Row: Service Health
  Panel 1: Latency (p50/p95/p99)
  Panel 2: Traffic (req/s)
  Panel 3: Errors (5xx/min)
  Panel 4: Saturation (queue depth)
```

첫 화면은 건강 요약이어야 합니다. 처음 보는 사람도 몇 초 안에 상태를 읽을 수 있어야 하므로, 가장 많이 보는 질문만 앞줄에 남기는 편이 좋습니다.

### 4단계 — 배포 시점 표시하기

```yaml
annotations:
  - name: deploy
    datasource: prometheus
    expr: changes(build_info[1m]) > 0
```

숫자만 보면 원인과 시점을 연결하기 어렵습니다. 배포, 구성 변경, 장애 조치 같은 이벤트를 주석으로 같이 표시하면 변화의 맥락이 훨씬 또렷해집니다.

### 5단계 — 환경 전환 변수 만들기

```text
$env = staging | production
$service = api | worker | scheduler
```

같은 대시보드 구조를 환경과 서비스별로 재사용할 수 있어야 유지 비용이 낮아집니다. 변수는 화면 수를 무한히 늘리지 않고도 비교와 전환을 가능하게 합니다.

## 첫 화면은 이렇게 검증합니다

좋은 대시보드는 패널이 예쁜지보다 첫 30초 안에 다음 행동을 정하게 해 주는지가 중요합니다. 배포 직후 checkout 지연이 올라간 상황을 예로 들면 아래 순서가 가장 실용적입니다.

```text
1) Latency p95/p99 패널에서 지연 상승 확인
2) Error 패널에서 같은 시점의 5xx 증가 여부 확인
3) Saturation 패널에서 큐 길이 또는 CPU 포화 여부 확인
4) Deploy annotation 과 시간 축을 맞춰 배포 영향인지 확인
```

```text
Expected output:
- 첫 행만 보고도 성능 저하인지 오류 급증인지 구분됩니다.
- 포화도 패널이 정상이라면 애플리케이션 내부나 외부 의존성을 더 의심하게 됩니다.
- 배포 주석이 겹치면 롤백 또는 설정 변경 검토가 빨라집니다.
```

## 이 코드에서 먼저 봐야 할 점

- RED는 바깥에서 본 사용자 경험이고, USE는 안쪽에서 본 자원 상태입니다.
- p95와 p99는 평균이 숨기는 긴 꼬리를 드러냅니다.
- 주석은 숫자의 원인을 읽게 해 주는 중요한 맥락입니다.

## 자주 하는 실수 다섯 가지

1. 한 화면에 패널을 너무 많이 넣습니다. 어디부터 봐야 할지 모르게 됩니다.
2. 모든 것을 평균으로만 봅니다. 분포가 사라집니다.
3. 단위 표기가 없습니다. 숫자의 의미가 흐려집니다.
4. 기준선과 임계값이 없습니다. 정상과 위험을 구분하기 어렵습니다.
5. 대시보드를 예쁘게 꾸미는 데 집중합니다. 질문에 답하지 못하는 패널이 남습니다.

## 실무에서는 이렇게 생각한다

가장 많이 보는 서비스 개요 화면은 보통 여섯 개 안팎의 패널로 끝납니다. 요청 수, 에러율, 지연 시간, 포화도 같은 핵심만 남기고, 나머지는 역할별 드릴다운 화면으로 분리합니다. 첫 화면에서 모든 것을 해결하려고 하면 오히려 아무 것도 읽히지 않습니다.

시니어 엔지니어는 대시보드 제목부터 질문처럼 씁니다. "API 건강 상태", "결제 경로 지연", "작업자 포화도"처럼 이름만 보고도 무엇을 답하려는 화면인지 드러나야 합니다.

## 체크리스트

- [ ] RED 패턴의 기본 질의를 이해합니다.
- [ ] USE 패턴이 무엇을 보는지 설명할 수 있습니다.
- [ ] 첫 화면이 건강 요약 역할을 합니다.
- [ ] 배포 주석이 함께 표시됩니다.

## 연습 문제

1. 하나의 서비스에 대해 RED 대시보드를 설계해 보세요.
2. 호스트 자원을 위한 USE 대시보드를 따로 그려 보세요.
3. 배포 시점을 주석으로 표시하는 규칙을 정해 보세요.

## 정리

좋은 대시보드는 많이 보여 주는 화면이 아니라 빨리 답하는 화면입니다. RED와 USE를 기준으로 첫 화면을 건강 요약으로 만들면 장애 대응 속도가 달라집니다. 다음 글에서는 숫자를 실제 행동으로 바꾸는 단계, 곧 경보와 온콜을 다루겠습니다.

## 처음 질문으로 돌아가기

- **좋은 대시보드와 벽지 같은 대시보드는 무엇이 다를까요?**
  - 본문의 기준은 대시보드 설계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **RED와 USE 패턴은 각각 어떤 질문에 답할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **평균 대신 분포를 봐야 하는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- [Observability 101 (4/10): 구조화된 로깅](./04-structured-logging.md)
- [Observability 101 (5/10): 분산 트레이싱 기초](./05-distributed-tracing.md)
- **대시보드 설계 (현재 글)**
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html)
- [Tom Wilkie — RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [Google SRE — Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Grafana panels and visualizations](https://grafana.com/docs/grafana/latest/panels-visualizations/)

Tags: Observability, Dashboard, Grafana, SRE, Monitoring
