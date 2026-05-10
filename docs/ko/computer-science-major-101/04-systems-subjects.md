---
series: computer-science-major-101
episode: 4
title: 시스템 과목 이해하기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - CS
  - Systems
  - OS
  - Architecture
  - Beginner
seo_description: 운영체제, 컴퓨터 구조, 컴파일러, 시스템 프로그래밍 과목의 의미를 정리한 입문 글
last_reviewed: '2026-05-04'
---

# 시스템 과목 이해하기

> 컴퓨터학과 전공 학습 가이드 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *시스템* 과목은 *코드 한 줄* 이 *왜 그렇게 동작* 하는지 알려 주는 과목이다 — 이 말이 정말 맞을까요?

> 맞습니다. *OS*, *컴퓨터 구조*, *컴파일러* 가 *코드의 무대* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *운영체제* 의 의미
- *컴퓨터 구조*
- *컴파일러* 의 역할
- *시스템 프로그래밍*
- 디버깅 능력 향상

## 왜 중요한가

*성능* 과 *장애 분석* 은 *시스템 지식* 위에서만 가능합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    H[Hardware] --> A[Architecture]
    A --> O[OS]
    O --> C[Compiler]
    C --> P[Program]
```

## 핵심 용어 정리

- **OS**: *자원 관리자*.
- **process**: *실행* 단위.
- **thread**: *경량* 실행.
- **register**: 가장 *빠른* 메모리.
- **compiler**: *번역* 기.

## Before/After

**Before**: *코드* 가 *그냥* 돈다고 본다.

**After**: *CPU*, *메모리*, *OS* 가 보인다.

## 실습: 시스템 감각 키우기

### 1단계 — 프로세스 ID

```python
import os
print(os.getpid())
```

### 2단계 — 환경 변수

```python
print(os.environ.get("PATH", ""))
```

### 3단계 — 파일 디스크립터

```python
with open("/etc/hostname") as f:
    print(f.fileno())
```

### 4단계 — 시간 측정

```python
import time
t = time.perf_counter()
sum(range(10_000_000))
print(time.perf_counter() - t)
```

### 5단계 — 메모리 감각

```python
import sys
print(sys.getsizeof([0] * 1000))
```

## 이 코드에서 주목할 점

- *프로세스* 는 *고유 ID*.
- *환경* 은 *프로세스* 단위.
- *시간* 은 *시스템 호출*.

## 자주 하는 실수 5가지

1. ***메모리 주소* 를 *값* 으로 본다.**
2. ***프로세스* 와 *스레드* 혼동.**
3. ***스택* 과 *힙* 혼동.**
4. ***버퍼링* 을 잊는다.**
5. ***시스템 호출* 비용을 무시.**

## 실무에서는 이렇게 쓰입니다

장애 보고서의 *근본 원인* 은 *대부분* *OS 자원* 한계입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *코드* 는 *기계* 위에서 돈다.
- *비용* 은 *CPU* 와 *메모리*.
- *동시성* 은 *OS* 가 결정.
- *컴파일러* 가 *형태* 를 정한다.
- *시스템 호출* 은 *비싸다*.

## 체크리스트

- [ ] *프로세스/스레드* 구분.
- [ ] *메모리* 영역 이해.
- [ ] *시스템 호출* 비용 인지.
- [ ] *시간 측정* 가능.

## 연습 문제

1. *운영체제* 한 줄 정의.
2. *컴파일러* 한 줄 정의.
3. *프로세스* 의 의미 한 줄.

## 정리 및 다음 단계

다음 글은 *데이터베이스와 네트워크* 입니다.

<!-- toc:begin -->
- [컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [1학년 과목 이해하기](./02-first-year-subjects.md)
- [자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- **시스템 과목 이해하기 (현재 글)**
- 데이터베이스와 네트워크 (예정)
- AI와 데이터사이언스 (예정)
- 프로젝트 과목 (예정)
- 전공 공부 방법 (예정)
- 포트폴리오로 연결하기 (예정)
- 졸업 전 갖춰야 할 역량 (예정)
<!-- toc:end -->

## 참고 자료

- [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Computer Systems: A Programmer's Perspective](https://csapp.cs.cmu.edu/)
- [Crafting Interpreters](https://craftinginterpreters.com/)
- [The Linux Programming Interface](https://man7.org/tlpi/)
