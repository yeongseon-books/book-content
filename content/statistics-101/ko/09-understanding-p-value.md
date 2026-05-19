---
series: statistics-101
episode: 9
title: p-value 이해하기
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
  - PValue
  - Inference
  - Misconceptions
  - Beginner
seo_description: p-value 의 정확한 정의와 자주 오해되는 다섯 가지 해석을 정리하고 p-hacking 을 피하는 실무 규칙을 다룬 입문 글
last_reviewed: '2026-05-12'
---

# p-value 이해하기

통계 결과를 읽다 보면 p < 0.05라는 문장을 매우 자주 만납니다. 그런데 이 한 줄은 자주 과대해석됩니다. 어떤 사람은 가설이 참일 확률이라고 읽고, 어떤 사람은 효과의 크기라고 읽고, 어떤 사람은 0.05만 넘으면 효과가 전혀 없다고 받아들입니다.

p-value는 그렇게 많은 일을 대신해 주는 숫자가 아닙니다. 이 값은 오직 “귀무가설이 참이라고 가정할 때, 지금처럼 극단적인 데이터를 볼 가능성이 얼마나 작은가”를 말합니다.

이 글은 Statistics 101 시리즈의 9번째 글입니다. 여기서는 p-value의 정확한 정의, 자주 반복되는 오해, p-hacking이 왜 위험한지, 그리고 효과 크기와 신뢰구간을 함께 봐야 하는 이유를 정리하겠습니다.

## 이 글에서 다룰 문제

- p-value는 정확히 무엇을 뜻할까요?
- 왜 많은 사람이 p-value를 잘못 읽을까요?
- p-value와 효과 크기는 어떻게 다를까요?
- 같은 데이터를 반복해서 들여다보면 왜 문제가 커질까요?

> p-value는 가설의 진실 확률이 아니라, 데이터가 얼마나 놀라운지를 보여 주는 숫자입니다.

## 왜 중요한가

논문, 실험 결과, 품질 보고서, A/B 테스트 결과표는 자주 p-value로 결론을 요약합니다. 문제는 이 숫자를 제대로 읽지 못하면 작은 효과를 큰 발견처럼 포장하거나, 반대로 데이터가 아직 부족한 상황을 효과 없음으로 오해할 수 있다는 점입니다.

또 하나의 문제는 절차 오염입니다. 분석을 여러 번 반복해 보고, 유리한 구간만 고르고, 가설을 결과에 맞춰 바꾸면 p-value는 빠르게 의미를 잃습니다. 그래서 p-value는 계산식보다도 절차와 함께 이해해야 합니다.

## 멘탈 모델

p-value는 귀무가설이 참이라는 가정 아래 계산됩니다. 즉, “차이가 없다”는 세계에서 지금처럼 극단적인 결과를 볼 확률을 묻는 값입니다. 그러니 이 값은 가설의 진실도나 효과 크기를 대신하지 못합니다.

![멘탈 모델](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/09/09-01-concept-at-a-glance.ko.png)

*p-value는 귀무가설 아래에서 관측 데이터가 얼마나 이례적인지 계산한 값입니다.*
이 구조를 이해하면 p-value는 답이 아니라 질문의 시작이라는 말이 자연스럽게 받아들여집니다. 작은 p-value는 “왜 이런 데이터가 나왔을까?”를 묻는 신호입니다.

## 핵심 용어

- **p-value**: H0가 참이라고 가정할 때, 현재 관측값만큼 또는 그보다 더 극단적인 결과가 나올 확률입니다.
- **유의수준 α**: 기각 기준으로 미리 정한 문턱값입니다.
- **1종 오류**: H0가 참인데 기각하는 오류입니다.
- **p-hacking**: 원하는 p-value가 나올 때까지 분석을 반복하거나 바꾸는 행위입니다.
- 사전등록: 분석 전에 가설과 절차를 미리 공개하는 방식입니다.

## 같은 p=0.03도 해석 문장은 크게 다르다

이전 해석: “p=0.03이므로 H0가 참일 확률은 3%입니다.”

이 문장은 틀렸습니다. p-value는 가설의 참확률이 아닙니다.

이후 해석: “H0가 참이라면, 지금처럼 극단적인 데이터를 볼 확률은 3%입니다.”

표현이 비슷해 보여도 통계적으로는 전혀 다른 문장입니다. p-value는 가설 자체보다 데이터를 조건부로 읽는 수치입니다.

## 실습: 5단계 p-value 읽기

### 1단계 — 가설을 정한다

```python
# H0: 평균 = 100, H1: 평균 != 100
mu0 = 100
```

### 2단계 — 데이터를 준비한다

```python
import numpy as np
rng = np.random.default_rng(0)
sample = rng.normal(102, 15, size=40)
```

### 3단계 — 검정을 실행한다

```python
from scipy import stats
t, p = stats.ttest_1samp(sample, mu0)
print("t:", t, "p:", p)
```

### 4단계 — 효과 크기를 계산한다

```python
import numpy as np
effect = (sample.mean() - mu0) / sample.std(ddof=1)
print("Cohen's d:", effect)
```

p-value와 별개로 차이의 크기를 읽는 단계입니다.

### 5단계 — p-hacking 위험을 시뮬레이션한다

```python
import numpy as np
from scipy import stats
hits = 0
for _ in range(20):
    x = np.random.default_rng().normal(100, 15, size=40)
    if stats.ttest_1samp(x, 100).pvalue < 0.05:
        hits += 1
print("False alarms in 20 looks:", hits)
```

같은 문제를 여러 번 들여다볼수록 우연한 유의성은 쉽게 늘어납니다.

## 이 코드에서 먼저 볼 점

- p-value는 데이터의 함수이지 가설의 참확률이 아닙니다.
- 표본 수가 크면 효과가 작아도 p가 작아질 수 있습니다.
- 같은 데이터를 여러 번 다시 분석하면 거짓 유의성이 누적됩니다.

## 자주 헷갈리는 지점 5가지

1. **p = P(H0가 참)**이라고 읽는 경우: 가장 대표적인 오해입니다.
2. **p-value를 효과 크기로 읽는 경우**: 작은 p가 큰 효과를 뜻하지는 않습니다.
3. **p > 0.05를 효과 없음으로 단정하는 경우**: 증거 부족일 수 있습니다.
4. **다중검정을 보정 없이 반복하는 경우**: 거짓 양성이 빠르게 늘어납니다.
5. **결과를 본 뒤 가설을 모양 바꾸는 경우**: p-hacking과 같은 문제로 이어집니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트, 임상시험, 품질 관리 보고서는 p-value를 자주 보여 줍니다. 하지만 실무에서는 p-value만으로 의사결정을 닫지 않습니다. 효과 크기와 신뢰구간을 함께 보고, 필요하면 다중비교 보정을 적용하고, 실험 설계 자체를 문서화합니다.

시니어 엔지니어는 p-value가 작아도 “의미 있는 크기의 효과인가”를 따로 묻습니다. 그리고 사전등록이나 실험 계획 문서처럼 절차를 먼저 고정해 p-hacking 여지를 줄입니다. 숫자 하나보다 절차의 신뢰성이 더 중요합니다.

## 체크리스트

- [ ] p-value를 정확히 정의할 수 있습니다.
- [ ] 유의수준과 1종 오류의 관계를 설명할 수 있습니다.
- [ ] p-hacking이 왜 위험한지 압니다.
- [ ] p-value와 효과 크기를 함께 보고합니다.

## 연습 문제

1. p=0.04와 p=0.06의 실무 차이를 어떻게 설명할지 적어 보세요.
2. 같은 데이터를 다섯 번 검정하면 거짓 양성 위험이 왜 커지는지 설명해 보세요.
3. 효과 크기는 아주 작은데 p-value는 작게 나온 상황을 어떻게 해석할지 써 보세요.

## 정리와 다음 글

p-value는 가설의 진실 여부를 단번에 판정하는 마법 숫자가 아닙니다. 이 값은 귀무가설 아래에서 현재 데이터가 얼마나 이례적인지를 보여 주는 지표일 뿐입니다. 그래서 효과 크기, 신뢰구간, 실험 설계와 함께 읽어야만 제대로 된 판단으로 이어집니다.

다음 글은 시리즈의 마지막 글로, 지금까지 배운 내용을 통계적 사고방식이라는 하나의 흐름으로 묶어 보겠습니다. 질문에서 데이터, 분포, 추정, 검정, 의사결정까지 어떻게 이어지는지 다시 정리할 차례입니다.

<!-- toc:begin -->
- [통계란 무엇인가?](./01-what-is-statistics.md)
- [평균, 중앙값, 분산](./02-mean-median-variance.md)
- [분포](./03-distributions.md)
- [표본과 모집단](./04-sample-and-population.md)
- [추정](./05-estimation.md)
- [신뢰구간](./06-confidence-interval.md)
- [가설검정](./07-hypothesis-testing.md)
- [상관과 회귀](./08-correlation-and-regression.md)
- **p-value 이해하기 (현재 글)**
- 통계적 사고방식 (예정)
<!-- toc:end -->

## 참고 자료

- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Nature — Scientists rise up against statistical significance](https://www.nature.com/articles/d41586-019-00857-9)
- [scipy.stats — ttest_1samp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html)
- [NIST/SEMATECH e-Handbook — Hypothesis Tests](https://www.itl.nist.gov/div898/handbook/prc/section2/prc2.htm)

Tags: Statistics, PValue, Inference, Misconceptions, Beginner
