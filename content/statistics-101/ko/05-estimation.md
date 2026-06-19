---
series: statistics-101
episode: 5
title: "Statistics 101 (5/10): 추정"
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
  - Estimation
  - Inference
  - PointEstimate
  - Beginner
seo_description: 점 추정과 구간 추정의 차이를 비교하고 표본 평균이 모평균을 추정하는 과정을 단계별 코드로 익히는 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (5/10): 추정

표본 평균을 계산했다고 해서 분석이 끝난 것은 아닙니다. 숫자 하나를 얻었다는 사실보다 중요한 것은 그 숫자가 모집단의 참값에서 얼마나 벗어날 수 있는지입니다. 추정은 이 거리감을 숫자로 다루는 과정입니다.

그래서 좋은 추정은 값만 내놓지 않습니다. 언제나 값과 오차를 함께 보고합니다. 오차가 빠진 추정값은 단정적인 문장처럼 보이지만 실제로는 불확실성을 숨긴 숫자에 가깝습니다.

이 글은 Statistics 101 시리즈의 5번째 글입니다. 여기서는 점 추정과 구간 추정의 차이, 표준오차의 의미, 표본 수가 추정 안정성에 주는 영향을 차례대로 봅니다.

![Statistics 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/05/05-01-concept-at-a-glance.ko.png)
*Statistics 101 5장 흐름 개요*
> 좋은 추정값은 큰 숫자 하나가 아니라 범위와 함께 말해집니다.

## 이 글에서 다룰 문제

- 표본평균은 모집단 평균을 얼마나 잘 대신할 수 있을까요?
- 점 추정과 구간 추정은 어떤 차이가 있을까요?
- 표준오차는 표준편차와 어떻게 다를까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

대시보드에 보이는 수치, 실험 결과의 평균, 보고서의 전환율은 모두 모집단의 참값이 아니라 표본에서 얻은 추정값입니다. 그런데 많은 보고서가 추정값만 적고 오차를 생략합니다. 이러면 숫자는 단정적으로 보이지만, 실제로는 얼마나 흔들릴 수 있는지 알 수 없습니다.

의사결정자는 평균 100이라는 숫자보다 그 숫자가 95인지 105인지 더 중요할 때가 많습니다. 예산을 배정할지, 기능을 배포할지, 리스크를 감수할지 판단하려면 추정의 불확실성이 반드시 함께 보여야 합니다.

## 멘탈 모델: 점 추정과 구간 추정

표본에서 먼저 하나의 대표값을 뽑고, 그다음 그 대표값이 얼마나 흔들릴 수 있는지를 표준오차로 표현한 뒤, 마지막에 구간으로 확장하는 흐름으로 보면 이해가 쉽습니다. 점 추정은 중심점이고, 구간 추정은 그 중심점의 흔들림을 드러냅니다.

표준오차는 표본 자체의 흩어짐이 아니라, 표본평균이라는 추정량이 반복 표집에서 얼마나 흔들릴지를 나타냅니다. 이 차이를 구분하면 표준편차와 표준오차를 헷갈릴 일이 크게 줄어듭니다.

### 점추정 대비 구간추정 비교

| 구분 | 점추정 | 구간추정 |
|---|---|---|
| **정의** | 모수를 하나의 값으로 추정 | 모수가 들어 있을 범위를 제시 |
| **장점** | 간결하고 이해하기 쉬움 | 불확실성을 명시적으로 표현 |
| **단점** | 오차를 보여주지 않음 | 구간이 넓으면 정보 가치 감소 |
| **예시** | "평균 응답시간은 120ms입니다" | "평균 응답시간은 115~125ms입니다 (95% 신뢰구간)" |
| **언제** | 빠른 요약이 필요할 때 | 의사결정에 위험 평가가 필요할 때 |

점추정은 보고서를 간결하게 만들지만, 구간추정은 판단자가 위험을 읽을 수 있게 합니다.

## 불편성과 효율성

좋은 추정량은 두 가지 조건을 만족합니다.

1. **불편성(unbiasedness)**: 추정량의 기대값이 참값과 일치합니다.
2. **효율성(efficiency)**: 분산이 작아서 반복 표집해도 결과가 안정적입니다.

### 불편추정량: 표본평균은 모평균의 불편추정량

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
population_mean = 100
population_std = 20

# 표본평균을 2000번 반복 (표집 분포)
n_samples = 2000
sample_size = 50
sample_means = [
    rng.normal(loc=population_mean, scale=population_std, size=sample_size).mean()
    for _ in range(n_samples)
]

print(f"표본평균들의 평균: {np.mean(sample_means):.2f}")
print(f"모평균: {population_mean}")
print(f"표본평균의 표준편차 (표준오차): {np.std(sample_means):.3f}")
print(f"이론 표준오차 (σ/√n): {population_std / np.sqrt(sample_size):.3f}")

# 표집 분포 시각화
plt.figure(figsize=(9, 4))
plt.hist(sample_means, bins=50, density=True, alpha=0.7, color="steelblue", edgecolor="white")
plt.axvline(np.mean(sample_means), color="red", lw=2,
            label=f"표본평균들의 평균: {np.mean(sample_means):.1f}")
plt.axvline(population_mean, color="green", lw=2, linestyle="--",
            label=f"모평균: {population_mean}")
plt.xlabel("표본평균")
plt.ylabel("밀도")
plt.title(f"표집 분포 (n={sample_size}, 반복={n_samples}회)")
plt.legend()
plt.tight_layout()
plt.show()
```

**예상 출력:**

```text
표본평균들의 평균: 99.97
모평균: 100
표본평균의 표준편차 (표준오차): 2.836
이론 표준오차 (σ/√n): 2.828
```

표본평균은 평균적으로 참값을 가리키므로 불편추정량입니다. 반면 표본분산을 `n`으로 나누면 편향됩니다. 그래서 `n-1`로 나누는 것이 불편추정량입니다(`ddof=1`).

## 표준오차와 표본 크기의 관계

```python
import numpy as np
import matplotlib.pyplot as plt

population_std = 20

sample_sizes = [10, 25, 50, 100, 200, 500, 1000]
standard_errors = [population_std / np.sqrt(n) for n in sample_sizes]

for n, se in zip(sample_sizes, standard_errors):
    print(f"n={n:4d} → SE={se:.3f}")

# 시각화
plt.figure(figsize=(8, 4))
plt.plot(sample_sizes, standard_errors, "o-", color="steelblue", lw=2)
plt.xlabel("표본 크기 (n)")
plt.ylabel("표준오차 (SE)")
plt.title("표본 크기와 표준오차의 관계 (σ=20)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

**예상 출력:**

```text
n=  10 → SE=6.325
n=  25 → SE=4.000
n=  50 → SE=2.828
n= 100 → SE=2.000
n= 200 → SE=1.414
n= 500 → SE=0.894
n=1000 → SE=0.632
```

표본 수가 4배 늘면 표준오차는 절반으로 줄어듭니다. 이 관계를 알면 "몇 개 샘플이면 충분한가?" 질문에 구체적으로 답할 수 있습니다.

## 파이썬으로 신뢰구간 계산하기

```python
import numpy as np
from scipy import stats

# 표본 데이터
rng = np.random.default_rng(42)
sample = rng.normal(loc=100, scale=20, size=50)

# 표본 통계
n = len(sample)
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(n)

# 95% 신뢰구간 (t-분포 사용: n < 30이거나 모분산 미지)
confidence = 0.95
t_crit = stats.t.ppf((1 + confidence) / 2, df=n-1)
margin = t_crit * se
ci_lower, ci_upper = mean - margin, mean + margin

print(f"표본평균: {mean:.2f}")
print(f"표준오차: {se:.2f}")
print(f"t 임계값 (df={n-1}): {t_crit:.3f}")
print(f"95% 신뢰구간: [{ci_lower:.2f}, {ci_upper:.2f}]")

# scipy로 간단히
ci = stats.t.interval(confidence, df=n-1, loc=mean, scale=se)
print(f"\nscipy 확인: [{ci[0]:.2f}, {ci[1]:.2f}]")
```

**예상 출력:**

```text
표본평균: 99.87
표준오차: 2.61
t 임계값 (df=49): 2.010
95% 신뢰구간: [94.62, 105.12]

scipy 확인: [94.62, 105.12]
```

표본 수가 30 이하일 때는 정규분포 대신 t-분포를 써야 합니다. t-분포는 꼬리가 더 두껍기 때문에 신뢰구간이 조금 더 넓어지고, 이는 작은 표본에서 불확실성이 크다는 사실을 반영합니다.

## 핵심 용어 정리

- **점 추정**: 모수를 하나의 값으로 추정하는 방식입니다.
- **구간 추정**: 모수가 들어 있을 법한 범위를 제시하는 방식입니다.
- **표준오차(SE)**: 추정량의 표준편차로, 보통 `s/√n` 형태를 가집니다.
- **불편추정량**: 기대값이 모수와 일치하는 추정량입니다.
- **일치추정량**: 표본 수가 커질수록 모수에 가까워지는 추정량입니다.

## 추정값만 적은 보고서는 반쪽짜리다

이전 해석: "표본 평균은 100입니다."

이 문장만으로는 이 값이 꽤 안정적인지, 표본이 작아서 많이 흔들릴 수 있는지 판단할 수 없습니다.

이후 해석: "표본평균은 100이고 표준오차는 2.5입니다. 표본 수 64 기준 95% 신뢰구간은 [95.1, 104.9]입니다."

추정값에 오차가 붙는 순간 숫자는 훨씬 덜 단정적이지만 훨씬 더 쓸모 있어집니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 표준편차와 표준오차 혼동 | SE를 데이터 퍼짐으로 설명 | SE = 추정량의 흔들림, SD = 데이터 퍼짐 |
| 점추정값만 보고 | "평균 100입니다" 에서 끝냄 | 95% CI도 함께 보고 |
| 표본이 작은데 z 근사 사용 | n=15에서 z=1.96 적용 | n < 30이면 t-분포 사용 |
| 표본 수 늘리면 오차 0 기대 | n=10000이면 완벽하다고 생각 | 편향이 있으면 n이 커도 오차가 남음 |
| ddof=0으로 표본분산 계산 | `np.var(data)` 사용 | 표본 분산은 `np.var(data, ddof=1)` |
| 구간이 좁으면 정확하다고 단정 | CI가 좁을수록 신뢰 가능하다고 믿음 | 편향이 있으면 좁아도 잘못될 수 있음 |

## 실습: 5단계 추정

### 1단계 — 표본을 준비한다

```python
import numpy as np
rng = np.random.default_rng(42)
sample = rng.normal(loc=100, scale=20, size=64)
```

모평균 100 주변에서 표본을 하나 뽑았다고 생각하면 됩니다.

### 2단계 — 점 추정값을 계산한다

```python
mean = sample.mean()
print(f"표본평균 (x̄): {mean:.2f}")
```

표본평균은 모평균에 대한 가장 기본적인 점 추정값입니다.

### 3단계 — 표준오차를 계산한다

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
print(f"표준오차 (SE): {se:.2f}")
```

표본 수가 커질수록 표준오차가 줄어드는 구조를 확인할 수 있습니다.

### 4단계 — 95% 구간을 만든다

```python
from scipy import stats

ci = stats.t.interval(0.95, df=len(sample)-1, loc=mean, scale=se)
print(f"95% CI: [{ci[0]:.1f}, {ci[1]:.1f}]")
```

점 하나였던 추정값이 범위로 바뀌는 순간 해석이 훨씬 안정됩니다.

### 5단계 — 보고 문장을 쓴다

```text
x̄ = 99.8 (n=64), SE = 2.4
95% CI: [95.0, 104.6]
→ 모평균은 95% 신뢰수준에서 95.0~104.6 사이에 있을 것으로 추정됩니다.
```

추정 결과는 값, 표본 수, 오차를 함께 적는 습관이 좋습니다.

## 부트스트랩으로 추정량 안정성 비교

부트스트랩(Bootstrap)은 표본에서 반복 추출해 추정량의 분포를 경험적으로 만드는 방법입니다. 정규성 가정 없이 신뢰구간을 구할 수 있어 실무에서 자주 씁니다.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(123)
sample = rng.lognormal(mean=4.0, sigma=0.8, size=120)

B = 8000
mean_boot = []
median_boot = []

for _ in range(B):
    r = rng.choice(sample, size=len(sample), replace=True)
    mean_boot.append(r.mean())
    median_boot.append(np.median(r))

mean_ci = np.percentile(mean_boot, [2.5, 97.5])
median_ci = np.percentile(median_boot, [2.5, 97.5])

print(f"원본 표본평균: {sample.mean():.2f}")
print(f"평균 추정 95% 부트스트랩 구간: [{mean_ci[0]:.2f}, {mean_ci[1]:.2f}]")
print(f"중앙값 추정 95% 부트스트랩 구간: [{median_ci[0]:.2f}, {median_ci[1]:.2f}]")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(mean_boot, bins=60, density=True, alpha=0.7, color="steelblue")
axes[0].axvline(mean_ci[0], color="red", linestyle="--")
axes[0].axvline(mean_ci[1], color="red", linestyle="--")
axes[0].set_title("평균 부트스트랩 분포")

axes[1].hist(median_boot, bins=60, density=True, alpha=0.7, color="orange")
axes[1].axvline(median_ci[0], color="red", linestyle="--")
axes[1].axvline(median_ci[1], color="red", linestyle="--")
axes[1].set_title("중앙값 부트스트랩 분포")

plt.tight_layout()
plt.show()
```

긴 꼬리에서는 중앙값 구간이 더 안정적으로 나오는 경우가 많습니다. 보고서에는 "어떤 추정량을 채택했는지"와 "채택 이유"를 함께 적는 것이 좋습니다.

## 추정의 정확도와 정밀도

추정량은 두 가지 차원에서 평가됩니다.

1. **정확도(Accuracy)**: 평균적으로 참값에 얼마나 가까운가 (편향 없음)
2. **정밀도(Precision)**: 반복 측정했을 때 결과가 얼마나 일관되는가 (분산 작음)

이상적인 추정량은 정확하면서도 정밀합니다. 하지만 때로는 트레이드오프가 있습니다.

- 표본평균은 불편추정량(정확)이지만 극단값에 민감합니다(정밀도 낮음).
- 중앙값은 극단값에 강하지만(정밀) 정규분포에서는 표본평균보다 효율이 떨어집니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트의 전환율, 월간 매출 평균, 대시보드의 p95 지연 시간은 모두 추정값입니다. 그래서 실무에서는 에러 바, 신뢰구간, 표준오차가 함께 등장합니다. 숫자가 좋아 보인다는 느낌보다, 그 숫자가 얼마나 흔들릴 수 있는지가 더 중요한 경우가 많습니다.

시니어 엔지니어는 추정값 옆에 표준오차를 붙이는 일을 빼먹지 않습니다. 표본 수는 감으로 정하지 않고 검정력이나 비용을 함께 고려해 정하며, 편향 여부를 먼저 점검합니다. 오차를 숨기지 않는 보고서가 더 신뢰받는 이유가 여기에 있습니다.

## 운영 체크리스트

- [ ] 점 추정과 구간 추정을 구분할 수 있습니다.
- [ ] 표준오차를 계산할 수 있습니다.
- [ ] 95% 구간이 왜 필요한지 설명할 수 있습니다.
- [ ] 표본 수가 추정 안정성에 미치는 영향을 이해합니다.

## 연습 문제

1. N=10과 N=1000에서 표준오차가 어떻게 달라지는지 비교해 보세요.
2. 불편추정량의 의미를 한 문장으로 적어 보세요.
3. 모평균이 100인지 판단하려면 어떤 추정 절차를 밟을지 써 보세요.

## 정리와 다음 글

추정은 일부 데이터를 보고 전체를 가늠하는 작업입니다. 이때 중요한 것은 추정값을 얼마나 멋지게 계산했느냐보다, 그 추정값이 얼마나 흔들릴 수 있는지를 함께 보여 주는가입니다. 점 추정은 출발점이고, 구간 추정은 그 출발점에 붙는 불확실성을 드러내는 장치입니다.

다음 글에서는 신뢰구간을 더 깊게 다룹니다. 95% 신뢰구간이라는 표현이 정확히 무엇을 뜻하는지, 그리고 많은 사람이 왜 이 개념을 잘못 읽는지 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- **Statistics 101 (5/10): 추정 (현재 글)**
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [scipy.stats — Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Estimation](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample)
- [Wikipedia — Standard Error](https://en.wikipedia.org/wiki/Standard_error)
- [NIST — Estimation Methods](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35.htm)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Estimation, Inference, PointEstimate, Beginner
