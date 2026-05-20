---
series: technical-writing-101
episode: 6
title: "Technical Writing 101 (6/10): 그림과 표 사용하기"
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

# Technical Writing 101 (6/10): 그림과 표 사용하기

문단으로 충분히 설명할 수 있는 내용을 그림으로 바꾸면 오히려 독자를 헷갈리게 만들 수 있습니다. 반대로 흐름이나 비교를 문단으로만 밀어붙이면 독자는 핵심 구조를 파악하기도 전에 스크롤부터 내리게 됩니다. 중요한 것은 시각 자료의 양이 아니라 질문과 형식의 짝을 맞추는 일입니다.

좋은 그림은 문장을 장식하지 않고 문장을 줄여 줍니다. 좋은 표는 선택지를 예쁘게 나열하는 대신 의사결정 기준을 한눈에 드러냅니다. 그래서 시각 자료는 글의 말미에 덧붙이는 부록이 아니라 본문 설계의 일부로 다루는 편이 낫습니다.

이 글은 Technical Writing 101 시리즈의 6번째 글입니다. 여기서는 그림과 표를 언제 고르고, 캡션과 대체 텍스트를 어떻게 써야 하는지 정리합니다.

## 먼저 던지는 질문

- 언제 그림이 문단보다 더 나을까요?
- 언제 표가 비교를 더 정확하게 보여 줄까요?
- 캡션과 대체 텍스트는 왜 장식이 아니라 본문 일부일까요?

## 큰 그림

![Technical Writing 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/06/06-01-concept-at-a-glance.ko.png)

*Technical Writing 101 6장 흐름 개요*

그림과 난닝날 거먷되는 개덕 단비늤 올어날닉니다.

> 링 및 난닝날 명각히 준니다.

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

## 다이어그램 유형별 사용 가이드

| 다이어그램 유형 | 적합한 상황 | 강점 | 추천 도구 |
| --- | --- | --- | --- |
| Flowchart | 요청 흐름, 결정 분기, 프로세스 단계 | 방향과 조건을 직관적으로 표현 | Mermaid, draw.io |
| Sequence Diagram | 서비스 간 호출 순서, 시간 흐름 | 호출 순서와 응답 관계를 명확히 드러냄 | Mermaid, PlantUML |
| ER Diagram | 데이터베이스 구조, 엔티티 관계 | 테이블 간 관계를 한눈에 파악 | dbdiagram.io, ERDPlus |
| Architecture Diagram | 시스템 구성 요소, 배포 구조 | 전체 시스템 경계와 역할 분리 표현 | draw.io, Lucidchart |
| State Diagram | 상태 전이, 워크플로 단계 | 상태 변화와 조건을 명확히 표현 | Mermaid, PlantUML |

다이어그램은 독자가 글에서 가장 먼저 눈길을 주는 요소입니다. 그래서 도구보다 먼저 어떤 질문에 답하려는지 명확히 해야 합니다. 요청이 어디로 흐르는지 보여 주려면 Flowchart가 강하고, 누가 누구를 언제 호출하는지 보여 주려면 Sequence Diagram이 더 적합합니다.

## 표 설계 원칙

표는 선택지를 나란히 비교할 때 가장 강력한 도구입니다. 하지만 표가 잘못 설계되면 오히려 혼란을 키울 수 있습니다. 다음 원칙을 따르면 독자가 훨씬 빨리 판단할 수 있습니다.

### 1. 비교축을 행에 둡니다

독자는 보통 왼쪽에서 오른쪽으로 읽습니다. 그래서 비교 대상(Option A, Option B)은 행으로, 비교 기준(Speed, Cost, Complexity)은 열로 두는 편이 자연스럽습니다.

### 2. 열 순서는 중요도 순입니다

가장 중요한 기준을 왼쪽에 둡니다. 예를 들어 비용이 가장 중요한 결정 요소라면 Cost 열을 Speed보다 먼저 배치합니다.

### 3. 단위를 헤더에 명시합니다

각 셀마다 `100ms`, `50ms`처럼 단위를 반복하지 말고, 헤더에 `Latency (ms)`처럼 한 번만 적습니다. 표가 훨씬 깔끔해집니다.

### 4. 셀 내용은 짧게 유지합니다

한 셀에 세 줄 이상 들어가면 표보다 본문 설명이 나을 수 있습니다. 표는 비교를 위한 요약 도구이지 전체 설명을 담는 곳이 아닙니다.

## 캡션 작성법

캡션은 그림이 무엇을 보여 주는지 한 문장으로 설명합니다. 좋은 캡션은 그림만 봐도 글의 맥락을 일부 복구할 수 있게 만듭니다.

### Good 캡션

```markdown
*클라이언트 요청이 API 서버와 데이터베이스를 거쳐 응답으로 돌아오는 전체 흐름입니다.*
```

이 캡션은 누가(클라이언트), 무엇을(요청), 어디로(API 서버 → 데이터베이스), 어떻게(흐름) 흐르는지 명확히 적었습니다.

### Bad 캡션

```markdown
*아키텍처 다이어그램*
```

이 캡션은 그림의 종류만 밝힐 뿐, 무엇을 읽어야 하는지 알려 주지 않습니다. 독자는 그림을 보고 나서야 맥락을 추측해야 합니다.

### 캡션과 대체 텍스트의 차이

- **캡션**: 시각 자료가 무엇을 보여 주는지 설명합니다. 모든 독자가 읽습니다.
- **대체 텍스트(alt text)**: 이미지를 볼 수 없는 환경(스크린 리더, 이미지 로딩 실패)에서 이미지를 대신합니다. 접근성 도구가 읽습니다.

둘 다 필수입니다. 캡션은 본문 흐름의 일부이고, 대체 텍스트는 접근성 요구사항입니다.

## Mermaid 코드 예시

Mermaid는 코드로 다이어그램을 그리는 도구입니다. 버전 관리가 쉽고, 텍스트 기반이라 협업에 강합니다.

### Flowchart 예시

```mermaid
flowchart LR
    Client["클라이언트"] --> API["API 서버"]
    API --> DB["데이터베이스"]
    DB --> API
    API --> Client
```

이 코드는 클라이언트에서 API 서버로, 다시 데이터베이스로 이어지는 요청 흐름을 네 단계로 보여 줍니다.

### Sequence Diagram 예시

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant A as API 서버
    participant D as 데이터베이스

    C->>A: GET /users
    A->>D: SELECT * FROM users
    D-->>A: 결과 반환
    A-->>C: JSON 응답
```

이 코드는 호출 순서와 응답 방향을 화살표로 명확히 드러냅니다. 실선 화살표는 요청, 점선 화살표는 응답을 나타냅니다.
캡션도 제목처럼 역할이 분명해야 합니다. `아키텍처 다이어그램`처럼 뭉뚱그린 캡션보다 `클라이언트 요청이 API 서버와 데이터베이스를 거치는 순서`처럼 무엇을 읽어야 하는지 알려 주는 문장이 훨씬 강합니다. 좋은 시각 자료는 그림만 봐도 맥락이 조금씩 회복되게 만듭니다.

## 해상도와 접근성 실전 가이드

이미지는 눈에 보이는 크기보다 두 배 해상도로 준비해야 레티나 디스플레이에서도 선명합니다.

### 권장 해상도

| 표시 크기 | 실제 이미지 해상도 | 비율 |
| --- | --- | --- |
| 800×600px | 1600×1200px | 2x |
| 1200×800px | 2400×1600px | 2x |

### 접근성 체크리스트

- [ ] 모든 이미지에 alt 텍스트가 있는가
- [ ] 캡션이 완전한 문장인가
- [ ] 색상만으로 정보를 전달하지 않는가
- [ ] 대비율이 4.5:1 이상인가

## 실무 팁: 다이어그램 도구 선택

| 상황 | 추천 도구 | 이유 |
| --- | --- | --- |
| 버전 관리가 중요 | Mermaid | 코드로 작성, Git 친화적 |
| 복잡한 아키텍처 | draw.io | 무료, 풍부한 아이콘 |
| 협업 중심 | Lucidchart | 실시간 협업, 클라우드 |
| 데이터베이스 설계 | dbdiagram.io | ERD 특화, 빠른 생성 |

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

## 처음 질문으로 돌아가기

- **언제 그림이 문단보다 더 나을까요?**
  - **언제 그림이 문단보다 더 난다는 늸 둋말까요?**
  늨른 그림으로 러른 부분을 단언편며 늤켚동을 래납닉니다.
- **언제 난다가 비교를 더 명확한 늸 둋말까요?**
  비교 난늤는 달랜 비교나그가 늤총닉니다.
- **캠학션과 대체 텍스트는 왜 장식이 아니라 본문 일부일까요?**
  본문은 본문니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
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
