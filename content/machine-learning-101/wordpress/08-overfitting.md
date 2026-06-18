---
title: "바이브코딩을 위한 머신러닝 기초 (8/10): AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기"
series: machine-learning-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- MachineLearning
- AI코딩
- 과적합
- 정규화
seo_description: "바이브코딩 시대, AI 모델이 훈련에서만 잘 되고 테스트에서 망가지는 과적합 진단과 Ridge, Lasso 정규화 해결법을 정리합니다"
---

# 바이브코딩을 위한 머신러닝 기초 (8/10): AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기

이 글은 바이브코딩을 위한 머신러닝 기초 시리즈의 8번째 글입니다.

AI가 만든 모델이 훈련 데이터에서 정확도 99%가 나왔습니다. 기대감이 높아진 채로 테스트 데이터를 돌렸더니 67%였습니다. "AI가 만든 코드가 왜 이렇게 차이가 나지?"라고 당황했습니다. AI에게 물어봤더니 "과적합(Overfitting)이 발생한 것 같습니다. 정규화를 추가해 보세요"라고 했지만, 정규화가 무엇인지, Ridge와 Lasso 중 어떤 걸 써야 하는지 몰랐습니다.

바이브코딩에서 과적합은 매우 자주 발생합니다. AI는 주어진 데이터에 최대한 맞는 코드를 만들어 주는 경향이 있어서, 규제 없이는 모델이 훈련 데이터를 외워 버릴 수 있습니다. 과적합을 진단하는 방법과 정규화를 요청하는 방법을 알면 이 문제를 미리 막을 수 있습니다.

과적합은 모델이 훈련 데이터의 잡음까지 외워서 새 데이터에서 실패하는 현상입니다. 반대로 과소적합은 모델이 너무 단순해서 훈련 데이터조차 제대로 맞추지 못하는 것입니다. 이 두 가지를 구분하면 "모델을 더 복잡하게 해야 하는지, 아니면 더 단순하게 해야 하는지" 방향을 잡을 수 있습니다.

> 훈련 점수가 높고 테스트 점수가 낮으면 과적합, 둘 다 낮으면 과소적합입니다. AI에게 학습 곡선 그려달라고 하면 어느 쪽인지 바로 알 수 있습니다.

---

## 이 글에서 다룰 문제
- 훈련 99% 테스트 67%, 이게 과적합인지 어떻게 확인하나요?
- 과적합과 과소적합을 학습 곡선으로 어떻게 구분하나요?
- Ridge와 Lasso는 어떤 상황에서 각각 더 적합한가요?
- 정규화 강도(alpha)를 어떻게 설정하면 좋은가요?
- AI에게 "과적합 고쳐줘"라고 할 때 더 구체적인 요청 방법은?

## 과적합 진단표

| 상황 | 훈련 점수 | 테스트 점수 | 진단 | 해결 방향 |
|---|---|---|---|---|
| 과적합 | 높음 (95%+) | 낮음 (-20%+) | 모델이 데이터 암기 | 정규화, 데이터 추가 |
| 과소적합 | 낮음 | 낮음 | 모델이 너무 단순 | 피처 추가, 모델 복잡도 증가 |
| 적합 | 높음 | 비슷하게 높음 | 잘 학습됨 | 유지 |
| 의심 상황 | 매우 높음 | 비슷하게 높음 | 누수 가능성 | 데이터 누수 확인 |

## 과적합 진단: 학습 곡선 요청하기

AI에게 이렇게 요청하면 과적합인지 과소적합인지 바로 볼 수 있습니다.

```python
# AI에게 요청: "학습 곡선 그려줘"
from sklearn.model_selection import learning_curve
import numpy as np

train_sizes, train_scores, test_scores = learning_curve(
    model, X, y, cv=5, n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 5)
)

print("Train sizes:", train_sizes)
print("Train mean:", train_scores.mean(axis=1))
print("Test mean :", test_scores.mean(axis=1))
```

**해석 방법:**
- 훈련 점수는 높고 테스트 점수가 크게 낮으면서 데이터 증가에도 좁혀지지 않음 → 과적합
- 훈련과 테스트 점수가 모두 낮음 → 과소적합
- 훈련 점수가 높고 데이터가 늘수록 테스트 점수가 따라 올라옴 → 정상

## Before / After

**Before**: AI가 만든 결정 트리(max_depth 없음), 훈련 100% 테스트 72%. "왜 이런지" 몰라서 다른 모델로 바꿔달라고만 했습니다.

**After**: "학습 곡선 그려줘, 과적합이면 Ridge로 교체하거나 max_depth 제한해줘"라고 요청해서 과적합 원인을 확인하고 해결했습니다. 최종 테스트 정확도 87%로 개선됐습니다.

## Ridge vs Lasso: 어떤 걸 요청해야 하나요?

```python
# Ridge: 모든 계수를 부드럽게 줄임
from sklearn.linear_model import Ridge
ridge = Ridge(alpha=1.0).fit(Xtr, ytr)
print("Ridge R^2:", ridge.score(Xte, yte))

# Lasso: 일부 계수를 0으로 만들어 피처 선택 효과
from sklearn.linear_model import Lasso
lasso = Lasso(alpha=0.01).fit(Xtr, ytr)
nz = (lasso.coef_ != 0).sum()
print(f"Lasso R^2: {lasso.score(Xte, yte):.3f}, 사용 피처: {nz}개")
```

**선택 기준:**
- 모든 피처를 유지하되 과적합만 줄이고 싶다 → Ridge
- 불필요한 피처를 자동으로 제거하고 싶다 → Lasso
- 상관관계 높은 피처가 많다 → ElasticNet(Ridge + Lasso 혼합)

## alpha 값 자동 설정 요청하기

alpha를 직접 정하기 어려울 때 AI에게 이렇게 요청합니다.

```python
# AI에게 요청: "RidgeCV로 최적 alpha 자동 선택해줘"
from sklearn.linear_model import RidgeCV
import numpy as np

alphas = np.logspace(-3, 2, 10)  # 0.001부터 100까지
ridge_cv = RidgeCV(alphas=alphas, cv=5).fit(Xtr, ytr)
print("최적 alpha:", ridge_cv.alpha_)
print("Test R^2:", ridge_cv.score(Xte, yte))
```

`RidgeCV`는 교차검증으로 최적 alpha를 자동 선택해서 감으로 정하는 것보다 훨씬 신뢰할 수 있습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 훈련 점수만 보고 모델 성공 판단 | 과적합을 발견 못 함 | 훈련+테스트 점수 항상 함께 확인 |
| "모델 더 크게 만들어줘"로 과적합 악화 | 더 복잡하면 더 과적합 | 학습 곡선 먼저 확인 후 방향 결정 |
| alpha 한 번만 시도 | 최적값이 아닐 수 있음 | RidgeCV/LassoCV로 자동 선택 |
| 스케일링 없이 Ridge/Lasso 적용 | 피처 단위에 따라 정규화 효과 다름 | 반드시 표준화 후 적용 |

## AI에게 ML 관련 질문하는 팁

**과적합 해결 완전한 요청 패턴:**

"현재 모델이 훈련 99% 테스트 67%입니다. 다음을 해줘:
1. 학습 곡선 그려서 과적합 확인
2. Ridge와 Lasso 각각 시도
3. RidgeCV로 최적 alpha 자동 선택
4. 표준화 포함된 Pipeline으로 구성
5. 최종 훈련/테스트 점수 비교 표 출력"

**과적합 진단 질문:**
- "훈련과 테스트 점수 차이가 이 정도면 과적합인가요?"
- "학습 곡선에서 데이터를 더 추가하면 나아질 것 같나요?"
- "이 모델에서 정규화 말고 다른 과적합 해결 방법은 뭐가 있나요?"

## 운영 체크리스트
- [ ] 훈련 점수와 테스트 점수를 항상 함께 출력합니다
- [ ] 점수 차이가 0.1 이상이면 과적합을 의심합니다
- [ ] 학습 곡선으로 과적합인지 과소적합인지 확인합니다
- [ ] alpha는 RidgeCV/LassoCV로 교차검증하여 정합니다
- [ ] Ridge/Lasso 적용 전에 표준화를 포함했는지 확인합니다

## 처음 질문으로 돌아가기

- **훈련 99% 테스트 67%, 이게 과적합인가요?**
  - 네, 전형적인 과적합입니다. 모델이 훈련 데이터를 외웠지만 새 데이터에 일반화되지 않은 것입니다.
- **학습 곡선으로 과적합을 어떻게 확인하나요?**
  - 훈련 점수는 높고 테스트 점수가 낮으면서 데이터를 추가해도 좁혀지지 않으면 과적합입니다. AI에게 `learning_curve` 코드 요청하면 됩니다.
- **Ridge와 Lasso 중 어떤 걸 써야 하나요?**
  - 피처 선택이 필요 없으면 Ridge, 불필요한 피처를 자동 제거하고 싶으면 Lasso입니다. 모르겠으면 Ridge부터 시도하고 결과가 안 좋으면 ElasticNet을 시도합니다.
- **alpha를 어떻게 정하나요?**
  - 감으로 정하지 말고 `RidgeCV`나 `LassoCV`를 사용해서 교차검증으로 자동 선택하도록 AI에게 요청합니다.
- **"모델 더 복잡하게 만들어줘"가 왜 나쁜 요청인가요?**
  - 이미 과적합인 상태에서 더 복잡한 모델을 쓰면 과적합이 더 심해집니다. 학습 곡선으로 문제 진단 후 방향을 결정해야 합니다.

## 정리

AI 모델이 훈련에서만 잘 되고 테스트에서 망가진다면 과적합입니다. 학습 곡선으로 진단하고, Ridge나 Lasso 정규화로 해결하는 것이 기본 접근법입니다. alpha는 감으로 정하지 말고 RidgeCV로 자동 선택하도록 AI에게 요청합니다. 스케일링 없이 정규화를 적용하면 효과가 줄어드므로 Pipeline으로 묶어서 요청하는 것이 가장 좋습니다.

## 참고 자료
### 공식 문서
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course)
### 관련 시리즈
- [Data Science 101](../../data-science-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 머신러닝 기초 (1/10): ML이 뭔지 알아야 AI에게 제대로 시킬 수 있다](./01-what-is-machine-learning.md)
- [바이브코딩을 위한 머신러닝 기초 (2/10): 지도학습 vs 비지도학습 — AI에게 어떤 유형인지 말해줘야](./02-supervised-unsupervised.md)
- [바이브코딩을 위한 머신러닝 기초 (3/10): AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지](./03-training-test-split.md)
- [바이브코딩을 위한 머신러닝 기초 (4/10): AI가 선형 회귀를 썼는데 맞는 선택인지 판단하려면](./04-linear-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (5/10): AI가 로지스틱 회귀를 쓴 이유를 이해하려면](./05-logistic-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (6/10): AI가 랜덤 포레스트를 추천했다 — 트리 모델 이해하기](./06-tree-models.md)
- [바이브코딩을 위한 머신러닝 기초 (7/10): AI가 KMeans를 썼는데 K를 어떻게 정할지](./07-clustering.md)
- **AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기 (현재 글)**
- [바이브코딩을 위한 머신러닝 기초 (9/10): AI가 "정확도 95%"라고 했는데 진짜 좋은 건지 — 평가 지표](./09-evaluation-metrics.md)
- [바이브코딩을 위한 머신러닝 기초 (10/10): AI와 함께 ML 프로젝트 처음부터 끝까지](./10-ml-project-workflow.md)

<!-- toc:end -->
Tags: 바이브코딩, MachineLearning, AI코딩, 과적합, 정규화
