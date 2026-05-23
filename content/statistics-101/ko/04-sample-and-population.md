---
series: statistics-101
episode: 4
title: "Statistics 101 (4/10): 표본과 모집단"
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
  - Sampling
  - Population
  - Bias
  - Beginner
seo_description: 표본이 모집단을 대표하려면 어떤 조건이 필요한지 무작위 추출과 표본 편향을 중심으로 정리한 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (4/10): 표본과 모집단

통계는 대개 전체를 다 보지 못한 채 시작합니다. 모든 고객에게 설문을 돌릴 수 없고, 모든 생산품을 파괴 검사할 수도 없고, 모든 방문자를 같은 조건으로 실험하기도 어렵습니다. 그래서 일부를 보고 전체를 말하게 됩니다.

문제는 일부가 전체를 얼마나 닮았느냐입니다. 표본이 모집단을 잘 대표하지 못하면 그 뒤에 아무리 정교한 분석을 올려도 출발점이 흔들립니다.

이 글은 Statistics 101 시리즈의 4번째 글입니다. 여기서는 모집단, 표본, 모수, 통계량의 관계를 정리하고, 무작위 추출과 표본 편향이 왜 통계의 기초 체력인지 설명하겠습니다.

![Statistics 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/04/04-01-concept-at-a-glance.ko.png)
*Statistics 101 4장 흐름 개요*
> 표본이 모집단을 제대로 대표할수록, 추론의 신뢰도가 높아집니다.

## 먼저 던지는 질문

- 모집단과 표본은 어떻게 구분할까요?
- 표본이 모집단을 닮게 만드는 핵심 조건은 무엇일까요?
- 무작위 추출은 왜 그렇게 자주 등장할까요?

## 왜 중요한가

좋은 통계는 좋은 표본에서 출발합니다. 사용자 만족도 조사를 했는데 응답한 사람만 분석했다면, 적극적인 만족층만 과대표집되었을 수 있습니다. 베타 테스트를 했는데 헤비 유저만 참여했다면, 실제 출시 후의 평균 사용자는 다른 경험을 할 가능성이 큽니다.

통계 실무에서 “표본이 어떤 방식으로 뽑혔는가”는 부록이 아니라 본문입니다. 표본이 편향되면 평균도 편향되고, 회귀도 편향되고, 신뢰구간과 가설검정도 편향된 출발점 위에 서게 됩니다.

## 멘탈 모델

표본은 모집단의 축소판이어야 합니다. 통계량은 표본에서 계산되고, 그 통계량으로 모집단의 모수를 추정합니다. 이 연결이 성립하려면 표본이 최소한 체계적으로 한쪽으로 기울지 않아야 합니다.

표본이 모집단을 대표하는지 볼 때는 표본 수만 보지 않습니다. 누가 빠졌는지, 어떤 세그먼트가 과도하게 많거나 적은지, 응답하지 않은 집단이 어떤 성격인지까지 함께 봐야 합니다.

### 표본추출 방법 비교

| 방법 | 설명 | 장점 | 단점 |
|---|---|---|---|
| **단순무작위추출** | 전체에서 랜덤하게 n개 선택 | 편향 없음, 간단함 | 모집단 목록 필요, 소수 집단 누락 가능 |
| **층화추출** | 세그먼트별 비율 유지하며 추출 | 세그먼트 분포 보존, 정밀도 향상 | 층 분류 기준 필요, 복잡함 |
| **군집추출** | 전체를 여러 군집으로 나누고 군집 단위로 랜덤 선택 | 비용 절감, 실행 용이 | 군집 내 유사도 높으면 편향 위험 |
| **체계적추출** | 정렬 후 k번째마다 선택 | 간단하고 빠름 | 주기 패턴 있으면 편향 발생 |

단순무작위추출은 가장 기본이지만, 실무에서는 세그먼트 분포가 중요하거나 비용 제약이 있을 때 층화추출이나 군집추출을 씁니다. 온라인 설문은 단순무작위, 오프라인 매장 조사는 군집, 사용자 행동 로그 샘플링은 체계적 추출을 쓰는 경우가 많습니다.

## 표본 크기 결정

표본 수가 많으면 추정이 더 정확해지지만, 비용과 시간도 함께 늘어납니다. 그래서 "몇 개면 충분한가?"는 통계 작업의 첫 질문입니다.

### 표본 크기 공식 직관

표본 크기를 결정할 때는 세 가지를 함께 고려합니다:

1. **허용 오차(margin of error)**: 얼마나 정확해야 하는가?
2. **신뢰 수준**: 95%? 99%?
3. **모집단 분산**: 데이터가 얼마나 흩어져 있는가?

단순한 경우 표본 수 공식은 이렇습니다:

```
n = (Z² × σ²) / E²
```

- Z: 신뢰수준에 해당하는 표준정규분포 값 (95%일 때 1.96)
- σ: 모집단 표준편차 (추정값 사용)
- E: 허용 오차

### 파이썬으로 필요 표본 수 계산하기

```python
import numpy as np

def sample_size_mean(sigma, margin_error, confidence=0.95):
    """평균 추정에 필요한 표본 크기 계산"""
    from scipy.stats import norm
    z = norm.ppf((1 + confidence) / 2)
    n = (z * sigma / margin_error) ** 2
    return int(np.ceil(n))

# 예제: 표준편차 20, 오차 ±2 허용, 95% 신뢰
n = sample_size_mean(sigma=20, margin_error=2, confidence=0.95)
print(f"필요한 표본 수: {n}")
```

**예상 출력:**

```text
필요한 표본 수: 385
```

만약 오차를 ±1로 줄이려면 표본 수는 4배로 늘어납니다. 정밀도를 2배 높이려면 비용은 4배 늘어나는 구조입니다. 그래서 실무에서는 허용 오차와 예산을 함께 고려해 표본 수를 정합니다.

## 파이썬 무작위 표본추출 예제

```python
import pandas as pd
import random

# 모집단 데이터프레임
users = pd.DataFrame({
    "user_id": range(1, 10001),
    "plan": random.choices(["free", "pro", "enterprise"], weights=[70, 25, 5], k=10000)
})

# 단순무작위추출
sample = users.sample(n=500, random_state=42)

# 층화추출 (plan별 비율 유지)
stratified = users.groupby("plan", group_keys=False).apply(
    lambda x: x.sample(frac=0.05, random_state=42)
)

print("모집단 plan 분포:")
print(users["plan"].value_counts(normalize=True))
print("\n단순무작위 표본 plan 분포:")
print(sample["plan"].value_counts(normalize=True))
print("\n층화 표본 plan 분포:")
print(stratified["plan"].value_counts(normalize=True))
```

층화추출은 세그먼트별 비율을 정확히 유지하므로, 소수 세그먼트(enterprise)가 과소표집되는 문제를 방지합니다. A/B 테스트나 설문조사에서 세그먼트 균형이 중요할 때 유용합니다.
## 핵심 용어

- 모집단: 알고 싶은 대상 전체입니다.
- 표본: 모집단에서 뽑아 관찰한 일부입니다.
- 모수: 모집단의 참값입니다. 예를 들어 모평균 μ가 있습니다.
- 통계량: 표본에서 계산한 값입니다. 예를 들어 표본평균 x̄가 있습니다.
- **표본 편향**: 표본이 모집단을 제대로 대표하지 못하는 상태입니다.

## 같은 설문도 표본을 어떻게 뽑느냐에 따라 해석이 달라진다

이전 해석: “웹사이트 만족도 평균은 4.5점입니다.”

응답자만 분석했다면 이 숫자는 실제 전체 사용자 만족도보다 높게 잡혔을 수 있습니다.

이후 해석: “응답자는 200명이고 전체 방문자는 1만 명입니다. 응답률은 2%이며 만족한 사용자가 더 적극적으로 응답했을 가능성이 있어 보수적으로 해석해야 합니다.”

표본 설명이 붙는 순간 숫자는 더 조심스러워지지만, 오히려 더 믿을 만해집니다.
표본 크기 결정 공식(`n = (Z² × σ²) / E²`)을 쓸 때는 모분산 σ를 미리 알아야 하는데, 실무에서는 파일럿 조사나 과거 데이터로 추정합니다. 목표 오차(E)가 절반으로 줄면 표본 크기는 4배 늘어나므로 비용과 정밀도 사이 균형을 잡아야 합니다.

## 실습: 5단계 표본 설계

### 1단계 — 모집단을 문장으로 적는다

```text
Population: "active users on our website over the last 30 days"
```

모집단 정의가 흐리면 표본도 흐려집니다.

### 2단계 — 표본 추출 틀을 준비한다

```python
import pandas as pd
users = pd.read_csv("active_users.csv")  # 모집단 목록
print(len(users))
```

누구를 뽑을 수 있는지, 목록 자체가 모집단을 얼마나 잘 덮는지 봐야 합니다.

### 3단계 — 무작위로 표본을 뽑는다

```python
sample = users.sample(n=500, random_state=42)
```

재현 가능한 무작위 추출은 편향을 줄이는 가장 기본적인 장치입니다.

### 4단계 — 응답을 수집한다

```python
responses = collect_survey(sample.user_id)
print("response rate:", len(responses) / len(sample))
```

응답률은 단순한 진행률이 아니라 편향 신호입니다.

### 5단계 — 편향 가능성을 점검한다

```python
print("plan dist (sample):", sample.plan.value_counts(normalize=True))
print("plan dist (pop):",    users.plan.value_counts(normalize=True))
```

세그먼트 분포 차이가 크면 표본이 대표성을 잃고 있다는 뜻일 수 있습니다.

- 표본 추출 단계에서 random seed를 고정(`random_state`)하면 재현 가능한 분석을 만들 수 있습니다. 실험 결과를 공유할 때 random seed도 함께 기록하는 것이 좋습니다.
- 응답률이 낮으면 비응답 편향(non-response bias)이 커질 수 있습니다. 응답자와 비응답자 간 속성 차이를 확인하고, 가중치 조정이나 민감도 분석을 고려해야 합니다.
## 이 코드에서 먼저 볼 점

- 모집단 정의는 표본 설계의 첫 단계입니다.
- `random_state`는 재현성을 보장합니다.
- 응답률과 세그먼트 분포는 편향을 드러내는 핵심 지표입니다.

## 자주 헷갈리는 지점 5가지

1. **편의 표본을 대표 표본처럼 다루는 경우**: 쉽게 모은 데이터는 대개 한쪽으로 치웁니다.
2. **응답자만 분석하고 비응답자를 잊는 경우**: 두 집단은 다를 수 있습니다.
3. **N=30이면 충분하다고 기계적으로 믿는 경우**: 표본 수보다 설계가 먼저입니다.
4. **모집단 정의 없이 표본을 뽑는 경우**: 무엇을 대표하는지 모호해집니다.
5. **시간순 일부 구간만 잘라 쓰는 경우**: 무작위성이 없어 특정 패턴이 과대반영될 수 있습니다.

## 실무에서는 이렇게 읽습니다

A/B 테스트, 만족도 조사, 품질 검사, 베타 테스트처럼 표본을 바탕으로 전체를 말해야 하는 작업은 많습니다. 이때 표본 설계가 분석 품질을 사실상 결정합니다. 층화추출이나 군집추출 같은 방법도 모두 같은 목표를 가집니다. 표본이 모집단의 구조를 덜 잃게 만드는 것입니다.

시니어 엔지니어는 모집단을 한 문장으로 먼저 적고, 무작위 시드를 고정하고, 응답률과 세그먼트 분포를 보고서에 함께 적습니다. 편향을 숨기지 않고 드러내는 태도가 오히려 판단의 품질을 높입니다.

## 체크리스트

- [ ] 모집단을 한 줄로 정의할 수 있습니다.
- [ ] 무작위 추출을 적용할 수 있습니다.
- [ ] 응답률을 함께 보고합니다.
- [ ] 표본과 모집단의 세그먼트 분포를 비교합니다.

## 연습 문제

1. 동아리나 팀 구성원을 예로 들어 모집단, 표본, 통계량을 정의해 보세요.
2. 편의 표본과 무작위 표본의 차이를 한 문장으로 설명해 보세요.
3. 응답률 30%인 설문 결과를 어떻게 조심해서 읽어야 할지 적어 보세요.

## 정리와 다음 글

표본과 모집단의 관계를 이해하면 통계가 왜 항상 불확실성과 함께 다녀야 하는지도 함께 보입니다. 표본은 전체의 일부이기 때문에 대표성, 편향, 응답률 같은 조건을 확인하지 않으면 숫자의 정밀함이 오히려 착시를 만들 수 있습니다.

다음 글에서는 추정을 다룹니다. 표본에서 계산한 통계량으로 모집단의 모수를 어떻게 가늠하는지, 그리고 그 추정값에 어떤 오차가 붙는지 봅니다.

## 표본 설계 실전: 편향을 줄이는 운영 절차

표본 설계는 분석 품질의 70%를 결정합니다. 특히 온라인 서비스에서는 표본 추출보다 비응답과 누락 집단이 더 큰 문제를 만들기 쉽습니다.

### 운영 절차

1. 모집단 정의를 문장으로 고정합니다.
2. 추출 프레임(누가 뽑힐 수 있는지)을 기록합니다.
3. 층화 기준(플랜, 지역, 기기)을 미리 정의합니다.
4. 응답률과 비응답자 특성을 동시에 기록합니다.
5. 가중치 보정 여부를 명시합니다.

### 층화 추출 + 가중치 보정 예제

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
pop = pd.DataFrame({
    'plan': rng.choice(['free', 'pro', 'enterprise'], size=30000, p=[0.78, 0.18, 0.04]),
    'satisfaction': rng.normal(3.9, 0.6, 30000).clip(1, 5),
})

# 층화 추출
sample = pop.groupby('plan', group_keys=False).apply(lambda g: g.sample(n=500, random_state=42))

# 응답 편향 가정: enterprise 응답률이 높음
resp_prob = sample['plan'].map({'free': 0.35, 'pro': 0.45, 'enterprise': 0.70})
resp = sample[np.random.rand(len(sample)) < resp_prob.to_numpy()]

# 단순 평균
naive = resp['satisfaction'].mean()

# 가중치 보정
pop_dist = pop['plan'].value_counts(normalize=True)
resp_dist = resp['plan'].value_counts(normalize=True)
weights = resp['plan'].map((pop_dist / resp_dist).to_dict())
weighted = np.average(resp['satisfaction'], weights=weights)

print(f"단순 평균: {naive:.3f}")
print(f"가중 보정 평균: {weighted:.3f}")
```

가중 보정은 편향을 완전히 없애지는 못하지만, 표본-모집단 분포 차이를 줄이는 데 실용적입니다.

## 추가 메모: 검증 가능한 의사결정 문장

분석 결과를 보고할 때는 "좋아 보입니다" 같은 모호한 문장을 피하고, 기준과 근거를 한 줄에 함께 적는 것이 좋습니다. 예를 들어 "전환율 +0.6%p, 95% 신뢰구간 +0.1~+1.1%p, p=0.014, 월간 기대효과 +320건, 2주 재검증 조건부 배포"처럼 쓰면 의사결정 책임이 명확해집니다. 이런 형식은 통계 도구가 바뀌어도 유지되는 팀 자산입니다.

## 처음 질문으로 돌아가기

- **모집단과 표본은 어떻게 구분할까요?**
  - 모집단은 이론상 전체(예: 지구의 모든 사용자), 표본은 실제 측정한 일부(예: 현재까지 모은 응답자)입니다.
- **표본이 모집단을 닮게 만드는 핵심 조건은 무엇일까요?**
  - 표본 크기와 선택 방식(무작위인지 편향된 건 아닌지)이 추론 정확도를 결정합니다.
- **무작위 추출은 왜 그렇게 자주 등장할까요?**
  - 편향된 표본에서 나온 결론은 운영에서 역효과를 낼 수 있으므로, 표본 구성을 정기적으로 검증합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- **표본과 모집단 (현재 글)**
- 추정 (예정)
- 신뢰구간 (예정)
- 가설검정 (예정)
- 상관과 회귀 (예정)
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)

<!-- toc:end -->

## 참고 자료

- [Pew Research — Sampling Methodology](https://www.pewresearch.org/our-methods/u-s-surveys/)
- [scikit-learn — Stratified Sampling](https://scikit-learn.org/stable/modules/cross_validation.html)
- [OpenIntro — Sampling Principles](https://www.openintro.org/book/os/)
- [Wikipedia — Selection Bias](https://en.wikipedia.org/wiki/Selection_bias)

### 비응답 편향

비응답 편향(Non-response bias)은 응답하지 않은 사람들이 응답한 사람들과 체계적으로 다를 때 발생합니다. 만족도 조사에서 불만족한 사람이 응답을 건너뛰면, 남은 응답만으로 계산한 평균은 실제보다 높게 나옵니다.

비응답 편향을 줄이는 방법:

1. **응답률을 높입니다**: 리마인더, 인센티브, 짧은 설문으로 응답 장벽을 낮춥니다
2. **비응답자 특성을 추적합니다**: 나이, 플랜, 활동 빈도 같은 메타데이터로 응답자와 비응답자 분포를 비교합니다
3. **가중치를 적용합니다**: 비응답자 특성을 반영해 응답자 데이터에 가중치를 부여합니다

```python
import pandas as pd
import numpy as np

# 모집단 (plan 분포)
population = pd.DataFrame({
    "user_id": range(1, 1001),
    "plan": np.random.choice(["free", "pro"], size=1000, p=[0.8, 0.2]),
    "satisfaction": np.random.choice([1, 2, 3, 4, 5], size=1000)
})

# 비응답 편향 시뮬레이션: pro 사용자는 응답률 높음
response_prob = population["plan"].map({"free": 0.1, "pro": 0.5})
responded = np.random.rand(len(population)) < response_prob

responses = population[responded]

print(f"모집단 plan 분포:\n{population['plan'].value_counts(normalize=True)}")
print(f"\n응답자 plan 분포:\n{responses['plan'].value_counts(normalize=True)}")
print(f"\n응답률: {len(responses) / len(population):.1%}")
```

응답자 중 pro 비율이 모집단보다 훨씬 높게 나오면 비응답 편향이 있다는 신호입니다. 이럴 때는 plan별 가중치를 적용해 보정해야 합니다.

### 생존자 편향

생존자 편향(Survivorship bias)은 "살아남은" 데이터만 보고 판단할 때 생깁니다. 성공한 스타트업만 분석하면 실패 요인을 놓치고, 활발한 사용자만 분석하면 이탈 원인을 놓칩니다.

예시:

- 앱 리뷰는 극단적으로 만족하거나 불만족한 사람만 남깁니다. 중간층은 조용히 떠납니다
- 1년 이상 사용자만 분석하면 초기 이탈 원인을 절대 찾을 수 없습니다
- 고객 만족도 조사를 기존 고객에게만 보내면 이미 떠난 고객의 목소리는 들을 수 없습니다

생존자 편향을 피하려면:

1. **전체 코호트를 추적합니다**: 가입 시점부터 이탈까지 전체 여정을 봅니다
2. **이탈자 인터뷰를 포함합니다**: 성공 사례만큼 실패 사례도 체계적으로 수집합니다
3. **타임라인 분석을 합니다**: 어느 시점에 누가 빠져나갔는지 시각화합니다

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Sampling, Population, Bias, Beginner
