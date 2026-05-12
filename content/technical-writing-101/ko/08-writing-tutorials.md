---
series: technical-writing-101
episode: 8
title: 튜토리얼 작성하기
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - TechnicalWriting
  - Tutorial
  - Learning
  - HandsOn
  - Beginner
seo_description: 따라하기만 해도 동작하는 튜토리얼을 작성하는 방법을 정리한 글
last_reviewed: '2026-05-12'
---

# 튜토리얼 작성하기

이 글은 Technical Writing 101 시리즈의 8번째 글입니다.

## 이 글에서 다룰 문제

- 따라 하기 글은 설명 글이나 레퍼런스와 무엇이 다를까요?
- 독자가 따라만 해도 동작하는 튜토리얼은 어떻게 만들까요?
- 전제 조건, 작은 성공, 복구 안내, 다음 단계는 어떤 순서로 놓여야 할까요?
- 왜 짧은 튜토리얼이 더 좋은 경우가 많을까요?

## 이 글에서 배울 것

- Diátaxis에서 튜토리얼의 자리
- 전제 조건 적기
- 작은 성공 설계하기
- 오류 복구 메모
- 정리와 다음 단계

## 왜 중요한가

첫 성공은 계속 배우고 싶게 만드는 힘을 줍니다. 그래서 좋은 튜토리얼은 완전한 설명보다 빠른 성공을 먼저 설계합니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 튜토리얼은 강의문이 아니라 안내선입니다. 전제 조건을 먼저 밝히고, 한 단계씩 따라가게 하고, 작은 성공을 빠르게 보여 준 뒤, 다음 학습으로 넘깁니다.

```mermaid
flowchart LR
    P[Prereq] --> S[Step]
    S --> W[Win]
    W --> N[Next]
```

## 핵심 용어

- **tutorial**: 학습 지향 글입니다.
- **prerequisite**: 전제 조건입니다.
- **small win**: 작은 성공입니다.
- **recovery**: 오류 복구 경로입니다.
- **next step**: 다음에 배울 주제입니다.

## Before / After

**Before**: "Let us learn about FastAPI." (lecture)

**After**: "Run Hello World in five minutes." (tutorial)

## 실습: 5분 튜토리얼 만들기

### 1단계 — 전제 조건

```bash
python3 --version  # 3.11 or newer
```

### 2단계 — 설치

```bash
pip install "fastapi[standard]"
```

### 3단계 — 코드

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}
```

### 4단계 — 실행

```bash
fastapi dev main.py
```

### 5단계 — 검증

```text
{"hello":"world"}
```

## 이 코드에서 먼저 볼 점

- 전제 조건이 먼저 나옵니다.
- 명령은 순서대로 놓여 있습니다.
- 결과가 분명히 적혀 있습니다.

## 자주 하는 실수 5가지

1. **전제 조건이 없습니다.**
2. **명령 순서가 틀립니다.**
3. **작은 성공이 없습니다.**
4. **오류 복구 메모가 없습니다.**
5. **다음 단계가 없습니다.**

## 실무에서는 이렇게 드러납니다

좋은 라이브러리의 공식 튜토리얼은 대부분 5분 안에 첫 성공을 끝냅니다. 튜토리얼은 모든 것을 다루는 문서가 아니라, 첫 성공을 여는 입구이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 전제 조건은 반드시 적습니다.
- 작은 성공은 3분 안팎에 도착해야 합니다.
- 모든 오류에는 복구 한 줄이 있어야 합니다.
- 다음 단계는 작은 점프여야 합니다.
- 튜토리얼은 학습용이지 레퍼런스가 아닙니다.

## 체크리스트

- [ ] 전제 조건이 적혀 있는가
- [ ] 단계 수가 다섯 개 이하인가
- [ ] 작은 성공이 하나 있는가
- [ ] 다음 단계가 보이는가

## 연습 문제

1. tutorial의 뜻을 한 줄로 적어 보세요.
2. small win의 뜻을 한 줄로 적어 보세요.
3. recovery의 예시를 한 줄로 적어 보세요.

## 정리

튜토리얼은 설명을 많이 하는 글이 아니라, 독자가 따라 하며 첫 성공을 얻는 글입니다. 그래서 전제 조건, 단계 순서, 작은 성공, 복구 안내, 다음 단계가 모두 중요합니다. 다음 글에서는 개인 경험을 담는 블로그와 팀의 공식 기준을 담는 문서를 어떻게 구분할지 살펴보겠습니다.

<!-- toc:begin -->
- [기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [독자 정의하기](./02-defining-the-reader.md)
- [제목과 구조 잡기](./03-title-and-structure.md)
- [개념 설명하기](./04-explaining-concepts.md)
- [예제 코드 설명하기](./05-explaining-example-code.md)
- [그림과 표 사용하기](./06-using-figures-and-tables.md)
- [README 작성하기](./07-writing-the-readme.md)
- **튜토리얼 작성하기 (현재 글)**
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [Diátaxis Framework](https://diataxis.fr/)
- [Django Tutorial Style](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Teach Tech with Tutorials - Write the Docs](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/)

Tags: TechnicalWriting, Tutorial, Learning, HandsOn, Beginner
