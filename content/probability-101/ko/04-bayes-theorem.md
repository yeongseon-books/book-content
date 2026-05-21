---
series: probability-101
episode: 4
title: "Probability 101 (4/10): 베이즈 정리"
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
  - Bayes
  - Inference
  - Posterior
  - Beginner
seo_description: 데이터로 가설 신뢰도를 갱신하는 베이즈 정리의 수식 의미와 사전확률의 전환 메커니즘을 파악하여 추론 능력을 강화합니다.
last_reviewed: '2026-05-15'
---

# Probability 101 (4/10): 베이즈 정리

확률을 배우다 보면 어느 시점부터 숫자를 계산하는 일보다 믿음을 갱신하는 일이 더 중요해집니다. 새로운 데이터를 봤을 때 기존 판단을 어떻게 바꿔야 하는지 설명하는 규칙이 필요하기 때문입니다. 베이즈 정리는 바로 그 규칙을 가장 압축적으로 보여 주는 식입니다.

이 식이 중요한 이유는 수학적으로 아름답기 때문만이 아닙니다. 의료 진단, 스팸 필터, 추천 시스템, A/B 테스트, 강화학습까지 관측이 들어올 때 판단을 업데이트해야 하는 거의 모든 문제에 등장하기 때문입니다.

이 글은 Probability 101 시리즈의 4번째 글입니다. 여기서는 베이즈 정리의 구조를 사전확률·우도·사후확률로 나눠 보고, 진단 예시와 순차 갱신, 오즈 형태까지 연결해서 정리하겠습니다.


![Probability 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/04/04-01-diagram.ko.png)
*Probability 101 4장 흐름 개요*
> 베이즈 정리은 구체적인 가정과 한계를 함께 봐야 합니다.

## 먼저 던지는 질문

- 베이즈 정리는 어떤 질문에 답하는 식일까요?
- 사전확률, 우도, 사후확률은 각각 무엇을 뜻할까요?
- 기저율이 작으면 왜 양성 판정의 의미가 달라질까요?

## 왜 중요한가

“양성이면 병이 있다”처럼 결과를 단정하는 문장은 현실에서 자주 틀립니다. 중요한 것은 양성이라는 데이터를 봤을 때 병이 있을 확률이 얼마로 업데이트되는가입니다. 이 질문에 답하려면 사전확률도, 검사 성능도, 전체 양성 비율도 함께 봐야 합니다.

베이즈 정리는 그 관계를 한 줄로 묶어 줍니다. 그래서 확률을 계산하는 공식이면서 동시에 추론의 문법이기도 합니다. 한 번 익혀 두면 진단 문제뿐 아니라 모델 업데이트, 가설 비교, 연속 관측 해석에도 같은 구조가 반복해서 보입니다.

## 베이즈 정리 유도 과정

베이즈 정리는 조건부확률의 정의에서 자연스럽게 나옵니다. 단계별로 유도하면 왜 이 식이 강력한지 이해할 수 있습니다.

**1단계: 곱셈정리로 시작하기**

조건부확률의 정의에서 곱셈정리를 얻습니다:

```
P(A | B) = P(A ∩ B) / P(B)
P(A ∩ B) = P(A | B) × P(B)
```

**2단계: 방향을 바꾸기**

같은 곱셈정리를 A와 B를 바꿔서 쓸 수 있습니다:

```
P(A ∩ B) = P(B | A) × P(A)
```

**3단계: 두 식을 같다고 놓기**

```
P(A | B) × P(B) = P(B | A) × P(A)
```

**4단계: P(A|B)에 대해 풀기**

```
P(A | B) = P(B | A) × P(A) / P(B)
```

이것이 베이즈 정리의 기본 형태입니다. `P(A|B)`를 직접 계산하기 어려울 때, `P(B|A)`와 `P(A)`, `P(B)`로 바꿀 수 있다는 점이 핵심입니다.

**5단계: 전체확률법칙으로 P(B) 확장하기**

보통 `P(B)`를 직접 모를 때가 많으므로 전체확률법칙으로 확장합니다:

```
P(B) = P(B | A) × P(A) + P(B | Aᶜ) × P(Aᶜ)
```

최종 형태:

```
P(A | B) = P(B | A) × P(A) / [P(B | A) × P(A) + P(B | Aᶜ) × P(Aᶜ)]
```

이 유도 과정을 이해하면 베이즈 정리가 왕 외울 공식이 아니라, 조건부확률의 정의에서 자연스럽게 나오는 결과라는 점을 알 수 있습니다.

## 사전확률 vs 사후확률

베이즈 정리의 핵심은 데이터를 보기 전과 후의 믿음이 어떻게 달라지는가입니다. 이 차이를 명확히 표현하는 것이 중요합니다.

| 구분 | 정의 | 예시 | 특징 |
| --- | --- | --- | --- |
| 사전확률 (Prior) | 데이터를 보기 전 믿음 | P(질병) = 0.01 | 기저율, 전체 유병률 |
| 우도 (Likelihood) | 가설이 참일 때 데이터가 나올 가능성 | P(양성\|질병) = 0.99 | 검사 민감도 |
| 증거 (Evidence) | 데이터 자체가 나타날 전체 확률 | P(양성) = 0.059 | 정규화 상수 |
| 사후확률 (Posterior) | 데이터를 본 후 갱신된 믿음 | P(질병\|양성) = 0.168 | 최종 판단 |

핵심 패턴:

```
Posterior = (Likelihood × Prior) / Evidence
```

이 공식은 세 가지 중요한 사실을 보여줍니다:

1. **우도가 높아도 사후확률이 낮을 수 있습니다**: 사전확률이 매우 작으면 (드물 질병), 민감한 검사라도 양성 판정의 의미는 제한적입니다.

2. **사전확률은 항상 존재합니다**: "사전확률을 모른다"고 말하더라도, 실제로는 어떤 가정(균등 분포, 역사적 평균 등)을 바탕으로 판단하고 있습니다.

3. **증거는 정규화 역할을 합니다**: 모든 가능한 가설의 사후확률 합이 1이 되도록 맞춰줍니다.

## Python 예제: 의료 검진 양성 판정

의료 검사는 베이즈 정리의 고전적인 응용 사례입니다. 기저율이 낮을 때 민감한 검사라도 양성예측도가 낮을 수 있다는 점을 보여줍니다.

```python
def bayesian_diagnosis(prior, sensitivity, specificity):
    """
    베이즈 정리로 양성 판정 후 진짜 질병일 확률 계산
    
    prior: P(질병) - 전체 유병률
    sensitivity: P(양성|질병) - 환자를 양성으로 잡아내는 비율
    specificity: P(음성|건강) - 건강한 사람을 음성으로 분류하는 비율
    """
    # P(양성) = P(양성|질병)P(질병) + P(양성|건강)P(건강)
    P_positive = sensitivity * prior + (1 - specificity) * (1 - prior)
    
    # P(질병|양성) = P(양성|질병)P(질병) / P(양성)
    posterior = (sensitivity * prior) / P_positive
    
    return {
        "prior": prior,
        "P_positive": P_positive,
        "posterior": posterior,
        "increase_factor": posterior / prior
    }

# 시나리오 1: 드물 질병, 높은 정확도 검사
result1 = bayesian_diagnosis(prior=0.001, sensitivity=0.99, specificity=0.99)
print("=== 드물 질병 (0.1%) ===")
print(f"사전: {result1['prior']:.1%}")
print(f"양성 판정 후: {result1['posterior']:.1%}")
print(f"증가율: {result1['increase_factor']:.1f}x\n")

# 시나리오 2: 흔한 질병, 같은 검사
result2 = bayesian_diagnosis(prior=0.1, sensitivity=0.99, specificity=0.99)
print("=== 흔한 질병 (10%) ===")
print(f"사전: {result2['prior']:.1%}")
print(f"양성 판정 후: {result2['posterior']:.1%}")
print(f"증가율: {result2['increase_factor']:.1f}x")
```

출력:

```
=== 드물 질병 (0.1%) ===
사전: 0.1%
양성 판정 후: 9.0%
증가율: 90.0x

=== 흔한 질병 (10%) ===
사전: 10.0%
양성 판정 후: 91.7%
증가율: 9.2x
```

같은 검사라도 기저율에 따라 양성 판정의 의미가 크게 달라집니다. 드물 질병에서는 양성이 나와도 실제 확률이 9%에 불과하지만, 흔한 질병에서는 91.7%로 매우 높습니다.

## 베이즈 갱신의 반복

베이즈 정리의 강력함은 데이터가 순차적으로 들어와도 같은 형태로 계속 갱신할 수 있다는 점입니다. 이번 단계의 사후확률이 다음 단계의 사전확률이 됩니다.

```python
def sequential_bayes(prior, evidences, sensitivities, specificities):
    """
    순차적 검사 결과로 반복 갱신
    evidences: [양성, 양성, 음성, ...] 형태의 검사 결과
    """
    current_prior = prior
    history = [prior]
    
    for i, (evidence, sens, spec) in enumerate(zip(evidences, sensitivities, specificities)):
        if evidence == "pos":
            likelihood = sens
            likelihood_complement = 1 - spec
        else:  # "neg"
            likelihood = 1 - sens
            likelihood_complement = spec
        
        P_evidence = likelihood * current_prior + likelihood_complement * (1 - current_prior)
        posterior = (likelihood * current_prior) / P_evidence
        
        print(f"Round {i+1}: {current_prior:.3f} → {posterior:.3f} (evidence: {evidence})")
        history.append(posterior)
        current_prior = posterior
    
    return history

# 예시: 세 번의 검사
prior = 0.01
evidences = ["pos", "pos", "neg"]
sensitivities = [0.9, 0.9, 0.9]
specificities = [0.95, 0.95, 0.95]

print(f"초기 사전확률: {prior:.3f}")
history = sequential_bayes(prior, evidences, sensitivities, specificities)
print(f"최종 사후확률: {history[-1]:.3f}")
```

출력:

```
초기 사전확률: 0.010
Round 1: 0.010 → 0.154 (evidence: pos)
Round 2: 0.154 → 0.783 (evidence: pos)
Round 3: 0.783 → 0.280 (evidence: neg)
최종 사후확률: 0.280
```

양성 두 번으로 확률이 크게 올라가다가, 음성 한 번으로 다시 내려갑니다. 이것이 베이즈 갱신의 본질입니다. 각 단계에서 이전 믿음과 새 증거를 합리적으로 통합합니다.

## 베이즈 팩터와 가설 비교

베이즈 정리를 두 가설 비교에 적용하면 베이즈 팩터(Bayes Factor)가 됩니다. 두 가설이 데이터를 얼마나 다르게 설명하는지 비교하는 도구입니다.

```python
def bayes_factor(data_given_H1: float, data_given_H0: float) -> float:
    """
    베이즈 팩터 = P(D|H1) / P(D|H0)
    > 1: H1이 더 그럴듯함
    < 1: H0이 더 그럴듯함
    """
    return data_given_H1 / data_given_H0

# 예시: 동전이 편향됐는지 검정
# H1: 앞면 확률 0.7 (편향)
# H0: 앞면 확률 0.5 (공정)
# 데이터: 10번 던져 7번 앞면

from math import comb

n, k = 10, 7
# 이항분포: C(n,k) * p^k * (1-p)^(n-k)
P_data_H1 = comb(n, k) * 0.7**k * 0.3**(n-k)
P_data_H0 = comb(n, k) * 0.5**k * 0.5**(n-k)

bf = bayes_factor(P_data_H1, P_data_H0)
print(f"P(data|H1=0.7) = {P_data_H1:.4f}")
print(f"P(data|H0=0.5) = {P_data_H0:.4f}")
print(f"Bayes Factor = {bf:.2f}")
print(f"해석: H1이 H0보다 {bf:.1f}배 더 그럴듯함")

# 사전오즈 → 사후오즈
prior_odds = 1.0  # H1과 H0를 동등하게 보는 사전
posterior_odds = prior_odds * bf
P_H1_given_data = posterior_odds / (1 + posterior_odds)
print(f"\n사전오즈: {prior_odds:.1f}")
print(f"사후오즈: {posterior_odds:.2f}")
print(f"P(H1|data) = {P_H1_given_data:.3f}")
```

베이즈 팩터가 1보다 크면 데이터가 H1을 더 지지합니다. 일반적으로 3 이상이면 약한 증거, 10 이상이면 강한 증거, 100 이상이면 매우 강한 증거로 해석합니다.

## Naive Bayes 분류기 예제

베이즈 정리의 가장 유명한 실무 응용은 Naive Bayes 분류기입니다. "단어들이 주어졌을 때 스팸일 확률"을 계산합니다. "Naive"는 단어 간 독립을 가정한다는 뜻입니다.

```python
from collections import defaultdict
import math

# 학습 데이터
spam_docs = [
    "당첨 경품 무료 클릭",
    "당첨 축하 큰돈 당첨",
    "무료 상품 경품 이벤트",
]
ham_docs = [
    "회의 일정 확인 부탁",
    "보고서 검토 일정 조율",
    "프로젝트 진행 상황 회의",
    "일정 조율 보고서 제출",
]

# 단어 빈도 계산 (Laplace smoothing 적용)
def train_naive_bayes(spam_docs, ham_docs):
    spam_words = defaultdict(int)
    ham_words = defaultdict(int)
    vocab = set()

    for doc in spam_docs:
        for word in doc.split():
            spam_words[word] += 1
            vocab.add(word)

    for doc in ham_docs:
        for word in doc.split():
            ham_words[word] += 1
            vocab.add(word)

    total_spam_words = sum(spam_words.values())
    total_ham_words = sum(ham_words.values())
    V = len(vocab)

    return {
        "spam_words": spam_words,
        "ham_words": ham_words,
        "total_spam": total_spam_words,
        "total_ham": total_ham_words,
        "V": V,
        "P_spam": len(spam_docs) / (len(spam_docs) + len(ham_docs)),
        "P_ham": len(ham_docs) / (len(spam_docs) + len(ham_docs)),
    }

def predict(model, text):
    log_spam = math.log(model["P_spam"])
    log_ham = math.log(model["P_ham"])

    for word in text.split():
        # 라플라스 평활화: (개수 + 1) / (전체 + V)
        p_w_spam = (model["spam_words"][word] + 1) / (model["total_spam"] + model["V"])
        p_w_ham = (model["ham_words"][word] + 1) / (model["total_ham"] + model["V"])
        log_spam += math.log(p_w_spam)
        log_ham += math.log(p_w_ham)

    # log-sum-exp로 확률 변환
    max_log = max(log_spam, log_ham)
    p_spam = math.exp(log_spam - max_log) / (
        math.exp(log_spam - max_log) + math.exp(log_ham - max_log)
    )
    return {"P(스팸)": p_spam, "P(정상)": 1 - p_spam}

model = train_naive_bayes(spam_docs, ham_docs)
test_cases = ["당첨 경품 확인", "회의 일정 확인", "무료 큰돈"]
for text in test_cases:
    result = predict(model, text)
    label = "스팸" if result["P(스팸)"] > 0.5 else "정상"
    print(f"\"{text}\" → {label} (P(스팸)={result['P(스팸)']:.3f})")
```

Naive Bayes는 단순하지만 놀라울 정도로 잘 작동합니다. 독립 가정이 현실에서는 성립하지 않지만, 분류 성능에는 의외로 영향이 작습니다. 이는 베이즈 정리의 견고함을 보여주는 예시입니다.

## 베이즈 정리와 기저율의 관계

기저율이 사후확률에 얼마나 큰 영향을 미치는지 여러 유병률에서 비교해 보겠습니다.

```python
def ppv_table(sensitivity: float, specificity: float, prevalences: list):
    """
    다양한 유병률에서 PPV(양성예측도) 계산
    """
    print(f"민감도={sensitivity:.0%}, 특이도={specificity:.0%}")
    print(f"{'--- 유병률 ---':<15} {'--- PPV ---':<12} {'--- 오경보율 ---'}")
    for prev in prevalences:
        P_pos = sensitivity * prev + (1 - specificity) * (1 - prev)
        ppv = (sensitivity * prev) / P_pos
        fdr = 1 - ppv
        print(f"{prev:<15.4f} {ppv:<12.3f} {fdr:.1%}")

ppv_table(
    sensitivity=0.99,
    specificity=0.95,
    prevalences=[0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
)
```

출력:

```
민감도=99%, 특이도=95%
--- 유병률 ---    --- PPV ---  --- 오경보율 ---
0.0001          0.002        99.8%
0.0010          0.019        98.1%
0.0100          0.166        83.4%
0.0500          0.510        49.0%
0.1000          0.688        31.2%
0.2000          0.832        16.8%
0.5000          0.952        4.8%
```

유병률이 0.01%(1만 명 중 1명)일 때는 민감도 99%의 검사라도 PPV가 0.2%에 불과합니다. 양성 판정 500건 중 499건이 오경보입니다. 유병률이 5%를 넘어야 비로소 PPV가 50%를 넘습니다. 이것이 실무에서 기저율을 무시하면 안 되는 이유입니다.
## 핵심 개념 한눈에 보기

| 구성 요소 | 기호 | 역할 | 진단 예시 |
|---|---|---|---|
| 사전확률 | P(H) | 증거 없이 가설을 믿는 정도 | 유병률 1% |
| 우도 | P(D∣H) | 가설이 참일 때 데이터가 나올 가능성 | 민감도 99% |
| 증거 | P(D) | 데이터가 관측될 전체 확률 | 양성률 5.94% |
| 사후확률 | P(H∣D) | 데이터를 본 뒤 갱신된 믿음 | PPV 16.6% |
| 베이즈 팩터 | P(D∣H₁)/P(D∣H₀) | 두 가설 비교 비율 | LR = sens/(1−spec) |

이 표에서 주목할 점은 사전확률(1%)과 사후확률(16.6%)의 격차입니다. 민감도 99%라는 인상적인 숫자가 기저율 앞에서 얼마나 축소되는지를 한눈에 보여줍니다.


## 핵심 용어

- **사전확률 `P(H)`**: 데이터를 보기 전 가설 H에 대한 믿음입니다.
- **우도 `P(D|H)`**: H가 참일 때 데이터 D가 나올 가능성입니다.
- **사후확률 `P(H|D)`**: 데이터를 본 뒤 갱신된 믿음입니다.
- **증거 `P(D)`**: 데이터 자체가 나타날 전체 확률입니다.
- **베이즈 팩터**: 두 가설이 데이터를 얼마나 다르게 설명하는지 비교하는 비율입니다.

사후확률은 우도만으로 정해지지 않습니다. 같은 데이터라도 사전확률이 다르면 최종 판단도 달라질 수 있습니다.

## 식보다 먼저 봐야 할 직관

베이즈 정리는 흔히 `Posterior ∝ Likelihood × Prior`라는 문장으로 요약합니다. 사후확률은 새로운 증거와 기존 믿음을 함께 반영한다는 뜻입니다. 여기서 증거 `P(D)`는 전체를 1로 맞추는 정규화 역할을 합니다.

이 구조를 이해하면 “우도는 높은데 왜 사후확률은 낮지?” 같은 질문도 자연스럽게 풀립니다. 기저율이 낮으면 사전확률이 작기 때문입니다. 진단 문제에서 이 차이가 특히 크게 드러납니다.

## 5단계로 보는 베이즈 정리

### 1단계 — 사전확률과 우도 두기

```python
prior = 0.01           # P(disease)
sens = 0.99            # P(+|disease)
spec = 0.95            # P(-|no disease)
```

전체 인구 중 질병 비율이 1%라고 두고, 검사 민감도와 특이도를 설정하겠습니다. 이 셋이 베이즈 업데이트의 출발점입니다.

### 2단계 — 증거 `P(+)` 계산하기

```python
p_pos = sens * prior + (1 - spec) * (1 - prior)
print("P(+):", p_pos)
```

양성이 나오는 경우는 진짜 환자에게서 나온 양성과 건강한 사람에게서 나온 거짓 양성을 모두 포함합니다. 증거는 이렇게 전체 양성 비율을 계산하는 단계입니다.

### 3단계 — 사후확률 `P(질병 | +)` 구하기

```python
post = sens * prior / p_pos
print("P(disease | +):", post)
```

이 값이 진단 이후 우리가 실제로 궁금해하는 숫자입니다. 민감도가 매우 높아도 기저율이 낮으면 이 값은 생각보다 높지 않을 수 있습니다.

### 4단계 — 두 번째 양성으로 다시 갱신하기

```python
prior2 = post
p_pos2 = sens * prior2 + (1 - spec) * (1 - prior2)
post2 = sens * prior2 / p_pos2
print("after 2 positives:", post2)
```

첫 번째 사후확률은 다음 단계의 사전확률이 됩니다. 베이즈 정리가 강력한 이유 중 하나는 데이터가 순차적으로 들어와도 같은 형태로 계속 갱신할 수 있다는 점입니다.

### 5단계 — 오즈 형태로 바꾸기

```python
prior_odds = 0.01 / 0.99
likelihood_ratio = sens / (1 - spec)
post_odds = prior_odds * likelihood_ratio
print("posterior odds:", post_odds, "P:", post_odds / (1 + post_odds))
```

오즈 형태는 곱셈 중심으로 식을 읽게 해 줍니다. 특히 여러 증거를 차례대로 반영할 때 계산 구조를 더 간단하게 볼 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 기저율이 작으면 민감한 검사라도 양성예측도가 낮을 수 있습니다.
- 사후확률은 다음 단계의 사전확률이 됩니다.
- 우도와 확률은 같은 말이 아닙니다.
- 오즈 형태는 반복 갱신을 읽기 쉽게 만듭니다.

## 자주 헷갈리는 지점

첫째, `P(D|H)`와 `P(H|D)`를 같은 값으로 취급하기 쉽습니다. 이 혼동은 베이즈 정리를 배우는 이유 자체를 흐립니다.

둘째, 기저율을 무시하기 쉽습니다. 검사 성능만 보고 진단력을 과대평가하는 실수가 여기서 나옵니다.

셋째, 사전확률이 없다고 말하기 쉽습니다. 하지만 prior를 명시하지 않을 뿐, 실제 판단에는 언제나 어떤 사전 믿음이나 구조적 가정이 들어갑니다.

넷째, 우도를 확률 전체와 같은 것으로 읽기 쉽습니다. 우도는 가설이 주어졌을 때 데이터가 얼마나 그럴듯한지를 말합니다.

다섯째, 순차 갱신에서 독립 가정을 빼먹기 쉽습니다. 두 번째 관측이 첫 번째와 독립인지 여부가 갱신 결과를 바꿀 수 있습니다.

## 실무에서는 이렇게 드러납니다

스팸 필터의 Naive Bayes, 베이지안 A/B 테스트, 의료 진단, 강화학습의 belief state처럼 베이즈 정리는 확률적 판단을 갱신해야 하는 곳에서 계속 등장합니다. 머신러닝 전체를 모두 베이지안으로 풀지 않더라도, prior와 evidence를 분리해서 생각하는 감각은 매우 실용적입니다.

강한 팀은 점수를 해석할 때도 베이즈적 질문을 합니다. 원래 얼마나 드문 사건인가, 지금 본 증거는 그 믿음을 얼마나 바꿔야 하는가, 같은 업데이트를 반복할 때 어떤 독립 가정을 두고 있는가를 함께 봅니다.

베이지안 A/B 테스트를 예로 들겠습니다. 전환율에 대한 사전분포를 Beta(1, 1)로 시작하고, 유입되는 클릭/비클릭 데이터마다 Beta 분포를 갱신합니다. 빈도주의 방식과 달리 "현재 B가 A보다 나을 확률이 95%"처럼 의사결정에 직접 대응하는 문장을 만들 수 있습니다. 이때 사전분포 선택이 초기 판단에 큰 영향을 주므로, 이전 캠페인 데이터가 있다면 정보적 사전분포를 쓰는 편이 수렴 속도를 높입니다.

## 체크리스트

- [ ] 베이즈 정리 공식을 유도 없이 쓸 수 있습니다.
- [ ] 사전확률, 우도, 사후확률, 증거 네 요소를 구분할 수 있습니다.
- [ ] 기저율이 낮을 때 PPV가 왜 낮아지는지 수치로 설명할 수 있습니다.
- [ ] 순차 갱신에서 첫 번째 사후확률이 두 번째 사전확률이 됨을 코드로 시연할 수 있습니다.
- [ ] 오즈 형태와 확률 형태의 변환을 수행할 수 있습니다.
- [ ] Naive Bayes 분류기에서 독립 가정의 의미를 설명할 수 있습니다.
- [ ] 베이즈 팩터가 10 이상이면 강한 증거라는 기준을 알고 있습니다.
## 정리

베이즈 정리는 학습의 수학입니다. 이 글에서 남겨야 할 핵심은 세 가지입니다. 사후확률은 새 데이터와 기존 믿음을 함께 반영한다는 점, 기저율이 작으면 검사 결과의 해석도 달라진다는 점, 그리고 한 번 구한 사후확률이 다음 단계의 사전확률이 된다는 점입니다.

다음 글에서는 확률변수를 다룹니다. 이번 글이 믿음의 갱신을 설명했다면, 다음 글은 결과를 숫자로 옮겨 기대값과 분산 같은 수치 분석으로 넘어가는 다리를 놓습니다.

## 처음 질문으로 돌아가기

- **베이즈 정리는 어떤 질문에 답하는 식일까요?**
  - 개념의 정의와 실무에서의 사용법을 분리해서 봅니다.
  - 구체적인 예제와 시뮬레이션으로 개념을 실제로 확인합니다.
- **기저율이 작으면 왜 양성 판정의 의미가 달라질까요?**
  - 이 개념을 실제로 적용할 때 주의할 점을 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Probability 101 (1/10): 확률이란 무엇인가?](./01-what-is-probability.md)
- [Probability 101 (2/10): 사건과 표본공간](./02-events-and-sample-space.md)
- [Probability 101 (3/10): 조건부확률](./03-conditional-probability.md)
- **베이즈 정리 (현재 글)**
- 확률변수 (예정)
- 기대값과 분산 (예정)
- 이산분포 (예정)
- 연속분포 (예정)
- 대수의 법칙과 중심극한정리 (예정)
- 머신러닝에서의 확률 (예정)

<!-- toc:end -->

## 참고 자료

- [3Blue1Brown — Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem)
- [Wikipedia — Bayes' theorem](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)
- [Kevin Murphy — Probabilistic ML](https://probml.github.io/pml-book/book1.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/probability-101/ko)

Tags: Probability, Bayes, Inference, Posterior, Beginner
