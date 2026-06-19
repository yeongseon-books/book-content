---
series: model-evaluation-101
episode: 7
title: "Model Evaluation 101 (7/10): 확률 보정 이해하기"
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
  - Calibration
  - BrierScore
  - Reliability
  - scikit-learn
seo_description: 분류 모델의 확률값이 실제 빈도와 일치하도록 보정하는 캘리브레이션 개념과 브라이어 점수 기반 신뢰도 측정법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (7/10): 확률 보정 이해하기

보험 회사의 리스크 평가 모델이 특정 고객에게 "사고 발생 확률 85%"라고 예측했습니다. 그 예측을 믿고 보험료를 설정했는데, 실제로 그 점수 대의 고객들을 추적해 보니 사고가 약 60%에서 발생했습니다. 모델이 일관되게 과신(overconfidence)을 보인 것입니다. 이 차이가 몇 년에 걸쳐 수천 건에 누적되면 실제 손실로 이어집니다.

이 글은 Model Evaluation 101 시리즈의 7번째 글입니다.

모델이 0.8의 확률을 예측했다고 할 때, 그 0.8이 실제로도 10번 중 8번 정도 맞는지를 확인하지 않으면, 그 숫자는 점수처럼 보일 뿐 확률이라고 부르기 어렵습니다. 바로 이 지점을 다루는 개념이 캘리브레이션(calibration, 확률 보정)입니다.

![Model Evaluation 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/07/07-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 7장 흐름 개요*

> 캘리브레이션은 모델의 0.8 점수를 '약 80% 확률'로 읽을 수 있게 해 주는 성질입니다 — 순위 품질과 확률 품질은 다른 축이고, 확률에 비용을 곱해 결정하는 시스템은 AUC가 아닌 이 두 번째 축이 필요합니다.

## 이 글에서 다룰 문제

- 캘리브레이션이란 무엇이고 왜 필요할까요?
- 신뢰도 다이어그램(Reliability Diagram)은 어떻게 읽을까요?
- Brier 점수는 무엇을 측정하고 어떻게 해석할까요?
- 보정 방법(Platt, Isotonic)은 어떤 차이가 있을까요?
- AUC가 높아도 캘리브레이션이 나쁠 수 있는 이유는 무엇인가요?

## 캘리브레이션의 정의

**완벽하게 캘리브레이션된 모델:** 예측 확률 0.7로 분류된 샘플들 중 실제로 70%가 양성

```
P(Y=1 | f(X) = p) = p   for all p ∈ [0, 1]
```

실제 모델에서는 이 조건이 정확히 만족되기 어렵습니다. 예를 들어:

- **과신(Overconfidence)**: 모델이 0.9를 예측했는데 실제 비율은 0.7
- **과소신(Underconfidence)**: 모델이 0.7을 예측했는데 실제 비율은 0.85
- **S자 왜곡**: 낮은 확률 구간은 실제보다 높게, 높은 구간은 실제보다 낮게 예측

### 어떤 모델이 캘리브레이션 문제를 가지는가?

| 모델 | 캘리브레이션 경향 |
| --- | --- |
| 로지스틱 회귀 | 일반적으로 잘 보정됨 |
| 랜덤 포레스트 | 과신 경향 (0과 1 방향으로 몰림) |
| SVM (확률 출력) | 잘 보정되지 않음 |
| 나이브 베이즈 | 극단적 예측 경향 |
| 그래디언트 부스팅 | 보통 잘 보정됨 |
| 신경망 | 과신 경향 (깊은 모델일수록) |

## 신뢰도 다이어그램 이해하기

신뢰도 다이어그램(Reliability Diagram, Calibration Curve)은 예측 확률 구간별 실제 양성 비율을 비교합니다.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

# 데이터 생성
X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=8,
    weights=[0.7, 0.3],
    random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# 세 가지 모델 비교
models = {
    "로지스틱 회귀": LogisticRegression(max_iter=2000, random_state=42),
    "랜덤 포레스트": RandomForestClassifier(n_estimators=100, random_state=42),
    "그래디언트 부스팅": GradientBoostingClassifier(n_estimators=100, random_state=42),
}

print("=== 신뢰도 다이어그램 비교 ===")
print(f"{'모델':>16} {'Brier 점수':>12} {'캘리브레이션 품질'}")
print("-" * 55)

probas = {}
for name, clf in models.items():
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    probas[name] = proba
    brier = brier_score_loss(y_test, proba)

    # 신뢰도 곡선 계산
    frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=10)
    cal_error = np.mean(np.abs(frac_pos - mean_pred))

    quality = "좋음" if cal_error < 0.05 else ("보통" if cal_error < 0.10 else "나쁨")
    print(f"{name:>16} {brier:>12.4f} {quality} (평균 오차: {cal_error:.4f})")
```

```python
# 상세 신뢰도 다이어그램 출력
print("\n=== 랜덤 포레스트 신뢰도 다이어그램 ===")
print("(완벽한 캘리브레이션 = 예측 확률 == 실제 비율)")
print(f"{'예측 확률':>10} {'실제 비율':>10} {'차이':>8} {'해석'}")
print("-" * 55)

rf_proba = probas["랜덤 포레스트"]
frac_pos, mean_pred = calibration_curve(y_test, rf_proba, n_bins=10)
for mp, fp in zip(mean_pred, frac_pos):
    diff = mp - fp
    interp = "과신" if diff > 0.05 else ("과소신" if diff < -0.05 else "적절")
    print(f"{mp:>10.3f} {fp:>10.3f} {diff:>+8.3f} {interp}")
```

예상 출력 (근사값):
```
=== 신뢰도 다이어그램 비교 ===
            모델  Brier 점수 캘리브레이션 품질
-------------------------------------------------------
    로지스틱 회귀       0.1420 좋음 (평균 오차: 0.028)
      랜덤 포레스트       0.1580 나쁨 (평균 오차: 0.112)
  그래디언트 부스팅       0.1460 보통 (평균 오차: 0.065)

=== 랜덤 포레스트 신뢰도 다이어그램 ===
 예측 확률  실제 비율     차이 해석
-------------------------------------------------------
     0.045     0.065   -0.020 적절
     0.150     0.218   -0.068 과소신
     0.280     0.302   -0.022 적절
     0.400     0.388   +0.012 적절
     0.520     0.461   +0.059 과신
     0.640     0.545   +0.095 과신
     0.730     0.632   +0.098 과신
     0.840     0.731   +0.109 과신
     0.930     0.847   +0.083 과신
     0.980     0.925   +0.055 과신
```

## Brier 점수 이해하기

```python
# Brier 점수 상세 설명
print("=== Brier 점수 이해하기 ===")
print()
print("공식: BS = (1/n) * Σ(p_i - y_i)^2")
print("  p_i: 예측 확률, y_i: 실제 레이블 (0 또는 1)")
print()
print("해석:")
print("  BS = 0.0: 완벽한 예측 (확신도 100%에서 항상 맞음)")
print("  BS = 0.25: 무작위 예측 (항상 0.5로 예측)")
print("  BS = 1.0: 최악의 예측 (완전히 반대 방향)")
print()
print("주요 임계점:")
print("  BS < 0.1: 매우 좋은 캘리브레이션")
print("  BS 0.1~0.2: 괜찮은 수준")
print("  BS > 0.25: 무작위보다 나쁨")
print()

# 예시 계산
example_probs = [0.9, 0.8, 0.3, 0.1]
example_true = [1, 1, 0, 0]
bs_example = np.mean([(p-y)**2 for p, y in zip(example_probs, example_true)])
print(f"예시: 예측={example_probs}, 실제={example_true}")
print(f"BS = {bs_example:.4f}")

for name, proba in probas.items():
    bs = brier_score_loss(y_test, proba)
    print(f"{name}: Brier = {bs:.4f}")
```

## 보정 방법 비교

```python
# Platt Scaling vs Isotonic Regression
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Platt 보정 (sigmoid)
rf_platt = CalibratedClassifierCV(
    RandomForestClassifier(n_estimators=100, random_state=42),
    method="sigmoid",
    cv=5
).fit(X_train, y_train)

# Isotonic 보정
rf_isotonic = CalibratedClassifierCV(
    RandomForestClassifier(n_estimators=100, random_state=42),
    method="isotonic",
    cv=5
).fit(X_train, y_train)

# 원래 모델
rf_raw = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)

print("=== 보정 방법 비교 ===")
models_cal = {
    "보정 없음 (원본)": rf_raw,
    "Platt (sigmoid) 보정": rf_platt,
    "Isotonic 보정": rf_isotonic,
}

print(f"{'방법':>22} {'Brier 점수':>12} {'비고'}")
print("-" * 60)
for name, clf in models_cal.items():
    proba_cal = clf.predict_proba(X_test)[:, 1]
    bs = brier_score_loss(y_test, proba_cal)
    frac_pos, mean_pred = calibration_curve(y_test, proba_cal, n_bins=10)
    cal_err = np.mean(np.abs(frac_pos - mean_pred))
    print(f"{name:>22} {bs:>12.4f} 평균 오차: {cal_err:.4f}")

print()
print("보정 방법 선택 가이드:")
print("  Platt (sigmoid): 데이터 적을 때 더 안정적, 단조 함수 가정")
print("  Isotonic: 데이터 많을 때 더 유연, 비선형 왜곡 교정 가능")
print("  주의: 두 방법 모두 별도 데이터에서 검증 필수")
```

## 캘리브레이션 전후 비교

```python
# 보정 전후 신뢰도 다이어그램 비교
print("=== 보정 전후 신뢰도 다이어그램 비교 ===")
print()
print("보정 전 (랜덤 포레스트):")
print(f"{'예측 확률':>10} {'실제 비율':>10} {'차이':>8}")
frac_before, pred_before = calibration_curve(
    y_test, rf_raw.predict_proba(X_test)[:, 1], n_bins=8
)
for mp, fp in zip(pred_before, frac_before):
    print(f"{mp:>10.3f} {fp:>10.3f} {mp-fp:>+8.3f}")

print()
print("보정 후 (Platt scaling):")
print(f"{'예측 확률':>10} {'실제 비율':>10} {'차이':>8}")
frac_after, pred_after = calibration_curve(
    y_test, rf_platt.predict_proba(X_test)[:, 1], n_bins=8
)
for mp, fp in zip(pred_after, frac_after):
    print(f"{mp:>10.3f} {fp:>10.3f} {mp-fp:>+8.3f}")
```

## 캘리브레이션이 중요한 실제 시나리오

### 시나리오 1: 광고 입찰 시스템

클릭 확률에 비례해 입찰가를 결정합니다. 모델이 클릭 확률을 0.15로 예측했는데 실제로는 0.08이라면, 지속적으로 과다 입찰이 발생합니다.

```python
# 광고 입찰 시나리오
def calculate_bid_loss(pred_prob, true_prob, cpc=100):
    """
    pred_prob: 모델 예측 클릭 확률
    true_prob: 실제 클릭 확률
    cpc: 클릭당 가치 (원)
    """
    optimal_bid = true_prob * cpc
    actual_bid = pred_prob * cpc
    overpay = max(0, actual_bid - optimal_bid)
    return overpay

# 10,000건의 입찰에서 과신으로 인한 손실
n_bids = 10000
avg_pred = 0.15   # 모델 예측 평균
avg_true = 0.08   # 실제 평균

total_overpay = calculate_bid_loss(avg_pred, avg_true) * n_bids
print(f"광고 입찰 과신 손실:")
print(f"  모델 예측 클릭률: {avg_pred:.2f}")
print(f"  실제 클릭률: {avg_true:.2f}")
print(f"  건당 과다 입찰: {calculate_bid_loss(avg_pred, avg_true):,.0f}원")
print(f"  10,000건 총 손실: {total_overpay:,.0f}원")
```

### 시나리오 2: 리스크 점수를 확률로 사용

보험, 신용 심사에서 리스크 점수를 직접 기대값 계산에 쓰는 경우입니다.

```python
# 리스크 점수 → 보험료 계산
def calculate_premium(risk_prob, max_claim=1000000):
    """리스크 확률에 비례한 보험료"""
    return risk_prob * max_claim

# 과신 모델 vs 잘 보정된 모델
def scenario_insurance():
    overconfident_preds = [0.85, 0.90, 0.75, 0.80]  # 모델 예측
    actual_risks = [0.60, 0.65, 0.55, 0.62]          # 실제 리스크

    for pred, actual in zip(overconfident_preds, actual_risks):
        premium_set = calculate_premium(pred)
        premium_needed = calculate_premium(actual)
        diff = premium_set - premium_needed
        print(f"예측 {pred:.2f} → 보험료 {premium_set:,.0f}원, "
              f"실제 필요 {premium_needed:,.0f}원, "
              f"과잉징수 {diff:,.0f}원")

print("=== 보험료 과잉징수 시나리오 (캘리브레이션 불량) ===")
scenario_insurance()
```

## Before vs. After: 캘리브레이션 적용 비교

| 항목 | 캘리브레이션 없이 | 캘리브레이션 적용 후 |
| --- | --- | --- |
| 확률 해석 | 불가 (점수로만 취급) | "0.75 = 약 75% 확률"로 해석 가능 |
| 기대값 계산 | 잘못된 결과 | 신뢰할 수 있는 결과 |
| 입찰/보험료 설정 | 체계적 오류 누적 | 현실적 수준으로 설정 |
| AUC와의 관계 | AUC가 높아도 확률 신뢰 못함 | AUC + 캘리브레이션 둘 다 확인 |
| Brier 점수 | 높음 (나쁨) | 낮음 (좋음) |

## 자주 하는 실수

**실수 1 — AUC가 높으면 확률도 믿을 만하다고 가정**

AUC는 순위 성능을 측정하고, 캘리브레이션은 확률의 정확도를 측정합니다. 두 가지는 독립적입니다. AUC 0.85인 랜덤 포레스트가 캘리브레이션은 매우 나쁠 수 있습니다.

**실수 2 — 훈련 데이터에 캘리브레이션 적용**

캘리브레이션도 일종의 학습입니다. 훈련 데이터에 보정하면 훈련 데이터에 과적합됩니다. 반드시 별도 검증 세트를 사용하거나 교차 검증으로 적용해야 합니다 (scikit-learn의 `cv=5` 옵션).

**실수 3 — 보정 후 임계값을 그대로 유지**

보정 전 확률 분포와 보정 후 확률 분포가 달라집니다. 따라서 보정 전에 선택한 임계값을 그대로 쓰면 의도한 재현율/정밀도가 달라집니다. 보정 후에는 임계값을 다시 검토해야 합니다.

**실수 4 — n_bins 설정에 무신경**

신뢰도 다이어그램에서 `n_bins=10`이 기본값이지만, 데이터가 적으면 각 구간에 샘플이 너무 적어 노이즈가 큽니다. 데이터 크기에 따라 5~20 사이에서 적절히 선택해야 합니다.

**실수 5 — 드리프트 후 보정 재확인 안 함**

데이터 분포가 바뀌면 캘리브레이션도 변합니다. 주기적으로 신뢰도 다이어그램과 Brier 점수를 재확인하고, 드리프트가 감지되면 재보정을 고려해야 합니다.

## 운영 체크리스트

- [ ] 신뢰도 다이어그램(`calibration_curve`)을 시각적으로 확인했습니다.
- [ ] Brier 점수를 계산하고 기준치(0.25)와 비교했습니다.
- [ ] 확률값을 의사결정에 직접 사용하는지 확인했습니다 (사용하면 보정 필수).
- [ ] 보정을 별도 검증 데이터나 교차 검증으로 적용했습니다.
- [ ] 보정 후 임계값을 재검토했습니다.
- [ ] 드리프트 모니터링에 Brier 점수를 포함했습니다.

## 처음 질문으로 돌아가기

- **캘리브레이션이란 무엇이고 왜 필요할까요?**
  - 캘리브레이션은 모델의 예측 확률이 실제 빈도와 일치하는 성질입니다. 예측 확률 0.8이 나온 사례들에서 실제로 80%가 양성이어야 잘 보정된 것입니다. 확률값을 기대값 계산, 입찰가 설정, 보험료 산출 등 의사결정에 직접 사용하는 시스템에서는 캘리브레이션이 필수입니다.

- **신뢰도 다이어그램은 어떻게 읽을까요?**
  - x축은 예측 확률 구간, y축은 그 구간에서 실제 양성 비율입니다. 완벽하게 보정된 모델은 x=y 대각선 위에 놓입니다. 대각선 위에 있으면 과소신(understimate), 아래에 있으면 과신(overconfidence)입니다.

- **AUC가 높아도 캘리브레이션이 나쁠 수 있는 이유는 무엇인가요?**
  - AUC는 양성과 음성의 순위 분리만 측정하며, 확률의 절댓값이 얼마나 정확한지는 측정하지 않습니다. 랜덤 포레스트처럼 AUC가 높아도 극단적인 확률(0과 1 방향으로 몰린)을 출력하는 모델은 순위는 맞아도 확률 해석은 할 수 없습니다.

---

## 정리

보정은 모델이 얼마나 잘 맞히는가보다, 모델이 말한 확률을 얼마나 믿을 수 있는가를 다룹니다. 순위 성능(AUC)과 확률 성능(Brier 점수, 신뢰도 다이어그램)은 다른 축이며, 운영에서는 둘 다 중요합니다.

확률값을 의사결정에 직접 사용한다면, AUC만 확인하고 끝내는 습관을 바꿔야 합니다. Brier 점수와 신뢰도 다이어그램으로 확률의 신뢰성을 반드시 검증하고, 필요하면 Platt 보정이나 Isotonic 회귀로 교정해야 합니다.

다음 글에서는 한 번의 분할에 기대지 않고 평가 추정치의 안정성을 보는 교차 검증을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- **Model Evaluation 101 (7/10): 확률 보정 이해하기 (현재 글)**
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn — calibration_curve](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.calibration_curve.html)
- [Wikipedia — Brier score](https://en.wikipedia.org/wiki/Brier_score)
- [Niculescu-Mizil & Caruana 2005](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Calibration, BrierScore, Reliability, scikit-learn
