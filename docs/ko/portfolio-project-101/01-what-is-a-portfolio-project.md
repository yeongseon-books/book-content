---
series: portfolio-project-101
episode: 1
title: 포트폴리오 프로젝트란 무엇인가
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Portfolio
  - Career
  - Project
  - Hiring
  - Beginner
seo_description: 포트폴리오 프로젝트의 정의와 채용 시 평가 기준을 정리한 글
last_reviewed: '2026-05-04'
---

# 포트폴리오 프로젝트란 무엇인가

> 포트폴리오 프로젝트 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *과제* 와 *포트폴리오 프로젝트* 의 *진짜 차이* 는 무엇일까요?

> *문제* 와 *결정 근거* 가 *기록* 되어 있는지 여부입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *포트폴리오 프로젝트* 의 정의
- 면접관이 *진짜* 보는 것
- *학교 과제* 와의 차이
- *최소 구성 요소*
- *평가 기준*

## 왜 중요한가

*포트폴리오* 는 *경험* 을 *증명* 하는 가장 빠른 도구입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    P[Problem] --> S[Solution]
    S --> C[Code]
    C --> D[Deploy]
    D --> R[README]
```

## 핵심 용어 정리

- **portfolio**: *공개된 작업물*.
- **case study**: *문제 - 해결 - 결과*.
- **README**: *입구* 문서.
- **demo**: *동작* 시연.
- **decision log**: *결정* 기록.

## Before/After

**Before**: *코드* 만 GitHub 에 올린다.

**After**: *문제 + 데모 + README* 가 함께 있다.

## 실습: 최소 포트폴리오

### 1단계 — 프로젝트 정의

```python
project = {"name": "task-tracker", "problem": "팀 일정 분실"}
```

### 2단계 — 데모 URL

```python
demo_url = "https://demo.example.com"
```

### 3단계 — README 골격

```python
sections = ["problem", "demo", "stack", "run", "next"]
```

### 4단계 — 결정 기록

```python
decisions = [{"why": "FastAPI", "trade": "less_admin"}]
```

### 5단계 — 한 줄 소개

```python
pitch = "팀 일정 분실을 해결하는 미니 SaaS"
```

## 이 코드에서 주목할 점

- *프로젝트* 는 *문제* 로 시작.
- *데모* 는 *URL*.
- *README* 는 *5 섹션*.

## 자주 하는 실수 5가지

1. ***스크린샷* 만 있다.**
2. ***README* 가 한 줄.**
3. ***결정 근거* 가 없다.**
4. ***데모* 가 *내려가* 있다.**
5. ***기능 자랑* 만 한다.**

## 실무에서는 이렇게 쓰입니다

채용 담당자는 *60 초* 안에 *문제 - 해결 - 결과* 를 찾습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *문제* 가 *제일* 중요.
- *결정 근거* 가 *실력*.
- *데모* 는 *살아 있어야*.
- *README* 가 *입구*.
- *작은 범위* 로 *완성*.

## 체크리스트

- [ ] *문제 한 줄*.
- [ ] *데모 URL*.
- [ ] *README* 5섹션.
- [ ] *결정 기록*.

## 연습 문제

1. *포트폴리오 프로젝트* 정의 한 줄.
2. *데모* 의 역할 한 줄.
3. *결정 기록* 의 의미 한 줄.

## 정리 및 다음 단계

다음 글은 *좋은 프로젝트의 조건* 입니다.

<!-- toc:begin -->
- **포트폴리오 프로젝트란 무엇인가 (현재 글)**
- 좋은 프로젝트의 조건 (예정)
- README 작성 (예정)
- 데모 만들기 (예정)
- 배포하기 (예정)
- 테스트와 문서화 (예정)
- 기술적 의사결정 기록 (예정)
- 블로그 글로 정리하기 (예정)
- 면접에서 설명하기 (예정)
- 포트폴리오 개선 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub README Best Practices](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Portfolio for Engineers - Cal Newport](https://calnewport.com/)
- [Show Your Work - Austin Kleon](https://austinkleon.com/show-your-work/)
- [Hiring Without Whiteboards](https://github.com/poteto/hiring-without-whiteboards)
