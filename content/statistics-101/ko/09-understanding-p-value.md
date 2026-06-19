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

p-value는 그렇게 많은 일을 대신해 주는 숫자가 아닙니다. 이 값은 오직 "귀무가설이 참이라고 가정할 때, 지금처럼 극단적인 데이터를 볼 가능성이 얼마나 작은가"를 말합니다.

이 글은 Statistics 101 시리즈의 9번째 글입니다. 여기서는 p-value의 정확한 정의, 자주 반복되는 오해, p-hacking이 왜 위험한지, 그리고 효과 크기와 신뢰구간을 함께 봐야 하는 이유를 정리하겠습니다.

![Statistics 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/09/09-01-concept-at-a-glance.ko.png)
*Statistics 101 9장 흐름 개요*
> p-value는 효과 크기가 아니고, 진실의 확률도 아닙니다. 단지 증거의 강도입니다.

## 이 글에서 다룰 문제

- p-value는 정확히 무엇을 뜻할까요?
- 왜 많은 사람이 p-value를 잘못 읽을까요?
- p-value와 효과 크기는 어떻게 다를까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

논문, 실험 결과, 품질 보고서, A/B 테스트 결과표는 자주 p-value로 결론을 요약합니다. 문제는 이 숫자를 제대로 읽지 못하면 작은 효과를 큰 발견처럼 포장하거나, 반대로 데이터가 아직 부족한 상황을 효과 없음으로 오해할 수 있다는 사실입니다.

또 하나의 문제는 절차 오염입니다. 분석을 여러 번 반복해 보고, 유리한 구간만 고르고, 가설을 결과에 맞춰 바꾸면 p-value는 빠르게 의미를 잃습니다.

## 멘탈 모델: p-value의 정확한 정의

p-value는 귀무가설이 참이라는 가정 아래 계산됩니다. 즉, "차이가 없다"는 세계에서 지금처럼 극단적인 결과를 볼 확률을 묻는 값입니다. 그러니 이 값은 가설의 진실도나 효과 크기를 대신하지 못합니다.

**공식 정의:**
> p-value = P(T ≥ t_obs | H0가 참)

여기서 T는 검정통계량이고 t_obs는 관측된 검정통계량 값입니다.

### p-value 오해 모음

| 오해 | 실제 의미 |
|------|----------|
| p = P(H0가 참) | p는 H0가 참이라고 가정할 때, 현재 데이터만큼 극단적인 결과가 나올 확률입니다. |
| p-value가 작으면 효과가 크다 | p-value는 효과 크기가 아니라 증거의 강도입니다. 표본이 크면 작은 효과도 p가 작아질 수 있습니다. |
| p > 0.05면 효과가 없다 | p > 0.05는 현재 데이터로는 H0를 기각할 충분한 증거가 없다는 뜻이지, H0가 참이라는 증명이 아닙니다. |
| p = 0.05와 p = 0.051은 완전히 다르다 | 0.05는 관례일 뿐입니다. p-value를 연속 스펙트럼으로 읽어야 합니다. |
| p-value가 작으면 재현 가능하다 | p-value는 한 번의 실험 결과입니다. 재현성은 반복 실험의 일관성에 달려 있습니다. |

## p-value 계산 과정 시각화

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 설정
rng = np.random.default_rng(42)
sample = rng.normal(loc=105, scale=15, size=30)
mu0 = 100

# t-통계량 계산
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
t_stat = (mean - mu0) / se
df = len(sample) - 1

# p-value
p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

print(f"표본 평균: {mean:.2f}")
print(f"표준오차: {se:.2f}")
print(f"t-통계량: {t_stat:.3f}")
print(f"자유도: {df}")
print(f"p-value: {p_value:.4f}")

# t-분포와 기각역 시각화
x = np.linspace(-5, 5, 400)
y = stats.t.pdf(x, df)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, y, "k-", lw=2, label=f"t-분포 (df={df})")

# 기각역 표시
crit = stats.t.ppf(0.975, df)
ax.fill_between(x, y, where=(x >= crit), color="red", alpha=0.4, label=f"기각역 (p={p_value:.3f}의 절반)")
ax.fill_between(x, y, where=(x <= -crit), color="red", alpha=0.4)
ax.axvline(t_stat, color="blue", lw=2, linestyle="--", label=f"관측 t = {t_stat:.3f}")
ax.axvline(-t_stat, color="blue", lw=2, linestyle="--")

ax.set_xlabel("t 통계량")
ax.set_ylabel("밀도")
ax.set_title(f"p-value 시각화: p={p_value:.4f}")
ax.legend()
plt.tight_layout()
plt.show()
```

p-value는 t-분포에서 관측 통계량보다 더 극단적인 영역의 확률(빨간 영역)입니다.

## 표본 크기와 p-value의 관계

```python
import numpy as np
from scipy.stats import ttest_1samp
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
true_effect = 2  # 실제 효과: 모평균 - H0 값
mu0 = 100
true_mean = mu0 + true_effect

sample_sizes = [10, 20, 50, 100, 200, 500, 1000, 5000]
p_values = []
cohens_ds = []

for n in sample_sizes:
    sample = rng.normal(true_mean, 15, n)
    _, p = ttest_1samp(sample, mu0)
    d = (sample.mean() - mu0) / sample.std(ddof=1)
    p_values.append(p)
    cohens_ds.append(d)
    print(f"n={n:5d}: p={p:.4f}, Cohen's d={d:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].semilogx(sample_sizes, p_values, "o-", color="steelblue", lw=2)
axes[0].axhline(0.05, color="red", linestyle="--", label="α=0.05")
axes[0].set_xlabel("표본 크기 (로그 스케일)")
axes[0].set_ylabel("p-value")
axes[0].set_title("표본 크기 증가 → p-value 감소")
axes[0].legend()

axes[1].semilogx(sample_sizes, cohens_ds, "o-", color="green", lw=2)
axes[1].axhline(true_effect / 15, color="red", linestyle="--",
                label=f"실제 효과 d={true_effect/15:.2f}")
axes[1].set_xlabel("표본 크기 (로그 스케일)")
axes[1].set_ylabel("Cohen's d")
axes[1].set_title("표본 크기 증가 → 효과 크기는 안정")
axes[1].legend()

plt.tight_layout()
plt.show()
```

핵심 통찰: 표본이 충분히 크면 매우 작은 효과도 p < 0.05가 나올 수 있습니다. p-value가 작아도 효과 크기(Cohen's d)는 별도로 확인해야 합니다.

## p-hacking 위험 시뮬레이션

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
n_simulations = 10000
alpha = 0.05

# 단일 검정 1종 오류율
single_test_fp = 0
for _ in range(n_simulations):
    x = rng.normal(0, 1, 30)
    _, p = stats.ttest_1samp(x, 0)
    if p < alpha:
        single_test_fp += 1

# 20회 반복 검정 중 1회 이상 유의
multiple_test_fp = 0
for _ in range(n_simulations):
    for _ in range(20):  # 20번 반복
        x = rng.normal(0, 1, 30)
        _, p = stats.ttest_1samp(x, 0)
        if p < alpha:
            multiple_test_fp += 1
            break  # 첫 번째 유의하면 멈춤

print(f"단일 검정 1종 오류율: {single_test_fp/n_simulations:.3f} (이론: {alpha:.3f})")
print(f"20회 반복 시 1종 오류율: {multiple_test_fp/n_simulations:.3f} (이론: {1-(1-alpha)**20:.3f})")
```

**예상 출력:**

```text
단일 검정 1종 오류율: 0.050 (이론: 0.050)
20회 반복 시 1종 오류율: 0.642 (이론: 0.642)
```

같은 데이터를 여러 번 들여다볼수록 우연한 유의성은 빠르게 누적됩니다. 20번 반복하면 귀무가설이 참이어도 64% 확률로 유의한 결과가 나옵니다.

## 핵심 용어 정리

- **p-value**: H0가 참이라고 가정할 때, 현재 관측값만큼 또는 그보다 더 극단적인 결과가 나올 확률입니다.
- **유의수준 α**: 기각 기준으로 미리 정한 문턱값입니다.
- **1종 오류**: H0가 참인데 기각하는 오류입니다.
- **p-hacking**: 원하는 p-value가 나올 때까지 분석을 반복하거나 바꾸는 행위입니다.
- **사전등록**: 분석 전에 가설과 절차를 미리 공개하는 방식입니다.

## 효과 크기: p-value의 필수 보완재

```python
import numpy as np
from scipy.stats import ttest_ind

rng = np.random.default_rng(42)

# 시나리오 1: 큰 표본, 작은 효과 (p 작음, 효과 크기 작음)
n1 = 10000
a1 = rng.normal(100, 10, n1)
b1 = rng.normal(100.5, 10, n1)  # 0.5 차이
t1, p1 = ttest_ind(a1, b1)
d1 = (b1.mean() - a1.mean()) / np.sqrt((a1.var(ddof=1) + b1.var(ddof=1)) / 2)

# 시나리오 2: 작은 표본, 큰 효과 (p 클 수 있음, 효과 크기 큼)
n2 = 20
a2 = rng.normal(100, 10, n2)
b2 = rng.normal(115, 10, n2)  # 15 차이
t2, p2 = ttest_ind(a2, b2)
d2 = (b2.mean() - a2.mean()) / np.sqrt((a2.var(ddof=1) + b2.var(ddof=1)) / 2)

print("시나리오 1 (n=10000, 효과=0.5):")
print(f"  p={p1:.4f}, Cohen's d={d1:.3f} → {'유의' if p1 < 0.05 else '비유의'}, 효과 {'작음' if abs(d1) < 0.2 else '중간'}")

print("\n시나리오 2 (n=20, 효과=15):")
print(f"  p={p2:.4f}, Cohen's d={d2:.3f} → {'유의' if p2 < 0.05 else '비유의'}, 효과 {'큼' if abs(d2) >= 0.8 else '중간'}")
```

p-value와 효과 크기는 다른 질문에 답합니다. p-value는 "우연인가?"를, 효과 크기는 "얼마나 큰가?"를 말합니다.

## 다중비교 보정

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

pvals = np.array([0.003, 0.021, 0.041, 0.074, 0.120, 0.032, 0.078, 0.011])

rej_bonf, p_bonf, _, _ = multipletests(pvals, alpha=0.05, method="bonferroni")
rej_fdr, p_fdr, _, _ = multipletests(pvals, alpha=0.05, method="fdr_bh")

print("원본 p값  | Bonferroni | FDR(BH)  | 기각(Bonf) | 기각(FDR)")
print("-" * 65)
for p, pb, pf, rb, rf in zip(pvals, p_bonf, p_fdr, rej_bonf, rej_fdr):
    print(f"{p:.3f}     | {pb:.3f}      | {pf:.3f}    | {'Y' if rb else 'N':1s}          | {'Y' if rf else 'N':1s}")
```

비교 수가 많을수록 보정 전 p-value는 과도하게 낙관적일 수 있습니다. Bonferroni는 보수적(1종 오류 강하게 통제), FDR은 균형적입니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| p = P(H0가 참)로 읽음 | "p=0.03이므로 H0 참 확률 3%" | "H0 참 가정 시 이런 결과 볼 확률 3%" |
| p-value = 효과 크기 | "p=0.001이므로 효과가 매우 큼" | Cohen's d 등 효과 크기 별도 계산 |
| p > 0.05 = 효과 없음 단정 | 비유의 → "차이 없음" 결론 | "현재 데이터로 확인 불가" 로 표현 |
| 다중검정 보정 없음 | 10개 가설 동시 검정, 1개 유의 | Bonferroni 또는 FDR 보정 적용 |
| HARKing | 결과 보고 가설 수정 | 사전등록으로 절차 고정 |
| 0.049와 0.051 극단 차이 | α=0.05 경계를 절대적 기준으로 사용 | 연속 스펙트럼으로 해석 |

## 실습: 5단계 p-value 읽기

### 1단계 — 가설을 정한다

```python
# H0: 평균 = 100, H1: 평균 ≠ 100
mu0 = 100
print(f"H0: μ = {mu0}")
print("H1: μ ≠ 100 (양측 검정)")
```

### 2단계 — 데이터를 준비한다

```python
import numpy as np
rng = np.random.default_rng(0)
sample = rng.normal(102, 15, size=40)
print(f"표본평균: {sample.mean():.2f}")
```

### 3단계 — 검정을 실행한다

```python
from scipy import stats
t, p = stats.ttest_1samp(sample, mu0)
print(f"t: {t:.3f}, p: {p:.4f}")
```

### 4단계 — 효과 크기를 계산한다

```python
effect = (sample.mean() - mu0) / sample.std(ddof=1)
print(f"Cohen's d: {effect:.3f}")
```

p-value와 별개로 차이의 크기를 읽는 단계입니다.

### 5단계 — 결과를 종합한다

```python
from scipy.stats import t as t_dist

ci = t_dist.interval(0.95, df=len(sample)-1,
                     loc=sample.mean(),
                     scale=sample.std(ddof=1)/np.sqrt(len(sample)))

print(f"\n=== 결과 요약 ===")
print(f"표본평균: {sample.mean():.2f}")
print(f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")
print(f"p-value: {p:.4f}")
print(f"Cohen's d: {effect:.3f}")
print(f"유의 여부: {'유의' if p < 0.05 else '비유의'} (α=0.05)")
```

p-value, 신뢰구간, 효과 크기를 함께 보고해야 완전한 결과입니다.

## p-value를 안전하게 쓰는 팀 규칙

1. 가설, 표본 수, 종료 조건을 실험 전 문서화합니다.
2. p-value 단독 보고를 금지하고 효과 크기와 구간을 필수로 포함합니다.
3. 동일 데이터셋에서 다중검정을 수행하면 보정을 적용합니다.
4. 중간 점검 횟수를 정하고 임의 중단을 금지합니다.
5. 재현 분석 스크립트와 시드를 함께 저장합니다.

2016년 미국통계학회(ASA)는 "p-value만으로 결론 내지 말 것"을 공식 성명으로 발표했습니다. 이제는 p-value를 하나의 참고 지표로만 쓰는 것이 표준입니다.

## 베이즈 팩터: p-value 대안

베이즈 팩터는 H1과 H0 중 어느 쪽이 데이터를 더 잘 설명하는지 비율로 나타냅니다. p-value와 달리 "H0가 얼마나 그럴듯한가"를 직접 말할 수 있습니다.

- BF > 10: H1을 강하게 지지
- BF = 1~3: 약한 지지
- BF < 0.1: H0를 강하게 지지

```python
# pingouin 라이브러리 사용 (pip install pingouin)
# import pingouin as pg
# result = pg.ttest(group_a, group_b, paired=False)
# print(result[['T', 'p-val', 'BF10']])
```

베이즈 팩터는 p-value보다 해석이 직관적이지만, 사전분포 선택에 민감할 수 있습니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트, 임상시험, 품질 관리 보고서는 p-value를 자주 보여 줍니다. 하지만 실무에서는 p-value만으로 의사결정을 닫지 않습니다. 효과 크기와 신뢰구간을 함께 보고, 필요하면 다중비교 보정을 적용하고, 실험 설계 자체를 문서화합니다.

시니어 엔지니어는 p-value가 작아도 "의미 있는 크기의 효과인가"를 따로 묻습니다. 그리고 사전등록이나 실험 계획 문서처럼 절차를 먼저 고정해 p-hacking 여지를 줄입니다. 숫자 하나보다 절차의 신뢰성이 더 중요합니다.

## 운영 체크리스트

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
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- **Statistics 101 (9/10): p-value 이해하기 (현재 글)**
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Nature — Scientists rise up against statistical significance](https://www.nature.com/articles/d41586-019-00857-9)
- [scipy.stats — ttest_1samp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html)
- [NIST/SEMATECH e-Handbook — Hypothesis Tests](https://www.itl.nist.gov/div898/handbook/prc/section2/prc2.htm)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, PValue, Inference, Misconceptions, Beginner
