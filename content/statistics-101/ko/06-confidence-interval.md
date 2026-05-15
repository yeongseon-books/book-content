---
series: statistics-101
episode: 6
title: 신뢰구간
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

# 신뢰구간

통계 보고서에서 95% 신뢰구간이라는 표현은 자주 보이지만, 실제 의미는 자주 틀리게 읽힙니다. 많은 사람이 “이 구간 안에 참값이 있을 확률이 95%다”라고 이해하지만, 고전적 신뢰구간은 그런 문장을 직접 말하지 않습니다.

신뢰구간은 개별 구간 하나의 확률보다, 그 구간을 만들어 내는 절차의 성질을 설명합니다. 이 차이를 분명히 이해해야 신뢰수준, 유의수준, 효과 해석을 섞지 않게 됩니다.

이 글은 Statistics 101 시리즈의 6번째 글입니다. 여기서는 95% 신뢰구간의 정확한 뜻, 작은 표본에서 t-분포를 써야 하는 이유, 분포 가정이 약할 때 bootstrap이 어떤 대안이 되는지 정리하겠습니다.

## 이 글에서 다룰 문제

- 95% 신뢰구간은 정확히 무엇을 뜻할까요?
- 왜 같은 95%라도 작은 표본에서는 t-분포를 써야 할까요?
- 분포가 비대칭이면 어떤 방식으로 구간을 만들 수 있을까요?
- 신뢰구간이 0을 포함한다고 해서 무엇을 바로 말할 수 있을까요?

> 신뢰는 개별 구간이 아니라 구간을 만드는 절차의 적중률에 붙는 말입니다.

## 왜 중요한가

신뢰구간은 불확실성을 가장 익숙한 형태로 보여 주는 도구입니다. 점 추정값 옆에 구간을 붙이면 숫자가 어느 정도 흔들릴 수 있는지 바로 읽을 수 있습니다. 그런데 해석을 잘못하면, 구간이 넓은 이유를 놓치거나, 0 포함 여부만 보고 성급한 결론을 내리게 됩니다.

실무에서는 A/B 테스트 결과, 회귀계수, 효과 크기 보고서에 신뢰구간이 거의 항상 따라옵니다. 구간의 폭은 데이터가 충분한지, 효과가 안정적인지, 추가 실험이 필요한지를 판단하는 근거가 됩니다.

## 멘탈 모델

신뢰구간은 표본에서 얻은 추정값과 표준오차, 그리고 임계값을 결합해 만듭니다. 표본이 작을수록 정규분포 대신 t-분포를 쓰는 이유는 꼬리를 조금 더 두껍게 잡아 불확실성을 더 보수적으로 반영하기 위해서입니다.

```mermaid
flowchart LR
    Sample["Sample"] --> SE["Standard Error"]
    SE --> Critical["t / z critical value"]
    Critical --> CI["Confidence Interval"]
```

같은 데이터라도 어떤 방법으로 구간을 만들었는지에 따라 결과가 조금 달라질 수 있습니다. 그래서 신뢰구간은 숫자 자체보다 절차를 함께 이해해야 합니다.

## 핵심 용어

- 신뢰구간: 같은 절차를 무한히 반복할 때 그중 일정 비율이 모수를 포함하도록 만든 구간입니다.
- 신뢰수준: 95%, 99%처럼 절차의 적중률을 나타내는 값입니다.
- 오차한계: 구간의 ± 폭입니다.
- **t-분포**: 작은 표본에서 쓰는, 꼬리가 조금 더 두꺼운 분포입니다.
- **Bootstrap**: 데이터를 재표집해 분포 가정 없이 구간을 만드는 방법입니다.

## 같은 95%라도 읽는 문장이 달라져야 한다

이전 해석: “모평균이 95와 105 사이에 있을 확률이 95%입니다.”

이 문장은 고전적 신뢰구간 해석으로는 맞지 않습니다. 이미 구간을 만들고 나면 모수는 그 안에 있거나 없거나 둘 중 하나입니다.

이후 해석: “같은 방식으로 표본을 반복해서 뽑아 구간을 만들면, 그중 약 95%가 참평균을 포함합니다.”

표현이 덜 직관적으로 보일 수 있지만, 이쪽이 통계적으로 정확한 문장입니다.

## 실습: 5단계 CI 구성

### 1단계 — 표본을 준비한다

```python
import numpy as np
sample = np.random.normal(100, 20, size=64)
```

### 2단계 — t 임계값을 구한다

```python
from scipy import stats
df = len(sample) - 1
t_crit = stats.t.ppf(0.975, df)
print("t*:", t_crit)
```

작은 표본일수록 이 임계값 선택이 중요합니다.

### 3단계 — 표준오차와 오차한계를 계산한다

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
moe = t_crit * se
```

### 4단계 — 구간을 만든다

```python
mean = sample.mean()
print(f"95% CI: [{mean - moe:.2f}, {mean + moe:.2f}]")
```

### 5단계 — bootstrap 구간과 비교한다

```python
from numpy.random import default_rng
rng = default_rng(0)
boots = [rng.choice(sample, len(sample), replace=True).mean() for _ in range(2000)]
print("Bootstrap CI:", np.percentile(boots, [2.5, 97.5]))
```

정규 가정이 약한 상황에서는 bootstrap이 좋은 보완책이 됩니다.

## 이 코드에서 먼저 볼 점

- 작은 표본에서는 t-분포를 쓰는 편이 안전합니다.
- bootstrap은 분포 가정이 약할 때 유용합니다.
- 두 방식의 결과가 비슷하면 현재 가정이 크게 무리하지 않았다는 신호로 볼 수 있습니다.

## 자주 헷갈리는 지점 5가지

1. **개별 신뢰구간에 95% 확률을 붙이는 경우**: 신뢰는 절차의 적중률에 붙습니다.
2. **N=10인데 z=1.96을 그대로 쓰는 경우**: t-분포를 먼저 검토해야 합니다.
3. **신뢰수준과 유의수준을 섞는 경우**: 서로 연결되지만 같은 개념은 아닙니다.
4. **비대칭 분포에 정규 근사 구간만 쓰는 경우**: bootstrap이 더 자연스러울 수 있습니다.
5. **구간이 0을 포함하면 효과가 전혀 없다고 단정하는 경우**: 데이터가 아직 부족하다는 뜻일 수도 있습니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트 결과표, 회귀 분석 요약, 효과 크기 보고서에는 거의 항상 신뢰구간이 붙습니다. 값 하나보다 구간 폭이 더 많은 정보를 줄 때도 많습니다. 구간이 넓으면 불확실성이 크고, 추가 표본이나 더 나은 측정 설계가 필요하다는 뜻일 수 있습니다.

시니어 엔지니어는 신뢰구간을 볼 때 먼저 정확한 의미를 알고, 작은 표본에서는 t-분포와 bootstrap을 검토합니다. 그리고 구간 폭을 효과 크기와 함께 읽습니다. 넓은 구간은 조심스러운 판단을 요구하고, 좁은 구간은 실행 속도를 높여 줍니다.

## 체크리스트

- [ ] 신뢰구간의 정확한 의미를 설명할 수 있습니다.
- [ ] 작은 표본에서 t-분포를 써야 하는 이유를 압니다.
- [ ] bootstrap의 용도를 설명할 수 있습니다.
- [ ] 구간 폭을 효과 크기와 함께 읽습니다.

## 연습 문제

1. 95% 구간과 99% 구간의 폭 차이를 시뮬레이션으로 비교해 보세요.
2. bootstrap 구간이 정규 근사 구간보다 나은 상황을 하나 적어 보세요.
3. “모평균이 이 구간 안에 있을 확률이 95%다”가 왜 틀린 문장인지 설명해 보세요.

## 정리와 다음 글

신뢰구간은 불확실성을 시각적으로 가장 잘 보여 주는 도구 중 하나입니다. 다만 그 의미를 확률 문장으로 단순 번역하면 쉽게 틀립니다. 신뢰수준은 절차의 적중률이고, 개별 구간은 그 절차가 만들어 낸 한 번의 결과라는 점을 기억하면 해석이 훨씬 안정됩니다.

다음 글에서는 가설검정을 다룹니다. 차이가 있는지 없는지를 묻는 표준 절차가 어떻게 돌아가는지, 그리고 p-value와 효과 크기를 함께 읽어야 하는 이유를 이어서 보겠습니다.

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

Tags: Statistics, ConfidenceInterval, Inference, Uncertainty, Beginner
