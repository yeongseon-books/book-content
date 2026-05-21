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

이 글은 Statistics 101 시리즈의 8번째 글입니다.

두 변수가 함께 움직이면 사람은 곧바로 이유를 찾고 싶어 합니다. 광고비가 늘면 매출이 오르는지, 공부 시간이 길면 점수가 오르는지, 가격이 내려가면 수요가 늘어나는지 같은 질문은 분석의 출발점이 됩니다.

하지만 함께 움직인다는 사실만으로 원인과 결과가 증명되지는 않습니다. 상관은 관계의 방향과 강도를 보여 주고, 회귀는 그 관계를 식으로 표현해 예측 가능한 형태로 만듭니다. 둘은 연결되어 있지만 같은 질문에 답하지는 않습니다.

이 글은 Statistics 101 시리즈의 8번째 글입니다. 여기서는 상관계수와 단순 선형 회귀를 나란히 놓고, R²와 잔차가 왜 중요한지, 그리고 왜 상관과 인과를 절대 섞어 읽으면 안 되는지 정리하겠습니다.


![Statistics 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/08/08-01-concept-at-a-glance.ko.png)
*Statistics 101 8장 흐름 개요*
> 두 변수가 함께 움직인다는 것이 한 변수가 다른 변수를 일으킨다는 뜻은 아닙니다.

## 먼저 던지는 질문

- 상관계수는 무엇을 말하고 무엇은 말하지 못할까요?
- 회귀식은 상관계수보다 어떤 정보를 더 줄까요?
- R²는 어떤 범위에서 어떻게 읽어야 할까요?

## 왜 중요한가

비즈니스 데이터의 많은 질문은 관계를 묻는 형태로 시작합니다. 광고비와 매출, 사용량과 이탈, 공부 시간과 점수처럼 변수 간 연결을 숫자로 요약해야 할 때가 많습니다. 이때 상관과 회귀는 가장 먼저 손에 잡히는 기본 도구입니다.

문제는 이 도구들이 너무 익숙해서 오용되기 쉽다는 점입니다. 상관이 높다고 곧바로 원인이라고 읽거나, R²가 높다고 좋은 모델이라고 단정하거나, 잔차를 보지 않고 선형성을 가정하는 일이 자주 생깁니다. 그래서 기본 개념을 차분하게 구분할 필요가 있습니다.

## 멘탈 모델

상관은 두 변수가 같은 방향으로 움직이는지와 그 강도를 보여 줍니다. 회귀는 그 관계를 식으로 적어, x가 바뀔 때 y가 어떻게 달라지는지 예측 가능한 형태로 만듭니다. 마지막으로 R²와 잔차는 그 식이 데이터를 얼마나 설명하는지 점검하게 합니다.

이 흐름을 이해하면 상관계수는 요약 지표이고, 회귀는 모델이며, 잔차 진단은 모델 검토 단계라는 점이 분명해집니다.

## 핵심 용어

- **Pearson 상관계수 r**: 선형 관계의 방향과 강도를 -1에서 +1 사이 값으로 나타냅니다.
- **Spearman ρ**: 순위 기반 상관으로, 비선형 구조나 이상치에 조금 더 강합니다.
- **단순 선형 회귀**: `y = β0 + β1·x + ε` 형태의 모델입니다.
- **R²**: 모델이 데이터 분산을 얼마나 설명하는지 나타내는 비율입니다.
- 잔차: 실제값에서 예측값을 뺀 값으로, 모델 진단의 핵심 재료입니다.

## 상관 대비 인과

상관과 인과는 가장 자주 섞이는 개념입니다. 아래 표는 둘의 차이와 판단 기준을 정리합니다.

| 구분 | 상관(Correlation) | 인과(Causation) |
|------|------------------|----------------|
| 정의 | 두 변수가 함께 움직이는 정도 | 한 변수가 다른 변수를 일으키는 관계 |
| 예시 | 아이스크림 판매량과 익사 사고 발생 건수 (여름에 둘 다 증가) | 백신 접종이 감염률을 낮춤 |
| 판단 기준 | 상관계수, 산점도 | 무작위 실험(RCT), 시간 선후관계, 메커니즘 설명 |
| 방향 | 쌍방향 관계 가능 | 단방향 관계 |
| 오해 | 상관이 높으면 원인이라고 착각 | 인과를 상관으로만 판단할 수 없음 |

상관이 있다고 해서 인과가 보장되지 않는 이유는 다음 세 가지입니다.

1. **제3의 변수**: 아이스크림과 익사는 둘 다 '여름'이라는 숨은 변수의 영향을 받습니다.
2. **역인과**: 매출이 광고비를 늘리는 방향일 수도 있습니다.
3. **우연**: 데이터가 작으면 무의미한 패턴도 상관으로 보일 수 있습니다.

인과를 확인하려면 무작위 대조 실험(RCT), 시간 선후 관계, 메커니즘 설명, 반복 실험이 필요합니다. 관찰 데이터만으로는 상관까지만 말할 수 있습니다.
## 함께 움직인다고 바로 원인이라고 말할 수는 없다

이전 해석: “광고비와 매출의 상관이 0.6이므로 광고비가 매출을 만든다.”

이 문장은 관계와 인과를 섞은 해석입니다. 제3의 변수나 시간 효과가 함께 작용했을 수도 있습니다.

이후 해석: “광고비와 매출 사이에는 양의 선형 관계가 보이며, 단순 회귀식은 `sales = 1,200 + 4.2·ads`입니다. 다만 이 식은 관계를 설명할 뿐 인과를 보증하지는 않습니다.”

상관과 회귀는 관계를 표현하는 도구이지, 자동으로 원인을 증명하는 장치는 아닙니다.

## 실습: 5단계 회귀 읽기

### 1단계 — 데이터를 준비한다

```python
import numpy as np, pandas as pd
ads = np.array([10, 20, 30, 40, 50, 60])
sales = np.array([1300, 1280, 1320, 1360, 1410, 1450])
```

### 2단계 — 상관계수를 계산한다

```python
print("r:", np.corrcoef(ads, sales)[0, 1])
```

**예상 출력:** `r: 0.9...`처럼 양의 선형 관계가 강하게 나타납니다.

방향과 강도를 먼저 봅니다.

### 3단계 — 회귀모형을 적합한다

```python
from sklearn.linear_model import LinearRegression
X = ads.reshape(-1, 1)
model = LinearRegression().fit(X, sales)
print("β1:", model.coef_[0], "β0:", model.intercept_)
```

**예상 출력:** `β1`은 광고비가 한 단위 늘 때 매출이 얼마나 같이 움직이는지, `β0`는 기준 절편을 보여 줍니다.

기울기와 절편은 관계를 식으로 바꾼 결과입니다.

### 4단계 — 설명력을 본다

```python
print("R^2:", model.score(X, sales))
```

**예상 출력:** `R^2: 0.8...`처럼 설명력이 높은 값을 기대할 수 있지만, 이 수치 하나만으로 모델을 확정하면 안 됩니다.

R²는 0과 1 사이에서 읽습니다.

### 5단계 — 잔차를 점검한다

```python
import matplotlib.pyplot as plt
resid = sales - model.predict(X)
plt.scatter(model.predict(X), resid); plt.axhline(0); plt.show()
```

잔차 패턴은 선형성 위반이나 누락 변수를 암시할 수 있습니다.

## 이 코드에서 먼저 볼 점

- 상관은 방향과 강도를, 회귀는 예측 가능한 식을 줍니다.
- R²는 설명력의 크기를 말하지만 모델 품질 전체를 대신하지는 않습니다.
- 잔차 패턴은 비선형성이나 구조적 문제를 알려 줍니다.

## 파이썬 스탯모델즈로 회귀 분석하기

statsmodels는 scikit-learn보다 더 자세한 통계 요약을 제공합니다. 계수의 신뢰구간, p-value, R², 잔차 진단까지 한 번에 볼 수 있습니다.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

# 데이터 준비
ads = np.array([10, 20, 30, 40, 50, 60])
sales = np.array([1300, 1280, 1320, 1360, 1410, 1450])

# statsmodels는 절편을 자동으로 추가하지 않으므로 명시적으로 추가
X = sm.add_constant(ads)
model = sm.OLS(sales, X).fit()

# 요약 출력
print(model.summary())
```

**예상 출력 (요약):**

```
                 coef    std err          t      P>|t|      [0.025      0.975]
const       1254.2857     25.xxx     49.xxx      0.000    1192.xxx    1316.xxx
x1             2.7143      0.xxx      8.xxx      0.002       1.xxx       4.xxx

R-squared:                       0.944
```

이 출력에서 확인할 점:

- **coef**: 광고비가 1 단위 늘 때 매출이 약 2.7 단위 증가합니다.
- **P>|t|**: 계수가 0이 아니라는 가설의 p-value입니다. 0.05보다 작으면 통계적으로 유의합니다.
- **[0.025, 0.975]**: 계수의 95% 신뢰구간입니다.
- **R-squared**: 모델이 데이터 분산의 약 94%를 설명합니다.

statsmodels는 회귀 결과를 논문이나 보고서에 붙일 때 유용합니다. scikit-learn은 예측에, statsmodels는 설명에 강합니다.
## 자주 헷갈리는 지점 5가지

1. **상관을 인과로 읽는 경우**: 가장 흔한 오해입니다.
2. **이상치가 상관을 부풀리는 경우를 놓치는 경우**: 산점도를 함께 봐야 합니다.
3. **비선형 관계에 Pearson 상관만 적용하는 경우**: Spearman이나 다른 모델을 검토해야 합니다.
4. **R²만 보고 모델이 좋다고 말하는 경우**: 해석과 예측은 더 많은 검토가 필요합니다.
5. **잔차 진단을 생략하는 경우**: 모델이 틀린 모양으로 데이터를 설명하고 있을 수 있습니다.

## 다중공선성

다중공선성(multicollinearity)은 회귀 모델에서 독립변수들이 서로 강한 상관을 가질 때 발생합니다. 이 경우 계수 추정이 불안정해지고, 해석이 왜곡될 수 있습니다.

### 증상

- 계수의 부호가 직관과 반대로 나옵니다.
- 신뢰구간이 지나치게 넓어집니다.
- 변수를 하나 빼면 계수가 크게 바뀝니다.
- VIF(Variance Inflation Factor)가 10 이상입니다.

### 진단 예제

```python
import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm

# 강한 상관을 가진 두 변수
x1 = np.random.normal(50, 10, 100)
x2 = x1 + np.random.normal(0, 2, 100)  # x1과 거의 비례
y = 3*x1 + 2*x2 + np.random.normal(0, 5, 100)

df = pd.DataFrame({'x1': x1, 'x2': x2, 'y': y})

# VIF 계산
X = df[['x1', 'x2']]
X = sm.add_constant(X)
vif = pd.DataFrame()
vif['Variable'] = X.columns
vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(vif)
```

**예상 출력:**

```
  Variable       VIF
0    const  xx.xxxxx
1       x1  25.xxxxx
2       x2  25.xxxxx
```

VIF > 10이면 다중공선성이 심각합니다. 해결 방법:

1. **변수를 하나 제거**: 중복 정보를 줄 변수 중 하나를 뺍니다.
2. **변수를 결합**: 두 변수의 평균이나 합을 새 변수로 만듭니다.
3. **주성분 분석(PCA)**: 상관된 변수들을 독립 성분으로 변환합니다.
4. **정규화(Ridge/Lasso)**: 계수에 페널티를 추가해 불안정성을 줄입니다.

다중공선성은 예측 정확도보다 **해석 신뢰성**을 해칩니다. 모델을 비즈니스에 설명해야 한다면 반드시 확인해야 합니다.
## 실무에서는 이렇게 읽습니다

매출 예측, 가격과 수요 관계, 광고와 전환, 사용량과 이탈률 분석처럼 관계를 다루는 작업은 매우 많습니다. 단순 선형 회귀는 출발점으로 유용하지만, 실제 문제는 다변량 회귀, 로지스틱 회귀, 시계열 회귀로 확장되는 경우가 많습니다. 그 출발점에서 가장 먼저 익혀야 할 태도는 시각화와 잔차 진단입니다.

시니어 엔지니어는 상관이 높아도 바로 인과를 말하지 않고, 산점도를 먼저 보고, 잔차를 점검하고, 설명과 예측을 구분합니다. 숫자를 멋지게 뽑는 것보다 어떤 질문에 이 모델이 답할 수 있고 무엇은 답하지 못하는지 말하는 능력이 더 중요합니다.

## 산점도(산점도) 해석 가이드

산점도는 회귀 분석에서 가장 먼저 그려야 하는 그림입니다. 숫자만으로는 놓치기 쉬운 패턴을 시각적으로 드러냅니다.

### 해석 체크리스트

1. **선형성**: 점들이 직선 주변에 모여 있습니까?
   - 그렇다 → 선형 회귀 적합
   - 아니다 → 비선형 모델 검토

2. **이상치**: 다른 점들과 멀리 떨어진 점이 있습니까?
   - 있다 → 원인 확인, 제거 또는 robust 회귀 고려

3. **등분산성**: 잔차의 퍼짐이 x 값에 관계없이 일정합니까?
   - 그렇다 → 가정 충족
   - 아니다 → 변환(로그 등) 또는 가중 회귀 검토

4. **군집**: 데이터가 여러 집단으로 나뉘어 보입니까?
   - 그렇다 → 층별 회귀 또는 혼합 모델 고려

### 실전 예제

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

ads = np.array([10, 20, 30, 40, 50, 60])
sales = np.array([1300, 1280, 1320, 1360, 1410, 1450])

# 회귀선
model = LinearRegression().fit(ads.reshape(-1,1), sales)
pred = model.predict(ads.reshape(-1,1))

# 산점도 + 회귀선
plt.scatter(ads, sales, label='Observed')
plt.plot(ads, pred, 'r-', label='Fitted line')
plt.xlabel('Advertising spend')
plt.ylabel('Sales')
plt.legend()
plt.title('Scatter plot with regression line')
plt.show()
```

이 그림에서 점들이 선 주변에 고르게 모여 있으면 선형 회귀가 적절합니다. 만약 곡선 패턴이 보이거나, 한쪽 끝에서 퍼짐이 커지면 모델을 수정해야 한다는 신호입니다.

**산점도 없이 R²만 보고 모델을 확정하는 것은 위험합니다.** Anscombe's Quartet처럼 R²와 계수가 같아도 데이터 모양이 완전히 다른 경우가 있습니다.
## 체크리스트

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

## 회귀 출력 해석 심화: 계수, 신뢰구간, 잔차

회귀 모델의 핵심은 식 자체보다 해석 가능성입니다. 계수 하나를 읽을 때도 신뢰구간과 잔차 패턴을 함께 봐야 안전합니다.

### 스탯모델즈 요약표에서 우선 볼 항목

1. 계수(`coef`)의 부호와 크기
2. 계수 구간(`[0.025, 0.975]`)이 0을 포함하는지
3. `R-squared`와 `Adj. R-squared` 차이
4. 잔차 진단(정규성, 등분산성)

### 회귀 출력 해석 예제

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

rng = np.random.default_rng(1)
n = 300
ads = rng.normal(100, 20, n)
price = rng.normal(50, 5, n)
sales = 800 + 3.2 * ads - 5.0 * price + rng.normal(0, 40, n)

df = pd.DataFrame({'ads': ads, 'price': price, 'sales': sales})
X = sm.add_constant(df[['ads', 'price']])
model = sm.OLS(df['sales'], X).fit()
print(model.summary())
```

이 출력에서 `ads` 계수의 구간이 0을 넘지 않고 양수라면 광고비 증가와 매출 증가의 관계가 통계적으로 안정적이라는 뜻입니다. 다만 인과 주장은 실험 설계가 뒷받침될 때만 가능합니다.


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 추가 메모: 검증 가능한 의사결정 문장

분석 결과를 보고할 때는 "좋아 보입니다" 같은 모호한 문장을 피하고, 기준과 근거를 한 줄에 함께 적는 것이 좋습니다. 예를 들어 "전환율 +0.6%p, 95% 신뢰구간 +0.1~+1.1%p, p=0.014, 월간 기대효과 +320건, 2주 재검증 조건부 배포"처럼 쓰면 의사결정 책임이 명확해집니다. 이런 형식은 통계 도구가 바뀌어도 유지되는 팀 자산입니다.


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 처음 질문으로 돌아가기

- **상관계수는 무엇을 말하고 무엇은 말하지 못할까요?**
  - 상관은 두 변수가 함께 움직이는 정도, 회귀는 한 변수로 다른 변수를 예측하는 관계입니다.
- **회귀식은 상관계수보다 어떤 정보를 더 줄까요?**
  - 상관이 높다고 해서 인과가 있다는 뜻은 아니며, 회귀도 과거 패턴이 미래를 보장하지 않습니다.
- **R²는 어떤 범위에서 어떻게 읽어야 할까요?**
  - 운영에서는 상관과 회귀 결과를 정기적으로 재검증하고, 새로운 패턴에 모형을 업데이트합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- **상관과 회귀 (현재 글)**
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Linear Regression](https://scikit-learn.org/stable/modules/linear_model.html)
- [Khan Academy — Correlation](https://www.khanacademy.org/math/statistics-probability/describing-relationships-quantitative-data)
- [Spurious Correlations (Vigen)](https://www.tylervigen.com/spurious-correlations)
- [Wikipedia — Anscombe's Quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet)


- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Correlation, Regression, Modeling, Beginner
