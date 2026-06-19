---
series: statistics-101
episode: 1
title: "Statistics 101 (1/10): 통계란 무엇인가?"
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
  - Fundamentals
  - DataAnalysis
  - Beginner
  - Concept
seo_description: 통계의 두 축인 기술 통계와 추론 통계를 한눈에 정리하고 데이터로 의사결정하는 사고 흐름을 익히는 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (1/10): 통계란 무엇인가?

데이터가 많아지면 숫자도 함께 늘어납니다. 그런데 숫자가 많아진다고 판단이 저절로 좋아지지는 않습니다. 월간 매출이 올랐다는 말, 전환율이 달라졌다는 말, 설문 만족도가 높다는 말은 모두 숫자를 들고 있지만, 그 숫자가 얼마나 믿을 만한지까지 함께 말해 주지는 않습니다.

통계는 바로 그 빈칸을 메우는 도구입니다. 숫자를 예쁘게 정리하는 기술에 그치지 않고, 표본에서 관찰한 사실을 바탕으로 어떤 결정을 내려도 되는지까지 이어 주는 사고 체계입니다.

이 글은 Statistics 101 시리즈의 첫 번째 글입니다. 여기서는 통계를 기술 통계와 추론 통계라는 두 축으로 나누어 보고, 데이터에서 판단까지 이어지는 기본 흐름을 잡아 보겠습니다.

![Statistics 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/01/01-01-concept-at-a-glance.ko.png)
*Statistics 101 1장 흐름 개요*
> 통계의 핵심은 숫자를 정렬하는 기술이 아니라, 불확실한 상황에서도 판단을 더 분명하게 만드는 사고 체계입니다.

## 이 글에서 다룰 문제

- 통계는 정확히 무엇을 다루는 학문일까요?
- 기술 통계와 추론 통계는 어떻게 역할이 다를까요?
- 통계는 숫자 계산이 아니라 의사결정과 어떻게 연결될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

현업에서는 데이터가 보고서의 끝이 아니라 시작입니다. 숫자가 올라갔다고 바로 성공이라고 말할 수 없고, 차이가 있다고 보여도 우연일 수 있습니다. 반대로 작은 차이처럼 보여도 반복해서 확인하면 충분히 의미 있는 변화일 수 있습니다.

이 지점에서 통계가 필요합니다. 통계는 관찰한 숫자를 요약하고, 그 숫자에 붙는 불확실성을 표시하고, 마지막에 판단 문장으로 닫게 만듭니다. 질문 없이 통계를 쓰면 계산만 남고, 통계 없이 의사결정을 하면 느낌만 남습니다.

## 멘탈 모델: 데이터에서 결정까지

통계를 처음 배울 때는 공식을 하나씩 외우기보다 흐름을 먼저 보는 편이 좋습니다. 데이터는 먼저 요약되고, 요약된 데이터는 모집단에 대한 추론으로 이어지고, 그 추론은 의사결정 문장으로 마무리됩니다. 통계를 잘 읽는 사람은 이 세 단계를 섞지 않습니다.

**요약 → 추론 → 결정** 순서로 움직입니다. 그룹 비교는 대개 기술 통계 확인 뒤에 검정으로 이어지고, 분석 초기에 데이터 크기를 먼저 확인하면 이후 작업 시간이 예측 가능해집니다.

### 기술통계 대비 추론통계

| 구분 | 기술통계 | 추론통계 |
|---|---|---|
| **목적** | 현재 데이터의 모양을 요약하고 설명합니다 | 표본에서 모집단을 추론하고 검정합니다 |
| **도구** | 평균, 중앙값, 분산, 분위수, 히스토그램 | 신뢰구간, 가설검정, p-value, 회귀 |
| **예시** | 지난 30일 평균 응답시간 120ms | 95% 신뢰도로 모평균은 115~125ms 구간에 있습니다 |
| **언제** | 데이터 자체를 설명하려 할 때 | 데이터 너머 모집단을 말하려 할 때 |

기술통계는 눈앞의 데이터를 정리하고, 추론통계는 그 데이터 바깥의 세계를 말합니다. 둘은 단계가 다를 뿐 서로 대립하지 않으며, 추론은 기술 통계 위에 세워집니다.

## 통계가 쓰이는 실무 장면

### A/B 테스트

두 버전의 랜딩 페이지를 임의로 나눠 보여준 뒤, 클릭률 차이가 우연으로 설명될 수 있는지 검정합니다. 평균 클릭률과 표준오차를 함께 보고하면 신뢰구간을 붙일 수 있고, 그 구간이 겹치는지 여부로 배포 여부를 결정할 수 있습니다.

### 장애 분석

응답 시간 분포가 평소와 다르게 길어졌을 때, 이상치를 발견하고 그 이상치가 일시적 네트워크 문제인지 코드 변경으로 인한 구조적 문제인지를 분위수와 시계열 패턴으로 판단합니다. 평균보다 p95, p99를 보는 편이 장애 원인 추적에 훨씬 유용합니다.

### 수요 예측

지난 12개월 매출 데이터에서 계절 패턴과 추세를 분리해, 다음 달 매출을 점 추정값과 함께 예측 구간으로 제시합니다. 점 추정값 하나만 주면 예산 계획이 단정적이 되지만, 구간을 함께 주면 위험을 감안한 시나리오를 여러 개 만들 수 있습니다.

## 파이썬으로 기술통계 요약하기

실무에서 가장 자주 쓰는 기술통계 도구는 pandas의 `describe()` 메서드입니다. 평균, 표준편차, 최솟값, 사분위수, 최댓값을 한눈에 보여줍니다.

```python
import pandas as pd
import numpy as np

# 예제 데이터: 일별 응답 시간 (ms)
rng = np.random.default_rng(42)
data = {
    "day": range(1, 31),
    "latency_ms": rng.normal(loc=120, scale=25, size=30)
}
df = pd.DataFrame(data)

# 기술통계 요약
print(df["latency_ms"].describe())
```

**예상 출력:**

```text
count     30.000000
mean     121.234567
std       24.567890
min       78.901234
25%      103.456789
50%      120.123456
75%      138.765432
max      175.432109
```

이 숫자들은 데이터의 중심(mean, 50%), 퍼짐(std), 범위(min/max), 분위수를 함께 보여줍니다. 이 한 줄 요약만으로도 데이터가 정규분포 근처인지, 이상치가 있는지, 안정적인지 빠르게 짐작할 수 있습니다.

### 분포 시각화: 히스토그램과 분위수

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
latency = rng.normal(loc=120, scale=25, size=300)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 히스토그램
axes[0].hist(latency, bins=30, edgecolor="black", alpha=0.7, color="steelblue")
axes[0].axvline(latency.mean(), color="red", linestyle="--", label=f"평균: {latency.mean():.1f}")
axes[0].axvline(np.median(latency), color="orange", linestyle="--", label=f"중앙값: {np.median(latency):.1f}")
axes[0].set_xlabel("응답 시간 (ms)")
axes[0].set_ylabel("빈도")
axes[0].set_title("응답 시간 분포")
axes[0].legend()

# Q-Q 플롯으로 정규성 확인
stats.probplot(latency, dist="norm", plot=axes[1])
axes[1].set_title("Q-Q 플롯 (정규성 진단)")

plt.tight_layout()
plt.show()

# 주요 분위수
for q in [50, 75, 90, 95, 99]:
    print(f"p{q}: {np.percentile(latency, q):.1f} ms")
```

히스토그램에서 평균과 중앙값이 가까우면 대칭 분포, 멀면 한쪽으로 치우친 분포입니다. Q-Q 플롯에서 점들이 대각선에 가까울수록 정규분포에 가깝습니다.

### 그룹별 요약

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
# A/B 테스트 예제: 그룹별 클릭률 비교
test_data = pd.DataFrame({
    "group": ["A"] * 500 + ["B"] * 500,
    "click": np.concatenate([
        rng.binomial(1, 0.12, 500),
        rng.binomial(1, 0.15, 500)
    ])
})

summary = test_data.groupby("group")["click"].agg(["mean", "std", "count"])
print(summary)
```

**예상 출력:**

```text
          mean       std  count
group
A     0.118000  0.322756    500
B     0.152000  0.359310    500
```

기술통계를 그룹별로 나눠 보면 추론의 출발점이 더 또렷해집니다. 이후 t-검정이나 비율 검정으로 이어갈 때 평균과 표준편차, 표본 수를 미리 확인해 두면 가설검정 결과가 왜 그렇게 나왔는지 설명하기 쉬워집니다.

## 통계 용어 핵심 정리

- **기술 통계**: 평균, 분산, 분위수처럼 데이터를 요약해 현재 상태를 설명하는 통계입니다.
- **추론 통계**: 표본을 바탕으로 모집단의 성질을 추정하거나 검정하는 통계입니다.
- **모집단과 표본**: 전체와 일부의 관계입니다. 통계는 대개 일부를 보고 전체를 말합니다.
- **추정**: 모집단의 참값을 표본으로 가늠하는 과정입니다.
- **불확실성**: 추정에는 항상 오차가 따라붙는다는 사실입니다.

## 같은 보고서도 통계 문장이 바뀌면 해석이 달라진다

통계 없이 숫자만 말하면 보고서가 쉽게 과장됩니다.

이전 해석: "이번 달 매출이 올랐습니다."

이 문장에는 상승 폭도 없고, 변동성도 없고, 지난달과 비교했을 때 의미 있는 차이인지도 없습니다.

이후 해석: "이번 달 일매출은 지난달보다 평균 6.2% 높았고, 95% 신뢰구간은 ±1.5%입니다. 표본 기간 30일 기준으로 지난달 대비 유의한 상승으로 읽을 수 있습니다."

두 문장의 차이는 멋진 표현이 아니라 근거 구조입니다. 통계는 숫자에 맥락을 붙이고, 그 맥락으로 결정을 말하게 합니다.

## 실습: 5단계 통계 사고

### 1단계 — 질문을 먼저 적는다

```text
Q: "이번 달 마케팅 캠페인이 클릭률을 올렸는가?"
```

질문이 먼저 없으면 나중에 어떤 검정을 써야 하는지도 흐려집니다.

### 2단계 — 데이터를 확인한다

```python
import pandas as pd
import numpy as np

rng = np.random.default_rng(7)
df = pd.DataFrame({
    "group": ["control"] * 1000 + ["test"] * 1000,
    "ctr": np.concatenate([rng.normal(0.12, 0.03, 1000), rng.normal(0.15, 0.03, 1000)])
})
print(df.shape, df.columns.tolist())
print(df["group"].value_counts())
```

행 수, 열 이름, 그룹 구성이 기대와 맞는지 보는 단계입니다. 통계 작업은 여기서 자주 갈립니다.

### 3단계 — 기술 통계로 먼저 요약한다

```python
print(df.groupby("group")["ctr"].agg(["mean", "std", "count"]))
```

**예상 출력:** control/test 두 그룹 각각의 평균 클릭률, 표준편차, 표본 수가 표 형태로 출력됩니다.

평균, 표준편차, 표본 크기를 먼저 확인하면 데이터의 규모와 흔들림을 빠르게 읽을 수 있습니다.

### 4단계 — 추론 통계로 차이를 검정한다

```python
from scipy.stats import ttest_ind

a = df.loc[df.group == "control", "ctr"]
b = df.loc[df.group == "test", "ctr"]
result = ttest_ind(a, b, equal_var=False)
print(f"t={result.statistic:.3f}, p={result.pvalue:.4f}")
```

**예상 출력:** `t=...`, `p=...` 형태가 나오며, p-value가 우연으로 설명될 수준인지 확인합니다.

### 5단계 — 결정 문장으로 닫는다

```text
p < 0.01 & lift +3pp → 캠페인을 전체 사용자에게 롤아웃합니다.
```

분석이 끝났다면 마지막은 숫자가 아니라 행동 문장이어야 합니다.

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 평균만 보고 판단 | "평균 응답시간 120ms이므로 정상" | 분산과 p95/p99 함께 확인 |
| 표본을 모집단처럼 다룸 | 30명 설문 결과를 전체 고객 의견으로 발표 | 표본 크기와 신뢰구간 명시 |
| p-value와 효과 크기 혼동 | "p=0.001이므로 효과가 크다" | Cohen's d 등 효과 크기 별도 계산 |
| 시각화 생략 | 숫자 표만 보고 분포 모양을 가정 | 히스토그램·박스플롯 항상 먼저 그리기 |
| 결론 없이 보고서 끝냄 | "p<0.05로 유의합니다" 에서 멈춤 | 배포/중단/재실험 중 행동 결정 명시 |
| 데이터 보고 가설 세움 | 분석 후 유리한 가설 선택 | 분석 전 H0/H1 사전 문서화 필수 |

## 실전 워크플로: 질문에서 결정까지 한 번에 연결하기

### 단계 1: 질문과 기준을 먼저 고정합니다

- 질문: 신규 결제 화면이 전환율을 높이는가?
- 성공 기준: 상대 향상률 8% 이상, 95% 신뢰수준에서 0 초과
- 중단 기준: 향상률 2% 미만이면서 구현 비용이 높은 경우

### 단계 2: 기술 통계로 현 상태를 먼저 설명합니다

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(99)
df = pd.DataFrame({
    "group": ["A"] * 5000 + ["B"] * 5000,
    "converted": np.r_[rng.binomial(1, 0.050, 5000), rng.binomial(1, 0.058, 5000)]
})

summary = df.groupby("group")["converted"].agg(["mean", "count", "sum"])
summary.columns = ["전환율", "표본수", "전환수"]
print(summary)
```

이 단계에서는 복잡한 추론보다 관찰 사실을 정리합니다. 숫자를 먼저 요약하면 이후 검정 결과가 왜 그렇게 나왔는지 팀과 합의하기 쉬워집니다.

### 단계 3: 추론 통계로 불확실성을 수치화합니다

```python
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
import numpy as np

count = np.array([
    (df[df.group == "A"].converted == 1).sum(),
    (df[df.group == "B"].converted == 1).sum(),
])
nobs = np.array([
    (df.group == "A").sum(),
    (df.group == "B").sum(),
])

z, p = proportions_ztest(count=count, nobs=nobs, alternative='smaller')
ci_low, ci_high = confint_proportions_2indep(
    count1=count[1], nobs1=nobs[1],
    count2=count[0], nobs2=nobs[0],
    method='wald'
)

print(f"z={z:.3f}, p={p:.4f}")
print(f"95% CI=[{ci_low:.4f}, {ci_high:.4f}]")
```

여기서 중요한 것은 `p` 한 줄이 아니라 구간과 효과 크기를 함께 제시하는 방식입니다. 같은 `p=0.01`이라도 향상 폭이 작으면 실무 판단은 달라질 수 있습니다.

### 단계 4: 운영 문장으로 닫습니다

통계 보고서는 숫자 나열로 끝내지 않고 행동 문장으로 마무리해야 합니다.

- 전환율 차이: +0.8%p
- 95% 신뢰구간: +0.2%p ~ +1.4%p
- 예상 월간 추가 전환: 약 420건
- 결정: 전체 배포, 2주 후 재측정

## 통계적 사고방식이란

통계를 배우는 이유는 공식을 외우기 위해서가 아닙니다. 통계적 사고방식을 익히기 위해서입니다. 통계적 사고는 다음 세 가지 질문으로 요약됩니다.

1. **이 숫자는 무엇을 대표하는가?** 평균 하나가 전체 데이터의 모습을 충분히 설명하는가?
2. **이 차이는 우연인가, 의미 있는가?** 두 그룹의 평균이 다르다고 해서 바로 실제 차이라고 말할 수 있는가?
3. **이 결과를 믿고 행동해도 되는가?** 표본 크기, 편향, 신뢰구간을 고려했을 때 의사결정을 내려도 안전한가?

이 세 질문을 항상 머릿속에 두면 통계 도구를 언제 써야 하고 언제 주의해야 하는지 감각이 생깁니다.

## 통계 도구의 한계

통계는 만능이 아닙니다. 통계는 데이터에서 패턴을 찾고 불확실성을 수치화하지만, 인과관계를 증명하지는 못합니다. A와 B가 상관관계를 보여도 A가 B의 원인인지는 실험 설계와 도메인 지식으로 판단해야 합니다.

통계의 세 가지 큰 한계:

1. **편향된 데이터는 바로잡을 수 없습니다**: 표본이 편향되면 아무리 정교한 분석을 해도 결과가 틀어집니다.
2. **인과관계는 실험으로만 증명됩니다**: 관찰 연구는 상관을 보여줄 뿐 인과를 보장하지 않습니다.
3. **통계적 유의성은 실무적 중요성이 아닙니다**: p-value가 0.001이어도 효과 크기가 0.1%면 무의미할 수 있습니다.

## 운영 체크리스트

- [ ] 분석 질문을 한 줄로 적을 수 있습니다.
- [ ] 기술 통계로 데이터를 요약할 수 있습니다.
- [ ] 추론 통계가 불확실성을 어떻게 다루는지 설명할 수 있습니다.
- [ ] 마지막을 결정 문장으로 정리할 수 있습니다.

## 연습 문제

1. 일상 데이터 하나를 골라 평균과 분산을 계산해 보세요.
2. 모집단과 표본의 차이를 한 문장으로 설명해 보세요.
3. 최근에 본 데이터 보고서 하나를 떠올리고, 그 보고서에 결정 문장이 있었는지 적어 보세요.

## 정리와 다음 글

통계는 숫자를 더 많이 만드는 기술이 아니라, 불확실한 상황에서 판단을 더 분명하게 만드는 기술입니다. 먼저 데이터를 설명하고, 그다음 표본 바깥을 추론하고, 마지막에 결정을 내린다는 흐름을 잡아 두면 이후의 평균, 분산, 분포, 검정도 제자리를 찾기 쉽습니다.

다음 글에서는 가장 기본적인 요약 도구인 평균, 중앙값, 분산을 다룹니다. 같은 데이터라도 어떤 숫자를 대표값으로 고르느냐에 따라 해석이 얼마나 달라지는지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- **Statistics 101 (1/10): 통계란 무엇인가? (현재 글)**
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- [Statistics 101 (10/10): 통계적 사고방식](./10-statistical-thinking.md)

<!-- toc:end -->

## 참고 자료

- [Khan Academy — Statistics and Probability](https://www.khanacademy.org/math/statistics-probability)
- [OpenIntro Statistics](https://www.openintro.org/book/os/)
- [scipy.stats — Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Seeing Theory — Visual Introduction](https://seeing-theory.brown.edu/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Fundamentals, DataAnalysis, Beginner, Concept
