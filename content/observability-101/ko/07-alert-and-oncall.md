---
series: observability-101
episode: 7
title: "Observability 101 (7/10): 경보와 온콜"
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
  - Alerting
  - SRE
  - OnCall
  - Monitoring
seo_description: 새벽 호출을 감수할 만한 경보의 조건과 경보 피로를 줄이는 온콜 운영 원칙을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (7/10): 경보와 온콜

경보는 많이 울릴수록 안전해질 것 같지만, 실제로는 그 반대가 되기 쉽습니다. 하루에 수십 번 울리는 경보는 결국 아무도 믿지 않게 됩니다. 정말 위험한 상황이 와도 "또 오경보겠지"라는 반응이 먼저 나오면 이미 설계가 잘못된 것입니다.

온콜은 도구 문제가 아니라 사람의 집중력과 수면을 다루는 운영 체계입니다. 그래서 좋은 경보 설계는 기술적 정확성만큼이나 인간 비용을 함께 고려해야 합니다.

이 글은 Observability 101 시리즈의 7번째 글입니다.

![Observability 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/07/07-01-concept-at-a-glance.ko.png)
*Observability 101 7장 흐름 개요*
> 경보와 온콜의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 먼저 던지는 질문

- 새벽에 사람을 깨울 만한 경보는 어떤 조건을 가져야 할까요?
- 경보 피로는 왜 생기고 어떻게 줄일 수 있을까요?
- 증상 경보와 원인 경보는 어떻게 다를까요?

## 왜 중요한가

온콜의 비용은 숫자로만 계산되지 않습니다. 자주 울리는 경보는 수면을 깨고, 집중력을 갉아먹고, 팀의 신뢰를 떨어뜨립니다. 그래서 경보 하나를 추가하는 일은 알림 한 줄을 더 만드는 것이 아니라 운영 비용을 늘리는 결정입니다.

좋은 경보 설계는 반대로 팀을 보호합니다. 사용자 영향이 분명한 문제만 즉시 깨우고, 나머지는 업무 시간 안에 처리할 수 있게 나누면 사람의 에너지를 중요한 문제에 집중시킬 수 있습니다.

### 알림 심각도 기준

알림은 모두 같은 급으로 취급할 수 없습니다. 즉시 대응해야 하는 것과 내일 아침에 처리해도 되는 것을 나누는 기준이 있어야 온콜이 오래 갑니다.

| 심각도 | 응답 시간 | 에스커레이션 | 예시 |
|---|---|---|---|
| P1 (Critical) | 15분 이내 | 30분후 팀장, 1시간후 경영진 | 결제 서비스 중단, 데이터 유출 |
| P2 (High) | 30분 이내 | 1시간후 팀장 | 특정 API 5xx 5% 이상 |
| P3 (Medium) | 4시간 이내 | 없음 | 디스크 사용률 80% |
| P4 (Low) | 업무 시간 내 | 없음 | 로그 용량 증가 추세 |

P1과 P2만 새벽에 사람을 깨우고, P3은 슬랙 채널로 보내고, P4는 일일 티켓으로 발급합니다. 이 기준은 팀의 업무 특성과 SLO에 따라 조정하지만, 기본 틀은 사용자 영향과 비즈니스 손실을 기준으로 삼습니다.
## 한눈에 보는 구조

경보의 목표는 인간이 즉시 조치해야 할 진짜 문제만 알리는 것입니다. 위양성이 많으면 팀이 경보를 무시하게 되므로, 신뢰 가능한 기준 설정이 중요합니다.

## 핵심 용어

- 경보 규칙: 조건과 지속 시간을 함께 정의한 규칙입니다.
- 심각도: 즉시 호출할지, 업무 시간 티켓으로 보낼지 구분하는 기준입니다.
- 라우팅: 어떤 팀과 채널로 보낼지 정하는 규칙입니다.
- 일시 중지: 유지보수나 이미 처리 중인 상황에서 잠시 억제하는 기능입니다.
- 런북: 경보를 받았을 때 처음 무엇을 해야 하는지 적어 둔 대응 문서입니다.

## 바꾸기 전과 후

바꾸기 전에는 하루에 수십 개 경보가 옵니다. 대부분은 잠깐 튀었다 사라지거나, 이미 알고 있던 원인 신호라서 아무도 적극적으로 보지 않습니다. 그러다 진짜 장애도 같은 소리 속에 섞입니다.

바꾼 뒤에는 새벽 호출용 경보가 극단적으로 줄어듭니다. 대신 사용자 영향이 큰 증상 경보만 남고, 나머지는 티켓이나 채팅으로 분리됩니다. 경보 수는 줄어들지만 신뢰도는 높아집니다.

## 실습: 경보 체계를 다섯 단계로 만들기

### 1단계 — 기본 경보 규칙 쓰기

```yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m]))
              / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "5xx > 5% for 10m"
          runbook: "https://wiki/runbook/api-error"
```

좋은 첫 경보는 사용자 영향과 연결된 증상 경보입니다. 에러율처럼 바로 체감되는 지표가 특히 적합합니다.

### 2단계 — 지속 시간 넣기

```yaml
for: 10m   # too short and noise explodes
```

지속 시간이 없으면 잠깐 튄 수치에도 경보가 바로 울립니다. `for`는 흔들림을 거르고, 실제로 지속된 문제만 남기는 첫 번째 필터입니다.

### 3단계 — 심각도 나누기

```yaml
labels:
  severity: page    # wakes you up
  # severity: ticket # business hours
```

모든 경보가 사람을 깨우면 시스템은 곧 망가집니다. 즉시 대응이 필요한 것과 업무 시간 처리로 충분한 것을 분리해야 온콜이 버틸 수 있습니다.

### 4단계 — 경보 라우팅하기

```yaml
route:
  receiver: default
  routes:
    - match: { severity: page }
      receiver: pagerduty
    - match: { severity: ticket }
      receiver: slack-ops
```

경보는 누구에게 가는지가 명확해야 합니다. 수신자가 불분명하면 결국 아무도 책임지지 않게 됩니다.

### 5단계 — 런북 연결하기

```text
Every alert MUST have a runbook URL.
The runbook covers: meaning, first 3 actions, escalation, related dashboards.
```

경보가 울린 뒤 처음 세 행동을 적어 두지 않으면, 받는 사람은 매번 처음부터 생각해야 합니다. 경보 없는 런북도 약하지만, 런북 없는 경보는 더 위험합니다.

### 알림 규칙 의사코드 예시

경보 규칙을 코드로 표현하면 논리가 더 명확해집니다. 아래는 Python 풍 의사코드 예시입니다.

```python
def evaluate_alert_rule(metrics, threshold, duration):
    """
    경보 규칙 평가 로직
    metrics: 시계열 데이터 포인트 목록
    threshold: 임계값
    duration: 지속 시간 (for 절)
    """
    breaches = []
    for point in metrics:
        if point.value > threshold:
            breaches.append(point.timestamp)
        else:
            breaches.clear()  # 임계 아래로 떨어지면 초기화
    
    if len(breaches) > 0:
        first_breach = breaches[0]
        last_breach = breaches[-1]
        if (last_breach - first_breach) >= duration:
            return "FIRING", first_breach
    return "OK", None

# 예시 사용
result, since = evaluate_alert_rule(
    error_rate_samples,
    threshold=0.05,
    duration=timedelta(minutes=10)
)
if result == "FIRING":
    send_alert(severity="page", since=since)
```

이 로직은 Prometheus 규칙 엔진과 동일한 원리로 작동합니다. 임계를 넘으면 계속 쌓이고, 아래로 떨어지면 초기화되며, `for` 지속 시간이 충족하면 `FIRING` 상태가 됩니다.

## 경보 품질을 이렇게 확인합니다

새 경보를 넣을 때는 쿼리 정확성보다 먼저 사람이 받을 만한 신호인지 검증해야 합니다. 가장 단순한 점검 순서는 아래와 같습니다.

```text
1) 최근 30일 데이터로 규칙을 재생해 오경보 빈도 확인
2) for 값이 짧은 튐을 충분히 걸러 주는지 확인
3) severity=page 인 경보마다 runbook 링크와 소유 팀이 있는지 확인
4) 실제 호출 테스트에서 PagerDuty 또는 채팅 채널로 올바르게 라우팅되는지 확인
```

```text
Expected output:
- page 등급 경보는 주간 몇 건 수준으로 유지됩니다.
- ticket 등급 경보는 업무 시간 채널로만 전달됩니다.
- 경보 메시지 안에 summary, runbook, owner 정보가 모두 들어 있습니다.
```

### 알림 피로 줄이기

알림 피로는 경보를 받는 사람이 더 이상 경보를 신뢰하지 않게 되는 상태입니다. 이를 줄이는 기법은 크게 세 가지입니다.

**Grouping (묶기)**

비슷한 원인의 경보를 하나의 알림으로 묶습니다. 예를 들어 같은 호스트에서 세 서비스가 동시에 문제가 생기면 알림 세 개가 아니라 하나로 합쳐서 보냅니다. Alertmanager의 `group_by` 기능이 이를 자동화합니다.

```yaml
route:
  group_by: ["instance", "severity"]
  group_wait: 30s
  group_interval: 5m
```

**Inhibition (억제)**

상위 장애가 하위 장애를 가립니다. 네트워크가 끊기면 모든 서비스가 다운되었다는 경보가 쏟아지는데, 이때 네트워크 경보가 있으면 나머지는 일시적으로 숨깁니다.

```yaml
inhibit_rules:
  - source_match: { alertname: NetworkDown }
    target_match: { severity: warning }
    equal: ["instance"]
```

**Silencing (일시 중지)**

이미 알고 있는 문제나 유지보수 중인 경볰는 수동으로 일시 중지합니다. PagerDuty나 Alertmanager는 시간 범위를 지정해 특정 경보를 안보내게 할 수 있습니다.

```bash
amtool silence add alertname=DiskFull instance=node01 \
  --duration=2h \
  --comment="디스크 정리 작업 중"
```

세 기법을 함께 쓰면 동일한 오류를 반복해서 받는 피로를 크게 줄일 수 있습니다.

### 온콜 교대 및 보상

온콜은 노동이므로 교대와 보상 체계가 명확해야 합니다. 아래는 실제로 사용하는 정책 예시입니다.

**교대 정책**

- 1차 온콜: 주간 반, 주말 포함 7일
- 2차 온콜: 1차가 30분 이내 응답 없으면 에스커레이션
- 인수인계: 매주 금요일 오후 5시 주간 회고 후
- 휴일: 온콜 주간 다음 주는 휴일

**보상 체계**

- 기본 보상: 주간 온콜 수당 1일 추가 휴가
- 사고 대응 보상: 1시간 이상 대응 시 0.5일 추가 휴가
- 야간/주말 보상: 평일 밤 11시 이후 또는 주말 사고는 1.5배

이 정책은 팀마다 다르지만, 공통적으로 "온콜은 노동"이라는 인식이 있어야 합니다. 교대 없이 한 사람이 계속 온콜을 도는 구조는 오래 가지 못합니다.

### 런북 작성 가이드

런북은 경보가 왔을 때 처음 3분 안에 할 행동을 적은 문서입니다. 좋은 런북의 구조는 아래와 같습니다.

```markdown
# [P1] 결제 API 5xx 5% 초과

## 의미
결제 API의 5분간 5xx 응답이 전체 요청의 5%를 넘어 사용자 결제가 실패하고 있습니다.

## 즉시 확인할 3가지
1. Grafana 결제 API 대시보드에서 에러율 패턴 확인
2. Loki에서 `{app="payment"} |= "error" | json | status >= 500` 쿼리로 에러 로그 확인
3. 최근 10분 내 배포 여부 확인 (Slack #deploy 채널)

## 1차 조치
- 5xx가 특정 엔드포인트에 집중되어 있으면 해당 엔드포인트 로그 드릴다운
- 최근 배포와 시간이 겹치면 롤백 검토
- DB 연결 풀 고갈이면 connection limit 일시 증가

## 에스컬레이션
30분 이내 해결 안 되면 결제팀 리드에게 에스컬레이션 (Slack @payment-lead)

## 관련 링크
- 대시보드: https://grafana/d/payment
- 로그: https://grafana/explore?loki
- 포스트모템 템플릿: https://wiki/postmortem
```

런북은 경보마다 반드시 있어야 하고, 처음 받는 사람도 바로 실행할 수 있을 정도로 구체적이어야 합니다.

## 이 코드에서 먼저 봐야 할 점

- `for: 10m`은 순간 튐을 줄이는 핵심 장치입니다.
- `severity` 라벨은 경보의 행동 방식을 결정합니다.
- 런북이 없으면 경보는 절반만 만들어진 상태입니다.

## 자주 하는 실수 다섯 가지

1. 모든 경보를 새벽 호출로 보냅니다. 결국 아무도 경보를 신뢰하지 않게 됩니다.
2. 원인 경보만 만들고 증상 경보를 놓칩니다. 사용자 영향과 멀어집니다.
3. `for` 없이 즉시 울리게 만듭니다. 소음이 폭증합니다.
4. 런북이 없습니다. 경보를 받은 사람이 얼어붙습니다.
5. 소유 팀이 없습니다. 모두의 경보가 아무의 경보도 아니게 됩니다.

## 실무에서는 이렇게 생각한다

강한 팀은 먼저 증상 경보를 세웁니다. 서비스 수준 목표 위반, 높은 에러율, 긴 지연 시간처럼 사용자 경험과 연결된 신호가 우선입니다. CPU 95% 같은 원인 경보는 보조 역할로 두는 편이 낫습니다.

또한 온콜을 노동으로 다룹니다. 교대, 보상, 인수인계, 런북, 경보 품질 리뷰가 함께 있어야 장기 운영이 가능합니다. 경보 설계는 결국 사람을 보호하는 설계이기도 합니다.

## 체크리스트

- [ ] 모든 경보에 런북 링크가 있습니다.
- [ ] 심각도가 즉시 호출과 업무 시간 대응으로 나뉩니다.
- [ ] `for` 값이 설정되어 있습니다.
- [ ] 온콜 교대와 소유 팀이 정해져 있습니다.

## 연습 문제

1. 서비스 수준 목표 위반을 감지하는 경보 하나를 작성해 보세요.
2. 증상 경보와 원인 경보를 각각 하나씩 골라 보세요.
3. 한 장짜리 런북을 직접 써 보세요.

## Alertmanager와 PagerDuty 연동 예시

경보 시스템이 성숙하려면 "울린다"에서 끝나면 안 됩니다. 누가 받는지, 몇 분 안에 응답해야 하는지, 실패하면 어디로 승격되는지가 함께 정의되어야 합니다.

```yaml
route:
  receiver: slack-default
  group_by: ["alertname", "service", "severity"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 2h
  routes:
    - matchers:
        - severity="page"
      receiver: pagerduty-critical
    - matchers:
        - severity="ticket"
      receiver: opsgenie-warning

receivers:
  - name: pagerduty-critical
    pagerduty_configs:
      - routing_key: "PD_ROUTING_KEY"
        severity: "critical"
        description: "{{ .CommonAnnotations.summary }}"

  - name: opsgenie-warning
    opsgenie_configs:
      - api_key: "OPS_GENIE_KEY"
        priority: "P3"

  - name: slack-default
    slack_configs:
      - channel: "#ops-alerts"
        send_resolved: true
```

이 구성의 핵심은 심각도 라벨이 곧 라우팅 정책이 된다는 점입니다. 코드에서 `severity=page`를 남발하면 사람을 깨우는 비용이 통제되지 않습니다. 반대로 `severity=ticket`만 쓰면 중요한 장애를 놓칩니다.

## 온콜 교대와 승격 정책 표

| 단계 | 응답 시간 | 담당 | 실패 시 다음 단계 |
| --- | --- | --- | --- |
| 1차 온콜 | 15분 | 주간 primary | 2차 온콜로 승격 |
| 2차 온콜 | 20분 | 주간 secondary | 팀 리드 승격 |
| 팀 리드 | 30분 | 서비스 오너 | 사고 지휘 전환 |
| 사고 지휘 | 즉시 | incident commander | 비즈니스 커뮤니케이션 시작 |

표준 승격 정책이 없으면 장애가 커졌을 때 책임 경계가 흐려집니다. 특히 야간에는 의사결정권자가 늦게 참여해 복구 시간이 길어지는 경우가 많습니다. 승격 단계는 사람 이름이 아니라 역할 기준으로 관리해야 교대 시에도 정책이 유지됩니다.

## 경보 품질 지표

경보 자체도 품질을 측정해야 개선이 됩니다. 아래 지표를 주간 단위로 리뷰하면 알림 피로를 수치로 관리할 수 있습니다.

1. 페이지 경보 건수(주간): 팀별 목표 상한 설정
2. 오경보 비율: `false_positive / total_alerts`
3. MTTA(평균 인지 시간): 경보 발생부터 확인까지
4. MTTR(평균 복구 시간): 인지부터 복구까지
5. Runbook 미연결 경보 비율: 0% 목표

오경보 비율이 높으면 규칙이 민감한 것이고, MTTA가 높으면 라우팅이나 승격 체계가 약한 것입니다. 지표를 경보 시스템 자체의 SLO로 관리하면 장기적으로 온콜 피로가 줄어듭니다.

## Multi-Window Burn Rate 경보

SLO 기반 경보의 핵심은 에러 버짯 소진 속도를 감지하는 것입니다. 단순히 "에러율 > 5%"보다 "에러 버짯이 예상보다 14배 빠르게 소진되고 있다"가 더 정확한 신호입니다.

```yaml
groups:
  - name: slo-burn-rate
    rules:
      # 빠른 번 (1시간 창): burn rate 14x → 즉시 호출
      - alert: SLOBurnRateFast
        expr: |
          (
            sum(rate(http_requests_total{status=~"5..",service="checkout"}[1h]))
            / sum(rate(http_requests_total{service="checkout"}[1h]))
          ) > (14 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "checkout SLO burn rate 14x (1h window)"
          runbook: "https://wiki/runbook/slo-burn"

      # 느린 번 (6시간 창): burn rate 6x → 티켓
      - alert: SLOBurnRateSlow
        expr: |
          (
            sum(rate(http_requests_total{status=~"5..",service="checkout"}[6h]))
            / sum(rate(http_requests_total{service="checkout"}[6h]))
          ) > (6 * 0.001)
        for: 30m
        labels:
          severity: ticket
        annotations:
          summary: "checkout SLO burn rate 6x (6h window)"
```

Multi-window 접근의 핵심:

| 창 크기 | Burn rate 임계 | 의미 | 대응 |
| --- | --- | --- | --- |
| 1시간 | 14x | 30일 버짯이 2일 만에 소진 | 즉시 호출 (page) |
| 6시간 | 6x | 30일 버짯이 5일 만에 소진 | 업무 시간 대응 (ticket) |
| 3일 | 1x | 소진 속도 정상 | 모니터링만 |

이 방식이 단순 임계값보다 나은 이유는, SLO와 직접 연결되므로 "이 경보가 왜 중요한가"를 비즈니스 언어로 설명할 수 있기 때문입니다.

## 사고 대응 타임라인 예시

경보가 울린 뒤 실제 대응 흐름을 시간순으로 정리하면 아래와 같습니다.

```text
T+0m   PagerDuty 경보 수신 (SLOBurnRateFast)
T+2m   1차 온콜 확인, Grafana 대시보드 접속
T+5m   결제 API /checkout 엔드포인트 5xx 집중 확인
T+7m   Loki 로그에서 "connection pool exhausted" 확인
T+10m  DB connection limit 50 → 100 임시 증가
T+12m  에러율 정상 복귀 확인
T+15m  Slack #incidents 에 상황 요약 공유
T+30m  근본 원인 조사 시작 (connection leak 의심)
T+2h   핑스 배포, connection pool 원래값 복구
T+24h  포스트모템 작성 완료
```

이 타임라인에서 중요한 점은 세 가지입니다:

1. **T+2m 안에 인지**: MTTA가 2분 이내면 승격 정책이 잘 작동하는 것입니다.
2. **T+10m에 완화 조치**: 근본 원인이 아니라도 사용자 영향을 먼저 멈추는 것이 우선입니다.
3. **T+24h 포스트모템**: 같은 장애가 반복되지 않도록 근본 원인과 재발 방지를 기록합니다.

## 경보 규칙 테스트 자동화

경보 규칙도 코드와 마찬가지로 테스트할 수 있습니다. Prometheus는 `promtool`로 룰 테스트를 지원합니다.

```yaml
# tests/alert_rules_test.yaml
rule_files:
  - ../rules/api_alerts.yaml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{status="500",service="checkout"}'
        values: "0+10x20"  # 1분마다 10씩 증가, 20분 동안
      - series: 'http_requests_total{status="200",service="checkout"}'
        values: "0+100x20"
    alert_rule_test:
      - eval_time: 15m
        alertname: HighErrorRate
        exp_alerts:
          - exp_labels:
              severity: page
            exp_annotations:
              summary: "5xx > 5% for 10m"
```

```bash
# CI에서 실행
promtool test rules tests/alert_rules_test.yaml
```

이 테스트는 "에러율이 10%일 때 15분 시점에 HighErrorRate가 발화하는가"를 검증합니다. CI에 포함하면 규칙 변경 시 오경보를 미리 방지할 수 있습니다.

## 경보 이력 관리

경보 이력을 기록하면 패턴을 발견할 수 있습니다. 매주 경보 리뷰에서 확인할 항목:

| 항목 | 목표 | 초과 시 조치 |
| --- | --- | --- |
| 주간 page 경보 건수 | ≤ 5건 | 규칙 튜닝 또는 자동화 검토 |
| 오경보 비율 | ≤ 20% | for 조정, 임계값 재검토 |
| Runbook 마리 비율 | 0% | 새 경보 승인 전 runbook 필수 |
| MTTA | ≤ 5분 | 라우팅/승격 점검 |
| MTTR | ≤ 1시간 (P1) | 런북 개선, 자동 복구 검토 |

이 지표를 Grafana 대시보드로 시각화하면 경보 시스템 자체의 건강도를 보는 메타 대시보드가 됩니다. "경보 시스템을 관측하는 경보"가 있어야 운영 성숙도가 높아집니다.
## 정리

좋은 경보는 사람을 자주 깨우지 않고도 중요한 문제를 놓치지 않게 만듭니다. 조치 가능성, 사용자 영향, 명확한 소유자가 경보 설계의 핵심입니다. 다음 글에서는 경보의 기준이 되는 수치 약속, 곧 서비스 수준 지표와 목표를 봅니다.

## 처음 질문으로 돌아가기

- **새벽에 사람을 깨울 만한 경보는 어떤 조건을 가져야 할까요?**
  - 세 가지 조건을 모두 만족해야 합니다. (1) 사용자 영향이 진행 중일 것, (2) 즐시 조치하지 않으면 피해가 커질 것, (3) 자동 복구가 불가능할 것. 이 세 가지 중 하나라도 빠지면 ticket 등급으로 낮춰야 합니다.
- **경보 피로는 왜 생기고 어떻게 줄일 수 있을까요?**
  - 피로는 낮은 신뢰도에서 시작됩니다. 오경보가 쟦이면 사람은 경보 자체를 무시합니다. 해결책은 grouping, inhibition, silencing으로 중복을 줄이고, `for` 지속 시간으로 순간 튀을 걸러내며, 주간 오경보 비율을 리뷰하는 것입니다.
- **증상 경보와 원인 경보는 어떻게 다를까요?**
  - 증상 경보는 "사용자가 겪는 문제"를 감지합니다(5xx 급증, 지연 상승). 원인 경보는 "시스템 내부 상태"를 감지합니다(CPU 95%, 디스크 90%). 새벽 호출은 증상 경보 중심으로, 원인 경보는 드릴다운과 티켓용으로 분리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- [Observability 101 (4/10): 구조화된 로깅](./04-structured-logging.md)
- [Observability 101 (5/10): 분산 트레이싱 기초](./05-distributed-tracing.md)
- [Observability 101 (6/10): 대시보드 설계](./06-dashboard-design.md)
- **경보와 온콜 (현재 글)**
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Google SRE — Alerting](https://sre.google/sre-book/practical-alerting/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager docs](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [On-call principles](https://increment.com/on-call/when-the-pager-goes-off/)
- [예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

Tags: Observability, Alerting, SRE, OnCall, Monitoring
