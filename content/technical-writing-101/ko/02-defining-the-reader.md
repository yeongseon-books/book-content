---
series: technical-writing-101
episode: 2
title: "Technical Writing 101 (2/10): 독자 정의하기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - TechnicalWriting
  - Audience
  - Persona
  - Writing
  - Beginner
seo_description: 기술 글의 독자를 페르소나로 정의하고 글의 범위를 좁히는 방법을 정리한 글
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (2/10): 독자 정의하기

같은 FastAPI 예제라도 처음 API를 만드는 주니어에게는 친절한 입문이 될 수 있고, 운영 장애를 잡는 온콜 엔지니어에게는 쓸모없는 장황한 설명이 될 수 있습니다. 글이 틀린 게 아니라 독자가 빗나간 것입니다.

문서를 읽는 사람을 한 덩어리로 놓고 쓰기 시작하면 예제 길이, 용어 수준, 생략 가능한 배경지식이 모두 흔들립니다. 반대로 독자를 한 사람처럼 구체화하면 무엇을 설명하고 무엇을 과감히 버려야 할지가 빠르게 정리됩니다.

이 글은 Technical Writing 101 시리즈의 2번째 글입니다. 여기서는 독자 모델을 페르소나, 전제 지식, 목표, 비목표로 나누어 글의 범위를 좁히는 방법을 다룹니다.

## 먼저 던지는 질문

- 왜 모두를 위한 글은 결국 아무도 제대로 돕지 못할까요?
- 페르소나를 만들면 문장이 왜 더 선명해질까요?
- 전제 지식과 목표를 먼저 적어 두면 범위가 어떻게 줄어들까요?

## 큰 그림

![Technical Writing 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/02/02-01-concept-at-a-glance.ko.png)

*Technical Writing 101 2장 흐름 개요*

이 그림에서는 독자 정의하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 독자 정의하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 페르소나 만들기
- 전제 지식 정리하기
- 목표 맞추기
- 범위 좁히기
- 예제 난이도 맞추기

## 왜 중요한가

독자가 흐리면 문장도 흐려집니다. 누구를 돕는 글인지 정하지 않으면 설명 깊이, 예제 길이, 용어 선택, 비목표가 모두 흔들립니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 선명한 독자 한 명을 먼저 세우면, 글의 지식 수준과 목표와 범위가 그 독자 주변으로 자동 정렬됩니다.

## 핵심 용어

- **persona**: 독자의 모델입니다.
- **prerequisite**: 전제 지식입니다.
- **goal**: 독자가 다음에 하게 될 일입니다.
- **scope**: 글이 다루는 범위입니다.
- **non-goal**: 글이 다루지 않는 범위입니다.

## Before / After

**Before**: "A post for developers."

**After**: "A post for a first-year Python engineer learning FastAPI."

## 같은 기능도 독자에 따라 완전히 달라집니다

| 독자 | 알고 있는 것 | 지금 필요한 것 | 이 글에서 빼야 할 것 |
| --- | --- | --- | --- |
| 입문자 | Python 문법, `pip` | 첫 FastAPI 엔드포인트 | 배포 전략, 성능 튜닝 |
| 리뷰어 | API 기본기 | 문서의 빠진 전제 지식 | 설치 세부 과정 전체 |
| 온콜 엔지니어 | 운영 환경 | 장애 대응 절차와 점검 순서 | 기초 개념 재설명 |

같은 `/health` 엔드포인트 예제라도 입문자에게는 라우트 선언과 실행 명령이 중요하고, 온콜 엔지니어에게는 로그 위치와 재현 경로가 더 중요합니다. 그래서 페르소나는 문체 취향을 고르는 장식이 아니라, 무엇을 남기고 무엇을 잘라낼지 결정하는 편집 기준입니다.

## 실습: 페르소나 카드 하나 만들기

### 1단계 — 이름과 역할

```python
persona = {"name": "Jimin", "role": "First-year Python backend"}
```

### 2단계 — 전제 지식

```python
knows = ["variables", "functions", "git basics"]
```

### 3단계 — 빈칸

```python
unknown = ["async", "type hints"]
```

### 4단계 — 목표

```python
goal = "Ship the first FastAPI endpoint"
```

### 5단계 — 비목표

```python
non_goal = ["deployment", "DB migrations"]
```

## 이 코드에서 먼저 볼 점

- 페르소나에 이름이 있습니다.
- 페르소나에 빈칸이 있습니다.
- 페르소나에 비목표가 있습니다.

## 자주 하는 실수 5가지

1. **모두를 대상으로 잡습니다.**
2. **전제 지식을 건너뜁니다.**
3. **목표가 모호합니다.**
4. **비목표가 없습니다.**
5. **예제가 너무 어렵습니다.**

## 실무에서는 이렇게 드러납니다

API 레퍼런스, 사용자 가이드, 튜토리얼은 모두 페르소나에 따라 갈라집니다. 독자가 다르면 필요한 배경과 예제가 달라지기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 독자는 한 사람처럼 느껴져야 합니다.
- 비목표가 글을 줄여 줍니다.
- 예제는 전제 지식 범위에서 돌아야 합니다.
- 목표는 동사로 적습니다.
- 2주 뒤의 나도 독자입니다.

## 체크리스트

- [ ] 페르소나가 한 명인가
- [ ] 전제 지식이 세 가지 있는가
- [ ] 목표가 한 줄로 적혀 있는가
- [ ] 비목표가 하나 이상 있는가

## 연습 문제

1. persona의 뜻을 한 줄로 적어 보세요.
2. non-goal의 뜻을 한 줄로 적어 보세요.
3. prerequisite의 예시를 한 줄로 적어 보세요.

## 정리

독자를 분명히 적으면 문장도, 예제도, 범위도 함께 선명해집니다. 특히 전제 지식과 목표와 비목표를 같이 적어 두면 글이 훨씬 짧고 유용해집니다. 다음 글에서는 이렇게 정한 독자를 기준으로 제목과 구조를 어떻게 설계해야 하는지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **왜 모두를 위한 글은 결국 아무도 제대로 돕지 못할까요?**
  - 본문의 기준은 독자 정의하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **페르소나를 만들면 문장이 왜 더 선명해질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **전제 지식과 목표를 먼저 적어 두면 범위가 어떻게 줄어들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- **독자 정의하기 (현재 글)**
- 제목과 구조 잡기 (예정)
- 개념 설명하기 (예정)
- 예제 코드 설명하기 (예정)
- 그림과 표 사용하기 (예정)
- README 작성하기 (예정)
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)

<!-- toc:end -->

## 참고 자료

- [The Persona Lifecycle - Pruitt & Adlin](https://www.elsevier.com/books/the-persona-lifecycle/pruitt/978-0-12-566251-2)
- [About Face - Cooper et al.](https://www.wiley.com/en-us/About+Face%3A+The+Essentials+of+Interaction+Design%2C+4th+Edition-p-9781118766576)
- [Nielsen Norman Group on Personas](https://www.nngroup.com/articles/persona/)
- [Writing for Developers - Karl Hughes](https://www.writingfordevelopers.com/)

Tags: TechnicalWriting, Audience, Persona, Writing, Beginner
