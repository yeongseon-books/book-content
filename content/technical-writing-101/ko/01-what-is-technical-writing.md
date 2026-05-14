---
episode: 1
language: ko
last_reviewed: '2026-05-12'
seo_description: 기술 정보를 독자의 행동으로 연결하는 기술 글쓰기의 정의와 독자, 작업, 결과 중심 멘탈 모델 구축법을 다룹니다.
series: technical-writing-101
status: publish-ready
tags:
- TechnicalWriting
- Writing
- Documentation
- Communication
- Beginner
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: 기술 글쓰기란 무엇인가
---

# 기술 글쓰기란 무엇인가

이 글은 Technical Writing 101 시리즈의 첫 번째 글입니다.

## 이 글에서 다룰 문제

- 기술 글쓰기는 일반 글쓰기와 무엇이 다를까요?
- 기술 글은 왜 설명에서 끝나지 않고 독자의 행동까지 이어져야 할까요?
- 기술 글의 목적을 독자, 작업, 결과, 범위로 나누면 무엇이 또렷해질까요?
- 짧은 기술 단락 하나도 왜 작은 시리즈처럼 설계해야 할까요?

## 이 글에서 배울 것

- 기술 글쓰기의 정의
- 일반 글과의 차이
- 세 가지 목적
- 독자의 행동
- 시리즈의 형태

## 왜 중요한가

기술 글은 설명하는 코드를 따라 오래 남는 경우가 많습니다. 그래서 오늘 적은 문장이 몇 주 뒤, 몇 달 뒤에도 누군가의 설치, 실행, 판단, 복구 작업에 직접 영향을 줍니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 기술 글은 정보를 나열하는 글이 아니라, 독자의 질문을 답으로 연결하고 그 답을 실제 행동으로 넘기는 글입니다.

```mermaid
flowchart LR
    R[Reader] --> Q[Question]
    Q --> A[Answer]
    A --> X[Action]
```

## 핵심 용어

- **technical writing**: 기술 정보를 전달하는 산문입니다.
- **audience**: 독자입니다.
- **task**: 해야 할 일입니다.
- **outcome**: 결과입니다.
- **scope**: 경계입니다.

## Before / After

**Before**: "Python is a great language."

**After**: "A beginner can run Hello World in five minutes."

## 실습: 짧은 기술 단락 하나 만들기

### 1단계 — 독자 고르기

```python
audience = "Python beginners"
```

### 2단계 — 작업 고르기

```python
task = "Create and activate a virtual environment"
```

### 3단계 — 명령 제시하기

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4단계 — 결과 적기

```python
result = "(.venv) shows up in the prompt"
```

### 5단계 — 다음 행동 적기

```python
next_step = "pip install requests"
```

## 이 코드에서 먼저 볼 점

- 독자가 가장 먼저 나옵니다.
- 명령은 짧습니다.
- 결과는 눈으로 확인할 수 있습니다.

## 자주 하는 실수 5가지

1. **독자가 모호합니다.**
2. **이론이 너무 많습니다.**
3. **복사해 붙여 넣을 수 없는 명령을 올립니다.**
4. **눈에 보이는 결과가 없습니다.**
5. **다음 단계가 없습니다.**

## 실무에서는 이렇게 드러납니다

회사 내부 문서, 오픈소스 README, 발표 슬라이드도 모두 기술 글쓰기입니다. 형식은 달라도 공통점은 하나입니다. 읽는 사람이 그 글을 바탕으로 무언가를 해야 한다는 점입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 독자의 시간을 아낍니다.
- 명령은 적힌 그대로 돌아가야 합니다.
- 결과는 눈으로 보여야 합니다.
- 오래된 정보는 지웁니다.
- 링크는 살아 있어야 합니다.

## 체크리스트

- [ ] 독자가 분명히 적혀 있는가
- [ ] 작업이 한 줄로 정리되는가
- [ ] 명령이 실제로 실행되는가
- [ ] 결과가 문장으로 드러나는가

## 연습 문제

1. 기술 글쓰기의 정의를 한 줄로 적어 보세요.
2. audience의 뜻을 한 줄로 적어 보세요.
3. outcome의 뜻을 한 줄로 적어 보세요.

## 정리

기술 글은 정보를 설명하는 데서 멈추지 않고, 독자가 바로 행동할 수 있게 만들어야 합니다. 그래서 독자, 작업, 명령, 결과, 다음 단계가 모두 분명해야 합니다. 다음 글에서는 같은 내용을 써도 누구를 위해 쓰느냐에 따라 문장이 어떻게 달라지는지 살펴보겠습니다.

<!-- toc:begin -->
- **기술 글쓰기란 무엇인가 (현재 글)**
- 독자 정의하기 (예정)
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

- [Docs for Developers - Bhatti et al.](https://docsfordevelopers.com/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [Write the Docs Community](https://www.writethedocs.org/)

Tags: TechnicalWriting, Writing, Documentation, Communication, Beginner