---
series: machine-learning-101
episode: 8
title: "Machine Learning 101 (8/10): Overfitting과 Regularization"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - Overfitting
  - Regularization
  - Ridge
  - Lasso
seo_description: 과적합과 과소적합의 신호, 편향-분산, Ridge·Lasso·ElasticNet의 차이를 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (8/10): Overfitting과 Regularization

훈련 점수는 99%인데 테스트 점수는 60%라면 모델이 똑똑한 것인지, 아니면 데이터를 외운 것인지부터 의심해야 합니다. 머신러닝에서 성능 개선의 절반은 더 강한 모델을 찾는 일이 아니라, 모델이 어디서 잡음을 외우고 있는지 진단하는 일에 가깝습니다. 과적합과 과소적합을 구분하지 못하면 점수가 좋아 보여도 실제 일반화는 오히려 나빠질 수 있습니다.

이 글은 머신러닝 101 시리즈의 8번째 글입니다. 여기서는 과적합과 과소적합의 신호, 편향-분산 트레이드오프, Ridge·Lasso·ElasticNet 같은 정규화 기법이 일반화를 어떻게 되찾아 주는지 봅니다.

![Machine Learning 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/08/08-01-diagram.ko.png)
*Machine Learning 101 8장 흐름 개요*
> 과적합은 모델이 노이즈를 외워 버리는 현상이고, 정규화는 그 모델을 일반화되는 패턴 쪽으로 다시 끌어당기는 페널티입니다.

## 이 글에서 다룰 문제

- 과적합과 과소적합은 어떤 신호로 구분할까요?
- 편향-분산 트레이드오프는 실무에서 어떤 판단을 바꿀까요?
- Ridge, Lasso, ElasticNet은 언제 각각 써야 할까요?
- 정규화 강도(alpha)를 잘못 설정하면 어떤 결과가 나올까요?
- 학습 곡선으로 과적합을 조기에 발견하는 방법은 무엇일까요?

모델 개선의 절반은 정규화라고 해도 과장이 아닙니다. 모델 용량이 클수록 정규화가 모델을 살려 줍니다.

- 과적합: 훈련 성능은 좋지만 테스트 성능은 약한 상태입니다.
- **과소적합**: 훈련과 테스트 모두 약한 상태입니다.
- **편향(Bias)**: 모델 가정에 내장된 오차입니다.
- **분산(Variance)**: 데이터 변화에 민감한 정도입니다.
- **L1 / L2**: 계수 크기에 패널티를 주는 방식입니다.

## 적용 전과 후
**Before**: "모델을 더 크게 만들자"고 해서 더 심하게 과적합합니다.

**After**: 먼저 학습 곡선으로 진단하고, 그다음 정규화를 적용합니다.

## 실습: 5단계로 정규화 비교하기

### 단계 1 — 데이터

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### 단계 2 — Linear

```python
from sklearn.linear_model import LinearRegression
lin = LinearRegression().fit(Xtr, ytr)
print("lin :", lin.score(Xte, yte))
```

### 단계 3 — Ridge (L2)
```python
from sklearn.linear_model import Ridge
ridge = Ridge(alpha=1.0).fit(Xtr, ytr)
print("ridge:", ridge.score(Xte, yte))
```

### 단계 4 — Lasso (L1)
```python
from sklearn.linear_model import Lasso
lasso = Lasso(alpha=0.01).fit(Xtr, ytr)
print("lasso:", lasso.score(Xte, yte), "nz:", (lasso.coef_ != 0).sum())
```

### 단계 5 — Alpha 탐색
```python
import numpy as np
for a in np.logspace(-3, 2, 6):
    s = Ridge(alpha=a).fit(Xtr, ytr).score(Xte, yte)
    print(f"alpha={a:.3g}  R^2={s:.3f}")
```

**예상 출력:** 선형 회귀, Ridge, Lasso 각각의 테스트 점수가 나오고, `alpha`를 바꾸면 성능 곡선이 움직입니다. 어느 값에서도 결과가 시원치 않다면 정규화 강도보다 **피처 품질**이나 **모델 계열**이 먼저 문제일 수 있습니다.

- Lasso는 계수를 0으로 만들어 피처 선택 효과까지 냅니다.
- Ridge는 모든 계수를 부드럽게 줄입니다.
- `alpha`는 감으로 찍는 값이 아니라 교차검증으로 정해야 합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 모델 용량이 커질수록 train-test 간격이 벌어지면, 구조 변경 전에 **정규화**와 **데이터 양**을 먼저 점검해야 합니다.
- Lasso가 실행할 때마다 다른 피처를 고르면, 상관 피처가 많은지 보고 ElasticNet이나 Ridge도 함께 비교해야 합니다.
- train과 test가 둘 다 낮으면 과적합이 아니라 **과소적합**이나 **피처 설계 부족**일 수 있습니다.

## 자주 하는 실수 5가지

1. **스케일링 없이 L1이나 L2를 적용합니다.**
2. **`alpha`를 한 번만 시도하고 끝냅니다.**
3. **훈련 점수만 보고 과적합을 판단합니다.**
4. **상관 피처가 많을 때 Lasso의 불안정성을 무시합니다.**
5. **ElasticNet의 존재를 잊습니다.**

## 실무에서는 이렇게 나타납니다

광고 CTR, 검색 랭킹, 유전체 데이터처럼 고차원 문제에서는 Lasso와 ElasticNet이 피처 선택 도구로도 자주 쓰입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 학습 곡선을 먼저 봅니다.
- 더 많은 데이터는 가장 강한 정규화일 때가 많습니다.
- 드롭아웃과 데이터 증강도 넓게 보면 정규화입니다.
- `RidgeCV`로 `alpha`를 자동 선택하는 편이 실용적입니다.
- 과소적합이라면 모델 용량을 늘려야 합니다.

## 운영 체크리스트

- [ ] 훈련 점수와 테스트 점수를 함께 추적합니다.
- [ ] 학습 곡선을 그립니다.
- [ ] `alpha`를 교차검증으로 정합니다.
- [ ] Lasso가 선택한 피처를 확인합니다.

## 연습 문제

1. `PolynomialFeatures(degree=10)`와 Ridge를 써서 과적합을 재현해 보세요.
2. `RidgeCV`와 수동으로 고른 `alpha`를 비교해 보세요.
3. Lasso가 0으로 줄인 피처 목록을 적어 보세요.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째, 과적합과 과소적합은 어떤 신호로 구분할까요. 둘째, 편향-분산 트레이드오프는 실무에서 어떤 판단을 바꿀까요. 셋째, Ridge, Lasso, ElasticNet은 언제 각각 써야 할까요. 이 기초를 잡아 두면 다음 단계로 넘어갈 때 훨씬 안정적입니다.

## 처음 질문으로 돌아가기

- **과적합과 과소적합은 어떤 신호로 구분할까요?**
  - 과적합과 과소적합은 어떤 신호로 구분할까요 — 본문에서 단계별로 설명합니다.
- **편향-분산 트레이드오프는 무엇을 뜻할까요?**
  - 편향-분산 트레이드오프는 무엇을 뜻할까요 — 본문에서 단계별로 설명합니다.
- **Ridge, Lasso, ElasticNet은 어떻게 다를까요?**
  - Ridge, Lasso, ElasticNet은 어떻게 다를까요 — 본문에서 단계별로 설명합니다.
