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

이 그림에서는 대수의 법칙과 중심극한정리를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 대수의 법칙과 중심극한정리의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

두 정리는 같은 말을 반복하지 않습니다. 하나는 목적지, 다른 하나는 오차의 모양을 말합니다.

## 평균이 믿을 만해지는 이유

“표본평균은 결국 모평균 근처로 간다”는 믿음은 대수의 법칙에서 옵니다. 하지만 얼마나 흔들리는지, 그 흔들림이 어느 정도 정규처럼 보이는지는 중심극한정리가 설명합니다. 그래서 둘은 함께 봐야 합니다.

특히 중심극한정리를 이해하면 정규분포가 왜 통계 전반에서 자주 나타나는지도 설명할 수 있습니다. 원래 모집단이 정규가 아니어도 평균은 정규에 가까워질 수 있기 때문입니다.

## 5단계로 보는 대수의 법칙과 중심극한정리

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

## 이 코드에서 먼저 봐야 할 점

- 표본 수가 커질수록 평균의 흔들림은 줄어듭니다.
- 비정규 모집단에서도 표본평균은 정규에 가까워질 수 있습니다.
- 중심극한정리는 평균과 합에 대한 이야기입니다.
- 표준오차는 표준편차와 다른 양입니다.

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

- [ ] 대수의 법칙과 중심극한정리의 차이를 설명할 수 있습니다.
- [ ] 표준오차의 뜻을 설명할 수 있습니다.
- [ ] 비정규 모집단에서도 평균이 정규에 가까워질 수 있음을 압니다.
- [ ] CLT를 조심해서 써야 하는 상황을 말할 수 있습니다.

## 정리

대수의 법칙은 평균이 어디로 가는지 말하고, 중심극한정리는 그 평균이 어떻게 흔들리는지 말합니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 표본 수가 커질수록 평균은 안정된다는 점, 평균의 오차는 정규근사로 다룰 수 있는 경우가 많다는 점, 그리고 이 모든 해석에는 i.i.d.와 표본 크기 같은 전제가 붙는다는 점입니다.

다음 글에서는 머신러닝에서의 확률을 다룹니다. 이번 글이 통계적 평균의 힘을 설명했다면, 다음 글은 지금까지 배운 확률 개념이 실제 ML 시스템 안에서 어디에 숨어 있는지 연결해 줍니다.

## 처음 질문으로 돌아가기

- **표본평균은 왜 표본 수가 커질수록 안정될까요?**
  - 본문의 기준은 대수의 법칙과 중심극한정리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **대수의 법칙과 중심극한정리는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **표준오차는 표준편차와 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
