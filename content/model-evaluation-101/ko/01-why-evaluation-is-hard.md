---
series: model-evaluation-101
episode: 1
title: "Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?"
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
  - Metrics
  - MachineLearning
  - Foundations
  - Beginner
seo_description: 머신러닝 모델 평가가 비즈니스 목표와 일치해야 하는 이유를 설명하고, 올바른 평가 지표 설정을 위한 접근법을 제시합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?

스팸 필터를 만들었습니다. 정확도 98%가 나왔습니다. 팀 모두가 박수를 쳤습니다. 그런데 다음 날 고객 지원 티켓이 쏟아졌습니다. "중요한 계약 이메일이 스팸으로 빠졌어요." 정확도 98%가 맞는 것이었는데, 왜 이런 일이 생겼을까요?

이 글은 Model Evaluation 101 시리즈의 첫 번째 글입니다.

모델 평가는 처음 배울 때보다 실무에 들어간 뒤 더 어렵게 느껴집니다. 실습에서는 점수 하나만 출력해도 그럴듯해 보이지만, 실제 의사결정은 그렇게 단순하지 않기 때문입니다. 같은 정확도 95%라도 어떤 데이터에서 측정했는지, 어떤 오류가 더 비싼지, 임계값을 어디에 두었는지에 따라 의미가 완전히 달라집니다.

평가가 흔들리면 모델 선택도 흔들립니다. 더 큰 문제는 팀이 잘못된 숫자를 기준으로 같은 방향으로 달려간다는 사실입니다. 그래서 평가를 지표 계산이 아니라 의사결정 설계의 일부로 이해해야 합니다.

![Model Evaluation 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/01/01-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 1장 흐름 개요*

> 평가는 지표 계산이 아니라 의사결정 설계입니다 — 같은 점수도 데이터 분포·오류 비용·임계값에 따라 전혀 다른 의미를 가지므로, 진짜 위험은 팀 전체가 잘못된 숫자를 향해 최적화하는 것입니다.

## 이 글에서 다룰 문제

- 왜 정확도 하나만으로 모델을 판단하면 위험할까요?
- 데이터 분포와 베이스레이트는 평가를 어떻게 왜곡할까요?
- 임계값이 바뀌면 같은 모델의 점수는 왜 달라질까요?
- 비용 행렬이란 무엇이고 왜 필요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

## 평가 프레임워크: 세 가지 축

좋은 모델 평가는 세 가지 축을 동시에 봅니다.

### 축 1 — 데이터 분포

어떤 데이터에서 측정했는지가 점수만큼 중요합니다. 훈련 데이터와 배포 환경의 분포가 다르면, 높은 테스트 점수도 미래 성능을 보장하지 못합니다. 특히 클래스 불균형이 심할수록 분포 파악이 먼저입니다.

### 축 2 — 오류 비용

모든 오류가 같은 비용을 지지 않습니다. 스팸 필터에서 정상 이메일을 스팸으로 분류하는 오류(false positive)와 스팸을 정상으로 분류하는 오류(false negative)는 비용이 전혀 다릅니다. 암 진단에서는 암을 놓치는 오류(false negative)가 암이 아닌데 암으로 판정하는 오류(false positive)보다 훨씬 비쌉니다.

### 축 3 — 임계값 선택

분류 모델은 확률을 출력합니다. 그 확률을 클래스 예측으로 바꾸는 기준이 임계값입니다. 기본값 0.5를 그대로 쓰는 경우가 많지만, 임계값은 비용 구조와 운영 목표에 따라 정해야 합니다. 같은 모델이라도 임계값에 따라 완전히 다른 운영 결과가 나옵니다.

## 시나리오: 사기 거래 탐지 시스템

구체적인 시나리오로 생각해 봅시다. 온라인 결제 플랫폼의 사기 거래 탐지 시스템을 평가한다고 가정합니다.

**데이터셋:**
- 총 10,000건의 거래
- 정상 거래: 9,700건 (97%)
- 사기 거래: 300건 (3%)

**두 모델의 결과:**

| 모델 | 정확도 | 사기 탐지율(재현율) | 오탐률(1-정밀도) |
| --- | ---: | ---: | ---: |
| 모델 A (더미: 전부 정상 예측) | 97.0% | 0% | 0% |
| 모델 B (실제 탐지 모델) | 96.5% | 70% | 15% |

정확도만 보면 모델 A가 더 좋습니다. 하지만 실제로 사기를 탐지해야 하는 시스템에서 모델 A는 완전히 쓸모없습니다. 이것이 정확도의 함정입니다.

**비용 계산:**

사기 거래 1건당 평균 손실이 100만 원, 오탐으로 인한 고객 불편 비용이 1만 원이라면:

- 모델 A: 300건 × 100만 원 = 3억 원 손실
- 모델 B: 90건 × 100만 원 + 31,500건의 오탐 × 1만 원 = 9천만 원 + 3억 1,500만 원 = 4억 500만 원

여기서 모델 B의 임계값을 높이면 오탐을 줄일 수 있습니다. 최적 임계값은 이 비용 구조에서 역산해야 합니다.

## 평가의 함정을 직접 보는 코드

### 1단계 — 불균형 데이터와 더미 모델의 정확도 함정

```python
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    recall_score,
    precision_score,
)

# 97:3 불균형 데이터 시뮬레이션
np.random.seed(42)
n_total = 10000
n_fraud = 300
y_true = np.array([0] * (n_total - n_fraud) + [1] * n_fraud)

# 더미 모델: 모두 정상으로 예측
y_dummy = np.zeros(n_total, dtype=int)

print("=== 더미 모델 (전부 정상 예측) ===")
print(f"정확도: {accuracy_score(y_true, y_dummy):.4f}")
print(f"사기 재현율: {recall_score(y_true, y_dummy):.4f}")
print(f"혼동 행렬:\n{confusion_matrix(y_true, y_dummy)}")
print()
print("→ 정확도 97%지만 사기를 하나도 못 잡음!")
```

예상 출력:
```
=== 더미 모델 (전부 정상 예측) ===
정확도: 0.9700
사기 재현율: 0.0000
혼동 행렬:
[[9700    0]
 [ 300    0]]

→ 정확도 97%지만 사기를 하나도 못 잡음!
```

### 2단계 — 혼동 행렬 완전 해석

```python
# 실제 탐지 모델 시뮬레이션
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

X, y = make_classification(
    n_samples=10000,
    n_features=15,
    n_informative=6,
    weights=[0.97, 0.03],
    class_sep=1.0,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=2000, class_weight='balanced').fit(X_train, y_train)
y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print("=== 혼동 행렬 해석 ===")
print(f"혼동 행렬:\n{cm}")
print()
print(f"TN (진음성): {tn}  → 정상을 정상으로 올바르게 분류")
print(f"FP (위양성): {fp}  → 정상을 사기로 잘못 분류 (고객 불편)")
print(f"FN (위음성): {fn}  → 사기를 정상으로 잘못 분류 (손실 발생!)")
print(f"TP (진양성): {tp}  → 사기를 사기로 올바르게 분류")
print()
print(f"정확도: {(tn+tp)/(tn+fp+fn+tp):.4f}")
print(f"정밀도: {tp/(tp+fp):.4f}  → 사기 경보 중 실제 사기 비율")
print(f"재현율: {tp/(tp+fn):.4f}  → 실제 사기 중 탐지 비율")
```

### 3단계 — 임계값 민감도 분석

```python
import numpy as np

y_proba = model.predict_proba(X_test)[:, 1]

print("=== 임계값별 성능 비교 ===")
print(f"{'임계값':>6} {'정확도':>8} {'정밀도':>8} {'재현율':>8} {'사기탐지':>8} {'오탐':>6}")
print("-" * 55)

for threshold in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    y_pred_t = (y_proba >= threshold).astype(int)
    tn_t, fp_t, fn_t, tp_t = confusion_matrix(y_test, y_pred_t).ravel()
    acc = (tn_t + tp_t) / len(y_test)
    prec = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0
    rec = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0
    print(f"{threshold:>6.1f} {acc:>8.4f} {prec:>8.4f} {rec:>8.4f} {tp_t:>8d} {fp_t:>6d}")
```

예상 출력 (근사값):
```
=== 임계값별 성능 비교 ===
임계값    정확도    정밀도    재현율  사기탐지    오탐
-------------------------------------------------------
   0.1   0.9320   0.2150   0.9333       84    307
   0.2   0.9580   0.3480   0.8333       75    141
   0.3   0.9710   0.5000   0.7222       65     65
   0.4   0.9780   0.6500   0.6111       55     30
   0.5   0.9820   0.7800   0.5000       45     13
   0.6   0.9840   0.8800   0.3778       34      5
   0.7   0.9850   0.9500   0.2111       19      1
```

임계값 0.5에서 0.3으로 낮추면 정확도는 약간 떨어지지만, 사기 탐지율(재현율)이 50%에서 72%로 크게 오릅니다. 이 차이가 실제 비즈니스에서는 수억 원의 차이가 됩니다.

### 4단계 — 비용 행렬(Cost Matrix) 설계

```python
def calculate_cost(y_true, y_pred, cost_fn=100, cost_fp=1):
    """
    cost_fn: False Negative 비용 (사기 놓침) - 단위: 만원
    cost_fp: False Positive 비용 (오탐, 고객 불편) - 단위: 만원
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    total_cost = fn * cost_fn + fp * cost_fp
    return {
        'FN': fn, 'FP': fp,
        'fn_cost': fn * cost_fn,
        'fp_cost': fp * cost_fp,
        'total_cost': total_cost
    }

print("=== 비용 행렬 분석 (사기 손실: 100만원, 오탐 비용: 1만원) ===")
print(f"{'임계값':>6} {'FN':>5} {'FP':>5} {'FN비용(만)':>12} {'FP비용(만)':>12} {'총비용(만)':>12}")
print("-" * 65)

for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
    y_pred_t = (y_proba >= threshold).astype(int)
    result = calculate_cost(y_test, y_pred_t)
    print(
        f"{threshold:>6.1f} {result['FN']:>5d} {result['FP']:>5d} "
        f"{result['fn_cost']:>12,d} {result['fp_cost']:>12,d} "
        f"{result['total_cost']:>12,d}"
    )
```

### 5단계 — 나이브 평가 vs. 올바른 평가 비교

```python
print("=== Before: 나이브 평가 (정확도만 보기) ===")
print("결론: '정확도 97%! 모델 완성!'")
print()

print("=== After: 올바른 평가 (비용 구조 반영) ===")
print("체크리스트:")
print("1. 베이스레이트 확인: 사기 비율 3%")
print("2. 더미 모델 기준선: 97.0% (아무것도 안 해도 이 수치)")
print("3. 소수 클래스 재현율: 사기의 몇 %를 잡는가?")
print("4. 비용 행렬: FN 손실 vs FP 불편 비용")
print("5. 최적 임계값: 비용 최소화 지점 찾기")
print("6. 임계값 결정 근거 문서화")
```

## 자주 하는 실수

실무에서 반복적으로 나타나는 평가 오류들입니다.

**실수 1 — 정확도만 보고 모델 채택**

불균형 데이터에서 정확도는 다수 클래스의 성능을 그대로 반영합니다. 97:3 데이터에서 97% 정확도를 보고 좋은 모델이라고 결론 내리면, 실제로는 아무것도 탐지 못하는 더미 모델을 채택하는 것과 같습니다.

**실수 2 — 임계값 0.5를 기본값으로 고정**

분류 모델의 기본 임계값은 편의상 0.5를 쓰지만, 이것이 비즈니스 최적점인 경우는 드뭅니다. 암 진단이라면 재현율을 극대화해야 하므로 임계값을 0.2~0.3으로 낮춰야 할 수도 있습니다. 임계값은 항상 비용 구조로부터 결정해야 합니다.

**실수 3 — 테스트 세트를 반복 사용해 임계값 조정**

임계값을 테스트 세트에서 반복해서 조정하면, 그 테스트 세트는 더 이상 독립적인 평가 세트가 아닙니다. 임계값 탐색은 반드시 검증 세트(validation set)에서만 해야 합니다.

**실수 4 — 단일 지표 최적화**

F1 점수 하나를 최대화하는 방향으로 모델을 튜닝하면, 비즈니스가 실제로 원하는 것(특정 재현율 보장, 특정 FPR 제약 등)을 놓칠 수 있습니다. 지표는 비즈니스 목표의 대리 변수일 뿐이며, 진짜 목표를 숫자로 직접 표현해야 합니다.

**실수 5 — 드리프트 무시**

배포 시점의 데이터 분포와 운영 중 데이터 분포가 달라지는 드리프트를 고려하지 않으면, 오늘의 좋은 평가가 3개월 뒤에는 무의미해집니다. 평가는 배포 시점만이 아니라 운영 중에도 지속적으로 해야 합니다.

## Before vs. After: 평가 접근 방식 비교

| 항목 | 나이브 접근 | 올바른 접근 |
| --- | --- | --- |
| 핵심 지표 | 정확도 하나 | 정확도 + 재현율 + 정밀도 + 비용 |
| 불균형 처리 | 확인 안 함 | 베이스레이트 먼저 확인 |
| 임계값 | 0.5 고정 | 비용 구조에서 역산 |
| 오류 구분 | FP/FN 구분 안 함 | FP/FN 개별 비용 산정 |
| 기준선 | 없음 | 더미 모델 기준선 필수 |
| 드리프트 | 고려 안 함 | 배포 후 모니터링 계획 포함 |
| 문서화 | 점수 하나 | 임계값, 비용 가정, 제약 조건 전부 기록 |

## 평가를 의사결정 설계로 보는 방법

평가 지표를 정하기 전에 반드시 먼저 물어야 할 질문들이 있습니다.

**1. 어떤 오류가 더 비싼가?**

FP(거짓 양성)와 FN(거짓 음성) 중 어느 쪽이 더 많은 비용을 지는지 명시적으로 정의합니다. 이 비율이 곧 임계값의 방향을 결정합니다.

**2. 이 모델이 실제로 돕는 결정은 무엇인가?**

모델의 출력이 어떤 인간 의사결정을 대체하거나 보조하는지 명확히 합니다. 이것이 지표 선택의 기준이 됩니다.

**3. 데이터 분포는 배포 환경과 얼마나 비슷한가?**

훈련/테스트 데이터가 실제 운영 환경을 대표하는지 확인합니다. 특히 시간적 드리프트, 지역적 편차, 계절성을 고려해야 합니다.

**4. 팀이 감당할 수 있는 운영 부담은 어느 수준인가?**

재현율을 높이면 오탐이 늘고, 오탐이 늘면 검토 비용이 증가합니다. 팀이 하루에 처리할 수 있는 경보 건수가 한계입니다. 이 제약도 지표 설계에 반영해야 합니다.

## 평가 지표 선택 가이드

어떤 지표를 써야 할지 막막할 때 이 표를 참고하세요.

| 상황 | 권장 지표 | 피해야 할 지표 |
| --- | --- | --- |
| 클래스 균형 (50:50) | 정확도, F1 | 없음 |
| 클래스 불균형 (90:10 이상) | 재현율, 정밀도, F1, AUC-PR | 정확도만 |
| 놓침(FN) 비용이 클 때 | 재현율 (소수 클래스), F-beta (beta>1) | 정밀도만 |
| 거짓 경보(FP) 비용이 클 때 | 정밀도, F-beta (beta<1) | 재현율만 |
| 모델 비교 (임계값 독립) | ROC-AUC, PR-AUC | 특정 임계값 F1 |
| 확률값을 비용 계산에 사용 | Brier 점수, 신뢰도 다이어그램 | AUC만 |
| 시계열, 드리프트 모니터링 | 롤링 윈도우 지표 | 전체 평균만 |

## 평가 설계 체크리스트 (배포 전)

실무에서 배포 전 평가를 설계할 때 이 질문들에 모두 답할 수 있어야 합니다.

```python
# 평가 설계 검증 함수
def validate_evaluation_design(config: dict) -> list:
    """
    평가 설계의 완전성을 검증합니다.
    누락된 요소 목록을 반환합니다.
    """
    required = {
        "base_rate": "클래스 비율 (베이스레이트) 확인",
        "dummy_baseline": "더미 모델 기준선 설정",
        "primary_metric": "주요 지표 선택 근거",
        "fp_cost": "FP (거짓 양성) 비용 정의",
        "fn_cost": "FN (거짓 음성) 비용 정의",
        "threshold": "임계값 선택 방법 명시",
        "test_set_strategy": "테스트 세트 독립성 보장",
        "monitoring_plan": "배포 후 모니터링 계획",
    }

    missing = []
    for key, description in required.items():
        if key not in config or config[key] is None:
            missing.append(f"누락: {description}")

    return missing

# 예시 평가 설계 (불완전한 경우)
incomplete_design = {
    "base_rate": 0.04,
    "dummy_baseline": 0.96,
    "primary_metric": "accuracy",
    # fp_cost, fn_cost 누락
    "threshold": 0.5,  # 근거 없이 0.5 고정
    "test_set_strategy": "random split",
    # monitoring_plan 누락
}

issues = validate_evaluation_design(incomplete_design)
print("평가 설계 검증 결과:")
if issues:
    for issue in issues:
        print(f"  {issue}")
else:
    print("  모든 요소 충족")
```

## 운영 체크리스트

- [ ] 데이터의 클래스 비율(베이스레이트)을 먼저 확인했습니다.
- [ ] 더미 모델(most_frequent 전략)과의 기준선 비교를 했습니다.
- [ ] 정확도 외에 재현율과 정밀도를 함께 확인했습니다.
- [ ] FP와 FN의 비즈니스 비용을 명시적으로 정의했습니다.
- [ ] 임계값 선택 근거를 문서로 남겼습니다.
- [ ] 배포 후 모니터링 계획을 세웠습니다.
- [ ] 혼동 행렬을 항상 확인합니다.

## 처음 질문으로 돌아가기

- **왜 정확도 하나만으로 모델을 판단하면 위험할까요?**
  - 불균형 데이터에서 정확도는 다수 클래스의 성능을 반영합니다. 97:3 사기 탐지 문제에서 아무것도 탐지 안 하는 더미 모델이 97% 정확도를 기록합니다. 정확도는 클래스 불균형이 크면 베이스레이트에 수렴하는 경향이 있고, 오류 비용의 비대칭성을 전혀 반영하지 못합니다.

- **데이터 분포와 베이스레이트는 평가를 어떻게 왜곡할까요?**
  - 베이스레이트가 97:3이면 모든 예측을 다수 클래스로 해도 97% 정확도가 나옵니다. 평가 지표를 선택하기 전에 베이스레이트를 확인해야 하며, 불균형이 심할수록 정확도 대신 재현율, 정밀도, F1, AUC-PR 등을 우선해야 합니다.

- **임계값이 바뀌면 같은 모델의 점수는 왜 달라질까요?**
  - 분류 모델은 확률을 출력하고, 임계값은 그 확률을 클래스로 변환하는 기준입니다. 임계값을 낮추면 더 많이 양성으로 분류하여 재현율이 오르고 정밀도가 낮아집니다. 임계값을 높이면 반대입니다. 따라서 같은 모델이라도 임계값에 따라 완전히 다른 운영 결과가 나옵니다.

---

## 정리

모델 평가가 어려운 이유는 숫자가 많아서가 아닙니다. 하나의 숫자로 줄일 수 없는 현실을 상대하기 때문입니다. 데이터 분포, 오류 비용, 임계값, 드리프트를 함께 봐야 비로소 평가가 모델 선택의 언어가 됩니다.

평가를 올바르게 설계하는 순서는 이렇습니다. 먼저 비즈니스 비용 구조를 정의합니다. 다음으로 데이터의 베이스레이트를 확인합니다. 더미 모델과 기준선을 만듭니다. 그 다음에야 지표를 선택하고, 마지막에 임계값을 결정합니다. 이 순서를 뒤집으면 숫자는 예뻐 보여도 의사결정은 약해집니다.

다음 글에서는 이 언어의 출발점인 train, validation, test 세트의 역할과 데이터 누수를 방지하는 방법을 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가? (현재 글)**
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Metrics, MachineLearning, Foundations, Beginner
