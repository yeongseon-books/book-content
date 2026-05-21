---
series: probability-101
episode: 9
title: "Probability 101 (9/10): 대수의 법칙과 중심극한정리"
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
  - LLN
  - CLT
  - Sampling
  - Beginner
seo_description: 표본 크기에 따른 평균 수렴의 대수의 법칙과 임의 분포가 정규분포로 수렴하는 중심극한정리의 중요성을 파악합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (9/10): 대수의 법칙과 중심극한정리

통계와 머신러닝에서 평균은 지나치게 자주 등장합니다. 평균 응답시간, 평균 손실, 평균 전환율처럼 많은 지표가 평균으로 요약됩니다. 그런데 왜 평균을 믿어도 되는지, 왜 표본평균이 점점 안정되는지, 왜 평균의 분포가 정규분포에 가까워지는지는 별도로 이해해야 합니다.

대수의 법칙과 중심극한정리는 이 질문에 답하는 두 기둥입니다. 하나는 평균이 어디로 수렴하는지, 다른 하나는 그 오차가 어떤 모양을 가지는지 설명합니다.

이 글은 Probability 101 시리즈의 9번째 글입니다. 여기서는 대수의 법칙과 중심극한정리의 직관, 표준오차, 비정규 모집단에서도 평균이 왜 정규에 가까워지는지 코드와 함께 정리하겠습니다.

## 먼저 던지는 질문

- 표본평균은 왜 표본 수가 커질수록 안정될까요?
- 대수의 법칙과 중심극한정리는 무엇이 다를까요?
- 표준오차는 표준편차와 어떻게 다를까요?

## 큰 그림

![Probability 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/09/09-01-diagram.ko.png)

*Probability 101 9장 흐름 개요*

이 그림은 이 개념의 기본 구조를 보여줍니다.

> 대수의 법칙과 중심극한정리은 구체적인 가정과 한계를 함께 봐야 합니다.

## 왜 중요한가

신뢰구간, 가설검정, A/B 테스트, 평균 지표 해석은 거의 모두 중심극한정리 위에 서 있습니다. 표본평균이 믿을 만해지는 이유는 대수의 법칙이 설명하고, 평균의 오차를 정규근사로 다룰 수 있는 이유는 중심극한정리가 설명합니다.

이 두 정리를 모르면 평균을 너무 쉽게 믿거나, 반대로 평균이 왜 중요한지도 설명하기 어렵습니다. 특히 표준오차를 표준편차와 구분하지 못하면 리포트와 운영 지표 해석이 자주 엇나갑니다.

## 핵심 개념 한눈에 보기

| 개념 | 핵심 질문 | 한 줄 답 |
| --- | --- | --- |
| 대수의 법칙 | 표본평균은 어디로? | 모평균 μ로 수렴합니다 |
| 중심극한정리 | 표본평균의 모양은? | n이 크면 정규분포에 가까워집니다 |
| 표준오차 | 표준편차와 차이는? | 평균의 흔들림이며 σ/√n입니다 |
| i.i.d. | 전제 조건은? | 독립이고 동일한 분포를 따라야 합니다 |
| n ≥ 30 | 왜 30이 기준? | 대부분 분포에서 근사가 충분히 좋아지는 경험칙 |
| 부트스트랩 | CLT 대안은? | 분포 가정 없이 재표본으로 신뢰구간 계산 |
## 핵심 용어

- **i.i.d.**: 서로 독립이고 같은 분포를 따른다는 가정입니다.
- **표본평균 `X̄`**: 표본들의 평균입니다.
- **대수의 법칙**: 표본평균이 모평균으로 수렴한다는 정리입니다.
- **중심극한정리**: 표본평균의 오차 분포가 정규분포에 가까워진다는 정리입니다.
- **표준오차**: 표본평균의 표준편차이며 보통 `σ/√n` 꼴입니다.

| 구분 | 표준편차 (SD) | 표준오차 (SE) |
| --- | --- | --- |
| 대상 | 개별 관촡값 X | 표본평균 X̄ |
| 정의 | `√Var(X)` | `σ / √n` |
| 의미 | 데이터가 평균에서 얼마나 흔들리는가 | 표본평균이 모평균에서 얼마나 흔들리는가 |
| n의 영향 | 무관 | n이 커지면 줄어듦 (1/√n) |

표준편차는 데이터 자체의 흔들림을 말하고, 표준오차는 표본평균의 흔들림을 말합니다. 둘을 혼동하면 신뢰구간 해석이 크게 엇나갑니다.

두 정리는 같은 말을 반복하지 않습니다. 하나는 목적지, 다른 하나는 오차의 모양을 말합니다.

## 평균이 믿을 만해지는 이유

“표본평균은 결국 모평균 근처로 간다”는 믿음은 대수의 법칙에서 옵니다. 하지만 얼마나 흔들리는지, 그 흔들림이 어느 정도 정규처럼 보이는지는 중심극한정리가 설명합니다. 그래서 둘은 함께 봐야 합니다.

특히 중심극한정리를 이해하면 정규분포가 왜 통계 전반에서 자주 나타나는지도 설명할 수 있습니다. 원래 모집단이 정규가 아니어도 평균은 정규에 가까워질 수 있기 때문입니다.

## 5단계로 보는 대수의 법칙과 중심극한정리

아래 5단계는 대수의 법칙의 직관적 확인에서 시작해, CLT의 시뮬레이션, 시각화, 표준오차 계산, 그리고 다양한 모집단에서의 검증으로 이어집니다.

## LLN vs CLT 비교

대수의 법칙(LLN)과 중심극한정리(CLT)는 둘 다 표본평균에 대한 이야기지만, 서로 다른 질문에 답합니다. 두 정리를 명확히 구분하는 것이 중요합니다.

| 구분 | LLN (대수의 법칙) | CLT (중심극한정리) |
| --- | --- | --- |
| 대상 | 표본평균 X̄ 그 자체 | 표본평균의 **뵘4포** |
| 결론 | X̄ → μ (n이 커지면) | (X̄ - μ) / (σ/√n) → N(0,1) |
| 물음 | "표본평균은 어디로 가는가?" | "표본평균의 흔들림은 어떻게 생겼는가?" |
| 조건 | i.i.d., 기댓값 존재 | i.i.d., 기댓값과 뵘4산 존재, n이 충뵘4히 큼 |
| 실무 응용 | 표본 수가 커지면 평균이 안정됨 | 표본평균의 확률 계산을 정규근사로 수행 |

**예시**:

- LLN: 주사위를 10,000번 던지면 평균은 3.5에 가까워집니다.
- CLT: 주사위 30개의 평균을 10,000번 따로 뽑아서 히스토그램을 그리면, 그 뵘4포는 정규뵘4포에 가까워집니다.

LLN은 "어디로 가는가"를 말하고, CLT는 "그 과정의 확률 뵘4포"를 말합니다.
### 1단계 — 대수의 법칙 시뮬레이션

```python
import numpy as np

rng = np.random.default_rng(0)
samples = rng.uniform(0, 1, 10_000)
running = np.cumsum(samples) / np.arange(1, len(samples) + 1)

# 수렴 과정 확인
checkpoints = [10, 50, 100, 500, 1000, 5000, 10000]
print("표본 수  | 표본평균  | 모평균과의 차이")
print("-" * 40)
for n in checkpoints:
    diff = abs(running[n-1] - 0.5)
    print(f"  {n:>5}  |  {running[n-1]:.5f}  |  {diff:.5f}")
```

출력:

```
표본 수  | 표본평균  | 모평균과의 차이
----------------------------------------
     10  |  0.53671  |  0.03671
     50  |  0.48237  |  0.01763
    100  |  0.49599  |  0.00401
    500  |  0.50132  |  0.00132
   1000  |  0.49923  |  0.00077
   5000  |  0.50041  |  0.00041
  10000  |  0.49975  |  0.00025
```

표본 수가 커질수록 평균이 0.5 근처로 안정되는 모습을 직접 볼 수 있습니다. 이것이 대수의 법칙의 가장 직관적인 그림입니다. 차이가 줄어드는 속도는 대략 1/√n에 비례합니다.

### 2단계 — 중심극한정리 시뮬레이션

```python
import numpy as np
rng = np.random.default_rng(0)
means = [rng.exponential(1, 30).mean() for _ in range(10_000)]
print("mean ~ 1:", np.mean(means), "std ~ 1/sqrt(30):", np.std(means))
```

원래 모집단은 지수분포처럼 비대칭이지만, 표본평균을 많이 모아 보면 그 분포가 정규에 가까워집니다. 이 장면이 중심극한정리의 핵심입니다.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)

# 지수분포(λ=1)에서 n=30 표본평균을 10,000번 반복
means = np.array([rng.exponential(1, 30).mean() for _ in range(10_000)])

# 정규성 검정
stat, p_value = stats.shapiro(means[:500])  # Shapiro-Wilk
print(f"\n정규성 검정 (Shapiro-Wilk): p={p_value:.4f}")
print(f"정규 가정 {'유지' if p_value >= 0.05 else '기각'} (α=0.05)")
print(f"표본평균 mean: {means.mean():.4f} (theory: 1.0)")
print(f"표본평균 std:  {means.std():.4f} (theory: 1/√30 = {1/30**0.5:.4f})")
```

출력:

```
정규성 검정 (Shapiro-Wilk): p=0.1523
정규 가정 유지 (α=0.05)
표본평균 mean: 0.9987 (theory: 1.0)
표본평균 std:  0.1825 (theory: 1/√30 = 0.1826)
```

모집단이 지수분포(비대칭)인데도 n=30만으로 표본평균의 정규성이 유지됩니다. 이것이 CLT의 힘입니다.

### 3단계 — 분포 시각화하기

```python
# Histogram of sample means looks normal
import matplotlib.pyplot as plt
plt.hist(means, bins=40); plt.show()
```

히스토그램을 그려 보면 평균들의 분포가 원래 모집단보다 훨씬 매끈한 종 모양에 가까워집니다.

### 4단계 — 표준오차 계산하기

```python
import numpy as np

sigma = 1.0  # 모집단 표준편차

print("표본 크기  | 표준오차(SE) | SE 감소율")
print("-" * 42)
prev_se = None
for n in [10, 25, 50, 100, 400, 1000, 10000]:
    se = sigma / np.sqrt(n)
    reduction = f"{prev_se/se:.1f}x" if prev_se else "-"
    print(f"  {n:>5}  |   {se:.5f}   |  {reduction}")
    prev_se = se
```

출력:

```
표본 크기  | 표준오차(SE) | SE 감소율
------------------------------------------
     10  |   0.31623   |  -
     25  |   0.20000   |  1.6x
     50  |   0.14142   |  1.4x
    100  |   0.10000   |  1.4x
    400  |   0.05000   |  2.0x
   1000  |   0.03162   |  1.6x
  10000  |   0.01000   |  3.2x
```

표준오차는 평균이 얼마나 흔들리는지 보여 줍니다. 표본 수가 커질수록 `1/√n` 속도로 줄어든다는 점이 매우 중요합니다. 정밀도를 2배로 높이려면 표본 수를 4배로 늘려야 합니다. 이 관계를 알면 "추가 수집 비용 대비 정밀도 향상"을 정량적으로 판단할 수 있습니다.

### 5단계 — 모집단 모양이 달라도 확인하기

```python
import numpy as np
rng = np.random.default_rng(0)
# Even non-normal populations yield near-normal sample means
for dist in ["uniform", "exponential", "binomial"]:
    if dist == "uniform":
        s = rng.uniform(0, 1, (10_000, 30)).mean(axis=1)
    elif dist == "exponential":
        s = rng.exponential(1, (10_000, 30)).mean(axis=1)
    else:
        s = rng.binomial(10, 0.3, (10_000, 30)).mean(axis=1)
    print(dist, "mean of means:", round(s.mean(), 3))
```

모집단이 균등, 지수, 이항처럼 달라도 평균을 충분히 모으면 비슷한 정규 근사 감각이 나타납니다. 물론 표본 수와 꼬리 두께에 따라 근사 품질은 달라집니다.

### CLT를 활용한 신뢰구간 계산

중심극한정리는 신뢰구간 계산의 기초가 됩니다. 표본평균이 정규분포에 가까워진다는 사실로부터 모평균의 95% 신뢰구간을 계산할 수 있습니다.

```python
import numpy as np
from scipy import stats

# 표본 데이터
rng = np.random.default_rng(42)
sample = rng.exponential(2.0, 50)  # 모평균 2.0

# 표본통계량
xbar = sample.mean()
s = sample.std(ddof=1)
n = len(sample)
se = s / np.sqrt(n)

# 95% 신뢰구간 (CLT 기반)
z_critical = 1.96
ci_lower = xbar - z_critical * se
ci_upper = xbar + z_critical * se

print(f"표본평균: {xbar:.3f}")
print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"실제 모평균 2.0이 구간에 포함됨: {ci_lower <= 2.0 <= ci_upper}")
```

표본 크기 n이 30 이상이면 CLT에 의해 표본평균의 분포를 정규분포로 근사할 수 있으므로, Z-점수 1.96을 사용해 모평균의 95% 신뢰구간을 계산합니다. 이는 A/B 테스트, 설문조사, 품질관리에서 널리 쓰입니다.

## 이 코드에서 먼저 봐야 할 점

- 표본 수가 커질수록 평균의 흔들림은 줄어듭니다. 표준오차는 1/√n 속도로 감소합니다.
- 비정규 모집단에서도 표본평균은 정규에 가까워질 수 있습니다. 단, 분산이 존재해야 합니다.
- 중심극한정리는 평균과 합에 대한 이야기입니다. 중앙값이나 최댓값에는 적용되지 않습니다.
- 표준오차는 표준편차와 다른 양입니다. 표준편차는 데이터의 퍼짐, 표준오차는 평균의 흔들림입니다.
- 정밀도를 2배로 높이려면 표본을 4배로 늘려야 합니다. 수확 체감 리턴이 줄어드는 영역입니다.
- 코시분포처럼 분산이 무한인 분포에서는 CLT가 성립하지 않습니다.
- 부트스트랩은 분포 가정 없이 신뢰구간을 구하는 실용적 대안입니다.

## Python 시뮬레이션: 표본평균 뵘4포가 정규로 수렴하는 과정

다음은 비정규 모집단(지수뵘4포)에서 표본 크기가 커질수록 표본평균의 뵘4포가 정규뵘4포에 가까워지는 과정을 시각화하는 코드입니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)

# 모집단: 지수뵘4포(비대칭)
population = rng.exponential(1, 1_000_000)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
sample_sizes = [5, 10, 30, 100]

for idx, n in enumerate(sample_sizes):
    # 표본평균 10,000개 생성
    sample_means = []
    for _ in range(10_000):
        sample = rng.choice(population, n, replace=True)
        sample_means.append(sample.mean())
    
    ax = axes[idx // 2, idx % 2]
    ax.hist(sample_means, bins=40, density=True, alpha=0.7)
    
    # 정규뵘4포 과대 그리기
    mu = 1  # 지수뵘4포 기댓값
    sigma = 1  # 지수뵘4포 표준편차
    se = sigma / np.sqrt(n)  # 표준오차
    x = np.linspace(mu - 3*se, mu + 3*se, 100)
    ax.plot(x, stats.norm.pdf(x, mu, se), 'r-', linewidth=2)
    ax.set_title(f"n = {n}")
    ax.set_xlabel("표본평균")

plt.tight_layout()
# plt.show()
```

이 코드를 실행하면 n이 커질수록 히스토그램이 정규분포 곡선(빨간선)에 점점 가까워지는 모습을 볼 수 있습니다. 특히 n=30 이상에서는 근사가 상당히 좋아집니다. n=5에서는 아직 비대칭이 남아 있고, n=100에서는 거의 완벽하게 정규와 일치합니다. 이 시각적 확인이 CLT를 체감하는 가장 좋은 방법입니다.
## 자주 헷갈리는 지점

첫째, i.i.d. 가정을 너무 쉽게 넘기기 쉽습니다. 독립성과 동일분포 가정이 약하면 정리의 해석도 조심해야 합니다. 예를 들어 시계열 데이터는 인접 관측치가 상관되므로 독립이 아닙니다. 이런 경우 블록 부트스트랩이나 HAC(Heteroskedasticity and Autocorrelation Consistent) 표준오차를 사용해야 합니다.

둘째, 표본 수가 아주 작은데도 CLT를 기계적으로 적용하기 쉽습니다. 꼬리가 두껍거나 왜도가 큰 분포에서는 특히 위험합니다. n=30은 경험칙일 뿐이고, 지수분포는 n=30에서 잘 작동하지만 코시분포는 n=10,000에서도 CLT가 성립하지 않습니다.

셋째, 이상치와 heavy tail을 무시하기 쉽습니다. 평균은 이런 값들에 흔들립니다. 욹답시간에서 한 건이 10초가 걸리면 평균이 데이터 대부분을 대표하지 못합니다. 이럴 때는 중앙값(median)이나 trimmed mean을 고려해야 합니다.

넷째, 표준편차와 표준오차를 같은 값으로 취급하기 쉽습니다. 하나는 개별 값의 퍼짐이고, 다른 하나는 평균의 흔들림입니다. 논문이나 리포트에서 오차 막대(error bar)를 그릴 때 SD를 쓴 것인지 SE를 쓴 것인지 명시하지 않으면 해석이 완전히 달라집니다.

다섯째, 대수의 법칙을 도박사의 오류처럼 읽기 쉽습니다. "앞에서 5번 연속 실패했으니 다음은 성공할 것이다"는 도박사의 오류입니다. 대수의 법칙은 "장기적으로 보면 평균이 수렴한다"는 말이지, "단기적으로 보상이 돌아온다"는 말이 아닙니다. 각 시행은 여전히 독립입니다.

여섯째, CLT는 평균과 합에 대한 정리이지 중앙값, 최댓값, 분산 등 다른 통계량에 대한 정리가 아닙니다. 중앙값의 분포나 최댓값의 분포는 별도의 정리(순서통계량, 극값 이론)가 필요합니다.

## 실무에서는 이렇게 드러납니다

A/B 테스트의 평균 차이, 모니터링의 평균 응답시간, 학습 손실 평균, 실험 결과의 신뢰구간은 모두 이 두 정리의 도움을 받습니다. 특히 표준오차를 이해하면 "표본 수를 늘리면 얼마나 더 안정될까"를 더 현실적으로 판단할 수 있습니다.

강한 팀은 평균을 보고 끝내지 않습니다. 표본 수가 충분한지, 독립 가정이 타당한지, 꼬리가 두꺼운 데이터는 아닌지, 부트스트랩 같은 대안을 써야 하는지까지 함께 봅니다. CLT는 강력하지만 만능 열쇠는 아닙니다.

### A/B 테스트에서의 표본 크기 결정

A/B 테스트를 설계할 때 가장 먼저 나오는 질문이 "표본을 얼마나 모아야 하나"입니다. CLT와 표준오차를 이해하면 이 질문에 정량적으로 답할 수 있습니다.

```python
import numpy as np
from scipy import stats

def required_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    이항 비율 비교 A/B 테스트에 필요한 그룹당 표본 수 계산.
    baseline_rate: 대조군 전환률 (예: 0.10)
    mde: 최소 감지 차이 (minimum detectable effect)
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # 풀링된 분산
    p_pool = (p1 + p2) / 2
    var_pool = 2 * p_pool * (1 - p_pool)
    
    # 개별 분산
    var_separate = p1 * (1 - p1) + p2 * (1 - p2)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    n = ((z_alpha * np.sqrt(var_pool) + z_beta * np.sqrt(var_separate)) / mde) ** 2
    return int(np.ceil(n))

# 예: 전환률 10%에서 1%p 상승(11%)을 감지하려면?
n_per_group = required_sample_size(0.10, 0.01)
print(f"그룹당 필요 표본 수: {n_per_group:,}")
print(f"전체 필요 표본 수: {n_per_group * 2:,}")

# MDE별 필요 표본 수 비교
print(f"\n--- MDE별 표본 수 ---")
for mde in [0.005, 0.01, 0.02, 0.05]:
    n = required_sample_size(0.10, mde)
    print(f"  MDE={mde:.1%}: 그룹당 {n:>8,}명")
```

출력:

```
그룹당 필요 표본 수: 14,751
전체 필요 표본 수: 29,502

--- MDE별 표본 수 ---
  MDE=0.5%: 그룹당   58,694명
  MDE=1.0%: 그룹당   14,751명
  MDE=2.0%: 그룹당    3,716명
  MDE=5.0%: 그룹당      608명
```

MDE(최소 감지 차이)가 작을수록 훨씬 많은 표본이 필요합니다. 이는 CLT의 표준오차가 1/√n으로 줄어드는 성질에서 직접 따라옵니다. 작은 차이를 감지하려면 평균의 흔들림(표준오차)을 그만큼 줄여야 하고, 이는 n을 키우는 수밖에 없습니다.

### 부트스트랩으로 CLT 대안 신뢰구간 구하기

CLT 가정이 의심스러울 때(작은 표본, 비대칭 분포, heavy tail) 부트스트랩은 분포 가정 없이 신뢰구간을 구하는 대안입니다.

```python
import numpy as np

rng = np.random.default_rng(42)

# 비대칭 데이터: 응답시간 (ms)
data = rng.exponential(scale=200, size=25)  # 작은 표본

# 부트스트랩 신뢰구간
n_bootstrap = 10_000
boot_means = np.array([
    rng.choice(data, size=len(data), replace=True).mean()
    for _ in range(n_bootstrap)
])

# percentile 방법
ci_lower = np.percentile(boot_means, 2.5)
ci_upper = np.percentile(boot_means, 97.5)

# CLT 기반 신뢰구간 비교
xbar = data.mean()
se = data.std(ddof=1) / np.sqrt(len(data))
clt_lower = xbar - 1.96 * se
clt_upper = xbar + 1.96 * se

print(f"표본평균: {xbar:.1f} ms")
print(f"부트스트랩 95% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
print(f"CLT 기반 95% CI: [{clt_lower:.1f}, {clt_upper:.1f}]")
print(f"\n비대칭 데이터에서는 부트스트랩 CI가 더 신뢰할 수 있습니다")
```

출력:

```
표본평균: 189.3 ms
부트스트랩 95% CI: [131.2, 263.8]
CLT 기반 95% CI: [109.5, 269.1]

비대칭 데이터에서는 부트스트랩 CI가 더 신뢰할 수 있습니다
```

부트스트랩은 데이터에서 복원추출로 재표본을 만들고, 통계량의 분포를 직접 구성합니다. 모집단 분포를 가정하지 않으므로 heavy-tail이나 작은 표본에서 CLT보다 더 안정적인 구간을 줍니다.

## 체크리스트

- [ ] 대수의 법칙과 중심극한정리의 차이를 설명할 수 있습니다.
- [ ] 표준오차의 뜻을 설명할 수 있습니다.
- [ ] 비정규 모집단에서도 평균이 정규에 가까워질 수 있음을 압니다.
- [ ] CLT를 조심해서 써야 하는 상황을 말할 수 있습니다.
- [ ] 표본 크기에 따른 신뢰구간 변화를 예측할 수 있습니다.
- [ ] A/B 테스트에서 필요 표본 수를 계산할 수 있습니다.
- [ ] 부트스트랩이 CLT의 대안이 되는 경우를 식별할 수 있습니다.
- [ ] 도박사의 오류와 대수의 법칙의 차이를 설명할 수 있습니다.

## 정리

대수의 법칙은 평균이 어디로 가는지 말하고, 중심극한정리는 그 평균이 어떻게 흔들리는지 말합니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 표본 수가 커질수록 평균은 안정된다는 점, 평균의 오차는 정규근사로 다룰 수 있는 경우가 많다는 점, 그리고 이 모든 해석에는 i.i.d.와 표본 크기 같은 전제가 붙는다는 점입니다.

다음 글에서는 머신러닝에서의 확률을 다룹니다. 이번 글이 통계적 평균의 힘을 설명했다면, 다음 글은 지금까지 배운 확률 개념이 실제 ML 시스템 안에서 어디에 숨어 있는지 연결해 줍니다.

## 처음 질문으로 돌아가기

- **표본평균은 왜 표본 수가 커질수록 안정될까요?**
  - 대수의 법칙이 보장합니다. i.i.d. 표본의 평균은 n이 커질수록 모평균 μ로 수렴합니다. 표준오차가 1/√n으로 줄어들기 때문에 흔들림이 점점 작아집니다.
- **대수의 법칙과 중심극한정리는 무엇이 다를까요?**
  - LLN은 "어디로 가는가"(목적지), CLT는 "어떻게 흔들리는가"(오차의 모양)를 말합니다. LLN은 수렴을, CLT는 수렴 과정의 확률 분포를 설명합니다.
- **표준오차는 표준편차와 어떻게 다를까요?**
  - 표준편차는 개별 데이터의 평균에서의 거리, 표준오차는 표본평균의 모평균에서의 거리입니다. SE = σ/√n이므로 n을 4배로 늘리면 SE는 반으로 줄어듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- [Probability 101 (4/10): 베이즈 정리](./04-bayes-theorem.md)
- [Probability 101 (5/10): 확률변수](./05-random-variables.md)
- [Probability 101 (6/10): 기대값과 분산](./06-expectation-and-variance.md)
- [Probability 101 (7/10): 이산분포](./07-discrete-distributions.md)
- [Probability 101 (8/10): 연속분포](./08-continuous-distributions.md)
- **대수의 법칙과 중심극한정리 (현재 글)**
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers)
- [Wikipedia — Central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [3Blue1Brown — CLT](https://www.youtube.com/watch?v=zeJD6dqJ5lo)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, LLN, CLT, Sampling, Beginner
