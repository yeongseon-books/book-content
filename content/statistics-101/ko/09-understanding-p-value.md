---
series: statistics-101
episode: 9
title: "Statistics 101 (9/10): p-value 이해하기"
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

# Statistics 101 (9/10): p-value 이해하기

통계 결과를 읽다 보면 p < 0.05라는 문장을 매우 자주 만납니다. 그런데 이 한 줄은 자주 과대해석됩니다. 어떤 사람은 가설이 참일 확률이라고 읽고, 어떤 사람은 효과의 크기라고 읽고, 어떤 사람은 0.05만 넘으면 효과가 전혀 없다고 받아들입니다.

p-value는 그렇게 많은 일을 대신해 주는 숫자가 아닙니다. 이 값은 오직 “귀무가설이 참이라고 가정할 때, 지금처럼 극단적인 데이터를 볼 가능성이 얼마나 작은가”를 말합니다.

이 글은 Statistics 101 시리즈의 9번째 글입니다. 여기서는 p-value의 정확한 정의, 자주 반복되는 오해, p-hacking이 왜 위험한지, 그리고 효과 크기와 신뢰구간을 함께 봐야 하는 이유를 정리하겠습니다.

![Statistics 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/09/09-01-concept-at-a-glance.ko.png)
*Statistics 101 9장 흐름 개요*
> p-value는 효과 크기가 아니고, 진실의 확률도 아닙니다. 단지 증거의 강도입니다.

## 먼저 던지는 질문

- p-value는 정확히 무엇을 뜻할까요?
- 왜 많은 사람이 p-value를 잘못 읽을까요?
- p-value와 효과 크기는 어떻게 다를까요?

## 왜 중요한가

논문, 실험 결과, 품질 보고서, A/B 테스트 결과표는 자주 p-value로 결론을 요약합니다. 문제는 이 숫자를 제대로 읽지 못하면 작은 효과를 큰 발견처럼 포장하거나, 반대로 데이터가 아직 부족한 상황을 효과 없음으로 오해할 수 있다는 사실입니다.

또 하나의 문제는 절차 오염입니다. 분석을 여러 번 반복해 보고, 유리한 구간만 고르고, 가설을 결과에 맞춰 바꾸면 p-value는 빠르게 의미를 잃습니다. 그래서 p-value는 계산식보다도 절차와 함께 이해해야 합니다.

## 멘탈 모델

p-value는 귀무가설이 참이라는 가정 아래 계산됩니다. 즉, “차이가 없다”는 세계에서 지금처럼 극단적인 결과를 볼 확률을 묻는 값입니다. 그러니 이 값은 가설의 진실도나 효과 크기를 대신하지 못합니다.

이 구조를 이해하면 p-value는 답이 아니라 질문의 시작이라는 말이 자연스럽게 받아들여집니다. 작은 p-value는 “왜 이런 데이터가 나왔을까?”를 묻는 신호입니다.

## 핵심 용어

- **p-value**: H0가 참이라고 가정할 때, 현재 관측값만큼 또는 그보다 더 극단적인 결과가 나올 확률입니다.
- **유의수준 α**: 기각 기준으로 미리 정한 문턱값입니다.
- **1종 오류**: H0가 참인데 기각하는 오류입니다.
- **p-hacking**: 원하는 p-value가 나올 때까지 분석을 반복하거나 바꾸는 행위입니다.
- 사전등록: 분석 전에 가설과 절차를 미리 공개하는 방식입니다.

## 유의확률 오해 모음

p-value는 통계에서 가장 많이 오해받는 개념입니다. 아래 표는 흔한 오해와 실제 의미를 정리합니다.

| 오해 | 실제 의미 |
|------|----------|
| p = P(H0가 참) | p는 H0가 참이라고 가정할 때, 현재 데이터만큼 극단적인 결과가 나올 확률입니다. |
| p-value가 작으면 효과가 크다 | p-value는 효과 크기가 아니라 증거의 강도입니다. 표본이 크면 작은 효과도 p가 작아질 수 있습니다. |
| p > 0.05면 효과가 없다 | p > 0.05는 현재 데이터로는 H0를 기각할 충분한 증거가 없다는 뜻이지, H0가 참이라는 증명이 아닙니다. |
| p = 0.05와 p = 0.051은 완전히 다르다 | 0.05는 관례일 뿐입니다. 실무에서는 p-value를 연속 스펙트럼으로 읽고, 효과 크기와 함께 판단합니다. |
| p-value가 작으면 재현 가능하다 | p-value는 한 번의 실험 결과입니다. 재현성은 같은 설계를 반복했을 때 일관성이 나오는지에 달려 있습니다. |

이 오해들은 대부분 p-value를 확률로 직역하려는 직관에서 나옵니다. p-value는 **조건부 확률**이라는 점을 기억하면 해석이 명확해집니다.
## 같은 유의확률 0.03도 해석 문장은 크게 다르다

이전 해석: “p=0.03이므로 H0가 참일 확률은 3%입니다.”

이 문장은 틀렸습니다. p-value는 가설의 참확률이 아닙니다.

이후 해석: “H0가 참이라면, 지금처럼 극단적인 데이터를 볼 확률은 3%입니다.”

표현이 비슷해 보여도 통계적으로는 전혀 다른 문장입니다. p-value는 가설 자체보다 데이터를 조건부로 읽는 수치입니다.

## 실습: 5단계 유의확률 읽기

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

### 5단계 — 선택적 분석 반복 위험을 시뮬레이션한다

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

## 파이썬 예제: 유의확률 계산 과정 보기

p-value는 scipy가 자동으로 계산해 주지만, 그 속을 한 번 들여다보면 개념이 더 선명해집니다.

```python
import numpy as np
from scipy import stats

# 데이터 준비
np.random.seed(42)
sample = np.random.normal(loc=105, scale=15, size=30)
mu0 = 100

# 1. t-통계량 계산
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
t_stat = (mean - mu0) / se

# 2. 자유도
df = len(sample) - 1

# 3. p-value (양측 검정)
p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

print(f"표본 평균: {mean:.2f}")
print(f"표준오차: {se:.2f}")
print(f"t-통계량: {t_stat:.3f}")
print(f"자유도: {df}")
print(f"p-value: {p_value:.4f}")

# scipy 결과와 비교
t_scipy, p_scipy = stats.ttest_1samp(sample, mu0)
print(f"\nscipy t: {t_scipy:.3f}, p: {p_scipy:.4f}")
```

**예상 출력:**

```
표본 평균: 105.xx
표준오차: 2.xx
t-통계량: 2.xxx
자유도: 29
p-value: 0.02xx

scipy t: 2.xxx, p: 0.02xx
```

이 계산 과정을 보면 p-value는 "표본 평균이 이렇게 멀리 떨어질 확률"을 t-분포의 꼬리 면적으로 구한 값이라는 게 보입니다. 표본 수가 늘거나 표준오차가 줄면 t-통계량이 커지고, p-value는 작아집니다.
## 자주 헷갈리는 지점 5가지

1. **p = P(H0가 참)**이라고 읽는 경우: 가장 대표적인 오해입니다.
2. **p-value를 효과 크기로 읽는 경우**: 작은 p가 큰 효과를 뜻하지는 않습니다.
3. **p > 0.05를 효과 없음으로 단정하는 경우**: 증거 부족일 수 있습니다.
4. **다중검정을 보정 없이 반복하는 경우**: 거짓 양성이 빠르게 늘어납니다.
5. **결과를 본 뒤 가설을 모양 바꾸는 경우**: p-hacking과 같은 문제로 이어집니다.

## 유의확률의 한계와 대안

p-value는 유용하지만, 그것만으로는 충분하지 않습니다. 최근 통계 커뮤니티는 p-value 중심 보고에서 벗어나 더 풍부한 정보를 함께 제공하자는 움직임을 보이고 있습니다.

### 한계

1. **효과 크기를 말하지 못함**: p-value는 차이가 있는지만 말하고, 그 차이가 큰지 작은지는 알려 주지 않습니다.
2. **표본 크기에 민감함**: n이 크면 실무적으로 무의미한 차이도 p < 0.05가 나올 수 있습니다.
3. **이분법적 판단 유도**: 0.049와 0.051을 극단적으로 다르게 해석하게 만듭니다.
4. **재현 위기**: p < 0.05를 발행 기준으로 삼으면 p-hacking과 발행 편향이 생깁니다.

### 대안 1: 효과 크기 (효과 크기)

효과 크기는 차이의 **실질적 크기**를 표준화된 척도로 나타냅니다. 대표적인 지표:

- **Cohen's d**: 두 그룹 평균 차이를 표준편차로 나눈 값. 0.2는 작음, 0.5는 중간, 0.8은 큼.
- **Pearson's r**: 상관 효과 크기. 0.1은 작음, 0.3은 중간, 0.5는 큼.
- **η² (eta-squared)**: ANOVA에서 설명 분산 비율.

```python
import numpy as np

# Cohen's d 계산
a = np.random.normal(50, 10, 100)
b = np.random.normal(53, 10, 100)

mean_diff = b.mean() - a.mean()
pooled_std = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

print(f"Cohen's d: {cohens_d:.3f}")
if abs(cohens_d) < 0.2:
    print("효과 크기: 작음")
elif abs(cohens_d) < 0.5:
    print("효과 크기: 중간")
else:
    print("효과 크기: 큼")
```

### 대안 2: 베이즈 팩터 (베이즈 팩터)

베이즈 팩터는 H1과 H0 중 어느 쪽이 데이터를 더 잘 설명하는지 비율로 나타냅니다. p-value와 달리 "H0가 얼마나 그럴듯한가"를 직접 말할 수 있습니다.

- BF > 10: H1을 강하게 지지
- BF = 1: 증거 없음
- BF < 0.1: H0를 강하게 지지

베이즈 팩터는 계산이 복잡하지만, `pingouin` 같은 라이브러리로 쉽게 구할 수 있습니다.

```python
# pingouin 설치 필요: pip install pingouin
import pingouin as pg
import pandas as pd

df = pd.DataFrame({'group': ['A']*50 + ['B']*50,
                   'value': list(np.random.normal(50, 10, 50)) + list(np.random.normal(53, 10, 50))})

# Bayesian t-test
result = pg.ttest(df[df['group']=='A']['value'], df[df['group']=='B']['value'], paired=False)
print(result[['T', 'p-val', 'BF10']])
```

베이즈 팩터는 p-value보다 해석이 직관적이지만, 사전분포 선택에 민감할 수 있습니다.

### 실무 권장 사항

- p-value 단독 보고 금지
- 효과 크기 + 신뢰구간 필수 포함
- 표본 수와 검정력 명시
- 다중비교 보정 적용
- 분석 계획 사전등록

2016년 미국통계학회(ASA)는 "p-value만으로 결론 내지 말 것"을 공식 성명으로 발표했습니다. 이제는 p-value를 하나의 참고 지표로만 쓰는 것이 표준입니다.
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

## 유의확률를 안전하게 쓰는 팀 규칙

p-value 자체보다 절차가 품질을 결정합니다. 아래 규칙을 팀 단위로 고정하면 p-hacking을 크게 줄일 수 있습니다.

### 권장 운영 규칙

1. 가설, 표본 수, 종료 조건을 실험 전 문서화합니다.
2. p-value 단독 보고를 금지하고 효과 크기와 구간을 필수로 포함합니다.
3. 동일 데이터셋에서 다중검정을 수행하면 보정을 적용합니다.
4. 중간 점검 횟수를 정하고 임의 중단을 금지합니다.
5. 재현 분석 스크립트와 시드를 함께 저장합니다.

### 다중비교 보정 예제

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

pvals = np.array([0.003, 0.021, 0.041, 0.074, 0.120])
rej_bonf, p_bonf, _, _ = multipletests(pvals, alpha=0.05, method='bonferroni')
rej_fdr, p_fdr, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')

print('원본 p값:', pvals)
print('Bonferroni 보정 p값:', p_bonf)
print('FDR 보정 p값:', p_fdr)
print('Bonferroni 기각 여부:', rej_bonf)
print('FDR 기각 여부:', rej_fdr)
```

비교 수가 많을수록 보정 전 p-value는 과도하게 낙관적일 수 있습니다. 분석 보고서에는 보정 방식과 선택 이유를 함께 기록해야 합니다.

## 추가 메모: 검증 가능한 의사결정 문장

분석 결과를 보고할 때는 "좋아 보입니다" 같은 모호한 문장을 피하고, 기준과 근거를 한 줄에 함께 적는 것이 좋습니다. 예를 들어 "전환율 +0.6%p, 95% 신뢰구간 +0.1~+1.1%p, p=0.014, 월간 기대효과 +320건, 2주 재검증 조건부 배포"처럼 쓰면 의사결정 책임이 명확해집니다. 이런 형식은 통계 도구가 바뀌어도 유지되는 팀 자산입니다.

## 처음 질문으로 돌아가기

- **p-value는 정확히 무엇을 뜻할까요?**
  - p-value는 귀무가설 하에서 현재 데이터만큼 극단적인 결과가 나올 확률입니다.
- **왜 많은 사람이 p-value를 잘못 읽을까요?**
  - p < 0.05는 관례이며, 상황에 따라 더 엄격하게(0.01) 또는 덜 엄격하게(0.10) 설정할 수 있습니다.
- **p-value와 효과 크기는 어떻게 다를까요?**
  - 운영에서는 p-value, 효과 크기, 신뢰구간을 모두 보고, 비즈니스 임팩트와 함께 판단합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- **p-value 이해하기 (현재 글)**
- 통계적 사고방식 (예정)

<!-- toc:end -->

## 참고 자료

- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Nature — Scientists rise up against statistical significance](https://www.nature.com/articles/d41586-019-00857-9)
- [scipy.stats — ttest_1samp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html)
- [NIST/SEMATECH e-Handbook — Hypothesis Tests](https://www.itl.nist.gov/div898/handbook/prc/section2/prc2.htm)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, PValue, Inference, Misconceptions, Beginner
