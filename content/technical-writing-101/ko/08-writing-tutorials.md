---
series: technical-writing-101
episode: 8
title: "Technical Writing 101 (8/10): 튜토리얼 작성하기"
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
  - Tutorial
  - Learning
  - HandsOn
  - Beginner
seo_description: 독자가 따라 하기만 해도 첫 성공을 경험하도록 돕는 튜토리얼 작성법을 배웁니다. 전제 조건, 단계별 설계, 오류 복구 등 실전 팁을 담았습니다.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (8/10): 튜토리얼 작성하기

튜토리얼을 쓰다 보면 설명을 더해야 안심이 됩니다. 그런데 독자는 지금 모든 배경을 배우러 온 것이 아니라, 손을 움직여 첫 성공을 확인하러 온 경우가 많습니다. 그래서 튜토리얼은 설명의 완전성보다 성공 경로의 안정성을 먼저 설계해야 합니다.

좋은 튜토리얼은 단계가 짧고, 검증 지점이 분명하고, 막히는 지점에서 바로 복구 힌트를 줍니다. 독자가 중간에 실패하더라도 무엇을 다시 확인해야 하는지 한 줄이라도 보여 주면 완주율이 크게 달라집니다.

이 글은 Technical Writing 101 시리즈의 8번째 글입니다. 여기서는 첫 성공을 빠르게 만들고 검증 가능한 단계로 나누는 튜토리얼 설계법을 정리합니다.

## 먼저 던지는 질문

- 따라 하기 글은 설명 글이나 레퍼런스와 무엇이 다를까요?
- 독자가 따라만 해도 동작하는 튜토리얼은 어떻게 만들까요?
- 전제 조건, 작은 성공, 복구 안내, 다음 단계는 어떤 순서로 놓여야 할까요?

## 큰 그림

![Technical Writing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/08/08-01-concept-at-a-glance.ko.png)

*Technical Writing 101 8장 흐름 개요*

이 그림에서는 튜토리얼 작성하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 튜토리얼 작성하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## 핵심 용어

- **tutorial**: 학습 지향 글입니다.
- **prerequisite**: 전제 조건입니다.
- **small win**: 작은 성공입니다.
- **recovery**: 오류 복구 경로입니다.
- **next step**: 다음에 배울 주제입니다.

## Before / After

**Before**: "Let us learn about FastAPI." (lecture)

**After**: "Run Hello World in five minutes." (tutorial)

## 튜토리얼 단계마다 검증 지점을 심어 둡니다

튜토리얼이 잘 작동하는지 확인하려면 각 단계가 독립적인 테스트처럼 보여야 합니다. 예를 들어 FastAPI 예제라면 아래처럼 파일 저장, 실행, 검증, 복구 힌트를 함께 둘 수 있습니다.

```bash
cat > main.py <<'PY'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}
PY

fastapi dev main.py
```

**Expected output:**

```text
Uvicorn running on http://127.0.0.1:8000
```

복구 힌트도 한 줄은 있어야 합니다. 예를 들어 `fastapi: command not found`가 보이면 `python3 -m pip install "fastapi[standard]"`를 다시 실행하라고 바로 적어 두면 독자는 검색창으로 새어나가지 않고 튜토리얼 안에서 문제를 풀 수 있습니다.

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

## 처음 질문으로 돌아가기

- **따라 하기 글은 설명 글이나 레퍼런스와 무엇이 다를까요?**
  - 본문의 기준은 튜토리얼 작성하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **독자가 따라만 해도 동작하는 튜토리얼은 어떻게 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **전제 조건, 작은 성공, 복구 안내, 다음 단계는 어떤 순서로 놓여야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- [Technical Writing 101 (7/10): README 작성하기](./07-writing-the-readme.md)
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
