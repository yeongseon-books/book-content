---
title: "바이브코딩을 위한 머신러닝 기초 (3/10): AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지"
series: machine-learning-101
episode: 3
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
- TrainTestSplit
- 데이터누수
seo_description: "바이브코딩 시대, AI가 생성한 ML 코드에 train/test split이 빠져 있으면 정확도 숫자를 믿을 수 없습니다"
---

# 바이브코딩을 위한 머신러닝 기초 (3/10): AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지

이 글은 바이브코딩을 위한 머신러닝 기초 시리즈의 3번째 글입니다.

AI가 만들어 준 ML 코드를 실행했더니 정확도 99%가 나왔습니다. 기분이 좋았습니다. 그런데 동료가 "혹시 train/test split 했어요?"라고 물었습니다. 코드를 다시 보니 AI가 `model.fit(X, y)` 다음에 `model.score(X, y)`를 썼습니다. 학습에 쓴 데이터 그대로 점수를 재고 있었습니다.

이건 시험 문제를 미리 다 외운 다음 그 문제로 시험 보는 것과 같습니다. 점수는 당연히 잘 나오지만, 그 점수는 "새로운 시험에서도 잘 할 수 있는가"를 전혀 보여 주지 못합니다.

바이브코딩에서 AI가 만들어 주는 코드에는 train/test split이 빠져 있는 경우가 자주 있습니다. 특히 "빠르게 모델 만들어줘", "일단 돌려봐줘" 같은 요청에 응할 때 그렇습니다. 이 글은 왜 split이 필수인지, 그리고 AI에게 어떻게 요청해야 처음부터 올바른 평가 코드가 나오는지 설명합니다.

> train/test split 없는 ML 코드의 정확도 숫자는 모델의 실력이 아니라 암기 능력을 보여 줍니다.

---

## 이 글에서 다룰 문제
- AI가 만든 코드에 split이 없을 때 어떤 문제가 생기나요?
- `random_state`를 왜 항상 고정해야 한다고 하나요?
- `stratify`는 언제 필요하고 AI에게 어떻게 요청하나요?
- 데이터 누수(Data Leakage)란 무엇이고 어떻게 막나요?
- 교차검증은 왜 단순 split보다 나을 수 있나요?

## 분할 전략 비교

| 전략 | 언제 사용 | AI 요청 시 명시 방법 |
|---|---|---|
| 홀드아웃 | 데이터가 충분히 많을 때 | "test_size=0.2, random_state=42로 분할해줘" |
| Stratified | 클래스 불균형이 있을 때 | "stratify=y 옵션 추가해줘" |
| K-fold | 데이터가 적을 때 | "5-fold 교차검증으로 평가해줘" |
| 시계열 분할 | 시간 순서가 있을 때 | "시계열 데이터라서 무작위 분할 하면 안 됨" |

## 가장 흔한 실수: split 없는 AI 코드

AI가 처음 만들어 주는 코드는 흔히 이렇게 생겼습니다.

```python
# AI가 생성한 코드 (split 없음)
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", model.score(X, y))  # 99%가 나올 수 있음
```

이건 같은 데이터로 학습하고 같은 데이터로 점수를 재는 겁니다. 모델이 문제를 "외웠는지" 확인하는 것이지, "이해했는지" 확인하는 게 아닙니다.

**올바른 코드를 얻으려면 이렇게 요청합니다:**

"train/test split 추가해줘. test_size=0.2, stratify=y, random_state=42 옵션 포함해줘."

```python
# 올바른 코드
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("Train:", model.score(Xtr, ytr))
print("Test :", model.score(Xte, yte))  # 이 숫자가 진짜 성능
```

## Before / After

**Before**: AI 코드를 그대로 실행, 정확도 99%, 성공이라고 생각했습니다. 실제 서비스에 올렸더니 성능이 절반으로 떨어졌습니다.

**After**: train/test split 추가 요청, 테스트 정확도 91% 확인, "훈련 점수와 테스트 점수 차이가 있으니 좀 더 개선이 필요하다"는 판단이 가능해졌습니다.

## 데이터 누수: AI도 놓치는 함정

데이터 누수는 훈련 데이터에 테스트 데이터 정보가 섞여 들어가는 현상입니다. AI가 만든 코드에서도 자주 발생합니다.

**가장 흔한 누수 패턴:**

```python
# 잘못된 코드: split 전에 스케일러 학습
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(X)  # 전체 데이터로 fit!
X_scaled = scaler.transform(X)

Xtr, Xte, ytr, yte = train_test_split(X_scaled, y, test_size=0.2)
```

```python
# 올바른 코드: split 후 훈련 데이터로만 스케일러 학습
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler().fit(Xtr)  # 훈련 데이터로만!
Xtr = scaler.transform(Xtr)
Xte = scaler.transform(Xte)  # 변환만 적용
```

AI에게 전처리 코드를 요청할 때는 이렇게 명시합니다: "스케일러는 훈련 데이터로만 fit하고 테스트 데이터는 transform만 해줘."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| split 없이 모델 점수 확인 | 암기 성능을 일반화 성능으로 착각 | 항상 test_size 지정해서 요청 |
| 분할 전에 스케일러 fit | 테스트 정보가 학습에 새어 들어감 | "split 후 스케일러 학습"을 명시 |
| random_state 없이 실행 | 실행마다 결과가 달라짐 | random_state=42 고정 요청 |
| 불균형 데이터에 stratify 없음 | 분할 후 클래스 비율이 달라질 수 있음 | stratify=y 옵션 추가 요청 |

## AI에게 ML 관련 질문하는 팁

**split을 포함한 완전한 코드 요청 패턴:**

"다음 조건으로 ML 코드 만들어줘:
- train/test split: test_size=0.2, stratify=y, random_state=42
- 전처리는 훈련 데이터로만 fit하고 테스트는 transform만
- 훈련 점수와 테스트 점수 모두 출력"

**AI 코드 검토 질문:**
- "이 코드에서 테스트 데이터가 학습에 영향을 주는 부분이 있나요?"
- "데이터 누수 가능성을 확인해줘"
- "random_state가 고정되어 있나요?"

## 운영 체크리스트
- [ ] AI가 만든 코드에 train/test split이 있는지 확인합니다
- [ ] `random_state=42`가 고정되어 있는지 확인합니다
- [ ] 불균형 데이터에 `stratify=y`가 있는지 확인합니다
- [ ] 스케일러가 훈련 데이터로만 fit되는지 확인합니다
- [ ] 훈련 점수와 테스트 점수 두 가지를 함께 보고합니다
- [ ] 테스트 세트는 최종 평가 전까지 건드리지 않습니다

## 처음 질문으로 돌아가기

- **split 없는 코드의 정확도 99%가 왜 믿을 수 없나요?**
  - 학습 데이터와 평가 데이터가 같으면 모델이 데이터를 "외운" 결과를 측정하는 겁니다. 새 데이터에서의 성능이 아닙니다.
- **`random_state`를 왜 고정해야 하나요?**
  - 고정하지 않으면 실행할 때마다 다른 분할이 일어나서 결과가 재현되지 않습니다. 팀과 결과를 공유하거나 비교할 수 없게 됩니다.
- **`stratify`는 언제 필요한가요?**
  - 클래스 불균형이 있을 때 사용합니다. 예를 들어 이탈 고객이 10%밖에 없다면, 무작위로 나누면 test에 이탈 고객이 거의 없을 수 있습니다.
- **데이터 누수가 뭐고 어떻게 막나요?**
  - 테스트 정보가 학습에 새어 들어가는 현상입니다. 스케일러를 split 전에 fit하거나, 피처에 정답 정보가 포함된 경우에 발생합니다. split을 가장 먼저 하고, 전처리는 훈련 데이터로만 fit하면 예방됩니다.
- **교차검증은 단순 split보다 언제 낫나요?**
  - 데이터가 적을 때 단 한 번의 분할에 의존하면 운에 따라 결과가 달라집니다. 5-fold 교차검증은 5가지 분할로 평균 점수를 내서 더 안정적입니다.

## 정리

바이브코딩에서 AI가 만든 ML 코드를 검토할 때 가장 먼저 확인할 것이 train/test split입니다. split 없이 나온 정확도 숫자는 모델의 암기 능력일 수 있습니다. AI에게 요청할 때 `test_size`, `stratify`, `random_state`를 명시하고, 전처리는 split 후 훈련 데이터로만 fit한다는 조건을 함께 전달하면 처음부터 신뢰할 수 있는 코드를 받을 수 있습니다.

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
- **AI가 전체 데이터로 학습시켰다 — train/test split이 왜 필요한지 (현재 글)**
- [바이브코딩을 위한 머신러닝 기초 (4/10): AI가 선형 회귀를 썼는데 맞는 선택인지 판단하려면](./04-linear-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (5/10): AI가 로지스틱 회귀를 쓴 이유를 이해하려면](./05-logistic-regression.md)
- [바이브코딩을 위한 머신러닝 기초 (6/10): AI가 랜덤 포레스트를 추천했다 — 트리 모델 이해하기](./06-tree-models.md)
- [바이브코딩을 위한 머신러닝 기초 (7/10): AI가 KMeans를 썼는데 K를 어떻게 정할지](./07-clustering.md)
- [바이브코딩을 위한 머신러닝 기초 (8/10): AI 모델이 훈련에서만 잘 된다 — 과적합 이해하기](./08-overfitting.md)
- [바이브코딩을 위한 머신러닝 기초 (9/10): AI가 "정확도 95%"라고 했는데 진짜 좋은 건지 — 평가 지표](./09-evaluation-metrics.md)
- [바이브코딩을 위한 머신러닝 기초 (10/10): AI와 함께 ML 프로젝트 처음부터 끝까지](./10-ml-project-workflow.md)

<!-- toc:end -->
Tags: 바이브코딩, MachineLearning, AI코딩, TrainTestSplit, 데이터누수
