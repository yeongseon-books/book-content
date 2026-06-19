---
series: model-evaluation-101
episode: 8
title: "Model Evaluation 101 (8/10): 교차 검증 이해하기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - CrossValidation
  - KFold
  - Stratified
  - scikit-learn
seo_description: 데이터 변동성에 따른 성능 변화를 측정하는 교차 검증 기법을 배우고, K-폴드 분할로 모델의 안정성과 신뢰도를 높입니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (8/10): 교차 검증 이해하기

데이터 과학 팀이 모델 A(F1=0.842)와 모델 B(F1=0.846)를 비교하고 있습니다. 모델 B를 선택하려는데, 한 팀원이 "잠깐, 무작위 시드를 바꾸면 결과가 달라지지 않을까요?"라고 질문했습니다. 시드를 5번 바꿔 보니 F1이 0.82~0.87 사이에서 흔들렸습니다. 이 두 모델의 0.004 차이는 아무 의미가 없었습니다.

이 글은 Model Evaluation 101 시리즈의 8번째 글입니다.

단 한 번의 train/test 분할에서 나온 점수는 생각보다 불안정합니다. 데이터가 조금만 달리 나뉘어도 순위가 뒤집힐 수 있기 때문입니다. 교차 검증은 이 문제를 해결합니다. 점수를 더 많이 만드는 기술이 아니라, 그 점수를 얼마나 믿어도 되는지 추정하는 기술입니다.

![Model Evaluation 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/08/08-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 8장 흐름 개요*

> 교차 검증은 점수 공장이 아니라 불확실성을 보는 도구입니다 — 폴드 간 평균뿐 아니라 분산을 함께 봐야 두 모델의 작은 격차가 실제 신호인지 단순한 분할 잡음인지 구분할 수 있습니다.

## 이 글에서 다룰 문제

- 단일 train/test 분할이 왜 불안정한 추정치를 줄까요?
- K-Fold 교차 검증은 어떻게 이 문제를 해결하나요?
- Stratified, Group, TimeSeries 교차 검증은 각각 언제 써야 하나요?
- 교차 검증 점수의 평균과 표준편차를 어떻게 해석할까요?
- 교차 검증이 있으면 테스트 세트가 필요 없을까요?

## K-Fold 교차 검증의 원리

### 기본 개념

K-Fold는 데이터를 K개의 폴드로 나누고 K번 반복합니다. 매번 K-1개 폴드로 학습하고, 남은 1개 폴드로 검증합니다.

```
데이터 전체
 ┌──────┬──────┬──────┬──────┬──────┐
 │ F1   │ F2   │ F3   │ F4   │ F5   │
 └──────┴──────┴──────┴──────┴──────┘

Fold 1: [테스트] [학습] [학습] [학습] [학습]
Fold 2: [학습] [테스트] [학습] [학습] [학습]
Fold 3: [학습] [학습] [테스트] [학습] [학습]
Fold 4: [학습] [학습] [학습] [테스트] [학습]
Fold 5: [학습] [학습] [학습] [학습] [테스트]
```

K=5이면 5개의 점수가 나옵니다. 평균은 전체적인 성능 추정치고, 표준편차는 불확실성을 나타냅니다.

### 단일 분할 vs. K-Fold 비교

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
    GroupKFold,
    TimeSeriesSplit,
    cross_validate,
)
from sklearn.metrics import f1_score

# 데이터 생성
X, y = make_classification(
    n_samples=2000,
    n_features=20,
    n_informative=8,
    weights=[0.7, 0.3],
    random_state=42,
)
model = LogisticRegression(max_iter=1000, random_state=42)

# 단일 분할: 시드에 따른 불안정성 시연
print("=== 단일 분할의 불안정성 ===")
print("동일한 데이터, 다른 무작위 분할:")
single_scores = []
for seed in range(10):
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=seed
    )
    m = LogisticRegression(max_iter=1000, random_state=42).fit(X_tr, y_tr)
    score = f1_score(y_te, m.predict(X_te), average="macro")
    single_scores.append(score)
    print(f"  시드 {seed:2d}: F1 = {score:.4f}")

print(f"  평균: {np.mean(single_scores):.4f}, 표준편차: {np.std(single_scores):.4f}")
print(f"  범위: {min(single_scores):.4f} ~ {max(single_scores):.4f}")
print()

# K-Fold 교차 검증
print("=== 5-Fold 교차 검증 ===")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro")
print(f"폴드별 점수: {[round(s, 4) for s in cv_scores]}")
print(f"평균: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"95% 신뢰구간: [{cv_scores.mean() - 2*cv_scores.std():.4f}, "
      f"{cv_scores.mean() + 2*cv_scores.std():.4f}]")
```

## 교차 검증 방식 선택 가이드

### 1. Stratified K-Fold — 분류 문제의 기본

```python
# Stratified K-Fold: 각 폴드의 클래스 비율을 유지
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_skf = cross_val_score(model, X, y, cv=skf, scoring="f1_macro")

print("=== Stratified K-Fold (분류 문제 기본) ===")
print(f"각 폴드 점수: {[round(s, 4) for s in scores_skf]}")
print(f"평균 ± 표준편차: {scores_skf.mean():.4f} ± {scores_skf.std():.4f}")
print()
print("언제 사용:")
print("  - 이진/다중 분류 문제")
print("  - 클래스 불균형이 있을 때 (각 폴드 비율 유지)")
print("  - 일반적인 분류 모델 비교")
```

### 2. Group K-Fold — 그룹 누수 방지

```python
# Group K-Fold: 같은 그룹이 여러 폴드에 나뉘지 않도록
groups = np.repeat(np.arange(200), 10)  # 200명 사용자, 각 10개 샘플
gkf = GroupKFold(n_splits=5)
scores_gkf = cross_val_score(model, X, y, cv=gkf, groups=groups, scoring="f1_macro")

print("=== Group K-Fold (그룹 누수 방지) ===")
print(f"각 폴드 점수: {[round(s, 4) for s in scores_gkf]}")
print(f"평균 ± 표준편차: {scores_gkf.mean():.4f} ± {scores_gkf.std():.4f}")
print()
print("언제 사용:")
print("  - 사용자별, 환자별, 문서별 데이터")
print("  - 같은 개체가 학습과 테스트 양쪽에 나타나면 안 될 때")
print("  - 추천 시스템, 의료 데이터, NLP (같은 문서의 문장들)")
print()

# 그룹 분리 검증
print("그룹 분리 검증:")
for fold, (tr_idx, te_idx) in enumerate(gkf.split(X, y, groups)):
    train_groups = set(groups[tr_idx])
    test_groups = set(groups[te_idx])
    overlap = train_groups & test_groups
    print(f"  Fold {fold+1}: 학습 그룹 {len(train_groups)}개, "
          f"테스트 그룹 {len(test_groups)}개, "
          f"겹침 {len(overlap)}개 (항상 0이어야 함)")
```

### 3. TimeSeriesSplit — 시계열 데이터

```python
# TimeSeriesSplit: 항상 과거에서 미래로
tscv = TimeSeriesSplit(n_splits=5)
scores_ts = cross_val_score(model, X, y, cv=tscv, scoring="f1_macro")

print("=== TimeSeriesSplit (시계열 데이터) ===")
print(f"각 폴드 점수: {[round(s, 4) for s in scores_ts]}")
print(f"평균 ± 표준편차: {scores_ts.mean():.4f} ± {scores_ts.std():.4f}")
print()
print("언제 사용:")
print("  - 시간 순서가 있는 데이터 (주가, 센서, 클릭 로그)")
print("  - 미래를 예측하는 모델")
print("  - 무작위 분할이 시간 순서를 깨뜨릴 때")

print()
print("각 폴드의 시간 범위:")
for fold, (tr_idx, te_idx) in enumerate(tscv.split(X)):
    print(f"  Fold {fold+1}: 학습 {tr_idx[0]}~{tr_idx[-1]}, "
          f"테스트 {te_idx[0]}~{te_idx[-1]}")
```

### 4. 교차 검증 방식 비교표

| 방식 | 언제 사용 | 주의사항 |
| --- | --- | --- |
| KFold | 회귀, 충분한 데이터 | 분류에서 클래스 비율 보장 안 됨 |
| StratifiedKFold | 분류 (기본값) | 그룹/시계열 데이터에 부적합 |
| GroupKFold | 개체 중복 방지 필요 | 그룹 수가 K보다 많아야 함 |
| TimeSeriesSplit | 시계열 데이터 | 학습 데이터가 폴드마다 커짐 |
| RepeatedStratifiedKFold | 작은 데이터 | 계산 비용 큼 |

## 여러 지표 동시 수집

```python
# cross_validate: 여러 지표를 한 번에 수집
cv_results = cross_validate(
    model, X, y,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring=["f1_macro", "roc_auc", "balanced_accuracy"],
    return_train_score=True,
)

print("=== 다중 지표 교차 검증 결과 ===")
for key, values in cv_results.items():
    if key.startswith("test_") or key.startswith("train_"):
        metric = key.replace("test_", "").replace("train_", "")
        prefix = "테스트" if key.startswith("test_") else "훈련 "
        print(f"{prefix} {metric:>20}: {values.mean():.4f} ± {values.std():.4f}")
print()

# 과적합 진단
print("=== 과적합 진단 ===")
for metric in ["f1_macro", "roc_auc"]:
    train_mean = cv_results[f"train_{metric}"].mean()
    test_mean = cv_results[f"test_{metric}"].mean()
    gap = train_mean - test_mean
    if gap > 0.05:
        print(f"{metric}: 과적합 의심 (훈련-테스트 차이 {gap:.4f})")
    else:
        print(f"{metric}: 정상 (훈련-테스트 차이 {gap:.4f})")
```

## 모델 비교: 평균과 분산으로 판단

```python
from sklearn.ensemble import RandomForestClassifier
from scipy import stats

# 두 모델 교차 검증 비교
model_a = LogisticRegression(max_iter=1000, random_state=42)
model_b = RandomForestClassifier(n_estimators=100, random_state=42)

cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scores_a = cross_val_score(model_a, X, y, cv=cv, scoring="f1_macro")
scores_b = cross_val_score(model_b, X, y, cv=cv, scoring="f1_macro")

print("=== 두 모델 비교 (10-Fold) ===")
print(f"모델 A (로지스틱): {scores_a.mean():.4f} ± {scores_a.std():.4f}")
print(f"  폴드별: {[round(s, 3) for s in scores_a]}")
print()
print(f"모델 B (랜덤 포레스트): {scores_b.mean():.4f} ± {scores_b.std():.4f}")
print(f"  폴드별: {[round(s, 3) for s in scores_b]}")
print()

# 통계적 유의성 검정
t_stat, p_value = stats.ttest_rel(scores_a, scores_b)
print(f"대응 t-검정: t={t_stat:.3f}, p={p_value:.4f}")
if p_value < 0.05:
    better = "A" if scores_a.mean() > scores_b.mean() else "B"
    print(f"통계적으로 유의미한 차이 있음 (모델 {better}가 유의미하게 더 좋음)")
else:
    print("통계적으로 유의미한 차이 없음 (분할 잡음 범위 내)")
    print("→ 두 모델 중 더 단순한 모델을 선택하는 것이 합리적")
```

## 교차 검증 결과 올바르게 읽기

```python
# 교차 검증 표준편차 해석
print("=== 표준편차 해석 가이드 ===")
print()
cv_a = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_10fold = cross_val_score(model_a, X, y, cv=cv_a, scoring="f1_macro")

std = scores_10fold.std()
mean = scores_10fold.mean()

print(f"평균: {mean:.4f}, 표준편차: {std:.4f}")
print()
if std < 0.02:
    print("표준편차 < 0.02: 매우 안정적인 평가")
    print("→ 다른 모델과의 0.01 차이도 신호로 볼 수 있음")
elif std < 0.05:
    print("표준편차 0.02~0.05: 적당히 안정적")
    print("→ 모델 비교 시 0.02 이상 차이를 의미 있다고 볼 수 있음")
else:
    print("표준편차 > 0.05: 불안정한 평가")
    print("→ 모델 비교보다 데이터/분할 전략 재검토 필요")
    print("→ K를 늘리거나 Repeated K-Fold 고려")
```

## Before vs. After: 교차 검증 사용 비교

| 항목 | 단일 분할 | 교차 검증 |
| --- | --- | --- |
| 점수 안정성 | 무작위 분할에 크게 의존 | 여러 분할의 평균 → 안정적 |
| 모델 비교 | 작은 차이도 선택 근거로 | 통계적 유의성 검정 가능 |
| 보고 형식 | "F1=0.84" | "F1=0.842 ± 0.018" |
| 누수 탐지 | 어려움 | 점수가 비정상적으로 높으면 의심 |
| 계산 비용 | 낮음 | K배 높음 (단, 가치 있음) |

## 자주 하는 실수

**실수 1 — 교차 검증 평균만 보고 표준편차 무시**

교차 검증의 핵심은 평균이 아닌 불확실성(표준편차)입니다. 평균이 좋아도 표준편차가 크면 이 모델은 신뢰할 수 없습니다. 항상 평균 ± 표준편차 형식으로 보고해야 합니다.

**실수 2 — 일반 KFold를 불균형 분류에 사용**

일반 KFold는 각 폴드에서 클래스 비율을 보장하지 않습니다. 불균형 데이터에서는 어떤 폴드는 양성이 너무 적거나 없을 수 있습니다. 분류 문제에서는 항상 StratifiedKFold를 기본값으로 써야 합니다.

**실수 3 — 교차 검증이 있으면 테스트 세트 불필요라고 착각**

교차 검증은 모델 선택과 하이퍼파라미터 조정을 위한 도구입니다. 최종 보고를 위한 독립적인 홀드아웃 테스트 세트는 여전히 필요합니다. 교차 검증으로 모델을 선택하고, 그 모델을 전체 학습 데이터로 재학습한 뒤, 마지막에 테스트 세트로 최종 평가합니다.

**실수 4 — 시계열 데이터에 StratifiedKFold 사용**

시계열에서 무작위 폴드 분할은 미래 정보 누수를 발생시킵니다. 시계열 데이터에서는 반드시 TimeSeriesSplit을 사용해야 합니다.

**실수 5 — 그룹 데이터에서 그룹 누수 무시**

추천 시스템, 의료 데이터, NLP 등에서 같은 사용자/환자/문서의 데이터가 학습과 테스트 양쪽에 나타나면 성능이 부풀려집니다. 이런 데이터에서는 GroupKFold 또는 GroupShuffleSplit을 사용해야 합니다.

## Nested Cross-Validation: 하이퍼파라미터 탐색과 평가 분리

하이퍼파라미터를 교차 검증으로 선택하면서 동시에 그 교차 검증으로 성능을 평가하면 낙관적 결과가 나옵니다. 이를 막는 것이 Nested Cross-Validation입니다.

```python
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression

# Nested CV: 외부 루프 평가, 내부 루프 하이퍼파라미터 선택
param_grid = {"C": [0.01, 0.1, 1.0, 10.0]}

outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=0)

# 내부 CV로 최적 파라미터를 찾고, 외부 CV로 실제 성능 추정
gs = GridSearchCV(
    LogisticRegression(max_iter=2000),
    param_grid=param_grid,
    cv=inner_cv,
    scoring="f1_macro",
)

# 외부 CV 점수 = 편향되지 않은 성능 추정치
nested_scores = cross_val_score(gs, X, y, cv=outer_cv, scoring="f1_macro")

print("=== Nested Cross-Validation ===")
print(f"외부 CV 점수: {[round(s, 4) for s in nested_scores]}")
print(f"평균 ± 표준편차: {nested_scores.mean():.4f} ± {nested_scores.std():.4f}")
print()

# 일반 CV (낙관적 편향 있음)
simple_scores = cross_val_score(
    LogisticRegression(C=1.0, max_iter=2000),
    X, y, cv=outer_cv, scoring="f1_macro"
)
print(f"단순 CV (C=1.0 고정): {simple_scores.mean():.4f} ± {simple_scores.std():.4f}")
print()
print("결론:")
print("  하이퍼파라미터 탐색을 포함한 실제 파이프라인은")
print("  Nested CV로 평가해야 편향 없는 성능 추정치를 얻습니다.")
```

## 운영 체크리스트

- [ ] 단일 분할 대신 5-fold 이상의 교차 검증을 사용했습니다.
- [ ] 데이터 성격에 맞는 교차 검증 방식을 선택했습니다.
- [ ] 평균과 표준편차를 함께 보고했습니다.
- [ ] 두 모델을 비교할 때 통계적 유의성 검정(t-검정)을 했습니다.
- [ ] 최종 평가를 위한 별도 홀드아웃 테스트 세트를 유지했습니다.
- [ ] 교차 검증 점수가 비정상적으로 높으면 누수를 확인했습니다.

## 처음 질문으로 돌아가기

- **단일 train/test 분할이 왜 불안정한 추정치를 줄까요?**
  - 단일 분할에서의 점수는 그 특정 분할 방식에 의존합니다. 무작위 시드를 바꾸면 동일한 데이터에서 F1이 0.82~0.87 사이로 흔들릴 수 있습니다. 교차 검증은 여러 분할에서의 평균을 사용해 이 불안정성을 줄입니다.

- **Stratified, Group, TimeSeries 교차 검증은 각각 언제 써야 하나요?**
  - StratifiedKFold: 분류 문제 (클래스 비율 유지). GroupKFold: 같은 사용자/환자/문서의 데이터가 있을 때 (그룹 누수 방지). TimeSeriesSplit: 시계열 데이터 (과거→미래 순서 유지). 데이터 특성을 무시하고 일반 KFold만 쓰면 누수가 발생합니다.

- **교차 검증이 있으면 테스트 세트가 필요 없을까요?**
  - 아닙니다. 교차 검증은 모델 선택(하이퍼파라미터 조정, 알고리즘 비교)에 사용합니다. 최종 배포 결정을 위한 독립적인 평가는 별도 홀드아웃 테스트 세트에서 해야 합니다. 교차 검증을 너무 많이 보면 결국 그 데이터에 과적합될 수 있습니다.

---

## 정리

교차 검증은 모델 점수의 평균을 보기 위한 도구이면서, 동시에 그 평균이 얼마나 흔들리는지 보여 주는 도구입니다. 올바른 분할 전략과 분산 해석이 함께 있어야 비교가 의미를 가집니다.

핵심 원칙: 점수 하나가 아닌 평균 ± 표준편차로 생각하고, 두 모델을 비교할 때는 차이가 표준편차보다 큰지 확인하며, 데이터 구조(그룹, 시계열)를 반영하는 교차 검증 방식을 선택합니다.

다음 글에서는 평균 점수 뒤에 숨은 실패 패턴을 꺼내는 오류 분석으로 넘어갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- **Model Evaluation 101 (8/10): 교차 검증 이해하기 (현재 글)**
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Wikipedia — Cross-validation](https://en.wikipedia.org/wiki/Cross-validation_(statistics))

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, CrossValidation, KFold, Stratified, scikit-learn
