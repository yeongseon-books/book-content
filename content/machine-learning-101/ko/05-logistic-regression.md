---
series: machine-learning-101
episode: 5
title: "Machine Learning 101 (5/10): Logistic Regression"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - LogisticRegression
  - Classification
  - scikit-learn
  - Beginner
seo_description: 로지스틱 회귀가 선형 점수를 확률로 바꾸는 방식과 임계값, 정밀도, 재현율을 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (5/10): Logistic Regression

0 또는 1을 예측하는데 왜 이름은 회귀인지, 입문 단계에서 가장 많이 받는 질문 중 하나입니다. 이 혼란은 자연스럽습니다. 로지스틱 회귀는 클래스를 곧바로 내놓는 모델처럼 보이지만, 실제로는 먼저 연속적인 확률을 계산한 뒤 임계값을 기준으로 분류를 결정합니다. 그래서 분류 문제를 다루지만 내부 동작은 확률 모델로 이해하는 편이 맞습니다.

이 글은 머신러닝 101 시리즈의 5번째 글입니다. 여기서는 시그모이드 함수, 임계값, 정밀도·재현율·F1의 의미를 함께 보면서 로지스틱 회귀를 분류의 가장 기본적인 기준선으로 정리해 보겠습니다.

![Machine Learning 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/05/05-01-diagram.ko.png)
*Machine Learning 101 5장 흐름 개요*
> 로지스틱 회귀는 선형 점수를 확률로 짜낸 다음, 두 클래스 사이 어디에 경계선을 그을지 결정하는 모델입니다.

## 이 글에서 다룰 문제

- 0 또는 1을 예측하는데 왜 이름은 회귀일까요?
- 시그모이드는 선형 점수를 어떻게 확률로 바꿀까요?
- 왜 0.5 임계값을 항상 정답처럼 쓰면 안 될까요?
- 이 기법의 한계는 어디서 드러나고 어떻게 보완할까요?
- 실무 프로젝트에서 이 개념을 적용할 때 가장 먼저 확인해야 할 점은 무엇일까요?

## 시그모이드 함수의 직관

로지스틱 회귀의 핵심은 **시그모이드 함수**입니다. 시그모이드는 어떤 실수 값이든 0과 1 사이로 보냅니다.

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

### 왜 시그모이드를 쓸까요?

1. 선형 회귀 `y_hat = Xw + b`는 `-∞`부터 `+∞`까지의 값을 낼 수 있습니다.
2. 분류 문제에서는 0와 1 사이의 확률을 내고 싶습니다.
3. 시그모이드는 실수를 `(0, 1)` 구간으로 압축하므로 이 역할을 합니다.

### 시그모이드의 특징

- `z = 0` 일 때 `σ(0) = 0.5`입니다.
- `z`가 클수록 `σ(z) → 1`입니다.
- `z`가 작을수록 `σ(z) → 0`입니다.
- S자 모양의 부드러운 곡선입니다.

로지스틱 회귀는 선형 점수를 먼저 계산한 뒤, 시그모이드로 감싸서 확률로 바꿔 줍니다.

## Python 예제: predict_proba로 확률 확인

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)

# 확률 확인
proba = model.predict_proba(Xte)[:5]
print("Class 0 | Class 1")
for p0, p1 in proba:
    print(f"{p0:.3f}   | {p1:.3f}")

# 예측 레이블
print("Predicted:", model.predict(Xte)[:5])
```

`.predict()`는 확률이 0.5를 넘으면 1, 아니면 0을 반환합니다. `.predict_proba()`를 보면 모델의 확신 정도를 알 수 있습니다.

## 로지스틱 vs 선형 회귀

| 항목 | 로지스틱 회귀 | 선형 회귀 |
|---|---|---|
| 출력 | 0과 1 사이 확률 | 연속값 |
| 손실함수 | Log Loss (Cross-Entropy) | MSE |
| 활용 | 분류 | 회귀 |

이름이 혼란스러운 이유는 로지스틱 회귀가 확률을 출력하기 때문입니다. 최종 분류는 임계값 적용 후에 결정됩니다.
로지스틱 회귀는 분류 문제의 표준 베이스라인입니다. 해석이 가능하고 빠르며, 임계값을 조정하면 불균형 데이터에서도 꽤 경쟁력 있게 동작합니다.

- **시그모이드**: 어떤 실수 값이든 `(0, 1)` 구간으로 매핑합니다.
- 확률: 클래스 1일 것이라는 모델의 믿음입니다.
- 임계값: 확률을 클래스 레이블로 바꾸는 기준선입니다.
- 정밀도: 양성이라고 예측한 것 중 실제 양성의 비율입니다.
- 재현율: 실제 양성 중 모델이 잡아낸 비율입니다.

## 적용 전과 후
**Before**: "정확도 95%"라는 숫자만 보고 만족합니다. 불균형 데이터에서는 거의 의미가 없습니다.

**After**: 정밀도, 재현율, F1, AUC를 함께 보고 임계값까지 조정합니다.

## 실습: 5단계로 보는 분류

### 단계 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### 단계 2 — 분할과 스케일링

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### 단계 3 — 학습

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
from sklearn.metrics import classification_report
print(classification_report(yte, model.predict(Xte)))
```

### 단계 5 — 임계값 조정

```python
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

**예상 출력:** `classification_report`는 클래스별 정밀도와 재현율을 보여 주고, 임계값 루프는 같은 모델이라도 cutoff를 바꾸면 결과가 달라진다는 점을 드러냅니다. 즉, 임계값 선택은 표시 옵션이 아니라 **모델링 결정**입니다.

- `predict_proba`는 레이블이 아니라 확률을 반환합니다.
- 임계값은 정밀도-재현율 절충을 조절하는 손잡이입니다.
- `StandardScaler`는 최적화가 수렴하는 데 도움을 줍니다.

## 분류 모델 비교: 로지스틱 회귀 vs 다른 분류기

같은 데이터에서 로지스틱 회귀와 다른 분류기를 나란히 비교해 봅니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "DecisionTree(d=4)": DecisionTreeClassifier(max_depth=4, random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
}

print(f"{'모델':>22} {'Accuracy':>10} {'F1':>8} {'AUC':>8}")
for name, m in models.items():
    m.fit(Xtr_s, ytr)
    pred = m.predict(Xte_s)
    prob = m.predict_proba(Xte_s)[:, 1]
    acc = m.score(Xte_s, yte)
    f1 = f1_score(yte, pred)
    auc = roc_auc_score(yte, prob)
    print(f"{name:>22} {acc:>10.4f} {f1:>8.4f} {auc:>8.4f}")
```

로지스틱 회귀는 단순하지만 선형 경계를 가진 데이터에서는 복잡한 모델과 거의 동등합니다. 결과가 비슷하다면 해석 가능한 모델이 우선입니다.

## 임계값과 정밀도-재현율 트레이드오프

임계값을 바꾸면 정밀도와 재현율이 반대 방향으로 움직입니다. 이 관계를 이해해야 비즈니스 목적에 맞는 임계값을 정할 수 있습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)
model = LogisticRegression(max_iter=1000).fit(Xtr_s, ytr)
prob = model.predict_proba(Xte_s)[:, 1]

print(f"{'임계값':>8} {'정밀도':>8} {'재현율':>8} {'F1':>8}")
for t in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    pred = (prob >= t).astype(int)
    p = precision_score(yte, pred, zero_division=0)
    r = recall_score(yte, pred, zero_division=0)
    f = f1_score(yte, pred, zero_division=0)
    print(f"{t:>8.1f} {p:>8.4f} {r:>8.4f} {f:>8.4f}")
```

- 임계값을 낮추면 재현율이 올라가고 정밀도가 내려갑니다.
- 암 진단처럼 놓치면 위험한 경우에는 재현율을 높입니다.
- 스팸 필터처럼 오탐이 불편한 경우에는 정밀도를 높입니다.
- F1은 두 지표의 조화평균으로 중간 지점을 찾을 때 기준이 됩니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 정확도는 높은데 중요한 양성을 놓친다면, 모델보다 먼저 **재현율**과 **임계값**을 봐야 합니다.
- 확률이 지나치게 자신 있어 보이면 `predict_proba`를 곧바로 믿기보다 **보정(calibration)** 여부를 확인해야 합니다.
- 계수가 불안정하게 흔들리면 solver보다 먼저 **스케일링**과 **클래스 불균형**을 점검하는 편이 낫습니다.

## 자주 하는 실수

| 실수 | 증상 | 교정 방법 |
|---|---|---|
| 확률이 이미 보정됐다고 가정 | 확률이 실제 비율과 다름 | calibration_curve로 확인 |
| 0.5 임계값 고정 | 비즈니스 비용 무시 | PR 곡선에서 임계값 탐색 |
| 불균형 데이터에서 정확도만 보고 | 소수 클래스 성능 숨겨짐 | F1, AUC, recall 함께 보고 |
| 피처 스케일링 생략 | 수렴 실패 또는 불안정 | StandardScaler 분할 후 적용 |
| 다중 클래스 설정 누락 | 기본값이 예상과 다를 수 있음 | `multi_class` 파라미터 명시 |

## 실무에서는 이렇게 나타납니다

스팸 필터링, 사기 탐지, 이탈 예측처럼 다운스트림 시스템이 **비용을 저울질해야 하는 문제**에서는 확률 출력이 필수입니다. 그래서 로지스틱 회귀는 단순한 분류 모델이 아니라 운영 의사결정의 입력 신호가 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 임계값은 **비즈니스 비용**이 결정합니다.
- 항상 정밀도-재현율 곡선을 그립니다.
- 불균형에는 class weight를 검토합니다.
- 해석 가능성은 중요한 레버리지입니다.
- 확률 보정은 별도로 검증합니다.

## 운영 체크리스트

- [ ] 후속 의사결정에 `predict_proba`를 사용합니다.
- [ ] 정밀도와 재현율을 함께 보고합니다.
- [ ] 비용 기준으로 임계값을 정합니다.
- [ ] 항상 피처를 스케일링합니다.

## ROC 곡선과 PR 곡선으로 모델 성능 요약

임계값에 독립적인 성능 지표가 필요할 때 AUC를 씁니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    roc_curve, precision_recall_curve
)
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)
model = LogisticRegression(max_iter=1000).fit(Xtr_s, ytr)
prob = model.predict_proba(Xte_s)[:, 1]

# AUC 지표
roc_auc = roc_auc_score(yte, prob)
pr_auc = average_precision_score(yte, prob)
print(f"ROC-AUC: {roc_auc:.4f}")
print(f"PR-AUC : {pr_auc:.4f}")

# ROC 곡선 포인트 샘플
fpr, tpr, thresholds = roc_curve(yte, prob)
print(f"\nROC 곡선 주요 포인트 (FPR, TPR, threshold):")
indices = [0, len(fpr)//4, len(fpr)//2, 3*len(fpr)//4, -1]
for i in indices:
    print(f"  FPR={fpr[i]:.3f}, TPR={tpr[i]:.3f}, t={thresholds[min(i, len(thresholds)-1)]:.3f}")
```

ROC-AUC는 임계값 전반에서 모델의 순위 품질을 요약합니다. 불균형이 심하면 PR-AUC가 더 정보량이 많습니다.

## 다중 클래스 로지스틱 회귀

이진 분류에서 다중 분류로 확장하는 방법입니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

X, y = load_iris(return_X_y=True)
feature_names = load_iris().feature_names
target_names = load_iris().target_names

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# multi_class='multinomial'은 소프트맥스를 씁니다
model = LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs")
model.fit(Xtr_s, ytr)

print(classification_report(yte, model.predict(Xte_s), target_names=target_names))

# 각 클래스별 확률 확인
proba = model.predict_proba(Xte_s)[:3]
print("\n첫 3개 샘플의 클래스별 확률:")
for i, row in enumerate(proba):
    probs = {n: f"{p:.3f}" for n, p in zip(target_names, row)}
    print(f"  샘플 {i}: {probs}")
```

다중 클래스에서 `multi_class="multinomial"`은 모든 클래스를 동시에 고려합니다. `"ovr"`(One-vs-Rest)과 비교해서 데이터에 맞는 설정을 찾습니다.

## 클래스 불균형 처리 전략 비교

불균형 데이터에서 로지스틱 회귀의 성능을 개선하는 여러 전략을 비교합니다.

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score, average_precision_score
import numpy as np

# 90:10 불균형 데이터
X, y = make_classification(
    n_samples=2000, n_features=15,
    weights=[0.90, 0.10], random_state=42
)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

strategies = {
    "기본 (C=1.0)": LogisticRegression(C=1.0, max_iter=1000),
    "class_weight=balanced": LogisticRegression(class_weight="balanced", max_iter=1000),
    "C=0.1 (정규화 강화)": LogisticRegression(C=0.1, max_iter=1000),
    "balanced + C=0.1": LogisticRegression(class_weight="balanced", C=0.1, max_iter=1000),
}

print(f"{'전략':>25} {'F1':>8} {'ROC-AUC':>9} {'PR-AUC':>8}")
for name, m in strategies.items():
    m.fit(Xtr_s, ytr)
    pred = m.predict(Xte_s)
    prob = m.predict_proba(Xte_s)[:, 1]
    f1 = f1_score(yte, pred, zero_division=0)
    auc = roc_auc_score(yte, prob)
    pr = average_precision_score(yte, prob)
    print(f"{name:>25} {f1:>8.4f} {auc:>9.4f} {pr:>8.4f}")
```

`class_weight="balanced"`는 소수 클래스에 더 큰 가중치를 줍니다. 불균형이 심할수록 F1과 PR-AUC가 더 의미 있는 지표입니다.

## 연습 문제

1. 임계값을 0.1부터 0.9까지 바꿔 가며 정밀도와 재현율을 그려 보세요.
2. `class_weight="balanced"`를 적용했을 때 결과를 비교해 보세요.
3. 다중 클래스 데이터셋에 `multi_class="multinomial"`을 적용해 보세요.
4. 로지스틱 회귀와 랜덤 포레스트의 AUC를 비교하고 어떤 상황에서 로지스틱 회귀가 더 나은지 분석해 보세요.
5. `C` 파라미터(정규화 강도 역수)를 0.001부터 100까지 바꿔 가며 검증 점수를 관찰해 보세요.

## 정리

로지스틱 회귀는 선형 점수를 확률로 짜낸 다음, 두 클래스 사이 어디에 경계선을 그을지 결정하는 모델입니다. 이 글에서는 시그모이드 함수의 직관부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **0 또는 1을 예측하는데 왜 이름은 회귀일까요?**
  - 내부적으로 선형 점수를 계산하기 때문에 회귀라는 이름이 붙었습니다. 최종 분류 결정은 그 점수를 확률로 변환한 뒤 임계값을 적용해 나옵니다.
- **시그모이드는 선형 점수를 어떻게 확률로 바꿀까요?**
  - 어떤 실수 입력도 (0, 1) 구간으로 압축합니다. 입력이 크면 1에 가까워지고, 작으면 0에 가까워지는 S자 곡선입니다.
- **왜 0.5 임계값을 항상 정답처럼 쓰면 안 될까요?**
  - 비즈니스 비용이 거짓 양성과 거짓 음성 사이에서 비대칭일 때는 임계값을 조정해야 합니다. 암 진단이라면 0.3이, 스팸 필터라면 0.7이 더 적절할 수 있습니다.
