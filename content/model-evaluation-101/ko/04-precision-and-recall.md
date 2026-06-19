---
series: model-evaluation-101
episode: 4
title: "Model Evaluation 101 (4/10): 정밀도와 재현율"
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
  - Precision
  - Recall
  - ConfusionMatrix
  - scikit-learn
seo_description: 정밀도와 재현율을 정의 설명에서 끝내지 않고, 임계값을 바꿀 때 운영 알림 정책이 어떻게 달라지는지 결정 메모 형식으로 보여 줍니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (4/10): 정밀도와 재현율

결제 이상 징후 탐지 시스템의 엔지니어링 팀 회의가 있었습니다. 두 팀이 의견이 갈렸습니다. 보안팀은 "재현율을 최대화해야 합니다. 사기 거래를 하나라도 놓치면 안 됩니다"라고 주장했습니다. 운영팀은 "정밀도를 높여야 합니다. 오탐이 너무 많으면 고객 항의와 처리 비용이 감당이 안 됩니다"라고 반박했습니다. 누가 맞을까요?

이 글은 Model Evaluation 101 시리즈의 4번째 글입니다.

둘 다 맞습니다. 그리고 바로 이것이 정밀도와 재현율의 트레이드오프입니다. 임계값을 낮추면 재현율이 올라가지만 정밀도가 낮아집니다. 임계값을 높이면 정밀도가 올라가지만 재현율이 낮아집니다. 이 교환을 숫자와 운영 문장으로 연결하는 것이 이 글의 핵심입니다.

![Model Evaluation 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/04/04-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 4장 흐름 개요*

> 정밀도와 재현율은 하나의 모델이 내리는 두 가지 다른 결정입니다 — 임계값을 바꾸면 같은 모델이 완전히 다른 운영 정책을 구현합니다.

## 이 글에서 다룰 문제

- 정밀도와 재현율은 정확히 무엇을 측정할까요?
- 임계값을 올리거나 낮출 때 어떤 트레이드오프가 발생할까요?
- 비즈니스 시나리오에서 최적 임계값을 어떻게 결정할까요?
- 평균 정밀도(AP)는 어디에 쓰는 지표인가요?
- 초보자가 가장 자주 오해하는 포인트는 무엇일까요?

## 정의: 수식보다 운영 의미로 이해하기

### 정밀도 (Precision)

```
정밀도 = TP / (TP + FP)
       = 양성으로 예측한 것 중 실제 양성의 비율
```

**운영 의미:** "경보를 울린 것 중 진짜 문제가 얼마나 되나요?"

정밀도가 낮으면 거짓 경보가 많습니다. 이상 탐지 시스템에서 정밀도가 0.1이면 경보 10건 중 1건만 실제 이상 상황입니다. 리뷰 팀이 불필요한 작업에 시간을 낭비하고, 고객은 불필요한 마찰을 경험합니다.

### 재현율 (Recall, Sensitivity)

```
재현율 = TP / (TP + FN)
       = 실제 양성 중 예측으로 잡아낸 비율
```

**운영 의미:** "실제 문제 중 얼마나 놓치지 않았나요?"

재현율이 낮으면 탐지되지 않고 지나가는 실제 문제가 많습니다. 의료 진단에서 재현율이 0.7이면 실제 환자 10명 중 3명을 놓칩니다.

### 두 지표의 트레이드오프

| | 정밀도 높음 | 재현율 높음 |
| --- | --- | --- |
| 임계값 | 높음 (0.7~0.9) | 낮음 (0.1~0.3) |
| 경보 건수 | 적음 | 많음 |
| 진짜 양성 탐지 | 적음 (놓침 많음) | 많음 |
| 거짓 경보 | 거의 없음 | 많음 |
| 적합한 상황 | 오탐 비용이 클 때 | 놓침 비용이 클 때 |

## 운영 시나리오: 결제 이상 징후 탐지

이 시나리오에서 비즈니스 맥락은 다음과 같습니다.

- **재현율이 낮으면**: 실제 이상 거래를 놓칩니다. 손실 발생.
- **정밀도가 낮으면**: 리뷰 팀이 거짓 경보를 너무 많이 처리합니다. 운영 비용 증가.
- **리뷰 팀 용량**: 하루 최대 100건 처리 가능.
- **이상 거래 1건당 예상 손실**: 50만원
- **거짓 경보 처리 비용**: 1만원

이 맥락에서 임계값 선택은 "몇 % 정밀도에서 몇 % 재현율로 운영할지"를 결정하는 정책 결정입니다.

## 임계값별 운영 결과 분석

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
import numpy as np

# 데이터 생성 (10% 이상 비율)
X, y = make_classification(
    n_samples=3000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.9, 0.1],
    class_sep=1.0,
    flip_y=0.02,
    random_state=7,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

# 임계값별 분석
print("=== 임계값별 성능 및 운영 비용 ===")
print(f"{'임계값':>6} {'정밀도':>8} {'재현율':>8} {'F1':>8} {'경보수':>8} {'FN손실(만)':>12} {'FP비용(만)':>12} {'총비용(만)':>12}")
print("-" * 90)

for threshold in [0.20, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70]:
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()

    prec = precision_score(y_test, pred, zero_division=0)
    rec = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)
    flagged = pred.sum()

    fn_cost = fn * 50   # FN당 50만원 손실
    fp_cost = fp * 1    # FP당 1만원 처리 비용
    total_cost = fn_cost + fp_cost

    print(
        f"{threshold:>6.2f} {prec:>8.3f} {rec:>8.3f} {f1:>8.3f} "
        f"{flagged:>8d} {fn_cost:>12,d} {fp_cost:>12,d} {total_cost:>12,d}"
    )

print(f"\nAP (Average Precision): {average_precision_score(y_test, proba):.3f}")
```

예상 출력 (근사값):
```
=== 임계값별 성능 및 운영 비용 ===
임계값    정밀도    재현율        F1    경보수   FN손실(만)   FP비용(만)   총비용(만)
------------------------------------------------------------------------------------------
  0.20    0.610    0.735    0.668      118      1,300          46      1,346
  0.30    0.720    0.694    0.707       94      1,500          28      1,528
  0.35    0.795    0.633    0.704       78      1,800          16      1,816
  0.40    0.840    0.592    0.695       69      2,000          11      2,011
  0.50    0.881    0.531    0.663       59      2,300           7      2,307
  0.60    0.920    0.449    0.606       48      2,700           4      2,704
  0.70    0.952    0.408    0.572       42      2,900           2      2,902

AP (Average Precision): 0.745
```

## 혼동 행렬로 각 임계값 깊이 이해하기

```python
# 두 가지 극단적 임계값 비교
for threshold, label in [(0.20, "낮은 임계값 (재현율 우선)"), (0.70, "높은 임계값 (정밀도 우선)")]:
    pred = (proba >= threshold).astype(int)
    cm = confusion_matrix(y_test, pred)
    tn, fp, fn, tp = cm.ravel()

    print(f"\n=== {label} (임계값={threshold}) ===")
    print(f"혼동 행렬:")
    print(f"               예측: 음성    예측: 양성")
    print(f"실제: 음성       {tn:6d}      {fp:6d}   (총 {tn+fp}건)")
    print(f"실제: 양성       {fn:6d}      {tp:6d}   (총 {fn+tp}건)")
    print()
    print(f"정밀도: {tp/(tp+fp):.3f} → 경보 {tp+fp}건 중 {tp}건이 실제 이상")
    print(f"재현율: {tp/(tp+fn):.3f} → 실제 이상 {tp+fn}건 중 {tp}건 탐지")
    print(f"놓친 이상: {fn}건 (손실 {fn*50:,}만원)")
    print(f"거짓 경보: {fp}건 (처리 비용 {fp*1:,}만원)")
```

## 운영점 표: 정밀도-재현율 교환 한눈에 보기

| 임계값 | 정밀도 | 재현율 | 경보 건수 | 실무 해석 |
| --- | ---: | ---: | ---: | --- |
| 0.20 | 0.610 | 0.735 | 118건 | 많이 잡지만 오탐이 많아 팀이 피로합니다. |
| 0.35 | 0.795 | 0.633 | 78건 | 놓침과 오탐이 균형 잡힌 절충점입니다. |
| 0.50 | 0.881 | 0.531 | 59건 | 팀 부담은 줄지만 놓침이 눈에 띄게 늘어납니다. |
| 0.70 | 0.952 | 0.408 | 42건 | 경보는 깨끗하지만 실제 이상을 많이 놓칩니다. |

**임계값 0.35를 운영 기본값으로 제안하는 이유:**
- 재현율 0.633으로 이상 거래의 약 63%를 탐지합니다.
- 정밀도 0.795로 경보 중 80%가 실제 이상입니다.
- 경보 78건은 팀 용량(100건) 내에 있습니다.
- 0.20보다 거짓 경보가 40건 적어 팀 부담이 낮습니다.

## 정밀도-재현율 곡선과 AP 이해하기

```python
from sklearn.metrics import precision_recall_curve
import numpy as np

precisions, recalls, thresholds = precision_recall_curve(y_test, proba)
ap = average_precision_score(y_test, proba)

print(f"Average Precision (AP): {ap:.3f}")
print()
print("=== 정밀도-재현율 곡선 주요 포인트 ===")
print(f"{'재현율':>8} {'정밀도':>8} {'임계값':>8}")
for i in range(0, len(thresholds), len(thresholds)//8):
    print(f"{recalls[i]:>8.3f} {precisions[i]:>8.3f} {thresholds[i]:>8.3f}")

print()
print("AP 해석:")
print(f"  AP = {ap:.3f}는 정밀도-재현율 곡선 아래 면적")
print("  AP가 높을수록 전반적인 정밀도-재현율 균형이 좋음")
print("  다만 AP는 배포 임계값을 직접 알려주지 않음")
print("  임계값은 위 표에서 비즈니스 맥락에 맞게 선택해야 함")
```

AP(Average Precision)는 0.745입니다. 이 숫자는 모든 임계값을 훑은 정밀도-재현율 곡선의 아래 면적으로, 후보 모델 비교에 유용합니다. 그러나 AP만으로는 실제 운영 임계값이 결정되지 않습니다. AP가 같은 두 모델이라도 특정 재현율 구간에서의 정밀도는 다를 수 있기 때문입니다.

## Before vs. After: 임계값 결정 방식 비교

| 항목 | 나이브 접근 | 올바른 접근 |
| --- | --- | --- |
| 임계값 | 0.5 고정 | 비즈니스 맥락에서 결정 |
| 정밀도-재현율 | 정의 암기 | 운영 결과로 번역 |
| 의사결정 기준 | 높은 F1 | 비용 구조 + 팀 용량 |
| 문서화 | 없음 | 임계값 결정 근거 메모 |
| 리뷰 주기 | 없음 | 분기별 임계값 재검토 |

## 자주 하는 실수

**실수 1 — 정밀도와 재현율의 정의만 외우고 활용 못 함**

"정밀도 = TP/(TP+FP)"를 외웠더라도, 실제 운영에서 임계값을 어떻게 정해야 하는지 모르면 의미가 없습니다. 정밀도와 재현율은 항상 임계값과 함께 논의해야 합니다.

**실수 2 — 정밀도와 재현율 중 하나만 최대화**

재현율 1.0을 달성하는 것은 쉽습니다. 임계값을 0으로 설정해 모든 것을 양성으로 예측하면 됩니다. 그러나 그때 정밀도는 베이스레이트(예: 10%)가 됩니다. 두 지표는 항상 트레이드오프 관계에서 함께 봐야 합니다.

**실수 3 — AP를 배포 임계값으로 오해**

AP가 0.8이면 "재현율 80%에서 정밀도 80%"가 아닙니다. AP는 전체 정밀도-재현율 곡선의 요약입니다. 실제 배포 임계값은 위에서처럼 비용 구조와 운영 제약을 반영해 별도로 결정해야 합니다.

**실수 4 — 임계값을 한 번 정하고 잊기**

비즈니스 환경은 바뀝니다. 이상 거래 패턴이 변하거나 팀 용량이 바뀌면 최적 임계값도 달라집니다. 분기별로 임계값이 여전히 적절한지 검토하는 프로세스가 필요합니다.

**실수 5 — 클래스 불균형 상황에서 정밀도를 무시**

소수 클래스 비율이 낮으면 재현율을 높이기 위해 임계값을 낮추는 경향이 있습니다. 그러나 임계값을 너무 낮추면 정밀도가 베이스레이트에 수렴하고, 실제로는 아무 의미 없는 경보가 대부분이 됩니다.

## 운영 메모 작성 예시

임계값 결정 후 반드시 다음 형식으로 운영 메모를 남겨야 합니다.

```
[결제 이상 징후 탐지 시스템 - 임계값 결정 메모]

결정 사항: 운영 기본 임계값 = 0.35
결정 근거:
  - 정밀도 0.795: 경보 중 약 80%가 실제 이상 → 팀 신뢰도 유지
  - 재현율 0.633: 이상 거래 63% 탐지 → 손실 허용 범위 내
  - 예상 경보 건수 78건/일 → 팀 처리 용량(100건) 이내
  - 예상 일일 비용: FN 1,800만원 + FP 16만원 = 1,816만원

비상 정책:
  - 고위험 기간(명절 등): 임계값 0.20으로 완화 (재현율 우선)
  - 팀 운영 제한 시: 임계값 0.50으로 강화 (처리량 우선)

다음 검토 일정: 2026-08-01
```

## 임계값 선택 자동화 코드

실제 프로젝트에서는 임계값 탐색을 자동화하고 최적점을 시각적으로 선택합니다.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score

# 정밀도-재현율 곡선 전체 계산
precisions, recalls, thresholds_pr = precision_recall_curve(y_test, proba)
ap = average_precision_score(y_test, proba)

# 각 목표 재현율에서 최고 정밀도 찾기
print("=== 재현율 목표별 최적 임계값 ===")
print(f"{'재현율 목표':>12} {'달성 정밀도':>12} {'임계값':>10} {'경보 건수':>10}")
print("-" * 50)

for target_recall in [0.50, 0.60, 0.70, 0.80, 0.90]:
    # 재현율이 목표 이상인 구간에서 정밀도 최대
    valid_mask = recalls[:-1] >= target_recall
    if not valid_mask.any():
        print(f"{target_recall:>12.2f} {'달성 불가':>12}")
        continue

    best_idx = np.argmax(precisions[:-1][valid_mask])
    best_prec = precisions[:-1][valid_mask][best_idx]
    best_thresh = thresholds_pr[valid_mask][best_idx]

    pred_t = (proba >= best_thresh).astype(int)
    n_flagged = pred_t.sum()

    print(f"{target_recall:>12.2f} {best_prec:>12.3f} {best_thresh:>10.3f} {n_flagged:>10d}")

print(f"\nAP (전체 곡선 요약): {ap:.3f}")
```

이 코드는 "재현율 최소 70% 보장" 같은 운영 목표를 먼저 정하고, 그 제약 아래에서 정밀도를 최대화하는 임계값을 자동으로 찾습니다. 비즈니스 요구사항에서 임계값을 역산하는 올바른 방향입니다.

## 실제 시나리오별 임계값 전략

비즈니스 도메인에 따라 임계값 선택 전략이 달라집니다.

| 도메인 | 핵심 오류 | 전략 | 권장 임계값 방향 |
| --- | --- | --- | --- |
| 의료 진단 (암) | FN (환자 놓침) | 재현율 최대화 | 낮게 (0.2~0.3) |
| 사기 탐지 | FN (사기 놓침) | 재현율 우선, 팀 용량 고려 | 중간 (0.3~0.4) |
| 스팸 필터 | FP (정상 메일 차단) | 정밀도 최대화 | 높게 (0.7~0.9) |
| 추천 시스템 | 양쪽 균형 | F1 최적화 | 중간 (0.4~0.6) |
| 광고 클릭 예측 | FP (예산 낭비) | 정밀도 우선 | 높게 (0.6~0.8) |

```python
# 도메인별 임계값 선택 함수
def select_threshold_by_domain(proba, y_test, domain="fraud"):
    """도메인 특성에 따른 임계값 선택"""
    strategies = {
        "medical": {"min_recall": 0.90, "priority": "recall"},
        "fraud": {"min_recall": 0.65, "priority": "balanced"},
        "spam": {"min_precision": 0.95, "priority": "precision"},
        "recommendation": {"priority": "f1"},
    }

    strategy = strategies.get(domain, strategies["recommendation"])

    precisions, recalls, thresholds = precision_recall_curve(y_test, proba)
    f1_scores = 2 * (precisions[:-1] * recalls[:-1]) / (
        precisions[:-1] + recalls[:-1] + 1e-10
    )

    if strategy["priority"] == "recall":
        # 재현율 최소 보장 아래에서 정밀도 최대화
        mask = recalls[:-1] >= strategy["min_recall"]
        if mask.any():
            best_idx = np.argmax(precisions[:-1][mask])
            return float(thresholds[mask][best_idx])
    elif strategy["priority"] == "precision":
        # 정밀도 최소 보장 아래에서 재현율 최대화
        mask = precisions[:-1] >= strategy["min_precision"]
        if mask.any():
            best_idx = np.argmax(recalls[:-1][mask])
            return float(thresholds[mask][best_idx])
    else:
        # F1 최대화
        best_idx = np.argmax(f1_scores)
        return float(thresholds[best_idx])

    return 0.5  # 기본값

# 도메인별 임계값 비교
print("=== 도메인별 권장 임계값 ===")
for domain in ["medical", "fraud", "spam", "recommendation"]:
    t = select_threshold_by_domain(proba, y_test, domain)
    pred_t = (proba >= t).astype(int)
    from sklearn.metrics import precision_score, recall_score
    prec_t = precision_score(y_test, pred_t, zero_division=0)
    rec_t = recall_score(y_test, pred_t, zero_division=0)
    print(f"  {domain:>16}: 임계값={t:.2f}, 정밀도={prec_t:.3f}, 재현율={rec_t:.3f}")
```

## 운영 체크리스트

- [ ] 비즈니스 시나리오에서 FP와 FN 비용을 정의했습니다.
- [ ] 임계값별 정밀도·재현율 표를 만들었습니다.
- [ ] 리뷰 팀 처리 용량을 경보 건수 제약으로 반영했습니다.
- [ ] 혼동 행렬로 각 임계값의 실제 운영 결과를 확인했습니다.
- [ ] AP를 후보 모델 비교용 숫자로만 사용했습니다.
- [ ] 임계값 결정 근거를 운영 메모로 남겼습니다.
- [ ] 임계값 재검토 일정을 계획했습니다.

## 처음 질문으로 돌아가기

- **정밀도와 재현율은 정확히 무엇을 측정할까요?**
  - 정밀도는 "양성으로 예측한 것 중 실제 양성 비율"로, 경보 품질을 측정합니다. 재현율은 "실제 양성 중 탐지한 비율"로, 탐지 완전성을 측정합니다. 두 지표는 서로 트레이드오프 관계에 있어 하나를 높이면 다른 하나가 낮아집니다.

- **임계값을 올리거나 낮출 때 어떤 트레이드오프가 발생할까요?**
  - 임계값을 낮추면 더 많은 것을 양성으로 분류하여 재현율이 오르고 정밀도가 낮아집니다. 임계값을 높이면 더 확실한 것만 양성으로 분류하여 정밀도가 오르고 재현율이 낮아집니다. 임계값 0.20과 0.70 사이에서 경보 건수는 118건에서 42건으로 줄고, 놓치는 이상 거래는 크게 늘어납니다.

- **평균 정밀도(AP)는 어디에 쓰는 지표인가요?**
  - AP는 모든 임계값에서의 정밀도-재현율 균형을 요약한 단일 점수로, 후보 모델 간 비교에 사용합니다. AP가 높은 모델이 전반적으로 더 좋은 정밀도-재현율 균형을 가집니다. 그러나 AP는 실제 배포 임계값을 직접 알려주지 않으며, 임계값은 비즈니스 비용 구조에서 별도로 결정해야 합니다.

---

## 정리

정밀도와 재현율은 정의보다 운영점 선택에서 가치가 드러납니다. 임계값을 바꿀 때 어떤 실수가 늘고 줄어드는지 메모 형식으로 남겨야 실제 의사결정에 쓸 수 있습니다. 그리고 이 결정은 비용 구조, 팀 용량, 비즈니스 리스크 허용 수준이라는 운영 맥락에서 이루어져야 합니다.

다음 글에서는 정밀도와 재현율을 하나의 숫자로 압축한 F1 점수를 다루되, 그 요약이 무엇을 숨기는지와 올바른 임계값 선택 절차를 함께 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- **Model Evaluation 101 (4/10): 정밀도와 재현율 (현재 글)**
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html)
- [scikit-learn — recall_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn — precision_recall_curve example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Precision, Recall, ConfusionMatrix, scikit-learn
