---
series: technical-writing-101
episode: 8
title: 튜토리얼 작성하기
status: content-ready
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
last_reviewed: '2026-05-04'
---

# 튜토리얼 작성하기

> 기술 글쓰기 101 시리즈 (8/10)


## 이 글에서 다룰 문제

*첫 성공* 이 *학습 의지* 를 만듭니다.

## 전체 흐름
```mermaid
flowchart LR
    P[Prereq] --> S[Step]
    S --> W[Win]
    W --> N[Next]
```

## Before/After

**Before**: "*FastAPI* 에 대해 알아봅시다." (강의)

**After**: "*5분 안에* *Hello World* 를 *띄웁니다*." (튜토리얼)

## 5분 튜토리얼

### 1단계 — 전제

```bash
python3 --version  # 3.11 이상
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

### 5단계 — 확인

```text
{"hello":"world"}
```

## 이 코드에서 주목할 점

- *전제* 가 *맨 앞*.
- *명령* 이 *순서*.
- *결과* 가 *명시*.

## 자주 하는 실수 5가지

1. ***전제* 가 *없다*.**
2. ***명령* 이 *순서* 가 *없다*.**
3. ***작은 승리* 가 *없다*.**
4. ***오류 복구* 안내가 *없다*.**
5. ***다음 단계* 가 *없다*.**

## 실무에서는 이렇게 쓰입니다

좋은 라이브러리는 *공식 튜토리얼* 을 *5분 이내* 로 끝냅니다.

## 체크리스트

- [ ] *전제* 명시.
- [ ] *5단계 이하*.
- [ ] *작은 승리* 1회.
- [ ] *다음 단계* 표시.

## 정리 및 다음 단계

다음 글은 *블로그와 문서 차이* 입니다.

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
