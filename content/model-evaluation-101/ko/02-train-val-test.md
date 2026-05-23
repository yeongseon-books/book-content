---
series: model-evaluation-101
episode: 2
title: "Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - TrainValTest
  - DataLeakage
  - CrossValidation
  - scikit-learn
seo_description: 일반화 성능 보장을 위한 데이터 분할 방법과 데이터 누수를 방지하여 신뢰할 수 있는 실험 환경을 구축하는 원칙을 설명합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기

이 글은 Model Evaluation 101 시리즈의 2번째 글입니다.

모델 성능은 지표를 계산하는 순간보다 데이터를 나누는 순간에 이미 상당 부분 결정됩니다. 분할이 잘못되면 이후에 나오는 모든 점수는 그럴듯해 보여도 신뢰할 수 없습니다. 특히 전처리를 먼저 해 버리거나, 시계열 데이터를 무작위로 섞거나, 같은 사용자가 여러 세트에 동시에 들어가면 성능은 쉽게 부풀려집니다.

그래서 train, validation, test의 역할 분리는 단순한 교과서 규칙이 아닙니다. 어떤 데이터로 학습하고, 어떤 데이터로 고르고, 어떤 데이터로 최종 확인할지 구분하는 훈련이 평가의 바닥을 만듭니다.

![Model Evaluation 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/02/02-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 2장 흐름 개요*

## 먼저 던지는 질문

- train, validation, test는 각각 무엇을 맡아야 할까요?
- 왜 validation과 test를 같은 용도로 쓰면 안 될까요?
- 데이터 누수는 어떤 경로로 가장 자주 들어올까요?

## 왜 이 글이 중요한가

분할 전략이 잘못되면 비교 자체가 불가능해집니다. 두 모델 중 하나가 더 좋아 보이더라도, 그 차이가 모델의 힘인지 누수의 부산물인지 알 수 없기 때문입니다. 평가가 아니라 착시가 되는 셈입니다.

실무에서는 특히 세 가지 누수가 자주 나옵니다. 전체 데이터에 스케일러를 먼저 맞추는 전처리 누수, 미래 정보를 과거 학습에 흘려보내는 시계열 누수, 같은 사용자나 문서가 서로 다른 분할에 등장하는 그룹 누수입니다. 이 셋을 막는 것만으로도 평가의 질이 크게 올라갑니다.

## 한눈에 보는 멘탈 모델

먼저 나누고, 그다음 학습해야 합니다. 전처리 역시 같은 원칙을 따릅니다. 나누기 전에 전체를 들여다보며 통계를 맞추는 순간, 답이 조금씩 새어 들어갑니다.

## 핵심 용어

- **훈련 세트(train)**: 모델 파라미터를 학습하는 데이터입니다.
- **검증 세트(validation)**: 하이퍼파라미터를 조정하고 모델을 고르는 데이터입니다.
- **테스트 세트(test)**: 최종 성능을 마지막으로 확인하는 데이터입니다.
- **누수(leakage)**: 정답이나 미래 정보가 부적절하게 학습 과정으로 스며드는 현상입니다.
- **그룹 분할(group split)**: 같은 개체가 서로 다른 분할에 동시에 나오지 않도록 막는 방식입니다.

## 분할을 잘못 볼 때와 제대로 볼 때

잘못된 방식은 전체 데이터를 다 본 뒤 일부를 떼어 점수를 확인하는 흐름입니다. 이 방법은 빠르지만, 실제로는 평가 기준을 스스로 흐리게 만듭니다. 반대로 제대로 된 방식은 train, validation, test를 분리하고, 전처리와 학습도 분할 이후에만 수행하는 것입니다.

이 차이는 점수 한두 자리보다 더 중요합니다. 분할 원칙이 지켜져야 이후의 정확도, F1, AUC도 해석할 수 있습니다.

## 다섯 가지 분할 패턴 실습

### 1단계 — 기본 분할

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
Xtrv, Xte, ytrv, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
Xtr, Xva, ytr, yva = train_test_split(Xtrv, ytrv, test_size=0.25, stratify=ytrv, random_state=42)
print(Xtr.shape, Xva.shape, Xte.shape)
```

### 2단계 — 누수 시연

```python
from sklearn.preprocessing import StandardScaler
sc_bad = StandardScaler().fit(X)
sc_ok = StandardScaler().fit(Xtr)
```

### 3단계 — 시계열 분할

```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
ts = np.arange(20).reshape(-1, 1)
for tr, te in TimeSeriesSplit(n_splits=3).split(ts):
    print(tr[-1], te[0])
```

### 4단계 — 그룹 분할

```python
from sklearn.model_selection import GroupKFold
groups = np.array([1,1,1,2,2,3,3,3,4,4])
X = np.arange(10).reshape(-1, 1); y = np.arange(10)
for tr, te in GroupKFold(n_splits=2).split(X, y, groups):
    print(set(groups[te]))
```

### 5단계 — 분할 후 학습

```python
from sklearn.linear_model import LogisticRegression
sc = StandardScaler().fit(Xtr)
m = LogisticRegression(max_iter=1000).fit(sc.transform(Xtr), ytr)
print("valid:", m.score(sc.transform(Xva), yva))
```

**예상 결과:** 전체 데이터에 맞춘 스케일러와 훈련 세트에만 맞춘 스케일러의 차이가 왜 중요한지 감이 와야 합니다. 시간 순서와 그룹 경계를 지키는 분할이 단순한 형식이 아니라 평가 신뢰도를 지키는 장치라는 점이 핵심입니다.

## 이 코드에서 먼저 봐야 할 점

두 번째 코드가 이 글의 핵심입니다. 전체 데이터에 `StandardScaler`를 맞추면 훈련 전에 이미 검증과 테스트의 통계를 본 셈이 됩니다. 아주 작은 정보 누수처럼 보여도 비교가 반복될수록 성능은 부풀려집니다.

세 번째와 네 번째 코드는 분할 방식이 데이터 성격에 따라 달라져야 한다는 점을 보여 줍니다. 시간 순서가 중요한 데이터는 과거에서 미래로 가야 하고, 같은 사용자가 여러 샘플로 나뉜 데이터는 그룹 단위로 묶어야 합니다.

## 자주 헷갈리는 지점

많이 나오는 오해는 탐색적 데이터 분석도 금지라고 생각하는 것입니다. 분할 전에 데이터를 이해하는 일은 괜찮습니다. 문제는 전처리의 `fit`이나 기준선 결정이 분할 전 전체 데이터를 먹는 순간입니다.

또 다른 오해는 테스트 세트를 자주 봐도 괜찮다는 생각입니다. 하지만 테스트를 반복해서 확인하는 순간 그 세트는 더 이상 최종 검증 세트가 아닙니다. 검증 세트와 같은 역할로 전락합니다.

## 실무에서는 이렇게 생각한다

강한 팀은 분할 전략을 모델보다 먼저 리뷰합니다. 추천 시스템이면 사용자나 세션 누수를 먼저 의심하고, 금융 데이터면 시간 순서를 먼저 확인합니다. 모델 구조를 바꾸는 것보다 분할 원칙을 바로잡는 편이 더 큰 차이를 내는 경우도 많습니다.

또한 각 세트의 역할을 문서로 남깁니다. 무엇이 튜닝용이고 무엇이 최종 보고용인지 분명하지 않으면, 시간이 지난 뒤 누구나 테스트 점수를 다시 쓰고 싶어집니다. 평가의 엄격함은 기억이 아니라 규칙에서 나옵니다.

## 점검 목록

- [ ] train, validation, test를 분리해 사용합니다.
- [ ] 전처리 `fit`은 분할 이후에만 수행합니다.
- [ ] 시계열 데이터는 시간 순서를 지켜 분할합니다.
- [ ] 그룹 정보가 있으면 명시적으로 분리합니다.

## 정리

데이터 분할은 평가의 준비 단계가 아니라 평가 그 자체의 일부입니다. train은 학습, validation은 선택, test는 최종 확인이라는 역할을 끝까지 지켜야 점수가 의미를 가집니다. 다음 글에서는 이렇게 준비된 평가 위에서 정확도라는 지표가 어디까지 유효한지 봅니다.

## 처음 질문으로 돌아가기

- **train, validation, test는 각각 무엇을 맡아야 할까요?**
  - 본문의 기준은 훈련·검증·테스트 데이터 나누기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 validation과 test를 같은 용도로 쓰면 안 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **데이터 누수는 어떤 경로로 가장 자주 들어올까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- **훈련·검증·테스트 데이터 나누기 (현재 글)**
- 정확도의 한계 (예정)
- 정밀도와 재현율 (예정)
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, TrainValTest, DataLeakage, CrossValidation, scikit-learn
