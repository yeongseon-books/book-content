---
series: statistics-101
episode: 6
title: "Statistics 101 (6/10): 신뢰구간"
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
  - ConfidenceInterval
  - Inference
  - Uncertainty
  - Beginner
seo_description: 95퍼센트 신뢰구간이 진짜로 의미하는 바와 흔한 오해를 정리하고 표본 평균에서 구간을 만드는 절차를 단계별로 보여 주는 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (6/10): 신뢰구간

통계 보고서에서 95% 신뢰구간이라는 표현은 자주 보이지만, 실제 의미는 자주 틀리게 읽힙니다. 많은 사람이 "이 구간 안에 참값이 있을 확률이 95%다"라고 이해하지만, 고전적 신뢰구간은 그런 문장을 직접 말하지 않습니다.

신뢰구간은 개별 구간 하나의 확률보다, 그 구간을 만들어 내는 절차의 성질을 설명합니다. 이 차이를 분명히 이해해야 신뢰수준, 유의수준, 효과 해석을 섞지 않게 됩니다.

이 글은 Statistics 101 시리즈의 6번째 글입니다. 여기서는 95% 신뢰구간의 정확한 뜻, 작은 표본에서 t-분포를 써야 하는 이유, 분포 가정이 약할 때 bootstrap이 어떤 대안이 되는지 정리하겠습니다.

![Statistics 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/06/06-01-concept-at-a-glance.ko.png)
*Statistics 101 6장 흐름 개요*
> 신뢰구간이 좁을수록 추정이 더 정확하고, 운영 결정도 더 분명해집니다.

## 이 글에서 다룰 문제

- 95% 신뢰구간은 정확히 무엇을 뜻할까요?
- 왜 같은 95%라도 작은 표본에서는 t-분포를 써야 할까요?
- 분포가 비대칭이면 어떤 방식으로 구간을 만들 수 있을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

신뢰구간은 불확실성을 가장 익숙한 형태로 보여 주는 도구입니다. 점 추정값 옆에 구간을 붙이면 숫자가 어느 정도 흔들릴 수 있는지 바로 읽을 수 있습니다. 그런데 해석을 잘못하면, 구간이 넓은 이유를 놓치거나, 0 포함 여부만 보고 성급한 결론을 내리게 됩니다.

실무에서는 A/B 테스트 결과, 회귀계수, 효과 크기 보고서에 신뢰구간이 거의 항상 따라옵니다. 구간의 폭은 데이터가 충분한지, 효과가 안정적인지, 추가 실험이 필요한지를 판단하는 근거가 됩니다.

## 멘탈 모델: 신뢰구간의 정확한 해석

신뢰구간은 표본에서 얻은 추정값과 표준오차, 그리고 임계값을 결합해 만듭니다. 표본이 작을수록 정규분포 대신 t-분포를 쓰는 이유는 꼬리를 조금 더 두껍게 잡아 불확실성을 더 보수적으로 반영하기 위해서입니다.

**95% 신뢰구간의 정확한 해석:** 같은 방식으로 표본을 반복해서 뽑아 구간을 만들면, 그중 약 95%가 참평균을 포함합니다.

이 해석은 개별 구간에 확률이 붙는 것이 아니라, 구간을 만드는 절차의 장기적 성공률이 95%라는 의미입니다.

### 신뢰수준별 z-값

| 신뢰수준 | z-값 | 용도 |
|---------|------|------|
| 90% | 1.645 | 초기 탐색, 빠른 추정 |
| 95% | 1.960 | 가장 흔한 표준, A/B 테스트 |
| 99% | 2.576 | 품질 관리, 높은 확신 필요 |

실무에서는 95%를 관례로 쓰지만, 오탐 비용이 클수록 99%로 올리고, 빠른 피드백이 중요할 때는 90%를 쓰기도 합니다.

## 신뢰구간 시뮬레이션: 반복 표집으로 직접 보기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
true_mean = 100
true_std = 20
n = 30
n_experiments = 50

fig, ax = plt.subplots(figsize=(10, 8))
coverage_count = 0

for i in range(n_experiments):
    sample = rng.normal(true_mean, true_std, n)
    mean = sample.mean()
    se = sample.std(ddof=1) / np.sqrt(n)
    ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)

    contains = ci[0] <= true_mean <= ci[1]
    coverage_count += contains

    color = "steelblue" if contains else "red"
    ax.plot([ci[0], ci[1]], [i, i], color=color, lw=1.5, alpha=0.7)
    ax.plot(mean, i, "o", color=color, ms=4)

ax.axvline(true_mean, color="black", lw=2, label=f"모평균: {true_mean}")
ax.set_xlabel("값")
ax.set_title(f"50회 반복 표집: {coverage_count}/50개 구간이 모평균 포함 (이론: 95%)")
ax.legend()
plt.tight_layout()
plt.show()

print(f"실제 포함 비율: {coverage_count}/{n_experiments} = {coverage_count/n_experiments:.1%}")
```

이 시뮬레이션은 신뢰구간의 핵심 아이디어를 눈으로 보여줍니다. 파란 구간은 모평균을 포함하고, 빨간 구간은 벗어났습니다. 장기적으로 약 95%가 파란 구간입니다.

## 파이썬으로 신뢰구간 계산하기

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)
sample = rng.normal(100, 15, size=50)
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
df = len(sample) - 1

# scipy로 신뢰구간 계산
ci_95 = stats.t.interval(0.95, df, loc=mean, scale=se)
ci_99 = stats.t.interval(0.99, df, loc=mean, scale=se)

print(f"표본평균: {mean:.2f}")
print(f"표준오차: {se:.3f}")
print(f"95% 신뢰구간: [{ci_95[0]:.2f}, {ci_95[1]:.2f}] (폭: {ci_95[1]-ci_95[0]:.2f})")
print(f"99% 신뢰구간: [{ci_99[0]:.2f}, {ci_99[1]:.2f}] (폭: {ci_99[1]-ci_99[0]:.2f})")
```

**예상 출력:**

```text
표본평균: 100.12
표준오차: 1.950
95% 신뢰구간: [96.20, 104.04] (폭: 7.84)
99% 신뢰구간: [94.89, 105.35] (폭: 10.46)
```

신뢰수준을 99%로 높이면 구간이 더 넓어집니다. 더 높은 확신을 얻으려면 더 넓은 범위를 허용해야 합니다.

## 표본 크기와 구간 폭의 관계

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
sizes = [10, 30, 120, 480, 1920]

print(f"{'n':>6} | {'구간 폭':>10} | {'SE':>8}")
print("-" * 30)
for n in sizes:
    sample = rng.normal(100, 15, size=n)
    mean = sample.mean()
    se = sample.std(ddof=1) / np.sqrt(n)
    ci = stats.t.interval(0.95, n-1, loc=mean, scale=se)
    width = ci[1] - ci[0]
    print(f"{n:>6} | {width:>10.2f} | {se:>8.3f}")
```

**예상 출력:**

```text
     n |    구간 폭 |       SE
------------------------------
    10 |      11.xx |    2.xxx
    30 |       5.xx |    1.xxx
   120 |       2.xx |    0.xxx
   480 |       1.xx |    0.xxx
  1920 |       0.xx |    0.xxx
```

표본을 4배씩 늘릴 때마다 구간 폭은 대략 절반으로 줄어듭니다. 이 관계는 실험 설계에서 필요한 표본 수를 계획할 때 중요한 기준이 됩니다.

## 부트스트랩 신뢰구간

분포 가정이 약하거나 비대칭 데이터에서는 부트스트랩이 좋은 대안입니다.

```python
import numpy as np
from scipy import stats
from numpy.random import default_rng

rng = default_rng(0)
# 비대칭 데이터 (지수분포)
sample = rng.exponential(scale=50, size=40)

# t-분포 기반 CI
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
ci_t = stats.t.interval(0.95, df=len(sample)-1, loc=mean, scale=se)

# 부트스트랩 CI
B = 5000
boots = [rng.choice(sample, len(sample), replace=True).mean() for _ in range(B)]
ci_boot = np.percentile(boots, [2.5, 97.5])

print(f"표본평균: {mean:.2f}")
print(f"t-분포 95% CI: [{ci_t[0]:.2f}, {ci_t[1]:.2f}]")
print(f"부트스트랩 95% CI: [{ci_boot[0]:.2f}, {ci_boot[1]:.2f}]")
```

정규 가정이 약한 상황에서는 bootstrap이 좋은 보완책이 됩니다. 두 방식의 결과가 비슷하면 현재 가정이 크게 무리하지 않았다는 신호로 볼 수 있습니다.

## 핵심 용어 정리

- **신뢰구간**: 같은 절차를 무한히 반복할 때 그중 일정 비율이 모수를 포함하도록 만든 구간입니다.
- **신뢰수준**: 95%, 99%처럼 절차의 적중률을 나타내는 값입니다.
- **오차한계**: 구간의 ± 폭입니다.
- **t-분포**: 작은 표본에서 쓰는, 꼬리가 조금 더 두꺼운 분포입니다.
- **Bootstrap**: 데이터를 재표집해 분포 가정 없이 구간을 만드는 방법입니다.

## 신뢰구간 해석의 흔한 오류

신뢰구간은 가장 많이 오독되는 통계 개념 중 하나입니다.

**오류 1: "모수가 이 구간 안에 있을 확률이 95%다"**
구간을 이미 만든 뒤에는 모수가 그 안에 있거나 없거나 둘 중 하나입니다. 확률은 절차의 성질에 붙습니다.

**오류 2: "95% 신뢰구간은 99% 신뢰구간보다 정확하다"**
신뢰수준을 높이면 구간 폭이 늘어납니다. 적중률을 더 보장하려면 더 넓은 범위를 잡아야 하기 때문입니다.

**오류 3: "구간이 좁으면 표본이 충분하다는 뜻이다"**
구간 폭은 표본 크기뿐 아니라 데이터 자체의 분산에도 의존합니다.

**오류 4: "0이 구간에 포함되면 효과가 없다"**
0 포함은 현재 데이터로는 효과를 확신할 수 없다는 뜻이지, 효과가 확실히 없다는 뜻이 아닙니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 개별 구간에 95% 확률 부여 | "이 구간에 참값이 있을 확률이 95%" | "절차의 95%가 참값을 포함" 이라고 수정 |
| n=10에서 z=1.96 사용 | 소표본에 정규 임계값 적용 | t-분포 임계값 사용 (자유도 n-1) |
| 신뢰수준과 유의수준 혼동 | "α=0.05이므로 95% CI" 기계적 연결 | 서로 연결되지만 다른 개념 |
| 비대칭 분포에 정규 근사만 사용 | 지수분포 데이터에 t-CI 적용 | 부트스트랩 CI 병행 |
| 0 포함 = 효과 없음 단정 | CI가 0을 포함하면 바로 효과 없다고 결론 | 데이터 부족 신호일 수 있음 |
| 구간 폭만 보고 모델 확정 | CI 좁음 = 좋은 추정 단정 | 편향 여부도 함께 확인 |

## 실습: 5단계 신뢰구간 구성

### 1단계 — 표본을 준비한다

```python
import numpy as np
rng = np.random.default_rng(42)
sample = rng.normal(100, 20, size=64)
```

### 2단계 — t 임계값을 구한다

```python
from scipy import stats
df = len(sample) - 1
t_crit = stats.t.ppf(0.975, df)
print(f"t* (df={df}): {t_crit:.3f}")
```

작은 표본일수록 이 임계값 선택이 중요합니다.

### 3단계 — 표준오차와 오차한계를 계산한다

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
moe = t_crit * se
print(f"SE: {se:.3f}, 오차한계: {moe:.3f}")
```

### 4단계 — 구간을 만든다

```python
mean = sample.mean()
print(f"95% CI: [{mean - moe:.2f}, {mean + moe:.2f}]")
```

### 5단계 — 부트스트랩 구간과 비교한다

```python
boots = [rng.choice(sample, len(sample), replace=True).mean() for _ in range(3000)]
print(f"Bootstrap CI: {np.percentile(boots, [2.5, 97.5])}")
```

## 신뢰구간과 가설검정의 관계

신뢰구간과 가설검정은 서로 다른 도구처럼 보이지만, 사실 깊이 연결되어 있습니다. 95% 신뢰구간이 특정 값을 포함하지 않으면, 그 값을 귀무가설로 하는 양측검정에서 p < 0.05가 나옵니다.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(5)
sample = rng.normal(105, 15, size=50)
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
df = len(sample) - 1

# 95% 신뢰구간
ci = stats.t.interval(0.95, df, loc=mean, scale=se)
print(f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")

# t-검정 (H0: μ = 100)
t_stat, p_value = stats.ttest_1samp(sample, 100)
print(f"t-통계량: {t_stat:.3f}")
print(f"p-value: {p_value:.4f}")

# 관계 확인
if 100 < ci[0] or 100 > ci[1]:
    print("→ 100이 CI 밖에 있음 → p < 0.05 예상 (일치)")
else:
    print("→ 100이 CI 안에 있음 → p > 0.05 예상 (일치)")
```

이 관계는 신뢰구간을 가설검정의 시각적 요약으로 볼 수 있게 합니다. 구간이 0을 포함하지 않으면 "차이가 없다"는 가설을 기각할 수 있다는 뜻입니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트 결과표, 회귀 분석 요약, 효과 크기 보고서에는 거의 항상 신뢰구간이 붙습니다. 값 하나보다 구간 폭이 더 많은 정보를 줄 때도 많습니다. 구간이 넓으면 불확실성이 크고, 추가 표본이나 더 나은 측정 설계가 필요하다는 뜻일 수 있습니다.

시니어 엔지니어는 신뢰구간을 볼 때 먼저 정확한 의미를 알고, 작은 표본에서는 t-분포와 bootstrap을 검토합니다. 그리고 구간 폭을 효과 크기와 함께 읽습니다. 넓은 구간은 조심스러운 판단을 요구하고, 좁은 구간은 실행 속도를 높여 줍니다.

## 운영 체크리스트

- [ ] 신뢰구간의 정확한 의미를 설명할 수 있습니다.
- [ ] 작은 표본에서 t-분포를 써야 하는 이유를 압니다.
- [ ] bootstrap의 용도를 설명할 수 있습니다.
- [ ] 구간 폭을 효과 크기와 함께 읽습니다.

## 연습 문제

1. 95% 구간과 99% 구간의 폭 차이를 시뮬레이션으로 비교해 보세요.
2. bootstrap 구간이 정규 근사 구간보다 나은 상황을 하나 적어 보세요.
3. "모평균이 이 구간 안에 있을 확률이 95%다"가 왜 틀린 문장인지 설명해 보세요.

## 정리와 다음 글

신뢰구간은 불확실성을 시각적으로 가장 잘 보여 주는 도구 중 하나입니다. 다만 그 의미를 확률 문장으로 단순 번역하면 쉽게 틀립니다. 신뢰수준은 절차의 적중률이고, 개별 구간은 그 절차가 만들어 낸 한 번의 결과라는 점을 기억하면 해석이 훨씬 안정됩니다.

다음 글에서는 가설검정을 다룹니다. 차이가 있는지 없는지를 묻는 표준 절차가 어떻게 돌아가는지, 그리고 p-value와 효과 크기를 함께 읽어야 하는 이유를 이어서 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- **Statistics 101 (6/10): 신뢰구간 (현재 글)**
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [scipy.stats — t and bootstrap](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [BMJ — Common Misconceptions of Confidence Intervals](https://www.bmj.com/content/322/7280/226)
- [Khan Academy — Confidence Intervals](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample)
- [Wikipedia — Bootstrap](https://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, ConfidenceInterval, Inference, Uncertainty, Beginner
