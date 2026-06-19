---
series: statistics-101
episode: 2
title: "Statistics 101 (2/10): 평균, 중앙값, 분산"
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
  - DescriptiveStats
  - Mean
  - Variance
  - Beginner
seo_description: 평균, 중앙값, 분산이 데이터의 어떤 면을 보여 주는지 비교하고 상황별로 어떤 요약 통계를 골라야 하는지 정리
last_reviewed: '2026-05-12'
---

# Statistics 101 (2/10): 평균, 중앙값, 분산

숫자가 많은 데이터를 한두 개 숫자로 줄이는 순간 해석의 방향이 정해집니다. 평균 하나만 적을지, 중앙값까지 함께 적을지, 퍼짐을 분산이나 표준편차로 설명할지에 따라 보고서의 문장이 달라집니다.

특히 데이터가 한쪽으로 길게 늘어지거나 극단값이 섞여 있으면 평균은 꽤 쉽게 흔들립니다. 그래서 요약 통계는 계산 공식보다 "어떤 질문에 어떤 숫자가 맞는가"를 먼저 판단해야 합니다.

이 글은 Statistics 101 시리즈의 2번째 글입니다. 여기서는 평균, 중앙값, 분산이 각각 무엇을 말하는지 비교하고, 왜 분포 모양에 따라 대표값 선택이 달라져야 하는지 정리하겠습니다.

![Statistics 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/02/02-01-concept-at-a-glance.ko.png)
*Statistics 101 2장 흐름 개요*
> 요약 통계는 맞는 숫자 하나를 찾는 작업이 아니라, 질문에 맞는 숫자를 고르는 판단 작업입니다.

## 이 글에서 다룰 문제

- 데이터를 대표하는 숫자로 평균과 중앙값 중 무엇을 써야 할까요?
- 분산과 표준편차는 평균이 말해 주지 못하는 무엇을 보완할까요?
- 극단값이 하나 섞였을 때 요약 통계는 어떻게 달라질까요?
- 파이썬으로 평균·중앙값·분산 계산할 때 실무에 적용할 때 주의할 점은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

사람은 수천 행의 원시 데이터를 직접 보고 판단하지 않습니다. 대시보드, 리포트, 실험 결과 페이지는 늘 몇 개의 숫자로 축약됩니다. 문제는 그 숫자가 데이터의 모양을 얼마나 잘 반영하느냐입니다.

예를 들어 사용자 결제 금액처럼 긴 꼬리를 가진 데이터에서 평균만 적으면, 대부분 사용자의 전형적인 행동과 멀어진 숫자가 대표값 자리를 차지할 수 있습니다. 반대로 공정한 분포에서 중앙값만 쓰면 평균이 주는 안정적인 정보를 버리게 됩니다. 요약 통계는 계산보다 선택이 더 중요합니다.

## 멘탈 모델: 중심과 퍼짐

데이터를 요약할 때는 중심과 퍼짐을 함께 봐야 합니다. 중심은 데이터가 어디에 몰려 있는지를, 퍼짐은 그 주변에서 얼마나 흔들리는지를 말합니다. 둘 중 하나만 보면 숫자의 성격을 절반만 읽게 됩니다.

평균과 중앙값은 중심을 설명하지만, 데이터 모양에 따라 신뢰할 만한 정도가 다릅니다. 분산, 표준편차, IQR은 퍼짐을 설명하며, 어느 지표를 붙이느냐에 따라 보고서가 말하는 위험 수준도 달라집니다.

### 평균, 중앙값, 최빈값 비교

| 지표 | 언제 쓰는가 | 이상치 민감도 | 예시 상황 |
|---|---|---|---|
| **평균** | 데이터가 대칭이고 이상치가 없을 때 | 높음 | 시험 점수, 센서 측정값 |
| **중앙값** | 긴 꼬리나 이상치가 있을 때 | 낮음 | 소득, 부동산 가격, 응답 시간 |
| **최빈값** | 범주형 데이터나 뚜렷한 봉우리가 있을 때 | 낮음 | 가장 인기 있는 상품, 가장 많은 요청 경로 |

같은 데이터셋이어도 평균, 중앙값, 최빈값은 서로 다른 이야기를 합니다. 평균은 전체 규모를 보여주지만 극단값에 휘둘리고, 중앙값은 중심 위치를 안정적으로 가리키며, 최빈값은 가장 전형적인 값이 무엇인지 보여줍니다.

## 분산과 표준편차의 직관

분산은 데이터가 평균에서 얼마나 떨어져 있는지를 제곱 거리로 평균 낸 값입니다. 제곱 단위이기 때문에 해석하기 어렵고, 그래서 제곱근을 씌운 표준편차를 더 자주 씁니다.

### 시험 점수 예제로 이해하기

반 평균이 70점이고 표준편차가 5점이라면, 대부분 학생은 65~75점 사이에 몰려 있다는 뜻입니다. 반면 표준편차가 20점이라면 점수가 넓게 퍼져 있어 평균 하나로 반 전체를 설명하기 어렵습니다.

```python
import numpy as np

# 두 반의 점수
class_a = np.array([68, 70, 69, 72, 71, 70, 69, 71, 70, 70])
class_b = np.array([50, 90, 60, 80, 70, 65, 75, 85, 55, 70])

print("A반 평균:", class_a.mean(), "표준편차:", class_a.std(ddof=1).round(2))
print("B반 평균:", class_b.mean(), "표준편차:", class_b.std(ddof=1).round(2))
```

**예상 출력:**

```text
A반 평균: 70.0 표준편차: 1.15
B반 평균: 70.0 표준편차: 13.33
```

두 반의 평균은 같지만 표준편차는 10배 이상 차이납니다. A반은 모두 비슷한 수준이고, B반은 상위권과 하위권이 섞여 있습니다. 평균만 보고 두 반이 비슷하다고 말하면 완전히 틀린 해석이 됩니다.

### 68-95-99.7 경험 법칙

정규분포를 따를 때 표준편차는 강력한 해석 도구가 됩니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
data = rng.normal(loc=100, scale=15, size=10000)

mean, std = data.mean(), data.std()

# 구간별 비율 계산
in_1sigma = np.sum((data >= mean - std) & (data <= mean + std)) / len(data)
in_2sigma = np.sum((data >= mean - 2*std) & (data <= mean + 2*std)) / len(data)
in_3sigma = np.sum((data >= mean - 3*std) & (data <= mean + 3*std)) / len(data)

print(f"평균: {mean:.1f}, 표준편차: {std:.1f}")
print(f"평균 ± 1σ 구간: {in_1sigma:.1%}")
print(f"평균 ± 2σ 구간: {in_2sigma:.1%}")
print(f"평균 ± 3σ 구간: {in_3sigma:.1%}")

# 시각화
fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(data, bins=60, density=True, alpha=0.6, color="steelblue", edgecolor="white")

x = np.linspace(mean - 4*std, mean + 4*std, 300)
ax.plot(x, stats.norm.pdf(x, mean, std), "k-", lw=2)

for i, (sigma, color) in enumerate([(1, "green"), (2, "orange"), (3, "red")], 1):
    ax.axvspan(mean - i*std, mean + i*std, alpha=0.1, color=color,
               label=f"±{i}σ ({[in_1sigma, in_2sigma, in_3sigma][i-1]:.1%})")

ax.set_xlabel("값")
ax.set_ylabel("밀도")
ax.set_title("정규분포와 표준편차 구간")
ax.legend()
plt.tight_layout()
plt.show()
```

**예상 출력:**

```text
평균: 100.0, 표준편차: 15.0
평균 ± 1σ 구간: 68.3%
평균 ± 2σ 구간: 95.4%
평균 ± 3σ 구간: 99.7%
```

이 규칙을 알면 표준편차만 보고도 데이터의 대략적인 범위를 머릿속으로 그릴 수 있습니다.

## 파이썬으로 평균·중앙값·분산 계산하기

```python
import numpy as np

data = np.array([10, 12, 11, 13, 12, 14, 11, 12, 5_000_000])

mean = np.mean(data)
median = np.median(data)
var = np.var(data, ddof=1)   # 표본 분산
std = np.std(data, ddof=1)   # 표본 표준편차

print(f"평균: {mean:.1f}")
print(f"중앙값: {median:.1f}")
print(f"분산: {var:.2e}")
print(f"표준편차: {std:.2e}")
```

**예상 출력:**

```text
평균: 555557.1
중앙값: 12.0
분산: 2.47e+12
표준편차: 1.57e+06
```

평균은 500만 근처로 튀었지만 중앙값은 12에 머물렀습니다. 이 경우 중앙값이 대부분 데이터의 중심을 훨씬 잘 설명합니다.

### 사분범위로 안정적인 퍼짐 측정하기

```python
import numpy as np

data = np.array([10, 12, 11, 13, 12, 14, 11, 12, 5_000_000])

q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1

print(f"Q1: {q1}, Q3: {q3}, IQR: {iqr}")
print(f"표준편차: {data.std(ddof=1):.1e}")
```

IQR은 가운데 50% 구간의 폭입니다. 극단값 하나 때문에 표준편차는 크게 뻥튀기되었지만, IQR은 대부분 데이터의 퍼짐을 그대로 보여줍니다. 긴 꼬리 데이터에서는 표준편차보다 IQR이 훨씬 안정적입니다.

### 절사평균으로 이상치 영향 줄이기

```python
import numpy as np
from scipy import stats

data = np.array([10, 12, 11, 13, 12, 14, 11, 12, 5_000_000])

mean = np.mean(data)
trimmed_mean = stats.trim_mean(data, proportiontocut=0.1)

print(f"평균: {mean:.1f}")
print(f"절사평균 (10% 제거): {trimmed_mean:.1f}")
print(f"중앙값: {np.median(data):.1f}")
```

절사평균은 극단값에 덜 민감하면서도 중앙값보다 더 많은 데이터를 활용합니다.

## 분포 시각화: 대표값 차이를 눈으로 확인하기

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 대칭 분포 (정규)
normal_data = rng.normal(100, 15, 1000)
axes[0].hist(normal_data, bins=40, edgecolor="white", alpha=0.7, color="steelblue")
axes[0].axvline(normal_data.mean(), color="red", lw=2, label=f"평균: {normal_data.mean():.1f}")
axes[0].axvline(np.median(normal_data), color="orange", lw=2, linestyle="--",
                label=f"중앙값: {np.median(normal_data):.1f}")
axes[0].set_title("대칭 분포: 평균 ≈ 중앙값")
axes[0].legend()

# 긴 꼬리 분포 (로그정규)
skewed_data = rng.lognormal(mean=4, sigma=1, size=1000)
axes[1].hist(skewed_data, bins=60, edgecolor="white", alpha=0.7, color="salmon")
axes[1].axvline(skewed_data.mean(), color="red", lw=2, label=f"평균: {skewed_data.mean():.0f}")
axes[1].axvline(np.median(skewed_data), color="orange", lw=2, linestyle="--",
                label=f"중앙값: {np.median(skewed_data):.0f}")
axes[1].set_title("긴 꼬리 분포: 평균 >> 중앙값")
axes[1].legend()

plt.tight_layout()
plt.show()
```

대칭 분포에서는 평균과 중앙값이 거의 같습니다. 긴 꼬리 분포에서는 극단값이 평균을 끌어올려 중앙값과 큰 차이가 납니다. 이 차이가 보이는 순간 어떤 대표값을 써야 할지 판단이 쉬워집니다.

## 핵심 용어 정리

- **평균**: 합계를 개수로 나눈 값입니다. 극단값에 민감합니다.
- **중앙값**: 정렬했을 때 가운데 놓인 값입니다. 극단값에 강합니다.
- **최빈값**: 가장 자주 등장하는 값입니다.
- **분산**: 평균에서 얼마나 떨어져 있는지를 제곱 거리로 평균 낸 값입니다.
- **표준편차**: 분산의 제곱근입니다. 데이터와 같은 단위를 가집니다.
- **IQR**: 3사분위수에서 1사분위수를 뺀 값으로, 가운데 50% 구간의 폭입니다.

## 같은 데이터도 대표값을 잘못 고르면 문장이 틀어진다

이전 해석: "우리 서비스의 평균 결제 금액은 50달러입니다."

문제는 소수의 고액 결제가 평균을 끌어올렸을 수 있다는 사실입니다. 이 경우 대부분 사용자는 50달러와 전혀 다른 행동을 하고 있을 수 있습니다.

이후 해석: "중앙값은 12달러이고 평균은 50달러입니다. 소수의 고액 결제가 포함된 긴 꼬리 분포이므로 대표값은 중앙값으로 읽는 편이 안전합니다."

같은 데이터라도 어떤 숫자를 내세우느냐에 따라 제품 가격 정책, 타깃 사용자 정의, KPI 해석이 모두 달라질 수 있습니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 평균만 보고 결정 | 평균 결제액 50달러로 가격 정책 수립 | 중앙값, IQR, 분위수 함께 확인 |
| 분산과 표준편차 혼동 | 단위 설명 없이 분산값 보고 | 표준편차는 원래 단위, 분산은 제곱 단위 명시 |
| 긴 꼬리에서 평균 사용 | 응답 시간 평균으로 SLA 관리 | p95, p99 분위수로 관리 기준 설정 |
| 표본 분산/모분산 혼동 | `np.var(data)` 사용 (모분산) | 표본 분산은 `np.var(data, ddof=1)` 사용 |
| 단위 생략 | "표준편차 24" 만 적음 | "표준편차 24ms" 처럼 단위 명시 |
| 이상치 원인 미확인 | 이상치를 바로 제거 | 원인 파악 후 제거 여부 결정 |

## 실습: 5단계 요약 통계

### 1단계 — 데이터를 준비한다

```python
import numpy as np
x = np.array([10, 12, 11, 13, 12, 14, 11, 12, 5_000_000])
```

작은 값이 모여 있고 극단값이 하나 섞인 데이터입니다.

### 2단계 — 평균과 중앙값을 같이 본다

```python
print("mean:", np.mean(x))
print("median:", np.median(x))
```

평균이 얼마나 끌려가는지 바로 드러납니다.

### 3단계 — 분산과 표준편차를 본다

```python
print("var:", np.var(x, ddof=1))
print("std:", np.std(x, ddof=1))
```

퍼짐이 매우 커졌다는 사실을 수치로 확인할 수 있습니다.

### 4단계 — 사분범위를 계산한다

```python
q1, q3 = np.percentile(x, [25, 75])
print("IQR:", q3 - q1)
```

가운데 50% 구간은 극단값 하나 때문에 크게 흔들리지 않습니다.

### 5단계 — 요약 문장을 쓴다

```text
중앙값: 12, IQR: 1.5 — 대부분 사용자는 12 근처에 있습니다.
평균: 555,557 (이상치 하나로 인한 왜곡).
결정: 대표값으로 중앙값을 사용합니다.
```

요약 통계는 숫자만 찍고 끝내지 말고, 어떤 값을 대표값으로 채택할지까지 적어야 합니다.

## 분위수 기반 요약: 운영 대시보드 패턴

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
latency = np.r_[rng.normal(120, 18, 9500), rng.normal(600, 120, 500)]

s = pd.Series(latency)
report = {
    "평균": s.mean(),
    "중앙값 (p50)": s.quantile(0.50),
    "p75": s.quantile(0.75),
    "p90": s.quantile(0.90),
    "p95": s.quantile(0.95),
    "p99": s.quantile(0.99),
    "IQR": s.quantile(0.75) - s.quantile(0.25),
}

for k, v in report.items():
    print(f"{k}: {v:.1f} ms")
```

평균은 꼬리 영향을 크게 받기 때문에 사용자 체감을 과소평가할 수 있습니다. 반면 중앙값과 분위수는 체감 품질을 더 직접적으로 보여줍니다. Datadog, Grafana 같은 모니터링 도구가 평균보다 p95/p99를 강조하는 이유입니다.

## 실무에서는 이렇게 읽습니다

매출, 응답 시간, 광고비, 주문 금액은 긴 꼬리를 가지는 경우가 많습니다. 그래서 실무 대시보드에서는 평균 하나보다 중앙값, p95, p99 같은 지표가 더 자주 쓰입니다. 평균은 전체 규모를 보여 주지만, 사용자 체감이나 운영 위험은 분위수 계열이 더 잘 드러내는 경우가 많기 때문입니다.

시니어 엔지니어는 먼저 분포를 그려 보고, 평균 옆에 중앙값과 분위수를 붙입니다. 그리고 왜 극단값이 생겼는지 원인을 따로 봅니다. 좋은 요약 통계는 멋진 숫자 하나가 아니라, 질문에 맞는 짧은 조합입니다.

## 운영 체크리스트

- [ ] 평균과 중앙값의 차이를 설명할 수 있습니다.
- [ ] 분산, 표준편차, IQR의 역할을 구분할 수 있습니다.
- [ ] 긴 꼬리 분포에서는 중앙값을 우선 검토합니다.
- [ ] 보고서에 단위를 함께 적습니다.

## 연습 문제

1. 지난 30일 공부 시간을 기준으로 평균과 중앙값을 각각 계산해 보세요.
2. 긴 꼬리 분포에서 평균이 위험한 이유를 한 문장으로 적어 보세요.
3. IQR과 표준편차가 어떤 상황에서 다른 판단을 줄 수 있는지 설명해 보세요.

## 정리와 다음 글

평균, 중앙값, 분산은 모두 데이터를 요약하지만, 같은 역할을 하지 않습니다. 중심을 말할지, 퍼짐을 말할지, 극단값에 강한 지표가 필요한지에 따라 선택이 달라져야 합니다. 요약 통계는 계산한 숫자보다 왜 그 숫자를 골랐는지가 더 중요합니다.

다음 글에서는 대표값보다 한 단계 더 바깥으로 나가서 데이터의 전체 모양을 다루는 분포를 봅니다. 평균이 같아도 왜 전혀 다른 행동을 보일 수 있는지 그 이유가 분포에 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- **Statistics 101 (2/10): 평균, 중앙값, 분산 (현재 글)**
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [NIST/SEMATECH e-Handbook of Statistical Methods](https://www.itl.nist.gov/div898/handbook/)
- [pandas — describe()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html)
- [Wikipedia — Robust Statistics](https://en.wikipedia.org/wiki/Robust_statistics)
- [Khan Academy — Summary Statistics](https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, DescriptiveStats, Mean, Variance, Beginner
