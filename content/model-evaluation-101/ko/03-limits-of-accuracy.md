---
series: model-evaluation-101
episode: 3
title: "Model Evaluation 101 (3/10): 정확도의 한계"
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
  - Accuracy
  - ImbalancedData
  - BaselineModel
  - scikit-learn
seo_description: 불균형 데이터에서 정확도를 더미 기준선, 소수 클래스 재현율, 균형 정확도와 함께 읽는 방법을 설명합니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (3/10): 정확도의 한계

희귀 질환 진단 모델을 만들었습니다. 검사 대상 1,000명 중 실제 환자는 20명(2%)입니다. 모델을 학습시켰더니 정확도 98.5%가 나왔습니다. 배포를 해야 할까요?

잠깐요. 아무것도 예측하지 않고 "모두 정상"이라고만 해도 정확도는 98%입니다. 이 모델이 실제 환자를 단 한 명이라도 더 발견하고 있는지 정확도만으로는 알 수 없습니다.

이 글은 Model Evaluation 101 시리즈의 3번째 글입니다.

정확도는 계산이 쉽고 설명도 편하지만, 그래서 오히려 너무 일찍 결론을 내리게 만드는 지표입니다. 이번 글에서는 정확도를 맨 앞 숫자가 아니라 **마지막 확인 숫자**로 다룹니다. 특히 높은 정확도가 실제 개선인지 아니면 다수 클래스가 만든 착시인지 판별하는 절차를 단계별로 살펴봅니다.

![Model Evaluation 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/03/03-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 3장 흐름 개요*

> 정확도 역설(Accuracy Paradox) — 불균형 데이터에서 아무것도 예측하지 않는 더미 모델이 실제 모델보다 높은 정확도를 가질 수 있습니다. 정확도가 높다고 모델이 좋은 것이 아니며, 낮다고 나쁜 것도 아닙니다.

## 이 글에서 다룰 문제

- 더미 기준선과 모델 정확도가 비슷할 때 왜 더 깊이 봐야 할까요?
- 혼동 행렬의 어느 칸을 봐야 진짜 성능을 알 수 있을까요?
- 소수 클래스 재현율과 균형 정확도는 언제 정확도를 대체해야 할까요?
- 불균형 데이터에서 가장 흔한 평가 실수는 무엇일까요?
- 정확도를 보고서 첫 줄에 올려도 되는 조건은 무엇인가요?

## 정확도 역설(Accuracy Paradox)이란

정확도 역설은 클래스 불균형이 심한 데이터에서 발생합니다. 가장 단순한 예를 봅시다.

**상황:** 1,000건의 데이터, 그 중 양성(소수 클래스) 20건, 음성(다수 클래스) 980건

**더미 모델 전략:** 모든 예측을 "음성"으로 고정

| 예측 \ 실제 | 음성 (980건) | 양성 (20건) |
| --- | ---: | ---: |
| 음성으로 예측 | 980 (TN) | 20 (FN) |
| 양성으로 예측 | 0 (FP) | 0 (TP) |

정확도 = (980 + 0) / 1000 = **98%**

이 "모델"은 양성을 단 한 건도 맞히지 못했지만 정확도는 98%입니다. 만약 실제 모델이 95% 정확도를 기록한다면, 이 더미 모델보다 낮은 정확도를 가진 셈이지만 실제로는 훨씬 더 유용한 모델입니다.

## 올바른 판단 순서: 5단계 체크

정확도를 해석할 때는 이 순서를 지키는 것이 안전합니다.

1. **베이스레이트 확인**: 양성 비율이 얼마나 낮은지 먼저 봅니다.
2. **더미 기준선 비교**: 아무것도 학습하지 않은 모델이 이미 몇 점인지 확인합니다.
3. **소수 클래스 재현율 확인**: 정말 중요한 양성을 얼마나 놓치는지 봅니다.
4. **균형 정확도 추가**: 다수 클래스와 소수 클래스를 공평하게 평균 냅니다.
5. **정확도 보고 여부 결정**: 위 네 단계를 통과한 뒤에만 정확도를 요약 숫자로 남깁니다.

## 전체 진단 코드

```python
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    recall_score,
    precision_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
import numpy as np

# 불균형 데이터 생성 (96:4 비율)
X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=5,
    n_redundant=2,
    weights=[0.96, 0.04],
    class_sep=1.1,
    flip_y=0.015,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# 더미 모델과 실제 모델
dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)
dummy_pred = dummy.predict(X_test)

# 핵심 지표 비교
print("=== 1단계: 베이스레이트 확인 ===")
print(f"양성 비율 (베이스레이트): {y.mean():.4f} ({y.mean()*100:.2f}%)")
print()

print("=== 2단계: 더미 기준선 비교 ===")
print(f"더미 모델 정확도: {accuracy_score(y_test, dummy_pred):.4f}")
print(f"실제 모델 정확도: {accuracy_score(y_test, pred):.4f}")
print(f"정확도 이득: +{accuracy_score(y_test, pred) - accuracy_score(y_test, dummy_pred):.4f}")
print()

print("=== 3단계: 소수 클래스 재현율 ===")
print(f"더미 모델 재현율 (양성): {recall_score(y_test, dummy_pred):.4f}")
print(f"실제 모델 재현율 (양성): {recall_score(y_test, pred):.4f}")
print()

print("=== 4단계: 균형 정확도 ===")
print(f"더미 모델 균형 정확도: {balanced_accuracy_score(y_test, dummy_pred):.4f}")
print(f"실제 모델 균형 정확도: {balanced_accuracy_score(y_test, pred):.4f}")
print()

print("=== 혼동 행렬 ===")
cm = confusion_matrix(y_test, pred)
tn, fp, fn, tp = cm.ravel()
print(cm)
print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")
print(f"실제 양성 {tp+fn}건 중 탐지: {tp}건, 놓침: {fn}건")
```

예상 출력:
```
=== 1단계: 베이스레이트 확인 ===
양성 비율 (베이스레이트): 0.0468 (4.68%)

=== 2단계: 더미 기준선 비교 ===
더미 모델 정확도: 0.9536
실제 모델 정확도: 0.9608
정확도 이득: +0.0072

=== 3단계: 소수 클래스 재현율 ===
더미 모델 재현율 (양성): 0.0000
실제 모델 재현율 (양성): 0.1897

=== 4단계: 균형 정확도 ===
더미 모델 균형 정확도: 0.5000
실제 모델 균형 정확도: 0.5940

=== 혼동 행렬 ===
[[1190    2]
 [  47   11]]
TN=1190, FP=2, FN=47, TP=11
실제 양성 58건 중 탐지: 11건, 놓침: 47건
```

## 혼동 행렬 완전 해석

혼동 행렬 `[[1190, 2], [47, 11]]`을 읽어봅시다.

```
                    예측: 음성    예측: 양성
실제: 음성          1190 (TN)      2 (FP)
실제: 양성           47 (FN)      11 (TP)
```

- **TN = 1190**: 음성 1,192건 중 1,190건을 올바르게 음성으로 분류 (매우 좋음)
- **FP = 2**: 음성 2건을 양성으로 잘못 분류 (오탐, 거의 없음)
- **FN = 47**: 양성 58건 중 47건을 음성으로 잘못 분류 (매우 심각!)
- **TP = 11**: 양성 11건을 올바르게 양성으로 분류

**핵심 해석:** 이 모델은 정상(음성)을 잡는 데는 뛰어나지만, 정작 탐지해야 할 양성을 81%나 놓치고 있습니다. 이런 모델을 "정확도 96%"라고 보고하면 실제 상황을 완전히 왜곡하게 됩니다.

## 단계별 깊은 분석

### 1단계 — 베이스레이트가 의미하는 것

```python
print(f"베이스레이트 {y.mean()*100:.2f}%의 의미:")
print(f"  → 전체 데이터에서 양성이 {y.mean()*100:.2f}%밖에 안 됨")
print(f"  → '모두 음성'으로 예측해도 {(1-y.mean())*100:.2f}%는 맞음")
print(f"  → 정확도 기준선이 자동으로 {(1-y.mean())*100:.2f}%")
print()
print("결론: 베이스레이트가 낮을수록 정확도는 왜곡이 심해짐")
```

베이스레이트 4.68%는 아무것도 예측하지 않아도 95.32%가 정확히 맞는다는 뜻입니다. 이 상황에서 96%라는 숫자는 그다지 의미 있는 개선이 아닙니다.

### 2단계 — 더미 기준선과의 차이가 실제 가치

```python
# 정확도 이득 계산
acc_model = accuracy_score(y_test, pred)
acc_dummy = accuracy_score(y_test, dummy_pred)
improvement = acc_model - acc_dummy

print(f"모델 정확도: {acc_model:.4f}")
print(f"더미 정확도: {acc_dummy:.4f}")
print(f"실제 개선분: +{improvement:.4f} ({improvement*100:.2f}%p)")
print()
if improvement < 0.02:
    print("경고: 정확도 개선이 2%p 미만입니다.")
    print("정확도는 이 문제의 적절한 지표가 아닐 수 있습니다.")
    print("소수 클래스 재현율과 균형 정확도를 확인하세요.")
```

정확도 이득이 0.72%p라는 것은 모델이 더미보다 단지 조금만 낫다는 의미입니다. 이때는 반드시 소수 클래스 지표를 확인해야 합니다.

### 3단계 — 소수 클래스 재현율이 핵심

```python
minority_recall = recall_score(y_test, pred)
print(f"소수 클래스 재현율: {minority_recall:.4f}")
print(f"  → 실제 양성 {tp+fn}건 중 {tp}건만 탐지")
print(f"  → {fn}건을 놓침 ({fn/(tp+fn)*100:.1f}%)")
print()

# 임계값을 낮추면 재현율이 올라감
proba = model.predict_proba(X_test)[:, 1]
print("임계값 조정으로 재현율 개선:")
print(f"{'임계값':>6} {'재현율':>8} {'정밀도':>8} {'정확도':>8}")
for t in [0.1, 0.2, 0.3, 0.5]:
    pred_t = (proba >= t).astype(int)
    print(
        f"{t:>6.1f} "
        f"{recall_score(y_test, pred_t):>8.4f} "
        f"{precision_score(y_test, pred_t, zero_division=0):>8.4f} "
        f"{accuracy_score(y_test, pred_t):>8.4f}"
    )
```

재현율 0.19는 실제 양성의 19%만 잡는다는 뜻입니다. 희귀 질환 진단이나 사기 탐지에서 81%를 놓치는 모델은 실제로 쓸 수 없습니다.

### 4단계 — 균형 정확도가 공평한 평가

```python
from sklearn.metrics import balanced_accuracy_score

bal_acc = balanced_accuracy_score(y_test, pred)
print(f"균형 정확도: {bal_acc:.4f}")
print(f"  = (음성 재현율 + 양성 재현율) / 2")

# 계산 확인
tn_r = tn / (tn + fp)  # 음성 재현율 (특이도)
tp_r = tp / (tp + fn)  # 양성 재현율 (민감도)
print(f"  = ({tn_r:.4f} + {tp_r:.4f}) / 2 = {(tn_r + tp_r) / 2:.4f}")
print()
print(f"균형 정확도 {bal_acc:.4f} vs 일반 정확도 {accuracy_score(y_test, pred):.4f}")
print(f"차이: {accuracy_score(y_test, pred) - bal_acc:.4f}")
print("→ 이 차이가 클수록 정확도가 다수 클래스에 의해 부풀려진 것")
```

균형 정확도 0.59는 정확도 0.96과 큰 차이를 보입니다. 이 차이가 불균형 데이터에서 정확도가 얼마나 왜곡될 수 있는지를 보여줍니다.

### 5단계 — 정확도를 보고서에 써도 될지 최종 판단

```python
def should_use_accuracy(y_test, pred, threshold_ba=0.8, threshold_minority_recall=0.5):
    """
    정확도를 주요 지표로 사용해도 될지 판단하는 함수
    """
    acc = accuracy_score(y_test, pred)
    bal_acc = balanced_accuracy_score(y_test, pred)
    minority_rec = recall_score(y_test, pred)

    print("=== 정확도 사용 적합성 판단 ===")
    print(f"정확도: {acc:.4f}")
    print(f"균형 정확도: {bal_acc:.4f}")
    print(f"소수 클래스 재현율: {minority_rec:.4f}")
    print()

    issues = []
    if bal_acc < threshold_ba:
        issues.append(f"균형 정확도 {bal_acc:.2f}가 {threshold_ba} 미만")
    if minority_rec < threshold_minority_recall:
        issues.append(f"소수 클래스 재현율 {minority_rec:.2f}가 {threshold_minority_recall} 미만")

    if issues:
        print("경고: 정확도를 주요 지표로 사용하기 부적합")
        for issue in issues:
            print(f"  - {issue}")
        print("권장: 재현율, 정밀도, F1, 균형 정확도를 함께 보고")
    else:
        print("정확도를 주요 지표로 사용 가능")

    return len(issues) == 0

should_use_accuracy(y_test, pred)
```

## Before vs. After: 불균형 데이터 평가 비교

| 항목 | 나이브 접근 | 올바른 접근 |
| --- | --- | --- |
| 첫 번째 확인 | 정확도 (96%) | 베이스레이트 (4.68%) |
| 기준선 | 없음 | 더미 모델 (95.36%) |
| 핵심 지표 | 정확도 | 소수 클래스 재현율 (18.97%) |
| 공평한 요약 | 없음 | 균형 정확도 (59.40%) |
| 의사결정 | "96%니까 좋다" | "양성 81% 놓침, 개선 필요" |
| 보고서 첫 줄 | "정확도 96%" | "소수 재현율 19%, 균형 정확도 59%" |

## 자주 하는 실수

**실수 1 — 정확도 하나만 보고 배포 결정**

가장 흔하고 위험한 실수입니다. 불균형 비율이 90:10만 넘어도 정확도는 왜곡되기 시작합니다. 항상 베이스레이트를 확인하고 더미 기준선과 비교해야 합니다.

**실수 2 — 균형 정확도와 일반 정확도를 혼용**

`balanced_accuracy_score`는 클래스 비율과 무관하게 각 클래스를 동등하게 취급합니다. 불균형 데이터에서는 항상 균형 정확도를 추가로 보고해야 합니다.

**실수 3 — 소수 클래스 재현율을 확인하지 않음**

정확도와 F1 점수가 낮지 않아도 소수 클래스 재현율은 0에 가까울 수 있습니다. 불균형 데이터에서는 반드시 `recall_score(y_test, pred)` (양성 클래스 재현율)를 별도로 확인해야 합니다.

**실수 4 — 데이터 증강/언더샘플링 후 정확도로만 평가**

SMOTE, 오버샘플링, 클래스 가중치 조정 후에도 정확도로만 평가하면 의미가 없습니다. 이런 기법의 효과는 균형 정확도와 소수 클래스 재현율로 확인해야 합니다.

**실수 5 — classification_report의 'accuracy' 줄만 보기**

`classification_report`의 마지막 줄에 있는 accuracy는 일반 정확도입니다. 위에 있는 per-class precision, recall, f1-score가 훨씬 더 중요한 정보를 담고 있습니다.

```python
# classification_report를 올바르게 읽는 방법
print("=== classification_report 올바르게 읽기 ===")
print(classification_report(y_test, pred, digits=4))
print()
print("→ 클래스 '1' (소수)의 recall이 가장 중요한 숫자")
print("→ 맨 아래 accuracy는 불균형 데이터에서 거의 의미 없음")
```

## 불균형 데이터에서의 지표 비교 표

| 지표 | 더미 모델 | 실제 모델 | 무엇을 말하는가 |
| --- | ---: | ---: | --- |
| 정확도 | 0.9536 | 0.9608 | 다수 클래스 성능에 지배됨 |
| 균형 정확도 | 0.5000 | 0.5940 | 클래스 간 공평한 비교 |
| 양성 재현율 | 0.0000 | 0.1897 | 실제 탐지 능력 |
| 양성 정밀도 | - | 0.8462 | 탐지 신뢰도 |
| F1 (양성) | 0.0000 | 0.3103 | 재현율과 정밀도의 균형 |

정확도만 보면 두 모델의 차이가 0.0072에 불과합니다. 그러나 균형 정확도로 보면 0.0940의 차이가 있고, 재현율은 0에서 0.19로 개선됩니다. 어떤 숫자를 볼지에 따라 완전히 다른 결론이 나옵니다.

## 운영 체크리스트

- [ ] 데이터의 베이스레이트(클래스 비율)를 먼저 확인했습니다.
- [ ] 더미 모델(`most_frequent` 전략)과의 정확도를 비교했습니다.
- [ ] 소수 클래스 재현율(`recall_score`)을 별도로 확인했습니다.
- [ ] 균형 정확도(`balanced_accuracy_score`)를 계산했습니다.
- [ ] `classification_report`에서 per-class 지표를 확인했습니다.
- [ ] 정확도를 주요 지표로 사용할지 위 결과를 바탕으로 결정했습니다.

## 처음 질문으로 돌아가기

- **더미 기준선과 모델 정확도가 비슷할 때 왜 더 깊이 봐야 할까요?**
  - 정확도가 비슷하다는 것은 모델이 더미 대비 실질적인 개선을 이루지 못했을 가능성을 시사합니다. 이 경우 소수 클래스 재현율과 균형 정확도를 확인하면 대부분 더미 모델과의 본질적인 차이가 드러납니다.

- **혼동 행렬의 어느 칸을 봐야 진짜 성능을 알 수 있을까요?**
  - 불균형 데이터에서는 FN(위음성) 칸이 핵심입니다. FN은 실제 양성을 음성으로 잘못 분류한 건수입니다. 이 숫자가 크면 소수 클래스 탐지에 실패하고 있는 것으로, 정확도는 높아도 실제 비즈니스 가치는 낮습니다.

- **소수 클래스 재현율과 균형 정확도는 언제 정확도를 대체해야 할까요?**
  - 클래스 비율이 80:20을 넘어가는 순간부터 정확도의 신뢰도가 떨어집니다. 90:10 이상이면 균형 정확도와 소수 클래스 재현율을 주요 지표로 써야 합니다. 특히 소수 클래스를 탐지하는 것이 비즈니스 목표인 경우에는 정확도가 아닌 재현율이 우선입니다.

---

## 정리

정확도는 쓸모없는 지표가 아니라 순서가 중요한 지표입니다. 베이스레이트와 더미 기준선, 소수 클래스 재현율, 균형 정확도를 거친 뒤에야 비로소 읽을 수 있습니다.

실무 보고서 작성 시 이 문장 구조를 참고하세요:

> "베이스레이트 4.68% 문제에서 모델 정확도는 96.08%로 더미 기준선 95.36%보다 0.72%포인트 높았습니다. 그러나 소수 클래스 재현율은 18.97%, 균형 정확도는 59.40%에 그쳤으므로, 이 모델은 정확도 기준으로는 개선되었으나 양성 탐지 능력은 아직 부족한 상태로 판단합니다."

다음 글에서는 이 흐름을 이어받아, 임계값을 움직일 때 정밀도와 재현율이 어떻게 트레이드오프를 형성하고, 그것이 어떤 운영 결정으로 연결되는지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- **Model Evaluation 101 (3/10): 정확도의 한계 (현재 글)**
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- [scikit-learn — accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)
- [scikit-learn — balanced_accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html)
- [Wikipedia — Accuracy paradox](https://en.wikipedia.org/wiki/Accuracy_paradox)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Accuracy, ImbalancedData, BaselineModel, scikit-learn
