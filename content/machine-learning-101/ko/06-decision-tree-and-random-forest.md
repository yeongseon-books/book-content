---
series: machine-learning-101
episode: 6
title: "Machine Learning 101 (6/10): Decision Tree와 Random Forest"
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
  - DecisionTree
  - RandomForest
  - Ensemble
  - scikit-learn
seo_description: 결정 트리가 피처 공간을 나누는 방식과 랜덤 포레스트가 분산을 줄이는 원리를 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (6/10): Decision Tree와 Random Forest

거대한 `if-else` 규칙 묶음이 때로는 신경망보다 표 데이터에서 더 잘 동작한다는 사실이 처음에는 이상하게 느껴질 수 있습니다. 하지만 고객 정보, 거래 로그, 클릭 기록처럼 열과 행으로 정리된 데이터에서는 트리 계열이 여전히 매우 강한 베이스라인입니다. 이유는 단순합니다. 비선형 관계를 자연스럽게 잡고, 전처리 요구도 비교적 적기 때문입니다.

이 글은 머신러닝 101 시리즈의 6번째 글입니다. 여기서는 결정 트리의 분할 기준, 단일 트리의 과적합 문제, 그리고 랜덤 포레스트가 여러 트리를 묶어 어떻게 더 안정적인 앙상블이 되는지 정리하겠습니다.

![Machine Learning 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/06/06-01-diagram.ko.png)
*Machine Learning 101 6장 흐름 개요*
> 결정 트리는 피처 공간을 사각형으로 잘라 나가는 모델이고, 랜덤 포레스트는 이런 트리 여러 그루의 다수결로 한 그루의 실수를 가립니다.

## 이 글에서 다룰 문제

- 결정 트리는 피처 공간을 어떤 기준으로 나눌까요?
- Gini와 entropy는 무엇을 측정하고, 언제 결과가 달라질까요?
- 단일 트리는 왜 쉽게 과적합되고, 어디서 멈춰야 할까요?
- 랜덤 포레스트가 단일 트리보다 안정적인 이유는 무엇일까요?
- 트리 깊이와 피처 중요도는 어떻게 해석해야 할까요?
- 트리 모델이 적합하지 않은 데이터 패턴은 어떤 것일까요?

랜덤 포레스트와 그래디언트 부스팅 트리는 지금도 표 데이터에서 강력한 기본 선택지입니다. 딥러닝으로 가기 전에 반드시 비교해야 할 베이스라인입니다.

- **분할(Split)**: 하나의 피처와 임계값으로 데이터를 나눕니다.
- **Gini / entropy**: 불순도를 재는 기준입니다.
- **Pruning**: 깊이나 리프 크기를 제한합니다.
- **Bagging**: 부트스트랩 샘플을 평균내는 방식입니다.
- **Feature importance**: 각 피처가 분할에 기여한 정도입니다.

## 적용 전과 후
**Before**: "트리는 해석 가능하다"에서 설명이 끝납니다. 단일 트리는 분산이 매우 큽니다.

**After**: 포레스트로 분산을 줄이고, 설명은 SHAP 같은 도구까지 포함해 생각합니다.

## 실습: 5단계로 보는 트리와 포레스트

### 단계 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### 단계 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### 단계 3 — 단일 트리

```python
from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier(max_depth=4, random_state=0).fit(Xtr, ytr)
print("tree:", tree.score(Xte, yte))
```

### 단계 4 — Random Forest
```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
print("rf  :", rf.score(Xte, yte))
```

### 단계 5 — 피처 중요도

```python
import numpy as np
order = np.argsort(rf.feature_importances_)[::-1][:5]
print("top:", order)
```

**예상 출력:** 단일 트리와 랜덤 포레스트의 테스트 정확도가 출력되고, 포레스트 쪽이 대체로 더 안정적인 편입니다. 중요도 목록은 어디를 더 볼지 알려 주는 **순위 힌트**이지, 인과관계를 증명하는 표는 아닙니다.

- `max_depth`는 과적합을 막는 가장 중요한 손잡이입니다.
- `n_estimators`가 많을수록 더 안정적이지만, 증가 효과는 점점 줄어듭니다.
- `feature_importances_`는 상관된 피처들 사이에 기여도를 나눠 가집니다.

## 트리 계열 모델 비교

표 데이터에서 자주 쓰는 트리 계열 모델을 한눈에 비교합니다.

| 모델 | 특징 | 과적합 위험 | 속도 | 언제 쓸까 |
|---|---|---|---|---|
| DecisionTree | 한 그루, 해석 쉬움 | 높음 | 빠름 | 규칙 시각화, 탐색 |
| RandomForest | 병렬 배깅 앙상블 | 낮음 | 중간 | 안정적 베이스라인 |
| GradientBoosting | 순차적 앙상블 | 중간 | 느림 | 높은 정확도 목표 |
| ExtraTrees | 극단적 무작위 분할 | 낮음 | 빠름 | 속도 우선, RF 대안 |

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.metrics import f1_score

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

models = {
    "DecisionTree(d=5)": DecisionTreeClassifier(max_depth=5, random_state=42),
    "RandomForest(200)": RandomForestClassifier(n_estimators=200, random_state=42),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "ExtraTrees(200)": ExtraTreesClassifier(n_estimators=200, random_state=42),
}

print(f"{'모델':>22} {'Train Acc':>10} {'Test Acc':>9} {'F1':>7}")
for name, m in models.items():
    m.fit(Xtr, ytr)
    tr = m.score(Xtr, ytr)
    te = m.score(Xte, yte)
    f1 = f1_score(yte, m.predict(Xte))
    print(f"{name:>22} {tr:>10.4f} {te:>9.4f} {f1:>7.4f}")
```

단일 트리는 훈련 정확도가 앙상블보다 높게 나오지만 테스트에서는 역전되는 경우가 많습니다. 이것이 과적합의 신호입니다.

## max_depth와 과적합의 관계

트리 깊이를 바꿔 가며 훈련과 테스트 점수의 간격을 관찰합니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print(f"{'depth':>7} {'train':>8} {'test':>8} {'gap':>7}")
for d in [1, 2, 3, 4, 5, 7, 10, None]:
    m = DecisionTreeClassifier(max_depth=d, random_state=42).fit(Xtr, ytr)
    tr = m.score(Xtr, ytr)
    te = m.score(Xte, yte)
    label = str(d) if d else "None"
    print(f"{label:>7} {tr:>8.4f} {te:>8.4f} {tr-te:>7.4f}")
```

깊이가 깊어질수록 훈련 점수는 올라가지만 테스트 점수는 어느 지점에서 다시 내려오기 시작합니다. 이 지점이 최적 깊이의 힌트입니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 훈련 점수는 완벽한데 테스트 점수가 떨어지면, 더 복잡한 모델보다 먼저 **깊이 제한**을 걸어야 합니다.
- 중요도 결과가 도메인 상식과 어긋나면 상관 피처와 **permutation importance**를 같이 봐야 합니다.
- 포레스트가 겨우 조금만 더 좋다면, 마지막 몇 점보다 **해석 가능성**이 더 중요한지 함께 판단해야 합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 깊이 제한 없는 단일 트리 | 훈련 100%, 테스트 폭락 | max_depth 명시 |
| feature_importance 인과 해석 | 잘못된 의사결정 | permutation importance 병행 |
| 트리에 불필요한 표준화 | 결과 변화 없음 | 트리는 스케일 무관 |
| 훈련 100% 신뢰 | 과적합 판단 못함 | train/test 점수 함께 추적 |
| GBDT와 비교 생략 | 더 좋은 모델 기회 놓침 | GradientBoosting 항상 비교 |

## 실무에서는 이렇게 나타납니다

신용 점수, 클릭 예측, 추천 피처 모델처럼 표 데이터 중심의 ML 시스템은 지금도 트리 앙상블 위에서 돌아갑니다. 여전히 **tabular ML의 주력 모델**입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 랜덤 포레스트는 **베이스라인 + 약간 더**입니다.
- 보통은 그래디언트 부스팅이 더 강합니다.
- permutation importance가 더 믿을 만한 경우가 많습니다.
- 인스턴스 수준 해석이 필요하면 SHAP를 더합니다.
- 범주형 피처 처리는 모델 특성에 맞춰 따로 봅니다.

## 운영 체크리스트

- [ ] `max_depth`를 명시적으로 설정합니다.
- [ ] 포레스트에 충분한 개수의 트리를 사용합니다.
- [ ] feature importance의 한계를 알고 있습니다.
- [ ] GBDT 모델과 비교합니다.

## Permutation Importance로 더 신뢰할 수 있는 피처 중요도 얻기

기본 `feature_importances_`는 상관 피처 사이에서 왜곡될 수 있습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
feature_names = load_breast_cancer().feature_names
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)

# 기본 feature importance (Gini 기반)
gini_imp = rf.feature_importances_
top5_gini = np.argsort(gini_imp)[::-1][:5]
print("기본 importance 상위 5:")
for i in top5_gini:
    print(f"  {feature_names[i]:35s}: {gini_imp[i]:.4f}")

# Permutation importance (테스트 세트 기반)
perm_imp = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=42)
top5_perm = np.argsort(perm_imp.importances_mean)[::-1][:5]
print("\nPermutation importance 상위 5 (테스트 세트):")
for i in top5_perm:
    print(f"  {feature_names[i]:35s}: {perm_imp.importances_mean[i]:.4f} ± {perm_imp.importances_std[i]:.4f}")
```

Permutation importance는 피처를 무작위로 섞었을 때 성능 하락 폭을 측정합니다. 상관 피처가 있어도 더 안정적인 순위를 줍니다.

## n_estimators와 성능-속도 트레이드오프

트리 수가 늘수록 성능이 오르지만 증가 속도는 점점 느려집니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import time

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print(f"{'n_estimators':>14} {'test_acc':>10} {'f1':>8} {'time(s)':>9}")
for n in [10, 25, 50, 100, 200, 500]:
    start = time.time()
    rf = RandomForestClassifier(n_estimators=n, random_state=42, n_jobs=-1).fit(Xtr, ytr)
    elapsed = time.time() - start
    acc = rf.score(Xte, yte)
    f1 = f1_score(yte, rf.predict(Xte))
    print(f"{n:>14} {acc:>10.4f} {f1:>8.4f} {elapsed:>9.3f}")
```

일반적으로 100~200 트리에서 성능이 안정됩니다. 그 이상은 학습 시간만 늘고 성능 향상은 미미합니다.

## 연습 문제

1. `max_depth`를 1부터 20까지 바꿔 가며 테스트 점수를 그려 보세요.
2. 랜덤 포레스트와 그래디언트 부스팅을 비교해 보세요.
3. 기본 importance와 permutation importance를 비교해 보세요.
4. `n_estimators`를 10, 50, 100, 200으로 늘려 가며 성능 변화와 학습 시간을 측정해 보세요.
5. 결정 트리를 시각화해서 어떤 피처와 임계값으로 분류가 이루어지는지 확인해 보세요.

## 정리

결정 트리는 피처 공간을 사각형으로 잘라 나가는 모델이고, 랜덤 포레스트는 이런 트리 여러 그루의 다수결로 한 그루의 실수를 가립니다. 이 글에서는 적용 전과 후부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **결정 트리는 피처 공간을 어떤 기준으로 나눌까요?**
  - 각 분할에서 Gini 불순도 또는 entropy를 가장 많이 줄이는 피처와 임계값을 찾습니다. 분할 후 두 그룹이 최대한 순수해지도록 만드는 것이 목표입니다.
- **Gini와 entropy는 무엇을 측정할까요?**
  - 둘 다 노드의 불순도를 측정합니다. Gini는 계산이 빠르고 entropy는 정보이론 기반입니다. 대부분의 상황에서 결과 차이는 크지 않습니다.
- **단일 트리는 왜 쉽게 과적합될까요?**
  - 깊이 제한 없이 성장하면 훈련 데이터의 노이즈까지 외웁니다. `max_depth`, `min_samples_leaf` 같은 파라미터로 성장을 제한해야 합니다.
