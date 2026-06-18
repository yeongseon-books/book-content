---
title: "바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜"
series: observability-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Alerting
  - SRE
  - OnCall
---

# 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜

이 글은 "바이브코딩을 위한 Observability 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 Prometheus 경보 규칙을 빠르게 만들어 줍니다. 그런데 경보는 많이 울릴수록 안전해질 것 같지만, 실제로는 그 반대가 되기 쉽습니다. 하루에 수십 번 울리는 경보는 결국 아무도 믿지 않게 됩니다. 정말 위험한 상황이 와도 "또 오경보겠지"라는 반응이 먼저 나오면 이미 설계가 잘못된 것입니다.

온콜은 도구 문제가 아니라 사람의 집중력과 수면을 다루는 운영 체계입니다. 경보 하나를 추가하는 일은 알림 한 줄을 더 만드는 것이 아니라 운영 비용을 늘리는 결정입니다. 좋은 경보 설계는 기술적 정확성만큼이나 인간 비용을 함께 고려해야 합니다.

사용자 영향이 분명한 문제만 즉시 깨우고, 나머지는 업무 시간 안에 처리할 수 있게 나누면 사람의 에너지를 중요한 문제에 집중시킬 수 있습니다.

경보 심각도 기준, 증상 경보 vs 원인 경보, Alertmanager 라우팅, 런북 연결을 중심으로 정리합니다.

> **핵심 인사이트:** P1/P2만 새벽에 사람을 깨우고 나머지는 채팅/티켓으로 보내는 것이 온콜 지속 가능성의 핵심입니다. `for: 10m` 없이 경보를 설정하면 잠깐 튄 수치에도 새벽 호출이 발생합니다.

## 이 글에서 다룰 문제

- 새벽에 사람을 깨울 만한 경보는 어떤 조건을 가져야 할까요?
- 경보 피로는 왜 생기고 어떻게 줄일 수 있을까요?
- 증상 경보와 원인 경보는 어떻게 다를까요?
- Alertmanager 라우팅은 어떻게 설정할까요?
- AI가 만든 경보 규칙에서 확인해야 할 것은 무엇인가요?

## 경보와 온콜 핵심 패턴

```yaml
# 좋은 경보 규칙: 증상 기반 + 지속 시간 + 런북 연결
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: >
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m          # 지속 시간 없으면 잡음이 폭발
        labels:
          severity: page  # P1: 즉시 호출
        annotations:
          summary: "5xx > 5% for 10m"
          runbook: "https://wiki/runbook/api-error"
```

```yaml
# Alertmanager 라우팅: 심각도별 채널 분리
route:
  receiver: default
  routes:
    - match: { severity: page }
      receiver: pagerduty    # P1/P2: 즉시 호출
    - match: { severity: ticket }
      receiver: slack-ops    # P3/P4: 채팅/티켓

# 심각도 기준
# P1 (Critical): 15분 이내 응답 - 결제 서비스 중단, 데이터 유출
# P2 (High):    30분 이내 응답 - API 5xx 5% 이상
# P3 (Medium):  4시간 이내 응답 - 디스크 80%
# P4 (Low):     업무 시간 내    - 로그 용량 증가 추세
```

## 변경 전후 비교

**Before: 경보 피로**
```text
- 하루 수십 개 경보 → 대부분 오경보
- 모든 경보가 새벽 호출
- 지속 시간 없어서 잠깐 튄 수치에도 알림
- 런북 없이 경보만 있음
- 진짜 장애가 소음 속에 묻힘
```

**After: 의미 있는 경보만**
```text
- 새벽 호출용 경보를 극단적으로 줄임
- P1/P2만 즉시 호출, 나머지는 채팅/티켓
- `for: 10m`으로 일시적 잡음 제거
- 모든 경보에 런북 URL 연결
- 경보 수는 줄어들지만 신뢰도 높아짐
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 지속 시간(`for`) 없음 | 잠깐 튄 수치에 새벽 호출 발생 | `for: 5m~15m` 설정 |
| 모든 경보를 P1으로 | 경보 피로로 진짜 사고를 놓침 | 심각도 기준 명확히 구분 |
| 원인 경보만 있음 | CPU 높음 → 사용자 영향인지 모름 | 증상 경보(에러율, 지연) 우선 |
| 런북 없는 경보 | 누가 받아도 무엇을 해야 할지 모름 | 모든 경보에 runbook URL 필수 |
| 라우팅 없이 모두 같은 채널 | 누가 책임자인지 불분명 | 팀/기능별 라우팅 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Prometheus 경보 규칙과 Alertmanager 설정을 만들어줘.
API 에러율 > 5% (10분 지속) → P1 PagerDuty 호출,
디스크 > 80% → P3 Slack 알림,
모든 경보에 runbook URL 포함,
심각도별 라우팅 설정"

# AI 결과물 검증 체크포인트:
# - 모든 경보에 `for:` 지속 시간이 있는가?
# - 심각도가 page/ticket/info로 구분되어 있는가?
# - Alertmanager 라우팅이 심각도별로 분리되어 있는가?
# - 모든 경보에 runbook URL이 있는가?
# - 증상 경보(에러율, 지연)가 원인 경보보다 우선인가?
```

## 운영 체크리스트

- [ ] 모든 경보에 `for:` 지속 시간이 설정되어 있다
- [ ] P1/P2만 새벽 호출, P3/P4는 채팅/티켓으로 라우팅된다
- [ ] 모든 경보에 runbook URL이 연결되어 있다
- [ ] 주간 경보 리뷰로 오경보를 정기적으로 제거한다
- [ ] 온콜 담당자 교체 주기와 에스컬레이션 체계가 명시되어 있다

## 처음 질문으로 돌아가기

- **새벽 호출 경보의 조건은?** 사용자에게 직접 영향을 주는 증상(에러율, 응답 지연, 서비스 다운)이어야 합니다. 일정 시간(`for:`) 이상 지속되어야 합니다. 자동화로 해결 가능하면 호출 대신 자동 조치를 우선합니다.
- **증상 경보와 원인 경보의 차이는?** 증상 경보는 "API 에러율 5% 초과"처럼 사용자 영향을 직접 측정합니다. 원인 경보는 "CPU 90% 초과"처럼 내부 리소스를 측정합니다. 사용자 영향과 연결되는 증상 경보를 먼저 설계해야 합니다.
- **경보 피로를 줄이는 가장 효과적인 방법은?** 모든 경보에 `for:` 지속 시간 추가, P3 이하는 채팅/티켓으로 라우팅, 주간 오경보 리뷰로 정기 제거입니다.

## 정리

바이브코딩에서 AI가 만들어 준 경보 규칙에서 지속 시간, 심각도 구분, 런북 연결, 라우팅 설정을 반드시 확인하세요. 경보 수보다 경보 신뢰도가 온콜 지속 가능성을 결정합니다. 다음 글에서는 SLI와 SLO를 다룹니다.

## 참고 자료

- [Google SRE Book — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [PagerDuty — Alerting Best Practices](https://www.pagerduty.com/resources/learn/best-practices-alerting/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭
- 바이브코딩을 위한 Observability 기초 (3/10): 로그
- 바이브코딩을 위한 Observability 기초 (4/10): 트레이스
- 바이브코딩을 위한 Observability 기초 (5/10): 세 신호 연결
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드
- **바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (8/10): SLI와 SLO
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Alerting, SRE, OnCall
