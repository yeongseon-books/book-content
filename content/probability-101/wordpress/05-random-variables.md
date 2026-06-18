---
series: probability-101
episode: 5
title: "바이브코딩을 위한 확률 기초 (5/10): 확률변수"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 확률변수
  - PMF
  - AI확률점수
language: ko
---

# 바이브코딩을 위한 확률 기초 (5/10): 확률변수

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 5편입니다. AI 모델이 출력하는 확률 점수를 제대로 읽으려면 그 숫자들이 어떤 구조 위에 서 있는지 알아야 합니다.

---

AI 모델이 이미지를 보고 "고양이 0.72, 개 0.18, 새 0.10"을 출력할 때 이 숫자들은 단순한 점수가 아닙니다. "클래스 레이블"이라는 결과를 숫자로 매핑한 확률변수의 분포입니다. 확률변수를 이해하면 AI 출력을 분포 관점에서 읽을 수 있고, 단순한 최댓값 선택을 넘어 불확실성 자체를 다룰 수 있습니다.

> "확률변수는 AI 출력을 '단일 점수'가 아니라 '분포'로 보게 해주는 렌즈입니다. 하나의 예측값보다 그 예측의 불확실성이 더 중요할 때가 많습니다."

## 이 글에서 다룰 질문들

- 확률변수는 왜 사건보다 한 단계 더 강한 표현일까요?
- 이산형과 연속형은 AI에서 어떻게 다르게 쓰일까요?
- PMF, PDF, CDF는 각각 어떤 질문에 답할까요?
- AI 출력 분포에서 불확실성을 어떻게 읽을까요?
- 분포의 엔트로피가 왜 중요할까요?

---

## 바이브코딩 관점: AI 출력은 확률변수의 실현값

AI 모델의 출력을 "하나의 숫자"로만 보면 많은 정보를 놓칩니다. 확률변수 관점에서 보면 AI 출력은 어떤 분포에서 나온 샘플입니다.

### Before: AI 출력을 단일 숫자로 보기

```python
output = model.predict(image)
# [0.72, 0.18, 0.10]

# 단순히 argmax
predicted_class = output.index(max(output))
print(f"예측: {predicted_class}")  # 고양이
# 끝. 0.72가 0.51이든 0.99든 같은 결론
```

### After: 확률변수(분포)로 보기

```python
import numpy as np

output = np.array([0.72, 0.18, 0.10])
classes = ["고양이", "개", "새"]

# 분포의 형태 확인
print("예측:", classes[np.argmax(output)])
print("확신도:", output.max())

# 엔트로피로 불확실성 측정
entropy = -np.sum(output * np.log(output + 1e-10))
print(f"엔트로피(불확실성): {entropy:.3f}")

# 확신 있는 예측 vs 불확실한 예측
certain = np.array([0.99, 0.005, 0.005])
uncertain = np.array([0.40, 0.35, 0.25])

e_certain = -np.sum(certain * np.log(certain + 1e-10))
e_uncertain = -np.sum(uncertain * np.log(uncertain + 1e-10))

print(f"확신 있는 예측 엔트로피: {e_certain:.3f}")   # 낮음
print(f"불확실한 예측 엔트로피: {e_uncertain:.3f}")   # 높음
```

엔트로피가 낮으면 모델이 확신을 갖고 예측하는 것이고, 높으면 여러 클래스 사이에서 헷갈리고 있다는 신호입니다.

---

## 이산형 vs 연속형: AI에서의 차이

| 구분 | 이산 확률변수 | 연속 확률변수 |
| --- | --- | --- |
| AI 예시 | 분류 레이블, 토큰 ID | 회귀 예측값, 임베딩 좌표 |
| 확률 함수 | PMF: P(X=x) | PDF: f(x) (밀도, 확률 아님) |
| 확률 계산 | 합: Σ p(x) | 적분: ∫f(x)dx |
| 한 점 확률 | P(X=k) ≥ 0 가능 | P(X=x) = 0 항상 |

```python
from scipy import stats
import numpy as np

# 이산형: 분류 모델 출력 (3개 클래스)
# PMF: 각 클래스에 대한 확률
pmf = np.array([0.72, 0.18, 0.10])
print("PMF 합:", pmf.sum())  # 1.0 (반드시 1)
print("P(클래스=0):", pmf[0])  # 직접 확률

# 연속형: 회귀 모델 출력 (가격 예측)
# 모델이 정규분포 N(150000, 20000²)로 가격을 예측
price_dist = stats.norm(loc=150000, scale=20000)

# PDF 값은 확률이 아님!
print("PDF(150000):", price_dist.pdf(150000))  # 0.0000199 — 확률 아님

# 구간 확률로 읽어야 함
print("P(130000 ~ 170000):", price_dist.cdf(170000) - price_dist.cdf(130000))
# 약 0.6827 (±1σ 범위)
```

---

## CDF: AI 임계값 설정의 핵심 도구

누적분포함수(CDF)는 "이 값 이하일 확률"을 알려줍니다. AI 시스템에서 임계값을 설정할 때 필수입니다.

```python
from scipy import stats
import numpy as np

# 예: 회귀 모델의 예측 불확실성 분석
# 서버 응답시간을 예측하는 모델
mu, sigma = 200, 50  # 예측 평균 200ms, 표준편차 50ms
response_dist = stats.norm(loc=mu, scale=sigma)

# 임계값 기반 SLA 분석
sla_limit = 300  # 300ms 이내 응답 목표
p_within_sla = response_dist.cdf(sla_limit)
print(f"SLA 충족 확률: {p_within_sla:.1%}")

# 95%tile: 95% 요청이 이 시간 이내
p95 = response_dist.ppf(0.95)
print(f"95 퍼센타일: {p95:.0f}ms")

# 이산형 분류: 임계값 변경 효과
# 기본 임계값 0.5 vs 도메인별 최적 임계값
thresholds = [0.3, 0.5, 0.7, 0.9]
spam_prob = 0.65  # 모델 출력

for t in thresholds:
    decision = "스팸" if spam_prob >= t else "정상"
    print(f"임계값 {t}: {decision}")
```

---

## AI 불확실성 정량화: 분포 전체를 활용하기

AI 시스템에서 불확실성을 정량화하면 더 나은 의사결정이 가능합니다.

```python
import numpy as np

def analyze_prediction_uncertainty(probs, class_names):
    """
    분류 모델 출력의 불확실성 분석
    """
    probs = np.array(probs)

    # 1. 최대 확률 (확신도)
    max_prob = probs.max()
    predicted = class_names[np.argmax(probs)]

    # 2. 엔트로피 (정보 이론적 불확실성)
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    max_entropy = np.log(len(probs))  # 균등분포일 때 최대

    # 3. 마진 (상위 두 확률 차이)
    sorted_probs = np.sort(probs)[::-1]
    margin = sorted_probs[0] - sorted_probs[1]

    print(f"예측 클래스: {predicted} ({max_prob:.1%})")
    print(f"엔트로피: {entropy:.3f} / {max_entropy:.3f} (정규화: {entropy/max_entropy:.1%})")
    print(f"마진: {margin:.3f}")

    if max_prob > 0.9 and entropy < 0.3:
        print("판정: 높은 확신 - 결과를 신뢰할 수 있음")
    elif max_prob < 0.6 or entropy > 0.8:
        print("판정: 불확실 - 추가 검토 권장")
    else:
        print("판정: 보통 확신 - 맥락 고려 필요")

# 예시
classes = ["고양이", "개", "새"]

print("=== 확신 있는 예측 ===")
analyze_prediction_uncertainty([0.95, 0.03, 0.02], classes)

print("\n=== 불확실한 예측 ===")
analyze_prediction_uncertainty([0.42, 0.38, 0.20], classes)
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| PDF 값을 확률로 읽기 | 연속분포에서 f(x)는 확률이 아닌 밀도 | 항상 구간으로 변환해 확률 계산 |
| argmax만 보기 | 최고 확률 클래스만 보고 불확실성 무시 | 엔트로피나 마진으로 확신도 함께 확인 |
| PMF 합이 1인지 미확인 | AI 출력이 올바른 확률분포인지 확인 안 함 | sum(output) ≈ 1.0 검증 |
| 이산/연속 구분 안 하기 | 분류 모델과 회귀 모델 출력을 같이 처리 | 태스크 타입에 따라 다르게 처리 |

---

## AI 팁: scipy.stats로 모델 출력 분포 분석

```python
from scipy import stats
import numpy as np

# AI 회귀 모델 예측 분포 분석 예시
# 집값 예측 모델이 평균과 분산을 함께 출력한다고 가정
predictions_mean = [300000, 450000, 220000]  # 예측값
predictions_std = [20000, 50000, 15000]       # 불확실성

for mean, std in zip(predictions_mean, predictions_std):
    dist = stats.norm(loc=mean, scale=std)

    # 90% 신뢰구간
    lower = dist.ppf(0.05)
    upper = dist.ppf(0.95)
    print(f"예측: {mean:,} | 90% CI: [{lower:,.0f}, {upper:,.0f}]")
```

---

## 실전 체크리스트

- [ ] AI 분류 출력의 합이 1인지 (PMF), 아닌지 (sigmoid) 구분할 수 있다
- [ ] 엔트로피로 모델 출력의 불확실성을 측정할 수 있다
- [ ] CDF를 이용해 임계값 기반 의사결정을 할 수 있다
- [ ] PDF 값이 확률이 아니라 밀도임을 이해한다
- [ ] 회귀 예측에서 점 추정값과 구간 추정값의 차이를 안다
- [ ] 분포의 퍼센타일(ppf)로 SLA 임계값을 설정할 수 있다

---

## 처음 질문으로 돌아가기

- **확률변수는 왜 사건보다 한 단계 더 강한 표현일까요?**
  사건은 "일어남/안 일어남"만 말하지만, 확률변수는 결과를 숫자로 매핑해 평균, 분산, 분포 등 수치 분석이 가능해집니다. AI 출력도 단순 레이블이 아니라 확률변수로 보면 불확실성까지 다룰 수 있습니다.

- **PMF와 PDF는 어떻게 다를까요?**
  PMF(이산형)의 값은 확률이지만, PDF(연속형)의 값은 밀도입니다. PDF 값이 1보다 클 수도 있고, 확률은 항상 구간의 넓이(적분)로 계산합니다.

- **AI 출력 분포에서 불확실성을 어떻게 읽을까요?**
  엔트로피가 높으면 불확실하고, 낮으면 확신이 있습니다. 상위 두 클래스의 확률 마진이 작으면 경계선 케이스입니다. argmax만 보지 말고 분포 전체를 살펴야 합니다.

---

## 정리

확률변수는 AI 출력을 숫자들의 분포로 읽게 해주는 도구입니다. 단일 예측값보다 그 분포의 모양, 불확실성, 퍼짐을 함께 보는 것이 AI 시스템을 안정적으로 운영하는 핵심입니다. 다음 글에서는 그 분포를 두 숫자로 요약하는 기대값과 분산을 다룹니다.

---

## 참고 자료

- [Khan Academy — Random variables](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Random variable](https://en.wikipedia.org/wiki/Random_variable)
- [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 확률 기초 (1/10): 확률이란 무엇인가?
- 바이브코딩을 위한 확률 기초 (2/10): 사건과 표본공간
- 바이브코딩을 위한 확률 기초 (3/10): 조건부확률
- 바이브코딩을 위한 확률 기초 (4/10): 베이즈 정리
- **바이브코딩을 위한 확률 기초 (5/10): 확률변수 (현재 글)**
- 바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산
- 바이브코딩을 위한 확률 기초 (7/10): 이산분포
- 바이브코딩을 위한 확률 기초 (8/10): 연속분포
- 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 확률변수, PMF, AI확률점수
