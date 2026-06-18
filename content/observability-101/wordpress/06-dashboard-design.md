---
series: observability-101
episode: 6
title: "바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Dashboard
  - Grafana
  - SRE
seo_description: 바이브코딩으로 만든 서비스의 운영 대시보드를 RED/USE 패턴으로 설계하는 방법과, AI에게 Grafana 패널을 요청하는 올바른 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 여섯 번째 글입니다. AI에게 "Grafana 대시보드 만들어줘"라고 하면 패널이 20개짜리 화려한 화면을 받을 수 있습니다. 하지만 장애가 났을 때 어디부터 봐야 할지 모르는 대시보드는 운영에 도움이 되지 않습니다.

---

패널이 많은 대시보드가 좋은 대시보드처럼 보일 때가 있습니다. AI에게 대시보드를 요청하면 CPU, 메모리, 네트워크, 요청 수, 에러율, 지연 시간, 큐 길이 등 모든 것을 한 화면에 넣어줍니다. 화면은 화려하지만, 새벽 3시 경보가 울렸을 때 어느 패널을 먼저 봐야 하는지 모르겠다는 말이 바로 나옵니다.

바이브코딩으로 만든 서비스의 대시보드는 특히 이 문제가 심합니다. 서비스를 빠르게 만들었기 때문에 "일단 다 모아두자"는 생각으로 패널을 쌓는 경향이 있습니다.

> "좋은 대시보드는 질문에 답합니다. AI가 만들어준 30개 패널 대시보드보다, 질문 4개에 정확히 답하는 6개 패널 대시보드가 운영에 훨씬 더 가치 있습니다."

## 이 글에서 다룰 문제

- 좋은 대시보드와 벽지 같은 대시보드는 무엇이 다를까요?
- RED와 USE 패턴은 각각 어떤 질문에 답할까요?
- 평균 대신 분포를 봐야 하는 이유는 무엇일까요?
- AI에게 Grafana 대시보드를 올바르게 요청하는 방법은 무엇일까요?
- 대시보드가 "벽지"가 되지 않으려면 어떻게 해야 할까요?

---

바이브코딩으로 만든 결제 서비스에 Grafana를 붙였습니다. AI가 만들어준 대시보드에는 CPU, 메모리, 디스크 I/O, 네트워크, 요청 수, 에러 수, p50, p95, p99 지연 시간, 각 엔드포인트별 지연 시간, DB 쿼리 시간, 외부 API 응답 시간 등 26개 패널이 있습니다.

그런데 결제 API가 느려졌다는 경보가 왔을 때, 26개 패널 중 어느 것부터 봐야 하는지 5초 안에 결정할 수 있나요? 그렇지 않다면 대시보드 설계를 바꿔야 합니다.

## RED 패턴: 사용자 관점의 서비스 건강도

RED는 바이브코딩 서비스의 첫 번째 대시보드 기준으로 가장 적합합니다.

| 항목 | 질문 | PromQL 예시 |
| --- | --- | --- |
| Rate (처리량) | 요청이 얼마나 들어오는가? | `sum(rate(http_requests_total[1m]))` |
| Errors (오류율) | 얼마나 실패하는가? | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` |
| Duration (지연 시간) | 얼마나 느린가? | `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))` |

이 세 가지만으로도 "서비스가 지금 건강한가"에 30초 안에 답할 수 있습니다.

## USE 패턴: 자원 관점의 인프라 건강도

| 항목 | 질문 | 예시 |
| --- | --- | --- |
| Utilization (사용률) | 자원을 얼마나 쓰는가? | CPU 사용률 % |
| Saturation (포화도) | 자원이 얼마나 가득 찼는가? | 큐 길이, 메모리 스왑 |
| Errors (오류) | 자원 관련 오류가 있는가? | DB 연결 실패 수 |

RED는 사용자 경험을 보고, USE는 그 원인이 될 수 있는 자원 상태를 봅니다. 첫 화면은 RED, 드릴다운은 USE로 분리하면 됩니다.

## 평균이 아닌 분포를 봐야 하는 이유

AI에게 "응답 시간 패널 만들어줘"라고 하면 평균을 그리는 경우가 많습니다. 하지만 평균은 느린 요청을 숨깁니다.

```text
[평균으로 본 응답 시간]
1000ms 평균 → "괜찮은데?"

[분포로 본 응답 시간]
p50: 100ms (대부분 요청)
p95: 800ms (상위 5% 요청)
p99: 3500ms (상위 1% 요청)
→ 1%의 사용자가 3.5초를 기다리고 있음!
```

Grafana 패널을 AI에게 요청할 때 "평균이 아닌 p95, p99 분위수를 보여줘"라고 명시하세요.

## Before / After: 대시보드 설계 개선

**Before (AI가 기본으로 만들어준 대시보드)**

```text
26개 패널, 모든 것이 한 화면에
→ CPU, 메모리, 네트워크, 요청 수, 에러 수,
  p50/p95/p99, 각 엔드포인트별 지연, DB, 외부 API...
→ 장애 시 어디부터 볼지 모름
→ 30초 안에 판단 불가
```

**After (질문 중심으로 재설계)**

```text
첫 화면 (4개 패널, RED + 포화도):
  - Request Rate (req/s)
  - Error Rate (%)
  - p95 Latency (ms)
  - In-Flight Requests (현재 처리 중)
→ 30초 안에 "장애인지, 성능 저하인지, 자원 포화인지" 판단

드릴다운 화면 (선택적):
  - 엔드포인트별 분석
  - DB 쿼리 시간
  - 외부 API 응답 시간
```

## Grafana 대시보드 JSON 예시

AI에게 이 JSON을 기반으로 대시보드를 만들어달라고 요청할 수 있습니다.

```json
{
  "title": "Service Health — checkout-api",
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "targets": [{"expr": "sum(rate(http_requests_total{service=\"checkout\"}[1m]))", "legendFormat": "req/s"}],
      "fieldConfig": {"defaults": {"unit": "reqps"}}
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "targets": [{"expr": "sum(rate(http_requests_total{service=\"checkout\",status=~\"5..\"}[1m])) / sum(rate(http_requests_total{service=\"checkout\"}[1m])) * 100", "legendFormat": "error %"}],
      "fieldConfig": {"defaults": {"unit": "percent", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "red", "value": 1}]}}}
    },
    {
      "title": "Latency p95",
      "type": "timeseries",
      "targets": [{"expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"checkout\"}[5m])))", "legendFormat": "p95"}],
      "fieldConfig": {"defaults": {"unit": "s", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "yellow", "value": 0.5}, {"color": "red", "value": 1.0}]}}}
    }
  ]
}
```

임계값 색상을 포함하면 수치가 기준선을 넘는 순간 빨간색으로 바뀝니다. 새벽 3시에 대시보드를 열었을 때 어떤 패널이 빨간지만 보면 즉시 판단할 수 있습니다.

## 배포 주석: AI 코드 배포 추적

바이브코딩에서 특히 중요한 것이 배포 주석입니다. AI가 만든 코드를 자주 배포할수록, "이 지연 증가가 오늘 배포 때문인가?"를 빠르게 확인할 수 있어야 합니다.

```yaml
# Grafana 주석 설정
annotations:
  - name: deploy
    datasource: prometheus
    expr: changes(build_info[1m]) > 0
```

이 설정을 추가하면 배포 시점이 그래프에 수직선으로 자동 표시됩니다.

## 자주 하는 실수

| 실수 | 문제 | 바이브코딩 맥락 |
| --- | --- | --- |
| 패널이 20개 이상 | 어디부터 볼지 모름 | AI가 요청 없이 모든 것을 추가 |
| 평균만 사용 | 느린 1% 사용자 경험 숨김 | AI가 avg() 기본 사용 |
| 임계값 없음 | 정상/위험 구분 불가 | AI가 threshold 생략 |
| 배포 주석 없음 | 배포 영향 판단 늦어짐 | 배포 시점 표시 필수 요청 필요 |
| 대시보드 이름 모호 | "시스템 모니터링"같은 포괄적 제목 | 질문 형태 제목 명시 필요 |

## AI 프롬프트 팁

```text
[Grafana 대시보드 요청]
"checkout-api 서비스의 운영 대시보드 만들어줘:
1. 첫 화면은 4-6개 패널로만 구성 (RED 패턴):
   - Request Rate (rate() 사용, 단위: req/s)
   - Error Rate (%, 임계값: 1% 주황, 5% 빨강)
   - p95 Latency (histogram_quantile, 임계값: 500ms 주황, 1s 빨강)
   - In-Flight Requests
2. 평균 대신 p95, p99 분위수 사용
3. 배포 시점 주석 자동 표시
4. $service, $env 변수로 여러 서비스/환경에서 재사용 가능하게
5. 패널 제목은 질문 형태로 작성"
```

## 운영 체크리스트

- [ ] RED 패턴의 기본 질의를 이해합니다.
- [ ] 첫 화면이 6개 이하 패널로 건강 요약 역할을 합니다.
- [ ] 모든 패널에 단위와 임계값이 있습니다.
- [ ] 배포 주석이 그래프에 표시됩니다.
- [ ] 평균이 아닌 p95/p99를 사용합니다.

## 처음 질문으로 돌아가기

- **좋은 대시보드와 벽지 같은 대시보드는 무엇이 다를까요?**
  좋은 대시보드는 30초 안에 "지금 서비스가 건강한가"에 답합니다. 패널이 많아도 행동으로 이어지지 않으면 벽지입니다.

- **RED와 USE 패턴은 각각 어떤 질문에 답할까요?**
  RED(Rate, Errors, Duration)는 사용자 관점의 서비스 건강도, USE(Utilization, Saturation, Errors)는 자원 관점의 인프라 상태입니다.

- **평균 대신 분포를 봐야 하는 이유는 무엇일까요?**
  평균은 느린 1% 사용자의 경험을 숨깁니다. p95, p99를 함께 보면 "대부분은 빠른데 일부가 매우 느린" 패턴을 발견할 수 있습니다.

---

## 정리

좋은 대시보드는 많이 보여주는 화면이 아니라 빠르게 판단하게 해주는 화면입니다. 바이브코딩으로 만든 서비스에 AI가 생성한 화려한 대시보드 대신, RED 패턴으로 6개 패널의 첫 화면을 만들면 장애 대응 속도가 달라집니다. 다음 글에서는 이 숫자들을 실제 행동으로 바꾸는 단계, 경보와 온콜을 다룹니다.

## 참고 자료

- [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html)
- [Tom Wilkie — RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [Google SRE — Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/best-practices/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스
- 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화
- 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅
- 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초
- **바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Dashboard, Grafana, SRE
