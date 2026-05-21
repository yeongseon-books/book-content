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

## 먼저 던지는 질문

- 머신러닝에서 확률은 정확히 어디에 숨어 있을까요?
- 교차 엔트로피와 음의 로그가능도는 왜 같은 방향을 가리킬까요?
- 분류 모델이 내놓는 0.8은 무엇을 뜻할까요?

## 큰 그림

![Probability 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/10/10-01-diagram.ko.png)

*Probability 101 10장 흐름 개요*

이 그림은 이 개념의 기본 구조를 보여줍니다.

> 머신러닝에서의 확률은 구체적인 가정과 한계를 함께 봐야 합니다.

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

## 핵심 용어

- 가능도: 파라미터가 주어졌을 때 데이터가 얼마나 그럴듯한지를 보는 함수입니다.
- **MLE**: 가능도를 최대화하는 파라미터를 찾는 방식입니다.
- **MAP**: 사전분포와 가능도를 함께 고려하는 방식입니다.
- **교차 엔트로피**: 예측분포와 실제 레이블 사이의 차이를 재는 손실입니다.
- **확률 보정**: 예측 확률이 실제 빈도와 얼마나 잘 맞는지 보는 성질입니다.

학습, 추론, 평가는 따로 놀지 않습니다. 학습에서 어떤 손실을 택했는지가 출력의 의미를 만들고, 그 출력이 실제 빈도와 얼마나 맞는지가 평가 단계에서 드러납니다.

## 모델 점수는 언제 확률이 될까요?

“모델이 0.8을 냈다”는 문장만으로는 충분하지 않습니다. 그 값이 `p(y=1 | x)=0.8`로 읽히는지, 아니면 단지 순서를 위한 score인지 구분해야 합니다. 확률로 읽고 싶다면 보정 상태도 함께 봐야 합니다. 잘 맞히는 모델이 꼭 정직한 확률을 내놓는 것은 아니기 때문입니다.

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

스팸 분류, 의료 진단, 사기 탐지, 추천 시스템, 이상치 탐지처럼 모델 점수가 직접 행동으로 이어지는 문제에서는 확률 해석이 곧 정책 해석입니다. 점수가 높아도 오탐 비용이 크면 threshold를 올려야 하고, 놓침 비용이 크면 낮춰야 합니다.

또 운영 환경에서는 보정의 드리프트도 봐야 합니다. 학습 당시 0.8이 실제 80%와 비슷했더라도 데이터 분포가 바뀌면 그 대응이 깨질 수 있습니다. 확률을 내놓는 모델은 학습으로 끝나지 않고, 시간이 지나도 그 확률이 여전히 정직한지 계속 점검해야 합니다.

## 체크리스트

- [ ] 교차 엔트로피와 NLL의 관계를 설명할 수 있습니다.
- [ ] `p(y|x)`의 의미를 설명할 수 있습니다.
- [ ] 정확도와 보정이 다른 축이라는 점을 말할 수 있습니다.
- [ ] 브라이어 점수와 로그 손실의 쓰임을 구분할 수 있습니다.

## 정리

머신러닝에서 확률은 주변 개념이 아니라 중심 개념입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 손실함수는 종종 확률 모형의 다른 표현이라는 점, 모델 출력은 보정을 거쳐야 비로소 신뢰할 만한 확률이 된다는 점, 그리고 베이지안 관점은 사전 정보와 데이터 업데이트를 연결하는 실용적인 렌즈라는 점입니다.

이 글로 Probability 101 시리즈를 마칩니다. 확률은 모델의 불확실성을 읽는 언어였습니다. 다음 단계에서는 선형대수와 머신러닝 자체의 모델 구조를 배우며, 그 불확실성을 어떤 표현 위에 올려놓는지 더 넓게 보게 됩니다.

## 처음 질문으로 돌아가기

- **머신러닝에서 확률은 정확히 어디에 숨어 있을까요?**
  - 개념의 정의와 실무에서의 사용법을 분리해서 봅니다.
  - 구체적인 예제와 시뮬레이션으로 개념을 실제로 확인합니다.
- **분류 모델이 내놓는 0.8은 무엇을 뜻할까요?**
  - 이 개념을 실제로 적용할 때 주의할 점을 정리합니다.

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

Tags: Probability, MachineLearning, Likelihood, Inference, Beginner
