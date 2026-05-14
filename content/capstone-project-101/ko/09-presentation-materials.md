---
series: capstone-project-101
episode: 9
title: 발표 자료 만들기
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Capstone
  - Presentation
  - Demo
  - Storytelling
  - Beginner
seo_description: 캡스톤 프로젝트 발표 자료를 문제·해결·결과 구조로 구성하고 데모와 Q&A 준비를 통해 프로젝트 가치를 효과적으로 전달하는 법을 정리합니다.
last_reviewed: '2026-05-12'
---

# 발표 자료 만들기

발표 자료는 기능 목록을 예쁘게 정리하는 문서가 아니라, 무엇을 왜 만들었고 어떤 결과가 나왔는지 짧은 시간 안에 설득력 있게 전달하는 도구입니다. 이 글은 Capstone Project 101 시리즈의 9번째 글입니다. 여기서는 문제·해결·결과 흐름으로 발표 자료를 구성하는 방법을 살펴보겠습니다.

> 멘탈 모델: 좋은 발표는 기능 설명이 아니라 서사입니다. 듣는 사람은 무엇을 만들었는지보다, 왜 만들었고 무엇이 달라졌는지를 더 빠르게 이해합니다.

## 이 글에서 다룰 문제

- 왜 기능 목록 중심 발표는 지루해질까요?
- 문제·해결·결과 구조는 왜 전달력이 높을까요?
- 슬라이드는 어떻게 구성해야 한 장당 메시지가 선명할까요?
- 데모 각본은 왜 미리 써야 할까요?
- Q&A와 시간 배분은 어떻게 준비해야 할까요?

## 이 글에서 배우는 내용

- 발표 서사 구조
- 슬라이드 구성 원칙
- 데모 각본 작성법
- Q&A 준비법
- 시간 배분 기준

## 왜 중요한가

발표는 결과물을 보여 주는 마지막 순간이자, 팀이 무엇을 배웠는지 설명하는 순간입니다. 같은 결과물이라도 서사가 없으면 단순 기능 나열로 보이고, 서사가 있으면 문제 해결 과정으로 보입니다.

실무 발표나 투자자 발표도 문제, 해결, 결과 구조를 자주 사용합니다. 듣는 사람은 기능 개수보다 어떤 문제를 풀었고 어떤 변화가 있었는지에 더 빠르게 반응합니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    P[Problem] --> S[Solution]
    S --> D[Demo]
    D --> R[Result]
    R --> N[Next]
```

## 핵심 용어

- **narrative**: 발표 전체를 묶는 이야기 흐름입니다.
- **slide**: 한 장에 하나의 메시지를 담는 화면입니다.
- **demo**: 미리 준비한 순서대로 보여 주는 시연입니다.
- **QnA**: 예상 질문과 답변 준비입니다.
- **timing**: 발표 시간 배분입니다.

## Before / After

**Before**: 기능 목록 슬라이드를 만듭니다.

**After**: 문제, 해결, 결과 흐름으로 슬라이드를 구성합니다.

## 실습: 슬라이드 표

### 1단계 — 서사 만들기

```python
story = ["problem", "solution", "demo", "result", "next"]
```

이 다섯 단계만 정리해도 발표의 뼈대가 잡힙니다. 기능은 이 흐름 안에서 필요한 만큼만 보여 주면 됩니다.

### 2단계 — 슬라이드 수 배분

```python
slides = {"problem": 2, "solution": 3, "demo": 1, "result": 2, "next": 1}
```

슬라이드 수를 미리 정해 두면 특정 구간이 과하게 길어지는 것을 막을 수 있습니다.

### 3단계 — 데모 각본

```python
demo_steps = ["login", "core_action", "result_view"]
```

데모는 욕심내기보다 세 단계 이내의 핵심 장면으로 줄이는 편이 안전합니다. 길어질수록 실패 가능성도 커집니다.

### 4단계 — Q&A 준비

```python
qna = ["why_this_stack", "how_we_tested", "what_we_cut"]
```

Q&A는 즉흥 대응만 믿지 말고, 예상 질문과 답변을 미리 정리해 두는 편이 좋습니다. 특히 왜 이 기술을 골랐는지, 무엇을 의도적으로 뺐는지는 자주 묻는 질문입니다.

### 5단계 — 시간 분배

```python
minutes = {"talk": 8, "demo": 5, "qna": 7}
```

시간 분배가 없으면 발표는 뒤로 갈수록 급해집니다. 발표 시간도 설계 대상이라고 보는 편이 좋습니다.

## 이 코드에서 먼저 볼 점

- 한 슬라이드에는 한 메시지만 둡니다.
- 데모는 세 단계 이내로 줄입니다.
- Q&A는 미리 준비합니다.
- 시간 배분도 문서에 적어 둡니다.

## 자주 하는 실수 5가지

1. 슬라이드에 텍스트를 너무 많이 넣습니다.
2. 기능 나열에 머뭅니다.
3. 데모 실패에 대비한 대체 흐름이 없습니다.
4. Q&A 준비가 없습니다.
5. 시간을 초과합니다.

## 실무에서는 이렇게 이어집니다

실무 발표나 투자자 피치도 문제, 해결, 결과 구조를 자주 사용합니다. 듣는 사람은 모든 기능을 알고 싶어 하기보다, 왜 이 일이 중요하고 어떤 결과가 있었는지를 먼저 이해하고 싶어 합니다. 캡스톤 발표도 같은 원리로 준비하는 편이 훨씬 설득력 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 서사가 기능보다 먼저입니다.
- 슬라이드는 시각적으로 단순해야 합니다.
- 데모는 리허설합니다.
- Q&A도 각본을 씁니다.
- 시간을 반드시 지킵니다.

## 체크리스트

- [ ] 다섯 단계 서사가 있습니다.
- [ ] 데모 각본이 있습니다.
- [ ] Q&A 답변이 있습니다.
- [ ] 시간 배분 표가 있습니다.

## 연습 문제

1. narrative 구조를 한 줄로 적어 보세요.
2. 데모 실패 대비책을 한 줄로 설명해 보세요.
3. Q&A 준비 방법 하나를 한 줄로 적어 보세요.

## 정리와 다음 글

발표 자료는 프로젝트의 마지막 포장지가 아니라, 팀이 무엇을 배웠는지 보여 주는 요약본입니다. 문제·해결·결과 흐름이 잡히면 기능 수보다 더 강한 설득력이 생깁니다. 다음 글에서는 프로젝트를 마친 뒤 무엇을 남겨야 하는지 회고 관점에서 정리하겠습니다.

<!-- toc:begin -->
- [캡스톤 프로젝트란 무엇인가](./01-what-is-capstone.md)
- [주제 선정](./02-choosing-a-topic.md)
- [문제 정의](./03-defining-the-problem.md)
- [요구사항 정리](./04-organizing-requirements.md)
- [팀 역할 나누기](./05-splitting-team-roles.md)
- [MVP 설계](./06-designing-the-mvp.md)
- [기술 스택 선택](./07-choosing-the-tech-stack.md)
- [일정 관리](./08-schedule-management.md)
- **발표 자료 만들기 (현재 글)**
- 프로젝트 회고 (예정)
<!-- toc:end -->

## 참고 자료

- [Presentation Zen - Garr Reynolds](https://www.presentationzen.com/)
- [The Cognitive Style of PowerPoint - Edward Tufte](https://www.edwardtufte.com/tufte/powerpoint)
- [TED Talks - Chris Anderson](https://www.ted.com/playlists/574/how_to_make_a_great_presentation)
- [Pyramid Principle - Barbara Minto](https://en.wikipedia.org/wiki/Pyramid_principle)

Tags: Capstone, Presentation, Demo, Storytelling, Beginner
