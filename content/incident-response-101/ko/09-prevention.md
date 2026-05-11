---
series: incident-response-101
episode: 9
title: 재발 방지
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Incident
  - Prevention
  - Reliability
  - Testing
  - Operations
seo_description: Incident 재발 방지, 액션 아이템 추적, 회귀 테스트, 가드레일, 카오스 엔지니어링을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# 재발 방지

> Incident Response 101 시리즈 (9/10)


## 이 글에서 다룰 문제

*Postmortem* 까지만 가면 *조직 학습* 이 *행동* 으로 *전환* 되지 않습니다.

## 전체 흐름
```mermaid
flowchart LR
    Action["action item"] --> Test["regression test"]
    Test --> Guard["guardrail"]
    Guard --> Chaos["chaos exp"]
    Chaos --> Learn["learning"]
    Learn --> Action
```

## Before/After

**Before**: *Postmortem* 후 *문서* 만 남음.

**After**: *Postmortem* 후 *코드* 와 *테스트* 가 남음.

## 재발 방지 키트

### 1단계 — 액션 등록

```python
def register(action):
    return {**action, "status": "open"}
```

### 2단계 — 회귀 테스트

```python
def test_regression(scenario, run):
    return run(scenario) == "ok"
```

### 3단계 — 가드레일

```python
def guard(payload, limit=1000):
    if payload > limit:
        raise ValueError("blocked")
```

### 4단계 — 카오스 실험

```python
def inject(failure):
    return {"injected": failure, "expected": "graceful"}
```

### 5단계 — 학습 루프

```python
def closed(action):
    return action["status"] == "done"
```

## 이 코드에서 주목할 점

- *상태* 는 *open/done* 두 개.
- *가드레일* 은 *raise* 한 줄.
- *카오스* 는 *기대 결과* 와 함께.

## 자주 하는 실수 5가지

1. ***액션* 만 등록 후 *방치*.**
2. ***회귀 테스트* 누락.**
3. ***가드레일* 을 *경고* 로만.**
4. ***카오스* 없이 *가설* 만.**
5. ***루프* 가 *분기* 를 못 넘김.**

## 실무에서는 이렇게 쓰입니다

*Postmortem* 의 모든 *액션* 이 *Jira* 에 *링크* 되고, *회귀 테스트* 와 *카오스 시나리오* 로 *변환* 되어 *CI* 에서 매주 실행됩니다.

## 체크리스트

- [ ] *액션 추적*.
- [ ] *회귀 테스트*.
- [ ] *가드레일 정책*.
- [ ] *카오스 일정*.

## 정리 및 다음 단계

다음 글은 캡스톤 *Incident Runbook 만들기* 입니다.

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
