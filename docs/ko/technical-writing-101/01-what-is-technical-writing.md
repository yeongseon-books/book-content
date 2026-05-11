---
series: technical-writing-101
episode: 1
title: 기술 글쓰기란 무엇인가
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
  - Writing
  - Documentation
  - Communication
  - Beginner
seo_description: 기술 글쓰기의 정의와 일반 글과의 차이를 정리한 글
last_reviewed: '2026-05-04'
---

# 기술 글쓰기란 무엇인가

> 기술 글쓰기 101 시리즈 (1/10)


## 이 글에서 다룰 문제

*글* 이 *코드* 만큼 *오래* 살기 때문입니다.

## 전체 흐름
```mermaid
flowchart LR
    R[Reader] --> Q[Question]
    Q --> A[Answer]
    A --> X[Action]
```

## Before/After

**Before**: "*Python* 은 *좋은 언어* 입니다."

**After**: "*초보자* 가 *5분* 안에 *Hello World* 를 *실행* 합니다."

## 기술 글 한 단락

### 1단계 — 독자 정하기

```python
audience = "Python 초보자"
```

### 2단계 — 과제 정하기

```python
task = "가상환경을 만들고 활성화한다"
```

### 3단계 — 명령

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4단계 — 결과

```python
result = "프롬프트 앞에 (.venv) 표시"
```

### 5단계 — 다음 행동

```python
next_step = "pip install requests"
```

## 이 코드에서 주목할 점

- *독자* 가 *먼저*.
- *명령* 이 *짧고*.
- *결과* 가 *눈에 보임*.

## 자주 하는 실수 5가지

1. ***독자* 가 *모호*.**
2. ***이론* 만 길다.**
3. ***명령* 이 *복사* 가 *안 됨*.**
4. ***결과* 가 *없다*.**
5. ***다음 행동* 이 *없다*.**

## 실무에서는 이렇게 쓰입니다

회사 내부 문서, 오픈소스 README, 컨퍼런스 발표 슬라이드가 모두 *기술 글* 입니다.

## 체크리스트

- [ ] *독자* 가 *명시* 됨.
- [ ] *과제* 가 *한 줄*.
- [ ] *명령* 이 *동작*.
- [ ] *결과* 가 *명시*.

## 정리 및 다음 단계

다음 글은 *독자 정의하기* 입니다.

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
