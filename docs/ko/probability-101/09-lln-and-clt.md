---
series: probability-101
episode: 9
title: 대수의 법칙과 중심극한정리
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
  - LLN
  - CLT
  - Sampling
  - Beginner
seo_description: 대수의 법칙으로 표본평균이 모평균에 수렴하고 중심극한정리로 표본평균이 정규분포가 되는 흐름을 코드로 정리한 입문 글
last_reviewed: '2026-05-04'
---

# 대수의 법칙과 중심극한정리

> Probability 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *왜 정규분포가 도처에 있을까요*? *왜 평균* 은 *모평균* 에 수렴할까요?

> *통계의 두 기둥, *LLN* 과 *CLT*.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *대수의 법칙 (LLN)*
- *중심극한정리 (CLT)*
- *표본평균* 의 *분포*
- 5단계 LLN/CLT 실습
- 흔한 함정 5가지

## 왜 중요한가

*신뢰구간, 가설검정, A/B* 모두 *CLT* 위에 서 있습니다. *LLN* 이 없으면 *표본 통계* 가 *의미* 가 없습니다.

> *LLN gives accuracy; CLT gives shape.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Sample["i.i.d. samples"] --> Mean["Sample mean Xbar"]
    Mean --> LLN["LLN: Xbar -> mu"]
    Mean --> CLT["CLT: sqrt(n)(Xbar - mu) -> N(0, sigma^2)"]
```

## 핵심 용어 정리

- **i.i.d.**: 독립이고 동일한 분포.
- **표본평균 X̄**: (X₁+...+Xₙ)/n.
- **LLN**: *X̄ → μ* (n→∞).
- **CLT**: *√n·(X̄ - μ) → N(0, σ²)*.
- **표준오차 SE**: σ/√n.

## Before/After

**Before**: *“표본평균이 모평균과 같다.”* — *언제 왜* 모름.

**After**: *LLN* 이 *수렴* 을 보장; *CLT* 가 *오차의 분포* 를 알려줌.

## 실습: 5단계 LLN/CLT

### 1단계 — LLN 시뮬레이션

```python
import numpy as np
rng = np.random.default_rng(0)
samples = rng.uniform(0, 1, 10_000)
running = np.cumsum(samples) / np.arange(1, len(samples) + 1)
print("means at n=10, 100, 10_000:", running[9], running[99], running[-1])
```

### 2단계 — CLT 시뮬레이션

```python
import numpy as np
rng = np.random.default_rng(0)
means = [rng.exponential(1, 30).mean() for _ in range(10_000)]
print("mean ~ 1:", np.mean(means), "std ~ 1/sqrt(30):", np.std(means))
```

### 3단계 — 분포 시각화

```python
# 표본 평균의 히스토그램이 정규분포에 가까워 보입니다
import matplotlib.pyplot as plt
plt.hist(means, bins=40); plt.show()
```

### 4단계 — 표준오차

```python
import math
sigma = 1.0
n = 30
print("SE:", sigma / math.sqrt(n))
```

### 5단계 — 모집단 분포 무관성 확인

```python
import numpy as np
rng = np.random.default_rng(0)
# 비정규 모집단도 평균은 정규에 가까움
for dist in ["uniform", "exponential", "binomial"]:
    if dist == "uniform":
        s = rng.uniform(0, 1, (10_000, 30)).mean(axis=1)
    elif dist == "exponential":
        s = rng.exponential(1, (10_000, 30)).mean(axis=1)
    else:
        s = rng.binomial(10, 0.3, (10_000, 30)).mean(axis=1)
    print(dist, "mean of means:", round(s.mean(), 3))
```

## 이 코드에서 주목할 점

- *n* 이 클수록 *X̄* 의 *표준오차* 가 *1/√n* 으로 줄어든다.
- *모집단이 비정규* 여도 *표본평균* 은 *근사적으로 정규*.
- *CLT 는 합/평균* 에만 적용 — *최댓값* 에는 *EVT*.

## 자주 하는 실수 5가지

1. ***i.i.d.*** 가정 무시.
2. ***작은 n*** 에서 CLT 강요.
3. ***이상치/꼬리분포*** 무시.
4. ***표준편차 ≠ 표준오차*** 혼동.
5. ***LLN ≠ Gambler's fallacy*** 혼동.

## 실무에서는 이렇게 쓰입니다

A/B 의 *전환율 차이* 신뢰구간, 모니터링의 *평균 응답시간*, ML 의 *손실 평균* 모두 *CLT* 가 *근거* 입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *i.i.d.* 가정을 *검증* 한다.
- *n* 이 *충분한지* 묻는다.
- *꼬리* 가 두꺼우면 *부트스트랩* 을 쓴다.
- *표준오차* 를 항상 보고한다.
- *LLN* 의 *오해* 를 안다.

## 체크리스트

- [ ] *LLN* 의 의미를 안다.
- [ ] *CLT* 의 의미와 한계를 안다.
- [ ] *표준오차* 를 안다.
- [ ] *부트스트랩* 의 존재를 안다.

## 연습 문제

1. *n=4 vs n=400* 의 *SE* 차이를 계산하세요.
2. *지수분포* 평균이 *왜 정규* 가 되는지 시뮬레이션으로 확인하세요.
3. *Gambler's fallacy* 가 *LLN 의 오해* 인 이유를 적으세요.

## 정리 및 다음 단계

LLN 은 *수렴*, CLT 는 *형태* 를 보장합니다. 마지막 글에서는 이 모든 것을 *머신러닝의 확률* 로 묶습니다.

<!-- toc:begin -->
- [확률이란 무엇인가?](./01-what-is-probability.md)
- [사건과 표본공간](./02-events-and-sample-space.md)
- [조건부확률](./03-conditional-probability.md)
- [베이즈 정리](./04-bayes-theorem.md)
- [확률변수](./05-random-variables.md)
- [기대값과 분산](./06-expectation-and-variance.md)
- [이산분포](./07-discrete-distributions.md)
- [연속분포](./08-continuous-distributions.md)
- **대수의 법칙과 중심극한정리 (현재 글)**
- 머신러닝에서의 확률 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers)
- [Wikipedia — Central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [3Blue1Brown — CLT](https://www.youtube.com/watch?v=zeJD6dqJ5lo)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
