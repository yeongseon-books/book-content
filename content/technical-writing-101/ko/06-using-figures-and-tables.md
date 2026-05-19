---
series: technical-writing-101
episode: 6
title: 그림과 표 사용하기
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
  - Diagrams
  - Tables
  - Visual
  - Beginner
seo_description: 텍스트 위주의 기술 문서에서 그림과 표를 적재적소에 활용하여 복잡한 흐름을 시각화하고 선택지를 비교 분석하는 효율적인 방법을 안내합니다.
last_reviewed: '2026-05-15'
---

# 그림과 표 사용하기

문단으로 충분히 설명할 수 있는 내용을 그림으로 바꾸면 오히려 독자를 헷갈리게 만들 수 있습니다. 반대로 흐름이나 비교를 문단으로만 밀어붙이면 독자는 핵심 구조를 파악하기도 전에 스크롤부터 내리게 됩니다. 중요한 것은 시각 자료의 양이 아니라 질문과 형식의 짝을 맞추는 일입니다.

좋은 그림은 문장을 장식하지 않고 문장을 줄여 줍니다. 좋은 표는 선택지를 예쁘게 나열하는 대신 의사결정 기준을 한눈에 드러냅니다. 그래서 시각 자료는 글의 말미에 덧붙이는 부록이 아니라 본문 설계의 일부로 다루는 편이 낫습니다.

이 글은 Technical Writing 101 시리즈의 6번째 글입니다. 여기서는 그림과 표를 언제 고르고, 캡션과 대체 텍스트를 어떻게 써야 하는지 정리합니다.

## 이 글에서 다룰 문제

- 언제 그림이 문단보다 더 나을까요?
- 언제 표가 비교를 더 정확하게 보여 줄까요?
- 캡션과 대체 텍스트는 왜 장식이 아니라 본문 일부일까요?
- 해상도와 접근성은 왜 시각 자료의 기본 조건일까요?

## 이 글에서 배울 것

- 흐름도와 시퀀스 다이어그램
- 비교 표와 결정 표
- 캡션 쓰기
- 대체 텍스트 쓰기
- 해상도와 접근성

## 왜 중요한가

좋은 그림 한 장은 다섯 문단을 대신할 수 있습니다. 좋은 표 하나는 여러 선택지를 한 번에 비교하게 해 줍니다. 시각 자료는 장식이 아니라 탐색 비용을 줄이는 도구입니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 흐름을 보여 주고 싶으면 그림을 고르고, 선택지를 나란히 비교하고 싶으면 표를 고릅니다. 이 구분만 지켜도 많은 시각 자료가 더 정확해집니다.

![한눈에 보는 멘탈 모델](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/06/06-01-concept-at-a-glance.ko.png)

*한눈에 보는 멘탈 모델*
## 핵심 용어

- **flowchart**: 흐름도입니다.
- **sequence diagram**: 시퀀스 다이어그램입니다.
- **caption**: 캡션입니다.
- **alt text**: 이미지 대체 텍스트입니다.
- **a11y**: 접근성입니다.

## Before / After

**Before**: "The request goes from client to server to DB..." (five lines)

**After**: One flowchart.

## 독자의 질문에 따라 시각 자료를 고르는 기준

| 독자의 질문 | 더 잘 맞는 형식 | 이유 |
| --- | --- | --- |
| 요청이 어디로 흐르나요? | 흐름도 | 방향과 순서를 빠르게 보여 줍니다. |
| 어떤 선택지가 더 싼가요? | 비교 표 | 기준을 나란히 맞춰 읽게 합니다. |
| 장애가 어느 단계에서 납니까? | 시퀀스 다이어그램 | 호출 순서와 응답 지점을 드러냅니다. |
| 팀 기준은 무엇이 다른가요? | 결정 표 | 선택 기준을 항목별로 비교합니다. |

캡션도 제목처럼 역할이 분명해야 합니다. `아키텍처 다이어그램`처럼 뭉뚱그린 캡션보다 `클라이언트 요청이 API 서버와 데이터베이스를 거치는 순서`처럼 무엇을 읽어야 하는지 알려 주는 문장이 훨씬 강합니다. 좋은 시각 자료는 그림만 봐도 맥락이 조금씩 회복되게 만듭니다.

## 실습: 그림 하나와 표 하나 만들기

### 1단계 — 흐름도

![클라이언트에서 서버와 데이터베이스로 이어지는 요청 흐름](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/06/06-02-step-1-flowchart.ko.png)

*클라이언트 요청이 서버와 데이터베이스로 흐르는 기본 경로를 보여 주는 흐름도입니다.*
### 2단계 — 시퀀스

![클라이언트와 서버, 데이터베이스 사이의 호출 순서](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/06/06-03-step-2-sequence.ko.png)

*클라이언트와 서버, 데이터베이스 사이의 호출 순서를 보여 주는 시퀀스 다이어그램입니다.*
### 3단계 — 비교 표

```markdown
| Option | Speed | Cost |
| --- | --- | --- |
| A | Fast | High |
| B | Medium | Low |
```

### 4단계 — 캡션

```markdown
*Figure 1*. Request flow from client to database.
```

### 5단계 — 대체 텍스트

```markdown
![Request flow diagram](flow.png "Client to Server to DB")
```

## 이 코드에서 먼저 볼 점

- 그림은 흐름을 보여 줍니다.
- 표는 비교를 보여 줍니다.
- 캡션은 완전한 문장입니다.

## 자주 하는 실수 5가지

1. **그림이 전혀 없습니다.**
2. **표가 너무 큽니다.**
3. **캡션이 없습니다.**
4. **대체 텍스트가 없습니다.**
5. **해상도가 낮습니다.**

## 실무에서는 이렇게 드러납니다

스펙 문서, 아키텍처 문서, 장애 회고는 거의 늘 그림과 표를 함께 씁니다. 흐름은 그림으로, 선택지는 표로 나누어야 독자가 훨씬 빨리 읽을 수 있기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 흐름에는 그림을 씁니다.
- 비교에는 표를 씁니다.
- 캡션은 완전한 문장입니다.
- 대체 텍스트는 필수입니다.
- 해상도는 표시 크기의 두 배입니다.

## 체크리스트

- [ ] 그림이 하나 이상 있는가
- [ ] 표가 일곱 행 이하인가
- [ ] 모든 그림에 캡션이 있는가
- [ ] 모든 그림에 대체 텍스트가 있는가

## 연습 문제

1. flowchart와 sequence diagram의 차이를 한 줄로 적어 보세요.
2. caption의 뜻을 한 줄로 적어 보세요.
3. alt text의 뜻을 한 줄로 적어 보세요.

## 정리

그림과 표는 글을 꾸미는 요소가 아니라 설명을 압축하는 도구입니다. 흐름은 그림으로, 비교는 표로 나누면 독자는 구조를 훨씬 빨리 파악합니다. 다음 글에서는 처음 방문한 사람이 5분 안에 프로젝트를 실행할 수 있게 만드는 README를 어떻게 써야 하는지 살펴보겠습니다.

<!-- toc:begin -->
- [기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [독자 정의하기](./02-defining-the-reader.md)
- [제목과 구조 잡기](./03-title-and-structure.md)
- [개념 설명하기](./04-explaining-concepts.md)
- [예제 코드 설명하기](./05-explaining-example-code.md)
- **그림과 표 사용하기 (현재 글)**
- README 작성하기 (예정)
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [The Visual Display of Quantitative Information - Tufte](https://www.edwardtufte.com/tufte/books_vdqi)
- [Mermaid Diagram Syntax](https://mermaid.js.org/intro/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [Storytelling with Data - Knaflic](https://www.storytellingwithdata.com/)

Tags: TechnicalWriting, Diagrams, Tables, Visual, Beginner
