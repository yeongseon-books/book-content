---
series: portfolio-project-101
episode: 7
title: 기술적 의사결정 기록
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
  - ADR
  - Decision
  - Architecture
  - Beginner
seo_description: 포트폴리오 프로젝트의 기술 결정 근거를 ADR로 기록하는 방법을 정리한 글
last_reviewed: '2026-05-11'
---

# 기술적 의사결정 기록

> 포트폴리오 프로젝트 101 시리즈 (7/10)


## 이 글에서 다룰 문제

결정 기록은 판단력을 보여 주는 증거입니다.

## 전체 흐름
```mermaid
flowchart LR
    C[Context] --> O[Options]
    O --> D[Decision]
    D --> R[Result]
    R --> N[Next]
```

## Before/After

**Before**: 왜 그렇게 했는지 설명이 없습니다.

**After**: 왜 그렇게 결정했는지 문서에 남아 있습니다.

## ADR 표

### 1단계 — 컨텍스트

```python
context = "팀 1인, 2주 마감, Python 친숙"
```

### 2단계 — 대안

```python
options = ["FastAPI", "Flask", "Django"]
```

### 3단계 — 결정

```python
decision = "FastAPI"
```

### 4단계 — 근거

```python
why = ["async", "type_hints", "swagger_auto"]
```

### 5단계 — 결과

```python
result = {"build_time": "fast", "trade": "smaller_ecosystem"}
```

## 이 코드에서 주목할 점

- 컨텍스트를 맨 위에 두어 판단 배경을 먼저 보여 줍니다.
- 대안은 최소 두 개 이상 비교해야 설득력이 생깁니다.
- 결과는 좋았던 점과 아쉬운 점을 솔직하게 적어야 합니다.

## 자주 하는 실수 5가지

1. 대안 비교 없이 바로 결론만 적습니다.
2. 근거가 유행이나 취향 수준에서 멈춥니다.
3. 결과를 적지 않아 나중에 평가할 수 없습니다.
4. ADR을 코드 가까이에 두지 않아 찾기 어렵습니다.
5. 버전 관리가 없어 변경 히스토리를 따라가기 어렵습니다.

## 실무에서는 이렇게 쓰입니다

회사 팀도 `docs/adr/0001-...md` 형태로 ADR을 관리합니다.

## 체크리스트

- [ ] ADR 폴더를 만들었다.
- [ ] ADR을 최소 3개 이상 남겼다.
- [ ] 대안, 결정, 결과를 모두 적었다.
- [ ] 번호를 붙여 순서를 관리한다.

## 정리 및 다음 단계

다음 글은 블로그 글로 정리하기입니다.

<!-- toc:begin -->
- [포트폴리오 프로젝트란 무엇인가](./01-what-is-a-portfolio-project.md)
- [좋은 프로젝트의 조건](./02-traits-of-a-good-project.md)
- [README 작성](./03-writing-the-readme.md)
- [데모 만들기](./04-building-the-demo.md)
- [배포하기](./05-deploying-the-project.md)
- [테스트와 문서화](./06-tests-and-documentation.md)
- **기술적 의사결정 기록 (현재 글)**
- 블로그 글로 정리하기 (예정)
- 면접에서 설명하기 (예정)
- 포트폴리오 개선 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [Architecture Decision Records](https://adr.github.io/)
- [ADR Tools - Nat Pryce](https://github.com/npryce/adr-tools)
- [Documenting Architecture Decisions - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ThoughtWorks Tech Radar](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)

Tags: Portfolio, ADR, Decision, Architecture, Beginner
