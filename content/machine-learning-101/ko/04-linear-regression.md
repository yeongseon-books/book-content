---
series: machine-learning-101
episode: 4
title: "Machine Learning 101 (4/10): Linear Regression"
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
  - LinearRegression
  - Regression
  - scikit-learn
  - Beginner
seo_description: 선형 회귀의 직관, 평균제곱오차와 R-squared, 잔차 해석까지 scikit-learn 예제로 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (4/10): Linear Regression

차트 위에 점이 대체로 직선처럼 보인다고 해서 바로 설명이 끝나는 것은 아닙니다. 직선 하나로 변동의 큰 부분을 설명할 수 있다면 그것만으로도 매우 강한 모델이 될 수 있지만, 반대로 그 직선이 무엇을 설명하지 못하는지도 함께 봐야 합니다. 선형 회귀는 단순한 만큼 속도가 빠르고, 그만큼 베이스라인으로도 강력합니다.

이 글은 Machine Learning 101 시리즈의 네 번째 글입니다. 여기서는 선형 회귀의 식과 직관, 평균제곱오차, R-squared, 잔차 해석을 함께 보면서 왜 이 모델이 여전히 가장 먼저 돌려 봐야 하는 기준선인지 정리하겠습니다.

## 먼저 던지는 질문

- 선형 회귀 식은 어떤 방식으로 예측값을 만들까요?
- 평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?
- R-squared는 정확히 무엇을 설명할까요?

## 큰 그림

![Machine Learning 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/04/04-01-diagram.ko.png)

*Machine Learning 101 4장 흐름 개요*

이 그림에서는 Linear Regression를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Linear Regression의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

선형 회귀는 해석이 쉽고 빠르며, 생각보다 강력합니다. 그래서 가장 먼저 돌려 보는 편이 좋습니다. 베이스라인이 없으면 더 복잡한 모델을 쓸 정당성도 약해집니다.

## 한눈에 보는 개념

## 핵심 용어

- **가중치 `w`**: 각 피처가 예측에 기여하는 정도입니다.
- **절편 `b`**: 기준 수준의 예측값입니다.
- **MSE**: 평균제곱오차입니다.
- **R-squared**: 모델이 설명한 분산의 비율입니다.
- **잔차(Residual)**: `y - y_hat`입니다.

## Before/After

**Before**: "그래프상 직선처럼 보인다"는 인상만 있고 수치 검증은 없습니다.

**After**: 모델, 지표, 잔차를 함께 보며 세 단계로 검증합니다.

## 실습: 5단계로 보는 회귀

### Step 1 — 데이터

```python
from sklearn.datasets import fetch_california_housing
X, y = fetch_california_housing(return_X_y=True)
```

### Step 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
```

### Step 3 — 학습

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(Xtr, ytr)
```

### Step 4 — 평가

```python
from sklearn.metrics import mean_squared_error, r2_score
pred = model.predict(Xte)
print("MSE:", mean_squared_error(yte, pred))
print("R^2:", r2_score(yte, pred))
```

### Step 5 — 계수 확인

```python
for name, coef in zip(range(Xtr.shape[1]), model.coef_):
    print(f"x{name}: {coef:.3f}")
```

**예상 출력:** MSE, `R^2`, 그리고 부호가 있는 계수 목록이 출력됩니다. 여기서 먼저 볼 것은 절대적인 점수보다 **계수 방향이 상식과 맞는지**, 그리고 잔차가 직선 모델로 설명되지 않는 패턴을 보이는지입니다.

## 이 코드에서 먼저 봐야 할 점

- `coef_`의 부호와 크기가 해석의 중심입니다.
- R-squared가 낮다면 비선형성이 숨어 있다는 신호일 수 있습니다.
- MSE는 오차를 제곱하기 때문에 이상치에 특히 민감합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- `R^2`가 낮고 잔차에 곡선 패턴이 보이면, 선형 모델을 버리기 전에 **비선형 피처**가 빠졌는지 봐야 합니다.
- 계수가 실행마다 크게 흔들리면 **다중공선성**과 **스케일 차이**를 먼저 점검해야 합니다.
- 일부 샘플이 오차를 지배하면, 이상치를 치울지 남길지 자체가 모델링 결정이라는 점을 드러내야 합니다.

## 자주 하는 실수 5가지

1. **스케일 차이를 무시한 채 계수를 바로 비교합니다.**
2. **다중공선성 때문에 계수가 흔들리는 상황을 놓칩니다.**
3. **잔차 플롯을 생략합니다.**
4. **이상치가 직선을 끌고 가는 상황을 방치합니다.**
5. **훈련 범위를 벗어난 구간까지 외삽합니다.**

## 실무에서는 이렇게 나타납니다

가격 책정, 수요 모델링, A/B 효과 추정처럼 이해관계자가 블랙박스보다 **해석 가능한 레버**를 원하는 영역에서는 선형 회귀가 여전히 중심에 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 항상 **베이스라인**에서 출발합니다.
- 해석 가능성은 기술 옵션이 아니라 **비즈니스 도구**입니다.
- 잔차는 모델의 일기장과 같습니다.
- 계수를 비교하기 전에는 표준화를 합니다.
- 규제가 필요하면 Ridge나 Lasso를 더합니다.

## 체크리스트

- [ ] MSE와 R-squared를 함께 보고합니다.
- [ ] 잔차를 시각화합니다.
- [ ] 계수를 읽기 전에 피처를 스케일링합니다.
- [ ] 외삽 위험을 명시적으로 표시합니다.

## 연습 문제

1. `PolynomialFeatures(degree=2)`를 추가하고 R-squared 변화를 관찰해 보세요.
2. 예측값 대비 잔차를 그린 뒤 어떤 패턴이 보이는지 설명해 보세요.
3. `Ridge(alpha=1.0)`와 `LinearRegression`의 계수 크기를 비교해 보세요.

## 정리

선형 회귀는 모든 회귀 작업의 출발점입니다. 단순하지만 강력하고, 숫자로 검증할 수 있으며, 해석 가능한 기준선을 제공합니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 선형 회귀는 `y_hat = Xw + b` 구조로 예측합니다. 둘째, MSE와 R-squared는 서로 다른 각도에서 성능을 읽게 해 줍니다. 셋째, 잔차 분석이 빠지면 모델 가정 검증도 빠집니다. 넷째, 복잡한 모델을 쓰기 전에는 항상 선형 회귀 베이스라인을 먼저 확인해야 합니다.

다음 글에서는 분류의 기본 모델인 Logistic Regression으로 넘어가겠습니다.

## 처음 질문으로 돌아가기

- **선형 회귀 식은 어떤 방식으로 예측값을 만들까요?**
  - 본문의 기준은 Linear Regression를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **R-squared는 정확히 무엇을 설명할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Machine Learning 101 (1/10): Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): 지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- **Linear Regression (현재 글)**
- Logistic Regression (예정)
- Decision Tree와 Random Forest (예정)
- Clustering (예정)
- Overfitting과 Regularization (예정)
- Model Evaluation (예정)
- ML 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Linear models](https://scikit-learn.org/stable/modules/linear_model.html)
- [An Introduction to Statistical Learning — James et al.](https://www.statlearning.com/)
- [Seeing Theory — Regression](https://seeing-theory.brown.edu/regression-analysis/index.html)
- [StatQuest — Linear Regression](https://www.youtube.com/watch?v=nk2CQITm_eo)

Tags: MachineLearning, LinearRegression, Regression, scikit-learn, Beginner
