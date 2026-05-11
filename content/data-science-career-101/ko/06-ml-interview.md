---
series: data-science-career-101
episode: 6
title: ML 인터뷰
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataCareer
  - ML
  - Interview
  - Modeling
  - Beginner
seo_description: ML 인터뷰의 핵심 영역과 답변 구조를 정리한 글
last_reviewed: '2026-05-11'
---

# ML 인터뷰

머신러닝 인터뷰를 준비할 때 많은 지원자가 모델 이름을 많이 아는 것이 유리하다고 생각합니다. 물론 알고리즘 이해도는 중요합니다. 하지만 실제 인터뷰에서는 어떤 모델을 아느냐보다, 어떤 문제에서 왜 그 모델을 고르는지, 어떤 지표로 평가할지, 운영 단계에서 어떤 함정을 조심할지를 더 자주 묻습니다.

즉 ML 인터뷰는 모델 암기 시험이 아니라 문제 해결 사고를 보는 자리입니다. 편향-분산 같은 기초 개념, 평가 지표 선택, 데이터 누수와 드리프트 같은 실무 함정, 그리고 서빙과 재학습을 포함한 시스템 관점까지 함께 말할 수 있어야 답변이 단단해집니다.

## 이 글에서 다룰 문제

- ML 인터뷰는 어떤 영역을 중심으로 질문할까요?
- 모델 선택을 설명할 때 무엇을 먼저 말해야 할까요?
- 평가 지표는 왜 문제 정의와 함께 다뤄야 할까요?
- 데이터 누수와 클래스 불균형 같은 함정은 왜 자주 나올까요?
- 모델을 넘어서 시스템 관점으로 답해야 하는 이유는 무엇일까요?

> 좋은 ML 답변은 “이 모델이 좋다”에서 끝나지 않고, 문제 정의와 지표와 운영 리스크까지 함께 설명합니다.

## 한눈에 보는 전체 흐름

```mermaid
flowchart LR
    P[문제] --> M[모델]
    M --> E[평가]
    E --> D[배포]
```

이 흐름은 ML 인터뷰의 답변 구조로 그대로 써도 좋습니다. 문제를 정의하고, 그 문제에 맞는 모델을 고르고, 어떤 지표로 평가할지 설명한 뒤, 배포와 모니터링까지 이어지면 훨씬 실무적인 답변이 됩니다.

## 핵심 용어

- **bias-variance**: 과소적합과 과적합 사이의 균형입니다.
- **overfitting**: 학습 데이터만 지나치게 외워 일반화가 약해진 상태입니다.
- **AUC**: ROC 곡선 아래 면적입니다.
- **precision/recall**: 오탐과 미탐 사이의 균형을 보여 주는 지표입니다.
- **drift**: 시간이 지나며 데이터 분포가 달라지는 현상입니다.

## Before/After

**Before**: "Random Forest가 늘 무난한 정답이라고 생각했다."

**After**: "문제 정의와 평가 지표를 기준으로 모델을 고르고 설명할 수 있다."

## 실습: 자주 쓰는 다섯 가지 답변 패턴

### Step 1 — Fundamentals

```text
Explain bias-variance in one line.
```

기초 개념 질문은 짧지만 강합니다. 편향-분산을 한 줄로 설명할 수 있는지, 과적합을 예시와 함께 말할 수 있는지 같은 질문으로 기본기를 확인합니다.

### Step 2 — Model Choice

```text
- assumptions: linear vs tree vs neural
- data size, interpretability
```

모델 선택 문제에서는 무엇을 예측하려는지, 데이터 양이 어떤지, 해석 가능성이 중요한지, 특징 간 관계가 비선형인지 등을 함께 봐야 합니다. 모델 이름을 나열하는 것보다 선택 기준을 말하는 편이 훨씬 강한 답변입니다.

### Step 3 — Evaluation

```python
from sklearn.metrics import precision_score, recall_score, roc_auc_score
```

평가 지표는 문제 맥락과 분리해서 말할 수 없습니다. 예를 들어 사기 탐지처럼 false negative 비용이 큰 문제에서는 recall이 더 중요할 수 있고, 운영 비용이 큰 문제에서는 precision을 더 보게 될 수 있습니다.

### Step 4 — Production Traps

```text
- data leakage
- class imbalance
- time leakage
```

이 함정들을 알고 있다는 사실 자체가 실무 경험 신호가 됩니다. 특히 time leakage처럼 시계열에서 자주 터지는 문제를 언급하면, 단순 모델 학습을 넘어 운영과 검증까지 생각하는 사람이라는 인상을 줍니다.

### Step 5 — System Design

```text
- data -> train -> serve -> monitor
- retraining cadence
- drift detection
```

모델 하나를 잘 만드는 것과 시스템을 운영하는 것은 다른 일입니다. 인터뷰 후반으로 갈수록 데이터 수집, 학습, 서빙, 모니터링, 재학습 주기를 하나의 흐름으로 설명할 수 있는지 보게 됩니다.

## 이 예시에서 봐야 할 점

- 결국 지표가 답변의 방향을 결정합니다.
- 실무 함정을 먼저 언급하면 답변의 깊이가 올라갑니다.
- 모델을 개별 객체가 아니라 시스템 일부로 보는 태도가 중요합니다.

많은 지원자가 정확도나 AUC만 말하고 끝내지만, 실제 서비스에서는 그것만으로 충분하지 않습니다. 데이터 분포가 바뀌는지, 예측 결과가 의사결정에 어떤 비용을 만드는지, 재학습은 얼마나 자주 할지까지 생각해야 하기 때문입니다. 그래서 ML 인터뷰는 기술 질문 같지만, 사실상 운영 질문이기도 합니다.

## 자주 하는 실수 5가지

1. **모든 문제에 같은 모델을 답으로 내는 실수**
2. **AUC만 보고 다른 지표를 보지 않는 실수**
3. **데이터 누수를 모르는 실수**
4. **재학습 계획을 생각하지 않는 실수**
5. **해석 가능성을 가볍게 보는 실수**

## 실무에서는 이렇게 나타납니다

면접관은 모델 정확도보다 운영 관점을 더 오래 묻는 경우가 많습니다. 데이터가 언제 들어오고, 예측이 어디서 쓰이고, 어떤 지표로 모니터링할지, 분포가 바뀌면 어떻게 대응할지를 물어보는 식입니다. 그만큼 현업의 ML은 모델 선택보다 시스템 운영에 더 가깝습니다.

## 시니어는 이렇게 생각합니다

- 문제 정의에서 시작합니다.
- 평가 지표가 모델 선택을 이끕니다.
- 함정을 먼저 떠올립니다.
- 개별 모델보다 시스템 수준에서 봅니다.
- 드리프트와 재학습 계획까지 답변에 포함합니다.

## 체크리스트

- [ ] 주요 평가 지표 다섯 개를 설명할 수 있다.
- [ ] 서로 다른 모델 세 가지를 비교할 수 있다.
- [ ] 실무 함정 세 가지를 예와 함께 말할 수 있다.
- [ ] 간단한 ML 시스템 흐름도를 머릿속에 그릴 수 있다.

## 연습 문제

1. overfitting을 한 줄로 설명해 보세요.
2. drift의 예를 한 줄로 적어 보세요.
3. AUC와 recall의 차이를 한 줄로 정리해 보세요.

## 정리 및 다음 단계

ML 인터뷰에서 중요한 것은 모델 이름을 많이 아는 일이 아니라, 문제와 지표와 운영 리스크를 함께 엮어 설명하는 일입니다. 기초 개념을 분명히 말하고, 모델 선택 기준을 설명하고, 평가 지표를 문제 맥락에 맞춰 고르고, 누수와 드리프트 같은 함정을 짚어 낼 수 있어야 답변이 단단해집니다.

다음 글에서는 제품 감각과 사고 구조를 많이 보는 케이스 인터뷰를 다뤄 보겠습니다.

<!-- toc:begin -->
- [데이터 직무란 무엇인가](./01-what-is-data-career.md)
- [분석가 vs 사이언티스트 vs 엔지니어](./02-analyst-scientist-engineer.md)
- [학습 경로 설계](./03-learning-path.md)
- [데이터 포트폴리오](./04-data-portfolio.md)
- [SQL과 분석 인터뷰](./05-sql-and-analytics-interview.md)
- **ML 인터뷰 (현재 글)**
- 케이스 인터뷰 (예정)
- 첫 직장 적응 (예정)
- 도메인 전문성 쌓기 (예정)
- 시니어 데이터 직무로 가는 길 (예정)
<!-- toc:end -->

## 참고 자료

- [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [scikit-learn metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [ML Interview Book](https://huyenchip.com/ml-interviews-book/)
- [Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: DataCareer, ML, Interview, Modeling, Beginner
