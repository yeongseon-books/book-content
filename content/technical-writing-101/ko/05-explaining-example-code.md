---
series: technical-writing-101
episode: 5
title: "Technical Writing 101 (5/10): 예제 코드 설명하기"
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
  - Code
  - Examples
  - Walkthrough
  - Beginner
seo_description: 개발자가 기술 문서에서 예제 코드를 효과적으로 제시하고 핵심을 짚어 설명하며 실행 가능한 결과까지 보여주는 방법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (5/10): 예제 코드 설명하기

예제 코드는 길수록 친절해 보이지만, 실제로는 독자를 더 빨리 지치게 만드는 경우가 많습니다. 복사해 붙여 넣기 전에 무엇부터 봐야 하는지, 어디가 핵심인지, 어떤 출력이 정상인지가 보이지 않으면 코드는 설명이 아니라 장애물이 됩니다.

좋은 코드 설명은 많은 줄을 보여 주는 데 있지 않습니다. 가장 작은 예제를 먼저 제시하고, 왜 그 줄이 필요한지 짚고, 실제 실행과 검증 결과로 독자의 불안을 줄이는 데 있습니다.

이 글은 Technical Writing 101 시리즈의 5번째 글입니다. 여기서는 최소 실행 예제를 고르고, 설명 줄과 실행 결과를 연결하는 코드 워크스루 방식을 정리합니다.

## 먼저 던지는 질문

- 코드를 붙여 넣었는데도 왜 독자는 길을 잃을까요?
- 최소 예제와 설명 줄과 출력 결과는 어떤 순서로 배치해야 할까요?
- 코드 안 주석과 코드 밖 설명은 언제 나누는 편이 좋을까요?

## 큰 그림

![Technical Writing 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/05/05-01-concept-at-a-glance.ko.png)

*Technical Writing 101 5장 흐름 개요*

이 그림에서는 예제 코드 설명하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 예제 코드 설명하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 최소 예제
- 주석을 둘 위치
- 설명 줄 쓰기
- 입력과 출력 보여 주기
- 전체 코드 링크 연결하기

## 왜 중요한가

실행 가능한 예제는 독자의 손에 닿아야 비로소 가르칠 수 있습니다. 읽기만 하고 돌려 보지 못하는 예제는 설명 자료일 수는 있어도 학습 도구가 되기 어렵습니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 좋은 예제 코드는 양으로 설득하지 않습니다. 가장 작은 코드 조각을 보여 주고, 그중 어디를 봐야 하는지 짚고, 직접 실행하게 하고, 눈에 보이는 출력으로 닫습니다.

## 핵심 용어

- **MWE**: 최소 실행 예제입니다.
- **callout**: 코드 밖에서 핵심을 짚는 설명 줄입니다.
- **inline comment**: 코드 안 주석입니다.
- **fixture**: 예제 데이터입니다.
- **snippet**: 짧게 잘라 낸 코드 조각입니다.

## Before / After

**Before**: A 200 line code dump.

**After**: An 8 line MWE with a 2 line callout.

## 더 나은 코드 워크스루는 설정, 핵심, 검증을 함께 줍니다

아래처럼 예제를 한 단계 더 현실적으로 만들 수 있습니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
def add(a: int, b: int) -> dict[str, int]:
    return {"result": a + b}
```

```bash
uvicorn main:app --reload
curl "http://127.0.0.1:8000/add?a=2&b=3"
```

**Expected output:**

```json
{"result":5}
```

이 예제에서 독자가 가장 먼저 봐야 할 줄은 함수 본문이 아니라 `@app.get`과 `curl` 명령입니다. 하나는 진입점을 만들고, 다른 하나는 독자가 직접 성공을 확인하게 합니다. 코드 설명은 소스만 해설하는 일이 아니라 검증 경로를 열어 주는 일입니다.

## 실습: 예제 하나 설명해 보기

### 1단계 — 최소 코드

```python
def add(a, b):
    return a + b
```

### 2단계 — 설명 줄

```python
# Highlight: take two numbers and return their sum
```

### 3단계 — 실행

```bash
python3 -c "from m import add; print(add(2, 3))"
```

### 4단계 — 출력

```text
5
```

### 5단계 — 전체 코드 링크

```python
full_code_url = "https://github.com/example/repo/blob/main/m.py"
```

## 이 코드에서 먼저 볼 점

- 코드는 최소입니다.
- 설명 줄은 코드 바깥에 있습니다.
- 출력은 눈에 보입니다.

## 자주 하는 실수 5가지

1. **코드가 너무 깁니다.**
2. **주석이 너무 많습니다.**
3. **출력을 보여 주지 않습니다.**
4. **버전을 적지 않습니다.**
5. **복사해 붙여 넣으면 깨지는 조각입니다.**

## 실무에서는 이렇게 드러납니다

오픈소스 README의 Quick Start 절은 거의 늘 MWE와 출력 결과 패턴을 따릅니다. 독자가 가장 빨리 성공을 확인할 수 있는 구조이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 코드는 최소여야 합니다.
- 설명은 바깥에 둡니다.
- 출력은 실제 값이어야 합니다.
- 버전은 고정합니다.
- 전체 코드는 링크로 둡니다.

## 체크리스트

- [ ] 열 줄 이하의 MWE가 있는가
- [ ] 한두 줄 설명 줄이 있는가
- [ ] 출력이 보이는가
- [ ] 버전이 적혀 있는가

## 연습 문제

1. MWE의 뜻을 한 줄로 적어 보세요.
2. callout의 뜻을 한 줄로 적어 보세요.
3. fixture의 예시를 한 줄로 적어 보세요.

## 정리

좋은 예제 코드는 많은 코드를 보여 주는 예제가 아니라, 가장 짧은 코드로 핵심을 드러내는 예제입니다. 설명 줄, 실행 명령, 출력 결과, 전체 코드 링크까지 갖추면 독자는 읽기와 실행을 함께 할 수 있습니다. 다음 글에서는 텍스트만으로는 느린 설명을 그림과 표로 어떻게 바꿀지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **코드를 붙여 넣었는데도 왜 독자는 길을 잃을까요?**
  - 본문의 기준은 예제 코드 설명하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **최소 예제와 설명 줄과 출력 결과는 어떤 순서로 배치해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **코드 안 주석과 코드 밖 설명은 언제 나누는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- **예제 코드 설명하기 (현재 글)**
- 그림과 표 사용하기 (예정)
- README 작성하기 (예정)
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)

<!-- toc:end -->

## 참고 자료

- [The Art of Readable Code - Boswell & Foucher](https://www.oreilly.com/library/view/the-art-of/9781449318482/)
- [Stack Overflow MCVE Guide](https://stackoverflow.com/help/minimal-reproducible-example)
- [Python Tutorial Style Guide](https://docs.python.org/3/tutorial/index.html)
- [Diátaxis Framework - Code Examples](https://diataxis.fr/)

Tags: TechnicalWriting, Code, Examples, Walkthrough, Beginner
