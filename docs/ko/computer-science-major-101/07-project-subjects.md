---
series: computer-science-major-101
episode: 7
title: 프로젝트 과목
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - CS
  - Project
  - Capstone
  - Teamwork
  - Beginner
seo_description: 프로젝트 과목의 목적, 팀 구성, 기획, 산출물, 발표까지 전체 흐름을 정리한 글
last_reviewed: '2026-05-04'
---

# 프로젝트 과목

> 컴퓨터학과 전공 학습 가이드 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *프로젝트* 과목이 *왜* *전공 후반* 의 *핵심* 일까요?

> *지식* 을 *문제* 에 *적용* 해서 *증거* 를 만들기 때문입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 프로젝트의 *목적*
- *팀* 구성
- *기획* 과 *범위*
- *산출물* 정리
- *발표* 의 의미

## 왜 중요한가

*포트폴리오* 의 *시작* 이 *전공 프로젝트* 인 경우가 많습니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    P[Plan] --> D[Design]
    D --> I[Implement]
    I --> T[Test]
    T --> S[Show]
```

## 핵심 용어 정리

- **scope**: *범위*.
- **MVP**: *최소* 기능.
- **demo**: *시연*.
- **stakeholder**: *이해관계자*.
- **retrospective**: *회고*.

## Before/After

**Before**: *과제* 처럼 본다.

**After**: *작은 제품* 으로 본다.

## 실습: 프로젝트 미니 플랜

### 1단계 — 문제 정의

```python
problem = "강의 시간표 충돌 검사기"
```

### 2단계 — 사용자

```python
users = ["student", "advisor"]
```

### 3단계 — 핵심 기능

```python
features = ["upload", "detect_conflict", "notify"]
```

### 4단계 — 일정

```python
weeks = {"plan": 1, "build": 6, "test": 2, "demo": 1}
```

### 5단계 — 위험

```python
risks = ["scope_creep", "team_sync", "data_format"]
```

## 이 코드에서 주목할 점

- *문제* 가 *프로젝트* 의 *시작*.
- *사용자* 가 *기능* 을 결정.
- *일정* 이 *현실* 을 만든다.

## 자주 하는 실수 5가지

1. ***기획서* 없이 *바로 코드*.**
2. ***팀 역할* 분리가 모호.**
3. ***주간 회의* 없음.**
4. ***Git 컨벤션* 합의 안 함.**
5. ***회고* 없이 *발표* 로 끝.**

## 실무에서는 이렇게 쓰입니다

스타트업의 *MVP* 는 *전공 프로젝트* 와 거의 *같은 형태* 입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *작게* 시작.
- *자주* 보여 준다.
- *피드백* 을 모은다.
- *문서* 를 남긴다.
- *회고* 를 쓴다.

## 체크리스트

- [ ] *문제* 한 줄.
- [ ] *기능* 목록.
- [ ] *일정* 표.
- [ ] *위험* 표.

## 연습 문제

1. *MVP* 한 줄 정의.
2. *데모* 한 줄 정의.
3. *회고* 의 의미 한 줄.

## 정리 및 다음 단계

다음 글은 *전공 공부 방법* 입니다.

<!-- toc:begin -->
- [컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [1학년 과목 이해하기](./02-first-year-subjects.md)
- [자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [시스템 과목 이해하기](./04-systems-subjects.md)
- [데이터베이스와 네트워크](./05-database-and-network.md)
- [AI와 데이터사이언스](./06-ai-and-data-science.md)
- **프로젝트 과목 (현재 글)**
- 전공 공부 방법 (예정)
- 포트폴리오로 연결하기 (예정)
- 졸업 전 갖춰야 할 역량 (예정)
<!-- toc:end -->

## 참고 자료

- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Mythical Man-Month](https://www.oreilly.com/library/view/mythical-man-month-the/0201835959/)
- [Atlassian Project Management Guide](https://www.atlassian.com/agile/project-management)
- [GitHub Project Boards](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
