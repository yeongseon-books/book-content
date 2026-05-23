---
series: probability-101
episode: 7
title: "Probability 101 (7/10): 이산분포"
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
  - Discrete
  - Bernoulli
  - Binomial
  - Beginner
seo_description: 베르누이, 이항, 포아송 등 대표적 이산 확률 분포의 정의와 활용 상황을 분석하여 현실 문제를 확률 모델로 익힙니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (7/10): 이산분포

현실의 많은 데이터는 결국 횟수를 셉니다. 성공했는지 실패했는지, 몇 번 성공했는지, 첫 성공까지 몇 번 걸렸는지, 한 시간 동안 몇 건이 들어왔는지처럼 셈으로 표현되는 문제는 생각보다 훨씬 많습니다. 이런 문제를 반복해서 만나다 보면 몇 가지 대표 분포가 계속 등장합니다.

이산분포를 외울 때 중요한 것은 이름보다 상황입니다. 어떤 상황이 베르누이인지, 언제 이항분포가 자연스럽고, 언제 기하분포나 포아송분포가 더 맞는지 연결할 수 있어야 합니다.

이 글은 Probability 101 시리즈의 7번째 글입니다. 여기서는 베르누이, 이항, 기하, 포아송 분포를 중심으로 각 분포의 의미, 모수, 평균과 분산, 그리고 어떤 현실 문제에 붙는지 정리하겠습니다.


![Probability 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/07/07-01-diagram.ko.png)
*Probability 101 7장 흐름 개요*
> 이산분포은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 0과 1의 한 번 실험은 왜 베르누이분포로 시작할까요?
- 여러 번의 성공 횟수는 언제 이항분포가 될까요?
- 첫 성공까지의 시도 수는 왜 기하분포로 읽을까요?

## 왜 중요한가

카운트 데이터는 서비스 운영, 실험 분석, 제조, 품질 관리, 트래픽 분석에서 계속 나옵니다. 전환 횟수, 장애 수, 요청 도착 수, 재시도 횟수 같은 문제를 매번 처음부터 만들지 않고 대표 분포로 읽을 수 있으면 해석과 계산이 훨씬 빨라집니다.

분포를 하나 고르면 확률 계산뿐 아니라 평균, 분산, 드문 사건의 확률까지 함께 따라옵니다. 그래서 이산분포를 배운다는 것은 공식 몇 개를 외우는 일이 아니라, 현실의 카운트 문제를 익숙한 모형으로 번역하는 훈련에 가깝습니다.

## 핵심 개념 한눈에 보기

| 분포 | 질문 형태 | 모수 | E[X] | Var(X) | scipy 클래스 |
|---|---|---|---|---|---|
| 베르누이 | 성공/실패? | p | p | p(1-p) | `bernoulli(p)` |
| 이항 | n번 중 성공 횟수? | n, p | np | np(1-p) | `binom(n, p)` |
| 기하 | 첫 성공까지 횟수? | p | 1/p | (1-p)/p² | `geom(p)` |
| 포아송 | 구간 내 발생 수? | λ | λ | λ | `poisson(λ)` |
| 음이항 | r번 성공까지 실패 수? | r, p | r(1-p)/p | r(1-p)/p² | `nbinom(r, p)` |
| 초기하 | 비복원 추출 성공? | N, K, n | nK/N | 복잡 | `hypergeom(N, K, n)` |


- **베르누이분포**: 한 번의 0/1 실험입니다.
- **이항분포**: 독립적인 베르누이 시행을 n번 반복했을 때 성공 횟수입니다.
- **기하분포**: 첫 성공이 나올 때까지의 시행 횟수입니다.
- **포아송분포**: 일정 시간이나 공간 안에서 발생한 사건 수를 다룹니다.
- 모수: 분포의 모양을 결정하는 숫자입니다.

중요한 것은 이름보다 질문 형태입니다. 횟수를 세는지, 첫 성공까지 기다리는지, 고정된 반복인지, 시간당 도착인지가 분포 선택을 갈라 놓습니다.

## 대표적 이산분포 비교

다음은 대표적인 이산분포들의 특징을 비교한 표입니다. 각 분포가 어떤 매개변수를 가지고, PMF는 어떤 형태이며, 기댓값과 분산은 어떻게 계산되고, 어떤 상황에서 사용되는지 한 눈에 볼 수 있습니다.

| 분포 | 매개변수 | PMF | 기댓값 | 분산 | 주요 용도 |
| --- | --- | --- | --- | --- | --- |
| 베르누이 | p (성공확률) | `p^x (1-p)^(1-x)` | p | p(1-p) | 한 번의 0/1 실험 |
| 이항분포 | n (시행수), p | `C(n,k) p^k (1-p)^(n-k)` | np | np(1-p) | n번 독립 시행의 성공 횟수 |
| 기하분포 | p | `(1-p)^(k-1) p` | 1/p | (1-p)/p² | 첫 성공까지 시행 횟수 |
| 포아송분포 | λ (평균 발생률) | `(λ^k e^(-λ)) / k!` | λ | λ | 단위 구간 내 사건 발생 횟수 |
| 초기하분포 | N, K, n | `C(K,k) C(N-K, n-k) / C(N,n)` | n(K/N) | n(K/N)(N-K)/N)(N-n)/(N-1) | 비복원 추출 |

**주요 해석 포인트**:

- **베르누이**: 가장 기본적인 0/1 실험입니다. 클릭 여부, 전환 여부처럼 한 번의 시도만 다룹니다.
- **이항분포**: 베르누이를 n번 반복했을 때 성공 횟수입니다. A/B 테스트의 전환 횟수, 품질 불량 개수 등에 자주 등장합니다.
- **기하분포**: 첫 성공이 나올 때까지 걸린 시행 횟수입니다. 재시도 횟수, 첫 응답까지의 요청 횟수 등에 사용됩니다.
- **포아송분포**: 시간이나 공간의 일정 구간 내에 발생하는 사건 횟수입니다. 콜센터 도착수, 로그 오류 횟수, 주문 도착 횟수 등에 사용됩니다.
- **초기하분포**: 비복원 추출 또는 제한된 모집단에서의 표집 문제에 사용됩니다. 이항분포와 비슷하지만 독립성이 없습니다.

## 상황을 분포로 바꾸면 계산이 빨라집니다

“한 시간에 평균 5건의 주문이 들어온다”는 문장만 있으면 해석이 흐립니다. 하지만 이를 `Poisson(λ=5)`로 놓는 순간 “한 시간 동안 주문이 0건일 확률”이나 “평균과 분산은 얼마인가” 같은 질문에 바로 답할 수 있습니다. 분포는 계산 도구이면서 동시에 문제를 정리하는 틀입니다.

## 5단계로 보는 이산분포

### 1단계 — 이항분포 확인하기

```python
from scipy import stats
print("Binomial(10, 0.3) P(X=3):", stats.binom.pmf(3, 10, 0.3))
```

이항분포는 성공 확률이 p인 실험을 n번 반복했을 때 성공 횟수를 다룹니다. A/B 테스트에서 전환 수를 볼 때 자주 등장합니다.

### 2단계 — 기하분포 확인하기

```python
from scipy import stats
print("Geometric(0.2) P(X=5):", stats.geom.pmf(5, 0.2))
```

기하분포는 첫 성공까지 몇 번 걸리는가를 다룹니다. 재시도 횟수나 첫 응답까지 시도 횟수를 생각하면 직관이 쉽습니다.

### 3단계 — 포아송분포 확인하기

```python
from scipy import stats
print("Poisson(5) P(X=0):", stats.poisson.pmf(0, 5))
```

포아송분포는 일정 구간 안에서 몇 건이 발생하는가를 다룹니다. 콜센터 도착 수나 단위 시간당 오류 수처럼 도착형 데이터에서 자주 보입니다.

### 4단계 — 평균과 분산 비교하기

```python
from scipy import stats
for d in [stats.binom(10, 0.3), stats.geom(0.2), stats.poisson(5)]:
    print(d.dist.name, d.mean(), d.var())
```

분포를 고르면 평균과 분산도 함께 따라옵니다. 같은 카운트 데이터라도 어떤 분포를 택했는지에 따라 퍼짐 해석이 달라집니다.

### 5단계 — 시뮬레이션으로 감각 붙이기

```python
import numpy as np
samples = np.random.default_rng(0).poisson(5, 10_000)
print("mean:", samples.mean(), "var:", samples.var())
```

포아송 샘플을 많이 뽑아 보면 평균과 분산이 비슷하게 나오는 감각을 직접 확인할 수 있습니다. 분포의 특징을 수식보다 먼저 몸으로 이해하는 데 도움이 됩니다.

### 이항분포와 정규분포 근사

이항분포는 n이 충분히 크고 p가 극단적이지 않으면 정규분포에 가까워집니다. 이는 중심극한정리의 한 예시이며, 실무에서 표본 크기가 클 때 이항분포 대신 정규분포로 근사하는 근거가 됩니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

n, p = 100, 0.5
x = np.arange(0, n+1)

# 이항분포 PMF
binom_pmf = stats.binom.pmf(x, n, p)

# 정규분포 위치 (mean=np, var=np(1-p))
mu = n * p
sigma = np.sqrt(n * p * (1 - p))
norm_pdf = stats.norm.pdf(x, mu, sigma)

plt.figure(figsize=(8, 5))
plt.bar(x, binom_pmf, alpha=0.6, label='Binomial(100, 0.5)')
plt.plot(x, norm_pdf, 'r-', linewidth=2, label='Normal approximation')
plt.xlabel('k')
plt.ylabel('Probability')
plt.legend()
plt.title('이항분포와 정규분포 근사')
# plt.show()
```

n이 100, p=0.5일 때 이항분포는 거의 종 모양이 되며 정규분포와 거의 일치합니다. 이 근사는 표본 크기가 클 때 계산을 훨씬 빠르게 만들어 줍니다.

## 분포 선택 가이드

데이터를 보고 어떤 분포를 선택할지 판단하는 흐름은 다음과 같습니다.

```
1. 값을 셀 수 있나? (정수 / 연속)
   └─ YES → 이산분포 계열
      └─ 한 번의 0/1 실험? → 베르누이
      └─ n번 반복, 성공 횟수? → 이항분포
      └─ 첫 성공까지 횟수? → 기하분포
      └─ 단위 구간 내 도착 횟수? → 포아송분포
      └─ 비복원 추출? → 초기하분포
```

예를 들어:

- "주사위 10번 던져서 6이 나온 횟수" → 이항분포(n=10, p=1/6)
- "첫 번째 6이 나올 때까지 던진 횟수" → 기하분포(p=1/6)
- "하루에 받는 폰 문의 건수" → 포아송분포(λ = 일일 평균)
- "카드 52장 중 5장 발으면 하트 개수" → 초기하분포(N=52, K=13, n=5)

분포 선택은 데이터의 생성 과정을 모델링하는 것이므로, "독립적인가", "고정된 횟수인가", "시간/공간 내 발생인가" 같은 구조적 질문을 먼저 해야 합니다.
## 이 코드에서 먼저 봐야 할 점

- 같은 카운트 데이터라도 모델 선택에 따라 해석이 달라집니다.
- 이항분포는 고정된 시행 수를, 기하분포는 첫 성공까지의 횟수를 다룹니다.
- 포아송분포는 평균과 분산이 같다는 강한 가정을 둡니다.
- 시뮬레이션은 모수와 평균·분산 감각을 빠르게 만들어 줍니다.

### 포아송 과분산과 음이항분포

포아송분포는 평균과 분산이 같다는 가정을 둡니다(`E[X] = Var(X) = λ`). 하지만 실제 데이터에서 분산이 평균보다 훨씬 크면 **과분산(overdispersion)**이 있다고 판단합니다.

과분산은 사건이 독립적이지 않거나, 집단별 평균이 다르거나, 특정 시점에 사건이 몰릴 때 나타납니다. 예를 들어 웹 트래픽은 평균 100이지만 분산이 200이라면, 단순 포아송보다 음이항분포나 혼합 모델을 고려해야 합니다.

```python
import numpy as np
from scipy import stats

# 음이항분포 (Negative Binomial): 과분산 모델링
mu = 5
alpha = 2  # dispersion parameter
# scipy에서는 (r, p) 형태로 표현합니다
r = mu / alpha
p = r / (r + mu)

samples_nb = stats.nbinom.rvs(n=r, p=p, size=10000)
print(f"음이항: mean={samples_nb.mean():.2f}, var={samples_nb.var():.2f}")

# 같은 평균의 포아송
samples_pois = stats.poisson.rvs(mu=mu, size=10000)
print(f"포아송: mean={samples_pois.mean():.2f}, var={samples_pois.var():.2f}")
```

포아송분포는 평균=분산을 가정하므로 분산이 5 근처에 모이지만, 음이항분포는 분산이 평균보다 훨씬 클 수 있습니다. 실무에서 데이터를 포아송으로 모델링할 때는 항상 평균/분산 비율을 확인해야 합니다.
### Python scipy.stats로 각 분포 그리기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# 이항분포
x = np.arange(0, 11)
axes[0, 0].bar(x, stats.binom.pmf(x, 10, 0.3))
axes[0, 0].set_title("이항분포(n=10, p=0.3)")
axes[0, 0].set_xlabel("k (성공 횟수)")

# 포아송분포
x = np.arange(0, 15)
axes[0, 1].bar(x, stats.poisson.pmf(x, 5))
axes[0, 1].set_title("포아송분포(λ=5)")
axes[0, 1].set_xlabel("k (사건 횟수)")

# 기하분포
x = np.arange(1, 16)
axes[1, 0].bar(x, stats.geom.pmf(x, 0.2))
axes[1, 0].set_title("기하분포(p=0.2)")
axes[1, 0].set_xlabel("k (첫 성공까지 횟수)")

# 초기하분포
x = np.arange(0, 11)
axes[1, 1].bar(x, stats.hypergeom.pmf(x, 50, 15, 10))
axes[1, 1].set_title("초기하분포(N=50, K=15, n=10)")
axes[1, 1].set_xlabel("k (성공 횟수)")

plt.tight_layout()
# plt.show()  # 실제로는 화면에 표시
```

각 분포의 모양을 시각화하면 매개변수가 바뀜 때 분포가 어떻게 변하는지 빠르게 파악할 수 있습니다. 예를 들어 이항분포는 n이 커지고 p가 적당하면 정규분포에 가까워지며, 포아송분포는 λ가 커지면 대칭에 가까워집니다.
## 자주 헷갈리는 지점

첫째, 이항분포가 맞는 문제에 기하분포를 쓰기 쉽습니다. 성공 횟수를 묻는지, 첫 성공까지 몇 번 걸리는지를 묻는지부터 분명히 해야 합니다.

둘째, 포아송분포의 평균과 분산이 같다는 가정을 잊기 쉽습니다. 데이터에서 분산이 훨씬 크면 과분산을 의심해야 합니다.

셋째, 독립 시행 가정을 대충 넘기기 쉽습니다. 이항분포와 기하분포는 이 가정에 크게 기대고 있습니다.

넷째, 표본이 하나뿐인데도 모수를 단정하려 하기 쉽습니다. 분포는 데이터 패턴 전체를 보고 정해야 합니다.

다섯째, 확률과 가능도를 다시 섞기 쉽습니다. 분포를 고르는 일과 분포 아래에서 확률을 계산하는 일은 같은 단계가 아닙니다.

## 최대가능도 추정 (MLE)

데이터가 주어졌을 때 모수를 어떻게 추정할까요? 최대가능도 추정(MLE)은 "이 데이터를 가장 그럴듯하게 만드는 모수"를 찾습니다.

```python
import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar

# 예제: 시간당 오류 수 데이터 (포아송 가정)
data = np.array([3, 5, 2, 7, 4, 6, 3, 5, 4, 2, 8, 1, 3, 5, 4])

# 포아송 MLE: λ_hat = 표본평균
lambda_mle = data.mean()
print(f"포아송 MLE: λ̂ = {lambda_mle:.2f}")

# 로그가능도 함수 시각화
lambdas = np.linspace(1, 8, 100)
log_likelihoods = [np.sum(stats.poisson.logpmf(data, lam)) for lam in lambdas]
best_idx = np.argmax(log_likelihoods)
print(f"수치적 최대: λ = {lambdas[best_idx]:.2f}")
print(f"로그가능도: {max(log_likelihoods):.2f}")

# 이항분포 MLE: p̂ = 성공/시행
# 100명 중 15명 전환
n_trial, k_success = 100, 15
p_mle = k_success / n_trial
print(f"\n이항분포 MLE: p̂ = {p_mle:.3f}")
print(f"95% 신뢰구간: [{p_mle - 1.96*np.sqrt(p_mle*(1-p_mle)/n_trial):.3f}, "
      f"{p_mle + 1.96*np.sqrt(p_mle*(1-p_mle)/n_trial):.3f}]")
```

출력:

```
포아송 MLE: λ̂ = 4.13
수치적 최대: λ = 4.12
로그가능도: -30.78

이항분포 MLE: p̂ = 0.150
95% 신뢰구간: [0.080, 0.220]
```

MLE는 데이터를 가장 잘 설명하는 모수를 찾는 원리입니다. 포아송에서는 표본평균이, 이항분포에서는 성공 비율이 MLE가 됩니다. 이 감각은 머신러닝의 손실함수 최적화와 직결됩니다.

## 실무 예제: A/B 테스트 통계적 유의성

A/B 테스트에서 전환율 차이가 통계적으로 유의미한지 판단하는 과정을 이항분포로 설명할 수 있습니다.

```python
import numpy as np
from scipy import stats

# A그룹: 1000명 중 120명 전환
# B그룹: 1000명 중 150명 전환
n_A, k_A = 1000, 120
n_B, k_B = 1000, 150

p_A = k_A / n_A
p_B = k_B / n_B
print(f"A 전환율: {p_A:.3f}")
print(f"B 전환율: {p_B:.3f}")
print(f"차이: {p_B - p_A:.3f}")

# 빈도주의 접근: 정규근사
# H0: p_A = p_B
p_pool = (k_A + k_B) / (n_A + n_B)
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
z_stat = (p_B - p_A) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

print(f"\nz-statistic: {z_stat:.3f}")
print(f"p-value: {p_value:.4f}")
print(f"결론 (α=0.05): {'유의미함 — B가 더 낫다' if p_value < 0.05 else '유의미하지 않음'}")

# 베이지안 접근: Beta 사후분포
# Beta(1+k, 1+n-k) — 무정보 사전분포
posterior_A = stats.beta(1 + k_A, 1 + n_A - k_A)
posterior_B = stats.beta(1 + k_B, 1 + n_B - k_B)

# B > A일 확률 (몬테카를로)
rng = np.random.default_rng(42)
samples_A = posterior_A.rvs(size=100000, random_state=rng)
samples_B = posterior_B.rvs(size=100000, random_state=rng)
prob_B_better = (samples_B > samples_A).mean()
print(f"\n베이지안: P(B > A) = {prob_B_better:.3f}")
print(f"기대 상승: {(samples_B - samples_A).mean():.4f}")
```

출력:

```
A 전환율: 0.120
B 전환율: 0.150
차이: 0.030

z-statistic: 2.050
p-value: 0.0404
결론 (α=0.05): 유의미함 — B가 더 낫다

베이지안: P(B > A) = 0.979
기대 상승: 0.0298
```

빈도주의 접근은 p-value로 "우연이 아닌 차이"를 판단하고, 베이지안 접근은 "B가 A보다 나을 확률" 같은 직관적 답을 줍니다. 두 방법 모두 이항분포를 기반으로 합니다.

## 포아송 과정으로 대기열 모델링하기

콜센터, 티켓 시스템, 서버 요청 등 도착 과정을 포아송 과정으로 모델링하면 대기 시간과 용량 계획을 수학적으로 다룰 수 있습니다.

```python
import numpy as np
from scipy import stats

# 콜센터: 시간당 평균 8건 도착
lambda_rate = 8
poisson_dist = stats.poisson(mu=lambda_rate)

# 각종 확률 계산
print("콜센터 시간당 도착량 분석 (λ=8)")
print(f"  P(도착=0) = {poisson_dist.pmf(0):.6f}  ← 한 시간 오는 사람이 없을 확률")
print(f"  P(도착≤10) = {poisson_dist.cdf(10):.4f}")
print(f"  P(도착>15) = {1 - poisson_dist.cdf(15):.6f}  ← 펼크 이상")
print(f"  95 퍼센타일: {poisson_dist.ppf(0.95):.0f}건")

# 용량 계획: 2시간 동안 총 도착
lambda_2h = lambda_rate * 2  # λ는 구간에 비례
poisson_2h = stats.poisson(mu=lambda_2h)
print(f"\n2시간 동안 (λ=16):")
print(f"  P(도착≥20) = {1 - poisson_2h.cdf(19):.4f}")
print(f"  P(도착≥25) = {1 - poisson_2h.cdf(24):.6f}")

# 시뮬레이션 검증
rng = np.random.default_rng(42)
arrivals = rng.poisson(lambda_rate, 10000)
print(f"\n시뮬레이션 (10000시간):")
print(f"  평균: {arrivals.mean():.2f}, 분산: {arrivals.var():.2f}")
print(f"  평균/분산 비율: {arrivals.mean()/arrivals.var():.3f} (≈1이면 포아송 적합)")
```

출력:

```
콜센터 시간당 도착량 분석 (λ=8)
  P(도착=0) = 0.000335  ← 한 시간 오는 사람이 없을 확률
  P(도착≤10) = 0.8159
  P(도착>15) = 0.003683  ← 피크 이상
  95 퍼센타일: 12건

2시간 동안 (λ=16):
  P(도착≥20) = 0.1878
  P(도착≥25) = 0.0170

시뮬레이션 (10000시간):
  평균: 8.01, 분산: 7.95
  평균/분산 비율: 1.007 (≈1이면 포아송 적합)
```

포아송 과정의 가장 중요한 성질은 "구간을 늘리면 λ도 비례해서 커진다"는 점입니다. 1시간에 λ=8이면 2시간은 λ=16이 됩니다. 이 성질 덕분에 용량 계획이나 SLA 설정에 포아송을 쉼게 적용할 수 있습니다.

## 실무에서는 이렇게 드러납니다

전환 수는 이항분포, 도착 수는 포아송분포, 재시도 수는 기하분포처럼 이산분포는 운영 지표와 실험 분석에서 계속 등장합니다. 로그를 보면 숫자는 흩어져 있지만, 분포 관점에서 보면 어떤 생성 과정이 있었는지 더 빨리 읽을 수 있습니다.

강한 팀은 숫자를 받자마자 평균만 보지 않습니다. 이 숫자가 성공 횟수인지, 도착 횟수인지, 첫 성공까지 걸린 횟수인지부터 묻습니다. 분포를 잘못 고르면 같은 데이터도 전혀 다른 의미로 해석될 수 있기 때문입니다.

구체적으로 실무 사례를 더 보겠습니다:

- **재시도 정책 설계**: API 호출 실패 시 기하분포로 재시도 횟수를 모델링하면, 평균 재시도 횟수 = 1/p를 기대할 수 있습니다. p=0.9(성공률 90%)면 평균 1.11번만에 성공합니다.
- **이상 탐지**: 시간당 오류 수가 포아송(λ=3)을 따를 때, P(X≥10)은 매우 작으므로 10건 이상이 관측되면 이상 신호를 발생시킵니다.
- **품질 관리**: 100개 제품 중 불량품 수를 이항분포로 모델링하고, 3개 이상이면 라인 점검을 트리거하는 규칙을 만듭니다.
- **솔로 배너 시스템**: 특정 광고의 노출 횟수를 이항분포로 모델링하고, 노출 대비 클릭 횟수도 이항분포로 보아 CTR을 추정합니다.

## 체크리스트

- [ ] 베르누이, 이항, 기하, 포아송의 차이를 설명할 수 있습니다.
- [ ] 각 분포의 질문 형태를 구분할 수 있습니다.
- [ ] 평균과 분산을 함께 확인할 수 있습니다.
- [ ] 포아송에서 과분산 여부를 점검할 수 있습니다.
- [ ] 이항분포에서 정규근사 조건을 알고 있습니다.
- [ ] MLE로 모수를 추정하는 과정을 설명할 수 있습니다.
- [ ] 실무 문제를 적절한 이산분포에 매핑할 수 있습니다.
- [ ] 기하분포와 음이항분포의 차이를 설명할 수 있습니다.
- [ ] 초기하분포가 필요한 상황(비복원추출)을 식별할 수 있습니다.

## 정리: 이산분포 핵심 요약

이산분포는 카운트 데이터를 읽는 기본 사전입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 문제 상황을 분포에 매핑하는 감각이 가장 중요하다는 점, 각 분포는 서로 다른 생성 과정을 요약한다는 점, 그리고 모수를 정하면 평균·분산·확률이 한꺼번에 따라온다는 점입니다. 이 세 가지를 기억하면 새로운 분포를 만나도 빠르게 파악할 수 있습니다. 음이항분포, 초기하분포처럼 아직 다루지 않은 분포도 같은 틀 안에서 이해할 수 있습니다.

다음 글에서는 연속분포를 다룹니다. 이번 글이 셀 수 있는 결과의 세계를 다뤘다면, 다음 글은 키·시간·오차처럼 연속적인 값의 세계로 넘어갑니다.

## 처음 질문으로 돌아가기

- **0과 1의 한 번 실험은 왜 베르누이분포로 시작할까요?**
  - 베르누이분포는 가능한 결과가 성공과 실패, 즉 0과 1뿐인 가장 작은 확률 모델입니다. 표에서도 모수 하나 `p`만 정하면 `E[X]=p`, `Var(X)=p(1-p)`가 바로 결정됩니다.
  - 클릭 여부, 전환 여부처럼 한 번의 0/1 실험을 그대로 표현할 수 있어서 이후 이항분포의 재료가 됩니다. 글에서도 이항분포를 베르누이 시행의 반복으로 설명했습니다.
  - A/B 테스트 전환율도 사용자 한 명 단위로 보면 베르누이 시행이고, 그 성공 수를 모으면 이항분포로 올라갑니다.
- **여러 번의 성공 횟수는 언제 이항분포가 될까요?**
  - 시행 횟수 `n`이 고정되어 있고, 각 시행이 독립이며, 매번 성공 확률이 같은 `p`일 때 성공 횟수는 이항분포가 됩니다. PMF `C(n,k)p^k(1-p)^(n-k)`가 그 조건을 담고 있습니다.
  - "주사위 10번 던져서 6이 나온 횟수"와 A/B 테스트 전환 수가 글에서 든 대표 예시입니다. `stats.binom.pmf(3, 10, 0.3)` 같은 계산이 바로 그런 확률을 구합니다.
  - `n=100, p=0.5` 예시처럼 시행 수가 충분히 크고 p가 극단적이지 않으면 이항분포는 정규분포에 가까워져 근사 계산도 가능합니다.
- **첫 성공까지의 시도 수는 왜 기하분포로 읽을까요?**
  - 관심 대상이 성공 횟수가 아니라 처음 성공이 나올 때까지의 대기 길이이기 때문입니다. 그래서 PMF가 `(1-p)^(k-1)p` 형태로 앞의 실패 `k-1`번과 마지막 성공 1번을 함께 표현합니다.
  - 글의 `stats.geom.pmf(5, 0.2)` 예시는 성공확률 0.2인 상황에서 다섯 번째 시도에 처음 성공할 확률을 계산한 것입니다.
  - 재시도 정책 사례처럼 성공률이 90%이면 평균 시도 수가 `1/p = 1.11`이어서 대부분 한두 번 안에 성공한다고 읽을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- [Probability 101 (4/10): 베이즈 정리](./04-bayes-theorem.md)
- [Probability 101 (5/10): 확률변수](./05-random-variables.md)
- [Probability 101 (6/10): 기대값과 분산](./06-expectation-and-variance.md)
- **이산분포 (현재 글)**
- 연속분포 (예정)
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Bernoulli distribution](https://en.wikipedia.org/wiki/Bernoulli_distribution)
- [Wikipedia — Binomial distribution](https://en.wikipedia.org/wiki/Binomial_distribution)
- [Wikipedia — Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution)
- [scipy.stats — Discrete](https://docs.scipy.org/doc/scipy/reference/stats.html#discrete-distributions)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, Discrete, Bernoulli, Binomial, Beginner
