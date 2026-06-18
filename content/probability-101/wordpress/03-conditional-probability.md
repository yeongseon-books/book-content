---
series: probability-101
episode: 3
title: "바이브코딩을 위한 확률 기초 (3/10): 조건부확률"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 확률
  - 조건부확률
  - AI확률점수
  - 기저율
language: ko
---

# 바이브코딩을 위한 확률 기초 (3/10): 조건부확률

이 글은 **바이브코딩을 위한 확률 기초** 시리즈의 3편입니다. AI 모델이 출력하는 확률 점수를 제대로 읽으려면 조건부확률의 방향을 정확히 이해해야 합니다.

---

AI 분류기가 "양성 확률 95%"를 출력했습니다. 여러분은 그 결과를 믿어야 할까요? 사실 이 95%가 무엇에 대한 확률인지 모르면 답할 수 없습니다. "모델이 양성이라고 했을 때 실제로 양성일 확률 95%"인가요, "실제 양성일 때 모델이 양성이라고 할 확률 95%"인가요? 이 두 가지는 완전히 다른 숫자입니다.

> "조건부확률의 핵심은 분모가 바뀐다는 것입니다. AI 모델 출력을 잘못 읽는 가장 흔한 실수가 바로 이 방향 혼동에서 옵니다."

## 이 글에서 다룰 질문들

- 조건부확률은 왜 분모가 바뀌는 문제일까요?
- `P(A|B)`와 `P(B|A)`는 왜 전혀 다른 값일 수 있을까요?
- 기저율이 낮으면 왜 AI 모델 결과를 과신하면 안 될까요?
- 전체확률법칙은 언제 필요할까요?
- 독립과 종속을 구분하는 실용적인 방법은?

---

## 바이브코딩 관점: 조건의 방향이 의사결정을 바꾼다

의료 AI, 사기 탐지 AI, 스팸 필터는 모두 조건부확률을 출력합니다. 그런데 우리가 실제로 알고 싶은 것과 모델이 제공하는 것이 다를 수 있습니다.

### Before: 조건 방향을 혼동한 경우

```python
# 암 진단 AI: "민감도(sensitivity) 99%"라는 광고
# 많은 사람이 이를 "양성이면 99% 확률로 암" 으로 읽음
# 하지만 실제 의미는:

sensitivity = 0.99  # P(양성 판정 | 실제 암) = 0.99
# 이것은 "실제 암 환자에게 검사했을 때 양성이 나올 확률"

# 우리가 알고 싶은 것:
# P(실제 암 | 양성 판정) = ???
# 이 값은 전혀 다릅니다!
```

### After: 조건 방향을 명확히 구분

```python
# 기저율(유병률)을 포함해서 올바르게 계산
prevalence = 0.001   # 인구 0.1%가 이 암에 걸림
sensitivity = 0.99   # P(양성|암)
specificity = 0.95   # P(음성|건강)

# 전체확률법칙으로 P(양성) 계산
P_positive = sensitivity * prevalence + (1 - specificity) * (1 - prevalence)

# 베이즈 정리로 실제 관심 확률 계산
P_cancer_given_positive = (sensitivity * prevalence) / P_positive

print(f"민감도: {sensitivity:.0%}")
print(f"P(암 | 양성 판정): {P_cancer_given_positive:.1%}")
# 출력: 민감도: 99% / P(암 | 양성 판정): 1.9%
```

민감도 99%인데도 양성 판정 후 실제 암일 확률이 1.9%밖에 안 됩니다. 이것이 기저율의 힘이고, 조건 방향을 바꿔야 하는 이유입니다.

---

## 조건부확률의 구조: 분모가 바뀐다

조건부확률 P(A|B)는 "B라는 세계 안에서 A가 일어날 비율"입니다. 분모가 전체 표본공간에서 B로 좁혀집니다.

```python
# 주사위 예제: 눈이 3 이상일 때 짝수일 확률
omega = set(range(1, 7))
B = {3, 4, 5, 6}  # 조건: 3 이상
A = {2, 4, 6}     # 관심 사건: 짝수

# 조건부 표본공간으로 축소
A_given_B = A & B   # {4, 6}
P_A_given_B = len(A_given_B) / len(B)

print(f"P(짝수): {len(A)/len(omega):.3f}")       # 0.500
print(f"P(짝수|3이상): {P_A_given_B:.3f}")        # 0.500
print(f"조건이 확률을 바꿨나: {P_A_given_B != len(A)/len(omega)}")  # False (독립)

# 종속 예제
C = {1, 2, 3}  # 조건: 3 이하
A_given_C = A & C  # {2}
P_A_given_C = len(A_given_C) / len(C)
print(f"P(짝수|3이하): {P_A_given_C:.3f}")  # 0.333 (달라짐!)
```

---

## 독립 vs 종속: AI 특징들의 관계

| 개념 | 정의 | AI 활용 예시 | 판별법 |
| --- | --- | --- | --- |
| 독립 사건 | A와 B가 서로 영향 없음 | 서로 다른 센서 값 | P(A∩B) = P(A)·P(B) |
| 종속 사건 | B를 알면 A의 확률이 바뀜 | 이전 클릭과 현재 클릭 | P(A\|B) ≠ P(A) |

```python
def check_independence(P_A, P_B, P_AB):
    """두 사건이 독립인지 확인"""
    expected_if_independent = P_A * P_B
    diff = abs(P_AB - expected_if_independent)
    is_independent = diff < 1e-10
    print(f"P(A∩B) = {P_AB:.4f}")
    print(f"P(A)·P(B) = {expected_if_independent:.4f}")
    print(f"독립: {is_independent}")
    return is_independent

# 예: 사용자가 광고를 클릭한 경우 구매할 확률
P_purchase = 0.05        # 전체 구매 확률
P_click = 0.3            # 전체 광고 클릭 확률
P_click_and_purchase = 0.04  # 클릭하고 구매

check_independence(P_purchase, P_click, P_click_and_purchase)
# 독립이 아님 — 클릭 여부가 구매에 영향을 줌
```

---

## 기저율 오류: AI 결과를 잘못 읽는 가장 흔한 실수

```python
def base_rate_ppv(prevalence, sensitivity, specificity):
    """
    양성 판정 후 실제 양성일 확률(PPV) 계산
    prevalence: 기저율 (전체 집단에서 실제 양성 비율)
    sensitivity: P(양성 판정 | 실제 양성)
    specificity: P(음성 판정 | 실제 음성)
    """
    P_pos = sensitivity * prevalence + (1 - specificity) * (1 - prevalence)
    ppv = (sensitivity * prevalence) / P_pos
    fdr = 1 - ppv  # 오경보율
    return ppv, fdr

# 시나리오 1: 드문 이벤트 (사기 탐지)
ppv, fdr = base_rate_ppv(0.001, 0.95, 0.99)
print(f"사기 탐지 — PPV: {ppv:.1%}, 오경보율: {fdr:.1%}")

# 시나리오 2: 흔한 이벤트 (스팸 메일)
ppv2, fdr2 = base_rate_ppv(0.3, 0.95, 0.99)
print(f"스팸 탐지 — PPV: {ppv2:.1%}, 오경보율: {fdr2:.1%}")
```

출력:
```
사기 탐지 — PPV: 8.7%, 오경보율: 91.3%
스팸 탐지 — PPV: 97.6%, 오경보율: 2.4%
```

같은 성능의 모델이라도 기저율(사기 0.1% vs 스팸 30%)에 따라 결과 신뢰도가 완전히 달라집니다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| P(A\|B)와 P(B\|A) 혼동 | 가장 흔하고 치명적인 실수 | 조건 방향을 항상 먼저 확인 |
| 기저율 무시 | "정확도 99%"만 보고 결과 신뢰 | 기저율 + 정확도 함께 계산 |
| 분모 확인 안 하기 | "85%"가 전체 중 85%인지, 조건부 85%인지? | 분모가 무엇인지 먼저 파악 |
| 독립 가정 남발 | 특징들이 실제로 독립이 아닌데 독립으로 처리 | 상관관계 분석으로 확인 |

---

## AI 팁: 분류 모델 결과 올바르게 해석하기

```python
def interpret_classifier_output(tp, fp, fn, tn):
    """
    혼동 행렬에서 다양한 조건부확률 계산
    """
    total = tp + fp + fn + tn
    sick = tp + fn      # 실제 양성
    positive = tp + fp  # 양성 판정

    metrics = {
        "P(실제 양성)": sick / total,
        "P(양성 판정)": positive / total,
        "민감도(sensitivity)": tp / sick,    # P(양성판정|실제양성)
        "PPV(정밀도)": tp / positive,        # P(실제양성|양성판정) ← 이게 중요
        "특이도(specificity)": tn / (tn + fp),
    }

    for name, value in metrics.items():
        print(f"{name}: {value:.3f}")

# 예: 사기 탐지 시스템
interpret_classifier_output(tp=95, fp=900, fn=5, tn=89000)
```

---

## 실전 체크리스트

- [ ] `P(A|B)`의 분모가 무엇인지 항상 확인한다
- [ ] AI 모델의 "정확도 N%"가 어떤 조건부확률인지 파악할 수 있다
- [ ] 기저율을 포함해 PPV를 계산할 수 있다
- [ ] 민감도(sensitivity)와 PPV(정밀도)의 차이를 설명할 수 있다
- [ ] 전체확률법칙으로 P(B)를 계산할 수 있다
- [ ] 독립과 종속을 코드로 확인할 수 있다

---

## 처음 질문으로 돌아가기

- **`P(A|B)`와 `P(B|A)`는 왜 전혀 다른 값일 수 있을까요?**
  분모가 다릅니다. P(A|B)는 B 세계 안에서의 A 비율이고, P(B|A)는 A 세계 안에서의 B 비율입니다. AI의 "민감도"와 "정밀도(PPV)"가 다른 이유가 바로 이것입니다.

- **기저율이 낮으면 왜 AI 모델 결과를 과신하면 안 될까요?**
  기저율이 낮으면 실제 양성보다 거짓 양성이 더 많아집니다. 민감도 99%의 모델도 기저율 0.1%에서는 PPV가 9% 수준밖에 안 됩니다.

- **조건부확률이 AI에서는 어떤 형태로 나타날까요?**
  모든 분류 모델의 출력이 조건부확률입니다. P(클래스|입력데이터) = 모델 출력값. 이 조건부 구조를 이해해야 임계값 설정과 비용 기반 의사결정이 가능합니다.

---

## 정리

조건부확률은 AI 모델 출력을 읽는 핵심 도구입니다. 분모가 바뀐다는 것, 조건의 방향이 있다는 것, 기저율이 결과 해석을 바꾼다는 것 — 이 세 가지를 기억하면 AI 모델 결과를 훨씬 정확하게 읽을 수 있습니다. 다음 글에서는 베이즈 정리를 통해 새로운 증거가 들어왔을 때 확률을 어떻게 갱신하는지 다룹니다.

---

## 참고 자료

- [Khan Academy — Conditional probability](https://www.khanacademy.org/math/statistics-probability/probability-library/conditional-probability-independence)
- [Wikipedia — Conditional probability](https://en.wikipedia.org/wiki/Conditional_probability)
- [Wikipedia — Base rate fallacy](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 확률 기초 (1/10): 확률이란 무엇인가?
- 바이브코딩을 위한 확률 기초 (2/10): 사건과 표본공간
- **바이브코딩을 위한 확률 기초 (3/10): 조건부확률 (현재 글)**
- 바이브코딩을 위한 확률 기초 (4/10): 베이즈 정리
- 바이브코딩을 위한 확률 기초 (5/10): 확률변수
- 바이브코딩을 위한 확률 기초 (6/10): 기대값과 분산
- 바이브코딩을 위한 확률 기초 (7/10): 이산분포
- 바이브코딩을 위한 확률 기초 (8/10): 연속분포
- 바이브코딩을 위한 확률 기초 (9/10): 대수의 법칙과 중심극한정리
- 바이브코딩을 위한 확률 기초 (10/10): 머신러닝에서의 확률
<!-- toc:end -->

Tags: 바이브코딩, 확률, 조건부확률, AI확률점수, 기저율
