---
episode: 9
language: ko
last_reviewed: '2026-05-12'
seo_description: 장애 재발을 코드와 테스트, 자동화 가드레일로 남겨 같은 실수를 반복하지 않도록 만드는 실무 방법을 정리합니다.
series: incident-response-101
status: publish-ready
tags:
- Incident
- Prevention
- Reliability
- Testing
- Operations
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: 재발 방지
---

# 재발 방지

이 글은 Incident Response 101 시리즈의 9번째 글입니다.

사후 분석 문서까지 마쳤다고 해서 incident 대응이 끝난 것은 아닙니다. 그 문서가 다시 코드, 테스트, 운영 규칙으로 돌아가지 않으면 조직은 같은 실수를 반복합니다. 그래서 재발 방지는 “좋은 회고를 남기는 일”이 아니라, 학습을 시스템에 박아 넣는 일에 가깝습니다.

## 이 글에서 다룰 문제

많은 팀이 이 구간에서 멈춥니다. 후속 조치는 등록했지만 추적하지 않고, 회귀 테스트는 만들지 않고, 위험한 작업을 막는 안전 장치도 두지 않습니다. 그러면 문서는 훌륭해 보여도 다음 분기에는 비슷한 incident가 다시 생깁니다. 학습이 행동으로 바뀌지 않은 셈입니다.

> 재발 방지는 문서가 아니라 코드와 운영 습관으로 남아야 합니다. 그래야 다음 incident를 실제로 막을 수 있습니다.

- 사후 분석 뒤에 왜 같은 incident가 다시 반복될까요?
- 후속 조치 추적이 없으면 어떤 문제가 생길까요?
- 회귀 테스트는 왜 재발 방지의 핵심일까요?
- 안전 장치는 경고와 무엇이 다를까요?
- 카오스 실험은 예방 체계에서 어떤 역할을 할까요?

## 왜 이 주제가 중요한가

incident는 한 번 해결했다고 사라지지 않습니다. 같은 조건이 남아 있으면 언젠가 같은 방식으로 다시 드러납니다. 그래서 재발 방지는 “다음엔 조심하자”가 아니라, 다음에 같은 실수를 해도 시스템이 막아 주도록 바꾸는 과정이어야 합니다.

또한 예방은 신뢰성 투자 방식을 바꿉니다. 사람 기억에 기대는 조직은 시간이 지날수록 약해지고, 코드와 테스트에 학습을 남기는 조직은 시간이 지날수록 강해집니다. 문서가 출발점이라면, 테스트와 안전 장치는 그 문서를 현실에 고정하는 장치입니다.

## 한눈에 보는 구조

```mermaid
flowchart LR
    Action["후속 조치"] --> Test["회귀 테스트"]
    Test --> Guard["안전 장치"]
    Guard --> Chaos["카오스 실험"]
    Chaos --> Learn["학습"]
    Learn --> Action
```

이 흐름은 선형이 아니라 반복 루프입니다. action item이 테스트로 바뀌고, 테스트가 guardrail로 이어지며, chaos 실험이 실제로 잘 막히는지 확인합니다. 그 결과를 다시 학습으로 돌려 다음 action item을 만듭니다.

## 핵심 용어

- **action item**: 사후 분석에서 나온 후속 작업입니다.
- **regression test**: 같은 버그가 다시 생기지 않는지 확인하는 테스트입니다.
- **guardrail**: 위험한 작업을 코드 차원에서 막는 장치입니다.
- **chaos exp**: 의도적으로 실패를 주입하는 실험입니다.
- **learning loop**: incident에서 배운 내용을 다음 예방 작업으로 돌리는 반복 구조입니다.

이 용어를 묶어 보면 재발 방지의 본질이 보입니다. 후속 조치는 할 일 목록이고, 회귀 테스트는 기억 장치이며, guardrail은 실시간 차단 장치입니다. chaos 실험은 그 차단 장치가 실제로 작동하는지 검증하는 단계입니다.

## 전후 비교

이전: 사후 분석 뒤에 문서만 남고 코드와 테스트는 그대로입니다.

이후: 사후 분석 뒤에 테스트, 안전 장치, 운영 규칙이 함께 남습니다.

이후 상태에서 중요한 변화는 재발 방지의 결과물이 문서가 아니라 실행 가능한 산출물이 된다는 점입니다. 나중에 새 팀원이 와도 문서를 읽기 전에 테스트가 먼저 실패하고, guardrail이 먼저 막아 줄 수 있습니다.

## 단계별 실습: 재발 방지 키트 만들기

### 1단계 — 후속 조치 등록하기

먼저 사후 분석에서 나온 후속 조치를 열린 상태로 등록합니다. 추적의 시작점은 무엇을 할지를 명시하는 일입니다.

```python
def register(action):
    return {**action, "status": "open"}
```

### 2단계 — 회귀 테스트 붙이기

수정이 코드 변경으로만 끝나면 시간이 지나면서 맥락이 사라집니다. 회귀 테스트를 같이 두면 같은 문제가 다시 들어왔을 때 바로 잡을 수 있습니다.

```python
def test_regression(scenario, run):
    return run(scenario) == "ok"
```

### 3단계 — guardrail 추가하기

위험한 입력이 들어오면 경고만 띄우지 말고, 아예 막아야 할 때가 있습니다. guardrail은 그런 차단선을 코드로 만든 것입니다.

```python
def guard(payload, limit=1000):
    if payload > limit:
        raise ValueError("blocked")
```

### 4단계 — chaos 실험 설계하기

예방 체계는 실제 실패를 넣어 봐야 믿을 수 있습니다. 어떤 실패를 넣고, 시스템이 어떤 방식으로 버텨야 하는지를 함께 적어 두면 실험이 훨씬 명확해집니다.

```python
def inject(failure):
    return {"injected": failure, "expected": "graceful"}
```

### 5단계 — 학습 루프 닫기

마지막은 action item이 실제로 닫혔는지 보는 단계입니다. 상태가 open인지 done인지 구분하는 것만으로도 방치된 작업을 찾을 수 있습니다.

```python
def closed(action):
    return action["status"] == "done"
```

## 이 코드에서 먼저 볼 점

- action status는 단순해야 추적이 쉽습니다.
- guardrail은 경고가 아니라 차단이어야 할 때가 있습니다.
- chaos 실험에는 항상 기대 결과가 함께 있어야 합니다.

재발 방지에서 가장 큰 착각은 경고 메시지만 남기면 충분하다고 생각하는 것입니다. 정말 위험한 경로라면 시스템이 거부해야 합니다. 로그를 남기는 것과 실패를 막는 것은 전혀 다른 수준의 예방입니다.

## 자주 하는 실수 5가지

1. 후속 조치를 등록만 하고 끝까지 추적하지 않습니다.
2. 회귀 테스트를 만들지 않아 같은 버그가 다시 들어와도 모릅니다.
3. guardrail을 경고 수준으로만 두고 실제 차단은 하지 않습니다.
4. chaos 실험 없이 가설만 세워 둡니다.
5. learning loop가 분기 리뷰까지 이어지지 못합니다.

특히 첫 번째 실수는 모든 예방 체계를 무너뜨립니다. 추적 없는 후속 조치는 해야 할 일을 적어 둔 메모와 다르지 않습니다. 담당자, 기한, 점검 주기가 함께 있어야 진짜 시스템이 됩니다.

## 실무에서는 이렇게 봅니다

실무에서는 사후 분석에서 나온 조치를 Jira에 연결하고, 주요 항목은 회귀 테스트와 chaos 시나리오로 바꿔 CI에 포함시키는 식으로 운영합니다. 그다음 분기 단위 리뷰에서 미완료 항목과 실패한 실험을 다시 봅니다. 예방은 한 번의 작업이 아니라 주기적 운영입니다.

시니어 엔지니어는 예방을 문서가 아니라 코드로 봅니다. 사후 분석은 출발점이고, 실제 예방은 테스트와 안전 장치에 남아야 한다고 생각합니다.

## 체크리스트

- [ ] 사후 분석 후속 조치를 추적하는 도구가 있다.
- [ ] 주요 incident마다 회귀 테스트가 추가된다.
- [ ] 위험 작업을 막는 guardrail 정책이 있다.
- [ ] chaos 실험 일정과 리뷰 주기가 있다.

## 연습 문제

1. guardrail을 한 문장으로 정의해 보세요.
2. 회귀 테스트가 문서보다 강력한 이유를 설명해 보세요.
3. 여러분 팀에서 chaos 실험으로 검증해 볼 실패 시나리오 하나를 적어 보세요.

## 정리와 다음 글

재발 방지는 “다시는 그러지 말자”는 다짐으로 이루어지지 않습니다. 후속 조치 추적, 회귀 테스트, guardrail, chaos 실험처럼 실행 가능한 장치로 학습을 남겨야 합니다. 사후 분석이 원인과 교훈을 정리한다면, 예방은 그 교훈을 시스템에 새기는 단계입니다.

다음 글에서는 시리즈의 마무리로, 지금까지 배운 severity, 대응, communication, postmortem, prevention을 하나의 incident runbook으로 묶는 방법을 다루겠습니다.

<!-- toc:begin -->
- [Incident란 무엇인가?](./01-what-is-incident.md)
- [Severity 분류](./02-severity.md)
- [초기 대응](./03-initial-response.md)
- [Communication](./04-communication.md)
- [Timeline 작성](./05-timeline.md)
- [Root Cause Analysis](./06-root-cause-analysis.md)
- [Mitigation과 Resolution](./07-mitigation-and-resolution.md)
- [Postmortem](./08-postmortem.md)
- **재발 방지 (현재 글)**
- Incident Runbook 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Action Items - Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)
- [Chaos Engineering Principles](https://principlesofchaos.org/)
- [Guardrails vs Gates - Thoughtworks](https://www.thoughtworks.com/insights/blog/guardrails-not-gates)
- [Preventing Recurrence - PagerDuty](https://response.pagerduty.com/after/preventing/)

Tags: Incident, Prevention, Reliability, Testing, Operations