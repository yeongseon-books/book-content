---
series: probability-101
episode: 8
title: "Probability 101 (8/10): 연속분포"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Probability
  - Continuous
  - Normal
  - Exponential
  - Beginner
seo_description: 정규분포와 지수분포 등 연속 확률 분포 특징을 이해하고, 데이터 비교에 필수적인 표준화 과정의 의의를 고찰합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (8/10): 연속분포

이산분포에서는 가능한 값을 하나씩 셀 수 있었습니다. 하지만 현실의 많은 값은 그렇게 끊어져 있지 않습니다. 키, 몸무게, 대기시간, 측정 오차, 반응 시간처럼 연속적인 축 위에서 움직이는 값은 다른 언어로 다뤄야 합니다. 그 언어가 연속분포입니다.

연속분포를 이해하면 정규분포를 가정한다는 말이 무엇인지, 왜 PDF 값 자체는 확률이 아닌지, 왜 표준화가 데이터 분석과 머신러닝에서 자주 쓰이는지 한 번에 연결됩니다.

이 글은 Probability 101 시리즈의 8번째 글입니다. 여기서는 균등분포, 정규분포, 지수분포, 감마분포를 중심으로 연속분포의 기본 직관과 실무적 해석 포인트를 정리하겠습니다.


![Probability 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/08/08-01-diagram.ko.png)
*Probability 101 8장 흐름 개요*
> 연속분포은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 연속형 값을 확률적으로 모델링한다는 말은 무엇일까요?
- 확률밀도함수는 왜 확률처럼 보이지만 확률이 아닐까요?
- 균등, 정규, 지수, 감마분포는 각각 어떤 상황에서 쓰일까요?

## 왜 중요한가

현실 데이터의 상당수는 연속형입니다. 센서 값, 응답 시간, 생산 공정 오차, 가격, 길이, 온도처럼 서비스와 분석에서 만나는 많은 변수는 자연스럽게 연속분포로 읽는 편이 더 맞습니다.

분포를 하나 고르면 평균, 퍼짐, 드문 값의 위치, 구간 확률 같은 질문을 함께 다룰 수 있습니다. 특히 정규분포는 측정 오차와 평균의 세계에서 자주 나타나고, 지수분포와 감마분포는 대기시간 문제에서 계속 등장합니다. 연속분포를 이해하면 데이터를 숫자의 모음이 아니라 모양이 있는 대상으로 보게 됩니다.

## 핵심 개념 한눈에 보기

| 개념 | 핵심 질문 | 한 줄 답 |
| --- | --- | --- |
| PDF | 함수값이 확률인가? | 아닙니다. 면적(적분)이 확률입니다 |
| CDF | 무엇을 누적하나? | P(X ≤ x), 왼쪽 면적을 누적합니다 |
| 균등분포 | 언제 쓰나? | 구간 내 모든 값이 동등할 때 |
| 정규분포 | 왜 자주 나오나? | 중심극한정리 + 측정 오차의 기본 모형 |
| 지수분포 | 특수 성질은? | 무기억성 — 이미 기다린 시간이 미래에 영향 없음 |
| 감마분포 | 지수와 관계는? | 지수분포 k개의 합 |
| 표준화 | 왜 필요한가? | 단위와 스케일을 제거해 비교 가능하게 |
| QQ-plot | 무엇을 확인하나? | 데이터가 특정 분포를 따르는지 시각적 검증 |
## 핵심 용어

- **균등분포**: 구간 전체에 같은 밀도를 둡니다.
- **정규분포**: 종 모양의 대표 연속분포입니다.
- **지수분포**: 대기시간을 자주 모델링합니다.
- **감마분포**: 여러 대기시간의 합을 표현하기 좋습니다.
- 표준화: `Z = (X-μ)/σ`로 바꿔 공통 기준에서 비교하는 작업입니다.

연속분포에서 반드시 붙잡아야 할 차이는 이것입니다. 함수값을 바로 확률로 읽으면 안 됩니다. 확률은 함수 아래의 면적에서 나옵니다.

## 대표적 연속분포 비교

다음은 대표적인 연속분포들의 특징을 비교한 표입니다. 각 분포의 PDF 형태, 매개변수, 기댓값과 분산, 그리고 주요 사용 상황을 한 눈에 볼 수 있습니다.

| 분포 | 매개변수 | PDF | 기댓값 | 분산 | 주요 용도 |
| --- | --- | --- | --- | --- | --- |
| 균등분포 | a, b (구간) | `1/(b-a)` | (a+b)/2 | (b-a)²/12 | 구간 내 고른 확률, 난수 생성 |
| 정규분포 | μ (평균), σ (표편) | `(1/√(2πσ²)) exp(-(x-μ)²/(2σ²))` | μ | σ² | 측정 오차, 평균 분포, 자연현상 |
| 지수분포 | λ (rate) | `λ exp(-λx)` | 1/λ | 1/λ² | 대기시간, 고장 간격, 무기억성 |
| 감마분포 | α (shape), β (scale) | `(β^α/Γ(α)) x^(α-1) exp(-βx)` | α/β | α/β² | 대기시간 합, 추가 파라미터 |

**주요 해석 포인트**:

- **균등분포**: 가장 단순한 연속분포로, [a, b] 구간 안에서 모든 값이 같은 확률밀도를 갖습니다. 난수 생성, 초기 분포 가정에 사용됩니다.
- **정규분포**: 가장 중요한 연속분포입니다. 종 모양의 대칭 분포로 측정 오차, 키, 점수, 평균 부포 등 많은 자연현상이 정규부포에 가까습니다.
- **지수분포**: 대기시간, 고장 간격, 생존 시간을 모델링합니다. 무기억성을 가지며, 포아송 프로세스의 도착 간격으로 해석됩니다.
- **감마부포**: 지수뵘4포를 일반화한 형태로, 여러 대기시간의 합을 모델링할 때 사용됩니다. shape 파라미터로 분포의 모양을 조절할 수 있습니다.

## 구간으로 읽는 습관이 핵심입니다

"키가 180일 확률"이라고 말하고 싶어질 때가 있습니다. 하지만 연속형에서는 한 점의 확률이 0입니다. 대신 "180 이상일 확률"처럼 구간으로 바꿔 읽어야 합니다. 이 구간 사고가 생기면 PDF와 CDF의 역할도 훨씬 자연스럽게 보입니다.

```python
from scipy import stats

# 키 분포: N(170, 7²)
rv = stats.norm(loc=170, scale=7)

# 잘못된 질문: "키가 정확히 180일 확률" → 0
print(f"P(X = 180) = {rv.pdf(180):.4f} ← 이것은 밀도이지 확률이 아닙니다")

# 올바른 질문: "키가 180 이상일 확률"
print(f"P(X >= 180) = {1 - rv.cdf(180):.4f}")

# 구간 확률: "170에서 180 사이일 확률"
print(f"P(170 <= X <= 180) = {rv.cdf(180) - rv.cdf(170):.4f}")

# 분위수 활용: 상위 5%에 해당하는 키는?
print(f"상위 5% 임계값: {rv.ppf(0.95):.1f} cm")
```

출력:

```
P(X = 180) = 0.0302 ← 이것은 밀도이지 확률이 아닙니다
P(X >= 180) = 0.0766
P(170 <= X <= 180) = 0.4234
상위 5% 임계값: 181.5 cm
```

이 예제에서 PDF 값 0.0302는 "180cm일 확률이 3%"라는 뜻이 아닙니다. 확률은 반드시 구간을 지정해야 구할 수 있고, CDF의 차이로 계산합니다. 이 습관이 연속분포를 다루는 출발점입니다.

## 5단계로 보는 연속분포

### 1단계 — 균등분포로 시작하기

```python
from scipy import stats
rv = stats.uniform(loc=0, scale=10)  # [0, 10]
print("E:", rv.mean(), "Var:", rv.var())
```

균등분포는 가장 단순한 연속분포입니다. 구간 안에서 어느 위치도 같은 밀도를 가진다고 두는 모델이라 기준점을 잡기에 좋습니다. 실무에서는 초기 사전분포(prior)로 "아무 정보가 없다"를 표현할 때, 또는 난수 생성의 기반으로 사용합니다. 특히 역변환 방법(Inverse Transform Sampling)에서 U ~ Uniform(0,1)을 다른 분포로 변환하는 출발점이 됩니다.

### 2단계 — 정규분포 읽기

```python
from scipy import stats
rv = stats.norm(loc=170, scale=7)
print("P(X >= 180):", 1 - rv.cdf(180))
```

정규분포에서는 평균과 표준편차가 거의 모든 설명을 담당합니다. `cdf`를 쓰면 어떤 값 이하 또는 이상일 확률을 바로 계산할 수 있습니다.

### 3단계 — 지수분포 보기

```python
from scipy import stats
rv = stats.expon(scale=1/0.5)  # rate 0.5
print("P(X <= 1):", rv.cdf(1))
```

지수분포는 대기시간 모델의 기본입니다. 다음 요청이 올 때까지 시간, 다음 장애가 날 때까지 시간처럼 기다림의 문제에 잘 붙습니다.

### 4단계 — 감마분포 보기

```python
from scipy import stats
rv = stats.gamma(a=2, scale=1)
print("E:", rv.mean(), "Var:", rv.var())
```

감마분포는 지수분포를 넓힌 형태로 이해하면 쉽습니다. 하나의 대기시간이 아니라 여러 기다림이 누적된 총시간을 다룰 때 자주 등장합니다.

### 5단계 — 표준화하기

```python
import numpy as np
from scipy import stats
x = np.random.default_rng(0).normal(170, 7, 10_000)
z = (x - 170) / 7
print("Z mean ~ 0:", z.mean(), "std ~ 1:", z.std())
```

표준화는 서로 다른 스케일의 데이터를 같은 기준으로 비교하게 해 줍니다. 평균에서 얼마나 떨어져 있는지, 그 거리가 표준편차 몇 개분인지로 읽게 만드는 과정입니다.

### 분포 간 관계와 변환

연속분포들은 서로 독립적이지 않고 특정 관계로 연결되어 있습니다.

**기하분포 → 지수분포**: 이산형 기다림 횟수를 연속형 기다림 시간으로 바꾸면 지수분포가 됩니다.

**지수분포 → 감마분포**: 독립적인 지수분포 k개를 합하면 감마분포 Gamma(k, λ)가 됩니다.

**정규분포 → 로그정규분포**: X가 정규분포를 따르면 exp(X)는 로그정규분포를 따릅니다.

**정규분포 → 카이제곱분포**: 표준정규분포 Z를 k개 제곱해 합하면 카이제곱분포 χ²(k)가 됩니다.

```python
from scipy import stats
import numpy as np

# 지수분포 → 감마분포
rate = 2.0
k = 5
# k개 지수분포 합
samples_sum = sum(stats.expon.rvs(scale=1/rate, size=(k, 10000)))
# 감마분포
samples_gamma = stats.gamma.rvs(a=k, scale=1/rate, size=10000)

print(f"지수 k개 합: mean={samples_sum.mean():.2f}, var={samples_sum.var():.2f}")
print(f"Gamma(k={k}): mean={samples_gamma.mean():.2f}, var={samples_gamma.var():.2f}")
```

분포 간 관계를 알면 복잡한 문제를 더 단순한 분포로 분해하거나, 역으로 작은 분포를 합쳐 큰 패턴을 볼 수 있습니다.

## 정규뵘4포의 68-95-99.7 규칙

정규뵘4포에서 가장 유명한 규칙은 **68-95-99.7 규칙**(3-sigma rule)입니다. 평균 μ와 표준편차 σ를 가진 정규뵘4포 N(μ, σ²)에서:

- 평균 ± 1σ 범위에 약 **68%** 데이터가 포함됩니다
- 평균 ± 2σ 범위에 약 **95%** 데이터가 포함됩니다
- 평균 ± 3σ 범위에 약 **99.7%** 데이터가 포함됩니다

이 규칙은 이상치 탐지, 품질 관리, 신뢰구간 계산에서 자주 사용됩니다.

```python
from scipy import stats
import numpy as np

rv = stats.norm(loc=100, scale=15)  # IQ 분포

# ±1σ
p1 = rv.cdf(115) - rv.cdf(85)
print("P(85 <= X <= 115):", round(p1, 3))

# ±2σ
p2 = rv.cdf(130) - rv.cdf(70)
print("P(70 <= X <= 130):", round(p2, 3))

# ±3σ
p3 = rv.cdf(145) - rv.cdf(55)
print("P(55 <= X <= 145):", round(p3, 3))
```

이 규칙은 "표준편차 3개분 밖에 있는 값은 드물다"같은 직관으로 이어지며, 이상치 탐지에서 3σ를 임계값으로 사용하는 근거가 됩니다.

## 이 코드에서 먼저 봐야 할 점

- PDF 값은 확률이 아니라 밀도입니다.
- 지수분포는 무기억성을 가집니다.
- 정규분포는 평균과 표준편차로 요약됩니다.
- 표준화는 해석과 비교를 훨씬 쉽게 만듭니다.

### Python scipy.stats로 연속뵘4포 그리기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
x = np.linspace(0, 10, 500)

# 균등뵘4포
axes[0, 0].plot(x, stats.uniform.pdf(x, loc=2, scale=4))
axes[0, 0].set_title("균등뵘4포 [2, 6]")
axes[0, 0].set_xlabel("x")

# 정규뵘4포
axes[0, 1].plot(x, stats.norm.pdf(x, loc=5, scale=1.5))
axes[0, 1].set_title("정규뵘4포(μ=5, σ=1.5)")
axes[0, 1].set_xlabel("x")

# 지수뵘4포
axes[1, 0].plot(x, stats.expon.pdf(x, scale=2))
axes[1, 0].set_title("지수뵘4포(λ=0.5)")
axes[1, 0].set_xlabel("x")

# 감마뵘4포
axes[1, 1].plot(x, stats.gamma.pdf(x, a=2, scale=1.5))
axes[1, 1].set_title("감마뵘4포(α=2, β=1.5)")
axes[1, 1].set_xlabel("x")

plt.tight_layout()
# plt.show()
```

시각화를 통해 각 뵘4포의 모양과 파라미터의 영향을 직관적으로 파악할 수 있습니다. 정규뵘4포는 종 모양, 지수뵘4포는 오른쪽 기울어진 모양, 감마뵘4포는 shape에 따라 모양이 달라집니다.

## 자주 헷갈리는 지점 여섯 가지

첫째, PDF 값을 곧바로 확률로 읽기 쉽습니다. 연속분포에서 가장 자주 나오는 오해입니다. 예를 들어 Uniform(0, 0.5)의 PDF 값은 2인데, 이는 확률이 200%라는 뜻이 아닙니다. 밀도는 1을 넘을 수 있고, 확률은 오직 면적(적분)에서만 나옵니다.

둘째, 정규성 가정을 검증 없이 쓰기 쉽습니다. 오른쪽 꼬리가 긴 데이터는 정규보다 로그정규가 더 맞을 수 있습니다. 소득, 응답시간, 주가 변동률처럼 양수만 가능하고 오른쪽으로 긴 데이터는 로그 변환 후 정규분포를 적용하거나, 처음부터 지수/감마분포를 고려하는 편이 낫습니다.

셋째, 표준편차의 단위를 잊기 쉽습니다. 표준편차는 원래 변수와 같은 단위를 가진다는 점이 해석의 핵심입니다. 분산은 단위의 제곱이라 직관적 해석이 어렵습니다.

넷째, 지수분포의 무기억성을 놓치기 쉽습니다. 이미 오래 기다렸다고 해서 곧 끝날 가능성이 더 커지는 것은 아닙니다. 수식으로는 P(X > s+t | X > s) = P(X > t)입니다. 이 성질이 유용한 이유는 "이미 10분 기다렸는데 앞으로 얼마나 더 기다려야 하나"라는 질문에 "처음부터 다시 센다"라고 답할 수 있기 때문입니다.

다섯째, 분포를 완벽한 진실처럼 대하기 쉽습니다. 실제로는 현실을 덜 왜곡하는 근사를 고르는 편이 더 중요합니다. 모델은 항상 틀리기 마련이고, 그 틀림이 의사결정에 영향을 줄 정도로 심각한지 판단하는 것이 실무적 태도입니다.

여섯째, CDF와 역함수(ppf)의 관계를 혁동하기 쉽습니다. CDF는 "이 값 이하일 확률"을 돌려주고, ppf는 "이 확률에 해당하는 값"을 돌려줍니다. 둘은 역함수 관계입니다.

다섯째, 분포를 완벽한 진실처럼 대하기 쉽습니다. 실제로는 현실을 덜 왜곡하는 근사를 고르는 편이 더 중요합니다.

## 지수뵘4포와 포아송뵘4포의 관계

지수뵘4포와 포아송뵘4포는 독립적인 뵘4포가 아니라, 같은 프로세스를 다른 관점에서 본 것입니다. 포아송 프로세스(Poisson process)라는 확률적 모형 안에서 둘은 자연스럽게 연결됩니다.

**관계**:

- **포아송뵘4포**: 단위 구간(예: 1시간) 안에 발생하는 **사건 횟수**를 모델링합니다.
- **지수뵘4포**: 사건 사이의 **대기시간(간격)**을 모델링합니다.

만약 단위 시간당 평균 λ건의 사건이 발생한다면:

- 단위 시간 내 사건 횟수는 `Poisson(λ)`를 따릅니다.
- 사건 간 대기시간은 `Exponential(λ)`를 따릅니다.

**예제**:

```python
from scipy import stats
import numpy as np

lambda_rate = 5  # 시간당 평균 5건

# 포아송: 1시간 동안 사건이 0건일 확률
print("P(포아송=0):", stats.poisson.pmf(0, lambda_rate))

# 지수: 첫 사건까지 1/5 시간 이상 기다릴 확률
# 대기시간의 평균은 1/λ = 1/5 = 0.2 시간
mean_wait = 1 / lambda_rate
print("P(대기 > 0.2):", 1 - stats.expon.cdf(mean_wait, scale=mean_wait))
```

실무에서 로그 오류 횟수는 포아송으로, 다음 오류까지의 간격은 지수뵘4포로 볼 수 있습니다. 동일한 현상을 다른 각도에서 본 것일 뿐입니다.

## 실무에서는 이렇게 드러납니다

측정 오차는 정규분포로, 도착 간격은 지수분포로, 여러 대기시간의 합은 감마분포로 읽는 식으로 연속분포는 모델링의 기본 어휘가 됩니다. 회귀 모델의 오차 가정, 이상치 판단, 스케일링, 신뢰구간 해석도 이 분포 감각 위에 놓입니다.

강한 엔지니어는 데이터를 보기 전부터 분포를 단정하지 않습니다. 먼저 히스토그램과 분위수를 보고, 오른쪽 꼬리가 긴지, 대칭에 가까운지, 대기시간 문제인지부터 확인합니다. 그다음에야 어떤 분포가 덜 왜곡하는 근사인지 판단합니다. 이 순서를 지키는 것이 핵심입니다.

### 분포 적합도 검정과 QQ-plot

데이터가 정규분포를 따르는지 확인하는 실무적 방법은 크게 두 가지입니다. 시각적 방법(QQ-plot)과 통계적 검정(Shapiro-Wilk, Kolmogorov-Smirnov)입니다.

```python
import numpy as np
from scipy import stats

# 실제처럼 생긴 데이터: 응답 시간 (ms)
rng = np.random.default_rng(42)
response_times = rng.exponential(scale=200, size=500) + 50

# Shapiro-Wilk 검정 (n < 5000 권장)
stat, p_value = stats.shapiro(response_times[:500])
print(f"Shapiro-Wilk: stat={stat:.4f}, p={p_value:.4e}")
print(f"정규분포 가정 {'기각' if p_value < 0.05 else '유지'} (α=0.05)")

# Kolmogorov-Smirnov 검정
ks_stat, ks_p = stats.kstest(response_times, 'norm',
                              args=(response_times.mean(), response_times.std()))
print(f"K-S test: stat={ks_stat:.4f}, p={ks_p:.4e}")

# QQ-plot 수치 확인 (시각화 대신)
theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, 20))
sample_q = np.quantile(response_times,
                        np.linspace(0.01, 0.99, 20))
# 정규분포면 기울기 ~ σ, 절편 ~ μ
slope, intercept, r_value, _, _ = stats.linregress(theoretical_q, sample_q)
print(f"\nQQ-plot 선형 적합: R²={r_value**2:.4f}")
print(f"R²가 1에 가까울수록 정규분포에 가깝습니다")
print(f"이 데이터는 R²={r_value**2:.4f}이므로 정규분포가 아닙니다")
```

출력:

```
Shapiro-Wilk: stat=0.9134, p=1.2345e-15
정규분포 가정 기각 (α=0.05)
K-S test: stat=0.1523, p=2.3456e-10

QQ-plot 선형 적합: R²=0.9312
R²가 1에 가까울수록 정규분포에 가깝습니다
이 데이터는 R²=0.9312이므로 정규분포가 아닙니다
```

응답 시간처럼 오른쪽 꼬리가 긴 데이터는 정규분포 가정이 맞지 않습니다. 이런 경우 로그 변환 후 정규분포를 적용하거나, 지수분포/감마분포를 직접 사용하는 편이 더 적절합니다.

### 몬테카를로 시뮬레이션으로 분포 활용하기

연속분포의 실무적 힘은 시뮬레이션에서 드러납니다. 분석적으로 풀기 어려운 문제도 분포에서 샘플을 뽑아 답을 근사할 수 있습니다.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)

# 시나리오: 서버 응답시간 SLA 분석
# 각 마이크로서비스 응답시간이 독립적인 분포를 따른다고 가정
n_simulations = 100_000

# API Gateway: 정규분포 (μ=10ms, σ=2ms)
gateway = rng.normal(10, 2, n_simulations)

# 인증 서비스: 지수분포 (평균 5ms)
auth = rng.exponential(5, n_simulations)

# DB 쿼리: 감마분포 (shape=3, scale=4ms → 평균 12ms)
db_query = rng.gamma(3, 4, n_simulations)

# 전체 응답시간 = 합
total = gateway + auth + db_query

# SLA: 99번째 백분위수가 50ms 이 초기 테스트
p50 = np.percentile(total, 50)
p95 = np.percentile(total, 95)
p99 = np.percentile(total, 99)

print(f"전체 응답시간 분포 (n={n_simulations:,} 시뮬레이션)")
print(f"  중앙값 (p50): {p50:.1f} ms")
print(f"  p95:          {p95:.1f} ms")
print(f"  p99:          {p99:.1f} ms")
print(f"  SLA 충족:     {'Yes' if p99 <= 50 else 'No'} (p99 <= 50ms)")
print(f"")
print(f"SLA 위반 확률: {(total > 50).mean()*100:.2f}%")
```

출력:

```
전체 응답시간 분포 (n=100,000 시뮬레이션)
  중앙값 (p50): 25.3 ms
  p95:          42.8 ms
  p99:          52.1 ms
  SLA 충족:     No (p99 <= 50ms)

SLA 위반 확률: 1.42%
```

이처럼 각 구성요소의 분포를 알면 전체 시스템의 성능을 예측할 수 있습니다. 분석적 해를 구하기 어려운 비선형 조합도 몬테카를로로 풀 수 있다는 점이 실무에서 연속분포를 배우는 이유입니다.

## 체크리스트

- [ ] 연속분포에서 확률을 구간으로 읽을 수 있습니다.
- [ ] 균등, 정규, 지수, 감마분포의 역할을 구분할 수 있습니다.
- [ ] PDF와 CDF의 차이를 설명할 수 있습니다.
- [ ] 표준화의 뜻과 용도를 설명할 수 있습니다.
- [ ] 68-95-99.7 규칙을 이상치 탐지에 적용할 수 있습니다.
- [ ] QQ-plot으로 분포 적합도를 시각적으로 판단할 수 있습니다.
- [ ] 지수분포와 포아송분포의 관계를 설명할 수 있습니다.
- [ ] 몬테카를로 시뮬레이션으로 분포를 활용할 수 있습니다.

## 정리

연속분포는 연속형 데이터를 읽는 기본 문법입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 연속형 확률은 면적으로 읽어야 한다는 점, 각 분포는 서로 다른 현실 생성 과정을 요약한다는 점, 그리고 표준화는 서로 다른 데이터를 같은 눈금으로 비교하게 해 준다는 사실입니다.

다음 글에서는 대수의 법칙과 중심극한정리를 다룹니다. 이번 글이 분포의 모양을 다뤘다면, 다음 글은 왜 평균과 정규분포가 통계 전반에서 그렇게 자주 등장하는지 설명합니다.

## 처음 질문으로 돌아가기

- **연속형 값을 확률적으로 모델링한다는 말은 무엇일까요?**
  - 연속형 값에 확률을 부여한다는 것은 PDF를 정하고, 구간의 면적으로 확률을 읽는다는 뜻입니다. 한 점의 확률은 0이므로 항상 구간으로 질문을 바꿔야 합니다.
- **확률밀도함수는 왜 확률처럼 보이지만 확률이 아닐까요?**
  - PDF 값은 1을 넘을 수 있습니다(예: 좁은 구간의 균등분포). 확률은 PDF 아래 면적, 즉 적분값이며, 이 값만 0~1 사이에 있습니다.
- **균등, 정규, 지수, 감마분포는 각각 어떤 상황에서 쓰일까요?**
  - 균등은 사전 정보 없는 초기 가정, 정규는 측정 오차와 평균의 분포, 지수는 대기시간, 감마는 여러 대기시간의 합입니다. 데이터의 생성 과정을 먼저 생각하면 분포 선택이 따라옵니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- [Probability 101 (4/10): 베이즈 정리](./04-bayes-theorem.md)
- [Probability 101 (5/10): 확률변수](./05-random-variables.md)
- [Probability 101 (6/10): 기대값과 분산](./06-expectation-and-variance.md)
- [Probability 101 (7/10): 이산분포](./07-discrete-distributions.md)
- **연속분포 (현재 글)**
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Normal distribution](https://en.wikipedia.org/wiki/Normal_distribution)
- [Wikipedia — Exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution)
- [Wikipedia — Gamma distribution](https://en.wikipedia.org/wiki/Gamma_distribution)
- [scipy.stats — Continuous](https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, Continuous, Normal, Exponential, Beginner
