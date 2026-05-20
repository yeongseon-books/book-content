---
series: clean-code-101
episode: 10
title: "Clean Code 101 (10/10): 좋은 코드 리뷰 기준"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: 좋은 코드 리뷰 기준과 실행 가능한 리뷰 코멘트 작성법을 익혀 팀의 개발 생산성과 코드 품질을 높이는 방법을 제안합니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (10/10): 좋은 코드 리뷰 기준

좋은 코드는 작성 단계에서만 만들어지지 않고, 리뷰 단계에서 팀의 기준으로 다시 다듬어집니다.

이 글은 Clean Code 101 시리즈의 마지막 글입니다.

여기서는 지금까지 다룬 이름, 함수, 분기, 중복, 오류, 테스트, 리팩토링 관점을 실제 PR 리뷰 기준으로 어떻게 묶을지 정리하겠습니다.

## 먼저 던지는 질문

- 리뷰 가능한 PR 크기는 어느 정도일까요?
- Clean Code 관점의 리뷰 체크리스트는 무엇일까요?
- 좋은 리뷰 코멘트는 어떤 형태를 가져야 할까요?

## 큰 그림

![Clean Code 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/10/10-01-concept-at-a-glance.ko.png)

*Clean Code 101 10장 흐름 개요*

이 그림에서는 좋은 코드 리뷰 기준를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 좋은 코드 리뷰 기준의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

코드 리뷰는 마지막 품질 게이트이면서 동시에 가장 큰 학습 채널입니다. 작은 PR, 충분한 맥락, 실행 가능한 코멘트가 갖춰지면 리뷰는 단순한 승인 절차가 아니라 팀의 기준을 맞추는 시간으로 바뀝니다.

반대로 큰 PR, 취향 위주의 코멘트, 자동화로도 잡을 수 있는 반복 지적이 쌓이면 리뷰는 금방 피로한 의식이 됩니다. 그래서 좋은 리뷰 기준은 코드만이 아니라 리뷰 프로세스 자체를 설계하는 문제이기도 합니다.

## 한눈에 보는 개념

자동화는 잡무를 처리하고, 사람은 의도와 구조를 봐야 리뷰가 가치 있는 시간이 됩니다.

## 핵심 용어

- **PR (Pull Request)**: 하나의 변경 단위입니다.
- **Review comment**: 변경에 대한 의견과 제안입니다.
- **Approval**: 병합 가능하다는 신호입니다.
- **CI (Continuous Integration)**: 자동 빌드와 테스트입니다.
- **Style guide**: 팀이 공유하는 규칙 모음입니다.

## Before/After

**Before**

```text
"This function is too long."
```

**After**

```text
"order_total is 60 lines. Splitting into subtotal/with_coupon/with_member
would make the body read like a table of contents (see ep03, ep05).
Options: (a) split in this PR, (b) follow-up PR with an issue link."
```

좋은 리뷰 코멘트는 실행 가능해야 합니다. 무엇이 문제인지, 왜 문제인지, 어떤 방향이 가능한지까지 보여 주어야 작성자가 바로 판단할 수 있습니다.

## 실전 적용: 탄탄한 리뷰 프로세스 다섯 단계

### Step 1 — Push toil into automation

```yaml
# 1_ci.yml
- run: ruff check .
- run: black --check .
- run: pytest -q
```

스타일, 포맷, 기본 테스트는 사람 눈앞에 오기 전에 끝나야 합니다. 사람이 자동화가 할 일을 대신하면 리뷰의 질이 바로 떨어집니다.

### Step 2 — Keep PRs small

```text
# 2_small_pr.txt
Recommended: under 400 lines diff, one responsibility
```

작은 PR은 빠른 리뷰의 전제입니다. 한 책임만 담긴 PR이어야 리뷰어도 기준을 선명하게 적용할 수 있습니다.

### Step 3 — Read intent first

```markdown
<!-- 3_pr_template.md -->
## What
What is changing
## Why
Why it changes (issue link)
## How
How it was verified (tests/screenshots)
## Risk
What could go wrong
```

맥락 없는 PR은 제대로 리뷰할 수 없습니다. 리뷰어는 코드보다 먼저 의도와 위험을 읽어야 전체 구조를 올바르게 판단할 수 있습니다.

### Step 4 — Write actionable comments

```text
# 4_comment.txt
NIT: minor (optional)
SUGG: suggestion (recommended for this PR)
MUST: must address before merge
QUESTION: clarification
```

우선순위 라벨이 붙은 코멘트는 불필요한 마찰을 줄입니다. 무엇이 선택 사항이고 무엇이 병합 전 필수인지 분명해야 합니다.

### Step 5 — Learn through retrospectives

```text
# 5_retro.txt
- Move repeated comments into lints/docs.
- Build a guide for splitting big PRs.
- Measure review time and treat it as an improvement target.
```

반복되는 리뷰 코멘트는 프로세스 개선 신호입니다. 같은 지적이 계속 나온다면 사람을 탓하기보다 자동화나 가이드로 옮겨야 합니다.

## 검증 방법

```bash
ruff check .
python -m pytest -q
GIT_PAGER=cat git diff --stat HEAD~1..HEAD
```

**기대 결과**

- 자동화가 처리할 문제는 PR에 올라오기 전에 정리됩니다.
- diff 크기와 검증 결과가 리뷰 설명과 맞아야 합니다.

## 실패하기 쉬운 지점

- 리뷰 코멘트가 취향과 필수를 구분하지 못합니다.
- 반복 지적이 lint나 템플릿으로 옮겨가지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 자동화가 끝낸 일은 사람이 다시 검사하지 않습니다.
- 코멘트는 우선순위 라벨을 가집니다.
- PR 설명이 변경 맥락을 충분히 제공합니다.

## 자주 하는 실수 5가지

1. **거대한 PR 만들기.** 아무도 끝까지 제대로 읽지 못합니다.
2. **취향 위주의 코멘트 남기기.** 마찰만 키웁니다.
3. **MUST를 남용하기.** 신뢰가 빠르게 떨어집니다.
4. **자동화 가능한 일을 사람이 하기.** 시간 낭비입니다.
5. **학습 기록 없이 승인하기.** 같은 실수가 반복됩니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 평균 PR 크기, 첫 응답까지 걸린 시간, 병합 리드 타임을 측정합니다. 숫자가 나빠지면 개발자 개인을 탓하기보다 리뷰 프로세스 자체를 리팩토링합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작은 PR을 강하게 지지합니다.
- 자동화가 할 수 있는 일은 직접 하지 않습니다.
- 코드를 보기 전에 의도를 읽습니다.
- 우선순위가 있는 실행 가능한 코멘트를 남깁니다.
- 리뷰 시간 자체도 하나의 지표로 봅니다.

## 체크리스트

- [ ] PR이 한 가지 책임만 다루는가?
- [ ] CI가 초록인가?
- [ ] 설명(What/Why/How/Risk)이 충분한가?
- [ ] 코멘트에 우선순위 라벨이 있는가?
- [ ] 반복 코멘트를 자동화로 옮길 수 있는가?

## 연습 문제

1. 팀의 평균 PR 크기를 측정하고 절반으로 줄이는 실험을 해 보세요.
2. 자주 반복되는 코멘트 세 개를 lint 규칙으로 바꿔 보세요.
3. PR 템플릿을 도입하고 한 달 뒤 회고를 진행해 보세요.

## 정리 및 다음 단계

좋은 리뷰는 Clean Code의 거울입니다. 이름, 함수, 분기, 중복, 오류, 주석, 테스트, 리팩토링, 리뷰까지 이 시리즈의 모든 주제는 결국 다음 사람이 더 쉽게 바꿀 수 있는 코드를 향합니다.

## 처음 질문으로 돌아가기

- **리뷰 가능한 PR 크기는 어느 정도일까요?**
  - 본문의 기준은 좋은 코드 리뷰 기준를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Clean Code 관점의 리뷰 체크리스트는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **좋은 리뷰 코멘트는 어떤 형태를 가져야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- [Clean Code 101 (6/10): 오류 처리](./06-error-handling.md)
- [Clean Code 101 (7/10): 주석과 문서화](./07-comments-and-docs.md)
- [Clean Code 101 (8/10): 테스트 가능한 코드](./08-testable-code.md)
- [Clean Code 101 (9/10): 리팩토링 기초](./09-refactoring-basics.md)
- **좋은 코드 리뷰 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google Engineering Practices — Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [Best Kept Secrets of Peer Code Review (Smart Bear)](https://smartbear.com/resources/ebooks/best-kept-secrets-of-peer-code-review/)
- [Microsoft Engineering Fundamentals — Code Review](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/)
- [Google engineering practices — code review](https://google.github.io/eng-practices/review/)
Tags: Computer Science, CleanCode, CodeReview, PullRequest, Quality, Collaboration
