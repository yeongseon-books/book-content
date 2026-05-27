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

정확도는 계산이 쉽고 설명도 편하지만, 그래서 오히려 너무 일찍 결론을 내리게 만드는 지표입니다. issue #772가 지적한 핵심도 여기에 있습니다. 기존 글은 정확도의 한계를 설명했지만, 실제 판단 순서인 베이스레이트 → 더미 기준선 → 소수 클래스 재현율 → 균형 정확도 → 최종 리뷰 흐름으로 독자를 끌고 가지 못했습니다.

이 글은 Model Evaluation 101 시리즈의 3번째 글입니다.

이번 글에서는 정확도를 맨 앞 숫자가 아니라 **마지막 확인 숫자**로 다루겠습니다. 특히 `ko/03-limits-of-accuracy.md:64-69,115-131`에서 약했던 부분을 보강해, 높은 정확도가 실제 개선인지 아니면 다수 클래스가 만든 착시인지 운영자 관점에서 판정하는 절차로 재구성하겠습니다.

![Model Evaluation 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/03/03-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 3장 흐름 개요*

## 먼저 던지는 질문

- 더미 기준선 95.36%와 모델 정확도 96.08%가 거의 비슷한데, 왜 이 모델을 바로 좋다고 말하면 안 될까요?
- 혼동 행렬에서 양성 58개 중 47개를 놓쳤다는 사실이 정확도 96.08%보다 더 중요한 이유는 무엇일까요?
- `minority recall 0.1897`과 `balanced accuracy 0.5940`를 함께 보면 보고서 첫 줄에 어떤 숫자를 올려야 할까요?

## 이 글이 답하는 질문

- 더미 기준선보다 약간 높은 정확도는 언제 의미가 약할까요?
- 소수 클래스 재현율과 균형 정확도는 정확도의 착시를 어떻게 벗겨 낼까요?
- 최종 보고서에서 정확도를 대표 숫자로 써도 되는지 어떻게 판단할까요?

## 이번 글의 판단 순서

정확도 해석은 다음 다섯 단계로 고정해 두는 편이 안전합니다.

1. **베이스레이트 확인**: 양성 비율이 얼마나 낮은지 먼저 봅니다.
2. **더미 기준선 비교**: 아무것도 학습하지 않은 모델이 이미 몇 점인지 확인합니다.
3. **소수 클래스 재현율 확인**: 정말 중요한 양성을 얼마나 놓치는지 봅니다.
4. **균형 정확도 추가**: 다수 클래스와 소수 클래스를 공평하게 평균 냅니다.
5. **정확도 보고 여부 결정**: 위 네 단계를 통과한 뒤에만 정확도를 요약 숫자로 남깁니다.

이 순서를 거꾸로 읽으면 `acc 96%` 같은 숫자에 속기 쉽습니다. 이 순서를 지키면 같은 96%라도 “실제 개선”과 “다수 클래스 안락함”을 구분할 수 있습니다.

## 한눈에 보는 멘탈 모델

핵심은 간단합니다. 클래스 비율이 크게 기울어져 있으면 정확도는 바로 읽는 숫자가 아니라, 다른 점검을 마친 뒤에만 참고할 수 있는 숫자입니다.

## 한 번에 끝내는 진단 코드

아래 코드는 정확도를 해석할 때 필요한 순서를 한 번에 보여 줍니다.

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
)
from sklearn.model_selection import train_test_split

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
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42,
)

dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

print("base rate:", round(y.mean(), 4))
print("dummy accuracy:", round(dummy.score(X_test, y_test), 4))
print("model accuracy:", round(accuracy_score(y_test, pred), 4))
print("minority recall:", round(recall_score(y_test, pred), 4))
print("balanced accuracy:", round(balanced_accuracy_score(y_test, pred), 4))
print("confusion matrix:\n", confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, digits=4))
```

예상 해석은 다음과 같습니다.

```text
base rate: 0.0468
dummy accuracy: 0.9536
model accuracy: 0.9608
minority recall: 0.1897
balanced accuracy: 0.5940
confusion matrix:
[[1190    2]
 [  47   11]]
```

정확도만 보면 96.08%라서 꽤 좋아 보입니다. 하지만 이 숫자를 더미 기준선 95.36%와 나란히 두는 순간 해석이 달라집니다. **정확도 이득은 0.72%포인트**뿐인데, 실제 양성 58개 중 47개를 놓쳤기 때문입니다.

## 1단계 — 베이스레이트를 먼저 보면 무엇이 달라질까요?

양성 비율이 4.68%라는 뜻은, 아무 생각 없이 대부분을 음성으로 찍어도 높은 정확도를 얻기 쉽다는 의미입니다. 즉 이 문제에서 정확도는 모델 실력보다 데이터 분포의 도움을 많이 받습니다.

이 한 줄이 중요한 이유는 이후 숫자들의 기준점을 미리 정해 주기 때문입니다. 베이스레이트가 50:50이 아니라는 사실을 먼저 알면, `96%`라는 숫자를 보는 순간에도 “실력”보다 “분포”를 먼저 의심하게 됩니다.

## 2단계 — 더미 기준선과의 비교가 왜 필수일까요?

`DummyClassifier(strategy="most_frequent")`는 모든 사례를 다수 클래스로 예측합니다. 여기서도 이 더미는 이미 **95.36% 정확도**를 냅니다. 즉 정확도만 놓고 보면 실제 모델은 겨우 조금 더 나아졌을 뿐입니다.

실무에서 이 비교가 빠지면 팀은 다음처럼 착각하기 쉽습니다.

- 잘못된 해석: `96%니까 충분히 좋다.`
- 올바른 해석: `기준선이 95.36%인데 96.08%면, 정확도 개선은 작다. 다른 지표를 바로 확인해야 한다.`

정확도는 더미와의 차이까지 붙여 읽어야 의미가 생깁니다.

## 3단계 — 소수 클래스 재현율이 사실상 본체입니다

이 예제의 소수 클래스 재현율은 **0.1897**입니다. 실제 양성 중 18.97%만 잡았다는 뜻입니다. 다시 말해 양성 100건이 들어오면 약 81건을 놓치는 모델입니다.

이 숫자가 중요한 이유는 정확도가 감추는 실패를 바로 드러내기 때문입니다. 혼동 행렬의 아래 행을 보면 실제 양성 58개 중 11개만 맞히고 47개를 놓쳤습니다. 사기 탐지, 희귀 질환 분류, 장애 경보처럼 놓침이 비싼 문제라면 이 모델은 아직 보고서 첫 줄에 올릴 상태가 아닙니다.

## 4단계 — 균형 정확도가 공평한 요약을 제공합니다

균형 정확도는 각 클래스 재현율의 평균입니다. 이 예제에서는 **0.5940**으로, 정확도 0.9608과 전혀 다른 그림을 보여 줍니다. 다수 클래스는 거의 완벽하게 맞히지만 소수 클래스는 크게 놓치므로, 공평하게 평균 내면 모델의 체감 성능이 급격히 내려갑니다.

이 차이가 바로 issue #772가 요구한 “정확도의 판단 순서”입니다. 정확도를 그대로 읽지 말고, 소수 클래스 재현율과 균형 정확도로 한번 뒤집어 봐야 합니다.

## 5단계 — 그러면 정확도를 보고서에 써도 될까요?

이제 마지막 질문을 던질 수 있습니다.

> 이 정확도는 실제 성능 향상인가, 아니면 다수 클래스를 편하게 맞힌 결과인가?

이 예제의 답은 후자에 가깝습니다. 정확도를 완전히 버릴 필요는 없지만, 최소한 다음 조건이 붙어야 합니다.

- 더미 기준선 대비 개선 폭을 함께 보고합니다.
- 소수 클래스 재현율을 같은 문단에 함께 둡니다.
- 균형 정확도를 같이 보고합니다.
- 운영에서 놓침 비용이 크다면 정확도를 대표 지표로 쓰지 않습니다.

즉 이 문제에서는 `accuracy=0.9608`보다 `minority recall=0.1897, balanced accuracy=0.5940`가 더 먼저 나와야 합니다.

## 실무 결정 리뷰 템플릿

정확도 검토를 보고서 문장으로 남길 때는 아래처럼 쓰면 됩니다.

> 베이스레이트 4.68% 문제에서 모델 정확도는 96.08%로 더미 기준선 95.36%보다 0.72%포인트 높았습니다. 그러나 소수 클래스 재현율은 18.97%, 균형 정확도는 59.40%에 그쳤으므로, 이 모델은 “정확도 개선”보다 “양성 놓침 위험”이 더 큰 상태로 판단합니다.

이 문장 구조를 익혀 두면, 정확도 하나만 강조하는 보고서를 자연스럽게 교정할 수 있습니다.

## 점검 목록

- [ ] 베이스레이트를 먼저 확인합니다.
- [ ] 더미 기준선과 정확도를 나란히 비교합니다.
- [ ] 소수 클래스 재현율을 별도 숫자로 적습니다.
- [ ] 균형 정확도를 함께 보고합니다.
- [ ] 정확도를 대표 지표로 쓸지 마지막에 결정합니다.

## 정리

정확도는 쓸모없는 지표가 아니라 **순서가 중요한 지표**입니다. 베이스레이트와 더미 기준선, 소수 클래스 재현율, 균형 정확도를 거친 뒤에야 비로소 읽을 수 있습니다. 다음 글에서는 이 흐름을 이어 받아, 임계값을 움직일 때 정밀도와 재현율이 어떤 운영 선택으로 연결되는지 봅니다.

## 처음 질문으로 돌아가기

- **더미 기준선 95.36%와 모델 정확도 96.08%가 거의 비슷한데, 왜 이 모델을 바로 좋다고 말하면 안 될까요?**
  - 이 예제의 양성 비율은 4.68%라서 아무것도 학습하지 않은 `DummyClassifier(strategy="most_frequent")`도 이미 95.36% 정확도를 냅니다. 실제 모델의 96.08%는 더미보다 0.72%포인트 높을 뿐이므로, 이 숫자 하나만으로는 성능 향상이라고 결론 내리기 어렵습니다.
- **혼동 행렬에서 양성 58개 중 47개를 놓쳤다는 사실이 정확도 96.08%보다 더 중요한 이유는 무엇일까요?**
  - 혼동 행렬의 아래 행은 실제 양성을 얼마나 건졌는지 직접 보여 주고, 여기서는 58개 중 11개만 맞혀 `minority recall`이 0.1897에 그쳤습니다. 사기 탐지나 희귀 이벤트처럼 놓침 비용이 큰 문제라면, 높은 정확도보다 양성 47건을 놓쳤다는 사실이 더 중요한 운영 신호입니다.
- **`minority recall 0.1897`과 `balanced accuracy 0.5940`를 함께 보면 보고서 첫 줄에 어떤 숫자를 올려야 할까요?**
  - 이 글의 결론은 `accuracy=0.9608`보다 `minority recall=0.1897`과 `balanced accuracy=0.5940`를 먼저 올려야 한다는 사실입니다. 정확도는 더미 대비 개선 폭 0.72%포인트와 함께 보조 숫자로 남기고, 핵심 판단은 양성 놓침 위험이 큰 모델이라는 문장으로 적는 편이 맞습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- **정확도의 한계 (현재 글)**
- 정밀도와 재현율 (예정)
- F1 점수 (예정)
- ROC와 AUC 이해하기 (예정)
- 확률 보정 이해하기 (예정)
- 교차 검증 이해하기 (예정)
- 오류 분석으로 약점 찾기 (예정)
- 평가 리포트 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [scikit-learn — DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- [scikit-learn — accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)
- [scikit-learn — balanced_accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html)
- [Wikipedia — Accuracy paradox](https://en.wikipedia.org/wiki/Accuracy_paradox)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Accuracy, ImbalancedData, BaselineModel, scikit-learn
