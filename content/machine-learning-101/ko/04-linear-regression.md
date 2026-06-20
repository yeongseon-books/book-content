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

이 글은 머신러닝 101 시리즈의 4번째 글입니다. 여기서는 선형 회귀의 식과 직관, 평균제곱오차, R-squared, 잔차 해석을 함께 보면서 왜 이 모델이 여전히 가장 먼저 돌려 봐야 하는 기준선인지 정리하겠습니다.

![Machine Learning 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/04/04-01-diagram.ko.png)
*Machine Learning 101 4장 흐름 개요*
> 선형 회귀는 모든 데이터까지의 제곱 거리가 가장 작은 단 하나의 직선을 그리는 일이고, 계수·R²·잔차는 모두 그 직선을 다른 각도에서 읽는 도구입니다.

## 이 글에서 다룰 문제

- 선형 회귀 식은 어떤 방식으로 예측값을 만들까요?
- 평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?
- R-squared는 정확히 무엇을 설명할까요?
- 이 기법의 한계는 어디서 드러나고 어떻게 보완할까요?
- 실무 프로젝트에서 이 개념을 적용할 때 가장 먼저 확인해야 할 점은 무엇일까요?

## 비용함수와 경사하강법

선형 회귀는 `y_hat = Xw + b`로 예측하지만, 어떻게 `w`와 `b`를 찾을까요? 답은 **비용함수**를 최소화하는 것입니다.

### 평균제곱오차(MSE)

$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$

오차를 제곱하기 때문에 큰 오차에 무거운 페널티를 줍니다. 그래서 이상치에 민감합니다.

### 경사하강법

경사하강법은 비용함수를 줄이기 위해 기울기 반대 방향으로 파라미터를 조금씩 움직이는 방법입니다.

1. 초기 가중치를 랜덤하게 설정합니다.
2. 현재 위치에서 비용함수의 기울기를 계산합니다.
3. 기울기의 반대 방향으로 가중치를 조금 움직입니다.
4. 수렴할 때까지 반복합니다.

선형 회귀는 경사하강 없이 폐형해로도 풀 수 있지만, 경사하강법의 기초를 이해하면 다른 모델을 다룰 때도 도움이 됩니다.

## Python 예제: Numpy로 직접 구현

```python
import numpy as np

# 간단한 데이터
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# 편향 항 추가 (bias trick)
X_b = np.c_[np.ones((X.shape[0], 1)), X]

# 최소제곱 폐형해
theta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
print("w, b:", theta)
```

이 코드는 10줄 이내로 선형 회귀의 핵심을 보여 줍니다. `sklearn`은 이 과정을 최적화하고 다양한 옵션을 제공합니다.

## 선형회귀 가정 검증

| 가정 | 의미 | 검증법 |
|---|---|---|
| 선형성 | X와 y가 선형 관계 | 잔차 vs 예측 플롯 |
| 독립성 | 피처 간 다중공선성 없음 | VIF(분산팽창지수) |
| 등분산성 | 잔차 분산 일정 | 잔차 절대값 플롯 |
| 정규성 | 잔차가 정규분포 | Q-Q 플롯 |

선형 회귀는 이 가정들이 만족될 때 가장 잘 동작합니다. 가정이 깨지면 계수의 해석이 흔들리거나 예측 성능이 떨어집니다.

선형 회귀는 해석이 쉽고 빠르며, 생각보다 강력합니다. 그래서 가장 먼저 돌려 보는 편이 좋습니다. 베이스라인이 없으면 더 복잡한 모델을 쓸 정당성도 약해집니다.

- **가중치 `w`**: 각 피처가 예측에 기여하는 정도입니다.
- **절편 `b`**: 기준 수준의 예측값입니다.
- **MSE**: 평균제곱오차입니다.
- **R-squared**: 모델이 설명한 분산의 비율입니다.
- **잔차(Residual)**: `y - y_hat`입니다.

## 적용 전과 후
**Before**: "그래프상 직선처럼 보인다"는 인상만 있고 수치 검증은 없습니다.

**After**: 모델, 지표, 잔차를 함께 보며 세 단계로 검증합니다.

## 실습: 5단계로 보는 회귀

### 단계 1 — 데이터

```python
from sklearn.datasets import fetch_california_housing
X, y = fetch_california_housing(return_X_y=True)
```

### 단계 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
```

### 단계 3 — 학습

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
from sklearn.metrics import mean_squared_error, r2_score
pred = model.predict(Xte)
print("MSE:", mean_squared_error(yte, pred))
print("R^2:", r2_score(yte, pred))
```

### 단계 5 — 계수 확인

```python
for name, coef in zip(range(Xtr.shape[1]), model.coef_):
    print(f"x{name}: {coef:.3f}")
```

**예상 출력:** MSE, `R^2`, 그리고 부호가 있는 계수 목록이 출력됩니다. 여기서 먼저 볼 것은 절대적인 점수보다 **계수 방향이 상식과 맞는지**, 그리고 잔차가 직선 모델로 설명되지 않는 패턴을 보이는지입니다.

- `coef_`의 부호와 크기가 해석의 중심입니다.
- R-squared가 낮다면 비선형성이 숨어 있다는 신호일 수 있습니다.
- MSE는 오차를 제곱하기 때문에 이상치에 특히 민감합니다.

## 회귀 모델 비교: 언제 어떤 모델을 써야 할까요?

선형 회귀 외에도 여러 회귀 모델이 있습니다. 상황에 맞게 선택하는 기준을 정리합니다.

| 모델 | 특징 | 언제 써야 할까 |
|---|---|---|
| LinearRegression | 계수 그대로, 정규화 없음 | 빠른 베이스라인, 피처 수가 적을 때 |
| Ridge (L2) | 계수를 전체적으로 줄임 | 다중공선성이 있을 때 |
| Lasso (L1) | 일부 계수를 0으로 만듦 | 피처 선택이 필요할 때 |
| ElasticNet | L1+L2 혼합 | 상관 피처가 많고 일부 제거도 원할 때 |
| PolynomialFeatures + Linear | 비선형 항 추가 | 관계가 곡선 형태일 때 |

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso

X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

models = {
    "Linear": LinearRegression(),
    "Ridge(1.0)": Ridge(alpha=1.0),
    "Lasso(0.01)": Lasso(alpha=0.01),
}

print(f"{'모델':>12} {'Train R²':>10} {'Test R²':>9}")
for name, m in models.items():
    m.fit(Xtr_s, ytr)
    print(f"{name:>12} {m.score(Xtr_s, ytr):>10.4f} {m.score(Xte_s, yte):>9.4f}")
```

같은 데이터에서 모델별로 점수를 비교해 보면 정규화가 일반화 성능을 어떻게 바꾸는지 보입니다.

## 잔차 해석으로 모델 진단하기

잔차(residual)는 실제값과 예측값의 차이입니다. 잔차 플롯에서 패턴이 보이면 모델이 뭔가를 놓치고 있다는 신호입니다.

```python
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression().fit(Xtr, ytr)
pred = model.predict(Xte)

residuals = yte - pred
print(f"잔차 평균: {residuals.mean():.4f}")   # 0에 가까워야 합니다
print(f"잔차 표준편차: {residuals.std():.4f}")
print(f"MAE : {mean_absolute_error(yte, pred):.4f}")
print(f"RMSE: {mean_squared_error(yte, pred)**0.5:.4f}")
print(f"R²  : {r2_score(yte, pred):.4f}")

# 큰 잔차를 가진 샘플 확인
large_err_idx = np.argsort(np.abs(residuals))[-5:]
print("\n잔차가 큰 샘플 인덱스:", large_err_idx)
print("실제값:", yte[large_err_idx])
print("예측값:", pred[large_err_idx].round(2))
```

잔차 평균이 0에서 크게 벗어나거나, 잔차에 뚜렷한 패턴이 있다면 비선형 항이나 교호작용 항을 추가해야 할 수 있습니다.

## 실패 신호를 먼저 이렇게 읽습니다

- `R^2`가 낮고 잔차에 곡선 패턴이 보이면, 선형 모델을 버리기 전에 **비선형 피처**가 빠졌는지 봐야 합니다.
- 계수가 실행마다 크게 흔들리면 **다중공선성**과 **스케일 차이**를 먼저 점검해야 합니다.
- 일부 샘플이 오차를 지배하면, 이상치를 치울지 남길지 자체가 모델링 결정이라는 점을 드러내야 합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 스케일 차이 무시 후 계수 비교 | 계수 크기가 피처 단위에 의존 | StandardScaler 후 비교 |
| 다중공선성 무시 | 계수 부호가 기대와 반대 | VIF 체크, Ridge 사용 |
| 잔차 플롯 생략 | 비선형 패턴 발견 못함 | 예측값 vs 잔차 플롯 필수 |
| 이상치 방치 | MSE가 이상치에 끌림 | 이상치 진단 후 처리 결정 |
| 훈련 범위 밖 외삽 | 신뢰할 수 없는 예측 | 외삽 범위 경고 표시 |

## 실무에서는 이렇게 나타납니다

가격 책정, 수요 모델링, A/B 효과 추정처럼 이해관계자가 블랙박스보다 **해석 가능한 레버**를 원하는 영역에서는 선형 회귀가 여전히 중심에 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 항상 **베이스라인**에서 출발합니다.
- 해석 가능성은 기술 옵션이 아니라 **비즈니스 도구**입니다.
- 잔차는 모델의 일기장과 같습니다.
- 계수를 비교하기 전에는 표준화를 합니다.
- 규제가 필요하면 Ridge나 Lasso를 더합니다.

## 운영 체크리스트

- [ ] MSE와 R-squared를 함께 보고합니다.
- [ ] 잔차를 시각화합니다.
- [ ] 계수를 읽기 전에 피처를 스케일링합니다.
- [ ] 외삽 위험을 명시적으로 표시합니다.

## RidgeCV로 최적 alpha 자동 탐색

수동으로 alpha를 탐색하는 대신 `RidgeCV`가 교차검증으로 자동 선택합니다.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np

X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# 수동 alpha 탐색
alphas = np.logspace(-3, 3, 13)
print(f"{'alpha':>10} {'train R²':>10} {'test R²':>9}")
for a in alphas:
    m = Ridge(alpha=a).fit(Xtr_s, ytr)
    print(f"{a:>10.4f} {m.score(Xtr_s, ytr):>10.4f} {m.score(Xte_s, yte):>9.4f}")

# RidgeCV로 자동 선택
rcv = RidgeCV(alphas=alphas, cv=5).fit(Xtr_s, ytr)
print(f"\nRidgeCV 선택 alpha: {rcv.alpha_:.4f}")
print(f"RidgeCV 테스트 R²: {rcv.score(Xte_s, yte):.4f}")
pred = rcv.predict(Xte_s)
print(f"MAE: {mean_absolute_error(yte, pred):.4f}")
```

`RidgeCV`는 교차검증으로 alpha를 고르므로 수동 탐색보다 안정적입니다. 단, 테스트 세트에 닿지 않은 채 최적화되어야 합니다.

## 다중 회귀에서 계수 해석의 한계

계수를 그대로 비교하면 잘못된 결론에 도달할 수 있습니다.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

data = fetch_california_housing()
X, y = data.data, data.target
feature_names = data.feature_names

sc = StandardScaler().fit(X)
X_s = sc.transform(X)
m = LinearRegression().fit(X_s, y)

print("표준화 후 계수 (크기 = 상대적 기여도):")
for name, coef in sorted(zip(feature_names, m.coef_), key=lambda x: abs(x[1]), reverse=True):
    print(f"  {name:20s}: {coef:+.4f}")

print("\n주의: 계수가 크다고 인과관계가 있는 것은 아닙니다.")
print("특히 상관된 피처들 사이에서는 계수 해석이 불안정합니다.")
```

계수를 비교하기 전에 표준화를 해야 단위가 다른 피처 간의 상대적 기여도를 볼 수 있습니다. 하지만 다중공선성이 있으면 개별 계수 해석 자체가 불안정합니다.

## 회귀 모델 성능 진단을 위한 체계적 접근

단순히 R² 하나만 보지 않고 여러 각도에서 모델을 진단합니다.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

X, y = fetch_california_housing(return_X_y=True)
feature_names = fetch_california_housing().feature_names
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

model = Ridge(alpha=1.0).fit(Xtr_s, ytr)
pred = model.predict(Xte_s)
residuals = yte - pred

print("=== 모델 진단 보고서 ===")
print(f"Train R²: {model.score(Xtr_s, ytr):.4f}")
print(f"Test  R²: {r2_score(yte, pred):.4f}")
print(f"MAE     : {mean_absolute_error(yte, pred):.4f}")
print(f"RMSE    : {mean_squared_error(yte, pred)**0.5:.4f}")
print(f"잔차 평균: {residuals.mean():.4f}  (0에 가까울수록 좋음)")
print(f"잔차 표준편차: {residuals.std():.4f}")

# 잔차 분포 확인
percentiles = [10, 25, 50, 75, 90]
print("\n잔차 백분위수:")
for p in percentiles:
    print(f"  {p:3d}%: {np.percentile(residuals, p):+.4f}")

# 큰 오차 샘플 비율
large_err = (np.abs(residuals) > 1.0).mean()
print(f"\n절대 잔차 > 1.0인 샘플 비율: {large_err:.2%}")
```

잔차의 평균이 0에 가깝고, 분포가 대칭적이며, 패턴이 없으면 모델이 데이터의 선형 관계를 잘 포착한 것입니다.

## 연습 문제

1. `PolynomialFeatures(degree=2)`를 추가하고 R-squared 변화를 관찰해 보세요.
2. 예측값 대비 잔차를 그린 뒤 어떤 패턴이 보이는지 설명해 보세요.
3. `Ridge(alpha=1.0)`와 `LinearRegression`의 계수 크기를 비교해 보세요.
4. Lasso로 0이 되는 계수(피처)가 무엇인지 확인하고 의미를 해석해 보세요.
5. 훈련 점수와 테스트 점수를 함께 출력하고 과적합 여부를 판단해 보세요.

## 정리

선형 회귀는 모든 데이터까지의 제곱 거리가 가장 작은 단 하나의 직선을 그리는 일이고, 계수·R²·잔차는 모두 그 직선을 다른 각도에서 읽는 도구입니다. 이 글에서는 비용함수와 경사하강법부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **선형 회귀 식은 어떤 방식으로 예측값을 만들까요?**
  - `y_hat = Xw + b`로 피처에 가중치를 곱하고 더해서 예측합니다. 가중치는 MSE를 최소화하는 방향으로 학습됩니다.
- **평균제곱오차와 최소제곱 해는 무엇을 최소화할까요?**
  - 실제값과 예측값 차이의 제곱 합을 최소화합니다. 폐형해(정규방정식)로 한 번에 구하거나 경사하강법으로 반복해서 구합니다.
- **R-squared는 정확히 무엇을 설명할까요?**
  - 전체 분산 중 모델이 설명한 비율입니다. 1에 가까울수록 좋고, 0이면 평균을 예측하는 수준과 같습니다. 음수라면 모델이 평균보다 나쁩니다.
