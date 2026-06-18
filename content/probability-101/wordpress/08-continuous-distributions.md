---
series: probability-101
episode: 8
title: "바이브코딩을 위한 확률 기초 (8/10): 연속분포"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 연속분포
  - 정규분포
  - AI확률점수
language: ko
---

# 바이브코딩을 위한 확률 기초 (8/10): 연속분포

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 8편입니다. AI 모델이 출력하는 확률 점수를 제대로 읽으려면 연속형 데이터를 다루는 분포의 언어를 알아야 합니다.

---

AI 회귀 모델이 "내일 서버 응답시간은 230ms"라고 예측했을 때, 그 숫자 하나만 믿어야 할까요? 실제 AI 시스템에서 더 중요한 질문은 "230ms 이상일 확률이 얼마인가", "SLA인 300ms를 넘길 가능성은 얼마인가"입니다. 이 질문들은 연속분포로만 답할 수 있습니다. 키, 응답시간, 가격 예측처럼 연속적인 값을 다루는 AI 시스템에서는 분포의 언어가 필수입니다.

> "AI 회귀 모델의 출력은 단일 숫자가 아니라 분포입니다. 그 분포를 읽지 못하면 예측의 불확실성을 놓칩니다."

## 이 글에서 다룰 질문들

- AI 회귀 모델의 출력을 왜 분포로 봐야 할까요?
- PDF 값이 확률이 아닌 이유를 AI 모델 맥락에서 어떻게 이해할까요?
- 68-95-99.7 규칙으로 AI 이상치 탐지를 어떻게 할까요?
- 응답시간 분포가 정규가 아닐 때 어떤 분포를 써야 할까요?
- SLA 분석에서 연속분포를 어떻게 활용할까요?

---

## 바이브코딩 관점: 회귀 예측을 분포로 읽기

AI 회귀 모델의 점 예측(point prediction)을 그대로 쓰면 중요한 정보를 잃습니다. 분포로 보면 불확실성, SLA 위반 확률, 신뢰구간을 함께 얻을 수 있습니다.

### Before: 점 예측만 쓰기

```python
# AI 서버 응답시간 예측 모델
predicted_ms = model.predict(features)
# [230.0]

# 단순히 230ms라는 숫자만 보고 판단
if predicted_ms[0] < 300:
    print("SLA 충족 예상")
# 하지만 230ms가 나오더라도 실제로는 300ms를 넘길 수 있음
# 분산을 전혀 고려하지 않음
```

### After: 예측 분포로 보기

```python
from scipy import stats
import numpy as np

# 모델이 평균과 표준편차를 함께 출력한다고 가정
# (또는 앙상블/드롭아웃으로 불확실성 추정)
predicted_mean = 230   # ms
predicted_std = 45     # ms

# 예측 분포 생성
response_dist = stats.norm(loc=predicted_mean, scale=predicted_std)

# SLA 위반 확률
sla_limit = 300  # ms
p_violation = 1 - response_dist.cdf(sla_limit)
print(f"SLA({sla_limit}ms) 위반 확률: {p_violation:.1%}")

# 95% 신뢰구간
lower = response_dist.ppf(0.025)
upper = response_dist.ppf(0.975)
print(f"95% 예측 구간: [{lower:.0f}, {upper:.0f}] ms")

# 99 퍼센타일: 최악의 1% 케이스
p99 = response_dist.ppf(0.99)
print(f"P99 응답시간: {p99:.0f} ms")
```

점 예측만 보면 SLA 충족처럼 보여도 분포로 보면 11%의 위반 확률이 있을 수 있습니다.

---

## 연속분포 비교

| 분포 | 매개변수 | 주요 용도 | AI 예시 |
| --- | --- | --- | --- |
| 균등분포 | a, b (구간) | 구간 내 고른 확률 | 하이퍼파라미터 탐색 범위 |
| 정규분포 | μ, σ | 측정 오차, 평균 분포 | 회귀 예측 오차, 임베딩 좌표 |
| 지수분포 | λ (rate) | 대기시간, 고장 간격 | 요청 간 도착 시간, 재시도 간격 |
| 감마분포 | α (shape), β (scale) | 여러 대기시간의 합 | 파이프라인 총 처리 시간 |

```python
from scipy import stats
import numpy as np

# 연속형: 회귀 모델 출력 (응답시간 예측)
# 모델이 정규분포 N(230, 45²)로 예측
response_dist = stats.norm(loc=230, scale=45)

# PDF 값은 확률이 아님!
print("PDF(230):", response_dist.pdf(230))  # 0.00886 — 확률이 아닌 밀도

# 구간 확률로 읽어야 함
print("P(200~260ms):", response_dist.cdf(260) - response_dist.cdf(200))

# 지수분포: 요청 간 도착 간격 (평균 0.2초 = 초당 5 요청)
arrival_dist = stats.expon(scale=0.2)
print("P(다음 요청이 0.5초 이내 도착):", arrival_dist.cdf(0.5))
```

---

## 68-95-99.7 규칙: AI 이상치 탐지의 기준선

정규분포의 68-95-99.7 규칙은 AI 시스템에서 이상치를 탐지하는 가장 간단한 기준입니다.

```python
from scipy import stats
import numpy as np

# AI 모델 예측 오차 분포 분석
# 정상 운영 시 측정한 응답시간 분포
mu, sigma = 200, 30  # 평균 200ms, 표준편차 30ms

rv = stats.norm(loc=mu, scale=sigma)

# 68-95-99.7 규칙
ranges = [
    (1, mu - sigma, mu + sigma),
    (2, mu - 2*sigma, mu + 2*sigma),
    (3, mu - 3*sigma, mu + 3*sigma),
]

print("시그마 범위별 포함 확률:")
for n_sigma, lower, upper in ranges:
    p = rv.cdf(upper) - rv.cdf(lower)
    print(f"  ±{n_sigma}σ [{lower:.0f}, {upper:.0f}] ms: {p:.1%}")

# 이상치 탐지: 3σ 임계값
threshold_upper = mu + 3 * sigma  # 290ms
threshold_lower = mu - 3 * sigma  # 110ms

new_response = 310  # ms
is_anomaly = not (threshold_lower <= new_response <= threshold_upper)
print(f"\n응답시간 {new_response}ms: {'이상 탐지' if is_anomaly else '정상'}")
print(f"(정상 범위: {threshold_lower}~{threshold_upper}ms)")
```

---

## 지수분포: 무기억성과 AI 재시도 로직

지수분포의 핵심 성질인 무기억성은 AI 시스템 설계에서 중요한 함의를 가집니다.

```python
from scipy import stats
import numpy as np

# AI API 오류 간격이 지수분포를 따른다고 가정
# 평균 오류 간격: 20분 (rate = 1/20)
error_dist = stats.expon(scale=20)  # 분 단위

# 무기억성: 이미 10분 기다렸어도 앞으로 기다릴 시간 분포는 동일
# P(X > 10+t | X > 10) = P(X > t)
t = 10

# 조건부 확률 계산
p_gt_20 = 1 - error_dist.cdf(20)
p_gt_10 = 1 - error_dist.cdf(10)
p_conditional = p_gt_20 / p_gt_10  # P(X>20 | X>10)

p_gt_10_fresh = 1 - error_dist.cdf(10)  # P(X>10) 새로 시작한 것처럼

print(f"P(오류 10분 이후 | 이미 10분 지남): {p_conditional:.4f}")
print(f"P(오류 10분 이후): {p_gt_10_fresh:.4f}")
print(f"동일하다 (무기억성): {abs(p_conditional - p_gt_10_fresh) < 1e-10}")

# AI 서비스 SLA 계산
p_within_sla = error_dist.cdf(30)  # 30분 이내 다음 오류 발생 확률
print(f"\n다음 오류가 30분 내 발생 확률: {p_within_sla:.1%}")
```

---

## QQ-plot으로 분포 가정 검증하기

AI 시스템 로그 데이터가 정규분포를 따른다고 가정하기 전에 검증이 필요합니다.

```python
from scipy import stats
import numpy as np

# AI 서버 응답시간 데이터 (실제 지수분포를 따름)
rng = np.random.default_rng(42)
response_times = rng.exponential(scale=200, size=500) + 50

# 정규성 검정
stat, p_value = stats.shapiro(response_times[:500])
print(f"Shapiro-Wilk 검정: p={p_value:.4e}")
print(f"정규분포 가정: {'기각 — 정규분포가 아닙니다' if p_value < 0.05 else '유지'}")

# QQ-plot 수치로 확인
theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, 20))
sample_q = np.quantile(response_times, np.linspace(0.01, 0.99, 20))
slope, intercept, r_value, _, _ = stats.linregress(theoretical_q, sample_q)
print(f"\nQQ-plot R²: {r_value**2:.4f}")
print(f"R²가 0.95 미만이면 정규분포 가정 의심 필요")

# 응답시간처럼 오른쪽 꼬리 데이터는 로그 변환 후 정규 가정
log_times = np.log(response_times)
stat2, p_value2 = stats.shapiro(log_times[:500])
print(f"\n로그 변환 후 Shapiro-Wilk: p={p_value2:.4e}")
print(f"로그 정규분포 가정: {'유지' if p_value2 >= 0.05 else '기각'}")
```

---

## 몬테카를로 SLA 시뮬레이션

AI 마이크로서비스 파이프라인의 종단 지연(end-to-end latency)을 연속분포로 시뮬레이션합니다.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)
n_simulations = 100_000

# AI 파이프라인 각 단계의 응답시간 분포
gateway = rng.normal(10, 2, n_simulations)          # API 게이트웨이: 정규
inference = rng.gamma(3, 15, n_simulations)          # AI 추론: 감마 (평균 45ms)
db_lookup = rng.exponential(5, n_simulations)        # DB 조회: 지수

# 전체 응답시간
total = gateway + inference + db_lookup

# SLA 분석
p50 = np.percentile(total, 50)
p95 = np.percentile(total, 95)
p99 = np.percentile(total, 99)
sla_300ms = (total > 300).mean()

print(f"P50: {p50:.0f}ms | P95: {p95:.0f}ms | P99: {p99:.0f}ms")
print(f"300ms 초과 확률: {sla_300ms:.2%}")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| PDF 값을 확률로 읽기 | f(x)는 밀도이지 확률이 아님. 1보다 클 수 있음 | CDF 차이로 구간 확률 계산 |
| 응답시간에 정규 가정 | 응답시간은 양수이고 오른쪽 꼬리가 긴 경우가 많음 | 지수/감마분포 또는 로그정규 고려 |
| 점 예측만 보기 | AI 예측값 하나만 보고 SLA 판단 | 예측 분포로 위반 확률 계산 |
| 이상치 기준 임의 설정 | "2배 이상이면 이상"처럼 근거 없는 기준 | 3σ 규칙으로 통계적 기준 설정 |

---

## AI 팁: 예측 불확실성 정량화

```python
from scipy import stats
import numpy as np

# AI 가격 예측 모델 (앙상블로 불확실성 추정)
# 집값 예측: 여러 모델의 예측값으로 분포 추정
predictions = np.array([295000, 310000, 305000, 320000, 298000])  # 5개 모델

mean_pred = predictions.mean()
std_pred = predictions.std()

# 예측 분포
pred_dist = stats.norm(loc=mean_pred, scale=std_pred)

# 90% 예측 구간
lower = pred_dist.ppf(0.05)
upper = pred_dist.ppf(0.95)

print(f"평균 예측: {mean_pred:,.0f}원")
print(f"90% 예측 구간: [{lower:,.0f}, {upper:,.0f}]원")

# 분포별 scipy 사용법
print("\n--- 연속분포 scipy.stats 요약 ---")
norm_rv = stats.norm(loc=0, scale=1)
expon_rv = stats.expon(scale=1)
gamma_rv = stats.gamma(a=2, scale=1)

for name, rv in [("정규", norm_rv), ("지수", expon_rv), ("감마", gamma_rv)]:
    print(f"{name}: mean={rv.mean():.2f}, std={rv.std():.2f}, p95={rv.ppf(0.95):.2f}")
```

---

## 실전 체크리스트

- [ ] PDF 값이 확률이 아닌 밀도임을 이해한다
- [ ] 구간 확률을 CDF의 차이로 계산할 수 있다
- [ ] 68-95-99.7 규칙으로 이상치 탐지 기준을 설정할 수 있다
- [ ] AI 응답시간 데이터에 정규분포 가정이 적합한지 검정할 수 있다
- [ ] 지수분포의 무기억성이 재시도 로직 설계에 주는 함의를 설명할 수 있다
- [ ] 몬테카를로 시뮬레이션으로 SLA 위반 확률을 추정할 수 있다

---

## 처음 질문으로 돌아가기

- **AI 회귀 모델의 출력을 왜 분포로 봐야 할까요?**
  점 예측만으로는 불확실성을 알 수 없습니다. 분포로 보면 SLA 위반 확률, 신뢰구간, 최악 시나리오를 함께 다룰 수 있습니다.

- **PDF 값이 확률이 아닌 이유는 무엇일까요?**
  연속분포에서 임의의 한 점에 대한 확률은 0입니다. f(x)는 면적당 확률 밀도이며, 확률은 항상 구간의 넓이(CDF 차이)로 계산합니다. f(x)는 1을 넘을 수도 있습니다.

- **SLA 분석에서 연속분포를 어떻게 활용할까요?**
  응답시간 분포를 맞춰 `cdf(sla_limit)`로 충족 확률을 계산하고, `ppf(0.99)`로 P99를 구합니다. 몬테카를로로 파이프라인 전체 위반 확률도 시뮬레이션할 수 있습니다.

---

## 정리

연속분포는 AI 회귀 모델 출력의 불확실성을 읽는 언어입니다. PDF와 CDF의 차이를 이해하고, 데이터의 특성(대칭/비대칭, 양수 제약)에 맞는 분포를 고르고, 분포 위에서 SLA와 이상치를 정의할 수 있어야 합니다. 다음 글에서는 표본 크기가 커질수록 평균이 안정되는 이유인 대수의 법칙과 중심극한정리를 다룹니다.

---

## 참고 자료

- [Wikipedia — Normal distribution](https://en.wikipedia.org/wiki/Normal_distribution)
- [Wikipedia — Exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution)
- [scipy.stats — Continuous distributions](https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions)
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
- **바이브코딩을 위한 확률 기초 (8/10): 연속분포 (현재 글)**
- 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 연속분포, 정규분포, AI확률점수
