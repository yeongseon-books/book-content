---
title: Evaluating and improving an AI app — measuring quality over time
series: ai-web-dev-101
episode: 7
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- Web Development
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Learn how to evaluate accuracy, relevance, and safety, then turn those results into a repeatable improvement loop.
---

# Evaluating and improving an AI app — measuring quality over time

An AI app is not finished when it is deployed. That is when users begin surfacing the real issues: strange answers, regressions after prompt changes, unnecessary verbosity, and brittle retrieval behavior.

This is the final post in the AI Web Development 101 series.

Here, we will turn “it feels better” into a repeatable evaluation and improvement loop.

## Questions this chapter answers

- Why is evaluation part of operations rather than an optional extra?
- Which quality axes should you measure first?
- How do you start with the smallest automatic evaluation?
- When is LLM-as-Judge useful, and what are its limits?
- How do you turn evaluation results into better prompts and retrieval behavior?

> AI evaluation converts “looks good to me” into numbers and concrete failure cases. Because models are probabilistic, you need separate input sets and scoring rules if you want to know whether a change really improved the system.

## Why evaluation is necessary

Traditional software usually aims for deterministic outputs from fixed inputs. AI systems often do not. The same prompt can vary slightly, and a change that improves one question can silently hurt another.

That is why evaluation matters for three reasons:

1. it gives you an objective comparison point
2. it catches regressions after model or prompt changes
3. it helps you compare quality against cost and latency

![Why evaluation matters for regression, accuracy, and cost](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/07/evaluation-three-axes.en.png)

*Why evaluation matters for regression, accuracy, and cost*

## Start by choosing quality axes

For a first evaluation framework, three axes are enough:

- **accuracy**: does the answer stay consistent with facts or evidence?
- **relevance**: does it answer the actual user intent?
- **safety**: does it avoid risky instructions, unsafe speculation, or privacy leaks?

Different products weight these differently. A customer-support assistant may prioritize accuracy and safety. A brainstorming tool may care more about relevance and tone.

![Scoring answer quality across accuracy, relevance, and safety](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/07/test-case-scoring-flow.en.png)

*Scoring answer quality across accuracy, relevance, and safety*

## The smallest useful dataset

Start by collecting question-and-expectation pairs.

```json
[
  {
    "id": "pricing-01",
    "question": "How much does this service cost?",
    "expected_keywords": ["9,900 KRW", "free trial", "subscription"],
    "category": "pricing"
  },
  {
    "id": "support-01",
    "question": "I forgot my password.",
    "expected_keywords": ["email verification", "password reset"],
    "category": "support"
  }
]
```

Without a stable input set, every quality comparison depends too much on memory and intuition.

## Why a keyword scorer is still useful

A simple keyword-based scorer is not sophisticated, but it is often enough to catch whether a response contains the must-have facts.

```python
def evaluate_response(response: str, expected_keywords: list[str]) -> float:
    hits = 0
    for keyword in expected_keywords:
        if keyword in response:
            hits += 1
    return hits / len(expected_keywords)


user_query = "Tell me the price"
ai_response = "The service costs 9,900 KRW per month and includes a free trial for the first month."
expected = ["9,900 KRW", "free trial"]

print(f"quality score: {evaluate_response(ai_response, expected) * 100:.0f}%")
```

## Batch evaluation for regression checks

```python
test_cases = [
    {
        "id": "pricing-01",
        "question": "How much does this service cost?",
        "expected_keywords": ["9,900 KRW", "free trial"],
    },
    {
        "id": "support-01",
        "question": "I forgot my password.",
        "expected_keywords": ["email verification", "password reset"],
    },
]


def run_batch(responder):
    report = []
    for case in test_cases:
        answer = responder(case["question"])
        score = evaluate_response(answer, case["expected_keywords"])
        report.append({
            "id": case["id"],
            "answer": answer,
            "score": score,
        })
    return report
```

This is enough to ask a practical question: after the latest prompt change, did the average score improve or regress?

## LLM-as-Judge

Keyword scoring cannot measure everything. Helpfulness, answer sufficiency, tone, and subtle grounding quality often need a richer judge. That is where LLM-as-Judge becomes useful.

```python
judge_prompt = """
You are an AI response evaluator.

Score the answer on:
1. accuracy
2. relevance
3. safety

Return only this JSON object:
{
  "accuracy": 1-5,
  "relevance": 1-5,
  "safety": 1-5,
  "reason": "one-sentence explanation"
}
"""
```

```python
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def judge_answer(question: str, rubric_context: str, answer: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": judge_prompt},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Reference context: {rubric_context}\n"
                    f"Answer: {answer}"
                ),
            },
        ],
    )
    return json.loads(response.choices[0].message.content)
```

LLM-as-Judge is valuable for larger batches, but it is still a model-based judgment system. For important changes, sample human review should stay in the loop.

![Using a judge model to score answer quality](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/07/llm-as-judge-flow.en.png)

*Using a judge model to score answer quality*

## Turn evaluation into an improvement loop

1. run evaluation on the current prompt, model, or retrieval setup
2. group low-scoring cases by failure pattern
3. change one layer at a time: prompt, retrieval, model choice, or safety rule
4. rerun the same dataset

Evaluation becomes useful only when it leads to controlled iteration.

![Feeding evaluation results back into the next iteration](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/07/improvement-cycle.en.png)

*Feeding evaluation results back into the next iteration*

## A concrete RAG improvement example

Imagine the RAG chatbot from the previous chapter fails on two out of five test questions.

- if the wrong documents were retrieved, investigate chunking and retrieval first
- if the right documents were retrieved but the answer still hallucinates, strengthen grounding rules in the prompt
- if the answer is correct but too verbose, revise output constraints rather than the search layer

This separation matters because “the answer is bad” is not a diagnosis.

![Regression checking after a system change](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/07/regression-check-flow.en.png)

*Regression checking after a system change*

## Cost and latency belong in the same report

A quality improvement that doubles latency or cost may still be the wrong operational choice.

- route simple tasks to a cheaper model when possible
- cache repeated questions
- trim overly long prompts and excess context
- track latency alongside quality scores

The goal is not maximum quality at any price. It is sustainable quality.

## Checklist

- [ ] I keep a stable test set and expected criteria.
- [ ] I chose the most important quality axes for the product.
- [ ] I rerun the same dataset after prompt or model changes.
- [ ] I separate retrieval problems from generation problems.
- [ ] I track cost and latency together with quality scores.

## Summary

Evaluation is not a luxury feature for AI applications. It is part of keeping the system trustworthy over time.

- Start with a stable dataset and a few clear quality axes.
- Even a simple keyword scorer is useful for regression detection.
- LLM-as-Judge helps with larger-scale qualitative scoring, but it should not replace human review entirely.
- Good improvement loops compare the same inputs before and after each change.

This closes the series. You have now walked through API calls, prompt design, browser chat UI, RAG, tool use, deployment, and evaluation—the full beginner path for AI web applications.

<!-- toc:begin -->
## Series table of contents

- [AI API first steps — sending your first request with the OpenAI API](./01-hello-ai-api.md)
- [Prompt engineering basics — getting the answer you actually want](./02-prompt-engineering.md)
- [Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK](./03-ai-chatbot.md)
- [RAG introduction — answering with your own data](./04-rag-intro.md)
- [First steps with AI agents — making the model use tools](./05-ai-agent.md)
- [Deploying an AI web app — shipping to Vercel and Azure](./06-deploy.md)
- **Evaluating and improving an AI app — measuring quality over time (current)**

<!-- toc:end -->

## References

- [OpenAI Cookbook: evaluation examples](https://cookbook.openai.com/categories/evaluation)
- [OpenAI evals guide](https://platform.openai.com/docs/guides/evals)
- [DeepLearning.AI: Evaluating and debugging generative AI](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/)
- [Arize Phoenix documentation](https://arize.com/docs/phoenix)

Tags: AI, LLM, Web Development, Python, Tutorial
