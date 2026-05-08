
# Designing Rubric-Based Scoring

> AI Evaluation 101 Series (5/10)

Per-dimension rubrics like 'accuracy', 'safety', and 'tone' are far more useful than a single 1-5 score. This post covers defining evaluation dimensions, writing anchors for each, and aggregating scores.

---
![Designing Rubric-Based scoring](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/05/05-01-designing-rubric-based-scoring.en.png)

*Designing Rubric-Based scoring*
## The Limits of Single Scores

![The limits of single scores](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/05/05-02-the-limits-of-single-scores.en.png)

*The limits of single scores*
Ep4 covered single scoring: one number from 1 to 5. But what does "3" actually mean? It could be 3 because the facts are wrong, or 3 because the tone is off. **A single score does not tell you what is broken.**

Rubric-based scoring breaks each response into multiple dimensions and grades each separately. For an LLM chatbot, you might use:

| Dimension | Meaning | Score |
|----------|---------|-------|
| Correctness | Are the facts right | 1-5 |
| Completeness | Is anything missing | 1-5 |
| Clarity | Is it easy to understand | 1-5 |
| Tone | Is the tone appropriate | 1-5 |

Now you can pinpoint weakness: "Correctness 5, Tone 2."

---

## Defining Rubric Dimensions — A Four-Step Process

![Defining rubric dimensions - A Four-Step process](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/05/05-03-defining-rubric-dimensions-a-four-step-p.en.png)

*Defining rubric dimensions - A Four-Step process*
A good rubric is not improvised. Use these four steps.

### Step 1: Derive dimensions from user value

Write what "a good response" means from the user's view. For a customer support bot:

- The user asks "Did this solve my problem?" → **Correctness, Completeness**
- The user asks "Can I understand it?" → **Clarity**
- The user asks "Did the bot treat me well?" → **Tone, Empathy**

Domains differ. A code-review bot might use Correctness, Specificity, Actionability instead.

### Step 2: Write anchors per dimension

For each dimension, give **concrete examples** of what 1, 3, and 5 look like.

```yaml
# rubric/clarity.yaml
dimension: Clarity
anchors:
  5: |
    Short and clear. Understood on first read.
    Example: "Set the API key in the OPENAI_API_KEY environment variable."
  3: |
    Understandable, but you have to re-read. Slightly verbose or vague.
    Example: "Configure the authentication credential appropriately in your environment settings."
  1: |
    Incomprehensible. Jargon dump or rambling.
    Example: "Leverage implicit context propagation for credential provisioning..."
```

Without anchors, both the judge LLM and humans grade inconsistently.

### Step 3: Verify dimensions are independent

If two dimensions measure the same thing, they are redundant. "Accuracy" and "Correctness" are the same. Check correlation across 50 samples.

```python
# rubric/check_independence.py
import pandas as pd

df = pd.DataFrame({
    "correctness": [5, 4, 3, 5, 2, ...],
    "clarity":     [4, 3, 4, 5, 3, ...],
    "tone":        [5, 5, 3, 4, 4, ...],
})
print(df.corr())
# Correlation > 0.9 means the two dimensions are effectively the same
# → merge or drop one
```

### Step 4: Cap at 3-5 dimensions

Beyond 10 dimensions the judge cannot grade consistently. **Stick to 3-5 core ones.**

---

## Putting the Rubric Into the Judge Prompt

![Putting the rubric into the judge prompt](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/05/05-04-putting-the-rubric-into-the-judge-prompt.en.png)

*Putting the rubric into the judge prompt*
Extend the Ep4 single-score prompt with the rubric.

```python
# rubric/judge_rubric.py
from openai import OpenAI
import json

client = OpenAI()

RUBRIC_PROMPT = """Grade the answer on each dimension from 1 to 5.

Question: {question}
Answer: {answer}

Dimensions:
1. Correctness — Are the facts right (5: all correct, 1: contains false info)
2. Completeness — Is the key information complete (5: complete, 1: more than half missing)
3. Clarity — Easy to understand (5: understood on first read, 1: incomprehensible)
4. Tone — Appropriate tone (5: polite and professional, 1: rude or off)

Respond with JSON only. No other text.
{{
  "correctness": <int>,
  "completeness": <int>,
  "clarity": <int>,
  "tone": <int>,
  "reasoning": "one-sentence justification"
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
        "Where do I set the API key?",
        "Set it in the OPENAI_API_KEY environment variable."
    )
    print(result)
    # {'correctness': 5, 'completeness': 4, 'clarity': 5, 'tone': 5, 'reasoning': '...'}
```

Forcing `response_format={"type": "json_object"}` almost eliminates parse failures.

---

## Aggregating Scores — The Mean Is Not the Answer

![Aggregating scores - the mean is not the answer](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/05/05-05-aggregating-scores-the-mean-is-not-the-a.en.png)

*Aggregating scores - the mean is not the answer*
How do you collapse per-dimension scores into one number? The common mistake is **plain averaging**, which hides weakness.

| Response | Correct | Complete | Clarity | Tone | Mean | Reality |
|---------|---------|----------|---------|------|------|---------|
| A | 5 | 5 | 5 | 5 | 5.0 | Excellent |
| B | 1 | 5 | 5 | 5 | 4.0 | **Hallucination** |

B averages 4 but is **unusable**. A 1 in Correctness must be a fail no matter what other dimensions look like.

### Three recommended aggregation strategies

**Strategy 1: Weighted average + threshold**

```python
# rubric/aggregate.py
def aggregate_weighted(scores: dict) -> tuple[float, str]:
    weights = {"correctness": 0.5, "completeness": 0.2,
               "clarity": 0.15, "tone": 0.15}
    weighted = sum(scores[k] * weights[k] for k in weights)

    # Correctness < 3 is an automatic FAIL
    if scores["correctness"] < 3:
        return weighted, "FAIL"
    if weighted >= 4.0:
        return weighted, "PASS"
    return weighted, "REVIEW"
```

**Strategy 2: Minimum (weakest link)**

```python
def aggregate_min(scores: dict) -> int:
    return min(scores.values())
# The weakest dimension defines overall quality
```

**Strategy 3: No aggregation — report per dimension**

Show all four dimensions on the dashboard. Refusing to average is the most honest option.

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

## Agreement With Humans — Per Dimension

Ep4 measured Cohen's kappa on a single score. With a rubric you measure kappa **per dimension**.

```python
# rubric/agreement_per_dim.py
from sklearn.metrics import cohen_kappa_score

dimensions = ["correctness", "completeness", "clarity", "tone"]
for dim in dimensions:
    h = [s[dim] for s in human_scores]
    j = [s[dim] for s in judge_scores]
    k = cohen_kappa_score(h, j, weights="quadratic")
    print(f"{dim}: kappa={k:.3f}")
# correctness: kappa=0.78  ← trustworthy
# completeness: kappa=0.65 ← trustworthy
# clarity:     kappa=0.42  ← fair, prompt needs work
# tone:        kappa=0.31  ← weak, rewrite anchors
```

When kappa varies by dimension, **rewrite the anchors of the weakest one** and iterate until every dimension exceeds 0.6.

---

## Common Mistakes

### Mistake 1: Too many dimensions

Correctness, Completeness, Clarity, Tone, Empathy, Conciseness, Helpfulness, Friendliness... eight dimensions and the judge cannot stay consistent. **Cap at 3-5.**

### Mistake 2: Naming dimensions without anchors

Writing "Clarity (1-5)" with no anchors leaves both the LLM judge and humans guessing. **Per-dimension anchors at 1, 3, and 5 are mandatory.**

### Mistake 3: Plain averaging

Reporting a hallucinated answer as 3.0 lets garbage through. Use **weighted average with thresholds** or **report per dimension**.

### Mistake 4: Equal weights on all dimensions

Domains have different priorities. A medical bot may weight Correctness at 70%; a marketing bot may give Tone 30%. **Tune weights to your use case.**

### Mistake 5: Skipping the independence check

If Helpfulness and Completeness correlate at 0.95 they are one dimension. **Merge anything above 0.9 correlation.**

---

## Key Takeaways

- A single score hides weakness. **3-5 dimensions** show what is actually broken.
- Rubric design has four steps: derive from user value → define dimensions → write anchors → check independence.
- Put dimensions and anchors into the judge prompt and **force JSON output** to avoid parse failures.
- Plain averaging is dangerous. Use **weighted average + threshold** or **report per dimension**.
- Measure Cohen's kappa **per dimension** and rewrite anchors for any dimension below 0.6.

The next post covers RAG pipeline evaluation — retrieval, faithfulness, answer relevance.

---

## AI Evaluation 101 Series

- [Ep1 Why Evaluate LLM Apps](./01-why-evaluate-llm-apps.md)
- [Ep2 Evaluation Dataset Design](./02-evaluation-dataset-design.md)
- [Ep3 Deterministic Metrics — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [Ep4 LLM-as-Judge — Evaluating Models with Models](./04-llm-as-judge.md)
- **Ep5 Rubric-Based Multi-Dimensional Scoring (current)**
- Ep6 RAG Evaluation (upcoming)
- Ep7 Agent Evaluation (upcoming)
- Ep8 Regression Testing (upcoming)
- Ep9 A/B Testing LLMs (upcoming)
- Ep10 Production Evaluation (upcoming)
## References

- [Liu et al. (2023). G-Eval — NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)
- [Anthropic — Multi-dimensional evaluation patterns](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [LangSmith — Custom Evaluators with Rubrics](https://docs.smith.langchain.com/evaluation/how_to_guides/custom_evaluator)
- [Hugging Face — Evaluating LLMs with multi-dimensional criteria](https://huggingface.co/learn/cookbook/en/llm_judge)

Tags: AI Evaluation, Rubric, Multi-Dimensional, JSON Output

---

© 2026 YeongseonBooks. All rights reserved.
