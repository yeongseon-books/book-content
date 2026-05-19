---
series: model-evaluation-101
episode: 6
title: ROC와 AUC 이해하기
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

# ROC와 AUC 이해하기

이 글은 Model Evaluation 101 시리즈의 6번째 글입니다.

ROC와 AUC는 임계값을 아직 고정하지 않았을 때 후보 모델을 비교하는 데 유용합니다. 하지만 issue #772가 정확히 짚었듯이 기존 글의 코드는 `ko/06-roc-and-auc.md:84-115`에서 `thr[:3]`, AUC, PR-AUC, `FPR<=0.05` 조회까지만 보여 주고 끝났습니다. 즉 **곡선 요약에서 실제 운영 결정으로 착지하지 못한 것**입니다.

이번 글은 그 마지막 단계를 보강합니다. ROC-AUC를 순위화 능력의 요약으로 읽고, 같은 데이터에서 PR-AUC 차이까지 확인한 뒤, 실제로 `FPR <= 0.05` 예산 아래에서 어떤 임계값을 고를지, 그때의 혼동 행렬과 정밀도·재현율·간단한 비용은 얼마인지까지 연결하겠습니다.

## 이 글이 답하는 질문

- ROC-AUC와 PR-AUC가 왜 같은 데이터에서 다른 온도로 들릴까요?
- `FPR <= 0.05` 같은 정책 제약은 실제 임계값 선택으로 어떻게 연결될까요?
- AUC가 괜찮아 보여도 어떤 조건에서 “아직 배포 준비가 안 됨” 결론이 나올까요?

## 이 장의 최종 질문

이번 장의 질문은 단순합니다.

> AUC가 괜찮아 보일 때, 실제 배포 임계값에서는 어떤 손해를 감수하게 될까요?

이 질문에 답하지 못하면 ROC-AUC는 “좋아 보이는 요약 숫자”에서 멈춥니다. 이 질문까지 답해야 03~06장의 결정 메트릭 흐름이 완성됩니다.

## 한눈에 보는 멘탈 모델

![점수 순위에서 ROC와 PR 비교로 이어지는 평가 흐름](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/06/06-01-concept-at-a-glance.ko.png)

*점수 순위에서 ROC와 PR 비교로 이어지는 평가 흐름*

ROC와 PR은 둘 다 **점수 순위**에서 출발합니다. 하지만 배포는 결국 하나의 임계값에서 일어나므로, 곡선은 마지막에 다시 혼동 행렬과 비용으로 내려와야 합니다.

## 곡선 요약에서 운영 선택까지 가는 코드

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
)
from sklearn.model_selection import train_test_split

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
    X,
    y,
    test_size=0.3,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

fpr, tpr, thresholds = roc_curve(y_test, proba)
print("ROC-AUC:", round(roc_auc_score(y_test, proba), 3))
print("PR-AUC:", round(average_precision_score(y_test, proba), 3))

target_fpr = 0.05
idx = max(i for i, value in enumerate(fpr) if value <= target_fpr)
threshold = thresholds[idx]
pred = (proba >= threshold).astype(int)

cm = confusion_matrix(y_test, pred)
tn, fp, fn, tp = cm.ravel()
precision = precision_score(y_test, pred, zero_division=0)
recall = recall_score(y_test, pred, zero_division=0)
decision_cost = fp * 1 + fn * 10

print("chosen threshold:", round(float(threshold), 3))
print("FPR:", round(fp / (fp + tn), 3))
print("precision:", round(precision, 3))
print("recall:", round(recall, 3))
print("confusion matrix:", cm.tolist())
print("cost (FP=1, FN=10):", decision_cost)
```

예상 결과는 다음과 같습니다.

```text
ROC-AUC: 0.819
PR-AUC: 0.463
chosen threshold: 0.141
FPR: 0.049
precision: 0.352
recall: 0.507
confusion matrix: [[1355, 70], [37, 38]]
cost (FP=1, FN=10): 440
```

## 먼저 읽어야 할 첫 번째 결론: ROC-AUC와 PR-AUC는 같은 얘기가 아닙니다

이 데이터의 ROC-AUC는 **0.819**라서 꽤 괜찮아 보입니다. 하지만 PR-AUC는 **0.463**입니다. 베이스레이트가 낮은 문제에서는 바로 이 차이가 중요합니다. ROC-AUC는 양성과 음성의 순위 분리를 요약하고, PR-AUC는 실제 양성을 얼마나 믿을 만하게 끌어올리는지에 더 민감합니다.

즉 “ROC-AUC가 좋으니 배포 가능하다”는 결론은 너무 빠릅니다. PR-AUC를 같이 보면 양성 탐지 품질이 기대만큼 강하지 않을 수 있다는 경고를 받습니다.

## FPR 예산 아래에서 임계값을 고르면 무슨 일이 생길까요?

운영 정책을 `FPR <= 0.05`로 둔다고 가정하면, 이 예제에서 선택되는 임계값은 **0.141**입니다. 이 지점의 결과는 다음과 같습니다.

- 정밀도: **0.352**
- 재현율: **0.507**
- 혼동 행렬: `[[1355, 70], [37, 38]]`

즉 거짓 양성 비율 예산은 지켰지만, 실제 양성의 절반가량만 잡았습니다. ROC 곡선 위에서 보던 한 점이 이제 실제 운영 비용으로 번역된 셈입니다.

## 임계값 후보를 나란히 놓고 비교해 보겠습니다

| 임계값 | FPR | 정밀도 | 재현율 | 실무 해석 |
| --- | ---: | ---: | ---: | --- |
| 0.10 | 0.081 | 0.275 | 0.587 | 재현율은 높지만 FPR 예산 5%를 넘겨 정책 위반입니다. |
| 0.141 | 0.049 | 0.352 | 0.507 | FPR 예산을 간신히 지키는 최대 재현율 운영점입니다. |
| 0.20 | 0.023 | 0.500 | 0.440 | 더 보수적이며 정밀도는 오르지만 양성 놓침이 늘어납니다. |

이 표가 중요한 이유는 “곡선이 예쁘다”는 느낌을 실제 선택지 비교로 바꿔 주기 때문입니다.

## 간단한 비용 함수까지 붙이면 더 명확해집니다

위 코드에서는 `FP=1`, `FN=10`이라는 매우 단순한 비용 가정을 두었습니다. 이때 선택된 임계값 0.141의 비용은 **440**입니다.

- false positive 70건 × 1 = 70
- false negative 37건 × 10 = 370
- 총 비용 = 440

흥미로운 점은 임계값 0.10이 총비용 **426**으로 더 낮아 보일 수 있다는 점입니다. 하지만 그 임계값은 `FPR=0.081`이라 운영 정책을 위반합니다. 즉 **비용 최소화와 정책 제약은 별개**입니다. 배포 기준은 보통 두 가지를 동시에 만족해야 합니다.

## 그래서 이 모델은 배포 가능한가요?

이제 마지막 질문을 던질 수 있습니다.

> `FPR <= 0.05`라는 정책 아래에서 재현율 0.507이면 충분한가요?

만약 팀의 목표가 “양성의 최소 60%는 잡아야 한다”라면, 이 모델은 아직 준비되지 않았습니다. 현재 정책 예산 안에서 얻을 수 있는 재현율이 약 50.7%에 그치기 때문입니다. 즉 이번 장의 결론은 “ROC-AUC 0.819라서 괜찮다”가 아니라 다음 문장에 가깝습니다.

> 현재 모델은 순위화 품질 자체는 나쁘지 않지만, `FPR <= 0.05` 제약 아래에서는 재현율이 0.507에 머문다. 재현율 목표가 더 엄격하다면 모델 개선이나 다른 정책 설계가 먼저 필요하다.

이것이 곡선 요약에서 운영 판단으로 내려오는 마지막 단계입니다.

## 점검 목록

- [ ] ROC-AUC와 PR-AUC를 함께 봅니다.
- [ ] 운영 제약(FPR, 리뷰 용량 등)을 먼저 적습니다.
- [ ] 선택한 임계값의 혼동 행렬을 반드시 남깁니다.
- [ ] 정밀도와 재현율을 같은 문단에 함께 씁니다.
- [ ] 가능하면 간단한 비용 함수로 정책 제약과 함께 비교합니다.

## 정리

ROC와 AUC는 임계값을 고르기 전 후보 모델의 순위화 능력을 비교하는 데 유용합니다. 하지만 진짜 배포 판단은 항상 **하나의 임계값, 하나의 혼동 행렬, 하나의 비용 가정**으로 내려와야 합니다. 이렇게 해서 03장의 베이스라인 검토, 04장의 정밀도·재현율 운영점, 05장의 F1 요약 한계를 지나, 06장에서 최종 운영 판단까지 이어지는 메트릭 서사가 완성됩니다.

<!-- toc:begin -->
- [모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [정확도의 한계](./03-limits-of-accuracy.md)
- [정밀도와 재현율](./04-precision-and-recall.md)
- [F1 점수](./05-f1-score.md)
- **ROC와 AUC 이해하기 (현재 글)**
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [scikit-learn — roc_curve](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
- [scikit-learn — roc_auc_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [Wikipedia — ROC curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)

Tags: ModelEvaluation, ROC, AUC, PRCurve, scikit-learn
