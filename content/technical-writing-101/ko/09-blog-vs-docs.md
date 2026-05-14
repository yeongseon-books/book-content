---
episode: 9
language: ko
last_reviewed: '2026-05-12'
seo_description: 블로그와 공식 문서의 차이를 Diátaxis 모델로 분석하고 각 역할과 최신성 유지 전략을 함께 정리합니다.
series: technical-writing-101
status: publish-ready
tags:
- TechnicalWriting
- Blog
- Documentation
- Diataxis
- Beginner
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: 블로그와 문서 차이
---

# 블로그와 문서 차이

이 글은 Technical Writing 101 시리즈의 9번째 글입니다.

## 이 글에서 다룰 문제

- 블로그와 공식 문서는 왜 서로 섞이면 안 될까요?
- 둘의 생명주기와 소유권은 무엇이 다를까요?
- Diátaxis의 네 구역은 이 차이를 어떻게 설명해 줄까요?
- 블로그와 문서를 연결하되 책임은 어떻게 나눠야 할까요?

## 이 글에서 배울 것

- Diátaxis의 네 구역
- 블로그와 문서의 생명주기
- 블로그가 잘하는 일
- 문서가 잘하는 일
- 둘을 연결하는 방법

## 왜 중요한가

글의 종류가 섞이면 독자가 길을 잃습니다. 블로그를 공식 문서처럼 인용하거나, 공식 문서를 개인 경험담처럼 쓰는 순간 신뢰의 기준이 흐려집니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 블로그는 경험과 해석을 담고, 문서는 지금 따라야 할 기준을 담습니다. 둘은 연결할 수 있지만 서로를 대신하면 안 됩니다.

```mermaid
flowchart LR
    Tut[Tutorial] --> Doc[Documentation]
    HT[How-to] --> Doc
    Ref[Reference] --> Doc
    Exp[Explanation] --> Blog[Blog]
```

## 핵심 용어

- **Diátaxis**: 네 구역 문서 모델입니다.
- **lifecycle**: 생명주기입니다.
- **freshness**: 최신성입니다.
- **canonical**: 정본입니다.
- **archive**: 아카이브입니다.

## Before / After

**Before**: A blog post gets cited as official documentation.

**After**: Blogs hold experience; docs hold truth.

## 실습: 네 구역에 배치해 보기

### 1단계 — Tutorial

```python
tutorial = "First-time learning"
```

### 2단계 — How-to

```python
how_to = "Solving a specific problem"
```

### 3단계 — Reference

```python
reference = "API specification"
```

### 4단계 — Explanation

```python
explanation = "Why a design was chosen"
```

### 5단계 — 블로그와 문서

```python
blog = "My experience and opinion"
docs = "The team's official truth"
```

## 이 코드에서 먼저 볼 점

- 블로그는 경험을 담습니다.
- 문서는 기준을 담습니다.
- 둘은 네 구역으로 더 잘 나눌 수 있습니다.

## 자주 하는 실수 5가지

1. **블로그를 공식 문서처럼 인용합니다.**
2. **문서를 오래된 채로 둡니다.**
3. **버전을 적지 않습니다.**
4. **아카이브 정책이 없습니다.**
5. **정본 링크가 없습니다.**

## 실무에서는 이렇게 드러납니다

좋은 엔지니어링 팀은 블로그와 문서를 분리해 운영하고, 문서는 코드와 함께 버전 관리합니다. 블로그는 경험과 배경을 남기고, 문서는 팀의 현재 진실을 유지합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 블로그는 지난 결정과 경험을 담습니다.
- 문서는 살아 있는 진실입니다.
- 오래된 글은 아카이브로 보냅니다.
- 정본은 문서에 둡니다.
- 블로그는 문서를 가리킵니다.

## 체크리스트

- [ ] 네 구역 매핑이 있는가
- [ ] 최신성 기준이 드러나는가
- [ ] 정본 링크가 있는가
- [ ] 아카이브 정책이 있는가

## 연습 문제

1. Diátaxis의 네 구역을 한 줄로 적어 보세요.
2. canonical의 뜻을 한 줄로 적어 보세요.
3. freshness의 뜻을 한 줄로 적어 보세요.

## 정리

블로그와 문서는 같은 기술을 다뤄도 역할이 다릅니다. 블로그는 경험과 배경을 남기고, 문서는 지금 따라야 할 기준을 유지합니다. 둘을 링크로 연결하는 것은 좋지만, 서로를 대신하게 두면 안 됩니다. 다음 글에서는 발행 직전에 무엇을 어떻게 점검해야 하는지 시리즈 마지막 정리로 이어 가겠습니다.

<!-- toc:begin -->
- [기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [독자 정의하기](./02-defining-the-reader.md)
- [제목과 구조 잡기](./03-title-and-structure.md)
- [개념 설명하기](./04-explaining-concepts.md)
- [예제 코드 설명하기](./05-explaining-example-code.md)
- [그림과 표 사용하기](./06-using-figures-and-tables.md)
- [README 작성하기](./07-writing-the-readme.md)
- [튜토리얼 작성하기](./08-writing-tutorials.md)
- **블로그와 문서 차이 (현재 글)**
- 발행 전 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [Diátaxis - Procida](https://diataxis.fr/)
- [Docs Like Code - Anne Gentle](https://www.docslikecode.com/)
- [Docs as Code - Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)
- [Stripe Engineering Blog](https://stripe.com/blog/engineering)

Tags: TechnicalWriting, Blog, Documentation, Diataxis, Beginner