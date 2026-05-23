---
series: probability-101
episode: 3
title: "Probability 101 (3/10): 조건부확률"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Probability
  - Conditional
  - Independence
  - Inference
  - Beginner
seo_description: 조건부확률과 곱셈정리를 배우고, 기저율 오류를 방지하며 정보를 업데이트하는 논리적 과정을 학습합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (3/10): 조건부확률

현실의 확률 문제는 대개 조건이 붙습니다. 비가 온다는 조건에서의 교통체증, 양성 판정이 있다는 조건에서의 질병, 어떤 단어가 나왔다는 조건에서의 스팸 메일처럼 우리가 실제로 묻는 대부분의 확률은 맥락이 붙은 확률입니다.

그래서 조건부확률은 확률 이론의 부가 기능이 아니라 중심에 가깝습니다. 새로운 정보를 알았을 때 분모가 어떻게 바뀌는지 이해해야 추론도, 해석도, 모델 점수도 제대로 읽을 수 있습니다.

이 글은 Probability 101 시리즈의 3번째 글입니다. 여기서는 조건부확률의 정의, 곱셈정리, 독립과 종속의 차이, 그리고 기저율이 왜 해석을 바꾸는지 코드와 함께 정리하겠습니다.


![Probability 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/03/03-01-diagram.ko.png)
*Probability 101 3장 흐름 개요*
> 조건부확률은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 조건부확률은 왜 분모가 바뀌는 문제일까요?
- `P(A|B)`와 `P(B|A)`는 왜 전혀 다른 값일 수 있을까요?
- 곱셈정리는 어떤 상황에서 자연스럽게 등장할까요?

## 왜 중요한가

확률을 배울 때 가장 흔한 오해 중 하나는 조건의 방향을 바꿔 읽는 것입니다. `P(질병 | 양성)`과 `P(양성 | 질병)`은 비슷해 보여도 전혀 다른 질문입니다. 이 방향 감각이 없으면 검사 결과, 모델 점수, 경보 시스템을 모두 잘못 읽게 됩니다.

특히 현실 문제에서는 기저율이 작을수록 오해가 더 커집니다. 질병 유병률이 낮은데 검사 민감도만 보고 판단하면 양성 판정의 의미를 과대평가하기 쉽습니다. 조건부확률은 결국 맥락을 반영하는 기술입니다.

## 독립 vs 종속 사건

조건부확률을 이해하려면 독립과 종속의 차이를 명확히 구분해야 합니다. 두 개념은 자주 혼동되지만 전혀 다른 질문에 답합니다.

| 개념 | 정의 | 판별법 | 예시 |
| --- | --- | --- | --- |
| 독립 사건 | A와 B가 서로 영향을 주지 않음 | P(A∩B) = P(A)·P(B) | 동전 두 번 던지기의 각 결과 |
| 종속 사건 | B를 알면 A의 확률이 바뀜 | P(A\|B) ≠ P(A) | 날씨와 교통체증 |

독립을 판별하는 가장 확실한 방법은 곱셈정리를 확인하는 것입니다. `P(A∩B)`와 `P(A)·P(B)`를 계산해서 같으면 독립, 다르면 종속입니다. 조건부확률로도 확인할 수 있습니다: `P(A|B) = P(A)`이면 B를 알아도 A의 확률이 바뀌지 않으므로 독립입니다.

실무에서는 독립을 가정하고 싶을 때가 많지만, 현실의 대부분 사건은 종속적입니다. 예를 들어 사용자의 클릭 행동은 이전 페이지 방문과 독립적이지 않습니다. 센서 값은 이전 측정값과 상관되어 있습니다. 독립을 부주의하게 가정하면 모델 성능이 크게 떨어지거나 편향이 발생할 수 있습니다.

## 파이썬 조건부확률 계산 예제: 스팸 필터

스팸 필터는 조건부확률의 실용적인 예시입니다. 특정 단어가 나왔을 때 스팸일 확률을 계산합니다.

```python
# 간단한 스팸 필터 예제 (가상 데이터)
# P(스팸) = 0.3
# P("당첨"|스팸) = 0.7
# P("당첨"|정상) = 0.05

P_spam = 0.3
P_normal = 0.7
P_word_given_spam = 0.7
P_word_given_normal = 0.05

# 전체확률법칙: P("당첨")
P_word = P_word_given_spam * P_spam + P_word_given_normal * P_normal
print(f"P('당첨') = {P_word:.3f}")

# 조건부확률: P(스팸 | "당첨")
P_spam_given_word = (P_word_given_spam * P_spam) / P_word
print(f"P(스팸 | '당첨') = {P_spam_given_word:.3f}")

# 비교: 단어 없을 때와 있을 때
print(f"P(스팸) = {P_spam:.3f}")
print(f"P(스팸|'당첨') = {P_spam_given_word:.3f}")
print(f"증가율: {P_spam_given_word / P_spam:.2f}x")
```

출력:

```
P('당첨') = 0.245
P(스팸 | '당첨') = 0.857
P(스팸) = 0.300
P(스팸|'당첨') = 0.857
증가율: 2.86x
```

"당첨"이라는 단어가 나오기 전에는 스팸일 확률이 30%였지만, 이 단어를 본 후에는 85.7%로 올라갑니다. 조건부확률은 이렇게 새로운 정보가 확률을 어떻게 갱신하는지 보여줍니다.

## 조건부확률 트리

조건부확률 문제를 체계적으로 풀려면 확률 트리(probability tree)를 그리는 것이 효과적입니다. 각 분기에서 조건부확률을 곱하면 경로 확률을 구할 수 있습니다.

```python
# 조건부확률 트리 예시: 날씨와 교통체증
# 1겵: 비 여부 (P(비)=0.3, P(맑음)=0.7)
# 2겵: 교통체증 여부
#   P(체증|비) = 0.8
#   P(체증|맑음) = 0.2

P_rain = 0.3
P_clear = 0.7
P_jam_given_rain = 0.8
P_jam_given_clear = 0.2

# 경로 확률 (곱셈정리)
path_rain_jam = P_rain * P_jam_given_rain
path_rain_no_jam = P_rain * (1 - P_jam_given_rain)
path_clear_jam = P_clear * P_jam_given_clear
path_clear_no_jam = P_clear * (1 - P_jam_given_clear)

print("확률 트리:")
print(f"  비 → 체증:    {path_rain_jam:.3f}")
print(f"  비 → 원활:    {path_rain_no_jam:.3f}")
print(f"  맑음 → 체증: {path_clear_jam:.3f}")
print(f"  맑음 → 원활: {path_clear_no_jam:.3f}")
print(f"  합계:         {path_rain_jam + path_rain_no_jam + path_clear_jam + path_clear_no_jam:.1f}")

# 전체확률법칙: P(체증)
P_jam = path_rain_jam + path_clear_jam
print(f"\nP(체증) = {P_jam:.3f}")

# 역추론: P(비|체증)
P_rain_given_jam = path_rain_jam / P_jam
print(f"P(비|체증) = {P_rain_given_jam:.3f}")
print(f"체증일 때 비 때문일 확률이 {P_rain_given_jam:.0%}")
```

출력:

```
확률 트리:
  비 → 체증:    0.240
  비 → 원활:    0.060
  맑음 → 체증: 0.140
  맑음 → 원활: 0.560
  합계:         1.0

P(체증) = 0.380
P(비|체증) = 0.632
체증일 때 비 때문일 확률이 63%
```

트리의 각 경로는 곱셈정리를 적용한 결과입니다. 모든 말단 노드의 확률을 더하면 1이 됩니다. 역추론(체증인데 비 때문일 확률)은 해당 경로의 확률을 전체 체증 확률로 나누면 됩니다.

## 몬테카를로로 조건부확률 추정하기

해석적 계산이 복잡한 조건부확률도 시뮬레이션으로 추정할 수 있습니다.

```python
import random

def simulate_conditional(n_trials: int = 100_000) -> dict:
    """
    주사위 2개: 합이 8 이상일 때, 두 눈이 같을 확률
    P(두 눈 같음 | 합 >= 8)
    """
    count_condition = 0  # 합 >= 8인 경우
    count_both = 0       # 합 >= 8이고 두 눈 같은 경우

    for _ in range(n_trials):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        if d1 + d2 >= 8:
            count_condition += 1
            if d1 == d2:
                count_both += 1

    return {
        "P(합>=8)": count_condition / n_trials,
        "P(두눈같음 ∩ 합>=8)": count_both / n_trials,
        "P(두눈같음 | 합>=8)": count_both / count_condition if count_condition > 0 else 0,
    }

# 이론값 계산
omega = [(i, j) for i in range(1, 7) for j in range(1, 7)]
cond = [(i, j) for i, j in omega if i + j >= 8]
both = [(i, j) for i, j in cond if i == j]
theory = len(both) / len(cond)

random.seed(42)
results = simulate_conditional()
print(f"시뮬레이션 P(두눈같음 | 합>=8) = {results['P(두눈같음 | 합>=8)']:.4f}")
print(f"이론값 P(두눈같음 | 합>=8) = {theory:.4f}")
print(f"조건 없이 P(두눈같음) = {6/36:.4f}")
print(f"조건이 확률을 바꿨: {theory:.4f} vs {6/36:.4f}")
```

조건이 없을 때 두 눈이 같을 확률은 6/36 = 0.167이지만, "합이 8 이상"이라는 조건이 붙으면 확률이 달라집니다. 이것이 종속의 핵심입니다.

## 기저율 오류 시뮬레이션

기저율 오류(base rate fallacy)는 조건부확률에서 가장 흔한 실수입니다. 유병률이 낮은 질병에서 검사 양성의 의미를 시뮬레이션으로 확인합니다.

```python
import random

def base_rate_simulation(
    prevalence: float,
    sensitivity: float,
    specificity: float,
    n_population: int = 100_000,
) -> dict:
    """
    기저율 오류 시뮬레이션
    prevalence: 유병률
    sensitivity: P(양성|질병)
    specificity: P(음성|건강)
    """
    tp = fp = fn = tn = 0

    for _ in range(n_population):
        sick = random.random() < prevalence
        if sick:
            positive = random.random() < sensitivity
        else:
            positive = random.random() > specificity

        if sick and positive:
            tp += 1
        elif not sick and positive:
            fp += 1
        elif sick and not positive:
            fn += 1
        else:
            tn += 1

    total_positive = tp + fp
    ppv = tp / total_positive if total_positive > 0 else 0
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "PPV": ppv}

random.seed(42)
# 낮은 유병률 (0.1%) + 높은 민감도 (99%)
result = base_rate_simulation(
    prevalence=0.001, sensitivity=0.99, specificity=0.95
)
print(f"TP={result['TP']}, FP={result['FP']}")
print(f"양성 판정 중 실제 환자 비율(PPV) = {result['PPV']:.3f}")
print(f"즉, 양성이어도 {1-result['PPV']:.1%}는 오경보")

print("\n--- 유병률을 5%로 높이면? ---")
result2 = base_rate_simulation(
    prevalence=0.05, sensitivity=0.99, specificity=0.95
)
print(f"TP={result2['TP']}, FP={result2['FP']}")
print(f"PPV = {result2['PPV']:.3f}")
```

유병률이 0.1%일 때는 민감도가 99%이더라도 양성 판정의 대부분이 오경보입니다. 유병률이 5%로 올라가면 PPV가 크게 개선됩니다. 이것이 기저율의 힘입니다. 다음 글(베이즈 정리)에서 이 문제를 수식으로 정리합니다.

## 다중 조건의 체이닝

조건이 여러 개 붙을 수도 있습니다. 곱셈정리를 반복 적용하면 됩니다.

```python
# P(A ∩ B ∩ C) = P(A) × P(B|A) × P(C|A∩B)
# 예: 비복원 추출에서 3장 모두 스페이드일 확률

# 52장 중 스페이드 13장
P_first = 13 / 52
P_second_given_first = 12 / 51  # 스페이드 1장 빠짐
P_third_given_first_two = 11 / 50  # 스페이드 2장 빠짐

P_all_spades = P_first * P_second_given_first * P_third_given_first_two
print(f"P(3장 모두 스페이드) = {P_all_spades:.4f}")
print(f"약 {1/P_all_spades:.0f}번에 1번 발생")
```

체이닝의 핵심은 앞의 결과가 뒤의 조건을 바꾼다는 점입니다. 비복원 추출에서는 앞의 결과가 남은 표본공간을 축소시키므로 각 단계의 확률이 달라집니다.

## 조건부 확률의 직관

조건부확률을 이해하는 가장 직관적인 방법은 2x2 분할표(contingency table)로 생각하는 것입니다.

진단 검사 예시:

|  | 질병 O | 질병 X | 합계 |
| --- | --- | --- | --- |
| 양성 | 45 (TP) | 5 (FP) | 50 |
| 음성 | 5 (FN) | 945 (TN) | 950 |
| 합계 | 50 | 950 | 1000 |

이 표에서 여러 확률을 읽을 수 있습니다:

- `P(질병) = 50/1000 = 0.05`
- `P(양성|질병) = 45/50 = 0.9` (sensitivity)
- `P(음성|건강) = 945/950 = 0.995` (specificity)
- `P(질병|양성) = 45/50 = 0.9` (PPV, positive predictive value)

핵심은 분모가 무엇인지 확인하는 것입니다:

- `P(양성|질병)`: 분모는 질병 있는 사람 50명
- `P(질병|양성)`: 분모는 양성 판정 받은 사람 50명

같은 숫자 50이지만 분모의 의미는 전혀 다릅니다. 이 차이를 명확히 보는 것이 조건부확률의 핵심입니다.

```python
# 2x2 표로 조건부확률 계산
TP, FP, FN, TN = 45, 5, 5, 945
total = TP + FP + FN + TN

sick = TP + FN
healthy = FP + TN
positive = TP + FP
negative = FN + TN

print(f"P(질병) = {sick/total:.3f}")
print(f"P(양성|질병) = {TP/sick:.3f}  # sensitivity")
print(f"P(질병|양성) = {TP/positive:.3f}  # PPV")
print(f"P(음성|건강) = {TN/healthy:.3f}  # specificity")
```

이 코드는 같은 데이터에서도 분모를 바꾸면 전혀 다른 확률이 나온다는 점을 명확히 보여줍니다.
## 핵심 용어

- **`P(A | B)`**: B가 주어졌을 때 A의 확률입니다.
- **곱셈정리**: `P(A∩B) = P(A | B)·P(B)`입니다.
- **전체확률법칙**: 사건을 여러 경우로 나눠 전체 확률을 다시 합치는 규칙입니다.
- 독립: `P(A | B) = P(A)`가 성립하는 관계입니다.
- 종속: 조건이 붙으면 확률이 달라지는 관계입니다.

조건이 붙으면 분모가 바뀝니다. 전체 집단에서 보던 비율을, B가 일어난 세계 안에서 다시 계산하는 것입니다.

## 방향을 바꿔 읽으면 바로 틀립니다

“검사가 양성이면 병이 있을 확률이 높다”라는 문장은 자주 들리지만, 실제로 계산해야 하는 값은 `P(질병 | 양성)`입니다. 반면 검사 성능표에 자주 나오는 값은 `P(양성 | 질병)`입니다. 하나는 진단 이후의 질문이고, 다른 하나는 질병이 있을 때 검사기가 어떻게 반응하는가에 대한 질문입니다.

두 값은 같은 정보가 아닙니다. 이 차이를 잡지 못하면 민감도가 높은 검사를 곧장 높은 진단 정확도로 착각하게 됩니다.

## 5단계로 보는 조건부확률

### 1단계 — 데이터 만들기

```python
# 100명; 5 아프다. 민감도 0.9, 특이도 0.95
N, sick = 100, 5
TP = round(sick * 0.9)
FN = sick - TP
TN = round((N - sick) * 0.95)
FP = (N - sick) - TN
print(TP, FN, TN, FP)
```

간단한 진단 예시를 직접 만들어 보면 조건부확률의 방향이 훨씬 또렷해집니다. 전체 100명 중 5명이 아프고, 검사에는 민감도와 특이도가 있다고 두겠습니다.

### 2단계 — `P(양성)` 계산하기

```python
pos = TP + FP
print("P(pos):", pos / N)
```

양성 확률은 진짜 환자에서 나온 양성과 건강한 사람에게서 잘못 나온 양성을 모두 포함합니다. 여기서 이미 전체확률법칙의 감각이 드러납니다.

### 3단계 — `P(질병 | 양성)` 계산하기

```python
print("P(sick|pos):", TP / pos)
```

이제 분모는 전체 100명이 아니라 양성 판정을 받은 사람 수입니다. 바로 이 분모 전환이 조건부확률의 핵심입니다.

### 4단계 — 곱셈정리 확인하기

```python
P_sick = sick / N
P_pos_given_sick = TP / sick
print("P(sick and pos):", P_pos_given_sick * P_sick, "==", TP / N)
```

곱셈정리는 외울 공식이라기보다, 조건을 붙여 교집합을 다시 쓰는 방법입니다. 코드로 확인하면 식이 훨씬 덜 추상적으로 보입니다.

### 5단계 — 독립성 점검하기

```python
P_pos = pos / N
print("indep?", round(TP/N - P_sick * P_pos, 6))  # nonzero implies dependence
```

독립이라면 `P(A∩B)`와 `P(A)P(B)`가 같아야 합니다. 진단 문제에서는 보통 그렇지 않습니다. 양성 여부는 질병 여부와 명백히 연결돼 있기 때문입니다.

## 이 코드에서 먼저 봐야 할 점

- 조건부확률은 분모를 바꾸는 연산입니다.
- `P(+|질병)`와 `P(질병|+)`는 다른 값입니다.
- 기저율이 낮으면 양성예측도가 낮아질 수 있습니다.
- 독립 여부는 조건을 붙였을 때 확률이 바뀌는지로 읽을 수 있습니다.

## 전체확률법칙 (Law of Total Probability)

전체확률법칙은 복잡한 사건을 여러 경우로 나누어 각각의 확률을 계산한 후 합치는 방법입니다. 베이즈 정리의 분모를 계산할 때 필수적으로 쓰입니다.

사건 B가 일어날 확률을 여러 상황으로 나누어 계산하는 공식:

```
P(B) = P(B | A₁) × P(A₁) + P(B | A₂) × P(A₂) + ... + P(B | Aₙ) × P(Aₙ)
```

조건:

- A₁, A₂, ..., Aₙ는 상호배반 (겹치지 않음)
- A₁ ∪ A₂ ∪ ... ∪ Aₙ = Ω (전체를 완전히 커버)

**실용 예시: 제품 불량 검사**

세 공장 A, B, C가 각각 40%, 35%, 25%의 제품을 생산합니다. 불량률은 각각 2%, 3%, 5%입니다. 무작위로 선택한 제품이 불량일 확률은?

```python
# 공장별 생산 비율
P_A = 0.40
P_B = 0.35
P_C = 0.25

# 공장별 불량률
P_defect_given_A = 0.02
P_defect_given_B = 0.03
P_defect_given_C = 0.05

# 전체확률법칙
P_defect = (P_defect_given_A * P_A +
            P_defect_given_B * P_B +
            P_defect_given_C * P_C)

print(f"P(불량) = {P_defect:.3f}")

# 역추론: 불량품이 A 공장에서 나왔을 확률 (베이즈 정리)
P_A_given_defect = (P_defect_given_A * P_A) / P_defect
print(f"P(A|불량) = {P_A_given_defect:.3f}")
```

출력:

```
P(불량) = 0.032
P(A|불량) = 0.250
```

전체 불량률은 3.2%이고, 불량품이 A 공장에서 나왔을 확률은 25%입니다. A 공장의 생산 비율은 40%이지만, 불량률이 낮기 때문에 불량품 중 비율은 25%로 떨어집니다.

전체확률법칙은 조건부확률을 계산할 때 분모를 구하는 표준 기법입니다. 베이즈 정리, 분포 계산, 의사결정 트리에서 반복해서 등장합니다.

## 조건부확률이 실무에 쓰이는 형태

조건부확률은 단순한 수식이 아니라 실무에서 의사결정의 뼈대입니다.

**웹 서비스에서의 전환율**은 `P(구매 | 방문)`입니다. 전체 방문자 중 구매자 비율이 아니라, 특정 페이지를 본 사람 중 구매한 비율을 추적합니다. 조건을 바꾸면 `P(구매 | 광고 클릭)`, `P(구매 | 이메일 열람)` 같은 채널별 분석도 가능합니다.

**검색 엔진의 relevance**는 `P(클릭 | 쿼리)`입니다. 사용자가 특정 키워드를 입력했을 때 어떤 결과를 클릭할지 예측하는 문제입니다. 검색 순위는 이 조건부확률을 최대화하는 방향으로 정렬됩니다.

**추천 시스템의 click-through rate**는 `P(클릭 | 노출)`입니다. 아이템을 보여줬을 때 클릭할 확률을 계산해서 상위 N개를 추천합니다. 여기서도 조건을 정의하는 방식이 추천 품질을 결정합니다.

조건부확률은 결국 "상황을 제한했을 때 무슨 일이 일어날 확률"을 계산하는 도구입니다. 조건을 어떻게 정의하느냐에 따라 같은 데이터에서도 전혀 다른 인사이트가 나옵니다.

**실무 체크리스트**

조건부확률을 해석할 때 스스로 확인해야 할 질문을 정리합니다:

1. **분모가 무엇인가?** — 전체 집단인지, 특정 조건을 만족하는 하위 집단인지
2. **조건의 방향은?** — P(A|B)와 P(B|A) 중 어느 쪽을 묻고 있는지
3. **기저율은 얼마인가?** — 전체 집단에서 사건이 얼마나 흔한지
4. **독립을 가정할 수 있는가?** — 조건이 확률을 실제로 바꾸는지
5. **데이터가 충분한가?** — 조건부 빈도를 계산할 만큼 샘플이 충분한지

이 다섯 가지 질문을 습관적으로 던지면 조건부확률 해석에서 생기는 대부분의 오류를 방지할 수 있습니다.
## 자주 헷갈리는 지점

첫째, `P(A|B)`와 `P(B|A)`를 같은 값으로 읽기 쉽습니다. 이 실수가 가장 흔하고 가장 치명적입니다.

둘째, 기저율을 무시하기 쉽습니다. 전체 집단에서 사건이 얼마나 드문지 모르면 양성 판정 하나의 의미도 크게 왜곡됩니다.

셋째, 독립과 상호배반을 다시 섞기 쉽습니다. 함께 일어날 수 없다는 말과 조건이 영향을 주지 않는다는 말은 다른 질문입니다.

넷째, 조건을 말로만 이해하고 수식에서 놓치기 쉽습니다. 곱셈정리에서 조건을 빼먹으면 식은 비슷해 보여도 완전히 다른 계산이 됩니다.

다섯째, 분모가 누구인지 묻지 않고 숫자만 보는 습관이 남기 쉽습니다. 강한 해석은 언제나 분모를 확인하는 데서 시작합니다.

## 실무에서는 이렇게 드러납니다

스팸 필터, 의료 검사, 사기 탐지, 자동완성, 검색 랭킹 모두 조건부확률 위에 서 있습니다. 모델 출력의 의미는 결국 어떤 조건이 붙은 확률인지로 해석됩니다. 예를 들어 `p(y|x)`는 입력 `x`가 주어졌을 때 정답 `y`의 확률입니다.

그래서 실무에서는 숫자 하나를 볼 때도 먼저 묻습니다. 무엇이 조건인가, 분모가 무엇인가, 기저율은 얼마인가. 이 세 질문을 빠뜨리면 모델 성능표도, 경보 시스템도, 진단 결과도 쉽게 과신하게 됩니다.

머신러닝 모델의 출력값 자체가 조건부확률입니다. 분류 모델은 `P(class=1|features)`를 출력하고, 언어 모델은 `P(next_token|context)`를 출력합니다. 조건부확률을 제대로 이해하지 못하면 모델 출력을 올바르게 해석할 수 없습니다.

## 체크리스트

- [ ] `P(A|B)`의 뜻을 분모 관점에서 설명할 수 있습니다.
- [ ] 곱셈정리를 사용할 수 있습니다.
- [ ] 독립과 종속을 구분할 수 있습니다.
- [ ] 기저율 오류가 왜 생기는지 설명할 수 있습니다.
- [ ] 전체확률법칙으로 P(B)를 계산할 수 있습니다.
- [ ] 확률 트리를 그려 조건부확률 문제를 풀 수 있습니다.
- [ ] 시뮬레이션으로 조건부확률을 추정할 수 있습니다.

## 정리

조건부확률은 맥락을 다루는 도구입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 조건이 붙으면 분모가 바뀐다는 점, 조건의 방향을 바꾸면 전혀 다른 질문이 된다는 점, 그리고 기저율을 함께 봐야 숫자의 의미를 제대로 읽을 수 있다는 점입니다.

다음 글에서는 베이즈 정리를 다룹니다. 이번 글이 조건부확률의 문법을 세웠다면, 다음 글은 그 문법을 이용해 믿음을 어떻게 갱신하는지 보여 줍니다.

## 처음 질문으로 돌아가기

- **조건부확률은 왜 분모가 바뀌는 문제일까요?**
  - 개념의 정의와 실무에서의 사용법을 분리해서 봅니다.
  - 구체적인 예제와 시뮬레이션으로 개념을 실제로 확인합니다.
- **곱셈정리는 어떤 상황에서 자연스럽게 등장할까요?**
  - 이 개념을 실제로 적용할 때 주의할 점을 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- **조건부확률 (현재 글)**
- 베이즈 정리 (예정)
- 확률변수 (예정)
- 기대값과 분산 (예정)
- 이산분포 (예정)
- 연속분포 (예정)
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [Khan Academy — Conditional probability](https://www.khanacademy.org/math/statistics-probability/probability-library/conditional-probability-independence)
- [Wikipedia — Conditional probability](https://en.wikipedia.org/wiki/Conditional_probability)
- [Wikipedia — Base rate fallacy](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, Conditional, Independence, Inference, Beginner
