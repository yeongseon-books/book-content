---
series: sre-101
episode: 8
title: Toil 줄이기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - SRE
  - Toil
  - Automation
  - Productivity
  - Operations
seo_description: Toil의 정의, 측정, 자동화 우선순위, 절감 전략, 기술 부채와의 관계를 입문자 관점에서 정리한 글
last_reviewed: '2026-05-11'
---

# Toil 줄이기

## 이 글에서 다룰 문제

- Toil이 무엇이고, 일반적인 운영 업무와 어떻게 다른지 설명합니다.
- 팀 시간이 반복 수작업에 얼마나 쓰이는지 측정하는 방법을 정리합니다.
- 어떤 작업부터 자동화해야 효과가 큰지 우선순위 기준을 살펴봅니다.
- 자동화의 손익분기점을 계산해 투자 판단에 연결하는 방법을 설명합니다.
- Toil을 줄이지 못하면 조직 성장과 신뢰성에 어떤 문제가 생기는지 짚어 봅니다.

> SRE 101 시리즈 (8/10)

운영팀이 바쁘다는 사실만으로 그 일이 모두 가치 있다고 볼 수는 없습니다. 어떤 일은 시스템 이해를 깊게 만들고, 어떤 일은 고객 가치에 직접 연결됩니다. 반면 어떤 일은 매일 반복되지만, 사람이 계속 붙어 있어야 한다는 사실 외에는 설명할 가치가 거의 없습니다. SRE에서는 이런 반복 수작업을 Toil이라고 부릅니다.

Toil은 단순히 귀찮은 일이 아닙니다. 자동화할 수 있고, 반복되고, 장기적으로는 엔지니어링 시간을 갉아먹는 작업입니다. 그래서 Toil을 줄이는 일은 편의 개선이 아니라 팀 생산성과 신뢰성을 지키는 핵심 활동입니다.

## 왜 중요한가

Toil이 팀 시간의 큰 비중을 차지하면 개선 작업이 멈춥니다. 장애 예방, 테스트 강화, 배포 자동화 같은 일은 모두 뒤로 밀리고, 팀은 계속 같은 운영 업무를 반복합니다.

또한 Toil은 보이지 않는 기술 부채이기도 합니다. 문서상으로는 시스템이 돌아가지만, 실제로는 야간 호출과 수동 복구에 의존하고 있다면 서비스는 이미 사람의 노동 위에 불안정하게 서 있는 상태입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Manual["수작업"] --> Toil["Toil"]
    Toil --> Automate["자동화"]
    Automate --> Saved["절약 시간"]
```

> Toil은 일을 많이 한다는 뜻이 아니라, 사람의 시간이 반복적으로 소모되는 구조를 뜻합니다. 자동화는 그 시간을 다시 엔지니어링에 돌려주는 수단입니다.

## 핵심 용어

- toil: 반복적이고 자동화 가능한 수작업입니다.
- runbook: 사람이 따라 하는 운영 절차 문서입니다.
- automation: 절차를 코드로 옮겨 사람이 직접 하지 않게 만드는 작업입니다.
- toil ratio: 전체 시간 중 Toil이 차지하는 비율입니다.
- break-even: 자동화에 투자한 시간이 절약되는 시점입니다.

## Before / After

Before에서는 야간 호출이 올 때마다 담당자가 수동으로 서비스 재시작, 로그 확인, 캐시 비우기 같은 작업을 반복합니다. 그 작업은 익숙해지지만, 팀은 같은 문제를 계속 손으로 해결합니다.

After에서는 반복 절차가 스크립트와 자동화 작업으로 바뀝니다. 사람은 예외 상황과 구조 개선에 더 많은 시간을 쓰고, 복구 속도도 빨라집니다.

## 단계별로 Toil 측정하고 자동화하기

### 1단계 — Toil 시간 기록

```python
def log_toil(task, minutes):
    return {"task": task, "minutes": minutes}
```

자동화를 논의하기 전에 먼저 시간을 기록해야 합니다. 어떤 작업이 얼마나 자주 반복되는지 보이지 않으면 우선순위도 감으로 흐릅니다.

### 2단계 — Toil 비율 계산

```python
def toil_ratio(toil_min, total_min):
    return toil_min / total_min
```

Toil ratio는 팀 상태를 한눈에 보여 줍니다. 운영 업무 자체가 문제가 아니라, 반복 수작업이 팀 시간을 얼마나 잠식하는지가 중요합니다.

### 3단계 — 자동화 후보 점수화

```python
def score(freq_per_week, minutes_each):
    return freq_per_week * minutes_each
```

빈도와 1회당 소요 시간을 곱하면 후보 간 우선순위를 비교하기 쉬워집니다. 가장 짜증 나는 작업보다 가장 많이 시간을 태우는 작업부터 손보는 편이 효과적일 때가 많습니다.

### 4단계 — 손익분기점 계산

```python
def break_even(saved_per_week, build_minutes):
    return build_minutes / saved_per_week
```

자동화도 공짜는 아닙니다. 만드는 데 드는 시간과 매주 절약되는 시간을 같이 보면 어떤 작업부터 투자할지 더 현실적으로 판단할 수 있습니다.

### 5단계 — 자동화 구현

```python
def auto_restart(service):
    return f"systemctl restart {service}"
```

마지막 단계는 절차를 코드로 옮기는 일입니다. 단순한 재시작 스크립트처럼 보이더라도, 반복 호출을 줄이고 복구 시간을 낮추는 효과가 크면 충분히 가치가 있습니다.

## 이 코드에서 봐야 할 점

Toil reduction의 출발점은 자동화 기술이 아니라 측정입니다. 얼마나 자주 일어나는지, 한 번에 얼마의 시간이 드는지, 자동화 후 언제 투자비를 회수하는지를 알아야 우선순위가 명확해집니다.

또한 runbook이 있다고 해서 Toil이 해결된 것은 아닙니다. 문서화는 첫 단계일 뿐이고, 반복 절차를 코드로 옮겨야 사람이 하던 일을 시스템이 대신하게 됩니다.

## 자주 하는 실수 5가지

1. Toil 시간을 기록하지 않아 우선순위가 매번 감으로 바뀌는 경우입니다.
2. 점수화 없이 가장 눈에 띄는 작업만 자동화하는 경우입니다.
3. runbook을 쌓아 두고 코드화는 미루는 경우입니다.
4. 자동화 자체의 유지보수 비용을 무시하는 경우입니다.
5. 운영 자동화가 출시 뒤에도 계속 관리되어야 한다는 점을 잊는 경우입니다.

## 실무에서는 이렇게 본다

현업에서는 야간 복구, 로그 수집, 임시 캐시 정리, 장애 공지 초안 생성 같은 작업이 Toil 후보가 되곤 합니다. 이런 작업을 자동화하면 MTTR이 줄고, 사람은 더 구조적인 개선에 시간을 쓸 수 있습니다.

시니어 엔지니어는 Toil을 단순 피로가 아니라 부채로 봅니다. 반복 작업이 많다는 사실은 시스템과 절차 어딘가에 아직 코드로 옮겨지지 않은 운영 지식이 남아 있다는 뜻이기 때문입니다.

## 체크리스트

- [ ] 팀의 Toil 시간을 주기적으로 기록한다.
- [ ] 빈도와 소요 시간을 기준으로 자동화 후보를 정렬한다.
- [ ] 자동화의 손익분기점을 계산한다.
- [ ] 자동화 코드에도 오너와 유지 계획이 있다.

## 연습 문제

1. Toil을 일반 운영 업무와 구분해서 정의해 보세요.
2. 손익분기점 계산이 자동화 우선순위에 왜 도움이 되는지 적어 보세요.
3. runbook만 있고 자동화가 없는 상태의 한계를 설명해 보세요.

## 정리와 다음 글

이 글에서는 Toil을 반복적이고 자동화 가능한 수작업으로 설명했습니다. 중요한 점은 불편함을 줄이는 데서 끝나지 않고, 시간을 측정하고 우선순위를 정해 자동화 투자로 연결하는 데 있습니다.

다음 글에서는 capacity planning을 다룹니다. 앞으로 들어올 수요를 어떻게 예측하고, 어느 정도 여유를 남겨 둘지 이어서 살펴보겠습니다.

<!-- toc:begin -->
- [SRE란 무엇인가?](./01-what-is-sre.md)
- [Reliability](./02-reliability.md)
- [SLI, SLO, SLA](./03-sli-slo-sla.md)
- [Error Budget](./04-error-budget.md)
- [Monitoring](./05-monitoring.md)
- [Incident Response](./06-incident-response.md)
- [Postmortem](./07-postmortem.md)
- **Toil 줄이기 (현재 글)**
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Eliminating Toil - Google SRE Book](https://sre.google/sre-book/eliminating-toil/)
- [Identifying and Tracking Toil - Google SRE Workbook](https://sre.google/workbook/eliminating-toil/)
- [Automating Operations - Google SRE Book](https://sre.google/sre-book/automation-at-google/)
- [Toil Reduction - Atlassian](https://www.atlassian.com/incident-management/devops/toil)

Tags: SRE, Toil, Automation, Productivity, Operations
