---
series: probability-101
episode: 5
title: 확률변수
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Probability
  - RandomVariable
  - Distribution
  - PMF
  - Beginner
seo_description: 확률변수의 정의와 이산 연속 구분, PMF 와 PDF 의 차이를 코드로 시각화하고 누적분포함수까지 정리한 확률 입문 글
last_reviewed: '2026-05-11'
---

# 확률변수

> Probability 101 시리즈 (5/10)


## 이 글에서 다룰 문제

확률변수가 있어야 기대값, 분산, 분포, 회귀 같은 수치 통계를 다룰 수 있습니다. ML 모델의 출력도 결국 확률변수로 볼 수 있습니다.

> *Random variables put numbers on outcomes.*

## 전체 흐름
```mermaid
flowchart LR
    Sample["Sample space"] --> RV["X: Omega -> R"]
    RV --> Discrete["Discrete: PMF"]
    RV --> Cont["Continuous: PDF"]
    Discrete --> CDF["CDF"]
    Cont --> CDF
```

## Before/After

**Before**: “주사위 결과” — 단순한 사건입니다.

**After**: X = 주사위 눈으로 두면 기대값 3.5, 분산 2.92 같은 수치 분석이 가능합니다.

## 5단계 확률변수

### 1단계 — 이산 확률변수

```python
import numpy as np
x = np.array([1, 2, 3, 4, 5, 6])
p = np.full(6, 1/6)  # PMF
print("sum p:", p.sum())
```

### 2단계 — CDF

```python
cdf = np.cumsum(p)
print("CDF:", cdf)
```

### 3단계 — 연속 확률변수 (정규)

```python
from scipy import stats
rv = stats.norm(loc=0, scale=1)
print("PDF at 0:", rv.pdf(0), "CDF at 0:", rv.cdf(0))
```

### 4단계 — 표본 추출

```python
import numpy as np
samples = np.random.default_rng(0).normal(0, 1, 10_000)
print("mean:", samples.mean(), "std:", samples.std())
```

### 5단계 — 확률 계산

```python
from scipy import stats
rv = stats.norm()
print("P(-1 <= X <= 1):", rv.cdf(1) - rv.cdf(-1))
```

## 이 코드에서 주목할 점

- PMF는 값마다 확률을 붙이고, PDF는 확률이 아니라 밀도를 나타냅니다.
- 연속 확률변수에서는 P(X = x) = 0입니다.
- CDF는 항상 정의됩니다.

## 자주 하는 실수 5가지

1. PDF 값을 확률로 해석합니다.
2. 이산과 연속을 혼동합니다.
3. PMF의 합이 1이 아닌데도 그대로 사용합니다.
4. CDF와 PDF를 혼동합니다.
5. 표본 통계를 모수로 단정합니다.

## 실무에서는 이렇게 쓰입니다

ML 모델 출력의 softmax 확률, 정규 노이즈 가정, 생존시간 분석처럼 확률변수는 모든 모델링의 기본입니다.

## 체크리스트

- [ ] 이산과 연속을 구분한다.
- [ ] PMF, PDF, CDF를 안다.
- [ ] scipy.stats로 분포를 다룬다.
- [ ] 표본 추출로 시뮬레이션한다.

## 정리 및 다음 단계

확률변수는 확률을 수치 분석으로 옮기는 다리입니다. 다음 글에서는 기대값과 분산을 봅니다.

<!-- toc:begin -->
- [확률이란 무엇인가?](./01-what-is-probability.md)
- [사건과 표본공간](./02-events-and-sample-space.md)
- [조건부확률](./03-conditional-probability.md)
- [베이즈 정리](./04-bayes-theorem.md)
- **확률변수 (현재 글)**
- 기대값과 분산 (예정)
- 이산분포 (예정)
- 연속분포 (예정)
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)
<!-- toc:end -->

## 참고 자료

- [Khan Academy — Random variables](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Random variable](https://en.wikipedia.org/wiki/Random_variable)
- [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, RandomVariable, Distribution, PMF, Beginner
