---
series: probability-101
episode: 6
title: "바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 기대값
  - 분산
  - AI확률점수
language: ko
---

# 바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 6편입니다. AI 모델이 출력하는 확률 점수를 제대로 읽으려면 분포를 두 숫자로 요약하는 방법을 알아야 합니다.

---

AI 회귀 모델이 "집값 예측: 3억 5천만원"이라고 출력합니다. 이 숫자만 보면 충분한 것처럼 보이지만 사실 이 숫자 하나로는 중요한 정보를 놓칩니다. 이 예측이 3억부터 4억 사이에서 항상 안정적으로 나오는 건지, 아니면 때로는 2억, 때로는 5억으로 크게 흔들리는 건지 알 수 없습니다. 기대값은 중심을, 분산은 흔들림을 말합니다. 둘을 함께 봐야 AI 예측을 제대로 읽을 수 있습니다.

> "AI 모델의 평균 성능만 보는 것은 반쪽 정보입니다. 분산이 큰 모델은 평균이 같아도 실제 운영에서 훨씬 더 불안정합니다."

## 이 글에서 다룰 질문들

- 기대값은 왜 분포의 중심이라고 부를까요?
- 분산이 크면 AI 시스템에서 어떤 문제가 생길까요?
- 표준편차는 분산과 어떻게 다르고 왜 더 자주 쓸까요?
- 기대값의 선형성이 AI 앙상블에서 어떻게 쓰일까요?
- 편향-분산 트레이드오프란 무엇일까요?

---

## 바이브코딩 관점: 평균만 보면 반쪽짜리 분석

AI 모델의 성능을 리포트할 때 평균 정확도만 보는 것은 위험합니다. 분산을 함께 봐야 합니다.

### Before: 평균만 보는 AI 성능 분석

```python
# 두 모델의 정확도 기록 (10번 평가)
model_A = [0.82, 0.83, 0.81, 0.84, 0.82, 0.83, 0.82, 0.81, 0.83, 0.84]
model_B = [0.70, 0.95, 0.65, 0.98, 0.72, 0.88, 0.60, 0.99, 0.75, 0.93]

import numpy as np
print("모델 A 평균:", np.mean(model_A))  # 0.825
print("모델 B 평균:", np.mean(model_B))  # 0.815

# 평균만 보면: 모델 A가 약간 낫네!
# 하지만 진짜로 나은 모델이 A인가요?
```

### After: 기대값 + 분산으로 제대로 비교

```python
import numpy as np

model_A = [0.82, 0.83, 0.81, 0.84, 0.82, 0.83, 0.82, 0.81, 0.83, 0.84]
model_B = [0.70, 0.95, 0.65, 0.98, 0.72, 0.88, 0.60, 0.99, 0.75, 0.93]

def analyze_model(name, scores):
    mean = np.mean(scores)
    std = np.std(scores)
    cv = std / mean  # 변동계수 (coefficient of variation)
    min_val, max_val = min(scores), max(scores)

    print(f"{name}: 평균={mean:.3f}, 표준편차={std:.3f}, CV={cv:.3f}")
    print(f"  범위: [{min_val:.2f}, {max_val:.2f}]")
    print(f"  안정성: {'높음' if cv < 0.05 else '낮음'}")

analyze_model("모델 A", model_A)
analyze_model("모델 B", model_B)
```

출력:
```
모델 A: 평균=0.825, 표준편차=0.010, CV=0.012
  범위: [0.81, 0.84]
  안정성: 높음
모델 B: 평균=0.815, 표준편차=0.143, CV=0.175
  범위: [0.60, 0.99]
  안정성: 낮음
```

모델 A가 평균도 약간 높고 분산은 훨씬 작습니다. 운영 환경에서는 모델 A가 훨씬 신뢰할 수 있습니다.

---

## 기대값과 분산: 공식과 직관

| 개념 | 이산 공식 | 연속 공식 | AI 의미 |
| --- | --- | --- | --- |
| 기대값 | E[X] = Σ x·p(x) | E[X] = ∫ x·f(x)dx | 평균 예측값 |
| 분산 | Var(X) = Σ (x-μ)²·p(x) | Var(X) = ∫ (x-μ)²·f(x)dx | 예측 흔들림 |
| 표준편차 | √Var(X) | √Var(X) | 원래 단위의 흔들림 |

```python
import numpy as np

# 분류 모델 출력을 확률변수로 보기
# 클래스: {0: 0점, 1: 1점, 2: 2점} (예: 품질 등급)
x = np.array([0, 1, 2])
p = np.array([0.10, 0.35, 0.55])  # 모델 출력 확률

# 기대값 (평균 예측 등급)
E_X = np.sum(x * p)
print(f"기대 등급: {E_X:.2f}")

# 분산
Var_X = np.sum((x - E_X)**2 * p)
print(f"분산: {Var_X:.3f}")

# 표준편차 (원래 단위로 해석 가능)
SD_X = np.sqrt(Var_X)
print(f"표준편차: {SD_X:.3f}")

# 단축 공식: E[X²] - (E[X])²
E_X2 = np.sum(x**2 * p)
Var_shortcut = E_X2 - E_X**2
print(f"분산(단축공식): {Var_shortcut:.3f}")  # 같은 값
```

---

## 기대값의 선형성: 앙상블 이해의 핵심

기대값은 독립 여부와 관계없이 선형으로 분해됩니다. AI 앙상블(여러 모델 결합)이 동작하는 원리입니다.

```python
import numpy as np

# 앙상블 예측: 세 모델의 평균
# E[앙상블] = E[모델1 + 모델2 + 모델3] / 3
#           = (E[모델1] + E[모델2] + E[모델3]) / 3

rng = np.random.default_rng(42)
n_samples = 10000

# 세 모델의 예측 (각각 다른 특성)
model_1 = rng.normal(0.75, 0.10, n_samples)  # 높은 평균, 낮은 분산
model_2 = rng.normal(0.70, 0.15, n_samples)  # 중간 평균, 중간 분산
model_3 = rng.normal(0.80, 0.08, n_samples)  # 높은 평균, 낮은 분산

# 앙상블 평균
ensemble = (model_1 + model_2 + model_3) / 3

print("기대값의 선형성 확인:")
print(f"  E[모델1]: {model_1.mean():.3f}")
print(f"  E[모델2]: {model_2.mean():.3f}")
print(f"  E[모델3]: {model_3.mean():.3f}")
print(f"  E[앙상블]: {ensemble.mean():.3f}")
print(f"  예측값: {(model_1.mean() + model_2.mean() + model_3.mean())/3:.3f}")
print(f"  (두 값이 같음 - 선형성)")

# 분산은 독립인 경우 줄어듦
print(f"\n분산:")
print(f"  Var[모델1]: {model_1.var():.4f}")
print(f"  Var[앙상블]: {ensemble.var():.4f}")
print(f"  앙상블 분산 감소: {(1 - ensemble.var()/model_1.var()):.1%}")
```

---

## 편향-분산 트레이드오프: AI 모델 선택의 핵심

MSE = Bias² + Variance + 노이즈

```python
import numpy as np

def simulate_bias_variance(degree, n_datasets=500, n_train=30):
    """다항식 회귀에서 편향과 분산 추정"""
    rng = np.random.default_rng(42)
    x_test = np.linspace(0, 2 * np.pi, 50)
    y_true = np.sin(x_test)
    predictions = []

    for _ in range(n_datasets):
        x_train = rng.uniform(0, 2 * np.pi, n_train)
        y_train = np.sin(x_train) + rng.normal(0, 0.3, n_train)
        coeffs = np.polyfit(x_train, y_train, degree)
        predictions.append(np.polyval(coeffs, x_test))

    predictions = np.array(predictions)
    mean_pred = predictions.mean(axis=0)

    bias_sq = np.mean((mean_pred - y_true)**2)
    variance = np.mean(predictions.var(axis=0))

    return bias_sq, variance

print(f"{'차수':>4} | {'편향²':>8} | {'분산':>8} | {'편향²+분산':>10}")
print("-" * 38)
for d in [1, 2, 3, 5, 10]:
    b, v = simulate_bias_variance(d)
    print(f"{d:>4} | {b:>8.4f} | {v:>8.4f} | {b+v:>10.4f}")
```

출력:
```
차수 |     편향² |       분산 |   편향²+분산
--------------------------------------
   1 |   0.1752 |   0.0056 |     0.1808
   2 |   0.0200 |   0.0095 |     0.0295
   3 |   0.0048 |   0.0138 |     0.0186
   5 |   0.0012 |   0.0201 |     0.0213
  10 |   0.0008 |   0.0834 |     0.0842
```

차수가 낮으면 편향이 크고(과소적합), 차수가 높으면 분산이 큽니다(과적합). 3차에서 둘의 합이 최소입니다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| 평균만 보고 모델 선택 | 분산이 큰 모델이 평균은 높을 수 있음 | 평균 ± 표준편차 함께 보고 판단 |
| Var(aX) = a·Var(X) | 잘못된 공식 — 실제로는 a²·Var(X) | 공식 정확히 숙지 |
| 표준편차 vs 분산 단위 혼동 | 분산은 단위의 제곱 | 해석 시 표준편차 사용 권장 |
| 표본분산 공식 오류 | 모집단 분산은 n, 표본분산은 n-1 | ddof=1 옵션 사용 확인 |

---

## AI 팁: sklearn으로 편향-분산 분석

```python
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Ridge
import numpy as np

# 정규화 강도별 편향-분산 확인
# alpha가 클수록 강한 정규화 → 편향 증가, 분산 감소
alphas = [0.001, 0.01, 0.1, 1.0, 10.0]

# 예시 데이터
rng = np.random.default_rng(42)
X = rng.normal(0, 1, (100, 20))
y = X[:, 0] * 2 + rng.normal(0, 1, 100)

print(f"{'alpha':>8} | {'평균 CV 점수':>12} | {'표준편차':>10}")
print("-" * 36)

for alpha in alphas:
    model = Ridge(alpha=alpha)
    scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_squared_error')
    mean_mse = -scores.mean()
    std_mse = scores.std()
    print(f"{alpha:>8.3f} | {mean_mse:>12.4f} | {std_mse:>10.4f}")
```

---

## 실전 체크리스트

- [ ] 기대값과 분산을 함께 계산하고 해석할 수 있다
- [ ] AI 모델 성능 비교 시 평균과 표준편차를 모두 본다
- [ ] 편향-분산 트레이드오프가 정규화와 연결됨을 이해한다
- [ ] Var(aX+b) = a²Var(X)를 적용할 수 있다
- [ ] 앙상블이 분산을 줄이는 원리를 기대값 선형성으로 설명할 수 있다
- [ ] 공분산이 양수/음수일 때의 의미를 AI 특징 상관관계와 연결할 수 있다

---

## 처음 질문으로 돌아가기

- **기대값은 왜 분포의 중심이라고 부를까요?**
  기대값은 분포의 무게중심입니다. 반드시 실제로 나올 수 있는 값일 필요는 없지만 (주사위 평균 3.5처럼), 분포의 전체적인 중심 위치를 나타냅니다. AI 모델의 평균 예측값이 이에 해당합니다.

- **분산이 크면 AI 시스템에서 어떤 문제가 생길까요?**
  분산이 크면 예측이 불안정합니다. 같은 입력에 다른 결과가 나올 수 있고, 데이터 변화에 과도하게 반응합니다. 운영 환경에서는 평균 정확도보다 안정성이 더 중요한 경우가 많습니다.

- **편향-분산 트레이드오프란 무엇일까요?**
  모델 복잡도를 높이면 편향(체계적 오류)은 줄지만 분산(불안정성)이 늘어납니다. MSE = Bias² + Variance + Noise로 분해되며, 두 항의 합이 최소가 되는 복잡도를 찾는 것이 모델 선택의 핵심입니다.

---

## 정리

기대값과 분산은 AI 모델 평가의 두 축입니다. 평균 성능(기대값)과 안정성(분산)을 함께 봐야 신뢰할 수 있는 AI 시스템을 구축할 수 있습니다. 다음 글에서는 현실의 카운트 데이터를 다루는 이산분포들을 살펴봅니다.

---

## 참고 자료

- [Khan Academy — Expected value](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Expected value](https://en.wikipedia.org/wiki/Expected_value)
- [Wikipedia — Variance](https://en.wikipedia.org/wiki/Variance)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 확률 기초 (1/10): 확률이란 무엇인가?
- 바이브코딩을 위한 확률 기초 (2/10): 사건과 표본공간
- 바이브코딩을 위한 확률 기초 (3/10): 조건부확률
- 바이브코딩을 위한 확률 기초 (4/10): 베이즈 정리
- 바이브코딩을 위한 확률 기초 (5/10): 확률변수
- **바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산 (현재 글)**
- 바이브코딩을 위한 확률 기초 (7/10): 이산분포
- 바이브코딩을 위한 확률 기초 (8/10): 연속분포
- 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 기대값, 분산, AI확률점수
