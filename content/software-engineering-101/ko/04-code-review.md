---
series: software-engineering-101
episode: 4
title: 코드 리뷰
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
  - SoftwareEngineering
  - CodeReview
  - PullRequest
  - Collaboration
  - Quality
seo_description: 코드 리뷰의 목적, PR 작성법, 리뷰어가 보는 항목, 자주 하는 실수를 정리합니다.
last_reviewed: '2026-05-12'
---

# 코드 리뷰

코드 리뷰는 많은 팀에서 가장 자주 하는 협업 작업입니다. 그런데 동시에 가장 쉽게 형식적인 절차로 변하기도 합니다. 작성자는 빨리 머지하고 싶고, 리뷰어는 바쁘고, CI는 이미 통과했고, 화면에는 수백 줄의 diff가 열려 있습니다. 이런 상황에서 리뷰는 결함도 못 잡고 지식도 못 나누는 단계로 밀려나기 쉽습니다.

좋은 코드 리뷰는 단순히 버그를 찾는 자리가 아닙니다. 이 변경이 왜 필요한지, 시스템 경계에 어떤 영향을 주는지, 팀이 이 코드를 앞으로도 이해할 수 있는지 확인하는 과정입니다. 그래서 리뷰는 판결문이 아니라 합의 과정에 더 가깝습니다.

이 글은 Software Engineering 101 시리즈의 네 번째 글입니다. 여기서는 코드 리뷰의 실제 목적, 리뷰하기 쉬운 PR을 만드는 방법, 리뷰어가 보는 신호, 그리고 자동화가 대신해야 할 일을 정리합니다.

## 이 글에서 다룰 문제

- 코드 리뷰는 결함 탐지와 지식 공유 중 무엇이 더 중요할까요?
- 리뷰하기 쉬운 PR은 어떻게 만들 수 있을까요?
- 리뷰어는 실제로 어떤 항목을 먼저 볼까요?
- 코멘트 톤과 태그는 왜 중요할까요?
- 자동화로 치울 수 있는 일과 사람이 직접 봐야 하는 일은 어떻게 나뉠까요?

> 리뷰는 판정이 아니라 합의입니다. 그런데 서투르게 운영하면 결함도 놓치고 지식도 남기지 못합니다.

## 왜 중요한가

팀 안에 특정 모듈을 한 사람만 이해하는 상태가 길어지면 조직은 매우 약해집니다. 그 사람이 휴가를 가거나 퇴사하는 순간 변경 속도가 떨어지고, 사고 대응도 느려집니다. 코드 리뷰는 이런 지식 편중을 줄이는 가장 일상적인 장치입니다.

또한 리뷰는 테스트와 자동화가 걸러내지 못하는 판단을 다룹니다. 이름이 의도를 드러내는지, 경계가 자연스러운지, 요구사항과 구현이 맞는지, 운영 리스크가 숨어 있지 않은지 같은 질문은 아직 사람의 몫입니다. 그래서 리뷰 시간이 길어지는 것이 문제가 아니라, 사람이 판단해야 할 것에 집중하지 못하는 상태가 문제입니다.

## 한눈에 보는 흐름

```mermaid
flowchart LR
    A["Author: PR"] --> B["Automated checks"]
    B --> C["Reviewer comments"]
    C --> D["Revise or discuss"]
    D --> E["Approve and merge"]
```

형식 검사와 테스트는 기계가 맡고, 사람은 의도와 판단을 봐야 리뷰 품질이 올라갑니다.

## 핵심 용어

- **PR**: 변경 단위이자 토론 공간입니다.
- 리뷰어: 코드를 평가하는 사람이 아니라 책임을 함께 지는 동료입니다.
- **nit**: 머지를 막지 않는 작은 제안입니다.
- **blocking comment**: 머지 전에 반드시 해결해야 하는 지적입니다.
- **Approve with comments**: 신뢰를 전제로 한 승인 방식입니다.

## 전후 비교

**이전 — 한 PR에 모든 변경 몰아넣기**

```text
PR title: Refactor user module + bug fix + log cleanup
-> impossible to review, intent is mixed
```

**이후 — 의도별로 나눈 작은 PR**

```text
1) fix: null user crash
2) refactor: extract notification port
3) chore: prune verbose logs
```

작은 PR은 리뷰 속도만 높이는 것이 아니라, 사고가 났을 때 원인을 좁히는 데도 유리합니다.

## 단계별로 리뷰 가능한 PR 만들기

### 1단계 — 제목 한 줄로 의도 쓰기

```text
# 1_pr_title.txt
fix(auth): handle expired refresh token without 500
```

제목만 읽어도 변경의 본질이 보여야 리뷰어가 빠르게 맥락을 잡을 수 있습니다.

### 2단계 — 본문 템플릿 채우기

```text
# 2_pr_body.md
## What
Return 401 for expired refresh tokens.

## Why
Today this throws 500 and floods our alerting.

## How
Map ExpiredTokenError to 401 in AuthService.refresh().

## Test
unit + manual cURL.
```

What, Why, How, Test 네 칸만 있어도 리뷰어는 어디서부터 읽어야 할지 바로 알 수 있습니다.

### 3단계 — 자동화로 사람의 부담 줄이기

```yaml
# 3_ci.yml
jobs:
  check:
    steps:
      - run: ruff check .
      - run: mypy app
      - run: pytest -q
```

포매팅, 타입 검사, 테스트 결과는 사람에게 맡기지 않는 편이 좋습니다.

### 4단계 — 머지 가능한 작은 단위로 나누기

```text
# 4_split.md
- PR 1: data model change
- PR 2: service logic
- PR 3: handlers and routing
```

가장 작은 머지 가능 단위를 찾는 능력은 협업 속도를 크게 좌우합니다.

### 5단계 — 코멘트 톤과 태그 정하기

```text
# 5_tone.md
[nit] Naming user_id consistently would be nicer.
[question] Could this branch trigger an N+1 query?
[blocking] A secret key ends up in the log. Must fix before merge.
```

코멘트에 의사결정 강도를 함께 적으면 토론이 빨라지고 오해가 줄어듭니다.

## 이 코드에서 먼저 봐야 할 점

- 자동화는 사람의 시야를 비워 주는 장치입니다.
- PR 본문 템플릿이 있으면 리뷰 시작 비용이 크게 내려갑니다.
- 코멘트 태그는 머지 기준을 드러냅니다.
- 작은 PR은 실패했을 때 복구 가능한 선택이 됩니다.

## 어디서 자주 헷갈릴까요?

첫 번째 실수는 거대한 PR을 들고 와서 리뷰어의 집중력을 시험하는 것입니다. 줄 수가 많아지면 사람은 모든 문맥을 유지하지 못합니다. 이때 리뷰는 구조 판단이 아니라 표면적인 지적만 남기고 끝나기 쉽습니다.

두 번째 실수는 기계가 할 수 있는 일을 사람에게 맡기는 것입니다. 들여쓰기, 포매팅, 사소한 정적 검사 결과를 사람이 코멘트로 적기 시작하면 정작 중요한 설계, 경계, 운영 리스크를 볼 여유가 사라집니다.

세 번째 실수는 코멘트를 사람에 대한 평가처럼 쓰는 태도입니다. 리뷰는 코드를 중심으로 해야 합니다. 공격적인 어조는 품질을 높이지 못하고 팀의 학습 속도만 떨어뜨립니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 코드 리뷰를 혼자 하는 품질 검사가 아니라 팀의 지식 분산 장치로 봅니다. CODEOWNERS, 보호된 브랜치, 필수 리뷰 수, 초록색 CI 게이트 같은 장치는 기본이고, 큰 변경은 PR 전에 RFC나 설계 검토를 먼저 거칩니다. 그러면 PR 리뷰는 큰 방향을 새로 논쟁하는 자리가 아니라, 이미 합의한 방향이 안전하게 반영됐는지 보는 자리가 됩니다.

시니어 엔지니어는 보통 “이 코드를 고칠 수 있는 사람이 팀에 몇 명인가”를 함께 봅니다. 리뷰의 수준은 얼마나 날카로운 지적을 했는가보다, 리뷰를 마친 뒤 더 많은 사람이 이 코드를 이해하게 되었는가로도 판단할 수 있습니다.

## 체크리스트

- [ ] PR 제목이 한 줄로 의도를 설명하나요?
- [ ] PR 본문에 What, Why, How, Test가 있나요?
- [ ] CI가 포매팅, 타입, 테스트를 자동으로 검사하나요?
- [ ] PR 크기가 대체로 200~400줄 안쪽인가요?
- [ ] 코멘트가 작성자가 아니라 코드를 향하고 있나요?

## 연습 문제

1. 최근 PR 하나를 골라 이 글의 템플릿으로 다시 써 보세요.
2. 아직 사람이 확인하는 항목 하나를 골라 자동화 방안을 제안해 보세요.
3. 팀에서 쓸 코멘트 태그 세 가지를 정리한 한 장짜리 가이드를 만들어 보세요.

## 정리

코드 리뷰는 결함 탐지와 지식 분산을 동시에 수행하는 협업 장치입니다. 잘 운영하려면 작은 PR, 명확한 의도, 자동화된 기본 검사, 코드 중심의 대화가 함께 있어야 합니다.

다음 글에서는 결함 탐지를 리뷰에만 기대지 않고, 테스트 전략으로 어떻게 앞당길지 다룹니다. 어떤 테스트를 어느 층에 놓아야 변경 비용이 내려가는지 이어서 살펴보겠습니다.

<!-- toc:begin -->
- [소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [요구사항 이해하기](./02-understanding-requirements.md)
- [설계와 구현의 차이](./03-design-vs-implementation.md)
- **코드 리뷰 (현재 글)**
- 테스트 전략 (예정)
- 버전 관리와 릴리스 (예정)
- 문서화 (예정)
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Google Engineering Practices — Code Review Developer Guide](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Best Kept Secrets of Peer Code Review — Smart Bear](https://smartbear.com/resources/ebooks/best-kept-secrets-of-peer-code-review/)

Tags: Computer Science, SoftwareEngineering, CodeReview, PullRequest, Collaboration, Quality
