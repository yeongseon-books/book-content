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

이 글은 Model Evaluation 101 시리즈의 4번째 글입니다.

issue #772는 이 장이 다른 장들과 비슷한 리듬으로 반복된다고 지적했습니다. 실제로 `ko/04-precision-and-recall.md:43-68`은 “왜 중요한가 → 멘탈 모델 → 핵심 용어” 설명에 머무르고, 운영자가 가장 먼저 던져야 할 질문인 **임계값을 내리면 무엇이 늘고, 올리면 무엇을 놓치는가**를 중심에 두지 못했습니다.

그래서 이번 글은 정의 설명보다 **운영 임계값 결정 메모**에 가깝게 다시 씁니다. 정밀도와 재현율은 개념 암기용 용어가 아니라, 알림을 얼마나 더 보내고 얼마나 더 놓칠지를 결정하는 숫자라는 관점으로 읽겠습니다.

![Model Evaluation 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/04/04-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 4장 흐름 개요*

## 먼저 던지는 질문

- 정밀도와 재현율를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 정밀도와 재현율에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 정밀도와 재현율를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 이 글이 답하는 질문

- 임계값을 낮추거나 올릴 때 리뷰 큐와 놓침은 어떻게 달라질까요?
- 운영 기본값으로 0.35 같은 절충점을 고르는 근거는 무엇일까요?
- AP는 왜 유용하지만 배포 임계값을 대신 정해 주지는 못할까요?

## 운영 시나리오 먼저 정하겠습니다

가정은 단순합니다. 이 모델은 사용자의 결제 이상 징후를 탐지해 리뷰 큐로 보내는 시스템입니다.

- **재현율이 낮으면** 실제 이상 거래를 놓칩니다.
- **정밀도가 낮으면** 리뷰 팀이 불필요한 경보를 너무 많이 받습니다.

이 문제에서 중요한 질문은 “정밀도와 재현율이 무엇인가?”보다 다음 문장입니다.

> 임계값을 0.20, 0.35, 0.50, 0.70 중 어디에 둘 때 운영이 버틸 수 있을까요?

## 한눈에 보는 멘탈 모델

임계값을 내리면 더 많은 사례를 양성으로 보게 되어 재현율은 올라가지만, 동시에 거짓 경보도 늘어나 정밀도는 내려가기 쉽습니다. 이 장의 핵심은 이 교환을 숫자와 운영 문장으로 연결하는 데 있습니다.

## 결정 메모를 만드는 코드

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

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
    X,
    y,
    test_size=0.3,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

for threshold in [0.20, 0.35, 0.50, 0.70]:
    pred = (proba >= threshold).astype(int)
    print(
        threshold,
        "precision=", round(precision_score(y_test, pred), 3),
        "recall=", round(recall_score(y_test, pred), 3),
        "flagged=", int(pred.sum()),
        "cm=", confusion_matrix(y_test, pred).tolist(),
    )

print("AP:", round(average_precision_score(y_test, proba), 3))
```

위 코드는 임계값을 바꿀 때 알림 수와 혼동 행렬이 함께 어떻게 바뀌는지 보여 줍니다. 예상 결과는 다음과 같습니다.

```text
0.20 precision= 0.610 recall= 0.735 flagged= 118 cm= [[756, 46], [26, 72]]
0.35 precision= 0.795 recall= 0.633 flagged= 78  cm= [[786, 16], [36, 62]]
0.50 precision= 0.881 recall= 0.531 flagged= 59  cm= [[795, 7],  [46, 52]]
0.70 precision= 0.952 recall= 0.408 flagged= 42  cm= [[800, 2],  [58, 40]]
AP: 0.745
```

## 운영점 표로 읽으면 판단이 빨라집니다

| 임계값 | 정밀도 | 재현율 | 리뷰 큐 크기 | 실무 해석 |
| --- | ---: | ---: | ---: | --- |
| 0.20 | 0.610 | 0.735 | 118건 | 많이 잡지만 오탐이 많아 리뷰 부담이 큽니다. |
| 0.35 | 0.795 | 0.633 | 78건 | 놓침과 오탐이 모두 관리 가능한 절충점입니다. |
| 0.50 | 0.881 | 0.531 | 59건 | 큐는 가벼워지지만 놓침이 눈에 띄게 늘어납니다. |
| 0.70 | 0.952 | 0.408 | 42건 | 경보는 매우 깨끗하지만 실제 이상 거래를 많이 놓칩니다. |

이 표가 중요한 이유는 정밀도와 재현율을 정의가 아니라 **운영 결과**로 번역해 주기 때문입니다. 같은 모델이라도 임계값을 바꾸는 것만으로 전혀 다른 제품이 됩니다.

## 추천 운영점: 왜 0.35를 메모의 기본값으로 둘까요?

이 예제에서는 **0.35**가 가장 설명력 있는 기준점입니다.

- 0.20보다 정밀도가 크게 좋아집니다. `0.610 → 0.795`
- 0.50보다 재현율이 덜 무너집니다. `0.633` 대 `0.531`
- 리뷰 큐도 118건에서 78건으로 줄어 운영 부담이 낮아집니다.

즉 “실제 이상 거래를 너무 많이 놓치지 않으면서도, 리뷰 팀이 감당 가능한 수준으로 경보를 줄이자”라는 메모를 쓰기에 0.35가 자연스럽습니다.

## 정밀도와 재현율은 이렇게 짧게 기억하면 충분합니다

- **정밀도**: 경보를 울린 것 중 진짜가 얼마나 되나요?
- **재현율**: 실제 진짜를 얼마나 놓치지 않았나요?

중요한 것은 정의 자체보다, 이 두 숫자가 임계값과 함께 어떻게 움직이는지입니다. issue #772가 요구한 서사 전환도 바로 여기 있습니다. 이번 장은 “용어 설명”보다 “임계값 메모”가 되어야 합니다.

## 평균 정밀도는 왜 같이 남길까요?

위 코드의 AP는 **0.745**입니다. 이 숫자는 모든 임계값을 훑은 뒤의 요약 점수이므로, 현재 모델이 전반적으로 어느 정도의 정밀도-재현율 곡선을 갖는지 알려 줍니다. 다만 AP만으로는 배포할 임계값이 정해지지 않습니다.

즉 AP는 **후보 모델 비교용 숫자**이고, 실제 운영 메모는 여전히 표와 혼동 행렬에서 나와야 합니다.

## 운영 메모를 문장으로 남기면 이렇게 됩니다

> 결제 이상 징후 탐지 모델에서 임계값 0.35는 정밀도 0.795, 재현율 0.633, 리뷰 큐 78건을 제공합니다. 0.20은 재현율은 높지만 거짓 경보가 많고, 0.50 이상은 큐는 줄지만 놓침이 커집니다. 따라서 현재 운영 기본값은 0.35로 두고, 리스크 이벤트가 증가하는 기간에는 0.20으로 완화하는 방안을 별도 검토합니다.

이런 문장이 있으면 정밀도와 재현율이 단순 지표가 아니라 정책 결정 근거가 됩니다.

## 점검 목록

- [ ] 임계값별 정밀도·재현율 표를 만듭니다.
- [ ] 리뷰 큐 크기나 후속 작업량을 함께 적습니다.
- [ ] 혼동 행렬로 놓침과 오탐을 동시에 확인합니다.
- [ ] AP를 후보 모델 비교용 숫자로만 사용합니다.

## 정리

정밀도와 재현율은 정의보다 **운영점 선택**에서 가치가 드러납니다. 임계값을 바꿀 때 어떤 실수가 늘고 줄어드는지 메모 형식으로 남겨야 실제 의사결정에 쓸 수 있습니다. 다음 글에서는 이렇게 드러난 정밀도-재현율 교환을 하나의 숫자로 압축한 F1을 다루되, 그 요약이 무엇을 숨기는지도 함께 봅니다.

## 처음 질문으로 돌아가기

- **정밀도와 재현율를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 먼저 확인할 경계는 임계값을 움직였을 때 리뷰 큐 부담과 놓침 비용이 어떻게 바뀌는지입니다. 이 글이 결제 이상 징후 탐지 시나리오를 둔 이유도, 정밀도와 재현율을 정의가 아니라 운영 선택으로 읽기 위해서입니다.
- **정밀도와 재현율에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제에서는 0.20, 0.35, 0.50, 0.70 네 임계값에서 정밀도, 재현율, `flagged` 건수, 혼동 행렬을 함께 비교했습니다. 특히 0.35가 `precision 0.795`, `recall 0.633`, 리뷰 큐 78건으로 절충점이 된다는 점이 핵심 신호입니다.
- **정밀도와 재현율를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - AP 같은 요약 점수만 보고 배포 임계값까지 자동으로 정해졌다고 착각하는 실패를 막아야 합니다. 본문이 강조했듯 AP는 후보 모델 비교용이고, 실제 배포 판단은 임계값별 혼동 행렬과 운영 메모에서 내려야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- **정밀도와 재현율 (현재 글)**
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html)
- [scikit-learn — recall_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn — precision_recall_curve example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Precision, Recall, ConfusionMatrix, scikit-learn
