---
series: data-science-career-101
episode: 7
title: 케이스 인터뷰
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataCareer
  - CaseInterview
  - ProductSense
  - Metrics
  - Beginner
seo_description: 데이터로 비즈니스 문제를 해결하는 케이스 인터뷰를 대비하여 지표 설계와 가설 검정 과정을 전개하는 문제 해결 프레임워크를 익힙니다.
last_reviewed: '2026-05-14'
---

# 케이스 인터뷰

케이스 인터뷰는 많은 지원자에게 가장 추상적으로 느껴지는 단계입니다. SQL처럼 정답 형태가 명확하지도 않고, 머신러닝처럼 알고리즘 이름을 기준으로 준비할 수도 없기 때문입니다. 그래서 질문을 들으면 곧바로 아이디어를 던지다가 구조 없이 끝나는 경우가 많습니다.

하지만 면접관이 보고 싶은 것은 아이디어의 양이 아니라 사고의 질입니다. 문제를 어떻게 명확히 하고, 어떤 지표를 중심에 둘지 정하고, 어떤 가설을 세운 뒤, 어떤 데이터로 검증하고, 마지막에 어떤 결정을 내릴지까지 보여 줘야 답변이 단단해집니다.

이 글은 Data Science Career 101 시리즈의 일곱 번째 글입니다.

## 이 글에서 다룰 문제

- 케이스 인터뷰가 실제로 무엇을 평가하는지 설명합니다.
- 문제를 들었을 때 왜 먼저 명확화 질문을 해야 하는지 짚습니다.
- 북극성 지표와 보조 지표를 어떻게 고를지 정리합니다.
- 가설과 데이터 계획을 어느 수준까지 구체화해야 하는지 살펴봅니다.
- 답변을 결정으로 닫아야 하는 이유를 설명합니다.

> 케이스 인터뷰의 핵심은 똑똑한 추측이 아니라, 문제를 명확히 하고 지표와 가설과 데이터를 거쳐 행동 가능한 결론으로 닫는 사고 구조를 보여 주는 일입니다.

## 이 글에서 배우는 내용

- 케이스 유형
- 답변 프레임
- 지표 설계
- 가설 검증
- 의사결정 제안

## 왜 중요한가

기술 역량만으로는 제품 문제를 풀 수 없습니다. 데이터 직무가 커질수록 질문을 구조화하고, 모호한 상황에서 판단 기준을 세우는 힘이 더 중요해집니다.

실무에서는 문제 정의가 늘 불완전한 상태에서 시작합니다. 숫자 하나가 떨어졌을 때도 세그먼트, 기간, 최근 변경 사항, 지표의 의미를 먼저 정리해야 합니다. 케이스 인터뷰는 바로 그 초기 구조화 능력을 압축해서 보는 방식이라고 생각하면 이해가 쉽습니다.

## 한눈에 보는 개념

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/07/07-01-concept-at-a-glance.ko.png)

*명확화에서 지표, 가설, 데이터, 결정으로 이어지는 케이스 인터뷰 답변 프레임*
이 다섯 단계는 답변 템플릿으로 그대로 써도 좋습니다. 문제를 명확히 하지 않으면 뒤의 지표와 데이터 계획이 모두 흔들립니다.

## 핵심 용어

- **product sense**: 기능과 지표가 사용자 경험에 미치는 영향을 읽는 감각입니다.
- **north star metric**: 제품의 핵심 가치를 대표하는 최상위 지표입니다.
- **hypothesis**: 데이터로 검증 가능한 설명입니다.
- **A/B test**: 두 조건을 비교하는 통제 실험입니다.
- **trade-off**: 하나를 얻으면 다른 하나를 잃는 관계입니다.

## Before / After

**Before**: "문제를 들으면 숫자부터 아무거나 던진다."

**After**: "Problem to Metric to Hypothesis to Data to Decision 순서로 답을 구성할 수 있다."

## 실습: 다섯 단계 프레임

### Step 1 — Clarify

```text
"DAU dropped" = which segment, what period?
```

명확화 질문은 시간을 버는 장치가 아니라 잘못된 문제를 푸는 일을 막는 장치입니다. 세그먼트, 기간, 최근 변경 사항을 먼저 확인해야 합니다.

### Step 2 — Metric

```text
- north star metric
- two supporting metrics
```

핵심 지표 하나와 보조 지표 둘 정도를 잡으면 답변의 중심이 생깁니다. 지표가 없으면 대화는 금방 추상적으로 흩어집니다.

### Step 3 — Hypothesis

```text
- product change
- external event
- data pipeline
```

가설은 하나만 두면 위험합니다. 제품 변경, 외부 이벤트, 데이터 파이프라인처럼 성격이 다른 가설을 함께 세워야 탐색이 균형을 잡습니다.

### Step 4 — Data

```text
- which query, which comparison
- A/B feasibility
```

“데이터를 보겠습니다”로는 약합니다. 어떤 비교를 할지, 어떤 로그를 볼지, 실험이 가능한지까지 말해야 실행 계획처럼 들립니다.

### Step 5 — Decision

```text
- recommended action
- risks
- follow-up measurement
```

케이스 답변은 결론이 있어야 끝납니다. 추천 액션과 리스크, 후속 측정이 함께 나와야 실제 의사결정 제안이 됩니다.

## 이 예시에서 먼저 봐야 할 점

- 명확화가 답변 품질을 끌어올립니다.
- 지표가 대화의 중심축이 됩니다.
- 마지막에는 반드시 결정을 내려야 합니다.

많은 지원자가 케이스 인터뷰를 브레인스토밍처럼 답하다가 끝냅니다. 하지만 면접관이 보고 싶은 것은 아이디어 양보다 구조화된 사고 방식입니다.

## 자주 하는 실수 5가지

1. **질문을 듣자마자 바로 답하는 실수**
2. **지표를 정의하지 않는 실수**
3. **가설을 하나만 두는 실수**
4. **데이터 계획을 추상적으로 말하는 실수**
5. **결정 없이 끝내는 실수**

## 실무에서는 이렇게 나타납니다

빅테크의 PM, 분석가, 사이언티스트 면접에서 케이스 스타일 질문 비중은 높습니다. 실제 업무가 늘 애매한 문제를 구조화하는 과정이기 때문입니다.

## 시니어는 이렇게 생각합니다

- 명확화부터 합니다.
- 북극성 지표를 먼저 고릅니다.
- 세 가지 가설을 세웁니다.
- 데이터 계획을 구체적으로 말합니다.
- 마지막에 결정을 닫습니다.

## 체크리스트

- [ ] 명확화 질문 세 가지를 준비했다.
- [ ] 핵심 지표와 보조 지표를 구분할 수 있다.
- [ ] 서로 다른 성격의 가설 세 가지를 세울 수 있다.
- [ ] 추천 액션과 후속 측정 계획까지 말할 수 있다.

## 연습 문제

1. north star metric을 한 줄로 설명해 보세요.
2. trade-off의 예를 한 줄로 적어 보세요.
3. 좋은 명확화 질문의 기준을 한 줄로 정리해 보세요.

## 정리 및 다음 단계

케이스 인터뷰는 숫자를 많이 아는 사람보다, 애매한 상황을 구조화할 줄 아는 사람에게 유리합니다. 문제를 명확히 하고, 지표를 정하고, 가설과 데이터 계획을 세운 뒤, 마지막에 결정을 내려야 답변이 완성됩니다.

다음 글에서는 첫 데이터 직무에 들어간 뒤 90일 동안 무엇을 먼저 해야 하는지 살펴보겠습니다.

<!-- toc:begin -->
- [데이터 직무란 무엇인가](./01-what-is-data-career.md)
- [분석가 vs 사이언티스트 vs 엔지니어](./02-analyst-scientist-engineer.md)
- [학습 경로 설계](./03-learning-path.md)
- [데이터 포트폴리오](./04-data-portfolio.md)
- [SQL과 분석 인터뷰](./05-sql-and-analytics-interview.md)
- [ML 인터뷰](./06-ml-interview.md)
- **케이스 인터뷰 (현재 글)**
- 첫 직장 적응 (예정)
- 도메인 전문성 쌓기 (예정)
- 시니어 데이터 직무로 가는 길 (예정)
<!-- toc:end -->

## 참고 자료

- [Lewis C. Lin - Decode and Conquer](https://www.lewis-lin.com/decode-and-conquer)
- [Cracking the PM Interview](https://www.crackingthepminterview.com/)
- [Ben Thompson - Stratechery](https://stratechery.com/)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, CaseInterview, ProductSense, Metrics, Beginner
