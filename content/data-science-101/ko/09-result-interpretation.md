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

분석이나 모델링이 끝났다고 해서 일이 끝난 것은 아닙니다. 오히려 가장 어려운 단계가 남아 있을 때가 많습니다. 숫자를 어떻게 읽고, 어디까지 주장하고, 어떤 행동으로 연결할지 정하는 단계입니다. 여기서 결과를 과장하면 잘못된 결정을 부르고, 반대로 지나치게 약하게 말하면 실제로 잡을 수 있었던 기회를 놓치게 됩니다.

이 글은 Data Science 101 시리즈의 9번째 글입니다.

좋은 해석은 숫자를 더 크게 보이게 만드는 일이 아닙니다. 숫자 위에 맥락과 불확실성을 겹쳐서, 팀이 과신하지도 않고 주저앉지도 않게 만드는 일입니다. 이 글에서는 결과를 결정으로 옮기는 기본 흐름을 정리하겠습니다.

![Data Science 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/09/09-01-concept-at-a-glance.ko.png)
*Data Science 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 숫자 결과를 어떻게 의사결정 문장으로 바꿀 수 있을까요?
- 왜 숫자와 맥락은 항상 함께 적어야 할까요?
- 효과 크기와 불확실성은 왜 동시에 보고해야 할까요?
- 이 단계에서 흔히 빠지는 함정은 무엇이고 어떻게 피할까요?

## 이 글에서 배우는 내용

- 결과에서 결정으로 이어지는 5단계 흐름
- 숫자와 함께 불확실성을 보고하는 법
- 해석을 왜곡하는 다섯 가지 인지 함정
- 5단계 해석 실습 흐름
- 보고서에서 자주 생기는 실수 다섯 가지

해석이 과장되면 의사결정은 자신만만해지지만 틀릴 가능성이 커집니다. 해석이 지나치게 약하면 팀은 계속 미루기만 하고 아무 행동도 하지 못합니다. 결국 중요한 것은 숫자를 숨기지 않고, 불확실성도 숨기지 않으면서도 행동 가능한 결론을 만드는 일입니다.

해석 단계는 기술보다 태도가 더 중요할 때가 많습니다. 유리한 결과만 선택적으로 보여 주지 않고, 불확실성을 부끄러워하지 않으며, 마지막에 무엇을 할지까지 분명히 적는 태도가 필요합니다.

> 좋은 해석은 과장하지 않지만, 그래도 결정을 가능하게 만듭니다.

- **Confidence Interval**: 추정치 주변의 불확실성 범위입니다.
- **Effect Size**: 차이의 크기 자체를 뜻합니다.
- **Practical Significance**: 통계적으로뿐 아니라 비즈니스적으로 의미 있는 차이인지 보는 관점입니다.
- **Cherry-picking**: 유리한 결과만 골라 보고하는 왜곡입니다.
- **Survivorship Bias**: 살아남은 사례만 보고 실패한 사례를 놓치는 편향입니다.

## 전/후 비교

**Before**: "정확도가 5% 올랐습니다"라고만 말합니다. 어디서, 누구에게, 얼마나 안정적으로 오른 것인지 알 수 없습니다.

**After**: "유료 사용자 6만 명 기준, 7일 평균 정확도가 89%에서 91%로 상승했고 95% 신뢰구간은 ±0.8%였습니다"처럼 씁니다. 이제야 숫자가 읽히기 시작합니다.

## 실습: 5단계 해석

### 1단계 — 숫자를 정확히 적기

```text
A/B test result: conversion 3.2% (control) vs 3.6% (variant)
n = 50,000 per arm
```

먼저 바뀐 숫자를 정확히 적습니다. 모호한 요약보다 원래 수치를 분명히 쓰는 편이 낫습니다. 표본 크기도 함께 써야 무게를 판단할 수 있습니다.

```python
# 실습 예시: A/B 테스트 결과 계산
import numpy as np
from scipy import stats

n_control = 50_000
n_variant = 50_000
conv_control = 0.032
conv_variant = 0.036

# 전환 수
x_control = int(n_control * conv_control)
x_variant = int(n_variant * conv_variant)

print(f"대조군: {x_control}/{n_control} = {conv_control:.2%}")
print(f"실험군: {x_variant}/{n_variant} = {conv_variant:.2%}")
print(f"절대 차이: +{conv_variant - conv_control:.4f} pp")
```

### 2단계 — 신뢰구간 함께 적기

```text
delta = +0.4pp (95% CI: +0.2pp ~ +0.6pp)
```

불확실성을 함께 적는 순간 결과는 훨씬 정직해집니다. 신뢰구간은 얼마나 불안정한가를 수치로 보여 주는 좋은 도구입니다.

```python
# 비율 차이 신뢰구간 계산
def proportion_ci(x1, n1, x2, n2, confidence=0.95):
    p1, p2 = x1 / n1, x2 / n2
    delta = p2 - p1
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = stats.norm.ppf((1 + confidence) / 2)
    lower = delta - z * se
    upper = delta + z * se
    return delta, lower, upper

delta, lower, upper = proportion_ci(x_control, n_control, x_variant, n_variant)
print(f"delta = {delta*100:+.2f}pp")
print(f"95% CI: ({lower*100:+.2f}pp, {upper*100:+.2f}pp)")
```

신뢰구간이 0을 포함하지 않으면 통계적으로 유의합니다. 하지만 유의하다고 해서 비즈니스적으로 의미 있다는 뜻은 아닙니다.

### 3단계 — 효과 크기 보기

```text
relative lift = +12.5%
```

유의하다는 말만으로는 부족합니다. 차이가 실제로 얼마나 큰지, 비즈니스적으로 행동할 만한 크기인지 확인해야 합니다.

```python
# 상대적 향상률 (Relative Lift)
relative_lift = (conv_variant - conv_control) / conv_control
print(f"상대 향상률: {relative_lift:.2%}")

# 비즈니스 임팩트 환산
monthly_visitors = 200_000
additional_conversions = monthly_visitors * (conv_variant - conv_control)
revenue_per_conversion = 50_000  # 원
monthly_impact = additional_conversions * revenue_per_conversion

print(f"예상 월 추가 전환: {additional_conversions:.0f}건")
print(f"예상 월 추가 매출: {monthly_impact:,.0f}원")
```

효과 크기를 비즈니스 단위로 환산하면 의사결정자에게 훨씬 명확하게 전달됩니다. "+0.4pp"보다 "월 800건 추가 전환, 4천만 원 매출 증대"가 훨씬 설득력 있습니다.

### 4단계 — 맥락 추가하기

```text
campaign window: 2 weeks; segment: paid users; device: desktop only
```

숫자는 맥락 없이 거의 의미가 없습니다. 어떤 기간인지, 어떤 세그먼트인지, 어떤 환경인지 적어야 과도한 일반화를 막을 수 있습니다.

맥락을 구조화하면 다음 분석에서 재사용할 수 있습니다.

```python
context = {
    "period": "2026-05-01 ~ 2026-05-14",
    "segment": "유료 사용자 (free tier 제외)",
    "device": "데스크톱 (모바일 미포함)",
    "traffic_allocation": "50/50 무작위 배정",
    "excluded": ["신규 가입 7일 미만", "봇 트래픽 필터 후"],
    "notes": "모바일 세그먼트는 별도 실험 필요",
}

for key, value in context.items():
    print(f"  {key}: {value}")
```

맥락 섹션에서 가장 중요한 것은 "이 결과를 적용할 수 없는 상황"을 명시하는 것입니다. 모바일 사용자에게도 같은 효과가 있을지는 별도 검증이 필요합니다.

### 5단계 — 의사결정으로 닫기

```text
Decision: roll out to 100% paid desktop users; monitor for 2 more weeks.
```

좋은 보고서는 마지막에 행동을 제안합니다. 무엇을 할지, 누가 볼지, 언제 다시 검토할지까지 쓰면 결과가 실행으로 이어집니다.

```text
의사결정 문장 예시:

분석 결과를 바탕으로 아래 행동을 권고합니다.

1. 즉시 적용: 유료 플랜 데스크톱 사용자에게 실험군 UI 100% 배포
2. 모니터링: 배포 후 2주간 전환율, 이탈율 일별 추적
3. 다음 실험: 모바일 유료 사용자 대상으로 동일 실험 재현
4. 재검토 시점: 2026-06-01 (4주 후 데이터 축적 후 최종 평가)

조건부 중단 기준: 전환율이 기존 대비 -1pp 이상 하락 시 즉시 롤백
```

**Expected output:** 숫자, 신뢰구간, 대상 세그먼트, 권장 행동이 한 문단 안에 함께 적힌 결정 문장을 남깁니다.

- 숫자와 맥락은 항상 한 쌍으로 움직여야 합니다.
- 신뢰구간은 의사결정 위험을 숫자로 드러내 줍니다.
- 보고서는 결정 문장으로 닫힐 때 비로소 실무 산출물이 됩니다.

## 자주 하는 실수 다섯 가지

1. **p-value만 보는 실수**: 효과 크기가 작으면 실무 의미가 약할 수 있습니다.
2. **한 세그먼트 결과를 전체에 일반화하는 실수**: 분산과 차이를 놓칩니다.
3. **좋은 결과만 보고하는 실수**: 전형적인 cherry-picking입니다.
4. **불확실성을 숨기는 실수**: 팀을 과신하게 만듭니다.
5. **결정 문장 없이 보고서를 끝내는 실수**: 결국 아무 행동도 일어나지 않습니다.

### 각 실수의 구체 사례와 수정 전후

**실수 1 — p-value만 보는 경우**

```text
잘못된 보고:
"p=0.03으로 유의미한 차이가 확인됐습니다. 실험군 UI를 전면 배포합니다."

올바른 보고:
"p=0.03이지만 절대 차이는 +0.05pp(상대 향상 1.5%)입니다.
월 추가 전환 예상치는 20건으로, 개발 비용 대비 ROI가 낮아 배포를 보류합니다."
```

**실수 2 — 한 세그먼트 일반화**

```text
잘못된 보고:
"데스크톱 유료 사용자 실험 결과: 전환율 +12.5% 향상. 전체 사용자에게 적용합니다."

올바른 보고:
"데스크톱 유료 사용자(전체의 35%)에서 +12.5% 향상.
모바일(45%)과 무료 사용자(20%)는 별도 실험 미진행 — 동일 결과 보장 불가."
```

**실수 3 — Cherry-picking**

```text
상황: 지표 A, B, C를 측정했는데 A만 유의미하게 개선됨

잘못된 보고:
"지표 A가 유의미하게 향상됐습니다" (B, C는 언급 안 함)

올바른 보고:
"지표 A: +8% (p=0.02, 유의)
지표 B: +1% (p=0.38, 비유의)
지표 C: -2% (p=0.15, 비유의)
전체적으로 A에서만 효과가 관측됐으며, B/C 영향은 불확실합니다."
```

## 세그먼트별 분산 드러내기

단일 지표로는 숨겨진 분산을 보기 어렵습니다. 세그먼트별로 쪼개면 전체 결과가 어디서 왔는지 알 수 있습니다.

```python
import pandas as pd
import numpy as np

# 세그먼트별 전환율 비교
segments = {
    "유료 + 데스크톱": (1_800, 50_000, 2_000, 50_000),
    "유료 + 모바일":   (900, 30_000, 910, 30_000),
    "무료 + 데스크톱": (300, 20_000, 320, 20_000),
    "무료 + 모바일":   (150, 15_000, 155, 15_000),
}

rows = []
for seg, (xc, nc, xv, nv) in segments.items():
    pc, pv = xc / nc, xv / nv
    delta = pv - pc
    lift = delta / pc * 100 if pc > 0 else None
    rows.append({"세그먼트": seg, "대조군": f"{pc:.2%}", "실험군": f"{pv:.2%}",
                 "절대 차이(pp)": f"{delta*100:+.2f}", "상대 향상(%)": f"{lift:+.1f}" if lift else "-"})

df = pd.DataFrame(rows)
print(df.to_string(index=False))
```

이 분석을 통해 "유료 + 데스크톱"에서만 효과가 크고, 무료나 모바일 세그먼트에서는 효과가 미미하다는 사실을 드러낼 수 있습니다. 이 정보가 없으면 전체 평균만 보고 잘못된 범위에 배포하게 됩니다.

## 실무에서는 이렇게 나타납니다

실무 데이터 팀은 주간 리뷰에서 숫자 → 맥락 → 신뢰구간 → 결정 순서를 템플릿처럼 씁니다. 어떤 팀은 분석 전에 가설을 미리 적어 두는 pre-registration 습관을 두어 cherry-picking을 줄입니다. 해석의 품질은 종종 개인 역량보다 팀 템플릿에 더 크게 좌우됩니다.

### 팀 해석 템플릿 예시

```text
분석 리뷰 템플릿 (주간 공유용)

실험명: [이름]
가설 (사전 작성): [실험군이 대조군보다 X를 Y만큼 개선할 것이다]
측정 기간: [시작일 ~ 종료일]
대상 세그먼트: [구체 설명]

결과 요약:
  - 주 지표: [값] (95% CI: [하한, 상한])
  - 보조 지표 1: [값]
  - 보조 지표 2: [값]

맥락 및 제약:
  - 이 결과가 적용되는 조건: [설명]
  - 이 결과가 적용되지 않는 조건: [설명]
  - 주의해야 할 편향: [설명]

의사결정:
  - 권고 행동: [구체 액션]
  - 다음 검토 시점: [날짜]
  - 후속 실험 제안: [있다면]
```

이 템플릿을 팀이 공유하면 발표자가 바뀌어도 해석 품질이 일관됩니다.

## 시니어는 이렇게 생각합니다

- 불확실성을 말하는 것을 부끄러워하지 않습니다.
- 결과는 항상 결정 문장으로 닫습니다.
- p-value보다 effect size를 더 유심히 봅니다.
- 세그먼트를 나눠 분산을 드러냅니다.
- 리뷰 템플릿 자체를 팀 자산으로 만듭니다.

## 운영 체크리스트

- [ ] 신뢰구간을 함께 적을 수 있습니다.
- [ ] 효과 크기를 읽을 수 있습니다.
- [ ] 세그먼트별로 나눠 보는 습관이 있습니다.
- [ ] 의사결정 문장을 작성할 수 있습니다.
- [ ] cherry-picking을 막는 pre-registration 규칙이 있습니다.
- [ ] 보고서가 항상 "다음 행동"으로 닫힙니다.

## 연습 문제

1. 과거 분석 하나를 골라 5단계 흐름으로 다시 해석해 보세요.
2. `p=0.04`지만 효과가 0.1%뿐인 결과를 어떻게 보고할지 적어 보세요.
3. cherry-picking을 막기 위한 팀 규칙 세 가지를 적어 보세요.
4. 같은 실험 결과를 두 가지 방식으로 작성해 보세요 — 하나는 과장한 버전, 하나는 올바른 버전.
5. 여러분이 최근에 본 분석 결과에서 맥락이 빠져 있는 부분을 찾아 보고 추가해 보세요.

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

### 파이썬 예시: 중요도와 개별 예측 설명

```python
import pandas as pd
from sklearn.inspection import permutation_importance

# Fitted model, X_valid, y_valid 가 이미 준비하고 있습니다
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

### 재현 가능한 결과 패키지 만들기

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

## 처음 질문으로 돌아가기

- **숫자 결과를 어떻게 의사결정 문장으로 바꿀 수 있을까요?**
  - 5단계 흐름이 핵심입니다. 숫자를 정확히 적고, 신뢰구간을 추가하고, 효과 크기를 확인하고, 맥락(기간, 세그먼트, 환경)을 추가한 뒤, 마지막으로 무엇을 할지 결정 문장으로 닫습니다. 이 순서가 있으면 숫자가 행동으로 이어집니다.

- **왜 숫자와 맥락은 항상 함께 적어야 할까요?**
  - 숫자 단독으로는 과도한 일반화를 부릅니다. "정확도 91%"는 어떤 기간인지, 어떤 사용자군인지, 어떤 환경에서 측정했는지 알아야 의미가 있습니다. 맥락 없는 숫자는 다음 팀이 그 결과를 어디에, 어떻게 적용할지 판단할 근거가 없습니다.

- **효과 크기와 불확실성은 왜 동시에 보고해야 할까요?**
  - p-value가 0.04라고 해도 효과 크기가 0.1%라면 비즈니스 행동을 바꿀 근거가 약합니다. 반대로 효과 크기가 크더라도 신뢰구간이 넓으면 재현 가능성에 의문이 생깁니다. 둘을 함께 보고해야 팀이 과신 없이 정확한 판단을 내릴 수 있습니다.

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
- **Data Science 101 (9/10): 결과 해석 (현재 글)**
- [데이터 프로젝트 전체 흐름](./10-data-project-end-to-end.md)

<!-- toc:end -->

## 참고 자료

- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)
- [Kahneman — Thinking, Fast and Slow](https://us.macmillan.com/books/9780374533557/thinkingfastandslow)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Microsoft — Trustworthy Online Experiments](https://exp-platform.com/)
- [book-examples — data-science-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-science-101/ko)

Tags: DataScience, Interpretation, Storytelling, Decision, Beginner
