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
print("means at n=10, 100, 10_000:", running[9], running[99], running[-1])
```

표본 수가 커질수록 평균이 0.5 근처로 안정되는 모습을 직접 볼 수 있습니다. 이것이 대수의 법칙의 가장 직관적인 그림입니다.

### 2단계 — 중심극한정리 시뮬레이션

```python
import numpy as np
rng = np.random.default_rng(0)
means = [rng.exponential(1, 30).mean() for _ in range(10_000)]
print("mean ~ 1:", np.mean(means), "std ~ 1/sqrt(30):", np.std(means))
```

원래 모집단은 지수분포처럼 비대칭이지만, 표본평균을 많이 모아 보면 그 분포가 정규에 가까워집니다. 이 장면이 중심극한정리의 핵심입니다.

### 3단계 — 분포 시각화하기

```python
# Histogram of sample means looks normal
import matplotlib.pyplot as plt
plt.hist(means, bins=40); plt.show()
```

히스토그램을 그려 보면 평균들의 분포가 원래 모집단보다 훨씬 매끈한 종 모양에 가까워집니다.

### 4단계 — 표준오차 계산하기

```python
import math
sigma = 1.0
n = 30
print("SE:", sigma / math.sqrt(n))
```

표준오차는 평균이 얼마나 흔들리는지 보여 줍니다. 표본 수가 커질수록 `1/√n` 속도로 줄어든다는 점이 매우 중요합니다.

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

- 표본 수가 커질수록 평균의 흔들림은 줄어듭니다.
- 비정규 모집단에서도 표본평균은 정규에 가까워질 수 있습니다.
- 중심극한정리는 평균과 합에 대한 이야기입니다.
- 표준오차는 표준편차와 다른 양입니다.

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

이 코드를 실행하면 n이 커질수록 히스토그램이 정규뵘4포 곡선(빨간선)에 점점 가까워지는 모습을 볼 수 있습니다. 특히 n=30 이상에서는 근사가 상당히 좋아집니다.
## 자주 헷갈리는 지점

첫째, i.i.d. 가정을 너무 쉽게 넘기기 쉽습니다. 독립성과 동일분포 가정이 약하면 정리의 해석도 조심해야 합니다.

둘째, 표본 수가 아주 작은데도 CLT를 기계적으로 적용하기 쉽습니다. 꼬리가 두껍거나 왜도가 큰 분포에서는 특히 위험합니다.

셋째, 이상치와 heavy tail을 무시하기 쉽습니다. 평균은 이런 값들에 흔들립니다.

넷째, 표준편차와 표준오차를 같은 값으로 취급하기 쉽습니다. 하나는 개별 값의 퍼짐이고, 다른 하나는 평균의 흔들림입니다.

다섯째, 대수의 법칙을 도박사의 오류처럼 읽기 쉽습니다. 과거의 실패가 다음 번 성공을 보장하는 것은 아닙니다. 수렴은 장기 평균의 이야기입니다.

## 실무에서는 이렇게 드러납니다

A/B 테스트의 평균 차이, 모니터링의 평균 응답시간, 학습 손실 평균, 실험 결과의 신뢰구간은 모두 이 두 정리의 도움을 받습니다. 특히 표준오차를 이해하면 “표본 수를 늘리면 얼마나 더 안정될까”를 더 현실적으로 판단할 수 있습니다.

강한 팀은 평균을 보고 끝내지 않습니다. 표본 수가 충분한지, 독립 가정이 타당한지, 꼬리가 두꺼운 데이터는 아닌지, 부트스트랩 같은 대안을 써야 하는지까지 함께 봅니다. CLT는 강력하지만 만능 열쇠는 아닙니다.

## 체크리스트

## CLT가 깨지는 경우

중심극한정리는 매우 강력하지만 만능은 아닙니다. 특정 조건에서는 CLT의 근사가 크게 빗나가거나 수렴 속도가 매우 느려집니다.

**1. Heavy-tailed distribution (꾸리가 두껐운 뵘4포)**

뵘4포의 꾸리가 두껍어서 극단값이 자주 나타나는 경우, 표본 수가 충뵘4히 크지 않으면 CLT 근사가 나빠지게 됩니다. 예를 들어 코시뵘4포처럼 뵘4산이 무한대인 뵘4포에서는 CLT 자체가 성립하지 않습니다.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
# Cauchy 뵘4포는 뵘4산이 정의되지 않음
# 표본평균을 모아도 정규뵘4포처럼 보이지 않음
means_cauchy = [rng.standard_cauchy(30).mean() for _ in range(10_000)]
plt.hist(means_cauchy, bins=50, range=(-10, 10))
plt.title("표본평균 뵘4포 (Cauchy)")
# 정규뵘4포로 수렴하지 않음
```

**2. 표본 수가 너무 작은 경우**

모집단이 비대칭이고 표본 수 n이 작으면 CLT 근사는 부정확합니다. 일반적으로 n ≥ 30을 근사 기준으로 삼지만, 비대칭이 클수록 더 큰 n이 필요합니다.

**3. 독립성이 긨지는 경우**

시계열 데이터나 공간적 상관 구조처럼 독립성 가정이 긨지면, 표준 CLT를 직접 적용할 수 없습니다. 이럴 때는 대안 기법(부트스트랩, 블럭 리샘플링)을 고려해야 합니다.
- [ ] 대수의 법칙과 중심극한정리의 차이를 설명할 수 있습니다.
- [ ] 표준오차의 뜻을 설명할 수 있습니다.
- [ ] 비정규 모집단에서도 평균이 정규에 가까워질 수 있음을 압니다.
- [ ] CLT를 조심해서 써야 하는 상황을 말할 수 있습니다.

## 정리

대수의 법칙은 평균이 어디로 가는지 말하고, 중심극한정리는 그 평균이 어떻게 흔들리는지 말합니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 표본 수가 커질수록 평균은 안정된다는 점, 평균의 오차는 정규근사로 다룰 수 있는 경우가 많다는 점, 그리고 이 모든 해석에는 i.i.d.와 표본 크기 같은 전제가 붙는다는 점입니다.

다음 글에서는 머신러닝에서의 확률을 다룹니다. 이번 글이 통계적 평균의 힘을 설명했다면, 다음 글은 지금까지 배운 확률 개념이 실제 ML 시스템 안에서 어디에 숨어 있는지 연결해 줍니다.

## 처음 질문으로 돌아가기

- **표본평균은 왜 표본 수가 커질수록 안정될까요?**
  - 개념의 정의와 실무에서의 사용법을 분리해서 봅니다.
  - 구체적인 예제와 시뮬레이션으로 개념을 실제로 확인합니다.
- **표준오차는 표준편차와 어떻게 다를까요?**
  - 이 개념을 실제로 적용할 때 주의할 점을 정리합니다.

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

Tags: Probability, LLN, CLT, Sampling, Beginner
