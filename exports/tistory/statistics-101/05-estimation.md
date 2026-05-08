
# 추정

> Statistics 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *표본 평균* 으로 *모평균* 을 *추정* 한다는 건 *얼마나 정확* 한 일일까요? *오차* 는 어떻게 적어야 할까요?

> *추정은 *값* 이 아니라 *값과 오차* 의 *짝* 이다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *점 추정* vs *구간 추정*
- *표준오차 (SE)* 의 의미
- *불편 추정량* 과 *일치성*
- 5단계 추정 실습
- 흔한 함정 5가지

## 왜 중요한가

*평균을 보고했다* 가 끝이 아닙니다. *얼마나 가까운지* 를 *함께 적어야* 의사결정자가 *위험* 을 평가할 수 있습니다.

> *추정값에는 *오차* 가 항상 따라온다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Sample["Sample x̄"] --> Estimate["Point Estimate"]
    Sample --> SE["Standard Error"]
    Estimate --> Interval["Interval Estimate"]
    SE --> Interval
```

## 핵심 용어 정리

- **Point Estimate**: 모수에 대한 *단일 값* 추정 (x̄).
- **Interval Estimate**: 모수가 들어 있을 *범위*.
- **Standard Error (SE)**: 추정량의 *표준편차* — 보통 s/√n.
- **Unbiased Estimator**: *기댓값* 이 *모수* 와 같음.
- **Consistent Estimator**: 표본이 클수록 *모수에 수렴*.

## Before/After

**Before**: *“표본 평균은 100”* — 얼마나 신뢰할 수 있는지 알 수 없음.

**After**: *“x̄ = 100, SE = 2.5 (n=64). 모평균은 95% 구간 [95.1, 104.9].”*

## 실습: 5단계 추정

### 1단계 — 표본 준비

```python
import numpy as np
sample = np.random.normal(loc=100, scale=20, size=64)
```

### 2단계 — 점 추정

```python
mean = sample.mean()
print("x̄:", mean)
```

### 3단계 — 표준오차

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
print("SE:", se)
```

### 4단계 — 95% 구간

```python
lower, upper = mean - 1.96 * se, mean + 1.96 * se
print(f"95% CI: [{lower:.1f}, {upper:.1f}]")
```

### 5단계 — 보고

```text
x̄ = 99.8 (n=64), SE = 2.4
95% CI: [95.1, 104.5]
```

## 이 코드에서 주목할 점

- *SE = s/√n* — *표본이 클수록* 작아진다.
- *95% CI* 는 *±1.96 × SE*.
- 추정값은 *항상 SE* 와 *함께* 보고.

## 자주 하는 실수 5가지

1. ***표준편차* 를 *SE* 로 *혼동*.**
2. ***N* 을 늘리면 *오차가 0* 이 된다고 *오해*.**
3. ***점 추정* 만 *보고* 한다.**
4. ***작은 표본* 에 *정규* 가정.** *t-distribution* 이 필요.
5. ***편향된 표본* 으로 *불편 추정량* 을 만든다.**

## 실무에서는 이렇게 쓰입니다

A/B 테스트의 *전환율 추정*, 매출 *월간 평균*, 응답 시간 *p95 추정* 등 모든 *대시보드 숫자* 는 *추정* 입니다. *오차 막대* 와 *신뢰구간* 으로 표현됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *추정값* 옆에 *SE* 를 *항상* 붙인다.
- *N* 을 *통계적으로* 정한다 (power analysis).
- *작은 표본* 에는 *t-distribution* 을 쓴다.
- *편향* 을 *먼저* 점검한다.
- *보고서* 에 *오차* 를 *숨기지 않는다*.

## 체크리스트

- [ ] *점 추정* 과 *구간 추정* 의 차이를 안다.
- [ ] *SE* 를 계산할 줄 안다.
- [ ] *95% CI* 를 만들 수 있다.
- [ ] *N* 의 영향을 이해한다.

## 연습 문제

1. *N=10* 과 *N=1000* 의 *SE* 차이를 비교해 보세요.
2. *불편 추정량* 의 의미를 한 문장으로 설명하세요.
3. *모평균이 100* 인지 어떻게 판단할지 *추정 과정* 을 적어 보세요.

## 정리 및 다음 단계

추정은 *불확실성을 수치로* 적는 일입니다. 다음 글에서는 *95% CI* 의 *진짜 의미* 를 자세히 봅니다.

- [통계란 무엇인가?](./01-what-is-statistics.md)
- [평균, 중앙값, 분산](./02-mean-median-variance.md)
- [분포](./03-distributions.md)
- [표본과 모집단](./04-sample-and-population.md)
- **추정 (현재 글)**
- 신뢰구간 (예정)
- 가설검정 (예정)
- 상관과 회귀 (예정)
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)
## 참고 자료

- [scipy.stats — Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Estimation](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample)
- [Wikipedia — Standard Error](https://en.wikipedia.org/wiki/Standard_error)
- [NIST — Estimation Methods](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35.htm)

Tags: Statistics, Estimation, Inference, PointEstimate, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
