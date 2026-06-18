---
series: probability-101
episode: 7
title: "바이브코딩을 위한 확률 기초 (7/10): 이산분포"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 이산분포
  - 이항분포
  - AI확률점수
language: ko
---

# 바이브코딩을 위한 확률 기초 (7/10): 이산분포

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 7편입니다. AI 시스템이 출력하는 카운트 데이터(클릭 수, 전환 수, 오류 횟수)를 제대로 모델링하려면 이산분포를 알아야 합니다.

---

바이브코딩으로 A/B 테스트를 설계할 때, 또는 API 오류 모니터링 시스템을 만들 때, 자연스럽게 숫자를 세는 문제를 만납니다. "1000명 중 몇 명이 전환했나?" "시간당 몇 번 오류가 났나?" "재시도를 몇 번 해야 성공할까?" 이런 질문들은 이산분포로 모델링할 수 있습니다. 이름보다 상황을 보세요.

> "이산분포를 안다는 것은 공식을 외우는 게 아닙니다. 어떤 데이터가 어떤 분포를 따르는지 알아보는 눈을 기르는 것입니다. AI 시스템의 카운트 데이터 대부분이 이 분포들 중 하나에 해당합니다."

## 이 글에서 다룰 질문들

- 전환(conversion)처럼 0/1 데이터는 어떤 분포일까요?
- A/B 테스트 결과(n번 중 성공 횟수)는 언제 이항분포일까요?
- API 오류 횟수를 포아송분포로 모델링하면 어떤 이점이 있을까요?
- 이산분포 선택을 잘못하면 어떤 오류가 생길까요?
- 과분산(overdispersion)이 뭔지, AI 시스템에서 왜 중요할까요?

---

## 바이브코딩 관점: 카운트 데이터를 분포로 모델링하기

AI 시스템을 운영하다 보면 숫자를 세는 지표가 많습니다. 이 지표들을 적절한 분포로 모델링하면 통계적 판단이 훨씬 쉬워집니다.

### Before: 카운트 데이터를 그냥 평균으로만 보기

```python
# A/B 테스트 결과
conversions_A = 120  # 1000명 중 전환
conversions_B = 150  # 1000명 중 전환

rate_A = 120 / 1000
rate_B = 150 / 1000

print(f"A 전환율: {rate_A:.1%}")
print(f"B 전환율: {rate_B:.1%}")
print(f"차이: {rate_B - rate_A:.1%}")

# 그런데 이 차이가 통계적으로 유의미한가?
# 단순 비교로는 알 수 없음
```

### After: 이항분포로 통계적 판단

```python
import numpy as np
from scipy import stats

n_A, k_A = 1000, 120
n_B, k_B = 1000, 150

p_A = k_A / n_A
p_B = k_B / n_B

# 이항분포로 불확실성 계산
dist_A = stats.binom(n=n_A, p=p_A)
dist_B = stats.binom(n=n_B, p=p_B)

# 95% 신뢰구간
se_A = np.sqrt(p_A * (1 - p_A) / n_A)
se_B = np.sqrt(p_B * (1 - p_B) / n_B)

print(f"A: {p_A:.1%} ± {1.96*se_A:.1%}")
print(f"B: {p_B:.1%} ± {1.96*se_B:.1%}")

# 통계적 유의성 검정
p_pool = (k_A + k_B) / (n_A + n_B)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
z_stat = (p_B - p_A) / se_pool
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

print(f"p-value: {p_value:.4f}")
print(f"결론: {'유의미한 차이' if p_value < 0.05 else '차이 없음'}")
```

---

## 핵심 이산분포 비교표

| 분포 | 질문 형태 | AI 활용 예시 | 모수 | E[X] | Var(X) |
| --- | --- | --- | --- | --- | --- |
| 베르누이 | 성공/실패? | 클릭 여부 | p | p | p(1-p) |
| 이항 | n번 중 성공 횟수? | A/B 테스트 전환 수 | n, p | np | np(1-p) |
| 기하 | 첫 성공까지 횟수? | API 재시도 횟수 | p | 1/p | (1-p)/p² |
| 포아송 | 구간 내 발생 수? | 시간당 오류 수 | λ | λ | λ |

```python
from scipy import stats

# 각 분포 직관 확인
print("=== 이항분포: A/B 테스트 ===")
# 1000명에게 버전 B를 보여줄 때 전환자 수 분포
binom = stats.binom(n=1000, p=0.15)
print(f"기대 전환수: {binom.mean():.0f}")
print(f"표준편차: {binom.std():.1f}")
print(f"P(150명 이상 전환): {1 - binom.cdf(149):.3f}")

print("\n=== 포아송분포: API 오류 모니터링 ===")
# 시간당 평균 3건 오류
poisson = stats.poisson(mu=3)
print(f"P(오류=0): {poisson.pmf(0):.4f}")
print(f"P(오류>=8): {1 - poisson.cdf(7):.4f}")
print(f"95 퍼센타일: {poisson.ppf(0.95):.0f}건")

print("\n=== 기하분포: API 재시도 ===")
# 각 시도 성공률 70%, 첫 성공까지 시도 횟수
geom = stats.geom(p=0.7)
print(f"평균 시도 횟수: {geom.mean():.2f}")
print(f"P(3번 이내 성공): {geom.cdf(3):.3f}")
```

---

## 포아송 이상탐지: AI 오류 모니터링

포아송분포로 "정상 범위"를 정의하면 이상 탐지를 자동화할 수 있습니다.

```python
from scipy import stats
import numpy as np

def setup_anomaly_detector(baseline_rate, confidence=0.99):
    """
    포아송분포 기반 이상 탐지 시스템
    baseline_rate: 정상 상태 시간당 이벤트 수
    """
    dist = stats.poisson(mu=baseline_rate)
    upper_threshold = dist.ppf(confidence)

    return {
        "baseline": baseline_rate,
        "threshold": upper_threshold,
        "dist": dist
    }

def check_anomaly(detector, observed_count):
    """관측값이 이상인지 판단"""
    p_value = 1 - detector["dist"].cdf(observed_count - 1)
    is_anomaly = observed_count > detector["threshold"]

    print(f"관측값: {observed_count}")
    print(f"임계값: {detector['threshold']:.0f}")
    print(f"P(X >= {observed_count}): {p_value:.5f}")
    print(f"이상 탐지: {'경보 발생' if is_anomaly else '정상'}")

# API 오류 모니터링: 정상 시간당 5건
detector = setup_anomaly_detector(baseline_rate=5)
print("=== 정상 상황 ===")
check_anomaly(detector, 7)

print("\n=== 이상 상황 ===")
check_anomaly(detector, 15)
```

---

## 분포 선택 가이드

```
데이터가 정수인가?
└─ YES
   └─ 한 번의 0/1 실험? → 베르누이
   └─ n번 반복, 성공 횟수? → 이항분포
   └─ 첫 성공까지 횟수? → 기하분포
   └─ 단위 구간 내 도착 횟수? → 포아송분포
   └─ 비복원 추출? → 초기하분포
└─ NO → 연속분포 계열 (다음 편 참조)
```

```python
def identify_distribution(description):
    """데이터 설명에서 분포 추천"""
    keywords = {
        "전환 여부": "베르누이(p=전환율)",
        "전환 수": "이항분포(n=방문자수, p=전환율)",
        "재시도": "기하분포(p=성공률)",
        "오류 수": "포아송분포(λ=평균 오류수)",
        "도착 수": "포아송분포(λ=평균 도착수)",
    }
    for key, dist in keywords.items():
        if key in description:
            return f"추천 분포: {dist}"
    return "더 많은 정보 필요"

# 예시
examples = [
    "사용자가 광고를 클릭한 전환 여부",
    "100명에게 노출했을 때 광고 클릭 전환 수",
    "API 호출 성공까지의 재시도 횟수",
    "1분 동안 서버에 들어오는 요청 도착 수",
]

for ex in examples:
    print(f"{ex}")
    print(f"  → {identify_distribution(ex)}\n")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| 포아송에서 평균≠분산 무시 | 포아송은 E[X]=Var(X)=λ를 가정함 | 데이터의 분산/평균 비율 확인 |
| 이항분포 독립 가정 무시 | 각 시도가 독립이어야 함 | 시도 간 의존성 확인 |
| 작은 표본으로 분포 단정 | 10개 샘플로 분포 결론 냄 | 더 많은 데이터 수집 후 판단 |
| 임계값에 포아송 안 쓰기 | 직관으로만 이상 탐지 | 포아송 기반 통계적 임계값 설정 |

---

## AI 팁: 과분산 확인하기

포아송을 가정했는데 실제 데이터의 분산이 평균보다 훨씬 크면 과분산(overdispersion)입니다.

```python
import numpy as np
from scipy import stats

def check_overdispersion(data):
    """포아송 가정의 과분산 여부 확인"""
    mean = np.mean(data)
    var = np.var(data)
    ratio = var / mean

    print(f"평균: {mean:.2f}")
    print(f"분산: {var:.2f}")
    print(f"분산/평균 비율: {ratio:.2f}")

    if ratio < 1.5:
        print("결론: 포아송 적합 (비율 ≈ 1)")
    else:
        print("결론: 과분산 - 음이항분포 고려 권장")

    return ratio

# 정상 트래픽 (포아송)
normal_traffic = np.random.poisson(lam=10, size=1000)
print("=== 정상 트래픽 ===")
check_overdispersion(normal_traffic)

# 이상 트래픽 (과분산)
bursty_traffic = np.concatenate([
    np.random.poisson(lam=5, size=700),   # 평상시
    np.random.poisson(lam=30, size=300),  # 버스트
])
print("\n=== 버스트 트래픽 ===")
check_overdispersion(bursty_traffic)
```

---

## 실전 체크리스트

- [ ] 베르누이, 이항, 기하, 포아송의 차이를 실무 예시로 설명할 수 있다
- [ ] A/B 테스트 결과를 이항분포로 분석할 수 있다
- [ ] 포아송분포로 이상 탐지 임계값을 설정할 수 있다
- [ ] 포아송 과분산 여부를 데이터로 확인할 수 있다
- [ ] 기하분포로 재시도 횟수의 기대값을 계산할 수 있다
- [ ] MLE로 포아송의 λ를 추정할 수 있다 (= 표본평균)

---

## 처음 질문으로 돌아가기

- **전환(conversion)처럼 0/1 데이터는 어떤 분포일까요?**
  베르누이분포입니다. 한 번의 독립 시행에서 성공(1) 또는 실패(0)를 관찰합니다. A/B 테스트의 개별 사용자 전환 여부가 이에 해당합니다.

- **API 오류 횟수를 포아송으로 모델링하면 어떤 이점이 있을까요?**
  분포를 알면 "정상 범위"를 통계적으로 정의할 수 있습니다. P(X >= 10) < 0.01이라면 10건 이상 오류가 발생할 때 자동으로 경보를 울릴 수 있습니다.

- **과분산이 뭔지, AI 시스템에서 왜 중요할까요?**
  포아송은 평균=분산을 가정하는데, 실제 데이터 분산이 평균보다 훨씬 크면 과분산입니다. 버스트 트래픽, 집단별 다른 평균 등이 원인이며, 이 경우 포아송 대신 음이항분포를 써야 이상 탐지 임계값이 더 정확합니다.

---

## 정리

이산분포는 AI 시스템의 카운트 데이터를 읽는 기본 언어입니다. 전환 수는 이항분포, 오류 횟수는 포아송분포, 재시도 횟수는 기하분포로 모델링하면 단순 평균을 넘어 통계적 판단이 가능해집니다. 다음 글에서는 키, 응답시간, 예측값처럼 연속적인 값을 다루는 연속분포를 알아봅니다.

---

## 참고 자료

- [Wikipedia — Binomial distribution](https://en.wikipedia.org/wiki/Binomial_distribution)
- [Wikipedia — Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution)
- [scipy.stats — Discrete](https://docs.scipy.org/doc/scipy/reference/stats.html#discrete-distributions)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 확률 기초 (1/10): 확률이란 무엇인가?
- 바이브코딩을 위한 확률 기초 (2/10): 사건과 표본공간
- 바이브코딩을 위한 확률 기초 (3/10): 조건부확률
- 바이브코딩을 위한 확률 기초 (4/10): 베이즈 정리
- 바이브코딩을 위한 확률 기초 (5/10): 확률변수
- 바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산
- **바이브코딩을 위한 확률 기초 (7/10): 이산분포 (현재 글)**
- 바이브코딩을 위한 확률 기초 (8/10): 연속분포
- 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 이산분포, 이항분포, AI확률점수
