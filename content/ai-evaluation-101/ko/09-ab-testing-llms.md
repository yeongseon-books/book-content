---
title: LLM A/B 테스팅 — 어느 prompt가 더 나은가
series: ai-evaluation-101
episode: 9
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- A/B Testing
- Statistics
- Win Rate
last_reviewed: '2026-05-03'
seo_description: 두 prompt 중 어느 쪽이 더 나은지 어떻게 결정할까요? 이 글은 paired comparison, win rate…
---

# LLM A/B 테스팅 — 어느 prompt가 더 나은가

> AI Evaluation 101 시리즈 (9/10)

두 prompt 중 어느 쪽이 더 나은지 어떻게 결정할까요? 이 글은 paired comparison, win rate, statistical significance, sample size 계산까지 LLM A/B 테스팅의 실무를 다룹니다.

---
## "더 나아 보인다"는 증거가 아닙니다

새 prompt 또는 새 모델로 바꾸면 흔히 다음과 같이 평가합니다.

> "GPT-4o로 바꿨더니 답변이 더 자연스러워 보여요. 출시합시다."

이는 위험합니다. **30개 샘플의 인상**으로 결정하는 것은 신뢰할 수 없습니다. 진짜 더 나은지 알려면 **통계적 유의성**까지 따져야 합니다.

A/B 테스트는 두 가지 변형(A, B)을 같은 입력에 적용하고 어느 쪽이 통계적으로 유의미하게 더 나은지 판정합니다. 이번 글에서는 다음을 다룹니다.

- Pairwise comparison으로 win rate 측정
- 표본 크기 결정 (몇 개 샘플이 필요한가)
- 통계적 유의성 검증
- Production traffic을 활용한 online A/B

---

## Pairwise Comparison으로 Win Rate 측정

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
    prompt = f"""두 답변 중 어느 쪽이 더 나은지 선택하세요.
질문: {question}
답변 A: {ans_a}
답변 B: {ans_b}
JSON으로 출력: {{"winner": "A" | "B" | "Tie", "reason": "..."}}
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
        # Position bias 통제: 순서 swap (Ep4 참조)
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

---

## 표본 크기 — 몇 개를 평가해야 하는가

10개로 60% vs 40%면 우연일 수 있습니다. 1000개로 같은 비율이면 확실히 다릅니다. 필요한 표본 크기는 **검출하려는 차이(effect size)**에 따라 결정됩니다.

```python
# ab/sample_size.py
import statsmodels.stats.power as smp

def required_sample_size(p_a: float, p_b: float,
                          alpha: float = 0.05, power: float = 0.8) -> int:
    """두 비율을 검정하는 데 필요한 그룹당 표본 크기."""
    effect_size = smp.proportion_effectsize(p_a, p_b)
    n = smp.NormalIndPower().solve_power(
        effect_size=abs(effect_size),
        alpha=alpha,
        power=power,
        alternative="two-sided",
    )
    return int(n) + 1

# 예시: 60% vs 50% 차이를 잡으려면?
print(required_sample_size(0.6, 0.5))  # ~388

# 예시: 55% vs 50% (작은 차이)?
print(required_sample_size(0.55, 0.5))  # ~1565

# 예시: 70% vs 50% (큰 차이)?
print(required_sample_size(0.7, 0.5))  # ~93
```

**경험적 가이드**:
- 작은 차이(5%p) 검출 → ~1500개 필요
- 중간 차이(10%p) 검출 → ~400개 필요
- 큰 차이(20%p) 검출 → ~100개 필요

평가 데이터셋을 처음 설계할 때 이 표를 보고 **목표 effect size를 정하고 그에 맞는 크기**를 준비합니다.

---

## 통계적 유의성 검증 — Two-Proportion Z-Test

Win rate를 비교할 때는 **two-proportion z-test**를 씁니다. 두 모델의 승률이 같은지를 귀무가설로 하고, p-value를 봅니다.

```python
# ab/significance.py
from statsmodels.stats.proportion import proportions_ztest

def is_significantly_better(wins_a: int, wins_b: int,
                              total: int, alpha: float = 0.05) -> dict:
    # Tie는 분모에서 제외하고 양 그룹 wins만 비교
    n_decisive = wins_a + wins_b
    if n_decisive == 0:
        return {"significant": False, "p_value": 1.0, "winner": None}

    count = [wins_a, wins_b]
    nobs = [n_decisive, n_decisive]  # 같은 input 수
    z_stat, p_value = proportions_ztest(count, nobs)

    return {
        "p_value":     p_value,
        "significant": p_value < alpha,
        "winner":      "A" if wins_a > wins_b else "B",
        "win_rate_a":  wins_a / n_decisive,
        "win_rate_b":  wins_b / n_decisive,
    }

# 예시
print(is_significantly_better(wins_a=240, wins_b=160, total=400))
# {'p_value': 0.0001, 'significant': True, 'winner': 'A', 'win_rate_a': 0.6, ...}

print(is_significantly_better(wins_a=22, wins_b=18, total=40))
# {'p_value': 0.52, 'significant': False, 'winner': 'A', ...}
# 같은 60% vs 45%지만 표본이 작아 유의하지 않음
```

**해석**:
- `p_value < 0.05`: 차이가 우연이 아닐 가능성 95% 이상 → A를 선택해도 됨.
- `p_value >= 0.05`: 차이를 신뢰할 수 없음 → 추가 표본 필요 또는 무승부 처리.

---

## 효과 크기 (Effect Size) — 통계적 유의성 ≠ 실용적 유의성

표본이 1만 개면 51% vs 50%도 통계적으로 유의합니다. 하지만 **1%p 차이는 실용적으로 의미가 없습니다.** 통계적 유의성과 효과 크기를 함께 봐야 합니다.

```python
# ab/effect_size.py
def cohen_h(p1: float, p2: float) -> float:
    """두 비율의 effect size (Cohen's h)."""
    import math
    phi1 = 2 * math.asin(math.sqrt(p1))
    phi2 = 2 * math.asin(math.sqrt(p2))
    return abs(phi1 - phi2)

# 해석 (Cohen, 1988):
# 0.2 = 작음, 0.5 = 중간, 0.8 = 큼
print(cohen_h(0.51, 0.50))  # 0.020 ← 무시해도 됨
print(cohen_h(0.60, 0.50))  # 0.201 ← 작지만 의미 있음
print(cohen_h(0.70, 0.50))  # 0.412 ← 분명히 의미 있음
```

**판정 규칙**:
- p < 0.05 **그리고** Cohen's h > 0.2 → 새 변형으로 교체.
- p < 0.05이지만 h < 0.2 → 통계적으로는 다르지만 실용적 차이 없음. 비용/latency 등 다른 기준으로 판단.

---

## Online A/B — Production Traffic 활용

Offline eval (위)은 평가 데이터셋에 의존합니다. Production에서는 **실제 사용자 traffic**을 두 그룹으로 나눠 비교할 수 있습니다.

```python
# ab/online_router.py
import hashlib

def assign_variant(user_id: str, experiment: str) -> str:
    """user_id를 hash해서 안정적으로 A 또는 B에 할당."""
    h = hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()
    return "A" if int(h, 16) % 2 == 0 else "B"

def handle_request(user_id: str, question: str) -> str:
    variant = assign_variant(user_id, experiment="prompt-v3-vs-v2")
    model = "gpt-4o" if variant == "A" else "gpt-4o-mini"
    response = get_response(model, question)
    log_metric(user_id, variant, response)  # 나중에 분석용
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
print(f"A 만족도: {a.mean():.3f}, B: {b.mean():.3f}, p={p:.4f}")
```

**Online의 함정**: novelty effect (새 변형이 처음에는 신선해 보임), 외부 이벤트(주말/평일), 사용자 segmentation. 최소 1주, 가능하면 2주는 돌리세요.

---

## Common Mistakes

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

---

## 핵심 요약

- "더 나아 보인다"는 증거가 아닙니다. **win rate + 통계적 유의성 + effect size** 3개를 함께 봅니다.
- Pairwise judge로 win rate를 측정하되 **position bias swap** 필수 (Ep4).
- 표본 크기는 검출하려는 차이에 따라 결정 — 5%p에 ~1500, 10%p에 ~400.
- Two-proportion z-test로 p-value를, Cohen's h로 effect size를 봅니다.
- Online A/B는 실제 production traffic으로 검증. **최소 1~2주** 돌립니다.

다음 글에서는 production에서의 **continuous evaluation** — 라이브 트래픽 샘플링, drift 감지 — 를 다룹니다.

---

<!-- toc:begin -->
## AI Evaluation 101 시리즈

- [Ep1 LLM 앱은 왜 평가해야 하는가](./01-why-evaluate-llm-apps.md)
- [Ep2 평가 데이터셋 설계](./02-evaluation-dataset-design.md)
- [Ep3 결정론적 메트릭 — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [Ep4 LLM-as-Judge — 모델로 모델을 평가하기](./04-llm-as-judge.md)
- [Ep5 Rubric 기반 다차원 채점](./05-rubric-based-scoring.md)
- [Ep6 RAG 평가](./06-rag-evaluation.md)
- [Ep7 Agent 평가](./07-agent-evaluation.md)
- [Ep8 회귀 테스트](./08-regression-testing.md)
- **Ep9 LLM A/B 테스트 (현재 글)**
- Ep10 프로덕션 평가 (예정)
<!-- toc:end -->

## 참고 자료

- [statsmodels — proportions_ztest](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html)
- [Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832)
- [Kohavi, Tang, Xu — Trustworthy Online Controlled Experiments (2020)](https://experimentguide.com/)
- [Chatbot Arena — Crowdsourced LLM A/B (Chiang et al., 2024)](https://arxiv.org/abs/2403.04132)

Tags: AI Evaluation, A/B Testing, Statistics, Win Rate
