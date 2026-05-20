---
title: "AI Evaluation 101 (9/10): LLM A/B 테스팅 — 어느 prompt가 더 나은가"
series: ai-evaluation-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- A/B Testing
- Statistics
- Win Rate
last_reviewed: '2026-05-12'
seo_description: 두 prompt 중 어느 쪽이 더 나은지 어떻게 결정할까요? 이 글은 paired comparison, win rate…
---

# AI Evaluation 101 (9/10): LLM A/B 테스팅 — 어느 prompt가 더 나은가

프롬프트나 모델을 바꾼 뒤 팀 채널에서 가장 자주 나오는 말은 '이쪽이 좀 더 좋아 보인다'입니다. 문제는 이 말만으로는 운영 결정을 내릴 수 없다는 점입니다. 소수 예시에서 좋아 보인 차이는 우연일 수 있고, 반대로 미세한 개선은 충분한 표본 없이는 눈에 잘 띄지 않습니다.

LLM에서는 특히 표현 자유도가 높아 단순 평균 점수보다 pairwise 비교가 더 실용적일 때가 많습니다. 같은 입력에서 A와 B를 나란히 놓고 어느 쪽이 더 나은지 반복해서 묻는 방식입니다.

현업에서 저는 표본 크기와 effect size를 빼먹은 A/B 테스트가 가장 자주 오판을 낳는다고 느꼈습니다. 작은 표본에서 얻은 승률은 과장되기 쉽고, 반대로 엄청 큰 표본에서는 실무적으로 의미 없는 차이도 통계적으로만 유의해질 수 있습니다.

이 글은 AI Evaluation 101 시리즈의 9번째 글입니다.

여기서는 pairwise win rate, 표본 크기 계산, 통계적 유의성, effect size, 그리고 운영 트래픽 기반 online A/B까지 실무 흐름으로 정리하겠습니다.

## 먼저 던지는 질문

- LLM A/B 테스트는 왜 “더 좋아 보인다”는 감상이 아니라 통계적 의사결정이어야 할까요?
- win rate, sample size, statistical significance는 각각 어떤 판단을 도와줄까요?
- 온라인 A/B에서 사용자 위험을 줄이려면 어떤 guardrail metric이 필요할까요?

## 큰 그림

![LLM A/B 테스팅 - prompt 비교](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/09/09-01-a-b-testing-llms-which-prompt-is-better.ko.png)

*LLM A/B 테스팅 - prompt 비교*

이 그림에서는 두 prompt나 모델 후보를 pairwise로 비교하고 win rate와 통계적 유의성을 통해 배포 판단을 내리는 흐름을 봅니다. A/B 테스트는 취향 대결이 아니라 불확실성을 줄이는 실험 설계입니다.

> LLM A/B 테스트의 목표는 더 좋아 보이는 후보를 고르는 것이 아니라, 더 낫다고 말할 근거를 만드는 것입니다.

## 왜 이 글이 중요한가

A/B 테스트는 좋은 느낌을 증거로 바꾸는 과정입니다. 같은 입력에서 어떤 변형이 더 자주 이기는지 기록하면, 팀의 논의가 취향이 아니라 데이터 위에서 진행됩니다.

또한 비용과 지연 같은 운영 특성을 함께 볼 수 있습니다. 답 품질 차이가 미미하다면 더 싼 모델이 나을 수 있고, 반대로 작은 품질 차이라도 특정 도메인에서는 충분히 교체 가치가 있을 수 있습니다.

그래서 A/B 테스트의 핵심은 승률 하나가 아닙니다. 승률, 표본 크기, 통계적 유의성, 효과 크기를 함께 묶어야 실무적인 결론이 나옵니다.

## 핵심 관점

이 주제는 개별 기법을 외우기보다 먼저 어떤 운영 문제를 풀기 위한 장치인지 붙잡아 두는 편이 이해가 빠릅니다. A/B 테스트는 좋은 느낌을 증거로 바꾸는 과정입니다. 같은 입력에서 어떤 변형이 더 자주 이기는지 기록하면, 팀의 논의가 취향이 아니라 데이터 위에서 진행됩니다.

> '더 자연스럽다'는 인상은 출발점일 뿐입니다. 같은 입력에서 누가 더 자주 이기고, 그 차이가 우연이 아닐 만큼 충분한 표본에서 나타났는지까지 봐야 비로소 교체 결정을 내릴 수 있습니다.

이 관점을 먼저 잡아 두면 뒤에 나오는 코드와 지표를 기능 설명이 아니라 운영 설계 관점에서 읽을 수 있습니다. 결국 중요한 것은 수치 이름보다, 그 수치가 어떤 의사결정을 가능하게 하느냐입니다.

## 핵심 개념

LLM A/B 테스팅 - prompt 비교

### "더 나아 보인다"는 증거가 아닙니다

!["더 나아 보인다"는 증거가 아닙니다](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/09/09-01-looks-better-is-not-evidence.ko.png)

"더 나아 보인다"는 증거가 아닙니다
새 prompt 또는 새 모델로 바꾸면 흔히 다음과 같이 평가합니다.

> "GPT-4o로 바꿨더니 답변이 더 자연스러워 보여요. 출시합시다."

이는 위험합니다. **30개 샘플의 인상**으로 결정하는 것은 신뢰할 수 없습니다. 진짜 더 나은지 알려면 **통계적 유의성**까지 따져야 합니다.

A/B 테스트는 두 가지 변형(A, B)을 같은 입력에 적용하고 어느 쪽이 통계적으로 유의미하게 더 나은지 판정합니다. 이번 글에서는 다음을 다룹니다.

- Pairwise comparison으로 win rate 측정
- 표본 크기 결정 (몇 개 샘플이 필요한가)
- 통계적 유의성 검증
- Production traffic을 활용한 online A/B

### Pairwise Comparison으로 Win Rate 측정

![Pairwise Comparison으로 Win Rate 측정](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/09/09-03-pairwise-comparison-and-win-rate.ko.png)

Pairwise Comparison으로 Win Rate 측정
Ep4에서 본 pairwise judge를 활용합니다. 같은 입력에 모델 A와 B의 응답을 받고, judge가 어느 쪽이 나은지 판정합니다.

```python
# ab/pairwise_winrate.py
from openai import OpenAI
import json

client = OpenAI()

def get_response(model: str, question: str) -> str:
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        temperature=0,
    ).choices[0].message.content

def judge_pairwise(question, ans_a, ans_b) -> str:
    prompt = f"""Pick the better answer.
Question: {question}
Answer A: {ans_a}
Answer B: {ans_b}
Output JSON: {{"winner": "A" | "B" | "Tie", "reason": "..."}}
"""
    r = client.chat.completions.create(
        model="gpt-4o", temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(r.choices[0].message.content)["winner"]

def ab_test(questions: list[str], model_a: str, model_b: str) -> dict:
    results = {"A": 0, "B": 0, "Tie": 0}
    for q in questions:
        ans_a = get_response(model_a, q)
        ans_b = get_response(model_b, q)
        # Control position bias by swapping (Ep4)
        v1 = judge_pairwise(q, ans_a, ans_b)
        v2 = judge_pairwise(q, ans_b, ans_a)
        flip = {"A": "B", "B": "A", "Tie": "Tie"}
        if v1 == flip[v2]:
            results[v1] += 1
        else:
            results["Tie"] += 1
    total = sum(results.values())
    return {
        "win_rate_a": results["A"] / total,
        "win_rate_b": results["B"] / total,
        "tie_rate":   results["Tie"] / total,
        "n":          total,
    }
```

**Win rate 해석**:
- A 60%, B 30%, Tie 10% → A가 더 나아 보임
- 하지만 **이게 통계적으로 유의한가?** 가 핵심.

### 표본 크기 — 몇 개를 평가해야 하는가

![표본 크기 - 필요 샘플 수](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/09/09-04-sample-size-how-many-to-evaluate.ko.png)

표본 크기 - 필요 샘플 수
10개로 60% vs 40%면 우연일 수 있습니다. 1000개로 같은 비율이면 확실히 다릅니다. 필요한 표본 크기는 **검출하려는 차이(effect size)**에 따라 결정됩니다.

```python
# ab/sample_size.py
import statsmodels.stats.power as smp

def required_sample_size(p_a: float, p_b: float,
                          alpha: float = 0.05, power: float = 0.8) -> int:
    """Per-group sample size to detect a difference between two proportions."""
    effect_size = smp.proportion_effectsize(p_a, p_b)
    n = smp.NormalIndPower().solve_power(
        effect_size=abs(effect_size),
        alpha=alpha,
        power=power,
        alternative="two-sided",
    )
    return int(n) + 1

# To detect 60% vs 50%
print(required_sample_size(0.6, 0.5))  # ~388

# 55% vs 50% (small difference)
print(required_sample_size(0.55, 0.5))  # ~1565

# 70% vs 50% (large difference)
print(required_sample_size(0.7, 0.5))  # ~93
```

**경험적 가이드**:
- 작은 차이(5%p) 검출 → ~1500개 필요
- 중간 차이(10%p) 검출 → ~400개 필요
- 큰 차이(20%p) 검출 → ~100개 필요

평가 데이터셋을 처음 설계할 때 이 표를 보고 **목표 effect size를 정하고 그에 맞는 크기**를 준비합니다.

### 통계적 유의성 검증 — Two-Proportion Z-Test

![통계적 유의성 검증 - Two-Proportion Z-Test](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/09/09-05-statistical-significance-two-proportion.ko.png)

통계적 유의성 검증 - Two-Proportion Z-Test
Win rate를 비교할 때는 **two-proportion z-test**를 씁니다. 두 모델의 승률이 같은지를 귀무가설로 하고, p-value를 봅니다.

```python
# ab/significance.py
from statsmodels.stats.proportion import proportions_ztest

def is_significantly_better(wins_a: int, wins_b: int,
                              total: int, alpha: float = 0.05) -> dict:
    # Drop ties from the denominator; compare wins_a vs wins_b
    n_decisive = wins_a + wins_b
    if n_decisive == 0:
        return {"significant": False, "p_value": 1.0, "winner": None}

    count = [wins_a, wins_b]
    nobs = [n_decisive, n_decisive]
    z_stat, p_value = proportions_ztest(count, nobs)

    return {
        "p_value":     p_value,
        "significant": p_value < alpha,
        "winner":      "A" if wins_a > wins_b else "B",
        "win_rate_a":  wins_a / n_decisive,
        "win_rate_b":  wins_b / n_decisive,
    }

print(is_significantly_better(wins_a=240, wins_b=160, total=400))
# {'p_value': 0.0001, 'significant': True, 'winner': 'A', 'win_rate_a': 0.6, ...}

print(is_significantly_better(wins_a=22, wins_b=18, total=40))
# {'p_value': 0.52, 'significant': False, 'winner': 'A', ...}
# Same 60% vs 45% but the sample is too small
```

해석:
- `p_value < 0.05`: 차이가 우연이 아닐 가능성 95% 이상 → A를 선택해도 됨.
- `p_value >= 0.05`: 차이를 신뢰할 수 없음 → 추가 표본 필요 또는 무승부 처리.

### 효과 크기 (Effect Size) — 통계적 유의성 ≠ 실용적 유의성

표본이 1만 개면 51% vs 50%도 통계적으로 유의합니다. 하지만 **1%p 차이는 실용적으로 의미가 없습니다.** 통계적 유의성과 효과 크기를 함께 봐야 합니다.

```python
# ab/effect_size.py
import math

def cohen_h(p1: float, p2: float) -> float:
    """Effect size (Cohen's h) between two proportions."""
    phi1 = 2 * math.asin(math.sqrt(p1))
    phi2 = 2 * math.asin(math.sqrt(p2))
    return abs(phi1 - phi2)

# Interpretation (Cohen, 1988):
# 0.2 = small, 0.5 = medium, 0.8 = large
print(cohen_h(0.51, 0.50))  # 0.020 ← negligible
print(cohen_h(0.60, 0.50))  # 0.201 ← small but meaningful
print(cohen_h(0.70, 0.50))  # 0.412 ← clearly meaningful
```

**판정 규칙**:
- p < 0.05 그리고 Cohen's h > 0.2 → 새 변형으로 교체.
- p < 0.05이지만 h < 0.2 → 통계적으로는 다르지만 실용적 차이 없음. 비용/latency 등 다른 기준으로 판단.

### Online A/B — Production Traffic 활용

Offline eval (위)은 평가 데이터셋에 의존합니다. Production에서는 **실제 사용자 traffic**을 두 그룹으로 나눠 비교할 수 있습니다.

```python
# ab/online_router.py
import hashlib

def assign_variant(user_id: str, experiment: str) -> str:
    """Stable A/B assignment by hashing user_id."""
    h = hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()
    return "A" if int(h, 16) % 2 == 0 else "B"

def handle_request(user_id: str, question: str) -> str:
    variant = assign_variant(user_id, experiment="prompt-v3-vs-v2")
    model = "gpt-4o" if variant == "A" else "gpt-4o-mini"
    response = get_response(model, question)
    log_metric(user_id, variant, response)
    return response
```

**Online metric 예시**:
- 사용자가 응답에 "👍" 또는 "👎"를 누르는 비율
- 후속 메시지에서 사용자가 다시 묻는 비율 (낮을수록 좋음)
- 세션 종료까지 걸린 시간

```python
# ab/online_analysis.py
import pandas as pd
from scipy.stats import ttest_ind

df = pd.read_sql("SELECT variant, thumbs_up FROM events WHERE experiment='...'", conn)
a = df[df.variant == "A"]["thumbs_up"]
b = df[df.variant == "B"]["thumbs_up"]
t, p = ttest_ind(a, b, equal_var=False)
print(f"A satisfaction: {a.mean():.3f}, B: {b.mean():.3f}, p={p:.4f}")
```

**Online의 함정**: novelty effect (새 변형이 처음에는 신선해 보임), 외부 이벤트(주말/평일), 사용자 segmentation. 최소 1주, 가능하면 2주는 돌리세요.

## 이 코드에서 먼저 봐야 할 점

- `ab_test` 함수는 pairwise 비교와 위치 편향 통제를 함께 묶어 놓은 가장 실용적인 골격입니다.
- 표본 크기 계산 예제는 작은 차이를 잡으려면 왜 생각보다 많은 샘플이 필요한지 보여 줍니다. 여기서 준비가 안 되면 실험 해석이 흔들립니다.
- p-value와 Cohen's h를 같이 보는 규칙은 온라인 실험에서도 그대로 이어집니다. 유의하다고 다 바꿀 수 있는 것은 아닙니다.

이 세 지점을 먼저 읽고 나면 세부 구현과 지표 해석이 훨씬 빨라집니다. 코드가 길어 보여도 운영 질문은 대개 여기로 다시 돌아옵니다.

## 어디서 자주 헷갈릴까요?

### Mistake 1: 표본 크기 무시

20개 보고 "A가 좋네!" 결정. 그 결정은 거의 확실히 우연. **검출하려는 effect size에 맞춰 표본 크기를 미리 계산**.

### Mistake 2: 통계적 유의성만 보고 효과 크기 무시

대규모 데이터에서는 무의미한 차이도 유의해집니다. **p-value와 effect size를 함께** 보세요.

### Mistake 3: Position bias 통제 안 함

Pairwise judge는 첫 번째를 선호합니다 (Ep4). A/B 결과가 사실상 position 효과일 수 있습니다. **항상 순서 swap**.

### Mistake 4: Tie를 무시

Tie 비율이 50%면 두 모델은 사실상 같습니다. Win rate만 보면 사소한 차이가 과장됩니다. **Tie rate도 함께 보고**, 너무 높으면 judge prompt가 모호하다는 신호.

### Mistake 5: Online A/B를 너무 짧게 돌림

3일 돌리고 결정하면 novelty effect와 요일 효과가 섞여 결과가 왜곡됩니다. **최소 1주, 권장 2주**.

현업에서 제가 가장 자주 보는 문제는 결과 숫자만 보고 원인 분해를 건너뛰는 습관입니다. 평가가 개선을 돕지 못하고 보고서용 숫자로만 남는 순간, 팀은 다시 감각에 의존하게 됩니다.

## 첫 번째 운영 체크리스트

- [ ] pairwise 비교에서 순서 교차를 기본으로 두는가
- [ ] 검출하려는 효과 크기에 맞춰 표본 수를 미리 계산하는가
- [ ] win rate뿐 아니라 tie rate도 함께 기록하는가
- [ ] p-value와 effect size를 함께 해석하는가
- [ ] online A/B를 최소 1주 이상 유지하는가

## 실무에서는 이렇게 생각한다

실무에서는 승률 차이보다 무승부 비율도 중요합니다. tie가 높다면 두 변형이 사실상 비슷하거나 judge 프롬프트가 모호하다는 뜻일 수 있습니다.

또한 온라인 A/B는 계절성, 요일 효과, 신규성 효과를 함께 봐야 합니다. 주중과 주말 트래픽이 다르면 3일짜리 실험은 결론을 왜곡하기 쉽습니다.

다음 글의 운영 평가로 가면 이런 실험이 일회성이 아니라 지속적 루프 속에 들어갑니다. 어떤 변형이 이겼는지도 중요하지만, 배포 후에도 계속 이기고 있는지 확인해야 하기 때문입니다.

## 정리: A/B 테스트는 감각을 통계적 배포 판단으로 바꾸는 절차입니다

- "더 나아 보인다"는 증거가 아닙니다. **win rate + 통계적 유의성 + effect size** 3개를 함께 봅니다.
- Pairwise judge로 win rate를 측정하되 **position bias swap** 필수 (Ep4).
- 표본 크기는 검출하려는 차이에 따라 결정 — 5%p에 ~1500, 10%p에 ~400.
- Two-proportion z-test로 p-value를, Cohen's h로 effect size를 봅니다.
- Online A/B는 실제 production traffic으로 검증. **최소 1~2주** 돌립니다.

다음 글에서는 배포 후 운영 환경에서 평가를 계속 돌리는 방법을 다룹니다. 실험에서 이긴 변형도 운영에서 분포가 바뀌면 다시 확인해야 합니다.

## 운영 체크리스트

- [ ] pairwise win rate와 tie rate를 함께 기록하기
- [ ] 표본 수를 감으로 정하지 않기
- [ ] p-value만 보고 교체하지 않기
- [ ] online A/B는 최소 1~2주 운영하기
- [ ] 품질 차이가 작으면 비용과 지연도 함께 비교하기

## 처음 질문으로 돌아가기

- **LLM A/B 테스트는 왜 “더 좋아 보인다”는 감상이 아니라 통계적 의사결정이어야 할까요?**
  - LLM 출력은 분산이 크고 사람 인상은 편향되기 쉬워, 표본과 효과 크기 없이 판단하면 우연을 개선으로 착각합니다.
- **win rate, sample size, statistical significance는 각각 어떤 판단을 도와줄까요?**
  - win rate는 어느 후보가 더 자주 이기는지, sample size는 판단에 필요한 관측량, significance는 우연일 가능성을 판단하게 해 줍니다.
- **온라인 A/B에서 사용자 위험을 줄이려면 어떤 guardrail metric이 필요할까요?**
  - 불만률, latency, 비용, safety violation, fallback rate 같은 guardrail을 함께 봐야 품질 win이 사용자 위험으로 바뀌지 않습니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가](./01-why-evaluate-llm-apps.md)
- [AI Evaluation 101 (2/10): 평가 데이터셋 설계하기](./02-evaluation-dataset-design.md)
- [AI Evaluation 101 (3/10): 결정적 지표 — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [AI Evaluation 101 (4/10): LLM-as-Judge — 모델로 모델을 평가하기](./04-llm-as-judge.md)
- [AI Evaluation 101 (5/10): Rubric 기반 채점 설계](./05-rubric-based-scoring.md)
- [AI Evaluation 101 (6/10): RAG 시스템 평가하기](./06-rag-evaluation.md)
- [AI Evaluation 101 (7/10): 에이전트 평가하기 — 단일 응답이 아닌 trajectory](./07-agent-evaluation.md)
- [AI Evaluation 101 (8/10): 회귀 테스트 — 어제 잘 되던 게 오늘 망가지지 않게](./08-regression-testing.md)
- **AI Evaluation 101 (9/10): LLM A/B 테스팅 — 어느 prompt가 더 나은가 (현재 글)**
- AI Evaluation 101 (10/10): 운영 환경에서의 지속적 평가 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [statsmodels — proportions_ztest](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html)
- [Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832)
- [Kohavi, Tang, Xu — Trustworthy Online Controlled Experiments (2020)](https://experimentguide.com/)
- [Chatbot Arena — Crowdsourced LLM A/B (Chiang et al., 2024)](https://arxiv.org/abs/2403.04132)

### 관련 시리즈

- [이전 글 — 회귀 테스트 — 어제 잘 되던 게 오늘 망가지지 않게](./08-regression-testing.md)
- [다음 글 — 운영 환경에서의 지속적 평가](./10-production-evaluation.md)
- [시리즈 현재 위치 다시 보기](./09-ab-testing-llms.md)

Tags: AI Evaluation, A/B Testing, Statistics, Win Rate
