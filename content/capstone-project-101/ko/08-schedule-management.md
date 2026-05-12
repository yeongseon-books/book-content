---
series: capstone-project-101
episode: 8
title: 일정 관리
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Capstone
  - Schedule
  - Planning
  - Project
  - Beginner
seo_description: 캡스톤 일정을 마일스톤, 주간 계획, 위험 버퍼로 관리하는 방법을 정리한 글
last_reviewed: '2026-05-11'
---

# 일정 관리

일정 관리는 바쁜 상태를 기록하는 일이 아니라 무엇이 늦고 왜 늦는지 설명할 수 있게 만드는 작업입니다.

이 글은 측스톤 프로젝트 101 시리즈의 8번째 글입니다.

> 캡스톤 프로젝트 101 시리즈 (8/10)


## 이 글에서 다룰 문제

일정이 모호하면 팀은 늘 바쁘지만 무엇이 늦는지 설명하지 못합니다. 마일스톤, 주간 계획, 위험 버퍼를 함께 잡아야 진행 상황을 현실적으로 볼 수 있습니다.

## 전체 흐름
```mermaid
flowchart LR
    M[Milestones] --> W[Weekly Plan]
    W --> S[Standup]
    S --> R[Risk Buffer]
    R --> P[Progress]
```

## Before/After

**Before**: 마지막 마감일만 적어 둡니다.

**After**: 마일스톤, 주간 계획, 버퍼를 함께 둡니다.

## 일정 표

### 1단계 — 마일스톤

```python
milestones = ["MVP", "Demo", "Final"]
```

### 2단계 — 주간 계획

```python
weeks = {1: "setup", 2: "core", 3: "polish"}
```

### 3단계 — 스탠드업 양식

```python
standup = ["yesterday", "today", "blockers"]
```

### 4단계 — 위험 버퍼

```python
buffer_days = 0.2 * 21
```

### 5단계 — 진척도

```python
progress = {"done": 12, "todo": 8, "blocked": 2}
```

## 이 코드에서 주목할 점

- 마일스톤은 너무 잘게 쪼개기보다 결과가 보이는 단위로 3~5개 정도 두는 편이 관리하기 좋습니다.
- 주간 계획은 길게 쓰기보다 한 주에 무엇을 끝낼지 한 줄로 말할 수 있어야 합니다.
- 버퍼는 낭비가 아니라 일정이 흔들릴 때 전체 계획을 지켜 주는 안전장치입니다.

## 자주 하는 실수 5가지

1. 버퍼 없이 계획을 꽉 채워 예상 밖 이슈에 바로 무너집니다.
2. 스탠드업이 길어져 공유 시간이 회의 시간으로 바뀝니다.
3. 진척도를 체감으로만 판단해서 실제 지연을 놓칩니다.
4. 주간 계획을 한 번 세운 뒤 끝까지 고정하려고 합니다.
5. 블로커를 늦게 공유해 팀 전체 대응이 늦어집니다.

## 실무에서는 이렇게 쓰입니다

실무 팀도 2주 스프린트, 번다운 차트, 주간 목표 같은 방식으로 일정을 관리합니다. 중요한 점은 형식 자체보다, 계획과 실제 차이를 매주 드러내고 바로 조정하는 리듬을 만드는 데 있습니다.

## 체크리스트

- [ ] 마일스톤 표를 만들었습니다.
- [ ] 주간 계획을 적었습니다.
- [ ] 데일리 스탠드업 형식을 정했습니다.
- [ ] 버퍼 20%를 반영했습니다.

## 정리 및 다음 단계

일정 관리는 예쁜 간트 차트를 만드는 일이 아니라, 늦어지는 지점을 빨리 드러내는 일입니다. 다음 글에서는 프로젝트 결과를 어떻게 발표 자료로 정리할지 살펴보겠습니다.

<!-- toc:begin -->
- [캡스톤 프로젝트란 무엇인가](./01-what-is-capstone.md)
- [주제 선정](./02-choosing-a-topic.md)
- [문제 정의](./03-defining-the-problem.md)
- [요구사항 정리](./04-organizing-requirements.md)
- [팀 역할 나누기](./05-splitting-team-roles.md)
- [MVP 설계](./06-designing-the-mvp.md)
- [기술 스택 선택](./07-choosing-the-tech-stack.md)
- **일정 관리 (현재 글)**
- 발표 자료 만들기 (예정)
- 프로젝트 회고 (예정)
<!-- toc:end -->

## 참고 자료

- [Scrum Guide](https://scrumguides.org/)
- [Critical Path Method](https://en.wikipedia.org/wiki/Critical_path_method)
- [Burndown Chart - Atlassian](https://www.atlassian.com/agile/tutorials/burndown-charts)
- [Estimation - Steve McConnell](https://stevemcconnell.com/sea/)

Tags: Capstone, Schedule, Planning, Project, Beginner
