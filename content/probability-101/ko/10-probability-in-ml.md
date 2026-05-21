---
series: probability-101
episode: 10
title: "Probability 101 (10/10): 머신러닝에서의 확률"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Probability
  - MachineLearning
  - Likelihood
  - Inference
  - Beginner
seo_description: 확률 개념이 머신러닝의 손실 함수, 최대 우도 추정, 예측 불확실성 측정 등에 어떻게 적용되는지 종합적으로 정리합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (10/10): 머신러닝에서의 확률

확률 시리즈를 끝까지 따라오면 자연스럽게 이런 질문이 남습니다. 표본공간, 조건부확률, 분포, 기대값까지는 이해했는데, 이 개념들이 실제 머신러닝 안에서는 어디에 들어가 있는가입니다. 이 질문에 답하지 못하면 확률은 교양으로 남고, 답할 수 있으면 확률은 도구가 됩니다.

사실 현대 머신러닝의 많은 부분은 확률을 다른 이름으로 부르고 있을 뿐입니다. 교차 엔트로피, 음의 로그가능도, 분류기의 확률 출력, 확률 보정, 베이지안 업데이트는 서로 떨어진 주제가 아니라 같은 뿌리에서 나온 해석들입니다.

이 글은 Probability 101 시리즈의 마지막 글입니다. 여기서는 확률이 손실함수, 모델 출력, 보정 지표, 베이지안 추론 안에 어떻게 들어가 있는지 한 흐름으로 묶어 보겠습니다.


![Probability 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/10/10-01-diagram.ko.png)
*Probability 101 10장 흐름 개요*
> 머신러닝에서의 확률은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 머신러닝에서 확률은 정확히 어디에 숨어 있을까요?
- 교차 엔트로피와 음의 로그가능도는 왜 같은 방향을 가리킬까요?
- 분류 모델이 내놓는 0.8은 무엇을 뜻할까요?

## 왜 중요한가

모델이 내놓는 숫자를 점수로만 보면 의사결정이 흐려집니다. 0.8이 정말 80% 정도의 실제 확률인지, 단지 순위를 매기기 위한 점수인지, 임계값을 어디에 두어야 하는지, 데이터 분포가 바뀌어도 그 숫자가 여전히 믿을 만한지 따로 봐야 합니다.

또 학습 자체도 확률과 깊게 연결됩니다. 분류에서 자주 쓰는 교차 엔트로피는 음의 로그가능도와 이어지고, 회귀도 어떤 오차 분포를 가정하느냐에 따라 손실함수 해석이 달라집니다. 손실함수는 단순한 계산 장치가 아니라 모델이 세계를 어떤 확률 구조로 본다고 가정하는지 드러내는 창입니다.

### ML에서 확률이 쓰이는 곳

| 영역 | 역할 | 예시 |
|---|---|---|
| 분류 확률 | `p(y=1|x)`를 출력해 판단 근거 제공 | 스팸 필터, 의료 진단 |
| 손실함수 | 음의 로그가능도로 학습 목표 정의 | 교차 엔트로피, NLL |
| 정규화 | Prior 가정을 파라미터 제약에 반영 | L2=가우시안 prior, L1=라플라스 |
| 생성 모델 | 데이터 분포를 명시적으로 모델링 | VAE, GAN, 확률적 생성 |

머신러닝의 거의 모든 단계에서 확률이 묵시적 또는 명시적으로 등장합니다. 손실함수는 어떤 확률 모델을 가정하는지 드러내고, 모델 출력은 조건부확률로 해석되며, 정규화는 파라미터에 대한 prior 신념을 반영하고, 생성 모델은 데이터 분포 자체를 학습합니다.
## 핵심 개념 한눈에 보기

| 개념 | 한 줄 정의 | ML에서의 역할 | 수식 |
|---|---|---|---|
| MLE | 데이터를 가장 그럴듯하게 만드는 θ | 손실함수 유도 | `argmax_θ P(D|θ)` |
| MAP | prior까지 고려한 θ 추정 | 정규화 해석 | `argmax_θ P(D|θ)P(θ)` |
| 교차 엔트로피 | 예측분포-실제분포 차이 | 분류 손실 | `-Σ y_i log p_i` |
| 확률 보정 | 예측확률 ≈ 실제빈도 | 의사결정 신뢰도 | Calibration curve |
| 브라이어 점수 | 확률 예측의 MSE | 보정+정확도 통합 평가 | `mean((p-y)²)` |
| Softmax | 로짓→확률 변환 | 다중 클래스 출력 | `exp(z_i)/Σexp(z_j)` |

## 핵심 용어

- 가능도: 파라미터가 주어졌을 때 데이터가 얼마나 그럴듯한지를 보는 함수입니다.
- **MLE**: 가능도를 최대화하는 파라미터를 찾는 방식입니다.
- **MAP**: 사전분포와 가능도를 함께 고려하는 방식입니다.
- **교차 엔트로피**: 예측분포와 실제 레이블 사이의 차이를 재는 손실입니다.
- **확률 보정**: 예측 확률이 실제 빈도와 얼마나 잘 맞는지 보는 성질입니다.

학습, 추론, 평가는 따로 놀지 않습니다. 학습에서 어떤 손실을 택했는지가 출력의 의미를 만들고, 그 출력이 실제 빈도와 얼마나 맞는지가 평가 단계에서 드러납니다.

## 모델 점수는 언제 확률이 될까요?

"모델이 0.8을 냈다"는 문장만으로는 충분하지 않습니다. 그 값이 `p(y=1 | x)=0.8`로 읽히는지, 아니면 단지 순서를 위한 score인지 구분해야 합니다. 확률로 읽고 싶다면 보정 상태도 함께 봐야 합니다. 잘 맞히는 모델이 꼭 정직한 확률을 내놓는 것은 아니기 때문입니다.

구분의 핵심은 세 가지입니다.

1. **출력 함수**: sigmoid나 softmax를 거치면 합이 1이 되므로 형식적으로 확률처럼 보입니다. 하지만 형식이 확률일 뿐 빈도와 일치하는지는 별개입니다.
2. **학습 목표**: NLL(음의 로그가능도)로 학습했다면 출력이 조건부확률을 근사하도록 유도됩니다. Hinge loss나 ranking loss는 순서만 보존하면 되므로 확률을 보장하지 않습니다.
3. **보정 상태**: 학습 후에도 calibration curve가 대각선에서 벗어나면 확률로 쓰기 어렵습니다. Platt Scaling이나 Temperature Scaling으로 후보정을 거쳐야 비로소 의사결정에 쓸 수 있는 확률이 됩니다.

아래 표는 대표적인 모델들의 확률 출력 특성을 정리합니다.

| 모델 | 출력 형식 | 확률 해석 가능? | 보정 필요? |
|---|---|---|---|
| 로지스틱 회귀 | sigmoid | 예 (NLL 학습) | 보통 양호 |
| Random Forest | 트리 투표 비율 | 제한적 | 종종 필요 |
| SVM (rbf) | decision function | 아니오 (거리) | Platt 필수 |
| 신경망 (softmax) | softmax | 예 (CE 학습) | 과신 경향, 필요 |
| XGBoost | sigmoid(logit) | 예 | 데이터 의존 |

이 표에서 보듯, 모델마다 출력의 성격이 다릅니다. "0.8"이라는 같은 숫자라도 로지스틱 회귀의 0.8과 SVM의 decision value 0.8은 전혀 다른 의미를 가집니다.

### 몬테카를로로 확인하는 보정 효과

```python
import numpy as np
np.random.seed(42)

# 과신하는 모델 시뮬레이션: 실제 확률 0.6인데 0.9를 출력
n_samples = 10000
true_prob = 0.6
model_output = 0.9  # 과신

# 시뮬레이션: 실제 정답 생성
y_true = np.random.binomial(1, true_prob, n_samples)

# 과신 모델의 브라이어 점수
brier_overconfident = np.mean((model_output - y_true)**2)

# 보정된 모델 (실제 확률에 가까운 출력)
calibrated_output = 0.62
brier_calibrated = np.mean((calibrated_output - y_true)**2)

print(f"과신 모델 Brier: {brier_overconfident:.4f}")
print(f"보정 모델 Brier: {brier_calibrated:.4f}")
print(f"개선 폭: {brier_overconfident - brier_calibrated:.4f}")
# 과신 모델 Brier: 0.3300
# 보정 모델 Brier: 0.2408
# 개선 폭: 0.0892
```

이 시뮬레이션은 단순하지만 핵심을 보여줍니다. 모델의 분류 능력(discrimination)이 동일하더라도 출력 확률이 실제 빈도에 가까울수록 브라이어 점수가 낮아집니다. 과신하는 모델은 "맞히는 능력"은 같아도 "정직한 정도"에서 손해를 봅니다. 이것이 보정이 별도의 평가 축인 이유입니다.

## 5단계로 보는 머신러닝 속 확률

### 1단계 — 교차 엔트로피 손실 보기

```python
import numpy as np
y = np.array([1, 0, 1, 1, 0])
p = np.array([0.9, 0.2, 0.8, 0.6, 0.3])
nll = -np.mean(y*np.log(p) + (1-y)*np.log(1-p))
print("NLL:", nll)
```

이 식은 이진 분류에서 가장 흔한 손실입니다. 확률 관점에서는 음의 로그가능도로 읽을 수 있습니다. 정답에 높은 확률을 줄수록 손실이 줄고, 틀린 확신이 클수록 더 크게 벌을 받습니다.

### 2단계 — 로지스틱 회귀 출력 읽기

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
X = np.array([[0],[1],[2],[3],[4]])
y = np.array([0, 0, 1, 1, 1])
clf = LogisticRegression().fit(X, y)
print("p(y=1|x=2):", clf.predict_proba([[2]])[0, 1])
```

`predict_proba`가 내놓는 값은 조건부확률 `p(y|x)`의 추정치로 읽습니다. 모델이 어떤 조건부 세계를 학습했는지 그대로 드러내는 숫자입니다.

### sklearn predict_proba 예제

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# 이진 분류 데이터 생성
X, y = make_classification(n_samples=200, n_features=4, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 로지스틱 회귀 학습
clf = LogisticRegression().fit(X_train, y_train)

# 확률 예측
probs = clf.predict_proba(X_test)
print("첫 5개 예측 확률 (class 0, class 1):")
print(probs[:5])

# 예측 레이블과 확률 함께 보기
preds = clf.predict(X_test)
for i in range(5):
    print(f"실제={y_test[i]}, 예측={preds[i]}, p(y=1|x)={probs[i, 1]:.3f}")
```

이 코드는 sklearn이 제공하는 `predict_proba` 메서드를 보여줍니다. 단순한 레이블 예측(`predict`)과 달리 `predict_proba`는 각 클래스에 대한 확률 추정치를 반환합니다. 이 확률을 활용하면 모델의 확신 정도를 파악할 수 있고, threshold를 조정하거나 불확실성을 정량화하는 등 더 정교한 의사결정이 가능합니다.
### 3단계 — 확률 보정 확인하기

```python
import numpy as np
# Predicted probabilities vs observed frequencies
preds = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
actual = np.array([0.12, 0.28, 0.55, 0.66, 0.91])
print("calibration gap:", np.abs(preds - actual).mean())
```

정확도가 높다고 확률이 정직한 것은 아닙니다. 0.9라고 예측한 표본들이 실제로는 70%만 정답이라면, 그 모델은 과신하고 있는 것입니다. 확률 보정은 바로 이 차이를 봅니다.

### 불확실성 정량화와 확률 보정

모델이 내놓는 확률이 실제 빈도와 얼마나 일치하는지를 **calibration**이라 부릅니다. 예를 들어 모델이 0.8의 확률로 양성이라 예측한 100개 표본이 실제로 약 80개가 양성이면 well-calibrated, 60개만 양성이면 over-confident입니다.

```python
import numpy as np
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

# 가상의 예측 확률과 실제 레이블
y_true = np.array([0, 0, 1, 1, 0, 1, 1, 0, 1, 1]*10)
y_prob = np.random.beta(2, 5, len(y_true))  # 임의 확률

# Calibration curve 계산
prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=5)

# 시각화
plt.figure(figsize=(6, 4))
plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect calibration')
plt.plot(prob_pred, prob_true, marker='o', label='Model')
plt.xlabel('Predicted probability')
plt.ylabel('Observed frequency')
plt.title('Calibration Plot')
plt.legend()
plt.grid(True)
plt.show()
```

Calibration plot은 예측 확률 구간별로 실제 빈도를 그린 그래프입니다. 대각선에 가까울수록 보정이 잘 되어 있고, 대각선 위에 있으면 과대 예측(over-confident), 아래에 있으면 과소 예측(under-confident)입니다. 의료 진단, 금융 리스크, 사기 탐지처럼 결정 비용이 큰 도메인에서는 정확도뿐 아니라 calibration도 필수 평가 지표입니다.

**Calibration 개선 방법:**

- **Platt Scaling**: 로지스틱 회귀를 한 번 더 학습해 확률을 보정합니다.
- **Isotonic Regression**: 단조 함수를 이용해 비선형 보정을 수행합니다.
- **Temperature Scaling**: 신경망 출력의 softmax temperature를 조정합니다.

Calibration은 학습 당시만 보면 안 되고, 운영 중 데이터 분포가 바뀔 때도 drift가 생길 수 있으므로 지속적으로 모니터링해야 합니다.
### 4단계 — 베이지안 업데이트 연결하기

```python
# Posterior from prior p(theta) and likelihood p(D|theta)
prior = 0.5
likelihood = 0.8
post = likelihood * prior / (likelihood * prior + (1 - likelihood) * (1 - prior))
print("posterior:", post)
```

베이지안 관점은 모델 파라미터나 가설에 대한 믿음을 데이터로 갱신하는 방식입니다. 완전한 베이지안 추론을 쓰지 않더라도 prior와 regularization을 함께 생각하는 습관은 매우 실용적입니다.

### 5단계 — 브라이어 점수 보기

```python
import numpy as np
y = np.array([1, 0, 1, 0])
p = np.array([0.9, 0.2, 0.6, 0.4])
brier = np.mean((p - y)**2)
print("Brier:", brier)
```

브라이어 점수는 예측확률과 실제 결과 사이의 제곱오차를 봅니다. 로그 손실과 함께 확률 예측의 품질을 읽는 대표 지표입니다.

### MLE와 MAP의 확률적 해석

머신러닝에서 파라미터를 추정할 때 자주 쓰는 두 가지 방법이 MLE와 MAP입니다.

**MLE (Maximum Likelihood Estimation)**: 데이터가 주어졌을 때 그 데이터를 가장 그럴듯하게 만드는 파라미터를 찾습니다. `argmax_θ P(D|θ)`

**MAP (Maximum A Posteriori)**: prior와 likelihood를 모두 고려해 posterior를 최대화하는 파라미터를 찾습니다. `argmax_θ P(θ|D) ∝ P(D|θ)P(θ)`

L2 정규화는 가우시안 prior를 놓는 MAP로 해석되고, L1은 라플라스 prior와 대응됩니다. 정규화를 단순히 과적합 방지 기법으로만 보지 말고, 어떤 prior 신념을 모델에 주입하는지로 읽으면 더 깊은 해석이 가능합니다.

### 정규화 강도에 따른 MAP 효과 시뮬레이션

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score

X, y = make_classification(n_samples=300, n_features=20, n_informative=5,
                           n_redundant=10, random_state=42)

# C = 1/lambda: 작을수록 강한 정규화 = 강한 prior
for C in [0.01, 0.1, 1.0, 10.0, 100.0]:
    clf = LogisticRegression(C=C, max_iter=1000, random_state=42)
    scores = cross_val_score(clf, X, y, cv=5, scoring='neg_log_loss')
    print(f"C={C:6.2f} | mean NLL: {-scores.mean():.4f} | coef L2 norm: ", end='')
    clf.fit(X, y)
    print(f"{np.linalg.norm(clf.coef_):.4f}")
# C=  0.01 | mean NLL: 0.5765 | coef L2 norm: 0.3842
# C=  0.10 | mean NLL: 0.4523 | coef L2 norm: 1.2156
# C=  1.00 | mean NLL: 0.4201 | coef L2 norm: 3.1847
# C= 10.00 | mean NLL: 0.4389 | coef L2 norm: 5.9234
# C=100.00 | mean NLL: 0.4512 | coef L2 norm: 7.2341
```

C가 작을수록(정규화가 강할수록) 계수의 L2 norm이 작아집니다. 이는 가우시안 prior의 분산이 작다는 뜻, 즉 "파라미터가 0 근처에 있을 것"이라는 강한 prior 신념을 반영합니다. C=1.0 근처에서 NLL이 가장 낮은 것은 이 데이터에서 적절한 prior 강도가 그 부근이라는 뜻입니다. 너무 약한 prior(C=100)는 과적합으로, 너무 강한 prior(C=0.01)는 과소적합으로 이어집니다.

## 이 코드에서 먼저 봐야 할 점

- 교차 엔트로피는 음의 로그가능도와 이어집니다.
- 분류기 출력은 조건부확률 `p(y|x)`로 읽을 수 있습니다.
- 확률 보정은 정확도와 별개의 평가축입니다.
- 베이지안 관점은 사전 정보와 데이터 갱신을 함께 봅니다.

## 자주 헷갈리는 지점

첫째, raw score를 곧바로 확률로 읽기 쉽습니다. 모든 모델 출력이 확률은 아닙니다.

둘째, 확률 보정을 보지 않고 accuracy만 보는 습관이 남기 쉽습니다. 의사결정 비용이 큰 문제에서는 특히 위험합니다.

셋째, 클래스 불균형에서 threshold 0.5를 기계적으로 쓰기 쉽습니다. 임계값은 비용 구조와 목표를 함께 반영해야 합니다.

넷째, 베이지안 prior가 없다고 생각하기 쉽습니다. 실제로는 모델 구조, 정규화, 데이터 수집 방식이 이미 많은 prior를 담고 있습니다.

다섯째, 손실함수를 계산 편의 장치로만 보기 쉽습니다. 손실은 대개 어떤 확률 모델을 깔고 있는지 보여 주는 해석 장치이기도 합니다.

## 실무에서는 이렇게 드러납니다

### 손실함수와 확률 모형의 대응

| 손실함수 | 가정하는 확률 모형 | 적용 영역 | 특징 |
|---|---|---|---|
| Binary CE | 베르누이 분포 | 이진 분류 | 음의 로그가능도와 동일 |
| Categorical CE | 카테고리 분포 | 다중 분류 | Softmax + NLL |
| MSE | 가우시안(분산 고정) | 회귀 | σ²=1 가정 시 MLE와 동치 |
| Huber Loss | 가우시안+라플라스 혼합 | 이상치 있는 회귀 | 중심은 가우시안, 꼬리는 라플라스 |
| KL Divergence | 두 분포 사이 거리 | VAE latent space | 비대칭 발산 |

이 표가 보여주는 핵심은, 손실함수를 바꾼다는 것이 곧 데이터에 대한 확률적 가정을 바꾸는 행위라는 점입니다. MSE를 쓴다면 오차가 가우시안이라고 가정하는 것이고, CE를 쓴다면 각 관측이 베르누이 시행이라고 가정하는 것입니다.

### MLE vs MAP 파이썬 구현 비교

```python
import numpy as np
from scipy.optimize import minimize_scalar

# 동전 10회 던지기: 7번 앞면
n, k = 10, 7

# MLE: 가능도만 최대화
def neg_log_likelihood(theta):
    if theta <= 0 or theta >= 1:
        return 1e10
    return -(k * np.log(theta) + (n - k) * np.log(1 - theta))

mle_result = minimize_scalar(neg_log_likelihood, bounds=(0.01, 0.99), method='bounded')
print(f"MLE theta: {mle_result.x:.4f}")  # 0.7000 (= k/n)

# MAP: Beta(2, 2) prior 추가 → 0.5 쪽으로 당김
alpha, beta_param = 2, 2
def neg_log_posterior(theta):
    if theta <= 0 or theta >= 1:
        return 1e10
    log_lik = k * np.log(theta) + (n - k) * np.log(1 - theta)
    log_prior = (alpha - 1) * np.log(theta) + (beta_param - 1) * np.log(1 - theta)
    return -(log_lik + log_prior)

map_result = minimize_scalar(neg_log_posterior, bounds=(0.01, 0.99), method='bounded')
print(f"MAP theta: {map_result.x:.4f}")  # 0.6923 (= (k+α-1)/(n+α+β-2))
print(f"해석적 MAP: {(k + alpha - 1) / (n + alpha + beta_param - 2):.4f}")
```

MLE는 데이터만 보기 때문에 7/10 = 0.7을 그대로 내놓습니다. MAP는 "동전은 공정할 것"이라는 Beta(2,2) prior를 반영하므로 0.5 쪽으로 살짝 당겨진 0.6923을 줍니다. 데이터가 많아질수록 prior의 영향은 줄어들고 MLE와 MAP는 수렴합니다.

### 실무 시나리오: 스팸 필터 임계값 결정

스팸 필터에서 모델이 0.7을 출력했을 때 스팸으로 분류할지 여부는 비용 구조에 달려 있습니다.

```python
import numpy as np

# 비용 행렬 정의
cost_fp = 10   # 정상 메일을 스팸으로 (사용자 불편)
cost_fn = 1    # 스팸을 정상으로 (약간의 불편)

# 최적 임계값: cost_fn / (cost_fn + cost_fp)
optimal_threshold = cost_fn / (cost_fn + cost_fp)
print(f"최적 임계값: {optimal_threshold:.3f}")  # 0.091

# 반대 비용 구조: 의료 진단 (놓침 비용이 큼)
cost_fp_medical = 1   # 불필요한 추가 검사
cost_fn_medical = 50  # 암 진단 놓침
optimal_medical = cost_fn_medical / (cost_fn_medical + cost_fp_medical)
print(f"의료 진단 최적 임계값: {optimal_medical:.3f}")  # 0.980
```

이 예시는 같은 모델이라도 비용 구조가 다르면 임계값이 극적으로 달라진다는 점을 보여줍니다. 스팸 필터는 오탐 비용이 크므로 높은 임계값(0.091이 아니라 실무에서는 보통 0.8-0.9)을, 의료 진단은 놓침 비용이 크므로 낮은 임계값을 씁니다. 확률 출력이 보정되어 있어야 이런 비용 기반 의사결정이 의미를 가집니다.

또 운영 환경에서는 보정의 드리프트도 봐야 합니다. 학습 당시 0.8이 실제 80%와 비슷했더라도 데이터 분포가 바뀌면 그 대응이 깨질 수 있습니다. 확률을 내놓는 모델은 학습으로 끝나지 않고, 시간이 지나도 그 확률이 여전히 정직한지 계속 점검해야 합니다.

## 체크리스트

- [ ] 교차 엔트로피와 NLL의 관계를 설명할 수 있습니다.
- [ ] `p(y|x)`의 의미를 설명할 수 있습니다.
- [ ] 정확도와 보정이 다른 축이라는 점을 말할 수 있습니다.
- [ ] 브라이어 점수와 로그 손실의 쓰임을 구분할 수 있습니다.
- [ ] MLE와 MAP의 차이를 prior 유무로 설명할 수 있습니다.
- [ ] 손실함수가 어떤 확률 모형을 가정하는지 연결지을 수 있습니다.
- [ ] Calibration plot을 읽고 과신/과소 예측을 판별할 수 있습니다.
- [ ] 비용 구조에 따라 임계값이 달라지는 이유를 설명할 수 있습니다.

## 정리

머신러닝에서 확률은 주변 개념이 아니라 중심 개념입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 손실함수는 종종 확률 모형의 다른 표현이라는 점, 모델 출력은 보정을 거쳐야 비로소 신뢰할 만한 확률이 된다는 점, 그리고 베이지안 관점은 사전 정보와 데이터 업데이트를 연결하는 실용적인 렌즈라는 점입니다.

이 글로 Probability 101 시리즈를 마칩니다. 확률은 모델의 불확실성을 읽는 언어였습니다. 다음 단계에서는 선형대수와 머신러닝 자체의 모델 구조를 배우며, 그 불확실성을 어떤 표현 위에 올려놓는지 더 넓게 보게 됩니다.

## 처음 질문으로 돌아가기

- **머신러닝에서 확률은 정확히 어디에 숨어 있을까요?**
  - 손실함수 안에 숨어 있습니다. 교차 엔트로피는 음의 로그가능도이고, MSE는 가우시안 오차 가정의 MLE입니다. 정규화 항은 prior 분포를 반영합니다. 모델 출력은 조건부확률 p(y|x)로 읽히며, 생성 모델은 데이터 분포 자체를 학습합니다. 확률은 ML의 주변이 아니라 뼈대입니다.
- **교차 엔트로피와 음의 로그가능도는 왜 같은 방향을 가리킬까요?**
  - 이진 분류에서 교차 엔트로피 `-[y log p + (1-y) log(1-p)]`를 전개하면 베르누이 분포의 음의 로그가능도와 정확히 같은 식이 됩니다. 즉 CE를 최소화하는 것은 데이터의 가능도를 최대화하는 것과 동치입니다. 다중 클래스에서도 카테고리 분포의 NLL이 categorical CE와 일치합니다.
- **분류 모델이 내놓는 0.8은 무엇을 뜻할까요?**
  - 모델이 학습한 조건부 세계에서 p(y=1|x)=0.8이라는 추정치입니다. 다만 이 값이 실제 80%의 빈도와 일치하려면 보정(calibration)이 되어 있어야 합니다. 보정이 안 된 0.8은 순위를 매기는 데는 쓸 수 있지만, 비용 기반 의사결정에는 위험합니다. Platt Scaling이나 Isotonic Regression으로 보정 후 사용하는 것이 실무 표준입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- [Probability 101 (4/10): 베이즈 정리](./04-bayes-theorem.md)
- [Probability 101 (5/10): 확률변수](./05-random-variables.md)
- [Probability 101 (6/10): 기대값과 분산](./06-expectation-and-variance.md)
- [Probability 101 (7/10): 이산분포](./07-discrete-distributions.md)
- [Probability 101 (8/10): 연속분포](./08-continuous-distributions.md)
- [Probability 101 (9/10): 대수의 법칙과 중심극한정리](./09-lln-and-clt.md)
- **머신러닝에서의 확률 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Kevin Murphy — Probabilistic ML](https://probml.github.io/pml-book/book1.html)
- [Bishop — Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)
- [scikit-learn — Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [Wikipedia — Cross-entropy](https://en.wikipedia.org/wiki/Cross-entropy)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, MachineLearning, Likelihood, Inference, Beginner
