---
series: statistics-101
episode: 6
title: 신뢰구간
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
last_reviewed: '2026-05-04'
---

# 신뢰구간

> Statistics 101 시리즈 (6/10)


## 이 글에서 다룰 문제

*신뢰구간* 은 *불확실성을 보여 주는 가장 흔한 도구* 입니다. 그러나 *오해* 도 가장 흔합니다. *정확한 의미* 를 알아야 *정확한 결정* 을 만듭니다.

> *95% CI는 *방법* 의 *적중률* 이지, *이번* 의 확률이 아니다.*

## 전체 흐름
```mermaid
flowchart LR
    Sample["Sample"] --> SE["Standard Error"]
    SE --> Critical["t / z critical value"]
    Critical --> CI["Confidence Interval"]
```

## Before/After

**Before**: *“95% 확률로 평균이 95~105 사이”* — 흔한 오해.

**After**: *“같은 방법으로 100번 추정하면 약 95번이 95~105를 포함.”*

## 5단계 CI

### 1단계 — 표본

```python
import numpy as np
sample = np.random.normal(100, 20, size=64)
```

### 2단계 — t-임계값

```python
from scipy import stats
df = len(sample) - 1
t_crit = stats.t.ppf(0.975, df)
print("t*:", t_crit)
```

### 3단계 — SE & MoE

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
moe = t_crit * se
```

### 4단계 — 구간

```python
mean = sample.mean()
print(f"95% CI: [{mean - moe:.2f}, {mean + moe:.2f}]")
```

### 5단계 — 부트스트랩

```python
from numpy.random import default_rng
rng = default_rng(0)
boots = [rng.choice(sample, len(sample), replace=True).mean() for _ in range(2000)]
print("Bootstrap CI:", np.percentile(boots, [2.5, 97.5]))
```

## 이 코드에서 주목할 점

- *작은 표본* 에는 *t-distribution*.
- *Bootstrap* 은 *분포 가정* 없이도 작동.
- 두 결과가 *비슷할수록* 가정이 *적절* 했다.

## 자주 하는 실수 5가지

1. ***이번 구간* 에 *95% 확률* 이 있다고 *오해*.**
2. ***N=10* 에 *z=1.96* 사용. *t* 가 필요.**
3. ***신뢰수준* 을 *유의수준* 과 *혼동*.**
4. ***부트스트랩* 없이 *왜곡* 된 분포에 정규 CI.**
5. ***CI 가 0* 을 포함하면 *효과 없음* 이라고 *단정*.**

## 실무에서는 이렇게 쓰입니다

A/B 테스트 결과, 회귀계수, 효과 크기 — *모든 추론 보고서* 에 *CI 가 함께* 적힙니다. *대시보드 오차 막대* 도 *신뢰구간* 의 시각화입니다.

## 체크리스트

- [ ] *CI 의 정확한 의미* 를 안다.
- [ ] *t-distribution* 을 쓸 줄 안다.
- [ ] *부트스트랩* 을 안다.
- [ ] *신뢰수준* 을 *상황* 에 맞춰 고른다.

## 정리 및 다음 단계

신뢰구간은 *불확실성을 시각화* 하는 도구입니다. 다음 글에서는 *가설검정* 으로 *차이가 있는지* 묻는 방법을 배웁니다.

<!-- toc:begin -->
- [통계란 무엇인가?](./01-what-is-statistics.md)
- [평균, 중앙값, 분산](./02-mean-median-variance.md)
- [분포](./03-distributions.md)
- [표본과 모집단](./04-sample-and-population.md)
- [추정](./05-estimation.md)
- **신뢰구간 (현재 글)**
- 가설검정 (예정)
- 상관과 회귀 (예정)
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)
<!-- toc:end -->

## 참고 자료

- [scipy.stats — t and bootstrap](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [BMJ — Common Misconceptions of Confidence Intervals](https://www.bmj.com/content/322/7280/226)
- [Khan Academy — Confidence Intervals](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample)
- [Wikipedia — Bootstrap](https://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29)
