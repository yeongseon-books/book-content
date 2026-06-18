---
episode: 5
language: ko
series: sre-101
title: "바이브코딩을 위한 SRE 기초 (5/10): Monitoring"
tags:
- SRE
- 바이브코딩
- Monitoring
- Metrics
- Alerting
- Observability
targets:
  wordpress: true
---

# 바이브코딩을 위한 SRE 기초 (5/10): Monitoring

이 글은 **바이브코딩을 위한 SRE 기초** 시리즈의 다섯 번째 글입니다. AI가 만든 서비스가 사용자에게 닿는 순간부터 무슨 일이 일어나고 있는지 알 수 없다면, 장애는 항상 사용자가 먼저 발견하게 됩니다. 모니터링은 "지금 움직여야 하는가"를 바로 판단하게 만드는 측정 설계입니다.

---

바이브코딩으로 서비스를 만들고 배포한 뒤 며칠이 지나면 이런 메시지를 받을 때가 있습니다.

"API가 갑자기 느려졌어요. 30분째 응답이 5초씩 걸려요." 알림을 받기 전에 사용자가 먼저 발견한 장애입니다.

AI 도구로 빠르게 서비스를 만들다 보면 모니터링을 나중으로 미루는 경우가 많습니다. "일단 기능을 완성하고, 운영은 그다음에 생각하자"는 생각입니다. 그런데 AI가 생성한 코드는 에러 처리나 타임아웃이 빠져 있는 경우가 많고, 예상치 못한 트래픽 패턴에서 이상하게 동작할 수 있습니다. 이런 문제를 사용자보다 먼저 발견하려면 모니터링이 필요합니다.

좋은 모니터링은 데이터를 많이 쌓는 체계가 아닙니다. 지금 움직여야 하는지 바로 판단하게 만드는 체계입니다. 알림이 울렸는데 누구도 무엇을 해야 할지 모른다면, 그 신호는 이미 역할을 잃은 상태입니다.

> 모니터링은 많이 보는 기술이 아니라, 필요한 순간에 바로 행동하게 만드는 측정 설계입니다.

## 이 글에서 다룰 문제

- monitoring은 단순 수집과 어떻게 다를까요?
- latency, traffic, errors, saturation은 왜 함께 봐야 할까요?
- 메트릭과 로그는 각각 어떤 질문에 답할까요?
- 바이브코딩 서비스에서 모니터링을 처음 설정할 때 어디서 시작해야 할까요?
- AI가 생성한 코드에 모니터링을 추가하는 효과적인 방법은 무엇일까요?

## 골든 시그널: 네 가지 핵심 신호

Google SRE가 제안한 네 가지 골든 시그널은 어떤 서비스에서도 시스템 상태를 빠르게 읽는 공통 언어입니다.

**Latency(지연 시간)**: 요청이 얼마나 빠르게 처리되는가. 평균보다 p95, p99가 실제 사용자 경험에 더 가깝습니다.

**Traffic(트래픽)**: 시스템에 얼마나 많은 요청이 들어오는가. 갑자기 줄어드는 것도 문제 신호일 수 있습니다.

**Errors(오류)**: 실패한 요청이 얼마나 되는가. 절대 수보다 비율로 봐야 트래픽 증가와 구분됩니다.

**Saturation(포화도)**: 자원이 한계에 얼마나 가까운가. CPU, 메모리, DB 커넥션 풀 사용률이 대표적입니다.

```python
# Prometheus 메트릭 예시 (바이브코딩 서비스에 추가)
from prometheus_client import Counter, Histogram, Gauge

# Traffic: 요청 수 카운터
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Latency: 지연 시간 히스토그램
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['endpoint']
)

# Saturation: 동시 접속 수 게이지
active_connections = Gauge(
    'active_connections',
    'Currently active connections'
)
```

## AI 생성 코드에 모니터링 추가하기

AI가 생성한 Flask/FastAPI 코드에 모니터링을 추가하는 방법입니다. AI에게 다음과 같이 요청하면 됩니다.

"이 FastAPI 앱에 prometheus_client를 사용해서 모든 엔드포인트의 요청 수, 지연 시간, 에러율을 자동으로 측정하는 미들웨어를 추가해줘. /metrics 엔드포인트도 노출해줘."

구조화 로그도 중요합니다. JSON 형식으로 로그를 남기면 나중에 검색과 분석이 훨씬 쉬워집니다.

```python
import json
import logging
from datetime import datetime

def structured_log(level, message, **kwargs):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "service": "my-vibe-service",
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

# 사용 예시
structured_log("error", "Payment failed",
    user_id="user_123",
    amount=50000,
    error_type="timeout",
    endpoint="/api/payments"
)
```

## 알림 설계: 사람을 깨울 가치가 있는 신호만

알림이 너무 많으면 중요한 신호가 묻힙니다. 알림 설계의 핵심 질문은 "이 신호가 울렸을 때 지금 바로 사람이 움직여야 하는가?"입니다.

| 알림 유형 | 조건 | 채널 |
| --- | --- | --- |
| Page (즉시 대응) | 에러율 > 1%, p95 지연 > 500ms, 포화도 > 90% | PagerDuty, 전화 |
| Warning (업무 시간 내) | 에러율 > 0.5%, p95 지연 > 300ms, 포화도 > 70% | Slack #alerts |
| Info (참고용) | 트래픽 급증, 배포 완료 | Slack #monitoring |

CPU > 80% 같은 증상 기반 알림보다, 에러 버짓 burn rate가 14.4배를 초과할 때 알림을 거는 SLO 기반 알림이 오탐이 적고 사용자 영향과 직결됩니다.

## Before / After: 모니터링 도입 전후

| 상황 | 모니터링 전 | 모니터링 후 |
| --- | --- | --- |
| 장애 발견 | 사용자 신고 후 20-30분 뒤 파악 | 2분 내 알림으로 자체 발견 |
| 원인 파악 | 로그 뒤지며 30분~1시간 소요 | 메트릭 + 로그 연결로 5분 내 파악 |
| 배포 영향 파악 | 배포 후 사용자 불만 올 때까지 대기 | 배포 후 5분 내 지표 변화 확인 |
| 용량 문제 | 서비스 다운된 후 파악 | 포화도 80% 도달 시 사전 경고 |
| 팀 상태 파악 | "잘 돌아가는 것 같아요" | "가용성 99.8%, p99 650ms" |

## 바이브코딩에서 자주 하는 실수

| 실수 | 왜 문제인가 | 개선 방법 |
| --- | --- | --- |
| 모든 지표에 알림 설정 | 알림 피로로 중요한 신호를 무시하게 됨 | 즉시 행동이 필요한 조건에만 page 알림 |
| 평균 지연 시간만 봄 | 느린 사용자 경험을 숨김 | p95, p99 분위수를 항상 함께 확인 |
| 로그를 plain text로 출력 | 검색과 분석이 어려움 | JSON 구조화 로그로 전환 |
| 서버 메트릭만 수집 | 사용자 경험과 거리가 멈 | HTTP 성공률, 응답 시간 같은 사용자 경험 지표 우선 |
| 대시보드가 너무 많음 | 무엇을 봐야 할지 모르게 됨 | 골든 시그널 4가지 기반의 단순한 대시보드 |

## AI 팁: 모니터링 코드 요청하기

**메트릭 추가 요청**: "이 Python Flask 앱에 prometheus_client로 요청 수, 지연 시간(히스토그램), 에러율을 측정하는 코드를 추가해줘. 엔드포인트별로 레이블을 분리해줘"

**알림 규칙 요청**: "5분 윈도우에서 HTTP 5xx 에러율이 1%를 초과하면 Slack으로 알림을 보내는 Prometheus alerting rule YAML을 만들어줘. runbook URL도 포함해줘"

**대시보드 요청**: "Grafana에서 골든 시그널(latency p95/p99, error rate, saturation, throughput)을 보여주는 대시보드 JSON을 만들어줘"

## 운영 체크리스트

- [ ] latency, traffic, errors, saturation을 모두 본다.
- [ ] 페이지 알림은 즉시 행동이 필요한 경우에만 울린다.
- [ ] 평균 외에 분위수 지표를 함께 본다.
- [ ] 대시보드는 질문 순서에 맞춰 구성되어 있다.
- [ ] 알림 피로를 정기적으로 측정하고 정리한다.

## 처음 질문으로 돌아가기

- **monitoring은 단순 수집과 어떻게 다를까요?**
  - 단순 수집은 데이터를 모으는 것이고, 모니터링은 그 데이터로 "지금 움직여야 하는가"를 즉시 판단하게 만드는 체계입니다. 알림이 울렸을 때 누구도 무엇을 해야 할지 모른다면 그건 수집이지 모니터링이 아닙니다.
- **바이브코딩 서비스에서 모니터링을 처음 설정할 때 어디서 시작해야 할까요?**
  - HTTP 성공률 (errors)과 p95 지연 시간 (latency) 두 가지부터 시작하세요. 이 두 지표가 보이면 사용자가 실제로 겪는 경험을 측정할 수 있습니다. traffic과 saturation은 그다음에 추가합니다.
- **AI가 생성한 코드에 모니터링을 추가하는 효과적인 방법은 무엇일까요?**
  - AI에게 "이 코드에 Prometheus 메트릭과 구조화 JSON 로그를 추가해줘"라고 요청하면 됩니다. 미들웨어 패턴을 쓰면 모든 엔드포인트에 자동으로 적용할 수 있습니다.

## 정리

모니터링은 데이터를 많이 쌓는 일이 아니라, 골든 시그널을 기반으로 지금 바로 행동할 수 있게 만드는 측정 설계입니다. 바이브코딩으로 만든 서비스도 처음부터 네 가지 핵심 신호를 측정하면, 사용자보다 먼저 문제를 발견할 수 있습니다.

다음 글에서는 인시던트 대응을 다룹니다. 장애가 실제로 발생했을 때 누가 어떤 순서로 움직이고, 어떻게 빠르게 복구하는지 정리합니다.

## 참고 자료

- [Monitoring Distributed Systems - Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Practical Alerting - Google SRE Book](https://sre.google/sre-book/practical-alerting/)
- [USE Method - Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 SRE 기초 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [바이브코딩을 위한 SRE 기초 (2/10): Reliability](./02-reliability.md)
- [바이브코딩을 위한 SRE 기초 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [바이브코딩을 위한 SRE 기초 (4/10): Error Budget](./04-error-budget.md)
- **바이브코딩을 위한 SRE 기초 (5/10): Monitoring (현재 글)**
- [바이브코딩을 위한 SRE 기초 (6/10): Incident Response](./06-incident-response.md)
- [바이브코딩을 위한 SRE 기초 (7/10): Postmortem](./07-postmortem.md)
- [바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기](./08-reducing-toil.md)
- [바이브코딩을 위한 SRE 기초 (9/10): Capacity Planning](./09-capacity-planning.md)
- [바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템 만들기](./10-building-operable-systems.md)

<!-- toc:end -->

Tags: SRE, 바이브코딩, Monitoring, Metrics, Alerting, Observability
