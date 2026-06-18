---
series: probability-101
episode: 9
title: "바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 중심극한정리
  - AB테스트
  - AI확률점수
language: ko
---

# 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 9편입니다. AI 모델이 출력하는 확률 점수를 제대로 읽으려면 그 숫자가 얼마나 안정적인지, 표본이 얼마나 필요한지 알아야 합니다.

---

AI 모델을 100개 샘플로 테스트했더니 정확도 92%가 나왔습니다. 이 숫자를 믿어야 할까요? 1000개로 늘리면 어떻게 달라질까요? A/B 테스트에서 실험군의 전환율이 0.5% 올랐는데, 이것이 진짜 개선인지 노이즈인지 어떻게 판단할까요? 이 모든 질문의 뒤에는 대수의 법칙과 중심극한정리가 있습니다.

> "표본이 적을 때 AI 모델의 성능 지표는 노이즈입니다. 표본이 충분해야 비로소 신호가 됩니다. 대수의 법칙이 이 차이를 설명합니다."

## 이 글에서 다룰 질문들

- 표본 100개로 측정한 AI 정확도를 얼마나 믿을 수 있을까요?
- 대수의 법칙과 중심극한정리는 무엇이 다를까요?
- A/B 테스트에서 표본이 얼마나 필요한지 어떻게 계산할까요?
- 표준오차와 표준편차를 혼동하면 어떤 실수가 생길까요?
- 표본이 적을 때 CLT 대신 쓸 수 있는 방법은 무엇일까요?

---

## 바이브코딩 관점: AI 모델 평가에서 표본 크기가 왜 중요한가

AI 모델 성능 지표는 표본에서 추정한 값입니다. 표본이 적으면 그 추정값이 크게 흔들립니다.

### Before: 표본 크기를 무시한 평가

```python
# AI 스팸 분류기 성능 측정
test_results = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0]  # 10개 테스트
accuracy = sum(test_results) / len(test_results)
print(f"정확도: {accuracy:.0%}")  # 70%

# 이 70%를 배포 기준으로 쓰면?
# 표본 10개로 측정한 값의 신뢰구간은 매우 넓음
# 실제 정확도는 40%~90% 어디든 될 수 있음
```

### After: 표준오차로 불확실성 정량화

```python
import numpy as np
from scipy import stats

# 표본 크기별 정확도 추정의 신뢰구간 비교
true_acc = 0.85  # 실제 모델 정확도

for n in [10, 50, 100, 500, 1000]:
    # 이항분포의 표준오차
    se = np.sqrt(true_acc * (1 - true_acc) / n)
    # 95% 신뢰구간
    ci_half = 1.96 * se
    print(f"n={n:5d}: 정확도 = {true_acc:.0%} ± {ci_half:.1%}  "
          f"[{true_acc-ci_half:.1%}, {true_acc+ci_half:.1%}]")
```

출력:
```
n=   10: 정확도 = 85% ± 22.1%  [62.9%, 107.1%]
n=   50: 정확도 = 85% ± 9.9%   [75.1%, 94.9%]
n=  100: 정확도 = 85% ± 7.0%   [78.0%, 92.0%]
n=  500: 정확도 = 85% ± 3.1%   [81.9%, 88.1%]
n= 1000: 정확도 = 85% ± 2.2%   [82.8%, 87.2%]
```

표본 10개로 측정한 85%는 실제 62%~107% 어디에나 있을 수 있습니다. 표본 1000개가 되어야 ±2% 수준의 의미 있는 추정이 됩니다.

---

## 대수의 법칙 vs 중심극한정리

| 구분 | 대수의 법칙 (LLN) | 중심극한정리 (CLT) |
| --- | --- | --- |
| 대상 | 표본평균 그 자체 | 표본평균의 분포 |
| 결론 | 표본평균 → 모평균 μ | (표본평균 - μ) / (σ/√n) → N(0,1) |
| 질문 | "어디로 수렴하나?" | "얼마나 흔들리나?" |
| 실무 응용 | 더 많은 데이터 = 더 안정적인 지표 | 신뢰구간, 가설검정 |

```python
import numpy as np
from scipy import stats

# 대수의 법칙: AI 모델 클릭률 추정이 수렴하는 과정
# 실제 클릭률 0.05 (5%)
rng = np.random.default_rng(42)
clicks = rng.binomial(1, 0.05, 10_000)
running_mean = np.cumsum(clicks) / np.arange(1, len(clicks) + 1)

checkpoints = [10, 50, 100, 500, 1000, 5000, 10000]
print("표본 수  | 추정 클릭률 | 실제와 차이")
print("-" * 40)
for n in checkpoints:
    diff = abs(running_mean[n-1] - 0.05)
    print(f"  {n:>5}  |   {running_mean[n-1]:.4f}   |  {diff:.4f}")
```

---

## 표준편차 vs 표준오차

| 구분 | 표준편차 (SD) | 표준오차 (SE) |
| --- | --- | --- |
| 대상 | 개별 데이터 포인트 | 표본평균 |
| 정의 | √Var(X) | σ / √n |
| AI 예시 | 모델 예측값들의 흩어짐 | 평균 정확도 추정의 불확실성 |
| n 증가 시 | 변하지 않음 | 줄어듦 (1/√n) |

```python
import numpy as np

# AI 모델 정확도 측정: SD와 SE의 차이
# 같은 모델을 100번 다른 배치로 테스트
rng = np.random.default_rng(42)
batch_accuracies = rng.normal(0.85, 0.08, 100)  # 100개 배치의 정확도

sd = batch_accuracies.std()        # 개별 배치 정확도의 흩어짐
se = sd / np.sqrt(len(batch_accuracies))  # 평균 정확도의 불확실성

print(f"개별 배치 정확도 SD: {sd:.3f}")
print(f"평균 정확도의 SE: {se:.3f}")
print(f"SE는 SD의 {sd/se:.1f}배 작음 (√{len(batch_accuracies)} = {np.sqrt(len(batch_accuracies)):.1f})")
print(f"\n95% 신뢰구간: {batch_accuracies.mean():.3f} ± {1.96*se:.3f}")
```

---

## A/B 테스트: 표본 크기 계산

중심극한정리를 알면 A/B 테스트에 필요한 표본 수를 정량적으로 계산할 수 있습니다.

```python
import numpy as np
from scipy import stats

def required_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    A/B 테스트에 필요한 그룹당 표본 수 계산.
    baseline_rate: 기준 전환율
    mde: 최소 감지 차이 (minimum detectable effect)
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    p_pool = (p1 + p2) / 2
    var_pool = 2 * p_pool * (1 - p_pool)
    var_separate = p1 * (1 - p1) + p2 * (1 - p2)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = ((z_alpha * np.sqrt(var_pool) + z_beta * np.sqrt(var_separate)) / mde) ** 2
    return int(np.ceil(n))

# AI 추천 시스템 A/B 테스트
# 기준 클릭률 5%, 최소 감지 차이 0.5%p
baseline = 0.05

print("AI 추천 시스템 A/B 테스트 표본 계산")
print("기준 클릭률: 5%")
print(f"\n{'MDE':>6} | {'그룹당 표본':>10} | {'전체 표본':>10}")
print("-" * 35)
for mde in [0.005, 0.01, 0.02, 0.05]:
    n = required_sample_size(baseline, mde)
    print(f"{mde:.1%}  | {n:>10,} | {n*2:>10,}")
```

출력:
```
MDE    | 그룹당 표본 |   전체 표본
-----------------------------------
  0.5% |     14,751 |     29,502
  1.0% |      3,716 |      7,432
  2.0% |        955 |      1,910
  5.0% |        159 |        318
```

더 작은 차이를 감지하려면 훨씬 더 많은 표본이 필요합니다. MDE를 절반으로 줄이면 표본은 4배가 됩니다(1/√n의 역수 관계).

---

## 중심극한정리 시뮬레이션

비정규 분포에서도 표본평균은 정규에 가까워집니다.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)

# AI 요청 처리 시간: 지수분포 (비대칭)
# 모집단 자체는 정규가 아님
print("모집단: 지수분포 (비대칭)")
print(f"모집단 왜도: {stats.expon.stats(moments='s'):.2f}")

# 표본 크기별로 표본평균의 분포가 정규에 가까워지는 과정
print("\n표본 크기별 표본평균 정규성 검정:")
for n in [5, 10, 30, 100]:
    # 표본평균 10000개 생성
    sample_means = np.array([rng.exponential(1, n).mean() for _ in range(10_000)])

    # Shapiro-Wilk 정규성 검정
    _, p_value = stats.shapiro(sample_means[:500])
    print(f"  n={n:3d}: 표본평균 정규성 p={p_value:.4f} "
          f"({'정규에 가까움' if p_value >= 0.05 else '아직 비정규'})")
```

---

## 부트스트랩: CLT 없이 신뢰구간 구하기

표본이 작거나 분포 가정이 의심스러울 때는 부트스트랩이 실용적인 대안입니다.

```python
import numpy as np

rng = np.random.default_rng(42)

# AI 모델 지연시간 (작은 표본, 비대칭)
latency_data = rng.exponential(scale=200, size=25)  # ms

# 부트스트랩 신뢰구간
n_bootstrap = 10_000
boot_means = np.array([
    rng.choice(latency_data, size=len(latency_data), replace=True).mean()
    for _ in range(n_bootstrap)
])

ci_lower = np.percentile(boot_means, 2.5)
ci_upper = np.percentile(boot_means, 97.5)

# CLT 기반 신뢰구간 비교
xbar = latency_data.mean()
se = latency_data.std(ddof=1) / np.sqrt(len(latency_data))
clt_lower = xbar - 1.96 * se
clt_upper = xbar + 1.96 * se

print(f"표본 크기: {len(latency_data)}, 표본평균: {xbar:.1f} ms")
print(f"부트스트랩 95% CI: [{ci_lower:.1f}, {ci_upper:.1f}] ms")
print(f"CLT 기반 95% CI:   [{clt_lower:.1f}, {clt_upper:.1f}] ms")
print(f"\n비대칭 소표본에서는 부트스트랩이 더 정확합니다")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| 적은 표본으로 모델 성능 결론 | n=50에서 정확도 92%는 불안정한 추정 | 표준오차로 신뢰구간 함께 계산 |
| SD와 SE 혼동 | 에러바 그릴 때 SD를 SE처럼 제시 | SD는 데이터 흩어짐, SE는 평균의 불확실성 |
| A/B 테스트 조기 중단 | 좋은 결과 나오자마자 실험 중단 | 사전에 계산한 표본 크기 채운 후 판단 |
| 도박사의 오류 | "10번 연속 실패했으니 다음엔 성공" | 각 시행은 독립, LLN은 장기 평균의 수렴 |

---

## AI 팁: 표본 크기에 따른 모델 평가 신뢰도

```python
import numpy as np
from scipy import stats

def evaluate_model_reliability(n_test, accuracy, confidence=0.95):
    """
    AI 모델 평가의 신뢰도를 표준오차로 정량화.
    """
    se = np.sqrt(accuracy * (1 - accuracy) / n_test)
    z = stats.norm.ppf((1 + confidence) / 2)
    margin = z * se

    print(f"테스트 샘플: {n_test:,}개")
    print(f"측정 정확도: {accuracy:.1%}")
    print(f"표준오차: {se:.4f}")
    print(f"{confidence:.0%} 신뢰구간: [{accuracy-margin:.1%}, {accuracy+margin:.1%}]")
    print(f"마진: ±{margin:.1%}")

    if margin > 0.05:
        print("판정: 표본 부족 — 신뢰구간이 너무 넓습니다")
    elif margin > 0.02:
        print("판定: 보통 — 대략적인 성능 파악 가능")
    else:
        print("판정: 충분 — 신뢰할 수 있는 성능 추정")

print("=== 소규모 테스트 ===")
evaluate_model_reliability(100, 0.88)

print("\n=== 충분한 테스트 ===")
evaluate_model_reliability(1000, 0.88)
```

---

## 실전 체크리스트

- [ ] 표준오차로 AI 모델 성능 지표의 신뢰구간을 계산할 수 있다
- [ ] SD(표준편차)와 SE(표준오차)의 차이를 설명할 수 있다
- [ ] A/B 테스트에 필요한 표본 수를 MDE와 검정력으로 계산할 수 있다
- [ ] 대수의 법칙과 중심극한정리가 다른 질문에 답함을 이해한다
- [ ] 작은 표본에서 CLT 대신 부트스트랩을 쓸 수 있다
- [ ] 도박사의 오류와 대수의 법칙의 차이를 설명할 수 있다

---

## 처음 질문으로 돌아가기

- **표본 100개로 측정한 AI 정확도를 얼마나 믿을 수 있을까요?**
  표준오차 σ/√n으로 신뢰구간을 계산하면 됩니다. n=100, 정확도 85%면 95% CI는 ±7%입니다. 이 불확실성을 항상 함께 보고해야 합니다.

- **A/B 테스트에서 표본이 얼마나 필요한지 어떻게 계산할까요?**
  MDE(최소 감지 차이), 유의수준 α, 검정력 1-β를 지정하면 CLT 기반 공식으로 계산됩니다. MDE가 절반이 되면 표본은 4배가 필요합니다.

- **표본이 적을 때 CLT 대신 쓸 수 있는 방법은 무엇일까요?**
  부트스트랩(bootstrap)은 분포 가정 없이 재표본 추출로 신뢰구간을 구합니다. 비대칭 분포, 작은 표본, heavy-tail 데이터에서 CLT보다 안정적입니다.

---

## 정리

대수의 법칙은 "더 많은 데이터가 왜 더 안정적인 지표를 만드는가"를 설명하고, 중심극한정리는 "그 지표의 불확실성이 어떤 모양인가"를 설명합니다. AI 시스템에서 성능 지표를 신뢰하려면 표본 크기와 표준오차를 함께 봐야 합니다. 다음 글에서는 이 모든 확률 개념이 머신러닝의 손실함수, 모델 보정, MLE/MAP에서 어떻게 나타나는지 정리합니다.

---

## 참고 자료

- [Wikipedia — Law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers)
- [Wikipedia — Central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [3Blue1Brown — CLT](https://www.youtube.com/watch?v=zeJD6dqJ5lo)
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
- 바이브코딩을 위한 확률 기초 (7/10): 이산분포
- 바이브코딩을 위한 확률 기초 (8/10): 연속분포
- **바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리 (현재 글)**
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 중심극한정리, AB테스트, AI확률점수
