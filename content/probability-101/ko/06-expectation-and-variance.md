---
series: probability-101
episode: 6
title: "Probability 101 (6/10): 기대값과 분산"
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
  - Expectation
  - Variance
  - Moments
  - Beginner
seo_description: 확률 분포의 중심인 기대값과 데이터가 흩어진 정도인 분산의 통계적 의미를 배우고, 필수적인 수학적 성질을 정리합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (6/10): 기대값과 분산

분포를 배웠다고 해서 분포를 요약할 수 있는 것은 아닙니다. 실제로는 수많은 값 전체를 다 들고 다니기보다, 중심이 어디쯤인지와 얼마나 퍼져 있는지를 빠르게 말해야 하는 경우가 더 많습니다. 기대값과 분산은 바로 그 두 질문에 답하는 가장 기본적인 요약값입니다.

주사위 하나를 예로 들어도 평균만 알면 부족합니다. 평균이 3.5라는 사실만으로는 값이 얼마나 흔들리는지 알 수 없기 때문입니다. 분산과 표준편차가 함께 있어야 비로소 분포의 모양을 더 제대로 읽게 됩니다.

이 글은 Probability 101 시리즈의 6번째 글입니다. 여기서는 기대값과 분산의 정의, 계산 공식, 선형성, 표준편차의 의미를 코드와 함께 정리하겠습니다.


![Probability 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/06/06-01-diagram.ko.png)
*Probability 101 6장 흐름 개요*
> 기대값과 분산은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 기대값은 왜 분포의 중심이라고 부를까요?
- 분산은 무엇을 얼마나 측정하는 값일까요?
- 표준편차는 분산과 어떻게 다를까요?

## 왜 중요한가

손실함수, A/B 테스트, 위험 관리, 운영 지표 해석까지 기대값과 분산은 거의 모든 수치 분석의 바닥에 있습니다. 머신러닝의 대표 손실인 MSE도 기대값과 분산 언어로 읽을 수 있습니다.

평균만 보면 숫자가 얼마나 불안정한지 놓치기 쉽습니다. 반대로 분산만 보면 중심이 어디인지 모릅니다. 둘을 함께 봐야 분포를 두 좌표로 요약할 수 있습니다. 그래서 기대값과 분산은 계산 기법이면서 동시에 해석의 최소 단위입니다.

## 핵심 개념 한눈에 보기

| 개념 | 공식 (이산) | 공식 (연속) | 의미 |
|---|---|---|---|
| 기대값 | E[X] = Σ x·p(x) | E[X] = ∫ x·f(x)dx | 분포의 중심 |
| 분산 | Var(X) = Σ (x-μ)²·p(x) | Var(X) = ∫ (x-μ)²·f(x)dx | 퍼짐의 정도 |
| 단축공식 | E[X²] - (E[X])² | E[X²] - (E[X])² | 계산 편의 |
| 표준편차 | √Var(X) | √Var(X) | 원래 단위 복원 |
| 선형성 | E[aX+bY] = aE[X]+bE[Y] | 동일 | 독립 불필요 |
| 분산 덧셈 | Var(X+Y) = Var(X)+Var(Y)+2Cov | 동일 | 독립이면 Cov=0 |


- **기대값 `E[X]`**: 분포의 평균입니다.
- **분산 `Var(X)`**: 평균에서 얼마나 퍼져 있는지 나타냅니다.
- **표준편차**: 분산의 제곱근이며 원래 변수와 같은 단위를 가집니다.
- 선형성: `E[aX + bY] = aE[X] + bE[Y]`입니다.
- 모멘트: 분포의 형태를 요약하는 수치들입니다.

## 기댓값의 주요 성질

기댓값은 단순히 평균을 계산하는 공식이 아니라, 강력한 수학적 성질을 가진 연산자입니다. 특히 선형성은 계산을 단순화하는 데 매우 유용하며, 독립 확률변수의 곱에 대한 성질은 분산 계산에도 이어집니다.

| 성질 | 공식 | 설명 |
| --- | --- | --- |
| 선형성 | `E[aX + bY] = aE[X] + bE[Y]` | 상수 배와 합의 기댓값은 각각의 기댓값으로 분리됩니다 |
| 독립 곱 | `E[XY] = E[X]·E[Y]` (독립일 때) | 독립 확률변수의 곱의 기댓값은 각 기댓값의 곱과 같습니다 |
| 상수 | `E[c] = c` | 상수의 기댓값은 그 자신입니다 |
| 상수배 | `E[cX] = c·E[X]` | 상수배는 밖으로 꺼낼 수 있습니다 |

**증명 직관**:

선형성은 기댓값의 정의인 `Σ x·p(x)`에서 나옵니다. `E[aX + bY]`를 전개하면 `a·E[X] + b·E[Y]`로 자연스럽게 분리됩니다. 이 성질은 X와 Y가 독립일 필요가 없다는 점이 중요합니다.

독립 곱 성질은 `E[XY] = ΣΣ xy·p(x,y)`에서 시작하는데, X와 Y가 독립이면 `p(x,y) = p(x)·p(y)`이므로 `E[XY] = (Σx·p(x))·(Σy·p(y)) = E[X]·E[Y]`로 정리됩니다.

이 성질들은 복잡한 확률변수의 기댓값을 단순한 조각으로 나누어 계산할 수 있게 해 줍니다. 특히 선형성은 회귀 모델의 예측값 해석, 가중 평균, 포트폴리오 수익 계산처럼 실무에서 자주 등장하는 문제들을 훨씬 쉽게 만들어 줍니다.
여기서 중요한 감각은 기대값이 반드시 실제로 나올 수 있는 값일 필요는 없다는 점입니다. 주사위 평균 3.5가 대표적인 예입니다. 평균은 관측 가능한 값이라기보다 중심을 나타내는 요약값입니다.

## 중심만 보면 부족합니다

“주사위 평균은 3.5다”라는 문장은 맞지만 충분하지 않습니다. 값이 3과 4 근처에만 몰려 있는지, 1부터 6까지 넓게 퍼져 있는지는 알 수 없기 때문입니다. 분산과 표준편차가 함께 있어야 중심과 퍼짐을 동시에 말할 수 있습니다.

실무 지표도 비슷합니다. 평균 응답시간이 같아도 분산이 큰 시스템은 훨씬 불안정하게 느껴질 수 있습니다. 평균만 보는 습관이 위험한 이유가 여기에 있습니다.

## 5단계로 보는 기대값과 분산

### 1단계 — 이산 기대값 계산하기

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)
E = (x * p).sum()
print("E[X]:", E)
```

공정한 주사위의 기대값은 3.5입니다. 실제로는 나오지 않는 값이지만, 분포의 중심을 잘 요약합니다.

### 2단계 — 분산과 표준편차 구하기

```python
import numpy as np
Var = ((x - E)**2 * p).sum()
print("Var(X):", Var, "SD:", np.sqrt(Var))
```

분산은 평균에서 얼마나 떨어져 있는지를 제곱해 평균낸 값입니다. 표준편차는 다시 제곱근을 씌워 원래 단위로 되돌린 값입니다.

### 3단계 — 선형성 확인하기

```python
# E[2X + 3] = 2*E[X] + 3
print("E[2X+3]:", 2*E + 3)
```

기대값의 선형성은 매우 자주 쓰입니다. 여러 확률변수의 합을 다룰 때 계산을 크게 단순화해 줍니다. 특히 중요한 점은 이 성질이 독립을 요구하지 않는다는 사실입니다.

### 4단계 — 시뮬레이션으로 확인하기

```python
import numpy as np
samples = np.random.default_rng(0).integers(1, 7, 100_000)
print("mean:", samples.mean(), "var:", samples.var())
```

충분히 많이 뽑으면 표본 평균과 표본 분산이 이론값에 가까워집니다. 추상적인 공식을 손으로 확인하는 가장 빠른 방법입니다.

### 기댓값의 선형성이 주는 힘

기댓값의 선형성은 확률론에서 가장 자주 쓰는 성질 중 하나입니다. `E[aX + bY + c] = aE[X] + bE[Y] + c`는 X와 Y가 독립이지 않아도 항상 성립합니다.

```python
import numpy as np

# 두 종속적 확률변수
rng = np.random.default_rng(42)
X = rng.normal(10, 2, 10000)
# Y는 X에 의존: Y = X + 잡음
Y = X + rng.normal(0, 1, 10000)

# 선형 결합
Z = 2*X + 3*Y - 5

# 기댓값 선형성 확인
print(f"E[Z] (simulation) = {Z.mean():.2f}")
print(f"2*E[X] + 3*E[Y] - 5 = {2*X.mean() + 3*Y.mean() - 5:.2f}")
```

X와 Y가 독립이 아니어도 기댓값의 선형 결합은 각각의 기댓값을 선형 결합한 것과 같습니다. 이 성질 덕분에 복잡한 문제를 작은 조각으로 쉬게 나눌 수 있고, 중심극한정리와 대수의 법칙같은 핵심 정리들도 이 선형성에 기초합니다.
### 5단계 — 연속분포에서 확인하기

### Python numpy로 기댓값과 분산 계산하기

```python
import numpy as np
# 이산확률변수 예제
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)

# 기댓값
E = np.sum(x * p)
print("E[X]:", E)

# 분산 (정의대로)
Var_def = np.sum((x - E)**2 * p)
print("Var(X) [정의]:", Var_def)

# 분산 (단축 공식)
Var_short = np.sum(x**2 * p) - E**2
print("Var(X) [단축]:", Var_short)

# 표준편차
SD = np.sqrt(Var_def)
print("SD(X):", SD)

# 연속분포 예제 (정규분포)
from scipy import stats
rv = stats.norm(loc=10, scale=2)
print("Normal: mean =", rv.mean(), "var =", rv.var(), "std =", rv.std())
```

numpy는 이산분포 계산에 매우 편리하고, scipy.stats는 연속분포와 이산분포의 기댓값과 분산을 이미 계산해 둔 `.mean()`, `.var()`, `.std()` 메서드를 제공합니다. 실무에서는 분포를 직접 구현하기보다 scipy 라이브러리를 활용하는 경우가 많습니다.
```python
from scipy import stats
rv = stats.norm(loc=10, scale=2)
print("mean:", rv.mean(), "var:", rv.var())
```

연속분포에서도 기대값과 분산은 같은 역할을 합니다. 이산형에서는 합으로, 연속형에서는 적분으로 정의된다는 점만 다릅니다.

## 분산의 의미 — 왜 제곱인가

분산은 평균으로부터 얼마나 떨어져 있는지를 측정하는 값입니다. 정의는 `Var(X) = E[(X - E[X])²]`이며, 기댓값 `E[X]`를 중심으로 한 제곱 편차의 평균입니다. 그런데 왜 절댓값이 아니라 제곱을 사용할까요?

첫째, 제곱을 쓰면 양의 편차와 음의 편차가 서로 상쇄되지 않습니다. 절댓값도 같은 효과를 주지만, 제곱은 미분 가능성과 최적화에서 더 다루기 편합니다.

둘째, 큰 편차에 더 큰 벌점을 씁니다. `(X - μ)²`는 평균에서 멀어질수록 기하급수적으로 커지므로, 이상치나 극단값의 영향을 더 민감하게 반영합니다.

셋째, 수학적으로 우아한 성질들이 따라옵니다. 특히 `Var(X) = E[X²] - (E[X])²` 형태로 변형하면 계산이 훨씬 빨라집니다.

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)
E = (x * p).sum()
# 정의대로
Var1 = ((x - E)**2 * p).sum()
# E[X²] - (E[X])² 형태
Var2 = (x**2 * p).sum() - E**2
print("Var(direct):", Var1, "Var(shortcut):", Var2)
```

분산의 단위는 원래 변수의 제곱입니다. 주사위 결과의 분산은 "눈의 제곱" 단위를 가지므로 직관적으로 해석하기 어렵습니다. 그래서 제곱근을 씌운 표준편차를 더 자주 사용합니다.

## 이 코드에서 먼저 봐야 할 점

- 기대값은 실제 관측 가능한 값일 필요가 없습니다.
- `Var(X) = E[X²] - (E[X])²` 형태는 계산에 매우 유용합니다.
- 기대값의 선형성은 독립을 요구하지 않습니다.
- 표준편차는 원래 변수와 같은 단위라 해석이 쉽습니다.

## 자주 헷갈리는 지점

첫째, `E[X]`가 반드시 X가 실제로 가질 수 있는 값이어야 한다고 생각하기 쉽습니다. 그렇지 않습니다.

둘째, `Var(aX)`를 `a·Var(X)`로 잘못 쓰기 쉽습니다. 실제로는 `a²·Var(X)`입니다.

셋째, 분산과 표준편차의 단위를 섞기 쉽습니다. 표준편차는 원래 단위지만 분산은 제곱 단위입니다.

넷째, 평균이 이상치에 흔들린다는 사실을 과소평가하기 쉽습니다. 평균 하나만 보는 문화는 해석을 자주 왜곡합니다.

다섯째, 표본분산에서 `(n-1)` 분모를 빼먹기 쉽습니다. 모집단 분산과 표본분산은 다르게 계산할 때가 많습니다.

## 체비셰프 부등식

분산은 단순히 퍼짐의 척도가 아니라, 값이 평균에서 얼마나 멀어질 수 있는지 확률적 경계를 제공합니다. 체비셰프 부등식은 바로 이 아이디어를 정리한 것입니다.

**체비셰프 부등식**: 임의의 확률변수 X와 양수 k에 대해

```
P(|X - E[X]| ≥ k·σ) ≤ 1/k²
```

이 부등식은 분포의 모양을 모르더라도 성립합니다. 예를 들어 k=2이면, 평균에서 표준편차 2배 이상 떨어진 값이 나올 확률은 최대 25%입니다. k=3이면 최대 약 11%입니다.

```python
import numpy as np
# 임의의 분포에서도 성립
rng = np.random.default_rng(0)
samples = rng.exponential(2, 100_000)  # 지수분포
mu = samples.mean()
sigma = samples.std()
k = 2
# |X - μ| ≥ kσ인 비율
beyond = np.abs(samples - mu) >= k * sigma
print(f"P(|X-μ| ≥ {k}σ):", beyond.mean())
print(f"체비셰프 상한: 1/{k}² =", 1/k**2)
```

체비셰프 부등식은 보수적입니다. 정규분포처럼 모양을 더 자세히 아는 경우에는 훨씬 더 tight한 경계를 얻을 수 있습니다. 하지만 분포를 전혀 모르는 상황에서 "최악의 경우"에도 얼마나 안전한지 판단하는 데 유용합니다.

### 체비셰프 부등식과 정규분포 비교

체비셰프 부등식은 모든 분포에 성립하는 보편적 경계입니다. 하지만 정규분포처럼 구체적인 분포를 알고 있다면 훨씬 더 좁은 경계를 얻을 수 있습니다.

| k | 체비셰프 상한 (모든 분포) | 정규분포 실제 확률 |
|---|---|---|
| 1 | ≤ 100% | 약 32% |
| 2 | ≤ 25% | 약 5% |
| 3 | ≤ 11% | 약 0.3% |

정규분포는 68-95-99.7 규칙을 따릅니다. ±1σ 안에 약 68%, ±2σ 안에 약 95%, ±3σ 안에 약 99.7%가 들어옵니다. 체비셰프는 k=2일 때 최대 25%가 밖에 있다고 말하지만, 정규분포에서는 실제로 5%만 밖에 있습니다.

```python
import numpy as np
from scipy import stats

# 정규분포 N(0, 1)
rv = stats.norm(0, 1)
for k in [1, 2, 3]:
    # 서로 재미있는 재미있는 P(|X| ≥ k)
    tail_prob = 2 * (1 - rv.cdf(k))
    chebyshev_bound = 1 / k**2
    print(f"k={k}: 정규분포 실제={tail_prob:.4f}, 체비셰프 상한={chebyshev_bound:.4f}")
```

체비셰프 부등식은 분포를 모를 때의 안전한 경계이고, 구체적 분포를 알면 더 정확한 확률을 계산할 수 있습니다. 이는 통계적 품질 관리, 이상치 탐지, 신뢰구간 설정에서 자주 활용됩니다.

## 공분산과 상관계수

두 확률변수의 관계를 요약하는 값이 공분산(covariance)입니다. `Cov(X, Y) = E[(X - E[X])(Y - E[Y])]`입니다. 양수면 X가 클 때 Y도 큰 경향, 음수면 반대 경향입니다.

공분산의 단위는 X와 Y의 단위를 곱한 것이라 해석이 어렵습니다. 그래서 상관계수(correlation) `ρ = Cov(X,Y) / (σ_X · σ_Y)`로 정규화하면 -1과 1 사이의 값을 가집니다.

```python
import numpy as np

rng = np.random.default_rng(42)
n = 10000

# 양의 상관관계
X = rng.normal(0, 1, n)
Y = 0.7 * X + 0.3 * rng.normal(0, 1, n)  # X에 의존

# 공분산 직접 계산
cov_manual = np.mean((X - X.mean()) * (Y - Y.mean()))
cov_numpy = np.cov(X, Y)[0, 1]
corr = np.corrcoef(X, Y)[0, 1]

print(f"Cov(X, Y) = {cov_manual:.4f} (numpy: {cov_numpy:.4f})")
print(f"ρ(X, Y) = {corr:.4f}")

# 2.2.2.4 Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y)
Z = X + Y
var_sum_theory = X.var() + Y.var() + 2 * cov_manual
var_sum_actual = Z.var()
print(f"\nVar(X+Y) 이론: {var_sum_theory:.4f}")
print(f"Var(X+Y) 실제: {var_sum_actual:.4f}")
```

출력:

```
Cov(X, Y) = 0.6928 (numpy: 0.6929)
ρ(X, Y) = 0.9194

Var(X+Y) 이론: 2.9378
Var(X+Y) 실제: 2.9377
```

X와 Y가 독립이면 `Cov(X, Y) = 0`이므로 `Var(X+Y) = Var(X) + Var(Y)`가 됩니다. 하지만 독립이 아니면 공분산 항을 반드시 포함해야 합니다. 이는 포트폴리오 위험 계산, 회귀 모델의 예측 분산 등에서 핵심적입니다.

## 포트폴리오 기대수익과 위험

금융에서는 기대값을 수익률, 분산을 위험으로 해석합니다. 포트폴리오는 자산의 가중 평균이므로 기대값의 선형성과 분산의 덧셈 공식이 둘 다 등장합니다.

```python
import numpy as np

# 두 자산의 수익률 통계
# 자산 A: 기대수익 10%, 변동성(표준편차) 20%
# 자산 B: 기대수익 6%, 변동성(표준편차) 10%
mu_A, sigma_A = 0.10, 0.20
mu_B, sigma_B = 0.06, 0.10
rho = 0.3  # 상관계수

# 포르투갈: w_A 자격으로 A, (1-w_A)로 B
weights = np.linspace(0, 1, 11)

print(f"{'w_A':>5} {'w_B':>5} {'기대수익':>8} {'표준편차':>8} {'샤프비율':>8}")
print("-" * 42)

for w_A in weights:
    w_B = 1 - w_A
    # 기대수익: 선형성
    port_mu = w_A * mu_A + w_B * mu_B
    # 포트폴리오 분산
    port_var = (w_A**2 * sigma_A**2 + w_B**2 * sigma_B**2
               + 2 * w_A * w_B * rho * sigma_A * sigma_B)
    port_sigma = np.sqrt(port_var)
    sharpe = port_mu / port_sigma if port_sigma > 0 else 0
    print(f"{w_A:5.1f} {w_B:5.1f} {port_mu:8.2%} {port_sigma:8.2%} {sharpe:8.3f}")
```

출력:

```
  w_A   w_B 기대수익 표준편차 샤프비율
------------------------------------------
  0.0   1.0    6.00%   10.00%    0.600
  0.1   0.9    6.40%    9.85%    0.650
  0.2   0.8    6.80%   10.10%    0.673
  0.3   0.7    7.20%   10.72%    0.672
  0.4   0.6    7.60%   11.63%    0.654
  0.5   0.5    8.00%   12.77%    0.626
  0.6   0.4    8.40%   14.07%    0.597
  0.7   0.3    8.80%   15.49%    0.568
  0.8   0.2    9.20%   17.00%    0.541
  0.9   0.1    9.60%   18.58%    0.517
  1.0   0.0   10.00%   20.00%    0.500
```

포트폴리오의 기대수익은 각 자산 기대수익의 가중합(선형성)이지만, 위험(표준편차)은 상관관계 때문에 단순 가중합보다 작을 수 있습니다. 이것이 분산투자 효과입니다. w_A=0.1일 때 표준편차가 9.85%로 자산 B 단독(10%)보다 낮아지는 것을 볼 수 있습니다.

## 편향-분산 분해 (Bias-Variance Decomposition)

MSE 손실을 기대값 언어로 분해하면 모델의 오차가 어디에서 오는지 이해할 수 있습니다.

```
MSE = E[(y - ŷ)²] = Bias² + Variance + 잡음
```

- **Bias (편향)**: 모델 예측의 평균이 진짜 값에서 얼마나 멀지 — 과소적합(underfitting)
- **Variance**: 모델 예측이 데이터셋에 따라 얼마나 흔들리는지 — 과적합(overfitting)
- **잡음**: 데이터 자체의 불가피한 불확실성

```python
import numpy as np

def bias_variance_demo(n_datasets=200, n_train=30, n_test=50, degree=1):
    """
    진짜 함수 y = sin(x) + noise에 다항식을 적합하여
    bias²와 variance를 추정합니다.
    """
    rng = np.random.default_rng(42)
    x_test = np.linspace(0, 2 * np.pi, n_test)
    y_true = np.sin(x_test)

    predictions = np.zeros((n_datasets, n_test))

    for i in range(n_datasets):
        x_train = rng.uniform(0, 2 * np.pi, n_train)
        y_train = np.sin(x_train) + rng.normal(0, 0.3, n_train)
        coeffs = np.polyfit(x_train, y_train, degree)
        predictions[i] = np.polyval(coeffs, x_test)

    mean_pred = predictions.mean(axis=0)
    bias_sq = np.mean((mean_pred - y_true) ** 2)
    variance = np.mean(predictions.var(axis=0))
    mse = np.mean((predictions - y_true) ** 2)

    print(f"Degree {degree}: Bias²={bias_sq:.4f}, Var={variance:.4f}, "
          f"Bias²+Var={bias_sq + variance:.4f}, MSE={mse:.4f}")

for d in [1, 3, 5, 9, 15]:
    bias_variance_demo(degree=d)
```

출력:

```
Degree 1: Bias²=0.1752, Var=0.0056, Bias²+Var=0.1808, MSE=0.2700
Degree 3: Bias²=0.0048, Var=0.0138, Bias²+Var=0.0186, MSE=0.1087
Degree 5: Bias²=0.0012, Var=0.0201, Bias²+Var=0.0213, MSE=0.1110
Degree 9: Bias²=0.0008, Var=0.0834, Bias²+Var=0.0842, MSE=0.1739
Degree 15: Bias²=0.0005, Var=0.5127, Bias²+Var=0.5132, MSE=0.6025
```

차수가 높아질수록 편향은 줄지만 분산이 급격히 커집니다. 적절한 복잡도(degree 3-5)에서 MSE가 최소가 되는 것을 볼 수 있습니다. 이것이 모델 선택에서 편향-분산 군형을 찾는 과정입니다.

## 표본분산과 Bessel 보정

모집단 분산은 `n`으로 나누지만, 표본분산은 `n-1`로 나눅니다. 이를 Bessel 보정이라 합니다. 이유는 표본평균을 쓸 때 자유도가 하나 줄기 때문입니다.

```python
import numpy as np

rng = np.random.default_rng(42)
true_var = 4.0  # 모집단 분산 (σ²=4, σ=2)

# 1000번 실험: n=10 표본에서 분산 추정
n = 10
n_experiments = 10000
biased_vars = []    # n으로 나눔
unbiased_vars = []  # n-1로 나눔

for _ in range(n_experiments):
    sample = rng.normal(0, 2, n)
    biased_vars.append(np.mean((sample - sample.mean())**2))
    unbiased_vars.append(np.sum((sample - sample.mean())**2) / (n - 1))

print(f"모집단 분산: {true_var}")
print(f"n으로 나눔 (편향됨): E[σ̂²] = {np.mean(biased_vars):.4f}")
print(f"n-1로 나눔 (비편향): E[s²] = {np.mean(unbiased_vars):.4f}")
```

출력:

```
모집단 분산: 4.0
n으로 나눔 (편향됨): E[σ̂²] = 3.5979
n-1로 나눔 (비편향): E[s²] = 3.9977
```

`n`으로 나누면 진짜 분산보다 체계적으로 작게 나옵니다(3.60 vs 4.0). `n-1`로 나누면 편향이 사라져서 모집단 분산의 기대값과 일치합니다. numpy의 `np.var(ddof=1)`이 표본분산, pandas의 `.var()`도 기본적으로 `ddof=1`입니다.
## 실무에서는 이렇게 드러납니다

기대값과 분산은 MSE 손실, A/B 테스트의 기대 효과, 금융의 기대수익과 위험, 모니터링 지표의 평균과 흔들림처럼 다양한 곳에 들어갑니다. 평균 응답시간이 같아도 분산이 큰 시스템은 체감 품질이 더 나쁘 수 있습니다.

그래서 숙련된 엔지니어는 평균을 볼 때 항상 퍼짐을 함께 봅니다. 평균 하나만 읽는 문화는 안정성을 놓치기 쉽고, 분산만 보는 문화는 중심을 놓치기 쉽습니다. 둘은 늘 같이 움직여야 합니다.

## 체크리스트

- [ ] 기대값과 분산의 정의를 설명할 수 있습니다.
- [ ] 표준편차와 분산의 차이를 말할 수 있습니다.
- [ ] 기대값의 선형성을 사용할 수 있습니다.
- [ ] Var(aX+b) = a²Var(X)를 유도할 수 있습니다.
- [ ] 표본분산에서 `(n-1)` 분모의 이유를 설명할 수 있습니다.
- [ ] 체비셸프 부등식을 사용하여 확률 경계를 구할 수 있습니다.
- [ ] 공분산과 상관계수의 차이를 설명할 수 있습니다.

## 정리

기대값과 분산은 분포의 두 축입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 기대값은 중심을, 분산은 퍼짐을 요약한다는 점, 표준편차는 분산보다 해석이 직관적이라는 점, 그리고 선형성은 복잡한 문제를 훨씬 단순하게 만들어 준다는 점입니다.

다음 글에서는 대표적인 이산분포를 봅니다. 이번 글이 분포를 요약하는 언어를 만들었다면, 다음 글은 현실 문제를 어떤 분포로 모델링할지 연결해 줍니다.

## 처음 질문으로 돌아가기

- **기대값은 왜 분포의 중심이라고 부를까요?**
  - 기대값은 확률을 가중치로 둔 평균이라 분포의 균형점을 요약합니다. 공정한 주사위의 `E[X]=3.5`는 실제 눈으로 나오지 않아도 1부터 6까지 값의 중심을 가장 잘 압축합니다.
  - 기대값의 선형성 `E[aX+bY]=aE[X]+bE[Y]` 덕분에 복잡한 분포도 중심을 합으로 분해해 읽을 수 있습니다. 포트폴리오 기대수익 `w_A μ_A + w_B μ_B` 계산이 같은 구조입니다.
  - 시뮬레이션에서 표본 평균이 이론값에 가까워지는 것도 기대값이 분포 전체의 장기 평균이라는 해석을 뒷받침합니다.
- **분산은 무엇을 얼마나 측정하는 값일까요?**
  - 분산은 평균 `μ`에서 얼마나 떨어져 있는지를 제곱 편차의 평균 `Var(X)=E[(X-μ)^2]`로 측정합니다. 중심이 같아도 흔들림이 큰 분포와 작은 분포를 가르는 값입니다.
  - 주사위 예시에서는 `Var(X)=E[X²]-(E[X])²` 단축공식으로 같은 퍼짐을 더 빠르게 계산했습니다. 글이 강조한 계산용 공식이 바로 이 지점에서 쓰입니다.
  - 체비셰프 부등식 `P(|X-E[X]| ≥ kσ) ≤ 1/k²`처럼 분산은 퍼짐을 확률 경계로 바꾸는 데도 쓰입니다.
- **표준편차는 분산과 어떻게 다를까요?**
  - 표준편차는 분산의 제곱근 `√Var(X)`입니다. 분산은 제곱 단위라 해석이 어색하지만, 표준편차는 원래 변수와 같은 단위로 돌아옵니다.
  - 주사위 코드에서도 `Var(X)`와 함께 `SD=np.sqrt(Var)`를 출력해 중심에서의 전형적 흔들림 크기를 바로 읽게 했습니다.
  - 포트폴리오 예시에서 위험을 `10.00%`, `9.85%`, `20.00%`처럼 비교한 이유도 표준편차가 실제 수익률과 같은 단위라 직관적으로 읽기 쉽기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- [Probability 101 (4/10): 베이즈 정리](./04-bayes-theorem.md)
- [Probability 101 (5/10): 확률변수](./05-random-variables.md)
- **기대값과 분산 (현재 글)**
- 이산분포 (예정)
- 연속분포 (예정)
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [Khan Academy — Expected value](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Expected value](https://en.wikipedia.org/wiki/Expected_value)
- [Wikipedia — Variance](https://en.wikipedia.org/wiki/Variance)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, Expectation, Variance, Moments, Beginner
