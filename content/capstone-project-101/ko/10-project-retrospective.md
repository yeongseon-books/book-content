---
series: capstone-project-101
episode: 10
title: 프로젝트 회고
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Capstone
  - Retrospective
  - Learning
  - Reflection
  - Beginner
seo_description: 캡스톤 회고를 KPT와 데이터, 다음 행동 중심으로 정리하는 법을 다룹니다
last_reviewed: '2026-05-14'
---

# 프로젝트 회고

프로젝트가 끝나면 팀은 보통 안도감부터 느낍니다. 그 순간 바로 흩어지면 이번 학기의 시행착오는 다시 개인 기억으로만 남습니다.

회고의 목적은 감정을 털어놓는 데서 멈추지 않고, 사실과 원인과 다음 행동을 문서로 남기는 데 있습니다. 그래야 이번 프로젝트의 실패와 성공이 다음 프로젝트의 입력이 됩니다.

이 글은 Capstone Project 101 시리즈의 마지막 글입니다. 여기서는 KPT, 데이터, 원인 분석, 다음 행동을 묶어 회고를 학습 문서로 남기는 방법을 정리합니다.

> 멘탈 모델: 좋은 회고는 잘못한 사람을 찾는 문서가 아니라, 어떤 사실이 있었고 무엇을 바꿀지 정리하는 다음 프로젝트의 출발 문서입니다.


## 이 글에서 다룰 문제

- 회고가 책임 공방으로 흐르지 않게 하려면 무엇이 필요할까요?
- KPT 형식은 왜 초보 팀에게 특히 유용할까요?
- 데이터는 회고의 어떤 부분을 단단하게 만들어 줄까요?
- Five Whys는 언제 도움이 될까요?
- 다음 행동은 어떤 형식으로 남겨야 실제 실행으로 이어질까요?

## 이 글에서 배우는 내용

- KPT 형식
- 데이터 기반 회고
- Five Whys 기초
- 다음 행동 작성법
- 학습 요약 정리법

## 왜 중요한가

프로젝트는 끝났는데 학습이 남지 않으면 다음 프로젝트도 같은 패턴을 반복하기 쉽습니다. 반대로 잘한 점, 문제, 시도할 점을 구조적으로 남기면 이번 경험이 다음 팀 작업의 출발점이 됩니다.

실무 팀도 스프린트 회고와 포스트모템을 꾸준히 운영합니다. 중요한 것은 감정을 털어놓는 것보다, 어떤 사실이 있었고 다음에 무엇을 바꿀지를 작게라도 정하는 일입니다.

## 한눈에 보는 흐름

![한눈에 보는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/10/10-01-the-flow-at-a-glance.ko.png)
*회고를 다음 프로젝트 입력으로 바꾸는 흐름*

## 실전 문서 예시: 회고 액션 로그

회고가 실제 변화로 이어지려면 다음 행동을 아래처럼 작고 선명하게 적는 편이 좋습니다.

```text
구분 | 내용 | 담당자 | 기한
Keep | 요구사항 변경 기록을 남긴다 | 팀 리드 | 다음 프로젝트 시작 전
Problem | 데모 리허설이 부족해 발표 직전 오류를 발견했다 | 팀 전체 | 회고 시점 기록
Try | 매주 금요일 20분 리허설 슬롯을 고정한다 | QA 담당 | 다음 프로젝트 1주차
Action | 배포 체크리스트 템플릿을 저장소에 추가한다 | 백엔드 담당 | 다음 프로젝트 1주차
```

## 이 문서로 먼저 확인할 것

- 잘한 점, 문제, 시도를 구분해서 적는지 확인합니다.
- 데이터가 없는 주장에는 근거를 더 모읍니다.
- 다음 행동에 담당자와 기한이 있는지 봅니다.
- 다음 프로젝트에서 다시 열어볼 수 있도록 문서를 남깁니다.

## 핵심 용어

- **KPT**: Keep, Problem, Try 세 칸으로 정리하는 회고 방식입니다.
- **5 Whys**: 원인을 다섯 번 정도 연쇄적으로 묻는 방식입니다.
- **action**: 다음에 실제로 실행할 한 단계입니다.
- **data**: 수치로 남긴 근거입니다.
- **learning**: 문서로 남긴 교훈입니다.

## Before / After

**Before**: 감정만 쏟아 놓고 끝냅니다.

**After**: 사실과 다음 행동을 함께 기록합니다.

## 실습: 회고 표

### 1단계 — KPT

```python
kpt = {"keep": [], "problem": [], "try": []}
```

KPT는 구조를 단순하게 유지해 줍니다. 초보 팀일수록 복잡한 형식보다 이 정도가 실용적입니다.

### 2단계 — 데이터

```python
metrics = {"velocity": 12, "bugs": 5, "review_time": 1.5}
```

데이터는 느낌보다 수치로 회고를 붙잡아 줍니다. 속도, 버그 수, 리뷰 시간 같은 지표는 논의를 훨씬 차분하게 만듭니다.

### 3단계 — Five Whys

```python
whys = ["bug_at_demo", "missed_test", "no_ci", "no_template", "first_time"]
```

Five Whys는 누가 잘못했는지보다 왜 이런 조건이 반복됐는지를 보는 데 도움이 됩니다. 원인을 시스템 관점으로 옮겨 주는 도구입니다.

### 4단계 — 다음 행동

```python
actions = [{"who": "A", "what": "add_ci", "by": "next_sprint"}]
```

다음 행동은 담당자와 마감이 함께 있어야 실행으로 이어집니다. 의지가 아니라 구조가 필요합니다.

### 5단계 — 학습 요약

```python
lessons = ["scope_first", "ci_early", "demo_dryrun"]
```

학습 요약은 다음 프로젝트에 그대로 들고 갈 수 있는 문장이어야 합니다. 짧더라도 재사용 가능해야 합니다.

## 이 코드에서 먼저 볼 점

- KPT는 세 칸 구조입니다.
- 데이터는 숫자로 남깁니다.
- 다음 행동에는 담당자와 마감이 있습니다.
- 학습은 재사용 가능한 문장으로 남깁니다.

## 자주 하는 실수 5가지

1. 누가 잘못했는지부터 묻습니다.
2. 감정만 기록합니다.
3. 다음 행동이 없습니다.
4. 데이터가 없습니다.
5. 다음 프로젝트와 연결하지 않습니다.

## 실무에서는 이렇게 이어집니다

실무 팀도 스프린트 회고와 포스트모템을 통해 다음 행동을 정합니다. 좋은 회고는 칭찬이나 비판에서 끝나지 않고, 작은 프로세스 개선으로 이어집니다. 캡스톤에서 이 감각을 익히면 프로젝트를 닫는 방식 자체가 달라집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 사실에서 시작합니다.
- 원인은 개인보다 시스템에서 찾습니다.
- 다음 행동은 작게 쪼갭니다.
- 책임은 팀이 함께 집니다.
- 학습은 반드시 문서화합니다.

## 체크리스트

- [ ] KPT 표가 있습니다.
- [ ] 데이터가 모여 있습니다.
- [ ] Five Whys가 정리되어 있습니다.
- [ ] 세 개 이상의 다음 행동이 있습니다.

## 연습 문제

1. KPT의 의미를 한 줄로 설명해 보세요.
2. Five Whys가 무엇인지 한 줄로 설명해 보세요.
3. next action 형식을 한 줄로 적어 보세요.

## 정리와 다음 글

회고는 프로젝트의 마지막 문서이면서 다음 프로젝트의 첫 문서입니다. KPT, 데이터, 원인 분석, 다음 행동을 함께 남기면 이번 캡스톤의 시행착오가 다음 작업의 자산으로 바뀝니다. 이것으로 Capstone Project 101 시리즈를 마칩니다.

<!-- toc:begin -->
- [캡스톤 프로젝트란 무엇인가](./01-what-is-capstone.md)
- [주제 선정](./02-choosing-a-topic.md)
- [문제 정의](./03-defining-the-problem.md)
- [요구사항 정리](./04-organizing-requirements.md)
- [팀 역할 나누기](./05-splitting-team-roles.md)
- [MVP 설계](./06-designing-the-mvp.md)
- [기술 스택 선택](./07-choosing-the-tech-stack.md)
- [일정 관리](./08-schedule-management.md)
- [발표 자료 만들기](./09-presentation-materials.md)
- **프로젝트 회고 (현재 글)**
<!-- toc:end -->

## 참고 자료

### 공식 문서와 실무 자료

- [Agile Retrospectives](https://pragprog.com/titles/dlret/agile-retrospectives/)
- [The Five Whys](https://en.wikipedia.org/wiki/Five_whys)
- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [Project Retrospectives](https://retrospectives.com/)

Tags: Capstone, Retrospective, Learning, Reflection, Beginner
