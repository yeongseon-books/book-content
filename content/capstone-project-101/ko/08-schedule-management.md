---
series: capstone-project-101
episode: 8
title: 일정 관리
status: publish-ready
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
seo_description: 캡스톤 일정을 마일스톤과 주간 계획, 버퍼 기준으로 정리합니다
last_reviewed: '2026-05-12'
---

# 일정 관리

일정 관리는 바쁜 상태를 기록하는 일이 아니라, 무엇이 늦고 왜 늦는지 설명할 수 있게 만드는 일입니다. 이 글은 Capstone Project 101 시리즈의 8번째 글입니다. 여기서는 마일스톤, 주간 계획, 스탠드업, 위험 버퍼를 묶어서 현실적인 일정 감각을 만드는 방법을 살펴보겠습니다.

> 멘탈 모델: 좋은 일정은 완벽한 계획표가 아니라, 실제와 계획의 차이를 빨리 드러내고 바로 조정할 수 있게 만드는 시스템입니다.

## 이 글에서 다룰 문제

- 왜 완벽해 보이는 계획이 실제로는 자주 무너질까요?
- 마일스톤과 주간 계획은 어떻게 구분해서 써야 할까요?
- 데일리 스탠드업은 왜 짧고 반복 가능해야 할까요?
- 위험 버퍼는 왜 선택이 아니라 기본값에 가까울까요?
- 진행 상황은 감이 아니라 무엇으로 측정해야 할까요?

## 이 글에서 배우는 내용

- 마일스톤 정의법
- 주간 계획 작성법
- 데일리 스탠드업 형식
- 위험 버퍼 계산 감각
- 진행률 측정 기준

## 왜 중요한가

캡스톤 일정은 생각보다 쉽게 무너집니다. 구현보다 디버깅이 오래 걸리고, 팀원 일정이 엇갈리고, 발표 준비가 예상보다 늦게 시작되기 때문입니다. 그래서 마지막 마감일만 적어 두는 방식으로는 현실을 따라가기 어렵습니다.

좋은 일정은 세밀해서 좋은 것이 아니라, 조정 가능해서 좋습니다. 무엇이 밀렸는지 보이게 만들고, 블로커가 생겼을 때 바로 드러나게 해야 합니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    M[Milestones] --> W[Weekly Plan]
    W --> S[Standup]
    S --> R[Risk Buffer]
    R --> P[Progress]
```

## 핵심 용어

- **milestone**: 큰 결과 단위입니다.
- **weekly plan**: 한 주 동안 끝내야 할 계획입니다.
- **standup**: 짧게 맞추는 일일 공유입니다.
- **buffer**: 예상 밖 문제를 위한 여유 시간입니다.
- **progress**: 측정 가능한 진척 상태입니다.

## Before / After

**Before**: 마지막 마감일만 적어 둡니다.

**After**: 마일스톤, 주간 계획, 버퍼를 함께 둡니다.

## 실습: 일정 표

### 1단계 — 마일스톤

```python
milestones = ["MVP", "Demo", "Final"]
```

마일스톤은 너무 잘게 쪼개기보다, 결과가 보이는 단위로 세 개에서 다섯 개 정도 두는 편이 좋습니다.

### 2단계 — 주간 계획

```python
weeks = {1: "setup", 2: "core", 3: "polish"}
```

주간 계획은 길게 쓰기보다, 한 주에 무엇을 끝낼지 한 줄로 말할 수 있어야 합니다.

### 3단계 — 스탠드업 형식

```python
standup = ["yesterday", "today", "blockers"]
```

스탠드업은 짧고 반복 가능한 형식이어야 합니다. 길어지는 순간 공유보다 회의가 됩니다.

### 4단계 — 위험 버퍼

```python
buffer_days = 0.2 * 21
```

버퍼는 낭비가 아니라 안전장치입니다. 예상보다 느린 현실을 계획에 반영하는 최소 장치라고 보는 편이 좋습니다.

### 5단계 — 진척도 스냅샷

```python
progress = {"done": 12, "todo": 8, "blocked": 2}
```

진척도는 체감보다 숫자로 보는 편이 낫습니다. 막힌 항목이 얼마나 있는지 드러나야 조정이 빨라집니다.

## 이 코드에서 먼저 볼 점

- 마일스톤은 세 개에서 다섯 개 정도가 적당합니다.
- 주간 계획은 한 줄로 읽혀야 합니다.
- 버퍼는 전체 일정의 약 20% 수준입니다.
- 블로커는 숨기지 않고 드러내야 합니다.

## 자주 하는 실수 5가지

1. 버퍼 없이 계획을 꽉 채웁니다.
2. 스탠드업이 길어집니다.
3. 진행률을 감으로 판단합니다.
4. 주간 계획을 고정된 문서로 생각합니다.
5. 블로커를 늦게 공유합니다.

## 실무에서는 이렇게 이어집니다

실무 팀도 2주 스프린트, 번다운 차트, 주간 목표 같은 방식으로 일정을 관리합니다. 중요한 것은 형식 자체보다, 계획과 실제의 차이를 매주 드러내고 바로 조정하는 리듬을 만드는 데 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 마일스톤은 결과 중심입니다.
- 계획은 조정 가능합니다.
- 버퍼는 기본값에 가깝습니다.
- 블로커는 빨리 보이게 만듭니다.
- 진행 상황은 숫자로 봅니다.

## 체크리스트

- [ ] 마일스톤 표가 있습니다.
- [ ] 주간 계획이 있습니다.
- [ ] 데일리 스탠드업 형식이 있습니다.
- [ ] 20% 버퍼가 반영되어 있습니다.

## 연습 문제

1. milestone을 한 줄로 정의해 보세요.
2. buffer의 목적을 한 줄로 설명해 보세요.
3. standup의 세 항목을 한 줄로 적어 보세요.

## 정리와 다음 글

일정 관리는 예쁜 계획표를 만드는 일이 아니라, 늦어지는 지점을 빨리 드러내는 일입니다. 마일스톤, 주간 계획, 버퍼, 블로커 관리가 함께 있어야 일정이 현실을 따라갑니다. 다음 글에서는 프로젝트 결과를 어떻게 발표 자료로 정리할지 살펴보겠습니다.

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
