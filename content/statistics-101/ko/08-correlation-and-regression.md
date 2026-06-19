---
series: statistics-101
episode: 8
title: "Statistics 101 (8/10): 상관과 회귀"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Statistics
  - Correlation
  - Regression
  - Modeling
  - Beginner
seo_description: 상관계수의 한계와 단순 선형 회귀로 변수 관계를 모델링하는 방법을 비교하고 인과와의 차이를 정리한 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (8/10): 상관과 회귀

두 변수가 함께 움직이면 사람은 곧바로 이유를 찾고 싶어 합니다. 광고비가 늘면 매출이 오르는지, 공부 시간이 길면 점수가 오르는지, 가격이 내려가면 수요가 늘어나는지 같은 질문은 분석의 출발점이 됩니다.

하지만 함께 움직인다는 사실만으로 원인과 결과가 증명되지는 않습니다. 상관은 관계의 방향과 강도를 보여 주고, 회귀는 그 관계를 식으로 표현해 예측 가능한 형태로 만듭니다. 둘은 연결되어 있지만 같은 질문에 답하지는 않습니다.

이 글은 Statistics 101 시리즈의 8번째 글입니다. 여기서는 상관계수와 단순 선형 회귀를 나란히 놓고, R²와 잔차가 왜 중요한지, 그리고 왜 상관과 인과를 절대 섞어 읽으면 안 되는지 정리하겠습니다.

![Statistics 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/08/08-01-concept-at-a-glance.ko.png)
*Statistics 101 8장 흐름 개요*
> 두 변수가 함께 움직인다는 것이 한 변수가 다른 변수를 일으킨다는 뜻은 아닙니다.

## 이 글에서 다룰 문제

- 상관계수는 무엇을 말하고 무엇은 말하지 못할까요?
- 회귀식은 상관계수보다 어떤 정보를 더 줄까요?
- R²는 어떤 범위에서 어떻게 읽어야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

비즈니스 데이터의 많은 질문은 관계를 묻는 형태로 시작합니다. 광고비와 매출, 사용량과 이탈, 공부 시간과 점수처럼 변수 간 연결을 숫자로 요약해야 할 때가 많습니다. 이때 상관과 회귀는 가장 먼저 손에 잡히는 기본 도구입니다.

문제는 이 도구들이 너무 익숙해서 오용되기 쉽다는 사실입니다. 상관이 높다고 곧바로 원인이라고 읽거나, R²가 높다고 좋은 모델이라고 단정하거나, 잔차를 보지 않고 선형성을 가정하는 일이 자주 생깁니다.

## 멘탈 모델: 상관 → 회귀 → 잔차 진단

상관은 두 변수가 같은 방향으로 움직이는지와 그 강도를 보여 줍니다. 회귀는 그 관계를 식으로 적어, x가 바뀔 때 y가 어떻게 달라지는지 예측 가능한 형태로 만듭니다. 마지막으로 R²와 잔차는 그 식이 데이터를 얼마나 설명하는지 점검하게 합니다.

### 상관 대비 인과

| 구분 | 상관(Correlation) | 인과(Causation) |
|------|------------------|----------------|
| 정의 | 두 변수가 함께 움직이는 정도 | 한 변수가 다른 변수를 일으키는 관계 |
| 예시 | 아이스크림 판매량과 익사 사고 (여름에 둘 다 증가) | 백신 접종이 감염률을 낮춤 |
| 판단 기준 | 상관계수, 산점도 | 무작위 실험(RCT), 시간 선후관계 |
| 주요 함정 | 제3 변수, 역인과, 우연 | 관찰 데이터만으로 인과 불가 |

상관이 있다고 해서 인과가 보장되지 않는 이유는 세 가지입니다.

1. **제3의 변수**: 아이스크림과 익사는 둘 다 '여름'이라는 숨은 변수의 영향을 받습니다.
2. **역인과**: 매출이 광고비를 늘리는 방향일 수도 있습니다.
3. **우연**: 데이터가 작으면 무의미한 패턴도 상관으로 보일 수 있습니다.

## 상관계수 계산과 시각화

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
n = 200

# 강한 양의 상관
x1 = rng.normal(0, 1, n)
y1 = 2 * x1 + rng.normal(0, 0.5, n)

# 약한 양의 상관
x2 = rng.normal(0, 1, n)
y2 = x2 + rng.normal(0, 2, n)

# 무상관
x3 = rng.normal(0, 1, n)
y3 = rng.normal(0, 1, n)

# 비선형 상관 (Pearson 낮지만 관계 존재)
x4 = rng.uniform(-3, 3, n)
y4 = x4**2 + rng.normal(0, 0.5, n)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
datasets = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
titles = ["강한 양의 상관", "약한 양의 상관", "무상관", "비선형 관계"]

for ax, (x, y), title in zip(axes.flat, datasets, titles):
    r, p = stats.pearsonr(x, y)
    rho, _ = stats.spearmanr(x, y)
    ax.scatter(x, y, alpha=0.4, s=20, color="steelblue")
    ax.set_title(f"{title}\nPearson r={r:.2f}, Spearman ρ={rho:.2f}")

plt.tight_layout()
plt.show()
```

비선형 관계에서는 Pearson r이 낮게 나오지만 관계가 분명히 존재합니다. 상관계수를 보기 전에 항상 산점도를 먼저 그려야 하는 이유입니다.

## 단순 선형 회귀 분석

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

rng = np.random.default_rng(42)
n = 100
ads = rng.normal(50, 15, n)
sales = 800 + 4.5 * ads + rng.normal(0, 60, n)

# statsmodels로 회귀 분석
X = sm.add_constant(ads)
model = sm.OLS(sales, X).fit()
print(model.summary())
```

**예상 출력 (요약):**

```text
                 coef    std err          t      P>|t|      [0.025      0.975]
const         802.xxx    12.xxx     66.xxx      0.000      778.xxx     826.xxx
x1              4.xxx     0.xxx      8.xxx      0.000        3.xxx       5.xxx

R-squared:                       0.xxx
Adj. R-squared:                  0.xxx
```

이 출력에서 확인할 점.

- **coef**: 광고비가 1단위 늘 때 매출이 약 4.5단위 증가합니다.
- **P>|t|**: 계수가 0이 아니라는 가설의 p-value입니다.
- **[0.025, 0.975]**: 계수의 95% 신뢰구간입니다.
- **R-squared**: 모델이 데이터 분산의 몇 %를 설명하는지입니다.

## 잔차 진단

회귀 모델의 품질은 R²만으로 판단할 수 없습니다. 잔차 분석이 필수입니다.

```python
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

rng = np.random.default_rng(42)
n = 150
ads = rng.normal(50, 15, n)
sales = 800 + 4.5 * ads + rng.normal(0, 60, n)

X = sm.add_constant(ads)
model = sm.OLS(sales, X).fit()

fitted = model.fittedvalues
residuals = model.resid

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 잔차 vs 적합값
axes[0, 0].scatter(fitted, residuals, alpha=0.5, color="steelblue")
axes[0, 0].axhline(0, color="red", linestyle="--")
axes[0, 0].set_xlabel("적합값")
axes[0, 0].set_ylabel("잔차")
axes[0, 0].set_title("잔차 vs 적합값 (등분산성 확인)")

# 잔차 히스토그램
axes[0, 1].hist(residuals, bins=30, edgecolor="black", alpha=0.7, color="green")
axes[0, 1].set_xlabel("잔차")
axes[0, 1].set_title("잔차 분포 (정규성 확인)")

# Q-Q 플롯
stats.probplot(residuals, dist="norm", plot=axes[1, 0])
axes[1, 0].set_title("잔차 Q-Q 플롯")

# 산점도 + 회귀선
axes[1, 1].scatter(ads, sales, alpha=0.5, color="steelblue", s=20)
x_line = np.linspace(ads.min(), ads.max(), 100)
axes[1, 1].plot(x_line, model.params[0] + model.params[1] * x_line,
                "r-", lw=2, label="회귀선")
axes[1, 1].set_xlabel("광고비")
axes[1, 1].set_ylabel("매출")
axes[1, 1].set_title("데이터와 회귀선")
axes[1, 1].legend()

plt.tight_layout()
plt.show()

# 잔차 정규성 검정
_, p_normality = stats.normaltest(residuals)
print(f"\n잔차 정규성 검정 p-value: {p_normality:.4f}")
if p_normality > 0.05:
    print("→ 잔차가 정규분포에 가깝습니다.")
else:
    print("→ 잔차가 정규분포에서 벗어납니다. 모델 재검토가 필요합니다.")
```

### 잔차 진단 체크리스트

1. **잔차 vs 적합값**: 패턴이 없어야 함 (등분산성)
2. **잔차 분포**: 정규분포에 가까워야 함
3. **Q-Q 플롯**: 직선에 가까워야 함
4. **이상치 확인**: Cook's distance가 큰 관측치 점검

## 다중공선성 진단

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

rng = np.random.default_rng(1)
n = 100
x1 = rng.normal(50, 10, n)
x2 = x1 + rng.normal(0, 2, n)  # x1과 강한 상관
y = 3 * x1 + 2 * x2 + rng.normal(0, 5, n)

df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
X = sm.add_constant(df[["x1", "x2"]])

vif = pd.DataFrame()
vif["Variable"] = X.columns
vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print("VIF 분석:")
print(vif)
print("\nVIF > 10이면 다중공선성 주의")
```

VIF(Variance Inflation Factor)가 10 이상이면 다중공선성이 심각합니다. 해결 방법은 변수 제거, 결합, PCA, 또는 Ridge/Lasso 정규화입니다.

## 핵심 용어 정리

- **Pearson 상관계수 r**: 선형 관계의 방향과 강도를 -1에서 +1 사이 값으로 나타냅니다.
- **Spearman ρ**: 순위 기반 상관으로, 비선형 구조나 이상치에 조금 더 강합니다.
- **단순 선형 회귀**: `y = β0 + β1·x + ε` 형태의 모델입니다.
- **R²**: 모델이 데이터 분산을 얼마나 설명하는지 나타내는 비율입니다.
- **잔차**: 실제값에서 예측값을 뺀 값으로, 모델 진단의 핵심 재료입니다.

## 함께 움직인다고 바로 원인이라고 말할 수는 없다

이전 해석: "광고비와 매출의 상관이 0.6이므로 광고비가 매출을 만든다."

이 문장은 관계와 인과를 섞은 해석입니다. 제3의 변수나 시간 효과가 함께 작용했을 수도 있습니다.

이후 해석: "광고비와 매출 사이에는 양의 선형 관계가 보이며, 단순 회귀식은 `sales = 800 + 4.5·ads`입니다. 다만 이 식은 관계를 설명할 뿐 인과를 보증하지는 않습니다."

상관과 회귀는 관계를 표현하는 도구이지, 자동으로 원인을 증명하는 장치는 아닙니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 상관을 인과로 읽음 | "상관계수 0.8 → 광고가 매출 원인" | "양의 선형 관계가 있다"까지만 말함 |
| 이상치가 상관을 부풀림 | 극단값 하나로 r이 크게 변함 | 산점도로 이상치 확인 후 Spearman 고려 |
| 비선형에 Pearson만 적용 | 이차 관계에서 r≈0으로 관계 없다고 판단 | Spearman 또는 비선형 모델 검토 |
| R²만으로 모델 확정 | R²=0.9 → 좋은 모델 단정 | 잔차 진단 필수 |
| 잔차 진단 생략 | 적합 후 결과만 보고 | 잔차 vs 적합값 플롯 항상 확인 |
| 다중공선성 미확인 | 다중 회귀에서 VIF 확인 안함 | VIF 계산 후 > 10인 변수 검토 |

## 실습: 5단계 회귀 읽기

### 1단계 — 데이터를 준비한다

```python
import numpy as np
rng = np.random.default_rng(42)
ads = rng.normal(50, 15, 100)
sales = 800 + 4.5 * ads + rng.normal(0, 60, 100)
```

### 2단계 — 상관계수를 계산한다

```python
from scipy import stats
r, p = stats.pearsonr(ads, sales)
print(f"r: {r:.3f}, p: {p:.4f}")
```

방향과 강도를 먼저 봅니다.

### 3단계 — 회귀모형을 적합한다

```python
from sklearn.linear_model import LinearRegression
X = ads.reshape(-1, 1)
model = LinearRegression().fit(X, sales)
print(f"β1: {model.coef_[0]:.2f}, β0: {model.intercept_:.2f}")
```

기울기와 절편은 관계를 식으로 바꾼 결과입니다.

### 4단계 — 설명력을 본다

```python
print(f"R²: {model.score(X, sales):.3f}")
```

R²는 0과 1 사이에서 읽습니다.

### 5단계 — 잔차를 점검한다

```python
import matplotlib.pyplot as plt
resid = sales - model.predict(X)
plt.scatter(model.predict(X), resid, alpha=0.5)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("적합값")
plt.ylabel("잔차")
plt.title("잔차 플롯")
plt.show()
```

잔차 패턴은 선형성 위반이나 누락 변수를 암시할 수 있습니다.

## 실무에서는 이렇게 읽습니다

매출 예측, 가격과 수요 관계, 광고와 전환, 사용량과 이탈률 분석처럼 관계를 다루는 작업은 매우 많습니다. 단순 선형 회귀는 출발점으로 유용하지만, 실제 문제는 다변량 회귀, 로지스틱 회귀, 시계열 회귀로 확장되는 경우가 많습니다. 그 출발점에서 가장 먼저 익혀야 할 태도는 시각화와 잔차 진단입니다.

시니어 엔지니어는 상관이 높아도 바로 인과를 말하지 않고, 산점도를 먼저 보고, 잔차를 점검하고, 설명과 예측을 구분합니다. 숫자를 멋지게 뽑는 것보다 어떤 질문에 이 모델이 답할 수 있고 무엇은 답하지 못하는지 말하는 능력이 더 중요합니다.

## 운영 체크리스트

- [ ] 상관과 인과를 구분할 수 있습니다.
- [ ] Pearson과 Spearman의 차이를 설명할 수 있습니다.
- [ ] R²의 의미와 한계를 압니다.
- [ ] 잔차를 확인해야 하는 이유를 설명할 수 있습니다.

## 연습 문제

1. 공부 시간과 점수 데이터를 만들어 r과 R²를 각각 계산해 보세요.
2. 상관이 높지만 인과가 아닌 사례 하나를 적어 보세요.
3. 비선형 관계에서 Pearson 상관이 약할 수 있는 이유를 설명해 보세요.

## 정리와 다음 글

상관과 회귀는 변수 관계를 숫자와 식으로 표현하는 가장 기본적인 도구입니다. 상관은 함께 움직임의 강도를, 회귀는 그 관계를 예측 가능한 형태로 보여 줍니다. 다만 둘 다 인과를 자동으로 보장하지 않으며, 잔차와 시각화 같은 진단 단계를 건너뛰면 쉽게 오해로 이어집니다.

다음 글에서는 p-value를 따로 떼어 더 깊게 다룹니다. 많은 보고서가 결론을 p < 0.05 한 줄로 적는 이유와, 그 문장이 왜 자주 잘못 읽히는지 정리해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- **Statistics 101 (8/10): 상관과 회귀 (현재 글)**
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Linear Regression](https://scikit-learn.org/stable/modules/linear_model.html)
- [Khan Academy — Correlation](https://www.khanacademy.org/math/statistics-probability/describing-relationships-quantitative-data)
- [Spurious Correlations (Vigen)](https://www.tylervigen.com/spurious-correlations)
- [Wikipedia — Anscombe's Quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Correlation, Regression, Modeling, Beginner
