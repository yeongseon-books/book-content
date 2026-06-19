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

이 글은 기술 글쓰기 101 시리즈의 5번째 글입니다.

좋은 코드 설명은 많은 줄을 보여 주는 데 있지 않습니다. 가장 작은 예제를 먼저 제시하고, 왜 그 줄이 필요한지 짚고, 실제 실행과 검증 결과로 독자의 불안을 줄이는 데 있습니다.

여기서는 최소 실행 예제를 고르고, 설명 줄과 실행 결과를 연결하는 코드 워크스루 방식을 정리합니다.

![Technical Writing 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/05/05-01-concept-at-a-glance.ko.png)
*Technical Writing 101 5장 흐름 개요*
> 좋은 예제 코드는 양으로 설득하지 않습니다. 가장 작은 코드를 보여 주고, 핵심을 짚고, 실행하게 하고, 출력으로 닫습니다.

## 이 글에서 다룰 문제

- 코드를 붙여 넣었는데도 왜 독자는 길을 잃을까요?
- 최소 예제와 설명 줄과 출력 결과는 어떤 순서로 배치해야 할까요?
- 코드 안 주석과 코드 밖 설명은 언제 나누는 편이 좋을까요?
- 코드 예제를 점진적으로 확장할 때 어떤 원칙을 따라야 할까요?
- 독자가 성공했는지 실패했는지 스스로 알게 하려면 무엇이 필요할까요?

## 이 글에서 배울 것

- 최소 실행 예제(MWE) 선택 기준
- 설명 줄(callout) 작성 위치와 방법
- 인라인 주석 vs 본문 설명 구분 기준
- 실행 명령과 기대 출력 제시 방법
- 점진적 공개(Progressive Disclosure) 구조

실행 가능한 예제는 독자의 손에 닿아야 비로소 가르칠 수 있습니다. 읽기만 하고 돌려 보지 못하는 예제는 설명 자료일 수는 있어도 학습 도구가 되기 어렵습니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 좋은 예제 코드는 양으로 설득하지 않습니다. 가장 작은 코드 조각을 보여 주고, 그중 어디를 봐야 하는지 짚고, 직접 실행하게 하고, 눈에 보이는 출력으로 닫습니다.

- **MWE**: 최소 실행 예제(Minimal Working Example)입니다.
- **callout**: 코드 밖에서 핵심을 짚는 설명 줄입니다.
- **inline comment**: 코드 안 주석입니다.
- **fixture**: 예제 데이터입니다.
- **snippet**: 짧게 잘라 낸 코드 조각입니다.

## 코드 예제 설명 흐름 구조

```
독자가 코드 블록을 만나는 순간
         │
         ▼
  [맥락 제공]  ← 이 코드가 무엇을 보여 주는지 한 문장
         │
         ▼
  [코드 블록]  ← MWE: 10-20줄 이하, 실행 가능
         │
         ▼
 [실행 명령]   ← bash 블록으로 복사-붙여넣기 가능
         │
         ▼
 [기대 출력]   ← 실제 실행 결과 그대로
         │
         ▼
 [callout]    ← 가장 중요한 줄 1-2개 짚기
         │
         ▼
  [전체 링크]  ← 확장 학습을 위한 저장소 링크
```

이 흐름을 따르면 독자는 코드를 읽는 단계에서 직접 실행하는 단계로 자연스럽게 이동합니다.

## Before / After 비교: 코드 예제 제시 방식

### Before / After 예시 1: 코드 덤프 vs MWE

**Before — 200줄 전체 코드를 한 번에 제시**

```python
# 아래 코드를 실행하면 사용자 관리 API가 동작합니다.
import logging
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
# ... (이후 180줄 계속)
```

독자는 무엇부터 봐야 할지 모릅니다. 핵심 진입점이 어디인지 찾는 데만 시간이 걸립니다.

**After — 핵심만 담은 MWE로 시작**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

```bash
fastapi dev main.py
```

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

`@app.get("/")`이 진입점을 만들고, `fastapi dev`가 서버를 띄웁니다. 독자는 8줄로 첫 성공을 확인할 수 있습니다.

---

### Before / After 예시 2: 버전 없음 vs 버전 고정

**Before — 버전 정보 없이 설치 안내**

```
FastAPI를 설치한 다음 main.py를 실행합니다.
```

6개월 후 독자는 다른 버전을 설치해 다른 결과를 얻습니다.

**After — 버전을 고정하여 재현성 보장**

```bash
pip install "fastapi[standard]==0.115.0" "uvicorn[standard]==0.32.0"
```

패키지 버전을 고정하면 이 글이 낡아도 독자는 같은 환경에서 같은 결과를 얻습니다.

---

### Before / After 예시 3: 출력 없음 vs 기대 출력 제시

**Before — 실행 결과 안내 없음**

```python
@app.get("/add")
def add(a: int, b: int) -> dict:
    return {"result": a + b}
```

독자는 이 코드가 정상 동작하는지 확인할 방법이 없습니다.

**After — 실행 명령과 기대 출력을 함께 제시**

```bash
curl "http://127.0.0.1:8000/add?a=2&b=3"
```

```json
{"result": 5}
```

`curl` 명령 하나로 독자는 성공 여부를 즉시 확인합니다.

## 문서 템플릿: 코드 예제 설명 블록

코드 설명을 작성할 때 이 템플릿을 복사해 사용하면 항목 누락을 줄일 수 있습니다.

```markdown
<!-- 코드 설명 블록 시작 -->

다음 예제는 [이 코드가 무엇을 보여 주는지 한 문장].

```[언어]
[MWE: 10-20줄 이하, 실행 가능한 코드]
```

```bash
[실행 명령 — 복사-붙여넣기로 동작해야 함]
```

```text
[기대 출력 — 실제 실행 결과 그대로]
```

이 예제에서 핵심은 `[가장 중요한 줄 또는 함수]`입니다. [한두 문장 설명]

복구 힌트: `[자주 발생하는 오류]`가 보이면 `[해결 명령]`을 실행합니다.

전체 코드: [GitHub 링크]

<!-- 코드 설명 블록 끝 -->
```

## 코드 예제의 세 가지 계층

코드 예제는 복잡도에 따라 세 계층으로 나눌 수 있습니다.

| 계층 | 줄 수 | 목적 | 사용 시점 |
| --- | --- | --- | --- |
| 스니펫 (Snippet) | 3-5줄 | 구문 확인, 빠른 참조 | 한 가지 개념만 보여줄 때 |
| MWE | 10-20줄 | 첫 번째 성공 경험 | 글의 첫 예제, Quick Start |
| 실무 예제 | 50-100줄 | 실무 적용 패턴 | 오류 처리, 검증, 로깅 포함 |

처음에는 항상 스니펫 또는 MWE로 시작합니다. 독자가 첫 성공을 확인한 뒤에야 실무 예제로 확장합니다.

## 인라인 주석 vs 본문 설명 — 언제 쓸까

| 상황 | 인라인 주석 (코드 안) | 본문 설명 (코드 밖) |
| --- | --- | --- |
| 한 줄이 핵심일 때 | 사용 | 중복 피하기 |
| 흐름 전체를 설명할 때 | 너무 길어짐 | 사용 |
| 독자가 한 줄만 수정해야 할 때 | 사용 (`# TODO: API 키 입력`) | 강조 병행 |
| 코드가 이미 자명할 때 | 불필요 | 불필요 |
| 트레이드오프 설명할 때 | 코드 흐름 방해 | 사용 |

**좋은 예 — 인라인 주석과 본문 설명 조합:**

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")  # 음수 ID 거부
    return {"user_id": user_id, "name": "Jimin"}
```

이 엔드포인트는 경로 파라미터로 `user_id`를 받아 검증합니다. 음수가 입력되면 HTTP 400 오류를 반환하고, 정상 값이 입력되면 사용자 정보를 JSON으로 돌려줍니다. 인라인 주석은 `HTTPException` 한 줄의 역할만 짚고, 나머지 흐름은 본문에서 설명합니다.

## Progressive Disclosure: 간단한 예제에서 복잡한 예제로

코드 예제를 한 번에 복잡하게 제시하면 독자는 첫 단계에서 포기합니다. 대신 간단한 예제부터 시작해 점진적으로 기능을 추가하는 방식이 훨씬 효과적입니다.

**단계 1 — Hello World (최소 동작 확인)**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

```bash
fastapi dev main.py
```

```text
{"message": "Hello World"}
```

**단계 2 — 경로 파라미터 추가**

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

```bash
curl http://127.0.0.1:8000/users/42
```

```json
{"user_id": 42}
```

**단계 3 — 검증 로직 추가**

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    return {"user_id": user_id}
```

각 단계마다 하나의 개념만 추가합니다. 독자는 각 단계에서 성공을 확인하며 자신감을 쌓고, 다음 단계로 자연스럽게 넘어갑니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 바로 고치는 방법 |
| --- | --- | --- |
| 코드가 너무 깁니다 | 독자가 핵심을 찾지 못하고 이탈합니다 | MWE로 줄이고 나머지는 링크로 제공합니다 |
| 출력을 보여 주지 않습니다 | 독자가 성공 여부를 확인할 수 없습니다 | 기대 출력 블록을 코드 블록 바로 아래 추가합니다 |
| 버전을 적지 않습니다 | 시간이 지나면 재현이 불가능해집니다 | pip install 명령에 버전을 고정합니다 |
| 인라인 주석이 과합니다 | 코드 흐름을 방해하고 가독성이 떨어집니다 | 핵심 줄 1-2개에만 주석을 달고 나머지는 본문에서 설명합니다 |
| 복사하면 깨지는 조각입니다 | 독자가 실행할 수 없어 신뢰를 잃습니다 | 독립 실행 가능한 완전한 예제를 제공합니다 |
| 전체 코드 링크가 없습니다 | 독자가 확장하거나 디버깅할 맥락이 없습니다 | GitHub 저장소 링크를 코드 블록 아래에 추가합니다 |

## 운영 체크리스트

- [ ] 열 줄 이하의 MWE가 있는가
- [ ] 실행 명령이 코드 블록 바로 아래 있는가
- [ ] 기대 출력이 명시되어 있는가
- [ ] 패키지 버전이 고정되어 있는가
- [ ] 전체 코드 저장소 링크가 있는가
- [ ] 자주 발생하는 오류와 복구 힌트가 있는가

## 연습 문제

1. MWE를 한 문장으로 정의해 보세요. "MWE는 \_\_\_ 예제입니다."
2. 아래 중 인라인 주석이 적합한 상황과 본문 설명이 적합한 상황을 구분하세요.
   - a. `return {"result": a + b}` — 두 수를 더해 반환합니다
   - b. 이 함수는 요청을 받아 검증하고 DB에 저장한 뒤 응답을 돌려줍니다
3. 200줄짜리 예제 코드를 MWE로 줄이는 원칙을 두 가지만 적어 보세요.

## 정리

좋은 예제 코드는 많은 코드를 보여 주는 예제가 아니라, 가장 짧은 코드로 핵심을 드러내는 예제입니다. 설명 줄, 실행 명령, 출력 결과, 전체 코드 링크까지 갖추면 독자는 읽기와 실행을 함께 할 수 있습니다. Progressive Disclosure 구조로 단계별로 기능을 추가하면 독자는 각 단계에서 성공을 확인하며 자신감을 쌓습니다. 다음 글에서는 텍스트만으로는 느린 설명을 그림과 표로 어떻게 바꿀지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- **Technical Writing 101 (5/10): 예제 코드 설명하기 (현재 글)**
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- [Technical Writing 101 (7/10): README 작성하기](./07-writing-the-readme.md)
- [Technical Writing 101 (8/10): 튜토리얼 작성하기](./08-writing-tutorials.md)
- [Technical Writing 101 (9/10): 블로그와 문서 차이](./09-blog-vs-docs.md)
- [발행 전 체크리스트](./10-pre-publish-checklist.md)

<!-- toc:end -->

## 참고 자료

- [The Art of Readable Code - Boswell & Foucher](https://www.oreilly.com/library/view/the-art-of/9781449318482/)
- [Stack Overflow MCVE Guide](https://stackoverflow.com/help/minimal-reproducible-example)
- [Python Tutorial Style Guide](https://docs.python.org/3/tutorial/index.html)
- [Diátaxis Framework - Code Examples](https://diataxis.fr/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/technical-writing-101/ko)

Tags: TechnicalWriting, Code, Examples, Walkthrough, Beginner
