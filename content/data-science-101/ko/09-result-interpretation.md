---
series: data-science-101
episode: 9
title: "Data Science 101 (9/10): 결과 해석"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - Interpretation
  - Storytelling
  - Decision
  - Beginner
seo_description: 숫자 결과에 맥락과 불확실성을 더해 과장 없는 의사결정 문장으로 바꾸는 5단계 해석 프레임워크를 상세히 정리합니다.
last_reviewed: '2026-05-15'
---

# Data Science 101 (9/10): 결과 해석

이 글은 Data Science 101 시리즈의 아홉 번째 글입니다.

분석이나 모델링이 끝났다고 해서 일이 끝난 것은 아닙니다. 오히려 가장 어려운 단계가 남아 있을 때가 많습니다. 숫자를 어떻게 읽고, 어디까지 주장하고, 어떤 행동으로 연결할지 정하는 단계입니다. 여기서 결과를 과장하면 잘못된 결정을 부르고, 반대로 지나치게 약하게 말하면 실제로 잡을 수 있었던 기회를 놓치게 됩니다.

좋은 해석은 숫자를 더 크게 보이게 만드는 일이 아닙니다. 숫자 위에 맥락과 불확실성을 겹쳐서, 팀이 과신하지도 않고 주저앉지도 않게 만드는 일입니다. 이 글에서는 결과를 결정으로 옮기는 기본 흐름을 정리하겠습니다.

## 먼저 던지는 질문

- 숫자 결과를 어떻게 의사결정 문장으로 바꿀 수 있을까요?
- 왜 숫자와 맥락은 항상 함께 적어야 할까요?
- 효과 크기와 불확실성은 왜 동시에 보고해야 할까요?

## 큰 그림

![Data Science 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/09/09-01-concept-at-a-glance.ko.png)

*Data Science 101 9장 흐름 개요*

결과 해석를 운영 시스템 속에서 올바르게 배치하려면 어떤 경계에서 무엇을 입력받고, 어디에서 검증하며, 어떤 신호를 남겨야 하는지 먼저 봐야 합니다.

> 결과 해석의 핵심은 기능 이름이 아니라, 입력을 받는 경계에서 결과를 내보내는 경계까지 어떤 기준으로 데이터를 검증하고 처리할 것인가를 명확히 정하는 데 있습니다.

## 이 글에서 배우는 내용

- 결과에서 결정으로 이어지는 5단계 흐름
- 숫자와 함께 불확실성을 보고하는 법
- 해석을 왜곡하는 다섯 가지 인지 함정
- 5단계 해석 실습 흐름
- 보고서에서 자주 생기는 실수 다섯 가지

## 왜 중요한가

해석이 과장되면 의사결정은 자신만만해지지만 틀릴 가능성이 커집니다. 해석이 지나치게 약하면 팀은 계속 미루기만 하고 아무 행동도 하지 못합니다. 결국 중요한 것은 숫자를 숨기지 않고, 불확실성도 숨기지 않으면서도 행동 가능한 결론을 만드는 일입니다.

해석 단계는 기술보다 태도가 더 중요할 때가 많습니다. 유리한 결과만 선택적으로 보여 주지 않고, 불확실성을 부끄러워하지 않으며, 마지막에 무엇을 할지까지 분명히 적는 태도가 필요합니다.

> 좋은 해석은 과장하지 않지만, 그래도 결정을 가능하게 만듭니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Confidence Interval**: 추정치 주변의 불확실성 범위입니다.
- **Effect Size**: 차이의 크기 자체를 뜻합니다.
- **Practical Significance**: 통계적으로뿐 아니라 비즈니스적으로 의미 있는 차이인지 보는 관점입니다.
- **Cherry-picking**: 유리한 결과만 골라 보고하는 왜곡입니다.
- **Survivorship Bias**: 살아남은 사례만 보고 실패한 사례를 놓치는 편향입니다.

## Before / After

**Before**: “정확도가 5% 올랐습니다”라고만 말합니다. 어디서, 누구에게, 얼마나 안정적으로 오른 것인지 알 수 없습니다.

**After**: “유료 사용자 6만 명 기준, 7일 평균 정확도가 89%에서 91%로 상승했고 95% 신뢰구간은 ±0.8%였습니다”처럼 씁니다. 이제야 숫자가 읽히기 시작합니다.

## 실습: 5단계 해석

### 1단계 — 숫자를 정확히 적기

```text
A/B test result: conversion 3.2% (control) vs 3.6% (variant)
n = 50,000 per arm
```

먼저 바뀐 숫자를 정확히 적습니다. 모호한 요약보다 원래 수치를 분명히 쓰는 편이 낫습니다. 표본 크기도 함께 써야 무게를 판단할 수 있습니다.

### 2단계 — 신뢰구간 함께 적기

```text
delta = +0.4pp (95% CI: +0.2pp ~ +0.6pp)
```

불확실성을 함께 적는 순간 결과는 훨씬 정직해집니다. 신뢰구간은 얼마나 불안정한가를 수치로 보여 주는 좋은 도구입니다.

### 3단계 — 효과 크기 보기

```text
relative lift = +12.5%
```

유의하다는 말만으로는 부족합니다. 차이가 실제로 얼마나 큰지, 비즈니스적으로 행동할 만한 크기인지 확인해야 합니다.

### 4단계 — 맥락 추가하기

```text
campaign window: 2 weeks; segment: paid users; device: desktop only
```

숫자는 맥락 없이 거의 의미가 없습니다. 어떤 기간인지, 어떤 세그먼트인지, 어떤 환경인지 적어야 과도한 일반화를 막을 수 있습니다.

### 5단계 — 의사결정으로 닫기

```text
Decision: roll out to 100% paid desktop users; monitor for 2 more weeks.
```

좋은 보고서는 마지막에 행동을 제안합니다. 무엇을 할지, 누가 볼지, 언제 다시 검토할지까지 쓰면 결과가 실행으로 이어집니다.

**Expected output:** 숫자, 신뢰구간, 대상 세그먼트, 권장 행동이 한 문단 안에 함께 적힌 결정 문장을 남깁니다.

## 이 코드에서 먼저 봐야 할 점

- 숫자와 맥락은 항상 한 쌍으로 움직여야 합니다.
- 신뢰구간은 의사결정 위험을 숫자로 드러내 줍니다.
- 보고서는 결정 문장으로 닫힐 때 비로소 실무 산출물이 됩니다.

## 자주 하는 실수 다섯 가지

1. **p-value만 보는 실수**: 효과 크기가 작으면 실무 의미가 약할 수 있습니다.
2. **한 세그먼트 결과를 전체에 일반화하는 실수**: 분산과 차이를 놓칩니다.
3. **좋은 결과만 보고하는 실수**: 전형적인 cherry-picking입니다.
4. **불확실성을 숨기는 실수**: 팀을 과신하게 만듭니다.
5. **결정 문장 없이 보고서를 끝내는 실수**: 결국 아무 행동도 일어나지 않습니다.

## 실무에서는 이렇게 나타납니다

실무 데이터 팀은 주간 리뷰에서 숫자 → 맥락 → 신뢰구간 → 결정 순서를 템플릿처럼 씁니다. 어떤 팀은 분석 전에 가설을 미리 적어 두는 pre-registration 습관을 두어 cherry-picking을 줄입니다. 해석의 품질은 종종 개인 역량보다 팀 템플릿에 더 크게 좌우됩니다.

## 시니어는 이렇게 생각합니다

- 불확실성을 말하는 것을 부끄러워하지 않습니다.
- 결과는 항상 결정 문장으로 닫습니다.
- p-value보다 effect size를 더 유심히 봅니다.
- 세그먼트를 나눠 분산을 드러냅니다.
- 리뷰 템플릿 자체를 팀 자산으로 만듭니다.

## 체크리스트

- [ ] 신뢰구간을 함께 적을 수 있습니다.
- [ ] 효과 크기를 읽을 수 있습니다.
- [ ] 세그먼트별로 나눠 보는 습관이 있습니다.
- [ ] 의사결정 문장을 작성할 수 있습니다.

## 연습 문제

1. 과거 분석 하나를 골라 5단계 흐름으로 다시 해석해 보세요.
2. `p=0.04`지만 효과가 0.1%뿐인 결과를 어떻게 보고할지 적어 보세요.
3. cherry-picking을 막기 위한 팀 규칙 세 가지를 적어 보세요.

## 정리 및 다음 글

결과 해석은 분석을 의사결정으로 옮기는 마지막 다리입니다. 숫자를 더 크게 말하는 것이 아니라, 숫자와 맥락과 불확실성을 함께 보여 준 뒤 행동 가능한 문장으로 닫는 일이 핵심입니다. 다음 글에서는 시리즈 전체를 묶어 하나의 데이터 프로젝트를 처음부터 끝까지 따라가 보겠습니다.

## 실무 확장: 해석 기법 비교와 설명 가능한 결과 작성법

결과 해석 단계에서는 "점수가 좋다"는 표현보다 "왜 그런 판단을 했는지"를 설명하는 능력이 중요합니다. 특히 모델 기반 의사결정에서는 해석 가능성을 확보해야 현업 신뢰를 얻을 수 있습니다. 이 섹션에서는 대표적인 해석 기법을 비교하고, Python으로 최소 설명 리포트를 만드는 방법을 다룹니다.

### 해석 기법 비교표

| 기법 | 설명 단위 | 장점 | 한계 | 권장 사용 상황 |
| --- | --- | --- | --- | --- |
| 계수 기반 해석 | 전역 | 단순, 빠름 | 비선형 모델 한계 | 로지스틱/선형 모델 |
| Permutation Importance | 전역 | 모델 불문 비교 가능 | 상관 피처 영향 | 피처 우선순위 점검 |
| SHAP | 전역 + 개별 | 일관성 높은 기여도 설명 | 계산 비용 | 중요 의사결정 보고 |
| LIME | 개별 | 로컬 설명 직관적 | 샘플링 민감 | 케이스 단위 설명 |

### Python 예시: 중요도와 개별 예측 설명

```python
import pandas as pd
from sklearn.inspection import permutation_importance

# fitted model, X_valid, y_valid 가 이미 준비되었다고 가정
result = permutation_importance(model, X_valid, y_valid, n_repeats=5, random_state=42)
imp = pd.DataFrame({
    "feature": X_valid.columns,
    "importance": result.importances_mean,
}).sort_values("importance", ascending=False)

print(imp.head(10))
```

아래는 SHAP 사용 예시입니다. 환경에 따라 패키지 설치가 필요할 수 있습니다.

```python
import shap

explainer = shap.Explainer(model, X_valid)
sv = explainer(X_valid.iloc[:200])
print("mean_abs_shap_top5")
print(pd.Series(abs(sv.values).mean(axis=0), index=X_valid.columns).sort_values(ascending=False).head())
```

### 해석 문장 템플릿

- 관찰: "위험 예측 상위군은 최근 14일 세션 수 감소 폭이 큽니다."
- 근거: "SHAP 평균 기여도에서 `days_since_last_login`이 가장 큽니다."
- 제한: "모바일 신규 사용자 세그먼트는 샘플 수가 적어 불확실성이 큽니다."
- 결정: "재참여 메시지는 상위군 중 웹 사용자부터 1차 적용합니다."

### 해석 품질 체크포인트

- 효과 크기와 불확실성을 함께 적었는가
- 단일 세그먼트 결과를 전체에 일반화하지 않았는가
- 반례/예외 케이스를 별도로 점검했는가
- 해석 결과가 실제 행동 제안으로 닫히는가
- 다음 검증 실험 계획이 포함되어 있는가

좋은 해석은 설명을 길게 쓰는 것이 아니라, 근거-제약-결정을 한 문맥에서 연결하는 것입니다. 이 구조가 있으면 보고서의 설득력과 실행 가능성이 함께 올라갑니다.

### 보강 메모: 팀 운영 관점에서 꼭 남겨야 할 기록

입문 프로젝트에서는 코드가 돌아가는 것만으로도 큰 성취를 느끼기 쉽습니다. 하지만 실무에서 더 중요한 것은 같은 결과를 팀이 다시 만들 수 있는가입니다. 그래서 본문 실습을 수행한 뒤에는 다음 항목을 반드시 문서로 남기는 습관이 필요합니다.

- 실행 날짜와 데이터 버전
- 사용한 핵심 컬럼 목록과 정의
- 주요 가정(제외한 데이터, 임계값, 기간)
- 결과 해석 시 주의할 제약 조건
- 다음 반복에서 확인할 질문

이 다섯 가지를 기록하면 다음 사이클에서 같은 논의를 처음부터 반복하지 않아도 됩니다. 특히 모델 점수나 차트 결과처럼 숫자가 좋아 보이는 상황일수록 제약 조건을 함께 적는 것이 중요합니다. 수치의 강점과 약점을 함께 남겨야 팀이 과신하지 않고, 반대로 필요한 행동은 빠르게 실행할 수 있습니다.

### 보강 예시: 재현 가능한 결과 패키지 만들기

```python
from pathlib import Path
import json
import datetime as dt

meta = {
    "run_at": dt.datetime.utcnow().isoformat(),
    "dataset": "example_v1",
    "assumptions": [
        "trial users excluded",
        "analysis window = last 30 days",
        "threshold fixed before final test",
    ],
    "next_question": "Which segment shows largest variance next week?",
}

out = Path("artifacts")
out.mkdir(exist_ok=True)
(out / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", out / "run_meta.json")
```

이 코드는 분석 산출물을 실행 메타데이터와 함께 저장하는 가장 작은 예시입니다. 이렇게 작은 기록이 쌓이면 팀 차원의 학습 속도가 크게 올라갑니다. 프로젝트는 한 번의 정답을 찾는 작업이 아니라 반복을 통해 품질을 높이는 작업이기 때문입니다.

### 추가 보강: 다음 반복에서 바로 쓰는 점검 질문

- 이번 결과를 다음 주에도 같은 방식으로 다시 계산할 수 있는가
- 세그먼트 기준이 바뀌면 결론이 얼마나 달라지는가
- 운영팀이 즉시 실행 가능한 행동 문장으로 정리되었는가

위 세 질문은 기술 난이도와 무관하게 모든 데이터 프로젝트에서 반복적으로 유효합니다. 프로젝트를 끝낼 때 이 질문에 답해 두면 다음 반복 주기의 출발 속도가 훨씬 빨라집니다.

### 마무리 보강: 운영 전 확인 포인트

최종 공유 전에 아래 항목을 마지막으로 점검합니다. 첫째, 결과 수치와 기준 기간이 문장 안에 함께 있는지 확인합니다. 둘째, 독자가 오해할 수 있는 축약 표현을 제거합니다. 셋째, 실행 오너와 재검토 날짜를 명시합니다. 이 세 가지는 글의 길이보다 품질을 크게 좌우하는 요소입니다.

### 최종 보충: 해석 문장 품질 규칙

해석 문장을 작성할 때는 수치, 제약, 행동을 한 문단에 함께 배치합니다. 수치만 있고 제약이 없으면 과신 위험이 커지고, 제약만 있고 행동이 없으면 실행이 멈춥니다. 따라서 한 문단 안에서 세 요소를 동시에 점검하는 습관이 필요합니다.


짧은 결론이라도 수치와 맥락, 다음 행동을 함께 적는 원칙을 지키면 해석 품질이 안정적으로 유지됩니다.

## 처음 질문으로 돌아가기

- **숫자 결과를 어떻게 의사결정 문장으로 바꿀 수 있을까요?**
  - 본문의 기준은 결과 해석를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 숫자와 맥락은 항상 함께 적어야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **효과 크기와 불확실성은 왜 동시에 보고해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- [Data Science 101 (4/10): 데이터 정제](./04-data-cleaning.md)
- [Data Science 101 (5/10): 탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- [Data Science 101 (6/10): 시각화](./06-visualization.md)
- [Data Science 101 (7/10): 모델링](./07-modeling.md)
- [Data Science 101 (8/10): 평가](./08-evaluation.md)
- **결과 해석 (현재 글)**
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)
- [Kahneman — Thinking, Fast and Slow](https://us.macmillan.com/books/9780374533557/thinkingfastandslow)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Microsoft — Trustworthy Online Experiments](https://exp-platform.com/)

Tags: DataScience, Interpretation, Storytelling, Decision, Beginner
