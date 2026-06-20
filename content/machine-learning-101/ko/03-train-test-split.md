---
series: machine-learning-101
episode: 3
title: "Machine Learning 101 (3/10): Train/Test Split"
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
  - TrainTestSplit
  - Generalization
  - CrossValidation
  - scikit-learn
seo_description: 일반화를 측정하기 위한 train/test split의 의미와 누수, stratify, random_state, 교차검증까지 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (3/10): Train/Test Split

훈련 정확도가 99%라고 해서 실제 서비스에서도 잘 동작한다는 뜻은 아닙니다. 머신러닝 입문에서 가장 자주 생기는 착각도 바로 여기서 나옵니다. 같은 데이터로 학습하고 같은 데이터로 점수를 재면 숫자는 좋아 보이지만, 그 숫자로는 배포 후 성능을 설명할 수 없습니다.

이 글은 머신러닝 101 시리즈의 3번째 글입니다. 여기서는 train/test split이 왜 일반화 측정의 최소 장치인지, 그리고 `random_state`, `stratify`, K-fold 교차검증이 각각 어떤 역할을 하는지 정리해 보겠습니다.

![Machine Learning 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/03/03-01-diagram.ko.png)
*Machine Learning 101 3장 흐름 개요*
> Train/Test split은 모델이 처음 보는 데이터에서 어떻게 동작할지 가늠하는 유일하게 정직한 방법이고, 여기서 한 번이라도 새면 측정값 전체가 흔들립니다.

## 이 글에서 다룰 문제

- 훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?
- `random_state`를 왜 항상 고정하라고 할까요?
- `stratify`는 클래스 불균형에서 어떤 도움을 줄까요?
- 이 개념을 실무 프로젝트에 적용할 때 가장 먼저 확인할 점은 무엇일까요?
- 이 기법의 한계는 어디서 드러나고 어떻게 보완할까요?

## 분할 전략 비교

| 전략 | 장점 | 단점 | 적합 상황 |
|---|---|---|---|
| 홀드아웃(Hold-out) | 빠름 | 한 번의 분할에 의존 | 데이터가 충분히 많을 때 |
| K-fold | 모든 데이터 활용 | 시간이 더 걸림 | 표본 수가 적을 때 |
| Stratified | 클래스 비율 유지 | 설정이 하나 더 | 불균형 데이터 |
| 시계열 분할 | 누수 방지 | 훈련 데이터 감소 | 시간 순서가 중요한 문제 |

분할 전략의 선택은 데이터의 특성과 문제 유형에 따라 결정됩니다. 무작위 분할이 항상 정답은 아닙니다.

일반화를 측정하지 못하면 모델을 고를 수도, 비교할 수도 없습니다. 훈련 점수는 보기에는 좋지만 그대로 배포할 수 있는 숫자가 아닙니다. 어떤 분할 전략을 썼는지가 결국 모델 선택과 MLOps 게이트의 기준을 결정합니다.

- **Train**: 모델을 학습시키는 데이터입니다.
- **Validation**: 하이퍼파라미터를 조정하는 데 쓰는 데이터입니다.
- **Test**: 마지막에 한 번만 보는 홀드아웃 데이터입니다.
- **Stratify**: 분할 뒤에도 클래스 비율이 유지되도록 맞춥니다.
- **K-fold**: 데이터를 K개로 나누고 테스트 폴드를 돌아가며 바꿔 가는 방식입니다.

## 적용 전과 후
**Before**: 전체 데이터에 학습하고 같은 데이터로 점수를 재서 성능을 과대평가합니다.

**After**: train으로 학습하고 홀드아웃 test로 평가해, 숫자가 현실에 더 가깝도록 만듭니다.

## 실습: 5단계로 분할하고 평가하기

### 단계 1 — 데이터

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### 단계 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### 단계 3 — 모델

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
print("train:", model.score(Xtr, ytr))
print("test :", model.score(Xte, yte))
```

### 단계 5 — 교차검증

```python
from sklearn.model_selection import cross_val_score
print(cross_val_score(model, X, y, cv=5).mean())
```

**예상 출력:** 훈련 점수는 테스트 점수보다 약간 높게 나오고, 교차검증 평균은 그 주변 값에 모이는 편이 자연스럽습니다. 세 숫자가 크게 벌어지면 모델보다 먼저 **분할 전략**을 의심해야 합니다.

## 세 세트의 역할 구분

데이터를 세 부분으로 나눌 때 각각의 역할이 명확해야 평가가 오염되지 않습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)

# 1단계: 테스트 세트를 먼저 분리합니다
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42
)

# 2단계: 나머지에서 검증 세트를 분리합니다
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.18, stratify=y_temp, random_state=42
)

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# 3단계: 전처리는 훈련 데이터만으로 fit
sc = StandardScaler().fit(X_train)
X_train_s = sc.transform(X_train)
X_val_s   = sc.transform(X_val)
X_test_s  = sc.transform(X_test)

# 4단계: 검증 세트로 하이퍼파라미터 탐색
for C in [0.01, 0.1, 1.0, 10.0]:
    m = LogisticRegression(C=C, max_iter=1000).fit(X_train_s, y_train)
    print(f"C={C:.2f}  val: {m.score(X_val_s, y_val):.3f}")

# 5단계: 최종 평가는 테스트 세트 한 번만
best_model = LogisticRegression(C=1.0, max_iter=1000).fit(X_train_s, y_train)
print("최종 테스트 점수:", best_model.score(X_test_s, y_test))
```

검증 세트로 하이퍼파라미터를 정하고, 테스트 세트는 맨 마지막에 딱 한 번만 사용합니다. 테스트 세트를 여러 번 보면 그 자체가 누수입니다.

## 데이터 누수(Data Leakage)

데이터 누수는 훈련 데이터에 테스트 데이터의 정보가 섞여 들어가는 현상으로, 가장 위험한 오류 중 하나입니다.

### 누수가 발생하는 주요 경우

1. **전처리 누수**: 분할 전에 전체 데이터로 스케일러를 학습합니다.
2. **타겟 누수**: 피처 안에 타겟 정보가 직접 들어갑니다.
3. **시간 누수**: 미래 정보를 과거 예측에 사용합니다.
4. **그룹 누수**: 같은 사용자/그룹이 train/test에 나뉘어 들어갑니다.

### 예방 방법

- 분할을 가장 먼저 수행합니다.
- 전처리는 훈련 데이터로만 `.fit()`하고 테스트 데이터는 `.transform()`만 합니다.
- 피처 선택 단계에서 타겟 정보가 섞인 컬럼을 제거합니다.
- 시계열 문제에서는 시간 순서를 엄격히 지킵니다.

## Python 예제: train_test_split + cross_val_score

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# 홀드아웃 분할
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("Train:", model.score(Xtr, ytr))
print("Test:", model.score(Xte, yte))

# 교차검증
scores = cross_val_score(model, X, y, cv=5)
print("CV mean:", scores.mean(), "std:", scores.std())
```

교차검증은 한 번의 분할에서 생길 수 있는 우연을 줄여 줍니다. 표본 수가 적을 때 특히 유용합니다.
- `stratify=y`는 두 분할 모두에서 클래스 비율을 유지합니다.
- 고정된 `random_state`는 결과를 재현 가능하게 만듭니다.
- `cross_val_score`는 훈련과 평가를 K번 반복합니다.

## 분할 크기별 성능 변화 관찰

`test_size` 비율이 성능 추정에 어떤 영향을 주는지 살펴보는 예제입니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

print(f"{'test_size':>10} {'train_score':>12} {'test_score':>11}")
for ts in [0.1, 0.15, 0.2, 0.25, 0.3]:
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=ts, stratify=y, random_state=42
    )
    m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
    print(f"{ts:>10.2f} {m.score(Xtr, ytr):>12.4f} {m.score(Xte, yte):>11.4f}")
```

`test_size`가 너무 작으면 테스트 추정의 분산이 커지고, 너무 크면 훈련 데이터가 부족해집니다. 일반적으로 0.15~0.25 사이를 씁니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 테스트 점수가 실행할 때마다 크게 흔들리면 표본 수가 너무 작거나 시드가 떠 있는지 먼저 봐야 합니다.
- train과 test가 모두 지나치게 좋다면, 성능보다 먼저 **전처리 누수**를 점검해야 합니다.
- 시계열이나 사용자 그룹 데이터인데 무작위 분할을 썼다면, 지표가 아니라 **분할 방식 자체가 버그**일 수 있습니다.

## 자주 하는 실수

| 실수 | 결과 | 올바른 방법 |
|---|---|---|
| 테스트 세트로 튜닝 | 성능 누수, 과적합 | 검증 세트 따로 분리 |
| 분할 전 스케일러 fit | 미래 정보 유입 | 분할 후 훈련 데이터만 fit |
| random_state 미고정 | 재현 불가 | `random_state=42` 등 고정 |
| stratify 생략 | 불균형 분할 | `stratify=y` 적용 |
| 시계열 무작위 분할 | 미래 정보 누수 | `TimeSeriesSplit` 사용 |

## 실무에서는 이렇게 나타납니다

A/B 실험, 모델 비교, MLOps 게이팅 모두 올바른 분할 전략에 기대고 있습니다. 결국 의사결정을 지배하는 것은 지표 이름만이 아니라 **어떻게 나눴는가**입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 테스트 세트는 **정말 한 번만** 봅니다.
- 검증 세트와 테스트 세트는 분리합니다.
- 시계열 데이터는 시간 순서대로 나눕니다.
- 항상 그룹 누수 가능성을 의심합니다.
- 전처리는 분할 이후에 합니다.

## 운영 체크리스트

- [ ] train, valid, test의 역할을 설명할 수 있습니다.
- [ ] `stratify`가 하는 일을 이해했습니다.
- [ ] `random_state`를 항상 고정합니다.
- [ ] `cross_val_score`를 실행할 수 있습니다.

## Pipeline을 활용한 누수 방지 패턴

`make_pipeline`으로 전처리와 모델을 묶으면 교차검증 시 누수가 자동으로 방지됩니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import numpy as np

X, y = load_breast_cancer(return_X_y=True)

# 파이프라인 없이 전처리하면 누수 가능성이 있습니다
sc_bad = StandardScaler().fit(X)  # 전체 데이터로 fit - 누수!
X_bad = sc_bad.transform(X)
scores_bad = cross_val_score(
    LogisticRegression(max_iter=1000), X_bad, y, cv=5
)
print(f"누수 가능 CV: {scores_bad.mean():.4f} ± {scores_bad.std():.4f}")

# 파이프라인을 쓰면 각 fold에서 훈련 데이터만으로 fit합니다
pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000)
)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_safe = cross_val_score(pipe, X, y, cv=cv, scoring="accuracy")
print(f"안전한 CV: {scores_safe.mean():.4f} ± {scores_safe.std():.4f}")
```

파이프라인을 쓰지 않고 전체 데이터에 스케일러를 fit하면, 교차검증의 각 fold에 테스트 데이터의 통계가 스며들어 점수가 낙관적으로 나옵니다.

## 시계열 데이터의 올바른 분할

시간 순서가 있는 데이터는 무작위 분할을 쓰면 미래 데이터가 훈련에 들어갑니다.

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
import numpy as np

# 시계열 형태로 데이터 생성
np.random.seed(42)
n = 200
t = np.arange(n)
X_ts = np.column_stack([t, t**2, np.sin(t * 0.1)])
y_ts = 0.5 * t + 2 * np.sin(t * 0.1) + np.random.randn(n) * 2

# TimeSeriesSplit: 항상 과거 → 미래 방향으로 분할
tscv = TimeSeriesSplit(n_splits=5)
print(f"{'fold':>5} {'train_size':>11} {'test_size':>10} {'R²':>8}")
for fold, (tr_idx, te_idx) in enumerate(tscv.split(X_ts), 1):
    m = Ridge().fit(X_ts[tr_idx], y_ts[tr_idx])
    r2 = r2_score(y_ts[te_idx], m.predict(X_ts[te_idx]))
    print(f"{fold:>5} {len(tr_idx):>11} {len(te_idx):>10} {r2:>8.4f}")
```

`TimeSeriesSplit`은 각 fold에서 훈련 세트가 테스트 세트보다 항상 이전 시점의 데이터만 포함하도록 보장합니다.

## 그룹 누수(Group Leakage) 방지: GroupKFold

같은 사용자나 환자가 훈련/테스트에 동시에 나타나면 성능이 과대평가됩니다.

```python
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

# 10명의 사용자, 각 100회 측정 - 총 1000 샘플
np.random.seed(42)
n_users, n_per_user = 10, 100
X = np.random.randn(n_users * n_per_user, 5)
groups = np.repeat(np.arange(n_users), n_per_user)  # 사용자 ID
y = (groups % 2).astype(int)  # 짝수 사용자=0, 홀수=1

pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

# 일반 KFold: 같은 사용자가 train/test에 섞임
from sklearn.model_selection import KFold
kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores_kf = cross_val_score(pipe, X, y, cv=kf, scoring="accuracy")
print(f"일반 KFold CV: {scores_kf.mean():.4f} ← 낙관적 (그룹 누수)")

# GroupKFold: 사용자 단위로 분할
gkf = GroupKFold(n_splits=5)
scores_gkf = cross_val_score(pipe, X, y, groups=groups, cv=gkf, scoring="accuracy")
print(f"GroupKFold CV: {scores_gkf.mean():.4f} ← 실제 성능에 가까움")
print(f"차이: {scores_kf.mean() - scores_gkf.mean():.4f}")
```

의료 데이터(환자 ID), 추천 시스템(사용자 ID), 음성 인식(화자 ID)처럼 그룹이 있는 데이터는 반드시 `GroupKFold` 또는 `LeaveOneGroupOut`을 씁니다.

## 교차검증 방식 비교: KFold vs StratifiedKFold vs GroupKFold

세 가지 교차검증 방식의 차이를 실제 분할 결과로 비교합니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import (
    KFold, StratifiedKFold, cross_val_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

# 클래스 비율 확인
print(f"전체 클래스 비율: {np.bincount(y) / len(y)}")

cv_methods = {
    "KFold(shuffle=True)": KFold(n_splits=5, shuffle=True, random_state=42),
    "StratifiedKFold": StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
}

print(f"\n{'방식':>22} {'CV Mean':>9} {'CV Std':>8} {'각 fold 점수'}")
for name, cv in cv_methods.items():
    scores = cross_val_score(pipe, X, y, cv=cv, scoring="accuracy")
    fold_str = " ".join(f"{s:.4f}" for s in scores)
    print(f"{name:>22} {scores.mean():>9.4f} {scores.std():>8.4f}  {fold_str}")

# 각 fold의 클래스 비율 확인
print("\nStratifiedKFold에서 각 fold의 클래스 1 비율:")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for fold, (tr_idx, te_idx) in enumerate(skf.split(X, y), 1):
    tr_ratio = y[tr_idx].mean()
    te_ratio = y[te_idx].mean()
    print(f"  fold {fold}: train={tr_ratio:.4f}, test={te_ratio:.4f}")
```

`StratifiedKFold`는 각 fold에서 클래스 비율을 원본과 동일하게 유지합니다. 불균형 데이터에서는 항상 `StratifiedKFold`를 씁니다.

## 연습 문제

1. `test_size`를 0.1부터 0.3까지 바꿔 가며 테스트 점수를 관찰해 보세요.
2. `stratify=None`일 때 train과 test의 클래스 비율을 비교해 보세요.
3. 5-fold와 10-fold 점수의 분산을 비교해 보세요.
4. 분할 전 전체 데이터로 StandardScaler를 fit했을 때와 분할 후 훈련 데이터만으로 fit했을 때 점수 차이를 측정해 보세요.
5. `TimeSeriesSplit`을 사용해서 시계열 데이터에 적합한 교차검증을 구현해 보세요.

## 정리

Train/Test split은 모델이 처음 보는 데이터에서 어떻게 동작할지 가늠하는 유일하게 정직한 방법이고, 여기서 한 번이라도 새면 측정값 전체가 흔들립니다. 이 글에서는 분할 전략 비교부터 시니어 엔지니어는 이렇게 생각합니다까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?**
  - 훈련 세트는 모델 학습, 검증 세트는 하이퍼파라미터 조정, 테스트 세트는 최종 평가에 딱 한 번 사용합니다.
- **`random_state`를 왜 항상 고정하라고 할까요?**
  - 분할 결과가 실행마다 달라지면 성능 비교가 의미 없어집니다. 고정된 시드는 팀 전체가 같은 분할을 보장합니다.
- **`stratify`는 클래스 불균형에서 어떤 도움을 줄까요?**
  - 무작위 분할에서는 소수 클래스가 한쪽에 몰릴 수 있습니다. `stratify=y`는 분할 후에도 클래스 비율을 원본과 동일하게 유지합니다.
  - 데이터 누수는 훈련 과정에서 테스트 시점의 정보가 섞여 들어가는 현상으로, 실전 성능을 과대평가하게 만듭니다.
