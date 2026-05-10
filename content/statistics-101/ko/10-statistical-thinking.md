---
series: statistics-101
episode: 10
title: 통계적 사고방식
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Statistics
  - Thinking
  - Mindset
  - Decision
  - Beginner
seo_description: 질문, 데이터, 분포, 추정, 불확실성, 의사결정으로 이어지는 통계적 사고의 흐름과 시리즈 전체를 한 사례로 묶어 마무리하는 글
last_reviewed: '2026-05-04'
---

# 통계적 사고방식

> Statistics 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *통계는 도구* 인가, *사고방식* 인가? *시리즈 전체* 를 *한 줄의 흐름* 으로 묶어보면 무엇이 보일까요?

> *통계는 *불확실성을 다루는 언어* 이다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *질문 → 의사결정* 으로 이어지는 *통계적 흐름*
- *시리즈 전체* 를 *하나의 사례* 로 정리
- *불확실성* 과 *맥락* 을 다루는 *마인드셋*
- 5단계 *통계적 사고* 실습
- 흔한 함정 5가지

## 왜 중요한가

도구를 알아도 *언제 어떻게 쓸지* 모르면 의미가 없습니다. *통계적 사고* 는 *데이터 → 결정* 의 *연결고리* 입니다.

> *Statistics is the grammar of evidence.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Q["Question"] --> D["Data"]
    D --> Dist["Distribution"]
    Dist --> Est["Estimate + CI"]
    Est --> Test["Hypothesis Test"]
    Test --> Eff["Effect Size"]
    Eff --> Dec["Decision"]
```

## 핵심 용어 정리

- **Question-first**: *데이터를 보기 전* 에 *질문을 명확히*.
- **Uncertainty**: *모든 추정* 에는 *오차* 가 있다.
- **Context**: 같은 *p* 도 *맥락* 에 따라 의미가 다름.
- **Effect size**: *유의* 보다 *크기* 가 더 중요한 경우가 많음.
- **Decision**: 통계의 *목적은 결정* 이지 *p* 가 아님.

## Before/After

**Before**: *“데이터를 *돌려보고* 무엇이 나오나 *보자*.”* — *fishing expedition*.

**After**: *“우리 *질문* 은 무엇이고, *어떤 데이터* 가 답하며, *결정* 에 *얼마의 근거* 가 필요한가?”*

## 실습: 5단계 통계적 사고 (A/B 테스트 사례)

### 1단계 — 질문

```python
# 새 결제 버튼이 전환율을 높이는가?
question = "Does new button increase conversion?"
```

### 2단계 — 데이터와 분포

```python
# A: 5,000명, 250 conversion ; B: 5,000명, 290 conversion
nA, kA = 5000, 250
nB, kB = 5000, 290
pA, pB = kA/nA, kB/nB
print(pA, pB)
```

### 3단계 — 추정과 신뢰구간

```python
import math
diff = pB - pA
se = math.sqrt(pA*(1-pA)/nA + pB*(1-pB)/nB)
print("diff:", diff, "95% CI:", (diff - 1.96*se, diff + 1.96*se))
```

### 4단계 — 가설검정과 효과 크기

```python
import math
z = diff / se
print("z:", z, "lift:", diff / pA)
```

### 5단계 — 의사결정

```python
# 작은 효과라도 비용이 0이면 적용; 비용이 크면 더 큰 표본으로 재검증
decision = "ship" if (diff > 0 and z > 1.96) else "hold"
print(decision)
```

## 이 코드에서 주목할 점

- *질문* 이 *분석 설계* 를 결정한다.
- *추정 + CI + 효과 크기* 가 *p* 보다 *정보가 많다*.
- *결정* 은 *통계 + 비즈니스 비용* 의 함수다.

## 자주 하는 실수 5가지

1. ***질문 없이*** *데이터부터* 본다.
2. ***p* 만 보고** *결정* 한다.
3. ***불확실성* 을 *말로 옮기지*** 않는다.
4. ***맥락 없이*** 다른 분석과 *비교* 한다.
5. ***효과 크기* 와 *비용*** 을 분리하지 않는다.

## 실무에서는 이렇게 쓰입니다

제품 실험, 가격 결정, 신약 승인, 정책 평가 — *통계적 사고* 는 *모든 데이터 기반 의사결정* 의 기반입니다. *데이터 사이언스, ML, 비즈니스 분석* 모두 같은 흐름을 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *질문 → 데이터 → 결정* 의 *흐름* 을 안다.
- *불확실성* 을 *수치로* 표현한다.
- *p* 가 아니라 *효과 크기와 비용* 으로 결정한다.
- *맥락* 을 *기록* 한다.
- *통계는 도구* 이자 *사고방식* 임을 안다.

## 체크리스트

- [ ] *질문* 을 먼저 정의한다.
- [ ] *추정 + CI + 효과 크기* 를 함께 본다.
- [ ] *불확실성* 을 *명시* 한다.
- [ ] *결정* 의 *비용* 을 고려한다.

## 연습 문제

1. 최근의 *데이터 기반 결정* 을 *질문 → 결정* 흐름으로 다시 써보세요.
2. *p < 0.05* 를 *효과 크기 + CI* 로 *대체* 한 보고서를 작성하세요.
3. *통계적으로 유의* 하지만 *비즈니스적으로 무의미* 한 사례를 적으세요.

## 정리 및 다음 단계

통계는 *불확실성을 다루는 언어* 이고, 통계적 사고는 *데이터에서 결정으로* 가는 *흐름* 입니다. 다음 단계는 *Probability 101* 과 *Machine Learning 101* 에서 이 사고를 *예측* 으로 확장하는 것입니다.

<!-- toc:begin -->
- [통계란 무엇인가?](./01-what-is-statistics.md)
- [평균, 중앙값, 분산](./02-mean-median-variance.md)
- [분포](./03-distributions.md)
- [표본과 모집단](./04-sample-and-population.md)
- [추정](./05-estimation.md)
- [신뢰구간](./06-confidence-interval.md)
- [가설검정](./07-hypothesis-testing.md)
- [상관과 회귀](./08-correlation-and-regression.md)
- [p-value 이해하기](./09-understanding-p-value.md)
- **통계적 사고방식 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Nate Silver — The Signal and the Noise](https://en.wikipedia.org/wiki/The_Signal_and_the_Noise)
- [Hans Rosling — Factfulness](https://en.wikipedia.org/wiki/Factfulness)
- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Wikipedia — Statistical Thinking](https://en.wikipedia.org/wiki/Statistical_thinking)

Tags: Statistics, Thinking, Mindset, Decision, Beginner
