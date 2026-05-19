---
series: model-evaluation-101
episode: 9
title: 오류 분석으로 약점 찾기
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
  - ErrorAnalysis
  - Slicing
  - Debugging
  - scikit-learn
seo_description: 평균 점수에 가려진 모델의 취약점을 파악하기 위한 오류 분석 기법을 소개하고, 실패 패턴을 찾아 모델을 개선합니다.
last_reviewed: '2026-05-15'
---

# 오류 분석으로 약점 찾기

전체 점수는 모델이 얼마나 잘하는지 대략 알려 줍니다. 하지만 모델을 실제로 고치려면 그 숫자만으로는 부족합니다. 정확도 92%라는 결과는 그럴듯하지만, 어디서 틀렸는지, 어떤 사용자 집단에서 약한지, false positive와 false negative 중 무엇이 더 큰지까지는 말해 주지 못합니다.

그래서 개선 작업의 출발점은 종종 더 좋은 지표를 찾는 일이 아니라, 틀린 예측을 더 잘 분해하는 일입니다. 오류 분석은 평균 점수 뒤에 숨어 있는 패턴을 꺼내서 다음 실험의 우선순위를 정하게 도와줍니다.

이 글은 Model Evaluation 101 시리즈의 9번째 글입니다.

---

## 이 글에서 다룰 문제

- 전체 점수가 비슷한 두 모델은 어디에서 다르게 실패할까요?
- 슬라이스 분석은 어떤 약점을 드러내 줄까요?
- false positive와 false negative를 왜 나눠 봐야 할까요?
- 신뢰도 구간별 오류율은 무엇을 말해 줄까요?
- 모델 문제와 라벨 문제를 어떻게 구분할 수 있을까요?

> 오류 분석의 핵심은 평균 점수 뒤에 숨은 실패 패턴을 드러내는 데 있습니다. 어떤 세그먼트가 약한지, 어떤 오류 유형이 많은지, 어떤 샘플이 애매한지 분리해야 다음 개선 실험이 정확해집니다.

## 왜 이 글이 중요한가

모델은 대개 전체 평균보다 특정 구간에서 더 위험하게 무너집니다. 특정 상품군, 특정 지역, 특정 입력 범위에서만 성능이 나빠질 수 있습니다. 이런 문제는 전체 점수만 보고 있으면 거의 보이지 않습니다.

오류 분석은 그래서 성능 향상뿐 아니라 신뢰성과 공정성 문제에도 직접 연결됩니다. 평균적으로 괜찮다는 말보다, 어디서 심하게 실패하는지를 아는 편이 운영에 훨씬 더 중요할 때가 많습니다.

## 한눈에 보는 멘탈 모델

![슬라이스 분석과 신뢰도 구간 분석으로 이어지는 오류 해부](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/09/09-01-concept-at-a-glance.ko.png)

*슬라이스 분석과 신뢰도 구간 분석으로 이어지는 오류 해부*
평균을 쪼개면 패턴이 보입니다. 특성별 슬라이스, 오류 유형, 신뢰도 구간을 나눠 보면 같은 모델도 전혀 다른 얼굴을 드러냅니다.

## 핵심 용어

- **슬라이스(slice)**: 특정 조건으로 정의한 데이터 부분집합입니다.
- **혼동 쌍(confusion pair)**: 서로 자주 바뀌어 예측되는 클래스 조합입니다.
- **신뢰도 히스토그램(confidence histogram)**: 예측 확률이 어떤 구간에 몰리는지 보여 주는 분포입니다.
- **어려운 샘플(hard example)**: 반복해서 오분류되는 사례입니다.
- **라벨 노이즈(label noise)**: 정답 라벨 자체가 잘못되었거나 불안정한 상태입니다.

## 오류 분석을 읽는 방식의 전환

좋지 않은 습관은 전체 점수가 높으니 모델도 괜찮다고 결론 내리는 것입니다. 그렇게 하면 개선 작업은 늘 막연해집니다. 무엇을 더 수집하고, 무엇을 다시 라벨링하고, 어떤 규칙을 조정해야 할지 알 수 없기 때문입니다.

좋은 습관은 먼저 약한 세그먼트를 찾고, 오류 유형을 나누고, 애매한 샘플을 다시 보는 것입니다. 오류 분석은 모델을 비난하는 절차가 아니라 다음 실험을 설계하는 절차입니다.

## 오류 분석 다섯 단계

### 1단계 — 데이터와 모델

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=3000, n_features=8, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
proba = m.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)
```

### 2단계 — 슬라이스 점수

```python
from sklearn.metrics import f1_score
slice_mask = Xte[:, 0] > 0
print("slice + :", f1_score(yte[slice_mask], pred[slice_mask]))
print("slice - :", f1_score(yte[~slice_mask], pred[~slice_mask]))
```

### 3단계 — 오류 유형 분리

```python
fp = (pred == 1) & (yte == 0)
fn = (pred == 0) & (yte == 1)
print("FP:", fp.sum(), "FN:", fn.sum())
```

### 4단계 — 신뢰도 구간별 오류율

```python
bins = np.linspace(0, 1, 6)
for lo, hi in zip(bins[:-1], bins[1:]):
    m_ = (proba >= lo) & (proba < hi)
    if m_.sum():
        err = (pred[m_] != yte[m_]).mean()
        print(round(lo, 1), round(hi, 1), "err:", round(err, 3))
```

### 5단계 — 가장 애매한 샘플 찾기

```python
order = np.argsort(np.abs(proba - 0.5))[:10]
print("ambiguous indices:", order.tolist())
```

**예상 결과:** 전체 점수 하나 대신 약한 슬라이스, FP/FN 비율, 확신도 구간별 오류율, 라벨 재검토 후보가 함께 나와야 합니다. 그래야 다음 실험이 막연한 개선이 아니라 구체적인 처방으로 이어집니다.

## 이 코드에서 먼저 봐야 할 점

두 번째 단계는 슬라이스 분석의 출발점입니다. 전체 점수는 괜찮아 보여도 특정 구간의 F1이 크게 떨어질 수 있습니다. 세 번째 단계는 false positive와 false negative가 서로 다른 처방을 요구한다는 사실을 보여 줍니다.

네 번째 단계는 확신도와 오류율의 관계를 드러냅니다. 모델이 자신 있어 하는 구간에서 자주 틀린다면, 단순한 분류 문제가 아니라 보정이나 라벨 품질 문제를 의심해야 합니다. 다섯 번째 단계의 애매한 샘플은 라벨 재검토 후보가 됩니다.

## 자주 헷갈리는 지점

첫째, 슬라이스를 결과를 본 뒤에만 정하면 체리피킹이 되기 쉽습니다. 가능하면 중요한 세그먼트는 미리 정의해 두는 편이 좋습니다. 둘째, false positive와 false negative를 한데 묶으면 실제 비용 구조가 사라집니다.

셋째, 모델이 틀렸다고 해서 항상 모델이 문제인 것은 아닙니다. 애매한 샘플을 들여다보면 라벨이 흔들리거나 규칙 자체가 불명확한 경우도 자주 나옵니다. 오류 분석은 모델과 데이터의 책임을 나누는 작업이기도 합니다.

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 평균보다 가장 약한 슬라이스를 먼저 봅니다. 운영 사고는 대개 평균 성능이 아니라 특정 조건에서의 급격한 실패로 시작되기 때문입니다. 그래서 오류 분석은 성능 향상 도구이면서 동시에 리스크 관리 도구입니다.

또한 개선책을 오류 유형에 맞춰 다르게 가져갑니다. threshold 조정, 데이터 추가 수집, 라벨 재검토, 특성 개선은 각각 다른 문제에 대응합니다. 오류 분석이 좋아야 처방도 정확해집니다.

## 점검 목록

- [ ] 최소 두 개 이상의 슬라이스를 확인합니다.
- [ ] false positive와 false negative를 분리해 봅니다.
- [ ] 신뢰도 구간별 오류율을 확인합니다.
- [ ] 애매한 샘플의 라벨을 점검합니다.

## 정리

오류 분석은 평균 점수의 뒤편을 보는 작업입니다. 어디서 틀리는지, 어떻게 틀리는지, 왜 틀리는지를 분리해야 개선의 방향이 생깁니다. 다음 글에서는 지금까지의 평가 결과를 한 장의 문서로 정리하는 평가 리포트 작성으로 시리즈를 마무리하겠습니다.

<!-- toc:begin -->
- [모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [정확도의 한계](./03-limits-of-accuracy.md)
- [정밀도와 재현율](./04-precision-and-recall.md)
- [F1 점수](./05-f1-score.md)
- [ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [확률 보정 이해하기](./07-calibration.md)
- [교차 검증 이해하기](./08-cross-validation.md)
- **오류 분석으로 약점 찾기 (현재 글)**
- 평가 리포트 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Model debugging](https://developers.google.com/machine-learning/testing-debugging)
- [Kaggle — Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning)
- [Andrew Ng — Error analysis](https://www.deeplearning.ai/the-batch/issue-115/)

Tags: ModelEvaluation, ErrorAnalysis, Slicing, Debugging, scikit-learn
