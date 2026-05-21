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

대시보드 설계를 다루는 이번 장에서는 주요 개념과 실무 패턴을 봅니다. 시스템이 복잡해질수록 이 개념들이 어디에서 시작되고 어떤 결과를 만드는지 이해하는 것이 중요합니다.

> 대시보드 설계의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 왜 중요한가

운영 중에는 30개의 패널을 차례로 읽을 시간이 없습니다. 첫 화면에서 지금이 장애인지, 성능 저하인지, 자원 포화인지 감이 와야 다음 행동이 빨라집니다. 질문 없는 대시보드는 숫자를 보여 주지만 결정을 돕지 못합니다.

대시보드 설계는 시각화 기술보다 정보 압축 기술에 가깝습니다. 무엇을 넣을지보다 무엇을 빼야 하는지가 더 중요합니다. 첫 화면은 건강 요약이고, 깊은 분석은 드릴다운 화면으로 넘기는 편이 좋습니다.

### 대시보드 유형

대시보드는 목적에 따라 역할이 다릅니다. 운영팀, 분석팀, 경영진이 보는 화면은 질문도 시간 축도 다르기 때문에 하나의 대시보드로 모두를 만족시키기 어렵습니다. 아래 표는 대표적인 세 가지 유형입니다.

| 대시보드 유형 | 목적 | 갱신 주기 | 핵심 지표 수 |
|---|---|---|---|
| 운영 대시보드 | 실시간 건강 확인 | 1분 미만 | 4-6개 |
| 분석 대시보드 | 패턴 발견과 원인 분석 | 5-10분 | 10-20개 |
| 경영 대시보드 | 비즈니스 지표 요약 | 1시간 이상 | 3-5개 |

운영 대시보드는 골든 시그널과 SLI 중심으로 빠른 판단을 돕고, 분석 대시보드는 시간 범위가 길고 비교 차트가 많으며, 경영 대시보드는 숫자보다 추세와 목표 대비 달성률을 중심으로 보여 줍니다.
## 한눈에 보는 구조

대시보드는 미리 준비한 질문들에 대한 답을 보여주는 화면입니다. 팀별, 서비스별, 계층별로 다르게 설계하며, RED 방법론이 표준입니다.

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

### 레이아웃 원칙

첫 화면의 위아래 구조도 우연이 아니라 설계입니다. 사람이 왼쪽 위부터 읽기 때문에, 가장 중요한 정보는 상단에 두고 세부 분석은 하단으로 내려가야 합니다.

**골든 시그널은 상단에 배치**합니다. Latency, Traffic, Errors, Saturation처럼 서비스 건강 상태를 보여 주는 핵심 지표는 한눈에 들어와야 합니다. 색상, 임계값 라인, 시간 범위도 일관되게 유지하는 편이 좋습니다.

**드릴다운 패널은 하단에 배치**합니다. 특정 엔드포인트별 지연 시간, 데이터베이스 연결 수, 메모리 세그먼트 분포처럼 세부 분석이 필요한 패널은 첫 화면이 복잡해지지 않도록 하단 또는 접힌 행으로 분리합니다.

이 원칙이 있으면 새 팀원도 처음 대시보드를 열었을 때 어디부터 보면 되는지 바로 알게 됩니다.

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

### 나쁜 대시보드 징후 5가지

좋은 대시보드보다 나쁜 대시보드는 패턴이 더 명확합니다. 아래 다섯 가지가 보이면 설계 전체를 다시 봐야 할 신호입니다.

**1. 패널이 20개가 넘습니다.**
어디를 먼저 봐야 할지 모르게 됩니다. 첫 화면은 핵심 건강 요약으로 제한하고, 나머지는 역할별 드릴다운 화면으로 분리하는 편이 낫습니다.

**2. 평균만 봅니다.**
평균은 긴 꼬리를 숨깁니다. 대부분의 요청이 100ms인데 1%만 5초라면 평균은 150ms쯤 나오지만, 사용자는 5초 경험을 합니다. p95, p99와 같은 분포 지표를 함께 보는 것이 훨씬 현실적입니다.

**3. 색상이 일관되지 않습니다.**
같은 지표가 화면마다 다른 색으로 보이면 혼란스럽습니다. 시간 범위, 색상 팔레트, 단위 표기를 전사 표준으로 정하는 팀이 강합니다.

**4. 임계값이 없습니다.**
기준선이 없으면 "이 숫자가 좋은 건가요?"라는 질문이 반복됩니다. SLO 목표선, 용량 경고선, 과거 평균선을 패널에 함께 표시하면 판단이 빨라집니다.

**5. 대시보드 이름이 모호합니다.**
"운영 현황", "시스템 모니터링"처럼 너무 포괄적인 제목은 어떤 질문에 답하려는 화면인지 알기 어렵습니다. "결제 API 건강 상태", "작업자 포화도"처럼 질문이 명확한 제목이 훨씬 좋습니다.

**해결책**: 나쁜 대시보드는 리팩터링하거나 아카이브합니다. 오래된 화면을 계속 두면 어느 것이 진짜 운영 화면인지 혼란스러워집니다. 실제로 보는 대시보드만 남기고 나머지는 접근 통계를 보고 정리하는 편이 좋습니다.

## 이 코드에서 먼저 봐야 할 점

- RED는 바깥에서 본 사용자 경험이고, USE는 안쪽에서 본 자원 상태입니다.
- p95와 p99는 평균이 숨기는 긴 꼬리를 드러냅니다.
- 주석은 숫자의 원인을 읽게 해 주는 중요한 맥락입니다.

### 히트맵 사용법

히트맵은 시간에 따른 분포 변화를 보여 줍니다. 평균이나 p95만 보면 놓치는 패턴을 히트맵은 시각화합니다.

예를 들어 요청 지연 시간이 대부분 100ms 이하인데 오전 9시마다 5초대 요청이 튤는 패턴을 히트맵으로 보면 특정 시간대에 빨간색 띄가 보입니다. Grafana의 Histogram over time 패널을 쓰거나 Prometheus histogram 버킷을 그대로 시각화하면 됩니다.

```promql
sum by (le) (rate(http_duration_seconds_bucket[5m]))
```

이 쿼리는 각 bucket별로 요청이 얼마나 들어왔는지 보여 주므로, 시간 축으로 그리면 히트맵이 됩니다. 이를 통해 특정 시간대에만 느려지는 패턴을 훨씬 빨리 발견할 수 있습니다.

### 대시보드 세트 구성

하나의 서비스를 위해 보통 세 가지 대시보드를 만듭니다.

**1. Service Overview (서비스 개요)**

- 목적: 서비스가 건강한지 30초 안에 판단
- 패널: Latency p95/p99, Traffic, Errors 5xx, Saturation (4-6개)
- 갱신 빈도: 10초 또는 실시간
- 사용자: 온콜 엔지니어, 사고 대응 팀

**2. Request Analysis (요청 분석)**

- 목적: 특정 엔드포인트의 성능 패턴 분석
- 패널: 엔드포인트별 지연/처리량, method별 분포, status 분포 (10-15개)
- 갱신 빈도: 1분
- 사용자: 백엔드 개발자, 성능 튜닝 팀

**3. Infrastructure Health (인프라 건강)**

- 목적: 호스트, 컨테이너, 데이터베이스 자원 상태 확인
- 패널: CPU, Memory, Disk, Network, DB connections (10-20개)
- 갱신 빈도: 1분
- 사용자: SRE, 인프라 팀

세 대시보드는 각기 다른 질문에 답하므로, 하나로 합치지 말고 역할별로 분리하는 것이 올바른 설계입니다.
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

## Grafana 패널 JSON 예시

코드형 관리(GitOps)를 하려면 대시보드를 JSON으로 버전 관리하는 편이 좋습니다. 아래는 요청 지연 p95 패널의 최소 예시입니다.

```json
{
  "title": "Checkout Latency p95",
  "type": "timeseries",
  "datasource": {"type": "prometheus", "uid": "prom-main"},
  "targets": [
    {
      "expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route=\"/checkout\"}[5m])))",
      "legendFormat": "p95"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "s",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": null},
          {"color": "yellow", "value": 0.5},
          {"color": "red", "value": 1.0}
        ]
      }
    }
  }
}
```

패널 정의에서 임계값을 함께 관리하면, 사람마다 다른 감으로 수치를 해석하는 문제를 줄일 수 있습니다. 특히 온콜 상황에서는 초록/노랑/빨강 기준선이 빠른 판단에 직접 도움이 됩니다.

## RED 방법 실무 표

| 항목 | 질문 | 대표 질의 | 흔한 오해 |
| --- | --- | --- | --- |
| Rate | 요청량이 변했는가 | `sum(rate(http_requests_total[1m]))` | 총합만 보면 경로 편차를 놓칩니다. |
| Errors | 실패가 늘었는가 | `sum(rate(http_requests_total{status=~"5.."}[5m]))` | 4xx를 무조건 제외하면 사용자 체감 오류를 놓칠 수 있습니다. |
| Duration | 느려졌는가 | `histogram_quantile(0.95, ...)` | 평균만 보면 꼬리 지연을 숨깁니다. |

RED는 "사용자 관점"입니다. CPU, 메모리, 디스크는 원인 탐색에 유용하지만, 사용자 품질 자체를 직접 나타내지는 않습니다. 그래서 첫 화면은 RED 중심, 두 번째 화면은 USE 중심으로 분리하는 구성이 실무에서 안정적입니다.

## 대시보드 안티패턴과 개선책

| 안티패턴 | 문제 | 개선 방법 |
| --- | --- | --- |
| 한 화면에 30개 패널 | 초기 대응 경로가 사라집니다. | 첫 화면을 4-6개 요약 패널로 축소합니다. |
| 단위 혼합(ms, s, %) | 해석 실수가 늘어납니다. | 패널 단위를 강제하고 템플릿화합니다. |
| 시간 범위 제각각 | 비교가 어려워집니다. | 대시보드 기본 범위를 통일합니다. |
| 색상 의미 불일치 | 위험 신호 인지가 느려집니다. | 임계값 색상 정책을 공통화합니다. |
| 주석 없음 | 배포 영향 판단이 늦어집니다. | 배포/장애 조치 주석을 자동 입력합니다. |

운영 대시보드는 디자인 산출물이 아니라 의사결정 인터페이스입니다. 지표 추가 요청이 들어올 때마다 "이 패널이 어떤 행동을 바꾸는가"를 묻는 습관을 팀 표준으로 두면 대시보드가 벽지가 되는 일을 막을 수 있습니다.

## Grafana 대시보드 Provisioning

Grafana는 대시보드를 YAML로 선언하고 Git으로 버전 관리할 수 있습니다. 아래는 provisioning 설정 예시입니다.

```yaml
# /etc/grafana/provisioning/dashboards/default.yaml
apiVersion: 1
providers:
  - name: "default"
    orgId: 1
    folder: "Operations"
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

이 설정을 두면 `/var/lib/grafana/dashboards/` 디렉터리에 JSON 파일을 넣는 것만으로 대시보드가 자동으로 반영됩니다. CI/CD 파이프라인에서 대시보드 JSON을 배포하면 수동 조작 없이 전체 환경이 동기화됩니다.

## 완성된 4패널 대시보드 JSON

아래는 운영 대시보드의 첫 행(Service Health)을 구성하는 4개 패널 JSON 예시입니다.

```json
{
  "title": "Service Health",
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
      "targets": [{
        "expr": "sum(rate(http_requests_total{service=\"$service\"}[1m]))",
        "legendFormat": "req/s"
      }],
      "fieldConfig": {"defaults": {"unit": "reqps"}}
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
      "targets": [{
        "expr": "sum(rate(http_requests_total{service=\"$service\",status=~\"5..\"}[1m])) / sum(rate(http_requests_total{service=\"$service\"}[1m])) * 100",
        "legendFormat": "error %"
      }],
      "fieldConfig": {"defaults": {"unit": "percent", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "red", "value": 1}]}}}
    },
    {
      "title": "Latency p95",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
      "targets": [{
        "expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])))",
        "legendFormat": "p95"
      }],
      "fieldConfig": {"defaults": {"unit": "s", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "yellow", "value": 0.5}, {"color": "red", "value": 1.0}]}}}
    },
    {
      "title": "In-Flight Requests",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
      "targets": [{
        "expr": "sum(http_requests_in_flight{service=\"$service\"})",
        "legendFormat": "in-flight"
      }],
      "fieldConfig": {"defaults": {"unit": "short", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "yellow", "value": 100}, {"color": "red", "value": 500}]}}}
    }
  ],
  "templating": {
    "list": [
      {"name": "service", "type": "query", "query": "label_values(http_requests_total, service)"},
      {"name": "env", "type": "custom", "query": "staging,production"}
    ]
  },
  "annotations": {
    "list": [{
      "name": "Deployments",
      "datasource": "prometheus",
      "expr": "changes(build_info{service=\"$service\"}[1m]) > 0",
      "tagKeys": "service",
      "titleFormat": "Deploy"
    }]
  }
}
```

이 JSON을 `/var/lib/grafana/dashboards/service-health.json`으로 저장하면 Grafana가 자동으로 로드합니다. `$service`와 `$env` 변수로 서비스별/환경별 전환이 가능하고, 배포 주석이 자동 표시됩니다.

## 대시보드 리뷰 체크리스트

대시보드를 새로 만들거나 리팩터링할 때 아래 항목을 점검하면 벽지화를 막을 수 있습니다.

| # | 점검 항목 | 통과 기준 |
| --- | --- | --- |
| 1 | 첫 화면 패널 수 ≤ 6 | 초과 시 드릴다운으로 분리 |
| 2 | 모든 패널에 단위 표기 | s, ms, %, reqps 등 명시 |
| 3 | 임계값 라인 존재 | SLO 목표선 또는 용량 경고선 |
| 4 | 배포 주석 연동 | 배포 시점이 자동 표시되는지 |
| 5 | 변수로 환경/서비스 전환 가능 | 대시보드 복제 없이 재사용 |
| 6 | 대시보드 제목이 질문 형태 | "시스템 모니터링"이 아닌 "결제 API 건강 상태" |
| 7 | 색상 정칅 일관성 | 초록=정상, 노랑=주의, 빨강=위험 |
| 8 | 시간 범위 기본값 통일 | 모든 패널이 같은 기간을 보여줌 |
## 처음 질문으로 돌아가기

- **좋은 대시보드와 벽지 같은 대시보드는 무엇이 다를까요?**
  - 좋은 대시보드는 질문에 답합니다. "지금 서비스가 건강한가?", "느려졌다면 어디를 파야 하는가?", "배포 직후에 문제가 생겼는가?"에 30초 안에 답할 수 있으면 좋은 대시보드입니다. 벽지 대시보드는 숫자는 많지만 행동을 유도하지 못합니다.
- **RED와 USE 패턴은 각각 어떤 질문에 답할까요?**
  - RED는 "사용자가 겪는 품질이 어떤가?"에 답합니다. 요청량(Rate), 실패율(Errors), 지연(Duration). USE는 "시스템 내부 자원이 어떤 상태인가?"에 답합니다. 사용률(Utilization), 포화도(Saturation), 오류(Errors). 첫 화면은 RED, 두 번째 화면은 USE로 분리하는 것이 실무 표준입니다.
- **평균 대신 분포를 봐야 하는 이유는 무엇일까요?**
  - 평균 100ms인 서비스에서 1% 요청이 5초라면 평균은 150ms로 보이지만 사용자 1%는 5초를 겪습니다. p95/p99 같은 분위수와 히트맵을 함께 보면 이 긴 꼬리를 놓치지 않습니다.

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
- [예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

Tags: Observability, Dashboard, Grafana, SRE, Monitoring
