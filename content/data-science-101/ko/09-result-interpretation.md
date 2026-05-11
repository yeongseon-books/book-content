---
series: data-science-101
episode: 9
title: 결과 해석
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - Interpretation
  - Storytelling
  - Decision
  - Beginner
seo_description: 모델 출력과 분석 결과를 비즈니스 결정으로 옮기는 5단계 해석 프레임워크와 흔한 인지 함정 정리
last_reviewed: '2026-05-11'
---

# 결과 해석

## 이 글에서 다룰 문제

- 숫자 결과를 어떻게 의사결정 문장으로 바꿀 수 있을까요?
- 왜 숫자와 맥락은 항상 함께 적어야 할까요?
- 효과 크기와 불확실성은 왜 동시에 보고해야 할까요?
- cherry-picking, survivorship bias 같은 함정은 어떻게 결과 해석을 왜곡할까요?
- 좋은 보고서는 왜 반드시 결정 문장으로 끝나야 할까요?

> Data Science 101 시리즈 (9/10)

분석이나 모델링이 끝났다고 해서 일이 끝난 것은 아닙니다. 오히려 가장 어려운 단계가 남아 있을 때가 많습니다. 숫자를 어떻게 읽고, 어디까지 주장하고, 어떤 행동으로 연결할지 정하는 단계입니다. 여기서 결과를 과장하면 잘못된 결정을 부르고, 반대로 지나치게 약하게 말하면 실제로 잡을 수 있었던 기회를 놓치게 됩니다.

좋은 해석은 숫자를 더 크게 보이게 만드는 일이 아닙니다. 숫자 위에 맥락과 불확실성을 겹쳐서, 팀이 과신하지도 않고 주저앉지도 않게 만드는 일입니다. 이 글에서는 결과를 결정으로 옮기는 기본 흐름을 정리하겠습니다.

## 왜 중요한가

해석이 과장되면 의사결정은 자신만만해지지만 틀릴 가능성이 커집니다. 해석이 지나치게 약하면 팀은 계속 미루기만 하고 아무 행동도 하지 못합니다. 결국 중요한 것은 숫자를 숨기지 않고, 불확실성도 숨기지 않으면서도 행동 가능한 결론을 만드는 일입니다.

> 좋은 해석은 과장하지 않지만, 그래도 결정을 가능하게 만듭니다.

## 해석 흐름 한눈에 보기

```mermaid
flowchart LR
    Result["숫자"] --> Context["맥락"]
    Context --> Uncertain["불확실성"]
    Uncertain --> Story["이야기"]
    Story --> Decide["의사결정"]
```

핵심은 숫자 하나만 던지지 않는 것입니다. 숫자에는 언제나 대상, 기간, 표본 크기, 불확실성, 다음 행동이 함께 붙어야 합니다.

## 핵심 용어

- **Confidence Interval**: 추정치 주변의 불확실성 범위입니다.
- **Effect Size**: 차이의 크기 자체를 뜻합니다.
- **Practical Significance**: 통계적으로뿐 아니라 비즈니스적으로 의미 있는 차이인지 보는 관점입니다.
- **Cherry-picking**: 유리한 결과만 골라 보고하는 왜곡입니다.
- **Survivorship Bias**: 살아남은 사례만 보고 실패한 사례를 놓치는 편향입니다.

해석 단계에서는 통계 지식보다 태도가 더 중요할 때도 많습니다. 어떤 결과를 일부러 빼거나, 불확실성을 숨기거나, 한 세그먼트의 결과를 전체로 일반화하는 순간 해석은 쉽게 무너집니다.

## Before / After

**Before**: “정확도가 5% 올랐습니다”라고만 말합니다. 어디서, 누구에게, 얼마나 안정적으로 오른 것인지 알 수 없습니다.

**After**: “유료 사용자 6만 명 기준, 7일 평균 정확도가 89%에서 91%로 상승했고 95% 신뢰구간은 ±0.8%였습니다”처럼 씁니다. 이제야 숫자가 읽히기 시작합니다.

## 5단계 해석

### 1단계 — 숫자를 정확히 적기

```text
A/B test result: conversion 3.2% (control) vs 3.6% (variant)
n = 50,000 per arm
```

먼저 바뀐 숫자를 정확히 적습니다. 모호한 요약보다 원래 수치를 분명히 쓰는 편이 낫습니다. 표본 크기도 함께 써야 무게를 판단할 수 있습니다.

### 2단계 — 신뢰구간 함께 적기

```text
delta = +0.4pp (95% CI: +0.2pp ~ +0.6pp)
```

불확실성을 함께 적는 순간 결과는 훨씬 정직해집니다. 신뢰구간은 “얼마나 불안정한가”를 수치로 보여 주는 좋은 도구입니다.

### 3단계 — 효과 크기 보기

```text
relative lift = +12.5%
```

유의하다는 말만으로는 부족합니다. 차이가 실제로 얼마나 큰지, 비즈니스적으로 행동할 만한 크기인지 확인해야 합니다.

### 4단계 — 맥락 추가하기

```text
campaign window: 2 weeks; segment: paid users; device: desktop only
```

숫자는 맥락 없이 거의 의미가 없습니다. 어떤 기간인지, 어떤 세그먼트인지, 어떤 환경인지 적어야 과도한 일반화를 막을 수 있습니다.

### 5단계 — 의사결정으로 닫기

```text
Decision: roll out to 100% paid desktop users; monitor for 2 more weeks.
```

좋은 보고서는 마지막에 행동을 제안합니다. 무엇을 할지, 누가 볼지, 언제 다시 검토할지까지 쓰면 결과가 실행으로 이어집니다.

## 이 코드에서 주목할 점

- 숫자와 맥락은 항상 한 쌍으로 움직여야 합니다.
- 신뢰구간은 의사결정 위험을 숫자로 드러내 줍니다.
- 보고서는 결정 문장으로 닫힐 때 비로소 실무 산출물이 됩니다.

## 자주 하는 실수 5가지

1. **p-value만 봅니다.** 효과 크기가 작으면 실무 의미가 약할 수 있습니다.
2. **한 세그먼트 결과를 전체에 일반화합니다.** 분산과 차이를 놓칩니다.
3. **좋은 결과만 보고합니다.** 전형적인 cherry-picking입니다.
4. **불확실성을 숨깁니다.** 팀을 과신하게 만듭니다.
5. **결정 문장 없이 보고서를 끝냅니다.** 결국 아무 행동도 일어나지 않습니다.

## 실무에서는 이렇게 드러납니다

실무 데이터 팀은 주간 리뷰에서 숫자 → 맥락 → 신뢰구간 → 결정 순서를 템플릿처럼 씁니다. 어떤 팀은 분석 전에 가설을 미리 적어 두는 pre-registration 습관을 두어 cherry-picking을 줄입니다. 해석의 품질은 종종 개인 역량보다 팀 템플릿에 더 크게 좌우됩니다.

## 시니어는 이렇게 생각합니다

- 불확실성을 말하는 것을 부끄러워하지 않습니다.
- 결과는 항상 결정 문장으로 닫습니다.
- p-value보다 effect size를 더 유심히 봅니다.
- 세그먼트를 나눠 분산을 드러냅니다.
- 리뷰 템플릿 자체를 팀 자산으로 만듭니다.

## 체크리스트

- [ ] 신뢰구간을 함께 적을 수 있습니다.
- [ ] 효과 크기를 읽을 수 있습니다.
- [ ] 세그먼트별로 나눠 보는 습관이 있습니다.
- [ ] 의사결정 문장을 작성할 수 있습니다.

## 연습 문제

1. 과거 분석 하나를 골라 5단계 흐름으로 다시 해석해 보세요.
2. `p=0.04`지만 효과가 0.1%뿐인 결과를 어떻게 보고할지 적어 보세요.
3. cherry-picking을 막기 위한 팀 규칙 세 가지를 적어 보세요.

## 정리 및 다음 글

결과 해석은 분석을 의사결정으로 옮기는 마지막 다리입니다. 숫자를 더 크게 말하는 것이 아니라, 숫자와 맥락과 불확실성을 함께 보여 준 뒤 행동 가능한 문장으로 닫는 일이 핵심입니다. 다음 글에서는 시리즈 전체를 묶어 하나의 데이터 프로젝트를 처음부터 끝까지 따라가 보겠습니다.

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [데이터 수집](./03-data-collection.md)
- [데이터 정제](./04-data-cleaning.md)
- [탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- [시각화](./06-visualization.md)
- [모델링](./07-modeling.md)
- [평가](./08-evaluation.md)
- **결과 해석 (현재 글)**
- 데이터 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)
- [Kahneman — Thinking, Fast and Slow](https://us.macmillan.com/books/9780374533557/thinkingfastandslow)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Microsoft — Trustworthy Online Experiments](https://exp-platform.com/)

Tags: DataScience, Interpretation, Storytelling, Decision, Beginner
