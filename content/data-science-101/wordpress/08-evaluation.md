---
title: "바이브코딩을 위한 데이터 사이언스 기초 (8/10): AI 모델의 성능이 진짜 좋은 건지 평가하기"
series: data-science-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DataScience
- AI코딩
seo_description: "바이브코딩 시대, AI 모델의 정확도 숫자에 속지 않는 방법 — precision, recall, F1, ROC AUC를 언제 왜 써야 하는지, 비즈니스 비용을 평가에 반영하는 방법을 정리합니다"
---

# 바이브코딩을 위한 데이터 사이언스 기초 (8/10): AI 모델의 성능이 진짜 좋은 건지 평가하기

이 글은 바이브코딩을 위한 데이터 사이언스 기초 시리즈의 8번째 글입니다.

AI가 만든 사기 탐지 모델이 정확도 99%를 기록했습니다. 대단해 보입니다. 팀에 공유했더니 칭찬이 쏟아졌습니다. 그런데 실제 사기 거래를 실제로 얼마나 잡고 있는지 확인했더니 5%에 불과했습니다. 99%의 거래가 정상 거래이기 때문에 모든 것을 "정상"으로 분류해도 99% 정확도가 나오는 겁니다. 모델이 사실상 아무것도 하지 않는데 성능이 완벽해 보이는 상황입니다.

바이브코딩에서 AI에게 모델 평가를 요청할 때 "정확도(accuracy)"만 확인하면 이런 함정에 빠질 수 있습니다. 문제의 성격에 따라 다른 지표가 필요합니다. 사기 탐지처럼 "놓치는 것"이 더 비싼 문제에서는 Recall이 중요합니다. 스팸 필터처럼 "잘못 알람"이 더 비싼 문제에서는 Precision이 중요합니다.

AI에게 모델 평가를 요청할 때 이 질문을 먼저 해야 합니다: "이 모델에서 어떤 종류의 실수가 더 비싼가?" False Negative(실제 양성을 음성으로 예측)가 비싸면 Recall을, False Positive(실제 음성을 양성으로 예측)가 비싸면 Precision을 주로 봐야 합니다.

AI에게 평가를 요청할 때 "정확도 출력해줘"가 아니라 "이 문제에서 어떤 지표가 왜 중요한지 설명하고, 비즈니스 비용을 고려한 최적 임계값을 찾아줘"라고 요청하면 훨씬 실용적인 결과를 얻을 수 있습니다.

> AI 모델의 정확도 숫자 하나는 거짓말을 할 수 있습니다. 비즈니스 비용을 반영한 지표만이 진실을 말합니다.

---

## 이 글에서 다룰 문제
- 정확도(accuracy) 99%인 모델이 왜 쓸모없을 수 있을까요?
- Precision과 Recall 중 어떤 것을 더 중요하게 봐야 할까요?
- ROC AUC는 무엇이고 언제 쓰나요?
- 비즈니스 비용을 모델 평가에 어떻게 반영할 수 있을까요?
- AI에게 모델 평가를 요청할 때 어떤 지시를 추가해야 할까요?

## 분류 지표 선택 가이드

| 문제 유형 | 더 비싼 실수 | 주요 지표 | 예시 |
|---|---|---|---|
| 사기 탐지 | 사기를 놓침 (FN) | Recall 우선 | 암 진단, 이상 거래 탐지 |
| 스팸 필터 | 정상 메일을 스팸으로 (FP) | Precision 우선 | 이메일 분류, 광고 차단 |
| 이탈 예측 캠페인 | 이탈할 사람을 놓침 (FN) | Recall + F1 | 리텐션 캠페인 대상 선정 |
| 추천 시스템 | 관련 없는 것을 추천 (FP) | Precision + F1 | 상품 추천, 콘텐츠 추천 |
| 의료 스크리닝 | 환자를 놓침 (FN) | Recall 최우선 | 암 1차 스크리닝 |

## AI에게 모델 평가를 더 잘 요청하는 방법

```python
# 좋지 않은 요청
"""
이 모델 정확도 계산해줘
"""

# 비즈니스 비용을 반영한 요청 (좋음)
"""
이탈 예측 모델 평가를 해줘. 다음 내용을 포함해줘:
- 이 문제에서 False Negative(이탈할 사람을 놓침)의 비용이 False Positive의 5배임
- confusion matrix, precision, recall, F1, ROC AUC 모두 계산
- 비용 함수 (5*FN + 1*FP)를 최소화하는 최적 임계값 찾기
- 불균형 데이터라면 accuracy 대신 F1이나 AUC 사용 이유 설명
"""

from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)
import numpy as np

# 기본 지표
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("=== 기본 지표 ===")
print(classification_report(y_test, y_pred))

# ROC AUC
print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")

# 비즈니스 비용 반영
cm = confusion_matrix(y_test, y_pred)
TN, FP, FN, TP = cm.ravel()
# FN 비용이 FP의 5배인 경우
business_cost = 5 * FN + 1 * FP
print(f"\n비즈니스 비용 (5*FN + 1*FP): {business_cost}")
print(f"FP: {FP}, FN: {FN}")

# 최적 임계값 찾기 (validation set 사용)
thresholds = np.linspace(0.1, 0.9, 17)
costs = []
for t in thresholds:
    pred = (y_proba >= t).astype(int)
    cm_t = confusion_matrix(y_test, pred)
    if cm_t.shape == (2, 2):
        TN_t, FP_t, FN_t, TP_t = cm_t.ravel()
        costs.append((t, 5 * FN_t + 1 * FP_t))

best_t, best_cost = min(costs, key=lambda x: x[1])
print(f"\n최적 임계값: {best_t:.2f}, 최소 비용: {best_cost}")
```

## 불균형 데이터에서 accuracy가 거짓말하는 이유

데이터의 99%가 정상 거래이고 1%가 사기 거래라면:

| 모델 | 모든 것을 "정상" 예측 | 실제 이탈 예측 모델 |
|---|---|---|
| Accuracy | 99% | 97% |
| Recall (사기 탐지율) | 0% | 70% |
| Precision | N/A | 85% |
| 비즈니스 가치 | 없음 | 있음 |

Accuracy만 보면 "모든 것을 정상으로 분류하는 모델"이 이탈 예측 모델보다 더 좋아 보입니다. 하지만 실제로는 쓸모가 없습니다.

## Before / After

**Before**: AI에게 사기 탐지 모델을 만들어달라고 했더니 정확도 99%가 나왔습니다. 대단하다고 생각했는데, 나중에 확인해보니 Recall이 3%였습니다. 실제 사기 거래의 97%를 놓치고 있었습니다.

**After**: AI에게 "이 문제에서 FN 비용이 FP의 5배입니다. 비용 함수를 최소화하는 임계값을 찾고, Recall을 주 지표로 보되 Precision이 0.7 아래로 내려가면 안 됩니다"라고 요청했습니다. 비즈니스에 실제로 유용한 모델을 얻었습니다.

## 바이브코딩할 때 자주 하는 실수
| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| Accuracy만 확인 | 불균형 데이터에서 오해 | precision, recall, F1, AUC 함께 확인 |
| 비즈니스 비용 무시 | 점수는 좋지만 실무에서 불만 | FP/FN 비용 반영한 지표 사용 |
| 임계값을 기본 0.5로 사용 | 비즈니스 요구와 다를 수 있음 | 최적 임계값 탐색 요청 |
| 테스트셋으로 임계값 조정 | 데이터 누수의 일종 | validation set에서만 임계값 조정 |

## AI에게 데이터 분석 요청하는 팁

AI에게 모델 평가를 요청할 때 이 요소들을 포함하면 좋습니다:

1. **비즈니스 비용 맥락**: "FN이 FP보다 X배 비쌉니다"
2. **불균형 데이터 여부**: "클래스 비율이 99:1입니다"
3. **주 지표와 가드레일**: "Recall을 최우선으로 하되 Precision >= 0.7 조건"
4. **임계값 최적화**: "비용 함수를 최소화하는 임계값을 찾아줘"
5. **복수 지표**: "accuracy, precision, recall, F1, ROC AUC 모두 출력"

## 운영 체크리스트
- [ ] 이 문제에서 FP와 FN 중 어떤 것이 더 비싼지 확인합니다
- [ ] Accuracy 외에 precision, recall, F1을 함께 확인합니다
- [ ] 불균형 데이터라면 ROC AUC를 주 지표로 사용합니다
- [ ] 비즈니스 비용을 반영한 최적 임계값을 찾습니다
- [ ] 임계값 조정은 validation set에서만 합니다
- [ ] 주 지표와 가드레일 지표를 분리해서 관리합니다

## 처음 질문으로 돌아가기

"AI 모델 정확도 99%가 진짜 좋은 건지 어떻게 알 수 있나요?"

정확도 숫자 하나로는 알 수 없습니다. 먼저 베이스라인(가장 많은 클래스만 예측)과 비교하고, 비즈니스 문제에 맞는 지표(Recall 또는 Precision)를 확인하고, 비즈니스 비용을 반영한 임계값에서의 성능을 검토해야 합니다. "99%니까 좋다"가 아니라 "이 모델이 실제 비즈니스 비용을 줄여주는가"가 진짜 질문입니다.

## 정리

AI 모델의 성능은 정확도 하나로 판단할 수 없습니다. 비즈니스 문제에서 어떤 실수가 더 비싼지 파악하고, 그에 맞는 지표를 선택하고, 비즈니스 비용을 반영한 최적 임계값을 찾는 것이 진짜 평가입니다. AI에게 이 과정을 포함한 평가를 요청하면 정확도 숫자에 속지 않을 수 있습니다. 다음 글에서는 AI가 준 결과를 어떻게 비즈니스에 설명하는지 다룹니다.

## 참고 자료
### 공식 문서
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
### 관련 시리즈
- [Machine Learning 101](../../machine-learning-101/ko/)
- [Statistics 101](../../statistics-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 데이터 사이언스 기초 (1/10): AI에게 데이터 분석 맡기기 전에 알아야 할 것](./01-what-is-data-science.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (2/10): 비즈니스 질문을 데이터 질문으로 바꾸는 법](./02-problem-to-data-problem.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (3/10): AI에게 줄 데이터를 어떻게 모을지](./03-data-collection.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (4/10): AI가 더러운 데이터로 분석하면 결과도 더럽다](./04-data-cleaning.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (5/10): AI에게 EDA 시키기 전에 알아야 할 것](./05-exploratory-data-analysis.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (6/10): AI가 만든 차트가 오해를 부를 때](./06-visualization.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (7/10): AI가 모델을 골라줬는데 맞는 선택인지](./07-modeling.md)
- **바이브코딩을 위한 데이터 사이언스 기초 (8/10): AI 모델의 성능이 진짜 좋은 건지 평가하기 (현재 글)**
- [바이브코딩을 위한 데이터 사이언스 기초 (9/10): AI가 준 결과를 비즈니스에 설명하려면](./09-result-interpretation.md)
- [바이브코딩을 위한 데이터 사이언스 기초 (10/10): AI와 함께 데이터 프로젝트 처음부터 끝까지](./10-data-project-end-to-end.md)
<!-- toc:end -->

Tags: 바이브코딩, DataScience, AI코딩, Evaluation, Metrics
