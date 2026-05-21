---
series: model-evaluation-101
episode: 10
title: "Model Evaluation 101 (10/10): 평가 리포트 만들기"
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
  - Reporting
  - ModelCard
  - Reproducibility
  - scikit-learn
seo_description: 프로덕션 배포 결정의 근거가 되는 종합적인 모델 평가 리포트 구성 요소와 자동화된 파이프라인 구축 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (10/10): 평가 리포트 만들기

모델 학습과 평가까지는 많은 팀이 잘합니다. 문제는 배포 직전입니다. 이때 결과가 슬라이드 한 장이나 메시지 한 줄로 축약되면, 며칠 뒤에는 가장 중요한 맥락이 사라집니다. 어떤 데이터에서 계산했는지, 임계값은 얼마였는지, 어떤 슬라이스가 약했는지, 재현성 정보가 남아 있는지 다시 묻게 됩니다.

좋은 평가 리포트는 그래서 문서 작업이 아니라 의사결정 기록입니다. 리뷰, 감사, 사고 후 분석이 모두 같은 문서를 참고할 수 있어야 팀의 속도도 유지되고 책임 경계도 분명해집니다.

이 글은 Model Evaluation 101 시리즈의 10번째 글입니다.

## 먼저 던지는 질문

- 모델 배포 전에 어떤 평가 정보를 한곳에 모아야 할까요?
- 평가 리포트와 Model Card는 무엇이 다를까요?
- 임계값, 슬라이스, 재현성 정보는 왜 빠지면 안 될까요?

## 큰 그림

![Model Evaluation 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/10/10-01-concept-at-a-glance.ko.png)

*Model Evaluation 101 10장 흐름 개요*

## 왜 이 글이 중요한가

평가 리포트가 없으면 같은 질문에 팀이 계속 같은 답을 다시 만들어야 합니다. 어떤 모델을 왜 선택했는지, 어떤 한계를 알고도 배포했는지, 나중에 같은 결과를 다시 재현할 수 있는지 확인하기가 어려워집니다.

반대로 리포트 형식이 일정하면 리뷰와 감사가 훨씬 빨라집니다. 어떤 숫자가 어디서 왔는지 추적하기 쉬워지고, 비교 기준도 안정됩니다. 결국 리포트는 문서 정리의 문제가 아니라 팀 메모리의 문제입니다.

## 한눈에 보는 멘탈 모델

이 다섯 요소가 한곳에 모여야 리포트가 완성됩니다. 데이터, 지표, 슬라이스, 재현성, 리스크 중 하나라도 빠지면 배포 판단의 근거가 비어 버립니다.

## 핵심 용어

- **Model Card**: 모델의 의도와 한계를 설명하는 문서입니다.
- **Datasheet**: 데이터셋의 출처와 편향 가능성을 설명하는 문서입니다.
- **운영 임계값**: 실제 배포 환경에서 사용하는 결정 기준선입니다.
- **재현성 해시**: 코드와 데이터 버전을 다시 식별할 수 있는 값입니다.
- **리스크 등록부**: 이미 알고 있는 실패 모드 목록입니다.

## 리포트를 읽는 방식의 전환

좋지 않은 습관은 점수 하나만 전달하고 끝내는 것입니다. `acc 0.92` 혹은 `F1 0.81`만으로는 배포 판단의 맥락이 남지 않습니다. 누가 봐도 다시 계산할 수 있고, 같은 질문에 같은 답을 줄 수 있어야 합니다.

좋은 습관은 리포트를 산출물로 다루는 것입니다. 모델을 다시 학습하면 리포트도 다시 생성되고, 숫자마다 어떤 데이터와 임계값에서 나왔는지 추적할 수 있어야 합니다.

## 평가 리포트를 만드는 다섯 단계

### 1단계 — 지표 수집

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score, brier_score_loss
X, y = make_classification(n_samples=3000, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
proba = m.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)
metrics = {
    "f1_macro": f1_score(yte, pred, average="macro"),
    "auc_roc": roc_auc_score(yte, proba),
    "brier": brier_score_loss(yte, proba),
}
```

### 2단계 — 슬라이스 점수 수집

```python
slice_mask = Xte[:, 0] > 0
slices = {
    "slice_pos": f1_score(yte[slice_mask], pred[slice_mask]),
    "slice_neg": f1_score(yte[~slice_mask], pred[~slice_mask]),
}
```

### 3단계 — 메타데이터 기록

```python
import hashlib, sys, sklearn
meta = {
    "python": sys.version.split()[0],
    "sklearn": sklearn.__version__,
    "data_hash": hashlib.sha1(X.tobytes()).hexdigest()[:10],
    "threshold": 0.5,
}
```

### 4단계 — 리포트 직렬화

```python
import json
report = {"metrics": metrics, "slices": slices, "meta": meta,
          "risks": ["minor calibration drift", "slice_neg lower F1"]}
print(json.dumps(report, indent=2))
```

### 5단계 — 마크다운 렌더링

```python
def to_md(rep):
    lines = ["# Evaluation Report", "## Metrics"]
    for k, v in rep["metrics"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Slices")
    for k, v in rep["slices"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Meta")
    for k, v in rep["meta"].items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)

print(to_md(report))
```

**예상 결과:** 먼저 기계가 읽기 좋은 JSON 리포트가 나오고, 그다음 사람이 바로 리뷰할 수 있는 마크다운 요약이 나와야 합니다. 지표, 임계값, 슬라이스, 재현성 메타데이터, 알려진 리스크가 한 번에 모이면 리포트의 최소 골격이 갖춰진 것입니다.

## 이 코드에서 먼저 봐야 할 점

첫 번째와 두 번째 단계는 리포트가 단순한 점수 표가 아니라는 점을 보여 줍니다. 전체 지표와 슬라이스 지표가 함께 있어야 약한 구간을 숨기지 않을 수 있습니다. 세 번째 단계의 메타데이터는 나중에 재현성을 복원하는 뼈대가 됩니다.

네 번째와 다섯 번째 단계는 생성 순서도 중요하다는 점을 보여 줍니다. 먼저 구조화된 JSON을 만들고, 그다음 사람이 읽을 마크다운으로 바꾸는 편이 자동화와 검증에 유리합니다.

## 자주 헷갈리는 지점

첫째, 임계값을 기록하지 않으면 숫자의 의미가 흔들립니다. 둘째, 슬라이스 점수를 빼면 평균 뒤의 위험이 사라집니다. 셋째, 버전과 해시 정보를 빼면 같은 결과를 다시 만들 수 없습니다.

또한 리스크 섹션을 비워 두는 실수도 많습니다. 하지만 배포 판단에서 가장 중요한 것은 이미 알고 있는 약점을 숨기지 않는 일입니다. 좋은 리포트는 자신감보다 제약을 더 또렷하게 남깁니다.

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 평가 리포트를 빌드 산출물처럼 다룹니다. 모델이 새로 학습되면 리포트도 함께 다시 생성되어야 하고, 숫자마다 출처가 분명해야 합니다. 손으로 작성한 요약은 빠를 수 있지만 오래 버티지 못합니다.

또한 Model Card와 평가 리포트를 구분합니다. Model Card가 더 넓은 설명 문서라면, 평가 리포트는 특정 실험과 배포 판단을 뒷받침하는 좁고 단단한 운영 문서입니다.

## 점검 목록

- [ ] 지표와 임계값을 함께 기록합니다.
- [ ] 슬라이스 점수를 포함합니다.
- [ ] 버전과 해시 정보를 남깁니다.
- [ ] 알려진 리스크를 숨기지 않고 적습니다.

## 정리

좋은 평가 리포트는 한 장짜리 요약이면서도, 배포 판단에 필요한 맥락을 빠짐없이 담고 있어야 합니다. 데이터, 지표, 임계값, 슬라이스, 재현성, 리스크가 한곳에 모여야 숫자가 의사결정의 근거가 됩니다. 여기까지가 Model Evaluation 101의 기본 어휘이며, 이후에는 MLOps와 더 깊은 오류 분석으로 자연스럽게 이어질 수 있습니다.


## 평가 실무에서 바로 쓰는 계산 루틴

### confusion matrix를 수식과 코드로 동시에 확인하기
평가 지표는 라이브러리 호출만으로 끝내면 해석이 약해집니다. confusion matrix를 직접 계산해 보면 지표의 민감도를 빠르게 이해할 수 있습니다.

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0])
y_pred = np.array([1,0,1,0,0,1,1,0,1,0])

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)

print(tn, fp, fn, tp)
print(round(precision, 4), round(recall, 4), round(f1, 4))
```

직접 계산한 값과 `precision_score`, `recall_score`, `f1_score` 결과가 일치해야 합니다. 일치하지 않으면 positive label 설정, threshold, 또는 데이터 정렬이 틀린 경우가 많습니다. 이 교차검증 절차는 평가 파이프라인의 기본 안전장치입니다.

### threshold 스윕으로 ROC와 운영 임계값 연결하기
ROC-AUC는 모델 분리 능력을 보여주지만, 실제 운영은 단일 threshold를 선택해야 합니다. 따라서 `0.1` 간격 또는 더 촘촘한 구간으로 threshold를 스윕해 TPR/FPR 변화를 확인하는 단계가 필요합니다.

```python
from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np

y_true = np.array([1,0,1,1,0,0,1,0,1,0])
y_score = np.array([0.91,0.12,0.82,0.45,0.31,0.72,0.88,0.28,0.79,0.21])

fpr, tpr, thresholds = roc_curve(y_true, y_score)
auc = roc_auc_score(y_true, y_score)

best = None
for th in np.linspace(0.1, 0.9, 17):
    pred = (y_score >= th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    tpr_now = tp / (tp + fn)
    fpr_now = fp / (fp + tn)
    score = tpr_now - fpr_now
    if best is None or score > best[0]:
        best = (score, th, tpr_now, fpr_now)

print("AUC:", round(auc, 4))
print("best threshold:", best)
```

여기서 `TPR - FPR` 최대 지점을 임시 후보로 잡고, 비즈니스 비용(오탐 처리 비용, 미탐 손실 비용)을 반영해 최종 threshold를 확정합니다. 즉, ROC는 시각화 도구이면서 동시에 정책 결정 입력값입니다.

### 교차검증 결과를 분포로 보고 불확실성 기록하기
단일 점수는 모델 안정성을 숨깁니다. `StratifiedKFold`로 fold별 점수 분포를 남기면 "성능 평균"뿐 아니라 "성능 흔들림"도 관리할 수 있습니다.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=2000, n_features=20, weights=[0.8, 0.2], random_state=42)
model = LogisticRegression(max_iter=1000)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
print("fold scores:", [round(s, 4) for s in scores])
print("mean/std:", round(scores.mean(), 4), round(scores.std(), 4))
```

표준편차가 큰 모델은 데이터 구간에 따라 성능이 크게 달라질 수 있으므로, 배포 전에 데이터 분할 기준과 샘플링 전략을 재점검해야 합니다. 보고서에는 평균과 함께 분산 정보를 반드시 기록해 의사결정의 근거를 명확히 남겨야 합니다.

## 운영 의사결정을 위한 평가 해석 확장

### 클래스 불균형에서 PR 곡선 확인
불균형 데이터에서는 ROC-AUC만으로 품질을 과대평가할 수 있습니다. 양성 비율이 낮을 때는 precision-recall 곡선을 함께 확인해야 실제 운영 난이도를 반영할 수 있습니다.

```python
from sklearn.metrics import precision_recall_curve, average_precision_score
import matplotlib.pyplot as plt

precision, recall, th = precision_recall_curve(y_true, y_score)
ap = average_precision_score(y_true, y_score)

print("AP:", round(ap, 4))
for i in range(0, len(th), max(1, len(th)//5)):
    print("th=", round(th[i], 3), "precision=", round(precision[i], 3), "recall=", round(recall[i], 3))
```

PR 곡선에서 운영팀이 감당 가능한 precision 구간을 먼저 정하고, 그때의 recall 손실을 확인하는 방식이 현실적입니다. 즉 지표 선택은 수학 문제가 아니라 운영 비용 문제와 연결됩니다.

### 비용 민감 confusion matrix
같은 오탐/미탐이라도 비용이 다르면 최적 모델이 달라집니다. 예를 들어 미탐 비용이 오탐보다 5배 크면 다음처럼 총비용을 계산해 비교할 수 있습니다.

```python
from sklearn.metrics import confusion_matrix

cost_fp = 1
cost_fn = 5

pred = (y_score >= 0.42).astype(int)
tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()

total_cost = fp * cost_fp + fn * cost_fn
print({"fp": int(fp), "fn": int(fn), "cost": int(total_cost)})
```

평가 보고서에 이 비용 지표를 함께 두면 모델 교체 기준이 명확해집니다. "AUC가 더 높다"는 주장보다 "월간 예상 손실을 18% 줄인다"는 근거가 훨씬 강합니다.

### 캘리브레이션 확인 루틴
점수 기반 의사결정에서는 확률 신뢰성이 중요합니다. 예측확률이 0.8인 샘플 집합에서 실제 양성 비율이 0.8에 근접하는지 확인해야 합니다.

```python
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=10)
for p_hat, p_real in zip(prob_pred, prob_true):
    print(round(p_hat, 3), round(p_real, 3), round(p_real - p_hat, 3))
```

차이가 큰 구간은 후처리 보정 대상입니다. Platt scaling이나 isotonic regression 적용 전후를 같은 표로 기록하면, 확률 품질이 실제로 개선되었는지 검증 가능합니다.

## 처음 질문으로 돌아가기

- **모델 배포 전에 어떤 평가 정보를 한곳에 모아야 할까요?**
  - 본문의 기준은 평가 리포트 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **평가 리포트와 Model Card는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **임계값, 슬라이스, 재현성 정보는 왜 빠지면 안 될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- **평가 리포트 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google — Model Cards](https://modelcards.withgoogle.com/about)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [MLOps — Production ML guide](https://ml-ops.org/)

Tags: ModelEvaluation, Reporting, ModelCard, Reproducibility, scikit-learn
