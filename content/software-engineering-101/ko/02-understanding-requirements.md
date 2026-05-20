---
series: software-engineering-101
episode: 2
title: "Software Engineering 101 (2/10): 요구사항 이해하기"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareEngineering
  - Requirements
  - ProductManagement
  - UserStory
  - Process
seo_description: 좋은 요구사항의 조건, 사용자 스토리, INVEST 원칙을 짧게 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (2/10): 요구사항 이해하기

실무에서 요구사항은 늘 “이미 아는 말”처럼 들립니다. 검색 기능을 만들어 달라, 비밀번호 재설정을 넣어 달라, 응답 속도를 개선해 달라 같은 문장은 모두 익숙합니다. 문제는 익숙한 말일수록 서로 다른 그림을 떠올린다는 점입니다. 같은 문장을 듣고도 PM, 디자이너, 개발자, 운영 담당자가 보는 완료 기준은 자주 달라집니다.

그래서 요구사항 단계의 실수는 위험합니다. 구현 초반에는 작은 오해처럼 보여도, 나중에는 구조와 테스트와 릴리스 계획 전체를 다시 쓰게 만들 수 있습니다. 코드 결함의 상당수가 요구사항 단계에서 시작된다는 말이 반복되는 이유도 여기에 있습니다.

이 글은 Software Engineering 101 시리즈의 두 번째 글입니다. 여기서는 좋은 요구사항의 조건, 사용자 스토리와 인수 기준, 비기능 요구사항, 그리고 모호함을 걷어내는 질문 패턴을 정리합니다.

## 먼저 던지는 질문

- 좋은 요구사항은 어떤 조건을 만족해야 할까요?
- 사용자 스토리와 인수 기준은 각각 무엇을 맡을까요?
- 기능 요구사항과 비기능 요구사항은 왜 따로 적어야 할까요?

## 큰 그림

![Software Engineering 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/02/02-01-concept-at-a-glance.ko.png)

*Software Engineering 101 2장 흐름 개요*

이 그림에서는 요구사항 이해하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 요구사항 이해하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

구현 단계에서 발견한 버그는 고치면 됩니다. 하지만 요구사항 단계에서 잘못 이해한 문제는 버그보다 더 비쌉니다. 코드, 테스트, 문서, 사용자 기대, 일정이 함께 틀어지기 때문입니다. 특히 기능 요구사항은 눈에 잘 보이지만, 응답 시간, 보안, 가용성 같은 비기능 요구사항은 늦게 드러나서 더 큰 비용을 만듭니다.

실무에서는 “무엇을 만들지 안다”는 착각이 자주 생깁니다. 한 문장 설명을 듣고 바로 설계와 구현을 시작해도 팀은 일하는 것처럼 보입니다. 그런데 완료 직전에 “우리가 원한 건 이게 아니었다”는 말이 나오면 앞선 속도는 모두 사라집니다. 요구사항을 검증 가능한 문장으로 바꾸는 작업이 먼저 필요한 이유입니다.

## 한눈에 보는 흐름

요구사항은 테스트로 연결될 때 비로소 실제 개발 계약이 됩니다.

## 핵심 용어

- **기능 요구사항**: 시스템이 무엇을 해야 하는지 설명하는 문장입니다.
- **비기능 요구사항**: 얼마나 빠르게, 얼마나 안전하게, 얼마나 안정적으로 동작해야 하는지 정하는 조건입니다.
- **사용자 스토리**: 역할, 행동, 가치를 한 줄로 묶는 표현입니다.
- **인수 기준**: 완료 여부를 판단하는 조건입니다.
- **INVEST**: 좋은 스토리가 가져야 할 여섯 가지 성질입니다.

## 전후 비교

**이전 — 모호한 요구**

```text
"Build a search feature"
```

**이후 — 측정 가능한 요구**

```text
A user (role) searches the product catalog (scope) by keyword (input)
and gets results sorted by relevance (sort) within 500ms (performance).
```

한 문장 안에 역할, 범위, 입력, 정렬, 성능까지 들어가면 구현 방향이 크게 흔들리지 않습니다.

## 단계별로 요구사항 다듬기

### 1단계 — 사용자 스토리 쓰기

```text
# 1_story.txt
As a registered user, I want a password-reset link via email so that
I can quickly recover account access.
```

역할, 행동, 가치가 한 줄에 들어가면 이 기능이 누구를 위한 것인지 선명해집니다.

### 2단계 — 인수 기준 붙이기

```text
# 2_ac.txt
- Email arrives within 60 seconds for a registered address
- Link expires after 30 minutes
- Token is invalidated immediately after use
- Identical response for unregistered emails (avoid leaking)
```

인수 기준은 테스트 가능한 문장으로 적어야 합니다. “충분히 빨라야 한다” 같은 표현으로는 머지 기준이 되지 않습니다.

### 3단계 — 비기능 요구사항 적기

```text
# 3_nfr.txt
- Availability: 99.9% monthly
- Security: single-use token
- Observability: send/use counters streamed to SIEM
```

비기능 요구사항은 구현 세부사항이 아니라 운영 비용과 위험도를 정하는 항목입니다.

### 4단계 — 모호함을 드러내는 질문 던지기

```text
# 4_questions.txt
- Who uses this?
- How often?
- What happens on failure?
- Where do we measure?
- What is "done"?
```

질문이 많다는 것은 이해가 부족하다는 말이 아니라, 오해를 초기에 줄이려는 태도에 가깝습니다.

### 5단계 — 위키나 티켓에 기록하기

```text
# 5_doc.md
- Context
- User story
- Acceptance criteria
- Non-functional requirements
- Decision log (options and reason chosen)
```

말로 끝난 합의는 시간이 지나면 사라집니다. 나중에 돌아볼 수 있는 형태로 남겨야 합니다.

## 모호함을 줄이는 확인 절차

요구사항 문장을 받았을 때 곧바로 설계로 넘어가지 말고, 인수 기준과 측정 지점을 먼저 써 보세요. 이 단계에서 걸리는 10분이 뒤의 재작업 시간을 크게 줄여 줍니다.

### 확인 절차

1. 기능 요청 한 줄을 그대로 복사합니다.
2. 사용자 역할, 입력, 완료 조건, 실패 시 동작을 각각 한 문장으로 적습니다.
3. 성능·보안·관측성 가운데 최소 두 가지 비기능 요구사항을 덧붙입니다.

**예상 결과:**

- 처음 문장에는 빠져 있던 완료 기준과 예외 처리가 드러납니다.
- QA와 개발이 같은 체크리스트를 공유할 수 있는 문장으로 바뀝니다.
- 나중에 PR 본문과 테스트 케이스를 연결하기 쉬워집니다.

### 실패 신호

- "빠르게", "적절히" 같은 단어만 있고 수치나 조건이 없습니다.
- 비등록 사용자, 실패 응답, 관측성 같은 운영 관점이 빠져 있습니다.
- 문서 없이 회의 메모에만 남아 있어 며칠 뒤 다시 같은 질문이 나옵니다.

## 이 코드에서 먼저 봐야 할 점

- 좋은 요구사항의 출발점은 검증 가능성입니다.
- 인수 기준은 나중에 PR 머지 기준과 테스트 케이스로 이어집니다.
- 비기능 요구사항을 초기에 박아 두면 운영 사고 비용이 줄어듭니다.
- 결정 로그가 있으면 “왜 이렇게 만들었지?”라는 질문의 반복이 줄어듭니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 요구사항을 듣자마자 설계로 넘어가는 것입니다. 머릿속에 경험이 많을수록 더 빨리 구현안을 떠올리지만, 그 속도는 종종 잘못된 문제를 더 빨리 푸는 속도가 됩니다.

또 다른 실수는 기능 요구사항만 적고 비기능 요구사항을 비워 두는 것입니다. 로그인은 되는데 응답 시간이 지나치게 느리거나, 복구가 어렵거나, 보안 노출이 생기면 기능은 사실상 실패한 셈입니다. 비기능 요구사항은 부가 옵션이 아니라 시스템 품질의 경계선입니다.

“대충 이런 느낌”이라는 문장을 받아들이는 문화도 위험합니다. 측정할 수 없는 요구사항은 검증할 수 없고, 검증할 수 없는 요구사항은 팀마다 다른 완료 기준을 만들기 쉽습니다.

## 실무에서는 이렇게 생각합니다

강한 팀은 요구사항을 회의에서만 소비하지 않습니다. 발견 회의를 짧게 하더라도 결과는 RFC, PRD, 이슈, 티켓 설명 같은 문서로 남깁니다. 그리고 그 문서 안에 인수 기준 체크박스가 들어가야 구현, 리뷰, 테스트, QA가 같은 기준으로 움직일 수 있습니다.

시니어 엔지니어는 요구사항을 받으면 곧바로 코드를 떠올리기보다 먼저 질문을 떠올립니다. 누가 쓰는가, 실패하면 무엇이 깨지는가, 어디서 측정하는가, 성능과 보안은 어떻게 보장할 것인가 같은 질문이 정리되지 않았다면 구현을 미루는 편이 더 빠른 선택일 때가 많습니다.

## 체크리스트

- [ ] 사용자 스토리에 역할, 행동, 가치가 모두 들어가 있나요?
- [ ] 인수 기준이 측정 가능한 문장으로 적혀 있나요?
- [ ] 비기능 요구사항이 분리되어 있나요?
- [ ] 선택지와 이유를 남긴 결정 로그가 있나요?
- [ ] PR 설명과 인수 기준이 연결되나요?

## 연습 문제

1. 현재 프로젝트 기능 하나를 사용자 스토리 한 줄로 다시 적어 보세요.
2. 인수 기준이 없는 기능 하나를 골라 다섯 개의 기준을 써 보세요.
3. 무시하면 실제 사고로 이어질 비기능 요구사항 두 가지를 적어 보세요.

## 정리

좋은 요구사항은 상세한 문장보다 검증 가능한 문장에 가깝습니다. 역할, 행동, 가치, 인수 기준, 비기능 요구사항, 결정 로그가 갖춰지면 구현 단계의 불확실성이 크게 줄어듭니다.

다음 글에서는 구현 바로 앞 단계인 설계를 다룹니다. 잘 작성된 코드와 잘 설계된 시스템이 왜 다른지, 그리고 그 차이를 어떻게 문서로 남길지 이어서 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **좋은 요구사항은 어떤 조건을 만족해야 할까요?**
  - 본문의 기준은 요구사항 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **사용자 스토리와 인수 기준은 각각 무엇을 맡을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **기능 요구사항과 비기능 요구사항은 왜 따로 적어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- **요구사항 이해하기 (현재 글)**
- 설계와 구현의 차이 (예정)
- 코드 리뷰 (예정)
- 테스트 전략 (예정)
- 버전 관리와 릴리스 (예정)
- 문서화 (예정)
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Mike Cohn — User Stories Applied](https://www.mountaingoatsoftware.com/books/user-stories-applied)
- [Atlassian — INVEST in Good Stories](https://www.atlassian.com/agile/project-management/user-stories)
- [Joel Spolsky — Painless Functional Specifications](https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/)
- [ISO/IEC/IEEE 29148 — Requirements Engineering](https://www.iso.org/standard/72089.html)

Tags: Computer Science, SoftwareEngineering, Requirements, ProductManagement, UserStory, Process
