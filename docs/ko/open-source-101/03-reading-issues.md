---
series: open-source-101
episode: 3
title: Issue 읽기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - Issues
  - GitHub
  - Triage
  - Beginner
seo_description: GitHub Issue 를 읽고 분류하고 우선순위를 정하는 방법을 정리한 글
last_reviewed: '2026-05-04'
---

# Issue 읽기

> 오픈소스 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *Issue* 를 *어떻게* *읽어야* *기여* 의 *시작점* 이 보일까요?

> *제목, 라벨, 댓글* 을 *순서대로* 읽습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *Issue* 의 *구성 요소*
- *라벨* 시스템
- *good first issue* 찾기
- *재현 절차* 확인
- *댓글 흐름* 따라가기

## 왜 중요한가

*Issue* 를 *오해* 하면 *PR* 도 *틀어집니다*.

## 개념 한눈에 보기

```mermaid
flowchart LR
    T[Title] --> B[Body]
    B --> R[Repro]
    R --> L[Labels]
    L --> C[Comments]
```

## 핵심 용어 정리

- **issue**: *문제* 또는 *제안*.
- **label**: *분류 태그*.
- **triage**: *분류 작업*.
- **repro**: *재현 절차*.
- **assignee**: *담당자*.

## Before/After

**Before**: "*Issue* 가 *뭐* 라는 *건지* *모르겠다*."

**After**: "*제목 → 본문 → 라벨 → 댓글* 순서로 *맥락* 을 *잡는다*."

## 실습: Issue 분석하기

### 1단계 — 제목 읽기

```text
[Bug] login fails on Safari 15
```

### 2단계 — 라벨 확인

```text
labels: bug, good first issue, help wanted
```

### 3단계 — 재현 절차 확인

```markdown
1. open https://example.com/login
2. enter valid credentials
3. click submit
expected: dashboard
actual: 500 error
```

### 4단계 — 댓글 흐름

```text
maintainer: can you share browser version?
reporter: Safari 15.1 on macOS 12
```

### 5단계 — 기여 가능 여부 판단

```text
- 라벨에 good first issue ✓
- 재현 가능 ✓
- 담당자 미지정 ✓
→ 기여 시도
```

## 이 코드에서 주목할 점

- *제목* 은 *요약*.
- *라벨* 은 *맥락*.
- *댓글* 은 *합의*.

## 자주 하는 실수 5가지

1. ***제목* 만 보고 *PR* 을 *연다*.**
2. ***재현 절차* 를 *건너뛴다*.**
3. ***담당자* 가 *있는데* *작업* 한다.**
4. ***라벨* 을 *무시* 한다.**
5. ***댓글* 의 *결정* 을 *놓친다*.**

## 실무에서는 이렇게 쓰입니다

기업 내부 트래커도 *triage rotation* 을 두어 *우선순위* 를 *주간* 으로 정합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *Issue* 는 *합의* 다.
- *라벨* 은 *프로토콜*.
- *재현* 은 *증거*.
- *담당자* 는 *책임*.
- *댓글* 은 *역사* 다.

## 체크리스트

- [ ] *제목* 읽음.
- [ ] *재현 절차* 확인.
- [ ] *라벨* 확인.
- [ ] *담당자* 확인.

## 연습 문제

1. *good first issue* 라벨의 의미 한 줄.
2. *triage* 한 줄 정의.
3. *재현 절차* 가 *없는* *Issue* 의 *위험* 한 줄.

## 정리 및 다음 단계

다음 글은 *PR 만들기* 입니다.

<!-- toc:begin -->
- [오픈소스란 무엇인가](./01-what-is-open-source.md)
- [라이선스 이해하기](./02-understanding-licenses.md)
- **Issue 읽기 (현재 글)**
- PR 만들기 (예정)
- 좋은 README (예정)
- Release 와 Versioning (예정)
- Community 관리 (예정)
- Maintainer 의 역할 (예정)
- 오픈소스 포트폴리오 (예정)
- 내 첫 오픈소스 프로젝트 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Issues docs](https://docs.github.com/en/issues)
- [good first issue](https://github.blog/2020-01-22-how-we-built-good-first-issues/)
- [Triage guide](https://opensource.guide/best-practices/)
- [Issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
