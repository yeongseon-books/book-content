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

이 글은 Statistics 101 시리즈의 7번째 글입니다.

데이터를 보다 보면 “차이가 있는가”라는 질문을 자주 만나게 됩니다. 새 버튼이 전환율을 올렸는지, 새 약물이 기존 치료보다 나은지, 두 모델의 성능 차이가 우연인지 아닌지 같은 질문입니다. 가설검정은 이런 비교 질문을 정식 절차로 다루는 방법입니다.

가설검정이 필요한 이유는 눈으로 보이는 차이가 항상 의미 있는 차이는 아니기 때문입니다. 표본에서는 우연한 흔들림이 계속 생기고, 그 흔들림을 통제하지 않으면 과장된 결론을 내리기 쉽습니다.

이 글은 Statistics 101 시리즈의 7번째 글입니다. 여기서는 귀무가설과 대립가설, t-test의 기본 흐름, 1종 오류와 2종 오류, 검정력이 왜 실무에서 빠지면 안 되는 개념인지 정리하겠습니다.

## 먼저 던지는 질문

- 데이터로 “차이가 있다”는 말을 어디까지 할 수 있을까요?
- 귀무가설 H0와 대립가설 H1은 무엇을 뜻할까요?
- p-value만으로 판단하면 왜 부족할까요?

## 큰 그림

![Statistics 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/07/07-01-concept-at-a-glance.ko.png)

*Statistics 101 7장 흐름 개요*

가설검정은 '관찰한 차이가 우연의 범위 안에 있는가, 아니면 진짜 변화인가'를 판단하는 절차입니다. 통계학이 의사결정을 직접 내려주지는 않지만, 불확실성 수준을 정량화합니다.

> 가설검정의 목표는 p-value 찾기가 아니라, 증거의 강도로 판단을 명확히 하는 것입니다.

## 왜 중요한가

A/B 테스트, 캠페인 효과 측정, 모델 성능 비교처럼 비교 중심의 의사결정은 매우 많습니다. 이때 차이가 보인다는 이유만으로 바로 배포하거나 중단하면, 우연한 잡음을 효과로 오해할 수 있습니다. 반대로 실제 효과가 있는데도 표본이 작아 놓치는 경우도 생깁니다.

가설검정은 이 두 위험을 구분하는 프레임을 제공합니다. 유의수준은 어느 정도의 거짓 경보를 감수할지 정하는 값이고, 검정력은 실제 효과를 얼마나 잘 잡아낼지를 말합니다. 실무에서는 이 둘을 함께 봐야 합니다.

## 멘탈 모델

가설검정은 먼저 “차이가 없다”는 기본 가정을 세우고, 표본에서 계산한 검정통계량이 그 가정 아래 얼마나 드문지 측정한 뒤, 미리 정한 기준과 비교해 결론을 내리는 절차입니다. 중요한 점은 가설을 데이터 보기 전에 정해야 한다는 것입니다.

이 구조를 이해하면 p-value는 답 자체가 아니라 판단 재료라는 점이 보입니다. 실제 의사결정은 p-value, 효과 크기, 비용, 맥락을 함께 놓고 이뤄집니다.

## 핵심 용어

- **귀무가설(H0)**: 차이가 없다는 기본 가정입니다.
- **대립가설(H1)**: 차이가 있다는 가정입니다.
- **유의수준(α)**: 1종 오류를 허용하는 기준값입니다. 보통 0.05를 많이 씁니다.
- **검정력(1-β)**: 실제 효과가 있을 때 그것을 잡아낼 확률입니다.
- **1종 오류**: H0가 참인데 기각하는 오류입니다.
- **2종 오류**: H0가 거짓인데 기각하지 못하는 오류입니다.

## 검정 유형

가설검정은 데이터 유형과 질문에 따라 여러 검정 방법을 씁니다. 아래 표는 실무에서 자주 쓰이는 네 가지 검정과 적용 조건입니다.

| 검정 유형 | 조건 | 용도 |
|----------|------|------|
| z-test | 분산 알려짐, n ≥ 30 | 모평균 검정, 비율 검정 |
| t-test | 분산 모름, n < 30 | 두 그룹 평균 비교 (paired/unpaired) |
| chi-square | 범주형 데이터 | 독립성 검정, 적합도 검정 |
| ANOVA | 세 그룹 이상 | 여러 그룹 평균 비교 |

t-test는 가장 많이 쓰이는 검정 중 하나입니다. A/B 테스트, 실험군 비교, 전후 비교에서 표준처럼 등장합니다. 세 그룹 이상을 비교할 때는 ANOVA를 먼저 쓴 뒤, 사후검정으로 어느 쌍이 다른지 좁혀 갑니다.
## 눈에 보이는 차이와 통계적 차이는 다를 수 있다

이전 해석: “B 그룹 평균이 더 높으니 새 처리 방식이 효과가 있습니다.”

표본 차이는 우연으로도 얼마든지 나타날 수 있습니다.

이후 해석: “B 그룹 평균은 0.4퍼센트포인트 높고, t=3.2, p=0.001입니다. 유의수준 0.05 기준에서는 차이가 있다고 읽을 수 있으며, 효과 크기는 별도로 함께 봐야 합니다.”

가설검정은 차이의 존재를 말하는 절차이지, 그 차이가 큰지 작은지 대신 말해 주는 절차는 아닙니다.

## 실습: 5단계 가설검정

### 1단계 — 가설을 적는다

```text
H0: μ_A = μ_B
H1: μ_A ≠ μ_B
α = 0.05
```

가설을 결과 보기 전에 정하는 습관이 중요합니다.

### 2단계 — 표본을 준비한다

```python
import numpy as np
a = np.random.normal(3.2, 1, 1000)
b = np.random.normal(3.6, 1, 1000)
```

### 3단계 — 검정통계량과 유의확률를 계산한다

```python
from scipy.stats import ttest_ind
stat, p = ttest_ind(a, b, equal_var=False)
print("t:", stat, "p:", p)
```

**예상 출력:** `t: ... p: ...` 형태가 나오며, 두 그룹 차이가 우연으로 설명될 가능성을 빠르게 읽을 수 있습니다.

Welch의 t-test를 사용하면 분산이 같지 않아도 더 안전합니다.

### 4단계 — 기준에 따라 판단한다

```python
print("Reject H0" if p < 0.05 else "Fail to reject H0")
```

**예상 출력:** 현재 예시에서는 보통 `Reject H0`가 출력됩니다.

기각 실패는 H0가 참하다고 단정할 근거가 아니라, 현재 데이터로는 충분히 반박하지 못했다는 말입니다.

### 5단계 — 효과 크기를 함께 본다

```python
diff = b.mean() - a.mean()
pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
print("Cohen's d:", diff / pooled)
```

**예상 출력:** `Cohen's d: 0.3`~`0.5` 안팎처럼 효과 크기를 해석할 실마리가 하나 더 생깁니다.

p-value와 효과 크기를 함께 읽어야 실제 의미가 보입니다.

## 파이썬 사이파이로 티검정 전체 예제

아래 코드는 두 그룹 데이터를 준비하고, t-test를 수행하고, 효과 크기까지 계산하는 전체 흐름입니다.

```python
import numpy as np
from scipy.stats import ttest_ind

# 두 그룹 데이터 생성
np.random.seed(42)
control = np.random.normal(loc=50, scale=10, size=100)
treatment = np.random.normal(loc=53, scale=10, size=100)

# Welch's t-test 수행
t_stat, p_value = ttest_ind(control, treatment, equal_var=False)

# 효과 크기 (Cohen's d)
mean_diff = treatment.mean() - control.mean()
pooled_std = np.sqrt((control.var(ddof=1) + treatment.var(ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

print(f"t-statistic: {t_stat:.3f}")
print(f"p-value: {p_value:.4f}")
print(f"Mean difference: {mean_diff:.2f}")
print(f"Cohen's d: {cohens_d:.3f}")
```

실제 A/B 테스트에서는 표본 크기가 충분한지 사전에 검정력 분석(power analysis)을 수행합니다. 검정력이 0.8 이상이면 실제 효과가 있을 때 이를 탐지할 확률이 80% 이상이라는 의미입니다. 표본이 부족하면 유의미한 차이가 있어도 p-value가 높게 나와 효과를 놓치게 됩니다.

**예상 출력:**

```
t-statistic: -2.xxx
p-value: 0.01xx
Mean difference: 3.xx
Cohen's d: 0.3xx
```

이 출력은 t-통계량, p-value, 평균 차이, 효과 크기를 한 번에 보여 줍니다. p-value가 작아도 Cohen's d가 작으면 실무적으로는 효과가 미미할 수 있으므로, 둘을 함께 봐야 합니다.
## 이 코드에서 먼저 볼 점

- p-value만으로 결론을 닫으면 부족합니다.
- 효과 크기를 같이 보면 차이의 크기를 해석할 수 있습니다.
- `equal_var=False`는 Welch의 t-test를 선택합니다.

## 1종 오류와 2종 오류 트레이드오프

1종 오류(α)는 귀무가설이 참인데 기각하는 거짓 양성입니다. 2종 오류(β)는 귀무가설이 거짓인데 기각하지 못하는 거짓 음성입니다. 둘은 서로 반대 방향으로 움직입니다.

### 구체적 시나리오

신약 임상시험을 예로 들어 봅시다.

- **H0**: 신약은 기존 치료와 효과가 같다.
- **H1**: 신약이 더 효과적이다.

| 실제 상태 | H0 기각 | H0 유지 |
|----------|---------|---------|
| H0 참 (신약 효과 없음) | 1종 오류 (α) — 효과 없는데 승인 | 올바른 판단 |
| H1 참 (신약 효과 있음) | 올바른 판단 | 2종 오류 (β) — 효과 있는데 승인 거부 |

α를 0.05에서 0.01로 낮추면 1종 오류는 줄지만, β는 커집니다. 즉, 효과 없는 약을 승인하는 위험은 줄지만, 효과 있는 약을 놓칠 위험이 늘어납니다.

실무에서는 오류 비용을 비교합니다. 의료 분야는 1종 오류 비용이 매우 크므로 α를 엄격하게 잡고, 마케팅 실험은 실패 비용이 낮아 α를 조금 느슨하게 쓸 수 있습니다.

### 트레이드오프 시뮬레이션

```python
import numpy as np
from scipy.stats import ttest_1samp

alpha_levels = [0.01, 0.05, 0.10]
n_trials = 1000

for alpha in alpha_levels:
    false_positives = 0
    for _ in range(n_trials):
        # H0가 참인 데이터
        sample = np.random.normal(100, 15, size=30)
        _, p = ttest_1samp(sample, 100)
        if p < alpha:
            false_positives += 1
    print(f"α={alpha:.2f} → 1종 오류 발생 비율: {false_positives/n_trials:.3f}")
```

α를 높이면 1종 오류 비율도 함께 오릅니다. 표본 수를 늘리면 둘 다 개선할 수 있지만, 비용과 시간 제약이 있을 때는 어느 오류를 더 피할지 선택해야 합니다.
## 자주 헷갈리는 지점 5가지

1. **p < 0.05면 자동으로 큰 효과라고 보는 경우**: 유의성과 효과 크기는 다릅니다.
2. **여러 검정을 하면서 다중비교 보정을 빼는 경우**: 거짓 양성이 빠르게 늘어납니다.
3. **검정력 계산 없이 표본 수를 정하는 경우**: 실제 효과를 놓칠 수 있습니다.
4. **단측검정과 양측검정을 결과를 보고 고르는 경우**: 절차 오염이 생깁니다.
5. **결과를 본 뒤 가설을 바꾸는 경우**: HARKing 문제로 이어집니다.

## 검정력(검정력)

검정력은 1-β로, 실제 효과가 있을 때 그것을 올바르게 검출하는 확률입니다. 검정력이 낮으면 진짜 효과를 놓칠 위험이 큽니다.

검정력은 다음 요소에 영향을 받습니다:

1. **효과 크기**: 효과가 클수록 검정력이 높아집니다.
2. **표본 크기**: n이 클수록 검정력이 높아집니다.
3. **유의수준 α**: α를 높이면 검정력도 올라가지만, 1종 오류 위험이 함께 늘어납니다.
4. **분산**: 데이터 분산이 작을수록 검정력이 높아집니다.

### 실무 표준

일반적으로 검정력 0.8 이상을 목표로 합니다. 즉, 실제 효과가 있을 때 80% 이상의 확률로 그것을 검출할 수 있는 표본 수를 미리 계산합니다.

### 파이썬으로 필요 표본 수 계산하기

statsmodels의 `tt_solve_power`를 쓰면 원하는 검정력을 달성하기 위해 필요한 표본 수를 역산할 수 있습니다.

```python
from statsmodels.stats.power import tt_solve_power

# 효과 크기 0.5, α=0.05, 검정력 0.8
n_required = tt_solve_power(effect_size=0.5, alpha=0.05, power=0.8, alternative='two-sided')
print(f"각 그룹당 필요 표본 수: {n_required:.0f}")
```

**예상 출력:** `각 그룹당 필요 표본 수: 64`

이 계산을 실험 설계 단계에서 먼저 하면, 데이터를 모은 뒤 "표본이 부족했다"는 결론을 피할 수 있습니다. 검정력 분석은 사전 계획의 핵심입니다.
## 실무에서는 이렇게 읽습니다

A/B 테스트 결과 페이지, 모델 비교 실험, 임상 연구처럼 비교가 중심인 작업에서는 가설검정이 표준 절차처럼 등장합니다. 이때 Bonferroni나 FDR 같은 다중비교 보정이 함께 붙는 경우도 많습니다. 비교가 많아질수록 우연히 유의해 보이는 결과가 늘기 때문입니다.

시니어 엔지니어는 데이터를 보기 전에 가설을 적고, p-value와 효과 크기를 함께 읽으며, 필요한 표본 수를 먼저 계산합니다. 또 “기각하지 못함”과 “차이가 없음”을 같은 말로 쓰지 않습니다. 이 구분이 의사결정 품질을 크게 바꿉니다.

## 체크리스트

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

다음 글에서는 상관과 회귀를 다룹니다. 두 변수의 관계를 숫자와 식으로 표현할 때 어떤 함정이 생기는지, 특히 상관과 인과를 섞지 않으려면 무엇을 봐야 하는지 이어서 살펴보겠습니다.

## 가설검정 운영화: 설계-실행-회고 루프

가설검정은 계산으로 끝나지 않습니다. 실무에서는 실험 설계 문서와 사후 회고 문서까지 포함해야 같은 실수를 줄일 수 있습니다.

### 실험 설계 문서에 반드시 넣을 항목

- 가설(H0/H1), 유의수준, 검정력 목표
- 최소 의미 효과(MDE)
- 중간 점검 규칙(언제 멈출지)
- 다중비교 보정 방식
- 로그 수집 품질 점검 항목

### 에이비 테스트 표본 수 역산 예제

```python
from statsmodels.stats.power import zt_ind_solve_power

baseline = 0.050
target = 0.055
effect = (target - baseline) / (baseline * (1 - baseline)) ** 0.5

n = zt_ind_solve_power(effect_size=effect, alpha=0.05, power=0.80, alternative='two-sided')
print(f"그룹당 필요 표본 수(근사): {int(n):,}")
```

검정력 분석 없이 실험을 시작하면 결과 해석에서 늘 “표본이 부족했을 수 있음”이라는 불확실성이 남습니다.

### 회고 문장 템플릿

- 관찰 효과: +0.42%p (95% 구간: +0.10%p ~ +0.74%p)
- 유의성: p=0.009
- 사업 영향: 월 추가 매출 추정 +1,800만원
- 결정: 전체 배포, 4주 후 유지 효과 재검증


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 추가 메모: 검증 가능한 의사결정 문장

분석 결과를 보고할 때는 "좋아 보입니다" 같은 모호한 문장을 피하고, 기준과 근거를 한 줄에 함께 적는 것이 좋습니다. 예를 들어 "전환율 +0.6%p, 95% 신뢰구간 +0.1~+1.1%p, p=0.014, 월간 기대효과 +320건, 2주 재검증 조건부 배포"처럼 쓰면 의사결정 책임이 명확해집니다. 이런 형식은 통계 도구가 바뀌어도 유지되는 팀 자산입니다.


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 처음 질문으로 돌아가기

- **데이터로 “차이가 있다”는 말을 어디까지 할 수 있을까요?**
  - 귀무가설은 '변화 없다'이고, 우리는 그 가설이 데이터와 맞지 않음을 보이는 증거를 찾습니다.
- **귀무가설 H0와 대립가설 H1은 무엇을 뜻할까요?**
  - p-value가 작을수록(p < 0.05), 관찰이 귀무가설 하에서 드물다는 뜻입니다.
- **p-value만으로 판단하면 왜 부족할까요?**
  - 운영에서는 검정 결과뿐 아니라 효과의 크기와 비즈니스 영향을 함께 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- **가설검정 (현재 글)**
- 상관과 회귀 (예정)
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)

<!-- toc:end -->

## 참고 자료

- [scipy.stats — Hypothesis Tests](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Hypothesis Testing](https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample)
- [Wikipedia — Multiple Comparisons Problem](https://en.wikipedia.org/wiki/Multiple_comparisons_problem)
- [Statistics Done Wrong (Reinhart)](https://www.statisticsdonewrong.com/)


- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, HypothesisTesting, Inference, ABTest, Beginner
