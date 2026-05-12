---
series: clean-code-101
episode: 10
title: 좋은 코드 리뷰 기준
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - CleanCode
  - CodeReview
  - PullRequest
  - Quality
  - Collaboration
seo_description: 클린 코드 관점에서의 PR 리뷰 체크리스트, 좋은 리뷰 코멘트, 협업 원칙을 정리합니다.
last_reviewed: '2026-05-11'
---

# 좋은 코드 리뷰 기준

클린 코드 관점에서의 PR 리뷰 체크리스트, 좋은 리뷰 코멘트, 협업 원칙을 정리합니다.

이 글은 Clean Code 101 시리즈의 10번째 글입니다.

> Clean Code 101 시리즈 (10/10)


## 이 글에서 다룰 문제

리뷰는 코드 품질을 지키는 마지막 관문이면서, 팀이 함께 배우는 가장 현실적인 통로이기도 합니다.

> 리뷰는 결함을 잡는 자리가 아니라 함께 더 나은 답을 찾는 자리다.

## 전체 흐름
```mermaid
flowchart LR
    A["작성자: 작은 PR"] --> B["자동 검사"]
    B --> C["리뷰어: 의도/구조"]
    C --> D["빠른 피드백"]
    D --> E["머지"]
```

단순 반복 검사는 자동화에 맡기고, 사람은 의도와 설계를 봐야 합니다.

## Before/After

**Before**

```text
"이 함수 너무 길어요."
```

**After**

```text
"order_total이 60줄입니다. subtotal/with_coupon/with_member로
나누면 본문이 목차처럼 읽힙니다 (ep03, ep05 참고).
선택: (a) 이번 PR에서 분리 (b) 후속 PR 이슈로."
```

좋은 코멘트는 바로 행동으로 옮길 수 있을 만큼 구체적입니다.

## 리뷰를 견고하게 만드는 5단계

### 1단계 — 자동화로 줄이기

```yaml
# 예시 파일: 1_ci.yml
- run: ruff check .
- run: black --check .
- run: pytest -q
```

스타일, 포맷, 기본 테스트는 사람이 직접 판정하지 않도록 자동화하는 편이 좋습니다.

### 2단계 — PR을 작게

```text
# 예시 파일: 2_small_pr.txt
권장: < 400 lines diff, 1 책임
```

작은 PR이 빠르고 정확한 리뷰의 출발점입니다.

### 3단계 — 의도부터 읽기

```markdown
<!-- 3_pr_template.md -->
## What
무엇이 바뀌나
## Why
왜 바꾸나 (이슈 링크)
## How
어떻게 검증했나 (테스트/스크린샷)
## Risk
무엇이 위험할 수 있나
```

설명이 빠진 PR은 리뷰어가 맥락을 추측하게 만듭니다.

### 4단계 — 행동 가능한 코멘트

```text
# 예시 파일: 4_comment.txt
NIT: 사소함 (선택)
SUGG: 제안 (이번 PR 권장)
MUST: 머지 전에 반드시
QUESTION: 이해 확인
```

이런 라벨은 코멘트의 우선순위를 빠르게 구분하게 도와줍니다.

### 5단계 — 회고로 학습

```text
# 예시 파일: 5_retro.txt
- 자주 반복되는 코멘트는 lint/문서로 옮긴다.
- 큰 PR은 작게 쪼개는 가이드를 만든다.
- 리뷰 시간을 측정해서 개선 대상으로 본다.
```

리뷰 프로세스 자체도 계속 개선 대상이라고 보는 태도가 중요합니다.

## 이 코드에서 주목할 점

- 자동화가 끝낼 수 있는 일은 사람이 반복하지 않습니다.
- 우선순위 라벨이 있으면 코멘트 해석 비용이 줄어듭니다.
- PR 설명은 변경의 맥락과 위험을 빠르게 전달합니다.

## 자주 하는 실수 5가지

1. **거대 PR.** 어차피 누구도 끝까지 못 봅니다.
2. **취향 코멘트.** 가치 충돌만 남깁니다.
3. **MUST를 남발.** 신뢰가 떨어집니다.
4. **자동화로 가능한 일을 사람이 봄.** 시간 낭비.
5. **승인만 하고 학습 기록 없음.** 같은 실수 반복.

## 실무에서는 이렇게 쓰입니다

좋은 팀은 평균 PR 크기, 첫 응답 시간, 머지까지 걸리는 시간을 계속 봅니다. 이런 지표가 나빠지면 개인의 성실함만 탓하지 않고 리뷰 프로세스 자체를 손봅니다.

## 체크리스트

- [ ] PR이 한 가지 책임만 다루는가?
- [ ] CI가 녹색인가?
- [ ] 설명(What/Why/How/Risk)이 충분한가?
- [ ] 코멘트가 우선순위 라벨을 가지나?
- [ ] 반복 코멘트를 자동화로 옮길 수 있나?

## 정리 및 다음 단계

좋은 리뷰는 결국 좋은 코드를 비추는 거울입니다. 이 시리즈에서 다룬 이름, 함수, 분기, 중복, 오류, 주석, 테스트, 리팩토링, 리뷰는 모두 다음 사람이 더 쉽게 바꿀 수 있는 코드를 만들기 위한 원칙이었습니다. 다음 시리즈에서는 이 관점을 더 큰 단위인 소프트웨어 설계로 확장해 보겠습니다.

<!-- toc:begin -->
- [Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [이름 짓기](./02-naming.md)
- [함수 작게 만들기](./03-small-functions.md)
- [조건문 줄이기](./04-simplifying-conditionals.md)
- [중복 제거](./05-removing-duplication.md)
- [오류 처리](./06-error-handling.md)
- [주석과 문서화](./07-comments-and-docs.md)
- [테스트 가능한 코드](./08-testable-code.md)
- [리팩토링 기초](./09-refactoring-basics.md)
- **좋은 코드 리뷰 기준 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Google Engineering Practices — Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [Best Kept Secrets of Peer Code Review (Smart Bear)](https://smartbear.com/resources/ebooks/best-kept-secrets-of-peer-code-review/)
- [Microsoft Engineering Fundamentals — Code Review](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/)

Tags: Computer Science, CleanCode, CodeReview, PullRequest, Quality, Collaboration
