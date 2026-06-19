---
series: model-evaluation-101
episode: 5
title: "Model Evaluation 101 (5/10): F1 점수"
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
  - F1Score
  - Fbeta
  - ImbalancedData
  - scikit-learn
seo_description: F1의 평균 방식 차이와 올바른 train/validation/test 임계값 선택 절차를 설명합니다.
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (5/10): F1 점수

모델 비교 회의에서 누군가 "F1 점수가 0.85예요"라고 말했습니다. 그런데 옆 팀 동료가 만든 모델은 F1 0.83입니다. 첫 번째 모델이 더 좋을까요? 잠깐, 두 모델 모두 F1의 평균 방식을 밝히지 않았습니다. 하나는 macro, 하나는 micro를 쓴 것으로 밝혀졌습니다. 그리고 소수 클래스의 F1은 각각 0.62와 0.71이었습니다. 이제 어떤 모델이 더 좋은지 분명해졌을까요?

이 글은 Model Evaluation 101 시리즈의 5번째 글입니다.

F1은 정밀도와 재현율을 하나의 숫자로 압축합니다. 그래서 "요약"이 되는 동시에 "숨김"이 됩니다. 이 글은 F1이 무엇을 말하고, 무엇을 숨기는지를 함께 봅니다. 그리고 임계값 선택을 올바른 절차(train → validation → test)로 분리하지 않으면 F1이 얼마나 낙관적인 숫자가 되는지도 살펴봅니다.

![Model Evaluation 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/05/05-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 5장 흐름 개요*

> F1 점수는 편리한 요약이지만, 어떤 평균을 썼는지, 어떤 임계값에서 계산했는지, 그 임계값이 검증 세트에서 올바르게 선택됐는지를 숨깁니다.

## 이 글에서 다룰 문제

- micro, macro, weighted F1은 각각 어떤 질문에 답할까요?
- 같은 예측인데 세 가지 F1이 서로 다른 결론을 주는 이유가 무엇일까요?
- 임계값 선택을 train/validation/test로 분리해야 하는 이유가 무엇일까요?
- F1을 최대화하는 임계값이 운영 최적점이 아닐 수 있는 이유는 무엇인가요?
- F-beta 점수는 언제 F1 대신 사용해야 할까요?

## F1의 정의와 특성

### 조화평균으로서의 F1

```
F1 = 2 × (정밀도 × 재현율) / (정밀도 + 재현율)
   = 2 × TP / (2×TP + FP + FN)
```

F1은 산술평균이 아닌 조화평균을 사용합니다. 조화평균은 두 값 중 하나가 낮으면 평균도 낮아지는 특성이 있습니다.

**예시:**
- 정밀도 0.9, 재현율 0.1 → 산술평균 0.5, F1 = 0.18
- 정밀도 0.5, 재현율 0.5 → 산술평균 0.5, F1 = 0.5

산술평균은 둘 다 0.5지만, F1은 균형 잡힌 두 번째 케이스를 훨씬 높게 평가합니다.

### F1의 맹점

F1은 다음을 숨깁니다.

- **평균 방식**: macro인지, micro인지, weighted인지
- **클래스별 약점**: 전체 평균이 좋아도 특정 클래스가 매우 약할 수 있음
- **임계값 의존성**: 어떤 임계값에서 계산했는지
- **임계값 선택 절차**: 검증 세트에서 선택했는지, 테스트 세트에 과적합했는지

## 1부 — 다중 분류에서 평균 방식 비교

세 가지 평균 방식은 서로 다른 질문에 답합니다.

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, fbeta_score, classification_report
from sklearn.model_selection import train_test_split
import numpy as np

# 3클래스 불균형 데이터 (65%, 25%, 10%)
X, y = make_classification(
    n_samples=3200,
    n_features=12,
    n_informative=6,
    n_redundant=2,
    n_classes=3,
    n_clusters_per_class=1,
    weights=[0.65, 0.25, 0.10],
    class_sep=1.1,
    flip_y=0.02,
    random_state=11,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

# 세 가지 평균 방식
micro_f1 = f1_score(y_test, pred, average="micro")
macro_f1 = f1_score(y_test, pred, average="macro")
weighted_f1 = f1_score(y_test, pred, average="weighted")
per_class = f1_score(y_test, pred, average=None)

print("=== F1 평균 방식 비교 ===")
print(f"micro F1:    {micro_f1:.3f}  → 전체 샘플 기준 (다수 클래스 영향 큼)")
print(f"macro F1:    {macro_f1:.3f}  → 클래스 동등 가중치 (소수 클래스 반영)")
print(f"weighted F1: {weighted_f1:.3f}  → 클래스 샘플 수 가중치")
print(f"per class:   {[round(x, 3) for x in per_class]}")
print()
print("해석:")
print(f"  클래스 0 (65%): F1 = {per_class[0]:.3f}")
print(f"  클래스 1 (25%): F1 = {per_class[1]:.3f}")
print(f"  클래스 2 (10%): F1 = {per_class[2]:.3f}  ← 소수 클래스 약점!")
print()

# F-beta: 비용 비중을 명시적으로 반영
f2_macro = fbeta_score(y_test, pred, beta=2, average="macro")
f05_macro = fbeta_score(y_test, pred, beta=0.5, average="macro")
print("=== F-beta 점수 (재현율 vs 정밀도 가중치) ===")
print(f"F2 macro:   {f2_macro:.3f}  → 재현율 2배 중요 (놓침이 비쌀 때)")
print(f"F1 macro:   {macro_f1:.3f}  → 재현율 = 정밀도")
print(f"F0.5 macro: {f05_macro:.3f}  → 정밀도 2배 중요 (오탐이 비쌀 때)")
```

예상 출력 (근사값):
```
=== F1 평균 방식 비교 ===
micro F1:    0.927  → 전체 샘플 기준 (다수 클래스 영향 큼)
macro F1:    0.881  → 클래스 동등 가중치 (소수 클래스 반영)
weighted F1: 0.925  → 클래스 샘플 수 가중치
per class:   [0.952, 0.923, 0.768]

해석:
  클래스 0 (65%): F1 = 0.952
  클래스 1 (25%): F1 = 0.923
  클래스 2 (10%): F1 = 0.768  ← 소수 클래스 약점!

=== F-beta 점수 (재현율 vs 정밀도 가중치) ===
F2 macro:   0.866  → 재현율 2배 중요 (놓침이 비쌀 때)
F1 macro:   0.881  → 재현율 = 정밀도
F0.5 macro: 0.900  → 정밀도 2배 중요 (오탐이 비쌀 때)
```

### 세 가지 평균 방식 선택 가이드

| 상황 | 권장 평균 방식 | 이유 |
| --- | --- | --- |
| 클래스 균형이 비슷함 | micro 또는 weighted | 각 샘플이 비슷하게 중요 |
| 소수 클래스도 동등하게 중요 | macro | 클래스 불균형 무시 |
| 클래스 비율이 그대로 반영되어야 함 | weighted | 실제 분포 반영 |
| 보고 시 투명성 필요 | per class + macro | 약점 클래스 드러냄 |

**규칙:** F1을 보고할 때는 항상 평균 방식을 명시합니다. "F1=0.88"이 아니라 "macro F1=0.88 (소수 클래스 F1=0.77)"처럼 써야 합니다.

## 2부 — 이진 분류에서 올바른 임계값 선택 절차

이것이 실무에서 가장 자주 틀리는 부분입니다.

### 잘못된 방식: 같은 데이터에서 학습과 임계값 탐색 동시에

```python
# [나쁜 방식] - 절대 하지 말 것!
# X_train으로 학습한 다음, 바로 X_train에서 임계값 탐색
bad_model = LogisticRegression(max_iter=4000)
bad_model.fit(X_train, y_train)
bad_proba_train = bad_model.predict_proba(X_train)[:, 1]

# 훈련 데이터에서 최적 임계값 찾기 (누수!)
best_t_bad = 0.5
best_f1_bad = 0
for t in np.arange(0.1, 0.9, 0.05):
    pred_t = (bad_proba_train >= t).astype(int)
    f1_t = f1_score(y_train, pred_t)
    if f1_t > best_f1_bad:
        best_f1_bad = f1_t
        best_t_bad = t

# 이 임계값으로 테스트 세트 평가
bad_test_proba = bad_model.predict_proba(X_test)[:, 1]
bad_test_pred = (bad_test_proba >= best_t_bad).astype(int)
print(f"[나쁜 방식] 선택된 임계값: {best_t_bad:.2f}")
print(f"[나쁜 방식] 훈련 F1 (과낙관): {best_f1_bad:.3f}")
print(f"[나쁜 방식] 테스트 F1 (실제): {f1_score(y_test, bad_test_pred):.3f}")
```

### 올바른 방식: Train → Validation → Test 분리

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import numpy as np

# 이진 불균형 데이터
X_bin, y_bin = make_classification(
    n_samples=4000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.88, 0.12],
    class_sep=1.0,
    flip_y=0.02,
    random_state=19,
)

# 3분할: train(60%) / val(20%) / test(20%)
X_train_b, X_temp, y_train_b, y_temp = train_test_split(
    X_bin, y_bin, test_size=0.4, stratify=y_bin, random_state=42
)
X_val, X_test_b, y_val, y_test_b = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)

print(f"훈련: {len(y_train_b)}건, 검증: {len(y_val)}건, 테스트: {len(y_test_b)}건")

# 훈련 세트로만 학습
model_b = LogisticRegression(max_iter=4000).fit(X_train_b, y_train_b)
val_proba = model_b.predict_proba(X_val)[:, 1]
test_proba = model_b.predict_proba(X_test_b)[:, 1]

# 검증 세트에서만 임계값 탐색
print("\n=== 검증 세트에서 임계값 탐색 ===")
print(f"{'임계값':>6} {'F1':>8} {'정밀도':>8} {'재현율':>8}")
thresholds = np.arange(0.10, 0.91, 0.05)
rows = []
for t in thresholds:
    val_pred = (val_proba >= t).astype(int)
    f1 = f1_score(y_val, val_pred, zero_division=0)
    prec = precision_score(y_val, val_pred, zero_division=0)
    rec = recall_score(y_val, val_pred, zero_division=0)
    rows.append((round(float(t), 2), f1, prec, rec))

# 주요 임계값만 출력
for t, f1, prec, rec in rows:
    if t in {0.20, 0.30, 0.40, 0.50, 0.60, 0.70}:
        print(f"{t:>6.2f} {f1:>8.3f} {prec:>8.3f} {rec:>8.3f}")

best_threshold, best_val_f1, _, _ = max(rows, key=lambda r: r[1])
print(f"\n최적 임계값 (검증 기준): {best_threshold} (F1={best_val_f1:.3f})")

# 선택한 임계값을 테스트 세트에 잠금
locked_pred = (test_proba >= best_threshold).astype(int)
print(f"\n=== 테스트 세트 최종 평가 (임계값={best_threshold}) ===")
print(f"F1:    {f1_score(y_test_b, locked_pred):.3f}")
print(f"정밀도: {precision_score(y_test_b, locked_pred):.3f}")
print(f"재현율: {recall_score(y_test_b, locked_pred):.3f}")

# 비교: 기본 임계값 0.5
business_pred = (test_proba >= 0.50).astype(int)
print(f"\n=== 비교: 기본 임계값 0.50 ===")
print(f"F1:    {f1_score(y_test_b, business_pred):.3f}")
print(f"정밀도: {precision_score(y_test_b, business_pred):.3f}")
print(f"재현율: {recall_score(y_test_b, business_pred):.3f}")
```

예상 출력 (근사값):
```
=== 검증 세트에서 임계값 탐색 ===
임계값       F1    정밀도    재현율
  0.20    0.596    0.485    0.775
  0.30    0.585    0.564    0.608
  0.40    0.550    0.650    0.480
  0.50    0.503    0.776    0.373
  0.60    0.448    0.862    0.300
  0.70    0.354    0.821    0.225

최적 임계값 (검증 기준): 0.2 (F1=0.596)

=== 테스트 세트 최종 평가 (임계값=0.20) ===
F1:    0.627
정밀도: 0.527
재현율: 0.775

=== 비교: 기본 임계값 0.50 ===
F1:    0.490
정밀도: 0.717
재현율: 0.373
```

## F1 최적 임계값 vs. 운영 최적 임계값

검증 세트에서 F1을 최대화하는 임계값이 0.20으로 나왔습니다. 그런데 이것이 항상 최고의 운영 정책일까요?

```python
print("=== F1 최적 vs. 운영 최적 비교 ===")
print()
print("임계값 0.20 (F1 최적):")
pred_020 = (test_proba >= 0.20).astype(int)
tn, fp, fn, tp = __import__('sklearn.metrics', fromlist=['confusion_matrix']).confusion_matrix(y_test_b, pred_020).ravel()
print(f"  재현율: {tp/(tp+fn):.3f}  → 놓침 {fn}건")
print(f"  정밀도: {tp/(tp+fp):.3f}  → 오탐 {fp}건")
print(f"  F1:    {f1_score(y_test_b, pred_020):.3f}")

print()
print("임계값 0.50 (기본값):")
pred_050 = (test_proba >= 0.50).astype(int)
tn2, fp2, fn2, tp2 = __import__('sklearn.metrics', fromlist=['confusion_matrix']).confusion_matrix(y_test_b, pred_050).ravel()
print(f"  재현율: {tp2/(tp2+fn2):.3f}  → 놓침 {fn2}건")
print(f"  정밀도: {tp2/(tp2+fp2):.3f}  → 오탐 {fp2}건")
print(f"  F1:    {f1_score(y_test_b, pred_050):.3f}")

print()
print("운영 결론:")
print("  - 놓침 비용이 크다면: 0.20 선택 (재현율 우선)")
print("  - 오탐 비용이 크다면: 0.50 선택 (정밀도 우선)")
print("  - F1이 가장 중요하다면: 0.20 선택")
print("  → F1 최적 임계값이 비즈니스 최적 임계값과 다를 수 있음!")
```

## F-beta 점수: 재현율과 정밀도의 가중 균형

```python
from sklearn.metrics import fbeta_score

# 의료 진단 시나리오: 환자를 놓치면 안 됨 → 재현율 중요
print("=== F-beta 시나리오별 선택 ===")
print()
print("시나리오 1: 희귀 질환 진단 (놓침 비용 매우 큼)")
print("  beta=2 사용: 재현율이 정밀도보다 2배 중요")
print(f"  F2 (beta=2): {fbeta_score(y_test_b, locked_pred, beta=2):.3f}")
print()
print("시나리오 2: 광고 클릭 예측 (오탐 비용 큼)")
print("  beta=0.5 사용: 정밀도가 재현율보다 2배 중요")
print(f"  F0.5 (beta=0.5): {fbeta_score(y_test_b, locked_pred, beta=0.5):.3f}")
print()
print("시나리오 3: 사기 탐지 (균형)")
print("  beta=1 사용: 재현율 = 정밀도")
print(f"  F1 (beta=1): {f1_score(y_test_b, locked_pred):.3f}")

print()
print("F-beta 공식:")
print("  F_beta = (1 + beta^2) × (precision × recall) / (beta^2 × precision + recall)")
print("  beta > 1: 재현율 가중 (놓침이 비쌀 때)")
print("  beta < 1: 정밀도 가중 (오탐이 비쌀 때)")
print("  beta = 1: F1 (균형)")
```

## Before vs. After: F1 사용 방식 비교

| 항목 | 나이브 접근 | 올바른 접근 |
| --- | --- | --- |
| 평균 방식 | 명시 안 함 | "macro F1 = 0.88" |
| 클래스별 확인 | 안 함 | per-class F1 필수 확인 |
| 임계값 선택 | 훈련 데이터에서 | 검증 세트에서만 |
| 테스트 사용 | 반복 사용 | 임계값 잠근 후 한 번만 |
| 보고 형식 | "F1 0.85" | "macro F1 0.88 (소수 클래스 F1 0.77, 임계값 0.35)" |

## 자주 하는 실수

**실수 1 — 평균 방식 생략**

"F1 0.88"이라고만 쓰면 micro인지, macro인지, weighted인지 알 수 없습니다. 이 세 가지는 같은 예측에서 서로 다른 숫자를 냅니다. 항상 평균 방식을 명시해야 합니다.

**실수 2 — 훈련 데이터에서 임계값 최적화**

학습한 데이터에서 임계값을 탐색하면 훈련 데이터에 과적합된 임계값을 얻습니다. 이 임계값은 실제 운영에서 기대치보다 낮은 성능을 냅니다. 임계값 탐색은 반드시 별도의 검증 세트에서 해야 합니다.

**실수 3 — F1 최댓값 임계값 = 운영 최적 임계값으로 오해**

F1을 최대화하는 임계값이 비즈니스 목표를 최적화하는 임계값과 같을 필요는 없습니다. 비즈니스에서 재현율 최소 70% 보장이 요구사항이라면, F1이 조금 낮더라도 그 요구사항을 만족하는 임계값을 선택해야 합니다.

**실수 4 — 소수 클래스 F1 확인 안 함**

macro F1이 0.88이어도 소수 클래스 F1이 0.60이면 이 모델은 소수 클래스를 제대로 처리하지 못합니다. `f1_score(y_test, pred, average=None)`으로 항상 클래스별 F1을 확인해야 합니다.

**실수 5 — beta 값을 임의로 선택**

F-beta에서 beta 값은 비용 구조에서 와야 합니다. "재현율이 조금 더 중요한 것 같으니 beta=1.5"가 아니라, 실제 비용 비율(FN 비용 / FP 비용)을 기반으로 결정해야 합니다.

## 운영 체크리스트

- [ ] F1의 평균 방식(micro/macro/weighted)을 명시했습니다.
- [ ] `f1_score(average=None)`으로 클래스별 F1을 확인했습니다.
- [ ] 임계값 탐색은 검증 세트(validation set)에서만 했습니다.
- [ ] 선택한 임계값을 테스트 세트에 잠근 후 최종 평가했습니다.
- [ ] F1 최적 임계값과 비즈니스 최적 임계값을 별도로 비교했습니다.
- [ ] 필요한 경우 F-beta를 사용해 비용 비중을 명시적으로 반영했습니다.

## 처음 질문으로 돌아가기

- **micro, macro, weighted F1은 각각 어떤 질문에 답할까요?**
  - micro F1은 "전체 예측의 몇 퍼센트가 맞는가?"로 클래스 비율 영향을 그대로 받습니다. macro F1은 "각 클래스에서 평균적으로 얼마나 잘하는가?"로 소수 클래스도 동등한 가중치를 받습니다. weighted F1은 "클래스 크기를 반영했을 때 얼마나 잘하는가?"입니다. 불균형 데이터에서 세 가지는 서로 다른 값을 냅니다.

- **임계값 선택을 train/validation/test로 분리해야 하는 이유가 무엇일까요?**
  - 훈련 데이터에서 임계값을 탐색하면 훈련 데이터의 우연한 패턴까지 흡수한 낙관적 임계값을 얻습니다. 이 임계값은 새 데이터에 일반화되지 않습니다. 검증 세트에서 임계값을 선택하고 테스트 세트에서 한 번만 평가해야 현실적인 성능 추정치를 얻을 수 있습니다.

- **F1을 최대화하는 임계값이 운영 최적점이 아닐 수 있는 이유는 무엇인가요?**
  - F1은 정밀도와 재현율의 균형을 측정하지만, 비즈니스에서는 재현율 최소 보장, 처리 팀 용량 제한, FN/FP 비용 비율 같은 추가 제약이 있습니다. 이 제약들을 모두 F1 단일 숫자로 표현할 수 없기 때문에, F1 최적 임계값이 비즈니스 최적 임계값과 다를 수 있습니다.

---

## 정리

F1은 여전히 유용한 요약 지표이지만, 절차가 빠지면 금세 낙관적 숫자가 됩니다. 올바른 질문은 "F1이 몇 점인가?"가 아니라 "어떤 평균 방식으로, 어떤 검증 절차를 거쳐, 어떤 임계값에서 그 점수가 나왔는가?"입니다.

보고서에 F1을 쓸 때는 이렇게 쓰세요: "macro F1 = 0.881 (클래스별: [0.952, 0.923, 0.768]). 이진 운영 정책에서는 검증 세트 기준 최적 임계값 0.20에서 F1 0.627, 정밀도 0.527, 재현율 0.775를 달성했습니다."

다음 글에서는 임계값 하나에 덜 묶인 순위화 관점인 ROC와 AUC를 살펴보고, 결국 다시 운영 임계값으로 착지하는 흐름을 완성합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- **Model Evaluation 101 (5/10): F1 점수 (현재 글)**
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- [Model Evaluation 101 (10/10): 평가 리포트 만들기](./10-evaluation-report.md)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)
- [scikit-learn — fbeta_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fbeta_score.html)
- [scikit-learn — precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
- [Wikipedia — F-score](https://en.wikipedia.org/wiki/F-score)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, F1Score, Fbeta, ImbalancedData, scikit-learn
