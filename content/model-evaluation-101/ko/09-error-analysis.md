---
series: model-evaluation-101
episode: 9
title: "Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기"
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
  - ErrorAnalysis
  - Slicing
  - Debugging
  - scikit-learn
seo_description: 평균 점수에 가려진 모델의 취약점을 파악하기 위한 오류 분석 기법을 소개하고, 실패 패턴을 찾아 모델을 개선합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기

고객 이탈 예측 모델의 전체 F1이 0.82로 꽤 좋습니다. 배포 후 3개월이 지났는데 "모델이 신규 사용자 이탈을 전혀 못 잡는다"는 피드백이 들어왔습니다. 전체 F1은 그대로였지만, 가입 30일 미만 신규 사용자 세그먼트의 F1은 0.41이었습니다. 전체 평균이 약점을 숨기고 있었습니다.

이 글은 Model Evaluation 101 시리즈의 9번째 글입니다.

전체 점수는 모델이 얼마나 잘하는지 대략 알려 줍니다. 하지만 모델을 실제로 고치려면 그 숫자만으로는 부족합니다. 정확도 92%라는 결과는 그럴듯하지만, 어디서 틀렸는지, 어떤 사용자 집단에서 약한지, false positive와 false negative 중 무엇이 더 큰지까지는 말해 주지 못합니다.

개선 작업의 출발점은 종종 더 좋은 지표를 찾는 일이 아니라, 틀린 예측을 더 잘 분해하는 일입니다. 오류 분석은 평균 점수 뒤에 숨어 있는 패턴을 꺼내서 다음 실험의 우선순위를 정하게 도와줍니다.

![Model Evaluation 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/09/09-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 9장 흐름 개요*

> 개선은 더 높은 평균이 아니라 분해에서 시작합니다 — 오류 분석은 하나의 집계 점수를 슬라이스·신뢰도·오류 유형으로 쪼개, 다음 실험이 막연한 기대가 아닌 구체적인 표적을 갖게 해 줍니다.

## 이 글에서 다룰 문제

- 전체 성능이 좋아도 특정 세그먼트에서 실패하는 이유는 무엇일까요?
- 슬라이스 분석으로 어떤 약점을 찾을 수 있을까요?
- FP(거짓 양성)와 FN(거짓 음성)을 나눠 봐야 하는 이유는 무엇일까요?
- 어려운 샘플(hard example)은 어떻게 찾고 어떻게 활용할까요?
- 오류 분석 결과를 어떻게 다음 개선 작업으로 연결할까요?

## 오류 분석 워크플로우

오류 분석은 이 순서로 진행합니다.

```
1. 혼동 행렬 드릴다운
   → FP와 FN의 절대 숫자와 비율 파악

2. 슬라이스 분석
   → 피처값, 사용자 세그먼트, 시간대별 F1/재현율
   → 가장 약한 세그먼트 발견

3. 신뢰도 구간별 오류율
   → 모델이 확신한 곳에서도 틀리는지 확인
   → 보정 문제 vs. 피처 부족 구분

4. 어려운 샘플 분석
   → 반복 오류 샘플 수동 검토
   → 라벨 노이즈, 피처 부족, 구조적 문제 파악

5. 오류 패턴 분류 및 처방
   → 각 오류 유형별 개선 방향 결정
```

## 전체 오류 분석 코드

```python
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report,
)

# 데이터 생성 (실제 시나리오 모사: 일부 피처로 세그먼트 생성)
np.random.seed(42)
X, y = make_classification(
    n_samples=4000,
    n_features=12,
    n_informative=6,
    n_redundant=2,
    weights=[0.7, 0.3],
    random_state=42,
)

# 메타데이터 추가 (피처 0을 세그먼트 기준으로 사용)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=2000, random_state=42).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]
pred = (proba >= 0.5).astype(int)

# 1단계: 전체 성능 요약
print("=== 1단계: 전체 성능 요약 ===")
cm = confusion_matrix(y_test, pred)
tn, fp, fn, tp = cm.ravel()
print(f"혼동 행렬:\n{cm}")
print(f"  TN={tn}, FP={fp}, FN={fn}, TP={tp}")
print(f"  전체 F1 (macro): {f1_score(y_test, pred, average='macro'):.4f}")
print(f"  양성 재현율: {recall_score(y_test, pred):.4f}")
print(f"  양성 정밀도: {precision_score(y_test, pred):.4f}")
print()

# 오류 마스크
fp_mask = (pred == 1) & (y_test == 0)
fn_mask = (pred == 0) & (y_test == 1)
tp_mask = (pred == 1) & (y_test == 1)
tn_mask = (pred == 0) & (y_test == 0)

print(f"  FP {fp}건: 정상을 양성으로 잘못 분류 (거짓 경보)")
print(f"  FN {fn}건: 양성을 정상으로 잘못 분류 (놓침)")
print(f"  → FN이 더 비쌀 경우: 임계값 낮추기 고려")
print(f"  → FP가 더 비쌀 경우: 임계값 높이기 고려")
```

## 슬라이스 분석: 약한 세그먼트 찾기

```python
print("=== 2단계: 슬라이스 분석 ===")
print()

# 피처 0를 기준으로 세그먼트 분할
segments = {
    "피처0 > 0 (그룹 A)": X_test[:, 0] > 0,
    "피처0 <= 0 (그룹 B)": X_test[:, 0] <= 0,
    "피처1 > 1 (고신호)": X_test[:, 1] > 1,
    "피처1 <= 1 (저신호)": X_test[:, 1] <= 1,
    "예측 확률 > 0.7 (고확신)": proba > 0.7,
    "예측 확률 <= 0.3 (저확신)": proba <= 0.3,
}

print(f"{'세그먼트':>22} {'샘플수':>8} {'F1':>8} {'정밀도':>8} {'재현율':>8} {'FP':>6} {'FN':>6}")
print("-" * 75)

for seg_name, seg_mask in segments.items():
    if seg_mask.sum() < 10:
        continue
    y_seg = y_test[seg_mask]
    pred_seg = pred[seg_mask]

    if len(np.unique(y_seg)) < 2:
        continue

    seg_cm = confusion_matrix(y_seg, pred_seg)
    seg_tn, seg_fp, seg_fn, seg_tp = seg_cm.ravel()

    f1 = f1_score(y_seg, pred_seg, average="macro", zero_division=0)
    prec = precision_score(y_seg, pred_seg, zero_division=0)
    rec = recall_score(y_seg, pred_seg, zero_division=0)

    flag = " ← 약점!" if f1 < 0.70 else ""
    print(f"{seg_name:>22} {seg_mask.sum():>8d} {f1:>8.3f} {prec:>8.3f} {rec:>8.3f} "
          f"{seg_fp:>6d} {seg_fn:>6d}{flag}")
```

```python
# 수치형 피처 구간별 오류율
print()
print("=== 피처 0 구간별 성능 ===")
print(f"{'구간':>16} {'샘플수':>8} {'양성 비율':>10} {'F1':>8} {'재현율':>8}")
print("-" * 55)

feat0 = X_test[:, 0]
bins = np.percentile(feat0, [0, 25, 50, 75, 100])
for i in range(len(bins) - 1):
    lo, hi = bins[i], bins[i+1]
    mask = (feat0 >= lo) & (feat0 < hi)
    if i == len(bins) - 2:
        mask = (feat0 >= lo) & (feat0 <= hi)

    if mask.sum() < 10 or len(np.unique(y_test[mask])) < 2:
        continue

    y_b = y_test[mask]
    pred_b = pred[mask]
    f1_b = f1_score(y_b, pred_b, average="macro", zero_division=0)
    rec_b = recall_score(y_b, pred_b, zero_division=0)
    pos_rate = y_b.mean()

    flag = " ← 약점!" if f1_b < 0.70 else ""
    print(f"{lo:>7.2f}~{hi:>6.2f} {mask.sum():>8d} {pos_rate:>10.3f} "
          f"{f1_b:>8.3f} {rec_b:>8.3f}{flag}")
```

## 신뢰도 구간별 오류율 분석

```python
print("=== 3단계: 신뢰도 구간별 오류율 ===")
print()
print("(모델이 확신한 구간에서도 자주 틀리면 보정/피처 문제 의심)")
print()
print(f"{'예측 확률 구간':>18} {'샘플수':>8} {'오류율':>8} {'신호'}")
print("-" * 50)

bins = np.linspace(0, 1, 11)
for lo, hi in zip(bins[:-1], bins[1:]):
    mask = (proba >= lo) & (proba < hi)
    if mask.sum() == 0:
        continue

    err_rate = (pred[mask] != y_test[mask]).mean()

    # 예상 오류율 (완벽 보정이라면 0.5 주변이 최고, 극단은 최저여야 함)
    expected_high_err = abs(lo + (hi - lo)/2 - 0.5)  # 0.5에서 멀수록 낮아야 함

    flag = ""
    if lo >= 0.7 and err_rate > 0.15:
        flag = " ← 고확신 오류! (보정 문제 의심)"
    elif lo >= 0.4 and lo < 0.6 and err_rate < 0.3:
        flag = " ← 애매 구간 양호"

    print(f"{lo:.1f}~{hi:.1f} {'':>8} {mask.sum():>8d} {err_rate:>8.3f}{flag}")
```

## 어려운 샘플 분석

```python
print("=== 4단계: 어려운 샘플 (Hard Examples) ===")
print()

# 방법 1: 경계선 근처 샘플 (0.5에 가장 가까운 예측)
ambiguity = np.abs(proba - 0.5)
hardest_idx = np.argsort(ambiguity)[:20]

print("경계선 근처 샘플 (가장 애매한 20개):")
print(f"{'인덱스':>8} {'예측 확률':>10} {'예측':>6} {'실제':>6} {'오류 유형'}")
print("-" * 50)
for idx in hardest_idx[:10]:
    pred_label = pred[idx]
    true_label = y_test[idx]
    prob = proba[idx]

    if pred_label == true_label:
        error_type = "정확"
    elif pred_label == 1 and true_label == 0:
        error_type = "FP (거짓 경보)"
    else:
        error_type = "FN (놓침)"

    print(f"{idx:>8d} {prob:>10.4f} {pred_label:>6d} {true_label:>6d} {error_type}")

print()

# 방법 2: 고확신 오류 (확신하지만 틀린 것)
high_conf_errors = (proba > 0.8) & (pred != y_test)
print(f"고확신 오류 (확률 > 0.8에서 틀린 샘플): {high_conf_errors.sum()}건")
if high_conf_errors.sum() > 0:
    print(f"  → 라벨 노이즈 또는 피처 부족 의심")
    print(f"  → 이 샘플들을 수동 검토 우선순위로 올림")

low_conf_correct = (proba < 0.3) & (pred == y_test) & (y_test == 0)
print(f"저확신 정확 (확률 < 0.3에서 맞은 음성): {low_conf_correct.sum()}건")
```

## 오류 패턴 분류 및 처방

```python
print("=== 5단계: 오류 패턴 분류 및 처방 ===")
print()

# FP 분석
fp_samples = X_test[fp_mask]
fp_proba = proba[fp_mask]

print(f"FP 분석 ({fp}건 — 정상을 양성으로 잘못 분류):")
print(f"  평균 예측 확률: {fp_proba.mean():.3f}")
print(f"  피처 0 평균값: {fp_samples[:, 0].mean():.3f} (전체: {X_test[:, 0].mean():.3f})")
print(f"  처방: 임계값 올리기 또는 FP 패턴 추가 피처 개발")
print()

# FN 분석
fn_samples = X_test[fn_mask]
fn_proba = proba[fn_mask]

print(f"FN 분석 ({fn}건 — 양성을 정상으로 잘못 분류):")
print(f"  평균 예측 확률: {fn_proba.mean():.3f}")
print(f"  피처 0 평균값: {fn_samples[:, 0].mean():.3f} (전체: {X_test[:, 0].mean():.3f})")
print(f"  처방: 임계값 낮추기 또는 양성 학습 데이터 추가")
print()

# 오류 비율 시각화 (텍스트)
print("오류 유형별 비율 분포:")
total = len(y_test)
print(f"  TN: {tn_mask.sum():5d}건 ({tn_mask.sum()/total*100:5.1f}%) ─ 정확")
print(f"  TP: {tp_mask.sum():5d}건 ({tp_mask.sum()/total*100:5.1f}%) ─ 정확")
print(f"  FP: {fp_mask.sum():5d}건 ({fp_mask.sum()/total*100:5.1f}%) ─ 거짓 경보")
print(f"  FN: {fn_mask.sum():5d}건 ({fn_mask.sum()/total*100:5.1f}%) ─ 놓침")
```

## 오류 유형별 처방 가이드

오류 분석 결과에 따라 다른 처방이 필요합니다.

```python
def diagnose_and_prescribe(fp_count, fn_count, fp_proba_mean, fn_proba_mean,
                           high_conf_error_count):
    """오류 패턴을 진단하고 처방을 제안합니다."""
    print("=== 오류 진단 및 처방 ===")
    print()

    total_errors = fp_count + fn_count
    fp_ratio = fp_count / total_errors if total_errors > 0 else 0
    fn_ratio = fn_count / total_errors if total_errors > 0 else 0

    print(f"FP/FN 비율: {fp_ratio:.2f} / {fn_ratio:.2f}")
    print()

    if fn_ratio > 0.7:
        print("진단: 놓침(FN)이 주요 문제")
        print("처방:")
        print("  1. 임계값을 낮추어 재현율 향상 (현재 대비 -0.10~0.15)")
        print("  2. 양성 클래스 학습 데이터 추가 수집")
        print("  3. 클래스 가중치 (class_weight='balanced') 적용")
    elif fp_ratio > 0.7:
        print("진단: 거짓 경보(FP)가 주요 문제")
        print("처방:")
        print("  1. 임계값을 높여 정밀도 향상")
        print("  2. FP 패턴을 구분하는 추가 피처 개발")
        print("  3. 규칙 기반 후처리로 명확한 FP 걸러내기")
    else:
        print("진단: FP와 FN이 균형")
        print("처방: F1 기준 임계값 최적화 또는 피처 품질 개선")

    print()
    if high_conf_error_count > total_errors * 0.1:
        print(f"추가 진단: 고확신 오류가 {high_conf_error_count}건으로 많음")
        print("처방:")
        print("  - 라벨 품질 점검 (노이즈 라벨 재검토)")
        print("  - 캘리브레이션 확인 (7장 참조)")
        print("  - 해당 샘플의 피처 분포 분석")

high_conf_err = ((proba > 0.8) & (pred != y_test)).sum()
diagnose_and_prescribe(fp, fn, fp_proba.mean(), fn_proba.mean(), high_conf_err)
```

## 오류 분석을 개선 우선순위로 변환

```python
print("=== 오류 분석 → 개선 우선순위 ===")
print()
print("발견된 문제와 예상 임팩트:")
print()

issues = [
    ("피처 0 <= 0 세그먼트 F1 낮음", "높음", "해당 세그먼트 데이터 추가 수집"),
    ("FN 비율 높음 (재현율 낮음)", "높음", "임계값 0.35로 낮추기 검토"),
    ("고확신 오류 존재", "중간", "라벨 품질 재검토"),
    ("예측 확률 0.4~0.6 구간 오류율", "낮음", "더 많은 피처 탐색"),
]

print(f"{'순위':>4} {'문제':>30} {'임팩트':>8} {'처방'}")
print("-" * 80)
for i, (issue, impact, prescription) in enumerate(issues, 1):
    print(f"{i:>4}. {issue:>30} {impact:>8} {prescription}")

print()
print("다음 실험 계획:")
print("  실험 1: 임계값 0.35 테스트 → 검증 세트에서 재현율 확인")
print("  실험 2: 피처 0 <= 0 그룹 데이터 2배 추가 → 재학습")
print("  실험 3: 고확신 오류 샘플 50건 수동 라벨 재검토")
```

## Before vs. After: 오류 분석 전후 비교

| 항목 | 분석 전 | 분석 후 |
| --- | --- | --- |
| 성능 파악 | "F1=0.82" | "그룹 A: F1=0.85, 그룹 B: F1=0.61" |
| 문제 이해 | "모델 개선 필요" | "FN 비율 높음, 특정 세그먼트 약함" |
| 개선 방향 | 막연한 모델 교체 | 임계값 조정 + 특정 그룹 데이터 추가 |
| 실험 계획 | 랜덤 시도 | 가장 임팩트 큰 문제 순서대로 처방 |

## 자주 하는 실수

**실수 1 — 전체 점수만 보고 배포 결정**

전체 F1이 0.85여도 특정 사용자 그룹에서 F1이 0.40일 수 있습니다. 배포 전에 최소한 주요 세그먼트(사용자 유형, 지역, 시간대 등)별 성능을 확인해야 합니다.

**실수 2 — FP와 FN을 합산해서 "오류율"로만 보기**

FP와 FN은 서로 다른 비즈니스 비용을 가집니다. 합산해서 단일 오류율로 보면 비용 구조를 잃어버립니다. 항상 분리해서 봐야 합니다.

**실수 3 — 슬라이스를 결과 후에 임의로 정하기**

분석 후에 좋은 결과가 나오는 세그먼트를 골라 보고하면 체리피킹입니다. 중요한 세그먼트는 분석 전에 미리 정의해야 합니다. "신규 사용자 vs. 기존 사용자", "모바일 vs. 웹" 같은 기준을 사전에 정합니다.

**실수 4 — 모든 오류가 모델 문제라고 가정**

어려운 샘플(hard examples)을 수동으로 검토해 보면 종종 라벨 자체가 잘못되어 있거나, 주관적인 경계선에 있는 경우가 많습니다. 오류 분석은 모델과 데이터의 책임을 나누는 작업이기도 합니다.

**실수 5 — 오류 분석 없이 더 복잡한 모델로 교체**

약점을 이해하지 못한 채 복잡한 모델로 교체하면 같은 약점이 반복될 가능성이 높습니다. 오류 분석 → 처방 → 실험의 순서를 지켜야 효율적인 개선이 가능합니다.

## 운영 체크리스트

- [ ] 전체 혼동 행렬을 확인하고 FP/FN 비율을 파악했습니다.
- [ ] 최소 3개 이상의 중요 세그먼트에서 성능을 확인했습니다.
- [ ] 신뢰도 구간별 오류율을 확인했습니다.
- [ ] 어려운 샘플(hard examples) 20건 이상을 수동 검토했습니다.
- [ ] 오류 패턴을 진단하고 처방을 결정했습니다.
- [ ] 다음 실험 계획을 오류 분석 결과에 기반해 수립했습니다.

## 처음 질문으로 돌아가기

- **전체 성능이 좋아도 특정 세그먼트에서 실패하는 이유는 무엇일까요?**
  - 전체 평균 점수는 다수 세그먼트의 성능에 지배됩니다. 특정 소수 세그먼트가 매우 나쁘더라도 전체 평균을 크게 낮추지 않을 수 있습니다. 예를 들어 신규 사용자가 전체의 5%라면, 그 세그먼트에서 F1=0.4여도 전체 F1에 미치는 영향은 제한적입니다.

- **FP와 FN을 나눠 봐야 하는 이유는 무엇일까요?**
  - FP(거짓 경보)와 FN(놓침)은 서로 다른 비즈니스 비용을 지닙니다. 합산 오류율로 보면 비용 구조 정보가 사라집니다. 의료 진단에서 FN(환자 놓침)이 FP(건강한 사람 재검)보다 훨씬 비싸므로, 두 가지를 항상 분리해서 봐야 처방이 맞는 방향으로 나옵니다.

- **어려운 샘플은 어떻게 찾고 어떻게 활용할까요?**
  - 어려운 샘플은 두 가지 방법으로 찾습니다. 첫째, 예측 확률이 0.5에 가장 가까운 샘플(경계선 불확실 샘플). 둘째, 높은 확신도(예: > 0.8)에서 틀린 샘플(고확신 오류). 전자는 수동 라벨 검토로 라벨 노이즈를 발견하는 데 쓰고, 후자는 캘리브레이션 문제나 구조적 피처 부족을 진단하는 데 씁니다.

---

## 정리

오류 분석은 평균 점수의 뒤편을 보는 작업입니다. 어디서 틀리는지, 어떻게 틀리는지, 왜 틀리는지를 분리해야 개선의 방향이 생깁니다.

전체 F1이 좋다는 것은 시작점일 뿐입니다. "어떤 세그먼트에서 실패하는가?", "FP와 FN 중 무엇이 더 많은가?", "확신한 곳에서도 틀리는가?", "어려운 샘플은 라벨 문제인가, 피처 문제인가?" 이 질문들에 답해야 다음 실험이 막연한 개선이 아닌 구체적인 처방이 됩니다.

다음 글에서는 지금까지의 평가 결과를 한 장의 문서로 정리하는 평가 리포트 작성으로 시리즈를 마무리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- **Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기 (현재 글)**
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Model debugging](https://developers.google.com/machine-learning/testing-debugging)
- [Kaggle — Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning)
- [Andrew Ng — Error analysis](https://www.deeplearning.ai/the-batch/issue-115/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, ErrorAnalysis, Slicing, Debugging, scikit-learn
