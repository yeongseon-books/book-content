---
series: model-evaluation-101
episode: 6
title: "Model Evaluation 101 (6/10): ROC와 AUC 이해하기"
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
  - ROC
  - AUC
  - PRCurve
  - scikit-learn
seo_description: ROC-AUC와 PR-AUC를 운영 임계값, 혼동 행렬, 비용 판단으로 연결하는 방법을 설명합니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (6/10): ROC와 AUC 이해하기

모델 A의 AUC가 0.85, 모델 B의 AUC가 0.82입니다. 모델 A를 배포해야 할까요? 그런데 실제로 FPR 5% 이하라는 운영 정책을 적용하면, 모델 A의 재현율은 0.45, 모델 B의 재현율은 0.61입니다. 이제 어떤 모델이 더 좋을까요?

이 글은 Model Evaluation 101 시리즈의 6번째 글입니다.

ROC와 AUC는 임계값을 아직 고정하지 않았을 때 후보 모델을 비교하는 데 매우 유용합니다. 그러나 AUC 하나로 배포 결정을 내리면 위험합니다. 곡선이 예쁘더라도 실제 운영 지점에서의 성능은 전혀 다를 수 있기 때문입니다. 이 글은 ROC 곡선 읽기에서 실제 운영 임계값 결정까지의 전 과정을 완성합니다.

![Model Evaluation 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/06/06-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 6장 흐름 개요*

> ROC-AUC는 모델의 순위화 능력 전반을 요약합니다. 하지만 배포는 하나의 임계값에서 일어나며, 그 지점에서의 혼동 행렬과 비용이 실제 운영을 결정합니다.

## 이 글에서 다룰 문제

- ROC 곡선은 무엇을 시각화하는가요?
- AUC(Area Under Curve)는 어떤 의미인가요?
- ROC-AUC와 PR-AUC는 언제 서로 다른 결론을 주나요?
- 운영 제약(FPR 예산)에서 임계값을 어떻게 선택하나요?
- AUC가 높아도 배포하면 안 되는 상황이 있을까요?

## ROC 곡선 이해하기

### FPR과 TPR

ROC 곡선은 거짓 양성 비율(FPR, x축)에 따른 진짜 양성 비율(TPR = 재현율, y축)의 트레이드오프를 시각화합니다.

```
FPR (거짓 양성 비율) = FP / (FP + TN)
                     = 실제 음성 중 양성으로 잘못 분류된 비율

TPR (진짜 양성 비율, 재현율) = TP / (TP + FN)
                              = 실제 양성 중 올바르게 탐지된 비율
```

임계값을 낮추면:
- TPR 증가 (더 많은 양성 탐지)
- FPR 증가 (더 많은 거짓 경보)

임계값을 높이면:
- TPR 감소
- FPR 감소

ROC 곡선은 이 트레이드오프를 모든 임계값에 걸쳐 보여줍니다.

### AUC의 의미

AUC(0에서 1 사이)는 다음을 의미합니다:

- **AUC = 1.0**: 완벽한 분류기 (모든 임계값에서 양성과 음성을 완벽히 구분)
- **AUC = 0.5**: 무작위 분류기 (동전 던지기 수준)
- **AUC = 0.8**: 임의로 선택한 양성 샘플의 점수가 임의 음성 샘플보다 높을 확률이 80%

AUC는 확률적 해석이 있습니다: "임의의 양성 샘플과 임의의 음성 샘플을 뽑았을 때, 모델이 양성에 더 높은 점수를 줄 확률"이 AUC입니다.

## 전체 분석 코드: 곡선에서 운영 결정까지

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)
from sklearn.model_selection import train_test_split

# 불균형 데이터 (4% 양성)
X, y = make_classification(
    n_samples=5000,
    n_features=12,
    n_informative=5,
    n_redundant=3,
    weights=[0.96, 0.04],
    class_sep=1.2,
    flip_y=0.02,
    random_state=31,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

# 1단계: 전체 성능 요약
roc_auc = roc_auc_score(y_test, proba)
pr_auc = average_precision_score(y_test, proba)
print(f"=== 전체 성능 요약 ===")
print(f"ROC-AUC: {roc_auc:.3f}")
print(f"PR-AUC:  {pr_auc:.3f}")
print(f"베이스레이트: {y.mean():.3f}")
print()

# 2단계: ROC 곡선 주요 지점 분석
fpr, tpr, thresholds = roc_curve(y_test, proba)
print("=== ROC 곡선 주요 지점 ===")
print(f"{'FPR':>6} {'TPR(재현율)':>12} {'임계값':>8}")
for target_fpr in [0.01, 0.02, 0.05, 0.10, 0.20]:
    idx = max(i for i, f in enumerate(fpr) if f <= target_fpr)
    print(f"{fpr[idx]:>6.3f} {tpr[idx]:>12.3f} {thresholds[idx]:>8.3f}")
print()

# 3단계: 운영 정책 적용 (FPR <= 0.05)
target_fpr = 0.05
idx = max(i for i, f in enumerate(fpr) if f <= target_fpr)
chosen_threshold = thresholds[idx]
pred = (proba >= chosen_threshold).astype(int)

cm = confusion_matrix(y_test, pred)
tn, fp, fn, tp = cm.ravel()
print(f"=== FPR <= 0.05 정책 적용 ===")
print(f"선택된 임계값: {chosen_threshold:.3f}")
print(f"실제 FPR: {fp/(fp+tn):.3f}")
print(f"정밀도: {precision_score(y_test, pred, zero_division=0):.3f}")
print(f"재현율: {recall_score(y_test, pred):.3f}")
print(f"혼동 행렬:\n{cm}")
print(f"비용 (FP=1, FN=10): {fp*1 + fn*10}")
```

예상 출력:
```
=== 전체 성능 요약 ===
ROC-AUC: 0.819
PR-AUC:  0.463
베이스레이트: 0.040

=== ROC 곡선 주요 지점 ===
   FPR  TPR(재현율)   임계값
 0.009       0.400    0.302
 0.019       0.427    0.250
 0.049       0.507    0.141
 0.098       0.573    0.100
 0.199       0.667    0.061

=== FPR <= 0.05 정책 적용 ===
선택된 임계값: 0.141
실제 FPR: 0.049
정밀도: 0.352
재현율: 0.507
혼동 행렬:
[[1355   70]
 [  37   38]]
비용 (FP=1, FN=10): 440
```

## ROC-AUC vs PR-AUC: 언제 무엇을 쓸까

```python
# 두 지표의 차이를 직관적으로 이해하기
print("=== ROC-AUC vs PR-AUC 비교 ===")
print()
print(f"ROC-AUC: {roc_auc:.3f}")
print("  - 양성과 음성의 순위 분리 능력")
print("  - 베이스레이트에 덜 민감")
print("  - 음성 클래스가 많을수록 낙관적으로 보일 수 있음")
print()
print(f"PR-AUC: {pr_auc:.3f}")
print("  - 양성 클래스를 얼마나 정밀하게 탐지하는가")
print("  - 베이스레이트에 민감 (낮은 베이스레이트 = 낮은 PR-AUC)")
print("  - 불균형 데이터에서 ROC보다 더 보수적인 평가")
print()
print("결론:")
print(f"  베이스레이트 {y.mean()*100:.1f}%에서:")
print(f"  ROC-AUC {roc_auc:.3f}는 '양성-음성 구분 능력 좋음'을 말하지만")
print(f"  PR-AUC {pr_auc:.3f}는 '실제 양성 탐지 품질은 제한적'을 경고함")
```

| 지표 | ROC-AUC | PR-AUC |
| --- | --- | --- |
| 측정 대상 | 양성/음성 순위 분리 | 양성 탐지 정밀도 |
| 베이스레이트 영향 | 낮음 | 높음 |
| 불균형 데이터 | 낙관적으로 보일 수 있음 | 더 현실적 |
| 사용 상황 | 모델 비교, 일반 성능 | 양성 탐지 품질 중요 시 |
| 기준선 | 0.5 (무작위) | 베이스레이트 |

## 임계값 후보 비교 분석

```python
# 여러 임계값에서의 운영 결과 비교
print("=== 임계값 후보 비교 ===")
print(f"{'임계값':>8} {'FPR':>6} {'정밀도':>8} {'재현율':>8} {'비용':>8} {'운영 해석'}")
print("-" * 80)

candidates = [
    (0.10, "FPR 예산 초과, 비용은 낮음"),
    (0.141, "FPR <= 5% 정책 준수 최대 재현율"),
    (0.20, "더 보수적, 정밀도 높음"),
    (0.30, "높은 정밀도, 낮은 재현율"),
]

for t, desc in candidates:
    pred_c = (proba >= t).astype(int)
    tn_c, fp_c, fn_c, tp_c = confusion_matrix(y_test, pred_c).ravel()
    fpr_c = fp_c / (fp_c + tn_c)
    prec_c = tp_c / (tp_c + fp_c) if (tp_c + fp_c) > 0 else 0
    rec_c = tp_c / (tp_c + fn_c) if (tp_c + fn_c) > 0 else 0
    cost_c = fp_c * 1 + fn_c * 10
    policy_ok = "OK" if fpr_c <= 0.05 else "VIOLATION"
    print(f"{t:>8.3f} {fpr_c:>6.3f} {prec_c:>8.3f} {rec_c:>8.3f} {cost_c:>8d}  [{policy_ok}] {desc}")
```

## 두 모델 비교: AUC보다 운영 지점이 중요

```python
# 모델 B: 다른 알고리즘으로 AUC가 조금 낮지만 특정 FPR에서 재현율이 높을 수 있음
from sklearn.ensemble import GradientBoostingClassifier

model_b = GradientBoostingClassifier(n_estimators=50, random_state=42).fit(X_train, y_train)
proba_b = model_b.predict_proba(X_test)[:, 1]

roc_auc_b = roc_auc_score(y_test, proba_b)
pr_auc_b = average_precision_score(y_test, proba_b)

fpr_b, tpr_b, thresholds_b = roc_curve(y_test, proba_b)

# FPR <= 0.05에서 각 모델의 재현율 비교
idx_b = max(i for i, f in enumerate(fpr_b) if f <= 0.05)

print("=== 모델 비교: AUC vs 운영 지점 ===")
print(f"                모델 A      모델 B")
print(f"ROC-AUC:       {roc_auc:.3f}      {roc_auc_b:.3f}")
print(f"PR-AUC:        {pr_auc:.3f}      {pr_auc_b:.3f}")
print(f"재현율 @FPR<=5%: {tpr[idx]:.3f}      {tpr_b[idx_b]:.3f}")
print()
print("AUC가 높다고 운영 지점에서 항상 더 좋은 것은 아닙니다!")
print("운영 제약 조건(FPR 예산 등)에서의 재현율을 비교해야 합니다.")
```

## 비용 최소화와 정책 제약은 별개

```python
print("=== 비용 vs 정책 제약 ===")
print()
print("임계값 0.10 분석:")
pred_010 = (proba >= 0.10).astype(int)
tn_010, fp_010, fn_010, tp_010 = confusion_matrix(y_test, pred_010).ravel()
fpr_010 = fp_010 / (fp_010 + tn_010)
cost_010 = fp_010 * 1 + fn_010 * 10
print(f"  FPR: {fpr_010:.3f}  (정책 위반! 0.05 초과)")
print(f"  비용: {cost_010} (0.141보다 낮음)")
print()

print("임계값 0.141 분석:")
pred_141 = (proba >= 0.141).astype(int)
tn_141, fp_141, fn_141, tp_141 = confusion_matrix(y_test, pred_141).ravel()
fpr_141 = fp_141 / (fp_141 + tn_141)
cost_141 = fp_141 * 1 + fn_141 * 10
print(f"  FPR: {fpr_141:.3f}  (정책 준수: 0.05 이하)")
print(f"  비용: {cost_141}")
print()

print("결론:")
print("  비용만 보면 0.10이 더 낮아 보이지만,")
print("  FPR 정책(최대 5%)을 위반하므로 선택 불가.")
print("  배포 기준은 비용 최소화와 정책 준수를 동시에 만족해야 합니다.")
```

## Before vs. After: AUC 해석 방식 비교

| 항목 | 나이브 접근 | 올바른 접근 |
| --- | --- | --- |
| 비교 지표 | AUC 하나 | AUC + PR-AUC + 운영 지점 재현율 |
| 임계값 | AUC에서 직접 결정 | 운영 정책에서 역산 |
| 배포 결정 | "AUC 0.82, 충분함" | "FPR 5% 제약에서 재현율 50.7%—목표 달성 여부 확인" |
| 불균형 처리 | ROC-AUC만 | PR-AUC 추가 확인 |
| 비용 분석 | 없음 | FP/FN 비용으로 총비용 계산 |

## 자주 하는 실수

**실수 1 — "AUC 0.85니까 배포 준비 됨"**

AUC는 모든 임계값에 걸친 평균 성능이지, 실제 운영 임계값에서의 성능이 아닙니다. 특정 FPR 제약이나 재현율 목표가 있다면, 그 지점에서의 실제 성능을 따로 확인해야 합니다.

**실수 2 — 불균형 데이터에서 ROC-AUC만 보기**

베이스레이트가 낮을수록 ROC-AUC는 낙관적으로 보입니다. 음성이 많아서 FPR 분모가 커지기 때문입니다. 불균형 데이터에서는 PR-AUC를 함께 확인해야 합니다.

**실수 3 — 비용 최소화와 정책 제약을 혼동**

비용을 최소화하는 임계값이 FPR 정책 제약을 위반할 수 있습니다. 두 가지 목표를 동시에 만족하는 임계값을 찾아야 합니다.

**실수 4 — ROC 곡선의 전체 모양만 보기**

ROC 곡선의 왼쪽 위 꼭짓점 근처(낮은 FPR, 높은 TPR)가 실제 운영에서 관심 있는 영역입니다. 특히 엄격한 FPR 제약이 있다면, 그 FPR 이하에서의 TPR이 핵심입니다.

**실수 5 — 단일 모델 선택에서 AUC 격차 과대해석**

AUC 0.82와 0.83의 차이는 통계적으로 의미 없을 수 있습니다. 교차 검증으로 불확실성을 추정하고, 실제 관심 있는 운영 지점에서의 성능 차이로 비교해야 합니다.

## 운영 결론 문장 예시

```
[ROC/AUC 분석 결론]

ROC-AUC 0.819는 양성-음성 순위 분리 능력이 양호함을 나타냅니다.
그러나 PR-AUC 0.463은 베이스레이트 4%에서 실제 양성 탐지 품질이
제한적임을 경고합니다.

FPR <= 5% 운영 정책 적용 시:
  - 선택 임계값: 0.141
  - 재현율: 0.507 (목표 60% 미달)
  - 정밀도: 0.352
  - 예상 비용: 440 (FP 70건, FN 37건)

판정: 재현율 목표(60%) 미달로 배포 보류.
개선 방향: 더 많은 양성 학습 데이터 확보, 클래스 가중치 조정,
           또는 FPR 예산 완화(7%로 확장) 검토.
```

## 모델 비교에서 AUC를 올바르게 쓰는 법

```python
# 여러 모델의 ROC-AUC와 PR-AUC를 함께 비교하는 패턴
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import numpy as np

models = {
    "로지스틱 회귀": LogisticRegression(max_iter=2000, random_state=42),
    "랜덤 포레스트": RandomForestClassifier(n_estimators=100, random_state=42),
    "그래디언트 부스팅": GradientBoostingClassifier(n_estimators=100, random_state=42),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("=== 모델 비교: ROC-AUC vs PR-AUC ===")
print(f"{'모델':>20} {'ROC-AUC':>10} {'PR-AUC':>10} {'운영 추천'}")
print("-" * 65)

for name, clf in models.items():
    # 교차 검증으로 AUC 추정 (더 신뢰할 수 있음)
    roc_scores = cross_val_score(clf, X_train, y_train, cv=cv,
                                  scoring="roc_auc")
    pr_scores = cross_val_score(clf, X_train, y_train, cv=cv,
                                 scoring="average_precision")

    roc_mean = roc_scores.mean()
    pr_mean = pr_scores.mean()

    # 베이스레이트 대비 PR-AUC 비율 (실제 개선 배수)
    baseline_pr = y_train.mean()
    pr_lift = pr_mean / baseline_pr

    recommend = "1순위" if pr_mean == max(
        cross_val_score(m, X_train, y_train, cv=cv, scoring="average_precision").mean()
        for m in models.values()
    ) else ""

    print(f"{name:>20} {roc_mean:>10.3f} {pr_mean:>10.3f}  리프트 {pr_lift:.1f}x {recommend}")

print()
print("주의: ROC-AUC가 높아도 PR-AUC 리프트가 낮으면 실제 양성 탐지력이 약함")
print("불균형 데이터에서는 PR-AUC 리프트(베이스레이트 대비 개선배수)로 비교 권장")
```

## 운영 체크리스트

- [ ] ROC-AUC와 PR-AUC를 함께 확인했습니다.
- [ ] 운영 FPR 제약(예: 5% 이하)을 먼저 정의했습니다.
- [ ] 정책 제약 아래에서 선택된 임계값을 명시했습니다.
- [ ] 선택 임계값의 혼동 행렬을 기록했습니다.
- [ ] FP/FN 비용으로 총 운영 비용을 계산했습니다.
- [ ] 재현율 목표 달성 여부로 배포 여부를 판정했습니다.

## 처음 질문으로 돌아가기

- **ROC 곡선은 무엇을 시각화하는가요?**
  - 모든 가능한 임계값에서의 FPR(거짓 양성 비율)과 TPR(진짜 양성 비율, 재현율)의 트레이드오프를 시각화합니다. 왼쪽 위 꼭짓점에 가까울수록 좋습니다.

- **ROC-AUC와 PR-AUC는 언제 서로 다른 결론을 주나요?**
  - 클래스 불균형이 심할 때입니다. 양성이 5% 미만인 데이터에서 ROC-AUC는 0.8이 넘어도 좋아 보이지만, PR-AUC는 0.5 미만으로 낮을 수 있습니다. 불균형 데이터에서는 항상 두 지표를 함께 봐야 합니다.

- **AUC가 높아도 배포하면 안 되는 상황이 있을까요?**
  - 있습니다. 운영 FPR 제약 아래에서 재현율이 목표치에 못 미치는 경우입니다. 예를 들어 ROC-AUC 0.819인 모델도 FPR 5% 제약에서 재현율 0.507에 그쳐, 재현율 60% 목표를 달성하지 못한다면 배포 준비가 안 된 것입니다.

---

## 정리

ROC와 AUC는 임계값을 고르기 전 후보 모델의 순위화 능력을 비교하는 데 유용합니다. 그러나 진짜 배포 판단은 항상 하나의 임계값, 하나의 혼동 행렬, 하나의 비용 가정으로 내려와야 합니다.

평가 시리즈의 흐름을 정리하면, 3장에서 정확도의 한계를 보았고, 4장에서 정밀도-재현율 트레이드오프를 운영 임계값으로 연결했고, 5장에서 F1의 올바른 사용법을 익혔으며, 6장에서 ROC-AUC로 모델을 비교한 뒤 다시 운영 임계값으로 착지하는 전 과정을 완성했습니다.

다음 글에서는 모델이 출력하는 확률값이 실제로 얼마나 믿을 수 있는지를 다루는 캘리브레이션(보정)을 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- **Model Evaluation 101 (6/10): ROC와 AUC 이해하기 (현재 글)**
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — roc_curve](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
- [scikit-learn — roc_auc_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [Wikipedia — ROC curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, ROC, AUC, PRCurve, scikit-learn
