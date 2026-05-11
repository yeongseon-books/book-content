---
series: capstone-project-101
episode: 7
title: 기술 스택 선택
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
  - TechStack
  - Decision
  - Architecture
  - Beginner
seo_description: 캡스톤 기술 스택을 친숙도, 학습 비용, 운영 부담 기준으로 선택하는 방법을 정리한 글
last_reviewed: '2026-05-04'
---

# 기술 스택 선택

> 캡스톤 프로젝트 101 시리즈 (7/10)


## 이 글에서 다룰 문제

*올바른 선택* 이 *집중* 을 만듭니다.

## 전체 흐름
```mermaid
flowchart LR
    R[Requirements] --> F[Familiar]
    F --> L[Learning Cost]
    L --> O[Ops]
    O --> D[Decide]
```

## Before/After

**Before**: *최신* 스택을 무조건 쓴다.

**After**: *친숙도 + 비용* 기준으로 고른다.

## 결정 표

### 1단계 — 후보 정리

```python
candidates = ["FastAPI", "Flask", "Django"]
```

### 2단계 — 친숙도 평가

```python
familiar = {"FastAPI": 4, "Flask": 5, "Django": 2}
```

### 3단계 — 학습 비용

```python
learning_cost = {"FastAPI": 2, "Flask": 1, "Django": 4}
```

### 4단계 — 운영 부담

```python
ops = {"FastAPI": 2, "Flask": 1, "Django": 3}
```

### 5단계 — 점수 합산

```python
score = {k: familiar[k] - learning_cost[k] - ops[k] for k in candidates}
```

## 이 코드에서 주목할 점

- *점수* 는 *친숙도 - 비용*.
- *대안* 은 *3개* 이내.
- *결정 기록* 은 *문서*.

## 자주 하는 실수 5가지

1. ***인기* 만 본다.**
2. ***친숙도* 를 무시한다.**
3. ***운영* 비용을 잊는다.**
4. ***결정 기록* 이 없다.**
5. ***대안* 비교가 없다.**

## 실무에서는 이렇게 쓰입니다

회사 팀도 *ADR* 로 결정 이유를 남깁니다.

## 체크리스트

- [ ] *후보 3개*.
- [ ] *친숙도* 점수.
- [ ] *학습 비용*.
- [ ] *결정 기록*.

## 정리 및 다음 단계

다음 글은 *일정 관리* 입니다.

<!-- toc:begin -->
- [캡스톤 프로젝트란 무엇인가](./01-what-is-capstone.md)
- [주제 선정](./02-choosing-a-topic.md)
- [문제 정의](./03-defining-the-problem.md)
- [요구사항 정리](./04-organizing-requirements.md)
- [팀 역할 나누기](./05-splitting-team-roles.md)
- [MVP 설계](./06-designing-the-mvp.md)
- **기술 스택 선택 (현재 글)**
- 일정 관리 (예정)
- 발표 자료 만들기 (예정)
- 프로젝트 회고 (예정)
<!-- toc:end -->

## 참고 자료

- [Architecture Decision Records](https://adr.github.io/)
- [Choose Boring Technology - Dan McKinley](https://boringtechnology.club/)
- [The Twelve-Factor App](https://12factor.net/)
- [Tech Radar - Thoughtworks](https://www.thoughtworks.com/radar)

Tags: Capstone, TechStack, Decision, Architecture, Beginner
