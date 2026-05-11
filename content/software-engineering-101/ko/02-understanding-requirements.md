---
series: software-engineering-101
episode: 2
title: 요구사항 이해하기
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
  - Requirements
  - ProductManagement
  - UserStory
  - Process
seo_description: 좋은 요구사항의 조건, 사용자 스토리, INVEST 원칙을 짧게 정리합니다.
last_reviewed: '2026-05-11'
---

# 요구사항 이해하기

> Software Engineering 101 시리즈 (2/10)


## 이 글에서 다룰 문제

코드 결함의 절반 이상이 요구사항 단계에서 발생합니다. 늦게 발견될수록 비용은 기하급수적으로 늘어납니다.

> 가장 비싼 코드는 다시 쓰는 코드입니다.

## 전체 흐름
```mermaid
flowchart LR
    U["사용자"] --> N["니즈"]
    N --> R["요구사항"]
    R --> A["인수 조건"]
    A --> T["테스트"]
```

요구는 인수 조건과 테스트로 검증 가능해져야 합니다.

## Before/After

**Before — 모호한 요구**

```text
"검색 기능 만들어 주세요"
```

**After — 측정 가능한 요구**

```text
사용자(역할)는 키워드(입력)로 상품 카탈로그(범위)를 검색해
0.5초 이내에(성능) 관련도순(정렬)으로 결과를 받는다.
```

같은 한 문장이 결과의 품질을 결정합니다.

## 요구를 다듬는 5단계

### 1단계 — 사용자 스토리 작성

```text
# 파일: 1_story.txt
As a 가입자, I want 비밀번호 재설정 링크를 이메일로 받기 so that
계정 접근을 빠르게 회복할 수 있다.
```

역할 - 행동 - 가치 세 부분.

### 2단계 — 인수 조건

```text
# 파일: 2_ac.txt
- 등록된 이메일이면 60초 내 발송
- 링크는 30분 후 만료
- 사용 후 토큰은 즉시 폐기
- 미등록 이메일도 동일 응답 (정보 노출 방지)
```

테스트 가능한 문장으로 적습니다.

### 3단계 — 비기능 요구

```text
# 파일: 3_nfr.txt
- 가용성: 월간 99.9%
- 보안: 토큰 1회 사용
- 관측: 발송/사용 카운터를 SIEM으로
```

비기능은 운영 비용을 결정합니다.

### 4단계 — 모호함 검출 질문

```text
# 파일: 4_questions.txt
- 누가 사용하는가?
- 얼마나 자주?
- 실패하면 어떻게 되나?
- 어디서 측정하나?
- 무엇이 "완료"인가?
```

5W1H를 붙여 모호함을 찾습니다.

### 5단계 — 위키/티켓에 글로 남기기

```text
# 파일: 5_doc.md
- 컨텍스트
- 사용자 스토리
- 인수 조건
- 비기능
- 의사결정 로그 (옵션과 선택 이유)
```

말로 합의한 요구는 사라집니다.

## 이 코드에서 주목할 점

- "검증 가능"이 좋은 요구의 시작입니다.
- 인수 조건은 PR 머지 기준이 됩니다.
- 비기능은 빨리 못 박을수록 좋습니다.
- 의사결정 로그는 미래의 디버깅 시간을 줄입니다.

## 자주 하는 실수 5가지

1. **요구를 듣자마자 설계.** 모호함이 그대로 코드로.
2. **"OO 같은 거"라는 표현 수용.** 측정 불가.
3. **비기능 무시.** 운영 단계에서 폭발.
4. **AC 없이 PR 머지.** 완료의 정의가 없음.
5. **변경 이력 없음.** "왜 이렇게 됐죠?"가 반복.

## 실무에서는 이렇게 쓰입니다

PM/디자이너/엔지니어가 함께 디스커버리 미팅을 갖고, RFC 또는 PRD에 요구를 정리합니다. Jira/Linear 티켓에는 AC가 체크박스로 들어가고, PR 설명에 매핑됩니다.

## 체크리스트

- [ ] 사용자 스토리에 역할/행동/가치가 모두 있는가?
- [ ] 인수 조건이 측정 가능한가?
- [ ] 비기능 요구가 명시되어 있는가?
- [ ] 의사결정 로그가 있는가?
- [ ] PR 설명이 AC와 매핑되는가?

## 정리 및 다음 단계

좋은 요구는 측정 가능합니다. 다음 글에서는 요구를 코드로 옮기기 전 단계 — 설계와 구현의 차이 — 를 봅니다.

<!-- toc:begin -->
- [소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
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
