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

실무에서 요구사항은 늘 "이미 아는 말"처럼 들립니다. 검색 기능을 만들어 달라, 비밀번호 재설정을 넣어 달라, 응답 속도를 개선해 달라 같은 문장은 모두 익숙합니다. 문제는 익숙한 말일수록 서로 다른 그림을 떠올린다는 사실입니다. 같은 문장을 듣고도 PM, 디자이너, 개발자, 운영 담당자가 보는 완료 기준은 자주 달라집니다.

이 글은 Software Engineering 101 시리즈의 2번째 글입니다.

그래서 요구사항 단계의 실수는 위험합니다. 구현 초반에는 작은 오해처럼 보여도, 나중에는 구조와 테스트와 릴리스 계획 전체를 다시 쓰게 만들 수 있습니다. 코드 결함의 상당수가 요구사항 단계에서 시작된다는 말이 반복되는 이유도 여기에 있습니다.

![Software Engineering 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/02/02-01-concept-at-a-glance.ko.png)
*Software Engineering 101 2장 흐름 개요*

> 요구사항은 익숙한 말일수록 사람마다 다른 그림을 떠올립니다 — PM·디자이너·개발자·운영의 완료 기준을 한 문서 위에 명시적으로 일치시키지 않으면, 초반의 작은 오해가 나중에 구조·테스트·릴리스 전체를 다시 쓰게 만듭니다.

## 이 글에서 다룰 문제

- 좋은 요구사항은 어떤 조건을 만족해야 할까요?
- 사용자 스토리와 인수 기준은 각각 무엇을 맡을까요?
- 기능 요구사항과 비기능 요구사항은 왜 따로 적어야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

구현 단계에서 발견한 버그는 고치면 됩니다. 하지만 요구사항 단계에서 잘못 이해한 문제는 버그보다 더 비쌉니다. 코드, 테스트, 문서, 사용자 기대, 일정이 함께 틀어지기 때문입니다. 특히 기능 요구사항은 눈에 잘 보이지만, 응답 시간, 보안, 가용성 같은 비기능 요구사항은 늦게 드러나서 더 큰 비용을 만듭니다.

실무에서는 "무엇을 만들지 안다"는 착각이 자주 생깁니다. 한 문장 설명을 듣고 바로 설계와 구현을 시작해도 팀은 일하는 것처럼 보입니다. 그런데 완료 직전에 "우리가 원한 건 이게 아니었다"는 말이 나오면 앞선 속도는 모두 사라집니다. 요구사항을 검증 가능한 문장으로 바꾸는 작업이 먼저 필요한 이유입니다.

## 한눈에 보는 흐름

요구사항은 테스트로 연결될 때 비로소 실제 개발 계약이 됩니다.

- **기능 요구사항**: 시스템이 무엇을 해야 하는지 설명하는 문장입니다.
- **비기능 요구사항**: 얼마나 빠르게, 얼마나 안전하게, 얼마나 안정적으로 동작해야 하는지 정하는 조건입니다.
- **사용자 스토리**: 역할, 행동, 가치를 한 줄로 묶는 표현입니다.
- **인수 기준**: 완료 여부를 판단하는 조건입니다.
- **INVEST**: 좋은 스토리가 가져야 할 여섯 가지 성질(Independent, Negotiable, Valuable, Estimable, Small, Testable)입니다.

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

인수 기준은 테스트 가능한 문장으로 적어야 합니다. "충분히 빨라야 한다" 같은 표현으로는 머지 기준이 되지 않습니다.

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

## 프로젝트 관리 예시: 스프린트에서 요구사항 처리 흐름

요구사항을 어떻게 처리하느냐는 스프린트 성공 여부와 직결됩니다. 아래는 2주 스프린트에서 요구사항 단계를 운영하는 전형적인 흐름입니다.

```markdown
[스프린트 계획 - D-1]
1. PM이 기능 요청 한 줄 공유: "쿠폰 적용 시 만료된 쿠폰 거부"
2. 개발자가 사용자 스토리 초안 작성 (10분)
3. PM/QA와 인수 기준 합의 (30분 회의)
4. 비기능 요구사항 추가 (응답 시간, 에러 코드 형식)
5. 스토리 포인트 산정 후 스프린트 백로그 등록

[스프린트 중 - D1~D8]
- 인수 기준을 그대로 테스트 케이스로 변환
- 구현 시 경계 케이스 발견 → 즉시 PM 확인 후 AC 업데이트

[스프린트 종료 - D10]
- 인수 기준 체크리스트 기준으로 QA 통과 확인
- 릴리스 노트에 "쿠폰 만료 시 오류 코드 COUPON_EXPIRED 반환" 기재
```

이 흐름에서 요구사항이 인수 기준 → 테스트 케이스 → 릴리스 노트로 자연스럽게 이어집니다. 중간에 끊기지 않으면 팀 전체가 같은 기준으로 움직일 수 있습니다.

## 인수 기준을 테스트 케이스로 변환하는 예시

요구사항 문서가 실제 개발 속도에 기여하려면 인수 기준이 테스트 케이스로 자연스럽게 연결되어야 합니다. 아래 예시는 결제 수단 저장 기능을 기준으로 변환한 형태입니다.

```markdown
[인수 기준]
- Given 로그인 사용자
- When 만료된 카드 정보를 저장하려고 하면
- Then 저장이 거부되고 만료 안내 문구를 표시한다

[테스트 케이스]
- 입력: 만료월/만료년이 현재 시점 이전
- 기대: 400 응답, error_code=CARD_EXPIRED
- 화면: 만료 안내 메시지 노출
- 로그: validation_error 카운트 증가
```

이처럼 요구사항 단계에서 검증 조건이 구조화되면, 개발자와 QA의 해석 차이가 크게 줄어듭니다.

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

## 자주 하는 실수

| 실수 패턴 | 구체적 증상 | 왜 문제인가 | 개선 방향 |
|---|---|---|---|
| 요구사항 없이 구현 시작 | 구두 설명만 듣고 코딩 착수 | 완료 직전 방향 재조정 발생 | 인수 기준 3개 이상 먼저 확정 |
| 비기능 요구사항 누락 | 기능은 동작하나 응답이 너무 느림 | 운영 단계에서 성능 장애 발생 | 성능·보안·가용성 항목을 별도 섹션으로 분리 |
| 인수 기준 모호 | "빨라야 함", "안전해야 함"처럼 측정 불가 | QA와 개발 기준이 달라 반복 리젝 | 수치와 조건을 명시 (p95 300ms, 400 에러코드 등) |
| 변경 이력 없음 | 요구사항이 바뀌어도 문서 미갱신 | 이전 결정 맥락을 잃어 재논의 반복 | 변경 요청마다 이슈 번호 + 이유 한 줄 의무화 |
| 제외 범위 미명시 | 리뷰 중 "이것도 포함해야 하지 않나"가 나옴 | 범위 크리프로 일정 초과 | "범위 제외" 섹션을 요구사항 문서에 고정 |

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 요구사항을 듣자마자 설계로 넘어가는 것입니다. 머릿속에 경험이 많을수록 더 빨리 구현안을 떠올리지만, 그 속도는 종종 잘못된 문제를 더 빨리 푸는 속도가 됩니다.

또 다른 실수는 기능 요구사항만 적고 비기능 요구사항을 비워 두는 것입니다. 로그인은 되는데 응답 시간이 지나치게 느리거나, 복구가 어렵거나, 보안 노출이 생기면 기능은 사실상 실패한 셈입니다. 비기능 요구사항은 부가 옵션이 아니라 시스템 품질의 경계선입니다.

"대충 이런 느낌"이라는 문장을 받아들이는 문화도 위험합니다. 측정할 수 없는 요구사항은 검증할 수 없고, 검증할 수 없는 요구사항은 팀마다 다른 완료 기준을 만들기 쉽습니다.

## 실무에서는 이렇게 생각합니다

강한 팀은 요구사항을 회의에서만 소비하지 않습니다. 발견 회의를 짧게 하더라도 결과는 RFC, PRD, 이슈, 티켓 설명 같은 문서로 남깁니다. 그리고 그 문서 안에 인수 기준 체크박스가 들어가야 구현, 리뷰, 테스트, QA가 같은 기준으로 움직일 수 있습니다.

시니어 엔지니어는 요구사항을 받으면 곧바로 코드를 떠올리기보다 먼저 질문을 떠올립니다. 누가 쓰는가, 실패하면 무엇이 깨지는가, 어디서 측정하는가, 성능과 보안은 어떻게 보장할 것인가 같은 질문이 정리되지 않았다면 구현을 미루는 편이 더 빠른 선택일 때가 많습니다.

## 요구사항-리뷰-테스트 연결표

엔지니어링에서 자주 놓치는 지점은 세 문서가 따로 움직이는 상황입니다. 요구사항 문서는 목표만 말하고, 리뷰는 스타일 중심으로 흘러가고, 테스트는 구현 이후에 뒤따라옵니다. 이렇게 분리되면 기능은 동작해도 품질 기준이 흐려집니다. 아래처럼 연결표를 두면 변경 영향이 추적됩니다.

```text
REQ-12: 만료 쿠폰 거부
- Review check: 상태 코드 400 + error_code=coupon_expired 확인
- Test case: test_apply_expired_coupon
- Metric: coupon_expired 발생 비율
```

연결표를 유지하면 "무엇을 만들었는가"가 아니라 "어떤 기준을 만족했는가"로 대화가 바뀝니다. 회고 시점에도 장애 원인을 요구사항 해석, 리뷰 누락, 테스트 공백 중 어디서 시작됐는지 빠르게 찾을 수 있습니다.

### 운영 전환 체크

- 배포 노트에 요구사항 ID와 PR 링크를 함께 남깁니다.
- 온콜 핸드오프 문서에 새 기능의 실패 시그널을 명시합니다.
- 첫 24시간 관찰 지표와 임계치를 릴리스 전에 고정합니다.

이 작은 연결 장치가 있으면 팀 규모가 커져도 품질 기준이 개인 기억에 의존하지 않습니다.

## 요구사항 문서 템플릿(실무형)

요구사항을 잘 쓴다는 말은 문장을 화려하게 꾸민다는 뜻이 아닙니다. 구현과 검증으로 바로 이어질 수 있게 구조화한다는 뜻입니다.

```markdown
# 기능: 비밀번호 재설정
## 목표
- 로그인 실패 문의를 월 30% 줄입니다.

## 사용자 스토리
- 사용자는 이메일 인증을 통해 비밀번호를 재설정할 수 있어야 합니다.

## 인수 기준
- Given 유효한 이메일 / When 재설정 요청 / Then 60초 안에 메일 발송
- Given 만료된 토큰 / When 재설정 시도 / Then 재요청 안내 문구 노출

## 비기능 요구사항
- p95 응답 시간 300ms 이하
- 실패율 1% 이하

## 제외 범위
- 소셜 로그인 계정 비밀번호 재설정은 제외합니다.
```

### CI 파이프라인에서 요구사항 검증하기

요구사항은 문서로 끝나지 않고 자동화와 연결되어야 합니다. 스모크 시나리오를 CI에 넣으면 "문서에 있었지만 구현 누락" 문제를 줄일 수 있습니다.

```yaml
name: acceptance-check
on: [pull_request]
jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run acceptance tests
        run: pytest tests/acceptance -q
```

## 요구사항 변경 관리 규칙

요구사항은 항상 바뀝니다. 문제는 변경 자체가 아니라 변경의 흔적이 사라지는 것입니다.

- 변경 요청은 반드시 이슈 번호로 등록합니다.
- 변경 이유를 사용자 영향과 함께 한 문단으로 적습니다.
- 기존 인수 기준에서 바뀐 줄만 명시적으로 표시합니다.
- 변경으로 영향받는 테스트 목록을 함께 갱신합니다.
- 릴리스 노트에 사용자 관점 변경점을 반영합니다.

요구사항 변경을 통제한다는 것은 변화를 막는 것이 아니라, 변화의 비용을 예측 가능하게 만드는 일입니다.

## 운영 체크리스트

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

다음 글에서는 구현 바로 앞 단계인 설계를 다룹니다. 잘 작성된 코드와 잘 설계된 시스템이 왜 다른지, 그리고 그 차이를 어떻게 문서로 남길지 이어서 봅니다.

## 처음 질문으로 돌아가기

- **좋은 요구사항은 어떤 조건을 만족해야 할까요?**
  - 좋은 요구사항은 INVEST 원칙을 충족합니다. 독립적으로 배포 가능하고(Independent), 협상 가능한 범위를 가지며(Negotiable), 사용자에게 가치를 전달하고(Valuable), 규모를 추정할 수 있고(Estimable), 충분히 작으며(Small), 테스트 가능한(Testable) 조건이 갖춰져야 합니다. 그 중에서도 핵심은 테스트 가능성입니다. 인수 기준으로 연결되지 않는 요구사항은 구현이 끝난 뒤에도 완료 여부를 판단할 수 없습니다.
- **사용자 스토리와 인수 기준은 각각 무엇을 맡을까요?**
  - 사용자 스토리는 "누가 무엇을 왜 필요한지"를 담는 커뮤니케이션 도구입니다. 인수 기준은 "어떤 조건이 충족될 때 완료로 볼 것인지"를 정하는 계약서입니다. 스토리는 방향을 잡고, 인수 기준은 경계를 그립니다. 둘 다 없으면 팀마다 다른 완료를 정의하게 됩니다.
- **기능 요구사항과 비기능 요구사항은 왜 따로 적어야 할까요?**
  - 기능 요구사항은 "무엇을 한다"를 설명하고, 비기능 요구사항은 "얼마나 잘 한다"를 정합니다. 응답 시간, 보안 정책, 가용성 목표는 구현 완료 이후에 드러나는 경우가 많아 초기에 분리해 두지 않으면 운영 단계에서 재작업 비용이 발생합니다. 두 유형을 같은 목록에 섞으면 리뷰에서 비기능 항목이 우선순위에서 밀리는 경향이 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- **Software Engineering 101 (2/10): 요구사항 이해하기 (현재 글)**
- [Software Engineering 101 (3/10): 설계와 구현의 차이](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): 코드 리뷰](./04-code-review.md)
- [Software Engineering 101 (5/10): 테스트 전략](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): 버전 관리와 릴리스](./06-version-control-and-release.md)
- [Software Engineering 101 (7/10): 문서화](./07-documentation.md)
- [Software Engineering 101 (8/10): 협업 프로세스](./08-collaboration-process.md)
- [Software Engineering 101 (9/10): 유지보수와 기술부채](./09-maintenance-and-tech-debt.md)
- [좋은 소프트웨어의 기준](./10-what-makes-good-software.md)

<!-- toc:end -->

## 참고 자료

- [Software Engineering 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/software-engineering-101/ko)
- [Mike Cohn — User Stories Applied](https://www.mountaingoatsoftware.com/books/user-stories-applied)
- [Atlassian — INVEST in Good Stories](https://www.atlassian.com/agile/project-management/user-stories)
- [Joel Spolsky — Painless Functional Specifications](https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/)
- [ISO/IEC/IEEE 29148 — Requirements Engineering](https://www.iso.org/standard/72089.html)

Tags: Computer Science, SoftwareEngineering, Requirements, ProductManagement, UserStory, Process
