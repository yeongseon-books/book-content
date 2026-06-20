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

## 정규화 방법 비교

| 방법 | 페널티 항 | 계수 특성 | 피처 선택 | 언제 쓸까 |
|---|---|---|---|---|
| LinearRegression | 없음 | 제한 없음 | 없음 | 피처 수가 적고 다중공선성 없을 때 |
| Ridge (L2) | sum(w²) | 전체적으로 줄어듦 | 없음 | 다중공선성 있을 때 |
| Lasso (L1) | sum(\|w\|) | 일부가 정확히 0 | 자동 | 피처 선택이 필요할 때 |
| ElasticNet | L1+L2 혼합 | 일부 0, 나머지 줄어듦 | 부분적 | 상관 피처가 많을 때 |

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
import numpy as np

X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

models = {
    "LinearRegression": LinearRegression(),
    "Ridge(alpha=1)": Ridge(alpha=1.0),
    "Lasso(alpha=0.01)": Lasso(alpha=0.01),
    "ElasticNet(l1=0.5)": ElasticNet(alpha=0.01, l1_ratio=0.5),
}

print(f"{'모델':>22} {'Train R²':>10} {'Test R²':>9} {'Non-zero 계수':>14}")
for name, m in models.items():
    m.fit(Xtr_s, ytr)
    coef = getattr(m, "coef_", np.array([]))
    nz = (coef != 0).sum() if len(coef) > 0 else "-"
    print(f"{name:>22} {m.score(Xtr_s, ytr):>10.4f} {m.score(Xte_s, yte):>9.4f} {str(nz):>14}")
```

## 학습 곡선으로 진단하기

학습 곡선은 훈련 데이터 크기를 늘려 가면서 훈련 점수와 검증 점수를 추적합니다.

```python
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge

X, y = fetch_california_housing(return_X_y=True)
pipeline = make_pipeline(StandardScaler(), Ridge(alpha=1.0))

train_sizes, train_scores, val_scores = learning_curve(
    pipeline, X, y,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5, scoring="r2", n_jobs=-1
)

print(f"{'Train size':>12} {'Train R²':>10} {'Val R²':>9}")
for ts, tr, vl in zip(train_sizes,
                       train_scores.mean(axis=1),
                       val_scores.mean(axis=1)):
    print(f"{ts:>12} {tr:>10.4f} {vl:>9.4f}")
```

- 훈련 점수와 검증 점수가 모두 낮으면: **과소적합** → 모델 용량을 늘립니다.
- 훈련 점수만 높고 검증이 낮으면: **과적합** → 정규화를 강화하거나 데이터를 늘립니다.
- 두 점수 모두 높고 수렴하면: **적절한 적합** → 배포 가능한 상태입니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 모델 용량이 커질수록 train-test 간격이 벌어지면, 구조 변경 전에 **정규화**와 **데이터 양**을 먼저 점검해야 합니다.
- Lasso가 실행할 때마다 다른 피처를 고르면, 상관 피처가 많은지 보고 ElasticNet이나 Ridge도 함께 비교해야 합니다.
- train과 test가 둘 다 낮으면 과적합이 아니라 **과소적합**이나 **피처 설계 부족**일 수 있습니다.

## 자주 하는 실수

| 실수 | 결과 | 올바른 방법 |
|---|---|---|
| 스케일링 없이 L1/L2 적용 | 페널티가 피처 단위에 의존 | StandardScaler 후 적용 |
| alpha를 한 번만 시도 | 최적 alpha 놓침 | logspace로 범위 탐색 |
| 훈련 점수만 보고 과적합 판단 | 오진 가능 | 학습 곡선 + 테스트 점수 |
| 상관 피처에서 Lasso 불안정 무시 | 피처 선택 불안정 | ElasticNet 또는 Ridge 병행 |
| ElasticNet 존재를 잊음 | L1/L2 중 하나만 선택 | 세 가지 모두 비교 |

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

## 다항 피처로 과적합 직접 재현하기

과적합이 어떻게 발생하는지 단계별로 재현하는 실험입니다.

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# 간단한 비선형 데이터 생성
np.random.seed(42)
n = 100
X = np.sort(np.random.uniform(-3, 3, n)).reshape(-1, 1)
y = np.sin(X.ravel()) + np.random.randn(n) * 0.3

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)

print(f"{'degree':>7} {'train R²':>10} {'test R²':>9} {'판단':>8}")
for deg in [1, 2, 3, 5, 8, 12]:
    m = make_pipeline(PolynomialFeatures(deg), LinearRegression()).fit(Xtr, ytr)
    tr = r2_score(ytr, m.predict(Xtr))
    te = r2_score(yte, m.predict(Xte))
    verdict = "좋음" if abs(tr - te) < 0.05 else ("과적합" if tr > te + 0.05 else "과소적합")
    print(f"{deg:>7} {tr:>10.4f} {te:>9.4f} {verdict:>8}")

# Ridge 정규화로 고차 다항식 제어
print("\nRidge로 degree=12 제어:")
for alpha in [0.0001, 0.001, 0.01, 0.1, 1.0]:
    m = make_pipeline(PolynomialFeatures(12), Ridge(alpha=alpha)).fit(Xtr, ytr)
    tr = r2_score(ytr, m.predict(Xtr))
    te = r2_score(yte, m.predict(Xte))
    print(f"  alpha={alpha:.4f}: train={tr:.4f}, test={te:.4f}")
```

차수가 낮으면 과소적합, 너무 높으면 과적합이 됩니다. Ridge 정규화는 고차 다항식의 계수를 줄여서 과적합을 막습니다.

## 편향-분산 트레이드오프의 실험적 시각화

모델 복잡도와 편향-분산의 관계를 데이터로 확인합니다.

```python
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=300, n_features=5, noise=20, random_state=42)

print(f"{'max_depth':>10} {'bias(train err)':>17} {'variance(cv std)':>17} {'판단':>10}")
for depth in [1, 2, 3, 4, 5, 7, 10, None]:
    m = DecisionTreeRegressor(max_depth=depth, random_state=42)
    cv = cross_val_score(m, X, y, cv=5, scoring="neg_mean_squared_error")
    m.fit(X, y)
    train_mse = -cross_val_score(m, X, y, cv=5, scoring="neg_mean_squared_error").mean()
    cv_mean = -cv.mean()
    cv_std = cv.std()
    label = str(depth) if depth else "None"
    verdict = "고편향" if train_mse > 500 else ("고분산" if cv_std > 100 else "균형")
    print(f"{label:>10} {cv_mean:>17.1f} {cv_std:>17.1f} {verdict:>10}")
```

얕은 트리는 편향(오차)이 크고 분산(불안정)이 작습니다. 깊은 트리는 편향이 작지만 분산이 커집니다. 정규화는 이 사이의 균형점을 찾는 작업입니다.

## GridSearchCV로 정규화 강도 자동 최적화

교차검증으로 최적 alpha를 찾는 체계적인 방법입니다.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.pipeline import make_pipeline
import numpy as np

X, y = fetch_california_housing(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

# Ridge GridSearch
ridge_pipe = make_pipeline(StandardScaler(), Ridge())
param_grid = {"ridge__alpha": np.logspace(-3, 3, 13)}
gs = GridSearchCV(ridge_pipe, param_grid, cv=5, scoring="r2", n_jobs=-1)
gs.fit(Xtr, ytr)

print(f"Ridge 최적 alpha: {gs.best_params_['ridge__alpha']:.4g}")
print(f"CV R² (최적):    {gs.best_score_:.4f}")
print(f"Test R² (최적):  {gs.score(Xte, yte):.4f}")

# 상위 3개 alpha 비교
results = gs.cv_results_
top3 = np.argsort(results["mean_test_score"])[::-1][:3]
print("\n상위 3개 alpha:")
for i in top3:
    alpha = results["params"][i]["ridge__alpha"]
    score = results["mean_test_score"][i]
    print(f"  alpha={alpha:.4g}: CV R²={score:.4f}")
```

`GridSearchCV`는 지정한 파라미터 조합을 교차검증으로 평가합니다. `make_pipeline`으로 스케일러를 포함해야 각 fold에서 누수 없이 학습됩니다.

## ElasticNet: L1과 L2의 균형점 찾기

상관 피처가 많을 때 Lasso의 불안정성을 ElasticNet으로 해결합니다.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso, ElasticNet, ElasticNetCV
from sklearn.pipeline import make_pipeline

# 상관 피처가 많은 데이터 생성
X, y, true_coef = make_regression(
    n_samples=500, n_features=20, n_informative=10,
    noise=15, random_state=42, coef=True
)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# l1_ratio 비교
print(f"{'l1_ratio':>10} {'의미':>15} {'Test R²':>9} {'0인 계수':>9}")
for l1_ratio in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
    if l1_ratio == 0.0:
        label = "Ridge (L2만)"
    elif l1_ratio == 1.0:
        label = "Lasso (L1만)"
    else:
        label = f"ElasticNet"
    m = ElasticNet(alpha=0.1, l1_ratio=l1_ratio, max_iter=5000).fit(Xtr_s, ytr)
    r2 = m.score(Xte_s, yte)
    nz = (m.coef_ == 0).sum()
    print(f"{l1_ratio:>10.1f} {label:>15} {r2:>9.4f} {nz:>9}")

# ElasticNetCV로 자동 선택
encv = ElasticNetCV(cv=5, max_iter=5000).fit(Xtr_s, ytr)
print(f"\nElasticNetCV 최적: alpha={encv.alpha_:.4g}, l1_ratio={encv.l1_ratio_:.2f}")
print(f"Test R²: {encv.score(Xte_s, yte):.4f}")
```

`l1_ratio=0`이면 Ridge(L2만), `l1_ratio=1`이면 Lasso(L1만), 중간값이면 ElasticNet입니다. 상관 피처가 많을 때는 중간 값이 더 안정적입니다.

## 드롭아웃 대신 교차검증: 모델 복잡도 선택 전략

신경망의 드롭아웃과 달리 sklearn 모델은 교차검증으로 최적 복잡도를 탐색합니다. 정규화 강도와 모델 구조를 동시에 비교하는 패턴입니다.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_regression(n_samples=300, n_features=20, noise=15, random_state=42)

candidates = {
    "Ridge(alpha=0.1)": Pipeline([("sc", StandardScaler()),
                                   ("m", Ridge(alpha=0.1))]),
    "Ridge(alpha=10)":  Pipeline([("sc", StandardScaler()),
                                   ("m", Ridge(alpha=10))]),
    "Lasso(alpha=0.1)": Pipeline([("sc", StandardScaler()),
                                   ("m", Lasso(alpha=0.1))]),
    "DecisionTree(d=3)": DecisionTreeRegressor(max_depth=3, random_state=0),
    "DecisionTree(d=8)": DecisionTreeRegressor(max_depth=8, random_state=0),
}

print(f"{'모델':<22} {'CV R² mean':>10} {'CV R² std':>10}")
print("-" * 44)
for name, model in candidates.items():
    scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    print(f"{name:<22} {scores.mean():>10.4f} {scores.std():>10.4f}")
```

std가 작고 mean이 높은 모델이 실전 데이터에서도 안정적입니다. 같은 mean이라면 std가 낮은 쪽을 선택하세요.

## 연습 문제

1. `PolynomialFeatures(degree=10)`와 Ridge를 써서 과적합을 재현해 보세요.
2. `RidgeCV`와 수동으로 고른 `alpha`를 비교해 보세요.
3. Lasso가 0으로 줄인 피처 목록을 적어 보세요.
4. `learning_curve`를 그려서 현재 모델이 과적합인지 과소적합인지 진단해 보세요.
5. ElasticNet의 `l1_ratio`를 0.1, 0.5, 0.9로 바꿔 가며 선택되는 피처 수를 비교해 보세요.

## 정리

과적합은 모델이 노이즈를 외워 버리는 현상이고, 정규화는 그 모델을 일반화되는 패턴 쪽으로 다시 끌어당기는 페널티입니다. 이 글에서는 적용 전과 후부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **과적합과 과소적합은 어떤 신호로 구분할까요?**
  - 훈련 점수가 높고 테스트 점수가 낮으면 과적합, 둘 다 낮으면 과소적합입니다. 학습 곡선을 그리면 두 상황을 명확히 구분할 수 있습니다.
- **편향-분산 트레이드오프는 무엇을 뜻할까요?**
  - 단순한 모델은 편향이 높고 분산이 낮으며, 복잡한 모델은 편향이 낮고 분산이 높습니다. 정규화는 복잡한 모델의 분산을 줄여 균형을 찾게 해 줍니다.
- **Ridge, Lasso, ElasticNet은 어떻게 다를까요?**
  - Ridge는 모든 계수를 줄이고, Lasso는 일부를 0으로 만들어 피처 선택까지 합니다. ElasticNet은 두 방법을 혼합해 상관 피처가 많은 상황에서 더 안정적입니다.
