---
series: statistics-101
episode: 7
title: "Statistics 101 (7/10): 가설검정"
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
  - HypothesisTesting
  - Inference
  - ABTest
  - Beginner
seo_description: 귀무가설과 대립가설을 세우고 t-test로 그룹 차이를 검정하는 절차를 단계별로 따라가며 1종 2종 오류와 검정력까지 정리
last_reviewed: '2026-05-12'
---

# Statistics 101 (7/10): 가설검정

데이터를 보다 보면 "차이가 있는가"라는 질문을 자주 만나게 됩니다. 새 버튼이 전환율을 올렸는지, 새 약물이 기존 치료보다 나은지, 두 모델의 성능 차이가 우연인지 아닌지 같은 질문입니다. 가설검정은 이런 비교 질문을 정식 절차로 다루는 방법입니다.

가설검정이 필요한 이유는 눈으로 보이는 차이가 항상 의미 있는 차이는 아니기 때문입니다. 표본에서는 우연한 흔들림이 계속 생기고, 그 흔들림을 통제하지 않으면 과장된 결론을 내리기 쉽습니다.

이 글은 Statistics 101 시리즈의 7번째 글입니다. 여기서는 귀무가설과 대립가설, t-test의 기본 흐름, 1종 오류와 2종 오류, 검정력이 왜 실무에서 빠지면 안 되는 개념인지 정리하겠습니다.

![Statistics 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/07/07-01-concept-at-a-glance.ko.png)
*Statistics 101 7장 흐름 개요*
> 가설검정의 목표는 p-value 찾기가 아니라, 증거의 강도로 판단을 명확히 하는 것입니다.

## 이 글에서 다룰 문제

- 데이터로 "차이가 있다"는 말을 어디까지 할 수 있을까요?
- 귀무가설 H0와 대립가설 H1은 무엇을 뜻할까요?
- p-value만으로 판단하면 왜 부족할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

A/B 테스트, 캠페인 효과 측정, 모델 성능 비교처럼 비교 중심의 의사결정은 매우 많습니다. 이때 차이가 보인다는 이유만으로 바로 배포하거나 중단하면, 우연한 잡음을 효과로 오해할 수 있습니다. 반대로 실제 효과가 있는데도 표본이 작아 놓치는 경우도 생깁니다.

가설검정은 이 두 위험을 구분하는 프레임을 제공합니다. 유의수준은 어느 정도의 거짓 경보를 감수할지 정하는 값이고, 검정력은 실제 효과를 얼마나 잘 잡아낼지를 말합니다. 실무에서는 이 둘을 함께 봐야 합니다.

## 멘탈 모델: 가설검정 절차

가설검정은 먼저 "차이가 없다"는 기본 가정을 세우고, 표본에서 계산한 검정통계량이 그 가정 아래 얼마나 드문지 측정한 뒤, 미리 정한 기준과 비교해 결론을 내리는 절차입니다. 중요한 점은 가설을 데이터 보기 전에 정해야 한다는 사실입니다.

- **귀무가설(H0)**: 차이가 없다는 기본 가정입니다.
- **대립가설(H1)**: 차이가 있다는 가정입니다.
- **유의수준(α)**: 1종 오류를 허용하는 기준값입니다. 보통 0.05를 많이 씁니다.
- **검정력(1-β)**: 실제 효과가 있을 때 그것을 잡아낼 확률입니다.
- **1종 오류**: H0가 참인데 기각하는 오류입니다 (거짓 양성).
- **2종 오류**: H0가 거짓인데 기각하지 못하는 오류입니다 (거짓 음성).

### 검정 유형 비교

| 검정 유형 | 조건 | 용도 |
|----------|------|------|
| z-test | 분산 알려짐, n ≥ 30 | 모평균 검정, 비율 검정 |
| t-test (독립) | 분산 모름, 두 독립 그룹 | 두 그룹 평균 비교 |
| t-test (대응) | 동일 대상 사전/사후 측정 | 처리 효과 비교 |
| chi-square | 범주형 데이터 | 독립성 검정, 적합도 검정 |
| ANOVA | 세 그룹 이상 | 여러 그룹 평균 비교 |
| Mann-Whitney U | 비모수, 두 그룹 | 정규성 가정 불가 시 t-test 대안 |

## 파이썬으로 t-검정 전체 흐름

```python
import numpy as np
from scipy.stats import ttest_ind

rng = np.random.default_rng(42)

# 두 그룹 데이터 생성
control = rng.normal(loc=50, scale=10, size=100)
treatment = rng.normal(loc=53, scale=10, size=100)

# 기술 통계 먼저
print("=== 기술 통계 ===")
print(f"Control:   mean={control.mean():.2f}, std={control.std(ddof=1):.2f}, n={len(control)}")
print(f"Treatment: mean={treatment.mean():.2f}, std={treatment.std(ddof=1):.2f}, n={len(treatment)}")

# Welch's t-test 수행 (분산이 다를 때도 안전)
t_stat, p_value = ttest_ind(control, treatment, equal_var=False)

# 효과 크기 (Cohen's d)
mean_diff = treatment.mean() - control.mean()
pooled_std = np.sqrt((control.var(ddof=1) + treatment.var(ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

print("\n=== 검정 결과 ===")
print(f"t-statistic: {t_stat:.3f}")
print(f"p-value:     {p_value:.4f}")
print(f"평균 차이:   {mean_diff:.2f}")
print(f"Cohen's d:   {cohens_d:.3f}")

# 판단
alpha = 0.05
print(f"\n유의수준 α={alpha}")
if p_value < alpha:
    print(f"→ H0 기각: 두 그룹 간 통계적으로 유의한 차이가 있습니다.")
else:
    print(f"→ H0 유지: 현재 데이터로는 차이를 확인할 수 없습니다.")

# Cohen's d 해석
if abs(cohens_d) < 0.2:
    effect_label = "작음"
elif abs(cohens_d) < 0.5:
    effect_label = "중간"
else:
    effect_label = "큼"
print(f"→ 효과 크기: {effect_label} (d={cohens_d:.3f})")
```

**예상 출력:**

```text
=== 기술 통계 ===
Control:   mean=50.14, std=9.82, n=100
Treatment: mean=53.03, std=10.21, n=100

=== 검정 결과 ===
t-statistic: -2.056
p-value:     0.0409
평균 차이:   2.89
Cohen's d:   0.289

유의수준 α=0.05
→ H0 기각: 두 그룹 간 통계적으로 유의한 차이가 있습니다.
→ 효과 크기: 중간 (d=0.289)
```

## 분포 시각화: 두 그룹 비교

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
control = rng.normal(50, 10, 300)
treatment = rng.normal(54, 10, 300)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 히스토그램 비교
axes[0].hist(control, bins=30, alpha=0.6, color="steelblue", label=f"Control (n=300)")
axes[0].hist(treatment, bins=30, alpha=0.6, color="salmon", label=f"Treatment (n=300)")
axes[0].axvline(control.mean(), color="blue", lw=2, linestyle="--",
                label=f"Control 평균: {control.mean():.1f}")
axes[0].axvline(treatment.mean(), color="red", lw=2, linestyle="--",
                label=f"Treatment 평균: {treatment.mean():.1f}")
axes[0].set_title("두 그룹 분포 비교")
axes[0].legend(fontsize=8)

# 효과 크기 시각화
mean_diff = treatment.mean() - control.mean()
pooled_std = np.sqrt((control.var(ddof=1) + treatment.var(ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

x = np.linspace(20, 90, 400)
axes[1].plot(x, stats.norm.pdf(x, control.mean(), control.std()), "steelblue", lw=2, label="Control")
axes[1].plot(x, stats.norm.pdf(x, treatment.mean(), treatment.std()), "salmon", lw=2, label="Treatment")
axes[1].fill_between(x, 0, stats.norm.pdf(x, treatment.mean(), treatment.std()),
                     where=(x >= control.mean()), alpha=0.2, color="salmon")
axes[1].set_title(f"효과 크기 시각화 (Cohen's d={cohens_d:.2f})")
axes[1].legend()

plt.tight_layout()
plt.show()
```

히스토그램에서 두 분포가 얼마나 겹치는지 보면 효과 크기를 직관적으로 이해할 수 있습니다. Cohen's d가 클수록 두 분포의 겹침이 줄어듭니다.

## 1종 오류와 2종 오류 트레이드오프

```python
import numpy as np
from scipy.stats import ttest_1samp

rng = np.random.default_rng(0)
alpha_levels = [0.01, 0.05, 0.10]
n_trials = 2000

print("=== 1종 오류 (H0가 참인 데이터에서 기각 비율) ===")
for alpha in alpha_levels:
    false_positives = 0
    for _ in range(n_trials):
        # H0가 참: 모평균 = 100인 데이터
        sample = rng.normal(100, 15, size=30)
        _, p = ttest_1samp(sample, 100)
        if p < alpha:
            false_positives += 1
    print(f"α={alpha:.2f} → 1종 오류 발생 비율: {false_positives/n_trials:.3f} (이론: {alpha:.2f})")
```

α를 높이면 1종 오류 비율도 함께 오릅니다. 표본 수를 늘리면 둘 다 개선할 수 있지만, 비용과 시간 제약이 있을 때는 어느 오류를 더 피할지 선택해야 합니다.

### 오류 유형 비교 표

| 실제 상태 | H0 기각 | H0 유지 |
|----------|---------|---------|
| H0 참 (차이 없음) | **1종 오류 (α)** — 거짓 양성 | 올바른 판단 |
| H1 참 (차이 있음) | 올바른 판단 | **2종 오류 (β)** — 거짓 음성 |

## 검정력 분석

검정력은 1-β로, 실제 효과가 있을 때 그것을 올바르게 검출하는 확률입니다.

```python
from statsmodels.stats.power import tt_solve_power
import numpy as np
import matplotlib.pyplot as plt

# 효과 크기별 필요 표본 수
effect_sizes = np.arange(0.1, 1.1, 0.1)
required_ns = [tt_solve_power(effect_size=d, alpha=0.05, power=0.80,
                               alternative='two-sided')
               for d in effect_sizes]

print("효과 크기별 필요 표본 수 (각 그룹당, α=0.05, 검정력=0.80):")
for d, n in zip(effect_sizes, required_ns):
    label = "작음" if d < 0.2 else ("중간" if d < 0.5 else "큼")
    print(f"d={d:.1f} ({label:3s}) → n={int(np.ceil(n)):4d}명")

# 시각화
plt.figure(figsize=(8, 4))
plt.plot(effect_sizes, [int(np.ceil(n)) for n in required_ns], "o-", color="steelblue", lw=2)
plt.xlabel("Cohen's d (효과 크기)")
plt.ylabel("필요 표본 수 (각 그룹당)")
plt.title("효과 크기와 필요 표본 수 (α=0.05, 검정력=0.80)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

검정력 분석 없이 실험을 시작하면 결과 해석에서 늘 "표본이 부족했을 수 있음"이라는 불확실성이 남습니다. 사전에 필요한 표본 수를 계산하면 이 문제를 예방할 수 있습니다.

## 핵심 용어 정리

- **귀무가설(H0)**: 차이가 없다는 기본 가정입니다.
- **대립가설(H1)**: 차이가 있다는 가정입니다.
- **유의수준(α)**: 1종 오류를 허용하는 기준값입니다.
- **검정력(1-β)**: 실제 효과가 있을 때 그것을 잡아낼 확률입니다.
- **Cohen's d**: 두 그룹 평균 차이를 풀드 표준편차로 나눈 효과 크기 지표입니다.

## 눈에 보이는 차이와 통계적 차이는 다를 수 있다

이전 해석: "B 그룹 평균이 더 높으니 새 처리 방식이 효과가 있습니다."

표본 차이는 우연으로도 얼마든지 나타날 수 있습니다.

이후 해석: "B 그룹 평균은 0.4퍼센트포인트 높고, t=3.2, p=0.001입니다. 유의수준 0.05 기준에서는 차이가 있다고 읽을 수 있으며, 효과 크기(d=0.31)는 중간 수준입니다."

가설검정은 차이의 존재를 말하는 절차이지, 그 차이가 큰지 작은지 대신 말해 주는 절차는 아닙니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| p-value만으로 결론 | "p<0.05이므로 효과가 큼" | 효과 크기(Cohen's d)를 별도로 계산 |
| 다중비교 보정 생략 | 10개 지표를 동시 검정 | Bonferroni 또는 FDR 보정 적용 |
| 검정력 미계산 | 표본 수 정하지 않고 실험 시작 | 사전에 power analysis로 필요 n 계산 |
| 단/양측 검정 사후 선택 | 결과 보고 단측 검정으로 변경 | 사전에 검정 방향 고정 |
| HARKing | 결과 보고 가설을 뒤늦게 맞춤 | 분석 전 가설 문서화 필수 |
| "기각 실패 = 차이 없음" | H0 유지를 효과 없음으로 단정 | 증거 부족 신호임을 명시 |

## 실습: 5단계 가설검정

### 1단계 — 가설을 적는다

```python
# H0: μ_A = μ_B (두 그룹 평균이 같다)
# H1: μ_A ≠ μ_B (두 그룹 평균이 다르다)
# α = 0.05 (양측 검정)
print("H0: μ_control = μ_treatment")
print("H1: μ_control ≠ μ_treatment")
print("α = 0.05")
```

가설을 결과 보기 전에 정하는 습관이 중요합니다.

### 2단계 — 표본을 준비한다

```python
import numpy as np
rng = np.random.default_rng(42)
a = rng.normal(3.2, 1, 1000)
b = rng.normal(3.6, 1, 1000)
```

### 3단계 — 검정통계량과 유의확률을 계산한다

```python
from scipy.stats import ttest_ind
stat, p = ttest_ind(a, b, equal_var=False)
print(f"t: {stat:.3f}, p: {p:.4f}")
```

Welch의 t-test를 사용하면 분산이 같지 않아도 더 안전합니다.

### 4단계 — 기준에 따라 판단한다

```python
print("Reject H0" if p < 0.05 else "Fail to reject H0")
```

기각 실패는 H0가 참이라고 단정할 근거가 아니라, 현재 데이터로는 충분히 반박하지 못했다는 말입니다.

### 5단계 — 효과 크기를 함께 본다

```python
diff = b.mean() - a.mean()
pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
d = diff / pooled
print(f"Cohen's d: {d:.3f}")
```

p-value와 효과 크기를 함께 읽어야 실제 의미가 보입니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트 결과 페이지, 모델 비교 실험, 임상 연구처럼 비교가 중심인 작업에서는 가설검정이 표준 절차처럼 등장합니다. 이때 Bonferroni나 FDR 같은 다중비교 보정이 함께 붙는 경우도 많습니다. 비교가 많아질수록 우연히 유의해 보이는 결과가 늘기 때문입니다.

시니어 엔지니어는 데이터를 보기 전에 가설을 적고, p-value와 효과 크기를 함께 읽으며, 필요한 표본 수를 먼저 계산합니다. 또 "기각하지 못함"과 "차이가 없음"을 같은 말로 쓰지 않습니다.

## 운영 체크리스트

- [ ] H0와 H1을 명확히 적을 수 있습니다.
- [ ] 유의수준과 검정력의 역할을 설명할 수 있습니다.
- [ ] p-value와 효과 크기를 함께 보고합니다.
- [ ] 다중비교 보정이 왜 필요한지 압니다.

## 연습 문제

1. N=30과 N=3000에서 p-value가 어떻게 달라질지 시뮬레이션해 보세요.
2. 1종 오류와 2종 오류를 예시와 함께 설명해 보세요.
3. 세 개의 캠페인을 동시에 비교할 때 어떤 보정을 고려할지 적어 보세요.

## 정리와 다음 글

가설검정은 차이를 정식으로 묻는 절차입니다. 귀무가설과 대립가설을 먼저 세우고, 우연으로 설명될 가능성을 계산하고, 그 결과를 미리 정한 기준과 비교해 판단합니다. 다만 실제 의사결정은 p-value 하나로 끝나지 않습니다. 효과 크기, 표본 수, 비용, 맥락이 함께 들어와야 합니다.

다음 글에서는 상관과 회귀를 다룹니다. 두 변수의 관계를 숫자와 식으로 표현할 때 어떤 함정이 생기는지, 특히 상관과 인과를 섞지 않으려면 무엇을 봐야 하는지 이어서 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- **Statistics 101 (7/10): 가설검정 (현재 글)**
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [scipy.stats — Hypothesis Tests](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Hypothesis Testing](https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample)
- [Wikipedia — Multiple Comparisons Problem](https://en.wikipedia.org/wiki/Multiple_comparisons_problem)
- [Statistics Done Wrong (Reinhart)](https://www.statisticsdonewrong.com/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, HypothesisTesting, Inference, ABTest, Beginner
