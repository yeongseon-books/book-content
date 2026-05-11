---
title: Rubric 기반 채점 설계
series: ai-evaluation-101
episode: 5
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- Rubric
- Multi-Dimensional
- JSON Output
last_reviewed: '2026-05-03'
seo_description: 단순 1-5 점수보다 '정확성', '안전성', '문체' 같은 차원별 rubric이 훨씬 유용합니다.
---

# Rubric 기반 채점 설계

> AI Evaluation 101 시리즈 (5/10)

단순 1-5 점수보다 '정확성', '안전성', '문체' 같은 차원별 rubric이 훨씬 유용합니다. 이 글은 평가 차원을 정의하고, 각 차원의 anchor를 만들고, 점수를 집계하는 방법을 다룹니다.

---
![Rubric 기반 채점 설계](../../../assets/ai-evaluation-101/05/05-01-designing-rubric-based-scoring.ko.png)

*Rubric 기반 채점 설계*

## 단일 점수의 한계

![단일 점수의 한계](../../../assets/ai-evaluation-101/05/05-02-the-limits-of-single-scores.ko.png)

*단일 점수의 한계*
Ep4의 single scoring은 응답에 1~5점을 매깁니다. 그런데 "3점"이 무슨 뜻일까요? 사실이 부정확해서 3점일 수도 있고, 정확하지만 톤이 어색해서 3점일 수도 있습니다. **단일 점수는 무엇이 잘못됐는지 알려주지 않습니다.**

Rubric 기반 채점은 응답을 여러 차원으로 나눠서 각각 점수를 매깁니다. 예를 들어 LLM 챗봇 응답을 다음 4가지로 평가합니다.

| 차원 | 의미 | 점수 |
|-----|------|-----|
| Correctness | 사실이 맞는가 | 1~5 |
| Completeness | 빠진 정보가 없는가 | 1~5 |
| Clarity | 이해하기 쉬운가 | 1~5 |
| Tone | 톤이 적절한가 | 1~5 |

이렇게 하면 "Correctness 5, Tone 2"처럼 **약점을 정확히 짚을 수 있습니다.**

---

## Rubric 차원 정의 — 4단계 프로세스

![Rubric 차원 정의 - 4단계 프로세스](../../../assets/ai-evaluation-101/05/05-03-defining-rubric-dimensions-a-four-step-p.ko.png)

*Rubric 차원 정의 - 4단계 프로세스*
좋은 rubric은 즉흥적으로 만들 수 없습니다. 다음 4단계를 따릅니다.

### Step 1: 사용자 가치에서 차원 도출

"좋은 응답"이 무엇인지 사용자 관점으로 적습니다. 고객 지원 봇의 경우:

- 사용자는 "내 문제를 해결할 수 있나"를 보고 → **Correctness, Completeness**
- 사용자는 "이해할 수 있나"를 보고 → **Clarity**
- 사용자는 "기분 좋게 응대받았나"를 보고 → **Tone, Empathy**

도메인마다 다릅니다. 코드 리뷰 봇이면 Correctness, Specificity, Actionability를 씁니다.

### Step 2: 차원당 anchor 작성

각 차원에 대해 1점, 3점, 5점이 어떤 모습인지 **구체적인 예시**를 작성합니다.

```yaml
# rubric/clarity.yaml
dimension: Clarity
anchors:
  5: |
    응답이 짧고 명확합니다. 한 번 읽으면 이해됩니다.
    예: "API key는 환경변수 OPENAI_API_KEY에 설정하세요."
  3: |
    이해할 수 있지만 한 번 더 읽어야 합니다. 약간 장황하거나 용어가 모호합니다.
    예: "Authentication credential을 환경 설정에서 적절히 구성하면 됩니다."
  1: |
    이해 불가. 전문용어 남발 또는 횡설수설.
    예: "credential provisioning을 위한 implicit context propagation을 활용..."
```

Anchor가 없으면 judge LLM도 사람도 채점이 흔들립니다.

### Step 3: 차원이 독립적인지 검증

두 차원이 비슷한 것을 측정하면 중복입니다. 예: "Accuracy"와 "Correctness"는 같습니다. 50건 샘플로 차원 간 상관관계를 봅니다.

```python
# rubric/check_independence.py
import pandas as pd

df = pd.DataFrame({
    "correctness": [5, 4, 3, 5, 2, ...],
    "clarity":     [4, 3, 4, 5, 3, ...],
    "tone":        [5, 5, 3, 4, 4, ...],
})
print(df.corr())
# 상관계수가 0.9 이상이면 두 차원이 사실상 같음 → 합치거나 제거
```

### Step 4: 3~5개로 제한

차원이 10개를 넘으면 judge가 일관되게 채점하지 못합니다. **핵심 3~5개**로 줄이세요.

---

## Judge prompt에 rubric 넣기

![Judge prompt에 rubric 넣기](../../../assets/ai-evaluation-101/05/05-04-putting-the-rubric-into-the-judge-prompt.ko.png)

*Judge prompt에 rubric 넣기*
Ep4의 single scoring prompt를 rubric으로 확장합니다.

```python
# rubric/judge_rubric.py
from openai import OpenAI
import json

client = OpenAI()

RUBRIC_PROMPT = """다음 차원별로 답변을 1~5점으로 채점하세요.

질문: {question}
답변: {answer}

차원:
1. Correctness — 사실이 정확한가 (5: 모두 맞음, 1: 거짓 정보 포함)
2. Completeness — 핵심 정보가 빠지지 않았나 (5: 완전함, 1: 절반 이상 빠짐)
3. Clarity — 이해하기 쉬운가 (5: 한 번에 이해, 1: 이해 불가)
4. Tone — 톤이 적절한가 (5: 정중하고 전문적, 1: 무례하거나 부적절)

다음 JSON 형식으로만 출력하세요. 다른 텍스트 금지.
{{
  "correctness": <int>,
  "completeness": <int>,
  "clarity": <int>,
  "tone": <int>,
  "reasoning": "한 문장 근거"
}}
"""

def judge_rubric(question: str, answer: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": RUBRIC_PROMPT.format(
            question=question, answer=answer
        )}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    result = judge_rubric(
        "API key는 어디에 설정하나요?",
        "환경변수 OPENAI_API_KEY에 설정하세요."
    )
    print(result)
    # {'correctness': 5, 'completeness': 4, 'clarity': 5, 'tone': 5, 'reasoning': '...'}
```

`response_format={"type": "json_object"}`로 강제하면 파싱 실패가 거의 없습니다.

---

## 점수 집계 — 평균이 답이 아닙니다

![점수 집계 - 평균이 답이 아닙니다](../../../assets/ai-evaluation-101/05/05-05-aggregating-scores-the-mean-is-not-the-a.ko.png)

*점수 집계 - 평균이 답이 아닙니다*
차원별 점수를 어떻게 하나로 합칠까요? 흔한 실수는 **단순 평균**입니다. 이는 약점을 가립니다.

| 응답 | Correct | Complete | Clarity | Tone | 평균 | 진실 |
|-----|---------|----------|---------|------|------|------|
| A | 5 | 5 | 5 | 5 | 5.0 | 우수 |
| B | 1 | 5 | 5 | 5 | 4.0 | **거짓 정보** |

B는 평균 4점이지만 실제로는 **사용 불가**입니다. Correctness 1점은 다른 차원이 무엇이든 fail이어야 합니다.

### 추천 집계 방식 3가지

**방식 1: 가중 평균 + 임계값**

```python
# rubric/aggregate.py
def aggregate_weighted(scores: dict) -> tuple[float, str]:
    weights = {"correctness": 0.5, "completeness": 0.2,
               "clarity": 0.15, "tone": 0.15}
    weighted = sum(scores[k] * weights[k] for k in weights)

    # Correctness 3점 미만이면 무조건 FAIL
    if scores["correctness"] < 3:
        return weighted, "FAIL"
    if weighted >= 4.0:
        return weighted, "PASS"
    return weighted, "REVIEW"
```

**방식 2: 최소값(weakest link)**

```python
def aggregate_min(scores: dict) -> int:
    return min(scores.values())
# 가장 약한 차원이 전체 품질을 결정
```

**방식 3: 차원별로 따로 보고 (집계 없음)**

대시보드에서 4개 차원을 각각 봅니다. 평균을 안 내는 게 가장 정직합니다.

```python
# rubric/dashboard.py
import pandas as pd
df = pd.DataFrame(scored_responses)
print(df[["correctness","completeness","clarity","tone"]].describe())
#         correct  complete  clarity  tone
# mean      4.2      4.5      3.8      4.7
# min       1        2        1        3
```

---

## 사람과의 일치도 — 차원별로 측정

Ep4에서는 단일 점수에 대해 Cohen's kappa를 측정했습니다. Rubric은 **차원별로 따로** kappa를 측정합니다.

```python
# rubric/agreement_per_dim.py
from sklearn.metrics import cohen_kappa_score

dimensions = ["correctness", "completeness", "clarity", "tone"]
for dim in dimensions:
    h = [s[dim] for s in human_scores]
    j = [s[dim] for s in judge_scores]
    k = cohen_kappa_score(h, j, weights="quadratic")
    print(f"{dim}: kappa={k:.3f}")
# correctness: kappa=0.78  ← 신뢰 가능
# completeness: kappa=0.65 ← 신뢰 가능
# clarity:     kappa=0.42  ← 보통, prompt 개선 필요
# tone:        kappa=0.31  ← 약함, anchor 다시 작성
```

차원별 kappa가 다르면 **약한 차원의 anchor를 다시 작성**하세요. 모든 차원이 0.6 이상이 될 때까지 반복합니다.

---

## Common Mistakes

### Mistake 1: 차원을 너무 많이 만듦

Correctness, Completeness, Clarity, Tone, Empathy, Conciseness, Helpfulness, Friendliness... 8개를 만들면 judge가 일관되게 채점하지 못합니다. **3~5개로 제한**하세요.

### Mistake 2: Anchor 없이 차원 이름만 적음

"Clarity (1~5)"만 적고 anchor를 안 쓰면, judge LLM도 사람도 매번 다르게 채점합니다. **차원당 1점/3점/5점 예시는 필수**입니다.

### Mistake 3: 단순 평균으로 집계

Correctness 1점, Tone 5점인 응답을 평균 3점으로 보고하면 거짓 정보를 통과시킵니다. **가중 평균 + 임계값** 또는 **차원별 따로 보기**를 쓰세요.

### Mistake 4: 모든 차원을 같은 가중치로 둠

도메인마다 우선순위가 다릅니다. 의료 챗봇은 Correctness가 70%, 마케팅 봇은 Tone이 30%일 수 있습니다. **사용 사례에 맞춰 가중치 조정**.

### Mistake 5: 차원 간 독립성을 검증하지 않음

Helpfulness와 Completeness가 0.95 상관관계면 사실상 한 차원입니다. **상관관계 0.9 이상이면 합치세요.**

---

## 핵심 요약

- 단일 점수는 약점을 숨깁니다. **3~5개 차원**으로 나누면 무엇이 문제인지 보입니다.
- Rubric 설계 4단계: 사용자 가치 → 차원 정의 → anchor 작성 → 독립성 검증.
- Judge prompt에 차원과 anchor를 넣고 **JSON 출력 강제**로 파싱 실패를 줄입니다.
- 단순 평균은 위험합니다. **가중 평균 + 임계값** 또는 **차원별 따로 보기**를 쓰세요.
- Cohen's kappa를 **차원별로** 측정하고, 0.6 미만 차원의 anchor를 다시 작성하세요.

다음 글에서는 RAG 파이프라인 평가 — retrieval, faithfulness, answer relevance — 를 다룹니다.

---

<!-- toc:begin -->
## AI Evaluation 101 시리즈

- [Ep1 LLM 앱은 왜 평가해야 하는가](./01-why-evaluate-llm-apps.md)
- [Ep2 평가 데이터셋 설계](./02-evaluation-dataset-design.md)
- [Ep3 결정론적 메트릭 — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [Ep4 LLM-as-Judge — 모델로 모델을 평가하기](./04-llm-as-judge.md)
- **Ep5 Rubric 기반 다차원 채점 (현재 글)**
- Ep6 RAG 평가 (예정)
- Ep7 Agent 평가 (예정)
- Ep8 회귀 테스트 (예정)
- Ep9 LLM A/B 테스트 (예정)
- Ep10 프로덕션 평가 (예정)
<!-- toc:end -->

## 참고 자료

- [Liu et al. (2023). G-Eval — NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)
- [Anthropic — Multi-dimensional evaluation patterns](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [LangSmith — Custom Evaluators with Rubrics](https://docs.smith.langchain.com/evaluation/how_to_guides/custom_evaluator)
- [Hugging Face — Evaluating LLMs with multi-dimensional criteria](https://huggingface.co/learn/cookbook/en/llm_judge)

Tags: AI Evaluation, Rubric, Multi-Dimensional, JSON Output
